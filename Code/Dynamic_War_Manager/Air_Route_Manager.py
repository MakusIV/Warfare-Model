import heapq
import math
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict
from Code.Dynamic_War_Manager.Cylinder import Cylinder


class ThreatAA:
    
    def __init__(self, danger_level, min_altitude: float, cylinder: Cylinder):
        self.danger_level = danger_level
        self.min_altitude = cylinder.center.z
        self.max_altitude = cylinder.bottom_center.z
        self.cylinder = cylinder

    def edgeIntersect(self, edge):
        segment = Segment3D(edge.wpA.point, edge.wpB.point)        
        return self.cylinder.getIntersection(segment)
    
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
            return path
        
        # Se non ci sono percorsi senza minacce, calcola il percorso con le minacce (path è passato come riferimento e dovrebbe essere aggiornato dal metodo)                
        found_path = self.calcPathWithThreat(p1, p2, end, threats, n_edge, n_path, path, aircraft_altitude_min , aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

        if found_path:
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
        
        elif ( aircraft_altitude_max > threat_intersect.max_altitude + 1 or aircraft_altitude_min < threat_intersect.min_altitude -1 ) and change_alt_option != "no_change": # l'aereo può passare sopra o sotto la minaccia
            intersected, segm = threat_intersect.cylinder.getIntersection(edge.getSegmet3D()) # determina il segmento di intersezione dell'edge con la minaccia
            
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
            
            if DEBUG: print(f"l'aereo può passare sopra o sotto la minaccia, aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")
            
            # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
            self.calcPathWithoutThreat(new_p1, p2, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)


        else: # l'aereo non può passare sotto o sopra la minaccia
            # determina i due punti esterni alla minaccia. NOTA: la tolleranza di 0.001 è solo se i test di unità li imposti con mappe limitate da 0 a 10.
            ext_p1, ext_p2 = threat_intersect.cylinder.getExtendedPoints(edge.getSegmet3D(), 0.001) 
            
            # valutazione primo path con ext_p1 (il primo path si considera come prosecuzione del path già considerato)
            wp_B = Waypoint(f"wp_B{n_edge}", ext_p1 ) # crea un nuovo waypoint B con il nuovo punto ext_p1
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)

            if DEBUG: print(f"l'aereo non può passare sopra o sotto la minaccia:\n  - Calcolo aggiornamento percorso base: wp_B: {wp_B}, edge: {edge}")

            # ricalcola il percorso per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithoutThreat(p1, ext_p1, end, threats, n_edge, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)
            
            # valutazione secondo path con ext_p1 (costituisce un nuovo path)
            wp_B = Waypoint(f"wp_B{n_edge}", ext_p2 ) # crea un nuovo waypoint B con il nuovo punto ext_p2
            edge = Edge(f"P:{n_path + 1}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)

            if DEBUG: print(f"  - Calcolo nuovo percorso n_path{n_path + 1}, wp_B: {wp_B}, edge: {edge}")

            # ricalcola il percorso aggiungendo un nuovo path, per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithoutThreat(p1, ext_p2, end, threats, n_edge, n_path + 1, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

    def calcPathWithThreat(self, p1: Point3D, p2: Point3D, end: Point3D, threats: list[ThreatAA], n_edge: int, n_path: int, path: list[Route], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, change_alt_option: str) -> bool:

        
        pass




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
    
    if lm1 < 0 and lm2 < 0:
        return 0
    
    if lm1>lm2:
        lm = lm1
    else:
        lm = lm2
    

    time_max_in_threat_zone = lm * missile_speed
    max_segmanet_lenght_in_threat_zone = ( time_max_in_threat_zone + time_to_inversion + time_sam_launch) * aircraft_speed


    return max_segmanet_lenght_in_threat_zone
