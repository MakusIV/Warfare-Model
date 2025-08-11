from functools import lru_cache
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Context.Context import GROUND_ACTION
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Vehicle_Data')


VEHICLE_TASK = GROUND_ACTION

@dataclass
class Vehicle_Data:
    _registry = []
    
    
    def __init__(self, constructor: str, made: str, model: str, category: str, cost: int, roles: str, engine: Dict, radar: Dict, TVD: Dict, communication: Dict, hydraulic: Dict, armor: Dict, speed_data: Dict):
        self.constructor = constructor
        self.made = made
        self.model = model
        self.category = category
        self.cost = cost
        self.roles = roles
        self.engine = engine
        self.radar = radar
        self.TVD = TVD
        self.communication = communication
        self.hydraulic = hydraulic
        self.armor = armor
        self.speed_data = speed_data
        Vehicle_Data._registry.append(self)

    # --- Getter e Setter ---
    def engine(self):
        return self.engine
    
    def engine(self, engine):
        self.engine = engine

    def roles(self):
        return self.roles
    # ... (altri getter/setter per tutte le proprietà)

    
    # --- Implementazioni predefinite delle formule ---
    #@lru_cache
    def _radar_eval(self, modes: Optional[List] = None) -> float:
        """Evaluates the radar capabilities of the aircraft based on predefined weights.

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
            cap = self.radar['capabilities'][m]
            if cap[0]: 
                score += cap[1].get('tracking_range', 0) * weights['tracking_range']
                score += cap[1].get('acquisition_range', 0) * weights['acquisition_range']
                score += cap[1].get('engagement_range', 0) * weights['engagement_range']
                score += cap[1].get('multi_target_capacity', 0) * weights['multi_target']
        
        return score
    
    def _TVD_eval(self, modes: Optional[List] = None) -> float:
        """Evaluates the radar capabilities of the aircraft based on predefined weights."""
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
        """evaluate reliability (mtbf) of aircraft subsystem

        Returns:
            float: time (hour) before fault of an aircraft subsystem
        """        
        components = [
            self.engine.get('reliability', {}).get('mtbf', 0),
            self.radar.get('reliability', {}).get('mtbf', 0),
            self.TVD.get('reliability', {}).get('mtbf', 0),
            self.communication.get('reliability', {}).get('mtbf', 0),
            self.armor.get('reliability', {}).get('mtbf', 0),
            self.hydraulic.get('reliability', {}).get('mtbf', 0)
        ]
        # l'mtbf del singolo sottosistema incide nel valore finale del 30% mentre il valore medio del 70%
        return min(components)* 0.3 + 0.7 * sum(components) / len(components) # aircraft mtbf
    
    def _maintenance_eval(self):
        """evaluate maintenance load (mttr) requested of aircraft subsystem

        Returns:
            float: hour quantity rappresentative of maintenance job
        """
        components = [
            self.engine.get('reliability', {}).get('mttr', 0),
            self.radar.get('reliability', {}).get('mttr', 0),
            self.TVD.get('reliability', {}).get('mtbf', 0),
            self.communication.get('reliability', {}).get('mttr', 0),
            self.armor.get('reliability', {}).get('mttr', 0),
            self.hydraulic.get('reliability', {}).get('mttr', 0)
        ]    

        # l'mttr del singolo sottosistema incide nel valore finale del 30% mentre il valore medio del 70%
        return max(components) * 0.3 + 0.7 * sum(components) / len(components) # aircraft mttr
    
    def _avalaiability_eval(self):
        """evaluate avalaiability of aircraft

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

    # --- Metodi di confronto normalizzati ---
    def get_normalized_radar_score(self, modes: Optional[Dict] = None):
        """returns radar score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized radar score
        """
        scores = [ac._radar_eval(modes = modes) for ac in Vehicle_Data._registry]
        return self._normalize(self._radar_eval(modes = modes), scores)
    
    def get_normalized_TVD_score(self, modes: Optional[Dict] = None):
        """returns TVD score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized TVD score
        """
        scores = [ac._TVD_eval(modes = modes) for ac in Vehicle_Data._registry]
        return self._normalize(self._TVD_eval(modes = modes), scores)
    
    def get_normalized_speed_score(self):
        """returns speed score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized speed score
        """
        scores = [ac._speed_eval() for ac in Vehicle_Data._registry]
        return self._normalize(self._speed_eval(), scores)

    def get_normalized_reliability_score(self):
        """returns reliability score (mtbf) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized reliability score
        """
        scores = [ac._reliability_eval() for ac in Vehicle_Data._registry]
        return self._normalize(self._reliability_eval(), scores)
    
    def get_normalized_avalaiability_score(self):
        """returns avalaiability score (mtbf/mttr) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized avalaiability score
        """
        scores = [ac._avalaiability_eval() for ac in Vehicle_Data._registry]
        return self._normalize(self._avalaiability_eval(), scores)
    
    def get_normalized_maintenance_score(self):
        """returns maintenance score (mttr) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized maintenance score
        """
        scores = [ac._maintenance_eval() for ac in Vehicle_Data._registry]
        return 1- self._normalize(self._maintenance_eval(), scores)        

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

    def task_score(self, role: str, task: str, target_dimension: Dict[str, any], minimum_destroyed_fraction: float):
        
        if not role or not isinstance(role, str):
            raise TypeError ("role must be a string")
        if role not in VEHICLE_ROLE:
            raise ValueError(f"role must be a string with values: {VEHICLE_ROLE!r}, got {role!r}")
        if role not in self.roles:
            logger.warning(f"role {role!r} not in roles for this aircraft {self.constructor} - {self.model}")
            return 0.0
        
        if not task or not isinstance(task, str):
            raise TypeError ("task must be a string")
        if task not in VEHICLE_TASK[role]:
            raise ValueError(f"task must be a string with values: {VEHICLE_TASK[role]!r}, got {task!r}")
        
        
        score_radar = self._score_radar(role = role)
        destroyed_fraction  = self._eval_destroyed_quantity_with_ordinance( task = task, target = target_dimension)

        if destroyed_fraction < minimum_destroyed_fraction:
            return 0.0, 0.0

        return destroyed_fraction * score_radar
    
    def task_score_cost_ratio(self):
        pass

