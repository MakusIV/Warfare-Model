"""Tests per Logic/Contact_Scheduler — FASE 3 del motore di sessioni virtuali.

Lo scheduler risponde a **quando**, non a **chi vince**: ogni test qui verifica istanti,
intervalli e potature, mai un esito d'ingaggio (che e' materia della Fase 4).

Strategia di setup
------------------
* Route/Edge/Waypoint/Cylinder sono costruiti con oggetti REALI: sono classi geometriche
  pure, senza dipendenze circolari, e usare mock qui nasconderebbe proprio cio' che si vuole
  verificare (la composizione fra `Cylinder.getIntersection` e la scansione temporale della
  rotta). Stessa scelta di Test_Route.py.
* Le geometrie sono scelte perche' il risultato atteso si calcoli a mano: rotte assiali,
  velocita' tonde, cilindri centrati. Ogni classe di test dichiara la propria aritmetica.
* Gli asset sono stub minimi. Dove serve verificare il ponte verso i DATI REALI dei sensori
  (`mutual_detection_ranges`), lo stub porta il vero `Mobile.detection_range` come metodo,
  stessa tecnica di Test_Threat_AA_Factory (Vehicle non e' importabile direttamente per il
  ciclo d'import noto del progetto).
* I blocchi sono stub con la stessa superficie che lo scheduler interroga
  (`assets`/`position`/`side`/`combat_range`/`detection_range`), perche' la potatura e' una
  regola aritmetica su quei numeri e non ha bisogno di una Region vera.
"""

import logging
import unittest
from unittest.mock import patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.DataType.Cylinder import Cylinder
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS

_SCHEDULER_LOGGER = 'Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler.logger'


# ── COSTRUTTORI DI COMODO ─────────────────────────────────────────────────────

def _wp(name: str, x: float, y: float, z: float = 0.0) -> Waypoint:
    return Waypoint(name=name, point=Point3D(x, y, z), obj_reference=None)


def _edge(wpA: Waypoint, wpB: Waypoint, speed, name: str) -> Edge:
    return Edge(wpA=wpA, wpB=wpB, path_type='air', danger_level=0.0, speed=speed, name=name)


def _route(points, speed=100.0, name='route', z=0.0) -> Route:
    """Rotta su una spezzata di coordinate (x, y), tutti gli archi alla stessa velocita'."""
    waypoints = [_wp(f'W{index}', x, y, z) for index, (x, y) in enumerate(points)]
    edges = {}

    for index in range(len(waypoints) - 1):
        a, b = waypoints[index], waypoints[index + 1]
        edges[(a.name, b.name)] = _edge(a, b, speed, f'E{index}')

    return Route(route_type='air', edges=edges, name=name)


def _straight_route(speed=100.0, name='straight') -> Route:
    """(0,0) -> (1000,0): 1000 m, 10 s a 100 m/s."""
    return _route([(0, 0), (1000, 0)], speed=speed, name=name)


def _l_route(speed=100.0) -> Route:
    """(0,0) -> (1000,0) -> (1000,2000): 3000 m, 30 s a 100 m/s."""
    return _route([(0, 0), (1000, 0), (1000, 2000)], speed=speed, name='l-shaped')


class _ThreatStub:
    """Minaccia duck-typed: cio' che lo scheduler legge di un ThreatAA (cilindro + pericolo)."""

    def __init__(self, cylinder, danger_level=None, name=None):
        self.cylinder = cylinder
        self.danger_level = danger_level
        self.name = name


class _AssetStub:
    """Asset minimo con id, posizione e portata di rilevamento imposta."""

    def __init__(self, asset_id=None, position=None, ranges=None, speed=None,
                 operative=True):
        self.id = asset_id
        self._position = position
        self._ranges = ranges or {}
        self.speed = speed
        self._operative = operative

    @property
    def position(self):
        return self._position

    def is_operative(self):
        return self._operative

    def detection_range(self, mode, sensor=None, range_type='acquisition_range'):
        return self._ranges.get(mode)


class Vehicle(_AssetStub):
    """Stub il cui NOME DI CLASSE e' quello che detection_mode_for interroga."""


class Aircraft(_AssetStub):
    pass


class Ship(_AssetStub):
    pass


class _BlockStub:
    """Blocco con la sola superficie che la potatura interroga."""

    def __init__(self, name=None, side=None, position=None, assets=None,
                 combat=None, detection=None):
        self.name = name
        self.side = side
        self._position = position
        self.assets = {getattr(asset, 'id', str(index)): asset
                       for index, asset in enumerate(assets or [])}
        self._combat = combat
        self._detection = detection

    @property
    def position(self):
        return self._position

    def combat_range(self):
        return (self._combat, self._combat, 1.0, 1) if self._combat else None

    def detection_range(self, mode, sensor=None):
        value = (self._detection or {}).get(mode)
        return (value, value, 1.0, 1) if value else None


# ── A-0. SCANSIONE TEMPORALE DELLA ROTTA ──────────────────────────────────────

