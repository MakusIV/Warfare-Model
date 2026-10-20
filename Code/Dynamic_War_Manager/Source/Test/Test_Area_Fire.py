"""Test di Logic/Area_Fire.py (F7b, fuoco su posizione) e dell'evento AREA_FIRE della sessione.

Asset REALI dei registri (`Scenario_Fixtures`), RNG di sessione (`Utility/Session_Rng`), mai valori attesi calibrati: la
frequenza attesa dei colpi a segno e' RICALCOLATA dalle costanti STIMATE dichiarate in `Area_Fire` (geometria del disco
di dispersione e del raggio letale), cosi' il test verifica la regola, non i numeri stimati.

Logger: silenziati con `Scenario_Fixtures.LoggerSilencer` (mixin, non un TestCase), che copre anche `Logic.Area_Fire`.
"""

import dataclasses
import math
import unittest
from unittest.mock import patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    FIRE_AT_POINT_ACTION,
    ActionKind,
    EndCriteria,
    MissionAction,
    StartCondition,
    Target,
    TargetKind,
    TargetProvenance,
)
from Code.Dynamic_War_Manager.Source.Logic import Area_Fire as AF
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Utility.Session_Rng import session_rng

GUN = '2A64-152mm'
SHOOTER = 'Red/art0'
ENEMY = 'Blue/ifv0'


class _CountingRng:
    """Avvolge un RNG di sessione contando le estrazioni (l'ordine e il numero fanno parte del contratto)."""

    def __init__(self, rng):
        self._rng = rng
        self.draws = 0

    def random(self):
        self.draws += 1
        return self._rng.random()


def _rng(seed='A', event='area_fire|m|Red/art0|1|0'):
    return _CountingRng(session_rng(f'AF-{seed}', 'm', event))


def _order(**overrides):
    values = dict(mission_id='m', asset_id=SHOOTER, waypoint_index=1, action_index=0, t_fire=600.0, aim_x=0.0,
                  aim_y=0.0, dispersion_m=AF.AREA_FIRE_MIN_DISPERSION_M, rounds=1, weapon=None)
    values.update(overrides)
    return AF.FireOrder(**values)


class _Fixture(F.LoggerSilencer):
    """Mixin (NON un TestCase): un tiratore 2S19, un nemico BMP-2 e le posizioni."""

    def setUp(self):
        self.red = F.make_force('Red', 'Red')
        self.blue = F.make_force('Blue', 'Blue')
        self.shooter = F.make_vehicle(self.red, SHOOTER, '2S19-Msta', (-15_000.0, 0.0, 0.0))
        self.enemy = F.make_vehicle(self.blue, ENEMY, 'BMP-2', (0.0, 0.0, 0.0))
        F.add_assets(self.red, [self.shooter])
        F.add_assets(self.blue, [self.enemy])
        self.positions = {SHOOTER: (-15_000.0, 0.0, 0.0), ENEMY: (0.0, 0.0, 0.0)}

    def positions_at(self, asset_id, time):
        return self.positions.get(asset_id)

    def resolve(self, order=None, enemies=None, rng=None, **kwargs):
        return AF.resolve_area_fire(order or _order(), self.shooter, [self.enemy] if enemies is None else enemies,
                                    self.positions_at, rng or _rng(), **kwargs)


# ── Ordini di fuoco ───────────────────────────────────────────────────────────

