"""Fabbrica di scenari per la validazione del motore di sessioni virtuali (FASE 7).

Harness condiviso dai test di validazione (`Test_Session_Validation.py`,
`Test_Session_Scenarios.py` e i successivi S10-S18): costruisce con **oggetti reali** gli
ingredienti comuni agli scenari, e SOLO quelli. Non duplica nessuna logica del motore
(niente Pd, salve, danno, carburante): ogni numero di un esito viene da
`Logic/Session_Simulator.run_session` e dai moduli che chiama.

Il nome del file NON comincia con `Test_`, quindi `unittest discover -p "Test_*.py"` non lo
tratta come modulo di test; le classi di supporto non ereditano da `unittest.TestCase`
(convenzione del progetto, v. il pattern mixin in memoria `feedback_test_base_class`).

## Cosa fornisce

* **Asset reali dai registri** — `make_vehicle`, `make_aircraft`, `make_ship`: le classi vere
  `Vehicle`/`Aircraft`/`Ship`, con un modello dei registri `Vehicle_Data`/`Aircraft_Data`/
  `Ship_Data`. Velocita' (Fase 1), portate dei sensori (Fase 2), munizioni, carburante e
  profilo di reazione sono quelli che i registri danno. L'id e' SEMPRE esplicito
  (`Asset.__init__` genererebbe un suffisso casuale: v. "Id stabili" sotto).
* **Forze** — `make_force` crea una `Military` (o, con `category='Logistic'`, un `Block`
  logistico) con id esplicito; `add_assets` vi inserisce gli asset; `build_force`
  fa le due cose insieme a partire da una lista di `Unit`.
* **Infrastrutture** (S7, S12-S18) — `make_infrastructure` crea un blocco non militare
  reale (`Production`/`Transport`/`Storage`/`Urban`, costruibili dal 2026-09-23) con
  sotto-categoria validata; `make_structure` crea una `Structure` reale (edificio, ponte,
  deposito) da mettere in un blocco infrastrutturale O in una `Military` (bunker C2,
  piazzole di un FARP, banchine di un porto). Una `Structure` non ha sensori ne' armi: e'
  solo un bersaglio (modo di rilevamento 'ground', v. Contact_Scheduler).
* **Rotte** — `straight_route` costruisce una `DataType.Route` reale su una spezzata, come
  gia' fanno Test_Contact_Scheduler/Test_Session_Simulator; `route_for` ne ricava la
  velocita' dal profilo del registro dell'asset.
* **Missioni** (Fase 3 del piano della Missione) — `missions_for` trasforma le rotte di
  `routes_for` in `Mission` (rotta di riferimento + offset di formazione): dal 2026-10-05 le
  missioni sono l'unica strada con cui un asset si muove in `run_session`. V. "Migrazione alle
  missioni" sotto.
* **fire_control di riferimento** — `make_fire_control` (v. sotto).
* **Esecuzione** — `run(...)`: `SessionOrder` + `run_session` in una chiamata;
  `Scenario` (forze + rotte + fire_control + durata, con `.run(session_id)`);
  `combined_arms_scenario()`: la composizione di S1, riusata da S9, dal test di
  determinismo e da quello di agnosticismo; `LoggerSilencer`: mixin che silenzia i
  logger dei moduli del motore per l'intera classe di test.
* **Letture dell'esito** — piccole funzioni di conteggio (`losses_of`, `damage_by_source`,
  ...): SOLO letture del `SessionOutcome`, nessun ricalcolo.

## Sensori dichiarati (lacuna dei registri, documentata)

I registri NON dichiarano alcun sensore in modo 'ground' per carri, corazzati e artiglieria
(tutti i record `Tank`/`Armored`/`Artillery_*` di Vehicle_Data hanno portate nulle), e nessun
sensore in modo 'ground' per le navi. Con i soli registri due forze terrestri non si
vedono MAI, quindi `Contact_Scheduler` non produce finestre e lo scontro terra-terra (S1,
S4, S8, S9) non avviene: e' un dato mancante, non un errore del motore
(`Mobile.detection_range` lo dichiara: "il chiamante decide la propria politica di
default (es. una portata visiva minima) su un None"), ma oggi nessun chiamante del core la
applica. Per gli scenari si usa quindi un **sensore dichiarato di test**
(`declare_sensor`): sostituisce la portata SOLO per i modi indicati e delega al registro
per gli altri. E' un'iniezione esplicita e visibile in ogni scenario, non un'alterazione
silenziosa dei registri.

## fire_control di riferimento: una tabella di ruoli, NON la selezione dell'arma

La selezione dell'arma dai registri (Ground_Weapon_Data/Ship_Weapon_Data/loadout) e'
esplicitamente fuori scope (rimandata dalla Fase 4). `make_fire_control` e' la funzione
minimale dichiarata come tale: classifica tiratore e bersaglio in un **ruolo** e consulta
una tabella `(ruolo tiratore, ruolo bersaglio) -> ShotSpec | None`.

* Ruoli dedotti dagli asset reali (`role_of`): 'air' (Aircraft), 'sea' (Ship), 'sam'/'aaa'
  (Vehicle.isSAM/isAAA, dai tipi del registro — anche dentro un blocco logistico: la
  difesa organica di un impianto resta difesa aerea), 'artillery' (Vehicle.isArtillery),
  'ground' (ogni altro Vehicle), 'logistic' (qualunque altro asset di un blocco logistico),
  'structure' (una `Structure` di un blocco NON logistico: bunker C2 di una `Military`,
  edificio di un `Urban` civile). Nella tabella di riferimento 'structure' e' un bersaglio
  di superficie come gli altri e non spara mai (non e' mai un tiratore).
* Ruoli di missione imposti per id (`roles={asset_id: ruolo}`), per distinguere cio' che
  il tipo non dice: 'fighter' (solo aria-aria), 'strike' (solo aria-suolo non-AD), 'sead'
  (solo contro sam/aaa). Valgono SOLO per il tiratore: come bersaglio ogni asset resta
  classificato per dominio (per un SAM uno 'strike' e' un 'air').
* Le `ShotSpec` sono **costanti di test dichiarate** (`SHOTS`), di ordine di grandezza
  plausibile ma NON calibrate e NON prese da una fonte: gli scenari ne verificano
  l'effetto qualitativo (chi perde di piu', cosa accade prima), mai un numero.
* Gerarchia: `overrides[shooter_id][target_role]` > `table[(shooter_role, target_role)]` >
  None (non ingaggia: stessa semantica ROE di `resolve_engagement`).

Per uno scenario che ha bisogno di armi diverse basta passare un'altra tabella (es.
`{**REFERENCE_FIRE_TABLE, (ruolo, ruolo): ShotSpec}` — le chiavi sono tuple, quindi non
`dict(..., **{...})`) o degli override per asset.

## Id stabili

`Block.__init__`/`Military.__init__` accettano `id` esplicito (v. Session_Simulator,
"Precondizione di riproducibilita'"); `Asset` no, e genera `name_#NNNNNN`: gli asset
ricevono quindi l'id esplicito DOPO la costruzione tramite il setter `Asset.id`, come fa
gia' Test_Session_Simulator. Con gli stessi argomenti lo stesso scenario e' ricostruito
identico, id compresi: e' la base del test di determinismo.

## Migrazione alle missioni (F3, 2026-10-05)

Ogni asset che prima riceveva una rotta in `routes` e' ora asset di una `Mission`; gli asset
fermi (difese, siti SAM, blocchi in posizione) NON sono missioni (saranno la postura continua
della F4). `missions_for` riproduce ESATTAMENTE la geometria di `routes_for`:
  * una missione = asset di UN blocco e di UN dominio sulla stessa geometria. In F3 la
    velocita' sugli archi divideva anche le missioni (in un blocco misto, es. carri M1A2 + M2
    Bradley, i due modelli diventavano due missioni dello stesso blocco); dalla F4a vale la
    **regola A** (decisione dell'utente, 2026-10-05): la missione si muove INSIEME, alla
    velocita' del mezzo piu' lento, come un gruppo DCS. `missions_for` riunisce quindi gli asset
    che differiscono SOLO per velocita' in una missione la cui rotta di riferimento ha, tratto
    per tratto, la velocita' minima fra quelle dei suoi asset (v. `_slowest_reference`). Chi
    vuole velocita' diverse chiama `missions_for` piu' volte con `only` (missioni separate);
  * dentro una missione la rotta di riferimento e' quella del primo asset (per id) e gli altri
    hanno l'offset di formazione che riproduce la loro rotta traslata; l'offset e' accettato
    solo se `Mission_Adapter.asset_route` ridà gli STESSI punti (confronto esatto), altrimenti
    l'asset ha una missione propria (succede con rotte che cambiano direzione: una traslata
    rigida non e' un offset nella terna di marcia, v. `Mission_Adapter`).
In F4 la missione diventa l'unita' d'ingaggio: dove un blocco ha piu' missioni, queste
disingaggeranno separatamente.

**Effetto della regola A sulla geometria**: nessuno. Gli offset di formazione sono gli stessi di
F3 (la velocita' non entra nell'offset); cambia solo la velocita' degli asset piu' veloci, che ora
procedono al passo del piu' lento della loro missione.

**Semplificazione di scenario: rotta senza rientro, da completare con RTB in F5-F6.** Le
rotte aeree degli scenari partono in volo (`start_mode` AIR) e finiscono sull'obiettivo o
oltre, senza tornare in base; per non indebolire la validazione di `Mission` (D2.c: una
missione aerea finisce con LAND) l'ultimo punto ha ruolo LAND. Vale per OGNI missione aerea
costruita da `missions_for`.

## Cosa NON fa
- Non sceglie armi dai registri, non calcola esiti, non campiona nulla: nessun RNG qui.
- Nessun componente LLM, in nessuna forma.
"""