class TestRouteLegs(unittest.TestCase):
    """route_legs: la rotta canonica diventa una sequenza di tratti in tempo assoluto."""

    def setUp(self):
        self.route = _l_route()

    def test_geometry_precondition(self):
        """Le attese di questa classe dipendono da questi due valori."""
        self.assertAlmostEqual(float(self.route.length()), 3000.0)
        self.assertAlmostEqual(float(self.route.travelTime()), 30.0)

    def test_one_leg_per_edge(self):
        self.assertEqual(len(CS.route_legs(self.route)), 2)

    def test_legs_are_contiguous_and_cover_the_travel_time(self):
        legs = CS.route_legs(self.route)
        self.assertAlmostEqual(legs[0].t_start, 0.0)
        self.assertAlmostEqual(legs[0].t_end, 10.0)
        self.assertAlmostEqual(legs[1].t_start, 10.0)
        self.assertAlmostEqual(legs[1].t_end, 30.0)

    def test_leg_start_matches_travelTimeToEdge(self):
        """Non-regressione: l'accumulo dei tempi non deve divergere da DataType.Route."""
        legs = CS.route_legs(self.route)

        for edge, leg in zip(self.route.edges.values(), legs):
            self.assertAlmostEqual(leg.t_start, float(self.route.travelTimeToEdge(edge)))

    def test_t0_shifts_every_leg(self):
        legs = CS.route_legs(self.route, t0=1000.0)
        self.assertAlmostEqual(legs[0].t_start, 1000.0)
        self.assertAlmostEqual(legs[-1].t_end, 1030.0)

    def test_speed_override(self):
        legs = CS.route_legs(self.route, speed=200.0)
        self.assertAlmostEqual(legs[-1].t_end, 15.0)

    def test_endpoints_are_the_waypoints(self):
        legs = CS.route_legs(self.route)
        self.assertEqual(legs[0].p_start, (0.0, 0.0, 0.0))
        self.assertEqual(legs[-1].p_end, (1000.0, 2000.0, 0.0))

    def test_empty_route_returns_no_legs(self):
        with patch(_SCHEDULER_LOGGER):
            self.assertEqual(CS.route_legs(Route(route_type='air', edges={}, name='empty')), [])

    def test_undefined_speed_returns_no_legs_and_warns(self):
        """Dato mancante: lista vuota e log, mai eccezione (stessa politica di positionAtTime)."""
        route = _straight_route(speed=None)

        with patch(_SCHEDULER_LOGGER) as mock_logger:
            self.assertEqual(CS.route_legs(route), [])

        mock_logger.warning.assert_called_once()

    def test_horizon_clips_the_last_leg(self):
        legs = CS.route_legs(self.route, horizon=20.0)
        self.assertAlmostEqual(legs[-1].t_end, 20.0)
        self.assertEqual(legs[-1].p_end, (1000.0, 1000.0, 0.0))

    def test_negative_horizon_raises(self):
        """Argomento fuori dominio: qui l'eccezione ci vuole."""
        with self.assertRaises(ValueError):
            CS.route_legs(self.route, horizon=-1.0)


class TestStaticLegs(unittest.TestCase):
    """static_legs: un asset fermo e' un tratto come gli altri."""

    def test_single_leg_with_coincident_endpoints(self):
        legs = CS.static_legs(Point3D(10, 20, 30), 5.0, 65.0)
        self.assertEqual(len(legs), 1)
        self.assertEqual(legs[0].p_start, legs[0].p_end)
        self.assertAlmostEqual(legs[0].duration, 60.0)

    def test_missing_position_returns_no_legs(self):
        with patch(_SCHEDULER_LOGGER):
            self.assertEqual(CS.static_legs(None, 0.0, 10.0), [])

    def test_inverted_interval_raises(self):
        with self.assertRaises(ValueError):
            CS.static_legs(Point3D(0, 0, 0), 10.0, 0.0)


class TestPositionOnLegs(unittest.TestCase):
    """position_on_legs deve coincidere con Route.positionAtTime, che e' la fonte."""

    def setUp(self):
        self.route = _l_route()
        self.legs = CS.route_legs(self.route)

    def test_matches_route_positionAtTime(self):
        for t in (0.0, 2.5, 10.0, 17.5, 30.0):
            expected = self.route.positionAtTime(t)
            actual = CS.position_on_legs(self.legs, t)
            self.assertAlmostEqual(actual[0], float(expected.x), places=6)
            self.assertAlmostEqual(actual[1], float(expected.y), places=6)

    def test_before_start_saturates_on_first_point(self):
        self.assertEqual(CS.position_on_legs(self.legs, -100.0), (0.0, 0.0, 0.0))

    def test_after_end_saturates_on_last_point(self):
        self.assertEqual(CS.position_on_legs(self.legs, 1e6), (1000.0, 2000.0, 0.0))

    def test_no_legs_returns_none(self):
        self.assertIsNone(CS.position_on_legs([], 0.0))


