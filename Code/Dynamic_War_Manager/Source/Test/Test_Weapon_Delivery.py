"""Test di Logic/Weapon_Delivery.py (Proposta B: balistica di rilascio e profilo d'attacco).

I valori attesi della balistica sono ricalcolati qui dalla formula del vuoto (sqrt(2h/g), moto
parabolico) e dai fattori dichiarati del modulo, non copiati dall'implementazione. I dati d'arma e di
loadout sono quelli REALI dei registri (Mk-82/Mk-83/Mk-82AIR/GBU-24/BK-90/KMGU-2, F/A-18C, A-10C, B-52H);
le minacce sono cilindri scritti a mano, cosi' la geometria attesa e' nota.

Logger: silenziati con `Scenario_Fixtures.LoggerSilencer` (mixin, non un TestCase).
"""

import math
import unittest

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import AIR_WEAPONS
from Code.Dynamic_War_Manager.Source.Command.Attack_Types import AttackProfile, ThreatExposure
from Code.Dynamic_War_Manager.Source.DataType.Cylinder import Cylinder
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.Logic import Weapon_Delivery as WD
from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import DetectionThreat, ThreatAA
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F


G = 9.80665
FA18, A10, B52, F14 = 'F/A-18C Hornet', 'A-10C Thunderbolt II', 'B-52H Stratofortress', 'F-14B Tomcat'
TARGET = Point3D(0, 0, 0)


def _vacuum(h, v_ms, pitch_deg=0.0):
    """(tempo, gittata orizzontale) nel vuoto, calcolati qui."""
    vz = v_ms * math.sin(math.radians(pitch_deg))
    t = (vz + math.sqrt(vz * vz + 2 * G * h)) / G
    return t, v_ms * math.cos(math.radians(pitch_deg)) * t


def _sam(radius, height, source='sam', danger=0.5, acquisition=10.0, fire=5.0, center=(0, 0, 0)):
    return ThreatAA(danger, 600.0, fire, acquisition_time=acquisition,
                    cylinder=Cylinder(center=Point3D(*center), radius=radius, height=height), source_id=source)


def _radar(radius, source='sam', center=(0, 0, 0)):
    return DetectionThreat(Cylinder(center=Point3D(*center), radius=radius, height=25_000.0), 'radar',
                           acquisition_range=radius, reference_altitude=1_000.0, source_id=source)


# ── LIVELLO 1: FISICA ─────────────────────────────────────────────────────────

class TestReleaseWindows(unittest.TestCase):

    def test_single_window_from_registry(self):
        (window,) = WD.release_windows('Mk-83')
        data = AIR_WEAPONS['BOMBS']['Mk-83']['release']
        self.assertEqual(window.drag, 'low')
        self.assertEqual(window.min_altitude, data['min_altitude'])
        self.assertEqual(window.max_speed_kmh, data['max_speed'])
        self.assertEqual(window.modes, ('level', 'dive', 'loft'))

    def test_selectable_drag_gives_low_then_high(self):
        low, high = WD.release_windows('Mk-82AIR')
        self.assertEqual((low.drag, high.drag), ('low', 'high'))
        self.assertEqual(high.min_altitude, 60.0)
        self.assertNotIn('loft', high.modes)

    def test_no_release_data_means_no_window(self):
        mk83_without_release = {k: v for k, v in AIR_WEAPONS['BOMBS']['Mk-83'].items() if k != 'release'}
        self.assertEqual(WD.release_windows(mk83_without_release), ())
        self.assertEqual(WD.release_windows('AGM-65D'), ())
        self.assertEqual(WD.release_windows('not-a-weapon'), ())

    def test_select_window_low_if_altitude_fits_else_high(self):
        windows = WD.release_windows('Mk-82AIR')
        self.assertEqual(WD.select_window(windows, 1_000.0).drag, 'low')
        self.assertEqual(WD.select_window(windows, 200.0).drag, 'high')
        self.assertIsNone(WD.select_window(windows, 20.0))


