import unittest
from unittest.mock import MagicMock, patch
from sympy import Point3D
from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Threat import Threat
from Code.Dynamic_War_Manager.Source.DataType.State import State

class TestAsset(unittest.TestCase):
    def setUp(self):
        # Create a mock Block
        self.mock_block = MagicMock(spec=Block)
        self.mock_block.isMilitary = True
        self.mock_block.isLogistic = False
        self.mock_block.isCivilian = False
        self.mock_block.get_asset.return_value = None
        
        # Basic Asset for testing
        self.asset = Asset(
            block=self.mock_block,
            name="Test Asset",
            description="Test Description",
            category="Military",
            asset_type="Tank",
            functionality="Combat",
            cost=100,
            value=150,
            position=Point3D(10, 20, 30)
        )
        
        # Payloads for testing
        self.test_acp = Payload(goods=100, energy=50, hr=10, hc=5, hs=2, hb=1)
        self.test_rcp = Payload(goods=20, energy=10, hr=2, hc=1, hs=0, hb=0)
        self.test_payload = Payload(goods=200, energy=100, hr=20, hc=10, hs=5, hb=2)

    def test_initialization(self):
        self.assertEqual(self.asset.name, "Test Asset")
        self.assertEqual(self.asset.description, "Test Description")
        self.assertEqual(self.asset.category, "Military")
        self.assertEqual(self.asset.asset_type, "Tank")
        self.assertEqual(self.asset.functionality, "Combat")
        self.assertEqual(self.asset.cost, 100)
        self.assertEqual(self.asset.value, 150)
        self.assertEqual(self.asset.position, Point3D(10, 20, 30))
        self.assertIsInstance(self.asset.id, str)
        self.assertIsInstance(self.asset.state, State)

    def test_property_setters(self):
        # Test name setter
        self.asset.name = "New Name"
        self.assertEqual(self.asset.name, "New Name")
        
        # Test invalid name type
        with self.assertRaises(TypeError):
            self.asset.name = 123
            
        # Test position setter
        new_pos = Point3D(50, 60, 70)
        self.asset.position = new_pos
        self.assertEqual(self.asset.position, new_pos)
        
        # Test invalid position type
        with self.assertRaises(TypeError):
            self.asset.position = "invalid position"

    def test_payload_operations(self):
        # Set payloads
        self.asset.assigned_for_self = self.test_acp
        self.asset.requested_for_self = self.test_rcp
        self.asset.storage = self.test_payload
        
        # Test balance_trade calculation
        expected_balance = sum([
            self.test_acp.goods / self.test_rcp.goods,
            self.test_acp.energy / self.test_rcp.energy,
            self.test_acp.hr / self.test_rcp.hr,
            self.test_acp.hc / self.test_rcp.hc
        ]) / 4  # Only 4 items have non-zero rcp
        
        self.assertAlmostEqual(self.asset.balance_trade, expected_balance)
        
        # Test efficiency calculation
        self.asset.health = 80
        expected_efficiency = expected_balance * 80
        self.assertAlmostEqual(self.asset.efficiency, expected_efficiency)
        
        # Test consume operation
        consume_result = self.asset.consume()
        self.assertFalse(all(consume_result.values()))
        
        # Verify acp was reduced
        self.assertEqual(self.asset.assigned_for_self.goods, 80)  # 100 - 20
        self.assertEqual(self.asset.assigned_for_self.energy, 40)  # 50 - 10
        self.assertEqual(self.asset.assigned_for_self.hr, 8)  # 10 - 2
        self.assertEqual(self.asset.assigned_for_self.hc, 4)  # 5 - 1

    def test_event_management(self):
        event1 = Event(event_type="Event 1")
        event2 = Event(event_type="Event 2")
        
        # Test adding events
        self.asset.add_event(event1)
        self.asset.add_event(event2)
        self.assertEqual(len(self.asset.events), 2)
        
        # Test getting events
        self.assertEqual(self.asset.get_last_event(), event2)
        self.assertEqual(self.asset.get_event(0), event1)
        
        # Test removing events
        self.asset.remove_event(event1)
        self.assertEqual(len(self.asset.events), 1)
        self.assertEqual(self.asset.events[0], event2)
        
        # Test invalid operations
        with self.assertRaises(ValueError):
            self.asset.add_event("not an event")
            
        with self.assertRaises(IndexError):
            self.asset.get_event(10)
            
        with self.assertRaises(ValueError):
            self.asset.remove_event(event1)  # Already removed

    def test_dcs_data_handling(self):
        valid_dcs_data = {
            "unit_name": "DCS Unit",
            "unit_type": "T-90",
            "unitId": 12345,
            "unit_frequency": 251.0,
            "unit_x": 100.0,
            "unit_y": 200.0,
            "unit_alt": 50.0,
            "unit_alt_type": "ASL",
            "unit_health": 95
        }
        
        # Test setting valid DCS data
        self.asset.dcs_unit_data = valid_dcs_data
        self.assertEqual(self.asset.name, "DCS Unit")
        self.assertEqual(self.asset.id, "12345")
        self.assertEqual(self.asset.position, Point3D(100, 200, 50))
        self.assertEqual(self.asset.health, 95)
        
        # Test invalid DCS data
        invalid_dcs_data = valid_dcs_data.copy()
        invalid_dcs_data["unit_health"] = "not an integer"
        
        with self.assertRaises(ValueError):
            self.asset.dcs_unit_data = invalid_dcs_data

    def test_block_association(self):
        new_block = MagicMock(spec=Block)
        new_block.get_asset.return_value = None
        
        # Test valid block change
        self.asset.block = new_block
        self.assertEqual(self.asset.block, new_block)
        
        # Test invalid block type
        with self.assertRaises(TypeError):
            self.asset.block = "not a block"
            
        # Test association conflict
        conflicting_block = MagicMock(spec=Block)
        conflicting_asset = Asset(block=self.mock_block, name="Conflict")
        conflicting_block.get_asset.return_value = conflicting_asset
        
        with self.assertRaises(ValueError):
            self.asset.block = conflicting_block

    def test_type_checking(self):
        # Test military/civilian/logistic checks
        self.assertTrue(self.asset.is_military())
        self.assertFalse(self.asset.is_logistic())
        self.assertFalse(self.asset.is_civilian())
        
        # Change block type and re-test
        self.mock_block.isMilitary = False
        self.mock_block.isLogistic = True
        self.assertFalse(self.asset.is_military())
        self.assertTrue(self.asset.is_logistic())

    def test_volume_and_threat(self):
        mock_volume = MagicMock(spec=Volume)
        mock_threat = MagicMock(spec=Threat)
        
        # Test volume setting
        self.asset.volume = mock_volume
        self.assertEqual(self.asset.volume, mock_volume)
        
        # Test threat setting
        self.asset.threat = mock_threat
        self.assertEqual(self.asset.threat, mock_threat)
        
        # Test invalid types
        with self.assertRaises(TypeError):
            self.asset.volume = "not a volume"
            
        with self.assertRaises(TypeError):
            self.asset.threat = "not a threat"

if __name__ == '__main__':
    unittest.main()