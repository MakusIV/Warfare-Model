"""Validatore di sessione di campagna (F8, §4.1, decisioni 17-18).

Funzione fuori da `run_session`: l'esecutore, sintetico o DCS, esegue; il pianificatore valida
(la stessa scelta gia' fatta per il bingo a priori, deviazione 15). `validate_session` e' una
funzione pura: nessuna mutazione degli asset, nessuna estrazione casuale.

Chiamanti previsti: `Logic/Session_Campaign.run_campaign_session` e il pianificatore aereo.
Import di `Logic/Session_Simulator`, `Logic/Mission_Adapter`, `Logic/Contact_Scheduler` e
`Command/*_Types`: nessun ciclo, perche' nessuno di loro importa questo modulo.
"""
from __future__ import annotations

from typing import Iterable, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    CampaignLedger,
    SessionRules,
    SessionValidationError,
    SessionViolation,
    ViolationCode,
)
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import check_mission_assets
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Session_Validator').logger

# Tolleranza sui confronti fra istanti [s] (la stessa di `Contact_Scheduler.TIME_EPS`, importata).
_TIME_EPS = CS.TIME_EPS


def validate_session(order: SessionOrder, forces_a: Iterable, forces_b: Iterable, *,
                     ledger: Optional[CampaignLedger] = None,
                     rules: Optional[SessionRules] = None,
                     horizon: Optional[float] = None) -> Tuple[SessionViolation, ...]:
    """Valida un ordine di sessione contro le regole di campagna (F8).

    Args:
        order: l'ordine di sessione.
        forces_a, forces_b: le forze dei due lati (Military, Block, BlockItem).
        ledger: registro di campagna (sessioni passate e prontezza); None = nessun controllo
            di sovrapposizione ne' di prontezza.
        rules: regole di finestra; None = `ledger.rules` se presente, altrimenti `SessionRules()`.
        horizon: durata [s] per sessioni aperte (`order.t_end` None); obbligatoria per i
            controlli di fine missione.

    Returns:
        Tupla delle violazioni, nell'ordine dichiarato (finestra, disgiunzione, missioni).
        Vuota se l'ordine e' valido.

    Raises:
        ValueError: errori strutturali delle forze (forze duplicate o fuori `force_ids`,
            propagate da `SS.session_blocks`): sono errori di programma, non di pianificazione.
    """
    if not isinstance(order, SessionOrder):
        raise TypeError(f"order must be a SessionOrder, got {type(order).__name__}")

    if rules is None:
        rules = ledger.rules if ledger is not None else SessionRules()
    elif not isinstance(rules, SessionRules):
        raise TypeError(f"rules must be a SessionRules or None, got {type(rules).__name__}")

    violations = []

    # ── 1. Finestra ───────────────────────────────────────────────────────────
    t_start = order.t_start

    if order.t_end is None:
        violations.append(SessionViolation(
            ViolationCode.SESSION_OPEN,
            f"session {order.session_id!r} has no t_end (open session): open sessions are not "
            f"allowed in a campaign; use SessionRules.window() to set a duration",
            mission_id=None, asset_id=None,
        ))
        session_end = t_start + horizon if horizon is not None else None
    else:
        session_end = order.t_end
        duration = session_end - t_start
        if duration > rules.max_duration_s + _TIME_EPS:
            violations.append(SessionViolation(
                ViolationCode.SESSION_TOO_LONG,
                f"session {order.session_id!r} duration ({duration:.1f} s) exceeds the maximum "
                f"({rules.max_duration_s:.1f} s)",
                mission_id=None, asset_id=None,
            ))

    # ── 2. Disgiunzione ──────────────────────────────────────────────────────
    if ledger is not None and ledger.last_end is not None and t_start < ledger.last_end - _TIME_EPS:
        violations.append(SessionViolation(
            ViolationCode.SESSION_OVERLAP,
            f"session {order.session_id!r} starts at t={t_start:.1f}, before the effective end "
            f"of the previous session (t={ledger.last_end:.1f})",
            mission_id=None, asset_id=None,
        ))

    # ── 3. Blocchi ───────────────────────────────────────────────────────────
    try:
        blocks = SS.session_blocks(order, forces_a, forces_b)
    except ValueError:
        # Errori strutturali delle forze: propagati.
        raise

    # Mappa asset -> oggetto, come in run_session.
    assets: dict = {}
    for block in blocks.values():
        for asset in (getattr(block, 'assets', None) or {}).values():
            asset_id = _domain_id(asset)
            if asset_id is not None:
                assets[asset_id] = asset

    # ── 4. Per missione ──────────────────────────────────────────────────────
    for mission in order.missions:
        block = blocks.get(mission.block_id)
        v_before = len(violations)

        # a. Blocco e appartenenza degli asset.
        if block is None:
            violations.append(SessionViolation(
                ViolationCode.MISSION_ASSETS,
                f"mission {mission.mission_id!r}: block {mission.block_id!r} is not among the "
                f"forces passed ({sorted(blocks)})",
                mission_id=mission.mission_id, asset_id=None,
            ))
            continue

        try:
            check_mission_assets(mission, block)
        except ValueError as e:
            violations.append(SessionViolation(
                ViolationCode.MISSION_ASSETS,
                str(e),
                mission_id=mission.mission_id, asset_id=None,
            ))
            continue

        # b. Asset distrutti e prontezza.
        for asset_id in mission.asset_ids:
            asset = assets.get(asset_id)
            if asset is not None and getattr(asset, 'is_destroyed', lambda: False)():
                violations.append(SessionViolation(
                    ViolationCode.ASSET_DESTROYED,
                    f"mission {mission.mission_id!r}: asset {asset_id!r} is destroyed",
                    mission_id=mission.mission_id, asset_id=asset_id,
                ))
            elif ledger is not None and not ledger.is_ready(asset_id, order.t_start):
                record = ledger.readiness.get(asset_id)
                ready_at = record.ready_at if record is not None else None
                process = _process_label(record)
                violations.append(SessionViolation(
                    ViolationCode.ASSET_NOT_READY,
                    f"mission {mission.mission_id!r}: asset {asset_id!r} is not ready at "
                    f"t={order.t_start:.1f} (ready at t={ready_at:.1f}, {process})" if ready_at is not None else
                    f"mission {mission.mission_id!r}: asset {asset_id!r} is not ready at "
                    f"t={order.t_start:.1f} (no readiness record)",
                    mission_id=mission.mission_id, asset_id=asset_id,
                ))

        # c. Movimenti (partenza, rotta).
        side = getattr(block, 'side', None)
        bases = MA.air_base_points(blocks.values(), side) if mission.domain == 'air' else ()

        try:
            movements = MA.mission_movements(mission, order.t_start, bases)
        except ValueError as e:
            violations.append(SessionViolation(
                ViolationCode.MISSION_START_INVALID,
                str(e),
                mission_id=mission.mission_id, asset_id=None,
            ))
            continue

        # d. Fine pianificata oltre la sessione.
        if session_end is not None:
            end = MA.mission_planned_end(mission, movements)
            if end is not None and end > session_end + _TIME_EPS:
                violations.append(SessionViolation(
                    ViolationCode.MISSION_BEYOND_SESSION,
                    f"mission {mission.mission_id!r}: planned end t={end:.1f} is after the "
                    f"session end t={session_end:.1f} (excess: {end - session_end:.1f} s)",
                    mission_id=mission.mission_id, asset_id=None,
                ))

        # e. Regola A (velocita').
        try:
            MA.check_mission_speed(mission, assets, order.t_start)
        except ValueError as e:
            violations.append(SessionViolation(
                ViolationCode.MISSION_SPEED,
                str(e),
                mission_id=mission.mission_id, asset_id=None,
            ))

        # f. Carburante (solo aria).
        if mission.domain == 'air':
            try:
                MA.check_mission_fuel(mission, assets, order.t_start, bases)
            except ValueError as e:
                violations.append(SessionViolation(
                    ViolationCode.FUEL_MINIMUM,
                    str(e),
                    mission_id=mission.mission_id, asset_id=None,
                ))

            if SS.F6_BINGO:
                try:
                    MA.check_mission_bingo(mission, assets, bases, order.t_start,
                                          reverse_route=SS.F6_BINGO_REVERSE_ROUTE,
                                          disengage_reserve=SS.F6_BINGO_DISENGAGE_RESERVE)
                except ValueError as e:
                    violations.append(SessionViolation(
                        ViolationCode.BINGO_AT_START,
                        str(e),
                        mission_id=mission.mission_id, asset_id=None,
                    ))

        if len(violations) > v_before:
            logger.debug(f"validate_session: mission {mission.mission_id!r}: "
                         f"{len(violations) - v_before} violation(s)")

    if violations:
        logger.info(f"validate_session: session {order.session_id!r}: "
                    f"{len(violations)} violation(s), {len(order.missions)} mission(s)")

    return tuple(violations)


