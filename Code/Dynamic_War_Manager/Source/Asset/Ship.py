from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import get_ship_data, get_ship_scores
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.Context.Context import (
    SEA_MILITARY_CRAFT_ASSET,
    BLOCK_ASSET_CATEGORY,
    BLOCK_INFRASTRUCTURE_ASSET,
    SEA_COMBAT_EFFICACY,
    ACTION_TASKS,
    combat_power_from_score,
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
logger = Logger(module_name = __name__, class_name = 'Ship').logger

# ASSET
class Ship(Mobile) :    

    def __init__(self, block: Block, name: Optional[str] = None, model: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, dcs_unit_data: Optional[dict] = None):

            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data)

            self._model = model  # key per Ship_Data._registry

            # Profilo di velocita' canonico in m/s, popolato dal registry del modello.
            # (Prima non era popolabile affatto: il setter passava per checkParam, che le
            # sottoclassi sovrascrivono con firme senza 'speed' — v. Mobile.speed.setter.)
            self.load_speed_from_registry()
            # Scorta di munizioni dal registro (R3, v. Mobile.UNIT_COUNTED_WEAPON_TYPES).
            self.load_ammunition_from_registry()
            # Carburante dal registro (autonomia `range` in nm, v. Mobile.FUEL_FULL).
            self.load_fuel_from_registry()

            self._ship_scores = get_ship_scores(model=model)  # load data from Ship_Data.py module

            self.set_combat_power(ACTION_TASKS['sea'])
    
            # Association    
            
            
            # check input parameters
           
       # methods
    def loadAssetDataFromContext(self) -> bool:
        """Initialize some asset property loading data from Context module
            asset_type is Subcategory of BLOCK_ASSET 

        Returns:
            bool: True if data is loaded, otherwise False
        """     

        if self.block.isMilitary():
            asset_data = SEA_MILITARY_CRAFT_ASSET

            for k, v in asset_data[self.asset_type]:

                if self.category == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True              
        
        elif self.block.isLogistic():
            asset_data = BLOCK_INFRASTRUCTURE_ASSET

            for k, v in asset_data[self.block.block_class][self.category]:     # block_class = Transport, category = AircraftB,        
                    
                if self.asset_type == k:
                    self.cost = v["cost"]
                    self.value = v["value"]
                    self.requested_for_consume = v["rcp"]
                    self.repair_time = v["t2r"]
                    self._payload_perc = v["payload%"]
                    return True     
        
        else:
            raise Exception(f"This Ship Asset {self!r} is not consistent with the ownership block - Asset category, type: {self.category, self.asset_type}Block: {self.block!r}")

        
        return False
    
    # use case methods
    def checkParam(self, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
       
        if asset_type and (isinstance(asset_type, str)):        

            if self.block.block_class == "Military": # asset is a Military component
            
                if asset_type in SEA_MILITARY_CRAFT_ASSET.keys():
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Ship Asset category not defined. Aircraft Asset must be any value from: {SEA_MILITARY_CRAFT_ASSET.keys()}")
                    
            
            else:  # asset isn't a Military component (civilian or logistic not again implemented)
                asset_t = BLOCK_ASSET_CATEGORY[self.block.block_class][self.category].keys()

                if asset_type in asset_t:
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Aircraft asset_type not found. Aircraft asset_type must be any value from: {asset_t!r}")                
                    
        return (False, f"Bad Arg: Ship Asset_type must be any string from BLOCK_ASSET_CATEGORY {BLOCK_ASSET_CATEGORY!r}")                                       



    def set_combat_power(self, actions: Optional[Dict] = ACTION_TASKS["sea"]):
        """
        Calculates and sets the combat power value for the specific ship based on the specified action.
        If actions is None, calculates the combat power for all actions defined in ACTION_TASKS["sea"].

        args:
        action - action from Sea_Task: 'Attack', 'Defense', 'Retrait'

        raises:
        TypeError - if action is not in ACTION_TASKS["sea"]

        -------------------------------

        Calcola ed imposta il valore di combat_power per la specifica nave in funzione dell'azione specificata.
        Se actions è None, calcola il combat_power per tutte le azioni definite in ACTION_TASKS["sea"].

        args:
        action - action from Sea_Task: 'Attack', 'Defense', 'Retrait'

        raises:
        TypeError - if action is not in ACTION_TASKS["sea"]
        """

        combat_power = {}

        if actions and any(action not in ACTION_TASKS["sea"] for action in actions):
            raise TypeError(f"Unexpected action in actions: {actions}. Expected actions are: {ACTION_TASKS['sea']}")

        if self.asset_type == None:
            logger.warning("self.asset_type not defined: Unable to set combat_power")
            return

        for act in actions:
            # Calcolo della combat_power in relazione: all'azione da eseguire, alla classe generale
            # della nave (asset_type), al suo punteggio di combattimento, alla sua efficienza,
            # applicando i pesi di confronto tra classi di navi riportati nella tabella
            # SEA_COMBAT_EFFICACY definita nel Context.
            categories_in_action = SEA_COMBAT_EFFICACY.get(act, {}).keys()

            if self.asset_type in categories_in_action:
                combat_power[act] = combat_power_from_score(
                    category=self.asset_type,
                    score=self._ship_scores['combat score']['global_score'],  # global_score: normalizzato su tutto il registro, non solo sulla categoria (v. Ship_Data.py)
                    efficacy_table=SEA_COMBAT_EFFICACY[act],
                    efficiency=self.efficiency,
                )

            else:
                # asset_type not in SEA_COMBAT_EFFICACY (e.g., logistic ships)
                logger.debug(f"asset_type '{self.asset_type}' not found in SEA_COMBAT_EFFICACY for action '{act}'. Setting combat_power to 0.")
                combat_power[act] = 0

        self.set_combat_power_value({"sea": combat_power})

    @property
    def isDestroyer(self):
        return self.asset_type == "Destroyer"
    @property
    def isCarrier(self):
        return self.asset_type == "Carrier"
    @property
    def isCruiser(self):
        return self.asset_type == "Cruiser"
    @property
    def isFrigate(self):
        return self.asset_type == "Frigate"
    @property
    def isFastAttackShip(self):
        return self.asset_type == "FastAttackShip"
    @property
    def isTransport(self):
        return self.asset_type == "Transport"
    @property
    def isSubmarine(self):
        return self.asset_type == "Submarine"
    
    
    def get_physical_characteristics(self) -> Dict:
        """Returns the physical characteristics of the ship as defined in the Context module."""
        if self._model is None:
            logger.warning("Model not defined: Unable to get physical characteristics")
            return None
        
        ship_data = get_ship_data(model=self._model)
        physical_characteristics = ship_data.get('physical_characteristics', None)
        return physical_characteristics
    