"""Fire control dai registri d'arma — **con che cosa spara un tiratore contro un bersaglio**.

Passo B2 del motore di sessioni virtuali (v. [[project_virtual_session_engine_design]] e la
proposta B1 `Analysis/Document/Proposta_Efficacia_Antiaerea.md`, approvata dall'utente il
2026-09-24). Il risolutore d'ingaggio (`Logic/Engagement_Resolver.py`) riceve la dottrina
di fuoco come funzione iniettata `fire_control(shooter, target) -> ShotSpec | None`; fino a
qui l'unica implementazione era la tabella a ruoli di test (`Test/Scenario_Fixtures.py`).
Questo modulo ne fornisce una che legge i registri veri:

    fire_control = make_registry_fire_control()
    run_session(order, forces, routes, fire_control, ...)

Il motore (`Engagement_Resolver`, `Session_Simulator`) NON e' modificato e il contratto
`ShotSpec` e' invariato.

## La catena, per ogni coppia (tiratore, bersaglio)

1. **Armi candidate del tiratore.**
   * `Vehicle`: `Vehicle_Data._registry[model].weapons` -> `GROUND_WEAPONS`;
   * `Ship`: `Ship_Data._registry[model].weapons` -> `SHIP_WEAPONS`;
   * `Aircraft`: i piloni del loadout ASSEGNATO (`Aircraft.assigned_loadout` ->
     `AIRCRAFT_LOADOUTS[model][loadout]['stores']['pylons']`) -> `AIR_WEAPONS`. Il cannone
     di bordo (`stores['gun_rounds']`) non ha un modello d'arma e non e' candidato. Senza
     loadout assegnato l'aereo non ha armi candidate.
   * qualunque altro asset (`Structure`, ...): nessuna arma, quindi None.
2. **Chiave del bersaglio** (classe, dimensione):
   * aereo in volo: la sottoclasse di `Context.get_air_target_class` (dalla category del
     modello piu' i campi `ground_fire_armored`/`air_target_class` del registro) e, se
     l'arma non ha quella riga, il fallback `'Aircraft'` (che e' anche l'unica riga delle
     tabelle aria-aria);
   * ogni altro bersaglio: `get_weapon_target_class(get_target_classification(asset_type))`,
     la stessa catena degli scorer di pianificazione. Nessuna classificazione -> None;
   * dimensione: `Context.classify_asset_dimension`; se non determinabile,
     FALLBACK_DIMENSION.
3. **Filtro di adeguatezza.**
   * bersaglio aereo: l'arma deve avere una riga aerea nel proprio template (le righe aeree
     sono state aggiunte SOLO ai template delle armi che possono colpire aerei: e' il
     template stesso a dire se l'arma e' antiaerea). Un cannone da carro o un ATGM non ha
     righe aeree e non e' mai candidato contro un aereo;
   * bersaglio di superficie: l'arma deve avere almeno un task che NON sia puramente
     antiaereo (AIR_ONLY_TASKS). Un SAM (task ['Anti_Air']) o un AAM (['A2A']) non spara
     mai a un bersaglio di superficie, anche se il suo template ha righe terrestri
     (quelle dei SAM sono dichiarate "inutili" nei registri). E' lo stesso discriminante
     di `Mobile.combat_range` (task Anti_Air), rilassato per le armi a doppio impiego: un
     cannone navale da 76 mm (Anti_Air + Anti_Ship) o un cannone AA (Anti_Air +
     Infantry_Support) puo' sparare anche a superficie, mentre `combat_range` li esclude.
   * Pk = accuracy x destroy_capacity > 0.
4. **Filtro di quota** (solo bersagli aerei, v. "Quota" sotto).
5. **Scelta.** Massima Pk = accuracy x destroy_capacity; a parita', tie-break
   deterministico sul nome del modello d'arma (poi sul tipo). I valori sono letti GREZZI da
   `efficiency[classe][dimensione]`: mai gli scorer (`calc_weapon_efficiency` usa il modulo
   `random` globale e romperebbe il determinismo di sessione).

## Quota

La quota corrente di un asset e' `asset.position.z` [m] (Point3D): e' la stessa che usano
`Mobile.air_defense_volume` (base del cilindro = z del tiratore + min_altitude) e le rotte
aeree degli scenari (waypoint alla quota di volo). Il motore NON aggiorna `position`
durante la sessione (le rotte sono consumate dal Contact_Scheduler, non scritte
sull'asset): la quota letta e' quindi quella di partenza, che per un aereo in rotta a quota
costante coincide con la quota di volo. Unita' dei registri, verificate:

* Ground_Weapon_Data e Ship_Weapon_Data: `min_altitude`/`max_altitude` in METRI, relativi
  al tiratore (stessa convenzione di `air_defense_volume`): il filtro confronta
  `target.z - shooter.z`;
* Aircraft_Weapon_Data: `max_height` in KM, quota assoluta: il filtro confronta
  `target.z` con `max_height x 1000`;
* armi senza dati di quota (CIWS, cannoni navali, autocannoni, HMG; armi di bordo senza
  `max_height`): la quota relativa non puo' superare la portata dell'arma (di tiro diretto
  per le armi terrestri). E' un limite
  geometrico derivato dal registro (una traiettoria non sale oltre la propria portata),
  non una costante stimata.

Se la posizione del tiratore o del bersaglio non e' disponibile il filtro NON viene
applicato (dichiarato: meglio un'arma forse fuori inviluppo che un asset reso inerme per
mancanza di dato, stessa politica "None = non modellato" di munizioni e carburante).

## Campi derivati della ShotSpec (costanti STIMATE, dichiarate qui sotto)

* `weapon`: nome del modello d'arma.
* `max_range` [m] (controllo di portata del risolutore, 2026-09-24): la portata del
  registro convertita in metri (Ground in m, Ship e Air in km). Contro un bersaglio aereo,
  per le armi terrestri, la portata di tiro DIRETTO (`range['direct']`), non quella
  indiretta; contro la superficie la maggiore delle due. None quando il registro non
  dichiara una portata (le bombe di Aircraft_Weapon_Data non hanno `range`): per
  quell'arma nessun vincolo di portata, dichiarato.
* `interceptable`: True per missili (SAM, AAM, ASM, ATGM) e bombe guidate
  (`type == 'Guided bombs'`); False per proiettili, razzi non guidati, bombe a caduta
  libera e siluri (le difese di salva sono SAM/cannoni AA, che non intercettano un siluro).
* `time_of_flight`: ENGAGEMENT_RANGE_FRACTION x max_range / velocita' dell'arma quando il
  registro da' entrambe, altrimenti DEFAULT_TIME_OF_FLIGHT_S per categoria. La distanza
  vera di tiro non e' nota alla fire control (la calcola il risolutore, dopo).
* `rounds` / `cycle_time`: per le armi a tiro rapido (fire_rate >=
  AUTOMATIC_FIRE_RATE_RPM) un colpo della ShotSpec e' una RAFFICA (le righe dei template
  dei cannoni AA/CIWS/HMG sono per raffica) e `cycle_time` = GUN_BURST_ROUNDS x 60 /
  fire_rate; per le armi a tiro singolo (cannoni da carro, artiglieria, cannoni navali
  lenti) un colpo e' un proietto e `cycle_time` = 60 / fire_rate. Per missili, bombe,
  razzi e siluri `rounds` = SALVO_ROUNDS per categoria e `cycle_time` None (intervallo
  del profilo di reazione).

## Memoizzazione

La scelta e' una funzione PURA di (tiratore: classe, modello, loadout; bersaglio: chiave,
dimensione; quote). Ogni fire control creata da `make_registry_fire_control` ha una propria
cache per quella chiave: nessuno stato che dipenda dall'ordine delle chiamate, quindi il
determinismo non cambia (due run con lo stesso seed restano identiche, cache calda o
fredda). Le armi candidate sono memoizzate per (classe, modello, loadout).

## Cosa NON fa

- Non modula la Pk con la posizione nell'inviluppo (distanza, aspetto): valori di template.
- Non conta le munizioni per arma: la scorta e' il contatore aggregato di `Mobile`, e per
  le armi a raffica il risolutore consuma 1 unita' per raffica (sottostima dichiarata).
- Non distingue stealth, contromisure o ECM (materia del rilevamento).
- Nessun componente LLM, in nessuna forma; nessun uso del modulo `random`.
"""

