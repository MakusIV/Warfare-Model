import datetime

from numpy import median
from heapq import heappop, heappush
from Dynamic_War_Manager.Source.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Code.Dynamic_War_Manager.Source.Context.Context import STATE, GROUND_COMBAT_EFFICACY, GROUND_ACTION, AIR_TASK
#from typing import Literal, List, Dict
#from sympy import Point, Line, Point3D, Line3D
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Region import Region
from Dynamic_War_Manager.Source.Volume import Volume
from Dynamic_War_Manager.Source.Military import Military
from Dynamic_War_Manager.Source.Urban import Urban
from Dynamic_War_Manager.Source.Production import Production
from Dynamic_War_Manager.Source.Storage import Storage
from Dynamic_War_Manager.Source.Transport import Transport



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

    def getTacticalReport(self) -> dict:
    
      """ getTacticalReport: 
            - get tactical report from all military blocks in the region
            - return a list of tactical report ordered by priority
            - tactical report is a dictionary with the following keys:
                  - region: name of the region
                  - block: name of the block
                  - report: tactical report (dict) with the following keys:
                  - type: type of the report (attack, defence, etc)
                  - priority: priority of the report (high, medium, low)
                  - description: description of the report
                  - action: action to be taken (attack, defend, etc)
                  - the report is ordered by priority (high, medium, low)
      Args:
            side (str): side of the blocks (red, blue)

      Returns:
            dict: with the following keys:
                  - region: name of the region
                  - block: name of the block
      """    
      
      # scorre elenco Military: aggiunge alla lista di report il report corrente. La lista è ordinata per criticità
      tactical_reports = {} # 

      
      Militarys = self.getBlocks(blockCategory = "Military", side = self.side)

      for block in Militarys:            
            #tactical reports only from ground bases and air bases
            if isinstance(block, Military):
                  report = block.getTacticalReport()
                  tactical_reports[block.region][block.name] = report

      return tactical_reports