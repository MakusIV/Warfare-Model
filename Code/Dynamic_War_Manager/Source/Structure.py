import random
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Block import Block
#import Utility, Sphere, Hemisphere
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STRUCTURE_ASSET_CATEGORY
#from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
f

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Structure')

# ASSET
class Structure(Asset) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point = None, volume: Volume = None, threat: Threat = None, crytical: bool = False, repair_time: int = 0):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time) 

            # propriety             
            
    
            # Association    
            
            
            # check input parameters
            if not super.checkParam( name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time ):    
                raise Exception("Invalid parameters! Object not istantiate.")

    # methods
    def getBlockInfo(self, request: str, asset_Number_Accuracy: float, asset_Efficiency_Accuracy: float):    
        """ Return a List of enemy asset near this block with detailed info: qty, type, efficiency, range, status resupply. Override Block.getBlockInfo()"""

        report = {
            "reporter name": self.side + "_" + self.name + "_" + self.state.n_mission + "_" + self.state.date_mission,
            "area": None,
            "structure category": self.category, 
            "criticality": 0.0,           
            "asset": {
                STRUCTURE_ASSET_CATEGORY["Bridge"]: {"Number": 0, "Efficiency": 0},
                STRUCTURE_ASSET_CATEGORY["Hangar"]: {"Number": 0, "Efficiency": 0},
                
            }
        }
        
        # calculate total number and efficiency for each assets category: Tank, Armor, Motorized, ...
        for asset in self.assets:        
            category = asset.category # Bridge, 
            efficiency = asset.efficiency
            report["asset"][category]["Number"] += 1
            report["asset"][category]["Efficiency"] += efficiency

        
        # update efficiency and number for each category of asset
        for category in STRUCTURE_ASSET_CATEGORY:
 
            if request == "enemy_request": # if it's an enemy request update efficiency and number with random error                                
                efficiency_error = random.choice([-1, 1]) * random.uniform(0, asset_Efficiency_Accuracy)
                number_error = random.choice([-1, 1]) * random.uniform(0, asset_Number_Accuracy)
                report["asset"][category]["Efficiency"] = report["asset"]["Efficiency"] * (1 + efficiency_error) / report["asset"]["Number"]
                report["asset"][category]["Number"] = report["asset"]["Number"] * (1 + number_error)
            



        
    def isBridge(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Bridge"]
    
    def isHangar(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Hangar"]
    
    def isDepot(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Depot"]
    
    def isOilTank(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Oil_Tank"]
    
    def isFarm(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Farm"]
    
    def isPowerPlant(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Power_Plant"]
    
    def isFarm(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Farm"]
    
    def isStation(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Station"]
    
    def isBuilding(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Building"]
    
    def isFactory(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Factory"]
    
    def isBarrack(self):
        return self.category == STRUCTURE_ASSET_CATEGORY["Barrack"]