import time as _time
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from unittest.mock import MagicMock, patch

from sympy import Point3D

# Military prima delle classi di asset: e' l'ordine d'import che evita il ciclo noto
# Aircraft/Vehicle/Ship <-> Block (v. memoria feedback_circular_import_workaround).
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.Asset.Structure import Structure
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Asset.Ship import Ship
from Code.Dynamic_War_Manager.Source.Asset.Vehicle import Vehicle
from Code.Dynamic_War_Manager.Source.Asset.Mobile import DEFAULT_DETECTION_RANGE_TYPE, DETECTION_MODES
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    Mission,
    MissionAsset,
    MissionWaypoint,
    StartMode,
    Target,
    TargetKind,
    TargetProvenance,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Context.Context import MILITARY_CATEGORY
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS


# ── LOGGER ────────────────────────────────────────────────────────────────────

_SOURCE = 'Code.Dynamic_War_Manager.Source.'

# Logger dei moduli toccati da uno scenario: silenziati per non riempire i log di file con
# migliaia di righe per test (costruzione di centinaia di asset, ogni ingaggio).
LOGGER_TARGETS = tuple(_SOURCE + name + '.logger' for name in (
    'Asset.Asset', 'Asset.Mobile', 'Asset.Vehicle', 'Asset.Aircraft', 'Asset.Ship',
    'Asset.Structure', 'Block.Block', 'Block.Military', 'Block.Production', 'Block.Transport',
    'Block.Storage', 'Block.Urban', 'DataType.State', 'Logic.Air_Route_Manager',
    'Logic.Engagement_Resolver', 'Logic.Contact_Scheduler', 'Logic.Fuel_Model',
    'Logic.Damage_Model', 'Logic.Session_Simulator', 'Logic.Fire_Control', 'Logic.Weapon_Delivery',
    'Command.Session_Types', 'Command.Mission_Types', 'Logic.Mission_Adapter',
    'Context.Reaction_Profile', 'Context.Doctrine'))


def start_logger_patches() -> List:
    """Avvia i patch dei logger di LOGGER_TARGETS; un modulo senza `logger` e' saltato."""
    started = []

    for target in LOGGER_TARGETS:
        patcher = patch(target, MagicMock())

        try:
            patcher.start()
        except AttributeError:
            continue

        started.append(patcher)

    return started


def stop_logger_patches(started: Sequence) -> None:
    for patcher in reversed(list(started)):
        patcher.stop()


class LoggerSilencer:
    """Mixin (NON un TestCase) che silenzia i logger del motore per l'intera classe di test.

    A livello di CLASSE (setUpClass/tearDownClass) e non di singolo test, perche' gli
    scenari eseguono le repliche una volta sola in `setUpClass` e le condividono fra i
    metodi di verifica. Uso:

        class TestX(LoggerSilencer, unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                super().setUpClass()      # prima: avvia i patch
                cls.outcomes = ...        # repliche
    """

    @classmethod
    def setUpClass(cls):
        cls._logger_patches = start_logger_patches()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        stop_logger_patches(cls._logger_patches)


