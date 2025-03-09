"""
Module Route_Manager

Class and methds for managing the route of the vehicles, helicopters and aircraft in the simulation
"""

from heapq import heappop, heappush

class Waypoint:
    def __init__(self, name, x, y, z, state='inactive'):
        self.name = name
        self.x = x
        self.y = y
        self.z = z # Altitude
        self.state = state  # Es: 'active', 'blocked', 'inactive'
        
    def __repr__(self):
        return f"Waypoint({self.name}, ({self.x}, {self.y}, {self.z}), {self.state})"

class Edge:
    def __init__(self, start, end, danger_level, path_type, slope, max_speed):
        self.start = start
        self.end = end
        self.danger_level = danger_level
        self.path_type = path_type # 'onroad', 'offroad', 'air'
        self.slope = slope # percentuale
        self.max_speed = max_speed
        self.distance = self._calculate_distance()

    def _calculate_distance(self):
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        dz = self.end.z - self.start.z
        
        # Calcolo distanza euclidea standard
        base_distance = (dx**2 + dy**2 + dz**2) ** 0.5
        
        if self.path_type == 'onroad':
            max_slope = 10  # Pendenza massima consentita per le strade (10%)
            
            # Calcolo componente orizzontale e pendenza effettiva
            horizontal = (dx**2 + dy**2) ** 0.5
            if horizontal == 0:
                return float('inf')  # Evita divisione per zero
            
            actual_slope = (abs(dz) / horizontal) * 100  # Pendenza percentuale

            # Se la pendenza supera il massimo consentito
            if actual_slope > max_slope:
                # Calcola la nuova lunghezza orizzontale necessaria
                required_horizontal = (abs(dz) * 100) / max_slope
                
                # Calcola la nuova distanza 3D complessiva
                new_distance = (required_horizontal**2 + dz**2) ** 0.5
                return new_distance
        
        return base_distance
    
    def __repr__(self):
        return f"Edge({self.start.name} -> {self.end.name}, Dist: {self.distance:.2f}m, Slope: {self.slope}%)"

class NavigationGraph:
    def __init__(self):
        self.graph = {}  # Dizionario: {Waypoint: [Edge]}
        
    def add_waypoint(self, waypoint):
        if waypoint not in self.graph:
            self.graph[waypoint] = []
            
    def add_edge(self, edge):
        if edge.start not in self.graph or edge.end not in self.graph:
            raise ValueError("Waypoint non presente nel grafo")
        self.graph[edge.start].append(edge)
        
    def get_neighbors(self, waypoint):
        return [edge for edge in self.graph.get(waypoint, []) if edge.end.state != 'blocked']
    
    def find_optimal_path(self, start, end, weight_func=lambda edge: edge.danger_level):
        """
        Algoritmo Dijkstra personalizzabile con funzione di peso
        weight_func: Funzione che riceve un Edge e restituisce il peso
        """
        
        if start.state == 'blocked' or end.state == 'blocked':
            return None
        
        queue = []
        heappush(queue, (0, start, []))
        visited = set()
        costs = {waypoint: float('inf') for waypoint in self.graph}
        costs[start] = 0
        
        while queue:
            current_cost, current_node, path = heappop(queue)
            
            if current_node in visited:
                continue
                
            if current_node == end:
                return path + [current_node]
                
            visited.add(current_node)
            
            for edge in self.get_neighbors(current_node):
                neighbor = edge.end
                new_cost = current_cost + weight_func(edge)
                
                if new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    heappush(queue, (new_cost, neighbor, path + [current_node]))
        
        return None  # Nessun percorso trovato

    def find_min_danger_path(self, start, end):# per aerei ed elicotteri
        return self.find_optimal_path(start, end, lambda e: e.danger_level)
    
    def find_fastest_path(self, start, end):
        return self.find_optimal_path(
            start, end, 
            lambda e: (e.distance / e.max_speed) if e.max_speed > 0 else float('inf')
        )
    
    def find_min_danger_fastest_path(self, start, end, perc_danger = 0.5, perc_time = 0.5):
        return self.find_optimal_path(
            start, end, 
            lambda e: perc_danger * e.danger_level + perc_time * (e.distance / e.max_speed) if e.max_speed > 0 else float('inf')
        )