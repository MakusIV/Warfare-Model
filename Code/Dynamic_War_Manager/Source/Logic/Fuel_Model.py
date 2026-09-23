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
  `amount` e' il residuo, `distance_covered` < `distance` e `exhausted` e' True. Dove l'asset
  si ferma lungo la rotta lo decide chi fa avanzare le rotte (Fase 6), con `distance_covered`.
- Nessun concetto del simulatore: id di dominio, metri, secondi assoluti, `provenance`
  dichiarata (stesse costanti di `Damage_Model`: un adapter DCS produrra' eventi MEASURED).
- Mai eccezioni per dati mancanti: carburante non modellato o asset senza id -> None + log.

## Cosa NON fa
- Non integra il consumo nel risolutore d'ingaggio: `Engagement_Resolver` non modella il
  movimento fra un contatto e l'altro. E' un'API a se', che l'orchestratore (Fase 6)
  chiamera' quando fa avanzare le rotte.
- Non rifornisce: il rifornimento e' materia del ciclo di campagna.
- Nessun componente LLM, in nessuna forma.
"""

from dataclasses import dataclass
from typing import Optional

from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Fuel_Model').logger

# Stessa soglia di Mobile.FUEL_EPS (non importata per non legare Logic ad Asset a livello di
# modulo): sotto questo residuo il carburante e' zero.
_FUEL_EPS = 1e-12


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
