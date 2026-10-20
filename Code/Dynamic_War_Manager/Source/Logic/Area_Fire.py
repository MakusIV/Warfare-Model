"""Fuoco su posizione — la "salva su area" della missione di terra e di mare (F7b del piano della Missione).

V. `Analysis/Document/Proposta_F7_Bersagli_Filtro_Armi.md` §6 e la decisione 15 dell'utente del 2026-10-20 (scelte a-g,
tutte come raccomandate). Il risolutore d'ingaggio (`Logic/Engagement_Resolver`) spara solo a cio' che ha rilevato:
un'artiglieria che spara su "il punto dove i blu erano" (N3.e, posizione STIMATA del bersaglio POINT/AREA) non si
rappresentava. Qui il fuoco su posizione e' un EVENTO DI SESSIONE separato dal risolutore: nessun rilevamento, nessuna
finestra di contatto, solo geometria e estrazioni.

## La regola

**Missione di fuoco**: una missione di terra o di mare con bersaglio POINT o AREA e un'azione
`MissionAction(kind=TASK, name='Fire_At_Point', params={'rounds': int >= 1, 'weapon': str (facoltativo)}, start=...)`
su un suo waypoint (`Mission_Types.FIRE_AT_POINT_ACTION`, validata dalla `Mission`). Per ogni asset della missione
`fire_orders` ricava un `FireOrder`:
  * istante di tiro `t_fire`: l'arrivo dell'asset al waypoint (`Mission_Adapter.waypoint_times`, attese comprese);
    poi la condizione d'avvio: ON_ARRIVAL l'arrivo, AT_TIME `max(arrivo, t0 + time)`, AFTER_DURATION
    `arrivo + duration_s`;
  * punto mirato = `target.position` (la posizione STIMATA, N3.e: nebbia di guerra, il bersaglio vero e' altrove se si
    e' mosso); raggio di dispersione `R = max(radius_m, uncertainty_m se ESTIMATED, AREA_FIRE_MIN_DISPERSION_M)`.

`resolve_area_fire` risolve l'evento all'istante d'impatto `t_impact = t_fire + time_of_flight` (la formula di
`Fire_Control.shot_spec_for`):
  * condizioni, altrimenti nessun tiro (con log): il tiratore non e' passivo/distrutto/a secco a `t_fire`
    (`inactive_from`, calcolato dalla sessione); un'arma e' utilizzabile (`Fire_Control.area_fire_weapon`: quella
    dichiarata in `params['weapon']`, altrimenti la prima con task Artillery / Naval_Gunfire_Support / Land_Attack che
    ha scorta e portata; armi `missile` e aerei esclusi, 15a/15e); il punto mirato e' entro la portata dell'arma, in
    orizzontale, dalla posizione del tiratore a `t_fire`;
  * colpi = `min(rounds, scorta // stock_per_round)`;
  * per ogni colpo, nell'ordine: 2 estrazioni per il punto d'impatto, uniforme nel disco di raggio `R` (raggio
    `R * sqrt(u1)`, angolo `2 pi u2`); poi, per ogni nemico del tiratore NON distrutto, in ordine di id, la cui
    posizione a `t_impact` dista in orizzontale non piu' di `r_l` dal punto d'impatto: 1 estrazione e
    `Damage_Model.resolve_hit(1.0, destroy_capacity, draw)` (un colpo a segno entro il raggio letale: la letalita' e'
    solo la `destroy_capacity` della riga del template, non c'e' una seconda Ph). `destroy_capacity` viene dalla riga del
    template dell'arma per la classe del bersaglio (stessa catena `target_key` / `_cell` della fire control,
    `Fire_Control.area_fire_pk`); Pk nulla o bersaglio aereo in volo: nessun effetto e nessuna estrazione;
  * `r_l = AREA_FIRE_LETHAL_RADIUS_PER_MM x caliber`, ripiego `AREA_FIRE_LETHAL_RADIUS_M`;
  * l'esito e' un `EngagementResult` con `forces=()` (nessuna forza d'ingaggio: niente tempra, disingaggio o shock sul
    colpito, 15g), gli `AmmunitionEvent` all'istante `t_fire` e i `DamageEvent` a `t_impact`. La sessione lo applica
    subito (`apply_engagement_result`) e lo accoda ai risultati; le distruzioni entrano nelle conoscenze degli episodi
    successivi.

## Costanti STIMATE (non tarate, decisione 15 b/c)

Dichiarate sotto: `AREA_FIRE_MIN_DISPERSION_M`, `AREA_FIRE_LETHAL_RADIUS_PER_MM`, `AREA_FIRE_LETHAL_RADIUS_M`. Nessun dato
d'arma le fonda: sono il minimo per avere un modello (dispersione uniforme, letalita' a soglia).

## RNG

Solo l'RNG di sessione: la sessione passa `order.rng(mission_id=<missione>, event_id=area_fire_event_id(ordine),
counter=0)` (primo uso dello slot `mission_id` di `Session_Rng`, corretto perche' il tiro appartiene a UNA missione).
L'ordine delle estrazioni dentro lo stream e' quello sopra e fa parte del contratto. Non tocca gli stream degli
ingaggi: ogni sessione senza azioni `Fire_At_Point` e' identica a prima.

## Limiti dichiarati (modello volutamente semplice)

Dispersione uniforme, letalita' a soglia, niente fuoco amico (solo i nemici del tiratore, 15d), niente intercettazione
(15e), niente effetti dottrinali sul colpito (15g), aerei in volo come tiratori e come bersagli esclusi (un aereo A TERRA
e' un bersaglio di superficie, come nella fire control), un solo evento all'impatto: un bersaglio distrutto da un altro
episodio fra `t_fire` e `t_impact` e' gia' distrutto all'impatto (corretto), ma la scorta e' consumata nell'ordine di
applicazione anche se l'evento di munizioni porta l'istante `t_fire`.

Nessun componente LLM, in nessuna forma; nessun uso del modulo `random` (l'RNG e' iniettato).
"""

