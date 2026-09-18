import unittest
from unittest.mock import MagicMock, patch
from sympy import Point2D
from typing import List, Dict, Optional, Tuple
from datetime import date, time
import inspect  # Aggiungi questo import

# Import the classes to test
from Code.Dynamic_War_Manager.Source.Context.Region import Region, BlockItem, BlockCategory
from Code.Dynamic_War_Manager.Source.Command.Command_Types import RegionInfoReport
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Context import Combat_Power_Estimation
from Code.Dynamic_War_Manager.Source.Logic import Tactical_Analysis
from Code.Dynamic_War_Manager.Source.Logic import Tactical_Evaluation
from Code.Dynamic_War_Manager.Source.Context.Context import (
    Ground_Vehicle_Asset_Type as gat,
    Air_Asset_Type as aat,
)
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from tabulate import tabulate

# Lightweight class stubs used only to set mock.__class__ for classification-loop dispatch,
# mirroring Test_Military.py -- Vehicle/Ship/Aircraft cannot be imported directly because they
# trigger a pre-existing circular import in the Aircraft->Aircraft_Weapon_Data chain.
_Vehicle  = type('Vehicle',  (), {})
_Ship     = type('Ship',     (), {})
_Aircraft = type('Aircraft', (), {})
_Structure = type('Structure', (), {})


from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Limes import Limes


def _make_combat_power_side_effect(value, task=None):
    """Mimics Military.combat_power's (force, action) contract: float if both `force` and
    `action` given, Dict[task, float] if only `force` given. If `task` is given, only that
    task carries `value` (every other task is 0.0) -- mirrors an asset whose combat power is
    concentrated on a single posture, which is what Region._calculate_priority's action-based
    selection (Fase 2) actually reads."""
    def _side_effect(force=None, action=None):
        if force and action:
            return value if task is None or action == task else 0.0
        if force:
            return {t: (value if task is None or t == task else 0.0) for t in Context.ACTION_TASKS[force]}
        return {f: {t: value for t in Context.ACTION_TASKS[f]} for f in Context.MILITARY_FORCES}
    return _side_effect


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
        self.mock_military.is_logistic.return_value = False
        self.mock_military.is_civilian.return_value = False
        self.mock_military.is_Ground_Base.return_value = True
        self.mock_military.position = Point2D(10, 10)
        self.mock_military.combat_power.return_value = 100
        self.mock_military.time2attack.return_value = 60
        self.mock_military.value = 1
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
        self.mock_production.is_civilian.return_value = False
        self.mock_production.position = Point2D(20, 20)
        self.mock_production.value = 1.0
        self.mock_production.category = 'Logistic'
        
        self.mock_urban = MagicMock(spec=Urban)
        self.mock_urban.id = "urban1"
        self.mock_urban.name = "Urban Area"
        self.mock_urban.side = "Blue"
        self.mock_urban.is_military.return_value = False
        self.mock_urban.is_logistic.return_value = False
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

    def test_get_normalized_priority_blocks(self):
        high_priority = self.region.get_normalized_priority_blocks(2, "Red", "highest")
        self.assertEqual(len(high_priority), 2)
        self.assertEqual(high_priority[0].priority, 1)
        
        low_priority = self.region.get_normalized_priority_blocks(1, "Red", "lowest")
        self.assertEqual(low_priority[0].priority, 0)
    
    def test_add_route(self):
        new_route = MagicMock(spec=Route)
        self.region.add_route("new_route", new_route)
        self.assertIn("new_route", self.region._routes)
    
    def test_get_route(self):
        route = self.region.get_route("military1", "prod1")
        self.assertEqual(route[0], self.mock_route)
        
        route = self.region.get_route("military1")
        self.assertEqual(route[0], self.mock_route)
    
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

            # Urban is a logistic block too (produces hr, affects morale — a legitimate
            # logistic/strategic-bombing target), so _is_logistic_block(urban1) is now True;
            # give it a harmless zero production value, this test only asserts on prod1.
            self.mock_urban.resource_manager = MagicMock()
            self.mock_urban.resource_manager.production_value.return_value = 0

            updated = self.region.update_logistic_priorities("Red")
            self.assertTrue(updated)
            
            block_item = self.region.get_block_by_id("prod1")
            self.assertAlmostEqual(block_item.priority, 0.1)  # 100 * 1.0 / ( 100 *10 (MAX_VALUE)) = 0.1
    
    @staticmethod
    def _combat_power_side_effect(value):
        """Mimics Military.combat_power's (force, action) contract: float if both given,
        Dict[task, float] if only force is given (each task set to `value`)."""
        def _side_effect(force=None, action=None):
            if force and action:
                return value
            if force:
                return {t: value for t in Context.ACTION_TASKS[force]}
            return {f: {t: value for t in Context.ACTION_TASKS[f]} for f in Context.MILITARY_FORCES}
        return _side_effect

    def test_update_military_priorities(self):
        # Setup military block
        self.mock_military.combat_power.side_effect = self._combat_power_side_effect(100)

        # Setup enemy block
        enemy_block = MagicMock(spec=Military)
        enemy_block.id = "enemy1"
        enemy_block.side = "Blue"
        enemy_block.get_military_category.return_value = "Ground_Base"
        enemy_block.is_military.return_value = True
        enemy_block.is_logistic.return_value = False
        enemy_block.is_civilian.return_value = False
        enemy_block.combat_power.side_effect = self._combat_power_side_effect(80)
        enemy_block.position = Point2D(50, 50)
        enemy_block.value = 1
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
            
            self.region.run_resource_management_cycle(side="Red")
            
            # Verify methods were called
            mock_log.assert_called_once_with(side="Red")
            mock_mil.assert_called_once_with(side="Red")
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
    
        
        

