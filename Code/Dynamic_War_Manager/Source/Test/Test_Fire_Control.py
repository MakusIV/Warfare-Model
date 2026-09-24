"""Test di Logic/Fire_Control.py (B2) e delle righe aeree dei template d'efficacia (B1).

Asset REALI dei registri (`Scenario_Fixtures.make_vehicle/make_aircraft/make_ship`), mai
valori attesi calibrati: ogni valore atteso di una ShotSpec e' riletto dal template del
registro (`efficiency[classe][dimensione]`), cosi' il test verifica la CATENA di selezione
(classe del bersaglio, dimensione, filtri, scelta), non i numeri stimati della proposta.

Logger: silenziati con `Scenario_Fixtures.LoggerSilencer` (mixin, non un TestCase), che
copre anche `Logic.Fire_Control`.
"""

import unittest

from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Asset import Ground_Weapon_Data as GWD
from Code.Dynamic_War_Manager.Source.Asset import Ship_Weapon_Data as SWD
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Context import Context as C
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver import ShotSpec


AIR_KEYS = C.AIR_TARGET_CLASSES
DIMS = C.DIMENSION_CLASSES

GROUND_AIR_TEMPLATES = ('_EFF_SAM_SHORAD', '_EFF_SAM_MERAD', '_EFF_SAM_LORAD', '_EFF_AA_CANNON',
                        '_EFF_AA_CANNON_57MM', '_EFF_AUTOCANNON', '_EFF_HMG')
SHIP_AIR_TEMPLATES = ('_EFF_SAM_SHORAD', '_EFF_SAM_MERAD', '_EFF_SAM_LORAD', '_EFF_CIWS',
                      '_EFF_NAVAL_GUN_76MM', '_EFF_NAVAL_GUN_100MM', '_EFF_NAVAL_GUN_127MM',
                      '_EFF_NAVAL_GUN_130MM')

BUK, STRELA10, SHILKA, T72 = '9K37-Buk', '9K35-Strela-10', 'ZSU-23-4-Shilka', 'T-72B'
A10, F16, B52, SU24M, SU24MR, SU27, MIG25RB = ('A-10C Thunderbolt II', 'F-16C Block 52d', 'B-52H Stratofortress',
                                              'Su-24M', 'Su-24MR', 'Su-27', 'MiG-25RB')
BURKE = 'USS Arleigh Burke IIa'


def _cell(template, key, dim):
    return template[key][dim]['accuracy'], template[key][dim]['destroy_capacity']


# ── B1: righe aeree dei template ──────────────────────────────────────────────

