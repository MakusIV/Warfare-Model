"""Adattatore verso il modello di rotta canonico del progetto.

DECISIONE (2026-09-22, §9 di `Architettura_esecuzione_sessioni_virtuali_ANALISI.md`):
**`DataType.Route`/`DataType.Edge`/`DataType.Waypoint` e' l'UNICO modello di rotta del
dominio**, conferma della decisione di agosto 2026. Le classi `Waypoint`/`Edge`/`Route`/
`Path`/`PathCollection` interne a `Logic/Air_Route_Manager.py` e le `Waypoint`/`Edge` interne
a `Logic/Ground_Route_Manager.py` sono **stato di lavoro privato dell'algoritmo di ricerca**
(code di priorita', ricorsione, metriche parziali) e non devono mai uscire dal loro modulo.

Questo modulo e' la frontiera: converte il risultato finale di un path-finding nel tipo
canonico, che e' quello che consumano `Context/Region.py`, `Block/Military.py`,
`Logic/Tactical_Evaluation.py`, `Command/Command_Types.py` e — dalla Fase 3 in avanti — il
`Contact_Scheduler` del motore di sessioni virtuali (che ha bisogno di `Route.positionAtTime`
e `Route.travelTimeToEdge`, esistenti solo sul tipo canonico).

Le funzioni sono **duck-typed di proposito**: non importano ne' `Air_Route_Manager` ne'
`Ground_Route_Manager`, cosi' la dipendenza resta a senso unico (i Route Manager possono
importare questo modulo, non viceversa) e non si introducono cicli.

Convenzioni rispettate:
- nessuna eccezione per dati mancanti o degeneri: `None`/default sicuro + log;
  `TypeError`/`ValueError` solo per argomenti fuori dominio (errore di programmazione);
- archi di lunghezza nulla scartati con log di debug: non sono percorrenza, e un arco
  degenere e' comunque rappresentabile dal tipo canonico ma non trasporta nulla.
"""

from typing import Dict, Iterable, List, Optional

from Code.Dynamic_War_Manager.Source.Context.Context import PATH_TYPE, ROUTE_TYPE
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Route_Adapter').logger


# Mappa path_type -> route_type quando il chiamante non lo impone esplicitamente.
# 'mixed' quando gli archi non sono tutti dello stesso tipo (v. Context.ROUTE_TYPE).
_PATH_TYPE_TO_ROUTE_TYPE = {
    'air': 'air',
    'onroad': 'ground',
    'offroad': 'ground',
    'water': 'water',
}


def route_type_from_path_types(path_types: Iterable[str]) -> Optional[str]:
    """route_type canonico corrispondente all'insieme dei path_type degli archi.

    Returns:
        Uno di ROUTE_TYPE, 'mixed' se gli archi appartengono a famiglie diverse,
        None se l'insieme e' vuoto o contiene solo tipi sconosciuti.
    """
    families = {_PATH_TYPE_TO_ROUTE_TYPE[pt] for pt in path_types if pt in _PATH_TYPE_TO_ROUTE_TYPE}

    if not families:
        return None

    if len(families) > 1:
        return 'mixed'

    return families.pop()


def _unique_name(base: Optional[str], used: Dict[str, int]) -> str:
    """Nome di waypoint univoco all'interno della rotta.

    Obbligatorio: `Route.getWaypoints()` mette i waypoint in un heap di tuple
    `(nome, waypoint)`; a parita' di nome Python confronta i `Waypoint`, che non
    definiscono `__lt__`, e solleva TypeError. I generatori di rotta riusano gli stessi
    nomi (es. `wp_A0_1` e `wp_A0_1_alt` su rami diversi della ricorsione), quindi la
    de-duplicazione va fatta qui, non nel tipo canonico.
    """
    name = base if isinstance(base, str) and base else 'wp'
    count = used.get(name, 0)
    used[name] = count + 1

    return name if count == 0 else f"{name}#{count}"


def _canonical_waypoint(point, name: Optional[str], used: Dict[str, int]) -> Waypoint:
    """DataType.Waypoint da un punto sympy e un nome (reference asset non disponibile qui)."""
    return Waypoint(point=point, name=_unique_name(name, used), obj_reference=None)


