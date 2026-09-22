"""Scheduler dei contatti — **quando** due forze contrapposte si incontrano.

FASE 3 del motore di sessioni virtuali (strato 1 dell'architettura DES, v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` e
[[project_virtual_session_engine_design]]).

E' il pezzo che mancava a entrambe le strategie proposte dall'utente: la strategia a tick
rispondeva "quando" solo pagando 1 ms di risoluzione globale, quella probabilistica non ci
rispondeva affatto. Qui la risposta e' **analitica**: nessun tick, nessun campionamento,
solo geometria e tempo in **secondi assoluti**.

## Cosa fa e cosa NON fa

Questo modulo calcola **istanti e intervalli**. Non risolve nessun ingaggio: non decide chi
rileva davvero (Pd), chi spara per primo (latenze di reazione), chi colpisce (Pk) — e' il
lavoro dell'`Engagement_Resolver` della Fase 4, che consuma cio' che qui viene prodotto.
Il confine e' netto di proposito: *questo* strato e' deterministico e verificabile con la
sola trigonometria, quello e' stocastico e ha bisogno dell'RNG di sessione.

## I tre meccanismi

**A. Rotta contro volume di minaccia** (`threat_windows`, `route_threat_windows`).
Una rotta attraversa il cilindro di un `ThreatAA`: quando entra e quando esce. Si compone
`Cylinder.getIntersection` (geometria, gia' esistente e gia' testata) con la scansione
temporale della rotta (`route_legs`, equivalente a `Route.travelTimeToEdge` +
`Route.positionAtTime`). Nota: `ThreatAA.edgeIntersect` fa la parte geometrica ma sul
modello **interno** di `Air_Route_Manager`, stato di lavoro privato del path-finding; qui
si lavora **solo** su `DataType.Route/Edge/Waypoint`, il modello canonico confermato dalla
decisione Q1 ([[route-model-unification]]).

**B. CPA/TCPA fra mobili** (`closest_point_of_approach`, `contact_windows`).
Due asset su rotte proprie: `t* = -(Δr·Δv)/|Δv|²` da' l'istante di massimo avvicinamento.
La formula vale per moto relativo rettilineo uniforme, e una rotta e' una **spezzata**:
quindi il calcolo non si fa una volta sulla rotta intera ma su ogni sottointervallo
delimitato dai waypoint **di entrambe** le rotte (`_breakpoints`), dove le due velocita'
sono costanti per costruzione. Dentro ognuno la soluzione e' esatta, e il risultato globale
e' il minimo dei minimi locali. Per il rilevamento si risolve invece l'equazione completa
`|Δr + Δv s|² = R²` — non basta il solo CPA: serve *quando comincia* e *quando finisce* il
contatto, non solo quanto sono arrivati vicini.

**C. Potatura gerarchica a livello Block** (`block_pair_candidates`, `region_block_pairs`).
Valutare il CPA di tutte le coppie di asset e' O(N²) e con N fino a 10.000 (limite
superiore teorico dichiarato dall'utente) non e' praticabile. Prima si scartano le coppie
di `Block`/`Military` il cui **inviluppo di movimento** nella finestra considerata non puo'
in nessun caso produrre un contatto: due blocchi piu' distanti di
`(v_max_A + v_max_B) * orizzonte + portata_A + portata_B` non si incontrano, punto. Il test
e' un confronto fra due numeri per coppia di blocchi, e i blocchi sono ordini di grandezza
meno numerosi degli asset.

## Convenzioni rispettate

- **Tempo in secondi assoluti.** Ogni rotta ha il proprio istante di partenza `t0`: due
  asset che partono in momenti diversi sono la norma, non l'eccezione, e il contatto va
  cercato solo nella sovrapposizione dei rispettivi intervalli di validita'.
- **Nessuna sorgente di casualita'.** Lo strato e' puramente geometrico; se un giorno ne
  servisse una, va passata dal chiamante come il `draw` di `Logic/Damage_Model.py`, mai
  generata qui dentro.
- **Ordinamento deterministico dei risultati.** L'ordine di risoluzione degli eventi fa
  parte del contratto di riproducibilita' (decisione dell'utente n. 2): le liste restituite
  sono sempre ordinate per tempo e, a parita' di tempo, per identificativo di dominio.
- **Mai eccezioni per dati mancanti** (asset senza rotta, senza `detection_range`, rotta con
  velocita' indefinita): `None` o lista vuota, piu' un log. Le eccezioni restano per gli
  argomenti fuori dominio.
- **Import locali ai metodi** per i moduli con cicli d'import noti.
"""

from dataclasses import dataclass
from math import sqrt
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from sympy import Point3D, Segment3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import DEFAULT_DETECTION_RANGE_TYPE
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Contact_Scheduler').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Tolleranza geometrica [m] passata a Cylinder.getIntersection: sotto questa lunghezza un
# segmento e' indistinguibile da un punto. Stesso valore di
# Air_Route_Manager.TOLERANCE_FOR_INTERSECTION_CALCULUS, ma ridichiarato e non importato:
# questo modulo non deve dipendere dal pianificatore di rotta aereo (v. decisione Q1).
DEFAULT_INTERSECTION_TOLERANCE = 0.1

# Due istanti piu' vicini di questo sono lo stesso istante. Serve a due cose: non generare
# sottointervalli di durata nulla fra waypoint coincidenti, e unire finestre contigue
# prodotte da archi consecutivi (una rotta che entra in un volume sull'arco i ed esce
# sull'arco i+2 e' UNA finestra di minaccia, non tre).
TIME_EPS = 1e-9

# Sotto questa soglia |Δv|² e' considerato nullo: i due mobili sono fermi, o si muovono
# paralleli alla stessa velocita'. E' il caso degenere della formula del TCPA, dove il
# denominatore si annulla: la distanza e' costante e l'istante di massimo avvicinamento non
# e' definito (vale tutto l'intervallo). Si restituisce l'estremo iniziale.
VELOCITY_EPS = 1e-12

# Dimensione del bersaglio -> modo di rilevamento dei sensori (v. Mobile.DETECTION_MODES).
# Il modo dice in quale dominio si trova il BERSAGLIO, non l'osservatore: un radar terrestre
# ha portate diverse contro un carro e contro un aereo. La mappa e' sul nome della classe,
# come Context.classify_asset_dimension, per non importare i tre registry qui.
DETECTION_MODE_BY_CLASS = {
    'Vehicle': 'ground',
    'Structure': 'ground',
    'Ship': 'sea',
    'Aircraft': 'air',
}