class TestBallistics(unittest.TestCase):

    def test_level_fall_time_is_free_fall(self):
        self.assertAlmostEqual(WD.fall_time(3_000.0, 250.0, 0.0), math.sqrt(2 * 3_000.0 / G))

    def test_dive_shorter_and_loft_longer_than_level(self):
        level = WD.fall_time(1_000.0, 250.0, 0.0)
        self.assertLess(WD.fall_time(1_000.0, 250.0, -30.0), level)
        self.assertGreater(WD.fall_time(1_000.0, 250.0, 30.0), level)

    def test_level_release_solution_low_drag(self):
        (window,) = WD.release_windows('Mk-83')
        sol = WD.release_solution(window, 3_000.0, 850.0)
        t, r = _vacuum(3_000.0, 850.0 / 3.6)
        self.assertAlmostEqual(sol.fall_time_s, t * WD.DRAG_FACTORS['low']['time'])
        self.assertAlmostEqual(sol.ground_range_m, r * WD.DRAG_FACTORS['low']['range'])
        self.assertAlmostEqual(sol.slant_range_m, math.hypot(sol.ground_range_m, 3_000.0))
        # ordine di grandezza della proposta (vuoto 5,8 km)
        self.assertTrue(5_000.0 < sol.ground_range_m < 6_000.0)

    def test_dive_and_loft_use_the_same_vector_model(self):
        (window,) = WD.release_windows('Mk-84')
        v = 900.0 / 3.6
        dive = WD.release_solution(window, 1_500.0, 900.0, 'dive', 30.0)
        loft = WD.release_solution(window, 1_500.0, 900.0, 'loft')
        self.assertAlmostEqual(dive.ground_range_m, _vacuum(1_500.0, v, -30.0)[1] * 0.9)
        self.assertAlmostEqual(loft.ground_range_m, _vacuum(1_500.0, v, WD.LOFT_PITCH_DEG)[1] * 0.9)
        self.assertEqual((dive.pitch_deg, loft.pitch_deg), (-30.0, WD.LOFT_PITCH_DEG))
        self.assertLess(dive.ground_range_m, loft.ground_range_m)

    def test_high_drag_is_shorter_and_slower(self):
        low, high = WD.release_windows('Mk-82AIR')
        a = WD.release_solution(low, 1_000.0, 800.0)
        b = WD.release_solution(high, 1_000.0, 800.0)
        self.assertLess(b.ground_range_m, a.ground_range_m)
        self.assertGreater(b.fall_time_s, a.fall_time_s)

    def test_release_outside_window_is_refused(self):
        (window,) = WD.release_windows('Mk-83')
        self.assertIsNone(WD.release_solution(window, 100.0, 850.0))        # sotto min_altitude
        self.assertIsNone(WD.release_solution(window, 3_000.0, 2_000.0))    # sopra max_speed
        self.assertIsNone(WD.release_solution(window, 3_000.0, 850.0, 'dive', 80.0))   # oltre dive_angle
        (cbu,) = WD.release_windows('CBU-52B')
        self.assertIsNone(WD.release_solution(cbu, 1_000.0, 800.0, 'loft'))  # profilo non ammesso

    def test_programming_errors_raise(self):
        (window,) = WD.release_windows('Mk-83')
        with self.assertRaises(ValueError):
            WD.release_solution(window, 3_000.0, 850.0, 'toss')
        with self.assertRaises(ValueError):
            WD.release_solution(window, 3_000.0, 850.0, 'dive')

    def test_glide_ratio_extends_range(self):
        (window,) = WD.release_windows('GBU-24')
        sol = WD.release_solution(window, 10_000.0, 900.0)
        self.assertAlmostEqual(sol.ground_range_m, 3.0 * 10_000.0)
        self.assertAlmostEqual(sol.fall_time_s, 30_000.0 / 250.0)

    def test_standoff_dispenser_interpolates_in_altitude(self):
        (window,) = WD.release_windows('BK-90MJ1')
        self.assertAlmostEqual(WD.release_solution(window, 50.0, 900.0).ground_range_m, 5_000.0)
        self.assertAlmostEqual(WD.release_solution(window, 500.0, 900.0).ground_range_m, 10_000.0)
        self.assertAlmostEqual(WD.release_solution(window, 275.0, 900.0).ground_range_m, 7_500.0)