class TestLegsSpan(unittest.TestCase):
    """legs_span: fuori da qui l'asset non esiste per lo scheduler."""

    def test_span_of_a_route(self):
        self.assertEqual(CS.legs_span(CS.route_legs(_l_route(), t0=100.0)), (100.0, 130.0))

    def test_no_legs_returns_none(self):
        self.assertIsNone(CS.legs_span([]))


# ── A. ROTTA CONTRO VOLUME DI MINACCIA ────────────────────────────────────────

class TestThreatWindows(unittest.TestCase):
    """Rotta (0,0)->(1000,0) a 100 m/s; cilindro centro (500,0), raggio 200, quota 0-1000.

    La rotta e' dentro il volume da x=300 a x=700, cioe' da t=3 a t=7.
    """

    def setUp(self):
        self.route = _straight_route()
        self.cylinder = Cylinder(Point3D(500, 0, 0), 200.0, 1000.0)

    def test_crossing_gives_one_window(self):
        windows = CS.threat_windows(self.route, self.cylinder)
        self.assertEqual(len(windows), 1)
        self.assertAlmostEqual(windows[0].t_entry, 3.0, places=6)
        self.assertAlmostEqual(windows[0].t_exit, 7.0, places=6)

    def test_duration_is_the_exposure_time(self):
        self.assertAlmostEqual(CS.threat_windows(self.route, self.cylinder)[0].duration,
                               4.0, places=6)

    def test_entry_and_exit_points(self):
        window = CS.threat_windows(self.route, self.cylinder)[0]
        self.assertAlmostEqual(float(window.entry_point.x), 300.0, places=4)
        self.assertAlmostEqual(float(window.exit_point.x), 700.0, places=4)

    def test_accepts_a_threat_object_and_reads_its_danger_level(self):
        threat = _ThreatStub(self.cylinder, danger_level=0.42, name='osa-1')
        window = CS.threat_windows(self.route, threat, threat_id='osa-1')[0]
        self.assertEqual(window.threat_id, 'osa-1')
        self.assertAlmostEqual(window.danger_level, 0.42)

    def test_t0_shifts_the_window(self):
        window = CS.threat_windows(self.route, self.cylinder, t0=500.0)[0]
        self.assertAlmostEqual(window.t_entry, 503.0, places=6)
        self.assertAlmostEqual(window.t_exit, 507.0, places=6)

    def test_route_far_away_gives_no_window(self):
        far = _route([(0, 100000), (1000, 100000)])
        self.assertEqual(CS.threat_windows(far, self.cylinder), [])

    def test_route_entirely_inside_the_volume(self):
        """Caso che Cylinder.getIntersection non distingue da 'nessuna intersezione'."""
        inside = _route([(450, 0), (550, 0)], speed=10.0)
        windows = CS.threat_windows(inside, self.cylinder)
        self.assertEqual(len(windows), 1)
        self.assertAlmostEqual(windows[0].t_entry, 0.0, places=6)
        self.assertAlmostEqual(windows[0].t_exit, 10.0, places=6)

    def test_route_starting_inside_the_volume(self):
        outbound = _route([(500, 0), (1500, 0)], speed=100.0)
        windows = CS.threat_windows(outbound, self.cylinder)
        self.assertEqual(len(windows), 1)
        self.assertAlmostEqual(windows[0].t_entry, 0.0, places=6)
        self.assertAlmostEqual(windows[0].t_exit, 2.0, places=6)

    def test_consecutive_edges_are_merged_into_one_window(self):
        """Entrare su un arco e uscire due archi dopo e' UNA esposizione, non tre."""
        route = _route([(0, 0), (400, 0), (600, 0), (1000, 0)], speed=100.0)
        windows = CS.threat_windows(route, self.cylinder)
        self.assertEqual(len(windows), 1)
        self.assertAlmostEqual(windows[0].t_entry, 3.0, places=6)
        self.assertAlmostEqual(windows[0].t_exit, 7.0, places=6)
        self.assertEqual(len(windows[0].edge_names), 3)

    def test_two_separate_crossings_stay_separate(self):
        """(0,0)->(1000,0)->(1000,-1000)->(0,-1000)->(0,0): rientra nel volume alla fine? no.

        Qui la rotta attraversa il volume, se ne allontana e lo riattraversa: due finestre.
        """
        route = _route([(0, 0), (1000, 0), (1000, 500), (0, 500), (0, 0), (1000, 0)],
                       speed=100.0)
        windows = CS.threat_windows(route, self.cylinder)
        self.assertEqual(len(windows), 2)
        self.assertLess(windows[0].t_exit, windows[1].t_entry)

    def test_horizon_clips_the_window(self):
        window = CS.threat_windows(self.route, self.cylinder, horizon=5.0)[0]
        self.assertAlmostEqual(window.t_entry, 3.0, places=6)
        self.assertAlmostEqual(window.t_exit, 5.0, places=6)

    def test_window_entirely_beyond_the_horizon_is_dropped(self):
        self.assertEqual(CS.threat_windows(self.route, self.cylinder, horizon=1.0), [])

    def test_altitude_matters(self):
        """Una rotta che scavalca il volume non e' esposta: e' il senso del cilindro."""
        high = _route([(0, 0), (1000, 0)], speed=100.0, z=5000.0)
        self.assertEqual(CS.threat_windows(high, self.cylinder), [])

    def test_threat_without_cylinder_warns_and_returns_empty(self):
        with patch(_SCHEDULER_LOGGER) as mock_logger:
            self.assertEqual(CS.threat_windows(self.route, None, threat_id='x'), [])

        mock_logger.warning.assert_called_once()

    def test_unschedulable_route_returns_empty(self):
        with patch(_SCHEDULER_LOGGER):
            self.assertEqual(CS.threat_windows(_straight_route(speed=None), self.cylinder), [])


