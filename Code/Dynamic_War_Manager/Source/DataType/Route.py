from heapq import heappush, heappop
from Dynamic_War_Manager.Source.Asset.Asset import Asset
from Dynamic_War_Manager.Source.DataType.Edge import Edge
from Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from sympy import Point3D
from Code.Dynamic_War_Manager.Source.Context.Context import ROUTE_TYPE
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Route')

# ASSET
class Route:    

    def __init__(self, route_type: str, edges: dict, name: str|None):   
            
            
            # propriety  
            self._name = name
            self._route_type = route_type # air, ground, water            
            self._edges = edges  # edges = { (wpA, wpB): Edge }
            self._waypoints = self.getWaypoints(self)
    
            
            # check input parameters
            check_results =  self.checkParam( type, edges )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")
            



    def checkParam(name: str, route_type: str, edges: dict) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")        
        if route_type and route_type not in ROUTE_TYPE:            
            return (False, f"Bad Arg: route_type must be: {ROUTE_TYPE}")  
        if edges and ( not isinstance(edges, dict) or not all( isinstance(edge_value, Edge) for edge_value in edges.values ) ):
            return (False, "Bad Arg: edges must be a dict with Edge class value: edges = { (wpA, wpB): Edge }")        
    
        return (True, "OK")

            


    def getWaypoints(self):
        queue = []      

        for k, v in self._edges:            
            heappush(queue, (v.wpA.name, v.wpA))
            heappush(queue, (v.wpB.name, v.wpB))

        return queue

  
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
    def route_type(self) -> str: 
        return self._oute_type  

    @route_type.setter    
    def route_type(self, param) -> bool: #override
        
        check_result = self.checkParam(route_type = param)

        if not check_result[0]:
            raise Exception(check_result[1])                
        self._route_type = param
        return True 
    
    @property
    def edges(self) -> Point3D: #override      
        return self._point
    
    @edges.setter
    def edges(self, param) -> bool: #override
        
        check_result = self.checkParam(edges = param)

        if not check_result[0]:
            raise Exception(check_result[1])                
        self._edges = param
        return True

    def minDistance(self, point: Point3D):# distance 3D
        min_distance = float('inf')
        
        for k, v in self._edges:
            md = v.minDistance(point)
            
            if md < min_distance:
                min_distance = md

        return min_distance

    def travelTime(self):        

        return self.travelTimeToEdge(self._edges.get(-1))
    
    def travelTimeToEdge(self, edge: Edge):
        travel_time = 0

        for v in self._edges.values():
            if v == edge:
                return travel_time
            
            travel_time += v.calcTravelTime()

        return travel_time
    
    def length(self) -> float:
        length = 0
        for k, v in self._edges:
            length += v.calcLength()
        
        return length

        