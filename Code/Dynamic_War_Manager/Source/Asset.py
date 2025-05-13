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
import Code.Utility
from Code.LoggerClass import Logger
#from Code.Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.Volume import Volume
from Code.Dynamic_War_Manager.Source.Threat import Threat
from Code.Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import SIDE, BLOCK_ASSET_CATEGORY
from sympy import Point, Point3D
#from Code.Dynamic_War_Manager.Source.Region import Region

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Asset')

# ASSET
class Asset :    

    def __init__(self, block: Block, name: str|None = None, description: str|None = None, category: str|None = None, asset_type:str|None = None, functionality: str|None = None, cost: int|None = None, acp: Payload|None = None, rcp: Payload|None = None, payload: Payload|None = None, position: Point3D|None = None, volume: Volume|None = None, threat: Threat|None = None, crytical: bool|None = False, repair_time: int|None = 0, country: str|None = None, role: str|None = None, dcs_unit_data: dict|None = None): # type: ignore   
            
            
            # propriety
            # health: int|None = None, unit_index: str|Dict = None, unit_name: str|None = None, unit_type: str|None = None, unit_unitId: int|None = None, unit_communication: bool|None = None, unit_lateActivation: bool|None = None, unit_start_time: int|None = None, unit_frequency: float|None = None, unit_x: float|None = None, unit_y: float|None = None, unit_alt: float|None = None, unit_alt_type: str|None = None, heading: int|None = None, unit_speed: float|None = None, unit_hardpoint_racks: int|None = None, unit_livery_id: int|None = None, unit_psi: float|None = None, unit_skill: str|None = None, unit_onboard_num: int|None = None, unit_payload: str|Dict = None, unit_callsign: str|Dict = None             
            self._name = name # asset name - type str
            self._id = Utility.setId(self._name) # id self-assigned - type str
            self._description = description # asset description - type str
            self._side = block.side # asset side - type str            
            self._category = category # asset category - type Literal
            self._asset_type = asset_type # lo usi per le sub categorie 
            self._functionality = functionality # asset functionality - type str  
            self._health = int|None      
            self._position: Point|None = position # asset position - type Point (3D -> anche l'altezza deve essere considerata per la presenza di rilievi nel terreno)
            self._cost: int = None # asset cost - type int             
            self._value: float = None # asset value - type float
            self._payload_perc: int = None
            self._crytical: bool|None = crytical 
            self._repair_time: int = None
            self._role: str|None = role # asset role - type str Recon, Interdiction, ReconAndInterdiction, defence, attack, support, transport, storage (energy, goods, ..)                          
            self._dcs_unit_data = dcs_unit_data
            """

            dcs_unit_data = { "unit_health": int, "unit_index": int, "unit_name": str, "unit_type": str, "unit_unitId": int, "unit_communication": bool, 
                                   "unit_lateActivation": bool, "unit_start_time": int, "unit_frequency": float, "unit_x": float, "unit_y": float, 
                                   "unit_alt": float, "unit_alt_type": str, "heading": int, "unit_speed": float, "unit_hardpoint_racks": int, "unit_livery_id": int, 
                                   "unit_psi": float, "unit_skill": str, "unit_onboard_num": int, "unit_payload": str|Dict, "unit_callsign": str|Dict}
            
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
            """
            
            # Association    
            self._volume: int|Volume|None = volume
            self._threat: int|Threat|None = threat
            self._block: int|Block = block # asset block - component of Block - type Block asset not exist without block
            

            # load Context.BLOCK_ASSET data
            if not self.loadAssetDataFromContext():
                raise Exception(f"Error in load BLOCK ASSET data cost: {self._cost}, value: {self._value}, repair_time: {self._repair_time}, rpc: {self._rcp!r}\n - Object not istantiate.")

            # check input parameters

            if dcs_unit_data and self.checkParamDCS(dcs_unit_data): # update property with dcs_unit_data if defined 
                self._nome = dcs_unit_data["unit_name"]
                self._id = dcs_unit_data["unitId"]                
                self._position = Point3D(dcs_unit_data["unit_x"], dcs_unit_data["unit_y"], dcs_unit_data["unit_alt"])# att: nella gestione dello z devi tener conto se BARO o ASL
                self._health = dcs_unit_data["unit_health"]
            else:
                raise Exception(check_results[2] + ". Object not istantiate (DCS_DATA).")


            if not acp:
                acp = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)
            
            if not rcp:
                rcp = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)

            if not payload:
                payload = Payload(goods=0,energy=0,hr=0, hc=0, hrp=0, hcp=0)

            if not side:
                side = "Neutral"

            check_results =  self.checkParam( name, description, category, asset_type, side, functionality, position, volume, threat, crytical, repair_time, country, role )
            
            if not check_results[1]:
                raise Exception(check_results[2] + ". Object not istantiate.")


    def loadAssetDataFromContext(self, block__asset_data_from_context: dict) -> bool:
        """Initialize some asset property loading data from Context module
            asset_type is Subcategory of BLOCK_ASSET 

        Returns:
            bool: True if data is loaded, otherwise False
        """        

        for k1, v1 in block__asset_data_from_context:

            for k2, v2 in v1:

                for asset_type, asset_data in v2:
                    
                    if asset_type == self.asset_type:
                        self.cost = asset_data["cost"]
                        self.value = asset_data["value"]
                        self.rcp = asset_data["rcp"]
                        self.repair_time = asset_data["t2r"]
                        self._payload_perc = asset_data["payload%"]
                        return True              
        return False
    


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
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._name = param  
        return True
            
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, param):

        check_result = self.checkParam(id = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        
        self._id = str(param)
            
        return True
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, param):

        check_result = self.checkParam(description = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        
        self._description = param       
            
        return True
    
    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, param):
        
        check_result = self.checkParam(description = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        
        self._description = param       
            
        return True

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, param):

        check_result = self.checkParam(category = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._category = param

        return True
    
    @property
    def functionality(self):
        return self._functionality

    @functionality.setter
    def functionality(self, param):

        check_result = self.checkParam(functionality = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    


        self._functionality = param  
            
        return True

    @property
    def cost(self) -> int: #override      
        return self._cost
    
    @cost.setter
    def cost(self, param) -> bool:
        check_result = self.checkParam(cost = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._cost = param              
        return True
    
    @property
    def health(self) -> int: #override      
        return self._health

    @health.setter
    def health(self, health) -> bool: #override
        check_result = self.checkParam(health = health)
        
        if not check_result[1]:
            raise Exception(check_result[2])                        
        self._health = health
        return True

    @property
    def crytical(self) -> int: #override      
        return self._crytical

    @crytical.setter
    def crytical(self, crytical) -> bool: #override
        check_result = self.checkParam(crytical = crytical)
        
        if not check_result[1]:
            raise Exception(check_result[2])                
        self._crytical = crytical
        return True
    
    @property
    def repair_time(self) -> int: #override      
        return self._repair_time

    @repair_time.setter
    def repair_time(self, repair_time) -> bool: #override
        
        check_result = self.checkParam(repair_time = repair_time)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._repair_time = repair_time
        return True

    @property
    def role(self) -> str: #override
        return self._role    

    @role.setter    
    def role(self, role) -> bool: #override
        
        check_result = self.checkParam(role = role)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._role = role
        return True 
    
    @property
    def asset_type(self) -> str: 
        return self._asset_type    

    @asset_type.setter    
    def asset_type(self, asset_type) -> bool: #override
        
        check_result = self.checkParam(asset_type = asset_type)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._asset_type = asset_type
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
    def position(self) -> Point3D: #override      
        return self._position
    
    @position.setter
    def position(self, param) -> bool: #override
        
        check_result = self.checkParam(position = param)

        if not check_result[1]:
            raise Exception(check_result[2])                
        self._position = param
        return True

    @property
    def state(self):                
        return {"name": self._name, "id": self.id, "category": self._category, "role": self._role, "health": self._health, "efficiency": self.efficiency, "balance_trade": self.balance_trade, "position": self._position}
    

    @property
    def efficiency(self):
        return self.balance_trade * self._health

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
        
        if not check_result[1]:
            raise Exception(check_result[2])    

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
        
        if not check_result[1]:
            raise Exception(check_result[2])    
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
        
        if not check_result[1]:
            raise Exception(check_result[2])    
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
        
        if not check_result[1]:
            raise Exception(check_result[2])    

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
    def checkParam(self, name: str, description: str, category: str, asset_type:str, side: str, functionality: str, position: Point3D, volume: Volume, threat: Threat, crytical: bool, repair_time: int, cost: int, country: str, block: Block, role: str, health: int) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")
        if description and not isinstance(description, str):
            return (False, "Bad Arg: description must be a str")
        if side and (not isinstance(side, str) or side not in SIDE):
            return (False, "Bad Arg: side must be a str with value: Blue, Red or Neutral")
        if asset_type and (isinstance(asset_type, str)):        

            if self.block.block_class == "Mil_Base": # asset is a Mil_Base component

                air_asset = BLOCK_ASSET_CATEGORY["Air_Mil_Base_Craft_Asset"].keys()
                naval_asset = BLOCK_ASSET_CATEGORY["Naval_Mil_Base_Craft_Asset"].keys() 

                if asset_type in [air_asset, naval_asset]:
                    return (True, "OK")
                
                elif category:
                    vehicle_asset = BLOCK_ASSET_CATEGORY["Ground_Mil_Base Vehicle Asset"][category].keys()
                    air_defence_asset = BLOCK_ASSET_CATEGORY["Air_Defence_Asset_Category"][category].keys()
                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class][category].keys()

                    if asset_type in [vehicle_asset, air_defence_asset, struct_asset]:
                        return (True, "OK")
                    
                else:

                    vehicle_asset = BLOCK_ASSET_CATEGORY["Ground_Mil_Base Vehicle Asset"].values().keys()
                    air_defence_asset = BLOCK_ASSET_CATEGORY["Air_Defence_Asset_Category"].values().keys()
                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class].values().keys()

                    if asset_type in [vehicle_asset, air_defence_asset, struct_asset]:
                        return (True, "OK")
            
            else:  # asset isn't a Mil_Base component

                if category: 

                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class][category].values()                
                
                else:
                    struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class].values().keys()                
                
                if asset_type in struct_asset:
                    return (True, "OK")
                    
            return (False, f"Bad Arg: asset_type must be any string from BLOCK_ASSET_CATEGORY {BLOCK_ASSET_CATEGORY!r}")                  


        if category and isinstance(category, str):

            vehicle_asset = BLOCK_ASSET_CATEGORY["Ground_Mil_Base Vehicle Asset"].keys()
            air_defence_asset = BLOCK_ASSET_CATEGORY["Air_Defence_Asset_Category"].keys()
            struct_asset = BLOCK_ASSET_CATEGORY["Block_Infrastructure_Asset"][self.block.block_class].keys()

            if asset_type in [vehicle_asset, air_defence_asset, struct_asset]:
                return (True, "OK")

            return (False, "Bad Arg: category must be any string from GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, STRUCTURE_ASSET_CATEGORY")                     

        
        if functionality and not isinstance(functionality, str):
            return (False, "Bad Arg: function must be a str")       
        if position and not isinstance(position, Point3D):
            return (False, "Bad Arg: position must be a Point3D object")        
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
    
        return (True, "OK")
    
    def checkParamDCS(data):
        if data["unit_index"] and not isinstance(data["unit_index"], str):
            return (False, "Bad Arg: unit_index must be a str")        
        if data["unit_name"]  and not isinstance(data["unit_name"], str):
            return (False, "Bad Arg: unit_name must be a str")        
        if data["unit_type"]  and not isinstance(data["unit_type"], str):
            return (False, "Bad Arg: unit_type must be a str")          
        if data["unit_unitId"]  and not isinstance(data["unit_unitId"], int):
            return (False, "Bad Arg: unit_unitId must be a int")        
        if data["unit_communication"]  and not isinstance(data["unit_communication"], bool):
            return (False, "Bad Arg: unit_communication must be a bool")        
        if data["unit_lateActivation"]  and not isinstance(data["unit_lateActivation"], bool):
            return (False, "Bad Arg: unit_lateActivation must be a bool")        
        if data["unit_start_time"]  and not isinstance(data["unit_start_time"], int):
            return (False, "Bad Arg: unit_start_time must be a int")        
        if data["unit_frequency"]  and not isinstance(data["unit_frequency"], float):
            return (False, "Bad Arg: unit_frequency must be a float")        
        if data["unit_x"]  and not isinstance(data["unit_x"], float):
            return (False, "Bad Arg: unit_x must be a float")        
        if data["unit_y"]  and not isinstance(data["unit_y"], float):    
            return (False, "Bad Arg: unit_y must be a float")        
        if data["unit_alt"]  and not isinstance(data["unit_alt"], float):
            return (False, "Bad Arg: unit_alt must be a float")        
        if data["unit_alt_type"]  and not isinstance(data["unit_alt_type"], str):
            return (False, "Bad Arg: unit_alt_type must be a str")                
        if data["heading"]  and not isinstance(data["heading"], int):
            return (False, "Bad Arg: heading must be a int")               
        if data["unit_speed"]  and not isinstance(data["unit_speed"], float):
            return (False, "Bad Arg: unit_speed must be a float")        
        if data["unit_hardpoint_racks"]  and not isinstance(data["unit_hardpoint_racks"], int):
            return (False, "Bad Arg: unit_hardpoint_racks must be a int")        
        if data["unit_livery_id"]  and not isinstance(data["unit_livery_id"], int):
            return (False, "Bad Arg: unit_livery_id must be a int")        
        if data["unit_psi"]  and not isinstance(data["unit_psi"], float):
            return (False, "Bad Arg: unit_psi must be a float")        
        if data["unit_skill"]  and not isinstance(data["unit_skill"], str):
            return (False, "Bad Arg: unit_skill must be a str")
        if data["unit_onboard_num"]  and not isinstance(data["unit_onboard_num"], int):
            return (False, "Bad Arg: unit_onboard_num must be a int")
        if data["unit_payload"]  and not isinstance(data["unit_payload"], dict):
            return (False, "Bad Arg: unit_payload must be a dict")
        if data["unit_callsign"]  and not isinstance(data["unit_callsign"], dict):
            return (False, "Bad Arg: unit_callsign must be a dict")
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
    
    