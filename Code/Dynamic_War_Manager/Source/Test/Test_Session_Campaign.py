"""Tests per Logic/Session_Campaign — conduttore minimo del ciclo di campagna (F8c, blocco 2).

`apply_final_positions` (posizione persistente, decisione 22) e `run_campaign_session`
(validazione + esecuzione + posizioni + registrazione). `run_session` e' chiamata come
attributo del modulo (`SS.run_session`): nei test si patcha con `patch.object(SS, 'run_session')`.
"""
import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    CampaignLedger,
    ReadyRecord,
    SessionValidationError,
)
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    EndCriteria,
    Mission,
    MissionAsset,
    StartMode,
    Target,
    TargetKind,
    TargetProvenance,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Campaign as SC
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

_SOURCE = 'Code.Dynamic_War_Manager.Source.'
_SESSION_CAMPAIGN_LOGGER = _SOURCE + 'Logic.Session_Campaign.logger'


class _Base(unittest.TestCase):
    """Silenzia i logger del motore e tiene un riferimento al logger di Session_Campaign."""

    def setUp(self):
        self._sc_logger = MagicMock()
        self._patches = F.start_logger_patches()
        self._patches.append(patch(_SESSION_CAMPAIGN_LOGGER, self._sc_logger))
        self._patches[-1].start()

    def tearDown(self):
        for patcher in reversed(self._patches):
            patcher.stop()


def _ground_block():
    return F.make_force('Blue', 'Blue')


def _air_block():
    return F.make_force('Blue-Air', 'Blue', mil_category=F.AIR_UNIT)


def _outcome(final_positions=None, postures=None, **overrides):
    values = dict(session_id='S', t_start=0.0, t_end=3600.0,
                  final_positions=final_positions or {}, postures=postures or {})
    values.update(overrides)
    return SessionOutcome(**values)