# ── TIPI DI SCAMBIO ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Leg:
    """Tratto di rotta a velocita' costante, in tempo assoluto.

    E' la forma su cui lavora tutta la matematica di questo modulo: la spezzata di una
    `DataType.Route` diventa una sequenza di tratti, ognuno con i propri istanti di inizio e
    fine e i propri estremi geometrici. Le posizioni sono terne di float (non `Point3D`)
    perche' dentro ai cicli si fanno migliaia di prodotti scalari e l'aritmetica esatta di
    sympy li renderebbe inutilmente costosi; i `Point3D` ricompaiono sui risultati.

    Un tratto **statico** (asset fermo: un sito SAM, un blocco in posizione) e' un Leg con
    `p_start == p_end` e durata pari alla finestra considerata: il resto del modulo non ha
    bisogno di sapere che e' fermo.
    """
    t_start: float
    t_end: float
    p_start: Tuple[float, float, float]
    p_end: Tuple[float, float, float]
    edge_name: Optional[str] = None

    @property
    def duration(self) -> float:
        return self.t_end - self.t_start


@dataclass(frozen=True)
class ThreatWindow:
    """Intervallo in cui una rotta si trova dentro un volume di minaccia.

    Prodotto del meccanismo A. Il consumatore di Fase 4 legge `t_entry`/`t_exit` per sapere
    quando il difensore puo' iniziare la propria sequenza di reazione (e la confronta con
    `ThreatAA.min_detection_time` + `min_fire_time`, che dicono quanto tempo *serve*), e
    `danger_level` per pesare l'esito.

    Attributes:
        t_entry/t_exit: secondi assoluti di ingresso e uscita dal volume.
        entry_point/exit_point: posizioni corrispondenti sulla rotta.
        threat_id: identificativo di dominio della minaccia, None se il chiamante non ne ha
                   fornito uno (`ThreatAA` non porta un id proprio).
        danger_level: il `danger_level` in [0, 1] della minaccia, se disponibile.
        route_name: nome della rotta attraversata.
        edge_names: archi della rotta toccati dalla finestra, nell'ordine di percorrenza.
    """
    t_entry: float
    t_exit: float
    entry_point: Point3D
    exit_point: Point3D
    threat_id: Optional[str] = None
    danger_level: Optional[float] = None
    route_name: Optional[str] = None
    edge_names: Tuple[Optional[str], ...] = ()

    @property
    def duration(self) -> float:
        """Tempo di esposizione alla minaccia [s]."""
        return self.t_exit - self.t_entry


@dataclass(frozen=True)
class CPA:
    """Punto di massimo avvicinamento fra due mobili (Closest Point of Approach).

    `time` e' il TCPA in secondi assoluti, `distance` la distanza minima in metri.
    `degenerate` e' True quando i due mobili sono fermi o si muovono paralleli alla stessa
    velocita': in quel caso la distanza e' costante e `time` e' convenzionalmente l'inizio
    dell'intervallo di sovrapposizione, non un vero minimo.
    """
    time: float
    distance: float
    point_a: Point3D
    point_b: Point3D
    degenerate: bool = False


@dataclass(frozen=True)
class ContactWindow:
    """Intervallo in cui due asset sono nel raggio di rilevamento (almeno unidirezionale).

    E' l'unita' che l'`Engagement_Resolver` della Fase 4 consuma: "questi due asset sono in
    reciproco raggio in [t_start, t_end]". Una coppia puo' produrre **piu'** finestre
    disgiunte (rotte che si incrociano piu' volte), quindi l'API ne restituisce una lista.

    La distinzione fra rilevamento unidirezionale e bidirezionale e' esplicita perche' e'
    esattamente cio' che decide **chi spara per primo**, la domanda a cui i modelli a
    rapporto di forze non sanno rispondere:

    - `[t_start, t_end]` usa la portata **maggiore** delle due: e' il primo contatto in
      assoluto, e chi lo ottiene e' `first_detector`;
    - `[t_mutual_start, t_mutual_end]` usa la portata **minore**: da quel momento entrambi
      si vedono. E' None quando uno dei due non vede mai l'altro (portata piu' corta della
      distanza minima, o sensore assente).

    Attributes:
        asset_a_id/asset_b_id: identificativi di dominio (mai id del simulatore).
        t_start/t_end: secondi assoluti della finestra di contatto.
        t_cpa/distance_cpa: massimo avvicinamento **dentro questa finestra**.
        range_a/range_b: portate usate [m], None se l'asset non dichiara sensori utili.
        first_detector: 'a', 'b' o 'both' (portate uguali, o una sola disponibile).
    """
    asset_a_id: Optional[str]
    asset_b_id: Optional[str]
    t_start: float
    t_end: float
    t_cpa: float
    distance_cpa: float
    range_a: Optional[float] = None
    range_b: Optional[float] = None
    t_mutual_start: Optional[float] = None
    t_mutual_end: Optional[float] = None
    first_detector: str = 'both'

    @property
    def duration(self) -> float:
        return self.t_end - self.t_start

    @property
    def is_mutual(self) -> bool:
        """True se esiste un intervallo in cui entrambi rilevano l'altro."""
        return self.t_mutual_start is not None


# ── ALGEBRA VETTORIALE MINIMA (terne di float) ────────────────────────────────

def _to_xyz(point) -> Tuple[float, float, float]:
    """Point3D (o qualunque oggetto con x/y/z) -> terna di float."""
    return (float(point.x), float(point.y), float(point.z))


def _to_point(xyz: Tuple[float, float, float]) -> Point3D:
    return Point3D(xyz[0], xyz[1], xyz[2])


def _sub(u, v) -> Tuple[float, float, float]:
    return (u[0] - v[0], u[1] - v[1], u[2] - v[2])


def _dot(u, v) -> float:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def _lerp(p0, p1, f: float) -> Tuple[float, float, float]:
    return (p0[0] + (p1[0] - p0[0]) * f,
            p0[1] + (p1[1] - p0[1]) * f,
            p0[2] + (p1[2] - p0[2]) * f)


# ── A-0. SCANSIONE TEMPORALE DI UNA ROTTA ─────────────────────────────────────

