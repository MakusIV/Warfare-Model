"""
MODULE Mission_Types

Tipi di dominio della Missione (Fase 1 di `Analysis/Document/Piano_Implementazione_Missione.md`),
dalle decisioni D1-D6 e N1-N3 di `Analysis/Document/Proposta_Struttura_Missione_Decisioni.md`.

## Terminologia (D3.a)
  * **Missione**: azioni di attacco, trasporto, posizionamento o supporto svolte da asset di UN
    solo blocco, con un bersaglio (o nessuno), una rotta di riferimento e le direttive (ROE, ...).
  * **Operazione**: insieme facoltativo di missioni (anche di blocchi diversi) per uno stesso
    scopo, con TOT comune facoltativo e una regola d'esito (D2.e).

## Forma
  * La rotta resta GEOMETRICA (`DataType.Route`, N2.a = C): tempi, ruoli e azioni dei punti
    vivono in `MissionWaypoint`, che CONTIENE il `DataType.Waypoint` della rotta (stesso oggetto).
  * Una rotta di riferimento per missione, con un offset di formazione per asset (D3.b) e un
    ruolo per asset da un elenco chiuso per dominio (D3.c).
  * Condizioni d'avvio delle azioni solo pre-calcolabili (N2.d); attese con durata o istante di
    fine (N2.c); criteri di fine dichiarati (D2.a, D2.b); rientro in base nella rotta aerea (D2.c).
  * Esito per missione e per asset (D2.d), con le ETA effettive (N2.b).

## Vincolo simulator-agnostic (`.claude/memory/feedback_core_simulator_agnostic.md`)
Solo id di dominio (stringhe), secondi dall'inizio della sessione, metri, km/h. Le regole (ROE,
allerta, reazione alla minaccia, EMCON, formazione) sono valori di DOMINIO: un adapter li
tradurra' nel proprio vocabolario (DCS e' stato solo uno spunto per gli elenchi).

## Elenchi chiusi
Rivisti e confermati dall'utente il 2026-10-05: `MISSION_ASSET_ROLES` (ruoli = posizioni nella
formazione, non tipi di missione), `FORMATIONS`, `DEFAULT_RULES`, `DEFAULT_START_MODE` (aria: dal
parcheggio). Restano di PRIMA STESURA (stime di progetto, non dati tarati): `EMCON_STATES` e
`THREAT_REACTIONS`. Loadout e profilo d'attacco sono per asset (`MissionAsset`).

## Cosa NON c'e' (di proposito)
  * Nessuna logica di calcolo (ETA derivate, posizioni di formazione, esito di un'Operazione):
    solo validazione strutturale. Dalla F3 la logica che ricava rotta, partenza e velocita' per
    asset e' in `Logic/Mission_Adapter`, e `Command/Session_Types.SessionOrder` porta le missioni
    fino a `Logic/Session_Simulator.run_session` (che produce i `MissionOutcome`).
  * Condizioni sullo stato e re-scheduling (N2.d opzione C, R4 seconda parte).

Stile di `Command/Attack_Types.py` e `Command/Session_Types.py`: dataclass immutabili, validazione
in `__post_init__`, mapping resi immutabili con `MappingProxyType`. Dipendenze: sympy, `Context`,
`DataType` e `Command.Attack_Types`; nessun modulo di `Logic`, quindi nessun ciclo d'import.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Attack_Types import AttackProfile
from Code.Dynamic_War_Manager.Source.Context.Context import (
    MILITARY_FORCES,
    MISSION_TYPES,
    Mission_Category,
    mission_category_of,
)
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Mission_Types').logger

# Nome del piano (`MissionCategory`) e nome di Context (`Mission_Category`): lo stesso enum.
MissionCategory = Mission_Category

# Tolleranza sui confronti fra istanti [s]: stessa grandezza di `Contact_Scheduler.TIME_EPS`,
# ripetuta qui per non importare `Logic` (questo modulo deve restare senza dipendenze dal motore).
_TIME_EPS = 1e-9


# ── ENUM ──────────────────────────────────────────────────────────────────────

class TargetKind(Enum):
    """Forma del bersaglio (N3.d)."""
    ASSET = 'asset'      # un asset nemico identificato (mobile: inseguito)
    GROUP = 'group'      # un gruppo o blocco (nemico, o amico per trasporto/posizionamento)
    POINT = 'point'      # una posizione fissa (raggio facoltativo)
    AREA = 'area'        # una posizione fissa con raggio
    ZONE = 'zone'        # una zona (posizionamento, pattugliamento, ricerca e ingaggio)
    NONE = 'none'        # nessun bersaglio: ingaggia cio' che entra in portata secondo le regole


class TargetProvenance(Enum):
    """Conoscenza su cui si basa il bersaglio (N3.e)."""
    OBSERVED = 'observed'    # id identificato, con l'istante dell'ultima osservazione
    ESTIMATED = 'estimated'  # posizione stimata, con istante e incertezza


class WaypointRole(Enum):
    """Ruolo del punto nella missione (N2.a)."""
    DEPARTURE = 'departure'  # decollo / partenza
    JOIN = 'join'            # ricongiungimento della formazione
    NAV = 'nav'              # punto di navigazione
    IP = 'ip'                # punto iniziale d'attacco
    ATTACK = 'attack'        # punto d'attacco (sgancio, tiro)
    EGRESS = 'egress'        # disimpegno
    SPLIT = 'split'          # separazione della formazione
    LAND = 'land'            # atterraggio (anche su base diversa: divert)
    STATION = 'station'      # stazione (CAP, AWACS, Tanker, pattugliamento)
    ASSEMBLY = 'assembly'    # area di raccolta (terra)
    OBJECTIVE = 'objective'  # obiettivo (terra/mare: punto da raggiungere o tenere)
    HOLD = 'hold'            # punto d'attesa (sincronizzazione, N2.c)


class ActionKind(Enum):
    """Genere di un'azione su un waypoint (N2.a)."""
    TASK = 'task'        # compito (attacco, orbita, scorta, ...)
    RULE = 'rule'        # cambio di regola (ROE, EMCON, ...) da quel punto in poi
    COMMAND = 'command'  # comando istantaneo (es. cambio di frequenza, attivazione)
    WAIT = 'wait'        # attesa: sosta o orbita (N2.c)


class StartConditionKind(Enum):
    """Condizioni d'avvio pre-calcolabili (N2.d): nessuna dipende dallo stato della sessione."""
    ON_ARRIVAL = 'on_arrival'          # all'arrivo al waypoint
    AT_TIME = 'at_time'                # all'istante t [s dall'inizio sessione], non prima dell'arrivo
    AFTER_DURATION = 'after_duration'  # dopo s secondi dall'arrivo al waypoint