class TestRouteThreatWindows(unittest.TestCase):
    """Piu' minacce in una passata, con ordinamento deterministico."""

    def setUp(self):
        self.route = _route([(0, 0), (3000, 0)], speed=100.0)
        self.near = Cylinder(Point3D(500, 0, 0), 200.0, 1000.0)
        self.far = Cylinder(Point3D(2500, 0, 0), 200.0, 1000.0)

    def test_mapping_input_keeps_the_ids(self):
        windows = CS.route_threat_windows(self.route, {'far': self.far, 'near': self.near})
        self.assertEqual([w.threat_id for w in windows], ['near', 'far'])

    def test_sorted_by_entry_time(self):
        windows = CS.route_threat_windows(self.route, {'far': self.far, 'near': self.near})
        self.assertLess(windows[0].t_entry, windows[1].t_entry)

    def test_iterable_input_takes_the_id_from_name(self):
        threats = [_ThreatStub(self.far, name='far'), _ThreatStub(self.near, name='near')]
        windows = CS.route_threat_windows(self.route, threats)
        self.assertEqual([w.threat_id for w in windows], ['near', 'far'])

    def test_no_threats_returns_empty(self):
        self.assertEqual(CS.route_threat_windows(self.route, []), [])


# ── B. CPA/TCPA ───────────────────────────────────────────────────────────────

class TestClosestPointOfApproach(unittest.TestCase):
    """t* = -(dr . dv) / |dv|^2, clampato ai tratti e all'esistenza di entrambe le rotte."""

    def test_perpendicular_crossing_at_the_same_instant(self):
        """A lungo x, B lungo y, entrambi a 100 m/s: si toccano a (500,0) a t=5."""
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(500, -500), (500, 500)]))
        cpa = CS.closest_point_of_approach(legs_a, legs_b)
        self.assertAlmostEqual(cpa.time, 5.0, places=6)
        self.assertAlmostEqual(cpa.distance, 0.0, places=6)
        self.assertFalse(cpa.degenerate)

    def test_moving_against_static(self):
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.static_legs(Point3D(500, 300, 0), 0.0, 10.0)
        cpa = CS.closest_point_of_approach(legs_a, legs_b)
        self.assertAlmostEqual(cpa.time, 5.0, places=6)
        self.assertAlmostEqual(cpa.distance, 300.0, places=6)

    def test_parallel_same_speed_is_degenerate_without_dividing_by_zero(self):
        """|dv|^2 ~ 0: la distanza e' costante, l'istante non e' definito."""
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(0, 400), (1000, 400)]))
        cpa = CS.closest_point_of_approach(legs_a, legs_b)
        self.assertTrue(cpa.degenerate)
        self.assertAlmostEqual(cpa.distance, 400.0, places=6)

    def test_both_static_is_degenerate(self):
        cpa = CS.closest_point_of_approach(CS.static_legs(Point3D(0, 0, 0), 0.0, 100.0),
                                           CS.static_legs(Point3D(0, 50, 0), 0.0, 100.0))
        self.assertTrue(cpa.degenerate)
        self.assertAlmostEqual(cpa.distance, 50.0, places=6)

    def test_diverging_routes_have_their_cpa_at_the_start(self):
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(0, 100), (-1000, 100)]))
        cpa = CS.closest_point_of_approach(legs_a, legs_b)
        self.assertAlmostEqual(cpa.time, 0.0, places=6)
        self.assertAlmostEqual(cpa.distance, 100.0, places=6)

    def test_no_temporal_overlap_returns_none(self):
        """Nessuno dei due esiste prima di partire o dopo essere arrivato."""
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]), t0=0.0)
        legs_b = CS.route_legs(_route([(0, 0), (1000, 0)]), t0=1000.0)
        self.assertIsNone(CS.closest_point_of_approach(legs_a, legs_b))

    def test_start_offset_moves_the_cpa(self):
        """B parte 5 s dopo: l'incrocio non e' piu' simultaneo."""
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(500, -500), (500, 500)]), t0=5.0)
        cpa = CS.closest_point_of_approach(legs_a, legs_b)
        self.assertGreater(cpa.distance, 0.0)

    def test_polyline_cpa_is_not_the_whole_route_cpa(self):
        """Il minimo sta su un waypoint interno: la formula sulla rotta intera lo mancherebbe.

        A e' fermo nell'origine; B va da (0,1000) a (0,100) e torna a (0,1000), 100 m/s.
        Gli estremi di B distano entrambi 1000 m: chi applicasse il CPA agli estremi della
        rotta direbbe 1000. Il vero massimo avvicinamento e' 100 m a t = 9 s.
        """
        legs_a = CS.static_legs(Point3D(0, 0, 0), 0.0, 100.0)
        legs_b = CS.route_legs(_route([(0, 1000), (0, 100), (0, 1000)], speed=100.0))
        cpa = CS.closest_point_of_approach(legs_a, legs_b)
        self.assertAlmostEqual(cpa.distance, 100.0, places=5)
        self.assertAlmostEqual(cpa.time, 9.0, places=5)

    def test_no_legs_returns_none(self):
        self.assertIsNone(CS.closest_point_of_approach([], CS.static_legs(Point3D(0, 0, 0), 0, 1)))


