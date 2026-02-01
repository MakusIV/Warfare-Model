'''
Vehicle_Data

Singleton Class

NOTA: il calcolo dello score normalizzato deve essere effettuato considerando tipologie simili:
fighter-fighter, bomber-bomber ecc. altrimenti c'è il rischio che le differenze di score tra due stesse tipologie
siano ridotte causa il valutazione sottostimata delle score totale


'''

from functools import lru_cache
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import get_weapon_score
from Code.Dynamic_War_Manager.Source.Context.Context import GROUND_ACTION, ACTION_TASKS, BLOCK_ASSET_CATEGORY, Ground_Vehicle_Asset_Type
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import convert_mph_to_kmh
from sympy import Point3D
from tabulate import tabulate
import pandas as pd
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Vehicle_Data').logger


VEHICLE_TASK = GROUND_ACTION
MODES = ACTION_TASKS.keys()
# AVAILABLE CATEGORIES : Tank, Armored, Motorized, Artillery_Fixed, Artillery_Semovent, SAM_Big, SAM_Medium, SAM_Small, EWR, AAA from Context BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"], BLOCK_ASSET_CATEGORY["Air_Defense_Asset"].
# Sostituisce le due righe sottostanti con Ground_Vehicle_Asset_Type Enum
CATEGORY = set(BLOCK_ASSET_CATEGORY['Ground_Military_Vehicle_Asset'].keys())
CATEGORY.update(BLOCK_ASSET_CATEGORY['Air_Defense_Asset'].keys())

@dataclass
class Vehicle_Data:

    _registry = {}
    
    def __init__(self, constructor: str, made: str, model: str, category: str, start_service: str, end_service: str, cost: int, range: int, roles: str, engine: Dict, weapons: Dict, radar: Dict, TVD: Dict, communication: Dict, hydraulic: Dict, protections: Dict, speed_data: Dict):
        self.constructor = constructor
        self.made = made
        self.model = model # registry keys
        self.category = category #Tank, Armored, Motorized from Context BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"], BLOCK_ASSET_CATEGORY["Air_Defense_Asset"].
        self.start_service = start_service
        self.end_service = end_service
        self.cost = cost
        self.range = range
        self.roles = roles
        self.engine = engine
        self.weapons = weapons #{'model': quantity}
        self.radar = radar
        self.TVD = TVD
        self.communication = communication
        self.hydraulic = hydraulic
        self.protections = protections
        self.speed_data = speed_data

        Vehicle_Data._registry[self.model] = self

    # --- Getter e Setter ---
    def engine(self):
        return self.engine
    
    def engine(self, engine):
        self.engine = engine

    def model(self):
        return self.model
    
    def model(self, model):
        self.model = model

    def made(self):
        return self.made
    
    def made(self, made):
        self.made = made

    def get_vehicle(self, model: str):
        return self._registry.get(model)
    # ... (altri getter/setter per tutte le proprietà)

    
    # --- Implementazioni predefinite delle formule ---
    #@lru_cache
    def _radar_eval(self, modes: Optional[List] = None) -> float:
        """Evaluates the radar capabilities of the vehicle based on predefined weights.

        Params:
            Optional[List]: modes = []  with : 'air', 'ground', 'sea'

        Raises:
            TypeError: if modes element 

        Returns:
            float: radar score value
        """
        if not self.radar:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Radar not defined.")
            return 0.0
        
        if not modes:
            modes = MODES #['air', 'ground', 'sea']
        elif not isinstance(modes, List) or not all ( m in MODES for m in modes ):
            raise TypeError(f"modes must be a List of string with value:  {MODES!r}, got {modes!r}.")
    
        
        weights = {
            'tracking_range': 0.2,
            'acquisition_range': 0.1,
            'engagement_range': 0.3,
            'multi_target': 0.4
        }
        score = 0.0
        
        for m in modes:
            cap = self.radar['capabilities'][m]
            if cap[0]: 
                score += cap[1].get('tracking_range', 0) * weights['tracking_range']
                score += cap[1].get('acquisition_range', 0) * weights['acquisition_range']
                score += cap[1].get('engagement_range', 0) * weights['engagement_range']
                score += cap[1].get('multi_target_capacity', 0) * weights['multi_target']
        
        return score
    
    def _TVD_eval(self, modes: Optional[List] = None) -> float:
        """Evaluates the radar capabilities of the vehicle based on predefined weights."""
        if not self.TVD:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - TVD not defined.")
            return 0.0
        
        if not modes:
            modes = MODES #['air', 'ground', 'sea']
        elif not isinstance(modes, List) or not all ( m in MODES for m in modes ):
            raise TypeError(f"modes must be a List of string with value:  {MODES!r}, got {modes!r}.")
        
        weights = {
            'tracking_range': 0.2,
            'acquisition_range': 0.1,
            'engagement_range': 0.3,
            'multi_target': 0.4
        }
        score = 0.0
        
        for m in modes:
            cap = self.TVD['capabilities'][m]
            if cap[0]: 
                score += cap[1].get('tracking_range', 0) * weights['tracking_range']
                score += cap[1].get('acquisition_range', 0) * weights['acquisition_range']
                score += cap[1].get('engagement_range', 0) * weights['engagement_range']
                score += cap[1].get('multi_target_capacity', 0) * weights['multi_target']
        
        return score

    def _reliability_eval(self):
        """evaluate reliability (mtbf) of vehicle subsystem

        Returns:
            float: time (hour) before fault of an vehicle subsystem
        """                
        components = [
            self.engine.get('reliability', {}).get('mtbf', 0) if self.engine is not None and self.engine.get('reliability') else None,
            self.radar.get('reliability', {}).get('mtbf', 0) if self.radar is not None and self.radar.get('reliability') else None,
            self.TVD.get('reliability', {}).get('mtbf', 0) if self.TVD is not None and self.TVD.get('reliability') else None,
            self.communication.get('reliability', {}).get('mtbf', 0) if self.communication is not None and self.communication.get('reliability') else None,
            self.protections.get('reliability', {}).get('mtbf', 0) if self.protections is not None and self.protections.get('reliability') else None,            
            self.hydraulic.get('reliability', {}).get('mtbf', 0) if self.hydraulic is not None and self.hydraulic.get('reliability') else None
        ]
        filtered_components = [x for x in components if x is not None]
        # l'mtbf del singolo sottosistema incide nel valore finale del 30% mentre il valore medio del 70%
        return min(filtered_components) * 0.3 + 0.7 * sum(filtered_components) / len(filtered_components) # vehicle mtbf
    
    def _maintenance_eval(self):
        """evaluate maintenance load (mttr) requested of vehicle subsystem

        Returns:
            float: hour quantity rappresentative of maintenance job
        """
        components = [
            self.engine.get('reliability', {}).get('mttr', 0) if self.engine is not None and self.engine.get('reliability') else None,
            self.radar.get('reliability', {}).get('mttr', 0) if self.radar is not None and self.radar.get('reliability') else None,
            self.TVD.get('reliability', {}).get('mttr', 0) if self.TVD is not None and self.TVD.get('reliability') else None,
            self.communication.get('reliability', {}).get('mttr', 0) if self.communication is not None and self.communication.get('reliability') else None,
            self.protections.get('reliability', {}).get('mttr', 0) if self.protections is not None and self.protections.get('reliability') else None,            
            self.hydraulic.get('reliability', {}).get('mttr', 0) if self.hydraulic is not None and self.hydraulic.get('reliability') else None
        ]
        filtered_components = [x for x in components if x is not None]
        # l'mttr del singolo sottosistema incide nel valore finale del 30% mentre il valore medio del 70%
        return min(filtered_components) * 0.3 + 0.7 * sum(filtered_components) / len(filtered_components) # vehicle mttr
    
    def _avalaiability_eval(self):
        """evaluate avalaiability of vehicle

        Returns:
            float: avalaiability value (value = mtbf/mttr)
        """
        mtbf = self._reliability_eval()
        mttr = self._maintenance_eval()

        if mtbf == 0:
            return 0.0
        
        # Calcola il punteggio di disponibilità come rapporto tra MTBF e (MTBF + MTTR)
        ratio = mtbf / mttr if mttr > 0 else 0.0        
        return ratio

     #@lru_cache
    
    def _speed_eval(self):
        """Evaluates the speed of the vehicle.
        Args:
            metric (str): 'metric' for km/h and meters, 'imperial' for mph and feet.
            
        Returns:
            float: Calculated speed score.
        Raises:
            ValueError: If altitude is negative or metric is not 'metric' or 'imperial'.
        """

        if not self.speed_data:
            logger.warning("speed_data not defined.")
            return 0.0

        weights = {'sustained': 0.3, 'max': 0.5, 'off_road': 0.2}
        score = 0

        for speed_type, weight in weights.items():
            data = self.speed_data.get(speed_type, {})
            metric = data.get('metric')

            if metric not in ['metric', 'imperial']:
                raise ValueError(f"metric must be 'metric' or 'imperial', got {metric!r}.")
            
            speed = data.get('speed', 0)

            if metric == 'imperial':
                speed = convert_mph_to_kmh(speed)
        
            score += speed * weight # - data.get('consume', 0) * 0.001
            
        return score / sum(weights.values())

    def _weapon_eval(self):
        """Returns the score of all installed weapons

        Returns:
            float: weapons combat score
        """
              
        '''
        'weapons': {
            'cannons': [('2A46M', 42)],
            'missiles': [('9K119M', 6)],
            'machine_guns': [('PKT-7.62', 1), ('Kord-12.7', 1)],
         '''
        score = 0.0

        for weapon_type, weapon in self.weapons.items():

            for weapon_item in weapon:
                factor_ammo_quantity = 1

                if weapon_type == 'CANNONS':
                    factor_ammo_quantity += weapon_item[1] / 40 # 40 reference for cannons (42 cannons ammo -> factor_ammo_quantity = 1.05) 

                elif weapon_type == 'MISSILES':
                    factor_ammo_quantity += weapon_item[1] / 3 # 3 reference for missiles (6 missiles -> factor_ammo_quantity = 1.5) 
                
                elif weapon_type == 'ROCKETS':
                    factor_ammo_quantity += weapon_item[1] / 8 # 8 reference for rockets (16 rockets -> factor_ammo_quantity = 2) 
                
                #else:
                #    logger.warning(f"weapon_type unknow, got {weapon_type}"                                   
                score += get_weapon_score( weapon_type = weapon_type, weapon_model = weapon_item[0] ) * (1 + factor_ammo_quantity * 0.1) # incremento del 10% del punteggio dell'arma in base alla quantità di munizionamento disponibile

        return score

    def _protection_eval(self):
        """Evaluates the protection capabilities of the vehicle.

        Considers:
        - Base armor thickness by zone (front, lateral, back, turret)
        - Active protection systems (countermeasures)
        - Reactive armor (ERA)

        Returns:
            float: protection score
        """
        if not self.protections:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Protections not defined.")
            return 0.0

        # Pesi per le zone di corazzatura (front e turret più importanti)
        zone_weights = {
            'front': 0.35,
            'turret': 0.30,
            'lateral': 0.20,
            'back': 0.15
        }

        # Pesi per i tipi di munizioni (APFSDS più pericoloso, quindi protezione più importante)
        ammo_weights = {
            'APFSDS': 0.40,
            'HEAT': 0.30,
            '2HEAT': 0.35,
            'AP': 0.15,
            'HE': 0.10
        }

        # Valore di riferimento per normalizzazione (mm equivalenti)
        reference_value = 100.0

        score = 0.0

        # 1. Valutazione corazzatura base
        armor = self.protections.get('armor')
        if armor:
            for zone, zone_weight in zone_weights.items():
                zone_data = armor.get(zone)
                if zone_data and zone_data[0]:  # (True, {...})
                    armor_values = zone_data[1]
                    # Calcola score pesato per tipo di munizione
                    zone_score = 0.0
                    total_ammo_weight = 0.0
                    for ammo_type, thickness in armor_values.items():
                        ammo_weight = ammo_weights.get(ammo_type, min(ammo_weights.values()))
                        zone_score += (thickness / reference_value) * ammo_weight
                        total_ammo_weight += ammo_weight

                    if total_ammo_weight > 0:
                        zone_score = zone_score / total_ammo_weight  # Normalizza per peso totale

                    score += zone_score * zone_weight

        # 2. Valutazione corazzatura reattiva (ERA)
        reactive = self.protections.get('reactive')
        if reactive and reactive.get('increment_thickness'):
            era_bonus = 0.0
            for zone, zone_weight in zone_weights.items():
                zone_data = reactive['increment_thickness'].get(zone)
                if zone_data and zone_data[0]:
                    era_values = zone_data[1]
                    zone_era = 0.0
                    total_ammo_weight = 0.0
                    for ammo_type, thickness in era_values.items():
                        ammo_weight = ammo_weights.get(ammo_type, 0.1)
                        zone_era += (thickness / reference_value) * ammo_weight
                        total_ammo_weight += ammo_weight

                    if total_ammo_weight > 0:
                        zone_era = zone_era / total_ammo_weight

                    era_bonus += zone_era * zone_weight

            score += era_bonus

        # 3. Valutazione protezione attiva (APS)
        active = self.protections.get('active')
        if active:
            countermeasures = active.get('threath_countermeasure', [])
            # Bonus per ogni tipo di contromisura (max 4 tipi comuni)
            aps_bonus = len(countermeasures) * 0.5  # 0.5 punti per tipo
            score += aps_bonus

        return score

    def _communication_eval(self) -> float:
        """Evaluates the communication capabilities of the vehicle.

        Considers:
        - navigation_accuracy: precision of navigation system (0-1)
        - communication_range: communication range in km

        Returns:
            float: communication score
        """
        if not self.communication:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Communication not defined.")
            return 0.0

        capabilities = self.communication.get('capabilities')
        if not capabilities:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Communication capabilities not defined.")
            return 0.0

        weights = {
            'navigation_accuracy': 0.4,
            'communication_range': 0.6
        }

        # Valori di riferimento per normalizzazione
        reference_values = {
            'navigation_accuracy': 1.0,  # max accuracy
            'communication_range': 300.0  # km (riferimento per sistemi avanzati)
        }

        score = 0.0
        navigation_accuracy = capabilities.get('navigation_accuracy', 0)
        communication_range = capabilities.get('communication_range', 0)

        # Normalizza e applica i pesi
        score += (navigation_accuracy / reference_values['navigation_accuracy']) * weights['navigation_accuracy']
        score += (communication_range / reference_values['communication_range']) * weights['communication_range']

        return score

    def _hydraulic_eval(self) -> float:
        """Evaluates the hydraulic system capabilities of the vehicle.

        Considers:
        - pressure: hydraulic system pressure (PSI)
        - fluid_capacity: hydraulic fluid capacity (liters)

        Returns:
            float: hydraulic system score
        """
        if not self.hydraulic:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Hydraulic system not defined.")
            return 0.0

        capabilities = self.hydraulic.get('capabilities')
        if not capabilities:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Hydraulic capabilities not defined.")
            return 0.0

        weights = {
            'pressure': 0.6,
            'fluid_capacity': 0.4
        }

        # Valori di riferimento per normalizzazione
        reference_values = {
            'pressure': 4000.0,  # PSI (riferimento per sistemi ad alta pressione)
            'fluid_capacity': 80.0  # litri (riferimento per veicoli pesanti)
        }

        score = 0.0
        pressure = capabilities.get('pressure', 0)
        fluid_capacity = capabilities.get('fluid_capacity', 0)

        # Normalizza e applica i pesi
        score += (pressure / reference_values['pressure']) * weights['pressure']
        score += (fluid_capacity / reference_values['fluid_capacity']) * weights['fluid_capacity']

        return score

    def _range_eval(self) -> float:
        """Evaluates the operational range of the vehicle.

        Considers:
        - range: maximum operational range in km

        Returns:
            float: range score
        """
        if not self.range:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Range not defined.")
            return 0.0

        # Valore di riferimento per normalizzazione (km)
        # 800 km è un buon riferimento per veicoli corazzati moderni
        reference_range = 800.0

        score = self.range / reference_range

        return score
    
    def _combat_eval(self):        
        """Returns the combat score calculated by considering the individual scores of the vehicle's subsystems

        Returns:
            float: combat score
        """
        
        params = {   
                    'weapon':           { 'score': self._weapon_eval(), 
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 10, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 10,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 10,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 10,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 10,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 5,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 10
                                                      } }, 
                    'radar':            { 'score': self._radar_eval(), 
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 2, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 2,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 7,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 10,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 7
                                                      } }, 
                    'TVD':              { 'score': self._TVD_eval(),
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 3, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 3,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 3,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 3,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 5,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 5,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 1,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 5
                                                      } }, 
                    'protection':       { 'score': self._protection_eval(), 
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 10, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 10,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 2,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 2,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 10
                                                      } },                     
                    'communication':    { 'score': self._communication_eval(), 
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 3, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 3,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 3,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 1,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 3,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 3,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 3,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 1,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 3,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 3
                                                      } }, 
                    'speed_data':       { 'score': self._speed_eval(),
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 8, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 8,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 7,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 1,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 4,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 3,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 3,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 5,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 1,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 5
                                                      }  }, 
                    'hydraulic':        { 'score': self._hydraulic_eval(), 
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 2, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 2,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 2,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 2,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 2,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 2,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 2
                                                      } }, 
                    'range':            { 'score': self._range_eval(), 
                                          'weights': {Ground_Vehicle_Asset_Type.TANK.value: 5, 
                                                      Ground_Vehicle_Asset_Type.ARMORED.value: 10,
                                                      Ground_Vehicle_Asset_Type.MOTORIZED.value: 10,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value: 10,
                                                      Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_BIG.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 10,
                                                      Ground_Vehicle_Asset_Type.SAM_SMALL.value: 10,
                                                      Ground_Vehicle_Asset_Type.EWR.value: 5,
                                                      Ground_Vehicle_Asset_Type.AAA.value: 10
                                                      } }
                }
        
        tot_weights = sum( data['weights'][self.category] for param, data in params.items() )
        return sum( data['score'] * data['weights'][self.category] for param, data in params.items() ) / tot_weights


    # --- Metodi di confronto normalizzati ---
    def get_normalized_weapon_score(self, category: Optional[str] = None):
        """returns weapon score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized weapon score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]

        scores = [ac._weapon_eval() for ac in vehicles]
        return self._normalize(self._weapon_eval(), scores)

    # --- Metodi di confronto normalizzati ---
    def get_normalized_radar_score(self, modes: Optional[Dict] = None, category: Optional[str] = None):
        """returns radar score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized radar score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]

        scores = [ac._radar_eval(modes = modes) for ac in vehicles]
        return self._normalize(self._radar_eval(modes = modes), scores)
    
    def get_normalized_TVD_score(self, modes: Optional[Dict] = None, category: Optional[str] = None):
        """returns TVD score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized TVD score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._TVD_eval(modes = modes) for ac in vehicles]
        return self._normalize(self._TVD_eval(modes = modes), scores)
    
    def get_normalized_speed_score(self, category: Optional[str] = None):
        """returns speed score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized speed score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._speed_eval() for ac in vehicles]
        return self._normalize(self._speed_eval(), scores)

    def get_normalized_reliability_score(self, category: Optional[str] = None):
        """returns reliability score (mtbf) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized reliability score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._reliability_eval() for ac in vehicles]
        return self._normalize(self._reliability_eval(), scores)
    
    def get_normalized_avalaiability_score(self, category: Optional[str] = None):
        """returns avalaiability score (mtbf/mttr) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized avalaiability score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._avalaiability_eval() for ac in vehicles]
        return self._normalize(self._avalaiability_eval(), scores)
    
    def get_normalized_maintenance_score(self, category: Optional[str] = None):
        """returns maintenance score (mttr) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized maintenance score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._maintenance_eval() for ac in vehicles]
        return 1- self._normalize(self._maintenance_eval(), scores)        

    def get_normalized_protection_score(self, category: Optional[str] = None):
        """returns protection score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized protection score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._protection_eval() for ac in vehicles]
        return self._normalize(self._protection_eval(), scores)

    def get_normalized_combat_score(self, category: Optional[str] = None):
        """returns combat score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized combat score score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._combat_eval() for ac in vehicles]
        return self._normalize(self._combat_eval(), scores)

    def get_normalized_communication_score(self, category: Optional[str] = None):
        """Returns communication score normalized from 0 (min score) to 1 (max score)

        Args:
            category (Optional[str], optional): Vehicle category for comparison. Defaults to all categories.

        Returns:
            float: normalized communication score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category must be string with value: {CATEGORY!r}, got {category!r}.")

        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._communication_eval() for ac in vehicles]
        return self._normalize(self._communication_eval(), scores)

    def get_normalized_hydraulic_score(self, category: Optional[str] = None):
        """Returns hydraulic system score normalized from 0 (min score) to 1 (max score)

        Args:
            category (Optional[str], optional): Vehicle category for comparison. Defaults to all categories.

        Returns:
            float: normalized hydraulic score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category must be string with value: {CATEGORY!r}, got {category!r}.")

        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._hydraulic_eval() for ac in vehicles]
        return self._normalize(self._hydraulic_eval(), scores)

    def get_normalized_range_score(self, category: Optional[str] = None):
        """Returns operational range score normalized from 0 (min score) to 1 (max score)

        Args:
            category (Optional[str], optional): Vehicle category for comparison. Defaults to all categories.

        Returns:
            float: normalized range score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category must be string with value: {CATEGORY!r}, got {category!r}.")

        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category]
        scores = [ac._range_eval() for ac in vehicles]
        return self._normalize(self._range_eval(), scores)

    def _normalize(self, value, scores):
        """Normalize values from 0 to 1

        Args:
            value (_type_): value to normalize
            scores (_type_): list of values for normalization calculus

        Returns:
            float: score (from 0 to 1)
        """
        if not scores:
            return 0
        min_val = min(scores)
        max_val = max(scores)
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)


    def task_score(self, task: str, loadout: Dict[str, any], target_dimension: Dict[str, any], minimum_target_destroyed: float):
        #VALUTA SE QUESTA FUNZIONE DEVE ESSERE IMPLEMENTATA NEL MODULO ATO NON QUI CONSIDERANDO CHE DEVE GESTIRE IL LOADOUT DELLE WEAPON

        if not task or not isinstance(task, str):
            raise TypeError ("task must be a string")
        if task not in GROUND_ACTION:
            raise ValueError(f"task must be a string with values: {GROUND_ACTION!r}, got {task!r}")
        
    
        if task in ['CAP', 'Intercept', 'Fighter_Sweep', 'Escort', 'Recon']:
            score_radar = self.get_normalized_radar_score(mode = ['air'])
            target_destroyed  = self._eval_destroyed_quantity_with_ordinance( task = task, loadout = loadout, target = target_dimension)
            #dovresti anche inserire la valutazione sulle capacità di autodifesa e quelle relative al range

        elif task in ['Strike', 'CAS', 'Pinpoint_Strike', 'SEAD']:
            score_radar = self.get_normalized_radar_score(['ground'])
            pass
            
        elif task in ['Anti_Ship']:
            score_radar = self.get_normalized_radar_score(['sea'])
            pass

        else:
            score_radar = 0.0
            pass

        if target_destroyed < minimum_target_destroyed:
            return 0.0

        return target_destroyed * score_radar
    
    #  VALUTA SE QUESTA FUNZIONE DEVE ESSERE IMPLEMENTATA NEL MODULO ATO NON QUI CONSIDERANDO CHE DEVE GESTIRE IL PAYLOAD DELLE WEAPON
    def task_score_cost_ratio(self):
        pass
 

