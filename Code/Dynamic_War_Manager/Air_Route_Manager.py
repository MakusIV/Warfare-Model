import sys
import os
from heapq import heappop, heappush
import math
import copy
from numpy import arange
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

#NOTA: QUESTI PARAMETRI INFLUENZANO I RISULTATI DI RICERCA - CONSIGLIO: MANTENERE BASSO IL NUMERO DI RICORRENZE (MAX_RECURSION) E ALZARE IL NUMERO DI PATH (MAX_PATHS) PER OTTENERE UNA RICERCA VELOCE E CHE CONSIDERI I PERCORSI PIU' CORTI
# SE SI VUOLE UNA RICERCA PIÙ RAPIDA MA MENO CAPACE DI TROVARE IL PERCORSO OTTIMO -> DIMINUIRE SU MAX_PATH
# SI SCONSIGLIA DI AUMENTARE MAX_RECURSION OLTRE 10: LA RICERCA DIVENTA MOLTO ONEROSA E NON NECESSARIAMENTE CAPACE DI TROVARE PERCORSI MIGLIORI: LE RICORSIONI SONO EFFETTUATE PER OGNI SINGLO PATH DI RICERCA
MAX_PATHS = 50      # 50 path per una singola ricerca
MAX_COMPLETED = 10  # 10 path completati per ogni singolo percorso per interrompere la ricerca
MAX_RECURSION = 10  # 10 ricorsione per ogni path dedicato ad una ricerca
MAX_EDGES = 30      # 30
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE = 1.05 # factor to increment upper limits for altitude route path
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE = 0.95 # factor to decrement lower limits for altitude route path
RADIUS_EXTENSION_THREAT_CIRCONFERENCE = 1.03 # factor to increments radius threat circonference for route path calculus
MIN_SECURE_LENGTH_EDGE = 0.1 # max length of edge in threat zone (per velocizzare il calcolo: tutti i segmenti )
MIN_DISTANCE_TO_CHANGE_ALTITUDE = 1 # min distance from threat to change altitude
TOLERANCE_FOR_INTERSECTION_CALCULUS = 0.1 # minimum length of segment to consider it as valid intersection ATT questa è necessaria per distinguere un segmento da un punto 


class ThreatAA:
    
    def __init__(self, danger_level, interception_speed: float, min_fire_time: float, min_detection_time: float, cylinder: Cylinder):
        self.danger_level = danger_level                    
        self.interception_speed = interception_speed                            # speed of the interception object in m/s 
        self.min_fire_time = min_fire_time                                      # minimum time to fire an interception object in seconds
        self.min_detection_time = min_detection_time                            # minimum time to detect an intruders into this threat
        self.min_altitude = cylinder.bottom_center.z                            # minimum altitude of the threat
        self.max_altitude = cylinder.bottom_center.z + cylinder.height          # maximum altitude of the threat
        self.cylinder = cylinder                                                # geometric volume object of threat

    def edgeIntersect(self, edge) -> Tuple[bool, Optional[Segment3D]]:
        
        """_Check if the edge intersects with the threat cylinder. Returns the intersection segment if it does. 

        Returns:
            tuple: _bool, Segment3D/None:
              - True, Segment3D se il segmento interseca il cilindro in due punti posti sulla superfice laterale del cilindro, Segment3D definito dai punti di intersezione;
              - False, Segment3D se il segmento interseca il cilindro in due punti ed uno dei punti è su una delle superfici orizzontali del cilindro (top/down);
              - False, Segment3D se il segmento interseca il cilindro in un solo punto e uno degli estremi dell'edge è interno;
              - False, None se il segmento non interseca il cilindro;


        """

        segment = Segment3D(edge.wpA.point, edge.wpB.point)        
        return self.cylinder.getIntersection(segment, tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS)
    
    def innerPoint(self, point:Point3D):
        """ Check if the point is inside the threat cylinder. Returns True if it is."""            
        if self.cylinder.innerPoint(point):
            return True
        return False

    def calcMaxLenghtCrossSegment(self, aircraft_speed: float, aircraft_altitude: float, time_to_inversion: float) -> float:
        """ Calculate the maximum length of the segment that can be crossed in the threat zone before interception. Returns the length in meters. """
        a = 1 / aircraft_speed 
        b = 0.5 / self.interception_speed 
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
        

        time_max_in_threat_zone = lm / self.interception_speed
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
                f"  interception_speed: {self.interception_speed:.2f}\n"
                f"  min_fire_time: {self.min_fire_time:.2f}\n"
                f"  min_detection_time: {self.min_detection_time:.2f}")
        
    

