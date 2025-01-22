#rom Code.LoggerClass import Logger
from sympy import Point3D, symbols, Eq, solve, sqrt
from sympy.geometry import Line3D, Segment3D



# LOGGING --
 
#logger = Logger(module_name = __name__, class_name = 'Hemiphere')

from sympy.geometry import Line3D, Segment3D
class Hemisphere:
    def __init__(self, center, radius):
        """
        Inizializza una semisfera superiore con centro e raggio.
        :param center: Il centro della sfera da cui è derivata la semisfera (Point3D).
        :param radius: Il raggio della sfera da cui è derivata la semisfera (float o int).
        """
        if not isinstance(center, Point3D):
            raise ValueError("Il centro deve essere un'istanza di Point3D")
        if radius <= 0:
            raise ValueError("Il raggio deve essere positivo")
        if center.z < 0:
            raise ValueError("Il centro deve trovarsi sull'asse z >= 0")
        
        self.center = center
        self.radius = radius

    def surface_area(self):
        """Calcola l'area della superficie della semisfera."""
        return 2 * 3.14159 * (self.radius**2)  # Superficie curva più base circolare

    def volume(self):
        """Calcola il volume della semisfera."""
        return (2/3) * 3.14159 * (self.radius**3)

    def is_point_inside(self, point):
        """
        Verifica se un punto è interno alla semisfera.
        :param point: Punto da verificare (Point3D).
        :return: True se interno, False altrimenti.
        """
        if point.z < self.center.z:
            return False
        distance = self.center.distance(point)
        return distance <= self.radius

    def is_point_outside(self, point):
        """
        Verifica se un punto è esterno alla semisfera.
        :param point: Punto da verificare (Point3D).
        :return: True se esterno, False altrimenti.
        """
        return not self.is_point_inside(point)

    def point_distance_to_surface(self, point):
        """
        Calcola la distanza minima tra un punto e la superficie della semisfera.
        Specifica se il punto è interno o esterno.
        """
        if point.z < self.center.z:
            return abs(point.z - self.center.z), "esterno sotto"
        
        distance = self.center.distance(point)
        if distance < self.radius:
            return self.radius - distance, "interno"
        else:
            return distance - self.radius, "esterno"

    def segment_intersection(self, segment):
        """
        Calcola i punti di intersezione tra un segmento e la superficie della semisfera.
        :param segment: Segmento (Segment3D).
        :return: Lista di punti di intersezione.
        """
        if not isinstance(segment, Segment3D):
            raise ValueError("Il segmento deve essere un'istanza di Segment3D")
        
        t = symbols('t', real=True)
        p1, p2 = segment.p1, segment.p2
        parametric_eq = p1 + t * (p2 - p1)

        x, y, z = parametric_eq
        sphere_eq = Eq((x - self.center.x)**2 + (y - self.center.y)**2 + (z - self.center.z)**2, self.radius**2)

        solutions = solve(sphere_eq, t)
        intersections = []

        for sol in solutions:
            if 0 <= sol <= 1:  # Soluzione valida sul segmento
                intersection_point = p1 + sol * (p2 - p1)
                if intersection_point.z >= self.center.z:
                    intersections.append(Point3D(*intersection_point))

        return intersections

    def line_intersection(self, line):
        """
        Calcola i punti di intersezione tra una retta e la superficie della semisfera.
        :param line: Linea (Line3D).
        :return: Lista di punti di intersezione.
        """
        if not isinstance(line, Line3D):
            raise ValueError("La linea deve essere un'istanza di Line3D")
        
        t = symbols('t', real=True)
        p1, p2 = line.p1, line.p2
        parametric_eq = p1 + t * (p2 - p1)

        x, y, z = parametric_eq
        sphere_eq = Eq((x - self.center.x)**2 + (y - self.center.y)**2 + (z - self.center.z)**2, self.radius**2)

        solutions = solve(sphere_eq, t)
        intersections = []

        for sol in solutions:
            intersection_point = p1 + sol * (p2 - p1)
            if intersection_point.z >= self.center.z:
                intersections.append(Point3D(*intersection_point))

        return intersections

    def sphere_intersection(self, other_sphere):
        """
        Determina se la semisfera interseca un'altra sfera o semisfera.
        :param other_sphere: Oggetto sfera o semisfera (Hemisphere o Sphere).
        :return: True se c'è intersezione, False altrimenti.
        """
        if not isinstance(other_sphere, (Sphere, Hemisphere)):
            raise ValueError("L'argomento deve essere un'istanza di Sphere o Hemisphere")
        
        distance = self.center.distance(other_sphere.center)
        return abs(self.radius - other_sphere.radius) <= distance <= (self.radius + other_sphere.radius)

    def equation(self):
        """Restituisce l'equazione della sfera (completa, ma valida solo per la semisfera superiore)."""
        x, y, z = symbols('x y z')
        return Eq((x - self.center.x)**2 + (y - self.center.y)**2 + (z - self.center.z)**2, self.radius**2)

    def tangents_from_external_point(self, external_point):
        """
        Calcola le tangenti alla semisfera da un punto esterno e i punti di tangenza.
        Restituisce i punti di tangenza.
        """
        if self.is_point_inside(external_point):
            raise ValueError("Il punto deve essere esterno alla semisfera")
        
        direction = external_point - self.center
        distance_to_center = self.center.distance(external_point)
        tangent_distance = sqrt(distance_to_center**2 - self.radius**2)

        t1 = self.center + (self.radius / distance_to_center) * direction
        t2 = self.center - (self.radius / distance_to_center) * direction

        # Controlla se i punti di tangenza sono validi per la semisfera superiore
        tangents = []
        for tangent in [t1, t2]:
            if tangent.z >= self.center.z:
                tangents.append(tangent)

        return tangents

# Esempio di utilizzo
"""
if __name__ == "__main__":
    center = Point3D(0, 0, 0)
    hemisphere = Hemisphere(center, 5)
    
    # Proprietà
    print("Centro:", hemisphere.center)
    print("Raggio:", hemisphere.radius)
    print("Superficie:", hemisphere.surface_area())
    print("Volume:", hemisphere.volume())

    # Intersezioni
    line = Line3D(Point3D(-10, 0, 5), Point3D(10, 0, 5))
    print("Intersezioni con una linea:", hemisphere.line_intersection(line))

    # Tangenti da punto esterno
    external_point = Point3D(10, 10, 10)
    print("Tangenti da punto esterno:", hemisphere.tangents_from_external_point(external_point))

if __name__ == "__main__":
    center1 = Point3D(0, 0, 0)
    center2 = Point3D(7, 0, 0)
    sphere1 = Sphere(center1, 5)
    sphere2 = Sphere(center2, 3)

    # Equazione della sfera
    print("Equazione della sfera:", sphere1.equation())

    # Intersezione con una linea
    line = Line3D(Point3D(-10, 0, 0), Point3D(10, 0, 0))
    print("Intersezioni con la linea:", sphere1.line_intersection(line))

    # Intersezione con un'altra sfera
    print("Intersezione tra le due sfere:", sphere1.sphere_intersection(sphere2))

    # Tangenti da un punto esterno
    external_point = Point3D(10, 10, 10)
    print("Punti di tangenza:", sphere1.tangents_from_external_point(external_point))
"""