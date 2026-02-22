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
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import loadout_eval, loadout_target_effectiveness
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft_Data').logger

AIRCRAFT_ROLE = AIR_MILITARY_CRAFT_ASSET.keys()
AIRCRAFT_TASK = AIR_TASK

SYSTEM_WEIGHTS = {

    "radar_weights": {
            'tracking_range': 0.2 / 400, # weights / reference distance (km)
            'acquisition_range': 0.1 / 200,
            'engagement_range': 0.3 / 100,
            'multi_target': 0.4 / 5 # weights / reference multi targets
    },

    "tvd_weights": {
            'tracking_range': 0.2 / 130, # weights / reference distance (km)
            'acquisition_range': 0.1 / 130,
            'engagement_range': 0.3 / 100,
            'multi_target': 0.4 / 1, # weights / reference multi targets
    },
    "speed_weights": {
        'sustained': 0.2,
        'combat': 0.4,
        'emergency': 0.3
    }
}

@dataclass
class Aircraft_Data:
    _registry = {}
        
    def __init__(self, constructor: str, users: List, made: str, model: str, start_service: str, end_service: str, category: str, cost: int, roles: str, manouvrability: float, resilience: float, engine: Dict, radar: Dict, TVD: Dict, radio_nav: Dict, avionics: Dict, hydraulic: Dict, speed_data: Dict):
        self.constructor = constructor
        self.users = users
        self.made = made
        self.model = model
        self.start_service = start_service
        self.end_service = end_service
        self.category = category
        self.cost = cost
        self.roles = roles
        self.manouvrability = manouvrability
        self.resilience = resilience
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
        
        score = 0.0
        
        for m in modes:
            cap = self.radar['capabilities'][m]
            if cap[0]: 
                score += cap[1].get('tracking_range', 0) * SYSTEM_WEIGHTS["radar_weights"].get('tracking_range', 0)
                score += cap[1].get('acquisition_range', 0) * SYSTEM_WEIGHTS["radar_weights"].get('acquisition_range', 0)
                score += cap[1].get('engagement_range', 0) * SYSTEM_WEIGHTS["radar_weights"].get('engagement_range', 0)
                score += cap[1].get('multi_target_capacity', 0) * SYSTEM_WEIGHTS["radar_weights"].get('multi_target', 0)
        
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
        
        score = 0.0
        
        for m in modes:
            cap = self.TVD['capabilities'][m]
            if cap[0]: 
                score += cap[1].get('tracking_range', 0) * SYSTEM_WEIGHTS["tvd_weights"].get('tracking_range', 0)
                score += cap[1].get('acquisition_range', 0) * SYSTEM_WEIGHTS["tvd_weights"].get('acquisition_range', 0)
                score += cap[1].get('engagement_range', 0) * SYSTEM_WEIGHTS["tvd_weights"].get('engagement_range', 0)
                score += cap[1].get('multi_target_capacity', 0) * SYSTEM_WEIGHTS["tvd_weights"].get('multi_target', 0)
        
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

        score = 0

        for speed_type, weight in SYSTEM_WEIGHTS["speed_weights"].items():
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

    def _loadout_eval(self, loadout: str) -> float: # questo lo usi per verificare come l'aereo performa per la missione senza considerare la tipologia del target
        """Returns the score of installed loadout

        Returns:
            float: weapons combat score
        """
        
        return loadout_eval(aircraft_name = self.model, loadout_name = loadout)

    def _loadout_target_effectiveness(self, loadout: str, target_type: List, target_dimension: List) -> float: # questo lo usi per valutare l'efficacia del loadout sul target specifico, considerando le caratteristiche del target e confrontandole con quelle del loadout
        """Returns the score of installed loadout against a specific target

        Returns:
            float: weapons combat score against the target
        """
        
        return loadout_target_effectiveness(aircraft_name = self.model, loadout_name = loadout, target_type = target_type, target_dimension = target_dimension)
    


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
    "constructor": "General Dynamics", "made": "USA", "model": "F-16A Fighting Falcon",
    "users": ["USA", "Belgium", "Netherlands", "Denmark", "Norway", "Pakistan"], "start_service": 1978, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 6,
    "roles": ["CAP", "Intercept", "Strike", "SEAD"],
    "manouvrability": 0.82, "resilience": 0.68,
    "engine": {"model": "F100-PW-200", "capabilities": {"thrust": 10800, "fuel_efficiency": 0.73, "type": "turbofan"}, "reliability": {"mtbf": 38, "mttr": 6}},
    "radar": {
        "model": "AN/APG-66",
        "capabilities": {
            "air": (True, {"tracking_range": 130, "acquisition_range": 65, "engagement_range": 46, "multi_target_capacity": 4}),
            "ground": (True, {"tracking_range": 70, "acquisition_range": 45, "engagement_range": 15, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 45, "mttr": 5}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "AN/ARN-108", "capabilities": {"navigation_system": 0.75, "communication_system": 0.78, "communication_range": 200}, "reliability": {"mtbf": 55, "mttr": 2}},
    "avionics": {"model": "AN/ALR-69", "capabilities": {"flight_control": 0.82, "countermeasures": 0.62, "self_defense": 0.56}, "reliability": {"mtbf": 38, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 88, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 10000, "consume": 1100},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 12200, "consume": 2300, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 12200, "consume": 4200, "time": 60},
    },
}

# ==================== US FIGHTERS ====================

f14a_data = {
    "constructor": "Grumman", "made": "USA", "model": "F-14A Tomcat",
    "users": ["USA", "Iran"], "start_service": 1974, "end_service": 2006,
    "category": [Air_Asset_Type.FIGHTER], "cost": 38,
    "roles": ["CAP", "Intercept", "Escort"],
    "manouvrability": 0.72, "resilience": 0.72,
    "engine": {"model": "TF30-P-414A", "capabilities": {"thrust": 19000, "fuel_efficiency": 0.62, "type": "turbofan"}, "reliability": {"mtbf": 28, "mttr": 10}},
    "radar": {
        "model": "AN/AWG-9",
        "capabilities": {
            "air": (True, {"tracking_range": 315, "acquisition_range": 185, "engagement_range": 185, "multi_target_capacity": 24}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 180, "acquisition_range": 130, "engagement_range": 0, "multi_target_capacity": 6}),
        },
        "reliability": {"mtbf": 35, "mttr": 8}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAX-1 TCS",
        "capabilities": {
            "air": (True, {"tracking_range": 110, "acquisition_range": 130, "engagement_range": 100, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 6}, "type": "optical",
    },
    "radio_nav": {"model": "AN/ARN-84", "capabilities": {"navigation_system": 0.72, "communication_system": 0.75, "communication_range": 250}, "reliability": {"mtbf": 50, "mttr": 2.5}},
    "avionics": {"model": "AN/ALR-45", "capabilities": {"flight_control": 0.75, "countermeasures": 0.60, "self_defense": 0.55}, "reliability": {"mtbf": 38, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 75}, "reliability": {"mtbf": 85, "mttr": 8}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 10000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2485, "altitude": 15200, "consume": 3200, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2485, "altitude": 15200, "consume": 5500, "time": 60},
    },
}

f14b_data = {
    "constructor": "Grumman", "made": "USA", "model": "F-14B Tomcat",
    "users": ["USA"], "start_service": 1991, "end_service": 2006,
    "category": [Air_Asset_Type.FIGHTER], "cost": 43,
    "roles": ["CAP", "Intercept", "Escort", "Strike"],
    "manouvrability": 0.75, "resilience": 0.73,
    "engine": {"model": "F110-GE-400", "capabilities": {"thrust": 24000, "fuel_efficiency": 0.72, "type": "turbofan"}, "reliability": {"mtbf": 40, "mttr": 7}},
    "radar": {
        "model": "AN/AWG-9 (upgraded)",
        "capabilities": {
            "air": (True, {"tracking_range": 315, "acquisition_range": 185, "engagement_range": 185, "multi_target_capacity": 24}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 180, "acquisition_range": 130, "engagement_range": 0, "multi_target_capacity": 6}),
        },
        "reliability": {"mtbf": 38, "mttr": 7}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAX-1 TCS",
        "capabilities": {
            "air": (True, {"tracking_range": 110, "acquisition_range": 130, "engagement_range": 100, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 32, "mttr": 5}, "type": "optical",
    },
    "radio_nav": {"model": "AN/ARN-84", "capabilities": {"navigation_system": 0.75, "communication_system": 0.78, "communication_range": 250}, "reliability": {"mtbf": 52, "mttr": 2.5}},
    "avionics": {"model": "AN/ALR-67", "capabilities": {"flight_control": 0.78, "countermeasures": 0.65, "self_defense": 0.60}, "reliability": {"mtbf": 42, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 75}, "reliability": {"mtbf": 90, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1050, "altitude": 10000, "consume": 1300},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2485, "altitude": 15200, "consume": 3000, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2485, "altitude": 15200, "consume": 5200, "time": 60},
    },
}

f15c_data = {
    "constructor": "McDonnell Douglas", "made": "USA", "model": "F-15C Eagle",
    "users": ["USA", "Israel", "Saudi Arabia", "Japan"], "start_service": 1979, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 28,
    "roles": ["CAP", "Intercept", "Fighter_Sweep", "Escort"],
    "manouvrability": 0.85, "resilience": 0.80,
    "engine": {"model": "F100-PW-220", "capabilities": {"thrust": 21500, "fuel_efficiency": 0.75, "type": "turbofan"}, "reliability": {"mtbf": 55, "mttr": 8}},
    "radar": {
        "model": "AN/APG-63(V)1",
        "capabilities": {
            "air": (True, {"tracking_range": 185, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 8}),
            "ground": (True, {"tracking_range": 90, "acquisition_range": 60, "engagement_range": 20, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 50, "mttr": 6}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-13 LANTIRN (nav pod)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 30, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 5}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.82, "communication_system": 0.85, "communication_range": 300}, "reliability": {"mtbf": 60, "mttr": 2}},
    "avionics": {"model": "AN/ALR-56C", "capabilities": {"flight_control": 0.88, "countermeasures": 0.72, "self_defense": 0.65}, "reliability": {"mtbf": 45, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 95, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1050, "altitude": 10000, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2655, "altitude": 15200, "consume": 3500, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2655, "altitude": 15200, "consume": 6000, "time": 60},
    },
}

f15e_data = {
    "constructor": "McDonnell Douglas", "made": "USA", "model": "F-15E Strike Eagle",
    "users": ["USA", "Saudi Arabia", "Israel", "South Korea", "Singapore"], "start_service": 1989, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 31,
    "roles": ["CAP", "Strike", "Pinpoint_Strike", "SEAD"],
    "manouvrability": 0.82, "resilience": 0.80,
    "engine": {"model": "F100-PW-229", "capabilities": {"thrust": 26000, "fuel_efficiency": 0.77, "type": "turbofan"}, "reliability": {"mtbf": 58, "mttr": 7}},
    "radar": {
        "model": "AN/APG-70",
        "capabilities": {
            "air": (True, {"tracking_range": 185, "acquisition_range": 110, "engagement_range": 90, "multi_target_capacity": 8}),
            "ground": (True, {"tracking_range": 120, "acquisition_range": 90, "engagement_range": 40, "multi_target_capacity": 4}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 55, "mttr": 5}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-14 LANTIRN",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 42, "mttr": 4}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.85, "communication_system": 0.87, "communication_range": 300}, "reliability": {"mtbf": 62, "mttr": 2}},
    "avionics": {"model": "AN/ALR-56C", "capabilities": {"flight_control": 0.88, "countermeasures": 0.75, "self_defense": 0.68}, "reliability": {"mtbf": 48, "mttr": 3.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 95, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 980, "altitude": 10000, "consume": 1800},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2655, "altitude": 15200, "consume": 3800, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2655, "altitude": 15200, "consume": 6500, "time": 60},
    },
}

fa18a_data = {
    "constructor": "McDonnell Douglas", "made": "USA", "model": "F/A-18A Hornet",
    "users": ["USA", "Australia", "Canada", "Spain", "Kuwait"], "start_service": 1983, "end_service": 2020,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 24,
    "roles": ["CAP", "Intercept", "Strike", "CAS", "Anti_Ship"],
    "manouvrability": 0.80, "resilience": 0.73,
    "engine": {"model": "F404-GE-400", "capabilities": {"thrust": 14500, "fuel_efficiency": 0.73, "type": "turbofan"}, "reliability": {"mtbf": 42, "mttr": 6}},
    "radar": {
        "model": "AN/APG-65",
        "capabilities": {
            "air": (True, {"tracking_range": 150, "acquisition_range": 80, "engagement_range": 60, "multi_target_capacity": 8}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 50, "engagement_range": 20, "multi_target_capacity": 2}),
            "sea": (True, {"tracking_range": 100, "acquisition_range": 70, "engagement_range": 0, "multi_target_capacity": 3}),
        },
        "reliability": {"mtbf": 48, "mttr": 5}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAS-38 NITE Hawk",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 60, "acquisition_range": 80, "engagement_range": 60, "multi_target_capacity": 2}),
            "sea": (True, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 40, "multi_target_capacity": 1}),
        },
        "reliability": {"mtbf": 38, "mttr": 5}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.80, "communication_system": 0.82, "communication_range": 250}, "reliability": {"mtbf": 58, "mttr": 2}},
    "avionics": {"model": "AN/ALR-67", "capabilities": {"flight_control": 0.82, "countermeasures": 0.70, "self_defense": 0.65}, "reliability": {"mtbf": 45, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 60}, "reliability": {"mtbf": 88, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 2800, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 5000, "time": 60},
    },
}

