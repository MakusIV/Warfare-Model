"""Tests per la fabbrica ThreatAA di Logic/Air_Route_Manager.

build_threat_aa / threat_reaction_times / threat_danger_level vivono in
Air_Route_Manager accanto a ThreatAA, ma i loro test stanno in un file proprio invece che
in Test_Air_Route_Manager.py: quello e' una suite di geometria e pianificazione di rotta
(matplotlib, cilindri, path search) che costruisce le minacce a mano, mentre qui si verifica
il ponte verso i DATI REALI di asset e armi. Tenerli separati evita di mescolare due
soggetti e non rallenta la suite geometrica.

Strategia di setup
------------------
* Si usano i registry e i registri d'arma REALI (Vehicle_Data, Ship_Data, GROUND_WEAPONS,
  SHIP_WEAPONS): il valore di questi test e' proprio verificare che i numeri ricercati
  (velocita' dei missili, inviluppi, acquire_time della tabella minacce SAM) arrivino fino
  all'oggetto ThreatAA.
* L'asset e' uno stub minimo che porta il vero Mobile.air_defense_volume() come metodo:
  Vehicle non e' importabile direttamente per il ciclo d'import noto del progetto
  (v. [[feedback_circular_import_workaround]]) e non serve, perche' la fabbrica legge solo
  `_model`, `category`, `_position` e air_defense_volume().
* I casi che richiedono dati inesistenti nei registri (arma AD senza velocita') usano una
  voce 'test-*' aggiunta ai dizionari reali e rimossa in tearDown.
"""

import logging
import unittest
from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data
from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS
from Code.Dynamic_War_Manager.Source.Context.Context import (
    Ground_Vehicle_Asset_Type as gat,
    Sea_Asset_Type as sat,
)
from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import (
    ThreatAA,
    build_threat_aa,
    threat_danger_level,
    threat_reaction_times,
    SAM_REACTION_TABLE,
    LAUNCH_SEQUENCE_TIME_S,
    DEFAULT_LAUNCH_SEQUENCE_TIME_S,
    GUN_LAUNCH_SEQUENCE_TIME_S,
    DEFAULT_ACQUIRE_TIME_S,
    DEFAULT_ACQUIRE_TIME_FALLBACK_S,
    DEFAULT_INTERCEPTION_SPEED_MS,
    DANGER_LEVEL_REFERENCE_RADIUS_M,
    DANGER_LEVEL_REFERENCE_CEILING_M,
    DANGER_LEVEL_REFERENCE_REACTION_S,
)


class _AssetStub:
    """Asset minimo: porta il vero air_defense_volume() e i tre campi che la fabbrica legge."""

    air_defense_volume = Mobile.air_defense_volume

    def __init__(self, model=None, category=None, position=Point3D(0, 0, 0)):
        self._model = model
        self.category = category
        self._position = position


def _silence_data_warnings():
    """I registry emettono warning noti sui dati (es. 2K22-Tunguska: AA_CANNONS su SAM_Small)."""
    for name in ('Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data',
                 'Code.Dynamic_War_Manager.Source.Asset.Mobile',
                 'Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager'):
        logging.getLogger(name).setLevel(logging.ERROR)


