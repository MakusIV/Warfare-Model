import unittest
from unittest.mock import MagicMock, patch

from Code.Dynamic_War_Manager.Source.Logic import Tactical_Analysis as ta
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Context import Combat_Power_Estimation
from Code.Dynamic_War_Manager.Source.Context.Context import (
    Ground_Vehicle_Asset_Type as gat,
    Air_Asset_Type as aat,
)

# Lightweight class stubs used only to set mock.__class__ for classification-loop dispatch,
# mirroring Test_Region.py/Test_Military.py -- Vehicle/Ship/Aircraft cannot be imported directly
# because they trigger a pre-existing circular import in the Aircraft->Aircraft_Weapon_Data chain.
_Vehicle = type('Vehicle', (), {})
_Aircraft = type('Aircraft', (), {})


def _make_combat_power_side_effect(value, task=None):
    """Mimics Military.combat_power's (force, action) contract: float if both `force` and
    `action` given, Dict[task, float] if only `force` given. If `task` is given, only that
    task carries `value` (every other task is 0.0) -- mirrors an asset whose combat power is
    concentrated on a single posture."""
    def _side_effect(force=None, action=None):
        if force and action:
            return value if task is None or action == task else 0.0
        if force:
            return {t: (value if task is None or t == task else 0.0) for t in Context.ACTION_TASKS[force]}
        return {f: {t: value for t in Context.ACTION_TASKS[f]} for f in Context.MILITARY_FORCES}
    return _side_effect


