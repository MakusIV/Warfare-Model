from Code import Context
import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.State import State
from Dynamic_War_Manager.Source.Block import Block
from Dynamic_War_Manager.Source.Block import Mil_Base
from Dynamic_War_Manager.Source.Block import Urban
from Dynamic_War_Manager.Source.Block import Production
from Dynamic_War_Manager.Source.Block import Storage
from Dynamic_War_Manager.Source.Block import Transport
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Limes import Limes
from Dynamic_War_Manager.Source.Payload import Payload
from Dynamic_War_Manager.Source.Event import Event
from LoggerClass import Logger
from Context import STATE, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Region')

class Region:    

    def __init__(self, name: str, description: str, blocks: List[Block] = None, limes: List[Limes]=None):
            
        
        # check input parameters
        check_results = self.checkParam( name, description, blocks, limes )
        
        if not check_results:
            raise TypeError("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
            

        # propriety
        self._name = name # block name - type str
        self._description = description # block description - type str               
        self._limes = limes # list of limes of the Region - type List[Limes]

        # Association                
        self._blocks = blocks # list of Block members of Region - type List[Block]
        # NOTA: I BLOCKS CONSENTITI SONO MIL_ZONE, STORAGE
                    
    # methods

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):

        if not self.checkParam(name = value):
            raise TypeError("Invalid parameters! Type not valid, str type expected")

        self._name = value    
        return True
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):

        if not self.checkParam(description = value):
            raise TypeError("Invalid parameters! Type not valid, str type expected")
        
        self._description = value
            
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


    def getEnemyBlocks(self, enemy_side: str):
        
        """
        Return a list of Blocks of the Region that have the same side as the enemy_side parameter
        :param enemy_side: the side of the enemy
        :return: a list of Blocks
        """
        enemy_blocks = [block for block in self._blocks if block.side == enemy_side]
        return enemy_blocks

    def to_string(self):
        return 'Name: {0}  -  Id: {1}'.format(self.getName(), str(self._id))
    
    def checkClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        return type(object) == type(self)
        

    def checkClassList(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""
        return all(type(obj) == type(self) for obj in objects)

    def checkListOfObjects(self, classType: type, objects: List) -> bool: 
        """ Return True if objects is a list of classType object otherwise False"""
        return isinstance(objects, List) and not all(isinstance(obj, classType) for obj in objects )
    

    def checkParam(self, name: str, description: str, blocks: List[Block], limes: List[Limes]) -> bool:
        """Return True if type compliance of the parameters is verified"""   

        if name and not isinstance(name, str):
            return (False, "Bad Arg: side must be a str with value: Blue, Red or Neutral")
        
        if description and not isinstance(description, str):
            return (False, "Bad Arg: description must be a str")
        
        if blocks and self.checkListOfObjects(classType = Block, objects = blocks):
            return (False, "Bad Arg: blocks must be a list of Block object")
        
        if limes and not self.checkListOfObjects(classType = Limes, objects = limes):
            return (False, "Bad Arg: limes must be a list of Limes object")
                
        return True
    
    def morale(self): # sostituisce operational()
        """calculate morale from region's members"""
        # morale = median(block.morale for block in blocks)
        # return morale
        pass
            
    def block_status(self, blockCategory: str):
        """report info on specific block type(Mil, Urban, Production, Storage, Transport)"""
        # as = .... 
        # return as
        pass

    def getBlocks(self, blockCategory: str, side: str) -> List[Block]:
        """ Return a list of blocks of a specific category and side"""

        if blockCategory not in Context.BLOCK_CATEGORY:
            raise ValueError(f"Invalid block category {0}. block category must be: {1}".format(blockCategory, Context.BLOCK_CATEGORY))
        
        if blockCategory == "Logistic":
            return [block for block in self._blocks if any(isinstance(block, Production), isinstance(block, Storage), isinstance(block, Transport)) and block.side == side]
        
        if blockCategory == "Civilian":
            return [block for block in self._blocks if isinstance(block, Urban) and block.side == side]
        
        if blockCategory == "Military":
            return [block for block in self._blocks if isinstance(block, Mil_Base) and block.side == side]


    def calcRegionStrategicLogisticCenter(self, side: str): # inserire in region?
        
        logistic_blocks = self.getBlocks("Logistic", side)
        
        # escludo le mil_base in quanto tot_RSP è utilizzato per valutare la copertura da richiedere alle mil_base per la protezione di questi blocchi    
        n = len(logistic_blocks)
        tot_RSP, tp = 0, 0 # tot_RSP: summmatory of strategic logistic block priority

        for block in logistic_blocks:
            tot_RSP += block.priority 
            tp += block.position * block.priority 
        
        r_SLP = tp / (n * tot_RSP) # r_SLP: region strategic logistic center position for side blocks
        return r_SLP
    
    def calcRegionCombatPowerCenter(self, side: str): # inserire in region?
        
        military_blocks = self.getBlocks("Military", side)
                
        n = len(military_blocks)
        tot_CP, tp = 0, 0 # tot_CP: summmatory of strategic block combat power

        for block in military_blocks:
            tot_CP += block.combat_power
            tp += block.position * block.combat_power 
        
        r_CPP = tp / (n * tot_CP) # r_CPP: region strategic combat power center position for side blocks
        return r_CPP


    def calcRegionTotalProduction(self, side: str, type: str):
        """ Return the total production of a specific type of goods, energy, human resource"""
        # side.sum( block_prod.production() )
        pass

    def calcRegionTotalCombatPower(self, side: str):
        """ Return the total combat power of the Region"""
        # side.sum( block.combat_power() )
        pass

    def calcRegionTotalStorage(self, side: str, type: str):
        """ Return the total storage of the Region"""
        # side.sum( block.storage() )
        pass

    def calcRegionTotalConsumed(self, side: str, type: str):
        """ Return the total consumed of the Region"""
        # side.sum( block.consumed() )
        pass        

    def calcRegionTotalTransport(self, side: str, type: str):
        """ Return the total transport of the Region"""
        # side.sum( block.transport() )