fa18c_data = {
    "constructor": "McDonnell Douglas", "made": "USA", "model": "F/A-18C Hornet",
    "users": ["USA", "Finland", "Switzerland", "Malaysia", "Kuwait"], "start_service": 1987, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 29,
    "roles": ["CAP", "Intercept", "Strike", "SEAD", "Anti_Ship"],
    "manouvrability": 0.82, "resilience": 0.74,
    "engine": {"model": "F404-GE-402", "capabilities": {"thrust": 16000, "fuel_efficiency": 0.75, "type": "turbofan"}, "reliability": {"mtbf": 45, "mttr": 5}},
    "radar": {
        "model": "AN/APG-73",
        "capabilities": {
            "air": (True, {"tracking_range": 160, "acquisition_range": 90, "engagement_range": 70, "multi_target_capacity": 10}),
            "ground": (True, {"tracking_range": 90, "acquisition_range": 60, "engagement_range": 25, "multi_target_capacity": 3}),
            "sea": (True, {"tracking_range": 110, "acquisition_range": 80, "engagement_range": 0, "multi_target_capacity": 4}),
        },
        "reliability": {"mtbf": 52, "mttr": 4}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (True, {"tracking_range": 90, "acquisition_range": 110, "engagement_range": 90, "multi_target_capacity": 4}),
            "ground": (True, {"tracking_range": 75, "acquisition_range": 95, "engagement_range": 75, "multi_target_capacity": 3}),
            "sea": (True, {"tracking_range": 60, "acquisition_range": 70, "engagement_range": 50, "multi_target_capacity": 2}),
        },
        "reliability": {"mtbf": 40, "mttr": 4}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.83, "communication_system": 0.85, "communication_range": 250}, "reliability": {"mtbf": 60, "mttr": 2}},
    "avionics": {"model": "AN/ALR-67(V)2", "capabilities": {"flight_control": 0.85, "countermeasures": 0.73, "self_defense": 0.67}, "reliability": {"mtbf": 48, "mttr": 3.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 60}, "reliability": {"mtbf": 90, "mttr": 5.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 920, "altitude": 10000, "consume": 1350},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 2700, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 4900, "time": 60},
    },
}

fa18c_lot20_data = {
    "constructor": "McDonnell Douglas", "made": "USA", "model": "F/A-18C Lot 20",
    "users": ["USA", "Switzerland"], "start_service": 1998, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 33,
    "roles": ["CAP", "Intercept", "Strike", "Pinpoint_Strike", "SEAD", "Anti_Ship"],
    "manouvrability": 0.83, "resilience": 0.75,
    "engine": {"model": "F404-GE-402", "capabilities": {"thrust": 16000, "fuel_efficiency": 0.75, "type": "turbofan"}, "reliability": {"mtbf": 46, "mttr": 5}},
    "radar": {
        "model": "AN/APG-73",
        "capabilities": {
            "air": (True, {"tracking_range": 165, "acquisition_range": 95, "engagement_range": 75, "multi_target_capacity": 10}),
            "ground": (True, {"tracking_range": 95, "acquisition_range": 65, "engagement_range": 28, "multi_target_capacity": 4}),
            "sea": (True, {"tracking_range": 115, "acquisition_range": 85, "engagement_range": 0, "multi_target_capacity": 4}),
        },
        "reliability": {"mtbf": 54, "mttr": 4}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (True, {"tracking_range": 95, "acquisition_range": 115, "engagement_range": 95, "multi_target_capacity": 5}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 4}),
            "sea": (True, {"tracking_range": 65, "acquisition_range": 75, "engagement_range": 55, "multi_target_capacity": 2}),
        },
        "reliability": {"mtbf": 42, "mttr": 3.5}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.85, "communication_system": 0.87, "communication_range": 260}, "reliability": {"mtbf": 62, "mttr": 1.8}},
    "avionics": {"model": "AN/ALR-67(V)3", "capabilities": {"flight_control": 0.87, "countermeasures": 0.76, "self_defense": 0.70}, "reliability": {"mtbf": 50, "mttr": 3}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 60}, "reliability": {"mtbf": 92, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 930, "altitude": 10000, "consume": 1350},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 2700, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1915, "altitude": 12200, "consume": 4900, "time": 60},
    },
}

f4e_data = {
    "constructor": "McDonnell Douglas", "made": "USA", "model": "F-4E Phantom II",
    "users": ["USA", "Israel", "Turkey", "Greece", "Germany"], "start_service": 1961, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER_BOMBER], "cost": 18,
    "roles": ["CAP", "Strike", "CAS"],
    "manouvrability": 0.55, "resilience": 0.75,
    "engine": {"model": "J79-GE-17", "capabilities": {"thrust": 16200, "fuel_efficiency": 0.58, "type": "turbojet"}, "reliability": {"mtbf": 35, "mttr": 9}},
    "radar": {
        "model": "AN/APQ-120",
        "capabilities": {
            "air": (True, {"tracking_range": 100, "acquisition_range": 55, "engagement_range": 40, "multi_target_capacity": 2}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 8}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AVQ-26 Pave Tack",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 40, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 28, "mttr": 7}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-101", "capabilities": {"navigation_system": 0.62, "communication_system": 0.65, "communication_range": 200}, "reliability": {"mtbf": 42, "mttr": 3}},
    "avionics": {"model": "AN/ALR-46", "capabilities": {"flight_control": 0.60, "countermeasures": 0.50, "self_defense": 0.45}, "reliability": {"mtbf": 32, "mttr": 6}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 65}, "reliability": {"mtbf": 80, "mttr": 9}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 11000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2370, "altitude": 12200, "consume": 4500, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2370, "altitude": 12200, "consume": 7500, "time": 60},
    },
}

f5e_data = {
    "constructor": "Northrop", "made": "USA", "model": "F-5E Tiger II",
    "users": ["USA", "Taiwan", "South Korea", "Iran", "Saudi Arabia", "Switzerland"], "start_service": 1972, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 2,
    "roles": ["CAP", "Intercept"],
    "manouvrability": 0.80, "resilience": 0.58,
    "engine": {"model": "J85-GE-21", "capabilities": {"thrust": 4500, "fuel_efficiency": 0.60, "type": "turbojet"}, "reliability": {"mtbf": 40, "mttr": 4}},
    "radar": {
        "model": "AN/APQ-159",
        "capabilities": {
            "air": (True, {"tracking_range": 55, "acquisition_range": 35, "engagement_range": 25, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 35, "mttr": 5}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.68, "communication_system": 0.70, "communication_range": 180}, "reliability": {"mtbf": 48, "mttr": 2}},
    "avionics": {"model": "AN/ALR-46", "capabilities": {"flight_control": 0.70, "countermeasures": 0.50, "self_defense": 0.45}, "reliability": {"mtbf": 38, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 35}, "reliability": {"mtbf": 90, "mttr": 4}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 800, "altitude": 10000, "consume": 800},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1741, "altitude": 11000, "consume": 1800, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1741, "altitude": 11000, "consume": 3200, "time": 60},
    },
}

f86e_data = {
    "constructor": "North American Aviation", "made": "USA", "model": "F-86E Sabre",
    "users": ["USA", "UK", "Canada", "Australia", "Norway"], "start_service": 1950, "end_service": 1975,
    "category": [Air_Asset_Type.FIGHTER], "cost": 0,
    "roles": ["CAP", "Intercept"],
    "manouvrability": 0.65, "resilience": 0.62,
    "engine": {"model": "J47-GE-27", "capabilities": {"thrust": 2700, "fuel_efficiency": 0.45, "type": "turbojet"}, "reliability": {"mtbf": 30, "mttr": 6}},
    "radar": {
        "model": "AN/APG-30",
        "capabilities": {
            "air": (True, {"tracking_range": 20, "acquisition_range": 12, "engagement_range": 8, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 22, "mttr": 8}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "AN/ARN-6", "capabilities": {"navigation_system": 0.45, "communication_system": 0.50, "communication_range": 100}, "reliability": {"mtbf": 30, "mttr": 3}},
    "avionics": {"model": "Generic 1950s avionics", "capabilities": {"flight_control": 0.45, "countermeasures": 0.10, "self_defense": 0.10}, "reliability": {"mtbf": 25, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 25}, "reliability": {"mtbf": 70, "mttr": 4}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 9000, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1105, "altitude": 9000, "consume": 2500, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1105, "altitude": 9000, "consume": 3500, "time": 20},
    },
}

f16a_data = {
    "constructor": "General Dynamics", "made": "USA", "model": "F-16A Fighting Falcon",
    "users": ["USA", "Belgium", "Netherlands", "Denmark", "Norway", "Pakistan"], "start_service": 1978, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 6,
    "roles": ["CAP", "Intercept", "Strike", "SEAD"],
    "manouvrability": 0.82, "resilience": 0.68,
    "engine": {"model": "F100-PW-200", "capabilities": {"thrust": 10800, "fuel_efficiency": 0.73, "type": "turbofan"}, "reliability": {"mtbf": 38, "mttr": 6}},
    "radar": {
        "model": "AN/APG-66",
        "capabilities": {
            "air": (True, {"tracking_range": 130, "acquisition_range": 65, "engagement_range": 46, "multi_target_capacity": 4}),
            "ground": (True, {"tracking_range": 70, "acquisition_range": 45, "engagement_range": 15, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 45, "mttr": 5}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "AN/ARN-108", "capabilities": {"navigation_system": 0.75, "communication_system": 0.78, "communication_range": 200}, "reliability": {"mtbf": 55, "mttr": 2}},
    "avionics": {"model": "AN/ALR-69", "capabilities": {"flight_control": 0.82, "countermeasures": 0.62, "self_defense": 0.56}, "reliability": {"mtbf": 38, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 88, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 10000, "consume": 1100},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 12200, "consume": 2300, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 12200, "consume": 4200, "time": 60},
    },
}

f16a_mlu_data = {
    "constructor": "Lockheed Martin", "made": "USA", "model": "F-16A MLU",
    "users": ["Belgium", "Netherlands", "Denmark", "Norway", "Portugal"], "start_service": 1998, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 11,
    "roles": ["CAP", "Intercept", "Strike", "SEAD"],
    "manouvrability": 0.83, "resilience": 0.68,
    "engine": {"model": "F100-PW-220E", "capabilities": {"thrust": 10900, "fuel_efficiency": 0.75, "type": "turbofan"}, "reliability": {"mtbf": 42, "mttr": 5}},
    "radar": {
        "model": "AN/APG-66(V)2A",
        "capabilities": {
            "air": (True, {"tracking_range": 140, "acquisition_range": 70, "engagement_range": 50, "multi_target_capacity": 6}),
            "ground": (True, {"tracking_range": 75, "acquisition_range": 50, "engagement_range": 18, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 50, "mttr": 4}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 70, "acquisition_range": 90, "engagement_range": 70, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 3.5}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.80, "communication_system": 0.82, "communication_range": 220}, "reliability": {"mtbf": 58, "mttr": 1.8}},
    "avionics": {"model": "AN/ALR-69A", "capabilities": {"flight_control": 0.85, "countermeasures": 0.67, "self_defense": 0.60}, "reliability": {"mtbf": 42, "mttr": 3.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 90, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 960, "altitude": 10000, "consume": 1100},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 12200, "consume": 2300, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 12200, "consume": 4200, "time": 60},
    },
}

f16c_bl52d_data = {
    "constructor": "Lockheed Martin", "made": "USA", "model": "F-16C Block 52d",
    "users": ["USA", "Turkey", "Greece", "Israel"], "start_service": 1991, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 18,
    "roles": ["CAP", "Strike", "Pinpoint_Strike", "SEAD"],
    "manouvrability": 0.80, "resilience": 0.70,
    "engine": {"model": "F110-GE-100", "capabilities": {"thrust": 13000, "fuel_efficiency": 0.78, "type": "turbofan"}, "reliability": {"mtbf": 40, "mttr": 5}},
    "radar": {
        "model": "AN/APG-68(V)5",
        "capabilities": {
            "air": (True, {"tracking_range": 150, "acquisition_range": 70, "engagement_range": 50, "multi_target_capacity": 6}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 55, "engagement_range": 20, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 55, "mttr": 4}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (True, {"tracking_range": 90, "acquisition_range": 110, "engagement_range": 90, "multi_target_capacity": 4}),
            "ground": (True, {"tracking_range": 75, "acquisition_range": 95, "engagement_range": 75, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 3}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.83, "communication_system": 0.85, "communication_range": 200}, "reliability": {"mtbf": 60, "mttr": 1.5}},
    "avionics": {"model": "AN/ALR-69A", "capabilities": {"flight_control": 0.88, "countermeasures": 0.68, "self_defense": 0.60}, "reliability": {"mtbf": 40, "mttr": 3.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 90, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 960, "altitude": 10000, "consume": 1150},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 2500, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 4500, "time": 60},
    },
}

f16cm_bl50_data = {
    "constructor": "Lockheed Martin", "made": "USA", "model": "F-16CM Block 50",
    "users": ["USA", "Israel", "South Korea"], "start_service": 1991, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 20,
    "roles": ["CAP", "Strike", "Pinpoint_Strike", "SEAD"],
    "manouvrability": 0.80, "resilience": 0.70,
    "engine": {"model": "F110-GE-129", "capabilities": {"thrust": 13400, "fuel_efficiency": 0.80, "type": "turbofan"}, "reliability": {"mtbf": 42, "mttr": 5}},
    "radar": {
        "model": "AN/APG-68(V)9",
        "capabilities": {
            "air": (True, {"tracking_range": 160, "acquisition_range": 70, "engagement_range": 50, "multi_target_capacity": 6}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 60, "engagement_range": 20, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 50, "multi_target_capacity": 3}),
        },
        "reliability": {"mtbf": 60, "mttr": 4}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "AN/AAQ-28 LITENING",
        "capabilities": {
            "air": (True, {"tracking_range": 100, "acquisition_range": 120, "engagement_range": 100, "multi_target_capacity": 5}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 4}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 3}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"navigation_system": 0.83, "communication_system": 0.85, "communication_range": 200}, "reliability": {"mtbf": 60, "mttr": 1.5}},
    "avionics": {"model": "AN/ALR-69A", "capabilities": {"flight_control": 0.90, "countermeasures": 0.70, "self_defense": 0.60}, "reliability": {"mtbf": 40, "mttr": 1.2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 90, "mttr": 1.0}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 970, "altitude": 12200, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 2500, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2414, "altitude": 12200, "consume": 4500, "time": 120},
    },
}

