"""
Class Volume
Represents the volume occupied by a Block or an Asset
"""
import Utility, Sphere, Hemisphere
from LoggerClass import Logger
from Context import SHAPE2D, SHAPE3D, AREA_FOR_VOLUME
from Dynamic_War_Manager.Source.Area import Area
from sympy import Point2D, Line2D, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Volume')

class Volume:

     def __init__(self, area_base: Area, volume_shape: str, radius_at_height: dict = None): 
            
          if not isinstance(area_base, Area):
               raise TypeError("Bad Arg: only Class Area, are allowed")
            
          if not isinstance(volume_shape, str) or not (volume_shape in SHAPE3D):
               raise TypeError("Bad Arg: shape must be a string from SHAPE3D: {0}".format(SHAPE3D))
            
          if not AREA_FOR_VOLUME[area_base._shape] in SHAPE3D:
               raise TypeError("Bad Arg: {0} area shape must be associable to volume shape: {1}".format(area_base.shape, AREA_FOR_VOLUME[area_base._shape]))
            
          if volume_shape == SHAPE3D.Solid:

               if radius_at_height == None:
                    raise TypeError("Bad Arg: radius_at_height must be defined if volume shape is {0}".format(SHAPE3D.Solid))

               else:                    
                    for key in radius_at_height:

                         if not isinstance(radius_at_height[key], float) or radius_at_height[key] < 0:
                              raise TypeError("Bad Arg: radius_at_height must be a float >= 0")
                              
                         if float(key) < 0: 
                              raise TypeError("Bad Arg: height must be a float >= 0")
                    
          self._shape = volume_shape
          self._areabase = area_base
          
     @property       
     def getAreaBase(self):        
          return self._areabase

     @getAreaBase.setter
     def getAreaBase(self, area_base: Area):
          if not isinstance(area_base, Area):
               raise TypeError("Bad Arg: only Class Area, are allowed")
          self._areabase = area_base


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


    

    