from typing import Callable, Dict, List, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import AIR_WEAPONS
from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import GROUND_WEAPONS
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data
from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS
from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver import ShotSpec
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name=__name__, class_name='Fire_Control').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Task puramente antiaerei: un'arma i cui task sono TUTTI qui non spara a superficie.
# 'A2A' e' il task degli AAM di Aircraft_Weapon_Data; gli altri quelli di Ground/Ship.
AIR_ONLY_TASKS = frozenset({'Anti_Air', 'Anti_Missile', 'Anti_Ballistic', 'A2A'})

# Dimensione usata quando classify_asset_dimension non sa classificare il bersaglio
# (caratteristiche fisiche mancanti, Structure senza categoria). STIMA: la classe centrale,
# che nei template ha valori intermedi fra big e small.
FALLBACK_DIMENSION = 'med'

# Frazione della portata massima a cui si assume avvenga l'ingaggio, per il tempo di volo.
# STIMA non tarata: la fire control non conosce la distanza reale di tiro.
ENGAGEMENT_RANGE_FRACTION = 0.5

# Tempo di volo [s] quando il registro non da' portata e velocita'. STIME non tarate,
# ordine di grandezza: missile a meta' portata (~10-20 s), proietto d'arma automatica
# (~1-3 s), razzo d'artiglieria (~20-40 s), bomba sganciata da quota media (~20-30 s),
# siluro a ~40 kt su ~6 km (~300 s).
DEFAULT_TIME_OF_FLIGHT_S = {'missile': 15.0, 'gun': 2.0, 'rocket': 20.0, 'bomb': 25.0, 'torpedo': 300.0}

