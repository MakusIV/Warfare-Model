"""Tests per Logic/Mission_Adapter — dalla Missione al movimento per asset (Fase 3 del piano Missione).

Waypoint, Edge e Route sono oggetti reali (classi geometriche pure), come in Test_Mission_Types.
Verificano: identita' con offset nullo (stessa rotta, stessi tratti), regola dell'offset ai cambi
di direzione (bisettrice, giunzione a spigolo, limite, inversione, tratti verticali), velocita'
(archi, uniforme, per tratto), partenza (start_time, ETA bloccata, TOT) e le mappe per il motore.
"""

import math
import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command import Mission_Types as MT
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA

_LOGGERS = ['Code.Dynamic_War_Manager.Source.' + name + '.logger'
            for name in ('Logic.Mission_Adapter', 'Command.Mission_Types', 'Logic.Contact_Scheduler')]


def _wp(name, x, y, z=0.0):
    return Waypoint(name=name, point=Point3D(x, y, z), obj_reference=None)


def _route(points, speed=200.0, route_type='air', path_type='air', name='r'):
    wps = [_wp(f'{name}{i}', *p) for i, p in enumerate(points)]
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type=path_type, danger_level=0.0, speed=speed,
                                    name=f'{a.name}-{b.name}')
             for a, b in zip(wps, wps[1:])}
    return Route(route_type=route_type, edges=edges, name=name)


def _plan(route, roles=None, speeds=None, etas=None, locked=None):
    wps = MT.route_waypoints(route)
    n = len(wps)
    roles = roles or [MT.WaypointRole.NAV] * (n - 1) + [MT.WaypointRole.LAND]
    speeds = speeds or [None] * n
    etas = etas or [None] * n
    locked = locked or [False] * n
    return tuple(MT.MissionWaypoint(waypoint=w, role=r, speed_kmh=s, planned_eta=e, eta_locked=k)
                 for w, r, s, e, k in zip(wps, roles, speeds, etas, locked))


def _mission(route=None, assets=None, waypoints=None, **overrides):
    route = route if route is not None else _route([(0, 0, 3000), (40_000, 0, 3000)])
    kwargs = dict(mission_id='m1', block_id='wing', domain='air', mission_type='CAS',
                  assets=assets or (MT.MissionAsset('a1', 'lead'),),
                  target=MT.Target(kind=MT.TargetKind.GROUP, target_id='red', provenance=MT.TargetProvenance.OBSERVED,
                                   observed_at=0.0),
                  route=route, waypoints=waypoints if waypoints is not None else _plan(route),
                  start_time=0.0, start_mode=MT.StartMode.AIR)
    kwargs.update(overrides)
    return MT.Mission(**kwargs)


def _points(route):
    return [(float(w.point.x), float(w.point.y), float(w.point.z)) for w in MT.route_waypoints(route)]


class _Base(unittest.TestCase):
    def setUp(self):
        self._patches = [patch(target, MagicMock()) for target in _LOGGERS]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()


# ── IDENTITA' CON OFFSET NULLO ────────────────────────────────────────────────

class TestZeroOffsetIdentity(_Base):

    def test_zero_offset_returns_the_reference_route_itself(self):
        mission = _mission()
        route, speed = MA.asset_route(mission, mission.assets[0])
        self.assertIs(route, mission.route)
        self.assertIsNone(speed)

    def test_zero_offset_legs_are_identical_to_the_reference(self):
        reference = _route([(0, 0, 3000), (10_000, 5_000, 3000), (30_000, 5_000, 2000)])
        mission = _mission(route=reference, start_time=120.0)
        movement, = MA.mission_movements(mission, t0=1_000.0)
        expected = CS.route_legs(reference, t0=1_120.0)
        self.assertEqual(CS.route_legs(movement.route, t0=movement.start, speed=movement.speed), expected)
        self.assertEqual(movement.start, 1_120.0)

    def test_session_maps_have_the_same_form_as_explicit_routes(self):
        mission = _mission()
        routes, starts, speeds = MA.session_movements([mission], t0=0.0)
        self.assertEqual(routes, {'a1': mission.route})
        self.assertEqual(starts, {'a1': 0.0})
        self.assertEqual(speeds, {})
        self.assertEqual(CS.schedule_contacts([], [], 3600.0, routes=routes, starts=starts, speeds=speeds), [])


# ── OFFSET DI FORMAZIONE ──────────────────────────────────────────────────────