class TestDispersion(unittest.TestCase):

    def test_minimum_radius_and_uncertainty(self):
        point = Target(kind=TargetKind.POINT, position=Point3D(0, 0, 0))
        self.assertEqual(AF.dispersion_radius(point), AF.AREA_FIRE_MIN_DISPERSION_M)
        estimated = Target(kind=TargetKind.POINT, position=Point3D(0, 0, 0), provenance=TargetProvenance.ESTIMATED,
                           estimated_at=-10.0, uncertainty_m=300.0)
        self.assertEqual(AF.dispersion_radius(estimated), 300.0)
        small = dataclasses.replace(estimated, uncertainty_m=10.0)
        self.assertEqual(AF.dispersion_radius(small), AF.AREA_FIRE_MIN_DISPERSION_M)

    def test_area_radius_is_the_largest(self):
        area = Target(kind=TargetKind.AREA, position=Point3D(0, 0, 0), radius_m=800.0,
                      provenance=TargetProvenance.ESTIMATED, estimated_at=-10.0, uncertainty_m=200.0)
        self.assertEqual(AF.dispersion_radius(area), 800.0)

    def test_uncertainty_is_ignored_unless_estimated(self):
        # un bersaglio non stimato non ha incertezza: solo il raggio dichiarato e il minimo
        area = Target(kind=TargetKind.AREA, position=Point3D(0, 0, 0), radius_m=70.0)
        self.assertEqual(AF.dispersion_radius(area), 70.0)


class TestFireOrders(_Fixture, unittest.TestCase):

    def mission(self, start, waypoint=1, **kwargs):
        art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 1, origin=(-15_000.0, 0.0), prefix='art')])
        target = Target(kind=TargetKind.POINT, position=Point3D(100.0, -50.0, 0.0), provenance=TargetProvenance.ESTIMATED,
                        estimated_at=-600.0, uncertainty_m=120.0)
        action = MissionAction(ActionKind.TASK, FIRE_AT_POINT_ACTION, params={'rounds': 6, **kwargs}, start=start)
        missions = F.missions_for(art, [(-14_500.0, 0.0), (-14_000.0, 0.0)], mission_type='Fire_Support',
                                  target=target, actions={waypoint: [action]})
        return missions[0], MA.mission_movements(missions[0], 0.0)[0]

    def test_on_arrival_is_the_arrival_at_the_waypoint(self):
        mission, movement = self.mission(StartCondition.on_arrival(), waypoint=2)
        [order] = AF.fire_orders(mission, movement, 0.0)
        arrival = MA.waypoint_times(movement)[2]
        self.assertAlmostEqual(order.t_fire, arrival)
        self.assertGreater(order.t_fire, 0.0)

    def test_at_time_is_not_before_the_arrival(self):
        mission, movement = self.mission(StartCondition.at_time(900.0), waypoint=1)
        self.assertEqual(AF.fire_orders(mission, movement, 0.0)[0].t_fire, 900.0)
        # un istante anteriore all'arrivo: vale l'arrivo
        mission, movement = self.mission(StartCondition.at_time(1.0), waypoint=2)
        self.assertAlmostEqual(AF.fire_orders(mission, movement, 0.0)[0].t_fire, MA.waypoint_times(movement)[2])

    def test_at_time_is_relative_to_the_session_start(self):
        mission, movement = self.mission(StartCondition.at_time(900.0))
        self.assertEqual(AF.fire_orders(mission, movement, 1_000.0)[0].t_fire, 1_900.0)

    def test_after_duration_follows_the_arrival(self):
        mission, movement = self.mission(StartCondition.after_duration(60.0), waypoint=2)
        order = AF.fire_orders(mission, movement, 0.0)[0]
        self.assertAlmostEqual(order.t_fire, MA.waypoint_times(movement)[2] + 60.0)

    def test_order_fields(self):
        mission, movement = self.mission(StartCondition.on_arrival(), weapon='2A64-152mm')
        [order] = AF.fire_orders(mission, movement, 0.0)
        self.assertEqual((order.mission_id, order.asset_id, order.waypoint_index, order.action_index),
                         (mission.mission_id, 'Red-Art/art0', 1, 0))
        self.assertEqual((order.aim_x, order.aim_y, order.dispersion_m, order.rounds, order.weapon),
                         (100.0, -50.0, 120.0, 6, '2A64-152mm'))
        self.assertEqual(AF.area_fire_event_id(order), f'area_fire|{mission.mission_id}|Red-Art/art0|1|0')

    def test_no_action_no_order(self):
        art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 1, origin=(-15_000.0, 0.0), prefix='art')])
        target = Target(kind=TargetKind.POINT, position=Point3D(0.0, 0.0, 0.0))
        mission = F.missions_for(art, [(-14_500.0, 0.0)], mission_type='Fire_Support', target=target)[0]
        self.assertEqual(AF.fire_orders(mission, MA.mission_movements(mission, 0.0)[0], 0.0), [])

    def test_the_same_action_gives_one_order_per_asset(self):
        art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 2, origin=(-15_000.0, 0.0),
                                                      step=(0.0, 100.0), prefix='art')])
        target = Target(kind=TargetKind.POINT, position=Point3D(0.0, 0.0, 0.0))
        action = MissionAction(ActionKind.TASK, FIRE_AT_POINT_ACTION, params={'rounds': 2})
        mission = F.missions_for(art, [(-14_500.0, 0.0)], mission_type='Fire_Support', target=target,
                                 actions={1: [action]})[0]
        orders = [order for movement in MA.mission_movements(mission, 0.0)
                  for order in AF.fire_orders(mission, movement, 0.0)]
        self.assertEqual([order.asset_id for order in orders], ['Red-Art/art0', 'Red-Art/art1'])


