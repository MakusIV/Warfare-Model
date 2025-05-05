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
logger = Logger(module_name = __name__, class_name = 'Coalition')

# BLOCK
class Coalition:    

    def __init__(self, side: str, blocks: Block|None):   
            

            self._side = side
            self._blocks = blocks

            # propriety             
            
    
            
            
            

            
                       

    # methods

    # calcState
    # calcStatistic