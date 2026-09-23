"""Tests per Logic/Engagement_Resolver — FASE 4 del motore di sessioni virtuali.

Ogni classe verifica UNA delle decisioni di design che il modulo implementa, e il nome
della classe lo dice: Pd e istante di rilevamento, iniziativa (chi spara per primo),
saturazione per salva (R1), soglie di disingaggio per erosione e shock (P1 + R2, incluso
il test di simmetria fra i lati che R2 chiede esplicitamente), congelamento del payload
(R4), scorte (R3), determinismo e ordine delle estrazioni, non-mutazione e applicazione.

Strategia di setup
------------------
* Asset e forze sono stub con la sola superficie che il risolutore legge (`id`, `health`,
  `ammunition`; `name`, `side`, `assets`, `salvo_interceptors`). Il risolutore lavora su
  uno stato ombra e non chiama altro sugli asset: usare stub rende ogni scenario
  calcolabile a mano. Una classe finale (TestIntegrationWithRealObjects) ripete il giro
  con `Military` e `Mobile` REALI, per verificare che la superficie sia davvero quella.
* Le finestre di contatto sono costruite direttamente come `ContactWindow` con
  `distance_cpa = 0`: con Pd(0) = 1 ogni estrazione rileva, e il rilevamento smette di
  essere una variabile dello scenario quando non e' cio' che si vuole verificare.
* Le ShotSpec con accuracy = destroy_capacity = 1 uccidono con certezza qualunque sia
  l'estrazione (resolve_hit: KILL se draw < 1); con accuracy = 0 mancano con certezza.
  Cosi' gli esiti dipendono solo dal meccanismo sotto test.
* I profili di reazione sono imposti per asset (`reaction_profile_for`), perche'
  l'iniziativa e' esattamente cio' che alcuni test devono controllare.
"""

import random
import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Context.Context import MILITARY_CATEGORY
from Code.Dynamic_War_Manager.Source.Context.Reaction_Profile import ReactionProfile
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import ContactWindow, Leg

_ER_LOGGER = 'Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver.logger'


# ── STUB E COSTRUTTORI DI COMODO ──────────────────────────────────────────────

class _Asset:
    def __init__(self, asset_id, health=100, ammunition=None):
        self.id = asset_id
        self.health = health
        self.ammunition = ammunition


class _Force:
    def __init__(self, name, side, assets, interceptors=None):
        self.name = name
        self.side = side
        self.assets = {asset.id: asset for asset in assets}
        self._interceptors = interceptors or []

    def salvo_interceptors(self):
        return list(self._interceptors)


class _ScriptedRng:
    """RNG che restituisce valori prefissati e conta le chiamate."""

    def __init__(self, values):
        self.values = list(values)
        self.calls = 0

    def random(self):
        value = self.values[self.calls] if self.calls < len(self.values) else 0.5
        self.calls += 1
        return value


def _window(a, b, t_start=0.0, t_end=1000.0, range_a=1000.0, range_b=1000.0,
            distance=0.0, t_mutual_start=None):
    return ContactWindow(asset_a_id=a, asset_b_id=b, t_start=t_start, t_end=t_end,
                         t_cpa=(t_start + t_end) / 2, distance_cpa=distance,
                         range_a=range_a, range_b=range_b,
                         t_mutual_start=t_mutual_start if t_mutual_start is not None else t_start,
                         t_mutual_end=t_end)


def _profile(total, refire=1.0):
    """Profilo con totale e intervallo di tiro imposti (RIV = residuo)."""
    return ReactionProfile(detection=total - refire, evaluation=refire, command=0.0, actuation=0.0,
                           source='test')


def _profiles(mapping, default=(10.0, 1.0)):
    return lambda asset: _profile(*mapping.get(asset.id, default))


def _kill(**kwargs):
    return ER.ShotSpec(accuracy=1.0, destroy_capacity=1.0, **kwargs)


def _miss(**kwargs):
    return ER.ShotSpec(accuracy=0.0, destroy_capacity=1.0, **kwargs)


def _always(spec):
    return lambda shooter, target: spec


# ── Pd ────────────────────────────────────────────────────────────────────────

class TestDetectionProbability(unittest.TestCase):
    """La legge di Pd dichiarata: 1 a distanza nulla, PD_AT_ACQUISITION_RANGE al bordo, R^4."""

    def test_certain_at_zero_distance(self):
        self.assertAlmostEqual(ER.detection_probability(0.0, 1000.0), 1.0)

    def test_declared_value_at_the_range_edge(self):
        self.assertAlmostEqual(ER.detection_probability(1000.0, 1000.0), ER.PD_AT_ACQUISITION_RANGE)

    def test_zero_beyond_range(self):
        self.assertEqual(ER.detection_probability(1000.1, 1000.0), 0.0)

    def test_fourth_power_law(self):
        """A meta' portata: 1 - 0.5 * 0.5^4 = 0.96875."""
        self.assertAlmostEqual(ER.detection_probability(500.0, 1000.0), 1.0 - 0.5 * 0.5 ** 4)

    def test_factor_scales(self):
        self.assertAlmostEqual(ER.detection_probability(0.0, 1000.0, factor=0.3), 0.3)

    def test_monotone_decreasing(self):
        values = [ER.detection_probability(d, 1000.0) for d in range(0, 1001, 50)]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_bad_arguments_raise(self):
        with self.assertRaises(ValueError):
            ER.detection_probability(-1.0, 1000.0)
        with self.assertRaises(ValueError):
            ER.detection_probability(1.0, 0.0)
        with self.assertRaises(ValueError):
            ER.detection_probability(1.0, 1000.0, factor=1.5)


class TestDetectionRadius(unittest.TestCase):
    """L'inversa di Pd: una sola estrazione decide se E dove avviene il rilevamento."""

    def test_is_the_inverse_of_detection_probability(self):
        for draw in (0.55, 0.7, 0.9, 0.99):
            with self.subTest(draw=draw):
                radius = ER.detection_radius(draw, 1000.0)
                self.assertAlmostEqual(ER.detection_probability(radius, 1000.0), draw)

    def test_consistent_with_the_detection_decision(self):
        """Dentro il raggio l'estrazione rileva, fuori no."""
        draw = 0.8
        radius = ER.detection_radius(draw, 1000.0)
        self.assertLess(draw, ER.detection_probability(radius - 1.0, 1000.0))
        self.assertGreaterEqual(draw, ER.detection_probability(radius + 1.0, 1000.0))

    def test_low_draw_detects_at_the_range_edge(self):
        self.assertEqual(ER.detection_radius(0.3, 1000.0), 1000.0)

    def test_draw_above_factor_never_detects(self):
        self.assertIsNone(ER.detection_radius(0.5, 1000.0, factor=0.4))

    def test_bad_draw_raises(self):
        with self.assertRaises(ValueError):
            ER.detection_radius(1.0, 1000.0)


