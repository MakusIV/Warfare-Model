import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.Mobile import Mobile
from Dynamic_War_Manager.Source.Block import Block
from Dynamic_War_Manager.Source.State import State
from Code.LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, AIR_ASSET_CATEGORY, AIR_COMBAT_EFFICACY
#from typing import Literal, List, Dict
#from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft')

# ASSET
class Aircraft(Mobile) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point = None, volume: Volume = None, threat: Threat = None, crytical: bool = False, repair_time: int = 0):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time) 

            # propriety             
            
    
            # Association    
            
            
            # check input parameters
           
    # methods

    @property
    def combatPower(self, task):
        return AIR_COMBAT_EFFICACY[self.asset_type][task] * self.efficiency


    def isFighter(self):
        return self.category == AIR_ASSET_CATEGORY["Fighter"]
    
    def isFighterBomber(self):
        return self.category == AIR_ASSET_CATEGORY["Fighter_Bomber"]
    
    def isAttacker(self):
        return self.category == AIR_ASSET_CATEGORY["Attacker"]
    
    def isBomber(self):
        return self.category == AIR_ASSET_CATEGORY["Bomber"]
    
    def isHeavyBomber(self):
        return self.category == AIR_ASSET_CATEGORY["Heavy_Bomber"]
    
    def isAwacs(self):
        return self.category == AIR_ASSET_CATEGORY["Awacs"]
    
    def isRecon(self):
        return self.category == AIR_ASSET_CATEGORY["Recon"]
    
    def isTransport(self):
        return self.category == AIR_ASSET_CATEGORY["Transport"]
    
    def isHelicopter(self):
        return self.category == AIR_ASSET_CATEGORY["Helicopter"]
    

    