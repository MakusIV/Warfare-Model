"""Contabilita' della scorta PER MODELLO D'ARMA — funzioni pure, condivise.

Proposta A1 di `Analysis/Document/Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md`
(decisione utente 2026-09-26). Fino ad allora la scorta di un asset era UN contatore
aggregato (`Mobile.ammunition`) che sommava armi eterogenee: la fire control sceglieva
un'arma per nome, ma il risolutore scalava lo scalare, e un A-10 con 4 Maverick a bordo ne
lanciava 642 pagandoli con i colpi del cannone. Ora lo stato primario e' il dizionario

    stores = {modello_arma: quantita'}

e `ammunition` / `interceptor_stock` sono VISTE calcolate su di esso.

Perche' un modulo a parte: la stessa contabilita' serve in due posti che devono dare
esattamente lo stesso risultato — l'asset reale (`Asset/Mobile.py`) e lo stato ombra del
risolutore (`Logic/Engagement_Resolver._Shadow`), che simula i consumi senza mutare l'asset
e li restituisce come eventi, applicati poi con `apply_engagement_result`. Due
implementazioni separate potrebbero divergere (l'ombra concede una salva che l'asset reale
non puo' pagare). Qui solo funzioni pure su argomenti espliciti: nessuno stato, nessun
import di dominio, nessuna casualita'.

## Le quattro forme della scorta, per un'arma richiesta `weapon`

1. `stores is None` -> **pool anonimo** (`anonymous`): il comportamento precedente al
   2026-09-26, usabile da qualunque arma. E' la forma degli stub di test e di chi imposta
   `Mobile.ammunition = n` a mano. `anonymous is None` = scorta non modellata, nessun
   vincolo (stessa semantica di sempre).
2. `weapon` in `stores` -> **la sua voce**, e solo quella.
3. `weapon` in `unmodelled` -> **arma reale dell'asset senza dato di scorta** (tipi contati
   a unita' dei registri, `Mobile.UNIT_COUNTED_WEAPON_TYPES`: mitragliatrici, CIWS, dove il
   registro da' il numero di armi e non i colpi): nessun vincolo, come ogni dato non
   modellato del progetto. Non paga ne' e' pagata da altre armi.
4. `weapon` None o **nome estraneo** all'asset (tabelle di fuoco di test con nomi
   'test:*', fire control che non dichiara l'arma) -> **l'aggregato**: la richiesta e'
   pagata dall'insieme delle voci, nell'ordine `drain_order`. E' la scelta conservativa
   per chi non ha informazione per arma: stesso totale e stesso esaurimento di prima.
   La fire control dai registri (`Logic/Fire_Control.py`) sceglie solo armi del registro
   dell'asset, quindi non passa mai di qui.

## Intercettori (vista)

`interceptor_weapons = {modello: e'_cannone}` elenca le armi AD dell'asset (selezione di
`Mobile.air_defense_volume`). Con `stores` presente e `interceptor_weapons` non vuoto la
scorta di intercettori e'

    sum(stores[missile]) + sum(stores[cannone] // ROUNDS_PER_GUN_INTERCEPT)

e un'intercettazione consuma 1 missile o ROUNDS_PER_GUN_INTERCEPT colpi DALLA STESSA VOCE
usata dal fuoco offensivo: un lanciatore che intercetta e tira con lo stesso missile scala
naturalmente lo stesso numero (la vecchia regola del "SAM puro" non serve piu'). Ordine di
consumo (regola F della proposta SAM): prima i cannoni, poi i missili; a parita' il nome
del modello. Altrimenti (vista non attiva) la scorta di intercettori e' il pool anonimo
`anonymous_interceptors`, distinto dalle munizioni come prima del 2026-09-26.
"""

from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Tuple


