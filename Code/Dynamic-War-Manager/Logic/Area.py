"""
Class Area
Represents the area occupied by a Block or an Asset
"""

from LoggerClass import Logger
from Context import SHAPE2D
from sympy import Point2D, Line2D, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Area')

class Area:

    def __init__(self, shape: str = SHAPE2D.Circonference, radius: float = None, center: Point2D = None): 
            
            if not isinstance(shape, str) or not (shape in SHAPE2D):
                raise TypeError("Bad Arg: shape must be a string from SHAPE2D")
            
            if not isinstance(radius, float) or radius < 0:
                raise TypeError("Bad Arg: radius must be a float >= 0")
            
            if not isinstance(center, Point2D):
                raise TypeError("Bad Arg: center must be a Point2D from SymPy")
            
            self._shape = shape
            self._radius = radius
            self._center = center 
            
            
    def getArea(self):
        area = 0
        return area
    
    @property
    def shape(self):
        return self._shape         
    
    @shape.setter
    def shape(self, shape):
        if not isinstance(shape, str) or not (shape in SHAPE2D):
            raise TypeError("Bad Arg: shape must be a string from SHAPE2D")
        self._shape = shape   

    @property
    def radius(self):
        return self._radius   
    
    @radius.setter
    def radius(self, radius):
        self._radius = radius 

    @property
    def center(self):
        return self._center   
        
    @center.setter
    def center(self, center):
        self._center = center 



    def inside(self, obj):
        #obj = (Point2D or Line2D)

        if (isinstance(obj, Point2D)):
             # code 
             pass
        
        elif(isinstance(obj, Line2D)):
             # code 
             pass
        
        else:
             # raise exception
             raise TypeError("Bad Arg: only Point2D or Line3D from SymPy, are allowed")

        result = False
        return False


    

    