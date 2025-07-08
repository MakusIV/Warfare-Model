from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Threat import Threat
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.State import State
from Code.Dynamic_War_Manager.Source.Utility.Utility import true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft_Data')

@dataclass
class Engine:
    model: str = "Generic Engine"
    capabilities: Dict[str, Any] = {"thrust": 0, "fuel_efficiency": 0, "type": "jet"}
    reliability: Dict[str, Any] = {"mtbf": 0, "mttr": 0}
    daily_maintenance_hours: float = 0.0
    field_repair_hours: float = 0.0

@dataclass
class Radar:
    model: str = "Generic Radar" 
    capabilities: Dict[str, Any] = {    "air": {True, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0} }, 
                                        "ground": {False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0} },
                                        "sea": {False, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0} },
                                        "type": "pulse-doppler"
                                    }
    reliability: Dict[str, Any] = {"mtbf": 0, "mttr": 0}
    daily_maintenance_hours: float = 0.0    
    field_repair_hours: float = 0.0


@dataclass
class TVD:
    """TVD (Thermal Vision Device) for aircraft, typically used for night operations or low-visibility conditions."""
    model: str = "Generic TVD Sensor"
    # Capabilities for infrared sensors can vary widely, so this is a placeholder
    capabilities: Dict[str, Any] = {    "air": {True, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0} }, 
                                        "ground": {True, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0} },
                                        "sea": {True, {"tracking_range": 0, "acquisition_range": 0, "engagement_range": 0, "multi_target_capacity": 0} },
                                        "type": "thermal and optical" 
                                    }
    reliability: Dict[str, Any] = {"mtbf": 0, "mttr": 0}
    daily_maintenance_hours: float = 0.0    
    field_repair_hours: float = 0.0


@dataclass
class RadioNav:
    model: str = "Generic RadioNav"
    capabilities: Dict[str, Any] = {"navigation_accuracy": 0, "communication_range": 0}
    reliability: Dict[str, Any] = {"mtbf": 0, "mttr": 0}
    daily_maintenance_hours: float = 0.0
    field_repair_hours: float = 0.0

@dataclass
class Avionics:
    model: str = "Generic Avionics"
    capabilities: Dict[str, Any] = {"flight_control": 0, "navigation_system": 0, "communication_system": 0}
    reliability: Dict[str, Any] = {"mtbf": 0, "mttr": 0} 
    daily_maintenance_hours: float = 0.0
    field_repair_hours: float = 0.0

@dataclass
class Hydraulic:
    model: str = "Generic Hydraulic System"
    capabilities: Dict[str, Any] = {"pressure": 0, "fluid_capacity": 0}
    reliability: Dict[str, Any] = {"mtbf": 0, "mttr": 0}
    daily_maintenance_hours: float = 0.0
    field_repair_hours: float = 0.0

@dataclass
class SpeedData: #metric: speed in km/h, altitude in meters, imperial: speed in mph, altitude in feet, time in minutes
    sustained: Dict[str, Any] = {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 0, "altitude": 0, "consume": 0}
    combat: Dict[str, Any] = {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 0, "altitude": 0, "consume": 0, "time": 0}
    emergency: Dict[str, Any] = {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 0, "altitude": 0, "consume": 0, "time": 0}
    # Add more speed types as needed    

    
