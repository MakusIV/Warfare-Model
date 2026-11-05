"""Test del blocco B (D-4b): i record EWR del nucleo e la normalizzazione globale del combat score.

Verifica i dati del registro `Vehicle_Data` (Proposta_Dati_Sensori_EWR_Visivo.md, §4.B):
  * gli 8 radar EWR mobili/semimobili sono registrati con la forma del sensore di sola scoperta aria;
  * `reliability` generica 45/4 (decisione 12, diversa dalla raccomandazione) dichiarata come STIMA;
  * `acquisition_profile` conservato come dato non letto, coerente con `acquisition_range`;
  * la categoria EWR e' esclusa dalla popolazione GLOBALE del solo combat score (decisione 9, G2):
    nessuno score globale dei modelli esistenti cambia;
  * come asset: combat power terra 0, rilevamento senza intercettazione, emettitore fuori dal
    catalogo RWR, e in sessione rileva senza mai sparare.

Il blocco C (Proposta_Dati_Sensori_EWR_Siti_Fissi.md) aggiunge i 7 siti fissi (marcatore `fixed_site`,
velocita' 0, autonomia segnaposto): record, punteggi e comportamento come asset in coda a questo file.

Nessuna unita' nuova nella fotografia: i blocchi B e C non istanziano EWR in nessuno scenario esistente.
"""

import copy
import unittest
from unittest.mock import patch, MagicMock

from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data, P18_Terek_data, MTLB_data
from Code.Dynamic_War_Manager.Source.Context import Air_Defense_Efficacy as ADE
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import radar_horizon_range, SENSOR_HEIGHT_EWR_M
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control, target_class
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD


_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data.logger"

# modello -> acquisition_range [km] (tabella di B.2).
EWR_MODELS = {
    'SCR-270': 160,
    'FuMG-80-Freya': 120,
    'P-12-Yenisei': 200,
    'P-18-Terek': 180,
    'P-37-Mech': 280,
    '1L13-Nebo-SV': 250,
    '55Zh6-Nebo': 400,
    'AN-TPS-43': 440,
}

# modello -> multi_target_capacity (0 = "non trovato"; solo il P-18 ha 10 [F]).
MULTI_TARGET = {'P-18-Terek': 10}

# modello -> acquisition_profile ((quota bersaglio [m], portata [km]), ...), dato di FONTE non letto.
ACQUISITION_PROFILES = {
    'SCR-270': ((305, 32), (1524, 80), (6096, 160), (7620, 180)),
    'P-18-Terek': ((500, 60), (10000, 180), (20000, 260)),
    '1L13-Nebo-SV': ((500, 50), (10000, 250), (27000, 330)),
    '55Zh6-Nebo': ((500, 65), (20000, 400)),
}

# modello -> quota di riferimento [m] alla quale la portata del profilo coincide con acquisition_range.
REFERENCE_QUOTAS = {
    'SCR-270': 6096,
    'P-18-Terek': 10000,
    '1L13-Nebo-SV': 10000,
    '55Zh6-Nebo': 20000,
}

# modello -> acquisition_range [km] dei siti fissi (blocco C, tabella C.3-b).
FIXED_SITE_MODELS = {
    'AN-FPS-117': 330,
    'Chain-Home': 160,
    'AMES-Type-7': 140,
    'AMES-Type-80': 390,
    'Wassermann': 190,
    'Mammut': 300,
    'P-14-Lena': 400,
}
FIXED_SITE_RELIABILITY = {'AN-FPS-117': {'mtbf': 2000, 'mttr': 0.75}}   # gli altri: 45/4 (decisione 12)
FIXED_SITE_PROFILES = {
    'AMES-Type-7': ((150, 16), (6100, 140)),
    'Wassermann': ((50, 35), (6000, 190)),
}
FIXED_SITE_REFERENCE_QUOTAS = {'AMES-Type-7': 6100, 'Wassermann': 6000}
FIXED_SITE_ANTENNA = {'Chain-Home': 73.0, 'AMES-Type-80': 11.4, 'Wassermann': 37.0}