class TestGetTargetClassificationReport(unittest.TestCase):
    """
    Unit tests for Tactical_Analysis.get_target_report().

    Context.get_target_classification is mocked throughout to isolate the
    function under test from the bug in that helper (the comparison
    `if target_type == tg_type_element` sits outside the inner for-loop,
    so it only ever matches the last element of each classification list).
    """

    _PATCH = 'Code.Dynamic_War_Manager.Source.Context.Context.get_target_classification'

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    def test_raises_type_error_for_non_dict_report(self):
        """Raises TypeError when report is not a dict (string, int, list, None)."""
        for bad in ("string", 42, None, []):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    ta.get_target_report(bad)

    # ------------------------------------------------------------------
    # Returns None for absent / empty operative assets
    # ------------------------------------------------------------------
    def test_returns_none_when_asset_summary_missing(self):
        """Returns None when report has no 'asset_summary' key."""
        result = ta.get_target_report({})
        self.assertIsNone(result)

    def test_returns_none_when_asset_summary_is_none(self):
        """Returns None when asset_summary value is None."""
        result = ta.get_target_report({'asset_summary': None})
        self.assertIsNone(result)

    def test_returns_none_when_operative_key_missing(self):
        """Returns None when asset_summary dict has no 'operative' key."""
        result = ta.get_target_report(
            {'asset_summary': {'damaged': {'Tank': {'big': 1}}}}
        )
        self.assertIsNone(result)

    def test_returns_none_when_operative_is_none(self):
        """Returns None when operative value is None."""
        result = ta.get_target_report(
            {'asset_summary': {'operative': None}}
        )
        self.assertIsNone(result)

    def test_returns_none_when_operative_is_empty_dict(self):
        """Returns None when operative is an empty dict (no assets to classify)."""
        result = ta.get_target_report(
            {'asset_summary': {'operative': {}}}
        )
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # No visibility: non-empty operative dict, but all counts zero
    # (Block.get_recognition_report's per-report detection gate failed --
    # asset_type/dimension buckets are still populated with 0, unlike a
    # genuinely empty operative dict). Must be treated the same as "no
    # report at all", not as valid zero-asset data.
    # ------------------------------------------------------------------
    def test_returns_none_when_operative_counts_all_zero(self):
        """Returns None when every asset_type/dimension count is zero, even though the
        operative dict itself has real keys (recon didn't reveal quantities this report)."""
        with patch(self._PATCH, return_value='Armored'):
            result = ta.get_target_report(
                {'asset_summary': {'operative': {
                    'Tank':    {'big': 0, 'medium': 0, 'small': 0},
                    'Armored': {'big': 0},
                }}}
            )
        self.assertIsNone(result)

    def test_all_zero_counts_distinct_from_empty_dict_result(self):
        """A single asset_type with all-zero counts is no-visibility (None), not a valid dict
        reporting zero assets of that classification."""
        with patch(self._PATCH, return_value='Soft'):
            result = ta.get_target_report(
                {'asset_summary': {'operative': {'Motorized': {'big': 0}}}}
            )
        self.assertIsNone(result)

    def test_some_nonzero_counts_not_treated_as_no_visibility(self):
        """As soon as at least one raw count is nonzero, the result is a real dict, even if some
        asset_type/dimension entries are individually zero."""
        with patch(self._PATCH, return_value='Armored'):
            result = ta.get_target_report(
                {'asset_summary': {'operative': {
                    'Tank':    {'big': 0, 'medium': 0},
                    'Armored': {'big': 1},
                }}}
            )
        self.assertIsInstance(result, dict)
        self.assertEqual(result['Armored']['big'], 1)

    # ------------------------------------------------------------------
    # Single asset type
    # ------------------------------------------------------------------
    def test_single_asset_type_classified_correctly(self):
        """Single asset type: dimension counts are preserved under the correct key."""
        with patch(self._PATCH, return_value='Armored'):
            report = {'asset_summary': {'operative': {
                'Tank': {'big': 2, 'medium': 1, 'small': 0}
            }}}
            result = ta.get_target_report(report)
        self.assertIsInstance(result, dict)
        self.assertIn('Armored', result)
        self.assertEqual(result['Armored'], {'big': 2, 'medium': 1, 'small': 0})

    def test_result_is_dict_not_none_for_valid_input(self):
        """Returns a dict (not None) when at least one asset is classified."""
        with patch(self._PATCH, return_value='Soft'):
            report = {'asset_summary': {'operative': {'Motorized': {'big': 3}}}}
            result = ta.get_target_report(report)
        self.assertIsInstance(result, dict)

    # ------------------------------------------------------------------
    # Accumulation — same classification
    # ------------------------------------------------------------------
    def test_two_types_same_classification_accumulates_counts(self):
        """Two asset types mapping to the same classification have counts summed per dimension."""
        with patch(self._PATCH, return_value='Armored'):
            report = {'asset_summary': {'operative': {
                'Tank':    {'big': 3, 'medium': 2, 'small': 1},
                'Armored': {'big': 1, 'medium': 4, 'small': 3},
            }}}
            result = ta.get_target_report(report)
        self.assertEqual(result['Armored']['big'],    4)  # 3+1
        self.assertEqual(result['Armored']['medium'], 6)  # 2+4
        self.assertEqual(result['Armored']['small'],  4)  # 1+3

    def test_accumulation_handles_disjoint_dimension_keys(self):
        """Accumulation merges correctly when the two asset_data dicts have different dim keys."""
        with patch(self._PATCH, return_value='Armored'):
            report = {'asset_summary': {'operative': {
                'Tank':    {'big': 2},                # solo 'big'
                'Armored': {'medium': 3, 'small': 1}, # 'medium' e 'small'
            }}}
            result = ta.get_target_report(report)
        self.assertEqual(result['Armored']['big'],    2)
        self.assertEqual(result['Armored']['medium'], 3)
        self.assertEqual(result['Armored']['small'],  1)

    # ------------------------------------------------------------------
    # Multiple different classifications
    # ------------------------------------------------------------------
    def test_two_types_different_classifications_produce_two_entries(self):
        """Two asset types that map to different classifications produce separate entries."""
        def classify(asset_type):
            return 'Armored' if asset_type == 'Tank' else 'Soft'

        with patch(self._PATCH, side_effect=classify):
            report = {'asset_summary': {'operative': {
                'Tank':      {'big': 2, 'medium': 1},
                'Motorized': {'big': 0, 'medium': 3},
            }}}
            result = ta.get_target_report(report)

        self.assertIn('Armored', result)
        self.assertIn('Soft', result)
        self.assertEqual(result['Armored'], {'big': 2, 'medium': 1})
        self.assertEqual(result['Soft'],    {'big': 0, 'medium': 3})

    def test_three_types_two_classifications(self):
        """Three asset types: two share one classification, one has another."""
        def classify(asset_type):
            return 'Armored' if asset_type in ('Tank', 'Armored') else 'Air_Defense'

        with patch(self._PATCH, side_effect=classify):
            report = {'asset_summary': {'operative': {
                'Tank':    {'big': 1},
                'Armored': {'big': 2},
                'SAM_Big': {'big': 0, 'medium': 4},
            }}}
            result = ta.get_target_report(report)

        self.assertEqual(result['Armored']['big'],        3)  # 1+2
        self.assertEqual(result['Air_Defense']['big'],    0)
        self.assertEqual(result['Air_Defense']['medium'], 4)

    # ------------------------------------------------------------------
    # Skipping unclassifiable asset types
    # ------------------------------------------------------------------
    def test_asset_type_with_no_classification_is_skipped(self):
        """Asset type for which get_target_classification returns None is excluded from result."""
        def classify(asset_type):
            return 'Armored' if asset_type == 'Tank' else None

        with patch(self._PATCH, side_effect=classify):
            report = {'asset_summary': {'operative': {
                'Tank':      {'big': 2},
                'Artillery': {'big': 5},  # senza classificazione → ignorato
            }}}
            result = ta.get_target_report(report)

        self.assertIn('Armored', result)
        self.assertNotIn(None, result)
        self.assertEqual(len(result), 1)

    def test_all_unclassifiable_returns_empty_dict(self):
        """Returns empty dict when every asset type has no classification."""
        with patch(self._PATCH, return_value=None):
            report = {'asset_summary': {'operative': {
                'Tank':      {'big': 2},
                'Motorized': {'big': 1},
            }}}
            result = ta.get_target_report(report)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    # ------------------------------------------------------------------
    # Copy semantics — original report must not be mutated
    # ------------------------------------------------------------------
    def test_original_asset_data_not_mutated(self):
        """The original operative entry inside the report is not modified by the function."""
        with patch(self._PATCH, return_value='Armored'):
            original_counts = {'big': 3, 'medium': 2}
            report = {'asset_summary': {'operative': {
                'Tank': original_counts,
            }}}
            ta.get_target_report(report)
        # L'originale non deve essere stato modificato
        self.assertEqual(original_counts, {'big': 3, 'medium': 2})

    def test_accumulation_does_not_bleed_into_original_on_second_type(self):
        """When a second type triggers accumulation, the original dict of the first is not changed."""
        original_tank = {'big': 1, 'medium': 0}
        original_arm  = {'big': 2, 'medium': 3}

        with patch(self._PATCH, return_value='Armored'):
            report = {'asset_summary': {'operative': {
                'Tank':    original_tank,
                'Armored': original_arm,
            }}}
            result = ta.get_target_report(report)

        # I dict originali non devono essere stati modificati
        self.assertEqual(original_tank, {'big': 1, 'medium': 0})
        self.assertEqual(original_arm,  {'big': 2, 'medium': 3})
        # Il risultato deve contenere i conteggi sommati
        self.assertEqual(result['Armored']['big'],    3)
        self.assertEqual(result['Armored']['medium'], 3)


