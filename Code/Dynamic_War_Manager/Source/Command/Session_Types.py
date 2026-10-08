"""
MODULE Session_Types

Contratto di dominio delle porte di sessione: `SessionOrder` (core -> sessione) e
`SessionOutcome` (sessione -> core). E' la "Fase 0" della roadmap del motore di sessioni
virtuali (§8 di `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`),
rimasta indietro rispetto alle fasi 1-4 e chiusa qui insieme alla Fase 5.

## Vincolo che questo modulo incarna (wiki decisions/core-simulator-agnostic)
Le due porte sono cio' a cui QUALUNQUE esecutore di sessione deve conformarsi: il risolutore
sintetico del core oggi, un adapter DCS domani. Quindi:
  * nessun identificativo, unita' o concetto del simulatore: solo id di dominio (stringhe),
    secondi assoluti dall'inizio sessione, metri;
  * provenienza dichiarata per dato: gli eventi atomici la portano gia' (`DamageEvent`,
    `FuelEvent`: `measured`/`derived`/`estimated`, costanti di `Logic/Damage_Model`);
  * i tipi atomici NON sono duplicati: `ForceOutcome`/`AmmunitionEvent`/
    `InterceptionEvent`/`EngagementResult` vengono da `Logic/Engagement_Resolver`, `DamageEvent` da `Logic/Damage_Model`,
    `FuelEvent` da `Logic/Fuel_Model`. Questo modulo definisce solo i contenitori.

## Missioni alla porta (Fase 3 di `Analysis/Document/Piano_Implementazione_Missione.md`)
`SessionOrder` porta le `Mission` e le `Operation` di `Command/Mission_Types` (la forma e' quella
decisa in D1-D6/N1-N3): le missioni sono l'UNICA strada con cui un asset riceve rotta, partenza e
velocita' in una sessione (`Logic/Mission_Adapter` le ricava, `Logic/Session_Simulator` le
consuma). `SessionOutcome` porta l'esito di ogni missione (`MissionOutcome`, prima forma: v.
`Session_Simulator`). Qui solo validazione strutturale dell'ordine (unicita', riferimenti):
l'appartenenza degli asset al blocco si verifica con gli oggetti del modello, in `run_session`.

## Cosa NON c'e' (di proposito)
  * Nessun concetto che il codice non ha ancora: obiettivi di campagna, finestre di sessione
    di campagna (F8), re-scheduling. Quel livello nascera' con `Theater_Session_Manager`;
    aggiungerlo ora vorrebbe dire inventarne la forma.
  * Nessuna scrittura in `Campaign_State` e nessuna applicazione agli asset:
    `assemble_session_outcome` e' una funzione pura. Applicare l'esito "in un'unica passata"
    e' responsabilita' di `Theater_Session_Manager` (wiki decisions/c2-hierarchy-design),
    non ancora costruito.
  * Nessun componente LLM, in nessuna forma.

Stile di `Command/Command_Types.py`: dataclass, nessuna logica di calcolo oltre alla
validazione e all'aggregazione. Import di `Logic` a livello di modulo: nessun ciclo, perche'
nessun modulo di `Logic`/`Asset`/`Context` importa questo file.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Iterable, Mapping, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import Mission, MissionOutcome, Operation
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS
from Code.Dynamic_War_Manager.Source.Logic.Damage_Model import DamageEvent
from Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver import (
    AmmunitionEvent,
    EngagementResult,
    ForceOutcome,
    InterceptionEvent,
)
from Code.Dynamic_War_Manager.Source.Logic.Fuel_Model import FuelEvent
from Code.Dynamic_War_Manager.Source.Utility import Session_Rng
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Session_Types').logger


def _check_domain_id(label: str, value) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{label} must be a non-empty str (domain id), got {value!r}")

    return value


def _check_time(label: str, value) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number of seconds or None, got {value!r}")

    return float(value)


def _as_tuple(label: str, value, item_type) -> tuple:
    if isinstance(value, (str, bytes)) or not hasattr(value, '__iter__'):
        raise TypeError(f"{label} must be an iterable of {item_type.__name__}, got {value!r}")

    items = tuple(value)

    for item in items:
        if not isinstance(item, item_type):
            raise TypeError(f"{label} items must be {item_type.__name__}, got {type(item).__name__}")

    return items


def _check_mission_outcomes(value) -> Mapping[str, MissionOutcome]:
    """`{mission_id: MissionOutcome}` reso immutabile; chiave = `mission_id` dell'esito."""
    if not isinstance(value, Mapping):
        raise TypeError(f"mission_outcomes must be a mapping mission_id -> MissionOutcome, "
                        f"got {type(value).__name__}")

    normalized: Dict[str, MissionOutcome] = {}

    for mission_id, outcome in value.items():
        _check_domain_id('mission_outcomes key', mission_id)

        if not isinstance(outcome, MissionOutcome):
            raise TypeError(f"mission_outcomes[{mission_id!r}] must be a MissionOutcome, "
                            f"got {type(outcome).__name__}")

        if outcome.mission_id != mission_id:
            raise ValueError(f"mission_outcomes key {mission_id!r} differs from its mission_id "
                             f"{outcome.mission_id!r}")

        normalized[mission_id] = outcome

    return MappingProxyType(normalized)


