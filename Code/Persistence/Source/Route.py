"""
Class Route
contains DCS Group Route information
Coalition -> Country -> Group -> Route
"""

from LoggerClass import Logger
from Persistence.Source.Country import Country
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
        
        

        self._points # DCS route points - Dict
        self._spans # DCS route spans - Dict
        

    
    @property
    def points(self):
        return self._points         
    
    @points.setter
    def points(self, param):

        check_result = self.checkParam(points = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._points = param

    def addPoint(self, index: int, point: List):
        
        if not isinstance(point, List) and 'x' in point.keys() and 'y' in point.keys() and isinstance(point.x, int) and isinstance(point.y, int):    
            raise Exception("Bad Arg: point must be a List: point = ('x': int, 'y': int)")
        
        if not isinstance(index, int) or index < 0 or index in self._points:
            raise Exception("Bad Arg: index must be an integer greater of 0 and unique")
        
        self._points[index] = point 



    @property
    def spans(self):
        return self._spans   
    
    @spans.setter
    def spans(self, param):

        check_result = self.checkParam(spans = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._spans = param 

    
    def addSpan(self, index: int, points: List):
        
        if not isinstance(points, List) or not isinstance(index, int) or index < 0 or index in self._units:
            raise Exception("Bad Arg: points must be a List of point and index must be an integer greater of 0 and unique")
        
        for point_index, point in points:
            if not isinstance(point.value, int):
                # eliminare i precedenti point inseriti?                
                raise Exception("Bad Arg: point must be an integer")
            
            self._countries[index][point_index] = point # point = ('x': int, 'y': int)

    def removeSpanPoint(self, point: List) -> bool:
        
        if not isinstance(point, List) and 'x' in point.keys() and 'y' in point.keys() and isinstance(point.x, int) and isinstance(point.y, int):    
            raise Exception("Bad Arg: point must be a List: point = ('x': int, 'y': int)")

        response, span_index, point_index, point = self.searchSpamPoint(point = point)

        if response:
            del self._spans[span_index][point_index]
            return True
        else:
            return False

    def removeSpan(self, index: int) -> bool:
        if not isinstance(index, int):
            raise Exception("Bad Arg: index must be an integer")

        if index in self._spans:
            del self._spans[index]
            return True
        else:
            return False

    def searchSpanPoint(self, point: List = None, index: int = None) -> bool:

        if point and isinstance(point, List):
            for span_index, span in self._spans.items():
                for point_index, point_ in span:
                    if point_.x == point.x and point_.y == point.y:
                        return True, span_index, point_index, point

        if index and isinstance(point_index, int) and point_index >= 0:
            for span_index, span in self._spans.items():
                for point_index_, point_ in span:
                    if point_index_ == point_index:
                        return True, span_index, point_index, point_        

        return False, None, None, None    

    
    def checkParam(side: str, bullseye: Point2D, nav_points: Dict(Point2D), countries: Dict(Country), spans: Dict) -> List: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(side, str) or not (side in SIDE):
            return (False, "Bad Arg: shape must be a string from SIDE")
        
        if bullseye and not isinstance(bullseye, Point2D):
            return (False, "Bad Arg: bullseye must be a Point2D")
        
        if nav_points and not isinstance(nav_points, Dict) or not (isinstance(nav_point, Point2D) for nav_point in nav_points.values):
            return (False, "Bad Arg: nav_points must be a dict of Point2D") 

        if countries and not isinstance(countries, Dict) or not (isinstance(country, Point2D) for country in countries.values):
            return (False, "Bad Arg: nav_points must be a dict of Country")   
        
        if spans and not isinstance(spans, Dict):

            if not all (( isinstance(span, List), isinstance(span_index, int), span_index >= 0, all( isinstance(point, List) and 'x' in point.keys() and 'y' in point.keys() and isinstance(point.x, int) and isinstance(point.y, int) for point in span)) for span_index, span in self._spans.items()):
                return (False, "Bad Arg: spans must be a dict: spans = { span_index: [ point = ('x': int, 'y': int) ] }")
        
        return (True, "parameters ok")


    

    