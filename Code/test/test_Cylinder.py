import sys
import os

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
from Code.Dynamic_War_Manager.Cylinder import CylinderClaude, CylinderCGPT, CylinderDeepSeek, CylinderManus

class TestCylinderClaude(unittest.TestCase):
    def setUp(self):
        # Crea un'istanza di Cylinder per i test
        self.cylinder = CylinderClaude(Point3D(6, 9, 5), 2, 10)
        
        # Crea i segmenti per i test specifici
        self.edge_A = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
        self.edge_B = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7))
        self.edge_C = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4))
        self.edge_D = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6))
        self.edge_E = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6))
        self.edge_F = Segment3D(Point3D(4, 14, 9), Point3D(5, 6, 14))
        self.edge_G = Segment3D(Point3D(8.5, 9.5, 14), Point3D(3.5, 8.5, 14))
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
        self.assertIsNotNone(intersection_point)

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
        self.assertAlmostEqual(lp.z, 11.50, delta=1e-2)
        self.assertAlmostEqual(rp.x, 9.13, delta=1e-2)
        self.assertAlmostEqual(rp.y, 8.61, delta=1e-2)
        self.assertAlmostEqual(rp.z, 11.50, delta=1e-2)  
        #print(f"edge_F extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
    
    def test_edge_G_intersection(self):
        """Test specifico per edge_G"""
        intersects, segment = self.cylinder.getIntersection(self.edge_G)
        self.assertTrue(intersects)       
        self.assertIsNotNone(segment)
        #self.assertAlmostEqual(segment.p1.x, 4.46, delta=1e-2)
        #self.assertAlmostEqual(segment.p1.y, 10.28, delta=1e-2)
        #self.assertAlmostEqual(segment.p1.z, 11.32, delta=1e-2)
        #self.assertAlmostEqual(segment.p2.x, 4.83, delta=1e-2)
        #self.assertAlmostEqual(segment.p2.y, 7.38, delta=1e-2)
        #self.assertAlmostEqual(segment.p2.z, 13.14, delta=1e-2)  
        points = [f"({p.x.evalf():.2f}, {p.y.evalf():.2f}, {p.z.evalf():.2f})" for p in segment.points]
        print(f"edge_G intersection points: {points}")

        # Verifica il risultato di getExtendedPoints        
        lp, rp = self.cylinder.getExtendedPoints(self.edge_G) 
        #self.assertAlmostEqual(lp.x, 4.00, delta=1e-2)
        #self.assertAlmostEqual(lp.y, 8.63, delta=1e-2)
        #self.assertAlmostEqual(lp.z, 11.50, delta=1e-2)
        #self.assertAlmostEqual(rp.x, 9.13, delta=1e-2)
        #self.assertAlmostEqual(rp.y, 8.61, delta=1e-2)
        #self.assertAlmostEqual(rp.z, 11.50, delta=1e-2)  
        print(f"edge_F extended points: ( {lp.x.evalf():.2f}, {lp.y.evalf():.2f}, {lp.z.evalf():.2f} ), ( {rp.x.evalf():.2f}, {rp.y.evalf():.2f}, {rp.z.evalf():.2f}")
    

"""
# Modulo di test per la classe Cylinder
class TestCylinderCGPT(unittest.TestCase):
    def setUp(self):
        # Creazione del cilindro con center=(6,9,5), radius=2 e height=10.
        self.cylinder = CylinderCGPT
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
            self.assertAlmostEqual(dist2, self.cylinder.radius**2, places=5)
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
        self.assertIsNotNone(seg)
        self.assertFalse(flag)
        # Nel caso di intersezione singola, entrambi gli estremi del segmento restituito coincidono.
        self.assertEqual(seg.p1, seg.p2)

    def test_get_intersection_edge_E(self):
        # Per edge_E si attende almeno un'intersezione (la configurazione potrebbe portare a due o a un solo punto)
        flag, seg = self.cylinder.getIntersection(self.edge_E)
        self.assertIsNotNone(seg)

    def test_get_extended_points_edge_A(self):
        # Test per getExtendedPoints con edge_A.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_A)
        self.assertIsNotNone(P_left)
        self.assertIsNotNone(P_right)
        # Se la distanza tra i punti è maggiore della tolleranza, si attende che siano distinti.
        self.assertNotEqual(P_left, P_right)

    def test_get_extended_points_edge_C(self):
        # Per edge_C, dato che non c'è intersezione, ci si aspetta (None, None).
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_C)
        self.assertIsNone(P_left)
        self.assertIsNone(P_right)

    def test_get_extended_points_edge_D(self):
        # Test per getExtendedPoints con edge_D: anche se l'intersezione è singola,
        # ci aspettiamo di ottenere dei punti (che possono coincidere se la distanza è minore della tolleranza)
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_D)
        self.assertIsNotNone(P_left)
        self.assertIsNotNone(P_right)

    def test_get_extended_points_edge_E(self):
        # Test per getExtendedPoints con edge_E.
        P_left, P_right = self.cylinder.getExtendedPoints(self.edge_E)
        self.assertIsNotNone(P_left)
        self.assertIsNotNone(P_right)
"""


