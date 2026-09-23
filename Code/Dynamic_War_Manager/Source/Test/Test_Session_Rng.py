"""Tests per Utility/Session_Rng — RNG di sessione seedato (Fase 0 della roadmap DES).

Ogni classe verifica una clausola del contratto del modulo: determinismo, stabilita' fra
processi (niente `hash()` di Python), indipendenza empirica degli stream per chiavi diverse,
validazione della chiave, compatibilita' con `Engagement_Resolver.resolve_engagement`.

Le verifiche statistiche sono DETERMINISTICHE: gli stream sono seedati, quindi le soglie
non possono fallire a caso fra un'esecuzione e l'altra; sono dimensionate con ampio
margine rispetto alla deviazione standard attesa per stream indipendenti.
"""

import math
import os
import random
import subprocess
import sys
import unittest

from Code.Dynamic_War_Manager.Source.Utility import Session_Rng as SR

# Valore di riferimento calcolato una volta: se cambia, sono cambiati la codifica canonica
# o l'hash, e ogni sessione salvata smetterebbe di essere riproducibile.
_GOLDEN_KEY = ('S1', 'M1', 'E1', 0)
_GOLDEN_SEED = 6800766637189618860
_GOLDEN_FIRST_DRAW = 0.5065947952144855

_N = 2000


def _draws(rng, n=_N):
    return [rng.random() for _ in range(n)]


def _pearson(xs, ys):
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    return cov / math.sqrt(var_x * var_y)


class TestDeterminism(unittest.TestCase):
    """Stessa chiave -> stesso seed e stessa sequenza di estrazioni."""

    def test_same_key_same_seed(self):
        self.assertEqual(SR.session_seed(*_GOLDEN_KEY), SR.session_seed(*_GOLDEN_KEY))

    def test_same_key_same_sequence(self):
        self.assertEqual(_draws(SR.session_rng(*_GOLDEN_KEY)), _draws(SR.session_rng(*_GOLDEN_KEY)))

    def test_each_call_is_a_fresh_stream(self):
        """Consumare un'istanza non avanza l'altra: ogni chiamata riparte dall'inizio."""
        first = SR.session_rng(*_GOLDEN_KEY)
        _draws(first, 100)
        second = SR.session_rng(*_GOLDEN_KEY)
        self.assertEqual(second.random(), _GOLDEN_FIRST_DRAW)

    def test_golden_value(self):
        self.assertEqual(SR.session_seed(*_GOLDEN_KEY), _GOLDEN_SEED)
        self.assertEqual(SR.session_rng(*_GOLDEN_KEY).random(), _GOLDEN_FIRST_DRAW)

    def test_seed_fits_declared_bits(self):
        for counter in range(50):
            seed = SR.session_seed('S', 'M', 'E', counter)
            self.assertGreaterEqual(seed, 0)
            self.assertLess(seed, 2 ** SR.SEED_BITS)

    def test_stable_across_processes_with_different_hash_seeds(self):
        """Il seed non dipende da PYTHONHASHSEED: `hash()` non e' usato."""
        code = ("from Code.Dynamic_War_Manager.Source.Utility.Session_Rng import session_seed; "
                "print(session_seed('S1', 'M1', 'E1', 0))")
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 4)))

        for hash_seed in ('0', '4242'):
            env = dict(os.environ, PYTHONHASHSEED=hash_seed)
            out = subprocess.run([sys.executable, '-c', code], cwd=root, env=env,
                                 capture_output=True, text=True, check=True)
            self.assertEqual(int(out.stdout.strip().splitlines()[-1]), _GOLDEN_SEED)


