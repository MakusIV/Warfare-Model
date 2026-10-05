"""Tests per Command/Mission_Types — tipi di dominio della Missione (Fase 1 del piano Missione).

Solo costruzione e validazione: nessun altro modulo usa ancora questi tipi. Waypoint, Edge e Route
sono oggetti reali (classi geometriche pure, nessun mock), come in Test_Route.
"""

import unittest
from types import MappingProxyType
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command import Mission_Types as MT
from Code.Dynamic_War_Manager.Source.Command.Attack_Types import AttackProfile
from Code.Dynamic_War_Manager.Source.Context.Context import Mission_Category
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint

_MT_LOGGER = 'Code.Dynamic_War_Manager.Source.Command.Mission_Types.logger'


def _wp(name, x, y, z=0.0):
    return Waypoint(name=name, point=Point3D(x, y, z), obj_reference=None)


def _route(waypoints, route_type='air', path_type='air', speed=200.0):
    edges = {}

    for a, b in zip(waypoints, waypoints[1:]):
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type=path_type, danger_level=0.0, speed=speed,
                                       name=f"{a.name}{b.name}")

    return Route(route_type=route_type, edges=edges, name='r')


def _air_plan(start_eta=0.0, locked=True):
    """Base -> IP -> attacco -> base: rotta reale e piano di missione con ETA crescenti."""
    wps = [_wp('BASE', 0, 0), _wp('IP', 20000, 0, 3000), _wp('TGT', 30000, 0, 3000), _wp('HOME', 0, 1000)]
    roles = [MT.WaypointRole.DEPARTURE, MT.WaypointRole.IP, MT.WaypointRole.ATTACK, MT.WaypointRole.LAND]
    etas = [start_eta, start_eta + 300, start_eta + 360, start_eta + 900]
    plan = tuple(MT.MissionWaypoint(waypoint=w, role=r, planned_eta=e, eta_locked=(locked and i == 0))
                 for i, (w, r, e) in enumerate(zip(wps, roles, etas)))

    return _route(wps), plan


def _target_asset():
    return MT.Target(kind=MT.TargetKind.ASSET, target_id='sam_1', provenance=MT.TargetProvenance.OBSERVED,
                     observed_at=-120.0)


def _zone(radius=5000.0):
    return MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(1000, 1000, 0), radius_m=radius)


def _air_mission(**overrides):
    route, plan = _air_plan()
    kwargs = dict(mission_id='m_air', block_id='wing_1', domain='air', mission_type='Strike',
                  assets=(MT.MissionAsset('f16_1', 'lead'), MT.MissionAsset('f16_2', 'wingman', right_m=200.0)),
                  target=_target_asset(), route=route, waypoints=plan)
    kwargs.update(overrides)

    return MT.Mission(**kwargs)


def _ground_mission(**overrides):
    wps = [_wp('A', 0, 0), _wp('B', 5000, 0), _wp('C', 5000, 5000)]
    plan = tuple(MT.MissionWaypoint(waypoint=w, role=r) for w, r in
                 zip(wps, (MT.WaypointRole.ASSEMBLY, MT.WaypointRole.NAV, MT.WaypointRole.OBJECTIVE)))
    kwargs = dict(mission_id='m_gnd', block_id='bde_1', domain='ground', mission_type='Attack',
                  assets=(MT.MissionAsset('t72_1', 'lead'), MT.MissionAsset('t72_2', 'main', forward_m=-50.0)),
                  target=MT.Target(kind=MT.TargetKind.AREA, position=Point3D(5000, 5000, 0), radius_m=500.0,
                                   provenance=MT.TargetProvenance.ESTIMATED, estimated_at=-600.0,
                                   uncertainty_m=300.0),
                  route=_route(wps, route_type='ground', path_type='offroad', speed=10.0),
                  waypoints=plan, start_time=60.0)
    kwargs.update(overrides)

    return MT.Mission(**kwargs)


class _LoggerMock:
    """Mixin (NON eredita da TestCase): mocka il logger del modulo."""

    def setUp(self):
        self._log = patch(_MT_LOGGER, MagicMock())
        self.logger = self._log.start()

    def tearDown(self):
        self._log.stop()


# ── Target ────────────────────────────────────────────────────────────────────