# AIRCRAFT DATA

# metric = metric - > speed: km/h, altitude: m, radar/TVD/radioNav range: km 
# metric = imperial - > speed: mph, altitude: feet, radar/TVD/radioNav range: nm

T90_data = {
    'constructor': 'UVTZ',    
    'model': 'T-90M',
    'made': 'Russia',
    'start_service': 2020,
    'end_service': int('inf'),
    'category': 'MTB', # Main Battle Tank
    'cost': 4, # M$
    'range': 550, # km
    'roles': ['', 'Intercept', 'SEAD'],
    'engine': {
        'model': 'Multifuel 12 Cylinders', 
        'capabilities': {'thrust': 840, 'fuel_efficiency': 0.8, 'type': 'multifuel'}, 
        'reliability': {'mtbf': 40, 'mttr': 5}
    },
    'weapons': {
        'cannons': [('2A46M', 42)],
        'missiles': [('9K119M', 6)],
        'machine_guns': [('PKT-7.62', 1), ('Kord-12.7', 1)],
            
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
        'cruise': ('metric', 45, None),
        'max': ('metric', 60, None),
        'off_road': ('metric', 45, None),
    },
}


T130_data = {
    'constructor': 'UVTZ',    
    'model': 'T-90M',
    'made': 'Russia',
    'start_service': 2020,
    'end_service': int('inf'),
    'category': 'MTB', # Main Battle Tank
    'cost': 4, # M$
    'roles': ['', 'Intercept', 'SEAD'],
    'engine': {
        'model': 'Multifuel 12 Cylinders', 
        'capabilities': {'thrust': 840, 'fuel_efficiency': 0.8, 'type': 'multifuel'}, 
        'reliability': {'mtbf': 40, 'mttr': 5}
    },
    'weapons': {
        'cannons': [('2A46M', 42)],
        'missiles': [('9K119M', 6)],
        'machine_guns': [('PKT-7.62', 1), ('Kord-12.7', 1)],
            
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
        'cruise': {'metric', 45, 'consume': None},
        'max': {'metric', 70, 'consume': None},
        'off_road': {'metric', 50, 'consume': None},
    },
}

# TEST
T90 = Vehicle_Data(**T90_data)
#Abrams = Vehicle_Data(**f18_data)

# Ottenere punteggi normalizzati
print(f"T90 Radar score: {T90.get_normalized_radar_score():.2f}")
print(f"T-90 Radar score air: {T90.get_normalized_radar_score(['air']):.2f}")
print(f"T-90 Speed score: {T90.get_normalized_speed_score():.2f}")
print(f"T-90 avalaibility: {T90.get_normalized_avalaiability_score():.2f}")
print(f"T-90 manutenability score (mttr): {T90.get_normalized_maintenance_score()}")
print(f"T-90 reliability score (mtbf): {T90.get_normalized_reliability_score()}")
