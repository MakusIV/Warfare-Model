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
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
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


# ── VISTA D'INGAGGIO: MissionForce (F4b) ──────────────────────────────────────

# Classi di stub con i NOMI della gerarchia reale: `validate_class` confronta i nomi nella MRO, e
# la regola di `can_disengage` (Military si', Block non militare no) dipende solo da quelli.
class Block:
    def __init__(self, block_id, side, asset_ids, interceptors=()):
        self.id = block_id
        self.name = f'{block_id}-name'
        self.side = side
        self.assets = {f'key-{asset_id}': _ForceAsset(asset_id) for asset_id in asset_ids}
        self._interceptors = tuple(interceptors)

    def salvo_interceptors(self):
        by_id = {asset.id: asset for asset in self.assets.values()}
        return [(by_id[asset_id], channels) for asset_id, channels in self._interceptors]


class Military(Block):
    pass


class _ForceAsset:
    def __init__(self, asset_id):
        self.id = asset_id


class _Plain:
    """Forza duck-typed che non e' un Block: combattente per il risolutore."""

    def __init__(self):
        self.id = 'plain'
        self.side = 'Blue'
        self.assets = {'p1': _ForceAsset('p1')}


class TestMissionForce(_Base):

    def setUp(self):
        super().setUp()
        self.wing = Military('wing', 'Blue', ['a1', 'a2', 'a3'], interceptors=[('a3', 2), ('a1', 1)])

    def _two_ship(self, mission_id='m1'):
        return _mission(mission_id=mission_id,
                        assets=(MT.MissionAsset('a1', 'lead'), MT.MissionAsset('a2', 'wingman', 0.0, 500.0, 0.0)))

    def test_identity_side_and_owner(self):
        view = MA.MissionForce.of_mission(self._two_ship(), self.wing)
        self.assertEqual((view.id, view.name, view.mission_id), ('m1', 'm1', 'm1'))
        self.assertEqual((view.block_id, view.side), ('wing', 'Blue'))
        self.assertIs(view.owner_block, self.wing)
        self.assertEqual(view.mission.mission_id, 'm1')

    def test_assets_are_the_real_ones_restricted_to_the_mission(self):
        view = MA.MissionForce.of_mission(self._two_ship(), self.wing)
        self.assertEqual(list(view.assets), ['key-a1', 'key-a2'])
        self.assertIs(view.assets['key-a1'], self.wing.assets['key-a1'])

    def test_salvo_interceptors_restricted_to_the_mission(self):
        view = MA.MissionForce.of_mission(self._two_ship(), self.wing)
        self.assertEqual([(asset.id, channels) for asset, channels in view.salvo_interceptors()], [('a1', 1)])

    def test_salvo_interceptors_empty_if_the_block_has_none(self):
        block = Military('wing', 'Blue', ['a1', 'a2'])
        del block._interceptors
        block.salvo_interceptors = None
        self.assertEqual(MA.MissionForce.of_mission(self._two_ship(), block).salvo_interceptors(), [])

    def test_no_block_attribute_so_it_is_not_unwrapped(self):
        """`_as_block` (scheduler, simulatore) scarta un `.block`: la vista non deve averlo."""
        view = MA.MissionForce.of_mission(self._two_ship(), self.wing)
        self.assertIs(getattr(view, 'block', view), view)

    def test_wrong_block_or_foreign_asset_rejected(self):
        with self.assertRaisesRegex(ValueError, "belongs to block 'wing'"):
            MA.MissionForce.of_mission(self._two_ship(), Military('other', 'Blue', ['a1', 'a2']))
        with self.assertRaisesRegex(ValueError, r"\['a2'\] do not belong"):
            MA.MissionForce.of_mission(self._two_ship(), Military('wing', 'Blue', ['a1']))
        with self.assertRaises(TypeError):
            MA.MissionForce.of_mission('m1', self.wing)

    def test_unassigned_view_has_the_block_identity(self):
        residual = MA.MissionForce.unassigned(self.wing, [self._two_ship()])
        self.assertEqual((residual.id, residual.name, residual.mission_id), ('wing', 'wing-name', None))
        self.assertEqual(list(residual.assets), ['key-a3'])
        self.assertEqual([(asset.id, channels) for asset, channels in residual.salvo_interceptors()], [('a3', 2)])

    def test_unassigned_view_is_none_when_every_asset_has_a_mission(self):
        other = _mission(mission_id='m2', assets=(MT.MissionAsset('a3', 'lead'),))
        self.assertIsNone(MA.MissionForce.unassigned(self.wing, [self._two_ship(), other]))

    def test_can_disengage_follows_the_block_class(self):
        self.assertTrue(MA.MissionForce.of_mission(self._two_ship(), self.wing).can_disengage)
        depot = Block('wing', 'Blue', ['a1', 'a2'])
        self.assertFalse(MA.MissionForce.of_mission(self._two_ship(), depot).can_disengage)

    def test_resolver_honours_the_declared_can_disengage(self):
        """Adattatore: la vista non e' ne' Military ne' Block, il risolutore legge il dichiarato."""
        from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

        depot_view = MA.MissionForce.of_mission(self._two_ship(), Block('wing', 'Blue', ['a1', 'a2']))
        self.assertFalse(ER._can_disengage(depot_view))
        self.assertTrue(ER._can_disengage(MA.MissionForce.of_mission(self._two_ship(), self.wing)))
        self.assertTrue(ER._can_disengage(_Plain()))
        self.assertFalse(ER._can_disengage(Block('depot', 'Blue', [])))


# ── POSTURA CONTINUA (F4c, D1.c) ──────────────────────────────────────────────

class Aircraft(_ForceAsset):
    """Stub con il NOME di classe che `continuous_posture` riconosce (validate_class)."""


class Ship(_ForceAsset):
    pass


class Vehicle(_ForceAsset):
    pass


def _airbase(*assets):
    """Military 'base' (lato Red) con gli asset dati, chiavi = id."""
    block = Military('base', 'Red', [])
    block.assets = {asset.id: asset for asset in assets}
    return block


