"""
Asset Class

Nota: rappresenta unit -> group -> country -> coalition (DCS)
Il Block può essere costituito da diversi gruppi apparenenti a country diverse della stessa coalizione

"""


from Block import Block
from Utility import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Payload import Payload
from Context import STATE, CATEGORY, MIL_CATEGORY, COUNTRY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And
from Region import Region

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Asset')

# ASSET
class Asset(Block) :    

    def __init__(self, block: Block, name: str = None, description: str = None, category: str = None, functionality: str = None, value: int = None, cost: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point = None, volume: Volume = None, threat: Threat = None, crytical: bool = False, repair_time: int = 0, region: Region = None, country: str = None):      
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, region, nationality)

            # propriety             
            self._position = position # asset position - type Point (3D -> anche l'altezza deve essere considerata per la presenza di rilievi nel terreno)
            self._cost = cost # asset cost - type int 
            self._crytical = crytical 
            self._repair_time = repair_time
            self._country = country # DCS country name - str
            self._side # DCS country side - str             
            self._country_id # DCS country id
            self._country_bullseye # DCS country side bullseye
            self._nav_points_side # DCS side nav_points 
            self._category_country_group # DCS country category (ship, helicopter, vehicle, plane, static)
            self._group_index # DCS country group index
            self._group_modulation # DCS group modulation            
            self._group_task  # DCS group task (CAS, ...) - str
            self._group_radioSet # DCS group radioset - bool
            self._group_uncontrolled  # DCS group uncontrolled - bool
            self._group_taskSelected  # DCS group task selected - bool
            self._group_groupId # DCS group id - int
            self._group_hidden # DCS group hidden - bool
            self._group_x # DCS group x - float
            self._group_y # DCS group y - float
            self._group_name # DCS group name - str
            self._group_communication # DCS group communication - bool
            self._group_lateActivation # DCS group lateActivation - bool
            self._group_start_time # DCS group start_time - int
            self._group_frequency # DCS group frequency - float
            self._group_tasks # DCS group tasks - index Dict
            self._group_route # DCS group route - index Dict
            
            self._unit_index # DCS group unit_index - index Dict            
            self._unit_name # DCS unit group name - str
            self._unit_type # DCS unit group type - str
            self._unit_unitId # DCS unit group id - int
            self._unit_communication # DCS unit group communication - bool
            self._unit_lateActivation # DCS unit group lateActivation - bool
            self._unit_start_time # DCS unit group start_time - int
            self._unit_frequency # DCS unit group frequency - float
            self._unit_x # DCS unit x - float
            self._unit_y # DCS unit y - float
            self._unit_alt # DCS unit altitude - float
            self._unit_alt_type # DCS unit altitude type - str (BARO, ...)
            self._heading # DCS unit heading - int
            self._unit_speed # DCS unit speed - float
            self._unit_hardpoint_racks # DCS unit hardpoint_racks - int
            self._unit_livery_id # DCS unit livery_id - int
            self._unit_psi # DCS unit psi - float
            self._unit_skill # DCS unit skill - Literal (Average, ....)
            self._unit_onboard_num # DCS unit onboard_num - int
            self._unit_payload # DCS unit payload - Dict
            self._unit_callsign  # DCS unit callsign - Dict

            # Association    
            self._volume = volume
            self._threat = threat
            self._block = block # asset block - component of Block - type Block asset not exist without block
           
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
    
    @nationality.setter
    def nationality(self, param) -> bool: #override
        
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
    
    

    def checkParam(name: str, description: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload, position: Point, volume: Volume, threat: Threat, crytical: bool, repair_time: int, cost: int, country: str) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
    
        chek_super_result = super().checkParam(name, description, category, function, value, position, acs, rcs, payload)

        if not check_super_result[1]:
            return (False, check_super_result[2])     
        
        if position and not isinstance(position, Point):
            return (False, "Bad Arg: position must be a Point object")
        
        if volume and not isinstance(volume, Volume):
            return (False, "Bad Arg: volume must be a Volume object")
        
        if threat and not isinstance(threat, Threat):                        
            return (False, "Bad Arg: threat must be a Threat object")   
             
        if repair_time and not isinstance(repair_time, int):
            return (False, "Bad Arg: repair_time must be a int")
        
        if cost and not isinstance(repair_time, int):
            return (False, "Bad Arg: cost must be a int")
        
        if country and not (country in COUNTRY):
            return (False, "Bad Arg: nationality must be a Literal.COUNTRY")

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

    def getAsset(self, key): #overload
            raise Exception("Metodo non implementato in questa classe")

    def setAsset(self, key, value): #overload
            raise Exception("Metodo non implementato in questa classe")

    def removeAsset(self, key):#overload
            raise Exception("Metodo non implementato in questa classe")
  