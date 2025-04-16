import sys
import os
import heapq
import math
import copy
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Code.Dynamic_War_Manager.Cylinder import Cylinder
from Code.Utility import getFormattedPoint



MIN_LENGTH_SEGMENT = 0.1 # minimum length of segment to consider it as valid intersection

class ThreatAA:
    
    def __init__(self, danger_level, missile_speed: float, min_fire_time: float, cylinder: Cylinder):
        self.danger_level = danger_level
        self.missile_speed = missile_speed
        self.min_fire_time = min_fire_time
        self.min_altitude = cylinder.bottom_center.z
        self.max_altitude = cylinder.bottom_center.z + cylinder.height
        self.cylinder = cylinder

    def edgeIntersect(self, edge) -> Tuple[bool, Optional[Segment3D]]:
        segment = Segment3D(edge.wpA.point, edge.wpB.point)
        #intersected, intersection = self.cylinder.getIntersection(segment, tolerance = MIN_LENGTH_SEGMENT)        
        return self.cylinder.getIntersection(segment, tolerance = MIN_LENGTH_SEGMENT)
    
    def innerPoint(self, point:Point3D):
            
        if self.cylinder.innerPoint(point):
            return True
        return False

    def calcMaxLenghtCrossSegment(self, aircraft_speed: float, aircraft_altitude: float, time_to_inversion: float, segment: Segment3D) -> float:
    
        a = 1 / aircraft_speed 
        b = 0.5 / self.missile_speed 
        c = -(self.cylinder.radius + aircraft_altitude * aircraft_altitude) / aircraft_speed
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
        

        time_max_in_threat_zone = lm * self.missile_speed
        max_segmanet_lenght_in_threat_zone = ( time_max_in_threat_zone + time_to_inversion +self.min_fire_time) * aircraft_speed


        return max_segmanet_lenght_in_threat_zone
     

class Waypoint:
    
    def __init__(self, name: str, point: Point3D, id: str|None):
        self.id = id
        self.name = name
        self.point = point
        self.point2d = Point2D(point.x, point.y)

        if not id:
            self.id = name
    
    def to_dict(self) -> Dict:
        """Converte il waypoint in un dizionario per serializzazione."""
        return {
            'name': self.name,
            'point': (self.point.x, self.point.y, self.point.z),
            'id': self.id
        }

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

    def getSegment3D(self):
        return Segment3D(self.wpA.point, self.wpB.point)
    
   

    def calculate_danger(self, threats: List[ThreatAA]) -> float:
        danger = 0.0
        for threat in threats:
            result, intersections = self.intersects_threat(threat)

            if result:                                                    
                exposure_length = (intersections[1] - intersections[0]) * self.length
                exposure_time = exposure_length / self.speed
                danger += threat.danger_level * exposure_time
                
        return danger
        
    
    def intersects_threat(self, threat: ThreatAA) -> Tuple[bool, Optional[List[float]]]:        

        if (threat.innerPoint(self.wpA.point) or threat.innerPoint(self.wpB.point)):
            return True, None
        
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
            return False, None
        
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
    
    def calculate_exposure(self, threat: ThreatAA) -> Tuple[float, float]:
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

    def to_dict(self) -> Dict:
        """Converte l'edge in un dizionario per serializzazione."""
        return {
            'name': self.name,
            'wpA': self.wpA.to_dict(),
            'wpB': self.wpB.to_dict(),
            'length': self.length,
            'danger': self.danger
        }
    
    
class Route:

    def __init__(self, name):
        self.name = name
        self.edges = {}
    
    def add_edge(self, edge: Edge):
        self.edges[(edge.wpA, edge.wpB)] = edge
    
    def getWaypoints(self):
        # Calcola self.start come il primo waypoint che non è un punto di arrivo
        all_start_points = {a for a, b in self.edges.keys()}
        all_end_points = {b for a, b in self.edges.keys()}
        self.start = next(iter(all_start_points - all_end_points), None)

        if not self.start:
            raise ValueError("Impossibile determinare il punto di partenza (self.start).")

        path = []
        current = self.start

        while True:
            path.append(current)
            next_edges = [e for (a, b), e in self.edges.items() if a == current]

            if not next_edges:
                break
            current = next_edges[0].wpB

        return path

    def getPoints(self):
        waypoints = self.getWaypoints()
        points = [wp.point for wp in waypoints]
        return points   