# Colpi per salva per le armi non a tiro rapido. STIME non tarate: 2 missili (dottrina
# "shoot-shoot" dei SAM e lancio doppio degli AAM a lungo raggio), 2 bombe, 4 razzi (una
# frazione di un lanciatore/pod), 1 siluro; per i cannoni un colpo = un proietto o una
# raffica (v. docstring).
SALVO_ROUNDS = {'missile': 2, 'bomb': 2, 'rocket': 4, 'torpedo': 1, 'gun': 1}

# Soglia [colpi/min] oltre la quale un'arma e' a tiro rapido e un colpo della ShotSpec e'
# una raffica. STIMA: separa i cannoni AA/autocannoni/mitragliatrici (>= 240 colpi/min) dai
# cannoni da carro, artiglieria e cannoni navali (<= 120 colpi/min).
AUTOMATIC_FIRE_RATE_RPM = 200.0

# Colpi di una raffica di un'arma a tiro rapido, per il cycle_time. STIMA non tarata, dello
# stesso ordine di ROUNDS_PER_GUN_INTERCEPT di Mobile (100) ma per un tiro offensivo
# (raffiche piu' brevi): 2A38M a 5000 colpi/min -> 0.6 s, S-68 a 240 -> 12.5 s.
GUN_BURST_ROUNDS = 50

# Velocita' del suono al livello del mare [m/s], per i max_speed in Mach degli AAM di
# Aircraft_Weapon_Data (gli ASM lo danno in m/s; atmosfera standard ISA a 15 °C: e' una
# definizione, non una stima).
SPEED_OF_SOUND_MS = 340.3

# Nodo -> m/s (definizione): la velocita' dei siluri di Ship_Weapon_Data e' in nodi.
KNOT_MS = 1852.0 / 3600.0

