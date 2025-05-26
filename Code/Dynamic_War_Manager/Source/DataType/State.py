"""
 CLASS State
 
 Rappresenta lo stato di un oggetto di classe Block, di cui è uno dei componenti necessari.
 L'associazione tra State e Block è di 1 a 1.

 ATTRIBUTI:
    _ID: string
    _damage: float [0:1]
    _state_value: string {Active, Inactive, Standby, Destroyed}

"""

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')

class State:

    def __init__(self, success_ratio: float =  None, state: str = None): 
        
        
        # property        
        #         
        self._success_ratio = {} # ("Block_ID", "Block_Name"): float) # per mil: mission_success_ratio, per prod, storage, transport = random_anomaly (anomalie di produzione, trasporto ecc generate casualmente in funzione del livello di goods (ricambi):  random(0, rcp_goods / acp _goods))        
        self._health = 0.0 # health  - float := [0:1]
        self._state_value =  None # Operational, Not_Operational, Damaged, Critical, Destroyed
        

   

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
        
        elif state_value not in STATE.keys:
            value = [v for v in STATE.keys]
            str_value = ', '.join(value)
            raise ValueError("value not valid: " + state_value + ". Value expected: \n" + str_value)
        
        else:
            self._state_value = state_value

        return True


    def isOperational(self):
        return self._state_value == STATE["Operational"]               
    
    def isNotOperational(self):
        return self._state_value == STATE["Not_Operational"]

    def isDestroyed(self):
        return self._state_value == STATE["Destroyed"]

    def isDamaged(self):
        return self._state_value == STATE["Damaged"]
    
    def isCritical(self):
        return self._state_value == STATE["Critical"]

    
    def update(self) -> bool:
        
        if not self._state_value:
            return False        
        
        if self._health < 0.1:
            self._state_value = STATE["Destroyed"]

        elif self._health < 0.3:
            self._state_value = STATE["Not_Operational"]
        
        elif self._health < 0.5:
            self._state_value = STATE["Critical"]

        elif self._health < 0.8:
            self._state_value = STATE["Damaged"]

        else:
            self._state_value = STATE["Operational"]
        
        return True
        

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)