def route_legs(route, t0: float = 0.0, speed: Optional[float] = None,
               horizon: Optional[float] = None) -> List[Leg]:
    """Scompone una `DataType.Route` nei suoi tratti, in tempo assoluto.

    E' la porta d'ingresso di tutto il modulo: da qui in poi non si parla piu' di rotte ma
    di `Leg`. L'accumulo dei tempi e' identico a quello di `Route.travelTimeToEdge` e
    `Route.positionAtTime` — stessa assunzione sull'ordine di percorrenza (l'ordine di
    inserimento di `route.edges`) e stessa chiamata `Edge.calcTravelTime(speed)` — ma qui
    serve l'elenco completo in una passata sola, non un tempo alla volta: cercare i contatti
    significa attraversare la rotta molte volte, e ricalcolare il prefisso a ogni arco
    sarebbe quadratico. L'equivalenza con `travelTimeToEdge` e' verificata dai test.

    Args:
        route: una `DataType.Route` (unico modello ammesso, decisione Q1).
        t0: istante assoluto [s] di partenza dell'asset lungo questa rotta.
        speed: velocita' [m/s] che sovrascrive quella dei singoli archi, stessa semantica di
               `Route.travelTime`.
        horizon: se dato, i tratti sono ritagliati a `[t0, t0 + horizon]`.

    Returns:
        Lista di `Leg` in ordine di percorrenza; **lista vuota** se la rotta e' vuota, priva
        di archi o con un arco a velocita' indefinita (`calcTravelTime` infinito) — nel qual
        caso la posizione non e' calcolabile e inventarne una sarebbe peggio, esattamente
        come fa `Route.positionAtTime` restituendo None.

    Raises:
        ValueError: solo per `horizon` negativo (argomento fuori dominio).
    """
    if horizon is not None and horizon < 0:
        raise ValueError(f"horizon must be non-negative, got {horizon!r}")

    edges = getattr(route, 'edges', None)

    if not edges:
        logger.debug("route_legs: route has no edges, no legs produced")
        return []

    legs: List[Leg] = []
    elapsed = float(t0)

    for edge in edges.values():
        travel_time = edge.calcTravelTime(speed)

        if travel_time == float('inf') or travel_time != travel_time:
            logger.warning(f"route_legs: undefined speed on edge {getattr(edge, 'name', None)!r}, "
                           f"route not schedulable")
            return []

        travel_time = float(travel_time)
        legs.append(Leg(t_start=elapsed,
                        t_end=elapsed + travel_time,
                        p_start=_to_xyz(edge.wpA.point),
                        p_end=_to_xyz(edge.wpB.point),
                        edge_name=getattr(edge, 'name', None)))
        elapsed += travel_time

    if horizon is not None:
        legs = clamp_legs(legs, float(t0), float(t0) + float(horizon))

    return legs


def static_legs(position, t_start: float, t_end: float) -> List[Leg]:
    """Tratto unico di un asset fermo: un sito SAM, un deposito, un blocco in posizione.

    Serve perche' il caso piu' frequente di contatto non e' rotta contro rotta ma **rotta
    contro bersaglio fermo**, e senza questo il chiamante dovrebbe fabbricare una rotta
    fittizia solo per interrogare lo scheduler.

    Returns:
        Lista con un solo `Leg`, o lista vuota se `position` e' None (asset senza posizione:
        dato mancante, non errore).
    """
    if position is None:
        logger.debug("static_legs: position is None, no leg produced")
        return []

    if t_end < t_start:
        raise ValueError(f"t_end ({t_end!r}) must not precede t_start ({t_start!r})")

    xyz = _to_xyz(position)

    return [Leg(t_start=float(t_start), t_end=float(t_end), p_start=xyz, p_end=xyz,
                edge_name=None)]


def clamp_legs(legs: Sequence[Leg], lo: float, hi: float) -> List[Leg]:
    """Ritaglia i tratti all'intervallo `[lo, hi]`, interpolando gli estremi tagliati."""
    clamped: List[Leg] = []

    for leg in legs:
        if leg.t_end < lo - TIME_EPS or leg.t_start > hi + TIME_EPS:
            continue

        new_start = max(leg.t_start, lo)
        new_end = min(leg.t_end, hi)

        if new_end < new_start:
            continue

        duration = leg.duration
        f0 = 0.0 if duration <= TIME_EPS else (new_start - leg.t_start) / duration
        f1 = 1.0 if duration <= TIME_EPS else (new_end - leg.t_start) / duration

        clamped.append(Leg(t_start=new_start, t_end=new_end,
                           p_start=_lerp(leg.p_start, leg.p_end, f0),
                           p_end=_lerp(leg.p_start, leg.p_end, f1),
                           edge_name=leg.edge_name))

    return clamped


def legs_span(legs: Sequence[Leg]) -> Optional[Tuple[float, float]]:
    """Intervallo di validita' `[primo istante, ultimo istante]`, None se non ci sono tratti.

    E' l'intervallo fuori dal quale l'asset **non esiste** per lo scheduler: non c'e' prima
    di partire e non c'e' dopo essere arrivato. Ogni calcolo di contatto e' clampato alla
    sovrapposizione di due span.
    """
    if not legs:
        return None

    return (legs[0].t_start, legs[-1].t_end)


def position_on_legs(legs: Sequence[Leg], t: float) -> Optional[Tuple[float, float, float]]:
    """Posizione all'istante assoluto `t`, terna di float. None se non ci sono tratti.

    Fuori dallo span si satura sugli estremi (stessa scelta di `Route.positionAtTime`, che
    oltre la durata totale restituisce l'ultimo waypoint).
    """
    if not legs:
        return None

    if t <= legs[0].t_start:
        return legs[0].p_start

    if t >= legs[-1].t_end:
        return legs[-1].p_end

    for leg in legs:
        if leg.t_start <= t <= leg.t_end:
            duration = leg.duration
            f = 0.0 if duration <= TIME_EPS else (t - leg.t_start) / duration
            return _lerp(leg.p_start, leg.p_end, f)

    # Buco fra due tratti (non dovrebbe accadere: sono contigui per costruzione).
    logger.debug(f"position_on_legs: t={t!r} falls in a gap between legs")
    return legs[-1].p_end


# ── A. ROTTA CONTRO VOLUME DI MINACCIA ────────────────────────────────────────

def _cylinder_of(threat):
    """Il `Cylinder` di una minaccia: accetta un `ThreatAA` o direttamente un `Cylinder`."""
    return getattr(threat, 'cylinder', threat)


def _fraction_along(p_start, p_end, point) -> float:
    """Frazione in [0, 1] del punto proiettato sul tratto `p_start -> p_end`."""
    direction = _sub(p_end, p_start)
    length2 = _dot(direction, direction)

    if length2 <= VELOCITY_EPS:
        return 0.0

    f = _dot(_sub(point, p_start), direction) / length2

    return min(max(f, 0.0), 1.0)


