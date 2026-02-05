'''
NOTA: il calcolo dello score normalizzato deve essere effettuato considerando tipologie simili:
fighter-fighter, bomber-bomber ecc. altrimenti c'è il rischio che le differenze di score tra due stesse tipologie
siano ridotte causa il valutazione sottostimata delle score totale

NO: 
 specificando   nell'argomento la category, lo score viene calcolato in base agli score dei veicoli di pari categoria
# probabilmente è meglio calcolarlo su tutte le categorie (non specificando la categoria negli argomenti) in quanto 
# il valor rappresenterebbe il un valore significaativo per il confronto con tutte le categorie, permettendo unaa più 
# realistica valutazione nel confronto tra forze eterogenee sul campo
# Tuttavia la presenza nel dizzionario di veicoli di supporto può 'desensibilizzare' lo score quando si confrontano 
# veicoli di pari caratteristiche.


'''


from functools import lru_cache
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Context.Context import AIR_MILITARY_CRAFT_ASSET, AIR_TASK , Air_Asset_Type, Ground_Vehicle_Asset_Type
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft_Data').logger

AIRCRAFT_ROLE = AIR_MILITARY_CRAFT_ASSET.keys()
AIRCRAFT_TASK = AIR_TASK

@dataclass
class Aircraft_Data:
    _registry = {}
        
    def __init__(self, constructor: str, made: str, model: str, start_service: str, end_service: str, category: str, cost: int, roles: str, engine: Dict, radar: Dict, TVD: Dict, radio_nav: Dict, avionics: Dict, hydraulic: Dict, speed_data: Dict):
        self.constructor = constructor
        self.made = made
        self.model = model
        self.start_service = start_service
        self.end_service = end_service
        self.category = category
        self.cost = cost
        self.roles = roles
        self.engine = engine
        self.radar = radar
        self.TVD = TVD
        self.radio_nav = radio_nav
        self.avionics = avionics
        self.hydraulic = hydraulic
        self.speed_data = speed_data
        Aircraft_Data._registry[self.model] = self

    # --- Getter e Setter ---
    def engine(self):
        return self.engine
    
    def engine(self, engine):
        self.engine = engine

    def roles(self):
        return self.roles


    def model(self):
        return self.model
    
    def model(self, model):
        self.model = model

    def made(self):
        return self.made
    
    def made(self, made):
        self.made = made

    def get_aircraft(self, model: str):
        return self._registry.get(model)
    
    # --- Implementazioni predefinite delle formule ---
    #@lru_cache
    def _radar_eval(self, modes: Optional[List] = None, category: Optional[str] = None) -> float:
        """Evaluates the radar capabilities of the aircraft based on predefined weights.

        Params:
            Optional[List]: modes = []  with : 'air', 'ground', 'sea'

        Raises:
            TypeError: if modes element 

        Returns:
            float: radar score value
        """
        if self.radar == False:
            return 0.0

        if self.radar == None:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Radar not defined.")
            return 0.0
        
        if not modes:
            modes = ['air', 'ground', 'sea']
        
        elif not isinstance(modes, List) or not all ( m in ['air', 'ground', 'sea'] for m in modes ):
            raise TypeError(f"Il parametro 'modes' must be a List of string with value:  ['air', 'ground', 'sea'], got {modes!r}.")
        
        weights = {
            'tracking_range': 0.2 / 400, # weights / reference distance (km)
            'acquisition_range': 0.1 / 200,
            'engagement_range': 0.3 / 100,
            'multi_target': 0.4 / 5 # weights / reference multi targets
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
        if self.TVD == False:
            return 0.0
        
        if self.TVD == None:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - TVD not defined.")
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

    #@lru_cache
    def _speed_at_altitude_eval(self, metric: str, altitude: Optional[float] = None):
        """Evaluates the speed of the aircraft at a given altitude based on predefined speed data.
        Args:
            metric (str): 'metric' for km/h and meters, 'imperial' for mph and feet.
            altitude (Optional[float]): Altitude in meters (if metric) or feet (if imperial). Defaults to None, which will use 0.
        Returns:
            float: Calculated speed score.
        Raises:
            ValueError: If altitude is negative or metric is not 'metric' or 'imperial'.
        """
        if not isinstance(metric, str):
            raise TypeError(f"Metric must be a string, got {type(metric).__name__!r}.")        

        if not self.speed_data:
            logger.warning("speed_data not defined.")
            return 0.0
        
        if altitude is None:
            altitude = 0
        
        if altitude < 0:
            raise ValueError(f"Altitude must be a non-negative value, got {altitude!r}.")
        
        if metric not in ['metric', 'imperial']:
            raise ValueError(f"Metric must be 'metric' or 'imperial', got {metric!r}.")


        weights = {'sustained': 0.2, 'combat': 0.4, 'emergency': 0.3}
        score = 0

        for speed_type, weight in weights.items():
            data = self.speed_data.get(speed_type, {})
            speed = data.get('airspeed', 0)
                      

            if data.get('type_speed') == "indicated_airspeed":
                # converte l'airspeed indicato in velocità vera
                speed = true_air_speed( data.get('airspeed', 0), data.get('altitude'), data.get('metric') )

            elif data.get('type_speed') == "true_airspeed":
                speed = data['airspeed']            
            else:
                raise ValueError(f"Invalid type_speed: {data.get('type_speed', 'unknown')}. Expected 'indicated_airspeed' or 'true_airspeed'.")
            
            speed = true_air_speed_at_new_altitude(speed, data.get('altitude'), altitude, metric=data.get('metric'))

            if not hasattr(data, 'time'):
                time = 1 # sustained speed
            else:
                time = data.get('time')
                if speed_type == 'combat':
                    time /=  60  # reference on 60'
                 
                elif speed_type == 'emergency':
                    time /= 3 # reference on 3'
            
            # Considera anche l'altitudine e il consumo
            score += (speed * weight) * time # - data.get('consume', 0) * 0.001
        return score

    def _speed_eval(self) -> float:
        """evaluate speed score at fixed altitude for comparations

        Returns:
            float: median of speed calculates at 1000 and 6000 meter
        """        
        eval_1000 = self._speed_at_altitude_eval('metric', 1000)  # Default to metric and altitude 1000
        eval_5000 = self._speed_at_altitude_eval('metric', 6000)  # Default to metric and altitude 6000
        return (eval_1000 + eval_5000) / 2

    def _reliability_eval(self):
        """evaluate reliability (mtbf) of aircraft subsystem

        Returns:
            float: time (hour) before fault of an aircraft subsystem
        """                
        components = [
            self.engine.get('reliability', {}).get('mtbf', 0) if self.engine is not None and self.engine.get('reliability') else None,
            self.radar.get('reliability', {}).get('mtbf', 0) if self.radar and self.radar.get('reliability') else None,
            self.TVD.get('reliability', {}).get('mtbf', 0) if self.TVD and self.TVD.get('reliability') else None,
            self.avionics.get('reliability', {}).get('mtbf', 0) if self.avionics and self.avionics.get('reliability') else None,
            self.radio_nav.get('reliability', {}).get('mtbf', 0) if self.radio_nav and self.radio_nav.get('reliability') else None,            
            self.hydraulic.get('reliability', {}).get('mtbf', 0) if self.hydraulic and self.hydraulic.get('reliability') else None
        ]
        filtered_components = [x for x in components if x is not None]
        # l'mtbf del singolo sottosistema incide nel valore finale del 30% mentre il valore medio del 70%
        return min(filtered_components) * 0.3 + 0.7 * sum(filtered_components) / len(filtered_components) # aircraft mtbf
    
    def _maintenance_eval(self):
        """evaluate maintenance load (mttr) requested of aircraft subsystem

        Returns:
            float: hour quantity rappresentative of maintenance job
        """
        components = [
            self.engine.get('reliability', {}).get('mttr', 0) if self.engine is not None and self.engine.get('reliability') else None,
            self.radar.get('reliability', {}).get('mttr', 0) if self.radar and self.radar.get('reliability') else None,
            self.TVD.get('reliability', {}).get('mttr', 0) if self.TVD and self.TVD.get('reliability') else None,
            self.avionics.get('reliability', {}).get('mttr', 0) if self.avionics and self.avionics.get('reliability') else None,
            self.radio_nav.get('reliability', {}).get('mttr', 0) if self.radio_nav and self.radio_nav.get('reliability') else None,            
            self.hydraulic.get('reliability', {}).get('mttr', 0) if self.hydraulic and self.hydraulic.get('reliability') else None
        ]
        filtered_components = [x for x in components if x is not None]
        # l'mttr del singolo sottosistema incide nel valore finale del 30% mentre il valore medio del 70%
        return min(filtered_components) * 0.3 + 0.7 * sum(filtered_components) / len(filtered_components) # aircraft mttr
    
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
            machine_gun_score = 0

            for weapon_item in weapon:                
                factor_ammo_quantity = 1.0
                
                if weapon_type == 'CANNONS':                    
                    if self.category in [Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value, Ground_Vehicle_Asset_Type.TANK.value]:
                        factor_ammo_quantity = weapon_item[1] / 30 # 30 reference for cannons (32 cannons ammo -> factor_ammo_quantity = 1.05)
                    elif self.category == Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value:
                        factor_ammo_quantity = weapon_item[1] / 50 # 50 reference for cannons (100 cannons ammo -> factor_ammo_quantity = 2)

                elif weapon_type == 'MACHINE_GUNS': # non sono ammo ma numero di mitragliatrici dello stesso tipo                    
                    machine_gun_score += get_weapon_score( weapon_type = weapon_type, weapon_model = weapon_item[0] ) * weapon_item[1]
                               
                elif weapon_type == 'MISSILES':
                    if self.category in [Ground_Vehicle_Asset_Type.SAM_BIG.value, Ground_Vehicle_Asset_Type.SAM_MEDIUM.value, Ground_Vehicle_Asset_Type.SAM_SMALL.value, Ground_Vehicle_Asset_Type.AAA.value]:
                        factor_ammo_quantity = weapon_item[1] / 4 # 4 reference for missiles (4 missiles -> factor_ammo_quantity = 1)     
                    elif self.category in [Ground_Vehicle_Asset_Type.TANK.value, Ground_Vehicle_Asset_Type.ARMORED.value, Ground_Vehicle_Asset_Type.MOTORIZED.value]:
                        factor_ammo_quantity = weapon_item[1] / 2 # 2 reference for missiles (6 missiles -> factor_ammo_quantity = 3) 
                
                elif weapon_type == 'ROCKETS':
                    factor_ammo_quantity = weapon_item[1] / 4 # 4 reference for rockets (8 rockets -> factor_ammo_quantity = 2) 
                
                elif weapon_type == 'BOMBS':
                    factor_ammo_quantity = weapon_item[1] / 10 # 10 reference for mortar bombs (10 bobms -> factor_ammo_quantity = 1) 
                
                 
                # else:
                #    logger.warning(f"weapon_type unknow, got {weapon_type}"                                   
                
                factor_ammo_quantity = max(0.80, min(1.2, factor_ammo_quantity)) # limit to +-20%                                
                score += get_weapon_score( weapon_type = weapon_type, weapon_model = weapon_item[0] ) * factor_ammo_quantity # incremento del 10% del punteggio dell'arma in base alla quantità di munizionamento disponibile
                

        return score + machine_gun_score * 0.33 # riduco il peso delle mitragliatrici al 33% dello score totale in quanto armi di supporto se presente score (arma principale)


    # --- Metodi di confronto normalizzati ---
    def get_normalized_radar_score(self, modes: Optional[List] = None):
        """returns radar score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized radar score
        """
        scores = [ac._radar_eval(modes = modes) for ac in Aircraft_Data._registry.values()]
        return self._normalize(self._radar_eval(modes = modes), scores)
    
    def get_normalized_TVD_score(self, modes: Optional[Dict] = None):
        """returns TVD score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized TVD score
        """
        scores = [ac._TVD_eval(modes = modes) for ac in Aircraft_Data._registry.values()]
        return self._normalize(self._TVD_eval(modes = modes), scores)
    
    def get_normalized_speed_score(self):
        """returns speed score normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized speed score
        """
        scores = [ac._speed_eval() for ac in Aircraft_Data._registry.values()]
        return self._normalize(self._speed_eval(), scores)

    def get_normalized_reliability_score(self):
        """returns reliability score (mtbf) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized reliability score
        """
        scores = [ac._reliability_eval() for ac in Aircraft_Data._registry.values()]
        return self._normalize(self._reliability_eval(), scores)
    
    def get_normalized_avalaiability_score(self):
        """returns avalaiability score (mtbf/mttr) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized avalaiability score
        """
        scores = [ac._avalaiability_eval() for ac in Aircraft_Data._registry.values()]
        return self._normalize(self._avalaiability_eval(), scores)
    
    def get_normalized_maintenance_score(self):
        """returns maintenance score (mttr) normalized from 0 (min score) 1 (max score)

        Returns:
            float: normalized maintenance score
        """
        scores = [ac._maintenance_eval() for ac in Aircraft_Data._registry.values()]
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

    # VALUTA SE QUESTA FUNZIONE DEVE ESSERE IMPLEMENTATA NEL MODULO ATO NON QUI CONSIDERANDO CHE DEVE GESTIRE IL LOADOUT DELLE WEAPON
    def task_score(self, task: str, loadout: Dict[str, any], target_dimension: Dict[str, any], minimum_target_destroyed: float):
        
        if not task or not isinstance(task, str):
            raise TypeError ("task must be a string")
        if task not in AIR_TASK:
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

    
    #  VALUTA SE QUESTA FUNZIONE DEVE ESSERE IMPLEMENTATA NEL MODULO ATO NON QUI CONSIDERANDO CHE DEVE GESTIRE IL PAYLOAD DELLE WEAPON
    def _eval_destroyed_quantity_with_ordinance( self, task: str, loadout: Dict, target: str):
     
        pass

# AIRCRAFT DATA

# metric = metric - > speed: km/h, altitude: m, radar/TVD/radioNav range: km 
# metric = imperial - > speed: mph, altitude: feet, radar/TVD/radioNav range: nm

f16_data_example = {
    "constructor": "Lockheed Martin",
    "made": "USA",
    "model": "F-16C Block 50",
    "start_service": 1978,
    "end_service": None,
    "category": "fighter",
    "cost": 10, # M$
    "roles": ["CAP", "Intercept", "SEAD"],
    "engine": {
        "model": "F110-GE-129", 
        "capabilities": {"thrust": 13000, "fuel_efficiency": 0.8, "type": "jet"}, 
        "reliability": {"mtbf": 40, "mttr": 5}
    },
    "radar": {
        "model": "AN/APG-68(V)9",
        "capabilities": {
            "air": (True, {"tracking_range": 160, "acquisition_range": 70, "engagement_range": 50, "multi_target_capacity": 6}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 60, "engagement_range": 20, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 50, "multi_target_capacity": 3})            
        },
        "reliability": {"mtbf": 60, "mttr": 4},
        "type": "pulse-doppler"
            
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (True, {"tracking_range": 100, "acquisition_range": 120, "engagement_range": 100, "multi_target_capacity": 5}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 4}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0})      
        },
        "reliability": {"mtbf": 40, "mttr": 3},
        "type": "thermal and optical"
    },
    "radio_nav": {
        "model": "AN/ARN-118", 
        "capabilities": {"navigation_accuracy": 0.5, "communication_range": 200},
        "reliability": {"mtbf": 60, "mttr": 1.5}
        },
    "avionics": {
        "model": "AN/ALR-69A",
        "capabilities": {"flight_control": 0.9, "navigation_system": 0.8, "communication_system": 0.85},
        "reliability": {"mtbf": 40, "mttr": 1.2}
    },
    "hydraulic": {
        "model": "Generic Hydraulic System",
        "capabilities": {"pressure": 3000, "fluid_capacity": 50},
        "reliability": {"mtbf": 90, "mttr": 1.0},
    },
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 2500, "time": 120},  # time in minutes
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 4500, "time": 120}  # time in minutes   
    },
}

