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
import math
import unittest
from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data
from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data
from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS
from Code.Dynamic_War_Manager.Source.Context.Context import (
    Ground_Vehicle_Asset_Type as gat,
    Sea_Asset_Type as sat,
)
from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import (
    ThreatAA,
    DetectionThreat,
    build_threat_aa,
    build_detection_threat,
    build_air_defense_threats,
    radar_horizon_range,
    sensor_antenna_height,
    EARTH_RADIUS_M,
    SENSOR_HEIGHT_VEHICLE_M,
    SENSOR_HEIGHT_EWR_M,
    SENSOR_HEIGHT_SHIP_M,
    DETECTION_VOLUME_CEILING_M,
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
    """Asset minimo: porta i veri air_defense_volume()/detection_range() e i campi che le fabbriche leggono."""

    air_defense_volume = Mobile.air_defense_volume
    detection_range = Mobile.detection_range
    _sensor_range_km = staticmethod(Mobile._sensor_range_km)

    def __init__(self, model=None, category=None, position=Point3D(0, 0, 0), id=None):
        self._model = model
        self.category = category
        self._position = position
        self.id = id


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
        self.assertAlmostEqual(threat.acquisition_time, detection)
        self.assertAlmostEqual(threat.min_detection_time, detection)  # alias storico (D-6)
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


def _horizon(h_antenna, h_target, k=4.0 / 3.0):
    """Orizzonte calcolato qui, indipendente dall'implementazione: sqrt(2kR)*(sqrt(h_a)+sqrt(h_t))."""
    return math.sqrt(2.0 * k * 6_371_000.0) * (math.sqrt(h_antenna) + math.sqrt(h_target))


class TestRadarHorizon(unittest.TestCase):
    """radar_horizon_range: formula standard dell'orizzonte radar (terra 4/3)."""

    def test_standard_constant_is_4_12_km_per_sqrt_m(self):
        """d_km ~= 4,12*(sqrt(h_a) + sqrt(h_t)), h in metri."""
        self.assertAlmostEqual(radar_horizon_range(1.0, 0.0) / 1000.0, 4.12, places=2)

    def test_values_of_the_proposal_table(self):
        """Proposta §2.5 (calcolata con 4,12 arrotondato): 31,8 / 50,4 / 139,5 km per antenna 5 m."""
        self.assertAlmostEqual(radar_horizon_range(5.0, 30.0) / 1000.0, 31.8, delta=0.05)
        self.assertAlmostEqual(radar_horizon_range(5.0, 100.0) / 1000.0, 50.4, delta=0.05)
        self.assertAlmostEqual(radar_horizon_range(5.0, 1000.0) / 1000.0, 139.5, delta=0.1)
        self.assertAlmostEqual(radar_horizon_range(20.0, 30.0) / 1000.0, 41.0, delta=0.05)

    def test_geometric_line_of_sight_is_shorter(self):
        """k = 1 (TVD, linea di vista geometrica) < k = 4/3 (radar)."""
        self.assertLess(radar_horizon_range(5.0, 30.0, 1.0), radar_horizon_range(5.0, 30.0))
        self.assertAlmostEqual(radar_horizon_range(5.0, 30.0, 1.0), _horizon(5.0, 30.0, 1.0))

    def test_negative_heights_saturate(self):
        self.assertAlmostEqual(radar_horizon_range(5.0, -100.0), _horizon(5.0, 0.0))


class TestBuildDetectionThreat(unittest.TestCase):
    """Volume di RILEVAMENTO dai dati sensore reali; SA-6 = 2K12-Kub (radar 1S91: scoperta 75 km,
    guida 28 km; missile 3M9: 24 km, 100-14 000 m)."""

    @classmethod
    def setUpClass(cls):
        _silence_data_warnings()

    def _sa6(self, z=0.0, id='sa6-1'):
        return _AssetStub(model='2K12-Kub', category=gat.SAM_MEDIUM.value,
                          position=Point3D(1000, 2000, z), id=id)

    def test_sa6_in_altitude_sees_at_full_acquisition_range(self):
        """A 1000 m l'orizzonte (139 km) non limita: raggio = acquisition_range 75 km."""
        threat = build_detection_threat(self._sa6(), 1000.0)

        self.assertIsInstance(threat, DetectionThreat)
        self.assertAlmostEqual(float(threat.cylinder.radius), 75_000.0)
        self.assertEqual(threat.sensor, 'radar')
        self.assertAlmostEqual(threat.acquisition_range, 75_000.0)
        self.assertAlmostEqual(threat.reference_altitude, 1000.0)

    def test_sa6_at_low_altitude_is_limited_by_the_horizon(self):
        """A 30 m: min(75 km, orizzonte(5 m, 30 m) ~ 31,8 km)."""
        threat = build_detection_threat(self._sa6(), 30.0)
        self.assertAlmostEqual(float(threat.cylinder.radius), _horizon(SENSOR_HEIGHT_VEHICLE_M, 30.0), places=3)
        self.assertAlmostEqual(threat.acquisition_range, 75_000.0)  # la portata nominale resta

    def test_target_height_is_relative_to_the_site(self):
        low = build_detection_threat(self._sa6(z=0.0), 30.0)
        high = build_detection_threat(self._sa6(z=500.0), 530.0)
        self.assertAlmostEqual(float(low.cylinder.radius), float(high.cylinder.radius), places=6)

    def test_volume_geometry_and_zero_danger(self):
        threat = build_detection_threat(self._sa6(z=200.0), 1000.0)

        self.assertAlmostEqual(float(threat.cylinder.bottom_center.x), 1000.0)
        self.assertAlmostEqual(float(threat.cylinder.bottom_center.y), 2000.0)
        self.assertAlmostEqual(float(threat.min_altitude), 200.0)
        self.assertAlmostEqual(float(threat.max_altitude), 200.0 + DETECTION_VOLUME_CEILING_M)
        self.assertEqual(threat.danger_level, 0.0)
        self.assertIs(threat.volume, threat.cylinder)
        self.assertEqual(threat.source_id, 'sa6-1')

    def test_tvd_only_system(self):
        """Strela-1 (SA-9): solo TVD 8 km; a 30 m la linea di vista (~27 km) non limita."""
        threat = build_detection_threat(_AssetStub(model='Strela-1-9P31', category=gat.SAM_SMALL.value), 30.0)
        self.assertEqual(threat.sensor, 'TVD')
        self.assertAlmostEqual(float(threat.cylinder.radius), 8_000.0)

    def test_systems_without_sensor_data_give_none(self):
        """ZSU-57-2 e M163-VADS non hanno sensori nei registri: rilevamento non modellato (D-4)."""
        for model in ('ZSU-57-2', 'M163-VADS'):
            asset = _AssetStub(model=model, category=gat.AAA.value)
            self.assertIsNone(build_detection_threat(asset, 1000.0), msg=model)
            self.assertIsNotNone(build_threat_aa(asset), msg=model)  # l'intercettazione resta

    def test_none_guards(self):
        self.assertIsNone(build_detection_threat(_AssetStub(model='T-90M', category=gat.TANK.value), 1000.0))
        self.assertIsNone(build_detection_threat(_AssetStub(model='inesistente'), 1000.0))
        self.assertIsNone(build_detection_threat(_AssetStub(model='2K12-Kub', position=None), 1000.0))

        class _Plain:
            _model = '2K12-Kub'
            _position = Point3D(0, 0, 0)
        self.assertIsNone(build_detection_threat(_Plain(), 1000.0))

    def test_ship_uses_mast_height(self):
        asset = _AssetStub(model='CVN-70 Carl Vinson', category=sat.CARRIER.value)
        self.assertEqual(sensor_antenna_height(asset, 'radar'), SENSOR_HEIGHT_SHIP_M)
        threat = build_detection_threat(asset, 30.0)
        self.assertAlmostEqual(float(threat.cylinder.radius), _horizon(SENSOR_HEIGHT_SHIP_M, 30.0), places=3)

    def test_ewr_class_uses_pole_height(self):
        self.assertEqual(sensor_antenna_height(_AssetStub(model='2K12-Kub', category='EWR'), 'radar'),
                         SENSOR_HEIGHT_EWR_M)
        self.assertEqual(sensor_antenna_height(self._sa6(), 'radar'), SENSOR_HEIGHT_VEHICLE_M)

    def test_sensor_only_record_with_registry_antenna_height(self):
        """Sito sensore puro (forma EWR/AWACS: engagement_range 0) con `antenna_height` di registro:
        produce il volume di rilevamento senza produrre minacce d'intercettazione."""
        record = object.__new__(Vehicle_Data)
        record.weapons = {}
        record.category = 'EWR'
        record.radar = {'model': 'test-ewr', 'antenna_height': 30.0,
                        'capabilities': {'air': (True, {'tracking_range': 0, 'acquisition_range': 300,
                                                        'engagement_range': 0, 'multi_target_capacity': 0})}}
        record.TVD = False
        Vehicle_Data._registry['test-ewr-sensor-only'] = record

        try:
            asset = _AssetStub(model='test-ewr-sensor-only', category='EWR', id='ewr-1')
            detection, interception = build_air_defense_threats(asset, 5000.0)
        finally:
            Vehicle_Data._registry.pop('test-ewr-sensor-only', None)

        self.assertIsNone(interception)
        self.assertEqual(detection.source_id, 'ewr-1')
        # a 5000 m l'orizzonte da 30 m e' ~314 km > 300 km: vale la portata nominale
        self.assertAlmostEqual(float(detection.cylinder.radius), 300_000.0)
        self.assertGreater(_horizon(30.0, 5000.0), 300_000.0)


class TestBuildAirDefenseThreats(unittest.TestCase):
    """build_air_defense_threats: i due volumi dello stesso sito, legati da source_id."""

    @classmethod
    def setUpClass(cls):
        _silence_data_warnings()

    def test_sa6_two_distinct_volumes(self):
        """SA-6 a 1000 m: rilevamento 75 km, intercettazione 24 km (arma 3M9), stesso source_id."""
        asset = _AssetStub(model='2K12-Kub', category=gat.SAM_MEDIUM.value, id='kub-7')
        detection, interception = build_air_defense_threats(asset, 1000.0)

        self.assertIsInstance(detection, DetectionThreat)
        self.assertIsInstance(interception, ThreatAA)
        self.assertAlmostEqual(float(detection.cylinder.radius), 75_000.0)
        self.assertAlmostEqual(float(interception.cylinder.radius), 24_000.0)
        self.assertEqual(detection.source_id, 'kub-7')
        self.assertEqual(interception.source_id, 'kub-7')
        self.assertEqual(detection.danger_level, 0.0)
        self.assertGreater(interception.danger_level, 0.0)

    def test_interception_part_equals_build_threat_aa(self):
        asset = _AssetStub(model='2K12-Kub', category=gat.SAM_MEDIUM.value)
        _, interception = build_air_defense_threats(asset, 1000.0)
        reference = build_threat_aa(asset)

        self.assertAlmostEqual(interception.danger_level, reference.danger_level)
        self.assertAlmostEqual(interception.interception_speed, reference.interception_speed)
        self.assertAlmostEqual(interception.acquisition_time, reference.acquisition_time)
        self.assertAlmostEqual(float(interception.cylinder.radius), float(reference.cylinder.radius))
        self.assertIsNone(reference.source_id)  # build_threat_aa invariata: nessun source_id

    def test_nesting_is_checked_on_declared_values_not_assumed(self):
        """Il rilevamento NON contiene sempre l'intercettazione. SA-6 a 30 m: 31,8 km > 24 km (annidati);
        S-300PS a 30 m: l'orizzonte (31,8 km) e' sotto la portata del 5V55R (75 km) e la quota 30 m e'
        dentro la sua fascia (da 25 m): evitare il volume di rilevamento NON evita l'intercettazione."""
        _det, _int = build_air_defense_threats(
            _AssetStub(model='2K12-Kub', category=gat.SAM_MEDIUM.value), 30.0)
        self.assertGreater(float(_det.cylinder.radius), float(_int.cylinder.radius))

        det, inter = build_air_defense_threats(
            _AssetStub(model='S-300PS', category=gat.SAM_BIG.value), 30.0)
        self.assertLess(float(det.cylinder.radius), float(inter.cylinder.radius))
        self.assertTrue(inter.min_altitude <= 30.0 <= inter.max_altitude)
        point_outside_detection = Point3D(float(det.cylinder.radius) + 5_000.0, 0, 30.0)
        self.assertFalse(det.innerPoint(point_outside_detection))
        self.assertTrue(inter.innerPoint(point_outside_detection))

    def test_asset_without_anything(self):
        self.assertEqual(build_air_defense_threats(_AssetStub(model='T-90M', category=gat.TANK.value), 1000.0),
                         (None, None))


if __name__ == '__main__':
    unittest.main(verbosity=2)