class TestEWRRecords(unittest.TestCase):
    """Le 8 chiavi del registro EWR e la forma del loro sensore (B.4 test 1-8)."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_ewr_models_are_registered(self):
        for model in EWR_MODELS:
            with self.subTest(model=model):
                record = Vehicle_Data._registry[model]
                self.assertEqual(record.category, 'EWR')
                self.assertEqual(record.roles, ['EWR'])

    def test_ewr_radar_is_an_air_only_search_sensor(self):
        for model in EWR_MODELS:
            with self.subTest(model=model):
                caps = Vehicle_Data._registry[model].radar['capabilities']
                self.assertTrue(caps['air'][0])
                for mode in ('ground', 'sea'):
                    self.assertFalse(caps[mode][0], msg=mode)
                self.assertEqual(caps['air'][1]['tracking_range'], 0)
                self.assertEqual(caps['air'][1]['engagement_range'], 0)

    def test_acquisition_ranges_match_the_plan(self):
        for model, km in EWR_MODELS.items():
            with self.subTest(model=model):
                caps = Vehicle_Data._registry[model].radar['capabilities']
                self.assertEqual(caps['air'][1]['acquisition_range'], km)

    def test_multi_target_capacity(self):
        for model in EWR_MODELS:
            with self.subTest(model=model):
                caps = Vehicle_Data._registry[model].radar['capabilities']
                self.assertEqual(caps['air'][1]['multi_target_capacity'], MULTI_TARGET.get(model, 0))

    def test_ewr_have_no_weapons_and_no_other_sensor(self):
        for model in EWR_MODELS:
            with self.subTest(model=model):
                record = Vehicle_Data._registry[model]
                self.assertEqual(record.weapons, {})
                self.assertIs(record.TVD, False)
                # getattr cosi' il test vale anche prima del blocco A (campo `visual`).
                self.assertIsNone(getattr(record, 'visual', None))

    def test_reliability_is_the_declared_generic_estimate(self):
        """Decisione 12 (scelta dell'utente): reliability generica 45/4 per tutti e 8, dichiarata [S]."""
        for model in EWR_MODELS:
            with self.subTest(model=model):
                self.assertEqual(Vehicle_Data._registry[model].radar['reliability'],
                                 {'mtbf': 45, 'mttr': 4})

    def test_acquisition_profiles_are_consistent(self):
        """Quote e portate strettamente crescenti; alla quota di riferimento la portata = acquisition_range."""
        for model, profile in ACQUISITION_PROFILES.items():
            with self.subTest(model=model):
                quotes = [point[0] for point in profile]
                ranges = [point[1] for point in profile]
                self.assertEqual(quotes, sorted(quotes))
                self.assertEqual(ranges, sorted(ranges))
                self.assertEqual(len(set(quotes)), len(quotes))
                self.assertEqual(len(set(ranges)), len(ranges))
                ref = REFERENCE_QUOTAS[model]
                point = next(p for p in profile if p[0] == ref)
                self.assertEqual(point[1], EWR_MODELS[model])

    def test_scr270_antenna_height(self):
        self.assertEqual(Vehicle_Data._registry['SCR-270'].radar['antenna_height'], 16.8)
        for model in EWR_MODELS:
            if model == 'SCR-270':
                continue
            with self.subTest(model=model):
                self.assertNotIn('antenna_height', Vehicle_Data._registry[model].radar)


class TestEWRDoNotShiftTheCombatScores(unittest.TestCase):
    """G2: la categoria EWR non entra nella popolazione globale del combat score (B.4 test 9-11)."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_global_combat_population_excludes_ewr(self):
        t90 = Vehicle_Data._registry['T-90M']
        before = t90.get_normalized_combat_score()

        data = copy.deepcopy(P18_Terek_data)
        data['model'] = 'test-ewr-extreme'
        data['radar']['capabilities']['air'][1]['acquisition_range'] = 10000
        data['radar']['capabilities']['air'][1]['multi_target_capacity'] = 100

        try:
            Vehicle_Data(**data)
            # Il record estremo non tocca la popolazione globale: il valore di T-90M non cambia.
            self.assertAlmostEqual(t90.get_normalized_combat_score(), before)
        finally:
            Vehicle_Data._registry.pop('test-ewr-extreme', None)

    def test_ewr_global_combat_scores_in_unit_interval(self):
        for model in EWR_MODELS:
            with self.subTest(model=model):
                score = Vehicle_Data._registry[model].get_normalized_combat_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_global_combat_scores_of_existing_models_ignore_ewr(self):
        non_ewr = [ac for ac in Vehicle_Data._registry.values() if ac.category != 'EWR']
        scores = [ac._combat_eval() for ac in non_ewr]

        for ac in non_ewr:
            with self.subTest(model=ac.model):
                expected = ac._normalize(ac._combat_eval(), scores)
                self.assertAlmostEqual(ac.get_normalized_combat_score(), expected)


class TestEWRAsAssets(F.LoggerSilencer, unittest.TestCase):
    """Gli EWR come asset reali: potenza terra 0, rilevamento senza intercettazione, RWR, sessione (B.4 test 12-15)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.force = F.make_force('EWR-Test', 'Red')
        cls.p18 = F.make_vehicle(cls.force, 'EWR-Test/p18', 'P-18-Terek', (0.0, 0.0, 0.0))
        cls.scr270 = F.make_vehicle(cls.force, 'EWR-Test/scr270', 'SCR-270', (100.0, 0.0, 0.0))
        F.add_assets(cls.force, [cls.p18, cls.scr270])

    def test_ewr_vehicle_has_zero_ground_combat_power(self):
        self.assertTrue(self.p18.isEWR)
        self.p18.set_combat_power()
        ground = self.p18.combat_power(force='ground')
        self.assertTrue(ground)
        for action, value in ground.items():
            with self.subTest(action=action):
                self.assertEqual(value, 0)

    def test_ewr_gives_detection_without_interception(self):
        self.assertEqual(self.force.air_defense_threats(), [])

        high = {t.source_id: t for t in self.force.air_detection_threats(10000.0)}
        p18_high = high['EWR-Test/p18']
        self.assertEqual(p18_high.sensor, 'radar')
        self.assertEqual(p18_high.cylinder.radius, 180000.0)

        low = {t.source_id: t for t in self.force.air_detection_threats(500.0)}
        # A 500 m l'orizzonte (antenna EWR di default 20 m) taglia sotto i 180 km.
        self.assertEqual(low['EWR-Test/p18'].cylinder.radius, radar_horizon_range(SENSOR_HEIGHT_EWR_M, 500.0))
        # Lo SCR-270 usa l'antenna da fonte 16,8 m.
        self.assertEqual(low['EWR-Test/scr270'].cylinder.radius, radar_horizon_range(16.8, 500.0))

    def test_ewr_is_an_emitter_outside_the_rwr_catalogue(self):
        self.assertTrue(ADE.emits_radar(self.p18))
        self.assertIsNone(ADE.sam_category(self.p18))
        self.assertIsNone(ADE.air_defense_profile(self.p18))

        catalogue_models = {getattr(a, '_model', None) for a in ADE.default_rwr_catalogue()}
        self.assertTrue(catalogue_models.isdisjoint(set(EWR_MODELS)))

    def test_ewr_in_a_session_detects_and_never_fires(self):
        red = F.build_force('Red-EWR', 'Red', [
            F.Unit('vehicle', 'P-18-Terek', 1, origin=(0.0, 0.0), prefix='ewr')])
        cas = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', 'A-10C Thunderbolt II', 1, origin=(-100_000.0, 0.0, 3_000.0),
                   prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)

        fire_control = make_registry_fire_control()
        target = F.group_target('Red-EWR')
        missions = F.missions_for(cas, [(20_000.0, 0.0)], mission_type='CAS', target=target)

        outcome = F.run('EWR-detection-session', [cas], [red], fire_control, duration=1_800.0,
                        missions=missions, thresholds=BOTH_HOLD)

        ewr_id = 'Red-EWR/ewr0'
        self.assertFalse(any(e.asset_id == ewr_id for e in outcome.ammunition_events))


