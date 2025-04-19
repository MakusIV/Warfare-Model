import sys
import os
import unittest
import matplotlib.pyplot as plt
import numpy as np

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Code.Dynamic_War_Manager.Air_Route_Manager import *
from Code.Dynamic_War_Manager.Cylinder import Cylinder

######################### ChatGPT #########################


# --- Inizio dei test unitari ---
class GPT_TestModule(unittest.TestCase):

    def setUp(self):
        # Definizione di punti e creazione del cilindro tramite la classe reale
        self.start_point = Point3D(0, 0, 10)
        self.end_point = Point3D(20, 20, 10)
        self.center = Point3D(10, 10, 0)
        self.bottom_center = self.center
        self.radius = 5
        self.height = 15
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        self.cylinder = Cylinder(center=self.center, radius=self.radius, height=self.height)
        # Creazione di una minaccia utilizzando il cilindro reale
        self.threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 1.0, min_detection_time = 7,  cylinder = self.cylinder)
        self.threats = [self.threat]

    def test_waypoint_equality_and_ordering(self):
        wp1 = Waypoint("A", Point3D(1, 2, 3), None)
        wp2 = Waypoint("B", Point3D(1, 2, 3), None)
        wp3 = Waypoint("C", Point3D(2, 3, 4), None)
        self.assertEqual(wp1, wp2)
        self.assertNotEqual(wp1, wp3)
        self.assertTrue(wp1 < wp3)

    def test_edge_length_and_segment(self):
        wpA = Waypoint("A", Point3D(0, 0, 10), None)
        wpB = Waypoint("B", Point3D(3, 4, 10), None)
        edge = Edge("edge1", wpA, wpB, speed=250)
        self.assertAlmostEqual(float(edge.length), 5.0)
        seg3d = edge.getSegment3D()
        self.assertEqual(seg3d.p1, wpA.point)
        self.assertEqual(seg3d.p2, wpB.point)

    def test_edge_intersects_threat(self):
        wpA = Waypoint("A", Point3D(10, 10, 10), None)
        wpB = Waypoint("B", Point3D(15, 15, 10), None)
        edge = Edge("edge_int", wpA, wpB, speed=250)
        result, params = edge.intersects_threat(self.threat)
        self.assertTrue(result)
        t_range = edge.calculate_exposure(self.threat)
        self.assertIsInstance(t_range, tuple)

    def test_route_waypoints(self):
        route = Route("TestRoute", 1000, 1000)
        wpA = Waypoint("A", Point3D(0, 0, 10), None)
        wpB = Waypoint("B", Point3D(10, 0, 10), None)
        wpC = Waypoint("C", Point3D(10, 10, 10), None)
        edge1 = Edge("edge1", wpA, wpB, speed=200)
        edge2 = Edge("edge2", wpB, wpC, speed=200)
        route.add_edge(edge1)
        route.add_edge(edge2)
        waypoints = route.getWaypoints()
        self.assertEqual(waypoints, [wpA, wpB, wpC])
        points = route.getPoints()
        self.assertEqual(points, [wpA.point, wpB.point, wpC.point])

    def test_path_and_collection(self):
        wpA = Waypoint("A", Point3D(0, 0, 10), None)
        wpB = Waypoint("B", Point3D(3, 4, 10), None)
        wpC = Waypoint("C", Point3D(6, 8, 10), None)
        edge1 = Edge("edge1", wpA, wpB, speed=250)
        edge2 = Edge("edge2", wpB, wpC, speed=250)
        path = Path([edge1, edge2])
        self.assertAlmostEqual(float(path.total_length), 10.0)
        pc = PathCollection()
        path_id = pc.add_path([edge1])
        pc.get_path(path_id).add_edge(edge2)
        pc.mark_path_completed(path_id)
        best = pc.get_best_path(max_range = 100000)
        self.assertIsNotNone(best)
        self.assertAlmostEqual(float(best.total_length), 10.0)

    def test_threat_calcMaxLenghtCrossSegment(self):
        wpA = Waypoint("A", Point3D(0, 0, 10), None)
        wpB = Waypoint("B", Point3D(20, 0, 10), None)
        segment = Segment3D(wpA.point, wpB.point)
        max_len = self.threat.calcMaxLenghtCrossSegment(aircraft_speed=250, aircraft_altitude=10, time_to_inversion=1.0, segment=segment)
        self.assertGreater(max_len, MIN_SECURE_LENGTH_EDGE)

    def test_route_planner_calcRoute_no_threats(self):
        threats = []
        planner = RoutePlanner(self.start_point, self.end_point, threats)
        route = planner.calcRoute(self.start_point, self.end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion=20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=True)
        self.assertIsNotNone(route)
        self.assertLess(sum(edge.length for edge in route.edges.values()), 1000)

    def test_route_planner_calcRoute_with_threat_escape_up(self):
        threats = [self.threat]
        planner = RoutePlanner(self.start_point, self.end_point, threats)
        route = planner.calcRoute(self.start_point, self.end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="change_up", intersecate_threat=False, consider_aircraft_altitude_route=True)
        self.assertIsNotNone(route)
        self.assertEqual(len(route.edges), 3)
        self.assertAlmostEqual(route.length, 31.60, delta=0.1)

    def test_route_planner_calcRoute_with_threat_escape_down(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 1.0, min_detection_time = 7, cylinder = cylinder)
        threats = [threat]
        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="change_down", intersecate_threat=False, consider_aircraft_altitude_route=False)
        self.assertIsNotNone(route)
        self.assertEqual(len(route.edges), 3)
        self.assertAlmostEqual(route.length, 33.32, delta=0.1)

    def test_route_planner_calcRoute_with_threat_escape_lateral(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 1.0, min_detection_time = 7, cylinder = cylinder)
        threats = [threat]
        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 

        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertGreater(len(route.edges), 1)


    def test_route_planner_calcRoute_with_2_threat_escape_lateral(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)        
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats = [threat]
        cylinder = Cylinder(center = Point3D(14, 22, 10), radius = 5, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertGreater(len(route.edges), 1)

    def test_route_planner_calcRoute_with_2_threat_escape_lateral_and_up(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 25) # height > max_aircraft_altitude -> escape lateral
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats = [threat]
        cylinder = Cylinder(center = Point3D(14, 22, 3), radius = 5, height = 15) # height < max_aircraft_altitude -> escape up
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=22,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="change_up", intersecate_threat=False, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertGreater(len(route.edges), 1)

    def test_route_planner_calcRoute_with_3_threat_escape_lateral(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)        
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats = [threat]
        cylinder = Cylinder(center = Point3D(14, 22, 10), radius = 5, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(19, 18, 7), radius = 3, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertGreater(len(route.edges), 1)


    def test_route_planner_calcRoute_with_4_threat_escape_lateral(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)        
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats = [threat]
        cylinder = Cylinder(center = Point3D(14, 22, 10), radius = 5, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(19, 18, 7), radius = 3, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(26, 21, 7), radius = 4.315, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        #self.assertGreater(len(route.edges), 1)
        self.assertEqual(len(route.edges), 5)
        self.assertAlmostEqual(route.length, 38.44, delta = 0.1)


    def test_route_planner_calcRoute_with_4_threat_escape_lateral_limited_range(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)        
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats = [threat]
        cylinder = Cylinder(center = Point3D(14, 22, 10), radius = 5, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(19, 18, 7), radius = 3, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(26, 21, 7), radius = 4.315, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7,  cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=40, aircraft_time_to_inversion = 20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)        
        self.assertEqual(len(route.edges), 5)
        self.assertAlmostEqual(route.length, 38.44, delta = 0.1)



    def test_route_planner_calcRoute_with_4_threat_over_threat_altitude(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 5)        
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7, cylinder = cylinder)
        threats = [threat]
        cylinder = Cylinder(center = Point3D(14, 22, 10), radius = 5, height = 5)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7, cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(19, 18, 7), radius = 3, height = 8)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7, cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(26, 21, 7), radius = 4.315, height = 8)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 600, min_fire_time = 5.0, min_detection_time = 7, cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=16,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=300, aircraft_speed=250,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 20, 
                                  change_alt_option="no_change", intersecate_threat=False, consider_aircraft_altitude_route=True)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertEqual(len(route.edges), 1)
        self.assertAlmostEqual(route.length, 33.30, delta = 0.1)


    def test_route_planner_calcRoute_with_1_threat_pass_throught(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 1, min_fire_time = 1.0, min_detection_time = 7,  cylinder = cylinder)
        threats = [threat]
        
        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=1.5, aircraft_speed=1,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 2, 
                                  change_alt_option="no_change", intersecate_threat=True, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 

        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertEqual(len(route.edges), 3)
        self.assertAlmostEqual(route.length, 33.38, delta = 0.1)



    def test_route_planner_calcRoute_with_3_threat_pass_throught(self):
        start_point = Point3D(0, 0, 10)
        end_point = Point3D(22, 25, 10)
        
        # Istanza del cilindro (si assume che il costruttore di Cylinder accetti questi parametri)
        cylinder = Cylinder(center = Point3D(12, 10, 10), radius = 4, height = 15)        
        # Creazione di una minaccia utilizzando il cilindro reale
        threat = ThreatAA(danger_level = 2.0, missile_speed = 1, min_fire_time = 1.0, min_detection_time = 7, cylinder = cylinder)
        threats = [threat]

        cylinder = Cylinder(center = Point3D(14, 22, 10), radius = 5, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 1, min_fire_time = 1.0, min_detection_time = 7, cylinder = cylinder)
        threats.append(threat)

        cylinder = Cylinder(center = Point3D(19, 18, 7), radius = 3, height = 15)
        threat = ThreatAA(danger_level = 4.0, missile_speed = 1, min_fire_time = 1.0, min_detection_time = 7, cylinder = cylinder)
        threats.append(threat)

        planner = RoutePlanner(start_point, end_point, threats)
        route = planner.calcRoute(start_point, end_point, threats, aircraft_altitude_route=10,
                                  aircraft_altitude_min=5, aircraft_altitude_max=20,
                                  aircraft_speed_max=1.5, aircraft_speed=1,
                                  aircraft_range_max=1000, aircraft_time_to_inversion = 2, 
                                  change_alt_option="no_change", intersecate_threat=True, consider_aircraft_altitude_route=False)
                
        points = route.getPoints() 
        
        for point in points:
            print(getFormattedPoint(point)) 
            
        self.assertEqual(points[0], start_point)
        self.assertEqual(points[-1], end_point)
        self.assertIsNotNone(route)
        self.assertGreater(len(route.edges), 1)
        #self.assertEqual(len(route.edges), 3)
        #self.assertAlmostEqual(route.length, 33.38, delta = 0.1)

