"""
Asset Class

Nota: rappresenta unit -> group -> country -> coalition (DCS)
Il Block può essere costituito da diversi gruppi apparenenti a country diverse della stessa coalizione

"""

import sys
import os
# Aggiungi il percorso della directory principale del progetto
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Code.Dynamic_War_Manager.Source.Block import Block
from Code  import Utility
from Code.LoggerClass import Logger
#from Code.Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.Volume import Volume
from Code.Dynamic_War_Manager.Source.Threat import Threat
from Code.Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import SIDE, BLOCK_ASSET_CATEGORY, AIR_MIL_BASE_CRAFT_ASSET, AIR_DEFENCE_ASSET, GROUND_MIL_BASE_VEHICLE_ASSET, NAVAL_MIL_BASE_CRAFT_ASSET, BLOCK_INFRASTRUCTURE_ASSET
from sympy import Point, Point3D
#from Code.Dynamic_War_Manager.Source.Region import Region

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Asset')

# ASSET
class Asset :    

    def __init__(self, block: Block, name: str|None = None, description: str|None = None, category: str|None = None, asset_type:str|None = None, functionality: str|None = None, cost: int|None = None, value: int|None = None, acp: Payload|None = None, rcp: Payload|None = None, payload: Payload|None = None, position: Point3D|None = None, volume: Volume|None = None, crytical: bool|None = False, repair_time: int|None = 0, role: str|None = None, dcs_unit_data: dict|None = None): # type: ignore   
            
            
            # propriety
            # health: int|None = None, unit_index: str|Dict = None, unit_name: str|None = None, unit_type: str|None = None, unit_unitId: int|None = None, unit_communication: bool|None = None, unit_lateActivation: bool|None = None, unit_start_time: int|None = None, unit_frequency: float|None = None, unit_x: float|None = None, unit_y: float|None = None, unit_alt: float|None = None, unit_alt_type: str|None = None, heading: int|None = None, unit_speed: float|None = None, unit_hardpoint_racks: int|None = None, unit_livery_id: int|None = None, unit_psi: float|None = None, unit_skill: str|None = None, unit_onboard_num: int|None = None, unit_payload: str|Dict = None, unit_callsign: str|Dict = None             
            self._name = name # asset name - type str
            self._id = Utility.setId(self._name) # id self-assigned - type str
            self._description = description # asset description - type str                  
            self._category = category # asset category - (Tank, Armored, ..., SAM, AAA, .... Road, Port, Airbase, ....)
            self._asset_type = asset_type # asset type (Tank, Armored_Personal_Carrier,...,Fighter, Bomber, ...., Carrier, Cruiser, ..., Radar, Track_Radar, AAA, ....,Factory, Oil_Tank, Depot, ... )
            self._functionality = functionality # asset functionality - type str  
            self._health = int|None      
            self._position: Point|None = position # asset position - type Point (3D -> anche l'altezza deve essere considerata per la presenza di rilievi nel terreno)
            self._cost: int = cost # asset cost - type int             
            self._value: int = value # asset value - type int
            self._payload_perc: int = None
            self._crytical: bool|None = crytical 
            self._repair_time: int = None
            self._role: str|None = role # asset role - type str Recon, Interdiction, ReconAndInterdiction, defence, attack, support, transport, storage (energy, goods, ..)                          
            self._dcs_unit_data = dcs_unit_data
          
            
            # Association    
            self._volume: Volume|None = volume
            self._block: Block = block # asset block - component of Block - type Block asset not exist without block
            

            # check input parameters

            if dcs_unit_data and self.checkParamDCS(dcs_unit_data): # update property with dcs_unit_data if defined 
                self._nome = dcs_unit_data["unit_name"]
                self._id = dcs_unit_data["unitId"]                
                self._position = Point3D(dcs_unit_data["unit_x"], dcs_unit_data["unit_y"], dcs_unit_data["unit_alt"])# att: nella gestione dello z devi tener conto se BARO o ASL
                self._health = dcs_unit_data["unit_health"]
            #else:
            #    raise Exception(check_results[2] + ". Object not istantiate (DCS_DATA).")


            if not acp:
                acp = Payload(goods=0,energy=0,hr=0, hc=0, hs=0, hb=0)
            
            if not rcp:
                rcp = Payload(goods=0,energy=0,hr=0, hc=0, hs=0, hb=0)

            if not payload:
                payload = Payload(goods=0,energy=0,hr=0, hc=0, hs=0, hb=0)
            

            check_results =  self.checkParam( name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role)
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")


   
    # getter & setter methods

    @property
    def dcs_unit_data(self):
        return self._dcs_unit_data
    
    @dcs_unit_data.setter
    def dcs_unit_data(self, data):

        self._dcs_unit_data = data


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, param):

        check_result = self.checkParam(name = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        self._name = param  
        return True
            
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, param):
        
        if id:                        
            self._id = str(param)
        else:
            self._id = None
            
        return True
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, param):

        check_result = self.checkParam(description = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        
        self._description = param       
            
        return True
    
    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, param):
        
        check_result = self.checkParam(description = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        
        self._description = param       
            
        return True

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, param):

        check_result = self.checkParam(category = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        self._category = param

        return True
    
    @property
    def functionality(self):
        return self._functionality

    @functionality.setter
    def functionality(self, param):

        check_result = self.checkParam(functionality = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    


        self._functionality = param  
            
        return True

    @property
    def cost(self) -> int: #override      
        return self._cost
    
    @cost.setter
    def cost(self, param) -> bool:
        check_result = self.checkParam(cost = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        self._cost = param              
        return True
    

    @property
    def value(self) -> int: #override      
        return self._value
    
    @value.setter
    def value(self, param) -> bool:
        check_result = self.checkParam(value = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        self._value = param              
        return True
    
    @property
    def health(self) -> int: #override      
        return self._health

    @health.setter
    def health(self, health) -> bool: #override
        check_result = self.checkParam(health = health)
        
        if not check_result[0]:
            raise Exception(check_result[0])                        
        self._health = health
        return True

    @property
    def crytical(self) -> int: #override      
        return self._crytical

    @crytical.setter
    def crytical(self, crytical) -> bool: #override
        check_result = self.checkParam(crytical = crytical)
        
        if not check_result[0]:
            raise Exception(check_result[0])                
        self._crytical = crytical
        return True
    
    @property
    def repair_time(self) -> int: #override      
        return self._repair_time

    @repair_time.setter
    def repair_time(self, repair_time) -> bool: #override
        
        check_result = self.checkParam(repair_time = repair_time)

        if not check_result[0]:
            raise Exception(check_result[0])                
        self._repair_time = repair_time
        return True

    @property
    def role(self) -> str: #override
        return self._role    

    @role.setter    
    def role(self, role) -> bool: #override
        
        check_result = self.checkParam(role = role)

        if not check_result[0]:
            raise Exception(check_result[0])                
        self._role = role
        return True 
    
    @property
    def asset_type(self) -> str: 
        return self._asset_type    

    @asset_type.setter    
    def asset_type(self, asset_type) -> bool: #override
        
        check_result = self.checkParam(asset_type = asset_type)

        if not check_result[0]:
            raise Exception(check_result[0])                
        self._asset_type = asset_type
        return True 
        
    @property
    def position(self) -> Point3D: #override      
        return self._position
    
    @position.setter
    def position(self, param) -> bool: #override
        
        check_result = self.checkParam(position = param)

        if not check_result[0]:
            raise Exception(check_result[0])                
        self._position = param
        return True

    @property
    def state(self):                
        return {"name": self._name, "id": self.id, "category": self._category, "role": self._role, "health": self._health, "efficiency": self.efficiency, "balance_trade": self.balance_trade, "position": self._position}
    

    @property
    def efficiency(self) -> float:
        return float(self.balance_trade * self._health)

    @property
    def balance_trade(self) -> float:        
        """Returns median value of sum of the acp.item / rcp.item ratio 

        Returns:
            float: median value of sum of the acp.item / rcp.item ratio 
        """        
        goods = None 
        energy = None
        hr = None 
        hc = None 
        hs = None
        hb = None              
        
        if self.rcp.goods and self.rcp.goods > 0:
            goods = self.acp.goods / self.rcp.goods
        
        if self.rcp.energy and self.rcp.energy > 0:
            energy = self.acp.energy / self.rcp.energy

        if self.rcp.hr and self.rcp.hr > 0:
            hr = self.acp.hr / self.rcp.hr

        if self.rcp.hc and self.rcp.hc > 0:
            hc = self.acp.hc / self.rcp.hc

        if self.rcp.hs and self.rcp.hs > 0:
            hs = self.acp.hs / self.rcp.hs

        if self.rcp.hb and self.rcp.hb > 0:
            hb = self.acp.hb / self.rcp.hb

        variables =  [goods, energy, hr, hc, hs, hb]

        balances = [v for v in variables if v is not None]        
        balance = sum(balances) / len(balances)

        return balance


    @property
    def acp(self) -> Payload:
        """Assigned Consume Payload
        Assigned Consume Payload is the payload that the asset can consume from the block

        Returns:
            Payload: acp object
        """        
        return self._acp


    @acp.setter
    def acp(self, param: Payload) -> bool:
        """Assigned Consume Payload
        Assigned Consume Payload is the payload that the asset can consume from the block
        
        Args:
            param (Payload): payload object

        Raises:
            Exception: Validation error

        Returns:
            bool: True if the payload is set correctly
        """
        check_result = self.checkParam(acp = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        else:
            self._acp = param
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True
    

    @property
    def rcp(self) -> Payload:
        """Required Consume Payload
        Required Consume Payload is the payload that the asset needs to consume from the block

        Returns:
            Payload: rcp object
        """        
        return self._rcp

    @rcp.setter
    def rcp(self, param: Payload) -> bool:
        """Required Consume Payload is the payload that the asset needs to consume from the block

        Args:
            param (Payload): assignment consume payload object

        Raises:
            Exception: validation error

        Returns:
            bool: True if the payload is set correctly
        """        
        check_result = self.checkParam(rcp = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    
        else:
            self._rcp = param           
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True

    @property
    def payload(self) -> Payload:
        """Payload is the payload that the asset must manage (transport, trasformation) from the block

        Returns:
            Payload: payload object
        """        
        return self._payload

    @payload.setter
    def payload(self, param: Payload) -> bool:
        """Payload is the payload that the asset must manage (transport, trasformation) from the block

        Args:
            param (Payload): payload object for management

        Raises:
            Exception: Validation error

        Returns:
            bool: True if the payload is set correctly
        """        
        check_result = self.checkParam(payload = param)
        
        if not check_result[0]:
            raise Exception(check_result[0])    
        else:
            self._payload = param             
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True    

    def consume(self) -> dict:
        """Reduce acp of rcp payload quantity

        Returns:
            Dictionary[item]: bool: True if subtraction from acp is complete (acp >=0 after reduction), item = ("goods", "energy", "hr", "hc", "hs", "hb")
        """         
        return self._consume(self.rcp)
    
    def _consume(self, cons: Payload) -> dict:
        """Reduce acp of cons payload quantity

        Args:
            cons (Payload): object with resource quantity for subtraction

        Raises:
            Exception: Validation error

        Returns:
            Dictionary[item]: bool: True if subtraction from acp is complete (acp >=0 after reduction), item = ("goods", "energy", "hr", "hc", "hs", "hb")
        """        
        check_result = self.checkParam(payload = cons)
        
        if not check_result[0]:
            raise Exception(check_result[0])    

        else:
            consume_execution = {"goods": None, "energy": None, "hr": None, "hc": None, "hs": None, "hb": None}

            if cons.goods: # il consumo di goods è richiesto

                if self.acp.goods >= cons.goods: # assigned consume payload previsto per goods (acp) è sufficiente per soddisfare il consumo
                    self.acp.goods -= cons.goods # riduco goods nell'acp
                    consume_execution["goods"] = True # consumo soddisfatto
                
                else:
                    consume_execution["goods"] = False # consumo non soddisfatto

            if cons.energy:
                
                if self.acp.energy >= cons.energy:
                    self.acp.energy -= cons.energy
                    consume_execution["energy"] = True
                
                else:
                    consume_execution["energy"] = False
                
            if cons.hr:

                if self.acp.hr >= cons.hr:
                    self.acp.hr -= cons.hr
                    consume_execution["hr"] = True
                
                else:
                    consume_execution["hr"] = False

            if cons.hc:

                if self.acp.hc >= cons.hc:
                    self.acp.hc -= cons.hc
                    consume_execution["hc"] = True
                
                else:
                    consume_execution["hc"] = False
                
            if cons.hs:

                if self.acp.hs >= cons.hs:
                    self.acp.hs -= cons.hs
                    consume_execution["hs"] = True
                
                else:
                    consume_execution["hs"] = False
                
            if cons.hb:

                if self.acp.hb >= cons.hb:
                    self.acp.hb -= cons.hb
                    consume_execution["hb"] = True
                
                else:
                    consume_execution["hb"] = False
        
        return True    


    @property
    def volume(self) -> Volume: #override      
        return self._volume
    
    @volume.setter
    def volume(self, param) -> bool: #override
        
        check_result = self.checkParam(volume = param)

        if not check_result[0]:
            raise Exception(check_result[0])                
        self._volume = param
        return True
    
    @property
    def threat(self) -> Threat: #override      
        return self._threat
    
    @threat.setter
    def threat(self, param) -> bool: #override
        
        check_result = self.checkParam(threat = param)

        if not check_result[0]:
            raise Exception(check_result[0])                
        self._threat = param
        return True
    
    @property
    def block(self):
        return self._block
    
    @block.setter
    def block(self, param):
        check_result = self.checkParam(block = param)

        if not check_result[0]:
            raise Exception(check_result[0])                
        
        if param and param.getAsset(self._id).id != self._id:
            raise Exception("Association Incongruence: this Asset id is present like a key in Block association dictionary, but Asset object has different id")
        
        self._block = param
        return True

    # use case methods
    def checkParam(self, name: str = None, description: str = None, category: str = None, asset_type: str = None, functionality: str = None, cost: int = None, value: int = None, acp: Payload = None, rcp: Payload = None, payload: Payload = None, position: Point3D = None, volume: Volume = None, crytical: bool = None, repair_time: int = None, block: Block = None, role: str = None, health: int = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")
        if description and not isinstance(description, str):
            return (False, "Bad Arg: description must be a str")
      
        if asset_type and (isinstance(asset_type, str)): # i controlli sugli asset_type sono svolti nelle classi derivate: Aircraft, Vehicle, Ship e Structure        
            return (False, "Bad Arg: asset_type must be a str")

        if category and isinstance(category, str): # i controlli sulle categorie sono svolti nelle classi derivate: Aircraft, Vehicle, Ship e Structure
            return (False, "Bad Arg: category must be a str")
        if functionality and not isinstance(functionality, str):
            return (False, "Bad Arg: function must be a str")       
        if position and not isinstance(position, Point3D):
            return (False, "Bad Arg: position must be a Point3D object")        
        if block and not isinstance(block, Block):
            return (False, "Bad Arg: block must be a Block object")        
        if volume and not isinstance(volume, Volume):
            return (False, "Bad Arg: volume must be a Volume object")        
        if acp and not isinstance(acp, Payload):                        
            return (False, "Bad Arg: tacp must be a Payload object")                
        if rcp and not isinstance(rcp, Payload):                        
            return (False, "Bad Arg: rcp must be a Payload object")                
        if payload and not isinstance(payload, Payload):                        
            return (False, "Bad Arg: payload must be a Payload object")                
        if repair_time and not isinstance(repair_time, int):
            return (False, "Bad Arg: repair_time must be a int")        
        if cost and not isinstance(repair_time, int):
            return (False, "Bad Arg: cost must be a int")  
        if value and not isinstance(repair_time, int):
            return (False, "Bad Arg: value must be a int")        
        if role and not isinstance(role, str):  
            return (False, "Bad Arg: role must be a str")        
        if health and not isinstance(health, int):
            return (False, "Bad Arg: health must be a int")
            
        if crytical and not isinstance(crytical, bool):
            return (False, "Bad Arg: crytical must be a bool")        
    
        return (True, "OK")
    
    def checkParamDCS(data: dict):
            
        if data["unit_name"]  and not isinstance(data["unit_name"], str):
            return (False, "Bad Arg: unit_name must be a str")        
        if data["unit_type"]  and not isinstance(data["unit_type"], str):
            return (False, "Bad Arg: unit_type must be a str")          
        if data["unit_unitId"]  and not isinstance(data["unit_unitId"], int):
            return (False, "Bad Arg: unit_unitId must be a int")        
        
            return (False, "Bad Arg: unit_frequency must be a float")        
        if data["unit_x"]  and not isinstance(data["unit_x"], float):
            return (False, "Bad Arg: unit_x must be a float")        
        if data["unit_y"]  and not isinstance(data["unit_y"], float):    
            return (False, "Bad Arg: unit_y must be a float")        
        if data["unit_alt"]  and not isinstance(data["unit_alt"], float):
            return (False, "Bad Arg: unit_alt must be a float")        
        if data["unit_alt_type"]  and not isinstance(data["unit_alt_type"], str):
            return (False, "Bad Arg: unit_alt_type must be a str")                
        if data["unit_health"]  and not isinstance(data["unit_health"], float):
            return (False, "Bad Arg: unit_health must be a float")   
        return (True, "DCS_DATA OK")
   
    def threatVolume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # pos = position
        # evaluate complessive volume of threat from all threat sources
        # return tv
        pass
    
   
    def isMilitary(self):
        return self.block.isMilitary
    
    def isLogistic(self):
        return self.block.isLogistic
    
    def isCivilian(self):
        return self.block.isCivilian
    
    