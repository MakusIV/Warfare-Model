"""Conduttore minimo del ciclo di campagna (F8, §4.4, decisioni 19-22).

`run_campaign_session` esegue una sessione nel ciclo di campagna: processi fra sessioni
(prontezza, `Logic/Readiness`), validazione (`Logic/Session_Validator`), esecuzione
(`SS.run_session`), applicazione delle posizioni finali e registrazione della sessione nel
registro. `apply_final_positions` applica `SessionOutcome.final_positions` agli asset delle
forze (D1.d, decisione 22).

Il conduttore NON e' il `Theater_Session_Manager`: e' il minimo per provare prontezza e
posizione persistente (scenario S30). `run_session` va chiamata come ATTRIBUTO DEL MODULO
(`SS.run_session`), mai importata per nome: `Scenario_Baseline` la intercetta cosi'
(`Scenario_Baseline.py:20-26`). Il modulo e' del core e non sa nulla del simulatore: un
adapter DCS sostituirebbe il solo punto (3) di `run_campaign_session`.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional, Tuple

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import CampaignLedger
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Readiness
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic import Session_Validator
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class

# LOGGING --
logger = Logger(module_name=__name__, class_name='Session_Campaign').logger


def _domain_id(obj) -> Optional[str]:
    """Id di dominio: `obj.id` o `obj.name` (non vuoto), None altrimenti."""
    for attr in ('id', 'name'):
        value = getattr(obj, attr, None)
        if isinstance(value, str) and value:
            return value
    return None


def _assets_of(forces_a: Iterable, forces_b: Iterable) -> Dict[str, object]:
    """`{asset_id: asset}` di tutti gli asset delle forze (per id di dominio).

    Stesso criterio di `Session_Validator`/`run_session`: le forze possono essere
    `Military`/`Block` o `BlockItem` (che incapsula il blocco in `.block`).
    """
    assets: Dict[str, object] = {}

    for side in (forces_a, forces_b):
        for item in (side or []):
            block = getattr(item, 'block', item)
            for asset in (getattr(block, 'assets', None) or {}).values():
                asset_id = _domain_id(asset)
                if asset_id is not None:
                    assets[asset_id] = asset

    return assets


def apply_final_positions(outcome: SessionOutcome, forces_a: Iterable,
                          forces_b: Iterable) -> Dict[str, Tuple[float, float, float]]:
    """Applica `outcome.final_positions` agli asset delle forze (D1.d, decisione 22).

    Per ogni asset (ordine di id) con una posizione nell'esito:
    * postura `Mission_Adapter.OFF_SCENE_POSTURE` -> NON applicata (rientrato fuori scena,
      la posizione resta quella di partenza, decisione 22);
    * aereo con postura diversa da `PARKED_POSTURE` e `DESTROYED_POSTURE` -> applicata con
      un warning ("in volo a fine sessione");
    * altrimenti applicata.

    `asset.position = Point3D(x, y, z)` con le coordinate arrotondate a
    `Mission_Adapter.OFFSET_DECIMALS` (rumore della rotazione). Restituisce
    `{asset_id: posizione}` delle sole posizioni applicate.
    """
    assets = _assets_of(forces_a, forces_b)
    applied: Dict[str, Tuple[float, float, float]] = {}

    for asset_id in sorted(outcome.final_positions):
        point = outcome.final_positions[asset_id]
        asset = assets.get(asset_id)

        if asset is None:
            continue

        posture = outcome.postures.get(asset_id)

        if posture == MA.OFF_SCENE_POSTURE:
            continue

        x = float(round(point[0], MA.OFFSET_DECIMALS))
        y = float(round(point[1], MA.OFFSET_DECIMALS))
        z = float(round(point[2], MA.OFFSET_DECIMALS))

        if (validate_class(asset, 'Aircraft')
                and posture not in (MA.PARKED_POSTURE, MA.DESTROYED_POSTURE)):
            logger.warning(
                f"apply_final_positions: aircraft {asset_id!r} is still airborne at the end "
                f"of the session (posture {posture!r}): applying its final position "
                f"({x}, {y}, {z})")

        asset.position = Point3D(x, y, z)
        applied[asset_id] = (x, y, z)

    return applied


def run_campaign_session(ledger: CampaignLedger, order: SessionOrder, forces_a: Iterable,
                         forces_b: Iterable, fire_control: Callable, *,
                         apply_positions: bool = True,
                         **run_kwargs) -> Tuple[SessionOutcome, CampaignLedger]:
    """Una sessione nel ciclo di campagna (F8).

    Passi: (1) `Readiness.apply_campaign_processes(ledger, assets, order.t_start)` (i processi
    conclusi di asset assenti restano nel registro fino al loro ritorno);
    (2) `Session_Validator.check_session(order, forces_a, forces_b, ledger=ledger,
    horizon=run_kwargs.get('horizon'))` (solleva `SessionValidationError`: i processi del
    punto 1 sono gia' applicati agli asset, e riapplicarli e' idempotente);
    (3) `SS.run_session(order, forces_a, forces_b, fire_control, **run_kwargs)`;
    (4) con `apply_positions`, `apply_final_positions`; (5) `Readiness.record_session`.

    Args:
        ledger: registro di campagna (sessioni passate e prontezza).
        order: l'ordine di sessione.
        forces_a/forces_b: le forze dei due lati.
        fire_control: `(shooter, target) -> ShotSpec | None`.
        apply_positions: applica le posizioni finali agli asset (default True).
        **run_kwargs: passati a `SS.run_session` (es. `horizon`).

    Returns:
        `(esito della sessione, nuovo registro)`.

    Raises:
        SessionValidationError: l'ordine non e' valido (validatore, passo 2).
    """
    assets = _assets_of(forces_a, forces_b)

    # (1) Processi di campagna fra sessioni conclusi entro l'inizio della sessione.
    ledger = Readiness.apply_campaign_processes(ledger, assets, order.t_start)

    # (2) Validazione (solleva SessionValidationError, non chiama run_session).
    Session_Validator.check_session(order, forces_a, forces_b, ledger=ledger,
                                    horizon=run_kwargs.get('horizon'))

    # (3) Esecuzione (attributo del modulo: Scenario_Baseline la intercetta cosi').
    outcome = SS.run_session(order, forces_a, forces_b, fire_control, **run_kwargs)

    # (4) Posizioni finali (persistenza fra sessioni, decisione 22).
    if apply_positions:
        apply_final_positions(outcome, forces_a, forces_b)

    # (5) Registrazione della sessione e nuova prontezza.
    return outcome, Readiness.record_session(ledger, order, outcome, assets)
