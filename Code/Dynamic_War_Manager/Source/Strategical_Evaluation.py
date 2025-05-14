"""
 MODULE Strategical_Evaluation
 
 Data and methods for strategical evaluation. Used by Lead Command & Control

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

from Utility import get_membership_label
from Dynamic_War_Manager.Source.Block import Block


#import skfuzzy as fuzz
#import numpy as np
from Dynamic_War_Manager.Source.Mil_Base import Mil_Base
from Context import BLOCK_ASSET_CATEGORY, VALUE, GROUND_MIL_BASE_VEHICLE_ASSET, GROUND_ACTION



""" 
NO, DEVE VALUTARE LE AZIONI CONSIDERANDO TRE GRAFI: QUELLO DEL CONFLITTO COSTITUITO DA BASI_MIL AMICHE E NEMICHE, QUELLO LOGISTICO
E QUELLO DELLA DIFESA DELLE INFRASTRUTTURE STRATEGICHE. 


"""

class ConflictGraph:
    def __init__(self):
        self.blocks = {}
        self.path_cache = {}
    
    def add_block(self, block: Block):
        self.blocks[block.id] = block
    
    def calculate_combat_power(self, start: Block) -> float:
        visited = set()
        total_power = 0.0
        
        def dfs(node: Block):
            nonlocal total_power
            if node.id in visited:
                return
            visited.add(node.id)
            
            if node.type == 'militare' and node.faction == start.faction:
                total_power += node.combat_power
                
            for connection in node.connections:
                dfs(connection[0])
        
        dfs(start)
        return total_power

class PrioritySystem:
    STRATEGIC_MULTIPLIER = 2.0
    
    def __init__(self, graph: ConflictGraph):
        self.graph = graph
        self.dijkstra = DijkstraModule()  # Supposto già implementato
    
    def generate_reports(self, faction: str) -> List[Report]:
        reports = []
        friendly_blocks = [b for b in self.graph.blocks.values() if b.faction == faction]
        enemy_blocks = [b for b in self.graph.blocks.values() if b.faction != faction]
        
        for friend in friendly_blocks:
            for enemy in enemy_blocks:
                if self._is_reachable(friend, enemy):
                    friend_power = self.graph.calculate_combat_power(friend)
                    enemy_power = self.graph.calculate_combat_power(enemy)
                    
                    if friend_power > enemy_power:
                        action = 'attack'
                        crit = friend_power - enemy_power
                    else:
                        action = 'defend'
                        crit = enemy_power - friend_power
                    
                    reports.append(Report(friend, enemy, action, crit))
        return reports
    
    def _is_reachable(self, source: Block, target: Block) -> bool:
        # Utilizza il modulo Dijkstra per verificare la raggiungibilità
        return self.dijkstra.shortest_path(source.id, target.id) is not None
    
    def prioritize_actions(self, reports: List[Report]) -> List[Report]:
        for report in reports:
            if report.action == 'defend' and report.source.is_strategic:
                report.adjusted_criticality *= self.STRATEGIC_MULTIPLIER
            elif report.action == 'attack' and report.target.is_strategic:
                report.adjusted_criticality *= 1.5  # Bonus per attacchi a target strategici
        
        # Usa una max-heap per ordinare per criticità
        heap = []
        for report in reports:
            heapq.heappush(heap, (-report.adjusted_criticality, report))
        
        return [heapq.heappop(heap)[1] for _ in range(len(heap))]

# Esempio di utilizzo
if __name__ == "__main__":
    # Creazione grafo
    graph = ConflictGraph()
    
    # Blocchi amici
    friend_factory = Block(1, 'produzione', 'amici', is_strategic=True)
    friend_base = Block(2, 'militare', 'amici', combat_power=100)
    friend_storage = Block(3, 'stoccaggio', 'amici', is_strategic=True)
    
    # Blocchi nemici
    enemy_base = Block(4, 'militare', 'nemici', combat_power=80)
    enemy_radar = Block(5, 'infrastruttura', 'nemici', is_strategic=True)
    
    # Collegamenti
    friend_factory.add_connection(friend_base, 'strada', 1.0)
    friend_base.add_connection(enemy_base, 'aereo', 5.0)
    friend_storage.add_connection(friend_base, 'strada', 2.0)
    
    # Aggiunta al grafo
    for b in [friend_factory, friend_base, friend_storage, enemy_base, enemy_radar]:
        graph.add_block(b)
    
    # Sistema di priorità
    ps = PrioritySystem(graph)
    reports = ps.generate_reports('amici')
    prioritized = ps.prioritize_actions(reports)
    
    # Stampa risultati
    print("Priorità delle azioni:")
    for i, action in enumerate(prioritized, 1):
        print(f"{i}. {action.action.upper()} - {action.source.type} -> {action.target.type}")
        print(f"   Criticità: {action.adjusted_criticality:.1f}\n")


"""
Caratteristiche principali:

    Struttura dati:

    Block rappresenta ogni unità con attributi e connessioni

    ConflictGraph gestisce la topologia della mappa

    Report contiene le proposte di azione

    Calcolo priorità:

    Considera sia la criticità base che l'importanza strategica

    Applica moltiplicatori per obiettivi strategici

    Usa una max-heap per l'ordinamento efficiente

    Logica avanzata:

    Calcolo ricorsivo della potenza militare aggregata

    Verifica raggiungibilità tramite modulo Dijkstra

    Bonus differenziati per attacchi/defense strategiche

    Estendibilità:

    Facile aggiungere nuovi tipi di blocchi

    Parametri configurabili (moltiplicatori strategici)

    Logica di calcolo criticità separata

