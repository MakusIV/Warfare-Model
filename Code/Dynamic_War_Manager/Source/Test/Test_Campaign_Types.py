"""Tests per Command/Campaign_Types — tipi di dominio della campagna (F8a)."""
import json
import unittest
from types import MappingProxyType

from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    DEFAULT_SESSION_DURATION_S,
    MAX_SESSION_DURATION_S,
    CampaignLedger,
    ReadyRecord,
    SessionRecord,
    SessionRules,
    SessionValidationError,
    SessionViolation,
    ViolationCode,
)


class TestSessionRules(unittest.TestCase):
    """SessionRules: default, massimo, finestra."""

    def test_defaults(self):
        rules = SessionRules()
        self.assertEqual(rules.default_duration_s, DEFAULT_SESSION_DURATION_S)
        self.assertEqual(rules.max_duration_s, MAX_SESSION_DURATION_S)

    def test_custom(self):
        rules = SessionRules(default_duration_s=3600.0, max_duration_s=7200.0)
        self.assertEqual(rules.default_duration_s, 3600.0)
        self.assertEqual(rules.max_duration_s, 7200.0)

    def test_window_default_duration(self):
        rules = SessionRules()
        start, end = rules.window(0.0)
        self.assertEqual(start, 0.0)
        self.assertEqual(end, DEFAULT_SESSION_DURATION_S)

    def test_window_explicit_duration(self):
        rules = SessionRules()
        start, end = rules.window(100.0, 3600.0)
        self.assertEqual(start, 100.0)
        self.assertEqual(end, 3700.0)

    def test_default_greater_than_max_raises(self):
        with self.assertRaises(ValueError):
            SessionRules(default_duration_s=20000.0, max_duration_s=10000.0)

    def test_window_duration_zero_raises(self):
        rules = SessionRules()
        with self.assertRaises(ValueError):
            rules.window(0.0, 0.0)

    def test_window_duration_negative_raises(self):
        rules = SessionRules()
        with self.assertRaises(ValueError):
            rules.window(0.0, -1.0)

    def test_window_duration_exceeds_max_raises(self):
        rules = SessionRules()
        with self.assertRaises(ValueError):
            rules.window(0.0, MAX_SESSION_DURATION_S + 1.0)

    def test_non_number_rejected(self):
        with self.assertRaises(TypeError):
            SessionRules(default_duration_s='abc')
        with self.assertRaises(TypeError):
            SessionRules(max_duration_s=True)
        rules = SessionRules()
        with self.assertRaises(TypeError):
            rules.window('abc')
        with self.assertRaises(TypeError):
            rules.window(0.0, 'abc')

    def test_bool_duration_rejected(self):
        rules = SessionRules()
        with self.assertRaises(TypeError):
            rules.window(0.0, True)

    def test_default_equal_to_max_is_allowed(self):
        rules = SessionRules(default_duration_s=7200.0, max_duration_s=7200.0)
        self.assertEqual(rules.window(0.0), (0.0, 7200.0))

    def test_immutable(self):
        rules = SessionRules()
        with self.assertRaises(Exception):
            rules.default_duration_s = 100.0
        with self.assertRaises(Exception):
            rules.max_duration_s = 100.0


class TestSessionViolation(unittest.TestCase):
    """SessionViolation e ViolationCode."""

    def test_construction(self):
        v = SessionViolation(ViolationCode.SESSION_OPEN, "open session")
        self.assertEqual(v.code, ViolationCode.SESSION_OPEN)
        self.assertEqual(v.message, "open session")
        self.assertIsNone(v.mission_id)
        self.assertIsNone(v.asset_id)

    def test_with_context(self):
        v = SessionViolation(ViolationCode.ASSET_DESTROYED, "destroyed",
                             mission_id='M', asset_id='A')
        self.assertEqual(v.mission_id, 'M')
        self.assertEqual(v.asset_id, 'A')

    def test_empty_message_raises(self):
        with self.assertRaises(ValueError):
            SessionViolation(ViolationCode.SESSION_OPEN, "")

    def test_bad_mission_id_raises(self):
        with self.assertRaises(ValueError):
            SessionViolation(ViolationCode.SESSION_OPEN, "x", mission_id="")

    def test_bad_asset_id_raises(self):
        with self.assertRaises(ValueError):
            SessionViolation(ViolationCode.SESSION_OPEN, "x", asset_id="")

    def test_immutable(self):
        v = SessionViolation(ViolationCode.SESSION_OPEN, "x")
        with self.assertRaises(Exception):
            v.message = "y"