# ── Risoluzione ───────────────────────────────────────────────────────────────

class TestResolveAreaFire(_Fixture, unittest.TestCase):

    def test_result_shape(self):
        rng = _rng()
        result = self.resolve(_order(rounds=3), rng=rng)
        weapon = FC.area_fire_weapon(self.shooter, 15_000.0)
        self.assertEqual(result.forces, ())
        self.assertEqual((result.t_start, result.t_end), (600.0, 600.0 + weapon.time_of_flight))
        self.assertEqual(result.salvos, ())
        self.assertEqual(result.interception_events, ())
        self.assertEqual(result.ammunition_events, (ER.AmmunitionEvent(time=600.0, asset_id=SHOOTER, rounds=3,
                                                                       weapon=GUN),))
        self.assertTrue(all(event.time == result.t_end and event.source_id == SHOOTER and event.weapon == GUN
                            for event in result.damage_events))

    def test_nobody_in_the_disc_no_damage_and_two_draws_per_round(self):
        self.positions[ENEMY] = (3_000.0, 0.0, 0.0)
        rng = _rng()
        result = self.resolve(_order(rounds=5), rng=rng)
        self.assertEqual(result.damage_events, ())
        self.assertEqual(rng.draws, 10)                    # 2 per colpo (punto d'impatto), nessuna estrazione di danno
        self.assertEqual(result.ammunition_events[0].rounds, 5)

    def test_a_target_in_the_lethal_radius_is_hit_with_the_expected_frequency(self):
        """Bersaglio fermo nel punto, un colpo per seed su 200 seed: frazione dei colpi a segno attesa dal rapporto fra
        l'area del disco letale e quella del disco di dispersione (entro 5 sigma)."""
        weapon = FC.area_fire_weapon(self.shooter, 15_000.0)
        probability = (AF.lethal_radius(weapon) / AF.AREA_FIRE_MIN_DISPERSION_M) ** 2
        runs = 200
        hits = sum(len(self.resolve(rng=_rng(str(seed))).damage_events) for seed in range(runs))
        sigma = math.sqrt(runs * probability * (1.0 - probability))
        self.assertLess(abs(hits - runs * probability), 5.0 * sigma)
        self.assertGreater(hits, 0)

    def test_the_position_is_read_at_the_impact_time(self):
        """Il bersaglio e' nel punto al tiro e ne e' uscito all'impatto: nessun danno (e nessuna estrazione di danno)."""
        weapon = FC.area_fire_weapon(self.shooter, 15_000.0)
        t_impact = 600.0 + weapon.time_of_flight
        rng = _rng()
        result = AF.resolve_area_fire(_order(rounds=4), self.shooter, [self.enemy],
                                      lambda asset_id, time: ((0.0, 0.0, 0.0) if time < t_impact - 1e-6
                                                              else (3_000.0, 0.0, 0.0))
                                      if asset_id == ENEMY else self.positions[asset_id], rng)
        self.assertEqual(result.damage_events, ())
        self.assertEqual(rng.draws, 8)

    def test_the_stream_is_deterministic(self):
        first = self.resolve(_order(rounds=30), rng=_rng('same'))
        second = self.resolve(_order(rounds=30), rng=_rng('same'))
        other = self.resolve(_order(rounds=30), rng=_rng('other'))
        self.assertEqual(first, second)
        self.assertGreater(len(first.damage_events), 0)
        self.assertNotEqual(first.damage_events, other.damage_events)

    def test_the_draw_order_is_point_then_hits_per_round(self):
        """Contratto dell'ordine: 2 estrazioni per colpo e poi 1 per nemico a segno; il numero totale lo conferma."""
        rng = _rng()
        result = self.resolve(_order(rounds=10), rng=rng)
        self.assertEqual(rng.draws, 2 * 10 + len(result.damage_events))

    def test_damage_events_are_chained_on_the_health(self):
        result = self.resolve(_order(rounds=40), rng=_rng())
        events = [event for event in result.damage_events if event.target_id == ENEMY]
        self.assertGreater(len(events), 1)
        self.assertEqual(events[0].health_before, DM.HEALTH_MAX)

        for before, after in zip(events, events[1:]):
            self.assertEqual(after.health_before, before.health_after)

        # un nemico distrutto non e' piu' colpito
        self.assertTrue(all(not event.destroyed for event in events[:-1]))

    def test_a_destroyed_enemy_is_not_hit(self):
        self.enemy.apply_damage(-self.enemy.health)
        rng = _rng()
        result = self.resolve(_order(rounds=20), rng=rng)
        self.assertEqual(result.damage_events, ())
        self.assertEqual(rng.draws, 40)

    def test_only_the_given_enemies_are_hit(self):
        """Il chiamante passa solo i nemici (niente fuoco amico): un amico nel punto non e' mai colpito."""
        friend = F.make_vehicle(self.red, 'Red/friend', 'BMP-2', (0.0, 0.0, 0.0))
        self.positions['Red/friend'] = (0.0, 0.0, 0.0)
        result = self.resolve(_order(rounds=30), enemies=[self.enemy])
        self.assertNotIn(friend.id, {event.target_id for event in result.damage_events})

    def test_enemies_are_resolved_in_id_order(self):
        second = F.make_vehicle(self.blue, 'Blue/aaa', 'BMP-2', (0.0, 0.0, 0.0))
        self.positions['Blue/aaa'] = (0.0, 0.0, 0.0)
        a = self.resolve(_order(rounds=30), enemies=[self.enemy, second], rng=_rng('x'))
        b = self.resolve(_order(rounds=30), enemies=[second, self.enemy], rng=_rng('x'))
        self.assertEqual(a, b)
        self.assertEqual(a.damage_events[0].target_id, 'Blue/aaa')

    def test_pk_zero_or_aircraft_in_flight_has_no_effect_and_no_draw(self):
        flying = F.make_aircraft(self.blue, 'Blue/ac', 'F-16C Block 52d', (0.0, 0.0, 3_000.0), loadout='Strike')
        self.positions['Blue/ac'] = (0.0, 0.0, 3_000.0)
        rng = _rng()
        result = self.resolve(_order(rounds=10), enemies=[flying], rng=rng)
        self.assertEqual(result.damage_events, ())
        self.assertEqual(rng.draws, 20)

    def test_a_grounded_aircraft_is_a_surface_target(self):
        parked = F.make_aircraft(self.blue, 'Blue/ac', 'F-16C Block 52d', (0.0, 0.0, 0.0), loadout='Strike')
        self.positions['Blue/ac'] = (0.0, 0.0, 0.0)
        result = self.resolve(_order(rounds=40), enemies=[parked], grounded_at=lambda asset_id, time: True)
        self.assertGreater(len(result.damage_events), 0)
        self.assertEqual({event.target_id for event in result.damage_events}, {'Blue/ac'})

    def test_stock_limits_the_rounds(self):
        self.shooter.stores = {GUN: 3}
        result = self.resolve(_order(rounds=10))
        self.assertEqual(result.ammunition_events[0].rounds, 3)

    def test_no_stock_no_fire(self):
        self.shooter.stores = {GUN: 0}
        self.assertIsNone(self.resolve())

    def test_out_of_range_no_fire(self):
        self.assertIsNone(self.resolve(_order(aim_x=30_000.0)))

    def test_range_is_from_the_shooter_position_at_the_firing_time(self):
        self.positions[SHOOTER] = (5_000.0, 0.0, 0.0)           # a 5 km dal punto: in portata
        self.assertIsNotNone(self.resolve())

    def test_no_position_no_fire(self):
        del self.positions[SHOOTER]
        self.assertIsNone(self.resolve())

    def test_inactive_shooter_does_not_fire(self):
        self.assertIsNone(self.resolve(inactive_from=600.0))        # passivo proprio da t_fire
        self.assertIsNone(self.resolve(inactive_from=10.0))
        self.assertIsNotNone(self.resolve(inactive_from=601.0))
        self.assertIsNotNone(self.resolve(inactive_from=None))

    def test_the_declared_weapon_and_its_lethal_radius(self):
        order = _order(aim_x=-15_000.0 + 1_000.0, weapon='NSVT-12.7', rounds=2)
        result = self.resolve(order)
        self.assertEqual(result.ammunition_events[0].weapon, 'NSVT-12.7')
        self.assertEqual(AF.lethal_radius(FC.area_fire_weapon(self.shooter, 1_000.0, 'NSVT-12.7')),
                         AF.AREA_FIRE_LETHAL_RADIUS_PER_MM * 12.7)

    def test_a_weapon_that_is_not_the_shooters_gives_no_fire(self):
        self.assertIsNone(self.resolve(_order(weapon='M284-155mm')))

    def test_lethal_radius_from_the_caliber_or_the_fallback(self):
        gun = FC.area_fire_weapon(self.shooter, 1_000.0)
        self.assertEqual(AF.lethal_radius(gun), AF.AREA_FIRE_LETHAL_RADIUS_PER_MM * 152.0)
        no_caliber = FC.AreaWeapon('x', None, None, 1.0, 1)
        self.assertEqual(AF.lethal_radius(no_caliber), AF.AREA_FIRE_LETHAL_RADIUS_M)

    def test_the_resolution_does_not_mutate_the_assets(self):
        health, stock = self.enemy.health, self.shooter.stock_of(GUN)
        self.resolve(_order(rounds=40))
        self.assertEqual((self.enemy.health, self.shooter.stock_of(GUN)), (health, stock))

    def test_the_result_is_applicable(self):
        result = self.resolve(_order(rounds=5), rng=_rng('apply'))
        stock = self.shooter.stock_of(GUN)
        summary = ER.apply_engagement_result(result, self.red, self.blue)
        self.assertEqual(self.shooter.stock_of(GUN), stock - 5)
        self.assertEqual(summary['missing_assets'], 0)


