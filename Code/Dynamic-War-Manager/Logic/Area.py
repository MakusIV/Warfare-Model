"""
Class Area
rappresenta l'area occupata da un Block o un Asset

"""

from LoggerClass import Logger
from Context import SHAPE2D
from sympy import Point2D, Line2D, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')

class State:

    def __init__(self, shape = SHAPE2D.Circonference, radius = None, center = None): 
            
            self._shape = shape
            self._radius = radius
            self._center = center 
            
            
    def getArea(self):
        area = 0
        return area


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


    

    