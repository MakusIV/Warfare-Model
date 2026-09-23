from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import get_aircraft_data, get_aircraft_scores, get_aircraft_combat_score, get_aircraft_physical_characteristics
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


# ── CARBURANTE (motore di sessioni virtuali, Fase 5; v. Mobile.FUEL_FULL) ──────
#
# Profilo del loadout letto per ciascun regime di Mobile.FUEL_REGIMES.
AIRCRAFT_FUEL_REGIME_PROFILE = {"nominal": "cruise", "max": "attack"}

# I `range` dei loadout sono RAGGI D'AZIONE (commento di testa di Aircraft_Loadouts: "range
# values are combat radius in km"), non distanze percorribili: un raggio e' andata + ritorno.
# STIMA DICHIARATA: distanza percorribile col pieno = 2 x raggio. E' prudente, perche' il
# profilo di missione sotteso al raggio include anche il carburante di combattimento e le
# riserve: la distanza pura percorribile e' un po' maggiore, quindi questa stima SOVRASTIMA
# il consumo per metro (l'aereo "torna a secco" un po' prima del reale, mai dopo).
AIRCRAFT_RADIUS_TO_DISTANCE_FACTOR = 2.0


def _is_external_fuel_tank(store_name: str) -> bool:
    """True se la voce di pylon e' un serbatoio sganciabile (`*tank*`, `PTB-*`).

    Riconoscimento per nome, l'unico disponibile: Aircraft_Loadouts non ha un campo di tipo
    per le voci non-arma. I nomi presenti oggi sono `<N>gal_tank`, `<N>L_tank`, `PTB-<N>`;
    i pod di rifornimento in volo (`boom_refueling`, `buddy_refueling_pod`,
    `hose_drogue_pod`) sono esclusi.
    """
    name = store_name.lower()
    return 'tank' in name or name.startswith('ptb')