# Categoria balistica di ogni tipo d'arma dei registri, per dominio del tiratore.
_KIND_BY_TYPE = {
    'ground': {'MISSILES': 'missile', 'ROCKETS': 'rocket', 'AA_CANNONS': 'gun', 'AUTO_CANNONS': 'gun',
               'CANNONS': 'gun', 'ARTILLERY': 'gun', 'MORTARS': 'gun', 'MACHINE_GUNS': 'gun',
               'GRENADE_LAUNCHERS': 'gun'},
    'ship': {'MISSILES_SAM': 'missile', 'MISSILES_ASM': 'missile', 'MISSILES_TORPEDO': 'torpedo',
             'GUNS': 'gun', 'CIWS': 'gun'},
    'air': {'MISSILES_AAM': 'missile', 'MISSILES_ASM': 'missile', 'BOMBS': 'bomb', 'ROCKETS': 'rocket',
            'CANNONS': 'gun', 'MACHINE_GUNS': 'gun'},
}


# ── ARMI CANDIDATE ────────────────────────────────────────────────────────────

class _Weapon:
    """Un'arma candidata: dati del registro gia' normalizzati in unita' SI."""

    __slots__ = ('model', 'weapon_type', 'domain', 'kind', 'data', 'range_m', 'air_range_m', 'speed_ms',
                 'fire_rate', 'min_alt', 'max_alt', 'max_height_m', 'tasks')

    def __init__(self, model: str, weapon_type: str, domain: str, data: Dict):
        self.model = model
        self.weapon_type = weapon_type
        self.domain = domain
        self.kind = _KIND_BY_TYPE[domain].get(weapon_type, 'gun')
        self.data = data
        self.range_m = _range_m(domain, data)
        self.air_range_m = _air_range_m(domain, data, self.range_m)
        self.speed_ms = _speed_ms(domain, weapon_type, data)
        self.fire_rate = _positive(data.get('fire_rate'))
        self.min_alt = _number(data.get('min_altitude'))
        self.max_alt = _number(data.get('max_altitude'))
        max_height = _positive(data.get('max_height'))
        self.max_height_m = max_height * 1000.0 if max_height is not None else None  # km -> m
        tasks = data.get('task')
        self.tasks = frozenset(tasks) if isinstance(tasks, (list, tuple, set, frozenset)) else None

    @property
    def efficiency(self) -> Dict:
        efficiency = self.data.get('efficiency')
        return efficiency if isinstance(efficiency, dict) else {}


def _number(value) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _positive(value) -> Optional[float]:
    value = _number(value)
    return value if value is not None and value > 0 else None


def _range_m(domain: str, data: Dict) -> Optional[float]:
    """Portata massima [m]: Ground in metri (dict direct/indirect o numero), Ship e Air in km."""
    raw = data.get('range')

    if isinstance(raw, dict):
        values = [v for v in (_number(raw.get('direct')), _number(raw.get('indirect'))) if v is not None]
        value = max(values) if values else None
    else:
        value = _number(raw)

    if value is None or value <= 0:
        return None

    return value if domain == 'ground' else value * 1000.0


def _air_range_m(domain: str, data: Dict, range_m: Optional[float]) -> Optional[float]:
    """Portata [m] contro bersagli aerei: per Ground la portata di tiro DIRETTO se c'e'
    (un cannone AA S-68 ha 'indirect' 12 km per il tiro contro superficie, ma ingaggia un
    aereo a vista entro 'direct' 4 km); per Ship/Air l'unica portata del registro."""
    raw = data.get('range')

    if domain == 'ground' and isinstance(raw, dict):
        direct = _positive(raw.get('direct'))

        if direct is not None:
            return direct

    return range_m


