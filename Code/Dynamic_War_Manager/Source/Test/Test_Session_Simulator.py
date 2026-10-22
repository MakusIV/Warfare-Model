"""Tests per Logic/Session_Simulator — FASE 6 del motore di sessioni virtuali.

L'orchestratore non ha logica di calcolo propria: mette in fila scheduler, risolutore,
applicazione, carburante e assemblaggio. I test verificano quindi la FILA — che i pezzi si
incastrino su oggetti reali e che l'ordine sia quello dichiarato — non i singoli modelli,
gia' coperti dai rispettivi test.

Strategia di setup
------------------
* Forze `Military` REALI e rotte `DataType.Route/Edge/Waypoint` REALI.
* Asset: sottoclassi REALI di `Mobile` chiamate `Aircraft`/`Vehicle`, perche'
  `Contact_Scheduler.detection_mode_for` classifica per nome di classe (stessa tecnica di
  Test_Contact_Scheduler). Salute, danno, munizioni e carburante sono quindi quelli veri di
  `Asset`/`Mobile`; sono imposti solo portata di rilevamento e autonomia (i registri sono
  coperti da Test_Mobile/Test_Aircraft), cosi' ogni numero e' calcolabile a mano.
* Profili di reazione imposti, per non dipendere dai default di Reaction_Profile.
* Dal 2026-10-05 (Fase 3 del piano della Missione) le rotte arrivano dalle `Mission` dell'ordine:
  `_air_mission` costruisce una missione aerea su una rotta di test (partenza in volo, ultimo
  punto LAND: semplificazione di scenario, rotta senza rientro, da completare con RTB in F5-F6).
  Le coppie di aerei della stessa forza su rotte parallele sono UNA missione con offset laterale.
"""

import dataclasses
import json
import unittest
from math import sqrt
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AbortReason,
    ActionKind,
    AssetEndReason,
    AssetState,
    EndCriteria,
    Mission,
    MissionAction,
    MissionAsset,
    MissionRules,
    MissionStatus,
    MissionWaypoint,
    Operation,
    StartMode,
    Target,
    TargetKind,
    TargetProvenance,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Context.Context import MILITARY_CATEGORY
from Code.Dynamic_War_Manager.Source.Context.Reaction_Profile import ReactionProfile
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA

_SOURCE = 'Code.Dynamic_War_Manager.Source.'
_LOGGERS = [_SOURCE + name + '.logger' for name in (
    'Asset.Mobile', 'Asset.Asset', 'Logic.Engagement_Resolver', 'Logic.Contact_Scheduler',
    'Logic.Fuel_Model', 'Logic.Session_Simulator', 'Command.Session_Types', 'Block.Military',
    'Command.Mission_Types', 'Logic.Mission_Adapter')]

# Autonomie imposte [m]: al regime di combattimento si consuma il doppio.
AUTONOMY = {'nominal': 1_000_000.0, 'max': 500_000.0}
SENSOR_RANGE = 5_000.0


# ── ASSET E FORZE ─────────────────────────────────────────────────────────────

class _SensorMixin:
    def detection_range(self, mode, sensor=None, range_type='acquisition_range'):
        return SENSOR_RANGE

    def fuel_autonomy(self, regime='nominal'):
        return AUTONOMY[regime]


class Aircraft(_SensorMixin, Mobile):
    """Nome di classe -> modo 'air' per lo scheduler."""


class Vehicle(_SensorMixin, Mobile):
    """Nome di classe -> modo 'ground' per lo scheduler."""


def _asset(cls, asset_id, x, y, z=0.0, ammunition=20, fuel=1.0, speed=None):
    asset = cls(block=MagicMock(spec=Block), name=asset_id, position=Point3D(x, y, z))
    asset.id = asset_id
    asset.ammunition = ammunition
    asset.fuel = fuel

    if speed is not None:
        asset.speed = {'nominal': speed, 'max': speed}

    return asset


def _force(name, side, assets):
    military = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name=name, side=side)
    # Id STABILE: Block genera un id con suffisso casuale (Utility.setId), e l'id di forza e'
    # chiave dell'RNG. In campagna l'id e' persistito; qui lo si fissa come farebbe il caricamento.
    military.id = name
    military._assets = {asset.id: asset for asset in assets}
    return military


def _route(points, speed, name, z=0.0):
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(x, y, z), obj_reference=None)
                 for i, (x, y) in enumerate(points)]
    edges = {}

    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0,
                                       speed=speed, name=f'{name}-E{i}')

    return Route(route_type='air', edges=edges, name=name)


def _air_mission(mission_id, force, route, assets, target_block='Red', start_time=0.0):
    """Missione aerea di test sulla rotta `route` per `assets` = [(asset_id, right_m), ...].

    Partenza in volo, ultimo punto LAND: semplificazione di scenario (rotta senza rientro, da
    completare con RTB in F5-F6). Bersaglio GROUP osservato all'istante 0.
    """
    waypoints = route_waypoints(route)
    roles = [WaypointRole.NAV] * (len(waypoints) - 1) + [WaypointRole.LAND]
    members = tuple(MissionAsset(asset_id, 'lead' if index == 0 else 'wingman', right_m=right)
                    for index, (asset_id, right) in enumerate(assets))
    target = Target(kind=TargetKind.GROUP, target_id=target_block, provenance=TargetProvenance.OBSERVED,
                    observed_at=0.0)
    return Mission(mission_id=mission_id, block_id=force.id, domain='air', mission_type='CAS', assets=members,
                   target=target, route=route,
                   waypoints=tuple(MissionWaypoint(wp, role) for wp, role in zip(waypoints, roles)),
                   start_time=start_time, start_mode=StartMode.AIR)


def _profile(asset):
    return ReactionProfile(detection=4.0, evaluation=1.0, command=0.0, actuation=0.0, source='test')


SPEC = ER.ShotSpec(accuracy=0.7, destroy_capacity=0.3, rounds=1)


def _fire(shooter, target):
    return SPEC


class _Base(unittest.TestCase):
    def setUp(self):
        self._patches = [patch(target, MagicMock()) for target in _LOGGERS]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()

    def _scenario(self, red_offset=0.0):
        """Due forze per lato, due fronti indipendenti 100 km l'uno dall'altro.

        Fronte ovest (x = 0): Blue-North (2 aerei) sorvola Red-East (2 veicoli fermi).
        Fronte est (x = 100 km): Blue-South (1 aereo) sorvola Red-West (1 veicolo fermo).
        Rotte di 40 km a 200 m/s: 200 s. `red_offset` sposta tutti i rossi lungo y.
        """
        blue_north = _force('Blue-North', 'Blue', [
            _asset(Aircraft, 'bn1', 0, -20_000, speed=200.0),
            _asset(Aircraft, 'bn2', 500, -20_000, speed=200.0)])
        blue_south = _force('Blue-South', 'Blue', [
            _asset(Aircraft, 'bs1', 100_000, -20_000, speed=200.0)])
        red_east = _force('Red-East', 'Red', [
            _asset(Vehicle, 're1', 0, red_offset), _asset(Vehicle, 're2', 300, red_offset)])
        red_west = _force('Red-West', 'Red', [_asset(Vehicle, 'rw1', 100_000, red_offset)])

        # Blue-North: una missione, bn2 a 500 m sulla destra (est) di bn1 in rotta nord.
        missions = (
            _air_mission('M-north', blue_north, _route([(0, -20_000), (0, 20_000)], 200.0, 'r-bn1'),
                         [('bn1', 0.0), ('bn2', 500.0)], target_block='Red-East'),
            _air_mission('M-south', blue_south, _route([(100_000, -20_000), (100_000, 20_000)], 200.0, 'r-bs1'),
                         [('bs1', 0.0)], target_block='Red-West'),
        )

        return [blue_north, blue_south], [red_east, red_west], missions

    def _order(self, session_id='S-test', missions=(), **kwargs):
        kwargs.setdefault('t_end', 3600.0)
        return SessionOrder(session_id, t_start=0.0, missions=tuple(missions), **kwargs)

    def _run(self, session_id='S-test', red_offset=0.0, fire=_fire, **kwargs):
        blue, red, missions = self._scenario(red_offset)
        outcome = SS.run_session(self._order(session_id, missions), blue, red, fire,
                                 reaction_profile_for=_profile, **kwargs)
        return outcome, blue, red


class TestEngagedAssetsCountsInterceptions(unittest.TestCase):
    """Regressione: un asset che ha SOLO intercettato deve contare come 'ha combattuto'.

    `_engaged_assets` decide il regime di consumo carburante (COMBAT_REGIME vs CRUISE_REGIME,
    v. `run_session`). Fino a questo fix leggeva `salvos`/`ammunition_events` ma non
    `interception_events`: da quando le intercettazioni sono un tipo a se' (`InterceptionEvent`,
    non piu' `AmmunitionEvent(purpose=PURPOSE_INTERCEPTION)`), un intercettore che non ha mai
    sparato una salva propria e non e' mai stato bersaglio restava classificato 'nominal'
    (crociera) invece di 'max' (combattimento) — nessun test se ne accorgeva.
    """

    def test_interceptor_only_asset_is_engaged(self):
        result = ER.EngagementResult(
            t_start=0.0, t_end=1.0, forces=(),
            interception_events=(
                ER.InterceptionEvent(time=1.0, asset_id='sam1', interceptions=2,
                                     force_id='red', salvo_ids=(0,)),
            ),
        )

        self.assertIn('sam1', SS._engaged_assets(result))

    def test_asset_with_no_activity_is_not_engaged(self):
        result = ER.EngagementResult(t_start=0.0, t_end=1.0, forces=())

        self.assertEqual(SS._engaged_assets(result), set())


# ── SCENARIO END-TO-END ───────────────────────────────────────────────────────

class TestEndToEnd(_Base):
    """2 forze per lato, rotte reali: contatti, ingaggi, applicazione, carburante, esito."""

    def setUp(self):
        super().setUp()
        self.outcome, self.blue, self.red = self._run()
        self.assets = {a.id: a for f in self.blue + self.red for a in f.assets.values()}

    def test_one_engagement_per_front(self):
        """Dalla F4b la forza d'ingaggio blu e' la MISSIONE (id = mission_id), i rossi senza
        missione restano il loro blocco."""
        self.assertIsInstance(self.outcome, SessionOutcome)
        pairs = {tuple(o.force_id for o in engagement) for engagement in self.outcome.engagement_outcomes}
        self.assertEqual(pairs, {('M-north', self.red[0].id), ('M-south', self.red[1].id)})
        self.assertEqual([o.block_id for o in self.outcome.outcomes_of_block(self.blue[0].id)], [self.blue[0].id])

    def test_fronts_are_resolved_in_time_order(self):
        """Stesso istante di primo contatto: vale l'id canonico dell'evento (JSON)."""
        first = [engagement[0].force_id for engagement in self.outcome.engagement_outcomes]
        expected = sorted(['M-north', 'M-south'],
                          key=lambda fid: SS.engagement_event_id(
                              fid, self.red[0].id if fid == 'M-north' else self.red[1].id))
        self.assertEqual(first, expected)

    def test_something_actually_happened(self):
        self.assertGreater(len(self.outcome.damage_events), 0)
        self.assertGreater(len(self.outcome.ammunition_events), 0)

    def test_damage_is_applied_to_the_real_assets(self):
        final = {}
        for event in self.outcome.damage_events:
            final[event.target_id] = event.health_after

        for asset_id, asset in self.assets.items():
            self.assertEqual(asset.health, final.get(asset_id, 100), asset_id)

    def test_ammunition_is_applied_to_the_real_assets(self):
        consumed = self.outcome.ammunition_consumed()

        for asset_id, asset in self.assets.items():
            self.assertEqual(asset.ammunition, 20 - consumed.get(asset_id, 0), asset_id)

    def test_fuel_events_only_for_moving_assets(self):
        """Un evento di movimento per aereo (G3: piu' gli eventi istantanei d'ingaggio degli stessi aerei)."""
        moving = [e.asset_id for e in self.outcome.fuel_events if e.regime != FM.ENGAGEMENT_REGIME]
        self.assertEqual(sorted(moving), ['bn1', 'bn2', 'bs1'])
        self.assertTrue({e.asset_id for e in self.outcome.fuel_events} <= {'bn1', 'bn2', 'bs1'})

    def test_fuel_distance_time_and_application(self):
        consumed = self.outcome.fuel_consumed()

        for event in self.outcome.fuel_events:
            if event.regime != FM.ENGAGEMENT_REGIME:
                self.assertAlmostEqual(event.distance, 40_000.0, places=6)
                self.assertAlmostEqual(event.time, 200.0, places=6)

            self.assertAlmostEqual(self.assets[event.asset_id].fuel, 1.0 - consumed[event.asset_id])

    @staticmethod
    def _fought(outcome):
        fought = set()
        for event in outcome.ammunition_events:
            fought.add(event.asset_id)
        for event in outcome.damage_events:
            fought.add(event.target_id)
        return fought

    def test_regime_is_combat_only_for_assets_that_fought(self):
        """G3 spento: la regola della F6-A, tutto il movimento di chi ha combattuto al regime 'max'."""
        with patch.object(SS, 'G3_ENGAGEMENT_FUEL', False):
            outcome, _, _ = self._run()

        fought = self._fought(outcome)
        self.assertTrue(fought & {'bn1', 'bn2', 'bs1'})

        for event in outcome.fuel_events:
            expected = SS.COMBAT_REGIME if event.asset_id in fought else SS.CRUISE_REGIME
            self.assertEqual(event.regime, expected, event.asset_id)
            self.assertAlmostEqual(event.amount, 40_000.0 / AUTONOMY[expected])

    def test_g3_movement_at_cruise_plus_one_engagement_charge(self):
        """G3: movimento sempre alla crociera; chi ha combattuto consuma in piu' la riserva di disimpegno (ripiego
        'max': 200 m/s x 300 s / 500 km = 0,12) all'istante della sua prima salva, prima del tratto."""
        results = []
        original = ER.resolve_engagement

        def resolve(*args, **kwargs):
            results.append(original(*args, **kwargs))
            return results[-1]

        with patch.object(SS.ER, 'resolve_engagement', side_effect=resolve):
            outcome, _, _ = self._run()

        self.assertEqual([e for e in outcome.fuel_events], list(self.outcome.fuel_events))
        salvos = [salvo for result in results if result is not None for salvo in result.salvos]
        fought = self._fought(outcome) & {'bn1', 'bn2', 'bs1'}
        self.assertTrue(fought)

        for asset_id in ('bn1', 'bn2', 'bs1'):
            events = [e for e in outcome.fuel_events if e.asset_id == asset_id]
            moving = [e for e in events if e.regime != FM.ENGAGEMENT_REGIME]
            charges = [e for e in events if e.regime == FM.ENGAGEMENT_REGIME]
            self.assertEqual(len(moving), 1, asset_id)
            self.assertEqual(moving[0].regime, SS.CRUISE_REGIME, asset_id)
            self.assertAlmostEqual(moving[0].amount, 40_000.0 / AUTONOMY['nominal'])

            if asset_id not in fought:
                self.assertEqual(charges, [], asset_id)
                continue

            first = min(s.t_launch for s in salvos if asset_id in (s.shooter_id, s.target_id))
            self.assertEqual(len(charges), 1, asset_id)
            self.assertAlmostEqual(charges[0].amount, 200.0 * FM.DISENGAGE_TIME / AUTONOMY['max'])
            self.assertEqual((charges[0].distance, charges[0].duration, charges[0].t_start),
                             (0.0, 0.0, charges[0].time))
            self.assertLess(charges[0].time, moving[0].time)
            self.assertEqual(events, [charges[0], moving[0]], asset_id)
            self.assertAlmostEqual(moving[0].fuel_before, charges[0].fuel_after)
            self.assertAlmostEqual(charges[0].time, first)

    def test_declared_interval(self):
        self.assertEqual((self.outcome.t_start, self.outcome.t_end), (0.0, 3600.0))


class TestSeedDiscipline(_Base):
    """RNG: uno stream per ingaggio, da SessionOrder.rng e solo da li'."""

    def test_same_order_same_outcome(self):
        first, _, _ = self._run('S-alpha')
        second, _, _ = self._run('S-alpha')
        self.assertEqual(first, second)
        self.assertGreater(len(first.damage_events), 0)

    def test_different_session_id_changes_the_draws(self):
        self.assertNotEqual(self._run('S-alpha')[0].damage_events,
                            self._run('S-beta')[0].damage_events)

    def test_engagement_uses_the_documented_stream(self):
        """Ripetere a mano l'ingaggio del fronte est con order.rng(None, event_id, 0), e la
        tempra delle forze con il flusso separato order.rng(None, temper_event_id, 0).

        Dalla F4b la forza blu e' la vista della missione 'M-south' e il suo id entra nell'event_id."""
        outcome, _, _ = self._run('S-gamma')
        # Scenario pulito (i due fronti non condividono forze), stesso ingaggio, stream documentato.
        blue3, red3, missions = self._scenario()
        routes = MA.mission_routes(missions)
        order = self._order('S-gamma')
        south = MA.MissionForce.of_mission(missions[1], blue3[1])
        windows = CS.schedule_contacts([blue3[1]], [red3[1]], 3600.0, routes=routes)
        legs = {'bs1': CS.clamp_legs(CS.route_legs(routes['bs1']), 0.0, 3600.0),
                'rw1': CS.static_legs(red3[1].assets['rw1'].position, 0.0, 3600.0)}
        manual = ER.resolve_engagement(
            south, red3[1], windows, _fire,
            order.rng(mission_id=None, event_id=SS.engagement_event_id('M-south', red3[1].id)),
            legs=legs, reaction_profile_for=_profile,
            breakpoint_rng=order.rng(mission_id=None, event_id=SS.temper_event_id('M-south', red3[1].id)))
        self.assertIn(manual.forces, outcome.engagement_outcomes)
        self.assertTrue(set(manual.damage_events) <= set(outcome.damage_events))

    def test_event_id_is_pure_and_unambiguous(self):
        self.assertEqual(SS.engagement_event_id('a', 'b'), SS.engagement_event_id('a', 'b'))
        self.assertNotEqual(SS.engagement_event_id('a:b', 'c'), SS.engagement_event_id('a', 'b:c'))
        self.assertNotEqual(SS.engagement_event_id('a', 'b'), SS.engagement_event_id('a', 'b', 'c'))

    def test_event_id_depends_on_the_set_of_forces_not_their_order(self):
        """Una componente ha un solo seed, qualunque sia l'ordine di passaggio delle forze."""
        self.assertEqual(SS.engagement_event_id('a', 'b'), SS.engagement_event_id('b', 'a'))
        self.assertEqual(SS.engagement_event_id('x', 'a', 'b'), SS.engagement_event_id('b', 'x', 'a'))

    def test_event_id_rejects_out_of_domain_arguments(self):
        for ids in (('a',), (), ('a', 'a'), ('a', ''), ('a', None)):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                SS.engagement_event_id(*ids)

    def test_temper_stream_is_distinct_and_order_independent(self):
        """Soglia di rottura (2026-09-29): la tempra ha un flusso proprio, non quello dell'ingaggio."""
        self.assertNotEqual(SS.temper_event_id('a', 'b'), SS.engagement_event_id('a', 'b'))
        self.assertEqual(SS.temper_event_id('a', 'b'), SS.temper_event_id('b', 'a'))
        for ids in (('a',), ('a', 'a')):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                SS.temper_event_id(*ids)