# ottimizzazione deepseek
@dataclass
class Path:
    """Rappresenta un singolo percorso composto da una sequenza di edge."""
    edges: List['Edge']
    completed: bool = False
    
    def __post_init__(self):
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calcola le metriche aggregate del percorso."""
        self.total_length = sum(edge.length for edge in self.edges)
        self.total_danger = sum(edge.danger for edge in self.edges)
        self.waypoints = self._get_waypoints()
    
    def _get_waypoints(self) -> List[Waypoint]:
        """Restituisce la sequenza ordinata di waypoint del percorso."""
        if not self.edges:
            return []
            
        waypoints = [self.edges[0].wpA]
        for edge in self.edges:
            waypoints.append(edge.wpB)
        return waypoints
    
    def add_edge(self, edge: 'Edge'):
        """Aggiunge un edge al percorso e aggiorna le metriche."""
        self.edges.append(edge)
        self._calculate_metrics()
    
    def to_dict(self) -> Dict:
        """Converte il percorso in un dizionario per serializzazione."""
        return {
            'edges': [edge.to_dict() for edge in self.edges],
            'total_length': self.total_length,
            'total_danger': self.total_danger,
            'completed': self.completed
        }
    def to_route(self) -> Route:
        """Converte il percorso in un oggetto Route."""
        route = Route("Route")

        for edge in self.edges:
            route.add_edge(edge)
        return route

class PathCollection:
    """Collezione di percorsi alternativi con metodi di utilità."""
    def __init__(self):
        self.paths: List[Path] = []
        self._active_path_indices = set()
    
    def add_path(self, initial_edges: Optional[List['Edge']] = None) -> int:
        """
        Aggiunge un nuovo percorso alla collezione.
        Restituisce l'ID del percorso creato.
        """
        path_id = len(self.paths)
        new_path = Path(initial_edges or [])
        self.paths.append(new_path)
        self._active_path_indices.add(path_id)
        return path_id
    
    def get_path(self, path_id: int) -> Path:
        """Restituisce il percorso con l'ID specificato."""
        if path_id < 0 or path_id >= len(self.paths):
            raise IndexError(f"Invalid path ID: {path_id}")
        return self.paths[path_id]
    
    def mark_path_completed(self, path_id: int):
        """Segna un percorso come completato con successo."""
        if path_id in self._active_path_indices:
            self._active_path_indices.remove(path_id)
            self.paths[path_id].completed = True
    
    def get_active_paths(self) -> List[Path]:
        """Restituisce una lista dei percorsi ancora attivi."""
        return [self.paths[i] for i in sorted(self._active_path_indices)]
    
    def get_best_path(self, max_range: float) -> Optional[Path]:
        """Restituisce il percorso migliore basato su pericolo e lunghezza escludendo i percorsi che superano come lunghezza il max_range."""
        if not self.paths:
            return None
            
        # Filtra solo i percorsi completati
        completed_paths = [p for p in self.paths if p.completed]

        for path in completed_paths:
            if path.total_length > max_range:
                completed_paths.remove(path)

        if not completed_paths:
            return None
            
        # Trova il percorso con il miglior compromesso pericolo-lunghezza
        return min(completed_paths, key=lambda p: (p.total_danger, p.total_length))
    
    def to_dict(self) -> Dict:
        """Converte l'intera collezione in un dizionario."""
        return {
            'paths': [path.to_dict() for path in self.paths],
            'active_paths': list(sorted(self._active_path_indices))
        }



