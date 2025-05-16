from __future__ import annotations
from typing import TYPE_CHECKING
import sys
import os
# Aggiungi il percorso della directory principale del progetto
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Code import Context, Utility
from numpy import mean
from Code.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Block import Block
from Code.Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.State import State
from Code.Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import BLOCK_CATEGORY, SIDE, BLOCK_ASSET_CATEGORY
from typing import List, Dict
from sympy import Point

if TYPE_CHECKING:    
    from Code.Dynamic_War_Manager.Source.Asset import Asset
    from Code.Dynamic_War_Manager.Source.Region import Region



# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Production')

# BLOCK
class Production(Block):    

    def __init__(self, block: Block, mil_category: str, name: str|None, side: str|None, description: str|None, category: str|None, sub_category: str|None, functionality: str|None, value: int|None, acp: Payload|None, rcp: Payload|None, payload: Payload|None, region: Region|None):   
            
            super().__init__(name, description, side, category, sub_category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
            if not name:
                self._name = Utility.setName('Unnamed_Production')

            else:
                self._name = "Production." + name

            self._id = Utility.setId(self._name)
            

            # check input parameters            
            check_results =  self.checkParam( mil_category )            
            
            if not check_results[1]:
                raise Exception("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
                       

    # methods