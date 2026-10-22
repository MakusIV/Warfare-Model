"""Tests per Logic/Session_Validator — validatore di sessione di campagna (F8a)."""
import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    CampaignLedger,
    ReadyRecord,
    SessionRecord,
    SessionRules,
    SessionValidationError,
    SessionViolation,
    ViolationCode,
)
from Code.Dynamic_War_Manager.Source.Command import Mission_Types as MT
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    EndCriteria,
    Mission,
    MissionAsset,
    MissionWaypoint,
    StartMode,
    Target,
    TargetKind,
    TargetProvenance,
    WaypointRole,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder
from Code.Dynamic_War_Manager.Source.Context.Context import MILITARY_CATEGORY
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Session_Validator import check_session, validate_session

_SOURCE = 'Code.Dynamic_War_Manager.Source.'
_LOGGERS = [_SOURCE + name + '.logger' for name in (
    'Logic.Session_Validator', 'Logic.Mission_Adapter', 'Command.Mission_Types',
    'Logic.Session_Simulator', 'Asset.Mobile', 'Asset.Asset')]


class _Vehicle(Mobile):
    """Unita' di terra di test."""


class _Aircraft(Mobile):
    """Aereo di test."""


def _make_asset(cls, asset_id, x, y, z=0.0, ammunition=20, fuel=1.0, speed=None):
    asset = cls(block=MagicMock(spec=Block), name=asset_id, position=Point3D(x, y, z))
    asset.id = asset_id
    asset.ammunition = ammunition
    asset.fuel = fuel
    if speed is not None:
        asset.speed = {'nominal': speed, 'max': speed}
    return asset


def _make_force(name, side, assets):
    military = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name=name, side=side)
    military.id = name
    military._assets = {a.id: a for a in assets}
    return military


def _make_route(points, speed, name, z=0.0):
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(x, y, z), obj_reference=None)
                 for i, (x, y) in enumerate(points)]
    edges = {}
    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type='offroad', danger_level=0.0,
                                        speed=speed, name=f'{name}-E{i}')
    return Route(route_type='ground', edges=edges, name=name)


def _make_air_route(points, speed, name, z=0.0):
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(x, y, z), obj_reference=None)
                 for i, (x, y) in enumerate(points)]
    edges = {}
    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0,
                                        speed=speed, name=f'{name}-E{i}')
    return Route(route_type='air', edges=edges, name=name)


def _make_mission(mission_id, block_id, domain, route, asset_ids, waypoints=None, start_time=0.0,
                  start_mode=None, end_criteria=None, target_block='Red',
                  mission_type=None):
    if waypoints is None:
        wps = MT.route_waypoints(route)
        waypoints = tuple(MissionWaypoint(wp, WaypointRole.NAV if i < len(wps) - 1 else WaypointRole.LAND)
                          for i, wp in enumerate(wps))
    members = tuple(MissionAsset(asset_id, 'lead') for asset_id in asset_ids)
    target = Target(kind=TargetKind.GROUP, target_id=target_block,
                    provenance=TargetProvenance.OBSERVED, observed_at=0.0)
    if mission_type is None:
        mission_type = 'CAS' if domain == 'air' else 'Movement'
    if start_mode is None:
        start_mode = StartMode.AIR if domain == 'air' else StartMode.GROUND
    return Mission(mission_id=mission_id, block_id=block_id, domain=domain, mission_type=mission_type,
                   assets=members, target=target, route=route, waypoints=waypoints,
                   start_time=start_time, start_mode=start_mode,
                   end_criteria=end_criteria or EndCriteria())


class _Base(unittest.TestCase):
    def setUp(self):
        self._patches = [patch(target, MagicMock()) for target in _LOGGERS]
        for p in self._patches:
            p.start()
        self._patches.append(patch.object(SS, 'F6_BINGO', True))
        self._patches[-1].start()

    def tearDown(self):
        for p in self._patches:
            p.stop()