# ── COSTANTI DI SCENARIO (dichiarate di test) ─────────────────────────────────

# Portata di un sensore "visivo/ottico" dichiarato per i mezzi terrestri che nei registri
# non ne hanno (v. "Sensori dichiarati" nel docstring). Ordine di grandezza della linea di
# vista in terreno aperto; NON calibrata.
DECLARED_GROUND_VISUAL_RANGE = 4_000.0

# Portata dichiarata per l'osservazione d'artiglieria (osservatore avanzato), stesso statuto.
DECLARED_ARTILLERY_OBSERVATION_RANGE = 12_000.0

# Quota di default [m] degli aerei negli scenari.
DEFAULT_AIR_ALTITUDE = 5_000.0

# Mil_category di default per dominio (chiavi di MILITARY_CATEGORY).
GROUND_UNIT = MILITARY_CATEGORY['Ground_Base'][4]   # 'Company'
AIR_UNIT = MILITARY_CATEGORY['Air_Base'][0]         # 'Airbase'
NAVAL_UNIT = MILITARY_CATEGORY['Naval_Base'][2]     # 'Naval_Group'
LOGISTIC_CATEGORY = 'Logistic'


# ── ASSET REALI ───────────────────────────────────────────────────────────────

def _point(position) -> Point3D:
    if isinstance(position, Point3D):
        return position

    x, y, *rest = position
    return Point3D(x, y, rest[0] if rest else 0.0)


def declare_sensor(asset, ranges: Mapping[str, float]):
    """Sensore dichiarato di test: `ranges` = {modo: portata [m]} (v. docstring del modulo).

    Scavalca `detection_range` SOLO sull'istanza e SOLO per i modi indicati (qualunque
    `range_type`: un sensore dichiarato ha una sola portata); per gli altri modi delega al
    metodo della classe, cioe' al registro. Restituisce l'asset.

    Raises:
        ValueError: modo fuori da DETECTION_MODES o portata non positiva.
    """
    declared = {}

    for mode, value in ranges.items():
        if mode not in DETECTION_MODES:
            raise ValueError(f"mode must be one of {DETECTION_MODES!r}, got {mode!r}")

        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"declared range must be a positive number, got {value!r}")

        declared[mode] = float(value)

    registry_method = type(asset).detection_range

    def detection_range(mode, sensor=None, range_type=DEFAULT_DETECTION_RANGE_TYPE):
        if mode in declared:
            return declared[mode]

        return registry_method(asset, mode, sensor=sensor, range_type=range_type)

    asset.detection_range = detection_range
    asset.declared_sensors = dict(declared)

    return asset


def _finish(asset, asset_id: str, sensors: Optional[Mapping[str, float]]):
    asset.id = asset_id

    if sensors:
        declare_sensor(asset, sensors)

    return asset


def make_vehicle(block, asset_id: str, model: str, position, *,
                 asset_type: Optional[str] = None,
                 sensors: Optional[Mapping[str, float]] = None) -> Vehicle:
    """`Vehicle` reale del registro `Vehicle_Data`, con id esplicito.

    `asset_type` di default = la categoria del registro (es. 'Tank', 'SAM_Medium'), che e'
    cio' che leggono `Vehicle.isSAM/isAAA/isArtillery` e quindi `role_of` e
    `Military.salvo_interceptors`.
    """
    if asset_type is None:
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data
        record = Vehicle_Data._registry.get(model)
        asset_type = getattr(record, 'category', None)

    vehicle = Vehicle(block=block, name=asset_id, model=model, category=asset_type,
                      asset_type=asset_type, position=_point(position))

    return _finish(vehicle, asset_id, sensors)


def make_aircraft(block, asset_id: str, model: str, position, *,
                  asset_type=None, loadout: Optional[str] = None,
                  sensors: Optional[Mapping[str, float]] = None) -> Aircraft:
    """`Aircraft` reale del registro `Aircraft_Data`, con id esplicito.

    `loadout` (chiave di AIRCRAFT_LOADOUTS[model]) arma il velivolo: munizioni e carburante
    dal loadout; senza, restano None (non modellati), come in campagna prima
    dell'assegnazione della missione.
    """
    if asset_type is None:
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
        record = Aircraft_Data._registry.get(model)
        category = getattr(record, 'category', None)
        asset_type = category[0] if isinstance(category, (list, tuple)) and category else category

    aircraft = Aircraft(block=block, name=asset_id, model=model, asset_type=asset_type,
                        position=_point(position))

    if loadout is not None:
        aircraft.assigned_loadout = loadout

    return _finish(aircraft, asset_id, sensors)


def make_ship(block, asset_id: str, model: str, position, *,
              asset_type=None, sensors: Optional[Mapping[str, float]] = None) -> Ship:
    """`Ship` reale del registro `Ship_Data`, con id esplicito."""
    if asset_type is None:
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data
        record = Ship_Data._registry.get(model)
        asset_type = getattr(record, 'category', None)

    ship = Ship(block=block, name=asset_id, model=model, asset_type=asset_type,
                position=_point(position))

    return _finish(ship, asset_id, sensors)


# ── FORZE ─────────────────────────────────────────────────────────────────────

def make_force(force_id: str, side: str, mil_category: str = GROUND_UNIT, *,
               category: Optional[str] = None):
    """Forza vuota con id esplicito e stabile.

    Default: una `Military` di `mil_category` (v. `MILITARY_CATEGORY`). Con
    `category='Logistic'` un `Block` logistico generico (storico: era l'unico bersaglio
    non-militare costruibile prima della correzione di Transport/Storage/Urban/Production;
    per un blocco infrastrutturale vero usare `make_infrastructure`).
    """
    if category == LOGISTIC_CATEGORY:
        return Block(name=force_id, side=side, category=LOGISTIC_CATEGORY, id=force_id)

    return Military(mil_category=mil_category, name=force_id, side=side, id=force_id)


