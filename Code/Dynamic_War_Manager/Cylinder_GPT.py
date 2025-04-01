#ChatGPT
from sympy import Point3D, Line3D, Segment3D
import math


#Manus
#from sympy import Point2D, Line2D, Point3D, Line3D, Segment3D, sqrt, solve, symbols, Eq, Matrix
#from sympy.geometry import Circle, Point, Line
#import numpy as np

# Claude
#from sympy import Point3D, Line3D, Segment3D, Plane, Circle, Ray3D
#from sympy.geometry import intersection
#import math
#import numpy as np

#Deepseek
#from sympy import Point3D, Segment3D, Line3D, Circle, Point, solve, Eq, sqrt, symbols, simplify, geometry
#from sympy.abc import t
#from typing import Tuple, Optional



# innerPoint: Claude, ChatGPT (utilizza math), DeepSeek, Manus kverifica velocità esecuzine
# getTangentPoints: Claude, ChatGPT (utilizza math), Deepseek, Manus ha toppato, verifica velocità esecuzine
# getTangents: Claude, ChatGPT (utilizza math), verifica velocità esecuzine
# getIntersection: ChatGPT, DeepSeek, Claude non considera le superfici superiore ed inferiore, verifica velocità esecuzine
# getExtendedPoints: ChatGPT, DeepSeek non lo implementa, Claude non considera le superfici superiore ed inferiore, verifica velocità esecuzine




