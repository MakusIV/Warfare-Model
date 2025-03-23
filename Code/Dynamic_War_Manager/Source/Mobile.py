from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Block import Block
import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, CATEGORY, MIL_BASE_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Mobile')

# ASSET
class Mobile(Asset) :    

    def __init__(self, block: Block, name: str|None, description: str|None, category: str|None, functionality: str|None, value: int|None, cost: int|None, acp: Payload|None, rcp: Payload|None, payload: Payload|None, position: Point|None, volume: Volume|None, threat: Threat|None, crytical: bool|None, repair_time: int|None, max_speed: float|None):   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time) 

            # propriety   
            self._max_speed = max_speed
            
    
            # Association    
            
            
            # check input parameters
            
    # methods

    @property
    def max_speed(self):
        return self._max_speed

    @max_speed.setter
    def max_speed(self, param):

        check_result = self.checkParam(max_speed = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._max_speed = param  
        return True



    def checkParam(max_speed: float) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if max_speed and not isinstance(max_speed, float):
            return (False, "Bad Arg: max_speed must be a float")
    
        return (True, "OK")

    def attackRange(self):
         #return value
         pass
    

    def airDefense(self):
        #return Volume
        pass

