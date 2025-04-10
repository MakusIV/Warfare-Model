import sys
import os

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))







import time
import unittest
from sympy import Point2D, Point3D, Line3D, Segment3D, sqrt, Matrix
import math
import numpy as np

# Importa la classe Cylinder dal modulo implementato
# Assumo che la classe sia in un file chiamato cylinder.py
from Code.Dynamic_War_Manager.Cylinder import Cylinder

class TestCylinderClaude(unittest.TestCase):
    
    def setUp(self):
        # Crea un'istanza di Cylinder per i test
        self.cylinder = Cylinder(Point3D(6, 9, 5), 2, 10)
        
        # Crea i segmenti per i test specifici
        self.edge_A = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7)) # interseca
        self.edge_B = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7)) # interseca
        self.edge_C = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4)) # non interseca
        self.edge_D = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6)) # non interseca
        self.edge_E = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6)) # interseca solo in un punto, l'altro passa attraverso la superficie inferiore
        self.edge_F = Segment3D(Point3D(4, 14, 9), Point3D(5, 6, 14)) # interseca
        self.edge_G = Segment3D(Point3D(8, 9.1, 5), Point3D(4, 8.9, 15))  # interseca
        # self.edge_G = Segment3D(Point3D(8.5, 9.5, 14), Point3D(3.5, 8.5, 14)) : OK
        # self.edge_G = Segment3D(Point3D(9, 9.5, 6), Point3D(3.5, 8.5, 14)) : OK
        # self.edge_G = Segment3D(Point3D(8.5, 9.5, 13), Point3D(3.5, 8.5, 14)) : NO
        # devi inserire un controllo della distanza degli estremi dei segmenti in relazione all'altezza

        

        
    def test_initialization(self):
        """Verifica che il cilindro venga inizializzato correttamente"""
        self.assertEqual(self.cylinder.center, Point3D(6, 9, 5))
        self.assertEqual(self.cylinder.radius, 2)
        self.assertEqual(self.cylinder.height, 10)
        self.assertEqual(self.cylinder.bottom_center, Point3D(6, 9, 5)) # center è la base
        self.assertEqual(self.cylinder.top_center, Point3D(6, 9, 15)) # top è center.z + height
        
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
        
    def test_get_circle_at_z(self):
        """Verifica che il metodo _get_circle_at_z funzioni correttamente"""
        center, radius = self.cylinder._get_circle_at_z(7)
        self.assertEqual(center, Point3D(6, 9, 7))
        self.assertEqual(radius, 2)
        
    def test_get_tangent_points(self):
        """Verifica che il metodo getTangentPoints funzioni correttamente"""
        # Punto esterno sul piano XY
        point = Point3D(10, 9, 7)
        tan_point1, tan_point2 = self.cylinder.getTangentPoints(point)
        
        # Verifica che i punti tangenti siano alla giusta distanza dal centro
        self.assertAlmostEqual(tan_point1.distance(Point3D(6, 9, 7)), 2, delta=1e-10)
        self.assertAlmostEqual(tan_point2.distance(Point3D(6, 9, 7)), 2, delta=1e-10)
        
        # Verifica che i vettori dal punto ai punti tangenti siano perpendicolari
        # ai raggi dal centro ai punti tangenti
        v1 = Matrix(tan_point1 - point).normalized()
        v2 = Matrix(tan_point2 - point).normalized()
        r1 = Matrix(tan_point1 - Point3D(6, 9, 7)).normalized()
        r2 = Matrix(tan_point2 - Point3D(6, 9, 7)).normalized()
        
        self.assertAlmostEqual(v1.dot(r1), 0, delta=1e-10)
        self.assertAlmostEqual(v2.dot(r2), 0, delta=1e-10)
        
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
        
        self.assertAlmostEqual(dist1, 2, delta=1e-10)
        self.assertAlmostEqual(dist2, 2, delta=1e-10)
        
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
        

    def test_find_intersection_point(self):
        """Verifica che il metodo _find_intersection_point funzioni correttamente"""
        # Linee che si intersecano
        line1 = Line3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
        line2 = Line3D(Point3D(0, 1, 0), Point3D(1, 0, 1))
        
        intersection_point = self.cylinder._find_intersection_point(line1, line2)
        
        # Le linee si intersecano in (0.5, 0.5, 0.5)
        self.assertAlmostEqual(intersection_point.x, 0.5, delta=1e-6)
        self.assertAlmostEqual(intersection_point.y, 0.5, delta=1e-6)
        self.assertAlmostEqual(intersection_point.z, 0.5, delta=1e-6)
        
        # Linee parallele
        line3 = Line3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
        line4 = Line3D(Point3D(0, 1, 0), Point3D(1, 2, 1))
        
        intersection_point = self.cylinder._find_intersection_point(line3, line4)
        
        # Dovrebbe restituire un punto medio tra le due linee
        self.assertIsNone(intersection_point)

    def test_edge_A_intersection(self):
        """Test specifico per edge_A"""
        intersects, segment = self.cylinder.getIntersection(self.edge_A)
        self.assertTrue(intersects)       
        self.assertAlmostEqual(segment.p1.x, 5.92, delta=1e-2)
        self.assertAlmostEqual(segment.p1.y, 7.00, delta=1e-2)
        self.assertAlmostEqual(segment.p1.z, 7.00, delta=1e-2)
        self.assertAlmostEqual(segment.p2.x, 7.28, delta=1e-2)
        self.assertAlmostEqual(segment.p2.y, 10.53, delta=1e-2)
        self.assertAlmostEqual(segment.p2.z, 7.00, delta=1e-2)
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_A intersection points: {points}")
        
        # Verifica il risultato di getExtendedPoints        
        lp, rp = self.cylinder.getExtendedPoints(self.edge_A) 
        self.assertAlmostEqual(lp.x, 7.91, delta=1e-2)
        self.assertAlmostEqual(lp.y, 8.28, delta=1e-2)
        self.assertAlmostEqual(lp.z, 7.00, delta=1e-2)
        self.assertAlmostEqual(rp.x, 4.00, delta=1e-2)
        self.assertAlmostEqual(rp.y, 9.81, delta=1e-2)
        self.assertAlmostEqual(rp.z, 7.00, delta=1e-2)       
        #print(f"edge_A extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
        
    def test_edge_B_intersection(self):
        """Test specifico per edge_B"""
        intersects, segment = self.cylinder.getIntersection(self.edge_B)
        self.assertTrue(intersects)  
        self.assertAlmostEqual(segment.p1.x, 7.26, delta=1e-2)
        self.assertAlmostEqual(segment.p1.y, 7.44, delta=1e-2)
        self.assertAlmostEqual(segment.p1.z, 7.00, delta=1e-2)
        self.assertAlmostEqual(segment.p2.x, 7.81, delta=1e-2)
        self.assertAlmostEqual(segment.p2.y, 9.85, delta=1e-2)
        self.assertAlmostEqual(segment.p2.z, 7.00, delta=1e-2)     
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_B intersection points: {points}")
        
        # Verifica il risultato di getExtendedPoints        
        lp, rp = self.cylinder.getExtendedPoints(self.edge_B) 
        self.assertAlmostEqual(lp.x, 7.95, delta=1e-2)
        self.assertAlmostEqual(lp.y, 8.55, delta=1e-2)
        self.assertAlmostEqual(lp.z, 7.00, delta=1e-2)
        self.assertAlmostEqual(rp.x, 3.75, delta=1e-2)
        self.assertAlmostEqual(rp.y, 9.55, delta=1e-2)
        self.assertAlmostEqual(rp.z, 7.00, delta=1e-2)       
        #print(f"edge_B extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
        
    def test_edge_C_intersection(self):
        """Test specifico per edge_C"""
        intersects, segment = self.cylinder.getIntersection(self.edge_C)
        self.assertFalse(intersects)       
        self.assertIsNone(segment)
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_C intersection points: {points}")
        
        # Verifica il risultato di getExtendedPoints        
        #lp, rp = self.cylinder.getExtendedPoints(self.edge_C)        
        #print(f"edge_C extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
        
    def test_edge_D_intersection(self):
        """Test specifico per edge_D"""
        intersects, segment = self.cylinder.getIntersection(self.edge_D)
        self.assertFalse(intersects)       
        self.assertIsNone(segment)
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_D intersection points: {points}")
        
        # Verifica il risultato di getExtendedPoints        
        #lp, rp = self.cylinder.getExtendedPoints(self.edge_D)        
        #print(f"edge_E extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
        
    def test_edge_E_intersection(self):
        """Test specifico per edge_E lo buca da sotto. La funzione rileva solo l'intersezione con la superfice laterale del cilindro"""
        intersects, segment = self.cylinder.getIntersection(self.edge_E)
        self.assertFalse(intersects)       
        self.assertIsNotNone(segment)
        self.assertTrue(isinstance(segment, Point3D))
        self.assertAlmostEqual(segment.x, 4.64, delta=1e-2)
        self.assertAlmostEqual(segment.y, 10.47, delta=1e-2)
        self.assertAlmostEqual(segment.z, 5.68, delta=1e-2)

        #points = f"({segment.x.evalf():.2f}, {segment.y.evalf():.2f}, {segment.z.evalf():.2f})"
        #print(f"edge_E intersection points: {points}")
        
        # Verifica il risultato di getExtendedPoints        
        #lp, rp = self.cylinder.getExtendedPoints(self.edge_E)        
        #print(f"edge_E extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
        
    def test_edge_F_intersection(self):
        """Test specifico per edge_F"""
        intersects, segment = self.cylinder.getIntersection(self.edge_F)
        self.assertTrue(intersects)       
        self.assertIsNotNone(segment)
        self.assertAlmostEqual(segment.p1.x, 4.46, delta=1e-2)
        self.assertAlmostEqual(segment.p1.y, 10.28, delta=1e-2)
        self.assertAlmostEqual(segment.p1.z, 11.32, delta=1e-2)
        self.assertAlmostEqual(segment.p2.x, 4.83, delta=1e-2)
        self.assertAlmostEqual(segment.p2.y, 7.38, delta=1e-2)
        self.assertAlmostEqual(segment.p2.z, 13.14, delta=1e-2)  
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_F intersection points: {points}")

        # Verifica il risultato di getExtendedPoints        
        lp, rp = self.cylinder.getExtendedPoints(self.edge_F) 
        self.assertAlmostEqual(lp.x, 4.00, delta=1e-2)
        self.assertAlmostEqual(lp.y, 8.63, delta=1e-2)
        self.assertAlmostEqual(lp.z, 12.23, delta=1e-2)
        self.assertAlmostEqual(rp.x, 9.13, delta=1e-2)
        self.assertAlmostEqual(rp.y, 8.61, delta=1e-2)
        self.assertAlmostEqual(rp.z, 12.23, delta=1e-2)  
        #print(f"edge_F extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
    
    def test_edge_G_intersection(self):
        """Test specifico per edge_G"""
        intersects, segment = self.cylinder.getIntersection(self.edge_G)
        self.assertTrue(intersects)       
        self.assertIsNotNone(segment)
        self.assertAlmostEqual(segment.p1.x, 8.00, delta=1e-2)
        self.assertAlmostEqual(segment.p1.y, 9.10, delta=1e-2)
        self.assertAlmostEqual(segment.p1.z, 5.01, delta=1e-2)
        self.assertAlmostEqual(segment.p2.x, 4.00, delta=1e-2)
        self.assertAlmostEqual(segment.p2.y, 8.90, delta=1e-2)
        self.assertAlmostEqual(segment.p2.z, 14.99, delta=1e-2)  
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        #print(f"edge_G intersection points: {points}")

        # Verifica il risultato di getExtendedPoints        
        lp, rp = self.cylinder.getExtendedPoints(self.edge_G) 
        self.assertAlmostEqual(lp.x, 4.00, delta=1e-2)
        self.assertAlmostEqual(lp.y, 49.00, delta=1e-2)
        self.assertAlmostEqual(lp.z, 10.00, delta=1e-2)
        self.assertAlmostEqual(rp.x, 8.00, delta=1e-2)
        self.assertAlmostEqual(rp.y, -31.00, delta=1e-2)
        self.assertAlmostEqual(rp.z, 10.00, delta=1e-2)  
        #print(f"edge_G extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
    