def _check_interval(t_start: Optional[float], t_end: Optional[float]) -> None:
    if t_start is not None and t_end is not None and t_end < t_start - TIME_EPS:
        raise ValueError(f"t_end ({t_end}) precedes t_start ({t_start})")


# ── PORTA DI INGRESSO ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SessionOrder:
    """Cosa una sessione deve simulare. Minimo e onesto: solo cio' che il core sa gia' usare.

    Ogni campo corrisponde a un parametro che i componenti esistenti consumano oggi
    (`Engagement_Resolver.resolve_engagement`, `Session_Rng`), niente di piu'.

    Attributes:
        session_id: id di dominio della sessione. E' anche la RADICE DEL SEED: tutte le
            estrazioni della sessione derivano da `Session_Rng.session_seed(session_id, ...)`,
            quindi due sessioni con lo stesso id e lo stesso ordine di eventi producono la
            stessa storia (decisione "riproducibile da seed", §9 del documento).
        t_start/t_end: intervallo della sessione [s]. `t_end` None = aperto (la durata la
            decide l'esecutore).
        force_ids: id di dominio delle forze coinvolte (i `Military.name`, cioe' cio' che
            `Engagement_Resolver` usa come id di forza). Id, non oggetti: la porta deve poter
            attraversare il confine verso un adapter esterno.
        committed: `{force_id: (asset_id, ...)}` per impegnare solo una parte di una forza;
            stessa forma e semantica del parametro `committed` di `resolve_engagement`.
            Assente o forza non elencata = tutti gli asset operativi. Chiavato per BLOCCO anche
            dalla F4b: `Session_Simulator` lo traduce per forza d'ingaggio (missione),
            intersecando la restrizione del blocco con gli asset di ciascuna missione.
        salvo_window: secondi che raggruppano impatti successivi in un unico evento-salva,
            passato tale e quale a `resolve_engagement` (default 0.0, stesso default).
        missions: le `Mission` della sessione (Fase 3 del piano della Missione), default
            nessuna: gli asset senza missione restano fermi. Vincoli: `mission_id` unici; un
            asset in AL PIU' una missione della sessione (un blocco puo' invece avere piu'
            missioni nella stessa sessione, regola dell'utente 2026-10-05); `block_id` in
            `force_ids` se `force_ids` non e' vuoto.
        operations: le `Operation` della sessione, default nessuna. Vincoli: `operation_id`
            unici; ogni `mission_ids` si riferisce a missioni di questo ordine; una missione
            in al piu' un'operazione, e se dichiara `operation_id` deve essere quello
            dell'operazione che la elenca (se quell'operazione e' nell'ordine).
    """
    session_id: str
    t_start: float = 0.0
    t_end: Optional[float] = None
    force_ids: Tuple[str, ...] = ()
    committed: Optional[Mapping[str, Tuple[str, ...]]] = field(default=None, hash=False)
    salvo_window: float = 0.0
    missions: Tuple[Mission, ...] = ()
    operations: Tuple[Operation, ...] = ()

    def __post_init__(self):
        _check_domain_id('session_id', self.session_id)

        t_start = _check_time('t_start', self.t_start)

        if t_start is None:
            raise TypeError("t_start must be a number of seconds")

        t_end = _check_time('t_end', self.t_end)
        _check_interval(t_start, t_end)
        object.__setattr__(self, 't_start', t_start)
        object.__setattr__(self, 't_end', t_end)

        force_ids = tuple(self.force_ids)

        for force_id in force_ids:
            _check_domain_id('force_ids item', force_id)

        if len(set(force_ids)) != len(force_ids):
            raise ValueError(f"force_ids must be distinct, got {force_ids}")

        object.__setattr__(self, 'force_ids', force_ids)

        if self.committed is not None:
            if not isinstance(self.committed, Mapping):
                raise TypeError(f"committed must be a mapping force_id -> asset ids, "
                                f"got {type(self.committed).__name__}")

            normalized: Dict[str, Tuple[str, ...]] = {}

            for force_id, asset_ids in self.committed.items():
                _check_domain_id('committed key', force_id)

                if force_ids and force_id not in force_ids:
                    raise ValueError(f"committed force {force_id!r} is not in force_ids {force_ids}")

                if isinstance(asset_ids, str):
                    raise TypeError(f"committed[{force_id!r}] must be an iterable of asset ids, not a str")

                normalized[force_id] = tuple(_check_domain_id(f"committed[{force_id!r}] item", a)
                                             for a in asset_ids)

            object.__setattr__(self, 'committed', MappingProxyType(normalized))

        if isinstance(self.salvo_window, bool) or not isinstance(self.salvo_window, (int, float)) \
                or self.salvo_window < 0:
            raise ValueError(f"salvo_window must be a non-negative number, got {self.salvo_window!r}")

        object.__setattr__(self, 'salvo_window', float(self.salvo_window))
        self._validate_missions(force_ids)
        self._validate_operations()

    def _validate_missions(self, force_ids: Tuple[str, ...]) -> None:
        missions = _as_tuple('missions', self.missions, Mission)
        seen_missions = set()
        asset_mission: Dict[str, str] = {}

        for mission in missions:
            if mission.mission_id in seen_missions:
                raise ValueError(f"mission_id {mission.mission_id!r} is repeated in the order")

            seen_missions.add(mission.mission_id)

            if force_ids and mission.block_id not in force_ids:
                raise ValueError(f"mission {mission.mission_id!r}: block {mission.block_id!r} is not in "
                                 f"force_ids {force_ids}")

            for asset_id in mission.asset_ids:
                if asset_id in asset_mission:
                    raise ValueError(f"asset {asset_id!r} is in missions {asset_mission[asset_id]!r} and "
                                     f"{mission.mission_id!r}: an asset takes part in at most one mission "
                                     f"per session")

                asset_mission[asset_id] = mission.mission_id

        object.__setattr__(self, 'missions', missions)

    def _validate_operations(self) -> None:
        operations = _as_tuple('operations', self.operations, Operation)
        missions = {mission.mission_id: mission for mission in self.missions}
        seen_operations = set()
        mission_operation: Dict[str, str] = {}

        for operation in operations:
            if operation.operation_id in seen_operations:
                raise ValueError(f"operation_id {operation.operation_id!r} is repeated in the order")

            seen_operations.add(operation.operation_id)

            for mission_id in operation.mission_ids:
                if mission_id not in missions:
                    raise ValueError(f"operation {operation.operation_id!r} refers to mission {mission_id!r}, "
                                     f"which is not in the order")

                if mission_id in mission_operation:
                    raise ValueError(f"mission {mission_id!r} is in operations {mission_operation[mission_id]!r} "
                                     f"and {operation.operation_id!r}")

                declared = missions[mission_id].operation_id

                if declared is not None and declared != operation.operation_id:
                    raise ValueError(f"mission {mission_id!r} declares operation {declared!r} but is listed "
                                     f"by {operation.operation_id!r}")

                mission_operation[mission_id] = operation.operation_id

        for mission in self.missions:
            if mission.operation_id in seen_operations and mission.mission_id not in mission_operation:
                raise ValueError(f"mission {mission.mission_id!r} declares operation {mission.operation_id!r}, "
                                 f"which does not list it")

        object.__setattr__(self, 'operations', operations)

    def mission(self, mission_id: str) -> Mission:
        """La missione `mission_id` dell'ordine (KeyError se assente)."""
        for mission in self.missions:
            if mission.mission_id == mission_id:
                return mission

        raise KeyError(mission_id)

    def rng(self, mission_id=None, event_id=None, counter: int = 0) -> random.Random:
        """Il `random.Random` di questa sessione per la chiave data (v. `Session_Rng`)."""
        return Session_Rng.session_rng(self.session_id, mission_id, event_id, counter)

    def committed_map(self) -> Optional[Dict[str, Tuple[str, ...]]]:
        """`committed` come dict ordinario, pronto per `resolve_engagement(committed=...)`."""
        return dict(self.committed) if self.committed is not None else None