class TestGetBlocksByCriteriaMilCategory(unittest.TestCase):
    """Tests for the mil_category filter on get_blocks_by_criteria/get_sorted_priority_blocks/
    get_normalized_priority_blocks, and for the new get_priority_lists_by_mil_category."""

    def setUp(self):
        self.mock_regiment = MagicMock(spec=Military)
        self.mock_regiment.id = "regiment1"
        self.mock_regiment.side = "Red"
        self.mock_regiment.category = 'Military'
        self.mock_regiment.mil_category = 'Regiment'

        self.mock_regiment2 = MagicMock(spec=Military)
        self.mock_regiment2.id = "regiment2"
        self.mock_regiment2.side = "Red"
        self.mock_regiment2.category = 'Military'
        self.mock_regiment2.mil_category = 'Regiment'

        self.mock_airbase = MagicMock(spec=Military)
        self.mock_airbase.id = "airbase1"
        self.mock_airbase.side = "Red"
        self.mock_airbase.category = 'Military'
        self.mock_airbase.mil_category = 'Airbase'

        self.mock_blue_regiment = MagicMock(spec=Military)
        self.mock_blue_regiment.id = "regiment_blue"
        self.mock_blue_regiment.side = "Blue"
        self.mock_blue_regiment.category = 'Military'
        self.mock_blue_regiment.mil_category = 'Regiment'

        self.mock_production = MagicMock(spec=Production)
        self.mock_production.id = "prod1"
        self.mock_production.side = "Red"
        self.mock_production.category = 'Logistic'

        self.region = Region(
            name="Test Region",
            description="Test Description",
            blocks=[
                BlockItem(priority=0.9, block=self.mock_regiment),
                BlockItem(priority=0.5, block=self.mock_regiment2),
                BlockItem(priority=0.7, block=self.mock_airbase),
                BlockItem(priority=0.4, block=self.mock_blue_regiment),
                BlockItem(priority=0.2, block=self.mock_production),
            ],
        )

    def test_get_blocks_by_criteria_filters_by_mil_category(self):
        result = self.region.get_blocks_by_criteria(mil_category='Regiment')
        self.assertEqual({b.block.id for b in result}, {"regiment1", "regiment2", "regiment_blue"})

    def test_get_blocks_by_criteria_mil_category_excludes_non_military(self):
        result = self.region.get_blocks_by_criteria(mil_category='Regiment')
        self.assertNotIn(self.mock_production, [b.block for b in result])

    def test_get_blocks_by_criteria_invalid_mil_category_raises(self):
        with self.assertRaises(ValueError):
            self.region.get_blocks_by_criteria(mil_category='Not_A_Category')

    def test_get_blocks_by_criteria_mil_category_combines_with_side_and_category(self):
        result = self.region.get_blocks_by_criteria(side="Red", category="Military", mil_category='Regiment')
        self.assertEqual({b.block.id for b in result}, {"regiment1", "regiment2"})

    def test_get_sorted_priority_blocks_mil_category_forwarded(self):
        result = self.region.get_sorted_priority_blocks(count=10, side="Red", mil_category='Regiment')
        self.assertEqual([b.block.id for b in result], ["regiment1", "regiment2"])

    def test_get_normalized_priority_blocks_mil_category_forwarded(self):
        result = self.region.get_normalized_priority_blocks(count=10, side="Red", mil_category='Regiment')
        self.assertEqual([b.block.id for b in result], ["regiment1", "regiment2"])
        self.assertEqual(result[0].priority, 1)
        self.assertEqual(result[1].priority, 0)

    def test_get_normalized_priority_blocks_single_block_group_returns_block_priority(self):
        result = self.region.get_normalized_priority_blocks(count=10, side="Red", mil_category='Airbase')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].priority, 0.7)


class TestGetPriorityListsByMilCategory(unittest.TestCase):
    def setUp(self):
        self.mock_regiment = MagicMock(spec=Military)
        self.mock_regiment.id = "regiment1"
        self.mock_regiment.side = "Red"
        self.mock_regiment.category = 'Military'
        self.mock_regiment.mil_category = 'Regiment'

        self.mock_regiment2 = MagicMock(spec=Military)
        self.mock_regiment2.id = "regiment2"
        self.mock_regiment2.side = "Red"
        self.mock_regiment2.category = 'Military'
        self.mock_regiment2.mil_category = 'Regiment'

        self.mock_airbase = MagicMock(spec=Military)
        self.mock_airbase.id = "airbase1"
        self.mock_airbase.side = "Red"
        self.mock_airbase.category = 'Military'
        self.mock_airbase.mil_category = 'Airbase'

        self.region = Region(
            name="Test Region",
            description="Test Description",
            blocks=[
                BlockItem(priority=0.9, block=self.mock_regiment),
                BlockItem(priority=0.5, block=self.mock_regiment2),
                BlockItem(priority=0.7, block=self.mock_airbase),
            ],
        )

    def test_returns_one_list_per_present_mil_category(self):
        result = self.region.get_priority_lists_by_mil_category(side="Red")
        self.assertEqual(set(result.keys()), {"Regiment", "Airbase"})
        self.assertEqual([b.block.id for b in result["Regiment"]], ["regiment1", "regiment2"])
        self.assertEqual([b.block.id for b in result["Airbase"]], ["airbase1"])

    def test_skips_categories_not_present(self):
        result = self.region.get_priority_lists_by_mil_category(side="Red")
        self.assertNotIn("Naval_Group", result)
        self.assertNotIn("Farp", result)

    def test_empty_region_returns_empty_dict(self):
        empty_region = Region(name="Empty", description="Empty", blocks=[])
        result = empty_region.get_priority_lists_by_mil_category(side="Red")
        self.assertEqual(result, {})

    def test_side_with_no_military_blocks_returns_empty_dict(self):
        result = self.region.get_priority_lists_by_mil_category(side="Blue")
        self.assertEqual(result, {})

    def test_invalid_side_raises(self):
        with self.assertRaises(ValueError):
            self.region.get_priority_lists_by_mil_category(side="Green")

    def test_sort_by_lowest_and_highest(self):
        highest = self.region.get_priority_lists_by_mil_category(side="Red", sort_by="highest")
        lowest = self.region.get_priority_lists_by_mil_category(side="Red", sort_by="lowest")
        self.assertEqual([b.block.id for b in highest["Regiment"]], ["regiment1", "regiment2"])
        self.assertEqual([b.block.id for b in lowest["Regiment"]], ["regiment2", "regiment1"])


