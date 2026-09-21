from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Cylinder import Cylinder
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from typing import Literal, List, Dict, Union, Optional, Tuple
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from Code.Dynamic_War_Manager.Source.Context.Context import (
    GROUND_ACTION, 
    AIR_TASK,
    SEA_TASK,
    MILITARY_CATEGORY,    
    MILITARY_FORCES,
    ACTION_TASKS,
    GROUND_WEAPON_TASK
)

# LOGGING --
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name = __name__, class_name = 'Mobile').logger


# ── PROFILO DI VELOCITA' CANONICO ──────────────────────────────────────────────
#
# SPEED_SCHEMA — forma di `Mobile.speed`. Tutte le velocita' sono in METRI AL SECONDO:
# il core fissa le proprie unita' e sono i registry (o l'adapter del simulatore) a
# convertire. I dati sorgente NON sono omogenei — Vehicle_Data e' in km/h o mph,
# Ship_Data in nodi, Aircraft_Data in km/h o mph e per giunta come IAS o TAS a una
# quota di riferimento — e questa e' la ragione per cui la conversione sta qui e una
# volta sola.
#
#   {
#       "nominal":  float | None,   # regime sostenuto / di crociera  [m/s]
#       "max":      float | None,   # regime massimo                  [m/s]
#
#       # solo Vehicle: regime fuoristrada, stessa forma
#       "off_road": {"nominal": float | None, "max": float | None},
#
#       # solo Aircraft: quota [m] a cui le velocita' sopra sono valide. Le velocita'
#       # aeronautiche dipendono dalla quota, quindi il dato senza la sua quota di
#       # riferimento non e' interpretabile.
#       "reference_altitude": float | None,
#   }
#
SPEED_REGIME_KEYS = ("nominal", "max")
SPEED_PROFILE_KEYS = ("nominal", "max", "off_road", "reference_altitude")


def default_speed_profile(off_road: bool = False) -> Dict:
    """Profilo di velocita' vuoto ma ben formato. Nuovo ad ogni chiamata."""
    profile: Dict = {key: None for key in SPEED_REGIME_KEYS}

    if off_road:
        profile["off_road"] = {key: None for key in SPEED_REGIME_KEYS}

    return profile


def _speed_to_meters_per_second(value: float, metric: str) -> float:
    """Converte una velocita' dall'unita' dichiarata dal registry a m/s.

    metric: 'metric' -> km/h, 'imperial' -> mph, 'nautical' -> nodi.
    """
    if metric == 'metric':
        return Utility.kmh_2_meters_per_second(value)

    if metric == 'imperial':
        return Utility.mph_2_meters_per_second(value)

    if metric == 'nautical':
        return Utility.knots_2_meters_per_second(value)

    raise ValueError(f"metric must be 'metric', 'imperial' or 'nautical', got {metric!r}")


