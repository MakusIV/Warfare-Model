import heapq
import math
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict
from Code.Dynamic_War_Manager.Cylinder import Cylinder


MIN_LENGHT_SEGMENT = 0.1 # minimum length of segment to consider it as valid intersection

class ThreatAA:
    
    def __init__(self, danger_level, missile_speed: float, cylinder: Cylinder):
        self.danger_level = danger_level
        self.missile_speed = missile_speed
        self.min_altitude = cylinder.center.z
        self.max_altitude = cylinder.bottom_center.z
        self.cylinder = cylinder

    def edgeIntersect(self, edge):
        segment = Segment3D(edge.wpA.point, edge.wpB.point)        
        return self.cylinder.getIntersection(segment, tolerance = MIN_LENGHT_SEGMENT)
    
    def innerPoint(self, point:Point3D, tolerance: float):
            
        if self.cylinder.innerPoint(point):
            return True
        return False
          

class Waypoint:
    
    def __init__(self, name: str, point: Point3D, id: str|None):
        self.id = id
        self.name = name
        self.point = point
        self.point2d = Point2D(point.x, point.y)

        if not id:
            self.id = name
    
    
    def __lt__(self, other):
        # Implementazione di confronto basata sulle coordinate
        return (self.point.x, self.point.y, self.point.z) < (other.point.x, other.point.y, other.point.z)

    def __eq__(self, other):
        if not isinstance(other, Waypoint):
            return False
        return self.point == other.point

    def __hash__(self):
        return hash((self.point.x, self.point.y, self.point.z))


class Edge:
    
    
    def __init__(self, name: str, wpA: Waypoint, wpB: Waypoint, speed: float):
        self.name = name # name = "P: num path - E: num edge "
        self.wpA = wpA
        self.wpB = wpB
        self.speed = speed
        self.length = wpA.point.distance(wpB.point)
        self.danger = 0

    def getSegmet3D(self):
        return Segment3D(self.wpA.point, self.wpB.point)
    
   

    def calculate_danger(self, threats):
        danger = 0.0
        for threat in threats:
            result, intersections = self.intersects_threat(threat)

            if result:                                                    
                exposure_length = (intersections[1] - intersections[0]) * self.length
                exposure_time = exposure_length / self.speed
                danger += threat.danger_level * exposure_time
                
        return danger
        
    
    def intersects_threat(self, threat):        

        if (self.point_in_cylinder(self.wpA.point, threat) or self.point_in_cylinder(self.wpB.point, threat)):
            return True
        
        # Controllo punti coincidenti 2D
        if self.wpA.point2d() == self.wpB.point2d():
            point = self.wpA.point
            distance_2d = point.distance(Point3D(threat.cylinder.center.x, threat.cylinder.center.y, point.z))
            return (distance_2d <= threat.cylinder.radius and 
                    threat.min_altitude <= point.z <= threat.cylinder.height)
        
        # Creazione oggetti geometrici SymPy
        line2d = Line2D(self.wpA.point2d(), self.wpB.point2d())
        circle = Circle(threat.cylinder.center, threat.cylinder.radius)
        
        # Fase 1: Intersezione geometrica 2D
        intersections = line2d.intersection(circle)
        if not intersections:
            return False
        
        # Fase 2: Verifica parametrica 3D
        direction = self.wpB.point - self.wpA.point
        dx = direction.x
        dy = direction.y
        dz = direction.z
        
        # Equazione parametrica del segmento: P(t) = wpA + t*direction, t ∈ [0,1]
        a = dx**2 + dy**2
        b = 2*(dx*(self.wpA.point.x - threat.cylinder.center.x) + 
            dy*(self.wpA.point.y - threat.cylinder.center.y))
        c = ((self.wpA.point.x - threat.cylinder.center.x)**2 + 
            (self.wpA.point.y - threat.cylinder.center.y)**2 - 
            threat.cylinder.radius**2)
        
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return False, None
        
        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b + sqrt_disc) / (2*a)
        t2 = (-b - sqrt_disc) / (2*a)
        
        valid_t = sorted([t for t in [t1, t2] if 0 <= t <= 1])
                
        if len(valid_t) < 2:
            return False, None  # Solo tocco superficiale

        #for t in [t1, t2]:
        #    if 0 <= t <= 1:
        #        z = self.wpA.point.z + t*dz
        #        if threat.min_altitude <= z <= threat.cylinder.height:
        #            return True
        
        return True, valid_t
    
    def calculate_exposure(self, threat):
        direction = self.wpB.point - self.wpA.point
        t_values = []
        a = direction.x**2 + direction.y**2
        b = 2*(direction.x*(self.wpA.point.x - threat.cylinder.center.x) + direction.y*(self.wpA.point.y - threat.cylinder.center.y))
        c = (self.wpA.point.x - threat.cylinder.center.x)**2 + (self.wpA.point.y - threat.cylinder.center.y)**2 - threat.cylinder.radius**2
        
        sqrt_disc = math.sqrt(b**2 - 4*a*c)
        t1 = (-b + sqrt_disc)/(2*a)
        t2 = (-b - sqrt_disc)/(2*a)
        
        valid_t = []
        for t in [t1, t2]:
            if 0 <= t <= 1:
                z = self.wpA.point.z + t*direction.z
                if threat.min_altitude <= z <= threat.cylinder.height:
                    valid_t.append(t)
        
        if len(valid_t) < 2:
            return (0, 0)
        
        return (min(valid_t), max(valid_t))
    
    