def threat_windows(route, threat, t0: float = 0.0, speed: Optional[float] = None,
                   horizon: Optional[float] = None,
                   threat_id: Optional[str] = None,
                   tolerance: float = DEFAULT_INTERSECTION_TOLERANCE) -> List[ThreatWindow]:
    """Intervalli di tempo assoluto in cui `route` attraversa il volume di `threat`.

    Meccanismo A. La geometria non e' riscritta: per ogni arco si chiama
    `Cylinder.getIntersection(Segment3D, tolerance)`, gia' esistente e coperta da test, e si
    converte il risultato in frazioni di arco e quindi in istanti. I casi che
    `getIntersection` non distingue da sola sono chiusi qui:

    - **arco interamente dentro** il cilindro (nessun attraversamento di superficie):
      `getIntersection` restituisce `(False, None)`, indistinguibile da "nessuna
      intersezione". Si disambigua con `Cylinder.innerPoint` sui due estremi.
    - **arco con un estremo dentro**: `getIntersection` restituisce il segmento
      intersezione-estremo; l'estremo interno da' comunque la frazione 0 o 1.
    - **tangenza** (un solo punto, nessun estremo interno): `getIntersection` **solleva**
      `ValueError` ("Intersezione anomala"). E' un contatto di misura nulla, non un errore
      di programmazione: si registra a debug e si scarta l'arco.

    Le finestre di archi consecutivi vengono **fuse**: una rotta che entra nel volume
    sull'arco i ed esce sull'arco i+2 produce una sola `ThreatWindow`, che e' cio' che
    significa fisicamente.

    Returns:
        Lista di `ThreatWindow` ordinate per `t_entry`; vuota se la rotta non entra mai nel
        volume, se la rotta non e' schedulabile o se la minaccia non espone un cilindro.
    """
    cylinder = _cylinder_of(threat)

    if cylinder is None or not hasattr(cylinder, 'getIntersection'):
        logger.warning(f"threat_windows: threat {threat_id!r} has no usable cylinder")
        return []

    # I tratti si calcolano SENZA horizon: cosi' restano in corrispondenza 1:1 con gli archi
    # e l'appaiamento e' posizionale, senza dipendere dai nomi (che possono mancare o
    # ripetersi). Il ritaglio all'orizzonte si applica alla fine, sulle finestre.
    legs = route_legs(route, t0=t0, speed=speed)

    if not legs:
        return []

    raw: List[Tuple[float, float, Optional[str]]] = []

    for edge, leg in zip(route.edges.values(), legs):
        window = _edge_threat_fractions(cylinder, edge, tolerance)

        if window is None:
            continue

        f_in, f_out = window
        duration = leg.duration
        raw.append((leg.t_start + f_in * duration,
                    leg.t_start + f_out * duration,
                    leg.edge_name))

    if not raw:
        return []

    merged = _merge_threat_intervals(raw)

    if horizon is not None:
        limit = float(t0) + float(horizon)
        merged = [(max(entry, float(t0)), min(exit_, limit), names)
                  for entry, exit_, names in merged
                  if exit_ >= float(t0) - TIME_EPS and entry <= limit + TIME_EPS]
    route_name = getattr(route, 'name', None)
    danger = getattr(threat, 'danger_level', None)
    danger = float(danger) if isinstance(danger, (int, float)) else None

    windows = []

    for t_entry, t_exit, names in merged:
        entry = position_on_legs(legs, t_entry)
        exit_ = position_on_legs(legs, t_exit)
        windows.append(ThreatWindow(t_entry=t_entry,
                                    t_exit=t_exit,
                                    entry_point=_to_point(entry),
                                    exit_point=_to_point(exit_),
                                    threat_id=threat_id,
                                    danger_level=danger,
                                    route_name=route_name,
                                    edge_names=tuple(names)))

    return windows


def _edge_threat_fractions(cylinder, edge, tolerance: float) -> Optional[Tuple[float, float]]:
    """Frazioni di ingresso/uscita di un arco nel cilindro, None se l'arco non lo tocca."""
    point_a = edge.wpA.point
    point_b = edge.wpB.point
    xyz_a = _to_xyz(point_a)
    xyz_b = _to_xyz(point_b)

    inside_a = bool(cylinder.innerPoint(point_a))
    inside_b = bool(cylinder.innerPoint(point_b))

    fractions: List[float] = []

    try:
        _, segment = cylinder.getIntersection(Segment3D(point_a, point_b), tolerance)
    except ValueError as exc:
        # Segment3D degenere (estremi coincidenti) oppure tangenza: "Intersezione anomala:
        # un solo punto trovato ma nessun estremo interno". Dato legittimo, non errore.
        logger.debug(f"_edge_threat_fractions: edge {getattr(edge, 'name', None)!r} discarded ({exc})")
        segment = None

    if segment is not None:
        for point in segment.points:
            fractions.append(_fraction_along(xyz_a, xyz_b, _to_xyz(point)))

    if inside_a:
        fractions.append(0.0)

    if inside_b:
        fractions.append(1.0)

    if not fractions:
        return None

    f_in = min(fractions)
    f_out = max(fractions)

    if f_out - f_in <= 0.0 and not (inside_a or inside_b):
        # Contatto di misura nulla (sfioramento): non e' un'esposizione.
        return None

    return (f_in, f_out)


def _merge_threat_intervals(raw: Sequence[Tuple[float, float, Optional[str]]]
                            ) -> List[Tuple[float, float, List[Optional[str]]]]:
    """Fonde gli intervalli contigui (fine di uno == inizio del successivo, entro TIME_EPS)."""
    ordered = sorted(raw, key=lambda item: (item[0], item[1]))
    merged: List[Tuple[float, float, List[Optional[str]]]] = []

    for t_entry, t_exit, name in ordered:
        if merged and t_entry <= merged[-1][1] + TIME_EPS:
            previous = merged[-1]
            names = previous[2]

            if name not in names:
                names.append(name)

            merged[-1] = (previous[0], max(previous[1], t_exit), names)
        else:
            merged.append((t_entry, t_exit, [name]))

    return merged


def route_threat_windows(route, threats, t0: float = 0.0, speed: Optional[float] = None,
                         horizon: Optional[float] = None,
                         tolerance: float = DEFAULT_INTERSECTION_TOLERANCE) -> List[ThreatWindow]:
    """`threat_windows` su piu' minacce in una volta.

    Args:
        threats: mappa `{threat_id: threat}` — e allora l'id finisce nelle finestre — oppure
                 un semplice iterabile di minacce, come quello che restituisce
                 `Military.air_defense_threats()`, nel qual caso l'id e' preso da
                 `threat.name` se esiste, altrimenti None.

    Returns:
        Tutte le finestre, ordinate per `(t_entry, threat_id)` — deterministico anche a
        parita' di istante, perche' l'ordine fa parte del contratto di riproducibilita'.
    """
    if isinstance(threats, Mapping):
        items = list(threats.items())
    else:
        items = [(getattr(threat, 'name', None), threat) for threat in (threats or [])]

    windows: List[ThreatWindow] = []

    for threat_id, threat in items:
        windows.extend(threat_windows(route, threat, t0=t0, speed=speed, horizon=horizon,
                                      threat_id=threat_id, tolerance=tolerance))

    windows.sort(key=lambda w: (w.t_entry, str(w.threat_id)))

    return windows


