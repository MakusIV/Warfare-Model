"""Semantica della perdita e del danno per singolo asset.

DECISIONE (2026-09-22, §9 di `Architettura_esecuzione_sessioni_virtuali_ANALISI.md`).
Il motore di sessioni virtuali deve produrre **perdite e danni per singolo asset** (decisione
dell'utente registrata il 21/09, vincolo non negoziabile). Finora non esisteva alcuna
trasformazione da "arma che spara" a "salute che cala": `Asset.health` era un intero 0-100
con setter diretto e nessuna logica. Questo modulo fissa il contratto; la parte stocastica
(chi spara, quando, quante volte) resta al `Engagement_Resolver` della Fase 4.

## Contratto

1. **Unita' di scambio: `DamageEvent`** — un evento per ogni colpo risolto, non un aggregato.
   E' l'atomo di cui sara' fatto il `SessionOutcome` della Fase 0/6. Non contiene alcun
   identificativo del simulatore (v. [[feedback_core_simulator_agnostic]]): solo id di
   dominio, secondi assoluti, e un campo `provenance` che dichiara se il dato e' misurato
   (adapter DCS), derivato (risolutore sintetico) o stimato.

2. **`accuracy` = P(colpo a segno), `destroy_capacity` = P(distruzione | colpo a segno).**
   Non e' un'invenzione: e' la lettura naturale dei due campi gia' presenti nei registri
   d'arma (`Ground_Weapon_Data`, `Ship_Weapon_Data`, `Aircraft_Weapon_Data`), entrambi in
   [0, 1] e indicizzati per tipo e taglia del bersaglio. Il loro prodotto
   `accuracy x destroy_capacity` e' la Pk gia' usata come principio di punteggio in tutto il
   progetto, qui semplicemente scomposta in Ph e Pk|h — la stessa scomposizione dei modelli
   d'ingaggio reali. **Nessuna costante nuova viene introdotta.**

3. **Tre esiti per colpo**, mutuamente esclusivi:
   - `KILL`   con probabilita' `accuracy * destroy_capacity` -> l'asset e' distrutto;
   - `DAMAGE` con probabilita' `accuracy * (1 - destroy_capacity)` -> colpito ma non
     distrutto, la salute cala di `round(100 * destroy_capacity)` punti (minimo 1);
   - `MISS`   con probabilita' `1 - accuracy` -> nessun effetto.
   La stessa `destroy_capacity` misura sia la probabilita' di uccidere sia l'entita' del
   danno non letale: e' la letalita' dell'arma contro quel bersaglio, ed e' coerente che un
   colpo non letale di un'arma molto letale faccia comunque molto male. Ne discende che
   servono circa `1/destroy_capacity` colpi a segno non letali per mettere fuori uso il
   bersaglio, il che rende l'**accumulo** una proprieta' emergente e non un parametro.

4. **Un colpo puo' uccidere direttamente**: non esiste un pavimento artificiale che obblighi
   a degradare per gradi. E' proprio il senso dell'esito KILL.

5. **La soglia `Destroyed` resta a `health <= 15`** (`DataType/State.py:HEALTH_LEVEL`), NON
   viene abbassata a 0. Il residuo del 15% e' il relitto: l'asset non combatte piu' ma esiste
   ancora come oggetto recuperabile, ed e' cio' che da' significato a `repair_time`.
   `health = 0` resta raggiungibile e significa distruzione completa. Si noti che la messa
   fuori combattimento avviene **prima**: `State.isOperative()` e' gia' falso sotto il 50%
   (stato `Critical`), e `Military.combat_power` somma solo gli asset operativi — quindi il
   modello distingue da solo "mission kill" (<= 50) da "distruzione" (<= 15), e non serve
   introdurre nessuna delle due nozioni.

6. **Nessuna estrazione casuale qui dentro.** `resolve_hit` riceve `draw`, un numero in
   [0, 1) che il chiamante ottiene dall'RNG di sessione seedato (Fase 0). E' cio' che rende
   la sessione riproducibile da seed (decisione dell'utente n. 2) e rispetta la convenzione
   di progetto "mai `random` a livello di modulo". L'ordine delle soglie (KILL, poi DAMAGE,
   poi MISS) **fa parte del contratto**: cambiarlo cambierebbe l'esito a parita' di seed.

## Cosa NON e' deciso qui
- La penetrazione contro corazza: i record d'arma non hanno un campo `penetration` (§9 del
  documento, questione aperta). Finche' non c'e', `destroy_capacity` per taglia/tipo di
  bersaglio e' il solo discriminante disponibile.
- La riparazione: `repair_time` esiste ma nessuno lo consuma. Il contratto qui e'
  volutamente a senso unico (solo danno); il recupero e' materia del ciclo di campagna, non
  della sessione.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from Code.Dynamic_War_Manager.Source.DataType.State import HEALTH_LEVEL, StateCategory
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Damage_Model').logger


# Salute: intero 0-100, come Asset.health / State.health.
HEALTH_MAX = 100
HEALTH_MIN = 0

# Soglia di distruzione, derivata (non duplicata) da DataType/State.HEALTH_LEVEL, che la
# esprime come frazione. Resta a 15: v. punto 5 del contratto sopra.
DESTROYED_HEALTH = int(round(HEALTH_MAX * HEALTH_LEVEL[StateCategory.DESTROYED.value]))

# Un colpo andato a segno non puo' non avere alcun effetto: senza questo minimo, un'arma con
# destroy_capacity molto piccola (le infrastrutture nei registri hanno dc ~ 0) non potrebbe
# mai danneggiare il bersaglio nemmeno con un numero illimitato di colpi, cioe' l'accumulo
# sarebbe impossibile per costruzione. Convenzione dichiarata, non un parametro di taratura.
MIN_EFFECTIVE_HIT_DAMAGE = 1

# Esiti possibili di un colpo.
MISS = 'miss'
DAMAGE = 'damage'
KILL = 'kill'
HIT_OUTCOMES = (MISS, DAMAGE, KILL)

# Provenienza del dato, per il contratto delle porte SessionOrder/SessionOutcome:
# misurato dal simulatore, derivato dal risolutore sintetico, stimato da ricognizione.
MEASURED = 'measured'
DERIVED = 'derived'
ESTIMATED = 'estimated'
PROVENANCES = (MEASURED, DERIVED, ESTIMATED)


@dataclass(frozen=True)
class DamageEvent:
    """Un colpo risolto contro un singolo asset. Atomo del futuro `SessionOutcome`.

    Immutabile di proposito: l'ordine di risoluzione degli eventi fa parte del contratto di
    riproducibilita', quindi un evento gia' prodotto non va riscritto ma sostituito.

    Attributes:
        time: secondi assoluti dall'inizio della sessione.
        target_id: id di dominio dell'asset colpito (mai un id del simulatore).
        source_id: id di dominio di chi ha sparato, None se non attribuibile.
        weapon: modello d'arma di dominio (chiave dei registri d'arma), None se ignoto.
        outcome: uno di HIT_OUTCOMES.
        health_before/health_after: salute [0, 100] prima e dopo.
        health_delta: variazione (<= 0).
        destroyed: True se dopo l'evento l'asset e' nello stato Destroyed.
        provenance: uno di PROVENANCES.
    """
    time: float
    target_id: Optional[str]
    outcome: str
    health_before: int
    health_delta: int
    health_after: int
    destroyed: bool
    source_id: Optional[str] = None
    weapon: Optional[str] = None
    provenance: str = DERIVED


def hit_outcome_probabilities(accuracy: float, destroy_capacity: float) -> Dict[str, float]:
    """Probabilita' dei tre esiti di un colpo singolo.

    Args:
        accuracy: P(colpo a segno), [0, 1], dal registro d'arma.
        destroy_capacity: P(distruzione | colpo a segno), [0, 1], dal registro d'arma.

    Returns:
        {MISS: p, DAMAGE: p, KILL: p}, somma 1.

    Raises:
        TypeError/ValueError: argomenti non numerici o fuori [0, 1] (errore di
            programmazione: un registro d'arma mal formato va corretto, non tollerato).
    """
    accuracy = _check_probability('accuracy', accuracy)
    destroy_capacity = _check_probability('destroy_capacity', destroy_capacity)

    p_kill = accuracy * destroy_capacity
    p_damage = accuracy * (1.0 - destroy_capacity)

    return {KILL: p_kill, DAMAGE: p_damage, MISS: 1.0 - accuracy}


def resolve_hit(accuracy: float, destroy_capacity: float, draw: float) -> str:
    """Esito di un colpo singolo dato un numero casuale gia' estratto.

    `draw` viene dall'RNG di sessione seedato (Fase 0), MAI da `random` qui dentro: e' cio'
    che rende la sessione riproducibile. L'ordine delle soglie e' parte del contratto.

    Args:
        draw: numero in [0, 1).

    Returns:
        Uno di HIT_OUTCOMES.
    """
    draw = _check_probability('draw', draw)
    probabilities = hit_outcome_probabilities(accuracy, destroy_capacity)

    if draw < probabilities[KILL]:
        return KILL

    if draw < probabilities[KILL] + probabilities[DAMAGE]:
        return DAMAGE

    return MISS


def health_delta_for_outcome(outcome: str, destroy_capacity: float, current_health: int) -> int:
    """Variazione di salute (<= 0) prodotta da un esito.

    KILL porta a 0 qualunque sia la salute residua; DAMAGE toglie
    `round(100 * destroy_capacity)` punti, mai meno di MIN_EFFECTIVE_HIT_DAMAGE e mai piu'
    della salute residua; MISS non toglie nulla.
    """
    if outcome not in HIT_OUTCOMES:
        raise ValueError(f"outcome must be one of {HIT_OUTCOMES}, got {outcome!r}")

    current_health = _check_health(current_health)

    if outcome == MISS:
        return 0

    if outcome == KILL:
        return -current_health

    destroy_capacity = _check_probability('destroy_capacity', destroy_capacity)
    damage = max(MIN_EFFECTIVE_HIT_DAMAGE, int(round(HEALTH_MAX * destroy_capacity)))

    return -min(damage, current_health)


def build_damage_event(asset,
                       accuracy: float,
                       destroy_capacity: float,
                       draw: float,
                       time: float = 0.0,
                       source_id: Optional[str] = None,
                       weapon: Optional[str] = None,
                       provenance: str = DERIVED) -> Optional[DamageEvent]:
    """Risolve un colpo contro `asset` e ne descrive l'esito, **senza applicarlo**.

    Separare il calcolo dall'applicazione serve al risolutore della Fase 4: puo' calcolare
    tutti gli esiti di una salva, ordinarli deterministicamente e solo poi applicarli
    (modello a salva di Hughes: chi spara per primo non deve dipendere dall'ordine di
    iterazione di un dizionario).

    Returns:
        Il DamageEvent, oppure None se l'asset non espone una salute leggibile (dato
        mancante -> None + log, non eccezione).
    """
    if provenance not in PROVENANCES:
        raise ValueError(f"provenance must be one of {PROVENANCES}, got {provenance!r}")

    health_before = getattr(asset, 'health', None)

    if not isinstance(health_before, int) or isinstance(health_before, bool):
        logger.warning(f"build_damage_event: asset {getattr(asset, 'id', None)!r} has no readable health, event not built")
        return None

    outcome = resolve_hit(accuracy, destroy_capacity, draw)
    delta = health_delta_for_outcome(outcome, destroy_capacity, health_before)
    health_after = health_before + delta

    return DamageEvent(
        time=float(time),
        target_id=getattr(asset, 'id', None),
        outcome=outcome,
        health_before=health_before,
        health_delta=delta,
        health_after=health_after,
        destroyed=health_after <= DESTROYED_HEALTH,
        source_id=source_id,
        weapon=weapon,
        provenance=provenance,
    )


def apply_damage_event(asset, event: DamageEvent) -> Optional[int]:
    """Applica un DamageEvent all'asset. Ritorna la salute risultante, None se non applicato.

    L'evento e' la sola fonte del delta: applicare due volte lo stesso evento toglie due
    volte la salute, perche' un colpo ripetuto e' un altro colpo. L'idempotenza, se servira',
    e' responsabilita' di chi tiene la coda degli eventi, non di questa funzione.
    """
    if not isinstance(event, DamageEvent):
        raise TypeError(f"event must be a DamageEvent, got {type(event).__name__}")

    if event.health_delta == 0:
        return getattr(asset, 'health', None)

    apply_damage = getattr(asset, 'apply_damage', None)

    if apply_damage is None:
        logger.warning(f"apply_damage_event: asset {getattr(asset, 'id', None)!r} has no apply_damage(), event not applied")
        return None

    return apply_damage(event.health_delta)


def _check_probability(label: str, value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number, got {value!r}")

    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be in [0, 1], got {value!r}")

    return float(value)


def _check_health(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"health must be an int, got {value!r}")

    if not HEALTH_MIN <= value <= HEALTH_MAX:
        raise ValueError(f"health must be in [{HEALTH_MIN}, {HEALTH_MAX}], got {value!r}")

    return value
