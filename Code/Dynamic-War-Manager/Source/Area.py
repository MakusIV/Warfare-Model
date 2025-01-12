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
            

            # check input parameters
            check_results =  self.checkParam( shape, radius, center )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")    
            
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
    def shape(self, param):

        check_result = self.checkParam(shape = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._shape = param

    @property
    def radius(self):
        return self._radius   
    
    @radius.setter
    def radius(self, param):

        check_result = self.checkParam(radius = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._radius = param 

    @property
    def center(self):
        return self._center   
        
    @center.setter
    def center(self, param):
        
        check_result = self.checkParam(center = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._center = param



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

    
    def checkParam(shape: str, radius: float, center: Point2D) -> bool: # type: ignore
        
            """Return True if type compliance of the parameters is verified"""   
        
            if not isinstance(shape, str) or not (shape in SHAPE2D):
                return (False, "Bad Arg: shape must be a string from SHAPE2D")
            
            if radius and not isinstance(radius, float) or radius < 0:
                return (False, "Bad Arg: radius must be a float >= 0")
            
            if center and not isinstance(center, Point2D):
                return (False, "Bad Arg: center must be a Point2D from SymPy")  
            
            return (True, "parameters ok")
    

    

    