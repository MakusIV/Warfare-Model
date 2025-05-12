import datetime

from numpy import median
from heapq import heappop, heappush
from Dynamic_War_Manager.Source.Block import Block
import Utility
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, GROUND_COMBAT_EFFICACY, GROUND_ACTION, AIR_TASK
#from typing import Literal, List, Dict
#from sympy import Point, Line, Point3D, Line3D
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
    def regions(self) -> list:
          regions_dict = None # (name_of_region, percentuale possesso_area, combat_power, enemy_combat_power, combat_power_ratio, production_importance (production/total _production), production efficiency, transport .....)
          return region_dict # (name_of_region, percentuale possesso_area, combat_power, enemy_combat_power, combat_power_ratio, production_importance (production/total _production), production efficiency, transport .....)

    # calcState
    # calcStatistic