class TestContinuousPosture(_Base):
    """Decisioni dell'utente 2026-10-11: aereo senza missione a terra, superficie in difesa."""

    def test_posture_by_class(self):
        self.assertEqual(MA.continuous_posture(Aircraft('a')), MA.PARKED_POSTURE)
        self.assertEqual(MA.continuous_posture(Ship('s')), MA.SEA_DEFENSE_POSTURE)
        self.assertEqual(MA.continuous_posture(Vehicle('v')), MA.GROUND_DEFENSE_POSTURE)
        self.assertEqual(MA.continuous_posture(_ForceAsset('x')), MA.GROUND_DEFENSE_POSTURE)

    def test_labels_are_the_existing_context_values(self):
        from Code.Dynamic_War_Manager.Source.Context.Context import Ground_Action, Sea_Task
        self.assertEqual(MA.GROUND_DEFENSE_POSTURE, Ground_Action.DEFENSE.value)
        self.assertEqual(MA.SEA_DEFENSE_POSTURE, Sea_Task.DEFENSE.value)
        self.assertEqual(MA.PARKED_POSTURE, MT.StartMode.PARKING_COLD.value)

    def test_residual_view_of_a_mixed_block_marks_the_aircraft_grounded(self):
        """Blocco misto: un aereo in missione, uno parcheggiato, una difesa terrestre e una nave."""
        base = _airbase(Aircraft('a1'), Aircraft('a2'), Vehicle('sam'), Ship('patrol'))
        mission = _mission(block_id='base', assets=(MT.MissionAsset('a1', 'lead'),))
        residual = MA.MissionForce.unassigned(base, [mission])
        self.assertEqual(residual.grounded, frozenset({'a2'}))
        self.assertEqual(residual.postures, {'a2': MA.PARKED_POSTURE, 'sam': MA.GROUND_DEFENSE_POSTURE,
                                             'patrol': MA.SEA_DEFENSE_POSTURE})

    def test_mission_view_has_no_posture(self):
        """Gli aerei di una missione NON sono a terra (la presenza prima della partenza e' F5)."""
        base = _airbase(Aircraft('a1'), Aircraft('a2'))
        view = MA.MissionForce.of_mission(_mission(block_id='base', assets=(MT.MissionAsset('a1', 'lead'),)), base)
        self.assertEqual((view.postures, view.grounded), ({}, frozenset()))

    def test_grounded_assets_over_the_engagement_forces(self):
        """Vista residua, blocco senza missioni (passato tale e quale) e vista di missione."""
        base = _airbase(Aircraft('a1'), Aircraft('a2'), Vehicle('sam'))
        apron = Military('apron', 'Red', [])
        apron.assets = {'p1': Aircraft('p1'), 'p2': Aircraft('p2')}
        mission = _mission(block_id='base', assets=(MT.MissionAsset('a1', 'lead'),))
        forces = {'m1': MA.MissionForce.of_mission(mission, base),
                  'base': MA.MissionForce.unassigned(base, [mission]),
                  'apron': apron}
        self.assertEqual(MA.grounded_assets(forces), frozenset({'a2', 'p1', 'p2'}))

    def test_no_aircraft_without_mission_means_an_empty_set(self):
        base = _airbase(Aircraft('a1'), Vehicle('sam'))
        mission = _mission(block_id='base', assets=(MT.MissionAsset('a1', 'lead'),))
        forces = {'m1': MA.MissionForce.of_mission(mission, base), 'base': MA.MissionForce.unassigned(base, [mission])}
        self.assertEqual(MA.grounded_assets(forces), frozenset())

    def test_no_mutation_of_the_assets(self):
        aircraft = Aircraft('a2')
        before = dict(vars(aircraft))
        MA.MissionForce.unassigned(_airbase(aircraft), [])
        self.assertEqual(vars(aircraft), before)


# ── DOMINIO DI COORDINAMENTO (2026-10-11, decisioni 6 e 7) ────────────────────

class TestCoordinationDomains(_Base):
    """Stesso blocco OPPURE stessa Operazione, unione transitiva, mai a cavallo dei lati."""

    def setUp(self):
        super().setUp()
        self.blocks = {'b1': Military('b1', 'Blue', ['a1', 'a2', 'a3']),
                       'b2': Military('b2', 'Blue', ['c1']),
                       'b3': Military('b3', 'Blue', ['d1']),
                       'r1': Military('r1', 'Red', ['e1'])}

    def _view(self, mission_id, block_id, asset_id, operation_id=None):
        mission = _mission(mission_id=mission_id, block_id=block_id, operation_id=operation_id,
                           assets=(MT.MissionAsset(asset_id, 'lead'),))
        return MA.MissionForce.of_mission(mission, self.blocks[block_id])

    def _forces(self, *views):
        return {view.id: view for view in views}

    def test_without_links_every_force_is_its_own_domain(self):
        forces = self._forces(self._view('mA', 'b1', 'a1'), self._view('mC', 'b2', 'c1'))
        self.assertEqual(MA.coordination_domains(forces), {'mA': 'mA', 'mC': 'mC'})

    def test_same_block(self):
        forces = self._forces(self._view('mB', 'b1', 'a1'), self._view('mA', 'b1', 'a2'),
                              self._view('mC', 'b2', 'c1'))
        self.assertEqual(MA.coordination_domains(forces), {'mA': 'mA', 'mB': 'mA', 'mC': 'mC'})

    def test_same_operation_across_blocks(self):
        forces = self._forces(self._view('mA', 'b1', 'a1', 'op'), self._view('mC', 'b2', 'c1', 'op'))
        operation = MT.Operation(operation_id='op', purpose='strike', mission_ids=('mA', 'mC'))
        self.assertEqual(MA.coordination_domains(forces, [operation]), {'mA': 'mA', 'mC': 'mA'})

    def test_operation_listed_only_by_the_order(self):
        """Missioni senza `operation_id` ma elencate da un'Operazione: legate lo stesso."""
        forces = self._forces(self._view('mA', 'b1', 'a1'), self._view('mC', 'b2', 'c1'))
        operation = MT.Operation(operation_id='op', purpose='strike', mission_ids=('mA', 'mC'))
        self.assertEqual(MA.coordination_domains(forces), {'mA': 'mA', 'mC': 'mC'})
        self.assertEqual(MA.coordination_domains(forces, [operation])['mC'], 'mA')

    def test_transitive_union(self):
        """A-blocco1, B-blocco1+Op, C-blocco2+Op -> un solo dominio; D-blocco3 resta fuori."""
        forces = self._forces(self._view('A', 'b1', 'a1'), self._view('B', 'b1', 'a2', 'op'),
                              self._view('C', 'b2', 'c1', 'op'), self._view('D', 'b3', 'd1'))
        domains = MA.coordination_domains(forces, [MT.Operation('op', 'strike', ('B', 'C'))])
        self.assertEqual(domains, {'A': 'A', 'B': 'A', 'C': 'A', 'D': 'D'})

    def test_residual_view_joins_the_missions_of_its_block(self):
        mission = _mission(mission_id='m1', block_id='b1', assets=(MT.MissionAsset('a1', 'lead'),))
        forces = {'m1': MA.MissionForce.of_mission(mission, self.blocks['b1']),
                  'b1': MA.MissionForce.unassigned(self.blocks['b1'], [mission]),
                  'b2': self.blocks['b2']}
        self.assertEqual(MA.coordination_domains(forces), {'m1': 'b1', 'b1': 'b1', 'b2': 'b2'})

    def test_operation_never_spans_two_sides(self):
        forces = self._forces(self._view('mA', 'b1', 'a1', 'op'), self._view('mB', 'b2', 'c1', 'op'),
                              self._view('mR', 'r1', 'e1', 'op'))
        with patch('Code.Dynamic_War_Manager.Source.Logic.Mission_Adapter.logger') as mock_logger:
            domains = MA.coordination_domains(forces, [MT.Operation('op', 'mixed', ('mA', 'mB', 'mR'))])

        self.assertEqual(domains, {'mA': 'mA', 'mB': 'mA', 'mR': 'mR'})
        mock_logger.warning.assert_called_once()

    def test_deterministic_and_independent_of_the_mapping_order(self):
        views = [self._view('B', 'b1', 'a2', 'op'), self._view('C', 'b2', 'c1', 'op'), self._view('A', 'b1', 'a1')]
        operation = MT.Operation('op', 'strike', ('B', 'C'))
        self.assertEqual(MA.coordination_domains(self._forces(*views), [operation]),
                         MA.coordination_domains(self._forces(*reversed(views)), [operation]))

    def test_the_resolver_accepts_the_map(self):
        """Le chiavi sono quelle che `resolve_engagement` accetta come `coordination_of`."""
        from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

        forces = self._forces(self._view('mA', 'b1', 'a1'), self._view('mB', 'b1', 'a2'), self._view('mR', 'r1', 'e1'))
        for view in forces.values():
            for asset in view.assets.values():
                asset.health = 100
        run = ER._EngagementRun(tuple(forces.values()), [], lambda s, t: None, None, None, None, None, None,
                                None, 0.0, 'derived', coordination_of=MA.coordination_domains(forces))
        self.assertEqual(run.domain_of, {'mA': 'mA', 'mB': 'mA', 'mR': 'mR'})

    def test_bad_arguments(self):
        with self.assertRaises(TypeError):
            MA.coordination_domains([self._view('mA', 'b1', 'a1')])
        with self.assertRaises(TypeError):
            MA.coordination_domains(self._forces(self._view('mA', 'b1', 'a1')), ['op'])


