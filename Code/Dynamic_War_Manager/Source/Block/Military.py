from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, List, Literal, Tuple, Union
from heapq import heappop, heappush
from numpy import median
from sympy import Point3D, Point2D, re
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, calcProbability
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.State import StateCategory
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import (
    GROUND_ACTION, 
    AIR_TASK,
    SEA_TASK,
    MILITARY_CATEGORY,    
    MILITARY_FORCES,
    ACTION_TASKS,
    Ground_Vehicle_Asset_Type as gat,
    Sea_Asset_Type as sat,
    Air_Asset_Type as aat,
    Asset_Role
)
if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Context.Region import Region
    from Code.Dynamic_War_Manager.Source.Asset.Vehicle import Vehicle
    from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
    from Code.Dynamic_War_Manager.Source.Asset.Ship import Ship
    from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
    
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name=__name__, class_name='Military').logger


#constant:
GROUND_ASSET_TYPE = [ v.value for v in gat ]
AIR_ASSET_TYPE = [ v.value for v in aat ]
SEA_ASSET_TYPE = [ v.value for v in sat ]
STATE_CATEGORY = [ v.value for v in StateCategory ]
ASSET_TYPE = GROUND_ASSET_TYPE + AIR_ASSET_TYPE + SEA_ASSET_TYPE

# Canali di fuoco di un asset di difesa aerea che non dichiara `multi_target_capacity`
# (puntamento ottico, MANPADS, AAA senza radar di tiro): impegna un bersaglio alla volta.
# Stima dichiarata, v. Military.salvo_interception_capacity.
DEFAULT_INTERCEPTION_CHANNELS = 1


