"""Tests per Command/Session_Types — contratto SessionOrder/SessionOutcome (Fase 0 + Fase 5).

Gli `EngagementResult` sono costruiti a mano (eventi con tempi scelti) per verificare
l'aggregazione in isolamento; una classe finale ripete il giro con `resolve_engagement`
reale seedato da `SessionOrder.rng`, per verificare che i pezzi si incastrino.
"""

import unittest
from unittest.mock import MagicMock, patch

from Code.Dynamic_War_Manager.Source.Command import Session_Types as ST
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fuel_Model import FuelEvent
from Code.Dynamic_War_Manager.Source.Utility import Session_Rng as SR

_ST_LOGGER = 'Code.Dynamic_War_Manager.Source.Command.Session_Types.logger'


def _force(force_id, side='Blue', committed=2, lost=0):
    return ER.ForceOutcome(force_id=force_id, side=side, outcome=ER.HELD, time=None, triggers=(),
                           committed=committed, lost=lost, erosion=lost / committed, max_shock=0.0)


def _damage(time, target, delta=-10, before=100):
    return DM.DamageEvent(time=time, target_id=target, outcome=DM.DAMAGE, health_before=before,
                          health_delta=delta, health_after=before + delta, destroyed=False)


def _ammo(time, asset, rounds=1):
    return ER.AmmunitionEvent(time=time, asset_id=asset, rounds=rounds)


def _intercept(time, asset, interceptions=1, force='red'):
    return ER.InterceptionEvent(time=time, asset_id=asset, interceptions=interceptions, force_id=force)


def _fuel(time, asset, amount=0.1):
    return FuelEvent(time=time, asset_id=asset, distance=1000.0, distance_covered=1000.0,
                     amount=amount, fuel_before=1.0, fuel_after=1.0 - amount, exhausted=False)


def _result(t_start, t_end, forces, damage=(), ammo=(), intercepts=()):
    return ER.EngagementResult(t_start=t_start, t_end=t_end, forces=tuple(forces),
                               damage_events=tuple(damage), ammunition_events=tuple(ammo),
                               interception_events=tuple(intercepts))


class _Base(unittest.TestCase):
    def setUp(self):
        self._log = patch(_ST_LOGGER, MagicMock())
        self.logger = self._log.start()

    def tearDown(self):
        self._log.stop()


# ── SessionOrder ──────────────────────────────────────────────────────────────

class TestSessionOrder(_Base):

    def test_minimal_order(self):
        order = ST.SessionOrder('S1')
        self.assertEqual(order.session_id, 'S1')
        self.assertEqual(order.t_start, 0.0)
        self.assertIsNone(order.t_end)
        self.assertEqual(order.force_ids, ())
        self.assertIsNone(order.committed)
        self.assertIsNone(order.committed_map())

    def test_committed_is_normalized_and_immutable(self):
        order = ST.SessionOrder('S1', force_ids=['blue', 'red'], committed={'blue': ['b1', 'b2']})
        self.assertEqual(order.force_ids, ('blue', 'red'))
        self.assertEqual(order.committed_map(), {'blue': ('b1', 'b2')})

        with self.assertRaises(TypeError):
            order.committed['red'] = ('r1',)
        with self.assertRaises(Exception):
            order.session_id = 'S2'

    def test_order_is_hashable_and_comparable(self):
        a = ST.SessionOrder('S1', force_ids=('blue',), committed={'blue': ['b1']})
        b = ST.SessionOrder('S1', force_ids=('blue',), committed={'blue': ('b1',)})
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_rng_is_rooted_in_the_session_id(self):
        order = ST.SessionOrder('S1')
        self.assertEqual(order.rng('M1', 'E1', 3).random(), SR.session_rng('S1', 'M1', 'E1', 3).random())
        self.assertNotEqual(order.rng('M1', 'E1', 0).random(),
                            ST.SessionOrder('S2').rng('M1', 'E1', 0).random())

    def test_validation(self):
        with self.assertRaises(TypeError):
            ST.SessionOrder('')
        with self.assertRaises(TypeError):
            ST.SessionOrder(42)
        with self.assertRaises(ValueError):
            ST.SessionOrder('S1', t_start=100.0, t_end=50.0)
        with self.assertRaises(ValueError):
            ST.SessionOrder('S1', force_ids=('blue', 'blue'))
        with self.assertRaises(ValueError):
            ST.SessionOrder('S1', force_ids=('blue',), committed={'red': ('r1',)})
        with self.assertRaises(TypeError):
            ST.SessionOrder('S1', committed={'blue': 'b1'})
        with self.assertRaises(ValueError):
            ST.SessionOrder('S1', salvo_window=-1.0)
        with self.assertRaises(TypeError):
            ST.SessionOrder('S1', t_start=None)


# ── assemble_session_outcome ──────────────────────────────────────────────────

