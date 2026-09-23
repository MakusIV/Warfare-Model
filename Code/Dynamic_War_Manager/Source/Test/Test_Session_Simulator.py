"""Tests per Logic/Session_Simulator — FASE 6 del motore di sessioni virtuali.

L'orchestratore non ha logica di calcolo propria: mette in fila scheduler, risolutore,
applicazione, carburante e assemblaggio. I test verificano quindi la FILA — che i pezzi si
incastrino su oggetti reali e che l'ordine sia quello dichiarato — non i singoli modelli,
gia' coperti dai rispettivi test.

Strategia di setup
------------------
* Forze `Military` REALI e rotte `DataType.Route/Edge/Waypoint` REALI.
* Asset: sottoclassi REALI di `Mobile` chiamate `Aircraft`/`Vehicle`, perche'
  `Contact_Scheduler.detection_mode_for` classifica per nome di classe (stessa tecnica di
  Test_Contact_Scheduler). Salute, danno, munizioni e carburante sono quindi quelli veri di
  `Asset`/`Mobile`; sono imposti solo portata di rilevamento e autonomia (i registri sono
  coperti da Test_Mobile/Test_Aircraft), cosi' ogni numero e' calcolabile a mano.
* Profili di reazione imposti, per non dipendere dai default di Reaction_Profile.
"""

import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Context.Context import MILITARY_CATEGORY
from Code.Dynamic_War_Manager.Source.Context.Reaction_Profile import ReactionProfile
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS

_SOURCE = 'Code.Dynamic_War_Manager.Source.'
_LOGGERS = [_SOURCE + name + '.logger' for name in (
    'Asset.Mobile', 'Asset.Asset', 'Logic.Engagement_Resolver', 'Logic.Contact_Scheduler',
    'Logic.Fuel_Model', 'Logic.Session_Simulator', 'Command.Session_Types', 'Block.Military')]

# Autonomie imposte [m]: al regime di combattimento si consuma il doppio.
AUTONOMY = {'nominal': 1_000_000.0, 'max': 500_000.0}
SENSOR_RANGE = 5_000.0


# ── ASSET E FORZE ─────────────────────────────────────────────────────────────

class _SensorMixin:
    def detection_range(self, mode, sensor=None, range_type='acquisition_range'):
        return SENSOR_RANGE

    def fuel_autonomy(self, regime='nominal'):
        return AUTONOMY[regime]


class Aircraft(_SensorMixin, Mobile):
    """Nome di classe -> modo 'air' per lo scheduler."""


class Vehicle(_SensorMixin, Mobile):
    """Nome di classe -> modo 'ground' per lo scheduler."""


def _asset(cls, asset_id, x, y, z=0.0, ammunition=20, fuel=1.0, speed=None):
    asset = cls(block=MagicMock(spec=Block), name=asset_id, position=Point3D(x, y, z))
    asset.id = asset_id
    asset.ammunition = ammunition
    asset.fuel = fuel

    if speed is not None:
        asset.speed = {'nominal': speed, 'max': speed}

    return asset


def _force(name, side, assets):
    military = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name=name, side=side)
    # Id STABILE: Block genera un id con suffisso casuale (Utility.setId), e l'id di forza e'
    # chiave dell'RNG. In campagna l'id e' persistito; qui lo si fissa come farebbe il caricamento.
    military.id = name
    military._assets = {asset.id: asset for asset in assets}
    return military


def _route(points, speed, name, z=0.0):
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(x, y, z), obj_reference=None)
                 for i, (x, y) in enumerate(points)]
    edges = {}

    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0,
                                       speed=speed, name=f'{name}-E{i}')

    return Route(route_type='air', edges=edges, name=name)


def _profile(asset):
    return ReactionProfile(detection=4.0, evaluation=1.0, command=0.0, actuation=0.0, source='test')


SPEC = ER.ShotSpec(accuracy=0.7, destroy_capacity=0.3, rounds=1)


def _fire(shooter, target):
    return SPEC


