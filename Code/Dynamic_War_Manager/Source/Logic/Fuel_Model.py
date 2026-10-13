"""Consumo di carburante per movimento: l'evento `FuelEvent` e la coppia calcolo/applicazione.

FASE 5 del motore di sessioni virtuali (strato 3 dell'architettura DES, v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §6: "danno per
singolo asset, consumo munizioni e carburante, assemblaggio del SessionOutcome").

Il contatore vive sull'asset (`Mobile.fuel`, frazione del carico pieno — v. il commento
FUEL_FULL in `Asset/Mobile.py` per l'unita' e la sua motivazione); qui c'e' solo l'atomo
che entra nel `SessionOutcome` e le due funzioni che lo producono e lo applicano, con la
stessa separazione gia' scelta da `Damage_Model` (build vs apply) e da
`Engagement_Resolver` (il risolutore non muta gli asset):

  * `build_fuel_event` calcola il consumo di una tratta SENZA toccare l'asset: un esito puo'
    essere ispezionato, confrontato o scartato senza aver toccato la campagna;
  * `apply_fuel_event` lo applica con `Mobile.consume_fuel`.

## Contratto
- Consumo deterministico, proporzionale alla distanza (`Mobile.fuel_for_distance`):
  **nessuna estrazione casuale** in questo modulo, nessun RNG richiesto.
- L'evento e' **gia' limitato** al carburante disponibile (come il `health_delta` di un
  `DamageEvent` e' limitato alla salute residua): se la tratta richiede piu' di quanto c'e',
  `amount` e' il residuo, `distance_covered` < `distance` e `exhausted` e' True.
- Nessun concetto del simulatore: id di dominio, metri, secondi assoluti, `provenance`
  dichiarata (stesse costanti di `Damage_Model`: un adapter DCS produrra' eventi MEASURED).
- Mai eccezioni per dati mancanti: carburante non modellato o asset senza id -> None + log.

## Consumo per tratto e nel tempo (F6-A del piano della Missione, decisioni dell'utente 2026-10-12)

Fino alla F5 il carburante era un vincolo A POSTERIORI: un solo `FuelEvent` per asset a fine
movimento, per distanza, e un asset a secco continuava a muoversi e a combattere (esperimento E5).
Dalla F6-A:
  * **un `FuelEvent` per tratto** (`build_leg_fuel_event`), di movimento o fermo, con l'istante e la
    durata del tratto (`t_start`, `duration`, `duration_covered`, `stationary`);
  * **tratto di movimento**: in distanza, come prima (`distance` = lunghezza del tratto);
  * **tratto fermo** (attese e orbite della F5-C, sosta di un'unita' di superficie): consumo NEL
    TEMPO pari a quello del movimento alla velocita' di CROCIERA dell'asset (`cruise_speed`, il
    regime 'nominal' del profilo cinematico): `distanza equivalente = durata x crociera`, consumata al
    regime di crociera (`HOLD_REGIME`). Nessuna costante nuova. IPOTESI DICHIARATA, pessimistica per
    gli aerei: il consumo reale in attesa (loiter) e' piu' basso di quello di crociera, ma il dato non
    c'e' nei registri. Stesso criterio per terra e mare (un'unita' ferma in attesa consuma come in
    marcia di crociera: sovrastima dichiarata, nessun dato di consumo a motore acceso da fermo). Un
    asset senza velocita' di crociera nota non consuma nelle soste (nessun evento, log);
  * **esaurimento a monte** (`fuel_exhaustion`): dai tratti e dal carburante disponibile, l'istante e
    il punto in cui il carburante finisce (al regime di crociera). L'orchestratore lo usa PRIMA dello
    scheduler per troncare i tratti: oltre il punto di esaurimento l'asset non si muove (v.
    `Session_Simulator`, "Carburante");
  * **planata** di un aereo a secco in volo (`glide_range`, `nearest_reachable_base`): raggio =
    quota x `GLIDE_RATIO` (stima dichiarata, sotto).
Il carburante di partenza e il rifornimento NON cambiano (rifornimento: F8).

## Bingo (F6-B2 del piano della Missione, decisione 14)

  * **margine di rientro** (`return_margin`): carburante attuale - fabbisogno dei tratti alla crociera -
    rientro in linea retta dall'ultimo punto alla base idonea piu' vicina - riserva `BINGO_RESERVE`
    (stima dichiarata, sotto). E' il controllo A PRIORI del validatore
    (`Mission_Adapter.check_mission_bingo`): margine negativo = la missione non rientra con la riserva;
  * **punto di bingo** (`bingo_point`): il primo istante in cui il residuo basta appena per rientrare
    alla base piu' vicina con la riserva; l'orchestratore lo usa PRIMA dello scheduler per far tornare
    l'aereo (v. `Session_Simulator`, "Bingo"). Esiste se e solo se il margine e' negativo: con lo stesso
    carburante e le stesse basi la missione rifiutata a priori e' esattamente quella che in volo arriva
    al bingo (al regime di crociera).

## Cosa NON fa
- Non integra il consumo nel risolutore d'ingaggio: `Engagement_Resolver` non modella il
  movimento fra un contatto e l'altro. L'orchestratore tronca i tratti all'esaurimento prima di
  cercare i contatti e contabilizza il consumo tratto per tratto quando fa avanzare le rotte.
- Non rifornisce: il rifornimento e' materia del ciclo di campagna.
- Nessun componente LLM, in nessuna forma.
"""

