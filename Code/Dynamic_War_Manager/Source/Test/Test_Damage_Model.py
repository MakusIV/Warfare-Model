"""Tests per Logic/Damage_Model — semantica della perdita per singolo asset.

Verificano il contratto documentato nel modulo: scomposizione accuracy/destroy_capacity in
Ph e Pk|h, i tre esiti, l'accumulo, la soglia Destroyed lasciata a 15, l'assenza di
estrazioni casuali interne (il `draw` e' sempre del chiamante) e il ponte verso
`Asset.apply_damage`.

L'asset si costruisce reale (con un Block mock, come in Test_Asset.py): apply_damage
attraversa State.update(), ed e' proprio quell'attraversamento che va verificato.
"""

import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.State import StateCategory
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM


def _asset(health=100):
    block = MagicMock(spec=Block)
    block.isMilitary = True
    block.isLogistic = False
    block.isCivilian = False
    block.get_asset.return_value = None
    asset = Asset(block=block, name="Target", description="d", category="Military",
                  asset_type="Tank", functionality="Combat", cost=1, value=1,
                  position=Point3D(0, 0, 0))
    asset.health = health
    return asset


class TestOutcomeProbabilities(unittest.TestCase):

    def test_probabilities_sum_to_one(self):
        p = DM.hit_outcome_probabilities(0.8, 0.25)
        self.assertAlmostEqual(sum(p.values()), 1.0)

    def test_kill_is_accuracy_times_destroy_capacity(self):
        """La Pk del progetto (accuracy x destroy_capacity) e' preservata esattamente."""
        p = DM.hit_outcome_probabilities(0.8, 0.25)
        self.assertAlmostEqual(p[DM.KILL], 0.2)
        self.assertAlmostEqual(p[DM.DAMAGE], 0.6)
        self.assertAlmostEqual(p[DM.MISS], 0.2)

    def test_certain_kill(self):
        p = DM.hit_outcome_probabilities(1.0, 1.0)
        self.assertAlmostEqual(p[DM.KILL], 1.0)

    def test_certain_miss(self):
        p = DM.hit_outcome_probabilities(0.0, 1.0)
        self.assertAlmostEqual(p[DM.MISS], 1.0)

    def test_out_of_domain_raises(self):
        with self.assertRaises(ValueError):
            DM.hit_outcome_probabilities(1.5, 0.5)
        with self.assertRaises(ValueError):
            DM.hit_outcome_probabilities(0.5, -0.1)
        with self.assertRaises(TypeError):
            DM.hit_outcome_probabilities('0.5', 0.5)


class TestResolveHit(unittest.TestCase):

    def test_threshold_order_is_kill_damage_miss(self):
        self.assertEqual(DM.resolve_hit(0.8, 0.25, 0.0), DM.KILL)
        self.assertEqual(DM.resolve_hit(0.8, 0.25, 0.19), DM.KILL)
        self.assertEqual(DM.resolve_hit(0.8, 0.25, 0.21), DM.DAMAGE)
        self.assertEqual(DM.resolve_hit(0.8, 0.25, 0.79), DM.DAMAGE)
        self.assertEqual(DM.resolve_hit(0.8, 0.25, 0.81), DM.MISS)

    def test_is_deterministic_for_the_same_draw(self):
        outcomes = {DM.resolve_hit(0.7, 0.3, 0.42) for _ in range(20)}
        self.assertEqual(len(outcomes), 1)

    def test_bad_draw_raises(self):
        with self.assertRaises(ValueError):
            DM.resolve_hit(0.8, 0.25, 1.5)


