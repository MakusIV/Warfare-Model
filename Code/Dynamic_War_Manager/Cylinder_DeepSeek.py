

#Deepseek

from sympy import Point, Line, Point3D, Segment3D, Line3D, Plane, symbols, sqrt
from sympy.geometry import Circle
from typing import Tuple, Optional




# innerPoint: Claude, ChatGPT (utilizza math), DeepSeek, Manus kverifica velocità esecuzine
# getTangentPoints: Claude, ChatGPT (utilizza math), Deepseek, Manus ha toppato, verifica velocità esecuzine
# getTangents: Claude, ChatGPT (utilizza math), verifica velocità esecuzine
# getIntersection: ChatGPT, DeepSeek, Claude non considera le superfici superiore ed inferiore, verifica velocità esecuzine
# getExtendedPoints: ChatGPT, DeepSeek non lo implementa, Claude non considera le superfici superiore ed inferiore, verifica velocità esecuzine




class CylinderDeepSeek:

    DEBUG = True
    
    def __init__(self, center: Point3D, radius: float, height: float):
        self.center = center
        self.radius = radius
        self.height = height

    def innerPoint(self, point: Point3D) -> bool:
        # Verifica se il punto è all'interno del cilindro
        dx = point.x - self.center.x
        dy = point.y - self.center.y
        dz = point.z - self.center.z
        in_radius = (dx**2 + dy**2) <= self.radius**2
        in_height = (self.center.z - self.height/2 <= point.z <= self.center.z + self.height/2)
        return in_radius and in_height

    def getTangentPoints(self, point: Point3D) -> Tuple[Point3D, Point3D]:
        # Calcola i punti tangenti nel piano xy e li estende a 3D
        circle_2d = Circle(Point(self.center.x, self.center.y), self.radius)
        point_2d = Point(point.x, point.y)
        tangent_lines = circle_2d.tangent_lines(point_2d)
        tangent_points = []
        for line in tangent_lines:
            for p in line.points:
                if p != point_2d:
                    tangent_point_3d = Point3D(p.x, p.y, self.center.z)
                    tangent_points.append(tangent_point_3d)
                    break
        return (tangent_points[0], tangent_points[1])

    def getTangents(self, point: Point3D) -> Tuple[Line3D, Line3D]:
        # Ottiene le linee tangenti dai punti calcolati
        t1, t2 = self.getTangentPoints(point)
        return (Line3D(point, t1), Line3D(point, t2))

    def getIntersection(self, edge: Segment3D) -> Tuple[bool, Optional[Segment3D]]:
        intersections = []
        line = Line3D(edge.points[0], edge.points[1])
        cx, cy, cz = self.center.x, self.center.y, self.center.z
        h = self.height
        t = symbols('t')

        # Intersezione superficie laterale
        a = (line.direction.x)**2 + (line.direction.y)**2
        b = 2 * (line.p1.x - cx)*line.direction.x + 2 * (line.p1.y - cy)*line.direction.y
        c = (line.p1.x - cx)**2 + (line.p1.y - cy)**2 - self.radius**2
        discriminant = b**2 - 4*a*c

        if discriminant >= 0:
            sqrt_disc = sqrt(discriminant)
            t1 = (-b + sqrt_disc)/(2*a)
            t2 = (-b - sqrt_disc)/(2*a)
            
            for ti in [t1, t2]:
                try:
                    ti_num = ti.evalf()
                    if not ti_num.is_real or ti_num < 0 or ti_num > 1:
                        continue
                    
                    p = line.arbitrary_point(t).subs(t, ti_num)
                    p_eval = Point3D(p.x.evalf(), p.y.evalf(), p.z.evalf())
                    
                    if (cz - h/2 <= p_eval.z <= cz + h/2):
                        intersections.append(p_eval)
                except:
                    continue

        # Intersezione piani superiore/inferiore
        for z_val in [cz + h/2, cz - h/2]:
            try:
                plane = Plane(Point3D(0,0,z_val), normal_vector=(0,0,1))
                p = line.intersection(plane)[0]
                p_eval = Point3D(p.x.evalf(), p.y.evalf(), p.z.evalf())
                
                if ((p_eval.x - cx)**2 + (p_eval.y - cy)**2 <= self.radius**2):
                    # Calcolo parametro t alternativo
                    t_val = self._calculate_parameter(edge, p_eval)
                    if 0 <= t_val <= 1:
                        intersections.append(p_eval)
            except (IndexError, TypeError):
                continue

        # Elimina duplicati e ordina
        valid = []
        seen = set()
        for p in intersections:
            coords = (round(p.x, 6), round(p.y, 6), round(p.z, 6))
            if coords not in seen:
                seen.add(coords)
                valid.append(p)
        
        # Ordina in base alla distanza dal primo punto del segmento
        valid.sort(key=lambda p: p.distance(edge.p1))

        if len(valid) >= 2:
            return True, Segment3D(valid[0], valid[-1])
        elif len(valid) == 1:
            inside_points = [p for p in edge.points if self.innerPoint(p)]
            if inside_points:
                return False, Segment3D(valid[0], inside_points[0])
            return False, None
        else:
            return False, None

    def _calculate_parameter(self, edge: Segment3D, point: Point3D) -> float:
        """Calcola il parametro t per un punto sul segmento"""
        vec = edge.p2 - edge.p1
        if vec.x != 0:
            return (point.x - edge.p1.x) / vec.x
        elif vec.y != 0:
            return (point.y - edge.p1.y) / vec.y
        elif vec.z != 0:
            return (point.z - edge.p1.z) / vec.z
        return 0
        
    def getExtendedPoints(self, edge: Segment3D, tolleranza: float = 1e-6) -> Tuple[Optional[Point3D], Optional[Point3D]]:
        # Verifica se gli estremi sono interni
        if self.innerPoint(edge.p1) or self.innerPoint(edge.p2):
            return (None, None)
        
        # Ottieni l'intersezione con il cilindro
        intersezione, segmento = self.getIntersection(edge)
        if not intersezione or segmento is None:
            return (None, None)
        
        p1, p2 = segmento.points
        distanza = p1.distance(p2)
        
        # Caso distanza minima
        if distanza < tolleranza:
            medio = Point3D((p1.x + p2.x)/2, (p1.y + p2.y)/2, (p1.z + p2.z)/2)
            return (medio, medio)
        
        # Proiezione 2D per il calcolo delle tangenti
        centro_2d = Point(self.center.x, self.center.y)
        cerchio = Circle(centro_2d, self.radius)
        
        # Funzione per classificare le tangenti
        def classifica_tangenti(punto_esterno: Point, tangenti: list) -> Tuple[Line, Line]:
            direzione_bordo = edge.p2 - edge.p1
            tangenti_classificati = []
            
            for tangente in tangenti:
                # Trova il punto di tangenza
                pt = [p for p in tangente.points if p != punto_esterno][0]
                vettore_tangente = pt - punto_esterno
                # Prodotto vettoriale per determinare la direzione
                cross = direzione_bordo.x * vettore_tangente.y - direzione_bordo.y * vettore_tangente.x
                tangenti_classificati.append((cross, tangente))
            
            # Ordina per prodotto vettoriale
            tangenti_classificati.sort(key=lambda x: x[0])
            return (tangenti_classificati[0][1], tangenti_classificati[1][1])

        # Ottieni e classifica le tangenti per entrambi gli estremi
        try:
            tangenti_p1 = cerchio.tangent_lines(Point(edge.p1.x, edge.p1.y))
            sinistra_p1, destra_p1 = classifica_tangenti(Point(edge.p1.x, edge.p1.y), tangenti_p1)
            
            tangenti_p2 = cerchio.tangent_lines(Point(edge.p2.x, edge.p2.y))
            sinistra_p2, destra_p2 = classifica_tangenti(Point(edge.p2.x, edge.p2.y), tangenti_p2)
        except Exception("GeometryError"):
            return (None, None)

        # Calcola le intersezioni 3D
        def intersezione_3d(line1: Line3D, line2: Line3D) -> Optional[Point3D]:
            try:
                punti = line1.intersection(line2)
                if len(punti) > 0 and isinstance(punti[0], Point3D):
                    return punti[0]
            except Exception:
                pass
            return None

        # Costruisci le linee 3D dalle tangenti 2D
        def linee_da_tangente_2d(tangente_2d: Line, punto_origine: Point3D) -> Line3D:
            punti_3d = [Point3D(p.x, p.y, self.center.z) for p in tangente_2d.points]
            return Line3D(punto_origine, [p for p in punti_3d if p != punto_origine][0])

        # Linee tangenti sinistre
        l_sx_p1 = linee_da_tangente_2d(sinistra_p1, edge.p1)
        l_sx_p2 = linee_da_tangente_2d(sinistra_p2, edge.p2)
        
        # Linee tangenti destre
        l_dx_p1 = linee_da_tangente_2d(destra_p1, edge.p1)
        l_dx_p2 = linee_da_tangente_2d(destra_p2, edge.p2)

        # Trova le intersezioni
        punto_sx = intersezione_3d(l_sx_p1, l_sx_p2)
        punto_dx = intersezione_3d(l_dx_p1, l_dx_p2)

        return (punto_sx, punto_dx)