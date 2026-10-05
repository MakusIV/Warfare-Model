"""Dalla Missione al movimento per asset: rotta, partenza e velocita' che il motore consuma.

FASE 3 di `Analysis/Document/Piano_Implementazione_Missione.md` ("la Missione attraversa la
porta di sessione"). `Command/Mission_Types` e' solo struttura; la LOGICA che ricava, per ogni
asset di una `Mission`, la forma che `Session_Simulator.run_session` consuma (le tre mappe
`routes`/`starts`/`speeds` di `Contact_Scheduler.schedule_contacts`) vive qui.

## Rotta per asset: rotta di riferimento + offset di formazione (D3.b)

La missione ha UNA rotta di riferimento (`Mission.route`, o in mancanza la spezzata dei
`MissionWaypoint`, v. `reference_route`); ogni `MissionAsset` dichiara un offset
(`forward_m`, `right_m`, `up_m`) nella terna della direzione di marcia:
  * avanti = versore ORIZZONTALE della direzione di marcia (la quota non inclina la formazione);
  * destra = avanti ruotato di 90 gradi in senso orario visto dall'alto (convenzione del
    progetto: nord = +y, est = +x, azimut orario, v. `Weapon_Delivery._unit`): avanti (hx, hy)
    -> destra (hy, -hx);
  * alto = +z, sempre.

**Offset nullo = la STESSA rotta** (lo stesso oggetto `Route`): i tratti sono identici a quelli
che si avrebbero passando la rotta di riferimento, senza alcuna aritmetica in mezzo.

**Regola ai cambi di direzione (decisa in F3): la formazione ruota con la rotta, sulla
bisettrice.** L'offset si applica PUNTO PER PUNTO, non tratto per tratto (applicarlo per tratto
staccherebbe i tratti consecutivi):
  * primo punto: terna del primo tratto; ultimo punto: terna dell'ultimo tratto;
  * punto intermedio: terna della BISETTRICE b = normalizzato(h_entrata + h_uscita), cioe' la
    direzione media fra il tratto in arrivo e quello in partenza;
  * la componente laterale e' scalata di 1/cos(theta/2) (theta = angolo di virata; giunzione "a
    spigolo", la stessa delle spezzate parallele): cosi' i tratti dell'asset restano PARALLELI a
    quelli di riferimento, a distanza `right_m`, prima e dopo la virata. Il fattore e' limitato
    a `MITER_LIMIT` per le virate strette (oltre 120 gradi il punto non schizza lontano);
  * la componente avanti e' presa lungo la bisettrice, senza scala;
  * inversione esatta (h_uscita = -h_entrata, bisettrice indefinita): si usa la terna del
    tratto in ENTRATA; il tratto successivo porta l'asset nella terna d'uscita al punto dopo
    (in una virata di 180 gradi il gregario di destra finisce dall'altra parte del riferimento,
    come in una formazione vera);
  * tratti senza componente orizzontale (salita/discesa sulla verticale, punti ripetuti)
    ereditano la direzione dal tratto orizzontale piu' vicino (prima il precedente); una rotta
    senza alcun tratto orizzontale ammette solo `up_m` (altrimenti ValueError).

Conseguenza da sapere: una formazione che TRASLA rigidamente (stesso spostamento per ogni
punto) coincide con una rotta di riferimento + offset solo se la rotta non cambia direzione;
con virate la traslata e' un'altra geometria (v. la migrazione degli scenari, F3).

Le coordinate della rotta per asset sono arrotondate al micrometro (`OFFSET_DECIMALS`): il
rumore della rotazione (ordine 1e-12 m) non ha significato fisico e non deve comparire come
differenza di posizione (sympy `Point3D` conserva i float come razionali).

## Velocita'

`MissionWaypoint.speed_kmh` e' la velocita' del tratto IN ARRIVO al punto (None = quella
dell'arco della rotta, in m/s). Quella del primo punto non ha tratto in arrivo ed e' ignorata.
  * nessuna velocita' dichiarata: valgono quelle degli archi, nessuna voce in `speeds`;
  * tutti i tratti dichiarano la STESSA velocita': una voce in `speeds` [m/s] (sostituisce
    quella degli archi, semantica di `route_legs`), rotta invariata;
  * dichiarazioni diverse o parziali: la rotta per asset e' ricostruita con la velocita'
    dichiarata sui tratti che la dichiarano e quella dell'arco sugli altri.
Conversione km/h -> m/s: `kmh / 3.6`.

## Partenza (istante assoluto)

Gli istanti della missione sono in secondi dall'inizio della sessione; la partenza assoluta e'
`t0 + ...` con `t0 = SessionOrder.t_start`. In ordine di precedenza:
  1. `start_time`;
  2. il primo waypoint con `eta_locked`: partenza = ETA - tempo di percorrenza fino a quel punto
     sulla rotta di riferimento (con le velocita' di missione);
  3. `tot`, ancorato al primo waypoint ATTACK (o, in mancanza, OBJECTIVE): stessa derivazione;
     senza un punto d'ancoraggio ValueError.
Tutti gli asset di una missione partono insieme (la formazione e' una). Una partenza derivata
anteriore all'inizio della sessione e' un errore (le missioni fuori finestra saranno rifiutate dal
validatore di sessione della F8; qui non si tagliano in silenzio). `Activation.ON_EVENT` e' solo
dichiarabile: ValueError.

## Cosa NON fa
- Nessuna attesa (WAIT), nessuna presenza prima della partenza o dopo la fine (F5).
- Non usa ruoli, regole, bersaglio, criteri di fine: arrivano con F4-F7.
- Nessun RNG, nessuna mutazione: funzioni pure.
"""

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    Activation,
    Mission,
    MissionAsset,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Mission_Adapter').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Limite del fattore 1/cos(theta/2) della componente laterale alle virate (v. docstring). STIMA DI