class TestAssembleSessionOutcome(_Base):

    def test_empty_session_is_a_valid_outcome(self):
        outcome = ST.assemble_session_outcome('S1', [])
        self.assertEqual(outcome.session_id, 'S1')
        self.assertIsNone(outcome.t_start)
        self.assertIsNone(outcome.t_end)
        self.assertEqual(outcome.force_outcomes, ())
        self.assertEqual(outcome.damage_events, ())

    def test_declared_interval_is_kept_when_empty(self):
        outcome = ST.assemble_session_outcome('S1', [], t_start=0.0, t_end=7200.0)
        self.assertEqual((outcome.t_start, outcome.t_end), (0.0, 7200.0))

    def test_aggregates_several_engagements(self):
        e1 = _result(100.0, 200.0, [_force('blue'), _force('red', 'Red')],
                     damage=[_damage(150.0, 'r1')], ammo=[_ammo(140.0, 'b1', 2)],
                     intercepts=[_intercept(180.0, 'r2', 2)])
        e2 = _result(50.0, 300.0, [_force('blue'), _force('green', 'Red')],
                     damage=[_damage(60.0, 'g1'), _damage(250.0, 'b2')], ammo=[_ammo(55.0, 'g1', 3)],
                     intercepts=[_intercept(70.0, 'b2', 1, 'blue')])
        outcome = ST.assemble_session_outcome('S1', [e1, e2], fuel_events=[_fuel(400.0, 'b1')])

        self.assertEqual(len(outcome.engagement_outcomes), 2)
        self.assertEqual([o.force_id for o in outcome.force_outcomes], ['blue', 'red', 'blue', 'green'])
        self.assertEqual(len(outcome.outcomes_of('blue')), 2)
        self.assertEqual(outcome.outcomes_of('nobody'), ())

        self.assertEqual([e.time for e in outcome.damage_events], [60.0, 150.0, 250.0])
        self.assertEqual([e.time for e in outcome.ammunition_events], [55.0, 140.0])
        # ammunition_consumed() conta solo le salve; le intercettazioni a parte (2026-09-23).
        self.assertEqual(outcome.ammunition_consumed(), {'b1': 2, 'g1': 3})
        self.assertEqual([e.time for e in outcome.interception_events], [70.0, 180.0])
        self.assertEqual(outcome.interceptions_consumed(), {'r2': 2, 'b2': 1})
        self.assertAlmostEqual(outcome.fuel_consumed()['b1'], 0.1)

        # Intervallo ricavato: min/max su ingaggi ed eventi (il carburante a 400 s incluso).
        self.assertEqual((outcome.t_start, outcome.t_end), (50.0, 400.0))

    def test_sort_is_stable_on_ties(self):
        """A parita' di istante: ordine interno dell'ingaggio, poi ordine degli ingaggi."""
        e1 = _result(0.0, 10.0, [_force('blue')],
                     damage=[_damage(10.0, 'x', -5), _damage(10.0, 'x', -7, before=95)])
        e2 = _result(0.0, 10.0, [_force('red', 'Red')], damage=[_damage(10.0, 'y', -1)])
        outcome = ST.assemble_session_outcome('S1', [e1, e2])

        self.assertEqual([(e.target_id, e.health_delta) for e in outcome.damage_events],
                         [('x', -5), ('x', -7), ('y', -1)])

    def test_same_input_same_output(self):
        results = [_result(0.0, 20.0, [_force('blue')], damage=[_damage(5.0, 'r1')])]
        self.assertEqual(ST.assemble_session_outcome('S1', results, [_fuel(1.0, 'b1')]),
                         ST.assemble_session_outcome('S1', results, [_fuel(1.0, 'b1')]))

    def test_none_results_are_skipped(self):
        outcome = ST.assemble_session_outcome('S1', [None, _result(0.0, 1.0, [_force('blue')]), None])
        self.assertEqual(len(outcome.engagement_outcomes), 1)

    def test_interceptions_count_in_the_interval_and_sort_stably(self):
        e1 = _result(0.0, 10.0, [_force('red', 'Red')],
                     intercepts=[_intercept(10.0, 'r1', 1), _intercept(10.0, 'r2', 2)])
        e2 = _result(0.0, 5.0, [_force('red', 'Red')], intercepts=[_intercept(5.0, 'r3', 1)])
        outcome = ST.assemble_session_outcome('S1', [e1, e2])

        self.assertEqual([e.asset_id for e in outcome.interception_events], ['r3', 'r1', 'r2'])
        self.assertEqual(outcome.ammunition_consumed(), {})

        late = _result(0.0, 1.0, [_force('red', 'Red')], intercepts=[_intercept(30.0, 'r1')])
        with self.assertRaises(ValueError):
            ST.assemble_session_outcome('S1', [late], t_end=20.0)

    def test_events_outside_declared_interval_raise(self):
        results = [_result(10.0, 20.0, [_force('blue')], damage=[_damage(15.0, 'r1')])]
        with self.assertRaises(ValueError):
            ST.assemble_session_outcome('S1', results, t_start=12.0)
        with self.assertRaises(ValueError):
            ST.assemble_session_outcome('S1', results, t_end=18.0)
        with self.assertRaises(ValueError):
            ST.assemble_session_outcome('S1', [], fuel_events=[_fuel(99.0, 'b1')], t_end=50.0)

        outcome = ST.assemble_session_outcome('S1', results, t_start=0.0, t_end=7200.0)
        self.assertEqual((outcome.t_start, outcome.t_end), (0.0, 7200.0))

    def test_wrong_types_raise(self):
        with self.assertRaises(TypeError):
            ST.assemble_session_outcome('S1', [object()])
        with self.assertRaises(TypeError):
            ST.assemble_session_outcome('S1', [], fuel_events=[_ammo(1.0, 'b1')])
        with self.assertRaises(TypeError):
            ST.assemble_session_outcome('', [])
        with self.assertRaises(ValueError):
            ST.assemble_session_outcome('S1', [], t_start=10.0, t_end=5.0)

    def test_shared_target_across_engagements_is_warned(self):
        e1 = _result(0.0, 10.0, [_force('blue')], damage=[_damage(5.0, 'r1')])
        e2 = _result(0.0, 10.0, [_force('green')], damage=[_damage(6.0, 'r1')])
        ST.assemble_session_outcome('S1', [e1, e2])
        self.logger.warning.assert_called_once()

    def test_no_warning_for_disjoint_targets(self):
        e1 = _result(0.0, 10.0, [_force('blue')], damage=[_damage(5.0, 'r1'), _damage(6.0, 'r1')])
        e2 = _result(0.0, 10.0, [_force('green')], damage=[_damage(6.0, 'r2')])
        ST.assemble_session_outcome('S1', [e1, e2])
        self.logger.warning.assert_not_called()

    def test_outcome_is_immutable(self):
        outcome = ST.assemble_session_outcome('S1', [])
        with self.assertRaises(Exception):
            outcome.session_id = 'S2'