# ROUNDS_PER_GUN_INTERCEPT — STIMA DICHIARATA, da ricalibrare con il processo ATCAL
# interno. Un cannone AA non intercetta con un colpo ma con una raffica prolungata sul
# bersaglio in avvicinamento: un Phalanx (3000-4500 colpi/min) impegna un missile con
# raffiche da 1-2 s, cioe' ~75-150 colpi; la raffica lunga dottrinale dello Shilka e' di
# ~150-200 colpi complessivi sui quattro tubi. 100 colpi per tentativo sta nel mezzo, ed e'
# volutamente dalla parte prudente per la difesa, dato che la Pk dell'intercettazione e'
# gia' assunta = 1 per canale (Military.salvo_interception_capacity). Valore unico per
# tutti i calibri: il registro non da' una cadenza per arma utilizzabile qui.
# (Definita qui e non in Mobile perche' serve anche allo stato ombra del risolutore;
# Mobile la re-esporta con lo stesso nome.)
ROUNDS_PER_GUN_INTERCEPT = 100


def check_units(name: str, value) -> int:
    """Valida una quantita' da consumare: int >= 0 (bool escluso).

    Raises:
        TypeError: non intero (errore di programmazione).
        ValueError: negativo — il rifornimento non passa di qui.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, got {type(value).__name__}")

    if value < 0:
        raise ValueError(f"{name} must be non-negative (no resupply here), got {value}")

    return value


def normalize_stores(stores) -> Optional[Dict[str, int]]:
    """Copia validata di un dizionario di scorta, o None.

    Raises:
        TypeError: non e' un Mapping, chiavi non stringa o quantita' non intere.
        ValueError: quantita' negative.
    """
    if stores is None:
        return None

    if not isinstance(stores, Mapping):
        raise TypeError(f"stores must be a mapping {{weapon: quantity}} or None, got {type(stores).__name__}")

    result: Dict[str, int] = {}

    for weapon, quantity in stores.items():
        if not isinstance(weapon, str):
            raise TypeError(f"stores keys must be weapon model names (str), got {weapon!r}")

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError(f"stores[{weapon!r}] must be an int, got {type(quantity).__name__}")

        if quantity < 0:
            raise ValueError(f"stores[{weapon!r}] must be non-negative, got {quantity}")

        result[weapon] = quantity

    return result


# ── MUNIZIONI (fuoco offensivo) ───────────────────────────────────────────────

def total_stock(stores: Optional[Mapping[str, int]], anonymous: Optional[int]) -> Optional[int]:
    """La vista `ammunition`: somma delle voci, o il pool anonimo se `stores` e' None."""
    if stores is None:
        return anonymous

    return sum(stores.values())


def available_stock(stores: Optional[Mapping[str, int]], anonymous: Optional[int],
                    unmodelled: Iterable[str], weapon: Optional[str]) -> Optional[int]:
    """Unita' di scorta spendibili da `weapon` (v. "Le quattro forme"); None = nessun vincolo."""
    if stores is None:
        return anonymous

    if weapon is not None and weapon in stores:
        return stores[weapon]

    if weapon is not None and weapon in unmodelled:
        return None

    return sum(stores.values())


def has_stock(stores: Optional[Mapping[str, int]], anonymous: Optional[int],
              unmodelled: Iterable[str]) -> bool:
    """True se almeno un'arma puo' ancora sparare per scorta.

    Con la scorta per arma: una voce > 0, oppure un'arma non modellata (senza vincolo).
    Con il pool anonimo: > 0 o non modellato (None), come prima.
    """
    if stores is None:
        return anonymous is None or anonymous > 0

    return any(quantity > 0 for quantity in stores.values()) or bool(frozenset(unmodelled))


def drain_order(stores: Mapping[str, int],
                interceptor_weapons: Optional[Mapping[str, bool]] = None) -> List[str]:
    """Ordine in cui l'aggregato paga un consumo senza arma (forma 4).

    Prima le armi NON di difesa aerea, poi i cannoni AD, poi i missili AD; a parita' il
    nome del modello. Scelta conservativa dichiarata: un consumo non attribuito (tabella
    di test) erode per ultima la capacita' di intercettazione, che fino al 2026-09-26 era
    un contatore indipendente dalle munizioni per ogni asset non "SAM puro".
    """
    ad = interceptor_weapons or {}

    def key(model: str) -> Tuple[int, str]:
        if model not in ad:
            return 0, model

        return (1 if ad[model] else 2), model

    return sorted(stores, key=key)