# ── B. CPA/TCPA FRA MOBILI ────────────────────────────────────────────────────

def _overlap(legs_a: Sequence[Leg], legs_b: Sequence[Leg]) -> Optional[Tuple[float, float]]:
    """Intervallo in cui entrambi gli asset esistono, None se non si sovrappongono."""
    span_a = legs_span(legs_a)
    span_b = legs_span(legs_b)

    if span_a is None or span_b is None:
        return None

    lo = max(span_a[0], span_b[0])
    hi = min(span_a[1], span_b[1])

    if hi < lo - TIME_EPS:
        return None

    return (lo, max(hi, lo))


def _breakpoints(legs_a: Sequence[Leg], legs_b: Sequence[Leg],
                 lo: float, hi: float) -> List[float]:
    """Istanti in cui almeno uno dei due cambia velocita', piu' gli estremi.

    Fra due breakpoint consecutivi entrambi i mobili si muovono di moto rettilineo uniforme:
    e' l'unica condizione sotto cui la formula del TCPA e l'equazione `|Δr + Δv s|² = R²`
    sono esatte. Senza questa suddivisione, applicare il CPA "alla rotta intera" darebbe un
    risultato semplicemente sbagliato su qualunque rotta con piu' di un arco.
    """
    times = {lo, hi}

    for legs in (legs_a, legs_b):
        for leg in legs:
            for t in (leg.t_start, leg.t_end):
                if lo - TIME_EPS <= t <= hi + TIME_EPS:
                    times.add(min(max(t, lo), hi))

    ordered = sorted(times)
    pruned = [ordered[0]]

    for t in ordered[1:]:
        if t - pruned[-1] > TIME_EPS:
            pruned.append(t)

    return pruned


def _relative_motion(legs_a, legs_b, u: float, v: float):
    """(Δr, Δv, durata) del moto relativo sul sottointervallo `[u, v]`.

    Δr = posizione di B meno posizione di A all'istante `u`; Δv = velocita' relativa,
    costante sul sottointervallo per costruzione (v. `_breakpoints`).
    """
    duration = v - u
    pa_u = position_on_legs(legs_a, u)
    pb_u = position_on_legs(legs_b, u)

    if duration <= TIME_EPS:
        return _sub(pb_u, pa_u), (0.0, 0.0, 0.0), 0.0

    pa_v = position_on_legs(legs_a, v)
    pb_v = position_on_legs(legs_b, v)

    va = tuple(component / duration for component in _sub(pa_v, pa_u))
    vb = tuple(component / duration for component in _sub(pb_v, pb_u))

    return _sub(pb_u, pa_u), _sub(vb, va), duration


def closest_point_of_approach(legs_a: Sequence[Leg], legs_b: Sequence[Leg]) -> Optional[CPA]:
    """Istante e distanza di massimo avvicinamento fra due mobili.

    Meccanismo B. Su ogni sottointervallo a velocita' relativa costante si applica

        t* = -(Δr · Δv) / |Δv|²

    e si **clampa** il risultato al sottointervallo: un minimo che cade fuori significa che
    su quel tratto la distanza e' monotona e il minimo sta su un estremo. Il caso degenere
    `|Δv|² ~ 0` (fermi, o paralleli alla stessa velocita') non viene diviso per zero: la
    distanza e' costante e si prende l'estremo iniziale.

    Il risultato e' clampato all'intervallo di validita' di **entrambe** le rotte: nessuno
    dei due asset esiste prima della propria partenza o dopo il proprio arrivo.

    Args:
        legs_a/legs_b: i tratti dei due asset (v. `route_legs`/`static_legs`).

    Returns:
        `CPA`, oppure None se uno dei due non ha tratti o se i loro intervalli di validita'
        non si sovrappongono (i due non esistono mai contemporaneamente).
    """
    overlap = _overlap(legs_a, legs_b)

    if overlap is None:
        return None

    lo, hi = overlap
    breakpoints = _breakpoints(legs_a, legs_b, lo, hi)

    best_time = None
    best_distance2 = None
    best_degenerate = True

    if len(breakpoints) == 1:
        # Sovrapposizione istantanea: i due esistono insieme per un solo istante.
        t = breakpoints[0]
        delta = _sub(position_on_legs(legs_b, t), position_on_legs(legs_a, t))
        best_time, best_distance2, best_degenerate = t, _dot(delta, delta), True

    for u, v in zip(breakpoints, breakpoints[1:]):
        dr, dv, duration = _relative_motion(legs_a, legs_b, u, v)
        speed2 = _dot(dv, dv)

        if speed2 <= VELOCITY_EPS:
            s = 0.0
            degenerate = True
        else:
            s = -_dot(dr, dv) / speed2
            s = min(max(s, 0.0), duration)
            degenerate = False

        at_s = (dr[0] + dv[0] * s, dr[1] + dv[1] * s, dr[2] + dv[2] * s)
        distance2 = _dot(at_s, at_s)

        if best_distance2 is None or distance2 < best_distance2:
            best_time = u + s
            best_distance2 = distance2
            best_degenerate = degenerate

    if best_time is None:
        return None

    return CPA(time=best_time,
               distance=sqrt(max(best_distance2, 0.0)),
               point_a=_to_point(position_on_legs(legs_a, best_time)),
               point_b=_to_point(position_on_legs(legs_b, best_time)),
               degenerate=best_degenerate)