class TestRangeIntervals(unittest.TestCase):
    """|dr + dv s|^2 = R^2 sui sottointervalli a velocita' relativa costante."""

    def test_known_analytic_interval(self):
        """A: (100t, 0). B: (500, -500+100t). |d|^2 = 2(500-100t)^2 = 200^2 -> t = 3.586, 6.414."""
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(500, -500), (500, 500)]))
        intervals = CS.range_intervals(legs_a, legs_b, 200.0)
        self.assertEqual(len(intervals), 1)
        self.assertAlmostEqual(intervals[0][0], 3.5857864376, places=6)
        self.assertAlmostEqual(intervals[0][1], 6.4142135623, places=6)

    def test_radius_too_small_gives_no_interval(self):
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(0, 5000), (1000, 5000)]))
        self.assertEqual(CS.range_intervals(legs_a, legs_b, 100.0), [])

    def test_constant_distance_within_range_covers_the_whole_overlap(self):
        legs_a = CS.route_legs(_route([(0, 0), (1000, 0)]))
        legs_b = CS.route_legs(_route([(0, 50), (1000, 50)]))
        intervals = CS.range_intervals(legs_a, legs_b, 100.0)
        self.assertEqual(len(intervals), 1)
        self.assertAlmostEqual(intervals[0][0], 0.0, places=6)
        self.assertAlmostEqual(intervals[0][1], 10.0, places=6)

    def test_two_disjoint_intervals(self):
        """B si avvicina, si allontana e torna: due passaggi dentro il raggio, non uno."""
        legs_a = CS.static_legs(Point3D(0, 0, 0), 0.0, 100.0)
        legs_b = CS.route_legs(_route([(0, 200), (0, 50), (0, 400), (0, 50)], speed=10.0))
        intervals = CS.range_intervals(legs_a, legs_b, 100.0)
        self.assertEqual(len(intervals), 2)
        self.assertAlmostEqual(intervals[0][0], 10.0, places=5)
        self.assertAlmostEqual(intervals[0][1], 20.0, places=5)
        self.assertAlmostEqual(intervals[1][0], 80.0, places=5)
        self.assertAlmostEqual(intervals[1][1], 85.0, places=5)

    def test_negative_radius_raises(self):
        with self.assertRaises(ValueError):
            CS.range_intervals(CS.static_legs(Point3D(0, 0, 0), 0, 1),
                               CS.static_legs(Point3D(0, 0, 0), 0, 1), -1.0)

    def test_no_overlap_returns_empty(self):
        legs_a = CS.static_legs(Point3D(0, 0, 0), 0.0, 10.0)
        legs_b = CS.static_legs(Point3D(0, 0, 0), 100.0, 110.0)
        self.assertEqual(CS.range_intervals(legs_a, legs_b, 1000.0), [])


# ── B-bis. FINESTRE DI CONTATTO ───────────────────────────────────────────────

class TestDetectionModeFor(unittest.TestCase):
    """Il modo dice in che dominio sta il BERSAGLIO, non l'osservatore."""

    def test_vehicle_is_ground(self):
        self.assertEqual(CS.detection_mode_for(Vehicle()), 'ground')

    def test_aircraft_is_air(self):
        self.assertEqual(CS.detection_mode_for(Aircraft()), 'air')

    def test_ship_is_sea(self):
        self.assertEqual(CS.detection_mode_for(Ship()), 'sea')

    def test_unknown_class_returns_none(self):
        self.assertIsNone(CS.detection_mode_for(object()))


