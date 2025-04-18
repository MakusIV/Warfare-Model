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
from functools import singledispatch

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Code.Dynamic_War_Manager.Cylinder import Cylinder
from Code.Utility import getFormattedPoint


MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE = 1.05 # factor to increment upper limits for altitude route path
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE = 0.95 # factor to decrement lower limits for altitude route path
RADIUS_EXTENSION_THREAT_CIRCONFERENCE = 1.03 # factor to increments radius threat circonference for route path calculus
MIN_SECURE_LENGTH_EDGE = 0.1 # max length of edge in threat zone (per velocizzare il calcolo: tutti i segmenti )
TOLERANCE_FOR_INTERSECTION_CALCULUS = 0.1 # minimum length of segment to consider it as valid intersection ATT questa è necessaria per distinguere un segmento da un punto 

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
        return self.cylinder.getIntersection(segment, tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS)
    
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
        max_segment_lenght_in_threat_zone = ( time_max_in_threat_zone + time_to_inversion + self.min_fire_time) * aircraft_speed


        return max_segment_lenght_in_threat_zone
     

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
        
        
    def calcRoute(self, start: Point3D, end: Point3D, threats: list[ThreatAA], aircraft_altitude_route: float, aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, aircraft_time_to_inversion: float, change_alt_option: str = "no_change", intersecate_threat: bool = False, consider_aircraft_altitude_route: bool = True) -> Route:      

        # change_alt_option: str = "no_change", "change_down", "change_up"
        # NOTA: 
        # CONSIDERANDO L'ARCHITETTURA DI QUESTO ALGORITMO CONVIENE CALCOLARE LE ROTTE 
        # ESEGUENDO QUESTA FUNZIONE CONSIDERANDO LA DOPPIA ESECUZIONE CON 
        # change_alt_option = "no_change" E CON change_alt_optiNo = "change_up o down"
        # p.e.: la scelta di cosa eseguire prima eè in base alle caratteristiche della missione:
        # mission low profile (evitare intercettazione): prima esegui calcRoute con l'opzione change_down" e se non trovi un percorso soddisfacente esegui calcRoute con l'altezza cosnisderata e l'opzione "no_change" seconda della convenienza prima esegui 

                      
        found_path = False
        

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
                print(f"\nFound path --> Path ID: {id_path}, Length: {_path.total_length:.2f}, Danger: {_path.total_danger:.2f}, completed: {_path.completed}")

                for edge in _path.edges:
                    print(f"Edge {edge.name} from {getFormattedPoint(edge.wpA.point)} to {getFormattedPoint(edge.wpB.point)}")

            best_path = path_collection.get_best_path(aircraft_range_max)       

            print(f"\nBest path length: {best_path.total_length:.2f}, danger: {best_path.total_danger:.2f}")

            for edge in best_path.edges:
                print(f"Edge from {getFormattedPoint(edge.wpA.point)} to {getFormattedPoint(edge.wpB.point)}")
                
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
    

        for threat in threats:
            threatInrange, intersection = threat.edgeIntersect(edge)
            
            if threatInrange or intersection:                
                wpA_Intersection_distance = edge.wpA.point.distance(intersection.p1) # distanza dalla circonferenza della threat
                
                if wpA_Intersection_distance < threat_distance:
                    threat_distance = wpA_Intersection_distance
                    first_threat = threat                    
                    if DEBUG: print(f"Found threat intersection at lesser distance: threat: {threat}, threat_distance: {threat_distance:.2f}")        

        return first_threat

    def checkPathOverlimits(self, path_id, path: Path, range_max: float, danger_max: float) -> bool:
        DEBUG = True

        if path.total_length > range_max:
            if DEBUG:
                print(f"Current path {path_id} with length {path.total_length} exceed range_max {range_max}")
            return True
        
        if path.total_danger > danger_max:
            if DEBUG:
                print(f"Current path {path_id} with danger {path.total_danger} exceed danger_max {danger_max}")
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
                aircraft_speed_max, aircraft_speed, aircraft_range_max,
                change_alt_option, max_recursion - 1, debug
            )

        # Gestione alternativa (cambio quota o percorso alternativo)
        return self._handle_threat_avoidance(
            edge, threat_intersect, p1, p2, end, threats, n_edge,
            path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, None,
            change_alt_option, max_recursion, "calcPathWithoutThreat", debug
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
                p2, end, end, threats, n_edge + 1, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion - 1, debug
            )

        else:
            threatInrange, intersection = threat_intersect.edgeIntersect(edge)
            
            # la lunghezza dell'intersezione è inferiore al valore minimo di default
            if intersection.length < MIN_SECURE_LENGTH_EDGE:

                current_path.add_edge(edge)

                # terminate path if length or danger exceed limits
                if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                    return False
                
                return self.calcPathWithThreat(
                p2, end, end, threats, n_edge + 1, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion - 1, debug
            )

            
            else: 
                # Calcola la massima lunghezza per un attraversamento sicuro
                max_length = threat_intersect.calcMaxLenghtCrossSegment(
                    aircraft_speed,
                    aircraft_altitude_max,            
                    time_to_inversion,                    
                    edge.getSegment3D()
                )

                # Verifica se possiamo attraversare la minaccia in sicurezza
                
                return self._handle_threat_crossing(
                    edge, threat_intersect, p2, end, threats, n_edge,
                    path_id, path_collection, max_length,
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                    change_alt_option, intersection, max_recursion, debug
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
        time_to_inversion: float,
        change_alt_option: str,
        intersection: Segment3D,
        max_recursion: int,
        debug: bool
    ) -> bool:
        """Gestisce l'attraversamento sicuro di una minaccia."""
        if debug:
            print(f"Attempting to cross threat at {threat.cylinder.center} with max length {max_length: .2f}")


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
            edge.wpA,
            wp_c,
            edge.speed
        )

        # Edge attraverso la minaccia
        edge_through = Edge(
            f"P:{path_id}-E:{n_edge}_through",
            wp_c,
            wp_d,
            edge.speed
        )

        # Verify other threat on exit point
        for other_threat in threats:

            if other_threat != threat and other_threat.innerPoint(wp_d.point): # exit point inside another threat
                
                # continue to avoid threat
                return self._handle_threat_avoidance(
                    edge, threat, edge.wpA.point, edge.wpB.point, end, threats, n_edge,
                    path_id, path_collection, 
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max, None,
                    change_alt_option, max_recursion, "calcPathWithThreat", debug
                )        

        # exit_point isn't inside other threats
        current_path = path_collection.get_path(path_id)
        current_path.add_edge(edge_to_c)
        current_path.add_edge(edge_through)

        # terminate path if length or danger exceed limits
        if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
            return False

        # Prosegui dal punto di uscita
        return self.calcPathWithThreat(
            edge_through.wpB.point,  # Punto d
            end, end, threats, n_edge + 2, path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, 
            time_to_inversion, change_alt_option, max_recursion - 1, debug
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
        can_change_altitude =   ( change_alt_option!= "no_change") and (change_alt_option == "change_up" and (aircraft_altitude_max > threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE)) or (change_alt_option == "change_down" and (aircraft_altitude_min < threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE))
                

        if can_change_altitude:
            if debug:
                print(f"Attempting altitude change for threat at {threat.cylinder.bottom_center}")

            intersected, segm = threat.cylinder.getIntersection(
                edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
            )
            
            if not intersected:
                if debug:
                    print("Unexpected: no intersection found where threat was detected")
                return False

            new_p1 = segm.p1
            if change_alt_option == "change_up":
                new_p1 = Point3D(new_p1.x, new_p1.y, threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE) 
                if debug:
                    print(f"Changing altitude UP to {new_p1.z:.2f}")
            else:
                new_p1 = Point3D(new_p1.x, new_p1.y, threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE)
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
            current_path = path_collection.get_path(path_id)
            current_path.add_edge(new_edge)

            # terminate path if length or danger exceed limits
            if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                return False

            if caller == "calcPathWithThreat":
                
                return self.calcPathWithThreat(
                    new_p1, p2, end, threats, n_edge + 1, path_id, path_collection, 
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion, 
                    change_alt_option, max_recursion - 1, debug
                )
            
            elif caller == "calcPathWithoutThreat":

                return self.calcPathWithoutThreat(
                    new_p1, p2, end, threats, n_edge + 1, path_id, path_collection, 
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max,
                    change_alt_option, max_recursion - 1, debug
                )
            
            else:
                raise ValueError(f"Unexpected caller: {caller}. Expected 'calcPathWithThreat' or 'calcPathWithoutThreat'.")

        # Se non possiamo cambiare quota, troviamo percorsi alternativi calcolando gli extended points per una circonferenza leggermente più grande della threat
        extended_cylinder = Cylinder(threat.cylinder.center, threat.cylinder.radius * RADIUS_EXTENSION_THREAT_CIRCONFERENCE, threat.cylinder.height)
        ext_p1, ext_p2 = extended_cylinder.getExtendedPoints(
            edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
        )
        

        # SE NON FUNZIONA VERIFICATA LA CODIZIONE DI  xt_p2_distance > 2 * ext_p1_distance RITORNA FALSE


        if not ext_p1 and not ext_p2: # or
            if debug:
                print("Could not find extended points around threat")
            return False

        

        ext_p1_distance = ext_p1.distance(edge.wpA.point) + ext_p1.distance(edge.wpB.point) # new
        ext_p2_distance = ext_p2.distance(edge.wpA.point) + ext_p2.distance(edge.wpB.point)  # new      
        
        if ext_p2_distance > 2 * ext_p1_distance: # new ext_p2 richiede un punto del percorso troppo distante rispetto ext_p1. Il punto non viemne considerato per procedere nella ricorsione per la valutazione di un percorso
            ext_p2 = None # procede solo ext_p2 con il path corrente
            if debug:
                print("Deleted ext_p2 from path ricorsion: ext_p2_distance{ext_p2_distance} > double ext_p1_distance{ext_p1_distance}")

        elif ext_p1_distance > 2 * ext_p2_distance: # new ext_p1 richiede un punto del percorso troppo distante rispetto ext_p12. Il punto non viemne considerato per procedere nella ricorsione per la valutazione di un percorso
            ext_p1 = None            
            new_path_id = path_id # procede solo ext_p2 con il path corrente
            if debug:
                print("Deleted ext_p1 from path ricorsion: ext_p1_distance{ext_p1_distance} > double ext_p2_distance{ext_p2_distance}")

        else: # procedono sia ext_p1 che  ext_p2 il primo con il path corrente, il secondo con un nuovo path
            path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
            new_path_id = path_collection.add_path(path_edges_copy) 

            
        
        if ext_p1: # new
            #path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
            #new_path_id = path_collection.add_path(path_edges_copy) 

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


        if ext_p2:# new
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


