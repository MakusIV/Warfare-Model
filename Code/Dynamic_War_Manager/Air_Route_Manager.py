import heapq
import math
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict
from Code.Dynamic_War_Manager.Cylinder import Cylinder


class ThreatAA:
    def __init__(self, danger_level, min_altitude: float, cylinder: Cylinder):
        self.danger_level = danger_level
        self.min_altitude = min_altitude
        self.cylinder = cylinder

        def edgeInRange(self, edge):
            segment = Segment3D(edge.wpA.point, edge.wpB.point)
            return cylinder.getIntersection(segment)
            


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
    
    
    def __init__(self, wpA: Waypoint, wpB: Waypoint, speed: float):
        self.name = f"{wpA.name}_{wpB.name}"
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

    def calcRoute(self, start: Point3D, end: Point3D, threats: list[ThreatAA], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float):      

      
        p1 = start
        p2 = end
        end = end
        path = dict(Route)

        # Calcola il percorso senza minacce
        self.calcPathWithoutThreat(p1, p2, end, threats, n_waypoint = 0, n_path = 0, path = {str(0): ()}, aircraft_altitude_min = aircraft_altitude_min , aircraft_altitude_max = aircraft_altitude_max, aircraft_speed_max = aircraft_speed_max, aircraft_speed = aircraft_speed, aircraft_range_max = aircraft_range_max)  

        if path.count > 0 and path[0] != None:
            return path
        
        # Se non ci sono percorsi senza minacce, calcola il percorso con le minacce                
        path = self.calcPathWithThreat(p1, p2, end, threats, n_waypoint = 0, n_path = 0, path = (), aircraft_altitude_min = aircraft_altitude_min , aircraft_altitude_max = aircraft_altitude_max, aircraft_speed_max = aircraft_speed_max, aircraft_speed = aircraft_speed, aircraft_range_max = aircraft_range_max)

        return path


    def nearThreatIntersecate(self, edge: Edge, threats: list[ThreatAA]):
        threat_distance = float('inf') # distanza da edge.wpa a threat.center
        near_threat = None

        for threat in threats:
            threatInrange, intersection = threat.edgeInRange(edge)
            
            if threatInrange:
                wpA_Intersection_distance = edge.wpA.point.distance(intersection[0]) # distanza dalla circonferenza della threat
                
                if wpA_Intersection_distance < threat_distance:
                    threat_distance = wpA_Intersection_distance
                    near_threat = threat

        return near_threat


    def calcPathWithoutThreat(self, p1: Point3D, p2: Point3D, end: Point3D, threats: list[ThreatAA], n_waypoint: int, n_path: int, path: list[Route], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float):  
        start = Waypoint(f"wp_{n_waypoint}", start)
        edge = Edge(p1, p2, speed = aircraft_speed)
        threat_intersect = self.nearThreatIntersecate(edge, threats)

        if not threat_intersect:
            path[str(n_path)].append(edge)
            
            if p2 == end:
                return path
            else:

        pass

    def calcPathWithThreat(self, start: Point3D, end: Point3D, threats: list[ThreatAA], n_path: int, path: dict, altitude_min: float, altitude_max: float):
        pass




def createRoute(start, end, threats, grid_step, grid_alt_step, range_max, speed_max, altitude_max, altitude_min):
    params = {
        'range_max': range_max,
        'speed_max': speed_max,
        'altitude_max': altitude_max,
        'altitude_min': altitude_min
    }
    
    planner = RoutePlanner(start, end, threats, params, grid_step, grid_alt_step)
    path = planner.a_star()
    
    if not path:
        return None
    
    route = Route("optimized_route")
    for i in range(len(path)-1):
        edge = Edge(path[i], path[i+1], speed_max, threats)
        route.add_edge(edge)


    return route

c
