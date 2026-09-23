"""Tests per Context/Reaction_Profile — latenze RIV/VAL/COM/ATT (Fase 4).

Cosa si verifica e perche':
* i TOTALI dei profili documentati sono esattamente quelli della tabella §4.2 del documento
  di architettura: sono l'unico dato con fonte, e una ripartizione in fasi sbagliata non
  deve mai spostarli;
* le grandezze derivate che il risolutore consuma (`total`, `refire_interval`) sono quelle
  dichiarate;
* l'associazione asset -> profilo segue la precedenza documentata, incluso il riuso di
  `Air_Route_Manager.threat_reaction_times` per i sistemi AD non documentati qui (una sola
  verita' sulla reattivita' di uno stesso sito);
* il ripiego non regala l'iniziativa (e' il totale piu' lento), e SKILL e' neutro.

Gli asset sono stub il cui NOME DI CLASSE e' quello interrogato (Vehicle/Aircraft/Ship non
sono importabili direttamente per il ciclo d'import noto del progetto).
"""

import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Context import Reaction_Profile as RP
from Code.Dynamic_War_Manager.Source.Context.Context import SKILL

_RP_LOGGER = 'Code.Dynamic_War_Manager.Source.Context.Reaction_Profile.logger'


class _Stub:
    def __init__(self, model=None, asset_type=None, category=None):
        self._model = model
        self.asset_type = asset_type
        self.category = category


class Vehicle(_Stub):
    pass


class Aircraft(_Stub):
    pass


class Ship(_Stub):
    pass


class TestReactionProfileType(unittest.TestCase):

    def test_total_is_the_sum_of_the_four_phases(self):
        profile = RP.ReactionProfile(detection=4.0, evaluation=0.1, command=0.1, actuation=0.01)
        self.assertAlmostEqual(profile.total, 4.21)

    def test_refire_interval_skips_detection(self):
        """Contro un bersaglio gia' in traccia non si rileva di nuovo."""
        profile = RP.ReactionProfile(detection=20.0, evaluation=1.0, command=0.5, actuation=0.5)
        self.assertAlmostEqual(profile.refire_interval, 2.0)

    def test_negative_phase_raises(self):
        with self.assertRaises(ValueError):
            RP.ReactionProfile(detection=-1.0, evaluation=1.0, command=0.0, actuation=0.0)

    def test_non_numeric_phase_raises(self):
        with self.assertRaises(TypeError):
            RP.ReactionProfile(detection='1', evaluation=1.0, command=0.0, actuation=0.0)

    def test_zero_refire_interval_raises(self):
        """Un intervallo di tiro nullo impedirebbe al risolutore a eventi di terminare."""
        with self.assertRaises(ValueError):
            RP.ReactionProfile(detection=5.0, evaluation=0.0, command=0.0, actuation=0.0)

    def test_scaled(self):
        profile = RP.ReactionProfile(detection=2.0, evaluation=1.0, command=1.0, actuation=0.0)
        self.assertAlmostEqual(profile.scaled(2.0).total, 8.0)
        self.assertIs(profile.scaled(1.0), profile)
        with self.assertRaises(ValueError):
            profile.scaled(0)

    def test_is_immutable(self):
        profile = RP.reaction_profile(RP.PILOT)
        with self.assertRaises(Exception):
            profile.detection = 3.0


class TestDocumentedTotals(unittest.TestCase):
    """I totali sono l'unico dato con fonte: la ripartizione non deve spostarli."""

    def test_osa(self):
        self.assertAlmostEqual(RP.reaction_profile('9A33-Osa').total, 26.0)

    def test_s300(self):
        self.assertAlmostEqual(RP.reaction_profile('S-300PS').total, 28.0)

    def test_tor_from_standstill_is_the_midpoint_of_5_8(self):
        self.assertAlmostEqual(RP.reaction_profile('9K331-Tor').total, 6.5)

    def test_tor_short_stop_is_the_midpoint_of_2_3(self):
        self.assertAlmostEqual(RP.reaction_profile(RP.TOR_SHORT_STOP).total, 2.5)

    def test_pilot_is_the_midpoint_of_1_2(self):
        self.assertAlmostEqual(RP.reaction_profile(RP.PILOT).total, 1.5)

    def test_tank_crew(self):
        self.assertAlmostEqual(RP.reaction_profile(RP.TANK_CREW).total, 31.0)

    def test_s300_evaluation_comes_from_the_documented_iads_figures(self):
        """VAL = valutazione minaccia (~1 s) + assegnazione arma-bersaglio (~0,3 s)."""
        self.assertAlmostEqual(RP.reaction_profile('S-300PS').evaluation, 1.3)

    def test_every_profile_has_non_negative_phases_and_a_source(self):
        for key, profile in RP.REACTION_PROFILES.items():
            with self.subTest(key=key):
                for phase in (profile.detection, profile.evaluation, profile.command, profile.actuation):
                    self.assertGreaterEqual(phase, 0.0)
                self.assertTrue(profile.source)

    def test_ordering_matches_the_sources(self):
        """Il pilota reagisce prima del Tor, che reagisce prima dell'Osa e dell'S-300."""
        pilot = RP.reaction_profile(RP.PILOT).total
        tor = RP.reaction_profile('9K331-Tor').total
        osa = RP.reaction_profile('9A33-Osa').total
        s300 = RP.reaction_profile('S-300PS').total
        self.assertLess(pilot, tor)
        self.assertLess(tor, osa)
        self.assertLess(osa, s300)

    def test_fallback_is_the_slowest_documented_total(self):
        """La mancanza di un dato non deve regalare l'iniziativa."""
        documented = [p.total for k, p in RP.REACTION_PROFILES.items() if k != RP.DEFAULT_PROFILE_KEY]
        self.assertAlmostEqual(RP.reaction_profile(RP.DEFAULT_PROFILE_KEY).total, max(documented))

    def test_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            RP.reaction_profile('nessuno')