def _edges_in_order(container) -> List:
    """Archi del contenitore nell'ordine di percorrenza.

    Accetta sia un oggetto con `.edges` lista (i `Path` dei pianificatori) sia con `.edges`
    dizionario (le loro `Route` interne): in entrambi i casi l'ordine di inserimento e'
    l'ordine di percorrenza, la stessa assunzione gia' fatta da `Route.travelTimeToEdge`.
    """
    edges = getattr(container, 'edges', None)

    if edges is None:
        return []

    if isinstance(edges, dict):
        return list(edges.values())

    return list(edges)


def to_canonical_route(container,
                       name: Optional[str] = None,
                       path_type: str = 'air',
                       route_type: Optional[str] = None,
                       speed: Optional[float] = None) -> Optional[Route]:
    """Converte il risultato di un pianificatore di rotta in una `DataType.Route`.

    Il contenitore e' duck-typed: serve solo un attributo `edges` (lista o dizionario) i cui
    elementi espongano `wpA`/`wpB` (con `.point` sympy e `.name`), `speed` e `danger`.
    E' la forma di `Air_Route_Manager.Path` e `Air_Route_Manager.Route`.

    Args:
        container: il Path/Route interno prodotto dal pianificatore.
        name: nome della rotta canonica; se None si usa `container.name` se esiste.
        path_type: path_type da attribuire a ogni arco canonico (uno di Context.PATH_TYPE).
        route_type: route_type canonico; se None viene dedotto dal path_type.
        speed: velocita' [m/s] che sovrascrive quella dei singoli archi. Serve perche' la
            `speed` degli archi del pianificatore aereo e' marcata "deprecated" nel suo
            modello, mentre sul tipo canonico e' il dato su cui poggiano `travelTime` e
            `positionAtTime`.

    Returns:
        La `Route` canonica, oppure None se il contenitore non ha archi utilizzabili.

    Raises:
        ValueError: path_type/route_type fuori dominio (errore di programmazione).
    """
    if path_type not in PATH_TYPE:
        raise ValueError(f"path_type must be one of {PATH_TYPE}, got {path_type!r}")

    if route_type is not None and route_type not in ROUTE_TYPE:
        raise ValueError(f"route_type must be one of {ROUTE_TYPE}, got {route_type!r}")

    if container is None:
        logger.debug("to_canonical_route: no container (path-finding found no route)")
        return None

    source_edges = _edges_in_order(container)

    if not source_edges:
        logger.warning("to_canonical_route: container has no edges, route not built")
        return None

    used_names: Dict[str, int] = {}
    canonical_edges: Dict = {}
    previous_wp: Optional[Waypoint] = None

    for source_edge in source_edges:
        point_a = source_edge.wpA.point
        point_b = source_edge.wpB.point

        if point_a == point_b:
            logger.debug(f"to_canonical_route: zero-length edge {getattr(source_edge, 'name', None)!r} skipped")
            continue

        # Il waypoint di arrivo dell'arco precedente e quello di partenza di questo sono lo
        # stesso punto in oggetti distinti: si riusa l'oggetto canonico gia' creato, cosi'
        # la rotta e' una spezzata connessa e non una sequenza di archi scollegati.
        if previous_wp is not None and previous_wp.point == point_a:
            wp_a = previous_wp
        else:
            wp_a = _canonical_waypoint(point_a, getattr(source_edge.wpA, 'name', None), used_names)

        wp_b = _canonical_waypoint(point_b, getattr(source_edge.wpB, 'name', None), used_names)

        edge_speed = speed if speed is not None else getattr(source_edge, 'speed', None)
        danger = getattr(source_edge, 'danger', None)

        if danger is None:
            danger = getattr(source_edge, 'danger_level', None)

        canonical_edges[(wp_a.name, wp_b.name)] = Edge(
            wpA=wp_a,
            wpB=wp_b,
            path_type=path_type,
            danger_level=float(danger) if danger is not None else None,
            speed=float(edge_speed) if edge_speed is not None else None,
            name=getattr(source_edge, 'name', None),
        )

        previous_wp = wp_b

    if not canonical_edges:
        logger.warning("to_canonical_route: every edge was degenerate, route not built")
        return None

    if route_type is None:
        route_type = route_type_from_path_types([path_type]) or 'mixed'

    route_name = name if name is not None else getattr(container, 'name', None)

    return Route(route_type=route_type, edges=canonical_edges, name=route_name)


