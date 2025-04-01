import sys
import os
import time

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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
from Code.Dynamic_War_Manager.Cylinder_GPT import CylinderCGPT


# Modulo di test per la classe Cylinder
class TestCylinderCGPT(unittest.TestCase):
    def setUp(self):
        # Creazione del cilindro con center=(6,9,5), radius=2 e height=10.
        self.cylinder = CylinderCGPT(center= Point3D(6,9,5), radius = 2.0, height = 10.0)
        self.edge_A = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
        self.edge_B = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7))
        self.edge_C = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4))
        self.edge_D = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6))
        self.edge_E = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6))
        self.edge_F = Segment3D(Point3D(4, 14, 9), Point3D(5, 6, 14)) # interseca
        self.edge_G = Segment3D(Point3D(8, 9.1, 5), Point3D(4, 8.9, 15))  # interseca

    def test_inner_point(self):
        # Test per innerPoint: punto interno, punto sul bordo (non interno) e punto esterno per la coordinata z.
        p_inside = Point3D(6,9,6)
        self.assertTrue(self.cylinder.innerPoint(p_inside))
        p_border = Point3D(8,9,6)  # distanza esattamente uguale al raggio (non interno)
        self.assertFalse(self.cylinder.innerPoint(p_border))
        p_above = Point3D(6,9,16)
        self.assertFalse(self.cylinder.innerPoint(p_above))

    def test_get_tangent_points(self):
        # Test per getTangentPoints: il punto scelto è esterno al cerchio in pianta.
        test_point = Point3D(10,9,7)
        t1, t2 = self.cylinder.getTangentPoints(test_point)
        # I punti di tangenza devono appartenere al cerchio (verifica della distanza dal centro in xy)
        for t in (t1, t2):
            dist2 = (t.x - self.cylinder.center.x)**2 + (t.y - self.cylinder.center.y)**2
            self.assertAlmostEqual(dist2, self.cylinder.radius**2, delta = 1e-4)
            # La coordinata z deve essere la stessa del punto test
            self.assertEqual(t.z, test_point.z)

    def test_get_tangents(self):
        # Test per getTangents: le rette devono contenere il punto dato.
        test_point = Point3D(10,9,7)
        l1, l2 = self.cylinder.getTangents(test_point)
        self.assertTrue(test_point.equals(l1.p1) or test_point.equals(l1.p2))
        self.assertTrue(test_point.equals(l2.p1) or test_point.equals(l2.p2))

    def test_get_intersection_edge_A(self):
        # Per edge_A si attende l'intersezione in due punti (flag=True)
        
        flag, seg = self.cylinder.getIntersection(self.edge_A)
        self.assertIsNotNone(seg)
        self.assertTrue(flag)
        # Controllo che i due estremi siano distinti
        self.assertNotEqual(seg.p1, seg.p2)
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in seg.points]
        #print(f"edge_A intersection points: {points}")
        

    def test_get_intersection_edge_B(self):
        # Per edge_B ci si aspetta anch'essa due intersezioni (flag=True)
        
        flag, seg = self.cylinder.getIntersection(self.edge_B)
        self.assertIsNotNone(seg)
        self.assertTrue(flag)
        self.assertNotEqual(seg.p1, seg.p2)

    def test_get_intersection_edge_C(self):
        # Per edge_C (z costante fuori dai limiti del cilindro) non ci si aspetta intersezione
        
        flag, seg = self.cylinder.getIntersection(self.edge_C)
        self.assertFalse(flag)
        self.assertIsNone(seg)

    def test_get_intersection_edge_D(self):
        # Per edge_D, il segmento interseca il cilindro in un solo punto.
        
        flag, seg = self.cylinder.getIntersection(self.edge_D)
        self.assertIsNone(seg)
        self.assertFalse(flag)
        # Nel caso di intersezione singola, entrambi gli estremi del segmento restituito coincidono.
        

    def test_get_intersection_edge_E(self):
        # Per edge_E si attende almeno un'intersezione (la configurazione potrebbe portare a due o a un solo punto)
        
        flag, seg = self.cylinder.getIntersection(self.edge_E)
        self.assertTrue(flag)
        self.assertIsNotNone(seg)

    def test_get_extended_points_edge_A(self):
        # Test per getExtendedPoints con edge_A.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_A)
        self.assertIsNotNone(P_left)
        self.assertIsNotNone(P_right)
        # Se la distanza tra i punti è maggiore della tolleranza, si attende che siano distinti.
        self.assertNotEqual(P_left, P_right)
        #print(f"edge_A extended points: ( {P_left.x.evalf():.2f}, {P_left.y.evalf():.2f}, {P_left.z.evalf():.2f} ), ( {P_right.x.evalf():.2f}, {P_right.y.evalf():.2f}, {P_right.z.evalf():.2f}")

    def test_get_extended_points_edge_C(self):
        # Per edge_C, dato che non c'è intersezione, ci si aspetta (None, None).
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_C)
        self.assertIsNone(P_left)
        self.assertIsNone(P_right)

    def test_get_extended_points_edge_D(self):
        # Test per getExtendedPoints con edge_D: anche se l'intersezione è singola,
        # ci aspettiamo di ottenere dei punti (che possono coincidere se la distanza è minore della tolleranza)
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_D)
        self.assertIsNone(P_left)
        self.assertIsNone(P_right)

    def test_get_extended_points_edge_E(self):
        # Test per getExtendedPoints con edge_E.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_E)
        #print(f"Edge E: P_left = {P_left}, P_right = {P_right}")
        # intersezione nella superfice inferiore e poi sulla superfice laterale-> non può generare extended points (verifica funzione)
        self.assertIsNone(P_left)
        self.assertIsNone(P_right)

    def test_get_extended_points_edge_E(self):
        # Test per getExtendedPoints con edge_E.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_E)
        #print(f"Edge E: P_left = {P_left}, P_right = {P_right}")
        # intersezione nella superfice inferiore e poi sulla superfice laterale-> non può generare extended points (verifica funzione)
        self.assertIsNone(P_left)
        self.assertIsNone(P_right)

    def test_get_extended_points_edge_F(self):
        # Test per getExtendedPoints con edge_E.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_F)
        #print(f"Edge F: P_left = {P_left}, P_right = {P_right}")
        # intersezione nella superfice inferiore e poi sulla superfice laterale-> non può generare extended points (verifica funzione)
        self.assertIsNotNone(P_left)
        self.assertIsNotNone(P_right)

    def test_get_extended_points_edge_G(self):
        # Test per getExtendedPoints con edge_E.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_G)
        print(f"Edge G: P_left = {P_left}, P_right = {P_right}")        
        self.assertIsNotNone(P_left)
        self.assertIsNotNone(P_right)

    def test_get_intersection_edge_F(self):
        # Per edge_A si attende l'intersezione in due punti (flag=True)
        
        flag, seg = self.cylinder.getIntersection(self.edge_F)
        self.assertIsNotNone(seg)
        self.assertTrue(flag)
        # Controllo che i due estremi siano distinti
        self.assertNotEqual(seg.p1, seg.p2)
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in seg.points]
        #print(f"edge_A intersection points: {points}")

    def test_get_intersection_edge_G(self):
        # Per edge_A si attende l'intersezione in due punti (flag=True)
        
        flag, seg = self.cylinder.getIntersection(self.edge_G)
        self.assertIsNotNone(seg)
        self.assertTrue(flag)
        # Controllo che i due estremi siano distinti
        self.assertNotEqual(seg.p1, seg.p2)
        #points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in seg.points]
        #print(f"edge_A intersection points: {points}")

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
    cylinder = CylinderCGPT(Point3D(6, 9, 5), 2, 10)
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

    # esegui tutti i test
    unittest.main()

    #esegue solo i test di performance
    #performance_test()

"""
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

    #suite.addTest(TestCylinderCGPT('test_all_edges'))
    #suite.addTest(TestCylinderDeepSeek('test_all_edges'))
    #suite.addTest(TestCylinderManus('test_all_edges'))

    unittest.TextTestRunner().run(suite)
    """
