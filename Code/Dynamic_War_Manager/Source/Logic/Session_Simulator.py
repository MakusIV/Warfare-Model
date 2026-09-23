"""Orchestratore di sessione — fa girare **una sessione virtuale vera**, dall'ordine all'esito.

FASE 6 del motore di sessioni virtuali (v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §6 e §8, e
[[project_virtual_session_engine_design]]): "orchestratore a coda eventi (heapq, clock in
secondi), risoluzione simultanea".

Le fasi 3-5 hanno prodotto i pezzi, ma nessuno li aveva mai messi in fila:

    SessionOrder ──> Contact_Scheduler.schedule_contacts      (strato 1: QUANDO)
                 ──> raggruppamento in componenti connesse di forze
                 ──> Engagement_Resolver.resolve_engagement    (strato 2: COME FINISCE)
                 ──> apply_engagement_result                   (strato 3: danno, munizioni)
                 ──> Fuel_Model.build/apply_fuel_event         (strato 3: carburante)
                 ──> Session_Types.assemble_session_outcome    (porta di uscita)

Questo modulo e' SOLO quella fila: non reimplementa geometria, Pd, latenze, salve, danno o
consumi. Ogni numero che produce viene da uno dei moduli chiamati.

## La coda eventi

Due tipi di evento di sessione, in un `heapq` con chiave `(t, tipo, id, sequenza)`:

- **ENGAGEMENT** — uno per componente connessa di forze (v. sotto): le forze legate,
  direttamente o per tramite di altre, da almeno una `ContactWindow`; istante = inizio
  della prima finestra fra QUALUNQUE coppia della componente. Risolve l'intera componente
  con UNA chiamata a `resolve_engagement` (che ha la propria coda interna di
  lanci/impatti) e ne applica subito l'esito agli asset reali di tutte le sue forze.
- **MOVEMENT** — uno per asset con rotta schedulabile nella sessione; istante = fine del
  suo movimento dentro la sessione. Produce e applica il `FuelEvent` del tragitto.

A parita' d'istante ENGAGEMENT < MOVEMENT, poi l'id (stringa canonica, mai l'ordine di un
dizionario Python). Le finestre di un asset mobile cadono tutte dentro lo span dei suoi
tratti, quindi quando il suo MOVEMENT viene estratto ogni ingaggio che lo coinvolge e' gia'
stato risolto: il regime di consumo (v. sotto) e' noto.

## Forze impegnate su piu' fronti: componenti connesse

**Prima (fino al 2026-09-23): un ingaggio per coppia.** Le finestre erano raggruppate per
coppia (forza del lato A, forza del lato B) e ogni coppia era un ENGAGEMENT separato;
`Session_Types.assemble_session_outcome` dichiara che se due ingaggi coinvolgono lo stesso
asset i `health_before/after` sono concatenabili solo se il primo esito e' applicato prima
di risolvere il secondo, e l'orchestratore lo garantiva applicando ogni esito subito.
Restava pero' un difetto, non solo un'approssimazione: se X era in contatto con A e con B
in finestre SOVRAPPOSTE, l'ingaggio (X,A) estratto per primo era svolto fino alla sua
conclusione e applicato, e (X,B) leggeva uno stato di X gia' consumato anche per le salve
che, in tempo di sessione, precedevano la fine di (X,A). L'ordine della coda decideva chi
"arrivava prima" alla salute e alle scorte di X: un artefatto d'implementazione, non la
fisica del combattimento.

**Ora: un ingaggio per componente connessa.** Si costruisce il grafo non orientato con un
nodo per forza e un arco per ogni coppia (lato A, lato B) con almeno una finestra (la
stessa appartenenza ai lati di prima, `_group_windows`), e se ne cercano le componenti
connesse (`_connected_components`, visita deterministica per id). Ogni componente e'
risolta con UNA chiamata a `resolve_engagement`, con tutte le finestre delle sue coppie:
`force_a`/`force_b` = le prime due forze per id, `extra_forces` = le altre, per id. Dentro
la run lo stato ombra di X evolve in un'unica timeline consumata da tutti i fronti, e un
disingaggio e' per-forza (v. "Forze rotte" in Engagement_Resolver): il disingaggio di X
non ferma un eventuale altro fronte della componente.

Le componenti sono disgiunte: nessuna forza compare in due ingaggi della stessa sessione,
quindi il limite di `assemble_session_outcome` non puo' piu' presentarsi, e l'ordine di
risoluzione delle componenti non influenza gli esiti (resta comunque deterministico).

**Deliberatamente conservativa rispetto al tempo:** non si distingue se le finestre di una
componente si sovrappongono davvero o sono in sequenza (X contro A al mattino, contro B
la sera): anche in quel caso {X, A, B} e' risolta con una sola run. E' sempre corretto,
perche' la coda eventi interna ordina comunque gli eventi nel tempo esatto; un clustering
per intervalli aggiungerebbe complessita' senza aggiungere correttezza.

## RNG: uno stream per ingaggio

`SessionOrder.rng(mission_id=None, event_id=engagement_event_id(*forze), counter=0)`:

- `mission_id=None`: `SessionOrder` non porta ancora missioni (v. il suo docstring, "Cosa
  NON c'e'"); None e' il livello "di sessione" di `Session_Rng`. Quando nascera'
  `Theater_Session_Manager` con le missioni, qui entrera' l'id di missione.
- `event_id`: codifica JSON di `['engagement', id_1, id_2, ...]` con gli id della
  componente ORDINATI — funzione pura dell'INSIEME delle forze (id di dominio), mai
  dell'ordine di iterazione o di passaggio a `run_session`, e non ambigua anche con id che
  contengono separatori (una concatenazione `"a:b"` non lo sarebbe).
- `counter=0`: ogni componente e' risolta una sola volta per sessione. Il contatore resta
  libero per un futuro re-ingaggio (re-scheduling dopo un disingaggio, R4 seconda parte,
  non implementato).

**Precondizione di riproducibilita':** gli id di forza devono essere STABILI fra le
esecuzioni. `Block.__init__` genera l'id con `Utility.setId`, che aggiunge un suffisso
casuale (`'Military.Blue_#822100'`): due `Military` costruite da zero con lo stesso nome
avrebbero id diversi, quindi seed diversi E un diverso ordine della coda. **Corretto
2026-09-23**: `Block.__init__`/`Military.__init__` accettano ora un parametro `id` esplicito
(passthrough opzionale, comportamento invariato se assente) — chi costruisce forze da zero
per un replay/test deve passarlo per avere id stabili, invece di mutare `.id` dopo la
costruzione. In campagna l'id e' comunque quello dell'istanza gia' in memoria (persistito),
quindi il caso comune non è mai stato a rischio.

Stream indipendenti per ingaggio significano che aggiungere o togliere un ingaggio non
sposta le estrazioni degli altri. Aggiungere una forza a una componente, invece, cambia il
suo event_id e quindi l'intero stream della componente: e' voluto, perche' e' un ingaggio
diverso.

## `fire_control`: una sola callable, iniettata

`fire_control(shooter, target) -> ShotSpec | None`, la stessa firma di
`resolve_engagement`, passata tale e quale a ogni ingaggio. Non una per lato: la callable
riceve gli asset REALI e puo' distinguere lato, blocco o modello da se', quindi una mappa
per lato non aggiungerebbe capacita' ma solo una seconda forma dello stesso contratto. La
selezione dell'arma dai registri resta fuori (rimandata dalla Fase 4).

## Carburante

Per ogni asset con rotta in `routes` si prendono i tratti della rotta ritagliati alla
sessione (stessa costruzione di `Contact_Scheduler.schedule_contacts`: `route_legs` +
`clamp_legs`, partenza da `starts`, velocita' da `speeds`) e la distanza e' la somma delle
lunghezze dei tratti. Un solo `FuelEvent` per asset, all'istante di fine movimento.

Regime (scelta dichiarata, la piu' semplice che distingua combattimento da crociera):
`'max'` se l'asset ha **combattuto** nella sessione — ha lanciato una salva, e' stato
bersaglio di una salva, o ha intercettato — altrimenti `'nominal'`. Per gli aerei 'max'
legge il profilo `attack` del loadout, per veicoli e navi il registro non distingue (v.
FUEL_FULL in `Asset/Mobile.py`). Tutto il tragitto e' consumato al regime scelto: per chi ha
combattuto e' una sovrastima **pessimistica** del consumo (il tratto di crociera e'
contato a regime di combattimento), preferita a una ripartizione per intervalli che
richiederebbe di inventare quando comincia e finisce la manovra di combattimento. Se il
regime 'max' non e' ricavabile per l'asset si ricade su 'nominal'.

**Limiti dichiarati:**
- nessun movimento fisico: se il carburante finisce a meta' (`FuelEvent.exhausted`,
  `distance_covered < distance`) l'asset NON viene fermato sulla rotta e i contatti gia'
  calcolati non vengono ricalcolati; l'informazione e' nel `FuelEvent`, e la usera' il
  livello superiore (C2/campagna);
- un asset distrutto a meta' rotta consuma comunque il tragitto intero (il carburante di un
  relitto non ha conseguenze di campagna);
- un asset senza rotta (fermo) non produce FuelEvent.

## Sessione aperta (`SessionOrder.t_end is None`)

Regola conservativa: la durata **non si deduce**. Con `t_end` None il chiamante deve
passare `horizon` esplicito; con `t_end` valorizzato `horizon` e' ricavato (se passato
comunque deve coincidere). Nessuna durata di default inventata.

## Attivita' oltre la fine della sessione

Una salva lanciata poco prima della fine arriva comunque (payload congelato, R4): impatti e
risoluzioni possono cadere dopo `t_start + horizon`. L'esito non viene troncato (sarebbe
cancellare danni gia' decisi): il `t_end` del `SessionOutcome` e' esteso fino all'ultima
attivita', con un log. I contatti invece sono cercati solo dentro la sessione.

## Cosa NON fa
- Non costruisce `Theater_Session_Manager`, non legge/scrive `Campaign_State`.
- Non seleziona l'arma, non rifornisce (munizioni o carburante), non ri-instrada le forze
  che si disingaggiano (restano solo segnalate nell'esito).
- Nessun componente LLM, in nessuna forma.
"""