######################### Claude Sonnet 3.7.2024 #########################

from unittest.mock import MagicMock, patch
import math
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
#from Code.Dynamic_War_Manager.Cylinder import Cylinder

# Assuming we have access to the module with the classes
# from your_module import ThreatAA, Waypoint, Edge, Route, Path, PathCollection, RoutePlanner, Cylinder
# For testing, we'll include mock imports

# Mock the Cylinder class for testing
class MockCylinder:
    def __init__(self, center, radius, height):
        self.center = center
        self.radius = radius
        self.height = height
        self.bottom_center = Point3D(center.x, center.y, center.z - height)
    
    def getIntersection(self, segment, tolerance=0.1):
        # Mocked implementation for testing
        return True, [Point3D(1, 1, 1), Point3D(2, 2, 2)]
    
    def innerPoint(self, point):
        # Mocked implementation for testing
        x_dist = point.x - self.center.x
        y_dist = point.y - self.center.y
        dist_2d = math.sqrt(x_dist**2 + y_dist**2)
        return dist_2d <= self.radius and self.bottom_center.z <= point.z <= self.center.z
    
    def find_chord_coordinates(self, radius, center, start, end, max_length):
        # Mocked implementation returning two points
        return Point2D(center.x - 1, center.y), Point2D(center.x + 1, center.y)
    
    def getExtendedPoints(self, segment, tolerance=0.001):
        # Mocked implementation returning two points
        c = self.center
        return Point3D(c.x + self.radius*1.5, c.y, c.z), Point3D(c.x - self.radius*1.5, c.y, c.z)