class TestTarget(_LoggerMock, unittest.TestCase):

    def test_none_default(self):
        target = MT.Target.none()
        self.assertIs(target.kind, MT.TargetKind.NONE)
        self.assertIsNone(target.target_id)

    def test_none_rejects_fields(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.NONE, target_id='x')

    def test_observed_asset(self):
        target = _target_asset()
        self.assertIs(target.provenance, MT.TargetProvenance.OBSERVED)
        self.assertEqual(target.observed_at, -120.0)

    def test_kind_from_string(self):
        self.assertIs(MT.Target(kind='zone', position=Point3D(0, 0, 0), radius_m=10).kind, MT.TargetKind.ZONE)

    def test_asset_needs_id_and_observed(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.ASSET, provenance=MT.TargetProvenance.OBSERVED, observed_at=0)

        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.GROUP, target_id='g')

        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.ASSET, target_id='a', position=Point3D(0, 0, 0),
                      provenance=MT.TargetProvenance.ESTIMATED, estimated_at=0, uncertainty_m=10)

    def test_asset_rejects_radius(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.ASSET, target_id='a', radius_m=10, provenance='observed', observed_at=0)

    def test_observed_needs_time(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.ASSET, target_id='a', provenance=MT.TargetProvenance.OBSERVED)

    def test_point_area_zone_need_position(self):
        for kind in (MT.TargetKind.POINT, MT.TargetKind.AREA, MT.TargetKind.ZONE):
            with self.assertRaises(ValueError):
                MT.Target(kind=kind, radius_m=10)

    def test_area_zone_need_radius(self):
        for kind in (MT.TargetKind.AREA, MT.TargetKind.ZONE):
            with self.assertRaises(ValueError):
                MT.Target(kind=kind, position=Point3D(0, 0, 0))

        point = MT.Target(kind=MT.TargetKind.POINT, position=Point3D(0, 0, 0))
        self.assertIsNone(point.radius_m)

    def test_position_type(self):
        with self.assertRaises(TypeError):
            MT.Target(kind=MT.TargetKind.POINT, position=(0, 0, 0))

    def test_estimated_requires_all(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.POINT, position=Point3D(0, 0, 0),
                      provenance=MT.TargetProvenance.ESTIMATED, estimated_at=0)

        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.POINT, position=Point3D(0, 0, 0), provenance='estimated',
                      estimated_at=0, uncertainty_m=1, observed_at=0)

    def test_times_without_provenance(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.POINT, position=Point3D(0, 0, 0), estimated_at=0)

    def test_negative_uncertainty(self):
        with self.assertRaises(ValueError):
            MT.Target(kind=MT.TargetKind.POINT, position=Point3D(0, 0, 0), provenance='estimated',
                      estimated_at=0, uncertainty_m=-1)

    def test_bad_kind(self):
        with self.assertRaises(ValueError):
            MT.Target(kind='building')


# ── Azioni e waypoint ─────────────────────────────────────────────────────────

class TestStartCondition(_LoggerMock, unittest.TestCase):

    def test_factories(self):
        self.assertIs(MT.StartCondition.on_arrival().kind, MT.StartConditionKind.ON_ARRIVAL)
        self.assertEqual(MT.StartCondition.at_time(100).time, 100.0)
        self.assertEqual(MT.StartCondition.after_duration(30).duration_s, 30.0)

    def test_mismatched_fields(self):
        with self.assertRaises(ValueError):
            MT.StartCondition(kind=MT.StartConditionKind.AT_TIME)

        with self.assertRaises(ValueError):
            MT.StartCondition(kind=MT.StartConditionKind.ON_ARRIVAL, time=10)

        with self.assertRaises(ValueError):
            MT.StartCondition(kind=MT.StartConditionKind.AFTER_DURATION, duration_s=10, time=5)

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            MT.StartCondition.at_time(-1)

        with self.assertRaises(ValueError):
            MT.StartCondition.after_duration(0)

        with self.assertRaises(TypeError):
            MT.StartCondition.at_time('10')


