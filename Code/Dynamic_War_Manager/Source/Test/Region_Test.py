import unittest
from unittest.mock import MagicMock, patch
from sympy import Point2D
from typing import List, Dict, Optional, Tuple
import inspect  # Aggiungi questo import

# Import the classes to test
from Code.Dynamic_War_Manager.Source.Context.Region import Region, BlockItem, BlockCategory
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload


from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Limes import Limes

class TestBlockItem(unittest.TestCase):
    def test_block_item_creation(self):
        mock_block = MagicMock(spec=Block)
        block_item = BlockItem(priority=0.5, block=mock_block)
        self.assertEqual(block_item.priority, 0.5)
        self.assertEqual(block_item.block, mock_block)
    
    def test_block_item_validation(self):
        mock_block = MagicMock(spec=Block)
        with self.assertRaises(TypeError):
            BlockItem(priority="invalid", block=mock_block)
        with self.assertRaises(ValueError):
            BlockItem(priority=-1.0, block=mock_block)

class TestRegion(unittest.TestCase):
    def setUp(self):
        # Create mock blocks
        self.mock_military = MagicMock(spec=Military)
        self.mock_military.id = "military1"
        self.mock_military.name = "Military Base"
        self.mock_military.side = "Red"
        self.mock_military.get_military_category.return_value = "Ground_Base"
        self.mock_military.is_military.return_value = True
        self.mock_military.is_Ground_Base.return_value = True
        self.mock_military.position = Point2D(10, 10)
        self.mock_military.combat_power.return_value = 100
        self.mock_military.time2attack.return_value = 60
        self.mock_military.artillery_in_range.return_value = {
            "target_within_med_range": True,
            "med_range_ratio": 0.8
        }
        self.mock_military.category = 'Military'

        self.mock_production = MagicMock(spec=Production)
        self.mock_production.id = "prod1"
        self.mock_production.name = "Production Facility"
        self.mock_production.side = "Red"
        self.mock_production.is_military.return_value = False
        self.mock_production.is_logistic.return_value = True
        self.mock_production.position = Point2D(20, 20)
        self.mock_production.value = 1.0
        self.mock_production.category = 'Logistic'
        
        self.mock_urban = MagicMock(spec=Urban)
        self.mock_urban.id = "urban1"
        self.mock_urban.name = "Urban Area"
        self.mock_urban.side = "Blue"
        self.mock_urban.is_military.return_value = False
        self.mock_urban.is_civilian.return_value = True
        self.mock_urban.position = Point2D(30, 30)
        self.mock_urban.value = 0.5
        self.mock_urban.category = 'Civilian'
        
        # Create mock routes
        self.mock_route = MagicMock(spec=Route)
        self.mock_route.length.return_value = 100
        
        # Create region with mock blocks
        self.region = Region(
            name="Test Region",
            description="Test Description",
            blocks=[
                BlockItem(priority=0.8, block=self.mock_military),
                BlockItem(priority=0.6, block=self.mock_production),
                BlockItem(priority=0.3, block=self.mock_urban)
            ],
            routes={
                "military1,prod1": self.mock_route,
                "military1,urban1": self.mock_route
            }
        )
    
    def test_region_initialization(self):
        self.assertEqual(self.region.name, "Test Region")
        self.assertEqual(self.region.description, "Test Description")
        self.assertEqual(len(self.region.blocks), 3)
        self.assertEqual(len(self.region.routes), 2)
    
    def test_add_block(self):
        new_block = MagicMock(spec=Block)
        new_block.id = "new_block"
        new_block.region = None
        self.region.add_block(new_block, priority=0.5)
        self.assertIn("new_block", self.region._blocks)
    
    def test_remove_block(self):
        result = self.region.remove_block("military1")
        self.assertTrue(result)
        self.assertNotIn("military1", self.region._blocks)
    
    def test_get_block_by_id(self):
        block_item = self.region.get_block_by_id("military1")
        self.assertEqual(block_item.block, self.mock_military)
    
    def test_get_blocks_by_criteria(self):
        # Test side filter
        red_blocks = self.region.get_blocks_by_criteria(side="Red")
        self.assertEqual(len(red_blocks), 2)
        
        # Test category filter
        military_blocks = self.region.get_blocks_by_criteria(category="Military")
        self.assertEqual(len(military_blocks), 1)
        
        # Test class filter
        production_blocks = self.region.get_blocks_by_criteria(block_class=Production)
        self.assertEqual(len(production_blocks), 1)
    
    def test_get_sorted_priority_blocks(self):
        high_priority = self.region.get_sorted_priority_blocks(2, "Red", "highest")
        self.assertEqual(len(high_priority), 2)
        self.assertEqual(high_priority[0].priority, 0.8)
        
        low_priority = self.region.get_sorted_priority_blocks(1, "Red", "lowest")
        self.assertEqual(low_priority[0].priority, 0.6)
    
    def test_add_route(self):
        new_route = MagicMock(spec=Route)
        self.region.add_route("new_route", new_route)
        self.assertIn("new_route", self.region._routes)
    
    def test_get_route(self):
        route = self.region.get_route("military1", "prod1")
        self.assertEqual(route, self.mock_route)
        
        route = self.region.get_route("military1")
        self.assertEqual(route, self.mock_route)
    
    def test_calc_strategic_logistic_center(self):
        # Setup production block with position and priority
        self.mock_production.position = Point2D(10, 20)        
        block_item = self.region.get_block_by_id("prod1")
        block_item.priority = 1.0
        
        center = self.region.calc_strategic_logistic_center("Red")
        self.assertEqual(center, Point2D(10, 20))
    
    def test_calc_combat_power_center(self):
        # Setup military block with combat power
        self.mock_military.combat_power.return_value = 100
        self.mock_military.position = Point2D(10, 10)
        
        centers = self.region.calc_combat_power_center("Red")
        self.assertIn("ground", centers)
        self.assertIsInstance(centers["ground"]["Attack"], Point2D)
        self.assertIsInstance(centers["ground"]["Maintain"], Point2D)
        self.assertIsInstance(centers["ground"]["Defense"], Point2D)
    
    
    def test_calc_total_warehouse(self):
        # Setup production block with resource manager
        self.mock_production.resource_manager = MagicMock()
        
        # Create a real Payload instance
        real_payload = Payload(goods=100)# Configurazione CORRETTA per una property
        type(self.mock_production.resource_manager).warehouse = real_payload
        # Disabilita resource_manager per military1
        self.mock_military.resource_manager = None
        
        # Chiama con il case corretto ("Red")
        total = self.region.calc_total_warehouse("Red")
        
        # Verifica
        self.assertEqual(total.goods, 100)
       

    def test_calc_total_production(self):
        # Setup production block with resource manager
        self.mock_production.resource_manager = MagicMock()
        
        # Create a proper Payload instance instead of MagicMock        
        mock_payload = Payload(goods=50)  # Usa il costruttore reale di Payload        
        self.mock_production.resource_manager.actual_production.return_value = mock_payload
        total = self.region.calc_total_production("Red")
        
        # Verify
        self.assertEqual(total.goods, 50)
        self.mock_production.resource_manager.actual_production.assert_called_once()
    
    def test_calc_production_values(self):
        # Setup production block with production value
        self.mock_production.resource_manager = MagicMock()
        self.mock_production.resource_manager.production_value.return_value = 100
        
        values = self.region.calc_production_values("Red")
        self.assertEqual(values["production"], 100)
    
    def test_update_logistic_priorities(self):
        # Setup production values
        with patch.object(self.region, 'calc_production_values', return_value={
            "production": 100, "storage": 50, "transport": 30, "urban": 20, "military": 10, "total": 210
        }):
            # Setup production block
            self.mock_production.resource_manager = MagicMock()
            self.mock_production.resource_manager.production_value.return_value = 100
            self.mock_production.value = 1.0
            
            updated = self.region.update_logistic_priorities("Red")
            self.assertTrue(updated)
            
            block_item = self.region.get_block_by_id("prod1")
            self.assertAlmostEqual(block_item.priority, 1.0)  # 100 * 1.0 / 100
    
    def test_update_military_priorities(self):
        # Setup military block
        self.mock_military.combat_power.return_value = 100
        
        # Setup enemy block
        enemy_block = MagicMock(spec=Military)
        enemy_block.id = "enemy1"
        enemy_block.side = "Blue"
        enemy_block.get_military_category.return_value = "Ground_Base"
        enemy_block.is_military.return_value = True
        enemy_block.combat_power.return_value = 80
        enemy_block.position = Point2D(50, 50)
        
        # Add enemy block to region
        self.region._add_block_item(BlockItem(priority=0.5, block=enemy_block))
        
        # Test priority update
        self.region.update_military_priorities("Red")
        block_item = self.region.get_block_by_id("military1")
        self.assertGreater(block_item.priority, 0)
    
    def test_run_resource_management_cycle(self):
        # Setup production block with resource manager
        self.mock_production.resource_manager = MagicMock()
        self.mock_production.resource_manager.run_resource_management_cycle.return_value = True
        
        # Test cycle run
        with patch.object(self.region, 'update_logistic_priorities', return_value=True) as mock_log, \
             patch.object(self.region, 'update_military_priorities') as mock_mil:
            
            self.region.run_resource_management_cycle("Red")
            
            # Verify methods were called
            mock_log.assert_called_once_with("Red")
            mock_mil.assert_called_once_with("Red")
            self.mock_production.resource_manager.run_resource_management_cycle.assert_called_once()
    
    def test_invalidate_caches(self):
        """Test the cache invalidation mechanism"""
        # Create mock functions that preserve cache_clear
        mock_functions = {}
        
        # List of all cached methods to test
        cached_methods = [
            'get_blocks_by_criteria',
            'get_route',
            'calc_strategic_logistic_center',
            'calc_combat_power_center',
            'calc_total_warehouse',
            'calc_total_production',
            'calc_production_values',
            '_calc_attack_priority',
            '_calc_defense_priority'
        ]

        # Create a tracker for calls
        calls = {name: 0 for name in cached_methods}

        # Replace each method with a mock that tracks calls to cache_clear
        for name in cached_methods:
            original = getattr(self.region, name)
            
            def make_mock(original, name):
                def mock_cache_clear():
                    calls[name] += 1
                    return original.cache_clear()
                
                mock = MagicMock()
                mock.cache_clear = mock_cache_clear
                return mock
            
            mock_func = make_mock(original, name)
            setattr(self.region, name, mock_func)

        # Call the method under test
        self.region._invalidate_caches()

        # Verify all caches were cleared
        for name in cached_methods:
            self.assertEqual(calls[name], 1, f"{name} cache not cleared")
    
    def test_validate_weight_priority_target(self):
        valid_weights = {
            "Ground_Base": {
                "attack": {"Ground_Base": 0.7, "Naval_Base": 0.0},
                "defense": {"Ground_Base": 0.1, "Naval_Base": 0.1}
            }
        }
        
        # Test valid structure
        self.region._validate_weight_priority_target(valid_weights)
        
        # Test invalid structures
        with self.assertRaises(TypeError):
            self.region._validate_weight_priority_target("invalid")
        
        with self.assertRaises(TypeError):
            self.region._validate_weight_priority_target({"Ground_Base": "invalid"})
        
        with self.assertRaises(ValueError):
            self.region._validate_weight_priority_target({"Ground_Base": {"attack": {}, "defense": {}}})
        
        with self.assertRaises(ValueError):
            invalid_weights = {"Ground_Base": {"attack": {"Ground_Base": 1.5}, "defense": {"Ground_Base": 0.1}}}
            self.region._validate_weight_priority_target(invalid_weights)

if __name__ == '__main__':
    unittest.main()