class TestThreatDangerLevel(unittest.TestCase):
    """threat_danger_level: scala [0, 1], monotona, saturata."""

    def test_zero_threat_is_zero(self):
        """Nessuna portata, nessuna quota, reattivita' nulla → 0."""
        self.assertAlmostEqual(
            threat_danger_level(0.0, 0.0, DANGER_LEVEL_REFERENCE_REACTION_S), 0.0)

    def test_maximum_threat_is_one(self):
        self.assertAlmostEqual(
            threat_danger_level(DANGER_LEVEL_REFERENCE_RADIUS_M,
                                DANGER_LEVEL_REFERENCE_CEILING_M, 0.0), 1.0)

    def test_values_above_reference_saturate(self):
        self.assertAlmostEqual(
            threat_danger_level(DANGER_LEVEL_REFERENCE_RADIUS_M * 10,
                                DANGER_LEVEL_REFERENCE_CEILING_M * 10, 0.0), 1.0)

    def test_reaction_time_above_reference_saturates(self):
        a = threat_danger_level(10_000.0, 5_000.0, DANGER_LEVEL_REFERENCE_REACTION_S)
        b = threat_danger_level(10_000.0, 5_000.0, DANGER_LEVEL_REFERENCE_REACTION_S * 100)
        self.assertAlmostEqual(a, b)

    def test_longer_range_is_more_dangerous(self):
        self.assertGreater(threat_danger_level(50_000.0, 10_000.0, 10.0),
                           threat_danger_level(5_000.0, 10_000.0, 10.0))

    def test_higher_ceiling_is_more_dangerous(self):
        self.assertGreater(threat_danger_level(20_000.0, 20_000.0, 10.0),
                           threat_danger_level(20_000.0, 2_000.0, 10.0))

    def test_faster_reaction_is_more_dangerous(self):
        self.assertGreater(threat_danger_level(20_000.0, 10_000.0, 2.0),
                           threat_danger_level(20_000.0, 10_000.0, 25.0))

    def test_range_dominates_reaction(self):
        """La portata pesa piu' della reattivita': l'evitamento e' un problema geometrico."""
        long_slow = threat_danger_level(DANGER_LEVEL_REFERENCE_RADIUS_M, 0.0,
                                        DANGER_LEVEL_REFERENCE_REACTION_S)
        short_fast = threat_danger_level(0.0, 0.0, 0.0)
        self.assertGreater(long_slow, short_fast)

    def test_always_within_unit_interval(self):
        for radius in (0.0, 1_000.0, 500_000.0):
            for ceiling in (0.0, 3_000.0, 200_000.0):
                for reaction in (0.0, 15.0, 120.0):
                    value = threat_danger_level(radius, ceiling, reaction)
                    self.assertGreaterEqual(value, 0.0)
                    self.assertLessEqual(value, 1.0)


class TestThreatReactionTimes(unittest.TestCase):
    """threat_reaction_times: tabella ricercata quando c'e', stima dichiarata altrimenti."""

    @classmethod
    def setUpClass(cls):
        _silence_data_warnings()

    def test_table_model_uses_researched_acquire_time(self):
        detection, _fire = threat_reaction_times(_AssetStub(model='S-300PS',
                                                            category=gat.SAM_BIG.value))
        self.assertAlmostEqual(detection, SAM_REACTION_TABLE['S-300PS']['acquire_time'])

    def test_table_model_uses_launcher_keyed_fire_time(self):
        _detection, fire = threat_reaction_times(_AssetStub(model='9K331-Tor',
                                                            category=gat.SAM_SMALL.value))
        launcher = SAM_REACTION_TABLE['9K331-Tor']['launcher']
        self.assertAlmostEqual(fire, LAUNCH_SEQUENCE_TIME_S[launcher])

    def test_every_table_launcher_has_a_launch_time(self):
        """Nessuna voce della tabella deve cadere sul default per un lanciatore non censito."""
        for model, entry in SAM_REACTION_TABLE.items():
            self.assertIn(entry['launcher'], LAUNCH_SEQUENCE_TIME_S,
                          msg=f"launcher of {model} missing from LAUNCH_SEQUENCE_TIME_S")

    def test_model_outside_table_uses_category_placeholder(self):
        detection, fire = threat_reaction_times(
            _AssetStub(model='MIM-72G-Chaparral', category=gat.SAM_SMALL.value))
        self.assertAlmostEqual(detection, DEFAULT_ACQUIRE_TIME_S[gat.SAM_SMALL.value])
        self.assertAlmostEqual(fire, DEFAULT_LAUNCH_SEQUENCE_TIME_S)

    def test_unknown_category_uses_fallback(self):
        """Le navi hanno una Sea_Asset_Type come category: nessuna classe AD → ripiego."""
        detection, _fire = threat_reaction_times(
            _AssetStub(model='CVN-70 Carl Vinson', category=sat.CARRIER.value))
        self.assertAlmostEqual(detection, DEFAULT_ACQUIRE_TIME_FALLBACK_S)

    def test_no_category_at_all_uses_fallback(self):
        detection, _fire = threat_reaction_times(_AssetStub(model='ignoto'))
        self.assertAlmostEqual(detection, DEFAULT_ACQUIRE_TIME_FALLBACK_S)

    def test_guns_only_uses_traverse_time(self):
        """Un cannone AA non ha sequenza di lancio: resta il solo brandeggio."""
        _detection, fire = threat_reaction_times(
            _AssetStub(model='ZSU-23-4-Shilka', category=gat.AAA.value), has_missiles=False)
        self.assertAlmostEqual(fire, GUN_LAUNCH_SEQUENCE_TIME_S)

    def test_guns_only_overrides_even_a_table_model(self):
        _detection, fire = threat_reaction_times(
            _AssetStub(model='S-300PS', category=gat.SAM_BIG.value), has_missiles=False)
        self.assertAlmostEqual(fire, GUN_LAUNCH_SEQUENCE_TIME_S)

    def test_all_times_are_positive(self):
        for model in list(SAM_REACTION_TABLE) + ['MIM-72G-Chaparral', 'ignoto']:
            detection, fire = threat_reaction_times(_AssetStub(model=model))
            self.assertGreater(detection, 0.0, msg=model)
            self.assertGreater(fire, 0.0, msg=model)