class TestMissionAction(_LoggerMock, unittest.TestCase):

    def test_task_params_immutable(self):
        params = {'weapon': 'Mk-82', 'quantity': 4}
        action = MT.MissionAction(MT.ActionKind.TASK, 'Attack_Target', params=params, priority=1)
        self.assertIsInstance(action.params, MappingProxyType)
        params['quantity'] = 99
        self.assertEqual(action.params['quantity'], 4)

        with self.assertRaises(TypeError):
            action.params['quantity'] = 2

    def test_wait_with_duration_or_until(self):
        hold = MT.MissionAction(MT.ActionKind.WAIT, 'Hold', wait_mode='hold', wait_duration_s=600)
        orbit = MT.MissionAction('wait', 'Orbit', wait_mode='orbit', wait_until=1800)
        self.assertEqual(hold.wait_duration_s, 600.0)
        self.assertIs(orbit.kind, MT.ActionKind.WAIT)

    def test_wait_needs_exactly_one_end(self):
        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.WAIT, 'Hold', wait_mode='hold')

        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.WAIT, 'Hold', wait_mode='hold', wait_duration_s=1, wait_until=10)

    def test_wait_mode(self):
        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.WAIT, 'Hold', wait_duration_s=10)

        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.WAIT, 'Hold', wait_mode='loiter', wait_duration_s=10)

    def test_wait_fields_only_for_wait(self):
        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.TASK, 'Orbit', wait_duration_s=10)

    def test_priority_and_name(self):
        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.RULE, 'Set_ROE', priority=-1)

        with self.assertRaises(ValueError):
            MT.MissionAction(MT.ActionKind.RULE, 'Set_ROE', priority=True)

        with self.assertRaises(TypeError):
            MT.MissionAction(MT.ActionKind.COMMAND, '')

    def test_params_and_start_types(self):
        with self.assertRaises(TypeError):
            MT.MissionAction(MT.ActionKind.TASK, 'T', params=[('a', 1)])

        with self.assertRaises(TypeError):
            MT.MissionAction(MT.ActionKind.TASK, 'T', start='on_arrival')


class TestMissionWaypoint(_LoggerMock, unittest.TestCase):

    def test_contains_waypoint(self):
        wp = _wp('A', 0, 0)
        mw = MT.MissionWaypoint(waypoint=wp, role='ip', planned_eta=100, speed_kmh=800,
                                altitude_reference='AGL',
                                actions=[MT.MissionAction(MT.ActionKind.TASK, 'Bombing')])
        self.assertIs(mw.waypoint, wp)
        self.assertIs(mw.role, MT.WaypointRole.IP)
        self.assertIsInstance(mw.actions, tuple)

    def test_waypoint_type(self):
        with self.assertRaises(TypeError):
            MT.MissionWaypoint(waypoint=Point3D(0, 0, 0))

    def test_locked_needs_eta(self):
        with self.assertRaises(ValueError):
            MT.MissionWaypoint(waypoint=_wp('A', 0, 0), eta_locked=True)

    def test_speed_and_altitude_reference(self):
        with self.assertRaises(ValueError):
            MT.MissionWaypoint(waypoint=_wp('A', 0, 0), speed_kmh=0)

        with self.assertRaises(ValueError):
            MT.MissionWaypoint(waypoint=_wp('A', 0, 0), altitude_reference='baro')

    def test_actions_type(self):
        with self.assertRaises(TypeError):
            MT.MissionWaypoint(waypoint=_wp('A', 0, 0), actions=('Bombing',))

    def test_wait_until_before_eta(self):
        wait = MT.MissionAction(MT.ActionKind.WAIT, 'Hold', wait_mode='hold', wait_until=50)

        with self.assertRaises(ValueError):
            MT.MissionWaypoint(waypoint=_wp('A', 0, 0), planned_eta=100, actions=(wait,))

    def test_start_time_before_eta(self):
        action = MT.MissionAction(MT.ActionKind.TASK, 'T', start=MT.StartCondition.at_time(50))

        with self.assertRaises(ValueError):
            MT.MissionWaypoint(waypoint=_wp('A', 0, 0), planned_eta=100, actions=(action,))


# ── Asset, criteri, regole ────────────────────────────────────────────────────

class TestMissionAsset(_LoggerMock, unittest.TestCase):

    def test_valid(self):
        asset = MT.MissionAsset('a1', 'escort', forward_m=-100, right_m=50, up_m=20)
        self.assertEqual((asset.forward_m, asset.right_m, asset.up_m), (-100.0, 50.0, 20.0))

    def test_unknown_role(self):
        with self.assertRaises(ValueError):
            MT.MissionAsset('a1', 'captain')

    def test_bad_id_and_offset(self):
        with self.assertRaises(TypeError):
            MT.MissionAsset('', 'lead')

        with self.assertRaises(TypeError):
            MT.MissionAsset('a1', 'lead', forward_m=float('nan'))


