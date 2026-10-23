"""Tests per Logic/Readiness — prontezza e processi fra sessioni (F8c, blocco 1).

Asset REALI dei registri (`Scenario_Fixtures`), `Command` tipi costruiti a mano per gli
`SessionOutcome`/`SessionOrder`. Gli attesi di turnaround/riparazione sono ricalcolati dalle
costanti STIMATE dichiarate in `Context` (mai valori copiati a mano): il test verifica la
regola, non i numeri.
"""
import unittest
from unittest.mock import MagicMock, patch

from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    CampaignLedger,
    ReadyRecord,
)
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AssetEndReason,
    AssetMissionOutcome,
    AssetState,
    EndCriteria,
    Mission,
    MissionAsset,
    MissionOutcome,
    MissionStatus,
    StartMode,
    Target,
    TargetKind,
    TargetProvenance,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Context.Context import (
    AIR_TURNAROUND_DEFAULT_S,
    AIR_TURNAROUND_S,
    GROUND_TURNAROUND_S,
    REPAIR_TIME_FULL_S,
    SEA_TURNAROUND_S,
    Air_Asset_Type,
)
from Code.Dynamic_War_Manager.Source.Logic import Readiness as R
from Code.Dynamic_War_Manager.Source.Logic.Damage_Model import DamageEvent
from Code.Dynamic_War_Manager.Source.Logic.Fuel_Model import FuelEvent
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

_SOURCE = 'Code.Dynamic_War_Manager.Source.'
_READINESS_LOGGER = _SOURCE + 'Logic.Readiness.logger'


class _Base(unittest.TestCase):
    """Silenzia i logger del motore e tiene un riferimento al logger di Readiness (per i warning)."""

    def setUp(self):
        self._readiness_logger = MagicMock()
        # `F.start_logger_patches` salta i moduli senza `logger` (es. Context.Doctrine).
        self._patches = F.start_logger_patches()
        self._patches.append(patch(_READINESS_LOGGER, self._readiness_logger))
        self._patches[-1].start()

    def tearDown(self):
        for patcher in reversed(self._patches):
            patcher.stop()


def _air_block():
    return F.make_force('Blue-Air', 'Blue', mil_category=F.AIR_UNIT)


def _ground_block():
    return F.make_force('Blue', 'Blue')


def _sea_block():
    return F.make_force('Blue-Sea', 'Blue', mil_category=F.NAVAL_UNIT)


def _mission(mission_id, asset_ids):
    members = tuple(MissionAsset(aid, 'lead') for aid in asset_ids)
    target = Target(kind=TargetKind.GROUP, target_id='Red',
                    provenance=TargetProvenance.OBSERVED, observed_at=0.0)
    return Mission(mission_id=mission_id, block_id='Blue', domain='ground', mission_type='Movement',
                   assets=members, target=target, route=None, waypoints=(),
                   start_time=0.0, start_mode=StartMode.GROUND, end_criteria=EndCriteria())


def _order(session_id='S', t_start=0.0, t_end=3600.0, asset_ids=()):
    missions = (_mission('m1', asset_ids),) if asset_ids else ()
    return SessionOrder(session_id, t_start=t_start, t_end=t_end, missions=missions)


def _outcome(**overrides):
    values = dict(session_id='S', t_start=0.0, t_end=3600.0)
    values.update(overrides)
    return SessionOutcome(**values)


class TestAssetDomain(_Base):
    def setUp(self):
        super().setUp()
        self.aircraft = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        self.ship = F.make_ship(_sea_block(), 's0', 'USS Arleigh Burke IIa', (0.0, 0.0, 0.0))
        self.vehicle = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))

    def test_domains(self):
        self.assertEqual(R.asset_domain(self.aircraft), 'air')
        self.assertEqual(R.asset_domain(self.ship), 'sea')
        self.assertEqual(R.asset_domain(self.vehicle), 'ground')


