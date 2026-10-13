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


if __name__ == '__main__':
    unittest.main()