# ==================== US ATTACKERS ====================

a10a_data = {
    "constructor": "Fairchild Republic", "made": "USA", "model": "A-10A Thunderbolt II",
    "users": ["USA"], "start_service": 1977, "end_service": None,
    "category": [Air_Asset_Type.ATTACKER], "cost": 0,
    "roles": ["CAS"],
    "manouvrability": 0.50, "resilience": 0.88,
    "engine": {"model": "GE TF34-GE-100", "capabilities": {"thrust": 40200, "fuel_efficiency": 0.37, "type": "turbofan"}, "reliability": {"mtbf": 60, "mttr": 2.5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/APN-194", "capabilities": {"range": 400, "accuracy": 0.65}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "AN/ALR-69", "capabilities": {"flight_control": 0.60, "countermeasures": 0.70, "self_defense": 0.55}, "reliability": {"mtbf": 50, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 90, "mttr": 1.0}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 560, "altitude": 0, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 680, "altitude": 5000, "consume": 2200, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 705, "altitude": 5000, "consume": 3000, "time": 30},
    },
}

a10c_data = {
    "constructor": "Fairchild Republic", "made": "USA", "model": "A-10C Thunderbolt II",
    "users": ["USA"], "start_service": 2005, "end_service": None,
    "category": [Air_Asset_Type.ATTACKER], "cost": 0,
    "roles": ["CAS", "Strike", "Pinpoint_Strike"],
    "manouvrability": 0.52, "resilience": 0.88,
    "engine": {"model": "GE TF34-GE-100A", "capabilities": {"thrust": 40900, "fuel_efficiency": 0.38, "type": "turbofan"}, "reliability": {"mtbf": 65, "mttr": 2.2}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "LITENING AT",
        "capabilities": {"type": "thermal and optical", "resolution": 0.85, "range": 30},
        "reliability": {"mtbf": 200, "mttr": 3},
    },
    "radio_nav": {"model": "AN/APN-194", "capabilities": {"range": 400, "accuracy": 0.80}, "reliability": {"mtbf": 90, "mttr": 1.5}},
    "avionics": {"model": "AN/ALR-69A", "capabilities": {"flight_control": 0.75, "countermeasures": 0.80, "self_defense": 0.70}, "reliability": {"mtbf": 55, "mttr": 1.8}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 90, "mttr": 1.0}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 560, "altitude": 0, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 680, "altitude": 5000, "consume": 2200, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 705, "altitude": 5000, "consume": 3000, "time": 30},
    },
}

a10c2_data = {
    "constructor": "Fairchild Republic", "made": "USA", "model": "A-10C II Thunderbolt II",
    "users": ["USA"], "start_service": 2018, "end_service": None,
    "category": [Air_Asset_Type.ATTACKER], "cost": 0,
    "roles": ["CAS", "Strike", "Pinpoint_Strike"],
    "manouvrability": 0.53, "resilience": 0.88,
    "engine": {"model": "GE TF34-GE-100A", "capabilities": {"thrust": 40900, "fuel_efficiency": 0.38, "type": "turbofan"}, "reliability": {"mtbf": 65, "mttr": 2.2}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "Sniper ATP",
        "capabilities": {"type": "thermal and optical", "resolution": 0.92, "range": 40},
        "reliability": {"mtbf": 220, "mttr": 2.5},
    },
    "radio_nav": {"model": "AN/APN-194", "capabilities": {"range": 400, "accuracy": 0.88}, "reliability": {"mtbf": 90, "mttr": 1.5}},
    "avionics": {"model": "EGI/DVADR", "capabilities": {"flight_control": 0.82, "countermeasures": 0.85, "self_defense": 0.78}, "reliability": {"mtbf": 60, "mttr": 1.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 90, "mttr": 1.0}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 560, "altitude": 0, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 680, "altitude": 5000, "consume": 2200, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 705, "altitude": 5000, "consume": 3000, "time": 30},
    },
}

a20g_data = {
    "constructor": "Douglas", "made": "USA", "model": "A-20G Havoc",
    "users": ["USA", "UK", "USSR"], "start_service": 1941, "end_service": 1954,
    "category": [Air_Asset_Type.ATTACKER], "cost": 0,
    "roles": ["CAS", "Strike"],
    "manouvrability": 0.45, "resilience": 0.55,
    "engine": {"model": "Wright R-2600-23", "capabilities": {"thrust": 1700, "fuel_efficiency": 0.30, "type": "piston"}, "reliability": {"mtbf": 40, "mttr": 6}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-5", "capabilities": {"range": 200, "accuracy": 0.45}, "reliability": {"mtbf": 30, "mttr": 5}},
    "avionics": {"model": "Basic WWII", "capabilities": {"flight_control": 0.35, "countermeasures": 0.10, "self_defense": 0.15}, "reliability": {"mtbf": 25, "mttr": 6}},
    "hydraulic": {"model": "Basic Hydraulic", "capabilities": {"pressure": 1500, "fluid_capacity": 20}, "reliability": {"mtbf": 50, "mttr": 4}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 430, "altitude": 3000, "consume": 700},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 510, "altitude": 4500, "consume": 1100, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 545, "altitude": 4500, "consume": 1400, "time": 15},
    },
}

a4ec_data = {
    "constructor": "Douglas", "made": "USA", "model": "A-4E Skyhawk",
    "users": ["USA", "Israel", "Australia", "Singapore"], "start_service": 1956, "end_service": 1998,
    "category": [Air_Asset_Type.ATTACKER], "cost": 0,
    "roles": ["CAS", "Strike", "Anti_Ship"],
    "manouvrability": 0.70, "resilience": 0.62,
    "engine": {"model": "Pratt & Whitney J52-P-8A", "capabilities": {"thrust": 37800, "fuel_efficiency": 0.45, "type": "turbojet"}, "reliability": {"mtbf": 40, "mttr": 4}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/APN-141", "capabilities": {"range": 300, "accuracy": 0.60}, "reliability": {"mtbf": 50, "mttr": 3}},
    "avionics": {"model": "AN/ALR-45", "capabilities": {"flight_control": 0.60, "countermeasures": 0.50, "self_defense": 0.40}, "reliability": {"mtbf": 40, "mttr": 3}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 30}, "reliability": {"mtbf": 70, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 0, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1083, "altitude": 0, "consume": 2800, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1083, "altitude": 0, "consume": 3500, "time": 20},
    },
}

# ==================== US BOMBERS & MARITIME ====================

f117_data = {
    "constructor": "Lockheed", "made": "USA", "model": "F-117 Nighthawk",
    "users": ["USA"], "start_service": 1983, "end_service": 2008,
    "category": [Air_Asset_Type.BOMBER], "cost": 0,
    "roles": ["Pinpoint_Strike"],
    "manouvrability": 0.40, "resilience": 0.55,
    "engine": {"model": "GE F404-GE-F1D2", "capabilities": {"thrust": 48000, "fuel_efficiency": 0.40, "type": "turbofan"}, "reliability": {"mtbf": 50, "mttr": 3}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "DLIR/FLIR",
        "capabilities": {"type": "thermal and optical", "resolution": 0.85, "range": 20},
        "reliability": {"mtbf": 150, "mttr": 4},
    },
    "radio_nav": {"model": "AN/AAQ-27 FLIR", "capabilities": {"range": 350, "accuracy": 0.95}, "reliability": {"mtbf": 70, "mttr": 2}},
    "avionics": {"model": "Inertial Nav/GPS", "capabilities": {"flight_control": 0.85, "countermeasures": 0.60, "self_defense": 0.50}, "reliability": {"mtbf": 60, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 40}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 9000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1040, "altitude": 9000, "consume": 3500, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1040, "altitude": 9000, "consume": 4500, "time": 30},
    },
}

b1b_data = {
    "constructor": "Rockwell", "made": "USA", "model": "B-1B Lancer",
    "users": ["USA"], "start_service": 1986, "end_service": None,
    "category": [Air_Asset_Type.HEAVY_BOMBER], "cost": 0,
    "roles": ["Strike", "Pinpoint_Strike"],
    "manouvrability": 0.42, "resilience": 0.62,
    "engine": {"model": "GE F101-GE-102", "capabilities": {"thrust": 137000, "fuel_efficiency": 0.35, "type": "turbofan"}, "reliability": {"mtbf": 55, "mttr": 3}},
    "radar": {
        "model": "AN/APQ-164",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 180, "acquisition_range": 120, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 60, "mttr": 2.5}, "type": "passive",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/APN-218", "capabilities": {"range": 500, "accuracy": 0.90}, "reliability": {"mtbf": 70, "mttr": 2}},
    "avionics": {"model": "AN/ALQ-161", "capabilities": {"flight_control": 0.88, "countermeasures": 0.90, "self_defense": 0.85}, "reliability": {"mtbf": 55, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 100}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 12000, "consume": 8000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1448, "altitude": 1000, "consume": 18000, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1448, "altitude": 1000, "consume": 22000, "time": 20},
    },
}

b52h_data = {
    "constructor": "Boeing", "made": "USA", "model": "B-52H Stratofortress",
    "users": ["USA"], "start_service": 1961, "end_service": None,
    "category": [Air_Asset_Type.HEAVY_BOMBER], "cost": 0,
    "roles": ["Strike"],
    "manouvrability": 0.25, "resilience": 0.60,
    "engine": {"model": "Pratt & Whitney TF33-P-3/103", "capabilities": {"thrust": 75600, "fuel_efficiency": 0.32, "type": "turbofan"}, "reliability": {"mtbf": 60, "mttr": 3}},
    "radar": {
        "model": "AN/APQ-166",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 250, "acquisition_range": 180, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 200, "acquisition_range": 150, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 50, "mttr": 3}, "type": "passive",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/APN-218", "capabilities": {"range": 600, "accuracy": 0.85}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "AN/ALQ-172", "capabilities": {"flight_control": 0.80, "countermeasures": 0.85, "self_defense": 0.75}, "reliability": {"mtbf": 50, "mttr": 3}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 120}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 819, "altitude": 12200, "consume": 12000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1047, "altitude": 12200, "consume": 20000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1047, "altitude": 12200, "consume": 25000, "time": 30},
    },
}