class _Base(unittest.TestCase):
    def setUp(self):
        self._patches = [patch(target, MagicMock()) for target in _LOGGERS]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()

    def _scenario(self, red_offset=0.0):
        """Due forze per lato, due fronti indipendenti 100 km l'uno dall'altro.

        Fronte ovest (x = 0): Blue-North (2 aerei) sorvola Red-East (2 veicoli fermi).
        Fronte est (x = 100 km): Blue-South (1 aereo) sorvola Red-West (1 veicolo fermo).
        Rotte di 40 km a 200 m/s: 200 s. `red_offset` sposta tutti i rossi lungo y.
        """
        blue_north = _force('Blue-North', 'Blue', [
            _asset(Aircraft, 'bn1', 0, -20_000, speed=200.0),
            _asset(Aircraft, 'bn2', 500, -20_000, speed=200.0)])
        blue_south = _force('Blue-South', 'Blue', [
            _asset(Aircraft, 'bs1', 100_000, -20_000, speed=200.0)])
        red_east = _force('Red-East', 'Red', [
            _asset(Vehicle, 're1', 0, red_offset), _asset(Vehicle, 're2', 300, red_offset)])
        red_west = _force('Red-West', 'Red', [_asset(Vehicle, 'rw1', 100_000, red_offset)])

        routes = {
            'bn1': _route([(0, -20_000), (0, 20_000)], 200.0, 'r-bn1'),
            'bn2': _route([(500, -20_000), (500, 20_000)], 200.0, 'r-bn2'),
            'bs1': _route([(100_000, -20_000), (100_000, 20_000)], 200.0, 'r-bs1'),
        }

        return [blue_north, blue_south], [red_east, red_west], routes

    def _order(self, session_id='S-test', **kwargs):
        kwargs.setdefault('t_end', 3600.0)
        return SessionOrder(session_id, t_start=0.0, **kwargs)

    def _run(self, session_id='S-test', red_offset=0.0, fire=_fire, **kwargs):
        blue, red, routes = self._scenario(red_offset)
        outcome = SS.run_session(self._order(session_id), blue, red, fire, routes=routes,
                                 reaction_profile_for=_profile, **kwargs)
        return outcome, blue, red


class TestEngagedAssetsCountsInterceptions(unittest.TestCase):
    """Regressione: un asset che ha SOLO intercettato deve contare come 'ha combattuto'.

    `_engaged_assets` decide il regime di consumo carburante (COMBAT_REGIME vs CRUISE_REGIME,
    v. `run_session`). Fino a questo fix leggeva `salvos`/`ammunition_events` ma non
    `interception_events`: da quando le intercettazioni sono un tipo a se' (`InterceptionEvent`,
    non piu' `AmmunitionEvent(purpose=PURPOSE_INTERCEPTION)`), un intercettore che non ha mai
    sparato una salva propria e non e' mai stato bersaglio restava classificato 'nominal'
    (crociera) invece di 'max' (combattimento) — nessun test se ne accorgeva.
    """

    def test_interceptor_only_asset_is_engaged(self):
        result = ER.EngagementResult(
            t_start=0.0, t_end=1.0, forces=(),
            interception_events=(
                ER.InterceptionEvent(time=1.0, asset_id='sam1', interceptions=2,
                                     force_id='red', salvo_ids=(0,)),
            ),
        )

        self.assertIn('sam1', SS._engaged_assets(result))

    def test_asset_with_no_activity_is_not_engaged(self):
        result = ER.EngagementResult(t_start=0.0, t_end=1.0, forces=())

        self.assertEqual(SS._engaged_assets(result), set())


# ── SCENARIO END-TO-END ───────────────────────────────────────────────────────

