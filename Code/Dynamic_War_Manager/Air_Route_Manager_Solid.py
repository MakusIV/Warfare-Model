import heapq
from sympy import Point, Point3D, Point2D
from sympy.geometry import intersection, Plane, Segment3D
from sympy.utilities.iterables import subsets
from collections import defaultdict

class SolidoParallelepipedo:
    def __init__(self, base_center, side_length, base_z, height):
        self.base_center = Point(base_center[0], base_center[1])
        self.side_length = side_length
        self.base_z = base_z
        self.height = height
        self.top_z = base_z + height

        # Calcola i limiti del solido
        half = side_length / 2
        self.x_min = float(self.base_center.x - half)
        self.x_max = float(self.base_center.x + half)
        self.y_min = float(self.base_center.y - half)
        self.y_max = float(self.base_center.y + half)
        self.z_min = float(base_z)
        self.z_max = float(base_z + height)

    def contiene_punto(self, point):
        x, y, z = float(point.x), float(point.y), float(point.z)
        return (self.x_min <= x <= self.x_max and
                self.y_min <= y <= self.y_max and
                self.z_min <= z <= self.z_max)

    def interseca_segmento(self, segmento):
        for plane in self._get_faces():
            inter = plane.intersection(segmento)
            if inter:
                if isinstance(inter[0], Segment3D):
                    point = inter[0].p1
                    
                elif isinstance(inter[0], Point3D):
                    point = inter[0]
                else:
                    raise ValueError(f"Intersezione non valida - self: {self}, plane: {plane}, segment: {segmento}, inter[0]: {inter[0]}")
                    
                if (self.x_min <= point.x <= self.x_max and
                    self.y_min <= point.y <= self.y_max and
                    self.base_z <= point.z <= self.top_z):
                    return True, point
        return False, None

    def _get_faces(self):
        # Crea 6 piani per le facce del parallelepipedo
        return [
            # Faccia superiore (z = top_z)
            Plane(
                Point3D(self.x_min, self.y_min, self.top_z),
                Point3D(self.x_max, self.y_min, self.top_z),
                Point3D(self.x_min, self.y_max, self.top_z)
            ),
            # Faccia inferiore (z = base_z)
            Plane(
                Point3D(self.x_min, self.y_min, self.base_z),
                Point3D(self.x_max, self.y_min, self.base_z),
                Point3D(self.x_min, self.y_max, self.base_z)
            ),
            # Faccia x = x_min
            Plane(
                Point3D(self.x_min, self.y_min, self.base_z),
                Point3D(self.x_min, self.y_max, self.base_z),
                Point3D(self.x_min, self.y_min, self.top_z)
            ),
            # Faccia x = x_max
            Plane(
                Point3D(self.x_max, self.y_min, self.base_z),
                Point3D(self.x_max, self.y_max, self.base_z),
                Point3D(self.x_max, self.y_min, self.top_z)
            ),
            # Faccia y = y_min
            Plane(
                Point3D(self.x_min, self.y_min, self.base_z),
                Point3D(self.x_max, self.y_min, self.base_z),
                Point3D(self.x_min, self.y_min, self.top_z)
            ),
            # Faccia y = y_max
            Plane(
                Point3D(self.x_min, self.y_max, self.base_z),
                Point3D(self.x_max, self.y_max, self.base_z),
                Point3D(self.x_min, self.y_max, self.top_z)
            )
        ]
""""
class SolidoComposto:
    def __init__(self, solidi):
        self.solidi = solidi
        self.x_min = min(s.x_min for s in solidi)
        self.x_max = max(s.x_max for s in solidi)
        self.y_min = min(s.y_min for s in solidi)
        self.y_max = max(s.y_max for s in solidi)
        self.z_min = min(s.z_min for s in solidi)
        self.z_max = max(s.z_max for s in solidi)

    def contiene_punto(self, point):
        return any(s.contiene_punto(point) for s in self.solidi)

    def interseca_segmento(self, segmento):
        for face in self._get_faces():
            plane = face['plane']
            inter = plane.intersection(segmento)
            
            if not inter:
                continue
                
            point = inter[0]
            
            if 'z_val' in face:  # Facce superiore/inferiore
                if (face['x_lim'][0] <= point.x <= face['x_lim'][1] and 
                   face['y_lim'][0] <= point.y <= face['y_lim'][1]):
                    return True, point
                    
            elif 'x_val' in face:  # Facce laterali x
                if (face['y_lim'][0] <= point.y <= face['y_lim'][1] and 
                   face['z_lim'][0] <= point.z <= face['z_lim'][1]):
                    return True, point
                    
            elif 'y_val' in face:  # Facce laterali y
                if (face['x_lim'][0] <= point.x <= face['x_lim'][1] and 
                   face['z_lim'][0] <= point.z <= face['z_lim'][1]):
                    return True, point
        
        return False, None
"""
class Waypoint:
    _counter = 0

    @classmethod
    def reset_counter(cls):
        cls._counter = 0

    def __init__(self, point):
        Waypoint._counter += 1
        self.name = f"wp_{Waypoint._counter}"
        self._point = Point3D(point)

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, value):
        self._point = Point3D(value)

    def point2d(self):
        return Point2D(self.point.x, self.point.y)