@dataclass
class Aircraft_Data:
    _registry = []
    
    
    def __init__(self, constructor: str, made: str, model: str, category: str, roles: str, engine: Optional[Engine] = None, radar: Optional[Radar] = None, radio_nav: Optional[RadioNav] = None, avionics: Optional[Avionics] = None, hydraulic: Optional[Hydraulic] = None, speed_data: Optional[SpeedData] = None, ordinance: Optional[Ordinance] = None ):
        self.constructor = constructor
        self.made = made
        self.model = model
        self.category = category
        self.roles = roles
        self.engine = engine
        self.radar = radar
        self.radio_nav = radio_nav
        self.avionics = avionics
        self.hydraulic = hydraulic
        self.speed_data = speed_data
        self.ordinance = ordinance
        Aircraft_Data._registry.append(self)

    # --- Getter e Setter ---
    def get_engine(self):
        return self.engine
    
    def set_engine(self, engine):
        self.engine = engine

    # ... (altri getter/setter per tutte le proprietà)

    
    # --- Implementazioni predefinite delle formule ---
    def _radar_eval(self, modes: List = ['air', 'ground', 'sea']) -> float:
        """Evaluates the radar capabilities of the aircraft based on predefined weights."""
        if not self.radar:
            logger.warning("Radar not defined.")
            return 0.0
        
        if not isinstance(modes, List) or modes not in ['air', 'ground', 'sea']:
            raise TypeError(f"Il parametro 'mode' must be a List of string with value:  ['air', 'ground', 'sea', 'all'], got {mode!r}.")
        
        weights = {
            'tracking_range': 0.2,
            'acquisition_range': 0.1,
            'engagement_range': 0.3,
            'multi_target': 0.4
        }
        score = 0.0
        
        for m in modes:
            cap = self.radar.capabilities[m]
            if cap.key(): 
                score += cap.get('tracking_range', 0) * weights['tracking_range']
                score += cap.get('acquisition_range', 0) * weights['acquisition_range']
                score += cap.get('engagement_range', 0) * weights['engagement_range']
                score += cap.get('multi_target_capacity', 0) * weights['multi_target']
        
        return score

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
                speed = true_air_speed( data.get('true_airspeed', 0), data.get('altitude', 0), data.get('metric', 'metric') )

            elif data.get('type_speed') == "true_airspeed":
                speed = data['airspeed']            
            else:
                raise ValueError(f"Invalid type_speed: {data.get('type_speed', 'unknown')}. Expected 'indicated_airspeed' or 'true_airspeed'.")
            
            speed = true_air_speed_at_new_altitude(speed, data.get('altitude', 0), altitude, metric=data.get('metric', 'metric'))

            if not hasattr(data, 'time'):
                time = 1 # sustained speed
            else:
                time = data.get('time')
                if speed_type == 'combat':
                    time /=  60  # reference on 60'
                 
                elif speed_type == 'emergency':
                    time /= 3 # reference on 3'
            
            # Considera anche l'altitudine e il consumo
            score += (speed * weight) * time - data.get('consume', 0) * 0.001
        return score

    def _default_reliability_eval(self):
        """Formula predefinita per l'affidabilità complessiva"""
        components = [
            self.engine.get('reliability', {}).get('mtbf', 0),
            self.radar.get('reliability', {}).get('mtbf', 0),
            self.radio_nav.get('reliability', {}).get('mtbf', 0),
            self.avionics.get('reliability', {}).get('mtbf', 0),
            self.hydraulic.get('reliability', {}).get('mtbf', 0)
        ]
        return sum(components) / len(components)

    def _default_maintenance_eval(self):
        """Formula predefinita per il carico di manutenzione"""
        daily = self.engine.get('daily_maintenance_hours', 0)
        daily += self.avionics.get('daily_maintenance_hours', 0)
        daily += self.hydraulic.get('daily_maintenance_hours', 0)
        
        field_repair = self.engine.get('field_repair_hours', 0)
        field_repair += self.radar.get('field_repair_hours', 0)
        field_repair += self.radio_nav.get('field_repair_hours', 0)
        
        return daily + (field_repair * 0.1)  # Ponderazione riparazioni

    # --- Metodi di confronto normalizzati ---
    def get_normalized_radar_score(self):
        scores = [ac.evaluate_radar() for ac in Aircraft_Data._registry]
        return self._normalize(self.evaluate_radar(), scores)

    def get_normalized_speed_score(self):
        scores = [ac.evaluate_speed() for ac in Aircraft_Data._registry]
        return self._normalize(self.evaluate_speed(), scores)

    def get_normalized_reliability_score(self):
        scores = [ac.evaluate_reliability() for ac in Aircraft_Data._registry]
        return self._normalize(self.evaluate_reliability(), scores)

    def get_normalized_maintenance_score(self):
        scores = [ac.evaluate_maintenance() for ac in Aircraft_Data._registry]
        # Min-max invertito: manutenzione più bassa = migliore
        normalized = self._normalize(self.evaluate_maintenance(), scores)
        return 1 - normalized

    def _normalize(self, value, scores):
        if not scores:
            return 0
        min_val = min(scores)
        max_val = max(scores)
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)

    # --- Metodi di utilità ---
    @classmethod
    def update_radar_formula(cls, new_formula):
        cls.RADAR_EVAL_FORMULA = new_formula
        
    @classmethod
    def update_speed_formula(cls, new_formula):
        cls.SPEED_EVAL_FORMULA = new_formula
        
    @classmethod
    def get_all_Aircraft_Data(cls):
        return cls._registry
    
        # Valutazione personalizzata
    def custom_radar_eval(radar):
        return radar['capabilities']['tracking_range'] * 0.7 + radar['capabilities']['multi_target_capacity'] * 0.3

    # Aircraft_Data.update_radar_formula(custom_radar_eval)