def add_assets(force, assets: Iterable):
    """Inserisce gli asset nella forza, per id. Restituisce la forza.

    Si usa il setter `Block.assets` (che valida la classe) e non `Block.set_asset`, che
    accetta solo istanze la cui classe si chiama esattamente 'Asset' e rifiuta quindi
    Vehicle/Aircraft/Ship (v. il report di Fase 7).
    """
    merged = dict(force.assets or {})

    for asset in assets:
        if asset.id in merged:
            raise ValueError(f"asset id {asset.id!r} already in force {force.id!r}")

        merged[asset.id] = asset

    force.assets = merged
    return force


# Classi di blocco infrastrutturale (non militari) costruibili, per nome.
INFRASTRUCTURE_CLASSES = {'Production': Production, 'Transport': Transport,
                          'Storage': Storage, 'Urban': Urban}

# Categoria di blocco di default per classe infrastrutturale (chiave di BLOCK_CATEGORY):
# 'Civilian' per l'area urbana, 'Logistic' per il resto. E' cio' che legge `role_of`
# ('logistic' per gli asset di un blocco logistico).
INFRASTRUCTURE_DEFAULT_CATEGORY = {'Production': LOGISTIC_CATEGORY, 'Transport': LOGISTIC_CATEGORY,
                                   'Storage': LOGISTIC_CATEGORY, 'Urban': 'Civilian'}


def make_infrastructure(block_class: str, force_id: str, side: str, sub_category: str, *,
                        category: Optional[str] = None):
    """Blocco infrastrutturale REALE (`Production`/`Transport`/`Storage`/`Urban`), vuoto.

    `sub_category` e' validata dal costruttore della classe contro
    `Context.BLOCK_INFRASTRUCTURE_ASSET[block_class]` (ValueError se fuori tabella).
    `category` di default da INFRASTRUCTURE_DEFAULT_CATEGORY. Id esplicito e stabile.
    """
    cls = INFRASTRUCTURE_CLASSES[block_class]
    category = INFRASTRUCTURE_DEFAULT_CATEGORY[block_class] if category is None else category
    return cls(name=force_id, side=side, category=category, sub_category=sub_category, id=force_id)


def make_structure(block, asset_id: str, position, *, category: Optional[str] = None,
                   asset_type: Optional[str] = None) -> Structure:
    """`Structure` reale (edificio, ponte, deposito, bunker), con id esplicito.

    `category`/`asset_type` sono la sotto-tabella e il tipo di
    `BLOCK_INFRASTRUCTURE_ASSET[block.block_class]` (es. 'Railway'/'Bridge' in un
    Transport, 'Farp'/'Parked_Helicopter' in una Military): `Structure` valida l'asset_type
    se la tabella esiste. Nessun sensore, nessuna arma: e' solo un bersaglio.
    """
    structure = Structure(block=block, name=asset_id, category=category, asset_type=asset_type,
                          position=_point(position))
    structure.id = asset_id
    return structure


@dataclass(frozen=True)
class Unit:
    """Gruppo di asset identici in fila lungo x (o lungo `step`), per `build_force`.

    Attributes:
        kind: 'vehicle' | 'aircraft' | 'ship'.
        model: chiave del registro.
        count: quanti.
        origin: posizione del primo (x, y[, z]); per gli aerei z di default
            DEFAULT_AIR_ALTITUDE.
        step: spostamento (dx, dy) fra due asset successivi.
        prefix: prefisso dell'id; id = f'{force_id}/{prefix}{i}'.
        sensors: sensore dichiarato (v. declare_sensor), None = solo registro.
        loadout: solo aerei.
    """
    kind: str
    model: str
    count: int = 1
    origin: Tuple[float, ...] = (0.0, 0.0)
    step: Tuple[float, float] = (200.0, 0.0)
    prefix: str = 'u'
    sensors: Optional[Mapping[str, float]] = field(default=None, hash=False)
    loadout: Optional[str] = None


def build_force(force_id: str, side: str, units: Sequence[Unit], *,
                mil_category: str = GROUND_UNIT, category: Optional[str] = None):
    """`make_force` + gli asset di `units`. Id asset: `f'{force_id}/{prefix}{i}'`."""
    force = make_force(force_id, side, mil_category, category=category)
    assets = []

    for unit in units:
        x0, y0, *rest = unit.origin

        for index in range(unit.count):
            asset_id = f'{force_id}/{unit.prefix}{index}'
            x, y = x0 + index * unit.step[0], y0 + index * unit.step[1]

            if unit.kind == 'vehicle':
                z = rest[0] if rest else 0.0
                assets.append(make_vehicle(force, asset_id, unit.model, (x, y, z),
                                           sensors=unit.sensors))
            elif unit.kind == 'aircraft':
                z = rest[0] if rest else DEFAULT_AIR_ALTITUDE
                assets.append(make_aircraft(force, asset_id, unit.model, (x, y, z),
                                            loadout=unit.loadout, sensors=unit.sensors))
            elif unit.kind == 'ship':
                z = rest[0] if rest else 0.0
                assets.append(make_ship(force, asset_id, unit.model, (x, y, z),
                                        sensors=unit.sensors))
            else:
                raise ValueError(f"unknown unit kind {unit.kind!r}")

    return add_assets(force, assets)


def asset_ids(force) -> List[str]:
    """Id degli asset della forza, ordinati."""
    return sorted(force.assets)


# ── ROTTE ─────────────────────────────────────────────────────────────────────

_ROUTE_TYPE_OF_PATH = {'air': 'air', 'offroad': 'ground', 'onroad': 'ground', 'water': 'water'}


def straight_route(points: Sequence[Sequence[float]], speed: float, name: str,
                   z: float = 0.0, path_type: str = 'air') -> Route:
    """`DataType.Route` reale su una spezzata di punti (x, y), archi alla stessa velocita' [m/s]."""
    if speed is None or speed <= 0:
        raise ValueError(f"speed must be positive, got {speed!r}")

    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(p[0], p[1], p[2] if len(p) > 2 else z),
                          obj_reference=None)
                 for i, p in enumerate(points)]
    edges = {}

    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type=path_type, danger_level=0.0,
                                       speed=speed, name=f'{name}-E{i}')

    return Route(route_type=_ROUTE_TYPE_OF_PATH[path_type], edges=edges, name=name)