def range_intervals(legs_a: Sequence[Leg], legs_b: Sequence[Leg],
                    radius: float) -> List[Tuple[float, float]]:
    """Intervalli in cui la distanza fra i due mobili e' `<= radius`.

    Il CPA da solo non basta allo scheduler: dice *quanto* si sono avvicinati, non *da
    quando a quando* sono stati a tiro. Qui si risolve l'equazione completa

        |Δr + Δv s|² = R²

    su ogni sottointervallo a velocita' relativa costante, e si fondono gli intervalli
    contigui. Il risultato puo' contenere piu' intervalli disgiunti: due rotte che si
    incrociano piu' volte entrano e escono dal raggio piu' volte.

    Raises:
        ValueError: `radius` negativo (argomento fuori dominio).
    """
    if radius < 0:
        raise ValueError(f"radius must be non-negative, got {radius!r}")

    overlap = _overlap(legs_a, legs_b)

    if overlap is None:
        return []

    lo, hi = overlap
    breakpoints = _breakpoints(legs_a, legs_b, lo, hi)
    radius2 = radius * radius
    found: List[Tuple[float, float]] = []

    if len(breakpoints) == 1:
        t = breakpoints[0]
        delta = _sub(position_on_legs(legs_b, t), position_on_legs(legs_a, t))

        return [(t, t)] if _dot(delta, delta) <= radius2 else []

    for u, v in zip(breakpoints, breakpoints[1:]):
        dr, dv, duration = _relative_motion(legs_a, legs_b, u, v)
        a = _dot(dv, dv)
        b = 2.0 * _dot(dr, dv)
        c = _dot(dr, dr) - radius2

        if a <= VELOCITY_EPS:
            # Distanza costante sul sottointervallo: dentro o fuori per tutta la durata.
            if c <= 0.0:
                found.append((u, v))
            continue

        discriminant = b * b - 4.0 * a * c

        if discriminant < 0.0:
            continue

        root = sqrt(discriminant)
        s1 = max((-b - root) / (2.0 * a), 0.0)
        s2 = min((-b + root) / (2.0 * a), duration)

        if s2 < s1:
            continue

        found.append((u + s1, u + s2))

    return _merge_intervals(found)


def _merge_intervals(intervals: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Fonde gli intervalli che si toccano o si sovrappongono (entro TIME_EPS)."""
    if not intervals:
        return []

    ordered = sorted(intervals)
    merged = [ordered[0]]

    for start, end in ordered[1:]:
        if start <= merged[-1][1] + TIME_EPS:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    return merged


# ── B-bis. DAL RAGGIO DI RILEVAMENTO ALLE FINESTRE DI CONTATTO ────────────────

def detection_mode_for(asset) -> Optional[str]:
    """Modo di rilevamento con cui un **bersaglio** di questa classe va interrogato.

    `Mobile.detection_range(mode, ...)` vuole sapere in quale dominio si trova il bersaglio
    ('ground'/'air'/'sea'), perche' lo stesso radar ha portate diverse contro un carro e
    contro un aereo. La classificazione e' sul nome della classe, come fa
    `Context.classify_asset_dimension`, per non importare i registry qui.

    Returns:
        'ground', 'air', 'sea', oppure None se la classe non e' riconosciuta (dato mancante,
        non errore: il chiamante decide la propria politica).
    """
    return DETECTION_MODE_BY_CLASS.get(asset.__class__.__name__)


def mutual_detection_ranges(asset_a, asset_b,
                            range_type: str = DEFAULT_DETECTION_RANGE_TYPE
                            ) -> Tuple[Optional[float], Optional[float]]:
    """Portate [m] con cui A vede B e B vede A.

    Ognuno e' interrogato **sul dominio dell'altro**: A chiede il proprio raggio contro
    bersagli del modo di B, e viceversa. Le due portate sono di norma diverse, ed e' proprio
    questa asimmetria a decidere chi vede per primo.

    Returns:
        `(range_a, range_b)`; un elemento e' None quando l'asset non espone
        `detection_range`, quando la classe dell'altro non e' classificabile, o quando il
        modello non dichiara sensori utili su quel modo. Mai un'eccezione: e' un dato
        mancante (stessa politica di `Mobile.detection_range`).
    """
    def _range(observer, target) -> Optional[float]:
        mode = detection_mode_for(target)

        if mode is None:
            logger.debug(f"mutual_detection_ranges: target class "
                         f"{target.__class__.__name__!r} has no detection mode")
            return None

        if not hasattr(observer, 'detection_range'):
            logger.debug(f"mutual_detection_ranges: observer class "
                         f"{observer.__class__.__name__!r} has no detection_range()")
            return None

        try:
            value = observer.detection_range(mode, range_type=range_type)
        except ValueError:
            # mode/range_type fuori dominio: lo scheduler non li inventa, quindi qui puo'
            # succedere solo se il chiamante ha passato un range_type sbagliato. Rilancia.
            raise

        return float(value) if isinstance(value, (int, float)) else None

    return (_range(asset_a, asset_b), _range(asset_b, asset_a))


def contact_windows(asset_a, legs_a: Sequence[Leg], asset_b, legs_b: Sequence[Leg],
                    range_a: Optional[float] = None, range_b: Optional[float] = None,
                    range_type: str = DEFAULT_DETECTION_RANGE_TYPE) -> List[ContactWindow]:
    """Finestre in cui due asset sono a portata di rilevamento l'uno dell'altro.

    E' l'uscita principale del modulo verso la Fase 4. Per ogni finestra si dice quando
    comincia il contatto (portata maggiore delle due), chi lo ottiene per primo, se e quando
    diventa bidirezionale (portata minore) e quanto si arriva vicini.

    Args:
        asset_a/asset_b: i due asset, interrogati per le portate se non fornite.
        legs_a/legs_b: i rispettivi tratti (`route_legs` o `static_legs`).
        range_a/range_b: portate [m] imposte dal chiamante, che scavalcano
                         `detection_range`. Servono a due cose: ai test, e alla Fase 4, dove
                         le degradazioni (disturbo, meteo, silenzio radar) si applicheranno
                         **fuori** da questo strato, che resta puramente geometrico.
        range_type: 'acquisition_range' (default), 'tracking_range' o 'engagement_range'.
                    Con 'engagement_range' questa stessa funzione risponde alla domanda
                    "quando sono a tiro" invece che "quando si vedono".

    Returns:
        Lista di `ContactWindow` ordinate per `t_start`; vuota se non c'e' sovrapposizione
        temporale, se nessuno dei due dichiara una portata utilizzabile, o se non si
        avvicinano mai abbastanza.
    """
    if not legs_a or not legs_b:
        logger.debug("contact_windows: one of the two assets has no legs")
        return []

    if range_a is None or range_b is None:
        derived_a, derived_b = mutual_detection_ranges(asset_a, asset_b, range_type=range_type)
        range_a = derived_a if range_a is None else range_a
        range_b = derived_b if range_b is None else range_b

    available = [value for value in (range_a, range_b) if value is not None and value > 0.0]

    if not available:
        logger.debug("contact_windows: neither asset declares a usable detection range")
        return []

    outer = max(available)
    inner = min(available) if len(available) == 2 else None

    outer_intervals = range_intervals(legs_a, legs_b, outer)

    if not outer_intervals:
        return []

    mutual_intervals = range_intervals(legs_a, legs_b, inner) if inner is not None else []

    asset_a_id = _asset_id(asset_a)
    asset_b_id = _asset_id(asset_b)
    detector = _first_detector(range_a, range_b)

    windows: List[ContactWindow] = []

    for start, end in outer_intervals:
        cpa = closest_point_of_approach(clamp_legs(legs_a, start, end),
                                        clamp_legs(legs_b, start, end))
        mutual = _first_contained(mutual_intervals, start, end)

        windows.append(ContactWindow(asset_a_id=asset_a_id,
                                     asset_b_id=asset_b_id,
                                     t_start=start,
                                     t_end=end,
                                     t_cpa=cpa.time if cpa else start,
                                     distance_cpa=cpa.distance if cpa else float('inf'),
                                     range_a=range_a,
                                     range_b=range_b,
                                     t_mutual_start=mutual[0] if mutual else None,
                                     t_mutual_end=mutual[1] if mutual else None,
                                     first_detector=detector))

    return windows


def _first_detector(range_a: Optional[float], range_b: Optional[float]) -> str:
    """Chi ottiene il primo contatto: chi ha la portata piu' lunga."""
    a = range_a if range_a is not None else 0.0
    b = range_b if range_b is not None else 0.0

    if a > b:
        return 'a'

    if b > a:
        return 'b'

    return 'both'


