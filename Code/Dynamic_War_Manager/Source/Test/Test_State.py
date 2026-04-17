import unittest
from Code.Dynamic_War_Manager.Source.DataType.State import State, StateCategory, HEALTH_LEVEL

# ---------------------------------------------------------------------------
# Soglie di stato (health int [0-100], normalizzato /100 per il confronto)
#
#   HEALTHFUL  : health > 80          →  health ∈ [81, 100]
#   DAMAGED    : 50 < health <= 80    →  health ∈ [51,  80]
#   CRITICAL   : 15 < health <= 50    →  health ∈ [16,  50]
#   DESTROYED  : health <= 15         →  health ∈ [ 0,  15]
# ---------------------------------------------------------------------------


class TestState(unittest.TestCase):

    # -----------------------------------------------------------------------
    # setUp
    # -----------------------------------------------------------------------
    def setUp(self):
        """Set up common test fixture (health=100, success_ratio=None)."""
        self.state = State(object_type="Block", object_id="block_001")

    # -----------------------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------------------
    def test_initialization_defaults(self):
        """Default init: health=100 → HEALTHFUL, success_ratio=None."""
        state = State(object_type="Block", object_id="block_001")
        self.assertEqual(state._object_type, "Block")
        self.assertEqual(state._object_id, "block_001")
        self.assertEqual(state.health, 100)
        self.assertIsNone(state.success_ratio)
        self.assertEqual(state.state_value, StateCategory.HEALTHFUL.value)

    def test_initialization_with_health(self):
        """Custom health and object_type are stored correctly."""
        state = State(object_type="Asset", object_id="asset_001", health=50)
        self.assertEqual(state.health, 50)
        self.assertEqual(state._object_type, "Asset")
        self.assertEqual(state._object_id, "asset_001")

    def test_initialization_with_success_ratio_none(self):
        """success_ratio=None is accepted and stored as None."""
        state = State(object_type="Block", object_id="b1", success_ratio=None)
        self.assertIsNone(state.success_ratio)

    def test_initialization_state_value_is_string(self):
        """_state_value must be a str from the first update(), not an Enum member."""
        state = State(object_type="Block", object_id="b1")
        self.assertIsInstance(state._state_value, str)

    # -----------------------------------------------------------------------
    # Validation errors at init
    # -----------------------------------------------------------------------
    def test_init_invalid_object_type_empty(self):
        """Empty object_type must raise ValueError."""
        with self.assertRaises(ValueError):
            State(object_type="", object_id="b1")

    def test_init_invalid_object_type_not_string(self):
        """Non-string object_type must raise ValueError."""
        with self.assertRaises((ValueError, TypeError)):
            State(object_type=123, object_id="b1")

    def test_init_invalid_object_id_empty(self):
        """Empty object_id must raise ValueError."""
        with self.assertRaises(ValueError):
            State(object_type="Block", object_id="")

    def test_init_invalid_object_id_not_string(self):
        """Non-string object_id must raise ValueError."""
        with self.assertRaises((ValueError, TypeError)):
            State(object_type="Block", object_id=None)

    def test_init_invalid_health_negative(self):
        """Negative health must raise TypeError (validated in _validate_init_params)."""
        with self.assertRaises(TypeError):
            State(object_type="Block", object_id="b1", health=-1)

    def test_init_invalid_health_float(self):
        """Float health must raise TypeError."""
        with self.assertRaises(TypeError):
            State(object_type="Block", object_id="b1", health=0.5)

    # -----------------------------------------------------------------------
    # health property
    # -----------------------------------------------------------------------
    def test_health_setter_valid(self):
        """health setter accepts any non-negative int."""
        self.state.health = 80
        self.assertEqual(self.state.health, 80)

    def test_health_setter_zero(self):
        """health=0 is a valid boundary value."""
        self.state.health = 0
        self.assertEqual(self.state.health, 0)

    def test_health_setter_invalid_type_float(self):
        """health setter raises TypeError for float."""
        with self.assertRaises(TypeError):
            self.state.health = 0.5

    def test_health_setter_invalid_type_string(self):
        """health setter raises TypeError for string."""
        with self.assertRaises(TypeError):
            self.state.health = "100"

    def test_health_setter_negative(self):
        """Negative health raises ValueError."""
        with self.assertRaises(ValueError):
            self.state.health = -1

    def test_health_setter_triggers_update(self):
        """Setting health automatically refreshes state_value."""
        self.state.health = 90   # HEALTHFUL
        self.assertEqual(self.state.state_value, StateCategory.HEALTHFUL.value)
        self.state.health = 70   # DAMAGED
        self.assertEqual(self.state.state_value, StateCategory.DAMAGED.value)
        self.state.health = 30   # CRITICAL
        self.assertEqual(self.state.state_value, StateCategory.CRITICAL.value)
        self.state.health = 10   # DESTROYED
        self.assertEqual(self.state.state_value, StateCategory.DESTROYED.value)

    # -----------------------------------------------------------------------
    # success_ratio property
    # -----------------------------------------------------------------------
    def test_success_ratio_setter_valid_float(self):
        """success_ratio setter accepts a non-negative float."""
        self.state.success_ratio = 0.75
        self.assertEqual(self.state.success_ratio, 0.75)

    def test_success_ratio_setter_zero(self):
        """success_ratio=0.0 is a valid boundary value."""
        self.state.success_ratio = 0.0
        self.assertEqual(self.state.success_ratio, 0.0)

    def test_success_ratio_setter_invalid_type_int(self):
        """success_ratio setter raises TypeError for int."""
        with self.assertRaises(TypeError):
            self.state.success_ratio = 1

    def test_success_ratio_setter_negative(self):
        """Negative success_ratio raises ValueError."""
        with self.assertRaises(ValueError):
            self.state.success_ratio = -0.1

    # -----------------------------------------------------------------------
    # state_value setter
    # -----------------------------------------------------------------------
    def test_state_value_setter_valid(self):
        """state_value setter accepts any valid StateCategory value string."""
        for cat in StateCategory:
            with self.subTest(cat=cat):
                self.state.state_value = cat.value
                self.assertEqual(self.state.state_value, cat.value)

    def test_state_value_setter_invalid_type(self):
        """state_value setter raises TypeError for non-string input."""
        with self.assertRaises(TypeError):
            self.state.state_value = 42

    def test_state_value_setter_invalid_value(self):
        """state_value setter raises ValueError for unknown state string."""
        with self.assertRaises(ValueError):
            self.state.state_value = "NotAState"

    # -----------------------------------------------------------------------
    # update() — state transitions (health normalised as /100)
    #
    #   HEALTHFUL  : health/100 > 0.80   →  health ∈ [81, 100]
    #   DAMAGED    : 0.50 < h/100 ≤ 0.80 →  health ∈ [51,  80]
    #   CRITICAL   : 0.15 < h/100 ≤ 0.50 →  health ∈ [16,  50]
    #   DESTROYED  : h/100 ≤ 0.15        →  health ∈ [ 0,  15]
    # -----------------------------------------------------------------------
    def test_update_healthful_interior(self):
        """Interior HEALTHFUL values (82-100)."""
        for h in [100, 90, 82]:
            with self.subTest(health=h):
                self.state._health = h
                self.state.update()
                self.assertEqual(self.state.state_value, StateCategory.HEALTHFUL.value)

    def test_update_healthful_boundary_min(self):
        """health=81 is the minimum HEALTHFUL value (81/100=0.81 > 0.8)."""
        self.state._health = 81
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.HEALTHFUL.value)

    def test_update_damaged_boundary_max(self):
        """health=80 is the maximum DAMAGED value (80/100=0.80, not > 0.8)."""
        self.state._health = 80
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.DAMAGED.value)

    def test_update_damaged_interior(self):
        """Interior DAMAGED values (52-79)."""
        for h in [79, 70, 60, 52]:
            with self.subTest(health=h):
                self.state._health = h
                self.state.update()
                self.assertEqual(self.state.state_value, StateCategory.DAMAGED.value)

    def test_update_damaged_boundary_min(self):
        """health=51 is the minimum DAMAGED value (51/100=0.51, 0.5 < 0.51 ≤ 0.8)."""
        self.state._health = 51
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.DAMAGED.value)

    def test_update_critical_boundary_max(self):
        """health=50 is the maximum CRITICAL value (50/100=0.50, 0.15 < 0.50 ≤ 0.50)."""
        self.state._health = 50
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.CRITICAL.value)

    def test_update_critical_interior(self):
        """Interior CRITICAL values (17-49)."""
        for h in [49, 40, 30, 17]:
            with self.subTest(health=h):
                self.state._health = h
                self.state.update()
                self.assertEqual(self.state.state_value, StateCategory.CRITICAL.value)

    def test_update_critical_boundary_min(self):
        """health=16 is the minimum CRITICAL value (16/100=0.16, 0.15 < 0.16 ≤ 0.5)."""
        self.state._health = 16
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.CRITICAL.value)

    def test_update_destroyed_boundary_max(self):
        """health=15 is the maximum DESTROYED value (15/100=0.15, 0.15 ≤ 0.15)."""
        self.state._health = 15
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.DESTROYED.value)

    def test_update_destroyed_interior(self):
        """Interior DESTROYED values (1-14)."""
        for h in [14, 10, 5, 1]:
            with self.subTest(health=h):
                self.state._health = h
                self.state.update()
                self.assertEqual(self.state.state_value, StateCategory.DESTROYED.value)

    def test_update_destroyed_at_zero(self):
        """health=0 is the absolute minimum → DESTROYED."""
        self.state._health = 0
        self.state.update()
        self.assertEqual(self.state.state_value, StateCategory.DESTROYED.value)

    def test_update_does_not_change_on_falsy_state_value(self):
        """update() returns early when _state_value is falsy, leaving it unchanged."""
        self.state._state_value = None
        self.state._health = 0
        self.state.update()
        self.assertIsNone(self.state._state_value)

    # -----------------------------------------------------------------------
    # Boolean status checks
    # -----------------------------------------------------------------------
    def test_is_healthful_true(self):
        self.state._state_value = StateCategory.HEALTHFUL.value
        self.assertTrue(self.state.isHealtful())

    def test_is_healthful_false(self):
        self.state._state_value = StateCategory.DAMAGED.value
        self.assertFalse(self.state.isHealtful())

    def test_is_damaged_true(self):
        self.state._state_value = StateCategory.DAMAGED.value
        self.assertTrue(self.state.isDamaged())

    def test_is_damaged_false(self):
        self.state._state_value = StateCategory.HEALTHFUL.value
        self.assertFalse(self.state.isDamaged())

    def test_is_critical_true(self):
        self.state._state_value = StateCategory.CRITICAL.value
        self.assertTrue(self.state.isCritical())

    def test_is_critical_false(self):
        self.state._state_value = StateCategory.HEALTHFUL.value
        self.assertFalse(self.state.isCritical())

    def test_is_destroyed_true(self):
        self.state._state_value = StateCategory.DESTROYED.value
        self.assertTrue(self.state.isDestroyed())

    def test_is_destroyed_false(self):
        self.state._state_value = StateCategory.HEALTHFUL.value
        self.assertFalse(self.state.isDestroyed())

    def test_is_operative_healthful(self):
        self.state._state_value = StateCategory.HEALTHFUL.value
        self.assertTrue(self.state.isOperative())

    def test_is_operative_damaged(self):
        self.state._state_value = StateCategory.DAMAGED.value
        self.assertTrue(self.state.isOperative())

    def test_is_operative_critical(self):
        self.state._state_value = StateCategory.CRITICAL.value
        self.assertFalse(self.state.isOperative())

    def test_is_operative_destroyed(self):
        self.state._state_value = StateCategory.DESTROYED.value
        self.assertFalse(self.state.isOperative())

    # -----------------------------------------------------------------------
    # set_task_success / get_task_success / get_task_success_ratio
    # -----------------------------------------------------------------------
    def test_set_task_success_first_entry(self):
        """First call creates the task entry with correct counters."""
        self.state.set_task_success("STRIKE", True)
        result = self.state.get_task_success("STRIKE")
        self.assertIsNotNone(result)
        self.assertEqual(result["success_count"], 1)
        self.assertEqual(result["total_count"], 1)

    def test_set_task_success_accumulates(self):
        """Repeated calls accumulate success_count and total_count."""
        self.state.set_task_success("STRIKE", True)
        self.state.set_task_success("STRIKE", False)
        self.state.set_task_success("STRIKE", True)
        result = self.state.get_task_success("STRIKE")
        self.assertEqual(result["success_count"], 2)
        self.assertEqual(result["total_count"], 3)

    def test_set_task_success_failure_only(self):
        """Failures never increment success_count."""
        self.state.set_task_success("RECON", False)
        self.state.set_task_success("RECON", False)
        result = self.state.get_task_success("RECON")
        self.assertEqual(result["success_count"], 0)
        self.assertEqual(result["total_count"], 2)

    def test_set_task_success_initializes_dict_from_none(self):
        """set_task_success initializes _success_ratio dict when it is None."""
        state = State(object_type="Block", object_id="b1", success_ratio=None)
        self.assertIsNone(state._success_ratio)
        state.set_task_success("ATTACK", True)
        self.assertIsNotNone(state._success_ratio)

    def test_set_task_success_multiple_tasks_independent(self):
        """Different tasks maintain independent counters."""
        self.state.set_task_success("STRIKE", True)
        self.state.set_task_success("RECON", False)
        self.state.set_task_success("STRIKE", True)
        self.assertEqual(self.state.get_task_success("STRIKE")["total_count"], 2)
        self.assertEqual(self.state.get_task_success("RECON")["total_count"], 1)

    def test_get_task_success_unknown_task(self):
        """Returns None for an unregistered task."""
        self.assertIsNone(self.state.get_task_success("NONEXISTENT"))

    def test_get_task_success_when_no_success_ratio(self):
        """Returns None when _success_ratio is None."""
        state = State(object_type="Block", object_id="b1", success_ratio=None)
        self.assertIsNone(state.get_task_success("STRIKE"))

    def test_get_task_success_ratio_correct(self):
        """Returns correct float ratio (2 success / 4 total = 0.5)."""
        self.state.set_task_success("STRIKE", True)
        self.state.set_task_success("STRIKE", False)
        self.assertAlmostEqual(self.state.get_task_success_ratio("STRIKE"), 0.5)

    def test_get_task_success_ratio_all_success(self):
        """Returns 1.0 when all attempts succeeded."""
        for _ in range(4):
            self.state.set_task_success("ATTACK", True)
        self.assertAlmostEqual(self.state.get_task_success_ratio("ATTACK"), 1.0)

    def test_get_task_success_ratio_zero_attempts(self):
        """Returns 0.0 when total_count is zero."""
        self.state._success_ratio = {"STRIKE": {"success_count": 0, "total_count": 0}}
        self.assertAlmostEqual(self.state.get_task_success_ratio("STRIKE"), 0.0)

    def test_get_task_success_ratio_unknown_task(self):
        """Returns None for an unregistered task."""
        self.assertIsNone(self.state.get_task_success_ratio("NONEXISTENT"))

    def test_get_task_success_ratio_no_success_ratio(self):
        """Returns None when _success_ratio is None."""
        state = State(object_type="Block", object_id="b1", success_ratio=None)
        self.assertIsNone(state.get_task_success_ratio("STRIKE"))

    # -----------------------------------------------------------------------
    # total_success_ratio
    # -----------------------------------------------------------------------
    def test_total_success_ratio_empty(self):
        """Returns 0.0 when no tasks have been recorded."""
        state = State(object_type="Block", object_id="b1", success_ratio=None)
        self.assertAlmostEqual(state.total_success_ratio, 0.0)

    def test_total_success_ratio_single_task(self):
        """Aggregates correctly for a single task (2 success / 3 total)."""
        self.state.set_task_success("STRIKE", True)
        self.state.set_task_success("STRIKE", True)
        self.state.set_task_success("STRIKE", False)
        self.assertAlmostEqual(self.state.total_success_ratio, 2 / 3)

    def test_total_success_ratio_multiple_tasks(self):
        """Aggregates correctly across multiple tasks (2 success / 3 total)."""
        self.state.set_task_success("STRIKE", True)   # 1/1
        self.state.set_task_success("RECON", False)   # 0/1
        self.state.set_task_success("RECON", True)    # 1/2 → total 2/3
        self.assertAlmostEqual(self.state.total_success_ratio, 2 / 3)

    def test_total_success_ratio_all_zero_counts(self):
        """Returns 0.0 when all total_counts are zero."""
        self.state._success_ratio = {
            "STRIKE": {"success_count": 0, "total_count": 0},
            "RECON":  {"success_count": 0, "total_count": 0},
        }
        self.assertAlmostEqual(self.state.total_success_ratio, 0.0)

    # -----------------------------------------------------------------------
    # __repr__ and __str__
    # -----------------------------------------------------------------------
    def test_repr(self):
        """__repr__ includes object_type, object_id and health."""
        r = repr(self.state)
        self.assertIn("Block", r)
        self.assertIn("block_001", r)
        self.assertIn(str(self.state.health), r)

    def test_str(self):
        """__str__ includes object_type and object_id."""
        s = str(self.state)
        self.assertIn("Block", s)
        self.assertIn("block_001", s)

    # -----------------------------------------------------------------------
    # StateCategory enum
    # -----------------------------------------------------------------------
    def test_state_category_values(self):
        """StateCategory enum values match expected strings."""
        self.assertEqual(StateCategory.HEALTHFUL.value, "Healtful")
        self.assertEqual(StateCategory.DAMAGED.value, "Damaged")
        self.assertEqual(StateCategory.CRITICAL.value, "Critical")
        self.assertEqual(StateCategory.DESTROYED.value, "Destroyed")
        self.assertEqual(StateCategory.UNKNOW.value, "Unknow")

    # -----------------------------------------------------------------------
    # HEALTH_LEVEL thresholds
    # -----------------------------------------------------------------------
    def test_health_level_thresholds(self):
        """HEALTH_LEVEL contains expected float thresholds."""
        self.assertAlmostEqual(HEALTH_LEVEL[StateCategory.DAMAGED.value], 0.8)
        self.assertAlmostEqual(HEALTH_LEVEL[StateCategory.CRITICAL.value], 0.5)
        self.assertAlmostEqual(HEALTH_LEVEL[StateCategory.DESTROYED.value], 0.15)
        self.assertIsNone(HEALTH_LEVEL[StateCategory.UNKNOW.value])


if __name__ == "__main__":
    unittest.main()