class TestRegionRoutes(unittest.TestCase):
    """Tests for get_route, get_shortest_route, get_safest_route, get_shortest_and_safest_route."""

    def setUp(self):
        self.route_short_dangerous = MagicMock(spec=Route)
        self.route_short_dangerous.length.return_value = 50.0
        self.route_short_dangerous.max_danger_level.return_value = 8
        self.route_short_dangerous.min_danger_level.return_value = 4

        self.route_long_safe = MagicMock(spec=Route)
        self.route_long_safe.length.return_value = 150.0
        self.route_long_safe.max_danger_level.return_value = 2
        self.route_long_safe.min_danger_level.return_value = 1

        self.region = Region(
            name="Route Test Region",
            routes={
                "blockA,blockB": self.route_short_dangerous,
                "blockA-blockB": self.route_long_safe,
            }
        )

    # --- get_route ---

    def test_get_route_returns_all_matching(self):
        """get_route returns all routes involving both block IDs."""
        routes = self.region.get_route("blockA", "blockB")
        self.assertIsNotNone(routes)
        self.assertEqual(len(routes), 2)
        self.assertIn(self.route_short_dangerous, routes)
        self.assertIn(self.route_long_safe, routes)

    def test_get_route_source_only_returns_all(self):
        """get_route with only source ID returns all routes involving that block."""
        routes = self.region.get_route("blockA")
        self.assertIsNotNone(routes)
        self.assertEqual(len(routes), 2)

    def test_get_route_no_match_returns_none(self):
        """get_route returns None when no routes match."""
        result = self.region.get_route("unknown", "block")
        self.assertIsNone(result)

    def test_get_route_invalid_same_ids_raises(self):
        """get_route raises ValueError when source and target IDs are identical."""
        with self.assertRaises(ValueError):
            self.region.get_route("blockA", "blockA")

    def test_get_route_invalid_type_raises(self):
        """get_route raises TypeError for non-string block_id."""
        with self.assertRaises(TypeError):
            self.region.get_route(123)

    # --- get_shortest_route ---

    def test_get_shortest_route_returns_shorter(self):
        """get_shortest_route returns the route with the minimum length."""
        route = self.region.get_shortest_route("blockA", "blockB")
        self.assertEqual(route, self.route_short_dangerous)

    def test_get_shortest_route_single_match(self):
        """get_shortest_route returns the only route when there is one match."""
        region = Region(
            name="Single Route Region",
            routes={"blockA,blockB": self.route_short_dangerous}
        )
        route = region.get_shortest_route("blockA", "blockB")
        self.assertEqual(route, self.route_short_dangerous)

    def test_get_shortest_route_no_match_returns_none(self):
        """get_shortest_route returns None when no routes match."""
        result = self.region.get_shortest_route("unknown", "block")
        self.assertIsNone(result)

    # --- get_safest_route ---

    def test_get_safest_route_returns_min_max_danger(self):
        """get_safest_route returns the route with the lowest max_danger_level."""
        route = self.region.get_safest_route("blockA", "blockB")
        self.assertEqual(route, self.route_long_safe)

    def test_get_safest_route_no_match_returns_none(self):
        """get_safest_route returns None when no routes match."""
        result = self.region.get_safest_route("unknown", "block")
        self.assertIsNone(result)

    def test_get_safest_route_equal_danger_returns_first_min(self):
        """get_safest_route handles equal danger levels without error."""
        self.route_short_dangerous.max_danger_level.return_value = 2
        route = self.region.get_safest_route("blockA", "blockB")
        self.assertIn(route, [self.route_short_dangerous, self.route_long_safe])

    # --- get_shortest_and_safest_route ---

    def test_get_shortest_and_safest_route_prefers_lower_min_danger(self):
        """get_shortest_and_safest_route sorts by (min_danger_level, length); picks safest first."""
        # route_long_safe: min_danger=1, route_short_dangerous: min_danger=4
        route = self.region.get_shortest_and_safest_route("blockA", "blockB")
        self.assertEqual(route, self.route_long_safe)

    def test_get_shortest_and_safest_route_tie_on_danger_picks_shorter(self):
        """When min_danger_level ties, get_shortest_and_safest_route picks the shorter route."""
        self.route_short_dangerous.min_danger_level.return_value = 1
        self.route_long_safe.min_danger_level.return_value = 1
        route = self.region.get_shortest_and_safest_route("blockA", "blockB")
        self.assertEqual(route, self.route_short_dangerous)

    def test_get_shortest_and_safest_route_no_match_returns_none(self):
        """get_shortest_and_safest_route returns None when no routes match."""
        result = self.region.get_shortest_and_safest_route("unknown", "block")
        self.assertIsNone(result)

    def test_get_shortest_and_safest_route_single_match(self):
        """get_shortest_and_safest_route returns the only route when there is one match."""
        region = Region(
            name="Single Route Region",
            routes={"blockA,blockB": self.route_long_safe}
        )
        route = region.get_shortest_and_safest_route("blockA", "blockB")
        self.assertEqual(route, self.route_long_safe)