# VEHICLE DATA

# metric = metric - > speed: km/h, altitude: m, radar/TVD/radioNav range: km 
# metric = imperial - > speed: mph, altitude: feet, radar/TVD/radioNav range: nm

T90_data = {
    'constructor': 'UVTZ',    
    'model': 'T-90M',
    'made': 'Russia',
    'start_service': 2020,
    'end_service': None,
    'category': 'Tank', # Main Battle Tank
    'cost': 4, # M$
    'range': 550, # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Multifuel 12 Cylinders', 
        'capabilities': {'thrust': 840, 'fuel_efficiency': 0.8, 'type': 'multifuel'}, 
        'reliability': {'mtbf': 40, 'mttr': 5}
    },
    'weapons': {
        'CANNONS': [('2A46M', 42)],
        'MISSILES': [('9K119M', 6)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('Kord-12.7', 1)],
            
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model', 
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 200},
        'reliability': {'mtbf': 60, 'mttr': 1.5}
        },
    'protections': {
        # HE: Esplosivo, HEAT: carica cava, 2HEAT: carica a cava doppia, AP: 'Armour Piercing', APFSDS = AP a energia cinetica 
        'active':       {
                            'model': 'Shtora-300',
                            'threath_countermeasure': ['Laser', 'Infrared', 'TVD', 'Radar']
                        },
        'armor':        {  
                            'front': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'lateral': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'back': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'turret': (True, {'HEAT': 1340, 'APFSDS': 920}), 
                        },
        'reactive':     {
                            'model': 'Kontact5',
                            'increment_thickness': {
                                'front': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'lateral': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'back': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'turret': (True, {'HEAT': 600, 'APFSDS': 250}),      
                            },                                                
                        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 50},
        'reliability': {'mtbf': 90, 'mttr': 1.0},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 45, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.5},
    },
}

T72_data = {
    'constructor': 'UVTZ',    
    'model': 'T-72B',
    'made': 'Russia',
    'start_service': 2020,
    'end_service': None,
    'category': 'Tank', # Main Battle Tank
    'cost': 2.5, # M$
    'range': 400, # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Multifuel 12 Cylinders', 
        'capabilities': {'thrust': 780, 'fuel_efficiency': 0.6, 'type': 'multifuel'}, 
        'reliability': {'mtbf': 30, 'mttr': 8}
    },
    'weapons': {
        'CANNONS': [('2A46M', 38)],
        'MISSILES': [('99K120', 4)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('NSVT-12.7', 1)],
            
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model', 
        'capabilities': {'navigation_accuracy': 0.3, 'communication_range': 130},
        'reliability': {'mtbf': 50, 'mttr': 2.5}
        },
    'protections': {
        # HE: Esplosivo, HEAT: carica cava, 2HEAT: carica a cava doppia, AP: 'Armour Piercing', APFSDS = AP a energia cinetica 
        'active':       {
                            'model': 'Shtora-300',
                            'threath_countermeasure': ['Laser', 'Infrared', 'TVD', 'Radar']
                        },
        'armor':        {  
                            'front': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'lateral': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'back': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'turret': (True, {'HEAT': 1340, 'APFSDS': 920}), 
                        },
        'reactive':     {
                            'model': 'Kontact5',
                            'increment_thickness': {
                                'front': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'lateral': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'back': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'turret': (True, {'HEAT': 600, 'APFSDS': 250}),      
                            },                                                
                        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 50},
        'reliability': {'mtbf': 60, 'mttr': 2.0},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 40, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 50, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.5},
    },
}

T130_data = {
    'constructor': 'UVTZ',    
    'model': 'T130',
    'made': 'Russia',
    'start_service': 2030,
    'end_service': None,
    'category': 'Tank', # Main Battle Tank
    'cost': 4, # M$
    'range': 1200, # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Multifuel 12 Cylinders', 
        'capabilities': {'thrust': 840, 'fuel_efficiency': 0.8, 'type': 'multifuel'}, 
        'reliability': {'mtbf': 40, 'mttr': 5}
    },
    'weapons': {
        'CANNONS': [('2A46M', 42)],
        'MISSILES': [('9K119M', 6)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('Kord-12.7', 1)],
            
    },
    'radar': {
        'model': 'AN/APG-68(V)9',
        'capabilities': {
            'air': (False, {'tracking_range': 160, 'acquisition_range': 70, 'engagement_range': 50, 'multi_target_capacity': 6}),
            'ground': (True, {'tracking_range': 80, 'acquisition_range': 60, 'engagement_range': 20, 'multi_target_capacity': 3}),
            'sea': (False, {'tracking_range': 50, 'acquisition_range': 60, 'engagement_range': 50, 'multi_target_capacity': 3})            
        },
        'reliability': {'mtbf': 60, 'mttr': 4},
        'type': 'pulse-doppler'
            
    },
    'TVD': {
        'model': 'AN/AAQ-28 LITENING',
        'capabilities': {
            'air': (True, {'tracking_range': 100, 'acquisition_range': 120, 'engagement_range': 100, 'multi_target_capacity': 5}),
            'ground': (True, {'tracking_range': 80, 'acquisition_range': 100, 'engagement_range': 80, 'multi_target_capacity': 4}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0})      
        },
        'reliability': {'mtbf': 40, 'mttr': 3},
        'type': 'thermal and optical'
    },
    'communication': {
        'model': 'AN/ARN-118', 
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 200},
        'reliability': {'mtbf': 60, 'mttr': 1.5}
        },
    'protections': {
        # HE: Esplosivo, HEAT: carica cava, 2HEAT: carica a cava doppia, AP: 'Armour Piercing', APFSDS = AP a energia cinetica 
        'active':       {
                            'model': 'Shtora-1',
                            'threath_countermeasure': ['Laser', 'Infrared', 'TVD', 'Radar']
                        },
        'armor':        {  
                            'front': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'lateral': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'back': (True, {'HEAT': 1070, 'APFSDS': 710}),
                            'turret': (True, {'HEAT': 1340, 'APFSDS': 920}), 
                        },
        'reactive':     {
                            'model': 'Kontact5',
                            'increment_thickness': {
                                'front': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'lateral': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'back': (True, {'HEAT': 600, 'APFSDS': 250}),
                                'turret': (True, {'HEAT': 600, 'APFSDS': 250}),      
                            },                                                
                        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 50},
        'reliability': {'mtbf': 90, 'mttr': 1.0},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 45, 'consume': 0.15},
        'max': {'metric': 'metric', 'speed': 70, 'consume': 0.3},
        'off_road': {'metric': 'metric', 'speed': 50, 'consume': 0.4},
    },
}

