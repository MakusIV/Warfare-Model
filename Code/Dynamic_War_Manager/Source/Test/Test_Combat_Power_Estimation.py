import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Context import Combat_Power_Estimation as cpe
from Code.Dynamic_War_Manager.Source.Context import Context


class TestEstimatedModelScoreFallbackChain(unittest.TestCase):
    """Family A: deterministic, mocked bucket table -- verifies only the fallback logic."""

    def setUp(self):
        self.buckets = {
            ('Tank', 'big'): (0.2, 0.4, 0.6),      # n=3 >= min_samples -> level 1
            ('Tank', 'med'): (0.3, 0.5),           # n=2 < min_samples -> falls to level 2
            ('Armored', 'small'): (0.1,),          # n=1
            ('Motorized', 'small'): (0.05,),       # asset_type in efficacy table, but sparse
        }
        patcher = patch.object(cpe, '_bucket_scores', return_value=self.buckets)
        self.mock_bucket_scores = patcher.start()
        self.addCleanup(patcher.stop)

    def test_level1_bucket_used_when_enough_samples(self):
        self.assertEqual(cpe.estimated_model_score('Tank', 'big', 'ground'), 0.4)

    def test_level2_asset_type_only_when_dimension_bucket_sparse(self):
        # ('Tank','med') has only 2 samples (< default min_samples=3) -> falls to all-Tank median
        # across every dimension bucket: (0.2, 0.4, 0.6, 0.3, 0.5) -> median 0.4
        self.assertEqual(cpe.estimated_model_score('Tank', 'med', 'ground'), 0.4)

    def test_custom_min_samples_changes_which_level_is_used(self):
        # With min_samples=2, the ('Tank','med') bucket itself now qualifies.
        self.assertEqual(cpe.estimated_model_score('Tank', 'med', 'ground', min_samples=2), 0.4)

    def test_level3_global_median_excludes_non_combatant_asset_types(self):
        # 'Artillery_Fixed' has zero samples in any bucket -> falls to the global median of the
        # force, which must exclude asset_types absent from GROUND_COMBAT_EFFICACY (none of our
        # mocked buckets are excluded here since Tank/Armored/Motorized are all real ground
        # combat categories) -> median of all pooled scores (0.2,0.4,0.6,0.3,0.5,0.1,0.05).
        import statistics
        expected = statistics.median([0.2, 0.4, 0.6, 0.3, 0.5, 0.1, 0.05])
        self.assertEqual(cpe.estimated_model_score('Artillery_Fixed', 'big', 'ground'), expected)

    def test_global_median_excludes_sam_aaa_ewr_buckets(self):
        """SAM/AAA/EWR scores must never pollute the global fallback median (structural exclusion,
        not incidental to this particular mock)."""
        buckets_with_sam = dict(self.buckets)
        buckets_with_sam[('SAM_Big', 'big')] = (0.9, 0.95, 0.99)  # would skew the median upward
        self.mock_bucket_scores.return_value = buckets_with_sam
        import statistics
        expected = statistics.median([0.2, 0.4, 0.6, 0.3, 0.5, 0.1, 0.05])  # SAM_Big excluded
        self.assertEqual(cpe.estimated_model_score('Artillery_Fixed', 'big', 'ground'), expected)

    def test_empty_registry_returns_zero(self):
        self.mock_bucket_scores.return_value = {}
        self.assertEqual(cpe.estimated_model_score('Tank', 'big', 'ground'), 0.0)

    def test_dimension_none_skips_level1_goes_straight_to_asset_type(self):
        self.assertEqual(cpe.estimated_model_score('Tank', None, 'ground'), 0.4)


