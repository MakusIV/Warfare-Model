from Dynamic_War_Manager.Source.Asset.Asset import Asset
from Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Context.Context import PATH_TYPE
from sympy import Point, Line, Point3D, Line3D, Line2D, symbols, solve, Eq, sqrt, And
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

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
            self._line2d = Line2D(wpA.point2d, wpB.point2d)
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
        
        if not check_result[0]:
            raise Exception(check_result[1])    

        self._name = param  
        return True
    
    @property
    def path_type(self) -> str: 
        return self._path_type  

    @path_type.setter    
    def path_type(self, param) -> bool: #override
        
        check_result = self.checkParam(path_type = param)

        if not check_result[0]:
            raise Exception(check_result[1])                
        self._path_type = param
        return True 
    
    @property
    def wpA(self) -> Point3D: #override      
        return self._wpA
    
    @wpA.setter
    def wpA(self, param) -> bool: #override
        
        check_result = self.checkParam(wpA = param)

        if not check_result[0]:
            raise Exception(check_result[1])                
        self._wpA = param
        return True
    
    @property
    def wpB(self) -> Point3D: #override      
        return self._wpB
    
    @wpB.setter
    def wpB(self, param) -> bool: #override
        
        check_result = self.checkParam(wpB = param)

        if not check_result[0]:
            raise Exception(check_result[1])                
        self._wpB = param
        return True


    @property
    def danger_level(self):
        return self._danger_level

    @danger_level.setter
    def danger_level(self, param):

        check_result = self.checkParam(danger_level = param)
        
        if not check_result[0]:
            raise Exception(check_result[1])    

        self._danger_level = param  
        return True
    
    
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, param):

        check_result = self.checkParam(speed = param)
        
        if not check_result[0]:
            raise Exception(check_result[1])    

        self._speed = param  
        return True


    def calcLenght(self):
            return self._wpA.distanceFrom(self._wpB)
        

    def calcTravelTime(self):

        if self._speed > 0:
            return self._lenght / self._speed
        else:
            return float('inf')

        

    def minDistance(self, point: Point):# distance 3D

        if isinstance(point, Point3D):
            return self._line.distance(point)
        else:
            return self._line2d.distance(point)
        

    def intersectPoint(self, line: Line) -> Point: # poni z = 0 per calcolo 2D
        """
        Calcola il punto di intersezione tra self e la retta costituita dalla distanza minima tra self e line.

        Parameters
        ----------
        line : Line o Line3D
            La linea con cui calcolare l'intersezione.

        Returns
        -------
        Point o Point3D
            Il punto di intersezione.
        """
        intersection = None

        if self._path_type == "air" and isinstance(line, Line3D):
            intersection = self._line.intersection(line)
            self._line.intersect

        elif isinstance(line, Line2D):
            intersection = self._line.intersection(line)

        if intersection:
            return intersection[0]
        else:
            return None

        
 
        