class TestMutualDetectionRanges(unittest.TestCase):
    """Ponte verso i dati sensore reali: ognuno e' interrogato sul dominio dell'altro."""

    class _RealSensorVehicle:
        """Stub che porta il vero Mobile.detection_range (v. Test_Threat_AA_Factory)."""

        detection_range = Mobile.detection_range
        _sensor_range_km = staticmethod(Mobile._sensor_range_km)

        def __init__(self, model):
            self._model = model
            self.id = model

    def setUp(self):
        # I registry emettono warning noti sui propri dati, irrilevanti qui.
        logging.getLogger('Code.Dynamic_War_Manager.Source.Asset.Mobile').setLevel(logging.ERROR)

    def test_real_registry_range_against_an_aircraft(self):
        """9A33-Osa vede un bersaglio 'air' a 30 km: il valore arriva fino allo scheduler."""
        observer = self._RealSensorVehicle('9A33-Osa')
        range_a, range_b = CS.mutual_detection_ranges(observer, Aircraft(asset_id='target'))
        self.assertAlmostEqual(range_a, 30000.0)

    def test_target_without_detection_range_gives_none(self):
        observer = self._RealSensorVehicle('9A33-Osa')
        _, range_b = CS.mutual_detection_ranges(observer, Aircraft(asset_id='target'))
        self.assertIsNone(range_b)

    def test_unclassifiable_target_gives_none(self):
        with patch(_SCHEDULER_LOGGER):
            ranges = CS.mutual_detection_ranges(Vehicle(ranges={'ground': 5000.0}), object())
        self.assertIsNone(ranges[0])

    def test_stub_ranges_are_read_on_the_other_domain(self):
        vehicle = Vehicle(asset_id='v', ranges={'air': 12000.0, 'ground': 3000.0})
        aircraft = Aircraft(asset_id='a', ranges={'air': 60000.0, 'ground': 80000.0})
        range_v, range_a = CS.mutual_detection_ranges(vehicle, aircraft)
        self.assertAlmostEqual(range_v, 12000.0)   # il veicolo guarda un bersaglio 'air'
        self.assertAlmostEqual(range_a, 80000.0)   # l'aereo guarda un bersaglio 'ground'


class TestContactWindows(unittest.TestCase):
    """Chi vede per primo, da quando, e da quando si vedono entrambi.

    A e' fermo in (0,0,0); B passa da (0,-1000) a (0,1000) a 100 m/s, quindi la distanza
    e' |1000 - 100t| e vale 400 a t = 6 e t = 14, 200 a t = 8 e t = 12.
    """

    def setUp(self):
        self.legs_a = CS.static_legs(Point3D(0, 0, 0), 0.0, 20.0)
        self.legs_b = CS.route_legs(_route([(0, -1000), (0, 1000)], speed=100.0))
        self.asset_a = Vehicle(asset_id='defender')
        self.asset_b = Aircraft(asset_id='raider')

    def test_asymmetric_ranges_give_one_window_on_the_longer_one(self):
        windows = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                     range_a=400.0, range_b=200.0)
        self.assertEqual(len(windows), 1)
        self.assertAlmostEqual(windows[0].t_start, 6.0, places=5)
        self.assertAlmostEqual(windows[0].t_end, 14.0, places=5)

    def test_first_detector_is_the_one_with_the_longer_range(self):
        window = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                    range_a=400.0, range_b=200.0)[0]
        self.assertEqual(window.first_detector, 'a')

    def test_mutual_sub_window_uses_the_shorter_range(self):
        window = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                    range_a=400.0, range_b=200.0)[0]
        self.assertTrue(window.is_mutual)
        self.assertAlmostEqual(window.t_mutual_start, 8.0, places=5)
        self.assertAlmostEqual(window.t_mutual_end, 12.0, places=5)

    def test_cpa_inside_the_window(self):
        window = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                    range_a=400.0, range_b=200.0)[0]
        self.assertAlmostEqual(window.t_cpa, 10.0, places=5)
        self.assertAlmostEqual(window.distance_cpa, 0.0, places=4)

    def test_equal_ranges_detect_together(self):
        window = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                    range_a=400.0, range_b=400.0)[0]
        self.assertEqual(window.first_detector, 'both')
        self.assertTrue(window.is_mutual)

    def test_single_range_means_no_mutual_detection(self):
        window = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                    range_a=400.0, range_b=0.0)[0]
        self.assertFalse(window.is_mutual)
        self.assertEqual(window.first_detector, 'a')

    def test_ids_are_domain_ids(self):
        window = CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, self.legs_b,
                                    range_a=400.0, range_b=200.0)[0]
        self.assertEqual((window.asset_a_id, window.asset_b_id), ('defender', 'raider'))

    def test_range_too_short_gives_no_window(self):
        far_b = CS.route_legs(_route([(50000, -1000), (50000, 1000)], speed=100.0))
        self.assertEqual(CS.contact_windows(self.asset_a, self.legs_a, self.asset_b, far_b,
                                            range_a=400.0, range_b=200.0), [])

    def test_no_declared_range_gives_no_window_and_logs(self):
        with patch(_SCHEDULER_LOGGER) as mock_logger:
            self.assertEqual(CS.contact_windows(Vehicle(), self.legs_a,
                                                Aircraft(), self.legs_b), [])
        mock_logger.debug.assert_called()

    def test_no_legs_gives_no_window(self):
        with patch(_SCHEDULER_LOGGER):
            self.assertEqual(CS.contact_windows(self.asset_a, [], self.asset_b, self.legs_b,
                                                range_a=400.0, range_b=200.0), [])

    def test_ranges_are_derived_from_the_assets_when_not_given(self):
        asset_a = Vehicle(asset_id='defender', ranges={'air': 400.0})
        asset_b = Aircraft(asset_id='raider', ranges={'ground': 200.0})
        window = CS.contact_windows(asset_a, self.legs_a, asset_b, self.legs_b)[0]
        self.assertAlmostEqual(window.range_a, 400.0)
        self.assertAlmostEqual(window.range_b, 200.0)