class TestEWRFixedSiteRecords(unittest.TestCase):
    """I 7 siti fissi del blocco C: record, marcatore `fixed_site`, velocita' 0, autonomia segnaposto (C.6 test 1-10)."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_fixed_sites_are_registered(self):
        for model in FIXED_SITE_MODELS:
            with self.subTest(model=model):
                record = Vehicle_Data._registry[model]
                self.assertEqual(record.category, 'EWR')
                self.assertEqual(record.roles, ['EWR'])
                self.assertIs(record.fixed_site, True)

    def test_only_the_fixed_sites_carry_the_marker(self):
        """Copre gli 8 EWR mobili e i record precedenti (default False)."""
        for model, record in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(record.fixed_site, bool)
                self.assertEqual(record.fixed_site, model in FIXED_SITE_MODELS)

    def test_fixed_sites_declare_zero_speed(self):
        for model, record in Vehicle_Data._registry.items():
            if not record.fixed_site:
                continue
            with self.subTest(model=model):
                for regime in ('sustained', 'max', 'off_road'):
                    self.assertEqual(record.speed_data[regime]['speed'], 0, msg=regime)
                    self.assertEqual(record.speed_data[regime]['metric'], 'metric', msg=regime)
                self.assertEqual(record._speed_eval(), 0.0)
                self.assertEqual(record.range, 1)   # SEGNAPOSTO di schema, non un'autonomia

    def test_fixed_site_radar_is_an_air_only_search_sensor(self):
        for model in FIXED_SITE_MODELS:
            with self.subTest(model=model):
                record = Vehicle_Data._registry[model]
                caps = record.radar['capabilities']
                self.assertTrue(caps['air'][0])
                for mode in ('ground', 'sea'):
                    self.assertFalse(caps[mode][0], msg=mode)
                for key in ('tracking_range', 'engagement_range', 'multi_target_capacity'):
                    self.assertEqual(caps['air'][1][key], 0, msg=key)
                self.assertEqual(record.weapons, {})
                self.assertIs(record.TVD, False)
                self.assertIsNone(record.visual)

    def test_fixed_site_acquisition_ranges_match_the_plan(self):
        for model, km in FIXED_SITE_MODELS.items():
            with self.subTest(model=model):
                caps = Vehicle_Data._registry[model].radar['capabilities']
                self.assertEqual(caps['air'][1]['acquisition_range'], km)

    def test_fixed_site_reliability(self):
        for model in FIXED_SITE_MODELS:
            with self.subTest(model=model):
                self.assertEqual(Vehicle_Data._registry[model].radar['reliability'],
                                 FIXED_SITE_RELIABILITY.get(model, {'mtbf': 45, 'mttr': 4}))

    def test_fixed_site_acquisition_profiles_are_consistent(self):
        for model in FIXED_SITE_MODELS:
            radar = Vehicle_Data._registry[model].radar
            with self.subTest(model=model):
                if model not in FIXED_SITE_PROFILES:
                    self.assertNotIn('acquisition_profile', radar)
                    continue
                profile = radar['acquisition_profile']
                self.assertEqual(profile, FIXED_SITE_PROFILES[model])
                quotes = [point[0] for point in profile]
                ranges = [point[1] for point in profile]
                self.assertEqual(quotes, sorted(quotes))
                self.assertEqual(ranges, sorted(ranges))
                self.assertEqual(len(set(quotes)), len(quotes))
                self.assertEqual(len(set(ranges)), len(ranges))
                ref = FIXED_SITE_REFERENCE_QUOTAS[model]
                point = next(p for p in profile if p[0] == ref)
                self.assertEqual(point[1], FIXED_SITE_MODELS[model])

    def test_fixed_site_antenna_heights(self):
        for model in FIXED_SITE_MODELS:
            radar = Vehicle_Data._registry[model].radar
            with self.subTest(model=model):
                if model in FIXED_SITE_ANTENNA:
                    self.assertEqual(radar['antenna_height'], FIXED_SITE_ANTENNA[model])
                else:
                    self.assertNotIn('antenna_height', radar)

    def test_constructor_defaults_fixed_site_to_false(self):
        data = copy.deepcopy(MTLB_data)
        data['model'] = 'test-fixed-default'
        try:
            record = Vehicle_Data(**data)
            self.assertIs(record.fixed_site, False)
        finally:
            Vehicle_Data._registry.pop('test-fixed-default', None)

    def test_constructor_rejects_a_non_bool_marker(self):
        data = copy.deepcopy(MTLB_data)
        data['model'] = 'test-fixed-invalid'
        data['fixed_site'] = 'yes'
        try:
            with self.assertRaises(ValueError):
                Vehicle_Data(**data)
            # La validazione precede la registrazione: il record invalido non entra nel registro.
            self.assertNotIn('test-fixed-invalid', Vehicle_Data._registry)
        finally:
            Vehicle_Data._registry.pop('test-fixed-invalid', None)


class TestEWRFixedSitesKeepTheCombatScores(unittest.TestCase):
    """I siti fissi non spostano il combat score globale (C.6 test 11)."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_fixed_site_global_combat_scores_in_unit_interval(self):
        # L'invarianza dei record esistenti e' coperta da test_global_combat_scores_of_existing_models_ignore_ewr,
        # che esclude per categoria e quindi copre anche i siti.
        for model in FIXED_SITE_MODELS:
            with self.subTest(model=model):
                score = Vehicle_Data._registry[model].get_normalized_combat_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestEWRFixedSitesAsAssets(F.LoggerSilencer, unittest.TestCase):
    """I siti fissi come asset reali: immobili, rilevamento senza intercettazione, RWR, sessione (C.6 test 12-15)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.force = F.make_force('EWR-Fixed', 'Red')
        cls.fps117 = F.make_vehicle(cls.force, 'EWR-Fixed/fps117', 'AN-FPS-117', (0.0, 0.0, 0.0))
        cls.chain_home = F.make_vehicle(cls.force, 'EWR-Fixed/ch', 'Chain-Home', (100.0, 0.0, 0.0))
        cls.type80 = F.make_vehicle(cls.force, 'EWR-Fixed/t80', 'AMES-Type-80', (200.0, 0.0, 0.0))
        F.add_assets(cls.force, [cls.fps117, cls.chain_home, cls.type80])

    def test_fixed_site_vehicle_does_not_move_or_burn_fuel(self):
        asset = self.fps117
        speed = asset.speed
        self.assertEqual(speed['nominal'], 0.0)
        self.assertEqual(speed['max'], 0.0)
        self.assertEqual(speed['off_road']['nominal'], 0.0)
        self.assertEqual(speed['off_road']['max'], 0.0)
        self.assertIsNone(FM.cruise_speed(asset))
        self.assertIsNone(FM.max_speed(asset))
        self.assertEqual(asset.fuel_autonomy(), 1000.0)
        self.assertEqual(asset.fuel, 1.0)
        self.assertTrue(asset.isEWR)
        asset.set_combat_power()
        ground = asset.combat_power(force='ground')
        self.assertTrue(ground)
        for action, value in ground.items():
            with self.subTest(action=action):
                self.assertEqual(value, 0)

    def test_fixed_site_gives_detection_without_interception(self):
        self.assertEqual(self.force.air_defense_threats(), [])

        high = {t.source_id: t for t in self.force.air_detection_threats(10000.0)}
        self.assertEqual(high['EWR-Fixed/fps117'].sensor, 'radar')
        self.assertEqual(high['EWR-Fixed/fps117'].cylinder.radius, 330000.0)

        low = {t.source_id: t for t in self.force.air_detection_threats(500.0)}
        # A 500 m l'orizzonte taglia la portata: antenna di default EWR (20 m) per l'FPS-117, da record per gli altri.
        self.assertEqual(low['EWR-Fixed/fps117'].cylinder.radius, radar_horizon_range(SENSOR_HEIGHT_EWR_M, 500.0))
        self.assertEqual(low['EWR-Fixed/ch'].cylinder.radius, radar_horizon_range(73.0, 500.0))
        self.assertEqual(low['EWR-Fixed/t80'].cylinder.radius, radar_horizon_range(11.4, 500.0))

    def test_fixed_site_is_an_air_defence_emitter_outside_the_rwr_catalogue(self):
        self.assertTrue(ADE.emits_radar(self.fps117))
        self.assertIsNone(ADE.sam_category(self.fps117))
        self.assertIsNone(ADE.air_defense_profile(self.fps117))
        self.assertEqual(target_class(self.fps117), Context.TARGET_CLASS_AIR_DEFENCE)

        catalogue_models = {getattr(a, '_model', None) for a in ADE.default_rwr_catalogue()}
        self.assertTrue(catalogue_models.isdisjoint(set(FIXED_SITE_MODELS)))

    def test_fixed_site_in_a_session_detects_and_never_fires(self):
        red = F.build_force('Red-EWR-Fixed', 'Red', [
            F.Unit('vehicle', 'AN-FPS-117', 1, origin=(0.0, 0.0), prefix='ewr')])
        cas = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', 'A-10C Thunderbolt II', 1, origin=(-100_000.0, 0.0, 3_000.0),
                   prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)

        fire_control = make_registry_fire_control()
        target = F.group_target('Red-EWR-Fixed')
        missions = F.missions_for(cas, [(20_000.0, 0.0)], mission_type='CAS', target=target)

        outcome = F.run('EWR-fixed-session', [cas], [red], fire_control, duration=1_800.0,
                        missions=missions, thresholds=BOTH_HOLD)

        site_id = 'Red-EWR-Fixed/ewr0'
        self.assertFalse(any(e.asset_id == site_id for e in outcome.ammunition_events))
        self.assertFalse(any(e.asset_id == site_id for e in outcome.fuel_events))


if __name__ == '__main__':
    unittest.main()