class CylinderCGPT:
    def __init__(self, center: Point3D, radius: float, height: float):
        self.center = center
        self.radius = radius
        self.height = height
        # Con center posizionato sulla base, il cilindro si estende da center.z a center.z + height.

    def innerPoint(self, point: Point3D) -> bool:
        """
        Verifica se il punto è interno al cilindro.
        Il punto è interno se:
         - La sua proiezione sul piano xy è dentro il cerchio di raggio radius centrato in (center.x, center.y)
         - La coordinata z è compresa tra center.z e center.z + height.
        """
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        px, py, pz = point.x, point.y, point.z
        in_circle = (px - cx)**2 + (py - cy)**2 < self.radius**2
        in_z = (pz >= cz) and (pz <= cz + self.height)
        return in_circle and in_z

    def getTangentPoints(self, point: Point3D):
        """
        Calcola i due punti di tangenza sul cerchio (in pianta) del cilindro,
        relativi alle due rette tangenti che partono dal punto dato.
        
        Il problema viene risolto in piano xy mantenendo la coordinata z del punto.
        Se il punto è interno al cerchio (in pianta) viene sollevata un'eccezione.
        """
        cx, cy = self.center.x, self.center.y
        px, py = point.x, point.y
        d = math.hypot(px - cx, py - cy)
        if d < self.radius:
            raise ValueError("Il punto è interno al cerchio, non esistono tangenti")
        # Calcola l'angolo del vettore (center -> point)
        angle = math.atan2(py - cy, px - cx)
        # Angolo tra il raggio e la retta che congiunge center al punto di tangenza
        theta = math.acos(self.radius/d)
        angle1 = angle + theta
        angle2 = angle - theta
        # I punti di tangenza (si mantiene la coordinata z del punto dato)
        t1 = Point3D(cx + self.radius * math.cos(angle1), cy + self.radius * math.sin(angle1), point.z)
        t2 = Point3D(cx + self.radius * math.cos(angle2), cy + self.radius * math.sin(angle2), point.z)
        return t1, t2

    def getTangents(self, point: Point3D):
        """
        Restituisce le due rette (Line3D) tangenti al cilindro che partono dal punto dato.
        """
        t1, t2 = self.getTangentPoints(point)
        return Line3D(point, t1), Line3D(point, t2)

    def getIntersection(self, edge: Segment3D):
        """
        Calcola l'intersezione del segmento (edge) con il cilindro.
        
        Il calcolo viene effettuato considerando:
         - La superficie laterale: (x - center.x)^2 + (y - center.y)^2 = radius^2,
           con il vincolo che la coordinata z sia compresa tra center.z e center.z + height.
         - I tappi superiore (z = center.z + height) e inferiore (z = center.z).
        
        Restituisce:
         - Se edge interseca il cilindro in due punti: (True, Segment3D(p_int1, p_int2)).
         - Se interseca in un solo punto (presumibilmente perché uno degli estremi è interno),
           restituisce (False, Segment3D(p_int, p_interno)).
         - Se non vi è intersezione, restituisce (False, None).
        """
        A = edge.p1
        B = edge.p2
        intersections = []
        
        ax, ay, az = A.x, A.y, A.z
        bx, by, bz = B.x, B.y, B.z
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        dx = bx - ax
        dy = by - ay
        
        # Intersezione con la superficie laterale (in pianta):
        # (ax + t*dx - cx)^2 + (ay + t*dy - cy)^2 = radius^2
        a_coeff = dx**2 + dy**2
        b_coeff = 2*((ax - cx)*dx + (ay - cy)*dy)
        c_coeff = (ax - cx)**2 + (ay - cy)**2 - self.radius**2
        discr = b_coeff**2 - 4*a_coeff*c_coeff
        if a_coeff != 0 and discr >= 0:
            sqrt_discr = math.sqrt(discr)
            for t in [(-b_coeff + sqrt_discr) / (2*a_coeff), (-b_coeff - sqrt_discr) / (2*a_coeff)]:
                if 0 <= t <= 1:
                    z_val = az + t * (bz - az)
                    # Verifica che la z sia compresa nei limiti del cilindro
                    if cz <= z_val <= cz + self.height:
                        pt = Point3D(ax + t*dx, ay + t*dy, z_val)
                        intersections.append((t, pt))
                        
        # Intersezione con il tappo superiore: z = cz + height
        if bz != az:
            t_top = (cz + self.height - az) / (bz - az)
            if 0 <= t_top <= 1:
                x_candidate = ax + t_top * dx
                y_candidate = ay + t_top * dy
                if (x_candidate - cx)**2 + (y_candidate - cy)**2 <= self.radius**2:
                    pt = Point3D(x_candidate, y_candidate, cz + self.height)
                    intersections.append((t_top, pt))
                    
        # Intersezione con il tappo inferiore: z = cz
        if bz != az:
            t_bot = (cz - az) / (bz - az)
            if 0 <= t_bot <= 1:
                x_candidate = ax + t_bot * dx
                y_candidate = ay + t_bot * dy
                if (x_candidate - cx)**2 + (y_candidate - cy)**2 <= self.radius**2:
                    pt = Point3D(x_candidate, y_candidate, cz)
                    intersections.append((t_bot, pt))
                    
        # Rimozione di duplicati, basata sul parametro t
        intersections = list({round(t, 6): (t, pt) for t, pt in intersections}.values())
        intersections.sort(key=lambda tup: tup[0])
        
        if len(intersections) == 0:
            return False, None
        elif len(intersections) == 2:
            return True, Segment3D(intersections[0][1], intersections[1][1])
        elif len(intersections) == 1:
            t_int, pt_int = intersections[0]
            if self.innerPoint(A):
                return False, Segment3D(A, pt_int)
            elif self.innerPoint(B):
                return False, Segment3D(B, pt_int)
            else:
                return False, Segment3D(pt_int, pt_int)
        else:
            # In caso di più intersezioni (situazione degenerata), si prendono i punti con t minimo e massimo.
            pt1 = intersections[0][1]
            pt2 = intersections[-1][1]
            return True, Segment3D(pt1, pt2)

    def getExtendedPoints(self, edge: Segment3D, tolerance=1e-6):
        """
        Data un segmento (edge) che interseca il cilindro, calcola i punti d'intersezione 
        delle tangenti ai due estremi del segmento.
        
        Procedura:
         1. Se uno degli estremi di edge è interno al cilindro (con innerPoint), restituisce (None, None).
         2. Si calcola l'intersezione del segmento con il cilindro (usando getIntersection).
         3. Per ciascuno degli estremi di edge si calcolano le due tangenti, ottenendo i corrispondenti
            punti di tangenza.
         4. Si accoppiano i due insiemi di tangenti per ottenere una coppia "a sinistra" e una "a destra"
            rispetto alla direzione del segmento. Per fare ciò si calcola la normale (in pianta) ottenuta
            ruotando di 90° il vettore che collega gli estremi del segmento.
         5. Si calcola l'intersezione delle rette tangenti di ciascuna coppia.
         6. Se la distanza fra i due punti ottenuti è inferiore a tolerance, si restituisce il punto medio;
            altrimenti, i due punti distinti.
        """
        # Se uno degli estremi è interno, non si procede
        if self.innerPoint(edge.p1) or self.innerPoint(edge.p2):
            return None, None
        
        flag, seg_int = self.getIntersection(edge)
        if seg_int is None:
            return None, None
        
        # Calcolo dei punti di tangenza per ciascun estremo
        t1_a, t1_b = self.getTangentPoints(edge.p1)
        t2_a, t2_b = self.getTangentPoints(edge.p2)
        
        # Calcola la direzione del segmento (in pianta)
        dx = edge.p2.x - edge.p1.x
        dy = edge.p2.y - edge.p1.y
        # Normale a sinistra (rotazione di 90° in senso antiorario)
        n = Point3D(-dy, dx, 0)
        
        def sign_relative(ep: Point3D, tp: Point3D):
            # Restituisce il segno del prodotto scalare (in pianta) tra il vettore (ep -> tp) e n.
            vec = (tp.x - ep.x, tp.y - ep.y)
            dot = vec[0]*n.x + vec[1]*n.y
            return math.copysign(1, dot) if dot != 0 else 0
        
        s1a = sign_relative(edge.p1, t1_a)
        s1b = sign_relative(edge.p1, t1_b)
        s2a = sign_relative(edge.p2, t2_a)
        s2b = sign_relative(edge.p2, t2_b)
        
        left_pair = None
        right_pair = None
        # Accoppia le tangenti in base al segno: se i segni sono uguali, assumo che siano dallo stesso lato.
        if s1a == s2a:
            left_pair = (t1_a, t2_a)
        if s1b == s2b:
            right_pair = (t1_b, t2_b)
        # In caso di ambiguità, si prova l'accoppiamento incrociato
        if left_pair is None and right_pair is None:
            left_pair = (t1_a, t2_b)
            right_pair = (t1_b, t2_a)
        
        # Crea le linee tangenti per ciascuna coppia
        left_line1 = Line3D(edge.p1, left_pair[0])
        left_line2 = Line3D(edge.p2, left_pair[1])
        right_line1 = Line3D(edge.p1, right_pair[0])
        right_line2 = Line3D(edge.p2, right_pair[1])
        
        # Calcola le intersezioni delle coppie di tangenti
        left_intersections = left_line1.intersection(left_line2)
        right_intersections = right_line1.intersection(right_line2)
        if left_intersections and right_intersections:
            P_left = left_intersections[0]
            P_right = right_intersections[0]
            if P_left.distance(P_right) < tolerance:
                mid = Point3D((P_left.x + P_right.x)/2, (P_left.y + P_right.y)/2, (P_left.z + P_right.z)/2)
                return mid, mid
            else:
                return P_left, P_right
        return None, None

