from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import get_aircraft_data, get_aircraft_scores, get_aircraft_combat_score
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Context.Context import (
    AIR_MILITARY_CRAFT_ASSET,
    BLOCK_ASSET_CATEGORY,
    BLOCK_INFRASTRUCTURE_ASSET,
    AIR_COMBAT_EFFICACY,
    ACTION_TASKS,
    combat_power_from_score,
)
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Threat import Threat
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.State import State
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'Aircraft').logger

# ASSET
class Aircraft(Mobile) :    

    def __init__(self, block: Block, name: Optional[str] = None, model: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, dcs_unit_data: Optional[dict] = None):

            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data)

            self._model = model  # key per Aircraft_Data._registry / AIRCRAFT

            # NOTA: self.speed è già inizializzato da Mobile.__init__ con lo stesso placeholder
            # {"nominal": None, "max": None}. Riassegnarlo qui passerebbe per Mobile.speed.setter,
            # che chiama self.checkParam(speed=...) — Aircraft.checkParam non accetta 'speed' e
            # solleverebbe TypeError ad ogni istanziazione reale (bug analogo a quello in Ship.py).

            self.set_combat_power(ACTION_TASKS['air'])

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
            asset_data = AIR_MILITARY_CRAFT_ASSET            

            for k, v in asset_data[self.category]:            
                    
                if self.asset_type == k:
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
            raise Exception(f"This asset {self!r} is not consistent with the ownership block - Asset category, type: {self.category, self.asset_type}Block: {self.block!r}")

        
        return False
    
    # use case methods
    def checkParam(self, asset_type: str = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""          
       
        if asset_type and (isinstance(asset_type, str)):        

            if self.block.block_class == "Military": # asset is a Military component
                
                asset_t = AIR_MILITARY_CRAFT_ASSET.keys()
                if asset_type in asset_t:
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Aircraft asset_type not found. Aircraft asset_type must be any value from: {asset_t!r}")
                    
            
            else:  # asset isn't a Military component (civilian or logistic not again implemented)
                asset_t = BLOCK_ASSET_CATEGORY[self.block.block_class][self.category].keys()

                if asset_type in asset_t:
                    return (True, "OK")
                
                else:
                    raise ValueError(f"Aircraft asset_type not found. Aircraft asset_type must be any value from: {asset_t!r}")
                
                    
        return (False, f"Bad Arg: Aircraft Asset_type must be any string{asset_type}")                                       



    def air_combat_power(self) -> float:
        """Combat power aggregata dell'aereo, indipendente dal task aereo (v. set_combat_power).

        A differenza dei veicoli/navi, per gli aerei i task (CAP, Strike, SEAD, ...) sono ruoli di
        missione, non posture tattiche mutuamente esclusive come Attack/Defense/Retrait: un aereo capace
        in CAP lo è anche in Intercept o Escort con lo stesso loadout aria-aria. Quindi qui c'è UN solo
        valore, calcolato dal punteggio di combattimento normalizzato del modello (il migliore loadout
        per ciascun task, sommato — v. Aircraft_Data.combat_aggregate/get_aircraft_combat_score) pesato
        per l'efficacia di classe del ruolo dell'aereo (Context.AIR_COMBAT_EFFICACY) e per l'efficienza.
        """
        if self._model is None or self.category is None:
            return 0.0
        return combat_power_from_score(
            category=self.category,
            score=get_aircraft_combat_score(self._model),
            efficacy_table=AIR_COMBAT_EFFICACY,
            efficiency=self.efficiency,
        )

    def set_combat_power(self, actions: Optional[Dict] = ACTION_TASKS["air"]):
        """
        Calculates and sets the combat power value for the specific aircraft.
        Unlike Vehicle/Ship, the value is the SAME single aggregate (air_combat_power()) replicated
        across every task in `actions`, since air tasks aren't mutually-exclusive tactical postures
        the way ground/sea actions are (see air_combat_power docstring). Callers that need the block's
        total air combat power must read a single task, not sum across tasks (they'd all be equal).

        args:
        actions - subset of ACTION_TASKS["air"] to populate. Defaults to all.

        raises:
        TypeError - if actions contains a value not in ACTION_TASKS["air"]

        -------------------------------

        Calcola ed imposta il valore di combat_power per lo specifico aereo.
        A differenza di Vehicle/Ship, il valore è LO STESSO aggregato singolo (air_combat_power())
        replicato su ogni task di `actions`, perché i task aria non sono posture tattiche mutuamente
        esclusive come le azioni di veicoli/navi (v. docstring di air_combat_power). I chiamanti che
        necessitano della combat power totale aerea del blocco devono leggere un solo task, non sommare
        sui task (sarebbero tutti uguali).

        args:
        actions - sottoinsieme di ACTION_TASKS["air"] da popolare. Default: tutti.

        raises:
        TypeError - se actions contiene un valore non presente in ACTION_TASKS["air"]
        """

        if actions and any(action not in ACTION_TASKS["air"] for action in actions):
            raise TypeError(f"Unexpected action in actions: {actions}. Expected actions are: {ACTION_TASKS['air']}")

        cp = self.air_combat_power()
        self.set_combat_power_value({"air": {act: cp for act in actions}})

    @property
    def isFighter(self):
        return self.category == "Fighter"
    @property
    def isFighterBomber(self):
        return self.category == "Fighter_Bomber"
    @property
    def isAttacker(self):
        return self.category == "Attacker"
    @property
    def isBomber(self):
        return self.category == "Bomber"
    @property
    def isHeavyBomber(self):
        return self.category == "Heavy_Bomber"
    @property
    def isAwacs(self):
        return self.category == "Awacs"
    @property
    def isRecon(self):
        return self.category == "Recon"
    @property
    def isTransport(self):
        return self.category == "Transport"
    @property
    def isHelicopter(self):
        return self.category == "Helicopter"
    