class TestEndCriteria(_LoggerMock, unittest.TestCase):

    def test_defaults(self):
        criteria = MT.EndCriteria()
        self.assertTrue(criteria.last_waypoint)
        self.assertTrue(criteria.bingo)
        self.assertEqual(criteria.winchester, ())

    def test_full(self):
        criteria = MT.EndCriteria(last_waypoint=False, max_duration_s=3600, winchester=['MISSILES_AAM'],
                                  abort_on_threat=True, damage_threshold=0.5, target_destroyed=True)
        self.assertEqual(criteria.winchester, ('MISSILES_AAM',))

    def test_must_end(self):
        with self.assertRaises(ValueError):
            MT.EndCriteria(last_waypoint=False)

    def test_damage_threshold_range(self):
        for bad in (0, -0.1, 1.5):
            with self.assertRaises(ValueError):
                MT.EndCriteria(damage_threshold=bad)

    def test_winchester(self):
        with self.assertRaises(TypeError):
            MT.EndCriteria(winchester='BOMBS')

        with self.assertRaises(ValueError):
            MT.EndCriteria(winchester=('BOMBS', 'BOMBS'))

    def test_bool_fields(self):
        with self.assertRaises(TypeError):
            MT.EndCriteria(bingo=1)


class TestMissionRules(_LoggerMock, unittest.TestCase):

    def test_defaults_per_domain(self):
        air = MT.MissionRules().for_domain('air')
        ground = MT.MissionRules().for_domain('ground')
        self.assertEqual(air.roe, 'weapon_free')
        self.assertEqual(air.threat_reaction, 'evade_fire')
        self.assertIsNone(air.alarm_state)
        self.assertEqual(ground.alarm_state, 'auto')
        self.assertIsNone(ground.threat_reaction)

    def test_air_roe_five_levels(self):
        for roe in MT.AIR_ROE:
            self.assertEqual(MT.MissionRules(roe=roe).for_domain('air').roe, roe)

    def test_surface_roe_three_levels(self):
        self.assertEqual(MT.MissionRules(roe='return_fire').for_domain('sea').roe, 'return_fire')

        with self.assertRaises(ValueError):
            MT.MissionRules(roe='only_designated').for_domain('ground')

    def test_unknown_values(self):
        with self.assertRaises(ValueError):
            MT.MissionRules(roe='fire_at_will')

        with self.assertRaises(ValueError):
            MT.MissionRules(emcon='off')

        with self.assertRaises(ValueError):
            MT.MissionRules(formation='blob')

    def test_domain_applicability(self):
        with self.assertRaises(ValueError):
            MT.MissionRules(alarm_state='red').for_domain('air')

        with self.assertRaises(ValueError):
            MT.MissionRules(threat_reaction='evade_fire').for_domain('sea')

        with self.assertRaises(ValueError):
            MT.MissionRules(formation='finger_four').for_domain('ground')

        with self.assertRaises(ValueError):
            MT.MissionRules().for_domain('space')


# ── Missione ──────────────────────────────────────────────────────────────────

