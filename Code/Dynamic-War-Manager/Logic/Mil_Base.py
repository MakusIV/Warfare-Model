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
logger = Logger(module_name = __name__, class_name = 'Mil_Base')

# ASSET
class Mil_Base(Block) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
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
    
    
    def efficiency(self): # sostituisce operational()
        """calculate efficiency from asset state, rcp, acp, .."""
        # efficiency = state * acp / rcp
        # return efficiency
        pass
        

    def threat_volume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    def combatRange(self, type: str = Artillery, height: int = 0):
        """calculate combat range from asset position"""    
        # return combatVolume(type=type).range(height=height)
         
        pass

    def cdefenceAARange(self, height: int = 0):
        """calculate combat range from asset position"""    
        # return defenceAAVolume().range(height=height)
         
        pass

    def combatVolume(self, type: str = Artillery):
        """calculate combat volume from asset position"""
        # distinguere tra arty, mech, mototized, 
        pass
    
    def defenceAAVolume(self):
        """calculate defence volume from asset position"""    
        pass


    def position(self):
        """calculate position from asset position"""
        # ap = median(assetPosition) 
        # return ap
        pass


    def morale(self): # sostituisce operational()
        """calculate morale from region's members"""
        # morale = median(block.morale for block in blocks)
        # return morale
        pass
        

    def intelligence(self):
        """calculate intelligence level"""
        # intelligence = median(asset.efficiency for asset in assets.recognitor())
        # return intelligence
        pass
    
    def recognition(self):
        """calculate recognition report"""
        # intelligence = median(asset.efficiency for asset in assetIntelligence)
        # return intelligence
        pass
    

    def asset_status(self):
        """report info on any mil-base assets category (aircraft, vehicle, supply, ...)"""
        # as = .... 
        # return as
        pass

    def threat_volume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    def front(self):
        """calculate front from asset position"""
        # ap = median(assetPosition) 
        # return ap
        pass

    