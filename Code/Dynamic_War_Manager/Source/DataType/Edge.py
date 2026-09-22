from typing import TYPE_CHECKING, Optional, Dict, List, Literal, Tuple, Union
from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Context.Context import PATH_TYPE
from sympy import Point, Line, Point3D, Line3D, Line2D, symbols, solve, Eq, sqrt, And
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
# .logger: Logger e' un wrapper, il logging.Logger vero sta nel suo attributo .logger.
# Senza, ogni logger.debug()/warning() qui solleverebbe AttributeError (stesso difetto
# gia' corretto in DataType/Route.py quando vi sono stati aggiunti i primi call site).
logger = Logger(module_name = __name__, class_name = 'Edge').logger

# ASSET
class Edge:    

    def __init__(self, 
                 wpA: Waypoint, 
                 wpB: Waypoint, 
                 path_type: str, 
                 danger_level: float|None, 
                 speed: float|None, 
                 name: str|None):   
                        
            # propriety  
            self._name = name            
            self._wpA = wpA            
            self._wpB = wpB            
            self._path_type = path_type # 'onroad', 'offroad', 'air', "water"
            self._danger_level = danger_level
            self._speed = speed
            self._line = self._buildLine(wpA.point, wpB.point, Line3D, "3D")
            self._line2d = self._buildLine(wpA.point2d, wpB.point2d, Line2D, "2D")
            self._lenght = self.calcLength() # distance2D if path_type = [onroad, offroad, water] or distance 3D if path_type = air
            self._travel_time = self.calcTravelTime()

            # check input parameters
            check_results = self.checkParam(wpA, wpB, path_type, danger_level, speed, name)

            if not check_results[0]:
                raise Exception(check_results[1] + ". Object not istantiate.")
            



    @staticmethod
    def _buildLine(pA, pB, line_class, label: str):
        """Costruisce la retta di supporto dell'arco, oppure None se l'arco e' degenere.

        sympy rifiuta `Line*(P, P)` ("requires two unique Points"): l'arco e' degenere per
        la 3D quando i due waypoint coincidono, e per la 2D anche quando l'arco e' una
        salita/discesa verticale pura (stessa x,y, z diverse) — caso che un pianificatore
        di rotta aereo produce normalmente quando scavalca una minaccia.

        Prima questo sollevava un'eccezione in costruzione e rendeva l'arco non
        rappresentabile: un dato degenere ma legittimo non e' un errore di programmazione,
        quindi si registra None e si degrada (v. `minDistance`/`intersectPoint`), coerente
        con la convenzione del progetto "niente eccezioni per dati, solo per argomenti
        fuori dominio".
        """
        try:
            return line_class(pA, pB)
        except ValueError:
            logger.debug(f"Edge: degenerate {label} segment ({pA} == {pB}), support line not built")
            return None

    @staticmethod
    def checkParam(wpA: Waypoint = None, wpB: Waypoint = None, path_type: str = None, danger_level: float = None, speed: float = None, name: str = None) -> (bool, str): # type: ignore
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
    def danger_level(self) -> float:
        return self._danger_level

    @danger_level.setter
    def danger_level(self, param) -> bool:

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


    def calcLength(self):
            return self._wpA.distanceFrom(self._wpB)
        

    def calcTravelTime(self, speed: Optional[float] = None):
        """Travel time for this edge. If speed is given, overrides the edge's own speed."""
        _speed = speed if speed else self._speed

        if _speed and _speed > 0:
            return self._lenght / _speed
        else:
            return float('inf')
            

    def minDistance(self, point: Point):# distance 3D

        line = self._line if isinstance(point, Point3D) else self._line2d

        if line is None:
            # arco degenere: la retta di supporto non esiste, la distanza minima dall'arco
            # e' la distanza dal punto in cui l'arco si riduce (v. _buildLine).
            wp = self._wpA.point if isinstance(point, Point3D) else self._wpA.point2d
            return wp.distance(point)

        return line.distance(point)


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

        if self._line is None:
            logger.debug(f"Edge {self._name!r}: degenerate segment, no intersection computable")
            return None

        if self._path_type == "air" and isinstance(line, Line3D):
            intersection = self._line.intersection(line)
            self._line.intersect

        elif isinstance(line, Line2D):
            if self._line2d is None:
                logger.debug(f"Edge {self._name!r}: degenerate 2D segment, no intersection computable")
                return None
            intersection = self._line2d.intersection(line)

        if intersection:
            return intersection[0]
        else:
            return None

        
 
        