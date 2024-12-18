import random
import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Block')

# ASSET o BLOCK
class Block:    

    def __init__(self, name = None, description = None, category = None, function = None, value = None, acp = None, rcp = None, payload = None):

            # propriety
            self._name = name # block name - type str
            self._id = None # id self-assigned - type str
            self._description = description # block description - type str
            self._category = category # block category - type Literal
            self._function = function # block function - type str
            self._value = value # block value - type int            
            self._acs = acp # assigned consume profile - type Payload
            self._rcs = rcp # requested consume profile - type Payload            
            self._payload = None # block payload - type Payload
            
            # Association      
            self._state = State(self._name) # block state - type State

            # check input parameters
            if not self.checkParam( name, description, category, function, value, acp, rcp, payload ):
                raise Exception("Invalid parameters! Object not istantiate.")


            if not name:
                self._name = Utility.setName('Unamed_Block')

            else:
                self._name = "Block." + name

            self._id = Utility.setId(self._name, None)
           
            
            


    # methods

    def setState(self, state):

        if not state or not isinstance(state, State):
            self._state = State( name = "State." + self._name )

        else:
            self._state = state

        return True

    def getState(self):
        return self._state


    def setId(self, id):

        if not id:
            return False

        elif isinstance(id, str):
            self._id = id       
        
        else:
            self._id = str( id )       
            
        return True
    
    
    def getId(self):
        return self._id



    def setName(self, name):

        if not name:
            return False
        else:
            self._name = name

        return True
            

    def getName(self):
        return self._name


    def to_string(self):
        return 'Name: {0}  -  Id: {1}'.format(self.getName(), str(self._id))
    
    def checkBlockClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        if not object or not isinstance(object, Block):
            return False
        
        return True

    def checkBlockList(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""

        if objects and isinstance(objects, list) and all( isinstance(object, Block) for object in objects ):
            return True

        return False


     # vedi il libro
    def checkParam(name: str, description: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload) -> bool:
        """Return True if type compliance of the parameters is verified"""   
    
        # Controlla se i tipi dei parametri sono conformi
        if not isinstance(name, str):
            return False
        if not isinstance(description, str):
            return False
        if not isinstance(category, Literal) or category not in [CATEGORY, MIL_CATEGORY]:                        
            return False        
        if not isinstance(function, str):
            return False
        if not isinstance(value, int):
            return False
        if not isinstance(position, Point):
            return False
        if not isinstance(acs, Payload):
            return False        
        if not isinstance(rcs, Payload):
            return False        
        if not isinstance(payload, Payload):
            return False
            
        return True
    
    def destroy( self ):
        """Destroy this object"""

        for ev in self._eventsQueue:
            ev.destroy()

        self._state.destroy()
        self._coord = None
        self._eventsQueue = None        
        logger.logger.debug("Object: {0} destroyed".format( self._name ) )
        return True


    def efficiency(self): # sostituisce operational()
        """calculate efficiency from asset state, rcp, acp, .."""
        # efficiency = state * acp / rcp
        # return efficiency
        pass
        
    def value(self):
        """calculate Value from asset Value"""
        # Value = median(assetValue)
        # return Value
        pass

    def cost(self):
        """calculate cost from asset cost """
        # cost = sum(assetCost)
        # return cost
        pass

    def rcp(self):
        """calculate request consume payload (rcp) from asset rcp"""
        # rcp = sum(assetRcp) 
        # return rcp
        pass

    def acp(self):
        """calculate assigned consume payload (acp) from asset acp"""
        # acp = sum(assetAcp) 
        # return acp
        pass

    def payload(self):
        """calculate payload from asset payload"""
        # pl = sum(assetPayload) 
        # return pl
        pass

    def asset_status(self):
        """calculate Asset_Status from asset Asset_Status"""
        # as = median(Asset_Status) 
        # return as
        pass

    def threat_volume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    def position(self):
        """calculate position from asset position"""
        # ap = median(assetPosition) 
        # return ap
        pass