class TestEstimateCombatPowerFromAssetSummary(unittest.TestCase):
    """Family A: deterministic behaviour of the entry point used by Region."""

    def setUp(self):
        patcher = patch.object(cpe, '_bucket_scores', return_value={('Tank', 'big'): (0.4, 0.4, 0.4)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_empty_asset_summary_returns_zero(self):
        self.assertEqual(cpe.estimate_combat_power_from_asset_summary({}, 'ground', 'Attack'), 0.0)

    def test_all_zero_counts_returns_zero(self):
        self.assertEqual(
            cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 0}}, 'ground', 'Attack'), 0.0
        )

    def test_asset_type_absent_from_efficacy_table_contributes_zero(self):
        """SAM/AAA/EWR: zero contribution, and estimated_model_score is never even called for them
        (skips the score lookup entirely, not just its use)."""
        with patch.object(cpe, 'estimated_model_score') as mock_score:
            result = cpe.estimate_combat_power_from_asset_summary(
                {'SAM_Big': {'big': 3}, 'EWR': {'small': 2}}, 'ground', 'Attack'
            )
        self.assertEqual(result, 0.0)
        mock_score.assert_not_called()

    def test_linear_in_count(self):
        one = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 1}}, 'ground', 'Attack')
        ten = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 10}}, 'ground', 'Attack')
        self.assertAlmostEqual(ten, one * 10)

    def test_matches_combat_power_from_score_directly(self):
        expected = Context.combat_power_from_score('Tank', 0.4, Context.GROUND_COMBAT_EFFICACY['Attack'], 1.0)
        result = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 1}}, 'ground', 'Attack')
        self.assertAlmostEqual(result, expected)

    def test_efficiency_parameter_is_forwarded(self):
        full = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 1}}, 'ground', 'Attack', efficiency=1.0)
        half = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 1}}, 'ground', 'Attack', efficiency=0.5)
        self.assertAlmostEqual(half, full * 0.5)


class TestNoTargetClassificationDependency(unittest.TestCase):
    """Combat_Power_Estimation must never touch Context.TARGET_CLASSIFICATION/get_target_classification
    -- that vocabulary answers a different question (weapon-vs-target planning), v. memoria di progetto.
    (The module's own docstrings legitimately mention it by name to document why it's absent, so the
    invariant is checked behaviourally rather than by grepping the source.)"""

    def test_get_target_classification_never_called(self):
        with patch.object(Context, 'get_target_classification') as mock_gtc:
            cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 5}}, 'ground', 'Attack')
        mock_gtc.assert_not_called()


class TestRealRegistryCoherence(unittest.TestCase):
    """Family B: real registry, no tolerance needed -- properties guaranteed by construction
    (median always falls within [min, max] of its own population; ordering is preserved)."""

    def test_estimate_falls_within_real_bucket_range(self):
        buckets = cpe._bucket_scores('ground', None)
        tank_big_scores = buckets.get(('Tank', 'big'), ())
        self.assertGreaterEqual(len(tank_big_scores), cpe.DEFAULT_MIN_SAMPLES)

        per_unit = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 1}}, 'ground', 'Attack')
        efficacy_table = Context.GROUND_COMBAT_EFFICACY['Attack']
        real_values = [Context.combat_power_from_score('Tank', s, efficacy_table, 1.0) for s in tank_big_scores]

        self.assertGreaterEqual(per_unit, min(real_values))
        self.assertLessEqual(per_unit, max(real_values))

    def test_ordering_preserved_tank_outranks_armored_on_attack(self):
        tank_cp = cpe.estimate_combat_power_from_asset_summary({'Tank': {'big': 10}}, 'ground', 'Attack')
        armored_cp = cpe.estimate_combat_power_from_asset_summary({'Armored': {'big': 10}}, 'ground', 'Attack')
        self.assertGreater(tank_cp, armored_cp)

    def test_aircraft_model_contributes_to_every_listed_category_bucket(self):
        """An Aircraft whose registry `category` lists multiple Air_Asset_Type roles (e.g. F-16A:
        Fighter + Fighter_Bomber) must contribute its score to every one of those buckets."""
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
        f16 = Aircraft_Data._registry['F-16A Fighting Falcon']
        categories = [c.value for c in f16.category]
        self.assertIn('Fighter', categories)
        self.assertIn('Fighter_Bomber', categories)

        buckets = cpe._bucket_scores('air', None)
        fighter_scores = [v for (at, dim), vals in buckets.items() if at == 'Fighter' for v in vals]
        fb_scores = [v for (at, dim), vals in buckets.items() if at == 'Fighter_Bomber' for v in vals]
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import get_aircraft_combat_score
        f16_score = get_aircraft_combat_score('F-16A Fighting Falcon')
        self.assertIn(f16_score, fighter_scores)
        self.assertIn(f16_score, fb_scores)

    def test_side_filter_uses_real_users_field(self):
        """Fase 4 (2026-09-16): Vehicle_Data/Ship_Data now have a real, populated `users` field --
        filtering _bucket_scores by side must actually narrow the population using real data, not
        just accept the parameter without effect."""
        no_filter = cpe._bucket_scores('ground', None)
        blue = cpe._bucket_scores('ground', 'Blue')
        red = cpe._bucket_scores('ground', 'Red')

        def total_samples(buckets):
            return sum(len(v) for v in buckets.values())

        self.assertGreater(total_samples(no_filter), total_samples(blue))
        self.assertGreater(total_samples(no_filter), total_samples(red))
        self.assertGreater(total_samples(blue), 0)
        self.assertGreater(total_samples(red), 0)

    def test_side_filter_never_excludes_a_model_with_no_users(self):
        """A model with an empty `users` must always be included regardless of `side` (inclusive
        fallback, deliberate -- v. memoria Fase 4: 'modello senza users incluso in ogni bucket
        per-lato'). Temporarily clears a real model's `users` (T-90M: Russia/India, neither in
        'Blue') to prove it stays in the 'Blue' pool precisely because `users` is empty, not
        because of a coincidental match."""
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data, VEHICLE

        t90m = Vehicle_Data._registry['T-90M']
        self.assertTrue(t90m.users)  # sanity: really has real users data, none in 'Blue'
        self.assertFalse(any(u in Context.COALITIONS['Blue'] for u in t90m.users))

        cpe._bucket_scores.cache_clear()
        with patch.object(t90m, 'users', []):
            buckets = cpe._bucket_scores('ground', 'Blue')
        cpe._bucket_scores.cache_clear()

        t90m_score = VEHICLE['T-90M']['combat score']['global_score']
        self.assertIn(t90m_score, buckets.get(('Tank', 'big'), ()))