# PROGETTO, non un dato: 2.0 = esatto fino a virate di 120 gradi, tagliato oltre.
MITER_LIMIT = 2.0

# Decimali [m] delle coordinate di una rotta con offset: micrometro (v. docstring).
OFFSET_DECIMALS = 6

# Sotto questa norma [m] un tratto non ha direzione orizzontale; sotto questa norma (adimensionale)
# la somma di due versori e' un'inversione.
_HORIZONTAL_EPS = 1e-9
_REVERSAL_EPS = 1e-9

# Tipo d'arco e tipo di rotta per una rotta costruita dai soli MissionWaypoint.
_PATH_TYPE_BY_DOMAIN = {'air': 'air', 'ground': 'offroad', 'sea': 'water'}
_ROUTE_TYPE_BY_DOMAIN = {'air': 'air', 'ground': 'ground', 'sea': 'water'}

# Ruoli d'ancoraggio del TOT, in ordine di preferenza.
_TOT_ANCHOR_ROLES = (WaypointRole.ATTACK, WaypointRole.OBJECTIVE)


def kmh_to_ms(speed_kmh: float) -> float:
    """km/h -> m/s."""
    return float(speed_kmh) / 3.6


# ── TIPI ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AssetMovement:
    """Movimento di un asset di missione nella sessione, nella forma del motore.

    Attributes:
        mission_id/asset_id: id di dominio.
        route: `DataType.Route` dell'asset (None = missione senza rotta: l'asset resta fermo).
        start: istante assoluto di partenza [s] (t0 + istante di missione).
        speed: velocita' [m/s] che sostituisce quella degli archi, None = quella degli archi.
    """
    mission_id: str
    asset_id: str
    route: Optional[Route]
    start: float
    speed: Optional[float] = None


# ── ROTTA DI RIFERIMENTO E VELOCITA' ──────────────────────────────────────────

def _route_from_waypoints(mission: Mission) -> Route:
    """Rotta costruita dai `MissionWaypoint` quando la missione non porta una `Route`.

    Ogni tratto prende la velocita' dichiarata dal punto d'arrivo: senza, la rotta non e'
    percorribile (nessun arco da cui leggerla) e si solleva ValueError.
    """
    path_type = _PATH_TYPE_BY_DOMAIN[mission.domain]
    edges = {}

    for index in range(len(mission.waypoints) - 1):
        a, b = mission.waypoints[index], mission.waypoints[index + 1]

        if b.speed_kmh is None:
            raise ValueError(f"mission {mission.mission_id!r} has no route and waypoint {index + 1} "
                             f"declares no speed_kmh: the leg cannot be travelled")

        edges[(a.waypoint.name, b.waypoint.name)] = Edge(wpA=a.waypoint, wpB=b.waypoint, path_type=path_type,
                                                         danger_level=None, speed=kmh_to_ms(b.speed_kmh),
                                                         name=f'{mission.mission_id}-E{index}')

    return Route(route_type=_ROUTE_TYPE_BY_DOMAIN[mission.domain], edges=edges, name=f'{mission.mission_id}-route')