class TestProfileToWeaponDistribution(unittest.TestCase):
    """Unit tests for Tactical_Analysis.profile_to_weapon_distribution().

    Sostituisce l'euristica a copertura troncata (_profile_to_weapon_lists, rimossa) con una
    distribuzione pesata: ogni classificazione/dimensione presente nel profilo contribuisce
    sempre, pesata per la sua quota reale, invece di essere inclusa/esclusa tramite una soglia.
    """

    def test_empty_dict_profile_returns_empty_dict(self):
        self.assertEqual(ta.profile_to_weapon_distribution({}), {})

    def test_none_profile_returns_empty_dict(self):
        self.assertEqual(ta.profile_to_weapon_distribution(None), {})

    def test_single_class_single_dimension(self):
        result = ta.profile_to_weapon_distribution({'Armored': {'big': 5}})
        self.assertEqual(result, {'Armored': {'perc_type': 1.0, 'perc_dimension': {'big': 1.0}}})

    def test_two_classes_perc_type_proportional_to_count(self):
        result = ta.profile_to_weapon_distribution(
            {'Armored': {'big': 3}, 'Soft': {'small': 1}}
        )
        self.assertAlmostEqual(result['Armored']['perc_type'], 0.75)
        self.assertAlmostEqual(result['Soft']['perc_type'], 0.25)

    def test_perc_type_sums_to_one(self):
        result = ta.profile_to_weapon_distribution(
            {'Armored': {'big': 3}, 'Soft': {'small': 1}, 'Hard': {'med': 6}}
        )
        self.assertAlmostEqual(sum(v['perc_type'] for v in result.values()), 1.0)

    def test_perc_dimension_sums_to_one_within_each_class(self):
        result = ta.profile_to_weapon_distribution(
            {'Armored': {'big': 2, 'med': 1, 'small': 1}}
        )
        self.assertAlmostEqual(sum(result['Armored']['perc_dimension'].values()), 1.0)

    def test_perc_dimension_proportional_within_class(self):
        result = ta.profile_to_weapon_distribution({'Armored': {'big': 3, 'small': 1}})
        self.assertAlmostEqual(result['Armored']['perc_dimension']['big'], 0.75)
        self.assertAlmostEqual(result['Armored']['perc_dimension']['small'], 0.25)

    def test_zero_count_dimension_excluded_from_perc_dimension(self):
        result = ta.profile_to_weapon_distribution({'Armored': {'big': 0, 'small': 4}})
        self.assertEqual(result, {'Armored': {'perc_type': 1.0, 'perc_dimension': {'small': 1.0}}})

    def test_classification_with_all_zero_counts_excluded(self):
        result = ta.profile_to_weapon_distribution(
            {'Armored': {'big': 0}, 'Soft': {'small': 5}}
        )
        self.assertNotIn('Armored', result)
        self.assertIn('Soft', result)

    def test_zero_total_returns_empty_dict(self):
        result = ta.profile_to_weapon_distribution({'Armored': {'big': 0, 'small': 0}})
        self.assertEqual(result, {})

    def test_no_truncation_all_classes_present_regardless_of_share(self):
        """A differenza della vecchia euristica a copertura, non c'è soglia: anche una classe con
        una quota minima resta nel risultato."""
        profile = {'Dominant': {'big': 970}}
        for i in range(10):
            profile[f"Tail{i}"] = {'small': 3}
        result = ta.profile_to_weapon_distribution(profile)
        self.assertEqual(len(result), 11)
        for i in range(10):
            self.assertIn(f"Tail{i}", result)