class TestSessionOutcomeContract(_Base):
    """Il contenitore stesso: validazione minima e nessun tipo duplicato."""

    def test_reuses_the_atomic_types(self):
        self.assertIs(ST.ForceOutcome, ER.ForceOutcome)
        self.assertIs(ST.AmmunitionEvent, ER.AmmunitionEvent)
        self.assertIs(ST.InterceptionEvent, ER.InterceptionEvent)
        self.assertIs(ST.DamageEvent, DM.DamageEvent)

    def test_direct_construction_validates_interval(self):
        with self.assertRaises(ValueError):
            ST.SessionOutcome('S1', t_start=10.0, t_end=0.0)
        with self.assertRaises(TypeError):
            ST.SessionOutcome('', t_start=None, t_end=None)


class TestEndToEndWithResolver(_Base):
    """SessionOrder -> rng seedato -> resolve_engagement x2 -> SessionOutcome, riproducibile."""

    def _run(self, session_id):
        from Code.Dynamic_War_Manager.Source.Context.Reaction_Profile import ReactionProfile
        from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import ContactWindow

        class _Asset:
            def __init__(self, asset_id):
                self.id, self.health, self.ammunition = asset_id, 100, 20

        class _Force:
            def __init__(self, name, side, ids):
                self.name, self.side = name, side
                self.assets = {i: _Asset(i) for i in ids}

        def windows(blue, red):
            return [ContactWindow(a, b, t_start=0.0, t_end=600.0, t_cpa=300.0, distance_cpa=400.0,
                                  range_a=1000.0, range_b=1000.0, t_mutual_start=0.0, t_mutual_end=600.0)
                    for a in blue for b in red]

        order = ST.SessionOrder(session_id, t_start=0.0, t_end=3600.0, force_ids=('blue', 'red', 'green'))
        spec = ER.ShotSpec(accuracy=0.6, destroy_capacity=0.4, rounds=2)
        profile = ReactionProfile(detection=3.0, evaluation=1.0, command=0.0, actuation=0.0)
        results = []

        for event_id, (blue_ids, other, other_ids) in enumerate(
                [(('b1', 'b2'), 'red', ('r1', 'r2')), (('b3',), 'green', ('g1',))]):
            results.append(ER.resolve_engagement(
                _Force('blue', 'Blue', blue_ids), _Force(other, 'Red', other_ids),
                windows(blue_ids, other_ids), lambda s, t: spec,
                order.rng(mission_id=None, event_id=event_id),
                committed=order.committed_map(), salvo_window=order.salvo_window,
                reaction_profile_for=lambda asset: profile))

        return ST.assemble_session_outcome(order.session_id, results, t_start=order.t_start,
                                           t_end=order.t_end)

    def test_same_session_id_reproduces_the_outcome(self):
        with patch('Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver.logger'):
            first, second = self._run('S-alpha'), self._run('S-alpha')

        self.assertEqual(first, second)
        self.assertGreater(len(first.damage_events), 0)
        self.assertEqual(len(first.engagement_outcomes), 2)
        self.assertEqual((first.t_start, first.t_end), (0.0, 3600.0))

    def test_different_session_id_changes_the_draws(self):
        with patch('Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver.logger'):
            self.assertNotEqual(self._run('S-alpha').damage_events, self._run('S-beta').damage_events)


if __name__ == '__main__':
    unittest.main()