class TestAirRowsInTemplates(unittest.TestCase):
    """Struttura e coerenze interne delle righe aeree (non i valori, che sono STIME)."""

    def _templates(self):
        for name in GROUND_AIR_TEMPLATES:
            yield f'GWD.{name}', getattr(GWD, name)
        for name in SHIP_AIR_TEMPLATES:
            yield f'SWD.{name}', getattr(SWD, name)

    def test_every_template_has_all_air_rows_in_range(self):
        for label, template in self._templates():
            for key in AIR_KEYS:
                for dim in DIMS:
                    with self.subTest(template=label, key=key, dim=dim):
                        accuracy, destroy_capacity = _cell(template, key, dim)
                        self.assertTrue(0.0 < accuracy <= 1.0)
                        self.assertTrue(0.0 < destroy_capacity <= 1.0)

    def test_attacker_never_more_vulnerable_than_fighter(self):
        for label, template in self._templates():
            for dim in DIMS:
                with self.subTest(template=label, dim=dim):
                    self.assertLessEqual(template['Aircraft_Attacker'][dim]['destroy_capacity'],
                                         template['Aircraft'][dim]['destroy_capacity'])
                    self.assertLessEqual(template['Helicopter_Attack'][dim]['destroy_capacity'],
                                         template['Helicopter'][dim]['destroy_capacity'])

    def test_heavy_same_resistance_easier_to_hit(self):
        """Decisione utente (b): dc Aircraft_Heavy = dc fighter, accuracy piu' alta."""
        for label, template in self._templates():
            for dim in DIMS:
                with self.subTest(template=label, dim=dim):
                    self.assertEqual(template['Aircraft_Heavy'][dim]['destroy_capacity'],
                                     template['Aircraft'][dim]['destroy_capacity'])
                    self.assertGreater(template['Aircraft_Heavy'][dim]['accuracy'],
                                       template['Aircraft'][dim]['accuracy'])

    def test_ground_rows_untouched(self):
        """Le righe terrestri preesistenti restano (es. Soft del cannone AA)."""
        self.assertEqual(GWD._EFF_AA_CANNON['Soft']['med'], {'accuracy': 0.9, 'destroy_capacity': 0.75})
        self.assertEqual(SWD._EFF_CIWS['ship']['big'], {'accuracy': 0.15, 'destroy_capacity': 0.02})

    def test_kpvt_inline_table_inherits_air_rows(self):
        kpvt = GWD.GROUND_WEAPONS['MACHINE_GUNS']['KPVT-14.5']['efficiency']
        for key in AIR_KEYS:
            self.assertEqual(kpvt[key], GWD._EFF_HMG[key])

    def test_ammo_target_effectiveness_untouched(self):
        for ammo in GWD.AMMO_TARGET_EFFECTIVENESS.values():
            self.assertFalse(set(AIR_KEYS) & set(ammo))


# ── B1: campi del registro aerei ──────────────────────────────────────────────

class TestRegistryAirTargetClass(F.LoggerSilencer, unittest.TestCase):

    def _cls(self, model):
        record = Aircraft_Data._registry[model]
        return C.get_air_target_class(record.category, record.ground_fire_armored, record.air_target_class)

    def test_armored_attackers(self):
        for model in ('A-10A Thunderbolt II', 'A-10C Thunderbolt II', 'A-10C II Thunderbolt II',
                      'Su-25', 'Su-25T', 'Su-25TM'):
            self.assertTrue(Aircraft_Data._registry[model].ground_fire_armored, model)
            self.assertEqual(self._cls(model), 'Aircraft_Attacker', model)

    def test_unarmored_attackers_are_fighters(self):
        for model in ('A-4E Skyhawk', 'A-20G Havoc'):
            self.assertFalse(Aircraft_Data._registry[model].ground_fire_armored)
            self.assertEqual(self._cls(model), 'Aircraft', model)

    def test_fighter_bombers_are_not_attackers(self):
        for model in ('F-16C Block 52d', 'F-16A Fighting Falcon', 'F-15E Strike Eagle', 'Su-34', 'F-4E Phantom II'):
            self.assertEqual(self._cls(model), 'Aircraft', model)

    def test_per_model_override(self):
        for model in (SU24M, SU24MR, MIG25RB):
            self.assertEqual(Aircraft_Data._registry[model].air_target_class, 'Aircraft')
            self.assertEqual(self._cls(model), 'Aircraft', model)

    def test_heavy(self):
        for model in (B52, 'E-3A Sentry', 'C-130 Hercules', 'MQ-9 Reaper', 'F-117 Nighthawk'):
            self.assertEqual(self._cls(model), 'Aircraft_Heavy', model)

    def test_only_expected_models_have_the_new_fields(self):
        armored = {m for m, r in Aircraft_Data._registry.items() if r.ground_fire_armored}
        overridden = {m for m, r in Aircraft_Data._registry.items() if r.air_target_class is not None}
        self.assertEqual(len(armored), 6)
        self.assertEqual(overridden, {SU24M, SU24MR, MIG25RB})

    def test_constructor_validation(self):
        """Valori non validi dei nuovi campi: eccezione PRIMA della registrazione del modello."""
        from Code.Dynamic_War_Manager.Source.Asset import Aircraft_Data as AD
        for field, value, error in (('air_target_class', 'Tank', ValueError),
                                    ('ground_fire_armored', 'yes', TypeError)):
            with self.subTest(field=field):
                data = dict(AD.f16_data_example, model='Test-Probe-Model', **{field: value})
                with self.assertRaises(error):
                    Aircraft_Data(**data)
                self.assertNotIn('Test-Probe-Model', Aircraft_Data._registry)

    def test_fields_default_when_absent(self):
        from Code.Dynamic_War_Manager.Source.Asset import Aircraft_Data as AD
        self.assertNotIn('ground_fire_armored', AD.f16_data_example)
        record = Aircraft_Data._registry[AD.f16_data_example['model']]
        self.assertFalse(record.ground_fire_armored)
        self.assertIsNone(record.air_target_class)


