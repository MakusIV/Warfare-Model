"""Risolutore d'ingaggio — **chi rileva, chi spara per primo, con che esito**.

FASE 4 del motore di sessioni virtuali (strato 2 dell'architettura DES, v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §6 e
[[project_virtual_session_engine_design]]).

Lo strato 1 (`Logic/Contact_Scheduler.py`) risponde a **quando** due forze si incontrano,
con sola geometria. Questo modulo consuma le sue `ContactWindow` e risponde a **come
finisce**: e' il primo punto del motore in cui entra la casualita', sempre e solo
attraverso l'RNG di sessione passato dal chiamante.

## La catena, per ogni ingaggio (due o piu' forze, v. "Ingaggi a N forze")

1. **Pd — chi rileva davvero.** La finestra di contatto dice che l'osservatore *potrebbe*
   vedere il bersaglio; se lo vede lo decide un'estrazione contro
   `detection_probability(d_cpa, portata)`. Una sola estrazione per coppia e direzione
   decide sia *se* sia *a che distanza* avviene il rilevamento (v. `detection_radius`), e
   quindi *quando*: l'istante e' ricavato analiticamente con
   `Contact_Scheduler.range_intervals` quando il chiamante fornisce i tratti delle rotte.
2. **Latenza di reazione — chi spara per primo.** Dal rilevamento al primo lancio passa
   `ReactionProfile.total` (RIV+VAL+COM+ATT, `Context/Reaction_Profile.py`); le salve
   successive sono separate da `refire_interval`. E' la parte salvata della "Strategia 1":
   l'iniziativa, che i modelli a rapporto di forze non sanno rappresentare.
3. **Dottrina di fuoco / ROE — se e con cosa si spara.** Iniettata: `fire_control(shooter,
   target)` restituisce una `ShotSpec` (accuracy, destroy_capacity, colpi per salva, tempo
   di volo, intercettabilita') oppure None (non ingaggia: ROE, arma inadatta).
4. **Salva e saturazione (Hughes, R1).** I colpi che arrivano su una forza nello stesso
   evento-salva sono prima confrontati con la capacita' di intercettazione del bersaglio
   (`Military.salvo_interceptors`): i primi N intercettabili sono fermati e non
   raggiungono mai il modello di danno, il surplus lo raggiunge integralmente.
5. **Danno per singolo colpo.** Ogni colpo superstite passa da
   `Damage_Model.build_damage_event` (che chiama `resolve_hit`), con un `draw` estratto
   qui dall'RNG iniettato. Nessuna reimplementazione del contratto del danno.
6. **Disingaggio (P1 + R2).** Dopo ogni evento-salva la forza colpita confronta le proprie
   perdite con la dottrina di lato (`Context/Doctrine.get_disengagement_thresholds`):
   erosione cumulata *oppure* shock della singola salva, qualunque scatti per primo. Se
   scatta, **tutta la forza** rompe il contatto: esito `DISENGAGED`, distinto da
   `DESTROYED` (nessun asset impegnato ancora operativo).

## Ingaggi a N forze (2+)

`resolve_engagement(force_a, force_b, ..., extra_forces=(...))` risolve in UNA run, con UNA
coda eventi condivisa, tutte le forze `(force_a, force_b, *extra_forces)`, trattate in modo
uniforme. Chi puo' combattere contro chi lo dicono solo le finestre di contatto passate
(ogni finestra fra asset di due forze diverse genera le due direzioni di rilevamento); il
lato (`side`) serve solo a leggere la dottrina, e piu' forze possono condividerlo.

Perche' serve (caso che ha originato la generalizzazione, 2026-09-23): la forza X e' in
contatto con A e con B in finestre sovrapposte. Risolvendo (X,A) e (X,B) con due chiamate
separate, la prima veniva svolta fino in fondo e applicata, e la seconda leggeva uno stato
di X gia' consumato anche per la parte di tempo in cui X combatteva su entrambi i fronti:
l'ordine delle chiamate decideva chi "arrivava prima" a salute e scorte di X. In una sola
run la salute e le scorte ombra di X evolvono in un'unica timeline, consumata da entrambi i
fronti nell'ordine esatto degli eventi. Con `extra_forces=()` il comportamento e' identico
a quello dell'ingaggio a due.

Nulla nel resto della catena assume due forze: rilevamento (stesso `force_id` -> ignorata),
saturazione e danno (chiavati sulla forza bersaglio), soglie (per lato), esito (per forza,
nell'ordine di ingresso) erano gia' generali. L'unico punto che non lo era e' il contatto
rotto, qui sotto.

## Forze rotte: per-forza, non un flag globale

Una forza che raggiunge DESTROYED o DISENGAGED entra in `broken_forces`. Da quel momento:
- nessun suo tiratore riceve un NUOVO lancio, e i suoi lanci schedulati e non ancora
  eseguiti sono annullati;
- nessun tiratore di altre forze puo' piu' sceglierla come bersaglio (un bersaglio
  disingaggiato e' vivo ma "andato via"); un lancio gia' schedulato contro di essa e'
  annullato e il tiratore decide di nuovo, eventualmente contro un'altra forza;
- le salve GIA' partite, da o verso di essa, arrivano comunque (payload congelato, R4).

Fino all'introduzione delle N forze il contatto rotto era un flag unico della run: appena
una delle due forze rompeva, ogni lancio si fermava. Con due forze le due formulazioni
coincidono — se una forza e' rotta, l'altra non ha piu' bersagli ingaggiabili e smette di
sparare per conseguenza naturale. Con N forze il flag globale sarebbe sbagliato: nello
scenario X/A/B, il disingaggio di X non deve fermare il fronte A-B, se esiste. Il ciclo
eventi finisce sempre e solo quando la coda si svuota.

## Vincoli di progetto rispettati

- **Congelamento del payload (R4, prima parte).** Il bersaglio, la `ShotSpec` e il numero
  di colpi sono fissati quando il lancio viene schedulato e, una volta che la salva e'
  partita, nessun evento successivo li modifica — nemmeno la distruzione del lanciatore:
  una salva in volo arriva comunque. Prima del lancio un evento programmato puo' solo
  essere *annullato* (lanciatore fuori combattimento, bersaglio gia' fuori combattimento
  o uscito dalla finestra, scorte insufficienti, contatto rotto), mai *riscritto*: la
  decisione successiva e' un nuovo evento con un nuovo payload.
- **Re-scheduling delle finestre NON implementato (R4, seconda parte, rimandato).** Una
  forza che si disingaggia e' solo *segnalata* nell'esito; il nuovo instradamento e il
  ricalcolo delle finestre di contatto spettano a un livello superiore (C2/campagna).
- **Il risolutore non muta gli asset.** Lavora su uno stato ombra (salute, scorte) che
  evolve durante l'ingaggio e restituisce gli eventi (`DamageEvent`, `AmmunitionEvent`)
  in un `EngagementResult` immutabile. Applicarli e' un passo separato ed esplicito
  (`apply_engagement_result`): e' la separazione calcolo/applicazione gia' scelta da
  `Damage_Model` (build vs apply) e l'"applicazione in un'unica passata" dello strato 3.
- **RNG sempre iniettato**: un oggetto con `.random()` in [0, 1) — tipicamente
  `random.Random(seed)` creato dal chiamante. Mai `random` di modulo.
- **L'ordine delle estrazioni fa parte del contratto**: prima tutte le estrazioni di
  rilevamento, nell'ordine canonico delle finestre `(t_start, id_a, id_b, t_end)` e per
  ognuna la direzione a->b poi b->a; poi un'estrazione per colpo non intercettato, nell'
  ordine degli eventi. Coda eventi con tie-break deterministico `(t, tipo, id, sequenza)`,
  tipi nell'ordine LANCIO < IMPATTO < RISOLUZIONE: a parita' di istante tutti i lanci
  leggono lo stato *prima* dei danni (risoluzione simultanea, §4.4 del documento).
- **Mai eccezioni per dati mancanti** (forza senza asset utilizzabili, asset senza salute
  leggibile, lato senza soglie dottrinali): None/lista vuota/politica dichiarata + log.
  Le eccezioni restano per gli argomenti fuori dominio.
- **Nessun componente LLM**, in nessuna forma.

## Cosa NON fa (ancora)

- Non seleziona l'arma dai registri: `fire_control` e' iniettata. La selezione da
  `Ground_Weapon_Data`/`Ship_Weapon_Data`/loadout aerei e la modulazione della Pk con la
  posizione nell'inviluppo sono il passo successivo.
- Non applica il meteo da se': la degradazione di Pd resta un fattore iniettato
  (`detection_factor`, 1.0 di default). Il collegamento con `Meteo_Analysis` e' una
  fabbrica di quel fattore (`meteo_detection_factor`/`weather_detection_factor_fn`), che
  il chiamante passa esplicitamente; il fattore non distingue ancora radar da ottico.
- Ripartisce il fuoco fra i tiratori di una forza solo con una regola greedy locale
  (round-robin, v. `_EngagementRun._schedule_next`), non con un'assegnazione ottima.
- Non tocca `Logic/Tactical_Evaluation.calcFightResult` (fallback aggregato, invariato).
"""

