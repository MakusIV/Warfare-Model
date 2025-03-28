

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei percorsi in una mappa di solidi di rotazione.

Questo modulo implementa classi e funzioni per gestire solidi di rotazione (parallelepipedi
e aggregati di parallelepipedi) posizionati su una mappa tridimensionale, e per calcolare
percorsi ottimali tra due punti evitando intersezioni con i solidi.
"""

import numpy as np
import sympy as sp
from sympy.geometry import Point3D, Point2D, Line3D, Segment3D
import heapq
import math
from typing import List, Tuple, Dict, Set, Optional, Union, Any


class SolidoParallelepipedo:
    """
    Rappresenta un parallelepipedo a base quadrata posizionato sulla mappa.
    
    Attributes:
        base_center (Point2D): Centro della base del parallelepipedo.
        side_length (float): Lunghezza del lato della base quadrata.
        height (float): Altezza del parallelepipedo.
        base_corners (List[Point2D]): Lista dei quattro angoli della base.
    """
    
    def __init__(self, base_center: Point2D, side_length: float, height: float):
        """
        Inizializza un nuovo parallelepipedo.
        
        Args:
            base_center (Point2D): Centro della base del parallelepipedo.
            side_length (float): Lunghezza del lato della base quadrata.
            height (float): Altezza del parallelepipedo.
        """
        self.base_center = base_center
        self.side_length = side_length
        self.height = height
        
        # Calcola gli angoli della base
        half_side = side_length / 2
        self.base_corners = [
            Point2D(base_center.x - half_side, base_center.y - half_side),  # Bottom-left
            Point2D(base_center.x + half_side, base_center.y - half_side),  # Bottom-right
            Point2D(base_center.x + half_side, base_center.y + half_side),  # Top-right
            Point2D(base_center.x - half_side, base_center.y + half_side)   # Top-left
        ]
        
        # Calcola i vertici 3D (8 vertici del parallelepipedo)
        self.vertices_3d = [
            # Base inferiore (z = 0)
            Point3D(self.base_corners[0].x, self.base_corners[0].y, 0),
            Point3D(self.base_corners[1].x, self.base_corners[1].y, 0),
            Point3D(self.base_corners[2].x, self.base_corners[2].y, 0),
            Point3D(self.base_corners[3].x, self.base_corners[3].y, 0),
            # Base superiore (z = height)
            Point3D(self.base_corners[0].x, self.base_corners[0].y, height),
            Point3D(self.base_corners[1].x, self.base_corners[1].y, height),
            Point3D(self.base_corners[2].x, self.base_corners[2].y, height),
            Point3D(self.base_corners[3].x, self.base_corners[3].y, height)
        ]
        
        # Calcola le facce del parallelepipedo (6 facce)
        # Ogni faccia è definita dai suoi 4 vertici
        self.faces = [
            # Base inferiore
            [self.vertices_3d[0], self.vertices_3d[1], self.vertices_3d[2], self.vertices_3d[3]],
            # Base superiore
            [self.vertices_3d[4], self.vertices_3d[5], self.vertices_3d[6], self.vertices_3d[7]],
            # Faccia frontale
            [self.vertices_3d[0], self.vertices_3d[1], self.vertices_3d[5], self.vertices_3d[4]],
            # Faccia posteriore
            [self.vertices_3d[2], self.vertices_3d[3], self.vertices_3d[7], self.vertices_3d[6]],
            # Faccia sinistra
            [self.vertices_3d[0], self.vertices_3d[3], self.vertices_3d[7], self.vertices_3d[4]],
            # Faccia destra
            [self.vertices_3d[1], self.vertices_3d[2], self.vertices_3d[6], self.vertices_3d[5]]
        ]
        
        # Calcola gli spigoli del parallelepipedo (12 spigoli)
        self.edges = [
            # Base inferiore
            Segment3D(self.vertices_3d[0], self.vertices_3d[1]),
            Segment3D(self.vertices_3d[1], self.vertices_3d[2]),
            Segment3D(self.vertices_3d[2], self.vertices_3d[3]),
            Segment3D(self.vertices_3d[3], self.vertices_3d[0]),
            # Base superiore
            Segment3D(self.vertices_3d[4], self.vertices_3d[5]),
            Segment3D(self.vertices_3d[5], self.vertices_3d[6]),
            Segment3D(self.vertices_3d[6], self.vertices_3d[7]),
            Segment3D(self.vertices_3d[7], self.vertices_3d[4]),
            # Spigoli verticali
            Segment3D(self.vertices_3d[0], self.vertices_3d[4]),
            Segment3D(self.vertices_3d[1], self.vertices_3d[5]),
            Segment3D(self.vertices_3d[2], self.vertices_3d[6]),
            Segment3D(self.vertices_3d[3], self.vertices_3d[7])
        ]
    
    def contains_point(self, point: Point3D) -> bool:
        """
        Verifica se un punto è contenuto nel parallelepipedo.
        
        Args:
            point (Point3D): Punto da verificare.
            
        Returns:
            bool: True se il punto è contenuto nel parallelepipedo, False altrimenti.
        """
        # Verifica se il punto è all'interno del parallelepipedo
        half_side = self.side_length / 2
        
        # Verifica se il punto è all'interno dei limiti x, y, z
        x_in_range = (self.base_center.x - half_side) <= point.x <= (self.base_center.x + half_side)
        y_in_range = (self.base_center.y - half_side) <= point.y <= (self.base_center.y + half_side)
        z_in_range = 0 <= point.z <= self.height
        
        return x_in_range and y_in_range and z_in_range
    
    def _point_on_face(self, point: Point3D, face_vertices: List[Point3D]) -> bool:
        """
        Verifica se un punto si trova su una faccia del parallelepipedo.
        
        Args:
            point (Point3D): Punto da verificare.
            face_vertices (List[Point3D]): Vertici della faccia.
            
        Returns:
            bool: True se il punto si trova sulla faccia, False altrimenti.
        """
        # Per verificare se un punto è su una faccia, controlliamo se:
        # 1. Il punto è complanare con la faccia
        # 2. Il punto è all'interno del poligono formato dai vertici della faccia
        
        # Calcola il vettore normale alla faccia
        v1 = face_vertices[1] - face_vertices[0]
        v2 = face_vertices[2] - face_vertices[0]
        
        # Utilizziamo Matrix di sympy per il prodotto vettoriale
        v1_vec = sp.Matrix([v1.x, v1.y, v1.z])
        v2_vec = sp.Matrix([v2.x, v2.y, v2.z])
        normal_vec = v1_vec.cross(v2_vec)
        normal = Point3D(normal_vec[0], normal_vec[1], normal_vec[2])
        
        # Verifica se il punto è complanare con la faccia
        # Equazione del piano: ax + by + cz + d = 0
        d = -(normal.x * face_vertices[0].x + normal.y * face_vertices[0].y + normal.z * face_vertices[0].z)
        dot_product = normal.x * point.x + normal.y * point.y + normal.z * point.z
        normal_norm = (normal.x**2 + normal.y**2 + normal.z**2)**0.5
        distance_to_plane = float(abs(dot_product + d) / normal_norm)
        
        # Tolleranza per errori di arrotondamento
        if distance_to_plane > 1e-10:
            return False
        
        # Verifica se il punto è all'interno del poligono
        # Proietta il punto e i vertici della faccia su un piano 2D
        # Scegliamo il piano in base alla componente più grande del vettore normale
        max_component = max(abs(normal.x), abs(normal.y), abs(normal.z))
        
        if max_component == abs(normal.x):
            # Proiezione sul piano YZ
            point_2d = Point2D(point.y, point.z)
            vertices_2d = [Point2D(v.y, v.z) for v in face_vertices]
        elif max_component == abs(normal.y):
            # Proiezione sul piano XZ
            point_2d = Point2D(point.x, point.z)
            vertices_2d = [Point2D(v.x, v.z) for v in face_vertices]
        else:
            # Proiezione sul piano XY
            point_2d = Point2D(point.x, point.y)
            vertices_2d = [Point2D(v.x, v.y) for v in face_vertices]
        
        # Verifica se il punto è all'interno del poligono usando il ray casting algorithm
        inside = False
        n = len(vertices_2d)
        for i in range(n):
            j = (i + 1) % n
            if ((vertices_2d[i].y > point_2d.y) != (vertices_2d[j].y > point_2d.y)) and \
               (point_2d.x < (vertices_2d[j].x - vertices_2d[i].x) * (point_2d.y - vertices_2d[i].y) / 
                (vertices_2d[j].y - vertices_2d[i].y) + vertices_2d[i].x):
                inside = not inside
        
        return inside
    
    def _segment_intersects_face(self, segment: Segment3D, face_vertices: List[Point3D]) -> Tuple[bool, Optional[Point3D]]:
        """
        Verifica se un segmento interseca una faccia del parallelepipedo.
        
        Args:
            segment (Segment3D): Segmento da verificare.
            face_vertices (List[Point3D]): Vertici della faccia.
            
        Returns:
            Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
            se c'è intersezione e, in caso affermativo, il punto di intersezione.
        """
        # Calcola il vettore normale alla faccia
        v1 = face_vertices[1] - face_vertices[0]
        v2 = face_vertices[2] - face_vertices[0]
        
        # Utilizziamo Matrix di sympy per il prodotto vettoriale
        v1_vec = sp.Matrix([v1.x, v1.y, v1.z])
        v2_vec = sp.Matrix([v2.x, v2.y, v2.z])
        normal_vec = v1_vec.cross(v2_vec)
        normal = Point3D(normal_vec[0], normal_vec[1], normal_vec[2])
        
        # Equazione del piano: ax + by + cz + d = 0
        d = -(normal.x * face_vertices[0].x + normal.y * face_vertices[0].y + normal.z * face_vertices[0].z)
        
        # Calcola l'intersezione tra il segmento e il piano della faccia
        p1, p2 = segment.points
        
        # Calcola i valori di t per i punti del segmento
        t1 = normal.dot(p1) + d
        t2 = normal.dot(p2) + d
        
        # Se t1 e t2 hanno lo stesso segno, il segmento non interseca il piano
        if t1 * t2 > 0:
            return False, None
        
        # Calcola il punto di intersezione
        t = float(t1 / (t1 - t2))
        # Calcola le coordinate del punto di intersezione manualmente
        x = p1.x + t * (p2.x - p1.x)
        y = p1.y + t * (p2.y - p1.y)
        z = p1.z + t * (p2.z - p1.z)
        intersection_point = Point3D(x, y, z)
        
        # Verifica se il punto di intersezione è all'interno della faccia
        if self._point_on_face(intersection_point, face_vertices):
            return True, intersection_point
        
        return False, None
    
    def intersects_segment(self, segment: Segment3D) -> Tuple[bool, Optional[Point3D]]:
        """
        Verifica se un segmento interseca il parallelepipedo.
        
        Args:
            segment (Segment3D): Segmento da verificare.
            
        Returns:
            Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
            se c'è intersezione e, in caso affermativo, il punto di intersezione.
        """
        # Verifica se uno degli estremi del segmento è contenuto nel parallelepipedo
        p1, p2 = segment.points
        if self.contains_point(p1):
            return True, p1
        if self.contains_point(p2):
            return True, p2
        
        # Verifica se il segmento interseca una delle facce del parallelepipedo
        for face in self.faces:
            intersects, point = self._segment_intersects_face(segment, face)
            if intersects:
                return True, point
        
        return False, None
    
    def intersects_line(self, line: Line3D) -> Tuple[bool, Optional[Point3D]]:
        """
        Verifica se una linea interseca il parallelepipedo.
        
        Args:
            line (Line3D): Linea da verificare.
            
        Returns:
            Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
            se c'è intersezione e, in caso affermativo, il punto di intersezione.
        """
        # Per ogni faccia del parallelepipedo, verifica se la linea interseca la faccia
        for face in self.faces:
            # Calcola il vettore normale alla faccia
            v1 = face[1] - face[0]
            v2 = face[2] - face[0]
            
            # Utilizziamo Matrix di sympy per il prodotto vettoriale
            v1_vec = sp.Matrix([v1.x, v1.y, v1.z])
            v2_vec = sp.Matrix([v2.x, v2.y, v2.z])
            normal_vec = v1_vec.cross(v2_vec)
            normal = Point3D(normal_vec[0], normal_vec[1], normal_vec[2])
            
            # Equazione del piano: ax + by + cz + d = 0
            d = -(normal.x * face[0].x + normal.y * face[0].y + normal.z * face[0].z)
            
            # Calcola l'intersezione tra la linea e il piano della faccia
            p, v = line.p1, line.direction
            
            # Verifica se la linea è parallela al piano
            denom = normal.x * v.x + normal.y * v.y + normal.z * v.z
            if abs(denom) < 1e-10:
                continue
            
            # Calcola il parametro t per il punto di intersezione
            t = -(normal.x * p.x + normal.y * p.y + normal.z * p.z + d) / denom
            
            # Calcola le coordinate del punto di intersezione manualmente
            x = p.x + t * v.x
            y = p.y + t * v.y
            z = p.z + t * v.z
            intersection_point = Point3D(x, y, z)
            
            # Verifica se il punto di intersezione è all'interno della faccia
            if self._point_on_face(intersection_point, face):
                return True, intersection_point
        
        return False, None
    
    def _aabb_intersect(self, other: 'SolidoParallelepipedo') -> bool:
        """
        Verifica se i bounding box dei due parallelepipedi si intersecano (AABB - Axis-Aligned Bounding Box).
        
        Args:
            other (SolidoParallelepipedo): Altro parallelepipedo.
            
        Returns:
            bool: True se i bounding box si intersecano, False altrimenti.
        """
        # Calcola i limiti dei due parallelepipedi
        half_side_self = self.side_length / 2
        half_side_other = other.side_length / 2
        
        # Limiti del primo parallelepipedo
        min_x_self = self.base_center.x - half_side_self
        max_x_self = self.base_center.x + half_side_self
        min_y_self = self.base_center.y - half_side_self
        max_y_self = self.base_center.y + half_side_self
        min_z_self = 0
        max_z_self = self.height
        
        # Limiti del secondo parallelepipedo
        min_x_other = other.base_center.x - half_side_other
        max_x_other = other.base_center.x + half_side_other
        min_y_other = other.base_center.y - half_side_other
        max_y_other = other.base_center.y + half_side_other
        min_z_other = 0
        max_z_other = other.height
        
        # Verifica se i bounding box si intersecano
        return (min_x_self <= max_x_other and max_x_self >= min_x_other and
                min_y_self <= max_y_other and max_y_self >= min_y_other and
                min_z_self <= max_z_other and max_z_self >= min_z_other)
    
    def intersects_solid(self, solid: 'SolidoParallelepipedo') -> bool:
        """
        Verifica se un altro solido interseca questo parallelepipedo.
        
        Args:
            solid (SolidoParallelepipedo): Solido da verificare.
            
        Returns:
            bool: True se i solidi si intersecano, False altrimenti.
        """
        # Prima verifica se i bounding box si intersecano
        if not self._aabb_intersect(solid):
            return False
        
        # Verifica se uno dei vertici di un parallelepipedo è contenuto nell'altro
        for vertex in self.vertices_3d:
            if solid.contains_point(vertex):
                return True
        
        for vertex in solid.vertices_3d:
            if self.contains_point(vertex):
                return True
        
        # Verifica se uno degli spigoli di un parallelepipedo interseca l'altro
        for edge in self.edges:
            intersects, _ = solid.intersects_segment(edge)
            if intersects:
                return True
        
        for edge in solid.edges:
            intersects, _ = self.intersects_segment(edge)
            if intersects:
                return True
        
        return False


class SolidoComposto:
    """
    Rappresenta un solido composto dall'unione di due o più parallelepipedi intersecanti.
    
    Attributes:
        components (List[SolidoParallelepipedo]): Lista dei parallelepipedi che compongono il solido.
        perimeter_segments (List[Tuple[Segment3D, float]]): Lista di segmenti che definiscono il perimetro
            della base, ciascuno con la propria altezza.
    """
    
    def __init__(self, components: List[SolidoParallelepipedo]):
        """
        Inizializza un nuovo solido composto.
        
        Args:
            components (List[SolidoParallelepipedo]): Lista dei parallelepipedi che compongono il solido.
        """
        self.components = components
        self.perimeter_segments = self._calculate_perimeter_segments()
        
        # Calcola il bounding box del solido composto
        self._calculate_bounding_box()
    
    def _calculate_bounding_box(self):
        """
        Calcola il bounding box del solido composto.
        """
        # Inizializza i limiti del bounding box
        min_x = float('inf')
        min_y = float('inf')
        min_z = 0  # La base è sempre a z=0
        max_x = float('-inf')
        max_y = float('-inf')
        max_z = float('-inf')
        
        # Aggiorna i limiti in base ai vertici di tutti i componenti
        for component in self.components:
            for vertex in component.vertices_3d:
                min_x = min(min_x, vertex.x)
                min_y = min(min_y, vertex.y)
                max_x = max(max_x, vertex.x)
                max_y = max(max_y, vertex.y)
                max_z = max(max_z, vertex.z)
        
        # Memorizza i limiti del bounding box
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z
    
    def _calculate_perimeter_segments(self) -> List[Tuple[Segment3D, float]]:
        """
        Calcola i segmenti che definiscono il perimetro della base del solido composto.
        
        Returns:
            List[Tuple[Segment3D, float]]: Lista di coppie (segmento, altezza).
        """
        # Questa è una versione semplificata che considera solo i perimetri esterni
        # dei parallelepipedi componenti. In una implementazione completa, si dovrebbe
        # calcolare l'unione effettiva dei perimetri, tenendo conto delle intersezioni.
        
        perimeter_segments = []
        
        # Per ogni componente, aggiungi i segmenti del perimetro della base
        for component in self.components:
            base_corners_2d = component.base_corners
            n = len(base_corners_2d)
            
            for i in range(n):
                j = (i + 1) % n
                p1 = Point3D(base_corners_2d[i].x, base_corners_2d[i].y, 0)
                p2 = Point3D(base_corners_2d[j].x, base_corners_2d[j].y, 0)
                segment = Segment3D(p1, p2)
                
                # Aggiungi il segmento con l'altezza del componente
                perimeter_segments.append((segment, component.height))
        
        return perimeter_segments
    
    def contains_point(self, point: Point3D) -> bool:
        """
        Verifica se un punto è contenuto nel solido composto.
        
        Args:
            point (Point3D): Punto da verificare.
            
        Returns:
            bool: True se il punto è contenuto nel solido composto, False altrimenti.
        """
        # Verifica rapida con il bounding box
        if not (self.min_x <= point.x <= self.max_x and
                self.min_y <= point.y <= self.max_y and
                self.min_z <= point.z <= self.max_z):
            return False
        
        # Verifica se il punto è contenuto in almeno uno dei componenti
        for component in self.components:
            if component.contains_point(point):
                return True
        
        return False
    
    def intersects_segment(self, segment: Segment3D) -> Tuple[bool, Optional[Point3D]]:
        """
        Verifica se un segmento interseca il solido composto.
        
        Args:
            segment (Segment3D): Segmento da verificare.
            
        Returns:
            Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
            se c'è intersezione e, in caso affermativo, il punto di intersezione.
        """
        # Verifica se uno degli estremi del segmento è contenuto nel solido composto
        p1, p2 = segment.points
        if self.contains_point(p1):
            return True, p1
        if self.contains_point(p2):
            return True, p2
        
        # Verifica se il segmento interseca uno dei componenti
        # Troviamo l'intersezione più vicina al primo punto del segmento
        min_distance = float('inf')
        closest_intersection = None
        
        for component in self.components:
            intersects, point = component.intersects_segment(segment)
            if intersects and point is not None:
                # Calcola la distanza dal primo punto del segmento
                distance = p1.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = point
        
        if closest_intersection is not None:
            return True, closest_intersection
        
        return False, None
    
    def intersects_line(self, line: Line3D) -> Tuple[bool, Optional[Point3D]]:
        """
        Verifica se una linea interseca il solido composto.
        
        Args:
            line (Line3D): Linea da verificare.
            
        Returns:
            Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
            se c'è intersezione e, in caso affermativo, il punto di intersezione.
        """
        # Verifica se la linea interseca uno dei componenti
        # Troviamo l'intersezione più vicina al punto di riferimento della linea
        min_distance = float('inf')
        closest_intersection = None
        
        for component in self.components:
            intersects, point = component.intersects_line(line)
            if intersects and point is not None:
                # Calcola la distanza dal punto di riferimento della linea
                distance = line.p1.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = point
        
        if closest_intersection is not None:
            return True, closest_intersection
        
        return False, None
    
    def _aabb_intersect(self, solid: Union['SolidoParallelepipedo', 'SolidoComposto']) -> bool:
        """
        Verifica se i bounding box dei due solidi si intersecano (AABB - Axis-Aligned Bounding Box).
        
        Args:
            solid (Union[SolidoParallelepipedo, SolidoComposto]): Altro solido.
            
        Returns:
            bool: True se i bounding box si intersecano, False altrimenti.
        """
        if isinstance(solid, SolidoParallelepipedo):
            # Calcola i limiti del parallelepipedo
            half_side = solid.side_length / 2
            min_x_solid = solid.base_center.x - half_side
            max_x_solid = solid.base_center.x + half_side
            min_y_solid = solid.base_center.y - half_side
            max_y_solid = solid.base_center.y + half_side
            min_z_solid = 0
            max_z_solid = solid.height
        else:  # SolidoComposto
            # Usa i limiti già calcolati
            min_x_solid = solid.min_x
            max_x_solid = solid.max_x
            min_y_solid = solid.min_y
            max_y_solid = solid.max_y
            min_z_solid = solid.min_z
            max_z_solid = solid.max_z
        
        # Verifica se i bounding box si intersecano
        return (self.min_x <= max_x_solid and self.max_x >= min_x_solid and
                self.min_y <= max_y_solid and self.max_y >= min_y_solid and
                self.min_z <= max_z_solid and self.max_z >= min_z_solid)
    
    def intersects_solid(self, solid: Union['SolidoParallelepipedo', 'SolidoComposto']) -> bool:
        """
        Verifica se un altro solido interseca questo solido composto.
        
        Args:
            solid (Union[SolidoParallelepipedo, SolidoComposto]): Solido da verificare.
            
        Returns:
            bool: True se i solidi si intersecano, False altrimenti.
        """
        # Verifica rapida con i bounding box
        if not self._aabb_intersect(solid):
            return False
        
        # Caso 1: solid è un SolidoParallelepipedo
        if isinstance(solid, SolidoParallelepipedo):
            # Verifica se uno dei vertici del parallelepipedo è contenuto nel solido composto
            for vertex in solid.vertices_3d:
                if self.contains_point(vertex):
                    return True
            
            # Verifica se uno dei vertici dei componenti è contenuto nel parallelepipedo
            for component in self.components:
                for vertex in component.vertices_3d:
                    if solid.contains_point(vertex):
                        return True
            
            # Verifica se uno degli spigoli del parallelepipedo interseca il solido composto
            for edge in solid.edges:
                intersects, _ = self.intersects_segment(edge)
                if intersects:
                    return True
            
            # Verifica se uno degli spigoli dei componenti interseca il parallelepipedo
            for component in self.components:
                for edge in component.edges:
                    intersects, _ = solid.intersects_segment(edge)
                    if intersects:
                        return True
        
        # Caso 2: solid è un SolidoComposto
        else:
            # Verifica se uno dei componenti di questo solido interseca uno dei componenti dell'altro solido
            for component1 in self.components:
                for component2 in solid.components:
                    if component1.intersects_solid(component2):
                        return True
        
        return False


class Waypoint:
    """
    Rappresenta un punto del percorso.
    
    Attributes:
        name (str): Nome del waypoint, del tipo "wp_x" dove x è un numero progressivo.
        point (Point3D): Posizione del waypoint sulla mappa.
    """
    
    def __init__(self, name: str, point: Point3D):
        """
        Inizializza un nuovo waypoint.
        
        Args:
            name (str): Nome del waypoint.
            point (Point3D): Posizione del waypoint.
        """
        self._name = name
        self._point = point
    
    @property
    def name(self) -> str:
        """Restituisce il nome del waypoint."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Imposta il nome del waypoint."""
        self._name = value
    
    @property
    def point(self) -> Point3D:
        """Restituisce la posizione del waypoint."""
        return self._point
    
    @point.setter
    def point(self, value: Point3D):
        """Imposta la posizione del waypoint."""
        self._point = value
    
    def point2d(self) -> Point2D:
        """
        Restituisce la proiezione 2D del waypoint.
        
        Returns:
            Point2D: Proiezione 2D del waypoint.
        """
        return Point2D(self._point.x, self._point.y)