def reference_route(mission: Mission) -> Optional[Route]:
    """La rotta di riferimento della missione, None se la missione non si muove.

    `Mission.route` se presente; altrimenti, con almeno due `MissionWaypoint`, la spezzata dei
    loro `Waypoint` (v. `_route_from_waypoints`); altrimenti None (missione sul posto).
    """
    if not isinstance(mission, Mission):
        raise TypeError(f"mission must be a Mission, got {type(mission).__name__}")

    if mission.route is not None:
        return mission.route if mission.route.edges else None

    if len(mission.waypoints) >= 2:
        return _route_from_waypoints(mission)

    return None


def _leg_speeds(mission: Mission, route: Route) -> Tuple[Optional[float], Optional[List[Optional[float]]]]:
    """(velocita' uniforme [m/s] | None, velocita' per tratto [m/s | None] | None), v. docstring.

    Solo per una missione con `Mission.route`: una rotta costruita dai waypoint ha gia' le
    velocita' dichiarate sugli archi.
    """
    if mission.route is None or not mission.waypoints:
        return None, None

    declared = [mw.speed_kmh for mw in mission.waypoints[1:]]

    if all(speed is None for speed in declared):
        return None, None

    if len(declared) == len(route.edges) and len(set(declared)) == 1:
        return kmh_to_ms(declared[0]), None

    return None, [kmh_to_ms(speed) if speed is not None else None for speed in declared]


# ── GEOMETRIA DELL'OFFSET ─────────────────────────────────────────────────────

def _xyz(point) -> Tuple[float, float, float]:
    return float(point.x), float(point.y), float(point.z)


def _horizontal_heading(a, b) -> Optional[Tuple[float, float]]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    norm = math.hypot(dx, dy)
    return (dx / norm, dy / norm) if norm > _HORIZONTAL_EPS else None


def _leg_headings(points: Sequence[Tuple[float, float, float]]) -> List[Tuple[float, float]]:
    """Direzione orizzontale di ogni tratto; i tratti senza componente orizzontale la ereditano."""
    raw = [_horizontal_heading(points[i], points[i + 1]) for i in range(len(points) - 1)]

    if all(h is None for h in raw):
        raise ValueError("the route has no horizontal leg: forward/right offsets are undefined")

    headings: List[Optional[Tuple[float, float]]] = list(raw)

    for index, heading in enumerate(raw):
        if heading is not None:
            continue

        previous = next((raw[j] for j in range(index - 1, -1, -1) if raw[j] is not None), None)
        following = next((raw[j] for j in range(index + 1, len(raw)) if raw[j] is not None), None)
        headings[index] = previous if previous is not None else following

    return headings  # type: ignore[return-value]


def _point_frame(h_in: Optional[Tuple[float, float]], h_out: Optional[Tuple[float, float]]
                 ) -> Tuple[Tuple[float, float], float]:
    """(direzione avanti al punto, fattore della componente laterale), v. docstring."""
    if h_in is None:
        return h_out, 1.0

    if h_out is None:
        return h_in, 1.0

    sx, sy = h_in[0] + h_out[0], h_in[1] + h_out[1]
    norm = math.hypot(sx, sy)

    if norm < _REVERSAL_EPS:
        return h_in, 1.0   # inversione esatta: terna del tratto in entrata

    bisector = (sx / norm, sy / norm)
    cos_half = bisector[0] * h_in[0] + bisector[1] * h_in[1]
    return bisector, min(1.0 / cos_half, MITER_LIMIT)