class TestThreatAA(unittest.TestCase):
    def setUp(self):
        self.center = Point3D(0, 0, 100)
        self.cylinder = Cylinder(self.center, 10, 20) #MockCylinder(self.center, 10, 20)
        self.threat = ThreatAA(5, 500, 2, self.cylinder)
        
        # Create test waypoints and edges
        self.wp_a = Waypoint("A", Point3D(-20, 0, 100), "A")
        self.wp_b = Waypoint("B", Point3D(20, 0, 100), "B")
        self.edge = Edge("test_edge", self.wp_a, self.wp_b, 200)
    
    def test_init(self):
        """Test the initialization of ThreatAA"""
        self.assertEqual(self.threat.danger_level, 5)
        self.assertEqual(self.threat.missile_speed, 500)
        self.assertEqual(self.threat.min_fire_time, 2)
        self.assertEqual(self.threat.min_altitude, 100)
        self.assertEqual(self.threat.max_altitude, 80)  # bottom_center.z
        self.assertEqual(self.threat.cylinder, self.cylinder)
    
    def test_edgeIntersect(self):
        """Test the edge intersection calculation"""
        result, intersections = self.threat.edgeIntersect(self.edge)
        self.assertTrue(result)
        self.assertEqual(len(intersections), 2)
    
    def test_innerPoint(self):
        """Test if a point is inside the threat cylinder"""
        # Point inside cylinder
        inside_point = Point3D(5, 0, 90)
        self.assertTrue(self.threat.innerPoint(inside_point, 0.1))
        
        # Point outside cylinder
        outside_point = Point3D(15, 0, 90)
        self.assertFalse(self.threat.innerPoint(outside_point, 0.1))
    
    def test_calcMaxLenghtCrossSegment(self):
        """Test calculation of maximum segment length to cross threat"""
        segment = Segment3D(self.wp_a.point, self.wp_b.point)
        max_length = self.threat.calcMaxLenghtCrossSegment(200, 100, 5, segment)
        
        # This should return a positive value since the threat can be crossed
        self.assertGreater(max_length, 0)


class TestWaypoint(unittest.TestCase):
    def test_init(self):
        """Test waypoint initialization"""
        wp = Waypoint("Test", Point3D(1, 2, 3), "WP1")
        self.assertEqual(wp.name, "Test")
        self.assertEqual(wp.point, Point3D(1, 2, 3))
        self.assertEqual(wp.point2d, Point2D(1, 2))
        self.assertEqual(wp.id, "WP1")
    
    def test_init_without_id(self):
        """Test waypoint initialization without explicit ID"""
        wp = Waypoint("Test", Point3D(1, 2, 3), None)
        self.assertEqual(wp.id, "Test")
    
    def test_comparison(self):
        """Test waypoint comparison operators"""
        wp1 = Waypoint("A", Point3D(1, 2, 3), "1")
        wp2 = Waypoint("B", Point3D(2, 3, 4), "2")
        wp3 = Waypoint("C", Point3D(1, 2, 3), "3")
        
        self.assertTrue(wp1 < wp2)
        self.assertFalse(wp2 < wp1)
        self.assertEqual(wp1, wp3)  # Same coordinates
        self.assertNotEqual(wp1, wp2)
    
    def test_hash(self):
        """Test waypoint hashing for use in dictionaries"""
        wp1 = Waypoint("A", Point3D(1, 2, 3), "1")
        wp2 = Waypoint("B", Point3D(1, 2, 3), "2")
        
        d = {wp1: "value1"}
        # Should not add wp2 as a new key since they have the same coordinates
        d[wp2] = "value2"
        
        self.assertEqual(len(d), 1)
        self.assertEqual(d[wp1], "value2")


