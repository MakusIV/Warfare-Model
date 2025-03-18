from Dynamic_War_Manager.Source.Mobile import Mobile
from Dynamic_War_Manager.Source.Block import Block
import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, GROUND_ASSET_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Vehicle')

# ASSET
class Vehicle(Mobile) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point = None, volume: Volume = None, threat: Threat = None, crytical: bool = False, repair_time: int = 0):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time) 

            # propriety             
            
    
            # Association    
            
            
            # check input parameters
            

    # methods


    def isTank(self):
        return self.category == GROUND_ASSET_CATEGORY["Tank"]
    
    def isArmor(self):
        return self.category == GROUND_ASSET_CATEGORY["Armor"]
    
    def isMotorized(self):
        return self.category == GROUND_ASSET_CATEGORY["Motorized"]
    
    def isArtillery_Semovent(self):
        return self.category == GROUND_ASSET_CATEGORY["Artillery_Semovent"]
    
    def isArtillery_Fixed(self):
        return self.category == GROUND_ASSET_CATEGORY["Artillery_Fixed"]
    
    def isArtillery(self):
        return self.isArtillery_Fixed or self.isArtillery_Semovent
    
    def isAntiAircraft(self):
        return self.isSAM or self.isAAA
    
    def isSAM(self):
        return self.isSAM_Big or self.isSAM_Med or self.isSAM_Small
    
    def isSAM_Big(self):
        return self.category == GROUND_ASSET_CATEGORY["SAM Big"]
    
    def isSAM_Med(self):
        return self.category == GROUND_ASSET_CATEGORY["SAM Med"]
    
    def isSAM_Small(self):
        return self.category == GROUND_ASSET_CATEGORY["SAM Small"]
    
    def isAAA(self):
        return self.category == GROUND_ASSET_CATEGORY["AAA"]
    
    def isEWR(self):
        return self.category == GROUND_ASSET_CATEGORY["EWR"]
    
    def isCommandControl(self):
        return self.category == GROUND_ASSET_CATEGORY["Command_&_Control"]
    