def _speed_ms(domain: str, weapon_type: str, data: Dict) -> Optional[float]:
    """Velocita' dell'arma/proietto [m/s], nelle unita' di ogni registro (v. commenti costanti)."""
    if domain == 'ship' and weapon_type == 'MISSILES_TORPEDO':
        speed = _positive(data.get('speed'))
        return speed * KNOT_MS if speed is not None else None

    speed = _positive(data.get('speed')) or _positive(data.get('muzzle_speed'))

    if speed is None and domain == 'air':
        # Unita' di `max_speed` in Aircraft_Weapon_Data (v. WEAPON_PARAM di quel modulo):
        # Mach per gli AAM, m/s per gli ASM (AGM-65D: 320).
        max_speed = _positive(data.get('max_speed'))

        if max_speed is not None:
            speed = max_speed * SPEED_OF_SOUND_MS if weapon_type == 'MISSILES_AAM' else max_speed

    return speed


def _shooter_key(shooter) -> Optional[Tuple[str, str, Optional[str]]]:
    """(classe, modello, loadout) del tiratore, o None se non ha un modello."""
    model = getattr(shooter, '_model', None)

    if not isinstance(model, str):
        return None

    class_name = type(shooter).__name__
    loadout = getattr(shooter, 'assigned_loadout', None) if class_name == 'Aircraft' else None
    return class_name, model, loadout


def _candidate_weapons(shooter_key: Tuple[str, str, Optional[str]]) -> Tuple[_Weapon, ...]:
    """Armi candidate di un tiratore, in ordine deterministico (tipo, modello)."""
    class_name, model, loadout = shooter_key
    weapons: List[_Weapon] = []

    if class_name == 'Aircraft':
        stores = (AIRCRAFT_LOADOUTS.get(model, {}).get(loadout) or {}).get('stores') if loadout else None
        pylons = (stores or {}).get('pylons') or {}
        seen = set()

        for item in pylons.values():
            if not isinstance(item, (list, tuple)) or len(item) < 2 or not isinstance(item[0], str):
                continue

            name = item[0]

            if name in seen:
                continue

            for weapon_type, db in AIR_WEAPONS.items():
                if name in db:
                    weapons.append(_Weapon(name, weapon_type, 'air', db[name]))
                    seen.add(name)
                    break  # serbatoi e pod non sono in AIR_WEAPONS: saltati

    else:
        if class_name == 'Ship':
            record, db_root, domain = Ship_Data._registry.get(model), SHIP_WEAPONS, 'ship'
        elif class_name == 'Vehicle':
            record, db_root, domain = Vehicle_Data._registry.get(model), GROUND_WEAPONS, 'ground'
        else:
            return ()

        registry_weapons = getattr(record, 'weapons', None)

        if not isinstance(registry_weapons, dict):
            return ()

        for weapon_type, weapon_list in registry_weapons.items():
            db = db_root.get(weapon_type, {})

            for item in weapon_list or []:
                if not isinstance(item, (list, tuple)) or not item or not isinstance(item[0], str):
                    continue

                data = db.get(item[0])

                if isinstance(data, dict):
                    weapons.append(_Weapon(item[0], weapon_type, domain, data))

    weapons.sort(key=lambda w: (w.weapon_type, w.model))
    return tuple(weapons)


# ── CHIAVE DEL BERSAGLIO ──────────────────────────────────────────────────────

def air_target_class_of(target) -> str:
    """Classe di bersaglio aereo (Context.AIR_TARGET_CLASSES) di un Aircraft in volo.

    Dal registro del modello (category + ground_fire_armored + air_target_class); senza
    record, dal solo `asset_type` dell'istanza (ruolo), senza flag ne' override.
    """
    record = Aircraft_Data._registry.get(getattr(target, '_model', None))

    if record is None:
        return Context.get_air_target_class(getattr(target, 'asset_type', None))

    return Context.get_air_target_class(record.category,
                                        armored=bool(getattr(record, 'ground_fire_armored', False)),
                                        override=getattr(record, 'air_target_class', None))