# ── C. POTATURA GERARCHICA ────────────────────────────────────────────────────

class TestBlockMaxSpeed(unittest.TestCase):
    """L'inviluppo di movimento deve essere conservativo: sottostimarlo scarta veri contatti."""

    def test_reads_the_canonical_profile(self):
        block = _BlockStub(assets=[_AssetStub('a', speed={'nominal': 10.0, 'max': 25.0})])
        self.assertAlmostEqual(CS.block_max_speed(block), 25.0)

    def test_reads_the_off_road_branch_too(self):
        block = _BlockStub(assets=[_AssetStub('a', speed={'nominal': 5.0, 'max': 8.0,
                                                          'off_road': {'max': 30.0}})])
        self.assertAlmostEqual(CS.block_max_speed(block), 30.0)

    def test_non_operative_assets_are_ignored(self):
        block = _BlockStub(assets=[_AssetStub('a', speed={'max': 99.0}, operative=False)])
        self.assertAlmostEqual(CS.block_max_speed(block), 0.0)

    def test_block_without_assets_is_static(self):
        self.assertAlmostEqual(CS.block_max_speed(_BlockStub()), 0.0)


class TestBlockReach(unittest.TestCase):
    """La portata del blocco e' il massimo, non la mediana: basta un sensore lungo."""

    def test_takes_the_longer_of_combat_and_detection(self):
        block = _BlockStub(combat=5000.0, detection={'air': 30000.0})
        self.assertAlmostEqual(CS.block_reach(block), 30000.0)

    def test_restricted_to_one_mode(self):
        block = _BlockStub(combat=5000.0, detection={'air': 30000.0, 'ground': 8000.0})
        self.assertAlmostEqual(CS.block_reach(block, mode='ground'), 8000.0)

    def test_block_without_ranges_has_zero_reach(self):
        self.assertAlmostEqual(CS.block_reach(_BlockStub()), 0.0)


class TestBlockPairCandidates(unittest.TestCase):
    """Si scarta SOLO quando il contatto e' geometricamente impossibile."""

    def _blocks(self, distance, speed=0.0, reach=0.0):
        asset = _AssetStub('a', speed={'max': speed}) if speed else _AssetStub('a')
        blue = _BlockStub('blue', 'blue', Point3D(0, 0, 0), [asset], combat=reach or None)
        red = _BlockStub('red', 'red', Point3D(distance, 0, 0), [asset], combat=reach or None)
        return [blue], [red]

    def test_far_blocks_are_pruned(self):
        blue, red = self._blocks(1_000_000.0, speed=100.0, reach=10_000.0)
        self.assertEqual(CS.block_pair_candidates(blue, red, horizon=3600.0), [])

    def test_close_blocks_are_kept(self):
        blue, red = self._blocks(5_000.0, speed=100.0, reach=10_000.0)
        self.assertEqual(len(CS.block_pair_candidates(blue, red, horizon=3600.0)), 1)

    def test_movement_envelope_alone_can_close_the_gap(self):
        """Fermi sarebbero scartati; a 100 m/s per un'ora no."""
        blue, red = self._blocks(500_000.0, speed=100.0)
        self.assertEqual(CS.block_pair_candidates(blue, red, horizon=1.0), [])
        self.assertEqual(len(CS.block_pair_candidates(blue, red, horizon=3600.0)), 1)

    def test_margin_widens_the_envelope(self):
        blue, red = self._blocks(1_000.0)
        self.assertEqual(CS.block_pair_candidates(blue, red, horizon=0.0), [])
        self.assertEqual(len(CS.block_pair_candidates(blue, red, horizon=0.0, margin=2_000.0)), 1)

    def test_block_without_position_is_never_pruned(self):
        blue = [_BlockStub('blue', 'blue', None)]
        red = [_BlockStub('red', 'red', Point3D(1e9, 0, 0))]

        with patch(_SCHEDULER_LOGGER):
            self.assertEqual(len(CS.block_pair_candidates(blue, red, horizon=1.0)), 1)

    def test_same_side_pairs_are_skipped_by_default(self):
        blue = [_BlockStub('b1', 'blue', Point3D(0, 0, 0))]
        other = [_BlockStub('b2', 'blue', Point3D(10, 0, 0))]
        self.assertEqual(CS.block_pair_candidates(blue, other, horizon=1.0, margin=1_000.0), [])
        self.assertEqual(len(CS.block_pair_candidates(blue, other, horizon=1.0, margin=1_000.0,
                                                      skip_same_side=False)), 1)

    def test_block_items_are_accepted_and_returned_as_given(self):
        """Region.get_blocks_by_criteria restituisce BlockItem, non Block."""
        class _Item:
            def __init__(self, block):
                self.block = block

        blue = [_Item(_BlockStub('blue', 'blue', Point3D(0, 0, 0)))]
        red = [_Item(_BlockStub('red', 'red', Point3D(100, 0, 0)))]
        pairs = CS.block_pair_candidates(blue, red, horizon=0.0, margin=1_000.0)
        self.assertEqual(pairs, [(blue[0], red[0])])

    def test_negative_horizon_raises(self):
        blue, red = self._blocks(100.0)
        with self.assertRaises(ValueError):
            CS.block_pair_candidates(blue, red, horizon=-1.0)

    def test_empty_inputs_give_no_pairs(self):
        self.assertEqual(CS.block_pair_candidates([], [], horizon=10.0), [])