s3b_data = {
    "constructor": "Lockheed", "made": "USA", "model": "S-3B Viking",
    "users": ["USA"], "start_service": 1974, "end_service": 2009,
    "category": [Air_Asset_Type.BOMBER], "cost": 0,
    "roles": ["Anti_Ship", "Recon"],
    "manouvrability": 0.48, "resilience": 0.55,
    "engine": {"model": "GE TF34-GE-2", "capabilities": {"thrust": 41300, "fuel_efficiency": 0.42, "type": "turbofan"}, "reliability": {"mtbf": 55, "mttr": 3}},
    "radar": {
        "model": "AN/APS-137",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 280, "acquisition_range": 220, "engagement_range": 0, "multi_target_capacity": 4}),
        },
        "reliability": {"mtbf": 60, "mttr": 2.5}, "type": "passive",
    },
    "TVD": {
        "model": "AN/AAS-44",
        "capabilities": {"type": "thermal and optical", "resolution": 0.78, "range": 25},
        "reliability": {"mtbf": 120, "mttr": 3},
    },
    "radio_nav": {"model": "AN/APN-200", "capabilities": {"range": 500, "accuracy": 0.85}, "reliability": {"mtbf": 70, "mttr": 2}},
    "avionics": {"model": "AN/ALR-76", "capabilities": {"flight_control": 0.78, "countermeasures": 0.70, "self_defense": 0.60}, "reliability": {"mtbf": 55, "mttr": 2.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 40}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 700, "altitude": 6000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 834, "altitude": 6000, "consume": 3500, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 834, "altitude": 6000, "consume": 4500, "time": 30},
    },
}

s3b_tanker_data = {
    "constructor": "Lockheed", "made": "USA", "model": "S-3B Viking Tanker",
    "users": ["USA"], "start_service": 1974, "end_service": 2009,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 0,
    "roles": [],
    "manouvrability": 0.45, "resilience": 0.55,
    "engine": {"model": "GE TF34-GE-2", "capabilities": {"thrust": 41300, "fuel_efficiency": 0.42, "type": "turbofan"}, "reliability": {"mtbf": 55, "mttr": 3}},
    "radar": {
        "model": "AN/APS-137",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 200, "acquisition_range": 150, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 60, "mttr": 2.5}, "type": "passive",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/APN-200", "capabilities": {"range": 500, "accuracy": 0.85}, "reliability": {"mtbf": 70, "mttr": 2}},
    "avionics": {"model": "AN/ALR-76", "capabilities": {"flight_control": 0.75, "countermeasures": 0.65, "self_defense": 0.55}, "reliability": {"mtbf": 55, "mttr": 2.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 40}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 700, "altitude": 6000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 834, "altitude": 6000, "consume": 3500, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 834, "altitude": 6000, "consume": 4500, "time": 30},
    },
}

# ==================== US AWACS & RECON ====================

e2d_data = {
    "constructor": "Northrop Grumman", "made": "USA", "model": "E-2D Advanced Hawkeye",
    "users": ["USA", "Japan", "France"], "start_service": 1964, "end_service": None,
    "category": [Air_Asset_Type.AWACS], "cost": 0,
    "roles": [],
    "manouvrability": 0.30, "resilience": 0.40,
    "engine": {"model": "Allison T56-A-427", "capabilities": {"thrust": 4900, "fuel_efficiency": 0.35, "type": "turboprop"}, "reliability": {"mtbf": 70, "mttr": 2}},
    "radar": {
        "model": "AN/APY-9",
        "capabilities": {
            "air": (True, {"tracking_range": 556, "acquisition_range": 556, "engagement_range": 0, "multi_target_capacity": 30}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 60, "mttr": 3}, "type": "AESA",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"range": 400, "accuracy": 0.90}, "reliability": {"mtbf": 80, "mttr": 1.5}},
    "avionics": {"model": "ACCS", "capabilities": {"flight_control": 0.80, "countermeasures": 0.50, "self_defense": 0.30}, "reliability": {"mtbf": 60, "mttr": 2.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 40}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 550, "altitude": 9400, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 648, "altitude": 9400, "consume": 2500, "time": 240},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 648, "altitude": 9400, "consume": 3000, "time": 60},
    },
}

e3a_data = {
    "constructor": "Boeing", "made": "USA", "model": "E-3A Sentry",
    "users": ["USA", "NATO", "UK", "France", "Saudi Arabia"], "start_service": 1977, "end_service": None,
    "category": [Air_Asset_Type.AWACS], "cost": 0,
    "roles": [],
    "manouvrability": 0.25, "resilience": 0.40,
    "engine": {"model": "Pratt & Whitney TF33-PW-100A", "capabilities": {"thrust": 93400, "fuel_efficiency": 0.33, "type": "turbofan"}, "reliability": {"mtbf": 65, "mttr": 2.5}},
    "radar": {
        "model": "AN/APY-2",
        "capabilities": {
            "air": (True, {"tracking_range": 400, "acquisition_range": 400, "engagement_range": 0, "multi_target_capacity": 24}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 55, "mttr": 3}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-120", "capabilities": {"range": 500, "accuracy": 0.90}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "AN/ASQ-137", "capabilities": {"flight_control": 0.82, "countermeasures": 0.55, "self_defense": 0.35}, "reliability": {"mtbf": 60, "mttr": 2.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 750, "altitude": 9000, "consume": 6000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 851, "altitude": 9000, "consume": 9000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 851, "altitude": 9000, "consume": 12000, "time": 60},
    },
}

mq1a_data = {
    "constructor": "General Atomics", "made": "USA", "model": "MQ-1 Predator",
    "users": ["USA", "Italy", "Morocco"], "start_service": 1995, "end_service": 2018,
    "category": [Air_Asset_Type.RECON], "cost": 0,
    "roles": ["Recon", "CAS"],
    "manouvrability": 0.20, "resilience": 0.20,
    "engine": {"model": "Rotax 914F", "capabilities": {"thrust": 75, "fuel_efficiency": 0.55, "type": "piston"}, "reliability": {"mtbf": 100, "mttr": 2}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "MTS-A",
        "capabilities": {"type": "thermal and optical", "resolution": 0.80, "range": 10},
        "reliability": {"mtbf": 200, "mttr": 2},
    },
    "radio_nav": {"model": "AN/APX-100", "capabilities": {"range": 300, "accuracy": 0.95}, "reliability": {"mtbf": 100, "mttr": 1}},
    "avionics": {"model": "Triplex fly-by-wire", "capabilities": {"flight_control": 0.75, "countermeasures": 0.20, "self_defense": 0.10}, "reliability": {"mtbf": 80, "mttr": 2}},
    "hydraulic": {"model": "none", "capabilities": {"pressure": 0, "fluid_capacity": 0}, "reliability": {"mtbf": 0, "mttr": 0}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 150, "altitude": 5000, "consume": 50},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 217, "altitude": 5000, "consume": 80, "time": 1440},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 217, "altitude": 5000, "consume": 90, "time": 120},
    },
}

mq9_data = {
    "constructor": "General Atomics", "made": "USA", "model": "MQ-9 Reaper",
    "users": ["USA", "UK", "Italy", "France", "Netherlands"], "start_service": 2007, "end_service": None,
    "category": [Air_Asset_Type.RECON], "cost": 0,
    "roles": ["Recon", "CAS", "Strike"],
    "manouvrability": 0.25, "resilience": 0.25,
    "engine": {"model": "Honeywell TPE331-10GD", "capabilities": {"thrust": 671, "fuel_efficiency": 0.52, "type": "turboprop"}, "reliability": {"mtbf": 110, "mttr": 2}},
    "radar": {
        "model": "AN/APY-8 Lynx",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 60, "acquisition_range": 50, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 90, "mttr": 2}, "type": "passive",
    },
    "TVD": {
        "model": "MTS-B",
        "capabilities": {"type": "thermal and optical", "resolution": 0.90, "range": 15},
        "reliability": {"mtbf": 220, "mttr": 2},
    },
    "radio_nav": {"model": "AN/APX-100", "capabilities": {"range": 400, "accuracy": 0.97}, "reliability": {"mtbf": 110, "mttr": 1}},
    "avionics": {"model": "Triplex fly-by-wire", "capabilities": {"flight_control": 0.80, "countermeasures": 0.30, "self_defense": 0.20}, "reliability": {"mtbf": 90, "mttr": 2}},
    "hydraulic": {"model": "none", "capabilities": {"pressure": 0, "fluid_capacity": 0}, "reliability": {"mtbf": 0, "mttr": 0}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 300, "altitude": 7600, "consume": 100},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 482, "altitude": 7600, "consume": 160, "time": 1080},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 482, "altitude": 7600, "consume": 200, "time": 120},
    },
}

# ==================== US TRANSPORT & TANKERS ====================

c130_data = {
    "constructor": "Lockheed", "made": "USA", "model": "C-130 Hercules",
    "users": ["USA", "UK", "many"], "start_service": 1956, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 0,
    "roles": [],
    "manouvrability": 0.35, "resilience": 0.55,
    "engine": {"model": "Allison T56-A-15", "capabilities": {"thrust": 4591, "fuel_efficiency": 0.35, "type": "turboprop"}, "reliability": {"mtbf": 75, "mttr": 2}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"range": 350, "accuracy": 0.80}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "Generic Transport", "capabilities": {"flight_control": 0.70, "countermeasures": 0.40, "self_defense": 0.25}, "reliability": {"mtbf": 70, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 60}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 540, "altitude": 6700, "consume": 3000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 643, "altitude": 6700, "consume": 4500, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 643, "altitude": 6700, "consume": 5500, "time": 60},
    },
}

c17a_data = {
    "constructor": "Boeing", "made": "USA", "model": "C-17A Globemaster III",
    "users": ["USA", "UK", "Canada", "Australia"], "start_service": 1995, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 0,
    "roles": [],
    "manouvrability": 0.30, "resilience": 0.50,
    "engine": {"model": "Pratt & Whitney F117-PW-100", "capabilities": {"thrust": 185000, "fuel_efficiency": 0.38, "type": "turbofan"}, "reliability": {"mtbf": 70, "mttr": 2}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"range": 400, "accuracy": 0.88}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "Advanced Transport Avionics", "capabilities": {"flight_control": 0.88, "countermeasures": 0.50, "self_defense": 0.35}, "reliability": {"mtbf": 70, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 100}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 750, "altitude": 10000, "consume": 8000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 833, "altitude": 10000, "consume": 11000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 833, "altitude": 10000, "consume": 14000, "time": 60},
    },
}

kc130_data = {
    "constructor": "Lockheed Martin", "made": "USA", "model": "KC-130",
    "users": ["USA", "many"], "start_service": 1962, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 0,
    "roles": [],
    "manouvrability": 0.32, "resilience": 0.55,
    "engine": {"model": "Allison T56-A-16", "capabilities": {"thrust": 4591, "fuel_efficiency": 0.35, "type": "turboprop"}, "reliability": {"mtbf": 75, "mttr": 2}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"range": 350, "accuracy": 0.80}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "Generic Transport", "capabilities": {"flight_control": 0.70, "countermeasures": 0.40, "self_defense": 0.25}, "reliability": {"mtbf": 70, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 60}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 540, "altitude": 6700, "consume": 3200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 643, "altitude": 6700, "consume": 4700, "time": 360},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 643, "altitude": 6700, "consume": 5700, "time": 60},
    },
}

kc135_data = {
    "constructor": "Boeing", "made": "USA", "model": "KC-135 Stratotanker",
    "users": ["USA", "France", "Turkey", "Singapore"], "start_service": 1957, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 0,
    "roles": [],
    "manouvrability": 0.28, "resilience": 0.50,
    "engine": {"model": "CFM International CFM56-2B-1", "capabilities": {"thrust": 97900, "fuel_efficiency": 0.38, "type": "turbofan"}, "reliability": {"mtbf": 70, "mttr": 2.5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"range": 450, "accuracy": 0.85}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "Generic Transport", "capabilities": {"flight_control": 0.78, "countermeasures": 0.45, "self_defense": 0.30}, "reliability": {"mtbf": 70, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10700, "consume": 5500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 933, "altitude": 10700, "consume": 8000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 933, "altitude": 10700, "consume": 10000, "time": 60},
    },
}

kc135_mprs_data = {
    "constructor": "Boeing", "made": "USA", "model": "KC-135 MPRS",
    "users": ["USA"], "start_service": 1985, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 0,
    "roles": [],
    "manouvrability": 0.28, "resilience": 0.50,
    "engine": {"model": "CFM International CFM56-2B-1", "capabilities": {"thrust": 97900, "fuel_efficiency": 0.38, "type": "turbofan"}, "reliability": {"mtbf": 70, "mttr": 2.5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 0, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "AN/ARN-118", "capabilities": {"range": 450, "accuracy": 0.85}, "reliability": {"mtbf": 80, "mttr": 2}},
    "avionics": {"model": "MPRS Avionics", "capabilities": {"flight_control": 0.80, "countermeasures": 0.45, "self_defense": 0.30}, "reliability": {"mtbf": 72, "mttr": 2}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10700, "consume": 5500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 933, "altitude": 10700, "consume": 8000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 933, "altitude": 10700, "consume": 10000, "time": 60},
    },
}