class TestNoContact(_Base):
    """Nessun incontro non e' un errore: esito vuoto ma valido."""

    def test_far_apart_forces_produce_no_engagement(self):
        outcome, blue, red = self._run(red_offset=10_000_000.0)
        self.assertEqual(outcome.engagement_outcomes, ())
        self.assertEqual(outcome.damage_events, ())
        self.assertEqual(outcome.ammunition_events, ())
        # Il movimento c'e' comunque, a regime di crociera.
        self.assertEqual(len(outcome.fuel_events), 3)
        self.assertTrue(all(e.regime == SS.CRUISE_REGIME for e in outcome.fuel_events))

    def test_nothing_moves_nothing_meets(self):
        blue, red, _ = self._scenario(red_offset=10_000_000.0)
        outcome = SS.run_session(self._order(), blue, red, _fire)
        # Dalla F5-B l'esito porta comunque la postura di ogni asset: aerei senza missione a terra,
        # veicoli in difesa.
        postures = {'bn1': MA.PARKED_POSTURE, 'bn2': MA.PARKED_POSTURE, 'bs1': MA.PARKED_POSTURE,
                    're1': MA.GROUND_DEFENSE_POSTURE, 're2': MA.GROUND_DEFENSE_POSTURE,
                    'rw1': MA.GROUND_DEFENSE_POSTURE}
        self.assertEqual(outcome, SessionOutcome('S-test', 0.0, 3600.0, postures=postures))

    def test_empty_sides(self):
        outcome = SS.run_session(self._order(), [], [], _fire)
        self.assertEqual(outcome, SessionOutcome('S-test', 0.0, 3600.0))


class TestTwoFronts(_Base):
    """Una forza impegnata su due fronti: UNA componente connessa, UN ingaggio congiunto.

    Il Raider (lato A) sorvola Red-A e poi Red-B (lato B): le finestre Raider-Red-A e
    Raider-Red-B legano le tre forze in una componente, risolta con una sola chiamata a
    `resolve_engagement` (prima erano due ingaggi applicati in sequenza).
    """

    def _forces(self):
        raider = _force('Raider', 'Blue', [_asset(Aircraft, 'x1', -20_000, 0, speed=200.0),
                                            _asset(Aircraft, 'x2', -20_000, 300, speed=200.0)])
        red_a = _force('Red-A', 'Red', [_asset(Vehicle, 'ra1', 0, 0)])
        red_b = _force('Red-B', 'Red', [_asset(Vehicle, 'rb1', 30_000, 0)])
        # Una missione: x2 300 m a sinistra (nord) di x1 in rotta est.
        missions = (_air_mission('M-raid', raider, _route([(-20_000, 0), (50_000, 0)], 200.0, 'r-x1'),
                                 [('x1', 0.0), ('x2', -300.0)], target_block='Red-A'),)
        return raider, red_a, red_b, missions

    def _two_fronts(self, session_id, reverse_red=False):
        raider, red_a, red_b, missions = self._forces()
        reds = [red_b, red_a] if reverse_red else [red_a, red_b]
        outcome = SS.run_session(self._order(session_id, missions), [raider], reds, _fire,
                                 reaction_profile_for=_profile)
        return outcome, raider, red_a, red_b

    def test_connected_forces_are_one_engagement(self):
        outcome, raider, red_a, red_b = self._two_fronts('S-fronts')
        self.assertEqual([tuple(o.force_id for o in e) for e in outcome.engagement_outcomes],
                         [('M-raid', red_a.id, red_b.id)])
        self.assertEqual(len(outcome.outcomes_of('M-raid')), 1)
        self.assertEqual(len(outcome.outcomes_of_block(raider.id)), 1)

    def test_one_resolver_call_with_all_forces(self):
        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as spy:
            outcome, raider, red_a, red_b = self._two_fronts('S-fronts')

        spy.assert_called_once()
        args, kwargs = spy.call_args
        self.assertEqual([f.id for f in (args[0], args[1], *kwargs['extra_forces'])],
                         sorted(['M-raid', red_a.id, red_b.id]))
        # Le finestre di entrambi i fronti arrivano nella stessa chiamata.
        pairs = {(w.asset_a_id, w.asset_b_id) for w in args[2]}
        self.assertTrue({a for a, _ in pairs} <= {'x1', 'x2'})
        self.assertEqual({b for _, b in pairs}, {'ra1', 'rb1'})
        self.assertGreater(len(outcome.damage_events), 0)

    def test_result_is_applied_to_all_the_forces_of_the_component(self):
        with patch.object(ER, 'apply_engagement_result', wraps=ER.apply_engagement_result) as spy:
            outcome, raider, red_a, red_b = self._two_fronts('S-fronts')

        spy.assert_called_once()
        self.assertEqual({f.id for f in spy.call_args[0][1:]}, {'M-raid', red_a.id, red_b.id})

        final = {}
        for event in outcome.damage_events:
            final[event.target_id] = event.health_after
        consumed = outcome.ammunition_consumed()

        for force in (raider, red_a, red_b):
            for asset_id, asset in force.assets.items():
                self.assertEqual(asset.health, final.get(asset_id, 100), asset_id)
                self.assertEqual(asset.ammunition, 20 - consumed.get(asset_id, 0), asset_id)

    def test_health_is_chained_within_the_joint_engagement(self):
        """Una sola timeline per asset: ogni before == l'after precedente."""
        for session_id in ('S-f1', 'S-f2', 'S-f3', 'S-f4'):
            outcome, *_ = self._two_fronts(session_id)
            last = {}

            for event in outcome.damage_events:
                if event.target_id in last:
                    self.assertEqual(event.health_before, last[event.target_id])
                last[event.target_id] = event.health_after

    def test_joint_engagement_is_deterministic(self):
        """Stesso ordine, forze con id stabili -> stesso esito; anche con i lati passati in
        un altro ordine (componente e seed dipendono dall'insieme delle forze)."""
        first, *_ = self._two_fronts('S-det')
        second, *_ = self._two_fronts('S-det')
        reversed_order, *_ = self._two_fronts('S-det', reverse_red=True)
        self.assertEqual(first, second)
        self.assertEqual(first, reversed_order)
        self.assertGreater(len(first.damage_events), 0)

    def test_stable_ids_from_the_constructor(self):
        """`Military(id=...)` (non la mutazione di .id) basta per il determinismo."""
        def build():
            raider = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name='Raider',
                              side='Blue', id='raider-stable')
            raider._assets = {a.id: a for a in (_asset(Aircraft, 'x1', -20_000, 0, speed=200.0),)}
            reds = []
            for name, x in (('red-a-stable', 0), ('red-b-stable', 30_000)):
                red = Military(mil_category=MILITARY_CATEGORY["Ground_Base"][1], name=name,
                               side='Red', id=name)
                red._assets = {f'{name}-1': _asset(Vehicle, f'{name}-1', x, 0)}
                reds.append(red)
            missions = (_air_mission('M-stable', raider, _route([(-20_000, 0), (50_000, 0)], 200.0, 'r-x1'),
                                     [('x1', 0.0)], target_block='red-a-stable'),)
            return SS.run_session(self._order('S-stable', missions), [raider], reds, _fire,
                                  reaction_profile_for=_profile)

        first, second = build(), build()
        self.assertEqual(first, second)
        self.assertEqual([tuple(o.force_id for o in e) for e in first.engagement_outcomes],
                         [('M-stable', 'red-a-stable', 'red-b-stable')])

    def test_disjoint_components_stay_separate(self):
        """Nessun legame fra i due fronti dello scenario base: due componenti, due chiamate."""
        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as spy:
            outcome, _, _ = self._run('S-disjoint')

        self.assertEqual(spy.call_count, 2)
        self.assertTrue(all(call.kwargs['extra_forces'] == [] for call in spy.call_args_list))
        self.assertEqual(len(outcome.engagement_outcomes), 2)


class TestConnectedComponents(unittest.TestCase):
    """`_connected_components`: grafo delle forze, visita deterministica."""

    def test_chain_is_one_component(self):
        groups = {('a1', 'b1'): ['w1'], ('a2', 'b1'): ['w2'], ('a2', 'b2'): ['w3']}
        self.assertEqual(SS._connected_components(groups),
                         [(('a1', 'a2', 'b1', 'b2'), ['w1', 'w2', 'w3'])])

    def test_disjoint_pairs_and_order_independence(self):
        groups = {('a2', 'b2'): ['w2'], ('a1', 'b1'): ['w1']}
        expected = [(('a1', 'b1'), ['w1']), (('a2', 'b2'), ['w2'])]
        self.assertEqual(SS._connected_components(groups), expected)
        self.assertEqual(SS._connected_components(dict(reversed(list(groups.items())))), expected)

    def test_empty(self):
        self.assertEqual(SS._connected_components({}), [])

    def test_forces_of_one_coordination_domain_share_the_component(self):
        """Dal 2026-10-11: due fronti disgiunti, ma a1 e a2 nello stesso dominio -> una run."""
        groups = {('a2', 'b2'): ['w2'], ('a1', 'b1'): ['w1']}
        domains = {'a1': 'a1', 'a2': 'a1', 'b1': 'b1', 'b2': 'b2'}
        self.assertEqual(SS._connected_components(groups, domains), [(('a1', 'a2', 'b1', 'b2'), ['w1', 'w2'])])
        self.assertEqual(SS._connected_components(groups, {'a1': 'a1'}), SS._connected_components(groups))


class TestSessionInterval(_Base):

    def test_open_session_requires_horizon(self):
        blue, red, missions = self._scenario()
        order = SessionOrder('S-open', t_start=0.0, missions=missions)

        with self.assertRaises(ValueError):
            SS.run_session(order, blue, red, _fire)

        outcome = SS.run_session(order, blue, red, _fire, horizon=600.0,
                                 reaction_profile_for=_profile)
        self.assertEqual(outcome.t_end, 600.0)

    def test_horizon_must_agree_with_the_order(self):
        blue, red, missions = self._scenario()

        with self.assertRaises(ValueError):
            SS.run_session(self._order(missions=missions), blue, red, _fire, horizon=10.0)

    def test_salvos_in_flight_extend_the_outcome(self):
        """Impatti dopo la fine: l'esito e' esteso, non troncato (R4)."""
        slow = ER.ShotSpec(accuracy=1.0, destroy_capacity=0.3, time_of_flight=5_000.0)
        outcome, _, _ = self._run(fire=lambda s, t: slow)
        self.assertGreater(outcome.t_end, 3600.0)
        self.assertGreaterEqual(outcome.t_end, max(e.time for e in outcome.damage_events))


class TestFuelExhaustion(_Base):
    """F6-A: il carburante vincola il movimento (tratti troncati all'esaurimento calcolato a monte)."""

    def _dry_flight(self, constraint=True, base=None, z=1_000.0):
        """b1 con carburante per 10 km su una rotta di 40 km a 200 m/s, quota 1000 m (planata 10 km):
        si esaurisce a 50 s in (0, 10 km). `base`: posizione (x, y) di una base aerea Blue."""
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0, 0, z=z, fuel=0.01, speed=200.0)])]

        if base is not None:
            airbase = Military(mil_category=MILITARY_CATEGORY['Air_Base'][0], name='Blue-Base', side='Blue')
            airbase.id = 'Blue-Base'
            airbase._assets = {'bb1': _asset(Vehicle, 'bb1', *base)}
            blue.append(airbase)

        route = _route([(0, 0), (0, 40_000)], 200.0, 'r-b1', z=z)
        # F6-B2: la missione dichiara di NON rientrare al bingo, cosi' l'esaurimento della F6-A resta il
        # soggetto del test anche con una base (con il bingo tornerebbe subito alla base, v. TestBingo).
        missions = (dataclasses.replace(_air_mission('M-b1', blue[0], route, [('b1', 0.0)]),
                                        end_criteria=EndCriteria(bingo=False)),)

        with patch.object(SS, 'F6_FUEL_CONSTRAINT', constraint), \
                patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
            outcome = SS.run_session(self._order(missions=missions), blue, [], _fire)

        return outcome, blue[0].assets['b1'], scheduler.call_args.kwargs['legs']['b1']

    def test_without_the_constraint_exhaustion_is_only_reported(self):
        """Interruttore spento: il comportamento di prima (E5), l'aereo completa la rotta a secco."""
        # Quota 0, la sessione registrata nella fotografia prima della F6-A (unita' 'ORC-fuel').
        outcome, b1, legs = self._dry_flight(constraint=False, z=0.0)
        event, = outcome.fuel_events
        self.assertTrue(event.exhausted)
        self.assertAlmostEqual(event.distance_covered, 10_000.0)
        self.assertEqual(b1.fuel, 0.0)
        self.assertAlmostEqual(legs[-1].t_end, 200.0)
        self.assertFalse(b1.is_destroyed())

    def test_aircraft_without_a_reachable_base_is_lost(self):
        outcome, b1, legs = self._dry_flight()
        self.assertAlmostEqual(legs[-1].t_end, 50.0)
        self.assertEqual(legs[-1].p_end, (0.0, 10_000.0, 1_000.0))
        event, = outcome.fuel_events
        self.assertTrue(event.exhausted)
        self.assertTrue(b1.is_destroyed())
        self.assertEqual(outcome.damage_events, ())
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual(mission.status, MissionStatus.DESTROYED)
        self.assertEqual(mission.asset_outcomes['b1'].end_reason, AssetEndReason.FUEL_EXHAUSTED)
        # F6-B1: un aereo perso per carburante ha postura `destroyed`; con l'interruttore spento quella
        # della F6-A (uscito di scena).
        self.assertEqual(outcome.postures['b1'], MA.DESTROYED_POSTURE)

        with patch.object(SS, 'F6_DESTROYED_POSTURE', False):
            outcome, _, _ = self._dry_flight()

        self.assertEqual(outcome.postures['b1'], MA.OFF_SCENE_POSTURE)

    def test_aircraft_glides_to_a_reachable_own_base(self):
        """Base a 6 km dal punto di esaurimento (planata 10 km): planata a 200 m/s, poi a terra."""
        outcome, b1, legs = self._dry_flight(base=(6_000.0, 10_000.0))
        glide, parked = legs[-2], legs[-1]
        self.assertEqual((glide.p_start, glide.p_end), ((0.0, 10_000.0, 1_000.0), (6_000.0, 10_000.0, 0.0)))
        t_land = 50.0 + sqrt(6_000.0 ** 2 + 1_000.0 ** 2) / 200.0
        self.assertAlmostEqual(glide.t_end, t_land)
        self.assertEqual((parked.p_start, parked.t_end), ((6_000.0, 10_000.0, 0.0), 3_600.0))
        self.assertFalse(b1.is_destroyed())
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.FUEL))
        asset = mission.asset_outcomes['b1']
        self.assertEqual((asset.state, asset.end_reason, asset.end_time),
                         (AssetState.OPERATIONAL, AssetEndReason.FUEL_EXHAUSTED, 50.0))
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)
        self.assertEqual(mission.actual_etas, (0.0, None))

    def test_parked_aircraft_with_an_empty_tank_stays_on_the_ground(self):
        """Serbatoio vuoto sul parcheggio (quota 0): nessun decollo, resta A TERRA nel punto (non perso)."""
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0, 0, fuel=0.0, speed=200.0)])]
        route = _route([(0, 0), (0, 40_000)], 200.0, 'r-b1')
        mission = _air_mission('M-b1', blue[0], route, [('b1', 0.0)], start_time=100.0)
        departure = dataclasses.replace(mission.waypoints[0], role=WaypointRole.DEPARTURE)
        mission = dataclasses.replace(mission, start_mode=StartMode.PARKING_COLD,
                                      waypoints=(departure,) + mission.waypoints[1:])

        with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
            outcome = SS.run_session(self._order(missions=(mission,)), blue, [], _fire)

        legs = scheduler.call_args.kwargs['legs']['b1']
        self.assertEqual([(leg.t_start, leg.t_end) for leg in legs], [(0.0, 100.0), (100.0, 3_600.0)])
        self.assertTrue(scheduler.call_args.kwargs['grounded'].at('b1', 3_000.0))
        self.assertFalse(blue[0].assets['b1'].is_destroyed())
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.ABORTED)

    def test_ground_unit_halts_and_stays(self):
        """Un veicolo a secco resta FERMO nel punto, presente fino a fine sessione, in difesa."""
        blue = [_force('Blue', 'Blue', [_asset(Vehicle, 'v1', 0, 0, fuel=0.002, speed=10.0)])]
        route = _ground_route([(0, 0), (0, 10_000)], 10.0, 'r-v1')

        with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
            outcome = SS.run_session(self._order(missions=(_ground_mission('M-v1', blue[0], route, 'v1'),)),
                                     blue, [], _fire)

        legs = scheduler.call_args.kwargs['legs']['v1']
        # Autonomia di test 1000 km: 0,002 -> 2 km, a 200 s.
        self.assertEqual([(leg.t_start, leg.t_end) for leg in legs], [(0.0, 200.0), (200.0, 3_600.0)])
        self.assertEqual(legs[-1].p_start, (0.0, 2_000.0, 0.0))
        mission = outcome.mission_outcomes['M-v1']
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.FUEL))
        self.assertEqual(outcome.postures['v1'], MA.GROUND_DEFENSE_POSTURE)
        self.assertFalse(blue[0].assets['v1'].is_destroyed())