class TestEndToEnd(_Base):
    """2 forze per lato, rotte reali: contatti, ingaggi, applicazione, carburante, esito."""

    def setUp(self):
        super().setUp()
        self.outcome, self.blue, self.red = self._run()
        self.assets = {a.id: a for f in self.blue + self.red for a in f.assets.values()}

    def test_one_engagement_per_front(self):
        self.assertIsInstance(self.outcome, SessionOutcome)
        pairs = {tuple(o.force_id for o in engagement) for engagement in self.outcome.engagement_outcomes}
        self.assertEqual(pairs, {(self.blue[0].id, self.red[0].id), (self.blue[1].id, self.red[1].id)})

    def test_fronts_are_resolved_in_time_order(self):
        """Stesso istante di primo contatto: vale l'id canonico dell'evento (JSON)."""
        first = [engagement[0].force_id for engagement in self.outcome.engagement_outcomes]
        expected = sorted([self.blue[0].id, self.blue[1].id],
                          key=lambda fid: SS.engagement_event_id(
                              fid, self.red[0].id if fid == self.blue[0].id else self.red[1].id))
        self.assertEqual(first, expected)

    def test_something_actually_happened(self):
        self.assertGreater(len(self.outcome.damage_events), 0)
        self.assertGreater(len(self.outcome.ammunition_events), 0)

    def test_damage_is_applied_to_the_real_assets(self):
        final = {}
        for event in self.outcome.damage_events:
            final[event.target_id] = event.health_after

        for asset_id, asset in self.assets.items():
            self.assertEqual(asset.health, final.get(asset_id, 100), asset_id)

    def test_ammunition_is_applied_to_the_real_assets(self):
        consumed = self.outcome.ammunition_consumed()

        for asset_id, asset in self.assets.items():
            self.assertEqual(asset.ammunition, 20 - consumed.get(asset_id, 0), asset_id)

    def test_fuel_events_only_for_moving_assets(self):
        self.assertEqual(sorted(e.asset_id for e in self.outcome.fuel_events), ['bn1', 'bn2', 'bs1'])

    def test_fuel_distance_time_and_application(self):
        for event in self.outcome.fuel_events:
            self.assertAlmostEqual(event.distance, 40_000.0, places=6)
            self.assertAlmostEqual(event.time, 200.0, places=6)
            self.assertAlmostEqual(self.assets[event.asset_id].fuel, 1.0 - event.amount)

    def test_regime_is_combat_only_for_assets_that_fought(self):
        fought = set()
        for event in self.outcome.ammunition_events:
            fought.add(event.asset_id)
        for event in self.outcome.damage_events:
            fought.add(event.target_id)

        for event in self.outcome.fuel_events:
            expected = SS.COMBAT_REGIME if event.asset_id in fought else SS.CRUISE_REGIME
            self.assertEqual(event.regime, expected, event.asset_id)
            self.assertAlmostEqual(event.amount, 40_000.0 / AUTONOMY[expected])

    def test_declared_interval(self):
        self.assertEqual((self.outcome.t_start, self.outcome.t_end), (0.0, 3600.0))