class TestFormationOffset(_Base):

    def test_straight_route_is_translated_in_the_heading_frame(self):
        # Rotta verso est: destra = sud (-y), avanti = +x, alto = +z.
        points = MA.offset_points([(0, 0, 0), (1000, 0, 0)], forward_m=50.0, right_m=100.0, up_m=10.0)
        self.assertEqual(points, [(50.0, -100.0, 10.0), (1050.0, -100.0, 10.0)])

    def test_heading_north_puts_right_to_the_east(self):
        points = MA.offset_points([(0, 0, 0), (0, 1000, 0)], 0.0, 500.0, 0.0)
        self.assertEqual(points, [(500.0, 0.0, 0.0), (500.0, 1000.0, 0.0)])

    def test_turn_keeps_parallel_legs_at_the_lateral_distance(self):
        """Virata di 90 gradi a sinistra: il punto esterno e' sulla giunzione a spigolo."""
        points = MA.offset_points([(0, 0, 0), (1000, 0, 0), (1000, 1000, 0)], 0.0, 100.0, 0.0)
        self.assertEqual(points, [(0.0, -100.0, 0.0), (1100.0, -100.0, 0.0), (1100.0, 1000.0, 0.0)])

    def test_sharp_turn_is_capped_by_the_miter_limit(self):
        angle = math.radians(160.0)   # virata di 160 gradi: 1/cos(80) ~ 5.8 > MITER_LIMIT
        corner = (1000.0, 0.0, 0.0)
        end = (1000.0 + 1000.0 * math.cos(angle), 1000.0 * math.sin(angle), 0.0)
        points = MA.offset_points([(0.0, 0.0, 0.0), corner, end], 0.0, 100.0, 0.0)
        shift = math.dist(points[1], corner)
        self.assertAlmostEqual(shift, 100.0 * MA.MITER_LIMIT, places=6)

    def test_reversal_uses_the_incoming_frame(self):
        points = MA.offset_points([(0, 0, 0), (1000, 0, 0), (0, 0, 0)], 0.0, 100.0, 0.0)
        # Al punto d'inversione la terna e' quella in entrata (destra = sud); all'ultimo quella in
        # uscita (verso ovest, destra = nord): il gregario finisce dall'altra parte.
        self.assertEqual(points, [(0.0, -100.0, 0.0), (1000.0, -100.0, 0.0), (0.0, 100.0, 0.0)])

    def test_vertical_leg_inherits_the_previous_heading(self):
        points = MA.offset_points([(0, 0, 0), (1000, 0, 0), (1000, 0, 500)], 0.0, 100.0, 0.0)
        self.assertEqual(points[-1], (1000.0, -100.0, 500.0))

    def test_no_horizontal_leg_admits_only_vertical_offsets(self):
        with self.assertRaises(ValueError):
            MA.offset_points([(0, 0, 0), (0, 0, 500)], 0.0, 100.0, 0.0)

        self.assertEqual(MA.offset_points([(0, 0, 0), (0, 0, 500)], 0.0, 0.0, 20.0),
                         [(0.0, 0.0, 20.0), (0.0, 0.0, 520.0)])

    def test_asset_route_with_offset_is_a_new_route_with_the_same_edges_data(self):
        reference = _route([(0, 0, 3000), (40_000, 0, 3000)], speed=150.0)
        mission = _mission(route=reference, assets=(MT.MissionAsset('a1', 'lead'),
                                                     MT.MissionAsset('a2', 'wingman', right_m=500.0)))
        route, speed = MA.asset_route(mission, mission.assets[1])
        self.assertIsNot(route, reference)
        self.assertEqual(_points(route), [(0.0, -500.0, 3000.0), (40_000.0, -500.0, 3000.0)])
        self.assertEqual([e.speed for e in route.edges.values()], [150.0])
        self.assertEqual(route.route_type, 'air')
        self.assertIsNone(speed)

    def test_rotation_noise_is_rounded_away(self):
        """Tratto diagonale: offset ricavato da una traslazione intera ridà la traslazione esatta."""
        reference = [(-8300.0, 150.0, 0.0), (2000.0, 0.0, 0.0)]
        hx, hy = 10300.0, -150.0
        norm = math.hypot(hx, hy)
        hx, hy = hx / norm, hy / norm
        dx, dy = 0.0, 300.0
        forward, right = dx * hx + dy * hy, dx * hy - dy * hx
        self.assertEqual(MA.offset_points(reference, forward, right, 0.0),
                         [(-8300.0, 450.0, 0.0), (2000.0, 300.0, 0.0)])

    def test_asset_not_in_the_mission_raises(self):
        with self.assertRaises(ValueError):
            MA.asset_route(_mission(), MT.MissionAsset('other', 'lead'))


# ── VELOCITA' ─────────────────────────────────────────────────────────────────

