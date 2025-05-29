from __future__ import annotations
from typing import TYPE_CHECKING,  List, Dict, Literal
from numpy import median
from heapq import heappop, heappush
from Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
#from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_CATEGORY, SIDE, BLOCK_ASSET_CATEGORY

if TYPE_CHECKING:        
    from Code.Dynamic_War_Manager.Source.Context.Region import Region



# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Transport')

# BLOCK
class Transport(Block):    

    def __init__(self, block: Block, mil_category: str, name: str|None, side: str|None, description: str|None, category: str|None, sub_category: str|None, functionality: str|None, value: int|None, acp: Payload|None, rcp: Payload|None, payload: Payload|None, region: Region|None):   
            
            super().__init__(name, description, side, category, sub_category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
            if not name:
                self._name = Utility.setName('Unnamed_Transport')

            else:
                self._name = "Transport." + name

            self._id = Utility.setId(self._name)
            

            # check input parameters            
            check_results =  self.checkParam( mil_category )            
            
            if not check_results[1]:
                raise Exception("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
                       

    # methods