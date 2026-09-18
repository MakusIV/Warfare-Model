"""
MODULE Meteo_Analysis

Placeholder deterministico per le condizioni meteo di una Region. Non è un modello
meteorologico reale (nessun dato climatico, nessuna serie storica): è una funzione pura,
riproducibile, di (region_name, date, time) -- stessi input, stesso output, mai `random` --
pensata per essere sostituita in futuro da una generazione meteo vera senza dover cambiare la
forma dei dati che consuma (v. Region.get_meteorological_reports, Region.build_info_report).

La forma del risultato ricalca deliberatamente `mission_requirements['usability']` di
Logic/Air_Resources_Assigner.py ({'day': bool, 'night': bool, 'adverse_weather': bool}), cosicché
le condizioni meteo correnti di una regione siano direttamente confrontabili con i requisiti di
usabilità di una missione, senza conversioni.

v. project memory project_c2_hierarchy_design.md (TASK 2 / Fase A).
"""
from __future__ import annotations

from datetime import date as _date, time as _time
from typing import Dict

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

logger = Logger(module_name=__name__, class_name='Meteo_Analysis').logger

# Confine giorno/notte, ora locale placeholder -- nessun modello reale di alba/tramonto.
DAY_START_HOUR = 6
DAY_END_HOUR = 20

# Mesi placeholder per il meteo avverso (non climatologia reale) -- inverno nell'emisfero nord.
ADVERSE_WEATHER_MONTHS = frozenset({11, 12, 1, 2})


def is_daylight(time: _time) -> bool:
    """True se `time` cade nella finestra diurna placeholder [DAY_START_HOUR, DAY_END_HOUR)."""
    if not isinstance(time, _time):
        raise TypeError(f"time must be a datetime.time, got {type(time).__name__}")
    return DAY_START_HOUR <= time.hour < DAY_END_HOUR


def has_adverse_weather(region_name: str, date: _date) -> bool:
    """Placeholder deterministico: meteo avverso possibile solo nei mesi invernali, con una
    variazione per-regione/per-giorno che non usa `random` (somma dei codici carattere del nome
    regione + giorno del mese, parità). Non rappresenta un fenomeno meteorologico reale."""
    if not isinstance(region_name, str) or not region_name:
        raise TypeError(f"region_name must be a non-empty string, got {region_name!r}")
    if not isinstance(date, _date):
        raise TypeError(f"date must be a datetime.date, got {type(date).__name__}")

    if date.month not in ADVERSE_WEATHER_MONTHS:
        return False

    return (date.day + sum(ord(c) for c in region_name)) % 2 == 0


def get_meteo_conditions(region_name: str, date: _date, time: _time) -> Dict[str, bool]:
    """Condizioni meteo correnti di una regione, shape identica a
    `mission_requirements['usability']` (v. Air_Resources_Assigner.get_aircraft_mission):
    `{'day': bool, 'night': bool, 'adverse_weather': bool}`. Placeholder deterministico -- v.
    docstring di modulo.
    """
    day = is_daylight(time)
    conditions = {
        'day': day,
        'night': not day,
        'adverse_weather': has_adverse_weather(region_name, date),
    }
    logger.debug(f"Meteo conditions for {region_name!r} on {date} {time}: {conditions}")
    return conditions