# Funzione per misurare il tempo medio di esecuzione di una funzione
def measure_time(func, *args, iterations=10000, **kwargs):
    start = time.perf_counter()
    result = None
    for _ in range(iterations):
        result = func(*args, **kwargs)
    end = time.perf_counter()
    avg_time = (end - start) / iterations
    return avg_time, result

# Funzione per eseguire i test di performance sui metodi della classe Cylinder
def performance_test():
    # Inizializzazione di un cilindro e degli input di test
    cylinder = Cylinder(Point3D(6, 9, 5), 2, 10)
    # Punto per innerPoint e getTangentPoints/getTangents
    test_point_out = Point3D(10, 9, 7)  # punto esterno in pianta
    test_point_in  = Point3D(6, 9, 7)    # punto interno per innerPoint
    # Edge per getIntersection e getExtendedPoints
    edge_A = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
    edge_B = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7))
    edge_C = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4))
    edge_D = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6))
    edge_E = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6))
    edge_F = Segment3D(Point3D(4, 14, 9), Point3D(5, 6, 14)) # interseca
    edge_G = Segment3D(Point3D(8, 9.1, 5), Point3D(4, 8.9, 15))  # interseca

    iterations = 10  # Numero di iterazioni per ciascun test

    # Misurazione dei tempi di esecuzione
    t_inner = measure_time(cylinder.innerPoint, test_point_in, iterations=iterations)[0]
    t_tangent_points = measure_time(cylinder.getTangentPoints, test_point_out, iterations=iterations)[0]
    t_tangents = measure_time(cylinder.getTangents, test_point_out, iterations=iterations)[0]
    t_intersection_A = measure_time(cylinder.getIntersection, edge_A, iterations=iterations)[0]
    t_intersection_B = measure_time(cylinder.getIntersection, edge_B, iterations=iterations)[0]
    t_intersection_C = measure_time(cylinder.getIntersection, edge_C, iterations=iterations)[0]
    t_intersection_D = measure_time(cylinder.getIntersection, edge_D, iterations=iterations)[0]
    t_intersection_E = measure_time(cylinder.getIntersection, edge_E, iterations=iterations)[0]
    t_intersection_F = measure_time(cylinder.getIntersection, edge_F, iterations=iterations)[0]
    t_intersection_G = measure_time(cylinder.getIntersection, edge_G, iterations=iterations)[0]
    t_extended_A = measure_time(cylinder.getExtendedPoints, edge_A, iterations=iterations)[0]
    t_extended_D = measure_time(cylinder.getExtendedPoints, edge_D, iterations=iterations)[0]
    t_extended_E = measure_time(cylinder.getExtendedPoints, edge_E, iterations=iterations)[0]
    t_extended_F = measure_time(cylinder.getExtendedPoints, edge_F, iterations=iterations)[0]
    t_extended_G = measure_time(cylinder.getExtendedPoints, edge_G, iterations=iterations)[0]

    print("Performance dei metodi della classe Cylinder (tempo medio per chiamata in secondi):")
    print(f"  innerPoint:            {t_inner:.6e}")
    print(f"  getTangentPoints:      {t_tangent_points:.6e}")
    print(f"  getTangents:           {t_tangents:.6e}")
    print(f"  getIntersection (edge_A): {t_intersection_A:.6e}")
    print(f"  getIntersection (edge_B): {t_intersection_B:.6e}")
    print(f"  getIntersection (edge_C): {t_intersection_C:.6e}")
    print(f"  getIntersection (edge_D): {t_intersection_D:.6e}")
    print(f"  getIntersection (edge_E): {t_intersection_E:.6e}")
    print(f"  getIntersection (edge_F): {t_intersection_F:.6e}")
    print(f"  getIntersection (edge_G): {t_intersection_G:.6e}")
    print(f"  getExtendedPoints (edge_A): {t_extended_A:.6e}")
    print(f"  getExtendedPoints (edge_D): {t_extended_D:.6e}")
    print(f"  getExtendedPoints (edge_E): {t_extended_E:.6e}")
    print(f"  getExtendedPoints (edge_F): {t_extended_F:.6e}")
    print(f"  getExtendedPoints (edge_G): {t_extended_G:.6e}")