# ==================== NATO/ALLIED AIRCRAFT ====================

asj37_data = {
    "constructor": "Saab", "made": "Sweden", "model": "AJ/ASJ 37 Viggen",
    "users": ["Sweden"], "start_service": 1971, "end_service": 2005,
    "category": [Air_Asset_Type.FIGHTER_BOMBER], "cost": 0,
    "roles": ["Strike", "CAS", "Fighter_Sweep", "CAP"],
    "manouvrability": 0.78, "resilience": 0.68,
    "engine": {"model": "Volvo Flygmotor RM8B", "capabilities": {"thrust": 125000, "fuel_efficiency": 0.40, "type": "turbofan"}, "reliability": {"mtbf": 45, "mttr": 3}},
    "radar": {
        "model": "Ericsson PS-46/A",
        "capabilities": {
            "air": (True, {"tracking_range": 60, "acquisition_range": 45, "engagement_range": 30, "multi_target_capacity": 1}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 60, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 35, "mttr": 4}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "Swedish TILS", "capabilities": {"range": 350, "accuracy": 0.80}, "reliability": {"mtbf": 55, "mttr": 3}},
    "avionics": {"model": "Swedish ECM suite", "capabilities": {"flight_control": 0.78, "countermeasures": 0.70, "self_defense": 0.65}, "reliability": {"mtbf": 40, "mttr": 3}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 80, "mttr": 2}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1100, "altitude": 11000, "consume": 3000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2231, "altitude": 11000, "consume": 8000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2231, "altitude": 11000, "consume": 12000, "time": 30},
    },
}

m2000c_data = {
    "constructor": "Dassault", "made": "France", "model": "Mirage 2000C",
    "users": ["France", "India", "Egypt", "UAE", "Greece", "Qatar", "Taiwan", "Peru"], "start_service": 1984, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 0,
    "roles": ["CAP", "Intercept", "Fighter_Sweep"],
    "manouvrability": 0.85, "resilience": 0.65,
    "engine": {"model": "SNECMA M53-P2", "capabilities": {"thrust": 95100, "fuel_efficiency": 0.42, "type": "turbofan"}, "reliability": {"mtbf": 45, "mttr": 3}},
    "radar": {
        "model": "Thomson-CSF RDI",
        "capabilities": {
            "air": (True, {"tracking_range": 100, "acquisition_range": 80, "engagement_range": 60, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 3}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {"type": "none", "resolution": 0, "range": 0},
        "reliability": {"mtbf": 0, "mttr": 0},
    },
    "radio_nav": {"model": "TACAN", "capabilities": {"range": 400, "accuracy": 0.85}, "reliability": {"mtbf": 60, "mttr": 2.5}},
    "avionics": {"model": "SERVAL ECM", "capabilities": {"flight_control": 0.85, "countermeasures": 0.72, "self_defense": 0.68}, "reliability": {"mtbf": 45, "mttr": 2.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 40}, "reliability": {"mtbf": 85, "mttr": 1.5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1100, "altitude": 11000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2338, "altitude": 11000, "consume": 7000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2338, "altitude": 11000, "consume": 10000, "time": 30},
    },
}

# ==================== SOVIET/RUSSIAN FIGHTERS ====================

mig15_data = {
    "constructor": "Mikoyan-Gurevich", "made": "USSR", "model": "MiG-15bis",
    "users": ["USSR", "China", "North Korea"], "start_service": 1949, "end_service": 1980,
    "category": [Air_Asset_Type.FIGHTER], "cost": 0,
    "roles": ["CAP", "Intercept"],
    "manouvrability": 0.68, "resilience": 0.62,
    "engine": {"model": "Klimov VK-1", "capabilities": {"thrust": 2700, "fuel_efficiency": 0.42, "type": "turbojet"}, "reliability": {"mtbf": 28, "mttr": 7}},
    "radar": {
        "model": "SRD-1 Bariy-M",
        "capabilities": {
            "air": (True, {"tracking_range": 15, "acquisition_range": 10, "engagement_range": 5, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 20, "mttr": 8}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSI-6K", "capabilities": {"navigation_system": 0.38, "communication_system": 0.42, "communication_range": 80}, "reliability": {"mtbf": 22, "mttr": 4}},
    "avionics": {"model": "Generic 1950s Soviet avionics", "capabilities": {"flight_control": 0.42, "countermeasures": 0.05, "self_defense": 0.05}, "reliability": {"mtbf": 20, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 20}, "reliability": {"mtbf": 65, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 8000, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1075, "altitude": 8000, "consume": 2200, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1075, "altitude": 8000, "consume": 3000, "time": 20},
    },
}

mig19p_data = {
    "constructor": "Mikoyan-Gurevich", "made": "USSR", "model": "MiG-19P",
    "users": ["USSR", "China"], "start_service": 1955, "end_service": 1980,
    "category": [Air_Asset_Type.FIGHTER], "cost": 0,
    "roles": ["CAP", "Intercept"],
    "manouvrability": 0.72, "resilience": 0.62,
    "engine": {"model": "Tumansky RD-9B", "capabilities": {"thrust": 6400, "fuel_efficiency": 0.48, "type": "turbojet"}, "reliability": {"mtbf": 28, "mttr": 7}},
    "radar": {
        "model": "RP-5 Izumrud",
        "capabilities": {
            "air": (True, {"tracking_range": 25, "acquisition_range": 15, "engagement_range": 10, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 22, "mttr": 8}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSIU-4V", "capabilities": {"navigation_system": 0.42, "communication_system": 0.45, "communication_range": 90}, "reliability": {"mtbf": 25, "mttr": 4}},
    "avionics": {"model": "Generic 1950s Soviet avionics", "capabilities": {"flight_control": 0.48, "countermeasures": 0.08, "self_defense": 0.08}, "reliability": {"mtbf": 22, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 25}, "reliability": {"mtbf": 68, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1452, "altitude": 10000, "consume": 3500, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1452, "altitude": 10000, "consume": 5000, "time": 20},
    },
}

mig21bis_data = {
    "constructor": "Mikoyan-Gurevich", "made": "USSR", "model": "MiG-21bis",
    "users": ["USSR", "Russia", "India", "Finland", "Algeria", "Vietnam"], "start_service": 1959, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 1,
    "roles": ["CAP", "Intercept", "Strike"],
    "manouvrability": 0.78, "resilience": 0.65,
    "engine": {"model": "Tumansky R-25-300", "capabilities": {"thrust": 9900, "fuel_efficiency": 0.52, "type": "turbojet"}, "reliability": {"mtbf": 32, "mttr": 6}},
    "radar": {
        "model": "RP-22 Sapfir-21",
        "capabilities": {
            "air": (True, {"tracking_range": 60, "acquisition_range": 35, "engagement_range": 25, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 28, "mttr": 7}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-5S", "capabilities": {"navigation_system": 0.55, "communication_system": 0.58, "communication_range": 130}, "reliability": {"mtbf": 32, "mttr": 4}},
    "avionics": {"model": "SPO-10 Sirena", "capabilities": {"flight_control": 0.60, "countermeasures": 0.35, "self_defense": 0.30}, "reliability": {"mtbf": 28, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 30}, "reliability": {"mtbf": 72, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2175, "altitude": 13000, "consume": 3500, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2175, "altitude": 13000, "consume": 6000, "time": 30},
    },
}

mig23mld_data = {
    "constructor": "Mikoyan", "made": "USSR", "model": "MiG-23MLD",
    "users": ["USSR", "Russia", "Syria", "Libya", "Algeria"], "start_service": 1983, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 6,
    "roles": ["CAP", "Strike", "CAS"],
    "manouvrability": 0.72, "resilience": 0.68,
    "engine": {"model": "Tumansky R-35-300", "capabilities": {"thrust": 13000, "fuel_efficiency": 0.55, "type": "turbojet"}, "reliability": {"mtbf": 32, "mttr": 7}},
    "radar": {
        "model": "Sapfir-23MLA-II",
        "capabilities": {
            "air": (True, {"tracking_range": 120, "acquisition_range": 65, "engagement_range": 45, "multi_target_capacity": 2}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 8}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.65, "communication_system": 0.68, "communication_range": 180}, "reliability": {"mtbf": 38, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.68, "countermeasures": 0.55, "self_defense": 0.48}, "reliability": {"mtbf": 32, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 78, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 1600},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2445, "altitude": 13000, "consume": 4000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2445, "altitude": 13000, "consume": 7000, "time": 30},
    },
}

mig25pd_data = {
    "constructor": "Mikoyan", "made": "USSR", "model": "MiG-25PD",
    "users": ["USSR", "Algeria", "Libya", "Iraq"], "start_service": 1978, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 8,
    "roles": ["Intercept", "CAP"],
    "manouvrability": 0.45, "resilience": 0.72,
    "engine": {"model": "Tumansky R-15BD-300", "capabilities": {"thrust": 22000, "fuel_efficiency": 0.42, "type": "turbojet"}, "reliability": {"mtbf": 25, "mttr": 10}},
    "radar": {
        "model": "Saphir-25 (RP-25)",
        "capabilities": {
            "air": (True, {"tracking_range": 120, "acquisition_range": 80, "engagement_range": 60, "multi_target_capacity": 2}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 28, "mttr": 10}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.68, "communication_system": 0.70, "communication_range": 200}, "reliability": {"mtbf": 38, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.60, "countermeasures": 0.48, "self_defense": 0.42}, "reliability": {"mtbf": 30, "mttr": 7}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 80, "mttr": 9}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 13000, "consume": 3500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 3000, "altitude": 20000, "consume": 8000, "time": 20},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 3000, "altitude": 20000, "consume": 12000, "time": 15},
    },
}

mig25rb_data = {
    "constructor": "Mikoyan", "made": "USSR", "model": "MiG-25RB",
    "users": ["USSR", "Russia"], "start_service": 1972, "end_service": None,
    "category": [Air_Asset_Type.RECON], "cost": 8,
    "roles": ["Recon"],
    "manouvrability": 0.43, "resilience": 0.70,
    "engine": {"model": "Tumansky R-15B-300", "capabilities": {"thrust": 22000, "fuel_efficiency": 0.42, "type": "turbojet"}, "reliability": {"mtbf": 25, "mttr": 10}},
    "radar": {
        "model": "Saphir-25 (RP-25, recon variant)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 200, "acquisition_range": 150, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 28, "mttr": 10}, "type": "mechanical",
    },
    "TVD": {
        "model": "AFA-70 camera system",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 35, "mttr": 6}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.70, "communication_system": 0.70, "communication_range": 200}, "reliability": {"mtbf": 38, "mttr": 4}},
    "avionics": {"model": "Generic Soviet recon avionics", "capabilities": {"flight_control": 0.58, "countermeasures": 0.45, "self_defense": 0.40}, "reliability": {"mtbf": 30, "mttr": 7}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 80, "mttr": 9}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 13000, "consume": 3500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 3000, "altitude": 20000, "consume": 8000, "time": 20},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 3000, "altitude": 20000, "consume": 12000, "time": 15},
    },
}

mig27k_data = {
    "constructor": "Mikoyan", "made": "USSR", "model": "MiG-27K",
    "users": ["USSR", "Russia", "India"], "start_service": 1975, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER_BOMBER], "cost": 5,
    "roles": ["Strike", "CAS", "Pinpoint_Strike"],
    "manouvrability": 0.68, "resilience": 0.70,
    "engine": {"model": "Tumansky R-29B-300", "capabilities": {"thrust": 11500, "fuel_efficiency": 0.52, "type": "turbojet"}, "reliability": {"mtbf": 30, "mttr": 8}},
    "radar": {
        "model": "PrNK-23K Kaira-23",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 60, "acquisition_range": 45, "engagement_range": 20, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 28, "mttr": 8}, "type": "mechanical",
    },
    "TVD": {
        "model": "Kaira-23 (laser-TV)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 40, "acquisition_range": 55, "engagement_range": 35, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 6}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.65, "communication_system": 0.68, "communication_range": 180}, "reliability": {"mtbf": 36, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.68, "countermeasures": 0.55, "self_defense": 0.48}, "reliability": {"mtbf": 30, "mttr": 6}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 78, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 800, "altitude": 5000, "consume": 1800},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1885, "altitude": 8000, "consume": 4000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1885, "altitude": 8000, "consume": 6500, "time": 30},
    },
}

