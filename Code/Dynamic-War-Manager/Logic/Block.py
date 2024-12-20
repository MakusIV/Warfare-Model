from Utility import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Payload import Payload
from Context import STATE, CATEGORY, MIL_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And
from Asset import Asset

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Block')

# ASSET o BLOCK
class Block:    

    def __init__(self, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, region: Region = None):

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
            self._region = region # block map region - type Region

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
            raise TypeError("Invalid parameters! Type not valid, str type expected")

        self._name = id    
        return True
            
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):

        if not ( isinstance(id, int) or isinstance(id, str) ):
            raise TypeError("Invalid parameters! Type not valid, int or str type expected")

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
            raise TypeError("Invalid parameters! Type not valid, str type expected")
        
        self._description = id       
            
        return True
    
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, id):

        if not isinstance(id, str):
            raise TypeError("Invalid parameters! Type not valid, str type expected")
        
        self._category = id    

        return True
    

    @property
    def functionality(self):
        return self._functionality

    @functionality.setter
    def functionality(self, id):

        if not isinstance(id, str):
            raise TypeError("Invalid parameters! Type not valid, str type expected")

        self._functionality = id    
            
        return True
    

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, id):

        if not ( isinstance(id, int) or isinstance(id, str) ):
            raise TypeError("Invalid parameters! Type not valid, int or str type expected")

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
    
    @cost.setter
    def cost(self, cost):
        raise ValueError("cost not modifiable for Block")
    


    @property
    def state(self):

        if not self._state:
           raise ValueError("state not defined")
                
        return self._state
    
    # questo metodo non serve in quanto la costruzione di state presuppone una istanza di Block. Questa funzione verifica solo se l'associazioneè presente
    @state.setter
    def state(self, state) -> bool:

        if not not isinstance(state, State):
            raise TypeError("Invalid parameters! Type not valid, State Class expected")

        else:
            if not self._state or self._state != state: 
                raise ValueError("Invalid construction of state: parent association not defined during construction")

        return True

    
    @property
    def acp(self) -> Payload:
        return self._acp


    @acp.setter
    def acp(self, payload: Payload) -> bool:

        if not isinstance(payload, Payload):
            raise TypeError("Invalid parameters! Type not valid, Payload Class expected")

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
            raise TypeError("Invalid parameters! Type not valid, Payload Class expected")

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
            raise TypeError("Invalid parameters! Type not valid, Payload Class expected")

        else:
            self._payload = payload             
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, id):

        if not isinstance(id, Region):
            raise TypeError("Invalid parameters! Type not valid, Region type expected")
        
        self._region = id       
            
        return True


    def to_string(self):
        return 'Name: {0}  -  Id: {1}'.format(self.getName(), str(self._id))
    
    def checkClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        return type(object) == type(self)
        

    def checkClassList(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""
        return all(type(obj) == type(self) for obj in objects)


     # vedi il libro
    def checkParam(name: str, description: str, category: Literal, function: str, value: int, position: Point, acp: Payload, rcp: Payload, payload: Payload) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
                   
        if not isinstance(name, str):
            return False
        if description and not isinstance(description, str):
            return False
        if category and (not isinstance(category, Literal) or category not in [CATEGORY, MIL_CATEGORY]):                        
            return False        
        if function and not isinstance(function, str):
            return False
        if value and not isinstance(value, int):
            return False
        if position and not isinstance(position, Point):
            return False
        if acp and not isinstance(acp, Payload):
            return False        
        if rcp and not isinstance(rcp, Payload):
            return False        
        if payload and not isinstance(payload, Payload):
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