class TestMissionValid(_LoggerMock, unittest.TestCase):

    def test_air_strike(self):
        mission = _air_mission(loadout='strike_mk82', operation_id='op_1',
                               rules=MT.MissionRules(roe='only_designated', formation='finger_four'),
                               end_criteria=MT.EndCriteria(winchester=('BOMBS',), target_destroyed=True))
        self.assertIs(mission.category, Mission_Category.ATTACK)
        self.assertIs(mission.start_mode, MT.StartMode.RUNWAY)
        self.assertEqual(mission.rules.roe, 'only_designated')
        self.assertEqual(mission.rules.threat_reaction, 'evade_fire')
        self.assertEqual(mission.asset_ids, ('f16_1', 'f16_2'))
        self.assertIs(mission.waypoints[1].waypoint, MT.route_waypoints(mission.route)[1])

    def test_air_with_attack_profile(self):
        profile = AttackProfile(target_id='sam_1', target_point=Point3D(30000, 0, 0), weapon='Mk-82',
                                feasible=True)
        self.assertIs(_air_mission(attack_profile=profile).attack_profile, profile)

    def test_air_start_in_air_without_departure(self):
        wps = [_wp('ENTRY', 0, 0, 5000), _wp('CAP', 50000, 0, 8000), _wp('HOME', 90000, 0)]
        plan = (MT.MissionWaypoint(waypoint=wps[0], role='nav', planned_eta=0, eta_locked=True),
                MT.MissionWaypoint(waypoint=wps[1], role='station',
                                   actions=(MT.MissionAction('wait', 'Orbit', wait_mode='orbit',
                                                             wait_duration_s=1800),)),
                MT.MissionWaypoint(waypoint=wps[2], role='land'))
        mission = MT.Mission(mission_id='cap', block_id='wing_1', domain='air', mission_type='CAP',
                             assets=(MT.MissionAsset('su27_1', 'lead'),), target=_zone(),
                             route=_route(wps), waypoints=plan, start_mode='air')
        self.assertIs(mission.category, Mission_Category.POSITIONING)

    def test_air_support_without_target(self):
        wps = [_wp('BASE', 0, 0), _wp('ORBIT', 50000, 0, 9000), _wp('BASE2', 0, 0)]
        plan = (MT.MissionWaypoint(waypoint=wps[0], role='departure'),
                MT.MissionWaypoint(waypoint=wps[1], role='station'),
                MT.MissionWaypoint(waypoint=wps[2], role='land'))
        mission = MT.Mission(mission_id='awacs', block_id='wing_2', domain='air', mission_type='AWACS',
                             assets=(MT.MissionAsset('e3_1', 'support'),), route=_route(wps), waypoints=plan,
                             start_time=0, start_mode=MT.StartMode.PARKING_COLD)
        self.assertIs(mission.category, Mission_Category.SUPPORT)
        self.assertIs(mission.target.kind, MT.TargetKind.NONE)

    def test_ground_attack(self):
        mission = _ground_mission(rules=MT.MissionRules(alarm_state='red', formation='wedge'))
        self.assertIs(mission.category, Mission_Category.ATTACK)
        self.assertIs(mission.start_mode, MT.StartMode.GROUND)
        self.assertEqual(mission.rules.alarm_state, 'red')

    def test_ground_static_defense(self):
        mission = MT.Mission(mission_id='def', block_id='bde_1', domain='ground', mission_type='Defense',
                             assets=(MT.MissionAsset('sa8_1', 'support'),), target=_zone(), start_time=0)
        self.assertEqual(mission.waypoints, ())
        self.assertIs(mission.category, Mission_Category.POSITIONING)

    def test_sea_escort_group(self):
        wps = [_wp('P0', 0, 0), _wp('P1', 100000, 0)]
        plan = tuple(MT.MissionWaypoint(waypoint=w, role='nav') for w in wps)
        mission = MT.Mission(mission_id='esc', block_id='fleet_1', domain='sea', mission_type='Escort',
                             assets=(MT.MissionAsset('ffg_1', 'lead'), MT.MissionAsset('ffg_2', 'escort')),
                             target=MT.Target(kind='group', target_id='convoy_1', provenance='observed',
                                              observed_at=0),
                             route=_route(wps, route_type='water', path_type='water', speed=10.0),
                             waypoints=plan, tot=3600, activation=MT.Activation.ON_EVENT,
                             activation_event='convoy_departed')
        self.assertIs(mission.category, Mission_Category.POSITIONING)
        self.assertEqual(mission.rules.alarm_state, 'auto')

    def test_frozen(self):
        mission = _air_mission()

        with self.assertRaises(Exception):
            mission.priority = 3