import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    FIRE_AT_POINT_ACTION,
    ActionKind,
    Mission,
    StartConditionKind,
    TargetProvenance,
)
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Area_Fire').logger


# ── COSTANTI (tutte STIME non tarate, decisione 15 del 2026-10-20) ────────────

# Raggio minimo [m] di dispersione dei colpi attorno al punto mirato. STIMA, non un dato: l'ordine di grandezza della
# dispersione di una batteria d'artiglieria su un punto noto con precisione (decine di metri); il raggio effettivo e' il
# massimo con il raggio e l'incertezza del bersaglio.
AREA_FIRE_MIN_DISPERSION_M = 50.0

# Raggio letale [m] per mm di calibro. STIMA, non un dato: un proietto da 152 mm fa danni letali a un mezzo entro ~40 m
# (ordine di grandezza dei raggi di frammentazione di una granata HE); scala lineare col calibro per semplicita'.
AREA_FIRE_LETHAL_RADIUS_PER_MM = 0.25

# Raggio letale [m] di ripiego quando il registro non dichiara il calibro dell'arma. STIMA, non un dato.
AREA_FIRE_LETHAL_RADIUS_M = 25.0

# Tolleranza sui confronti fra istanti [s] (la stessa grandezza di `Contact_Scheduler.TIME_EPS`).
_TIME_EPS = 1e-9


# ── ORDINI DI FUOCO ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FireOrder:
    """Un'azione di fuoco su posizione di UN asset (F7b), nella forma del motore.

    Attributes:
        mission_id/asset_id: id di dominio della missione e del tiratore.
        waypoint_index/action_index: posizione dell'azione nel piano dei punti (indice del waypoint, indice
            dell'azione nel waypoint): identifica l'ordine e ne costruisce l'`event_id`.
        t_fire: istante assoluto [s] del tiro.
        aim_x/aim_y: punto mirato [m], la posizione stimata del bersaglio.
        dispersion_m: raggio [m] del disco di dispersione attorno al punto mirato.
        rounds: colpi richiesti (>= 1); weapon: modello dichiarato in `params['weapon']`, None = scelta automatica.
    """
    mission_id: str
    asset_id: str
    waypoint_index: int
    action_index: int
    t_fire: float
    aim_x: float
    aim_y: float
    dispersion_m: float
    rounds: int
    weapon: Optional[str] = None


def area_fire_event_id(order: FireOrder) -> str:
    """`event_id` dell'RNG e dell'evento: `'area_fire|<mission_id>|<asset_id>|<wp>|<action>'`."""
    return f"area_fire|{order.mission_id}|{order.asset_id}|{order.waypoint_index}|{order.action_index}"


def dispersion_radius(target) -> float:
    """Raggio di dispersione [m] per il bersaglio `target` (`Mission_Types.Target`):
    `max(radius_m, uncertainty_m se ESTIMATED, AREA_FIRE_MIN_DISPERSION_M)`."""
    radius = float(target.radius_m or 0.0)
    uncertainty = float(target.uncertainty_m or 0.0) if target.provenance is TargetProvenance.ESTIMATED else 0.0
    return max(radius, uncertainty, AREA_FIRE_MIN_DISPERSION_M)


