import heapq
import math
from sympy import Point3D, Point2D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict

class Waypoint:
    def __init__(self, name, point):
        self._name = name
        self._point = point

    @property
    def name(self):
        return self._name
    
    @property
    def point(self):
        return self._point
    
    def point2d(self):
        return Point2D(self.point.x, self.point.y)
    
    
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
    def __init__(self, wpA, wpB, speed, threats):
        self._wpA = wpA
        self._wpB = wpB
        self._speed = speed
        self._length = wpA.point.distance(wpB.point)
        self._danger = self.calculate_danger(threats)
    

    def calculate_danger(self, threats):
        danger = 0.0
        for threat in threats:
            result, intersections = self.intersects_threat(threat)

            if result:                                                    
                exposure_length = (intersections[1] - intersections[0]) * self.length
                exposure_time = exposure_length / self.speed
                danger += threat.danger_level * exposure_time
                
        return danger
    

    def point_in_cylinder(self, point, threat):
        distance_2d = point.distance(Point3D(threat.cylinder.center.x, threat.cylinder.center.y, point.z))
        return (distance_2d <= threat.cylinder.radius and threat.min_altitude <= point.z <= threat.cylinder.height)

    
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
    
    @property
    def wpA(self):
        return self._wpA
    
    @property
    def wpB(self):
        return self._wpB
    
    @property
    def speed(self):
        return self._speed
    
    @property
    def length(self):
        return self._length
    
    @property
    def danger(self):
        return self._danger

class ThreatAA:
    def __init__(self, danger_level: float, min_altitude: float, max_altitude: float, center: Point2D, radius: float):
        self.danger_level = danger_level
        
        self.cylinder = Cylinder(Point3D(center.x, center.y, min_altitude), radius, max_altitude-min_altitude)

        @property
        def min_altitude(self):
            return self.cylinder.center.z
        
        @property
        def max_altitude(self):
            return self.cylinder.height

class Cylinder:
    def __init__(self, center: Point3D, radius: float, height: float):
            
        self.center = center
        self.radius = radius
        self.height = height
        
        




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


    def find_neighbors(self, waypoint):
        neighbors = []
        step = 1
        directions = [
            (self.grid_step, 0, 0),
            (-self.grid_step, 0, 0),
            (0, self.grid_step, 0),
            (0, -self.grid_step, 0),
            (0, 0, self.grid_step),
            (0, 0, -self.grid_step)
        ]
        
        for dx, dy, dz in directions:
            new_point = Point3D(
                waypoint.point.x + dx,
                waypoint.point.y + dy,
                waypoint.point.z + dz
            )
            
            # Filtra movimenti puramente verticali nello stesso punto 2D
            if (dx == 0 and dy == 0) and (dz != 0):
                continue
                
            if (self.params['altitude_min'] <= new_point.z <= 
                self.params['altitude_max']):
                neighbors.append(Waypoint(f"wp_{new_point.x}_{new_point.y}_{new_point.z}", new_point))
        
        return neighbors
    
    def a_star(self):
        open_set = []
        heapq.heappush(open_set, (0, self.start))
        
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[self.start] = 0
        
        f_score = defaultdict(lambda: float('inf'))
        f_score[self.start] = self.heuristic(self.start)
        
        while open_set:
            current = heapq.heappop(open_set)[1]

            # DEBUG 2: Stampa informazioni sui vicini
            neighbors = self.find_neighbors(current)
            print(f"\nNodo corrente: {current.point}")
            print(f"Vicini trovati ({len(neighbors)}):")
            for n in neighbors:
                print(f"- {n.point}")
            # ---------------------------------
            
           
            if current.point == self.end.point:  # Confronto per coordinate
                return self.reconstruct_path(came_from, current)
            
            for neighbor in self.find_neighbors(current):
                edge = Edge(current, neighbor, self.params['speed_max'], self.threats)
                
                if edge.length > self.params['range_max']:
                    continue
                
                tentative_g_score = g_score[current] + edge.danger
                
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None
    
    def heuristic(self, waypoint):
        return waypoint.point.distance(self.end.point) / self.params['speed_max']
    
    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]


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