class TestMissions(_Base):
    """Porta delle missioni (Fase 3 del piano della Missione): validazione ed esito di prima forma."""

    LETHAL = ER.ShotSpec(accuracy=1.0, destroy_capacity=1.0, rounds=1)

    def _far(self, session_id='S-mission', t_end=3600.0, missions=None):
        blue, red, default = self._scenario(red_offset=10_000_000.0)
        order = self._order(session_id, default if missions is None else missions, t_end=t_end)
        return SS.run_session(order, blue, red, _fire, reaction_profile_for=_profile), blue, red

    def test_routes_parameters_are_gone(self):
        blue, red, missions = self._scenario()

        with self.assertRaises(TypeError):
            SS.run_session(self._order(), blue, red, _fire, routes=MA.mission_routes(missions))

    def test_one_outcome_per_mission(self):
        outcome, _, _ = self._far()
        self.assertEqual(sorted(outcome.mission_outcomes), ['M-north', 'M-south'])

    def test_completed_mission(self):
        outcome, _, _ = self._far()
        north = outcome.mission_outcomes['M-north']
        self.assertEqual(north.status, MissionStatus.COMPLETED)
        self.assertEqual(north.actual_etas, (0.0, 200.0))

        for asset_id in ('bn1', 'bn2'):
            asset = north.asset_outcomes[asset_id]
            self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.ROUTE_COMPLETED))
            self.assertAlmostEqual(asset.end_time, 200.0)

    def test_route_cut_by_the_session_end_fails(self):
        outcome, _, _ = self._far(t_end=100.0)
        north = outcome.mission_outcomes['M-north']
        self.assertEqual(north.status, MissionStatus.FAILED)
        self.assertEqual(north.actual_etas, (0.0, None))
        self.assertEqual({(o.end_reason, o.end_time) for o in north.asset_outcomes.values()},
                         {(AssetEndReason.SESSION_END, 100.0)})

    def test_late_start_shifts_the_arrival(self):
        blue, red, missions = self._scenario(red_offset=10_000_000.0)
        late = _air_mission('M-late', blue[1], missions[1].route, [('bs1', 0.0)], start_time=150.0)
        order = self._order('S-late', (missions[0], late))
        outcome = SS.run_session(order, blue, red, _fire)
        self.assertEqual(outcome.mission_outcomes['M-late'].actual_etas, (150.0, 350.0))
        fuel = {e.asset_id: e.time for e in outcome.fuel_events}
        self.assertAlmostEqual(fuel['bs1'], 350.0)

    def test_asset_without_mission_stays_still(self):
        blue, red, missions = self._scenario(red_offset=10_000_000.0)
        outcome = SS.run_session(self._order('S-still', missions[:1]), blue, red, _fire)
        self.assertEqual(sorted(e.asset_id for e in outcome.fuel_events), ['bn1', 'bn2'])
        self.assertEqual(sorted(outcome.mission_outcomes), ['M-north'])

    # Partenze in volo senza basi: con l'uscita di scena del G4b (`G4_OFF_SCENE_EXIT`) un superstite di una forza
    # disingaggiata esce di scena (DISENGAGED); qui si prova la regola DESTROYED/COMPLETED.
    @patch.object(SS, 'G4_OFF_SCENE_EXIT', False)
    def test_destroyed_mission(self):
        def fire(shooter, target):
            return self.LETHAL if type(target).__name__ == 'Aircraft' else None

        blue, red, missions = self._scenario()
        outcome = SS.run_session(self._order('S-kill', missions), blue, red, fire, reaction_profile_for=_profile)
        killed = {e.target_id: e.time for e in outcome.damage_events if e.destroyed}
        # Fronte est: un solo aereo, abbattuto -> missione DESTROYED.
        self.assertIn('bs1', killed)
        self.assertEqual(outcome.mission_outcomes['M-south'].status, MissionStatus.DESTROYED)

        for mission_id in ('M-north', 'M-south'):
            mission = outcome.mission_outcomes[mission_id]
            all_killed = all(asset_id in killed for asset_id in mission.asset_outcomes)
            self.assertEqual(mission.status is MissionStatus.DESTROYED, all_killed, mission_id)

            for asset_id, asset in mission.asset_outcomes.items():
                if asset_id in killed:
                    self.assertEqual((asset.state, asset.end_reason), (AssetState.DESTROYED, AssetEndReason.DESTROYED))
                    self.assertEqual(asset.end_time, killed[asset_id])
                else:
                    self.assertEqual(asset.end_reason, AssetEndReason.ROUTE_COMPLETED)

            if not all_killed:
                # Un superstite arriva all'ultimo punto (200 s, dentro la sessione): COMPLETED.
                self.assertEqual(mission.status, MissionStatus.COMPLETED)

    def test_mission_of_a_block_not_passed_raises(self):
        blue, red, missions = self._scenario()

        with self.assertRaises(ValueError):
            SS.run_session(self._order('S', missions), blue[:1], red, _fire)

    def test_mission_asset_of_another_block_raises(self):
        blue, red, missions = self._scenario()
        stolen = _air_mission('M-stolen', blue[1], missions[1].route, [('bs1', 0.0), ('bn1', 300.0)])

        with self.assertRaises(ValueError):
            SS.run_session(self._order('S', (stolen,)), blue, red, _fire)

    def test_mission_faster_than_its_slowest_asset_raises(self):
        """Regola A (F4a): la missione si muove alla velocita' del suo mezzo piu' lento."""
        blue, red, missions = self._scenario(red_offset=10_000_000.0)
        blue[0].assets['bn2'].speed = {'nominal': 150.0, 'max': 180.0}   # archi a 200 m/s

        with self.assertRaisesRegex(ValueError, "slowest asset 'bn2'"):
            SS.run_session(self._order('S-fast', missions), blue, red, _fire)

    def test_unknown_max_speed_does_not_block(self):
        blue, red, missions = self._scenario(red_offset=10_000_000.0)
        blue[0].assets['bn2'].speed = {'nominal': None, 'max': None}
        outcome = SS.run_session(self._order('S-unknown', missions), blue, red, _fire)
        self.assertEqual(outcome.mission_outcomes['M-north'].status, MissionStatus.COMPLETED)

    def test_missions_do_not_change_the_draws(self):
        """La missione e' ancora solo un contenitore (F3): l'RNG resta per forza, mission_id None."""
        with patch.object(SessionOrder, 'rng', autospec=True, side_effect=SessionOrder.rng) as spy:
            self._run('S-rng')

        self.assertTrue(spy.call_args_list)
        self.assertTrue(all(call.kwargs.get('mission_id') is None for call in spy.call_args_list))


class TestInputs(_Base):

    def test_force_outside_force_ids_raises(self):
        blue, red, _ = self._scenario()
        order = SessionOrder('S', t_start=0.0, t_end=60.0, force_ids=(blue[0].id,))

        with self.assertRaises(ValueError):
            SS.run_session(order, blue, red, _fire)

    def test_same_force_on_both_sides_raises(self):
        blue, _, _ = self._scenario()

        with self.assertRaises(ValueError):
            SS.run_session(self._order(), blue, [blue[0]], _fire)

    def test_bad_arguments_raise(self):
        with self.assertRaises(TypeError):
            SS.run_session('order', [], [], _fire)
        with self.assertRaises(TypeError):
            SS.run_session(self._order(), [], [], 'nope')


class TestMissionAsEngagementUnit(_Base):
    """F4b: la missione e' l'unita' d'ingaggio (vista `MissionForce`), e il suo id entra nell'RNG."""

    def _north_route(self):
        return _route([(0, -20_000), (0, 20_000)], 200.0, 'r-bn1')

    def _split_north(self, blue_north, ids=('M-a', 'M-b')):
        """Blue-North in DUE missioni sulla stessa rotta: bn1 da sola, bn2 a 500 m sulla destra."""
        return (_air_mission(ids[0], blue_north, self._north_route(), [('bn1', 0.0)], target_block='Red-East'),
                _air_mission(ids[1], blue_north, self._north_route(), [('bn2', 500.0)], target_block='Red-East'))

    def test_rng_streams_are_keyed_by_mission_ids(self):
        """Ogni stream d'ingaggio (e di tempra) ha nell'event_id gli id delle MISSIONI; lo slot
        mission_id di Session_Rng resta None (un ingaggio e' fra piu' forze, v. docstring)."""
        original = SessionOrder.rng

        with patch.object(SessionOrder, 'rng', autospec=True, side_effect=original) as spy:
            self._run('S-rng')

        keys = {tuple(json.loads(call.kwargs['event_id'])) for call in spy.call_args_list}
        self.assertEqual(keys, {('engagement', 'M-north', 'Red-East'), ('engagement', 'M-south', 'Red-West'),
                                ('temper', 'M-north', 'Red-East'), ('temper', 'M-south', 'Red-West')})
        self.assertTrue(all(call.kwargs['mission_id'] is None for call in spy.call_args_list))

    def test_renaming_a_mission_changes_its_stream_only(self):
        """Stesse rotte e stessi asset, mission_id diverso: cambia lo stream di quell'ingaggio
        (tempre diverse), non quello dell'altro fronte."""
        first, _, _ = self._run('S-rename')
        blue, red, missions = self._scenario()
        renamed = (_air_mission('M-north-bis', blue[0], self._north_route(), [('bn1', 0.0), ('bn2', 500.0)],
                                target_block='Red-East'), missions[1])
        second = SS.run_session(self._order('S-rename', renamed), blue, red, _fire, reaction_profile_for=_profile)
        temper = lambda outcome, force_id: outcome.outcomes_of(force_id)[0].temper  # noqa: E731
        self.assertNotEqual(temper(first, 'Red-East'), temper(second, 'Red-East'))
        self.assertEqual(temper(first, 'Red-West'), temper(second, 'Red-West'))
        self.assertEqual(first.outcomes_of('M-south'), second.outcomes_of('M-south'))

    def test_two_missions_of_one_block_are_two_forces(self):
        blue, red, missions = self._scenario()
        split = self._split_north(blue[0]) + (missions[1],)
        outcome = SS.run_session(self._order('S-split', split), blue, red, _fire, reaction_profile_for=_profile)
        north = outcome.outcomes_of_block('Blue-North')
        self.assertEqual(sorted(o.force_id for o in north), ['M-a', 'M-b'])
        self.assertTrue(all(o.block_id == 'Blue-North' and o.committed == 1 for o in north))
        self.assertIn(('M-a', 'M-b', 'Red-East'), [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes])

    def test_committed_is_keyed_by_block_and_applied_per_mission(self):
        blue, red, missions = self._scenario()
        order = self._order('S-committed', missions, force_ids=('Blue-North', 'Blue-South', 'Red-East', 'Red-West'),
                            committed={'Blue-North': ('bn1',)})
        outcome = SS.run_session(order, blue, red, _fire, reaction_profile_for=_profile)
        self.assertEqual(outcome.outcomes_of('M-north')[0].committed, 1)
        self.assertEqual(outcome.outcomes_of('M-south')[0].committed, 1)

    def test_unassigned_assets_keep_the_block_identity(self):
        """Asset senza missione nella vista residua con l'id del blocco; un blocco senza missioni
        entra com'e' (la postura continua della F4c non cambia le forze d'ingaggio)."""
        blue, red, _ = self._scenario()
        only_bn1 = (_air_mission('M-a', blue[0], self._north_route(), [('bn1', 0.0)], target_block='Red-East'),)
        order = self._order('S-residual', only_bn1)
        _, _, blocks, block_owner = SS._collect_forces(order, blue, red)
        forces, owner = SS._engagement_forces(order, blocks, block_owner)
        self.assertEqual(sorted(forces), ['Blue-North', 'Blue-South', 'M-a', 'Red-East', 'Red-West'])
        self.assertIsInstance(forces['Blue-North'], MA.MissionForce)
        self.assertIsNone(forces['Blue-North'].mission_id)
        self.assertEqual([a.id for a in forces['Blue-North'].assets.values()], ['bn2'])
        self.assertIs(forces['Blue-South'], blue[1])
        self.assertIs(forces['Red-East'], red[0])
        self.assertEqual((owner['bn1'], owner['bn2'], owner['re1']), ((0, 'M-a'), (0, 'Blue-North'), (1, 'Red-East')))

    # Partenze in volo senza basi: con l'uscita di scena del G4b (`G4_OFF_SCENE_EXIT`) una forza disingaggiata
    # ripercorre la rotta a ritroso (un episodio in piu'); qui si provano i domini di coordinamento.
    @patch.object(SS, 'G4_OFF_SCENE_EXIT', False)
    def test_coordination_domains_are_passed_to_every_engagement(self):
        """Senza Operazioni: ogni missione e' il proprio dominio (blocchi diversi), due run."""
        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as spy:
            self._run('S-domains')

        self.assertEqual(spy.call_count, 2)
        for call in spy.call_args_list:
            self.assertEqual(call.kwargs['coordination_of'],
                             {'M-north': 'M-north', 'M-south': 'M-south', 'Red-East': 'Red-East', 'Red-West': 'Red-West'})

    def test_an_operation_joins_the_fronts_in_one_coordinated_run(self):
        """M-north e M-south (blocchi diversi) nella stessa Operazione: un dominio, quindi una run
        con entrambi i fronti (la condivisione vale dentro la run); i Red restano separati."""
        blue, red, missions = self._scenario()
        order = self._order('S-operation', missions,
                            operations=(Operation('op-strike', 'strike', ('M-north', 'M-south')),))

        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as spy:
            outcome = SS.run_session(order, blue, red, _fire, reaction_profile_for=_profile)

        spy.assert_called_once()
        self.assertEqual(spy.call_args.kwargs['coordination_of'],
                         {'M-north': 'M-north', 'M-south': 'M-north', 'Red-East': 'Red-East', 'Red-West': 'Red-West'})
        self.assertEqual([tuple(o.force_id for o in e) for e in outcome.engagement_outcomes],
                         [('M-north', 'M-south', 'Red-East', 'Red-West')])

    def test_aircraft_without_mission_are_grounded_for_scheduler_and_resolver(self):
        """F4c: bn2 (vista residua di Blue-North) e bs1 (Blue-South, blocco senza missioni) sono a
        terra; l'insieme arriva allo scheduler e a ogni ingaggio. I veicoli Red non lo sono."""
        blue, red, _ = self._scenario()
        only_bn1 = (_air_mission('M-a', blue[0], self._north_route(), [('bn1', 0.0)], target_block='Red-East'),)

        with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler, \
                patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as resolver:
            SS.run_session(self._order('S-grounded', only_bn1), blue, red, _fire, reaction_profile_for=_profile)

        # Dalla F5-B un programma nel tempo (`GroundedSchedule`): gli aerei senza missione sono a
        # terra SEMPRE, nessun altro (le missioni partono in volo).
        expected = CS.GroundedSchedule.of({'bn2', 'bs1'})
        self.assertEqual(scheduler.call_args.kwargs['grounded'], expected)
        self.assertEqual(scheduler.call_args.kwargs['grounded'].always_ids(), frozenset({'bn2', 'bs1'}))
        self.assertTrue(resolver.call_args_list)
        self.assertTrue(all(call.kwargs['grounded'] == expected for call in resolver.call_args_list))

    def test_residual_view_carries_the_continuous_posture(self):
        """Vista residua mista (aereo + veicolo dello stesso blocco): aereo a terra, veicolo in difesa."""
        blue, red, _ = self._scenario()
        blue[0]._assets['bv1'] = _asset(Vehicle, 'bv1', 0, -21_000)
        only_bn1 = (_air_mission('M-a', blue[0], self._north_route(), [('bn1', 0.0)], target_block='Red-East'),)
        order = self._order('S-posture', only_bn1)
        _, _, blocks, block_owner = SS._collect_forces(order, blue, red)
        forces, _ = SS._engagement_forces(order, blocks, block_owner)
        self.assertEqual(forces['Blue-North'].postures, {'bn2': MA.PARKED_POSTURE, 'bv1': MA.GROUND_DEFENSE_POSTURE})
        self.assertEqual(forces['Blue-North'].grounded, frozenset({'bn2'}))
        self.assertEqual(forces['M-a'].postures, {})

    def test_every_aircraft_in_a_mission_means_nobody_is_grounded(self):
        """Senza aerei fuori missione l'insieme e' vuoto: la sessione e' quella di prima della F4c."""
        with patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as resolver:
            self._run('S-nobody-grounded')

        self.assertTrue(all(not call.kwargs['grounded'] for call in resolver.call_args_list))

    def test_mission_id_equal_to_a_block_id_is_rejected(self):
        blue, red, _ = self._scenario()
        clash = (_air_mission('Red-East', blue[0], self._north_route(), [('bn1', 0.0)], target_block='Red-East'),)
        with self.assertRaisesRegex(ValueError, 'also the id of a block'):
            SS.run_session(self._order('S-clash', clash), blue, red, _fire)



# ── PRESENZA E POSTURA NELL'ESITO (F5-B) ──────────────────────────────────────

def _ground_route(points, speed, name):
    """Rotta terrestre di test (archi 'offroad', quota 0)."""
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(x, y, 0), obj_reference=None)
                 for i, (x, y) in enumerate(points)]
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type='offroad', danger_level=0.0, speed=speed,
                                    name=f'{name}-E{i}')
             for i, (a, b) in enumerate(zip(waypoints, waypoints[1:]))}
    return Route(route_type='ground', edges=edges, name=name)


def _ground_mission(mission_id, force, route, asset_id, start_time=0.0, target_block='Red'):
    waypoints = route_waypoints(route)
    roles = [WaypointRole.DEPARTURE] + [WaypointRole.NAV] * (len(waypoints) - 2) + [WaypointRole.OBJECTIVE]
    target = Target(kind=TargetKind.GROUP, target_id=target_block, provenance=TargetProvenance.OBSERVED,
                    observed_at=0.0)
    return Mission(mission_id=mission_id, block_id=force.id, domain='ground', mission_type='Attack',
                   assets=(MissionAsset(asset_id, 'lead'),), target=target, route=route,
                   waypoints=tuple(MissionWaypoint(wp, role) for wp, role in zip(waypoints, roles)),
                   start_time=start_time)


class TestPresenceAndPostures(_Base):
    """F5-B: tratti di presenza a scheduler e risolutore, programma degli aerei a terra, carburante
    sul solo movimento, postura di ogni asset nell'esito (anche dei blocchi senza missioni)."""

    def _scenario(self, start_time=1_000.0, air_start_mode=StartMode.AIR):
        """Blue-Armor: bv1 da (-12 km, 0) a (-4 km, 0) a 10 m/s, partenza `start_time` (800 s di
        movimento); Blue-Air: ba1 in missione (rotta di 40 km a 200 m/s, 200 s) e ba2 senza missione;
        Red: rv1 fermo in (0, 0), nessuna missione."""
        armor = _force('Blue-Armor', 'Blue', [_asset(Vehicle, 'bv1', -12_000, 0, speed=10.0)])
        air = _force('Blue-Air', 'Blue', [_asset(Aircraft, 'ba1', -50_000, 0, speed=200.0),
                                          _asset(Aircraft, 'ba2', -50_000, 500, speed=200.0)])
        red = _force('Red', 'Red', [_asset(Vehicle, 'rv1', 0, 0)])
        air_route = _route([(-50_000, 0), (-10_000, 0)], 200.0, 'r-ba1')
        air_mission = _air_mission('M-air', air, air_route, [('ba1', 0.0)], start_time=start_time)

        if air_start_mode is not StartMode.AIR:
            roles = [WaypointRole.DEPARTURE, WaypointRole.LAND]
            air_mission = Mission(mission_id='M-air', block_id='Blue-Air', domain='air', mission_type='CAS',
                                  assets=air_mission.assets, target=air_mission.target, route=air_route,
                                  waypoints=tuple(MissionWaypoint(wp, role)
                                                  for wp, role in zip(route_waypoints(air_route), roles)),
                                  start_time=start_time, start_mode=air_start_mode)

        missions = (_ground_mission('M-armor', armor, _ground_route([(-12_000, 0), (-4_000, 0)], 10.0, 'r-bv1'),
                                    'bv1', start_time=start_time),
                    air_mission)
        return [armor, air], [red], missions

    def _run(self, session_id='S-presence', **kwargs):
        blue, red, missions = self._scenario(**kwargs)

        with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler, \
                patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as resolver:
            outcome = SS.run_session(self._order(session_id, missions), blue, red, _fire,
                                     reaction_profile_for=_profile)

        return outcome, scheduler, resolver

    def test_ground_unit_is_present_before_departure_and_after_arrival(self):
        _, scheduler, resolver = self._run()
        legs = scheduler.call_args.kwargs['legs']['bv1']
        self.assertEqual((legs[0].t_start, legs[0].t_end, legs[0].p_start, legs[0].p_end),
                         (0.0, 1_000.0, (-12_000.0, 0.0, 0.0), (-12_000.0, 0.0, 0.0)))
        self.assertEqual((legs[-1].t_start, legs[-1].t_end, legs[-1].p_start), (1_800.0, 3_600.0, (-4_000.0, 0.0, 0.0)))
        # Il risolutore riceve gli stessi tratti (istante esatto di rilevamento).
        self.assertTrue(resolver.call_args_list)
        self.assertTrue(all(call.kwargs['legs']['bv1'] == legs for call in resolver.call_args_list))

    def test_air_start_aircraft_is_absent_outside_its_route(self):
        _, scheduler, _ = self._run()
        legs = scheduler.call_args.kwargs['legs']['ba1']
        self.assertEqual((legs[0].t_start, legs[-1].t_end), (1_000.0, 1_200.0))
        self.assertEqual(scheduler.call_args.kwargs['grounded'].intervals('ba1'), ())

    def test_parked_aircraft_is_grounded_until_takeoff(self):
        _, scheduler, resolver = self._run(air_start_mode=StartMode.PARKING_COLD)
        grounded = scheduler.call_args.kwargs['grounded']
        self.assertEqual(grounded.intervals('ba1'), ((float('-inf'), 1_000.0),))
        self.assertTrue(grounded.always('ba2'))
        legs = scheduler.call_args.kwargs['legs']['ba1']
        self.assertEqual((legs[0].t_start, legs[0].t_end), (0.0, 1_000.0))
        self.assertTrue(all(call.kwargs['grounded'] == grounded for call in resolver.call_args_list))

    def test_fuel_is_consumed_on_the_movement_only(self):
        """La presenza ferma non consuma: distanza = la sola rotta, evento a fine movimento."""
        outcome, _, _ = self._run()
        fuel = {event.asset_id: event for event in outcome.fuel_events}
        self.assertAlmostEqual(fuel['bv1'].distance, 8_000.0)
        self.assertAlmostEqual(fuel['bv1'].time, 1_800.0)
        self.assertAlmostEqual(fuel['ba1'].distance, 40_000.0)

    def test_postures_of_every_asset_in_the_outcome(self):
        """Il carro `bv1` e' distrutto in questa sessione: postura `destroyed` (F6-B1); con
        `F6_DESTROYED_POSTURE` spento la postura di piano della F5-B (`Defense` a movimento finito)."""
        outcome, _, _ = self._run()
        self.assertTrue(any(event.destroyed and event.target_id == 'bv1' for event in outcome.damage_events))
        self.assertEqual(dict(outcome.postures), {'ba1': MA.OFF_SCENE_POSTURE, 'ba2': MA.PARKED_POSTURE,
                                                  'bv1': MA.DESTROYED_POSTURE,
                                                  'rv1': MA.GROUND_DEFENSE_POSTURE})

        with patch.object(SS, 'F6_DESTROYED_POSTURE', False):
            outcome, _, _ = self._run()

        self.assertEqual(dict(outcome.postures), {'ba1': MA.OFF_SCENE_POSTURE, 'ba2': MA.PARKED_POSTURE,
                                                  'bv1': MA.GROUND_DEFENSE_POSTURE,
                                                  'rv1': MA.GROUND_DEFENSE_POSTURE})

    def test_postures_while_moving_and_before_takeoff(self):
        """Partenza a 3500 s: a fine sessione il carro e' in movimento (postura del tipo di missione)
        e l'aereo in volo (il tipo di missione). Partenza a 4000 s, oltre la fine: carro non ancora
        partito (`Defense`, D1.b), aereo dal parcheggio ancora a terra."""
        moving, _, _ = self._run(start_time=3_500.0, air_start_mode=StartMode.PARKING_HOT)
        self.assertEqual((moving.postures['bv1'], moving.postures['ba1']), ('Attack', 'CAS'))
        waiting, _, _ = self._run(start_time=4_000.0, air_start_mode=StartMode.PARKING_HOT)
        self.assertEqual((waiting.postures['bv1'], waiting.postures['ba1']),
                         (MA.GROUND_DEFENSE_POSTURE, MA.PARKED_POSTURE))

    def test_without_presence_the_legs_are_the_route_legs(self):
        """Interruttore spento: tratti della sola rotta, nessun intervallo a terra di missione (la
        sessione della F5-A); la postura e' riportata comunque."""
        with patch.object(MA, 'F5_PRESENCE', False):
            outcome, scheduler, _ = self._run(air_start_mode=StartMode.PARKING_COLD)

        legs = scheduler.call_args.kwargs['legs']['bv1']
        self.assertEqual((legs[0].t_start, legs[-1].t_end), (1_000.0, 1_800.0))
        self.assertEqual(scheduler.call_args.kwargs['grounded'].ids(), frozenset({'ba2'}))
        self.assertTrue(outcome.postures)


    def _with_base(self, side):
        """Lo scenario con una base aerea vera (Military 'Airbase', un veicolo a 500 m dalla fine
        della rotta di ba1) del lato `side`."""
        blue, red, missions = self._scenario()
        base = Military(mil_category=MILITARY_CATEGORY['Air_Base'][0], name=f'{side}-Base', side=side)
        base.id = f'{side}-Base'
        base._assets = {'bb1': _asset(Vehicle, 'bb1', -10_000, 500)}
        (blue if side == 'Blue' else red).append(base)
        return blue, red, missions

    def test_landing_in_the_area_of_an_own_air_base(self):
        """F5-B: l'ultimo LAND di ba1 senza riferimento ma nell'area di una base Blue -> a terra
        dall'arrivo; la base del NEMICO non conta."""
        for side, grounded_after in (('Blue', True), ('Red', False)):
            blue, red, missions = self._with_base(side)

            with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
                outcome = SS.run_session(self._order(f'S-area-{side}', missions), blue, red, _fire,
                                         reaction_profile_for=_profile)

            intervals = scheduler.call_args.kwargs['grounded'].intervals('ba1')
            self.assertEqual(intervals == ((1_200.0, float('inf')),), grounded_after, side)
            self.assertEqual(outcome.postures['ba1'], MA.PARKED_POSTURE if grounded_after else MA.OFF_SCENE_POSTURE)