class StartMode(Enum):
    """Modo di partenza della missione."""
    RUNWAY = 'runway'              # aria: da pista, motori accesi
    PARKING_COLD = 'parking_cold'  # aria: da parcheggio, motori spenti
    PARKING_HOT = 'parking_hot'    # aria: da parcheggio, motori accesi
    AIR = 'air'                    # aria: gia' in volo
    GROUND = 'ground'              # terra/mare: da fermo sul posto; aria: elicotteri da piazzola/terreno


class Activation(Enum):
    """Quando la missione diventa attiva nella sessione."""
    AT_SESSION_START = 'at_session_start'
    AT_TIME = 'at_time'      # a `start_time`
    ON_EVENT = 'on_event'    # solo DICHIARABILE: nessun esecutore la esegue ancora (re-scheduling)


class OutcomeRule(Enum):
    """Regola d'esito di un'Operazione (D2.e)."""
    MAIN_MISSION = 'main_mission'  # riuscita se la missione principale e' COMPLETED
    ALL = 'all'                    # riuscita se tutte le missioni sono COMPLETED
    ANY = 'any'                    # riuscita se almeno una missione e' COMPLETED


class MissionStatus(Enum):
    """Esito di una missione (D2.d)."""
    COMPLETED = 'completed'
    ABORTED = 'aborted'      # con `AbortReason`
    FAILED = 'failed'        # obiettivo non raggiunto entro la fine
    DESTROYED = 'destroyed'  # tutti gli asset persi


class AbortReason(Enum):
    """Motivo di aborto di una missione (D2.d)."""
    THREAT = 'threat'
    DAMAGE = 'damage'
    FUEL = 'fuel'
    AMMUNITION = 'ammunition'
    SUPPORT_MISSING = 'support_missing'


class AssetState(Enum):
    """Stato di un asset a fine missione (D2.d)."""
    OPERATIONAL = 'operational'
    DAMAGED = 'damaged'
    DESTROYED = 'destroyed'


class AssetEndReason(Enum):
    """Motivo della fine (di missione o di attivita', D2.a) di un singolo asset.

    I criteri di stato (bingo, winchester, danno, minaccia, bersaglio distrutto) nel DES producono
    una "fine di attivita'" senza cambio di rotta (D2.a = B): l'asset resta sulla rotta pianificata.
    """
    ROUTE_COMPLETED = 'route_completed'    # ultimo waypoint raggiunto
    MAX_DURATION = 'max_duration'          # durata / tempo sulla stazione esaurito
    BINGO = 'bingo'
    WINCHESTER = 'winchester'
    DAMAGE = 'damage'                      # soglia di danno superata (mission kill)
    THREAT = 'threat'                      # aborto per minaccia
    TARGET_DESTROYED = 'target_destroyed'
    MISSION_ABORTED = 'mission_aborted'    # segue la missione che abortisce come gruppo (D3.d)
    DESTROYED = 'destroyed'
    SESSION_END = 'session_end'            # missione ancora in corso alla fine della sessione


# ── ELENCHI CHIUSI PER DOMINIO ────────────────────────────────────────────────

# Ruoli degli asset nella missione (D3.c): POSIZIONI nella formazione e nella catena di comando
# della missione, NON tipi di missione (indicazione dell'utente, 2026-10-05: strike, SEAD, scorta...
# sono tipi di missione, `Context.MISSION_TYPES`). Cio' che un asset fa nella missione dipende dal
# tipo di missione e dal SUO loadout (`MissionAsset.loadout`).
# Elenchi di prima stesura: aria = capo formazione, capo della seconda coppia, gregario; terra =
# testa, grosso, retroguardia della colonna; mare = unita' guida, grosso, schermo (le unita' disposte
# a protezione del grosso).
MISSION_ASSET_ROLES: Mapping[str, Tuple[str, ...]] = MappingProxyType({
    'air': ('lead', 'element_lead', 'wingman'),
    'ground': ('lead', 'main', 'rear'),
    'sea': ('lead', 'main', 'screen'),
})

# ROE (valori di dominio): aria a 5 livelli, terra/mare a 3.
AIR_ROE: Tuple[str, ...] = ('weapon_free', 'priority_designated', 'only_designated', 'return_fire',
                            'weapon_hold')
SURFACE_ROE: Tuple[str, ...] = ('weapon_free', 'return_fire', 'weapon_hold')
ROE_BY_DOMAIN: Mapping[str, Tuple[str, ...]] = MappingProxyType({
    'air': AIR_ROE, 'ground': SURFACE_ROE, 'sea': SURFACE_ROE,
})

# Stato di allerta: solo terra e mare (per l'aria non ha significato).
ALARM_STATES: Tuple[str, ...] = ('auto', 'green', 'red')

# Reazione alla minaccia: solo aria. PRIMA STESURA dal vocabolario DCS reso di dominio.
THREAT_REACTIONS: Tuple[str, ...] = ('no_reaction', 'passive_defence', 'evade_fire', 'evasive_vertical',
                                     'allow_abort', 'horizontal_aaa_evade')

# EMCON (emissioni dei sensori attivi), tutti i domini. PRIMA STESURA, stima di progetto.
EMCON_STATES: Tuple[str, ...] = ('free', 'search_if_required', 'attack_only', 'silent')

# Formazioni per dominio. PRIMA STESURA, stima di progetto: nomi di dominio generici, nessun
# legame con un simulatore; la geometria vera la danno gli offset di `MissionAsset`.
FORMATIONS: Mapping[str, Tuple[str, ...]] = MappingProxyType({
    'air': ('line_abreast', 'trail', 'wedge', 'echelon_left', 'echelon_right', 'finger_four', 'spread'),
    'ground': ('column', 'line', 'wedge', 'vee', 'diamond', 'echelon_left', 'echelon_right'),
    'sea': ('column', 'line', 'diamond', 'screen'),
})

# Default delle regole per dominio, confermati dall'utente il 2026-10-05: weapon_free come default
# d'ingaggio di una missione pianificata; reazione 'evade_fire' per l'aria; allerta 'auto' e
# EMCON 'free'; formazione None = lasciata alla dottrina dell'esecutore.
DEFAULT_RULES: Mapping[str, Mapping[str, Optional[str]]] = MappingProxyType({
    'air': MappingProxyType({'roe': 'weapon_free', 'alarm_state': None, 'threat_reaction': 'evade_fire',
                             'emcon': 'free', 'formation': None}),
    'ground': MappingProxyType({'roe': 'weapon_free', 'alarm_state': 'auto', 'threat_reaction': None,
                                'emcon': 'free', 'formation': None}),
    'sea': MappingProxyType({'roe': 'weapon_free', 'alarm_state': 'auto', 'threat_reaction': None,
                             'emcon': 'free', 'formation': None}),
})