class TestMissionInvalid(_LoggerMock, unittest.TestCase):

    def test_domain_and_type(self):
        with self.assertRaises(ValueError):
            _air_mission(domain='space')

        with self.assertRaises(ValueError):
            _air_mission(mission_type='Shore_Bombardment')

        with self.assertRaises(ValueError):
            _ground_mission(mission_type='CAS')

    def test_ids(self):
        with self.assertRaises(TypeError):
            _air_mission(mission_id='')

        with self.assertRaises(TypeError):
            _air_mission(block_id=None)

    def test_assets(self):
        with self.assertRaises(ValueError):
            _air_mission(assets=())

        with self.assertRaises(ValueError):
            _air_mission(assets=(MT.MissionAsset('a', 'lead'), MT.MissionAsset('a', 'wingman')))

        with self.assertRaises(TypeError):
            _air_mission(assets=('f16_1',))

    def test_role_not_of_domain(self):
        with self.assertRaises(ValueError):
            _air_mission(assets=(MT.MissionAsset('f16_1', 'rear'),))

        with self.assertRaises(ValueError):
            _ground_mission(assets=(MT.MissionAsset('t72_1', 'sead'),))

    def test_category_target_coherence(self):
        with self.assertRaises(ValueError):
            _air_mission(target=MT.Target.none())          # ATTACK senza bersaglio

        with self.assertRaises(ValueError):                # POSITIONING su un asset
            _ground_mission(mission_type='Defense', target=_target_asset())

        with self.assertRaises(ValueError):                # SUPPORT su un gruppo
            _ground_mission(mission_type='Recon',
                            target=MT.Target(kind='group', target_id='g', provenance='observed', observed_at=0))

    def test_route_waypoints_mismatch(self):
        route, plan = _air_plan()

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=plan[:-1])

        other = (MT.MissionWaypoint(waypoint=_wp('BASE', 0, 0), role='departure', planned_eta=0,
                                    eta_locked=True),) + plan[1:]

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=other)

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=(plan[0], plan[2], plan[1], plan[3]))

    def test_route_type_for_domain(self):
        wps = [_wp('A', 0, 0), _wp('B', 1000, 0)]
        plan = tuple(MT.MissionWaypoint(waypoint=w) for w in wps)

        with self.assertRaises(ValueError):
            _ground_mission(route=_route(wps, route_type='air'), waypoints=plan)

        with self.assertRaises(TypeError):
            _ground_mission(route='r1', waypoints=plan)

    def test_air_needs_departure_and_land(self):
        route, plan = _air_plan()
        no_land = plan[:-1] + (MT.MissionWaypoint(waypoint=plan[-1].waypoint, role='egress',
                                                  planned_eta=plan[-1].planned_eta),)

        with self.assertRaises(ValueError):
            _air_mission(waypoints=no_land)

        no_dep = (MT.MissionWaypoint(waypoint=plan[0].waypoint, role='nav', planned_eta=0, eta_locked=True),) \
            + plan[1:]

        with self.assertRaises(ValueError):
            _air_mission(waypoints=no_dep)

        with self.assertRaises(ValueError):
            _air_mission(route=None, waypoints=())

    def test_start_mode_for_domain(self):
        with self.assertRaises(ValueError):
            _ground_mission(start_mode=MT.StartMode.RUNWAY)

        with self.assertRaises(ValueError):
            _air_mission(start_mode='catapult')

    def test_locked_instant_required(self):
        route, plan = _air_plan(locked=False)

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=plan)

        self.assertEqual(_air_mission(route=route, waypoints=plan, tot=360).tot, 360.0)

    def test_etas_increasing(self):
        route, plan = _air_plan()
        swapped = (plan[0], plan[1],
                   MT.MissionWaypoint(waypoint=plan[2].waypoint, role='attack', planned_eta=200),
                   plan[3])

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=swapped)

        equal = (plan[0], plan[1],
                 MT.MissionWaypoint(waypoint=plan[2].waypoint, role='attack', planned_eta=300),
                 plan[3])

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=equal)

    def test_eta_before_start_time(self):
        route, plan = _air_plan(start_eta=0.0)

        with self.assertRaises(ValueError):
            _air_mission(route=route, waypoints=plan, start_time=100)

    def test_tot_before_start(self):
        with self.assertRaises(ValueError):
            _ground_mission(start_time=100, tot=50)

    def test_activation(self):
        with self.assertRaises(ValueError):
            _air_mission(activation=MT.Activation.AT_TIME)            # senza start_time

        with self.assertRaises(ValueError):
            _air_mission(activation=MT.Activation.ON_EVENT)           # senza evento

        with self.assertRaises(ValueError):
            _air_mission(activation_event='x')                        # evento senza ON_EVENT

        self.assertIs(_ground_mission(activation='at_time').activation, MT.Activation.AT_TIME)

    def test_rules_for_domain(self):
        with self.assertRaises(ValueError):
            _ground_mission(rules=MT.MissionRules(roe='priority_designated'))

        with self.assertRaises(TypeError):
            _ground_mission(rules={'roe': 'weapon_free'})

    def test_target_destroyed_needs_destroyable_target(self):
        with self.assertRaises(ValueError):
            _ground_mission(mission_type='Defense', target=_zone(),
                            end_criteria=MT.EndCriteria(target_destroyed=True))

    def test_loadout_and_profile_only_air(self):
        with self.assertRaises(ValueError):
            _ground_mission(loadout='x')

        profile = AttackProfile(target_id=None, target_point=Point3D(0, 0, 0), weapon='w', feasible=False)

        with self.assertRaises(ValueError):
            _ground_mission(attack_profile=profile)

        with self.assertRaises(TypeError):
            _air_mission(attack_profile='profile')

    def test_priority(self):
        with self.assertRaises(ValueError):
            _air_mission(priority=-1)

    def test_target_type(self):
        with self.assertRaises(TypeError):
            _air_mission(target='sam_1')


