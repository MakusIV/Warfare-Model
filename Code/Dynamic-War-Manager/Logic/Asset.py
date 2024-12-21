from Block import Block
from Utility import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Payload import Payload
from Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Asset')

# ASSET
class Asset(Block) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point = None, volume: Volume = None, threat: Threat = None, crytical: bool = False, repair_time: int = 0):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload)

            # propriety             
            self._position = position # asset position - type Point (3D -> anche l'altezza deve essere considerata per la presenza di rilievi nel terreno)
            self._cost = cost # asset cost - type int 
            self._crytical = crytical 
            self._repair_time = repair_time

    
            # Association    
            self._volume = volume
            self._threat = threat
            self._block = block # asset block - component of Block - type Block asset not exist without block

            if not name:
                self._name = Utility.setName('Unnamed_Block')

            else:
                self._name = "Block." + name

            self._id = Utility.setId(self._name)
           
            if not acp:
                acp = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)
            
            if not rcp:
                rcp = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)

            if not payload:
                payload = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)

             # check input parameters
            if not self.checkParam( name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time ):    
                raise Exception("Invalid parameters! Object not istantiate.")

    # methods

    @property
    def cost(self) -> int: #override      
        return self._cost

    @cost.setter
    def cost(self, cost) -> bool: #override
        
        if not isinstance(cost, int):
            raise Exception("Invalid parameters! Type not valid, int expected")        
        self._cost = cost
        return True
    
    @property
    def crytical(self) -> int: #override      
        return self._crytical

    @crytical.setter
    def crytical(self, crytical) -> bool: #override
        
        if not isinstance(crytical, bool):
            raise Exception("Invalid parameters! Type not valid, bool expected")        
        self._crytical = crytical
        return True
    
    @property
    def repair_time(self) -> int: #override      
        return self._repair_time

    @repair_time.setter
    def repair_time(self, repair_time) -> bool: #override
        
        if not isinstance(repair_time, int):
            raise Exception("Invalid parameters! Type not valid, int expected")        
        self._repair_time = repair_time
        return True



    def checkParam(name: str, description: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload, position: Point, volume: Volume, threat: Threat, crytical: bool, repair_time: int) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
    
        if not super().checkParam(name, description, category, function, value, position, acs, rcs, payload):
            return False     
        if position and not isinstance(position, Point):
            return False
        if volume and not isinstance(volume, Volume):
            return False
        if threat and not isinstance(threat, Threat):                        
            return False                    
        if crytical and not isinstance(position, bool):
            return False
        if repair_time and not isinstance(repair_time, int):
            return False
        return True
    
    def destroy( self ):
        """Destroy this object"""

        for ev in self._eventsQueue:
            ev.destroy()

        self._state.destroy()
        self._coord = None
        self._eventsQueue = None        
        logger.logger.debug("Object: {0} destroyed".format( self._name ) )
        return True


    def efficiency(self): # sostituisce operational()
        """calculate efficiency from asset state, rcp, acp, .."""
        # efficiency = state * acp / rcp
        # return efficiency
        pass
        

    
    def asset_status(self):
        """calculate Asset_Status from asset Asset_Status"""
        # as = median(Asset_Status) 
        # return as
        pass

    def threat_volume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    def position(self):
        """calculate position from asset position"""
        # ap = median(assetPosition) 
        # return ap
        pass

    @property #overload
    def assets(self):
        raise Exception("Metodo non implementato in questa classe")
     
    @assets.setter #overload
    def assets(self, value):
            raise Exception("Metodo non implementato in questa classe")

    def getAsset(self, key): #overload
            raise Exception("Metodo non implementato in questa classe")

    def setAsset(self, key, value): #overload
            raise Exception("Metodo non implementato in questa classe")

    def removeAsset(self, key):#overload
            raise Exception("Metodo non implementato in questa classe")
  