class TestSessionValidationError(unittest.TestCase):
    """SessionValidationError."""

    def test_is_value_error(self):
        err = SessionValidationError("S", (SessionViolation(ViolationCode.SESSION_OPEN, "x"),))
        self.assertIsInstance(err, ValueError)

    def test_carries_violations(self):
        v1 = SessionViolation(ViolationCode.SESSION_OPEN, "open")
        v2 = SessionViolation(ViolationCode.MISSION_ASSETS, "no block", mission_id='M')
        err = SessionValidationError("S1", (v1, v2))
        self.assertEqual(err.session_id, "S1")
        self.assertEqual(len(err.violations), 2)
        self.assertIn("S1", str(err))
        self.assertIn("open", str(err))
        self.assertIn("no block", str(err))
        self.assertIn("mission 'M'", str(err))


class TestSessionRecord(unittest.TestCase):
    """SessionRecord."""

    def test_construction(self):
        r = SessionRecord("S1", 0.0, 3600.0)
        self.assertEqual(r.session_id, "S1")
        self.assertEqual(r.t_start, 0.0)
        self.assertEqual(r.t_end, 3600.0)

    def test_t_end_less_than_t_start_raises(self):
        with self.assertRaises(ValueError):
            SessionRecord("S1", 100.0, 50.0)

    def test_non_number_raises(self):
        with self.assertRaises(TypeError):
            SessionRecord("S1", "abc", 100.0)

    def test_immutable(self):
        r = SessionRecord("S1", 0.0, 100.0)
        with self.assertRaises(Exception):
            r.t_start = 50.0


class TestReadyRecord(unittest.TestCase):
    """ReadyRecord."""

    def test_construction(self):
        r = ReadyRecord("A", 1000.0, 500.0, turnaround_s=300.0, repair_s=200.0)
        self.assertEqual(r.asset_id, "A")
        self.assertEqual(r.ready_at, 1000.0)
        self.assertEqual(r.since, 500.0)
        self.assertEqual(r.turnaround_s, 300.0)
        self.assertEqual(r.repair_s, 200.0)

    def test_rearm_and_repair(self):
        r = ReadyRecord("A", 1000.0, 500.0, turnaround_s=500.0, repair_s=0.0)
        self.assertTrue(r.rearm)
        self.assertFalse(r.repair)

        r2 = ReadyRecord("A", 1000.0, 500.0, turnaround_s=0.0, repair_s=500.0)
        self.assertFalse(r2.rearm)
        self.assertTrue(r2.repair)

        r3 = ReadyRecord("A", 1000.0, 500.0, turnaround_s=200.0, repair_s=300.0)
        self.assertTrue(r3.rearm)
        self.assertTrue(r3.repair)

    def test_both_zero_raises(self):
        with self.assertRaises(ValueError):
            ReadyRecord("A", 1000.0, 500.0, turnaround_s=0.0, repair_s=0.0)

    def test_ready_at_too_early_raises(self):
        with self.assertRaises(ValueError):
            ReadyRecord("A", 500.0, 500.0, turnaround_s=300.0, repair_s=0.0)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            ReadyRecord("A", 1000.0, 500.0, turnaround_s=-1.0)

    def test_immutable(self):
        r = ReadyRecord("A", 1000.0, 500.0, turnaround_s=500.0, repair_s=0.0)
        with self.assertRaises(Exception):
            r.ready_at = 2000.0


