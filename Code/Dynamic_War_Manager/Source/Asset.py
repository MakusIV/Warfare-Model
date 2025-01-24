"""
Asset Class

Nota: rappresenta unit -> group -> country -> coalition (DCS)
Il Block può essere costituito da diversi gruppi apparenenti a country diverse della stessa coalizione

"""


from Dynamic_War_Manager.Source.Block import Block
import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Volume import Volume
from Dynamic_War_Manager.Source.Threat import Threat
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, CATEGORY, MIL_CATEGORY, COUNTRY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from Dynamic_War_Manager.Source.Region import Region

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Asset')

# ASSET
class Asset(Block) :    

    def __init__(self, block: Block, name: str|None = None, description: str|None = None, category: str|None = None, functionality: str|None = None, value: int|None = None, cost: int|None = None, acp: Payload|None = None, rcp: Payload|None = None, payload: Payload|None = None, position: Point|None = None, volume: Volume|None = None, threat: Threat|None = None, crytical: bool|None = False, repair_time: int|None = 0, region: Region|None = None, country: str|None = None):      
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, region)

            # propriety             
            self._position: int|None = position # asset position - type Point (3D -> anche l'altezza deve essere considerata per la presenza di rilievi nel terreno)
            self._cost: int|None = cost # asset cost - type int 
            self._crytical: bool|None = crytical 
            self._repair_time: int|None = repair_time
            
            
            
            self._unit_index: str|Dict = None # DCS group unit_index - index Dict            
            self._unit_name: str|None = None # DCS unit group name - str
            self._unit_type: str|None = None # DCS unit group type - str
            self._unit_unitId: int|None = None # DCS unit group id - int
            self._unit_communication: bool|None = None # DCS unit group communication - bool
            self._unit_lateActivation: bool|None = None # DCS unit group lateActivation - bool
            self._unit_start_time: int|None = None # DCS unit group start_time - int
            self._unit_frequency: float|None = None # DCS unit group frequency - float
            self._unit_x: float|None = None # DCS unit x - float
            self._unit_y: float|None = None # DCS unit y - float
            self._unit_alt: float|None = None # DCS unit altitude - float
            self._unit_alt_type: str|None = None # DCS unit altitude type - str (BARO, ...)
            self._heading: int|None = None # DCS unit heading - int
            self._unit_speed: float|None = None # DCS unit speed - float
            self._unit_hardpoint_racks: int|None = None # DCS unit hardpoint_racks - int
            self._unit_livery_id: int|None = None # DCS unit livery_id - int
            self._unit_psi: float|None = None # DCS unit psi - float
            self._unit_skill: str|None = None # DCS unit skill - Literal (Average, ....)
            self._unit_onboard_num: int|None = None # DCS unit onboard_num - int
            self._unit_payload: str|Dict = None # DCS unit payload - Dict
            self._unit_callsign: str|Dict = None  # DCS unit callsign - Dict

            # Association    
            self._volume: int|Volume = volume
            self._threat: int|Threat = threat
            self._block: int|Block = block # asset block - component of Block - type Block asset not exist without block
           
            # check input parameters
            check_results =  self.checkParam( name, description, category, functionality, value, acp, rcp, payload, position, volume, threat, crytical, repair_time, region, country )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")

    # methods

    @property
    def cost(self) -> int: #override      
        return self._cost

    @cost.setter
    def cost(self, cost) -> bool: #override
        check_result = self.checkParam(cost)
        
        if not check_result[1]:
            raise Exception(check_result[2])                        
        self._cost = cost
        return True
    
    @property
    def crytical(self) -> int: #override      
        return self._crytical

    @crytical.setter
    def crytical(self, crytical) -> bool: #override
        check_result = self.checkParam(crytical)
        
        if not check_result[1]:
            raise Exception(check_result[2])                
        self._crytical = crytical
        return True
    
    @property
    def repair_time(self) -> int: #override      
        return self._repair_time

    @repair_time.setter
    def repair_time(self, repair_time) -> bool: #override
        
        check_result = self.checkParam(repair_time)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._repair_time = repair_time
        return True

    @property
    def country(self) -> str: #override      
        return self._country
    
    @country.setter
    def country(self, param) -> bool: #override
        
        check_result = self.checkParam(country = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._country = param
        return True
    
    @property
    def position(self) -> Point: #override      
        return self._position
    
    @position.setter
    def position(self, param) -> bool: #override
        
        check_result = self.checkParam(position = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._position = param
        return True

    @property
    def volume(self) -> Volume: #override      
        return self._volume
    
    @volume.setter
    def volume(self, param) -> bool: #override
        
        check_result = self.checkParam(volume = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._volume = param
        return True
    
    @property
    def threat(self) -> Threat: #override      
        return self._threat
    
    @threat.setter
    def threat(self, param) -> bool: #override
        
        check_result = self.checkParam(threat = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._threat = param
        return True
    
    @property
    def block(self):
        return self._block
    
    @block.setter
    def block(self, param):
        check_result = self.checkParam(block = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        
        if param.get_asset(self._id).get_id() != self._id:
            raise Exception("Association Incongruence: this Asset id is present like a key in Block association dictionary, but Asset object has different id")
        
        self._block = param
        return True


    def checkParam(name: str, description: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload, volume: Volume, threat: Threat, crytical: bool, repair_time: int, cost: int, country: str, block: Block) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
    
        check_super_result = super().checkParam(name, description, category, function, value, position, acs, rcs, payload)

        if not check_super_result[1]:
            return (False, check_super_result[2])     
        
        if position and not isinstance(position, Point):
            return (False, "Bad Arg: position must be a Point object")
        
        if block and not isinstance(block, Block):
            return (False, "Bad Arg: block must be a Block object")
        
        if volume and not isinstance(volume, Volume):
            return (False, "Bad Arg: volume must be a Volume object")
        
        if threat and not isinstance(threat, Threat):                        
            return (False, "Bad Arg: threat must be a Threat object")   
             
        if repair_time and not isinstance(repair_time, int):
            return (False, "Bad Arg: repair_time must be a int")
        
        if cost and not isinstance(repair_time, int):
            return (False, "Bad Arg: cost must be a int")        

        return (True, "parameters ok")
    
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

    def calc_position(self):
        """calculate position from asset position"""
        # ap = median(assetPosition) 
        # return ap
        pass

    @property #overload
    def assets(self):
        raise Exception("Metodo non implementato in questa classe")
     
    @assets.setter #overload
    def assets(self, value):
            raise Exception("Metodo non implementato in questa classe")

    def get_Asset(self, key): #overload
            raise Exception("Metodo non implementato in questa classe")

    def set_Asset(self, key, value): #overload
            raise Exception("Metodo non implementato in questa classe")

    def remove_Asset(self, key):#overload
            raise Exception("Metodo non implementato in questa classe")
  