# ── PORTA DI USCITA ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SessionOutcome:
    """Tutto cio' che e' successo in una sessione, agnostico dal simulatore. Immutabile.

    Attributes:
        session_id: id di dominio della sessione.
        t_start/t_end: intervallo coperto [s], None se la sessione non ha prodotto nulla e
            l'intervallo non e' stato dichiarato.
        engagement_outcomes: per ogni ingaggio, nell'ordine di risoluzione, gli esiti delle
            forze (`EngagementResult.forces`). Tenuti raggruppati per ingaggio perche' un
            `ForceOutcome` e' relativo al SUO ingaggio (committed/lost/erosion si riferiscono
            agli asset impegnati li'): fonderli fra ingaggi diversi richiederebbe di
            reinventare quella semantica. Una forza impegnata in due ingaggi compare due volte.
            Dalla F4b la forza e' la missione (v. `outcomes_of_block` per gli esiti di un blocco).
        damage_events/ammunition_events/interception_events/fuel_events: gli eventi
            atomici, in ordine di tempo (v. `assemble_session_outcome` per il criterio
            esatto). `ammunition_events` sono le sole salve offensive, `interception_events`
            le intercettazioni (tipi distinti dal 2026-09-23).
        mission_outcomes: `{mission_id: MissionOutcome}`, mapping immutabile, una voce per
            missione dell'ordine (Fase 3 del piano della Missione; regola d'esito di prima
            forma in `Logic/Session_Simulator`). Vuoto se l'ordine non ha missioni.
    """
    session_id: str
    t_start: Optional[float]
    t_end: Optional[float]
    engagement_outcomes: Tuple[Tuple[ForceOutcome, ...], ...] = ()
    damage_events: Tuple[DamageEvent, ...] = ()
    ammunition_events: Tuple[AmmunitionEvent, ...] = ()
    fuel_events: Tuple[FuelEvent, ...] = ()
    interception_events: Tuple[InterceptionEvent, ...] = ()
    mission_outcomes: Mapping[str, MissionOutcome] = field(default_factory=dict, hash=False)

    def __post_init__(self):
        _check_domain_id('session_id', self.session_id)
        _check_interval(_check_time('t_start', self.t_start), _check_time('t_end', self.t_end))
        object.__setattr__(self, 'mission_outcomes', _check_mission_outcomes(self.mission_outcomes))

    @property
    def force_outcomes(self) -> Tuple[ForceOutcome, ...]:
        """Tutti gli esiti di forza, appiattiti nell'ordine degli ingaggi."""
        return tuple(outcome for engagement in self.engagement_outcomes for outcome in engagement)

    def outcomes_of(self, force_id: str) -> Tuple[ForceOutcome, ...]:
        """Gli esiti della forza `force_id`, uno per ingaggio a cui ha partecipato."""
        return tuple(outcome for outcome in self.force_outcomes if outcome.force_id == force_id)

    def outcomes_of_block(self, block_id: str) -> Tuple[ForceOutcome, ...]:
        """Gli esiti delle forze d'ingaggio del blocco `block_id`, nell'ordine degli ingaggi.

        Dalla F4b del piano della Missione la forza d'ingaggio e' la missione (`ForceOutcome.force_id`
        = `mission_id`, `block_id` = blocco); un blocco senza missioni, o la vista residua dei suoi
        asset senza missione, ha `force_id` = id del blocco. L'esito del blocco e' questo INSIEME, non
        un esito sintetico: le sue missioni hanno combattuto e disingaggiato separatamente.
        """
        return tuple(outcome for outcome in self.force_outcomes
                     if outcome.block_id == block_id or (outcome.block_id is None and outcome.force_id == block_id))

    def ammunition_consumed(self) -> Dict[str, int]:
        """Unita' di scorta spese OFFENSIVAMENTE per asset nell'intera sessione (solo salve).

        Cambio di comportamento del 2026-09-23: fino ad allora sommava anche le
        intercettazioni, registrate come AmmunitionEvent. Ora sono `InterceptionEvent` e
        si leggono con `interceptions_consumed()`. Con la scorta per arma (2026-09-26) un
        missile AD usato per intercettare cala la stessa voce della salva offensiva: il
        calo totale di quella voce e' la somma dei due conteggi.
        """
        consumed: Dict[str, int] = {}

        for event in self.ammunition_events:
            consumed[event.asset_id] = consumed.get(event.asset_id, 0) + event.rounds

        return consumed

    def ammunition_consumed_by_weapon(self) -> Dict[str, Dict[Optional[str], int]]:
        """Come `ammunition_consumed`, ripartito per arma: {asset: {arma | None: unita'}}.

        E' la forma che la porta verso il simulatore ricevera' dall'altro lato (payload per
        pilone di DCE, `Unit.getAmmo` per arma): la scorta per arma (2026-09-26) non va
        appiattita all'uscita. None = salve senza arma dichiarata (pool anonimo).
        """
        consumed: Dict[str, Dict[Optional[str], int]] = {}

        for event in self.ammunition_events:
            by_weapon = consumed.setdefault(event.asset_id, {})
            by_weapon[event.weapon] = by_weapon.get(event.weapon, 0) + event.rounds

        return consumed

    def interceptions_consumed(self) -> Dict[str, int]:
        """Intercettazioni effettuate per asset nell'intera sessione (`interception_events`)."""
        consumed: Dict[str, int] = {}

        for event in self.interception_events:
            consumed[event.asset_id] = consumed.get(event.asset_id, 0) + event.interceptions

        return consumed

    def fuel_consumed(self) -> Dict[str, float]:
        """Carburante consumato per asset nell'intera sessione [frazione del carico pieno]."""
        consumed: Dict[str, float] = {}

        for event in self.fuel_events:
            consumed[event.asset_id] = consumed.get(event.asset_id, 0.0) + event.amount

        return consumed


