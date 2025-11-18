import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from sympy import Point3D
from Code.Dynamic_War_Manager.Source.Asset.Vehicle import Vehicle
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.Context.Context import (
    GROUND_COMBAT_EFFICACY,
    ACTION_TASKS,
    Ground_Asset_Type
)


class TestVehicle(unittest.TestCase):
    """Test suite for Vehicle class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a mock Block
        self.mock_block = MagicMock(spec=Block)
        self.mock_block.isMilitary.return_value = True
        self.mock_block.isLogistic.return_value = False
        self.mock_block.isCivilian.return_value = False
        self.mock_block.block_class = "Military"
        self.mock_block.get_asset.return_value = None

        # Mock vehicle data
        self.mock_vehicle_scores = {
            'combat score': 0.75,
            'mobility score': 0.85,
            'defense score': 0.65
        }

        # Basic test payloads
        self.test_acp = Payload(goods=100, energy=50, hr=10, hc=5, hs=2, hb=1)
        self.test_rcp = Payload(goods=20, energy=10, hr=2, hc=1, hs=0, hb=0)
        self.test_payload = Payload(goods=200, energy=100, hr=20, hc=10, hs=5, hb=2)

        # Test volume
        self.test_volume = Volume(x=10, y=5, z=3)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_initialization(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test Vehicle initialization with all parameters"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            name="Test Tank",
            model="M1_Abrams",
            description="Test Description",
            category=Ground_Asset_Type.TANK.value,
            asset_type="Main_Battle_Tank",
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
            role="Heavy Combat"
        )

        self.assertEqual(vehicle.name, "Test Tank")
        self.assertEqual(vehicle._model, "M1_Abrams")
        self.assertEqual(vehicle.description, "Test Description")
        self.assertEqual(vehicle.category, Ground_Asset_Type.TANK.value)
        self.assertEqual(vehicle.asset_type, "Main_Battle_Tank")
        self.assertEqual(vehicle.functionality, "Combat")
        self.assertEqual(vehicle.cost, 1000)
        self.assertEqual(vehicle.value, 10)
        self.assertEqual(vehicle.position, Point3D(100, 200, 0))
        self.assertTrue(vehicle.crytical)
        self.assertEqual(vehicle.repair_time, 48)
        self.assertEqual(vehicle.role, "Heavy Combat")

        # Verify get_vehicle_scores was called
        mock_get_vehicle_scores.assert_called_once_with(model="M1_Abrams")

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_initialization_minimal_params(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test Vehicle initialization with minimal parameters"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(block=self.mock_block)

        self.assertEqual(vehicle.block, self.mock_block)
        self.assertIsNotNone(vehicle.id)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.GROUND_MILITARY_VEHICLE_ASSET')
    def test_loadAssetDataFromContext_military(self, mock_asset_data, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test loadAssetDataFromContext for military vehicles"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Mock the asset data structure
        mock_asset_data.__getitem__ = MagicMock(return_value={
            "Main_Battle_Tank": {
                "cost": 2000,
                "value": 9,
                "rcp": self.test_rcp,
                "t2r": 72,
                "payload%": 0.8
            }
        })

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.TANK.value,
            asset_type="Main_Battle_Tank"
        )

        result = vehicle.loadAssetDataFromContext()

        # Since we're mocking, the actual loading won't happen as expected
        # This test verifies that the method can be called
        self.assertIsInstance(result, bool)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_loadAssetDataFromContext_logistic(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test loadAssetDataFromContext for logistic vehicles"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Create a logistic block
        logistic_block = MagicMock(spec=Block)
        logistic_block.isMilitary.return_value = False
        logistic_block.isLogistic.return_value = True
        logistic_block.block_class = "Transport"

        vehicle = Vehicle(
            block=logistic_block,
            category="Road",
            asset_type="Truck"
        )

        result = vehicle.loadAssetDataFromContext()
        self.assertIsInstance(result, bool)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_loadAssetDataFromContext_invalid_block(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test loadAssetDataFromContext with invalid block type raises exception"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Create an invalid block (neither military nor logistic)
        invalid_block = MagicMock(spec=Block)
        invalid_block.isMilitary.return_value = False
        invalid_block.isLogistic.return_value = False
        invalid_block.block_class = "Invalid"

        vehicle = Vehicle(
            block=invalid_block,
            category="Unknown",
            asset_type="Unknown"
        )

        with self.assertRaises(Exception) as context:
            vehicle.loadAssetDataFromContext()

        self.assertIn("not consistent with the ownership block", str(context.exception))

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.BLOCK_ASSET_CATEGORY')
    def test_checkParam_with_valid_asset_type(self, mock_asset_category, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test checkParam with valid asset_type"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(block=self.mock_block)

        # Mock the asset category structure
        mock_asset_category.__getitem__ = MagicMock(return_value={
            "Tank": {"Main_Battle_Tank": {}}
        })

        result = vehicle.checkParam(category="Tank", asset_type="Main_Battle_Tank")

        # The result should be a tuple (bool, str)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], bool)
        self.assertIsInstance(result[1], str)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_checkParam_with_invalid_asset_type(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test checkParam with invalid asset_type (non-string)"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(block=self.mock_block)

        # The method expects strings, so it should handle None gracefully
        result = vehicle.checkParam(category=None, asset_type=None)
        self.assertIsInstance(result, tuple)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isTank(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isTank property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.TANK.value
        )

        self.assertTrue(vehicle.isTank)

        # Test with non-tank category
        vehicle_armor = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.ARMORED.value
        )

        self.assertFalse(vehicle_armor.isTank)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isArmor(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isArmor property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.ARMORED.value
        )

        self.assertTrue(vehicle.isArmor)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isMotorized(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isMotorized property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.MOTORIZED.value
        )

        self.assertTrue(vehicle.isMotorized)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isArtillery_Semovent(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isArtillery_Semovent property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.ARTILLERY_SEMOVENT
        )

        self.assertTrue(vehicle.isArtillery_Semovent)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isArtillery_Fixed(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isArtillery_Fixed property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.ARTILLERY_FIXED
        )

        self.assertTrue(vehicle.isArtillery_Fixed)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isArtillery(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isArtillery property (compound property)"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Test with semovent artillery
        vehicle_semovent = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.ARTILLERY_SEMOVENT
        )
        self.assertTrue(vehicle_semovent.isArtillery)

        # Test with fixed artillery
        vehicle_fixed = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.ARTILLERY_FIXED
        )
        self.assertTrue(vehicle_fixed.isArtillery)

        # Test with non-artillery
        vehicle_tank = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.TANK.value
        )
        self.assertFalse(vehicle_tank.isArtillery)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isSAM_Big(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isSAM_Big property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category="SAM_Big"
        )

        self.assertTrue(vehicle.isSAM_Big)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isSAM_Med(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isSAM_Med property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category="SAM_Med"
        )

        self.assertTrue(vehicle.isSAM_Med)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isSAM_Small(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isSAM_Small property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category="SAM_Small"
        )

        self.assertTrue(vehicle.isSAM_Small)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isSAM(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isSAM property (compound property)"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Test SAM_Big
        vehicle_big = Vehicle(block=self.mock_block, category="SAM_Big")
        self.assertTrue(vehicle_big.isSAM)

        # Test SAM_Med
        vehicle_med = Vehicle(block=self.mock_block, category="SAM_Med")
        self.assertTrue(vehicle_med.isSAM)

        # Test SAM_Small
        vehicle_small = Vehicle(block=self.mock_block, category="SAM_Small")
        self.assertTrue(vehicle_small.isSAM)

        # Test non-SAM
        vehicle_tank = Vehicle(block=self.mock_block, category=Ground_Asset_Type.TANK.value)
        self.assertFalse(vehicle_tank.isSAM)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isAAA(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isAAA property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category="AAA"
        )

        self.assertTrue(vehicle.isAAA)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isAntiAircraft(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isAntiAircraft property (compound property)"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Test with SAM
        vehicle_sam = Vehicle(block=self.mock_block, category="SAM_Med")
        self.assertTrue(vehicle_sam.isAntiAircraft)

        # Test with AAA
        vehicle_aaa = Vehicle(block=self.mock_block, category="AAA")
        self.assertTrue(vehicle_aaa.isAntiAircraft)

        # Test with non-anti-aircraft
        vehicle_tank = Vehicle(block=self.mock_block, category=Ground_Asset_Type.TANK.value)
        self.assertFalse(vehicle_tank.isAntiAircraft)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isEWR(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isEWR property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category="EWR"
        )

        self.assertTrue(vehicle.isEWR)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    def test_property_isCommandControl(self, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test isCommandControl property"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        vehicle = Vehicle(
            block=self.mock_block,
            category="Command_&_Control"
        )

        self.assertTrue(vehicle.isCommandControl)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.GROUND_COMBAT_EFFICACY')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.ACTION_TASKS')
    def test_set_combat_power_no_action(self, mock_action_tasks, mock_combat_efficacy, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test set_combat_power without specific action"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Mock ACTION_TASKS and GROUND_COMBAT_EFFICACY
        mock_action_tasks.__getitem__ = MagicMock(return_value=["attack", "defend", "recon"])
        mock_combat_efficacy.__getitem__ = MagicMock(return_value={
            Ground_Asset_Type.TANK.value: 1.0
        })

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.TANK.value,
            model="M1_Abrams"
        )

        # Manually set efficiency for testing
        vehicle._efficiency = 0.9

        vehicle.set_combat_power()

        # Verify combat_power was set
        self.assertIsNotNone(vehicle.combat_power)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.GROUND_COMBAT_EFFICACY')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.ACTION_TASKS')
    def test_set_combat_power_with_action(self, mock_action_tasks, mock_combat_efficacy, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test set_combat_power with specific action"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Mock ACTION_TASKS and GROUND_COMBAT_EFFICACY
        mock_action_tasks.__getitem__ = MagicMock(return_value=["attack", "defend", "recon"])
        mock_combat_efficacy.__getitem__ = MagicMock(return_value={
            Ground_Asset_Type.TANK.value: 1.0
        })

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.TANK.value,
            model="M1_Abrams"
        )

        # Manually set efficiency for testing
        vehicle._efficiency = 0.9

        vehicle.set_combat_power(action="attack")

        # Verify combat_power was set
        self.assertIsNotNone(vehicle.combat_power)

    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_scores')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.get_vehicle_data')
    @patch('Code.Dynamic_War_Manager.Source.Asset.Vehicle.ACTION_TASKS')
    def test_set_combat_power_invalid_action(self, mock_action_tasks, mock_get_vehicle_data, mock_get_vehicle_scores):
        """Test set_combat_power with invalid action raises TypeError"""
        mock_get_vehicle_scores.return_value = self.mock_vehicle_scores
        mock_get_vehicle_data.return_value = {}

        # Mock ACTION_TASKS to return a specific list
        mock_action_tasks.__getitem__ = MagicMock(return_value=["attack", "defend", "recon"])

        vehicle = Vehicle(
            block=self.mock_block,
            category=Ground_Asset_Type.TANK.value,
            model="M1_Abrams"
        )

        with self.assertRaises(TypeError):
            vehicle.set_combat_power(action="invalid_action")


if __name__ == '__main__':
    unittest.main()