class TestStreamIndependence(unittest.TestCase):
    """Chiavi diverse -> sequenze diverse e, empiricamente, indipendenti."""

    def test_different_counter_different_sequence(self):
        a = _draws(SR.session_rng('S1', 'M1', 'E1', 0))
        b = _draws(SR.session_rng('S1', 'M1', 'E1', 1))
        self.assertNotEqual(a, b)
        # Nessuna coincidenza posizionale: due stream sfasati o identici a tratti ne avrebbero.
        self.assertEqual(sum(1 for x, y in zip(a, b) if x == y), 0)

    def test_counter_streams_are_uncorrelated(self):
        """Correlazione di Pearson fra stream adiacenti: attesa ~0, dev. std ~1/sqrt(N) ~ 0.022."""
        base = _draws(SR.session_rng('S1', 'M1', 'E1', 0))

        for counter in (1, 2, 3, 10):
            other = _draws(SR.session_rng('S1', 'M1', 'E1', counter))
            self.assertLess(abs(_pearson(base, other)), 0.1, f"counter {counter}")

    def test_counter_streams_are_not_shifted_copies(self):
        """Uno stream non e' lo stesso di un altro spostato di qualche posizione."""
        a = _draws(SR.session_rng('S1', 'M1', 'E1', 0))
        b = _draws(SR.session_rng('S1', 'M1', 'E1', 1))

        for lag in range(1, 6):
            self.assertLess(abs(_pearson(a[lag:], b[:-lag])), 0.1, f"lag {lag}")
            self.assertLess(abs(_pearson(a[:-lag], b[lag:])), 0.1, f"lag {lag}")

    def test_first_draws_across_counters_are_uniform(self):
        """La prima estrazione di 2000 stream consecutivi e' uniforme in [0, 1) (10 classi)."""
        firsts = [SR.session_rng('S1', 'M1', 'E1', counter).random() for counter in range(_N)]
        bins = [0] * 10

        for value in firsts:
            bins[int(value * 10)] += 1

        expected = _N / 10
        chi2 = sum((count - expected) ** 2 / expected for count in bins)
        # 9 gradi di liberta': chi^2 critico al 99.9% = 27.9
        self.assertLess(chi2, 27.9)
        self.assertAlmostEqual(sum(firsts) / _N, 0.5, delta=0.03)

    def test_every_key_component_changes_the_seed(self):
        base = SR.session_seed('S1', 'M1', 'E1', 0)
        variants = [SR.session_seed('S2', 'M1', 'E1', 0), SR.session_seed('S1', 'M2', 'E1', 0),
                    SR.session_seed('S1', 'M1', 'E2', 0), SR.session_seed('S1', 'M1', 'E1', 1)]
        self.assertNotIn(base, variants)
        self.assertEqual(len(set(variants)), len(variants))

    def test_types_and_none_are_part_of_the_key(self):
        """'1' e 1, None e 'None' sono chiavi diverse; lo spostamento fra campi pure."""
        self.assertNotEqual(SR.session_seed('S', '1'), SR.session_seed('S', 1))
        self.assertNotEqual(SR.session_seed('S', None), SR.session_seed('S', 'None'))
        self.assertNotEqual(SR.session_seed('S', 'X', None), SR.session_seed('S', None, 'X'))


class TestKeyValidation(unittest.TestCase):
    """Chiave malformata = errore di programmazione: eccezione, non un seed a caso."""

    def test_session_id_required(self):
        with self.assertRaises(TypeError):
            SR.session_seed(None)
        with self.assertRaises(ValueError):
            SR.session_seed('')

    def test_bool_and_other_types_rejected(self):
        for bad in (True, 1.5, ('a',), b'S'):
            with self.assertRaises(TypeError):
                SR.session_seed('S', bad)

    def test_counter_validation(self):
        with self.assertRaises(ValueError):
            SR.session_seed('S', counter=-1)
        with self.assertRaises(TypeError):
            SR.session_seed('S', counter=1.0)
        with self.assertRaises(TypeError):
            SR.session_seed('S', counter=True)

    def test_int_ids_accepted(self):
        self.assertIsInstance(SR.session_seed(7, 3, 12, 0), int)

    def test_non_ascii_ids_accepted(self):
        self.assertEqual(SR.session_seed('sessione-è'), SR.session_seed('sessione-è'))


class TestEngagementResolverCompatibility(unittest.TestCase):
    """L'istanza e' un `rng` valido per resolve_engagement e ne rende l'esito riproducibile."""

    def test_is_a_random_instance_with_unit_interval_draws(self):
        rng = SR.session_rng('S1')
        self.assertIsInstance(rng, random.Random)
        self.assertTrue(all(0.0 <= value < 1.0 for value in _draws(rng, 500)))

    def test_same_key_reproduces_the_engagement(self):
        from unittest.mock import patch
        from Code.Dynamic_War_Manager.Source.Context.Reaction_Profile import ReactionProfile
        from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
        from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import ContactWindow

        class _Asset:
            def __init__(self, asset_id):
                self.id, self.health, self.ammunition = asset_id, 100, None

        class _Force:
            def __init__(self, name, side, ids):
                self.name, self.side = name, side
                self.assets = {i: _Asset(i) for i in ids}

        def run(counter):
            windows = [ContactWindow(a, b, t_start=0.0, t_end=300.0, t_cpa=150.0, distance_cpa=500.0,
                                     range_a=1000.0, range_b=1000.0, t_mutual_start=0.0,
                                     t_mutual_end=300.0)
                       for a in ('b1', 'b2', 'b3') for b in ('r1', 'r2', 'r3')]
            spec = ER.ShotSpec(accuracy=0.5, destroy_capacity=0.3, rounds=2)
            profile = ReactionProfile(detection=2.0, evaluation=1.0, command=0.0, actuation=0.0)
            return ER.resolve_engagement(_Force('blue', 'Blue', ('b1', 'b2', 'b3')),
                                         _Force('red', 'Red', ('r1', 'r2', 'r3')),
                                         windows, lambda s, t: spec,
                                         SR.session_rng('S1', 'M1', 'E1', counter),
                                         reaction_profile_for=lambda asset: profile)

        with patch('Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver.logger'):
            self.assertEqual(run(0), run(0))
            self.assertNotEqual(run(0).damage_events, run(1).damage_events)


if __name__ == '__main__':
    unittest.main()