BMP1_data = {
    'constructor': 'Kurganmashzavod',    
    'model': 'BMP-1',
    'made': 'Russia',
    'start_service': 1966,
    'end_service': None,
    'category': 'Armored', # 
    'cost': 0.06, # M$
    'range': 500, # km
    'roles': ['APC', 'IFV'], # APC: Armored Personnel Carrier, IFV: Infantry Fighting Vehicle
    'engine': {
        'model': 'UTD-20', 
        'capabilities': {'thrust': 300, 'fuel_efficiency': 0.8, 'type': 'diesel'}, 
        'reliability': {'mtbf': 40, 'mttr': 5} # hours
    },
    'weapons': {
        'CANNONS': [('2A28 Grom', 40)], # type, number of roundscapabilities'
        'MISSILES': [('9M14 Malyutka', 4)], # type, number of missiles
        'MACHINE_GUNS': [('PKT-7.62', 1)], #type, units
            #['air', 'ground', 'sea']
    },
    'radar': None,
    'TVD': None,
    'communication': None,
    'protections': {
        # HE: Esplosivo, HEAT: carica cava, 2HEAT: carica a cava doppia, AP: 'Armour Piercing', APFSDS = AP a energia cinetica 
        'active':       None,
        'armor':        {  
                            'front': (True, {'AP': 19}),
                            'lateral': (True, {'AP': 10}),
                            'back': (True, {'AP': 10}),
                            'turret': (True, {'AP': 23}), 
                        },
        'reactive':     {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 50},
        'reliability': {'mtbf': 90, 'mttr': 1.0},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.15},
        'max': {'metric': 'metric', 'speed': 70, 'consume': 0.3},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.4},
    },
}

# ========================================
# MAIN BATTLE TANKS - Nuovi veicoli aggiunti
# ========================================

# ===== T-55 =====
T55_data = {
    'constructor': 'Uralvagonzavod',
    'model': 'T-55',
    'made': 'USSR',
    'start_service': 1958,
    'end_service': 1990,
    'category': 'Tank',
    'cost': 1.5,  # M$
    'range': 500,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'V-55 V-12',
        'capabilities': {'thrust': 580, 'fuel_efficiency': 0.6, 'type': 'diesel'},
        'reliability': {'mtbf': 25, 'mttr': 10}
    },
    'weapons': {
        'CANNONS': [('D-10T2S-100mm', 34)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('DShK-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.2, 'communication_range': 80},
        'reliability': {'mtbf': 40, 'mttr': 3}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 200, 'AP': 200}),
            'lateral': (True, {'AP': 80}),
            'back': (True, {'AP': 45}),
            'turret': (True, {'HEAT': 240, 'AP': 200}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2500, 'fluid_capacity': 40},
        'reliability': {'mtbf': 50, 'mttr': 2.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 40, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 50, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 32, 'consume': 0.7},
    },
}

# ===== Chieftain MK.3 =====
Chieftain_MK3_data = {
    'constructor': 'Leyland Motors',
    'model': 'Chieftain-MK3',
    'made': 'UK',
    'start_service': 1969,
    'end_service': 1995,
    'category': 'Tank',
    'cost': 2.5,  # M$
    'range': 450,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Leyland L60',
        'capabilities': {'thrust': 750, 'fuel_efficiency': 0.65, 'type': 'multifuel'},
        'reliability': {'mtbf': 35, 'mttr': 7}
    },
    'weapons': {
        'CANNONS': [('L11A5-120mm', 64)],
        'MACHINE_GUNS': [('L8A1-7.62', 1), ('L37A1-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.4, 'communication_range': 150},
        'reliability': {'mtbf': 55, 'mttr': 2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 400, 'APFSDS': 300}),
            'lateral': (True, {'AP': 88}),
            'back': (True, {'AP': 38}),
            'turret': (True, {'HEAT': 450, 'APFSDS': 350}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2800, 'fluid_capacity': 45},
        'reliability': {'mtbf': 70, 'mttr': 1.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 40, 'consume': 0.45},
        'max': {'metric': 'metric', 'speed': 48, 'consume': 0.65},
        'off_road': {'metric': 'metric', 'speed': 28, 'consume': 0.8},
    },
}

# ===== Leopard 1A3 =====
Leopard_1A3_data = {
    'constructor': 'Krauss-Maffei',
    'model': 'Leopard-1A3',
    'made': 'Germany',
    'start_service': 1973,
    'end_service': 2000,
    'category': 'Tank',
    'cost': 1.8,  # M$
    'range': 600,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'MTU MB 838 CaM 500',
        'capabilities': {'thrust': 830, 'fuel_efficiency': 0.75, 'type': 'multifuel'},
        'reliability': {'mtbf': 50, 'mttr': 4}
    },
    'weapons': {
        'CANNONS': [('L7A3-105mm', 60)],
        'MACHINE_GUNS': [('MG3-7.62', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 180},
        'reliability': {'mtbf': 65, 'mttr': 1.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 100, 'AP': 70}),
            'lateral': (True, {'AP': 35}),
            'back': (True, {'AP': 25}),
            'turret': (True, {'HEAT': 100, 'AP': 65}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3200, 'fluid_capacity': 50},
        'reliability': {'mtbf': 80, 'mttr': 1.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.6},
    },
}

# ===== M60A3 Patton =====
M60A3_data = {
    'constructor': 'Chrysler Defense',
    'model': 'M60A3-Patton',
    'made': 'USA',
    'start_service': 1978,
    'end_service': 1997,
    'category': 'Tank',
    'cost': 2.5,  # M$
    'range': 480,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Continental AVDS-1790-2C',
        'capabilities': {'thrust': 750, 'fuel_efficiency': 0.68, 'type': 'diesel'},
        'reliability': {'mtbf': 40, 'mttr': 6}
    },
    'weapons': {
        'CANNONS': [('M68-105mm', 63)],
        'MACHINE_GUNS': [('M240-7.62', 1), ('M2HB-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.45, 'communication_range': 160},
        'reliability': {'mtbf': 60, 'mttr': 2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 350, 'APFSDS': 250}),
            'lateral': (True, {'AP': 76}),
            'back': (True, {'AP': 40}),
            'turret': (True, {'HEAT': 400, 'APFSDS': 280}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2900, 'fluid_capacity': 48},
        'reliability': {'mtbf': 75, 'mttr': 1.6},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 40, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 48, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 33, 'consume': 0.75},
    },
}

# ===== Leopard 2A4 =====
Leopard_2A4_data = {
    'constructor': 'Krauss-Maffei Wegmann',
    'model': 'Leopard-2A4',
    'made': 'Germany',
    'start_service': 1985,
    'end_service': None,
    'category': 'Tank',
    'cost': 5.5,  # M$
    'range': 550,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'MTU MB 873 Ka-501',
        'capabilities': {'thrust': 1500, 'fuel_efficiency': 0.85, 'type': 'multifuel'},
        'reliability': {'mtbf': 60, 'mttr': 3}
    },
    'weapons': {
        'CANNONS': [('Rheinmetall-120mm-L44', 42)],
        'MACHINE_GUNS': [('MG3-7.62', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.7, 'communication_range': 220},
        'reliability': {'mtbf': 80, 'mttr': 1}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 600, 'APFSDS': 400}),
            'lateral': (True, {'AP': 200}),
            'back': (True, {'AP': 50}),
            'turret': (True, {'HEAT': 800, 'APFSDS': 600}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3500, 'fluid_capacity': 55},
        'reliability': {'mtbf': 95, 'mttr': 0.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 60, 'consume': 0.3},
        'max': {'metric': 'metric', 'speed': 72, 'consume': 0.45},
        'off_road': {'metric': 'metric', 'speed': 48, 'consume': 0.55},
    },
}

# ===== Leopard 2A5 =====
Leopard_2A5_data = {
    'constructor': 'Krauss-Maffei Wegmann',
    'model': 'Leopard-2A5',
    'made': 'Germany',
    'start_service': 1995,
    'end_service': None,
    'category': 'Tank',
    'cost': 6.5,  # M$
    'range': 550,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'MTU MB 873 Ka-501',
        'capabilities': {'thrust': 1500, 'fuel_efficiency': 0.85, 'type': 'multifuel'},
        'reliability': {'mtbf': 65, 'mttr': 2.5}
    },
    'weapons': {
        'CANNONS': [('Rheinmetall-120mm-L44', 42)],
        'MACHINE_GUNS': [('MG3-7.62', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.75, 'communication_range': 230},
        'reliability': {'mtbf': 85, 'mttr': 0.9}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 700, 'APFSDS': 600}),
            'lateral': (True, {'AP': 250}),
            'back': (True, {'AP': 50}),
            'turret': (True, {'HEAT': 900, 'APFSDS': 800}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3500, 'fluid_capacity': 55},
        'reliability': {'mtbf': 95, 'mttr': 0.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 60, 'consume': 0.3},
        'max': {'metric': 'metric', 'speed': 72, 'consume': 0.45},
        'off_road': {'metric': 'metric', 'speed': 48, 'consume': 0.55},
    },
}

# ===== Leopard 2A6M =====
Leopard_2A6M_data = {
    'constructor': 'Krauss-Maffei Wegmann',
    'model': 'Leopard-2A6M',
    'made': 'Germany',
    'start_service': 2007,
    'end_service': None,
    'category': 'Tank',
    'cost': 9.0,  # M$
    'range': 550,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'MTU MB 873 Ka-501',
        'capabilities': {'thrust': 1500, 'fuel_efficiency': 0.85, 'type': 'multifuel'},
        'reliability': {'mtbf': 70, 'mttr': 2}
    },
    'weapons': {
        'CANNONS': [('Rheinmetall-120mm-L55', 42)],
        'MACHINE_GUNS': [('MG3-7.62', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.8, 'communication_range': 250},
        'reliability': {'mtbf': 90, 'mttr': 0.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 700, 'APFSDS': 600}),
            'lateral': (True, {'HEAT': 300, 'AP': 250}),
            'back': (True, {'AP': 50}),
            'turret': (True, {'HEAT': 900, 'APFSDS': 800}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3500, 'fluid_capacity': 55},
        'reliability': {'mtbf': 100, 'mttr': 0.7},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 58, 'consume': 0.32},
        'max': {'metric': 'metric', 'speed': 72, 'consume': 0.47},
        'off_road': {'metric': 'metric', 'speed': 43, 'consume': 0.6},
    },
}

# ===== M1A2 Abrams =====
M1A2_Abrams_data = {
    'constructor': 'General Dynamics Land Systems',
    'model': 'M1A2-Abrams',
    'made': 'USA',
    'start_service': 1992,
    'end_service': None,
    'category': 'Tank',
    'cost': 8.5,  # M$
    'range': 426,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Honeywell AGT1500C',
        'capabilities': {'thrust': 1500, 'fuel_efficiency': 0.7, 'type': 'turbine'},
        'reliability': {'mtbf': 55, 'mttr': 4}
    },
    'weapons': {
        'CANNONS': [('M256-120mm', 42)],
        'MACHINE_GUNS': [('M240-7.62', 2), ('M2HB-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.85, 'communication_range': 280},
        'reliability': {'mtbf': 95, 'mttr': 0.7}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 800, 'APFSDS': 600}),
            'lateral': (True, {'AP': 150}),
            'back': (True, {'AP': 50}),
            'turret': (True, {'HEAT': 1000, 'APFSDS': 800}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3800, 'fluid_capacity': 60},
        'reliability': {'mtbf': 100, 'mttr': 0.6},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.5},
        'max': {'metric': 'metric', 'speed': 67, 'consume': 0.7},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.85},
    },
}

# ===== Leclerc =====
Leclerc_data = {
    'constructor': 'Nexter Systems',
    'model': 'Leclerc',
    'made': 'France',
    'start_service': 1992,
    'end_service': None,
    'category': 'Tank',
    'cost': 9.0,  # M$
    'range': 550,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'SACM V8X-1500',
        'capabilities': {'thrust': 1500, 'fuel_efficiency': 0.82, 'type': 'diesel'},
        'reliability': {'mtbf': 65, 'mttr': 2.5}
    },
    'weapons': {
        'CANNONS': [('CN120-26-120mm', 40)],
        'MACHINE_GUNS': [('M693-12.7', 1), ('ANF1-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.8, 'communication_range': 260},
        'reliability': {'mtbf': 90, 'mttr': 0.8}
    },
    'protections': {
        'active': {
            'model': 'GALIX',
            'threath_countermeasure': ['Laser', 'Infrared']
        },
        'armor': {
            'front': (True, {'HEAT': 700, 'APFSDS': 600}),
            'lateral': (True, {'AP': 200}),
            'back': (True, {'AP': 50}),
            'turret': (True, {'HEAT': 800, 'APFSDS': 700}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3600, 'fluid_capacity': 58},
        'reliability': {'mtbf': 98, 'mttr': 0.7},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 60, 'consume': 0.28},
        'max': {'metric': 'metric', 'speed': 71, 'consume': 0.42},
        'off_road': {'metric': 'metric', 'speed': 50, 'consume': 0.5},
    },
}

# ===== Challenger II =====
Challenger_II_data = {
    'constructor': 'BAE Systems',
    'model': 'Challenger-II',
    'made': 'UK',
    'start_service': 1998,
    'end_service': None,
    'category': 'Tank',
    'cost': 6.0,  # M$
    'range': 550,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Perkins CV12 Condor',
        'capabilities': {'thrust': 1200, 'fuel_efficiency': 0.75, 'type': 'diesel'},
        'reliability': {'mtbf': 70, 'mttr': 2}
    },
    'weapons': {
        'CANNONS': [('L30A1-120mm', 52)],
        'MACHINE_GUNS': [('L94A1-7.62', 1), ('L37A2-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.75, 'communication_range': 240},
        'reliability': {'mtbf': 88, 'mttr': 0.9}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 900, 'APFSDS': 650}),
            'lateral': (True, {'AP': 200}),
            'back': (True, {'AP': 50}),
            'turret': (True, {'HEAT': 1000, 'APFSDS': 700}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3400, 'fluid_capacity': 54},
        'reliability': {'mtbf': 92, 'mttr': 0.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 59, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.65},
    },
}

# ===== Merkava IV =====
Merkava_IV_data = {
    'constructor': 'Israel Military Industries',
    'model': 'Merkava-IV',
    'made': 'Israel',
    'start_service': 2004,
    'end_service': None,
    'category': 'Tank',
    'cost': 6.5,  # M$
    'range': 500,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'MTU MT883 Ka-501',
        'capabilities': {'thrust': 1500, 'fuel_efficiency': 0.78, 'type': 'diesel'},
        'reliability': {'mtbf': 68, 'mttr': 2.2}
    },
    'weapons': {
        'CANNONS': [('MG251-120mm', 48)],
        'MACHINE_GUNS': [('M2HB-12.7', 1), ('FN MAG-7.62', 3)],
        'MORTARS': [('M933-60mm', 12)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.82, 'communication_range': 270},
        'reliability': {'mtbf': 92, 'mttr': 0.75}
    },
    'protections': {
        'active': {
            'model': 'Trophy APS',
            'threath_countermeasure': ['ATGM', 'RPG', 'Tank rounds']
        },
        'armor': {
            'front': (True, {'HEAT': 900, 'APFSDS': 700}),
            'lateral': (True, {'HEAT': 600, 'AP': 300}),
            'back': (True, {'AP': 100}),
            'turret': (True, {'HEAT': 950, 'APFSDS': 750}),
        },
        'reactive': {
            'model': 'Modular ERA',
            'increment_thickness': {
                'front': (True, {'HEAT': 300, 'APFSDS': 150}),
                'lateral': (True, {'HEAT': 300, 'APFSDS': 150}),
                'back': (False, {}),
                'turret': (True, {'HEAT': 200, 'APFSDS': 100}),
            },
        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3600, 'fluid_capacity': 56},
        'reliability': {'mtbf': 96, 'mttr': 0.72},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.32},
        'max': {'metric': 'metric', 'speed': 64, 'consume': 0.48},
        'off_road': {'metric': 'metric', 'speed': 50, 'consume': 0.58},
    },
}

