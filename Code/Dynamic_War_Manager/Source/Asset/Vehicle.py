from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
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
    Ground_Vehicle_Asset_Type
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

    def __init__(self, block: Block, name: Optional[str] = None, model: Optional[str]= None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, dcs_unit_data: Optional[dict] = None):   
                        
            super().__init__(block=block, name=name, description=description, category=category, asset_type=asset_type, functionality=functionality, cost=cost, value=value, resources_assigned=acp, resources_to_self_consume=rcp, payload=payload, position=position, volume=volume, crytical=crytical, repair_time=repair_time, role=role, dcs_unit_data=dcs_unit_data) 

            self._model = model #key per richiamare i datti definiti nella classe Vehicle_Data
            # propriety
            self._speed_off_road = {"nominal": None, "max": None}
            
            #vehicle_scores = get_vehicle_scores(model=model)
            self._vehicle_scores = get_vehicle_scores(model=model)

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

            # load primary asset data for his category
            for k, v in asset_data[self.category].items(): # block_class = "Military", category = "Armor", asset_type = "Infantry_Fighting_Vehicle"

                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True

            # air defence asset data for his category
            for k, v in asset_data_air_defense[self.category].items(): # block_class = "Military", category = "SAM_Big", asset_type = "Track_Radar"

                for k1, v1 in v.items():
                    key = k + "_" + k1
                if self.asset_type == key:
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

                # Check in Ground_Military_Vehicle_Asset
                ground_military = BLOCK_ASSET_CATEGORY.get("Ground_Military_Vehicle_Asset", {})
                if category in ground_military.keys():
                    vehicle_asset = list(ground_military[category].keys())

                # Check in Air_Defense_Asset
                air_defense = BLOCK_ASSET_CATEGORY.get("Air_Defense_Asset", {})
                if category in air_defense.keys():
                    air_defense_asset = list(air_defense[category].keys())

                # Check in Block_Infrastructure_Asset for Military blocks
                # Note: Military blocks may have infrastructure assets too
                # block_infra = BLOCK_ASSET_CATEGORY.get("Block_Infrastructure_Asset", {})
                # military_infra = block_infra.get("Military", {})
                # if category in military_infra.keys():
                #    struct_asset = list(military_infra[category].keys())

                if not vehicle_asset and not air_defense_asset:
                    logger.warning(f"Military category ({category}) not found in BLOCK_ASSET_CATEGORY")

                if asset_type in vehicle_asset or asset_type in air_defense_asset:
                   return (True, "OK")

                else:
                    # Check if asset_type exists in any category 
                    for cat in ground_military.values():
                        if asset_type in cat.keys():
                            return (True, "OK")
                    for cat in air_defense.values():
                        if asset_type in cat.keys():
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
    

    @property
    def isTank(self):
        return self.category == Ground_Vehicle_Asset_Type.TANK.value
    @property
    def isArmor(self):
        return self.category == Ground_Vehicle_Asset_Type.ARMORED.value
    @property
    def isMotorized(self):
        return self.category == Ground_Vehicle_Asset_Type.MOTORIZED.value
    @property
    def isArtillery_Semovent(self):
        return self.category == Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value
    @property
    def isArtillery_Fixed(self):
        return self.category == Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value
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
        return self.category == Ground_Vehicle_Asset_Type.SAM_BIG.value
    @property
    def isSAM_Medium(self):
        return self.category == Ground_Vehicle_Asset_Type.SAM_MEDIUM.value
    @property
    def isSAM_Small(self):
        return self.category == Ground_Vehicle_Asset_Type.SAM_SMALL.value
    @property
    def isAAA(self):
        return self.category == Ground_Vehicle_Asset_Type.AAA.value
    @property
    def isEWR(self):
        return self.category == Ground_Vehicle_Asset_Type.EWR.value
    @property
    def isCommandControl(self):
        return self.category == "Command_&_Control"
    


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
                
        if self.category == None:
            logger.warning("self.category not defined: Unable to set combat_power")
            return



        for act in actions:

            #if action and act!= action:# if action!=None set combat_power only for specific action, otherwise set combat_power value for any action
            #    continue

            # NOTA: Questo calcolo si basa sul valore di efficacia attibuito alla classificazione definita nel Context: tank, armor, ...
            # è opportuno rivederlo nell'ottica (1 + self._vehicle_scores['combat score'])di una valutazione più accurata: 
            #    attribuire una efficacia nell'attacco di una forza tank superiore rispetto ad una armor potrebbe essere erroneo,
            # Probabilmente è più opportuno valutare le capacità e prestazioni dello specifico veicolo in relazione all'azione da eseguire (attacco, difesa).

            # Check if category exists in GROUND_COMBAT_EFFICACY for this action
            # Calcolo della combat_power in relazione:
            # - all'azione da eseguire, 
            # - alla categoria del veicolo, 
            # - al suo punteggio di combattimento, 
            # - alla sua efficienza 
            # - applicando anche i pesi di confronto tra classi di veicoli, riportati mparametri della tabella GROUND_COMBAT_EFFICACY definita nel Context
            categories_in_action = GROUND_COMBAT_EFFICACY.get(act, {}).keys()
            if self.category in categories_in_action:
                relative_weight = 1 + GROUND_COMBAT_EFFICACY[act][self.category]  * 0.3 / 5  # weight of vehicle class effectiveness respect to other class vehicles (30% of specific vehicle weight)
                score_modifier = 1 + self._vehicle_scores['combat score']['global score']  # score modifier based on vehicle combat score
                combat_power[act] = relative_weight * score_modifier * self.efficiency
            else:
                # Category not in GROUND_COMBAT_EFFICACY (e.g., SAM, AAA, logistic vehicles)
                # Set a default combat power or skip
                logger.debug(f"Category '{self.category}' not found in GROUND_COMBAT_EFFICACY for action '{act}'. Setting combat_power to 0.")
                combat_power[act] = 0

        # call parent method
        self.set_combat_power_value({"ground": combat_power})