import math
from dataclasses import dataclass, replace
from typing import Iterable, Mapping, Optional, Sequence, Tuple

from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Fuel_Model').logger

# Stessa soglia di Mobile.FUEL_EPS (non importata per non legare Logic ad Asset a livello di
# modulo): sotto questo residuo il carburante e' zero.
_FUEL_EPS = 1e-12

# Sotto questa lunghezza [m] un tratto e' FERMO (attesa, orbita, sosta): consumo nel tempo.
_LENGTH_EPS = 1e-9

# Regime del consumo nelle soste (F6-A, decisione dell'utente): la CROCIERA, qualunque sia il regime
# del movimento (Mobile.DEFAULT_FUEL_REGIME, non importato per non legare Logic ad Asset).
HOLD_REGIME = 'nominal'

# Rapporto di planata (distanza orizzontale / quota persa) di un aereo a motore spento, per decidere se
# un aereo a secco in volo raggiunge una base (F6-A). STIMA DI PROGETTO, NON UN DATO TARATO: i registri
# (`Aircraft_Data`) non hanno un dato di planata o di efficienza aerodinamica; 10:1 e' l'ordine di
# grandezza indicato dall'utente per un caccia a motore spento (un aliante supera 30:1, un caccia in
# configurazione pulita sta fra circa 7:1 e 12:1), unico per tutti gli aerei.
GLIDE_RATIO = 10.0


@dataclass(frozen=True)
class FuelEvent:
    """Consumo di carburante di un asset su una tratta. Atomo del `SessionOutcome`.

    Attributes:
        time: secondi assoluti dall'inizio della sessione (istante di fine tratta, o quello
            che l'orchestratore sceglie di attribuire al consumo).
        asset_id: id di dominio dell'asset (mai un id del simulatore).
        distance: metri richiesti per la tratta.
        distance_covered: metri effettivamente percorribili col carburante disponibile
            (== distance se basta).
        amount: carburante consumato [frazione del carico pieno], gia' limitato al disponibile.
        fuel_before/fuel_after: carburante [frazione] prima e dopo.
        exhausted: True se dopo l'evento il carburante e' finito (l'asset non si muove piu').
        regime: regime di Mobile.FUEL_REGIMES usato per il consumo.
        provenance: una di Damage_Model.PROVENANCES.
        t_start: istante d'inizio del tratto (F6-A, evento per tratto); None per l'evento per
            distanza di `build_fuel_event` (forma precedente, un evento per asset).
        duration: durata [s] del tratto (0 per l'evento per distanza).
        duration_covered: secondi del tratto percorsi o trascorsi col carburante disponibile
            (== duration se basta).
        stationary: tratto FERMO (attesa, orbita, sosta): consumo nel tempo alla crociera,
            `distance` e `distance_covered` nulli.
    """
    time: float
    asset_id: str
    distance: float
    distance_covered: float
    amount: float
    fuel_before: float
    fuel_after: float
    exhausted: bool
    regime: str = 'nominal'
    provenance: str = DM.DERIVED
    t_start: Optional[float] = None
    duration: float = 0.0
    duration_covered: float = 0.0
    stationary: bool = False