# Modi di partenza ammessi e di default per dominio. Default aria = dal parcheggio a motori spenti
# (indicazione dell'utente, 2026-10-05: partenza dal parking point).
START_MODES: Mapping[str, Tuple[StartMode, ...]] = MappingProxyType({
    'air': (StartMode.RUNWAY, StartMode.PARKING_COLD, StartMode.PARKING_HOT, StartMode.AIR, StartMode.GROUND),
    'ground': (StartMode.GROUND,),
    'sea': (StartMode.GROUND,),
})
DEFAULT_START_MODE: Mapping[str, StartMode] = MappingProxyType({
    'air': StartMode.PARKING_COLD, 'ground': StartMode.GROUND, 'sea': StartMode.GROUND,
})

# `route_type` della rotta di riferimento ammessi per dominio (valori di `Context.ROUTE_TYPE`).
ROUTE_TYPES_BY_DOMAIN: Mapping[str, Tuple[str, ...]] = MappingProxyType({
    'air': ('air',), 'ground': ('ground', 'mixed'), 'sea': ('water', 'mixed'),
})

# Forme di bersaglio ammesse per categoria di missione (decisione F1 sulla coerenza).
TARGET_KINDS_BY_CATEGORY: Mapping[Mission_Category, Tuple[TargetKind, ...]] = MappingProxyType({
    Mission_Category.ATTACK: (TargetKind.ASSET, TargetKind.GROUP, TargetKind.POINT, TargetKind.AREA,
                              TargetKind.ZONE),
    Mission_Category.TRANSPORT: (TargetKind.ZONE, TargetKind.POINT, TargetKind.AREA, TargetKind.GROUP),
    Mission_Category.POSITIONING: (TargetKind.ZONE, TargetKind.POINT, TargetKind.AREA, TargetKind.GROUP),
    Mission_Category.SUPPORT: (TargetKind.ZONE, TargetKind.POINT, TargetKind.NONE),
})

ALTITUDE_REFERENCES: Tuple[str, ...] = ('MSL', 'AGL')
WAIT_MODES: Tuple[str, ...] = ('hold', 'orbit')


# ── VALIDATORI ────────────────────────────────────────────────────────────────

def _check_domain_id(label: str, value) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{label} must be a non-empty str (domain id), got {value!r}")

    return value


def _check_optional_id(label: str, value) -> Optional[str]:
    return None if value is None else _check_domain_id(label, value)