class TestRegionMetrics(unittest.TestCase):
    """Tests for _get_region_average_metric, get_block_morale,
    the five region-level metric functions and get_recon_reports."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _make_military(self, id_: str, side: str = "Red") -> MagicMock:
        m = MagicMock(spec=Military)
        m.id = id_
        m.name = f"Base_{id_}"
        m.side = side
        m.category = "Military"
        m.region = None
        return m

    def _make_logistic(self, id_: str, side: str = "Red") -> MagicMock:
        m = MagicMock(spec=Production)
        m.id = id_
        m.name = f"Prod_{id_}"
        m.side = side
        m.category = "Logistic"
        m.region = None
        return m

    def setUp(self):
        self.mil1 = self._make_military("mil1")
        self.mil2 = self._make_military("mil2")
        self.prod1 = self._make_logistic("prod1")

        self.region = Region(
            name="Metric Region",
            blocks=[
                BlockItem(priority=1.0, block=self.mil1),
                BlockItem(priority=0.5, block=self.mil2),
                BlockItem(priority=0.3, block=self.prod1),
            ]
        )

    # ------------------------------------------------------------------
    # _get_region_average_metric
    # ------------------------------------------------------------------
    def test_helper_invalid_side_raises(self):
        """_get_region_average_metric raises ValueError for an unknown side."""
        with self.assertRaises(ValueError):
            self.region._get_region_average_metric("Unknown", BlockCategory.MILITARY.value, "morale")

    def test_helper_no_matching_blocks_returns_zero(self):
        """Returns 0.0 when no blocks match the requested category."""
        result = self.region._get_region_average_metric("Blue", BlockCategory.MILITARY.value, "morale")
        self.assertAlmostEqual(result, 0.0)

    def test_helper_method_not_found_returns_zero(self):
        """Returns 0.0 when the requested method does not exist on any block."""
        result = self.region._get_region_average_metric("Red", BlockCategory.MILITARY.value, "_nonexistent_xyz_")
        self.assertAlmostEqual(result, 0.0)

    def test_helper_method_returns_non_numeric_ignored(self):
        """Returns 0.0 when every block method returns a non-numeric value."""
        self.mil1.morale.return_value = "not a number"
        self.mil2.morale.return_value = None
        result = self.region._get_region_average_metric("Red", BlockCategory.MILITARY.value, "morale")
        self.assertAlmostEqual(result, 0.0)

    def test_helper_single_block_returns_its_value(self):
        """Returns the single block's value when only one block contributes."""
        self.mil1.morale.return_value = 0.8
        self.mil2.morale.return_value = "bad"
        result = self.region._get_region_average_metric("Red", BlockCategory.MILITARY.value, "morale")
        self.assertAlmostEqual(result, 0.8)

    def test_helper_multiple_blocks_returns_mean(self):
        """Returns the arithmetic mean across all valid blocks."""
        self.mil1.morale.return_value = 0.6
        self.mil2.morale.return_value = 0.4
        result = self.region._get_region_average_metric("Red", BlockCategory.MILITARY.value, "morale")
        self.assertAlmostEqual(result, 0.5)

    def test_helper_filters_by_category_military_vs_logistic(self):
        """Logistic blocks are excluded when category=MILITARY, and vice versa."""
        self.prod1.morale = MagicMock(return_value=1.0)
        self.mil1.morale.return_value = 0.4
        self.mil2.morale.return_value = 0.6
        # logistic block's morale must NOT be included
        result = self.region._get_region_average_metric("Red", BlockCategory.MILITARY.value, "morale")
        self.assertAlmostEqual(result, 0.5)

    # ------------------------------------------------------------------
    # get_block_morale
    # ------------------------------------------------------------------
    def test_get_block_morale_valid_block_returns_float(self):
        """get_block_morale returns the morale float for a known block."""
        self.mil1.morale.return_value = 0.75
        result = self.region.get_block_morale("mil1")
        self.assertAlmostEqual(result, 0.75)

    def test_get_block_morale_unknown_id_returns_none(self):
        """get_block_morale returns None when the block ID is not in the region."""
        self.assertIsNone(self.region.get_block_morale("does_not_exist"))

    def test_get_block_morale_non_numeric_returns_none(self):
        """get_block_morale returns None when morale() returns a non-numeric value."""
        self.mil1.morale.return_value = "invalid"
        self.assertIsNone(self.region.get_block_morale("mil1"))

    # ------------------------------------------------------------------
    # get_region_morale
    # ------------------------------------------------------------------
    def test_get_region_morale_invalid_side_raises(self):
        """get_region_morale raises ValueError for an unknown side."""
        with self.assertRaises(ValueError):
            self.region.get_region_morale("InvalidSide")

    def test_get_region_morale_no_military_blocks_returns_zero(self):
        """get_region_morale returns 0.0 when no military blocks exist for the side."""
        self.assertAlmostEqual(self.region.get_region_morale("Blue"), 0.0)

    def test_get_region_morale_returns_mean_of_military_blocks(self):
        """get_region_morale returns the mean morale across military blocks."""
        self.mil1.morale.return_value = 0.9
        self.mil2.morale.return_value = 0.7
        result = self.region.get_region_morale("Red")
        self.assertAlmostEqual(result, 0.8)

    # ------------------------------------------------------------------
    # get_region_recon_efficiency
    # ------------------------------------------------------------------
    def test_get_region_recon_efficiency_no_blocks_returns_zero(self):
        """get_region_recon_efficiency returns 0.0 when no military blocks for side."""
        self.assertAlmostEqual(self.region.get_region_recon_efficiency("Blue"), 0.0)

    def test_get_region_recon_efficiency_returns_mean(self):
        """get_region_recon_efficiency averages get_recon_efficiency across military blocks."""
        self.mil1.get_recon_efficiency.return_value = 0.8
        self.mil2.get_recon_efficiency.return_value = 0.4
        result = self.region.get_region_recon_efficiency("Red")
        self.assertAlmostEqual(result, 0.6)

    # ------------------------------------------------------------------
    # get_region_resource_efficiency
    # ------------------------------------------------------------------
    def test_get_region_resource_efficiency_no_logistic_returns_zero(self):
        """get_region_resource_efficiency returns 0.0 when no logistic blocks for side."""
        self.assertAlmostEqual(self.region.get_region_resource_efficiency("Blue"), 0.0)

    def test_get_region_resource_efficiency_uses_logistic_blocks_only(self):
        """get_region_resource_efficiency averages resource_efficiency on logistic blocks."""
        # resource_efficiency is not yet on Production spec — assign explicitly
        self.prod1.resource_efficiency = MagicMock(return_value=0.7)
        # military blocks should be excluded even if they expose the method
        self.mil1.resource_efficiency = MagicMock(return_value=1.0)
        result = self.region.get_region_resource_efficiency("Red")
        self.assertAlmostEqual(result, 0.7)

    # ------------------------------------------------------------------
    # get_c2_efficiency
    # ------------------------------------------------------------------
    def test_get_c2_efficiency_no_blocks_returns_zero(self):
        """get_c2_efficiency returns 0.0 when no military blocks for the side."""
        self.assertAlmostEqual(self.region.get_c2_efficiency("Blue"), 0.0)

    def test_get_c2_efficiency_returns_mean(self):
        """get_c2_efficiency averages get_c2_efficiency() across military blocks."""
        self.mil1.get_c2_efficiency.return_value = 0.6
        self.mil2.get_c2_efficiency.return_value = 0.8
        result = self.region.get_c2_efficiency("Red")
        self.assertAlmostEqual(result, 0.7)

    # ------------------------------------------------------------------
    # get_recon_reports
    # ------------------------------------------------------------------
    def test_get_recon_reports_invalid_side_raises(self):
        """get_recon_reports raises ValueError for an unknown side."""
        with self.assertRaises(ValueError):
            self.region.get_recon_reports("InvalidSide")

    def test_get_recon_reports_no_military_blocks_returns_empty_list(self):
        """get_recon_reports returns [] when no military blocks exist for the side."""
        result = self.region.get_recon_reports("Blue")
        self.assertEqual(result, [])

    def test_get_recon_reports_single_block_dict_report(self):
        """get_recon_reports returns a list with one entry for a single valid report."""
        report = {"position": None, "state": "Healtful"}
        self.mil1.get_recognition_report.return_value = report
        self.mil2.get_recognition_report.return_value = report
        result = self.region.get_recon_reports("Red")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn(report, result)

    def test_get_recon_reports_non_dict_report_excluded(self):
        """get_recon_reports excludes blocks whose get_recognition_report returns non-dict."""
        self.mil1.get_recognition_report.return_value = {"position": None}
        self.mil2.get_recognition_report.return_value = None   # non-dict → excluded
        result = self.region.get_recon_reports("Red")
        self.assertEqual(len(result), 1)
        self.assertIn({"position": None}, result)

    def test_get_recon_reports_all_non_dict_returns_empty(self):
        """get_recon_reports returns [] when every block returns a non-dict report."""
        self.mil1.get_recognition_report.return_value = "bad"
        self.mil2.get_recognition_report.return_value = 42
        result = self.region.get_recon_reports("Red")
        self.assertEqual(result, [])

    def test_get_recon_reports_passes_c2_efficiency_to_each_block(self):
        """get_recon_reports passes the region c2 efficiency to every block's get_recognition_report."""
        c2_value = 0.65
        report = {"position": None}
        self.mil1.get_recognition_report.return_value = report
        self.mil2.get_recognition_report.return_value = report

        with patch.object(self.region, 'get_c2_efficiency', return_value=c2_value) as mock_c2:
            self.region.get_recon_reports("Red")
            mock_c2.assert_called_once_with(side="Blue")
            self.mil1.get_recognition_report.assert_called_once_with(c2_value)
            self.mil2.get_recognition_report.assert_called_once_with(c2_value)

    def test_get_recon_reports_c2_computed_once_not_per_block(self):
        """get_c2_efficiency is called exactly once, not once per block."""
        self.mil1.get_recognition_report.return_value = {"k": "v"}
        self.mil2.get_recognition_report.return_value = {"k": "v"}

        with patch.object(self.region, 'get_c2_efficiency', return_value=0.5) as mock_c2:
            self.region.get_recon_reports("Red")
            self.assertEqual(mock_c2.call_count, 1)

    def test_get_recon_reports_result_is_list_of_dicts(self):
        """get_recon_reports always returns a list, and every element is a dict."""
        self.mil1.get_recognition_report.return_value = {"a": 1}
        self.mil2.get_recognition_report.return_value = {"b": 2}
        result = self.region.get_recon_reports("Red")
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, dict)