# ── ATTESE, ETA BLOCCATE E TOT (F5-C) ─────────────────────────────────────────

def _wait_action(duration, mode='hold'):
    return MissionAction(kind=ActionKind.WAIT, name=f'Wait_{mode}', wait_mode=mode, wait_duration_s=duration)


def _with_actions(mission, actions, **overrides):
    """Copia della missione con le azioni `{indice: [MissionAction]}` sui punti."""
    waypoints = tuple(dataclasses.replace(mw, actions=tuple(actions.get(index, ())))
                      for index, mw in enumerate(mission.waypoints))
    return dataclasses.replace(mission, waypoints=waypoints, **overrides)


def _strike_mission(mission_id, force, asset_id, x0, y0, start_time=0.0, tot=None, operation_id=None):
    """Missione aerea da (x0, y0) a (x0, 0) ATTACK e (x0, 20 km) LAND, a 200 m/s."""
    route = _route([(x0, y0), (x0, 0), (x0, 20_000)], 200.0, f'r-{asset_id}')
    roles = [WaypointRole.NAV, WaypointRole.ATTACK, WaypointRole.LAND]
    target = Target(kind=TargetKind.GROUP, target_id='Red', provenance=TargetProvenance.OBSERVED, observed_at=0.0)
    return Mission(mission_id=mission_id, block_id=force.id, domain='air', mission_type='CAS',
                   assets=(MissionAsset(asset_id, 'lead'),), target=target, route=route,
                   waypoints=tuple(MissionWaypoint(wp, role) for wp, role in zip(route_waypoints(route), roles)),
                   start_time=start_time, tot=tot, start_mode=StartMode.AIR, operation_id=operation_id)


class TestWaitsAndEtas(_Base):
    """F5-C: attese WAIT, TOT per missione ed ETA effettive cablati in sessione."""

    def _hold_run(self, session_id='S-hold'):
        armor = _force('Blue-Armor', 'Blue', [_asset(Vehicle, 'bv1', -12_000, 0, speed=10.0)])
        red = _force('Red', 'Red', [_asset(Vehicle, 'rv1', 0, 0)])
        route = _ground_route([(-12_000, 0), (-4_000, 0), (-4_000, -8_000)], 10.0, 'r-bv1')
        mission = _with_actions(_ground_mission('M-armor', armor, route, 'bv1'), {1: [_wait_action(600.0)]})

        with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler, \
                patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as resolver:
            outcome = SS.run_session(self._order(session_id, (mission,)), [armor], [red], _fire,
                                     reaction_profile_for=_profile)

        return outcome, scheduler, resolver

    def test_a_hold_is_a_static_leg_for_scheduler_and_resolver(self):
        outcome, scheduler, resolver = self._hold_run()
        legs = scheduler.call_args.kwargs['legs']['bv1']
        hold = [(leg.t_start, leg.t_end, leg.p_start) for leg in legs
                if leg.p_start == leg.p_end and leg.p_start == (-4_000.0, 0.0, 0.0) and leg.t_end < 3_600.0]
        self.assertEqual(hold, [(800.0, 1_400.0, (-4_000.0, 0.0, 0.0))])
        self.assertTrue(resolver.call_args_list)
        self.assertTrue(all(call.kwargs['legs']['bv1'] == legs for call in resolver.call_args_list))

    def test_actual_etas_include_the_hold(self):
        outcome, _, _ = self._hold_run()
        self.assertEqual(outcome.mission_outcomes['M-armor'].actual_etas, (0.0, 800.0, 2_200.0))

    def test_the_hold_consumes_fuel_per_leg(self):
        """F6-A: un FuelEvent per tratto (8 km, sosta di 600 s, 8 km); la sosta consuma nel tempo alla
        crociera (10 m/s -> 6 km equivalenti), autonomia di test 1000 km."""
        outcome, _, _ = self._hold_run()
        events = [event for event in outcome.fuel_events if event.asset_id == 'bv1']
        self.assertEqual([(e.t_start, e.time, e.distance, e.stationary) for e in events],
                         [(0.0, 800.0, 8_000.0, False), (800.0, 1_400.0, 0.0, True), (1_400.0, 2_200.0, 8_000.0, False)])
        self.assertAlmostEqual(events[1].amount, 6_000.0 / AUTONOMY['nominal'])
        self.assertEqual(events[1].regime, SS.CRUISE_REGIME)

        # I tratti di movimento al regime della sessione (bv1 e' ingaggiato da rv1: 'max').
        for event in (events[0], events[2]):
            self.assertAlmostEqual(event.amount, 8_000.0 / AUTONOMY[event.regime])

    def test_without_per_leg_fuel_the_hold_does_not_consume(self):
        """Interruttore `F6_FUEL_PER_LEG` spento: un solo evento sulla distanza della rotta, alla fine del
        movimento (sosta compresa), come la F5-C."""
        with patch.object(SS, 'F6_FUEL_PER_LEG', False):
            outcome, _, _ = self._hold_run()

        fuel = {event.asset_id: event for event in outcome.fuel_events}
        self.assertAlmostEqual(fuel['bv1'].distance, 16_000.0)
        self.assertAlmostEqual(fuel['bv1'].time, 2_200.0)

    def test_without_waits_the_hold_is_ignored(self):
        with patch.object(MA, 'F5_WAITS', False):
            outcome, _, _ = self._hold_run()

        self.assertEqual(outcome.mission_outcomes['M-armor'].actual_etas, (0.0, 800.0, 1_600.0))

    def _tot_run(self, near_tot=780.0, far_tot=900.0):
        """M-near (bn1, 20 km dall'ATTACK) e M-far (bs1, 40 km) partono a 0 nell'Operazione 'Op'
        (senza TOT comune), ciascuna con il PROPRIO TOT: M-near anticipa M-far di 120 s."""
        blue = _force('Blue', 'Blue', [_asset(Aircraft, 'bn1', 0, -20_000, speed=200.0),
                                       _asset(Aircraft, 'bs2', 100_000, -40_000, speed=200.0)])
        red = _force('Red', 'Red', [_asset(Vehicle, 'rv1', 50_000, 0)])
        missions = (_strike_mission('M-near', blue, 'bn1', 0, -20_000, tot=near_tot, operation_id='Op'),
                    _strike_mission('M-far', blue, 'bs2', 100_000, -40_000, tot=far_tot, operation_id='Op'))
        order = self._order('S-tot', missions, operations=(Operation('Op', 'strike', ('M-near', 'M-far')),))
        return SS.run_session(order, [blue], [red], _fire, reaction_profile_for=_profile)

    def test_missions_of_one_operation_reach_each_its_own_tot(self):
        """Il TOT e' di ogni missione (decisione dell'utente del 2026-10-12): partenza a 0 per
        entrambe, ciascuna attende al punto di partenza quanto basta per essere sul proprio ATTACK al
        PROPRIO TOT (680 s e 700 s di attesa, 100 s e 200 s di volo)."""
        outcome = self._tot_run()
        self.assertEqual(outcome.mission_outcomes['M-near'].actual_etas, (0.0, 780.0, 880.0))
        self.assertEqual(outcome.mission_outcomes['M-far'].actual_etas, (0.0, 900.0, 1_000.0))

    def test_a_mission_without_tot_does_not_inherit_one(self):
        """Nessun TOT d'Operazione: la missione senza TOT non attende."""
        outcome = self._tot_run(near_tot=None)
        self.assertEqual(outcome.mission_outcomes['M-near'].actual_etas, (0.0, 100.0, 200.0))
        self.assertEqual(outcome.mission_outcomes['M-far'].actual_etas, (0.0, 900.0, 1_000.0))

    def test_without_waits_the_tots_are_not_waited(self):
        with patch.object(MA, 'F5_WAITS', False):
            outcome = self._tot_run()

        self.assertEqual(outcome.mission_outcomes['M-near'].actual_etas, (0.0, 100.0, 200.0))
        self.assertEqual(outcome.mission_outcomes['M-far'].actual_etas, (0.0, 200.0, 300.0))


# ── FINE DI ATTIVITA' E STATO DI MISSIONE (F6-B1) ─────────────────────────────

def _with_criteria(mission, **criteria):
    """Copia della missione con i criteri di fine dichiarati."""
    return dataclasses.replace(mission, end_criteria=EndCriteria(**criteria))


KILL = ER.ShotSpec(accuracy=1.0, destroy_capacity=1.0, rounds=1, time_of_flight=1.0)


def _blue_only(spec):
    """Fire control: spara solo Blue (i veicoli rossi non rispondono), sempre `spec`."""
    return lambda shooter, target: spec if shooter.id.startswith('b') else None


class TestEndCriteria(_Base):
    """F6-B1: i criteri dichiarati in `EndCriteria` chiudono l'attivita' (senza cambio di rotta) e lo
    stato di missione segue la regola unica DESTROYED > COMPLETED > ABORTED(motivo) > FAILED."""

    FIGHT_ON = {'Blue': {'erosion': 1.0, 'shock': 1.0}, 'Red': {'erosion': 1.0, 'shock': 1.0}}

    def _north(self, fire, session_id='S-end', stores=None, **criteria):
        blue, red, missions = self._scenario()
        north, south = missions
        missions = (_with_criteria(north, **criteria) if criteria else north, south)

        if stores is not None:
            for asset in blue[0].assets.values():
                asset.stores = dict(stores)

        # Nessun disingaggio (erosione e shock a 1): Red-East subisce fino all'ultimo veicolo.
        outcome = SS.run_session(self._order(session_id, missions), blue, red, fire,
                                 reaction_profile_for=_profile, thresholds=self.FIGHT_ON)
        return outcome, blue, red

    def _launches(self, outcome, prefix='bn'):
        return [event.time for event in outcome.ammunition_events if event.asset_id.startswith(prefix)]

    def test_default_criteria_read_nothing(self):
        """Nei default nessun criterio di stato e' attivo: nessun piano, la sessione e' quella di prima."""
        blue, red, missions = self._scenario()
        movement_of = {m.asset_id: m for mission in missions for m in MA.mission_movements(mission)}
        assets = {a.id: a for force in blue + red for a in force.assets.values()}
        blocks = {force.id: force for force in blue + red}
        mission_of = {mission.mission_id: mission for mission in missions}
        self.assertEqual(SS._activity_plans(self._order(missions=missions), movement_of, mission_of, assets, blocks), {})

    def test_target_destroyed_completes_the_mission(self):
        """Red-East (2 veicoli) e' il bersaglio di M-north: distrutti entrambi, la missione e'
        COMPLETED, gli asset chiudono TARGET_DESTROYED all'istante dell'ultima distruzione e non
        lanciano piu'; con il criterio spento la rotta completata (200 s)."""
        outcome, _, _ = self._north(_blue_only(KILL), target_destroyed=True)
        mission = outcome.mission_outcomes['M-north']
        last = max(e.time for e in outcome.damage_events if e.destroyed and e.target_id in ('re1', 're2'))
        self.assertEqual(mission.status, MissionStatus.COMPLETED)

        for asset_id in ('bn1', 'bn2'):
            self.assertEqual((mission.asset_outcomes[asset_id].end_reason, mission.asset_outcomes[asset_id].end_time),
                             (AssetEndReason.TARGET_DESTROYED, last))

        self.assertTrue(all(t <= last for t in self._launches(outcome)))

        with patch.object(SS, 'F6_END_CRITERIA', False):
            off, _, _ = self._north(_blue_only(KILL), target_destroyed=True)

        self.assertEqual(off.mission_outcomes['M-north'].asset_outcomes['bn1'].end_reason, AssetEndReason.ROUTE_COMPLETED)

    def test_route_completed_without_the_declared_target_is_failed(self):
        """Con `target_destroyed` dichiarato la sola rotta completata non e' l'obiettivo: FAILED."""
        outcome, _, _ = self._north(lambda s, t: None, target_destroyed=True)
        mission = outcome.mission_outcomes['M-north']
        self.assertEqual(mission.status, MissionStatus.FAILED)
        self.assertEqual(mission.asset_outcomes['bn1'].end_reason, AssetEndReason.ROUTE_COMPLETED)

    def test_max_duration_ends_the_activity(self):
        """Durata di 10 s dalla partenza: il contatto con Red-East comincia dopo, nessun lancio; motivo
        MAX_DURATION a 10 s, fine regolare (COMPLETED). Senza criterio Blue spara."""
        outcome, _, _ = self._north(_blue_only(SPEC), max_duration_s=10.0)
        mission = outcome.mission_outcomes['M-north']
        self.assertEqual(self._launches(outcome), [])
        self.assertEqual(mission.status, MissionStatus.COMPLETED)
        self.assertEqual((mission.asset_outcomes['bn1'].end_reason, mission.asset_outcomes['bn1'].end_time),
                         (AssetEndReason.MAX_DURATION, 10.0))
        free, _, _ = self._north(_blue_only(SPEC))
        self.assertTrue(self._launches(free))

    def test_winchester_aborts_for_ammunition(self):
        """Un AGM-65D a testa e il cannone: con winchester su 'MISSILES_ASM' una salva per asset, poi
        passivi; missione ABORTED per munizioni. Senza criterio il cannone continua."""
        options = (ER.ShotSpec(accuracy=0.0, destroy_capacity=1.0, weapon='AGM-65D', time_of_flight=1.0),
                   ER.ShotSpec(accuracy=0.0, destroy_capacity=1.0, weapon='M61A1', stock_per_round=50))
        stores = {'AGM-65D': 1, 'M61A1': 500}
        outcome, _, _ = self._north(_blue_only(options), stores=stores, winchester=('MISSILES_ASM',))
        mission = outcome.mission_outcomes['M-north']
        self.assertEqual(len(self._launches(outcome)), 2)
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.AMMUNITION))
        self.assertEqual({o.end_reason for o in mission.asset_outcomes.values()}, {AssetEndReason.WINCHESTER})
        free, _, _ = self._north(_blue_only(options), stores=stores)
        self.assertGreater(len(self._launches(free)), 2)

    def test_winchester_weapons_by_registry_category(self):
        """Categoria = chiave del registro d'arma del dominio; un'arma della categoria non modellata, o
        nessuna, disattiva il criterio."""
        asset = _asset(Aircraft, 'x1', 0, 0)
        asset.stores = {'AIM-9M': 2, 'AGM-65D': 2, 'M61A1': 500}
        self.assertEqual(SS._winchester_weapons(asset, 'x1', 'air', ('MISSILES_AAM',)), frozenset({'AIM-9M'}))
        self.assertEqual(SS._winchester_weapons(asset, 'x1', 'air', ('MISSILES_AAM', 'CANNONS')),
                         frozenset({'AIM-9M', 'M61A1'}))
        self.assertEqual(SS._winchester_weapons(asset, 'x1', 'air', ('BOMBS',)), frozenset())
        asset._unmodelled_weapons = frozenset({'M61A1'})
        self.assertEqual(SS._winchester_weapons(asset, 'x1', 'air', ('CANNONS',)), frozenset())

    def test_target_ids_by_target_kind(self):
        blue, red, missions = self._scenario()
        blocks = {force.id: force for force in blue + red}
        mission_of = {mission.mission_id: mission for mission in missions}
        assets = {a.id: a for force in blue + red for a in force.assets.values()}
        north = missions[0]
        self.assertEqual(SS._mission_target_ids(north, blocks, mission_of, assets), frozenset({'re1', 're2'}))
        by_mission = dataclasses.replace(north, target=Target(kind=TargetKind.GROUP, target_id='M-south',
                                                              provenance=TargetProvenance.OBSERVED, observed_at=0.0))
        self.assertEqual(SS._mission_target_ids(by_mission, blocks, mission_of, assets), frozenset({'bs1'}))
        single = dataclasses.replace(north, target=Target(kind=TargetKind.ASSET, target_id='rw1',
                                                          provenance=TargetProvenance.OBSERVED, observed_at=0.0))
        self.assertEqual(SS._mission_target_ids(single, blocks, mission_of, assets), frozenset({'rw1'}))
        point = dataclasses.replace(north, target=Target(kind=TargetKind.POINT, position=Point3D(0, 0, 0)))
        self.assertEqual(SS._mission_target_ids(point, blocks, mission_of, assets), frozenset())
        unknown = dataclasses.replace(north, target=Target(kind=TargetKind.ASSET, target_id='nobody',
                                                           provenance=TargetProvenance.OBSERVED, observed_at=0.0))
        self.assertEqual(SS._mission_target_ids(unknown, blocks, mission_of, assets), frozenset())


