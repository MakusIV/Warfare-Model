from Dynamic_War_Manager.Source.Asset.Asset import Asset
from Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Dynamic_War_Manager.Source.DataType.Event import Event
from Dynamic_War_Manager.Source.DataType.Sphere import Sphere
from Dynamic_War_Manager.Source.DataType.Hemisphere import Hemisphere
from Dynamic_War_Manager.Source.DataType.Volume import Volume
from Dynamic_War_Manager.Source.DataType.Payload import Payload
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from Code.Dynamic_War_Manager.Source.Context.Context import (
    GROUND_ACTION, 
    AIR_TASK,
    SEA_TASK,
    MILITARY_CATEGORY,    
    MILITARY_FORCES,
    ACTION_TASKS
)

# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'Mobile').logger

# ASSET
class Mobile(Asset) :    

    def __init__(self, block: Block, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, resources_assigned: Optional[Payload] = None, resources_to_self_consume: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, speed: Optional[Dict] = {"nominal": None, "max": None}, range: Optional[float] = None, fire_range: Optional[float] = None, dcs_unit_data: Optional[dict] = None):   
            

            super().__init__(block=block, name=name, description=description, category=category, asset_type=asset_type, functionality=functionality, cost=cost, value=value, resources_assigned=resources_assigned, resources_to_self_consume=resources_to_self_consume, payload=payload, position=position, volume=volume, crytical=crytical, repair_time=repair_time, role=role, dcs_unit_data=dcs_unit_data) 
     

            # propriety   
            self._speed = speed
            
            # UTILIZZARE PER CALCOLO COMBAT_POWER
            # LA COMBAT_POWER PUO ASSUMERE QUALUNQUE VALORE, TUTTAVIA IL CONFRONTO DEVE ESSERE OMOGNENO PER UGUAL TIPI DI FORCE:
            # ground <-> ground, air <->air
            self._fire_range = fire_range
            self._range = range
            self._weapon = {}
            self._combat_power = {force: {task: 0.0 for task in ACTION_TASKS[force]} 
                for force in MILITARY_FORCES}
            """
            combat_power = {    "air": {"CAP": 0.0, "Intercept": 0.0, "Pinpoint_Strike": 0.0, ...},
            
                                "ground": {"Attack": 0.0 , "Defense": 0.0},
                                
                                "sea": {"Attack": 0.0 , "Defense": 0.0}
                                
                            }"""
            
            
            if dcs_unit_data: 
                result = self.checkParamDCS(dcs_unit_data)
                if self.checkParamDCS(dcs_unit_data): # update property with dcs_unit_data if defined 
                    self._nome = dcs_unit_data["unit_name"]
                    self._id = dcs_unit_data["unitId"]                
                    self._position = Point3D(dcs_unit_data["unit_x"], dcs_unit_data["unit_y"], dcs_unit_data["unit_alt"])# att: nella gestione dello z devi tener conto se BARO o ASL
                    self._health = dcs_unit_data["unit_health"]
                else:
                    raise Exception(f"Not valid DCS_DATA {result} . DCS compatibility could be compromised.")
            else:
                logger.warning("Not valid DCS_DATA. DCS compatibility could be compromised.")

               
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

    def combat_power(self, force: Optional[str] = None, action: Optional[str] = None) -> Optional[Union[Dict, float]]:

        if force is not None and not isinstance(force, str):
            raise TypeError(f"Expected str instance, got {type(force).__name__}")

        if force is not None and force not in MILITARY_FORCES:
            raise ValueError(f"force must be: {MILITARY_FORCES!r}")

        if action is not None and not isinstance(action, str):
            raise TypeError(f"Expected str instance, got {type(action).__name__}")

        if force is not None:
            admit_task = [task for task in ACTION_TASKS[force]]
            if action is not None and action not in admit_task:
                raise ValueError(f"action must be: {admit_task}")

        if force and action:
            return self._combat_power[force][action]

        if force:
            return self._combat_power[force]

        if action:
            result = {}
            for force in MILITARY_FORCES:
                for task in ACTION_TASKS[force]:
                    if action == task:
                        result[force]={task: self._combat_power[force][action]
                                       }
            return result

        return self._combat_power

        #return result

    def set_combat_power_value(self, combat_power: Dict):
        """Imposta il valore la combat_power del Mobile 
           E' il metodo utilizzato dalle classi derivate (Vehicle, Ship, Aircraft, ecc.) per settare il valore della combat_power dopo averlo calcolato specificatamente per lo specifico tipo di Mobile.

        Args:
            combat_power (Dict): _description_

        Raises:
            TypeError: _description_
            TypeError: _description_
            TypeError: _description_
            TypeError: _description_
        """

        if not isinstance(combat_power, Dict):
            raise TypeError(f"Expected Dict instance, got {type(combat_power).__name__}")
        
        keys = [key in MILITARY_FORCES for key in combat_power.keys()]

        if any(key in MILITARY_FORCES for key in combat_power.keys()):
            for force in combat_power.keys():
                if isinstance(combat_power[force], Dict):
                    if not any(key in ACTION_TASKS[force] for key in combat_power[force].keys()):
                        raise TypeError(f"Unexpected combat_power[{force}].keys: {combat_power}")
                else:
                    raise TypeError(f"Expected Dict, got {type(combat_power[force].value()).__name__}")
        else:
            raise TypeError(f"Unexpected combat_power.keys, got {combat_power.keys()}")
        
        self._combat_power = combat_power



    def checkParam(speed: float, fire_range: float) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          

        if speed and isinstance(speed, Dict):
            for key in speed.keys():
                if key not in ["cruise", "max"]:
                    return(False, (f"Unexpected speed.key: {key}. speed.keys() correct value: [\"cruise\", \"max\"]"))
                else:
                    continue        
        
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



