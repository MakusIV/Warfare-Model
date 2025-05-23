from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.Context.Context import NAVAL_Military_CRAFT_ASSET, BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point3D

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Ship')

# ASSET
class Ship(Mobile) :    

    def __init__(self, block: Block, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, dcs_unit_data: Optional[dict] = None):   
            
            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data) 
           
            # propriety             
            self.speed = { 

                "nominal": None,
                "max": None                
            }
    
            # Association    
            
            
            # check input parameters
           
       # methods
    def loadAssetDataFromContext(self) -> bool:
        """Initialize some asset property loading data from Context module
            asset_type is Subcategory of BLOCK_ASSET 

        Returns:
            bool: True if data is loaded, otherwise False
        """     

        if self.block.isMilitary():
            asset_data = NAVAL_Military_CRAFT_ASSET            

            for k, v in asset_data[self.category]:            
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True              
        
        elif self.block.isLogistic():
            asset_data = BLOCK_INFRASTRUCTURE_ASSET

            for k, v in asset_data[self.block.block_class][self.category]:     # block_class = Transport, category = AircraftB,        
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True     
        
        else:
            raise Exception(f"This Ship Asset {self!r} is not consistent with the ownership block - Asset category, type: {self.category, self.asset_type}Block: {self.block!r}")

        
        return False
    
    # use case methods
    def checkParam(self, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
       
        if asset_type and (isinstance(asset_type, str)):        

            if self.block.block_class == "Military": # asset is a Military component
            
                if asset_type in NAVAL_Military_CRAFT_ASSET.keys():
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Ship Asset category not defined. Aircraft Asset must be any value from: {NAVAL_Military_CRAFT_ASSET.keys()}")
                    
            
            else:  # asset isn't a Military component (civilian or logistic not again implemented)
                asset_t = BLOCK_ASSET_CATEGORY[self.block.block_class][self.category].keys()

                if asset_type in asset_t:
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Aircraft asset_type not found. Aircraft asset_type must be any value from: {asset_t!r}")                
                    
        return (False, f"Bad Arg: Ship Asset_type must be any string from BLOCK_ASSET_CATEGORY {BLOCK_ASSET_CATEGORY!r}")                                       



    @property
    def combatPower(self, task):
        pass

    @property
    def isDestroyer(self):
        return self.category == "Destroyer"
    @property
    def isCarrier(self):
        return self.category == "Carrier"
    @property
    def isCruiser(self):
        return self.category == "Cruiser"
    @property   
    def isFrigate(self):
        return self.category == "Frigate"
    @property
    def isFastAttackShip(self):
        return self.category == "FastAttackShip"
    @property
    def isTransport(self):
        return self.category == "Transport"
    @property
    def isSubmarine(self):
        return self.category == "Submarine"
    
    

    