class TestTurnaroundClass(_Base):
    def setUp(self):
        super().setUp()
        self.aircraft = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        self.vehicle = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))

    def test_string_asset_type(self):
        self.assertEqual(R.turnaround_class(self.aircraft), 'Fighter')

    def test_enum_asset_type(self):
        # Bypass del setter (che convertirebbe l'enum in stringa) per provare il ramo `.value`.
        self.aircraft._asset_type = Air_Asset_Type.BOMBER
        self.assertEqual(R.turnaround_class(self.aircraft), 'Bomber')

    def test_from_registry(self):
        # asset_type non nella tabella: si ricade sulla prima classe di Aircraft_Data (Fighter).
        self.aircraft._asset_type = 'Not_A_Key'
        self.assertEqual(R.turnaround_class(self.aircraft), 'Fighter')

    def test_unknown(self):
        self.aircraft._asset_type = 'Not_A_Key'
        self.aircraft._model = 'UnknownModel'
        self.assertIsNone(R.turnaround_class(self.aircraft))

    def test_non_aircraft_returns_none(self):
        self.assertIsNone(R.turnaround_class(self.vehicle))


class TestTurnaroundS(_Base):
    def setUp(self):
        super().setUp()
        self.aircraft = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        self.ship = F.make_ship(_sea_block(), 's0', 'USS Arleigh Burke IIa', (0.0, 0.0, 0.0))
        self.vehicle = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))

    def test_each_air_class(self):
        for cls in AIR_TURNAROUND_S:
            self.aircraft.asset_type = cls
            seconds, provenance = R.turnaround_s(self.aircraft)
            self.assertEqual(seconds, float(AIR_TURNAROUND_S[cls]))
            self.assertEqual(provenance, f'class:{cls}')

    def test_default_with_warning(self):
        self.aircraft._asset_type = 'Not_A_Key'
        self.aircraft._model = 'UnknownModel'
        seconds, provenance = R.turnaround_s(self.aircraft)
        self.assertEqual(seconds, float(AIR_TURNAROUND_DEFAULT_S))
        self.assertEqual(provenance, 'default')
        self.assertTrue(self._readiness_logger.warning.called)

    def test_ground(self):
        seconds, provenance = R.turnaround_s(self.vehicle)
        self.assertEqual(seconds, float(GROUND_TURNAROUND_S))
        self.assertEqual(provenance, 'ground')

    def test_sea(self):
        seconds, provenance = R.turnaround_s(self.ship)
        self.assertEqual(seconds, float(SEA_TURNAROUND_S))
        self.assertEqual(provenance, 'sea')


class TestRepairS(_Base):
    def setUp(self):
        super().setUp()
        self.aircraft = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        self.vehicle = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))

    def test_intact_is_zero(self):
        self.assertEqual(R.repair_s(self.aircraft), 0.0)

    def test_linear_in_damage(self):
        self.aircraft.health = 60
        self.assertAlmostEqual(R.repair_s(self.aircraft),
                               REPAIR_TIME_FULL_S['air'] * 0.4, places=6)

    def test_ground_domain(self):
        self.vehicle.health = 60
        self.assertAlmostEqual(R.repair_s(self.vehicle),
                               REPAIR_TIME_FULL_S['ground'] * 0.4, places=6)

    def test_destroyed_is_none(self):
        self.aircraft.health = 0
        self.assertIsNone(R.repair_s(self.aircraft))