class TestBombEngagementEstimate(unittest.TestCase):
    """Stima per il DES (B6): quota e velocita' portate dentro la finestra."""

    def test_inside_window_equals_level_solution(self):
        (window,) = WD.release_windows('Mk-82')
        self.assertEqual(WD.bomb_engagement_estimate('Mk-82', 1_000.0, 580.0),
                         WD.release_solution(window, 1_000.0, 580.0))

    def test_altitude_and_speed_are_clamped(self):
        est = WD.bomb_engagement_estimate('Mk-82', 300.0, 2_000.0)
        self.assertEqual(est.altitude_agl, 450.0)
        self.assertEqual(est.speed_kmh, 1_110.0)

    def test_selectable_drag_low_altitude_uses_high_drag(self):
        self.assertEqual(WD.bomb_engagement_estimate('Mk-82AIR', 150.0, 800.0).drag, 'high')
        self.assertEqual(WD.bomb_engagement_estimate('Mk-82AIR', 2_000.0, 800.0).drag, 'low')

    def test_no_speed_uses_window_centre(self):
        est = WD.bomb_engagement_estimate('Mk-83', 3_000.0, None)
        self.assertEqual(est.speed_kmh, (370.0 + 1_110.0) / 2.0)

    def test_no_release_data_returns_none(self):
        mk83_without_release = {k: v for k, v in AIR_WEAPONS['BOMBS']['Mk-83'].items() if k != 'release'}
        self.assertIsNone(WD.bomb_engagement_estimate(mk83_without_release, 1_000.0, 800.0))

    def test_kmgu_dispenser_releases_level_high_drag_almost_overhead(self):
        """D4: il KMGU-2 resta sul pilone; cadono i blocchi di submunizioni (drag high) da bassa quota."""
        (window,) = WD.release_windows('KMGU-2AO')
        self.assertEqual((window.modes, window.drag), (('level',), 'high'))
        est = WD.bomb_engagement_estimate('KMGU-2AO', 200.0, 800.0)
        self.assertEqual(est.drag, 'high')
        self.assertLess(est.slant_range_m, 1_500.0)


# ── LIVELLO 2: PIANIFICAZIONE ─────────────────────────────────────────────────

class TestPlanFeasibility(F.LoggerSilencer, unittest.TestCase):

    def test_unknown_loadout(self):
        profile = WD.plan_attack_profile(FA18, 'nope', 'Mk-83', TARGET)
        self.assertFalse(profile.feasible)
        self.assertIn('loadout', profile.reason)

    def test_weapon_not_carried(self):
        profile = WD.plan_attack_profile(FA18, 'Strike', 'Mk-84', TARGET)
        self.assertFalse(profile.feasible)
        self.assertIn('not carried', profile.reason)

    def test_missile_is_out_of_scope(self):
        profile = WD.plan_attack_profile(A10, 'Maverick/Gun CAS', 'AGM-65D', TARGET)
        self.assertFalse(profile.feasible)
        self.assertIn('not a bomb', profile.reason)

    def test_no_common_window(self):
        """CBU-52B non ammette il loft: con i soli profili in cabrata nessun candidato."""
        profile = WD.plan_attack_profile(A10, 'Heavy CAS', 'CBU-52B', TARGET, modes=['loft'])
        self.assertFalse(profile.feasible)
        self.assertIn('no common window', profile.reason)

    def test_target_point_type_checked(self):
        with self.assertRaises(TypeError):
            WD.plan_attack_profile(FA18, 'Strike', 'Mk-83', (0, 0, 0))

    def test_quantity_from_pylons(self):
        self.assertEqual(WD.weapon_quantity(FA18, 'Strike', 'Mk-83'), 2)
        self.assertEqual(WD.weapon_quantity(FA18, 'Strike', 'Mk-82'), 4)
        profile = WD.plan_attack_profile(FA18, 'Strike', 'Mk-82', TARGET)
        self.assertEqual(profile.quantity, 4)
        self.assertEqual(WD.plan_attack_profile(FA18, 'Strike', 'Mk-82', TARGET, quantity=2).quantity, 2)