# ── Arma del tiro (Fire_Control) ──────────────────────────────────────────────

class TestAreaFireWeapon(_Fixture, unittest.TestCase):

    def test_howitzer_gun_from_the_registry(self):
        weapon = FC.area_fire_weapon(self.shooter, 10_000.0)
        self.assertEqual((weapon.model, weapon.caliber_mm, weapon.max_range_m, weapon.stock_per_round),
                         (GUN, 152.0, 24_700.0, 1))
        self.assertAlmostEqual(weapon.time_of_flight, FC.ENGAGEMENT_RANGE_FRACTION * 24_700.0 / 810.0)

    def test_range(self):
        self.assertIsNotNone(FC.area_fire_weapon(self.shooter, 24_700.0))
        self.assertIsNone(FC.area_fire_weapon(self.shooter, 24_701.0))

    def test_stock_callable(self):
        self.assertIsNotNone(FC.area_fire_weapon(self.shooter, 1_000.0, stock_of=lambda model: 1))
        self.assertIsNotNone(FC.area_fire_weapon(self.shooter, 1_000.0, stock_of=lambda model: None))
        self.assertIsNone(FC.area_fire_weapon(self.shooter, 1_000.0, stock_of=lambda model: 0))

    def test_missiles_and_aircraft_are_excluded(self):
        sam = F.make_vehicle(self.red, 'Red/sam', '9K35-Strela-10', (0.0, 0.0, 0.0))
        plane = F.make_aircraft(self.red, 'Red/ac', 'F-16C Block 52d', (0.0, 0.0, 0.0), loadout='Strike')
        self.assertIsNone(FC.area_fire_weapon(sam, 100.0))
        self.assertIsNone(FC.area_fire_weapon(plane, 100.0))
        self.assertIsNone(FC.area_fire_weapon(sam, 100.0, 'Strela-10M'))     # nemmeno dichiarata, se missile

    def test_naval_gunfire(self):
        ship = F.make_ship(self.red, 'Red/ship', 'USS Arleigh Burke IIa', (0.0, 0.0, 0.0))
        weapon = FC.area_fire_weapon(ship, 10_000.0)
        self.assertEqual((weapon.model, weapon.caliber_mm), ('Mk-45-5in', 127.0))
        self.assertEqual(FC.area_fire_weapon(ship, 10_000.0).max_range_m, 24_000.0)

    def test_pk_is_the_template_cell(self):
        weapon = FC.area_fire_weapon(self.shooter, 1_000.0)
        keys, dimension, _ = FC.target_key(self.enemy)
        self.assertEqual(FC.area_fire_pk(weapon, self.enemy), FC._cell(weapon.entry, keys, dimension)[1])

    def test_pk_aircraft(self):
        weapon = FC.area_fire_weapon(self.shooter, 1_000.0)
        plane = F.make_aircraft(self.blue, 'Blue/ac', 'F-16C Block 52d', (0.0, 0.0, 3_000.0), loadout='Strike')
        self.assertIsNone(FC.area_fire_pk(weapon, plane))
        self.assertIsNotNone(FC.area_fire_pk(weapon, plane, grounded=True))