class TestDetectionInResolver(unittest.TestCase):

    def test_draw_above_pd_means_no_detection_and_no_fire(self):
        """d_cpa al bordo della portata: Pd = 0.5; un'estrazione di 0.9 non rileva."""
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        window = _window('b1', 'r1', distance=1000.0, range_a=1000.0, range_b=None)

        result = ER.resolve_engagement(blue, red, [window], _always(_kill()), _ScriptedRng([0.9]))

        self.assertEqual(len(result.detections), 1)
        self.assertFalse(result.detections[0].detected)
        self.assertEqual(result.salvos, ())

    def test_detection_factor_zero_blinds_the_sensor(self):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])

        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1', range_b=None)], _always(_kill()),
                                       random.Random(0), detection_factor=lambda o, t: 0.0)

        self.assertFalse(result.detections[0].detected)

    def test_without_legs_the_longer_range_detects_at_t_start(self):
        """Iniziativa preservata anche senza rotte: chi vede piu' lontano vede prima."""
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        window = _window('b1', 'r1', t_start=100.0, range_a=2000.0, range_b=500.0, t_mutual_start=160.0)

        result = ER.resolve_engagement(blue, red, [window], lambda s, t: None, random.Random(0))
        times = {d.observer_id: d.time for d in result.detections}

        self.assertAlmostEqual(times['b1'], 100.0)
        self.assertAlmostEqual(times['r1'], 160.0)

    def test_with_legs_detection_time_is_exact(self):
        """Osservatore fermo, bersaglio in avvicinamento a 100 m/s da 10 km.

        Estrazione 0.9 -> raggio r = R * ((1 - 0.9)/(1 - 0.5))^(1/4); il bersaglio vi
        entra a t = (10000 - r) / 100.
        """
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        legs = {'b1': [Leg(0.0, 100.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))],
                'r1': [Leg(0.0, 100.0, (10000.0, 0.0, 0.0), (0.0, 0.0, 0.0))]}
        window = ContactWindow('b1', 'r1', t_start=20.0, t_end=100.0, t_cpa=100.0, distance_cpa=0.0,
                               range_a=8000.0, range_b=None)

        result = ER.resolve_engagement(blue, red, [window], lambda s, t: None, _ScriptedRng([0.9]),
                                       legs=legs)

        radius = 8000.0 * ((1 - 0.9) / (1 - ER.PD_AT_ACQUISITION_RANGE)) ** 0.25
        self.assertAlmostEqual(result.detections[0].time, (10000.0 - radius) / 100.0, places=6)


# ── INIZIATIVA ────────────────────────────────────────────────────────────────

class TestInitiative(unittest.TestCase):
    """La latenza di reazione decide chi spara per primo, e quindi chi sopravvive."""

    def _duel(self, blue_latency, red_latency):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        profiles = _profiles({'b1': (blue_latency, 1.0), 'r1': (red_latency, 1.0)})
        return ER.resolve_engagement(blue, red, [_window('b1', 'r1')], _always(_kill()),
                                     random.Random(0), reaction_profile_for=profiles)

    def test_faster_side_fires_first_and_wins(self):
        result = self._duel(blue_latency=2.0, red_latency=26.0)

        self.assertEqual(result.outcome_of('blue').outcome, ER.HELD)
        self.assertEqual(result.outcome_of('red').outcome, ER.DESTROYED)
        self.assertEqual([s.shooter_id for s in result.salvos], ['b1'])
        self.assertAlmostEqual(result.salvos[0].t_launch, 2.0)

    def test_reversing_latencies_reverses_the_outcome(self):
        result = self._duel(blue_latency=26.0, red_latency=2.0)

        self.assertEqual(result.outcome_of('blue').outcome, ER.DESTROYED)
        self.assertEqual(result.outcome_of('red').outcome, ER.HELD)

    def test_simultaneous_launches_both_fire(self):
        """Risoluzione simultanea: a parita' di istante tutti i lanci leggono lo stato prima dei danni."""
        result = self._duel(blue_latency=5.0, red_latency=5.0)

        self.assertEqual(sorted(s.shooter_id for s in result.salvos), ['b1', 'r1'])
        self.assertEqual(result.outcome_of('blue').outcome, ER.DESTROYED)
        self.assertEqual(result.outcome_of('red').outcome, ER.DESTROYED)

    def test_launch_after_window_end_never_happens(self):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1', t_end=5.0, range_b=None)],
                                       _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({'b1': (26.0, 1.0)}))
        self.assertEqual(result.salvos, ())


# ── R1: SATURAZIONE PER SALVA ─────────────────────────────────────────────────

class TestSalvoSaturation(unittest.TestCase):
    """I primi N colpi intercettabili sono fermati; il surplus raggiunge integralmente il danno."""

    def _scenario(self, spec, channels=3, interceptor_ammo=None, shooters=('b1',),
                  latencies=None, salvo_window=0.0):
        blue = _Force('blue', 'Blue', [_Asset(s) for s in shooters])
        interceptor = _Asset('r2', ammunition=interceptor_ammo)
        red = _Force('red', 'Red', [_Asset('r1'), interceptor], interceptors=[(interceptor, channels)])
        # La finestra chiude prima del secondo lancio (re-fire 1 s): una salva per tiratore.
        windows = [_window(s, 'r1', t_end=2.9, range_b=None) for s in shooters]
        profiles = _profiles(latencies or {s: (2.0, 1.0) for s in shooters})
        return ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(0),
                                     reaction_profile_for=profiles, salvo_window=salvo_window)

    def test_first_n_rounds_are_intercepted(self):
        result = self._scenario(_miss(rounds=5, interceptable=True))
        resolution = result.resolutions[0]

        self.assertEqual(resolution.capacity, 3)
        self.assertEqual(resolution.intercepted, 3)
        self.assertEqual(len(result.damage_events), 2)

    def test_intercepted_rounds_never_reach_resolve_hit(self):
        with patch.object(DM, 'build_damage_event', wraps=DM.build_damage_event) as spy:
            self._scenario(_miss(rounds=5, interceptable=True))
        self.assertEqual(spy.call_count, 2)

    def test_saturation_is_not_a_per_round_probability(self):
        """Stesso esito con qualunque seed: e' un contatore, non un'estrazione."""
        for seed in range(5):
            blue = _Force('blue', 'Blue', [_Asset('b1')])
            interceptor = _Asset('r2')
            red = _Force('red', 'Red', [_Asset('r1'), interceptor], interceptors=[(interceptor, 3)])
            result = ER.resolve_engagement(blue, red, [_window('b1', 'r1', t_end=2.9, range_b=None)],
                                           _always(_miss(rounds=5, interceptable=True)),
                                           random.Random(seed),
                                           reaction_profile_for=_profiles({'b1': (2.0, 1.0)}))
            self.assertEqual(result.resolutions[0].intercepted, 3)

    def test_non_interceptable_rounds_ignore_the_defence(self):
        result = self._scenario(_miss(rounds=5, interceptable=False))

        self.assertEqual(result.resolutions[0].intercepted, 0)
        self.assertEqual(len(result.damage_events), 5)

    def test_interceptions_consume_the_interceptor_ammunition(self):
        result = self._scenario(_miss(rounds=5, interceptable=True), interceptor_ammo=10)
        interceptions = [e for e in result.ammunition_events if e.purpose == ER.PURPOSE_INTERCEPTION]

        self.assertEqual([(e.asset_id, e.rounds) for e in interceptions], [('r2', 3)])

    def test_capacity_is_capped_by_interceptor_ammunition(self):
        result = self._scenario(_miss(rounds=5, interceptable=True), interceptor_ammo=1)

        self.assertEqual(result.resolutions[0].capacity, 1)
        self.assertEqual(len(result.damage_events), 4)

    def test_simultaneous_salvos_share_the_capacity(self):
        """Due salve da 2 colpi nello stesso istante contro capacita' 3: ne passa 1."""
        result = self._scenario(_miss(rounds=2, interceptable=True), shooters=('b1', 'b2'))

        self.assertEqual(len(result.resolutions), 1)
        self.assertEqual(result.resolutions[0].intercepted, 3)
        self.assertEqual(len(result.damage_events), 1)

    def test_capacity_refreshes_between_separate_salvo_events(self):
        """Salve a 0,5 s di distanza con salvo_window = 0: due eventi, tutto intercettato."""
        result = self._scenario(_miss(rounds=2, interceptable=True), shooters=('b1', 'b2'),
                                latencies={'b1': (2.0, 1.0), 'b2': (2.5, 1.0)})

        self.assertEqual(len(result.resolutions), 2)
        self.assertEqual(len(result.damage_events), 0)

    def test_salvo_window_groups_near_simultaneous_impacts(self):
        result = self._scenario(_miss(rounds=2, interceptable=True), shooters=('b1', 'b2'),
                                latencies={'b1': (2.0, 1.0), 'b2': (2.5, 1.0)}, salvo_window=1.0)

        self.assertEqual(len(result.resolutions), 1)
        self.assertEqual(result.resolutions[0].intercepted, 3)
        self.assertEqual(len(result.damage_events), 1)

    def test_force_without_interceptors_has_no_capacity(self):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1', t_end=2.9, range_b=None)],
                                       _always(_miss(rounds=3, interceptable=True)), random.Random(0),
                                       reaction_profile_for=_profiles({'b1': (2.0, 1.0)}))
        self.assertEqual(result.resolutions[0].capacity, 0)
        self.assertEqual(len(result.damage_events), 3)