# ── F6-B2: BINGO IN VOLO CON RIENTRO (rientro a ritroso dalla F6-B2bis) ──────

def _route3d(points, speed, name):
    """Rotta aerea di test su punti (x, y, z) espliciti (quote diverse per punto)."""
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(*point), obj_reference=None)
                 for i, point in enumerate(points)]
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0, speed=speed,
                                    name=f'{name}-E{i}')
             for i, (a, b) in enumerate(zip(waypoints, waypoints[1:]))}
    return Route(route_type='air', edges=edges, name=name)


class TestBingo(_Base):
    """F6-B2bis: al bingo l'aereo rientra lungo la rotta a ritroso (partito in volo: fino al punto di comparsa,
    poi diretto alla base del lato piu' vicina) con il fabbisogno `Fuel_Model.BINGO_RETURN_FACTOR` x il
    ritorno (autonomia di test 1000 km alla crociera: 0,1 del pieno = 100 km). Con
    `F6_BINGO_REVERSE_ROUTE` spento il rientro rettilineo con la riserva della F6-B2. Dal G2 la classe gira con
    `F6_BINGO_DISENGAGE_RESERVE` SPENTO: le regole precedenti restano invariate (v. `TestReserveBingo`)."""

    def setUp(self):
        super().setUp()
        switch = patch.object(SS, 'F6_BINGO_DISENGAGE_RESERVE', False)
        switch.start()
        self._patches.append(switch)

    def _flight(self, fuel=0.2, base=(0.0, 0.0), length=150_000.0, bingo=True, start=(0.0, 0.0), z=0.0, red=None):
        """b1 a 200 m/s da `start` verso nord per `length` metri; base aerea Blue in `base` (None = nessuna);
        `red`: posizione (x, y) di un veicolo Red fermo."""
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', *start, z=z, fuel=fuel, speed=200.0)])]

        if base is not None:
            blue.append(self._airbase(base))

        reds = [_force('Red', 'Red', [_asset(Vehicle, 'r1', *red)])] if red is not None else []
        route = _route([start, (start[0], start[1] + length)], 200.0, 'r-b1', z=z)
        mission = _air_mission('M-b1', blue[0], route, [('b1', 0.0)])

        if not bingo:
            mission = dataclasses.replace(mission, end_criteria=EndCriteria(bingo=False))

        return self._execute(mission, blue, reds)

    def _airbase(self, base):
        airbase = Military(mil_category=MILITARY_CATEGORY['Air_Base'][0], name='Blue-Base', side='Blue')
        airbase.id = 'Blue-Base'
        airbase._assets = {'bb1': _asset(Vehicle, 'bb1', *base)}
        return airbase

    def _execute(self, mission, blue, reds=()):
        with patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler, \
                patch.object(ER, 'resolve_engagement', wraps=ER.resolve_engagement) as resolver:
            outcome = SS.run_session(self._order(missions=(mission,)), blue, list(reds), _fire,
                                     reaction_profile_for=_profile)

        return outcome, blue[0].assets['b1'], scheduler.call_args.kwargs, resolver

    def _bingo_distance(self, fuel):
        """Partenza in volo sulla base (ritorno = metri percorsi): F - u = f u -> u = F / (1 + f) [m]."""
        return fuel * AUTONOMY['nominal'] / (1.0 + FM.BINGO_RETURN_FACTOR)

    def test_bingo_returns_along_the_route_to_the_own_base(self):
        """0,2 del pieno (200 km), partenza in volo sulla base: bingo a u = 200 / 2,2 km (~90,9 km, ~454,5 s),
        ritroso fino al punto di comparsa (che e' sulla base), a terra dall'atterraggio; a bordo resta il 20%
        del carburante del ritorno; BINGO, ABORTED(BINGO), postura a terra."""
        outcome, b1, scheduler, _ = self._flight()
        u = self._bingo_distance(0.2)
        legs = scheduler['legs']['b1']
        expected = [(0.0, u / 200.0), (u / 200.0, 2 * u / 200.0), (2 * u / 200.0, 3_600.0)]
        self.assertEqual(len(legs), len(expected))

        for leg, (t_start, t_end) in zip(legs, expected):
            self.assertAlmostEqual(leg.t_start, t_start, delta=1e-6)
            self.assertAlmostEqual(leg.t_end, t_end, delta=1e-6)

        self.assertAlmostEqual(legs[1].p_start[1], u, delta=1e-6)
        self.assertEqual(legs[1].p_end, (0.0, 0.0, 0.0))
        self.assertTrue(scheduler['grounded'].at('b1', 2 * u / 200.0 + 1.0))
        self.assertFalse(scheduler['grounded'].at('b1', 2 * u / 200.0 - 1.0))
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
        asset = mission.asset_outcomes['b1']
        self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.BINGO))
        self.assertAlmostEqual(asset.end_time, u / 200.0, delta=1e-6)
        self.assertEqual(mission.actual_etas, (0.0, None))
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)
        self.assertAlmostEqual(b1.fuel, (FM.BINGO_RETURN_FACTOR - 1.0) * u / AUTONOMY['nominal'], delta=1e-9)
        self.assertEqual(len(outcome.fuel_events), 2)

    def test_reverse_route_switch_off_is_the_straight_return_with_the_reserve(self):
        """`F6_BINGO_REVERSE_ROUTE` spento: la F6-B2 com'era (100 - u = u -> bingo a 50 km, 250 s; rientro di
        250 s; a terra con la riserva 0,1)."""
        with patch.object(SS, 'F6_BINGO_REVERSE_ROUTE', False):
            outcome, b1, scheduler, _ = self._flight()

        legs = scheduler['legs']['b1']
        self.assertEqual([(round(leg.t_start, 6), round(leg.t_end, 6)) for leg in legs],
                         [(0.0, 250.0), (250.0, 500.0), (500.0, 3_600.0)])
        self.assertEqual(outcome.mission_outcomes['M-b1'].reason, AbortReason.BINGO)
        self.assertAlmostEqual(b1.fuel, FM.BINGO_RESERVE)

    def test_switch_off_flies_the_route(self):
        """`F6_BINGO` spento: il comportamento di prima, rotta completata (150 km con 200 km di carburante)."""
        with patch.object(SS, 'F6_BINGO', False):
            outcome, b1, scheduler, _ = self._flight()

        self.assertAlmostEqual(scheduler['legs']['b1'][-1].t_end, 750.0)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)
        self.assertAlmostEqual(b1.fuel, 0.05)

    def test_no_bingo_without_an_own_base_or_when_declared_off(self):
        """Partenza in volo senza base del lato, o `EndCriteria.bingo` False: nessun rientro (la rotta basta:
        COMPLETED)."""
        for kwargs in ({'base': None}, {'bingo': False}):
            outcome, _, scheduler, _ = self._flight(**kwargs)
            self.assertAlmostEqual(scheduler['legs']['b1'][-1].t_end, 750.0, msg=kwargs)
            self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED, kwargs)

    def test_enough_fuel_no_bingo(self):
        outcome, _, _, _ = self._flight(fuel=1.0)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)

    def test_after_bingo_no_offensive_salvo(self):
        """Dal bingo l'aereo non lancia piu': il risolutore riceve la fine di attivita' nota a monte (`until`
        all'istante del bingo); il veicolo Red sulla rotta e' sorvolato prima del bingo (a 20 km, 100 s)."""
        outcome, _, _, resolver = self._flight(red=(0.0, 20_000.0))
        t_bingo = self._bingo_distance(0.2) / 200.0
        criteria = resolver.call_args.kwargs['activity_criteria']
        self.assertAlmostEqual(criteria['b1'].until, t_bingo, delta=1e-6)
        self.assertTrue(all(salvo.time <= t_bingo for salvo in outcome.ammunition_events if salvo.asset_id == 'b1'))

    def test_dry_on_the_return_follows_the_fuel_rules(self):
        """Carburante 0,05 a 100 km dalla base: bingo alla partenza (il tratto diretto alla base costa gia'
        1,2 x 100 km), rientro verso la base, a secco dopo 50 km (250 s, a meta' discesa: ~500 m, planata
        5 km), base fuori portata: perso, DESTROYED/FUEL_EXHAUSTED."""
        outcome, b1, scheduler, _ = self._flight(fuel=0.05, base=(0.0, -100_000.0), z=1_000.0)
        legs = scheduler['legs']['b1']
        self.assertAlmostEqual(legs[-1].t_end, 50_000.0 / 200.0, delta=1.0)
        self.assertTrue(b1.is_destroyed())
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual(mission.status, MissionStatus.DESTROYED)
        self.assertEqual(mission.asset_outcomes['b1'].end_reason, AssetEndReason.FUEL_EXHAUSTED)

    def test_from_a_base_the_route_is_retraced_to_the_departure(self):
        """Partenza da pista (RUNWAY) in W0 (0, 0, 0), salita a W1 (0, 50 km, 5000), sosta di 300 s in W1,
        W2 (50 km, 50 km, 5000), LAND lontano in W3 (50 km, 150 km, 0) su un'altra base (non conta: divert
        escluso). Carburante 0,35 (350 km; la sosta ne consuma 60 alla crociera): bingo nel tratto W2-W3 (a
        ~31,6 km da W2: 350 - 50,2 - 60 - 50 - u = 1,2 (100,2 + u)), il rientro ripercorre W2, W1 e
        finisce sul DEPARTURE W0 (discesa solo sull'ultimo tratto), la sosta NON e' ripercorsa; a terra
        sul DEPARTURE fino a fine sessione. Nessuna base del lato fra le forze: partendo da una base non
        serve (il rientro finisce sul DEPARTURE)."""
        points = [(0.0, 0.0, 0.0), (0.0, 50_000.0, 5_000.0), (50_000.0, 50_000.0, 5_000.0), (50_000.0, 150_000.0, 0.0)]
        route = _route3d(points, 200.0, 'r-dep')
        roles = [WaypointRole.DEPARTURE, WaypointRole.NAV, WaypointRole.NAV, WaypointRole.LAND]
        hold = MissionAction(ActionKind.WAIT, 'Wait', wait_mode='hold', wait_duration_s=300.0)
        waypoints = tuple(MissionWaypoint(wp, role, actions=(hold,) if index == 1 else ())
                          for index, (wp, role) in enumerate(zip(route_waypoints(route), roles)))
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0.0, 0.0, fuel=0.35, speed=200.0)])]
        target = Target(kind=TargetKind.GROUP, target_id='Red', provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        mission = Mission(mission_id='M-b1', block_id='Blue', domain='air', mission_type='CAS', target=target,
                          assets=(MissionAsset('b1', 'lead'),), route=route, waypoints=waypoints,
                          start_time=0.0, start_mode=StartMode.RUNWAY)
        # Lo stesso criterio a priori: il validatore rifiuta la missione con l'istante di bingo eseguito sotto.
        movement, = MA.mission_movements(mission)
        planned = FM.bingo_point(blue[0].assets['b1'], MA.airborne_legs(movement), (),
                                 rule=MA.bingo_return_rule(mission))

        with self.assertRaisesRegex(ValueError, f't={planned.time:.1f} s'):
            MA.check_mission_bingo(mission, blue[0].assets, (), disengage_reserve=False)

        outcome, _, scheduler, _ = self._execute(mission, blue)
        self.assertAlmostEqual(outcome.mission_outcomes['M-b1'].asset_outcomes['b1'].end_time, planned.time, delta=1e-6)
        legs = scheduler['legs']['b1']
        moving = [leg for leg in legs if leg.p_start != leg.p_end]
        bingo = moving[2].p_end
        self.assertEqual(moving[2].p_start, points[2])
        for got, want in zip(moving[3].p_start, bingo):
            self.assertAlmostEqual(got, want, delta=1e-6)

        self.assertEqual([leg.p_end for leg in moving[3:]], [points[2], points[1], points[0]])
        self.assertEqual(sum(1 for leg in legs if leg.p_start == leg.p_end and leg.p_start == points[1]), 1)
        parked = legs[-1]
        self.assertEqual((parked.p_start, parked.p_end, parked.t_end), (points[0], points[0], 3_600.0))
        self.assertTrue(scheduler['grounded'].at('b1', parked.t_start + 1.0))
        self.assertEqual(outcome.mission_outcomes['M-b1'].reason, AbortReason.BINGO)
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)


# ── G2: SOGLIA DI BINGO CON LA RISERVA DI DISIMPEGNO E ALBERO DI DECISIONE ─────

