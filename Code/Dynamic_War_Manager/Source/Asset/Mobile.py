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


# ── PERCEZIONE: SENSORI E RAGGI DI RILEVAMENTO ────────────────────────────────
#
# I tre registry (Vehicle_Data, Ship_Data, Aircraft_Data) descrivono i sensori con
# un'unica forma, gia' letta da `_radar_eval`/`_TVD_eval`:
#
#   record.<sensore>['capabilities'][mode] = (
#       bool_capacita',
#       {'tracking_range': km, 'acquisition_range': km,
#        'engagement_range': km, 'multi_target_capacity': int}
#   )
#
# con `mode` in DETECTION_MODES. I raggi sono in CHILOMETRI in tutti e tre i registry;
# `detection_range` li restituisce in METRI, come combat_range() e air_defense_volume(),
# perche' il core lavora in metri e secondi.
#
# Casi normali (non errori) da attraversare senza sollevare:
#   * `radar`/`TVD` == False o None  -> il mezzo non ha quel sensore (es. un carro);
#   * `TVD` assente come attributo   -> Ship_Data non descrive sensori ottici;
#   * capabilities[mode][0] == False -> sensore presente ma cieco su quella dimensione;
#   * capabilities[mode][1] == {}    -> capacita' dichiarata senza dati (Ship_Data 'ground').
DETECTION_MODES = tuple(ACTION_TASKS.keys())          # ('ground', 'air', 'sea')
DETECTION_SENSORS = ("radar", "TVD")
DETECTION_RANGE_TYPES = ("acquisition_range", "tracking_range", "engagement_range")

# Il rilevamento e' l'acquisizione: il tracking e l'ingaggio sono stadi successivi e piu'
# corti. Lo scheduler dei contatti (Fase 3) chiede "quando questo osservatore vede il
# bersaglio", quindi il default e' l'acquisizione.
DEFAULT_DETECTION_RANGE_TYPE = "acquisition_range"


# ── SCORTA DI MUNIZIONI (motore di sessioni virtuali, Fase 4) ─────────────────
#
# DECISIONE (2026-09-23, wiki decisions/risolutore-ingaggio-salva-fase4 R3). Prima di
# questa, il progetto non aveva in nessuna forma una scorta che si esaurisce: `ammo_type`
# e `AMMO_PARAM` dei registri d'arma sono parametri statici di punteggio. Qui nasce UN
# contatore AGGREGATO PER ASSET (non per arma installata, non per tipo di munizione):
#
#   * consumo esplicito e deterministico — N colpi sparati = N in meno, nessuna
#     estrazione casuale; la sola varianza del combattimento resta in
#     Logic/Damage_Model.resolve_hit;
#   * a zero l'asset non spara piu' ma resta un bersaglio valido: la salute non c'entra
#     (coerente con Asset.apply_damage, che non tocca le munizioni);
#   * il rifornimento e' FUORI SCOPE (materia del ciclo di campagna): qui non esiste
#     alcun metodo che aumenti la scorta, salvo il setter per inizializzazione/persistenza.
#
# Sede: Mobile e non Asset, perche' e' il livello che possiede le armi (combat_range,
# air_defense_volume leggono qui i registri d'arma); una Structure non spara.
#
# Valore iniziale: il registro del modello. In Vehicle_Data e Ship_Data la forma e'
#     record.weapons = {weapon_type: [(weapon_model, quantita'), ...]}
# e per quasi tutti i tipi la quantita' e' il numero di colpi/missili imbarcati (lo
# conferma l'uso che ne fanno Vehicle_Data._weapon_eval e Ship_Data.AMMO_LOAD_REFERENCE:
# "42" colpi del 2A46M di un T-72, "6" missili 9M33 di un Osa). Fanno eccezione i tipi in
# UNIT_COUNTED_WEAPON_TYPES, dove la quantita' e' il NUMERO DI ARMI installate (cosi' li
# commentano gli stessi registri), non una scorta: vengono esclusi dalla somma, perche'
# sommare "1 mitragliatrice" a "42 colpi" non ha senso.
# Aircraft_Data non ha un campo `weapons` (l'armamento di un aereo e' il loadout, non il
# modello): per gli aerei la scorta e' derivata dal loadout ASSEGNATO
# (Aircraft.assigned_loadout / Aircraft.ammunition_from_registry, decisione 2026-09-23) e
# resta None ("non modellata") finche' nessun loadout e' assegnato.
#
# None = scorta NON MODELLATA: nessun vincolo di consumo (stessa semantica di
# Military.weapons_availability, dove None salta il filtro invece di forzarlo a zero). E'
# l'opzione reversibile: un asset senza dato non viene reso inerme per mancanza di dato.
UNIT_COUNTED_WEAPON_TYPES = ('MACHINE_GUNS', 'CIWS')