class TestUpdateMilitaryPrioritiesUseRecon(unittest.TestCase):
    """Fase 5: Region.update_military_priorities(use_recon=True) -- guard Neutral, uno sweep di
    ricognizione per chiamata, snapshot valido solo dentro lo sweep."""

    def setUp(self):
        self.region = Region(name="UMP UseRecon Region")

    def test_neutral_side_is_noop(self):
        with patch.object(self.region, 'get_blocks_by_criteria') as mock_gbc, \
             patch.object(self.region, 'get_recon_reports') as mock_grr, \
             patch.object(Tactical_Analysis, 'build_recon_cp_snapshot') as mock_snapshot:
            self.region.update_military_priorities('Neutral', use_recon=True)
        mock_gbc.assert_not_called()
        mock_grr.assert_not_called()
        mock_snapshot.assert_not_called()

    def test_recon_sweep_called_once_regardless_of_friendly_block_count(self):
        mil1 = MagicMock(spec=Military)
        mil1.id = 'm1'
        mil1.side = 'Blue'
        mil1.category = 'Military'
        mil1.get_military_category.return_value = 'Ground_Base'
        mil1.combat_power.side_effect = _make_combat_power_side_effect(1.0)
        mil1.is_Ground_Base.return_value = True
        mil1.is_Naval_Base.return_value = False
        mil1.is_Air_Base.return_value = False
        mil1.position = None

        mil2 = MagicMock(spec=Military)
        mil2.id = 'm2'
        mil2.side = 'Blue'
        mil2.category = 'Military'
        mil2.get_military_category.return_value = 'Ground_Base'
        mil2.combat_power.side_effect = _make_combat_power_side_effect(1.0)
        mil2.is_Ground_Base.return_value = True
        mil2.is_Naval_Base.return_value = False
        mil2.is_Air_Base.return_value = False
        mil2.position = None

        self.region._add_block_item(BlockItem(priority=0.0, block=mil1))
        self.region._add_block_item(BlockItem(priority=0.0, block=mil2))

        with patch.object(self.region, 'get_recon_reports', return_value=[]) as mock_grr, \
             patch.object(Tactical_Analysis, 'build_recon_cp_snapshot', return_value={}) as mock_snapshot:
            self.region.update_military_priorities('Blue', use_recon=True)
        mock_grr.assert_called_once_with('Red')
        mock_snapshot.assert_called_once_with([])

    def test_snapshot_cleared_after_sweep_completes(self):
        with patch.object(Tactical_Analysis, 'build_recon_cp_snapshot', return_value={'x': 1.0}):
            self.region.update_military_priorities('Blue', use_recon=True)
        self.assertIsNone(self.region._recon_cp_snapshot)

    def test_snapshot_cleared_even_if_sweep_raises(self):
        mil1 = MagicMock(spec=Military)
        mil1.id = 'm1'
        mil1.side = 'Blue'
        mil1.category = 'Military'
        mil1.get_military_category.side_effect = RuntimeError("boom")
        self.region._add_block_item(BlockItem(priority=0.0, block=mil1))

        with patch.object(Tactical_Analysis, 'build_recon_cp_snapshot', return_value={'x': 1.0}):
            with self.assertRaises(RuntimeError):
                self.region.update_military_priorities('Blue', use_recon=True)
        self.assertIsNone(self.region._recon_cp_snapshot)

    def test_use_recon_false_never_builds_snapshot(self):
        with patch.object(Tactical_Analysis, 'build_recon_cp_snapshot') as mock_snapshot:
            self.region.update_military_priorities('Blue', use_recon=False)
        mock_snapshot.assert_not_called()
        self.assertIsNone(self.region._recon_cp_snapshot)