class TestReserveBingo(_Base):
    """G2 (`F6_BINGO_DISENGAGE_RESERVE`, attivo): bingo se il carburante e' sotto la rotta intera + la riserva di
    disimpegno, valutato all'inizio dei tratti; albero per tipo di missione. Aereo di test: autonomia 1000 km
    alla crociera (0,1 del pieno = 100 km), riserva di ripiego = 200 m/s x 300 s al regime 'max' (autonomia
    500 km) = 0,12 del pieno. Rotta di 150 km = 0,15: soglia 0,27; con 0,2 l'aereo e' sotto la soglia ma ha
    carburante per la rotta."""

    _execute = TestBingo._execute

    def _airbase(self, base, name='Blue-Base'):
        airbase = Military(mil_category=MILITARY_CATEGORY['Air_Base'][0], name=name, side='Blue')
        airbase.id = name
        airbase._assets = {f'{name}/a': _asset(Vehicle, f'{name}/a', *base)}
        return airbase

    def _air(self, fuel=0.2, bases=((0.0, -10_000.0),), mission_type='CAS', bingo=True, z=1_000.0):
        """b1 in volo da (0, 0, z) verso nord per 150 km a 200 m/s; basi aeree Blue nelle posizioni `bases`."""
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0.0, 0.0, z=z, fuel=fuel, speed=200.0)])]
        blue += [self._airbase(base, f'Blue-Base-{index}') for index, base in enumerate(bases)]
        mission = _air_mission('M-b1', blue[0], _route([(0.0, 0.0), (0.0, 150_000.0)], 200.0, 'r-b1', z=z),
                               [('b1', 0.0)])
        mission = dataclasses.replace(mission, mission_type=mission_type, end_criteria=EndCriteria(bingo=bingo))
        return mission, blue

    def test_the_rule_is_active_by_default(self):
        self.assertTrue(SS.F6_BINGO_DISENGAGE_RESERVE)

    def test_combat_from_a_base_under_the_threshold_stays_on_the_ground(self):
        """Partenza da pista alle 100 s, rotta di ~150 km fino a un'altra base, carburante 0,2 < 0,15 + 0,12: bingo
        alla partenza (istante calcolato, = partenza), ritroso di lunghezza zero: resta a terra sul DEPARTURE per
        tutta la sessione, nessun FuelEvent, BINGO e ABORTED(BINGO); il validatore la rifiuta con lo stesso
        istante."""
        points = [(0.0, 0.0, 0.0), (0.0, 50_000.0, 5_000.0), (0.0, 150_000.0, 0.0)]
        route = _route3d(points, 200.0, 'r-dep')
        roles = [WaypointRole.DEPARTURE, WaypointRole.NAV, WaypointRole.LAND]
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0.0, 0.0, fuel=0.2, speed=200.0)])]
        target = Target(kind=TargetKind.GROUP, target_id='Red', provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        mission = Mission(mission_id='M-b1', block_id='Blue', domain='air', mission_type='CAS', target=target,
                          assets=(MissionAsset('b1', 'lead'),), route=route,
                          waypoints=tuple(MissionWaypoint(wp, role) for wp, role in zip(route_waypoints(route), roles)),
                          start_time=100.0, start_mode=StartMode.RUNWAY)
        movement, = MA.mission_movements(mission)
        decision = MA.mission_bingo_decision(mission, movement, blue[0].assets['b1'], ())
        self.assertEqual((decision.action, decision.return_length), (FM.BINGO_DEPARTURE, 0.0))

        with self.assertRaisesRegex(ValueError, f't={decision.time:.1f} s'):
            MA.check_mission_bingo(mission, blue[0].assets, ())

        outcome, b1, scheduler, _ = self._execute(mission, blue)
        legs = scheduler['legs']['b1']
        self.assertTrue(all(leg.p_start == leg.p_end == points[0] for leg in legs))
        self.assertAlmostEqual(legs[-1].t_end, 3_600.0)
        self.assertTrue(all(scheduler['grounded'].at('b1', t) for t in (50.0, 100.0, 1_000.0)))
        result = outcome.mission_outcomes['M-b1']
        self.assertEqual((result.status, result.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
        self.assertEqual(result.asset_outcomes['b1'].end_reason, AssetEndReason.BINGO)
        self.assertAlmostEqual(result.asset_outcomes['b1'].end_time, decision.time, delta=1e-9)
        self.assertAlmostEqual(decision.time, movement.start, delta=1e-9)
        self.assertEqual(len(outcome.fuel_events), 0)
        self.assertEqual(b1.fuel, 0.2)
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)

    def test_transfer_under_the_reserve_continues(self):
        """Trasferimento ('Transport') con 0,2: sotto la soglia ma con carburante per la rotta: continua, rotta
        completata consumando la riserva (0,05 a bordo), nessun bingo. Lo stesso volo di combattimento ('CAS')
        interrompe alla partenza e scende sulla base (10 km a sud, ~10,05 km dal punto di comparsa)."""
        mission, blue = self._air(mission_type='Transport')
        outcome, b1, scheduler, _ = self._execute(mission, blue)
        result = outcome.mission_outcomes['M-b1']
        self.assertEqual(result.status, MissionStatus.COMPLETED)
        self.assertEqual(result.asset_outcomes['b1'].end_reason, AssetEndReason.ROUTE_COMPLETED)
        self.assertAlmostEqual(scheduler['legs']['b1'][-1].t_end, 750.0)
        self.assertAlmostEqual(b1.fuel, 0.05)

        mission, blue = self._air(mission_type='CAS')
        outcome, b1, scheduler, _ = self._execute(mission, blue)
        result = outcome.mission_outcomes['M-b1']
        self.assertEqual((result.status, result.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
        self.assertEqual(result.asset_outcomes['b1'].end_time, 0.0)
        descent, parked = scheduler['legs']['b1']
        self.assertEqual((descent.p_start, descent.p_end), ((0.0, 0.0, 1_000.0), (0.0, -10_000.0, 0.0)))
        self.assertAlmostEqual(descent.t_end, sqrt(10_000.0 ** 2 + 1_000.0 ** 2) / 200.0, delta=1e-6)
        self.assertEqual(parked.p_start, parked.p_end)

    def test_air_start_lands_on_the_alternate_base_of_its_route(self):
        """Partenza in volo, due basi: una 60 km dietro, l'altra a 2 km dalla rotta 40 km avanti (base alternativa
        entro 3 km). All'inizio dei tratti il diretto alla base piu' vicina al punto di comparsa (quella sulla
        rotta, ~40,06 km) non e' piu' lungo del percorso lungo la rotta (40 km + ~2,24 km): l'aereo scende sulla
        base della rotta, non su quella dietro, e vi resta a terra."""
        alternate = (2_000.0, 40_000.0)
        mission, blue = self._air(bases=((0.0, -60_000.0), alternate))
        movement, = MA.mission_movements(mission)
        bases = MA.air_base_points(blue, 'Blue')
        decision = MA.mission_bingo_decision(mission, movement, blue[0].assets['b1'], bases)
        self.assertEqual(decision.base, (*alternate, 0.0))

        outcome, _, scheduler, _ = self._execute(mission, blue)
        descent, parked = scheduler['legs']['b1']
        self.assertEqual(descent.p_end, (*alternate, 0.0))
        self.assertAlmostEqual(descent.t_end, decision.return_length / 200.0, delta=1e-6)
        self.assertTrue(scheduler['grounded'].at('b1', descent.t_end + 1.0))
        self.assertEqual(outcome.mission_outcomes['M-b1'].reason, AbortReason.BINGO)
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)

    def test_no_reachable_base_lost_with_the_crew_recovered(self):
        """0,05 del pieno (50 km) e la sola base a 100 km: nessuna raggiungibile, l'aereo punta comunque alla base,
        resta a secco a meta' strada (planata di 5 km da ~500 m): perso, DESTROYED/FUEL_EXHAUSTED con
        l'equipaggio recuperato. Senza bingo dichiarato (F6-A) e senza base: perso, equipaggio recuperato."""
        mission, blue = self._air(fuel=0.05, bases=((0.0, -100_000.0),))
        outcome, b1, scheduler, _ = self._execute(mission, blue)
        asset = outcome.mission_outcomes['M-b1'].asset_outcomes['b1']
        self.assertEqual((asset.state, asset.end_reason, asset.crew_recovered),
                         (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, True))
        self.assertAlmostEqual(scheduler['legs']['b1'][-1].p_end[1], -50_000.0, delta=10.0)
        self.assertTrue(b1.is_destroyed())

        mission, blue = self._air(fuel=0.05, bases=(), bingo=False)
        outcome, _, _, _ = self._execute(mission, blue)
        asset = outcome.mission_outcomes['M-b1'].asset_outcomes['b1']
        self.assertEqual((asset.end_reason, asset.crew_recovered), (AssetEndReason.FUEL_EXHAUSTED, True))

    def test_bingo_declared_off_flies_the_route(self):
        """`EndCriteria.bingo` False: nessun controllo, la rotta basta (0,15 < 0,2): COMPLETED."""
        mission, blue = self._air(bingo=False)
        outcome, _, _, _ = self._execute(mission, blue)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)

    def test_enough_fuel_no_bingo(self):
        mission, blue = self._air(fuel=0.3)
        outcome, _, _, _ = self._execute(mission, blue)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)

    def test_switch_off_is_the_reverse_route_rule(self):
        """Interruttore spento: la F6-B2bis com'era (bingo a meta' rotta, alla distanza della bisezione di
        `Fuel_Model.bingo_point` con la regola della missione), non alla partenza."""
        mission, blue = self._air()
        movement, = MA.mission_movements(mission)
        planned = FM.bingo_point(blue[0].assets['b1'], MA.airborne_legs(movement), MA.air_base_points(blue, 'Blue'),
                                 rule=MA.bingo_return_rule(mission))

        with patch.object(SS, 'F6_BINGO_DISENGAGE_RESERVE', False):
            outcome, _, _, _ = self._execute(mission, blue)

        self.assertGreater(planned.time, 0.0)
        self.assertAlmostEqual(outcome.mission_outcomes['M-b1'].asset_outcomes['b1'].end_time, planned.time, delta=1e-6)


# ── F7a: REGOLE D'INGAGGIO DI MISSIONE ─────────────────────────────────────────

class TestMissionEngagementRules(_Base):
    """F7a (`F7_WEAPON_POLICY`, `F7_TARGET_RULES`, attivi): bersaglio designato, ROE e armi designate della
    missione arrivano al risolutore; il loadout dichiarato dev'essere quello assegnato; con i due interruttori
    spenti la sessione e' quella di prima."""

    def _spy(self, mission_edit=None, switches=(True, True), **run_kwargs):
        """Esegue `_scenario` (M-north con `mission_edit` applicata) registrando le chiamate al risolutore:
        `(outcome, [(kwargs, result), ...])`."""
        blue, red, missions = self._scenario()

        if mission_edit is not None:
            missions = tuple(mission_edit(m) if m.mission_id == 'M-north' else m for m in missions)

        calls = []
        original = ER.resolve_engagement

        def resolve(*args, **kwargs):
            result = original(*args, **kwargs)
            calls.append((kwargs, result))
            return result

        weapon_policy, target_rules = switches

        with patch.object(SS, 'F7_WEAPON_POLICY', weapon_policy), patch.object(SS, 'F7_TARGET_RULES', target_rules), \
                patch.object(SS.ER, 'resolve_engagement', side_effect=resolve):
            outcome = SS.run_session(self._order('S-f7a', missions), blue, red, _fire, reaction_profile_for=_profile,
                                     **run_kwargs)

        return outcome, calls

    @staticmethod
    def _only_re2(mission):
        """M-north: bersaglio GROUP 'Red-East' ristretto a 're2', ROE `only_designated`."""
        target = Target(kind=TargetKind.GROUP, target_id='Red-East', provenance=TargetProvenance.OBSERVED,
                        observed_at=0.0, asset_ids=('re2',))
        return dataclasses.replace(mission, target=target, rules=MissionRules(roe='only_designated'))

    @staticmethod
    def _north_targets(calls):
        return {salvo.target_id for _, result in calls if result is not None for salvo in result.salvos
                if salvo.shooter_id in ('bn1', 'bn2')}

    def test_designation_and_roe_reach_the_resolver(self):
        _, free = self._spy()
        self.assertTrue(all('target_rules' not in kwargs for kwargs, _ in free))
        self.assertIn('re1', self._north_targets(free))                      # premessa: senza regole anche re1

        outcome, calls = self._spy(self._only_re2)
        rules = {asset_id: rule for kwargs, _ in calls for asset_id, rule in kwargs.get('target_rules', {}).items()}
        self.assertEqual(set(rules), {'bn1', 'bn2'})
        self.assertEqual(rules['bn1'].roe, 'only_designated')
        self.assertEqual(rules['bn1'].designated_ids, frozenset({'re2'}))
        self.assertEqual(self._north_targets(calls), {'re2'})
        self.assertGreater(len(outcome.ammunition_events), 0)

    def test_both_switches_off_is_the_weapon_free_session(self):
        free, _ = self._spy()
        off, calls = self._spy(self._only_re2, switches=(False, False))
        self.assertTrue(all('target_rules' not in kwargs for kwargs, _ in calls))
        self.assertEqual(off, free)

    def test_target_rules_switch_alone(self):
        free, _ = self._spy()
        no_rules, calls = self._spy(self._only_re2, switches=(True, False))
        self.assertTrue(all('target_rules' not in kwargs for kwargs, _ in calls))
        self.assertEqual(no_rules, free)
        with_rules, _ = self._spy(self._only_re2, switches=(False, True))
        self.assertNotEqual(with_rules, free)

    def test_mission_loadout_must_be_the_assigned_one(self):
        blue, red, missions = self._scenario()
        blue[0].assets['bn1'].assigned_loadout = 'CAS'
        declared = tuple(dataclasses.replace(m, assets=tuple(dataclasses.replace(a, loadout='Strike')
                                                             for a in m.assets)) if m.mission_id == 'M-north' else m
                         for m in missions)

        for switches in ((True, True), (False, False)):         # la validazione non dipende dagli interruttori
            with self.subTest(switches=switches), patch.object(SS, 'F7_WEAPON_POLICY', switches[0]), \
                    patch.object(SS, 'F7_TARGET_RULES', switches[1]):
                with self.assertRaises(ValueError):
                    SS.run_session(self._order('S-f7a-loadout', declared), blue, red, _fire,
                                   reaction_profile_for=_profile)

    def test_declared_loadout_equal_to_the_assigned_one_is_accepted(self):
        blue, red, missions = self._scenario()
        blue[0].assets['bn1'].assigned_loadout = 'CAS'
        blue[0].assets['bn2'].assigned_loadout = 'CAS'
        declared = tuple(dataclasses.replace(m, assets=tuple(dataclasses.replace(a, loadout='CAS')
                                                             for a in m.assets)) if m.mission_id == 'M-north' else m
                         for m in missions)
        SS.run_session(self._order('S-f7a-loadout-ok', declared), blue, red, _fire, reaction_profile_for=_profile)

    def test_target_destroyed_respects_the_asset_ids(self):
        blue, red, missions = self._scenario()
        mission = missions[0]
        subset = dataclasses.replace(mission, end_criteria=EndCriteria(target_destroyed=True),
                                     target=Target(kind=TargetKind.GROUP, target_id='Red-East',
                                                   provenance=TargetProvenance.OBSERVED, observed_at=0.0,
                                                   asset_ids=('re2',)))
        mission_of = {m.mission_id: m for m in missions}
        assets = {a.id: a for force in blue + red for a in force.assets.values()}
        blocks = {force.id: force for force in blue + red}
        self.assertEqual(SS._mission_target_ids(subset, blocks, mission_of, assets), frozenset({'re2'}))
        whole = dataclasses.replace(subset, target=Target(kind=TargetKind.GROUP, target_id='Red-East',
                                                          provenance=TargetProvenance.OBSERVED, observed_at=0.0))
        self.assertEqual(SS._mission_target_ids(whole, blocks, mission_of, assets), frozenset({'re1', 're2'}))

    def test_return_fire_sees_the_hostiles_of_a_previous_episode(self):
        """b1 (return_fire) sorvola r1 due volte (andata e ritorno, 550 s > `EPISODE_GAP`: due episodi). Nel primo
        r1 gli spara; nel secondo r1 e' un ostile NOTO (memoria per sessione: `known_hostile_ids`) e b1 gli spara
        subito. Nel primo episodio b1 reagisce solo dopo il lancio di r1 (ostile nella run), mai prima."""
        blue = _force('Blue', 'Blue', [_asset(Aircraft, 'b1', -20_000, 0, speed=200.0, ammunition=200)])
        red = _force('Red', 'Red', [_asset(Vehicle, 'r1', 0, 0, ammunition=20)])
        mission = _air_mission('M-b1', blue, _route([(-20_000, 0), (60_000, 0), (-20_000, 0)], 200.0, 'r-b1'),
                               [('b1', 0.0)])
        mission = dataclasses.replace(mission, rules=MissionRules(roe='return_fire'))
        calls = []
        original = ER.resolve_engagement

        def resolve(*args, **kwargs):
            result = original(*args, **kwargs)
            calls.append((kwargs, result))
            return result

        scratch = ER.ShotSpec(accuracy=1.0, destroy_capacity=0.0, rounds=1, time_of_flight=1.0)

        def fire(shooter, target):
            return scratch                                       # nessuno distrugge nessuno: due episodi

        with patch.object(SS.ER, 'resolve_engagement', side_effect=resolve):
            SS.run_session(self._order('S-f7a-hostile', (mission,)), [blue], [red], fire,
                           reaction_profile_for=_profile)

        self.assertEqual(len(calls), 2)
        first_rules = calls[0][0]['target_rules']['b1']
        second_rules = calls[1][0]['target_rules']['b1']
        self.assertEqual((first_rules.roe, first_rules.known_hostile_ids), ('return_fire', frozenset()))
        self.assertEqual(second_rules.known_hostile_ids, frozenset({'r1'}))
        first = calls[0][1]
        first_hostile = min(s.t_launch for s in first.salvos if s.shooter_id == 'r1')
        reaction = [s.t_launch for s in first.salvos if s.shooter_id == 'b1' and s.target_id == 'r1']
        self.assertTrue(reaction)                                   # stessa run: reazione al lancio di r1
        self.assertTrue(all(t > first_hostile for t in reaction))   # ... mai prima
        self.assertTrue(any(s.shooter_id == 'b1' and s.target_id == 'r1' for s in calls[1][1].salvos))

    def test_priority_designated_gets_the_attack_point_of_the_asset_route(self):
        """`TargetRules.attack_point` = punto ATTACK sulla rotta DELL'ASSET (offset di formazione compreso)."""
        blue, red, missions = self._scenario()
        north = missions[0]
        roles = [WaypointRole.NAV, WaypointRole.ATTACK, WaypointRole.LAND]
        route = _route([(0, -20_000), (0, 0), (0, 20_000)], 200.0, 'r-bn1')
        waypoints = tuple(MissionWaypoint(wp, role) for wp, role in zip(route_waypoints(route), roles))
        north = dataclasses.replace(north, route=route, waypoints=waypoints,
                                    rules=MissionRules(roe='priority_designated'))
        calls = []
        original = ER.resolve_engagement

        def resolve(*args, **kwargs):
            calls.append(kwargs)
            return original(*args, **kwargs)

        with patch.object(SS.ER, 'resolve_engagement', side_effect=resolve):
            SS.run_session(self._order('S-f7a-attack', (north, missions[1])), blue, red, _fire,
                           reaction_profile_for=_profile)

        rules = {asset_id: rule for kwargs in calls for asset_id, rule in kwargs.get('target_rules', {}).items()}
        self.assertEqual(set(rules), {'bn1', 'bn2'})
        self.assertEqual(rules['bn1'].attack_point, (0.0, 0.0, 0.0))
        self.assertEqual(rules['bn2'].attack_point, (500.0, 0.0, 0.0))      # bn2 a 500 m sulla destra (est)


if __name__ == '__main__':
    unittest.main()


# ── G3: CONSUMO DI CARBURANTE IN INGAGGIO ──────────────────────────────────────

def _aircraft_fire(shooter, target):
    """Spara solo l'aereo: i veicoli rossi non rispondono (consumo d'ingaggio isolato dal danno)."""
    return SPEC if type(shooter).__name__ == 'Aircraft' else None


class TestEngagementFuel(_Base):
    """G3 (`G3_ENGAGEMENT_FUEL`, attivo): l'aereo in volo che partecipa a un ingaggio consuma la riserva di
    disimpegno (aerei di test: ripiego 'max', 200 m/s x 300 s / 500 km = 0,12) all'istante della prima
    partecipazione; il movimento resta alla crociera; terra e mare invariati."""

    CHARGE = 200.0 * FM.DISENGAGE_TIME / AUTONOMY['max']

    def _single(self, fuel=1.0, parked=False, fire=_aircraft_fire):
        """Un aereo blu su 40 km (200 s) sopra un veicolo rosso fermo (e, a richiesta, un aereo rosso parcheggiato
        senza missione accanto al veicolo)."""
        blue = _force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0, -20_000, fuel=fuel, speed=200.0)])
        reds = [_asset(Vehicle, 'r1', 0, 0)]

        if parked:
            reds.append(_asset(Aircraft, 'rp1', 300, 0))

        red = _force('Red', 'Red', reds)
        mission = _air_mission('M-b1', blue, _route([(0, -20_000), (0, 20_000)], 200.0, 'r-b1'), [('b1', 0.0)])
        outcome = SS.run_session(self._order('S-g3', (mission,)), [blue], [red], fire, reaction_profile_for=_profile)
        return outcome, blue.assets['b1'], red

    def test_engagement_fuel_is_the_disengagement_reserve(self):
        asset = _asset(Aircraft, 'x', 0, 0, speed=200.0)
        self.assertAlmostEqual(FM.engagement_fuel(asset), FM.disengagement_reserve(asset))
        self.assertAlmostEqual(FM.engagement_fuel(asset), self.CHARGE)

    def test_one_charge_before_the_leg_and_movement_at_cruise(self):
        outcome, b1, _ = self._single()
        events = [e for e in outcome.fuel_events if e.asset_id == 'b1']
        self.assertEqual([e.regime for e in events], [FM.ENGAGEMENT_REGIME, SS.CRUISE_REGIME])
        charge, leg = events
        self.assertAlmostEqual(charge.amount, self.CHARGE)
        self.assertTrue(0.0 < charge.time < leg.time)
        self.assertAlmostEqual(leg.amount, 40_000.0 / AUTONOMY['nominal'])
        self.assertAlmostEqual(leg.fuel_before, 1.0 - self.CHARGE)
        self.assertAlmostEqual(b1.fuel, 1.0 - self.CHARGE - 0.04)
        self.assertFalse(any(e.asset_id == 'r1' for e in outcome.fuel_events))

    def test_switch_off_is_the_f6a_rule(self):
        with patch.object(SS, 'G3_ENGAGEMENT_FUEL', False):
            outcome, b1, _ = self._single()

        events = [e for e in outcome.fuel_events if e.asset_id == 'b1']
        self.assertEqual([e.regime for e in events], [SS.COMBAT_REGIME])
        self.assertAlmostEqual(b1.fuel, 1.0 - 40_000.0 / AUTONOMY['max'])

    def test_no_engagement_no_charge(self):
        outcome, b1, _ = self._single(fire=lambda shooter, target: None)
        self.assertEqual([e.regime for e in outcome.fuel_events], [SS.CRUISE_REGIME])
        self.assertAlmostEqual(b1.fuel, 0.96)

    def test_a_parked_aircraft_hit_on_the_ground_does_not_consume(self):
        """Il bersaglio aereo a terra (senza missione, F4c) colpito sul parcheggio non manovra: nessun consumo."""
        outcome, _, red = self._single(parked=True)
        targeted = {e.target_id for e in outcome.damage_events}
        self.assertIn('rp1', targeted)
        self.assertFalse(any(e.asset_id == 'rp1' for e in outcome.fuel_events))
        self.assertEqual(red.assets['rp1'].fuel, 1.0)

    def test_exhaustion_by_the_charge_empties_the_counter_only(self):
        """G4b spento (il G3 e il G4a): carburante 0,10 < consumo d'ingaggio 0,12: il contatore va a zero
        all'istante dell'ingaggio, nessun evento dopo (il tratto non e' contabilizzato), ma l'aereo non e' fermato
        ne' perso (nessun ri-scheduling): esito di rotta completata, nessun `crew_recovered`. Senza basi il bingo
        alla partenza (soglia 0,04 + 0,12) non ha dove rientrare (`BINGO_NO_BASE`). Con il G4b acceso v.
        `TestReplanAfterEpisode`."""
        with patch.object(SS, 'G4_REPLAN', False):
            outcome, b1, _ = self._single(fuel=0.10)
        events = [e for e in outcome.fuel_events if e.asset_id == 'b1']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].regime, FM.ENGAGEMENT_REGIME)
        self.assertAlmostEqual(events[0].amount, 0.10)
        self.assertTrue(events[0].exhausted)
        self.assertEqual(b1.fuel, 0.0)
        self.assertFalse(b1.is_destroyed())
        asset_outcome = outcome.mission_outcomes['M-b1'].asset_outcomes['b1']
        self.assertEqual(asset_outcome.end_reason, AssetEndReason.ROUTE_COMPLETED)
        self.assertIsNone(asset_outcome.crew_recovered)

    def test_without_per_leg_fuel_the_charge_precedes_the_single_event(self):
        with patch.object(SS, 'F6_FUEL_PER_LEG', False):
            outcome, b1, _ = self._single()

        self.assertEqual([e.regime for e in outcome.fuel_events], [FM.ENGAGEMENT_REGIME, SS.CRUISE_REGIME])
        self.assertAlmostEqual(b1.fuel, 1.0 - self.CHARGE - 0.04)

    def test_engagement_instants_first_participation(self):
        """Prima partecipazione: lancio delle salve sparate o ricevute, intercettazioni."""
        salvo = lambda sid, t, shooter, target: ER.Salvo(salvo_id=sid, t_launch=t, t_impact=t + 5.0, shooter_id=shooter,
                                                        target_id=target, target_force_id='F', rounds=1, spec=SPEC)
        result = ER.EngagementResult(
            t_start=0.0, t_end=100.0, forces=(),
            salvos=(salvo(0, 30.0, 'a', 'b'), salvo(1, 10.0, 'c', 'a'), salvo(2, 50.0, 'b', 'c')),
            interception_events=(ER.InterceptionEvent(time=20.0, asset_id='d', interceptions=1),
                                 ER.InterceptionEvent(time=5.0, asset_id='b', interceptions=1)))
        self.assertEqual(SS._engagement_instants(result), {'a': 10.0, 'b': 5.0, 'c': 10.0, 'd': 20.0})
        self.assertEqual(set(SS._engagement_instants(result)), SS._engaged_assets(result))