def check_session(order: SessionOrder, forces_a: Iterable, forces_b: Iterable, *,
                  ledger: Optional[CampaignLedger] = None,
                  rules: Optional[SessionRules] = None,
                  horizon: Optional[float] = None) -> None:
    """`validate_session`: se c'e' almeno una violazione, `SessionValidationError`.

    Raises:
        SessionValidationError: l'ordine non e' valido.
        ValueError: errori strutturali delle forze (propagati da `validate_session`).
    """
    violations = validate_session(order, forces_a, forces_b, ledger=ledger, rules=rules, horizon=horizon)

    if violations:
        raise SessionValidationError(order.session_id, violations)


# ── HELPER ─────────────────────────────────────────────────────────────────

def _domain_id(obj) -> Optional[str]:
    """Id di dominio: `obj.id` o `obj.name` (non vuoto), None altrimenti."""
    for attr in ('id', 'name'):
        value = getattr(obj, attr, None)
        if isinstance(value, str) and value:
            return value

    return None


def _process_label(record) -> str:
    """Etichetta del processo di prontezza: 'turnaround', 'repair', 'turnaround+repair'."""
    if record is None:
        return 'no record'
    if record.repair and record.rearm:
        return 'turnaround+repair'
    if record.repair:
        return 'repair'
    if record.rearm:
        return 'turnaround'
    return 'unknown process'