# ===== Type 59 =====
Type_59_data = {
    'constructor': 'Norinco',
    'model': 'Type-59',
    'made': 'China',
    'start_service': 1958,
    'end_service': 1985,
    'category': 'Tank',
    'cost': 0.8,  # M$
    'range': 500,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'Model 12150L V-12',
        'capabilities': {'thrust': 520, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 22, 'mttr': 12}
    },
    'weapons': {
        'CANNONS': [('Type-59-100mm', 34)],
        'MACHINE_GUNS': [('Type-59T-7.62', 1), ('DShK-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.15, 'communication_range': 60},
        'reliability': {'mtbf': 35, 'mttr': 4}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 200}),
            'lateral': (True, {'AP': 80}),
            'back': (True, {'AP': 45}),
            'turret': (True, {'AP': 200}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2400, 'fluid_capacity': 38},
        'reliability': {'mtbf': 45, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 40, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 50, 'consume': 0.62},
        'off_road': {'metric': 'metric', 'speed': 32, 'consume': 0.75},
    },
}

# ===== T-80U =====
T80U_data = {
    'constructor': 'Omsktransmash',
    'model': 'T-80U',
    'made': 'USSR',
    'start_service': 1985,
    'end_service': None,
    'category': 'Tank',
    'cost': 4.0,  # M$
    'range': 335,  # km (500 with external tanks)
    'roles': ['Tank'],
    'engine': {
        'model': 'GTD-1250 gas turbine',
        'capabilities': {'thrust': 1250, 'fuel_efficiency': 0.55, 'type': 'turbine'},
        'reliability': {'mtbf': 35, 'mttr': 6}
    },
    'weapons': {
        'CANNONS': [('2A46M-125mm', 45)],
        'MISSILES': [('9M119-Refleks', 6)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('NSVT-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 190},
        'reliability': {'mtbf': 65, 'mttr': 1.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'HEAT': 500, 'APFSDS': 400}),
            'lateral': (True, {'AP': 80}),
            'back': (True, {'AP': 45}),
            'turret': (True, {'HEAT': 600, 'APFSDS': 450}),
        },
        'reactive': {
            'model': 'Kontakt-5',
            'increment_thickness': {
                'front': (True, {'HEAT': 400, 'APFSDS': 200}),
                'lateral': (True, {'HEAT': 300, 'APFSDS': 150}),
                'back': (True, {'HEAT': 200, 'APFSDS': 100}),
                'turret': (True, {'HEAT': 400, 'APFSDS': 200}),
            },
        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3200, 'fluid_capacity': 52},
        'reliability': {'mtbf': 85, 'mttr': 1.1},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 60, 'consume': 0.55},
        'max': {'metric': 'metric', 'speed': 70, 'consume': 0.75},
        'off_road': {'metric': 'metric', 'speed': 48, 'consume': 0.85},
    },
}

# ===== T-90 (base) =====
T90_base_data = {
    'constructor': 'Uralvagonzavod',
    'model': 'T-90',
    'made': 'Russia',
    'start_service': 1992,
    'end_service': None,
    'category': 'Tank',
    'cost': 4.5,  # M$
    'range': 550,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'V-84MS',
        'capabilities': {'thrust': 840, 'fuel_efficiency': 0.78, 'type': 'diesel'},
        'reliability': {'mtbf': 42, 'mttr': 5}
    },
    'weapons': {
        'CANNONS': [('2A46M-125mm', 43)],
        'MISSILES': [('9M119-Refleks', 6)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('NSVT-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.52, 'communication_range': 200},
        'reliability': {'mtbf': 68, 'mttr': 1.6}
    },
    'protections': {
        'active': {
            'model': 'Shtora-1',
            'threath_countermeasure': ['Laser', 'ATGM']
        },
        'armor': {
            'front': (True, {'HEAT': 550, 'APFSDS': 450}),
            'lateral': (True, {'AP': 85}),
            'back': (True, {'AP': 45}),
            'turret': (True, {'HEAT': 700, 'APFSDS': 550}),
        },
        'reactive': {
            'model': 'Kontakt-5',
            'increment_thickness': {
                'front': (True, {'HEAT': 450, 'APFSDS': 220}),
                'lateral': (True, {'HEAT': 350, 'APFSDS': 170}),
                'back': (True, {'HEAT': 250, 'APFSDS': 120}),
                'turret': (True, {'HEAT': 450, 'APFSDS': 220}),
            },
        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3100, 'fluid_capacity': 51},
        'reliability': {'mtbf': 88, 'mttr': 1.0},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 63, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 43, 'consume': 0.62},
    },
}

# ===== T-72B3 =====
T72B3_data = {
    'constructor': 'Uralvagonzavod',
    'model': 'T-72B3',
    'made': 'Russia',
    'start_service': 2013,
    'end_service': None,
    'category': 'Tank',
    'cost': 1.8,  # M$ (modernization cost)
    'range': 500,  # km
    'roles': ['Tank'],
    'engine': {
        'model': 'V-84-1',
        'capabilities': {'thrust': 840, 'fuel_efficiency': 0.76, 'type': 'diesel'},
        'reliability': {'mtbf': 38, 'mttr': 6}
    },
    'weapons': {
        'CANNONS': [('2A46M5-125mm', 45)],
        'MISSILES': [('9M119M-Refleks-M', 6)],
        'MACHINE_GUNS': [('PKT-7.62', 1), ('Kord-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.6, 'communication_range': 210},
        'reliability': {'mtbf': 72, 'mttr': 1.4}
    },
    'protections': {
        'active': {
            'model': 'Shtora-1',
            'threath_countermeasure': ['Laser', 'ATGM']
        },
        'armor': {
            'front': (True, {'HEAT': 500, 'APFSDS': 400}),
            'lateral': (True, {'AP': 80}),
            'back': (True, {'AP': 40}),
            'turret': (True, {'HEAT': 600, 'APFSDS': 450}),
        },
        'reactive': {
            'model': 'Kontakt-5',
            'increment_thickness': {
                'front': (True, {'HEAT': 400, 'APFSDS': 200}),
                'lateral': (True, {'HEAT': 300, 'APFSDS': 150}),
                'back': (True, {'HEAT': 200, 'APFSDS': 100}),
                'turret': (True, {'HEAT': 400, 'APFSDS': 200}),
            },
        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 50},
        'reliability': {'mtbf': 82, 'mttr': 1.15},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 52, 'consume': 0.36},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.54},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.65},
    },
}

# ===== ZTZ-96B =====
ZTZ_96B_data = {
    'constructor': 'Norinco',
    'model': 'ZTZ-96B',
    'made': 'China',
    'start_service': 2017,
    'end_service': None,
    'category': 'Tank',
    'cost': 2.8,  # M$
    'range': 400,  # km
    'roles': ['Tank'],
    'engine': {
        'model': '12150ZL',
        'capabilities': {'thrust': 1000, 'fuel_efficiency': 0.72, 'type': 'diesel'},
        'reliability': {'mtbf': 45, 'mttr': 4.5}
    },
    'weapons': {
        'CANNONS': [('ZPT-98-125mm', 42)],
        'MACHINE_GUNS': [('Type-86-7.62', 1), ('QJC88-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.65, 'communication_range': 215},
        'reliability': {'mtbf': 75, 'mttr': 1.3}
    },
    'protections': {
        'active': {
            'model': 'GL-5 APS',
            'threath_countermeasure': ['Laser', 'Infrared']
        },
        'armor': {
            'front': (True, {'HEAT': 600, 'APFSDS': 500}),
            'lateral': (True, {'AP': 80}),
            'back': (True, {'AP': 45}),
            'turret': (True, {'HEAT': 650, 'APFSDS': 500}),
        },
        'reactive': {
            'model': 'FY-4 ERA',
            'increment_thickness': {
                'front': (True, {'HEAT': 350, 'APFSDS': 180}),
                'lateral': (True, {'HEAT': 300, 'APFSDS': 150}),
                'back': (True, {'HEAT': 200, 'APFSDS': 100}),
                'turret': (True, {'HEAT': 350, 'APFSDS': 180}),
            },
        },
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3100, 'fluid_capacity': 52},
        'reliability': {'mtbf': 80, 'mttr': 1.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 57, 'consume': 0.56},
        'off_road': {'metric': 'metric', 'speed': 38, 'consume': 0.68},
    },
}


# ========================================
# NUOVI VEICOLI AGGIUNTI
# ========================================

# ========================================
# INFANTRY FIGHTING VEHICLES (IFV)
# Da aggiungere a Vehicle_Data.py
# ========================================

# ===== Marder =====
Marder_data = {
    'constructor': 'Rheinmetall Landsysteme',
    'model': 'Marder',
    'made': 'Germany',
    'start_service': 1971,
    'end_service': None,
    'category': 'Armored',
    'cost': 3.5,  # M$
    'range': 520,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'MTU MB 833 Ea-500',
        'capabilities': {'thrust': 600, 'fuel_efficiency': 0.75, 'type': 'diesel'},
        'reliability': {'mtbf': 55, 'mttr': 4}
    },
    'weapons': {
        'CANNONS': [('MK-20-Rh-202-20mm', 1250)],
        'MACHINE_GUNS': [('MG3-7.62', 2)],
        'MISSILES': [('MILAN', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.6, 'communication_range': 180},
        'reliability': {'mtbf': 65, 'mttr': 1.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 35}),
            'lateral': (True, {'AP': 30}),
            'back': (True, {'AP': 20}),
            'turret': (True, {'AP': 35}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2900, 'fluid_capacity': 46},
        'reliability': {'mtbf': 75, 'mttr': 1.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.32},
        'max': {'metric': 'metric', 'speed': 75, 'consume': 0.45},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.55},
    },
}

# ===== BMP-2 =====
BMP2_data = {
    'constructor': 'Kurganmashzavod',
    'model': 'BMP-2',
    'made': 'USSR',
    'start_service': 1980,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.8,  # M$
    'range': 600,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'UTD-20',
        'capabilities': {'thrust': 300, 'fuel_efficiency': 0.72, 'type': 'diesel'},
        'reliability': {'mtbf': 45, 'mttr': 5}
    },
    'weapons': {
        'CANNONS': [('2A42-30mm', 500)],
        'MACHINE_GUNS': [('PKT-7.62', 1)],
        'MISSILES': [('9M113-Konkurs', 4)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.4, 'communication_range': 140},
        'reliability': {'mtbf': 50, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 33}),
            'lateral': (True, {'AP': 25}),
            'back': (True, {'AP': 18}),
            'turret': (True, {'AP': 33}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2700, 'fluid_capacity': 42},
        'reliability': {'mtbf': 65, 'mttr': 2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.6},
    },
}

# ===== BMD-1 =====
BMD1_data = {
    'constructor': 'Volgograd Tractor Plant',
    'model': 'BMD-1',
    'made': 'USSR',
    'start_service': 1969,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.2,  # M$
    'range': 600,  # km
    'roles': ['IFV', 'Airborne'],
    'engine': {
        'model': '5D-20',
        'capabilities': {'thrust': 240, 'fuel_efficiency': 0.68, 'type': 'diesel'},
        'reliability': {'mtbf': 38, 'mttr': 6}
    },
    'weapons': {
        'CANNONS': [('2A28-Grom-73mm', 40)],
        'MACHINE_GUNS': [('PKT-7.62', 3)],
        'MISSILES': [('9M14-Malyutka', 3)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 120},
        'reliability': {'mtbf': 45, 'mttr': 3}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 23}),
            'lateral': (True, {'AP': 15}),
            'back': (True, {'AP': 12}),
            'turret': (True, {'AP': 23}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2500, 'fluid_capacity': 38},
        'reliability': {'mtbf': 55, 'mttr': 2.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 60, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 70, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 38, 'consume': 0.62},
    },
}

# ===== M-2 Bradley =====
M2_Bradley_data = {
    'constructor': 'BAE Systems',
    'model': 'M2-Bradley',
    'made': 'USA',
    'start_service': 1981,
    'end_service': None,
    'category': 'Armored',
    'cost': 3.8,  # M$
    'range': 400,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'Cummins VTA-903T',
        'capabilities': {'thrust': 600, 'fuel_efficiency': 0.7, 'type': 'diesel'},
        'reliability': {'mtbf': 52, 'mttr': 4.5}
    },
    'weapons': {
        'CANNONS': [('M242-Bushmaster-25mm', 900)],
        'MACHINE_GUNS': [('M240C-7.62', 1)],
        'MISSILES': [('BGM-71-TOW', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.7, 'communication_range': 200},
        'reliability': {'mtbf': 75, 'mttr': 1.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 30}),
            'lateral': (True, {'AP': 25}),
            'back': (True, {'AP': 15}),
            'turret': (True, {'AP': 30}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 48},
        'reliability': {'mtbf': 80, 'mttr': 1.3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 56, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 66, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.6},
    },
}

# ===== BMP-3 =====
BMP3_data = {
    'constructor': 'Kurganmashzavod',
    'model': 'BMP-3',
    'made': 'USSR',
    'start_service': 1987,
    'end_service': None,
    'category': 'Armored',
    'cost': 2.5,  # M$
    'range': 600,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'UTD-29',
        'capabilities': {'thrust': 500, 'fuel_efficiency': 0.76, 'type': 'diesel'},
        'reliability': {'mtbf': 48, 'mttr': 4.5}
    },
    'weapons': {
        'CANNONS': [('2A70-100mm', 40), ('2A72-30mm', 500)],
        'MACHINE_GUNS': [('PKT-7.62', 3)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 160},
        'reliability': {'mtbf': 58, 'mttr': 2.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 43}),
            'lateral': (True, {'AP': 25}),
            'back': (True, {'AP': 18}),
            'turret': (True, {'AP': 43}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2850, 'fluid_capacity': 45},
        'reliability': {'mtbf': 70, 'mttr': 1.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 60, 'consume': 0.33},
        'max': {'metric': 'metric', 'speed': 70, 'consume': 0.48},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.58},
    },
}