# ── P1 + R2: DISINGAGGIO ──────────────────────────────────────────────────────

def _one_shooter_vs_ten(shooter_side='Blue', target_side='Red', shooters=1):
    """`shooters` tiratori certi contro 10 bersagli che non vedono nessuno.

    Ogni tiratore uccide un bersaglio per salva, una salva al secondo: con 1 tiratore la
    perdita per salva e' 0.1 (sotto lo shock 0.2) e l'erosione raggiunge 0.3 alla terza.
    I bersagli sono ripartiti fra i tiratori gia' nelle finestre (t_i al tiratore
    i % shooters), cosi' le perdite per salva crescono col numero di tiratori a
    prescindere dalla ripartizione del fuoco del risolutore (round-robin, verificata a
    parte in TestFireDistribution): qui si verificano le soglie, non la ripartizione.
    """
    targets = [_Asset(f't{i:02d}') for i in range(10)]
    shooter_assets = [_Asset(f's{i}') for i in range(shooters)]
    attackers = _Force('attackers', shooter_side, shooter_assets)
    defenders = _Force('defenders', target_side, targets)
    windows = [_window(s.id, t.id, range_b=None)
               for index, s in enumerate(shooter_assets)
               for number, t in enumerate(targets) if number % shooters == index]
    return attackers, defenders, windows


class TestDisengagementErosion(unittest.TestCase):

    def test_force_disengages_when_cumulative_losses_reach_the_threshold(self):
        """Uccisioni a t = 2, 4, 6: il lancio a t = 3 era gia' deciso contro il bersaglio
        ucciso a t = 2 (payload congelato allo scheduling), viene annullato e la nuova
        decisione costa un altro ciclo di tiro (shoot-look-shoot). Alla terza perdita
        l'erosione vale 0.3 e la forza si disingaggia."""
        attackers, defenders, windows = _one_shooter_vs_ten()
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)))
        outcome = result.outcome_of('defenders')

        self.assertEqual(outcome.outcome, ER.DISENGAGED)
        self.assertEqual(outcome.triggers, (ER.TRIGGER_EROSION,))
        self.assertEqual(outcome.lost, 3)
        self.assertAlmostEqual(outcome.erosion, 0.3)
        self.assertAlmostEqual(outcome.time, 6.0)

    def test_disengagement_is_not_destruction(self):
        """La forza superstite non sparisce: 7 asset su 10 restano operativi."""
        attackers, defenders, windows = _one_shooter_vs_ten()
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)))

        self.assertNotEqual(result.outcome_of('defenders').outcome, ER.DESTROYED)
        self.assertEqual(result.outcome_of('defenders').committed - result.outcome_of('defenders').lost, 7)

    def test_no_launch_after_contact_is_broken(self):
        attackers, defenders, windows = _one_shooter_vs_ten()
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)))

        self.assertEqual(len(result.salvos), 3)
        self.assertTrue(all(s.t_launch <= result.outcome_of('defenders').time for s in result.salvos))

    def test_custom_doctrine_is_respected(self):
        attackers, defenders, windows = _one_shooter_vs_ten()
        doctrine = {'Blue': {'erosion': 0.3, 'shock': 0.2}, 'Red': {'erosion': 0.5, 'shock': 0.2}}
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)),
                                       thresholds=doctrine)
        self.assertEqual(result.outcome_of('defenders').lost, 5)

    def test_invalid_doctrine_raises(self):
        attackers, defenders, windows = _one_shooter_vs_ten()
        with self.assertRaises(ValueError):
            ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                  thresholds={'Red': {'erosion': 0.1, 'shock': 0.5}})

    def test_side_without_doctrine_fights_to_annihilation(self):
        attackers, defenders, windows = _one_shooter_vs_ten(target_side='Unknown')
        with patch(_ER_LOGGER) as mock_logger:
            result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()),
                                           random.Random(0),
                                           reaction_profile_for=_profiles({}, default=(2.0, 1.0)))
        self.assertEqual(result.outcome_of('defenders').outcome, ER.DESTROYED)
        self.assertEqual(result.outcome_of('defenders').lost, 10)
        mock_logger.warning.assert_called()


class TestDisengagementShock(unittest.TestCase):

    def test_single_salvo_loss_triggers_shock_before_erosion(self):
        """Due tiratori simultanei: 2 perdite su 10 in un impulso = 0.2 >= shock, erosione 0.2 < 0.3."""
        attackers, defenders, windows = _one_shooter_vs_ten(shooters=2)
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)))
        outcome = result.outcome_of('defenders')

        self.assertEqual(outcome.outcome, ER.DISENGAGED)
        self.assertEqual(outcome.triggers, (ER.TRIGGER_SHOCK,))
        self.assertAlmostEqual(outcome.max_shock, 0.2)
        self.assertEqual(outcome.lost, 2)

    def test_both_triggers_can_fire_together(self):
        attackers, defenders, windows = _one_shooter_vs_ten(shooters=3)
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)))
        self.assertEqual(result.outcome_of('defenders').triggers, (ER.TRIGGER_EROSION, ER.TRIGGER_SHOCK))

    def test_shock_is_checked_per_salvo_not_per_round(self):
        """Una salva di 3 colpi su 3 bersagli diversi? No: una salva ha UN bersaglio.

        Qui un solo tiratore spara 3 colpi certi sullo stesso bersaglio: una perdita per
        salva (0.1), shock mai raggiunto; il disingaggio arriva per erosione.
        """
        attackers, defenders, windows = _one_shooter_vs_ten()
        result = ER.resolve_engagement(attackers, defenders, windows, _always(_kill(rounds=3)),
                                       random.Random(0),
                                       reaction_profile_for=_profiles({}, default=(2.0, 1.0)))
        self.assertEqual(result.outcome_of('defenders').triggers, (ER.TRIGGER_EROSION,))
        self.assertAlmostEqual(result.outcome_of('defenders').max_shock, 0.1)