class TestReadinessAfterSession(_Base):
    def setUp(self):
        super().setUp()
        self.ac0 = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        self.v0 = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))
        self.sh0 = F.make_ship(_sea_block(), 's0', 'USS Arleigh Burke IIa', (0.0, 0.0, 0.0))
        self.assets = {'ac0': self.ac0, 'v0': self.v0, 's0': self.sh0}

    def test_destroyed_asset_no_record(self):
        self.ac0.health = 0
        ready = R.readiness_after_session(CampaignLedger(), _order(asset_ids=('ac0',)),
                                          _outcome(), self.assets)
        self.assertNotIn('ac0', ready)

    def test_mission_asset_with_movement_ends(self):
        order = _order(asset_ids=('ac0',))
        outcome = _outcome(movement_ends={'ac0': 3000.0})
        rec = R.readiness_after_session(CampaignLedger(), order, outcome, self.assets)['ac0']
        self.assertEqual(rec.since, 3000.0)
        self.assertEqual(rec.turnaround_s, float(AIR_TURNAROUND_S['Fighter']))
        self.assertEqual(rec.repair_s, 0.0)
        self.assertEqual(rec.ready_at, 3000.0 + float(AIR_TURNAROUND_S['Fighter']))

    def test_mission_asset_falls_back_to_end_time(self):
        asset_outcomes = {'ac0': AssetMissionOutcome('ac0', AssetState.OPERATIONAL,
                                                     AssetEndReason.ROUTE_COMPLETED, 2500.0)}
        order = _order(asset_ids=('ac0',))
        outcome = _outcome(
            mission_outcomes={'m1': MissionOutcome('m1', MissionStatus.COMPLETED,
                                                   asset_outcomes=asset_outcomes)})
        rec = R.readiness_after_session(CampaignLedger(), order, outcome, self.assets)['ac0']
        self.assertEqual(rec.since, 2500.0)

    def test_asset_without_mission_that_consumed_fuel(self):
        fe = FuelEvent(time=100.0, asset_id='v0', distance=1000.0, distance_covered=1000.0,
                       amount=0.2, fuel_before=1.0, fuel_after=0.8, exhausted=False)
        rec = R.readiness_after_session(CampaignLedger(), _order(),
                                        _outcome(fuel_events=(fe,)), self.assets)['v0']
        self.assertEqual(rec.since, 3600.0)
        self.assertEqual(rec.turnaround_s, float(GROUND_TURNAROUND_S))
        self.assertEqual(rec.repair_s, 0.0)
        self.assertEqual(rec.ready_at, 3600.0 + float(GROUND_TURNAROUND_S))

    def test_damaged_without_session_novelty_repairs_only(self):
        self.v0.health = 60
        rec = R.readiness_after_session(CampaignLedger(), _order(),
                                        _outcome(), self.assets)['v0']
        self.assertEqual(rec.since, 3600.0)
        self.assertAlmostEqual(rec.repair_s, REPAIR_TIME_FULL_S['ground'] * 0.4, places=6)
        self.assertEqual(rec.turnaround_s, 0.0)

    def test_repair_in_progress_not_restarted(self):
        self.v0.health = 60
        prev = ReadyRecord('v0', 9000.0, 1000.0, 0.0, 8000.0)
        ledger = CampaignLedger(readiness={'v0': prev})
        ready = R.readiness_after_session(ledger, _order(), _outcome(), self.assets)
        self.assertEqual(ready['v0'], prev)

    def test_damage_in_session_sets_since_to_last_damage(self):
        self.ac0.health = 60
        damage = (DamageEvent(time=4000.0, target_id='ac0', outcome='damage',
                              health_before=100, health_delta=-40, health_after=60,
                              destroyed=False),)
        order = _order(asset_ids=('ac0',))
        rec = R.readiness_after_session(CampaignLedger(), order,
                                        _outcome(movement_ends={'ac0': 2000.0},
                                                 damage_events=damage),
                                        self.assets)['ac0']
        self.assertEqual(rec.since, 4000.0)
        self.assertAlmostEqual(rec.repair_s, REPAIR_TIME_FULL_S['air'] * 0.4, places=6)
        self.assertEqual(rec.turnaround_s, float(AIR_TURNAROUND_S['Fighter']))

    def test_longer_previous_record_prevails(self):
        prev = ReadyRecord('ac0', 20000.0, 5000.0, 15000.0, 0.0)
        ledger = CampaignLedger(readiness={'ac0': prev})
        order = _order(asset_ids=('ac0',))
        rec = R.readiness_after_session(ledger, order, _outcome(movement_ends={'ac0': 3000.0}),
                                        self.assets)['ac0']
        self.assertEqual(rec.ready_at, 20000.0)

    def test_record_session(self):
        order = _order(asset_ids=('ac0',))
        ledger = R.record_session(CampaignLedger(), order, _outcome(movement_ends={'ac0': 3000.0}),
                                  self.assets)
        self.assertEqual(ledger.sessions[0].session_id, 'S')
        self.assertEqual(ledger.last_end, 3600.0)
        self.assertIn('ac0', ledger.readiness)

    def test_record_session_open_order_uses_outcome_end(self):
        order = _order(t_end=None, asset_ids=())
        ledger = R.record_session(CampaignLedger(), order, _outcome(t_end=5000.0), self.assets)
        self.assertEqual(ledger.last_end, 5000.0)


