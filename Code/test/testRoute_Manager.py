"""
Modulo unit test  per modulo Route_Manager


Caratteristiche del Test Module

    Copertura Completa:

        Verifica inizializzazione waypoint e stati

        Test del calcolo della distanza con vincoli di pendenza

        Controllo operazioni sul grafo (aggiunta elementi, gestione errori)

        Verifica algoritmi di ricerca percorsi in diversi scenari

    Scenari Complessi:

        Percorsi con waypoint bloccati

        Confronto tra diversi tipi di percorso (strada/aria)

        Personalizzazione delle funzioni di peso

        Edge cases (nessun percorso, start=end)

    Verifiche di Correttezza:

        Precisione nei calcoli delle distanze

        Corretto ordinamento dei percorsi ottimali

        Gestione degli errori e casi limite

    Struttura Modulare:

        setUp() per configurazione iniziale

        Metodi di test separati per diverse funzionalità

        Assert specifici per tipo di verifica

Esecuzione dei Test

Per eseguire i test con output dettagliato:
bash
Copy

python -m unittest test_navigation.py -v

Metriche di Qualità

    Completezza: Verifica tutte le componenti principali

    Robustezza: Include test di error handling e casi limite

    Manutenibilità: Struttura modulare e chiara

    Realismo: Usa dati realistici e scenari significativi

Questo modulo garantisce che il sistema rispetti i requisiti funzionali e sia resiliente a condizioni anomale.
"""

import unittest
from math import sqrt
from Route_Manager import NavigationGraph, Waypoint, Edge