class TestTargetProfileFromReport(unittest.TestCase):
    """Unit tests for Tactical_Analysis.target_profile_from_report()."""

    def test_delegates_to_get_target_report_with_same_args(self):
        report = {'asset_summary': {'operative': {'Tank': {'big': 1}}}}
        with patch.object(ta, 'get_target_report', return_value={'sentinel': True}) as mock_gtr:
            result = ta.target_profile_from_report(report)
        mock_gtr.assert_called_once_with(report)
        self.assertEqual(result, {'sentinel': True})

    def test_equivalent_to_get_target_report_real_call(self):
        with patch(
            'Code.Dynamic_War_Manager.Source.Context.Context.get_target_classification',
            return_value='Armored',
        ):
            report = {'asset_summary': {'operative': {'Tank': {'big': 2}}}}
            self.assertEqual(
                ta.target_profile_from_report(report),
                ta.get_target_report(report),
            )

    def test_returns_none_when_get_target_report_returns_none(self):
        result = ta.target_profile_from_report({'asset_summary': {'operative': {}}})
        self.assertIsNone(result)


class TestTargetProfileFromBlock(unittest.TestCase):
    """Unit tests for Tactical_Analysis.target_profile_from_block()."""

    def setUp(self):
        self.target_block = Block(
            name="Target Block", description="", side="Red",
            category="Military", sub_category="Base", functionality="Attack", value=10,
        )

    @staticmethod
    def _mock_asset(cls, asset_type, category=None, operative=True, physical=None):
        m = MagicMock()
        m.__class__ = cls
        m.asset_type = asset_type
        m.category = category
        m.is_operative.return_value = operative
        m.id = f"{asset_type}-mock"
        if physical is not None:
            m.get_physical_characteristics.return_value = physical
        return m

    def _call(self):
        return ta.target_profile_from_block(self.target_block)

    def test_empty_block_returns_empty_dict(self):
        self.target_block._assets = {}
        self.assertEqual(self._call(), {})

    def test_mixed_armor_and_sam_block_ground_truth_counts(self):
        tank = self._mock_asset(
            _Vehicle, gat.TANK.value,
            physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
        )
        sam = self._mock_asset(
            _Vehicle, gat.SAM_SMALL.value,
            physical={'length': 5, 'width': 2.5, 'height': 2, 'weight': 18},
        )
        self.target_block._assets = {'v1': tank, 'v2': sam}
        result = self._call()
        self.assertEqual(result, {'Armored': {'big': 1}, 'Air_Defense': {'small': 1}})

    def test_damaged_and_destroyed_assets_excluded(self):
        tank = self._mock_asset(
            _Vehicle, gat.TANK.value, operative=False,
            physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
        )
        self.target_block._assets = {'v1': tank}
        self.assertEqual(self._call(), {})

    def test_unclassifiable_asset_skipped(self):
        asset = self._mock_asset(
            _Vehicle, 'NotARealAssetType',
            physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
        )
        self.target_block._assets = {'v1': asset}
        self.assertEqual(self._call(), {})

    def test_aircraft_dimension_mapping_small_med_big(self):
        # Fase 3-bis (2026-09-16): la dimensione viene ora dalle physical characteristics reali,
        # non più derivata da asset_type/ruolo -- un asset per chiamata perché ogni caso usa lo
        # stesso asset_type (FIGHTER) per dimostrare che è la fisica, non il ruolo, a decidere.
        for physical, expected_dimension in (
            ({'length': 15, 'width': 9, 'height': 5, 'weight': 7690}, 'small'),    # F-16-like
            ({'length': 23, 'width': 14, 'height': 6, 'weight': 21820}, 'med'),    # MiG-31-like
            ({'length': 53, 'width': 52, 'height': 17, 'weight': 128100}, 'big'),  # C-17A-like
        ):
            with self.subTest(expected_dimension=expected_dimension):
                aircraft = self._mock_asset(_Aircraft, aat.FIGHTER.value, category=aat.FIGHTER.value, physical=physical)
                self.target_block._assets = {'a1': aircraft}
                result = self._call()
                classification = Context.get_target_classification(aat.FIGHTER.value)
                self.assertEqual(result, {classification: {expected_dimension: 1}})

    def test_aircraft_missing_asset_type_skipped(self):
        aircraft = self._mock_asset(
            _Aircraft, None, category=aat.FIGHTER.value,
            physical={'length': 15, 'width': 9, 'height': 5, 'weight': 7690},
        )
        self.target_block._assets = {'a1': aircraft}
        self.assertEqual(self._call(), {})

    def test_aircraft_missing_physical_characteristics_skipped(self):
        aircraft = self._mock_asset(_Aircraft, aat.FIGHTER.value, category=aat.FIGHTER.value)
        aircraft.get_physical_characteristics.return_value = None
        self.target_block._assets = {'a1': aircraft}
        self.assertEqual(self._call(), {})

    def test_vehicle_missing_physical_characteristics_skipped(self):
        asset = self._mock_asset(_Vehicle, gat.TANK.value, physical=None)
        asset.get_physical_characteristics.return_value = None
        self.target_block._assets = {'v1': asset}
        self.assertEqual(self._call(), {})

    def test_asset_type_none_skipped(self):
        asset = self._mock_asset(
            _Vehicle, None,
            physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
        )
        self.target_block._assets = {'v1': asset}
        self.assertEqual(self._call(), {})

    def test_two_assets_same_classification_and_dimension_accumulate(self):
        tank1 = self._mock_asset(
            _Vehicle, gat.TANK.value,
            physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
        )
        tank2 = self._mock_asset(
            _Vehicle, gat.TANK.value,
            physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
        )
        self.target_block._assets = {'v1': tank1, 'v2': tank2}
        result = self._call()
        self.assertEqual(result, {'Armored': {'big': 2}})

    def test_no_randomness_calc_probability_never_invoked(self):
        with patch(
            'Code.Dynamic_War_Manager.Source.Utility.Utility.calcProbability',
            side_effect=AssertionError("calcProbability must not be called by target_profile_from_block"),
        ):
            tank = self._mock_asset(
                _Vehicle, gat.TANK.value,
                physical={'length': 9, 'width': 3.5, 'height': 2.5, 'weight': 48},
            )
            self.target_block._assets = {'v1': tank}
            result = self._call()
        self.assertEqual(result, {'Armored': {'big': 1}})