# ── CARBURANTE (motore di sessioni virtuali, Fase 5) ──────────────────────────
#
# Prima di questa sezione il progetto non aveva alcun contatore di carburante: il solo
# `engine.capabilities.fuel_efficiency` dei registri e' un PUNTEGGIO adimensionale di
# selezione dell'asset (0.3-0.8 per i velivoli, 1.0 per le navi nucleari; il docstring di
# Aircraft_Data lo chiama "km/l", ma i valori non lo sono), non un consumo fisico. Qui nasce
# un contatore AGGREGATO PER ASSET con la stessa disciplina delle munizioni:
#
#   * consumo esplicito e deterministico, proporzionale alla distanza percorsa — nessuna
#     estrazione casuale;
#   * a zero l'asset non si muove piu' ma resta un asset valido: la salute non c'entra;
#   * il rifornimento e' FUORI SCOPE (ciclo di campagna): nessun metodo aumenta il
#     carburante, salvo il setter per inizializzazione/persistenza e il riarmo implicito
#     quando a un aereo viene (ri)assegnato un loadout, come per le munizioni.
#
# UNITA': FRAZIONE DEL CARICO PIENO, in [0, 1] (FUEL_FULL = 1.0), per TUTTI gli asset.
# Scelta motivata dai dati, non di comodo:
#   1. Vehicle_Data e Ship_Data non dichiarano una capacita' del serbatoio. Dichiarano pero'
#      l'AUTONOMIA (`range`: km per i veicoli, miglia nautiche per le navi), che e' proprio
#      il dato che serve: col pieno si percorrono `range` metri. Il consumo per metro e'
#      quindi 1/autonomia, senza alcuna costante inventata.
#   2. Per gli aerei i raggi dei loadout (`cruise/attack.range['fuel_100%']`) valgono per
#      il carico COMPLETO — interno PIU' serbatoi esterni se imbarcati (commento di testa di
#      Aircraft_Loadouts) — mentre `fuel_internal_max` e' il solo carburante interno. Un
#      contatore in kg inizializzato a `fuel_internal_max` e consumato col raggio del
#      loadout sovrastimerebbe l'autonomia di chi porta serbatoi. La frazione del carico
#      pieno e' coerente con il dato di autonomia per costruzione; la massa resta
#      ricavabile con Aircraft.fuel_capacity_kg() (frazione x capacita').
#   3. Una sola unita' per tutti gli asset rende sommabili/confrontabili i FuelEvent del
#      SessionOutcome, come il contatore aggregato delle munizioni.
#
# Regimi: gli stessi di SPEED_REGIME_KEYS ('nominal', 'max'). Per gli aerei 'nominal' legge
# il profilo `cruise` del loadout e 'max' il profilo `attack`; per veicoli e navi il registro
# ha un'unica autonomia, usata per entrambi (limite dichiarato: sottostima il consumo al
# regime massimo — e' il dato a non distinguere, non una semplificazione introdotta qui).
#
# None = carburante NON MODELLATO: nessun vincolo di movimento (stessa semantica delle
# munizioni). Casi: modello ignoto, autonomia mancante, aereo senza loadout assegnato,
# propulsione nucleare (v. NUCLEAR_ENGINE_TYPES).
FUEL_FULL = 1.0
FUEL_REGIMES = SPEED_REGIME_KEYS
DEFAULT_FUEL_REGIME = "nominal"

