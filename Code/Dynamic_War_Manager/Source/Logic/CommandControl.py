"""
Class CommandControl

command and control class for the simulation of the command and control system in the simulation of the dynamic war manager

"""

from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Dynamic_War_Manager.Source.State import State
from Dynamic_War_Manager.Source.Block import Block
from Dynamic_War_Manager.Source.Military import Military
from Dynamic_War_Manager.Source.Urban import Urban
from Dynamic_War_Manager.Source.Production import Production
from Dynamic_War_Manager.Source.Storage import Storage
from Dynamic_War_Manager.Source.Transport import Transport
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Limes import Limes
from Dynamic_War_Manager.Source.Payload import Payload
from Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import STATE
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Region')

class CommandControl:    

    def __init__(self, side: str, regions: List|None, blocks: Block|None):


        self._side = side
        self._enemy_side = Utility.enemySide(side)
        self._regions = regions
        self._blocks = blocks
        self._state = {

            "morale": {},        
            "trade_balance": { "goods": {},
                            "food": {}, 
                            "energy": {}, 
                            "human resource": {"HC": {}, "HS": {}, "HB": {}, "HR": {}}
                            },        
            "military": {}
            }
        
        # check input parameters
        check_results = self.checkParam(side, regions, blocks)
        
        if not check_results:
            raise TypeError("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
    


    def checkParam(self, side = None, regions = None, blocks = None):
        
        if blocks and self.checkListOfObjects(classType = Block, objects = blocks):
            return (False, "Bad Arg: blocks must be a list of Block object")
        
        if regions and self.checkListOfObjects(classType = Region, objects = regions):
            return (False, "Bad Arg: regions must be a list of Region object")
        
        if side and not isinstance(side, str):
            return (False, "Bad Arg: side must be a string")
        
        return True


    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, value):
        if not self.checkParam(blocks = value):
            raise ValueError("Il valore deve essere una lista")

        self._blocks = value

    def addBlock(self, block):
        if isinstance(block, Block):
            self._events.append(block)
        else:
            raise ValueError("Il valore deve essere un oggetto di tipo Block")

    def getLastBlock(self):
        if self._blocks:
            return self._blocks[-1]
        else:
            raise IndexError("La lista è vuota")

    def getBlock(self, index):
        if index < len(self._blocks):
            return self.blocks[index]
        else:
            raise IndexError("Indice fuori range")

    def removeBlock(self, block):
        if block in self._blocks:
            self._blocks.remove(block)
        else:
            raise ValueError("Il blocco non esiste nella lista")

    def addRegion(self, region):
        if isinstance(region, Region):
            self._regions.append(region)
        else:
            raise ValueError("Il valore deve essere un oggetto di tipo Region")
        
    def getLastRegion(self):
        if self._regions:
            return self._regions[-1]
        else:
            raise IndexError("La lista è vuota")
        
    def getRegion(self, index):
        if index < len(self._regions):
            return self.regions[index]
        else:
            raise IndexError("Indice fuori range")
        
    def removeRegion(self, region):
        if region in self._regions:
            self._regions.remove(region)
        else:
            raise ValueError("La regione non esiste nella lista")
        
    

    # reading and loading DCS data: reading from lua table and loading to python object
    pass

    # evaluate mission result: from python object evaluate mission results
    pass

    # execute simulation for virtual mission result: execution of the simulation in relation to the mission results
    pass

    # save mission result: saving the mission results for statistical use and analysis 
    pass

    # execute tactical blocks evaluation and planning: loop of recon request to all blocks
    # recoinassance report request   
    
    def executeRecoinnassanceRequest(self):

        recons = { "side": None, "Military": None, "id": None, "reports": None }

        for side in Context.SIDE:
            recons["side"] = side
            
            for block in self.regions[side]:    

                if isinstance(block, Military):
                    recons["Military"] = block.name
                    recons["id"] = block.id
                    recons["reports"] = block.getRecon()

    """
    evaluate strategic directive: 
        parameters:
        zone 
            level of air operation: 
                interdiction (strategic strike): production, storage and transport of: goods, energy, hr, military, urban
                ground support: ground attack operation, ground defense operation
                naval support: naval attack operation, naval defense operation
                air superiority: awacs, fighter sweep, 
                air defense operation: intercept, patrol (goods, energy, hr, military, urban)
                air escort: air strike mission, air transport mission, air recon mission, ground operation, naval operation 
                air recon, 
                air transport, 
                    
            level of ground operation:
                offensive: ground attack operation: production, storage and transport of: goods, energy, hr, military, urban,
                defensive: ground defense operation, 
                maintaing: ground patrol operation,
                recon: ground recon operation: production, storage and transport of: goods, energy, hr, military, urban,
                transport: ground transport operation: production, storage and transport of: goods, energy, hr, military, urban,
                
            level of naval operation:
                offensive: naval attack operation,
                defensive: naval defense operation,
                maintaing: naval patrol operation,
                transport: naval transport operation,
                recon: naval recon operation,

            level of goods: production, storage and transport

            minimum level of goods

            level of energy: production, storage and transport

            minimum level of energy

            level of human resource
                civilian: hr
                military: hc, hs, hb
                
            minimum level of human resource


        Il modello TLC introduce un "C2 Planner" (Pianificatore di Comando e Controllo) che simula l'esecuzione di piani operativi di manovra, 
        valutando la probabilità di successo di un piano operativo e allocando risorse di terra e aeree per massimizzare la probabilità di raggiungere 
        gli obiettivi prioritari.

        Il documento descrive l'uso di algoritmi adattativi per l'allocazione delle risorse, come l'algoritmo Sequential Analytic Game Evaluation (SAGE), 
        che consente di simulare decisioni basate su obiettivi e di adattare le strategie in risposta alle informazioni disponibili.

        Questo approccio adattativo è fondamentale per rappresentare il valore dei sistemi di comando, controllo, comunicazioni, computer e intelligence (C4I) e 
        per analizzare l'impatto delle decisioni sotto incertezza.

        assegnazione riserve in relazione agli obiettivi prioritari
        assegnazione risorse in relazione agli obiettivi prioritari




        Crea in DCS ed in WM percorsi spostamenti asset

        Questi percorsi sono rappresentati dalle route e/o dagli oggetti DCS (cross point, stop point, ecc) utilizzati per identificare e localizzare gli 
        elementi importanti del percorso di spostamento (incroci, ponti, ecc)   Nel WM devono essere utilizzati per definire un grafo con: 
        
        - Nodi: costituiti dagli waypoint DCS di una route: i waypoint dovrebbero essere definiti tra due punti dove la percorribilità è possibile e nel 
        caso di offroad è in linea retta. Quindi è opportuno uilizzare anche degli oggetti statici DCS per ulteriore localizzazione e gestione del waypoint 
        ed eventualmente anche dello stato (verifica se e come DCE gestisce lo stato delle infrastrutture predefinite nelle mappe DCS)

        - Archi: il percorso definito tra due waypoint: questo percorso è caratterizzato da un livello di minaccia (aerea, terrestre), da un tempo di 
        percorrenza, dal livello di pendenza e dalla tipologia di terreno che viene utilizzata in relazione per verificare difficoltà e possibilità di 
        percorrenza di un mezzo specifico




        
    """     

    pass

    # execute strategical and tactical evaluation and planning: analysis of block reports and global situation (general status and intelligence) and block mission planning
    pass

    # writing DCS data to lua table: writing from python object to lua table
    pass