class TestSeedDiscipline(_Base):
    """RNG: uno stream per ingaggio, da SessionOrder.rng e solo da li'."""

    def test_same_order_same_outcome(self):
        first, _, _ = self._run('S-alpha')
        second, _, _ = self._run('S-alpha')
        self.assertEqual(first, second)
        self.assertGreater(len(first.damage_events), 0)

    def test_different_session_id_changes_the_draws(self):
        self.assertNotEqual(self._run('S-alpha')[0].damage_events,
                            self._run('S-beta')[0].damage_events)

    def test_engagement_uses_the_documented_stream(self):
        """Ripetere a mano l'ingaggio del fronte est con order.rng(None, event_id, 0)."""
        outcome, _, _ = self._run('S-gamma')
        # Scenario pulito (i due fronti non condividono forze), stesso ingaggio, stream documentato.
        blue3, red3, routes = self._scenario()
        order = self._order('S-gamma')
        windows = CS.schedule_contacts([blue3[1]], [red3[1]], 3600.0, routes=routes)
        legs = {'bs1': CS.clamp_legs(CS.route_legs(routes['bs1']), 0.0, 3600.0),
                'rw1': CS.static_legs(red3[1].assets['rw1'].position, 0.0, 3600.0)}
        manual = ER.resolve_engagement(
            blue3[1], red3[1], windows, _fire,
            order.rng(mission_id=None, event_id=SS.engagement_event_id(blue3[1].id, red3[1].id)),
            legs=legs, reaction_profile_for=_profile)
        self.assertIn(manual.forces, outcome.engagement_outcomes)
        self.assertTrue(set(manual.damage_events) <= set(outcome.damage_events))

    def test_event_id_is_pure_and_unambiguous(self):
        self.assertEqual(SS.engagement_event_id('a', 'b'), SS.engagement_event_id('a', 'b'))
        self.assertNotEqual(SS.engagement_event_id('a:b', 'c'), SS.engagement_event_id('a', 'b:c'))
        self.assertNotEqual(SS.engagement_event_id('a', 'b'), SS.engagement_event_id('a', 'b', 'c'))

    def test_event_id_depends_on_the_set_of_forces_not_their_order(self):
        """Una componente ha un solo seed, qualunque sia l'ordine di passaggio delle forze."""
        self.assertEqual(SS.engagement_event_id('a', 'b'), SS.engagement_event_id('b', 'a'))
        self.assertEqual(SS.engagement_event_id('x', 'a', 'b'), SS.engagement_event_id('b', 'x', 'a'))

    def test_event_id_rejects_out_of_domain_arguments(self):
        for ids in (('a',), (), ('a', 'a'), ('a', ''), ('a', None)):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                SS.engagement_event_id(*ids)


class TestNoContact(_Base):
    """Nessun incontro non e' un errore: esito vuoto ma valido."""

    def test_far_apart_forces_produce_no_engagement(self):
        outcome, blue, red = self._run(red_offset=10_000_000.0)
        self.assertEqual(outcome.engagement_outcomes, ())
        self.assertEqual(outcome.damage_events, ())
        self.assertEqual(outcome.ammunition_events, ())
        # Il movimento c'e' comunque, a regime di crociera.
        self.assertEqual(len(outcome.fuel_events), 3)
        self.assertTrue(all(e.regime == SS.CRUISE_REGIME for e in outcome.fuel_events))

    def test_nothing_moves_nothing_meets(self):
        blue, red, _ = self._scenario(red_offset=10_000_000.0)
        outcome = SS.run_session(self._order(), blue, red, _fire)
        self.assertEqual(outcome, SessionOutcome('S-test', 0.0, 3600.0))

    def test_empty_sides(self):
        outcome = SS.run_session(self._order(), [], [], _fire)
        self.assertEqual(outcome, SessionOutcome('S-test', 0.0, 3600.0))