class TestValidateSession(_Base):
    """Validatore di sessione."""

    def setUp(self):
        super().setUp()
        # Forze minime: un blocco di terra Blue con due veicoli.
        self.v1 = _make_asset(_Vehicle, 'v1', 0.0, 0.0, speed=20.0)
        self.v2 = _make_asset(_Vehicle, 'v2', 500.0, 0.0, speed=20.0)
        self.blue_force = _make_force('Blue', 'Blue', [self.v1, self.v2])
        # Un blocco Red vuoto (per il lato opposto).
        self.r1 = _make_asset(_Vehicle, 'r1', 10000.0, 0.0, speed=20.0)
        self.red_force = _make_force('Red', 'Red', [self.r1])

        # Rotta di terra: 10 km a 20 m/s -> 500 s.
        self.ground_route = _make_route([(0.0, 0.0), (10000.0, 0.0)], 20.0, 'r-ground')
        self.ground_mission = _make_mission('M-ground', 'Blue', 'ground', self.ground_route,
                                            ['v1', 'v2'])

        self.order = SessionOrder('S-test', t_start=0.0, t_end=3600.0,
                                  missions=(self.ground_mission,))

    def test_valid_order_returns_empty_violations(self):
        violations = validate_session(self.order, [self.blue_force], [self.red_force])
        self.assertEqual(violations, ())

    def test_check_session_valid_does_not_raise(self):
        check_session(self.order, [self.blue_force], [self.red_force])

    def test_session_open(self):
        order = SessionOrder('S-open', t_start=0.0, t_end=None,
                             missions=(self.ground_mission,))
        violations = validate_session(order, [self.blue_force], [self.red_force])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].code, ViolationCode.SESSION_OPEN)

    def test_session_too_long(self):
        order = SessionOrder('S-long', t_start=0.0, t_end=SessionRules().max_duration_s + 1.0,
                             missions=(self.ground_mission,))
        violations = validate_session(order, [self.blue_force], [self.red_force])
        self.assertTrue(any(v.code == ViolationCode.SESSION_TOO_LONG for v in violations))

    def test_session_overlap(self):
        r = SessionRecord('S-prev', 0.0, 7200.0)
        ledger = CampaignLedger(sessions=(r,))
        order = SessionOrder('S-now', t_start=3600.0, t_end=10800.0,
                             missions=(self.ground_mission,))
        violations = validate_session(order, [self.blue_force], [self.red_force], ledger=ledger)
        self.assertTrue(any(v.code == ViolationCode.SESSION_OVERLAP for v in violations))

    def test_block_missing(self):
        order = SessionOrder('S-bad', t_start=0.0, t_end=3600.0, missions=(self.ground_mission,))
        # Pass only the Red force (no Blue force).
        violations = validate_session(order, [], [self.red_force])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].code, ViolationCode.MISSION_ASSETS)
        self.assertEqual(violations[0].mission_id, 'M-ground')

    def test_asset_destroyed(self):
        # Distruggi v1 (health = 15 e' distrutto: soglia 15 da `State.Destroyed`).
        self.v1.health = 0
        violations = validate_session(self.order, [self.blue_force], [self.red_force])
        self.assertTrue(any(v.code == ViolationCode.ASSET_DESTROYED and v.asset_id == 'v1'
                            for v in violations))

    def test_asset_not_ready(self):
        ready = {'v1': ReadyRecord('v1', 10000.0, 0.0, turnaround_s=10000.0)}
        ledger = CampaignLedger(readiness=ready)
        violations = validate_session(self.order, [self.blue_force], [self.red_force], ledger=ledger)
        self.assertTrue(any(v.code == ViolationCode.ASSET_NOT_READY and v.asset_id == 'v1'
                            for v in violations))

    def test_mission_beyond_session(self):
        # Missione di terra che finisce a 500 s in sessione di 100 s.
        order = SessionOrder('S-short', t_start=0.0, t_end=100.0,
                             missions=(self.ground_mission,))
        violations = validate_session(order, [self.blue_force], [self.red_force])
        self.assertTrue(any(v.code == ViolationCode.MISSION_BEYOND_SESSION and v.mission_id == 'M-ground'
                            for v in violations))

    def test_fuel_minimum_and_bingo_at_start(self):
        # Mock check_mission_fuel e check_mission_bingo per una missione aerea.
        fuel_msg = "fuel too low"
        bingo_msg = "bingo at start"

        # Crea missione aerea.
        air_route = _make_air_route([(0.0, 0.0), (10000.0, 5000.0)], 200.0, 'r-air')
        a1 = _make_asset(_Aircraft, 'a1', 0.0, 0.0, speed=200.0)
        air_force = _make_force('Blue-Air', 'Blue', [a1])
        mission = _make_mission('M-air', 'Blue-Air', 'air', air_route, ['a1'],
                                end_criteria=EndCriteria(max_duration_s=100.0))

        order = SessionOrder('S-air', t_start=0.0, t_end=3600.0, missions=(mission,))

        with patch.object(MA, 'check_mission_fuel', side_effect=ValueError(fuel_msg)), \
             patch.object(MA, 'check_mission_bingo', side_effect=ValueError(bingo_msg)):
            violations = validate_session(order, [air_force], [self.red_force])
            codes = [v.code for v in violations]
            self.assertIn(ViolationCode.FUEL_MINIMUM, codes)
            self.assertIn(ViolationCode.BINGO_AT_START, codes)

    def test_only_fuel_minimum_when_bingo_off(self):
        fuel_msg = "fuel too low"
        bingo_msg = "bingo at start"

        air_route = _make_air_route([(0.0, 0.0), (10000.0, 5000.0)], 200.0, 'r-air')
        a1 = _make_asset(_Aircraft, 'a1', 0.0, 0.0, speed=200.0)
        air_force = _make_force('Blue-Air', 'Blue', [a1])
        mission = _make_mission('M-air', 'Blue-Air', 'air', air_route, ['a1'],
                                end_criteria=EndCriteria(max_duration_s=100.0))

        order = SessionOrder('S-air', t_start=0.0, t_end=3600.0, missions=(mission,))

        with patch.object(MA, 'check_mission_fuel', side_effect=ValueError(fuel_msg)), \
             patch.object(MA, 'check_mission_bingo', side_effect=ValueError(bingo_msg)), \
             patch.object(SS, 'F6_BINGO', False):
            violations = validate_session(order, [air_force], [self.red_force])
            codes = [v.code for v in violations]
            self.assertIn(ViolationCode.FUEL_MINIMUM, codes)
            self.assertNotIn(ViolationCode.BINGO_AT_START, codes)

    def test_multiple_violations_collected(self):
        # Ordine con sessione aperta e asset distrutto (il blocco esiste).
        self.v1.health = 0
        order = SessionOrder('S-multi', t_start=0.0, t_end=None,
                             missions=(self.ground_mission,))
        violations = validate_session(order, [self.blue_force], [self.red_force])
        codes = [v.code for v in violations]
        # Ordine atteso: finestra, poi disgiunzione, poi missioni.
        self.assertIn(ViolationCode.SESSION_OPEN, codes)
        self.assertIn(ViolationCode.ASSET_DESTROYED, codes)
        # SESSION_OPEN deve venire prima di ASSET_DESTROYED.
        self.assertLess(codes.index(ViolationCode.SESSION_OPEN),
                        codes.index(ViolationCode.ASSET_DESTROYED))

    def test_mission_with_bingo_false_not_checked_for_fuel(self):
        # Missione aerea con EndCriteria(bingo=False): check_mission_fuel restituisce None.
        air_route = _make_air_route([(0.0, 0.0), (10000.0, 5000.0)], 200.0, 'r-air')
        a1 = _make_asset(_Aircraft, 'a1', 0.0, 0.0, speed=200.0)
        air_force = _make_force('Blue-Air', 'Blue', [a1])
        mission = _make_mission('M-air', 'Blue-Air', 'air', air_route, ['a1'],
                                end_criteria=EndCriteria(bingo=False, max_duration_s=100.0))

        order = SessionOrder('S-air', t_start=0.0, t_end=3600.0, missions=(mission,))
        violations = validate_session(order, [air_force], [self.red_force])
        codes = [v.code for v in violations]
        # check_mission_fuel restituisce None per bingo=False -> nessuna violazione di carburante.
        # check_mission_bingo non chiamato per bingo=False.
        self.assertNotIn(ViolationCode.FUEL_MINIMUM, codes)
        self.assertNotIn(ViolationCode.BINGO_AT_START, codes)

    def test_ground_mission_on_site_allowed(self):
        # Missione di terra senza rotta (None).
        members = (MissionAsset('v1', 'lead'),)
        target = Target(kind=TargetKind.GROUP, target_id='Red',
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        mission = Mission(mission_id='M-site', block_id='Blue', domain='ground', mission_type='Movement',
                          assets=members, target=target, route=None, waypoints=(),
                          start_time=0.0, start_mode=StartMode.GROUND,
                          end_criteria=EndCriteria(max_duration_s=100.0))
        order = SessionOrder('S-site', t_start=0.0, t_end=3600.0, missions=(mission,))
        # mission_planned_end con max_duration_s restituisce start + duration = 0 + 100 = 100.
        violations = validate_session(order, [self.blue_force], [self.red_force])
        # 100 <= 3600, nessuna violazione di fine.
        codes = [v.code for v in violations]
        self.assertNotIn(ViolationCode.MISSION_BEYOND_SESSION, codes)
        self.assertNotIn(ViolationCode.MISSION_START_INVALID, codes)

    def test_validator_does_not_mutate_assets(self):
        fuel_before = self.v1.fuel
        health_before = getattr(self.v1, 'health', 100)
        pos_before = self.v1.position

        validate_session(self.order, [self.blue_force], [self.red_force])

        self.assertEqual(self.v1.fuel, fuel_before)
        self.assertEqual(getattr(self.v1, 'health', 100), health_before)
        self.assertEqual(self.v1.position, pos_before)

    def test_check_session_raises_on_violations(self):
        order = SessionOrder('S-bad', t_start=0.0, t_end=None,
                             missions=(self.ground_mission,))
        with self.assertRaises(SessionValidationError):
            check_session(order, [self.blue_force], [self.red_force])