# ── G4a: EPISODI D'INGAGGIO ────────────────────────────────────────────────────

def _cw(a, b, t_start, t_end):
    """Finestra di contatto minima (solo gli istanti contano per gli episodi)."""
    return CS.ContactWindow(asset_a_id=a, asset_b_id=b, t_start=float(t_start), t_end=float(t_end),
                            t_cpa=float(t_start), distance_cpa=0.0, range_a=1.0, range_b=1.0)


class TestEpisodes(unittest.TestCase):
    """`_episodes` (G4a): finestre legate da una forza (o un dominio di coordinamento) comune che si sovrappongono
    entro `EPISODE_GAP`; ordine deterministico."""

    def test_gap_is_the_disengage_time(self):
        self.assertEqual(SS.EPISODE_GAP, FM.DISENGAGE_TIME)
        self.assertEqual(SS.EPISODE_GAP, 300.0)

    def test_the_gap_splits_the_same_pair(self):
        near = {('a', 'b'): [_cw('x', 'y', 0, 100), _cw('x', 'y', 400, 500)]}
        far = {('a', 'b'): [_cw('x', 'y', 0, 100), _cw('x', 'y', 401, 500)]}
        self.assertEqual([ids for ids, _ in SS._episodes(near)], [('a', 'b')])
        self.assertEqual([(ids, [w.t_start for w in ws]) for ids, ws in SS._episodes(far)],
                         [(('a', 'b'), [0.0]), (('a', 'b'), [401.0])])
        self.assertEqual(len(SS._episodes(near, gap=0.0)), 2)
        self.assertEqual(len(SS._episodes({('a', 'b'): [_cw('x', 'y', 0, 100), _cw('x', 'y', 100, 200)]}, gap=0.0)), 1)

    def test_a_shared_force_joins_and_chains(self):
        shared = {('a1', 'b1'): [_cw('x', 'y', 0, 100)], ('a1', 'b2'): [_cw('x', 'z', 250, 300)]}
        self.assertEqual([ids for ids, _ in SS._episodes(shared)], [('a1', 'b1', 'b2')])
        chain = {('a1', 'b1'): [_cw('p', 'q', 0, 100)], ('a2', 'b1'): [_cw('r', 'q', 350, 450)],
                 ('a2', 'b2'): [_cw('r', 's', 700, 800)]}
        self.assertEqual([ids for ids, _ in SS._episodes(chain)], [('a1', 'a2', 'b1', 'b2')])
        disjoint = {('a2', 'b2'): [_cw('r', 's', 50, 80)], ('a1', 'b1'): [_cw('p', 'q', 0, 100)]}
        self.assertEqual([ids for ids, _ in SS._episodes(disjoint)], [('a1', 'b1'), ('a2', 'b2')])

    def test_coordination_domain_joins_only_within_the_gap(self):
        domains = {'a1': 'D', 'a2': 'D', 'b1': 'b1', 'b2': 'b2'}
        overlapping = {('a1', 'b1'): [_cw('p', 'q', 0, 100)], ('a2', 'b2'): [_cw('r', 's', 50, 80)]}
        apart = {('a1', 'b1'): [_cw('p', 'q', 0, 100)], ('a2', 'b2'): [_cw('r', 's', 1000, 1100)]}
        self.assertEqual([ids for ids, _ in SS._episodes(overlapping, domains)], [('a1', 'a2', 'b1', 'b2')])
        self.assertEqual([ids for ids, _ in SS._episodes(apart, domains)], [('a1', 'b1'), ('a2', 'b2')])

    def test_infinite_gap_is_the_connected_component(self):
        groups = {('a1', 'b1'): [_cw('p', 'q', 0, 100), _cw('p', 'q', 5000, 5100)],
                  ('a1', 'b2'): [_cw('p', 'z', 9000, 9100)], ('a2', 'b3'): [_cw('r', 's', 20, 30)]}
        domains = {'a1': 'D', 'a2': 'D'}

        for mapping in (None, domains):
            with self.subTest(domains=mapping):
                self.assertEqual(sorted(SS._episodes(groups, mapping, gap=float('inf'))),
                                 sorted(SS._connected_components(groups, mapping)))

    def test_one_episode_has_the_windows_of_the_component_in_its_order(self):
        groups = {('a2', 'b1'): [_cw('r', 'q', 10, 50)], ('a1', 'b1'): [_cw('p', 'q', 30, 60), _cw('p', 'q', 0, 20)]}
        self.assertEqual(SS._episodes(groups), SS._connected_components(groups))

    def test_order_by_time_then_event_id_and_dict_order_independent(self):
        groups = {('a3', 'b3'): [_cw('u', 'v', 10, 20)], ('a2', 'b2'): [_cw('r', 's', 0, 5)],
                  ('a1', 'b1'): [_cw('p', 'q', 10, 20)]}
        expected = [('a2', 'b2'), ('a1', 'b1'), ('a3', 'b3')]
        self.assertEqual([ids for ids, _ in SS._episodes(groups)], expected)
        self.assertEqual([ids for ids, _ in SS._episodes(dict(reversed(list(groups.items()))))], expected)

    def test_negative_gap_raises(self):
        with self.assertRaises(ValueError):
            SS._episodes({}, gap=-1.0)

    def test_busy_force_trims_or_drops_the_later_windows(self):
        """Forza occupata: le finestre di 'a' che cominciano prima della fine del suo episodio sono ritagliate o
        scartate; quelle di altre forze non cambiano."""
        legs = {name: CS.static_legs(Point3D(0, 0, 0), 0.0, 1000.0) for name in ('p', 'q', 'r', 's')}
        left = {('a', 'b'): [_cw('p', 'q', 100, 200), _cw('p', 'q', 150, 400)], ('c', 'd'): [_cw('r', 's', 100, 200)]}

        with patch(_SOURCE + 'Logic.Session_Simulator.logger'):
            self.assertTrue(SS._trim_busy(left, {'a': 300.0}, legs))
            self.assertFalse(SS._trim_busy(left, {'a': 300.0}, legs))

        self.assertEqual([(w.t_start, w.t_end) for w in left[('a', 'b')]], [(300.0, 400.0)])
        self.assertEqual([(w.t_start, w.t_end) for w in left[('c', 'd')]], [(100.0, 200.0)])


class TestEngagementEpisodes(_Base):
    """G4a (`G4_EPISODES`, attivo): un aereo blu sorvola due veicoli della STESSA forza rossa a 150 km l'uno
    dall'altro (finestre [75, 125] e [825, 875] s, 700 s > `EPISODE_GAP`): due episodi con lo stesso insieme di
    forze, risolti in ordine di tempo, ciascuno con le sole sue finestre."""

    CHARGE = 200.0 * FM.DISENGAGE_TIME / AUTONOMY['max']
    # Il blu manca sempre, i veicoli rossi (2 salve ciascuno) graffiano senza distruggere: 5 punti a salva.
    MISS = ER.ShotSpec(accuracy=0.0, destroy_capacity=0.0, rounds=1, time_of_flight=1.0)
    SCRATCH = ER.ShotSpec(accuracy=1.0, destroy_capacity=0.0, rounds=5, time_of_flight=1.0)

    def _scratch(self, shooter, target):
        return self.MISS if type(shooter).__name__ == 'Aircraft' else self.SCRATCH

    def _patrol(self, fire=_aircraft_fire, episodes=True, session_id='S-g4a', criteria=None, spy=None):
        blue = _force('Blue', 'Blue', [_asset(Aircraft, 'b1', -20_000, 0, speed=200.0, ammunition=200)])
        red = _force('Red', 'Red', [_asset(Vehicle, 'r1', 0, 0, ammunition=2), _asset(Vehicle, 'r2', 150_000, 0, ammunition=2)])
        mission = _air_mission('M-b1', blue, _route([(-20_000, 0), (200_000, 0)], 200.0, 'r-b1'), [('b1', 0.0)])

        if criteria:
            mission = _with_criteria(mission, **criteria)

        calls = []
        original = ER.resolve_engagement

        def resolve(*args, **kwargs):
            forces = (args[0], args[1], *kwargs.get('extra_forces', ()))
            health = {asset.id: asset.health for force in forces for asset in force.assets.values()}
            result = original(*args, **kwargs)
            result = spy(len(calls), result) if spy is not None and result is not None else result
            calls.append((args, kwargs, health, result))
            return result

        with patch.object(SS, 'G4_EPISODES', episodes), patch.object(SS.ER, 'resolve_engagement', side_effect=resolve):
            outcome = SS.run_session(self._order(session_id, (mission,)), [blue], [red], fire,
                                     reaction_profile_for=_profile)

        return outcome, blue.assets['b1'], calls

    def test_two_episodes_in_time_order_with_their_own_windows(self):
        outcome, _, calls = self._patrol()
        self.assertEqual(len(calls), 2)
        self.assertEqual([{w.asset_b_id for w in args[2]} for args, *_ in calls], [{'r1'}, {'r2'}])
        self.assertLess(max(w.t_end for w in calls[0][0][2]), min(w.t_start for w in calls[1][0][2]))
        self.assertEqual([tuple(o.force_id for o in e) for e in outcome.engagement_outcomes],
                         [('M-b1', 'Red'), ('M-b1', 'Red')])
        self.assertEqual(len(outcome.outcomes_of('M-b1')), 2)

    def test_switch_off_is_one_connected_component(self):
        outcome, _, calls = self._patrol(episodes=False)
        self.assertEqual(len(calls), 1)
        self.assertEqual({w.asset_b_id for w in calls[0][0][2]}, {'r1', 'r2'})
        self.assertEqual(len(outcome.engagement_outcomes), 1)

    def test_same_forces_counter_is_the_ordinal(self):
        """Stesso insieme di forze: stesso event_id, `counter` 0 e 1, per l'ingaggio e per la tempra (tempra nuova)."""
        original = SessionOrder.rng

        with patch.object(SessionOrder, 'rng', autospec=True, side_effect=original) as spy:
            outcome, _, _ = self._patrol()

        keys = [(tuple(json.loads(call.kwargs['event_id'])), call.kwargs['counter']) for call in spy.call_args_list]
        self.assertEqual(keys, [(('engagement', 'M-b1', 'Red'), 0), (('temper', 'M-b1', 'Red'), 0),
                                (('engagement', 'M-b1', 'Red'), 1), (('temper', 'M-b1', 'Red'), 1)])
        first, second = outcome.outcomes_of('M-b1')
        self.assertNotEqual(first.temper, second.temper)

    # Requisito del G4a: con l'uscita di scena del G4b (`G4_OFF_SCENE_EXIT`, partenze in volo senza basi) una
    # forza disingaggiata cambierebbe rotta dopo l'episodio; qui si confrontano solo episodi e componenti.
    @patch.object(SS, 'G4_OFF_SCENE_EXIT', False)
    def test_one_episode_sessions_are_identical_to_the_switch_off(self):
        """Requisito forte: una componente che e' un solo episodio ha lo stream e l'esito di prima."""
        for session_id in ('S-one-1', 'S-one-2'):
            with self.subTest(session_id=session_id):
                with patch.object(SS, 'G4_EPISODES', False):
                    before, _, _ = self._run(session_id)

                after, _, _ = self._run(session_id)
                self.assertEqual(after, before)
                self.assertGreater(len(after.damage_events), 0)

        for session_id in ('S-one-3', 'S-one-4'):
            with self.subTest(session_id=session_id):
                outcomes = []

                for episodes in (False, True):
                    raider, red_a, red_b, missions = TestTwoFronts._forces(self)

                    with patch.object(SS, 'G4_EPISODES', episodes):
                        outcomes.append(SS.run_session(self._order(session_id, missions), [raider], [red_a, red_b],
                                                       _fire, reaction_profile_for=_profile))

                self.assertEqual(outcomes[1], outcomes[0])

    def test_deterministic(self):
        first, _, _ = self._patrol(fire=_fire)
        second, _, _ = self._patrol(fire=_fire)
        self.assertEqual(first, second)

    def test_two_engagement_charges_in_two_episodes(self):
        """G3: un consumo d'ingaggio per episodio, all'istante della prima salva di ciascuno, prima del tratto
        (unico) di movimento alla crociera; con il G4a spento un consumo solo."""
        outcome, b1, calls = self._patrol()
        events = [e for e in outcome.fuel_events if e.asset_id == 'b1']
        self.assertEqual([e.regime for e in events], [FM.ENGAGEMENT_REGIME, FM.ENGAGEMENT_REGIME, SS.CRUISE_REGIME])
        first = [min(s.t_launch for s in result.salvos) for *_, result in calls]
        self.assertEqual([e.time for e in events[:2]], first)
        self.assertAlmostEqual(events[0].amount, self.CHARGE)
        self.assertAlmostEqual(events[1].fuel_before, events[0].fuel_after)
        self.assertAlmostEqual(events[2].fuel_before, 1.0 - 2 * self.CHARGE)
        self.assertAlmostEqual(b1.fuel, 1.0 - 2 * self.CHARGE - 220_000.0 / AUTONOMY['nominal'])

        outcome, _, _ = self._patrol(episodes=False)
        self.assertEqual([e.regime for e in outcome.fuel_events if e.asset_id == 'b1'],
                         [FM.ENGAGEMENT_REGIME, SS.CRUISE_REGIME])

    def test_health_is_chained_across_episodes(self):
        """Ogni esito e' applicato prima dell'episodio successivo: il secondo legge la salute gia' ridotta e i
        `health_before/after` sono concatenati."""
        outcome, b1, calls = self._patrol(fire=self._scratch)
        hits = [e for e in outcome.damage_events if e.target_id == 'b1']
        self.assertTrue(any(e.time < 500 for e in hits) and any(e.time > 500 for e in hits))
        self.assertEqual(calls[1][2]['b1'], [e for e in hits if e.time < 500][-1].health_after)

        for previous, event in zip(hits, hits[1:]):
            self.assertEqual(event.health_before, previous.health_after)

        self.assertEqual(b1.health, hits[-1].health_after)

    def test_damage_threshold_reference_is_the_session_start_health(self):
        """Soglia di danno: la salute di riferimento passata a OGNI episodio e' quella d'inizio sessione (100),
        anche quando l'aereo entra nel secondo gia' danneggiato; con il G4a spento non e' passata."""
        _, _, calls = self._patrol(fire=self._scratch, criteria={'damage_threshold': 0.9})
        self.assertEqual([kwargs['activity_criteria']['b1'].reference_health for _, kwargs, *_ in calls], [100, 100])
        self.assertLess(calls[1][2]['b1'], 100)

        _, _, calls = self._patrol(fire=self._scratch, criteria={'damage_threshold': 0.9}, episodes=False)
        self.assertIsNone(calls[0][1]['activity_criteria']['b1'].reference_health)

    # Partenza in volo senza basi: dal G4b la forza disingaggiata uscirebbe di scena (`G4_OFF_SCENE_EXIT`,
    # provata in TestReplanAfterEpisode) e il secondo episodio non ci sarebbe; qui si prova la passivita' del G4a.
    @patch.object(SS, 'G4_OFF_SCENE_EXIT', False)
    def test_a_disengaged_force_is_passive_in_the_later_episodes(self):
        """Forza DISINGAGGIATA nel primo episodio (esito forzato a 100 s): nel secondo nessuna salva offensiva
        (`until` = istante del disingaggio), resta bersaglio; senza disingaggio nel secondo episodio spara."""
        def disengage(index, result):
            if index:
                return result

            forces = tuple(dataclasses.replace(o, outcome=ER.DISENGAGED, time=100.0) if o.force_id == 'M-b1' else o
                           for o in result.forces)
            return dataclasses.replace(result, forces=forces)

        _, _, free = self._patrol()
        self.assertTrue(any(s.shooter_id == 'b1' for s in free[1][3].salvos))

        outcome, _, calls = self._patrol(spy=disengage)
        self.assertEqual(calls[1][1]['activity_criteria']['b1'].until, 100.0)
        self.assertFalse(any(s.shooter_id == 'b1' for s in calls[1][3].salvos))
        self.assertEqual(outcome.outcomes_of('M-b1')[0].outcome, ER.DISENGAGED)

    def test_an_activity_end_carries_over_to_the_later_episodes(self):
        """Fine di attivita' (qui: danno oltre la soglia 0,01, il primo graffio) nel primo episodio: nel secondo l'aereo e' passivo
        dall'istante della fine, nessuna salva offensiva."""
        _, _, free = self._patrol(fire=self._scratch)
        self.assertTrue(any(s.shooter_id == 'b1' for s in free[1][3].salvos))
        _, _, calls = self._patrol(fire=self._scratch, criteria={'damage_threshold': 0.01})
        end, = [e for e in calls[0][3].activity_ends if e.asset_id == 'b1']
        self.assertEqual(end.reason, ER.ACTIVITY_DAMAGE)
        self.assertEqual(calls[1][1]['activity_criteria']['b1'].until, end.time)
        self.assertFalse(any(s.shooter_id == 'b1' for s in calls[1][3].salvos))

    def test_a_force_busy_until_its_salvos_land_skips_the_overlapping_contact(self):
        """Forza occupata: salve con 1000 s di volo nel primo episodio (fine dell'esito > 1000 s), quindi la
        finestra con r2 ([825, 875] s) cade dentro l'occupazione ed e' scartata: un solo episodio."""
        slow = ER.ShotSpec(accuracy=0.7, destroy_capacity=0.3, rounds=1, time_of_flight=1000.0)
        outcome, _, calls = self._patrol(fire=lambda shooter, target: slow if type(shooter).__name__ == 'Aircraft'
                                         else None)
        self.assertEqual(len(calls), 1)
        self.assertGreater(calls[0][3].t_end, 875.0)
        self.assertEqual({w.asset_b_id for w in calls[0][0][2]}, {'r1'})


# ── G4b: RI-PIANIFICAZIONE DOPO L'EPISODIO D'INGAGGIO ──────────────────────────