class TestRouteWaypoints(_LoggerMock, unittest.TestCase):

    def test_order_follows_edges_not_names(self):
        wps = [_wp('Z', 0, 0), _wp('A', 1000, 0), _wp('M', 2000, 0)]
        self.assertEqual([w.name for w in MT.route_waypoints(_route(wps))], ['Z', 'A', 'M'])

    def test_disconnected_edges_keep_both_ends(self):
        a, b, c, d = _wp('A', 0, 0), _wp('B', 1, 0), _wp('C', 2, 0), _wp('D', 3, 0)
        edges = {('A', 'B'): Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0, speed=1.0, name='AB'),
                 ('C', 'D'): Edge(wpA=c, wpB=d, path_type='air', danger_level=0.0, speed=1.0, name='CD')}
        route = Route(route_type='air', edges=edges, name='gap')
        self.assertEqual([w.name for w in MT.route_waypoints(route)], ['A', 'B', 'C', 'D'])


# ── check_mission_assets ──────────────────────────────────────────────────────

class _FakeAsset:
    def __init__(self, asset_id):
        self.id = asset_id


class _FakeBlock:
    def __init__(self, block_id, asset_ids):
        self.id = block_id
        self.assets = {f"key_{i}": _FakeAsset(a) for i, a in enumerate(asset_ids)}


class TestCheckMissionAssets(_LoggerMock, unittest.TestCase):

    def test_ok(self):
        MT.check_mission_assets(_air_mission(), _FakeBlock('wing_1', ['f16_1', 'f16_2', 'f16_3']))

    def test_wrong_block(self):
        with self.assertRaises(ValueError):
            MT.check_mission_assets(_air_mission(), _FakeBlock('wing_2', ['f16_1', 'f16_2']))

    def test_missing_asset(self):
        with self.assertRaises(ValueError) as ctx:
            MT.check_mission_assets(_air_mission(), _FakeBlock('wing_1', ['f16_1']))

        self.assertIn('f16_2', str(ctx.exception))

    def test_matches_asset_ids_not_dict_keys(self):
        block = _FakeBlock('wing_1', ['f16_1', 'f16_2'])
        block.assets = {'f16_1': _FakeAsset('other_1'), 'f16_2': _FakeAsset('other_2')}

        with self.assertRaises(ValueError):
            MT.check_mission_assets(_air_mission(), block)

    def test_mission_type(self):
        with self.assertRaises(TypeError):
            MT.check_mission_assets('m_air', _FakeBlock('wing_1', []))


# ── Operazione ────────────────────────────────────────────────────────────────

