"""Tests per Context/Air_Defense_Efficacy — efficacia difensiva antiaerea (D4, 2026-09-29).

Verifica la grandezza E(N) (aerei abbattuti attesi, D4a) sui registri reali, la sua forma
(letalita' contro un aereo solo e saturazione sul numero di aerei), l'effetto della scorta
corrente, le correzioni per modello (D4c) e i pesi di minaccia per forze aeree (D4d) e di
superficie (D4e). Gli asset sono `Vehicle`/`Ship`/`Aircraft` reali costruiti con
`Scenario_Fixtures`, perche' la misura legge proprio i registri.
"""

import logging
import math
import unittest

from Code.Dynamic_War_Manager.Source.Context import Air_Defense_Efficacy as ADE
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F


class _Base:
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)
        cls.force = F.make_force('ADE-Test', 'Red')

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def vehicle(self, model):
        return F.make_vehicle(self.force, f'ADE-Test/{model}', model, (0.0, 0.0, 0.0))


class TestExpectedKills(_Base, unittest.TestCase):
    """E(N) = N (1 - prod (1 - p)^(K / N))."""

    def test_kub_is_less_effective_than_buk(self):
        """Il caso che ha motivato D4: un Kub non vale un Buk, ne' contro uno ne' contro molti."""
        kub, buk = self.vehicle('2K12-Kub'), self.vehicle('9K37-Buk')

        for n in (1, 2, 4, 8):
            with self.subTest(n=n):
                self.assertLess(ADE.air_defense_efficacy(kub, n), ADE.air_defense_efficacy(buk, n))

    def test_single_aircraft_is_the_single_target_lethality(self):
        buk = self.vehicle('9K37-Buk')
        weapon = ADE.air_defense_profile(buk).weapons[0]
        k = min(weapon.time_limited_engagements, weapon.full_stock)

        self.assertAlmostEqual(ADE.air_defense_efficacy(buk, 1), 1.0 - (1.0 - weapon.p) ** k)

    def test_monotone_bounded_and_saturating(self):
        tor = self.vehicle('9K331-Tor')
        values = [ADE.air_defense_efficacy(tor, n) for n in (1, 2, 4, 8, 64)]

        self.assertEqual(values, sorted(values))
        for n, value in zip((1, 2, 4, 8, 64), values):
            self.assertLessEqual(value, n)

        weapon = ADE.air_defense_profile(tor).weapons[0]
        k = min(weapon.time_limited_engagements, weapon.full_stock)
        # Per N grande tende a K x (-ln(1 - p)), il massimo abbattibile.
        self.assertLess(values[-1], k * -math.log1p(-weapon.p) + 1e-9)

    def test_zero_aircraft(self):
        self.assertEqual(ADE.air_defense_efficacy(self.vehicle('9K37-Buk'), 0), 0.0)

    def test_current_stock_limits_engagements(self):
        buk = self.vehicle('9K37-Buk')
        full = ADE.air_defense_efficacy(buk, 4)

        self.assertEqual(ADE.air_defense_efficacy(buk, 4, stock={'9M38-SAM': 0}), 0.0)
        self.assertLess(ADE.air_defense_efficacy(buk, 4, stock={'9M38-SAM': 1}), full)
        # Una voce assente dalla scorta passata usa la dotazione.
        self.assertAlmostEqual(ADE.air_defense_efficacy(buk, 4, stock={'altro': 3}), full)

    def test_guns_count_bursts(self):
        """Shilka: 2000 colpi = 40 raffiche, ma il tempo di esposizione ne consente meno."""
        weapon = ADE.air_defense_profile(self.vehicle('ZSU-23-4-Shilka')).weapons[0]
        from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import GUN_BURST_ROUNDS

        self.assertEqual(weapon.rounds_per_engagement, GUN_BURST_ROUNDS)
        self.assertEqual(weapon.full_stock, 2000)

    def test_ships_are_covered(self):
        ship = F.make_ship(self.force, 'ADE-Test/ship', 'FFG-46', (0.0, 0.0, 0.0))

        self.assertIsNotNone(ADE.air_defense_profile(ship))
        self.assertGreater(ADE.air_defense_efficacy(ship, 2), 0.0)

    def test_invalid_n_raises(self):
        profile = ADE.air_defense_profile(self.vehicle('9K37-Buk'))

        for bad in (-1, 1.5, True):
            with self.subTest(n=bad):
                with self.assertRaises(ValueError):
                    ADE.expected_kills(profile, bad)


class TestNotAirDefence(_Base, unittest.TestCase):

    def test_tank_has_no_profile(self):
        tank = self.vehicle('T-72B')

        self.assertIsNone(ADE.air_defense_profile(tank))
        self.assertIsNone(ADE.air_defense_efficacy(tank, 2))

    def test_unknown_model_and_stub(self):
        class _Stub:
            _model = 'nessun-modello'

        self.assertIsNone(ADE.air_defense_efficacy(_Stub(), 2))
        self.assertIsNone(ADE.air_defense_efficacy(object(), 2))


class TestCorrections(_Base, unittest.TestCase):
    """D4c: correzione per modello sulla p, per distinguere un sistema dalla sua classe."""

    def tearDown(self):
        ADE.EFFICACY_CORRECTIONS.pop('2K12-Kub', None)
        ADE.clear_cache()

    def test_correction_scales_p(self):
        kub = self.vehicle('2K12-Kub')
        base = ADE.air_defense_profile(kub).weapons[0].p

        ADE.EFFICACY_CORRECTIONS['2K12-Kub'] = 0.5
        ADE.clear_cache()

        self.assertAlmostEqual(ADE.air_defense_profile(kub).weapons[0].p, base * 0.5)


class TestThreatWeights(_Base, unittest.TestCase):

    def test_surface_weight(self):
        """D4e: SAM puri 0; AAA con impiego terrestre, mezzi da combattimento 1."""
        for model, expected in (('9K37-Buk', 0.0), ('2K12-Kub', 0.0), ('9K35-Strela-10', 0.0),
                                ('ZSU-23-4-Shilka', 1.0), ('2K22-Tunguska', 1.0), ('T-72B', 1.0)):
            with self.subTest(model=model):
                self.assertEqual(ADE.surface_threat_weight(self.vehicle(model)), expected)

    def test_surface_weight_of_aircraft(self):
        attacker = F.make_aircraft(self.force, 'ADE-Test/a10', 'A-10C Thunderbolt II', (0.0, 0.0, 3000.0))
        self.assertEqual(ADE.surface_threat_weight(attacker), 1.0)

        attacker.asset_type = 'Transport'
        self.assertEqual(ADE.surface_threat_weight(attacker), 0.0)

    def test_unknown_asset_counts_on_the_surface(self):
        self.assertEqual(ADE.surface_threat_weight(object()), 1.0)

    def test_air_weight(self):
        """D4d: AD = E(N), caccia 1, tutto il resto 0."""
        buk = self.vehicle('9K37-Buk')
        self.assertAlmostEqual(ADE.air_threat_weight(buk, 2), ADE.air_defense_efficacy(buk, 2))
        self.assertEqual(ADE.air_threat_weight(self.vehicle('T-72B'), 2), 0.0)

        fighter = F.make_aircraft(self.force, 'ADE-Test/f15', 'A-10C Thunderbolt II', (0.0, 0.0, 3000.0))
        fighter.asset_type = 'Fighter'
        self.assertEqual(ADE.air_threat_weight(fighter, 2), 1.0)
        fighter.asset_type = 'Attacker'
        self.assertEqual(ADE.air_threat_weight(fighter, 2), 0.0)


if __name__ == '__main__':
    unittest.main()
