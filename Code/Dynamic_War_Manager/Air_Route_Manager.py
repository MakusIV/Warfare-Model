import sys
import os
from heapq import heappop, heappush
import math
import copy
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from functools import singledispatch
from Code.Utility import rotate_vector, get_direction_vector

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Code.Dynamic_War_Manager.Cylinder import Cylinder
from Code.Utility import getFormattedPoint

MAX_PATHS = 50
MAX_RECURSION = 50
MAX_EDGES = 50
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE = 1.05 # factor to increment upper limits for altitude route path
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE = 0.95 # factor to decrement lower limits for altitude route path
RADIUS_EXTENSION_THREAT_CIRCONFERENCE = 1.03 # factor to increments radius threat circonference for route path calculus
MIN_SECURE_LENGTH_EDGE = 0.1 # max length of edge in threat zone (per velocizzare il calcolo: tutti i segmenti )
TOLERANCE_FOR_INTERSECTION_CALCULUS = 0.1 # minimum length of segment to consider it as valid intersection ATT questa è necessaria per distinguere un segmento da un punto 

class ThreatAA:
    
    def __init__(self, danger_level, missile_speed: float, min_fire_time: float, min_detection_time: float, cylinder: Cylinder):
        self.danger_level = danger_level
        self.missile_speed = missile_speed
        self.min_fire_time = min_fire_time
        self.min_detection_time = min_detection_time
        self.min_altitude = cylinder.bottom_center.z
        self.max_altitude = cylinder.bottom_center.z + cylinder.height
        self.cylinder = cylinder

    def edgeIntersect(self, edge) -> Tuple[bool, Optional[Segment3D]]:
        segment = Segment3D(edge.wpA.point, edge.wpB.point)        
        return self.cylinder.getIntersection(segment, tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS)
    
    def innerPoint(self, point:Point3D):
            
        if self.cylinder.innerPoint(point):
            return True
        return False

    def calcMaxLenghtCrossSegment(self, aircraft_speed: float, aircraft_altitude: float, time_to_inversion: float) -> float:
    
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
        

        time_max_in_threat_zone = lm / self.missile_speed
        max_segment_lenght_in_threat_zone = ( time_max_in_threat_zone + time_to_inversion + self.min_fire_time) * aircraft_speed


        return max_segment_lenght_in_threat_zone
     
    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"cylinder {self.cylinder!r}, alt:( {self.min_altitude:.2f} - {self.max_altitude:.2f} ), danger: {self.danger_level:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Threat Information:\n"
                f"  cylinder: {self.cylinder!r}\n"
                f"  min alt: {self.min_altitude:.2f}\n"
                f"  max alt: {self.max_altitude:.2f}\n"
                f"  danger: {self.danger_level:.2f}\n"
                f"  missile_speed: {self.missile_speed:.2f}\n"
                f"  min_fire_time: {self.min_fire_time:.2f}\n"
                f"  min_detection_time: {self.min_detection_time:.2f}")
        
    

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

    def __repr__(self):
        """
        Rappresentazione ufficiale dell'oggetto Block.
        Utile per il debugging.
        """
        return (f"name: {self.name!r}, point: {getFormattedPoint(self.point)}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Waypoint info:\n"
                f"  id: {self.id!r}\n"
                f"  name: {self.name!r}\n")                



class Edge:
    
    
    def __init__(self, name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float):
        self.name = name # name = "P: num path - E: num edge "
        self.order_position = order_position
        self.wpA = wpA
        self.wpB = wpB
        self.speed = speed
        self.length = wpA.point.distance(wpB.point)
        self.danger = 0

    def getSegment3D(self):
        return Segment3D(self.wpA.point, self.wpB.point)

    def to_dict(self) -> Dict:
        """Converte l'edge in un dizionario per serializzazione."""
        return {
            'name': self.name,
            'wpA': self.wpA.to_dict(),
            'wpB': self.wpB.to_dict(),
            'length': self.length,
            'danger': self.danger
        }
    
    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"name: {self.name!r}, order position: {self.order_position}, wpA: {self.wpA!r}, wpB: {self.wpB!r}, length: {self.length:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Edge Information:\n"
                f"  name: {self.name!r},\n"
                f"  order position: {self.order_position},\n"
                f"  wpA: {self.wpA!r}\n"
                f"  wpB: {self.wpB!r}\n"
                f"  length: {self.length:.2f}\n"
                f"  speed: {self.speed:.2f}\n"
                f"  danger: {self.danger:.2f}"
                )
    