f18_data_example = {
    "constructor": "Lockheed Martin",
    "made": "USA",
    "model": "F-18C Block 50",
    "start_service": 1978,
    "end_service": None,
    "category": "fighter",
    "cost": 10, # M$
    "roles": ["CAP", "Intercept", "SEAD"],
    "engine": {
        "model": "F110-GE-129", 
        "capabilities": {"thrust": 13000, "fuel_efficiency": 0.8, "type": "jet"}, 
        "reliability": {"mtbf": 35, "mttr": 8}
    },
    "radar": {
        "model": "AN/APG-68(V)9",
        "capabilities": {
            "air": (True, {"tracking_range": 150, "acquisition_range": 70, "engagement_range": 70, "multi_target_capacity": 10}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 40, "engagement_range": 30, "multi_target_capacity": 5}),
            "sea": (True, {"tracking_range": 50, "acquisition_range": 30, "engagement_range": 30, "multi_target_capacity": 3})    
        },
        "reliability": {"mtbf": 65, "mttr": 6},
        "type": "pulse-doppler"
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (True, {"tracking_range": 100, "acquisition_range": 120, "engagement_range": 100, "multi_target_capacity": 5}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 4}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0})        
        },
        "reliability": {"mtbf": 55, "mttr": 5},
        "type": "thermal and optical"
    },
    "radio_nav": {
        "model": "AN/ARN-118", 
        "capabilities": {"navigation_accuracy": 0.5, "communication_range": 200},
        "reliability": {"mtbf": 60, "mttr": 4.5}
        },
    "avionics": {
        "model": "AN/ALR-69A",
        "capabilities": {"flight_control": 0.9, "navigation_system": 0.8, "communication_system": 0.85},
        "reliability": {"mtbf": 80, "mttr": 3.2}
    },
    "hydraulic": {
        "model": "Generic Hydraulic System",
        "capabilities": {"pressure": 3000, "fluid_capacity": 50},
        "reliability": {"mtbf": 100, "mttr": 1.0},
    },
    "speed_data": {
        "sustained": {"metric": "imperial", "type_speed": "indicated_airspeed", "airspeed": 350, "altitude": 29000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 2700, "time": 120},  # time in minutes
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 4900, "time": 120}  # time in minutes   
    },
}