class TestBuildThreatAA(unittest.TestCase):
    """build_threat_aa su dati di asset e di arma reali."""

    @classmethod
    def setUpClass(cls):
        _silence_data_warnings()

    def test_returns_threat_for_real_sam(self):
        threat = build_threat_aa(_AssetStub(model='S-300PS', category=gat.SAM_BIG.value))
        self.assertIsInstance(threat, ThreatAA)

    def test_cylinder_comes_from_air_defense_volume(self):
        asset = _AssetStub(model='S-300PS', category=gat.SAM_BIG.value)
        threat = build_threat_aa(asset)
        expected = asset.air_defense_volume()

        self.assertAlmostEqual(float(threat.cylinder.radius), float(expected.radius))
        self.assertAlmostEqual(float(threat.cylinder.height), float(expected.height))

    def test_s300_radius_is_the_real_missile_range(self):
        """5V55R-SAM: range diretto 75 000 m."""
        threat = build_threat_aa(_AssetStub(model='S-300PS', category=gat.SAM_BIG.value))
        self.assertAlmostEqual(float(threat.cylinder.radius), 75_000.0)

    def test_interception_speed_is_the_real_missile_speed(self):
        """5V55R-SAM: speed 1700 m/s."""
        threat = build_threat_aa(_AssetStub(model='S-300PS', category=gat.SAM_BIG.value))
        self.assertAlmostEqual(threat.interception_speed, 1700.0)

    def test_gun_only_asset_uses_muzzle_speed(self):
        """AZP-23-23mm: muzzle_speed 970 m/s; nessun missile → tempo di brandeggio."""
        threat = build_threat_aa(_AssetStub(model='ZSU-23-4-Shilka', category=gat.AAA.value))

        self.assertAlmostEqual(threat.interception_speed, 970.0)
        self.assertAlmostEqual(threat.min_fire_time, GUN_LAUNCH_SEQUENCE_TIME_S)

    def test_mixed_gun_and_missile_asset_takes_the_fastest(self):
        """2K22-Tunguska: 9M311 a 900 m/s + 2A38M a 960 m/s → 960 (caso peggiore)."""
        threat = build_threat_aa(_AssetStub(model='2K22-Tunguska',
                                            category=gat.SAM_SMALL.value))
        self.assertAlmostEqual(threat.interception_speed, 960.0)

    def test_mixed_asset_keeps_the_missile_launch_sequence(self):
        """Avere anche i cannoni non deve azzerare la sequenza di lancio dei missili."""
        threat = build_threat_aa(_AssetStub(model='2K22-Tunguska',
                                            category=gat.SAM_SMALL.value))
        launcher = SAM_REACTION_TABLE['2K22-Tunguska']['launcher']
        self.assertAlmostEqual(threat.min_fire_time, LAUNCH_SEQUENCE_TIME_S[launcher])

    def test_reaction_times_reach_the_threat_object(self):
        threat = build_threat_aa(_AssetStub(model='9A33-Osa', category=gat.SAM_SMALL.value))
        detection, fire = threat_reaction_times(_AssetStub(model='9A33-Osa',
                                                           category=gat.SAM_SMALL.value))
        self.assertAlmostEqual(threat.min_detection_time, detection)
        self.assertAlmostEqual(threat.min_fire_time, fire)

    def test_altitudes_come_from_the_envelope(self):
        asset = _AssetStub(model='S-300PS', category=gat.SAM_BIG.value,
                           position=Point3D(0, 0, 100))
        threat = build_threat_aa(asset)

        # 5V55R-SAM: min_altitude 25 m, max_altitude 27 000 m, su terreno a 100 m.
        self.assertAlmostEqual(float(threat.min_altitude), 125.0)
        self.assertAlmostEqual(float(threat.max_altitude), 125.0 + (27_000.0 - 25.0))

    def test_danger_level_within_unit_interval(self):
        for model, category in (('S-300PS', gat.SAM_BIG.value),
                                ('9K37-Buk', gat.SAM_MEDIUM.value),
                                ('9A33-Osa', gat.SAM_SMALL.value),
                                ('ZSU-23-4-Shilka', gat.AAA.value)):
            threat = build_threat_aa(_AssetStub(model=model, category=category))
            self.assertGreaterEqual(threat.danger_level, 0.0, msg=model)
            self.assertLessEqual(threat.danger_level, 1.0, msg=model)

    def test_danger_level_ordering_across_real_systems(self):
        """S-300 > Buk > Osa: l'ordine che la pianificazione di rotta deve vedere."""
        s300 = build_threat_aa(_AssetStub(model='S-300PS', category=gat.SAM_BIG.value))
        buk = build_threat_aa(_AssetStub(model='9K37-Buk', category=gat.SAM_MEDIUM.value))
        osa = build_threat_aa(_AssetStub(model='9A33-Osa', category=gat.SAM_SMALL.value))

        self.assertGreater(s300.danger_level, buk.danger_level)
        self.assertGreater(buk.danger_level, osa.danger_level)

    def test_ship_sam_builds_a_threat(self):
        """RIM-162-ESSM: 50 km, 1360 m/s — le navi passano dal ramo MISSILES_SAM."""
        threat = build_threat_aa(_AssetStub(model='CVN-70 Carl Vinson',
                                            category=sat.CARRIER.value))
        self.assertAlmostEqual(float(threat.cylinder.radius), 50_000.0)
        self.assertAlmostEqual(threat.interception_speed, 1360.0)

    def test_threat_is_printable(self):
        """ThreatAA.__str__ formatta tutti i campi con :.2f: devono essere numeri."""
        threat = build_threat_aa(_AssetStub(model='9K331-Tor', category=gat.SAM_SMALL.value))
        self.assertIn('interception_speed', str(threat))
        self.assertIn('danger', repr(threat))


