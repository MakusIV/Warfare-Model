"""
 CLASS State
 
 Represents the state of an object (Block, Asset, ..)

 
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple

# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'State')

class StateCategory(Enum):
    HEALTHFUL = "Healtful"
    DAMAGED = "Damaged"
    CRITICAL = "Critical"
    DESTROYED = "Destroyed"
    UNKNOW = "Unknow"


HEALTH_LEVEL = {    
    StateCategory.DAMAGED.value: 0.8,       # healt level vaue for Damaged status
    StateCategory.CRITICAL.value: 0.5,      # healt level value for Crititcal status
    StateCategory.DESTROYED.value: 0.15,    # healt level value for Destroyed status
    StateCategory.UNKNOW.value: None     # healt level value for Destroyed status
}

class State:

    def __init__(self, object_type: str, object_id: str, success_ratio: Optional[float], health: Optional[float]): 
        
        
        self._validate_init_params(object_type, object_id, success_ratio, health)
        # property        
        #       

        self._object_type: str = object_type # Block, Asset, ...
        self._object_id: str = object_id   
        self._success_ratio: float = success_ratio # ("Block_ID", "Block_Name"): float) # per mil: mission_success_ratio, per prod, storage, transport = random_anomaly (anomalie di produzione, trasporto ecc generate casualmente in funzione del livello di goods (ricambi):  random(0, rcp_goods / acp _goods))        
        self._health: float = health# health  - float := [0:1] ( o int := [0-100] ??)
        self._state_value: str        
        self.update()
        logger.debug(f"State created {self!r}")    

   

    @property        
    def health(self):
        return self._health
    
    @health.setter
    def health(self, health):
        
        if not isinstance(health, float):
            raise TypeError(f"type not valid, float type expected, got {type(health).__name__}")

        if health < 0:
            raise ValueError(f"health don't must be negative, got {health}")        
        self._health = health
        self.update()


    @property        
    def success_ratio(self):
        return self._success_ratio
    
    @success_ratio.setter
    def success_ratio(self, success_ratio):
        
        if not isinstance(success_ratio, float):
            raise TypeError(f"type not valid, float type expected, got {type(success_ratio).__name__}")
        if success_ratio < 0:
            raise ValueError(f"success_ratio don't must be negative, got {success_ratio}")        
        self._success_ratio = success_ratio

    @property
    def state_value(self):
        return self._state_value
    
    @state_value.setter
    def state_value(self, state_value):
        
        if not isinstance(state_value, str):
            raise TypeError("type not valid, str type expected")
        
        elif state_value not in StateCategory:
            value = [v for v in StateCategory.keys()]
            str_value = ', '.join(value)
            raise ValueError("value not valid: " + state_value + ". Value expected: \n" + str_value)
        
        else:
            self._state_value = state_value            



    def isOperative(self):
        return self._state_value == StateCategory.DAMAGED.value or self._state_value == StateCategory.HEALTHFUL.value 
    
    def isHealtful(self):
        return self._state_value == StateCategory.HEALTHFUL.value

    def isDestroyed(self):
        return self._state_value == StateCategory.DESTROYED.value

    def isDamaged(self):
        return self._state_value == StateCategory.DAMAGED.value
    
    def isCritical(self):
        return self._state_value == StateCategory.CRITICAL.value

    
    def update(self):
        "update state_value property"

        if not self._state_value:
            return
        
        if self._health > HEALTH_LEVEL[StateCategory.DAMAGED.value]:
            self._state_value = StateCategory.HEALTHFUL.value
            
        elif HEALTH_LEVEL[StateCategory.CRITICAL.value] < self._health <= HEALTH_LEVEL[StateCategory.DAMAGED.value]:
            self._state_value = StateCategory.DAMAGED.value

        elif HEALTH_LEVEL[StateCategory.DESTROYED.value] < self._health <= HEALTH_LEVEL[StateCategory.CRITICAL.value]:
            self._state_value = StateCategory.CRITICAL.value

        elif self._health <= HEALTH_LEVEL[StateCategory.DESTROYED.value]:
            self._state_value = StateCategory.DESTROYED.value
        
        else:
            self._state_value = StateCategory.UNKNOW.value

        logger.debug(f"State updated. state_value: {self.state_value}")    

        

    # VALIDATION METHODS
    #(object_type, object_id, success_ratio, health)
    def _validate_init_params(self, object_type: str, object_id: str, success_ratio: Optional[float], 
                            health: Optional[float]) -> None:
        """Validate initialization parameters."""
        if not isinstance(object_type, str) or not object_type:
            raise ValueError("object_type must be a non-empty string")
        
        if not isinstance(object_id, str) or not object_id:
            raise ValueError("object_id must be a non-empty string")
        
        if success_ratio is not None and not isinstance(success_ratio, float) and success_ratio >= 0:
            raise TypeError("success_ratio must be a float not negative")
        # Puoi aggiungere validazioni per gli elementi della lista limes se Limes ha un tipo specifico
        
        if health is not None and not isinstance(health, float) and health >= 0:
            raise TypeError("health must be a float not negative")
        
        
                    


    def __repr__(self) -> str:
        """String representation of the Region."""
        return (f"State(object_type='{self._object_type}', object_id='{self._object_id}', "
                f"success_ratio={self._success_ratio}, health={self._health}, state_value={self._state_value})")
    
    def __str__(self) -> str:
        """Readable string representation."""
        return f"State(object_type='{self._object_type}', object_id='{self._object_id}', state_value={self._state_value})"
    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)