class TestDisengagementSymmetry(unittest.TestCase):
    """R2: la soglia si applica allo STESSO modo a entrambi i lati, in ogni scenario.

    Lo scenario viene ripetuto scambiando il colore dei lati e l'ordine degli argomenti:
    l'esito della forza colpita deve essere identico.
    """

    def _run(self, shooter_side, target_side, swap, shooters):
        attackers, defenders, windows = _one_shooter_vs_ten(shooter_side, target_side, shooters)
        forces = (defenders, attackers) if swap else (attackers, defenders)
        return ER.resolve_engagement(*forces, windows, _always(_kill()), random.Random(7),
                                     reaction_profile_for=_profiles({}, default=(2.0, 1.0)))

    def test_erosion_is_side_independent(self):
        reference = self._run('Blue', 'Red', False, 1).outcome_of('defenders')

        for shooter_side, target_side, swap in (('Red', 'Blue', False), ('Blue', 'Red', True),
                                                ('Red', 'Blue', True)):
            with self.subTest(shooter=shooter_side, swap=swap):
                outcome = self._run(shooter_side, target_side, swap, 1).outcome_of('defenders')
                self.assertEqual((outcome.outcome, outcome.triggers, outcome.lost, outcome.time),
                                 (reference.outcome, reference.triggers, reference.lost, reference.time))

    def test_shock_is_side_independent(self):
        reference = self._run('Blue', 'Red', False, 2).outcome_of('defenders')
        mirrored = self._run('Red', 'Blue', True, 2).outcome_of('defenders')

        self.assertEqual(reference.triggers, (ER.TRIGGER_SHOCK,))
        self.assertEqual((mirrored.outcome, mirrored.triggers, mirrored.lost),
                         (reference.outcome, reference.triggers, reference.lost))

    def test_default_doctrine_is_symmetric(self):
        self.assertEqual(Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Blue'],
                         Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Red'])


# ── R4: CONGELAMENTO DEL PAYLOAD ──────────────────────────────────────────────

class TestPayloadFreezing(unittest.TestCase):

    def test_salvo_in_flight_lands_after_its_launcher_is_destroyed(self):
        """b1 lancia a t=1 con 10 s di volo; r1 lo distrugge a t=2; la salva di b1 arriva a t=11."""
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        specs = {'b1': _kill(time_of_flight=10.0, cycle_time=100.0), 'r1': _kill()}
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1')],
                                       lambda shooter, target: specs[shooter.id], random.Random(0),
                                       reaction_profile_for=_profiles({'b1': (1.0, 1.0), 'r1': (2.0, 1.0)}))

        self.assertEqual(result.outcome_of('blue').outcome, ER.DESTROYED)
        self.assertAlmostEqual(result.outcome_of('blue').time, 2.0)
        self.assertEqual(result.outcome_of('red').outcome, ER.DESTROYED)
        self.assertAlmostEqual(result.outcome_of('red').time, 11.0)

        late_hit = [e for e in result.damage_events if e.source_id == 'b1']
        self.assertEqual(len(late_hit), 1)
        self.assertAlmostEqual(late_hit[0].time, 11.0)

    def test_payload_of_a_launched_salvo_is_never_rewritten(self):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        specs = {'b1': _miss(rounds=4, time_of_flight=10.0, cycle_time=100.0), 'r1': _kill()}
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1')],
                                       lambda shooter, target: specs[shooter.id], random.Random(0),
                                       reaction_profile_for=_profiles({'b1': (1.0, 1.0), 'r1': (2.0, 1.0)}))
        salvo = [s for s in result.salvos if s.shooter_id == 'b1'][0]

        self.assertEqual((salvo.rounds, salvo.target_id), (4, 'r1'))
        self.assertEqual(len([e for e in result.damage_events if e.source_id == 'b1']), 4)

    def test_salvo_is_immutable(self):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1', range_b=None)], _always(_kill()),
                                       random.Random(0))
        with self.assertRaises(Exception):
            result.salvos[0].rounds = 99

    def test_scheduled_launch_is_cancelled_if_the_launcher_dies_first(self):
        """Prima del lancio l'evento puo' essere annullato (mai riscritto)."""
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1')], _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({'b1': (5.0, 1.0), 'r1': (1.0, 1.0)}))

        self.assertEqual([s.shooter_id for s in result.salvos], ['r1'])


# ── R3: MUNIZIONI ─────────────────────────────────────────────────────────────

class TestAmmunition(unittest.TestCase):

    def _run(self, ammunition, spec, targets=5):
        blue = _Force('blue', 'Blue', [_Asset('b1', ammunition=ammunition)])
        red = _Force('red', 'Red', [_Asset(f'r{i}') for i in range(targets)])
        windows = [_window('b1', f'r{i}', range_b=None) for i in range(targets)]
        return ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(0),
                                     reaction_profile_for=_profiles({'b1': (2.0, 1.0)}),
                                     thresholds={'Blue': {'erosion': 1.0, 'shock': 1.0},
                                                 'Red': {'erosion': 1.0, 'shock': 1.0}})

    def test_shooter_stops_when_ammunition_runs_out(self):
        result = self._run(ammunition=2, spec=_kill())

        self.assertEqual(len(result.salvos), 2)
        self.assertEqual(result.ammunition_consumed(), {'b1': 2})
        self.assertEqual(result.outcome_of('red').lost, 2)

    def test_consumption_is_deterministic_and_explicit(self):
        """N colpi sparati = N in meno, per ogni seed; anche con colpi mancati."""
        for seed in range(3):
            blue = _Force('blue', 'Blue', [_Asset('b1', ammunition=3)])
            red = _Force('red', 'Red', [_Asset('r0')])
            result = ER.resolve_engagement(blue, red, [_window('b1', 'r0', range_b=None)],
                                           _always(_miss()), random.Random(seed),
                                           reaction_profile_for=_profiles({'b1': (2.0, 1.0)}))
            self.assertEqual(result.ammunition_consumed(), {'b1': 3})

    def test_salvo_size_is_capped_by_the_stock(self):
        result = self._run(ammunition=2, spec=_miss(rounds=4), targets=1)

        self.assertEqual([s.rounds for s in result.salvos], [2])

    def test_empty_stock_means_no_fire_but_still_a_target(self):
        blue = _Force('blue', 'Blue', [_Asset('b1', ammunition=0)])
        red = _Force('red', 'Red', [_Asset('r1')])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1')], _always(_kill()), random.Random(0),
                                       reaction_profile_for=_profiles({'b1': (1.0, 1.0), 'r1': (2.0, 1.0)}))

        self.assertEqual([s.shooter_id for s in result.salvos], ['r1'])
        self.assertEqual(result.outcome_of('blue').outcome, ER.DESTROYED)

    def test_unmodelled_stock_does_not_limit_fire(self):
        result = self._run(ammunition=None, spec=_kill())
        self.assertEqual(len(result.salvos), 5)


# ── RIPARTIZIONE DEL FUOCO (ROUND-ROBIN) ──────────────────────────────────────

