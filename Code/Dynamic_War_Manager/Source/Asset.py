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
from Context import STATE, MIL_CATEGORY, COUNTRY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from Dynamic_War_Manager.Source.Region import Region

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Asset')

# ASSET
class Asset(Block) :    

    def __init__(self, block: Block, name: str|None = None, description: str|None = None, category: str|None = None, functionality: str|None = None, value: int|None = None, cost: int|None = None, acp: Payload|None = None, rcp: Payload|None = None, payload: Payload|None = None, position: Point|None = None, volume: Volume|None = None, threat: Threat|None = None, crytical: bool|None = False, repair_time: int|None = 0, region: Region|None = None, country: str|None = None, role: str|None = None, health: int|None = None, unit_index: str|Dict = None, unit_name: str|None = None, unit_type: str|None = None, unit_unitId: int|None = None, unit_communication: bool|None = None, unit_lateActivation: bool|None = None, unit_start_time: int|None = None, unit_frequency: float|None = None, unit_x: float|None = None, unit_y: float|None = None, unit_alt: float|None = None, unit_alt_type: str|None = None, heading: int|None = None, unit_speed: float|None = None, unit_hardpoint_racks: int|None = None, unit_livery_id: int|None = None, unit_psi: float|None = None, unit_skill: str|None = None, unit_onboard_num: int|None = None, unit_payload: str|Dict = None, unit_callsign: str|Dict = None): # type: ignore   
            
            super().__init__(name, description, category, functionality, value, acp, rcp, payload, region)

            # propriety             
            self._position: Point|None = position # asset position - type Point (3D -> anche l'altezza deve essere considerata per la presenza di rilievi nel terreno)
            self._cost: int|None = cost # asset cost - type int 
            self._crytical: bool|None = crytical 
            self._repair_time: int|None = repair_time
            self._role: str|None = role # asset role - type str Recon, Interdiction, ReconAndInterdiction, defence, attack, support, transport, storage (energy, goods, ..)
            
            
            self._unit_index: str|Dict|None = unit_index # DCS group unit_index - index Dict            
            self._unit_name: str|None = unit_name # DCS unit group name - str
            self._unit_type: str|None = unit_type # DCS unit group type - str
            self._unit_unitId: int|None = unit_unitId # DCS unit group id - int
            self._unit_communication: bool|None = unit_communication # DCS unit group communication - bool
            self._unit_lateActivation: bool|None = unit_lateActivation # DCS unit group lateActivation - bool
            self._unit_start_time: int|None = unit_start_time # DCS unit group start_time - int
            self._unit_frequency: float|None = unit_frequency # DCS unit group frequency - float
            self._unit_x: float|None = unit_x # DCS unit x - float
            self._unit_y: float|None = unit_y # DCS unit y - float
            self._unit_alt: float|None = unit_alt # DCS unit altitude - float
            self._unit_alt_type: str|None = unit_alt_type # DCS unit altitude type - str (BARO, ...)
            self._heading: int|None = heading # DCS unit heading - int
            self._unit_speed: float|None = unit_speed # DCS unit speed - float
            self._unit_hardpoint_racks: int|None = unit_hardpoint_racks # DCS unit hardpoint_racks - int
            self._unit_livery_id: int|None = unit_livery_id # DCS unit livery_id - int
            self._unit_psi: float|None = unit_psi # DCS unit psi - float
            self._unit_skill: str|None = unit_skill # DCS unit skill - Literal (Average, ....)
            self._unit_onboard_num: int|None = unit_onboard_num # DCS unit onboard_num - int
            self._unit_payload: str|Dict|None = unit_payload # DCS unit payload - Dict
            self._unit_callsign: str|Dict|None = unit_callsign  # DCS unit callsign - Dict

            self._unit_health: int|None = health # DCS unit health - int [0-100] DEVI VEDERE NEI FILE TEMPORANEI GENERATI DOPO LA CONSLUSIONE DI UNA MISSIONE E PIMA DEL PROCESSAMENTO CON DCE

            # Association    
            self._volume: int|Volume|None = volume
            self._threat: int|Threat|None = threat
            self._block: int|Block = block # asset block - component of Block - type Block asset not exist without block
           
            # check input parameters
            check_results =  self.checkParam( name, description, category, functionality, position, volume, threat, crytical, repair_time, country, role, health )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")

    # getter & setter methods

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
    def health(self) -> int: #override      
        return self._unit_health

    @health.setter
    def cost(self, health) -> bool: #override
        check_result = self.checkParam(health)
        
        if not check_result[1]:
            raise Exception(check_result[2])                        
        self._unit_health = health
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
    def role(self) -> str: #override
        return self._role    

    @role.setter    
    def role(self, role) -> bool: #override
        
        check_result = self.checkParam(role)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._role = role
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
    def unit_index(self):
        return self._unit_index

    @unit_index.setter
    def unit_index(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_index = value
        return True

    @property
    def unit_name(self):
        return self._unit_name

    @unit_name.setter
    def unit_name(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_name = value
        return True

    @property
    def unit_type(self):
        return self._unit_type

    @unit_type.setter
    def unit_type(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_type = value
        return True

    @property
    def unit_unitId(self):
        return self._unit_unitId

    @unit_unitId.setter
    def unit_unitId(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_unitId = value
        return True

    @property
    def unit_communication(self):
        return self._unit_communication

    @unit_communication.setter
    def unit_communication(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_communication = value
        return True

    @property
    def unit_lateActivation(self):
        return self._unit_lateActivation

    @unit_lateActivation.setter
    def unit_lateActivation(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_lateActivation = value
        return True

    @property
    def unit_start_time(self):
        return self._unit_start_time

    @unit_start_time.setter
    def unit_start_time(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_start_time = value
        return True

    @property
    def unit_frequency(self):
        return self._unit_frequency

    @unit_frequency.setter
    def unit_frequency(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_frequency = value
        return True

    @property
    def unit_x(self):
        return self._unit_x

    @unit_x.setter
    def unit_x(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_x = value
        return True

    @property
    def unit_y(self):
        return self._unit_y

    @unit_y.setter
    def unit_y(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_y = value
        return True

    @property
    def unit_alt(self):
        return self._unit_alt

    @property
    def unit_alt_type(self):
        return self._unit_alt_type

    @property
    def heading(self):
        return self._heading

    @property
    def unit_speed(self):
        return self._unit_speed

    @property
    def unit_hardpoint_racks(self):
        return self._unit_hardpoint_racks

    @property
    def unit_livery_id(self):
        return self._unit_livery_id

    @property
    def unit_psi(self):
        return self._unit_psi

    @property
    def unit_skill(self):
        return self._unit_skill

    @property
    def unit_onboard_num(self):
        return self._unit_onboard_num

    @property
    def unit_payload(self):
        return self._unit_payload

    @property
    def unit_callsign(self):
        return self._unit_callsign


    @unit_alt.setter
    def unit_alt(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_alt = value
        return True

    @unit_alt_type.setter
    def unit_alt_type(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_alt_type = value
        return True

    @heading.setter
    def heading(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._heading = value
        return True

    @unit_speed.setter
    def unit_speed(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_speed = value
        return True

    @unit_hardpoint_racks.setter
    def unit_hardpoint_racks(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_hardpoint_racks = value
        return True

    @unit_livery_id.setter
    def unit_livery_id(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_livery_id = value
        return True

    @unit_psi.setter
    def unit_psi(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_psi = value
        return True

    @unit_skill.setter
    def unit_skill(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_skill = value
        return True

    @unit_onboard_num.setter
    def unit_onboard_num(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._unit_onboard_num = value
        return True

    @unit_payload.setter
    def unit_payload(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
    
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

    # use case methods
    def checkParam(name: str, description: str, category: Literal, function: str, position: Point, volume: Volume, threat: Threat, crytical: bool, repair_time: int, cost: int, country: str, block: Block, role: str, health: int, unit_index: int, unit_name: str, unit_type: str, unit_unitId: int, unit_communication: bool, unit_lateActivation: bool, unit_start_time: int, unit_frequency: float, unit_x: float, unit_y: float, unit_alt: float, unit_alt_type: str, heading: int, unit_speed: float, unit_hardpoint_racks: int, unit_livery_id: int, unit_psi: float, unit_skill: str, unit_onboard_num: int, unit_payload: str|Dict, unit_callsign: str|Dict) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""          

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
        if role and not isinstance(role, str):  
            return (False, "Bad Arg: role must be a str")        
        if health and not isinstance(health, int):
            return (False, "Bad Arg: health must be a int")
        if country and not isinstance(country, str):  
            return (False, "Bad Arg: country must be a str")        
        if crytical and not isinstance(crytical, bool):
            return (False, "Bad Arg: crytical must be a bool")        
        if unit_index and not isinstance(unit_index, str):
            return (False, "Bad Arg: unit_index must be a str")        
        if unit_name and not isinstance(unit_name, str):
            return (False, "Bad Arg: unit_name must be a str")        
        if unit_type and not isinstance(unit_type, str):
            return (False, "Bad Arg: unit_type must be a str")          
        if unit_unitId and not isinstance(unit_unitId, int):
            return (False, "Bad Arg: unit_unitId must be a int")        
        if unit_communication and not isinstance(unit_communication, bool):
            return (False, "Bad Arg: unit_communication must be a bool")        
        if unit_lateActivation and not isinstance(unit_lateActivation, bool):
            return (False, "Bad Arg: unit_lateActivation must be a bool")        
        if unit_start_time and not isinstance(unit_start_time, int):
            return (False, "Bad Arg: unit_start_time must be a int")        
        if unit_frequency and not isinstance(unit_frequency, float):
            return (False, "Bad Arg: unit_frequency must be a float")        
        if unit_x and not isinstance(unit_x, float):
            return (False, "Bad Arg: unit_x must be a float")        
        if unit_y and not isinstance(unit_y, float):    
            return (False, "Bad Arg: unit_y must be a float")        
        if unit_alt and not isinstance(unit_alt, float):
            return (False, "Bad Arg: unit_alt must be a float")        
        if unit_alt_type and not isinstance(unit_alt_type, str):
            return (False, "Bad Arg: unit_alt_type must be a str")                
        if heading and not isinstance(heading, int):
            return (False, "Bad Arg: heading must be a int")               
        if unit_speed and not isinstance(unit_speed, float):
            return (False, "Bad Arg: unit_speed must be a float")        
        if unit_hardpoint_racks and not isinstance(unit_hardpoint_racks, int):
            return (False, "Bad Arg: unit_hardpoint_racks must be a int")        
        if unit_livery_id and not isinstance(unit_livery_id, int):
            return (False, "Bad Arg: unit_livery_id must be a int")        
        if unit_psi and not isinstance(unit_psi, float):
            return (False, "Bad Arg: unit_psi must be a float")        
        if unit_skill and not isinstance(unit_skill, str):
            return (False, "Bad Arg: unit_skill must be a str")
        if unit_onboard_num and not isinstance(unit_onboard_num, int):
            return (False, "Bad Arg: unit_onboard_num must be a int")
        if unit_payload and not isinstance(unit_payload, dict):
            return (False, "Bad Arg: unit_payload must be a dict")
        if unit_callsign and not isinstance(unit_callsign, dict):
            return (False, "Bad Arg: unit_callsign must be a dict")
    
        return (True, "OK")
    
    @property
    def efficiency(self):
        """calculate efficiency from asset health, rcp, acp, .."""
        
        efficiency = 0

        if self.rcp.energy != 0 and ( self.role == "storage_energy" or self.role == "production_energy" or self.role == "transport_energy" ):
            efficiency = self.acp.energy / self.rcp.energy
            
        elif self.rcp.goods != 0 and ( self.role == "storage_goods" or self.role == "production_goods" or self.role == "transport_goods" ):
            efficiency = self.acp.goods / self.rcp.goods

        elif ( self.rcp.hc != 0 and self.rcp.hs != 0 and self.rcp.hb != 0 ) and ( self.role == "formation_hr_mil" or self.role == "transport_hr_mil" ):
            efficiency = ( self.acp.hc + self.acp.hs + self.acp.hb ) / ( self.rcp.hc + self.rcp.hs + self.rcp.hb )

        elif self.rcp.hr != 0 and ( self.role == "formation_hr_civ" or self.role == "transport_hr_civ" ):
            efficiency = self.acp.hr / self.rcp.hr

        else:
            raise Exception("unexpected role ( {0} ) or zero rcp values ( energy: {1} goods: {2} hc: {3} hs: {4} hb: {5} hr: {6} )".format( self.role, self.rcp.energy, self.rcp.goods, self.rcp.hc, self.rcp.hs, self.rcp.hb, self.rcp.hr ) )
        
        efficiency = self._unit_health * efficiency 

        return efficiency
             
   
    def threatVolume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # pos = position
        # evaluate complessive volume of threat from all threat sources
        # return tv
        pass

        


    # Method inherited from Block but not allowed for this class

    def getReport(self): #override
        raise Exception("Method not allowed for this class")
    
    def assetStatus(self):#override
        raise Exception("Method not allowed for this class")


    @property #override
    def assets(self):
        raise Exception("Method not allowed for this class")
     
    @assets.setter #override
    def assets(self, value):
            raise Exception("Method not allowed for this class")

    def getAsset(self, key): #override
            raise Exception("Method not allowed for this class")

    def setAsset(self, key, value): #override
            raise Exception("Method not allowed for this class")

    def removeAsset(self, key):#override
        raise Exception("Method not allowed for this class")
  
    def getBlocks(self, blockCategory: str, side: str): #override
        raise Exception("Method not allowed for this class")
           
    @property
    def morale(self):
        # dipende da tipo di asset, dal rapporto tra goods, energy e hr request e fornite
        
        efficiency = self.efficiency
        
        if efficiency > 0.7:
            return 1

        elif efficiency >= 0.5:
            return 0.7 

        elif efficiency >= 0.3:
            return 0.3
        
        else:
            return 0.1
        

    @property
    def efficiency(self):
        return self.balance_trade * self.state.damage
    