import heapq
from collections import abc
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Context import Reaction_Profile as RP
from Code.Dynamic_War_Manager.Source.DataType.State import HEALTH_LEVEL, StateCategory
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS, range_intervals
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Engagement_Resolver').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Pd sul bordo della portata di acquisizione. STIMA DICHIARATA: delle due convenzioni con
# cui si dichiara la portata di un radar (Pd 0.5 o 0.9 a quella distanza) si adotta la piu'
# prudente. Da ricalibrare.
PD_AT_ACQUISITION_RANGE = 0.5

# Esponente della distanza nella legge di Pd: e' la dipendenza R^4 dell'equazione radar
# (SNR proporzionale a 1/R^4, §4.6 del documento). La FORMA viene dalla fisica, la curva
# Pd(SNR) reale (Swerling) e' sigmoide: questa legge ne e' una semplificazione monotona.
PD_RANGE_EXPONENT = 4

# Degradazione ambientale della Pd (v. weather_detection_factor), moltiplicativa.
# STIMA DICHIARATA, nessuna fonte del progetto la fornisce; da ricalibrare via ATCAL interno.
# - Notte: un sensore ottico a occhio nudo perde quasi tutto, un visore/FLIR parte, un radar
#   nulla. Il fattore e' UNICO per tutti i sensori (il risolutore non sa quale sensore ha
#   prodotto la portata della finestra): 0.7 e' un compromesso dichiarato fra "radar, 1.0"
#   e "ottico, molto meno", pesato verso il radar perche' le portate maggiori — quelle che
#   la finestra riporta — sono in genere radar.
# - Meteo avverso: degrada tutti i sensori (l'ottico per visibilita', il radar per
#   attenuazione e clutter da precipitazione), in misura minore della notte sull'ottico
#   ma senza risparmiare il radar: 0.8.
# Notte + meteo avverso = 0.56.
NIGHT_DETECTION_FACTOR = 0.7
ADVERSE_WEATHER_DETECTION_FACTOR = 0.8

# Una forza e' "operativa" per l'asset con salute sopra questa soglia: e' la stessa
# frontiera di State.isOperative (sotto il 50% l'asset e' Critical, fuori combattimento).
OPERATIVE_HEALTH_FLOOR = int(round(DM.HEALTH_MAX * HEALTH_LEVEL[StateCategory.CRITICAL.value]))

# Tolleranza nei confronti fra frazioni di perdita e soglie dottrinali: 3/10 deve valere
# 0.30 anche con l'aritmetica in virgola mobile.
FRACTION_EPS = 1e-9

# Esiti di forza.
HELD = 'held'                  # ancora in contatto a fine ingaggio (o nessuno ha rotto)
DISENGAGED = 'disengaged'      # ha rotto il contatto per soglia dottrinale (P1/R2)
DESTROYED = 'destroyed'        # nessun asset impegnato e' piu' operativo
FORCE_OUTCOMES = (HELD, DISENGAGED, DESTROYED)

# Motivi del cambio di esito.
TRIGGER_EROSION = Doctrine.DISENGAGEMENT_EROSION
TRIGGER_SHOCK = Doctrine.DISENGAGEMENT_SHOCK
TRIGGER_ANNIHILATION = 'annihilation'

# Motivo di consumo delle munizioni.
PURPOSE_SALVO = 'salvo'
PURPOSE_INTERCEPTION = 'interception'

# Tipi di evento, nell'ordine di risoluzione a parita' di istante (v. docstring).
_LAUNCH = 0
_IMPACT = 1
_RESOLVE = 2


# ── TIPI DI SCAMBIO ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ShotSpec:
    """Cosa spara un tiratore contro un bersaglio: prodotta dalla `fire_control` iniettata.

    Attributes:
        accuracy/destroy_capacity: Ph e Pk|h dal registro d'arma, [0, 1] (contratto di
            `Damage_Model`).
        rounds: colpi lanciati per salva (>= 1).
        weapon: modello d'arma di dominio, per la tracciabilita' dei DamageEvent.
        time_of_flight: secondi fra lancio e impatto (>= 0). Con 0 l'impatto e' nello
            stesso istante del lancio, ma risolto DOPO tutti i lanci di quell'istante.
        interceptable: True se i colpi possono essere intercettati dalla difesa del
            bersaglio (missili, bombe guidate); False per i proiettili d'artiglieria o di
            carro. La decide chi conosce l'arma (il chiamante), non il risolutore.
        cycle_time: intervallo fra due salve del tiratore; None = `refire_interval` del
            suo profilo di reazione.
    """
    accuracy: float
    destroy_capacity: float
    rounds: int = 1
    weapon: Optional[str] = None
    time_of_flight: float = 0.0
    interceptable: bool = False
    cycle_time: Optional[float] = None

    def __post_init__(self):
        for name in ('accuracy', 'destroy_capacity'):
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number, got {value!r}")

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value!r}")

        if isinstance(self.rounds, bool) or not isinstance(self.rounds, int) or self.rounds < 1:
            raise ValueError(f"rounds must be an int >= 1, got {self.rounds!r}")

        if isinstance(self.time_of_flight, bool) or not isinstance(self.time_of_flight, (int, float)) \
                or self.time_of_flight < 0:
            raise ValueError(f"time_of_flight must be a non-negative number, got {self.time_of_flight!r}")

        if self.cycle_time is not None and (isinstance(self.cycle_time, bool)
                                            or not isinstance(self.cycle_time, (int, float))
                                            or self.cycle_time <= 0):
            raise ValueError(f"cycle_time must be None or a positive number, got {self.cycle_time!r}")