class TestOperativeAircraftByModel(unittest.TestCase):
    """Unit tests for Tactical_Analysis.operative_aircraft_by_model()."""

    def setUp(self):
        self.airbase = Military(
            mil_category=Context.MILITARY_CATEGORY["Air_Base"][1], name="AB", side="Blue"
        )

    @staticmethod
    def _mock_aircraft(model, operative=True):
        m = MagicMock()
        m.__class__ = _Aircraft
        m.model = model
        m.asset_type = aat.FIGHTER.value
        m.is_operative.return_value = operative
        return m

    def test_empty_block_returns_empty_dict(self):
        self.airbase._assets = {}
        self.assertEqual(ta.operative_aircraft_by_model(self.airbase), {})

    def test_groups_by_model(self):
        a1 = self._mock_aircraft('F-14A Tomcat')
        a2 = self._mock_aircraft('F-14A Tomcat')
        a3 = self._mock_aircraft('F-16C Block 50')
        self.airbase._assets = {'a1': a1, 'a2': a2, 'a3': a3}
        result = ta.operative_aircraft_by_model(self.airbase)
        self.assertEqual(set(result.keys()), {'F-14A Tomcat', 'F-16C Block 50'})
        self.assertEqual(len(result['F-14A Tomcat']), 2)
        self.assertEqual(len(result['F-16C Block 50']), 1)

    def test_excludes_non_operative(self):
        a1 = self._mock_aircraft('F-14A Tomcat', operative=False)
        self.airbase._assets = {'a1': a1}
        self.assertEqual(ta.operative_aircraft_by_model(self.airbase), {})

    def test_excludes_model_none(self):
        a1 = self._mock_aircraft(None)
        self.airbase._assets = {'a1': a1}
        self.assertEqual(ta.operative_aircraft_by_model(self.airbase), {})

    def test_non_aircraft_assets_ignored(self):
        v = MagicMock()
        v.__class__ = _Vehicle
        v.is_operative.return_value = True
        self.airbase._assets = {'v1': v}
        self.assertEqual(ta.operative_aircraft_by_model(self.airbase), {})