mig29a_data = {
    "constructor": "Mikoyan", "made": "USSR", "model": "MiG-29A",
    "users": ["USSR", "Russia", "Germany", "Poland", "Romania", "Hungary"], "start_service": 1982, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 11,
    "roles": ["CAP", "Intercept", "Fighter_Sweep"],
    "manouvrability": 0.88, "resilience": 0.72,
    "engine": {"model": "Klimov RD-33", "capabilities": {"thrust": 16600, "fuel_efficiency": 0.62, "type": "turbofan"}, "reliability": {"mtbf": 35, "mttr": 6}},
    "radar": {
        "model": "NO-193 (N019) Rubin",
        "capabilities": {
            "air": (True, {"tracking_range": 100, "acquisition_range": 70, "engagement_range": 50, "multi_target_capacity": 2}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 32, "mttr": 7}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "OEPrNK-29 IRST",
        "capabilities": {
            "air": (True, {"tracking_range": 40, "acquisition_range": 50, "engagement_range": 35, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 5}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.72, "communication_system": 0.72, "communication_range": 200}, "reliability": {"mtbf": 42, "mttr": 3}},
    "avionics": {"model": "SPO-15LM Beryoza", "capabilities": {"flight_control": 0.80, "countermeasures": 0.62, "self_defense": 0.55}, "reliability": {"mtbf": 35, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 55}, "reliability": {"mtbf": 82, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2445, "altitude": 13000, "consume": 3500, "time": 90},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2445, "altitude": 13000, "consume": 6000, "time": 45},
    },
}

mig29s_data = {
    "constructor": "Mikoyan", "made": "Russia", "model": "MiG-29S",
    "users": ["Russia", "Algeria"], "start_service": 1985, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 15,
    "roles": ["CAP", "Intercept", "Fighter_Sweep", "Strike"],
    "manouvrability": 0.88, "resilience": 0.72,
    "engine": {"model": "Klimov RD-33 Series 3", "capabilities": {"thrust": 16600, "fuel_efficiency": 0.63, "type": "turbofan"}, "reliability": {"mtbf": 37, "mttr": 6}},
    "radar": {
        "model": "N019M Topaz",
        "capabilities": {
            "air": (True, {"tracking_range": 120, "acquisition_range": 80, "engagement_range": 60, "multi_target_capacity": 4}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 35, "mttr": 6}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "OEPrNK-29 IRST",
        "capabilities": {
            "air": (True, {"tracking_range": 45, "acquisition_range": 55, "engagement_range": 38, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 32, "mttr": 5}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.74, "communication_system": 0.74, "communication_range": 200}, "reliability": {"mtbf": 44, "mttr": 3}},
    "avionics": {"model": "SPO-15LM Beryoza", "capabilities": {"flight_control": 0.82, "countermeasures": 0.65, "self_defense": 0.58}, "reliability": {"mtbf": 37, "mttr": 4.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 55}, "reliability": {"mtbf": 84, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 920, "altitude": 10000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2445, "altitude": 13000, "consume": 3500, "time": 90},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2445, "altitude": 13000, "consume": 6000, "time": 45},
    },
}

mig31_data = {
    "constructor": "Mikoyan", "made": "USSR", "model": "MiG-31",
    "users": ["USSR", "Russia"], "start_service": 1981, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 22,
    "roles": ["Intercept", "CAP"],
    "manouvrability": 0.50, "resilience": 0.75,
    "engine": {"model": "Soloviev D-30F6", "capabilities": {"thrust": 31000, "fuel_efficiency": 0.52, "type": "turbofan"}, "reliability": {"mtbf": 30, "mttr": 9}},
    "radar": {
        "model": "Zaslon S-800",
        "capabilities": {
            "air": (True, {"tracking_range": 400, "acquisition_range": 200, "engagement_range": 180, "multi_target_capacity": 10}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 32, "mttr": 9}, "type": "passive",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.78, "communication_system": 0.80, "communication_range": 350}, "reliability": {"mtbf": 45, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.70, "countermeasures": 0.60, "self_defense": 0.55}, "reliability": {"mtbf": 35, "mttr": 7}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 90}, "reliability": {"mtbf": 85, "mttr": 9}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 13000, "consume": 4000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 3000, "altitude": 20000, "consume": 9000, "time": 30},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 3000, "altitude": 20000, "consume": 14000, "time": 15},
    },
}

# ==================== SOVIET/RUSSIAN ATTACKERS & STRIKE ====================

su17m4_data = {
    "constructor": "Sukhoi", "made": "USSR", "model": "Su-17M4",
    "users": ["USSR", "Russia", "Syria", "Libya"], "start_service": 1970, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER_BOMBER], "cost": 5,
    "roles": ["Strike", "CAS"],
    "manouvrability": 0.68, "resilience": 0.70,
    "engine": {"model": "AL-21F-3", "capabilities": {"thrust": 11200, "fuel_efficiency": 0.52, "type": "turbojet"}, "reliability": {"mtbf": 30, "mttr": 7}},
    "radar": {
        "model": "Klen-54",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 50, "acquisition_range": 40, "engagement_range": 15, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 28, "mttr": 7}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.62, "communication_system": 0.65, "communication_range": 180}, "reliability": {"mtbf": 35, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.65, "countermeasures": 0.50, "self_defense": 0.44}, "reliability": {"mtbf": 30, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 78, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 800, "altitude": 5000, "consume": 1500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1850, "altitude": 11000, "consume": 4000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1850, "altitude": 11000, "consume": 6500, "time": 30},
    },
}

su24m_data = {
    "constructor": "Sukhoi", "made": "USSR", "model": "Su-24M",
    "users": ["USSR", "Russia", "Ukraine", "Algeria", "Libya", "Syria"], "start_service": 1979, "end_service": None,
    "category": [Air_Asset_Type.BOMBER], "cost": 24,
    "roles": ["Strike", "Pinpoint_Strike", "SEAD"],
    "manouvrability": 0.58, "resilience": 0.72,
    "engine": {"model": "Saturn AL-21F-3A", "capabilities": {"thrust": 22000, "fuel_efficiency": 0.52, "type": "turbojet"}, "reliability": {"mtbf": 30, "mttr": 8}},
    "radar": {
        "model": "Orion-A",
        "capabilities": {
            "air": (True, {"tracking_range": 80, "acquisition_range": 50, "engagement_range": 0, "multi_target_capacity": 1}),
            "ground": (True, {"tracking_range": 120, "acquisition_range": 90, "engagement_range": 40, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 9}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "Kaira-24 (laser-TV)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 50, "acquisition_range": 65, "engagement_range": 45, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 32, "mttr": 6}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.72, "communication_system": 0.72, "communication_range": 250}, "reliability": {"mtbf": 40, "mttr": 3.5}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.70, "countermeasures": 0.58, "self_defense": 0.50}, "reliability": {"mtbf": 32, "mttr": 6}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 85, "mttr": 8}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 3000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1700, "altitude": 11000, "consume": 5500, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1700, "altitude": 11000, "consume": 9000, "time": 30},
    },
}

su24mr_data = {
    "constructor": "Sukhoi", "made": "USSR", "model": "Su-24MR",
    "users": ["USSR", "Russia", "Ukraine"], "start_service": 1983, "end_service": None,
    "category": [Air_Asset_Type.RECON], "cost": 25,
    "roles": ["Recon"],
    "manouvrability": 0.58, "resilience": 0.72,
    "engine": {"model": "Saturn AL-21F-3A", "capabilities": {"thrust": 22000, "fuel_efficiency": 0.52, "type": "turbojet"}, "reliability": {"mtbf": 30, "mttr": 8}},
    "radar": {
        "model": "Shtyk SAR",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 200, "acquisition_range": 160, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 30, "mttr": 9}, "type": "mechanical",
    },
    "TVD": {
        "model": "AFA-100 FLIR/camera",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 35, "mttr": 6}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.72, "communication_system": 0.72, "communication_range": 250}, "reliability": {"mtbf": 40, "mttr": 3.5}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.68, "countermeasures": 0.55, "self_defense": 0.48}, "reliability": {"mtbf": 32, "mttr": 6}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 85, "mttr": 8}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 3000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1700, "altitude": 11000, "consume": 5500, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1700, "altitude": 11000, "consume": 9000, "time": 30},
    },
}

su25_data = {
    "constructor": "Sukhoi", "made": "USSR", "model": "Su-25",
    "users": ["USSR", "Russia", "Ukraine", "Georgia", "Belarus", "many others"], "start_service": 1981, "end_service": None,
    "category": [Air_Asset_Type.ATTACKER], "cost": 11,
    "roles": ["CAS", "Strike"],
    "manouvrability": 0.55, "resilience": 0.88,
    "engine": {"model": "Tumansky R-95Sh", "capabilities": {"thrust": 9000, "fuel_efficiency": 0.60, "type": "turbojet"}, "reliability": {"mtbf": 40, "mttr": 5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "Klen-PS laser rangefinder",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 10, "acquisition_range": 15, "engagement_range": 8, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 3}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.60, "communication_system": 0.62, "communication_range": 150}, "reliability": {"mtbf": 38, "mttr": 3}},
    "avionics": {"model": "SPO-15LM Beryoza", "capabilities": {"flight_control": 0.60, "countermeasures": 0.52, "self_defense": 0.46}, "reliability": {"mtbf": 35, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 50}, "reliability": {"mtbf": 95, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 500, "altitude": 5000, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 5000, "consume": 2000, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 5000, "consume": 3000, "time": 60},
    },
}

su25t_data = {
    "constructor": "Sukhoi", "made": "USSR", "model": "Su-25T",
    "users": ["USSR", "Russia"], "start_service": 1990, "end_service": None,
    "category": [Air_Asset_Type.ATTACKER], "cost": 14,
    "roles": ["CAS", "Strike", "Pinpoint_Strike"],
    "manouvrability": 0.55, "resilience": 0.88,
    "engine": {"model": "Tumansky R-195", "capabilities": {"thrust": 9300, "fuel_efficiency": 0.62, "type": "turbojet"}, "reliability": {"mtbf": 42, "mttr": 5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "Shkval-M (TV/optical)",
        "capabilities": {
            "air": (True, {"tracking_range": 15, "acquisition_range": 20, "engagement_range": 10, "multi_target_capacity": 1}),
            "ground": (True, {"tracking_range": 40, "acquisition_range": 50, "engagement_range": 35, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 38, "mttr": 4}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.68, "communication_system": 0.70, "communication_range": 180}, "reliability": {"mtbf": 42, "mttr": 3}},
    "avionics": {"model": "Pastel RWR", "capabilities": {"flight_control": 0.68, "countermeasures": 0.60, "self_defense": 0.54}, "reliability": {"mtbf": 38, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 52}, "reliability": {"mtbf": 95, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 520, "altitude": 5000, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 5000, "consume": 2000, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 5000, "consume": 3000, "time": 60},
    },
}

su25tm_data = {
    "constructor": "Sukhoi", "made": "Russia", "model": "Su-25TM",
    "users": ["Russia"], "start_service": 2008, "end_service": None,
    "category": [Air_Asset_Type.ATTACKER], "cost": 17,
    "roles": ["CAS", "Strike", "Pinpoint_Strike", "SEAD"],
    "manouvrability": 0.56, "resilience": 0.88,
    "engine": {"model": "Tumansky R-195", "capabilities": {"thrust": 9300, "fuel_efficiency": 0.62, "type": "turbojet"}, "reliability": {"mtbf": 44, "mttr": 5}},
    "radar": {
        "model": "Kopyo-25 (optional)",
        "capabilities": {
            "air": (True, {"tracking_range": 80, "acquisition_range": 50, "engagement_range": 30, "multi_target_capacity": 2}),
            "ground": (True, {"tracking_range": 60, "acquisition_range": 45, "engagement_range": 20, "multi_target_capacity": 2}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 38, "mttr": 6}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "Shkval-M + Mercury FLIR",
        "capabilities": {
            "air": (True, {"tracking_range": 20, "acquisition_range": 25, "engagement_range": 15, "multi_target_capacity": 1}),
            "ground": (True, {"tracking_range": 50, "acquisition_range": 65, "engagement_range": 45, "multi_target_capacity": 3}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 3.5}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.75, "communication_system": 0.75, "communication_range": 200}, "reliability": {"mtbf": 45, "mttr": 3}},
    "avionics": {"model": "Pastel RWR + L166S-11E IRCM", "capabilities": {"flight_control": 0.72, "countermeasures": 0.68, "self_defense": 0.62}, "reliability": {"mtbf": 42, "mttr": 3.5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 52}, "reliability": {"mtbf": 95, "mttr": 5}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 530, "altitude": 5000, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 5000, "consume": 2000, "time": 120},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 5000, "consume": 3000, "time": 60},
    },
}

su27_data = {
    "constructor": "Sukhoi", "made": "USSR", "model": "Su-27",
    "users": ["USSR", "Russia", "Ukraine", "Kazakhstan", "China"], "start_service": 1985, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER], "cost": 30,
    "roles": ["CAP", "Intercept", "Fighter_Sweep", "Escort"],
    "manouvrability": 0.90, "resilience": 0.78,
    "engine": {"model": "Saturn AL-31F", "capabilities": {"thrust": 25000, "fuel_efficiency": 0.68, "type": "turbofan"}, "reliability": {"mtbf": 38, "mttr": 7}},
    "radar": {
        "model": "N001 Myech",
        "capabilities": {
            "air": (True, {"tracking_range": 240, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 10}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 36, "mttr": 7}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "OEPS-27 IRST",
        "capabilities": {
            "air": (True, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 45, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 32, "mttr": 5}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.75, "communication_system": 0.75, "communication_range": 280}, "reliability": {"mtbf": 45, "mttr": 3}},
    "avionics": {"model": "SPO-15LM Beryoza", "capabilities": {"flight_control": 0.85, "countermeasures": 0.65, "self_defense": 0.58}, "reliability": {"mtbf": 38, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 88, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 10000, "consume": 1800},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2500, "altitude": 13000, "consume": 4200, "time": 90},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2500, "altitude": 13000, "consume": 7000, "time": 45},
    },
}

