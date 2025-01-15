"""
Class Point
contains DCS Point information
Coalition -> Country -> Group -> Route -> Point
"""

from LoggerClass import Logger
from Country import Country
from Context import SIDE
from Task import Task
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Point')

class Point:

    def __init__(self, task: Dict = None, properties: Dict = None, briefing_name: str = None, action: str = None, type: str = None, speed_locked: bool = None, alt: float = None, speed: float = None, ETA: float = None, ETA_locked: bool = None, x: float = None, y: float = None, name: str = None, airdromeId: int = None, formation_template: str = None): 
            
        # check input parameters
        check_results =  self.checkParam( task, properties )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        self._briefing_name = briefing_name # DCS point breafing_name  - str  (e.g.: spawn)
        self._action = action # DCS point action  - str  (e.g.: Turning Point)
        self._type = type # DCS point type  - str  (e.g.: Turning Point)
        self._speed_locked = speed_locked # DCS point speed_locked  - bool
        self._alt_type = alt_type # DCS point alt_type  - str  (e.g.: BARO, MSL)
        self._speed = speed # DCS point speed - float
        self._ETA = ETA # DCS point ETA - float
        self._ETA_locked = ETA_locked # DCS point ETA_locked - bool
        self._y = y # DCS point y - float
        self._x = x # DCS point x - float
        self._name = name # DCS point name - str
        self._alt = alt # DCS point altitude - float
        self._airdromeId= airdromeId # DCS point airdromeId - int
        self._formation_template = formation_template # DCS point formation_template - str

        self._properties = properties # DCS point properties  - Dict: {'vnav': 0, 'scale': 0, 'angle': 0, 'vangle': 0, 'steer': 0} 

        # task.id: str, task.params: Dict
        # task.params.tasks Dict        
        self._task = task # DCS point task - Dict: {'id': str, 'params': Dict: {index_int: value.Task} }
    
    
    @property
    def task(self):
        return self._task         
    
    @task.setter
    def task(self, param):

        check_result = self.checkParam(task = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._task = param

    
    @property
    def properties(self):
        return self._properties   
    
    @properties.setter
    def properties(self, param):

        check_result = self.checkParam(properties = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._properties = param 

    @properties
    def briefing_name(self):
        return self._briefing_name
    
    @briefing_name.setter 
    def briefing_name(self, param):
        
        check_result = self.checkParam(briefing_name = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._briefing_name = param 


    @properties
    def action(self):
        return self._action
    
    @action.setter 
    def action(self, param):
        
        check_result = self.checkParam(action = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._action = param    


    @properties
    def type(self):
        return self._type  
    
    @type.setter 
    def type(self, param):
        
        check_result = self.checkParam(type = param)

        if not check_result[1]:
            raise Exception(check_result[2])
        
        self._type = param


    @properties
    def speed_locked(self):
        return self._speed_locked
    
    @speed_locked.setter 
    def speed_locked(self, param):
        
        check_result = self.checkParam(speed_locked = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._speed_locked = param


    @properties
    def alt_type(self):
        return self._alt_type    
   
    @alt_type.setter 
    def alt_type(self, param):
        
        check_result = self.checkParam(alt_type = param)    

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._alt_type = param


    @properties
    def speed(self):
        return self._speed
    
    @speed.setter 
    def speed(self, param):
        
        check_result = self.checkParam(speed = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._speed = param


    @properties
    def ETA(self):
        return self._ETA    
    
    @ETA.setter 
    def ETA(self, param):
        
        check_result = self.checkParam(ETA = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._ETA = param


    @properties
    def ETA_locked(self):
        return self._ETA_locked
    
    @ETA_locked.setter 
    def ETA_locked(self, param):
        
        check_result = self.checkParam(ETA_locked = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._ETA_locked = param


    @properties
    def y(self):
        return self._y    
   
    @y.setter 
    def y(self, param):
        
        check_result = self.checkParam(y = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._y = param


    @properties
    def x(self):
        return self._x
    
    @x.setter   
    def x(self, param):
        
        check_result = self.checkParam(x = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._x = param


    @properties
    def name(self):
        return self._name
    
    @name.setter    
    def name(self, param):
        
        check_result = self.checkParam(name = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._name = param

    @properties
    def alt(self):
        return self._alt
    
    @alt.setter    
    def alt(self, param):
        
        check_result = self.checkParam(alt = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._alt = param


    @properties
    def airdromeId(self):
        return self._airdromeId
    
    @airdromeId.setter    
    def airdromeId(self, param):
        
        check_result = self.checkParam(airdromeId = param)

        if not check_result[1]:
            raise Exception(check_result[2])
        

        self._airdromeId = param   


    @properties
    def formation_template(self):
        return self._formation_template
    
    @formation_template.setter    
    def formation_template(self, param):
        
        check_result = self.checkParam(formation_template = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._formation_template = param


    
    def checkParam(task: Dict = None, properties: Dict = None, briefing_name: str = None, action: str = None, type: str = None, speed_locked: bool = None, alt: float = None, speed: float = None, ETA: float = None, ETA_locked: bool = None, x: float = None, y: float = None, name: str = None, airdromeId: int = None, formation_template: str = None) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if briefing_name and not isinstance(briefing_name, str):
            return (False, "Bad Arg: briefing_name must be a str")
        
        if action and not isinstance(action, str):
            return (False, "Bad Arg: action must be a str")
        
        if type and not isinstance(type, str):
            return (False, "Bad Arg: type must be a str")
        
        if speed_locked and not isinstance(speed_locked, bool):
            return (False, "Bad Arg: speed_locked must be a bool")
        
        if alt and not isinstance(alt, float):
            return (False, "Bad Arg: alt must be a float")
        
        if speed and not isinstance(speed, float):
            return (False, "Bad Arg: speed must be a float")
        
        if ETA and not isinstance(ETA, float):
            return (False, "Bad Arg: ETA must be a float")
        
        if ETA_locked and not isinstance(ETA_locked, bool):
            return (False, "Bad Arg: ETA_locked must be a bool")
        
        if x and not isinstance(x, float):
            return (False, "Bad Arg: x must be a float")
        
        if y and not isinstance(y, float):
            return (False, "Bad Arg: y must be a float")
        
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")
        
        if airdromeId and not isinstance(airdromeId, int):
            return (False, "Bad Arg: airdromeId must be a int")
        
        if formation_template and not isinstance(formation_template, str):
            return (False, "Bad Arg: formation_template must be a str")
        
        if task and not isinstance(task, Dict) or not all( keys in task.keys() for keys in ['id', 'params'] ) or not isinstance(task.params, Dict) or not all( isinstance(value, Task) for value in task.params.values() ):
            return (False, "Bad Arg: task must be a Dict: task = {'id': str, 'params': Dict {index: int, value: Task}}")

        if properties and not isinstance(property, Dict) or not all (keys in property.keys() for keys in ['vnav', 'scale', 'angle', 'vangle', 'steer'] ) or not all ( isinstance(value, int) for value in property.values() ): 
            return (False, "Bad Arg: property must be a Dict: properties = {'vnav': 0, 'scale': 0, 'angle': 0, 'vangle': 0, 'steer': 0}")
        
        return (True, "parameters ok")


    

    