# ── ATTESE, ETA EFFETTIVE, PRESENZA E POSTURA FINALE (F5) ─────────────────────

_INF = float('inf')


def _wait(mode='hold', duration=None, until=None, start=None):
    return MT.MissionAction(MT.ActionKind.WAIT, 'Wait', wait_mode=mode, wait_duration_s=duration,
                            wait_until=until, start=start or MT.StartCondition())


def _three_points(speed=200.0):
    """Rotta aerea di tre punti, 100 s per tratto a 200 m/s."""
    return _route([(0, 0, 3000), (20_000, 0, 3000), (40_000, 0, 3000)], speed=speed)


def _with_actions(route, actions_at, roles=None, etas=None, locked=None):
    plan = _plan(route, roles=roles, etas=etas, locked=locked)
    return tuple(MT.MissionWaypoint(waypoint=mw.waypoint, role=mw.role, planned_eta=mw.planned_eta,
                                    eta_locked=mw.eta_locked, actions=tuple(actions_at.get(index, ())))
                 for index, mw in enumerate(plan))


def _ground_mission(start_time=0.0, mission_type='Attack', points=((0, 0), (1000, 0)), speed=10.0, **overrides):
    route = _route([(x, y, 0) for x, y in points], speed=speed, route_type='ground', path_type='offroad', name='g')
    roles = [MT.WaypointRole.DEPARTURE] + [MT.WaypointRole.NAV] * (len(points) - 2) + [MT.WaypointRole.OBJECTIVE]
    kwargs = dict(mission_id='g1', block_id='bde', domain='ground', mission_type=mission_type,
                  assets=(MT.MissionAsset('t1', 'lead'),),
                  target=MT.Target(kind=MT.TargetKind.GROUP, target_id='red', provenance=MT.TargetProvenance.OBSERVED,
                                   observed_at=0.0),
                  route=route, waypoints=_plan(route, roles=roles), start_time=start_time)
    kwargs.update(overrides)
    return MT.Mission(**kwargs)


def _base_reference(is_air_base=True):
    """Un `Asset` (finto, `spec`) il cui blocco dichiara `is_Air_Base()`."""
    from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset

    reference = MagicMock(spec=Asset)
    reference.block.is_Air_Base.return_value = is_air_base
    return reference


def _landing_route(reference):
    wps = [_wp('d', 0, 0, 3000), _wp('n', 20_000, 0, 3000),
           Waypoint(name='l', point=Point3D(40_000, 0, 0), obj_reference=reference)]
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0, speed=200.0, name=f'{a.name}-{b.name}')
             for a, b in zip(wps, wps[1:])}
    return Route(route_type='air', edges=edges, name='land')


class _F5Active(_Base):
    """F5 (b)-(d): presenza (`MA.F5_PRESENCE`, attiva dalla F5-B) e attese (`MA.F5_WAITS`, attive
    dalla F5-C): i test le attivano entrambe per sé, indipendentemente dal default."""

    def setUp(self):
        super().setUp()

        for name in ('F5_PRESENCE', 'F5_WAITS'):
            flag = patch.object(MA, name, True)
            flag.start()
            self.addCleanup(flag.stop)


class TestHoldsAndEffectiveEtas(_F5Active):

    def test_wait_duration_shifts_the_following_times(self):
        route = _three_points()
        mission = _mission(route=route, waypoints=_with_actions(route, {1: [_wait(duration=300.0)]}))
        movement, = MA.mission_movements(mission)
        self.assertEqual(movement.holds, ((1, 300.0),))
        self.assertEqual(MA.waypoint_times(movement), (0.0, 100.0, 500.0))

    def test_wait_until_an_instant(self):
        route = _three_points()
        mission = _mission(route=route, waypoints=_with_actions(route, {1: [_wait(until=250.0)]}))
        movement, = MA.mission_movements(mission, t0=1_000.0)
        self.assertEqual(MA.waypoint_times(movement), (1_000.0, 1_100.0, 1_350.0))

    def test_orbit_is_a_static_presence_at_the_waypoint(self):
        """'orbit' senza geometria di circuito (MissionAction non dichiara raggio): presenza ferma
        nel punto per la durata (approssimazione dichiarata)."""
        route = _three_points()
        mission = _mission(route=route, waypoints=_with_actions(route, {1: [_wait('orbit', duration=1_800.0)]}))
        movement, = MA.mission_movements(mission)
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        hold = [leg for leg in legs if leg.p_start == leg.p_end]
        self.assertEqual([(leg.t_start, leg.t_end, leg.p_start) for leg in hold], [(100.0, 1_900.0, (20_000.0, 0.0, 3000.0))])
        self.assertEqual(legs[-1].t_end, 2_000.0)   # AIR, ultimo LAND non su una base: esce di scena

    def test_wait_start_conditions(self):
        route = _three_points()
        at_time = _wait(duration=50.0, start=MT.StartCondition.at_time(300.0))
        after = _wait(duration=50.0, start=MT.StartCondition.after_duration(20.0))
        for action, expected in ((at_time, 450.0), (after, 270.0)):
            mission = _mission(route=route, waypoints=_with_actions(route, {1: [action]}))
            self.assertEqual(MA.waypoint_times(MA.mission_movements(mission)[0])[-1], expected)

    def test_locked_eta_is_reached_with_a_hold_before_the_point(self):
        route = _three_points()
        plan = _with_actions(route, {}, etas=[None, None, 600.0], locked=[False, False, True])
        movement, = MA.mission_movements(_mission(route=route, waypoints=plan, start_time=0.0))
        self.assertEqual(movement.holds, ((1, 400.0),))
        self.assertEqual(MA.waypoint_times(movement), (0.0, 100.0, 600.0))

    def test_late_locked_eta_is_reported_not_enforced(self):
        route = _three_points()
        plan = _with_actions(route, {}, etas=[None, None, 150.0], locked=[False, False, True])

        with patch('Code.Dynamic_War_Manager.Source.Logic.Mission_Adapter.logger') as mock_logger:
            movement, = MA.mission_movements(_mission(route=route, waypoints=plan, start_time=0.0))

        self.assertEqual(MA.waypoint_times(movement), (0.0, 100.0, 200.0))
        mock_logger.warning.assert_called_once()

    def test_common_tot_of_two_missions(self):
        """Due missioni a distanze diverse, stessa partenza e lo stesso TOT dichiarato da ciascuna sul
        punto ATTACK: l'attesa prima del punto le sincronizza (N2.c; il TOT e' della missione)."""
        roles = [MT.WaypointRole.NAV, MT.WaypointRole.ATTACK, MT.WaypointRole.LAND]
        near, far = _three_points(), _route([(0, 0, 3000), (40_000, 0, 3000), (80_000, 0, 3000)], name='far')
        times = [MA.waypoint_times(MA.mission_movements(_mission(mission_id=mid, route=r, waypoints=_plan(r, roles=roles),
                                                                 start_time=0.0, tot=900.0))[0])
                 for mid, r in (('near', near), ('far', far))]
        self.assertEqual([t[1] for t in times], [900.0, 900.0])
        self.assertEqual(times, [(0.0, 900.0, 1_000.0), (0.0, 900.0, 1_100.0)])

    def test_waits_before_a_locked_anchor_advance_the_derived_departure(self):
        route = _three_points()
        plan = _with_actions(route, {1: [_wait(duration=300.0)]}, etas=[None, None, 1_000.0], locked=[False, False, True])
        mission = _mission(route=route, waypoints=plan, start_time=None)
        self.assertAlmostEqual(MA.mission_start(mission), 500.0)
        self.assertEqual(MA.waypoint_times(MA.mission_movements(mission)[0]), (500.0, 600.0, 1_000.0))

    def test_inactive_flag_is_the_previous_behaviour(self):
        route = _three_points()
        plan = _with_actions(route, {1: [_wait(duration=300.0)]})

        with patch.object(MA, 'F5_PRESENCE', False), patch.object(MA, 'F5_WAITS', False):
            movement, = MA.mission_movements(_mission(route=route, waypoints=plan))

        self.assertEqual((movement.holds, movement.present_before, movement.present_after), ((), False, False))
        self.assertEqual(MA.waypoint_times(movement), (0.0, 100.0, 200.0))

    def test_without_waits_the_legs_are_the_route_legs(self):
        route = _three_points()
        movement, = MA.mission_movements(_mission(route=route, start_time=30.0))
        self.assertEqual(MA.movement_legs(movement, 0.0, 3_600.0),
                         CS.clamp_legs(CS.route_legs(route, t0=30.0), 0.0, 3_600.0))


