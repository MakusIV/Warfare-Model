import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.State import State
from Dynamic_War_Manager.Source.Block import Block
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Limes import Limes
from Dynamic_War_Manager.Source.Payload import Payload
from Dynamic_War_Manager.Source.Event import Event
from LoggerClass import Logger
from Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Region')

class Region:    

    def __init__(self, name: str, description: str, blocks: List[Block] = None, limes: List[Limes]=None):
            
        
        # check input parameters
        if not self.checkParam( name, description, blocks, limes ):
            raise TypeError("Bad Arg, object not istantiate - name ({0}) must be a str, description ({1}) must be a str, blocks ({2}) must be a list of Block object and limes must be a list of Limes object ({3}): ".format(type(name), type(description), type(blocks), type(limes)))

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
            return False
        if description and not isinstance(description, str):
            return False

        if blocks and self.checkListOfObjects(classType = Block, objects = blocks):
            return False 
            
        if limes and not self.checkListOfObjects(classType = Limes, objects = limes):
            return False #raise TypeError("Bad Arg: {0} limes must be a list of Limes object".format(type(limes)))
                
        return True
    
    def morale(self): # sostituisce operational()
        """calculate morale from region's members"""
        # morale = median(block.morale for block in blocks)
        # return morale
        pass
            
    def block_status(self, blockType: str):
        """report info on specific block type(Mil, Urban, Production, Storage, Transport)"""
        # as = .... 
        # return as
        pass