class TestTwoFronts(_Base):
    """Una forza impegnata su due fronti: UNA componente connessa, UN ingaggio congiunto.

    Il Raider (lato A) sorvola Red-A e poi Red-B (lato B): le finestre Raider-Red-A e
    Raider-Red-B legano le tre forze in una componente, risolta con una sola chiamata a
    `resolve_engagement` (prima erano due ingaggi applicati in sequenza).
    """

    def _forces(self):
        raider = _force('Raider', 'Blue', [_asset(Aircraft, 'x1', -20_000, 0, speed=200.0),
                                            _asset(Aircraft, 'x2', -20_000, 300, speed=200.0)])
        red_a = _force('Red-A', 'Red', [_asset(Vehicle, 'ra1', 0, 0)])
        red_b = _force('Red-B', 'Red', [_asset(Vehicle, 'rb1', 30_000, 0)])
        routes = {'x1': _route([(-20_000, 0), (50_000, 0)], 200.0, 'r-x1'),
                  'x2': _route([(-20_000, 300), (50_000, 300)], 200.0, 'r-x2')}
        return raider, red_a, red_b, routes

    def _two_fronts(self, session_id, reverse_red=False):
        raider, red_a, red_b, routes = self._forces()
        reds = [red_b, red_a] if reverse_red else [red_a, red_b]
        outcome = SS.run_session(self._order(session_id), [raider], reds, _fire,
                                 routes=routes, reaction_profile_for=_profile)
        return outcome, raider, red_a, red_b

    def test_connected_forces_are_one_engagement(self):
        outcome, raider, red_a, red_b = self._two_fronts('S-fronts')
        self.assertEqual([tuple(o.force_id for o in e) for e in outcome.engagement_outcomes],
                         [(raider.id, red_a.id, red_b.id)])
        self.assertEqual(len(outcome.outcomes_of(raider.id)), 1)

    def test_one_resolver_call_with_all_forces(self):
        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as spy:
            outcome, raider, red_a, red_b = self._two_fronts('S-fronts')

        spy.assert_called_once()
        args, kwargs = spy.call_args
        self.assertEqual([f.id for f in (args[0], args[1], *kwargs['extra_forces'])],
                         sorted([raider.id, red_a.id, red_b.id]))
        # Le finestre di entrambi i fronti arrivano nella stessa chiamata.
        pairs = {(w.asset_a_id, w.asset_b_id) for w in args[2]}
        self.assertTrue({a for a, _ in pairs} <= {'x1', 'x2'})
        self.assertEqual({b for _, b in pairs}, {'ra1', 'rb1'})
        self.assertGreater(len(outcome.damage_events), 0)

    def test_result_is_applied_to_all_the_forces_of_the_component(self):
        with patch.object(ER, 'apply_engagement_result', wraps=ER.apply_engagement_result) as spy:
            outcome, raider, red_a, red_b = self._two_fronts('S-fronts')

        spy.assert_called_once()
        self.assertEqual({f.id for f in spy.call_args[0][1:]}, {raider.id, red_a.id, red_b.id})

        final = {}
        for event in outcome.damage_events:
            final[event.target_id] = event.health_after
        consumed = outcome.ammunition_consumed()

        for force in (raider, red_a, red_b):
            for asset_id, asset in force.assets.items():
                self.assertEqual(asset.health, final.get(asset_id, 100), asset_id)
                self.assertEqual(asset.ammunition, 20 - consumed.get(asset_id, 0), asset_id)

    def test_health_is_chained_within_the_joint_engagement(self):
        """Una sola timeline per asset: ogni before == l'after precedente."""
        for session_id in ('S-f1', 'S-f2', 'S-f3', 'S-f4'):
            outcome, *_ = self._two_fronts(session_id)
            last = {}

            for event in outcome.damage_events:
                if event.target_id in last:
                    self.assertEqual(event.health_before, last[event.target_id])
                last[event.target_id] = event.health_after

    def test_joint_engagement_is_deterministic(self):
        """Stesso ordine, forze con id stabili -> stesso esito; anche con i lati passati in
        un altro ordine (componente e seed dipendono dall'insieme delle forze)."""
        first, *_ = self._two_fronts('S-det')
        second, *_ = self._two_fronts('S-det')
        reversed_order, *_ = self._two_fronts('S-det', reverse_red=True)
        self.assertEqual(first, second)
        self.assertEqual(first, reversed_order)
        self.assertGreater(len(first.damage_events), 0)

    def test_stable_ids_from_the_constructor(self):
        """`Military(id=...)` (non la mutazione di .id) basta per il determinismo."""
        def build():
            raider = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name='Raider',
                              side='Blue', id='raider-stable')
            raider._assets = {a.id: a for a in (_asset(Aircraft, 'x1', -20_000, 0, speed=200.0),)}
            reds = []
            for name, x in (('red-a-stable', 0), ('red-b-stable', 30_000)):
                red = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name=name,
                               side='Red', id=name)
                red._assets = {f'{name}-1': _asset(Vehicle, f'{name}-1', x, 0)}
                reds.append(red)
            routes = {'x1': _route([(-20_000, 0), (50_000, 0)], 200.0, 'r-x1')}
            return SS.run_session(self._order('S-stable'), [raider], reds, _fire, routes=routes,
                                  reaction_profile_for=_profile)

        first, second = build(), build()
        self.assertEqual(first, second)
        self.assertEqual([tuple(o.force_id for o in e) for e in first.engagement_outcomes],
                         [('raider-stable', 'red-a-stable', 'red-b-stable')])

    def test_disjoint_components_stay_separate(self):
        """Nessun legame fra i due fronti dello scenario base: due componenti, due chiamate."""
        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as spy:
            outcome, _, _ = self._run('S-disjoint')

        self.assertEqual(spy.call_count, 2)
        self.assertTrue(all(call.kwargs['extra_forces'] == [] for call in spy.call_args_list))
        self.assertEqual(len(outcome.engagement_outcomes), 2)