class TestFireDistribution(unittest.TestCase):
    """Round-robin semplice: i tiratori di una forza si ripartiscono i bersagli ingaggiabili
    nello stesso istante invece di convergere tutti sull'id minore."""

    _LOOSE = {'Blue': {'erosion': 1.0, 'shock': 1.0}, 'Red': {'erosion': 1.0, 'shock': 1.0}}

    def _run(self, shooters, targets, spec, latencies=None, windows=None, seed=0):
        blue = _Force('blue', 'Blue', [_Asset(s) for s in shooters])
        red = _Force('red', 'Red', [_Asset(t) for t in targets])
        windows = windows or [_window(s, t, range_b=None) for s in shooters for t in targets]
        profiles = _profiles(latencies or {}, default=(2.0, 1.0))
        return ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(seed),
                                     reaction_profile_for=profiles, thresholds=self._LOOSE)

    def test_simultaneous_shooters_spread_over_targets(self):
        """3 tiratori pronti a t=2 contro 3 bersagli: un bersaglio a testa, non 3 su r0."""
        result = self._run(['b0', 'b1', 'b2'], ['r0', 'r1', 'r2'], _miss(cycle_time=100.0))
        first = {s.shooter_id: s.target_id for s in result.salvos if s.t_launch == 2.0}

        self.assertEqual(first, {'b0': 'r0', 'b1': 'r1', 'b2': 'r2'})

    def test_more_shooters_than_targets_wrap_around(self):
        shooters, targets = ['b0', 'b1', 'b2', 'b3'], ['r0', 'r1']
        windows = [_window(s, t, t_end=2.9, range_b=None) for s in shooters for t in targets]
        result = self._run(shooters, targets, _miss(), windows=windows)
        counts = {}
        for salvo in result.salvos:
            counts[salvo.target_id] = counts.get(salvo.target_id, 0) + 1

        self.assertEqual(counts, {'r0': 2, 'r1': 2})

    def test_simultaneous_kills_hit_different_targets(self):
        """Con colpi certi, 2 tiratori simultanei uccidono 2 bersagli diversi al primo impulso."""
        result = self._run(['b0', 'b1'], ['r0', 'r1', 'r2'], _kill(cycle_time=100.0))

        self.assertEqual(result.resolutions[0].losses, ('r0', 'r1'))

    def _b0_fires_once(self, time_of_flight):
        """b0 spara una sola salva su r0 a t=1 (la sua finestra chiude a 1,5 s); b1 spara a
        t=2 (su r1, perche' r0 ha il lancio schedulato di b0) e decide la seconda salva a
        t=3, quando b0 non ha piu' lanci in coda."""
        windows = [_window('b0', t, t_end=1.5, range_b=None) for t in ('r0', 'r1')]
        windows += [_window('b1', t, t_end=3.5, range_b=None) for t in ('r0', 'r1')]
        result = self._run(['b0', 'b1'], ['r0', 'r1'], _miss(time_of_flight=time_of_flight),
                           latencies={'b0': (1.0, 1.0), 'b1': (2.0, 1.0)}, windows=windows)
        return [s.target_id for s in sorted(result.salvos, key=lambda s: s.t_launch)
                if s.shooter_id == 'b1']

    def test_in_flight_salvo_counts_as_coverage(self):
        """A t=3 la salva di b0 su r0 e' ancora in volo (impatto a t=11): b1 resta su r1."""
        self.assertEqual(self._b0_fires_once(time_of_flight=10.0), ['r1', 'r1'])

    def test_resolved_salvo_no_longer_counts(self):
        """Volo istantaneo: la salva di b0 e' risolta a t=1; a t=3 r0 non e' piu' coperto
        e b1 torna al criterio precedente (id minore)."""
        self.assertEqual(self._b0_fires_once(time_of_flight=0.0), ['r1', 'r0'])

    def test_a_ready_shooter_never_waits_for_a_less_covered_target(self):
        """b1 puo' sparare su r0 a t=2; r1 (scoperto) gli e' ingaggiabile solo da t=50.
        La ripartizione non ritarda il tiro: l'iniziativa resta quella della latenza."""
        windows = [_window('b0', 'r0', range_b=None), _window('b1', 'r0', range_b=None),
                   _window('b1', 'r1', t_start=48.0, range_b=None)]
        result = self._run(['b0', 'b1'], ['r0', 'r1'], _miss(cycle_time=100.0), windows=windows)
        first_b1 = min((s for s in result.salvos if s.shooter_id == 'b1'), key=lambda s: s.t_launch)

        self.assertAlmostEqual(first_b1.t_launch, 2.0)
        self.assertEqual(first_b1.target_id, 'r0')

    def test_single_shooter_behaviour_is_unchanged(self):
        """Senza altri tiratori la copertura vale 0 ovunque: resta sull'id minore."""
        result = self._run(['b0'], ['r0', 'r1', 'r2'], _miss(cycle_time=50.0))

        self.assertTrue(all(s.target_id == 'r0' for s in result.salvos))

    def test_distribution_is_deterministic(self):
        spec = ER.ShotSpec(accuracy=0.6, destroy_capacity=0.5)
        shooters, targets = ['b0', 'b1', 'b2'], ['r0', 'r1', 'r2', 'r3']
        self.assertEqual(self._run(shooters, targets, spec, seed=5), self._run(shooters, targets, spec, seed=5))


# ── DEGRADAZIONE METEO DELLA Pd ───────────────────────────────────────────────

class TestWeatherDetectionFactor(unittest.TestCase):
    """Collegamento Meteo_Analysis -> detection_factor (stime dichiarate nel modulo)."""

    GOOD = {'day': True, 'night': False, 'adverse_weather': False}
    NIGHT = {'day': False, 'night': True, 'adverse_weather': False}
    ADVERSE = {'day': True, 'night': False, 'adverse_weather': True}
    WORST = {'day': False, 'night': True, 'adverse_weather': True}

    def test_factor_values(self):
        self.assertEqual(ER.weather_detection_factor(self.GOOD), 1.0)
        self.assertAlmostEqual(ER.weather_detection_factor(self.NIGHT), ER.NIGHT_DETECTION_FACTOR)
        self.assertAlmostEqual(ER.weather_detection_factor(self.ADVERSE), ER.ADVERSE_WEATHER_DETECTION_FACTOR)
        self.assertAlmostEqual(ER.weather_detection_factor(self.WORST),
                               ER.NIGHT_DETECTION_FACTOR * ER.ADVERSE_WEATHER_DETECTION_FACTOR)

    def test_factors_are_degradations(self):
        for value in (ER.NIGHT_DETECTION_FACTOR, ER.ADVERSE_WEATHER_DETECTION_FACTOR):
            self.assertTrue(0.0 < value < 1.0)

    def test_missing_data_means_no_degradation(self):
        with patch(_ER_LOGGER):
            self.assertEqual(ER.weather_detection_factor(None), 1.0)
        self.assertEqual(ER.weather_detection_factor({}), 1.0)
        self.assertAlmostEqual(ER.weather_detection_factor({'day': False}), ER.NIGHT_DETECTION_FACTOR)

    def test_bad_conditions_raise(self):
        with self.assertRaises(TypeError):
            ER.weather_detection_factor('rain')

    def test_callable_ignores_the_pair(self):
        fn = ER.weather_detection_factor_fn(self.ADVERSE)
        self.assertEqual(fn(_Asset('a'), _Asset('b')), ER.ADVERSE_WEATHER_DETECTION_FACTOR)

    def test_meteo_analysis_link(self):
        """La fabbrica legge davvero Meteo_Analysis.get_meteo_conditions."""
        from datetime import date, time
        from Code.Dynamic_War_Manager.Source.Logic import Meteo_Analysis

        conditions = Meteo_Analysis.get_meteo_conditions('Caucasus', date(2026, 1, 1), time(23, 0))
        fn = ER.meteo_detection_factor('Caucasus', date(2026, 1, 1), time(23, 0))

        self.assertAlmostEqual(fn(None, None), ER.weather_detection_factor(conditions))
        self.assertTrue(conditions['night'])

    def _detection_rate(self, conditions, trials=400):
        """Frazione di coppie rilevate in un ingaggio reale, a d_cpa = 80% della portata."""
        blue = _Force('blue', 'Blue', [_Asset(f'b{i}') for i in range(trials)])
        red = _Force('red', 'Red', [_Asset(f'r{i}') for i in range(trials)])
        windows = [_window(f'b{i}', f'r{i}', distance=800.0, range_b=None) for i in range(trials)]
        result = ER.resolve_engagement(blue, red, windows, lambda s, t: None, random.Random(123),
                                       detection_factor=ER.weather_detection_factor_fn(conditions))
        return result, sum(d.detected for d in result.detections) / len(result.detections)

    def test_adverse_weather_lowers_pd_in_a_real_engagement(self):
        good, good_rate = self._detection_rate(self.GOOD)
        bad, bad_rate = self._detection_rate(self.ADVERSE)
        base_pd = ER.detection_probability(800.0, 1000.0)

        for detection in good.detections:
            self.assertAlmostEqual(detection.probability, base_pd)
        for detection in bad.detections:
            self.assertAlmostEqual(detection.probability, base_pd * ER.ADVERSE_WEATHER_DETECTION_FACTOR)

        # Stesso seed, stesse estrazioni: ogni rilevamento col maltempo lo era anche col bel tempo.
        good_hits = {d.observer_id for d in good.detections if d.detected}
        bad_hits = {d.observer_id for d in bad.detections if d.detected}
        self.assertLess(bad_rate, good_rate)
        self.assertTrue(bad_hits < good_hits)

    def test_night_and_adverse_compound(self):
        _, adverse_rate = self._detection_rate(self.ADVERSE)
        _, worst_rate = self._detection_rate(self.WORST)
        self.assertLess(worst_rate, adverse_rate)

    def test_worse_weather_means_later_first_shot(self):
        """Con le rotte, un Pd ridotta restringe il raggio di rilevamento: il primo colpo arriva dopo."""
        legs = {'b1': [Leg(0.0, 100.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))],
                'r1': [Leg(0.0, 100.0, (10000.0, 0.0, 0.0), (0.0, 0.0, 0.0))]}
        window = ContactWindow('b1', 'r1', t_start=20.0, t_end=100.0, t_cpa=100.0, distance_cpa=0.0,
                               range_a=8000.0, range_b=None)

        def first_launch(conditions):
            blue = _Force('blue', 'Blue', [_Asset('b1')])
            red = _Force('red', 'Red', [_Asset('r1')])
            result = ER.resolve_engagement(blue, red, [window], _always(_kill()), _ScriptedRng([0.6]),
                                           legs=legs, reaction_profile_for=_profiles({'b1': (2.0, 1.0)}),
                                           detection_factor=ER.weather_detection_factor_fn(conditions))
            return result.salvos[0].t_launch

        self.assertGreater(first_launch(self.ADVERSE), first_launch(self.GOOD))


