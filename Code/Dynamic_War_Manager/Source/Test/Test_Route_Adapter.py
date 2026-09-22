"""Tests per Logic/Route_Adapter — la frontiera verso il modello di rotta canonico.

Il progetto ha avuto per lungo tempo tre modelli Route/Edge/Waypoint incompatibili; la
decisione registrata in Route_Adapter conferma `DataType.Route` come unico modello di
dominio e degrada quelli dei due Route Manager a stato di lavoro privato. Questi test
verificano il ponte: che il risultato di un path-finding diventi una rotta canonica
effettivamente utilizzabile dal motore di sessione (`travelTime`, `positionAtTime`).

Si usano oggetti reali, non mock: sia i tipi canonici (classi geometriche pure) sia i tipi
interni dei due pianificatori, perche' e' proprio la loro forma cio' che l'adattatore deve
accettare.
"""

import unittest

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.Logic import Route_Adapter
from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import (
    Edge as AirEdge,
    Path as AirPath,
    Waypoint as AirWaypoint,
)
from Code.Dynamic_War_Manager.Source.Logic.Ground_Route_Manager import (
    Edge as GroundEdge,
    NavigationGraph,
    Waypoint as GroundWaypoint,
)


def _air_wp(name, x, y, z):
    return AirWaypoint(name, Point3D(x, y, z), None)


def _air_edge(name, a, b, speed=100.0, danger=0.0):
    edge = AirEdge(name, 0, a, b, speed)
    edge.danger = danger
    return edge


def _air_path(speed=100.0):
    """A(0,0,0) -> B(1000,0,0) -> C(1000,2000,0): 3000 m."""
    a, b, c = _air_wp('A', 0, 0, 0), _air_wp('B', 1000, 0, 0), _air_wp('C', 1000, 2000, 0)
    return AirPath([_air_edge('AB', a, b, speed, 0.2), _air_edge('BC', b, c, speed, 0.4)])


class TestAirConversion(unittest.TestCase):

    def test_returns_canonical_route(self):
        route = Route_Adapter.to_canonical_route(_air_path(), name='ingress')
        self.assertIsInstance(route, Route)
        self.assertEqual(route.name, 'ingress')
        self.assertEqual(route.route_type, 'air')
        self.assertEqual(len(route.edges), 2)

    def test_geometry_and_time_are_preserved(self):
        route = Route_Adapter.to_canonical_route(_air_path(speed=100.0))
        self.assertAlmostEqual(float(route.length()), 3000.0, places=6)
        self.assertAlmostEqual(float(route.travelTime()), 30.0, places=6)

    def test_position_at_time_works_on_the_converted_route(self):
        """La ragione per cui esiste la conversione: positionAtTime non esiste sul tipo interno."""
        route = Route_Adapter.to_canonical_route(_air_path(speed=100.0))
        self.assertEqual(route.positionAtTime(5.0), Point3D(500, 0, 0))
        self.assertEqual(route.positionAtTime(20.0), Point3D(1000, 1000, 0))

    def test_danger_level_is_carried_over(self):
        route = Route_Adapter.to_canonical_route(_air_path())
        self.assertAlmostEqual(route.max_danger_level(), 0.4)
        self.assertAlmostEqual(route.min_danger_level(), 0.2)

    def test_speed_override(self):
        route = Route_Adapter.to_canonical_route(_air_path(speed=100.0), speed=200.0)
        self.assertAlmostEqual(float(route.travelTime()), 15.0, places=6)

    def test_consecutive_edges_share_the_junction_waypoint(self):
        route = Route_Adapter.to_canonical_route(_air_path())
        edges = list(route.edges.values())
        self.assertIs(edges[0].wpB, edges[1].wpA)

    def test_duplicate_source_names_are_disambiguated(self):
        """Nomi duplicati romperebbero Route.getWaypoints (heap su tuple con Waypoint)."""
        a, b, c = _air_wp('wp', 0, 0, 0), _air_wp('wp', 1000, 0, 0), _air_wp('wp', 1000, 2000, 0)
        path = AirPath([_air_edge('AB', a, b), _air_edge('BC', b, c)])
        route = Route_Adapter.to_canonical_route(path)
        names = [wp.name for wp in {id(e.wpA): e.wpA for e in route.edges.values()}.values()]
        self.assertEqual(len(names), len(set(names)))

    def test_zero_length_edges_are_skipped(self):
        a, b = _air_wp('A', 0, 0, 0), _air_wp('B', 1000, 0, 0)
        path = AirPath([_air_edge('AA', a, _air_wp('A2', 0, 0, 0)), _air_edge('AB', a, b)])
        route = Route_Adapter.to_canonical_route(path)
        self.assertEqual(len(route.edges), 1)

    def test_vertical_climb_is_representable(self):
        """Salita verticale pura: la proiezione 2D e' degenere, ma l'arco resta valido."""
        a, b = _air_wp('A', 0, 0, 0), _air_wp('B', 0, 0, 5000)
        route = Route_Adapter.to_canonical_route(AirPath([_air_edge('AB', a, b, 100.0)]))
        self.assertIsNotNone(route)
        self.assertAlmostEqual(float(route.length()), 5000.0, places=6)

    def test_none_container_returns_none(self):
        self.assertIsNone(Route_Adapter.to_canonical_route(None))

    def test_empty_container_returns_none(self):
        self.assertIsNone(Route_Adapter.to_canonical_route(AirPath([])))

    def test_all_degenerate_returns_none(self):
        a = _air_wp('A', 0, 0, 0)
        path = AirPath([_air_edge('AA', a, _air_wp('A2', 0, 0, 0))])
        self.assertIsNone(Route_Adapter.to_canonical_route(path))

    def test_bad_path_type_raises(self):
        with self.assertRaises(ValueError):
            Route_Adapter.to_canonical_route(_air_path(), path_type='nonesiste')

    def test_bad_route_type_raises(self):
        with self.assertRaises(ValueError):
            Route_Adapter.to_canonical_route(_air_path(), route_type='nonesiste')

    def test_accepts_the_internal_route_dict_form(self):
        """Il pianificatore aereo restituisce una Route interna (edges dict), non un Path."""
        internal_route = _air_path().to_route()
        route = Route_Adapter.to_canonical_route(internal_route)
        self.assertEqual(len(route.edges), 2)