class TestConnectedComponents(unittest.TestCase):
    """`_connected_components`: grafo delle forze, visita deterministica."""

    def test_chain_is_one_component(self):
        groups = {('a1', 'b1'): ['w1'], ('a2', 'b1'): ['w2'], ('a2', 'b2'): ['w3']}
        self.assertEqual(SS._connected_components(groups),
                         [(('a1', 'a2', 'b1', 'b2'), ['w1', 'w2', 'w3'])])

    def test_disjoint_pairs_and_order_independence(self):
        groups = {('a2', 'b2'): ['w2'], ('a1', 'b1'): ['w1']}
        expected = [(('a1', 'b1'), ['w1']), (('a2', 'b2'), ['w2'])]
        self.assertEqual(SS._connected_components(groups), expected)
        self.assertEqual(SS._connected_components(dict(reversed(list(groups.items())))), expected)

    def test_empty(self):
        self.assertEqual(SS._connected_components({}), [])


class TestSessionInterval(_Base):

    def test_open_session_requires_horizon(self):
        blue, red, routes = self._scenario()
        order = SessionOrder('S-open', t_start=0.0)

        with self.assertRaises(ValueError):
            SS.run_session(order, blue, red, _fire, routes=routes)

        outcome = SS.run_session(order, blue, red, _fire, routes=routes, horizon=600.0,
                                 reaction_profile_for=_profile)
        self.assertEqual(outcome.t_end, 600.0)

    def test_horizon_must_agree_with_the_order(self):
        blue, red, routes = self._scenario()

        with self.assertRaises(ValueError):
            SS.run_session(self._order(), blue, red, _fire, routes=routes, horizon=10.0)

    def test_salvos_in_flight_extend_the_outcome(self):
        """Impatti dopo la fine: l'esito e' esteso, non troncato (R4)."""
        slow = ER.ShotSpec(accuracy=1.0, destroy_capacity=0.3, time_of_flight=5_000.0)
        outcome, _, _ = self._run(fire=lambda s, t: slow)
        self.assertGreater(outcome.t_end, 3600.0)
        self.assertGreaterEqual(outcome.t_end, max(e.time for e in outcome.damage_events))


class TestFuelExhaustion(_Base):

    def test_exhaustion_is_reported_not_simulated(self):
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0, 0, fuel=0.01, speed=200.0)])]
        route = _route([(0, 0), (0, 40_000)], 200.0, 'r-b1')
        outcome = SS.run_session(self._order(), blue, [], _fire, routes={'b1': route})

        event, = outcome.fuel_events
        self.assertTrue(event.exhausted)
        self.assertAlmostEqual(event.distance_covered, 10_000.0)
        self.assertEqual(blue[0].assets['b1'].fuel, 0.0)


class TestInputs(_Base):

    def test_force_outside_force_ids_raises(self):
        blue, red, routes = self._scenario()
        order = SessionOrder('S', t_start=0.0, t_end=60.0, force_ids=(blue[0].id,))

        with self.assertRaises(ValueError):
            SS.run_session(order, blue, red, _fire)

    def test_same_force_on_both_sides_raises(self):
        blue, _, _ = self._scenario()

        with self.assertRaises(ValueError):
            SS.run_session(self._order(), blue, [blue[0]], _fire)

    def test_bad_arguments_raise(self):
        with self.assertRaises(TypeError):
            SS.run_session('order', [], [], _fire)
        with self.assertRaises(TypeError):
            SS.run_session(self._order(), [], [], 'nope')


if __name__ == '__main__':
    unittest.main()