class Route:

    def __init__(self, name, length: float|None, danger: float|None):
        self.name = name
        self.edges = {}
        self.length = length
        self.danger = danger
    
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

    def getLength(self) -> float:
        length = 0
        
        for edge in self.edges:
            length += edge.length

        return length

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"name: {self.name!r}, edges: {len(self.edges)}, length: {self.length:.2f}, danger: {self.danger:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Route Information:\n"
                f"  name: {self.name!r},\n"
                f"  edges ({len(self.edges)}):\n"                  
                f"  length: {self.length:.2f}\n"                
                f"  danger: {self.danger:.2f}"
                )


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
        route = Route("Route", self.total_length, self.total_danger)

        for edge in self.edges:
            route.add_edge(edge)
        return route

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"( edges: {len(self.edges)}, length: {self.total_length:.2f}, danger: {self.total_danger:.2f},completed: {self.completed} )")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Path Information:\n"                     
                f"  edges: {len(self.edges)},\n,"
                f"  length: {self.total_length:.2f},\n"                
                f"  danger: {self.total_danger:.2f},\n"
                f"  completed: {self.completed}"
                )



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

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"paths: {len(self.paths)}, active_path_indicies: {self._active_path_indices}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Path Information:\n"
                f"  paths: {len(self.paths)},\n"
                f"  active_path_indicies: {self._active_path_indices}\n"                                
                )