# ── ORCHESTRAZIONE ────────────────────────────────────────────────────────────

class TestScheduleContacts(unittest.TestCase):
    """Potatura, poi CPA solo sulle coppie superstiti, con ordinamento deterministico."""

    def setUp(self):
        self.raider = Aircraft(asset_id='raider', position=Point3D(0, -1000, 0),
                               ranges={'ground': 200.0}, speed={'max': 100.0})
        self.sam = Vehicle(asset_id='sam', position=Point3D(0, 0, 0),
                           ranges={'air': 400.0})
        self.blue = [_BlockStub('blue', 'blue', Point3D(0, -1000, 0), [self.raider],
                                detection={'ground': 200.0})]
        self.red = [_BlockStub('red', 'red', Point3D(0, 0, 0), [self.sam],
                               detection={'air': 400.0})]
        self.route = _route([(0, -1000), (0, 1000)], speed=100.0)

    def test_moving_asset_against_static_asset(self):
        windows = CS.schedule_contacts(self.blue, self.red, horizon=20.0,
                                       routes={'raider': self.route})
        self.assertEqual(len(windows), 1)
        self.assertAlmostEqual(windows[0].t_start, 6.0, places=5)
        self.assertAlmostEqual(windows[0].t_end, 14.0, places=5)

    def test_asset_without_route_is_treated_as_static(self):
        """Il caso piu' comune in campagna: un sito SAM non ha una rotta."""
        windows = CS.schedule_contacts(self.blue, self.red, horizon=20.0,
                                       routes={'raider': self.route})
        self.assertEqual(windows[0].asset_b_id, 'sam')

    def test_start_offset_is_honoured(self):
        windows = CS.schedule_contacts(self.blue, self.red, horizon=100.0,
                                       routes={'raider': self.route},
                                       starts={'raider': 50.0})
        self.assertAlmostEqual(windows[0].t_start, 56.0, places=5)

    def test_pruned_pair_produces_nothing(self):
        far = [_BlockStub('red', 'red', Point3D(0, 1e7, 0), [self.sam], detection={'air': 400.0})]
        self.assertEqual(CS.schedule_contacts(self.blue, far, horizon=20.0,
                                              routes={'raider': self.route}), [])

    def test_result_is_sorted_deterministically(self):
        """L'ordine fa parte del contratto di riproducibilita', non e' un dettaglio."""
        second = Vehicle(asset_id='aaa-sam', position=Point3D(0, 200, 0), ranges={'air': 400.0})
        red = [_BlockStub('red', 'red', Point3D(0, 100, 0), [self.sam, second],
                          detection={'air': 400.0})]
        windows = CS.schedule_contacts(self.blue, red, horizon=30.0,
                                       routes={'raider': self.route})
        keys = [(w.t_start, w.asset_a_id, w.asset_b_id) for w in windows]
        self.assertEqual(keys, sorted(keys))

    def test_negative_horizon_raises(self):
        with self.assertRaises(ValueError):
            CS.schedule_contacts(self.blue, self.red, horizon=-1.0)

    def test_unschedulable_route_falls_back_to_the_static_position(self):
        broken = _route([(0, -1000), (0, 1000)], speed=None)

        with patch(_SCHEDULER_LOGGER):
            windows = CS.schedule_contacts(self.blue, self.red, horizon=20.0,
                                           routes={'raider': broken})

        # Fermo a 1000 m dal SAM, fuori portata: nessun contatto, ma nessuna eccezione.
        self.assertEqual(windows, [])


if __name__ == '__main__':
    unittest.main()