def route_for(asset, points: Sequence[Sequence[float]], speed: Optional[float] = None,
              regime: str = 'nominal') -> Route:
    """Rotta dell'asset: parte dalla sua posizione e tocca `points`.

    Velocita' di default = il regime `regime` del profilo cinematico del registro (Fase 1,
    m/s); quota = quella dell'asset; tipo d'arco dalla classe (aereo 'air', nave 'water',
    veicolo 'offroad').
    """
    if speed is None:
        speed = (asset.speed or {}).get(regime)

    position = asset.position
    z = float(position.z)
    start = (float(position.x), float(position.y), z)
    path_type = {'Aircraft': 'air', 'Ship': 'water'}.get(type(asset).__name__, 'offroad')

    return straight_route([start] + [tuple(p) + ((z,) if len(p) == 2 else ()) for p in points],
                          speed=float(speed), name=f'route:{asset.id}', z=z, path_type=path_type)


def routes_for(force, points: Sequence[Sequence[float]], *, offset_with_position: bool = True,
               speed: Optional[float] = None) -> Dict[str, Route]:
    """Una rotta per ogni asset della forza verso `points`.

    Con `offset_with_position` ogni asset mantiene il proprio scostamento dal primo asset
    della forza (la formazione trasla invece di convergere su un punto).
    """
    ids = asset_ids(force)

    if not ids:
        return {}

    lead = force.assets[ids[0]].position
    routes = {}

    for asset_id in ids:
        asset = force.assets[asset_id]
        dx = float(asset.position.x - lead.x) if offset_with_position else 0.0
        dy = float(asset.position.y - lead.y) if offset_with_position else 0.0
        shifted = [(p[0] + dx, p[1] + dy, *p[2:]) for p in points]
        routes[asset_id] = route_for(asset, shifted, speed=speed)

    return routes


# ── MISSIONI ──────────────────────────────────────────────────────────────────

_DOMAIN_OF_CLASS = {'Aircraft': 'air', 'Ship': 'sea'}


def domain_of(asset) -> str:
    """Dominio di missione dell'asset: 'air' (Aircraft), 'sea' (Ship), 'ground' (il resto)."""
    return _DOMAIN_OF_CLASS.get(type(asset).__name__, 'ground')


def group_target(block_id: str, observed_at: float = 0.0) -> Target:
    """Bersaglio GROUP (un blocco) osservato all'istante `observed_at` [s dall'inizio sessione]."""
    return Target(kind=TargetKind.GROUP, target_id=block_id, provenance=TargetProvenance.OBSERVED,
                  observed_at=observed_at)


def zone_target(center: Sequence[float], radius_m: float) -> Target:
    """Bersaglio ZONE dichiarato dal pianificatore (centro (x, y[, z]), raggio [m])."""
    return Target(kind=TargetKind.ZONE, position=_point(center), radius_m=radius_m)


def _mission_waypoints(route: Route, domain: str) -> Tuple[MissionWaypoint, ...]:
    """Piano dei punti di una rotta di scenario: aria NAV ... LAND (semplificazione di scenario:
    rotta senza rientro, v. docstring), terra/mare DEPARTURE ... OBJECTIVE."""
    waypoints = route_waypoints(route)
    first, last = ((WaypointRole.NAV, WaypointRole.LAND) if domain == 'air'
                   else (WaypointRole.DEPARTURE, WaypointRole.OBJECTIVE))
    roles = [first] + [WaypointRole.NAV] * (len(waypoints) - 2) + [last]
    return tuple(MissionWaypoint(waypoint=wp, role=role) for wp, role in zip(waypoints, roles))


def _asset_role(domain: str, index: int) -> str:
    """Posizione in formazione (D3.c): il primo e' 'lead'; poi aria 'wingman'/'element_lead'
    alternati, terra/mare 'main'."""
    if index == 0:
        return 'lead'

    if domain == 'air':
        return 'element_lead' if index % 2 == 0 else 'wingman'

    return 'main'


def _xyz_points(route: Route) -> List[Tuple[float, float, float]]:
    return [(float(w.point.x), float(w.point.y), float(w.point.z)) for w in route_waypoints(route)]


def _offset_of(reference: Route, route: Route) -> Tuple[float, float, float]:
    """Offset (avanti, destra, alto) che porta il primo punto di `reference` sul primo di `route`,
    nella terna del primo tratto di `reference` (stessa convenzione di Mission_Adapter)."""
    ref, own = _xyz_points(reference), _xyz_points(route)
    dx, dy, dz = own[0][0] - ref[0][0], own[0][1] - ref[0][1], own[0][2] - ref[0][2]

    if dx == 0.0 and dy == 0.0:
        return 0.0, 0.0, dz

    hx, hy = ref[1][0] - ref[0][0], ref[1][1] - ref[0][1]
    norm = (hx * hx + hy * hy) ** 0.5
    hx, hy = hx / norm, hy / norm
    return dx * hx + dy * hy, dx * hy - dy * hx, dz


def _slowest_reference(reference: Route, routes: Sequence[Route]) -> Route:
    """Rotta di riferimento con, tratto per tratto, la velocita' minima fra le `routes` dei
    membri della missione (regola A). La stessa `reference` se e' gia' la piu' lenta ovunque;
    altrimenti una copia con gli stessi waypoint (stessi oggetti) e gli archi rallentati."""
    edges = list(reference.edges.values())
    slowest = [min(float(list(route.edges.values())[index].speed) for route in routes)
               for index in range(len(edges))]

    if all(float(edge.speed) == speed for edge, speed in zip(edges, slowest)):
        return reference

    slowed = {key: Edge(wpA=edge.wpA, wpB=edge.wpB, path_type=edge.path_type, danger_level=edge.danger_level,
                        speed=speed, name=edge.name)
              for (key, edge), speed in zip(reference.edges.items(), slowest)}
    return Route(route_type=reference.route_type, edges=slowed, name=reference.name)


def _scenario_mission(mission_id: str, force, domain: str, mission_type: str, target: Target,
                      reference: Route, assets: Sequence[MissionAsset]) -> Mission:
    return Mission(mission_id=mission_id, block_id=force.id, domain=domain, mission_type=mission_type,
                   target=target, assets=tuple(assets), route=reference,
                   waypoints=_mission_waypoints(reference, domain), start_time=0.0,
                   start_mode=StartMode.AIR if domain == 'air' else None)


