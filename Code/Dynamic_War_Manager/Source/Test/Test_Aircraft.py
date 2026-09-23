import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from sympy import Point3D
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Area import Area
from Code.Dynamic_War_Manager.Source.Context.Context import (
    SHAPE2D,
    SHAPE3D,
    AIR_COMBAT_EFFICACY,
    ACTION_TASKS,
    Air_Asset_Type,
)
from sympy import Point2D


class TestAircraft(unittest.TestCase):
    """Test suite for Aircraft class"""

    def setUp(self):
        self.mock_block = MagicMock(spec=Block)
        self.mock_block.is_military.return_value = True
        self.mock_block.is_logistic.return_value = False
        self.mock_block.is_civilian.return_value = False
        self.mock_block.block_class = "Military"
        self.mock_block.get_asset.return_value = None

        self.test_acp = Payload(goods=100, energy=50, hr=10, hc=5, hs=2, hb=1)
        self.test_rcp = Payload(goods=20, energy=10, hr=2, hc=1, hs=0, hb=0)
        self.test_payload = Payload(goods=200, energy=100, hr=20, hc=10, hs=5, hb=2)

        area = Area(shape=SHAPE2D.CIRCLE, radius=4.0, center=Point2D(0, 0))
        self.test_volume = Volume(area_base=area, volume_shape=SHAPE3D.CYLINDER)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    def test_initialization(self, mock_get_aircraft_combat_score):
        """Test Aircraft initialization with all parameters"""
        mock_get_aircraft_combat_score.return_value = 0.5

        aircraft = Aircraft(
            block=self.mock_block,
            name="Test Fighter",
            model="F-15C Eagle",
            description="Test Description",
            category="Fighter",
            asset_type=Air_Asset_Type.FIGHTER,
            functionality="Combat",
            cost=1000,
            value=10,
            acp=self.test_acp,
            rcp=self.test_rcp,
            payload=self.test_payload,
            position=Point3D(100, 200, 0),
            volume=self.test_volume,
            crytical=True,
            repair_time=48,
            role="Air Superiority"
        )

        self.assertEqual(aircraft.name, "Test Fighter")
        self.assertEqual(aircraft._model, "F-15C Eagle")
        self.assertEqual(aircraft.model, "F-15C Eagle")  # base Asset.model property
        self.assertEqual(aircraft.category, "Fighter")
        self.assertEqual(aircraft.asset_type, Air_Asset_Type.FIGHTER.value)
        self.assertTrue(aircraft.crytical)
        self.assertEqual(aircraft.repair_time, 48)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    @patch.object(Aircraft, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_set_combat_power_replicates_same_value_across_all_tasks(self, mock_efficiency, mock_get_aircraft_combat_score):
        """set_combat_power populates every air task with the SAME aggregate value (not per-task)."""
        mock_get_aircraft_combat_score.return_value = 0.5

        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model="F-15C Eagle")

        combat_power_result = aircraft.combat_power(force='air')
        self.assertIsInstance(combat_power_result, dict)
        self.assertEqual(set(combat_power_result.keys()), set(ACTION_TASKS['air']))
        values = set(combat_power_result.values())
        self.assertEqual(len(values), 1)  # all tasks carry the same value
        self.assertGreater(values.pop(), 0.0)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    @patch.object(Aircraft, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_air_combat_power_matches_shared_formula(self, mock_efficiency, mock_get_aircraft_combat_score):
        """air_combat_power() matches Context.combat_power_from_score() applied to AIR_COMBAT_EFFICACY."""
        mock_get_aircraft_combat_score.return_value = 0.5

        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model="F-15C Eagle")

        expected = (1 + AIR_COMBAT_EFFICACY['Fighter'] * 0.3 / 5) * (1 + 0.5) * 0.8
        self.assertAlmostEqual(aircraft.air_combat_power(), expected)
        self.assertAlmostEqual(aircraft.combat_power(force='air', action='CAP'), expected)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    @patch.object(Aircraft, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_fighter_outranks_transport_at_equal_score(self, mock_efficiency, mock_get_aircraft_combat_score):
        """A Fighter has higher combat power than a Transport with the identical model score."""
        mock_get_aircraft_combat_score.return_value = 0.5

        fighter = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model="F-15C Eagle")
        transport = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.TRANSPORT, model="C-17A")

        self.assertGreater(fighter.air_combat_power(), transport.air_combat_power())

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    @patch.object(Aircraft, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_unknown_category_returns_zero(self, mock_efficiency, mock_get_aircraft_combat_score):
        """A category absent from AIR_COMBAT_EFFICACY gets combat power 0."""
        mock_get_aircraft_combat_score.return_value = 0.5

        aircraft = Aircraft(block=self.mock_block, asset_type="Not_A_Real_Role", model="F-15C Eagle")
        self.assertEqual(aircraft.air_combat_power(), 0.0)

    def test_no_model_returns_zero_combat_power(self):
        """Without a model, air_combat_power is 0.0 (no crash, no registry lookup)."""
        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER)
        self.assertIsNone(aircraft._model)
        self.assertEqual(aircraft.air_combat_power(), 0.0)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    def test_set_combat_power_invalid_action_raises(self, mock_get_aircraft_combat_score):
        mock_get_aircraft_combat_score.return_value = 0.5
        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model="F-15C Eagle")

        with self.assertRaises(TypeError):
            aircraft.set_combat_power(actions=["CAP", "invalid_action"])

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    def test_property_isFighter(self, mock_get_aircraft_combat_score):
        mock_get_aircraft_combat_score.return_value = 0.5
        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model="F-15C Eagle")
        self.assertTrue(aircraft.isFighter)

        transport = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.TRANSPORT, model="C-17A")
        self.assertFalse(transport.isFighter)
        self.assertTrue(transport.isTransport)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_physical_characteristics')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score')
    def test_get_physical_characteristics_returns_data(self, mock_get_combat_score, mock_get_pc):
        """get_physical_characteristics (Fase 3-bis) delegates to Aircraft_Data's registry."""
        mock_get_combat_score.return_value = 0.5
        mock_get_pc.return_value = {'length': 15, 'width': 9, 'height': 5, 'weight': 7690}

        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model="F-16A Fighting Falcon")

        self.assertEqual(aircraft.get_physical_characteristics(), {'length': 15, 'width': 9, 'height': 5, 'weight': 7690})
        mock_get_pc.assert_called_once_with(model="F-16A Fighting Falcon")

    def test_get_physical_characteristics_no_model_returns_none(self):
        """get_physical_characteristics returns None when no model is set (mirror of Ship's equivalent test)."""
        aircraft = Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER)
        self.assertIsNone(aircraft.get_physical_characteristics())