su30_data = {
    "constructor": "Sukhoi", "made": "Russia", "model": "Su-30",
    "users": ["Russia", "India", "China", "Malaysia", "Algeria"], "start_service": 1996, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 38,
    "roles": ["CAP", "Strike", "SEAD", "Anti_Ship", "Escort"],
    "manouvrability": 0.92, "resilience": 0.80,
    "engine": {"model": "Saturn AL-31FP (TVC)", "capabilities": {"thrust": 25000, "fuel_efficiency": 0.70, "type": "turbofan"}, "reliability": {"mtbf": 40, "mttr": 6}},
    "radar": {
        "model": "N011M Bars",
        "capabilities": {
            "air": (True, {"tracking_range": 350, "acquisition_range": 150, "engagement_range": 120, "multi_target_capacity": 15}),
            "ground": (True, {"tracking_range": 150, "acquisition_range": 120, "engagement_range": 60, "multi_target_capacity": 4}),
            "sea": (True, {"tracking_range": 250, "acquisition_range": 200, "engagement_range": 0, "multi_target_capacity": 6}),
        },
        "reliability": {"mtbf": 40, "mttr": 6}, "type": "passive",
    },
    "TVD": {
        "model": "OLS-30 IRST",
        "capabilities": {
            "air": (True, {"tracking_range": 60, "acquisition_range": 75, "engagement_range": 55, "multi_target_capacity": 1}),
            "ground": (True, {"tracking_range": 30, "acquisition_range": 40, "engagement_range": 25, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 35, "mttr": 4}, "type": "optical",
    },
    "radio_nav": {"model": "A-737 GPS/INS", "capabilities": {"navigation_system": 0.85, "communication_system": 0.82, "communication_range": 350}, "reliability": {"mtbf": 52, "mttr": 2.5}},
    "avionics": {"model": "SPO-32 Pastel", "capabilities": {"flight_control": 0.88, "countermeasures": 0.72, "self_defense": 0.65}, "reliability": {"mtbf": 42, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 80}, "reliability": {"mtbf": 90, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 10000, "consume": 2000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 11000, "consume": 4500, "time": 90},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2120, "altitude": 11000, "consume": 7500, "time": 45},
    },
}

su33_data = {
    "constructor": "Sukhoi", "made": "Russia", "model": "Su-33",
    "users": ["Russia"], "start_service": 1998, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER, Air_Asset_Type.FIGHTER_BOMBER], "cost": 37,
    "roles": ["CAP", "Intercept", "Strike"],
    "manouvrability": 0.88, "resilience": 0.78,
    "engine": {"model": "Saturn AL-31F3", "capabilities": {"thrust": 25000, "fuel_efficiency": 0.68, "type": "turbofan"}, "reliability": {"mtbf": 38, "mttr": 7}},
    "radar": {
        "model": "N001K Myech-K",
        "capabilities": {
            "air": (True, {"tracking_range": 240, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 10}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 150, "acquisition_range": 120, "engagement_range": 0, "multi_target_capacity": 5}),
        },
        "reliability": {"mtbf": 36, "mttr": 7}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "OEPS-27K IRST",
        "capabilities": {
            "air": (True, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 45, "multi_target_capacity": 1}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 30, "acquisition_range": 40, "engagement_range": 0, "multi_target_capacity": 1}),
        },
        "reliability": {"mtbf": 32, "mttr": 5}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.78, "communication_system": 0.78, "communication_range": 280}, "reliability": {"mtbf": 48, "mttr": 3}},
    "avionics": {"model": "SPO-15LM Beryoza", "capabilities": {"flight_control": 0.86, "countermeasures": 0.65, "self_defense": 0.58}, "reliability": {"mtbf": 38, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 82}, "reliability": {"mtbf": 88, "mttr": 7}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1000, "altitude": 10000, "consume": 1900},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2300, "altitude": 13000, "consume": 4300, "time": 90},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2300, "altitude": 13000, "consume": 7200, "time": 45},
    },
}

su34_data = {
    "constructor": "Sukhoi", "made": "Russia", "model": "Su-34",
    "users": ["Russia"], "start_service": 2014, "end_service": None,
    "category": [Air_Asset_Type.FIGHTER_BOMBER], "cost": 36,
    "roles": ["Strike", "Pinpoint_Strike", "SEAD", "Anti_Ship"],
    "manouvrability": 0.80, "resilience": 0.80,
    "engine": {"model": "Saturn AL-31FM1", "capabilities": {"thrust": 27000, "fuel_efficiency": 0.70, "type": "turbofan"}, "reliability": {"mtbf": 42, "mttr": 6}},
    "radar": {
        "model": "V004 Leninets (AESA)",
        "capabilities": {
            "air": (True, {"tracking_range": 350, "acquisition_range": 200, "engagement_range": 160, "multi_target_capacity": 16}),
            "ground": (True, {"tracking_range": 200, "acquisition_range": 150, "engagement_range": 80, "multi_target_capacity": 6}),
            "sea": (True, {"tracking_range": 400, "acquisition_range": 300, "engagement_range": 0, "multi_target_capacity": 8}),
        },
        "reliability": {"mtbf": 50, "mttr": 5}, "type": "AESA",
    },
    "TVD": {
        "model": "OLS-35 IRST",
        "capabilities": {
            "air": (True, {"tracking_range": 60, "acquisition_range": 75, "engagement_range": 55, "multi_target_capacity": 1}),
            "ground": (True, {"tracking_range": 50, "acquisition_range": 65, "engagement_range": 45, "multi_target_capacity": 3}),
            "sea": (True, {"tracking_range": 40, "acquisition_range": 50, "engagement_range": 35, "multi_target_capacity": 2}),
        },
        "reliability": {"mtbf": 38, "mttr": 4}, "type": "thermal and optical",
    },
    "radio_nav": {"model": "GLONASS/GPS INS", "capabilities": {"navigation_system": 0.92, "communication_system": 0.88, "communication_range": 400}, "reliability": {"mtbf": 58, "mttr": 2}},
    "avionics": {"model": "Khibiny ECM + Pastel", "capabilities": {"flight_control": 0.90, "countermeasures": 0.80, "self_defense": 0.75}, "reliability": {"mtbf": 45, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 90}, "reliability": {"mtbf": 92, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 950, "altitude": 10000, "consume": 2500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1900, "altitude": 11000, "consume": 5000, "time": 90},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1900, "altitude": 11000, "consume": 8500, "time": 45},
    },
}

# ==================== SOVIET/RUSSIAN STRATEGIC BOMBERS ====================

tu22m_data = {
    "constructor": "Tupolev", "made": "USSR", "model": "Tu-22M",
    "users": ["USSR", "Russia"], "start_service": 1972, "end_service": None,
    "category": [Air_Asset_Type.HEAVY_BOMBER], "cost": 45,
    "roles": ["Strike", "Anti_Ship"],
    "manouvrability": 0.35, "resilience": 0.72,
    "engine": {"model": "NK-25", "capabilities": {"thrust": 50000, "fuel_efficiency": 0.55, "type": "turbofan"}, "reliability": {"mtbf": 35, "mttr": 12}},
    "radar": {
        "model": "PN-A (Leninets)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 200, "acquisition_range": 150, "engagement_range": 80, "multi_target_capacity": 4}),
            "sea": (True, {"tracking_range": 400, "acquisition_range": 350, "engagement_range": 0, "multi_target_capacity": 8}),
        },
        "reliability": {"mtbf": 40, "mttr": 12}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.80, "communication_system": 0.80, "communication_range": 500}, "reliability": {"mtbf": 50, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.72, "countermeasures": 0.68, "self_defense": 0.60}, "reliability": {"mtbf": 38, "mttr": 8}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 200}, "reliability": {"mtbf": 110, "mttr": 12}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 10000, "consume": 10000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2000, "altitude": 13000, "consume": 16000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2000, "altitude": 13000, "consume": 22000, "time": 30},
    },
}

tu95ms_data = {
    "constructor": "Tupolev", "made": "USSR", "model": "Tu-95MS",
    "users": ["USSR", "Russia"], "start_service": 1981, "end_service": None,
    "category": [Air_Asset_Type.HEAVY_BOMBER], "cost": 36,
    "roles": ["Strike"],
    "manouvrability": 0.18, "resilience": 0.68,
    "engine": {"model": "NK-12M", "capabilities": {"thrust": 51000, "fuel_efficiency": 0.55, "type": "turboprop"}, "reliability": {"mtbf": 40, "mttr": 14}},
    "radar": {
        "model": "Obzor-MS",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 250, "acquisition_range": 200, "engagement_range": 0, "multi_target_capacity": 2}),
            "sea": (True, {"tracking_range": 350, "acquisition_range": 300, "engagement_range": 0, "multi_target_capacity": 4}),
        },
        "reliability": {"mtbf": 45, "mttr": 14}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.80, "communication_system": 0.82, "communication_range": 600}, "reliability": {"mtbf": 55, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.68, "countermeasures": 0.65, "self_defense": 0.58}, "reliability": {"mtbf": 38, "mttr": 10}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 300}, "reliability": {"mtbf": 120, "mttr": 14}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 740, "altitude": 12000, "consume": 13000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 920, "altitude": 12000, "consume": 17000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 920, "altitude": 12000, "consume": 22000, "time": 240},
    },
}

tu142_data = {
    "constructor": "Tupolev", "made": "USSR", "model": "Tu-142",
    "users": ["USSR", "Russia", "India"], "start_service": 1972, "end_service": None,
    "category": [Air_Asset_Type.BOMBER], "cost": 30,
    "roles": ["Anti_Ship", "Recon"],
    "manouvrability": 0.18, "resilience": 0.65,
    "engine": {"model": "NK-12MV", "capabilities": {"thrust": 51000, "fuel_efficiency": 0.55, "type": "turboprop"}, "reliability": {"mtbf": 38, "mttr": 14}},
    "radar": {
        "model": "Berkut-95 maritime search",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 450, "acquisition_range": 400, "engagement_range": 0, "multi_target_capacity": 6}),
        },
        "reliability": {"mtbf": 42, "mttr": 14}, "type": "mechanical",
    },
    "TVD": {
        "model": "AFA-42 camera",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (True, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 0, "multi_target_capacity": 2}),
        },
        "reliability": {"mtbf": 38, "mttr": 8}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.78, "communication_system": 0.80, "communication_range": 600}, "reliability": {"mtbf": 52, "mttr": 4}},
    "avionics": {"model": "SPO-15 Beryoza", "capabilities": {"flight_control": 0.65, "countermeasures": 0.60, "self_defense": 0.52}, "reliability": {"mtbf": 36, "mttr": 10}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 300}, "reliability": {"mtbf": 115, "mttr": 14}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 700, "altitude": 10000, "consume": 13000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 16000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 20000, "time": 240},
    },
}