# ASSET
class Mobile(Asset) :    

    def __init__(self, block: Block, 
                 name: Optional[str] = None, 
                 description: Optional[str] = None, 
                 category: Optional[str] = None, 
                 asset_type:Optional[str] = None, 
                 functionality: Optional[str] = None, 
                 cost: Optional[int] = None, 
                 value: Optional[int] = None, 
                 resources_assigned: Optional[Payload] = None, 
                 resources_to_self_consume: Optional[Payload] = None, 
                 payload: Optional[Payload] = None, 
                 position: Optional[Point3D] = None, 
                 volume: Optional[Volume] = None, 
                 crytical: Optional[bool] = False, 
                 repair_time: Optional[int] = 0, 
                 role: Optional[str] = None, 
                 speed: Optional[Dict] = None, 
                 range: Optional[float] = None,                  
                 dcs_unit_data: Optional[dict] = None):   
            

            super().__init__(block=block, name=name, description=description, category=category, asset_type=asset_type, functionality=functionality, cost=cost, value=value, resources_assigned=resources_assigned, resources_to_self_consume=resources_to_self_consume, payload=payload, position=position, volume=volume, crytical=crytical, repair_time=repair_time, role=role, dcs_unit_data=dcs_unit_data) 
     

            # propriety   
            # speed: profilo cinematico canonico, SEMPRE in m/s (v. SPEED_SCHEMA).
            # Il default era un dizionario mutabile condiviso fra tutte le istanze: ora
            # se ne costruisce uno nuovo ad ogni costruzione.
            if speed is None:
                self._speed = default_speed_profile()
            else:
                ok, msg = Mobile._validate_speed(speed)
                if not ok:
                    raise ValueError(msg)
                self._speed = speed
            self._range = range
            self._weapon = {}
            self._combat_power = {force: {task: 0.0 for task in ACTION_TASKS[force]} 
                for force in MILITARY_FORCES}
            """
            combat_power = {    "air": {"CAP": 0.0, "Intercept": 0.0, "Pinpoint_Strike": 0.0, ...},
            
                                "ground": {"Attack": 0.0 , "Defense": 0.0},
                                
                                "sea": {"Attack": 0.0 , "Defense": 0.0}
                                
                            }"""
            
            
            if dcs_unit_data: 
                result = self.checkParamDCS(dcs_unit_data)
                if self.checkParamDCS(dcs_unit_data): # update property with dcs_unit_data if defined 
                    self._nome = dcs_unit_data["unit_name"]
                    self._id = dcs_unit_data["unitId"]                
                    self._position = Point3D(dcs_unit_data["unit_x"], dcs_unit_data["unit_y"], dcs_unit_data["unit_alt"])# att: nella gestione dello z devi tener conto se BARO o ASL
                    self._health = dcs_unit_data["unit_health"]
                else:
                    raise Exception(f"Not valid DCS_DATA {result} . DCS compatibility could be compromised.")
            else:
                logger.warning("Not valid DCS_DATA. DCS compatibility could be compromised.")

               
            # Association    
                       
            # check input parameters
            
    # methods

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, param):
        # NB: si valida con _validate_speed e non con checkParam, perche' Vehicle, Ship e
        # Aircraft sovrascrivono checkParam con firme che non accettano 'speed' (vedi
        # Vehicle.checkParam(category, asset_type), Ship/Aircraft.checkParam(asset_type)):
        # self.checkParam(speed=...) sollevava quindi TypeError ad ogni assegnazione.
        ok, msg = Mobile._validate_speed(param)

        if not ok:
            raise ValueError(msg)

        self._speed = param
        return True
    
    

    def combat_power(self, force: Optional[str] = None, action: Optional[str] = None) -> Optional[Union[Dict, float]]:
        """
        Returns the value contained in self._combat_power as a function of the specified force and action.

        :param force: A string specifying the type of military force (e.g., "ground", "air", "sea") belonging to Context.MILITARY_FORCES.
        :type force: Optional[str]
        :param action: A string specifying the military action (e.g., "Attack", "Defense", etc.) belonging to Context.ACTION_TASKS[force].
        :type action: Optional[str]
        :return: The value contained in self._combat_power as a function of the specified force and action.
        :rtype: Dict | float | None
        
        -------------------------------
        
        Restituisce il valore contenuto in self._combat_power in funzione del force e dell'action specificati.
        
        :param force: stringa che specifica il tipo di forza militare (ad esempio, "ground", "air", "sea") appartenente a Context.MILITARY_FORCES.
        :type force: Optional[str]
        :param action: stringa che specifica l'azione militare (ad esempio, "Attack", "Defense", ecc.) appartenente a Context.ACTION_TASKS[force].
        :type action: Optional[str]
        :return: il valore contenuto in self._combat_power in funzione del force e dell'action specificati.
        :rtype: Dict | float | None
        """

        if force is not None and not isinstance(force, str):
            raise TypeError(f"Expected str instance, got {type(force).__name__}")

        if force is not None and force not in MILITARY_FORCES:
            raise ValueError(f"force must be: {MILITARY_FORCES!r}")

        if action is not None and not isinstance(action, str):
            raise TypeError(f"Expected str instance, got {type(action).__name__}")

        if force is not None:
            admit_task = [task for task in ACTION_TASKS[force]]
            if action is not None and action not in admit_task:
                raise ValueError(f"action must be: {admit_task}")

        if force and action:
            return self._combat_power[force][action] # return float

        if force:
            return self._combat_power[force] # return Dict

        if action:
            result = {}
            for force in MILITARY_FORCES:
                for task in ACTION_TASKS[force]:
                    if action == task:
                        result[force]={task: self._combat_power[force][action]
                                       }
            return result # return Dict

        return self._combat_power   # return Dict

        #return result

    def set_combat_power_value(self, combat_power: Dict):
        """
        Assigns the combat_power value to self._combat_power.
        Combat_power is calculated in derived classes (Vehicle, Ship, Aircraft, etc.)

        Args:
        combat_power (Dict): Value to be assigned to self._combat_power

        Raises:
        TypeError: The combat_power argument is not of type Dict
        TypeError: Combat_power does not have the correct keys

        ------------------------------
        
        Assegna il valore della combat_power a self._combat_power.
        Il calcolo del valore della combat_power viene effettuato nelle classi derivate (Vehicle, Ship, Aircraft, ecc.)

        Args:
            combat_power (Dict): valore che si vuole assegnare a self._combat_power

        Raises:
            TypeError: l'argomento combat_power non è di tipo Dict
            TypeError: combat_power non ha le chiavi corrette           
        """

        if not isinstance(combat_power, Dict):
            raise TypeError(f"Expected Dict instance, got {type(combat_power).__name__}")
        
        #keys = [key in MILITARY_FORCES for key in combat_power.keys()]

        if any(key in MILITARY_FORCES for key in combat_power.keys()):
            for force in combat_power.keys():
                if isinstance(combat_power[force], Dict):
                    if not any(key in ACTION_TASKS[force] for key in combat_power[force].keys()):
                        raise TypeError(f"Unexpected combat_power[{force}].keys: {combat_power}")
                else:
                    raise TypeError(f"Expected Dict, got {type(combat_power[force].value()).__name__}")
        else:
            raise TypeError(f"Unexpected combat_power.keys, got {combat_power.keys()}")
        
        self._combat_power = combat_power

    @staticmethod
    def _validate_speed(profile) -> Tuple[bool, str]:
        """Valida un profilo di velocita' contro SPEED_SCHEMA. Non usa lo stato dell'istanza."""
        if not isinstance(profile, dict):
            return (False, f"Bad Arg: speed must be a dict, got {type(profile).__name__}")

        def _valid_value(value) -> bool:
            if value is None:
                return True
            # bool e' sottoclasse di int: va rifiutato esplicitamente
            return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0

        for key, value in profile.items():
            if key not in SPEED_PROFILE_KEYS:
                return (False, f"Unexpected speed key: {key!r}. Allowed keys: {list(SPEED_PROFILE_KEYS)}")

            if key == "off_road":
                if value is None:
                    continue

                if not isinstance(value, dict):
                    return (False, f"Bad Arg: speed['off_road'] must be a dict, got {type(value).__name__}")

                for sub_key, sub_value in value.items():
                    if sub_key not in SPEED_REGIME_KEYS:
                        return (False, f"Unexpected speed['off_road'] key: {sub_key!r}. Allowed keys: {list(SPEED_REGIME_KEYS)}")

                    if not _valid_value(sub_value):
                        return (False, f"Bad Arg: speed['off_road'][{sub_key!r}] must be a non-negative number or None, got {sub_value!r}")

                continue

            if not _valid_value(value):
                return (False, f"Bad Arg: speed[{key!r}] must be a non-negative number or None, got {value!r}")

        return (True, "OK")

    def speed_profile_from_registry(self) -> Optional[Dict]:
        """Costruisce il profilo di velocita' canonico (m/s) dai dati del registry del modello.

        E' il ponte che mancava: i dati esistono da sempre in Vehicle_Data / Ship_Data /
        Aircraft_Data, ma nessuna riga di codice li portava mai sull'istanza, quindi
        `asset.speed` restava il placeholder a None e ogni calcolo cinematico a valle
        (Military._get_nominal_speed, time_to_direct_line_attack, Route.travelTime)
        lavorava su 0 o None.

        Ritorna None — e non solleva — se il modello non e' noto o non ha speed_data:
        stesso contratto di air_defense_volume() e combat_range().
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as _AircraftData

        model = getattr(self, '_model', None)

        if model is None:
            logger.warning("speed_profile_from_registry: _model not set")
            return None

        # Il dispatch e' sul registry che risponde, non su isinstance(record, ...): i tre
        # registry hanno schemi di speed_data diversi ed e' l'appartenenza al registry a
        # determinare quale leggere.
        for registry, builder in ((_VehicleData._registry, self._vehicle_speed_profile),
                                  (_ShipData._registry, self._ship_speed_profile),
                                  (_AircraftData._registry, self._aircraft_speed_profile)):
            data_record = registry.get(model)

            if data_record is None:
                continue

            speed_data = getattr(data_record, 'speed_data', None)

            if not speed_data:
                logger.warning(f"speed_profile_from_registry: no speed_data for model {model!r}")
                return None

            return builder(speed_data)

        logger.warning(f"speed_profile_from_registry: no registry entry for model {model!r}")
        return None

    @staticmethod
    def _regime_speed(speed_data: Dict, regime: str) -> Optional[float]:
        """Velocita' [m/s] di un regime di Vehicle_Data/Ship_Data ({'metric','speed',...})."""
        data = speed_data.get(regime)

        if not data:
            return None

        value = data.get('speed')

        if value is None:
            return None

        return _speed_to_meters_per_second(float(value), data.get('metric'))

    def _vehicle_speed_profile(self, speed_data: Dict) -> Dict:
        """Vehicle_Data: regimi 'sustained' / 'max' / 'off_road', in km/h o mph.

        Il fuoristrada ha un unico regime nei dati, quindi nominal e max off-road
        coincidono: e' il dato a non distinguerli, non una semplificazione introdotta qui.
        """
        profile = default_speed_profile(off_road=True)
        profile["nominal"] = self._regime_speed(speed_data, 'sustained')
        profile["max"] = self._regime_speed(speed_data, 'max')

        off_road = self._regime_speed(speed_data, 'off_road')
        profile["off_road"]["nominal"] = off_road
        profile["off_road"]["max"] = off_road

        return profile

    def _ship_speed_profile(self, speed_data: Dict) -> Dict:
        """Ship_Data: regimi 'sustained' / 'max' / 'flank', tipicamente in nodi.

        'max' canonico = il piu' alto fra 'max' e 'flank': flank e' il regime di punta
        effettivo di una nave, e ignorarlo sottostimerebbe la velocita' massima reale.
        """
        profile = default_speed_profile()
        profile["nominal"] = self._regime_speed(speed_data, 'sustained')

        candidates = [value for value in (self._regime_speed(speed_data, 'max'),
                                          self._regime_speed(speed_data, 'flank'))
                      if value is not None]
        profile["max"] = max(candidates) if candidates else None

        return profile

    def _aircraft_speed_profile(self, speed_data: Dict) -> Dict:
        """Aircraft_Data: regimi 'sustained' / 'combat' / 'emergency'.

        Ogni regime porta {'metric', 'type_speed', 'airspeed', 'altitude', ...}. Se la
        velocita' e' indicata (IAS) va prima convertita in vera (TAS) alla sua quota —
        Utility.true_air_speed restituisce sempre km/h — e solo dopo in m/s.

        'max' canonico = il piu' alto fra 'combat' ed 'emergency'; 'reference_altitude'
        e' la quota del regime sostenuto, senza la quale le velocita' aeronautiche non
        sono interpretabili.
        """
        def _airspeed_ms(regime: str) -> Optional[float]:
            data = speed_data.get(regime)

            if not data:
                return None

            airspeed = data.get('airspeed')

            if airspeed is None:
                return None

            metric = data.get('metric')
            type_speed = data.get('type_speed')

            if type_speed == 'indicated_airspeed':
                # true_air_speed converte l'eventuale input imperiale e ritorna km/h
                return Utility.kmh_2_meters_per_second(
                    Utility.true_air_speed(float(airspeed), data.get('altitude') or 0, metric))

            if type_speed == 'true_airspeed':
                return _speed_to_meters_per_second(float(airspeed), metric)

            raise ValueError(f"Invalid type_speed: {type_speed!r}. Expected 'indicated_airspeed' or 'true_airspeed'.")

        profile = default_speed_profile()
        profile["nominal"] = _airspeed_ms('sustained')

        candidates = [value for value in (_airspeed_ms('combat'), _airspeed_ms('emergency'))
                      if value is not None]
        profile["max"] = max(candidates) if candidates else None

        sustained = speed_data.get('sustained') or {}
        altitude = sustained.get('altitude')
        profile["reference_altitude"] = float(altitude) if altitude is not None else None

        return profile

    def load_speed_from_registry(self) -> bool:
        """Popola `self.speed` dal registry del modello. True se il profilo e' stato caricato.

        Chiamata dai costruttori di Vehicle/Ship/Aircraft dopo che `_model` e' stato
        assegnato. Se il modello non e' noto il profilo resta quello di default (tutto
        None) e si ritorna False, senza sollevare: un asset con un modello sconosciuto
        deve restare costruibile, come per combat_range()/air_defense_volume().
        """
        profile = self.speed_profile_from_registry()

        if profile is None:
            return False

        self._speed = profile
        return True

    def air_defense_volume(self) -> Optional[Cylinder]:
        """Return the Cylinder representing the engagement envelope of this AD asset.

        radius    = max engagement range across all AD weapons (metres)
        height    = max_altitude - min_altitude (metres AGL)
        bottom_center.z = asset position.z + min_altitude across all AD weapons
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import GROUND_WEAPONS
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS

        if self._position is None:
            logger.warning("air_defense_volume: position not set")
            return None

        model = getattr(self, '_model', None)
        if model is None:
            logger.warning("air_defense_volume: _model not set")
            return None

        data_record = _VehicleData._registry.get(model) or _ShipData._registry.get(model)
        if data_record is None:
            logger.warning(f"air_defense_volume: no registry entry for model {model!r}")
            return None

        is_ship = isinstance(data_record, _ShipData)

        max_range = 0.0
        min_alt = float('inf')
        max_alt = 0.0

        for weapon_type, weapon_list in data_record.weapons.items():
            if is_ship:
                if weapon_type != 'MISSILES_SAM':
                    continue
                weapon_db = SHIP_WEAPONS.get('MISSILES_SAM', {})
            else:
                if weapon_type not in ('AA_CANNONS', 'MISSILES'):
                    continue
                weapon_db = GROUND_WEAPONS.get(weapon_type, {})

            for weapon_model, _qty in weapon_list:
                wdata = weapon_db.get(weapon_model)
                if ( wdata is None or 'min_altitude' not in wdata or 'max_altitude' not in wdata ) or ( 'task' in wdata and GROUND_WEAPON_TASK['Anti_Air'] not in wdata['task'] ):
                    continue

                w_min = float(wdata['min_altitude'])
                w_max = float(wdata['max_altitude'])
                if w_max <= 0.0:
                    continue

                if is_ship:
                    w_range = float(wdata.get('range', 0)) * 1000.0  # km → m
                else:
                    w_range = float(wdata.get('range', {}).get('direct', 0))  # m

                max_range = max(max_range, w_range)
                min_alt = min(min_alt, w_min)
                max_alt = max(max_alt, w_max)

        if max_range == 0.0:
            logger.warning(f"air_defense_volume: no AD weapons with altitude data for model {model!r}")
            return None

        if min_alt == float('inf'):
            min_alt = 0.0

        pos = self._position
        bottom_center = Point3D(float(pos.x), float(pos.y), float(pos.z) + min_alt)
        return Cylinder(center=bottom_center, radius=max_range, height=max_alt - min_alt)

    def combat_range(self) -> Optional[float]:
        """Return max engagement range (metres) across all ground-attack / naval-attack weapons.

        Vehicle offensive types: CANNONS, ARTILLERY, MORTARS, ROCKETS, MISSILES (non-AA).
        Ship offensive types:    MISSILES_ASM, MISSILES_TORPEDO, GUNS.
        MISSILES with min_altitude (SAM) are skipped via the same discriminator used in
        air_defense_volume().  Ship weapon ranges are stored in km and converted to metres.
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import GROUND_WEAPONS
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS

        model = getattr(self, '_model', None)
        if model is None:
            logger.warning("combat_range: _model not set")
            return None

        data_record = _VehicleData._registry.get(model) or _ShipData._registry.get(model)
        if data_record is None:
            logger.warning(f"combat_range: no registry entry for model {model!r}")
            return None

        is_ship = isinstance(data_record, _ShipData)

        _GROUND_ATTACK = ('CANNONS', 'ARTILLERY', 'MORTARS', 'ROCKETS', 'MISSILES', 'AUTO_CANNONS')
        _SHIP_ATTACK   = ('MISSILES_ASM', 'MISSILES_TORPEDO', 'GUNS')

        max_range = 0.0

        for weapon_type, weapon_list in data_record.weapons.items():
            if is_ship:
                if weapon_type not in _SHIP_ATTACK:
                    continue
                weapon_db = SHIP_WEAPONS.get(weapon_type, {})
            else:
                if weapon_type not in _GROUND_ATTACK:
                    continue
                weapon_db = GROUND_WEAPONS.get(weapon_type, {})

            for weapon_model, _qty in weapon_list:
                wdata = weapon_db.get(weapon_model)
                if wdata is None:
                    continue

                # MISSILES that carry min_altitude are SAM weapons → skip
                if ( weapon_type == 'MISSILES' and 'min_altitude' in wdata ) or ( 'task' in wdata and GROUND_WEAPON_TASK['Anti_Air'] in wdata['task'] ):
                    continue

                raw = wdata.get('range', 0)
                if isinstance(raw, dict):
                    # dict format {'direct': N, 'indirect': N} — used by CANNONS/ARTILLERY/MORTARS/MISSILES
                    w_range = float(max(raw.get('direct', 0), raw.get('indirect', 0)))
                else:
                    # plain number — ROCKETS (metres) or ship weapons (km → metres)
                    w_range = float(raw) * (1000.0 if is_ship else 1.0)

                max_range = max(max_range, w_range)

        if max_range == 0.0:
            logger.warning(f"combat_range: no offensive weapons found for model {model!r}")
            return None

        return max_range

    @staticmethod
    def checkParam(speed: Optional[Dict] = None, fire_range: Optional[float] = None) -> Tuple[bool, str]:
        """Return True if type compliance of the parameters is verified.

        Era dichiarata senza `self` pur essendo un metodo di istanza: ogni chiamata
        `self.checkParam(...)` legava `self` al primo parametro posizionale. E' ora
        esplicitamente statica (non usa lo stato dell'istanza) e valida lo schema
        canonico di `speed` (v. SPEED_SCHEMA), non piu' le chiavi obsolete
        ["cruise", "max"] che nessun produttore di dati ha mai usato.
        """
        if speed is not None:
            ok, msg = Mobile._validate_speed(speed)
            if not ok:
                return (False, msg)

        if fire_range is not None and not isinstance(fire_range, (int, float)):
            return (False, "Bad Arg: fire_range must be a number")

        return (True, "OK")

    def checkParamDCS(data: dict):
        if data["unit_index"] and not isinstance(data["unit_index"], str):
            return (False, "Bad Arg: unit_index must be a str")        
        if data["unit_name"]  and not isinstance(data["unit_name"], str):
            return (False, "Bad Arg: unit_name must be a str")        
        if data["unit_type"]  and not isinstance(data["unit_type"], str):
            return (False, "Bad Arg: unit_type must be a str")          
        if data["unit_unitId"]  and not isinstance(data["unit_unitId"], int):
            return (False, "Bad Arg: unit_unitId must be a int")        
        if data["unit_communication"]  and not isinstance(data["unit_communication"], bool):
            return (False, "Bad Arg: unit_communication must be a bool")        
        if data["unit_lateActivation"]  and not isinstance(data["unit_lateActivation"], bool):
            return (False, "Bad Arg: unit_lateActivation must be a bool")        
        if data["unit_start_time"]  and not isinstance(data["unit_start_time"], int):
            return (False, "Bad Arg: unit_start_time must be a int")        
        if data["unit_frequency"]  and not isinstance(data["unit_frequency"], float):
            return (False, "Bad Arg: unit_frequency must be a float")        
        if data["unit_x"]  and not isinstance(data["unit_x"], float):
            return (False, "Bad Arg: unit_x must be a float")        
        if data["unit_y"]  and not isinstance(data["unit_y"], float):    
            return (False, "Bad Arg: unit_y must be a float")        
        if data["unit_alt"]  and not isinstance(data["unit_alt"], float):
            return (False, "Bad Arg: unit_alt must be a float")        
        if data["unit_alt_type"]  and not isinstance(data["unit_alt_type"], str):
            return (False, "Bad Arg: unit_alt_type must be a str")                
        if data["heading"]  and not isinstance(data["heading"], int):
            return (False, "Bad Arg: heading must be a int")               
        if data["unit_speed"]  and not isinstance(data["unit_speed"], float):
            return (False, "Bad Arg: unit_speed must be a float")        
        if data["unit_hardpoint_racks"]  and not isinstance(data["unit_hardpoint_racks"], int):
            return (False, "Bad Arg: unit_hardpoint_racks must be a int")        
        if data["unit_livery_id"]  and not isinstance(data["unit_livery_id"], int):
            return (False, "Bad Arg: unit_livery_id must be a int")        
        if data["unit_psi"]  and not isinstance(data["unit_psi"], float):
            return (False, "Bad Arg: unit_psi must be a float")        
        if data["unit_skill"]  and not isinstance(data["unit_skill"], str):
            return (False, "Bad Arg: unit_skill must be a str")
        if data["unit_onboard_num"]  and not isinstance(data["unit_onboard_num"], int):
            return (False, "Bad Arg: unit_onboard_num must be a int")
        if data["unit_payload"]  and not isinstance(data["unit_payload"], dict):
            return (False, "Bad Arg: unit_payload must be a dict")
        if data["unit_callsign"]  and not isinstance(data["unit_callsign"], dict):
            return (False, "Bad Arg: unit_callsign must be a dict")
        return (True, "DCS_DATA OK")