class TestSpeeds(_Base):

    def test_uniform_declared_speed_becomes_a_speed_override(self):
        reference = _route([(0, 0, 3000), (10_000, 0, 3000), (20_000, 0, 3000)])
        mission = _mission(route=reference, waypoints=_plan(reference, speeds=[None, 720.0, 720.0]))
        route, speed = MA.asset_route(mission, mission.assets[0])
        self.assertIs(route, reference)
        self.assertAlmostEqual(speed, 200.0)
        _, _, speeds = MA.session_movements([mission])
        self.assertAlmostEqual(speeds['a1'], 200.0)

    def test_mixed_declared_speeds_rebuild_the_edges(self):
        reference = _route([(0, 0, 3000), (10_000, 0, 3000), (20_000, 0, 3000)], speed=100.0)
        mission = _mission(route=reference, waypoints=_plan(reference, speeds=[None, 360.0, None]))
        route, speed = MA.asset_route(mission, mission.assets[0])
        self.assertIsNone(speed)
        self.assertEqual([e.speed for e in route.edges.values()], [100.0, 100.0])
        mission = _mission(route=reference, waypoints=_plan(reference, speeds=[None, 720.0, None]))
        route, _ = MA.asset_route(mission, mission.assets[0])
        self.assertEqual([e.speed for e in route.edges.values()], [200.0, 100.0])
        self.assertEqual(_points(route), _points(reference))

    def test_route_from_waypoints_without_a_route(self):
        wps = [_wp('A', 0, 0), _wp('B', 3600, 0)]
        plan = (MT.MissionWaypoint(wps[0], MT.WaypointRole.DEPARTURE),
                MT.MissionWaypoint(wps[1], MT.WaypointRole.OBJECTIVE, speed_kmh=36.0))
        mission = MT.Mission(mission_id='g1', block_id='bde', domain='ground', mission_type='Movement',
                             assets=(MT.MissionAsset('t1', 'lead'),),
                             target=MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(3600, 0, 0), radius_m=100.0),
                             waypoints=plan, start_time=0.0)
        movement, = MA.mission_movements(mission)
        self.assertEqual(movement.route.route_type, 'ground')
        self.assertEqual(MA.waypoint_times(movement), (0.0, 360.0))

    def test_route_from_waypoints_needs_speeds(self):
        wps = [_wp('A', 0, 0), _wp('B', 3600, 0)]
        plan = (MT.MissionWaypoint(wps[0], MT.WaypointRole.DEPARTURE), MT.MissionWaypoint(wps[1], MT.WaypointRole.OBJECTIVE))
        mission = MT.Mission(mission_id='g1', block_id='bde', domain='ground', mission_type='Movement',
                             assets=(MT.MissionAsset('t1', 'lead'),),
                             target=MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(3600, 0, 0), radius_m=100.0),
                             waypoints=plan, start_time=0.0)
        with self.assertRaises(ValueError):
            MA.mission_movements(mission)

    def test_mission_on_the_spot_does_not_move(self):
        mission = MT.Mission(mission_id='g2', block_id='bde', domain='ground', mission_type='Defense',
                             assets=(MT.MissionAsset('t1', 'lead'),),
                             target=MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(0, 0, 0), radius_m=100.0),
                             start_time=0.0)
        movement, = MA.mission_movements(mission)
        self.assertIsNone(movement.route)
        self.assertEqual(MA.session_movements([mission]), ({}, {}, {}))
        self.assertEqual(MA.waypoint_times(movement), ())


# ── PARTENZA ──────────────────────────────────────────────────────────────────

class TestStart(_Base):

    def test_start_time_is_relative_to_the_session_start(self):
        self.assertEqual(MA.mission_start(_mission(start_time=300.0), t0=7_200.0), 7_500.0)

    def test_locked_eta_derives_the_departure_backwards(self):
        reference = _route([(0, 0, 3000), (20_000, 0, 3000), (40_000, 0, 3000)])   # 100 s per tratto
        plan = _plan(reference, roles=[MT.WaypointRole.NAV, MT.WaypointRole.ATTACK, MT.WaypointRole.LAND],
                     etas=[None, 500.0, None], locked=[False, True, False])
        mission = _mission(route=reference, waypoints=plan, start_time=None)
        self.assertAlmostEqual(MA.mission_start(mission, t0=1_000.0), 1_400.0)

    def test_tot_is_anchored_to_the_attack_waypoint(self):
        reference = _route([(0, 0, 3000), (20_000, 0, 3000), (40_000, 0, 3000)])
        plan = _plan(reference, roles=[MT.WaypointRole.NAV, MT.WaypointRole.ATTACK, MT.WaypointRole.LAND])
        mission = _mission(route=reference, waypoints=plan, start_time=None, tot=600.0)
        self.assertAlmostEqual(MA.mission_start(mission), 500.0)

    def test_tot_without_anchor_raises(self):
        with self.assertRaises(ValueError):
            MA.mission_start(_mission(start_time=None, tot=600.0))

    def test_derived_departure_before_the_session_raises(self):
        reference = _route([(0, 0, 3000), (20_000, 0, 3000), (40_000, 0, 3000)])
        plan = _plan(reference, roles=[MT.WaypointRole.NAV, MT.WaypointRole.ATTACK, MT.WaypointRole.LAND])
        with self.assertRaises(ValueError):
            MA.mission_start(_mission(route=reference, waypoints=plan, start_time=None, tot=50.0))

    def test_on_event_activation_is_not_executable(self):
        mission = _mission(activation=MT.Activation.ON_EVENT, activation_event='go')
        with self.assertRaises(ValueError):
            MA.mission_start(mission)

    def test_all_assets_of_a_mission_start_together(self):
        mission = _mission(assets=(MT.MissionAsset('a1', 'lead'), MT.MissionAsset('a2', 'wingman', forward_m=-200.0)),
                           start_time=60.0)
        self.assertEqual({m.start for m in MA.mission_movements(mission, t0=10.0)}, {70.0})