@dataclass(frozen=True)
class FuelExhaustion:
    """Istante e punto in cui il carburante di un asset finisce lungo i suoi tratti (F6-A).

    Attributes:
        asset_id: id di dominio.
        time: istante assoluto [s] dell'esaurimento.
        point: posizione (x, y, z) dell'esaurimento, interpolata nel tratto.
        leg_index: indice del tratto (nella sequenza passata a `fuel_exhaustion`) in cui finisce.
        fuel_before: carburante [frazione] all'inizio dei tratti.
    """
    asset_id: str
    time: float
    point: Tuple[float, float, float]
    leg_index: int
    fuel_before: float


def _domain_id(asset) -> Optional[str]:
    """Id di dominio: stesso criterio di Engagement_Resolver._domain_id (id, poi name)."""
    for attribute in ('id', 'name'):
        value = getattr(asset, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


def build_fuel_event(asset, distance: float, time: float = 0.0, regime: str = 'nominal',
                     provenance: str = DM.DERIVED) -> Optional[FuelEvent]:
    """Calcola il consumo di `asset` per percorrere `distance` metri, **senza applicarlo**.

    Returns:
        Il FuelEvent, oppure None (con un log) se l'asset non ha un id di dominio o se il suo
        carburante non e' modellato (fuel None o autonomia non ricavabile): nessun vincolo,
        nessun evento — stessa semantica di `build_damage_event` su una salute illeggibile.

    Raises:
        ValueError: provenance sconosciuta; TypeError/ValueError da `fuel_for_distance` per
            distanza non numerica o negativa, o regime sconosciuto.
    """
    if provenance not in DM.PROVENANCES:
        raise ValueError(f"provenance must be one of {DM.PROVENANCES}, got {provenance!r}")

    if isinstance(time, bool) or not isinstance(time, (int, float)):
        raise TypeError(f"time must be a number, got {time!r}")

    asset_id = _domain_id(asset)

    if asset_id is None:
        logger.warning("build_fuel_event: asset without domain id, event not built")
        return None

    fuel_before = getattr(asset, 'fuel', None)
    fuel_for_distance = getattr(asset, 'fuel_for_distance', None)

    if fuel_before is None or not callable(fuel_for_distance):
        logger.debug(f"build_fuel_event: fuel not modelled for asset {asset_id!r}, no event")
        return None

    required = fuel_for_distance(distance, regime)

    if required is None:
        logger.debug(f"build_fuel_event: no fuel autonomy for asset {asset_id!r}, no event")
        return None

    fuel_before = float(fuel_before)
    amount = min(required, fuel_before)
    fuel_after = fuel_before - amount

    if fuel_after < _FUEL_EPS:
        amount, fuel_after = fuel_before, 0.0

    if required <= 0.0 or amount >= required:
        covered = float(distance)
    else:
        covered = float(distance) * amount / required

    return FuelEvent(time=float(time), asset_id=asset_id, distance=float(distance),
                     distance_covered=covered, amount=amount, fuel_before=fuel_before,
                     fuel_after=fuel_after, exhausted=fuel_after <= 0.0, regime=regime,
                     provenance=provenance)


def apply_fuel_event(asset, event: FuelEvent) -> Optional[float]:
    """Applica un FuelEvent all'asset. Ritorna il carburante risultante, None se non applicato.

    Come `Damage_Model.apply_damage_event`, l'evento e' la sola fonte della quantita':
    applicarlo due volte consuma due volte (una tratta ripetuta e' un'altra tratta).
    L'idempotenza, se servira', e' responsabilita' di chi tiene la coda degli eventi.
    """
    if not isinstance(event, FuelEvent):
        raise TypeError(f"event must be a FuelEvent, got {type(event).__name__}")

    consume = getattr(asset, 'consume_fuel', None)

    if not callable(consume):
        logger.warning(f"apply_fuel_event: asset {_domain_id(asset)!r} has no consume_fuel(), "
                       f"event not applied")
        return None

    consume(event.amount)

    return getattr(asset, 'fuel', None)


# ── CONSUMO PER TRATTO (F6-A) ─────────────────────────────────────────────────
# I tratti sono quelli di `Contact_Scheduler.Leg` (t_start, t_end, p_start, p_end), letti per
# attributo: il modulo non importa lo scheduler.

def _leg_length(leg) -> float:
    return math.sqrt(sum((e - s) ** 2 for s, e in zip(leg.p_start, leg.p_end)))


def _leg_duration(leg) -> float:
    return max(0.0, float(leg.t_end) - float(leg.t_start))


def is_stationary(leg) -> bool:
    """Il tratto e' FERMO (attesa, orbita, sosta): lunghezza nulla."""
    return _leg_length(leg) <= _LENGTH_EPS


def cruise_speed(asset) -> Optional[float]:
    """Velocita' di crociera [m/s] dell'asset: il regime 'nominal' del profilo cinematico
    (`Mobile.speed`, dal registro), None se non disponibile."""
    profile = getattr(asset, 'speed', None)

    if not isinstance(profile, Mapping):
        return None

    value = profile.get('nominal')

    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None

    return float(value)


def _leg_equivalent(asset, leg, regime: str, hold_regime: str) -> Tuple[Optional[float], str]:
    """(metri da consumare, regime) per il tratto: la lunghezza al `regime` per un tratto di
    movimento, `durata x crociera` a `hold_regime` per un tratto fermo; (None, ...) per un tratto
    fermo di un asset senza velocita' di crociera nota (nessun consumo)."""
    if not is_stationary(leg):
        return _leg_length(leg), regime

    speed = cruise_speed(asset)

    if speed is None:
        return None, hold_regime

    return _leg_duration(leg) * speed, hold_regime


def leg_fuel_demand(asset, leg, regime: str = 'nominal', hold_regime: str = HOLD_REGIME) -> Optional[float]:
    """Carburante [frazione] richiesto dal tratto intero, NON limitato al disponibile.

    Returns:
        Il fabbisogno; 0.0 per un tratto fermo di un asset senza velocita' di crociera nota (nessun
        consumo, v. docstring del modulo); None se il carburante dell'asset non e' modellato
        (nessun vincolo).
    """
    if getattr(asset, 'fuel', None) is None or not callable(getattr(asset, 'fuel_for_distance', None)):
        return None

    distance, use_regime = _leg_equivalent(asset, leg, regime, hold_regime)

    if distance is None:
        return 0.0 if asset.fuel_for_distance(0.0, use_regime) is not None else None

    return asset.fuel_for_distance(distance, use_regime)


def build_leg_fuel_event(asset, leg, regime: str = 'nominal', provenance: str = DM.DERIVED,
                         hold_regime: str = HOLD_REGIME) -> Optional[FuelEvent]:
    """Consumo di `asset` su UN tratto (F6-A), **senza applicarlo**.

    Tratto di movimento: come `build_fuel_event` sulla sua lunghezza al `regime`. Tratto fermo:
    consumo nel tempo alla crociera (`durata x cruise_speed` a `hold_regime`), con `distance` e
    `distance_covered` nulli e `stationary` True. L'istante dell'evento e' la fine del tratto.

    Returns:
        Il FuelEvent, oppure None (con un log) se il carburante non e' modellato, l'asset non ha id
        o il tratto e' fermo e l'asset non ha una velocita' di crociera nota.
    """
    distance, use_regime = _leg_equivalent(asset, leg, regime, hold_regime)
    stationary = is_stationary(leg)
    duration = _leg_duration(leg)

    if distance is None:
        logger.debug(f"build_leg_fuel_event: asset {_domain_id(asset)!r} has no cruise speed, "
                     f"its hold does not consume")
        return None

    event = build_fuel_event(asset, distance, time=float(leg.t_end), regime=use_regime, provenance=provenance)

    if event is None:
        return None

    fraction = 1.0 if distance <= 0.0 else min(1.0, event.distance_covered / distance)

    if stationary:
        return replace(event, distance=0.0, distance_covered=0.0, t_start=float(leg.t_start),
                       duration=duration, duration_covered=duration * fraction, stationary=True)

    return replace(event, t_start=float(leg.t_start), duration=duration, duration_covered=duration * fraction)


def fuel_exhaustion(asset, legs: Sequence, regime: str = 'nominal',
                    hold_regime: str = HOLD_REGIME) -> Optional[FuelExhaustion]:
    """Istante e punto in cui il carburante di `asset` finisce lungo `legs` (F6-A), calcolati A MONTE.

    Il fabbisogno di ogni tratto e' quello di `leg_fuel_demand` (movimento in distanza, soste nel
    tempo alla crociera), sottratto in ordine dal carburante attuale dell'asset (non mutato). Nel
    tratto in cui il fabbisogno supera il residuo l'esaurimento e' nella frazione `residuo /
    fabbisogno` del tratto (consumo uniforme lungo il tratto), con posizione interpolata.

    Args:
        legs: i tratti che CONSUMANO, in ordine di tempo (il chiamante esclude quelli senza consumo,
            es. un aereo fermo a terra).

    Returns:
        Il `FuelExhaustion`, oppure None se il carburante basta per tutti i tratti o non e'
        modellato (nessun vincolo).
    """
    fuel = getattr(asset, 'fuel', None)
    asset_id = _domain_id(asset)

    if fuel is None or asset_id is None:
        return None

    fuel = float(fuel)
    remaining = fuel

    for index, leg in enumerate(legs):
        demand = leg_fuel_demand(asset, leg, regime, hold_regime)

        if demand is None:
            return None

        if demand <= 0.0:
            continue

        if demand <= remaining + _FUEL_EPS:
            remaining = max(0.0, remaining - demand)
            continue

        fraction = max(0.0, remaining) / demand
        time = float(leg.t_start) + fraction * _leg_duration(leg)
        point = tuple(float(s) + fraction * (float(e) - float(s)) for s, e in zip(leg.p_start, leg.p_end))
        return FuelExhaustion(asset_id=asset_id, time=time, point=point, leg_index=index, fuel_before=fuel)

    return None


# ── PLANATA DI UN AEREO A SECCO (F6-A) ────────────────────────────────────────

def glide_range(altitude: float, ratio: float = GLIDE_RATIO) -> float:
    """Distanza orizzontale [m] percorribile in planata da `altitude` metri (0 se a terra o sotto).

    La quota e' trattata come altezza sulla base d'arrivo: il terreno non e' modellato (modulo
    mappe), approssimazione dichiarata."""
    return max(0.0, float(altitude)) * float(ratio)


def nearest_reachable_base(point: Sequence[float], bases: Iterable[Tuple[float, float]],
                           ratio: float = GLIDE_RATIO) -> Optional[Tuple[float, float]]:
    """La base (x, y) piu' vicina in orizzontale a `point` entro il raggio di planata, None se nessuna.

    A parita' di distanza vince la coppia (x, y) minore: deterministico, mai l'ordine d'ingresso."""
    reach = glide_range(point[2], ratio)
    best = None

    for bx, by in bases:
        distance = math.hypot(float(bx) - float(point[0]), float(by) - float(point[1]))

        if distance <= reach and (best is None or (distance, bx, by) < best):
            best = (distance, float(bx), float(by))

    return None if best is None else (best[1], best[2])


# ── BINGO: RIENTRO CON LA RISERVA (F6-B2) ─────────────────────────────────────
#
# Bingo = il carburante residuo basta appena per rientrare alla base idonea piu' vicina con la
# riserva `BINGO_RESERVE`. In metri di crociera (`E` = residuo / consumo per metro alla crociera,
# `R` = riserva / consumo per metro, `d` = distanza in linea retta dalla base piu' vicina):
#
#     H(t) = E(t) - R - min_b d_b(P(t))        bingo al primo istante con H(t) <= 0
#
# `H` e' NON CRESCENTE lungo i tratti che consumano: in movimento E cala di 1 m per metro percorso e
# la distanza da una base cambia al piu' di 1 m per metro (|d'| <= 1); in sosta E cala e d e' costante.
# Per un tratto di movimento e una base b, con A = E all'inizio del tratto - R, w = P0 - B e versore e,
# `A - u = |w + u e|` ha la soluzione unica u = (A^2 - |w|^2) / (2 (A + w.e)); il bingo nel tratto e'
# il MASSIMO degli u_b (H <= 0 quando TUTTE le basi sono fuori portata). Nessuna estrazione casuale.
# Il rientro e' in linea retta 3D dal punto alla base a quota 0 (stessa convenzione della planata:
# terreno non modellato), consumato al regime di crociera: arriva con la riserva.

# Riserva di carburante [frazione del carico pieno] con cui un aereo deve rientrare (F6-B2). STIMA DI
# PROGETTO, NON UN DATO TARATO: i registri non hanno una riserva per tipo d'aereo. 0,10 del carico pieno
# e' l'ordine di grandezza delle riserve finali di dottrina (10% del carburante, o 20-30 minuti di volo
# in attesa), unica per tutti gli aerei; da sostituire con un dato per modello o con la dottrina del lato.
BINGO_RESERVE = 0.10


@dataclass(frozen=True)
class BingoPoint:
    """Istante e punto del bingo di un asset lungo i suoi tratti (F6-B2), calcolati A MONTE.

    Attributes:
        asset_id: id di dominio.
        time/point: istante assoluto [s] e posizione (x, y, z) del bingo, interpolata nel tratto.
        leg_index: indice del tratto (nella sequenza passata a `bingo_point`) in cui cade.
        base: punto d'atterraggio (x, y, 0) della base idonea piu' vicina al punto di bingo.
        fuel: carburante residuo [frazione] al bingo.
        margin: margine [frazione] a fine tratti: residuo - rientro dall'ultimo punto - riserva (< 0:
            e' il carburante che manca per rientrare con la riserva, v. `return_margin`).
    """
    asset_id: str
    time: float
    point: Tuple[float, float, float]
    leg_index: int
    base: Tuple[float, float, float]
    fuel: float
    margin: float


def nearest_base(point: Sequence[float], bases: Iterable[Tuple[float, float]]
                 ) -> Optional[Tuple[float, Tuple[float, float, float]]]:
    """(distanza 3D, punto d'atterraggio (x, y, 0)) della base piu' vicina a `point`, None senza basi.

    A parita' di distanza vince la coppia (x, y) minore: deterministico, mai l'ordine d'ingresso."""
    best = None

    for bx, by in bases:
        landing = (float(bx), float(by), 0.0)
        distance = math.dist(tuple(float(c) for c in point), landing)

        if best is None or (distance, landing[0], landing[1]) < (best[0], best[1][0], best[1][1]):
            best = (distance, landing)

    return best


def _cruise_rate(asset) -> Optional[float]:
    """Consumo [frazione per metro] alla crociera (`fuel_for_distance` e' lineare nella distanza)."""
    fuel_for_distance = getattr(asset, 'fuel_for_distance', None)

    if getattr(asset, 'fuel', None) is None or not callable(fuel_for_distance):
        return None

    rate = fuel_for_distance(1.0, HOLD_REGIME)
    return rate if rate is not None and rate > 0.0 else None


def return_margin(asset, legs: Sequence, bases: Iterable[Tuple[float, float]], reserve: float = BINGO_RESERVE,
                  hold_regime: str = HOLD_REGIME) -> Optional[float]:
    """Margine [frazione del carico pieno] a fine `legs`: carburante attuale - fabbisogno dei tratti (alla
    crociera, soste nel tempo come `leg_fuel_demand`) - rientro in linea retta dall'ultimo punto alla base
    piu' vicina - `reserve`. >= 0: l'asset rientra con la riserva.

    Returns:
        Il margine, oppure None se il carburante non e' modellato, non ci sono tratti o basi (nessun
        controllo possibile: il chiamante decide).
    """
    bases = tuple(bases)
    rate = _cruise_rate(asset)

    if rate is None or not legs or not bases:
        return None

    remaining = float(asset.fuel)

    for leg in legs:
        demand = leg_fuel_demand(asset, leg, HOLD_REGIME, hold_regime)

        if demand is None:
            return None

        remaining -= demand

    distance, _ = nearest_base(legs[-1].p_end, bases)
    return remaining - rate * distance - float(reserve)


def bingo_point(asset, legs: Sequence, bases: Iterable[Tuple[float, float]], reserve: float = BINGO_RESERVE,
                hold_regime: str = HOLD_REGIME) -> Optional[BingoPoint]:
    """Il bingo di `asset` lungo `legs` (F6-B2): il primo istante in cui il residuo basta appena per
    rientrare alla base piu' vicina di `bases` con la riserva (regola e formula sopra), calcolato A MONTE
    alla crociera sul carburante attuale (non mutato).

    Args:
        legs: i tratti che CONSUMANO, in ordine di tempo (come `fuel_exhaustion`).
        bases: posizioni (x, y) delle basi idonee (in sessione: `Mission_Adapter.air_base_points` del lato).

    Returns:
        Il `BingoPoint`, oppure None se l'asset rientra con la riserva dalla fine dei tratti
        (`return_margin` >= 0, a meno del rumore `_FUEL_EPS`) o se il controllo non e' possibile
        (carburante non modellato, nessun tratto, nessuna base).
    """
    bases = tuple(bases)
    margin = return_margin(asset, legs, bases, reserve, hold_regime)
    asset_id = _domain_id(asset)

    if margin is None or asset_id is None or margin >= -_FUEL_EPS:
        return None

    rate = _cruise_rate(asset)
    landings = [(float(bx), float(by), 0.0) for bx, by in bases]
    remaining = float(asset.fuel)
    found = None

    for index, leg in enumerate(legs):
        demand = leg_fuel_demand(asset, leg, HOLD_REGIME, hold_regime)
        start = tuple(float(c) for c in leg.p_start)
        reach = (remaining - float(reserve)) / rate       # A: metri di crociera oltre la riserva

        if is_stationary(leg):
            gap = reach - nearest_base(start, bases)[0]
            spent = demand / rate

            if gap <= 0.0:
                fraction = 0.0
            elif spent > 0.0 and gap <= spent:
                fraction = gap / spent
            else:
                fraction = None
        else:
            end = tuple(float(c) for c in leg.p_end)
            length = _leg_length(leg)
            direction = tuple((e - s) / length for s, e in zip(start, end))
            crossing = 0.0

            for landing in landings:
                w = tuple(s - b for s, b in zip(start, landing))
                distance0 = math.sqrt(sum(c * c for c in w))

                if reach - distance0 <= 0.0:
                    u = 0.0
                elif reach - length - math.dist(end, landing) > 0.0:
                    u = math.inf
                else:
                    u = (reach * reach - distance0 * distance0) / (2.0 * (reach + sum(a * b for a, b in zip(w, direction))))
                    u = min(max(u, 0.0), length)

                crossing = max(crossing, u)

            fraction = None if math.isinf(crossing) else crossing / length

        if fraction is not None:
            found = (index, leg, min(max(fraction, 0.0), 1.0), remaining - fraction * demand)
            break

        remaining -= demand

    if found is None:
        # Non puo' accadere con H non crescente e margine negativo, se non per arrotondamento: bingo a fine tratti.
        found = (len(legs) - 1, legs[-1], 1.0, remaining)

    index, leg, fraction, fuel = found
    time = float(leg.t_start) + fraction * _leg_duration(leg)
    point = tuple(float(s) + fraction * (float(e) - float(s)) for s, e in zip(leg.p_start, leg.p_end))
    _, base = nearest_base(point, bases)
    return BingoPoint(asset_id=asset_id, time=time, point=point, leg_index=index, base=base,
                      fuel=max(0.0, fuel), margin=margin)