class TestReplanAfterEpisode(_Base):
    """G4b (`G4_REPLAN`, attivo): alla fine di ogni episodio gli aerei di missione in volo che vi hanno consumato
    (G3) o la cui forza si e' disingaggiata sono ri-pianificati da quell'istante. Volo di test: b1 in volo da
    (0, 0, 1000) verso nord per 150 km a 200 m/s (750 s, 0,15 del pieno alla crociera); veicoli rossi r1 a 20 km
    (finestra ~[75, 125] s) e r2 a 100 km (~[475, 525] s), due episodi; spara solo l'aereo (consumo d'ingaggio
    0,12 = la riserva di ripiego, v. `TestEngagementFuel`); base aerea Blue a (0, -10 km)."""

    CHARGE = TestEngagementFuel.CHARGE

    def _flight(self, fuel=0.30, base=(0.0, -10_000.0), mission_type='CAS', bingo=True, replan=True, spy=None,
                z=1_000.0, fire=_aircraft_fire, session_id='S-g4b', exit_scene=True):
        blue = [_force('Blue', 'Blue', [_asset(Aircraft, 'b1', 0.0, 0.0, z=z, fuel=fuel, speed=200.0)])]

        if base is not None:
            blue.append(TestReserveBingo._airbase(self, base))

        red = _force('Red', 'Red', [_asset(Vehicle, 'r1', 0.0, 20_000.0), _asset(Vehicle, 'r2', 0.0, 100_000.0)])
        mission = _air_mission('M-b1', blue[0], _route([(0.0, 0.0), (0.0, 150_000.0)], 200.0, 'r-b1', z=z),
                               [('b1', 0.0)])
        mission = dataclasses.replace(mission, mission_type=mission_type, end_criteria=EndCriteria(bingo=bingo))
        calls = []
        original = ER.resolve_engagement

        def resolve(*args, **kwargs):
            result = original(*args, **kwargs)
            result = spy(len(calls), result) if spy is not None and result is not None else result
            calls.append((args, kwargs, result))
            return result

        with patch.object(SS, 'G4_REPLAN', replan), patch.object(SS, 'G4_OFF_SCENE_EXIT', exit_scene), \
                patch.object(SS.ER, 'resolve_engagement', side_effect=resolve), \
                patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler, \
                patch.object(FM, 'bingo_decision', wraps=FM.bingo_decision) as decisions:
            outcome = SS.run_session(self._order(session_id, (mission,)), blue, [red], fire,
                                     reaction_profile_for=_profile)

        return outcome, blue[0].assets['b1'], calls, scheduler, decisions

    @staticmethod
    def _disengage_first(index, result):
        """Esito della forza blu forzato a DISINGAGGIATA nel primo episodio (100 s)."""
        if index:
            return result

        forces = tuple(dataclasses.replace(o, outcome=ER.DISENGAGED, time=100.0) if o.force_id == 'M-b1' else o
                       for o in result.forces)
        return dataclasses.replace(result, forces=forces)

    @staticmethod
    def _miss(shooter, target):
        """Spara solo l'aereo, e manca sempre: il bersaglio resta operativo per tutta la finestra."""
        return TestEngagementEpisodes.MISS if type(shooter).__name__ == 'Aircraft' else None

    @staticmethod
    def _met(calls, asset_id):
        return any(asset_id in (w.asset_a_id, w.asset_b_id) for args, _, _ in calls for w in args[2])

    def test_the_switch_is_on_and_needs_the_episodes(self):
        self.assertTrue(SS.G4_REPLAN)
        _, _, calls, scheduler, _ = self._flight(fuel=1.0, spy=self._disengage_first)
        self.assertGreater(scheduler.call_count, 1)

        with patch.object(SS, 'G4_EPISODES', False):
            _, _, _, scheduler, _ = self._flight(fuel=1.0, spy=self._disengage_first)

        self.assertEqual(scheduler.call_count, 1)

    def test_bingo_after_the_episode_returns_and_never_meets_the_threat_ahead(self):
        """0,30 > soglia alla partenza (0,15 + 0,12): nessun bingo al G2; dopo il primo episodio (consumo 0,12) il
        residuo a fine episodio e' sotto il resto della rotta + la riserva: bingo da `t_r`, ritroso fino al punto
        di comparsa e diretto sulla base; r2, piu' avanti sulla rotta, non e' mai incontrato. Esito BINGO a `t_r`,
        ABORTED(BINGO), a terra sulla base."""
        outcome, b1, calls, scheduler, decisions = self._flight(fire=self._miss)
        t_r = calls[0][2].t_end
        self.assertFalse(self._met(calls, 'r2'))
        # Contatti ricalcolati da `t_r` (l'aereo manca sempre, r1 resta operativo): sul ritroso l'aereo ripassa su r1
        # (nuovo episodio, passivo: nessuna salva).
        self.assertEqual(len(calls), 2)
        self.assertEqual({w.asset_b_id for w in calls[1][0][2]}, {'r1'})
        self.assertGreaterEqual(min(w.t_start for w in calls[1][0][2]), t_r - 1e-9)
        self.assertEqual(calls[1][2].salvos, ())
        self.assertFalse(any(e.target_id == 'r2' for e in outcome.damage_events))
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
        asset = mission.asset_outcomes['b1']
        self.assertEqual(asset.end_reason, AssetEndReason.BINGO)
        self.assertAlmostEqual(asset.end_time, t_r, delta=1e-9)
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)
        legs = scheduler.call_args.kwargs['legs']['b1']
        self.assertEqual(legs[-1].p_end, (0.0, -10_000.0, 0.0))
        self.assertAlmostEqual(legs[0].t_end, t_r, delta=1e-6)
        # Residuo analitico a `t_r` (coerenza con la contabilita'): partenza - crociera fino a `t_r` - consumo.
        replanned = [call for call in decisions.call_args_list if call.kwargs.get('time') not in (None, 0.0)]
        self.assertEqual(len(replanned), 1)
        residual = 0.30 - 200.0 * t_r / AUTONOMY['nominal'] - self.CHARGE
        self.assertAlmostEqual(replanned[0].kwargs['fuel'], residual, delta=1e-12)
        decision = FM.bingo_decision(b1, *replanned[0].args[1:], **replanned[0].kwargs)
        self.assertAlmostEqual(b1.fuel, residual - decision.return_length / AUTONOMY['nominal'], delta=1e-9)
        self.assertFalse(any(e.exhausted for e in outcome.fuel_events))

    def test_switch_off_flies_on_and_empties_the_counter(self):
        """G4b spento (il G4a): l'aereo prosegue, incontra r2, consuma due volte e il contatore arriva a zero con
        la rotta completata (il limite del G3)."""
        outcome, b1, calls, scheduler, _ = self._flight(replan=False)
        self.assertTrue(self._met(calls, 'r2'))
        self.assertEqual(scheduler.call_count, 1)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)
        self.assertEqual(b1.fuel, 0.0)

    def test_above_the_threshold_nothing_changes(self):
        """Pieno: dopo ogni consumo l'aereo resta sopra la soglia, nessun tratto cambia, nessun nuovo scheduling:
        l'esito e' quello del G4a."""
        outcome, _, _, scheduler, _ = self._flight(fuel=1.0)
        self.assertEqual(scheduler.call_count, 1)
        before, _, _, _, _ = self._flight(fuel=1.0, replan=False)
        self.assertEqual(outcome, before)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)

    def test_exhaustion_in_the_engagement_without_a_base_is_a_loss(self):
        """0,10 < consumo d'ingaggio 0,12, nessuna base (nessun bingo possibile alla partenza): esaurito in
        ingaggio, regole della F6-A dal punto a fine episodio, nessuna base in planata: perso con l'equipaggio
        recuperato, i tratti finiscono a `t_r`, r2 mai incontrato."""
        outcome, b1, calls, scheduler, _ = self._flight(fuel=0.10, base=None)
        t_r = calls[0][2].t_end
        asset = outcome.mission_outcomes['M-b1'].asset_outcomes['b1']
        self.assertEqual((asset.state, asset.end_reason, asset.crew_recovered),
                         (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, True))
        self.assertAlmostEqual(asset.end_time, t_r, delta=1e-9)
        self.assertAlmostEqual(scheduler.call_args.kwargs['legs']['b1'][-1].t_end, t_r, delta=1e-6)
        self.assertTrue(b1.is_destroyed())
        self.assertFalse(self._met(calls, 'r2'))
        self.assertEqual(outcome.postures['b1'], MA.DESTROYED_POSTURE)

    def test_exhaustion_in_the_engagement_glides_to_a_reachable_base(self):
        """Come sopra, con una base 5 km a est del punto di fine episodio (planata 10 km da 1000 m) e il bingo non
        dichiarato (altrimenti al G2 l'aereo tornerebbe subito): planata sulla base, a terra, FUEL_EXHAUSTED,
        ABORTED(FUEL)."""
        _, _, calls, _, _ = self._flight(fuel=0.10, base=None)
        y = 200.0 * calls[0][2].t_end
        outcome, b1, _, scheduler, _ = self._flight(fuel=0.10, base=(5_000.0, y), bingo=False)
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.FUEL))
        self.assertEqual((mission.asset_outcomes['b1'].state, mission.asset_outcomes['b1'].end_reason),
                         (AssetState.OPERATIONAL, AssetEndReason.FUEL_EXHAUSTED))
        glide, parked = scheduler.call_args.kwargs['legs']['b1'][-2:]
        for got, want in zip(glide.p_end, (5_000.0, y, 0.0)):
            self.assertAlmostEqual(got, want, delta=1e-6)

        self.assertEqual(parked.p_start, parked.p_end)
        self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)
        self.assertFalse(b1.is_destroyed())

    def test_disengaged_force_returns_with_plenty_of_fuel(self):
        """Forza disingaggiata nel primo episodio, carburante pieno (nessuna soglia): rientro forzato con la regola
        di combattimento da `t_r`, motivo DISENGAGED, ABORTED(DISENGAGED); r2 mai incontrato. Anche un
        trasferimento ('Transport') rientra: il rientro forzato e' sempre con la regola di combattimento."""
        for mission_type in ('CAS', 'Transport'):
            with self.subTest(mission_type=mission_type):
                outcome, _, calls, scheduler, _ = self._flight(fuel=1.0, spy=self._disengage_first,
                                                               mission_type=mission_type)
                mission = outcome.mission_outcomes['M-b1']
                self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.DISENGAGED))
                asset = mission.asset_outcomes['b1']
                self.assertEqual(asset.end_reason, AssetEndReason.DISENGAGED)
                self.assertAlmostEqual(asset.end_time, calls[0][2].t_end, delta=1e-9)
                self.assertFalse(self._met(calls, 'r2'))
                self.assertEqual(scheduler.call_args.kwargs['legs']['b1'][-1].p_end, (0.0, -10_000.0, 0.0))
                self.assertEqual(outcome.postures['b1'], MA.PARKED_POSTURE)

    def _assert_exit(self, outcome, calls, scheduler, t_r, reason, abort):
        """Uscita di scena (G4b, `G4_OFF_SCENE_EXIT`): ritroso da `t_r` fino al punto di comparsa (0, 0, 1000) alla
        crociera, nessuna sosta dopo (presenza finita), postura `off_scene`, nessun contatto dopo l'uscita, r2 mai
        incontrato, motivo dell'esito quello del rientro all'istante della decisione."""
        legs = scheduler.call_args.kwargs['legs']['b1']
        exit_time = 2.0 * t_r      # andata e ritorno alla stessa velocita' (200 m/s)
        self.assertEqual(legs[-1].p_end, (0.0, 0.0, 1_000.0))
        self.assertNotEqual(legs[-1].p_start, legs[-1].p_end)          # nessuna sosta: non atterra
        self.assertAlmostEqual(legs[-1].t_end, exit_time, delta=1e-6)
        self.assertAlmostEqual(legs[0].t_end, t_r, delta=1e-6)
        self.assertFalse(any(w.t_end > exit_time + 1e-6 for args, _, _ in calls for w in args[2]
                             if 'b1' in (w.asset_a_id, w.asset_b_id)))
        self.assertFalse(self._met(calls, 'r2'))
        self.assertFalse(any(s.shooter_id == 'b1' and s.t_launch > t_r + 1e-9 for _, _, result in calls
                             for s in result.salvos))
        self.assertEqual(outcome.postures['b1'], MA.OFF_SCENE_POSTURE)
        mission = outcome.mission_outcomes['M-b1']
        self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, abort))
        asset = mission.asset_outcomes['b1']
        self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, reason))
        self.assertAlmostEqual(asset.end_time, t_r, delta=1e-9)
        self.assertIsNone(asset.crew_recovered)

    def test_disengaged_without_a_base_exits_at_the_appearance_point(self):
        """Partenza in volo senza basi del lato, forza disingaggiata nel primo episodio (decisione dell'utente del
        2026-10-17): al posto di NO_BASE l'aereo ripercorre la rotta a ritroso fino al punto di comparsa e li' esce
        di scena; ABORTED(DISENGAGED). Il ritroso consuma alla crociera."""
        outcome, b1, calls, scheduler, decisions = self._flight(fuel=1.0, base=None, spy=self._disengage_first)
        t_r = calls[0][2].t_end
        self.assertEqual(decisions.call_args.kwargs.get('exit_scene'), True)
        self._assert_exit(outcome, calls, scheduler, t_r, AssetEndReason.DISENGAGED, AbortReason.DISENGAGED)
        self.assertAlmostEqual(b1.fuel, 1.0 - self.CHARGE - 2.0 * 200.0 * t_r / AUTONOMY['nominal'], delta=1e-9)
        self.assertFalse(b1.is_destroyed())

    def test_bingo_after_the_episode_without_a_base_exits(self):
        """Come `test_bingo_after_the_episode_returns_and_never_meets_the_threat_ahead` senza basi: bingo dopo il
        consumo d'ingaggio, ritroso fino al punto di comparsa e uscita di scena, ABORTED(BINGO)."""
        outcome, b1, calls, scheduler, _ = self._flight(base=None, fire=self._miss)
        t_r = calls[0][2].t_end
        self._assert_exit(outcome, calls, scheduler, t_r, AssetEndReason.BINGO, AbortReason.BINGO)
        self.assertAlmostEqual(b1.fuel, 0.30 - self.CHARGE - 2.0 * 200.0 * t_r / AUTONOMY['nominal'], delta=1e-9)
        self.assertFalse(any(e.exhausted for e in outcome.fuel_events))

    def test_exit_with_an_insufficient_residual_is_a_loss(self):
        """Residuo a fine episodio pari a meta' del ritroso: a secco a meta' strada, nessuna base in planata
        (regole della F6-A): perso, DESTROYED/FUEL_EXHAUSTED con l'equipaggio recuperato. Alla partenza (G2) la
        soglia scatta ma senza basi nessun rientro (NO_BASE, invariato)."""
        _, _, calls, _, _ = self._flight(base=None, fire=self._miss)
        t_r = calls[0][2].t_end
        leg = 200.0 * t_r / AUTONOMY['nominal']
        outcome, b1, calls, scheduler, decisions = self._flight(fuel=self.CHARGE + 1.5 * leg, base=None,
                                                                fire=self._miss)
        self.assertAlmostEqual(calls[0][2].t_end, t_r, delta=1e-9)
        self.assertEqual(decisions.call_args_list[0].kwargs.get('exit_scene', False), False)    # G2: invariato
        asset = outcome.mission_outcomes['M-b1'].asset_outcomes['b1']
        self.assertEqual((asset.state, asset.end_reason, asset.crew_recovered),
                         (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, True))
        self.assertAlmostEqual(asset.end_time, 1.5 * t_r, delta=1e-6)
        self.assertAlmostEqual(scheduler.call_args.kwargs['legs']['b1'][-1].t_end, 1.5 * t_r, delta=1e-6)
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.DESTROYED)
        self.assertTrue(b1.is_destroyed())
        self.assertEqual(outcome.postures['b1'], MA.DESTROYED_POSTURE)
        self.assertFalse(self._met(calls, 'r2'))

    def test_exit_switch_off_stays_passive_on_its_route(self):
        """`G4_OFF_SCENE_EXIT` spento (il G4b fino al 2026-10-17): nessun rientro possibile (NO_BASE), passivo
        sulla rotta (incontra r2 senza sparare), nessun motivo nuovo."""
        outcome, b1, calls, scheduler, _ = self._flight(fuel=1.0, base=None, spy=self._disengage_first,
                                                        exit_scene=False)
        self.assertEqual(scheduler.call_count, 1)
        self.assertTrue(self._met(calls, 'r2'))
        self.assertFalse(any(s.shooter_id == 'b1' for s in calls[1][2].salvos))
        self.assertEqual(outcome.mission_outcomes['M-b1'].status, MissionStatus.COMPLETED)

    def test_exit_switch_is_on_and_without_effect_with_a_base_or_without_replan(self):
        """Con una base del lato (rientro sulla base) o con il G4b spento l'interruttore non cambia nulla (senza G4b
        e senza basi l'aereo finisce la rotta e la postura e' gia' `off_scene` per la F5-B)."""
        self.assertTrue(SS.G4_OFF_SCENE_EXIT)

        for kwargs in (dict(fuel=1.0, spy=self._disengage_first), dict(fire=self._miss),
                       dict(fuel=1.0, base=None, spy=self._disengage_first, replan=False),
                       dict(base=None, fire=self._miss, replan=False)):
            with self.subTest(**{k: v for k, v in kwargs.items() if k not in ('spy', 'fire')}):
                on = self._flight(**kwargs)[0]
                off = self._flight(exit_scene=False, **kwargs)[0]
                self.assertEqual(on, off)

    def test_ground_forces_are_not_replanned(self):
        """Terra: una colonna disingaggiata non e' ri-instradata (passiva sulla rotta, G4a): nessun nuovo
        scheduling, esito identico a G4b spento."""
        def run(replan):
            blue = _force('Blue', 'Blue', [_asset(Vehicle, 'v1', 0.0, 0.0, speed=10.0)])
            red = _force('Red', 'Red', [_asset(Vehicle, 'r1', 0.0, 2_000.0), _asset(Vehicle, 'r2', 0.0, 20_000.0)])
            mission = _ground_mission('M-v1', blue, _ground_route([(0.0, 0.0), (0.0, 30_000.0)], 10.0, 'g-v1'), 'v1')

            def resolve(*args, **kwargs):
                result = ER_resolve(*args, **kwargs)

                if result is None:
                    return result

                forces = tuple(dataclasses.replace(o, outcome=ER.DISENGAGED, time=o.time or result.t_start)
                               if o.force_id == 'M-v1' else o for o in result.forces)
                return dataclasses.replace(result, forces=forces)

            with patch.object(SS, 'G4_REPLAN', replan), patch.object(SS.ER, 'resolve_engagement', side_effect=resolve), \
                    patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
                outcome = SS.run_session(self._order('S-g4b-ground', (mission,)), [blue], [red], _fire,
                                         reaction_profile_for=_profile)

            return outcome, scheduler.call_count

        ER_resolve = ER.resolve_engagement
        on, calls_on = run(True)
        off, _ = run(False)
        self.assertEqual(calls_on, 1)
        self.assertEqual(on, off)
        self.assertGreater(len(on.engagement_outcomes), 0)

    def test_deterministic(self):
        first = self._flight()[0]
        second = self._flight()[0]
        self.assertEqual(first, second)


class TestSessionBlocks(unittest.TestCase):
    """`session_blocks` (F8a): blocchi per id di dominio."""

    def setUp(self):
        patchers = [patch(target, MagicMock()) for target in _LOGGERS]
        for p in patchers:
            p.start()
        self._patchers = patchers

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    def test_returns_blocks_by_id(self):
        """Restituisce i blocchi in un dict chiave=id dominio."""
        a1 = _asset(Aircraft, 'a1', 0, 0, 500.0)
        blue = _force('Blue', 'Blue', [a1])
        r1 = _asset(Vehicle, 'r1', 10000, -10000, 500.0)
        red = _force('Red', 'Red', [r1])

        order = SessionOrder('S', t_start=0.0, t_end=3600.0)
        blocks = SS.session_blocks(order, [blue], [red])
        self.assertEqual(set(blocks), {'Blue', 'Red'})
        self.assertIs(blocks['Blue'], blue)
        self.assertIs(blocks['Red'], red)

    def test_force_not_in_force_ids_raises(self):
        a1 = _asset(Aircraft, 'a1', 0, 0, 500.0)
        blue = _force('Blue', 'Blue', [a1])

        order = SessionOrder('S', t_start=0.0, t_end=3600.0, force_ids=['Red'])
        with self.assertRaises(ValueError):
            SS.session_blocks(order, [blue], [])


class TestMissionBeyondSessionWarning(_Base):
    """Warning E4 in `run_session` (F8a)."""

    def setUp(self):
        # Mocka tutti i logger TRANNE Session_Simulator (serve il logger reale per assertLogs).
        ss_logger = _SOURCE + 'Logic.Session_Simulator.logger'
        self._patches = [patch(target, MagicMock()) for target in _LOGGERS if target != ss_logger]
        for p in self._patches:
            p.start()

    def test_mission_beyond_session_end_produces_warning(self):
        """Una missione pianificata oltre la fine emette un warning."""
        blue, red, missions = self._scenario()
        # Sessione corta: 100 s, la missione M-north finisce a 200 s.
        order = self._order('S-warn', missions, t_end=100.0)
        with self.assertLogs(_SOURCE + 'Logic.Session_Simulator', level='WARNING') as log:
            SS.run_session(order, blue, red, _fire, reaction_profile_for=_profile)
        warnings = [r for r in log.records if 'is planned to end' in r.getMessage()]
        self.assertTrue(warnings, "Expected at least one warning for a mission beyond session end")
        # La missione e' ancora FAILED (comportamento invariato).
        self.assertIn('planned to end at t=200.0', warnings[0].getMessage())
