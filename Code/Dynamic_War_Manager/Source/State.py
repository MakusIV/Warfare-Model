"""
 CLASS State
 
 Rappresenta lo stato di un oggetto di classe Block, di cui è uno dei componenti necessari.
 L'associazione tra State e Block è di 1 a 1.

 ATTRIBUTI:
    _ID: string
    _damage: float [0:1]
    _state_value: string {Active, Inactive, Standby, Destroyed}

"""

from Code.LoggerClass import Logger
from Code.Context import STATE
import Block, Utility

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')

class State:

    def __init__(self, parent:Block): 
        
        if not isinstance(parent, Block):
            raise TypeError("type not valid, Block Class expected")

        # property        
        self._damage = 0.0 # damage  - float := [0:1]
        self._state_value =  STATE.Inactive # Active, Inactive, Standby, Destroyed
        
        # association
        self._parent = parent
        parent.state = self 



    @property        
    def damage(self):
        return self._damage
    
    @damage.setter
    def damage(self, damage):
        
        if not isinstance(damage, float):
            raise TypeError("type not valid, float type expected")
        
        self._damage = damage

    @property
    def state_value(self):
        return self._state_value
    
    @state_value.setter
    def state_value(self, state_value):
        
        if not isinstance(state_value, str):
            raise TypeError("type not valid, str type expected")
        
        elif state_value not in [STATE]:
            value = [v for v in STATE]
            str_value = ', '.join(value)
            raise ValueError("value not valid: " + state_value + ". Value expected: \n" + str_value)
        
        else:
            self._state_value = state_value

        return True

  
   
    @property        
    def parent(self):
        """Get the parent Block associated with this State.

        Raises:
            ValueError: If the parent is not defined.

        Returns:
            Block: The parent Block object.
        """

        if not self._parent:
            raise ValueError("parent not defined")
        
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        
        """
        Set the parent Block associated with this State.

        Raises:
            TypeError: If the parent is not an instance of Block.
            ValueError: If the parent already has a State defined.

        """
        if not isinstance(parent, Block):
                raise TypeError("type not valid, Block Class expected")
        
        if parent.state:
            raise ValueError("parent state already defined")
        
        self._parent = parent   
        parent.state = self
        

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