def consume_stock(stores: Optional[Dict[str, int]], anonymous: Optional[int], unmodelled: Iterable[str],
                  weapon: Optional[str], units: int,
                  interceptor_weapons: Optional[Mapping[str, bool]] = None) -> Tuple[int, Optional[int]]:
    """Consuma `units` unita' per `weapon`. MUTA `stores` sul posto.

    Returns:
        (consumate, nuovo pool anonimo). Mai sotto zero: con scorta insufficiente si
        consuma il residuo e il valore di ritorno lo dice; senza vincolo (pool None, arma
        non modellata) si ritorna `units`.
    """
    units = check_units('units', units)

    if stores is None:
        if anonymous is None:
            return units, None

        consumed = min(units, anonymous)
        return consumed, anonymous - consumed

    if weapon is not None and weapon in stores:
        consumed = min(units, stores[weapon])
        stores[weapon] -= consumed
        return consumed, anonymous

    if weapon is not None and weapon in unmodelled:
        return units, anonymous

    left = units

    for model in drain_order(stores, interceptor_weapons):
        if left <= 0:
            break

        take = min(left, stores[model])
        stores[model] -= take
        left -= take

    return units - left, anonymous


# ── INTERCETTORI ──────────────────────────────────────────────────────────────

def interceptor_view_active(stores: Optional[Mapping[str, int]],
                            interceptor_weapons: Optional[Mapping[str, bool]]) -> bool:
    """True se la scorta di intercettori e' la vista sulle voci di `stores`."""
    return stores is not None and bool(interceptor_weapons)


def _interceptions_of(stores: Mapping[str, int], model: str, is_gun: bool) -> int:
    quantity = stores.get(model, 0)
    return quantity // ROUNDS_PER_GUN_INTERCEPT if is_gun else quantity


def interceptor_stock(stores: Optional[Mapping[str, int]], interceptor_weapons: Optional[Mapping[str, bool]],
                      anonymous: Optional[int]) -> Optional[int]:
    """Intercettazioni ancora possibili: la vista sulle armi AD, oppure il pool anonimo."""
    if not interceptor_view_active(stores, interceptor_weapons):
        return anonymous

    return sum(_interceptions_of(stores, model, is_gun) for model, is_gun in interceptor_weapons.items())


def interceptor_order(interceptor_weapons: Mapping[str, bool]) -> List[str]:
    """Ordine di consumo degli intercettori (regola F): cannoni prima, poi missili; poi il nome."""
    return sorted(interceptor_weapons, key=lambda model: (not interceptor_weapons[model], model))


def plan_interceptions(stores: Mapping[str, int], interceptor_weapons: Mapping[str, bool], amount: int,
                       weapon: Optional[str] = None) -> List[Tuple[str, int]]:
    """Ripartizione per arma di `amount` intercettazioni, SENZA mutare `stores`.

    Con `weapon` fra le armi AD si usa solo quella (applicazione di un evento che la
    dichiara); altrimenti l'ordine `interceptor_order`. Le voci senza scorta sufficiente
    sono saltate; la somma del piano puo' essere < `amount` (scorta esaurita).
    """
    amount = check_units('amount', amount)

    if weapon is not None and weapon in interceptor_weapons:
        order = [weapon]
    else:
        order = interceptor_order(interceptor_weapons)

    plan: List[Tuple[str, int]] = []
    left = amount

    for model in order:
        if left <= 0:
            break

        count = min(left, _interceptions_of(stores, model, interceptor_weapons[model]))

        if count > 0:
            plan.append((model, count))
            left -= count

    return plan


def apply_interception_plan(stores: Dict[str, int], interceptor_weapons: Mapping[str, bool],
                            plan: Iterable[Tuple[str, int]]) -> int:
    """Scala dalle voci il piano di `plan_interceptions`. MUTA `stores`. Ritorna le intercettazioni."""
    done = 0

    for model, count in plan:
        cost = ROUNDS_PER_GUN_INTERCEPT if interceptor_weapons[model] else 1
        stores[model] = max(0, stores.get(model, 0) - count * cost)
        done += count

    return done


def frozen_names(names: Optional[Iterable[str]]) -> FrozenSet[str]:
    """Insieme immutabile di nomi d'arma (None -> vuoto)."""
    return frozenset(names or ())