class TestApplyCampaignProcesses(_Base):
    def setUp(self):
        super().setUp()
        self.ac0 = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0),
                                   loadout='Strike')
        self.v0 = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))
        self.assets = {'ac0': self.ac0, 'v0': self.v0}

    def test_repair_sets_health_to_100(self):
        self.v0.health = 60
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 1000.0, 0.0, 0.0, 1000.0)})
        new = R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertEqual(self.v0.health, 100)
        self.assertIsNone(new.ready_at('v0'))

    def test_rearm_refuels_aircraft_and_restores_stores(self):
        stores_before = dict(self.ac0.stores or {})
        self.ac0.fuel = 0.4
        self.ac0.stores = {}
        ledger = CampaignLedger(readiness={'ac0': ReadyRecord('ac0', 1000.0, 0.0, 1000.0, 0.0)})
        R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertEqual(self.ac0.fuel, 1.0)
        self.assertEqual(dict(self.ac0.stores or {}), stores_before)

    def test_refuel_vehicle(self):
        self.v0.fuel = 0.3
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 1000.0, 0.0, 1000.0, 0.0)})
        R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertEqual(self.v0.fuel, 1.0)

    def test_not_concluded_record_remains(self):
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 5000.0, 0.0, 5000.0, 0.0)})
        new = R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertEqual(new.ready_at('v0'), 5000.0)

    def test_absent_asset_dropped_with_warning(self):
        ledger = CampaignLedger(readiness={'ghost': ReadyRecord('ghost', 1000.0, 0.0, 1000.0, 0.0)})
        new = R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertIsNone(new.ready_at('ghost'))
        self.assertTrue(self._readiness_logger.warning.called)

    def test_destroyed_asset_record_dropped(self):
        self.v0.health = 0
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 1000.0, 0.0, 1000.0, 0.0)})
        new = R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertIsNone(new.ready_at('v0'))
        self.assertEqual(self.v0.health, 0)

    def test_idempotent(self):
        self.v0.fuel = 0.3
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 1000.0, 0.0, 1000.0, 0.0)})
        R.apply_campaign_processes(ledger, self.assets, 1000.0)
        fuel_after_first = self.v0.fuel
        R.apply_campaign_processes(ledger, self.assets, 1000.0)
        self.assertEqual(self.v0.fuel, fuel_after_first)


class TestReadyAssets(_Base):
    def setUp(self):
        super().setUp()
        self.ac0 = F.make_aircraft(_air_block(), 'ac0', 'F-16C Block 52d', (0.0, 0.0, 0.0))
        self.v0 = F.make_vehicle(_ground_block(), 'v0', 'BMP-2', (0.0, 0.0, 0.0))
        self.sh0 = F.make_ship(_sea_block(), 's0', 'USS Arleigh Burke IIa', (0.0, 0.0, 0.0))
        self.assets = {'ac0': self.ac0, 'v0': self.v0, 's0': self.sh0}

    def test_ready_assets(self):
        self.sh0.health = 0
        ledger = CampaignLedger(readiness={'v0': ReadyRecord('v0', 9000.0, 1000.0, 8000.0, 0.0)})
        self.assertEqual(R.ready_assets(ledger, self.assets, 3600.0), ('ac0',))
        self.assertEqual(R.ready_assets(ledger, self.assets, 10000.0), ('ac0', 'v0'))