def fire_orders(mission: Mission, movement, t0: float = 0.0) -> List[FireOrder]:
    """Gli ordini di fuoco dell'asset di `movement` (un `Mission_Adapter.AssetMovement` della missione), nell'ordine
    del piano dei punti (waypoint, poi azione). `t0`: inizio della sessione, a cui si riferisce l'istante delle
    condizioni AT_TIME. Funzione pura. Lista vuota se la missione non e' di terra o di mare, non ha azioni
    `FIRE_AT_POINT_ACTION`, o l'asset non ha una rotta percorribile (un warning se le azioni ci sono ma gli istanti
    d'arrivo no)."""
    if mission.domain == 'air':
        return []

    actions = [(index, action_index, action) for index, waypoint in enumerate(mission.waypoints)
               for action_index, action in enumerate(waypoint.actions)
               if action.kind is ActionKind.TASK and action.name == FIRE_AT_POINT_ACTION]

    if not actions:
        return []

    arrivals = MA.waypoint_times(movement)

    if len(arrivals) != len(mission.waypoints):
        logger.warning(f"fire_orders: mission {mission.mission_id!r}, asset {movement.asset_id!r}: no usable route "
                       f"({len(arrivals)} arrival times for {len(mission.waypoints)} waypoints), "
                       f"{FIRE_AT_POINT_ACTION!r} actions ignored")
        return []

    target = mission.target
    orders = []

    for index, action_index, action in actions:
        arrival = arrivals[index]
        start = action.start

        if start.kind is StartConditionKind.AT_TIME:
            t_fire = max(arrival, float(t0) + start.time)
        elif start.kind is StartConditionKind.AFTER_DURATION:
            t_fire = arrival + start.duration_s
        else:
            t_fire = arrival

        orders.append(FireOrder(mission_id=mission.mission_id, asset_id=movement.asset_id, waypoint_index=index,
                                action_index=action_index, t_fire=float(t_fire),
                                aim_x=float(target.position.x), aim_y=float(target.position.y),
                                dispersion_m=dispersion_radius(target), rounds=int(action.params['rounds']),
                                weapon=action.params.get('weapon')))

    return orders


# ── SCELTA DEL TIRO E RISOLUZIONE ─────────────────────────────────────────────

def lethal_radius(weapon: FC.AreaWeapon) -> float:
    """Raggio letale [m] di `weapon`: `AREA_FIRE_LETHAL_RADIUS_PER_MM x caliber`, ripiego
    `AREA_FIRE_LETHAL_RADIUS_M` se il registro non dichiara il calibro."""
    if weapon.caliber_mm is None:
        return AREA_FIRE_LETHAL_RADIUS_M

    return AREA_FIRE_LETHAL_RADIUS_PER_MM * weapon.caliber_mm


def plan_shot(order: FireOrder, shooter, positions_at: Callable, stock_of: Optional[Callable] = None
              ) -> Optional[FC.AreaWeapon]:
    """L'arma del tiro (`Fire_Control.area_fire_weapon`) dalla posizione del tiratore a `order.t_fire`
    (`positions_at(asset_id, t) -> (x, y[, z]) | None`), None se non c'e' posizione, arma, portata o scorta. Senza
    `stock_of` la scorta non e' considerata (la sessione la usa per stimare l'istante d'impatto a monte)."""
    position = positions_at(order.asset_id, order.t_fire)

    if position is None:
        return None

    distance = math.hypot(order.aim_x - float(position[0]), order.aim_y - float(position[1]))
    return FC.area_fire_weapon(shooter, distance, order.weapon, stock_of)


def impact_time(order: FireOrder, weapon: FC.AreaWeapon) -> float:
    """Istante d'impatto [s]: `t_fire + time_of_flight` dell'arma."""
    return order.t_fire + weapon.time_of_flight


class _Hit:
    """Copia di lavoro di un nemico: id e salute che evolvono colpo dopo colpo (duck typing di
    `Damage_Model.build_damage_event`, come `Engagement_Resolver._Shadow`)."""
    __slots__ = ('id', 'health')

    def __init__(self, asset_id: str, health: int):
        self.id = asset_id
        self.health = health


