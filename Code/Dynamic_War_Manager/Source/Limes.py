"""

Class Limes
Represents the limes of a Region: a closed line defined from points

"""

from LoggerClass import Logger
import Utility
from Dynamic_War_Manager.Source.Area import Area
from typing import Literal, List, Dict
from Context import Context
from sympy import Point2D, Line2D, Point3D, Line3D, symbols, solve, Eq, sqrt, And
import numpy as np
from collections import deque

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Limes')

class Limes:

    def __init__(self, points: Dict = None): 
            
            if points and not isinstance(points, Dict) or not ( isinstance(points.name, str) and isinstance(points.name.position, Point2D)):
                raise TypeError("Bad Arg: points must be a Dict:{ 'name': str, 'position': Point2D }")

                     
            self._points = deque(points)


            
            
    def calcLenght(self):
        lenght = 0
        return lenght
    

    
    def calcDistance(self, center, point):
        """" 
        returns near points and they distance from point using center like referent point for external/internal evaluation. 
        external == False point is inside limes (on distance from center to limes) otherwise point is outside.
        far_point == True point is far from limes (on distance from center to limes)

        center: center of limes or center of Mil_Base object - Point2D 
        point: Point2D

        return: { 'distance_A': float, 'distance_B': float, 'point_A': Point2D, 'point_B': Point2D, 'external_point': bool, 'far_point': bool }  

        """


        external_point = False
        far_point = False
        pointA = np.array(point)
        min_distance = Context.MAX_WORLD_DISTANCE
        max_limes_distance2center = 0
        distance_Point2Center = np.linalg.norm( np.array(center) - pointA )
        duplicate_points = self._points.copy()
        
        #trova il punto limes più vicino
        while duplicate_points:
            limes_point = duplicate_points.popleft()            
            distance_A = np.linalg.norm( np.array(limes_point.position) - pointA )
            limes_distance2center = np.linalg.norm( np.array(limes_point.position) - np.array(center) )

            if limes_distance2center > max_limes_distance2center:
                max_limes_distance2center = limes_distance2center

            if distance_A > Context.MAX_WORLD_DISTANCE:
                 raise Exception("distance too big for map")

            if distance_A < min_distance:
                min_distance = distance_A
                min_point_A = limes_point                
                min_point_B = duplicate_points.popleft()
                distance_B = np.linalg.norm( np.array(min_point_B.position) - pointA )
                duplicate_points.appendleft(min_point_B)


        if distance_Point2Center < min_distance or distance_Point2Center < distance_B:
            external_point = True

        if min_distance > max_limes_distance2center and distance_B > max_limes_distance2center:
            far_point = True

        result = { 'distance_A': min_distance, 'distance_B': distance_B, 'point_A': min_point_A, 'point_B': min_point_B, 'external_point': external_point, 'far_point': far_point }  
        
        return result 


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


    

    