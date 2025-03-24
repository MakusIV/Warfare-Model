from Dynamic_War_Manager.Source.Asset import Asset
from sympy import Point3D, Point2D
from LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Waypoint')

# ASSET
class Waypoint:    

    def __init__(self, point: Point3D, name: str|None, obj_reference: Asset|None):   
            
            
            # propriety  
            self._name = name
            self._point = point            
            self._reference = obj_reference
    
            
            # check input parameters
            check_results =  self.checkParam( point, obj_reference )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")
            



    def checkParam(name: str, obj_reference: Asset, position: Point3D) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")        
        if obj_reference and (not isinstance(obj_reference, Asset)):            
            return (False, "Bad Arg: asset_type must be an Asset")        
        if position and not isinstance(position, Point3D):
            return (False, "Bad Arg: position must be a Point3D object")        
    
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
    def reference(self) -> Asset: 
        return self._reference    

    @reference.setter    
    def reference(self, param) -> bool: #override
        
        check_result = self.checkParam(obj_reference = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._reference = param
        return True 
    
    @property
    def point(self) -> Point3D: #override      
        return self._point
    
    @point.setter
    def point(self, param) -> bool: #override
        
        check_result = self.checkParam(point = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._point = param
        return True


    @property
    def point2d(self):
        return Point2D(self._point.x, self._point.x)

    def distanceFrom(self, point: Point2D|Point3D) -> list:        

        if isinstance(point, Point2D):
            return  ( (self._point.x - point.x)**2 + (self._point.x - point.x)**2 ) ** 0.5
        
        elif isinstance( point, Point3D):
            return self.point.distance(point)
        
        elif isinstance( point, Waypoint):
            return self.point.distance(point.point)
        
        else:
            raise TypeError(f"point {type(point)} must be Point2D, Point3D or Waypoint")
    

    