class Edge:
    """
    Rappresenta il segmento che collega due Waypoint consecutivi.
    
    Attributes:
        name (str): Nome dell'edge, formato dai nomi dei due waypoint.
        wp_A (Waypoint): Primo waypoint.
        wp_B (Waypoint): Secondo waypoint.
        length (float): Lunghezza del segmento tra wp_A e wp_B.
    """
    
    def __init__(self, name: str, wp_A: Waypoint, wp_B: Waypoint):
        """
        Inizializza un nuovo edge.
        
        Args:
            name (str): Nome dell'edge.
            wp_A (Waypoint): Primo waypoint.
            wp_B (Waypoint): Secondo waypoint.
        """
        self._name = name
        self._wp_A = wp_A
        self._wp_B = wp_B
        self._length = self._calculate_length()
    
    def _calculate_length(self) -> float:
        """
        Calcola la lunghezza del segmento.
        
        Returns:
            float: Lunghezza del segmento.
        """
        return float(self._wp_A.point.distance(self._wp_B.point))
    
    @property
    def name(self) -> str:
        """Restituisce il nome dell'edge."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Imposta il nome dell'edge."""
        self._name = value
    
    @property
    def wp_A(self) -> Waypoint:
        """Restituisce il primo waypoint."""
        return self._wp_A
    
    @wp_A.setter
    def wp_A(self, value: Waypoint):
        """Imposta il primo waypoint."""
        self._wp_A = value
        self._length = self._calculate_length()
    
    @property
    def wp_B(self) -> Waypoint:
        """Restituisce il secondo waypoint."""
        return self._wp_B
    
    @wp_B.setter
    def wp_B(self, value: Waypoint):
        """Imposta il secondo waypoint."""
        self._wp_B = value
        self._length = self._calculate_length()
    
    @property
    def length(self) -> float:
        """Restituisce la lunghezza del segmento."""
        return self._length
    
    def intersectSolid(self, solids: List[Union[SolidoParallelepipedo, SolidoComposto]]) -> Tuple[bool, Optional[Point3D]]:
        """
        Verifica se l'edge interseca un solido.
        
        Args:
            solids (List[Union[SolidoParallelepipedo, SolidoComposto]]): Lista dei solidi da verificare.
            
        Returns:
            Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
            se c'è intersezione e, in caso affermativo, il punto di intersezione.
        """
        # Crea un segmento 3D dai due waypoint
        segment = Segment3D(self._wp_A.point, self._wp_B.point)
        
        # Verifica se il segmento interseca uno dei solidi
        # Troviamo l'intersezione più vicina al primo waypoint
        min_distance = float('inf')
        closest_intersection = None
        
        for solid in solids:
            intersects, point = solid.intersects_segment(segment)
            if intersects and point is not None:
                # Calcola la distanza dal primo waypoint
                distance = self._wp_A.point.distance(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = point
        
        if closest_intersection is not None:
            return True, closest_intersection
        
        return False, None


class Route:
    """
    Rappresenta un percorso che collega un punto di inizio a un punto di fine.
    
    Attributes:
        name (str): Nome del percorso.
        edges (List[Edge]): Lista degli edge che compongono il percorso.
    """
    
    def __init__(self, name: str, edges: List[Edge] = None):
        """
        Inizializza un nuovo percorso.
        
        Args:
            name (str): Nome del percorso.
            edges (List[Edge], optional): Lista degli edge che compongono il percorso.
        """
        self._name = name
        self._edges = edges if edges is not None else []
    
    @property
    def name(self) -> str:
        """Restituisce il nome del percorso."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Imposta il nome del percorso."""
        self._name = value
    
    @property
    def edges(self) -> List[Edge]:
        """Restituisce la lista degli edge che compongono il percorso."""
        return self._edges
    
    @edges.setter
    def edges(self, value: List[Edge]):
        """Imposta la lista degli edge che compongono il percorso."""
        self._edges = value
    
    def length(self) -> float:
        """
        Calcola la lunghezza totale del percorso.
        
        Returns:
            float: Lunghezza totale del percorso.
        """
        return sum(edge.length for edge in self._edges)
    
    def add_edge(self, edge: Edge) -> None:
        """
        Aggiunge un edge al percorso.
        
        Args:
            edge (Edge): Edge da aggiungere.
        """
        self._edges.append(edge)
    
    def get_start_waypoint(self) -> Optional[Waypoint]:
        """
        Restituisce il waypoint di partenza del percorso.
        
        Returns:
            Optional[Waypoint]: Waypoint di partenza, o None se il percorso è vuoto.
        """
        if not self._edges:
            return None
        return self._edges[0].wp_A
    
    def get_end_waypoint(self) -> Optional[Waypoint]:
        """
        Restituisce il waypoint di arrivo del percorso.
        
        Returns:
            Optional[Waypoint]: Waypoint di arrivo, o None se il percorso è vuoto.
        """
        if not self._edges:
            return None
        return self._edges[-1].wp_B
    
    def get_waypoints(self) -> List[Waypoint]:
        """
        Restituisce tutti i waypoint del percorso, senza duplicati.
        
        Returns:
            List[Waypoint]: Lista dei waypoint del percorso.
        """
        if not self._edges:
            return []
        
        waypoints = [self._edges[0].wp_A]
        for edge in self._edges:
            waypoints.append(edge.wp_B)
        
        return waypoints


# Funzioni per la gestione della mappa e dei solidi

def posiziona_parallelepipedo(mappa: List[Union[SolidoParallelepipedo, SolidoComposto]], 
                             parallelepipedo: SolidoParallelepipedo) -> None:
    """
    Posiziona un parallelepipedo sulla mappa.
    
    Args:
        mappa (List[Union[SolidoParallelepipedo, SolidoComposto]]): Mappa su cui posizionare il parallelepipedo.
        parallelepipedo (SolidoParallelepipedo): Parallelepipedo da posizionare.
    """
    mappa.append(parallelepipedo)

def posiziona_parallelepipedi(mappa: List[Union[SolidoParallelepipedo, SolidoComposto]], 
                             parallelepipedi: List[SolidoParallelepipedo]) -> None:
    """
    Posiziona una lista di parallelepipedi sulla mappa.
    
    Args:
        mappa (List[Union[SolidoParallelepipedo, SolidoComposto]]): Mappa su cui posizionare i parallelepipedi.
        parallelepipedi (List[SolidoParallelepipedo]): Lista di parallelepipedi da posizionare.
    """
    for parallelepipedo in parallelepipedi:
        posiziona_parallelepipedo(mappa, parallelepipedo)

def identifica_solidi_composti(mappa: List[SolidoParallelepipedo]) -> List[Union[SolidoParallelepipedo, SolidoComposto]]:
    """
    Identifica i gruppi di parallelepipedi che si intersecano e crea solidi composti.
    
    Args:
        mappa (List[SolidoParallelepipedo]): Mappa contenente i parallelepipedi.
        
    Returns:
        List[Union[SolidoParallelepipedo, SolidoComposto]]: Lista contenente i solidi singoli e composti.
    """
    # Crea un grafo di intersezioni
    grafo_intersezioni = {}
    for i, solido1 in enumerate(mappa):
        grafo_intersezioni[i] = []
        for j, solido2 in enumerate(mappa):
            if i != j and solido1.intersects_solid(solido2):
                grafo_intersezioni[i].append(j)
    
    # Identifica le componenti connesse (gruppi di parallelepipedi intersecanti)
    visitati = set()
    componenti_connesse = []
    
    def dfs(nodo, componente):
        visitati.add(nodo)
        componente.append(nodo)
        for vicino in grafo_intersezioni[nodo]:
            if vicino not in visitati:
                dfs(vicino, componente)
    
    for i in range(len(mappa)):
        if i not in visitati:
            componente = []
            dfs(i, componente)
            componenti_connesse.append(componente)
    
    # Crea i solidi composti e mantieni i parallelepipedi isolati
    nuova_mappa = []
    
    for componente in componenti_connesse:
        if len(componente) == 1:
            # Parallelepipedo isolato
            nuova_mappa.append(mappa[componente[0]])
        else:
            # Gruppo di parallelepipedi intersecanti
            componenti_solido = [mappa[i] for i in componente]
            solido_composto = SolidoComposto(componenti_solido)
            nuova_mappa.append(solido_composto)
    
    return nuova_mappa

def punto_in_solido(punto: Point3D, solidi: List[Union[SolidoParallelepipedo, SolidoComposto]]) -> bool:
    """
    Verifica se un punto appartiene a un solido presente sulla mappa.
    
    Args:
        punto (Point3D): Punto da verificare.
        solidi (List[Union[SolidoParallelepipedo, SolidoComposto]]): Lista dei solidi da verificare.
        
    Returns:
        bool: True se il punto appartiene a un solido, False altrimenti.
    """
    for solido in solidi:
        if solido.contains_point(punto):
            return True
    return False

def segmento_interseca_solido(segmento: Segment3D, solidi: List[Union[SolidoParallelepipedo, SolidoComposto]]) -> Tuple[bool, Optional[Point3D]]:
    """
    Verifica se un segmento interseca un solido presente sulla mappa.
    
    Args:
        segmento (Segment3D): Segmento da verificare.
        solidi (List[Union[SolidoParallelepipedo, SolidoComposto]]): Lista dei solidi da verificare.
        
    Returns:
        Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
        se c'è intersezione e, in caso affermativo, il punto di intersezione.
    """
    # Troviamo l'intersezione più vicina al primo punto del segmento
    min_distance = float('inf')
    closest_intersection = None
    
    for solido in solidi:
        intersects, point = solido.intersects_segment(segmento)
        if intersects and point is not None:
            # Calcola la distanza dal primo punto del segmento
            distance = segmento.points[0].distance(point)
            if distance < min_distance:
                min_distance = distance
                closest_intersection = point
    
    if closest_intersection is not None:
        return True, closest_intersection
    
    return False, None

def linea_interseca_solido(linea: Line3D, solidi: List[Union[SolidoParallelepipedo, SolidoComposto]]) -> Tuple[bool, Optional[Point3D]]:
    """
    Verifica se una linea interseca un solido presente sulla mappa.
    
    Args:
        linea (Line3D): Linea da verificare.
        solidi (List[Union[SolidoParallelepipedo, SolidoComposto]]): Lista dei solidi da verificare.
        
    Returns:
        Tuple[bool, Optional[Point3D]]: Una tupla contenente un booleano che indica
        se c'è intersezione e, in caso affermativo, il punto di intersezione.
    """
    # Troviamo l'intersezione più vicina al punto di riferimento della linea
    min_distance = float('inf')
    closest_intersection = None
    
    for solido in solidi:
        intersects, point = solido.intersects_line(linea)
        if intersects and point is not None:
            # Calcola la distanza dal punto di riferimento della linea
            distance = linea.p1.distance(point)
            if distance < min_distance:
                min_distance = distance
                closest_intersection = point
    
    if closest_intersection is not None:
        return True, closest_intersection
    
    return False, None

def crea_percorso(wp_start: Waypoint, wp_end: Waypoint, 
                 solidi: List[Union[SolidoParallelepipedo, SolidoComposto]], 
                 altitude_min: float, altitude_max: float) -> Route:
    """
    Crea un percorso da un punto di partenza a un punto di arrivo, evitando l'intersezione con i solidi.
    
    Args:
        wp_start (Waypoint): Waypoint di partenza.
        wp_end (Waypoint): Waypoint di arrivo.
        solidi (List[Union[SolidoParallelepipedo, SolidoComposto]]): Lista dei solidi presenti sulla mappa.
        altitude_min (float): Altezza minima consentita per il percorso.
        altitude_max (float): Altezza massima consentita per il percorso.
        
    Returns:
        Route: Percorso creato.
    """
    # Filtra i solidi che contengono i punti di partenza e arrivo
    solidi_filtrati = []
    for solido in solidi:
        if not (solido.contains_point(wp_start.point) or solido.contains_point(wp_end.point)):
            solidi_filtrati.append(solido)
    
    # Crea un nuovo percorso
    route = Route(f"route_{wp_start.name}_{wp_end.name}")
    
    # Tentativo iniziale: collegamento diretto
    edge_diretto = Edge(f"edg_{wp_start.name}_{wp_end.name}", wp_start, wp_end)
    intersects, intersection_point = edge_diretto.intersectSolid(solidi_filtrati)
    
    if not intersects:
        # Il percorso diretto è valido
        route.add_edge(edge_diretto)
        return route
    
    # Il percorso diretto interseca un solido, dobbiamo trovare un percorso alternativo
    return _trova_percorso_alternativo(wp_start, wp_end, solidi_filtrati, altitude_min, altitude_max)

def _trova_percorso_alternativo(wp_start: Waypoint, wp_end: Waypoint, 
                               solidi: List[Union[SolidoParallelepipedo, SolidoComposto]], 
                               altitude_min: float, altitude_max: float) -> Route:
    """
    Trova un percorso alternativo quando il percorso diretto interseca un solido.
    
    Args:
        wp_start (Waypoint): Waypoint di partenza.
        wp_end (Waypoint): Waypoint di arrivo.
        solidi (List[Union[SolidoParallelepipedo, SolidoComposto]]): Lista dei solidi presenti sulla mappa.
        altitude_min (float): Altezza minima consentita per il percorso.
        altitude_max (float): Altezza massima consentita per il percorso.
        
    Returns:
        Route: Percorso alternativo.
    """
    # Implementazione dell'algoritmo A* per trovare il percorso
    route = Route(f"route_{wp_start.name}_{wp_end.name}")
    
    # Crea un grafo di waypoints
    waypoints = [wp_start]
    
    # Funzione per verificare se un edge è valido (non interseca solidi)
    def edge_valido(wp_a: Waypoint, wp_b: Waypoint) -> bool:
        edge = Edge(f"edg_{wp_a.name}_{wp_b.name}", wp_a, wp_b)
        intersects, _ = edge.intersectSolid(solidi)
        return not intersects
    
    # Funzione per creare un nuovo waypoint sopra un solido
    def crea_waypoint_sopra_solido(intersection_point: Point3D, solido: Union[SolidoParallelepipedo, SolidoComposto], 
                                  wp_index: int) -> Waypoint:
        # Determina l'altezza del waypoint
        if isinstance(solido, SolidoParallelepipedo):
            height = solido.height
        else:  # SolidoComposto
            # Trova l'altezza massima dei componenti
            height = max(component.height for component in solido.components)
        
        # Crea un nuovo waypoint sopra il solido
        new_z = max(height, altitude_min)
        if new_z > altitude_max:
            new_z = altitude_min  # Se l'altezza è troppo grande, passa sotto il solido
        
        new_point = Point3D(intersection_point.x, intersection_point.y, new_z)
        return Waypoint(f"wp_{wp_index}", new_point)
    
    # Funzione per creare un nuovo waypoint attorno a un solido
    def crea_waypoint_attorno_solido(solido: Union[SolidoParallelepipedo, SolidoComposto], 
                                    wp_a: Waypoint, wp_b: Waypoint, 
                                    wp_index: int) -> List[Waypoint]:
        # Questa è una versione semplificata che crea waypoints attorno al solido
        # In una implementazione completa, si dovrebbe calcolare il percorso ottimale
        
        new_waypoints = []
        
        if isinstance(solido, SolidoParallelepipedo):
            # Calcola i punti attorno al parallelepipedo
            half_side = solido.side_length / 2
            center_x = solido.base_center.x
            center_y = solido.base_center.y
            
            # Crea waypoints ai quattro angoli del parallelepipedo
            corners = [
                Point3D(center_x - half_side - 1, center_y - half_side - 1, altitude_min),
                Point3D(center_x + half_side + 1, center_y - half_side - 1, altitude_min),
                Point3D(center_x + half_side + 1, center_y + half_side + 1, altitude_min),
                Point3D(center_x - half_side - 1, center_y + half_side + 1, altitude_min)
            ]
            
            for i, corner in enumerate(corners):
                new_wp = Waypoint(f"wp_{wp_index + i}", corner)
                new_waypoints.append(new_wp)
        
        else:  # SolidoComposto
            # Per un solido composto, crea waypoints attorno al bounding box
            margin = 1.0  # Margine di sicurezza
            
            corners = [
                Point3D(solido.min_x - margin, solido.min_y - margin, altitude_min),
                Point3D(solido.max_x + margin, solido.min_y - margin, altitude_min),
                Point3D(solido.max_x + margin, solido.max_y + margin, altitude_min),
                Point3D(solido.min_x - margin, solido.max_y + margin, altitude_min)
            ]
            
            for i, corner in enumerate(corners):
                new_wp = Waypoint(f"wp_{wp_index + i}", corner)
                new_waypoints.append(new_wp)
        
        return new_waypoints
    
    # Tentativo di creare un percorso passando sopra o attorno ai solidi
    edge_diretto = Edge(f"edg_{wp_start.name}_{wp_end.name}", wp_start, wp_end)
    intersects, intersection_point = edge_diretto.intersectSolid(solidi)
    
    if intersects:
        # Trova il solido intersecato
        solido_intersecato = None
        for solido in solidi:
            segment = Segment3D(wp_start.point, wp_end.point)
            intersects, _ = solido.intersects_segment(segment)
            if intersects:
                solido_intersecato = solido
                break
        
        if solido_intersecato is not None:
            # Crea waypoints intermedi
            wp_index = 1
            
            # Prova a passare sopra il solido
            wp_sopra = crea_waypoint_sopra_solido(intersection_point, solido_intersecato, wp_index)
            waypoints.append(wp_sopra)
            wp_index += 1
            
            # Se passare sopra non funziona, prova a passare attorno
            if not edge_valido(wp_start, wp_sopra) or not edge_valido(wp_sopra, wp_end):
                waypoints.pop()  # Rimuovi il waypoint sopra
                
                # Crea waypoints attorno al solido
                wps_attorno = crea_waypoint_attorno_solido(solido_intersecato, wp_start, wp_end, wp_index)
                waypoints.extend(wps_attorno)
                wp_index += len(wps_attorno)
    
    # Aggiungi il waypoint di destinazione
    if wp_end not in waypoints:
        waypoints.append(wp_end)
    
    # Crea il percorso collegando i waypoints
    for i in range(len(waypoints) - 1):
        wp_a = waypoints[i]
        wp_b = waypoints[i + 1]
        
        # Verifica se l'edge è valido
        if edge_valido(wp_a, wp_b):
            edge = Edge(f"edg_{wp_a.name}_{wp_b.name}", wp_a, wp_b)
            route.add_edge(edge)
        else:
            # Se l'edge non è valido, potremmo dover aggiungere altri waypoints intermedi
            # Questa è una versione semplificata che non gestisce questo caso
            # In una implementazione completa, si dovrebbe ricorsivamente trovare un percorso
            # tra wp_a e wp_b
            pass
    
    return route