f14_data_example = {
    "constructor": "Grumman",
    "made": "USA",
    "model": "F-14A Tomcat",
    "start_service": 1978,
    "end_service": None,
    "category": "fighter",
    "cost": 10,
    "roles": ["CAP", "Intercept", "SEAD"],
    "engine": {
        "model": "TF30-P-414A", 
        "capabilities": {"thrust": 20000, "fuel_efficiency": 0.7, "type": "jet"}, 
        "reliability": {"mtbf": 30, "mttr": 10}
    },
    "radar": {
        "model": "AN/AWG-9",
        "capabilities": {
            "air": (True, {"tracking_range": 185, "acquisition_range": 120, "engagement_range": 120, "multi_target_capacity": 20}),
            "ground": (False, {"tracking_range": 100, "acquisition_range": 120, "engagement_range": 100, "multi_target_capacity": 10}),
            "sea": (False, {"tracking_range": 70, "acquisition_range": 80, "engagement_range": 70, "multi_target_capacity": 5})            
        },
        "reliability": {"mtbf": 43, "mttr": 8},
        "type": "pulse-doppler"
    },
    "TVD": {
        "model": "AN/AAX-1 TCS",
        "capabilities": {
            "air": (True, {"tracking_range": 150, "acquisition_range": 180, "engagement_range": 150, "multi_target_capacity": 10}),
            "ground": (True, {"tracking_range": 100, "acquisition_range": 120, "engagement_range": 100, "multi_target_capacity": 8}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0})        
        },
        "reliability": {"mtbf": 36, "mttr": 8},
        "type": "thermal and optical"
    },
    "radio_nav": {
        "model": "AN/ARN-92", 
        "capabilities": {"navigation_accuracy": 0.6, "communication_range": 250},
        "reliability": {"mtbf": 50, "mttr": 2}
        },
    "avionics": {
        "model": "AN/ALR-45",
        "capabilities": {"flight_control": 0.85, "navigation_system": 0.75, "communication_system": 0.8},
        "reliability": {"mtbf": 45, "mttr": 6}
    },
    "hydraulic": {
        "model": "Generic Hydraulic System",
        "capabilities": {"pressure": 3000, "fluid_capacity": 50},
        "reliability": {"mtbf": 105, "mttr": 12},
    },
    "speed_data": {
        "sustained": {"metric": "imperial", "type_speed": "indicated_airspeed", "airspeed": 540, "altitude": 30000, "consume": 1300},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2485, "altitude": 12200, "consume": 2600, "time": 120},  # time in minutes
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2485, "altitude": 12200, "consume": 4800, "time": 120}  # time in minutes   
    },
    
}