# ── B2: fire control ──────────────────────────────────────────────────────────

class _FireControlFixture(F.LoggerSilencer):
    """Mixin (NON un TestCase): forze e fire control condivisi."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fc = staticmethod(FC.make_registry_fire_control())  # funzione, non metodo
        cls.blue = F.make_force('Blue', 'Blue')
        cls.red = F.make_force('Red', 'Red')
        cls._n = 0

    @classmethod
    def vehicle(cls, model, z=0.0):
        cls._n += 1
        return F.make_vehicle(cls.blue, f'Blue/v{cls._n}', model, (0.0, 0.0, z))

    @classmethod
    def aircraft(cls, model, z, loadout=None, force=None):
        cls._n += 1
        return F.make_aircraft(force or cls.red, f'Red/a{cls._n}', model, (0.0, 0.0, z), loadout=loadout)

    @classmethod
    def ship(cls, model):
        cls._n += 1
        return F.make_ship(cls.blue, f'Blue/s{cls._n}', model, (0.0, 0.0, 0.0))


class TestFireControlGroundAir(_FireControlFixture, unittest.TestCase):

    def test_lorad_uses_air_subclass_and_dimension(self):
        buk = self.vehicle(BUK)
        template = GWD._EFF_SAM_LORAD
        for model, key, dim in ((A10, 'Aircraft_Attacker', 'med'), (F16, 'Aircraft', 'small'),
                                (B52, 'Aircraft_Heavy', 'big'), (SU24M, 'Aircraft', 'med')):
            with self.subTest(model=model):
                spec = self.fc(buk, self.aircraft(model, 5_000.0))
                self.assertIsInstance(spec, ShotSpec)
                self.assertEqual(spec.weapon, '9M38-SAM')
                self.assertEqual((spec.accuracy, spec.destroy_capacity), _cell(template, key, dim))
                self.assertTrue(spec.interceptable)
                self.assertEqual(spec.rounds, FC.SALVO_ROUNDS['missile'])
                self.assertIsNone(spec.cycle_time)

    def test_shorad_attacker_harder_to_kill_than_fighter_same_size(self):
        strela = self.vehicle(STRELA10)
        a10 = self.fc(strela, self.aircraft(A10, 2_000.0))
        su27 = self.fc(strela, self.aircraft(SU27, 2_000.0))
        self.assertLess(a10.accuracy * a10.destroy_capacity, su27.accuracy * su27.destroy_capacity)

    def test_override_matches_fighter(self):
        """Su-24M (Bomber, override 'Aircraft') = Su-27 (Fighter), stessa dimensione med."""
        buk = self.vehicle(BUK)
        self.assertEqual(self.fc(buk, self.aircraft(SU24M, 5_000.0)), self.fc(buk, self.aircraft(SU27, 5_000.0)))

    def test_gun_spec_is_a_burst(self):
        shilka = self.vehicle(SHILKA)
        spec = self.fc(shilka, self.aircraft(A10, 1_000.0))
        self.assertEqual(spec.weapon, 'AZP-23-23mm')
        self.assertEqual((spec.accuracy, spec.destroy_capacity),
                         _cell(GWD._EFF_AA_CANNON, 'Aircraft_Attacker', 'med'))
        self.assertFalse(spec.interceptable)
        self.assertEqual(spec.rounds, 1)
        fire_rate = GWD.GROUND_WEAPONS['AA_CANNONS']['AZP-23-23mm']['fire_rate']
        self.assertAlmostEqual(spec.cycle_time, FC.GUN_BURST_ROUNDS * 60.0 / fire_rate)

    def test_time_of_flight_from_range_and_speed(self):
        spec = self.fc(self.vehicle(BUK), self.aircraft(F16, 5_000.0))
        weapon = GWD.GROUND_WEAPONS['MISSILES']['9M38-SAM']
        self.assertAlmostEqual(spec.time_of_flight,
                               FC.ENGAGEMENT_RANGE_FRACTION * weapon['range']['direct'] / weapon['speed'])

    def test_sam_never_fires_at_surface(self):
        self.assertIsNone(self.fc(self.vehicle(BUK), F.make_vehicle(self.red, 'Red/tank', T72, (0, 0, 0))))

    def test_tank_vs_tank_uses_surface_weapon(self):
        spec = self.fc(self.vehicle(T72), F.make_vehicle(self.red, 'Red/tank2', T72, (0, 0, 0)))
        self.assertIsNotNone(spec)
        self.assertGreater(spec.accuracy * spec.destroy_capacity, 0.0)

    def test_tank_hmg_against_low_aircraft_only(self):
        tank = self.vehicle(T72)
        low = self.fc(tank, self.aircraft(A10, 500.0))
        self.assertIsNotNone(low)
        self.assertIn(low.weapon, GWD.GROUND_WEAPONS['MACHINE_GUNS'])
        self.assertIsNone(self.fc(tank, self.aircraft(A10, 5_000.0)))  # oltre la portata dell'HMG


class TestFireControlAltitude(_FireControlFixture, unittest.TestCase):

    def test_envelope_limits(self):
        strela = self.vehicle(STRELA10)
        weapon = GWD.GROUND_WEAPONS['MISSILES']['9M37-SAM']
        self.assertIsNotNone(self.fc(strela, self.aircraft(F16, weapon['max_altitude'] - 1.0)))
        self.assertIsNone(self.fc(strela, self.aircraft(F16, weapon['max_altitude'] + 1.0)))
        self.assertIsNone(self.fc(strela, self.aircraft(F16, weapon['min_altitude'] - 1.0)))

    def test_envelope_is_relative_to_shooter(self):
        weapon = GWD.GROUND_WEAPONS['MISSILES']['9M37-SAM']
        on_hill = self.vehicle(STRELA10, z=1_000.0)
        self.assertIsNotNone(self.fc(on_hill, self.aircraft(F16, weapon['max_altitude'] + 500.0)))

    def test_lorad_reaches_high_bomber(self):
        self.assertIsNotNone(self.fc(self.vehicle(BUK), self.aircraft(B52, 15_000.0)))
        self.assertIsNone(self.fc(self.vehicle(BUK), self.aircraft(B52, 30_000.0)))

    def test_filter_can_be_disabled(self):
        no_filter = FC.make_registry_fire_control(altitude_filter=False)
        self.assertIsNotNone(no_filter(self.vehicle(STRELA10), self.aircraft(F16, 12_000.0)))

    def test_no_altitude_no_filter(self):
        weapon = FC._candidate_weapons(('Vehicle', STRELA10, None))[0]
        self.assertTrue(FC.in_altitude_envelope(weapon, 0.0, None))
        self.assertTrue(FC.in_altitude_envelope(weapon, None, 50_000.0))

    def test_weapon_without_altitude_data_capped_by_range(self):
        hmg = [w for w in FC._candidate_weapons(('Vehicle', T72, None)) if w.weapon_type == 'MACHINE_GUNS'][0]
        self.assertIsNone(hmg.max_alt)
        self.assertTrue(FC.in_altitude_envelope(hmg, 0.0, hmg.range_m))
        self.assertFalse(FC.in_altitude_envelope(hmg, 0.0, hmg.range_m + 1.0))

    def test_air_weapon_max_height_in_km(self):
        aim9 = FC._Weapon('AIM-9M', 'MISSILES_AAM', 'air', {'max_height': 18, 'range': 18.5})
        self.assertEqual(aim9.max_height_m, 18_000.0)
        self.assertTrue(FC.in_altitude_envelope(aim9, 5_000.0, 18_000.0))
        self.assertFalse(FC.in_altitude_envelope(aim9, 5_000.0, 18_001.0))


class TestFireControlShipAndAircraft(_FireControlFixture, unittest.TestCase):

    def test_ship_sam_against_aircraft(self):
        spec = self.fc(self.ship(BURKE), self.aircraft(F16, 5_000.0))
        self.assertIn(spec.weapon, SWD.SHIP_WEAPONS['MISSILES_SAM'])
        self.assertTrue(spec.interceptable)

    def test_ship_does_not_fire_sam_at_surface(self):
        spec = self.fc(self.ship(BURKE), F.make_vehicle(self.red, 'Red/tank3', T72, (0, 0, 0)))
        self.assertIsNotNone(spec)
        self.assertNotIn(spec.weapon, SWD.SHIP_WEAPONS['MISSILES_SAM'])

    def test_fighter_aam_uses_aircraft_row(self):
        f16 = self.aircraft(F16, 5_000.0, loadout='CAP', force=self.blue)
        su27 = self.aircraft(SU27, 5_000.0)
        spec = self.fc(f16, su27)
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import AIR_WEAPONS
        self.assertIn(spec.weapon, AIR_WEAPONS['MISSILES_AAM'])
        self.assertEqual((spec.accuracy, spec.destroy_capacity),
                         _cell(AIR_WEAPONS['MISSILES_AAM'][spec.weapon]['efficiency'], 'Aircraft', 'med'))
        # un AAM non spara a un bersaglio di superficie
        self.assertIsNone(self.fc(f16, F.make_vehicle(self.red, 'Red/tank4', T72, (0, 0, 0))))

    def test_aircraft_without_loadout_has_no_weapon(self):
        self.assertIsNone(self.fc(self.aircraft(F16, 5_000.0, force=self.blue), self.aircraft(SU27, 5_000.0)))

    def test_cas_against_tank(self):
        a10 = self.aircraft(A10, 3_000.0, loadout='Maverick/Gun CAS', force=self.blue)
        self.assertIsNotNone(self.fc(a10, F.make_vehicle(self.red, 'Red/tank5', T72, (0, 0, 0))))


class TestFireControlMaxRange(_FireControlFixture, unittest.TestCase):
    """ShotSpec.max_range [m] dalla portata del registro (controllo di portata del risolutore)."""

    def test_ground_sam_range_in_metres(self):
        spec = self.fc(self.vehicle(BUK), self.aircraft(F16, 5_000.0))
        self.assertEqual(spec.max_range, GWD.GROUND_WEAPONS['MISSILES']['9M38-SAM']['range']['direct'])

    def test_ground_gun_direct_range_against_air_max_range_against_surface(self):
        s68 = FC._Weapon('S-68-57mm', 'AA_CANNONS', 'ground', GWD.GROUND_WEAPONS['AA_CANNONS']['S-68-57mm'])
        rng = GWD.GROUND_WEAPONS['AA_CANNONS']['S-68-57mm']['range']
        self.assertEqual(FC.shot_spec_for(s68, 0.5, 0.5, is_air=True).max_range, rng['direct'])
        self.assertEqual(FC.shot_spec_for(s68, 0.5, 0.5, is_air=False).max_range,
                         max(rng['direct'], rng['indirect']))

    def test_ship_range_converted_from_km(self):
        spec = self.fc(self.ship(BURKE), self.aircraft(F16, 5_000.0))
        self.assertEqual(spec.max_range, SWD.SHIP_WEAPONS['MISSILES_SAM'][spec.weapon]['range'] * 1000.0)

    def test_air_missile_speed_units(self):
        """max_speed: Mach per gli AAM, m/s per gli ASM (WEAPON_PARAM di Aircraft_Weapon_Data)."""
        aim9 = FC._Weapon('AIM-9M', 'MISSILES_AAM', 'air', {'range': 18.5, 'max_speed': 2.5})
        agm65 = FC._Weapon('AGM-65D', 'MISSILES_ASM', 'air', {'range': 15, 'max_speed': 320})
        self.assertAlmostEqual(aim9.speed_ms, 2.5 * FC.SPEED_OF_SOUND_MS)
        self.assertEqual(agm65.speed_ms, 320.0)
        self.assertAlmostEqual(FC.shot_spec_for(agm65, 0.5, 0.5).time_of_flight,
                               FC.ENGAGEMENT_RANGE_FRACTION * 15_000.0 / 320.0)

    def test_air_weapon_without_range_has_no_limit(self):
        bomb = FC._Weapon('Mk-83', 'BOMBS', 'air', {'type': 'Bombs'})
        self.assertIsNone(FC.shot_spec_for(bomb, 0.5, 0.5).max_range)
        aim9 = FC._Weapon('AIM-9M', 'MISSILES_AAM', 'air', {'range': 18.5, 'max_speed': 2.5})
        self.assertEqual(FC.shot_spec_for(aim9, 0.5, 0.5, is_air=True).max_range, 18_500.0)


class TestFireControlNoneAndDeterminism(_FireControlFixture, unittest.TestCase):

    def test_structure_never_fires(self):
        structure = F.make_structure(self.blue, 'Blue/bunker', (0.0, 0.0))
        self.assertIsNone(self.fc(structure, self.aircraft(F16, 2_000.0)))

    def test_unclassifiable_target(self):
        class _Stub:
            asset_type = 'Not_A_Target_Type'
            position = None
            _model = None

        self.assertIsNone(self.fc(self.vehicle(T72), _Stub()))

    def test_tie_break_by_model_name(self):
        row = {'Aircraft': {d: {'accuracy': 0.5, 'destroy_capacity': 0.5} for d in DIMS}}
        weapons = (FC._Weapon('Zeta', 'MISSILES', 'ground', {'efficiency': row}),
                   FC._Weapon('Alfa', 'MISSILES', 'ground', {'efficiency': row}))
        choice = FC.select_weapon(weapons, ('Aircraft',), 'med', True)
        self.assertEqual(choice[0].model, 'Alfa')
        choice = FC.select_weapon(tuple(reversed(weapons)), ('Aircraft',), 'med', True)
        self.assertEqual(choice[0].model, 'Alfa')

    def test_subclass_falls_back_to_aircraft_row(self):
        row = {'Aircraft': {d: {'accuracy': 0.4, 'destroy_capacity': 0.6} for d in DIMS}}
        weapons = (FC._Weapon('W', 'MISSILES', 'ground', {'efficiency': row}),)
        choice = FC.select_weapon(weapons, ('Aircraft_Attacker', 'Aircraft'), 'med', True)
        self.assertEqual(choice[1:], (0.4, 0.6))

    def test_memoized_equals_uncached_and_repeatable(self):
        plain = FC.make_registry_fire_control(memoize=False)
        cached = FC.make_registry_fire_control(memoize=True)
        shooters = [self.vehicle(m) for m in (BUK, STRELA10, SHILKA, T72)] + [self.ship(BURKE)]
        targets = [self.aircraft(m, z) for m in (A10, F16, B52) for z in (500.0, 3_000.0, 12_000.0)]
        for shooter in shooters:
            for target in targets:
                expected = plain(shooter, target)
                self.assertEqual(cached(shooter, target), expected)
                self.assertEqual(cached(shooter, target), expected)   # seconda chiamata: cache
                self.assertEqual(FC.make_registry_fire_control()(shooter, target), expected)

    def test_factory_argument_validation(self):
        with self.assertRaises(TypeError):
            FC.make_registry_fire_control(altitude_filter='yes')


if __name__ == '__main__':
    unittest.main()