# ── DETERMINISMO E ORDINE DELLE ESTRAZIONI ────────────────────────────────────

class TestDeterminism(unittest.TestCase):

    def _scenario(self, seed):
        blue = _Force('blue', 'Blue', [_Asset(f'b{i}') for i in range(4)])
        red = _Force('red', 'Red', [_Asset(f'r{i}') for i in range(4)])
        windows = [_window(f'b{i}', f'r{j}', distance=800.0) for i in range(4) for j in range(4)]
        spec = ER.ShotSpec(accuracy=0.6, destroy_capacity=0.4)
        return ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(seed),
                                     reaction_profile_for=_profiles({'b0': (3.0, 2.0), 'r1': (4.0, 1.5)},
                                                                    default=(6.0, 2.0)))

    def test_same_seed_same_result(self):
        self.assertEqual(self._scenario(42), self._scenario(42))

    def test_window_order_does_not_matter(self):
        """Le finestre sono ordinate canonicamente: l'ordine d'ingresso non cambia l'esito."""
        blue = _Force('blue', 'Blue', [_Asset('b0'), _Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r0'), _Asset('r1')])
        windows = [_window('b0', 'r0', distance=700.0), _window('b1', 'r1', distance=700.0),
                   _window('b0', 'r1', t_start=5.0, distance=700.0)]
        spec = ER.ShotSpec(accuracy=0.5, destroy_capacity=0.5)
        first = ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(3))
        second = ER.resolve_engagement(blue, red, list(reversed(windows)), _always(spec), random.Random(3))
        self.assertEqual(first, second)

    def test_detection_draws_come_first_then_one_draw_per_round(self):
        """2 direzioni rilevate + 1 colpo non intercettato su bersaglio vivo = 3 estrazioni."""
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        rng = _ScriptedRng([0.1, 0.2, 0.0])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1')], _always(_kill()), rng,
                                       reaction_profile_for=_profiles({'b1': (1.0, 1.0), 'r1': (9.0, 1.0)}))

        self.assertEqual(rng.calls, 3)
        self.assertEqual([d.draw for d in result.detections], [0.1, 0.2])

    def test_rounds_on_a_wreck_are_wasted_without_a_draw(self):
        blue = _Force('blue', 'Blue', [_Asset('b1')])
        red = _Force('red', 'Red', [_Asset('r1')])
        rng = _ScriptedRng([0.1, 0.0, 0.0, 0.0])
        result = ER.resolve_engagement(blue, red, [_window('b1', 'r1', range_b=None)],
                                       _always(_kill(rounds=3)), rng)

        self.assertEqual(rng.calls, 2)
        self.assertEqual(result.resolutions[0].wasted, 2)


# ── INGRESSI E DATI MANCANTI ──────────────────────────────────────────────────

class TestInputs(unittest.TestCase):

    def setUp(self):
        self.blue = _Force('blue', 'Blue', [_Asset('b1')])
        self.red = _Force('red', 'Red', [_Asset('r1')])

    def test_rng_without_random_raises(self):
        with self.assertRaises(TypeError):
            ER.resolve_engagement(self.blue, self.red, [], _always(_kill()), object())

    def test_fire_control_must_be_callable(self):
        with self.assertRaises(TypeError):
            ER.resolve_engagement(self.blue, self.red, [], None, random.Random(0))

    def test_fire_control_must_return_a_shotspec(self):
        with self.assertRaises(TypeError):
            ER.resolve_engagement(self.blue, self.red, [_window('b1', 'r1')], lambda s, t: 'boom',
                                  random.Random(0))

    def test_negative_salvo_window_raises(self):
        with self.assertRaises(ValueError):
            ER.resolve_engagement(self.blue, self.red, [], _always(_kill()), random.Random(0), salvo_window=-1)

    def test_bad_rng_value_raises(self):
        with self.assertRaises(ValueError):
            ER.resolve_engagement(self.blue, self.red, [_window('b1', 'r1')], _always(_kill()),
                                  _ScriptedRng([1.5]))

    def test_force_without_usable_assets_returns_none(self):
        empty = _Force('red', 'Red', [_Asset('r1', health=None)])
        with patch(_ER_LOGGER) as mock_logger:
            self.assertIsNone(ER.resolve_engagement(self.blue, empty, [], _always(_kill()), random.Random(0)))
        mock_logger.warning.assert_called()

    def test_non_operative_assets_are_not_committed(self):
        red = _Force('red', 'Red', [_Asset('r1'), _Asset('r2', health=40)])
        result = ER.resolve_engagement(self.blue, red, [], _always(_kill()), random.Random(0))
        self.assertEqual(result.outcome_of('red').committed, 1)

    def test_same_force_twice_raises(self):
        with self.assertRaises(ValueError):
            ER.resolve_engagement(self.blue, self.blue, [], _always(_kill()), random.Random(0))

    def test_no_contacts_means_nothing_happens(self):
        result = ER.resolve_engagement(self.blue, self.red, [], _always(_kill()), random.Random(0))

        self.assertIsNone(result.t_start)
        self.assertEqual([o.outcome for o in result.forces], [ER.HELD, ER.HELD])

    def test_windows_with_unknown_or_friendly_assets_are_ignored(self):
        blue = _Force('blue', 'Blue', [_Asset('b1'), _Asset('b2')])
        windows = [_window('b1', 'ghost'), _window('b1', 'b2')]
        result = ER.resolve_engagement(blue, self.red, windows, _always(_kill()), random.Random(0))
        self.assertEqual(result.detections, ())

    def test_fire_control_none_means_no_engagement(self):
        """ROE / arma inadatta: il bersaglio rilevato non viene ingaggiato."""
        result = ER.resolve_engagement(self.blue, self.red, [_window('b1', 'r1')], lambda s, t: None,
                                       random.Random(0))
        self.assertEqual(result.salvos, ())
        self.assertEqual(len(result.detections), 2)

    def test_committed_subset(self):
        red = _Force('red', 'Red', [_Asset('r1'), _Asset('r2')])
        result = ER.resolve_engagement(self.blue, red, [_window('b1', 'r2')], _always(_kill()),
                                       random.Random(0), committed={'red': ['r1']})
        self.assertEqual(result.outcome_of('red').committed, 1)
        self.assertEqual(result.detections, ())