class TestRepresentativeCombatPowerActionSelection(unittest.TestCase):
    """Fase 2: Tactical_Analysis.representative_combat_power() con selezione di azione esplicita."""

    def _block(self, **combat_power_kwargs):
        block = MagicMock(spec=Military)
        block.combat_power.side_effect = _make_combat_power_side_effect(**combat_power_kwargs)
        return block

    def test_no_action_ground_sums_all_tasks(self):
        """action=None (comportamento legacy): somma su tutti i task della force."""
        block = self._block(value=2.0)  # ogni task di 'ground' vale 2.0
        result = ta.representative_combat_power(block, 'ground', None)
        self.assertAlmostEqual(result, 2.0 * len(Context.ACTION_TASKS['ground']))

    def test_ground_action_returns_single_task_value(self):
        """action='Attack' (ground): ritorna solo il valore di quel task, non la somma."""
        block = self._block(value=5.0, task='Attack')  # solo 'Attack' vale 5.0, gli altri 0.0
        result = ta.representative_combat_power(block, 'ground', 'Attack')
        self.assertEqual(result, 5.0)
        block.combat_power.assert_called_once_with(force='ground', action='Attack')

    def test_sea_action_returns_single_task_value(self):
        """action='Defense' (sea): stesso comportamento di 'ground', SEA_TASK non ha 'Maintain'."""
        block = self._block(value=3.0, task='Defense')
        result = ta.representative_combat_power(block, 'sea', 'Defense')
        self.assertEqual(result, 3.0)

    def test_air_ignores_action_argument(self):
        """force='air': l'azione è ignorata per costruzione (AIR_COMBAT_EFFICACY è piatta)."""
        block = self._block(value=7.0)
        result_no_action = ta.representative_combat_power(block, 'air', None)
        result_with_action = ta.representative_combat_power(block, 'air', 'Attack')
        self.assertEqual(result_no_action, result_with_action)
        # entrambe le chiamate a combat_power devono passare solo `force`, mai `action`
        for call in block.combat_power.call_args_list:
            self.assertNotIn('action', call.kwargs)