class TestPresenceBeforeAndAfter(_F5Active):

    def test_ground_unit_is_present_before_departure_and_after_arrival(self):
        movement, = MA.mission_movements(_ground_mission(start_time=1_000.0))
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        self.assertEqual((legs[0].t_start, legs[0].t_end, legs[0].p_start, legs[0].p_end),
                         (0.0, 1_000.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        self.assertEqual((legs[-1].t_start, legs[-1].t_end, legs[-1].p_start), (1_100.0, 3_600.0, (1000.0, 0.0, 0.0)))
        self.assertEqual(MA.movement_legs(movement, 0.0, 3_600.0, presence=False),
                         CS.clamp_legs(CS.route_legs(movement.route, t0=1_000.0), 0.0, 3_600.0))
        self.assertEqual(MA.grounded_intervals(movement), ())

    def test_air_start_is_absent_before_and_exits_at_the_end_without_a_base(self):
        movement, = MA.mission_movements(_mission(start_time=500.0))   # AIR, LAND senza riferimento
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        self.assertEqual((legs[0].t_start, legs[-1].t_end), (500.0, 700.0))
        self.assertEqual(MA.grounded_intervals(movement), ())

    def test_parked_start_is_grounded_until_takeoff(self):
        route = _route([(0, 0, 3000), (40_000, 0, 3000)])
        plan = _plan(route, roles=[MT.WaypointRole.DEPARTURE, MT.WaypointRole.LAND])
        mission = _mission(route=route, waypoints=plan, start_time=500.0, start_mode=MT.StartMode.PARKING_COLD)
        movement, = MA.mission_movements(mission)
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        self.assertEqual((legs[0].t_start, legs[0].t_end, legs[0].p_start), (0.0, 500.0, (0.0, 0.0, 3000.0)))
        self.assertEqual(MA.grounded_intervals(movement), ((-_INF, 500.0),))

    def test_landing_on_a_real_air_base(self):
        route = _landing_route(_base_reference())
        mission = _mission(route=route, waypoints=_plan(route), start_time=0.0)
        self.assertTrue(MA.lands_on_air_base(mission))
        movement, = MA.mission_movements(mission)
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        landing = MA.waypoint_times(movement)[-1]   # discesa a quota 0: un po' oltre 200 s
        self.assertEqual((legs[-1].t_start, legs[-1].t_end, legs[-1].p_start), (landing, 3_600.0, (40_000.0, 0.0, 0.0)))
        self.assertEqual(MA.grounded_intervals(movement), ((landing, _INF),))

    def test_a_land_waypoint_not_on_an_air_base_is_not_a_landing(self):
        for reference in (None, _base_reference(is_air_base=False)):
            route = _landing_route(reference)
            mission = _mission(route=route, waypoints=_plan(route), start_time=0.0)
            self.assertFalse(MA.lands_on_air_base(mission))
            self.assertEqual(MA.grounded_intervals(MA.mission_movements(mission)[0]), ())

    def test_grounded_schedule_joins_always_and_intervals(self):
        route = _route([(0, 0, 3000), (40_000, 0, 3000)])
        plan = _plan(route, roles=[MT.WaypointRole.DEPARTURE, MT.WaypointRole.LAND])
        movement, = MA.mission_movements(_mission(route=route, waypoints=plan, start_time=500.0, start_mode='parking_hot'))
        block = _airbase(Aircraft('p1'), Vehicle('v1'))
        schedule = MA.grounded_schedule({'base': block}, [movement])
        self.assertEqual(schedule.always_ids(), frozenset({'p1'}))
        self.assertTrue(schedule.at('a1', 499.0) and not schedule.at('a1', 500.0))


class TestFinalPosture(_F5Active):

    def _posture(self, mission, end=3_600.0, schedule=None):
        movement, = MA.mission_movements(mission)
        schedule = schedule or MA.grounded_schedule({}, [movement])
        return MA.final_posture(mission, movement, schedule, end)

    def test_ground_unit(self):
        self.assertEqual(self._posture(_ground_mission()), MA.GROUND_DEFENSE_POSTURE)             # arrivata
        self.assertEqual(self._posture(_ground_mission(), end=50.0), 'Attack')                   # in movimento
        self.assertEqual(self._posture(_ground_mission(start_time=100.0), end=50.0), MA.GROUND_DEFENSE_POSTURE)
        on_the_spot = MT.Mission(mission_id='g2', block_id='bde', domain='ground', mission_type='Movement',
                                 assets=(MT.MissionAsset('t1', 'lead'),),
                                 target=MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(0, 0, 0), radius_m=100.0),
                                 start_time=0.0)
        self.assertEqual(self._posture(on_the_spot), 'Maintain')   # postura di riferimento del tipo

    def test_aircraft(self):
        self.assertEqual(self._posture(_mission(), end=100.0), 'CAS')                 # in volo
        self.assertEqual(self._posture(_mission()), MA.OFF_SCENE_POSTURE)              # uscito di scena
        route = _landing_route(_base_reference())
        self.assertEqual(self._posture(_mission(route=route, waypoints=_plan(route))), MA.PARKED_POSTURE)
        route = _route([(0, 0, 3000), (40_000, 0, 3000)])
        plan = _plan(route, roles=[MT.WaypointRole.DEPARTURE, MT.WaypointRole.LAND])
        parked = _mission(route=route, waypoints=plan, start_time=500.0, start_mode=MT.StartMode.RUNWAY)
        self.assertEqual(self._posture(parked, end=400.0), MA.PARKED_POSTURE)

    def test_session_postures_cover_every_asset_in_id_order(self):
        block = Military('base', 'Blue', ['a1', 'v1'])
        block.assets['a1'] = Aircraft('a1')
        block.assets['v1'] = Vehicle('v1')
        lone = Military('red', 'Red', [])
        lone.assets['s1'] = Ship('s1')
        mission = _mission(block_id='base')
        view = MA.MissionForce.of_mission(mission, block)
        residual = MA.MissionForce.unassigned(block, [mission])
        movement, = MA.mission_movements(mission)
        postures = MA.session_postures({'m1': view, 'base': residual, 'red': lone}, {'a1': movement},
                                       MA.grounded_schedule({}, [movement]), 3_600.0)
        self.assertEqual(postures, {'a1': MA.OFF_SCENE_POSTURE, 's1': MA.SEA_DEFENSE_POSTURE,
                                    'v1': MA.GROUND_DEFENSE_POSTURE})
        self.assertEqual(list(postures), ['a1', 's1', 'v1'])


class TestF5Switches(_Base):
    """Interruttori di default (nessun patch): presenza ATTIVA (F5-B) e attese ATTIVE (F5-C); con le
    attese spente il comportamento e' quello della F5-B."""

    def _ground_plan(self):
        route = _route([(0, 0, 0), (1000, 0, 0), (2000, 0, 0)], speed=10.0, route_type='ground',
                       path_type='offroad', name='g')
        roles = [MT.WaypointRole.DEPARTURE, MT.WaypointRole.NAV, MT.WaypointRole.OBJECTIVE]
        return route, _with_actions(route, {1: [_wait(duration=300.0)]}, roles=roles)

    def test_default_switches(self):
        self.assertTrue(MA.F5_PRESENCE)
        self.assertTrue(MA.F5_WAITS)

    def test_presence_and_waits_by_default(self):
        """Una WAIT dichiarata produce l'attesa (F5-C), con la presenza prima e dopo (F5-B)."""
        route, plan = self._ground_plan()
        movement, = MA.mission_movements(_ground_mission(start_time=500.0, waypoints=plan, route=route))
        self.assertEqual(movement.holds, ((1, 300.0),))
        self.assertEqual(MA.waypoint_times(movement), (500.0, 600.0, 1_000.0))
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        self.assertEqual((legs[0].t_start, legs[0].t_end, legs[-1].t_start, legs[-1].t_end),
                         (0.0, 500.0, 1_000.0, 3_600.0))

    def test_presence_without_waits(self):
        """Attese spente: una WAIT dichiarata non produce attese, ma la presenza prima e dopo c'e'."""
        route, plan = self._ground_plan()

        with patch.object(MA, 'F5_WAITS', False):
            movement, = MA.mission_movements(_ground_mission(start_time=500.0, waypoints=plan, route=route))

        self.assertEqual(movement.holds, ())
        self.assertEqual((movement.present_before, movement.present_after), (True, True))
        self.assertEqual(MA.waypoint_times(movement), (500.0, 600.0, 700.0))
        legs = MA.movement_legs(movement, 0.0, 3_600.0)
        self.assertEqual((legs[0].t_start, legs[0].t_end, legs[-1].t_start, legs[-1].t_end),
                         (0.0, 500.0, 700.0, 3_600.0))

    def test_a_locked_departure_delays_the_start_time(self):
        """ETA bloccata sul punto di partenza oltre `start_time`: con le attese attive la partenza e'
        ritardata all'ETA; spente resta `start_time` (comportamento precedente alla F5)."""
        route = _three_points()
        plan = _with_actions(route, {}, etas=[900.0, None, None], locked=[True, False, False])
        mission = _mission(route=route, waypoints=plan, start_time=0.0)
        self.assertEqual(MA.mission_start(mission), 900.0)

        with patch.object(MA, 'F5_WAITS', False):
            self.assertEqual(MA.mission_start(mission), 0.0)


class TestTotPerMission(_Base):
    """Il TOT e' di ogni missione, anche nella stessa Operazione (decisione dell'utente del
    2026-10-12, che ha rimosso il TOT comune dell'Operazione): attese prima dell'ancoraggio."""

    ROLES = [MT.WaypointRole.NAV, MT.WaypointRole.ATTACK, MT.WaypointRole.LAND]

    def _missions(self, near_tot, far_tot, start_time=0.0):
        """'near' (100 s di volo fino all'ATTACK) e 'far' (200 s), stessa Operazione 'op'."""
        near, far = _three_points(), _route([(0, 0, 3000), (40_000, 0, 3000), (80_000, 0, 3000)], name='far')
        return (_mission(mission_id='near', route=near, waypoints=_plan(near, roles=self.ROLES), tot=near_tot,
                         start_time=start_time, operation_id='op'),
                _mission(mission_id='far', route=far, waypoints=_plan(far, roles=self.ROLES), tot=far_tot,
                         start_time=start_time, operation_id='op'))

    def test_missions_of_one_operation_reach_each_its_own_tot(self):
        """Caso dell'utente: uno sweep ('near') sulla zona 120 s prima dello strike ('far'), stessa
        partenza: ciascuna missione e' sul proprio ATTACK al PROPRIO TOT."""
        missions = self._missions(near_tot=780.0, far_tot=900.0)
        MT.Operation('op', 'sweep and strike', ('near', 'far'))   # nessun TOT d'Operazione
        times = [MA.waypoint_times(MA.mission_movements(m)[0]) for m in missions]
        self.assertEqual(times, [(0.0, 780.0, 880.0), (0.0, 900.0, 1_100.0)])
        self.assertEqual([MA.mission_movements(m)[0].holds for m in missions], [((0, 680.0),), ((0, 700.0),)])

    def test_different_tots_with_derived_departures(self):
        """Senza `start_time` ogni partenza e' derivata dal proprio TOT."""
        missions = self._missions(near_tot=780.0, far_tot=900.0, start_time=None)
        self.assertEqual([MA.mission_start(m) for m in missions], [680.0, 700.0])
        self.assertEqual([MA.waypoint_times(MA.mission_movements(m)[0])[1] for m in missions], [780.0, 900.0])

    def test_a_mission_without_tot_does_not_wait(self):
        """Nessun TOT ereditato: una missione senza TOT nella stessa Operazione non attende."""
        near, far = self._missions(near_tot=None, far_tot=900.0)
        self.assertEqual(MA.mission_movements(near)[0].holds, ())
        self.assertEqual(MA.waypoint_times(MA.mission_movements(near)[0]), (0.0, 100.0, 200.0))

    def test_tot_without_an_anchor_is_ignored_with_a_warning(self):
        route = _three_points()

        with patch('Code.Dynamic_War_Manager.Source.Logic.Mission_Adapter.logger') as mock_logger:
            movement, = MA.mission_movements(_mission(route=route, tot=900.0))

        self.assertEqual(movement.holds, ())
        mock_logger.warning.assert_called_once()

    def test_the_adapter_has_no_operation_tot(self):
        self.assertFalse(hasattr(MA, 'operation_tots'))


class _BaseBlock:
    """Blocco duck-typed con `is_Air_Base()` e lato (criterio d'area della F5-B)."""

    def __init__(self, side, is_base, assets):
        self.side = side
        self._is_base = is_base
        self.assets = {asset.id: asset for asset in assets}

    def is_Air_Base(self):
        return self._is_base


def _placed(cls, asset_id, x, y):
    asset = cls(asset_id)
    asset.position = Point3D(x, y, 0)
    return asset


class TestAirBaseArea(_Base):
    """F5-B: atterraggio su una base vera anche senza riferimento, se il punto LAND e' nell'area di
    una base (`air_base_points`, `AIR_BASE_AREA_RADIUS_M`)."""

    def test_points_of_the_non_aircraft_assets_of_real_bases(self):
        base = _BaseBlock('Red', True, [_placed(Vehicle, 'sam', 1_000, 0), _placed(Aircraft, 'mig', 50_000, 0)])
        other = _BaseBlock('Red', False, [_placed(Vehicle, 'tank', 0, 0)])
        enemy = _BaseBlock('Blue', True, [_placed(Vehicle, 'depot', 5_000, 0)])
        self.assertEqual(MA.air_base_points([base, other, enemy], 'Red'), ((1_000.0, 0.0),))
        self.assertEqual(MA.air_base_points([base, other, enemy]), ((1_000.0, 0.0), (5_000.0, 0.0)))

    def test_landing_in_the_area_of_a_base(self):
        route = _landing_route(None)   # LAND in (40 km, 0, 0), senza riferimento
        mission = _mission(route=route, waypoints=_plan(route), start_time=0.0)
        near = ((40_000.0 + MA.AIR_BASE_AREA_RADIUS_M - 1.0, 0.0),)
        far = ((40_000.0 + MA.AIR_BASE_AREA_RADIUS_M + 1.0, 0.0),)
        self.assertFalse(MA.lands_on_air_base(mission))
        self.assertTrue(MA.lands_on_air_base(mission, near))
        self.assertFalse(MA.lands_on_air_base(mission, far))
        movement, = MA.mission_movements(mission, 0.0, near)
        self.assertTrue(movement.present_after and movement.grounded_after)


# ── BINGO A PRIORI (F6-B2) ────────────────────────────────────────────────────

class _FuelAsset:
    """Asset minimo con carburante (frazione del pieno), autonomia [m] e crociera [m/s], come `Mobile`."""

    def __init__(self, asset_id='a1', fuel=1.0, autonomy=100_000.0, cruise=200.0):
        self.id = asset_id
        self.fuel = fuel
        self._autonomy = autonomy
        self.speed = {'nominal': cruise, 'max': cruise}

    def fuel_for_distance(self, distance, regime='nominal'):
        return None if self._autonomy is None else distance / self._autonomy


class TestBingoValidator(_Base):
    """`check_mission_bingo` con `reverse_route` False (e, dal G2, `disengage_reserve` False): la regola della
    F6-B2, invariata (la missione aerea che non rientra con la riserva e' rifiutata). Rotta di 40 km a 3000 m, base alla partenza (0, 0): andata
    40 km + rientro ~40,1 km (3D)."""

    BASE = ((0.0, 0.0),)

    def _check(self, *args, **kwargs):
        return MA.check_mission_bingo(*args, reverse_route=False, disengage_reserve=False, **kwargs)

    def test_enough_fuel_is_accepted_with_its_margin(self):
        margins = self._check(_mission(), {'a1': _FuelAsset(fuel=1.0)}, self.BASE, reserve=0.1)
        rate = 1.0 / 100_000.0
        expected = 1.0 - 40_000.0 * rate - math.hypot(40_000.0, 3_000.0) * rate - 0.1
        self.assertAlmostEqual(margins['a1'], expected, delta=1e-12)

    def test_not_returning_with_the_reserve_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "'a1' does not return with the fuel reserve"):
            self._check(_mission(), {'a1': _FuelAsset(fuel=0.85)}, self.BASE, reserve=0.1)

    def test_default_reserve_is_the_fuel_model_one(self):
        fuel = 0.4 + math.hypot(40_000.0, 3_000.0) / 100_000.0 + FM.BINGO_RESERVE
        self.assertIsNotNone(self._check(_mission(), {'a1': _FuelAsset(fuel=fuel + 1e-6)}, self.BASE))
        with self.assertRaises(ValueError):
            self._check(_mission(), {'a1': _FuelAsset(fuel=fuel - 1e-6)}, self.BASE)

    def test_no_suitable_base_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no suitable air base'):
            self._check(_mission(), {'a1': _FuelAsset(fuel=1.0)}, ())

    def test_not_applicable(self):
        """Missione di terra, o `EndCriteria.bingo` False: nessun controllo (None), con entrambe le regole."""
        no_bingo = _mission(end_criteria=MT.EndCriteria(bingo=False))

        for reverse in (False, True):
            self.assertIsNone(MA.check_mission_bingo(no_bingo, {'a1': _FuelAsset(fuel=0.01)}, (), reverse_route=reverse))
            self.assertIsNone(MA.check_mission_bingo(_ground_mission(), {'t1': _FuelAsset('t1', fuel=0.0)}, (),
                                                     reverse_route=reverse))

    def test_unmodelled_fuel_is_not_checked(self):
        self.assertEqual(MA.check_mission_bingo(_mission(), {'a1': _FuelAsset(fuel=None)}, self.BASE), {})
        self.assertEqual(MA.check_mission_bingo(_mission(), {}, self.BASE), {})

    def test_holds_consume_and_ground_stays_do_not(self):
        """Un'orbita di 600 s alla crociera (120 km equivalenti) rende la missione non rientrabile; una sosta
        A TERRA di 6000 s prima del decollo (parcheggio) non consuma."""
        route = _three_points()
        orbit = _mission(route=route, waypoints=_with_actions(route, {1: [_wait('orbit', 600.0)]}))
        with self.assertRaises(ValueError):
            self._check(orbit, {'a1': _FuelAsset(fuel=1.0)}, self.BASE, reserve=0.1)

        route = _route([(0, 0, 3000), (40_000, 0, 3000)])
        roles = [MT.WaypointRole.DEPARTURE, MT.WaypointRole.LAND]
        parked = _mission(route=route, waypoints=_with_actions(route, {0: [_wait('hold', 6_000.0)]}, roles=roles),
                          start_mode=MT.StartMode.PARKING_COLD)
        movement, = MA.mission_movements(parked)
        self.assertEqual([FM.is_stationary(leg) for leg in MA._timeline(movement)[0]], [True, False])
        self.assertEqual(len(MA.airborne_legs(movement)), 1)
        self.assertIsNotNone(self._check(parked, {'a1': _FuelAsset(fuel=1.0)}, self.BASE, reserve=0.1))


