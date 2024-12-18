"""
 CLASS State
 
 Rappresenta lo stato di un Block

"""

from LoggerClass import Logger
from Context import STATE
import Utility

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')

class State:

    def __init__(self, parent_name = "unamed_parent", parent_id = None): 
            
            self._ID =  parent_name + Utility.setId(parent_name, parent_id) # name - string
            self._damage = 0.0 # damage  - float := [0:1]
            self._state_value =  STATE.Inactive # Active, Inactive, Standby, Destroyed
            
            
    def getDamage(self):
        return self._damage


    def getState(self):
        return self._state_value
    

    def setStateValue(self, state_value):
        if not state_value or not isinstance(state_value, str):
            raise ValueError("type not valid, str type expected")
        
        elif state_value not in [STATE]:
            value = [v for v in STATE]
            str_value = ', '.join(value)
            raise ValueError("value not valid: " + state_value + ". Value expected: \n" + str_value)
        
        else:
            self._state_value = state_value

        return True


   

    def toString(self):
        return "name: " + self._name + ", damage: " + str(self._damage) + ", state:value: " + self._state_value
            

    def isActive(self):
        return self._state_value == STATE.Active               
    
    def isInactive(self):
        return self._state_value == STATE.Inactive

    def isDestroyed(self):
        return self._state_value == STATE.Destroyed

    def isDamaged(self):
        return self._state_value == STATE.Damaged
    
    def isCritical(self):
        return self._damage <= 0.3

    def checkState(self):
        
        if self._damage >= 1:
            self._state_value = STATE.Destroyed

        elif self._damage > 0:
            self._state_value = STATE.Damaged

        

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)