# ── L'evento di sessione ──────────────────────────────────────────────────────

def _session(variant='default', rounds=40, mission_changes=None, extra_blue=(), duration=1_200.0, **switches):
    """Una missione di fuoco (2S19 -> punto (0, 0)) contro Blue-Stay fermo nel punto; `variant` 'default'."""
    art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 1, origin=(-15_000.0, 0.0), prefix='art')])
    stay = F.build_force('Blue-Stay', 'Blue', [F.Unit('vehicle', 'BMP-2', 2, origin=(0.0, 0.0), step=(0.0, 60.0),
                                                    prefix='ifv')])
    target = Target(kind=TargetKind.POINT, position=Point3D(0.0, 0.0, 0.0))
    action = MissionAction(ActionKind.TASK, FIRE_AT_POINT_ACTION, params={'rounds': rounds},
                           start=StartCondition.at_time(600.0))
    missions = F.missions_for(art, [(-14_500.0, 0.0)], mission_type='Fire_Support', target=target, actions={1: [action]})

    if mission_changes:
        missions = [dataclasses.replace(mission, **mission_changes) for mission in missions]

    patches = [patch.object(SS, name, value) for name, value in switches.items()]

    for started in patches:
        started.start()

    try:
        outcome = F.run('AF-SESSION', [art], [stay, *extra_blue], make_registry_fire_control(), duration=duration,
                        missions=missions)
    finally:
        for started in patches:
            started.stop()

    return outcome, art, stay


