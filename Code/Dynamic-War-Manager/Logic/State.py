"""
 CLASS State
 
 Rappresenta lo stato di un asset

"""

from LoggerClass import Logger
from Context import STATE

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')

class State:

    def __init__(self, name = "no_name"): 
            
            self._name = name
            self._damage = 0 # asset damage float := [0:1]
            self._state =  STATE.Inactive # Active, Inactive, Standby, Destroyed
            
            
    def getDamage(self):
        return self._damage


    def getState(self):
        return self._state


    def updateEfficiency(self):
        """Update efficiency from energy and health levels ad return efficiency level"""
        # unit test: ok

        self._efficiency = int( round( self._energy * self._health / 100 ) )
        return self._efficiency

    
    def evalutateAnomaly(self):
        """Update anomaly state from efficiency level and return it"""
        # unit test: ok

        if (self._efficiency <= 30):
            self.setAnomaly(True)
        
        return self._anomaly
        

    def evalutateCritical(self):
        """Upgrade critical state from health level and return it"""
        # unit test: ok

        if (self._health <= 30 ):
            self.setCritical(True)
        
        return self._critical


    def setCritical(self, value):

        if not self._active or self._destroy or self._remove:
            return False

        self._critical = value
        self.checkState()

        return True


    def setAnomaly(self, value):

        if not self._active or self._destroy or self._remove:
            return False

        self._anomaly = value
        self.checkState()

        return True


    def toString(self):
        return "active: " + str(self._active) + ", run: " + str(self._run) + ", remove: " + str(self._remove) + ", destroy: " + str(self._destroy) + ", anomaly: " + str(self._anomaly) + ", critical: " + str(self._critical) 
            

    def isActive(self):
        return self._active            


    def isRunning(self):
        return self._run            


    def isDestroyed(self):
        return self._destroy


    def isRemoved(self):
        return self._remove

    def isAnomaly(self):
        return self._anomaly
    
    def isCritical(self):
        return self._critical


    def checkState(self):
        """Check state and return true if correct state is verificated or raise Exception for state anomaly"""
        # unit test: ok

        wrongState = ( self._active and self._remove ) or ( self._run and ( not self._active or self._destroy or self._remove) ) 

        if wrongState:
            raise Exception("Anomaly state!")

        return True
       


    def checkStateClass(self, state):

        if not state or not isinstance(state, State):
            return False
        
        return True


    

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)