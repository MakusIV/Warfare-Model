from Asset import Asset
from Block import Block
from Utility import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Payload import Payload
from Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Structure')

# ASSET
class Structure(Asset) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point = None, volume: Volume = None, threat: Threat = None, crytical: bool = False, repair_time: int = 0):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time) 

            # propriety             
            
    
            # Association    
            
            
            # check input parameters
            if not super.checkParam( name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time ):    
                raise Exception("Invalid parameters! Object not istantiate.")

    # methods