class TestRealRegistryToleranceCoherence(unittest.TestCase):
    """Family C: real registry, explicit tolerance on relative error -- combat_power_from_score's
    `1 + score` compresses the wide raw-score spread into a much narrower combat-power spread, so a
    tolerance far below the raw score range is still correct. See project memory for the derivation:
    for a single Tank the worst-case error is ~=24% (score range 0.154-1.000 around median 0.432
    compresses through `1+score` to a ~1.49-2.30 range around ~1.86); on a mixed composite block the
    error typically shrinks further. delta=0.30 leaves headroom above the measured single-asset
    worst case.
    """

    def test_composite_block_within_30_percent_of_ground_truth(self):
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data, VEHICLE

        composition = {'Tank': 10, 'Armored': 15, 'Artillery_Semovent': 5}
        efficacy_table = Context.GROUND_COMBAT_EFFICACY['Attack']

        ground_truth = 0.0
        for asset_type, count in composition.items():
            models = [m for m, d in Vehicle_Data._registry.items() if d.category == asset_type]
            self.assertTrue(models, f"no models found for {asset_type}")
            avg_score = sum(VEHICLE[m]['combat score']['global_score'] for m in models) / len(models)
            ground_truth += count * Context.combat_power_from_score(asset_type, avg_score, efficacy_table, 1.0)

        # Not every model of these asset_types is necessarily 'big'; anchor the observed
        # asset_summary to the real, most common dimension for each asset_type instead of
        # assuming one, to keep the ground-truth comparison honest.
        asset_summary = {}
        for asset_type, count in composition.items():
            dims = [
                Context.get_dimension('Vehicle', **d.physical_characteristics)
                for m, d in Vehicle_Data._registry.items() if d.category == asset_type
            ]
            common_dim = max(set(dims), key=dims.count)
            asset_summary[asset_type] = {common_dim: count}

        estimate = cpe.estimate_combat_power_from_asset_summary(asset_summary, 'ground', 'Attack')

        self.assertGreater(ground_truth, 0.0)
        self.assertAlmostEqual(estimate / ground_truth, 1.0, delta=0.30)


if __name__ == '__main__':
    unittest.main()
