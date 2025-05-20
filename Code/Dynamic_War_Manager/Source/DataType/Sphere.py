from sympy import Point3D, symbols, Eq, solve, sqrt
from sympy.geometry import Line3D, Segment3D



# LOGGING --
 
#logger = Logger(module_name = __name__, class_name = 'Sphere')

class Sphere:
    def __init__(self, center, radius):
        if not isinstance(center, Point3D):
            raise ValueError("Il centro deve essere un'istanza di Point3D")
        if radius <= 0:
            raise ValueError("Il raggio deve essere positivo")
        
        self.center = center
        self.radius = radius

    def surface_area(self):
        """Calcola l'area della superficie della sfera."""
        return 4 * 3.14159 * (self.radius**2)

    def volume(self):
        """Calcola il volume della sfera."""
        return (4/3) * 3.14159 * (self.radius**3)

    def is_point_inside(self, point):
        """Verifica se un punto è interno alla sfera."""
        distance = self.center.distance(point)
        return distance < self.radius

    def is_point_outside(self, point):
        """Verifica se un punto è esterno alla sfera."""
        distance = self.center.distance(point)
        return distance > self.radius

    def point_distance_to_surface(self, point):
        """
        Calcola la distanza minima tra un punto e la superficie della sfera.
        Specifica se il punto è interno o esterno.
        """
        distance = self.center.distance(point)
        if distance < self.radius:
            return self.radius - distance, "interno"
        else:
            return distance - self.radius, "esterno"

    def segment_intersection(self, segment):
        """Calcola i punti di intersezione tra un segmento e la superficie della sfera."""
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
                intersections.append(Point3D(*intersection_point))

        return intersections

    def line_intersection(self, line):
        """Calcola i punti di intersezione tra una retta e la superficie della sfera."""
        if not isinstance(line, Line3D):
            raise ValueError("La linea deve essere un'istanza di Line3D")
        
        t = symbols('t', real=True)
        p1, p2 = line.p1, line.p2
        parametric_eq = p1 + t * (p2 - p1)

        x, y, z = parametric_eq
        sphere_eq = Eq((x - self.center.x)**2 + (y - self.center.y)**2 + (z - self.center.z)**2, self.radius**2)

        solutions = solve(sphere_eq, t)
        intersections = [Point3D(*(p1 + sol * (p2 - p1))) for sol in solutions]

        return intersections

    def sphere_intersection(self, other_sphere):
        """Determina se la sfera interseca un'altra sfera."""
        if not isinstance(other_sphere, Sphere):
            raise ValueError("L'argomento deve essere un'istanza di Sphere")
        
        distance = self.center.distance(other_sphere.center)
        return abs(self.radius - other_sphere.radius) <= distance <= (self.radius + other_sphere.radius)

    def equation(self):
        """Restituisce l'equazione della sfera nella forma (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = r^2."""
        x, y, z = symbols('x y z')
        return Eq((x - self.center.x)**2 + (y - self.center.y)**2 + (z - self.center.z)**2, self.radius**2)

    def tangents_from_external_point(self, external_point):
        """
        Calcola le tangenti alla sfera da un punto esterno e i punti di tangenza.
        Restituisce i punti di tangenza.
        """
        if self.is_point_inside(external_point):
            raise ValueError("Il punto deve essere esterno alla sfera")
        
        direction = external_point - self.center
        distance_to_center = self.center.distance(external_point)
        tangent_distance = sqrt(distance_to_center**2 - self.radius**2)

        t1 = self.center + (self.radius / distance_to_center) * direction
        t2 = self.center - (self.radius / distance_to_center) * direction
        return [t1, t2]

# Esempio di utilizzo
"""
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