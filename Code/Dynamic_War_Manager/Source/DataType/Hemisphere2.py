#rom Code.LoggerClass import Logger
import numpy as np
import sympy as sp



# LOGGING --
 
#logger = Logger(module_name = __name__, class_name = 'Hemiphere')


class Emisphere:
    
    def __init__(self, radius, center):
        """
        Inizializza una semisfera 3D con raggio e centro.
        :param radius: Raggio della semisfera (float).
        :param center: Centro della semisfera (array o lista di 3 elementi [x0, y0, z0]).
        """
        self.radius = radius
        self.center = np.array(center)
        self.x0, self.y0, self.z0 = center

    def is_point_inside(self, point):
        """
        Verifica se un punto è interno alla semisfera.
        :param point: Punto da verificare (array o lista di 3 elementi [x, y, z]).
        :return: True se il punto è interno, False altrimenti.
        """
        x, y, z = point
        distance_squared = (x - self.x0)**2 + (y - self.y0)**2 + (z - self.z0)**2
        return distance_squared <= self.radius**2 and z >= self.z0

    def min_distance_to_surface(self, point):
        """
        Calcola la distanza minima di un punto dalla superficie della semisfera.
        :param point: Punto da valutare (array o lista di 3 elementi [x, y, z]).
        :return: Distanza minima e posizione ("interno" o "esterno").
        """
        x, y, z = point
        distance_to_center = np.sqrt((x - self.x0)**2 + (y - self.y0)**2 + (z - self.z0)**2)
        distance_to_surface = abs(distance_to_center - self.radius)
        
        if distance_to_center < self.radius and z >= self.z0:
            position = "interno"
        else:
            position = "esterno"
        
        return distance_to_surface, position

    def segment_intersection(self, segment_start, segment_end):
        """
        Calcola l'intersezione di un segmento con la superficie della semisfera.
        :param segment_start: Punto iniziale del segmento (array o lista di 3 elementi).
        :param segment_end: Punto finale del segmento (array o lista di 3 elementi).
        :return: Punto di intersezione se esiste, altrimenti None.
        """
        # Parametrizzazione del segmento: P(t) = segment_start + t * (segment_end - segment_start)
        direction = segment_end - segment_start
        t = sp.symbols('t')
        parametric_eq = segment_start + t * direction
        
        # Equazione della semisfera: (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = r^2
        sphere_eq = (parametric_eq[0] - self.x0)**2 + (parametric_eq[1] - self.y0)**2 + (parametric_eq[2] - self.z0)**2 - self.radius**2
        
        # Risolviamo l'equazione per t
        solutions = sp.solve(sp.Eq(sphere_eq, 0), t)
        
        # Filtriamo le soluzioni valide (0 <= t <= 1) e z >= z0
        intersection_points = []
        for sol in solutions:
            if 0 <= sol <= 1:
                point = segment_start + sol * direction
                if point[2] >= self.z0:
                    intersection_points.append(point)
        
        return intersection_points[0] if intersection_points else None

    def line_intersection(self, line_point, line_direction):
        """
        Calcola l'intersezione di una retta con la superficie della semisfera.
        :param line_point: Punto sulla retta (array o lista di 3 elementi).
        :param line_direction: Direzione della retta (array o lista di 3 elementi).
        :return: Lista dei punti di intersezione.
        """
        # Parametrizzazione della retta: P(t) = line_point + t * line_direction
        t = sp.symbols('t')
        parametric_eq = line_point + t * line_direction
        
        # Equazione della semisfera: (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = r^2
        sphere_eq = (parametric_eq[0] - self.x0)**2 + (parametric_eq[1] - self.y0)**2 + (parametric_eq[2] - self.z0)**2 - self.radius**2
        
        # Risolviamo l'equazione per t
        solutions = sp.solve(sp.Eq(sphere_eq, 0), t)
        
        # Filtriamo le soluzioni valide (z >= z0)
        intersection_points = []
        for sol in solutions:
            point = line_point + sol * line_direction
            if point[2] >= self.z0:
                intersection_points.append(point)
        
        return intersection_points

    def sphere_intersection(self, other_emisphere):
        """
        Verifica se due semisfere si intersecano.
        :param other_emisphere: Altra semisfera (istanza della classe Emisphere).
        :return: True se le semisfere si intersecano, False altrimenti.
        """
        distance_between_centers = np.linalg.norm(self.center - other_emisphere.center)
        return distance_between_centers <= self.radius + other_emisphere.radius

    def equation(self):
        """
        Restituisce l'equazione della semisfera nella forma: (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = r^2
        :return: Stringa rappresentante l'equazione.
        """
        return f"(x - {self.x0})^2 + (y - {self.y0})^2 + (z - {self.z0})^2 = {self.radius}^2"

    def tangent_points(self, external_point):
        """
        Calcola i tre punti di tangenza rispetto a un punto esterno dato.
        :param external_point: Punto esterno (array o lista di 3 elementi).
        :return: Lista dei punti di tangenza.
        """
        # Implementazione complessa, richiede ulteriori dettagli matematici
        pass

# Esempio di utilizzo
emisphere = Emisphere(5, [0, 0, 0])
print(emisphere.is_point_inside([1, 1, 1]))  # True
print(emisphere.min_distance_to_surface([1, 1, 1]))  # (4.0, "interno")
print(emisphere.segment_intersection(np.array([0, 0, 0]), np.array([10, 10, 10])))  # [5.0, 5.0, 5.0]
print(emisphere.line_intersection(np.array([0, 0, 0]), np.array([1, 1, 1])))  # [[5.0, 5.0, 5.0]]
print(emisphere.sphere_intersection(Emisphere(3, [2, 2, 0])))  # True
print(emisphere.equation())  # (x - 0)^2 + (y - 0)^2 + (z - 0)^2 = 5^2