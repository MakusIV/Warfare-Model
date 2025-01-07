"""

Class Limes
Represents the limes of a Region: a closed line defined from points

"""

from LoggerClass import Logger
from Area import Area
from typing import Literal, List, Dict
from Context import SHAPE2D
from sympy import Point2D, Line2D, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Limes')

class Limes:

    def __init__(self, points: List = None): 
            
            if points and not isinstance(points, List) or not (isinstance(points[1], str) and isinstance(points[2], Point2D) and isinstance(points[3], vector2D)):
                raise TypeError("Bad Arg: shape must be a string from SHAPE2D")
            
            if not isinstance(radius, float) or radius < 0:
                raise TypeError("Bad Arg: radius must be a float >= 0")
            
            if not isinstance(center, Point2D):
                raise TypeError("Bad Arg: center must be a Point2D from SymPy")
            
            self._points = [] # [name: str, position: Point3D, orientation: vector2D]
            
            
    def calcArea(self):
        area = 0
        return area
    

    
    def calcCenter(self):
        return self._center   


    def inside(self, obj):
        #obj = (Point2D or Line2D)

        if (isinstance(obj, Point2D)):
             # code 
             pass
        
        elif(isinstance(obj, Line2D)):
             # code 
             pass
        
        elif(isinstance(obj, Area)):
             # code 
             pass             
        
        
        return False


    

    