class TestBuildThreatAANoneGuards(unittest.TestCase):
    """Un asset che non e' una minaccia AA da' None, mai un'eccezione."""

    @classmethod
    def setUpClass(cls):
        _silence_data_warnings()

    def test_asset_without_ad_weapons(self):
        self.assertIsNone(build_threat_aa(_AssetStub(model='T-90M', category=gat.TANK.value)))

    def test_unknown_model(self):
        self.assertIsNone(build_threat_aa(_AssetStub(model='inesistente')))

    def test_model_not_set(self):
        self.assertIsNone(build_threat_aa(_AssetStub()))

    def test_position_not_set(self):
        self.assertIsNone(build_threat_aa(_AssetStub(model='S-300PS',
                                                     category=gat.SAM_BIG.value,
                                                     position=None)))

    def test_object_without_air_defense_volume(self):
        class _Plain:
            _model = 'S-300PS'
        self.assertIsNone(build_threat_aa(_Plain()))


class TestInterceptionSpeedFallback(unittest.TestCase):
    """Arma AD senza dato di velocita': ThreatAA divide per interception_speed, mai 0."""

    @classmethod
    def setUpClass(cls):
        _silence_data_warnings()

    def setUp(self):
        SHIP_WEAPONS['MISSILES_SAM']['test-sam-no-speed'] = {
            'model': 'test-sam-no-speed',
            'range': 20,            # km
            'min_altitude': 10,
            'max_altitude': 8_000,
        }
        record = object.__new__(Ship_Data)
        record.weapons = {'MISSILES_SAM': [('test-sam-no-speed', 8)]}
        Ship_Data._registry['test-ship-no-speed'] = record

    def tearDown(self):
        SHIP_WEAPONS['MISSILES_SAM'].pop('test-sam-no-speed', None)
        Ship_Data._registry.pop('test-ship-no-speed', None)

    def test_falls_back_to_default_speed(self):
        threat = build_threat_aa(_AssetStub(model='test-ship-no-speed',
                                            category=sat.DESTROYER.value))
        self.assertAlmostEqual(threat.interception_speed, DEFAULT_INTERCEPTION_SPEED_MS)

    def test_fallback_speed_is_usable_by_the_threat_math(self):
        """calcMaxLenghtCrossSegment divide per interception_speed: non deve esplodere."""
        threat = build_threat_aa(_AssetStub(model='test-ship-no-speed',
                                            category=sat.DESTROYER.value))
        length = threat.calcMaxLenghtCrossSegment(aircraft_speed=250.0,
                                                  aircraft_altitude=5_000.0,
                                                  time_to_inversion=30.0)
        self.assertIsNotNone(length)


if __name__ == '__main__':
    unittest.main(verbosity=2)