class Edge:
    _counter = 0

    def __init__(self, wp_A, wp_B):
        self._segment = Segment3D(wp_A.point, wp_B.point)  # Usare Segment3D
        Edge._counter += 1
        self.name = f"edg_{wp_A.name.split('_')[1]}_{wp_B.name.split('_')[1]}"
        self.wp_A = wp_A
        self.wp_B = wp_B

    @property
    def length(self):
        return float(self._segment.length)

    def interseca_solido(self, solido):
        return solido.interseca_segmento(self._segment)

class Route:
    def __init__(self, edges):
        self.edges = edges

    @property
    def length(self):
        return sum(edge.length for edge in self.edges)

"""
def riconosci_composti(solidi):
    graph = defaultdict(list)
    for a, b in subsets(solidi, 2):
        if intersecano(a, b):
            graph[a].append(b)
            graph[b].append(a)
    
    visited = set()
    composti = []
    for solido in solidi:
        if solido not in visited:
            stack = [solido]
            gruppo = []
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    gruppo.append(current)
                    stack.extend(graph[current])
            if len(gruppo) > 1:
                composti.append(SolidoComposto(gruppo))
            else:
                composti.extend(gruppo)
    return composti
"""

def intersecano(a, b):
    return not (a.x_max < b.x_min or a.x_min > b.x_max or
                a.y_max < b.y_min or a.y_min > b.y_max or
                a.z_max < b.z_min or a.z_min > b.z_max)

def crea_percorso(mappa, wp_start, wp_end, altitude_min, altitude_max):
    solidi_esclusi = []
    for solido in mappa.solidi:
        if solido.contiene_punto(wp_start.point) or solido.contiene_punto(wp_end.point):
            solidi_esclusi.append(solido)
    solidi_validi = [s for s in mappa.solidi if s not in solidi_esclusi]

    heap = []
    heapq.heappush(heap, (0, [wp_start], []))

    while heap:
        current_cost, path, edges = heapq.heappop(heap)
        current_wp = path[-1]

        if current_wp.point == wp_end.point:
            return Route(edges)

        direct_edge = Edge(current_wp, wp_end)
        intersezioni = []
        for solido in solidi_validi:
            interseca, punto = solido.interseca_segmento(direct_edge._segment)
            if interseca:
                intersezioni.append( (solido, punto) )

        if not intersezioni:
            new_edges = edges + [direct_edge]
            return Route(new_edges)

        for solido, punto in intersezioni:
            nuovo_z = None
            if solido.z_max < altitude_max:
                nuovo_z = altitude_max
            elif solido.z_min > altitude_min:
                nuovo_z = altitude_min

            if nuovo_z is not None:
                nuovo_punto = Point3D(punto.x, punto.y, nuovo_z)
                nuovo_wp = Waypoint(nuovo_punto)
                new_edge = Edge(current_wp, nuovo_wp)
                heapq.heappush(heap, (current_cost + new_edge.length, path + [nuovo_wp], edges + [new_edge]))
            else:
                nuovo_wp = Waypoint(punto)
                new_edge = Edge(current_wp, nuovo_wp)
                heapq.heappush(heap, (current_cost + new_edge.length, path + [nuovo_wp], edges + [new_edge]))

    return Route([])

class Mappa:
    def __init__(self):
        self.solidi = []

    def aggiungi_parallelepipedo(self, base_center, side_length, base_z, height):
        self.solidi.append(SolidoParallelepipedo(base_center, side_length, base_z, height))

    def aggiungi_parallelepipedi(self, lista):
        for params in lista:
            self.aggiungi_parallelepipedo(*params)

    #def riconosci_composti(self):
        #self.solidi = riconosci_composti(self.solidi)