@dataclass(frozen=True)
class Detection:
    """Esito di un'estrazione di rilevamento (una per finestra e direzione).

    `time` e' l'istante del rilevamento (None se non rilevato); `probability` e' la Pd
    al massimo avvicinamento, `draw` il numero estratto.
    """
    observer_id: str
    target_id: str
    sensor_range: float
    distance_cpa: float
    probability: float
    draw: float
    detected: bool
    time: Optional[float] = None


@dataclass(frozen=True)
class Salvo:
    """Una salva lanciata: il suo payload e' CONGELATO (R4).

    Attributes:
        salvo_id: progressivo di lancio nell'ingaggio (ordine deterministico).
        t_launch/t_impact: secondi assoluti.
        shooter_id/target_id/target_force_id: id di dominio.
        rounds: colpi effettivamente lanciati (gia' limitati dalla scorta al momento della
            schedulazione).
        spec: la ShotSpec usata.
    """
    salvo_id: int
    t_launch: float
    t_impact: float
    shooter_id: str
    target_id: str
    target_force_id: str
    rounds: int
    spec: ShotSpec


@dataclass(frozen=True)
class SalvoResolution:
    """Un evento-salva risolto contro una forza: l'unita' di saturazione (R1) e di shock (R2).

    Attributes:
        time: istante di risoluzione.
        force_id: forza colpita.
        salvo_ids: salve che compongono l'evento.
        rounds: colpi in arrivo; interceptable_rounds: di cui intercettabili.
        capacity: capacita' di intercettazione disponibile all'istante.
        intercepted: colpi fermati (min(interceptable_rounds, capacity)).
        wasted: colpi arrivati su bersagli gia' distrutti (nessuna estrazione).
        losses: asset impegnati passati da operativi a non operativi in questo evento.
        shock/erosion: frazioni dell'organico impegnato, v. Context/Doctrine.
    """
    time: float
    force_id: str
    salvo_ids: Tuple[int, ...]
    rounds: int
    interceptable_rounds: int
    capacity: int
    intercepted: int
    wasted: int
    losses: Tuple[str, ...]
    shock: float
    erosion: float


@dataclass(frozen=True)
class AmmunitionEvent:
    """Consumo esplicito di munizioni (R3): `rounds` colpi di `asset_id` all'istante `time`."""
    time: float
    asset_id: str
    rounds: int
    purpose: str


@dataclass(frozen=True)
class ForceOutcome:
    """Esito di una forza. Pensato per essere promosso a voce del futuro `SessionOutcome`.

    Attributes:
        force_id/side: identita' di dominio della forza.
        outcome: uno di FORCE_OUTCOMES.
        time: istante del cambio di esito (None se HELD).
        triggers: motivi (TRIGGER_*) — possono scattare insieme erosione e shock.
        committed: asset impegnati all'inizio; lost: di questi, non piu' operativi alla fine.
        erosion: lost / committed alla fine; max_shock: la salva peggiore subita.
    """
    force_id: str
    side: Optional[str]
    outcome: str
    time: Optional[float]
    triggers: Tuple[str, ...]
    committed: int
    lost: int
    erosion: float
    max_shock: float


@dataclass(frozen=True)
class EngagementResult:
    """Esito completo di un ingaggio. Immutabile: si sostituisce, non si riscrive.

    Contiene tutto cio' che serve ad applicare l'esito (`damage_events`,
    `ammunition_events`) e a spiegarlo (`detections`, `salvos`, `resolutions`).
    """
    t_start: Optional[float]
    t_end: Optional[float]
    forces: Tuple[ForceOutcome, ...]
    detections: Tuple[Detection, ...] = ()
    salvos: Tuple[Salvo, ...] = ()
    resolutions: Tuple[SalvoResolution, ...] = ()
    damage_events: Tuple[DM.DamageEvent, ...] = ()
    ammunition_events: Tuple[AmmunitionEvent, ...] = ()

    def outcome_of(self, force_id: str) -> Optional[ForceOutcome]:
        """L'esito della forza `force_id`, None se non partecipa."""
        for outcome in self.forces:
            if outcome.force_id == force_id:
                return outcome

        return None

    def ammunition_consumed(self) -> Dict[str, int]:
        """Colpi consumati per asset (salve + intercettazioni)."""
        consumed: Dict[str, int] = {}

        for event in self.ammunition_events:
            consumed[event.asset_id] = consumed.get(event.asset_id, 0) + event.rounds

        return consumed


# ── PERCEZIONE: Pd ────────────────────────────────────────────────────────────

def _check_factor(factor) -> float:
    if isinstance(factor, bool) or not isinstance(factor, (int, float)):
        raise TypeError(f"detection factor must be a number, got {factor!r}")

    if not 0.0 <= factor <= 1.0:
        raise ValueError(f"detection factor must be in [0, 1], got {factor!r}")

    return float(factor)


def detection_probability(distance: float, sensor_range: float, factor: float = 1.0) -> float:
    """Pd di un sensore contro un bersaglio a `distance` [m].

        Pd(d) = factor * (1 - (1 - PD_AT_ACQUISITION_RANGE) * (d / R)^4)    per d <= R
        Pd(d) = 0                                                            per d >  R

    STIMA DICHIARATA di forma: 1 a distanza nulla, PD_AT_ACQUISITION_RANGE sul bordo della
    portata dichiarata dal registro, decrescente con la quarta potenza della distanza come
    il rapporto segnale/rumore dell'equazione radar. `factor` in [0, 1] e' la degradazione
    (meteo, notte, disturbo) applicata dal chiamante; 1.0 = nessuna.

    Raises:
        ValueError: distanza o portata negative, factor fuori [0, 1].
    """
    if distance < 0:
        raise ValueError(f"distance must be non-negative, got {distance!r}")

    if sensor_range <= 0:
        raise ValueError(f"sensor_range must be positive, got {sensor_range!r}")

    factor = _check_factor(factor)

    if distance > sensor_range:
        return 0.0

    ratio = (distance / sensor_range) ** PD_RANGE_EXPONENT

    return factor * (1.0 - (1.0 - PD_AT_ACQUISITION_RANGE) * ratio)


def detection_radius(draw: float, sensor_range: float, factor: float = 1.0) -> Optional[float]:
    """Distanza alla quale un'estrazione `draw` produce il rilevamento, None se mai.

    E' l'inversa di `detection_probability`: il rilevamento avviene quando
    `draw < Pd(d)`, cioe' quando il bersaglio entra nel raggio restituito. Cosi' UNA sola
    estrazione decide sia se il sensore rileva (raggio >= distanza minima raggiunta) sia
    quando (primo istante in cui la distanza scende sotto il raggio), senza campionare
    la finestra nel tempo.

    Returns:
        raggio [m] in (0, sensor_range], oppure None se `draw >= factor` (nemmeno a
        distanza nulla la Pd supera l'estrazione).
    """
    if not 0.0 <= draw < 1.0:
        raise ValueError(f"draw must be in [0, 1), got {draw!r}")

    if sensor_range <= 0:
        raise ValueError(f"sensor_range must be positive, got {sensor_range!r}")

    factor = _check_factor(factor)

    if draw >= factor:
        return None

    if draw < factor * PD_AT_ACQUISITION_RANGE:
        return float(sensor_range)

    ratio = (1.0 - draw / factor) / (1.0 - PD_AT_ACQUISITION_RANGE)

    return float(sensor_range) * ratio ** (1.0 / PD_RANGE_EXPONENT)


