"""Tests for DataType.Edge.intersectPoint.

Nessuna copertura esisteva per questo metodo prima di questo fix: il ramo Line2D usava
`self._line` (la retta 3D dell'edge) invece di `self._line2d` (la sua proiezione 2D),
producendo un falso negativo silenzioso — nessuna eccezione, solo un'intersezione vuota —
ogni volta che l'edge non era esattamente a quota zero (v. wiki/decisions per il dettaglio).

Edge/Waypoint si costruiscono con oggetti reali (nessun mock): classi geometriche pure.
"""

import unittest

from sympy import Point3D, Point2D, Line2D, Line3D

from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge


def _wp(name: str, x: float, y: float, z: float = 0.0) -> Waypoint:
    return Waypoint(name=name, point=Point3D(x, y, z), obj_reference=None)


def _edge(wpA: Waypoint, wpB: Waypoint, path_type: str = 'air') -> Edge:
    return Edge(wpA=wpA, wpB=wpB, path_type=path_type, danger_level=0.0, speed=100.0, name='E')


class TestIntersectPointLine2D(unittest.TestCase):
    """Ramo `elif isinstance(line, Line2D)` — deve usare la proiezione 2D dell'edge, non la
    sua retta 3D."""

    def test_finds_intersection_for_edge_at_nonzero_altitude(self):
        """Un edge in quota (z=1000) deve intersecare una Line2D che attraversa la sua
        proiezione — prima del fix, l'intersezione 3D-vs-2D-a-z=0 risultava vuota."""
        edge = _edge(_wp('A', 0, 0, 1000), _wp('B', 10, 0, 1000))
        crossing = Line2D(Point2D(5, -5), Point2D(5, 5))

        result = edge.intersectPoint(crossing)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(float(result.x), 5.0)
        self.assertAlmostEqual(float(result.y), 0.0)

    def test_no_intersection_returns_none(self):
        edge = _edge(_wp('A', 0, 0, 1000), _wp('B', 10, 0, 1000))
        parallel = Line2D(Point2D(0, 5), Point2D(10, 5))

        self.assertIsNone(edge.intersectPoint(parallel))

    def test_degenerate_2d_projection_returns_none_not_raises(self):
        """Salita verticale pura (stessa x,y): _line2d e' None (v. _buildLine)."""
        edge = _edge(_wp('A', 0, 0, 0), _wp('B', 0, 0, 1000))
        crossing = Line2D(Point2D(-5, 0), Point2D(5, 0))

        self.assertIsNone(edge.intersectPoint(crossing))


class TestIntersectPointLine3D(unittest.TestCase):
    """Ramo `air`/Line3D — invariato dal fix, verificato per non-regressione."""

    def test_air_path_type_intersects_in_3d(self):
        edge = _edge(_wp('A', 0, 0, 1000), _wp('B', 10, 0, 1000), path_type='air')
        crossing = Line3D(Point3D(5, -5, 1000), Point3D(5, 5, 1000))

        result = edge.intersectPoint(crossing)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(float(result.x), 5.0)


if __name__ == '__main__':
    unittest.main()
