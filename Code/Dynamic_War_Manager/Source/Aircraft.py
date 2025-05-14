from Code import Utility
from Code.Dynamic_War_Manager.Source.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Block import Block
from Code.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import AIR_COMBAT_EFFICACY, AIR_MIL_BASE_CRAFT_ASSET, BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET
#from typing import Literal, List, Dict
from sympy import Point3D

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft')

# ASSET
class Aircraft(Mobile) :    

    def __init__(self, block: Block, name: str|None = None, description: str|None = None, category: str|None = None, asset_type:str|None = None, functionality: str|None = None, cost: int|None = None, value: int|None = None, acp: Payload|None = None, rcp: Payload|None = None, payload: Payload|None = None, position: Point3D|None = None, volume: Volume|None = None, crytical: bool|None = False, repair_time: int|None = 0, role: str|None = None, dcs_unit_data: dict|None = None):   
            
            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data) 
            
            # propriety             
            
    
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
            asset_data = AIR_MIL_BASE_CRAFT_ASSET            

            for k, v in asset_data[self.category]:            
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.rcp = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True              
        
        elif self.block.isLogistic():
            asset_data = BLOCK_INFRASTRUCTURE_ASSET

            for k, v in asset_data[self.block.block_class][self.category]:     # block_class = Transport, category = AircraftB,        
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.rcp = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True     
        
        else:
            raise Exception(f"This asset {self!r} is not consistent with the ownership block - Asset category, type: {self.category, self.asset_type}Block: {self.block!r}")

        
        return False
    
    # use case methods
    def checkParam(self, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
       
        if asset_type and (isinstance(asset_type, str)):        

            if self.block.block_class == "Mil_Base": # asset is a Mil_Base component
                
                asset_t = AIR_MIL_BASE_CRAFT_ASSET.keys()
                if asset_type in asset_t:
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Aircraft asset_type not found. Aircraft asset_type must be any value from: {asset_t!r}")
                    
            
            else:  # asset isn't a Mil_Base component (civilian or logistic not again implemented)
                asset_t = BLOCK_ASSET_CATEGORY[self.block.block_class][self.category].keys()

                if asset_type in asset_t:
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Aircraft asset_type not found. Aircraft asset_type must be any value from: {asset_t!r}")
                
                    
        return (False, f"Bad Arg: Aircraft Asset_type must be any string{asset_type}")                                       



    @property
    def combatPower(self, task):
        return AIR_COMBAT_EFFICACY[self.asset_type][task] * self.efficiency


    def isFighter(self):
        return self.category == "Fighter"
    
    def isFighterBomber(self):
        return self.category == "Fighter_Bomber"
    
    def isAttacker(self):
        return self.category == "Attacker"
    
    def isBomber(self):
        return self.category == "Bomber"
    
    def isHeavyBomber(self):
        return self.category == "Heavy_Bomber"
    
    def isAwacs(self):
        return self.category == "Awacs"
    
    def isRecon(self):
        return self.category == "Recon"
    
    def isTransport(self):
        return self.category == "Transport"
    
    def isHelicopter(self):
        return self.category == "Helicopter"
    

    