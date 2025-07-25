from Dynamic_War_Manager.Source.Asset.Asset import Asset
from Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Dynamic_War_Manager.Source.DataType.Event import Event
from Dynamic_War_Manager.Source.DataType.Sphere import Sphere
from Dynamic_War_Manager.Source.DataType.Hemisphere import Hemisphere
from Dynamic_War_Manager.Source.DataType.Volume import Volume
from Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.Context.Context import STATE, BLOCK_CATEGORY, MILITARY_CATEGORY
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Mobile')

# ASSET
class Mobile(Asset) :    

    def __init__(self, block: Block, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, speed: Optional[float] = None, max_speed: Optional[float] = None, range: Optional[float] = None, fire_range: Optional[float] = None, dcs_unit_data: Optional[dict] = None):   
            
            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data) 
     
            # propriety   
            self._speed = speed
            self._max_speed = max_speed
            self._fire_range = fire_range
            self._range = range
            
            
            if dcs_unit_data: 
                result = self.checkParamDCS(dcs_unit_data)
                if self.checkParamDCS(dcs_unit_data): # update property with dcs_unit_data if defined 
                    self._nome = dcs_unit_data["unit_name"]
                    self._id = dcs_unit_data["unitId"]                
                    self._position = Point3D(dcs_unit_data["unit_x"], dcs_unit_data["unit_y"], dcs_unit_data["unit_alt"])# att: nella gestione dello z devi tener conto se BARO o ASL
                    self._health = dcs_unit_data["unit_health"]
                else:
                    raise Exception(f"Object not istantiate not valid DCS_DATA {result} .")
            else:
                raise Exception("Object not istantiate DCS_DATA is  None.")

            
            """

            dcs_unit_data = { "unit_health": int, "unit_index": int, "unit_name": str, "unit_type": str, "unit_unitId": int, "unit_communication": bool, 
                                   "unit_lateActivation": bool, "unit_start_time": int, "unit_frequency": float, "unit_x": float, "unit_y": float, 
                                   "unit_alt": float, "unit_alt_type": str, "heading": int, "unit_speed": float, "unit_hardpoint_racks": int, "unit_livery_id": int, 
                                   "unit_psi": float, "unit_skill": str, "unit_onboard_num": int, "unit_payload": str|Dict, "unit_callsign": str|Dict}
            
            self._unit_index: str|Optional[dict] = unit_index # DCS group unit_index - index Dict            
            self._unit_name: Optional[str] = unit_name # DCS unit group name - str
            self._unit_type: Optional[str] = unit_type # DCS unit group type - str
            self._unit_unitId: Optional[int] = unit_unitId # DCS unit group id - int
            self._unit_communication: Optional[bool] = unit_communication # DCS unit group communication - bool
            self._unit_lateActivation: Optional[bool] = unit_lateActivation # DCS unit group lateActivation - bool
            self._unit_start_time: Optional[int] = unit_start_time # DCS unit group start_time - int
            self._unit_frequency: Optional[float] = unit_frequency # DCS unit group frequency - float
            self._unit_x: Optional[float] = unit_x # DCS unit x - float
            self._unit_y: Optional[float] = unit_y # DCS unit y - float
            self._unit_alt: Optional[float] = unit_alt # DCS unit altitude - float
            self._unit_alt_type: Optional[str] = unit_alt_type # DCS unit altitude type - str (BARO, ...)
            self._heading: Optional[int] = heading # DCS unit heading - int
            self._unit_speed: Optional[float] = unit_speed # DCS unit speed - float
            self._unit_hardpoint_racks: Optional[int] = unit_hardpoint_racks # DCS unit hardpoint_racks - int
            self._unit_livery_id: Optional[int] = unit_livery_id # DCS unit livery_id - int
            self._unit_psi: Optional[float] = unit_psi # DCS unit psi - float
            self._unit_skill: Optional[str] = unit_skill # DCS unit skill - Literal (Average, ....)
            self._unit_onboard_num: Optional[int] = unit_onboard_num # DCS unit onboard_num - int
            self._unit_payload: str|Optional[dict] = unit_payload # DCS unit payload - Dict
            self._unit_callsign: str|Optional[dict] = unit_callsign  # DCS unit callsign - Dict
            self._unit_health: Optional[int] = health # DCS unit health - int [0-100] DEVI VEDERE NEI FILE TEMPORANEI GENERATI DOPO LA CONSLUSIONE DI UNA MISSIONE E PIMA DEL PROCESSAMENTO CON DCE
            """
    
            # Association    
            
            
            # check input parameters
            
    # methods

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, param):

        check_result = self.checkParam(speed = param)
        
        if not check_result[0]:
            raise Exception(check_result[1])    

        self._speed = param  
        return True
    

    @property
    def fire_range(self):
        return self._fire_range

    @fire_range.setter
    def fire_range(self, param):

        check_result = self.checkParam(fire_range = param)
        
        if not check_result[0]:
            raise Exception(check_result[1])    

        self._fire_range = param  
        return True

    def attackRange(self):
         #return value
         pass
    

    def airDefense(self):
        #return Volume
        pass

    @property
    def combat_power(self):
        pass


    def checkParam(speed: float, fire_range: float) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
        if speed and not isinstance(speed, float):
            return (False, "Bad Arg: speed must be a float")
        
        if fire_range and not isinstance(fire_range, float):
            return (False, "Bad Arg: fire_range must be a float")
    
        return (True, "OK")

    def checkParamDCS(data: dict):
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


    