tu160_data = {
    "constructor": "Tupolev", "made": "USSR", "model": "Tu-160",
    "users": ["USSR", "Russia"], "start_service": 1987, "end_service": None,
    "category": [Air_Asset_Type.HEAVY_BOMBER], "cost": 250,
    "roles": ["Strike", "Pinpoint_Strike"],
    "manouvrability": 0.40, "resilience": 0.75,
    "engine": {"model": "NK-32", "capabilities": {"thrust": 100000, "fuel_efficiency": 0.60, "type": "turbofan"}, "reliability": {"mtbf": 35, "mttr": 14}},
    "radar": {
        "model": "Obzor-K + Sopka nav",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 300, "acquisition_range": 250, "engagement_range": 100, "multi_target_capacity": 4}),
            "sea": (True, {"tracking_range": 400, "acquisition_range": 350, "engagement_range": 0, "multi_target_capacity": 6}),
        },
        "reliability": {"mtbf": 40, "mttr": 14}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "GLONASS/INS", "capabilities": {"navigation_system": 0.90, "communication_system": 0.88, "communication_range": 700}, "reliability": {"mtbf": 60, "mttr": 3}},
    "avionics": {"model": "Baikal-3 EW", "capabilities": {"flight_control": 0.85, "countermeasures": 0.78, "self_defense": 0.72}, "reliability": {"mtbf": 42, "mttr": 10}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 5000, "fluid_capacity": 400}, "reliability": {"mtbf": 125, "mttr": 14}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 900, "altitude": 12000, "consume": 18000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2220, "altitude": 15000, "consume": 35000, "time": 60},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 2220, "altitude": 15000, "consume": 50000, "time": 30},
    },
}

# ==================== SOVIET/RUSSIAN SUPPORT & TRANSPORT ====================

a50_data = {
    "constructor": "Beriev", "made": "USSR", "model": "A-50",
    "users": ["USSR", "Russia"], "start_service": 1984, "end_service": None,
    "category": [Air_Asset_Type.AWACS], "cost": 330,
    "roles": [],
    "manouvrability": 0.22, "resilience": 0.55,
    "engine": {"model": "Soloviev D-30KP", "capabilities": {"thrust": 48000, "fuel_efficiency": 0.65, "type": "turbofan"}, "reliability": {"mtbf": 55, "mttr": 10}},
    "radar": {
        "model": "Shmel (Bumblebee) AWACS",
        "capabilities": {
            "air": (True, {"tracking_range": 600, "acquisition_range": 550, "engagement_range": 0, "multi_target_capacity": 50}),
            "ground": (True, {"tracking_range": 300, "acquisition_range": 250, "engagement_range": 0, "multi_target_capacity": 20}),
            "sea": (True, {"tracking_range": 400, "acquisition_range": 350, "engagement_range": 0, "multi_target_capacity": 20}),
        },
        "reliability": {"mtbf": 60, "mttr": 9}, "type": "pulse-doppler",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.85, "communication_system": 0.92, "communication_range": 700}, "reliability": {"mtbf": 62, "mttr": 3}},
    "avionics": {"model": "Generic AWACS avionics", "capabilities": {"flight_control": 0.72, "countermeasures": 0.55, "self_defense": 0.45}, "reliability": {"mtbf": 55, "mttr": 7}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 200}, "reliability": {"mtbf": 118, "mttr": 11}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 700, "altitude": 10000, "consume": 8000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 11000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 15000, "time": 240},
    },
}

an26b_data = {
    "constructor": "Antonov", "made": "USSR", "model": "An-26B",
    "users": ["USSR", "Russia", "Ukraine", "Cuba", "Vietnam"], "start_service": 1970, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 2,
    "roles": [],
    "manouvrability": 0.30, "resilience": 0.48,
    "engine": {"model": "AI-24VT", "capabilities": {"thrust": 4000, "fuel_efficiency": 0.58, "type": "turboprop"}, "reliability": {"mtbf": 55, "mttr": 5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-2S", "capabilities": {"navigation_system": 0.65, "communication_system": 0.65, "communication_range": 200}, "reliability": {"mtbf": 50, "mttr": 3}},
    "avionics": {"model": "Generic Soviet transport avionics", "capabilities": {"flight_control": 0.62, "countermeasures": 0.10, "self_defense": 0.08}, "reliability": {"mtbf": 50, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 60}, "reliability": {"mtbf": 100, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 430, "altitude": 6000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 540, "altitude": 6000, "consume": 2000, "time": 300},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 540, "altitude": 6000, "consume": 2500, "time": 180},
    },
}

an30m_data = {
    "constructor": "Antonov", "made": "USSR", "model": "An-30M",
    "users": ["USSR", "Russia", "Ukraine"], "start_service": 1968, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 2,
    "roles": [],
    "manouvrability": 0.28, "resilience": 0.45,
    "engine": {"model": "AI-24A", "capabilities": {"thrust": 4000, "fuel_efficiency": 0.56, "type": "turboprop"}, "reliability": {"mtbf": 52, "mttr": 5}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "AFA-41/20 survey cameras",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 10, "acquisition_range": 12, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 40, "mttr": 4}, "type": "optical",
    },
    "radio_nav": {"model": "RSBN-2S", "capabilities": {"navigation_system": 0.62, "communication_system": 0.62, "communication_range": 200}, "reliability": {"mtbf": 48, "mttr": 3}},
    "avionics": {"model": "Generic Soviet transport avionics", "capabilities": {"flight_control": 0.60, "countermeasures": 0.10, "self_defense": 0.08}, "reliability": {"mtbf": 48, "mttr": 4}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 55}, "reliability": {"mtbf": 95, "mttr": 6}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 420, "altitude": 6000, "consume": 1400},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 540, "altitude": 6000, "consume": 2000, "time": 300},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 540, "altitude": 6000, "consume": 2500, "time": 180},
    },
}

il76md_data = {
    "constructor": "Ilyushin", "made": "USSR", "model": "Il-76MD",
    "users": ["USSR", "Russia", "India", "China", "Algeria"], "start_service": 1974, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 30,
    "roles": [],
    "manouvrability": 0.25, "resilience": 0.55,
    "engine": {"model": "Soloviev D-30KP-2", "capabilities": {"thrust": 48000, "fuel_efficiency": 0.65, "type": "turbofan"}, "reliability": {"mtbf": 58, "mttr": 8}},
    "radar": {
        "model": "Kupol-76 (weather)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 60, "engagement_range": 0, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 55, "mttr": 7}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.80, "communication_system": 0.80, "communication_range": 400}, "reliability": {"mtbf": 62, "mttr": 3}},
    "avionics": {"model": "Generic Soviet transport avionics", "capabilities": {"flight_control": 0.72, "countermeasures": 0.30, "self_defense": 0.25}, "reliability": {"mtbf": 58, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 200}, "reliability": {"mtbf": 115, "mttr": 10}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 780, "altitude": 10000, "consume": 6500},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 9000, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 12000, "time": 240},
    },
}

il78m_data = {
    "constructor": "Ilyushin", "made": "USSR", "model": "Il-78M",
    "users": ["Russia"], "start_service": 1984, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 35,
    "roles": [],
    "manouvrability": 0.22, "resilience": 0.52,
    "engine": {"model": "Soloviev D-30KP-2", "capabilities": {"thrust": 48000, "fuel_efficiency": 0.65, "type": "turbofan"}, "reliability": {"mtbf": 58, "mttr": 8}},
    "radar": {
        "model": "Kupol-76 (weather)",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (True, {"tracking_range": 80, "acquisition_range": 60, "engagement_range": 0, "multi_target_capacity": 1}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 55, "mttr": 7}, "type": "mechanical",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-6S", "capabilities": {"navigation_system": 0.80, "communication_system": 0.80, "communication_range": 400}, "reliability": {"mtbf": 62, "mttr": 3}},
    "avionics": {"model": "Generic Soviet tanker avionics", "capabilities": {"flight_control": 0.70, "countermeasures": 0.28, "self_defense": 0.22}, "reliability": {"mtbf": 55, "mttr": 5}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 3000, "fluid_capacity": 200}, "reliability": {"mtbf": 115, "mttr": 10}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 770, "altitude": 10000, "consume": 7000},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 9500, "time": 480},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 10000, "consume": 13000, "time": 240},
    },
}

yak40_data = {
    "constructor": "Yakovlev", "made": "USSR", "model": "Yak-40",
    "users": ["USSR", "Russia", "Ukraine", "Cuba"], "start_service": 1968, "end_service": None,
    "category": [Air_Asset_Type.TRANSPORT], "cost": 1,
    "roles": [],
    "manouvrability": 0.32, "resilience": 0.48,
    "engine": {"model": "Ivchenko AI-25", "capabilities": {"thrust": 4500, "fuel_efficiency": 0.58, "type": "turbofan"}, "reliability": {"mtbf": 50, "mttr": 4}},
    "radar": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "TVD": {
        "model": "none",
        "capabilities": {
            "air": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "ground": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
            "sea": (False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0}),
        },
        "reliability": {"mtbf": 999, "mttr": 0}, "type": "none",
    },
    "radio_nav": {"model": "RSBN-2S", "capabilities": {"navigation_system": 0.62, "communication_system": 0.62, "communication_range": 150}, "reliability": {"mtbf": 48, "mttr": 3}},
    "avionics": {"model": "Generic Soviet avionics", "capabilities": {"flight_control": 0.60, "countermeasures": 0.05, "self_defense": 0.05}, "reliability": {"mtbf": 45, "mttr": 3}},
    "hydraulic": {"model": "Generic Hydraulic System", "capabilities": {"pressure": 1500, "fluid_capacity": 30}, "reliability": {"mtbf": 90, "mttr": 4}},
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 500, "altitude": 6000, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 600, "altitude": 6000, "consume": 1600, "time": 300},
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 600, "altitude": 6000, "consume": 2000, "time": 180},
    },
}

# SETUP DICTIONARY VALUE
SCORES = ('Radar score', 'Radar score air', 'Speed score', 'avalaibility', 'manutenability score (mttr)', 'reliability score (mtbf)')
AIRCRAFT = {}


Aircraft_Data(**f16_data_example)
Aircraft_Data(**f14a_data)
Aircraft_Data(**f14b_data)
Aircraft_Data(**f15c_data)
Aircraft_Data(**f15e_data)
Aircraft_Data(**fa18a_data)
Aircraft_Data(**fa18c_data)
Aircraft_Data(**fa18c_lot20_data)
Aircraft_Data(**f4e_data)
Aircraft_Data(**f5e_data)
Aircraft_Data(**f86e_data)
Aircraft_Data(**f16a_data)
Aircraft_Data(**f16a_mlu_data)
Aircraft_Data(**f16c_bl52d_data)
Aircraft_Data(**f16cm_bl50_data)
Aircraft_Data(**a10a_data)
Aircraft_Data(**a10c_data)
Aircraft_Data(**a10c2_data)
Aircraft_Data(**a20g_data)
Aircraft_Data(**a4ec_data)
Aircraft_Data(**f117_data)
Aircraft_Data(**b1b_data)
Aircraft_Data(**b52h_data)
Aircraft_Data(**s3b_data)
Aircraft_Data(**s3b_tanker_data)
Aircraft_Data(**e2d_data)
Aircraft_Data(**e3a_data)
Aircraft_Data(**mq1a_data)
Aircraft_Data(**mq9_data)
Aircraft_Data(**c130_data)
Aircraft_Data(**c17a_data)
Aircraft_Data(**kc130_data)
Aircraft_Data(**kc135_data)
Aircraft_Data(**kc135_mprs_data)
Aircraft_Data(**asj37_data)
Aircraft_Data(**m2000c_data)
Aircraft_Data(**mig15_data)
Aircraft_Data(**mig19p_data)
Aircraft_Data(**mig21bis_data)
Aircraft_Data(**mig23mld_data)
Aircraft_Data(**mig25pd_data)
Aircraft_Data(**mig25rb_data)
Aircraft_Data(**mig27k_data)
Aircraft_Data(**mig29a_data)
Aircraft_Data(**mig29s_data)
Aircraft_Data(**mig31_data)
Aircraft_Data(**su17m4_data)
Aircraft_Data(**su24m_data)
Aircraft_Data(**su24mr_data)
Aircraft_Data(**su25_data)
Aircraft_Data(**su25t_data)
Aircraft_Data(**su25tm_data)
Aircraft_Data(**su27_data)
Aircraft_Data(**su30_data)
Aircraft_Data(**su33_data)
Aircraft_Data(**su34_data)
Aircraft_Data(**tu22m_data)
Aircraft_Data(**tu95ms_data)
Aircraft_Data(**tu142_data)
Aircraft_Data(**tu160_data)
Aircraft_Data(**a50_data)
Aircraft_Data(**an26b_data)
Aircraft_Data(**an30m_data)
Aircraft_Data(**il76md_data)
Aircraft_Data(**il78m_data)
Aircraft_Data(**yak40_data)
#Aircraft_Data(**f18_data_example)
#Aircraft_Data(**f14_data_example)
#Aircraft_Data(**f15_data_example)

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
    

#print(f"F-14 Speed score and avalaibility: {get_aircraft_scores(model = 'F-14A Tomcat', scores = ['Speed score', 'avalaibility'])}" )
    


    
    