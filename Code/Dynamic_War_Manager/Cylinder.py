

from sympy import  Point2D, Line2D, Point3D, Line3D, Segment3D, Point, Line, Plane, Circle, Ray3D, Matrix
from sympy.geometry import intersection
import math
import numpy as np


# innerPoint: Claude, ChatGPT (utilizza math), DeepSeek, Manus kverifica velocità esecuzine
# getTangentPoints: Claude, ChatGPT (utilizza math), Deepseek, Manus ha toppato, verifica velocità esecuzine
# getTangents: Claude, ChatGPT (utilizza math), verifica velocità esecuzine
# getIntersection: ChatGPT, DeepSeek, Claude non considera le superfici superiore ed inferiore, verifica velocità esecuzine
# getExtendedPoints: ChatGPT, DeepSeek non lo implementa, Claude non considera le superfici superiore ed inferiore, verifica velocità esecuzine




class Cylinder:

    def __init__(self, center: Point3D, radius: float, height: float):
        # Center si riferisce alla base del cilindro
        self.center = center
        self.radius = radius
        self.height = height
        
        # Definiamo il centro geometrico del cilindro
        self.geometric_center = Point3D(center.x, center.y, center.z + height/2)
        
        # Definiamo i piani superiore e inferiore del cilindro
        self.bottom_center = center  # La base coincide con center
        self.top_center = Point3D(center.x, center.y, center.z + height)

    def distanceFromCirconference(self, point: Point3D):
        z = point.z
        center, radius = self._get_circle_at_z(z)
        return point.distance(center) - radius

    def distanceFromCenter(self, point: Point3D):
        z = point.z
        center, _ = self._get_circle_at_z(z)
        return point.distance(center)

    def centerProximity(self, point: Point3D) -> float: # 1: external point or point on circonference, 0: point == center

        if not self.innerPoint(point):
            return 0
        
        z = point.z
        center, radius = self._get_circle_at_z(z)        
        proximity = point.distance(center) / radius


    def innerPoint(self, point: Point3D) -> bool:
        """
        Verifica se un punto è interno al cilindro
        
        Args:
            point: Point3D - Il punto da verificare
            
        Returns:
            bool - True se il punto è interno al cilindro, False altrimenti
        """
        # Verifica se il punto è entro l'altezza del cilindro
        if not (self.bottom_center.z <= point.z <= self.top_center.z):
            return False
            
        # Verifica se il punto è entro il raggio del cilindro
        # Calcola la distanza dal punto all'asse del cilindro
        dx = point.x - self.bottom_center.x
        dy = point.y - self.bottom_center.y
        distance_to_axis = math.sqrt(dx**2 + dy**2)
        
        return distance_to_axis < self.radius
    
    def _get_circle_at_z(self, z):
        """
        Restituisce un Circle che rappresenta la sezione del cilindro all'altezza z
        """
        # Proiezione del centro del cilindro sul piano z
        center = Point3D(self.bottom_center.x, self.bottom_center.y, z)
        return center, self.radius
    
    def getTangentPoints(self, point: Point3D) -> tuple:
        """
        Calcola i punti di tangenza dal punto esterno al cilindro
        
        Args:
            point: Point3D - Punto esterno al cilindro
            
        Returns:
            tuple(Point3D, Point3D) - I due punti di tangenza
        """
        # Assicuriamoci che il punto sia esterno al cilindro
        if self.innerPoint(point):
            raise ValueError("Il punto deve essere esterno al cilindro")
        
        # Proiettiamo il problema sul piano XY passante per l'altezza del punto
        # non serve in quanto non può verificarsi perchè z è esterno al oilindro e questo viene verificato prim acon innerPOint 
        z = point.z
        if z < self.bottom_center.z:
            z = self.bottom_center.z
        elif z > self.top_center.z:
            z = self.top_center.z
            
        center, radius = self._get_circle_at_z(z)
        
        # Calcola i punti di tangenza nel piano 2D
        # Vettore dal centro al punto
        dx = point.x - center.x
        dy = point.y - center.y
        dist = math.sqrt(dx**2 + dy**2)
        
        # Se il punto è esattamente sul bordo del cilindro
        if abs(dist - self.radius) < 1e-10:
            return point, point
            
        # Coordinate dei punti di tangenza nel piano XY
        # Formula per i punti di tangenza da un punto a un cerchio
        a = self.radius**2 / dist
        h = self.radius * math.sqrt(dist**2 - self.radius**2) / dist
        
        # Punto di proiezione sul vettore dal centro al punto
        px = center.x + a * dx / dist
        py = center.y + a * dy / dist
        
        # Vettore perpendicolare
        nx = -dy / dist
        ny = dx / dist
        
        # Punti di tangenza
        t1x = px + h * nx
        t1y = py + h * ny
        t2x = px - h * nx
        t2y = py - h * ny
        
        # Restituisce i punti di tangenza
        return Point3D(t1x, t1y, z), Point3D(t2x, t2y, z)
    
    def getTangents(self, point: Point3D) -> tuple:
        """
        Calcola le linee tangenti dal punto al cilindro
        
        Args:
            point: Point3D - Il punto da cui partono le tangenti
            
        Returns:
            tuple(Line3D, Line3D) - Le due linee tangenti
        """
        tan_point1, tan_point2 = self.getTangentPoints(point)
        return Line3D(point, tan_point1), Line3D(point, tan_point2)
    
    def getTangents2D(self, point: Point3D) -> tuple:
        """
        Calcola le linee tangenti dal punto al cilindro
        
        Args:
            point: Point2D - Il punto da cui partono le tangenti
            
        Returns:
            tuple(Line2D, Line2D) - Le due linee tangenti
        """
        point = Point2D(point.x, point.y)
        tan_point1, tan_point2 = self.getTangentPoints(point)
        return Line2D(point, tan_point1), Line2D(point, tan_point2)
    
    #DEPRECATED
    def getIntersectionA(self, edge: Segment3D, tolerance: float) -> tuple:
    
        """
        Calcola l'intersezione tra un segmento e il cilindro
        
        Args:
            edge: Segment3D - Il segmento da intersecare col cilindro
            
        Returns:
            tuple:
                - Boolean: True se il segmento interseca il cilindro in due punti
                - Segment3D/None: Segmento definito dai punti di intersezione o None
        """
        DEBUG = False
        p1, p2 = edge.points
        
        # Convertiamo in coordinate numpy per semplificare i calcoli
        p1_np = np.array([float(p1.x), float(p1.y), float(p1.z)])
        p2_np = np.array([float(p2.x), float(p2.y), float(p2.z)])
        base_center_np = np.array([float(self.bottom_center.x), float(self.bottom_center.y), float(self.bottom_center.z)])
        
        # Direzione del segmento
        v = p2_np - p1_np
        v_length = np.linalg.norm(v)
        
        if DEBUG: print(f"getIntersection - p1: {p1_np}, p2: {p2_np}, base: {base_center_np}, dir: {v}, dir_len: {v_length}")
        
        if v_length < tolerance:
            # Il segmento è troppo corto per essere considerato
            return False, None
        
        # Calcolo dell'intersezione con la superficie laterale del cilindro
        # Definiamo l'asse del cilindro come una linea da base_center a top_center
        # Poiché l'asse è parallelo all'asse Z, possiamo semplificare
        
        # Proiettiamo tutto sul piano XY
        cylinder_center_xy = np.array([base_center_np[0], base_center_np[1]])
        p1_xy = np.array([p1_np[0], p1_np[1]])
        p2_xy = np.array([p2_np[0], p2_np[1]])
        v_xy = p2_xy - p1_xy
        
        # Risolviamo l'equazione quadratica per le intersezioni
        # || p1_xy + t*v_xy - cylinder_center_xy ||^2 = radius^2
        
        w = p1_xy - cylinder_center_xy
        
        a = np.dot(v_xy, v_xy) # prodotto scalare di v_xy per se stesso (restiuisce v_xy^2) serve per verificare se v_xy è 0 (vettore con coord x=y=0 -> parallelo a z)
        b = 2 * np.dot(w, v_xy)
        c = np.dot(w, w) - self.radius**2
        
        discriminant = b**2 - 4*a*c
        
        if abs(a) < 1e-10:
            # Il segmento è parallelo all'asse Z
            # [logica per questo caso]
            return False, None
        
        if discriminant < 0:
            # Nessuna intersezione
            return False, None
        
        # Calcolo dei valori t per le intersezioni
        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        if DEBUG: print(f"getIntersection - v_xy: {v_xy}, w: {w}, a: {a}, b: {b}, c: {c}, discri: {discriminant}, t1: {t1}, t2: {t2}")
        
        # Filtra le intersezioni che sono sul segmento [0, 1]
        # e all'interno dell'altezza del cilindro
        # gestisce estremi interni al cilindro ed uno dei due estremi esterno al cilindro che interseca sulla base o sul top del cilindro (interno o esterno l raggio della circonferenza)
        # NON gestisce due estremi esterni che intersecano entrambi solo sulla base e o sul top del cilindro
        valid_intersections = []
        horizzontal_intersection = None # 
        
        for t in [t1, t2]:

            if 0 <= t <= 1:
                point_3d = p1_np + t * v
                if DEBUG: print(f"getIntersection - t: {t}, point_3d: {point_3d}")
                
                if base_center_np[2] <= point_3d[2] <= base_center_np[2] + (self.top_center.z - self.bottom_center.z):
                    valid_intersections.append(Point3D(point_3d[0], point_3d[1], point_3d[2]))                    
                
                elif point_3d[2] < base_center_np[2]:
                    horizzontal_intersection = Point3D(point_3d[0], point_3d[1], base_center_np[2])
                
                elif point_3d[2] > base_center_np[2]+ (self.top_center.z - self.bottom_center.z):
                    horizzontal_intersection = Point3D(point_3d[0], point_3d[1], base_center_np[2] + (self.top_center.z - self.bottom_center.z))
                    
        if not valid_intersections: 
            return False, None
        
        elif len(valid_intersections) == 1:
            # Un solo punto di intersezione
            if self.innerPoint(p1):
                return False, Segment3D(valid_intersections[0], p1)
            elif self.innerPoint(p2):
                return False, Segment3D(valid_intersections[0], p2)
            else: # una delle intersezioni è sulla base o sul top del cilindro        
                return False, Segment3D( valid_intersections[0], horizzontal_intersection )
        else:
            # Due punti di intersezione
            return True, Segment3D(valid_intersections[0], valid_intersections[1])

    def getIntersection(self, edge: Segment3D, tolerance: float) -> tuple:
        """
        Calcola l'intersezione tra un segmento e il cilindro,
        includendo superfici laterali e piani orizzontali (base e top).
        """
        p1, p2 = edge.points
        # Coord numpy
        p1_np = np.array([float(p1.x), float(p1.y), float(p1.z)])
        p2_np = np.array([float(p2.x), float(p2.y), float(p2.z)])
        v = p2_np - p1_np
        v_len = np.linalg.norm(v)
        if v_len < tolerance:
            return False, None

        base_np = np.array([float(self.bottom_center.x), float(self.bottom_center.y), float(self.bottom_center.z)])
        base_z = base_np[2]
        top_z = self.top_center.z

        # Intersezioni con superficie laterale (proiezione XY)
        cyl_xy = base_np[:2]
        p1_xy = p1_np[:2]
        v_xy = v[:2]
        w = p1_xy - cyl_xy
        a = np.dot(v_xy, v_xy)
        lateral_ts = []
        if abs(a) > 1e-12:
            b = 2 * np.dot(w, v_xy)
            c = np.dot(w, w) - self.radius**2
            disc = b*b - 4*a*c
            if disc >= 0:
                sqrt_d = math.sqrt(disc)
                t0 = (-b - sqrt_d) / (2*a)
                t1 = (-b + sqrt_d) / (2*a)
                for t in (t0, t1):
                    if 0 <= t <= 1:
                        P = p1_np + t * v
                        if base_z <= P[2] <= top_z:
                            lateral_ts.append(t)

        # Intersezioni con piani orizzontali base e top
        plane_ts = []
        if abs(v[2]) > 1e-12:
            for z_plane in (base_z, top_z):
                t = (z_plane - p1_np[2]) / v[2]
                if 0 <= t <= 1:
                    P = p1_np + t * v
                    # Verifica raggio
                    dx, dy = P[0] - base_np[0], P[1] - base_np[1]
                    if dx*dx + dy*dy <= self.radius**2 + tolerance:
                        plane_ts.append(t)

        # Unisci e ordina i parametri validi
        all_ts = sorted(set(lateral_ts + plane_ts))
        if not all_ts:
            return False, None

        # Calcola punti di intersezione
        pts = [Point3D(*(p1_np + t * v)) for t in all_ts]
        
        # Se due o più, prendiamo i primi due
        if len(pts) >= 2:
            return True, Segment3D(pts[0], pts[1])
        
        # Un solo punto rilevato
        single = pts[0]
        
        # Se un estremo è interno, lo consideriamo
        if self.innerPoint(p1):

            if single == p1:
                p1 = Point3D(single.x + 1e-6, single.y, single.z)                
            return False, Segment3D(single, p1)
        
        if self.innerPoint(p2):

            if single == p2:
                p2 = Point3D(single.x + 1e-6, single.y, single.z)
            return False, Segment3D(single, p2)
        
        # Altrimenti due piani orizzontali? duplicalo
        return False, Segment3D(single, single)



    def get_direction_vector(self, line):
        """Restituisce il vettore direzionale di una Line3D come un oggetto Matrix."""
        return Matrix([line.p2.x - line.p1.x, line.p2.y - line.p1.y, line.p2.z - line.p1.z])


    def are_parallel(self, line1: Line3D, line2: Line3D, tolerance=1e-6):
        # Ottieni i vettori direzionali delle linee
        dir1 = self.get_direction_vector(line1)
        dir2 = self.get_direction_vector(line2)

        # Calcola il prodotto vettoriale
        cross_product = dir1.cross(dir2)
        
        # Verifica se il prodotto vettoriale è vicino a zero
        return cross_product.norm() < tolerance


    def are_perpendicular(self, line1: Line3D, line2: Line3D, tolerance=1e-6):
        # Ottieni i vettori direzionali delle linee
        dir1 = self.get_direction_vector(line1)
        dir2 = self.get_direction_vector(line2)
        
        # Calcola il prodotto scalare
        dot_product = dir1.dot(dir2)
        
        # Verifica se il prodotto scalare è vicino a zero
        return abs(dot_product) < tolerance
    
    def getExtendedPoints(self, edge: Segment3D, tolerance = 1e-6) -> tuple:
        """
        Calcola i punti estesi relativi all'intersezione del segmento col cilindro. I punti estesi sonocostituiti dai punti d'intersezione delle tangenti al cilindro le cui origini sono  gli estremi del segmento.
        Qesti punti estesi sono definiti ad una quota z intermedia tra le quote z degli estremi del segmento
        
        Args:
            edge: Segment3D - Il segmento da analizzare
            tolerance: float - Tolleranza per la distanza tra i punti di intersezione (sotto li considera coincidenti, calcola e resituisce il punto medio in entrambi i valori della tupla)
            
        Returns:
            tuple(Point3D, Point3D) - I punti di intersezione delle tangenti
        """
        DEBUG = False
        # Verifica prima se c'è un'intersezione
        intersects, intersect_segment = self.getIntersection(edge, tolerance = 0.1)# nella mappa reale puoi aumentare tolerance es: 10 metri
        
        if DEBUG: print(f"getExtendedPoints - intersects: {intersects}, intersect_segment: {intersect_segment}")

        if not intersects or intersect_segment is None:
            return None, None
            
        # Ottiene i punti di intersezione
        p1, p2 = edge.points
        intersection_points = intersect_segment.points
        
        if len(intersection_points) != 2:
            # Se c'è solo un punto di intersezione, uno degli estremi è interno
            return None, None
            
        int1, int2 = intersection_points
        
        # Calcola le distanze da ciascun estremo del segmento ai punti di intersezione
        dist_p1_int1 = p1.distance(int1)
        dist_p1_int2 = p1.distance(int2)
        
        # Determina quale punto di intersezione è più vicino a quale estremo
        if dist_p1_int1 < dist_p1_int2:
            left_int, right_int = int1, int2
        else:
            left_int, right_int = int2, int1
            
        # Calcola la distanza tra i punti di intersezione
        distance = left_int.distance(right_int)

        if DEBUG: print(f"getExtendedPoints - left_int: {left_int}, right_int: {right_int}, distance: {distance}")
        
        if distance < tolerance:
            # Se i punti sono molto vicini, restituisci il punto medio
            mid_point = Point3D((left_int.x + right_int.x)/2, 
                               (left_int.y + right_int.y)/2, 
                               (left_int.z + right_int.z)/2)
            return mid_point, mid_point
            
        # Calcola il valore medio delle altezze dei due punti d'intersezione nel cilindro
        mid_z = (left_int.z + right_int.z) / 2

        # sostituisce le z di p1 e p2 (estremi segmento) con mid_z in modo da calcolare le tangenti sul piano mid_z. (per evitare i problemi di calcolo dell'intersezione delle tangenti 3D non complanari: sghembe ecc. )
        p1 = Point3D(p1.x, p1.y, mid_z)
        p2 = Point3D(p2.x, p2.y, mid_z)

        # Calcola le tangenti dai punti estremi del segmento (sul piano mid_z). Si considera p1 a sinistra del cilindro e p2 a destra
        left_tangents = self.getTangents(p1)
        right_tangents = self.getTangents(p2)
        
        if DEBUG: print(f"getExtendedPoints - left_tangents: {left_tangents}, right_tangents: {right_tangents}")

        # Da qui dovremmo calcolare l'intersezione delle tangenti
        # Dobbiamo identificare quali sono le tangenti "in alto" e "in basso"
        
        # Assumiamo che le tangenti siano ordinate in modo che la prima sia "in alto"
        # e la seconda sia "in basso" rispetto al segmento
            
        up_point = self._find_intersection_point( left_tangents[0], right_tangents[0] ) # tangenti superiori sia destra che sinistra in [0]       
        down_point = self._find_intersection_point(right_tangents[1], left_tangents[1] ) # tangenti inferiori  sia destra che sinistra in [1]       

        up_point_B = self._find_intersection_point( left_tangents[0], right_tangents[1] ) # tangente superiore di sinistra in [0], quella di destra in [1]              
        down_point_B = self._find_intersection_point(right_tangents[0], left_tangents[1] ) # tangente superiore di sinistra in [1], quella di destra in [0]              

        if DEBUG: print(f"getExtendedPoints - up_point: {up_point}, down_point: {down_point}, up_point_B: {up_point_B}, down_point_B: {down_point_B}")
   
        

        if up_point and down_point: 
            
            if up_point_B and down_point_B:
            
                if up_point.distance(self.center) > up_point_B.distance(self.center):            
                    up_point = up_point_B            
                    down_point = down_point_B
            
        elif up_point_B and down_point_B:                
            up_point = up_point_B            
            down_point = down_point_B
        
        

        if DEBUG: print(f"getExtendedPoints - up_point: {up_point}, down_point: {down_point}")
        
        return up_point, down_point
    
    def _find_intersection_point(self, line1: Line3D, line2: Line3D) -> Point3D:
        """
        Trova il punto di intersezione tra due linee, se esiste
        """
        DEBUG = False      
        
        inters = intersection(line1, line2)
        if DEBUG: print(f"_find_intersection_point - inters: {inters}")

        if inters:
            for point in inters:
                if isinstance(point, Point3D):
                    return point
        
        return None # non ci sono intersezioni

        # Se non c'è intersezione, le linee sono parallele o sghembe
        # In questo caso, troviamo il punto più vicino tra le due linee
        #p1, v1 = line1.p1, Matrix(line1.p2 - line1.p1).normalized()
        #p2, v2 = line2.p1, Matrix(line2.p2 - line2.p1).normalized()
        
        # Vettore che connette i punti sulle due linee
        #w0 = p1 - p2
        
        # Calcoli necessari per trovare i parametri t e s
        #a = v1.dot(v1)
        #b = v1.dot(v2)
        #c = v2.dot(v2)
        #d = v1.dot(w0)
        #e = v2.dot(w0)
        
        # Denominatore
        #denom = a*c - b*b
        
        #if abs(denom) < 1e-10:
            # Linee quasi parallele
            # Troviamo il punto medio tra p1 e la proiezione di p1 su line2
            #t = 0
            #s = b/c * t - e/c
        #else:
            #t = (b*e - c*d) / denom
            #s = (a*e - b*d) / denom
        
        # Punti più vicini sulle due linee
        #point1 = p1 + t * v1
        #point2 = p2 + s * v2
        
        # Punto medio
        #mid_point = Point3D((point1.x + point2.x) / 2, 
         #                 (point1.y + point2.y) / 2, 
          #                (point1.z + point2.z) / 2)
        
        #if DEBUG: print(f"_find_intersection_point - w0: {w0}, denom: {denom}, point1: {point1}, point2: {point2}, mid_point: {mid_point}")
        #return mid_point





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
    

    def find_chord_coordinates(self, R, center, A, B, L):
        """
        Calcola le coordinate degli estremi di una corda CD di lunghezza L
        che sia la più vicina possibile alla corda AB sulla circonferenza.
        
        Parametri:
        - R: raggio della circonferenza
        - center: tupla (x,y) delle coordinate del centro
        - A: tupla (x,y) delle coordinate del punto A
        - B: tupla (x,y) delle coordinate del punto B
        - L: lunghezza desiderata della corda CD
        
        Returns:
        - (C, D): tupla contenente le coordinate di C e D
        """
        # Estrai le coordinate
        x_c = center.x 
        y_c = center.y
        x_A = A.x 
        y_A = A.y
        x_B = B.x
        y_B = B.y
        
        # Verifica che A e B siano sulla circonferenza
        dist_A = math.sqrt((x_A - x_c)**2 + (y_A - y_c)**2)
        dist_B = math.sqrt((x_B - x_c)**2 + (y_B - y_c)**2)
        
        if abs(dist_A - R) > 1e-4 or abs(dist_B - R) > 1e-4:
            raise ValueError("I punti A e B devono essere sulla circonferenza")
        
        # Verifica che L sia una lunghezza valida per una corda (L ≤ 2R)
        if L > 2*R:
            L = R 
        
        # Calcola il punto medio della corda AB
        mid_AB = ((x_A + x_B)/2, (y_A + y_B)/2)
        
        # Calcola il vettore dal centro al punto medio di AB
        vec_c_mid = (mid_AB[0] - x_c, mid_AB[1] - y_c)
        
        # Normalizza il vettore
        norm = math.sqrt(vec_c_mid[0]**2 + vec_c_mid[1]**2)
        if norm < 1e-6:  # Se AB passa per il centro
            # In questo caso, qualsiasi corda perpendicolare ad AB può essere la risposta
            # Prendiamo un vettore perpendicolare arbitrario
            vec_dir = (1, 0) if abs(x_B - x_A) < 1e-6 else (-vec_c_mid[1]/norm, vec_c_mid[0]/norm)
        else:
            # Direzione normalizzata dal centro verso il punto medio di AB
            vec_dir = (vec_c_mid[0]/norm, vec_c_mid[1]/norm)
        
        # Calcola la distanza dal centro al punto medio della corda CD
        # Usando la formula: d = sqrt(R^2 - (L/2)^2)
        d = math.sqrt(R**2 - (L/2)**2)
        
        # Calcola il punto medio della corda CD
        mid_CD = (x_c + d * vec_dir[0], y_c + d * vec_dir[1])
        
        # Calcola il vettore perpendicolare alla direzione centro-medio
        perp_vec = (-vec_dir[1], vec_dir[0])
        
        # Calcola le coordinate di C e D
        half_L = L / 2
        C = (mid_CD[0] - half_L * perp_vec[0], mid_CD[1] - half_L * perp_vec[1])
        D = (mid_CD[0] + half_L * perp_vec[0], mid_CD[1] + half_L * perp_vec[1])
        #C = Point2D(mid_CD[0] - half_L * perp_vec[0], mid_CD[1] - half_L * perp_vec[1])
        #D = Point2D(mid_CD[0] + half_L * perp_vec[0], mid_CD[1] + half_L * perp_vec[1])
        # Verifica che C e D siano sulla circonferenza
        dist_C = math.sqrt((C[0] - x_c)**2 + (C[1] - y_c)**2)
        dist_D = math.sqrt((D[0] - x_c)**2 + (D[1] - y_c)**2)
        
        if abs(dist_C - R) > 1e-6 or abs(dist_D - R) > 1e-6:
            print(f"Attenzione: i punti calcolati potrebbero non essere esattamente sulla circonferenza")
            print(f"Distanza C dal centro: {dist_C}, differenza con R: {abs(dist_C - R)}")
            print(f"Distanza D dal centro: {dist_D}, differenza con R: {abs(dist_D - R)}")

        C = Point2D(C[0], C[1])
        D = Point2D(D[0], D[1])
        
        return (C, D)

    # da utilizzare se sivuole considerare anche il caso di un segmento con un estremo interno al cilindro (unica intersezione)
    def find_chord_endpoint(self, R, center, A, B, L):
        """
        Calcola le coordinate del punto D tale che la corda ID abbia lunghezza L,
        dove I è il punto di intersezione tra il segmento AB e la circonferenza.
        
        Parametri:
        - R: raggio della circonferenza
        - center: tupla (x,y) delle coordinate del centro
        - A: tupla (x,y) delle coordinate del punto A
        - B: tupla (x,y) delle coordinate del punto B
        - L: lunghezza desiderata della corda ID
        
        Returns:
        - (I, D): tupla contenente le coordinate di I e le due possibili soluzioni per D
        """
        x_c, y_c = center
        x_A, y_A = A
        x_B, y_B = B
        
        # Verifica che la lunghezza della corda L sia valida
        if L > 2*R:
            raise ValueError(f"La lunghezza L della corda non può superare il diametro (2R = {2*R})")
        
        # Calcolo del vettore direzionale AB
        dir_AB = (x_B - x_A, y_B - y_A)
        len_AB = math.sqrt(dir_AB[0]**2 + dir_AB[1]**2)
        
        if len_AB < 1e-10:
            raise ValueError("I punti A e B devono essere distinti")
        
        # Normalizzo il vettore
        dir_AB = (dir_AB[0]/len_AB, dir_AB[1]/len_AB)
        
        # Risolvo il sistema per trovare l'intersezione della retta AB con la circonferenza
        # Equazione parametrica della retta: P(t) = A + t * dir_AB
        # Sostituzione nell'equazione della circonferenza: |P(t) - center|^2 = R^2
        
        # Sviluppo l'equazione quadratica at^2 + bt + c = 0
        a = dir_AB[0]**2 + dir_AB[1]**2  # sempre uguale a 1 perché dir_AB è normalizzato
        b = 2 * ((x_A - x_c) * dir_AB[0] + (y_A - y_c) * dir_AB[1])
        c = (x_A - x_c)**2 + (y_A - y_c)**2 - R**2
        
        # Calcolo il discriminante
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            raise ValueError("La retta AB non interseca la circonferenza")
        
        # Se ci sono due intersezioni, prendo quella che cade sul segmento AB
        t1 = (-b + math.sqrt(discriminant)) / (2*a)
        t2 = (-b - math.sqrt(discriminant)) / (2*a)
        
        # Calcolo i punti di intersezione
        P1 = (x_A + t1 * dir_AB[0], y_A + t1 * dir_AB[1])
        P2 = (x_A + t2 * dir_AB[0], y_A + t2 * dir_AB[1])
        
        # Determino quale dei due punti (se esiste) è sull'effettivo segmento AB
        I = None
        if 0 <= t1 <= len_AB:
            I = P1
        if 0 <= t2 <= len_AB:
            if I is None or t2 < t1:  # Se ci sono due punti validi, prendo il più vicino ad A
                I = P2
        
        if I is None:
            raise ValueError("Il segmento AB non interseca la circonferenza")
        
        # Verifica che I sia sulla circonferenza
        dist_I = math.sqrt((I[0] - x_c)**2 + (I[1] - y_c)**2)
        if abs(dist_I - R) > 1e-10:
            print(f"Avviso: il punto I calcolato non è esattamente sulla circonferenza")
        
        # Ora dobbiamo trovare il punto D sulla circonferenza tale che |ID| = L
        
        # Angolo al centro sotteso dalla corda di lunghezza L
        theta = 2 * math.asin(L / (2 * R))
        
        # Vettore dal centro all'intersezione I
        CI = (I[0] - x_c, I[1] - y_c)
        len_CI = math.sqrt(CI[0]**2 + CI[1]**2)  # Dovrebbe essere R
        CI_norm = (CI[0]/len_CI, CI[1]/len_CI)  # Normalizzo
        
        # Ruoto CI_norm di theta in entrambe le direzioni
        rot1 = rotate_vector(CI_norm, theta)
        rot2 = rotate_vector(CI_norm, -theta)
        
        # Calcolo i due possibili punti D
        D1 = (x_c + R * rot1[0], y_c + R * rot1[1])
        D2 = (x_c + R * rot2[0], y_c + R * rot2[1])
        
        # Verifica lunghezza della corda ID
        len_ID1 = math.sqrt((D1[0] - I[0])**2 + (D1[1] - I[1])**2)
        len_ID2 = math.sqrt((D2[0] - I[0])**2 + (D2[1] - I[1])**2)
        
        # Controllo della precisione
        if abs(len_ID1 - L) > 1e-10 or abs(len_ID2 - L) > 1e-10:
            print(f"Avviso: le corde calcolate potrebbero non avere esattamente lunghezza L")
            print(f"Lunghezza ID1: {len_ID1}, differenza con L: {abs(len_ID1 - L)}")
            print(f"Lunghezza ID2: {len_ID2}, differenza con L: {abs(len_ID2 - L)}")
        
        return I, (D1, D2)


def rotate_vector(v, angle):
        """
        Ruota un vettore 2D di un dato angolo (in radianti)
        """
        cos_ang = math.cos(angle)
        sin_ang = math.sin(angle)
        return (v[0] * cos_ang - v[1] * sin_ang, 
                v[0] * sin_ang + v[1] * cos_ang)

