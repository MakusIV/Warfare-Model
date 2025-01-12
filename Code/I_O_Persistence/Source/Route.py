"""
Class Route
contains DCS Route information
"""

from LoggerClass import Logger
from Country import Country
from Context import SIDE
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Route')

class Route:

    def __init__(self, points: Dict = None, spans: Dict = None): 
            

        # check input parameters
        check_results =  self.checkParam( points, spans )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        

        self._points # DCS coalition points - Dict
        self._spans # DCS coalition spans - Dict
        

    
    @property
    def points(self):
        return self._points         
    
    @points.setter
    def points(self, param):

        check_result = self.checkParam(points = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._points = param

    @property
    def spams(self):
        return self._spams   
    
    @spams.setter
    def spams(self, param):

        check_result = self.checkParam(spams = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._spams = param 

    
    
    def addSpam(self, index: int, points: List):
        
        if not isinstance(points, List) or not isinstance(index, int) or index < 0 or index in self._units:
            raise Exception("Bad Arg: points must be a List of point and index must be an integer greater of 0 and unique")
        
        for point_index, point in points:
            if not isinstance(point.value, int):
                # eliminare i precedenti point inseriti?                
                raise Exception("Bad Arg: point must be an integer")
            
            self._countries[index][point_index] = point # point = ('x': int, 'y': int)

    def removeSpamPoint(self, point: List):
        
        if not isinstance(point, List):
            raise Exception("Bad Arg: point must be a List")

        response, spam_index, point_index, point = self.searchSpamPoint(point = point)

        if response:
            del self._spams[spam_index][point_index]
            return True
        else:
            return False

    def removeSpam(self, index: int):
        if not isinstance(index, int):
            raise Exception("Bad Arg: index must be an integer")

        if index in self._spams:
            del self._spams[index]
            return True
        else:
            return False

    def searchSpamPoint(self, point: List = None, index: int = None) -> bool:

        if point and isinstance(point, List):
            for spam_index, spam in self._spams.items():
                for point_index, point_ in spam:
                    if point_.x == point.x and point_.y == point.y:
                        return True, spam_index, point_index, point

        if index and isinstance(point_index, int) and point_index >= 0:
            for spam_index, spam in self._spams.items():
                for point_index_, point_ in spam:
                    if point_index_ == point_index:
                        return True, spam_index, point_index, point_        

        return False, None, None, None    

    
    def checkParam(side: str, bullseye: Point2D, nav_points: Dict(Point2D), countries: Dict(Country)) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(side, str) or not (side in SIDE):
            return (False, "Bad Arg: shape must be a string from SIDE")
        
        if bullseye and not isinstance(bullseye, Point2D):
            return (False, "Bad Arg: bullseye must be a Point2D")
        
        if nav_points and not isinstance(nav_points, Dict) or not (isinstance(nav_point, Point2D) for nav_point in nav_points.values):
            return (False, "Bad Arg: nav_points must be a dict of Point2D") 

        if countries and not isinstance(countries, Dict) or not (isinstance(country, Point2D) for country in countries.values):
            return (False, "Bad Arg: nav_points must be a dict of Country")   
        
        return (True, "parameters ok")


    

    