# ── BINGO A PRIORI CON RIENTRO A RITROSO (F6-B2bis) ───────────────────────────

_SQUARE = [(0, 0, 0), (30_000, 0, 3000), (30_000, 30_000, 3000), (0, 30_000, 3000)]


def _from_base(points, land=None, start_mode=MT.StartMode.RUNWAY, references=(None, None)):
    """Missione aerea che parte da una base (DEPARTURE) sui punti dati e finisce in `land` (LAND); i
    riferimenti di DEPARTURE e LAND sono `references`."""
    land = land if land is not None else points[0]
    wps = [Waypoint(name=f'w{i}', point=Point3D(*p), obj_reference=references[0] if i == 0 else None)
           for i, p in enumerate(points)]
    wps.append(Waypoint(name='land', point=Point3D(*land), obj_reference=references[1]))
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0, speed=200.0,
                                    name=f'{a.name}-{b.name}')
             for a, b in zip(wps, wps[1:])}
    route = Route(route_type='air', edges=edges, name='loop')
    roles = [MT.WaypointRole.DEPARTURE] + [MT.WaypointRole.NAV] * (len(wps) - 2) + [MT.WaypointRole.LAND]
    return _mission(route=route, waypoints=_plan(route, roles=roles), start_mode=start_mode)


def _length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