# ── DEGRADAZIONE AMBIENTALE DELLA Pd (meteo/notte, da Logic/Meteo_Analysis) ────

def weather_detection_factor(conditions: Optional[Mapping]) -> float:
    """Fattore di degradazione della Pd, in (0, 1], dalle condizioni meteo di una regione.

    `conditions` ha la forma di `Meteo_Analysis.get_meteo_conditions`:
    `{'day': bool, 'night': bool, 'adverse_weather': bool}`. I fattori si moltiplicano:

        factor = (NIGHT_DETECTION_FACTOR se notte) * (ADVERSE_WEATHER_DETECTION_FACTOR se avverso)

    Sede: qui e non in `Meteo_Analysis` perche' il numero e' un parametro della legge di
    Pd (entra in `detection_probability` accanto a PD_AT_ACQUISITION_RANGE), non una
    proprieta' del meteo; `Meteo_Analysis` resta il produttore delle condizioni.

    **Limite noto, dichiarato:** il fattore e' UNICO per ogni sensore. La finestra di
    contatto porta solo la portata migliore fra radar e TVD (`Mobile.detection_range`,
    default = massimo dei due), e il risolutore non sa quale dei due l'ha prodotta: non
    puo' quindi risparmiare al radar la degradazione notturna che fisicamente non subisce.
    Il valore notturno e' percio' un compromesso fra i due sensori; la discriminazione per
    tipo di sensore richiede che la finestra porti il sensore (passo futuro).

    Dati mancanti: `conditions` None -> 1.0 (nessuna degradazione) con un log; una chiave
    assente vale False; se manca 'night' la si ricava da 'day'.

    Raises:
        TypeError: `conditions` non e' un Mapping (errore di programmazione).
    """
    if conditions is None:
        logger.debug("weather_detection_factor: no meteo conditions, no degradation applied")
        return 1.0

    if not isinstance(conditions, abc.Mapping):
        raise TypeError(f"conditions must be a mapping like Meteo_Analysis.get_meteo_conditions, "
                        f"got {type(conditions).__name__}")

    night = conditions.get('night')

    if night is None:
        day = conditions.get('day')
        night = (not day) if day is not None else False

    factor = 1.0

    if night:
        factor *= NIGHT_DETECTION_FACTOR

    if conditions.get('adverse_weather'):
        factor *= ADVERSE_WEATHER_DETECTION_FACTOR

    return factor


def weather_detection_factor_fn(conditions: Optional[Mapping]) -> Callable:
    """La callable `(observer, target) -> float` per `resolve_engagement(detection_factor=...)`.

    La firma di `detection_factor` riceve solo la coppia di asset, non regione/data/ora:
    le condizioni sono quindi catturate qui (closure), quando il chiamante prepara la
    chiamata, e il fattore e' lo stesso per ogni coppia (v. il limite noto in
    `weather_detection_factor`). Il fattore e' calcolato una volta sola, subito: un errore
    sulle condizioni emerge qui e non a meta' ingaggio.
    """
    factor = weather_detection_factor(conditions)

    def detection_factor(observer, target) -> float:
        return factor

    return detection_factor


def meteo_detection_factor(region_name: str, date, time) -> Callable:
    """Come `weather_detection_factor_fn`, leggendo le condizioni da `Meteo_Analysis`.

    E' il collegamento con `Meteo_Analysis.get_meteo_conditions(region_name, date, time)`
    (oggi un placeholder deterministico): nessuna casualita' entra da qui. Import locale,
    come altrove nel progetto fra moduli di Logic.
    """
    from Code.Dynamic_War_Manager.Source.Logic.Meteo_Analysis import get_meteo_conditions

    return weather_detection_factor_fn(get_meteo_conditions(region_name, date, time))


# ── STATO OMBRA ───────────────────────────────────────────────────────────────

class _Shadow:
    """Copia di lavoro di un asset impegnato: salute e scorta evolvono qui, non sull'asset.

    Espone `id` e `health` perche' `Damage_Model.build_damage_event` la tratti come un
    asset (duck typing): cosi' il contratto del danno resta uno solo.
    """
    __slots__ = ('id', 'asset', 'force_id', 'health', 'ammunition')

    def __init__(self, asset_id: str, asset, force_id: str, health: int, ammunition: Optional[int]):
        self.id = asset_id
        self.asset = asset
        self.force_id = force_id
        self.health = health
        self.ammunition = ammunition

    @property
    def operative(self) -> bool:
        return self.health > OPERATIVE_HEALTH_FLOOR

    @property
    def destroyed(self) -> bool:
        return self.health <= DM.DESTROYED_HEALTH


@dataclass
class _Candidate:
    """Un bersaglio rilevato da un tiratore, ingaggiabile in [t_ready, t_end]."""
    t_ready: float
    target_id: str
    t_end: float
    exhausted: bool = False


@dataclass
class _ForceState:
    force_id: str
    side: Optional[str]
    committed: Tuple[str, ...]
    thresholds: Optional[Dict[str, float]]
    interceptors: List[Tuple[_Shadow, int]] = field(default_factory=list)
    outcome: Optional[str] = None
    time: Optional[float] = None
    triggers: Tuple[str, ...] = ()
    max_shock: float = 0.0


@dataclass
class _PendingGroup:
    resolve_time: float
    salvos: List[Salvo] = field(default_factory=list)