class RoutePlanner:

    def __init__(self, start, end, threats):
        self.start = start
        self.end = end
        self.threats = threats
        
        
    def calcRoute(self, start: Point3D, end: Point3D, threats: list[ThreatAA], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, aircraft_time_to_inversion: float, change_alt_option: str = "no_change", intersecate_threat: bool = False) -> Route:      

        # change_alt_option: str = "no_change", "change_down", "change_up"
        # ricorda in threats devono essere escluse le threat che includono i 
                          
        found_path = False
        

        # Inizializzazione
        path_collection = PathCollection()
        initial_path_id = path_collection.add_path()

        # esclusione dal calcolo delle threats che includono l'inizio e la fine del percorso
        self.excludeThreat(threats, start)
        self.excludeThreat(threats, end)


        if intersecate_threat:            
            found_path = self.calcPathWithThreat(
                start, 
                end, 
                end,
                threats,
                n_edge = 0,                
                path_id = initial_path_id,
                path_collection = path_collection,
                aircraft_altitude_min = aircraft_altitude_min,
                aircraft_altitude_max = aircraft_altitude_max,
                aircraft_speed_max = aircraft_speed_max,
                aircraft_speed = aircraft_speed,
                aircraft_range_max = aircraft_range_max,
                time_to_inversion = aircraft_time_to_inversion,
                change_alt_option = change_alt_option,
                debug = True
            )


        else: # Calcola il percorso senza minacce (path_collectiopn è passato come riferimento e dovrebbe essere aggiornato dal metodo)
            found_path = self.calcPathWithoutThreat(
                start, 
                end, 
                end,
                threats,
                n_edge = 0,            
                path_id = initial_path_id,
                path_collection = path_collection,
                aircraft_altitude_min = aircraft_altitude_min,
                aircraft_altitude_max = aircraft_altitude_max,
                aircraft_speed_max = aircraft_speed_max,
                aircraft_speed = aircraft_speed,
                aircraft_range_max = aircraft_range_max,
                change_alt_option = change_alt_option,
                debug = True
            )

            if not found_path:    
                # Inizializzazione
                path_collection = PathCollection()
                initial_path_id = path_collection.add_path()

                # Se non ci sono percorsi senza minacce, calcola il percorso con le minacce (path è passato come riferimento e dovrebbe essere aggiornato dal metodo)                
                found_path = self.calcPathWithThreat(
                    start, 
                    end, 
                    end,
                    threats,
                    n_edge = 0,                
                    path_id = initial_path_id,
                    path_collection = path_collection,
                    aircraft_altitude_min = aircraft_altitude_min,
                    aircraft_altitude_max = aircraft_altitude_max,
                    aircraft_speed_max = aircraft_speed_max,
                    aircraft_speed = aircraft_speed,
                    aircraft_range_max = aircraft_range_max,
                    time_to_inversion = aircraft_time_to_inversion,
                    change_alt_option = change_alt_option,
                    debug = True
                )

        # nella funzione best path oltre che valutare la lunghezza devi valutare anche il pericolo: 0.7 * danger + 0.3 * length
        # Ottenere risultati
        if found_path:

            for id_path in range(len(path_collection.paths)):
                _path = path_collection.get_path(id_path)
                print(f"Found path --> Path ID: {id_path}, Length: {_path.total_length:.2f}, Danger: {_path.total_danger:.2f}")

                for edge in _path.edges:
                    print(f"Edge {edge.name} from {getFormattedPoint(edge.wpA.point)} to {getFormattedPoint(edge.wpB.point)}")

            best_path = path_collection.get_best_path(aircraft_range_max)       

            print(f"Best path length: {best_path.total_length:.2f}, danger: {best_path.total_danger:.2f}")

            for edge in best_path.edges:
                print(f"Edge from {getFormattedPoint(edge.wpA.point)} to {getFormattedPoint(edge.wpB.point)}")
                
            return best_path.to_route()
        
        return None

    def excludeThreat(self, threats: list[ThreatAA], point: Point3D):
        
        for threat in threats:
            
            if threat.innerPoint(point):
                threats.remove(threat)
                
        return True 


    def firstThreatIntersected(self, edge: Edge, threats: list[ThreatAA]) -> ThreatAA:
        DEBUG = True
        threat_distance = float('inf') # distanza da edge.wpa a threat.center
        first_threat = None
    

        for threat in threats:
            threatInrange, intersection = threat.edgeIntersect(edge)
            
            if threatInrange:                
                wpA_Intersection_distance = edge.wpA.point.distance(intersection.p1) # distanza dalla circonferenza della threat
                
                if wpA_Intersection_distance < threat_distance:
                    threat_distance = wpA_Intersection_distance
                    first_threat = threat                    
                    if DEBUG: print(f"Found threat intersection at lesser distance: threat: {threat}, threat_distance: {threat_distance:.2f}")        

        return first_threat

    # ottimizzazione deepseek

    def calcPathWithoutThreat(
        self,
        p1: Point3D,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,        
        path_id: int,
        path_collection: PathCollection,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        change_alt_option: str,
        max_recursion: int = 100,
        debug: bool = False
    ) -> bool:
        """
        Calcola un percorso evitando minacce usando una strategia ricorsiva.
        
        Args:
            p1: Punto di partenza corrente
            p2: Punto di arrivo corrente
            end: Punto finale del percorso
            threats: Lista di minacce da evitare
            n_edge: Contatore di edge nel percorso corrente
            path_collection: Collezione di tutti i percorsi
            path_id: ID del percorso corrente
            aircraft_*: Parametri delle prestazioni dell'aereo
            change_alt_option: Strategia per il cambio di quota
            max_recursion: Limite di sicurezza per la ricorsione
            debug: Flag per abilitare i log di debug
            
        Returns:
            True se è stato trovato almeno un percorso valido, False altrimenti
        """
        if max_recursion <= 0:
            if debug:
                print(f"Max recursion depth reached for path {path_id}")
            return False

        current_path = path_collection.get_path(path_id)
        wp_A = Waypoint(f"wp_A{path_id}_{n_edge}", p1, None)
        wp_B = Waypoint(f"wp_B{path_id}_{n_edge}", p2, None)
        edge = Edge(f"P:{path_id}-E:{n_edge}", wp_A, wp_B, aircraft_speed)

        if debug:
            print(f"\nProcessing path {path_id}, edge {n_edge}: {wp_A.name}({getFormattedPoint(wp_A.point)}) -> {wp_B.name}({getFormattedPoint(wp_B.point)})")

        # Verifica intersezioni con minacce
        threat_intersect = self.firstThreatIntersected(edge, threats)

        if not threat_intersect:
            current_path.add_edge(edge)
            if debug:
                print(f"No threats found. Added edge to path {path_id}")

            if p2 == end:
                path_collection.mark_path_completed(path_id)
                if debug:
                    print(f"Path {path_id} completed successfully!")
                return True

            return self.calcPathWithoutThreat(
                p2, end, end, threats, n_edge + 1, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max,
                change_alt_option, max_recursion - 1, debug
            )

        # Gestione alternativa (cambio quota o percorso alternativo)
        return self._handle_threat_avoidance(
            edge, threat_intersect, p1, p2, end, threats, n_edge,
            path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, None,
            change_alt_option, max_recursion - 1, "calcPathWithoutThreat", debug
        )        

    def calcPathWithThreat(
        self,
        p1: Point3D,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,
        path_id: int,
        path_collection: PathCollection,        
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        max_recursion: int = 100,
        debug: bool = False
    ) -> bool:
        """
        Calcola un percorso considerando l'attraversamento controllato delle minacce.
        
        Args:
            p1: Punto di partenza corrente
            p2: Punto di arrivo corrente
            end: Punto finale del percorso
            threats: Lista di minacce da valutare
            n_edge: Contatore di edge nel percorso corrente
            path_collection: Collezione di tutti i percorsi
            path_id: ID del percorso corrente
            aircraft_*: Parametri delle prestazioni dell'aereo
            change_alt_option: Strategia per il cambio di quota
            max_recursion: Limite di sicurezza per la ricorsione
            debug: Flag per abilitare i log di debug
            
        Returns:
            True se è stato trovato almeno un percorso valido, False altrimenti
        """
        if max_recursion <= 0:
            if debug:
                print(f"Max recursion depth reached for path {path_id}")
            return False

        current_path = path_collection.get_path(path_id)
        wp_A = Waypoint(f"wp_A{path_id}_{n_edge}", p1, None)
        wp_B = Waypoint(f"wp_B{path_id}_{n_edge}", p2, None)
        edge = Edge(f"P:{path_id}-E:{n_edge}", wp_A, wp_B, aircraft_speed)

        if debug:
            print(f"\nProcessing path {path_id}, edge {n_edge}: {wp_A.name} -> {wp_B.name}")

        # Verifica intersezioni con minacce
        threat_intersect = self.firstThreatIntersected(edge, threats)

        if not threat_intersect:
            current_path.add_edge(edge)
            if debug:
                print(f"No threats found. Added edge to path {path_id}")

            if p2 == end:
                path_collection.mark_path_completed(path_id)
                if debug:
                    print(f"Path {path_id} completed successfully!")
                return True

            return self.calcPathWithThreat(
                p2, end, end, threats, n_edge + 1, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion - 1, debug
            )

        # Calcola la massima lunghezza di attraversamento sicuro
        max_length = threat_intersect.calcMaxLenghtCrossSegment(
            aircraft_speed,
            aircraft_altitude_max,            
            time_to_inversion,
            threat_intersect.min_fire_time,
            edge.getSegment3D()
        )

        # Verifica se possiamo attraversare la minaccia in sicurezza
        if max_length > MIN_LENGTH_SEGMENT:
            return self._handle_threat_crossing(
                edge, threat_intersect, p2, end, threats, n_edge,
                path_id, path_collection, max_length,
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max,
                change_alt_option, max_recursion - 1, debug
            )

        # Gestione alternativa (cambio quota o percorso alternativo)
        return self._handle_threat_avoidance(
            edge, threat_intersect, p1, p2, end, threats, n_edge,
            path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
            change_alt_option, max_recursion - 1, "calcPathWithThreat", debug
        )

    def _handle_threat_crossing(
        self,
        edge: Edge,
        threat: ThreatAA,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,
        path_id: int,
        path_collection: PathCollection,        
        max_length: float,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        change_alt_option: str,
        max_recursion: int,
        debug: bool
    ) -> bool:
        """Gestisce l'attraversamento sicuro di una minaccia."""
        if debug:
            print(f"Attempting to cross threat at {threat.cylinder.center} with max length {max_length: .2f}")

        # Trova i punti di attraversamento ottimali
        c, d = threat.cylinder.find_chord_coordinates(
            threat.cylinder.radius,
            threat.cylinder.center,
            edge.wpA.point2d(),
            edge.wpB.point2d(),
            max_length
        )

        # Crea i waypoint di attraversamento
        wp_c = Waypoint(f"wp_{path_id}_{n_edge}_cross1", Point3D(c.x, c.y, edge.wpA.point.z), None)
        wp_d = Waypoint(f"wp_{path_id}_{n_edge}_cross2", Point3D(d.x, d.y, edge.wpA.point.z), None)

        # Edge fino al punto di ingresso
        edge_to_c = Edge(
            f"P:{path_id}-E:{n_edge}_pre",
            edge.wpA,
            wp_c,
            edge.speed
        )
        path_collection.get_path(path_id).add_edge(edge_to_c)

        # Edge attraverso la minaccia
        edge_through = Edge(
            f"P:{path_id}-E:{n_edge}_through",
            wp_c,
            wp_d,
            edge.speed
        )
        path_collection.get_path(path_id).add_edge(edge_through)

        # Prosegui dal punto di uscita
        return self.calcPathWithThreat(
            Point3D(d.x, d.y, edge.wpA.point.z),  # Punto d
            p2, end, threats, n_edge + 1, path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max,
            change_alt_option, max_recursion, debug
        )

    def _handle_threat_avoidance(
        self,
        edge: Edge,
        threat: ThreatAA,
        p1: Point3D,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,        
        path_id: int,
        path_collection: PathCollection,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float, 
        change_alt_option: str,
        max_recursion: int,
        caller: str,
        debug: bool
    ) -> bool:
        """Gestisce l'evitamento della minaccia con cambio quota o percorsi alternativi."""
        # Verifica se possiamo cambiare quota
        can_change_altitude = (
            (aircraft_altitude_max > threat.max_altitude * 1.01 or 
            aircraft_altitude_min < threat.min_altitude * 0.99 ) and
            change_alt_option != "no_change"
        )

        if can_change_altitude:
            if debug:
                print(f"Attempting altitude change for threat at {threat.cylinder.bottom_center}")

            intersected, segm = threat.cylinder.getIntersection(
                edge.getSegment3D(), tolerance = MIN_LENGTH_SEGMENT
            )
            
            if not intersected:
                if debug:
                    print("Unexpected: no intersection found where threat was detected")
                return False

            new_p1 = segm.p1
            if change_alt_option == "change_up":
                new_p1 = Point3D(new_p1.x, new_p1.y, threat.max_altitude * 1.01)
                if debug:
                    print(f"Changing altitude UP to {new_p1.z:.2f}")
            else:
                new_p1 = Point3D(new_p1.x, new_p1.y, threat.min_altitude * 0.99)
                if debug:
                    print(f"Changing altitude DOWN to {new_p1.z:.2f}")

            # Crea nuovo edge con punto modificato
            new_wp_B = Waypoint(f"wp_B{path_id}_{n_edge}_alt", new_p1, None) 
            new_edge = Edge(
                f"P:{path_id}-E:{n_edge}_alt", 
                edge.wpA, 
                new_wp_B, 
                aircraft_speed
            )
            path_collection.get_path(path_id).add_edge(new_edge)

            if caller == "calcPathWithThreat":
                
                return self.calcPathWithThreat(
                    new_p1, p2, end, threats, n_edge + 1, path_id, path_collection, 
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion, 
                    change_alt_option, max_recursion-1, debug
                )
            elif caller == "calcPathWithoutThreat":

                return self.calcPathWithoutThreat(
                    new_p1, p2, end, threats, n_edge + 1, path_id, path_collection, 
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max,
                    change_alt_option, max_recursion-1, debug
                )
            else:
                raise ValueError(f"Unexpected caller: {caller}. Expected 'calcPathWithThreat' or 'calcPathWithoutThreat'.")

        # Se non possiamo cambiare quota, troviamo percorsi alternativi calcolando gli extended points per una circonferenza leggermente più grande della threat
        extended_cylinder = Cylinder(threat.cylinder.center, threat.cylinder.radius * 1.03, threat.cylinder.height)
        ext_p1, ext_p2 = extended_cylinder.getExtendedPoints(
            edge.getSegment3D(), tolerance=0.001
        )
        
        if not ext_p1 or not ext_p2:
            if debug:
                print("Could not find extended points around threat")
            return False

       

        path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
        new_path_id = path_collection.add_path(path_edges_copy) 

        if debug:
            print(f"Creating alternative path through new point (ext_p1): {getFormattedPoint(ext_p1)}")#, \nProcessing path {path_id}, new edge {new_edge1}: {new_edge1.wpA.name}({getFormattedPoint(new_edge1.wpA.point)}) -> {new_edge1.wpB.name}({getFormattedPoint(new_edge1.wpB.point)})")

        if caller == "calcPathWithThreat":
                
            result1 = self.calcPathWithThreat(
                p1, ext_p1, end, threats, n_edge, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion, debug
            )
        elif caller == "calcPathWithoutThreat":

            result1 = self.calcPathWithoutThreat(
                p1, ext_p1, end, threats, n_edge, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max,
                change_alt_option, max_recursion, debug
            )
        else:
            raise ValueError(f"Unexpected caller: {caller}. Expected 'calcPathWithThreat' or 'calcPathWithoutThreat'.")


        # Percorso alternativo 2 (ext_p2)    
        
        #new_edge2 = Edge(
        #    f"P:{new_path_id}-E:{n_edge}_alt2",
        #    edge.wpA,
        #    Waypoint(f"wp_B{new_path_id}_{n_edge}_alt2", ext_p2, None),
        #    aircraft_speed
        #)
        #path_collection.get_path(new_path_id).add_edge(new_edge2)

        if debug:
            print(f"Creating alternative path through new point (ext_p2): {getFormattedPoint(ext_p2)}") #, \nProcessing path {new_path_id}, new edge {new_edge2}: {new_edge2.wpA.name}({getFormattedPoint(new_edge2.wpA.point)}) -> {new_edge2.wpB.name}({getFormattedPoint(new_edge2.wpB.point)})")

        if caller == "calcPathWithThreat":
                
            result2 = self.calcPathWithThreat(
                p1, ext_p2, end, threats, n_edge, new_path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion, debug
            )
        elif caller == "calcPathWithoutThreat":

            result2 = self.calcPathWithoutThreat(
                p1, ext_p2, end, threats, n_edge, new_path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max,
                change_alt_option, max_recursion, debug
            )
        else:
            raise ValueError(f"Unexpected caller: {caller}. Expected 'calcPathWithThreat' or 'calcPathWithoutThreat'.")

        return result1 or result2

        

    #deprecated ?    
    def OLDcalcPathWithoutThreat(self, p1: Point3D, p2: Point3D, end: Point3D, threats: list[ThreatAA], n_edge: int, n_path: int, path: list[Route], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, change_alt_option: str) -> bool:  
        DEBUG = False
        wp_A = Waypoint(f"wp_A{n_edge}", p1, None)
        wp_B = Waypoint(f"wp_B{n_edge}", p2, None)
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
        
        elif ( aircraft_altitude_max > threat_intersect.max_altitude or aircraft_altitude_min < threat_intersect.min_altitude ) and change_alt_option != "no_change": # l'aereo può passare sopra o sotto la minaccia
            intersected, segm = threat_intersect.cylinder.getIntersection(edge.getSegmet3D(), tolerance = MIN_LENGTH_SEGMENT) # determina il segmento di intersezione dell'edge con la minaccia
            
            if not intersected:
                raise Exception(f"Unexpected value intersected is {intersected} but must be True - threat_intersect: {threat_intersect}, n_path: {n_path}, n_edge: {n_edge}")
            
            new_p1 = segm[0].point # crea un nuovo punto considerando il punto d'intersezione del cilindro 

            if change_alt_option == "change_up":
                new_p1.z = threat_intersect.max_altitude + 1 # imposta la coordinata z del nuovo punto con l'altezza massima della della minaccia +1            
            
            elif change_alt_option == "change_down":
                new_p1.z = threat_intersect.min_altitude - 1 # imposta la coordinata z del nuovo punto con l'altezza minima della della minaccia - 1            
            
            else:
                raise ValueError(f"Unexpected value of change_alt_option: {change_alt_option}. change_alt_option must be: /'no_change'', /'change_up' or /'change_down'")
                        
            wp_B = Waypoint(f"wp_B{n_edge}", new_p1, None ) # crea un nuovo waypoint B con il nuovo punto
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
            wp_B = Waypoint(f"wp_B{n_edge}", ext_p1, None ) # crea un nuovo waypoint B con il nuovo punto ext_p1
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)

            if DEBUG: print(f"l'aereo non può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}). Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")

            # ricalcola il percorso per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithoutThreat(p1, ext_p1, end, threats, n_edge, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)
            
            # valutazione secondo path con ext_p1 (costituisce un nuovo path)
            wp_B = Waypoint(f"wp_B{n_edge}", ext_p2, None ) # crea un nuovo waypoint B con il nuovo punto ext_p2
            edge = Edge(f"P:{n_path + 1}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)

            if DEBUG: print(f"  - Calcolo nuovo percorso: Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path({n_path + 1}): {path}")

            # ricalcola il percorso aggiungendo un nuovo path, per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithoutThreat(p1, ext_p2, end, threats, n_edge, n_path + 1, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)
    #deprecated ?
    def OLDcalcPathWithThreat(self, p1: Point3D, p2: Point3D, end: Point3D, threats: list[ThreatAA], n_edge: int, n_path: int, path: list[Route], aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, time_to_inversion: float, change_alt_option: str) -> bool:
        DEBUG = False
        wp_A = Waypoint(f"wp_A{n_edge}", p1, None)
        wp_B = Waypoint(f"wp_B{n_edge}", p2, None)
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
        
        elif ( aircraft_altitude_max > threat_intersect.max_altitude or aircraft_altitude_min < threat_intersect.min_altitude ) and change_alt_option != "no_change": # l'aereo può passare sopra o sotto la minaccia
            intersected, segm = threat_intersect.cylinder.getIntersection(edge.getSegment3D(), tolerance = MIN_LENGTH_SEGMENT) # determina il segmento di intersezione dell'edge con la minaccia
            
            if not intersected:
                raise Exception(f"Unexpected value intersected is {intersected} but must be True - threat_intersect: {threat_intersect}, n_path: {n_path}, n_edge: {n_edge}")
            
            new_p1 = segm[0].point # crea un nuovo punto considerando il punto d'intersezione del cilindro 

            if change_alt_option == "change_up":
                new_p1.z = threat_intersect.max_altitude + 1 # imposta la coordinata z del nuovo punto con l'altezza massima della della minaccia +1            
            
            elif change_alt_option == "change_down":
                new_p1.z = threat_intersect.min_altitude - 1 # imposta la coordinata z del nuovo punto con l'altezza minima della della minaccia - 1            
            
            else:
                raise ValueError(f"Unexpected value of change_alt_option: {change_alt_option}. change_alt_option must be: /'no_change'', /'change_up' or /'change_down'")
                        
            wp_B = Waypoint(f"wp_B{n_edge}", new_p1, None ) # crea un nuovo waypoint B con il nuovo punto
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            
            if DEBUG: print(f"l'aereo può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}) Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")
            
            # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
            self.calcPathWithThreat(new_p1, p2, end, threats, n_edge + 1, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)


        else: # l'aereo non può passare sotto o sopra la minaccia        

            # determina i due punti esterni alla minaccia. NOTA: la tolleranza di 0.001 è solo se i test di unità li imposti con mappe limitate da 0 a 10.
            max_lenght = threat_intersect.calcMaxLenghtCrossSegment(aircraft_speed, aircraft_altitude_max, time_to_inversion, edge.getSegment3D()) # calcola la lunghezza massima del segmento che può attraversare la minaccia    
            valid_intersection, segment = threat_intersect.cylinder.getIntersection(edge.getSegment3D(), tolerance = max_lenght) # determina il segmento di intersezione dell'edge con la minaccia            

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
                    I, D1, D2 = threat_intersect.cylinder.find_chord_endpoint(threat_intersect.cylinder.radius, threat_intersect.cylinder.center, edge.wpA.point2d(), edge.wpB.point2d(), max_lenght) # calcola i punti C e D della corda CD che è la più vicina possibile alla corda AB sulla circonferenza                    
                    intersection = segment[0].point
                    if (I - intersection).length() > le-1:# I e intersection devono essere coincidenti
                        raise Exception(f"Incongruent intersection calculus from find_chord_endpoint: intersection({I}) and threat_intersect.cylinder.getIntersection: intersection({intersection}) - segment: {segment}, path: {n_path}: {path}")
                    wp_B = Waypoint(f"wp_B{n_edge}", intersection, None ) # crea un nuovo waypoint B con il nuovo punto
                    edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
                    path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso attuale
                    path[str(n_path + 1)].append(edge) # l'edge viene anche aggiunto al nuovo percorso

                    # calcolo secondo edge basato sulla prima corda di lunghezza = max_lenght
                    wp_A = Waypoint(f"wp_A{n_edge}", intersection, None ) # crea un nuovo waypoint A con il punto d'intersezione
                    wp_B = Waypoint(f"wp_B{n_edge}", D1, None ) # crea un nuovo waypoint B con l'estremo D della prima corda di lunghezza = max_lenght
                    edge = Edge(f"P:{n_path}-E:{n_edge + 1}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
                    path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
                    # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
                    self.calcPathWithThreat(D1, end, end, threats, n_edge + 2, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

                    # calcolo secondo edge per nuovo path basato sulla seconda corda di lunghezza = max_lenght
                    wp_B = Waypoint(f"wp_B{n_edge}", D2, None ) # crea un nuovo waypoint B con l'estremo D della prima corda di lunghezza = max_lenght
                    edge = Edge(f"P:{n_path}-E:{n_edge + 1 }", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
                    path[str(n_path + 1)].append(edge) # l'edge viene aggiunto al percorso
                    # chiama ricorsivemente lil metodo per proseguire il calcolo del percorso dal nuovo punto al punto p2
                    self.calcPathWithThreat(D2,end, end, threats, n_edge + 2, n_path + 1, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

            #edge attraversa la threat definendo un segmento di intersezione        
            c, d = threat_intersect.cylinder.find_chord_coordinates(threat_intersect.cylinder.radius, threat_intersect.cylinder.center, edge.wpA.point2d(), edge.wpB.point2d(), max_lenght) # calcola i punti C e D della corda CD che è la più vicina possibile alla corda AB sulla circonferenza                        
            wp_B = Waypoint( f"wp_B{n_edge}", c, None ) # crea un nuovo waypoint B con il nuovo punto c
            edge = Edge(f"P:{n_path}-E:{n_edge}", wp_A, wp_B, speed = aircraft_speed) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)            
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso
            
            if DEBUG: print(f"l'aereo non può passare sopra o sotto la minaccia: aircraft_altitude max, min ({aircraft_altitude_max, aircraft_altitude_min}), threat max, min altitude ({threat_intersect.max_altitude, threat_intersect.min_altitude}). Aggiornamento wp_B: {wp_B}, edge: {edge} e inserimento nel path: {path}")

            wp_A = Waypoint( f"wp_B{n_edge}", c, None ) # crea un nuovo waypoint A con il nuovo punto c
            wp_B = Waypoint( f"wp_B{n_edge}", d, None ) # crea un nuovo waypoint B con il nuovo punto ext_d            
            edge = Edge( f"P:{n_path}-E:{n_edge + 1}", wp_A, wp_B, speed = aircraft_speed ) # aggiorna il l'edge con il waypoint precedente (wp_A) ed il nuovo waypoint (wp_B)
            path[str(n_path)].append(edge) # l'edge viene aggiunto al percorso

            if DEBUG: print(f"  - Calcolo aggiornamento percorso base: wp_A: {wp_A}, wp_B: {wp_B}, edge: {edge} inserito nel path: {n_path}: {path}")

            # ricalcola il percorso aggiungendo un nuovo path, per considerare che l'edge aggiornato potrebbe comunque intersecare una minaccia diversa
            self.calcPathWithThreat(d, end, end, threats, n_edge + 2, n_path, path, aircraft_altitude_min, aircraft_altitude_max, aircraft_speed_max, aircraft_speed, aircraft_range_max, change_alt_option)

        return False