import heapq
import json
from math import sqrt
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Asset.Mobile import DEFAULT_DETECTION_RANGE_TYPE
from Code.Dynamic_War_Manager.Source.Command.Session_Types import (
    SessionOrder,
    SessionOutcome,
    assemble_session_outcome,
)
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Session_Simulator').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Tipi di evento di sessione, nell'ordine di risoluzione a parita' d'istante (v. docstring).
ENGAGEMENT_EVENT = 0
MOVEMENT_EVENT = 1

# Etichetta del primo elemento dell'event_id di un ingaggio (v. engagement_event_id).
ENGAGEMENT_EVENT_TAG = 'engagement'

# Regimi di consumo (Mobile.FUEL_REGIMES).
CRUISE_REGIME = 'nominal'
COMBAT_REGIME = 'max'


# ── IDENTITA' ─────────────────────────────────────────────────────────────────

def _domain_id(obj) -> Optional[str]:
    """Id di dominio: stesso criterio di Engagement_Resolver/Contact_Scheduler (id, poi name).

    Deve coincidere con quello del risolutore, perche' e' la chiave dei `ForceOutcome` e di
    `committed`: un criterio diverso qui farebbe ignorare in silenzio `committed`.
    """
    for attribute in ('id', 'name'):
        value = getattr(obj, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


def _as_block(item):
    """`Block` o `BlockItem` (che lo incapsula in `.block`): stesso criterio dello scheduler."""
    return getattr(item, 'block', item)


def engagement_event_id(*force_ids: str) -> str:
    """`event_id` dell'RNG per l'ingaggio fra le forze date (2 o piu', una componente).

    JSON di `['engagement', id_1, id_2, ...]` con gli id ORDINATI: funzione pura
    dell'INSIEME degli id — indipendente dall'ordine in cui sono passati e quindi
    dall'ordine con cui le forze arrivano a `run_session` — e non ambigua anche con id che
    contengono separatori.

    Raises:
        ValueError: meno di due id, id non stringa o vuoti, id ripetuti.
    """
    if len(force_ids) < 2:
        raise ValueError(f"an engagement needs at least two force ids, got {force_ids!r}")

    if any(not isinstance(force_id, str) or not force_id for force_id in force_ids):
        raise ValueError(f"force ids must be non-empty strings, got {force_ids!r}")

    if len(set(force_ids)) != len(force_ids):
        raise ValueError(f"force ids must be distinct, got {force_ids!r}")

    return json.dumps([ENGAGEMENT_EVENT_TAG, *sorted(force_ids)],
                      ensure_ascii=True, separators=(',', ':'))


# ── PREPARAZIONE ──────────────────────────────────────────────────────────────

def _session_horizon(order: SessionOrder, horizon: Optional[float]) -> float:
    """Durata [s] della sessione (v. "Sessione aperta" nel docstring del modulo)."""
    if horizon is not None:
        if isinstance(horizon, bool) or not isinstance(horizon, (int, float)) or horizon < 0:
            raise ValueError(f"horizon must be a non-negative number, got {horizon!r}")

        horizon = float(horizon)

    if order.t_end is None:
        if horizon is None:
            raise ValueError(f"session {order.session_id!r} is open (t_end is None): "
                             f"an explicit horizon is required")
        return horizon

    declared = order.t_end - order.t_start

    if horizon is not None and abs(horizon - declared) > CS.TIME_EPS:
        raise ValueError(f"horizon ({horizon}) disagrees with the order interval ({declared})")

    return declared


def _collect_forces(order: SessionOrder, forces_a: Iterable, forces_b: Iterable):
    """Normalizza le forze dei due lati e costruisce la mappa asset -> forza.

    Returns:
        (items_a, items_b, blocks, owner): gli oggetti come passati (per lo scheduler), i
        blocchi per id di forza, e `{asset_id: (lato, force_id)}` con lato 0 (A) o 1 (B).

    Raises:
        ValueError: forza senza id, forza ripetuta o su entrambi i lati, forza non elencata
            in `order.force_ids` (se non vuoto), asset appartenente a due forze.
    """
    items = (list(forces_a or []), list(forces_b or []))
    blocks: Dict[str, object] = {}
    owner: Dict[str, Tuple[int, str]] = {}

    for side_index, side_items in enumerate(items):
        for item in side_items:
            block = _as_block(item)
            force_id = _domain_id(block)

            if force_id is None:
                raise ValueError("every force must have a domain id (id or name)")

            if force_id in blocks:
                raise ValueError(f"force {force_id!r} is passed more than once")

            if order.force_ids and force_id not in order.force_ids:
                raise ValueError(f"force {force_id!r} is not in the order's force_ids {order.force_ids}")

            blocks[force_id] = block

            for asset in (getattr(block, 'assets', None) or {}).values():
                asset_id = _domain_id(asset)

                if asset_id is None:
                    continue

                if asset_id in owner:
                    raise ValueError(f"asset {asset_id!r} belongs to both {owner[asset_id][1]!r} "
                                     f"and {force_id!r}")

                owner[asset_id] = (side_index, force_id)

    if order.committed is not None:
        unknown = sorted(set(order.committed) - set(blocks))

        if unknown:
            logger.warning(f"run_session: committed forces {unknown} match no force passed "
                           f"(force ids are {sorted(blocks)}): their restriction is ignored")

    return items[0], items[1], blocks, owner


def _movement_legs(asset_id, routes, starts, speeds, t0: float, horizon: float) -> List[CS.Leg]:
    """Tratti di MOVIMENTO dell'asset nella sessione, lista vuota se non si muove.

    Stessa costruzione di `Contact_Scheduler._asset_legs` per il ramo con rotta: cosi' il
    tragitto consumato e' esattamente quello su cui sono stati cercati i contatti.
    """
    route = routes.get(asset_id) if asset_id is not None else None

    if route is None:
        return []

    start = float(starts.get(asset_id, t0))
    legs = CS.route_legs(route, t0=start, speed=speeds.get(asset_id))

    if not legs:
        return []

    return CS.clamp_legs(legs, t0, t0 + horizon)


def _legs_distance(legs) -> float:
    """Lunghezza [m] del tragitto: somma delle lunghezze dei tratti."""
    total = 0.0

    for leg in legs:
        total += sqrt(sum((e - s) ** 2 for s, e in zip(leg.p_start, leg.p_end)))

    return total


def _group_windows(windows, owner) -> Dict[Tuple[str, str], List[CS.ContactWindow]]:
    """Finestre raggruppate per coppia (forza lato A, forza lato B), ordine preservato."""
    groups: Dict[Tuple[str, str], List[CS.ContactWindow]] = {}

    for window in windows:
        own_a = owner.get(window.asset_a_id)
        own_b = owner.get(window.asset_b_id)

        if own_a is None or own_b is None:
            logger.debug(f"run_session: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                         f"involves an asset of no known force, skipped")
            continue

        if own_a[0] != 0 or own_b[0] != 1:
            # Non puo' accadere con schedule_contacts (itera A x B), ma il raggruppamento non
            # deve mai scambiare i lati in silenzio.
            logger.warning(f"run_session: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                           f"does not go from side A to side B, skipped")
            continue

        groups.setdefault((own_a[1], own_b[1]), []).append(window)

    return groups


def _connected_components(groups: Mapping[Tuple[str, str], List[CS.ContactWindow]]
                          ) -> List[Tuple[Tuple[str, ...], List[CS.ContactWindow]]]:
    """Componenti connesse del grafo delle forze, con le finestre di ciascuna.

    Nodi: le forze che compaiono in almeno una coppia di `groups`; archi: le coppie con
    almeno una finestra. Visita in ampiezza deterministica: si parte dalle forze in ordine
    di id e i vicini sono visitati in ordine di id — mai l'ordine di un dizionario.

    Returns:
        `[(force_ids ordinati, finestre), ...]`, componenti ordinate per id minimo. Le
        finestre di una componente sono quelle di tutte le sue coppie, concatenate
        nell'ordine delle coppie ordinate (il risolutore le riordina comunque in modo
        canonico, v. `Engagement_Resolver._detect`).
    """
    neighbours: Dict[str, set] = {}

    for force_a, force_b in groups:
        neighbours.setdefault(force_a, set()).add(force_b)
        neighbours.setdefault(force_b, set()).add(force_a)

    component_of: Dict[str, int] = {}
    members: List[List[str]] = []

    for start in sorted(neighbours):
        if start in component_of:
            continue

        index = len(members)
        component_of[start] = index
        frontier = [start]
        found = [start]

        while frontier:
            following = []

            for force_id in frontier:
                for other in sorted(neighbours[force_id]):
                    if other not in component_of:
                        component_of[other] = index
                        found.append(other)
                        following.append(other)

            frontier = following

        members.append(sorted(found))

    windows: List[List[CS.ContactWindow]] = [[] for _ in members]

    for pair in sorted(groups):
        windows[component_of[pair[0]]].extend(groups[pair])

    return [(tuple(ids), group) for ids, group in zip(members, windows)]


def _engaged_assets(result: ER.EngagementResult) -> set:
    """Asset che hanno combattuto: tiratori, bersagli di salve, intercettori."""
    engaged = set()

    for salvo in result.salvos:
        engaged.add(salvo.shooter_id)
        engaged.add(salvo.target_id)

    for event in result.ammunition_events:
        engaged.add(event.asset_id)

    for event in result.interception_events:
        engaged.add(event.asset_id)

    return engaged


def _build_fuel(asset, distance: float, time: float, regime: str, provenance: str):
    """`build_fuel_event` al regime dato, con ricaduta su 'nominal' (v. docstring)."""
    event = FM.build_fuel_event(asset, distance, time=time, regime=regime, provenance=provenance)

    if event is None and regime != CRUISE_REGIME:
        logger.debug(f"run_session: no '{regime}' fuel autonomy for {_domain_id(asset)!r}, "
                     f"falling back to '{CRUISE_REGIME}'")
        event = FM.build_fuel_event(asset, distance, time=time, regime=CRUISE_REGIME,
                                    provenance=provenance)

    return event


# ── API PUBBLICA ──────────────────────────────────────────────────────────────

def run_session(order: SessionOrder, forces_a: Iterable, forces_b: Iterable,
                fire_control: Callable, *,
                horizon: Optional[float] = None,
                routes: Optional[Mapping[str, object]] = None,
                starts: Optional[Mapping[str, float]] = None,
                speeds: Optional[Mapping[str, float]] = None,
                margin: float = 0.0,
                range_type: str = DEFAULT_DETECTION_RANGE_TYPE,
                thresholds: Optional[Dict] = None,
                reaction_profile_for: Optional[Callable] = None,
                detection_factor: Optional[Callable] = None,
                provenance: str = DM.DERIVED) -> SessionOutcome:
    """Esegue una sessione virtuale e restituisce il suo `SessionOutcome`. **Muta gli asset.**

    Danno, munizioni e carburante sono applicati agli asset reali man mano che gli eventi
    sono risolti (ogni componente connessa di forze e' un solo ingaggio, v. docstring del
    modulo). Il `SessionOutcome` restituito e' il resoconto di cio' che e' stato applicato.

    Args:
        order: il `SessionOrder`. Ne vengono usati `session_id` (radice del seed),
            `t_start`, `t_end`, `force_ids` (se non vuoto: le forze passate devono esservi
            elencate), `committed` e `salvo_window`, passati tali e quali al risolutore.
        forces_a/forces_b: `Military`/`Block`/`BlockItem` dei due schieramenti contrapposti.
            Si combatte solo fra A e B, mai dentro lo stesso lato.
        fire_control: `(shooter, target) -> ShotSpec | None`, v. `resolve_engagement`.
        horizon: durata [s]; obbligatoria se `order.t_end` e' None, altrimenti ricavata.
        routes/starts/speeds: `{asset_id: DataType.Route}`, `{asset_id: partenza [s]}`,
            `{asset_id: velocita' [m/s]}` — stessa semantica di `schedule_contacts`. Asset
            senza rotta = fermo in posizione.
        margin/range_type: passati a `schedule_contacts` (range_type decide se le finestre
            sono "a vista" o "a tiro").
        thresholds/reaction_profile_for/detection_factor/provenance: passati a
            `resolve_engagement`; `provenance` vale anche per i FuelEvent.

    Returns:
        Il `SessionOutcome`; vuoto ma valido se nessuno si incontra e nessuno si muove.

    Raises:
        TypeError: `order` non e' un SessionOrder, `fire_control` non chiamabile.
        ValueError: durata mancante o incoerente, forze/asset duplicati o fuori
            `order.force_ids`, e gli errori di dominio dei moduli chiamati.
    """
    if not isinstance(order, SessionOrder):
        raise TypeError(f"order must be a SessionOrder, got {type(order).__name__}")

    if not callable(fire_control):
        raise TypeError("fire_control must be callable")

    if provenance not in DM.PROVENANCES:
        raise ValueError(f"provenance must be one of {DM.PROVENANCES}, got {provenance!r}")

    horizon = _session_horizon(order, horizon)
    t0 = order.t_start
    session_end = t0 + horizon
    routes = routes or {}
    starts = starts or {}
    speeds = speeds or {}

    items_a, items_b, blocks, owner = _collect_forces(order, forces_a, forces_b)

    # ── strato 1: tutti i contatti della sessione ─────────────────────────────
    windows = CS.schedule_contacts(items_a, items_b, horizon, routes=routes, starts=starts,
                                   speeds=speeds, t0=t0, margin=margin, range_type=range_type)
    groups = _group_windows(windows, owner)

    # Tratti di ogni asset (movimento o posizione fissa): servono al risolutore per l'istante
    # esatto di rilevamento, e i tratti di movimento al consumo di carburante.
    all_legs: Dict[str, List[CS.Leg]] = {}
    movements: List[Tuple[str, object, List[CS.Leg]]] = []

    for force_id in sorted(blocks):
        for asset in (getattr(blocks[force_id], 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is None:
                continue

            moving = _movement_legs(asset_id, routes, starts, speeds, t0, horizon)

            if moving:
                all_legs[asset_id] = moving
                movements.append((asset_id, asset, moving))
            else:
                all_legs[asset_id] = CS.static_legs(getattr(asset, 'position', None), t0, session_end)

    # ── coda eventi ───────────────────────────────────────────────────────────
    queue: List = []
    sequence = 0

    # Un evento per COMPONENTE connessa di forze (v. "Forze impegnate su piu' fronti").
    for force_ids, group in _connected_components(groups):
        event_id = engagement_event_id(*force_ids)
        sequence += 1
        heapq.heappush(queue, (min(w.t_start for w in group), ENGAGEMENT_EVENT, event_id,
                               sequence, (force_ids, group)))

    for asset_id, asset, legs in movements:
        sequence += 1
        heapq.heappush(queue, (legs[-1].t_end, MOVEMENT_EVENT, asset_id, sequence, (asset, legs)))

    committed = order.committed_map()
    results: List[Optional[ER.EngagementResult]] = []
    fuel_events: List[FM.FuelEvent] = []
    engaged: set = set()

    while queue:
        time, kind, key, _, payload = heapq.heappop(queue)

        if kind == ENGAGEMENT_EVENT:
            force_ids, group = payload
            component = [blocks[force_id] for force_id in force_ids]
            result = ER.resolve_engagement(component[0], component[1], group, fire_control,
                                           order.rng(mission_id=None, event_id=key, counter=0),
                                           extra_forces=component[2:],
                                           legs=all_legs, committed=committed,
                                           thresholds=thresholds,
                                           reaction_profile_for=reaction_profile_for,
                                           detection_factor=detection_factor,
                                           salvo_window=order.salvo_window,
                                           provenance=provenance)
            results.append(result)

            if result is not None:
                # Applicato SUBITO, a tutte le forze della componente. Le componenti sono
                # disgiunte: nessun altro ingaggio della sessione legge queste forze.
                ER.apply_engagement_result(result, *component)
                engaged |= _engaged_assets(result)
        else:
            asset, legs = payload
            distance = _legs_distance(legs)

            if distance <= 0.0:
                continue

            regime = COMBAT_REGIME if key in engaged else CRUISE_REGIME
            event = _build_fuel(asset, distance, time, regime, provenance)

            if event is not None:
                FM.apply_fuel_event(asset, event)
                fuel_events.append(event)

                if event.exhausted and event.distance_covered < event.distance:
                    logger.info(f"run_session: asset {key!r} runs out of fuel after "
                                f"{event.distance_covered:.0f} of {event.distance:.0f} m "
                                f"(position not updated, see FuelEvent)")

    # ── porta di uscita ───────────────────────────────────────────────────────
    latest = session_end

    for result in results:
        if result is None:
            continue

        times = [e.time for e in result.damage_events + result.ammunition_events]

        if result.t_end is not None:
            times.append(result.t_end)

        if times and max(times) > latest:
            latest = max(times)

    if latest > session_end + CS.TIME_EPS:
        logger.info(f"run_session: session {order.session_id!r} has activity up to t={latest} "
                    f"beyond its end t={session_end} (salvos in flight): outcome interval extended")

    return assemble_session_outcome(order.session_id, results, fuel_events,
                                    t_start=t0, t_end=latest)
