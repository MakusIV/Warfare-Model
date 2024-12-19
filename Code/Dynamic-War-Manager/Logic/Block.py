import random
import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Payload import Payload
from Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Block')

# ASSET o BLOCK
class Block:    

    def __init__(self, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None):

            # propriety
            self._name = name # block name - type str
            self._id = None # id self-assigned - type str
            self._description = description # block description - type str
            self._category = category # block category - type Literal
            self._functionality = functionality # block functionality - type str
            self._value = value # block value - type int             
            self._event = List[Event] = [] # block event - list of Block event's          

            # Association    
            self._state = State(self) # block state- component of Block - type State  
            self._acp = acp # assigned consume profile - component of Block - type Payload -
            self._rcp = rcp # requested consume profile - component of Block - type Payload            
            self._payload = payload # block payload - component of Block - type Payload
            self._asset = Dict[str, Asset]= {} # assets - component of Block - type list forse è meglio un dict

            # check input parameters
            if not self.checkParam( name, description, category, functionality, value, acp, rcp, payload ):
                raise Exception("Invalid parameters! Object not istantiate.")


            if not name:
                self._name = Utility.setName('Unnamed_Block')

            else:
                self._name = "Block." + name

            self._id = Utility.setId(self._name)
           
            if not acp:
                acp = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)
            
            if not rcp:
                rcp = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)

            if not payload:
                payload = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)

    # methods

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):

        if not isinstance(id, str):
            raise TypeError("type not valid, str type expected")

        self._name = id    
        return True
            
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):

        if not ( isinstance(id, int) or isinstance(id, str) ):
            raise TypeError("type not valid, int or str type expected")

        elif isinstance(id, int):
            self._id = str( id )       
        
        else:
            self._id = id 
            
        return True
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, id):

        if not isinstance(id, str):
            raise TypeError("type not valid, str type expected")
        
        self._description = id       
            
        return True
    
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, id):

        if not isinstance(id, str):
            raise TypeError("type not valid, str type expected")
        
        self._category = id    

        return True
    

    @property
    def functionality(self):
        return self._functionality

    @functionality.setter
    def functionality(self, id):

        if not isinstance(id, str):
            raise TypeError("type not valid, str type expected")

        self._functionality = id    
            
        return True
    

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, id):

        if not ( isinstance(id, int) or isinstance(id, str) ):
            raise TypeError("type not valid, int or str type expected")

        elif isinstance(id, int):
            self._value = str( id )       
        
        else:
            self._value = id
            
        return True
    

    @property
    def cost(self) -> int:

        cost = 0

        for asset in self.assets:
            cost += asset.cost

        return cost

    


    @property
    def state(self):

        if not self._state:
           raise ValueError("state not defined")
                
        return self._state
    
    # questo metodo non serve in quanto la costruzione di state presuppone una istanza di Block. Questa funzione verifica solo se l'associazioneè presente
    @state.setter
    def state(self, state) -> bool:

        if not not isinstance(state, State):
            raise TypeError("type not valid, State Class expected")

        else:
            if not self._state or self._state != state: 
                raise ValueError("invalid construction of state object: parent association not defined during construction")

        return True

    
    @property
    def acp(self) -> Payload:
        return self._acp


    @acp.setter
    def acp(self, payload: Payload) -> bool:

        if not isinstance(payload, Payload):
            raise TypeError("type not valid, Payload Class expected")

        else:
            self._acp = payload             
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True
    

    @property
    def rcp(self) -> Payload:
        return self._rcp


    @rcp.setter
    def rcp(self, payload: Payload) -> bool:

        if not isinstance(payload, Payload):
            raise TypeError("type not valid, Payload Class expected")

        else:
            self._rcp = payload             
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True


    @property
    def payload(self) -> Payload:
        return self._payload


    @payload.setter
    def payload(self, payload: Payload) -> bool:

        if not isinstance(payload, Payload):
            raise TypeError("type not valid, Payload Class expected")

        else:
            self._payload = payload             
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True



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