# ===== Warrior =====
Warrior_data = {
    'constructor': 'BAE Systems',
    'model': 'Warrior',
    'made': 'UK',
    'start_service': 1987,
    'end_service': None,
    'category': 'Armored',
    'cost': 3.7,  # M$
    'range': 660,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'Perkins CV8 TCA Condor',
        'capabilities': {'thrust': 550, 'fuel_efficiency': 0.73, 'type': 'diesel'},
        'reliability': {'mtbf': 53, 'mttr': 4}
    },
    'weapons': {
        'CANNONS': [('L21A1-RARDEN-30mm', 230)],
        'MACHINE_GUNS': [('L94A1-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.65, 'communication_range': 190},
        'reliability': {'mtbf': 72, 'mttr': 1.6}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 80}),
            'lateral': (True, {'AP': 30}),
            'back': (True, {'AP': 20}),
            'turret': (True, {'AP': 80}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2950, 'fluid_capacity': 47},
        'reliability': {'mtbf': 78, 'mttr': 1.4},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.32},
        'max': {'metric': 'metric', 'speed': 75, 'consume': 0.46},
        'off_road': {'metric': 'metric', 'speed': 43, 'consume': 0.56},
    },
}

# ===== LAV-25 =====
LAV25_data = {
    'constructor': 'General Dynamics Land Systems',
    'model': 'LAV-25',
    'made': 'USA',
    'start_service': 1983,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.8,  # M$
    'range': 660,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'Detroit Diesel 6V53T',
        'capabilities': {'thrust': 275, 'fuel_efficiency': 0.78, 'type': 'diesel'},
        'reliability': {'mtbf': 58, 'mttr': 3.5}
    },
    'weapons': {
        'CANNONS': [('M242-Bushmaster-25mm', 630)],
        'MACHINE_GUNS': [('M240-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.62, 'communication_range': 175},
        'reliability': {'mtbf': 68, 'mttr': 1.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 16}),
            'lateral': (True, {'AP': 10}),
            'back': (True, {'AP': 10}),
            'turret': (True, {'AP': 16}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2650, 'fluid_capacity': 40},
        'reliability': {'mtbf': 72, 'mttr': 1.6},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 85, 'consume': 0.28},
        'max': {'metric': 'metric', 'speed': 100, 'consume': 0.4},
        'off_road': {'metric': 'metric', 'speed': 55, 'consume': 0.5},
    },
}

# ===== M1126 Stryker ICV =====
M1126_Stryker_data = {
    'constructor': 'General Dynamics Land Systems',
    'model': 'M1126-Stryker-ICV',
    'made': 'USA',
    'start_service': 2002,
    'end_service': None,
    'category': 'Armored',
    'cost': 5.0,  # M$
    'range': 500,  # km
    'roles': ['IFV', 'APC'],
    'engine': {
        'model': 'Caterpillar C7',
        'capabilities': {'thrust': 350, 'fuel_efficiency': 0.75, 'type': 'diesel'},
        'reliability': {'mtbf': 62, 'mttr': 3}
    },
    'weapons': {
        'MACHINE_GUNS': [('M2HB-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.75, 'communication_range': 210},
        'reliability': {'mtbf': 80, 'mttr': 1.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 14}),
            'lateral': (True, {'AP': 12}),
            'back': (True, {'AP': 10}),
            'turret': (True, {'AP': 14}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2750, 'fluid_capacity': 43},
        'reliability': {'mtbf': 85, 'mttr': 1.1},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 85, 'consume': 0.3},
        'max': {'metric': 'metric', 'speed': 100, 'consume': 0.42},
        'off_road': {'metric': 'metric', 'speed': 60, 'consume': 0.52},
    },
}

# ===== BTR-82A =====
BTR82A_data = {
    'constructor': 'Military Industrial Company',
    'model': 'BTR-82A',
    'made': 'Russia',
    'start_service': 2012,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.7,  # M$
    'range': 600,  # km
    'roles': ['IFV', 'APC'],
    'engine': {
        'model': 'KAMAZ-7403 V8',
        'capabilities': {'thrust': 300, 'fuel_efficiency': 0.72, 'type': 'diesel'},
        'reliability': {'mtbf': 48, 'mttr': 4.2}
    },
    'weapons': {
        'CANNONS': [('2A72-30mm', 500)],
        'MACHINE_GUNS': [('PKTM-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.58, 'communication_range': 170},
        'reliability': {'mtbf': 65, 'mttr': 1.9}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 13}),
            'lateral': (True, {'AP': 9}),
            'back': (True, {'AP': 7}),
            'turret': (True, {'AP': 13}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2650, 'fluid_capacity': 41},
        'reliability': {'mtbf': 68, 'mttr': 1.7},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 85, 'consume': 0.3},
        'max': {'metric': 'metric', 'speed': 100, 'consume': 0.43},
        'off_road': {'metric': 'metric', 'speed': 55, 'consume': 0.53},
    },
}

# ===== ZBD-04A =====
ZBD04A_data = {
    'constructor': 'Norinco',
    'model': 'ZBD-04A',
    'made': 'China',
    'start_service': 2004,
    'end_service': None,
    'category': 'Armored',
    'cost': 3.2,  # M$
    'range': 500,  # km
    'roles': ['IFV'],
    'engine': {
        'model': 'Deutz BF8L 413FC',
        'capabilities': {'thrust': 590, 'fuel_efficiency': 0.74, 'type': 'diesel'},
        'reliability': {'mtbf': 50, 'mttr': 4}
    },
    'weapons': {
        'CANNONS': [('ZPT-99-30mm', 500)],
        'MACHINE_GUNS': [('Type-86-7.62', 1)],
        'MISSILES': [('HJ-73C', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.63, 'communication_range': 185},
        'reliability': {'mtbf': 70, 'mttr': 1.7}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 30}),
            'lateral': (True, {'AP': 20}),
            'back': (True, {'AP': 15}),
            'turret': (True, {'AP': 35}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2850, 'fluid_capacity': 46},
        'reliability': {'mtbf': 75, 'mttr': 1.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.31},
        'max': {'metric': 'metric', 'speed': 75, 'consume': 0.45},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.55},
    },
}
# Nuovi APC (Armored Personnel Carrier) da aggiungere a Vehicle_Data.py
# Generato automaticamente per il progetto Warfare-Model

# ===== Sd.Kfz 251 Halftrack =====
SdKfz_251_data = {
    'constructor': 'Hanomag',
    'model': 'Sd.Kfz-251',
    'made': 'Germany',
    'start_service': 1939,
    'end_service': 1945,
    'category': 'Armored',
    'cost': 0.8,  # M$
    'range': 300,  # km
    'roles': ['APC'],
    'engine': {
        'model': 'Maybach HL 42 TUKRM',
        'capabilities': {'thrust': 100, 'fuel_efficiency': 0.45, 'type': 'gasoline'},
        'reliability': {'mtbf': 15, 'mttr': 8}
    },
    'weapons': {
        'MACHINE_GUNS': [('MG34-7.92', 2)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.1, 'communication_range': 30},
        'reliability': {'mtbf': 20, 'mttr': 5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 14.5}),
            'lateral': (True, {'AP': 8}),
            'back': (True, {'AP': 8}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 1500, 'fluid_capacity': 25},
        'reliability': {'mtbf': 25, 'mttr': 4},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 45, 'consume': 0.5},
        'max': {'metric': 'metric', 'speed': 52, 'consume': 0.7},
        'off_road': {'metric': 'metric', 'speed': 25, 'consume': 0.9},
    },
}

# ===== MTLB =====
MTLB_data = {
    'constructor': 'Kharkiv Tractor Plant',
    'model': 'MT-LB',
    'made': 'USSR',
    'start_service': 1966,
    'end_service': None,
    'category': 'Armored',
    'cost': 0.6,  # M$
    'range': 500,  # km
    'roles': ['APC', 'Transport'],
    'engine': {
        'model': 'YaMZ-238V',
        'capabilities': {'thrust': 240, 'fuel_efficiency': 0.55, 'type': 'diesel'},
        'reliability': {'mtbf': 30, 'mttr': 6}
    },
    'weapons': {
        'MACHINE_GUNS': [('PKT-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.25, 'communication_range': 50},
        'reliability': {'mtbf': 35, 'mttr': 4}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 10}),
            'lateral': (True, {'AP': 7}),
            'back': (True, {'AP': 7}),
            'turret': (True, {'AP': 7}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2000, 'fluid_capacity': 30},
        'reliability': {'mtbf': 40, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 61, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.65},
    },
}

# ===== M2A1 Halftrack =====
M2A1_Halftrack_data = {
    'constructor': 'White Motor Company',
    'model': 'M2A1-Halftrack',
    'made': 'USA',
    'start_service': 1940,
    'end_service': 1960,
    'category': 'Armored',
    'cost': 0.7,  # M$
    'range': 280,  # km
    'roles': ['APC'],
    'engine': {
        'model': 'White 160AX',
        'capabilities': {'thrust': 147, 'fuel_efficiency': 0.42, 'type': 'gasoline'},
        'reliability': {'mtbf': 18, 'mttr': 7}
    },
    'weapons': {
        'MACHINE_GUNS': [('M2HB-12.7', 1), ('M1919-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.15, 'communication_range': 35},
        'reliability': {'mtbf': 22, 'mttr': 5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 12.7}),
            'lateral': (True, {'AP': 6.35}),
            'back': (True, {'AP': 6.35}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 1600, 'fluid_capacity': 22},
        'reliability': {'mtbf': 28, 'mttr': 4},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 40, 'consume': 0.55},
        'max': {'metric': 'metric', 'speed': 48, 'consume': 0.75},
        'off_road': {'metric': 'metric', 'speed': 24, 'consume': 0.95},
    },
}

# ===== M-113 =====
M113_data = {
    'constructor': 'FMC Corporation',
    'model': 'M-113',
    'made': 'USA',
    'start_service': 1960,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.2,  # M$
    'range': 480,  # km
    'roles': ['APC'],
    'engine': {
        'model': 'Detroit Diesel 6V53',
        'capabilities': {'thrust': 275, 'fuel_efficiency': 0.6, 'type': 'diesel'},
        'reliability': {'mtbf': 45, 'mttr': 5}
    },
    'weapons': {
        'MACHINE_GUNS': [('M2HB-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.3, 'communication_range': 100},
        'reliability': {'mtbf': 50, 'mttr': 3}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 38}),
            'lateral': (True, {'AP': 32}),
            'back': (True, {'AP': 28}),
            'turret': (True, {'AP': 25}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2200, 'fluid_capacity': 35},
        'reliability': {'mtbf': 55, 'mttr': 2.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 67, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.68},
    },
}

# ===== AAV7 Amphibious =====
AAV7_data = {
    'constructor': 'FMC Corporation',
    'model': 'AAV7',
    'made': 'USA',
    'start_service': 1972,
    'end_service': None,
    'category': 'Armored',
    'cost': 2.0,  # M$
    'range': 480,  # km
    'roles': ['APC', 'Amphibious'],
    'engine': {
        'model': 'Cummins VT400',
        'capabilities': {'thrust': 400, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 38, 'mttr': 6}
    },
    'weapons': {
        'MACHINE_GUNS': [('M2HB-12.7', 1), ('M240-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 120},
        'reliability': {'mtbf': 48, 'mttr': 3.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 45}),
            'lateral': (True, {'AP': 35}),
            'back': (True, {'AP': 25}),
            'turret': (True, {'AP': 30}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2400, 'fluid_capacity': 40},
        'reliability': {'mtbf': 50, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 64, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 32, 'consume': 0.75},
    },
}

# ===== TPz Fuchs =====
TPz_Fuchs_data = {
    'constructor': 'Thyssen-Henschel',
    'model': 'TPz-Fuchs',
    'made': 'Germany',
    'start_service': 1979,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.5,  # M$
    'range': 800,  # km
    'roles': ['APC', 'NBC'],
    'engine': {
        'model': 'Mercedes-Benz OM 402A',
        'capabilities': {'thrust': 320, 'fuel_efficiency': 0.72, 'type': 'diesel'},
        'reliability': {'mtbf': 60, 'mttr': 4}
    },
    'weapons': {
        'MACHINE_GUNS': [('MG3-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.45, 'communication_range': 140},
        'reliability': {'mtbf': 65, 'mttr': 2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 30}),
            'lateral': (True, {'AP': 15}),
            'back': (True, {'AP': 15}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2600, 'fluid_capacity': 38},
        'reliability': {'mtbf': 70, 'mttr': 2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 85, 'consume': 0.32},
        'max': {'metric': 'metric', 'speed': 105, 'consume': 0.48},
        'off_road': {'metric': 'metric', 'speed': 50, 'consume': 0.6},
    },
}

# ===== BTR-80 =====
BTR80_data = {
    'constructor': 'GAZ',
    'model': 'BTR-80',
    'made': 'USSR',
    'start_service': 1986,
    'end_service': None,
    'category': 'Armored',
    'cost': 1.0,  # M$
    'range': 600,  # km
    'roles': ['APC'],
    'engine': {
        'model': 'KamAZ-7403',
        'capabilities': {'thrust': 260, 'fuel_efficiency': 0.62, 'type': 'diesel'},
        'reliability': {'mtbf': 42, 'mttr': 5}
    },
    'weapons': {
        'MACHINE_GUNS': [('KPVT-14.5', 1), ('PKT-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.4, 'communication_range': 130},
        'reliability': {'mtbf': 55, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 10}),
            'lateral': (True, {'AP': 7}),
            'back': (True, {'AP': 7}),
            'turret': (True, {'AP': 9}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2300, 'fluid_capacity': 34},
        'reliability': {'mtbf': 52, 'mttr': 2.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 70, 'consume': 0.36},
        'max': {'metric': 'metric', 'speed': 80, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.62},
    },
}

# ===== BTR-RD =====
BTR_RD_data = {
    'constructor': 'GAZ',
    'model': 'BTR-RD',
    'made': 'USSR',
    'start_service': 1984,
    'end_service': None,
    'category': 'Armored',
    'cost': 0.9,  # M$
    'range': 580,  # km
    'roles': ['APC', 'Airborne'],
    'engine': {
        'model': 'GAZ-49B',
        'capabilities': {'thrust': 240, 'fuel_efficiency': 0.58, 'type': 'gasoline'},
        'reliability': {'mtbf': 38, 'mttr': 6}
    },
    'weapons': {
        'MACHINE_GUNS': [('KPVT-14.5', 1), ('PKT-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 100},
        'reliability': {'mtbf': 45, 'mttr': 3.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 8}),
            'lateral': (True, {'AP': 5}),
            'back': (True, {'AP': 5}),
            'turret': (True, {'AP': 7}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2100, 'fluid_capacity': 30},
        'reliability': {'mtbf': 48, 'mttr': 3.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 75, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.68},
    },
}
# Nuovi veicoli Artillery (SPH, MLRS, SPM) da aggiungere a Vehicle_Data.py
# Generato automaticamente dalle ricerche degli agent

# ===== BM-21 Grad 122mm MLRS =====
BM21_Grad_data = {
    'constructor': 'Splav State Research',
    'model': 'BM-21-Grad',
    'made': 'USSR',
    'start_service': 1963,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 1.5,  # M$
    'range': 450,  # km
    'roles': ['MLRS'],
    'engine': {
        'model': 'ZIL-375 V8',
        'capabilities': {'thrust': 180, 'fuel_efficiency': 0.4, 'type': 'gasoline'},
        'reliability': {'mtbf': 35, 'mttr': 6}
    },
    'weapons': {
        'ARTILLERY': [('122mm-Grad-Rocket', 40)],
        'MACHINE_GUNS': [('PKM-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.3, 'communication_range': 80},
        'reliability': {'mtbf': 40, 'mttr': 4}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 8}),
            'lateral': (True, {'AP': 5}),
            'back': (True, {'AP': 5}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2000, 'fluid_capacity': 30},
        'reliability': {'mtbf': 45, 'mttr': 3.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.5},
        'max': {'metric': 'metric', 'speed': 75, 'consume': 0.7},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.85},
    },
}

# ===== 2S3 Akatsia 152mm SPH =====
S2S3_Akatsia_data = {
    'constructor': 'Uraltransmash',
    'model': '2S3-Akatsia',
    'made': 'USSR',
    'start_service': 1971,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 2.5,  # M$
    'range': 500,  # km
    'roles': ['SPH'],
    'engine': {
        'model': 'YaMZ-238V V8',
        'capabilities': {'thrust': 520, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 42, 'mttr': 5}
    },
    'weapons': {
        'ARTILLERY': [('2A33-152mm', 46)],
        'MACHINE_GUNS': [('PKT-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 100},
        'reliability': {'mtbf': 50, 'mttr': 3}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 20}),
            'lateral': (True, {'AP': 15}),
            'back': (True, {'AP': 15}),
            'turret': (True, {'AP': 15}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2400, 'fluid_capacity': 38},
        'reliability': {'mtbf': 55, 'mttr': 2.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.58},
        'off_road': {'metric': 'metric', 'speed': 30, 'consume': 0.75},
    },
}

# ===== 2S1 Gvozdika 122mm SPH =====
S2S1_Gvozdika_data = {
    'constructor': 'Uraltransmash',
    'model': '2S1-Gvozdika',
    'made': 'USSR',
    'start_service': 1972,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 1.8,  # M$
    'range': 500,  # km
    'roles': ['SPH'],
    'engine': {
        'model': 'YaMZ-238V V8',
        'capabilities': {'thrust': 300, 'fuel_efficiency': 0.55, 'type': 'diesel'},
        'reliability': {'mtbf': 40, 'mttr': 5}
    },
    'weapons': {
        'ARTILLERY': [('2A31-122mm', 40)],
        'MACHINE_GUNS': [('PKT-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.32, 'communication_range': 95},
        'reliability': {'mtbf': 48, 'mttr': 3.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 20}),
            'lateral': (True, {'AP': 15}),
            'back': (True, {'AP': 15}),
            'turret': (True, {'AP': 15}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2300, 'fluid_capacity': 35},
        'reliability': {'mtbf': 52, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.55},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.7},
    },
}

# ===== BM-27 Uragan 220mm MLRS =====
BM27_Uragan_data = {
    'constructor': 'Splav State Research',
    'model': 'BM-27-Uragan',
    'made': 'USSR',
    'start_service': 1975,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 3.5,  # M$
    'range': 500,  # km
    'roles': ['MLRS'],
    'engine': {
        'model': 'ZIL-375 V8',
        'capabilities': {'thrust': 180, 'fuel_efficiency': 0.42, 'type': 'gasoline'},
        'reliability': {'mtbf': 32, 'mttr': 7}
    },
    'weapons': {
        'ARTILLERY': [('220mm-Uragan-Rocket', 16)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.33, 'communication_range': 85},
        'reliability': {'mtbf': 42, 'mttr': 4}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 10}),
            'lateral': (True, {'AP': 5}),
            'back': (True, {'AP': 5}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2100, 'fluid_capacity': 32},
        'reliability': {'mtbf': 48, 'mttr': 3.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.52},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.7},
        'off_road': {'metric': 'metric', 'speed': 30, 'consume': 0.88},
    },
}