class TestProfileForAsset(unittest.TestCase):

    def setUp(self):
        self._log = patch(_RP_LOGGER)
        self._log.start()

    def tearDown(self):
        self._log.stop()

    def test_documented_model_wins(self):
        asset = Vehicle(model='9A33-Osa', category='SAM_Small')
        self.assertEqual(RP.profile_for_asset(asset), RP.reaction_profile('9A33-Osa'))

    def test_aircraft_is_a_pilot(self):
        self.assertEqual(RP.profile_for_asset(Aircraft(model='F-16C')), RP.reaction_profile(RP.PILOT))

    def test_crewed_ground_vehicle_is_a_tank_crew(self):
        for kind in ('Tank', 'Armored', 'Motorized', 'Artillery_Semovent', 'Artillery_Fixed'):
            with self.subTest(kind=kind):
                self.assertEqual(RP.profile_for_asset(Vehicle(model='x', asset_type=kind)),
                                 RP.reaction_profile(RP.TANK_CREW))

    def test_undocumented_sam_reuses_the_threat_factory(self):
        """Buk non e' in tabella qui: RIV/ATT arrivano da threat_reaction_times (21 s + 6 s)."""
        from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import threat_reaction_times

        asset = Vehicle(model='9K37-Buk', category='SAM_Medium')
        detection, fire = threat_reaction_times(asset, has_missiles=True)
        profile = RP.profile_for_asset(asset)

        self.assertAlmostEqual(profile.detection, detection)
        self.assertAlmostEqual(profile.actuation, fire)
        self.assertAlmostEqual(profile.evaluation, RP.MACHINE_EVALUATION_S)

    def test_aaa_uses_the_gun_actuation(self):
        """AAA: nessuna sequenza di lancio, solo brandeggio (has_missiles=False)."""
        from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import GUN_LAUNCH_SEQUENCE_TIME_S

        profile = RP.profile_for_asset(Vehicle(model='ZSU-x', category='AAA'))
        self.assertAlmostEqual(profile.actuation, GUN_LAUNCH_SEQUENCE_TIME_S)

    def test_ship_falls_back_to_default(self):
        """Nessuna fonte del progetto documenta latenze navali."""
        self.assertEqual(RP.profile_for_asset(Ship(model='x')),
                         RP.reaction_profile(RP.DEFAULT_PROFILE_KEY))

    def test_unknown_class_falls_back_to_default(self):
        self.assertEqual(RP.profile_for_asset(_Stub()), RP.reaction_profile(RP.DEFAULT_PROFILE_KEY))

    def test_reaction_delay_is_the_total(self):
        self.assertAlmostEqual(RP.reaction_delay(Aircraft()), 1.5)


class TestSkill(unittest.TestCase):

    def test_skill_factors_are_neutral(self):
        """Nessuna fonte li fornisce: l'aggancio esiste ma non cambia nulla."""
        for skill in SKILL:
            with self.subTest(skill=skill):
                self.assertEqual(RP.profile_for_asset(Aircraft(), skill=skill),
                                 RP.reaction_profile(RP.PILOT))

    def test_skill_accepts_the_string_value(self):
        self.assertAlmostEqual(RP.profile_for_asset(Aircraft(), skill='Excellent').total, 1.5)

    def test_unknown_skill_raises(self):
        with self.assertRaises(ValueError):
            RP.profile_for_asset(Aircraft(), skill='Legendary')


if __name__ == '__main__':
    unittest.main()