# ── INGAGGI A N FORZE ─────────────────────────────────────────────────────────

_THREE_SIDES = {'Blue': {'erosion': 0.3, 'shock': 0.2}, 'Red': {'erosion': 0.3, 'shock': 0.2},
                'Green': {'erosion': 0.3, 'shock': 0.2}}


class TestMultiForceEngagement(unittest.TestCase):
    """Tre forze in UNA run: la forza X in contatto con A e con B nello stesso intervallo.

    E' il caso che ha motivato `extra_forces`: con due chiamate separate lo stato di X
    sarebbe consumato da un fronte alla volta; in una run e' una sola timeline.
    """

    def test_extra_forces_default_is_the_two_force_engagement(self):
        blue = _Force('blue', 'Blue', [_Asset(f'b{i}') for i in range(3)])
        red = _Force('red', 'Red', [_Asset(f'r{i}') for i in range(3)])
        windows = [_window(f'b{i}', f'r{j}', distance=800.0) for i in range(3) for j in range(3)]
        spec = ER.ShotSpec(accuracy=0.6, destroy_capacity=0.5)
        profiles = _profiles({'b0': (3.0, 2.0)}, default=(5.0, 2.0))
        plain = ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(7),
                                      reaction_profile_for=profiles)
        explicit = ER.resolve_engagement(blue, red, windows, _always(spec), random.Random(7),
                                         extra_forces=(), reaction_profile_for=profiles)
        self.assertEqual(plain, explicit)

    def test_interceptor_stock_is_shared_across_fronts_in_time_order(self):
        """X intercetta per entrambi i fronti con UNA scorta (3 colpi, 2 canali).

        A lancia 2 colpi intercettabili a t = 3 e a t = 10, B lancia 2 colpi a t = 5.
        Timeline congiunta: t=3 ne ferma 2 (scorta 1), t=5 — il colpo di B, nel mezzo
        dell'ingaggio con A — ne ferma 1 (scorta 0), t=10 nessuno. Risolvendo prima (X,A)
        per intero, la scorta sarebbe andata tutta ad A (t=3 e t=10) e B non sarebbe stato
        intercettato affatto.
        """
        interceptor = _Asset('x1', ammunition=3)
        x = _Force('X', 'Blue', [interceptor], interceptors=[(interceptor, 2)])
        a = _Force('A', 'Red', [_Asset('a1')])
        b = _Force('B', 'Green', [_Asset('b1')])
        windows = [_window('x1', 'a1', t_end=12.0), _window('x1', 'b1', t_end=12.0)]

        def fire(shooter, target):
            if shooter.id == 'x1':
                return None
            cycle = 7.0 if shooter.id == 'a1' else 100.0
            return _miss(rounds=2, interceptable=True, cycle_time=cycle)

        result = ER.resolve_engagement(x, a, windows, fire, random.Random(0), extra_forces=[b],
                                       thresholds=_THREE_SIDES,
                                       reaction_profile_for=_profiles({'a1': (3.0, 1.0),
                                                                       'b1': (5.0, 1.0)}))

        self.assertEqual([(s.t_launch, s.shooter_id) for s in result.salvos],
                         [(3.0, 'a1'), (5.0, 'b1'), (10.0, 'a1')])
        self.assertEqual([(r.time, r.intercepted) for r in result.resolutions],
                         [(3.0, 2), (5.0, 1), (10.0, 0)])
        interceptions = [(e.time, e.rounds) for e in result.ammunition_events
                         if e.purpose == ER.PURPOSE_INTERCEPTION]
        self.assertEqual(interceptions, [(3.0, 2), (5.0, 1)])
        self.assertEqual(result.ammunition_consumed()['x1'], 3)

    def test_shooter_ammunition_is_consumed_by_both_fronts(self):
        """Un tiratore di X con 2 colpi: uccide a1 (A distrutta), poi passa al fronte B e
        spende l'ultimo colpo su b1; b2 resta intatto per mancanza di munizioni, non perche'
        la run si sia fermata alla distruzione di A. (Il lato di B e' senza dottrina, quindi
        B non si disingaggia: l'unico limite al fuoco di x1 e' la scorta.)"""
        x = _Force('X', 'Blue', [_Asset('x1', ammunition=2)])
        a = _Force('A', 'Red', [_Asset('a1')])
        b = _Force('B', 'Green', [_Asset('b1'), _Asset('b2')])
        windows = [_window('x1', 'a1'), _window('x1', 'b1', t_start=5.0),
                   _window('x1', 'b2', t_start=5.0)]

        def fire(shooter, target):
            return _kill() if shooter.id == 'x1' else None

        with patch(_ER_LOGGER):
            result = ER.resolve_engagement(x, a, windows, fire, random.Random(0), extra_forces=[b],
                                           thresholds={'Blue': _THREE_SIDES['Blue'],
                                                       'Red': _THREE_SIDES['Red']},
                                           reaction_profile_for=_profiles({}, default=(1.0, 1.0)))

        self.assertEqual([(s.t_launch, s.target_id) for s in result.salvos],
                         [(1.0, 'a1'), (6.0, 'b1')])
        self.assertEqual(result.outcome_of('A').outcome, ER.DESTROYED)
        self.assertEqual(result.outcome_of('B').lost, 1)
        self.assertEqual(result.ammunition_consumed(), {'x1': 2})
        self.assertEqual([o.force_id for o in result.forces], ['X', 'A', 'B'])

    def _disengaging_x(self):
        """X (2 asset) contro A e B; A e B hanno anche un fronte comune, indipendente da X.

        - a1 (pronto a t=2) uccide x1 a t=2: shock 0.5, X si disingaggia a t=2.
        - b1 (pronto a t=1, un colpo al secondo) spara su X a t=1 e a t=2 con tempo di volo
          5: due salve in volo quando X rompe il contatto, che atterrano a t=6 e t=7.
        - x2 e x1 (pronti a t=1.5) sparano a vuoto su A e B; il loro lancio successivo
          (t=2.5) cade dopo il disingaggio e non parte.
        - Il fronte A-B si apre a t=20 e prosegue fino a t=100 a colpi mancati.
        """
        x = _Force('X', 'Blue', [_Asset('x1'), _Asset('x2')])
        a = _Force('A', 'Red', [_Asset('a1')])
        b = _Force('B', 'Green', [_Asset('b1')])
        windows = [_window('x1', 'a1', t_end=100.0), _window('x2', 'a1', t_end=100.0),
                   _window('x1', 'b1', t_end=100.0), _window('x2', 'b1', t_end=100.0),
                   _window('a1', 'b1', t_start=20.0, t_end=100.0)]

        def fire(shooter, target):
            if shooter.id == 'a1' and target.id.startswith('x'):
                return _kill()
            if shooter.id == 'b1' and target.id.startswith('x'):
                return _miss(time_of_flight=5.0)
            return _miss()

        result = ER.resolve_engagement(x, a, windows, fire, random.Random(0), extra_forces=[b],
                                       thresholds=_THREE_SIDES,
                                       reaction_profile_for=_profiles({'a1': (2.0, 1.0),
                                                                       'b1': (1.0, 1.0),
                                                                       'x1': (1.5, 1.0),
                                                                       'x2': (1.5, 1.0)}))
        return result

    def test_disengaged_force_is_reported(self):
        outcome = self._disengaging_x().outcome_of('X')
        self.assertEqual(outcome.outcome, ER.DISENGAGED)
        self.assertEqual(outcome.time, 2.0)
        self.assertEqual(outcome.lost, 1)

    def test_no_new_launch_from_or_towards_the_disengaged_force(self):
        result = self._disengaging_x()
        x_assets = {'x1', 'x2'}

        self.assertTrue(result.salvos)
        for salvo in result.salvos:
            if salvo.shooter_id in x_assets or salvo.target_id in x_assets:
                self.assertLessEqual(salvo.t_launch, 2.0, salvo)

    def test_salvos_in_flight_still_land_on_the_disengaged_force(self):
        result = self._disengaging_x()
        late = [s for s in result.salvos if s.target_force_id == 'X' and s.t_impact > 2.0]

        self.assertEqual([(s.t_launch, s.t_impact) for s in late], [(1.0, 6.0), (2.0, 7.0)])
        self.assertEqual([r.time for r in result.resolutions if r.force_id == 'X' and r.time > 2.0],
                         [6.0, 7.0])

    def test_independent_front_keeps_being_resolved(self):
        """Il disingaggio di X non ferma il fronte A-B (niente flag globale di contatto rotto)."""
        result = self._disengaging_x()
        front = [s for s in result.salvos if {s.shooter_id, s.target_id} == {'a1', 'b1'}]

        self.assertTrue(front)
        self.assertTrue(all(s.t_launch >= 20.0 for s in front))
        self.assertEqual({s.shooter_id for s in front}, {'a1', 'b1'})
        self.assertGreater(max(s.t_launch for s in front), 90.0)
        self.assertEqual(result.outcome_of('A').outcome, ER.HELD)
        self.assertEqual(result.outcome_of('B').outcome, ER.HELD)

    def test_multi_force_run_is_deterministic(self):
        self.assertEqual(self._disengaging_x(), self._disengaging_x())

    def test_repeated_force_raises(self):
        x = _Force('X', 'Blue', [_Asset('x1')])
        a = _Force('A', 'Red', [_Asset('a1')])
        with self.assertRaises(ValueError):
            ER.resolve_engagement(x, a, [], _always(_kill()), random.Random(0), extra_forces=[x])

    def test_asset_shared_between_forces_raises(self):
        shared = _Asset('s1')
        x = _Force('X', 'Blue', [_Asset('x1')])
        a = _Force('A', 'Red', [shared])
        b = _Force('B', 'Green', [shared])
        with self.assertRaises(ValueError):
            ER.resolve_engagement(x, a, [], _always(_kill()), random.Random(0), extra_forces=[b],
                                  thresholds=_THREE_SIDES)

    def test_empty_extra_force_does_not_block_the_others(self):
        """Con 3+ forze una forza senza asset impegnabili non rende l'ingaggio irrisolvibile."""
        x = _Force('X', 'Blue', [_Asset('x1')])
        a = _Force('A', 'Red', [_Asset('a1')])
        empty = _Force('B', 'Green', [_Asset('b1', health=None)])
        with patch(_ER_LOGGER):
            result = ER.resolve_engagement(x, a, [_window('x1', 'a1')], _always(_miss()),
                                           random.Random(0), extra_forces=[empty],
                                           thresholds=_THREE_SIDES)

        self.assertIsNotNone(result)
        self.assertTrue(result.salvos)
        self.assertEqual(result.outcome_of('B').committed, 0)
        self.assertEqual(result.outcome_of('B').outcome, ER.HELD)

    def test_fewer_than_two_usable_forces_returns_none(self):
        x = _Force('X', 'Blue', [_Asset('x1')])
        a = _Force('A', 'Red', [_Asset('a1', health=None)])
        b = _Force('B', 'Green', [_Asset('b1', health=None)])
        with patch(_ER_LOGGER):
            self.assertIsNone(ER.resolve_engagement(x, a, [], _always(_kill()), random.Random(0),
                                                    extra_forces=[b], thresholds=_THREE_SIDES))


