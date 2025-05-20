import unittest
from unittest.mock import MagicMock, patch
from sympy import Point
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.State import State
from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.Context.Region import Region

class TestBlock(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.block = Block(
            name="Test Block",
            description="Test Description",
            side="Blue",
            category="Military",
            sub_category="Base",
            functionality="Defense",
            value=100
        )
        
        # Mock assets
        self.mock_asset1 = MagicMock(spec=Asset)
        self.mock_asset1.cost = 50
        self.mock_asset1.efficiency = 0.8
        self.mock_asset1.balance_trade = 1.2
        self.mock_asset1.position = Point(10, 20)
        
        self.mock_asset2 = MagicMock(spec=Asset)
        self.mock_asset2.cost = 75
        self.mock_asset2.efficiency = 0.6
        self.mock_asset2.balance_trade = 0.9
        self.mock_asset2.position = Point(30, 40)
        
        # Mock event
        self.mock_event = MagicMock(spec=Event)
        self.mock_event.name = "Test Event"

        # Mock Region
        self.mock_region = MagicMock()
        self.mock_region.__class__.__name__ = 'Region'

    def test_initialization(self):
        """Test block initialization"""
        self.assertEqual(self.block.name, "Test Block")
        self.assertEqual(self.block.description, "Test Description")
        self.assertEqual(self.block.side, "Blue")
        self.assertEqual(self.block.category, "Military")
        self.assertEqual(self.block.sub_category, "Base")
        self.assertEqual(self.block.functionality, "Defense")
        self.assertEqual(self.block.value, 100)
        self.assertIsInstance(self.block.id, str)
        self.assertIsInstance(self.block.state, State)

    def test_property_validation(self):
        """Test property validation"""
        # Test valid property setting
        self.block.name = "New Name"
        self.assertEqual(self.block.name, "New Name")
        
        # Test invalid property types
        with self.assertRaises(TypeError):
            self.block.name = 123
            
        with self.assertRaises(TypeError):
            self.block.value = "invalid"
            
        with self.assertRaises(ValueError):
            self.block.side = "InvalidSide"

    def test_event_management(self):
        """Test event management methods"""
        # Test adding events
        self.block.add_event(self.mock_event)
        self.assertEqual(len(self.block.events), 1)
        
        # Test getting events
        self.assertEqual(self.block.get_last_event(), self.mock_event)
        self.assertEqual(self.block.get_event(0), self.mock_event)
        
        # Test removing events
        self.block.remove_event(self.mock_event)
        self.assertEqual(len(self.block.events), 0)
        
        # Test invalid operations
        with self.assertRaises(TypeError):
            self.block.add_event("not an event")
            
        with self.assertRaises(IndexError):
            self.block.get_event(0)

    def test_asset_management(self):
        """Test asset management methods"""
        # Test adding assets
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        self.assertEqual(len(self.block.assets), 2)
        
        # Test getting assets
        self.assertEqual(self.block.get_asset("asset1"), self.mock_asset1)
        self.assertEqual(self.block.get_asset("invalid"), None)
        
        # Test listing asset keys
        self.assertCountEqual(self.block.list_asset_keys(), ["asset1", "asset2"])
        
        # Test removing assets
        self.block.remove_asset("asset1")
        self.assertEqual(len(self.block.assets), 1)
        
        # Test invalid operations
        with self.assertRaises(TypeError):
            self.block.set_asset(123, self.mock_asset1)
            
        with self.assertRaises(KeyError):
            self.block.remove_asset("nonexistent")

    def test_calculated_properties(self):
        """Test calculated properties"""
        # Set up assets
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        
        # Test cost calculation
        self.assertEqual(self.block.cost, 125)  # 50 + 75
        
        # Test efficiency calculation
        expected_efficiency = (0.8 + 0.6) / 2
        self.assertAlmostEqual(self.block.efficiency, expected_efficiency)
        
        # Test balance trade calculation
        expected_balance = (1.2 + 0.9) / 2
        self.assertAlmostEqual(self.block.balance_trade, expected_balance)
        
        # Test position calculation
        expected_position = Point(20, 30)  # Mean of (10,20) and (30,40)
        self.assertEqual(self.block.position, expected_position)
        
        # Test empty case
        empty_block = Block(name="Empty")
        self.assertEqual(empty_block.cost, 0)
        self.assertEqual(empty_block.efficiency, 0.0)
        self.assertIsNone(empty_block.position)

    def test_type_checks(self):
        """Test block type checking methods"""
        self.assertTrue(self.block.is_military())
        self.assertFalse(self.block.is_logistic())
        self.assertFalse(self.block.is_civilian())
        
        # Change category and re-test
        self.block.category = "Logistic"
        self.assertFalse(self.block.is_military())
        self.assertTrue(self.block.is_logistic())

    def test_representation(self):
        """Test string representations"""
        repr_str = repr(self.block)
        self.assertIn("Test Block", repr_str)
        self.assertIn("Military", repr_str)
        
        str_str = str(self.block)
        self.assertIn("Test Block", str_str)
        self.assertIn("Blue", str_str)

    def test_region_association(self):
        """Test region association"""        
        self.block.region = self.mock_region
        self.assertEqual(self.block.region, self.mock_region)
        
        # Test invalid region type
        with self.assertRaises(TypeError):
            self.block.region = "invalid region"

if __name__ == '__main__':
    unittest.main()