def target_key(target) -> Optional[Tuple[Tuple[str, ...], str, bool]]:
    """(chiavi di efficacia in ordine di ricerca, dimensione, e' aereo) del bersaglio.

    None se il bersaglio non ha una classificazione (non si spara a cio' che non si sa
    classificare: stessa semantica ROE di una fire control che restituisce None).
    """
    try:
        dimension = Context.classify_asset_dimension(target)
    except ValueError:
        dimension = None

    if dimension not in Context.DIMENSION_CLASSES:
        logger.debug(f"target_key: dimension of {getattr(target, 'id', None)!r} not classifiable "
                     f"({dimension!r}), using FALLBACK_DIMENSION {FALLBACK_DIMENSION!r}")
        dimension = FALLBACK_DIMENSION

    if type(target).__name__ == 'Aircraft':
        air_class = air_target_class_of(target)
        keys = (air_class,) if air_class == Context.AIR_TARGET_CLASS_AIRCRAFT \
            else (air_class, Context.AIR_TARGET_CLASS_AIRCRAFT)
        return keys, dimension, True

    asset_type = getattr(target, 'asset_type', None)
    classification = Context.get_target_classification(asset_type) if isinstance(asset_type, str) else None

    if classification is None:
        logger.debug(f"target_key: no target classification for {getattr(target, 'id', None)!r} "
                     f"(asset_type {asset_type!r}), no shot")
        return None

    return (Context.get_weapon_target_class(classification),), dimension, False


# ── FILTRI E SCELTA ───────────────────────────────────────────────────────────

def _z(asset) -> Optional[float]:
    position = getattr(asset, 'position', None)

    if position is None:
        return None

    try:
        return float(position.z)
    except (AttributeError, TypeError, ValueError):
        return None


def in_altitude_envelope(weapon: _Weapon, shooter_z: Optional[float], target_z: Optional[float]) -> bool:
    """True se il bersaglio aereo e' nell'inviluppo di quota dell'arma (v. "Quota").

    Quota non disponibile (tiratore o bersaglio senza posizione): nessun filtro, True.
    """
    if target_z is None:
        return True

    if weapon.domain == 'air':
        if weapon.max_height_m is not None:
            return target_z <= weapon.max_height_m

        if shooter_z is None or weapon.air_range_m is None:
            return True

        return abs(target_z - shooter_z) <= weapon.air_range_m

    if shooter_z is None:
        return True

    relative = target_z - shooter_z

    if weapon.min_alt is not None and weapon.max_alt is not None:
        return weapon.min_alt <= relative <= weapon.max_alt

    if weapon.air_range_m is None:
        return True

    return relative <= weapon.air_range_m


def _surface_capable(weapon: _Weapon) -> bool:
    """Un'arma spara a superficie se ha almeno un task non puramente antiaereo (o nessun task)."""
    return not weapon.tasks or not weapon.tasks <= AIR_ONLY_TASKS


def _cell(weapon: _Weapon, keys: Tuple[str, ...], dimension: str) -> Optional[Tuple[float, float]]:
    """(accuracy, destroy_capacity) grezzi della prima chiave presente nel template."""
    efficiency = weapon.efficiency

    for key in keys:
        row = efficiency.get(key)

        if isinstance(row, dict):
            cell = row.get(dimension)

            if isinstance(cell, dict):
                accuracy = _number(cell.get('accuracy'))
                destroy_capacity = _number(cell.get('destroy_capacity'))

                if accuracy is None or destroy_capacity is None:
                    return None

                return accuracy, destroy_capacity

    return None


def select_weapon(weapons: Tuple[_Weapon, ...], keys: Tuple[str, ...], dimension: str, is_air: bool,
                  shooter_z: Optional[float] = None, target_z: Optional[float] = None,
                  altitude_filter: bool = True) -> Optional[Tuple[_Weapon, float, float]]:
    """Arma con la massima Pk = accuracy x destroy_capacity fra quelle adatte, o None.

    Tie-break deterministico: nome del modello, poi tipo d'arma.
    """
    best = None
    best_sort_key = None

    for weapon in weapons:
        if not is_air and not _surface_capable(weapon):
            continue

        cell = _cell(weapon, keys, dimension)

        if cell is None:
            continue

        accuracy, destroy_capacity = cell
        pk = accuracy * destroy_capacity

        if pk <= 0.0:
            continue

        if is_air and altitude_filter and not in_altitude_envelope(weapon, shooter_z, target_z):
            continue

        sort_key = (-pk, weapon.model, weapon.weapon_type)

        if best_sort_key is None or sort_key < best_sort_key:
            best, best_sort_key = (weapon, accuracy, destroy_capacity), sort_key

    return best


