from Asset import Asset
from Waypoint import Waypoint
from Context import PATH_TYPE
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Edge')

# ASSET
class Edge:    

    def __init__(self, wpA: Waypoint, wpB: Waypoint, path_type: str, danger_level: str|None, speed: float|None, name: str|None):   
                        
            # propriety  
            self._name = name            
            self._wpA = wpA            
            self._wpB = wpB            
            self._path_type = path_type # 'onroad', 'offroad', 'air', "water"
            self._danger_level = danger_level
            self._speed = speed
            self._line = Line3D(wpA, wpB)
            self._lenght = self.calcLenght(self) # distance2D if path_type = [onroad, offroad, water] or distance 3D if path_type = air
            self._travel_time = self.calcTravelTime(self) 
                
            # check input parameters
            check_results = self.checkParam( wpA, wpB, path_type, danger_level, speed, name )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")
            



    def checkParam( wpA: Waypoint, wpB: Waypoint, path_type: str, danger_level: str, speed: float, name: str) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")        
        if path_type and path_type not in PATH_TYPE:            
            return (False, f"Bad Arg: path_type must be: {PATH_TYPE}")        
        if wpA and not isinstance(wpA, Waypoint):
            return (False, "Bad Arg: wpA must be a Point3D object")        
        if wpB and not isinstance(wpB, Waypoint):
            return (False, "Bad Arg: wpB must be a Point3D object")                
        if speed and not isinstance(speed, float):
            return (False, "Bad Arg: speed must be a float")        
        if danger_level and not isinstance(danger_level, float):
            return (False, "Bad Arg: danger_level must be a float")        
    
        return (True, "OK")

    
    
  
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, param):

        check_result = self.checkParam(name = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._name = param  
        return True
    
    @property
    def path_type(self) -> str: 
        return self._path_type  

    @path_type.setter    
    def path_type(self, param) -> bool: #override
        
        check_result = self.checkParam(path_type = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._path_type = param
        return True 
    
    @property
    def wpA(self) -> Point3D: #override      
        return self._wpA
    
    @wpA.setter
    def wpA(self, param) -> bool: #override
        
        check_result = self.checkParam(wpA = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._wpA = param
        return True
    
    @property
    def wpB(self) -> Point3D: #override      
        return self._wpB
    
    @wpB.setter
    def wpB(self, param) -> bool: #override
        
        check_result = self.checkParam(wpB = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._wpB = param
        return True


    @property
    def danger_level(self):
        return self._danger_level

    @danger_level.setter
    def danger_level(self, param):

        check_result = self.checkParam(danger_level = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._danger_level = param  
        return True
    
    
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, param):

        check_result = self.checkParam(speed = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._speed = param  
        return True


    def calcLenght(self):

        len2D, len3D = self._wpA.distanceFrom(self, self._wpB)

        if self._path_type == "air":
            return len3D

        else:
            return len2D

    def calcTravelTime(self):

        if self._speed > 0:
            return self._lenght / self._speed
        else:
            return float('inf')

        

    def minDistance(self, point: Point3D):# distance 3D
        return self._line.distance(point)
        

    def intersectPoint(self, line: Line) -> Point3D: # poni z = 0 per calcolo 2D

        if self._path_type == "air" and isinstance(line, Line3D):
            pass

        else:
            pass

        pass

    def nearPoint(self, point: Point, tolerance: float): # poni z = 0 per calcolo 2D

        if self._path_type == "air" and isinstance(point, Point3D):
            pass

        else:
            pass

        pass



                
        