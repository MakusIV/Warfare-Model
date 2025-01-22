from Dynamic_War_Manager.Source.Block import Block
from Utility import Utility
from Dynamic_War_Manager.Source.State import State
from Code.LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Region import Region
from Dynamic_War_Manager.Source.Volume import Volume

# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Mil_Base')

# ASSET
class Mil_Base(Block) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, region: Region = None):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
            if not name:
                self._name = Utility.setName('Unnamed_Mil_Base')

            else:
                self._name = "Mil_Base." + name

            self._id = Utility.setId(self._name)
                       

    # methods

    

    def checkParam(name: str, description: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload, position: Point, volume: Volume, threat: Threat, crytical: bool, repair_time: int) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
    
        if not super().checkParam(name, description, category, function, value, position, acs, rcs, payload):
            return False     
        
        return True
    
    
    def efficiency(self): # sostituisce operational()
        """calculate efficiency from asset state, rcp, acp, .."""
        # efficiency = state * acp / rcp
        # return efficiency
        pass
        

    def air_defense(self):
        """calculate air defense Volume from asset air defense volume"""
        # adsVolume = asset.air_defense from asset in self.assets 
        # adMax = max(adsVolume.range for adsVolume in adsVolume)
        # return adsVolume, adMax
        pass

    def combatRange(self, type: str = Artillery, height: int = 0):
        """calculate combat range from asset position"""    
        # return combatVolume(type=type).range(height=height)         
        pass

    

    def defenseAARange(self, height: int = 0):
        """calculate combat range from assets"""    
        # return defenceAAVolume().range(height=height)         
        pass

    def combatVolume(self, type: str = Artillery):
        """calculate combat volume from asset"""
        # distinguere tra arty, mech, motorized, 
        pass
    
    def defenseAAVolume(self):
        """return defense volume from asset"""    
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
        # intelligence_level = median(asset.efficiency for asset in assets.recognitor())
        # return intelligence_level
        pass
    
    def recognition(self):
        """calculate recognition report"""
        # f(intelligenze, evaluate neightroom, front)
        # return Dict{evaluate.enemy.asset.position, evaluate.enemy.asset.category, evaluate.enemy.asset.class, evaluate.enemy.asset.type, evaluate.enemy.asset.status, evaluate.enemy.asset.qty, evaluate.enemy.asset.efficiency}
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
        """calculate"""
        # ap = median(assetPosition) 
        # return ap
        pass

    def combat_state(self)
        """calculate front from state of assets"""

    