def resolve_area_fire(order: FireOrder, shooter, enemies: Sequence, positions_at: Callable, rng,
                      provenance: str = DM.DERIVED, *, inactive_from: Optional[float] = None,
                      grounded_at: Optional[Callable] = None) -> Optional[ER.EngagementResult]:
    """Risolve un ordine di fuoco su posizione (la regola nel docstring del modulo). **Non muta gli asset.**

    Args:
        order: l'ordine (`fire_orders`); shooter: l'asset tiratore.
        enemies: gli asset NEMICI del tiratore (il chiamante filtra per lato: niente fuoco amico, 15d), in qualunque
            ordine (l'ordine di risoluzione e' per id).
        positions_at: `(asset_id, t) -> (x, y[, z]) | None`, posizione dell'asset all'istante `t`; None = non
            disponibile (il tiratore non spara, il nemico non e' colpito).
        rng: oggetto con `.random()` in [0, 1) (di norma `SessionOrder.rng`); provenance: `Damage_Model` PROVENANCES.
        inactive_from: istante dal quale il tiratore e' distrutto, passivo (disingaggiato, fine di attivita') o a
            secco (calcolato dalla sessione); None = attivo. Se `inactive_from <= t_fire` nessun tiro.
        grounded_at: `(asset_id, t) -> bool`, True se l'asset e' un aereo A TERRA a `t` (bersaglio di superficie,
            come nella fire control); None = nessuno.

    Returns:
        L'`EngagementResult` (`forces=()`, `t_start=t_fire`, `t_end=t_impact`, gli `AmmunitionEvent` a `t_fire`, i
        `DamageEvent` a `t_impact`), oppure None se non c'e' tiro.
    """
    if inactive_from is not None and not inactive_from > order.t_fire + _TIME_EPS:
        logger.info(f"resolve_area_fire: {order.asset_id!r} is inactive from t={inactive_from:.1f}, no fire at "
                    f"t={order.t_fire:.1f} ({area_fire_event_id(order)})")
        return None

    stock_of = getattr(shooter, 'stock_of', None)
    stock_of = stock_of if callable(stock_of) else None
    weapon = plan_shot(order, shooter, positions_at, stock_of)

    if weapon is None:
        logger.info(f"resolve_area_fire: {order.asset_id!r} has no usable weapon, range or position at "
                    f"t={order.t_fire:.1f}: no fire ({area_fire_event_id(order)})")
        return None

    stock = stock_of(weapon.model) if stock_of is not None else None
    shots = order.rounds if stock is None else min(order.rounds, stock // weapon.stock_per_round)

    if shots < 1:
        return None

    t_impact = impact_time(order, weapon)
    radius = lethal_radius(weapon)
    candidates = []

    for enemy in sorted(enemies, key=lambda asset: str(_asset_id(asset))):
        enemy_id = _asset_id(enemy)
        health = getattr(enemy, 'health', None)

        if enemy_id is None or not isinstance(health, int) or isinstance(health, bool) \
                or health <= DM.DESTROYED_HEALTH:
            continue

        position = positions_at(enemy_id, t_impact)
        destroy_capacity = FC.area_fire_pk(weapon, enemy, grounded=bool(grounded_at and grounded_at(enemy_id, t_impact))) \
            if position is not None else None

        if destroy_capacity is None:
            continue

        candidates.append((_Hit(enemy_id, health), float(position[0]), float(position[1]), destroy_capacity))

    events = []

    for _ in range(shots):
        u_radius, u_angle = rng.random(), rng.random()
        spread = order.dispersion_m * math.sqrt(u_radius)
        angle = 2.0 * math.pi * u_angle
        impact_x = order.aim_x + spread * math.cos(angle)
        impact_y = order.aim_y + spread * math.sin(angle)

        for hit, x, y, destroy_capacity in candidates:
            if hit.health <= DM.DESTROYED_HEALTH or math.hypot(x - impact_x, y - impact_y) > radius:
                continue

            event = DM.build_damage_event(hit, 1.0, destroy_capacity, rng.random(), time=t_impact,
                                          source_id=order.asset_id, weapon=weapon.model, provenance=provenance)
            hit.health = event.health_after
            events.append(event)

    ammunition = ER.AmmunitionEvent(time=order.t_fire, asset_id=order.asset_id,
                                    rounds=shots * weapon.stock_per_round, weapon=weapon.model)

    return ER.EngagementResult(t_start=order.t_fire, t_end=t_impact, forces=(), damage_events=tuple(events),
                               ammunition_events=(ammunition,))


def _asset_id(asset) -> Optional[str]:
    """Id di dominio di un asset (id, poi name): stesso criterio di `Engagement_Resolver._domain_id`."""
    for attribute in ('id', 'name'):
        value = getattr(asset, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None