class TestEdge(unittest.TestCase):
    def setUp(self):
        self.wp_a = Waypoint("A", Point3D(0, 0, 0), "A")
        self.wp_b = Waypoint("B", Point3D(3, 4, 0), "B")
        self.edge = Edge("Test Edge", self.wp_a, self.wp_b, 100)
        
        # Create a mock threat
        center = Point3D(1.5, 2, 0)
        cylinder = Cylinder(center, 1, 5)
        self.threat = ThreatAA(10, 500, 2, cylinder)
    
    def test_init(self):
        """Test edge initialization"""
        self.assertEqual(self.edge.name, "Test Edge")
        self.assertEqual(self.edge.wpA, self.wp_a)
        self.assertEqual(self.edge.wpB, self.wp_b)
        self.assertEqual(self.edge.speed, 100)
        self.assertEqual(self.edge.length, 5)  # 3-4-5 triangle
        self.assertEqual(self.edge.danger, 0)
    
    def test_getSegment3D(self):
        """Test getting 3D segment representation"""
        segment = self.edge.getSegment3D()
        self.assertEqual(segment.p1, self.wp_a.point)
        self.assertEqual(segment.p2, self.wp_b.point)
    
    def test_calculate_danger(self):
        """Test danger calculation when intersecting threats"""
        threats = [self.threat]
        
        # Mock the intersects_threat method to return a known result
        with patch.object(Edge, 'intersects_threat', return_value=(True, (0.2, 0.8))):
            danger = self.edge.calculate_danger(threats)
            # Expected danger = threat danger level * exposure time
            # Exposure time = exposure length / speed = (0.8-0.2)*edge.length / speed
            expected_danger = 10 * (0.8-0.2)*5/100
            self.assertAlmostEqual(danger, expected_danger)
    
    def test_intersects_threat(self):
        """Test detection of threat intersection"""
        # Test intersection - the mock cylinder will return True
        result, params = self.edge.intersects_threat(self.threat)
        self.assertTrue(result)
        self.assertTrue(len(params) == 2)
        self.assertTrue(0 <= params[0] <= 1)
        self.assertTrue(0 <= params[1] <= 1)


class TestPath(unittest.TestCase):
    def setUp(self):
        # Create test waypoints
        self.wp_a = Waypoint("A", Point3D(0, 0, 0), "A")
        self.wp_b = Waypoint("B", Point3D(3, 4, 0), "B")
        self.wp_c = Waypoint("C", Point3D(7, 7, 0), "C")
        
        # Create test edges
        self.edge1 = Edge("Edge1", self.wp_a, self.wp_b, 100)
        self.edge1.danger = 2
        
        self.edge2 = Edge("Edge2", self.wp_b, self.wp_c, 100)
        self.edge2.danger = 3
    
    def test_init(self):
        """Test path initialization"""
        path = Path([self.edge1, self.edge2])
        
        self.assertEqual(path.edges, [self.edge1, self.edge2])
        self.assertFalse(path.completed)
        self.assertEqual(path.total_length, self.edge1.length + self.edge2.length)
        self.assertEqual(path.total_danger, self.edge1.danger + self.edge2.danger)
        self.assertEqual(path.waypoints, [self.wp_a, self.wp_b, self.wp_c])
    
    def test_add_edge(self):
        """Test adding an edge to the path"""
        path = Path([self.edge1])
        
        # Initial state
        self.assertEqual(path.total_length, self.edge1.length)
        self.assertEqual(path.total_danger, self.edge1.danger)
        
        # Add second edge
        path.add_edge(self.edge2)
        
        # Check updated metrics
        self.assertEqual(path.total_length, self.edge1.length + self.edge2.length)
        self.assertEqual(path.total_danger, self.edge1.danger + self.edge2.danger)
        self.assertEqual(path.waypoints, [self.wp_a, self.wp_b, self.wp_c])
    
    def test_to_dict(self):
        """Test conversion to dictionary for serialization"""
        path = Path([self.edge1, self.edge2])
        path_dict = path.to_dict()
        
        self.assertIn('edges', path_dict)
        self.assertIn('total_length', path_dict)
        self.assertIn('total_danger', path_dict)
        self.assertIn('completed', path_dict)
        self.assertEqual(len(path_dict['edges']), 2)
        self.assertEqual(path_dict['total_length'], self.edge1.length + self.edge2.length)
        self.assertEqual(path_dict['total_danger'], self.edge1.danger + self.edge2.danger)
        self.assertFalse(path_dict['completed'])


