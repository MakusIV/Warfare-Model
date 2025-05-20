import random
from Dynamic_War_Manager.Source.Asset.Asset import Asset
from Dynamic_War_Manager.Source.Block.Block import Block
#from Code.Dynamic_War_Manager.Source.Utility import Utility, Sphere, Hemisphere
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET
#from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
f

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Structure')

# ASSET
class Structure(Asset) :    

    def __init__(self, block: Block, name: str|None = None, description: str|None = None, category: str|None = None, asset_type:str|None = None, functionality: str|None = None, cost: int|None = None, value: int|None = None, acp: Payload|None = None, rcp: Payload|None = None, payload: Payload|None = None, position: Point3D|None = None, volume: Volume|None = None, crytical: bool|None = False, repair_time: int|None = 0, role: str|None = None, dcs_unit_data: dict|None = None):   
            
            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data) 
    
            # propriety             
            
    
            # Association    
            
            
            # check input parameters
            if not super.checkParam( name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time ):    
                raise Exception("Invalid parameters! Object not istantiate.")

    # methods

    def loadAssetDataFromContext(self) -> bool:
        """Initialize some asset property loading data from Code.Dynamic_War_Manager.Source.Context.Context module
            asset_type is Subcategory of BLOCK_ASSET 

        Returns:
            bool: True if data is loaded, otherwise False
        """    
        
        asset_data = BLOCK_INFRASTRUCTURE_ASSET

        for k, v in asset_data[self.block.block_class][self.category]:     # block_class = Transport, category = AircraftB,        
                
            if self.asset_type == k:
                self.cost = v["cost"]
                self.value = v["value"]
                self.rcp = v["rcp"]
                self.repair_time = v["t2r"]
                self._payload_perc = v["payload%"]
                return True     
    
        return False

    # use case methods
    def checkParam(self, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
       
        if asset_type and (isinstance(asset_type, str)):        

            asset_t = BLOCK_ASSET_CATEGORY[self.block.block_class][self.category].keys() 

            if asset_type in asset_t:
                return (True, "OK")
                
            else:
                raise ValueError(f"Structure asset_type not valid. Structure asset_type must be any value from: {asset_t!r}")            
                    
        return (False, f"Bad Arg: Structure asset_type must be any string {asset_type}")                                       




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