"""Prontezza degli asset e processi fra sessioni (F8, §4.4, decisioni 19-21).

Funzioni pure salvo `apply_campaign_processes` (che muta gli asset, come
`apply_engagement_result`); nessuna estrazione casuale (mai il modulo `random`);
iterazioni sempre in ordine di id (determinismo).

Il registro di campagna (`Command/Campaign_Types.CampaignLedger`) e' immutabile: qui si
producono e si consumano i `ReadyRecord` (prontezza) e i `SessionRecord` (sessioni passate).
Nessuna scrittura in `Campaign_State` ne' applicazione di posizioni: quelle sono del
conduttore di campagna (`Logic/Session_Campaign`).

## Tempi
I tempi di turnaround e riparazione sono in `Context/Context` (`AIR_TURNAROUND_S`,
`GROUND_TURNAROUND_S`, `SEA_TURNAROUND_S`, `REPAIR_TIME_FULL_S`): valori della ricerca F8-R del
2026-10-23 (`Analysis/Document/Ricerca_Turnaround_Riparazione.md`), ordini di grandezza e non dati
tarati; dove la ricerca non ha trovato una fonte il valore resta una STIMA DI PROGETTO, come dice
il commento in `Context`.

## Regola di `readiness_after_session` (decisioni 19-21)
Per ogni asset, dall'istante piu' tardo fra il rientro (`movement_ends`/`end_time`) e
l'ultimo danno subito: `ready_at = since + turnaround + repair`. Un processo precedente piu'
lungo prevale; un asset senza novita' nella sessione non riparte il suo processo.
I record degli asset non passati alla sessione restano nel registro com'erano (difetto 26).
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Iterable, Mapping, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    CampaignLedger,
    ReadyRecord,
    SessionRecord,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Context.Context import (
    AIR_TURNAROUND_DEFAULT_S,
    AIR_TURNAROUND_S,
    GROUND_TURNAROUND_S,
    REPAIR_TIME_FULL_S,
    SEA_TURNAROUND_S,
)
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class

# LOGGING --
logger = Logger(module_name=__name__, class_name='Readiness').logger

# Tolleranza sui confronti fra istanti [s]: stessa grandezza di `Campaign_Types._TIME_EPS`.
_TIME_EPS = 1e-9


def asset_domain(asset) -> str:
    """`'air'` (`validate_class(asset, 'Aircraft')`), `'sea'` ('Ship'), altrimenti `'ground'`
    (veicoli, strutture): la stessa partizione di `Mission_Adapter.continuous_posture`."""
    if validate_class(asset, 'Aircraft'):
        return 'air'

    if validate_class(asset, 'Ship'):
        return 'sea'

    return 'ground'


def _class_value(value) -> Optional[str]:
    """Valore stringa di una classe aerea: `Air_Asset_Type` (enum) o stringa, altrimenti None."""
    if isinstance(value, Enum):
        value = value.value

    return value if isinstance(value, str) and value else None


def turnaround_class(asset) -> Optional[str]:
    """Classe aerea per il turnaround: `asset.asset_type` (valore di `Air_Asset_Type`, o il
    membro dell'enum: si usa `.value`) se e' una chiave di `AIR_TURNAROUND_S`; altrimenti la
    prima classe di `Aircraft_Data` per `asset.model` (`category[0]`); altrimenti None. None
    per gli asset non aerei."""
    if not validate_class(asset, 'Aircraft'):
        return None

    asset_type = _class_value(getattr(asset, 'asset_type', None))
    if asset_type in AIR_TURNAROUND_S:
        return asset_type

    model = getattr(asset, 'model', None)
    if model is None:
        return None

    # Import locale (evita potenziali cicli con i moduli d'asset, v. memoria
    # feedback_circular_import_workaround).
    from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data

    record = Aircraft_Data._registry.get(model)
    category = getattr(record, 'category', None) if record is not None else None
    first = category[0] if isinstance(category, (list, tuple)) and category else category
    cls_value = _class_value(first)

    return cls_value if cls_value in AIR_TURNAROUND_S else None


def turnaround_s(asset) -> Tuple[float, str]:
    """`(secondi, provenienza)`: aereo = `AIR_TURNAROUND_S[classe]` ('class:<classe>') o
    `AIR_TURNAROUND_DEFAULT_S` ('default', con un warning); terra = `GROUND_TURNAROUND_S`
    ('ground'); mare = `SEA_TURNAROUND_S` ('sea')."""
    domain = asset_domain(asset)

    if domain == 'air':
        cls = turnaround_class(asset)
        if cls is not None:
            return (float(AIR_TURNAROUND_S[cls]), f'class:{cls}')

        logger.warning(f"turnaround_s: unknown air class for asset {_domain_id(asset)!r}, "
                       f"using the default ({AIR_TURNAROUND_DEFAULT_S} s)")
        return (float(AIR_TURNAROUND_DEFAULT_S), 'default')

    if domain == 'sea':
        return (float(SEA_TURNAROUND_S), 'sea')

    return (float(GROUND_TURNAROUND_S), 'ground')


def repair_s(asset) -> Optional[float]:
    """Tempo di riparazione [s] dal danno attuale: None se distrutto (`is_destroyed()`) o
    salute non leggibile; 0.0 se salute >= 100; altrimenti
    `REPAIR_TIME_FULL_S[asset_domain(asset)] * (100 - salute) / 100` (lineare, STIMA)."""
    is_destroyed = getattr(asset, 'is_destroyed', None)
    if callable(is_destroyed) and is_destroyed():
        return None

    health = getattr(asset, 'health', None)
    if health is None or isinstance(health, bool) or not isinstance(health, (int, float)):
        return None

    health = float(health)

    if health >= 100.0:
        return 0.0

    return REPAIR_TIME_FULL_S[asset_domain(asset)] * (100.0 - health) / 100.0


def _mission_assets(order: SessionOrder) -> Dict[str, str]:
    """`{asset_id: mission_id}` degli asset impegnati in una missione dell'ordine."""
    by_asset: Dict[str, str] = {}
    for mission in order.missions:
        for asset_id in mission.asset_ids:
            by_asset[asset_id] = mission.mission_id
    return by_asset


def _asset_outcomes(outcome: SessionOutcome) -> Dict[str, object]:
    """`{asset_id: AssetMissionOutcome}` ricavato da `outcome.mission_outcomes`."""
    by_asset: Dict[str, object] = {}
    for mission_outcome in outcome.mission_outcomes.values():
        for asset_id, asset_outcome in mission_outcome.asset_outcomes.items():
            by_asset[asset_id] = asset_outcome
    return by_asset


def _last_damage_times(outcome: SessionOutcome) -> Dict[str, float]:
    """`{asset_id: istante}` dell'ultimo `DamageEvent` con `target_id == asset_id`."""
    last: Dict[str, float] = {}
    for event in outcome.damage_events:
        if event.target_id is None or event.time is None:
            continue
        prev = last.get(event.target_id)
        if prev is None or event.time > prev:
            last[event.target_id] = event.time
    return last


def readiness_after_session(ledger: CampaignLedger, order: SessionOrder, outcome: SessionOutcome,
                            assets: Mapping[str, object]) -> Dict[str, ReadyRecord]:
    """La nuova mappa di prontezza dopo la sessione (regola nel docstring del modulo).

    I record degli asset NON presenti in `assets` (forze non passate a questa sessione) sono
    riportati tali e quali; per gli asset presenti decide solo la regola (un asset distrutto
    perde il suo record anche se ne aveva uno).
    """
    # I record degli asset non passati (forze assenti da questa sessione) restano com'erano:
    # il ciclo qui sotto scrive solo chiavi di `assets` (difetto 26).
    readiness: Dict[str, ReadyRecord] = {asset_id: record
                                         for asset_id, record in ledger.readiness.items()
                                         if asset_id not in assets}

    end_nominal = order.t_end if order.t_end is not None else outcome.t_end
    mission_assets = _mission_assets(order)
    asset_outcomes = _asset_outcomes(outcome)
    last_damage = _last_damage_times(outcome)

    ammo = outcome.ammunition_consumed()
    inter = outcome.interceptions_consumed()
    fuel = outcome.fuel_consumed()

    for asset_id in sorted(assets):
        asset = assets[asset_id]
        previous = ledger.readiness.get(asset_id)

        # 1. Distrutto: mai pronto.
        if getattr(asset, 'is_destroyed', lambda: False)():
            continue

        in_mission = asset_id in mission_assets
        consumed = (ammo.get(asset_id, 0) > 0
                    or inter.get(asset_id, 0) > 0
                    or fuel.get(asset_id, 0) > 0)
        damage_time = last_damage.get(asset_id)

        # 2. Nulla di nuovo nella sessione: un processo in corso non riparte; solo riparazione
        #    per un danno anteriore al registro.
        if not in_mission and not consumed and damage_time is None:
            if previous is not None:
                readiness[asset_id] = previous
            else:
                repair = repair_s(asset)
                if repair is not None and repair > 0.0 and end_nominal is not None:
                    readiness[asset_id] = ReadyRecord(
                        asset_id, float(end_nominal) + repair, end_nominal, 0.0, repair)
            continue

        # 3. Turnaround e riparazione per chi ha fatto qualcosa.
        turnaround = turnaround_s(asset)[0] if (in_mission or consumed) else 0.0
        repair = repair_s(asset)
        repair = 0.0 if repair is None else float(repair)

        if turnaround == 0.0 and repair == 0.0:
            if previous is not None:
                readiness[asset_id] = previous
            continue

        # 4. Inizio: rientro (movement_ends/end_time) o fine nominale.
        if in_mission:
            base = outcome.movement_ends.get(asset_id)
            if base is None:
                asset_outcome = asset_outcomes.get(asset_id)
                base = getattr(asset_outcome, 'end_time', None) if asset_outcome is not None else None
            if base is None:
                base = end_nominal
        else:
            base = end_nominal

        # 5. since = max(base, ultimo danno); il processo precedente prevale.
        candidates = [v for v in (base, damage_time) if v is not None]
        since = max(candidates) if candidates else end_nominal

        if since is None:
            # Senza inizio non si puo' collocare il processo (ordine ed esito entrambi aperti).
            if previous is not None:
                readiness[asset_id] = previous
            continue

        ready_at = float(since) + turnaround + repair
        if previous is not None:
            ready_at = max(ready_at, previous.ready_at)

        # 6. Record.
        readiness[asset_id] = ReadyRecord(asset_id, ready_at, float(since), turnaround, repair)

    return readiness


def record_session(ledger: CampaignLedger, order: SessionOrder, outcome: SessionOutcome,
                   assets: Mapping[str, object]) -> CampaignLedger:
    """Registro con la sessione conclusa e la nuova prontezza: `with_session(...)` e
    `with_readiness(readiness_after_session(...))`. `outcome.t_end` None -> `order.t_end`.
    La prontezza degli asset non passati resta quella del registro."""
    t_end = outcome.t_end if outcome.t_end is not None else order.t_end
    return (ledger
            .with_session(SessionRecord(order.session_id, order.t_start, t_end))
            .with_readiness(readiness_after_session(ledger, order, outcome, assets)))


def _rearm_and_refuel(asset) -> None:
    """Riarmo e rifornimento a fine turnaround (E1, decisione 21), senza logistica.

    Aereo con `assigned_loadout` non None: `asset.assigned_loadout = asset.assigned_loadout`
    (scorta e pieno del loadout, `Aircraft.py:176-213`); aereo senza loadout: niente (non
    modellato). Veicolo/nave: `load_stores_from_registry()` e `load_fuel_from_registry()` se
    esistono. Nessun consumo delle scorte del blocco (logistica fuori F8, dichiarato)."""
    if validate_class(asset, 'Aircraft'):
        loadout = getattr(asset, 'assigned_loadout', None)
        if loadout is not None:
            asset.assigned_loadout = loadout
        return

    loader = getattr(asset, 'load_stores_from_registry', None)
    if callable(loader):
        loader()

    refueler = getattr(asset, 'load_fuel_from_registry', None)
    if callable(refueler):
        refueler()


def apply_campaign_processes(ledger: CampaignLedger, assets: Mapping[str, object],
                             t: float) -> CampaignLedger:
    """Processi di campagna fra sessioni (D4.d) conclusi entro `t`.

    Per ogni record con `ready_at <= t + eps`, in ordine di id: asset assente -> record
    CONSERVATO, applicato quando l'asset torna (difetto 26); asset distrutto -> record tolto;
    `record.repair` -> `asset.health = 100`; `record.rearm` -> riarmo e rifornimento
    (`_rearm_and_refuel`); record tolto. Restituisce il registro con i record non conclusi e
    quelli conclusi di asset assenti. Lo stato di un asset assente (salute, carburante) resta
    quello vecchio finche' l'asset non torna. IDEMPOTENTE (riapplicarlo con lo stesso registro
    e lo stesso `t` lascia gli asset nello stesso stato)."""
    remaining = dict(ledger.readiness)

    for asset_id in sorted(remaining):
        record = remaining[asset_id]

        if record.ready_at > t + _TIME_EPS:
            continue

        asset = assets.get(asset_id)

        if asset is None:
            # Asset non passato (forza assente da questa sessione): il record resta e il processo
            # sara' applicato alla prima sessione in cui l'asset tornera' (difetto 26).
            logger.debug(f"apply_campaign_processes: asset {asset_id!r} is absent; keeping its "
                         f"concluded readiness record until it returns")
            continue

        if getattr(asset, 'is_destroyed', lambda: False)():
            del remaining[asset_id]
            continue

        if record.repair:
            asset.health = 100

        if record.rearm:
            _rearm_and_refuel(asset)

        del remaining[asset_id]

    return ledger.with_readiness(remaining)


def ready_assets(ledger: CampaignLedger, assets: Mapping[str, object], t: float) -> Tuple[str, ...]:
    """Id (ordinati) degli asset non distrutti e pronti a `t`: cio' che il pianificatore puo'
    impiegare (D6.a)."""
    ready = []
    for asset_id in sorted(assets):
        asset = assets[asset_id]
        if getattr(asset, 'is_destroyed', lambda: False)():
            continue
        if ledger.is_ready(asset_id, t):
            ready.append(asset_id)
    return tuple(ready)


def _domain_id(obj) -> Optional[str]:
    """Id di dominio: `obj.id` o `obj.name` (non vuoto), None altrimenti."""
    for attr in ('id', 'name'):
        value = getattr(obj, attr, None)
        if isinstance(value, str) and value:
            return value
    return None