def offset_points(points: Sequence[Tuple[float, float, float]], forward_m: float, right_m: float,
                  up_m: float) -> List[Tuple[float, float, float]]:
    """Punti della spezzata spostati dell'offset di formazione (regola nel docstring del modulo).

    Args:
        points: punti della rotta di riferimento (x, y, z) [m], almeno due.
        forward_m/right_m/up_m: offset nella terna della direzione di marcia [m].

    Returns:
        Lista di punti (x, y, z) arrotondati a `OFFSET_DECIMALS`.

    Raises:
        ValueError: meno di due punti; offset orizzontale su una rotta senza tratti orizzontali.
    """
    if len(points) < 2:
        raise ValueError(f"an offset needs at least two route points, got {len(points)}")

    if forward_m == 0.0 and right_m == 0.0:
        headings = [None] * (len(points) - 1)
    else:
        headings = _leg_headings(points)

    shifted = []

    for index, (x, y, z) in enumerate(points):
        if headings[0] is None:   # solo offset verticale
            dx = dy = 0.0
        else:
            h_in = headings[index - 1] if index > 0 else None
            h_out = headings[index] if index < len(headings) else None
            (fx, fy), lateral = _point_frame(h_in, h_out)
            rx, ry = fy, -fx   # destra = avanti ruotato di 90 gradi in senso orario
            dx = forward_m * fx + right_m * lateral * rx
            dy = forward_m * fy + right_m * lateral * ry

        shifted.append((round(x + dx, OFFSET_DECIMALS), round(y + dy, OFFSET_DECIMALS),
                        round(z + up_m, OFFSET_DECIMALS)))

    return shifted


def _rebuild_route(route: Route, points: Sequence[Tuple[float, float, float]],
                   speeds: Optional[Sequence[Optional[float]]], suffix: str) -> Route:
    """Copia di `route` con i punti dati e (se date) le velocita' per tratto; archi in ordine."""
    edges_in = list(route.edges.values())
    originals = route_waypoints(route)

    if len(originals) != len(edges_in) + 1 or len(points) != len(originals):
        raise ValueError(f"route {route.name!r} is not a chain of edges: cannot derive an asset route")

    waypoints = [Waypoint(point=Point3D(*point), name=f'{original.name}@{suffix}', obj_reference=original.reference)
                 for point, original in zip(points, originals)]
    edges = {}

    for index, edge in enumerate(edges_in):
        a, b = waypoints[index], waypoints[index + 1]
        speed = speeds[index] if speeds is not None and speeds[index] is not None else edge.speed
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type=edge.path_type, danger_level=edge.danger_level,
                                       speed=speed, name=f'{edge.name}@{suffix}')

    return Route(route_type=route.route_type, edges=edges, name=f'{route.name}@{suffix}')


# ── API ───────────────────────────────────────────────────────────────────────

def asset_route(mission: Mission, mission_asset: MissionAsset) -> Tuple[Optional[Route], Optional[float]]:
    """Rotta dell'asset di missione e velocita' uniforme [m/s] (None = quella degli archi).

    Offset nullo e nessuna velocita' per tratto: la rotta di riferimento STESSA (stesso oggetto).

    Raises:
        ValueError: asset non della missione, geometria non derivabile (v. `offset_points`).
    """
    if not isinstance(mission_asset, MissionAsset) or mission_asset not in mission.assets:
        raise ValueError(f"asset {getattr(mission_asset, 'asset_id', mission_asset)!r} is not in mission "
                         f"{mission.mission_id!r}")

    route = reference_route(mission)

    if route is None:
        return None, None

    uniform, per_leg = _leg_speeds(mission, route)
    zero_offset = (mission_asset.forward_m, mission_asset.right_m, mission_asset.up_m) == (0.0, 0.0, 0.0)

    if zero_offset and per_leg is None:
        return route, uniform

    points = [_xyz(waypoint.point) for waypoint in route_waypoints(route)]

    if not zero_offset:
        points = offset_points(points, mission_asset.forward_m, mission_asset.right_m, mission_asset.up_m)

    return _rebuild_route(route, points, per_leg, f'{mission.mission_id}:{mission_asset.asset_id}'), uniform


def _travel_time_to(route: Route, speed: Optional[float], index: int) -> float:
    """Tempo [s] dalla partenza al waypoint `index` (0 = partenza) della rotta."""
    if index == 0:
        return 0.0

    legs = CS.route_legs(route, t0=0.0, speed=speed)

    if len(legs) < index:
        raise ValueError(f"route {route.name!r} is not schedulable up to waypoint {index}")

    return legs[index - 1].t_end