# ===== Dana vz77 152mm SPH =====
Dana_vz77_data = {
    'constructor': 'Konštrukta Trenčín',
    'model': 'Dana-vz77',
    'made': 'Czechoslovakia',
    'start_service': 1980,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 4.5,  # M$
    'range': 600,  # km
    'roles': ['SPH'],
    'engine': {
        'model': 'Tatra T3-930-51 V12',
        'capabilities': {'thrust': 345, 'fuel_efficiency': 0.62, 'type': 'diesel'},
        'reliability': {'mtbf': 55, 'mttr': 4}
    },
    'weapons': {
        'ARTILLERY': [('Dana-152mm', 60)],
        'MACHINE_GUNS': [('DShK-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.45, 'communication_range': 130},
        'reliability': {'mtbf': 60, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 12.7}),
            'lateral': (True, {'AP': 8}),
            'back': (True, {'AP': 8}),
            'turret': (True, {'AP': 12}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2700, 'fluid_capacity': 42},
        'reliability': {'mtbf': 65, 'mttr': 2.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 70, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 80, 'consume': 0.48},
        'off_road': {'metric': 'metric', 'speed': 45, 'consume': 0.62},
    },
}

# ===== 2S9 Nona 120mm SPM =====
S2S9_Nona_data = {
    'constructor': 'Uraltransmash',
    'model': '2S9-Nona',
    'made': 'USSR',
    'start_service': 1981,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 1.2,  # M$
    'range': 500,  # km
    'roles': ['SPM', 'Airborne'],
    'engine': {
        'model': 'UTD-20',
        'capabilities': {'thrust': 240, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 38, 'mttr': 6}
    },
    'weapons': {
        'ARTILLERY': [('2A51-120mm', 22)],
        'MACHINE_GUNS': [('PKT-7.62', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 90},
        'reliability': {'mtbf': 45, 'mttr': 3.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 15}),
            'lateral': (True, {'AP': 10}),
            'back': (True, {'AP': 10}),
            'turret': (True, {'AP': 10}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2200, 'fluid_capacity': 32},
        'reliability': {'mtbf': 50, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.55},
        'off_road': {'metric': 'metric', 'speed': 30, 'consume': 0.72},
    },
}

# ===== M270 MLRS =====
M270_MLRS_data = {
    'constructor': 'Lockheed Martin',
    'model': 'M270-MLRS',
    'made': 'USA',
    'start_service': 1983,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 2.8,  # M$
    'range': 640,  # km
    'roles': ['MLRS'],
    'engine': {
        'model': 'Cummins VTA-903',
        'capabilities': {'thrust': 500, 'fuel_efficiency': 0.68, 'type': 'diesel'},
        'reliability': {'mtbf': 60, 'mttr': 4}
    },
    'weapons': {
        'ARTILLERY': [('227mm-MLRS-Rocket', 12)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.6, 'communication_range': 180},
        'reliability': {'mtbf': 75, 'mttr': 1.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 25}),
            'lateral': (True, {'AP': 12}),
            'back': (True, {'AP': 12}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2800, 'fluid_capacity': 45},
        'reliability': {'mtbf': 80, 'mttr': 1.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 64, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 38, 'consume': 0.68},
    },
}

# ===== 9A52 Smerch 300mm MLRS =====
A9A52_Smerch_data = {
    'constructor': 'NPO Splav',
    'model': '9A52-Smerch',
    'made': 'USSR',
    'start_service': 1989,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 6.0,  # M$
    'range': 850,  # km
    'roles': ['MLRS'],
    'engine': {
        'model': 'YaMZ-238V',
        'capabilities': {'thrust': 525, 'fuel_efficiency': 0.62, 'type': 'diesel'},
        'reliability': {'mtbf': 48, 'mttr': 5}
    },
    'weapons': {
        'ARTILLERY': [('300mm-Smerch-Rocket', 12)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 150},
        'reliability': {'mtbf': 62, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 10}),
            'lateral': (True, {'AP': 5}),
            'back': (True, {'AP': 5}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2500, 'fluid_capacity': 40},
        'reliability': {'mtbf': 68, 'mttr': 2.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.45},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 32, 'consume': 0.78},
    },
}

# ===== 2S19 Msta 152mm SPH =====
S2S19_Msta_data = {
    'constructor': 'Uraltransmash',
    'model': '2S19-Msta',
    'made': 'USSR',
    'start_service': 1989,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 3.0,  # M$
    'range': 500,  # km
    'roles': ['SPH'],
    'engine': {
        'model': 'V-84A',
        'capabilities': {'thrust': 780, 'fuel_efficiency': 0.65, 'type': 'diesel'},
        'reliability': {'mtbf': 52, 'mttr': 4.5}
    },
    'weapons': {
        'ARTILLERY': [('2A64-152mm', 50)],
        'MACHINE_GUNS': [('NSVT-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 140},
        'reliability': {'mtbf': 65, 'mttr': 2.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 30}),
            'lateral': (True, {'AP': 20}),
            'back': (True, {'AP': 20}),
            'turret': (True, {'AP': 25}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 48},
        'reliability': {'mtbf': 70, 'mttr': 2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.58},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.72},
    },
}

# ===== M109 Paladin 155mm SPH =====
M109_Paladin_data = {
    'constructor': 'BAE Systems',
    'model': 'M109-Paladin',
    'made': 'USA',
    'start_service': 1992,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 5.5,  # M$
    'range': 350,  # km
    'roles': ['SPH'],
    'engine': {
        'model': 'Detroit Diesel 8V71T',
        'capabilities': {'thrust': 440, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 55, 'mttr': 4}
    },
    'weapons': {
        'ARTILLERY': [('M284-155mm', 39)],
        'MACHINE_GUNS': [('M2HB-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.65, 'communication_range': 200},
        'reliability': {'mtbf': 80, 'mttr': 1.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 40}),
            'lateral': (True, {'AP': 30}),
            'back': (True, {'AP': 25}),
            'turret': (True, {'AP': 35}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3200, 'fluid_capacity': 52},
        'reliability': {'mtbf': 85, 'mttr': 1.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 48, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 56, 'consume': 0.55},
        'off_road': {'metric': 'metric', 'speed': 32, 'consume': 0.7},
    },
}

# ===== PLZ-05 155mm SPH =====
PLZ05_data = {
    'constructor': 'Norinco',
    'model': 'PLZ-05',
    'made': 'China',
    'start_service': 2008,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 3.5,  # M$
    'range': 450,  # km
    'roles': ['SPH'],
    'engine': {
        'model': '12150L-7BW',
        'capabilities': {'thrust': 730, 'fuel_efficiency': 0.64, 'type': 'diesel'},
        'reliability': {'mtbf': 58, 'mttr': 3.5}
    },
    'weapons': {
        'ARTILLERY': [('PL-45-155mm', 30)],
        'MACHINE_GUNS': [('QJC88-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.6, 'communication_range': 170},
        'reliability': {'mtbf': 72, 'mttr': 2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 35}),
            'lateral': (True, {'AP': 25}),
            'back': (True, {'AP': 20}),
            'turret': (True, {'AP': 30}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3100, 'fluid_capacity': 50},
        'reliability': {'mtbf': 78, 'mttr': 1.6},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.68},
    },
}

# ===== T155 Firtina 155mm SPH =====
T155_Firtina_data = {
    'constructor': 'FNSS Defence Systems',
    'model': 'T155-Firtina',
    'made': 'Turkey',
    'start_service': 2004,
    'end_service': None,
    'category': 'Artillery_Semovent',
    'cost': 4.0,  # M$
    'range': 480,  # km
    'roles': ['SPH'],
    'engine': {
        'model': 'MTU MT 881 Ka-500',
        'capabilities': {'thrust': 1000, 'fuel_efficiency': 0.72, 'type': 'diesel'},
        'reliability': {'mtbf': 65, 'mttr': 3}
    },
    'weapons': {
        'ARTILLERY': [('Firtina-155mm', 48)],
        'MACHINE_GUNS': [('K6-12.7', 1)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.68, 'communication_range': 190},
        'reliability': {'mtbf': 78, 'mttr': 1.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 40}),
            'lateral': (True, {'AP': 30}),
            'back': (True, {'AP': 25}),
            'turret': (True, {'AP': 35}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3300, 'fluid_capacity': 55},
        'reliability': {'mtbf': 82, 'mttr': 1.4},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.36},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.65},
    },
}
# Nuovi veicoli AAA (Anti-Aircraft Artillery) semoventi da aggiungere a Vehicle_Data.py
# Generato automaticamente dalle ricerche degli agent

# ===== ZSU-57-2 Sparka =====
ZSU_57_2_data = {
    'constructor': 'Uraltransmash',
    'model': 'ZSU-57-2',
    'made': 'USSR',
    'start_service': 1957,
    'end_service': 1990,
    'category': 'AAA',
    'cost': 1.5,  # M$
    'range': 420,  # km
    'roles': ['AAA'],
    'engine': {
        'model': 'V-54',
        'capabilities': {'thrust': 520, 'fuel_efficiency': 0.52, 'type': 'diesel'},
        'reliability': {'mtbf': 35, 'mttr': 6}
    },
    'weapons': {
        'CANNONS': [('S-68-57mm', 300)],  # Twin 57mm
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.25, 'communication_range': 70},
        'reliability': {'mtbf': 38, 'mttr': 4}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 15}),
            'lateral': (True, {'AP': 8}),
            'back': (True, {'AP': 8}),
            'turret': (True, {'AP': 12}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2200, 'fluid_capacity': 35},
        'reliability': {'mtbf': 42, 'mttr': 3.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 42, 'consume': 0.48},
        'max': {'metric': 'metric', 'speed': 50, 'consume': 0.65},
        'off_road': {'metric': 'metric', 'speed': 28, 'consume': 0.8},
    },
}

# ===== ZSU-23-4 Shilka =====
ZSU_23_4_data = {
    'constructor': 'Mytishchi Machine Building Plant',
    'model': 'ZSU-23-4-Shilka',
    'made': 'USSR',
    'start_service': 1965,
    'end_service': None,
    'category': 'AAA',
    'cost': 1.8,  # M$
    'range': 450,  # km
    'roles': ['AAA'],
    'engine': {
        'model': 'V-6R',
        'capabilities': {'thrust': 280, 'fuel_efficiency': 0.55, 'type': 'diesel'},
        'reliability': {'mtbf': 40, 'mttr': 5}
    },
    'weapons': {
        'CANNONS': [('AZP-23-23mm', 2000)],  # Quad 23mm
    },
    'radar': {
        'model': '1RL33 Gun Dish',
        'capabilities': {
            'air': (True, {'tracking_range': 8, 'acquisition_range': 20, 'engagement_range': 8, 'multi_target_capacity': 1}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 45, 'mttr': 4}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 95},
        'reliability': {'mtbf': 48, 'mttr': 3}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 15}),
            'lateral': (True, {'AP': 9}),
            'back': (True, {'AP': 9}),
            'turret': (True, {'AP': 12}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2400, 'fluid_capacity': 38},
        'reliability': {'mtbf': 52, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 42, 'consume': 0.45},
        'max': {'metric': 'metric', 'speed': 50, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 30, 'consume': 0.75},
    },
}