"""
#Modulo di test per la classe Cylinder
class TestCylinderManus(unittest.TestCase):
    def setUp(self):
        
        #Inizializza un cilindro con i dati specificati per tutti i test
        
        self.center = Point3D(6, 9, 5)
        self.height = 10
        self.radius = 2
        self.cylinder = CylinderManus(self.center, self.radius, self.height)
        
        # Creiamo i segmenti specificati per i test
        self.edge_A = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
        self.edge_B = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7))
        self.edge_C = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4))
        self.edge_D = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6))
        self.edge_E = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6))
    
    def test_innerPoint(self):
        
        #Test del metodo innerPoint
        
        # Punto interno al cilindro
        point_inside = Point3D(6, 9, 10)
        self.assertTrue(self.cylinder.innerPoint(point_inside), 
                        f"Il punto {point_inside} dovrebbe essere interno al cilindro")
        
        # Punto esterno al cilindro (fuori dal raggio)
        point_outside_radius = Point3D(9, 9, 10)
        self.assertFalse(self.cylinder.innerPoint(point_outside_radius), 
                         f"Il punto {point_outside_radius} dovrebbe essere esterno al cilindro (raggio)")
        
        # Punto esterno al cilindro (fuori dall'altezza)
        point_outside_height = Point3D(6, 9, 16)
        self.assertFalse(self.cylinder.innerPoint(point_outside_height), 
                         f"Il punto {point_outside_height} dovrebbe essere esterno al cilindro (altezza)")
        
        # Punto esterno al cilindro (sotto la base)
        point_below_base = Point3D(6, 9, 4)
        self.assertFalse(self.cylinder.innerPoint(point_below_base), 
                         f"Il punto {point_below_base} dovrebbe essere esterno al cilindro (sotto la base)")
    
    def test_getTangentPoints(self):
        
        #Test del metodo getTangentPoints
        
        # Punto esterno al cilindro
        point_outside = Point3D(10, 9, 10)
        tangent_point1, tangent_point2 = self.cylinder.getTangentPoints(point_outside)
        
        # Verifichiamo che i punti siano sulla superficie del cilindro
        # La distanza dal centro deve essere uguale al raggio
        distance1 = float(sqrt((tangent_point1.x - self.cylinder.base_center.x)**2 + 
                              (tangent_point1.y - self.cylinder.base_center.y)**2))
        distance2 = float(sqrt((tangent_point2.x - self.cylinder.base_center.x)**2 + 
                              (tangent_point2.y - self.cylinder.base_center.y)**2))
        
        self.assertAlmostEqual(distance1, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza del punto di tangenza 1 dal centro dovrebbe essere {self.cylinder.radius}")
        self.assertAlmostEqual(distance2, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza del punto di tangenza 2 dal centro dovrebbe essere {self.cylinder.radius}")
        
        # Verifichiamo che i punti siano all'interno dell'altezza del cilindro
        self.assertTrue(self.cylinder.base_center.z <= tangent_point1.z <= self.cylinder.base_center.z + self.cylinder.height,
                       msg=f"Il punto di tangenza 1 dovrebbe essere all'interno dell'altezza del cilindro")
        self.assertTrue(self.cylinder.base_center.z <= tangent_point2.z <= self.cylinder.base_center.z + self.cylinder.height,
                       msg=f"Il punto di tangenza 2 dovrebbe essere all'interno dell'altezza del cilindro")
    
    def test_getTangents(self):
        
        #Test del metodo getTangents
        
        # Punto esterno al cilindro
        point_outside = Point3D(10, 9, 10)
        tangent_line1, tangent_line2 = self.cylinder.getTangents(point_outside)
        
        # Verifichiamo che le linee passino per il punto dato
        self.assertTrue(point_outside in tangent_line1,
                       msg=f"La linea tangente 1 dovrebbe passare per il punto {point_outside}")
        self.assertTrue(point_outside in tangent_line2,
                       msg=f"La linea tangente 2 dovrebbe passare per il punto {point_outside}")
        
        # Verifichiamo che le linee siano tangenti al cilindro
        # Calcoliamo la distanza minima tra la linea e l'asse del cilindro
        # Per una linea tangente, questa distanza deve essere uguale al raggio
        
        # Asse del cilindro
        axis = Line3D(Point3D(self.cylinder.base_center.x, self.cylinder.base_center.y, self.cylinder.base_center.z), 
                     Point3D(self.cylinder.base_center.x, self.cylinder.base_center.y, 
                            self.cylinder.base_center.z + self.cylinder.height))
        
        # Calcoliamo la distanza minima tra le linee
        distance1 = float(tangent_line1.distance(axis))
        distance2 = float(tangent_line2.distance(axis))
        
        self.assertAlmostEqual(distance1, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza della linea tangente 1 dall'asse dovrebbe essere {self.cylinder.radius}")
        self.assertAlmostEqual(distance2, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza della linea tangente 2 dall'asse dovrebbe essere {self.cylinder.radius}")
    
    def test_getIntersection_edge_A(self):
        
        #Test del metodo getIntersection con edge_A
        
        intersects, intersection_segment = self.cylinder.getIntersection(self.edge_A)
        
        self.assertTrue(intersects, 
                       msg=f"edge_A dovrebbe intersecare il cilindro")
        self.assertIsNotNone(intersection_segment, 
                            msg=f"Il segmento di intersezione non dovrebbe essere None")
        
        # Verifichiamo che i punti di intersezione siano sulla superficie del cilindro
        intersection_point1, intersection_point2 = intersection_segment.points
        
        distance1 = float(sqrt((intersection_point1.x - self.cylinder.base_center.x)**2 + 
                              (intersection_point1.y - self.cylinder.base_center.y)**2))
        distance2 = float(sqrt((intersection_point2.x - self.cylinder.base_center.x)**2 + 
                              (intersection_point2.y - self.cylinder.base_center.y)**2))
        
        self.assertAlmostEqual(distance1, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza del punto di intersezione 1 dal centro dovrebbe essere {self.cylinder.radius}")
        self.assertAlmostEqual(distance2, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza del punto di intersezione 2 dal centro dovrebbe essere {self.cylinder.radius}")
    
    def test_getIntersection_edge_B(self):
        
        #Test del metodo getIntersection con edge_B
        
        intersects, intersection_segment = self.cylinder.getIntersection(self.edge_B)
        
        self.assertTrue(intersects, 
                       msg=f"edge_B dovrebbe intersecare il cilindro")
        self.assertIsNotNone(intersection_segment, 
                            msg=f"Il segmento di intersezione non dovrebbe essere None")
        
        # Verifichiamo che i punti di intersezione siano sulla superficie del cilindro
        intersection_point1, intersection_point2 = intersection_segment.points
        
        distance1 = float(sqrt((intersection_point1.x - self.cylinder.base_center.x)**2 + 
                              (intersection_point1.y - self.cylinder.base_center.y)**2))
        distance2 = float(sqrt((intersection_point2.x - self.cylinder.base_center.x)**2 + 
                              (intersection_point2.y - self.cylinder.base_center.y)**2))
        
        self.assertAlmostEqual(distance1, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza del punto di intersezione 1 dal centro dovrebbe essere {self.cylinder.radius}")
        self.assertAlmostEqual(distance2, self.cylinder.radius, delta=1e-10,
                              msg=f"La distanza del punto di intersezione 2 dal centro dovrebbe essere {self.cylinder.radius}")
    
    def test_getIntersection_edge_C(self):
        
        #Test del metodo getIntersection con edge_C
        
        intersects, intersection_segment = self.cylinder.getIntersection(self.edge_C)
        
        self.assertFalse(intersects, 
                        msg=f"edge_C non dovrebbe intersecare il cilindro")
        self.assertIsNone(intersection_segment, 
                         msg=f"Il segmento di intersezione dovrebbe essere None")
    
    def test_getIntersection_edge_D(self):
        
        #Test del metodo getIntersection con edge_D
        
        intersects, intersection_segment = self.cylinder.getIntersection(self.edge_D)
        
        self.assertFalse(intersects, 
                        msg=f"edge_D non dovrebbe intersecare il cilindro")
        self.assertIsNone(intersection_segment, 
                         msg=f"Il segmento di intersezione dovrebbe essere None")
    
    def test_getIntersection_edge_E(self):
        
        #Test del metodo getIntersection con edge_E
        
        intersects, intersection_segment = self.cylinder.getIntersection(self.edge_E)
        
        self.assertFalse(intersects, 
                        msg=f"edge_E non dovrebbe intersecare completamente il cilindro")
        self.assertIsNotNone(intersection_segment, 
                            msg=f"Il segmento di intersezione non dovrebbe essere None")
        
        # Verifichiamo se è un punto o un segmento
        self.assertFalse(hasattr(intersection_segment, 'points'),
                        msg=f"L'intersezione dovrebbe essere un punto, non un segmento")
    
    def test_getExtendedPoints_edge_A(self):
        
        #Test del metodo getExtendedPoints con edge_A
        
        left_point, right_point = self.cylinder.getExtendedPoints(self.edge_A)
        
        self.assertIsNotNone(left_point, 
                            msg=f"Il punto esteso sinistro non dovrebbe essere None")
        self.assertIsNotNone(right_point, 
                            msg=f"Il punto esteso destro non dovrebbe essere None")
    
    def test_getExtendedPoints_edge_B(self):
        
        #Test del metodo getExtendedPoints con edge_B
        
        left_point, right_point = self.cylinder.getExtendedPoints(self.edge_B)
        
        self.assertIsNotNone(left_point, 
                            msg=f"Il punto esteso sinistro non dovrebbe essere None")
        self.assertIsNotNone(right_point, 
                            msg=f"Il punto esteso destro non dovrebbe essere None")
    
    def test_getExtendedPoints_edge_C(self):
        
        #Test del metodo getExtendedPoints con edge_C
        
        left_point, right_point = self.cylinder.getExtendedPoints(self.edge_C)
        
        self.assertIsNone(left_point, 
                         msg=f"Il punto esteso sinistro dovrebbe essere None")
        self.assertIsNone(right_point, 
                         msg=f"Il punto esteso destro dovrebbe essere None")
    
    def test_getExtendedPoints_edge_D(self):
        
        #Test del metodo getExtendedPoints con edge_D
        
        left_point, right_point = self.cylinder.getExtendedPoints(self.edge_D)
        
        self.assertIsNone(left_point, 
                         msg=f"Il punto esteso sinistro dovrebbe essere None")
        self.assertIsNone(right_point, 
                         msg=f"Il punto esteso destro dovrebbe essere None")
    
    def test_getExtendedPoints_edge_E(self):
        
        #Test del metodo getExtendedPoints con edge_E
        
        left_point, right_point = self.cylinder.getExtendedPoints(self.edge_E)
        
        self.assertIsNone(left_point, 
                         msg=f"Il punto esteso sinistro dovrebbe essere None")
        self.assertIsNone(right_point, 
                         msg=f"Il punto esteso destro dovrebbe essere None")


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

    def test_edge_A(self):
        edge = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7))
        self._verify_intersection_result(edge, 2)
        
        left, right = self.cylinder.getExtendedPoints(edge)
        self.assertIsNotNone(left)
        self.assertIsNotNone(right)
        
        # Verifica che i punti siano sulle linee tangenti
        tangents_p1 = self.cylinder.getTangents(edge.p1)
        tangents_p2 = self.cylinder.getTangents(edge.p2)
        
        self.assertTrue(
            any(tangent.contains(left) for tangent in tangents_p1 + tangents_p2)
        )
        self.assertTrue(
            any(tangent.contains(right) for tangent in tangents_p1 + tangents_p2)
        )

    def test_edge_B(self):
        edge = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7))
        self._verify_intersection_result(edge, 2)
        
        left, right = self.cylinder.getExtendedPoints(edge)
        self.assertLess(left.x, right.x if edge.p1.x < edge.p2.x else right.x)

    def test_edge_C(self):
        edge = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4))
        self._verify_intersection_result(edge, 2)
        
        left, right = self.cylinder.getExtendedPoints(edge)
        _, segment = self.cylinder.getIntersection(edge)
        distance = segment.p1.distance(segment.p2)
        
        if distance < 1e-6:
            mid_x = (segment.p1.x + segment.p2.x)/2
            mid_y = (segment.p1.y + segment.p2.y)/2
            mid_z = (segment.p1.z + segment.p2.z)/2
            self.assertAlmostEqual(left.x, mid_x, delta=1e-6)
            self.assertAlmostEqual(left.y, mid_y, delta=1e-6)
            self.assertAlmostEqual(left.z, mid_z, delta=1e-6)
            self.assertEqual(left, right)
        else:
            self.assertGreater(left.distance(right), 0)

    def test_edge_D(self):
        edge = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6))
        self._verify_intersection_result(edge, 1)
        
        left, right = self.cylinder.getExtendedPoints(edge)
        self.assertIsNone(left)
        self.assertIsNone(right)

    def test_edge_E(self):
        edge = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6))
        self._verify_intersection_result(edge, 0)
        
        left, right = self.cylinder.getExtendedPoints(edge)
        self.assertIsNone(left)
        self.assertIsNone(right)

    def test_internal_endpoints(self):
        edge = Segment3D(Point3D(6, 9, 5), Point3D(7, 9, 5))
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
    
    # Poi esegui tutti i test
    #unittest.main()