def missions_for(force, points: Sequence[Sequence[float]], *, mission_type: str, target: Target,
                 name: Optional[str] = None, offset_with_position: bool = True,
                 speed: Optional[float] = None, only: Optional[Iterable[str]] = None) -> List[Mission]:
    """Le missioni con ESATTAMENTE la geometria di `routes_for(force, points, ...)`, ciascuna alla
    velocita' del suo mezzo piu' lento (regola A, F4a; v. docstring).

    Args:
        force: il blocco (tutti i suoi asset ricevono una missione).
        points/offset_with_position/speed: come `routes_for`.
        mission_type/target: tipo di missione del dominio e bersaglio (non ancora usato dal
            motore, F7).
        name: radice degli id di missione (default `<force.id>:<mission_type>`); con piu'
            missioni si aggiunge `-<n>`.
        only: se dato, solo questi asset (es. la parte strike e la parte scorta di un pacchetto,
            con tipi di missione diversi); gli offset restano quelli di `routes_for` sull'intera
            forza, quindi la geometria non cambia.

    Returns:
        Lista di `Mission` (start_time 0, aria `start_mode` AIR), una o piu' per blocco (piu'
        d'una solo per dominio diverso o per geometria non riducibile a un offset).
    """
    routes = routes_for(force, points, offset_with_position=offset_with_position, speed=speed)

    if only is not None:
        wanted = set(only)
        routes = {asset_id: route for asset_id, route in routes.items() if asset_id in wanted}

    root = name or f'{force.id}:{mission_type}'
    groups: List[Tuple[Route, List[Tuple[str, Tuple[float, float, float]]]]] = []

    for asset_id in sorted(routes):
        route = routes[asset_id]
        domain = domain_of(force.assets[asset_id])

        # Regola A (F4a): la velocita' non divide piu' le missioni, solo dominio e geometria.
        for reference, members in groups:
            if domain_of(force.assets[members[0][0]]) != domain:
                continue

            # L'offset e' accettato solo se l'adapter ridà ESATTAMENTE la rotta dell'asset.
            offset = _offset_of(reference, route)
            probe = _scenario_mission('probe', force, domain, mission_type, target, reference,
                                      (MissionAsset(asset_id, 'lead', *offset),))
            derived, _ = MA.asset_route(probe, probe.assets[0])

            if _xyz_points(derived) == _xyz_points(route):
                members.append((asset_id, offset))
                break
        else:
            groups.append((route, [(asset_id, (0.0, 0.0, 0.0))]))

    missions = []

    for index, (reference, members) in enumerate(groups):
        reference = _slowest_reference(reference, [routes[asset_id] for asset_id, _ in members])
        domain = domain_of(force.assets[members[0][0]])
        assets = []

        for position, (asset_id, offset) in enumerate(members):
            loadout = getattr(force.assets[asset_id], 'assigned_loadout', None) if domain == 'air' else None
            assets.append(MissionAsset(asset_id, _asset_role(domain, position), *offset,
                                       loadout=loadout if isinstance(loadout, str) else None))

        mission_id = root if len(groups) == 1 else f'{root}-{index + 1}'
        missions.append(_scenario_mission(mission_id, force, domain, mission_type, target, reference, assets))

    return missions


def mission_routes(missions: Iterable[Mission], t0: float = 0.0) -> Dict[str, Route]:
    """`{asset_id: Route}` delle missioni (per interrogare direttamente lo scheduler)."""
    return MA.mission_routes(missions, t0)


# ── FIRE CONTROL DI RIFERIMENTO ───────────────────────────────────────────────

# ShotSpec DICHIARATE DI TEST (v. docstring): ordini di grandezza plausibili, non calibrati,
# non da fonte. Gli scenari ne verificano solo l'effetto qualitativo.
SHOTS: Dict[str, ER.ShotSpec] = {
    'direct_fire': ER.ShotSpec(accuracy=0.55, destroy_capacity=0.5, rounds=1, weapon='test:direct_fire',
                               time_of_flight=1.5, cycle_time=10.0),
    'artillery':   ER.ShotSpec(accuracy=0.3, destroy_capacity=0.4, rounds=3, weapon='test:artillery',
                               time_of_flight=30.0, cycle_time=40.0),
    'sam':         ER.ShotSpec(accuracy=0.65, destroy_capacity=0.8, rounds=1, weapon='test:sam',
                               time_of_flight=15.0, cycle_time=12.0),
    'aaa':         ER.ShotSpec(accuracy=0.3, destroy_capacity=0.4, rounds=1, weapon='test:aaa',
                               time_of_flight=2.0, cycle_time=5.0),
    'aam':         ER.ShotSpec(accuracy=0.6, destroy_capacity=0.8, rounds=1, weapon='test:aam',
                               time_of_flight=20.0, cycle_time=15.0),
    'agm':         ER.ShotSpec(accuracy=0.7, destroy_capacity=0.6, rounds=1, weapon='test:agm',
                               time_of_flight=10.0, interceptable=True, cycle_time=15.0),
    'arm':         ER.ShotSpec(accuracy=0.8, destroy_capacity=0.8, rounds=1, weapon='test:anti_radiation',
                               time_of_flight=30.0, interceptable=True, cycle_time=15.0),
    'asm':         ER.ShotSpec(accuracy=0.6, destroy_capacity=0.6, rounds=2, weapon='test:anti_ship',
                               time_of_flight=60.0, interceptable=True, cycle_time=60.0),
    # Bombe a caduta libera / a guida laser (Mk-82/Mk-83, GBU-12 dei loadout 'Strike',
    # 'Laser Strike', 'Iron Bomb Strike'): NON intercettabili. Non e' nella tabella di
    # riferimento (che usa 'agm' per ogni aria-superficie, come in S1-S9): uno scenario la
    # usa esplicitamente quando il loadout e' di bombe (v. S12/S13 e il docstring di
    # Test_Session_Scenarios_S10_S18 sull'intercettazione R1, risolta dalla scorta di
    # intercettori distinta — Mobile.interceptor_stock, 2026-09-23).
    'bomb':        ER.ShotSpec(accuracy=0.5, destroy_capacity=0.7, rounds=2, weapon='test:bomb',
                               time_of_flight=25.0, interceptable=False, cycle_time=20.0),
}

_SURFACE = ('ground', 'artillery', 'sam', 'aaa', 'logistic', 'structure')