class TestPathCollection(unittest.TestCase):
    def setUp(self):
        # Create test waypoints
        self.wp_a = Waypoint("A", Point3D(0, 0, 0), "A")
        self.wp_b = Waypoint("B", Point3D(3, 4, 0), "B")
        self.wp_c = Waypoint("C", Point3D(7, 7, 0), "C")
        
        # Create test edges
        self.edge1 = Edge("Edge1", self.wp_a, self.wp_b, 100)
        self.edge1.danger = 2
        
        self.edge2 = Edge("Edge2", self.wp_b, self.wp_c, 100)
        self.edge2.danger = 3
    
    def test_add_path(self):
        """Test adding a path to the collection"""
        collection = PathCollection()
        
        # Add empty path
        path_id1 = collection.add_path()
        self.assertEqual(path_id1, 0)
        self.assertEqual(len(collection.paths), 1)
        self.assertEqual(len(collection.get_active_paths()), 1)
        
        # Add path with initial edges
        path_id2 = collection.add_path([self.edge1, self.edge2])
        self.assertEqual(path_id2, 1)
        self.assertEqual(len(collection.paths), 2)
        self.assertEqual(len(collection.get_active_paths()), 2)
        self.assertEqual(collection.paths[path_id2].edges, [self.edge1, self.edge2])
    
    def test_get_path(self):
        """Test retrieving a path by ID"""
        collection = PathCollection()
        path_id = collection.add_path([self.edge1])
        
        path = collection.get_path(path_id)
        self.assertEqual(path.edges, [self.edge1])
        
        # Test invalid ID
        with self.assertRaises(IndexError):
            collection.get_path(99)
    
    def test_mark_path_completed(self):
        """Test marking a path as completed"""
        collection = PathCollection()
        path_id = collection.add_path([self.edge1])
        
        # Initially the path is active
        self.assertIn(collection.paths[path_id], collection.get_active_paths())
        
        # Mark as completed
        collection.mark_path_completed(path_id)
        
        # Path should be completed and not active
        self.assertTrue(collection.paths[path_id].completed)
        self.assertNotIn(collection.paths[path_id], collection.get_active_paths())
    
    def test_get_best_path(self):
        """Test getting the best path based on length and danger"""
        collection = PathCollection()
        
        # Add two paths with different metrics
        path_id1 = collection.add_path([self.edge1])  # Length: 5, Danger: 2
        path_id2 = collection.add_path([self.edge1, self.edge2])  # Length: 5+~5.7, Danger: 2+3=5
        
        # Initially no completed paths
        self.assertIsNone(collection.get_best_path(max_range=100000))
        
        # Mark both as completed
        collection.mark_path_completed(path_id1)
        collection.mark_path_completed(path_id2)
        
        # First path should be best (shorter and less dangerous)
        best_path = collection.get_best_path(max_range=100000)
        self.assertEqual(best_path, collection.paths[path_id1])


