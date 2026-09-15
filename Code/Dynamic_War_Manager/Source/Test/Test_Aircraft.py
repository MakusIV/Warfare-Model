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


if __name__ == '__main__':
    unittest.main()