# Tabella di riferimento (ruolo tiratore, ruolo bersaglio) -> ShotSpec. Assente = None.
REFERENCE_FIRE_TABLE: Dict[Tuple[str, str], ER.ShotSpec] = {
    **{('ground', target): SHOTS['direct_fire'] for target in _SURFACE},
    **{('artillery', target): SHOTS['artillery'] for target in _SURFACE},
    ('sam', 'air'): SHOTS['sam'],
    ('aaa', 'air'): SHOTS['aaa'],
    ('sea', 'air'): SHOTS['sam'],
    ('sea', 'sea'): SHOTS['asm'],
    # 'air' = multiruolo: aria-aria e aria-superficie.
    ('air', 'air'): SHOTS['aam'],
    **{('air', target): SHOTS['agm'] for target in _SURFACE},
    ('air', 'sea'): SHOTS['asm'],
    # Ruoli di missione (imposti per id con `roles=`).
    ('fighter', 'air'): SHOTS['aam'],
    **{('strike', target): SHOTS['agm'] for target in ('ground', 'artillery', 'logistic', 'structure')},
    ('strike', 'sea'): SHOTS['asm'],
    ('sead', 'sam'): SHOTS['arm'],
    ('sead', 'aaa'): SHOTS['arm'],
}


def role_of(asset, roles: Optional[Mapping[str, str]] = None) -> Optional[str]:
    """Ruolo di un asset reale per la tabella di fuoco (v. docstring del modulo)."""
    if roles:
        imposed = roles.get(getattr(asset, 'id', None))

        if imposed is not None:
            return imposed

    kind = type(asset).__name__

    # Un sistema di difesa aerea resta 'sam'/'aaa' anche dentro un blocco logistico (difesa
    # organica di un impianto, S14): altrimenti come BERSAGLIO diventerebbe 'logistic' e un
    # ruolo 'strike' (per definizione "solo aria-suolo non-AD") lo attaccherebbe.
    if kind == 'Vehicle' and (asset.isSAM or asset.isAAA):
        return 'sam' if asset.isSAM else 'aaa'

    block = getattr(asset, 'block', None)
    is_logistic = getattr(block, 'is_logistic', None)

    if callable(is_logistic) and is_logistic():
        return 'logistic'

    if kind == 'Aircraft':
        return 'air'

    if kind == 'Ship':
        return 'sea'

    if kind == 'Vehicle':
        if asset.isSAM:
            return 'sam'
        if asset.isAAA:
            return 'aaa'
        if asset.isArtillery:
            return 'artillery'
        return 'ground'

    if kind == 'Structure':
        return 'structure'

    return None


def make_fire_control(table: Optional[Mapping[Tuple[str, str], Optional[ER.ShotSpec]]] = None, *,
                      roles: Optional[Mapping[str, str]] = None,
                      overrides: Optional[Mapping[str, Mapping[str, Optional[ER.ShotSpec]]]] = None
                      ) -> Callable:
    """`fire_control(shooter, target) -> ShotSpec | None` di riferimento per gli scenari.

    Args:
        table: `(ruolo tiratore, ruolo bersaglio) -> ShotSpec | None`; default
            REFERENCE_FIRE_TABLE.
        roles: `{asset_id: ruolo}` imposti (es. 'sead', 'strike', 'fighter').
        overrides: `{shooter_id: {ruolo bersaglio: ShotSpec | None}}`, prioritari sulla
            tabella (un None esplicito vieta l'ingaggio).

    Pura e deterministica: dipende solo dagli argomenti e dal tipo/id degli asset.
    """
    table = dict(REFERENCE_FIRE_TABLE if table is None else table)
    roles = dict(roles or {})
    overrides = {key: dict(value) for key, value in (overrides or {}).items()}

    def fire_control(shooter, target):
        # I ruoli di missione descrivono cosa un asset FA quando spara, non cosa E' come
        # bersaglio: il bersaglio e' sempre classificato per dominio (un 'strike' e' un
        # 'air' per un SAM).
        target_role = role_of(target)
        by_shooter = overrides.get(getattr(shooter, 'id', None))

        if by_shooter is not None and target_role in by_shooter:
            return by_shooter[target_role]

        return table.get((role_of(shooter, roles), target_role))

    return fire_control


# ── ESECUZIONE ────────────────────────────────────────────────────────────────

def make_order(session_id: str, duration: float, t_start: float = 0.0, **kwargs) -> SessionOrder:
    """`SessionOrder` chiuso `[t_start, t_start + duration]`."""
    return SessionOrder(session_id, t_start=float(t_start), t_end=float(t_start + duration), **kwargs)


def run(session_id: str, forces_a, forces_b, fire_control: Callable, *, duration: float,
        t_start: float = 0.0, missions: Iterable[Mission] = (), order_kwargs: Optional[Mapping] = None,
        **run_kwargs) -> SessionOutcome:
    """`make_order` (con le `missions`) + `Session_Simulator.run_session`. `run_kwargs` passati
    tali e quali."""
    order = make_order(session_id, duration, t_start, missions=tuple(missions), **dict(order_kwargs or {}))
    return SS.run_session(order, list(forces_a), list(forces_b), fire_control, **run_kwargs)


def timed(function: Callable, *args, **kwargs):
    """`(risultato, secondi)` — per i test di scala (S8)."""
    started = _time.perf_counter()
    result = function(*args, **kwargs)
    return result, _time.perf_counter() - started


# ── SCENARIO: CONTENITORE E SCENARIO DI RIFERIMENTO ───────────────────────────

@dataclass
class Scenario:
    """Uno scenario pronto da eseguire: forze dei due lati, missioni, fire_control, durata.

    `run(session_id, **kwargs)` chiama `run_session` (gli asset vengono MUTATI: per una
    replica si ricostruisce lo scenario, non lo si riesegue). `kwargs` vanno a
    `run_session` (thresholds, detection_factor, ...).
    """
    forces_a: List
    forces_b: List
    missions: List[Mission]
    fire_control: Callable
    duration: float
    roles: Dict[str, str] = field(default_factory=dict)

    @property
    def forces(self) -> List:
        return list(self.forces_a) + list(self.forces_b)

    @property
    def routes(self) -> Dict[str, Route]:
        """Rotte per asset ricavate dalle missioni (sola lettura)."""
        return mission_routes(self.missions)

    def force(self, force_id: str):
        for candidate in self.forces:
            if candidate.id == force_id:
                return candidate
        raise KeyError(force_id)

    def run(self, session_id: str, **kwargs) -> SessionOutcome:
        return run(session_id, self.forces_a, self.forces_b, self.fire_control,
                   duration=self.duration, missions=self.missions, **kwargs)