f15_data_example = {
    "constructor": "McDonnell Douglas",
    "made": "USA",
    "model": "F-15C Eagle",
    "start_service": 1978,
    "end_service": None,
    "category": "fighter",
    "cost": 10,
    "roles": ["CAP", "Intercept", "SEAD"],
    "engine": {
        "model": "F100-PW-220", 
        "capabilities": {"thrust": 15000, "fuel_efficiency": 0.75, "type": "jet"}, 
        "reliability": {"mtbf": 60, "mttr": 12}
    },
    "radar": {
        "model": "AN/APG-63(V)1",
        "capabilities": {
            "air": (True, {"tracking_range": 170, "acquisition_range": 80, "engagement_range": 60, "multi_target_capacity": 15}),
            "ground": (True, {"tracking_range": 90, "acquisition_range": 110, "engagement_range": 90, "multi_target_capacity": 7}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0})            
        },
        "reliability": {"mtbf": 45, "mttr": 7},
        "type": "pulse-doppler"
    },
    "TVD": {
        "model": "AN/AAQ-13 LANTIRN",
        "capabilities": {
            "air": (True, {"tracking_range": 120, "acquisition_range": 140, "engagement_range": 120, "multi_target_capacity": 6}),
            "ground": (True, {"tracking_range": 90, "acquisition_range": 110, "engagement_range": 90, "multi_target_capacity": 5}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0})            
        },
        "reliability": {"mtbf": 40, "mttr": 10},
        "type": 'thermal and optical'
    },
    "radio_nav": {
        "model": "AN/ARN-118", 
        "capabilities": {"navigation_accuracy": 0.5, "communication_range": 200},
        "reliability": {"mtbf": 38, "mttr": 4}
        },
    "avionics": {
        "model": "AN/ALR-56C",
        "capabilities": {"flight_control": 0.9, "navigation_system": 0.85, "communication_system": 0.9},
        "reliability": {"mtbf": 45, "mttr": 9}
    },
    "hydraulic": {
        "model": "Generic Hydraulic System",
        "capabilities": {"pressure": 3000, "fluid_capacity": 50},
        "reliability": {"mtbf": 58, "mttr": 8},
    },
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2650, "altitude": 11000, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2650, "altitude": 11000, "consume": 2800, "time": 120},  # time in minutes
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2650, "altitude": 11000, "consume": 5000, "time": 120}  # time in minutes   
    },
   
}