class TestReverseRouteBingoValidator(_Base):
    """`check_mission_bingo` con la regola F6-B2bis (default `reverse_route` True): fabbisogno 1,2 x il ritorno
    lungo la rotta a ritroso; anello per la via piu' breve; partenza in volo con il tratto alla base.
    Autonomia di test 100 km (0,01 del pieno = 1 km) sulla rotta di 40 km, 1000 km (`_jet`) sul quadrato. Dal G2
    con `disengage_reserve` False (`_check`): la regola della F6-B2bis, invariata."""

    @staticmethod
    def _check(*args, **kwargs):
        return MA.check_mission_bingo(*args, disengage_reserve=False, **kwargs)

    @staticmethod
    def _jet(fuel):
        return _FuelAsset(fuel=fuel, autonomy=1_000_000.0)

    def test_loop_mission_is_recognised(self):
        """Stessa base: punto LAND entro l'area di una base dal DEPARTURE, o riferimenti nello STESSO blocco
        base; riferimenti su due basi diverse non sono un anello; partenza in volo mai."""
        self.assertTrue(MA.is_loop_mission(_from_base(_SQUARE)))
        near = (MA.AIR_BASE_AREA_RADIUS_M - 1.0, 0.0, 0.0)
        far = (MA.AIR_BASE_AREA_RADIUS_M + 1.0, 0.0, 0.0)
        self.assertTrue(MA.is_loop_mission(_from_base(_SQUARE, land=near)))
        self.assertFalse(MA.is_loop_mission(_from_base(_SQUARE, land=far)))
        origin, other = _base_reference(), _base_reference()
        same = _base_reference()
        same.block = origin.block
        self.assertTrue(MA.is_loop_mission(_from_base(_SQUARE, land=(25_000, 0, 0), references=(origin, same))))
        self.assertFalse(MA.is_loop_mission(_from_base(_SQUARE, references=(origin, other))))
        self.assertFalse(MA.is_loop_mission(_mission(route=_route([(0, 0, 3000), (0, 0, 0)]))))

    def test_return_rule_of_the_mission(self):
        self.assertEqual(MA.bingo_return_rule(_mission()), FM.ReturnRule(departure=False))
        self.assertEqual(MA.bingo_return_rule(_from_base(_SQUARE)), FM.ReturnRule(departure=True, loop=True))
        self.assertEqual(MA.bingo_return_rule(_from_base(_SQUARE, land=(90_000, 0, 0))), FM.ReturnRule(departure=True))

    def test_air_start_needs_a_base_and_the_direct_leg(self):
        """Partenza in volo da (0, 0, 3000) per 40 km, base in (0, 0): ritorno al bingo = metri percorsi + tratto
        diretto di 3 km; a fine rotta 1 - 0,4 - 1,2 x (40 + 3) km. Senza base: rifiuto."""
        base = ((0.0, 0.0),)
        margins = self._check(_mission(), {'a1': _FuelAsset(fuel=1.0)}, base)
        expected = 1.0 - 0.4 - FM.BINGO_RETURN_FACTOR * (40_000.0 + 3_000.0) / 100_000.0
        self.assertAlmostEqual(margins['a1'], expected, delta=1e-12)

        with self.assertRaisesRegex(ValueError, "'a1' does not keep the bingo fuel"):
            self._check(_mission(), {'a1': _FuelAsset(fuel=0.4 + 0.4 * 1.2)}, base)

        with self.assertRaisesRegex(ValueError, 'no suitable air base'):
            self._check(_mission(), {'a1': _FuelAsset(fuel=1.0)}, ())

    def test_from_a_base_no_base_list_is_needed(self):
        """Partenza da una base: il rientro finisce sul DEPARTURE, le basi del lato non servono."""
        mission = _from_base(_SQUARE, land=(90_000, 0, 0))
        self.assertIn('a1', self._check(mission, {'a1': self._jet(1.0)}, ()))

    def test_loop_is_safe_with_about_1_1_times_its_route(self):
        """Anello DEPARTURE -> quadrato -> LAND sul DEPARTURE: accettato con (1 + (f - 1) / 2) x la rotta (+1e-6),
        rifiutato appena sotto; la stessa rotta con il LAND su un'altra base (divert escluso) richiede ben di
        piu' (ritorno a ritroso lungo tutto il percorso)."""
        mission = _from_base(_SQUARE)
        movement, = MA.mission_movements(mission)
        route = _length([leg.p_start for leg in MA.airborne_legs(movement)] + [MA.airborne_legs(movement)[-1].p_end])
        safe = (1.0 + (FM.BINGO_RETURN_FACTOR - 1.0) / 2.0) * route / 1_000_000.0
        self.assertIsNotNone(self._check(mission, {'a1': self._jet(safe + 1e-6)}, ()))

        with self.assertRaises(ValueError):
            self._check(mission, {'a1': self._jet(safe - 1e-6)}, ())

        divert = _from_base(_SQUARE, land=(-1_000, 30_000 + MA.AIR_BASE_AREA_RADIUS_M + 1.0, 0))

        with self.assertRaises(ValueError):
            self._check(divert, {'a1': self._jet(safe + 0.05)}, ())

    def test_validator_and_executor_use_the_same_criterion(self):
        """Per una serie di carburanti la missione e' rifiutata se e solo se `Fuel_Model.bingo_point` sui tratti
        della missione intera e con la regola della missione (cio' che usa `Session_Simulator`) da' un bingo,
        e l'istante annunciato e' quello."""
        mission = _from_base(_SQUARE, land=(60_000, 30_000, 0))
        movement, = MA.mission_movements(mission)
        legs, rule = MA.airborne_legs(movement), MA.bingo_return_rule(mission)
        answers = set()

        for fuel in (0.1, 0.2, 0.3, 0.5, 1.0):
            asset = self._jet(fuel)
            bingo = FM.bingo_point(asset, legs, (), rule=rule)

            try:
                self._check(mission, {'a1': asset}, ())
                rejected = None
            except ValueError as error:
                rejected = str(error)

            self.assertEqual(rejected is not None, bingo is not None, fuel)
            answers.add(rejected is not None)

            if bingo is not None:
                self.assertIn(f't={bingo.time:.1f} s', rejected)

        self.assertEqual(answers, {True, False})    # la serie copre rifiuti e accettazioni

    def test_switch_off_is_the_straight_rule(self):
        """`reverse_route` False = la F6-B2: stessa risposta di `Fuel_Model.bingo_point` senza regola."""
        movement, = MA.mission_movements(_mission())
        asset = _FuelAsset(fuel=0.85)
        self.assertIsNotNone(FM.bingo_point(asset, MA.airborne_legs(movement), ((0.0, 0.0),), 0.1))

        with self.assertRaisesRegex(ValueError, 'fuel reserve'):
            self._check(_mission(), {'a1': asset}, ((0.0, 0.0),), reserve=0.1, reverse_route=False)