def _event_time_bounds(times: Iterable[float]) -> Tuple[Optional[float], Optional[float]]:
    values = list(times)

    if not values:
        return None, None

    return min(values), max(values)


def assemble_session_outcome(session_id: str,
                             engagement_results: Iterable[Optional[EngagementResult]],
                             fuel_events: Iterable[FuelEvent] = (),
                             t_start: Optional[float] = None,
                             t_end: Optional[float] = None,
                             mission_outcomes: Optional[Mapping[str, MissionOutcome]] = None
                             ) -> SessionOutcome:
    """Aggrega gli esiti di una sessione in un unico `SessionOutcome`. Funzione pura.

    Non tocca alcun asset, non scrive `Campaign_State`, non estrae numeri casuali.

    Args:
        session_id: id di dominio della sessione.
        engagement_results: gli `EngagementResult` prodotti da chiamate separate a
            `resolve_engagement`, una per coppia di forze in contatto, **nell'ordine in cui
            sono stati risolti** — l'ordine e' parte del contratto (v. sotto). I None (il
            valore che `resolve_engagement` restituisce quando un ingaggio non e' risolvibile)
            sono saltati con un log.
        fuel_events: i `FuelEvent` dei movimenti della sessione (`Fuel_Model.build_fuel_event`).
        t_start/t_end: intervallo dichiarato [s]. Se None, e' ricavato dagli ingaggi e dagli
            eventi (min/max); se dichiarato, ogni ingaggio ed evento deve cadervi dentro.
        mission_outcomes: `{mission_id: MissionOutcome}` gia' calcolati dall'esecutore,
            riportati tali e quali (None = nessuna missione).

    Ordine degli eventi nel risultato: per ciascun tipo, ordinamento STABILE per `time`
    sulla concatenazione degli eventi nell'ordine degli ingaggi. Dentro un ingaggio gli eventi
    sono gia' in ordine di tempo non decrescente (la coda del risolutore), quindi l'ordine
    interno — con cui i delta dei DamageEvent sono coerenti — e' preservato; a parita' di
    istante fra ingaggi diversi vale l'ordine degli ingaggi. Stesso input, stesso output.

    Limite noto, dichiarato: se due ingaggi della stessa sessione coinvolgono lo stesso asset
    e sono stati risolti SENZA applicare il primo esito prima del secondo, i campi
    `health_before/after` dei loro DamageEvent non sono concatenabili (ogni ingaggio ha
    letto la salute di partenza). I delta restano applicabili in sequenza. Qui lo si segnala
    con un warning; evitarlo e' compito dell'orchestratore (Fase 6).

    Returns:
        Il `SessionOutcome` (anche vuoto: una sessione senza contatti e' un esito valido).

    Raises:
        TypeError: session_id non valido, elementi che non sono EngagementResult/FuelEvent.
        ValueError: intervallo incoerente, o eventi fuori dall'intervallo dichiarato.
    """
    _check_domain_id('session_id', session_id)
    t_start = _check_time('t_start', t_start)
    t_end = _check_time('t_end', t_end)
    _check_interval(t_start, t_end)

    results = []

    for index, result in enumerate(engagement_results):
        if result is None:
            logger.debug(f"assemble_session_outcome: engagement result #{index} is None "
                         f"(unresolvable engagement), skipped")
            continue

        if not isinstance(result, EngagementResult):
            raise TypeError(f"engagement_results must contain EngagementResult or None, "
                            f"got {type(result).__name__} at #{index}")

        results.append(result)

    fuel = tuple(fuel_events)

    for event in fuel:
        if not isinstance(event, FuelEvent):
            raise TypeError(f"fuel_events must contain FuelEvent, got {type(event).__name__}")

    _warn_shared_targets(session_id, results)

    by_time = lambda event: event.time  # noqa: E731 — sorted() e' stabile
    damage = tuple(sorted((e for r in results for e in r.damage_events), key=by_time))
    ammunition = tuple(sorted((e for r in results for e in r.ammunition_events), key=by_time))
    interceptions = tuple(sorted((e for r in results for e in r.interception_events), key=by_time))
    fuel = tuple(sorted(fuel, key=by_time))

    starts = [r.t_start for r in results if r.t_start is not None]
    ends = [r.t_end for r in results if r.t_end is not None]
    event_times = [e.time for e in damage + ammunition + interceptions + fuel]
    low, high = _event_time_bounds(starts + ends + event_times)

    if t_start is not None and low is not None and low < t_start - TIME_EPS:
        raise ValueError(f"session {session_id!r}: activity at t={low} precedes declared t_start={t_start}")

    if t_end is not None and high is not None and high > t_end + TIME_EPS:
        raise ValueError(f"session {session_id!r}: activity at t={high} follows declared t_end={t_end}")

    return SessionOutcome(session_id=session_id,
                          t_start=t_start if t_start is not None else low,
                          t_end=t_end if t_end is not None else high,
                          engagement_outcomes=tuple(r.forces for r in results),
                          damage_events=damage,
                          ammunition_events=ammunition,
                          interception_events=interceptions,
                          fuel_events=fuel,
                          mission_outcomes=mission_outcomes if mission_outcomes is not None else {})


def _warn_shared_targets(session_id: str, results) -> None:
    """Segnala asset colpiti in piu' di un ingaggio della stessa sessione (v. limite noto)."""
    seen: Dict[str, int] = {}

    for index, result in enumerate(results):
        for target_id in {e.target_id for e in result.damage_events if e.target_id is not None}:
            if target_id in seen and seen[target_id] != index:
                logger.warning(f"assemble_session_outcome: session {session_id!r}, asset {target_id!r} "
                               f"is damaged in engagements #{seen[target_id]} and #{index}: their "
                               f"health_before/after are not chained (deltas still apply in order)")
            seen.setdefault(target_id, index)
