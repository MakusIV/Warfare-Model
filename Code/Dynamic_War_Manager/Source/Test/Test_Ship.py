import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from sympy import Point3D
from Code.Dynamic_War_Manager.Source.Asset.Ship import Ship
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Area import Area
from Code.Dynamic_War_Manager.Source.Context.Context import (
    SHAPE2D,
    SHAPE3D,
    SEA_COMBAT_EFFICACY,
    ACTION_TASKS,
    Sea_Asset_Type,
)
from sympy import Point2D


class TestShip(unittest.TestCase):
    """Test suite for Ship class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.mock_block = MagicMock(spec=Block)
        self.mock_block.is_military.return_value = True
        self.mock_block.is_logistic.return_value = False
        self.mock_block.is_civilian.return_value = False
        self.mock_block.block_class = "Military"
        self.mock_block.get_asset.return_value = None

        # Mock ship scores, mirroring Ship_Data.get_ship_scores' real key shape
        # ('global_score'/'category_score', underscore — see Fase 0 B1 fix on Vehicle).
        self.mock_ship_scores = {
            'combat score': {'global_score': 0.75, 'category_score': 0.7},
            'weapon score': {'global_score': 0.6, 'category_score': 0.55},
        }

        self.test_acp = Payload(goods=100, energy=50, hr=10, hc=5, hs=2, hb=1)
        self.test_rcp = Payload(goods=20, energy=10, hr=2, hc=1, hs=0, hb=0)
        self.test_payload = Payload(goods=200, energy=100, hr=20, hc=10, hs=5, hb=2)

        area = Area(shape=SHAPE2D.CIRCLE, radius=4.0, center=Point2D(0, 0))
        self.test_volume = Volume(area_base=area, volume_shape=SHAPE3D.CYLINDER)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data')
    def test_initialization(self, mock_get_ship_data, mock_get_ship_scores):
        """Test Ship initialization with all parameters"""
        mock_get_ship_scores.return_value = self.mock_ship_scores
        mock_get_ship_data.return_value = {}

        ship = Ship(
            block=self.mock_block,
            name="Test Carrier",
            model="CVN-70 Carl Vinson",
            description="Test Description",
            category="Carrier",
            asset_type=Sea_Asset_Type.CARRIER,
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
            role="Power Projection"
        )

        self.assertEqual(ship.name, "Test Carrier")
        self.assertEqual(ship._model, "CVN-70 Carl Vinson")
        self.assertEqual(ship.category, "Carrier")
        self.assertEqual(ship.asset_type, Sea_Asset_Type.CARRIER.value)
        self.assertTrue(ship.crytical)
        self.assertEqual(ship.repair_time, 48)

        mock_get_ship_scores.assert_called_once_with(model="CVN-70 Carl Vinson")

    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data')
    def test_property_isCarrier(self, mock_get_ship_data, mock_get_ship_scores):
        """Test isCarrier property"""
        mock_get_ship_scores.return_value = self.mock_ship_scores
        mock_get_ship_data.return_value = {}

        ship = Ship(block=self.mock_block, asset_type=Sea_Asset_Type.CARRIER, model="CVN-70 Carl Vinson")
        self.assertTrue(ship.isCarrier)

        ship_destroyer = Ship(block=self.mock_block, asset_type=Sea_Asset_Type.DESTROYER, model="Arleigh Burke")
        self.assertFalse(ship_destroyer.isCarrier)
        self.assertTrue(ship_destroyer.isDestroyer)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data')
    @patch.object(Ship, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_set_combat_power_no_action(self, mock_efficiency, mock_get_ship_data, mock_get_ship_scores):
        """Test set_combat_power without specific action: computes all sea tasks"""
        mock_get_ship_scores.return_value = self.mock_ship_scores
        mock_get_ship_data.return_value = {}

        ship = Ship(block=self.mock_block, asset_type=Sea_Asset_Type.CARRIER, model="CVN-70 Carl Vinson")
        ship.set_combat_power()  # No actions provided, should compute for all sea tasks

        combat_power_result = ship.combat_power(force='sea')
        self.assertIsInstance(combat_power_result, dict)
        self.assertEqual(set(combat_power_result.keys()), set(ACTION_TASKS['sea']))
        for value in combat_power_result.values():
            self.assertIsInstance(value, (float, int))
            self.assertGreater(value, 0.0)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data')
    @patch.object(Ship, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_set_combat_power_with_action(self, mock_efficiency, mock_get_ship_data, mock_get_ship_scores):
        """Test set_combat_power with a specific action"""
        mock_get_ship_scores.return_value = self.mock_ship_scores
        mock_get_ship_data.return_value = {}

        ship = Ship(block=self.mock_block, asset_type=Sea_Asset_Type.DESTROYER, model="Arleigh Burke")
        ship.set_combat_power(actions=["Attack"])

        combat_power_result = ship.combat_power(force='sea', action='Attack')
        self.assertIsInstance(combat_power_result, (float, int))
        self.assertGreater(combat_power_result, 0.0)
        self.assertEqual(ship._combat_power['sea']['Attack'], combat_power_result)

        # Sanity check against the shared formula directly.
        expected = (1 + SEA_COMBAT_EFFICACY['Attack']['Destroyer'] * 0.3 / 5) * (1 + 0.75) * 0.8
        self.assertAlmostEqual(combat_power_result, expected)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data')
    def test_set_combat_power_invalid_action(self, mock_get_ship_data, mock_get_ship_scores):
        """Test set_combat_power with invalid action raises TypeError"""
        mock_get_ship_scores.return_value = self.mock_ship_scores
        mock_get_ship_data.return_value = {}

        ship = Ship(block=self.mock_block, asset_type=Sea_Asset_Type.CARRIER, model="CVN-70 Carl Vinson")

        with self.assertRaises(TypeError):
            ship.set_combat_power(actions=["Attack", "invalid_action"])

    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data')
    @patch.object(Ship, 'efficiency', new_callable=PropertyMock, return_value=0.8)
    def test_set_combat_power_unknown_category_returns_zero(self, mock_efficiency, mock_get_ship_data, mock_get_ship_scores):
        """A category absent from SEA_COMBAT_EFFICACY (e.g. a non-combat ship) gets combat_power 0."""
        mock_get_ship_scores.return_value = self.mock_ship_scores
        mock_get_ship_data.return_value = {}

        ship = Ship(block=self.mock_block, asset_type="Not_A_Real_Category", model="CVN-70 Carl Vinson")
        combat_power_result = ship.combat_power(force='sea', action='Attack')
        self.assertEqual(combat_power_result, 0)

    def test_get_physical_characteristics_no_model_returns_none(self):
        """get_physical_characteristics returns None when no model is set."""
        with patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_scores', return_value=self.mock_ship_scores), \
             patch('Code.Dynamic_War_Manager.Source.Asset.Ship.get_ship_data', return_value={}):
            ship = Ship(block=self.mock_block, asset_type=Sea_Asset_Type.CARRIER)
            self.assertIsNone(ship.get_physical_characteristics())


if __name__ == '__main__':
    unittest.main()