class TestHealthDelta(unittest.TestCase):

    def test_miss_does_nothing(self):
        self.assertEqual(DM.health_delta_for_outcome(DM.MISS, 0.5, 100), 0)

    def test_kill_zeroes_health(self):
        self.assertEqual(DM.health_delta_for_outcome(DM.KILL, 0.5, 100), -100)
        self.assertEqual(DM.health_delta_for_outcome(DM.KILL, 0.5, 30), -30)

    def test_damage_scales_with_destroy_capacity(self):
        self.assertEqual(DM.health_delta_for_outcome(DM.DAMAGE, 0.5, 100), -50)
        self.assertEqual(DM.health_delta_for_outcome(DM.DAMAGE, 0.1, 100), -10)

    def test_damage_never_exceeds_residual_health(self):
        self.assertEqual(DM.health_delta_for_outcome(DM.DAMAGE, 0.9, 20), -20)

    def test_near_zero_destroy_capacity_still_does_one_point(self):
        """Senza il minimo, un bersaglio infrastrutturale sarebbe indistruttibile."""
        self.assertEqual(DM.health_delta_for_outcome(DM.DAMAGE, 1e-12, 100), -DM.MIN_EFFECTIVE_HIT_DAMAGE)

    def test_bad_outcome_raises(self):
        with self.assertRaises(ValueError):
            DM.health_delta_for_outcome('boom', 0.5, 100)

    def test_bad_health_raises(self):
        with self.assertRaises(ValueError):
            DM.health_delta_for_outcome(DM.DAMAGE, 0.5, 200)
        with self.assertRaises(TypeError):
            DM.health_delta_for_outcome(DM.DAMAGE, 0.5, 50.0)


class TestDestroyedThreshold(unittest.TestCase):

    def test_threshold_is_fifteen_and_comes_from_state(self):
        self.assertEqual(DM.DESTROYED_HEALTH, 15)

    def test_asset_at_threshold_is_destroyed_but_not_at_zero_health(self):
        asset = _asset(100)
        asset.apply_damage(-85)
        self.assertEqual(asset.health, 15)
        self.assertTrue(asset.is_destroyed())

    def test_asset_below_fifty_is_already_out_of_action(self):
        """Mission kill: non operativo ben prima di essere distrutto."""
        asset = _asset(100)
        asset.apply_damage(-60)
        self.assertEqual(asset.health, 40)
        self.assertFalse(asset.is_operative())
        self.assertFalse(asset.is_destroyed())
        self.assertEqual(asset.state.state_value, StateCategory.CRITICAL.value)


class TestApplyDamage(unittest.TestCase):

    def test_reduces_health_and_updates_state(self):
        asset = _asset(100)
        self.assertEqual(asset.apply_damage(-25), 75)
        self.assertEqual(asset.health, 75)
        self.assertEqual(asset.state.state_value, StateCategory.DAMAGED.value)

    def test_accumulates(self):
        asset = _asset(100)
        asset.apply_damage(-20)
        asset.apply_damage(-20)
        asset.apply_damage(-20)
        self.assertEqual(asset.health, 40)

    def test_saturates_at_zero(self):
        asset = _asset(10)
        self.assertEqual(asset.apply_damage(-999), 0)
        self.assertEqual(asset.health, 0)

    def test_zero_delta_is_allowed(self):
        asset = _asset(80)
        self.assertEqual(asset.apply_damage(0), 80)

    def test_positive_delta_raises(self):
        with self.assertRaises(ValueError):
            _asset(50).apply_damage(10)

    def test_non_int_delta_raises(self):
        with self.assertRaises(TypeError):
            _asset(50).apply_damage(-10.5)
        with self.assertRaises(TypeError):
            _asset(50).apply_damage(True)

    def test_missing_state_logs_and_returns_none(self):
        asset = _asset(50)
        asset._state = None
        with patch('Code.Dynamic_War_Manager.Source.Asset.Asset.logger') as mock_logger:
            self.assertIsNone(asset.apply_damage(-10))
            mock_logger.warning.assert_called_once()