def shot_spec_for(weapon: _Weapon, accuracy: float, destroy_capacity: float, is_air: bool = False) -> ShotSpec:
    """ShotSpec della scelta, con i campi derivati del docstring del modulo.

    `max_range` = portata del registro (contro un aereo quella di tiro diretto, v.
    `_air_range_m`); None se il registro non la dichiara (bombe a caduta di
    Aircraft_Weapon_Data): nessun vincolo di portata per quell'arma.
    """
    kind = weapon.kind
    max_range = weapon.air_range_m if is_air else weapon.range_m

    if kind == 'missile':
        interceptable = True
    elif kind == 'bomb':
        interceptable = weapon.data.get('type') == 'Guided bombs'
    else:
        interceptable = False

    if max_range is not None and weapon.speed_ms is not None:
        time_of_flight = ENGAGEMENT_RANGE_FRACTION * max_range / weapon.speed_ms
    else:
        time_of_flight = DEFAULT_TIME_OF_FLIGHT_S[kind]

    cycle_time = None

    if kind == 'gun' and weapon.fire_rate is not None:
        burst = GUN_BURST_ROUNDS if weapon.fire_rate >= AUTOMATIC_FIRE_RATE_RPM else 1
        cycle_time = burst * 60.0 / weapon.fire_rate

    return ShotSpec(accuracy=min(1.0, max(0.0, accuracy)),
                    destroy_capacity=min(1.0, max(0.0, destroy_capacity)),
                    rounds=SALVO_ROUNDS[kind], weapon=weapon.model,
                    time_of_flight=time_of_flight, interceptable=interceptable,
                    cycle_time=cycle_time, max_range=max_range)


# ── FABBRICA ──────────────────────────────────────────────────────────────────

def make_registry_fire_control(altitude_filter: bool = True, memoize: bool = True) -> Callable:
    """Fire control `(shooter, target) -> ShotSpec | None` dai registri d'arma.

    Args:
        altitude_filter (bool): applica il filtro d'inviluppo di quota ai bersagli aerei.
        memoize (bool): memoizza armi candidate e scelte (v. "Memoizzazione"): cambia solo
            le prestazioni, mai il risultato.
    Returns:
        Callable: da passare come `fire_control` a `run_session`/`resolve_engagement`.
    Raises:
        TypeError: argomenti non booleani.
    """
    if not isinstance(altitude_filter, bool) or not isinstance(memoize, bool):
        raise TypeError("altitude_filter and memoize must be bool")

    candidates_cache: Dict = {}
    choice_cache: Dict = {}

    def candidates(key):
        if not memoize:
            return _candidate_weapons(key)

        if key not in candidates_cache:
            candidates_cache[key] = _candidate_weapons(key)

        return candidates_cache[key]

    def fire_control(shooter, target) -> Optional[ShotSpec]:
        shooter_key = _shooter_key(shooter)

        if shooter_key is None:
            return None

        weapons = candidates(shooter_key)

        if not weapons:
            return None

        t_key = target_key(target)

        if t_key is None:
            return None

        keys, dimension, is_air = t_key
        shooter_z = _z(shooter) if is_air else None
        target_z = _z(target) if is_air else None
        cache_key = (shooter_key, keys, dimension, is_air, shooter_z, target_z)

        if memoize and cache_key in choice_cache:
            return choice_cache[cache_key]

        choice = select_weapon(weapons, keys, dimension, is_air, shooter_z, target_z, altitude_filter)
        spec = shot_spec_for(*choice, is_air=is_air) if choice is not None else None

        if memoize:
            choice_cache[cache_key] = spec

        return spec

    return fire_control
