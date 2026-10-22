"""
MODULE Campaign_Types

Tipi di dominio della campagna (F8). Dataclass immutabili, validazione in `__post_init__`,
mapping resi immutabili con `MappingProxyType`. Solo libreria standard: nessun import da
`Logic`, `Context`, `Asset`.

## Finestra di sessione (D4.b, decisione dell'utente)
`SessionRules` porta i valori deliberati (NON stime): durata di default e massima di una
sessione. `window(t_start, duration)` restituisce `(t_start, t_start + duration)` con
duration None = default.

## Registro di campagna (decisione 19)
`CampaignLedger` tiene le sessioni passate (`SessionRecord`) e la prontezza degli asset
(`ReadyRecord`). Immutabile: `with_session` e `with_readiness` restituiscono un registro
nuovo. `readiness` e' un `MappingProxyType` ordinato per id; `sessions` una tupla in ordine.

## Validazione di sessione
`SessionViolation` / `ViolationCode` sono il resoconto di `Logic/Session_Validator`.
`SessionValidationError` (ValueError) porta la tupla delle violazioni e il `session_id`.

Stile di `Command/Session_Types.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Dict, Mapping, Optional, Tuple

# LOGGING --
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

logger = Logger(module_name=__name__, class_name='Campaign_Types').logger

# Tolleranza sui confronti fra istanti [s]: stessa grandezza di `Contact_Scheduler.TIME_EPS`,
# ripetuta qui per non importare `Logic`.
_TIME_EPS = 1e-9

# D4.b, decisione dell'utente (valori deliberati, NON stime): durata di default e massima
# di una sessione [s].
DEFAULT_SESSION_DURATION_S = 7_200.0
MAX_SESSION_DURATION_S = 14_400.0


# ── ENUM ──────────────────────────────────────────────────────────────────────

class ViolationCode(Enum):
    """Codici di violazione del validatore di sessione (F8)."""
    SESSION_OPEN = 'session_open'
    SESSION_TOO_LONG = 'session_too_long'
    SESSION_OVERLAP = 'session_overlap'
    MISSION_ASSETS = 'mission_assets'
    ASSET_DESTROYED = 'asset_destroyed'
    ASSET_NOT_READY = 'asset_not_ready'
    MISSION_START_INVALID = 'mission_start_invalid'
    MISSION_BEYOND_SESSION = 'mission_beyond_session'
    MISSION_SPEED = 'mission_speed'
    FUEL_MINIMUM = 'fuel_minimum'
    BINGO_AT_START = 'bingo_at_start'


# ── DATACLASS ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SessionRules:
    """Regole della finestra di sessione (D4.b): default e massimo deliberati.

    Attributes:
        default_duration_s: durata predefinita di una sessione [s].
        max_duration_s: durata massima di una sessione [s].
    """
    default_duration_s: float = DEFAULT_SESSION_DURATION_S
    max_duration_s: float = MAX_SESSION_DURATION_S

    def __post_init__(self):
        for name in ('default_duration_s', 'max_duration_s'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"SessionRules.{name} must be a number, got {value!r}")
            if value <= 0.0:
                raise ValueError(f"SessionRules.{name} must be > 0, got {value}")

        object.__setattr__(self, 'default_duration_s', float(self.default_duration_s))
        object.__setattr__(self, 'max_duration_s', float(self.max_duration_s))

        if self.default_duration_s > self.max_duration_s + _TIME_EPS:
            raise ValueError(f"SessionRules.default_duration_s ({self.default_duration_s}) must be "
                             f"<= max_duration_s ({self.max_duration_s})")

    def window(self, t_start: float, duration_s: Optional[float] = None) -> Tuple[float, float]:
        """Finestra (t_start, t_start + durata) di una sessione.

        Args:
            t_start: inizio della sessione [s].
            duration_s: durata [s]; None = default.

        Returns:
            (t_start, t_start + durata)

        Raises:
            TypeError: t_start non e' un numero.
            ValueError: durata <= 0 o > max.
        """
        if isinstance(t_start, bool) or not isinstance(t_start, (int, float)):
            raise TypeError(f"t_start must be a number, got {t_start!r}")

        if duration_s is None:
            duration_s = self.default_duration_s
        else:
            if isinstance(duration_s, bool) or not isinstance(duration_s, (int, float)):
                raise TypeError(f"duration_s must be a number or None, got {duration_s!r}")
            duration_s = float(duration_s)

        if duration_s <= 0.0:
            raise ValueError(f"duration_s must be > 0, got {duration_s}")
        if duration_s > self.max_duration_s + _TIME_EPS:
            raise ValueError(f"duration_s ({duration_s}) exceeds the maximum ({self.max_duration_s})")

        return (float(t_start), float(t_start) + duration_s)


@dataclass(frozen=True)
class SessionViolation:
    """Una violazione del validatore di sessione.

    Attributes:
        code: il codice della violazione.
        message: descrizione (non vuota).
        mission_id: id della missione a cui si riferisce, se applicabile.
        asset_id: id dell'asset a cui si riferisce, se applicabile.
    """
    code: ViolationCode
    message: str
    mission_id: Optional[str] = None
    asset_id: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.code, ViolationCode):
            raise TypeError(f"code must be a ViolationCode, got {type(self.code).__name__}")
        if not isinstance(self.message, str) or not self.message:
            raise ValueError(f"message must be a non-empty str, got {self.message!r}")
        if self.mission_id is not None and (not isinstance(self.mission_id, str) or not self.mission_id):
            raise ValueError(f"mission_id must be None or a non-empty str, got {self.mission_id!r}")
        if self.asset_id is not None and (not isinstance(self.asset_id, str) or not self.asset_id):
            raise ValueError(f"asset_id must be None or a non-empty str, got {self.asset_id!r}")


class SessionValidationError(ValueError):
    """Ordine di sessione rifiutato dal validatore.

    Attributes:
        session_id: id della sessione rifiutata.
        violations: tupla delle violazioni.
    """

    def __init__(self, session_id: str, violations: Tuple[SessionViolation, ...]):
        if not isinstance(session_id, str) or not session_id:
            raise TypeError(f"session_id must be a non-empty str, got {session_id!r}")
        if not isinstance(violations, tuple) or not all(isinstance(v, SessionViolation) for v in violations):
            raise TypeError(f"violations must be a tuple of SessionViolation, got {violations!r}")

        lines = [f"session {session_id!r}: {len(violations)} violation(s):"]
        for v in violations:
            where = []
            if v.mission_id is not None:
                where.append(f"mission {v.mission_id!r}")
            if v.asset_id is not None:
                where.append(f"asset {v.asset_id!r}")
            prefix = f"  [{v.code.value}]"
            if where:
                prefix += f" ({', '.join(where)})"
            lines.append(f"{prefix} {v.message}")

        super().__init__('\n'.join(lines))
        self.session_id = session_id
        self.violations = violations


@dataclass(frozen=True)
class SessionRecord:
    """Una sessione conclusa nel registro di campagna.

    Attributes:
        session_id: id di dominio della sessione (non vuoto).
        t_start: inizio [s].
        t_end: fine EFFETTIVA (SessionOutcome.t_end), >= t_start.
    """
    session_id: str
    t_start: float
    t_end: float

    def __post_init__(self):
        if not isinstance(self.session_id, str) or not self.session_id:
            raise ValueError(f"session_id must be a non-empty str, got {self.session_id!r}")

        for name in ('t_start', 't_end'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"SessionRecord.{name} must be a number, got {value!r}")
            object.__setattr__(self, name, float(value))

        if self.t_end < self.t_start - _TIME_EPS:
            raise ValueError(f"SessionRecord: t_end ({self.t_end}) < t_start ({self.t_start})")


@dataclass(frozen=True)
class ReadyRecord:
    """Stato di prontezza di un asset nel registro di campagna (F8).

    Attributes:
        asset_id: id di dominio dell'asset.
        ready_at: istante di campagna [s] dal quale l'asset e' pronto.
        since: inizio del processo (rientro o ultimo danno).
        turnaround_s: durata del turnaround [s], >= 0 (riarmo e rifornimento).
        repair_s: durata della riparazione [s], >= 0 (salute a 100 alla fine).
    """
    asset_id: str
    ready_at: float
    since: float
    turnaround_s: float = 0.0
    repair_s: float = 0.0

    def __post_init__(self):
        if not isinstance(self.asset_id, str) or not self.asset_id:
            raise ValueError(f"asset_id must be a non-empty str, got {self.asset_id!r}")

        for name in ('ready_at', 'since', 'turnaround_s', 'repair_s'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"ReadyRecord.{name} must be a number, got {value!r}")
            object.__setattr__(self, name, float(value))

        if self.turnaround_s < 0.0:
            raise ValueError(f"ReadyRecord.turnaround_s must be >= 0, got {self.turnaround_s}")
        if self.repair_s < 0.0:
            raise ValueError(f"ReadyRecord.repair_s must be >= 0, got {self.repair_s}")

        if self.turnaround_s + self.repair_s <= 0.0:
            raise ValueError(f"ReadyRecord: turnaround_s ({self.turnaround_s}) + repair_s ({self.repair_s}) "
                             f"must be > 0")

        min_ready = self.since + self.turnaround_s + self.repair_s - _TIME_EPS
        if self.ready_at < min_ready:
            raise ValueError(f"ReadyRecord: ready_at ({self.ready_at}) must be >= since ({self.since}) "
                             f"+ turnaround_s ({self.turnaround_s}) + repair_s ({self.repair_s}) "
                             f"- eps = {min_ready}")

    @property
    def rearm(self) -> bool:
        """True se il record include il riarmo e rifornimento."""
        return self.turnaround_s > 0.0

    @property
    def repair(self) -> bool:
        """True se il record include la riparazione."""
        return self.repair_s > 0.0


def _check_readiness_map(value: Mapping[str, ReadyRecord]) -> MappingProxyType:
    """Valida e congela la mappa di prontezza: chiave == record.asset_id, ordinata per id."""
    if not isinstance(value, Mapping):
        raise TypeError(f"readiness must be a Mapping[str, ReadyRecord], got {type(value).__name__}")

    for key, record in value.items():
        if not isinstance(key, str) or not key:
            raise TypeError(f"readiness keys must be non-empty str, got {key!r}")
        if not isinstance(record, ReadyRecord):
            raise TypeError(f"readiness values must be ReadyRecord, got {type(record).__name__}")
        if key != record.asset_id:
            raise ValueError(f"readiness key {key!r} differs from ReadyRecord.asset_id {record.asset_id!r}")

    return MappingProxyType({k: value[k] for k in sorted(value)})


@dataclass(frozen=True)
class CampaignLedger:
    """Registro immutabile di campagna: sessioni passate e prontezza degli asset (F8).

    Attributes:
        rules: regole della finestra di sessione.
        sessions: sessioni passate in ordine, ciascuna disgiunta dalla successiva.
        readiness: mappa {asset_id: ReadyRecord} della prontezza degli asset.
    """
    rules: SessionRules = field(default_factory=SessionRules)
    sessions: Tuple[SessionRecord, ...] = ()
    readiness: Mapping[str, ReadyRecord] = field(default_factory=dict, hash=False)

    def __post_init__(self):
        if not isinstance(self.rules, SessionRules):
            raise TypeError(f"rules must be a SessionRules, got {type(self.rules).__name__}")

        # Convalida sessioni
        sessions = tuple(self.sessions)
        for i, rec in enumerate(sessions):
            if not isinstance(rec, SessionRecord):
                raise TypeError(f"sessions[{i}] must be a SessionRecord, got {type(rec).__name__}")

        for i in range(1, len(sessions)):
            prev_end = sessions[i - 1].t_end
            curr_start = sessions[i].t_start
            if curr_start < prev_end - _TIME_EPS:
                raise ValueError(f"sessions[{i}] (t_start={curr_start}) starts before "
                                 f"sessions[{i - 1}].t_end ({prev_end})")

        object.__setattr__(self, 'sessions', sessions)
        object.__setattr__(self, 'readiness', _check_readiness_map(self.readiness))

    @property
    def last_end(self) -> Optional[float]:
        """Fine effettiva dell'ultima sessione, None se nessuna."""
        return self.sessions[-1].t_end if self.sessions else None

    def ready_at(self, asset_id: str) -> Optional[float]:
        """Istante di prontezza di un asset, None se nessun processo in corso."""
        record = self.readiness.get(asset_id)
        return record.ready_at if record is not None else None

    def is_ready(self, asset_id: str, t: float) -> bool:
        """L'asset e' pronto a `t`: nessun record o `ready_at <= t + eps`."""
        record = self.readiness.get(asset_id)
        return record is None or record.ready_at <= t + _TIME_EPS

    def with_session(self, record: SessionRecord) -> 'CampaignLedger':
        """Registro con una sessione in piu' in coda.

        Raises:
            ValueError: la sessione si sovrappone all'ultima (contigua ammessa).
        """
        if not isinstance(record, SessionRecord):
            raise TypeError(f"record must be a SessionRecord, got {type(record).__name__}")

        if self.sessions and record.t_start < self.sessions[-1].t_end - _TIME_EPS:
            raise ValueError(f"new session (t_start={record.t_start}) overlaps with "
                             f"last session (t_end={self.sessions[-1].t_end})")

        return CampaignLedger(rules=self.rules,
                              sessions=self.sessions + (record,),
                              readiness=self.readiness)

    def with_readiness(self, readiness: Mapping[str, ReadyRecord]) -> 'CampaignLedger':
        """Registro con la mappa di prontezza SOSTITUITA."""
        return CampaignLedger(rules=self.rules,
                              sessions=self.sessions,
                              readiness=readiness)

    def to_dict(self) -> Dict:
        """Rappresentazione JSON-compatibile (solo tipi JSON, chiavi ordinate)."""
        return {
            'rules': {
                'default_duration_s': self.rules.default_duration_s,
                'max_duration_s': self.rules.max_duration_s,
            },
            'sessions': [
                {
                    'session_id': s.session_id,
                    't_start': s.t_start,
                    't_end': s.t_end,
                }
                for s in self.sessions
            ],
            'readiness': {
                asset_id: {
                    'asset_id': r.asset_id,
                    'ready_at': r.ready_at,
                    'since': r.since,
                    'turnaround_s': r.turnaround_s,
                    'repair_s': r.repair_s,
                }
                for asset_id, r in self.readiness.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> 'CampaignLedger':
        """Ricostruisce un registro dal dizionario prodotto da `to_dict` (inversa esatta)."""
        if not isinstance(data, Mapping):
            raise TypeError(f"data must be a Mapping, got {type(data).__name__}")

        rules_data = data.get('rules', {})
        rules = SessionRules(
            default_duration_s=float(rules_data.get('default_duration_s', DEFAULT_SESSION_DURATION_S)),
            max_duration_s=float(rules_data.get('max_duration_s', MAX_SESSION_DURATION_S)),
        )

        sessions = tuple(
            SessionRecord(
                session_id=str(s['session_id']),
                t_start=float(s['t_start']),
                t_end=float(s['t_end']),
            )
            for s in data.get('sessions', [])
        )

        readiness = {
            str(asset_id): ReadyRecord(
                asset_id=str(r['asset_id']),
                ready_at=float(r['ready_at']),
                since=float(r['since']),
                turnaround_s=float(r.get('turnaround_s', 0.0)),
                repair_s=float(r.get('repair_s', 0.0)),
            )
            for asset_id, r in data.get('readiness', {}).items()
        }

        return cls(rules=rules, sessions=sessions, readiness=readiness)