# ===== M163 VADS =====
M163_VADS_data = {
    'constructor': 'General Electric',
    'model': 'M163-VADS',
    'made': 'USA',
    'start_service': 1969,
    'end_service': 1998,
    'category': 'AAA',
    'cost': 1.0,  # M$
    'range': 480,  # km
    'roles': ['AAA'],
    'engine': {
        'model': 'Detroit Diesel 6V53',
        'capabilities': {'thrust': 215, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 48, 'mttr': 4.5}
    },
    'weapons': {
        'CANNONS': [('M61-Vulcan-20mm', 2100)],
    },
    'radar': None,
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.4, 'communication_range': 110},
        'reliability': {'mtbf': 55, 'mttr': 2.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 38}),
            'lateral': (True, {'AP': 32}),
            'back': (True, {'AP': 28}),
            'turret': (True, {'AP': 25}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2500, 'fluid_capacity': 40},
        'reliability': {'mtbf': 60, 'mttr': 2.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 67, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.68},
    },
}

# ===== Flakpanzer Gepard =====
Flakpanzer_Gepard_data = {
    'constructor': 'Krauss-Maffei',
    'model': 'Flakpanzer-Gepard',
    'made': 'Germany',
    'start_service': 1976,
    'end_service': None,
    'category': 'AAA',
    'cost': 5.5,  # M$
    'range': 550,  # km
    'roles': ['AAA'],
    'engine': {
        'model': 'MTU MB 838 CaM 500',
        'capabilities': {'thrust': 830, 'fuel_efficiency': 0.7, 'type': 'diesel'},
        'reliability': {'mtbf': 58, 'mttr': 3.5}
    },
    'weapons': {
        'CANNONS': [('Oerlikon-KDA-35mm', 680)],  # Twin 35mm
    },
    'radar': {
        'model': 'Search and Tracking Radar',
        'capabilities': {
            'air': (True, {'tracking_range': 12, 'acquisition_range': 15, 'engagement_range': 12, 'multi_target_capacity': 1}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 65, 'mttr': 2.5}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.55, 'communication_range': 160},
        'reliability': {'mtbf': 70, 'mttr': 2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 40}),
            'lateral': (True, {'AP': 20}),
            'back': (True, {'AP': 15}),
            'turret': (True, {'AP': 30}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 3000, 'fluid_capacity': 48},
        'reliability': {'mtbf': 75, 'mttr': 1.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.36},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.65},
    },
}

# ===== 2K22 Tunguska =====
K2K22_Tunguska_data = {
    'constructor': 'KBP Instrument Design Bureau',
    'model': '2K22-Tunguska',
    'made': 'USSR',
    'start_service': 1982,
    'end_service': None,
    'category': 'AAA',
    'cost': 16.0,  # M$
    'range': 500,  # km
    'roles': ['AAA', 'SHORAD'],
    'engine': {
        'model': 'V-46-2',
        'capabilities': {'thrust': 780, 'fuel_efficiency': 0.62, 'type': 'diesel'},
        'reliability': {'mtbf': 52, 'mttr': 4}
    },
    'weapons': {
        'CANNONS': [('2A38M-30mm', 1904)],  # Quad 30mm
        'MISSILES': [('9M311-SAM', 8)],
    },
    'radar': {
        'model': '1RL144 Search + 1A26 Tracking',
        'capabilities': {
            'air': (True, {'tracking_range': 13, 'acquisition_range': 18, 'engagement_range': 10, 'multi_target_capacity': 2}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 60, 'mttr': 3}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 140},
        'reliability': {'mtbf': 65, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 20}),
            'lateral': (True, {'AP': 9}),
            'back': (True, {'AP': 9}),
            'turret': (True, {'AP': 15}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2800, 'fluid_capacity': 45},
        'reliability': {'mtbf': 68, 'mttr': 2.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.55},
        'off_road': {'metric': 'metric', 'speed': 38, 'consume': 0.7},
    },
}
# Nuovi veicoli SAM (Surface-to-Air Missile) montati su veicoli da aggiungere a Vehicle_Data.py
# Generato automaticamente dalle ricerche degli agent

# ===== Strela-1 9P31 (SA-9 Gaskin) =====
Strela1_9P31_data = {
    'constructor': 'KBM Kolomna',
    'model': 'Strela-1-9P31',
    'made': 'USSR',
    'start_service': 1968,
    'end_service': None,
    'category': 'SAM_Small',
    'cost': 1.2,  # M$
    'range': 500,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'GAZ-49B',
        'capabilities': {'thrust': 240, 'fuel_efficiency': 0.55, 'type': 'gasoline'},
        'reliability': {'mtbf': 38, 'mttr': 6}
    },
    'weapons': {
        'MISSILES': [('9M31-SAM', 4)],
    },
    'radar': None,
    'TVD': {
        'model': 'Optical sight',
        'capabilities': {
            'air': (True, {'tracking_range': 5, 'acquisition_range': 8, 'engagement_range': 5, 'multi_target_capacity': 1}),
            'ground': (True, {'tracking_range': 5, 'acquisition_range': 8, 'engagement_range': 5, 'multi_target_capacity': 1}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 50, 'mttr': 3}
    },
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.3, 'communication_range': 80},
        'reliability': {'mtbf': 45, 'mttr': 3.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 10}),
            'lateral': (True, {'AP': 7}),
            'back': (True, {'AP': 7}),
            'turret': (True, {'AP': 8}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2200, 'fluid_capacity': 32},
        'reliability': {'mtbf': 48, 'mttr': 3.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 65, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 75, 'consume': 0.58},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.72},
    },
}

# ===== MIM-72G Chaparral =====
MIM72G_Chaparral_data = {
    'constructor': 'Ford Aerospace',
    'model': 'MIM-72G-Chaparral',
    'made': 'USA',
    'start_service': 1969,
    'end_service': 1998,
    'category': 'SAM_Small',
    'cost': 1.5,  # M$
    'range': 480,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'Detroit Diesel 6V53',
        'capabilities': {'thrust': 215, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 48, 'mttr': 4.5}
    },
    'weapons': {
        'MISSILES': [('MIM-72-SAM', 4)],
    },
    'radar': None,
    'TVD': {
        'model': 'Forward Looking Infrared',
        'capabilities': {
            'air': (True, {'tracking_range': 6, 'acquisition_range': 10, 'engagement_range': 6, 'multi_target_capacity': 1}),
            'ground': (True, {'tracking_range': 6, 'acquisition_range': 10, 'engagement_range': 6, 'multi_target_capacity': 1}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 52, 'mttr': 3}
    },
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.4, 'communication_range': 110},
        'reliability': {'mtbf': 55, 'mttr': 2.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 38}),
            'lateral': (True, {'AP': 32}),
            'back': (True, {'AP': 28}),
            'turret': (True, {'AP': 25}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2500, 'fluid_capacity': 40},
        'reliability': {'mtbf': 60, 'mttr': 2.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.38},
        'max': {'metric': 'metric', 'speed': 67, 'consume': 0.52},
        'off_road': {'metric': 'metric', 'speed': 40, 'consume': 0.68},
    },
}

# ===== 9A33 Osa (SA-8 Gecko) =====
A9A33_Osa_data = {
    'constructor': 'NPO Almaz',
    'model': '9A33-Osa',
    'made': 'USSR',
    'start_service': 1971,
    'end_service': None,
    'category': 'SAM_Small',
    'cost': 5.0,  # M$
    'range': 500,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'D-20',
        'capabilities': {'thrust': 210, 'fuel_efficiency': 0.52, 'type': 'diesel'},
        'reliability': {'mtbf': 42, 'mttr': 5}
    },
    'weapons': {
        'MISSILES': [('9M33-SAM', 6)],
    },
    'radar': {
        'model': 'Land Roll',
        'capabilities': {
            'air': (True, {'tracking_range': 20, 'acquisition_range': 30, 'engagement_range': 15, 'multi_target_capacity': 2}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 50, 'mttr': 4}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 100},
        'reliability': {'mtbf': 52, 'mttr': 3.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 12}),
            'lateral': (True, {'AP': 8}),
            'back': (True, {'AP': 8}),
            'turret': (True, {'AP': 10}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2600, 'fluid_capacity': 42},
        'reliability': {'mtbf': 55, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.45},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.75},
    },
}

# ===== 9K35 Strela-10 (SA-13 Gopher) =====
K9K35_Strela10_data = {
    'constructor': 'KBM Kolomna',
    'model': '9K35-Strela-10',
    'made': 'USSR',
    'start_service': 1976,
    'end_service': None,
    'category': 'SAM_Small',
    'cost': 2.5,  # M$
    'range': 500,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'YaMZ-238V',
        'capabilities': {'thrust': 240, 'fuel_efficiency': 0.56, 'type': 'diesel'},
        'reliability': {'mtbf': 40, 'mttr': 5.5}
    },
    'weapons': {
        'MISSILES': [('9M37-SAM', 8)],
    },
    'radar': None,
    'TVD': {
        'model': 'Optical-IR tracker',
        'capabilities': {
            'air': (True, {'tracking_range': 6, 'acquisition_range': 10, 'engagement_range': 6, 'multi_target_capacity': 1}),
            'ground': (True, {'tracking_range': 6, 'acquisition_range': 10, 'engagement_range': 6, 'multi_target_capacity': 1}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 48, 'mttr': 3.5}
    },
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.35, 'communication_range': 95},
        'reliability': {'mtbf': 50, 'mttr': 3.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 10}),
            'lateral': (True, {'AP': 7}),
            'back': (True, {'AP': 7}),
            'turret': (True, {'AP': 8}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2300, 'fluid_capacity': 35},
        'reliability': {'mtbf': 52, 'mttr': 3},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 61, 'consume': 0.55},
        'off_road': {'metric': 'metric', 'speed': 35, 'consume': 0.7},
    },
}

# ===== MIM-115 Roland =====
MIM115_Roland_data = {
    'constructor': 'Euromissile',
    'model': 'MIM-115-Roland',
    'made': 'France',
    'start_service': 1977,
    'end_service': None,
    'category': 'SAM_Small',
    'cost': 3.5,  # M$
    'range': 450,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'Mercedes-Benz OM 402A',
        'capabilities': {'thrust': 320, 'fuel_efficiency': 0.68, 'type': 'diesel'},
        'reliability': {'mtbf': 55, 'mttr': 4}
    },
    'weapons': {
        'MISSILES': [('Roland-SAM', 10)],
    },
    'radar': {
        'model': 'MPDR 16',
        'capabilities': {
            'air': (True, {'tracking_range': 15, 'acquisition_range': 18, 'engagement_range': 10, 'multi_target_capacity': 2}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 60, 'mttr': 3}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 140},
        'reliability': {'mtbf': 65, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 15}),
            'lateral': (True, {'AP': 10}),
            'back': (True, {'AP': 10}),
            'turret': (True, {'AP': 12}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2700, 'fluid_capacity': 44},
        'reliability': {'mtbf': 68, 'mttr': 2.5},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 75, 'consume': 0.35},
        'max': {'metric': 'metric', 'speed': 90, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 50, 'consume': 0.62},
    },
}

# ===== 9K331 Tor (SA-15 Gauntlet) =====
K9K331_Tor_data = {
    'constructor': 'NPO Almaz',
    'model': '9K331-Tor',
    'made': 'USSR',
    'start_service': 1986,
    'end_service': None,
    'category': 'SAM_Small',
    'cost': 25.0,  # M$
    'range': 500,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'V-46-2',
        'capabilities': {'thrust': 780, 'fuel_efficiency': 0.6, 'type': 'diesel'},
        'reliability': {'mtbf': 50, 'mttr': 4.5}
    },
    'weapons': {
        'MISSILES': [('9M331-SAM', 8)],
    },
    'radar': {
        'model': 'Multifunction 3D Radar',
        'capabilities': {
            'air': (True, {'tracking_range': 20, 'acquisition_range': 25, 'engagement_range': 15, 'multi_target_capacity': 4}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 62, 'mttr': 3.5}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.55, 'communication_range': 150},
        'reliability': {'mtbf': 68, 'mttr': 2.2}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 20}),
            'lateral': (True, {'AP': 12}),
            'back': (True, {'AP': 12}),
            'turret': (True, {'AP': 15}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2900, 'fluid_capacity': 48},
        'reliability': {'mtbf': 72, 'mttr': 2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.4},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.55},
        'off_road': {'metric': 'metric', 'speed': 38, 'consume': 0.7},
    },
}

# ===== M6 Linebacker =====
M6_Linebacker_data = {
    'constructor': 'Boeing',
    'model': 'M6-Linebacker',
    'made': 'USA',
    'start_service': 1997,
    'end_service': None,
    'category': 'SAM_Small',
    'cost': 3.0,  # M$
    'range': 480,  # km
    'roles': ['SHORAD'],
    'engine': {
        'model': 'Cummins VTA-903T',
        'capabilities': {'thrust': 600, 'fuel_efficiency': 0.65, 'type': 'diesel'},
        'reliability': {'mtbf': 60, 'mttr': 3.5}
    },
    'weapons': {
        'CANNONS': [('M242-25mm', 900)],
        'MISSILES': [('FIM-92-Stinger', 4)],
    },
    'radar': None,
    'TVD': {
        'model': 'FLIR and targeting system',
        'capabilities': {
            'air': (True, {'tracking_range': 8, 'acquisition_range': 12, 'engagement_range': 8, 'multi_target_capacity': 1}),
            'ground': (True, {'tracking_range': 8, 'acquisition_range': 12, 'engagement_range': 8, 'multi_target_capacity': 1}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 65, 'mttr': 2.5}
    },
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.6, 'communication_range': 180},
        'reliability': {'mtbf': 75, 'mttr': 1.8}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 32}),
            'lateral': (True, {'AP': 20}),
            'back': (True, {'AP': 15}),
            'turret': (True, {'AP': 25}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2800, 'fluid_capacity': 46},
        'reliability': {'mtbf': 78, 'mttr': 1.6},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 58, 'consume': 0.36},
        'max': {'metric': 'metric', 'speed': 66, 'consume': 0.5},
        'off_road': {'metric': 'metric', 'speed': 42, 'consume': 0.65},
    },
}

# ===== 2K12 Kub (SA-6 Gainful) =====
K2K12_Kub_data = {
    'constructor': 'NPO Novator',
    'model': '2K12-Kub',
    'made': 'USSR',
    'start_service': 1967,
    'end_service': None,
    'category': 'SAM_Medium',
    'cost': 8.0,  # M$
    'range': 450,  # km
    'roles': ['MERAD'],
    'engine': {
        'model': 'V-6R',
        'capabilities': {'thrust': 300, 'fuel_efficiency': 0.54, 'type': 'diesel'},
        'reliability': {'mtbf': 42, 'mttr': 5.5}
    },
    'weapons': {
        'MISSILES': [('3M9-SAM', 3)],
    },
    'radar': {
        'model': '1S91 Straight Flush',
        'capabilities': {
            'air': (True, {'tracking_range': 28, 'acquisition_range': 75, 'engagement_range': 28, 'multi_target_capacity': 1}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 48, 'mttr': 4.5}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.4, 'communication_range': 120},
        'reliability': {'mtbf': 52, 'mttr': 3.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 15}),
            'lateral': (True, {'AP': 10}),
            'back': (True, {'AP': 10}),
            'turret': (True, {'AP': 12}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2500, 'fluid_capacity': 40},
        'reliability': {'mtbf': 55, 'mttr': 3.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 42, 'consume': 0.45},
        'max': {'metric': 'metric', 'speed': 50, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 28, 'consume': 0.78},
    },
}