class TestShotSpec(unittest.TestCase):

    def test_valid(self):
        spec = ER.ShotSpec(accuracy=0.5, destroy_capacity=0.5, rounds=2, time_of_flight=3.0)
        self.assertEqual(spec.rounds, 2)

    def test_invalid_values_raise(self):
        for kwargs in ({'accuracy': 1.2, 'destroy_capacity': 0.5},
                       {'accuracy': 0.5, 'destroy_capacity': 0.5, 'rounds': 0},
                       {'accuracy': 0.5, 'destroy_capacity': 0.5, 'time_of_flight': -1.0},
                       {'accuracy': 0.5, 'destroy_capacity': 0.5, 'cycle_time': 0.0}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    ER.ShotSpec(**kwargs)

    def test_non_numeric_probability_raises(self):
        with self.assertRaises(TypeError):
            ER.ShotSpec(accuracy='0.5', destroy_capacity=0.5)


# ── NON-MUTAZIONE E APPLICAZIONE, CON OGGETTI REALI ───────────────────────────

class TestIntegrationWithRealObjects(unittest.TestCase):
    """Stesso giro con Military e Mobile reali: la superficie letta dagli stub e' quella vera."""

    def setUp(self):
        self._loggers = [patch('Code.Dynamic_War_Manager.Source.Asset.Mobile.logger'),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Asset.logger')]
        for p in self._loggers:
            p.start()

        self.blue = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name='Blue', side='Blue')
        self.red = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name='Red', side='Red')
        self.blue._assets = {}
        self.red._assets = {}

        for military, prefix in ((self.blue, 'blue'), (self.red, 'red')):
            for index in range(3):
                asset = Mobile(block=MagicMock(spec=Block), name=f'{prefix}-{index}',
                               position=Point3D(0, 0, 0))
                asset.id = f'{prefix}-{index}'
                asset.ammunition = 10
                military._assets[asset.id] = asset

        self.windows = [_window(f'blue-{i}', f'red-{i}', range_b=None) for i in range(3)]
        self.spec = ER.ShotSpec(accuracy=0.7, destroy_capacity=0.3)

    def tearDown(self):
        for p in self._loggers:
            p.stop()

    def _resolve(self, seed=11):
        return ER.resolve_engagement(self.blue, self.red, self.windows, _always(self.spec),
                                     random.Random(seed),
                                     reaction_profile_for=_profiles({}, default=(2.0, 1.0)))

    def test_forces_are_identified_by_domain_id(self):
        result = self._resolve()
        self.assertEqual([o.force_id for o in result.forces], [self.blue.id, self.red.id])

    def test_resolver_does_not_mutate_assets(self):
        self._resolve()

        for asset in list(self.blue.assets.values()) + list(self.red.assets.values()):
            self.assertEqual(asset.health, 100)
            self.assertEqual(asset.ammunition, 10)

    def test_apply_writes_damage_and_consumption(self):
        result = self._resolve()
        summary = ER.apply_engagement_result(result, self.blue, self.red)

        self.assertEqual(summary['damage_events'], len(result.damage_events))
        self.assertEqual(summary['missing_assets'], 0)

        final_health = {}
        for event in result.damage_events:
            final_health[event.target_id] = event.health_after

        for asset_id, health in final_health.items():
            self.assertEqual(self.red.assets[asset_id].health, health)

        for asset_id, consumed in result.ammunition_consumed().items():
            self.assertEqual(self.blue.assets[asset_id].ammunition, 10 - consumed)

    def test_applied_state_matches_the_reported_outcome(self):
        result = self._resolve()
        ER.apply_engagement_result(result, self.blue, self.red)
        lost = sum(1 for asset in self.red.assets.values() if not asset.is_operative())

        self.assertEqual(lost, result.outcome_of(self.red.id).lost)

    def test_apply_requires_a_result(self):
        with self.assertRaises(TypeError):
            ER.apply_engagement_result('nope', self.blue)


if __name__ == '__main__':
    unittest.main()