class TestAreaFireInSession(F.LoggerSilencer, unittest.TestCase):

    def test_event_order_constants(self):
        self.assertLess(SS.ENGAGEMENT_EVENT, SS.AREA_FIRE_EVENT)
        self.assertLess(SS.AREA_FIRE_EVENT, SS.MOVEMENT_EVENT)

    def test_the_result_is_applied_to_the_real_assets(self):
        outcome, art, stay = _session()
        shots = sum(event.rounds for event in outcome.ammunition_events)
        self.assertEqual(shots, 40)
        self.assertEqual(art.assets['Red-Art/art0'].stock_of(GUN), 50 - 40)
        lost = sum(event.health_delta for event in outcome.damage_events)
        self.assertLess(lost, 0)
        self.assertEqual(sum(DM.HEALTH_MAX - asset.health for asset in stay.assets.values()), -lost)

    def test_the_same_outcome_without_episodes_g4a(self):
        """Il percorso della coda degli ingaggi (G4a spento) risolve lo stesso evento."""
        on, *_ = _session()
        off, *_ = _session(G4_EPISODES=False)
        self.assertEqual(on.damage_events, off.damage_events)
        self.assertEqual(on.ammunition_events, off.ammunition_events)

    def test_the_switch_off_ignores_the_action(self):
        outcome, art, stay = _session(F7_AREA_FIRE=False)
        self.assertEqual((outcome.damage_events, outcome.ammunition_events), ((), ()))
        self.assertEqual(art.assets['Red-Art/art0'].stock_of(GUN), 50)

    def test_destroyed_assets_have_the_destroyed_posture(self):
        outcome, art, stay = _session(rounds=50)
        destroyed = [event for event in outcome.damage_events if event.destroyed]
        self.assertTrue(destroyed)

        for event in destroyed:
            self.assertEqual(outcome.postures[event.target_id], MA.DESTROYED_POSTURE)

    def test_an_activity_end_before_the_firing_time_means_no_fire(self):
        """Fine di attivita' nota a monte (durata massima 300 s) prima del tiro a 600 s: l'asset e' passivo."""
        outcome, art, stay = _session(mission_changes={'end_criteria': EndCriteria(max_duration_s=300.0)})
        self.assertEqual((outcome.damage_events, outcome.ammunition_events), ((), ()))
        self.assertEqual(art.assets['Red-Art/art0'].stock_of(GUN), 50)
        # premessa: una durata maggiore del tiro non lo impedisce
        outcome, *_ = _session(mission_changes={'end_criteria': EndCriteria(max_duration_s=900.0)})
        self.assertEqual(len(outcome.ammunition_events), 1)

    def test_a_shooter_destroyed_before_the_firing_time_does_not_fire(self):
        art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 1, origin=(-15_000.0, 0.0), prefix='art')])
        art.assets['Red-Art/art0'].apply_damage(-art.assets['Red-Art/art0'].health)
        stay = F.build_force('Blue-Stay', 'Blue', [F.Unit('vehicle', 'BMP-2', 1, origin=(0.0, 0.0), prefix='ifv')])
        target = Target(kind=TargetKind.POINT, position=Point3D(0.0, 0.0, 0.0))
        action = MissionAction(ActionKind.TASK, FIRE_AT_POINT_ACTION, params={'rounds': 5})
        missions = F.missions_for(art, [(-14_500.0, 0.0)], mission_type='Fire_Support', target=target,
                                  actions={1: [action]})
        outcome = F.run('AF-DEAD', [art], [stay], make_registry_fire_control(), duration=900.0, missions=missions)
        self.assertEqual(outcome.ammunition_events, ())

    def test_a_shot_after_the_session_end_is_not_scheduled(self):
        outcome, art, stay = _session(duration=300.0)           # il tiro e' a 600 s
        self.assertEqual((outcome.damage_events, outcome.ammunition_events), ((), ()))

    def test_the_impact_may_follow_the_session_end(self):
        """Come una salva in volo: l'impatto oltre la fine estende l'intervallo dell'esito."""
        outcome, *_ = _session(duration=605.0)
        self.assertEqual(len(outcome.ammunition_events), 1)
        self.assertGreater(outcome.t_end, 605.0)


if __name__ == '__main__':
    unittest.main()
