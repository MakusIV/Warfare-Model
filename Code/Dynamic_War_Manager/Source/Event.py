
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
import Utility
from sympy import Point3D
from LoggerClass import Logger
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Event')
 
@dataclass
class EventParams:
    """Data class for holding block parameters for validation"""
    time2go: Optional[int] = None
    duration: Optional[int] = None
    energy: Optional[float] = None
    power: Optional[float] = None
    mass: Optional[float] = None
    position: Optional[Point3D] = None
    asset_id: Optional[str] = None
    destination: Optional[int] = None    

class Event:
    
    def __init__(self, event_type, time2go: Optional[int] = None,  duration: Optional[int] = None,
        energy: Optional[float] = None, power: Optional[float] = None, mass: Optional[float] = None,
        position: Optional[Point3D] = None, asset_id: Optional[str] = None, destination: Optional[int] = None):

        # Initialize properties
        self._event_type = event_type # type of event:
        self._id = Utility.setId(self._event_type) # l'id viene generato automaticamente nel runtime per ogni istanza creata        
        self._time2go = time2go # il tempo di attesa (in task o cicli) per considerare gli effetti dell'evento. time2go = 0 -> valutazione effetti evento
        self._duration = duration # la durata (in task o cicli) dell'evento. duration = 0 -> evento concluso 
        self._energy = energy
        self._power = power
        self._mass = mass
        self._position = position
        self._asset_id = asset_id
        self._destination = destination

        # Validate all parameters
        self._validate_all_params(
            event_type=event_type, time2go=time2go, duration=duration,
            energy=energy, power=power, mass=mass, position=position, asset_id=asset_id, destination=destination
        )
   

    @property
    def event_type(self):
        return self._event_type

    @event_type.setter
    def event_type(self, value: str):
        self._validate_param('event_type', value, str)
        self._event_type = value




    def destroy( self ):
       self._typ = None
       self._id = "destroyed"
       self._obj = None


    def decrTime2Go(self):
        self._time2go = self._time2go - 1
        return self._time2go

    def decrDuration(self):
        self._duration = self._duration - 1
        return self._duration

    def isActivable(self):
        return self._time2go == 0 and self._duration > 0

    def isAwaiting(self):
        return self._time2go > 0

    def isPush(self):
        return self._type == 'PUSH'

    def isPop(self):
        return self._type == 'POP'

    def isHit(self):
        return self._type == 'HIT'

    def isAssimilate(self):
        return self._type == 'ASSIMILATE'

    def isMove(self):
        return self._type == 'MOVE'

    
     # Validation methods
    def _validate_all_params(self, **kwargs) -> None:
        """Validate all input parameters"""
        type_checks = {
            'event_type': str,
            'time2go': int,
            'duration': int,
            'energy': float,
            'power': float,
            'mass': float,
            'position': Point3D,
            'asset_id': str,
            'destination': str,
                    
        }
        
        for param, value in kwargs.items():
            if value is not None and param in type_checks:
                self._validate_param(param, value, type_checks[param])

    def _validate_param(self, param_name: str, value: Any, expected_type: type) -> None:
        """Validate a single parameter"""
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for {param_name}. Expected {expected_type.__name__}, got {type(value).__name__}")