class TestOperation(_LoggerMock, unittest.TestCase):

    def test_main_mission(self):
        op = MT.Operation('op_1', 'Strike on SAM site', ['m_sead', 'm_strike'], tot=1800,
                          outcome_rule='main_mission', main_mission_id='m_strike')
        self.assertEqual(op.mission_ids, ('m_sead', 'm_strike'))
        self.assertIs(op.outcome_rule, MT.OutcomeRule.MAIN_MISSION)

    def test_all_default(self):
        self.assertIs(MT.Operation('op_2', 'p', ('m1',)).outcome_rule, MT.OutcomeRule.ALL)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            MT.Operation('op', 'p', ())

        with self.assertRaises(ValueError):
            MT.Operation('op', 'p', ('m1', 'm1'))

        with self.assertRaises(ValueError):
            MT.Operation('op', 'p', ('m1',), outcome_rule=MT.OutcomeRule.MAIN_MISSION)

        with self.assertRaises(ValueError):
            MT.Operation('op', 'p', ('m1',), outcome_rule=MT.OutcomeRule.MAIN_MISSION, main_mission_id='m2')

        with self.assertRaises(ValueError):
            MT.Operation('op', 'p', ('m1',), outcome_rule=MT.OutcomeRule.ANY, main_mission_id='m1')

        with self.assertRaises(TypeError):
            MT.Operation('op', '', ('m1',))

        with self.assertRaises(ValueError):
            MT.Operation('op', 'p', ('m1',), tot=-5)


# ── Esiti ─────────────────────────────────────────────────────────────────────

def _asset_out(asset_id, state='operational', reason='route_completed', t=900.0):
    return MT.AssetMissionOutcome(asset_id, state, reason, t)


class TestAssetMissionOutcome(_LoggerMock, unittest.TestCase):

    def test_valid(self):
        out = _asset_out('a', 'damaged', 'damage', 400)
        self.assertIs(out.state, MT.AssetState.DAMAGED)
        self.assertIs(out.end_reason, MT.AssetEndReason.DAMAGE)

    def test_destroyed_coherence(self):
        with self.assertRaises(ValueError):
            _asset_out('a', 'destroyed', 'route_completed')

        with self.assertRaises(ValueError):
            _asset_out('a', 'operational', 'destroyed')

    def test_bad_values(self):
        with self.assertRaises(ValueError):
            _asset_out('a', 'missing')

        with self.assertRaises(ValueError):
            _asset_out('a', t=-1)


class TestMissionOutcome(_LoggerMock, unittest.TestCase):

    def test_completed(self):
        outcomes = {'a': _asset_out('a'), 'b': _asset_out('b', 'destroyed', 'destroyed', 500)}
        result = MT.MissionOutcome('m', MT.MissionStatus.COMPLETED, asset_outcomes=outcomes,
                                   actual_etas=[0, 310, None, 950])
        self.assertIsInstance(result.asset_outcomes, MappingProxyType)
        self.assertEqual(result.actual_etas, (0.0, 310.0, None, 950.0))

    def test_aborted_needs_reason(self):
        self.assertIs(MT.MissionOutcome('m', 'aborted', reason='threat').reason, MT.AbortReason.THREAT)

        with self.assertRaises(ValueError):
            MT.MissionOutcome('m', MT.MissionStatus.ABORTED)

        with self.assertRaises(ValueError):
            MT.MissionOutcome('m', MT.MissionStatus.FAILED, reason=MT.AbortReason.FUEL)

    def test_destroyed_iff_all_destroyed(self):
        dead = {'a': _asset_out('a', 'destroyed', 'destroyed')}
        self.assertIs(MT.MissionOutcome('m', 'destroyed', asset_outcomes=dead).status, MT.MissionStatus.DESTROYED)

        with self.assertRaises(ValueError):
            MT.MissionOutcome('m', 'failed', asset_outcomes=dead)

        with self.assertRaises(ValueError):
            MT.MissionOutcome('m', 'destroyed', asset_outcomes={'a': _asset_out('a')})

    def test_asset_outcome_keys(self):
        with self.assertRaises(ValueError):
            MT.MissionOutcome('m', 'completed', asset_outcomes={'b': _asset_out('a')})

        with self.assertRaises(TypeError):
            MT.MissionOutcome('m', 'completed', asset_outcomes={'a': 'ok'})

        with self.assertRaises(TypeError):
            MT.MissionOutcome('m', 'completed', asset_outcomes=[_asset_out('a')])

    def test_actual_etas_non_decreasing(self):
        with self.assertRaises(ValueError):
            MT.MissionOutcome('m', 'completed', actual_etas=(100, None, 50))

        with self.assertRaises(TypeError):
            MT.MissionOutcome('m', 'completed', actual_etas='100')


if __name__ == '__main__':
    unittest.main()