# Creazione aeromobile
f16_data = {
    "constructor": "Lockheed Martin",
    "made": "USA",
    "model": "F-16C Block 50",
    "category": "fighter",
    "roles": ["CAP", "Intercept", "SEAD"],
    "engine": {"model": "F110-GE-129", "capabilities": {"thrust": 13000, "fuel_efficiency": 0.8, "type": "jet"}, "reliability": {"mtbf": 500, "mttr": 2}, "daily_maintenance_hours": 2.5, "field_repair_hours": 1.0},
    "radar": {
        "model": "AN/APG-68(V)9",
        "capabilities": {
            "air": {True, {"tracking_range": 160, "acquisition_range": 200, "engagement_range": 150, "multi_target_capacity": 10}},
            "ground": {False, {"tracking_range": 80, "acquisition_range": 100, "engagement_range": 80, "multi_target_capacity": 5}},
            "sea": {False, {"tracking_range": 50, "acquisition_range": 60, "engagement_range": 50, "multi_target_capacity": 3}}},
            "type": "pulse-doppler"},
    "radio_nav": {
        "model": "AN/ARN-118", 
        "capabilities": {"navigation_accuracy": 0.5, "communication_range": 200},
        "reliability": {"mtbf": 600, "mttr": 1.5},
        "daily_maintenance_hours": 1.0,
        "field_repair_hours": 0.5
        },
    "avionics": {
        "model": "AN/ALR-69A",
        "capabilities": {"flight_control": 0.9, "navigation_system": 0.8, "communication_system": 0.85},
        "reliability": {"mtbf": 400, "mttr": 1.2},
        "daily_maintenance_hours": 1.5,
        "field_repair_hours": 0.7
    },
    "hydraulic": {
        "model": "Generic Hydraulic System",
        "capabilities": {"pressure": 3000, "fluid_capacity": 50},
        "reliability": {"mtbf": 200, "mttr": 1.0},
        "daily_maintenance_hours": 1.0,
        "field_repair_hours": 0.5
    },
    "speed_data": {
        "sustained": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 850, "altitude": 5000, "consume": 1200},
        "combat": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 920, "altitude": 3000, "consume": 2500, "time": 120},  # time in minutes
        "emergency": {"metric": "metric", "type_speed": "true_airspeed", "airspeed": 1450, "altitude": 8000, "consume": 4500, "time": 120}  # time in minutes   
    },
    "ordinance": {
        'air_2_air': {'AIM-120': 6},
        'air_2_ground': {'GBU-12': 4},
    }
}

f16 = Aircraft_Data(**f16_data)

# Ottenere punteggi normalizzati
print(f"Radar score: {f16.get_normalized_radar_score():.2f}")
print(f"Speed score: {f16.get_normalized_speed_score():.2f}")
    