class Route:

    def __init__(self, name):
        self.name = name
        self.edges = {}
    
    def add_edge(self, edge):
        self.edges[(edge.wpA, edge.wpB)] = edge
    
    def getWaypoints(self):
        path = []
        current = self.edges[(self.start, next(iter(self.edges))[0])].wpA

        while True:
            path.append(current)
            next_edges = [e for (a, b), e in self.edges.items() if a == current]
        
            if not next_edges:
                break
            current = next_edges[0].wpB

        return path



class RoutePlanner:

    def __init__(self, start, end, threats, params, grid_step, grid_alt_step):
        self.start = start
        self.end = end
        self.threats = threats
        self.params = params
        self.grid_step = grid_step #5000  # 5km grid resolution
        self.grid_alt_step = grid_alt_step  #1000  # 1km vertical resolution
        self.grid = self.generate_grid()
    
    def generate_grid(self):
        grid = []
        x_range = range(self.start.point.x - 2, self.start.point.x + 3)
        y_range = range(self.start.point.y - 2, self.start.point.y + 3)
        
        for x in x_range:
            for y in y_range:
                for z in range(self.params['altitude_min'], 
                            self.params['altitude_max'] + 1):
                    if (x, y) != (self.start.point.x, self.start.point.y):
                        grid.append(Waypoint(f"wp_{x}_{y}_{z}", Point3D(x, y, z)))
        
        grid.append(self.end)
        return grid    
    
    def heuristic(self, waypoint):
        return waypoint.point.distance(self.end.point) / self.params['speed_max']
    
    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def calcRoute(self, start: Point3D, end: Point3D, threats: list[ThreatAA], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, change_alt_option: str = "no_change"):      


        # change_alt_option: str = "no_change", "change_down", "change_up"
        # ricorda in threats devono essere escluse le threat che includono i 
      
        p1 = start
        p2 = end
        end = end        
        n_edge = 0, 
        n_path = 0
        found_path = False
        path = {str(0): ()} #dict(Route)
    

        # esclusione dal calcolo delle threats che includono l'inizio e la fine del percorso
        self.excludeThreat(threats, start)
        self.excludeThreat(threats, end)

        # Calcola il percorso senza minacce (path è passato come riferimento e dovrebbe essere aggiornato dal metodo)
        found_path = self.calcPathWithoutThreat(p1, p2, end, threats, n_edge, n_path, path, aircraft_altitude_min , aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)  

        if found_path:
            lenght_path = self.calcLenghtPath(path)
            
            if lenght_path <= aircraft_range_max:
                return path
        
        # Se non ci sono percorsi senza minacce, calcola il percorso con le minacce (path è passato come riferimento e dovrebbe essere aggiornato dal metodo)                
        found_path = self.calcPathWithThreat(p1, p2, end, threats, n_edge, n_path, path, aircraft_altitude_min , aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

        if found_path:
            lenght_path = self.calcLenghtPath(path)
            
            if lenght_path <= aircraft_range_max:
                return path
        
        return None

    def excludeThreat(self, threats: list[ThreatAA], point: Point3D):
        
        for threat in threats:
            
            if threat.innerPoint(point):
                threats.remove(threat)
                
        return True 


    def firstThreatIntersected(self, edge: Edge, threats: list[ThreatAA]) -> ThreatAA:
        DEBUG = False
        threat_distance = float('inf') # distanza da edge.wpa a threat.center
        first_threat = None

        for threat in threats:
            threatInrange, intersection = threat.edgeIntersect(edge)
            
            if threatInrange:
                wpA_Intersection_distance = edge.wpA.point.distance(intersection[0]) # distanza dalla circonferenza della threat
                
                if wpA_Intersection_distance < threat_distance:
                    threat_distance = wpA_Intersection_distance
                    first_threat = threat                    
                    if DEBUG: print(f"Found threat intersection at lesser distance: threat: {threat}, threat_distance: {threat_distance}")        

        return first_threat

    
    def calcPathWithoutThreat(self, p1: Point3D, p2: Point3D, end: Point3D, threats: list[ThreatAA], n_edge: int, n_path: int, path: list[Route], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, change_alt_option: str) -> bool:  
        DEBUG = False
        wp_A = Waypoint(f"wp_A{n_edge}", p1)
        wp_B = Waypoint(f"wp_B{n_edge}", p2)
        edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed)
        threat_intersect = self.firstThreatIntersected(edge, threats)        

        if DEBUG: print(f"n_path: {n_path}, n_edge: {n_edge}, wp_A: {wp_A}, wp_B: {wp_B}, threat_intersect: {threat_intersect}")

        if not threat_intersect: # nessuna minaccia interseca l'edge p1-p2
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            if DEBUG: print(f"no threat intersect, path: {path}")
            
            if p2 == end: # se p2 coincide con la fine del percorso il calcolo del percorso termina
                return True #path
            
            else: # se p2 non coincide con la fine del percorso, chiama ricorsvamente la funzione considerando p2 come nuovo punto di partenza, end il punto p2 ed incrementando di 1 n_edge
                self.calcPathWithoutThreat(p2, end, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)        
        
        elif aircraft_altitude_max > threat_intersect.max_altitude or aircraft_altitude_min < threat_intersect.min_altitude and change_alt_option != "no_change": # l'aereo può passare sopra o sotto la minaccia
            intersected, segm = threat_intersect.cylinder.getIntersection(edge.getSegmet3D(), tolerance = MIN_LENGHT_SEGMENT) # determina il segmento di intersezione dell'edge con la minaccia
            
            if not intersected:
                raise Exception(f"Unexpected value intersected is {intersected} but must be True - threat_intersect: {threat_intersect}, n_path: {n_path}, n_edge: {n_edge}")
            
            new_p1 = segm[0].point # crea un nuovo punto considerando il punto d'intersezione del cilindro 

            if change_alt_option == "change_up":
                new_p1.z = threat_intersect.max_altitude + 1 # imposta la coordinata z del nuovo punto con l'altezza massima della della minaccia +1            
            
            elif change_alt_option == "change_down":
                new_p1.z = threat_intersect.min_altitude - 1 # imposta la coordinata z del nuovo punto con l'altezza minima della della minaccia - 1            
            
            else:
                raise ValueError(f"Unexpected value of change_alt_option: {change_alt_option}. change_alt_option must be: /'no_change'', /'change_up' or /'change_down'")
                        
            wp_B = Waypoint(f"wp_B{n_edge}", new_p1 ) # crea un nuovo waypoint B con il nuovo punto
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            
            if DEBUG: print(f"l'aereo può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}) Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")
            
            # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
            self.calcPathWithoutThreat(new_p1, p2, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)


        else: # l'aereo non può passare sotto o sopra la minaccia
            # determina i due punti esterni alla minaccia. NOTA: la tolleranza di 0.001 è solo se i test di unità li imposti con mappe limitate da 0 a 10.
            # Nota: non è considerata la gestione di un segmento con un'estremo interno alla threat (getEstendedPoints restituisce None, None) in quanto non dovrebbe essere possibile: partendo da segmenti tra inizio e fine i diversi edge valutati dovrebbero solo intersecare, non interseca oppure essere tangenti alle threats
            ext_p1, ext_p2 = threat_intersect.cylinder.getExtendedPoints(edge.getSegmet3D(), tolerance = 0.001) 
            
            if not ext_p1 or not ext_p2:
                raise Exception(f"Unexpected value ext_p1: {ext_p1}, ext_p2: {ext_p2} - threat_intersect: {threat_intersect}, n_path: {n_path}, n_edge: {n_edge}")
            
            # valutazione primo path con ext_p1 (il primo path si considera come prosecuzione del path già considerato)
            wp_B = Waypoint(f"wp_B{n_edge}", ext_p1 ) # crea un nuovo waypoint B con il nuovo punto ext_p1
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)

            if DEBUG: print(f"l'aereo non può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}). Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")

            # ricalcola il percorso per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithoutThreat(p1, ext_p1, end, threats, n_edge, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)
            
            # valutazione secondo path con ext_p1 (costituisce un nuovo path)
            wp_B = Waypoint(f"wp_B{n_edge}", ext_p2 ) # crea un nuovo waypoint B con il nuovo punto ext_p2
            edge = Edge(f"P:{n_path + 1}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)

            if DEBUG: print(f"  - Calcolo nuovo percorso: Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path({n_path + 1}): {path}")

            # ricalcola il percorso aggiungendo un nuovo path, per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithoutThreat(p1, ext_p2, end, threats, n_edge, n_path + 1, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

    def calcPathWithThreat(self, p1: Point3D, p2: Point3D, end: Point3D, threats: list[ThreatAA], n_edge: int, n_path: int, path: list[Route], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, change_alt_option: str) -> bool:
        DEBUG = False
        wp_A = Waypoint(f"wp_A{n_edge}", p1)
        wp_B = Waypoint(f"wp_B{n_edge}", p2)
        edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed)
        threat_intersect = self.firstThreatIntersected(edge, threats)        

        if DEBUG: print(f"n_path: {n_path}, n_edge: {n_edge}, wp_A: {wp_A}, wp_B: {wp_B}, threat_intersect: {threat_intersect}")

        if not threat_intersect: # nessuna minaccia interseca l'edge p1-p2
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            if DEBUG: print(f"no threat intersect, path: {path}")
            
            if p2 == end: # se p2 coincide con la fine del percorso il calcolo del percorso termina
                return True #path
            
            else: # se p2 non coincide con la fine del percorso, chiama ricorsvamente la funzione considerando p2 come nuovo punto di partenza, end il punto p2 ed incrementando di 1 n_edge
                self.calcPathWithThreat(p2, end, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)        
        
        elif aircraft_altitude_max > threat_intersect.max_altitude or aircraft_altitude_min < threat_intersect.min_altitude and change_alt_option != "no_change": # l'aereo può passare sopra o sotto la minaccia
            intersected, segm = threat_intersect.cylinder.getIntersection(edge.getSegmet3D(), tolerance = MIN_LENGHT_SEGMENT) # determina il segmento di intersezione dell'edge con la minaccia
            
            if not intersected:
                raise Exception(f"Unexpected value intersected is {intersected} but must be True - threat_intersect: {threat_intersect}, n_path: {n_path}, n_edge: {n_edge}")
            
            new_p1 = segm[0].point # crea un nuovo punto considerando il punto d'intersezione del cilindro 

            if change_alt_option == "change_up":
                new_p1.z = threat_intersect.max_altitude + 1 # imposta la coordinata z del nuovo punto con l'altezza massima della della minaccia +1            
            
            elif change_alt_option == "change_down":
                new_p1.z = threat_intersect.min_altitude - 1 # imposta la coordinata z del nuovo punto con l'altezza minima della della minaccia - 1            
            
            else:
                raise ValueError(f"Unexpected value of change_alt_option: {change_alt_option}. change_alt_option must be: /'no_change'', /'change_up' or /'change_down'")
                        
            wp_B = Waypoint(f"wp_B{n_edge}", new_p1 ) # crea un nuovo waypoint B con il nuovo punto
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            
            if DEBUG: print(f"l'aereo può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}) Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")
            
            # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
            self.calcPathWithThreat(new_p1, p2, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)


        else: # l'aereo non può passare sotto o sopra la minaccia        

            # determina i due punti esterni alla minaccia. NOTA: la tolleranza di 0.001 è solo se i test di unità li imposti con mappe limitate da 0 a 10.
            max_lenght = calcMaxLenghtCrossSegment(aircraft_speed, aircraft_altitude_max, threat_intersect.missile_speed, threat_intersect.cylinder.center, threat_intersect.cylinder.radius, threat_intersect.cylinder.time_to_inversion, threat_intersect.cylinder.time_sam_launch, edge.getSegmet3D()) # calcola la lunghezza massima del segmento che può attraversare la minaccia    
            valid_intersection, segment = threat_intersect.cylinder.getIntersection(edge.getSegmet3D(), tolerance = max_lenght) # determina il segmento di intersezione dell'edge con la minaccia            

            if DEBUG: print(f"l'aereo non può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}).\n Lunghezza massima attraversmaneto {max_lenght}")
            
            if not valid_intersection: # intersezione non valida: nessuna intersezione, segmento tangente, segmento con solo un punto di intersezione, segmento ha una lunghezza inferiore rispetto alla lunghezza massima considerata come tolerance
                
                if not segment: # nessuna intersezione, segmento parallelo asse z, segmento ha una lunghezza inferiore rispetto alla lunghezza massima considerata come tolerance
                    path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso

                    if DEBUG: print(f"no itersection or inner threat edge lenght is lesser of max_lenght: {max_lenght}. threat center: {threat_intersect.cylinder.center}, threat radius: {threat_intersect.cylinder.radius}, edge: {edge}, segment: {segment}")

                    if p2 == end: # se p2 coincide con la fine del percorso il calcolo del percorso termina
                        return True #path
            
                    else: # se p2 non coincide con la fine del percorso, chiama ricorsivamente la funzione considerando p2 come nuovo punto di partenza, end il punto p2 ed incrementando di 1 n_edge
                        self.calcPathWithThreat(p2, end, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)        

                else: # segmento con solo un punto di intersezione
                    raise Exception(f"segment with only one intersection point: {segment}, path: {n_path}: {path}")
                    # TODO: gestire il caso di un segmento con un estremo interno alla threat (unica intersezione). Da valutare per un utilizzo che preveda edge con un estremo interno alla threat
                    I, D1, D2 = self.find_chord_endpoint(threat_intersect.cylinder.radius, threat_intersect.cylinder.center, edge.wpA.point2d(), edge.wpB.point2d(), max_lenght) # calcola i punti C e D della corda CD che è la più vicina possibile alla corda AB sulla circonferenza                    
                    intersection = segment[0].point
                    if (I - intersection).length() > le-1:# I e intersection devono essere coincidenti
                        raise Exception(f"Incongruent intersection calculus from find_chord_endpoint: intersection({I}) and threat_intersect.cylinder.getIntersection: intersection({intersection}) - segment: {segment}, path: {n_path}: {path}")
                    wp_B = Waypoint(f"wp_B{n_edge}", intersection ) # crea un nuovo waypoint B con il nuovo punto
                    edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
                    path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso attuale
                    path[str(n_path + 1)].append(edge) # l'edge viene anche aggiunto al nuovo percorso

                    # calcolo secondo edge basato sulla prima corda di lunghezza = max_lenght
                    wp_A = Waypoint(f"wp_A{n_edge}", intersection ) # crea un nuovo waypoint A con il punto d'intersezione
                    wp_B = Waypoint(f"wp_B{n_edge}", D1 ) # crea un nuovo waypoint B con l'estremo D della prima corda di lunghezza = max_lenght
                    edge = Edge(f"P:{n_path}-E:{n_edge + 1}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
                    path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
                    # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
                    self.calcPathWithThreat(D1, end, end, threats, n_edge + 2, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

                    # calcolo secondo edge per nuovo path basato sulla seconda corda di lunghezza = max_lenght
                    wp_B = Waypoint(f"wp_B{n_edge}", D2 ) # crea un nuovo waypoint B con l'estremo D della prima corda di lunghezza = max_lenght
                    edge = Edge(f"P:{n_path}-E:{n_edge + 1 }", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
                    path[str(n_path + 1)].append(edge) # l'edge viene aggiunto al percorso
                    # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
                    self.calcPathWithThreat(D2,end, end, threats, n_edge + 2, n_path + 1, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

            #edge attraversa la threat definendo un segmento di intersezione        
            c, d = find_chord_coordinates(threat_intersect.cylinder.radius, threat_intersect.cylinder.center, edge.wpA.point2d(), edge.wpB.point2d(), max_lenght) # calcola i punti C e D della corda CD che è la più vicina possibile alla corda AB sulla circonferenza                        
            wp_B = Waypoint( f"wp_B{n_edge}", c ) # crea un nuovo waypoint B con il nuovo punto c
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)            
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            
            if DEBUG: print(f"l'aereo non può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}). Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")

            wp_A = Waypoint( f"wp_B{n_edge}", c ) # crea un nuovo waypoint A con il nuovo punto c
            wp_B = Waypoint( f"wp_B{n_edge}", d ) # crea un nuovo waypoint B con il nuovo punto ext_d            
            edge = Edge( f"P:{n_path}-E:{n_edge + 1}", wp_A, wp_B, speed = aircraft_speed ) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso

            if DEBUG: print(f"  - Calcolo aggiornamento percorso base: wp_A: {wp_A}, wp_B: {wp_B}, edge: {edge} inserito nel path: {n_path}: {path}")

            # ricalcola il percorso aggiungendo un nuovo path, per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithThreat(d, end, end, threats, n_edge + 2, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

        return False




def calcMaxLenghtCrossSegment(aircraft_speed: float, aircraft_altitude: float, missile_speed: float, threat_center: Point3D , threat_radius: float, time_to_inversion: float, time_sam_launch: float, segment: Segment3D) -> float:
    
    a= 1/aircraft_speed 
    b = 0.5/missile_speed 
    c = -(threat_radius + aircraft_altitude*aircraft_altitude) / aircraft_speed
    delta = b**2 - 4*a*c
    
    if delta < 0:
        return 0
    
    sqrt_delta = math.sqrt(delta)
    lm1 = (-b + sqrt_delta) / (2*a)
    lm2 = (-b - sqrt_delta) / (2*a)
    
    if lm1 <= 0 and lm2 <= 0:
        return 0
    
    if lm1>lm2:
        lm = lm1
        
    else:
        lm = lm2
    

    time_max_in_threat_zone = lm * missile_speed
    max_segmanet_lenght_in_threat_zone = ( time_max_in_threat_zone + time_to_inversion + time_sam_launch) * aircraft_speed


    return max_segmanet_lenght_in_threat_zone


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
    x_c, y_c = center
    x_A, y_A = A
    x_B, y_B = B
    
    # Verifica che A e B siano sulla circonferenza
    dist_A = math.sqrt((x_A - x_c)**2 + (y_A - y_c)**2)
    dist_B = math.sqrt((x_B - x_c)**2 + (y_B - y_c)**2)
    
    if abs(dist_A - R) > 1e-10 or abs(dist_B - R) > 1e-10:
        raise ValueError("I punti A e B devono essere sulla circonferenza")
    
    # Verifica che L sia una lunghezza valida per una corda (L ≤ 2R)
    if L > 2*R:
        raise ValueError(f"La lunghezza L della corda non può superare il diametro (2R = {2*R})")
    
    # Calcola il punto medio della corda AB
    mid_AB = ((x_A + x_B)/2, (y_A + y_B)/2)
    
    # Calcola il vettore dal centro al punto medio di AB
    vec_c_mid = (mid_AB[0] - x_c, mid_AB[1] - y_c)
    
    # Normalizza il vettore
    norm = math.sqrt(vec_c_mid[0]**2 + vec_c_mid[1]**2)
    if norm < 1e-10:  # Se AB passa per il centro
        # In questo caso, qualsiasi corda perpendicolare ad AB può essere la risposta
        # Prendiamo un vettore perpendicolare arbitrario
        vec_dir = (1, 0) if abs(x_B - x_A) < 1e-10 else (-vec_c_mid[1]/norm, vec_c_mid[0]/norm)
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
    
    # Verifica che C e D siano sulla circonferenza
    dist_C = math.sqrt((C[0] - x_c)**2 + (C[1] - y_c)**2)
    dist_D = math.sqrt((D[0] - x_c)**2 + (D[1] - y_c)**2)
    
    if abs(dist_C - R) > 1e-10 or abs(dist_D - R) > 1e-10:
        print(f"Attenzione: i punti calcolati potrebbero non essere esattamente sulla circonferenza")
        print(f"Distanza C dal centro: {dist_C}, differenza con R: {abs(dist_C - R)}")
        print(f"Distanza D dal centro: {dist_D}, differenza con R: {abs(dist_D - R)}")
    
    return (C, D)

# da utilizzare se sivuole considerare anche il caso di un segmento con un estremo interno alla threat (unica intersezione)
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