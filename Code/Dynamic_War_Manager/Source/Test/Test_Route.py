"""Tests for DataType.Route — posizione lungo la rotta in funzione del tempo.

`positionAtTime` e' la funzione posizione(t) su cui poggia il calcolo dei contatti del
motore di sessione: senza di essa non si puo' dire dove sia un asset a un dato istante,
e quindi nemmeno quando due forze contrapposte entrino nel reciproco raggio di
rilevamento o ingaggio.

Route, Edge e Waypoint si costruiscono con oggetti reali (nessun mock): sono classi
geometriche pure, senza dipendenze circolari.
"""

import unittest
from unittest.mock import MagicMock, patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route

_ROUTE_LOGGER = 'Code.Dynamic_War_Manager.Source.DataType.Route.logger'


def _wp(name: str, x: float, y: float, z: float = 0.0) -> Waypoint:
    return Waypoint(name=name, point=Point3D(x, y, z), obj_reference=None)


def _edge(wpA: Waypoint, wpB: Waypoint, speed, name: str) -> Edge:
    return Edge(wpA=wpA, wpB=wpB, path_type='air', danger_level=0.0, speed=speed, name=name)


def _l_shaped_route(speed=100.0) -> Route:
    """A(0,0,0) -> B(1000,0,0) -> C(1000,2000,0): 3000 m, 30 s a 100 m/s."""
    a, b, c = _wp('A', 0, 0), _wp('B', 1000, 0), _wp('C', 1000, 2000)

    return Route(route_type='air',
                 edges={('A', 'B'): _edge(a, b, speed, 'AB'),
                        ('B', 'C'): _edge(b, c, speed, 'BC')},
                 name='l-shaped')


class TestPositionAtTime(unittest.TestCase):
    """Interpolazione lungo la spezzata."""

    def setUp(self):
        self.route = _l_shaped_route()

    def test_route_geometry_precondition(self):
        """Le attese dei test sotto dipendono da questi due valori."""
        self.assertAlmostEqual(float(self.route.length()), 3000.0)
        self.assertAlmostEqual(float(self.route.travelTime()), 30.0)

    def test_at_zero_returns_first_waypoint(self):
        self.assertEqual(self.route.positionAtTime(0), Point3D(0, 0, 0))

    def test_midway_along_first_edge(self):
        self.assertEqual(self.route.positionAtTime(5), Point3D(500, 0, 0))

    def test_at_junction_between_edges(self):
        self.assertEqual(self.route.positionAtTime(10), Point3D(1000, 0, 0))

    def test_along_second_edge(self):
        self.assertEqual(self.route.positionAtTime(20), Point3D(1000, 1000, 0))

    def test_at_exact_end(self):
        self.assertEqual(self.route.positionAtTime(30), Point3D(1000, 2000, 0))

    def test_beyond_end_clamps_to_last_waypoint(self):
        """Oltre la durata totale l'asset e' a destinazione, non oltre."""
        self.assertEqual(self.route.positionAtTime(10_000), Point3D(1000, 2000, 0))

    def test_fractional_time(self):
        self.assertEqual(self.route.positionAtTime(2.5), Point3D(250, 0, 0))

    def test_interpolates_altitude(self):
        """La rotta e' una spezzata in 3D: anche z va interpolata.

        La salita ha anche una componente orizzontale perche' Edge costruisce una Line2D
        dalle proiezioni dei due waypoint: una salita verticale pura non e' rappresentabile
        (sympy rifiuta una Line2D fra due punti coincidenti).
        """
        a, b = _wp('A', 0, 0, 0), _wp('B', 1000, 0, 1000)
        route = Route(route_type='air', edges={('A', 'B'): _edge(a, b, 100.0, 'AB')}, name='climb')

        half_way = route.positionAtTime(float(route.travelTime()) / 2)

        self.assertAlmostEqual(float(half_way.x), 500.0)
        self.assertAlmostEqual(float(half_way.z), 500.0)

    def test_single_edge_route(self):
        a, b = _wp('A', 0, 0), _wp('B', 100, 0)
        route = Route(route_type='air', edges={('A', 'B'): _edge(a, b, 10.0, 'AB')}, name='one')

        self.assertEqual(route.positionAtTime(5), Point3D(50, 0, 0))


class TestPositionAtTimeSpeedOverride(unittest.TestCase):
    """`speed` sovrascrive la velocita' degli archi, come in travelTime/calcTravelTime."""

    def test_override_doubles_the_distance_covered(self):
        route = _l_shaped_route(speed=100.0)

        self.assertEqual(route.positionAtTime(5, speed=200.0), Point3D(1000, 0, 0))

    def test_override_makes_a_speedless_route_computable(self):
        a, b = _wp('A', 0, 0), _wp('B', 1000, 0)
        route = Route(route_type='air', edges={('A', 'B'): _edge(a, b, None, 'AB')}, name='nospeed')

        self.assertEqual(route.positionAtTime(5, speed=100.0), Point3D(500, 0, 0))


class TestPositionAtTimeGuards(unittest.TestCase):
    """Casi in cui la posizione non e' calcolabile o l'input non e' valido."""

    def setUp(self):
        self._log = patch(_ROUTE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()

    def test_undefined_speed_returns_none(self):
        """Senza velocita' il tempo di percorrenza e' infinito: restituire un punto
        qualsiasi sarebbe peggio di ammettere che la posizione non si sa."""
        a, b = _wp('A', 0, 0), _wp('B', 1000, 0)
        route = Route(route_type='air', edges={('A', 'B'): _edge(a, b, None, 'AB')}, name='nospeed')

        self.assertIsNone(route.positionAtTime(5))

    def test_undefined_speed_on_later_edge_returns_none(self):
        a, b, c = _wp('A', 0, 0), _wp('B', 1000, 0), _wp('C', 2000, 0)
        route = Route(route_type='air',
                      edges={('A', 'B'): _edge(a, b, 100.0, 'AB'),
                             ('B', 'C'): _edge(b, c, None, 'BC')},
                      name='partial')

        self.assertIsNone(route.positionAtTime(50))

    def test_empty_route_returns_none(self):
        route = Route(route_type='air', edges={}, name='empty')

        self.assertIsNone(route.positionAtTime(1))

    def test_negative_time_raises_value_error(self):
        with self.assertRaises(ValueError):
            _l_shaped_route().positionAtTime(-1)

    def test_non_numeric_time_raises_type_error(self):
        with self.assertRaises(TypeError):
            _l_shaped_route().positionAtTime('5')

    def test_bool_time_raises_type_error(self):
        """bool e' sottoclasse di int: True non e' un istante."""
        with self.assertRaises(TypeError):
            _l_shaped_route().positionAtTime(True)


class TestPositionAtTimeConsistency(unittest.TestCase):
    """Coerenza con gli altri metodi temporali della rotta."""

    def test_position_at_total_travel_time_is_the_last_waypoint(self):
        route = _l_shaped_route()
        total = float(route.travelTime())

        self.assertEqual(route.positionAtTime(total), Point3D(1000, 2000, 0))

    def test_position_at_travel_time_to_edge_is_that_edge_start(self):
        """travelTimeToEdge da' l'istante in cui inizia un arco: a quell'istante la
        posizione deve essere il suo primo waypoint."""
        route = _l_shaped_route()
        second_edge = list(route.edges.values())[1]
        t_start = float(route.travelTimeToEdge(second_edge))

        self.assertEqual(route.positionAtTime(t_start), second_edge.wpA.point)


if __name__ == '__main__':
    unittest.main()
