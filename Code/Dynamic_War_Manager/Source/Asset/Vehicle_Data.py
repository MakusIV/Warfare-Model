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
from Code.Dynamic_War_Manager.Source.Context.Context import GROUND_ACTION, ACTION_TASKS, BLOCK_ASSET_CATEGORY
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
CATEGORY = BLOCK_ASSET_CATEGORY['Ground_Military_Vehicle_Asset'].keys()

@dataclass
class Vehicle_Data:

    _registry = {}
    
    def __init__(self, constructor: str, made: str, model: str, category: str, start_service: str, end_service: str, cost: int, range: int, roles: str, engine: Dict, weapons: Dict, radar: Dict, TVD: Dict, communication: Dict, hydraulic: Dict, protections: Dict, speed_data: Dict):
        self.constructor = constructor
        self.made = made
        self.model = model # registry keys
        self.category = category #Tank, Armor, ......
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
            logger.warning("Radar not defined.")
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
            logger.warning("TVD not defined.")
            return 0.0
        
        if not modes:
            modes = ['air', 'ground', 'sea']
        
        elif not isinstance(modes, List) or not all ( m in ['air', 'ground', 'sea'] for m in modes ):
            raise TypeError(f"Il parametro 'modes' must be a List of string with value:  ['air', 'ground', 'sea'], got {modes!r}.")
        
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
                raise ValueError(f"Metric must be 'metric' or 'imperial', got {metric!r}.")
            
            speed = data.get('speed', 0)

            if metric == 'imperial':
                speed = convert_mph_to_kmh(speed)

            # Considera anche l'altitudine e il consumo
            score += speed * weight # - data.get('consume', 0) * 0.001
            
        return score


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
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == self.category]

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
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == self.category]
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
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == category]
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
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == category]
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
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == category]
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
        
        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == category]
        scores = [ac._maintenance_eval() for ac in vehicles]
        return 1- self._normalize(self._maintenance_eval(), scores)        

    def _combat_eval(self):
        """Returns the combat score calculated by considering the individual scores of the vehicle's subsystems

        Returns:
            float: combat score
        """
        # param = (value, weight)
        params = {   
                    'weapon':           ( self._weapon_eval(), 10 ), 
                    'radar':            ( self._radar_eval(), 2 ), 
                    'TVD':              ( self._TVD_eval(), 3 ), 
                    'protection':       ( self._protection_eval(), 9 ), 
                    'communication':    ( self._communication_eval(), 3 ), 
                    'speed_data':       ( self._speed_eval(), 7 ), 
                    'hydraulic':        ( self._hydraulic_eval(), 4 ), 
                    'range':            ( self._range_eval(), 1 )
                }
        
        tot_weights = sum( data[1] for param, data in params.items() )
        return sum( data[0] * data[1] for param, data in params.items() ) / tot_weights

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
                
                #else:
                #    logger.warning(f"weapon_type unknow, got {weapon_type}"
                                   
                score += get_weapon_score( weapon_type = weapon_type, weapon_model = weapon_item[0] ) * factor_ammo_quantity

        return score

    def _protection_eval(self):

        
        return 1

    def _communication_eval(self):

        
        return 1

    def _hydraulic_eval(self):

       
        return 1
    
    def _range_eval(self):

        
        return 1
    

    def get_normalized_combat_score(self, category: Optional[str] = None):
        """returns combat score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized combat score score
        """
        if not category:
            category = CATEGORY
        elif not isinstance(category, str) or not category in CATEGORY:
            raise ValueError(f"category be string with value:  {CATEGORY!r}, got {category!r}.")
        

        vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category == category]
        scores = [ac._combat_eval() for ac in vehicles]
        return self._normalize(self._combat_eval(), scores)
    

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
            raise ValueError(f"task must be a string with values: {AIR_TASK!r}, got {task!r}")
        
    
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
    'roles': ['', 'Intercept', 'SEAD'],
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
    'roles': ['', 'Intercept', 'SEAD'],
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
    'roles': ['', 'Intercept', 'SEAD'],
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

# SETUP DICTIONARY VALUE 
SCORES = ('combat score', 'Radar score', 'Radar score air', 'Speed score', 'avalaibility', 'manutenability score (mttr)', 'reliability score (mtbf)')
VEHICLE = {}

Vehicle_Data(**T90_data)
Vehicle_Data(**T72_data)
Vehicle_Data(**T130_data)

# Load scores in dict
# specificando   nell'argomento la category, lo score viene calcolato in base agli score dei veicoli di pari categoria
# probabilmente è meglio calcolarlo su tutte le categorie (non specificando la categoria negli argomenti) in quanto 
# il valor rappresenterebbe il un valore significaativo per il confronto con tutte le categorie, permettendo unaa più 
# realistica valutazione nel confronto tra forze eterogenee sul campo
# Tuttavia la presenza nel dizzionario di veicoli di supporto può 'desensibilizzare' lo score quando si confrontano 
# veicoli di pari caratteristiche.

for vehicle in Vehicle_Data._registry.values():    
    model = vehicle.model
    VEHICLE[model] = {}
    VEHICLE[model]['combat score'] = {'global_score': vehicle.get_normalized_combat_score(), 'category_score': vehicle.get_normalized_combat_score(category=vehicle.category)}
    VEHICLE[model]['Radar score'] = {'global_score': vehicle.get_normalized_radar_score(), 'category_score': vehicle.get_normalized_radar_score(category=vehicle.category) }
    VEHICLE[model]['Radar score air'] = {'global_score': vehicle.get_normalized_radar_score(modes = ['air']), 'category_score': vehicle.get_normalized_radar_score(modes = ['air'], category=vehicle.category) }
    VEHICLE[model]['Speed score'] = {'global_score': vehicle.get_normalized_speed_score(), 'category_score': vehicle.get_normalized_speed_score(category=vehicle.category) }
    VEHICLE[model]['avalaibility'] = {'global_score': vehicle.get_normalized_avalaiability_score(), 'category_score': vehicle.get_normalized_avalaiability_score(category=vehicle.category)}
    VEHICLE[model]['manutenability score (mttr)'] = {'global_score': vehicle.get_normalized_maintenance_score(), 'category_score': vehicle.get_normalized_maintenance_score(category=vehicle.category)}
    VEHICLE[model]['reliability score (mtbf)'] = {'global_score': vehicle.get_normalized_reliability_score(), 'category_score': vehicle.get_normalized_reliability_score(category=vehicle.category)}




# STATIC METHODS (API)
def get_vehicle_data(model: str) -> Dict:
    return VEHICLE

def get_vehicle_scores(model: str, scores: Optional[List]=None):

    if model not in VEHICLE.keys():
        raise ValueError(f"model unknow. model must be: {VEHICLE.keys()}")
    
    if scores and scores in SCORES:
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