class TestApplyFinalPositions(_Base):
    def setUp(self):
        super().setUp()
        self.block = _ground_block()
        self.vehicle = F.make_vehicle(self.block, 'v0', 'BMP-2', (0.0, 0.0, 0.0))
        self.other = F.make_vehicle(self.block, 'v1', 'BMP-2', (0.0, 0.0, 0.0))
        F.add_assets(self.block, [self.vehicle, self.other])

        self.air_block = _air_block()
        self.aircraft = F.make_aircraft(self.air_block, 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        F.add_assets(self.air_block, [self.aircraft])

    def test_ground_unit_moved(self):
        outcome = _outcome(final_positions={'v0': (100.0, 200.0, 0.0)},
                           postures={'v0': MA.GROUND_DEFENSE_POSTURE})
        applied = SC.apply_final_positions(outcome, [self.block], [])
        self.assertEqual(self.vehicle.position, Point3D(100.0, 200.0, 0.0))
        self.assertEqual(applied, {'v0': (100.0, 200.0, 0.0)})

    def test_parked_aircraft_moved(self):
        outcome = _outcome(final_positions={'ac0': (100.0, 200.0, 3000.0)},
                           postures={'ac0': MA.PARKED_POSTURE})
        applied = SC.apply_final_positions(outcome, [self.air_block], [])
        self.assertEqual(self.aircraft.position, Point3D(100.0, 200.0, 3000.0))
        self.assertEqual(applied, {'ac0': (100.0, 200.0, 3000.0)})

    def test_off_scene_aircraft_not_moved(self):
        outcome = _outcome(final_positions={'ac0': (100.0, 200.0, 3000.0)},
                           postures={'ac0': MA.OFF_SCENE_POSTURE})
        applied = SC.apply_final_positions(outcome, [self.air_block], [])
        self.assertEqual(self.aircraft.position, Point3D(0.0, 0.0, 0.0))
        self.assertEqual(applied, {})

    def test_airborne_aircraft_moved_with_warning(self):
        outcome = _outcome(final_positions={'ac0': (100.0, 200.0, 3000.0)},
                           postures={'ac0': 'Strike'})  # tipo di missione = in volo
        applied = SC.apply_final_positions(outcome, [self.air_block], [])
        self.assertEqual(self.aircraft.position, Point3D(100.0, 200.0, 3000.0))
        self.assertTrue(self._sc_logger.warning.called)

    def test_destroyed_aircraft_moved_without_warning(self):
        outcome = _outcome(final_positions={'ac0': (100.0, 200.0, 0.0)},
                           postures={'ac0': MA.DESTROYED_POSTURE})
        SC.apply_final_positions(outcome, [self.air_block], [])
        self.assertEqual(self.aircraft.position, Point3D(100.0, 200.0, 0.0))
        self.assertFalse(self._sc_logger.warning.called)

    def test_asset_without_position_untouched(self):
        # `v1` e' nelle forze ma non ha voce in final_positions: resta al suo posto.
        outcome = _outcome(final_positions={'v0': (100.0, 200.0, 0.0)},
                           postures={'v0': MA.GROUND_DEFENSE_POSTURE})
        SC.apply_final_positions(outcome, [self.block], [])
        self.assertEqual(self.other.position, Point3D(0.0, 0.0, 0.0))

    def test_coordinates_rounded_to_offset_decimals(self):
        outcome = _outcome(final_positions={'v0': (100.123456789, 200.987654321, 0.0)},
                           postures={'v0': MA.GROUND_DEFENSE_POSTURE})
        applied = SC.apply_final_positions(outcome, [self.block], [])
        self.assertEqual(applied['v0'], (100.123457, 200.987654, 0.0))
        self.assertEqual(self.vehicle.position, Point3D(100.123457, 200.987654, 0.0))


class TestRunCampaignSession(_Base):
    def setUp(self):
        super().setUp()
        self.block = _ground_block()
        self.vehicle = F.make_vehicle(self.block, 'v0', 'BMP-2', (0.0, 0.0, 0.0))
        F.add_assets(self.block, [self.vehicle])

    def _mission(self, asset_ids):
        members = tuple(MissionAsset(aid, 'lead') for aid in asset_ids)
        target = Target(kind=TargetKind.GROUP, target_id='Red',
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        return Mission(mission_id='m1', block_id='Blue', domain='ground', mission_type='Movement',
                       assets=members, target=target, route=None, waypoints=(),
                       start_time=0.0, start_mode=StartMode.GROUND, end_criteria=EndCriteria())

    def test_invalid_order_raises_and_does_not_call_run_session(self):
        order = SessionOrder('S', t_start=0.0, t_end=3600.0, missions=(self._mission(('v0',)),))
        # v0 non pronto a t=0 (turnaround in corso): il validatore rifiuta.
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 10000.0, 0.0, 10000.0, 0.0)})

        with patch.object(SS, 'run_session') as run_mock:
            with self.assertRaises(SessionValidationError):
                SC.run_campaign_session(ledger, order, [self.block], [],
                                        lambda shooter, target: None)
            run_mock.assert_not_called()

    def test_valid_order_calls_run_session_and_records(self):
        order = SessionOrder('S', t_start=0.0, t_end=3600.0, missions=())
        fake_outcome = SessionOutcome(session_id='S', t_start=0.0, t_end=3600.0)

        with patch.object(SS, 'run_session', return_value=fake_outcome) as run_mock:
            outcome, new_ledger = SC.run_campaign_session(
                CampaignLedger(), order, [self.block], [], lambda shooter, target: None)

        run_mock.assert_called_once()
        self.assertIs(outcome, fake_outcome)
        self.assertEqual(new_ledger.sessions[0].session_id, 'S')
        self.assertEqual(new_ledger.last_end, 3600.0)

    def test_absent_force_keeps_readiness_record(self):
        """Il record di un asset di una forza non passata alla sessione resta nel registro (difetto 26)."""
        record = ReadyRecord('ghost', 10000.0, 0.0, 10000.0, 0.0)
        order = SessionOrder('S', t_start=0.0, t_end=3600.0, missions=())
        fake_outcome = SessionOutcome(session_id='S', t_start=0.0, t_end=3600.0)

        with patch.object(SS, 'run_session', return_value=fake_outcome):
            _, new_ledger = SC.run_campaign_session(
                CampaignLedger(readiness={'ghost': record}), order, [self.block], [],
                lambda shooter, target: None)

        self.assertIn('ghost', new_ledger.readiness)
        self.assertEqual(new_ledger.readiness['ghost'], record)


if __name__ == '__main__':
    unittest.main()