class RoutePlanner:

    def __init__(self, start, end, threats):
        self.start = start
        self.end = end
        self.threats = threats
        
        
    def calcRoute(self, start: Point3D, end: Point3D, threats_: list[ThreatAA], aircraft_altitude_route: float, aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, aircraft_time_to_inversion: float, change_alt_option: str = "no_change", intersecate_threat: bool = False, consider_aircraft_altitude_route: bool = True) -> Route:      

        # change_alt_option: str = "no_change", "change_down", "change_up"
        # NOTA: 
        # CONSIDERANDO L'ARCHITETTURA DI QUESTO ALGORITMO CONVIENE CALCOLARE LE ROTTE 
        # ESEGUENDO QUESTA FUNZIONE CONSIDERANDO LA DOPPIA ESECUZIONE CON 
        # change_alt_option = "no_change" E CON change_alt_optiNo = "change_up o down"
        # p.e.: la scelta di cosa eseguire prima eè in base alle caratteristiche della missione:
        # mission low profile (evitare intercettazione): prima esegui calcRoute con l'opzione change_down" e se non trovi un percorso soddisfacente esegui calcRoute con l'altezza cosnisderata e l'opzione "no_change" seconda della convenienza prima esegui 
        
        DEBUG = True
                      
        found_path = False
        threats = copy.deepcopy(threats_) # Copia profonda della lista delle minacce per evitare modifiche indesiderate

        # Inizializzazione
        path_collection = PathCollection()
        initial_path_id = path_collection.add_path()

        # esclusione dal calcolo delle threats che includono l'inizio e la fine del percorso
        self.excludeThreat(threats, start)
        self.excludeThreat(threats, end)

        if consider_aircraft_altitude_route:
            self.excludeThreat(threats, aircraft_altitude_route)

        if intersecate_threat:            
            found_path = self.calcPathWithThreat(
                start, 
                end, 
                end,
                threats,
                n_edge = 0,                
                path_id = initial_path_id,
                path_collection = path_collection,
                aircraft_altitude = aircraft_altitude_route,
                aircraft_altitude_min = aircraft_altitude_min,
                aircraft_altitude_max = aircraft_altitude_max,
                aircraft_speed_max = aircraft_speed_max,
                aircraft_speed = aircraft_speed,
                aircraft_range_max = aircraft_range_max,
                time_to_inversion = aircraft_time_to_inversion,
                change_alt_option = change_alt_option,
                max_recursion = MAX_RECURSION,
                debug = True
            )    

        else: 
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
                time_to_inversion = aircraft_time_to_inversion,
                change_alt_option = change_alt_option,
                max_recursion = MAX_RECURSION,
                debug = True
            )           

        # nella funzione best path oltre che valutare la lunghezza devi valutare anche il pericolo: 0.7 * danger + 0.3 * length
        # Ottenere risultati
        if found_path:

            for id_path in range(len(path_collection.paths)):
                _path = path_collection.get_path(id_path)
                #print(f"\nFound path --> Path ID: {id_path}, Length: {_path.total_length:.2f}, Danger: {_path.total_danger:.2f}, completed: {_path.completed}")
                print(f"\nFound path --> Path ID: {id_path}, path: {_path!r}")

                for edge in _path.edges:
                    #print(f"Edge {edge.name} from {getFormattedPoint(edge.wpA.point)} to {getFormattedPoint(edge.wpB.point)}")
                    print(f"Edge {edge!r}")

            best_path = path_collection.get_best_path(aircraft_range_max)       

            print(f"\nBest path length: {best_path.total_length:.2f}, danger: {best_path.total_danger:.2f}")

            for edge in best_path.edges:
                #print(f"Edge from {getFormattedPoint(edge.wpA.point)} to {getFormattedPoint(edge.wpB.point)}")
                print(f"Edge {edge!r}")
                
            return best_path.to_route()
        
        return None

   

    def excludeThreat(self, threats: list[ThreatAA], arg) -> bool:
        # Controlla che gli elementi della lista siano di tipo ThreatAA
        if not all(isinstance(threat, ThreatAA) for threat in threats):
            raise TypeError("All elements in the list must be of type ThreatAA")
        
        check_for_altitude = False
        check_for_point = False

        if isinstance(arg, Point3D):
            point = arg
            check_for_point = True

        if isinstance(arg, float) or isinstance(arg, int):
            aircraft_altitude_route = arg
            check_for_altitude = True
                    
        threats_to_remove = []

        for threat in threats:
            
            if check_for_point and threat.innerPoint(point):
                threats_to_remove.append(threat)                

            if check_for_altitude and (  aircraft_altitude_route > threat.max_altitude or aircraft_altitude_route < threat.min_altitude):
                threats_to_remove.append(threat)                
                

        for threat in threats_to_remove:
            threats.remove(threat)

        return check_for_altitude or check_for_point
    
    def firstThreatIntersected(self, edge: Edge, threats: list[ThreatAA]) -> ThreatAA:
        DEBUG = True
        threat_distance = float('inf') # distanza da edge.wpa a threat.center
        first_threat = None
        complete_intersection = None
        complete_intersection_first_threat = None

        for threat in threats:
            complete_intersection, intersection = threat.edgeIntersect(edge)
            
            if complete_intersection or intersection:                
                wpA_Intersection_distance = edge.wpA.point.distance(intersection.p1) # distanza dalla circonferenza della threat
                
                if wpA_Intersection_distance < threat_distance:
                    threat_distance = wpA_Intersection_distance
                    complete_intersection_first_threat = complete_intersection
                    first_threat = threat                    
                    if DEBUG: print(f"Found threat intersection at lesser distance: threat: {threat!r}, threat_distance: {threat_distance:.2f}")        

        return complete_intersection_first_threat, first_threat

    def checkPathOverlimits(self, path_id, path: Path, range_max: float, danger_max: float) -> bool:
        DEBUG = True

        if path.total_length > range_max:
            if DEBUG:
                print(f"Current path {path_id} with length {path.total_length:.2f} exceed range_max {range_max:.2f}")
            return True
        
        if path.total_danger > danger_max:
            if DEBUG:
                print(f"Current path {path_id} with danger {path.total_danger:.2f} exceed danger_max {danger_max:.2f}")
            return True
        
        return False

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
        time_to_inversion: float,
        change_alt_option: str,
        max_recursion: int = MAX_RECURSION,
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
        edge = Edge(f"P:{path_id}-E:{n_edge}", n_edge, wp_A, wp_B, aircraft_speed)

        if debug:
            print(f"\nRecursion: {max_recursion} - Processing path {path_id}, edge {n_edge}: {wp_A.name}({getFormattedPoint(wp_A.point)}) -> {wp_B.name}({getFormattedPoint(wp_B.point)})")

        # Verifica intersezioni con minacce
        _, threat_intersect = self.firstThreatIntersected(edge, threats)

        if not threat_intersect:
            current_path.add_edge(edge)
            
            # terminate path if length or danger exceed limits
            if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                return False
            
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
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion - 1, debug
            )

        # Gestione alternativa (cambio quota o percorso alternativo)
        return self._handle_threat_avoidance(
            edge, threat_intersect, p1, p2, end, threats, n_edge,
            path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
            change_alt_option, max_recursion, debug
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
        aircraft_altitude: float,             
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        max_recursion: int = MAX_RECURSION,
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
        edge = Edge(f"P:{path_id}-E:{n_edge}", n_edge, wp_A, wp_B, aircraft_speed)

        if debug:
            print(f"\nProcessing path {path_id}, edge n:{n_edge}: {edge!r}")

        # Verifica intersezioni con minacce
        complete_intersection, threat_intersect = self.firstThreatIntersected(edge, threats)

        if not threat_intersect:
            current_path.add_edge(edge)

            # terminate path if length or danger exceed limits
            if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                return False
            
            if debug:
                print(f"No threats found. Added edge to path {path_id}")

            if p2 == end:
                path_collection.mark_path_completed(path_id)
                if debug:
                    print(f"Path {path_id} completed successfully!")
                return True

            return self.calcPathWithThreat(
                p2,
                end, 
                end, 
                threats, 
                n_edge + 1, 
                path_id, 
                path_collection, 
                aircraft_altitude,
                aircraft_altitude_min, 
                aircraft_altitude_max,
                aircraft_speed_max, 
                aircraft_speed, 
                aircraft_range_max, 
                time_to_inversion,
                change_alt_option, 
                max_recursion - 1, 
                debug
            )

        elif complete_intersection: # l'intersezione con la prima threat trovata è completa (il segmento interseca la threat in due punti)
            threatInrange, intersection = threat_intersect.edgeIntersect(edge) # crea l'intersezione

            if not threatInrange and intersection:
                raise Exception(f"not valid intersection: {getFormattedPoint(intersection.p1)} - {getFormattedPoint(intersection.p2)}")
                
            max_length = threat_intersect.calcMaxLenghtCrossSegment(aircraft_speed, 
                                                                    aircraft_altitude, 
                                                                    time_to_inversion)
                   

            #if intersection.length < MIN_SECURE_LENGTH_EDGE or intersection.length < max_length: #NO NO DEVE ESSERE VERIFICATO PER CONSENTIRE LA VERIFICA SE L'EDGE (IL SECOND PPUNTO) CADE DENTRO UNA THREAT DIFFERENTE#la lunghezza dell'intersezione completa è inferiore al valore minimo di default
                
                # NO DEVI VERIFICARE SE P2 DI EDGE NON SIA PRESENTE DENTRO UNA SECONDA THREAT DA RIVEDERE

                # SBAGLIATO L'EDGE: P2 DEVE ESSERE IL SECONDO PUNTO DEELL'INTERSEZIONE 
                #edge.danger = threat_intersect.danger_level * intersection.length / max_length
                #current_path.add_edge(edge)

                #if debug:
                #    print(f"intersection.length( {intersection.length:.2f} ) < MIN_SECURE_LENGTH_EDGE ({MIN_SECURE_LENGTH_EDGE}) or < max_length {max_length:.2f}. added edge: {edge!r}")#:({edge.wpA.point.x:.2f}, {edge.wpA.point.y:.2f}, {edge.wpA.point.z:.2f}) -  ({edge.wpB.point.x:.2f}, {edge.wpB.point.y:.2f}, {edge.wpB.point.z:.2f})")

                # terminate path if length or danger exceed limits
                #if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                #   return False
            """
            return self.calcPathWithThreat(
                p2,
                end, 
                end, 
                threats, 
                n_edge + 1, 
                path_id, 
                path_collection, 
                aircraft_altitude,
                aircraft_altitude_min, 
                aircraft_altitude_max,
                aircraft_speed_max, 
                aircraft_speed, 
                aircraft_range_max, 
                time_to_inversion,
                change_alt_option, 
                max_recursion - 1, 
                debug
            )
            """
        
            #else: # la lunghezza dell'intersezione completa è superiore al valore minimo di default
                # Calcola la massima lunghezza per un attraversamento sicuro                       

            # Verifica se possiamo attraversare la minaccia in sicurezza
        
            return self._handle_threat_crossing(
                edge, 
                threat_intersect, 
                p2, 
                end, 
                threats, 
                n_edge,
                path_id, 
                path_collection, 
                max_length, 
                aircraft_altitude,
                aircraft_altitude_min, 
                aircraft_altitude_max,
                aircraft_speed_max, 
                aircraft_speed, 
                aircraft_range_max, 
                time_to_inversion,
                change_alt_option, 
                intersection, 
                max_recursion, 
                debug
            )
                    
        else:
            return False

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
        aircraft_altitude: float,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        intersection: Segment3D,
        max_recursion: int,
        debug: bool
    ) -> bool:
        """Gestisce l'attraversamento sicuro di una minaccia."""
        if debug:
            print(f"Attempting to cross threat: {threat!r} with max length {max_length: .2f}")


        p_A = Point2D(intersection.p1.x, intersection.p1.y)
        p_B = Point2D(intersection.p2.x, intersection.p2.y)
        # Trova i punti di attraversamento ottimali
        c, d = threat.cylinder.find_chord_coordinates(
            threat.cylinder.radius,
            threat.cylinder.center,
            p_A,
            p_B,
            max_length
        )

        if c.distance(edge.wpA.point2d) > d.distance(edge.wpA.point2d):
            s = c
            c = d
            d = s


        # sposta il punto esternamente alla threat in direzione del segmento intersecante        
        v_dx = d.x - c.x
        v_dy = d.y - c.y
        v_norm = math.sqrt(v_dx**2 + v_dy**2)        
        d = Point2D( d.x + v_dx  * TOLERANCE_FOR_INTERSECTION_CALCULUS / v_norm, d.y + v_dy * TOLERANCE_FOR_INTERSECTION_CALCULUS / v_norm)

        # Crea i waypoint di attraversamento
        wp_c = Waypoint(f"wp_{path_id}_{n_edge}_cross1", Point3D(c.x, c.y, edge.wpA.point.z), None)
        wp_d = Waypoint(f"wp_{path_id}_{n_edge}_cross2", Point3D(d.x, d.y, edge.wpA.point.z), None)

        # Edge fino al punto di ingresso
        edge_to_c = Edge(
            f"P:{path_id}-E:{n_edge}_pre", 
            n_edge,
            edge.wpA,
            wp_c,
            edge.speed
        )

        # Edge attraverso la minaccia
        edge_through = Edge(
            f"P:{path_id}-E:{n_edge + 1}_through", 
            n_edge + 1,
            wp_c,
            wp_d,
            edge.speed
        )        

        if debug:
            print(f"calculated candidate edges to path {path_id}:\n - from p1 to threat: {edge_to_c!r},\n - through threat: {edge_through!r}")
        # Verify other threat on exit point

        
        for other_threat in threats:

            if other_threat != threat and other_threat.innerPoint(wp_d.point): # exit point inside another threat

                result1 = False
                result2 = False

                if debug:
                    print(f"cross threat edge intersecate another threat: ( {other_threat!r} )")
         
                # continue to avoid threat with lateral moving from wpA to new lateral point wp_b1
                dir = get_direction_vector(Point2D(d.x, d.y), Point2D(c.x, c.y))
                dir = rotate_vector(dir, math.pi / 2) # ruota il vettore di 90 gradi rispetto al segmento intersecante
                new_p1 = Point3D(threat.cylinder.center.x + dir[0] * 1.5 * threat.cylinder.radius, threat.cylinder.center.y + dir[1] * 1.5 * threat.cylinder.radius, edge.wpA.point.z)                    
                wp_b1 = Waypoint(f"wp_{path_id}_{n_edge}_lateral_1", new_p1, None)
                new_edge_1 = Edge(
                    f"P:{path_id}-E:{n_edge}_new_lateral_1", 
                    n_edge,
                    edge.wpA,
                    wp_b1,
                    edge.speed
                )


                # continue to avoid threat with lateral moving from wpA to new lateral point wp_b2 - new path
                path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                new_path_id = path_collection.add_path(path_edges_copy) 
                dir = rotate_vector(dir, math.pi) # ruota il vettore di 180 gradi
                new_p2 = Point3D(threat.cylinder.center.x + dir[0] * 1.5 * threat.cylinder.radius, threat.cylinder.center.y + dir[1] * 1.5 * threat.cylinder.radius, edge.wpA.point.z)                    
                wp_b2 = Waypoint(f"wp_{path_id}_{n_edge}_lateral_2", new_p2, None)
                new_edge_2 = Edge(
                    f"P:{new_path_id}-E:{n_edge}_new_lateral_2", 
                    n_edge,
                    edge.wpA,
                    wp_b2,
                    edge.speed
                )

                if debug:
                    print(f"\n   calculare two lateral point: new_p1: {getFormattedPoint(new_p1)}, new_p2: {getFormattedPoint(new_p2)}")


                if debug:
                    print(f"\n   will try with lateral moving of radius of the first threat. New point p1: {getFormattedPoint(new_p1)}")


                result1 = self.calcPathWithThreat(
                    new_edge_1.wpA.point,  # Punto d
                    new_edge_1.wpB.point,
                    end,
                    threats, 
                    n_edge, 
                    path_id, 
                    path_collection, 
                    aircraft_altitude,
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion, 
                    change_alt_option, 
                    max_recursion - 1, 
                    debug
                )
                
                if debug:
                    print(f"\n   will try with lateral moving of radius of the first threat. New point p2: {getFormattedPoint(new_p1)}")

                result2 = self.calcPathWithThreat(
                    new_edge_2.wpA.point,  # Punto d
                    new_edge_2.wpB.point,
                    end,
                    threats, 
                    n_edge, 
                    new_path_id, 
                    path_collection, 
                    aircraft_altitude,
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion, 
                    change_alt_option, 
                    max_recursion - 1, 
                    debug
                )

                return result1 or result2

        # exit_point isn't inside other threats
        current_path = path_collection.get_path(path_id)
        current_path.add_edge(edge_to_c)
        edge_through.danger = threat.danger_level
        current_path.add_edge(edge_through)
        threats.remove(threat) #remove crossing threat

        if debug:
            print(f"cross threat edge don't intersecate other threat. Current path: {current_path!r},\n    added two edges candidate edges (from p1 to threat, through threat) and delete crossing threat {threat!r}")

            
        # terminate path if length or danger exceed limits
        if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
            return False

        # Prosegui dal punto di uscita
        return self.calcPathWithThreat(
            edge_through.wpB.point,  # Punto d
            end, 
            end, 
            threats, 
            n_edge + 2, 
            path_id, 
            path_collection, 
            aircraft_altitude,
            aircraft_altitude_min, 
            aircraft_altitude_max,
            aircraft_speed_max, 
            aircraft_speed, 
            aircraft_range_max, 
            time_to_inversion, 
            change_alt_option, 
            max_recursion - 1, 
            debug
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
        debug: bool
    ) -> bool:
        """Gestisce l'evitamento della minaccia con cambio quota o percorsi alternativi."""
        # Verifica se possiamo cambiare quota
        can_change_altitude =   ( change_alt_option!= "no_change") and (change_alt_option == "change_up" and (aircraft_altitude_max > threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE)) or (change_alt_option == "change_down" and (aircraft_altitude_min < threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE))                

        if can_change_altitude:


            if debug:
                print(f"Attempting altitude change for threat at {threat!r}")

            intersected, segm = threat.cylinder.getIntersection(
                edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
            )
            
            if not intersected:
                if debug:
                    print("Unexpected: no intersection found where threat was detected  (segm: {segm!r})")
                return False

            new_p1 = segm.p1
            new_p2 = segm.p2

            if change_alt_option == "change_up":
                new_altitude = ( 2 * aircraft_altitude_max + threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE ) / 3
                new_p1 = Point3D(new_p1.x, new_p1.y, new_altitude )
                new_p2 = Point3D(new_p2.x, new_p2.y, new_altitude ) 
                if debug:
                    print(f"Changing altitude UP to {new_p1.z:.2f}")
            else:
                new_altitude = ( threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE + 2 * aircraft_altitude_min ) / 3
                new_p1 = Point3D(new_p1.x, new_p1.y, new_altitude )
                new_p2 = Point3D(new_p2.x, new_p2.y, new_altitude )
                if debug:
                    print(f"Changing altitude DOWN to {new_p1.z:.2f}")

            # Crea nuovo edge con punto modificato
            new_wp_B = Waypoint(f"wp_B{path_id}_{n_edge}_alt", new_p1, None)
            new_wp_C = Waypoint(f"wp_C{path_id}_{n_edge}_alt", new_p2, None)

            new_edge = Edge(
                f"P:{path_id}-E:{n_edge}_alt",
                n_edge, 
                edge.wpA, 
                new_wp_B, 
                aircraft_speed
            )

            new_edge_C = Edge(
                f"P:{path_id}-E:{n_edge + 1}_alt", 
                n_edge + 1, 
                new_wp_B, 
                new_wp_C, 
                aircraft_speed
            )

            current_path = path_collection.get_path(path_id)
            current_path.add_edge(new_edge)
            edge_incr = 1

            if debug:
                if debug:
                    print(f"current path: {current_path!r} added edge from wpA to threat: {new_edge!r}")

            threatInRange, threat_intersect = self.firstThreatIntersected(new_edge_C, threats)

            if not threatInRange or threat_intersect.max_altitude < new_edge_C.wpA.point.z: #not self.firstThreatIntersected(new_edge_C, threats):                      
                current_path.add_edge(new_edge_C) # se il segmento che passa sopra la minaccia incontra altre minacce lo aggiunge al pth
                edge_incr = 2
                new_p1 = new_p2
                if debug:
                    print(f"current path: {current_path!r} added edge from previous edge.wpB up or down threat: {new_edge_C!r}")
           
            # terminate path if length or danger exceed limits
            if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                return False

            return self.calcPathWithoutThreat(
                new_p1, end, end, threats, n_edge + edge_incr, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion - 1, debug
            )
                        
        # Se non possiamo cambiare quota, troviamo percorsi alternativi calcolando gli extended points per una circonferenza leggermente più grande della threat
        extended_cylinder = Cylinder(threat.cylinder.center, threat.cylinder.radius * RADIUS_EXTENSION_THREAT_CIRCONFERENCE, threat.cylinder.height)
        ext_p1, ext_p2 = extended_cylinder.getExtendedPoints(
            edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
        )
        

        if not ext_p1 and not ext_p2: # si può verificare solo nel caso che uno dei punti p1 o p2 sia sulla circonferenza
            if debug:
                print(f"Could not find extended points around threat: p1 or p2 on threat circonferenze? -> wpA: {threat.cylinder.pointOfCirconference(edge.wpA.point2d)}, wpB: {threat.cylinder.pointOfCirconference(edge.wpB.point2d)}")
            return False

        if debug:
            print(f"found two external point from extended_cylinder threat({extended_cylinder!r}), ext1: {getFormattedPoint(ext_p1)}, ext2: {getFormattedPoint(ext_p2)}")

        ext_p1_distance = ext_p1.distance(edge.wpA.point) + ext_p1.distance(edge.wpB.point) # new
        ext_p2_distance = ext_p2.distance(edge.wpA.point) + ext_p2.distance(edge.wpB.point)  # new      
        
        if ext_p2_distance > 2 * ext_p1_distance: # new ext_p2 richiede un punto del percorso troppo distante rispetto ext_p1. Il punto non viemne considerato per procedere nella ricorsione per la valutazione di un percorso
            ext_p2 = None # procede solo ext_p2 con il path corrente
            if debug:
                print(f"Deleted ext_p2 from path ricorsion: ext_p2_distance{ext_p2_distance:.2f} > double ext_p1_distance{ext_p1_distance:.2f}")

        elif ext_p1_distance > 2 * ext_p2_distance: # new ext_p1 richiede un punto del percorso troppo distante rispetto ext_p12. Il punto non viemne considerato per procedere nella ricorsione per la valutazione di un percorso
            ext_p1 = None            
            new_path_id = path_id # procede solo ext_p2 con il path corrente
            if debug:
                print(f"Deleted ext_p1 from path ricorsion: ext_p1_distance{ext_p1_distance:.2f} > double ext_p2_distance{ext_p2_distance:.2f}")

        elif len(path_collection.paths) < MAX_PATHS: # procedono sia ext_p1 che  ext_p2 il primo con il path corrente, il secondo con un nuovo path
            path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
            new_path_id = path_collection.add_path(path_edges_copy) 

        else:
            if debug:
                print(f"Stop paths creation due max limit achieve{MAX_PATHS}")
            return False

        

        found_path1 = False
        found_path2 = False

        #DEVI VERIFICARE SE SIA EXTP1 CHE EXTP2 SONO TRUE IN TAL CASO DEVI AGGIUNGERE UN NUOVO PATH ALTRIMENTI NO.
        if ext_p1 or ext_p2: # new

            if ext_p1: # new
                #path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id = path_collection.add_path(path_edges_copy) 

                if debug:
                    print(f"Creating alternative path through new point (ext_p1): {getFormattedPoint(ext_p1)}")#, \nProcessing path {path_id}, new edge {new_edge1}: {new_edge1.wpA.name}({getFormattedPoint(new_edge1.wpA.point)}) -> {new_edge1.wpB.name}({getFormattedPoint(new_edge1.wpB.point)})")
                    
                #path_edges_copy_1_1 = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id_1_1 = path_collection.add_path(path_edges_copy_1_1) 
                #new_path_id_1_2 = path_collection.add_path(path_edges_copy_1_1) 

                found_path1 = self.calcPathWithoutThreat(
                    p1, 
                    ext_p1, 
                    end, 
                    threats, 
                    n_edge, 
                    path_id, 
                    path_collection, 
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion,
                    change_alt_option, 
                    max_recursion - 1, 
                    debug
                )                    
                """
                if not found_path1:  # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat
                    # PROVA AD EFFETTUARE UNO SPOSTAMENTO LATERALE SUL PÈIANO Z DAL SECONDO PUNTO DEL PRIMO EDGE P1-TRHEAT A 90 GRADI VERSO L'ESTERNO DELLA THREAT CON SPOSTAMENTO PARI AL RAGGIO DELLA THREAT                            
                    dir = get_direction_vector(Point2D(ext_p1.x, ext_p1.y), Point2D(threat.cylinder.center.x, threat.cylinder.center.y))
                    new_ext_p = Point3D(ext_p1.x + dir[0] * threat.cylinder.radius, ext_p1.y + dir[1] * threat.cylinder.radius, ext_p1.z)                                        
                    
                    # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat
                    if debug:
                        print(f"Path not found, will try with lateral moving of radius of the first threat {threat!r}. New point p1: {getFormattedPoint(new_ext_p)}")

                    found_path1 = self.calcPathWithoutThreat(
                        p1, 
                        new_ext_p, 
                        end,
                        threats,
                        n_edge,                
                        new_path_id_1_1,
                        path_collection,
                        aircraft_altitude_min,
                        aircraft_altitude_max,
                        aircraft_speed_max,
                        aircraft_speed,
                        aircraft_range_max,
                        time_to_inversion,
                        change_alt_option,
                        max_recursion - 1, 
                        debug
                    )   

                if not found_path1:  # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat
                    
                    dir = rotate_vector(dir, math.pi) # ruota il vettore di 180 gradi rispetto al segmento intersecante
                    new_ext_p = Point3D(ext_p1.x + dir[0] * threat.cylinder.radius, ext_p1.y + dir[1] * threat.cylinder.radius, ext_p1.z)  

                    # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat
                    if debug:
                        print(f"Path not found, will try with lateral moving of radius of the first threat {threat!r}. New point p1: {getFormattedPoint(new_ext_p)}")                  

                    found_path1 = self.calcPathWithoutThreat(
                        p1, 
                        new_ext_p, 
                        end,
                        threats,
                        n_edge,                
                        new_path_id_1_2,
                        path_collection,
                        aircraft_altitude_min,
                        aircraft_altitude_max,
                        aircraft_speed_max,
                        aircraft_speed,
                        aircraft_range_max,
                        time_to_inversion,
                        change_alt_option,
                        max_recursion - 1, 
                        debug
                    )   

                """
            if ext_p2:# new
                # Percorso alternativo 2 (ext_p2)    
                # devi 
                
                if debug:
                        print(f"alterative path for path_id {path_id} with ext_p1: {getFormattedPoint(ext_p2)} not found")
                
                #path_edges_copy_1 = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id_1_1 = path_collection.add_path(path_edges_copy_1) 
                #new_path_id_1_2 = path_collection.add_path(path_edges_copy_1) 

                found_path2 = self.calcPathWithoutThreat(
                    p1,
                    ext_p2, 
                    end, 
                    threats, 
                    n_edge, 
                    new_path_id, 
                    path_collection, # o path_edges_copy?
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion,
                    change_alt_option, 
                    max_recursion - 1, 
                    debug
                )
                """
                if not found_path2:  # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat
                    # PROVA AD EFFETTUARE UNO SPOSTAMENTO LATERALE DAL SECONDO PUNTO DEL PRIMO EDGE P1-TRHEAT A 90 GRADI VERSO L'ESTERNO DELLA THREAT CON SPOSTAMENTO PARI AL RAGGIO DELLA THREAT        
                            
                    dir = get_direction_vector(Point2D(ext_p2.x, ext_p2.y), Point2D(threat.cylinder.center.x, threat.cylinder.center.y))
                    new_ext_p = Point3D(ext_p2.x + dir[0] * threat.cylinder.radius, ext_p2.y + dir[1] * threat.cylinder.radius, ext_p2.z)  
                    
                    # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat
                    if debug:
                        print(f"Path not found, will try with lateral moving of radius of the first threat {threat!r}. New point p2: {getFormattedPoint(new_ext_p)}")
                    
                    found_path2 = self.calcPathWithoutThreat(
                        p1, 
                        new_ext_p, 
                        end,
                        threats,
                        n_edge,                
                        new_path_id_1_1,
                        path_collection, # o path_edges_copy?
                        aircraft_altitude_min,
                        aircraft_altitude_max,
                        aircraft_speed_max,
                        aircraft_speed,
                        aircraft_range_max,
                        time_to_inversion,
                        change_alt_option,
                        max_recursion - 1, 
                        debug
                    )

                if not found_path2:  # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat

                     # another try with new point calculated by lateral moving of the ext_p2 point, new position wil be increase at radius of the threat                        
                    dir = rotate_vector(dir, math.pi) # ruota il vettore di 180 gradi rispetto al segmento intersecante
                    new_ext_p = Point3D(ext_p2.x + dir[0] * threat.cylinder.radius, ext_p2.y + dir[1] * threat.cylinder.radius, ext_p2.z)               

                    if debug:
                        print(f"Path not found, will try with lateral moving of radius of the first threat {threat!r}. New point p2: {getFormattedPoint(new_ext_p)}")
                         
                    found_path2 = self.calcPathWithoutThreat(
                        p1, 
                        new_ext_p, 
                        end,
                        threats,
                        n_edge,                
                        new_path_id_1_2,
                        path_collection, # o path_edges_copy?
                        aircraft_altitude_min,
                        aircraft_altitude_max,
                        aircraft_speed_max,
                        aircraft_speed,
                        aircraft_range_max,
                        time_to_inversion,
                        change_alt_option,
                        max_recursion - 1, 
                        debug
                    )
                """

            return found_path1 or found_path2



            
                    

                

        