def _first_contained(intervals: Sequence[Tuple[float, float]],
                     start: float, end: float) -> Optional[Tuple[float, float]]:
    """Il primo intervallo che cade dentro `[start, end]`, ritagliato ad esso."""
    for lo, hi in intervals:
        if hi < start - TIME_EPS or lo > end + TIME_EPS:
            continue

        return (max(lo, start), min(hi, end))

    return None


def _asset_id(asset) -> Optional[str]:
    """Identificativo di dominio di un asset o di un blocco. Mai un id del simulatore."""
    for attribute in ('id', 'name'):
        value = getattr(asset, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


# ── C. POTATURA GERARCHICA A LIVELLO BLOCK ────────────────────────────────────

def block_max_speed(block) -> float:
    """Velocita' massima [m/s] fra gli asset operativi del blocco, 0.0 se nessuno si muove.

    Legge il profilo canonico `Mobile.speed` (v. SPEED_SCHEMA): per i veicoli considera
    anche il ramo `off_road`, perche' il movimento tattico non avviene su strada e usare il
    solo regime stradale sottostimerebbe l'inviluppo — e una potatura che sottostima
    l'inviluppo **scarta coppie che si sarebbero incontrate**, che e' l'unico errore
    inaccettabile per un filtro conservativo.
    """
    assets = getattr(block, 'assets', None)

    if not assets:
        return 0.0

    best = 0.0

    for asset in assets.values():
        if hasattr(asset, 'is_operative') and not asset.is_operative():
            continue

        profile = getattr(asset, 'speed', None)

        if not isinstance(profile, dict):
            continue

        for candidate in (profile, profile.get('off_road')):
            if not isinstance(candidate, dict):
                continue

            for key in ('max', 'nominal'):
                value = candidate.get(key)

                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    best = max(best, float(value))

    return best


def block_reach(block, mode: Optional[str] = None) -> float:
    """Raggio d'azione [m] del blocco: la piu' lunga fra portata di fuoco e di rilevamento.

    E' il termine che, sommato all'inviluppo di movimento, definisce la distanza sotto la
    quale un contatto **non si puo' escludere**. Si prende il massimo (non la mediana e non
    la somma): la potatura deve essere conservativa, e basta un singolo sensore o una
    singola arma a lunga gittata per rendere la coppia non scartabile.

    Args:
        mode: modo di rilevamento del bersaglio; None considera tutti i modi.
    """
    from Code.Dynamic_War_Manager.Source.Asset.Mobile import DETECTION_MODES

    reach = 0.0

    combat = getattr(block, 'combat_range', None)

    if callable(combat):
        stats = combat()

        if stats:
            reach = max(reach, float(stats[0]))

    detection = getattr(block, 'detection_range', None)

    if callable(detection):
        modes = (mode,) if mode is not None else DETECTION_MODES

        for target_mode in modes:
            stats = detection(target_mode)

            if stats:
                reach = max(reach, float(stats[0]))

    threats = getattr(block, 'air_defense_threats', None)

    if callable(threats):
        for threat in (threats() or []):
            cylinder = _cylinder_of(threat)
            radius = getattr(cylinder, 'radius', None)

            if isinstance(radius, (int, float)) and not isinstance(radius, bool):
                reach = max(reach, float(radius))

    return reach


def _as_block(item):
    """Accetta indifferentemente un `Block` o un `BlockItem` (che lo incapsula in `.block`)."""
    return getattr(item, 'block', item)


def block_pair_candidates(blocks_a: Iterable, blocks_b: Iterable, horizon: float,
                          margin: float = 0.0,
                          skip_same_side: bool = True) -> List[Tuple[object, object]]:
    """Coppie di blocchi per cui un contatto **non e' escludibile** nella finestra `horizon`.

    Meccanismo C: e' cio' che rende trattabile l'algoritmo. Senza, si valuterebbe il CPA di
    ogni coppia di asset, O(N²) su N fino a 10.000. Con, si fa un confronto fra due numeri
    per coppia di **blocchi** e si scende ai singoli asset solo sulle coppie superstiti.

    Il criterio e' volutamente **conservativo**: si scarta solo quando e' geometricamente
    impossibile che i due si incontrino, cioe' quando

        distanza(centroide_A, centroide_B) > (v_max_A + v_max_B) * horizon
                                             + portata_A + portata_B + margin

    Un blocco senza posizione nota **non viene mai scartato**: l'assenza di dato non e' una
    prova di lontananza (stessa logica di [[feedback_no_visibility_low_priority]] applicata
    al contrario — li' l'ignoto non alza la priorita', qui non autorizza a scartare).

    Args:
        blocks_a/blocks_b: `Block`, `Military` o `BlockItem` (v. `Region.get_blocks_by_criteria`).
        horizon: durata [s] della finestra considerata.
        margin: margine di sicurezza [m] aggiuntivo.
        skip_same_side: scarta le coppie dello stesso schieramento (di norma i contatti si
                        cercano fra forze contrapposte).

    Returns:
        Lista di coppie `(item_a, item_b)` — gli **oggetti originali** passati dal chiamante,
        non i blocchi estratti, cosi' che il chiamante conservi i propri riferimenti.

    Raises:
        ValueError: `horizon` o `margin` negativi.
    """
    if horizon < 0:
        raise ValueError(f"horizon must be non-negative, got {horizon!r}")

    if margin < 0:
        raise ValueError(f"margin must be non-negative, got {margin!r}")

    list_a = list(blocks_a or [])
    list_b = list(blocks_b or [])

    if not list_a or not list_b:
        return []

    # Le grandezze aggregate si calcolano una volta per blocco, non una per coppia: e' il
    # motivo per cui la potatura e' economica.
    profile_a = [(item, _block_profile(_as_block(item), horizon)) for item in list_a]
    profile_b = [(item, _block_profile(_as_block(item), horizon)) for item in list_b]

    candidates: List[Tuple[object, object]] = []

    for item_a, (side_a, position_a, envelope_a) in profile_a:
        for item_b, (side_b, position_b, envelope_b) in profile_b:
            if item_a is item_b:
                continue

            if skip_same_side and side_a is not None and side_a == side_b:
                continue

            if position_a is None or position_b is None:
                logger.debug("block_pair_candidates: missing position, pair kept (cannot prune)")
                candidates.append((item_a, item_b))
                continue

            delta = _sub(position_a, position_b)

            if sqrt(_dot(delta, delta)) > envelope_a + envelope_b + margin:
                continue

            candidates.append((item_a, item_b))

    return candidates


def _block_profile(block, horizon: float):
    """(side, posizione, inviluppo) di un blocco: tutto cio' che serve alla potatura."""
    position = getattr(block, 'position', None)
    xyz = _to_xyz(position) if position is not None else None
    envelope = block_max_speed(block) * horizon + block_reach(block)

    return (getattr(block, 'side', None), xyz, envelope)


def region_block_pairs(region, side_a: str, side_b: str, horizon: float,
                       category: Optional[str] = None,
                       margin: float = 0.0) -> List[Tuple[object, object]]:
    """`block_pair_candidates` applicata ai blocchi di due schieramenti di una `Region`.

    Comodita' che chiude il giro con l'ecosistema esistente: `Region.get_blocks_by_criteria`
    seleziona, questa funzione pota. Restituisce coppie di `BlockItem`.
    """
    blocks_a = region.get_blocks_by_criteria(side=side_a, category=category)
    blocks_b = region.get_blocks_by_criteria(side=side_b, category=category)

    return block_pair_candidates(blocks_a, blocks_b, horizon=horizon, margin=margin,
                                 skip_same_side=False)


# ── ORCHESTRAZIONE: DAI BLOCCHI ALLE FINESTRE DI CONTATTO ─────────────────────

def schedule_contacts(blocks_a: Iterable, blocks_b: Iterable, horizon: float,
                      routes: Optional[Mapping[str, object]] = None,
                      starts: Optional[Mapping[str, float]] = None,
                      speeds: Optional[Mapping[str, float]] = None,
                      t0: float = 0.0,
                      margin: float = 0.0,
                      range_type: str = DEFAULT_DETECTION_RANGE_TYPE,
                      skip_same_side: bool = True) -> List[ContactWindow]:
    """Tutte le finestre di contatto fra due insiemi di blocchi, in `[t0, t0 + horizon]`.

    Mette insieme i tre meccanismi nell'ordine che li rende trattabili: prima la potatura a
    livello blocco (C), poi il CPA solo sulle coppie di asset superstiti (B).

    Un asset senza rotta in `routes` non viene ignorato: se ha una posizione, e' trattato
    come **fermo** per tutta la finestra (`static_legs`). E' il caso piu' comune in campagna
    — un sito SAM, un deposito, una base — e senza questo lo scheduler vedrebbe solo i
    contatti fra due forze entrambe in movimento.

    Args:
        blocks_a/blocks_b: `Block`/`Military`/`BlockItem` dei due schieramenti.
        horizon: durata [s] della finestra di simulazione.
        routes: `{asset_id: DataType.Route}` — **solo** il modello canonico (decisione Q1).
        starts: `{asset_id: istante di partenza [s]}`; default `t0`.
        speeds: `{asset_id: velocita' [m/s]}` che sovrascrive quella degli archi.
        t0: istante assoluto di inizio della finestra.
        margin/range_type/skip_same_side: v. `block_pair_candidates` e `contact_windows`.

    Returns:
        Lista di `ContactWindow` ordinata per `(t_start, asset_a_id, asset_b_id)`. **L'ordine
        e' parte del contratto**: e' cio' che rende la sessione riproducibile a parita' di
        seed (decisione dell'utente n. 2), non il seed da solo.
    """
    if horizon < 0:
        raise ValueError(f"horizon must be non-negative, got {horizon!r}")

    routes = routes or {}
    starts = starts or {}
    speeds = speeds or {}

    pairs = block_pair_candidates(blocks_a, blocks_b, horizon=horizon, margin=margin,
                                  skip_same_side=skip_same_side)

    if not pairs:
        return []

    legs_cache: Dict[int, List[Leg]] = {}
    windows: List[ContactWindow] = []

    def _legs_for(asset) -> List[Leg]:
        key = id(asset)

        if key not in legs_cache:
            legs_cache[key] = _asset_legs(asset, routes, starts, speeds, t0, horizon)

        return legs_cache[key]

    for item_a, item_b in pairs:
        assets_a = _operative_assets(_as_block(item_a))
        assets_b = _operative_assets(_as_block(item_b))

        for asset_a in assets_a:
            legs_a = _legs_for(asset_a)

            if not legs_a:
                continue

            for asset_b in assets_b:
                legs_b = _legs_for(asset_b)

                if not legs_b:
                    continue

                windows.extend(contact_windows(asset_a, legs_a, asset_b, legs_b,
                                               range_type=range_type))

    windows.sort(key=lambda w: (w.t_start, str(w.asset_a_id), str(w.asset_b_id)))

    return windows


def _operative_assets(block) -> List:
    """Asset operativi di un blocco; lista vuota se il blocco non ne ha."""
    assets = getattr(block, 'assets', None)

    if not assets:
        return []

    return [asset for asset in assets.values()
            if not hasattr(asset, 'is_operative') or asset.is_operative()]


def _asset_legs(asset, routes, starts, speeds, t0: float, horizon: float) -> List[Leg]:
    """Tratti di un asset: dalla sua rotta se ne ha una, altrimenti fermo in posizione."""
    asset_id = _asset_id(asset)
    route = routes.get(asset_id) if asset_id is not None else None

    if route is not None:
        start = float(starts.get(asset_id, t0))
        legs = route_legs(route, t0=start, speed=speeds.get(asset_id))

        if legs:
            return clamp_legs(legs, t0, t0 + horizon)

        logger.debug(f"_asset_legs: route of asset {asset_id!r} is not schedulable, "
                     f"falling back to its static position")

    return static_legs(getattr(asset, 'position', None), t0, t0 + horizon)
