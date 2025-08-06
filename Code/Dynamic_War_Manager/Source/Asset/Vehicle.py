from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.Context.Context import GROUND_COMBAT_EFFICACY, AIR_DEFENSE_ASSET, GROUND_Military_VEHICLE_ASSET, BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point3D

# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'Vehicle').logger

# ASSET
class Vehicle(Mobile) :    

    def __init__(self, block: Block, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, dcs_unit_data: Optional[dict] = None):   
            
            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data) 
            
            # proprietry
            self.speed_off_road = {"nominal": None, "max": None},
                
            
            # dcs_data for vehicle

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
            asset_data = GROUND_Military_VEHICLE_ASSET
            asset_data_air_defense = AIR_DEFENSE_ASSET

            for k, v in asset_data[self.category]: # block_class = "Military", category = "Armor", asset_type = "Infantry_Fighting_Vehicle"                       
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True              

            for k, v in asset_data_air_defense[self.category]: # block_class = "Military", category = "SAM_Big", asset_type = "Track_Radar"            

                for k1, v1 in v:
                    key = k + "_" + k1    
                if self.asset_type == key:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True              
        
        elif self.block.isLogistic():
            asset_data = BLOCK_INFRASTRUCTURE_ASSET

            for k, v in asset_data[self.block.block_class][self.category]:  # block_class = Transport, category = "Road", asset_type = "Truck"            
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True     
        
        else:
            raise Exception(f"This asset is not consistent with the ownership block - Asset category, type: {self.category, self.asset_type}Block: {self.block!r}")

        
        return False
    
    # use case methods
    def checkParam(self, category: str = None, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
       
        if asset_type and (isinstance(asset_type, str)):        

            if self.block.block_class == "Military": # asset is a Military component
                
                if category:
                    vehicle_asset = BLOCK_ASSET_CATEGORY["Ground_Military Vehicle Asset"][category].keys()
                    air_defense_asset = BLOCK_ASSET_CATEGORY["Air_Defence_Asset_Category"][category].keys()
                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"]["Military"][category].keys()

                    if asset_type in [vehicle_asset, air_defense_asset, struct_asset]:
                        return (True, "OK")
                    
                else:

                    vehicle_asset = BLOCK_ASSET_CATEGORY["Ground_Military Vehicle Asset"].items().keys()
                    air_defense_asset = BLOCK_ASSET_CATEGORY["Air_Defence_Asset_Category"].items().keys()
                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"]["Military"].items().keys()

                    if asset_type in [vehicle_asset, air_defense_asset, struct_asset]:
                        return (True, "OK")
            
            else:  # asset isn't a Military component

                if category: 

                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class][category].values()                
                
                else:
                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class].items().keys()                
                
                if asset_type in struct_asset:
                    return (True, "OK")
                    
            return (False, f"Bad Arg: Vehicle asset_type must be any string from BLOCK_ASSET_CATEGORY {BLOCK_ASSET_CATEGORY!r}")                  


        if category and isinstance(category, str):

            vehicle_asset = BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"].keys()
            air_defense_asset = BLOCK_ASSET_CATEGORY["Air_Defence_Asset"].keys()
            struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class].keys()

            if asset_type in [vehicle_asset, air_defense_asset, struct_asset]:
                return (True, "OK")

            return (False, "Bad Arg: Vehicle category must be any string from GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, STRUCTURE_ASSET_CATEGORY")                     
    
        return (True, "OK")
    

    @property
    def isTank(self):
        return self.category == "Tank"
    @property
    def isArmor(self):
        return self.category == "Armor"
    @property
    def isMotorized(self):
        return self.category == "Motorized"
    @property
    def isArtillery_Semovent(self):
        return self.category == "Artillery_Semovent"
    @property
    def isArtillery_Fixed(self):
        return self.category == "Artillery_Fixed"
    @property
    def isArtillery(self):
        return self.isArtillery_Fixed or self.isArtillery_Semovent
    @property
    def isAntiAircraft(self):
        return self.isSAM or self.isAAA
    @property
    def isSAM(self):
        return self.isSAM_Big or self.isSAM_Med or self.isSAM_Small
    @property
    def isSAM_Big(self):
        return self.category == "SAM Big"
    @property
    def isSAM_Med(self):
        return self.category == "SAM Med"
    @property
    def isSAM_Small(self):
        return self.category == "SAM Small"
    @property
    def isAAA(self):
        return self.category == "AAA"
    @property
    def isEWR(self):
        return self.category == "EWR"
    @property
    def isCommandControl(self):
        return self.category == "Command_&_Control"
    


    def set_combat_power(self, force: Optional[str]=None, action: Optional[str]=None):
        force ="ground"
        combat_power = {}

        if action and action not in ACTION_TASKS[force]:
            raise TypeError(f"Unexpected combat_power[{force}].keys: {combat_power}")
    
        for act in ACTION_TASKS[force]:
            if action and act!= action:
                continue
            else:
                combat_power[act] = GROUND_COMBAT_EFFICACY[action][self.category] * self.efficiency

        # call parent method
        self.combat_power = {force: {combat_power}}
    
