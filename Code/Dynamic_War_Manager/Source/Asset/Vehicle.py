from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile, default_speed_profile
from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import get_vehicle_data, get_vehicle_scores
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.Context.Context import (
    GROUND_COMBAT_EFFICACY,
    GROUND_ACTION,
    AIR_DEFENSE_ASSET,
    BLOCK_ASSET_CATEGORY,
    BLOCK_INFRASTRUCTURE_ASSET,
    ACTION_TASKS,
    GROUND_MILITARY_VEHICLE_ASSET,
    Ground_Vehicle_Asset_Type,
    combat_power_from_score
)
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point3D

# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'Vehicle').logger

# ASSET
class Vehicle(Mobile) :    

    def __init__(self, block: Block, 
                 name: Optional[str] = None, 
                 model: Optional[str]= None, 
                 description: Optional[str] = None, 
                 category: Optional[str] = None, 
                 asset_type:Optional[str] = None, 
                 functionality: Optional[str] = None, 
                 cost: Optional[int] = None, 
                 value: Optional[int] = None, 
                 acp: Optional[Payload] = None, 
                 rcp: Optional[Payload] = None, 
                 payload: Optional[Payload] = None, 
                 position: Optional[Point3D] = None, 
                 volume: Optional[Volume] = None, 
                 crytical: Optional[bool] = False, 
                 repair_time: Optional[int] = 0, 
                 role: Optional[str] = None, 
                 dcs_unit_data: Optional[dict] = None):   
                        
            super().__init__(block=block, name=name, description=description, category=category, asset_type=asset_type, functionality=functionality, cost=cost, value=value, resources_assigned=acp, resources_to_self_consume=rcp, payload=payload, position=position, volume=volume, crytical=crytical, repair_time=repair_time, role=role, dcs_unit_data=dcs_unit_data) 

            self._model = model #key per richiamare i datti definiti nella classe Vehicle_Data
            # propriety
            # Profilo di velocita' canonico in m/s, col ramo 'off_road' proprio dei veicoli,
            # popolato da Vehicle_Data.speed_data. Sostituisce _speed_off_road, attributo che
            # restava a None e che nessuna riga del progetto leggeva.
            self._speed = default_speed_profile(off_road=True)
            self.load_speed_from_registry()
            # Scorta di munizioni dal registro (R3, v. Mobile.UNIT_COUNTED_WEAPON_TYPES).
            self.load_ammunition_from_registry()
            # Carburante dal registro (autonomia `range`, v. Mobile.FUEL_FULL).
            self.load_fuel_from_registry()

            #vehicle_scores = get_vehicle_scores(model=model)
            self._vehicle_scores = get_vehicle_scores(model=model) # load data from Vehicle_Data.py module

            #for task in ACTION_TASKS['ground']:                 
            self.set_combat_power(ACTION_TASKS['ground'])


            # dcs_data for vehicle

            # Association    
                    
            # check input parameters
            

    # methods    
    def loadAssetDataFromContext(self) -> bool:
        """Initialize some asset property loading data from Context module
            asset_type is Subcategory of BLOCK_ASSET 
            data asset:
            -cost:
            -value:
            -rcp:request c p
            -t2r: time to repair
            -payload%:

        raise: 
            Exception: if asset is not consistent with the ownership block

        Returns:
            bool: True if data is loaded, otherwise False
        """     

        
        if self.block.is_military(): # reference Block is Military
            asset_data = GROUND_MILITARY_VEHICLE_ASSET # load data from Context
            asset_data_air_defense = AIR_DEFENSE_ASSET # load data from Context

            # load primary asset data for his asset_type
            for k, v in asset_data[self.asset_type].items(): # block_class = "Military", asset_type = "Armored", category = "Infantry_Fighting_Vehicle"

                if self.category == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True

            # air defence asset data for his asset_type
            for k, v in asset_data_air_defense[self.asset_type].items(): # block_class = "Military", asset_type = "SAM_Big", category = "Track_Radar"

                for k1, v1 in v.items():
                    key = k + "_" + k1
                if self.category == key:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True

        

        
        elif self.block.is_logistic(): # reference Block is Logistic
            asset_data = BLOCK_INFRASTRUCTURE_ASSET

            for k, v in asset_data[self.block.block_class][self.category].items():  # block_class = Transport, category = "Road", asset_type = "Truck"

                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True     
        
        else:
            raise Exception(f"This asset is not consistent with the ownership block - Asset category, type: {self.category, self.asset_type}Block: {self.block!r}")

        
        return False
    
    # use case methods
    def checkParam(self, category: str = None, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""

        if asset_type and (isinstance(asset_type, str)):

            if self.block.block_class == "Military": # asset is a Military component

                vehicle_asset = []
                air_defense_asset = []

                # Check in Ground_Military_Vehicle_Asset (bucket key = asset_type, general class)
                ground_military = BLOCK_ASSET_CATEGORY.get("Ground_Military_Vehicle_Asset", {})
                if asset_type in ground_military.keys():
                    vehicle_asset = list(ground_military[asset_type].keys())

                # Check in Air_Defense_Asset
                air_defense = BLOCK_ASSET_CATEGORY.get("Air_Defense_Asset", {})
                if asset_type in air_defense.keys():
                    air_defense_asset = list(air_defense[asset_type].keys())

                # Check in Block_Infrastructure_Asset for Military blocks
                # Note: Military blocks may have infrastructure assets too
                # block_infra = BLOCK_ASSET_CATEGORY.get("Block_Infrastructure_Asset", {})
                # military_infra = block_infra.get("Military", {})
                # if asset_type in military_infra.keys():
                #    struct_asset = list(military_infra[asset_type].keys())

                if not vehicle_asset and not air_defense_asset:
                    logger.warning(f"Military asset_type ({asset_type}) not found in BLOCK_ASSET_CATEGORY")

                if category in vehicle_asset or category in air_defense_asset:
                   return (True, "OK")

                else:
                    # Check if category (sub-class) exists under any asset_type bucket
                    for cat in ground_military.values():
                        if category in cat.keys():
                            return (True, "OK")
                    for cat in air_defense.values():
                        if category in cat.keys():
                            return (True, "OK")

            else:  # asset isn't a Military component

                block_infra = BLOCK_ASSET_CATEGORY.get("Block_Infrastructure_Asset", {})
                block_class_data = block_infra.get(self.block.block_class, {})

                if category:
                    category_data = block_class_data.get(category, {})
                    struct_asset = list(category_data.keys())
                else:
                    struct_asset = list(block_class_data.keys())

                if asset_type in struct_asset:
                    return (True, "OK")

            return (False, f"Bad Arg: Vehicle asset_type must be any string from BLOCK_ASSET_CATEGORY")


        #if category and isinstance(category, str):

        #    vehicle_asset = list(BLOCK_ASSET_CATEGORY.get("Ground_Military_Vehicle_Asset", {}).keys())
        #    air_defense_asset = list(BLOCK_ASSET_CATEGORY.get("Air_Defense_Asset", {}).keys())
        #    block_infra = BLOCK_ASSET_CATEGORY.get("Block_Infrastructure_Asset", {})
        #    struct_asset = list(block_infra.get(self.block.block_class, {}).keys())

        #    if category in vehicle_asset or category in air_defense_asset or category in struct_asset:
        #        return (True, "OK")

        #    return (False, "Bad Arg: Vehicle category must be any string from GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, STRUCTURE_ASSET_CATEGORY")

        return (True, "OK")
    

    def get_physical_characteristics(self) -> Dict:
        """Returns the physical characteristics of the vehicle as defined in the Context module."""
        if self._model is None:
            logger.warning("Model not defined: Unable to get physical characteristics")
            return None
        
        vehicle_data = get_vehicle_data(model=self._model)
        physical_characteristics = vehicle_data.get('physical_characteristics', None)
        return physical_characteristics

    def set_volume_from_physical_characteristics(self):
        """Sets the volume of the vehicle based on its physical characteristics defined in the Context module."""
        
        physical_characteristics = self.get_physical_characteristics()
        
        if physical_characteristics is None:
            logger.warning("Unable to set volume: Physical characteristics not available")
            return
        
        length = physical_characteristics.get('length', None)
        width = physical_characteristics.get('width', None)
        height = physical_characteristics.get('height', None)

        if length is not None and width is not None and height is not None:
            volume = Volume(length=length, width=width, height=height)

            if self.volume is None:                
                logger.warning(f"Volume {self.volume} set to {volume} based on physical characteristics")
                self.volume = volume
        else:
            logger.warning("Unable to set volume: Incomplete physical characteristics")

    @property
    def isTank(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.TANK.value
    @property
    def isArmor(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.ARMORED.value
    @property
    def isMotorized(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.MOTORIZED.value
    @property
    def isArtillery_Semovent(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value
    @property
    def isArtillery_Fixed(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value
    @property
    def isArtillery(self):
        return self.isArtillery_Fixed or self.isArtillery_Semovent
    @property
    def isAntiAircraft(self):
        return self.isSAM or self.isAAA
    @property
    def isSAM(self):
        return self.isSAM_Big or self.isSAM_Medium or self.isSAM_Small
    @property
    def isSAM_Big(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.SAM_BIG.value
    @property
    def isSAM_Medium(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.SAM_MEDIUM.value
    @property
    def isSAM_Small(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.SAM_SMALL.value
    @property
    def isAAA(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.AAA.value
    @property
    def isEWR(self):
        return self.asset_type == Ground_Vehicle_Asset_Type.EWR.value
    @property
    def isCommandControl(self):
        return self.category == "Command_&_Control"
    
     #Placeholder Methods for Future Implementation
    
  

    def set_combat_power(self, actions: Optional[Dict]=ACTION_TASKS["ground"]):
        """
        Calculates and sets the combat power value for the specific vehicle based on the specified action.
        If actions is None, calculates the combat power for all actions defined in ACTION_TASKS["ground"].

        args:
        action - action from GROUND_ACTION: 'Attack', 'Defense', 'Maintain', 'Retrait'

        raises:
        TypeError - if action is not in ACTION_TASKS["ground"]

        -------------------------------
        
        Calcola ed imposta il valore di combat_power per lo specifico  veicolo in funzione dell'azione specificata.
        Se actions è None, calcola il combat_power per tutte le azioni definite in ACTION_TASKS["ground"].


        args:
        action - action from GROUND_ACTION: 'Attack', 'Defense', 'Maintain', 'Retrait'

        raises:
        TypeError - if action is not in ACTION_TASKS["ground"] 
        """
        
        #force ="ground" # Vehicle is a ground asset
        combat_power = {}

        if actions and any(action not in ACTION_TASKS["ground"] for action in actions):
            raise TypeError(f"Unexpected action in actions: {actions}. Expected actions are: {ACTION_TASKS['ground']}")
                
        if self.asset_type == None:
            logger.warning("self.asset_type not defined: Unable to set combat_power")
            return

        for act in actions:
            # Check if asset_type exists in GROUND_COMBAT_EFFICACY for this action
            # Calcolo della combat_power in relazione:
            # - all'azione da eseguire,
            # - alla classe generale del veicolo (asset_type),
            # - al suo punteggio di combattimento,
            # - alla sua efficienza
            # - applicando anche i pesi di confronto tra classi di veicoli, riportati mparametri della tabella GROUND_COMBAT_EFFICACY definita nel Context
            categories_in_action = GROUND_COMBAT_EFFICACY.get(act, {}).keys()

            if self.asset_type in categories_in_action:
                combat_power[act] = combat_power_from_score(
                    category=self.asset_type,
                    score=self._vehicle_scores['combat score']['global_score'],  # global_score: normalizzato su tutto il registro, non solo sulla categoria (v. Vehicle_Data.py)
                    efficacy_table=GROUND_COMBAT_EFFICACY[act],
                    efficiency=self.efficiency,
                )

            else:
                # asset_type not in GROUND_COMBAT_EFFICACY (e.g., SAM, AAA, logistic vehicles)
                # Set a default combat power or skip
                logger.debug(f"asset_type '{self.asset_type}' not found in GROUND_COMBAT_EFFICACY for action '{act}'. Setting combat_power to 0.")
                combat_power[act] = 0
        # call parent method
        self.set_combat_power_value({"ground": combat_power})