class TestAircraftLoadoutAmmunition(unittest.TestCase):
    """Scorta di un aereo derivata dal loadout ASSEGNATO (decisione utente 2026-09-23).

    Dati reali di Aircraft_Loadouts (F-14A Tomcat):
      * "Phoenix Fleet Defense": 4 AIM-54A + 2 AIM-9L + 2 AIM-7M (8) + 675 colpi = 683;
      * "Sparrow CAP/Escort": 4 AIM-7M + 2 AIM-9L (6) + 2 serbatoi 267gal (esclusi) + 675 = 681;
      * un loadout con pod LANTIRN in `devices` (escluso).
    """

    MODEL = "F-14A Tomcat"

    def setUp(self):
        self.mock_block = MagicMock(spec=Block)
        self.mock_block.block_class = "Military"
        self._patches = [patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score',
                               return_value=0.5),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Mobile.logger'),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Asset.logger')]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()

    def _aircraft(self, model=MODEL):
        return Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model=model)

    def test_without_loadout_ammunition_is_not_modelled(self):
        aircraft = self._aircraft()
        self.assertIsNone(aircraft.assigned_loadout)
        self.assertIsNone(aircraft.ammunition)
        self.assertIsNone(aircraft.ammunition_from_registry())

    def test_missiles_and_gun_rounds_are_summed(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        self.assertEqual(aircraft.ammunition_from_registry(), 8 + 675)
        self.assertEqual(aircraft.ammunition, 8 + 675)

    def test_fuel_tanks_on_pylons_are_excluded(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Sparrow CAP/Escort"
        self.assertEqual(aircraft.ammunition, 6 + 675)

    def test_devices_are_excluded(self):
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import get_weapon

        model, name, loadout = next((m, n, l) for m, loadouts in AIRCRAFT_LOADOUTS.items()
                                    for n, l in loadouts.items() if l['stores']['devices'])
        stores = loadout['stores']
        expected = sum(q for w, q, *_ in stores['pylons'].values() if get_weapon(w) is not None)
        expected += stores['gun_rounds']

        aircraft = self._aircraft(model=model)
        aircraft.assigned_loadout = name
        self.assertEqual(aircraft.ammunition, expected)

    def test_unknown_loadout_raises(self):
        aircraft = self._aircraft()
        with self.assertRaises(ValueError):
            aircraft.assigned_loadout = "Nonexistent loadout"
        with self.assertRaises(TypeError):
            aircraft.assigned_loadout = 3
        self.assertIsNone(aircraft.assigned_loadout)

    def test_model_without_loadouts_raises(self):
        aircraft = self._aircraft(model=None)
        with self.assertRaises(ValueError):
            aircraft.assigned_loadout = "Phoenix Fleet Defense"

    def test_reassignment_rearms_and_none_unmodels(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        aircraft.consume_ammunition(100)
        self.assertEqual(aircraft.ammunition, 583)

        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        self.assertEqual(aircraft.ammunition, 683)

        aircraft.assigned_loadout = None
        self.assertIsNone(aircraft.ammunition)

    def test_loadout_stock_flows_into_the_engagement_resolver(self):
        """Lo stato ombra di resolve_engagement legge la scorta derivata dal loadout."""
        import random
        from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
        from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import ContactWindow
        from Code.Dynamic_War_Manager.Source.Context.Reaction_Profile import ReactionProfile

        class _Target:
            id = 'r1'
            health = 100

        class _Force:
            def __init__(self, name, side, assets):
                self.name, self.side = name, side
                self.assets = {a.id: a for a in assets}

        aircraft = self._aircraft()
        aircraft.id = 'b1'
        aircraft.assigned_loadout = "Phoenix Fleet Defense"

        window = ContactWindow('b1', 'r1', t_start=0.0, t_end=100.0, t_cpa=50.0, distance_cpa=0.0,
                               range_a=1000.0, range_b=None)
        profile = ReactionProfile(detection=1.0, evaluation=1.0, command=0.0, actuation=0.0)
        run = ER._EngagementRun((_Force('blue', 'Blue', [aircraft]), _Force('red', 'Red', [_Target()])),
                                [window], lambda s, t: None, random.Random(0), None, None, None,
                                lambda asset: profile, None, 0.0, ER.DM.DERIVED)

        self.assertEqual(run.shadows['b1'].ammunition, 683)

        spec = ER.ShotSpec(accuracy=0.0, destroy_capacity=1.0, rounds=700)
        result = ER.resolve_engagement(_Force('blue', 'Blue', [aircraft]), _Force('red', 'Red', [_Target()]),
                                       [window], lambda s, t: spec, random.Random(0),
                                       reaction_profile_for=lambda asset: profile)
        self.assertEqual(result.salvos[0].rounds, 683)


class TestAircraftLoadoutFuel(unittest.TestCase):
    """Carburante di un aereo dal loadout ASSEGNATO (Fase 5), stessa regola delle munizioni.

    Dati reali di Aircraft_Loadouts (F-14A Tomcat):
      * "Phoenix Fleet Defense": raggio cruise 850 km, attack 650 km, nessun serbatoio,
        fuel_internal_max 7348 kg;
      * "Sparrow CAP/Escort": raggio cruise 1135 km, attack 860 km, 2 serbatoi 267gal da 900 kg.
    Autonomia = AIRCRAFT_RADIUS_TO_DISTANCE_FACTOR (2) x raggio.
    """

    MODEL = "F-14A Tomcat"

    def setUp(self):
        self.mock_block = MagicMock(spec=Block)
        self.mock_block.block_class = "Military"
        self._patches = [patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score',
                               return_value=0.5),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.logger'),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Mobile.logger'),
                         patch('Code.Dynamic_War_Manager.Source.Asset.Asset.logger')]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()

    def _aircraft(self, model=MODEL):
        return Aircraft(block=self.mock_block, asset_type=Air_Asset_Type.FIGHTER, model=model)

    def test_without_loadout_fuel_is_not_modelled(self):
        aircraft = self._aircraft()
        self.assertIsNone(aircraft.fuel)
        self.assertIsNone(aircraft.fuel_autonomy())
        self.assertIsNone(aircraft.fuel_capacity_kg())
        self.assertIsNone(aircraft.fuel_for_distance(1000.0))

    def test_assignment_fills_the_tank(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        self.assertEqual(aircraft.fuel, 1.0)

    def test_autonomy_is_twice_the_radius_per_regime(self):
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft import AIRCRAFT_RADIUS_TO_DISTANCE_FACTOR

        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Sparrow CAP/Escort"
        self.assertEqual(AIRCRAFT_RADIUS_TO_DISTANCE_FACTOR, 2.0)
        self.assertAlmostEqual(aircraft.fuel_autonomy('nominal'), 2 * 1135 * 1000.0)
        self.assertAlmostEqual(aircraft.fuel_autonomy('max'), 2 * 860 * 1000.0)

    def test_known_leg_known_consumption(self):
        """850 km di raggio cruise -> 1700 km col pieno: 425 km consumano un quarto."""
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        self.assertAlmostEqual(aircraft.fuel_for_distance(425_000.0), 0.25)
        # Al regime di attacco (raggio 650 km) la stessa tratta costa di piu'.
        self.assertAlmostEqual(aircraft.fuel_for_distance(425_000.0, 'max'), 425 / 1300)

        aircraft.consume_fuel(aircraft.fuel_for_distance(425_000.0))
        self.assertAlmostEqual(aircraft.fuel, 0.75)
        self.assertAlmostEqual(aircraft.fuel_range_remaining(), 0.75 * 1_700_000.0)

    def test_capacity_includes_drop_tanks(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        self.assertEqual(aircraft.fuel_capacity_kg(), 7348.0)

        aircraft.assigned_loadout = "Sparrow CAP/Escort"
        self.assertEqual(aircraft.fuel_capacity_kg(), 7348.0 + 2 * 900.0)

    def test_refuelling_pods_are_not_own_fuel(self):
        """Il terzo campo dei pod di rifornimento e' carburante cedibile, non autonomia propria."""
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS

        model, name, loadout = next(
            (m, n, l) for m, loadouts in AIRCRAFT_LOADOUTS.items() for n, l in loadouts.items()
            if any(isinstance(item[0], str) and 'refueling' in item[0] or item[0] == 'hose_drogue_pod'
                   for item in l['stores']['pylons'].values()))
        aircraft = self._aircraft(model=model)
        aircraft.assigned_loadout = name
        self.assertEqual(aircraft.fuel_capacity_kg(), float(loadout['stores']['fuel_internal_max']))

    def test_reassignment_refuels_and_none_unmodels(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        aircraft.consume_fuel(0.4)
        self.assertAlmostEqual(aircraft.fuel, 0.6)

        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        self.assertEqual(aircraft.fuel, 1.0)

        aircraft.assigned_loadout = None
        self.assertIsNone(aircraft.fuel)

    def test_every_loadout_yields_a_usable_autonomy(self):
        """Sui dati reali: ogni loadout con raggio fuel_100% da' un'autonomia positiva."""
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS

        checked = 0

        for model, loadouts in list(AIRCRAFT_LOADOUTS.items())[:10]:
            aircraft = self._aircraft(model=model)

            for name, loadout in loadouts.items():
                radius = loadout.get('cruise', {}).get('range', {}).get('fuel_100%')

                if not radius:
                    continue

                aircraft.assigned_loadout = name
                self.assertAlmostEqual(aircraft.fuel_autonomy(), 2 * radius * 1000.0)
                self.assertEqual(aircraft.fuel, 1.0)
                checked += 1

        self.assertGreater(checked, 0)

    def test_bad_regime_raises(self):
        aircraft = self._aircraft()
        aircraft.assigned_loadout = "Phoenix Fleet Defense"
        with self.assertRaises(ValueError):
            aircraft.fuel_autonomy('afterburner')


if __name__ == '__main__':
    unittest.main()