class TestRouteTypeFromPathTypes(unittest.TestCase):

    def test_single_family(self):
        self.assertEqual(Route_Adapter.route_type_from_path_types(['onroad', 'offroad']), 'ground')
        self.assertEqual(Route_Adapter.route_type_from_path_types(['air']), 'air')
        self.assertEqual(Route_Adapter.route_type_from_path_types(['water']), 'water')

    def test_mixed_families(self):
        self.assertEqual(Route_Adapter.route_type_from_path_types(['onroad', 'water']), 'mixed')

    def test_empty_or_unknown(self):
        self.assertIsNone(Route_Adapter.route_type_from_path_types([]))
        self.assertIsNone(Route_Adapter.route_type_from_path_types(['boh']))


class TestGroundConversion(unittest.TestCase):

    def setUp(self):
        self.a = GroundWaypoint('A', 0, 0, 0)
        self.b = GroundWaypoint('B', 1000, 0, 0)
        self.c = GroundWaypoint('C', 1000, 2000, 0)
        self.graph = NavigationGraph()

        for wp in (self.a, self.b, self.c):
            self.graph.add_waypoint(wp)

        self.graph.add_edge(GroundEdge(self.a, self.b, 0.1, 'onroad', 20.0))
        self.graph.add_edge(GroundEdge(self.b, self.c, 0.3, 'onroad', 20.0))

    def test_find_canonical_route(self):
        route = self.graph.find_canonical_route(self.a, self.c, name='march')
        self.assertIsInstance(route, Route)
        self.assertEqual(route.route_type, 'ground')
        self.assertEqual(route.name, 'march')
        self.assertEqual(len(route.edges), 2)
        self.assertAlmostEqual(float(route.length()), 3000.0, places=6)

    def test_speeds_and_danger_from_the_graph(self):
        route = self.graph.find_canonical_route(self.a, self.c)
        self.assertAlmostEqual(float(route.travelTime()), 150.0, places=6)
        self.assertAlmostEqual(route.max_danger_level(), 0.3)

    def test_speed_override(self):
        route = self.graph.find_canonical_route(self.a, self.c, speed=10.0)
        self.assertAlmostEqual(float(route.travelTime()), 300.0, places=6)

    def test_mixed_path_types_give_mixed_route_type(self):
        d = GroundWaypoint('D', 1000, 4000, 0)
        self.graph.add_waypoint(d)
        self.graph.add_edge(GroundEdge(self.c, d, 0.2, 'water', 15.0))
        route = self.graph.find_canonical_route(self.a, d)
        self.assertEqual(route.route_type, 'mixed')

    def test_no_path_returns_none(self):
        isolated = GroundWaypoint('X', 9999, 9999, 0)
        self.graph.add_waypoint(isolated)
        self.assertIsNone(self.graph.find_canonical_route(self.a, isolated))

    def test_short_path_returns_none(self):
        self.assertIsNone(Route_Adapter.ground_path_to_route(self.graph, [self.a]))

    def test_missing_edge_returns_none(self):
        """Percorso non coerente col grafo: si degrada a None, non si solleva."""
        self.assertIsNone(Route_Adapter.ground_path_to_route(self.graph, [self.a, self.c]))

    def test_bad_route_type_raises(self):
        with self.assertRaises(ValueError):
            Route_Adapter.ground_path_to_route(self.graph, [self.a, self.b], route_type='nonesiste')


if __name__ == '__main__':
    unittest.main()