def mission_start(mission: Mission, t0: float = 0.0) -> float:
    """Istante assoluto [s] di partenza della missione (precedenze nel docstring del modulo).

    Raises:
        ValueError: attivazione ON_EVENT, TOT senza punto d'ancoraggio, partenza derivata
            anteriore a `t0`.
    """
    if mission.activation is Activation.ON_EVENT:
        raise ValueError(f"mission {mission.mission_id!r}: ON_EVENT activation is declarable only, "
                         f"no executor runs it yet")

    if mission.start_time is not None:
        return float(t0) + mission.start_time

    route = reference_route(mission)
    locked = next((index for index, mw in enumerate(mission.waypoints) if mw.eta_locked), None)

    if locked is not None:
        anchor, instant, label = locked, mission.waypoints[locked].planned_eta, 'locked ETA'
    else:
        anchor = next((index for role in _TOT_ANCHOR_ROLES
                       for index, mw in enumerate(mission.waypoints) if mw.role is role), None)

        if anchor is None:
            raise ValueError(f"mission {mission.mission_id!r}: tot needs an ATTACK or OBJECTIVE waypoint "
                             f"to anchor the departure")

        instant, label = mission.tot, 'tot'

    travel = 0.0

    if route is not None and anchor > 0:
        uniform, per_leg = _leg_speeds(mission, route)
        timed = route if per_leg is None else _rebuild_route(
            route, [_xyz(w.point) for w in route_waypoints(route)], per_leg, f'{mission.mission_id}:timing')
        travel = _travel_time_to(timed, uniform, anchor)

    start = float(t0) + instant - travel

    if start < float(t0) - CS.TIME_EPS:
        raise ValueError(f"mission {mission.mission_id!r}: departure derived from the {label} ({instant} s) "
                         f"falls {float(t0) - start:.1f} s before the session start")

    return start


def mission_movements(mission: Mission, t0: float = 0.0) -> Tuple[AssetMovement, ...]:
    """Un `AssetMovement` per asset della missione, nell'ordine degli asset."""
    start = mission_start(mission, t0)
    movements = []

    for mission_asset in mission.assets:
        route, speed = asset_route(mission, mission_asset)
        movements.append(AssetMovement(mission.mission_id, mission_asset.asset_id, route, start, speed))

    return tuple(movements)


def session_movements(missions: Iterable[Mission], t0: float = 0.0
                      ) -> Tuple[Dict[str, Route], Dict[str, float], Dict[str, float]]:
    """`(routes, starts, speeds)` per `schedule_contacts`/`run_session` da tutte le missioni.

    Solo gli asset con rotta compaiono nelle mappe (gli altri restano fermi, come prima); `speeds`
    solo per gli asset con velocita' uniforme dichiarata.

    Raises:
        ValueError: un asset in due missioni (lo vieta gia' `SessionOrder`; qui per chi chiama
            direttamente), e gli errori di `mission_movements`.
    """
    routes: Dict[str, Route] = {}
    starts: Dict[str, float] = {}
    speeds: Dict[str, float] = {}
    seen: Dict[str, str] = {}

    for mission in missions:
        for movement in mission_movements(mission, t0):
            if movement.asset_id in seen:
                raise ValueError(f"asset {movement.asset_id!r} is in missions {seen[movement.asset_id]!r} "
                                 f"and {movement.mission_id!r}")

            seen[movement.asset_id] = movement.mission_id

            if movement.route is None:
                continue

            routes[movement.asset_id] = movement.route
            starts[movement.asset_id] = movement.start

            if movement.speed is not None:
                speeds[movement.asset_id] = movement.speed

    return routes, starts, speeds


def waypoint_times(movement: AssetMovement) -> Tuple[float, ...]:
    """Istanti assoluti [s] di passaggio ai punti della rotta dell'asset (0 = partenza), senza
    taglio alla sessione; tupla vuota se l'asset non ha rotta o la rotta non e' percorribile."""
    if movement.route is None:
        return ()

    legs = CS.route_legs(movement.route, t0=movement.start, speed=movement.speed)

    if not legs:
        return ()

    return (legs[0].t_start,) + tuple(leg.t_end for leg in legs)


def mission_routes(missions: Iterable[Mission], t0: float = 0.0) -> Dict[str, Route]:
    """Solo le rotte per asset di `session_movements` (comodita' per chi interroga lo scheduler)."""
    return session_movements(missions, t0)[0]