class Waypoint:
    """Rappresents a waypoint in 3D space."""
    
    def __init__(self, name: str, point: Point3D, id: str|None):
        self.id = id                                # waypoint id    
        self.name = name                            # waypoint name
        self.point = point                          # 3d point
        self.point2d = Point2D(point.x, point.y)    # 2d point

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
    """Rappresents a route segment from two waypoints."""
    
    def __init__(self, name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float):
        self.name = name                                        # name = "P: num path - E: num edge "
        self.order_position = order_position                    # order position of the edge in the path (deprecatd ?)
        self.wpA = wpA                                          # waypoint A of edge
        self.wpB = wpB                                          # waypoint B of edge
        self.speed = speed                                      # speed of the edge (deprecated ?)
        self.length = wpA.point.distance(wpB.point)             # length of the edge
        self.danger = 0                                         # danger of the edge

    def getSegment3D(self):
        """Returns the Segment3D of edge"""
        return Segment3D(self.wpA.point, self.wpB.point)

    def to_dict(self) -> Dict:
        """Converts the edge to a dictionary for serialization."""
        
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
    """Rappresents a route composed of multiple edges."""

    def __init__(self, name, length: float|None, danger: float|None):
        self.name = name                    # name of the route
        self.edges = {}                     # dictionary of edges (key: tuple of waypoints)
        self.length = length                # length of the route
        self.danger = danger                # danger of the route
    
    def add_edge(self, edge: Edge):
        self.edges[(edge.wpA, edge.wpB)] = edge
    
    def getWaypoints(self):
        """Returns the waypoints list of the route (order)."""
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
        """Returns the points list of the route (order)."""
        waypoints = self.getWaypoints()
        points = [wp.point for wp in waypoints]
        return points  

    def getLength(self) -> float:
        """Returns the total length of the route."""
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
    """Rappresents a path composed of multiple edges."""
    edges: List['Edge']         # list of edges in the path
    completed: bool = False     # flag to indicate if the path is completed
    
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
    """Collection of paths with utility methods."""
    
    def __init__(self):
        self.paths: List[Path] = []
        self._active_path_indices = set()
        self.completed = 0

    
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
            self.completed += 1
    
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
    
    """ Class to calculate the best route avoiding threats with lesser length or best route with lesser danger and path length."""

    def __init__(self, start: Point3D, end: Point3D, threats: List[ThreatAA]):
        self.start = start                      # starting point of the route
        self.end = end                          # ending point of the route
        self.threats = threats                  # list of threats to avoid
        
        
    def calcRoute(self, start: Point3D, end: Point3D, threats_: list[ThreatAA], aircraft_altitude_route: float, aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, aircraft_time_to_inversion: float, change_alt_option: str = "no_change", intersecate_threat: bool = False, consider_aircraft_altitude_route: bool = True) -> Route:      
        """_summary_

        Args:
            start (Point3D): starting point of the route_
            end (Point3D): _ending point of the route_
            threats_ (list[ThreatAA]): _list of threats to avoid_
            aircraft_altitude_route (float): _aircraft reference altitude for the route_
            aircraft_altitude_min (float): _minimum altitude of the aircraft_
            aircraft_altitude_max (float): _maximum altitude of the aircraft_
            aircraft_speed_max (float): _maximum speed of the aircraft_
            aircraft_speed (float): _aircraft referemce speed_
            aircraft_range_max (float): _aircraft maximum range_
            aircraft_time_to_inversion (float): _aircraft time to inversion manouver to exit from threat volume_
            change_alt_option (str, optional): _flag to authorize change in aircraft altitude to avoid threat. Defaults to "no_change".
            intersecate_threat (bool, optional): _flag to authorize crossing threat volume. Defaults to False.
            consider_aircraft_altitude_route (bool, optional): _flag to authorize deleting threat with maximum height lesser of aircraft_altitude_route. Defaults to True.

        Returns:
            Route: best route avoiding threats or lesser danger level and path length
        """
        

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

            if change_alt_option == "change_down":
                raise Exception("Warning: consider_aricraft altitude == True and change:_alt_option == /'change_down'/ could be dangerous for path calculus")             
            self.excludeThreat(threats, aircraft_altitude_route) # exclude threats with max altitude lesser than aircraft altitude route

        if intersecate_threat: # if intersecate_threat is True, the aircraft can cross the threat volume. Path calculus is done with the crossing of the threat volume            
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
            found_path = self.calcPathWithoutThreat( # in this case the aircraft can't cross the threat volume. Path calculus is done avoiding threat volume
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

        
        
        if found_path: # if a path is found

            for id_path in range(len(path_collection.paths)):
                _path = path_collection.get_path(id_path)                
                print(f"\nFound path --> Path ID: {id_path}, path: {_path!r}")

                for edge in _path.edges:                    
                    print(f"Edge {edge!r}")

            best_path = path_collection.get_best_path(aircraft_range_max)       

            print(f"\nBest path length: {best_path.total_length:.2f}, danger: {best_path.total_danger:.2f}")

            for edge in best_path.edges:                
                print(f"Edge {edge!r}")
                
            return best_path.to_route()
        
        return None

   

    def excludeThreat(self, threats: list[ThreatAA], arg) -> bool:
        """Delete threats from the list of threats if match with the arg.

        Args:
            threats (list[ThreatAA]): _List of threats to check_
            arg (_Point3D or float or int_): _Point3D or float or int_ - Point3D to check if inside the threat volume or altitude to check if inside the threat volume
        

        Returns:
            bool: _True if threats was deleted, False otherwise_
        """        
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
        """_Returns first threat intersected by the edge and the intersection with the threat volume._

        Args:
            edge (Edge): _description_
            threats (list[ThreatAA]): _description_

        Returns:
            bool, ThreatAA: Returns bool and first threat encountered.
            _If intersection has two points on surface (lateral or horizzontal) cylinder - bool == True, first threat encountered. 
            _If intersection has only one point on lateral or horizzontal surface of cylinder and other point inside of cylinder - bool == False, , first threat encountered.
            _otherwise - bool == False, None 
        """        
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
        
        """_Check if the path exceed the limits of range and danger.

        Args:
            path_id (_type_): _id of the path_
            path (Path): _path object_
            range_max (float): _range max value_
            danger_max (float): _danger max value

        Returns:
            bool: True if the path exceed the limits, False otherwise
        """        
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
            True se è stato trovato almeno un percorso valido (inserito nella path collection), False altrimenti
        """
        if max_recursion <= 0 or path_collection.completed >= MAX_COMPLETED:
            if debug:
                print(f"Max recursion depth  or Max path completed {path_collection.completed} reached for path {path_id}")
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
            True se è stato trovato almeno un percorso valido (inserito nella path collection), False altrimenti
        """
        if max_recursion <= 0 or path_collection.completed >= MAX_COMPLETED:
            if debug:
                print(f"Max recursion depth or Max path completed {path_collection.completed}  completed reached for path {path_id}")
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
        p2: Point3D,# da eliminare
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
        """_Handles the threat crossing logic, including creating new edges and checking for valid paths._

        Args:
            edge (Edge): _edge object for evaluation_
            threat (ThreatAA): _threat object for evaluation_
            p2 (Point3D): _description_
            end (Point3D): _end point of the path_
            threats (List[ThreatAA]): _list of threats 
            n_edge (int): _edges counter
            path_id (int): _path id
            path_collection (PathCollection): _collection of paths found_
            max_length (float): _max length reference for calulated a valid intersection alternative 
            aircraft_altitude (float): _aircraft reference altitude_
            aircraft_altitude_min (float): _aircraft minimum altitude
            aircraft_altitude_max (float): _aircraft maximum altitude
            aircraft_speed_max (float): _aircraft maximum speed
            aircraft_speed (float): _aircraft reference speed
            aircraft_range_max (float): __aircraft maximum range
            time_to_inversion (float): _minimum time needed to invert aircraft direction
            change_alt_option (str): _flag to authorize change in aircraft altitude to avoid threat. Defaults to "no_change".
            intersection (Segment3D): _actual intersection segment of the edge with threat
            max_recursion (int): _recursion counter
            debug (bool): _flag to print debug info

        Returns:
            bool: _True if a valid path is found, False otherwise_
        """

        if debug:
            print(f"Attempting to cross threat: {threat!r} with max length {max_length: .2f}")

        # punti dell'intersezione relativa all'edge
        p_A = Point2D(intersection.p1.x, intersection.p1.y)
        p_B = Point2D(intersection.p2.x, intersection.p2.y)

        if intersection.length < max_length: # l'intersezione relativa all'edge è più corta della lunghezza massima consentita per l'attraversamento sicuro
            if debug:
                print(f"Intersection length {intersection.length:.2f} is less than max length {max_length:.2f}.")

            c = p_A
            d = p_B    


        else: # necesssario determinare un segmento d'intersezione alternativo da utilizzare come nuovo edge per un attarversamento sicuro
            if debug:
                print(f"Intersection length {intersection.length:.2f} is bigger than max length {max_length:.2f}.")

            
            # Trova i punti di attraversamento ottimali
            c, d = threat.cylinder.find_chord_coordinates(
                threat.cylinder.radius,
                threat.cylinder.center,
                p_A,
                p_B,
                max_length
            )
        # riordina i punti in modo da considerare c come primo punto e d come secondo punto
        if c.distance(edge.wpA.point2d) > d.distance(edge.wpA.point2d):
            s = c
            c = d
            d = s


        # calcola il vettore direzione e lo utilizza per lo spostamento  del punto esternamente alla threat in direzione del segmento intersecante                
        v_norm = get_direction_vector(Point2D(c.x, c.y), Point2D(d.x, d.y))
        #v_dx = d.x - c.x
        #v_dy = d.y - c.y
        #v_norm = math.sqrt(v_dx**2 + v_dy**2)        
        #d = Point2D( d.x + v_dx  * TOLERANCE_FOR_INTERSECTION_CALCULUS / v_norm, d.y + v_dy * TOLERANCE_FOR_INTERSECTION_CALCULUS / v_norm)
        d = Point2D( d.x + v_norm[0]  * TOLERANCE_FOR_INTERSECTION_CALCULUS, d.y + v_norm[1] * TOLERANCE_FOR_INTERSECTION_CALCULUS)

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
                # se sono rilevate altre threat non inserisco nessun edge dei due precedentemente calcolati e procedo
                # per calcolare due punti spostati lateralmente di +90 gradi e -90 gradi rispetto la direzione dell'edge iniziale di attraversamento della threat
                result1 = False
                result2 = False

                if debug:
                    print(f"cross threat edge intersecate another threat: ( {other_threat!r} )")
         
                # continue to avoid threat with lateral moving from wpA to new lateral point wp_b1
                dir = get_direction_vector(Point2D(d.x, d.y), Point2D(c.x, c.y))
                dir = rotate_vector(dir, math.pi / 2) # ruota il vettore direzione di 90 gradi rispetto al segmento intersecante
                new_p1 = Point3D(threat.cylinder.center.x + dir[0] * 1.5 * threat.cylinder.radius, threat.cylinder.center.y + dir[1] * 1.5 * threat.cylinder.radius, edge.wpA.point.z)# nuovo punto calcolato in direzione di 90 gradi rispetto la direzione dell'edge  precedentemente calcolato
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
                dir = rotate_vector(dir, math.pi) # ruota il vettore di 180 (-90) gradi rispetto al segmento intersecante
                new_p2 = Point3D(threat.cylinder.center.x + dir[0] * 1.5 * threat.cylinder.radius, threat.cylinder.center.y + dir[1] * 1.5 * threat.cylinder.radius, edge.wpA.point.z)# nuovo punto calcolato in direzione di -90 gradi rispetto la direzione dell'edge  precedentemente calcolato                    
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
                    print(f"\n   will try with lateral moving of radius of the first threat. New point p1: {getFormattedPoint(new_p1)}")
                
                result1 = self.calcPathWithThreat( # prova a calcolare il percorso con il nuovo edge relativo al nuovo punto calcolato con uno spostamento di 90 gradi rispetto l'edge precedentemente calcolato
                    new_edge_1.wpA.point,  # punto wpA  dell'edge precedentemente calcolato
                    new_edge_1.wpB.point,  # nuovo punto calcolato con uno spostamento di +90 gradi rispetto l'edge precedentemente calcolato
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

                result2 = self.calcPathWithThreat(# prova a calcolare il percorso con il nuovo edge relativo al nuovo punto calcolato con uno spostamento di -90 gradi rispetto l'edge precedentemente calcolato
                    new_edge_2.wpA.point,  # punto wpA  dell'edge precedentemente calcolato
                    new_edge_2.wpB.point,  # nuovo punto calcolato con uno spostamento di -90 gradi rispetto l'edge precedentemente calcolato
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
        current_path.add_edge(edge_to_c) # inserisco l'edge da p1 a c
        edge_through.danger = threat.danger_level
        current_path.add_edge(edge_through) # inserisco l'edge da c a d
        threats.remove(threat) #remove crossing threat. È improbabile che il calcolo dei successivi edge possa determinare una inversione della direzione del percorso tale da reintersecare la threat da cancellare

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
            n_edge + 2, # gli edge inseriti nel path sono due: edge_to_c e edge_through
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
        """_Handles the threat avoidance logic, including altitude change or alternative paths._

        Args:            
            edge (Edge): _edge object for evaluation_
            threat (ThreatAA): _threat object for evaluation_
            p1 (Point3D): _first point of the edge_
            p2 (Point3D): _second point of the edge_
            end (Point3D): _end point of the path_
            threats (List[ThreatAA]): _list of threats 
            n_edge (int): _edges counter
            path_id (int): _path id
            path_collection (PathCollection): _collection of paths found_                        
            aircraft_altitude_min (float): _aircraft minimum altitude
            aircraft_altitude_max (float): _aircraft maximum altitude
            aircraft_speed_max (float): _aircraft maximum speed
            aircraft_speed (float): _aircraft reference speed
            aircraft_range_max (float): __aircraft maximum range
            time_to_inversion (float): _minimum time needed to invert aircraft direction
            change_alt_option (str): _flag to authorize change in aircraft altitude to avoid threat. Defaults to "no_change".            
            max_recursion (int): _recursion counter
            debug (bool): _flag to print debug info


        Returns:
            bool: _True if a valid path is found, False otherwise_
        """        
        
        # Verifica se possiamo cambiare quota
        can_change_altitude =   ( change_alt_option!= "no_change") and (change_alt_option == "change_up" and (aircraft_altitude_max > threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE)) or (change_alt_option == "change_down" and (aircraft_altitude_min < threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE))                

        if can_change_altitude:
            
            if debug:
                print(f"Attempting altitude change for threat at {threat!r}")

            intersected, segm = threat.cylinder.getIntersection(
                edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
            )
            
            
            if not intersected and segm: # se l'intersezione è un segmento (parte dell'edge) che attraversa la threat viene dall'alto e và verso il basso, può essere gestito con cambio quota di pb. altrimenti no

                pa, pb = segm.points

                if  not ( threat.cylinder.innerPoint(pa) and  pa.z >= threat.max_altitude ): # l'intersezione non è un segmentro (parte dell'edge) che attraversa la threat viene dall'alto e và verso il basso. Quind non gestito con cambio quota

                    if debug:
                        print(f"Unexpected: no intersection found where threat was detected  (segm: {segm!r})")                    
                    
                    return False
            

            new_p1 = segm.p1
            new_p2 = segm.p2

            if edge.wpA.point.distance(Point3D(new_p1.x, new_p1.y, edge.wpA.point.z)) < MIN_DISTANCE_TO_CHANGE_ALTITUDE:# la distanza tra p1 e il cilindro è insufficiente a consentire all'aereo di cambiare quota

                if debug:
                    print(f"Distance to change altitude is too small: {edge.wpA.point.distance(Point3D(new_p1.x, new_p1.y, edge.wpA.point.z)):.2f} < {MIN_DISTANCE_TO_CHANGE_ALTITUDE}")

                # calcola il vettore direzione e lo utilizza per lo spostamento  del punto esternamente alla threat in direzione traslata di +90 gradi e -90 gradi rispetto al segmento intersecante
                direction_movement = get_direction_vector(edge.wpA.point2d, edge.wpB.point2d)
                direction_movement = rotate_vector(direction_movement, math.pi / 2) # direzione +90 gradi
                direction_movement_1 = rotate_vector(direction_movement, math.pi) # direzione -90 gradi
                new_p = None

                # prova a calcolare nuovo punti di attraversamento spostati lateralmente di +90 gradi e -90 gradi, a diverse distannze, rispetto la direzione dell'edge iniziale di attraversamento della threat verificando per ogni punto calcolato se questo è interno  ad una threat.
                #for ds in (0.1, 0.3, 0.6, 0.9, 1.2, 1.5, 2):
                for ds in (5, 10, 30, 70, 100):
                    #new_pA = Point3D(new_p1.x + direction_movement[0] * threat.cylinder.radius * ds, new_p1.y + direction_movement[1] * threat.cylinder.radius * ds, edge.wpA.point.z)                
                    #new_pB = Point3D(new_p1.x + direction_movement_1[0] * threat.cylinder.radius * ds, new_p1.y + direction_movement_1[1] * threat.cylinder.radius * ds, edge.wpA.point.z)                    
                    new_pA = Point3D(new_p1.x + direction_movement[0] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, new_p1.y + direction_movement[1] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, edge.wpA.point.z)                
                    new_pB = Point3D(new_p1.x + direction_movement_1[0] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, new_p1.y + direction_movement_1[1] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, edge.wpA.point.z)                    
                    
                    if not threat.innerPoint(new_pA):
                        new_p = new_pA
                        break
                        
                    elif not threat.innerPoint(new_pB):
                        new_p = new_pB
                        break

                if new_p: # trovato un nuovo punto laterale non interno ad una threat

                    if debug:
                        print(f" I'll try search path with new point: {getFormattedPoint(new_p)}.")

                    return self.calcPathWithoutThreat( # prosegue la ricerca del path utilizzando questo nuovo punto come p2
                        edge.wpA.point, new_p, end, threats, n_edge, path_id, path_collection, 
                        aircraft_altitude_min, aircraft_altitude_max,
                        aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                        change_alt_option, max_recursion - 1, debug
                    )
                                                        

            else:# la distanza tra p1 e il cilindro è idonea a consentire all'aereo di cambiare quota

                # calcolo nuovo punto sopra la threat
                if change_alt_option == "change_up":
                    new_altitude = ( 2 * aircraft_altitude_max + threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE ) / 3
                    new_p1 = Point3D(new_p1.x, new_p1.y, new_altitude )
                    new_p2 = Point3D(new_p2.x, new_p2.y, new_altitude ) 
                    if debug:
                        print(f"Changing altitude UP to {new_p1.z:.2f}")
                
                # calcolo nuovo punto sotto la threat        
                else:
                    new_altitude = ( threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE + 2 * aircraft_altitude_min ) / 3
                    new_p1 = Point3D(new_p1.x, new_p1.y, new_altitude )
                    new_p2 = Point3D(new_p2.x, new_p2.y, new_altitude )
                    if debug:
                        print(f"Changing altitude DOWN to {new_p1.z:.2f}")

                # Crea nuovo edge con punto modificato
                new_wp_B = Waypoint(f"wp_B{path_id}_{n_edge}_alt", new_p1, None)
                new_wp_C = Waypoint(f"wp_C{path_id}_{n_edge}_alt", new_p2, None)

                new_edge = Edge( # edge da wpA al primo punto spra la threat
                    f"P:{path_id}-E:{n_edge}_alt",
                    n_edge, 
                    edge.wpA, 
                    new_wp_B, 
                    aircraft_speed
                )

                new_edge_C = Edge(# edge dal primo punto spra la threat alla fine della threat
                    f"P:{path_id}-E:{n_edge + 1}_alt", 
                    n_edge + 1, 
                    new_wp_B, 
                    new_wp_C, 
                    aircraft_speed
                )

                current_path = path_collection.get_path(path_id)
                current_path.add_edge(new_edge) # inserisco il primo edge nel path
                edge_incr = 1

                if debug:
                    if debug:
                        print(f"current path: {current_path!r} added edge from wpA to threat: {new_edge!r}")

                # verifico se il secondo edge, quello che passa sopra la threat, non intersechi una threat differente rispetto quella considerata per il cambio della quota
                threatInRange, threat_intersect = self.firstThreatIntersected(new_edge_C, threats)

                # se il secondo edge non interseca una minaccia diversa da quella utilizzata per il calcolo della quota procede con il suo inserimento nel path
                if not threat_intersect or threat_intersect.max_altitude < new_edge_C.wpB.point.z: #not self.firstThreatIntersected(new_edge_C, threats):                      
                    current_path.add_edge(new_edge_C) # se il segmento che passa sopra la minaccia incontra altre minacce lo aggiunge al pth
                    edge_incr = 2
                    new_p1 = new_p2
                    if debug:
                        print(f"current path: {current_path!r} added edge from previous edge.wpB up or down threat: {new_edge_C!r}")
            
                # terminate path if length or danger exceed limits
                if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                    return False

                return self.calcPathWithoutThreat(# prosegue nella creazione del path
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
        

        if not ext_p1 and not ext_p2: # punti esterni non trovati: si può verificare solo nel caso che uno dei punti p1 o p2 sia sulla circonferenza
            if debug:
                print(f"Could not find extended points around threat: p1 or p2 on threat circonferenze? -> wpA: {threat.cylinder.pointOfCirconference(edge.wpA.point2d)}, wpB: {threat.cylinder.pointOfCirconference(edge.wpB.point2d)}")
            return False

        if debug:
            print(f"found two external point from extended_cylinder threat({extended_cylinder!r}), ext1: {getFormattedPoint(ext_p1)}, ext2: {getFormattedPoint(ext_p2)}")

        # verifica della lunghezza dai punti calcolati rispetto il primo punto per eliminare quello la cui distanza eccessiva è dovuta ad una condizione critica di posizione rispetto al punto di destinazione e vicinanza rispetto la superfica laterale della threat: le  due tangenti utilizzate per determinare il punto d'intersezione ext_p sono quasi parallele)
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


        # Verifica se i punti estesi sono all'interno di altre minacce
        for other_threat in threats:
            
            if ext_p1 and other_threat != threat and other_threat.innerPoint(ext_p1):
                
                if debug:
                    print(f"Extended point ext_p1 is inside another threat: {other_threat!r}. Trying to find a new point with lateral movement.")
                
                
                # calcola un nuovo punto applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno)
                direction_movement = get_direction_vector(Point2D(threat.cylinder.center.x, threat.cylinder.center.y), Point2D(ext_p1.x, ext_p1.y))
                valid_lateral_movement_ext_p1 = False
                
                # calcola nuove posizioni applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno) considerando come nuovo punto da considerare il primo che risulta non interno ad una threat
                for ds in (0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 2.0):
                    ext_p1 = Point3D(ext_p1.x + direction_movement[0] * ds * other_threat.cylinder.radius, ext_p1.y + direction_movement[1] * ds * other_threat.cylinder.radius, ext_p1.z)                                        
                    
                    if not other_threat.innerPoint(ext_p1):
                        print(f"Valid lateral movement of Extended point ext_p1 {getFormattedPoint(ext_p1)}")
                        valid_lateral_movement_ext_p1 = True
                        break
            
                if not valid_lateral_movement_ext_p1 and debug:            
                    ext_p1 = None
                    print(f"Not valid lateral movement of Extended point ext_p1 {getFormattedPoint(ext_p1)}. ext_p1 is inside another threat: {other_threat!r}")


            if ext_p2 and other_threat != threat and other_threat.innerPoint(ext_p2):
                
                if debug:
                    print(f"Extended point ext_p2 is inside another threat: {other_threat!r}. Trying to find a new point with lateral movement.")
                
                # calcola un nuovo punto applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno)
                direction_movement = get_direction_vector(Point2D(threat.cylinder.center.x, threat.cylinder.center.y), Point2D(ext_p2.x, ext_p2.y))
                valid_lateral_movement_ext_p2 = False

                # calcola nuove posizioni applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno) considerando come nuovo punto da considerare il primo che risulta non interno ad una threat
                for ds in (0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 2.0):
                    ext_p2 = Point3D(ext_p2.x + direction_movement[0] * ds * other_threat.cylinder.radius, ext_p2.y + direction_movement[1] * ds * other_threat.cylinder.radius, ext_p2.z)                                        
                    
                    if not other_threat.innerPoint(ext_p2):
                        print(f"Valid lateral movement of Extended point ext_p2 {getFormattedPoint(ext_p2)}")
                        valid_lateral_movement_ext_p2 = True
                        break
                
                
                if not valid_lateral_movement_ext_p2 and debug:
                    ext_p2 = None
                    print(f"Not valid lateral movement of Extended point ext_p2 {getFormattedPoint(ext_p2)}. ext_p2 is inside another threat: {other_threat!r}")        

        if len(path_collection.paths) < MAX_PATHS: # procedono sia ext_p1 che  ext_p2 il primo con il path corrente, il secondo con un nuovo path
            path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
            new_path_id = path_collection.add_path(path_edges_copy) 

        else:
            if debug:
                print(f"Stop paths creation due max limit achieve{MAX_PATHS}")
            return False

        found_path1 = False
        found_path2 = False


        if ext_p1 or ext_p2: # uno o due nuovi punti esterni alla minaccia sono stati trovati

            if ext_p1: # new
                #path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id = path_collection.add_path(path_edges_copy) 

                if debug:
                    print(f"Creating alternative path through new point (ext_p1): {getFormattedPoint(ext_p1)}")#, \nProcessing path {path_id}, new edge {new_edge1}: {new_edge1.wpA.name}({getFormattedPoint(new_edge1.wpA.point)}) -> {new_edge1.wpB.name}({getFormattedPoint(new_edge1.wpB.point)})")
                    
                #path_edges_copy_1_1 = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id_1_1 = path_collection.add_path(path_edges_copy_1_1) 
                #new_path_id_1_2 = path_collection.add_path(path_edges_copy_1_1) 

                found_path1 = self.calcPathWithoutThreat(# prosegue la ricerca del path considerando il nuovo punto
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
               
            if ext_p2:# new
                # Percorso alternativo 2 (ext_p2)    
                
                
                if debug:
                        print(f"alterative path for path_id {path_id} with ext_p1: {getFormattedPoint(ext_p2)} not found")
                
                #path_edges_copy_1 = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id_1_1 = path_collection.add_path(path_edges_copy_1) 
                #new_path_id_1_2 = path_collection.add_path(path_edges_copy_1) 

                found_path2 = self.calcPathWithoutThreat(# prosegue la ricerca del path considerando il nuovo punto
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
                
            return found_path1 or found_path2



            
                    

                

        