class TestUpdateMilitaryPrioritiesFase6Characterization(unittest.TestCase):
    """Test di caratterizzazione numerica per la Fase 6 del refactoring (estrazione di
    select_weight/calculate_priority/calc_surface_priority/calc_air_priority in
    Tactical_Evaluation.py, richiesto esplicitamente dall'utente).

    A differenza degli altri test (che verificano una singola funzione isolata, spesso con
    combat_power/route mockati ad-hoc), questo esercita l'intera catena end-to-end così come la
    percorre update_military_priorities: Tactical_Evaluation.calc_attack_priority -> select_weight +
    calc_surface_priority -> calculate_priority, con un valore atteso calcolato a mano dalla
    stessa formula documentata, per bloccare un errore di "cablaggio" fra le funzioni appena
    separate (parametro dimenticato, ordine sbagliato, ecc.) che un test unitario sulla singola
    funzione non potrebbe rivelare.

    Scenario: un solo blocco amico (side Blue) con potenza di 'Attack'=5.0, un solo blocco nemico
    (side Red) con potenza di 'Defense'=2.0 e 'Maintain'=3.0 (deve vincere Maintain, v.
    calculate_priority), nessuna route registrata (get_shortest_route -> None, si usa
    time2attack), tti mockato a 2.0, target_value=5, peso di dottrina di default
    (Ground_Base/attack/Ground_Base = 0.7), nessun altro alleato (defense_priority=0.0).

    Calcolo atteso:
        combat_power_ratio = clip(target_cp/combat_power, 0.1, 10.0) = clip(3.0/5.0, ...) = 0.6
        attack_priority     = (target_value * combat_power_ratio * range_ratio * weight) / tti
                             = (5 * 0.6 * 1.0 * 0.7) / 2.0 = 1.05
        overall_priority    = attack_priority * attack_weight + defense_priority * (1-attack_weight)
                             = 1.05 * 0.5 + 0.0 * 0.5 = 0.525
    """

    def setUp(self):
        self.region = Region(name="Fase6 Characterization Region")

    def _military_block(self, block_id, side, cp_task, cp_value, position):
        m = MagicMock(spec=Military)
        m.id = block_id
        m.side = side
        m.category = 'Military'
        m.get_military_category.return_value = 'Ground_Base'
        m.is_Ground_Base.return_value = True
        m.is_Naval_Base.return_value = False
        m.is_Air_Base.return_value = False
        m.position = position
        m.time2attack.return_value = 2.0
        m.artillery_in_range.return_value = {'target_within_med_range': False, 'med_range_ratio': 1.0}
        m.value = 5
        return m

    def test_end_to_end_priority_matches_hand_computed_value(self):
        friendly = self._military_block('friendly1', 'Blue', 'Attack', 5.0, Point2D(0, 0))
        friendly.combat_power.side_effect = _make_combat_power_side_effect(5.0, 'Attack')

        enemy = self._military_block('enemy1', 'Red', None, None, Point2D(10, 10))
        enemy.combat_power.side_effect = lambda force=None, action=None: (
            {'Defense': 2.0, 'Maintain': 3.0}.get(action, 0.0) if action else {}
        )

        self.region._add_block_item(BlockItem(priority=0.0, block=friendly))
        self.region._add_block_item(BlockItem(priority=0.0, block=enemy))

        self.region.update_military_priorities('Blue')

        block_item = self.region.get_block_by_id('friendly1')
        self.assertAlmostEqual(block_item.priority, 0.525)


