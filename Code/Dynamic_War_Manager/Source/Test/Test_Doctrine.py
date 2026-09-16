import unittest

from Code.Dynamic_War_Manager.Source.Context import Doctrine


class TestValidateWeightPriorityTarget(unittest.TestCase):
    """Unit tests for Doctrine.validate_weight_priority_target()."""

    def test_valid_structure_does_not_raise(self):
        valid_weights = {
            "Ground_Base": {
                "attack": {"Ground_Base": 0.7, "Naval_Base": 0.0},
                "defense": {"Ground_Base": 0.1, "Naval_Base": 0.1}
            }
        }
        Doctrine.validate_weight_priority_target(valid_weights)

    def test_non_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            Doctrine.validate_weight_priority_target("invalid")

    def test_non_dict_category_weights_raises_type_error(self):
        with self.assertRaises(TypeError):
            Doctrine.validate_weight_priority_target({"Ground_Base": "invalid"})

    def test_weight_out_of_range_raises_value_error(self):
        invalid_weights = {"Ground_Base": {"attack": {"Ground_Base": 1.5}, "defense": {"Ground_Base": 0.1}}}
        with self.assertRaises(ValueError):
            Doctrine.validate_weight_priority_target(invalid_weights)

    def test_empty_action_weights_raises_value_error(self):
        with self.assertRaises(ValueError):
            Doctrine.validate_weight_priority_target({"Ground_Base": {"attack": {}, "defense": {}}})

    def test_missing_attack_or_defense_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            Doctrine.validate_weight_priority_target({"Ground_Base": {"attack": {"Ground_Base": 0.5}}})

    def test_default_weight_priority_target_is_valid(self):
        """The shipped default must satisfy its own validator."""
        Doctrine.validate_weight_priority_target(Doctrine.DEFAULT_WEIGHT_PRIORITY_TARGET)


if __name__ == '__main__':
    unittest.main()
