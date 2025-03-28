#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test per il modulo di gestione dei percorsi in una mappa di solidi di rotazione.
"""

import unittest
import sympy as sp
from sympy.geometry import Point3D, Point2D, Line3D, Segment3D
from Code.Dynamic_War_Manager.Air_Route_Manager_Solid_Manus import (
    SolidoParallelepipedo, SolidoComposto, Waypoint, Edge, Route,
    posiziona_parallelepipedo, posiziona_parallelepipedi, identifica_solidi_composti,
    punto_in_solido, segmento_interseca_solido, linea_interseca_solido, crea_percorso
)


class TestSolidoParallelepipedo(unittest.TestCase):
    """Test per la classe SolidoParallelepipedo."""
    
    def setUp(self):
        """Inizializza i dati per i test."""
        self.base_center = Point2D(0, 0)
        self.side_length = 2.0
        self.height = 3.0
        self.parallelepipedo = SolidoParallelepipedo(self.base_center, self.side_length, self.height)
    
    def test_init(self):
        """Test per il costruttore."""
        self.assertEqual(self.parallelepipedo.base_center, self.base_center)
        self.assertEqual(self.parallelepipedo.side_length, self.side_length)
        self.assertEqual(self.parallelepipedo.height, self.height)
        self.assertEqual(len(self.parallelepipedo.base_corners), 4)
        self.assertEqual(len(self.parallelepipedo.vertices_3d), 8)
        self.assertEqual(len(self.parallelepipedo.faces), 6)
        self.assertEqual(len(self.parallelepipedo.edges), 12)
    
    def test_contains_point(self):
        """Test per il metodo contains_point."""
        # Punto all'interno
        point_inside = Point3D(0, 0, 1.5)
        self.assertTrue(self.parallelepipedo.contains_point(point_inside))
        
        # Punto all'esterno
        point_outside = Point3D(2, 2, 1.5)
        self.assertFalse(self.parallelepipedo.contains_point(point_outside))
        
        # Punto sul bordo
        point_on_edge = Point3D(1, 0, 1.5)
        self.assertTrue(self.parallelepipedo.contains_point(point_on_edge))
        
        # Punto sopra
        point_above = Point3D(0, 0, 4)
        self.assertFalse(self.parallelepipedo.contains_point(point_above))
        
        # Punto sotto
        point_below = Point3D(0, 0, -1)
        self.assertFalse(self.parallelepipedo.contains_point(point_below))
    
    def test_intersects_segment(self):
        """Test per il metodo intersects_segment."""
        # Segmento che attraversa il parallelepipedo
        segment_through = Segment3D(Point3D(-2, 0, 1.5), Point3D(2, 0, 1.5))
        intersects, point = self.parallelepipedo.intersects_segment(segment_through)
        self.assertTrue(intersects)
        self.assertIsNotNone(point)
        
        # Segmento che non interseca il parallelepipedo
        segment_outside = Segment3D(Point3D(-2, -2, 4), Point3D(2, 2, 4))
        intersects, point = self.parallelepipedo.intersects_segment(segment_outside)
        self.assertFalse(intersects)
        self.assertIsNone(point)
        
        # Segmento con un estremo all'interno del parallelepipedo
        segment_one_inside = Segment3D(Point3D(0, 0, 1.5), Point3D(3, 3, 1.5))
        intersects, point = self.parallelepipedo.intersects_segment(segment_one_inside)
        self.assertTrue(intersects)
        self.assertIsNotNone(point)
    
    def test_intersects_line(self):
        """Test per il metodo intersects_line."""
        # Linea che attraversa il parallelepipedo
        line_through = Line3D(Point3D(-2, 0, 1.5), Point3D(2, 0, 1.5))
        intersects, point = self.parallelepipedo.intersects_line(line_through)
        self.assertTrue(intersects)
        self.assertIsNotNone(point)
        
        # Linea che non interseca il parallelepipedo
        line_outside = Line3D(Point3D(-2, -2, 4), Point3D(2, 2, 4))
        intersects, point = self.parallelepipedo.intersects_line(line_outside)
        self.assertFalse(intersects)
        self.assertIsNone(point)
    
    def test_intersects_solid(self):
        """Test per il metodo intersects_solid."""
        # Parallelepipedo che interseca
        parallelepipedo_intersecting = SolidoParallelepipedo(Point2D(1, 1), 2.0, 3.0)
        self.assertTrue(self.parallelepipedo.intersects_solid(parallelepipedo_intersecting))
        
        # Parallelepipedo che non interseca
        parallelepipedo_non_intersecting = SolidoParallelepipedo(Point2D(4, 4), 2.0, 3.0)
        self.assertFalse(self.parallelepipedo.intersects_solid(parallelepipedo_non_intersecting))
        
        # Parallelepipedo adiacente
        parallelepipedo_adjacent = SolidoParallelepipedo(Point2D(2, 0), 2.0, 3.0)
        self.assertTrue(self.parallelepipedo.intersects_solid(parallelepipedo_adjacent))


class TestSolidoComposto(unittest.TestCase):
    """Test per la classe SolidoComposto."""
    
    def setUp(self):
        """Inizializza i dati per i test."""
        self.parallelepipedo1 = SolidoParallelepipedo(Point2D(0, 0), 2.0, 3.0)
        self.parallelepipedo2 = SolidoParallelepipedo(Point2D(1, 1), 2.0, 4.0)
        self.components = [self.parallelepipedo1, self.parallelepipedo2]
        self.solido_composto = SolidoComposto(self.components)
    
    def test_init(self):
        """Test per il costruttore."""
        self.assertEqual(self.solido_composto.components, self.components)
        self.assertIsNotNone(self.solido_composto.perimeter_segments)
        self.assertGreater(len(self.solido_composto.perimeter_segments), 0)
    
    def test_contains_point(self):
        """Test per il metodo contains_point."""
        # Punto all'interno del primo componente
        point_inside1 = Point3D(0, 0, 1.5)
        self.assertTrue(self.solido_composto.contains_point(point_inside1))
        
        # Punto all'interno del secondo componente
        point_inside2 = Point3D(1, 1, 2.0)
        self.assertTrue(self.solido_composto.contains_point(point_inside2))
        
        # Punto all'esterno
        point_outside = Point3D(3, 3, 1.5)
        self.assertFalse(self.solido_composto.contains_point(point_outside))
    
    def test_intersects_segment(self):
        """Test per il metodo intersects_segment."""
        # Segmento che attraversa il solido composto
        segment_through = Segment3D(Point3D(-2, 0, 1.5), Point3D(3, 0, 1.5))
        intersects, point = self.solido_composto.intersects_segment(segment_through)
        self.assertTrue(intersects)
        self.assertIsNotNone(point)
        
        # Segmento che non interseca il solido composto
        segment_outside = Segment3D(Point3D(-2, -2, 5), Point3D(2, -2, 5))
        intersects, point = self.solido_composto.intersects_segment(segment_outside)
        self.assertFalse(intersects)
        self.assertIsNone(point)
    
    def test_intersects_solid(self):
        """Test per il metodo intersects_solid."""
        # Parallelepipedo che interseca
        parallelepipedo_intersecting = SolidoParallelepipedo(Point2D(2, 0), 2.0, 3.0)
        self.assertTrue(self.solido_composto.intersects_solid(parallelepipedo_intersecting))
        
        # Parallelepipedo che non interseca
        parallelepipedo_non_intersecting = SolidoParallelepipedo(Point2D(4, 4), 2.0, 3.0)
        self.assertFalse(self.solido_composto.intersects_solid(parallelepipedo_non_intersecting))
        
        # Altro solido composto che interseca
        other_components = [
            SolidoParallelepipedo(Point2D(2, 0), 2.0, 3.0),
            SolidoParallelepipedo(Point2D(3, 1), 2.0, 4.0)
        ]
        other_solido_composto = SolidoComposto(other_components)
        self.assertTrue(self.solido_composto.intersects_solid(other_solido_composto))


class TestWaypointEdgeRoute(unittest.TestCase):
    """Test per le classi Waypoint, Edge e Route."""
    
    def setUp(self):
        """Inizializza i dati per i test."""
        self.wp1 = Waypoint("wp_1", Point3D(0, 0, 0))
        self.wp2 = Waypoint("wp_2", Point3D(3, 4, 0))
        self.wp3 = Waypoint("wp_3", Point3D(6, 8, 0))
        
        self.edge1 = Edge("edg_1_2", self.wp1, self.wp2)
        self.edge2 = Edge("edg_2_3", self.wp2, self.wp3)
        
        self.route = Route("route_1_3", [self.edge1, self.edge2])
    
    def test_waypoint(self):
        """Test per la classe Waypoint."""
        self.assertEqual(self.wp1.name, "wp_1")
        self.assertEqual(self.wp1.point, Point3D(0, 0, 0))
        self.assertEqual(self.wp1.point2d(), Point2D(0, 0))
        
        # Test setter
        self.wp1.name = "wp_new"
        self.assertEqual(self.wp1.name, "wp_new")
        
        self.wp1.point = Point3D(1, 1, 1)
        self.assertEqual(self.wp1.point, Point3D(1, 1, 1))
    
    def test_edge(self):
        """Test per la classe Edge."""
        self.assertEqual(self.edge1.name, "edg_1_2")
        self.assertEqual(self.edge1.wp_A, self.wp1)
        self.assertEqual(self.edge1.wp_B, self.wp2)
        self.assertEqual(self.edge1.length, 5.0)  # sqrt(3^2 + 4^2) = 5.0
        
        # Test setter
        self.edge1.name = "edg_new"
        self.assertEqual(self.edge1.name, "edg_new")
        
        old_wp_A = self.edge1.wp_A
        self.edge1.wp_A = self.wp3
        self.assertEqual(self.edge1.wp_A, self.wp3)
        # Dopo aver cambiato wp_A, la lunghezza dovrebbe essere diversa da 5.0
        self.assertNotEqual(self.edge1.length, 5.0, "La lunghezza dovrebbe essere cambiata dopo aver modificato wp_A")
        
        # Ripristina per i test successivi
        self.edge1.wp_A = old_wp_A
    
    def test_route(self):
        """Test per la classe Route."""
        self.assertEqual(self.route.name, "route_1_3")
        self.assertEqual(len(self.route.edges), 2)
        self.assertEqual(self.route.length(), 10.0)  # Lunghezza totale dei due edge
        
        # Test setter
        self.route.name = "route_new"
        self.assertEqual(self.route.name, "route_new")
        
        # Test add_edge
        wp4 = Waypoint("wp_4", Point3D(9, 12, 0))
        edge3 = Edge("edg_3_4", self.wp3, wp4)
        self.route.add_edge(edge3)
        self.assertEqual(len(self.route.edges), 3)
        
        # Test get_waypoints
        waypoints = self.route.get_waypoints()
        self.assertEqual(len(waypoints), 4)
        self.assertEqual(waypoints[0], self.wp1)
        self.assertEqual(waypoints[-1], wp4)
        
        # Test get_start_waypoint e get_end_waypoint
        self.assertEqual(self.route.get_start_waypoint(), self.wp1)
        self.assertEqual(self.route.get_end_waypoint(), wp4)


class TestFunzioniMappa(unittest.TestCase):
    """Test per le funzioni di gestione della mappa."""
    
    def setUp(self):
        """Inizializza i dati per i test."""
        self.mappa = []
        self.p1 = SolidoParallelepipedo(Point2D(0, 0), 2.0, 3.0)
        self.p2 = SolidoParallelepipedo(Point2D(1, 1), 2.0, 4.0)
        self.p3 = SolidoParallelepipedo(Point2D(5, 5), 2.0, 3.0)
    
    def test_posiziona_parallelepipedo(self):
        """Test per la funzione posiziona_parallelepipedo."""
        posiziona_parallelepipedo(self.mappa, self.p1)
        self.assertEqual(len(self.mappa), 1)
        self.assertEqual(self.mappa[0], self.p1)
    
    def test_posiziona_parallelepipedi(self):
        """Test per la funzione posiziona_parallelepipedi."""
        posiziona_parallelepipedi(self.mappa, [self.p1, self.p2, self.p3])
        self.assertEqual(len(self.mappa), 3)
        self.assertEqual(self.mappa[0], self.p1)
        self.assertEqual(self.mappa[1], self.p2)
        self.assertEqual(self.mappa[2], self.p3)
    
    def test_identifica_solidi_composti(self):
        """Test per la funzione identifica_solidi_composti."""
        mappa_parallelepipedi = [self.p1, self.p2, self.p3]
        nuova_mappa = identifica_solidi_composti(mappa_parallelepipedi)
        
        # Dovremmo avere 2 solidi: un SolidoComposto (p1 e p2 si intersecano) e un SolidoParallelepipedo (p3)
        self.assertEqual(len(nuova_mappa), 2)
        
        # Verifica che ci sia un SolidoComposto
        solidi_composti = [s for s in nuova_mappa if isinstance(s, SolidoComposto)]
        self.assertEqual(len(solidi_composti), 1)
        
        # Verifica che ci sia un SolidoParallelepipedo
        parallelepipedi = [s for s in nuova_mappa if isinstance(s, SolidoParallelepipedo)]
        self.assertEqual(len(parallelepipedi), 1)
        self.assertEqual(parallelepipedi[0], self.p3)
    
    def test_punto_in_solido(self):
        """Test per la funzione punto_in_solido."""
        mappa = [self.p1, self.p3]
        
        # Punto all'interno del primo solido
        self.assertTrue(punto_in_solido(Point3D(0, 0, 1.5), mappa))
        
        # Punto all'interno del secondo solido
        self.assertTrue(punto_in_solido(Point3D(5, 5, 1.5), mappa))
        
        # Punto all'esterno
        self.assertFalse(punto_in_solido(Point3D(3, 3, 1.5), mappa))
    
    def test_segmento_interseca_solido(self):
        """Test per la funzione segmento_interseca_solido."""
        mappa = [self.p1, self.p3]
        
        # Segmento che interseca il primo solido
        segment1 = Segment3D(Point3D(-2, 0, 1.5), Point3D(2, 0, 1.5))
        intersects, point = segmento_interseca_solido(segment1, mappa)
        self.assertTrue(intersects)
        self.assertIsNotNone(point)
        
        # Segmento che non interseca alcun solido
        segment2 = Segment3D(Point3D(2.5, 2.5, 1.5), Point3D(4, 4, 1.5))
        intersects, point = segmento_interseca_solido(segment2, mappa)
        self.assertFalse(intersects)
        self.assertIsNone(point)


class TestAlgoritmoDiPercorso(unittest.TestCase):
    """Test per l'algoritmo di creazione del percorso."""
    
    def setUp(self):
        """Inizializza i dati per i test."""
        self.mappa = []
        self.p1 = SolidoParallelepipedo(Point2D(0, 0), 2.0, 3.0)
        self.p2 = SolidoParallelepipedo(Point2D(5, 5), 2.0, 3.0)
        posiziona_parallelepipedi(self.mappa, [self.p1, self.p2])
        
        self.wp_start = Waypoint("wp_start", Point3D(-3, -3, 0))
        self.wp_end = Waypoint("wp_end", Point3D(8, 8, 0))
        
        self.altitude_min = 0.0
        self.altitude_max = 5.0
    
    def test_percorso_diretto(self):
        """Test per un percorso diretto senza ostacoli."""
        # Waypoints che non attraversano solidi
        wp_start = Waypoint("wp_start", Point3D(-3, -3, 0))
        wp_end = Waypoint("wp_end", Point3D(-1, -1, 0))
        
        route = crea_percorso(wp_start, wp_end, self.mappa, self.altitude_min, self.altitude_max)
        
        # Dovremmo avere un solo edge
        self.assertEqual(len(route.edges), 1)
        self.assertEqual(route.edges[0].wp_A, wp_start)
        self.assertEqual(route.edges[0].wp_B, wp_end)
    
    def test_percorso_con_ostacoli(self):
        """Test per un percorso che deve evitare ostacoli."""
        route = crea_percorso(self.wp_start, self.wp_end, self.mappa, self.altitude_min, self.altitude_max)
        
        # Dovremmo avere più di un edge
        self.assertGreater(len(route.edges), 1)
        
        # Verifica che il percorso inizi e finisca nei punti corretti
        self.assertEqual(route.get_start_waypoint(), self.wp_start)
        self.assertEqual(route.get_end_waypoint(), self.wp_end)
        
        # Verifica che nessun edge intersechi un solido
        for edge in route.edges:
            segment = Segment3D(edge.wp_A.point, edge.wp_B.point)
            intersects, _ = segmento_interseca_solido(segment, self.mappa)
            self.assertFalse(intersects)
    
    def test_percorso_con_punto_in_solido(self):
        """Test per un percorso con un punto all'interno di un solido."""
        # Waypoint di partenza all'interno di un solido
        wp_start_in_solido = Waypoint("wp_start_in", Point3D(0, 0, 1.5))
        
        route = crea_percorso(wp_start_in_solido, self.wp_end, self.mappa, self.altitude_min, self.altitude_max)
        
        # Verifica che il percorso inizi e finisca nei punti corretti
        self.assertEqual(route.get_start_waypoint(), wp_start_in_solido)
        self.assertEqual(route.get_end_waypoint(), self.wp_end)
        
        # Verifica che nessun edge intersechi un solido (escluso quello che contiene il punto di partenza)
        for edge in route.edges:
            segment = Segment3D(edge.wp_A.point, edge.wp_B.point)
            intersects, _ = segmento_interseca_solido(segment, [self.p2])  # Escludiamo p1 che contiene il punto di partenza
            self.assertFalse(intersects)


if __name__ == '__main__':
    unittest.main()