def ground_path_to_route(graph,
                         waypoints: List,
                         name: Optional[str] = None,
                         route_type: Optional[str] = None,
                         speed: Optional[float] = None) -> Optional[Route]:
    """Converte il risultato di `NavigationGraph.find_optimal_path` in una `DataType.Route`.

    Il pianificatore a terra restituisce la sola sequenza di waypoint attraversati: gli archi
    (con `danger_level`, `path_type` e `max_speed`) vanno ripresi dal grafo, che e' l'unico a
    saperli. Per questo la firma prende anche il grafo, a differenza della controparte aerea.

    Args:
        graph: il `NavigationGraph` su cui il percorso e' stato calcolato (duck-typed: serve
            `get_neighbors(waypoint)` oppure l'attributo `graph`).
        waypoints: la lista ordinata di waypoint interni restituita dal path-finding.
        name: nome della rotta canonica.
        route_type: route_type canonico; se None viene dedotto dai path_type degli archi.
        speed: velocita' [m/s] che sovrascrive la `max_speed` degli archi. La `max_speed` del
            grafo e' un limite del terreno, non la velocita' dell'asset che percorre la
            rotta: chi conosce l'asset (Fase 3) passa la sua velocita' qui.

    Returns:
        La `Route` canonica, oppure None se il percorso e' vuoto/non convertibile.
    """
    if route_type is not None and route_type not in ROUTE_TYPE:
        raise ValueError(f"route_type must be one of {ROUTE_TYPE}, got {route_type!r}")

    if not waypoints or len(waypoints) < 2:
        logger.debug("ground_path_to_route: path has less than two waypoints, route not built")
        return None

    used_names: Dict[str, int] = {}
    canonical_edges: Dict = {}
    path_types: List[str] = []
    previous_wp: Optional[Waypoint] = None

    for wp_from, wp_to in zip(waypoints, waypoints[1:]):
        source_edge = _find_ground_edge(graph, wp_from, wp_to)

        if source_edge is None:
            logger.warning(f"ground_path_to_route: no edge between {wp_from!r} and {wp_to!r}, route not built")
            return None

        point_a = _ground_point(wp_from)
        point_b = _ground_point(wp_to)

        if point_a == point_b:
            logger.debug("ground_path_to_route: zero-length edge skipped")
            continue

        if previous_wp is not None and previous_wp.point == point_a:
            wp_a = previous_wp
        else:
            wp_a = _canonical_waypoint(point_a, getattr(wp_from, 'name', None), used_names)

        wp_b = _canonical_waypoint(point_b, getattr(wp_to, 'name', None), used_names)

        edge_path_type = getattr(source_edge, 'path_type', None)

        if edge_path_type not in PATH_TYPE:
            logger.warning(f"ground_path_to_route: unknown path_type {edge_path_type!r}, edge defaulted to 'offroad'")
            edge_path_type = 'offroad'

        path_types.append(edge_path_type)
        edge_speed = speed if speed is not None else getattr(source_edge, 'max_speed', None)
        danger = getattr(source_edge, 'danger_level', None)

        canonical_edges[(wp_a.name, wp_b.name)] = Edge(
            wpA=wp_a,
            wpB=wp_b,
            path_type=edge_path_type,
            danger_level=float(danger) if danger is not None else None,
            speed=float(edge_speed) if edge_speed is not None else None,
            name=f"{wp_a.name}->{wp_b.name}",
        )

        previous_wp = wp_b

    if not canonical_edges:
        logger.warning("ground_path_to_route: every edge was degenerate, route not built")
        return None

    if route_type is None:
        route_type = route_type_from_path_types(path_types) or 'mixed'

    return Route(route_type=route_type, edges=canonical_edges, name=name)


def _ground_point(waypoint):
    """Point3D dal waypoint del pianificatore a terra, che porta x/y/z sciolte."""
    from sympy import Point3D

    return Point3D(waypoint.x, waypoint.y, waypoint.z)


def _find_ground_edge(graph, wp_from, wp_to):
    """Arco del grafo fra due waypoint consecutivi del percorso, None se assente."""
    if hasattr(graph, 'get_neighbors'):
        candidates = graph.get_neighbors(wp_from)
    else:
        candidates = getattr(graph, 'graph', {}).get(wp_from, [])

    for edge in candidates:
        if edge.end is wp_to or edge.end == wp_to:
            return edge

    return None