# ===== 9K37 Buk (SA-11 Gadfly) =====
K9K37_Buk_data = {
    'constructor': 'NPO Almaz',
    'model': '9K37-Buk',
    'made': 'USSR',
    'start_service': 1979,
    'end_service': None,
    'category': 'SAM_Medium',
    'cost': 12.0,  # M$
    'range': 500,  # km
    'roles': ['MERAD'],
    'engine': {
        'model': 'GTD-1000T',
        'capabilities': {'thrust': 1000, 'fuel_efficiency': 0.58, 'type': 'diesel'},
        'reliability': {'mtbf': 48, 'mttr': 5}
    },
    'weapons': {
        'MISSILES': [('9M38-SAM', 4)],
    },
    'radar': {
        'model': '9S35 Fire Dome',
        'capabilities': {
            'air': (True, {'tracking_range': 45, 'acquisition_range': 85, 'engagement_range': 45, 'multi_target_capacity': 1}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 55, 'mttr': 4}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.5, 'communication_range': 150},
        'reliability': {'mtbf': 62, 'mttr': 3}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 18}),
            'lateral': (True, {'AP': 12}),
            'back': (True, {'AP': 12}),
            'turret': (True, {'AP': 15}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2700, 'fluid_capacity': 45},
        'reliability': {'mtbf': 65, 'mttr': 2.8},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 55, 'consume': 0.42},
        'max': {'metric': 'metric', 'speed': 65, 'consume': 0.58},
        'off_road': {'metric': 'metric', 'speed': 38, 'consume': 0.72},
    },
}

# ===== S-300PS (SA-10 Grumble) =====
S300PS_data = {
    'constructor': 'NPO Almaz',
    'model': 'S-300PS',
    'made': 'USSR',
    'start_service': 1982,
    'end_service': None,
    'category': 'SAM_Big',
    'cost': 20.0,  # M$
    'range': 600,  # km
    'roles': ['LORAD'],
    'engine': {
        'model': 'MAZ-543 Engine',
        'capabilities': {'thrust': 525, 'fuel_efficiency': 0.55, 'type': 'diesel'},
        'reliability': {'mtbf': 45, 'mttr': 5.5}
    },
    'weapons': {
        'MISSILES': [('5V55R-SAM', 4)],
    },
    'radar': {
        'model': '30N6 Flap Lid',
        'capabilities': {
            'air': (True, {'tracking_range': 90, 'acquisition_range': 150, 'engagement_range': 90, 'multi_target_capacity': 6}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': {'mtbf': 58, 'mttr': 4.5}
    },
    'TVD': None,
    'communication': {
        'model': 'generic comm model',
        'capabilities': {'navigation_accuracy': 0.6, 'communication_range': 200},
        'reliability': {'mtbf': 68, 'mttr': 2.5}
    },
    'protections': {
        'active': None,
        'armor': {
            'front': (True, {'AP': 12}),
            'lateral': (True, {'AP': 8}),
            'back': (True, {'AP': 8}),
            'turret': (False, {}),
        },
        'reactive': {},
    },
    'hydraulic': {
        'model': 'Generic Hydraulic System',
        'capabilities': {'pressure': 2600, 'fluid_capacity': 42},
        'reliability': {'mtbf': 62, 'mttr': 3.2},
    },
    'speed_data': {
        'sustained': {'metric': 'metric', 'speed': 50, 'consume': 0.45},
        'max': {'metric': 'metric', 'speed': 60, 'consume': 0.6},
        'off_road': {'metric': 'metric', 'speed': 30, 'consume': 0.78},
    },
}


# SETUP DICTIONARY VALUE 
SCORES = ('combat score', 'radar score', 'radar score air', 'radar score ground', 'speed score', 'avalaibility', 'manutenability score (mttr)', 'reliability score (mtbf)')
VEHICLE = {}

Vehicle_Data(**T90_data)
Vehicle_Data(**T72_data)
Vehicle_Data(**T130_data)
Vehicle_Data(**BMP1_data)

# Nuovi Main Battle Tanks
Vehicle_Data(**T55_data)
Vehicle_Data(**Chieftain_MK3_data)
Vehicle_Data(**Leopard_1A3_data)
Vehicle_Data(**M60A3_data)
Vehicle_Data(**Leopard_2A4_data)
Vehicle_Data(**Leopard_2A5_data)
Vehicle_Data(**Leopard_2A6M_data)
Vehicle_Data(**M1A2_Abrams_data)
Vehicle_Data(**Leclerc_data)
Vehicle_Data(**Challenger_II_data)
Vehicle_Data(**Merkava_IV_data)
Vehicle_Data(**Type_59_data)
Vehicle_Data(**T80U_data)
Vehicle_Data(**T90_base_data)
Vehicle_Data(**T72B3_data)
Vehicle_Data(**ZTZ_96B_data)

# Nuovi IFV
Vehicle_Data(**Marder_data)
Vehicle_Data(**BMP2_data)
Vehicle_Data(**BMD1_data)
Vehicle_Data(**M2_Bradley_data)
Vehicle_Data(**BMP3_data)
Vehicle_Data(**Warrior_data)
Vehicle_Data(**LAV25_data)
Vehicle_Data(**M1126_Stryker_data)
Vehicle_Data(**BTR82A_data)
Vehicle_Data(**ZBD04A_data)

# Nuovi APC
Vehicle_Data(**SdKfz_251_data)
Vehicle_Data(**MTLB_data)
Vehicle_Data(**M2A1_Halftrack_data)
Vehicle_Data(**M113_data)
Vehicle_Data(**AAV7_data)
Vehicle_Data(**TPz_Fuchs_data)
Vehicle_Data(**BTR80_data)
Vehicle_Data(**BTR_RD_data)

# Nuovi Artillery
Vehicle_Data(**BM21_Grad_data)
Vehicle_Data(**S2S3_Akatsia_data)
Vehicle_Data(**S2S1_Gvozdika_data)
Vehicle_Data(**BM27_Uragan_data)
Vehicle_Data(**Dana_vz77_data)
Vehicle_Data(**S2S9_Nona_data)
Vehicle_Data(**M270_MLRS_data)
Vehicle_Data(**A9A52_Smerch_data)
Vehicle_Data(**S2S19_Msta_data)
Vehicle_Data(**M109_Paladin_data)
Vehicle_Data(**PLZ05_data)
Vehicle_Data(**T155_Firtina_data)

# Nuovi AAA
Vehicle_Data(**ZSU_57_2_data)
Vehicle_Data(**ZSU_23_4_data)
Vehicle_Data(**M163_VADS_data)
Vehicle_Data(**Flakpanzer_Gepard_data)
Vehicle_Data(**K2K22_Tunguska_data)

# Nuovi SAM
Vehicle_Data(**Strela1_9P31_data)
Vehicle_Data(**MIM72G_Chaparral_data)
Vehicle_Data(**A9A33_Osa_data)
Vehicle_Data(**K9K35_Strela10_data)
Vehicle_Data(**MIM115_Roland_data)
Vehicle_Data(**K9K331_Tor_data)
Vehicle_Data(**M6_Linebacker_data)
Vehicle_Data(**K2K12_Kub_data)
Vehicle_Data(**K9K37_Buk_data)
Vehicle_Data(**S300PS_data)


# Load scores in dict
# specificando   nell'argomento la category, lo score viene calcolato in base agli score dei veicoli di pari categoria
# probabilmente è meglio calcolarlo su tutte le categorie (non specificando la categoria negli argomenti) in quanto 
# il valore rappresenterebbe un valore significaativo per il confronto con tutte le categorie, permettendo unaa più 
# realistica valutazione nel confronto tra forze eterogenee sul campo
# Tuttavia la presenza nel dizionario di veicoli di supporto può 'desensibilizzare' lo score quando si confrontano 
# veicoli di pari caratteristiche.
# Il calcolo nelle funzioni normalizzate è il valore restituito dalle funzioni eval (punteggio assoluto) normalizzato in base ai valori massimi e minimi della categoria di appartenenza del veicolo in oggetto
# quindi il valore restituito è sempre relativo alla categoria di appartenenza del veicolo e non confrontabile con veicoli di altre categorie
# Pertanto quando viene calcolato lo score 

for vehicle in Vehicle_Data._registry.values():    
    model = vehicle.model
    VEHICLE[model] = {}
    VEHICLE[model]['combat score'] = {'global_score': vehicle.get_normalized_combat_score(), 'category_score': vehicle.get_normalized_combat_score(category=vehicle.category)}
    VEHICLE[model]['weapon score'] = {'global_score': vehicle.get_normalized_weapon_score(), 'category_score': vehicle.get_normalized_weapon_score(category=vehicle.category) }
    VEHICLE[model]['radar score'] = {'global_score': vehicle.get_normalized_radar_score(), 'category_score': vehicle.get_normalized_radar_score(category=vehicle.category) }
    VEHICLE[model]['radar score ground'] = {'global_score': vehicle.get_normalized_radar_score(modes = ['ground']), 'category_score': vehicle.get_normalized_radar_score(modes = ['ground'], category=vehicle.category) }
    VEHICLE[model]['speed score'] = {'global_score': vehicle.get_normalized_speed_score(), 'category_score': vehicle.get_normalized_speed_score(category=vehicle.category) }
    VEHICLE[model]['communication score'] = {'global_score': vehicle.get_normalized_communication_score(), 'category_score': vehicle.get_normalized_communication_score(category=vehicle.category) }
    VEHICLE[model]['hydraulic score'] = {'global_score': vehicle.get_normalized_hydraulic_score(), 'category_score': vehicle.get_normalized_hydraulic_score(category=vehicle.category) }
    VEHICLE[model]['range score'] = {'global_score': vehicle.get_normalized_range_score(), 'category_score': vehicle.get_normalized_range_score(category=vehicle.category) }
    VEHICLE[model]['avalaibility'] = {'global_score': vehicle.get_normalized_avalaiability_score(), 'category_score': vehicle.get_normalized_avalaiability_score(category=vehicle.category)}
    VEHICLE[model]['manutenability score (mttr)'] = {'global_score': vehicle.get_normalized_maintenance_score(), 'category_score': vehicle.get_normalized_maintenance_score(category=vehicle.category)}
    VEHICLE[model]['reliability score (mtbf)'] = {'global_score': vehicle.get_normalized_reliability_score(), 'category_score': vehicle.get_normalized_reliability_score(category=vehicle.category)}




# STATIC METHODS (API)
def get_vehicle_data(model: str) -> Dict:
    """ Returns all data of a specific vehicle.
    
        Restituisce tutti i dati di un veicolo specifico.

    Args:
        model (str): modello del veicolo

    Raises:
        ValueError: model unknow

    Returns:
        Dict: Data vehicle
    """

    if model not in VEHICLE.keys():
        raise ValueError(f"model unknow. model must be: {VEHICLE.keys()}")  
    
    return VEHICLE[model]

def get_vehicle_scores(model: str, scores: Optional[List]=SCORES) -> Dict:
    """ Returns the overall and category scores for a specific vehicle.
        Overall scores are calculated considering all vehicles in the database,
        while category scores are calculated considering only vehicles of the same category as the specified vehicle.
        The available scores are:
        - Combat Score: Represents the vehicle's overall combat score. This score takes into account various factors such as armament, protection, mobility, and communications systems.
        - Radar Score: Indicates the effectiveness of the vehicle's radar system. A higher score suggests a better ability to detect and track targets.
        - Speed ​​Score: Evaluates the vehicle's speed and mobility. A higher score indicates a greater ability to move around the battlefield.
        - Availability: Measures the vehicle's operational readiness, based on factors such as reliability and ease of maintenance.
        - Maintainability Score (MTTR): Evaluates the vehicle's ease of maintenance, with a higher score indicating shorter repair times.
        - reliability score (MTBF): represents the reliability of the vehicle, with a higher score indicating longer intervals between failures.

        -------------------------------------
    
        Restituisce i punteggi globali e di categoria di un veicolo specifico.
        I punteggi globali sono calcolati considerando tutti i veicoli presenti nel database,
        mentre i punteggi di categoria sono calcolati considerando solo i veicoli della stessa categoria del veicolo specificato.
        I punteggi disponibili sono:
        - combat score: rappresenta il punteggio complessivo di combattimento del veicolo. Questo punteggio tiene conto di vari fattori come armamento, protezione, mobilità e sistemi di comunicazione.
        - Radar score: indica l'efficacia del sistema radar del veicolo. Un punteggio più alto suggerisce una migliore capacità di rilevamento e tracciamento dei bersagli.
        - Speed score: valuta la velocità e la mobilità del veicolo. Un punteggio più alto indica una maggiore capacità di movimento sul campo di battaglia.
        - avalaibility: misura la disponibilità operativa del veicolo, basata su fattori come affidabilità e facilità di manutenzione.
        - manutenability score (mttr): valuta la facilità di manutenzione del veicolo, con un punteggio più alto che indica tempi di riparazione più brevi.
        - reliability score (mtbf): rappresenta l'affidabilità del veicolo, con un punteggio più alto che indica intervalli più lunghi tra i guasti.

    Args:
        model (str): modello del veicolo
        scores (Optional[List], optional): score richiesti. Defaults all scores.

    Raises:
        ValueError: model unknow
        ValueError: scores unknow
    Returns:
        Dict: Scores
    """
    if model not in VEHICLE.keys():
        raise ValueError(f"model unknow. model must be: {VEHICLE.keys()}")    

    if scores and scores not in SCORES:
        raise ValueError(f"scores unknow. scores must be: {SCORES!r}")
    
    
    results = {}
    for score in scores:
        results[score] = VEHICLE[model][score]

    return results

#TEST
'''
for model, data in VEHICLE.items():
    for name, score in data.items():
        for score_name, score_value in score.items():
            print(f"{model} {name} {score_name}: {score_value:.4f}")
    

print(f"T-90 Speed score and avalaibility: {get_vehicle_scores(model = 'T-90M', scores = ['Speed score', 'avalaibility', 'combat score'])}" )
'''
STAMPA = True
if STAMPA:
    # Prepara i dati per la tabella
    table_data = []

    # Itera sui dati per costruire le righe della tabella
    for model, data in VEHICLE.items():
        for name, score in data.items():
            for score_name, score_value in score.items():
                table_data.append([model, name, score_name, score_value])

    # Crea un DataFrame con i dati
    df = pd.DataFrame(table_data, columns=["Model", "Name", "Score Name", "Score Value"])

    # Crea la tabella pivot
    pivot_table = df.pivot_table(
        index=["Name", "Score Name"],  # Indici delle righe
        columns=["Model"],              # Colonne della tabella
        values="Score Value",         # Valori da visualizzare
        aggfunc="first"               # Funzione di aggregazione (non necessaria qui)
    )

    # Riformatta le colonne per ottenere un layout leggibile
    pivot_table = pivot_table.sort_index(axis=1, level=[0, 1])  # Ordina le colonne per Model e Score Name


    # Stampa la tabella pivot in formato leggibile
    print(tabulate(pivot_table, headers="keys", tablefmt="grid"))