class TestRoutePlanner(unittest.TestCase):
    def setUp(self):
        # Create start and end points
        self.start = Point3D(0, 0, 100)
        self.end = Point3D(100, 100, 100)
        
        # Create a threat
        center = Point3D(50, 50, 100)
        cylinder = Cylinder(center, 20, 30)
        self.threat = ThreatAA(5, 500, 2, cylinder)
        
        # Create the route planner
        self.route_planner = RoutePlanner(self.start, self.end, [self.threat])
        
        # Set aircraft parameters
        self.aircraft_altitude_min = 70
        self.aircraft_altitude_max = 130
        self.aircraft_speed_max = 250
        self.aircraft_speed = 200
        self.aircraft_range_max = 1000
        
        # Additional waypoints for testing
        self.wp_a = Waypoint("A", self.start, "A")
        self.wp_b = Waypoint("B", self.end, "B")
        self.wp_mid = Waypoint("Mid", Point3D(25, 25, 100), "Mid")
        
        # Edge for testing
        self.edge = Edge("TestEdge", self.wp_a, self.wp_mid, self.aircraft_speed)
    
    def test_excludeThreat(self):
        """Test excluding threats that include a point"""
        # Create a list with the threat
        threats = [self.threat]
        
        # Point outside the threat - should not exclude
        outside_point = Point3D(0, 0, 100)
        result = self.route_planner.excludeThreat(threats, outside_point)
        self.assertTrue(result)
        self.assertEqual(len(threats), 1)  # Threat still in list
        
        # Point inside the threat - should exclude
        inside_point = Point3D(50, 50, 100)
        with patch.object(ThreatAA, 'innerPoint', return_value=True):
            result = self.route_planner.excludeThreat(threats, inside_point)
            self.assertTrue(result)
            self.assertEqual(len(threats), 0)  # Threat removed
    
    def test_firstThreatIntersected(self):
        """Test finding the first threat intersected by an edge"""
        # Create multiple threats
        center1 = Point3D(30, 30, 100)
        cylinder1 = MockCylinder(center1, 10, 20)
        threat1 = ThreatAA(3, 400, 1, cylinder1)
        
        center2 = Point3D(15, 15, 100)
        cylinder2 = MockCylinder(center2, 5, 10)
        threat2 = ThreatAA(2, 300, 1, cylinder2)
        
        threats = [self.threat, threat1, threat2]
        
        # Mock the edgeIntersect method to return specific results
        with patch.object(ThreatAA, 'edgeIntersect') as mock_intersect:
            # Set up mock to return different results for each threat
            def side_effect(edge):
                if mock_intersect.call_count == 1:  # First call (self.threat)
                    return False, None
                elif mock_intersect.call_count == 2:  # Second call (threat1)
                    return True, [Point3D(20, 20, 100), Point3D(40, 40, 100)]
                else:  # Third call (threat2)
                    return True, [Point3D(10, 10, 100), Point3D(20, 20, 100)]
            
            mock_intersect.side_effect = side_effect
            
            # Test finding the first threat
            first_threat = self.route_planner.firstThreatIntersected(self.edge, threats)
            self.assertEqual(first_threat, threat2)  # threat2 is closer to wp_a
    
    def test_calcPathWithoutThreat_no_threat(self):
        """Test calculating path without threats when no threats intersect"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Mock firstThreatIntersected to return no threat
        with patch.object(RoutePlanner, 'firstThreatIntersected', return_value=None):
            result = self.route_planner.calcPathWithoutThreat(
                self.start, self.end, self.end, 
                [self.threat], 0, path_collection, path_id,
                self.aircraft_altitude_min, self.aircraft_altitude_max,
                self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                "no_change", debug=False
            )
            
            # Should succeed and mark path as completed
            self.assertTrue(result)
            self.assertTrue(path_collection.paths[path_id].completed)
            self.assertEqual(len(path_collection.paths[path_id].edges), 1)
    
    def test_calcPathWithoutThreat_with_threat(self):
        """Test calculating path without threats when threats are present"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Mock firstThreatIntersected to return a threat first time, then no threat
        with patch.object(RoutePlanner, 'firstThreatIntersected') as mock_threat:
            mock_threat.side_effect = [self.threat, None]
            
            # Mock _handle_threat_avoidance to return success
            with patch.object(RoutePlanner, '_handle_threat_avoidance', return_value=True):
                result = self.route_planner.calcPathWithoutThreat(
                    self.start, self.end, self.end, 
                    [self.threat], 0, path_collection, path_id,
                    self.aircraft_altitude_min, self.aircraft_altitude_max,
                    self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                    "change", debug=False
                )
                
                # Should succeed
                self.assertTrue(result)
    
    def test_calcPathWithThreat_no_threat(self):
        """Test calculating path with threats when no threats intersect"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Mock firstThreatIntersected to return no threat
        with patch.object(RoutePlanner, 'firstThreatIntersected', return_value=None):
            result = self.route_planner.calcPathWithThreat(
                self.start, self.end, self.end, 
                [self.threat], 0, path_collection, path_id,
                self.aircraft_altitude_min, self.aircraft_altitude_max,
                self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                5, "no_change", debug=False
            )
            
            # Should succeed and mark path as completed
            self.assertTrue(result)
            self.assertTrue(path_collection.paths[path_id].completed)
            self.assertEqual(len(path_collection.paths[path_id].edges), 1)
    
    def test_calcPathWithThreat_with_crossable_threat(self):
        """Test calculating path with threats when threats can be crossed"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Mock firstThreatIntersected to return a threat
        with patch.object(RoutePlanner, 'firstThreatIntersected', return_value=self.threat):
            # Mock calcMaxLenghtCrossSegment to return a valid crossing length
            with patch.object(ThreatAA, 'calcMaxLenghtCrossSegment', return_value=50):
                # Mock _handle_threat_crossing to return success
                with patch.object(RoutePlanner, '_handle_threat_crossing', return_value=True):
                    result = self.route_planner.calcPathWithThreat(
                        self.start, self.end, self.end, 
                        [self.threat], 0, path_collection, path_id,
                        self.aircraft_altitude_min, self.aircraft_altitude_max,
                        self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                        5, "no_change", debug=False
                    )
                    
                    # Should succeed
                    self.assertTrue(result)
    
    def test_calcPathWithThreat_with_uncrossable_threat(self):
        """Test calculating path with threats when threats cannot be crossed"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Mock firstThreatIntersected to return a threat
        with patch.object(RoutePlanner, 'firstThreatIntersected', return_value=self.threat):
            # Mock calcMaxLenghtCrossSegment to return a length too small
            with patch.object(ThreatAA, 'calcMaxLenghtCrossSegment', return_value=0.05):
                # Mock _handle_threat_avoidance to return success
                with patch.object(RoutePlanner, '_handle_threat_avoidance', return_value=True):
                    result = self.route_planner.calcPathWithThreat(
                        self.start, self.end, self.end, 
                        [self.threat], 0, path_collection, path_id,
                        self.aircraft_altitude_min, self.aircraft_altitude_max,
                        self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                        5, "no_change", debug=False
                    )
                    
                    # Should succeed
                    self.assertTrue(result)
    
    def test_handle_threat_crossing(self):
        """Test handling threat crossing when it's safe to cross"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Mock calcPathWithThreat to return success
        with patch.object(RoutePlanner, 'calcPathWithThreat', return_value=True):
            result = self.route_planner._handle_threat_crossing(
                self.edge, self.threat, self.end, self.end, 
                [self.threat], 0, path_collection, path_id, 50,
                self.aircraft_altitude_min, self.aircraft_altitude_max,
                self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                "no_change", 10, False
            )
            
            # Should succeed
            self.assertTrue(result)
            # Should have added 2 edges (to crossing point and through threat)
            self.assertEqual(len(path_collection.paths[path_id].edges), 2)
    
    def test_handle_threat_avoidance_altitude_change(self):
        """Test threat avoidance by changing altitude"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Setup conditions for altitude change
        threat = self.threat
        threat.min_altitude = 60  # Below aircraft_altitude_min
        threat.max_altitude = 140  # Above aircraft_altitude_max
        
        # Mock getIntersection to return a valid intersection
        with patch.object(MockCylinder, 'getIntersection', return_value=(
            True, [MagicMock(point=Point3D(30, 30, 100))]
        )):
            # Mock calcPathWithoutThreat to return success
            with patch.object(RoutePlanner, 'calcPathWithoutThreat', return_value=True):
                result = self.route_planner._handle_threat_avoidance(
                    self.edge, threat, self.start, self.end, self.end, 
                    [threat], 0, path_collection, path_id,
                    self.aircraft_altitude_min, self.aircraft_altitude_max,
                    self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                    5, "change_up", 10, "calcPathWithoutThreat", False
                )
                
                # Should succeed
                self.assertTrue(result)
                # Should have added 1 edge for altitude change
                self.assertEqual(len(path_collection.paths[path_id].edges), 1)
    
    def test_handle_threat_avoidance_go_around(self):
        """Test threat avoidance by going around"""
        # Create a path collection for testing
        path_collection = PathCollection()
        path_id = path_collection.add_path()
        
        # Force altitude change to be impossible
        threat = self.threat
        threat.min_altitude = 100  # Same as aircraft altitude
        threat.max_altitude = 100  # Same as aircraft altitude
        
        # Mock calcPathWithoutThreat to return success for first path
        with patch.object(RoutePlanner, 'calcPathWithoutThreat', return_value=True):
            result = self.route_planner._handle_threat_avoidance(
                self.edge, threat, self.start, self.end, self.end, 
                [threat], 0, path_collection, path_id,
                self.aircraft_altitude_min, self.aircraft_altitude_max,
                self.aircraft_speed_max, self.aircraft_speed, self.aircraft_range_max,
                None, "no_change", 10, "calcPathWithoutThreat", False
            )
            
            # Should succeed
            self.assertTrue(result)
            # Should have added edges for both paths (original and alternative)
            self.assertEqual(len(path_collection.paths), 2)
    
    def test_calcRoute(self):
        """Test the main route calculation function"""
        # Create a simple scenario
        start = Point3D(0, 0, 100)
        end = Point3D(100, 100, 100)
        threats = [self.threat]
        
        # Mock excludeThreat to do nothing
        with patch.object(RoutePlanner, 'excludeThreat', return_value=True):
            # Mock calcPathWithoutThreat to return a valid path
            with patch.object(RoutePlanner, 'calcPathWithoutThreat', return_value=True):
                # Mock calcLenghtPath to return a valid length
                with patch.object(RoutePlanner, 'calcLenghtPath', return_value=500):
                    result = self.route_planner.calcRoute(
                        start, end, threats,
                        self.aircraft_altitude_min, self.aircraft_altitude_max,
                        self.aircraft_speed_max, self.aircraft_speed, 
                        self.aircraft_range_max, "change"
                    )
                    
                    # Should return a path
                    self.assertIsNotNone(result)



if __name__ == "__main__":

    # Esegui tutti i test
    # unittest.main()

    # Esegui i test specifici
    suite = unittest.TestSuite()
    # GPT Test
    if True:
        
        suite.addTest(GPT_TestModule('test_waypoint_equality_and_ordering'))
        suite.addTest(GPT_TestModule('test_edge_length_and_segment'))
        suite.addTest(GPT_TestModule('test_edge_intersects_threat'))
        suite.addTest(GPT_TestModule('test_route_waypoints'))
        suite.addTest(GPT_TestModule('test_path_and_collection'))
        """
        suite.addTest(GPT_TestModule('test_threat_calcMaxLenghtCrossSegment'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_no_threats'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_threat_escape_up'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_threat_escape_down'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_threat_escape_lateral'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_2_threat_escape_lateral'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_2_threat_escape_lateral_and_up'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_3_threat_escape_lateral'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_4_threat_escape_lateral'))
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_4_threat_escape_lateral_limited_range'))
        
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_1_threat_pass_throught'))
        
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_4_threat_over_threat_altitude'))
        """
        suite.addTest(GPT_TestModule('test_route_planner_calcRoute_with_3_threat_pass_throught'))
        
        

        


    # Claude test
    if False:

        if True:
            suite.addTest(TestThreatAA('test_init'))
            suite.addTest(TestThreatAA('test_edgeIntersect'))
            suite.addTest(TestThreatAA('test_innerPoint'))
            suite.addTest(TestThreatAA('test_calcMaxLenghtCrossSegment'))

        if False:
            suite.addTest(TestWaypoint('test_init'))
            suite.addTest(TestWaypoint('test_init_without_id'))
            suite.addTest(TestWaypoint('test_comparison'))
            suite.addTest(TestWaypoint('test_hash'))

        if False:
            suite.addTest(TestEdge('test_init'))
            suite.addTest(TestEdge('test_getSegment3D'))
            suite.addTest(TestEdge('test_calculate_danger'))
            suite.addTest(TestEdge('test_intersects_threat'))

        if False:
            suite.addTest(TestPath('test_init'))
            suite.addTest(TestPath('test_add_edge'))
            suite.addTest(TestPath('test_to_dict'))

        if False:
            suite.addTest(TestPathCollection('test_add_path'))
            suite.addTest(TestPathCollection('test_get_path'))
            suite.addTest(TestPathCollection('test_mark_path_completed'))
            suite.addTest(TestPathCollection('test_get_best_path'))

        if False:
            suite.addTest(TestRoutePlanner('test_excludeThreat'))
            suite.addTest(TestRoutePlanner('test_firstThreatIntersected'))
            suite.addTest(TestRoutePlanner('test_calcPathWithoutThreat_no_threat'))
            suite.addTest(TestRoutePlanner('test_calcPathWithoutThreat_with_threat'))
            suite.addTest(TestRoutePlanner('test_calcPathWithThreat_no_threat'))
            suite.addTest(TestRoutePlanner('test_calcPathWithThreat_with_crossable_threat'))
            suite.addTest(TestRoutePlanner('test_calcPathWithThreat_with_uncrossable_threat'))
            suite.addTest(TestRoutePlanner('test_handle_threat_crossing'))
            suite.addTest(TestRoutePlanner('test_handle_threat_avoidance_altitude_change'))
            suite.addTest(TestRoutePlanner('test_calcRoute'))

    unittest.TextTestRunner().run(suite)










def plot_2d_threats(threats):
    plt.figure(figsize=(10, 8))
    
    # Plot minacce
    colors = ['red', 'orange', 'yellow', 'purple']
    for i, threat in enumerate(threats):
        circle = plt.Circle((threat.cylinder.center.x, threat.cylinder.center.y), 
                          threat.cylinder.radius, color=colors[i], alpha=0.3,
                          label=f'ThreatAA_{i+1}')
        plt.gca().add_patch(circle)
        
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('2D Route Map')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def plot_3d_threats(threats):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot minacce
    for i, threat in enumerate(threats):
        x = threat.cylinder.center.x
        y = threat.cylinder.center.y
        z = 0
        height = threat.cylinder.height
        
        # Base del cilindro
        theta = np.linspace(0, 2*np.pi, 100)
        x_c = x + threat.cylinder.radius * np.cos(theta)
        y_c = y + threat.cylinder.radius * np.sin(theta)
        ax.plot(x_c, y_c, z, color='r', alpha=0.3)
        
        # Superficie laterale
        z_c = np.linspace(z, height, 10)
        theta, z_c = np.meshgrid(theta, z_c)
        x_c = x + threat.cylinder.radius * np.cos(theta)
        y_c = y + threat.cylinder.radius * np.sin(theta)
        ax.plot_surface(x_c, y_c, z_c, color='r', alpha=0.1)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Altitude')
    ax.set_title('3D Route Visualization')
    plt.show()

def plot_2d_route(route, threats):
    plt.figure(figsize=(10, 8))
    
    # Plot minacce
    colors = ['red', 'orange', 'yellow', 'purple']
    for i, threat in enumerate(threats):
        circle = plt.Circle((threat.cylinder.center.x, threat.cylinder.center.y), 
                          threat.cylinder.radius, color=colors[i], alpha=0.3,
                          label=f'ThreatAA_{i+1}')
        plt.gca().add_patch(circle)
    
    # Plot percorso
    waypoints = route.getWaypoints()
    x = [wp.point.x for wp in waypoints]
    y = [wp.point.y for wp in waypoints]
    plt.plot(x, y, 'bo-', linewidth=2, markersize=8, label='Route')
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('2D Route Map')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def plot_3d_route(route, threats):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot minacce
    for i, threat in enumerate(threats):
        x = threat.cylinder.center.x
        y = threat.cylinder.center.y
        z = 0
        height = threat.cylinder.height
        
        # Base del cilindro
        theta = np.linspace(0, 2*np.pi, 100)
        x_c = x + threat.cylinder.radius * np.cos(theta)
        y_c = y + threat.cylinder.radius * np.sin(theta)
        ax.plot(x_c, y_c, z, color='r', alpha=0.3)
        
        # Superficie laterale
        z_c = np.linspace(z, height, 10)
        theta, z_c = np.meshgrid(theta, z_c)
        x_c = x + threat.cylinder.radius * np.cos(theta)
        y_c = y + threat.cylinder.radius * np.sin(theta)
        ax.plot_surface(x_c, y_c, z_c, color='r', alpha=0.1)
    
    # Plot percorso
    waypoints = route.getWaypoints()
    x = [wp.point.x for wp in waypoints]
    y = [wp.point.y for wp in waypoints]
    z = [wp.point.z for wp in waypoints]
    ax.plot(x, y, z, 'bo-', linewidth=2, markersize=8)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Altitude')
    ax.set_title('3D Route Visualization')
    plt.show()