# ── SOGLIA DI BINGO E ALBERO DI DECISIONE A PRIORI (G2) ───────────────────────

_ZONE = MT.Target(kind=MT.TargetKind.ZONE, position=Point3D(40_000, 0, 0), radius_m=5_000.0)


class TestReserveBingoValidator(_Base):
    """G2: tipo di missione per l'albero (trasferimento = categoria TRANSPORT) e `check_mission_bingo` con
    `disengage_reserve` (default): rifiuto se e solo se l'aereo parte sotto la soglia rotta intera + riserva di
    disimpegno, lo stesso criterio di `mission_bingo_decision` usato dalla sessione. `_FuelAsset`: autonomia 100
    km, riserva di ripiego = 200 m/s x 300 s al regime 'max' = 0,6 del pieno; rotta di 40 km = 0,4."""

    BASE = ((0.0, 0.0),)

    def test_transfer_is_the_transport_category(self):
        self.assertTrue(MA.is_transfer_mission(_mission(mission_type='Transport',
                                                        target=_ZONE)))

        for mission_type in ('CAS', 'Strike', 'CAP', 'Intercept', 'AWACS', 'Tanker', 'Recon'):
            self.assertFalse(MA.is_transfer_mission(_mission(mission_type=mission_type, target=_ZONE)), mission_type)

        self.assertFalse(MA.is_transfer_mission(_ground_mission(mission_type='Supply')))   # TRANSPORT, ma di terra

    def test_rejected_iff_under_the_threshold(self):
        """Soglia 0,4 + 0,6 = 1,0: pieno accettato con margine 0 (residuo non sotto la soglia), appena sotto
        rifiutato con soglia, riserva e decisione; le basi non servono alla soglia."""
        self.assertAlmostEqual(MA.check_mission_bingo(_mission(), {'a1': _FuelAsset(fuel=1.0)}, ())['a1'], 0.0,
                               delta=1e-12)

        with self.assertRaisesRegex(ValueError, r"'a1' starts under the bingo threshold: .* reserve 0\.6000.*"
                                                r"t=0\.0 s and decides 'departure'"):
            MA.check_mission_bingo(_mission(), {'a1': _FuelAsset(fuel=1.0 - 1e-6)}, self.BASE)

    def test_validator_and_executor_use_the_same_criterion(self):
        """Per una serie di carburanti: rifiuto se e solo se `mission_bingo_decision` (cio' che chiama la sessione)
        da' una decisione; anche il trasferimento che CONTINUA e' rifiutato (e' sotto il minimo)."""
        transfer = _mission(mission_type='Transport', target=_ZONE)
        answers = set()

        for mission in (_mission(), transfer):
            movement, = MA.mission_movements(mission)

            for fuel in (0.3, 0.5, 0.99, 1.0):
                asset = _FuelAsset(fuel=fuel)
                decision = MA.mission_bingo_decision(mission, movement, asset, self.BASE)

                try:
                    MA.check_mission_bingo(mission, {'a1': asset}, self.BASE)
                    rejected = None
                except ValueError as error:
                    rejected = str(error)

                self.assertEqual(rejected is not None, decision is not None, (mission.mission_type, fuel))
                answers.add(rejected is not None)

                if decision is not None and decision.action == FM.BINGO_CONTINUE:
                    self.assertIn('continues on its route', rejected)

        self.assertEqual(answers, {True, False})

    def test_relation_with_the_planning_minimum(self):
        """Stessa grandezza del G1 (rotta intera + riserva): sotto il minimo entrambi rifiutano, sopra entrambi
        accettano."""
        for fuel in (0.9, 1.0 - 1e-6):
            with self.assertRaises(ValueError):
                MA.check_mission_bingo(_mission(), {'a1': _FuelAsset(fuel=fuel)}, ())
            with self.assertRaises(ValueError):
                MA.check_mission_fuel(_mission(), {'a1': _FuelAsset(fuel=fuel)})

        roomy = _FuelAsset(fuel=1.0, autonomy=200_000.0)     # rotta 0,2 + riserva 0,3
        self.assertIn('a1', MA.check_mission_bingo(_mission(), {'a1': roomy}, ()))
        self.assertIn('a1', MA.check_mission_fuel(_mission(), {'a1': roomy}))

    def test_not_applicable_and_not_modelled(self):
        """`EndCriteria.bingo` False o missione di terra: None; carburante non modellato: non controllato."""
        no_bingo = _mission(end_criteria=MT.EndCriteria(bingo=False))
        self.assertIsNone(MA.check_mission_bingo(no_bingo, {'a1': _FuelAsset(fuel=0.01)}, ()))
        self.assertIsNone(MA.check_mission_bingo(_ground_mission(), {'t1': _FuelAsset('t1', fuel=0.0)}, ()))
        self.assertEqual(MA.check_mission_bingo(_mission(), {'a1': _FuelAsset(fuel=None)}, ()), {})


