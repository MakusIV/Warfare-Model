import json
import tempfile
import unittest
from pathlib import Path

from Dynamic_War_Manager.Source.Context.Target_Status_History import TargetStatusHistory


# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------

def _make_report(**overrides) -> dict:
    """Minimal recognition_report dict, optionally overriding fields."""
    base = {
        "block_name": "Alpha",
        "block_id": "B001",
        "side": "Blue",
        "state": "Healthy",
        "efficiency": 0.9,
        "morale": 0.8,
    }
    base.update(overrides)
    return base


class TestTargetStatusHistory(unittest.TestCase):

    def setUp(self):
        self.tsh = TargetStatusHistory()
        self.M1 = "M001"
        self.M2 = "M002"
        self.D1 = "2024-06-10"
        self.D2 = "2024-06-11"
        self.T1 = "06:30"
        self.T2 = "14:00"
        self.R1 = "North"
        self.R2 = "South"
        self.B1 = "B001"
        self.B2 = "B002"
        self.report1 = _make_report(block_id=self.B1, state="Healthy", efficiency=0.9)
        self.report2 = _make_report(block_id=self.B2, state="Damaged", efficiency=0.5)

    # -----------------------------------------------------------------------
    # add_block_snapshot — happy path
    # -----------------------------------------------------------------------

    def test_add_block_snapshot_creates_mission(self):
        """Adding a snapshot for a new mission_id creates the mission entry."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.assertIn(self.M1, self.tsh)

    def test_add_block_snapshot_stores_report(self):
        """The stored report is identical to the one passed in."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        stored = self.tsh.get_block_snapshot(self.M1, self.R1, self.B1)
        self.assertEqual(stored, self.report1)

    def test_add_block_snapshot_same_mission_two_regions(self):
        """Two different regions can be added to the same mission."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R2, self.B2, self.report2)
        self.assertEqual(
            self.tsh.get_block_snapshot(self.M1, self.R1, self.B1), self.report1
        )
        self.assertEqual(
            self.tsh.get_block_snapshot(self.M1, self.R2, self.B2), self.report2
        )

    def test_add_block_snapshot_overwrites_same_block(self):
        """Adding the same block twice overwrites the previous report."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        updated = _make_report(block_id=self.B1, state="Destroyed", efficiency=0.0)
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, updated)
        self.assertEqual(
            self.tsh.get_block_snapshot(self.M1, self.R1, self.B1)["state"], "Destroyed"
        )

    # -----------------------------------------------------------------------
    # add_block_snapshot — validation errors
    # -----------------------------------------------------------------------

    def test_add_block_snapshot_invalid_mission_id_type(self):
        with self.assertRaises(TypeError):
            self.tsh.add_block_snapshot(123, self.D1, self.T1, self.R1, self.B1, self.report1)

    def test_add_block_snapshot_empty_mission_id(self):
        with self.assertRaises(TypeError):
            self.tsh.add_block_snapshot("", self.D1, self.T1, self.R1, self.B1, self.report1)

    def test_add_block_snapshot_invalid_date_format(self):
        with self.assertRaises(ValueError):
            self.tsh.add_block_snapshot(self.M1, "10/06/2024", self.T1, self.R1, self.B1, self.report1)

    def test_add_block_snapshot_invalid_time_format(self):
        with self.assertRaises(ValueError):
            self.tsh.add_block_snapshot(self.M1, self.D1, "6h30", self.R1, self.B1, self.report1)

    def test_add_block_snapshot_empty_region_name(self):
        with self.assertRaises(TypeError):
            self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, "", self.B1, self.report1)

    def test_add_block_snapshot_empty_block_id(self):
        with self.assertRaises(TypeError):
            self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, "", self.report1)

    def test_add_block_snapshot_invalid_report_type(self):
        with self.assertRaises(TypeError):
            self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, "not a dict")

    def test_add_block_snapshot_conflicting_date(self):
        """Adding the same mission_id with a different date raises ValueError."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        with self.assertRaises(ValueError):
            self.tsh.add_block_snapshot(self.M1, self.D2, self.T1, self.R1, self.B2, self.report2)

    def test_add_block_snapshot_conflicting_time(self):
        """Adding the same mission_id with a different time raises ValueError."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        with self.assertRaises(ValueError):
            self.tsh.add_block_snapshot(self.M1, self.D1, self.T2, self.R1, self.B2, self.report2)

    # -----------------------------------------------------------------------
    # add_region_snapshot
    # -----------------------------------------------------------------------

    def test_add_region_snapshot_stores_all_blocks(self):
        """add_region_snapshot stores every block in the dict."""
        blocks = {self.B1: self.report1, self.B2: self.report2}
        self.tsh.add_region_snapshot(self.M1, self.D1, self.T1, self.R1, blocks)
        self.assertEqual(self.tsh.get_block_snapshot(self.M1, self.R1, self.B1), self.report1)
        self.assertEqual(self.tsh.get_block_snapshot(self.M1, self.R1, self.B2), self.report2)

    def test_add_region_snapshot_invalid_blocks_type(self):
        with self.assertRaises(TypeError):
            self.tsh.add_region_snapshot(self.M1, self.D1, self.T1, self.R1, [self.report1])

    # -----------------------------------------------------------------------
    # missions property / __len__ / __contains__
    # -----------------------------------------------------------------------

    def test_missions_empty(self):
        self.assertEqual(self.tsh.missions, [])

    def test_missions_insertion_order(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R1, self.B1, self.report2)
        self.assertEqual(self.tsh.missions, [self.M1, self.M2])

    def test_len_empty(self):
        self.assertEqual(len(self.tsh), 0)

    def test_len_after_inserts(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R1, self.B1, self.report2)
        self.assertEqual(len(self.tsh), 2)

    def test_contains_true(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.assertIn(self.M1, self.tsh)

    def test_contains_false(self):
        self.assertNotIn("NONEXISTENT", self.tsh)

    # -----------------------------------------------------------------------
    # get_mission
    # -----------------------------------------------------------------------

    def test_get_mission_returns_correct_metadata(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        mission = self.tsh.get_mission(self.M1)
        self.assertEqual(mission["date"], self.D1)
        self.assertEqual(mission["time"], self.T1)
        self.assertIn("regions", mission)

    def test_get_mission_missing_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.tsh.get_mission("NONEXISTENT")

    def test_get_mission_invalid_id_type(self):
        with self.assertRaises(TypeError):
            self.tsh.get_mission(42)

    # -----------------------------------------------------------------------
    # get_region_snapshot
    # -----------------------------------------------------------------------

    def test_get_region_snapshot_returns_blocks(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        snap = self.tsh.get_region_snapshot(self.M1, self.R1)
        self.assertIn(self.B1, snap)
        self.assertEqual(snap[self.B1], self.report1)

    def test_get_region_snapshot_missing_region_returns_empty_dict(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        snap = self.tsh.get_region_snapshot(self.M1, "NonExistentRegion")
        self.assertEqual(snap, {})

    # -----------------------------------------------------------------------
    # get_block_snapshot
    # -----------------------------------------------------------------------

    def test_get_block_snapshot_returns_report(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.assertEqual(
            self.tsh.get_block_snapshot(self.M1, self.R1, self.B1), self.report1
        )

    def test_get_block_snapshot_missing_block_returns_none(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.assertIsNone(self.tsh.get_block_snapshot(self.M1, self.R1, "GHOST"))

    def test_get_block_snapshot_missing_region_returns_none(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.assertIsNone(self.tsh.get_block_snapshot(self.M1, "GHOST", self.B1))

    # -----------------------------------------------------------------------
    # get_block_history
    # -----------------------------------------------------------------------

    def test_get_block_history_empty_when_no_missions(self):
        self.assertEqual(self.tsh.get_block_history(self.R1, self.B1), [])

    def test_get_block_history_single_entry(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        history = self.tsh.get_block_history(self.R1, self.B1)
        self.assertEqual(len(history), 1)
        mid, d, t, report = history[0]
        self.assertEqual(mid, self.M1)
        self.assertEqual(d, self.D1)
        self.assertEqual(t, self.T1)
        self.assertEqual(report, self.report1)

    def test_get_block_history_sorted_by_date_then_time(self):
        """Entries are sorted chronologically regardless of insertion order."""
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R1, self.B1, self.report2)
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        history = self.tsh.get_block_history(self.R1, self.B1)
        self.assertEqual(history[0][0], self.M1)
        self.assertEqual(history[1][0], self.M2)

    def test_get_block_history_skips_missing_block(self):
        """Missions where the block was not recorded are skipped."""
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R1, self.B2, self.report2)
        history = self.tsh.get_block_history(self.R1, self.B1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], self.M1)

    def test_get_block_history_invalid_region_type(self):
        with self.assertRaises(TypeError):
            self.tsh.get_block_history(123, self.B1)

    def test_get_block_history_invalid_block_id_type(self):
        with self.assertRaises(TypeError):
            self.tsh.get_block_history(self.R1, 456)

    # -----------------------------------------------------------------------
    # get_field_trend
    # -----------------------------------------------------------------------

    def test_get_field_trend_extracts_correct_field(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R1, self.B1, self.report2)
        trend = self.tsh.get_field_trend(self.R1, self.B1, "efficiency")
        values = [v for _, _, _, v in trend]
        self.assertEqual(values, [0.9, 0.5])

    def test_get_field_trend_missing_field_returns_none(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        trend = self.tsh.get_field_trend(self.R1, self.B1, "nonexistent_field")
        self.assertIsNone(trend[0][3])

    def test_get_field_trend_invalid_field_type(self):
        with self.assertRaises(TypeError):
            self.tsh.get_field_trend(self.R1, self.B1, 99)

    def test_get_field_trend_sorted_chronologically(self):
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R1, self.B1, self.report2)
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        trend = self.tsh.get_field_trend(self.R1, self.B1, "state")
        self.assertEqual([v for _, _, _, v in trend], ["Healthy", "Damaged"])

    # -----------------------------------------------------------------------
    # save / load round-trip
    # -----------------------------------------------------------------------

    def test_save_creates_valid_json_file(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.tsh.save(path)
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertIn(self.M1, data)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_restores_full_history(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        self.tsh.add_block_snapshot(self.M2, self.D2, self.T2, self.R2, self.B2, self.report2)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.tsh.save(path)
            loaded = TargetStatusHistory.load(path)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(
                loaded.get_block_snapshot(self.M1, self.R1, self.B1), self.report1
            )
            self.assertEqual(
                loaded.get_block_snapshot(self.M2, self.R2, self.B2), self.report2
            )
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_invalid_path_type(self):
        with self.assertRaises(TypeError):
            self.tsh.save(123)

    def test_load_invalid_path_type(self):
        with self.assertRaises(TypeError):
            TargetStatusHistory.load(None)

    # -----------------------------------------------------------------------
    # __repr__
    # -----------------------------------------------------------------------

    def test_repr_contains_mission_count(self):
        self.tsh.add_block_snapshot(self.M1, self.D1, self.T1, self.R1, self.B1, self.report1)
        r = repr(self.tsh)
        self.assertIn("1", r)
        self.assertIn(self.M1, r)


if __name__ == "__main__":
    unittest.main()
