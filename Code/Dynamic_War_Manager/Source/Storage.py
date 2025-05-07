import datetime

from numpy import median
from heapq import heappop, heappush
from Dynamic_War_Manager.Source.Block import Block
import Utility
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, MIL_BASE_CATEGORY, GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, GROUND_COMBAT_EFFICACY, GROUND_ACTION, AIR_TASK
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Region import Region
from Dynamic_War_Manager.Source.Volume import Volume



# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Storage')

# BLOCK
class Storage(Block):    

    def __init__(self, block: Block, mil_category: str, name: str|None, side: str|None, description: str|None, category: str|None, sub_category: str|None, functionality: str|None, value: int|None, acp: Payload|None, rcp: Payload|None, payload: Payload|None, region: Region|None):   
            
            super().__init__(name, description, side, category, sub_category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
            if not name:
                self._name = Utility.setName('Unnamed_Storage')

            else:
                self._name = "Storage." + name

            self._id = Utility.setId(self._name)

            # check input parameters            
            check_results =  self.checkParam( mil_category )            
            
            if not check_results[1]:
                raise Exception("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
                       

    # methods