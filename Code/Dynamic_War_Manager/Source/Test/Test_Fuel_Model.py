"""Tests per Logic/Fuel_Model — consumo di carburante per movimento (Fase 5).

Gli asset sono stub che portano i metodi REALI di Mobile sul carburante (consume_fuel,
fuel_for_distance, ...) con un'autonomia imposta: cosi' ogni numero e' calcolabile a mano e
il test verifica il contratto del modulo, non i registri (coperti da Test_Mobile/Test_Aircraft).
"""

import unittest
from unittest.mock import MagicMock, patch

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM


class _FuelStub:
    fuel = Mobile.fuel
    has_fuel = Mobile.has_fuel
    consume_fuel = Mobile.consume_fuel
    fuel_for_distance = Mobile.fuel_for_distance
    fuel_range_remaining = Mobile.fuel_range_remaining

    def __init__(self, asset_id='a1', fuel=1.0, autonomy=100_000.0):
        self.id = asset_id
        self._fuel = fuel
        self._autonomy = autonomy

    def fuel_autonomy(self, regime='nominal'):
        return self._autonomy


class _Base(unittest.TestCase):
    def setUp(self):
        self._patches = [patch('Code.Dynamic_War_Manager.Source.Logic.Fuel_Model.logger', MagicMock()),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Mobile.logger', MagicMock())]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()


class TestBuildFuelEvent(_Base):
    """Calcolo senza applicazione: numeri semplici e limite al carburante disponibile."""

    def test_known_distance_gives_expected_amount(self):
        """Autonomia 100 km, tratta 25 km -> un quarto del pieno."""
        asset = _FuelStub(fuel=1.0, autonomy=100_000.0)
        event = FM.build_fuel_event(asset, 25_000.0, time=60.0)

        self.assertAlmostEqual(event.amount, 0.25)
        self.assertAlmostEqual(event.fuel_before, 1.0)
        self.assertAlmostEqual(event.fuel_after, 0.75)
        self.assertEqual(event.distance, 25_000.0)
        self.assertEqual(event.distance_covered, 25_000.0)
        self.assertFalse(event.exhausted)
        self.assertEqual(event.time, 60.0)
        self.assertEqual(event.asset_id, 'a1')
        self.assertEqual(event.provenance, DM.DERIVED)

    def test_does_not_mutate_the_asset(self):
        asset = _FuelStub(fuel=0.5)
        FM.build_fuel_event(asset, 10_000.0)
        self.assertEqual(asset.fuel, 0.5)

    def test_insufficient_fuel_is_clamped_and_exhausts(self):
        """Serve 0.5 (50 km su 100), ce n'e' 0.2: si percorrono 20 km e si resta a secco."""
        asset = _FuelStub(fuel=0.2, autonomy=100_000.0)
        event = FM.build_fuel_event(asset, 50_000.0)

        self.assertAlmostEqual(event.amount, 0.2)
        self.assertEqual(event.fuel_after, 0.0)
        self.assertTrue(event.exhausted)
        self.assertAlmostEqual(event.distance_covered, 20_000.0)

    def test_exact_exhaustion(self):
        event = FM.build_fuel_event(_FuelStub(fuel=0.3, autonomy=100_000.0), 30_000.0)
        self.assertTrue(event.exhausted)
        self.assertEqual(event.fuel_after, 0.0)
        self.assertAlmostEqual(event.distance_covered, 30_000.0)

    def test_zero_distance(self):
        event = FM.build_fuel_event(_FuelStub(fuel=0.5), 0.0)
        self.assertEqual(event.amount, 0.0)
        self.assertFalse(event.exhausted)

    def test_empty_tank_covers_nothing(self):
        event = FM.build_fuel_event(_FuelStub(fuel=0.0), 1_000.0)
        self.assertEqual(event.amount, 0.0)
        self.assertEqual(event.distance_covered, 0.0)
        self.assertTrue(event.exhausted)

    def test_unmodelled_fuel_gives_no_event(self):
        self.assertIsNone(FM.build_fuel_event(_FuelStub(fuel=None), 1_000.0))
        self.assertIsNone(FM.build_fuel_event(_FuelStub(fuel=1.0, autonomy=None), 1_000.0))

    def test_asset_without_domain_id_gives_no_event(self):
        self.assertIsNone(FM.build_fuel_event(_FuelStub(asset_id=None), 1_000.0))

    def test_arguments_out_of_domain_raise(self):
        with self.assertRaises(ValueError):
            FM.build_fuel_event(_FuelStub(), -1.0)
        with self.assertRaises(ValueError):
            FM.build_fuel_event(_FuelStub(), 1.0, provenance='dcs')
        with self.assertRaises(TypeError):
            FM.build_fuel_event(_FuelStub(), 1.0, time='now')

    def test_event_is_frozen(self):
        event = FM.build_fuel_event(_FuelStub(), 1_000.0)
        with self.assertRaises(Exception):
            event.amount = 0.0


class TestApplyFuelEvent(_Base):

    def test_apply_consumes_the_event_amount(self):
        asset = _FuelStub(fuel=1.0, autonomy=100_000.0)
        event = FM.build_fuel_event(asset, 40_000.0)
        self.assertAlmostEqual(FM.apply_fuel_event(asset, event), 0.6)
        self.assertAlmostEqual(asset.fuel, 0.6)

    def test_apply_twice_consumes_twice(self):
        asset = _FuelStub(fuel=1.0, autonomy=100_000.0)
        event = FM.build_fuel_event(asset, 30_000.0)
        FM.apply_fuel_event(asset, event)
        FM.apply_fuel_event(asset, event)
        self.assertAlmostEqual(asset.fuel, 0.4)

    def test_exhausting_event_stops_the_asset(self):
        asset = _FuelStub(fuel=0.1, autonomy=100_000.0)
        FM.apply_fuel_event(asset, FM.build_fuel_event(asset, 50_000.0))
        self.assertEqual(asset.fuel, 0.0)
        self.assertFalse(asset.has_fuel())
        self.assertEqual(asset.fuel_range_remaining(), 0.0)

    def test_asset_without_consume_fuel_is_not_applied(self):
        event = FM.build_fuel_event(_FuelStub(), 1_000.0)

        class _Bare:
            id = 'bare'

        self.assertIsNone(FM.apply_fuel_event(_Bare(), event))

    def test_wrong_event_type_raises(self):
        with self.assertRaises(TypeError):
            FM.apply_fuel_event(_FuelStub(), object())


# ── F6-A: consumo per tratto, nel tempo, esaurimento a monte, planata ──────────

class _Leg:
    """Tratto minimo nella forma di Contact_Scheduler.Leg (letto per attributo)."""

    def __init__(self, t_start, t_end, p_start, p_end):
        self.t_start, self.t_end, self.p_start, self.p_end = t_start, t_end, p_start, p_end


class _CruiseStub(_FuelStub):
    """Stub con velocita' di crociera (profilo cinematico 'nominal' = 10 m/s)."""

    def __init__(self, cruise=10.0, **kwargs):
        super().__init__(**kwargs)
        self.speed = {'nominal': cruise, 'max': 2 * cruise} if cruise is not None else None


MOVE = _Leg(0.0, 100.0, (0.0, 0.0, 0.0), (1_000.0, 0.0, 0.0))     # 1 km in 100 s
HOLD = _Leg(100.0, 400.0, (1_000.0, 0.0, 0.0), (1_000.0, 0.0, 0.0))  # 300 s fermo


class TestLegFuelEvent(_Base):
    """Un FuelEvent per tratto: movimento in distanza, sosta nel tempo alla crociera."""

    def test_moving_leg(self):
        event = FM.build_leg_fuel_event(_CruiseStub(autonomy=100_000.0), MOVE)
        self.assertAlmostEqual(event.amount, 0.01)
        self.assertEqual((event.distance, event.t_start, event.time, event.duration), (1_000.0, 0.0, 100.0, 100.0))
        self.assertEqual(event.duration_covered, 100.0)
        self.assertFalse(event.stationary)

    def test_hold_consumes_in_time_at_cruise(self):
        """300 s alla crociera di 10 m/s = 3 km equivalenti su 100 km di autonomia."""
        event = FM.build_leg_fuel_event(_CruiseStub(autonomy=100_000.0), HOLD, regime='max')
        self.assertAlmostEqual(event.amount, 0.03)
        self.assertEqual((event.distance, event.distance_covered), (0.0, 0.0))
        self.assertTrue(event.stationary)
        self.assertEqual(event.regime, FM.HOLD_REGIME)
        self.assertEqual((event.t_start, event.time, event.duration), (100.0, 400.0, 300.0))

    def test_hold_exhausted_halfway(self):
        event = FM.build_leg_fuel_event(_CruiseStub(fuel=0.015, autonomy=100_000.0), HOLD)
        self.assertTrue(event.exhausted)
        self.assertAlmostEqual(event.duration_covered, 150.0)

    def test_hold_without_cruise_speed_does_not_consume(self):
        self.assertIsNone(FM.build_leg_fuel_event(_CruiseStub(cruise=None), HOLD))
        self.assertEqual(FM.leg_fuel_demand(_CruiseStub(cruise=None), HOLD), 0.0)

    def test_fuel_not_modelled(self):
        self.assertIsNone(FM.build_leg_fuel_event(_CruiseStub(fuel=None), MOVE))
        self.assertIsNone(FM.leg_fuel_demand(_CruiseStub(fuel=None), MOVE))


class TestFuelExhaustion(_Base):
    """Istante e punto dell'esaurimento calcolati a monte, senza mutare l'asset."""

    def test_enough_fuel(self):
        asset = _CruiseStub(fuel=1.0, autonomy=100_000.0)
        self.assertIsNone(FM.fuel_exhaustion(asset, [MOVE, HOLD]))
        self.assertEqual(asset.fuel, 1.0)

    def test_exhaustion_inside_a_moving_leg(self):
        found = FM.fuel_exhaustion(_CruiseStub(fuel=0.004, autonomy=100_000.0), [MOVE, HOLD])
        self.assertEqual(found.leg_index, 0)
        self.assertAlmostEqual(found.time, 40.0)
        self.assertAlmostEqual(found.point[0], 400.0)

    def test_exhaustion_inside_a_hold(self):
        """1 km di movimento (0,01) + 150 s di sosta (0,015): finisce a meta' sosta, fermo nel punto."""
        found = FM.fuel_exhaustion(_CruiseStub(fuel=0.025, autonomy=100_000.0), [MOVE, HOLD])
        self.assertEqual(found.leg_index, 1)
        self.assertAlmostEqual(found.time, 250.0)
        self.assertEqual(found.point, (1_000.0, 0.0, 0.0))

    def test_empty_tank_at_the_start(self):
        found = FM.fuel_exhaustion(_CruiseStub(fuel=0.0, autonomy=100_000.0), [MOVE])
        self.assertEqual((found.time, found.point), (0.0, (0.0, 0.0, 0.0)))

    def test_fuel_not_modelled_means_no_constraint(self):
        self.assertIsNone(FM.fuel_exhaustion(_CruiseStub(fuel=None), [MOVE]))


class TestGlide(_Base):

    def test_glide_range_is_altitude_times_ratio(self):
        self.assertEqual(FM.glide_range(5_000.0), 5_000.0 * FM.GLIDE_RATIO)
        self.assertEqual(FM.glide_range(-10.0), 0.0)

    def test_nearest_reachable_base(self):
        point = (0.0, 0.0, 1_000.0)      # raggio 10 km con il rapporto di default
        reach = FM.glide_range(1_000.0)
        bases = [(reach + 1.0, 0.0), (0.0, 6_000.0), (3_000.0, 0.0)]
        self.assertEqual(FM.nearest_reachable_base(point, bases), (3_000.0, 0.0))
        self.assertIsNone(FM.nearest_reachable_base(point, [(reach + 1.0, 0.0)]))
        self.assertIsNone(FM.nearest_reachable_base((0.0, 0.0, 0.0), [(1.0, 0.0)]))

    def test_tie_is_deterministic(self):
        self.assertEqual(FM.nearest_reachable_base((0.0, 0.0, 1_000.0), [(0.0, 5_000.0), (0.0, -5_000.0)]),
                         (0.0, -5_000.0))


# ── F6-B2: bingo (margine di rientro, punto di bingo) ─────────────────────────

EAST = _Leg(0.0, 10_000.0, (0.0, 0.0, 0.0), (100_000.0, 0.0, 0.0))   # 100 km in 10000 s


class TestBingo(_Base):
    """Bingo = primo istante in cui il residuo basta appena per rientrare alla base piu' vicina con la
    riserva (autonomia 100 km: 0,01 del pieno = 1 km)."""

    def test_reserve_is_a_declared_fraction(self):
        self.assertGreater(FM.BINGO_RESERVE, 0.0)
        self.assertLess(FM.BINGO_RESERVE, 1.0)

    def test_return_margin(self):
        """Pieno, 40 km di andata e 40 di rientro, riserva 0,1: margine 0,1."""
        leg = _Leg(0.0, 4_000.0, (0.0, 0.0, 0.0), (40_000.0, 0.0, 0.0))
        asset = _CruiseStub(fuel=1.0, autonomy=100_000.0)
        self.assertAlmostEqual(FM.return_margin(asset, [leg], [(0.0, 0.0)], reserve=0.1), 0.1)
        self.assertIsNone(FM.bingo_point(asset, [leg], [(0.0, 0.0)], reserve=0.1))

    def test_bingo_inside_a_moving_leg(self):
        """Carburante 0,5 (50 km), riserva 0,1 (10 km), base alla partenza: 40 - u = u -> bingo a 20 km,
        2000 s, con 0,3 a bordo; il margine a fine tratto e' 0,5 - 1 - 1 - 0,1."""
        asset = _CruiseStub(fuel=0.5, autonomy=100_000.0)
        bingo = FM.bingo_point(asset, [EAST], [(0.0, 0.0)], reserve=0.1)
        self.assertEqual((bingo.asset_id, bingo.leg_index, bingo.base), ('a1', 0, (0.0, 0.0, 0.0)))
        self.assertAlmostEqual(bingo.time, 2_000.0)
        self.assertAlmostEqual(bingo.point[0], 20_000.0)
        self.assertAlmostEqual(bingo.fuel, 0.3)
        self.assertAlmostEqual(bingo.margin, -1.6)
        self.assertEqual(asset.fuel, 0.5)

    def test_bingo_inside_a_hold(self):
        """1 km di movimento (0,01), poi sosta a 1 km dalla base (3 km equivalenti in 300 s), riserva 0:
        con 0,035 il residuo scende a 1 km (il rientro) a meta' sosta, 250 s."""
        bingo = FM.bingo_point(_CruiseStub(fuel=0.035, autonomy=100_000.0), [MOVE, HOLD], [(0.0, 0.0)], reserve=0.0)
        self.assertEqual(bingo.leg_index, 1)
        self.assertAlmostEqual(bingo.time, 250.0)
        self.assertEqual(bingo.point, (1_000.0, 0.0, 0.0))

    def test_bingo_at_the_start(self):
        """Sotto la riserva gia' alla partenza: bingo all'istante iniziale."""
        bingo = FM.bingo_point(_CruiseStub(fuel=0.05, autonomy=100_000.0), [EAST], [(0.0, 0.0)], reserve=0.1)
        self.assertEqual((bingo.time, bingo.point), (0.0, (0.0, 0.0, 0.0)))

    def test_a_base_ahead_counts(self):
        """Rotta di 60 km verso una seconda base: con 0,7 e senza riserva la base davanti resta sempre in
        portata (avvicinarsi non costa margine), nessun bingo; con riserva 0,15 la base davanti non basta
        mai e il bingo e' rispetto a quella di partenza (55 - u = u: 27,5 km)."""
        leg = _Leg(0.0, 6_000.0, (0.0, 0.0, 0.0), (60_000.0, 0.0, 0.0))
        bases = [(0.0, 0.0), (60_000.0, 0.0)]
        asset = _CruiseStub(fuel=0.7, autonomy=100_000.0)
        self.assertIsNone(FM.bingo_point(asset, [leg], bases, reserve=0.0))
        bingo = FM.bingo_point(asset, [leg], bases, reserve=0.15)
        self.assertAlmostEqual(bingo.point[0], 27_500.0)
        self.assertEqual(bingo.base, (0.0, 0.0, 0.0))

    def test_at_bingo_the_fuel_is_the_return_plus_the_reserve(self):
        """In quota e con una base fuori asse il rientro (3D, alla base a quota 0) consuma esattamente il
        residuo meno la riserva."""
        leg = _Leg(0.0, 10_000.0, (0.0, 0.0, 5_000.0), (100_000.0, 0.0, 5_000.0))
        base = (10_000.0, 20_000.0)
        bingo = FM.bingo_point(_CruiseStub(fuel=0.6, autonomy=100_000.0), [leg], [base], reserve=0.1)
        distance = sum((p - b) ** 2 for p, b in zip(bingo.point, (*base, 0.0))) ** 0.5
        self.assertAlmostEqual(bingo.fuel - 0.1, distance / 100_000.0, delta=1e-12)

    def test_no_check_without_fuel_bases_or_legs(self):
        self.assertIsNone(FM.bingo_point(_CruiseStub(fuel=None), [EAST], [(0.0, 0.0)]))
        self.assertIsNone(FM.bingo_point(_CruiseStub(fuel=0.1), [EAST], []))
        self.assertIsNone(FM.bingo_point(_CruiseStub(fuel=0.1), [], [(0.0, 0.0)]))
        self.assertIsNone(FM.return_margin(_CruiseStub(fuel=0.1), [EAST], []))

    def test_nearest_base_tie_is_deterministic(self):
        distance, base = FM.nearest_base((0.0, 0.0, 0.0), [(0.0, 5_000.0), (0.0, -5_000.0)])
        self.assertEqual((distance, base), (5_000.0, (0.0, -5_000.0, 0.0)))
        self.assertIsNone(FM.nearest_base((0.0, 0.0, 0.0), []))



# ── F6-B2bis: bingo con rientro lungo la rotta a ritroso ──────────────────────

KM = 1_000.0
AUTONOMY_1000 = 1_000_000.0     # 1000 km: 0,001 del pieno = 1 km
DEPARTURE = FM.ReturnRule(departure=True)
LOOP = FM.ReturnRule(departure=True, loop=True)
IN_AIR = FM.ReturnRule(departure=False)


def _square(hold=0.0):
    """Anello di 120 km a 10 m/s (quadrato di lato 30 km che torna nel punto di partenza), con una sosta
    di `hold` secondi nel terzo vertice (0, 30 km) prima dell'ultimo lato."""
    corners = [(0.0, 0.0, 0.0), (30 * KM, 0.0, 0.0), (30 * KM, 30 * KM, 0.0), (0.0, 30 * KM, 0.0)]
    legs, t = [], 0.0

    for a, b in zip(corners, corners[1:]):
        legs.append(_Leg(t, t + 3_000.0, a, b))
        t += 3_000.0

    if hold > 0.0:
        legs.append(_Leg(t, t + hold, corners[-1], corners[-1]))
        t += hold

    legs.append(_Leg(t, t + 3_000.0, corners[-1], corners[0]))
    return legs


class TestReverseRouteBingo(_Base):
    """F6-B2bis: fabbisogno di bingo = `BINGO_RETURN_FACTOR` x il ritorno lungo la rotta a ritroso (soste
    escluse), con il tratto diretto alla base per la partenza in volo e la via piu' breve sull'anello.
    Crociera dello stub 10 m/s, autonomia 1000 km (i numeri si fanno a mano)."""

    def _stub(self, fuel):
        return _CruiseStub(fuel=fuel, autonomy=AUTONOMY_1000)

    def test_factor_is_a_declared_estimate_above_one(self):
        self.assertEqual(FM.BINGO_RETURN_FACTOR, 1.2)
        self.assertEqual(DEPARTURE.factor, FM.BINGO_RETURN_FACTOR)

        with self.assertRaises(ValueError):
            FM.ReturnRule(departure=True, factor=0.9)

        with self.assertRaises(ValueError):
            FM.ReturnRule(departure=False, loop=True)

    def test_reverse_route_skips_the_holds(self):
        """Partenza da una base in (0, 0): 10 km a est, sosta di 1000 s (10 km equivalenti), 20 km verso nord.
        Carburante 0,05 (50 km): prima della sosta H = 40 - 1,2 x 10 = 28, dopo 18; nel secondo tratto
        18 - 2,2 u = 0 -> u = 8,18 km. Il rientro torna al vertice (10 km, 0) senza ripetere la sosta e
        finisce sul DEPARTURE; al bingo il residuo e' esattamente 1,2 x il ritorno."""
        legs = [_Leg(0.0, 1_000.0, (0.0, 0.0, 0.0), (10 * KM, 0.0, 0.0)),
                _Leg(1_000.0, 2_000.0, (10 * KM, 0.0, 0.0), (10 * KM, 0.0, 0.0)),
                _Leg(2_000.0, 4_000.0, (10 * KM, 0.0, 0.0), (10 * KM, 20 * KM, 0.0))]
        asset = self._stub(0.05)
        bingo = FM.bingo_point(asset, legs, (), rule=DEPARTURE)
        u = 18 * KM / (1.0 + FM.BINGO_RETURN_FACTOR)
        self.assertEqual((bingo.leg_index, bingo.via), (2, FM.RETURN_REVERSE))
        self.assertAlmostEqual(bingo.point[1], u, delta=1e-6)
        self.assertAlmostEqual(bingo.time, 2_000.0 + u / 10.0, delta=1e-6)
        self.assertEqual(bingo.route[1:], ((10 * KM, 0.0, 0.0), (0.0, 0.0, 0.0)))
        self.assertEqual(bingo.base, (0.0, 0.0, 0.0))
        self.assertAlmostEqual(bingo.return_length, 10 * KM + u, delta=1e-6)
        self.assertAlmostEqual(bingo.fuel, FM.BINGO_RETURN_FACTOR * bingo.return_length / AUTONOMY_1000, delta=1e-12)
        self.assertEqual(asset.fuel, 0.05)

    def test_margin_is_the_minimum_and_matches_the_bingo(self):
        """Margine = minimo di residuo - 1,2 x ritorno: senza anello e' a fine tratti (H decresce); bingo se
        e solo se negativo."""
        leg = _Leg(0.0, 4_000.0, (0.0, 0.0, 0.0), (40 * KM, 0.0, 0.0))
        enough = 2.2 * 40 * KM / AUTONOMY_1000
        self.assertAlmostEqual(FM.return_margin(self._stub(enough), [leg], (), rule=DEPARTURE), 0.0, delta=1e-12)
        self.assertIsNone(FM.bingo_point(self._stub(enough + 1e-6), [leg], (), rule=DEPARTURE))
        self.assertIsNotNone(FM.bingo_point(self._stub(enough - 1e-6), [leg], (), rule=DEPARTURE))

    def test_loop_takes_the_reverse_when_it_is_shorter(self):
        """Anello di 120 km senza soste, carburante 0,12 (120 km): H minimo a meta' (120 - 60 - 1,2 x 60 < 0);
        il bingo e' a s = 120 / 2,2 = 54,5 km (secondo lato), dove il ritroso (54,5) e' piu' corto del
        resto (65,5): torna indietro per il primo vertice."""
        bingo = FM.bingo_point(self._stub(0.12), _square(), (), rule=LOOP)
        s = 120 * KM / (1.0 + FM.BINGO_RETURN_FACTOR)
        self.assertEqual((bingo.leg_index, bingo.via), (1, FM.RETURN_REVERSE))
        self.assertAlmostEqual(bingo.point[1], s - 30 * KM, delta=1e-6)
        self.assertEqual(bingo.route[1:], ((30 * KM, 0.0, 0.0), (0.0, 0.0, 0.0)))
        self.assertAlmostEqual(bingo.return_length, s, delta=1e-6)

    def test_loop_takes_the_rest_of_the_route_when_it_is_shorter(self):
        """Anello con una sosta di 3000 s (30 km equivalenti) nel terzo vertice, carburante 0,15 (150 km): mai
        bingo in movimento (minimo a meta' 150 - 60 - 72 = 18 km), ma nella sosta il resto della rotta (30 km)
        e' piu' corto del ritroso (90 km): all'inizio della sosta H = 60 - 36 = 24 km, zero dopo 2400 s.
        Rientro in avanti sull'ultimo lato, senza ripetere la sosta; la ritirata non varrebbe (H < 0 da subito)."""
        bingo = FM.bingo_point(self._stub(0.15), _square(hold=3_000.0), (), rule=LOOP)
        self.assertEqual((bingo.leg_index, bingo.via), (3, FM.RETURN_FORWARD))
        self.assertAlmostEqual(bingo.time, 9_000.0 + 2_400.0, delta=1e-6)
        self.assertEqual(bingo.route, ((0.0, 30 * KM, 0.0), (0.0, 0.0, 0.0)))
        self.assertAlmostEqual(bingo.fuel, FM.BINGO_RETURN_FACTOR * 30 * KM / AUTONOMY_1000, delta=1e-12)
        # Margine = il minimo, a fine sosta (24 - 30 = -6 km), non a fine tratti (dove il residuo e' 0).
        self.assertAlmostEqual(bingo.margin, -6 * KM / AUTONOMY_1000, delta=1e-12)
        # Senza l'anello la stessa rotta va in bingo molto prima (la ritirata costa 2,2 m per metro).
        self.assertLess(FM.bingo_point(self._stub(0.15), _square(hold=3_000.0), (), rule=DEPARTURE).time,
                        bingo.time)

    def test_a_loop_is_safe_with_about_1_1_times_its_route(self):
        """Anello di 120 km senza soste: nessun bingo con carburante appena sopra (1 + (f - 1) / 2) x 120 km,
        bingo appena sotto (1,1 x con f = 1,2)."""
        safe = (1.0 + (FM.BINGO_RETURN_FACTOR - 1.0) / 2.0) * 120 * KM / AUTONOMY_1000
        self.assertIsNone(FM.bingo_point(self._stub(safe + 1e-6), _square(), (), rule=LOOP))
        self.assertIsNotNone(FM.bingo_point(self._stub(safe - 1e-6), _square(), (), rule=LOOP))

    def test_air_start_returns_to_the_spawn_then_to_the_nearest_base(self):
        """Partenza in volo da (10 km, 0, 5000) verso est, basi in (0, 0) e (0, 50 km): la piu' vicina al punto
        di comparsa e' (0, 0); il rientro torna al punto di comparsa (in quota) e poi scende sulla base con
        il tratto diretto; fabbisogno 1,2 x (ritroso + diretto)."""
        leg = _Leg(0.0, 10_000.0, (10 * KM, 0.0, 5 * KM), (110 * KM, 0.0, 5 * KM))
        bases = [(0.0, 50 * KM), (0.0, 0.0)]
        direct = ((10 * KM) ** 2 + (5 * KM) ** 2) ** 0.5     # comparsa (in quota) -> base a quota 0
        bingo = FM.bingo_point(self._stub(0.1), [leg], bases, rule=IN_AIR)
        u = (100 * KM - FM.BINGO_RETURN_FACTOR * direct) / (1.0 + FM.BINGO_RETURN_FACTOR)
        self.assertAlmostEqual(bingo.point[0], 10 * KM + u, delta=1e-6)
        self.assertEqual(bingo.route[1:], ((10 * KM, 0.0, 5 * KM), (0.0, 0.0, 0.0)))
        self.assertAlmostEqual(bingo.return_length, u + direct, delta=1e-6)
        self.assertAlmostEqual(bingo.fuel, FM.BINGO_RETURN_FACTOR * (u + direct) / AUTONOMY_1000, delta=1e-12)

    def test_air_start_without_bases_has_no_check(self):
        """Partenza in volo senza basi: nessun controllo (None, valgono le regole della F6-A); partendo da una
        base le basi non servono."""
        self.assertIsNone(FM.bingo_point(self._stub(0.01), [EAST], (), rule=IN_AIR))
        self.assertIsNone(FM.return_margin(self._stub(0.01), [EAST], (), rule=IN_AIR))
        self.assertIsNotNone(FM.bingo_point(self._stub(0.01), [EAST], (), rule=DEPARTURE))

    def test_bingo_at_the_start_with_an_air_start(self):
        """Il solo tratto diretto alla base costa gia' piu' del residuo: bingo all'istante iniziale, rientro
        diretto dal punto di comparsa."""
        bingo = FM.bingo_point(self._stub(0.01), [EAST], [(0.0, -20 * KM)], rule=IN_AIR)
        self.assertEqual((bingo.time, bingo.point, bingo.leg_index), (0.0, (0.0, 0.0, 0.0), 0))
        self.assertEqual(bingo.route, ((0.0, 0.0, 0.0), (0.0, -20 * KM, 0.0)))

    def test_no_check_without_fuel_or_legs(self):
        self.assertIsNone(FM.bingo_point(_CruiseStub(fuel=None), [EAST], (), rule=DEPARTURE))
        self.assertIsNone(FM.bingo_point(self._stub(0.1), [], (), rule=DEPARTURE))

    def test_straight_rule_is_unchanged_without_a_rule(self):
        """`rule` None = la F6-B2: rientro diretto con la riserva, spezzata (punto, base)."""
        bingo = FM.bingo_point(_CruiseStub(fuel=0.5, autonomy=100_000.0), [EAST], [(0.0, 0.0)], reserve=0.1)
        self.assertEqual((bingo.via, bingo.route), (FM.RETURN_DIRECT, (bingo.point, bingo.base)))
        self.assertAlmostEqual(bingo.return_length, 20_000.0)


# ── RISERVA DI DISIMPEGNO (G1) ────────────────────────────────────────────────

_REAL_MODEL = "F-14A Tomcat"
_NO_TANKS = "Phoenix Fleet Defense"      # nessun serbatoio esterno
_WITH_TANKS = "Sparrow CAP/Escort"       # 2 serbatoi esterni


class _MaxSpeedStub(_FuelStub):
    """Stub senza consumo militare ne' capacita': solo autonomia e profilo di velocita'."""

    def __init__(self, max_speed=500.0, **kwargs):
        super().__init__(**kwargs)
        self.speed = {'nominal': 200.0, 'max': max_speed}


class TestDisengagementReserve(_Base):
    """`disengagement_reserve`: consumo alla massima spinta militare x DISENGAGE_TIME / capacita' del loadout,
    con aerei REALI del registro (F-14A) e un loadout assegnato; ripiego sul regime 'max'; None."""

    def setUp(self):
        super().setUp()
        more = [patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score', return_value=0.5),
                patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.logger', MagicMock()),
                patch('Code.Dynamic_War_Manager.Source.Asset.Asset.logger', MagicMock())]
        for p in more:
            p.start()
        self._patches.extend(more)

    @staticmethod
    def _aircraft(loadout=_NO_TANKS, model=_REAL_MODEL):
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
        from Code.Dynamic_War_Manager.Source.Block.Block import Block
        from Code.Dynamic_War_Manager.Source.Context.Context import Air_Asset_Type

        block = MagicMock(spec=Block)
        block.block_class = "Military"
        aircraft = Aircraft(block=block, asset_type=Air_Asset_Type.FIGHTER, model=model)
        aircraft.assigned_loadout = loadout
        return aircraft

    def test_disengage_time_is_five_minutes(self):
        self.assertEqual(FM.DISENGAGE_TIME, 300.0)

    def test_reserve_from_the_military_flow_of_a_real_aircraft(self):
        """La formula sui dati dell'asset: flusso [kg/h] x 300 s / 3600 / capacita' [kg], provenienza dichiarata,
        frazione fra 0 e il pieno; indipendente dal carburante attuale."""
        aircraft = self._aircraft()
        reserve, source = FM.disengagement_reserve_with_source(aircraft)
        expected = aircraft.emergency_fuel_flow() * FM.DISENGAGE_TIME / 3600.0 / aircraft.fuel_capacity_kg()
        self.assertEqual(source, FM.RESERVE_FROM_MILITARY_FLOW)
        self.assertAlmostEqual(reserve, expected, delta=1e-12)
        self.assertTrue(0.0 < reserve < 1.0)

        aircraft.consume_fuel(0.5)
        self.assertAlmostEqual(FM.disengagement_reserve(aircraft), expected, delta=1e-12)

    def test_reserve_is_proportional_to_the_duration(self):
        aircraft = self._aircraft()
        self.assertAlmostEqual(FM.disengagement_reserve(aircraft, 2 * FM.DISENGAGE_TIME),
                               2 * FM.disengagement_reserve(aircraft), delta=1e-12)

    def test_drop_tanks_lower_the_reserve_fraction(self):
        """Stesso flusso, carico pieno piu' grande (serbatoi esterni): frazione minore."""
        self.assertLess(FM.disengagement_reserve(self._aircraft(_WITH_TANKS)),
                        FM.disengagement_reserve(self._aircraft(_NO_TANKS)))

    def test_every_model_with_a_loadout_has_a_reserve_below_a_full_load(self):
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS

        for model, loadouts in AIRCRAFT_LOADOUTS.items():
            result = FM.disengagement_reserve_with_source(self._aircraft(next(iter(loadouts)), model))
            self.assertIsNotNone(result, model)
            self.assertEqual(result[1], FM.RESERVE_FROM_MILITARY_FLOW, model)
            self.assertTrue(0.0 < result[0] < 1.0, model)

    def test_fallback_on_the_max_regime_without_military_flow(self):
        """Senza consumo militare (o senza capacita'): il carburante per `velocita' massima x DISENGAGE_TIME` al
        regime 'max' del loadout, con la provenienza del ripiego."""
        aircraft = self._aircraft()
        with patch.object(type(aircraft), 'emergency_fuel_flow', return_value=None):
            reserve, source = FM.disengagement_reserve_with_source(aircraft)
        self.assertEqual(source, FM.RESERVE_FROM_MAX_REGIME)
        self.assertAlmostEqual(reserve, aircraft.fuel_for_distance(aircraft.speed['max'] * FM.DISENGAGE_TIME, 'max'),
                               delta=1e-12)

        stub = _MaxSpeedStub(max_speed=500.0, autonomy=1_000_000.0)
        self.assertEqual(FM.disengagement_reserve_with_source(stub),
                         (500.0 * FM.DISENGAGE_TIME / 1_000_000.0, FM.RESERVE_FROM_MAX_REGIME))

    def test_not_modelled_is_none(self):
        """Nessun dato: aereo senza loadout (ne' capacita' ne' autonomia), stub senza velocita' massima o
        senza autonomia."""
        self.assertIsNone(FM.disengagement_reserve(self._aircraft(loadout=None)))
        self.assertIsNone(FM.disengagement_reserve(_FuelStub()))
        self.assertIsNone(FM.disengagement_reserve(_MaxSpeedStub(autonomy=None)))
        self.assertIsNone(FM.disengagement_reserve(object()))


# ── CONSUMO IN INGAGGIO (G3) ──────────────────────────────────────────────────

class TestEngagementFuel(TestDisengagementReserve):
    """`engagement_fuel` (G3) = la riserva di disimpegno del G1 (stessa fonte, stesso ripiego) e
    `build_engagement_fuel_event`: evento istantaneo limitato al disponibile. Eredita i test della riserva
    (setUp e aereo reale): rieseguirli qui non costa nulla e conferma che le due grandezze non divergono."""

    def test_engagement_fuel_is_the_disengagement_reserve(self):
        aircraft = self._aircraft()
        self.assertEqual(FM.engagement_fuel_with_source(aircraft), FM.disengagement_reserve_with_source(aircraft))
        self.assertEqual(FM.engagement_fuel_with_source(aircraft)[1], FM.RESERVE_FROM_MILITARY_FLOW)
        stub = _MaxSpeedStub(max_speed=500.0, autonomy=1_000_000.0)
        self.assertEqual(FM.engagement_fuel_with_source(stub), (0.15, FM.RESERVE_FROM_MAX_REGIME))
        self.assertAlmostEqual(FM.engagement_fuel(stub), 0.15)
        self.assertIsNone(FM.engagement_fuel(_FuelStub()))

    def test_event_is_instantaneous_and_not_applied(self):
        stub = _MaxSpeedStub(max_speed=500.0, autonomy=1_000_000.0, fuel=0.8)
        event = FM.build_engagement_fuel_event(stub, 123.0)
        self.assertEqual((event.time, event.t_start, event.asset_id, event.distance, event.distance_covered,
                          event.duration, event.duration_covered, event.stationary, event.regime, event.provenance),
                         (123.0, 123.0, 'a1', 0.0, 0.0, 0.0, 0.0, False, FM.ENGAGEMENT_REGIME, DM.DERIVED))
        self.assertAlmostEqual(event.amount, 0.15)
        self.assertAlmostEqual(event.fuel_after, 0.65)
        self.assertFalse(event.exhausted)
        self.assertEqual(stub.fuel, 0.8)
        FM.apply_fuel_event(stub, event)
        self.assertAlmostEqual(stub.fuel, 0.65)

    def test_event_on_a_real_aircraft(self):
        aircraft = self._aircraft()
        event = FM.build_engagement_fuel_event(aircraft, 10.0, provenance=DM.ESTIMATED)
        self.assertAlmostEqual(event.amount, FM.disengagement_reserve(aircraft), delta=1e-12)
        self.assertEqual(event.provenance, DM.ESTIMATED)

    def test_insufficient_fuel_is_clamped_and_exhausts(self):
        stub = _MaxSpeedStub(max_speed=500.0, autonomy=1_000_000.0, fuel=0.1)
        event = FM.build_engagement_fuel_event(stub, 0.0)
        self.assertEqual((event.amount, event.fuel_after, event.exhausted), (0.1, 0.0, True))

    def test_no_event(self):
        """Serbatoio vuoto, carburante o consumo non modellati, asset senza id: nessun evento."""
        self.assertIsNone(FM.build_engagement_fuel_event(_MaxSpeedStub(fuel=0.0), 0.0))
        self.assertIsNone(FM.build_engagement_fuel_event(_FuelStub(), 0.0))
        self.assertIsNone(FM.build_engagement_fuel_event(_MaxSpeedStub(fuel=None), 0.0))
        anonymous = _MaxSpeedStub()
        anonymous.id = None
        self.assertIsNone(FM.build_engagement_fuel_event(anonymous, 0.0))

    def test_arguments_out_of_domain_raise(self):
        with self.assertRaises(ValueError):
            FM.build_engagement_fuel_event(_MaxSpeedStub(), 0.0, provenance='guess')
        with self.assertRaises(TypeError):
            FM.build_engagement_fuel_event(_MaxSpeedStub(), '0')


# ── SOGLIA DI BINGO E ALBERO DI DECISIONE (G2) ────────────────────────────────

# Rotta a L da una base: 100 km verso est, poi 100 km verso nord (10 m/s: 10000 s per lato).
NORTH = _Leg(10_000.0, 20_000.0, (100 * KM, 0.0, 0.0), (100 * KM, 100 * KM, 0.0))
RESERVE = 0.01    # riserva di disimpegno imposta nei test: 10 km di crociera (autonomia 1000 km)


class TestBingoDecision(_Base):
    """`bingo_decision` in posizioni e con residui ARBITRARI (G2): soglia = resto della rotta + riserva,
    albero del trasferimento e del combattimento, raggiungibilita' senza riserva. Stub con crociera 10 m/s e
    autonomia 1000 km (0,001 del pieno = 1 km), riserva imposta `RESERVE` salvo dove si verifica il default."""

    @staticmethod
    def _stub(fuel):
        return _CruiseStub(fuel=fuel, autonomy=AUTONOMY_1000)

    def _decide(self, fuel, legs, bases=(), rule=DEPARTURE, transfer=False, time=None, reserve=RESERVE):
        return FM.bingo_decision(self._stub(fuel), legs, bases, rule, transfer=transfer, time=time, reserve=reserve)

    # -- soglia --

    def test_remaining_route_demand_and_threshold(self):
        """Resto della rotta dal punto (frazione rimanente del tratto in corso + tratti successivi, soste nel
        tempo alla crociera) e soglia = resto + riserva; default della riserva = `disengagement_reserve`."""
        stub = self._stub(1.0)
        self.assertAlmostEqual(FM.remaining_route_demand(stub, [EAST, NORTH]), 0.2, delta=1e-12)
        self.assertAlmostEqual(FM.remaining_route_demand(stub, [EAST, NORTH], time=2_500.0), 0.175, delta=1e-12)
        self.assertAlmostEqual(FM.remaining_route_demand(stub, [EAST, NORTH], time=25_000.0), 0.0, delta=1e-12)
        hold = _Leg(10_000.0, 11_000.0, (100 * KM, 0.0, 0.0), (100 * KM, 0.0, 0.0))     # 10 km equivalenti
        self.assertAlmostEqual(FM.remaining_route_demand(stub, [EAST, hold], time=10_500.0), 0.005, delta=1e-12)
        self.assertAlmostEqual(FM.bingo_threshold(stub, [EAST], reserve=RESERVE), 0.11, delta=1e-12)
        self.assertAlmostEqual(FM.bingo_threshold(stub, [EAST]), 0.1 + FM.disengagement_reserve(stub), delta=1e-12)
        self.assertIsNone(FM.bingo_threshold(_FuelStub(), [EAST]))     # riserva non modellata
        self.assertIsNone(FM.remaining_route_demand(stub, []))

    def test_threshold_is_strict(self):
        """Bingo se e solo se residuo < soglia, in un punto qualunque (qui a 30 km, resto 0,17 + riserva 0,01)."""
        legs = [EAST, NORTH]
        self.assertIsNone(self._decide(0.18 + 1e-6, legs, time=3_000.0))
        self.assertIsNone(self._decide(0.18, legs, time=3_000.0))
        decision = self._decide(0.18 - 1e-6, legs, time=3_000.0)
        self.assertEqual((decision.time, decision.point, decision.leg_index), (3_000.0, (30 * KM, 0.0, 0.0), 0))
        self.assertAlmostEqual(decision.rest, 0.17, delta=1e-12)
        self.assertAlmostEqual(decision.threshold, 0.18, delta=1e-12)

    def test_default_position_and_fuel_are_the_start_and_the_asset(self):
        stub = self._stub(0.05)
        decision = FM.bingo_decision(stub, [EAST], (), DEPARTURE, reserve=RESERVE)
        self.assertEqual((decision.time, decision.point, decision.fuel), (0.0, (0.0, 0.0, 0.0), 0.05))
        self.assertEqual(stub.fuel, 0.05)

    def test_no_check(self):
        """Carburante o riserva non modellati, nessun tratto: None."""
        self.assertIsNone(FM.bingo_decision(_CruiseStub(fuel=None), [EAST], (), DEPARTURE))
        self.assertIsNone(FM.bingo_decision(_FuelStub(fuel=0.01), [EAST], (), DEPARTURE))
        self.assertIsNone(self._decide(0.01, []))

    # -- trasferimento --

    def test_transfer_continues_when_the_rest_of_the_route_is_covered(self):
        """Residuo fra il resto della rotta e la soglia: CONTINUA, nessun rientro (consuma la riserva)."""
        decision = self._decide(0.105, [EAST], transfer=True)
        self.assertEqual((decision.action, decision.route, decision.base, decision.returns),
                         (FM.BINGO_CONTINUE, (), None, False))

    def test_transfer_returns_along_the_route_to_the_departure(self):
        """A 30 km, residuo 0,05 < resto 0,17: ritroso fino al DEPARTURE (30 km, raggiungibile)."""
        decision = self._decide(0.05, [EAST, NORTH], transfer=True, time=3_000.0)
        self.assertEqual((decision.action, decision.via), (FM.BINGO_DEPARTURE, FM.RETURN_REVERSE))
        self.assertEqual(decision.route, ((30 * KM, 0.0, 0.0), (0.0, 0.0, 0.0)))
        self.assertAlmostEqual(decision.return_length, 30 * KM, delta=1e-6)

    def test_transfer_at_the_start_from_a_base_stays_on_the_departure(self):
        """All'inizio dei tratti il ritroso ha lunghezza zero: atterraggio sul DEPARTURE, nessun movimento."""
        decision = self._decide(0.05, [EAST], transfer=True)
        self.assertEqual((decision.action, decision.base, decision.return_length), (FM.BINGO_DEPARTURE,
                                                                                    (0.0, 0.0, 0.0), 0.0))

    def test_transfer_from_the_air_goes_to_the_base_nearest_to_the_spawn(self):
        """Partenza in volo: ritroso fino al punto di comparsa, poi diretto alla base del lato piu' vicina."""
        spawn = _Leg(0.0, 10_000.0, (0.0, 0.0, 3 * KM), (100 * KM, 0.0, 3 * KM))
        decision = self._decide(0.05, [spawn], bases=[(0.0, -4 * KM), (0.0, 50 * KM)], rule=IN_AIR, transfer=True,
                                time=1_000.0)
        self.assertEqual(decision.route, ((10 * KM, 0.0, 3 * KM), (0.0, 0.0, 3 * KM), (0.0, -4 * KM, 0.0)))
        self.assertEqual(decision.via, FM.RETURN_REVERSE)

    def test_transfer_then_the_nearest_base_in_a_straight_line(self):
        """A (100 km, 30 km) sulla L il ritroso (130 km) non e' raggiungibile con 0,02: la base piu' vicina in
        linea retta (2 km a est della rotta), raggiungibile. Il trasferimento non usa le basi alternative."""
        decision = self._decide(0.02, [EAST, NORTH], bases=[(102 * KM, 30 * KM)], transfer=True, time=13_000.0)
        self.assertEqual((decision.action, decision.via), (FM.BINGO_NEAREST, FM.RETURN_DIRECT))
        self.assertEqual(decision.route, ((100 * KM, 30 * KM, 0.0), (102 * KM, 30 * KM, 0.0)))
        self.assertTrue(decision.reachable)

    def test_transfer_without_a_reachable_base_heads_for_the_nearest(self):
        """Nessuna base raggiungibile: verso la piu' vicina comunque (UNREACHABLE, le regole della F6-A)."""
        decision = self._decide(0.001, [EAST, NORTH], bases=[(110 * KM, 30 * KM), (120 * KM, 30 * KM)], transfer=True,
                                time=13_000.0)
        self.assertEqual((decision.action, decision.reachable), (FM.BINGO_UNREACHABLE, False))
        self.assertEqual(decision.base, (110 * KM, 30 * KM, 0.0))

    # -- combattimento --

    def test_combat_never_continues(self):
        """Lo stesso residuo che fa continuare un trasferimento interrompe il combattimento (qui alla partenza:
        resta sul DEPARTURE)."""
        decision = self._decide(0.105, [EAST])
        self.assertEqual((decision.action, decision.return_length), (FM.BINGO_DEPARTURE, 0.0))

    def test_combat_alternate_base_ahead(self):
        """A 30 km verso est, base a 2 km dalla rotta in (40 km, 2 km): in avanti fino a (40 km, 0) e poi
        diretta, 12 km, piu' corta del ritroso (30 km)."""
        decision = self._decide(0.05, [EAST, NORTH], bases=[(40 * KM, 2 * KM)], time=3_000.0)
        self.assertEqual((decision.action, decision.via), (FM.BINGO_ALTERNATE, FM.RETURN_ALONG))
        self.assertEqual(decision.route, ((30 * KM, 0.0, 0.0), (40 * KM, 0.0, 0.0), (40 * KM, 2 * KM, 0.0)))
        self.assertAlmostEqual(decision.return_length, 12 * KM, delta=1e-6)

    def test_combat_alternate_base_behind(self):
        """A (100 km, 50 km) sulla L, base a 2 km dalla rotta in (70 km, -2 km): a ritroso per il vertice
        (100 km, 0) fino a (70 km, 0), poi diretta (82 km), piu' corta del ritroso al DEPARTURE (150 km). Riserva
        0,1 perche' 0,1 di residuo sia sotto la soglia (resto 0,05)."""
        decision = self._decide(0.1, [EAST, NORTH], bases=[(70 * KM, -2 * KM)], time=15_000.0, reserve=0.1)
        self.assertEqual(decision.action, FM.BINGO_ALTERNATE)
        self.assertEqual(decision.route, ((100 * KM, 50 * KM, 0.0), (100 * KM, 0.0, 0.0), (70 * KM, 0.0, 0.0),
                                          (70 * KM, -2 * KM, 0.0)))
        self.assertAlmostEqual(decision.return_length, 82 * KM, delta=1e-6)

    def test_combat_alternate_descends_to_the_base(self):
        """In quota la base alternativa si raggiunge con un tratto diretto che scende a quota 0."""
        high = _Leg(0.0, 10_000.0, (0.0, 0.0, 3 * KM), (100 * KM, 0.0, 3 * KM))
        decision = self._decide(0.05, [high], bases=[(40 * KM, 2 * KM)], time=3_000.0)
        self.assertEqual(decision.route[-2:], ((40 * KM, 0.0, 3 * KM), (40 * KM, 2 * KM, 0.0)))

    def test_alternate_offset_limit(self):
        """Base a 3,0 km dalla rotta: alternativa; a 3,1 km: esclusa (ritroso al DEPARTURE)."""
        self.assertEqual(FM.ALTERNATE_BASE_MAX_OFFSET, 3_000.0)
        inside = self._decide(0.05, [EAST], bases=[(40 * KM, 3.0 * KM)], time=3_000.0)
        outside = self._decide(0.05, [EAST], bases=[(40 * KM, 3.1 * KM)], time=3_000.0)
        self.assertEqual(inside.action, FM.BINGO_ALTERNATE)
        self.assertEqual((outside.action, outside.base), (FM.BINGO_DEPARTURE, (0.0, 0.0, 0.0)))

    def test_ties_prefer_the_departure_then_x_y(self):
        """A 30 km: una base SULLA rotta a 60 km (30 km, come il ritroso) perde con la base di partenza; a 50 km
        due alternative alla stessa distanza (11 km) vince quella con (x, y) minore."""
        tie = self._decide(0.05, [EAST], bases=[(60 * KM, 0.0)], time=3_000.0)
        self.assertEqual((tie.action, tie.base), (FM.BINGO_DEPARTURE, (0.0, 0.0, 0.0)))
        pair = self._decide(0.05, [EAST], bases=[(60 * KM, KM), (40 * KM, KM)], time=5_000.0)
        self.assertEqual((pair.action, pair.base), (FM.BINGO_ALTERNATE, (40 * KM, KM, 0.0)))

    def test_combat_loop_takes_the_rest_of_the_route_when_shorter(self):
        """Anello (quadrato di 120 km): a 100 km il resto della rotta (20 km) e' piu' corto del ritroso; residuo
        0,025 sotto la soglia 0,03."""
        decision = self._decide(0.025, _square(), rule=LOOP, time=10_000.0)
        self.assertEqual((decision.action, decision.via), (FM.BINGO_DEPARTURE, FM.RETURN_FORWARD))
        self.assertAlmostEqual(decision.return_length, 20 * KM, delta=1e-6)

    def test_reachability_needs_no_reserve(self):
        """A 30 km il ritroso costa 0,03: con 0,03 e' raggiungibile (la riserva si consuma nel rientro); appena
        sotto no, e senza altre basi l'aereo punta comunque alla piu' vicina in linea retta, qui il DEPARTURE."""
        exact = self._decide(0.03, [EAST], time=3_000.0)
        self.assertEqual((exact.action, exact.reachable), (FM.BINGO_DEPARTURE, True))
        short = self._decide(0.03 - 1e-6, [EAST], time=3_000.0)
        self.assertEqual((short.action, short.base), (FM.BINGO_UNREACHABLE, (0.0, 0.0, 0.0)))

    def test_combat_without_a_reachable_candidate_takes_the_nearest_reachable_base(self):
        """A 50 km con 0,03: ritroso (50 km) irraggiungibile, nessuna alternativa entro 3 km; la base a 20 km
        dalla rotta e' raggiungibile in linea retta."""
        decision = self._decide(0.03, [EAST], bases=[(50 * KM, 20 * KM)], time=5_000.0)
        self.assertEqual((decision.action, decision.base), (FM.BINGO_NEAREST, (50 * KM, 20 * KM, 0.0)))

    def test_no_base_at_all(self):
        """Partenza in volo senza basi: nessun rientro possibile (NO_BASE, regole della F6-A); un trasferimento
        che puo' concludere continua comunque."""
        self.assertEqual(self._decide(0.05, [EAST], rule=IN_AIR).action, FM.BINGO_NO_BASE)
        self.assertEqual(self._decide(0.105, [EAST], rule=IN_AIR, transfer=True).action, FM.BINGO_CONTINUE)


if __name__ == '__main__':
    unittest.main()