# Residui sotto questa soglia sono zero: evita che l'aritmetica in virgola mobile lasci un
# asset "quasi vuoto" (1e-17) che has_fuel() considererebbe ancora in grado di muoversi.
FUEL_EPS = 1e-12

# Miglio nautico internazionale [m]: e' la definizione, non una stima (Ship_Data.range e' in nm).
NAUTICAL_MILE_M = 1852.0

# Propulsione nucleare: l'autonomia di Ship_Data per questi tipi e' "convenzionalmente
# 20 000 nm" (commento del registro stesso), cioe' un segnaposto per "praticamente
# illimitata", non un dato. Trattarla come carburante non modellato (None) e' piu' onesto
# che far esaurire una portaerei nucleare dopo 37 000 km.
NUCLEAR_ENGINE_TYPES = ('nuclear',)


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
            # Scorta di munizioni aggregata [colpi]; None = non modellata (v. commento
            # UNIT_COUNTED_WEAPON_TYPES). Popolata da load_ammunition_from_registry(),
            # chiamata dai costruttori di Vehicle/Ship/Aircraft dopo aver assegnato _model.
            self._ammunition: Optional[int] = None
            # Carburante [frazione del carico pieno, 0..1]; None = non modellato (v. commento
            # FUEL_FULL). Popolato da load_fuel_from_registry(), come le munizioni.
            self._fuel: Optional[float] = None
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

    # ── munizioni ─────────────────────────────────────────────────────────────

    @property
    def ammunition(self) -> Optional[int]:
        """Scorta di munizioni aggregata [colpi], o None se non modellata.

        V. il commento UNIT_COUNTED_WEAPON_TYPES in testa al modulo per la semantica.
        """
        return getattr(self, '_ammunition', None)

    @ammunition.setter
    def ammunition(self, value: Optional[int]) -> None:
        """Imposta la scorta (inizializzazione, persistenza). None = non modellata.

        Non e' un canale di rifornimento: il rifornimento e' fuori scope (materia del
        ciclo di campagna). Il consumo passa esclusivamente da consume_ammunition().
        """
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
            raise TypeError(f"ammunition must be an int or None, got {type(value).__name__}")

        if value is not None and value < 0:
            raise ValueError(f"ammunition must be non-negative, got {value}")

        self._ammunition = value

    def has_ammunition(self) -> bool:
        """True se l'asset puo' ancora sparare per munizioni: scorta > 0 o non modellata."""
        stock = self.ammunition
        return stock is None or stock > 0

    def consume_ammunition(self, rounds: int) -> int:
        """Consuma `rounds` colpi dalla scorta. Ritorna i colpi effettivamente consumati.

        Deterministico: nessuna estrazione casuale. Se la scorta e' inferiore alla richiesta
        si consuma il residuo (la scorta non va mai sotto zero) e il valore di ritorno lo
        dice al chiamante; se la scorta non e' modellata (None) non c'e' nulla da
        decrementare e si ritorna `rounds` — la richiesta e' soddisfatta per definizione.

        Raises:
            TypeError: `rounds` non intero (errore di programmazione).
            ValueError: `rounds` negativo — il rifornimento non passa di qui.
        """
        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError(f"rounds must be an int, got {type(rounds).__name__}")

        if rounds < 0:
            raise ValueError(f"rounds must be non-negative (no resupply here), got {rounds}")

        stock = self.ammunition

        if stock is None:
            return rounds

        consumed = min(rounds, stock)
        self._ammunition = stock - consumed

        if consumed < rounds:
            logger.debug(f"consume_ammunition: asset {getattr(self, 'id', None)!r} requested "
                         f"{rounds} rounds, only {consumed} available")

        return consumed

    def ammunition_from_registry(self) -> Optional[int]:
        """Scorta iniziale [colpi] dal registro del modello, o None se non ricavabile.

        Somma le quantita' di `record.weapons` escludendo i tipi in
        UNIT_COUNTED_WEAPON_TYPES (dove la quantita' e' il numero di armi, non di colpi).

        Returns:
            int >= 0, oppure None — senza sollevare, come speed_profile_from_registry() —
            se il modello non e' noto, se il registro non descrive armi (Aircraft_Data),
            o se descrive solo armi contate a unita' (nessun dato di scorta).
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as _AircraftData

        model = getattr(self, '_model', None)

        if model is None:
            logger.debug("ammunition_from_registry: _model not set")
            return None

        data_record = (_VehicleData._registry.get(model)
                       or _ShipData._registry.get(model)
                       or _AircraftData._registry.get(model))

        if data_record is None:
            logger.debug(f"ammunition_from_registry: no registry entry for model {model!r}")
            return None

        weapons = getattr(data_record, 'weapons', None)

        if not isinstance(weapons, dict) or not weapons:
            # Aircraft_Data: l'armamento e' il loadout, non il modello. Dato mancante.
            logger.debug(f"ammunition_from_registry: model {model!r} declares no weapons, "
                         f"ammunition not modelled")
            return None

        total = 0
        counted = False

        for weapon_type, weapon_list in weapons.items():
            if weapon_type in UNIT_COUNTED_WEAPON_TYPES:
                continue

            for item in weapon_list or []:
                if not isinstance(item, (tuple, list)) or len(item) < 2:
                    continue

                quantity = item[1]

                if isinstance(quantity, bool) or not isinstance(quantity, (int, float)) or quantity < 0:
                    continue

                total += int(quantity)
                counted = True

        if not counted:
            logger.debug(f"ammunition_from_registry: model {model!r} has only unit-counted "
                         f"weapons {tuple(weapons)}, ammunition not modelled")
            return None

        return total

    def load_ammunition_from_registry(self) -> bool:
        """Popola la scorta dal registro del modello. True se caricata.

        Chiamata dai costruttori di Vehicle/Ship/Aircraft dopo che `_model` e' stato
        assegnato, stessa disciplina di load_speed_from_registry(): se il dato non c'e' la
        scorta resta None (non modellata) e l'asset resta costruibile.
        """
        stock = self.ammunition_from_registry()

        if stock is None:
            return False

        self._ammunition = stock
        return True

    # ── carburante ────────────────────────────────────────────────────────────

    @property
    def fuel(self) -> Optional[float]:
        """Carburante [frazione del carico pieno, 0..1], o None se non modellato.

        V. il commento FUEL_FULL in testa al modulo per unita' e semantica.
        """
        return getattr(self, '_fuel', None)

    @fuel.setter
    def fuel(self, value: Optional[float]) -> None:
        """Imposta il carburante (inizializzazione, persistenza). None = non modellato.

        Non e' un canale di rifornimento: il rifornimento e' fuori scope (materia del
        ciclo di campagna). Il consumo passa esclusivamente da consume_fuel().

        Raises:
            TypeError: valore non numerico (bool incluso).
            ValueError: valore fuori [0, FUEL_FULL].
        """
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise TypeError(f"fuel must be a number or None, got {type(value).__name__}")

        if value is not None and not 0.0 <= value <= FUEL_FULL:
            raise ValueError(f"fuel must be in [0, {FUEL_FULL}], got {value}")

        self._fuel = float(value) if value is not None else None

    def has_fuel(self) -> bool:
        """True se l'asset puo' ancora muoversi per carburante: > 0 o non modellato."""
        fuel = self.fuel
        return fuel is None or fuel > 0.0

    def consume_fuel(self, amount: float) -> float:
        """Consuma `amount` (frazione del carico pieno). Ritorna la quantita' effettivamente consumata.

        Stessa disciplina di consume_ammunition(): deterministico; se il carburante non basta
        si consuma il residuo (mai sotto zero) e il valore di ritorno lo dice al chiamante;
        se non e' modellato (None) si ritorna `amount` — richiesta soddisfatta per
        definizione. Un residuo inferiore a FUEL_EPS e' azzerato.

        Raises:
            TypeError: `amount` non numerico (errore di programmazione).
            ValueError: `amount` negativo — il rifornimento non passa di qui.
        """
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError(f"amount must be a number, got {type(amount).__name__}")

        if amount < 0:
            raise ValueError(f"amount must be non-negative (no refuelling here), got {amount}")

        amount = float(amount)
        fuel = self.fuel

        if fuel is None:
            return amount

        consumed = min(amount, fuel)
        remaining = fuel - consumed

        if remaining < FUEL_EPS:
            consumed, remaining = fuel, 0.0

        self._fuel = remaining

        if consumed < amount - FUEL_EPS:
            logger.debug(f"consume_fuel: asset {getattr(self, 'id', None)!r} requested {amount:.6f}, "
                         f"only {consumed:.6f} available")

        return consumed

    def fuel_autonomy(self, regime: str = DEFAULT_FUEL_REGIME) -> Optional[float]:
        """Distanza [m] percorribile col carico pieno al regime dato, o None se non ricavabile.

        Dal registro del modello (dispatch sul registry che risponde, come
        speed_profile_from_registry(), perche' le unita' di `range` differiscono):
          * Vehicle_Data: `range` in km -> m. Unico valore per entrambi i regimi.
          * Ship_Data: `range` in miglia nautiche -> m (NAUTICAL_MILE_M). Unico valore per
            entrambi i regimi. None per la propulsione nucleare (NUCLEAR_ENGINE_TYPES).
          * Aircraft_Data: None — l'autonomia di un aereo dipende dal loadout, non dal
            modello (Aircraft.fuel_autonomy la ricava dal loadout assegnato).

        Mai un'eccezione per dati mancanti: None + log, come combat_range().

        Raises:
            ValueError: `regime` fuori da FUEL_REGIMES (errore di programmazione).
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as _AircraftData

        if regime not in FUEL_REGIMES:
            raise ValueError(f"regime must be one of {FUEL_REGIMES!r}, got {regime!r}")

        model = getattr(self, '_model', None)

        if model is None:
            logger.debug("fuel_autonomy: _model not set")
            return None

        for registry, unit_m in ((_VehicleData._registry, 1000.0),
                                 (_ShipData._registry, NAUTICAL_MILE_M),
                                 (_AircraftData._registry, None)):
            data_record = registry.get(model)

            if data_record is None:
                continue

            if unit_m is None:
                logger.debug(f"fuel_autonomy: model {model!r} is an aircraft, autonomy depends "
                             f"on the assigned loadout")
                return None

            engine = getattr(data_record, 'engine', None)
            capabilities = engine.get('capabilities') if isinstance(engine, dict) else None
            engine_type = capabilities.get('type') if isinstance(capabilities, dict) else None

            if engine_type in NUCLEAR_ENGINE_TYPES:
                logger.debug(f"fuel_autonomy: model {model!r} has {engine_type} propulsion, "
                             f"fuel not modelled")
                return None

            autonomy = getattr(data_record, 'range', None)

            if isinstance(autonomy, bool) or not isinstance(autonomy, (int, float)) or autonomy <= 0:
                logger.debug(f"fuel_autonomy: model {model!r} declares no usable range ({autonomy!r})")
                return None

            return float(autonomy) * unit_m

        logger.debug(f"fuel_autonomy: no registry entry for model {model!r}")
        return None

    def fuel_for_distance(self, distance: float, regime: str = DEFAULT_FUEL_REGIME) -> Optional[float]:
        """Carburante [frazione del carico pieno] necessario a percorrere `distance` metri.

            consumo = distance / fuel_autonomy(regime)

        Lineare nella distanza: a velocita' di regime costante e' la lettura diretta del
        dato di autonomia del registro, senza costanti nuove. Il risultato puo' superare
        FUEL_FULL (tratta piu' lunga dell'autonomia): e' il FABBISOGNO, non quanto si puo'
        consumare — il limite lo applica consume_fuel().

        Returns:
            float >= 0, oppure None se l'autonomia non e' ricavabile (carburante non
            modellato per questo asset).

        Raises:
            TypeError/ValueError: `distance` non numerica o negativa; `regime` sconosciuto.
        """
        if isinstance(distance, bool) or not isinstance(distance, (int, float)):
            raise TypeError(f"distance must be a number, got {type(distance).__name__}")

        if distance < 0:
            raise ValueError(f"distance must be non-negative, got {distance}")

        autonomy = self.fuel_autonomy(regime)

        if autonomy is None:
            return None

        return float(distance) / autonomy

    def fuel_range_remaining(self, regime: str = DEFAULT_FUEL_REGIME) -> Optional[float]:
        """Distanza [m] ancora percorribile col carburante residuo, o None se non modellato.

        E' il dato con cui un orchestratore sa dove l'asset si ferma lungo la rotta:
        `fuel x fuel_autonomy(regime)`. None se il carburante o l'autonomia non sono
        modellati (nessun vincolo).
        """
        fuel = self.fuel

        if fuel is None:
            return None

        autonomy = self.fuel_autonomy(regime)

        if autonomy is None:
            return None

        return fuel * autonomy

    def fuel_from_registry(self) -> Optional[float]:
        """Carburante iniziale: FUEL_FULL se l'autonomia e' ricavabile dal registro, altrimenti None.

        Nell'unita' scelta (frazione del carico pieno) il valore iniziale e' sempre il pieno:
        cio' che il registro decide e' SE il carburante e' modellato, cioe' se esiste
        un'autonomia su cui misurare il consumo.
        """
        return FUEL_FULL if self.fuel_autonomy(DEFAULT_FUEL_REGIME) is not None else None

    def load_fuel_from_registry(self) -> bool:
        """Popola il carburante dal registro del modello. True se caricato.

        Chiamata dai costruttori di Vehicle/Ship/Aircraft dopo che `_model` e' stato
        assegnato, stessa disciplina di load_ammunition_from_registry(): se il dato non c'e'
        il carburante resta None (non modellato) e l'asset resta costruibile.
        """
        fuel = self.fuel_from_registry()

        if fuel is None:
            return False

        self._fuel = fuel
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
    def _sensor_range_km(data_record, sensor: str, mode: str, range_type: str) -> Optional[float]:
        """Raggio [km] di un singolo sensore del record di registry, o None se non c'e'.

        Attraversa senza sollevare tutte le forme legittime dei dati (v. commento
        DETECTION_* in testa al modulo): sensore assente, sensore == False/None,
        capabilities mancanti, modo non coperto, dizionario di capacita' vuoto, valore
        nullo o non numerico. None significa sempre "questo sensore non da' un raggio
        utilizzabile su questo modo", non "errore".
        """
        sensor_data = getattr(data_record, sensor, None)

        if not sensor_data or not isinstance(sensor_data, dict):
            return None

        capabilities = sensor_data.get('capabilities')

        if not isinstance(capabilities, dict):
            return None

        capability = capabilities.get(mode)

        # Forma attesa: (bool, dict). Qualunque altra cosa e' un dato malformato: si scarta.
        if not isinstance(capability, (tuple, list)) or len(capability) < 2:
            return None

        if not capability[0] or not isinstance(capability[1], dict):
            return None

        value = capability[1].get(range_type)

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None

        value = float(value)

        return value if value > 0.0 else None

    def detection_range(self, mode: str, sensor: Optional[str] = None,
                        range_type: str = DEFAULT_DETECTION_RANGE_TYPE) -> Optional[float]:
        """Raggio di rilevamento [metri] di questo asset contro bersagli di dimensione `mode`.

        E' il ponte che mancava fra i dati sensore dei registry e lo scheduler dei contatti:
        i raggi radar/TVD esistevano per ogni modello ma nessuna classe li esponeva, quindi
        non era scrivibile nessun confronto rotta<->raggio analogo a quello che
        air_defense_volume() rende possibile per i volumi di difesa aerea.

        Params:
            mode:       dimensione del bersaglio, in DETECTION_MODES ('ground'/'air'/'sea').
            sensor:     None (default) = il migliore fra radar e TVD; oppure 'radar'/'TVD'
                        per isolare un solo sensore.
            range_type: 'acquisition_range' (default), 'tracking_range' o 'engagement_range'.

        Composizione radar+TVD: il default e' il MASSIMO dei due, non la somma e non il
        radar da solo. Motivo: la domanda dello scheduler e' "a che distanza questo
        osservatore vede per la prima volta il bersaglio", e la risposta e' il sensore che
        arriva piu' lontano fra quelli funzionanti; i due sensori non si sommano perche'
        guardano lo stesso bersaglio. Restano separabili con `sensor` proprio perche' le
        degradazioni future (disturbo elettronico sul radar, notte/meteo sull'ottico,
        silenzio radar) colpiscono un sensore alla volta e non devono richiedere di
        riscrivere questo metodo.

        Returns:
            float: raggio in metri (> 0), oppure None se il modello non e' noto, non ha
            sensori, o non ha capacita' su quel modo. Come combat_range() e
            air_defense_volume() non solleva mai per dati mancanti: un asset con modello
            sconosciuto deve restare costruibile e interrogabile. Il chiamante decide la
            propria politica di default (es. una portata visiva minima) su un None.

        Raises:
            ValueError: solo per argomenti fuori dominio (mode/sensor/range_type), che sono
            errori di programmazione, non dati mancanti.
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as _AircraftData

        if mode not in DETECTION_MODES:
            raise ValueError(f"mode must be one of {DETECTION_MODES!r}, got {mode!r}")

        if sensor is not None and sensor not in DETECTION_SENSORS:
            raise ValueError(f"sensor must be None or one of {DETECTION_SENSORS!r}, got {sensor!r}")

        if range_type not in DETECTION_RANGE_TYPES:
            raise ValueError(f"range_type must be one of {DETECTION_RANGE_TYPES!r}, got {range_type!r}")

        model = getattr(self, '_model', None)

        if model is None:
            logger.warning("detection_range: _model not set")
            return None

        # Stesso dispatch di speed_profile_from_registry(): sul registry che risponde, non
        # su isinstance(record, ...).
        data_record = (_VehicleData._registry.get(model)
                       or _ShipData._registry.get(model)
                       or _AircraftData._registry.get(model))

        if data_record is None:
            logger.warning(f"detection_range: no registry entry for model {model!r}")
            return None

        sensors = (sensor,) if sensor is not None else DETECTION_SENSORS

        ranges_km = [value for value in (self._sensor_range_km(data_record, s, mode, range_type)
                                         for s in sensors)
                     if value is not None]

        if not ranges_km:
            # Nessun warning: un mezzo senza sensori (radar == False) e' un dato corretto.
            logger.debug(f"detection_range: no {range_type} on mode {mode!r} for model {model!r} "
                         f"(sensors: {sensors})")
            return None

        return max(ranges_km) * 1000.0  # km -> m

    def engagement_channels(self, mode: str = 'air') -> Optional[int]:
        """Numero di bersagli di dimensione `mode` che il radar dell'asset gestisce insieme.

        Legge `multi_target_capacity` dalla stessa struttura sensori di detection_range()
        (record.radar['capabilities'][mode][1]); e' il dato reale piu' vicino, fra quelli
        disponibili nei registri, al numero di CANALI DI FUOCO di un sistema di difesa
        aerea — cioe' a quanti colpi in arrivo puo' impegnare nello stesso istante. Lo
        consuma Military.salvo_interceptors() (saturazione difensiva per salva, R1).
        Attenzione: per alcuni radar di scoperta il registro dichiara la capacita' di
        TRACCIAMENTO, che sovrastima i canali di fuoco; e' annotato la' come stima.

        Returns:
            int > 0, oppure None se il modello non e' noto, non ha radar o il radar non
            dichiara la capacita' su quel modo. Mai un'eccezione per dati mancanti.

        Raises:
            ValueError: `mode` fuori da DETECTION_MODES.
        """
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as _AircraftData

        if mode not in DETECTION_MODES:
            raise ValueError(f"mode must be one of {DETECTION_MODES!r}, got {mode!r}")

        model = getattr(self, '_model', None)

        if model is None:
            return None

        data_record = (_VehicleData._registry.get(model)
                       or _ShipData._registry.get(model)
                       or _AircraftData._registry.get(model))

        if data_record is None:
            return None

        # _sensor_range_km legge una chiave numerica > 0 del dizionario di capacita': il
        # nome parla di raggi ma il parsing (forme legittime dei dati, None su assenza) e'
        # esattamente quello che serve anche qui, e duplicarlo sarebbe peggio.
        value = self._sensor_range_km(data_record, 'radar', mode, 'multi_target_capacity')

        return int(value) if value is not None and int(value) > 0 else None

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