class Military(Block):
    """Military class representing specialized combat Block with combat capabilities."""
    
    def __init__(
        self,
        mil_category: str,
        name: Optional[str] = None,
        side: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        functionality: Optional[str] = None,
        value: Optional[int] = None,
        region: Optional["Region"] = None,
        id: Optional[str] = None

    ) -> None:
        """
        Initialize a Military instance.

        Args:
            mil_category: Military category (from Military_CATEGORY)
            name: Base name
            side: Base side (Blue/Red/Neutral)
            description: Base description
            category: Base category
            sub_category: Base sub-category
            functionality: Base functionality
            value: Strategic value
            region: Associated region
            id: id di dominio esplicito, stabile fra le esecuzioni (v. Block.__init__). Serve al
                motore di sessioni virtuali (Session_Simulator/Session_Rng): l'id di forza e'
                anche la chiave dell'RNG e dell'ordine di risoluzione degli ingaggi, quindi deve
                restare lo stesso a ogni esecuzione per chi ricostruisce le forze da zero (test,
                replay) invece di riusare le istanze gia' in memoria di una campagna in corso.
        """
        super().__init__(
            name=f"Military.{name}" if name else setName('Unnamed_Military'),
            description=description,
            side=side,
            category=category,
            sub_category=sub_category,
            functionality=functionality,
            value=value,
            region=region,
            id=id
        )
        
        self._mil_category = mil_category
        self._validate_mil_category(mil_category)
        self._weapons_availability: Optional[Dict[str, Dict[str, int]]] = None

    #military Properties
    @property
    def mil_category(self) -> str:
        """Get military category."""
        return self._mil_category

    @mil_category.setter
    def mil_category(self, value: str) -> None:
        """Set military category after validation."""
        self._validate_mil_category(value)
        self._mil_category = value

    @property
    def weapons_availability(self) -> Optional[Dict[str, Dict[str, int]]]:
        """Get munitions stock available for this block's loadouts (None = non modellato: il
        filtro di scorte in get_available_loadouts viene saltato, non forzato a zero)."""
        return self._weapons_availability

    @weapons_availability.setter
    def weapons_availability(self, value: Optional[Dict[str, Dict[str, int]]]) -> None:
        """Set munitions stock; None = non modellato, {} = scorte esplicitamente nulle."""
        if value is not None and not isinstance(value, dict):
            raise TypeError(f"weapons_availability deve essere un dict o None, ricevuto {type(value).__name__!r}")
        self._weapons_availability = value
    #endmilitary

    #military Validation Methods
    def _validate_mil_category(self, category: str) -> None:
        """Validate military category against allowed values."""
        cat = []                    
        for b in MILITARY_CATEGORY.values():
            for c in b:
                cat.append(c)

        if not isinstance(category, str) or category not in cat: #[MILITARY_CATEGORY["Air_Base"], MILITARY_CATEGORY["Naval_Base"], MILITARY_CATEGORY["Ground_Base"]]::   
            valid_categories = ", ".join(cat)
            raise ValueError(
                f"Invalid mil_category: {category}. Must be one of: {valid_categories}"
            )
    #endmilitary

    def get_asset_list(self,
                       asset_class: Optional[str] = None, # Aircraft, Vehicle, Ship, Structure
                       asset_type: Optional[str] = None, # Tank, Fighter, Armored, ...
                       asset_state: Optional[str] = None) -> Optional[Dict]:

        """
        Restituisce un dizionario contenente liste di assets appartenenti al Military Block,
        filtrati per classe, tipo e stato. I parametri None non applicano filtro.

        Args:
            asset_class: Optional[str]: 'Aircraft', 'Vehicle', 'Ship', 'Structure'. None = nessun filtro.
            asset_type: Optional[str]: tipo asset (es. 'Tank', 'Fighter', ...). None = nessun filtro.
            asset_state: Optional[str]: stato (es. 'Healtful', 'Damaged', 'Critical', 'Destroyed', 'Unknow'). None = nessun filtro.

        Returns:
            Dict organizzato come {asset_class: {asset_type: [asset, ...]}} o None se i parametri non sono validi.
        """

        if asset_class is not None and (not isinstance(asset_class, str) or asset_class not in ['Aircraft', 'Vehicle', 'Ship', 'Structure']):
            logger.warning(f"asset_class:{asset_class} is not valid. Must be one of: 'Aircraft', 'Vehicle', 'Ship', 'Structure'. Returns None")
            return None

        if asset_type is not None and (not isinstance(asset_type, str) or asset_type not in ASSET_TYPE):
            logger.warning(f"asset_type:{asset_type} is not valid. Must be one of: {ASSET_TYPE!r}. Returns None")
            return None

        if asset_state is not None and (not isinstance(asset_state, str) or asset_state not in STATE_CATEGORY):
            logger.warning(f"asset_state:{asset_state} is not valid. Must be one of: {STATE_CATEGORY!r}. Returns None")
            return None

        asset_list = {}

        for asset in self.assets.values():

            if asset_class is not None and asset.__class__.__name__ != asset_class:
                continue

            if asset_type is not None and asset.asset_type != asset_type:
                continue

            if asset_state is not None and asset.state.state_value != asset_state:
                continue

            current_class = asset.__class__.__name__
            current_type = asset.asset_type if asset.asset_type else 'Unknown_asset_type'

            if current_class not in asset_list:
                asset_list[current_class] = {}

            if current_type not in asset_list[current_class]:
                asset_list[current_class][current_type] = []

            asset_list[current_class][current_type].append(asset)

        return asset_list
                    
    def combat_power(self, force: Optional[str] = None, action: Optional[str] = None) -> Union[Dict, float]:
        """
        Aggregate combat power of this block's operative assets, summing each asset's
        Mobile.combat_power(force, action). Mirrors Mobile.combat_power's (force, action)
        contract: both given returns a float, one given returns a Dict, neither given
        returns the full {force: {task: value}} breakdown.

        Args:
            force: military force ('ground', 'air', 'sea'), from Context.MILITARY_FORCES.
            action: task within that force, from Context.ACTION_TASKS[force].

        Returns:
            float if both force and action are given, Dict otherwise.
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

        operative_assets = [
            asset for asset in self.assets.values()
            if hasattr(asset, 'combat_power') and asset.is_operative()
        ]

        if force and action:
            return sum(asset.combat_power(force, action) for asset in operative_assets)

        if force:
            return {
                task: sum(asset.combat_power(force, task) for asset in operative_assets)
                for task in ACTION_TASKS[force]
            }

        if action:
            result = {}
            for f in MILITARY_FORCES:
                if action in ACTION_TASKS[f]:
                    result[f] = {action: sum(asset.combat_power(f, action) for asset in operative_assets)}
            return result

        return {
            f: {task: sum(asset.combat_power(f, task) for asset in operative_assets) for task in ACTION_TASKS[f]}
            for f in MILITARY_FORCES
        }

    def get_military_category(self):
        """ Returns military category (Air_Base, Ground_Base, Naval_Base) of Block

        Returns:
        str: military category of block (Air_Base, Ground_Base, Naval_Base) 
        """
    
        military_category = None

        if self.is_Air_Base():
            military_category = "Air_Base"
        if self.is_Ground_Base():
            military_category = "Ground_Base"
        if self.is_Naval_Base():
            military_category = "Naval_Base"

        return military_category

    #military Loadout Availability
    def get_available_loadouts(self, model: str, task: Optional[str] = None, year: Optional[int] = None) -> List[str]:
        """Loadout disponibili per questo Block, secondo la cascata anno/dottrina/scorte.

        Delega a Air_Resources_Assigner.get_available_loadouts usando self.side (L2) e
        self.weapons_availability (L3, saltato se None). Import locale: Air_Resources_Assigner
        importa Block.Military a livello di modulo, quindi un import a livello di modulo qui
        creerebbe un import circolare irrisolvibile.
        """
        from Code.Dynamic_War_Manager.Source.Logic.Air_Resources_Assigner import get_available_loadouts

        return get_available_loadouts(
            model, task, year=year, side=self.side, weapons_availability=self.weapons_availability,
        )
    #endmilitary

    #military Base Type Checks
    def is_Air_Base(self) -> bool:
        """Check if base is an Air_Base."""
        return self._mil_category in MILITARY_CATEGORY["Air_Base"]

    def is_Ground_Base(self) -> bool:
        """Check if base is a ground base."""
        return self._mil_category in MILITARY_CATEGORY["Ground_Base"]

    def is_Naval_Base(self) -> bool:
        """Check if base is a sea group."""
        return self._mil_category in MILITARY_CATEGORY["Naval_Base"]
    #endmilitary

    #military Range Calculations
    def artillery_in_range(
        self, 
        target_point: Union[Point2D, Point3D]
    ) -> Tuple[bool, Optional[dict]]:
        """
        Check if target is within artillery range.
        
        Args:
            target_point: Target position (Point2D or Point3D)
            
        Returns:
            Tuple of (in_range, range_info) where:
            - in_range: True if target is in range of any artillery
            - range_info: Dictionary with range details if in range
        """
        if not isinstance(target_point, (Point2D, Point3D)):
            raise TypeError("Target must be Point2D or Point3D")
        
        position = self.position

        if position:
            target_distance = target_point.distance(self.position)
            has_artillery, max_range, med_range, ratio, quantity = self._get_artillery_stats()

            if not has_artillery:
                return False, None
        else: 
            return False, None
            
        result = {
            "target_within_max_range": max_range >= target_distance,
            "target_within_med_range": med_range >= target_distance,
            "max_range_ratio": max_range / target_distance if max_range > 0 else 0,
            "med_range_ratio": med_range / target_distance if med_range > 0 else 0,
            "artillery_quantity": quantity,
        }
        
        return True, result

    def _get_artillery_stats(self) -> Tuple[bool, float, float, float, int]:
        """
        Calculate artillery statistics for the military unit.
        
        Returns:
            Tuple containing:
            - has_artillery: Boolean indicating if any artillery exists
            - max_range: Maximum range of all artillery
            - med_range: Median range of all artillery
            - ratio: Median to max range ratio
            - quantity: Number of artillery assets
        """
        range_values = [
            asset.combat_range()
            for asset in self.assets.values()
            if ( validate_class(asset, "Vehicle") and asset.asset_type in [gat.ARTILLERY_FIXED.value, gat.ARTILLERY_SEMOVENT.value, gat.TANK.value] ) or ( validate_class(asset, "Ship") and asset.asset_type in [sat.CORVETTE.value, sat.CRUISER.value, sat.DESTROYER.value, sat.FRIGATE.value] )
        ]
        
        if not range_values:
            return False, 0.0, 0.0, 0.0, 0
            
        max_range = max(range_values)
        med_range = median(range_values)
        ratio = med_range / max_range if max_range > 0 else 0
        quantity = len(range_values)
        
        return True, max_range, med_range, ratio, quantity
    #endmilitary

    #military Time Calculations
    def time_to_direct_line_attack(
        self, 
        target: Union[Point2D, Point3D, Asset, Block]
    ) -> Optional[Dict[str, float]]:
        """
        Calculate estimated time to reach target with direct line path.
        
        Args:
            target: Target position or object with position
            
        Returns:
            Dictionary with time estimates in SECONDS or None if unreachable.
            (Le velocita' del profilo canonico sono in m/s e le posizioni in metri,
            quindi distanza/velocita' e' in secondi: la docstring diceva "hours" ma
            nessun calcolo qui converte in ore.)
        """
        distance = self._get_target_distance(target)
        if distance is None:
            return None
            
        max_speed, med_speed, _ = self._get_attack_speeds()
        if max_speed is None:
            return None
            
        return {
            "time": distance / med_speed if med_speed > 0 else float('inf'),
            "min_time": distance / max_speed if max_speed > 0 else float('inf')
        }

    def time_to_ground_intercept(self, route: Route, speed: Optional[float] = None) -> Optional[float]:

        return route.travelTime(speed=speed)


    def time2attack(self, target: Optional[Union[Point2D, Point3D, Asset, Block]] = None, route: Optional[Route] = None, speed: Optional[float] = None) -> Optional[float]:

        if not target and not route:
            raise ValueError("target or route value must be assigned")

        if self.is_Air_Base() and target:
            return self.time_to_direct_line_attack(target = target)

        elif (self.is_Ground_Base() or self.is_Naval_Base()) and route:
            return self.time_to_ground_intercept(route = route, speed = speed)


    def _get_target_distance(self, target: Union[Point2D, Point3D, Asset, Block]) -> Optional[float]:
        """Calculate distance to target."""
        if self.position: 
            if isinstance(target, (Point2D, Point3D)):
                return target.distance(self.position)
            elif hasattr(target, 'position') and target.position != None and isinstance(target.position, (Point2D, Point3D)):
                return target.position.distance(self.position)
        return None

    def _get_attack_speeds(self) -> Tuple[Optional[float], Optional[float], int]:
        """
        Get speed statistics for attack-capable assets.
        
        Returns:
            Tuple containing:
            - max_speed: Average maximum speed of attack assets
            - med_speed: Average nominal speed of attack assets
            - quantity: Number of attack-capable assets
        """
        speed_values = []
        max_speed_values = []
        
        for asset in self.assets.values():
            if self._is_attack_asset(asset):
                speed_values.append(self._get_nominal_speed(asset))
                max_speed_values.append(self._get_max_speed(asset))
        
        if not speed_values:
            return None, None, 0
            
        return (
            sum(max_speed_values) / len(max_speed_values),
            sum(speed_values) / len(speed_values),
            len(speed_values)
        )

    def _is_attack_asset(self, asset: Union[Vehicle, Aircraft, Ship]) -> bool:
        """Check if asset is attack-capable based on military category."""
        if self.is_Ground_Base() and validate_class(asset, "Vehicle"):
            return asset.isTank or asset.isArmor or asset.isMotorized
        elif self.is_Air_Base() and validate_class(asset, "Aircraft"):
            return not (asset.isTransport or asset.isAwacs or asset.isRecon or asset.isHelicopter)
        elif self.is_helibase() and validate_class(asset, "Aircraft"):
            return asset.isHelicopter
        elif self.is_Naval_Base() and validate_class(asset, "Ship"):
            return (asset.isCarrier or asset.isDestroyer or asset.isFrigate or 
                    asset.isCruiser or asset.isFastAttackShip or asset.isSubmarine)
        return False

    @staticmethod
    def _speed_regime(asset: Union[Vehicle, Aircraft, Ship], regime: str) -> float:
        """Velocita' [m/s] di un regime dal profilo canonico dell'asset (v. Mobile.SPEED_SCHEMA).

        I veicoli sono letti sul ramo 'off_road' perche' un'intercettazione terrestre non
        avviene su strada. Un modello senza dati di velocita' ha il regime a None: qui
        diventa 0.0, cosi' i chiamanti a valle possono confrontarlo con `> 0` senza
        incappare in un TypeError su None.
        """
        speed = getattr(asset, 'speed', None) or {}

        if validate_class(asset, "Vehicle"):
            speed = speed.get("off_road") or {}

        value = speed.get(regime)

        return float(value) if value is not None else 0.0

    def _get_nominal_speed(self, asset: Union[Vehicle, Aircraft, Ship]) -> float:
        """Get nominal speed of asset based on type. [m/s]"""
        return self._speed_regime(asset, "nominal")

    def _get_max_speed(self, asset: Union[Vehicle, Aircraft, Ship]) -> float:
        """Get maximum speed of asset based on type. [m/s]"""
        return self._speed_regime(asset, "max")
    #endmilitary

    #Reconnaissance Methods
    def get_recon_efficiency(self) -> float:
        """
        Calculate median efficiency of reconnaissance assets.
        
        Returns:
            Median efficiency of recon assets or 0.0 if none exist
        """
        recognitors = [
            asset for asset in self.assets.values() 
            if hasattr(asset, 'role') and asset.role == Asset_Role.RECONNAISSANCE.value
        ]
        return median(
            [asset.efficiency for asset in recognitors]
        ) if recognitors else 0.0
    #endmilitary

    def get_c2_efficiency(self) -> float:
        """Calculate median efficiency of command and control assets.

        Returns:
            Median efficiency of c2 assets, or 0.0 if none exist.
        """
        c2 = [
            asset for asset in self.assets.values()
            if hasattr(asset, 'role') and asset.role == Asset_Role.C2.value and hasattr(asset, 'efficiency') and asset.is_operative()
        ]
        return median(
            [asset.efficiency for asset in c2]
        ) if c2 else 0.0

    #Placeholder Methods for Future Implementation
    def air_defense_volume(self) -> List:
        """Return air-defense Cylinders for all operative Vehicle/Ship assets in this block.

        Delegates to Mobile.air_defense_volume() on each operative Vehicle or Ship.
        Assets without AD weapons (SAM/AAA) return None from that call and are excluded.

        Returns:
            List[Cylinder] — one Cylinder per operative AD asset; empty if none present.
        """
        cylinders = []
        for asset in self.assets.values():
            if not (validate_class(asset, "Vehicle") or validate_class(asset, "Ship")):
                continue
            if not asset.is_operative():
                continue
            if not hasattr(asset, 'air_defense_volume'):
                continue
            cyl = asset.air_defense_volume()
            if cyl is not None:
                cylinders.append(cyl)
        return cylinders

    def air_defense_threats(self) -> List:
        """Return the ThreatAA objects of all operative AD assets in this block.

        Pendant di air_defense_volume() un livello piu' in alto: quello restituisce la sola
        geometria (il Cylinder), questo la minaccia completa — geometria + velocita'
        dell'intercettore + latenze di reazione + livello di pericolo — che e' cio' che
        consuma la pianificazione di rotta (v. Logic/Air_Route_Manager.build_threat_aa,
        dove vive la fabbrica e la motivazione delle stime).

        L'import e' locale al metodo: Block non deve dipendere da Logic a tempo di import
        (stessa precauzione usata per i registry in Mobile.combat_range/air_defense_volume).

        Returns:
            List[ThreatAA] — una minaccia per ogni asset AD operativo; vuota se nessuno.
        """
        from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import build_threat_aa

        threats = []
        for asset in self.assets.values():
            if not (validate_class(asset, "Vehicle") or validate_class(asset, "Ship")):
                continue
            if not asset.is_operative():
                continue
            threat = build_threat_aa(asset)
            if threat is not None:
                threats.append(threat)
        return threats

    def air_defense_power(self) -> float:
        """Potenza di difesa aerea del blocco, in [0, 1].

        E' la dimensione che manca alla combat power: SAM, AAA e EWR valgono 0 nelle tabelle
        di efficacia (`Context.GROUND_COMBAT_EFFICACY`) **per definizione**, perche' quella
        misura la capacita' di fuoco e manovra terra-terra, che loro non hanno. La loro
        potenza esiste ma e' di natura diversa, e il progetto la modella gia': e' il
        `danger_level` dei `ThreatAA` costruiti dai volumi di difesa aerea degli asset
        (v. `air_defense_threats` e `Logic/Air_Route_Manager.build_threat_aa`).

        Aggregazione: `1 - prod(1 - danger_level_i)`, cioe' "almeno una delle difese e'
        efficace". Saturante in [0, 1] come i `danger_level` che la compongono, monotona nel
        numero di siti (due batterie difendono meglio di una) e senza il tetto artificiale
        che avrebbe un massimo. Si noti che NON e' una combat power e non e' confrontabile
        con quella: e' un'altra grandezza, sulla sua scala.

        Consumatori previsti (Fase 4): priorita' di targeting SEAD e risolutore d'ingaggio
        aria-superficie. Oggi nessuno la consuma ancora, come detection_range dopo la Fase 2.

        Returns:
            float in [0, 1]; 0.0 se il blocco non ha asset di difesa aerea operativi.
        """
        threats = self.air_defense_threats()

        if not threats:
            return 0.0

        survival = 1.0

        for threat in threats:
            danger = getattr(threat, 'danger_level', None)

            if danger is None:
                continue

            survival *= (1.0 - min(max(float(danger), 0.0), 1.0))

        return 1.0 - survival

    def salvo_interceptors(self) -> List[Tuple["Asset", int]]:
        """Asset del blocco che possono intercettare colpi in arrivo, con i canali di ciascuno.

        E' la base di salvo_interception_capacity() (v. la' per la motivazione e per lo
        statuto della stima). Esposta separatamente perche' il risolutore d'ingaggio
        (Logic/Engagement_Resolver) deve sapere non solo QUANTI colpi il blocco intercetta
        in una salva ma anche CHI li intercetta: ogni intercettazione consuma la scorta di
        intercettori di quell'asset (Mobile.interceptor_stock, distinta dalle munizioni
        offensive — ricalibrazione 2026-09-23), e il risolutore lavora su uno stato ombra
        che evolve durante l'ingaggio, quindi ricalcola la capacita' salva per salva
        partendo da questo elenco.

        Selezione: gli stessi asset di air_defense_threats() — Vehicle o Ship operativi per
        cui esiste una ThreatAA — cosi' che "chi pesa nella difesa aerea" (air_defense_power)
        e "chi intercetta" siano per costruzione lo stesso insieme.

        Returns:
            Lista di (asset, canali) ordinata per id dell'asset (l'ordine di consumo delle
            scorte fa parte del contratto di riproducibilita'); vuota se nessun asset AD.
        """
        from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import build_threat_aa

        interceptors = []

        for asset in self.assets.values():
            if not (validate_class(asset, "Vehicle") or validate_class(asset, "Ship")):
                continue
            if not asset.is_operative():
                continue
            if build_threat_aa(asset) is None:
                continue

            channels = None
            engagement_channels = getattr(asset, 'engagement_channels', None)

            if callable(engagement_channels):
                channels = engagement_channels('air')

            if not isinstance(channels, int) or isinstance(channels, bool) or channels <= 0:
                channels = DEFAULT_INTERCEPTION_CHANNELS

            interceptors.append((asset, channels))

        interceptors.sort(key=lambda item: str(getattr(item[0], 'id', '')))

        return interceptors

    def salvo_interception_capacity(self) -> int:
        """Colpi in arrivo che il blocco puo' intercettare in UNA salva (saturazione, R1).

        DECISIONE (2026-09-23, wiki decisions/risolutore-ingaggio-salva-fase4 R1). E' il
        termine difensivo del modello a salva di Hughes (y, z: "missili intercettati per
        salva"): i primi N colpi di una salva contro questo blocco vengono intercettati e
        non raggiungono mai Logic/Damage_Model.resolve_hit; il surplus oltre N la raggiunge
        integralmente. NON e' una probabilita' per colpo ma un contatore che si esaurisce
        dentro l'evento-salva, ed e' una proprieta' del BERSAGLIO — distinta
        dall'accuracy/destroy_capacity dell'arma che spara.

        E' tenuta volutamente separata da air_defense_power(): quella e' un livello di
        pericolo in [0, 1] per la pianificazione e il targeting, questa e' un conteggio di
        colpi per l'esito. Stessa popolazione di asset, grandezze diverse.

        FORMULA — STIMA DI PARTENZA DICHIARATA, da ricalibrare con il processo ATCAL
        interno (mai con i numeri della fonte Hughes, che non ne fornisce di utilizzabili):

            capacita' = sum_i min(canali_i, scorta_i)

        sugli asset di salvo_interceptors(), dove
          * canali_i = `multi_target_capacity` del radar sul modo 'air' (Mobile.
            engagement_channels) — il dato reale piu' vicino ai canali di fuoco; per un
            radar di scoperta il registro puo' dichiarare la capacita' di tracciamento, che
            li sovrastima. Senza dato radar (sistemi a puntamento ottico, MANPADS) vale
            DEFAULT_INTERCEPTION_CHANNELS = 1;
          * scorta_i = intercettori residui (Mobile.interceptor_stock): non si intercetta
            con intercettori che non si hanno; None (non modellata) non limita. E' un
            contatore DISTINTO dalle munizioni offensive (Mobile.ammunition): fino alla
            ricalibrazione del 2026-09-23 si leggeva `ammunition`, che per i cannoni AA e'
            un conteggio di colpi (Shilka: 2000) e dava migliaia di intercettazioni per
            asset. V. Mobile.ROUNDS_PER_GUN_INTERCEPT per la regola missili/cannoni. Per
            un SAM puro (Mobile.interceptor_shares_ammunition) `interceptor_stock` e' una
            vista di `ammunition`: i missili lanciati in salve offensive riducono anche la
            capacita' di intercettazione (pool fisico unico, v. "SCORTA CONDIVISA").
        Ogni canale intercetta UN colpo per salva: equivale ad assumere Pk
        dell'intercettore = 1 per canale, ipotesi ottimistica per la difesa e primo
        candidato alla ricalibrazione.

        Returns:
            int >= 0; 0 se il blocco non ha asset di difesa aerea operativi.
        """
        capacity = 0

        for asset, channels in self.salvo_interceptors():
            stock = getattr(asset, 'interceptor_stock', None)

            if isinstance(stock, int) and not isinstance(stock, bool):
                capacity += min(channels, max(stock, 0))
            else:
                capacity += channels

        return capacity

    def detection_range(self, mode: str, sensor: Optional[str] = None) -> Optional[Tuple[float, float, float, int]]:
        """Return detection-range statistics [m] of the block against `mode` targets.

        Chiama Mobile.detection_range(mode, sensor) su ogni asset operativo che la espone
        (v. la' per la semantica di mode/sensor e per la scelta di comporre radar e TVD con
        il massimo). Stessa forma di ritorno di combat_range(): un blocco e' un insieme di
        sensori eterogenei e il solo massimo non basta a descriverlo — il massimo dice fin
        dove il blocco vede, la mediana quanto quella capacita' sia diffusa.

        Returns:
            Tuple (max_range, med_range, ratio, quantity) in metri, o None se nessun asset
            operativo dichiara un raggio di rilevamento su quel modo.
        """
        ranges = []
        for asset in self.assets.values():
            if not asset.is_operative():
                continue
            if not hasattr(asset, 'detection_range'):
                continue
            r = asset.detection_range(mode, sensor)
            if r is not None:
                ranges.append(r)

        if not ranges:
            return None

        max_range = float(max(ranges))
        med_range = float(median(ranges))
        ratio     = med_range / max_range if max_range > 0.0 else 0.0

        return max_range, med_range, ratio, len(ranges)

    def combat_range(self) -> Optional[Tuple[float, float, float, int]]:
        """Return combat-range statistics across all operative assets in the block.

        Calls Mobile.combat_range() on every operative asset that exposes the method.
        Each asset is evaluated exactly once (dict iteration guarantees uniqueness).

        Returns:
            Tuple (max_range, med_range, ratio, quantity) or None if no ranges found.
            - max_range : maximum range in metres across operative assets
            - med_range : median range in metres across operative assets
            - ratio     : med_range / max_range  (0.0 if max_range == 0)
            - quantity  : number of operative assets that returned a valid range
        """
        ranges = []
        for asset in self.assets.values():
            if not asset.is_operative():
                continue
            if not hasattr(asset, 'combat_range'):
                continue
            r = asset.combat_range()
            if r is not None:
                ranges.append(r)

        if not ranges:
            return None

        max_range = float(max(ranges))
        med_range = float(median(ranges))
        ratio     = med_range / max_range if max_range > 0.0 else 0.0
        quantity  = len(ranges)

        return max_range, med_range, ratio, quantity

    # Non serve: c'è c2 efficiency, che è più specifico e pertinente per valutare la capacità di comando e controllo del blocco.
    #def intelligence(self) -> None:
    #    """Calculate intelligence level (to be implemented)."""
    #    pass

    def combat_state(self) -> Optional[float]:
        """Calculate combat operational state in [0, 1].

        Formula:
            combat_state = (0.3 * operative_efficiency + 0.7 * c2_efficiency)
                           * (n_operative / n_total)

        Where operative_efficiency is the mean efficiency of operative assets only,
        so that ratio_operative captures quantity attrition while operative_efficiency
        captures quality of surviving assets — cleaner separation than using the
        block-level efficiency (which averages all assets including destroyed ones).

        Returns None when no assets are present.
        """
        total = len(self.assets)
        if total == 0:
            return None

        operative_assets = [a for a in self.assets.values() if a.is_operative()]
        n_operative = len(operative_assets)
        ratio_operative = n_operative / total

        operative_efficiency = (
            sum(a.efficiency for a in operative_assets) / n_operative
            if n_operative > 0 else 0.0
        )
        c2_efficiency = self.get_c2_efficiency()

        return (0.3 * operative_efficiency + 0.7 * c2_efficiency) * ratio_operative
    #endmilitary

    # serve ? è implementato in Block, ma forse qui puoi aggiungere elementi specifici per Military
    def get_recognition_report(self, region_c2_recon_efficiency: Optional[float] = None) -> Dict:
        """Generate reconnaissance report for block
        This method should analyze the block's assets, events, and state to produce a report that can be used for strategic evaluation. 
        The actual implementation will depend on the specific requirements of the reconnaissance-
        The implementation of this method is currently a placeholder and will be developed on derivated class."""

        # ciclando tutti gli asset devi creare un report che sintetizza le informazioni più rilevanti per la valutazione strategica, come:
        # - Numero e tipo di asset presenti (es. 5 carri armati, 3 aerei da combattimento, 2 navi da guerra)
        # - Stato degli asset (es. 3 carri armati in condizioni critiche, 2 aerei da combattimento operativi)
        # - Eventi recenti che hanno coinvolto il blocco (es. attacchi subiti, missioni completate, movimenti di truppe)
        # - Informazioni sulla posizione e la capacità di difesa del blocco (es. presenza di sistemi di difesa aerea, distanza da obiettivi strategici)
        # - Stato generale del blocco (es. morale delle truppe, efficienza logistica, livello di ricognizione)
        # - Stato dei rifornimenti (munizionamento, energy, fuel e hr) e delle linee di comunicazione (es. se sono stati interrotti o se sono ancora operativi)
        # nota in Utilty hai evaluateMorale(success_ratio, efficiency) utilizzata per la proprietà morale in Block. Inoltre, success_ratio è presente come proprietà in State

                        
        if self.state:
            self.state.update()

        # il report realizzato in block considera in dettaglio asset e proprietà Military
        target_report = super().get_recognition_report(region_c2_recon_efficiency)
        
        return target_report        

