from Code.LoggerClass import Logger
from Code.Context import STATE
from Dynamic_War_Manager.Source.Block import Block
import Utility

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')



"""
 CLASS Payload
 
 Rappresenta il tipo di dato payload utilizzato in alcune proprietà e metodi della classe Block

"""


class Payload:
    def __init__(self, goods: int = 0, energy: int = 0, hr: int = 0, hc: int = 0, hs: int = 0, hb: int = 0, parent: Block = None):
        self._goods = goods # int 
        self._energy = energy # int
        self._hr = hr # human resource: civil worker int
        self._hc = hc # human resource: military commander int
        self._hs = hs # human resource: military specialist int
        self._hb = hb # human resource: military soldier int

        # association
        
        if parent != None and not isinstance(parent, Block):
            raise TypeError("Invalid parameters! Type not valid, Block Class expected")
        
        elif parent != None:             
            parent.payload = self # set parent association with payload

        self._parent = parent # parent association



    @property        
    def parent(self):
        
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        
        if not isinstance(parent, Block):
                raise TypeError("Invalid parameters! Type not valid, Block Class expected")
                
        self._parent = parent # parent association  
        parent.payload = self # set parent association with payload