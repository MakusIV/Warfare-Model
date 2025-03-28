import sys
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Aggiungi il percorso della directory principale del progetto
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))



import unittest
from sympy import Point3D, Segment
from sympy.geometry import Point2D

from Code.Dynamic_War_Manager.Air_Route_Manager_Solid import (
    SolidoParallelepipedo,
    #SolidoComposto,
    Mappa,
    Waypoint,
    Edge,
    Route,
    crea_percorso,
    #riconosci_composti,
)

class TestWaypoint(unittest.TestCase):
    def setUp(self):
        Waypoint.reset_counter()  # Aggiungere questo metodo

    def test_properties(self):
        wp = Waypoint(Point3D(1, 2, 3))
        self.assertEqual(wp.name, "wp_1")
        self.assertEqual(wp.point, Point3D(1, 2, 3))
        self.assertEqual(wp.point2d(), Point2D(1, 2))

class TestEdge(unittest.TestCase):
    def test_length(self):
        wp1 = Waypoint(Point3D(0, 0, 0))
        wp2 = Waypoint(Point3D(3, 4, 0))
        edge = Edge(wp1, wp2)
        self.assertAlmostEqual(edge.length, 5.0, places=2)

class TestSolidoParallelepipedo(unittest.TestCase):
    def setUp(self):
        self.solido = SolidoParallelepipedo((4, 5), 2, 0, 10)

    def test_contiene_punto(self):
        self.assertTrue(self.solido.contiene_punto(Point3D(4, 5, 5)))
        self.assertFalse(self.solido.contiene_punto(Point3D(6, 6, 5)))
"""
class TestSolidoComposto(unittest.TestCase):
    def test_contiene_punto(self):
        s1 = SolidoParallelepipedo((0, 0), 2, 0, 10)
        s2 = SolidoParallelepipedo((1, 1), 2, 0, 10)
        composto = SolidoComposto([s1, s2])
        self.assertTrue(composto.contiene_punto(Point3D(0.5, 0.5, 5)))

class TestRiconosciComposti(unittest.TestCase):
    def test_non_intersecanti(self):
        s1 = SolidoParallelepipedo((0, 0), 2, 0, 10)
        s2 = SolidoParallelepipedo((5, 5), 2, 0, 10)
        result = riconosci_composti([s1, s2])
        self.assertEqual(len(result), 2)

    def test_intersecanti(self):
        s1 = SolidoParallelepipedo((0, 0), 3, 0, 10)
        s2 = SolidoParallelepipedo((2, 2), 3, 0, 10)
        result = riconosci_composti([s1, s2])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], SolidoComposto)
"""
class BaseTestPath(unittest.TestCase):
    def base_test(self, test_case):
        mappa = Mappa()
        for params in test_case['solidi']:
            mappa.aggiungi_parallelepipedo(*params)
        
        
        #mappa.riconosci_composti()
        wp_start = Waypoint(Point3D(*test_case['start']))
        wp_end = Waypoint(Point3D(*test_case['end']))
        
        
        route = crea_percorso(
            mappa,
            wp_start,
            wp_end,
            test_case['alt_min'],
            test_case['alt_max']
        )
        
        self.assertIsNotNone(route)
        self.assertGreater(len(route.edges), 0)
        
        # Verifica collegamento start-end
        self.assertEqual(route.edges[0].wp_A.point, wp_start.point)
        self.assertEqual(route.edges[-1].wp_B.point, wp_end.point)
        
        # Verifica vincoli altitudine
        for edge in route.edges:
            self.assertTrue(test_case['alt_min'] <= edge.wp_A.point.z <= test_case['alt_max'])
            self.assertTrue(test_case['alt_min'] <= edge.wp_B.point.z <= test_case['alt_max'])
        
        # Verifica intersezioni
        solidi_validi = [
            s for s in mappa.solidi
            if not (s.contiene_punto(wp_start.point) or s.contiene_punto(wp_end.point))
        ]
        
        for edge in route.edges:
            segment = Segment(edge.wp_A.point, edge.wp_B.point)
            for solido in solidi_validi:
                interseca, _ = solido.interseca_segmento(segment)
                self.assertFalse(interseca, f"Intersezione rilevata in {edge.name}")

class TestA(BaseTestPath):
    def test_case_a(self):
        test_case = {
            'solidi': [
                ((4, 5), 2, 0, 10),
                ((2.5, 8.5), 3, 0, 10),
                ((9.5, 7.5), 3, 0, 10),
                ((7.5, 9.5), 3, 0, 10),
                ((12, 13), 2, 0, 10),
                ((11, 14), 2, 0, 10)
            ],
            'start': (3, 2, 0),
            'end': (11, 16, 0),
            'alt_min': 0,
            'alt_max': 8
        }
        self.base_test(test_case)

class TestB(BaseTestPath):
    def test_case_b(self):
        test_case = {
            'solidi': [
                ((4, 5), 2, 0, 4),
                ((2.5, 8.5), 3, 0, 5),
                ((9.5, 7.5), 3, 0, 10),
                ((7.5, 9.5), 3, 0, 22),
                ((12, 13), 2, 0, 15),
                ((11, 14), 2, 0, 16)
            ],
            'start': (3, 2, 4),
            'end': (11, 16, 6),
            'alt_min': 0,
            'alt_max': 20
        }
        self.base_test(test_case)

class TestC(BaseTestPath):
    def test_case_c(self):
        test_case = {
            'solidi': [
                ((4, 5), 2, 3, 20),
                ((2.5, 8.5), 3, 3, 10),
                ((9.5, 7.5), 3, 2, 20),
                ((7.5, 9.5), 3, 3, 16),
                ((12, 13), 2, 0, 20),
                ((11, 14), 2, 0, 18)
            ],
            'start': (3, 2, 12),
            'end': (11, 16, 3),
            'alt_min': 0,
            'alt_max': 15
        }
        self.base_test(test_case)

if __name__ == '__main__':
    unittest.main(verbosity=2)