# ── MAPPE PER IL MOTORE ───────────────────────────────────────────────────────

class TestSessionMovements(_Base):

    def test_asset_in_two_missions_raises(self):
        first = _mission(mission_id='m1')
        second = _mission(mission_id='m2')
        with self.assertRaises(ValueError):
            MA.session_movements([first, second])

    def test_waypoint_times_follow_the_route(self):
        reference = _route([(0, 0, 3000), (20_000, 0, 3000), (40_000, 0, 3000)])
        movement, = MA.mission_movements(_mission(route=reference, start_time=30.0))
        self.assertEqual(MA.waypoint_times(movement), (30.0, 130.0, 230.0))

    def test_mission_routes_are_the_routes_map(self):
        mission = _mission(assets=(MT.MissionAsset('a1', 'lead'), MT.MissionAsset('a2', 'wingman', right_m=100.0)))
        self.assertEqual(sorted(MA.mission_routes([mission])), ['a1', 'a2'])

    def test_kmh_conversion(self):
        self.assertEqual(MA.kmh_to_ms(36.0), 10.0)


if __name__ == '__main__':
    unittest.main()


# ── REGOLA A: LA MISSIONE SI MUOVE ALLA VELOCITA' DEL PIU' LENTO (F4a) ─────────

class _Asset:
    """Asset minimo con il solo profilo di velocita' (m/s), come `Mobile.speed`."""

    def __init__(self, max_speed):
        self.speed = {'nominal': None, 'max': max_speed}


class TestRuleASlowestSpeed(_Base):

    def _two_ship(self, **overrides):
        return _mission(assets=(MT.MissionAsset('a1', 'lead'), MT.MissionAsset('a2', 'wingman', 0.0, 500.0, 0.0)),
                        **overrides)

    def test_planned_speed_within_the_slowest_max_is_accepted(self):
        mission = self._two_ship()   # archi a 200 m/s
        limit = MA.check_mission_speed(mission, {'a1': _Asset(300.0), 'a2': _Asset(200.0)})
        self.assertEqual(limit, 200.0)

    def test_leg_faster_than_the_slowest_max_is_rejected(self):
        mission = self._two_ship()
        with self.assertRaisesRegex(ValueError, "slowest asset 'a2'"):
            MA.check_mission_speed(mission, {'a1': _Asset(300.0), 'a2': _Asset(150.0)})

    def test_declared_mission_speed_is_the_one_checked(self):
        route = _route([(0, 0, 3000), (40_000, 0, 3000)])
        mission = self._two_ship(route=route, waypoints=_plan(route, speeds=[None, 900.0]))   # 250 m/s
        with self.assertRaises(ValueError):
            MA.check_mission_speed(mission, {'a1': _Asset(300.0), 'a2': _Asset(240.0)})
        self.assertEqual(MA.check_mission_speed(mission, {'a1': _Asset(300.0), 'a2': _Asset(260.0)}), 260.0)

    def test_unknown_max_speed_is_logged_and_does_not_block(self):
        mission = self._two_ship()
        self.assertIsNone(MA.check_mission_speed(mission, {'a1': _Asset(None), 'a2': object()}))
        MA.logger.warning.assert_called()
        # Il solo asset con il dato fa da limite.
        self.assertEqual(MA.check_mission_speed(mission, {'a1': _Asset(250.0), 'a2': _Asset(None)}), 250.0)

    def test_mission_without_route_is_not_checked(self):
        mission = MT.Mission(mission_id='m0', block_id='armor', domain='ground', mission_type='Maintain',
                             assets=(MT.MissionAsset('a1', 'lead'),),
                             target=MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(0, 0, 0), radius_m=1_000.0),
                             start_time=0.0)
        self.assertIsNone(MA.check_mission_speed(mission, {'a1': _Asset(1.0)}))
