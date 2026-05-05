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
            self.assertAlmostEqual(block_item.priority, 0.1)  # 100 * 1.0 / ( 100 *10 (MAX_VALUE)) = 0.1
    
    def test_update_military_priorities(self):
        # Setup military block
        self.mock_military.combat_power.return_value = 100
        
        # Setup enemy block
        enemy_block = MagicMock(spec=Military)
        enemy_block.id = "enemy1"
        enemy_block.side = "Blue"
        enemy_block.get_military_category.return_value = "Ground_Base"
        enemy_block.is_military.return_value = True
        enemy_block.is_logistic.return_value = False
        enemy_block.is_civilian.return_value = False
        enemy_block.combat_power.return_value = 80
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
            invalid_weights = {"Ground_Base": {"attack": {"Ground_Base": 1.5}, "defense": {"Ground_Base": 0.1}}}
            self.region._validate_weight_priority_target(invalid_weights)
        
        with self.assertRaises(ValueError):
            self.region._validate_weight_priority_target({"Ground_Base": {"attack": {}, "defense": {}}})
        
        

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
    # get_region_intelligence_efficiency
    # ------------------------------------------------------------------
    def test_get_region_intelligence_efficiency_no_blocks_returns_zero(self):
        """get_region_intelligence_efficiency returns 0.0 when no military blocks for side."""
        self.assertAlmostEqual(self.region.get_region_intelligence_efficiency("Blue"), 0.0)

    def test_get_region_intelligence_efficiency_returns_mean(self):
        """get_region_intelligence_efficiency averages intelligence() across military blocks."""
        self.mil1.intelligence.return_value = 0.9
        self.mil2.intelligence.return_value = 0.5
        result = self.region.get_region_intelligence_efficiency("Red")
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
            mock_c2.assert_called_once_with(side="Red")
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


if __name__ == '__main__':
    unittest.main()