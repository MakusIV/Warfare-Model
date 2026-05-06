import random
from Dynamic_War_Manager.Source.Asset.Asset import Asset
from Dynamic_War_Manager.Source.Block.Block import Block
#from Code.Dynamic_War_Manager.Source.Utility import Utility, Sphere, Hemisphere
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Dynamic_War_Manager.Source.DataType.Event import Event
from Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET, Logistic_Asset_Type as la
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And


# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'Structure').logger

# ASSET
class Structure(Asset) :    

    def __init__(self, block: Block, 
                 name: Optional[str] = None, 
                 description: Optional[str] = None, 
                 category: Optional[str] = None, 
                 physical_characteristics: Optional[Dict] = None, # {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
                 asset_type:Optional[str] = None, 
                 functionality: Optional[str] = None, 
                 cost: Optional[int] = None, 
                 value: Optional[int] = None, 
                 acp: Optional[Payload] = None, 
                 rcp: Optional[Payload] = None, 
                 payload: Optional[Payload] = None, 
                 position: Optional[Point3D] = None, 
                 volume: Optional[Volume] = None, 
                 crytical: Optional[bool] = False, 
                 repair_time: Optional[int] = 0, 
                 role: Optional[str] = None, 
                 dcs_unit_data: Optional[dict] = None):   
            
            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data) 
    
            # propriety             
            self.physical_characteristics = physical_characteristics if physical_characteristics else self.get_physical_characteristics() # se non viene fornito, prova a caricarlo dal Context
            
            # Association    
            
            
            # check input parameters
            if not super.checkParam( name, description, category, functionality, value, acp, rcp, payload, position, volume, crytical, repair_time ):    
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



    # serve?
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
        return self.category == la.BRIDGE.value
    
    def isHangar(self):
        return self.category == la.HANGAR.value
    
    def isDepot(self):
        return self.category == la.DEPOT.value
    
    def isOilTank(self):
        return self.category == la.OIL_TANK.value
    
    def isFarm(self):
        return self.category == la.FARM.value
    
    def isPowerPlant(self):
        return self.category == la.POWER_PLANT.value
        
    def isStation(self):
        return self.category == la.STATION.value
    
    def isBuilding(self):
        return self.category == la.BUILDING.value
    
    def isFactory(self):
        return self.category == la.FACTORY.value
    
    def isBarrack(self):
        return self.category == la.BARRACK.value
    
    

    def get_physical_characteristics(self) -> Dict:
        """Returns the physical characteristics of the structure as defined in the Context module."""
               
        return self.physical_characteristics


    def set_volume_from_physical_characteristics(self):
        """Sets the volume of the vehicle based on its physical characteristics defined in the Context module."""
        
        
        if self.physical_characteristics is None:
            logger.warning("Unable to set volume: Physical characteristics not available")
            return
        
        length = self.physical_characteristics.get('length', None)
        width = self.physical_characteristics.get('width', None)
        height = self.physical_characteristics.get('height', None)

        if length is not None and width is not None and height is not None:
            volume = Volume(length=length, width=width, height=height)

            if self.volume is None:                
                logger.warning(f"Volume {self.volume} set to {volume} based on physical characteristics")
                self.volume = volume
        else:
            logger.warning("Unable to set volume: Incomplete physical characteristics")