class TestDamageEvent(unittest.TestCase):

    def test_build_does_not_mutate_the_asset(self):
        asset = _asset(100)
        event = DM.build_damage_event(asset, accuracy=1.0, destroy_capacity=1.0, draw=0.0)
        self.assertEqual(event.outcome, DM.KILL)
        self.assertEqual(asset.health, 100)

    def test_apply_mutates(self):
        asset = _asset(100)
        event = DM.build_damage_event(asset, accuracy=1.0, destroy_capacity=0.4, draw=0.99)
        self.assertEqual(event.outcome, DM.DAMAGE)
        self.assertEqual(event.health_delta, -40)
        self.assertEqual(DM.apply_damage_event(asset, event), 60)
        self.assertEqual(asset.health, 60)

    def test_kill_event_is_flagged_destroyed(self):
        asset = _asset(100)
        event = DM.build_damage_event(asset, accuracy=1.0, destroy_capacity=1.0, draw=0.0)
        self.assertTrue(event.destroyed)
        self.assertEqual(event.health_after, 0)

    def test_damage_event_below_threshold_is_flagged_destroyed(self):
        asset = _asset(20)
        event = DM.build_damage_event(asset, accuracy=1.0, destroy_capacity=0.1, draw=0.99)
        self.assertEqual(event.health_after, 10)
        self.assertTrue(event.destroyed)

    def test_miss_event_applies_nothing(self):
        asset = _asset(100)
        event = DM.build_damage_event(asset, accuracy=0.1, destroy_capacity=0.5, draw=0.99)
        self.assertEqual(event.outcome, DM.MISS)
        self.assertEqual(DM.apply_damage_event(asset, event), 100)

    def test_event_carries_domain_fields_only(self):
        asset = _asset(100)
        event = DM.build_damage_event(asset, accuracy=1.0, destroy_capacity=0.5, draw=0.99,
                                      time=123.5, source_id='blue-1', weapon='M256_120mm',
                                      provenance=DM.MEASURED)
        self.assertEqual(event.time, 123.5)
        self.assertEqual(event.source_id, 'blue-1')
        self.assertEqual(event.weapon, 'M256_120mm')
        self.assertEqual(event.provenance, DM.MEASURED)
        self.assertEqual(event.target_id, asset.id)

    def test_event_is_immutable(self):
        event = DM.build_damage_event(_asset(100), 1.0, 0.5, 0.99)
        with self.assertRaises(Exception):
            event.health_delta = -1

    def test_bad_provenance_raises(self):
        with self.assertRaises(ValueError):
            DM.build_damage_event(_asset(100), 1.0, 0.5, 0.99, provenance='inventato')

    def test_unreadable_health_returns_none(self):
        target = MagicMock()
        target.health = None
        with patch('Code.Dynamic_War_Manager.Source.Logic.Damage_Model.logger') as mock_logger:
            self.assertIsNone(DM.build_damage_event(target, 1.0, 0.5, 0.99))
            mock_logger.warning.assert_called_once()

    def test_apply_requires_a_damage_event(self):
        with self.assertRaises(TypeError):
            DM.apply_damage_event(_asset(100), 'not an event')

    def test_apply_on_asset_without_api_logs_and_returns_none(self):
        event = DM.build_damage_event(_asset(100), 1.0, 0.5, 0.99)
        target = MagicMock(spec=[])
        with patch('Code.Dynamic_War_Manager.Source.Logic.Damage_Model.logger') as mock_logger:
            self.assertIsNone(DM.apply_damage_event(target, event))
            mock_logger.warning.assert_called_once()


class TestAccumulationEmergesFromDestroyCapacity(unittest.TestCase):

    def test_number_of_non_lethal_hits_to_destroy(self):
        """~1/destroy_capacity colpi non letali mettono fuori uso il bersaglio."""
        asset = _asset(100)
        hits = 0

        while not asset.is_destroyed() and hits < 100:
            event = DM.build_damage_event(asset, accuracy=1.0, destroy_capacity=0.2, draw=0.99)
            DM.apply_damage_event(asset, event)
            hits += 1

        self.assertTrue(asset.is_destroyed())
        self.assertEqual(hits, 5)


if __name__ == '__main__':
    unittest.main()