class TestBuildReconCpSnapshot(unittest.TestCase):
    """Unit tests for Tactical_Analysis.build_recon_cp_snapshot() -- snapshot {block_id: cp} da una
    lista di report già recuperati dal chiamante (v. Region.update_military_priorities, che chiama
    get_recon_reports una sola volta per sweep e passa qui il risultato)."""

    def test_empty_reports_returns_empty_dict(self):
        self.assertEqual(ta.build_recon_cp_snapshot([]), {})

    def test_ground_report_uses_max_of_defense_and_maintain(self):
        report = {'block_id': 'b1', 'military_category': 'Ground_Base', 'side': 'Red', 'efficiency': None,
                   'asset_summary': {'operative': {'Tank': {'big': 5}}}}

        def fake_estimate(operative, force, action, *, side=None, efficiency=1.0):
            return {'Defense': 3.0, 'Maintain': 7.0}[action]

        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary', side_effect=fake_estimate):
            snapshot = ta.build_recon_cp_snapshot([report])
        self.assertEqual(snapshot, {'b1': 7.0})

    def test_sea_report_uses_only_defense_never_maintain(self):
        report = {'block_id': 'b1', 'military_category': 'Naval_Base', 'side': 'Red', 'efficiency': None,
                   'asset_summary': {'operative': {'Carrier': {'big': 1}}}}

        def fake_estimate(operative, force, action, *, side=None, efficiency=1.0):
            if action == 'Maintain':
                raise AssertionError("'Maintain' must never be queried for sea")
            return {'Defense': 5.0}[action]

        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary', side_effect=fake_estimate):
            snapshot = ta.build_recon_cp_snapshot([report])
        self.assertEqual(snapshot, {'b1': 5.0})

    def test_air_report_uses_single_action_none(self):
        report = {'block_id': 'b1', 'military_category': 'Air_Base', 'side': 'Red', 'efficiency': None,
                   'asset_summary': {'operative': {'Fighter': {'small': 4}}}}

        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary', return_value=9.0) as mock_est:
            snapshot = ta.build_recon_cp_snapshot([report])
        self.assertEqual(snapshot, {'b1': 9.0})
        mock_est.assert_called_once_with({'Fighter': {'small': 4}}, 'air', None, side='Red', efficiency=1.0)

    def test_report_missing_block_id_is_skipped(self):
        report = {'military_category': 'Ground_Base', 'side': 'Red', 'efficiency': None, 'asset_summary': {'operative': {}}}
        self.assertEqual(ta.build_recon_cp_snapshot([report]), {})

    def test_report_unrecognized_military_category_is_skipped(self):
        report = {'block_id': 'b1', 'military_category': 'Not_A_Real_Category', 'side': 'Red', 'efficiency': None, 'asset_summary': {'operative': {}}}
        self.assertEqual(ta.build_recon_cp_snapshot([report]), {})

    def test_multiple_reports_produce_multiple_entries(self):
        reports = [
            {'block_id': 'b1', 'military_category': 'Ground_Base', 'side': 'Red', 'efficiency': None, 'asset_summary': {'operative': {}}},
            {'block_id': 'b2', 'military_category': 'Ground_Base', 'side': 'Red', 'efficiency': None, 'asset_summary': {'operative': {}}},
        ]
        snapshot = ta.build_recon_cp_snapshot(reports)
        self.assertEqual(set(snapshot.keys()), {'b1', 'b2'})


class TestEstimatedTargetCombatPower(unittest.TestCase):
    """Unit tests for Tactical_Analysis.estimate_target_combat_power() -- wrapper per-report
    attorno a Combat_Power_Estimation.estimate_combat_power_from_asset_summary."""

    def test_none_force_returns_zero_without_calling_estimator(self):
        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary') as mock_est:
            result = ta.estimate_target_combat_power({'asset_summary': {'operative': {'Tank': {'big': 1}}}}, None, 'Attack')
        self.assertEqual(result, 0.0)
        mock_est.assert_not_called()

    def test_missing_efficiency_defaults_to_one(self):
        report = {'side': 'Red', 'efficiency': None, 'asset_summary': {'operative': {'Tank': {'big': 3}}}}
        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary', return_value=1.23) as mock_est:
            ta.estimate_target_combat_power(report, 'ground', 'Defense')
        mock_est.assert_called_once_with({'Tank': {'big': 3}}, 'ground', 'Defense', side='Red', efficiency=1.0)

    def test_present_efficiency_is_forwarded_unchanged(self):
        report = {'side': 'Blue', 'efficiency': 0.6, 'asset_summary': {'operative': {'Tank': {'big': 3}}}}
        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary', return_value=1.0) as mock_est:
            ta.estimate_target_combat_power(report, 'ground', 'Defense')
        mock_est.assert_called_once_with({'Tank': {'big': 3}}, 'ground', 'Defense', side='Blue', efficiency=0.6)

    def test_missing_asset_summary_passes_empty_dict(self):
        with patch.object(Combat_Power_Estimation, 'estimate_combat_power_from_asset_summary', return_value=0.0) as mock_est:
            ta.estimate_target_combat_power({'side': 'Red', 'efficiency': None}, 'ground', 'Defense')
        mock_est.assert_called_once_with({}, 'ground', 'Defense', side='Red', efficiency=1.0)


if __name__ == '__main__':
    unittest.main()
