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


class TestDisengagementThresholds(unittest.TestCase):
    """Soglie di disingaggio (Fase 4, P1 + R2): dottrina di lato, due soglie coerenti."""

    @staticmethod
    def _table(erosion=0.3, shock=0.2):
        return {"Blue": {"erosion": erosion, "shock": shock}}

    def test_default_is_valid(self):
        Doctrine.validate_disengagement_thresholds(Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS)

    def test_default_covers_every_side(self):
        """Ogni lato del progetto (Context.SIDE) ha una dottrina di default."""
        from Code.Dynamic_War_Manager.Source.Context.Context import SIDE

        for side in SIDE:
            with self.subTest(side=side):
                self.assertIsNotNone(Doctrine.get_disengagement_thresholds(side))

    def test_default_is_symmetric(self):
        """Nessuna asimmetria nascosta in un default: R2 chiede la stessa regola per i due lati."""
        values = {tuple(sorted(v.items())) for v in Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS.values()}
        self.assertEqual(len(values), 1)

    def test_shock_not_above_erosion(self):
        """Con lo stesso denominatore uno shock > erosione non potrebbe mai scattare per primo."""
        with self.assertRaises(ValueError):
            Doctrine.validate_disengagement_thresholds(self._table(erosion=0.2, shock=0.3))

    def test_shock_equal_to_erosion_is_allowed(self):
        Doctrine.validate_disengagement_thresholds(self._table(erosion=0.3, shock=0.3))

    def test_one_means_fight_to_annihilation_and_is_allowed(self):
        Doctrine.validate_disengagement_thresholds(self._table(erosion=1.0, shock=1.0))

    def test_zero_or_above_one_raises(self):
        for erosion, shock in ((0.0, 0.0), (1.2, 0.2), (0.3, -0.1)):
            with self.subTest(erosion=erosion, shock=shock):
                with self.assertRaises(ValueError):
                    Doctrine.validate_disengagement_thresholds(self._table(erosion, shock))

    def test_missing_or_unknown_key_raises(self):
        with self.assertRaises(ValueError):
            Doctrine.validate_disengagement_thresholds({"Blue": {"erosion": 0.3}})
        with self.assertRaises(ValueError):
            Doctrine.validate_disengagement_thresholds({"Blue": {"erosion": 0.3, "shock": 0.2, "morale": 1}})

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            Doctrine.validate_disengagement_thresholds([])
        with self.assertRaises(TypeError):
            Doctrine.validate_disengagement_thresholds({"Blue": 0.3})
        with self.assertRaises(TypeError):
            Doctrine.validate_disengagement_thresholds({"Blue": {"erosion": "0.3", "shock": 0.2}})
        with self.assertRaises(TypeError):
            Doctrine.validate_disengagement_thresholds({"Blue": {"erosion": True, "shock": 0.2}})

    def test_get_returns_a_copy(self):
        entry = Doctrine.get_disengagement_thresholds("Blue")
        entry["erosion"] = 0.99
        self.assertEqual(Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS["Blue"]["erosion"], 0.30)

    def test_get_unknown_side_is_none(self):
        self.assertIsNone(Doctrine.get_disengagement_thresholds("Green"))
        self.assertIsNone(Doctrine.get_disengagement_thresholds(None))

    def test_get_uses_and_validates_a_custom_table(self):
        self.assertEqual(Doctrine.get_disengagement_thresholds("Blue", self._table(0.5, 0.25)),
                         {"erosion": 0.5, "shock": 0.25})
        with self.assertRaises(ValueError):
            Doctrine.get_disengagement_thresholds("Blue", self._table(0.2, 0.5))


class TestBreakpointParameters(unittest.TestCase):
    """Chiavi facoltative della soglia di rottura stocastica (2026-09-29)."""

    @staticmethod
    def _table(**extra):
        entry = {"erosion": 0.3, "shock": 0.2}
        entry.update(extra)
        return {"Blue": entry}

    def test_default_declares_every_parameter(self):
        for side, entry in Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS.items():
            with self.subTest(side=side):
                for key in Doctrine.DISENGAGEMENT_OPTIONAL_KEYS:
                    self.assertIn(key, entry)

    def test_default_values_of_the_proposal(self):
        entry = Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS["Red"]
        self.assertEqual(entry[Doctrine.BREAKPOINT_DISPERSION], 0.5)
        self.assertEqual(entry[Doctrine.MORALE_WEIGHT], 0.3)
        self.assertEqual(entry[Doctrine.FORCE_RATIO_EXPONENT], 0.5)
        self.assertEqual(entry[Doctrine.AIR_FORCE_RATIO_SCALE], 2.0)
        self.assertEqual(entry[Doctrine.UNANSWERED_FIRE_WEIGHT], 0.3)
        self.assertEqual(entry[Doctrine.DEFENSIVE_POSTURE_FACTOR], 1.2)
        self.assertEqual(entry[Doctrine.SHOCK_MIN_LOSSES], 2)

    def test_missing_optional_key_reads_the_neutral_value(self):
        entry = self._table()["Blue"]
        for key, neutral in Doctrine.DISENGAGEMENT_NEUTRAL.items():
            with self.subTest(key=key):
                self.assertEqual(Doctrine.disengagement_parameter(entry, key), neutral)
        self.assertEqual(Doctrine.disengagement_parameter(entry, "erosion"), 0.3)
        with self.assertRaises(KeyError):
            Doctrine.disengagement_parameter(entry, "morale")

    def test_valid_optional_values(self):
        Doctrine.validate_disengagement_thresholds(self._table(
            dispersion=0.0, morale_weight=0.0, force_ratio_exponent=1.0, force_ratio_bounds=(1.0, 1.0),
            air_force_ratio_scale=0.5, unanswered_fire_weight=0.9, defensive_posture_factor=0.8,
            shock_min_losses=1, median_bounds=[0.1, 0.9]))

    def test_out_of_range_optional_values(self):
        for key, value in (("dispersion", -0.1), ("morale_weight", 1.0), ("force_ratio_exponent", -1),
                           ("force_ratio_bounds", (1.2, 1.5)), ("force_ratio_bounds", (0.5, 0.9)),
                           ("air_force_ratio_scale", 0.0), ("unanswered_fire_weight", -0.1),
                           ("defensive_posture_factor", 0.0), ("shock_min_losses", 0),
                           ("median_bounds", (0.0, 0.9)), ("median_bounds", (0.5, 1.0))):
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValueError):
                    Doctrine.validate_disengagement_thresholds(self._table(**{key: value}))

    def test_optional_type_errors(self):
        for key, value in (("shock_min_losses", 2.0), ("shock_min_losses", True), ("dispersion", "0.5"),
                           ("median_bounds", 0.5), ("force_ratio_bounds", (0.6,))):
            with self.subTest(key=key, value=value):
                with self.assertRaises(TypeError):
                    Doctrine.validate_disengagement_thresholds(self._table(**{key: value}))


if __name__ == '__main__':
    unittest.main()