class TestNavigationSystem(unittest.TestCase):
    def setUp(self):
        # Setup comune per i test
        self.wp1 = Waypoint("A", 0, 0, 0)
        self.wp2 = Waypoint("B", 100, 0, 0)
        self.wp3 = Waypoint("C", 100, 100, 0)
        self.wp4 = Waypoint("D", 200, 0, 30)
        self.wp_blocked = Waypoint("Bloccato", 50, 0, 0, 'blocked')

        # Creazione grafo di test
        self.nav_graph = NavigationGraph()
        for wp in [self.wp1, self.wp2, self.wp3, self.wp4, self.wp_blocked]:
            self.nav_graph.add_waypoint(wp)

    def test_waypoint_initialization(self):
        self.assertEqual(self.wp1.name, "A")
        self.assertEqual(self.wp1.state, 'inactive')
        self.assertEqual(self.wp_blocked.state, 'blocked')

    def test_edge_distance_calculation(self):
        # Test percorso onroad con pendenza <10%
        edge1 = Edge(self.wp1, self.wp2, 10, 'onroad', max_speed=80)
        self.assertAlmostEqual(edge1.distance, 100.0, delta=0.1)

        # Test percorso onroad con pendenza > 10% 
        edge2 = Edge(self.wp1, self.wp4, 20, 'onroad', max_speed=60)
        horizontal = (30 * 100) / 10  # 300m (per limitare pendenza al 10%)
        expected_distance = sqrt(horizontal**2 + 30**2)
        self.assertAlmostEqual(edge2.distance, expected_distance, delta=0.1)        

        # Test percorso aereo
        edge3 = Edge(self.wp1, self.wp4, 30, 'air', max_speed=120)
        direct_distance = sqrt(200**2 + 30**2)
        self.assertAlmostEqual(edge3.distance, direct_distance, delta=0.1)

    def test_graph_operations(self):
        # Test aggiunta waypoint duplicato
        with self.assertRaises(ValueError):
            self.nav_graph.add_edge(Edge(self.wp1, Waypoint("A", 0,0,0), 0, 'road', 0))

        # Test recupero vicini escludendo bloccati
        edge = Edge(self.wp1, self.wp_blocked, 0, 'road', 0)
        self.nav_graph.add_edge(edge)
        self.assertEqual(len(self.nav_graph.get_neighbors(self.wp1)), 0)

    def test_pathfinding_scenarios(self):
        # Costruzione grafo complesso
        edge1 = Edge(self.wp1, self.wp2, 20, 'onroad', 80)
        edge2 = Edge(self.wp2, self.wp3, 80, 'offroad', 40)
        edge3 = Edge(self.wp1, self.wp3, 60, 'air', 120)
        edge4 = Edge(self.wp3, self.wp4, 10, 'onroad', 50)
        
        for edge in [edge1, edge2, edge3, edge4]:
            self.nav_graph.add_edge(edge)

        # Test percorso più sicuro
        safe_path = self.nav_graph.find_min_danger_path(self.wp1, self.wp4)
        expected_path = [self.wp1, self.wp3, self.wp4]
        self.assertEqual(safe_path, expected_path)

        # Test percorso più veloce
        fast_path = self.nav_graph.find_fastest_path(self.wp1, self.wp4)
        self.assertEqual(fast_path, [self.wp1, self.wp3, self.wp4])

        # Test percorso con waypoint bloccato
        self.wp3.state = 'blocked'
        blocked_path = self.nav_graph.find_min_danger_path(self.wp1, self.wp4)
        self.assertIsNone(blocked_path)

    def test_custom_weight_function(self):
        # Personalizzazione peso: 70% pericolo + 30% pendenza
        edge1 = Edge(self.wp1, self.wp2, 20, 'road', 80)  # Peso: 20*0.7 + 100*0.3= 44
                
        self.nav_graph.add_edge(edge1)
    
        custom_func = lambda e: 0.7*e.danger_level + 0.3*e.distance
        path = self.nav_graph.find_optimal_path(self.wp1, self.wp2, custom_func)
        self.assertEqual(path, [self.wp1, self.wp2])

    def test_edge_cases(self):
        # Test nessun percorso
        self.assertIsNone(self.nav_graph.find_min_danger_path(self.wp1, self.wp4))
        
        # Test start == end
        path = self.nav_graph.find_min_danger_path(self.wp1, self.wp1)
        self.assertEqual(path, [self.wp1])

        # Test parametri non validi
        with self.assertRaises(ValueError):
            self.nav_graph.add_edge(Edge(Waypoint("X", 0,0,0), self.wp1, 0, 'road', 0))

    def test_complex_graph_with_shared_waypoints(self):
        """Test su grafo complesso con 6 waypoint e 12 archi"""
        # Configurazione waypoints aggiuntivi
        wpA = Waypoint("A", 0, 0, 0, 'active')
        wpB = Waypoint("B", 100, 0, 10, 'active')
        wpC = Waypoint("C", 50, 50, 20, 'active')
        wpD = Waypoint("D", 150, 30, 5, 'active')
        wpE = Waypoint("E", 200, 0, 15, 'active')
        wpF = Waypoint("F", 200, 100, 0, 'active')  # Punto finale

        # Aggiunta al grafo
        for wp in [wpA, wpB, wpC, wpD, wpE, wpF]:
            self.nav_graph.add_waypoint(wp)

        # Creazione 12 archi con caratteristiche diverse
        edges = [
            # Percorsi principali onroad (basso pericolo, alta velocità)
            Edge(wpA, wpB, 20, 'onroad', 80),
            Edge(wpB, wpD, 25, 'onroad', 70),
            Edge(wpD, wpF, 30, 'onroad', 60),
            
            # Percorsi alternativi offroad (alto pericolo, bassa velocità)
            Edge(wpA, wpC, 60, 'offroad', 30),
            Edge(wpC, wpF, 70, 'offroad', 20),
            
            # Collegamenti misti
            Edge(wpB, wpC, 40, 'offroad', 40),
            Edge(wpC, wpD, 35, 'onroad', 50),
            Edge(wpD, wpE, 50, 'offroad', 35),
            Edge(wpE, wpF, 45, 'onroad', 65),
            
            # Percorsi condivisi
            Edge(wpA, wpD, 55, 'onroad', 45),  # Condivide wpD
            Edge(wpB, wpE, 60, 'offroad', 25),  # Condivide wpE
            Edge(wpC, wpE, 30, 'onroad', 55)   # Collegamento cruciale
        ]

        # route         timing          danger  min timing  min danger
        # A-B-C-D-E-F	13.2635628253	190
        # A-B-C-D-F	    8.2588625892	125
        # A-B-C-F	    12.6912280564	139
        # A-B-D-F	    3.5167140057	75          *           *
        # A-B-E-F	    6.7884615385	125
        # A-B-C-E-F	    9.1987933173	135
        # A-D-F	        4.8330672202	85
        # A-D-E-F	    8.2993059179	105
        # A-C-F	        17.3337845662	139
        # A-C-D-F	    12.9014190991	125
        # A-C-E-F	    13.8413498272	135



        for edge in edges:
            self.nav_graph.add_edge(edge)

        # Test 1: Percorso più sicuro (minimo pericolo)
        expected_safe_path = [wpA, wpB, wpD, wpF]
        safe_path = self.nav_graph.find_min_danger_path(wpA, wpF)
        self.assertEqual(safe_path, expected_safe_path, 
                       "Percorso più sicuro non corretto")

        # Test 2: Percorso più veloce (considerando distanze reali e velocità)
        expected_fast_path = [wpA, wpB, wpD, wpF]
        fast_path = self.nav_graph.find_fastest_path(wpA, wpF)
        self.assertEqual(fast_path, expected_fast_path,
                       "Percorso più veloce non corretto")

        path1 = self.nav_graph.find_min_danger_fastest_path(wpA, wpF, perc_danger=0.5, perc_time=0.5)
        expected_path1 = [wpA, wpB, wpD, wpF]
        self.assertEqual(path1, expected_path1, "Percorso misto non corretto")

        # Test 3: Blocco di un waypoint condiviso (wpD)
        wpD.state = 'blocked'
        updated_safe_path = self.nav_graph.find_min_danger_path(wpA, wpF)
        expected_updated_path = [wpA, wpB, wpE, wpF]
        self.assertEqual(updated_safe_path, expected_updated_path,
                       "Gestione waypoint bloccato non corretta")

        # Test 4: Verifica costo totale percorso
        def calculate_total_cost(path, weight_func):
            total = 0
            for i in range(len(path)-1):
                for edge in self.nav_graph.get_neighbors(path[i]):
                    if edge.end == path[i+1]:
                        total += weight_func(edge)
            return total

        wpD.state = 'active'
        # Verifica coerenza costi
        danger_cost = calculate_total_cost(expected_safe_path, lambda e: e.danger_level)
        fast_cost = calculate_total_cost(expected_fast_path, lambda e: e.distance/e.max_speed)
        
        self.assertAlmostEqual(danger_cost, 20+25+30, delta = 0.1, msg = "Costo totale pericolo non corretto")

        self.assertAlmostEqual(fast_cost, 
                             (wpA.distance_to(wpB, "2D")[0])/80 + 
                             (wpB.distance_to(wpD, "2D")[0])/70 + 
                             (wpD.distance_to(wpF, "2D")[0])/60, 
                             delta = 0.1 ,
                             msg = "Costo totale tempo non corretto")
        


    def test_find_min_danger_fastest_path(self):

        # Configurazione waypoints
        wpA = Waypoint("A", 0, 0, 0, 'active')
        wpB = Waypoint("B", 100, 0, 0, 'active')
        wpC = Waypoint("C", 50, 50, 0, 'active')
        wpD = Waypoint("D", 150, 30, 0, 'active')
        wpE = Waypoint("E", 200, 0, 0, 'active')

        # Test 1: Grafo con percorsi misti "onroad" e "offroad"
        graph1 = NavigationGraph()
        for wp in [wpA, wpB, wpC, wpD, wpE]:
            graph1.add_waypoint(wp)

        edges1 = [
            Edge(wpA, wpB, 20, 'onroad', 80),
            Edge(wpB, wpD, 25, 'onroad', 70),
            Edge(wpD, wpE, 30, 'onroad', 60),
            Edge(wpA, wpC, 60, 'offroad', 30),
            Edge(wpC, wpE, 70, 'offroad', 20),
            Edge(wpB, wpC, 40, 'offroad', 40),
            Edge(wpC, wpD, 35, 'onroad', 50)
        ]

        for edge in edges1:
            graph1.add_edge(edge)

        path1 = graph1.find_min_danger_fastest_path(wpA, wpE, perc_danger=0.5, perc_time=0.5)
        expected_path1 = [wpA, wpB, wpD, wpE]
        self.assertEqual(path1, expected_path1, "Percorso misto non corretto")

        # Test 2: Grafo con percorsi esclusivamente "air"
        graph2 = NavigationGraph()
        for wp in [wpA, wpB, wpC, wpD, wpE]:
            graph2.add_waypoint(wp)

        edges2 = [
            Edge(wpA, wpB, 10, 'air', 120),
            Edge(wpB, wpD, 15, 'air', 110),
            Edge(wpD, wpE, 20, 'air', 100),
            Edge(wpA, wpC, 30, 'air', 90),
            Edge(wpC, wpE, 40, 'air', 80),
            Edge(wpB, wpC, 25, 'air', 100),
            Edge(wpC, wpD, 35, 'air', 95)
        ]

        for edge in edges2:
            graph2.add_edge(edge)

        path2 = graph2.find_min_danger_fastest_path(wpA, wpE, perc_danger=0.5, perc_time=0.5)
        expected_path2 = [wpA, wpB, wpD, wpE]
        self.assertEqual(path2, expected_path2, "Percorso aereo non corretto")

        # Test 3: Grafo con percorsi esclusivamente "water"
        graph3 = NavigationGraph()
        for wp in [wpA, wpB, wpC, wpD, wpE]:
            graph3.add_waypoint(wp)

        edges3 = [
            Edge(wpA, wpB, 5, 'water', 50),
            Edge(wpB, wpD, 10, 'water', 45),
            Edge(wpD, wpE, 15, 'water', 40),
            Edge(wpA, wpC, 20, 'water', 35),
            Edge(wpC, wpE, 25, 'water', 30),
            Edge(wpB, wpC, 12, 'water', 40),
            Edge(wpC, wpD, 18, 'water', 38)
        ]

        for edge in edges3:
            graph3.add_edge(edge)

        path3 = graph3.find_min_danger_fastest_path(wpA, wpE, perc_danger=0.5, perc_time=0.5)
        expected_path3 = [wpA, wpB, wpD, wpE]
        self.assertEqual(path3, expected_path3, "Percorso acquatico non corretto")

if __name__ == '__main__':
    unittest.main(verbosity=2)