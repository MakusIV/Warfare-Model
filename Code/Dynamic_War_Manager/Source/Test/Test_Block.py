import unittest
import warnings
from unittest.mock import MagicMock, patch
from sympy import Point
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.State import State
from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.Context.Region import Region
from Code.Dynamic_War_Manager.Source.Component.Resource_Manager import Resource_Manager


class TestBlock(unittest.TestCase):

    # -----------------------------------------------------------------------
    # setUp
    # -----------------------------------------------------------------------
    def setUp(self):
        """Set up common test fixtures."""
        self.block = Block(
            name="Test Block",
            description="Test Description",
            side="Blue",
            category="Military",
            sub_category="Base",
            functionality="Defense",
            value=10
        )

        # Mock assets (spec=Asset lets MagicMock expose Asset's interface)
        self.mock_asset1 = MagicMock(spec=Asset)
        self.mock_asset1.cost = 50
        self.mock_asset1.efficiency = 0.8
        self.mock_asset1.balance_trade = 1.2
        self.mock_asset1.position = Point(10, 20)
        self.mock_asset1.state = MagicMock()
        self.mock_asset1.state.total_success_ratio = 0.7

        self.mock_asset2 = MagicMock(spec=Asset)
        self.mock_asset2.cost = 75
        self.mock_asset2.efficiency = 0.6
        self.mock_asset2.balance_trade = 0.9
        self.mock_asset2.position = Point(30, 40)
        self.mock_asset2.state = MagicMock()
        self.mock_asset2.state.total_success_ratio = 0.9

        # Mock event
        self.mock_event = MagicMock(spec=Event)
        self.mock_event.name = "Test Event"

        # Mock Region (class name check used inside _validate_params)
        self.mock_region = MagicMock()
        self.mock_region.__class__.__name__ = 'Region'

    # -----------------------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------------------
    def test_initialization_full(self):
        """Fully parameterised Block stores all attributes correctly."""
        self.assertEqual(self.block.name, "Test Block")
        self.assertEqual(self.block.description, "Test Description")
        self.assertEqual(self.block.side, "Blue")
        self.assertEqual(self.block.category, "Military")
        self.assertEqual(self.block.sub_category, "Base")
        self.assertEqual(self.block.functionality, "Defense")
        self.assertEqual(self.block.value, 10)
        self.assertIsInstance(self.block.id, str)
        self.assertIsInstance(self.block.state, State)
        self.assertIsInstance(self.block.resource_manager, Resource_Manager)

    def test_initialization_defaults(self):
        """Block() with no params uses default values without raising."""
        block = Block()
        self.assertIsInstance(block.name, str)   # setName generates a string
        self.assertEqual(block.description, "")
        self.assertEqual(block.side, "Neutral")
        self.assertEqual(block.category, "")
        self.assertEqual(block.sub_category, "")
        self.assertEqual(block.functionality, "")
        self.assertEqual(block.value, 1)          # MIN_VALUE default
        self.assertIsNone(block.region)
        self.assertIsInstance(block.state, State)
        self.assertIsInstance(block.resource_manager, Resource_Manager)

    def test_initialization_assets_empty(self):
        """Newly created block has an empty assets dict."""
        self.assertEqual(self.block.assets, {})

    def test_initialization_events_empty(self):
        """Newly created block has an empty events list."""
        self.assertEqual(self.block.events, [])

    # -----------------------------------------------------------------------
    # block_class / id properties
    # -----------------------------------------------------------------------
    def test_block_class_property(self):
        """block_class returns the class name 'Block'."""
        self.assertEqual(self.block.block_class, "Block")

    def test_id_property_is_string(self):
        """id is a non-empty string."""
        self.assertIsInstance(self.block.id, str)
        self.assertTrue(len(self.block.id) > 0)

    def test_id_setter_valid(self):
        """id setter accepts a valid string."""
        self.block.id = "custom_id"
        self.assertEqual(self.block.id, "custom_id")

    def test_id_setter_invalid_type(self):
        """id setter raises TypeError for non-string input."""
        with self.assertRaises(TypeError):
            self.block.id = 123

    # -----------------------------------------------------------------------
    # Property validation (setters)
    # -----------------------------------------------------------------------
    def test_name_setter_valid(self):
        """name setter accepts a valid string."""
        self.block.name = "New Name"
        self.assertEqual(self.block.name, "New Name")

    def test_name_setter_invalid_type(self):
        """name setter raises TypeError for non-string."""
        with self.assertRaises(TypeError):
            self.block.name = 123

    def test_description_setter_valid(self):
        """description setter accepts a valid string."""
        self.block.description = "New Description"
        self.assertEqual(self.block.description, "New Description")

    def test_description_setter_invalid_type(self):
        """description setter raises TypeError for non-string."""
        with self.assertRaises(TypeError):
            self.block.description = 42

    def test_side_setter_invalid_value(self):
        """side setter raises ValueError for unknown side."""
        with self.assertRaises(ValueError):
            self.block.side = "InvalidSide"

    def test_category_setter_invalid_value(self):
        """category setter raises ValueError for unknown category."""
        with self.assertRaises(ValueError):
            self.block.category = "UnknownCategory"

    def test_value_setter_invalid_type(self):
        """value setter raises TypeError for non-integer."""
        with self.assertRaises(TypeError):
            self.block.value = "invalid"

    def test_value_setter_above_max(self):
        """value setter raises ValueError above MAX_VALUE (10)."""
        with self.assertRaises(ValueError):
            self.block.value = 11

    def test_value_setter_below_min(self):
        """value setter raises ValueError below MIN_VALUE (1)."""
        with self.assertRaises(ValueError):
            self.block.value = 0

    def test_value_boundaries_valid(self):
        """value accepts MIN_VALUE (1) and MAX_VALUE (10)."""
        self.block.value = 1
        self.assertEqual(self.block.value, 1)
        self.block.value = 10
        self.assertEqual(self.block.value, 10)

    # -----------------------------------------------------------------------
    # state / resource_manager properties
    # -----------------------------------------------------------------------
    def test_state_property_type(self):
        """state property returns a State instance."""
        self.assertIsInstance(self.block.state, State)

    def test_state_setter_valid(self):
        """state setter accepts a State object."""
        new_state = State(object_type="Block", object_id="x")
        self.block.state = new_state
        self.assertIs(self.block.state, new_state)

    def test_state_setter_invalid_type(self):
        """state setter raises TypeError for non-State object."""
        with self.assertRaises(TypeError):
            self.block.state = "not a state"

    def test_resource_manager_property_type(self):
        """resource_manager property returns a Resource_Manager instance."""
        self.assertIsInstance(self.block.resource_manager, Resource_Manager)

    def test_has_resource_manager(self):
        """has_resource_manager returns True when resource_manager is set."""
        self.assertTrue(self.block.has_resource_manager())

    # -----------------------------------------------------------------------
    # Event management
    # -----------------------------------------------------------------------
    def test_add_event_valid(self):
        """add_event appends an Event to the list."""
        self.block.add_event(self.mock_event)
        self.assertEqual(len(self.block.events), 1)

    def test_add_event_invalid_type(self):
        """add_event raises TypeError for non-Event input."""
        with self.assertRaises(TypeError):
            self.block.add_event("not an event")

    def test_get_last_event(self):
        """get_last_event returns the most recently added event."""
        self.block.add_event(self.mock_event)
        self.assertIs(self.block.get_last_event(), self.mock_event)

    def test_get_last_event_empty(self):
        """get_last_event raises IndexError when no events exist."""
        with self.assertRaises(IndexError):
            self.block.get_last_event()

    def test_get_event_by_index(self):
        """get_event returns the event at the specified index."""
        self.block.add_event(self.mock_event)
        self.assertIs(self.block.get_event(0), self.mock_event)

    def test_get_event_index_out_of_range(self):
        """get_event raises IndexError for an out-of-range index."""
        with self.assertRaises(IndexError):
            self.block.get_event(0)

    def test_get_event_negative_index(self):
        """get_event raises IndexError for a negative index."""
        self.block.add_event(self.mock_event)
        with self.assertRaises(IndexError):
            self.block.get_event(-1)

    def test_get_event_invalid_type_index(self):
        """get_event raises TypeError for a non-integer index."""
        self.block.add_event(self.mock_event)
        with self.assertRaises(TypeError):
            self.block.get_event("zero")

    def test_remove_event_valid(self):
        """remove_event removes the specified event."""
        self.block.add_event(self.mock_event)
        self.block.remove_event(self.mock_event)
        self.assertEqual(len(self.block.events), 0)

    def test_remove_event_not_found(self):
        """remove_event raises ValueError if event is not in the list."""
        with self.assertRaises(ValueError):
            self.block.remove_event(self.mock_event)

    def test_remove_event_invalid_type(self):
        """remove_event raises TypeError for non-Event input."""
        with self.assertRaises(TypeError):
            self.block.remove_event("not an event")

    def test_events_setter_valid(self):
        """events setter accepts a list of Event objects."""
        event_list = [self.mock_event]
        self.block.events = event_list
        self.assertEqual(self.block.events, event_list)

    def test_events_setter_invalid_type(self):
        """events setter raises TypeError for non-list input."""
        with self.assertRaises(TypeError):
            self.block.events = self.mock_event

    def test_events_setter_invalid_element(self):
        """events setter raises ValueError if any element is not an Event."""
        with self.assertRaises(ValueError):
            self.block.events = ["not an event"]

    # -----------------------------------------------------------------------
    # Asset management
    # -----------------------------------------------------------------------
    def test_set_get_asset(self):
        """set_asset stores the asset; get_asset retrieves it by key."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.assertIs(self.block.get_asset("asset1"), self.mock_asset1)

    def test_set_asset_invalid_key_type(self):
        """set_asset raises TypeError for non-string key."""
        with self.assertRaises(TypeError):
            self.block.set_asset(123, self.mock_asset1)

    def test_set_asset_invalid_asset_type(self):
        """set_asset raises TypeError for a non-Asset value."""
        with self.assertRaises(TypeError):
            self.block.set_asset("key", "not_an_asset")

    def test_get_asset_missing_key(self):
        """get_asset returns None for an unknown key."""
        self.assertIsNone(self.block.get_asset("nonexistent"))

    def test_get_asset_invalid_key_type(self):
        """get_asset raises TypeError for a non-string key."""
        with self.assertRaises(TypeError):
            self.block.get_asset(42)

    def test_list_asset_keys(self):
        """list_asset_keys returns all registered keys."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        self.assertCountEqual(self.block.list_asset_keys(), ["asset1", "asset2"])

    def test_remove_asset_valid(self):
        """remove_asset deletes the asset from the dictionary."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.remove_asset("asset1")
        self.assertEqual(len(self.block.assets), 0)

    def test_remove_asset_missing_key(self):
        """remove_asset raises KeyError for an unknown key."""
        with self.assertRaises(KeyError):
            self.block.remove_asset("nonexistent")

    def test_assets_setter_valid(self):
        """assets setter accepts a dict of Asset objects."""
        assets_dict = {"asset1": self.mock_asset1}
        self.block.assets = assets_dict
        self.assertEqual(self.block.assets, assets_dict)

    def test_assets_setter_invalid_type(self):
        """assets setter raises TypeError for non-dict input."""
        with self.assertRaises(TypeError):
            self.block.assets = [self.mock_asset1]

    # -----------------------------------------------------------------------
    # Calculated properties
    # -----------------------------------------------------------------------
    def test_cost_with_assets(self):
        """cost returns the sum of all asset costs."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        self.assertEqual(self.block.cost, 125)  # 50 + 75

    def test_cost_empty_assets(self):
        """cost returns 0 when there are no assets."""
        self.assertEqual(self.block.cost, 0)

    def test_efficiency_with_assets(self):
        """efficiency returns the mean of asset efficiencies."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        self.assertAlmostEqual(self.block.efficiency, (0.8 + 0.6) / 2)

    def test_efficiency_empty_assets(self):
        """efficiency returns 0.0 when there are no assets."""
        self.assertAlmostEqual(self.block.efficiency, 0.0)

    def test_balance_trade_with_assets(self):
        """balance_trade returns the mean of asset balance_trade values."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        self.assertAlmostEqual(self.block.balance_trade, (1.2 + 0.9) / 2)

    def test_balance_trade_empty_assets(self):
        """balance_trade returns 0.0 when there are no assets."""
        self.assertAlmostEqual(self.block.balance_trade, 0.0)

    def test_position_with_assets(self):
        """position returns the centroid of asset positions."""
        self.block.set_asset("asset1", self.mock_asset1)
        self.block.set_asset("asset2", self.mock_asset2)
        self.assertEqual(self.block.position, Point(20, 30))  # mean of (10,20) and (30,40)

    def test_position_empty_assets(self):
        """position returns None when there are no assets."""
        self.assertIsNone(self.block.position)

    # -----------------------------------------------------------------------
    # morale property
    # -----------------------------------------------------------------------
    def test_morale_empty_assets(self):
        """morale returns 0.0 when there are no assets."""
        self.assertAlmostEqual(self.block.morale, 0.0)

    @patch('Code.Dynamic_War_Manager.Source.Block.Block.evaluateMorale', return_value=('H', 0.85))
    def test_morale_with_assets(self, mock_eval):
        """morale calls evaluateMorale with mean total_success_ratio and efficiency."""
        self.block.set_asset("asset1", self.mock_asset1)  # total_success_ratio=0.7, efficiency=0.8
        self.block.set_asset("asset2", self.mock_asset2)  # total_success_ratio=0.9, efficiency=0.6
        result = self.block.morale
        self.assertAlmostEqual(result, 0.85)
        mock_eval.assert_called_once()
        args = mock_eval.call_args[0]
        self.assertAlmostEqual(args[0], (0.7 + 0.9) / 2)  # mean success ratio
        self.assertAlmostEqual(args[1], (0.8 + 0.6) / 2)  # mean efficiency

    def test_morale_zero_success_ratio_returns_zero(self):
        """morale returns 0.0 when mean total_success_ratio is zero (guard against evaluateMorale ValueError)."""
        self.mock_asset1.state.total_success_ratio = 0.0
        self.block.set_asset("asset1", self.mock_asset1)
        self.assertAlmostEqual(self.block.morale, 0.0)

    def test_morale_zero_efficiency_returns_zero(self):
        """morale returns 0.0 when efficiency is zero (guard against evaluateMorale ValueError)."""
        self.mock_asset1.efficiency = 0.0
        self.mock_asset1.state.total_success_ratio = 0.8
        self.block.set_asset("asset1", self.mock_asset1)
        self.assertAlmostEqual(self.block.morale, 0.0)

    # -----------------------------------------------------------------------
    # Category checks
    # -----------------------------------------------------------------------
    def test_is_military_true(self):
        """is_military() returns True for Military category."""
        self.assertTrue(self.block.is_military())

    def test_is_logistic_false_when_military(self):
        """is_logistic() returns False when category is Military."""
        self.assertFalse(self.block.is_logistic())

    def test_is_civilian_false_when_military(self):
        """is_civilian() returns False when category is Military."""
        self.assertFalse(self.block.is_civilian())

    def test_is_logistic_true(self):
        """is_logistic() returns True after changing category to Logistic."""
        self.block.category = "Logistic"
        self.assertTrue(self.block.is_logistic())
        self.assertFalse(self.block.is_military())

    def test_is_civilian_true(self):
        """is_civilian() returns True after changing category to Civilian."""
        self.block.category = "Civilian"
        self.assertTrue(self.block.is_civilian())
        self.assertFalse(self.block.is_military())

    # -----------------------------------------------------------------------
    # enemy_side / is_enemy
    # -----------------------------------------------------------------------
    def test_enemy_side_blue(self):
        """enemy_side() returns 'Red' for a Blue block (emits DeprecationWarning)."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.block.enemy_side()
            self.assertEqual(result, "Red")
            self.assertTrue(any(issubclass(warning.category, DeprecationWarning) for warning in w))

    def test_enemy_side_red(self):
        """enemy_side() returns 'Blue' for a Red block."""
        self.block.side = "Red"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.assertEqual(self.block.enemy_side(), "Blue")

    def test_is_enemy_true(self):
        """is_enemy() returns True when the given side is the enemy of block's side."""
        self.assertEqual(self.block.side, "Blue")
        self.assertTrue(self.block.is_enemy("Red"))

    def test_is_enemy_false_same_side(self):
        """is_enemy() returns False for the same side."""
        self.assertFalse(self.block.is_enemy("Blue"))

    def test_is_enemy_false_neutral(self):
        """is_enemy() returns False for Neutral (enemy of Blue is Red)."""
        self.assertFalse(self.block.is_enemy("Neutral"))

    def test_is_enemy_red_block(self):
        """is_enemy() returns True for Blue when block side is Red."""
        self.block.side = "Red"
        self.assertTrue(self.block.is_enemy("Blue"))

    # -----------------------------------------------------------------------
    # Region association
    # -----------------------------------------------------------------------
    def test_region_setter_valid(self):
        """region setter accepts a Region-like object."""
        self.block.region = self.mock_region
        self.assertIs(self.block.region, self.mock_region)

    def test_region_setter_none(self):
        """region setter accepts None."""
        self.block.region = self.mock_region
        self.block.region = None
        self.assertIsNone(self.block.region)

    def test_region_setter_invalid_type(self):
        """region setter raises TypeError for non-Region objects."""
        with self.assertRaises(TypeError):
            self.block.region = "invalid region"

    # -----------------------------------------------------------------------
    # is_instance / check_instance_list
    # -----------------------------------------------------------------------
    def test_is_instance_block(self):
        """is_instance() returns True for Block objects."""
        other = Block(name="Other")
        self.assertTrue(self.block.is_instance(other))

    def test_is_instance_non_block(self):
        """is_instance() returns False for non-Block objects."""
        self.assertFalse(self.block.is_instance("not a block"))

    def test_check_instance_list_all_blocks(self):
        """check_instance_list() returns True when all elements are Blocks."""
        blocks = [Block(name=f"B{i}") for i in range(3)]
        self.assertTrue(self.block.check_instance_list(blocks))

    def test_check_instance_list_mixed(self):
        """check_instance_list() returns False if any element is not a Block."""
        self.assertFalse(self.block.check_instance_list([Block(name="B"), "not a block"]))

    def test_check_instance_list_empty(self):
        """check_instance_list() returns True for an empty list."""
        self.assertTrue(self.block.check_instance_list([]))

    def test_check_instance_list_non_list(self):
        """check_instance_list() returns False for non-list input."""
        self.assertFalse(self.block.check_instance_list("not a list"))

    # -----------------------------------------------------------------------
    # get_recognition_report
    # -----------------------------------------------------------------------
    def test_get_recognition_report_returns_none(self):
        """get_recognition_report() returns None (placeholder implementation)."""
        self.assertIsNone(self.block.get_recognition_report())

    # -----------------------------------------------------------------------
    # __repr__ / __str__
    # -----------------------------------------------------------------------
    def test_repr_contains_name_and_category(self):
        """__repr__ includes name, side and category."""
        r = repr(self.block)
        self.assertIn("Test Block", r)
        self.assertIn("Military", r)
        self.assertIn("Blue", r)

    def test_str_contains_name_and_side(self):
        """__str__ includes name and side."""
        s = str(self.block)
        self.assertIn("Test Block", s)
        self.assertIn("Blue", s)


if __name__ == '__main__':
    unittest.main()