# ─────────────────────────────────────────────────────────────────────────────
#  DIAGNOSTIC TABLE — Tactical_Evaluation.target_affinity() across target-composition scenarios
# ─────────────────────────────────────────────────────────────────────────────
# Analogo ai blocchi diagnostici di Aircraft_Data.py (#TEST, incondizionato) e
# Vehicle_Data.py (STAMPA, disattivabile): NON è un test automatico (nessuna
# asserzione) -- serve per ispezionare a colpo d'occhio se target_affinity si
# comporta in modo sensato al variare della composizione del bersaglio, a parità
# di flotta aerea attaccante (F-14A Tomcat + F-16CM Block 50). Disattivato di
# default (STAMPA_TARGET_AFFINITY = False): per vederla, impostare a True ed
# eseguire il file direttamente (non tramite `unittest discover`, che comunque
# non attiva mai questo blocco essendo gated dal flag).

STAMPA_TARGET_AFFINITY = False

_DIAG_TANK_PHYSICAL = {'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48}   # -> big
_DIAG_SAM_PHYSICAL  = {'length': 5, 'width': 2.5, 'height': 2,   'weight': 18}   # -> small


def _diag_mock_ground_vehicle(asset_type, physical):
    """Asset Vehicle mockato per il bersaglio (classificazione/dimensione reali)."""
    m = MagicMock()
    m.__class__ = _Vehicle
    m.asset_type = asset_type
    m.category = None
    m.is_operative.return_value = True
    m.get_physical_characteristics.return_value = physical
    return m


def _diag_mock_parked_aircraft(role):
    """Asset Aircraft mockato per il bersaglio (es. velivoli a terra su un aeroporto nemico)."""
    m = MagicMock()
    m.__class__ = _Aircraft
    m.asset_type = role
    m.category = role
    m.is_operative.return_value = True
    return m


def _diag_mock_attacking_aircraft(model):
    """Asset Aircraft mockato per la flotta attaccante (serve .model per _operative_aircraft_by_model)."""
    m = MagicMock()
    m.__class__ = _Aircraft
    m.model = model
    m.asset_type = aat.FIGHTER.value
    m.is_operative.return_value = True
    m.combat_power = MagicMock(return_value=10.0)
    return m


def print_target_affinity_scenarios():
    """Stampa una tabella diagnostica di Tactical_Evaluation.target_affinity() su 4 scenari a
    composizione del bersaglio diversa, a parità di flotta aerea attaccante.

    priorità finale = Tactical_Evaluation.calculate_priority() con target civile, value=5, weight=2, tti=2,
    range_ratio=1 -- base_priority senza affinità = (5*1*2)/2 = 5.0, quindi
    priorità finale = 5.0 * target_affinity: isolare l'effetto moltiplicativo
    dell'affinità senza la complessità del ramo militare (combat_power_ratio) o di
    time2attack/posizioni reali, non pertinenti a questo controllo.
    """
    airbase = Military(
        mil_category=Context.MILITARY_CATEGORY["Air_Base"][1], name="Diag Airbase", side="Blue"
    )
    airbase._assets = {
        'f14': _diag_mock_attacking_aircraft('F-14A Tomcat'),
        'f16': _diag_mock_attacking_aircraft('F-16CM Block 50'),
    }

    scenarios = {
        '100% Armored (3 Tank)': {
            'v1': _diag_mock_ground_vehicle(gat.TANK.value, _DIAG_TANK_PHYSICAL),
            'v2': _diag_mock_ground_vehicle(gat.TANK.value, _DIAG_TANK_PHYSICAL),
            'v3': _diag_mock_ground_vehicle(gat.TANK.value, _DIAG_TANK_PHYSICAL),
        },
        '100% Air_Defense (3 SAM_Small)': {
            's1': _diag_mock_ground_vehicle(gat.SAM_SMALL.value, _DIAG_SAM_PHYSICAL),
            's2': _diag_mock_ground_vehicle(gat.SAM_SMALL.value, _DIAG_SAM_PHYSICAL),
            's3': _diag_mock_ground_vehicle(gat.SAM_SMALL.value, _DIAG_SAM_PHYSICAL),
        },
        'Misto Armored + Air_Defense (2+2)': {
            'v1': _diag_mock_ground_vehicle(gat.TANK.value, _DIAG_TANK_PHYSICAL),
            'v2': _diag_mock_ground_vehicle(gat.TANK.value, _DIAG_TANK_PHYSICAL),
            's1': _diag_mock_ground_vehicle(gat.SAM_SMALL.value, _DIAG_SAM_PHYSICAL),
            's2': _diag_mock_ground_vehicle(gat.SAM_SMALL.value, _DIAG_SAM_PHYSICAL),
        },
        '100% Aircraft (3 caccia a terra)': {
            'a1': _diag_mock_parked_aircraft(aat.FIGHTER.value),
            'a2': _diag_mock_parked_aircraft(aat.FIGHTER.value),
            'a3': _diag_mock_parked_aircraft(aat.FIGHTER.value),
        },
    }

    _WEIGHT, _TTI, _VALUE = 2.0, 2.0, 5  # base_priority senza affinità = 5.0

    rows = []
    for name, assets in scenarios.items():
        target = Block(
            name="Diag Target", description="", side="Red", category="Civilian",
            sub_category="", functionality="", value=_VALUE,
        )
        target._assets = assets

        affinity = Tactical_Evaluation.target_affinity(airbase, target)
        priority = Tactical_Evaluation.calculate_priority(
            block=airbase, target_block=target, weight=_WEIGHT,
            time_to_intercept=_TTI, range_ratio=1.0, target_affinity=affinity,
        )
        rows.append([name, f"{affinity:.3f}", f"{priority:.3f}"])

    print("\n--- Tactical_Evaluation.target_affinity() diagnostic (base_priority senza affinità = 5.0) ---")
    print(tabulate(rows, headers=["Scenario (composizione target)", "target_affinity", "priorità finale"], tablefmt="grid"))
    print()


if STAMPA_TARGET_AFFINITY:
    print_target_affinity_scenarios()


class TestRegionLimes(unittest.TestCase):
    """v. project_c2_hierarchy_design.md (TASK 2 / Fase A): limes diventa una property pubblica."""

    def test_limes_defaults_to_empty_list(self):
        region = Region(name="Limes Region")
        self.assertEqual(region.limes, [])

    def test_limes_returns_constructor_value(self):
        mock_limes = [MagicMock(spec=Limes), MagicMock(spec=Limes)]
        region = Region(name="Limes Region", limes=mock_limes)
        self.assertEqual(region.limes, mock_limes)

    def test_limes_is_a_defensive_copy(self):
        mock_limes = [MagicMock(spec=Limes)]
        region = Region(name="Limes Region", limes=mock_limes)
        region.limes.append(MagicMock(spec=Limes))
        self.assertEqual(len(region.limes), 1)


class TestRegionBuildInfoReport(unittest.TestCase):
    """v. project_c2_hierarchy_design.md (TASK 2 / Fase A) e Command.Command_Types.RegionInfoReport.

    build_info_report è puro orchestratore: nessuna logica propria, solo assemblaggio di metodi
    Region già testati altrove. I test qui verificano l'assemblaggio, non ricalcolano i valori
    attesi di ogni sotto-metodo (già coperti dalle rispettive suite dedicate).
    """

    def setUp(self):
        self.region = Region(name="Info Report Region")
        self.date = date(2026, 9, 18)
        self.time = time(12, 0)

    def test_invalid_side_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.region.build_info_report(side="Purple", date=self.date, time=self.time)

    def test_report_assembles_every_field_from_region_methods(self):
        report = self.region.build_info_report(side="Blue", date=self.date, time=self.time)

        self.assertIsInstance(report, RegionInfoReport)
        self.assertEqual(report.region_name, "Info Report Region")
        self.assertEqual(report.side, "Blue")
        self.assertEqual(report.date, self.date)
        self.assertEqual(report.time, self.time)
        self.assertEqual(report.priority, self.region.get_priority_lists_by_mil_category(side="Blue"))
        self.assertEqual(report.meteo, self.region.get_meteorological_reports(side="Blue", date=self.date, time=self.time))
        self.assertEqual(report.block_state, self.region.get_recon_reports(side="Blue"))
        self.assertEqual(report.routes, self.region.routes)
        self.assertEqual(report.limes, self.region.limes)
        self.assertEqual(report.logistic_center, self.region.calc_strategic_logistic_center(side="Blue"))
        self.assertEqual(report.combat_power_center, self.region.calc_combat_power_center(side="Blue"))
        # assertIs, non assertEqual: Payload.__eq__ ha un bug pre-esistente, non in scope qui,
        # per cui due Payload entrambi a zero risultano "diversi" (ogni `getattr(other, attr)`
        # è falsy, quindi il ciclo non trova mai un match -- v. Payload.py:127-133). Non
        # documentato altrove: scoperto verificando questo test. calc_total_warehouse/
        # calc_total_production sono @lru_cache: stesso `side`, stesso oggetto restituito, quindi
        # l'identità resta comunque l'asserzione corretta a prescindere dal bug.
        self.assertIs(report.warehouse, self.region.calc_total_warehouse(side="Blue"))
        self.assertIs(report.production, self.region.calc_total_production(side="Blue"))
        self.assertEqual(report.morale, self.region.get_region_morale(side="Blue"))

    def test_report_reflects_actual_meteo_conditions(self):
        night_report = self.region.build_info_report(side="Blue", date=self.date, time=time(2, 0))
        self.assertEqual(night_report.meteo, [{'day': False, 'night': True, 'adverse_weather': False}])


if __name__ == '__main__':
    unittest.main()