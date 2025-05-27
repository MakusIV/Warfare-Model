"""
Unit tests for Resource_Manager class

This module provides comprehensive test coverage for the Resource_Manager class
using unittest framework and MagicMock for mocking dependencies.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock, call
import sys
from typing import Dict, Any
from dataclasses import dataclass

# Mock the imports to avoid dependency issues during testing
sys.modules['Code.Dynamic_War_Manager.Source.Utility.Utility'] = MagicMock()
sys.modules['Code.Dynamic_War_Manager.Source.Utility.LoggerClass'] = MagicMock()
sys.modules['Code.Dynamic_War_Manager.Source.DataType.Event'] = MagicMock()
sys.modules['Code.Dynamic_War_Manager.Source.DataType.Volume'] = MagicMock()
sys.modules['Code.Dynamic_War_Manager.Source.DataType.Threat'] = MagicMock()
sys.modules['Code.Dynamic_War_Manager.Source.DataType.Payload'] = MagicMock()
sys.modules['Code.Dynamic_War_Manager.Source.DataType.State'] = MagicMock()
sys.modules['sympy'] = MagicMock()

# Mock Payload class for testing
class MockPayload:
    """Mock implementation of Payload class for testing"""
    
    def __init__(self, **kwargs):
        self.goods = kwargs.get('goods', 0)
        self.energy = kwargs.get('energy', 0)
        self.hr = kwargs.get('hr', 0)
        self.hc = kwargs.get('hc', 0)
        self.hs = kwargs.get('hs', 0)
        self.hb = kwargs.get('hb', 0)
    
    def __getitem__(self, key):
        return getattr(self, key, 0)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def __add__(self, other):
        result = MockPayload()
        for param in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']:
            result[param] = self[param] + other[param]
        return result
    
    def __sub__(self, other):
        result = MockPayload()
        for param in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']:
            result[param] = self[param] - other[param]
        return result
    
    def __mul__(self, multiplier):
        result = MockPayload()
        for param in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']:
            result[param] = self[param] * multiplier
        return result
    
    def __lt__(self, other):
        for param in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']:
            if self[param] >= other[param]:
                return False
        return True
    
    def copy(self):
        return MockPayload(goods=self.goods, energy=self.energy, hr=self.hr, 
                          hc=self.hc, hs=self.hs, hb=self.hb)
    
    def division(self, other):
        result = MockPayload()
        for param in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']:
            divisor = other[param]
            if divisor == 0:
                result[param] = float('inf')
            else:
                result[param] = self[param] / divisor
        return result
    
    def __repr__(self):
        return f"MockPayload(goods={self.goods}, energy={self.energy}, hr={self.hr}, hc={self.hc}, hs={self.hs}, hb={self.hb})"

# Replace the real Payload with our mock
sys.modules['Code.Dynamic_War_Manager.Source.DataType.Payload'].Payload = MockPayload

# Import the class under test (this should be done after mocking)
from resource_manager_optimized import Resource_Manager, Resource_Manager_Params


class TestResourceManager(unittest.TestCase):
    """Test cases for Resource_Manager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock Block objects
        self.mock_block = MagicMock()
        self.mock_block.id = "test_block_1"
        self.mock_block.__class__.__name__ = 'Block'
        self.mock_block.assets = []
        
        # Create mock region
        self.mock_region = MagicMock()
        self.mock_region.blocks_priority = {"client_1": 1.0, "client_2": 2.0}
        self.mock_block.region = self.mock_region
        
        # Create mock client blocks
        self.mock_client_1 = MagicMock()
        self.mock_client_1.id = "client_1"
        self.mock_client_1.__class__.__name__ = 'Block'
        self.mock_client_1.has_resource_manager.return_value = True
        
        self.mock_client_2 = MagicMock()
        self.mock_client_2.id = "client_2"
        self.mock_client_2.__class__.__name__ = 'Block'
        self.mock_client_2.has_resource_manager.return_value = True
        
        # Create mock server block
        self.mock_server = MagicMock()
        self.mock_server.id = "server_1"
        self.mock_server.__class__.__name__ = 'Block'
        self.mock_server.has_resource_manager.return_value = True
        
        # Create mock payloads
        self.mock_warehouse = MockPayload(goods=100, energy=50, hr=20, hc=10, hs=5, hb=2)
        self.mock_request = MockPayload(goods=10, energy=5, hr=2, hc=1, hs=1, hb=1)
        
        # Initialize Resource_Manager
        self.resource_manager = Resource_Manager(
            block=self.mock_block,
            warehouse=self.mock_warehouse
        )

    def tearDown(self):
        """Clean up after each test method."""
        pass

    # === INITIALIZATION TESTS ===
    
    def test_init_with_valid_parameters(self):
        """Test successful initialization with valid parameters"""
        clients = {"client_1": self.mock_client_1}
        server = {"server_1": self.mock_server}
        
        rm = Resource_Manager(
            block=self.mock_block,
            clients=clients,
            server=server,
            warehouse=self.mock_warehouse
        )
        
        self.assertEqual(rm.block, self.mock_block)
        self.assertEqual(rm.warehouse.goods, 100)
        self.assertIsInstance(rm._clients, dict)
        self.assertIsInstance(rm._server, dict)
    
    def test_init_with_none_parameters(self):
        """Test initialization with None parameters"""
        rm = Resource_Manager(block=self.mock_block)
        
        self.assertEqual(rm.block, self.mock_block)
        self.assertIsInstance(rm.warehouse, MockPayload)
        self.assertEqual(len(rm._clients), 0)
        self.assertEqual(len(rm._server), 0)
    
    def test_init_with_invalid_block(self):
        """Test initialization with invalid block parameter"""
        with self.assertRaises(TypeError):
            Resource_Manager(block="invalid_block")
    
    def test_init_with_invalid_clients(self):
        """Test initialization with invalid clients parameter"""
        with self.assertRaises(TypeError):
            Resource_Manager(block=self.mock_block, clients="invalid")
    
    def test_init_with_invalid_warehouse(self):
        """Test initialization with invalid warehouse parameter"""
        with self.assertRaises(TypeError):
            Resource_Manager(block=self.mock_block, warehouse="invalid")

    # === BLOCK PROPERTY TESTS ===
    
    def test_block_property_getter(self):
        """Test block property getter"""
        self.assertEqual(self.resource_manager.block, self.mock_block)
    
    def test_block_property_setter_valid(self):
        """Test block property setter with valid block"""
        new_block = MagicMock()
        new_block.__class__.__name__ = 'Block'
        
        self.resource_manager.block = new_block
        self.assertEqual(self.resource_manager.block, new_block)
    
    def test_block_property_setter_invalid(self):
        """Test block property setter with invalid block"""
        with self.assertRaises(TypeError):
            self.resource_manager.block = "invalid_block"
    
    def test_warehouse_property_getter(self):
        """Test warehouse property getter"""
        self.assertEqual(self.resource_manager.warehouse.goods, 100)
    
    def test_warehouse_property_setter_valid(self):
        """Test warehouse property setter with valid payload"""
        new_warehouse = MockPayload(goods=200, energy=100)
        self.resource_manager.warehouse = new_warehouse
        self.assertEqual(self.resource_manager.warehouse.goods, 200)
    
    def test_warehouse_property_setter_invalid(self):
        """Test warehouse property setter with invalid payload"""
        with self.assertRaises(TypeError):
            self.resource_manager.warehouse = "invalid_payload"

    # === SERVER MANAGEMENT TESTS ===
    
    def test_set_server_valid(self):
        """Test setting a valid server"""
        # Mock the server's resource manager
        mock_server_rm = MagicMock()
        self.mock_server.resource_manager = mock_server_rm
        
        self.resource_manager.set_server("server_1", self.mock_server)
        
        self.assertIn("server_1", self.resource_manager._server)
        self.assertEqual(self.resource_manager._server["server_1"], self.mock_server)
        mock_server_rm.set_client.assert_called_once_with(self.mock_block.id, self.mock_block)
    
    def test_set_server_invalid_key(self):
        """Test setting server with invalid key type"""
        with self.assertRaises(TypeError):
            self.resource_manager.set_server(123, self.mock_server)
    
    def test_set_server_invalid_block(self):
        """Test setting server with invalid block"""
        with self.assertRaises(TypeError):
            self.resource_manager.set_server("server_1", "invalid_block")
    
    def test_set_server_no_resource_manager(self):
        """Test setting server with block that has no resource manager"""
        self.mock_server.has_resource_manager.return_value = False
        
        with self.assertRaises(ValueError):
            self.resource_manager.set_server("server_1", self.mock_server)
    
    def test_get_server_existing(self):
        """Test getting an existing server"""
        self.resource_manager._server["server_1"] = self.mock_server
        
        result = self.resource_manager.get_server("server_1")
        self.assertEqual(result, self.mock_server)
    
    def test_get_server_non_existing(self):
        """Test getting a non-existing server"""
        result = self.resource_manager.get_server("non_existing")
        self.assertIsNone(result)
    
    def test_remove_server_valid(self):
        """Test removing a valid server"""
        # Setup server with resource manager
        mock_server_rm = MagicMock()
        self.mock_server.resource_manager = mock_server_rm
        self.resource_manager._server["server_1"] = self.mock_server
        
        self.resource_manager.remove_server("server_1")
        
        self.assertNotIn("server_1", self.resource_manager._server)
        mock_server_rm.remove_client.assert_called_once_with(self.mock_block.id)
    
    def test_remove_server_non_existing(self):
        """Test removing a non-existing server"""
        with self.assertRaises(KeyError):
            self.resource_manager.remove_server("non_existing")
    
    def test_list_server_keys(self):
        """Test listing server keys"""
        self.resource_manager._server = {"server_1": self.mock_server, "server_2": MagicMock()}
        
        keys = self.resource_manager.list_server_keys()
        self.assertEqual(set(keys), {"server_1", "server_2"})

    # === CLIENT MANAGEMENT TESTS ===
    
    def test_set_client_valid(self):
        """Test setting a valid client"""
        # Mock client's resource manager
        mock_client_rm = MagicMock()
        mock_client_rm.get_server.return_value = self.mock_block
        self.mock_client_1.resource_manager = mock_client_rm
        
        self.resource_manager.set_client("client_1", self.mock_client_1)
        
        self.assertIn("client_1", self.resource_manager._clients)
        self.assertEqual(self.resource_manager._clients["client_1"], self.mock_client_1)
    
    def test_set_client_no_resource_manager(self):
        """Test setting client with no resource manager"""
        self.mock_client_1.resource_manager = None
        
        with self.assertRaises(ValueError):
            self.resource_manager.set_client("client_1", self.mock_client_1)
    
    def test_set_client_missing_back_reference(self):
        """Test setting client with missing back reference"""
        mock_client_rm = MagicMock()
        mock_client_rm.get_server.return_value = None  # Missing back reference
        self.mock_client_1.resource_manager = mock_client_rm
        
        with self.assertRaises(ValueError):
            self.resource_manager.set_client("client_1", self.mock_client_1)
    
    def test_get_client_existing(self):
        """Test getting an existing client"""
        self.resource_manager._clients["client_1"] = self.mock_client_1
        
        result = self.resource_manager.get_client("client_1")
        self.assertEqual(result, self.mock_client_1)
    
    def test_remove_client_valid(self):
        """Test removing a valid client"""
        # Setup client with resource manager and back reference
        mock_client_rm = MagicMock()
        mock_client_rm.get_server.return_value = self.mock_block
        self.mock_client_1.resource_manager = mock_client_rm
        self.resource_manager._clients["client_1"] = self.mock_client_1
        
        self.resource_manager.remove_client("client_1")
        
        self.assertNotIn("client_1", self.resource_manager._clients)
    
    def test_list_client_keys(self):
        """Test listing client keys"""
        self.resource_manager._clients = {"client_1": self.mock_client_1, "client_2": self.mock_client_2}
        
        keys = self.resource_manager.list_client_keys()
        self.assertEqual(set(keys), {"client_1", "client_2"})

    # === RESOURCE CALCULATION TESTS ===
    
    def test_evaluate_resources_to_self_consume(self):
        """Test evaluation of resources for self consumption"""
        # Create mock assets with resource requirements
        mock_asset_1 = MagicMock()
        mock_asset_1.resources_to_self_consume = MockPayload(goods=5, energy=2)
        
        mock_asset_2 = MagicMock()
        mock_asset_2.resources_to_self_consume = MockPayload(goods=3, energy=1)
        
        self.mock_block.assets = [mock_asset_1, mock_asset_2]
        
        # Reset cache to force recalculation
        self.resource_manager._resources_to_self_consume = None
        
        result = self.resource_manager.resources_to_self_consume
        
        self.assertEqual(result.goods, 8)  # 5 + 3
        self.assertEqual(result.energy, 3)  # 2 + 1
    
    def test_evaluate_resources_to_self_consume_no_assets(self):
        """Test evaluation when block has no assets"""
        self.mock_block.assets = []
        self.resource_manager._resources_to_self_consume = None
        
        result = self.resource_manager.resources_to_self_consume
        
        self.assertEqual(result.goods, 0)
        self.assertEqual(result.energy, 0)
    
    @patch('resource_manager_optimized.Resource_Manager.resources_to_self_consume', new_callable=PropertyMock)
    def test_evaluate_effective_resources_needed(self, mock_self_consume):
        """Test evaluation of effective resources needed based on autonomy"""
        # Setup mock return values
        mock_self_consume.return_value = MockPayload(goods=10, energy=5)
        
        # Set warehouse with different autonomy levels
        self.resource_manager._warehouse = MockPayload(goods=15, energy=25)  # autonomy: 1.5, 5.0
        self.resource_manager._resources_needed = None
        
        result = self.resource_manager.resources_needed
        
        # goods autonomy = 1.5 (< 2) -> full request (10)
        # energy autonomy = 5.0 (>= 5) -> 10% request (0.5)
        self.assertEqual(result.goods, 10)
        self.assertEqual(result.energy, 0.5)
    
    def test_get_autonomy_multiplier(self):
        """Test autonomy multiplier calculation"""
        # Test different autonomy ranges
        self.assertEqual(self.resource_manager._get_autonomy_multiplier(1.0), 1.0)   # < 2
        self.assertEqual(self.resource_manager._get_autonomy_multiplier(2.5), 0.5)   # 2-3
        self.assertEqual(self.resource_manager._get_autonomy_multiplier(4.0), 0.25)  # 3-5
        self.assertEqual(self.resource_manager._get_autonomy_multiplier(10.0), 0.1)  # > 5

    # === RESOURCE OPERATIONS TESTS ===
    
    @patch('resource_manager_optimized.Resource_Manager.resources_to_self_consume', new_callable=PropertyMock)
    def test_consume_successful(self, mock_self_consume):
        """Test successful resource consumption"""
        mock_self_consume.return_value = MockPayload(goods=10, energy=5)
        self.resource_manager._warehouse = MockPayload(goods=50, energy=25)
        
        result = self.resource_manager.consume()
        
        self.assertTrue(result)
        self.assertEqual(self.resource_manager._warehouse.goods, 40)  # 50 - 10
        self.assertEqual(self.resource_manager._warehouse.energy, 20)  # 25 - 5
    
    @patch('resource_manager_optimized.Resource_Manager.resources_to_self_consume', new_callable=PropertyMock)
    def test_consume_insufficient_resources(self, mock_self_consume):
        """Test consumption with insufficient resources in warehouse"""
        mock_self_consume.return_value = MockPayload(goods=100, energy=50)
        self.resource_manager._warehouse = MockPayload(goods=50, energy=25)
        
        result = self.resource_manager.consume()
        
        self.assertFalse(result)
        # Warehouse should remain unchanged
        self.assertEqual(self.resource_manager._warehouse.goods, 50)
        self.assertEqual(self.resource_manager._warehouse.energy, 25)
    
    def test_receive_successful(self):
        """Test successful resource reception"""
        initial_warehouse = self.resource_manager._warehouse.copy()
        payload = MockPayload(goods=20, energy=10)
        
        result = self.resource_manager.receive(payload)
        
        self.assertTrue(result)
        self.assertEqual(self.resource_manager._warehouse.goods, initial_warehouse.goods + 20)
        self.assertEqual(self.resource_manager._warehouse.energy, initial_warehouse.energy + 10)
    
    def test_receive_invalid_payload(self):
        """Test reception with invalid payload type"""
        result = self.resource_manager.receive("invalid_payload")
        
        self.assertFalse(result)
    
    def test_delivery_successful(self):
        """Test successful resource delivery to clients"""
        # Setup clients with resource managers and requests
        mock_client_rm_1 = MagicMock()
        mock_client_rm_1.resources_needed = MockPayload(goods=5, energy=2)
        mock_client_rm_1.receive.return_value = True
        self.mock_client_1.resource_manager = mock_client_rm_1
        
        mock_client_rm_2 = MagicMock()
        mock_client_rm_2.resources_needed = MockPayload(goods=10, energy=5)
        mock_client_rm_2.receive.return_value = True
        self.mock_client_2.resource_manager = mock_client_rm_2
        
        self.resource_manager._clients = {
            "client_1": self.mock_client_1,
            "client_2": self.mock_client_2
        }
        
        # Mock resources_to_self_consume to return non-empty payload
        with patch.object(self.resource_manager, 'resources_to_self_consume', 
                         return_value=MockPayload(goods=1, energy=1)):
            result = self.resource_manager.delivery()
        
        self.assertIsInstance(result, dict)
        self.assertIn("client_1", result)
        self.assertIn("client_2", result)
    
    def test_delivery_no_clients(self):
        """Test delivery with no clients"""
        self.resource_manager._clients = {}
        
        with patch.object(self.resource_manager, 'resources_to_self_consume', 
                         return_value=MockPayload(goods=1, energy=1)):
            result = self.resource_manager.delivery()
        
        self.assertEqual(result, {})

    # === VALIDATION TESTS ===
    
    def test_is_valid_block_true(self):
        """Test valid block validation"""
        self.assertTrue(self.resource_manager._is_valid_block(self.mock_block))
    
    def test_is_valid_block_false(self):
        """Test invalid block validation"""
        invalid_block = "not_a_block"
        self.assertFalse(self.resource_manager._is_valid_block(invalid_block))
    
    def test_validate_dict_param_valid(self):
        """Test dictionary parameter validation with valid input"""
        valid_dict = {"key1": self.mock_block}
        
        # Should not raise exception
        self.resource_manager._validate_dict_param("test_param", valid_dict)
    
    def test_validate_dict_param_invalid_type(self):
        """Test dictionary parameter validation with invalid type"""
        with self.assertRaises(TypeError):
            self.resource_manager._validate_dict_param("test_param", "not_a_dict")
    
    def test_validate_dict_param_invalid_keys(self):
        """Test dictionary parameter validation with invalid keys"""
        invalid_dict = {123: self.mock_block}
        
        with self.assertRaises(TypeError):
            self.resource_manager._validate_dict_param("test_param", invalid_dict)
    
    def test_validate_dict_param_invalid_values(self):
        """Test dictionary parameter validation with invalid values"""
        invalid_dict = {"key1": "not_a_block"}
        
        with self.assertRaises(ValueError):
            self.resource_manager._validate_dict_param("test_param", invalid_dict)
    
    def test_validate_param_valid(self):
        """Test single parameter validation with valid input"""
        result = self.resource_manager._validate_param("test_param", self.mock_warehouse, MockPayload)
        self.assertTrue(result)
    
    def test_validate_param_invalid_type(self):
        """Test single parameter validation with invalid type"""
        with self.assertRaises(TypeError):
            self.resource_manager._validate_param("test_param", "invalid", MockPayload)

    # === EDGE CASES AND ERROR HANDLING ===
    
    def test_cache_invalidation_on_warehouse_change(self):
        """Test that cache is invalidated when warehouse changes"""
        # First access to populate cache
        _ = self.resource_manager.resources_needed
        self.assertIsNotNone(self.resource_manager._resources_needed)
        
        # Change warehouse - should invalidate cache
        self.resource_manager.warehouse = MockPayload(goods=200, energy=100)
        self.assertIsNone(self.resource_manager._resources_needed)
    
    def test_cache_invalidation_on_block_change(self):
        """Test that cache is invalidated when block changes"""
        # First access to populate cache
        _ = self.resource_manager.resources_to_self_consume
        self.assertIsNotNone(self.resource_manager._resources_to_self_consume)
        
        # Change block - should invalidate cache
        new_block = MagicMock()
        new_block.__class__.__name__ = 'Block'
        self.resource_manager.block = new_block
        self.assertIsNone(self.resource_manager._resources_to_self_consume)
    
    def test_string_representations(self):
        """Test __repr__ and __str__ methods"""
        repr_str = repr(self.resource_manager)
        str_str = str(self.resource_manager)
        
        self.assertIn("Resource_Manager", repr_str)
        self.assertIn("test_block_1", repr_str)
        self.assertIn("Resource Manager", str_str)
        self.assertIn("test_block_1", str_str)
    
    @patch('resource_manager_optimized.logger')
    def test_logging_on_errors(self, mock_logger):
        """Test that errors are properly logged"""
        # Test consume with insufficient resources
        with patch.object(self.resource_manager, 'resources_to_self_consume', 
                         return_value=MockPayload(goods=1000, energy=500)):
            self.resource_manager.consume()
        
        # Verify warning was logged
        mock_logger.warning.assert_called()


class TestResourceManagerParams(unittest.TestCase):
    """Test cases for Resource_Manager_Params dataclass"""
    
    def test_params_initialization_default(self):
        """Test params initialization with default values"""
        params = Resource_Manager_Params()
        
        self.assertIsNone(params.clients)
        self.assertIsNone(params.server)
        self.assertIsNone(params.resources_needed)
        self.assertIsNone(params.warehouse)
    
    def test_params_initialization_with_values(self):
        """Test params initialization with provided values"""
        mock_clients = {"client_1": MagicMock()}
        mock_warehouse = MockPayload(goods=100)
        
        params = Resource_Manager_Params(
            clients=mock_clients,
            warehouse=mock_warehouse
        )
        
        self.assertEqual(params.clients, mock_clients)
        self.assertEqual(params.warehouse, mock_warehouse)


# === TEST SUITE CONFIGURATION ===

def create_test_suite():
    """Create a test suite with all test cases"""
    suite = unittest.TestSuite()
    
    # Add Resource_Manager tests
    suite.addTest(unittest.makeSuite(TestResourceManager))
    
    # Add Resource_Manager_Params tests
    suite.addTest(unittest.makeSuite(TestResourceManagerParams))
    
    return suite


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)