def _check_number(label: str, value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TypeError(f"{label} must be a finite number, got {value!r}")

    return float(value)


def _check_time(label: str, value, allow_negative: bool = False) -> Optional[float]:
    """Istante in secondi dall'inizio sessione, None ammesso. Negativo solo se esplicitamente ammesso."""
    if value is None:
        return None

    value = _check_number(label, value)

    if not allow_negative and value < 0:
        raise ValueError(f"{label} must be >= 0 s from session start, got {value}")

    return value


def _check_positive(label: str, value, allow_zero: bool = False) -> Optional[float]:
    if value is None:
        return None

    value = _check_number(label, value)

    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{label} must be {'>= 0' if allow_zero else '> 0'}, got {value}")

    return value


def _check_bool(label: str, value) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{label} must be a bool, got {value!r}")

    return value


def _check_priority(label: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be an int >= 0 (0 = highest), got {value!r}")

    return value


def _coerce_enum(label: str, enum_cls, value):
    """Accetta il membro dell'enum o il suo valore stringa; altrimenti ValueError."""
    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(value)

    except ValueError:
        raise ValueError(f"{label} must be one of {[m.value for m in enum_cls]}, got {value!r}") from None


def _check_choice(label: str, value, choices) -> Optional[str]:
    if value is None:
        return None

    if value not in choices:
        raise ValueError(f"{label} must be one of {tuple(choices)}, got {value!r}")

    return value


def _check_domain(value) -> str:
    if value not in MILITARY_FORCES:
        raise ValueError(f"domain must be one of {MILITARY_FORCES}, got {value!r}")

    return value


def _as_tuple(label: str, value, item_type) -> tuple:
    if isinstance(value, (str, bytes)) or not hasattr(value, '__iter__'):
        raise TypeError(f"{label} must be an iterable of {item_type.__name__}, got {value!r}")

    items = tuple(value)

    for item in items:
        if not isinstance(item, item_type):
            raise TypeError(f"{label} items must be {item_type.__name__}, got {type(item).__name__}")

    return items


def _domain_id(obj) -> Optional[str]:
    """Id di dominio di un blocco o asset: stesso criterio (id, poi name) di
    `Logic/Engagement_Resolver._domain_id` e `Logic/Session_Simulator._domain_id`. Ripetuto qui per non
    importare `Logic`; deve restare allineato, altrimenti `check_mission_assets` darebbe esiti diversi
    da quelli del motore."""
    for attribute in ('id', 'name'):
        value = getattr(obj, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


def route_waypoints(route: Route) -> Tuple[Waypoint, ...]:
    """Waypoint di una `DataType.Route` nell'ordine di percorrenza.

    L'ordine di inserimento di `route.edges` e' l'ordine di percorrenza (stessa assunzione di
    `Route.travelTimeToEdge` e `Contact_Scheduler.route_legs`). `Route.getWaypoints()` NON serve:
    e' un heap ordinato per nome. Archi consecutivi condividono l'oggetto `Waypoint` (lo garantisce
    `Route_Adapter.to_canonical_route`); se non lo condividono, entrambi compaiono nella sequenza.
    """
    sequence: List[Waypoint] = []

    for edge in route.edges.values():
        if not sequence or sequence[-1] is not edge.wpA:
            sequence.append(edge.wpA)

        sequence.append(edge.wpB)

    return tuple(sequence)


# ── BERSAGLIO ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Target:
    """Bersaglio della missione: forma (N3.d) e provenienza dell'informazione (N3.e).

    Regole di forma:
      * NONE: nessun altro campo.
      * ASSET/GROUP: `target_id` obbligatorio (asset, gruppo o blocco), provenienza OBSERVED;
        `position` facoltativa (posizione dell'ultima osservazione, informativa); niente raggio.
      * POINT: `position` obbligatoria, `radius_m` facoltativo (>= 0).
      * AREA/ZONE: `position` (centro) e `radius_m` > 0 obbligatori.
    Regole di provenienza:
      * OBSERVED: `target_id` e `observed_at` obbligatori.
      * ESTIMATED: `position`, `estimated_at` e `uncertainty_m` (>= 0) obbligatori; `target_id`
        facoltativo (stima della posizione di un nemico noto). Il DES usera' la POSIZIONE STIMATA,
        non quella vera (nebbia di guerra C).
      * None (solo POINT/AREA/ZONE): posizione dichiarata dal pianificatore (es. zona di schieramento),
        senza incertezza.
    Gli istanti sono in secondi dall'inizio sessione e possono essere NEGATIVI (osservazione o stima
    precedente alla sessione).
    """
    kind: TargetKind = TargetKind.NONE
    target_id: Optional[str] = None
    position: Optional[Point3D] = None
    radius_m: Optional[float] = None
    provenance: Optional[TargetProvenance] = None
    observed_at: Optional[float] = None
    estimated_at: Optional[float] = None
    uncertainty_m: Optional[float] = None

    def __post_init__(self):
        kind = _coerce_enum('kind', TargetKind, self.kind)
        object.__setattr__(self, 'kind', kind)
        _check_optional_id('target_id', self.target_id)

        if self.position is not None and not isinstance(self.position, Point3D):
            raise TypeError(f"position must be a sympy Point3D, got {type(self.position).__name__}")

        provenance = None if self.provenance is None else _coerce_enum('provenance', TargetProvenance,
                                                                        self.provenance)
        object.__setattr__(self, 'provenance', provenance)
        object.__setattr__(self, 'radius_m', _check_positive('radius_m', self.radius_m, allow_zero=True))
        object.__setattr__(self, 'observed_at', _check_time('observed_at', self.observed_at, True))
        object.__setattr__(self, 'estimated_at', _check_time('estimated_at', self.estimated_at, True))
        object.__setattr__(self, 'uncertainty_m',
                           _check_positive('uncertainty_m', self.uncertainty_m, allow_zero=True))

        if kind is TargetKind.NONE:
            if any(v is not None for v in (self.target_id, self.position, self.radius_m, provenance,
                                           self.observed_at, self.estimated_at, self.uncertainty_m)):
                raise ValueError("a NONE target carries no id, position, radius or provenance")
            return

        if kind in (TargetKind.ASSET, TargetKind.GROUP):
            if self.target_id is None:
                raise ValueError(f"a {kind.name} target needs target_id")

            if self.radius_m is not None:
                raise ValueError(f"a {kind.name} target has no radius_m")

            if provenance is not TargetProvenance.OBSERVED:
                raise ValueError(f"a {kind.name} target must be OBSERVED (an estimated position is a "
                                 f"POINT/AREA target), got {provenance}")

        else:  # POINT, AREA, ZONE
            if self.position is None:
                raise ValueError(f"a {kind.name} target needs position")

            if kind in (TargetKind.AREA, TargetKind.ZONE) and not self.radius_m:
                raise ValueError(f"a {kind.name} target needs radius_m > 0")

        if provenance is TargetProvenance.OBSERVED:
            if self.target_id is None or self.observed_at is None:
                raise ValueError("an OBSERVED target needs target_id and observed_at")

            if self.estimated_at is not None or self.uncertainty_m is not None:
                raise ValueError("an OBSERVED target has no estimated_at/uncertainty_m")

        elif provenance is TargetProvenance.ESTIMATED:
            if self.position is None or self.estimated_at is None or self.uncertainty_m is None:
                raise ValueError("an ESTIMATED target needs position, estimated_at and uncertainty_m")

            if self.observed_at is not None:
                raise ValueError("an ESTIMATED target has no observed_at")

        elif any(v is not None for v in (self.observed_at, self.estimated_at, self.uncertainty_m)):
            raise ValueError("observed_at/estimated_at/uncertainty_m require a provenance")

    @classmethod
    def none(cls) -> 'Target':
        """Nessun bersaglio: ingaggia secondo le regole."""
        return cls()


# ── AZIONI E WAYPOINT ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class StartCondition:
    """Condizione d'avvio di un'azione, solo pre-calcolabile (N2.d).

    Attributes:
        kind: ON_ARRIVAL (default), AT_TIME (`time`, s dall'inizio sessione), AFTER_DURATION
            (`duration_s` dall'arrivo al waypoint).
    """
    kind: StartConditionKind = StartConditionKind.ON_ARRIVAL
    time: Optional[float] = None
    duration_s: Optional[float] = None

    def __post_init__(self):
        kind = _coerce_enum('kind', StartConditionKind, self.kind)
        object.__setattr__(self, 'kind', kind)
        time = _check_time('time', self.time)
        duration = _check_positive('duration_s', self.duration_s)
        object.__setattr__(self, 'time', time)
        object.__setattr__(self, 'duration_s', duration)

        expected = {StartConditionKind.ON_ARRIVAL: (False, False),
                    StartConditionKind.AT_TIME: (True, False),
                    StartConditionKind.AFTER_DURATION: (False, True)}[kind]

        if ((time is not None), (duration is not None)) != expected:
            raise ValueError(f"{kind.name} start condition: time given={time is not None}, "
                             f"duration_s given={duration is not None}, expected {expected}")

    @classmethod
    def on_arrival(cls) -> 'StartCondition':
        return cls()

    @classmethod
    def at_time(cls, t: float) -> 'StartCondition':
        return cls(kind=StartConditionKind.AT_TIME, time=t)

    @classmethod
    def after_duration(cls, s: float) -> 'StartCondition':
        return cls(kind=StartConditionKind.AFTER_DURATION, duration_s=s)


@dataclass(frozen=True)
class MissionAction:
    """Azione su un waypoint (N2.a): compito, regola, comando o attesa.

    Attributes:
        kind: genere dell'azione.
        name: nome di dominio dell'azione (es. 'Orbit', 'Attack_Target', 'Set_ROE').
        params: parametri dell'azione, mapping immutabile con chiavi stringa (valori non validati:
            la forma dipende dall'azione e la fissera' l'esecutore).
        priority: int >= 0, 0 = massima.
        start: condizione d'avvio pre-calcolabile.
        wait_mode/wait_duration_s/wait_until: solo per WAIT (N2.c): modo 'hold' (sosta) od 'orbit',
            e UNO fra durata [s] e istante di fine [s dall'inizio sessione].
    """
    kind: ActionKind
    name: str
    params: Mapping[str, Any] = field(default_factory=dict, hash=False)
    priority: int = 0
    start: StartCondition = field(default_factory=StartCondition)
    wait_mode: Optional[str] = None
    wait_duration_s: Optional[float] = None
    wait_until: Optional[float] = None

    def __post_init__(self):
        kind = _coerce_enum('kind', ActionKind, self.kind)
        object.__setattr__(self, 'kind', kind)
        _check_domain_id('name', self.name)

        if not isinstance(self.params, Mapping):
            raise TypeError(f"params must be a mapping, got {type(self.params).__name__}")

        for key in self.params:
            _check_domain_id('params key', key)

        object.__setattr__(self, 'params', MappingProxyType(dict(self.params)))
        _check_priority('priority', self.priority)

        if not isinstance(self.start, StartCondition):
            raise TypeError(f"start must be a StartCondition, got {type(self.start).__name__}")

        duration = _check_positive('wait_duration_s', self.wait_duration_s)
        until = _check_time('wait_until', self.wait_until)
        object.__setattr__(self, 'wait_duration_s', duration)
        object.__setattr__(self, 'wait_until', until)

        if kind is ActionKind.WAIT:
            _check_choice('wait_mode', self.wait_mode, WAIT_MODES)

            if self.wait_mode is None:
                raise ValueError(f"a WAIT action needs wait_mode in {WAIT_MODES}")

            if (duration is None) == (until is None):
                raise ValueError("a WAIT action needs exactly one of wait_duration_s and wait_until")

        elif self.wait_mode is not None or duration is not None or until is not None:
            raise ValueError(f"wait_mode/wait_duration_s/wait_until are only for WAIT actions, not {kind.name}")


@dataclass(frozen=True)
class MissionWaypoint:
    """Un punto della rotta di missione (N2.a = C): CONTIENE il `DataType.Waypoint` geometrico.

    Attributes:
        waypoint: il `DataType.Waypoint` (stesso oggetto della `Route` di missione, se presente).
        role: ruolo del punto.
        planned_eta: ETA pianificata [s dall'inizio sessione], None = derivata (N2.b).
        eta_locked: True = istante "bloccato" (vincolo di pianificazione); richiede `planned_eta`.
        speed_kmh: velocita' del tratto IN ARRIVO a questo punto [km/h], None = quella dell'arco.
        altitude_reference: 'MSL' (quota assoluta, come `Waypoint.point.z`) o 'AGL'.
        actions: azioni in ordine di dichiarazione (N2.b).
    """
    waypoint: Waypoint
    role: WaypointRole = WaypointRole.NAV
    planned_eta: Optional[float] = None
    eta_locked: bool = False
    speed_kmh: Optional[float] = None
    altitude_reference: str = 'MSL'
    actions: Tuple[MissionAction, ...] = ()

    def __post_init__(self):
        if not isinstance(self.waypoint, Waypoint):
            raise TypeError(f"waypoint must be a DataType.Waypoint, got {type(self.waypoint).__name__}")

        object.__setattr__(self, 'role', _coerce_enum('role', WaypointRole, self.role))
        eta = _check_time('planned_eta', self.planned_eta)
        object.__setattr__(self, 'planned_eta', eta)
        _check_bool('eta_locked', self.eta_locked)

        if self.eta_locked and eta is None:
            raise ValueError("eta_locked requires planned_eta")

        object.__setattr__(self, 'speed_kmh', _check_positive('speed_kmh', self.speed_kmh))
        _check_choice('altitude_reference', self.altitude_reference, ALTITUDE_REFERENCES)

        if self.altitude_reference is None:
            raise ValueError(f"altitude_reference must be one of {ALTITUDE_REFERENCES}")

        actions = _as_tuple('actions', self.actions, MissionAction)
        object.__setattr__(self, 'actions', actions)

        if eta is not None:
            for action in actions:
                if action.wait_until is not None and action.wait_until < eta - _TIME_EPS:
                    raise ValueError(f"WAIT action {action.name!r} ends at {action.wait_until} s, "
                                     f"before the planned ETA {eta} s of its waypoint")

                if action.start.time is not None and action.start.time < eta - _TIME_EPS:
                    raise ValueError(f"action {action.name!r} starts at {action.start.time} s, "
                                     f"before the planned ETA {eta} s of its waypoint")


# ── ASSET, CRITERI, REGOLE ────────────────────────────────────────────────────

_ALL_ASSET_ROLES = frozenset(role for roles in MISSION_ASSET_ROLES.values() for role in roles)


@dataclass(frozen=True)
class MissionAsset:
    """Un asset nella missione (D3.b, D3.c).

    Attributes:
        asset_id: id di dominio dell'asset (stesso criterio del motore: id, poi name).
        role: ruolo nella missione; qui si verifica che esista in qualche dominio, la `Mission`
            verifica che sia ammesso per il SUO dominio (`MISSION_ASSET_ROLES`).
        forward_m/right_m/up_m: offset di formazione rispetto al punto della rotta di riferimento,
            nella terna della direzione di marcia (avanti, destra, alto) [m]. 0,0,0 = sulla rotta.
        loadout: id del loadout dell'asset (solo aria), facoltativo. E' PER ASSET: una missione di un
            blocco puo' impiegare asset di tipo diverso, ciascuno col proprio loadout (es. fighter con
            loadout aria-aria e fighter_bomber con loadout d'attacco sulla stessa rotta e con la
            stessa partenza). La `Mission` verifica che il dominio sia l'aria.
        attack_profile: `AttackProfile` dell'asset (solo aria), facoltativo: dipende dall'arma del
            loadout, quindi e' per asset come il loadout.
    """
    asset_id: str
    role: str
    forward_m: float = 0.0
    right_m: float = 0.0
    up_m: float = 0.0
    loadout: Optional[str] = None
    attack_profile: Optional[AttackProfile] = None

    def __post_init__(self):
        _check_domain_id('asset_id', self.asset_id)

        if self.role not in _ALL_ASSET_ROLES:
            raise ValueError(f"role must be one of {sorted(_ALL_ASSET_ROLES)}, got {self.role!r}")

        for label in ('forward_m', 'right_m', 'up_m'):
            object.__setattr__(self, label, _check_number(label, getattr(self, label)))

        _check_optional_id('loadout', self.loadout)

        if self.attack_profile is not None and not isinstance(self.attack_profile, AttackProfile):
            raise TypeError(f"attack_profile must be an AttackProfile, got {type(self.attack_profile).__name__}")


@dataclass(frozen=True)
class EndCriteria:
    """Criteri di fine missione DICHIARATI (D2.a, D2.b).

    Pre-calcolabili: `last_waypoint`, `max_duration_s`, `bingo` (calcolato a priori sulla rotta).
    Di stato (nel DES: "fine di attivita'" senza cambio di rotta): `winchester`, `abort_on_threat`,
    `damage_threshold`, `target_destroyed`.

    Attributes:
        last_waypoint: la missione finisce all'ultimo waypoint (default True).
        max_duration_s: durata massima o tempo sulla stazione [s], None = nessun limite.
        bingo: rientro al bingo (default True, confermato dall'utente il 2026-10-05, come la dottrina "RTB on bingo").
        winchester: categorie d'arma il cui esaurimento chiude l'attivita' (id di categoria del
            registro d'arma del dominio, es. 'MISSILES_AAM'); vuota = criterio non attivo.
        abort_on_threat: aborto per minaccia.
        damage_threshold: frazione di danno (0, 1] oltre la quale l'asset chiude l'attivita'.
        target_destroyed: fine a bersaglio distrutto.
    Almeno uno fra `last_waypoint` e `max_duration_s` e' obbligatorio: senza una fine geometrica o
    temporale la missione non finirebbe mai se nessun criterio di stato scatta.
    """
    last_waypoint: bool = True
    max_duration_s: Optional[float] = None
    bingo: bool = True
    winchester: Tuple[str, ...] = ()
    abort_on_threat: bool = False
    damage_threshold: Optional[float] = None
    target_destroyed: bool = False

    def __post_init__(self):
        for label in ('last_waypoint', 'bingo', 'abort_on_threat', 'target_destroyed'):
            _check_bool(label, getattr(self, label))

        object.__setattr__(self, 'max_duration_s', _check_positive('max_duration_s', self.max_duration_s))
        winchester = _as_tuple('winchester', self.winchester, str)

        for category in winchester:
            _check_domain_id('winchester item', category)

        if len(set(winchester)) != len(winchester):
            raise ValueError(f"winchester categories must be distinct, got {winchester}")

        object.__setattr__(self, 'winchester', winchester)

        threshold = _check_positive('damage_threshold', self.damage_threshold)

        if threshold is not None and threshold > 1.0:
            raise ValueError(f"damage_threshold must be in (0, 1], got {threshold}")

        object.__setattr__(self, 'damage_threshold', threshold)

        if not self.last_waypoint and self.max_duration_s is None:
            raise ValueError("EndCriteria needs last_waypoint or max_duration_s (the mission must end)")


_RULE_FIELDS = ('roe', 'alarm_state', 'threat_reaction', 'emcon', 'formation')


@dataclass(frozen=True)
class MissionRules:
    """Direttive di missione (D3, sintesi §3.4), valori di DOMINIO.

    Un campo None = default del dominio (`DEFAULT_RULES`), applicato da `for_domain`; la `Mission`
    conserva sempre le regole gia' risolte per il suo dominio. Qui si verifica solo che ogni valore
    esista in qualche dominio; l'ammissibilita' per dominio la verifica `for_domain`:
      * roe: aria `AIR_ROE` (5 livelli), terra/mare `SURFACE_ROE` (3);
      * alarm_state: solo terra/mare (`ALARM_STATES`);
      * threat_reaction: solo aria (`THREAT_REACTIONS`);
      * emcon: tutti (`EMCON_STATES`);
      * formation: `FORMATIONS[dominio]`.
    """
    roe: Optional[str] = None
    alarm_state: Optional[str] = None
    threat_reaction: Optional[str] = None
    emcon: Optional[str] = None
    formation: Optional[str] = None

    def __post_init__(self):
        _check_choice('roe', self.roe, AIR_ROE)
        _check_choice('alarm_state', self.alarm_state, ALARM_STATES)
        _check_choice('threat_reaction', self.threat_reaction, THREAT_REACTIONS)
        _check_choice('emcon', self.emcon, EMCON_STATES)
        _check_choice('formation', self.formation,
                      frozenset(f for forms in FORMATIONS.values() for f in forms))

    def for_domain(self, domain: str) -> 'MissionRules':
        """Regole risolte per `domain`: verifica l'ammissibilita' e riempie i default."""
        domain = _check_domain(domain)

        if self.alarm_state is not None and domain == 'air':
            raise ValueError("alarm_state does not apply to the air domain")

        if self.threat_reaction is not None and domain != 'air':
            raise ValueError(f"threat_reaction applies only to the air domain, not {domain!r}")

        _check_choice(f"roe for {domain}", self.roe, ROE_BY_DOMAIN[domain])
        _check_choice(f"formation for {domain}", self.formation, FORMATIONS[domain])
        defaults = DEFAULT_RULES[domain]

        return MissionRules(**{name: getattr(self, name) if getattr(self, name) is not None else defaults[name]
                               for name in _RULE_FIELDS})


# ── MISSIONE ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Mission:
    """La Missione (D3): asset di un solo blocco, un bersaglio, una rotta di riferimento.

    Attributes:
        mission_id/block_id: id di dominio.
        domain: 'ground' | 'air' | 'sea' (`Context.MILITARY_FORCES`).
        mission_type: tipo specifico del dominio, chiave di `Context.MISSION_TYPES[domain]`.
        assets: tupla non vuota di `MissionAsset`, id unici, ruoli del dominio.
        target: bersaglio (default: nessuno), coerente con la categoria (`TARGET_KINDS_BY_CATEGORY`).
        priority: int >= 0, 0 = massima.
        route: rotta di riferimento geometrica, facoltativa; se presente, `waypoints` devono
            contenerne i waypoint (gli STESSI oggetti) nello stesso ordine (`route_waypoints`).
        waypoints: piano dei punti (`MissionWaypoint`); vuoto ammesso solo a terra/mare (missione
            sul posto). Aria: primo ruolo DEPARTURE salvo `start_mode` AIR, ultimo LAND (D2.c).
        start_time: istante di partenza [s dall'inizio sessione], None = derivato a ritroso.
        start_mode: None = `DEFAULT_START_MODE[domain]`; ammessi `START_MODES[domain]`.
        activation: AT_TIME richiede `start_time`; ON_EVENT richiede `activation_event` ed e' solo
            dichiarabile (nessun esecutore la esegue ancora).
        tot: Time On Target [s dall'inizio sessione], facoltativo.
        rules: None = default del dominio; conservate gia' risolte (`MissionRules.for_domain`).
        end_criteria: criteri di fine dichiarati.
        operation_id: Operazione di appartenenza, facoltativa.
    Loadout e profilo d'attacco sono PER ASSET (`MissionAsset`), non per missione.
    Vincoli temporali: almeno un istante bloccato (`start_time`, un waypoint con `eta_locked` o
    `tot`); ETA pianificate strettamente crescenti e non anteriori a `start_time`; `tot` non
    anteriore a `start_time`.
    """
    mission_id: str
    block_id: str
    domain: str
    mission_type: str
    assets: Tuple[MissionAsset, ...]
    target: Target = field(default_factory=Target)
    priority: int = 0
    route: Optional[Route] = None
    waypoints: Tuple[MissionWaypoint, ...] = ()
    start_time: Optional[float] = None
    start_mode: Optional[StartMode] = None
    activation: Activation = Activation.AT_SESSION_START
    activation_event: Optional[str] = None
    tot: Optional[float] = None
    rules: Optional[MissionRules] = None
    end_criteria: EndCriteria = field(default_factory=EndCriteria)
    operation_id: Optional[str] = None

    def __post_init__(self):
        _check_domain_id('mission_id', self.mission_id)
        _check_domain_id('block_id', self.block_id)
        domain = _check_domain(self.domain)

        if self.mission_type not in MISSION_TYPES[domain]:
            raise ValueError(f"mission_type for {domain!r} must be one of {sorted(MISSION_TYPES[domain])}, "
                             f"got {self.mission_type!r}")

        self._validate_assets(domain)

        if not isinstance(self.target, Target):
            raise TypeError(f"target must be a Target, got {type(self.target).__name__}")

        allowed_kinds = TARGET_KINDS_BY_CATEGORY[self.category]

        if self.target.kind not in allowed_kinds:
            raise ValueError(f"a {self.category.name} mission ({self.mission_type}) needs a target in "
                             f"{[k.name for k in allowed_kinds]}, got {self.target.kind.name}")

        _check_priority('priority', self.priority)
        self._validate_route_and_waypoints(domain)
        self._validate_start(domain)
        self._validate_times()

        rules = self.rules if self.rules is not None else MissionRules()

        if not isinstance(rules, MissionRules):
            raise TypeError(f"rules must be MissionRules, got {type(rules).__name__}")

        object.__setattr__(self, 'rules', rules.for_domain(domain))

        if not isinstance(self.end_criteria, EndCriteria):
            raise TypeError(f"end_criteria must be EndCriteria, got {type(self.end_criteria).__name__}")

        if self.end_criteria.target_destroyed and self.target.kind in (TargetKind.NONE, TargetKind.ZONE):
            raise ValueError(f"end_criteria.target_destroyed needs a destroyable target, "
                             f"not {self.target.kind.name}")

        _check_optional_id('operation_id', self.operation_id)

    # -- validazioni di dettaglio --

    def _validate_assets(self, domain: str) -> None:
        assets = _as_tuple('assets', self.assets, MissionAsset)

        if not assets:
            raise ValueError("a mission needs at least one asset")

        ids = [a.asset_id for a in assets]

        if len(set(ids)) != len(ids):
            raise ValueError(f"mission asset ids must be distinct, got {ids}")

        for asset in assets:
            if asset.role not in MISSION_ASSET_ROLES[domain]:
                raise ValueError(f"asset {asset.asset_id!r}: role for {domain!r} must be one of "
                                 f"{MISSION_ASSET_ROLES[domain]}, got {asset.role!r}")

            if domain != 'air' and (asset.loadout is not None or asset.attack_profile is not None):
                raise ValueError(f"asset {asset.asset_id!r}: loadout and attack_profile apply only to air "
                                 f"missions, not {domain!r}")

        object.__setattr__(self, 'assets', assets)

    def _validate_route_and_waypoints(self, domain: str) -> None:
        waypoints = _as_tuple('waypoints', self.waypoints, MissionWaypoint)
        object.__setattr__(self, 'waypoints', waypoints)

        if self.route is not None:
            if not isinstance(self.route, Route):
                raise TypeError(f"route must be a DataType.Route, got {type(self.route).__name__}")

            if self.route.route_type not in ROUTE_TYPES_BY_DOMAIN[domain]:
                raise ValueError(f"route_type for {domain!r} must be one of {ROUTE_TYPES_BY_DOMAIN[domain]}, "
                                 f"got {self.route.route_type!r}")

            expected = route_waypoints(self.route)

            if len(expected) != len(waypoints) or any(mw.waypoint is not wp
                                                      for mw, wp in zip(waypoints, expected)):
                raise ValueError(f"waypoints must wrap the route's waypoints in order: route has "
                                 f"{[wp.name for wp in expected]}, mission has "
                                 f"{[mw.waypoint.name for mw in waypoints]}")

        if domain == 'air' and not waypoints:
            raise ValueError("an air mission needs waypoints (departure ... landing, D2.c)")

    def _validate_start(self, domain: str) -> None:
        start_mode = DEFAULT_START_MODE[domain] if self.start_mode is None else \
            _coerce_enum('start_mode', StartMode, self.start_mode)

        if start_mode not in START_MODES[domain]:
            raise ValueError(f"start_mode for {domain!r} must be one of {[m.name for m in START_MODES[domain]]}, "
                             f"got {start_mode.name}")

        object.__setattr__(self, 'start_mode', start_mode)

        if domain == 'air':
            if start_mode is not StartMode.AIR and self.waypoints[0].role is not WaypointRole.DEPARTURE:
                raise ValueError(f"an air mission starting {start_mode.name} must begin with a DEPARTURE "
                                 f"waypoint, got {self.waypoints[0].role.name}")

            if self.waypoints[-1].role is not WaypointRole.LAND:
                raise ValueError(f"an air mission must end with a LAND waypoint (D2.c), "
                                 f"got {self.waypoints[-1].role.name}")

        activation = _coerce_enum('activation', Activation, self.activation)
        object.__setattr__(self, 'activation', activation)
        _check_optional_id('activation_event', self.activation_event)

        if activation is Activation.ON_EVENT and self.activation_event is None:
            raise ValueError("ON_EVENT activation needs activation_event")

        if activation is not Activation.ON_EVENT and self.activation_event is not None:
            raise ValueError("activation_event applies only to ON_EVENT activation")

    def _validate_times(self) -> None:
        start = _check_time('start_time', self.start_time)
        tot = _check_time('tot', self.tot)
        object.__setattr__(self, 'start_time', start)
        object.__setattr__(self, 'tot', tot)

        if self.activation is Activation.AT_TIME and start is None:
            raise ValueError("AT_TIME activation needs start_time")

        if start is None and tot is None and not any(mw.eta_locked for mw in self.waypoints):
            raise ValueError("a mission needs at least one locked instant: start_time, tot or a "
                             "waypoint with eta_locked (N2.b)")

        if start is not None and tot is not None and tot < start - _TIME_EPS:
            raise ValueError(f"tot ({tot}) precedes start_time ({start})")

        previous = start
        previous_label = 'start_time'

        for index, mw in enumerate(self.waypoints):
            if mw.planned_eta is None:
                continue

            if previous is not None and mw.planned_eta < previous - _TIME_EPS:
                raise ValueError(f"planned ETAs must increase: waypoint {index} ({mw.planned_eta}) "
                                 f"precedes {previous_label} ({previous})")

            if previous_label != 'start_time' and abs(mw.planned_eta - previous) <= _TIME_EPS:
                raise ValueError(f"planned ETAs must be strictly increasing: waypoint {index} "
                                 f"equals {previous_label} ({previous})")

            previous = mw.planned_eta
            previous_label = f"waypoint {index}"

    # -- proprieta' --

    @property
    def category(self) -> Mission_Category:
        """Categoria comune (Attacco/Trasporto/Posizionamento/Supporto, N3.a) dal tipo di missione.

        `Context.mission_category_of` restituisce il VALORE dell'enum: qui si torna al membro."""
        return Mission_Category(mission_category_of(self.domain, self.mission_type))

    @property
    def asset_ids(self) -> Tuple[str, ...]:
        return tuple(a.asset_id for a in self.assets)


def check_mission_assets(mission: Mission, block) -> None:
    """Verifica che il blocco sia quello della missione e che ogni asset della missione gli appartenga.

    Separata dal costruttore: la `Mission` porta solo id, il blocco e' un oggetto del modello
    (`Block.Block`, `Block.Military`), con gli asset in `block.assets` ({chiave: Asset}). Gli id si
    confrontano con il criterio del motore (`id`, poi `name`) sugli oggetti, non sulle chiavi del dict.

    Raises:
        TypeError: `mission` non e' una `Mission`.
        ValueError: blocco diverso da `mission.block_id` o asset non appartenenti al blocco.
    """
    if not isinstance(mission, Mission):
        raise TypeError(f"mission must be a Mission, got {type(mission).__name__}")

    block_id = _domain_id(block)

    if block_id != mission.block_id:
        raise ValueError(f"mission {mission.mission_id!r} belongs to block {mission.block_id!r}, "
                         f"not to {block_id!r}")

    owned = {_domain_id(asset) for asset in (getattr(block, 'assets', None) or {}).values()}
    missing = [asset_id for asset_id in mission.asset_ids if asset_id not in owned]

    if missing:
        raise ValueError(f"mission {mission.mission_id!r}: assets {missing} do not belong to block {block_id!r}")

    logger.debug(f"check_mission_assets: mission {mission.mission_id!r}, {len(mission.assets)} assets of "
                 f"block {block_id!r} verified")


# ── OPERAZIONE ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Operation:
    """Operazione (D3.a): missioni (anche di blocchi diversi) per uno stesso scopo.

    Attributes:
        operation_id: id di dominio.
        purpose: scopo dichiarato (testo libero di dominio).
        mission_ids: tupla non vuota di id di missione distinti.
        tot: TOT comune [s dall'inizio sessione], facoltativo.
        outcome_rule: regola d'esito (D2.e); MAIN_MISSION richiede `main_mission_id` fra `mission_ids`.
    """
    operation_id: str
    purpose: str
    mission_ids: Tuple[str, ...]
    tot: Optional[float] = None
    outcome_rule: OutcomeRule = OutcomeRule.ALL
    main_mission_id: Optional[str] = None

    def __post_init__(self):
        _check_domain_id('operation_id', self.operation_id)
        _check_domain_id('purpose', self.purpose)
        mission_ids = _as_tuple('mission_ids', self.mission_ids, str)

        for mission_id in mission_ids:
            _check_domain_id('mission_ids item', mission_id)

        if not mission_ids:
            raise ValueError("an operation needs at least one mission")

        if len(set(mission_ids)) != len(mission_ids):
            raise ValueError(f"mission_ids must be distinct, got {mission_ids}")

        object.__setattr__(self, 'mission_ids', mission_ids)
        object.__setattr__(self, 'tot', _check_time('tot', self.tot))
        rule = _coerce_enum('outcome_rule', OutcomeRule, self.outcome_rule)
        object.__setattr__(self, 'outcome_rule', rule)
        _check_optional_id('main_mission_id', self.main_mission_id)

        if rule is OutcomeRule.MAIN_MISSION:
            if self.main_mission_id not in mission_ids:
                raise ValueError(f"MAIN_MISSION rule needs main_mission_id in {mission_ids}, "
                                 f"got {self.main_mission_id!r}")

        elif self.main_mission_id is not None:
            raise ValueError(f"main_mission_id applies only to the MAIN_MISSION rule, not {rule.name}")


# ── ESITI ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AssetMissionOutcome:
    """Esito di un asset nella missione (D2.d).

    Attributes:
        asset_id: id di dominio.
        state: stato a fine missione.
        end_reason: motivo della fine (di missione o di attivita').
        end_time: istante di fine [s dall'inizio sessione], None se non definito.
    `state` DESTROYED e `end_reason` DESTROYED vanno insieme.
    """
    asset_id: str
    state: AssetState
    end_reason: AssetEndReason
    end_time: Optional[float] = None

    def __post_init__(self):
        _check_domain_id('asset_id', self.asset_id)
        state = _coerce_enum('state', AssetState, self.state)
        reason = _coerce_enum('end_reason', AssetEndReason, self.end_reason)
        object.__setattr__(self, 'state', state)
        object.__setattr__(self, 'end_reason', reason)
        object.__setattr__(self, 'end_time', _check_time('end_time', self.end_time))

        if (state is AssetState.DESTROYED) != (reason is AssetEndReason.DESTROYED):
            raise ValueError(f"state DESTROYED and end_reason DESTROYED go together, got "
                             f"{state.name}/{reason.name}")


@dataclass(frozen=True)
class MissionOutcome:
    """Esito di una missione (D2.d, N2.b).

    Attributes:
        mission_id: id di dominio.
        status: esito di missione.
        reason: motivo d'aborto, obbligatorio se ABORTED e vietato altrimenti.
        asset_outcomes: {asset_id: AssetMissionOutcome}, mapping immutabile.
        actual_etas: ETA effettive [s] per waypoint, nell'ordine della missione; None = punto non
            raggiunto. Le ETA presenti sono non decrescenti.
    Coerenza: DESTROYED se e solo se tutti gli esiti per asset (se presenti) sono DESTROYED.
    """
    mission_id: str
    status: MissionStatus
    reason: Optional[AbortReason] = None
    asset_outcomes: Mapping[str, AssetMissionOutcome] = field(default_factory=dict, hash=False)
    actual_etas: Tuple[Optional[float], ...] = ()

    def __post_init__(self):
        _check_domain_id('mission_id', self.mission_id)
        status = _coerce_enum('status', MissionStatus, self.status)
        object.__setattr__(self, 'status', status)
        reason = None if self.reason is None else _coerce_enum('reason', AbortReason, self.reason)
        object.__setattr__(self, 'reason', reason)

        if (status is MissionStatus.ABORTED) != (reason is not None):
            raise ValueError(f"reason is required for ABORTED and forbidden otherwise "
                             f"(status {status.name}, reason {reason})")

        if not isinstance(self.asset_outcomes, Mapping):
            raise TypeError(f"asset_outcomes must be a mapping, got {type(self.asset_outcomes).__name__}")

        normalized: Dict[str, AssetMissionOutcome] = {}

        for asset_id, outcome in self.asset_outcomes.items():
            _check_domain_id('asset_outcomes key', asset_id)

            if not isinstance(outcome, AssetMissionOutcome):
                raise TypeError(f"asset_outcomes[{asset_id!r}] must be AssetMissionOutcome")

            if outcome.asset_id != asset_id:
                raise ValueError(f"asset_outcomes key {asset_id!r} differs from its asset_id {outcome.asset_id!r}")

            normalized[asset_id] = outcome

        object.__setattr__(self, 'asset_outcomes', MappingProxyType(normalized))

        if normalized:
            all_destroyed = all(o.state is AssetState.DESTROYED for o in normalized.values())

            if all_destroyed != (status is MissionStatus.DESTROYED):
                raise ValueError(f"status DESTROYED if and only if every asset is destroyed "
                                 f"(status {status.name}, all destroyed {all_destroyed})")

        if isinstance(self.actual_etas, (str, bytes)) or not hasattr(self.actual_etas, '__iter__'):
            raise TypeError(f"actual_etas must be a tuple of times, got {self.actual_etas!r}")

        etas = tuple(_check_time('actual_etas item', eta) for eta in self.actual_etas)
        reached = [eta for eta in etas if eta is not None]

        if any(b < a - _TIME_EPS for a, b in zip(reached, reached[1:])):
            raise ValueError(f"actual_etas must be non-decreasing, got {etas}")

        object.__setattr__(self, 'actual_etas', etas)
