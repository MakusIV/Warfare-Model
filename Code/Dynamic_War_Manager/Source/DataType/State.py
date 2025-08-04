"""
 CLASS State
 
 Rappresenta lo stato di un oggetto di classe Block, di cui è uno dei componenti necessari.
 L'associazione tra State e Block è di 1 a 1.

 ATTRIBUTI:
    _ID: string
    _damage: float [0:1]
    _state_value: string {Active, Inactive, Standby, Destroyed}

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

OPERATIVE_MIN_HEALTH = 0.4 # minimum healt level for operative status
DESTROYED_HEALTH_LEVEL = 0.15 # minimum healt level for not destroyed status
CRITICAL_HEALTH_LEVEL = 0.5 # minimum healt level for not critical status

class StateCategory(Enum):
    HEALTHFUL = "Healtful"
    DAMAGED = "Damaged"
    CRITICAL = "Critical"
    DESTROYED = "Destroyed"


HEALTH_LEVEL = {    
    StateCategory.DAMAGED.value: 0.8,
    StateCategory.CRITICAL.value: 0.5,
    StateCategory.DESTROYED.value: 0.15
}

class State:

    def __init__(self, success_ratio: float =  None, state: str = None): 
        
        
        # property        
        #         
        self._success_ratio = {} # ("Block_ID", "Block_Name"): float) # per mil: mission_success_ratio, per prod, storage, transport = random_anomaly (anomalie di produzione, trasporto ecc generate casualmente in funzione del livello di goods (ricambi):  random(0, rcp_goods / acp _goods))        
        self._health = 0.0 # health  - float := [0:1]
        self._state_value =  StateCategory.HEALTHFUL.value # Healthful, Damaged, Critical, Destroyed
        

   

    @property        
    def health(self):
        return self._health
    
    @health.setter
    def health(self, health):
        
        if not isinstance(health, float):
            raise TypeError("type not valid, float type expected")
        
        self._health = health


    @property        
    def success_ratio(self):
        return self._success_ratio
    
    @success_ratio.setter
    def success_ratio(self, success_ratio):
        
        if not isinstance(success_ratio, float):
            raise TypeError("type not valid, float type expected")
        
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

        return True


    def isOperative(self):
        return self._state_value == StateCategory.HEALTHFUL.value or ( self._state_value == StateCategory.DAMAGED.value and self._health >= OPERATIVE_MIN_HEALTH)
    
    def isDestroyed(self):
        return self._state_value == StateCategory.DESTROYED.value

    def isDamaged(self):
        return self._state_value == StateCategory.DAMAGED.value
    
    def isCritical(self):
        return self._state_value == StateCategory.CRITICAL.value

    
    def update(self) -> bool:
        
        if not self._state_value:
            return False        
        
        if self._health < HEALTH_LEVEL[StateCategory.DESTROYED.value]:
            self._state_value = StateCategory.DESTROYED.value

        elif self._health < HEALTH_LEVEL[StateCategory.CRITICAL.value]:
            self._state_value = StateCategory.CRITICAL.value

        elif self._health < HEALTH_LEVEL[StateCategory.DAMAGED.value]:
            self._state_value = StateCategory.DAMAGED.value

        else:
            self._state_value = StateCategory.HEALTHFUL.value
        
        return
        

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)