Componenti da implementare:

    Modulo Dijkstra:

python
Copy

class DijkstraModule:
    def shortest_path(self, start_id: int, end_id: int) -> List[int]:
        # Implementazione algoritmo Dijkstra
        # Restituisce il percorso ottimale o None
        pass

    Ottimizzazioni:

    Caching dei percorsi calcolati

    Precalcolo delle potenze militari

    Aggiornamenti incrementali per mappe dinamiche

Questo sistema fornisce una base solida per:

    Gestire scenari complessi con molte unità

    Adattarsi a diverse strategie militari

    Integrare nuove regole di priorità

    Bilanciare offensive e difensive in modo dinamico
"""







def evaluateTacticalReport(report_list: dict) -> dict:
    """Evaluate priority of tactical reports and resource request. List ordered by priority."""
    # High probaility of attack (our asset is very weak respect wenemy force)
    # asset is very important 
    pass

def evaluateDefencePriorityZone(strategic_priority_list: dict) -> dict: #defence_priority_list
    """ Evaluate priority of strategic zone (Production Zone, Transport Line, Storage Zone ecc, Mil_Base) and resource request. List ordered by priority.
    
    strategic_infrastructure_list: block (name (id), position, area), type (production, transport, storage, mil_base, urban), importance (VH, H, M, L, VL) sorted by importance


    """

    # High probaility of attack (our asset is very weak respect wenemy force)
    # return defence_priority_list # sorted by priority
    pass

def definePriorityPatrolZone(defence_priority_list, fighter_zone_cover) -> dict:
    """ Define the priority patrol zone list for fighter aircrafts. 
        define patrol zone as set of near block covered by single patrol mission.

    """
    # return priorityPatrolZoneList
    pass

def evaluateResourceRequest(report):
    pass

def evaluateTargetPriority(target_list: list):
    """Evaluate priority of targets and resource request. List ordered by priority """
    pass


def evaluateTotalProduction(type:str, side:str): # type goods, energy, human resource
    
    for region in regions:
        region.calcRegionTotalProduction(side, type)
    # side.sum( block_prod.production() )
    pass

def evaluateStrategicPriority(block: Block): 
    pass

def evaluateTotalTransport(type:str, side:str): # type goods, energy, human resource
    # side.sum( block_trans.production() )
    pass

def evaluateLogisticLineTransport(type:str, trans_from_request, trans_to_request): # type goods, energy, human resource
    # side.sum( block_prod.production() )
    pass

def evaluateTotalStorage(type:str, side:str): # type goods, energy, human resource
    # side.sum( block_storage.production() )
    pass

def calcCombatPowerCentrum(side: str, region: Region):# type goods, energy, human resource    
    pass





