import unittest
from unittest.mock import MagicMock, patch, call
from typing import Dict, Optional
from dataclasses import dataclass
from Code.Dynamic_War_Manager.Source.Context.Region import Region
#from Code.Dynamic_War_Manager.Source.Block.Block import Block

# Import the class to test (adjust the import path as needed)
from Code.Dynamic_War_Manager.Source.Component.Resource_Manager import (
    Resource_Manager,
    Resource_Manager_Params,
    logger
)

# Mock classes to simulate dependencies
@dataclass
class MockPayload:
    goods: float = 0
    energy: float = 0
    hr: float = 0
    hc: float = 0
    hs: float = 0
    hb: float = 0
    
    def __add__(self, other):
        return MockPayload(
            goods=self.goods + other.goods if other.goods else self.goods,
            energy=self.energy + other.energy if other.energy else self.energy,
            hr=self.hr + other.hr if ( other.hr and other.hr > 0 ) else self.hr,
            hc=self.hc + other.hc if ( other.hc and other.hc > 0 ) else self.hc,
            hs=self.hs + other.hs if ( other.hs and other.hs > 0 ) else self.hs,
            hb=self.hb + other.hb if ( other.hb and other.hb > 0 ) else self.hb
        )
    
    def __sub__(self, other):
        return MockPayload(            
            goods=self.goods - other.goods if other.goods else self.goods,
            energy=self.energy - other.energy if other.energy else self.energy,
            hr=self.hr - other.hr if ( other.hr and other.hr > 0 ) else self.hr,
            hc=self.hc - other.hc if ( other.hc and other.hc > 0 ) else self.hc,
            hs=self.hs - other.hs if ( other.hs and other.hs > 0 ) else self.hs,
            hb=self.hb - other.hb if ( other.hb and other.hb > 0 ) else self.hb
        )
    
    def __mul__(self, factor: float):
        if not isinstance(factor, (int, float)):
            raise TypeError("Operand must be a number")   
        return MockPayload( 
            goods=self.goods * factor,
            energy=self.energy * factor,
            hr=self.hr * factor,
            hc=self.hc * factor,
            hs=self.hs * factor,
            hb=self.hb * factor
        )

    def __lt__(self, other):
        attributes = ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']
        for attr in attributes:
            if getattr(other, attr, None) and getattr(self, attr, None) < getattr(other, attr):
                return True
        return False


    def __le__(self, other):
        attributes = ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']
        for attr in attributes:
            if getattr(other, attr, None) and getattr(self, attr, None) <= getattr(other, attr):
                return True
        return False
    
    def copy(self):
        return MockPayload(
            goods=self.goods,
            energy=self.energy,
            hr=self.hr,
            hc=self.hc,
            hs=self.hs,
            hb=self.hb
        )
    
    def division(self, other):
        """Mock division operation that returns a new Payload with division results"""
        return MockPayload(
            goods=self.goods / other.goods if other.goods else float('inf'),
            energy=self.energy / other.energy if other.energy else float('inf'),
            hr=self.hr / other.hr if ( other.hr and other.hr > 0 ) else float('inf'),
            hc=self.hc / other.hc if ( other.hc and other.hc > 0 ) else float('inf'),
            hs=self.hs / other.hs if ( other.hs and other.hs > 0 ) else float('inf'),
            hb=self.hb / other.hb if ( other.hb and other.hb > 0 ) else float('inf')
        )
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def __repr__(self):
        return (f"Payload(goods={self.goods}, energy={self.energy}, hr={self.hr}, "
                f"hc={self.hc}, hs={self.hs}, hb={self.hb})")
    
    @property
    def __class__(self):
        class Payload: pass
        Payload.__name__ = 'Payload'
        return Payload

