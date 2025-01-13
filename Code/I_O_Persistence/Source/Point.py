"""
Class Point
contains DCS Point information
"""

from LoggerClass import Logger
from Country import Country
from Context import SIDE
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Point')

class Point:

    def __init__(self, task: Dict = None, properties: Dict = None): 
            

        # check input parameters
        check_results =  self.checkParam( task, properties )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        
        self._briefing_name # DCS point breafing_name  - str  (e.g.: spawn)
        self._action # DCS point action  - str  (e.g.: Turning Point)
        self._type # DCS point type  - str  (e.g.: Turning Point)
        self._speed_locked # DCS point speed_locked  - bool
        self._alt_type # DCS point alt_type  - str  (e.g.: BARO, MSL)
        self._speed # DCS point speed - float
        self._ETA # DCS point ETA - float
        self._ETA_locked # DCS point ETA_locked - bool
        self._y # DCS point y - float
        self._x # DCS point x - float
        self._name # DCS point name - str
        self._alt # DCS point altitude - float
        self._airdromeId # DCS point airdromeId - int
        self._formation_template # DCS point formation_template - str

        self._properties = # DCS point properties  - Dict: {'vnav': 0, 'scale': 0, 'angle': 0, 'vangle': 0, 'steer': 0} 
        self._task # DCS point task - Dict
        

    
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

    
    
    def setProperty(self, vnav: int, scale: int, angle: int, vangle: int, steer: int):
        # {'vnav': 0, 'scale': 0, 'angle': 0, 'vangle': 0, 'steer': 0} 

        if vnav and not isinstance(vnav, int) or scale and not isinstance(scale, int) or angle and not isinstance(angle, int) or vangle and not isinstance(vangle, int) or steer and not isinstance(steer, int):
            raise Exception("Bad Arg: vnav, scale, angle, vangle, steer must be integers")

        if vnav and isinstance(vnav, int):
            self._properties['vnav'] = vnav

        if scale and isinstance(scale, int):
            self._properties['scale'] = scale

        if angle and isinstance(angle, int):
            self._properties['angle'] = angle

        if vangle and isinstance(vangle, int):
            self._properties['vangle'] = vangle

        if steer and isinstance(steer, int):
            self._properties['steer'] = steer        

        return 

    def removeSpanPoint(self, point: List) -> bool:
        
        if not isinstance(point, List) and 'x' in point.keys() and 'y' in point.keys() and isinstance(point.x, int) and isinstance(point.y, int):    
            raise Exception("Bad Arg: point must be a List: point = ('x': int, 'y': int)")

        response, span_index, point_index, point = self.searchSpamPoint(point = point)

        if response:
            del self._properties[span_index][point_index]
            return True
        else:
            return False

    def removeSpan(self, index: int) -> bool:

        if not isinstance(index, int):
            raise Exception("Bad Arg: index must be an integer")

        if index in self._properties:
            del self._properties[index]
            return True
        else:
            return False

    def searchSpanPoint(self, point: List = None, index: int = None) -> bool:

        if point and isinstance(point, List):
            for span_index, span in self._properties.items():
                for point_index, point_ in span:
                    if point_.x == point.x and point_.y == point.y:
                        return True, span_index, point_index, point

        if index and isinstance(point_index, int) and point_index >= 0:
            for span_index, span in self._properties.items():
                for point_index_, point_ in span:
                    if point_index_ == point_index:
                        return True, span_index, point_index, point_        

        return False, None, None, None    

    
    def checkParam(task: Task, properties: Dict, nav_task: Dict(Point2D), countries: Dict(Country)) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(side, str) or not (side in SIDE):
            return (False, "Bad Arg: shape must be a string from SIDE")
        
        if bullseye and not isinstance(bullseye, Point2D):
            return (False, "Bad Arg: bullseye must be a Point2D")
        
        if nav_task and not isinstance(nav_task, Dict) or not (isinstance(nav_point, Point2D) for nav_point in nav_task.values):
            return (False, "Bad Arg: nav_task must be a dict of Point2D") 

        if countries and not isinstance(countries, Dict) or not (isinstance(country, Point2D) for country in countries.values):
            return (False, "Bad Arg: nav_task must be a dict of Country")   
        
        if task and not isinstance(task, Task):
            return (False, "Bad Arg: task must be a Task")

        if properties and not isinstance(property, List) or not all (keys in property.keys() for keys in ['vnav', 'scale', 'angle', 'vangle', 'steer'] ) or not all ( isinstance(value, int) for value in property.values() ): 
            return (False, "Bad Arg: property must be a List: properties = {'vnav': 0, 'scale': 0, 'angle': 0, 'vangle': 0, 'steer': 0}")
        
        return (True, "parameters ok")


    

    