class TestCampaignLedger(unittest.TestCase):
    """CampaignLedger."""

    def test_empty_ledger(self):
        ledger = CampaignLedger()
        self.assertIsNone(ledger.last_end)
        self.assertEqual(ledger.sessions, ())
        self.assertIsInstance(ledger.readiness, MappingProxyType)

    def test_last_end(self):
        r1 = SessionRecord("S1", 0.0, 3600.0)
        r2 = SessionRecord("S2", 3600.0, 7200.0)
        ledger = CampaignLedger(sessions=(r1, r2))
        self.assertEqual(ledger.last_end, 7200.0)

    def test_is_ready_no_record(self):
        ledger = CampaignLedger()
        self.assertTrue(ledger.is_ready("A", 0.0))

    def test_is_ready_before_and_after(self):
        ledger = CampaignLedger(readiness={"A": ReadyRecord("A", 1000.0, 500.0, turnaround_s=500.0)})
        self.assertFalse(ledger.is_ready("A", 0.0))
        self.assertFalse(ledger.is_ready("A", 999.0))
        self.assertTrue(ledger.is_ready("A", 1000.0))

    def test_ready_at(self):
        ledger = CampaignLedger(readiness={"A": ReadyRecord("A", 1000.0, 500.0, turnaround_s=500.0)})
        self.assertEqual(ledger.ready_at("A"), 1000.0)
        self.assertIsNone(ledger.ready_at("B"))

    def test_with_session(self):
        ledger = CampaignLedger()
        r1 = SessionRecord("S1", 0.0, 3600.0)
        ledger2 = ledger.with_session(r1)
        self.assertEqual(ledger2.last_end, 3600.0)
        self.assertEqual(len(ledger2.sessions), 1)

    def test_with_session_contiguous(self):
        r1 = SessionRecord("S1", 0.0, 3600.0)
        r2 = SessionRecord("S2", 3600.0, 7200.0)
        ledger = CampaignLedger(sessions=(r1,)).with_session(r2)
        self.assertEqual(ledger.last_end, 7200.0)

    def test_with_session_overlapping_raises(self):
        r1 = SessionRecord("S1", 0.0, 5000.0)
        ledger = CampaignLedger(sessions=(r1,))
        r2 = SessionRecord("S2", 4000.0, 8000.0)
        with self.assertRaises(ValueError):
            ledger.with_session(r2)

    def test_with_readiness_replaces(self):
        ledger = CampaignLedger(readiness={"A": ReadyRecord("A", 1000.0, 500.0, turnaround_s=500.0)})
        ledger2 = ledger.with_readiness({"B": ReadyRecord("B", 2000.0, 1000.0, turnaround_s=1000.0)})
        self.assertIsNone(ledger2.ready_at("A"))
        self.assertEqual(ledger2.ready_at("B"), 2000.0)

    def test_to_dict_and_from_dict(self):
        r1 = SessionRecord("S1", 0.0, 3600.0)
        r2 = SessionRecord("S2", 3600.0, 7200.0)
        readiness = {"A": ReadyRecord("A", 1000.0, 500.0, turnaround_s=500.0)}
        ledger = CampaignLedger(
            rules=SessionRules(default_duration_s=7200.0, max_duration_s=14400.0),
            sessions=(r1, r2),
            readiness=readiness,
        )
        data = ledger.to_dict()
        # Verifica JSON-serializzabile
        json_str = json.dumps(data)
        data2 = json.loads(json_str)
        ledger2 = CampaignLedger.from_dict(data2)

        self.assertEqual(ledger2.rules.default_duration_s, ledger.rules.default_duration_s)
        self.assertEqual(ledger2.rules.max_duration_s, ledger.rules.max_duration_s)
        self.assertEqual(len(ledger2.sessions), 2)
        self.assertEqual(ledger2.sessions[0].session_id, "S1")
        self.assertEqual(ledger2.last_end, 7200.0)
        self.assertEqual(ledger2.ready_at("A"), 1000.0)

    def test_readiness_keys_must_match_asset_ids(self):
        with self.assertRaises(ValueError):
            CampaignLedger(readiness={"A": ReadyRecord("B", 1000.0, 500.0, turnaround_s=500.0)})