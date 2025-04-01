import sys
import os

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))



import numpy as np


import unittest
from sympy import Point3D, Segment
from sympy.geometry import Point2D


import unittest
from sympy import Point3D, Line3D, Segment3D, sqrt, Matrix
import math
import numpy as np

# Importa la classe Cylinder dal modulo implementato
# Assumo che la classe sia in un file chiamato cylinder.py
from Code.Dynamic_War_Manager.Cylinder_DeepSeek import CylinderDeepSeek



class TestCylinderDeepSeek(unittest.TestCase):
    def setUp(self):
        self.cylinder = CylinderDeepSeek(
            center=Point3D(6, 9, 5),
            radius=2,
            height=10
        )
    
    def _verify_intersection_result(self, edge, expected_intersections):
        has_intersection, segment = self.cylinder.getIntersection(edge)
        
        if expected_intersections == 0:
            self.assertFalse(has_intersection)
            self.assertIsNone(segment)
        else:
            self.assertEqual(has_intersection, expected_intersections == 2)
            if segment is not None:
                points = segment.points
                self.assertEqual(len(points), 2 if expected_intersections == 2 else 1)
                
                for p in points:
                    # Verifica appartenenza al cilindro
                    self.assertAlmostEqual(
                        (p.x - 6)**2 + (p.y - 9)**2, 
                        4, 
                        delta=1e-6
                    )
                    self.assertTrue(0 <= p.z <= 10)


    def test_inner_point(self):
        """Verifica che il metodo innerPoint funzioni correttamente"""
        # Punto interno
        self.assertTrue(self.cylinder.innerPoint(Point3D(6, 9, 10)))
        self.assertTrue(self.cylinder.innerPoint(Point3D(7, 9, 10))) # In orizzontale entro il raggio
        self.assertTrue(self.cylinder.innerPoint(Point3D(6, 10, 7))) # In orizzontale entro il raggio
        
        # Punto esterno (fuori dal raggio)
        self.assertFalse(self.cylinder.innerPoint(Point3D(9, 9, 10))) # Oltre il raggio
        self.assertFalse(self.cylinder.innerPoint(Point3D(6, 12, 10))) # Oltre il raggio
        
        # Punto esterno (fuori dall'altezza)
        self.assertFalse(self.cylinder.innerPoint(Point3D(6, 9, 4))) # Sotto la base
        self.assertFalse(self.cylinder.innerPoint(Point3D(6, 9, 16))) # Sopra il top
        

        
    def test_get_tangent_points(self):
        """Verifica che il metodo getTangentPoints funzioni correttamente"""
        # Punto esterno sul piano XY
        point = Point3D(10, 9, 7)
        tan_point1, tan_point2 = self.cylinder.getTangentPoints(point)
        
        # Verifica che i punti tangenti siano alla giusta distanza dal centro
        self.assertAlmostEqual(tan_point1.distance(Point3D(6, 9, 7)), 2, delta=1e-4)
        self.assertAlmostEqual(tan_point2.distance(Point3D(6, 9, 7)), 2, delta=1e-4)
        
        # Verifica che i vettori dal punto ai punti tangenti siano perpendicolari
        # ai raggi dal centro ai punti tangenti
        v1 = Matrix(tan_point1 - point).normalized()
        v2 = Matrix(tan_point2 - point).normalized()
        r1 = Matrix(tan_point1 - Point3D(6, 9, 7)).normalized()
        r2 = Matrix(tan_point2 - Point3D(6, 9, 7)).normalized()
        
        self.assertAlmostEqual(v1.dot(r1), 0, delta=1e-5)
        self.assertAlmostEqual(v2.dot(r2), 0, delta=1e-5)
        
        # Verifica che sollevi un'eccezione per punti interni
        with self.assertRaises(ValueError):
            self.cylinder.getTangentPoints(Point3D(6, 9, 7))
            
    def test_get_tangents(self):
        """Verifica che il metodo getTangents funzioni correttamente"""
        # Punto esterno sul piano XY
        point = Point3D(10, 9, 7)
        line1, line2 = self.cylinder.getTangents(point)
        
        # Verifica che le linee partano dal punto dato
        self.assertEqual(line1.p1, point)
        self.assertEqual(line2.p1, point)
        
        # Verifica che le linee siano tangenti al cilindro
        # La distanza dal centro della sezione alla linea deve essere uguale al raggio
        center = Point3D(6, 9, 7)
        
        # Calcola la distanza dal centro alla linea
        dist1 = line1.distance(center)
        dist2 = line2.distance(center)
        
        self.assertAlmostEqual(dist1, 2, delta=1e-4)
        self.assertAlmostEqual(dist2, 2, delta=1e-4)
        
    def test_get_intersection(self):
        """Verifica generica che il metodo getIntersection funzioni correttamente"""
        # Segmento che attraversa completamente il cilindro
        seg_through = Segment3D(Point3D(3, 9, 7), Point3D(9, 9, 7))
        intersects, segment = self.cylinder.getIntersection(seg_through)
        self.assertTrue(intersects)
        self.assertEqual(len(segment.points), 2)
        
        # Segmento che tocca il cilindro in un punto
        seg_touch = Segment3D(Point3D(8, 9, 7), Point3D(10, 9, 7))
        intersects, segment = self.cylinder.getIntersection(seg_touch)
        self.assertFalse(intersects)
        self.assertIsNotNone(segment)
        
        # Segmento che non interseca il cilindro
        seg_outside = Segment3D(Point3D(9, 9, 7), Point3D(11, 9, 7))
        intersects, segment = self.cylinder.getIntersection(seg_outside)
        self.assertFalse(intersects)
        self.assertIsNone(segment)
        
        # Segmento con un estremo dentro il cilindro
        seg_one_inside = Segment3D(Point3D(6, 9, 7), Point3D(10, 9, 7))
        intersects, segment = self.cylinder.getIntersection(seg_one_inside)
        self.assertFalse(intersects)
        self.assertIsNotNone(segment)
        
    def test_get_extended_points(self):
        """Verifica generica che il metodo getExtendedPoints funzioni correttamente"""
        # Segmento che attraversa completamente il cilindro
        seg_through = Segment3D(Point3D(3, 9, 7), Point3D(9, 9, 7))
        left_point, right_point = self.cylinder.getExtendedPoints(seg_through)
        self.assertIsNotNone(left_point)
        self.assertIsNotNone(right_point)
        
        # Segmento con un estremo dentro il cilindro
        seg_one_inside = Segment3D(Point3D(6, 9, 7), Point3D(10, 9, 7))
        left_point, right_point = self.cylinder.getExtendedPoints(seg_one_inside)
        self.assertIsNone(left_point)
        self.assertIsNone(right_point)
        
    
    """
    def test_edge_A_1(self):
        
        edge = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
        print("test_edge_A_1 - edge:", edge, " -------------------------------------------------")
        self._verify_intersection_result(edge, 2)
        
        left, right = self.cylinder.getExtendedPoints(edge)
        print(f"left: {left}, right: {right}")
        self.assertIsNotNone(left)
        self.assertIsNotNone(right)
        
        # Verifica che i punti siano sulle linee tangenti
        tangents_p1 = self.cylinder.getTangents(edge.p1)
        tangents_p2 = self.cylinder.getTangents(edge.p2)
        print(f"tangents_p1: {tangents_p1}, tangents_p2: {tangents_p2}")
        
        self.assertTrue(
            any(tangent.contains(left) for tangent in tangents_p1 + tangents_p2)
        )
        self.assertTrue(
            any(tangent.contains(right) for tangent in tangents_p1 + tangents_p2)
        )

        left, right = self.cylinder.getExtendedPoints(edge)
        print(f"extendend points: left: {left}, right: {right}")

    def test_edge_A_intersection(self):
        #Test specifico per edge_A
        edge = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
        print("test_edge_A - edge:", edge, " -------------------------------------------------")
        has_intersection, segment = self.cylinder.getIntersection(edge)
        
        points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        print(f"edge_A intersection points: {points}")
        self.assertTrue(has_intersection)
        self.assertEqual(len(segment.points), 2)
        
        # Verifica che i punti siano sul cilindro
        p1, p2 = segment.points
        print(f"edge_A intersection points: {p1}, {p2}")
        self.assertAlmostEqual((p1.x - 6)**2 + (p1.y - 9)**2, 4, delta=1e-5)
        self.assertAlmostEqual((p2.x - 6)**2 + (p2.y - 9)**2, 4, delta=1e-5)
        self.assertTrue(0 <= p1.z <= 10)
        self.assertTrue(0 <= p2.z <= 10)
        
        # Verifica che i punti siano sul segmento
        self.assertTrue(edge.contains(p1))
        self.assertTrue(edge.contains(p2))
                
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_A intersection points: {points}")
        
        # Verifica il risultato di getExtendedPoints        
        lp, rp = self.cylinder.getExtendedPoints(self.edge_A) 
        #self.assertAlmostEqual(lp.x, 7.91, delta=1e-2)
        #self.assertAlmostEqual(lp.y, 8.28, delta=1e-2)
        #self.assertAlmostEqual(lp.z, 7.00, delta=1e-2)
        #self.assertAlmostEqual(rp.x, 4.00, delta=1e-2)
        #self.assertAlmostEqual(rp.y, 9.81, delta=1e-2)
        #self.assertAlmostEqual(rp.z, 7.00, delta=1e-2)       
        #print(f"edge_A extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
        print(f"lp: {lp},  rp: {rp}")

    def test_edge_B(self):
        edge = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7))
        print("test_edge_B - edge:", edge, " -------------------------------------------------")
        self._verify_intersection_result(edge, 2)
        
        #lp, rp = self.cylinder.getExtendedPoints(edge)
        #print(f"lp: {lp},  rp: {rp}")
        #self.assertLess(left.x, right.x if edge.p1.x < edge.p2.x else right.x)

    def test_edge_C(self):
        edge = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4))
        print("test_edge_B - edge:", edge, " -------------------------------------------------")
        self._verify_intersection_result(edge, 0)
        
        

    def test_edge_D(self):
        edge = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6))
        print("test_edge_C - edge:", edge, " -------------------------------------------------")
        self._verify_intersection_result(edge, 0)
        
        

    def test_edge_E(self):
        edge = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6))
        self._verify_intersection_result(edge, 1)
        
        

    def test_internal_endpoints(self):
        edge = Segment3D(Point3D(6, 9, 5), Point3D(7, 9, 5))
        print("test_edge_E - edge:", edge, " -------------------------------------------------")
        left, right = self.cylinder.getExtendedPoints(edge)
        self.assertIsNone(left)
        self.assertIsNone(right)

    def test_parallel_tangents(self):
        edge = Segment3D(Point3D(6, 12, 5), Point3D(6, 12, 10))
        left, right = self.cylinder.getExtendedPoints(edge)
        self.assertIsNotNone(left)
        self.assertIsNotNone(right)
        self.assertTrue(left.is_collinear(right))
"""

if __name__ == "__main__":

    # esegui tutti i test
    unittest.main()