class TestPlanGeometry(F.LoggerSilencer, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profile = WD.plan_attack_profile(FA18, 'Strike', 'Mk-83', TARGET, azimuths_deg=[0], modes=['level'])

    def test_lowest_altitude_of_the_common_band_without_threats(self):
        # attack 300-8000 m ∩ Mk-83 570-12000 m -> 570; velocita' attack 900 km/h (< max 1110)
        self.assertTrue(self.profile.feasible)
        self.assertEqual(self.profile.release_altitude_m, 570.0)
        self.assertEqual(self.profile.release_speed_kmh, 900.0)
        self.assertEqual(self.profile.release_mode, 'level')

    def test_points_along_the_run_in_azimuth(self):
        r = _vacuum(570.0, 250.0)[1] * WD.DRAG_FACTORS['low']['range']
        rel = [float(c) for c in self.profile.release_point]
        ip = [float(c) for c in self.profile.ip_point]
        egr = [float(c) for c in self.profile.egress_point]
        self.assertAlmostEqual(rel[0], 0.0)
        self.assertAlmostEqual(rel[1], r, places=3)
        self.assertAlmostEqual(ip[1], r + WD.IP_RUN_IN_DISTANCE_M, places=3)
        s = math.sin(math.radians(WD.EGRESS_TURN_DEG)) * WD.EGRESS_DISTANCE_M
        self.assertAlmostEqual(egr[0], s, places=3)
        self.assertEqual({rel[2], ip[2], egr[2]}, {570.0})

    def test_attack_route_is_canonical(self):
        route = self.profile.attack_route
        self.assertIsInstance(route, Route)
        self.assertEqual(len(route.edges), 2)
        expected = (WD.IP_RUN_IN_DISTANCE_M + WD.EGRESS_DISTANCE_M) / 250.0
        self.assertAlmostEqual(float(route.travelTime()), expected, places=3)
        self.assertIsNone(self.profile.full_route)

    def test_des_fields(self):
        self.assertAlmostEqual(self.profile.release_slant_range_m,
                               math.hypot(self.profile.release_ground_range_m, 570.0))
        self.assertGreater(self.profile.fall_time_s, 0.0)

    def test_deterministic(self):
        again = WD.plan_attack_profile(FA18, 'Strike', 'Mk-83', TARGET, azimuths_deg=[0], modes=['level'])
        self.assertEqual(again.release_point, self.profile.release_point)
        self.assertEqual(again.exposure, self.profile.exposure)

    def test_home_bearing_breaks_azimuth_ties(self):
        profile = WD.plan_attack_profile(FA18, 'Strike', 'Mk-83', TARGET,
                                         home_point=Point3D(60_000, 0, 0), modes=['level'])
        self.assertEqual(profile.run_in_azimuth_deg, 90.0)

    def test_imposed_azimuth(self):
        profile = WD.plan_attack_profile(FA18, 'Strike', 'Mk-83', TARGET, azimuths_deg=[225])
        self.assertEqual(profile.run_in_azimuth_deg, 225.0)


class TestPlanThreats(F.LoggerSilencer, unittest.TestCase):

    def test_overfly_short_range_defence(self):
        """B-52 (attack 5000-15000 m) sopra un SHORAD con tetto 3500 m: esposizione nulla."""
        profile = WD.plan_attack_profile(B52, 'Iron Bomb Strike', 'Mk-82', TARGET, [_sam(6_000.0, 3_500.0)])
        self.assertTrue(profile.feasible)
        self.assertEqual(profile.release_altitude_m, 5_000.0)
        self.assertEqual(profile.weighted_exposure, 0.0)

    def test_climbs_just_above_the_threat_ceiling(self):
        """A-10 CAS (attack 30-4000 m) con Mk-82AIR: la quota candidata e' il tetto x 1,05."""
        profile = WD.plan_attack_profile(A10, 'Maverick/Gun CAS', 'Mk-82AIR', TARGET, [_sam(6_000.0, 3_500.0)],
                                         modes=['level'])
        self.assertAlmostEqual(profile.release_altitude_m, 3_500.0 * 1.05)
        self.assertEqual(profile.weighted_exposure, 0.0)

    def test_unavoidable_threat_is_accepted(self):
        """A-10 'Heavy CAS' (tetto attack 3000 m) sotto un SAM che copre tutto: profilo fattibile."""
        profile = WD.plan_attack_profile(A10, 'Heavy CAS', 'Mk-82', TARGET, [_sam(40_000.0, 20_000.0)])
        self.assertTrue(profile.feasible)
        self.assertGreater(profile.weighted_exposure, 0.0)
        self.assertEqual(len(profile.exposure), 1)
        self.assertIsInstance(profile.exposure[0], ThreatExposure)


class TestExposureRule(F.LoggerSilencer, unittest.TestCase):
    """B3/D-8: t_lancio = max(t_ingresso V_I, t_contatto V_R + acquisizione) + tempo di lancio."""

    def plan(self, detection=None):
        return WD.plan_attack_profile(A10, 'Heavy CAS', 'Mk-82', TARGET, [_sam(40_000.0, 20_000.0)], detection,
                                      azimuths_deg=[0], modes=['level'])

    def test_without_detection_volume_site_is_already_tracking(self):
        (exposure,) = self.plan().exposure
        self.assertAlmostEqual(exposure.effective_seconds, exposure.seconds - 5.0)
        self.assertIsNone(exposure.detected_at_s)
        self.assertTrue(exposure.detected)

    def test_detection_volume_never_touched_means_no_launch(self):
        (exposure,) = self.plan([_radar(1_000.0, center=(200_000, 0, 0))]).exposure
        self.assertEqual(exposure.effective_seconds, 0.0)
        self.assertFalse(exposure.detected)

    def test_late_detection_delays_the_launch(self):
        # radar da 5 km sul bersaglio: oltre la gittata massima (quota attack <= 3000 m) quindi
        # inevitabile; con 3 km il pianificatore trova una quota che sgancia da fuori (esposizione 0)
        base = self.plan().exposure[0]
        (exposure,) = self.plan([_radar(5_000.0)]).exposure
        self.assertIsNotNone(exposure.detected_at_s)
        self.assertLess(exposure.effective_seconds, base.effective_seconds)
        # il preavviso e' dal rilevamento all'ingresso nel volume d'arma: gia' dentro all'IP -> 0
        self.assertEqual(exposure.warning_time_s, 0.0)

    def test_detection_of_another_site_does_not_count(self):
        (exposure,) = self.plan([_radar(1_000.0, source='other', center=(200_000, 0, 0))]).exposure
        self.assertAlmostEqual(exposure.effective_seconds, exposure.seconds - 5.0)

    def test_release_from_outside_the_radar_is_preferred(self):
        """Radar da 3 km: esiste una quota che sgancia da fuori e non vi entra mai."""
        profile = self.plan([_radar(3_000.0)])
        self.assertEqual(profile.weighted_exposure, 0.0)
        self.assertGreater(profile.release_ground_range_m, 3_000.0)
        self.assertFalse(profile.exposure[0].detected)

    def test_callable_detection_source_is_evaluated_per_altitude(self):
        seen = []

        def factory(altitude):
            seen.append(altitude)
            return [_radar(3_000.0)]

        WD.plan_attack_profile(A10, 'Heavy CAS', 'Mk-82', TARGET, [_sam(40_000.0, 20_000.0)], factory)
        self.assertGreater(len(set(seen)), 1)
        self.assertEqual(len(seen), len(set(seen)))      # una chiamata per quota (cache)


class TestTransitAndRealAssets(F.LoggerSilencer, unittest.TestCase):

    def test_full_route_from_home_and_back(self):
        home = Point3D(0, 150_000, 0)
        profile = WD.plan_attack_profile(FA18, 'Strike', 'Mk-83', TARGET, [_sam(6_000.0, 3_500.0)],
                                         home_point=home)
        route = profile.full_route
        self.assertIsInstance(route, Route)
        edges = list(route.edges.values())
        self.assertEqual(edges[0].wpA.point, home)
        self.assertEqual(edges[-1].wpB.point, home)
        self.assertIn('IP-RELEASE', [e.name for e in edges])
        self.assertIsNone(profile.reason)

    def test_real_site_links_interception_and_detection(self):
        blue = F.make_force('Blue', 'Blue')
        F.add_assets(blue, [F.make_vehicle(blue, 'Blue/buk', '9K37-Buk', (0.0, 0.0, 0.0))])
        (threat,) = blue.air_defense_threats()
        (detection,) = blue.air_detection_threats(3_000.0)
        self.assertEqual(threat.source_id, 'Blue/buk')
        self.assertEqual(detection.source_id, threat.source_id)

    def test_detection_factory_follows_the_radar_horizon(self):
        blue = F.make_force('Blue', 'Blue')
        buk = F.make_vehicle(blue, 'Blue/buk2', '9K37-Buk', (0.0, 0.0, 0.0))
        factory = WD.detection_threats_factory([buk])
        (low,) = factory(50.0)
        (high,) = factory(5_000.0)
        self.assertLess(low.cylinder.radius, high.cylinder.radius)


if __name__ == '__main__':
    unittest.main()