# ASSET
class Aircraft(Mobile) :    

    def __init__(self, block: Block, name: Optional[str] = None, model: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, asset_type:Optional[str] = None, functionality: Optional[str] = None, cost: Optional[int] = None, value: Optional[int] = None, acp: Optional[Payload] = None, rcp: Optional[Payload] = None, payload: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None, crytical: Optional[bool] = False, repair_time: Optional[int] = 0, role: Optional[str] = None, dcs_unit_data: Optional[dict] = None):

            super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data)

            self._model = model  # key per Aircraft_Data._registry / AIRCRAFT
            # Loadout assegnato a questo velivolo (chiave di AIRCRAFT_LOADOUTS[model]); None
            # finche' chi assembla la missione/sessione non lo imposta. V. assigned_loadout.
            self._assigned_loadout: Optional[str] = None

            # Profilo di velocita' canonico in m/s, popolato dal registry del modello.
            # (Prima non era popolabile affatto: il setter passava per checkParam, che le
            # sottoclassi sovrascrivono con firme senza 'speed' — v. Mobile.speed.setter.)
            self.load_speed_from_registry()
            # Scorta di munizioni dal registro (R3, v. Mobile.UNIT_COUNTED_WEAPON_TYPES).
            self.load_ammunition_from_registry()
            # Carburante: come le munizioni dipende dal loadout assegnato, quindi qui resta
            # None (non modellato) finche' assigned_loadout non viene impostato.
            self.load_fuel_from_registry()

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

            for k, v in asset_data[self.asset_type]:

                if self.category == k:
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



    # ── loadout assegnato e munizioni (motore di sessioni virtuali, Fase 4) ──────
    #
    # DECISIONE (utente, 2026-09-23): la scorta di un aereo si ricava dal loadout ASSEGNATO,
    # non dal modello (Aircraft_Data non ha un campo `weapons`). Prima di questa non esisteva
    # alcuno stato "loadout di questo volo" su un'istanza: Air_Resources_Assigner sceglie
    # loadout per nome/modello in pianificazione ma non muta mai un Aircraft, e nessun altro
    # modulo (Command_Types, Air_Route_Manager) lo associa a un'istanza. Lo stato vive quindi
    # qui, come attributo settabile; chi lo imposta e' chi assembla la missione/sessione.

    @property
    def assigned_loadout(self) -> Optional[str]:
        """Nome del loadout assegnato (chiave di AIRCRAFT_LOADOUTS[model]), o None."""
        return getattr(self, '_assigned_loadout', None)

    @assigned_loadout.setter
    def assigned_loadout(self, loadout: Optional[str]) -> None:
        """Assegna (o toglie, con None) il loadout e RIARMA l'aereo di conseguenza.

        Assegnare un loadout equivale ad armare il velivolo per la missione: la scorta
        viene ricalcolata da quel loadout (load_ammunition_from_registry) e l'eventuale
        consumo precedente viene sovrascritto. E' quindi un'operazione del ciclo di
        campagna/assemblaggio missione, non un canale di rifornimento durante l'ingaggio
        (il risolutore non la chiama mai). Con None la scorta torna None (non modellata):
        senza loadout non c'e' dato su cui basarla.

        Raises:
            TypeError: `loadout` non e' una stringa ne' None.
            ValueError: il modello non ha loadout noti, o `loadout` non e' fra i suoi.
        """
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS

        if loadout is not None:
            if not isinstance(loadout, str):
                raise TypeError(f"assigned_loadout must be a str or None, got {type(loadout).__name__}")

            known = AIRCRAFT_LOADOUTS.get(self._model)

            if not known:
                raise ValueError(f"no loadouts known for aircraft model {self._model!r}")

            if loadout not in known:
                raise ValueError(f"loadout {loadout!r} not defined for model {self._model!r}; "
                                 f"known: {sorted(known)}")

        self._assigned_loadout = loadout

        if not self.load_ammunition_from_registry():
            self._ammunition = None

        # Stessa regola per il carburante (Fase 5): assegnare il loadout equivale a preparare
        # il velivolo per la missione, quindi col pieno di QUEL loadout; con None, non modellato.
        if not self.load_fuel_from_registry():
            self._fuel = None

    def ammunition_from_registry(self) -> Optional[int]:
        """Scorta [colpi] dal loadout assegnato, o None se nessun loadout e' assegnato.

        Somma, dal loadout `AIRCRAFT_LOADOUTS[model][assigned_loadout]['stores']`:
          * per ogni pylon `[weapon_name, quantita', ...]` la quantita', SOLO se
            `weapon_name` e' un'arma di AIR_WEAPONS (get_weapon non None): serbatoi
            (`370gal_tank`, `PTB-1500`, ...) e pod di rifornimento stanno anch'essi nei
            pylon e vanno esclusi; ogni unita' e' un colpo usabile una volta, come la
            quantita' dei registri di Vehicle/Ship;
          * `gun_rounds` (colpi del cannone), se intero positivo.
        `stores['devices']` (pod di puntamento, sensori) non contiene armi: non e' letto.

        Stesso contatore AGGREGATO di Mobile (v. UNIT_COUNTED_WEAPON_TYPES): missili e colpi
        del cannone si sommano in un solo numero, come fanno gia' i 42 colpi del 2A46M e i
        6 missili di un T-72. Senza loadout assegnato delega a Mobile, che per un aereo
        restituisce None (non modellata): comportamento invariato.
        """
        loadout_name = self.assigned_loadout

        if loadout_name is None:
            return super().ammunition_from_registry()

        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import get_weapon

        loadout = AIRCRAFT_LOADOUTS.get(self._model, {}).get(loadout_name)

        if not isinstance(loadout, dict):
            logger.debug(f"ammunition_from_registry: loadout {loadout_name!r} not found for "
                         f"model {self._model!r}, ammunition not modelled")
            return None

        stores = loadout.get('stores') or {}
        total = 0

        for item in (stores.get('pylons') or {}).values():
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue

            weapon_name, quantity = item[0], item[1]

            if not isinstance(weapon_name, str) or get_weapon(weapon_name) is None:
                continue  # serbatoio, pod, voce non-arma

            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
                continue

            total += quantity

        gun_rounds = stores.get('gun_rounds')

        if isinstance(gun_rounds, int) and not isinstance(gun_rounds, bool) and gun_rounds > 0:
            total += gun_rounds

        return total

    # ── carburante dal loadout assegnato (motore di sessioni virtuali, Fase 5) ───

    def _assigned_loadout_data(self) -> Optional[Dict]:
        """Il dizionario del loadout assegnato in AIRCRAFT_LOADOUTS, o None."""
        loadout_name = self.assigned_loadout

        if loadout_name is None:
            return None

        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS

        loadout = AIRCRAFT_LOADOUTS.get(self._model, {}).get(loadout_name)

        return loadout if isinstance(loadout, dict) else None

    def fuel_autonomy(self, regime: str = "nominal") -> Optional[float]:
        """Distanza [m] percorribile col carico pieno del loadout assegnato, o None.

            autonomia = AIRCRAFT_RADIUS_TO_DISTANCE_FACTOR x raggio['fuel_100%'] [km] x 1000

        Il regime 'nominal' legge il profilo `cruise` del loadout, 'max' il profilo `attack`
        (stessi regimi di Mobile.SPEED_REGIME_KEYS). Il raggio del loadout vale per il carico
        completo, serbatoi esterni inclusi se imbarcati: e' coerente con l'unita' del
        contatore (frazione del carico pieno, v. Mobile.FUEL_FULL).

        Senza loadout assegnato: None (non modellato), come le munizioni.

        Raises:
            ValueError: `regime` fuori da Mobile.FUEL_REGIMES.
        """
        from Code.Dynamic_War_Manager.Source.Asset.Mobile import FUEL_REGIMES

        if regime not in FUEL_REGIMES:
            raise ValueError(f"regime must be one of {FUEL_REGIMES!r}, got {regime!r}")

        loadout = self._assigned_loadout_data()

        if loadout is None:
            logger.debug(f"fuel_autonomy: no assigned loadout for aircraft {getattr(self, 'id', None)!r}, "
                         f"fuel not modelled")
            return None

        profile = loadout.get(AIRCRAFT_FUEL_REGIME_PROFILE[regime])
        ranges = profile.get('range') if isinstance(profile, dict) else None
        radius_km = ranges.get('fuel_100%') if isinstance(ranges, dict) else None

        if isinstance(radius_km, bool) or not isinstance(radius_km, (int, float)) or radius_km <= 0:
            logger.debug(f"fuel_autonomy: loadout {self.assigned_loadout!r} of model {self._model!r} "
                         f"declares no usable fuel_100% radius for regime {regime!r}")
            return None

        return AIRCRAFT_RADIUS_TO_DISTANCE_FACTOR * float(radius_km) * 1000.0

    def fuel_capacity_kg(self) -> Optional[float]:
        """Massa [kg] del carico pieno del loadout assegnato: interno + serbatoi esterni.

        Serve a convertire il contatore (frazione del carico pieno) in massa, per la
        logistica futura: `fuel [kg] = fuel x fuel_capacity_kg()`.

          * `stores['fuel_internal_max']`: carburante interno in kg (verificato sul dato
            reale: 7348 per l'F-14A, pari alle 16 200 lb documentate).
          * serbatoi esterni: terzo elemento delle voci pylon `[nome, quantita', massa]` il cui
            nome NON e' un'arma di AIR_WEAPONS ed e' un serbatoio (v. _is_external_fuel_tank;
            es. `["370gal_tank", 1, 1200]`). STIMA
            DICHIARATA di lettura: il campo non e' documentato in Aircraft_Loadouts, ma i
            valori corrispondono alla massa in kg del volume nominale (370 gal ~ 1120 kg,
            600 gal ~ 1820 kg, 800 L ~ 640 kg) arrotondata per eccesso.

        Returns:
            float > 0, oppure None se nessun loadout e' assegnato o `fuel_internal_max` manca.
        """
        loadout = self._assigned_loadout_data()

        if loadout is None:
            return None

        stores = loadout.get('stores') or {}
        internal = stores.get('fuel_internal_max')

        if isinstance(internal, bool) or not isinstance(internal, (int, float)) or internal <= 0:
            logger.debug(f"fuel_capacity_kg: loadout {self.assigned_loadout!r} declares no fuel_internal_max")
            return None

        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import get_weapon

        external = 0.0

        for item in (stores.get('pylons') or {}).values():
            if not isinstance(item, (list, tuple)) or len(item) < 3:
                continue

            name, quantity, mass = item[0], item[1], item[2]

            if not isinstance(name, str) or get_weapon(name) is not None:
                continue  # un'arma, non un serbatoio

            if not _is_external_fuel_tank(name):
                # Pod di rifornimento in volo (boom_refueling, hose_drogue_pod, ...): il terzo
                # campo e' il carburante CEDIBILE ad altri velivoli, non autonomia propria.
                continue

            if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
                continue

            if isinstance(mass, bool) or not isinstance(mass, (int, float)) or mass <= 0:
                continue

            external += quantity * float(mass)

        return float(internal) + external

    def air_combat_power(self) -> float:
        """Combat power aggregata dell'aereo, indipendente dal task aereo (v. set_combat_power).

        A differenza dei veicoli/navi, per gli aerei i task (CAP, Strike, SEAD, ...) sono ruoli di
        missione, non posture tattiche mutuamente esclusive come Attack/Defense/Retrait: un aereo capace
        in CAP lo è anche in Intercept o Escort con lo stesso loadout aria-aria. Quindi qui c'è UN solo
        valore, calcolato dal punteggio di combattimento normalizzato del modello (il migliore loadout
        per ciascun task, sommato — v. Aircraft_Data.combat_aggregate/get_aircraft_combat_score) pesato
        per l'efficacia di classe del ruolo dell'aereo (Context.AIR_COMBAT_EFFICACY) e per l'efficienza.
        """
        if self._model is None or self.asset_type is None:
            return 0.0
        return combat_power_from_score(
            category=self.asset_type,
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
        return self.asset_type == "Fighter"
    @property
    def isFighterBomber(self):
        return self.asset_type == "Fighter_Bomber"
    @property
    def isAttacker(self):
        return self.asset_type == "Attacker"
    @property
    def isBomber(self):
        return self.asset_type == "Bomber"
    @property
    def isHeavyBomber(self):
        return self.asset_type == "Heavy_Bomber"
    @property
    def isAwacs(self):
        return self.asset_type == "Awacs"
    @property
    def isRecon(self):
        return self.asset_type == "Recon"
    @property
    def isTransport(self):
        return self.asset_type == "Transport"
    @property
    def isHelicopter(self):
        return self.asset_type == "Helicopter"

    def get_physical_characteristics(self) -> Optional[Dict]:
        """Returns the physical characteristics of the aircraft as defined in Aircraft_Data.

        Mirrors Ship.get_physical_characteristics(). physical_characteristics is kept out of
        Aircraft_Data.AIRCRAFT (the flat float-scores dict, see the #TEST print loop at the bottom
        of Aircraft_Data.py that formats every value as a float) in its own
        AIRCRAFT_PHYSICAL_CHARACTERISTICS dict instead, for the same reason
        AIRCRAFT_TASK_BEST_SCORES was kept separate.
        """
        if self._model is None:
            logger.warning("Model not defined: Unable to get physical characteristics")
            return None

        return get_aircraft_physical_characteristics(model=self._model)