def _domain_id(obj) -> Optional[str]:
    """Identificativo di dominio di un asset o di una forza. Mai un id del simulatore."""
    for attribute in ('id', 'name'):
        value = getattr(obj, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


# ── RISOLUTORE ────────────────────────────────────────────────────────────────

class _EngagementRun:
    """Stato e coda eventi di UN ingaggio (2+ forze). Uso interno: v. `resolve_engagement`."""

    def __init__(self, forces, contacts, fire_control, rng, legs, committed, thresholds,
                 reaction_profile_for, detection_factor, salvo_window, provenance):
        self.fire_control = fire_control
        self.rng = rng
        self.legs = legs or {}
        self.reaction_profile_for = reaction_profile_for or RP.profile_for_asset
        self.detection_factor = detection_factor
        self.salvo_window = float(salvo_window)
        self.provenance = provenance
        self.contacts = list(contacts or [])

        self.shadows: Dict[str, _Shadow] = {}
        self.force_states: Dict[str, _ForceState] = {}
        self.force_order: List[str] = []
        self.profiles: Dict[str, RP.ReactionProfile] = {}
        self.candidates: Dict[str, List[_Candidate]] = {}
        # Ripartizione del fuoco (v. _schedule_next): bersaglio del lancio schedulato e non
        # ancora eseguito di ogni tiratore, e salve lanciate non ancora risolte.
        self.assigned: Dict[str, str] = {}
        self.in_flight: Dict[int, Salvo] = {}

        self.queue: List = []
        self.sequence = 0
        self.pending: Dict[str, _PendingGroup] = {}
        # Forze che hanno rotto il contatto (DESTROYED o DISENGAGED): per-forza, non un
        # flag globale della run (v. "Forze rotte" nel docstring del modulo).
        self.broken_forces: set = set()
        self.t_start: Optional[float] = None
        self.t_end: Optional[float] = None

        self.detections: List[Detection] = []
        self.salvos: List[Salvo] = []
        self.resolutions: List[SalvoResolution] = []
        self.damage_events: List[DM.DamageEvent] = []
        self.ammunition_events: List[AmmunitionEvent] = []

        self.usable = self._build_forces(forces, committed, thresholds)

    # ── costruzione ───────────────────────────────────────────────────────────

    def _build_forces(self, forces, committed, thresholds) -> bool:
        for index, force in enumerate(forces):
            force_id = _domain_id(force) or f'force_{index}'

            if force_id in self.force_states:
                raise ValueError(f"the forces must be distinct, {force_id!r} appears more than once")

            assets = getattr(force, 'assets', None) or {}
            selected = None

            if committed is not None and force_id in committed:
                selected = {str(asset_id) for asset_id in committed[force_id]}

            committed_ids = []

            for asset in sorted(assets.values(), key=lambda a: str(_domain_id(a))):
                asset_id = _domain_id(asset)

                if asset_id is None:
                    logger.debug(f"resolve_engagement: asset without domain id in force {force_id!r}, skipped")
                    continue

                if selected is not None and asset_id not in selected:
                    continue

                if asset_id in self.shadows:
                    raise ValueError(f"asset {asset_id!r} appears in more than one force")

                health = getattr(asset, 'health', None)

                if isinstance(health, bool) or not isinstance(health, int):
                    logger.warning(f"resolve_engagement: asset {asset_id!r} has no readable health, not committed")
                    continue

                is_operative = getattr(asset, 'is_operative', None)

                if callable(is_operative) and not is_operative():
                    continue

                if health <= OPERATIVE_HEALTH_FLOOR:
                    continue

                ammunition = getattr(asset, 'ammunition', None)

                if isinstance(ammunition, bool) or not isinstance(ammunition, int):
                    ammunition = None

                self.shadows[asset_id] = _Shadow(asset_id, asset, force_id, health, ammunition)
                committed_ids.append(asset_id)

            side = getattr(force, 'side', None)
            side_thresholds = Doctrine.get_disengagement_thresholds(side, thresholds)

            if side_thresholds is None:
                logger.warning(f"resolve_engagement: no disengagement doctrine for side {side!r} "
                               f"(force {force_id!r}): it will fight until annihilation")

            state = _ForceState(force_id=force_id, side=side, committed=tuple(committed_ids),
                                thresholds=side_thresholds)
            state.interceptors = self._interceptors_of(force, force_id)
            self.force_states[force_id] = state
            self.force_order.append(force_id)

        empty = [force_id for force_id, state in self.force_states.items() if not state.committed]

        if not empty:
            return True

        if len(self.force_states) - len(empty) < 2:
            logger.warning(f"resolve_engagement: forces {empty} have no committed operative asset, "
                           f"engagement not resolvable")
            return False

        # Solo con 3+ forze: una forza vuota non blocca le altre, che hanno ancora almeno
        # un avversario possibile. Resta nell'esito (committed=0, HELD): nessuno la vede e
        # nessuno la colpisce, perche' non ha asset nello stato ombra.
        logger.warning(f"resolve_engagement: forces {empty} have no committed operative asset, "
                       f"they take no part in the engagement")
        return True

    def _interceptors_of(self, force, force_id: str) -> List[Tuple[_Shadow, int]]:
        provider = getattr(force, 'salvo_interceptors', None)

        if not callable(provider):
            return []

        interceptors = []

        for asset, channels in provider() or []:
            shadow = self.shadows.get(_domain_id(asset))

            if shadow is None or shadow.force_id != force_id:
                continue

            interceptors.append((shadow, int(channels)))

        interceptors.sort(key=lambda item: item[0].id)

        return interceptors

    def _profile(self, shooter_id: str) -> RP.ReactionProfile:
        if shooter_id not in self.profiles:
            self.profiles[shooter_id] = self.reaction_profile_for(self.shadows[shooter_id].asset)

        return self.profiles[shooter_id]

    # ── fase 1: rilevamento ───────────────────────────────────────────────────

    def _detect(self) -> None:
        windows = sorted(self.contacts, key=lambda w: (w.t_start, str(w.asset_a_id),
                                                        str(w.asset_b_id), w.t_end))

        for window in windows:
            shadow_a = self.shadows.get(window.asset_a_id)
            shadow_b = self.shadows.get(window.asset_b_id)

            if shadow_a is None or shadow_b is None:
                logger.debug(f"_detect: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                             f"involves an asset not committed to this engagement, skipped")
                continue

            if shadow_a.force_id == shadow_b.force_id:
                continue

            self.t_start = window.t_start if self.t_start is None else min(self.t_start, window.t_start)

            self._detect_direction(window, shadow_a, shadow_b, window.range_a, window.range_b)
            self._detect_direction(window, shadow_b, shadow_a, window.range_b, window.range_a)

    def _detect_direction(self, window, observer: _Shadow, target: _Shadow,
                          own_range: Optional[float], other_range: Optional[float]) -> None:
        if own_range is None or own_range <= 0:
            return

        factor = 1.0

        if self.detection_factor is not None:
            factor = _check_factor(self.detection_factor(observer.asset, target.asset))

        draw = self._draw()
        distance = max(float(window.distance_cpa), 0.0)
        probability = detection_probability(distance, own_range, factor) if distance <= own_range else 0.0
        detected = draw < probability
        time = None

        if detected:
            radius = detection_radius(draw, own_range, factor)
            time = self._detection_time(window, observer.id, target.id, own_range, other_range, radius)

            t_ready = time + self._profile(observer.id).total

            if t_ready <= window.t_end + TIME_EPS:
                self.candidates.setdefault(observer.id, []).append(
                    _Candidate(t_ready=t_ready, target_id=target.id, t_end=window.t_end))

        self.detections.append(Detection(observer_id=observer.id, target_id=target.id,
                                         sensor_range=float(own_range), distance_cpa=distance,
                                         probability=probability, draw=draw, detected=detected,
                                         time=time))

    def _detection_time(self, window, observer_id: str, target_id: str, own_range: float,
                        other_range: Optional[float], radius: Optional[float]) -> float:
        """Istante del rilevamento dentro la finestra.

        Con i tratti di entrambe le rotte: primo istante in cui la distanza scende sotto il
        raggio di rilevamento estratto (esatto, `range_intervals`). Senza: l'istante
        geometrico in cui il bersaglio entra nella portata dell'osservatore — `t_start` se
        la sua e' la portata maggiore, `t_mutual_start` altrimenti — cosi' l'iniziativa di
        chi vede piu' lontano resta preservata; ultimo ripiego `t_cpa`.
        """
        legs_observer = self.legs.get(observer_id)
        legs_target = self.legs.get(target_id)

        if legs_observer and legs_target and radius is not None:
            for start, end in range_intervals(legs_observer, legs_target, radius):
                if end >= window.t_start - TIME_EPS and start <= window.t_end + TIME_EPS:
                    return max(start, window.t_start)

            return window.t_cpa

        if other_range is None or own_range >= other_range:
            return window.t_start

        if window.t_mutual_start is not None:
            return window.t_mutual_start

        return window.t_cpa

    # ── coda eventi ───────────────────────────────────────────────────────────

    def _push(self, time: float, kind: int, key: str, payload) -> None:
        self.sequence += 1
        heapq.heappush(self.queue, (time, kind, key, self.sequence, payload))

    def _draw(self) -> float:
        value = self.rng.random()

        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value < 1.0:
            raise ValueError(f"rng.random() must return a float in [0, 1), got {value!r}")

        return float(value)

    def _touch(self, time: float) -> None:
        self.t_end = time if self.t_end is None else max(self.t_end, time)

    # ── fase 2: scelta del bersaglio e lancio ─────────────────────────────────

    def _engaged_shooters(self, target_id: str, force_id: str, exclude: str) -> int:
        """Quanti ALTRI tiratori della forza `force_id` sono impegnati ora su `target_id`.

        Un tiratore e' "impegnato" su un bersaglio se ha un lancio gia' schedulato contro
        di esso e non ancora eseguito (`self.assigned`) oppure una salva gia' lanciata
        contro di esso e non ancora risolta (`self.in_flight`). Si contano tiratori
        distinti, non colpi ne' salve. Il tiratore che sta decidendo e' escluso: la
        ripartizione riguarda come si dividono i tiratori, non se un tiratore debba
        abbandonare il proprio bersaglio (con un solo tiratore il comportamento resta
        identico a quello senza ripartizione). Calcolato dinamicamente dallo stato della
        coda: nessun contatore da tenere allineato.
        """
        shooters = {shooter_id for shooter_id, assigned in self.assigned.items()
                    if assigned == target_id}
        shooters.update(salvo.shooter_id for salvo in self.in_flight.values()
                        if salvo.target_id == target_id)
        shooters.discard(exclude)

        return sum(1 for shooter_id in shooters if self.shadows[shooter_id].force_id == force_id)

    def _schedule_next(self, shooter_id: str, t_earliest: float) -> None:
        """Decide il prossimo lancio del tiratore e lo mette in coda con payload congelato.

        Un tiratore ingaggia un bersaglio alla volta, fra quelli rilevati, ancora operativi
        e ancora in finestra. `fire_control` e' interrogata QUI, allo scheduling: la
        ShotSpec e il numero di colpi (limitato dalla scorta attuale) viaggiano con
        l'evento e non vengono piu' ricalcolati.

        ## Ripartizione del fuoco: round-robin semplice (decisione utente 2026-09-23)

        Senza ripartizione ogni tiratore sceglieva da solo il bersaglio ingaggiabile per
        primo, e i tiratori di una stessa forza convergevano tutti sullo stesso bersaglio
        (id minore) lasciando gli altri indisturbati. La regola, nell'ordine:

        1. **Istante di tiro:** si considerano solo i bersagli ingaggiabili al PRIMO istante
           utile del tiratore (`t_fire` minimo, entro TIME_EPS). La ripartizione non fa mai
           aspettare un tiratore pronto per andare su un bersaglio meno coperto che sara'
           ingaggiabile solo piu' tardi: cosi' la latenza di reazione — chi spara per primo
           e QUANDO, la parte salvata della Strategia 1 — resta esattamente quella di prima;
           la ripartizione cambia solo CONTRO CHI si spara. (Scelta conservativa su un punto
           che il briefing non chiudeva: "meno coperto prima, poi il piu' vicino nel tempo"
           letto alla lettera potrebbe tenere fermo un tiratore anche a lungo.)
        2. **Copertura:** fra questi, quello con meno ALTRI tiratori della stessa forza gia'
           impegnati (v. `_engaged_shooters`: lancio schedulato o salva in volo).
        3. **Criterio precedente:** a parita', `t_ready` minore (il primo rilevato), poi l'id
           del bersaglio, poi l'ordine di rilevamento.

        Deterministica: dipende solo dallo stato della coda, e i tiratori decidono in un
        ordine fissato (id ordinati all'avvio, poi l'ordine canonico della coda eventi). La
        prima decisione di ogni tiratore vede i lanci gia' schedulati dai tiratori con id
        minore.

        E' "semplice" perche' e' una regola greedy locale, presa dal singolo tiratore
        quando schedula il PROPRIO prossimo lancio. Cosa NON fa: non ottimizza globalmente
        l'assegnazione arma-bersaglio (nessun WTA, nessun peso per valore del bersaglio o
        per Pk della coppia); non redistribuisce assegnazioni gia' fatte — un lancio gia'
        in coda non viene mai spostato su un altro bersaglio (R4: al piu' annullato), e una
        salva in volo arriva dove era diretta; non tiene memoria del passato remoto: una
        salva gia' risolta non conta piu' come copertura.
        """
        shooter = self.shadows[shooter_id]

        if shooter.force_id in self.broken_forces:
            return

        if not shooter.operative or (shooter.ammunition is not None and shooter.ammunition <= 0):
            return

        candidates = self.candidates.get(shooter_id, [])

        while True:
            viable = []

            for index, candidate in enumerate(candidates):
                if candidate.exhausted:
                    continue

                target = self.shadows[candidate.target_id]

                if not target.operative or target.force_id in self.broken_forces:
                    # Fuori combattimento, oppure la sua forza ha rotto il contatto: un
                    # bersaglio DISINGAGGIATO e' vivo ma non piu' raggiungibile.
                    candidate.exhausted = True
                    continue

                t_fire = max(candidate.t_ready, t_earliest)

                if t_fire > candidate.t_end + TIME_EPS:
                    candidate.exhausted = True
                    continue

                viable.append((t_fire, index, candidate))

            if not viable:
                return

            # Round-robin (v. docstring): primo istante utile, poi copertura, poi il resto.
            t_first = min(t_fire for t_fire, _, _ in viable)
            best = None

            for t_fire, index, candidate in viable:
                if t_fire > t_first + TIME_EPS:
                    continue

                engaged = self._engaged_shooters(candidate.target_id, shooter.force_id, shooter_id)
                key = (engaged, t_fire, candidate.t_ready, candidate.target_id, index)

                if best is None or key < best:
                    best = key

            _, t_fire, _, target_id, index = best
            spec = self.fire_control(shooter.asset, self.shadows[target_id].asset)

            if spec is None:
                # ROE o arma inadatta: questo bersaglio non verra' mai ingaggiato da lui.
                candidates[index].exhausted = True
                continue

            if not isinstance(spec, ShotSpec):
                raise TypeError(f"fire_control must return a ShotSpec or None, got {type(spec).__name__}")

            rounds = spec.rounds if shooter.ammunition is None else min(spec.rounds, shooter.ammunition)
            self.assigned[shooter_id] = target_id
            self._push(t_fire, _LAUNCH, shooter_id, (index, spec, rounds))
            return

    def _refire_interval(self, shooter_id: str, spec: ShotSpec) -> float:
        return spec.cycle_time if spec.cycle_time is not None else self._profile(shooter_id).refire_interval

    def _on_launch(self, time: float, shooter_id: str, payload) -> None:
        index, spec, rounds = payload
        # Il lancio schedulato si esaurisce qui, qualunque sia l'esito: se la salva parte,
        # la copertura passa a `in_flight`; se e' annullata, non copre piu' nulla.
        self.assigned.pop(shooter_id, None)

        shooter = self.shadows[shooter_id]

        if shooter.force_id in self.broken_forces:
            # La forza del lanciatore ha rotto il contatto: il lancio non ancora eseguito e'
            # annullato, e il tiratore non ne schedula altri.
            return

        if not shooter.operative:
            # Lanciatore fuori combattimento prima del lancio: la salva non parte.
            return

        candidate = self.candidates[shooter_id][index]
        target = self.shadows[candidate.target_id]
        next_time = time + self._refire_interval(shooter_id, spec)

        if not target.operative or target.force_id in self.broken_forces \
                or time > candidate.t_end + TIME_EPS:
            # Bersaglio fuori combattimento, la sua forza ha rotto il contatto, o finestra
            # chiusa. Annullamento, non riscrittura (R4): la prossima decisione e' un nuovo
            # evento (con N forze il tiratore puo' passare a un bersaglio di un'altra forza).
            candidate.exhausted = True
            self._schedule_next(shooter_id, next_time)
            return

        if shooter.ammunition is not None and shooter.ammunition < rounds:
            # Scorta erosa dopo lo scheduling (intercettazioni): stesso trattamento.
            self._schedule_next(shooter_id, next_time)
            return

        if shooter.ammunition is not None:
            shooter.ammunition -= rounds

        self.ammunition_events.append(AmmunitionEvent(time=time, asset_id=shooter_id,
                                                      rounds=rounds, purpose=PURPOSE_SALVO))

        salvo = Salvo(salvo_id=len(self.salvos), t_launch=time,
                      t_impact=time + float(spec.time_of_flight), shooter_id=shooter_id,
                      target_id=target.id, target_force_id=target.force_id,
                      rounds=rounds, spec=spec)
        self.salvos.append(salvo)
        self.in_flight[salvo.salvo_id] = salvo
        self._touch(time)
        self._push(salvo.t_impact, _IMPACT, target.force_id, salvo)
        self._schedule_next(shooter_id, next_time)

    # ── fase 3: impatto, saturazione, danno ───────────────────────────────────

    def _on_impact(self, time: float, force_id: str, salvo: Salvo) -> None:
        group = self.pending.get(force_id)

        if group is None or time > group.resolve_time + TIME_EPS:
            group = _PendingGroup(resolve_time=time + self.salvo_window)
            self.pending[force_id] = group
            self._push(group.resolve_time, _RESOLVE, force_id, None)

        group.salvos.append(salvo)

    def _capacity(self, state: _ForceState) -> int:
        """Capacita' di intercettazione attuale: stessa formula di Military.salvo_interception_capacity."""
        capacity = 0

        for shadow, channels in state.interceptors:
            if not shadow.operative:
                continue

            capacity += channels if shadow.ammunition is None else min(channels, shadow.ammunition)

        return capacity

    def _on_resolve(self, time: float, force_id: str) -> None:
        group = self.pending.pop(force_id, None)

        if group is None or not group.salvos:
            return

        state = self.force_states[force_id]
        committed = state.committed
        before = {asset_id for asset_id in committed if self.shadows[asset_id].operative}
        ordered = sorted(group.salvos, key=lambda s: (s.t_impact, s.salvo_id))

        for salvo in ordered:
            self.in_flight.pop(salvo.salvo_id, None)

        rounds = sum(s.rounds for s in ordered)
        interceptable = sum(s.rounds for s in ordered if s.spec.interceptable)
        capacity = self._capacity(state)
        intercepted = min(interceptable, capacity)

        # Ogni intercettazione e' un colpo sparato dal difensore (R3): consumo esplicito,
        # asset in ordine di id.
        remaining = intercepted

        for shadow, channels in state.interceptors:
            if remaining <= 0:
                break

            if not shadow.operative:
                continue

            available = channels if shadow.ammunition is None else min(channels, shadow.ammunition)
            used = min(available, remaining)

            if used <= 0:
                continue

            if shadow.ammunition is not None:
                shadow.ammunition -= used

            self.ammunition_events.append(AmmunitionEvent(time=time, asset_id=shadow.id,
                                                          rounds=used, purpose=PURPOSE_INTERCEPTION))
            remaining -= used

        # I colpi fermati sono i primi intercettabili nell'ordine (impatto, salva).
        stopped: Dict[int, int] = {}
        left = intercepted

        for salvo in ordered:
            if left <= 0:
                break

            if salvo.spec.interceptable:
                stopped[salvo.salvo_id] = min(salvo.rounds, left)
                left -= stopped[salvo.salvo_id]

        wasted = 0

        for salvo in ordered:
            target = self.shadows[salvo.target_id]

            for _ in range(salvo.rounds - stopped.get(salvo.salvo_id, 0)):
                if target.destroyed:
                    # Payload congelato (R4): il colpo arriva comunque, ma su un relitto.
                    wasted += 1
                    continue

                event = DM.build_damage_event(target, salvo.spec.accuracy, salvo.spec.destroy_capacity,
                                              self._draw(), time=time, source_id=salvo.shooter_id,
                                              weapon=salvo.spec.weapon, provenance=self.provenance)
                target.health = event.health_after
                self.damage_events.append(event)

        after = {asset_id for asset_id in committed if self.shadows[asset_id].operative}
        losses = tuple(sorted(before - after))
        shock = len(losses) / len(committed)
        erosion = (len(committed) - len(after)) / len(committed)

        self.resolutions.append(SalvoResolution(time=time, force_id=force_id,
                                                salvo_ids=tuple(s.salvo_id for s in ordered),
                                                rounds=rounds, interceptable_rounds=interceptable,
                                                capacity=capacity, intercepted=intercepted,
                                                wasted=wasted, losses=losses, shock=shock,
                                                erosion=erosion))
        self._touch(time)
        self._check_doctrine(time, state, shock, erosion, len(after))

    # ── fase 4: disingaggio ───────────────────────────────────────────────────

    def _check_doctrine(self, time: float, state: _ForceState, shock: float, erosion: float,
                        operative_left: int) -> None:
        """Confronta le perdite con la dottrina del lato, per la FORZA INTERA (P1 + R2).

        Le due soglie sono verificate con la stessa regola per entrambi i lati: nessun
        trattamento speciale per chi ha colpito o per chi ha iniziato (R2 lo richiede
        esplicitamente, per non ereditare l'applicazione incoerente della fonte).
        """
        state.max_shock = max(state.max_shock, shock)

        if operative_left == 0:
            # Annientamento: prevale su un disingaggio gia' deciso (la forza e' stata
            # distrutta mentre rompeva il contatto, da salve gia' in volo).
            if state.outcome != DESTROYED:
                state.outcome = DESTROYED
                state.time = time
                state.triggers = (TRIGGER_ANNIHILATION,)
            self.broken_forces.add(state.force_id)
            return

        if state.outcome is not None or state.thresholds is None:
            return

        triggers = []

        if erosion >= state.thresholds[Doctrine.DISENGAGEMENT_EROSION] - FRACTION_EPS:
            triggers.append(TRIGGER_EROSION)

        if shock >= state.thresholds[Doctrine.DISENGAGEMENT_SHOCK] - FRACTION_EPS:
            triggers.append(TRIGGER_SHOCK)

        if triggers:
            state.outcome = DISENGAGED
            state.time = time
            state.triggers = tuple(triggers)
            self.broken_forces.add(state.force_id)
            logger.debug(f"force {state.force_id!r} disengages at t={time} ({triggers}): "
                         f"erosion={erosion:.3f}, shock={shock:.3f}")

    # ── ciclo principale ──────────────────────────────────────────────────────

    def run(self) -> EngagementResult:
        self._detect()

        for shooter_id in sorted(self.candidates):
            self._schedule_next(shooter_id, float('-inf'))

        while self.queue:
            time, kind, key, _, payload = heapq.heappop(self.queue)

            if kind == _LAUNCH:
                self._on_launch(time, key, payload)
            elif kind == _IMPACT:
                self._on_impact(time, key, payload)
            else:
                self._on_resolve(time, key)

        return self._result()

    def _result(self) -> EngagementResult:
        outcomes = []

        for force_id in self.force_order:
            state = self.force_states[force_id]
            committed = len(state.committed)
            operative = sum(1 for asset_id in state.committed if self.shadows[asset_id].operative)
            lost = committed - operative

            outcomes.append(ForceOutcome(force_id=force_id, side=state.side,
                                         outcome=state.outcome or HELD, time=state.time,
                                         triggers=state.triggers, committed=committed, lost=lost,
                                         erosion=lost / committed if committed else 0.0,
                                         max_shock=state.max_shock))

        return EngagementResult(t_start=self.t_start,
                                t_end=self.t_end if self.t_end is not None else self.t_start,
                                forces=tuple(outcomes),
                                detections=tuple(self.detections),
                                salvos=tuple(self.salvos),
                                resolutions=tuple(self.resolutions),
                                damage_events=tuple(self.damage_events),
                                ammunition_events=tuple(self.ammunition_events))


def resolve_engagement(force_a, force_b, contacts: Iterable, fire_control: Callable, rng, *,
                       extra_forces: Sequence = (),
                       legs: Optional[Mapping[str, Sequence]] = None,
                       committed: Optional[Mapping[str, Iterable[str]]] = None,
                       thresholds: Optional[Dict] = None,
                       reaction_profile_for: Optional[Callable] = None,
                       detection_factor: Optional[Callable] = None,
                       salvo_window: float = 0.0,
                       provenance: str = DM.DERIVED) -> Optional[EngagementResult]:
    """Risolve un ingaggio fra due o piu' forze, in un'unica timeline. Non muta alcun asset.

    Args:
        force_a/force_b: due delle forze — `Military` o qualunque oggetto con `assets`
            (dict di asset), `side`, `name`; se espongono `salvo_interceptors()` la loro
            difesa satura le salve in arrivo (R1).
        extra_forces: altre forze della stessa run, oltre alle prime due (default nessuna:
            ingaggio a due, comportamento invariato). Le forze della run sono
            `(force_a, force_b, *extra_forces)`, tutte trattate allo stesso modo: nessuna
            delle prime due ha un ruolo speciale, l'ordine decide solo l'ordine di
            `EngagementResult.forces`. Chi combatte contro chi lo decidono le finestre in
            `contacts`, non i lati (v. "Ingaggi a N forze" nel docstring del modulo).
        contacts: le `ContactWindow` di `Contact_Scheduler` fra asset di forze diverse. Le
            finestre con asset non impegnati, o fra asset della stessa forza, sono ignorate.
            Con `range_type='engagement_range'` lo scheduler produce finestre "a tiro"
            invece che "a vista": la scelta e' del chiamante.
        fire_control: `(shooter, target) -> ShotSpec | None`, riceve gli asset REALI (per
            la selezione dell'arma, non per leggerne lo stato: lo stato che evolve e'
            quello ombra del risolutore).
        rng: oggetto con `.random()` in [0, 1), es. `random.Random(seed)`. Unica sorgente
            di casualita'.
        legs: `{asset_id: [Leg, ...]}` (`Contact_Scheduler.route_legs/static_legs`) per
            ricavare l'istante esatto di rilevamento; senza, v. `_detection_time`.
        committed: `{force_id: [asset_id, ...]}` per impegnare solo una parte della forza;
            di default tutti gli asset operativi.
        thresholds: tabella dottrinale al posto di `Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS`.
        reaction_profile_for: `asset -> ReactionProfile`, default
            `Reaction_Profile.profile_for_asset`.
        detection_factor: `(observer, target) -> float in [0, 1]`, degradazione della Pd
            (meteo, notte, disturbo); default nessuna degradazione.
        salvo_window: secondi entro cui impatti successivi sulla stessa forza fanno parte
            dello STESSO evento-salva (saturazione e shock). Default 0: solo impatti
            simultanei — la scelta piu' conservativa; quale finestra usare e' un punto
            aperto di modello, da decidere con la taratura.
        provenance: provenienza dei DamageEvent prodotti (default DERIVED).

    Returns:
        `EngagementResult`, oppure None (con un log) se meno di due forze hanno asset
        impegnabili — con due forze: se una delle due non ne ha. Con 3+ forze una forza
        senza asset impegnabili compare nell'esito con committed=0 e HELD.

    Raises:
        TypeError: `rng` senza `.random()`, `fire_control` non chiamabile o che non
            restituisce una ShotSpec.
        ValueError: `salvo_window` negativo, provenance sconosciuta, forze ripetute o
            con asset in comune.
    """
    if not callable(getattr(rng, 'random', None)):
        raise TypeError("rng must expose a random() method returning a float in [0, 1)")

    if not callable(fire_control):
        raise TypeError("fire_control must be callable")

    if isinstance(salvo_window, bool) or not isinstance(salvo_window, (int, float)) or salvo_window < 0:
        raise ValueError(f"salvo_window must be a non-negative number, got {salvo_window!r}")

    if provenance not in DM.PROVENANCES:
        raise ValueError(f"provenance must be one of {DM.PROVENANCES}, got {provenance!r}")

    extra_forces = tuple(extra_forces) if extra_forces is not None else ()

    run = _EngagementRun((force_a, force_b) + extra_forces, contacts, fire_control, rng, legs,
                         committed, thresholds, reaction_profile_for, detection_factor,
                         salvo_window, provenance)

    if not run.usable:
        return None

    return run.run()


def apply_engagement_result(result: EngagementResult, *forces) -> Dict[str, int]:
    """Applica un esito agli asset reali: danni (Damage_Model) e consumi di munizioni.

    E' il passo separato che il risolutore non fa da se': cosi' un esito puo' essere
    ispezionato, confrontato fra repliche o scartato senza aver toccato la campagna.
    I DamageEvent si applicano nell'ordine in cui sono stati prodotti (i loro delta sono
    coerenti con quell'ordine); le munizioni con `consume_ammunition`.

    Returns:
        {'damage_events': applicati, 'ammunition_events': applicati, 'missing_assets': non
        trovati} — un asset non trovato e' registrato e saltato, non e' un errore.
    """
    if not isinstance(result, EngagementResult):
        raise TypeError(f"result must be an EngagementResult, got {type(result).__name__}")

    assets: Dict[str, object] = {}

    for force in forces:
        for asset in (getattr(force, 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is not None:
                assets[asset_id] = asset

    summary = {'damage_events': 0, 'ammunition_events': 0, 'missing_assets': 0}

    for event in result.damage_events:
        asset = assets.get(event.target_id)

        if asset is None:
            logger.warning(f"apply_engagement_result: target {event.target_id!r} not found")
            summary['missing_assets'] += 1
            continue

        DM.apply_damage_event(asset, event)
        summary['damage_events'] += 1

    for event in result.ammunition_events:
        asset = assets.get(event.asset_id)

        if asset is None:
            logger.warning(f"apply_engagement_result: shooter {event.asset_id!r} not found")
            summary['missing_assets'] += 1
            continue

        consume = getattr(asset, 'consume_ammunition', None)

        if callable(consume):
            consume(event.rounds)

        summary['ammunition_events'] += 1

    return summary