def combined_arms_scenario(*, with_cas: bool = True, blue_tanks: int = 3, blue_ifv: int = 2,
                           red_ifv: int = 3) -> Scenario:
    """Composizione di S1 (combined arms con CAS), riusata da S9, determinismo e agnosticismo.

    Lato A (Blue), in attacco da ovest verso est:
      * 'Blue-Armor' — `blue_tanks` M1A2-Abrams + `blue_ifv` M2-Bradley, in movimento;
      * 'Blue-CAS' (se `with_cas`) — 2 A-10C con loadout 'Maverick/Gun CAS', ruolo 'strike'
        (solo bersagli terrestri non-AD: il CAS non fa SEAD).
    Lato B (Red), in difesa, fermo:
      * 'Red-Line' — `red_ifv` BMP-2 in linea, 1 obice 2S19-Msta arretrato, 1 ZSU-23-4
        Shilka (AAA) e 1 9K35 Strela-10 (SAM a corto raggio): meccanizzata + artiglieria +
        AAA/VSHORAD.
    Carri, corazzati e artiglieria hanno i sensori dichiarati di test (v. docstring).
    """
    visual = {'ground': DECLARED_GROUND_VISUAL_RANGE}
    blue_units = [Unit('vehicle', 'M1A2-Abrams', blue_tanks, origin=(-8_000.0, 0.0), step=(0.0, 300.0),
                       prefix='mbt', sensors=visual)]

    if blue_ifv:
        blue_units.append(Unit('vehicle', 'M2-Bradley', blue_ifv, origin=(-8_300.0, 150.0), step=(0.0, 300.0),
                               prefix='ifv', sensors=visual))

    blue = build_force('Blue-Armor', 'Blue', blue_units)
    red = build_force('Red-Line', 'Red', [
        Unit('vehicle', 'BMP-2', red_ifv, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=visual),
        Unit('vehicle', '2S19-Msta', 1, origin=(6_000.0, 300.0), prefix='art',
             sensors={'ground': DECLARED_ARTILLERY_OBSERVATION_RANGE}),
        Unit('vehicle', 'ZSU-23-4-Shilka', 1, origin=(1_000.0, 600.0), prefix='aaa'),
        Unit('vehicle', '9K35-Strela-10', 1, origin=(1_000.0, -300.0), prefix='sam')])

    forces_a = [blue]
    # Attacco terrestre sulla linea Red: una missione M1A2 + M2 alla velocita' del piu' lento
    # (regola A, F4a; in F3 le velocita' diverse ne facevano due).
    missions = missions_for(blue, [(2_000.0, 0.0)], mission_type='Attack', target=group_target('Red-Line'))
    roles: Dict[str, str] = {}

    if with_cas:
        cas = build_force('Blue-CAS', 'Blue', [
            Unit('aircraft', 'A-10C Thunderbolt II', 2, origin=(-60_000.0, 0.0, 3_000.0), step=(0.0, 500.0),
                 prefix='cas', loadout='Maverick/Gun CAS')], mil_category=AIR_UNIT)
        forces_a.append(cas)
        missions += missions_for(cas, [(10_000.0, 0.0)], mission_type='CAS', target=group_target('Red-Line'))
        roles.update({asset_id: 'strike' for asset_id in cas.assets})

    return Scenario(forces_a=forces_a, forces_b=[red], missions=missions,
                    fire_control=make_fire_control(roles=roles), duration=3_600.0, roles=roles)


# ── LETTURE DELL'ESITO (solo letture, nessun ricalcolo) ───────────────────────

def force_outcome(outcome: SessionOutcome, force_id: str) -> Optional[ER.ForceOutcome]:
    """L'esito della forza nel suo (unico, per costruzione) ingaggio, None se non ha combattuto."""
    found = outcome.outcomes_of(force_id)
    return found[0] if found else None


def losses_of(outcome: SessionOutcome, force_id: str) -> int:
    """Asset impegnati e non piu' operativi a fine ingaggio (ForceOutcome.lost), 0 se assente."""
    found = force_outcome(outcome, force_id)
    return found.lost if found is not None else 0


def damage_on(outcome: SessionOutcome, target_ids: Iterable[str]) -> List:
    """DamageEvent subiti dagli asset `target_ids`."""
    wanted = set(target_ids)
    return [event for event in outcome.damage_events if event.target_id in wanted]


def damage_by_source(outcome: SessionOutcome, source_ids: Iterable[str]) -> List:
    """DamageEvent inflitti dai tiratori `source_ids`."""
    wanted = set(source_ids)
    return [event for event in outcome.damage_events if event.source_id in wanted]


def salvo_shooters(outcome: SessionOutcome) -> Dict[str, float]:
    """`{asset_id: istante del primo lancio}` dagli AmmunitionEvent (solo salve offensive)."""
    first: Dict[str, float] = {}

    for event in outcome.ammunition_events:
        if event.asset_id not in first:
            first[event.asset_id] = event.time

    return first


def interceptions_by(outcome: SessionOutcome, asset_ids: Optional[Iterable[str]] = None) -> List:
    """InterceptionEvent effettuati dagli intercettori `asset_ids` (tutti se None).

    Dal 2026-09-23 le intercettazioni sono un tipo a parte (`ER.InterceptionEvent`, in
    `SessionOutcome.interception_events`), non piu' AmmunitionEvent con un `purpose`.
    """
    if asset_ids is None:
        return list(outcome.interception_events)

    wanted = set(asset_ids)
    return [event for event in outcome.interception_events if event.asset_id in wanted]


def interceptions_on(outcome: SessionOutcome, force_id: str) -> List:
    """InterceptionEvent a difesa della forza `force_id` (quelli che hanno protetto lei)."""
    return [event for event in outcome.interception_events if event.force_id == force_id]


def active_assets(outcome: SessionOutcome) -> set:
    """Asset che hanno consumato una scorta: tiratori di salve O intercettori."""
    return ({event.asset_id for event in outcome.ammunition_events}
            | {event.asset_id for event in outcome.interception_events})


def health_map(forces: Iterable) -> Dict[str, int]:
    """`{asset_id: salute attuale}` degli asset delle forze (stato reale, gia' mutato)."""
    return {asset_id: asset.health for force in forces for asset_id, asset in force.assets.items()}