# ── MINIMO DI PIANIFICAZIONE DEL CARBURANTE (G1) ──────────────────────────────

class TestMissionFuelMinimum(_Base):
    """`check_mission_fuel`: carburante caricato > rotta intera + riserva di disimpegno, con un aereo REALE del
    registro (F-14A, loadout "Phoenix Fleet Defense") sulla rotta di 40 km."""

    MODEL = "F-14A Tomcat"
    LOADOUT = "Phoenix Fleet Defense"

    def setUp(self):
        super().setUp()
        more = [patch('Code.Dynamic_War_Manager.Source.Asset.Aircraft.get_aircraft_combat_score', return_value=0.5)]
        more += [patch('Code.Dynamic_War_Manager.Source.' + name + '.logger', MagicMock())
                 for name in ('Asset.Aircraft', 'Asset.Mobile', 'Asset.Asset', 'Logic.Fuel_Model')]
        for p in more:
            p.start()
        self._patches.extend(more)

    def _aircraft(self, loadout=LOADOUT):
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
        from Code.Dynamic_War_Manager.Source.Block.Block import Block
        from Code.Dynamic_War_Manager.Source.Context.Context import Air_Asset_Type

        block = MagicMock(spec=Block)
        block.block_class = "Military"
        aircraft = Aircraft(block=block, asset_type=Air_Asset_Type.FIGHTER, model=self.MODEL)
        aircraft.assigned_loadout = loadout
        return aircraft

    def _minimum(self, mission, aircraft):
        """Rotta intera (alla crociera, `airborne_legs`) + riserva: il minimo, calcolato con le stesse funzioni."""
        movement, = MA.mission_movements(mission)
        return MA.route_fuel_demand(aircraft, MA.airborne_legs(movement)) + FM.disengagement_reserve(aircraft)

    def _with_fuel(self, fuel):
        aircraft = self._aircraft()
        aircraft.consume_fuel(1.0 - fuel)
        return aircraft

    def test_full_load_is_accepted_with_its_margin(self):
        aircraft = self._aircraft()
        mission = _mission()
        margins = MA.check_mission_fuel(mission, {'a1': aircraft})
        self.assertAlmostEqual(margins['a1'], 1.0 - self._minimum(mission, aircraft), delta=1e-12)
        self.assertGreater(margins['a1'], 0.0)

    def test_just_above_and_below_the_minimum(self):
        minimum = self._minimum(_mission(), self._aircraft())
        self.assertIn('a1', MA.check_mission_fuel(_mission(), {'a1': self._with_fuel(minimum + 1e-6)}))

        with self.assertRaisesRegex(ValueError, r"'a1' loads fuel .* disengagement reserve .*military_flow.* is missing"):
            MA.check_mission_fuel(_mission(), {'a1': self._with_fuel(minimum - 1e-6)})

    def test_the_reserve_matters(self):
        """Carburante che basta per la sola rotta ma non per rotta + riserva: rifiutato."""
        aircraft = self._aircraft()
        movement, = MA.mission_movements(_mission())
        route = MA.route_fuel_demand(aircraft, MA.airborne_legs(movement))

        with self.assertRaises(ValueError):
            MA.check_mission_fuel(_mission(), {'a1': self._with_fuel(route + 0.5 * FM.disengagement_reserve(aircraft))})

    def test_holds_count_in_the_whole_route(self):
        """Un'orbita alla crociera aumenta il fabbisogno: lo stesso carburante, accettato senza, e' rifiutato con."""
        route = _three_points()
        plain = _mission(route=route)
        orbit = _mission(route=route, waypoints=_with_actions(route, {1: [_wait('orbit', 1_800.0)]}))
        fuel = self._minimum(plain, self._aircraft()) + 1e-3
        self.assertIn('a1', MA.check_mission_fuel(plain, {'a1': self._with_fuel(fuel)}))

        with self.assertRaises(ValueError):
            MA.check_mission_fuel(orbit, {'a1': self._with_fuel(fuel)})

    def test_not_applicable(self):
        """`EndCriteria.bingo` False o missione di terra: nessun controllo (None), anche a serbatoio quasi vuoto."""
        no_bingo = _mission(end_criteria=MT.EndCriteria(bingo=False))
        self.assertIsNone(MA.check_mission_fuel(no_bingo, {'a1': self._with_fuel(0.001)}))
        self.assertIsNone(MA.check_mission_fuel(_ground_mission(), {'t1': _FuelAsset('t1', fuel=0.0)}))

    def test_unmodelled_fuel_is_not_checked(self):
        """Aereo senza loadout (carburante non modellato), asset assente, stub senza riserva: non controllati."""
        self.assertEqual(MA.check_mission_fuel(_mission(), {'a1': self._aircraft(loadout=None)}), {})
        self.assertEqual(MA.check_mission_fuel(_mission(), {}), {})
        no_reserve = _FuelAsset(fuel=0.01)
        no_reserve.speed = {'nominal': 200.0, 'max': None}
        self.assertEqual(MA.check_mission_fuel(_mission(), {'a1': no_reserve}), {})

    def test_not_called_by_the_session(self):
        """G1 non cambia la sessione: `run_session` non chiama il validatore."""
        import inspect
        from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS

        self.assertNotIn('check_mission_fuel', inspect.getsource(SS))