class MockBlock:
    def __init__(self, block_id: str, has_rm: bool = True):
        self.id = block_id
        self.region = MagicMock(spec= Region)
        self.assets = []
        self._resource_manager = None
        
        
        if has_rm:
            self._resource_manager = MagicMock()
            self._resource_manager.block = self
    
    @property
    def __class__(self):
        class Block: pass
        Block.__name__ = 'Block'
        return Block


    @property
    def resource_manager(self):
        return self._resource_manager
    
    def has_resource_manager(self):
        return self._resource_manager is not None
    
    def __repr__(self):
        return f"MockBlock(id={self.id})"

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        # Create a mock block
        self.mock_block = MockBlock("test_block")
        self.mock_block.region.blocks_priority = {"client1": 1.0, "client2": 0.5}
        
        # Create mock clients and servers
        self.mock_client1 = MockBlock("client1")
        self.mock_client2 = MockBlock("client2")
        self.mock_server1 = MockBlock("server1")
        
        # Create mock payloads
        self.mock_payload = MockPayload(goods=100, energy=50)
        self.mock_empty_payload = MockPayload()
        
        # Initialize Resource_Manager with mocks
        self.rm = Resource_Manager(
            block=self.mock_block,
            clients={"client1": self.mock_client1, "client2": self.mock_client2},
            server={"server1": self.mock_server1},
            warehouse=self.mock_payload.copy()
        )
        
        # Patch the logger to avoid actual logging during tests
         # Mock dell'intero logger invece dei singoli metodi
        self.logger_patcher = patch('Code.Dynamic_War_Manager.Source.Component.Resource_Manager.logger')
        self.mock_logger = self.logger_patcher.start()
        # Configura i metodi del logger che verranno usati
        self.mock_logger.info = MagicMock()
        self.mock_logger.warning = MagicMock()
        self.mock_logger.error = MagicMock()

        #self.logger_patcher = patch('Code.Dynamic_War_Manager.Source.Component.Resource_Manager.logger', autospec=True)
        #self.mock_logger_info = self.logger_patcher.start()
        #self.mock_logger_warning = self.logger_warning_patcher.start()
        #self.mock_logger_error = self.logger_error_patcher.start()
    
    def tearDown(self):
        self.logger_patcher.stop()
        #self.logger_warning_patcher.stop()
        #self.logger_error_patcher.stop()
    
    def test_initialization(self):
        """Test that the Resource_Manager initializes correctly"""
        self.assertEqual(self.rm.block, self.mock_block)
        self.assertEqual(len(self.rm.clients), 2)
        self.assertEqual(len(self.rm.server), 1)
        self.assertEqual(self.rm.warehouse.goods, 100)
        self.assertEqual(self.rm.warehouse.energy, 50)
    
    def test_property_validation(self):
        """Test property validation"""
        # Test block property validation
        with self.assertRaises(TypeError):
            self.rm.block = "invalid_block"
        
        # Test warehouse property validation
        with self.assertRaises(TypeError):
            self.rm.warehouse = "invalid_payload"
    
    def test_server_management(self):
        """Test server management methods"""
        # Test list_server_keys
        self.assertEqual(self.rm.list_server_keys(), ["server1"])
        
        # Test get_server
        self.assertEqual(self.rm.get_server("server1"), self.mock_server1)
        self.assertIsNone(self.rm.get_server("nonexistent"))
        
        # Test set_server
        new_server = MockBlock("new_server")
        self.rm.set_server("new_server", new_server)
        self.assertEqual(self.rm.get_server("new_server"), new_server)
        
        # Verify bidirectional reference was set
        new_server.resource_manager.set_client.assert_called_once_with("test_block", self.mock_block)
        
        # Test remove_server
        self.rm.remove_server("new_server")
        self.assertNotIn("new_server", self.rm.server)
        new_server.resource_manager.remove_client.assert_called_once_with("test_block")
    
    def test_client_management(self):
        """Test client management methods"""
        # Test list_client_keys
        self.assertEqual(sorted(self.rm.list_client_keys()), ["client1", "client2"])
        
        # Test get_client
        self.assertEqual(self.rm.get_client("client1"), self.mock_client1)
        self.assertIsNone(self.rm.get_client("nonexistent"))
        
        # Test set_client
        new_client = MockBlock("new_client")
        new_client.resource_manager.get_server.return_value = self.mock_block
        self.rm.set_client("new_client", new_client)
        self.assertEqual(self.rm.get_client("new_client"), new_client)
        
        # Test remove_client
        self.rm.remove_client("new_client")
        self.assertNotIn("new_client", self.rm.clients)
    
    def test_consume_resources(self):
        """Test resource consumption"""
        # Set up resources needed for consumption
        self.rm._resources_to_self_consume = MockPayload(goods=10, energy=5)
        
        # Test successful consumption
        result = self.rm.consume()
        self.assertTrue(result)
        self.assertEqual(self.rm.warehouse.goods, 90)
        self.assertEqual(self.rm.warehouse.energy, 45)
        self.mock_logger.info.assert_called()
        
        # Test insufficient resources
        self.rm._resources_to_self_consume = MockPayload(goods=1000, energy=500)
        result = self.rm.consume()
        self.assertFalse(result)
        self.mock_logger.warning.assert_called()
    
    def test_receive_resources(self):
        """Test receiving resources"""
        # Test successful reception
        payload = MockPayload(goods=10, energy=5)
        result = self.rm.receive(payload)
        self.assertTrue(result)
        self.assertEqual(self.rm.warehouse.goods, 110)
        self.assertEqual(self.rm.warehouse.energy, 55)
        self.mock_logger.info.assert_called()
        
        # Test invalid payload type
        #with self.assertRaises(TypeError):
        self.assertFalse(self.rm.receive("invalid_payload"))
    
    def test_delivery_to_clients(self):
        """Test resource delivery to clients"""
        # Set up client requests and priorities
        self.rm._resources_needed = MockPayload(goods=30, energy=15)  # For self
        self.rm._resources_to_self_consume = MockPayload(goods=20, energy=10)  # For self
        
        # Configure client resource managers
        self.mock_client1.resource_manager.resources_needed = MockPayload(goods=20, energy=10)
        self.mock_client2.resource_manager.resources_needed = MockPayload(goods=10, energy=5)
        
        # Mock the receive method for clients
        self.mock_client1.resource_manager.receive.return_value = True
        self.mock_client2.resource_manager.receive.return_value = True
        
        # Perform delivery
        results = self.rm.delivery()
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(results["client1"])
        self.assertTrue(results["client2"])
        
        # Verify resources were deducted from warehouse
        self.assertLess(self.rm.warehouse.goods, 100)
        self.assertLess(self.rm.warehouse.energy, 50)
        
        # Verify receive was called on clients
        self.mock_client1.resource_manager.receive.assert_called()
        self.mock_client2.resource_manager.receive.assert_called()
    
    def test_resource_calculations(self):     
        """Test resource calculation methods"""  
        # Test _evaluate_resources_to_self_consume
        self.mock_block.assets = [
            MagicMock(resources_to_self_consume=MockPayload(goods=5, energy=2)),
            MagicMock(resources_to_self_consume=MockPayload(goods=3, energy=1))
        ]
        result = self.rm._evaluate_resources_to_self_consume()
        self.assertEqual(result.goods, 8)
        self.assertEqual(result.energy, 3)
        
        # Test _evaluate_effective_resources_needed
        self.rm._resources_to_self_consume = MockPayload(goods=10, energy=5)
        self.rm._warehouse = MockPayload(goods=20, energy=10)  # Autonomy of 2
        result = self.rm._evaluate_effective_resources_needed()
        # Should be 50% of request (autonomy between 2-3)
        self.assertEqual(result.goods, 5)
        self.assertEqual(result.energy, 2.5)
        
        # Test _get_autonomy_multiplier
        self.assertEqual(self.rm._get_autonomy_multiplier(1.5), 1.0)  # <2
        self.assertEqual(self.rm._get_autonomy_multiplier(2.5), 0.5)  # 2-3
        self.assertEqual(self.rm._get_autonomy_multiplier(4.0), 0.25)  # 3-5
        self.assertEqual(self.rm._get_autonomy_multiplier(10.0), 0.1)  # >5vvvvvvvvv

    def test_production_calculations(self):
        """Test production calculation methods"""
        class MockPayload:
            def __init__(self, goods=0, energy=0, hr=0, hc=0, hs=0, hb=0):
                self.goods = goods
                self.energy = energy
                self.hr = hr
                self.hc = hc
                self.hs = hs
                self.hb = hb

        # Configura i mock degli asset
        self.mock_block.assets = [
            MagicMock(get_production=MagicMock(return_value=MockPayload(goods=25, energy=20, hr=15, hc=10, hs=5, hb=5))),
            MagicMock(get_production=MagicMock(return_value=MockPayload(goods=30, energy=25, hr=20, hc=15, hs=10, hb=5))),
        ]
        old_warehouse = self.rm.warehouse.copy()
        # Test _evaluate_production: update warehouse with production values
        results = self.rm.produce()
        self.assertEqual(self.rm.warehouse.goods, old_warehouse.goods + 55)
        self.assertEqual(self.rm.warehouse.energy, old_warehouse.energy + 45)
        self.assertEqual(self.rm.warehouse.hr, old_warehouse.hr + 35)
        self.assertEqual(self.rm.warehouse.hc, old_warehouse.hc + 25)
        self.assertEqual(self.rm.warehouse.hs, old_warehouse.hs + 15)
        self.assertEqual(self.rm.warehouse.hb, old_warehouse.hb + 10)        
        self.assertTrue(all(results.values()))  # Ensure all resources were produced successfully
        # update production values
        self.assertEqual(self.rm.actual_production.goods, 55)
        self.assertEqual(self.rm.actual_production.energy, 45)
        self.assertEqual(self.rm.actual_production.hr, 35)
        self.assertEqual(self.rm.actual_production.hc, 25)
        self.assertEqual(self.rm.actual_production.hs, 15)
        self.assertEqual(self.rm.actual_production.hb, 10) 
        self.assertEqual(self.rm.production_value, 1095/34) # ( 55*6 + 45*8 + 35*1 + 25*10 + 15*6 + 10*3 ) / ( 6 + 8 + 1 + 10 + 6 + 3 ) = 1095/34 (32.2059)

    
    def test_client_priority_evaluation(self):
        """Test client priority evaluation"""        
        priorities = self.rm._evaluate_clients_priority()
        self.assertEqual(priorities["client1"], 1.0)
        self.assertEqual(priorities["client2"], 0.5)
        
        # Test with no region
        self.rm.block.region = None
        priorities = self.rm._evaluate_clients_priority()
        self.assertEqual(priorities, {})
        self.mock_logger.warning.assert_called()
    
    def test_invalid_operations(self):
        """Test error handling for invalid operations"""
        # Test with no block set
        #empty_rm = Resource_Manager(block=None)
        with self.assertRaises(ValueError):
            empty_rm = Resource_Manager(block=None)
            #empty_rm.delivery()
        
        # Test with invalid client (no resource manager)
        invalid_client = MockBlock("invalid", has_rm=False)
        with self.assertRaises(ValueError):
            self.rm.set_client("invalid", invalid_client)
        
        # Test removing nonexistent server
        with self.assertRaises(KeyError):
            self.rm.remove_server("nonexistent")
    
    def test_repr_and_str(self):
        """Test string representation methods"""
        repr_str = repr(self.rm)
        self.assertIn("Resource_Manager", repr_str)
        self.assertIn("test_block", repr_str)
        
        str_str = str(self.rm)
        self.assertIn("Resource Manager", str_str)
        self.assertIn("test_block", str_str)

if __name__ == '__main__':
    unittest.main()