# SETUP DICTIONARY VALUE 
SCORES = ('Radar score', 'Radar score air', 'Speed score', 'avalaibility', 'manutenability score (mttr)', 'reliability score (mtbf)')
AIRCRAFT = {}


Aircraft_Data(**f16_data_example)
Aircraft_Data(**f18_data_example)
Aircraft_Data(**f14_data_example)
Aircraft_Data(**f15_data_example)

for aircraft in Aircraft_Data._registry.values():    
    model = aircraft.model
    AIRCRAFT[model] = {}
    AIRCRAFT[model]['Radar score'] = aircraft.get_normalized_radar_score() 
    AIRCRAFT[model]['Radar score air'] = aircraft.get_normalized_radar_score(['air']) 
    AIRCRAFT[model]['Speed score'] = aircraft.get_normalized_speed_score() 
    AIRCRAFT[model]['avalaibility'] = aircraft.get_normalized_avalaiability_score()
    AIRCRAFT[model]['manutenability score (mttr)'] = aircraft.get_normalized_maintenance_score()
    AIRCRAFT[model]['reliability score (mtbf)'] = aircraft.get_normalized_reliability_score()

# STATIC METHODS (API)
def get_aircraft_data(model: str):
    return AIRCRAFT

def get_aircraft_scores(model: str, scores: Optional[List]=None):

    if model not in AIRCRAFT.keys():
        raise ValueError(f"model unknow. model must be: {AIRCRAFT.keys()}")
    
    if scores and scores in SCORES:
        raise ValueError(f"scores unknow. scores must be: {SCORES!r}")
    
    results = {}
    for score in scores:
        results[score] = AIRCRAFT[model][score]

    return results

#TEST
for model, data in AIRCRAFT.items():
    for name, score in data.items():
        print(f"{model} {name}: {score:.2f}")
    

print(f"F-14 Speed score and avalaibility: {get_aircraft_scores(model = 'F-14A Tomcat', scores = ['Speed score', 'avalaibility'])}" )
    


    
    