if __name__ == "__main__":
    # Esegui prima i test specifici
    suite = unittest.TestSuite()
    suite.addTest(TestCylinderClaude('test_initialization'))
    suite.addTest(TestCylinderClaude('test_inner_point'))
    suite.addTest(TestCylinderClaude('test_get_circle_at_z'))
    suite.addTest(TestCylinderClaude('test_get_tangent_points'))
    suite.addTest(TestCylinderClaude('test_get_tangents'))
    suite.addTest(TestCylinderClaude('test_get_intersection'))
    suite.addTest(TestCylinderClaude('test_get_extended_points'))
    suite.addTest(TestCylinderClaude('test_find_intersection_point'))
    suite.addTest(TestCylinderClaude('test_edge_A_intersection'))
    suite.addTest(TestCylinderClaude('test_edge_B_intersection'))
    suite.addTest(TestCylinderClaude('test_edge_C_intersection'))
    suite.addTest(TestCylinderClaude('test_edge_D_intersection'))
    suite.addTest(TestCylinderClaude('test_edge_E_intersection'))
    suite.addTest(TestCylinderClaude('test_edge_F_intersection'))
    suite.addTest(TestCylinderClaude('test_edge_G_intersection'))


    unittest.TextTestRunner().run(suite)
    
    #esegue solo i test di performance
    performance_test()