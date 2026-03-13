"""
Test_Military_Resources_Assigner.py
=====================================
Unit tests per il modulo Military_Resources_Assigner.py.

Funzioni testate
----------------
  Helpers privati (unit test puri, nessun mock):
    _extract_quantities        – conversione target_data → {type: {dim: int}}
    _extract_target_lists      – estrazione liste type/dim da target_data
    _check_mission_requirements– verifica requisiti di performance (cruise/attack)
    _usability_met             – verifica condizioni di usabilità (day/night/aw)
    _compute_score             – calcolo score ponderato combat × costo
    _reduce_target_data        – riduzione proporzionale target per priorità

  Funzione pubblica (test con mock dei logger):
    get_aircraft_mission       – selezione e ranking aircraft/loadout per missione
                                 (include test con target terrestre e target Aircraft)

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Military_Resources_Assigner.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Military_Resources_Assigner.py
    python  Code/Dynamic_War_Manager/Source/Test/Test_Military_Resources_Assigner.py --tests-only
"""

import os
import sys
import unittest
from contextlib import ExitStack
from unittest.mock import patch, MagicMock
from typing import Dict, List

# ─────────────────────────────────────────────────────────────────────────────
#  PATH SETUP
# ─────────────────────────────────────────────────────────────────────────────

sys.path.insert(
    0,
    os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..'] * 5))),
)

# ─────────────────────────────────────────────────────────────────────────────
#  LOGGER PATHS DA MOCKARE
# ─────────────────────────────────────────────────────────────────────────────

_LOGGER_MRA   = "Code.Dynamic_War_Manager.Source.Logic.Military_Resources_Assigner.logger"
_LOGGER_LO    = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts.logger"
_LOGGER_AWD   = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data.logger"
_LOGGER_AD    = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Logic.Military_Resources_Assigner import (
    get_aircraft_mission,
    _extract_quantities,
    _extract_target_lists,
    _check_mission_requirements,
    _usability_met,
    _compute_score,
    _reduce_target_data,
    _DIRECTIVE_WEIGHTS,
    _REFERENCE_COST_K,
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS

# ─────────────────────────────────────────────────────────────────────────────
#  FIXTURE GLOBALI
# ─────────────────────────────────────────────────────────────────────────────

# ── Loadout reali (usati in TestCheckMissionRequirements) ─────────────────────

_F14A_PHOENIX = AIRCRAFT_LOADOUTS["F-14A Tomcat"]["Phoenix Fleet Defense"]
# cruise: speed=850, ref_alt=9000, alt_max=15000, alt_min=5000, range(100%)=850 km
# attack: speed=1800, ref_alt=10000, alt_max=16000, alt_min=3000, range(100%)=650 km
# usability: day=True, night=True, adverse_weather=True

_F15E_IRON = AIRCRAFT_LOADOUTS["F-15E Strike Eagle"]["Iron Bomb Strike"]
# usability: day=True, night=False (o simile day-only)

# ── Mission requirements ──────────────────────────────────────────────────────

# Molto permissivi: quasi tutti i loadout li superano
_REQ_LENIENT: Dict = {
    'cruise': {
        'speed':               400,
        'reference_altitude':  3000,
        'altitude_max':        5000,
        'altitude_min':        20000,   # loadout alt_min ≤ 20000 → supera il check
        'range':               100,
    },
    'attack': {
        'speed':               400,
        'reference_altitude':  3000,
        'altitude_max':        5000,
        'altitude_min':        20000,
        'range':               100,
    },
    'usability': {'day': True, 'night': False, 'adverse_weather': False},
}

# Velocità irraggiungibile → nessun loadout supera il check
_REQ_STRICT_SPEED: Dict = {
    'cruise': {
        'speed': 99999, 'reference_altitude': 3000,
        'altitude_max': 5000, 'altitude_min': 20000, 'range': 100,
    },
    'attack': {
        'speed': 99999, 'reference_altitude': 3000,
        'altitude_max': 5000, 'altitude_min': 20000, 'range': 100,
    },
    'usability': {'day': True, 'night': False, 'adverse_weather': False},
}

# Range irraggiungibile → nessun loadout supera il check
_REQ_STRICT_RANGE: Dict = {
    'cruise': {
        'speed': 400, 'reference_altitude': 3000,
        'altitude_max': 5000, 'altitude_min': 20000, 'range': 999999,
    },
    'attack': {
        'speed': 400, 'reference_altitude': 3000,
        'altitude_max': 5000, 'altitude_min': 20000, 'range': 999999,
    },
    'usability': {'day': True, 'night': False, 'adverse_weather': False},
}

# Richiede volo notturno
_REQ_NIGHT: Dict = {
    'cruise': {
        'speed': 400, 'reference_altitude': 3000,
        'altitude_max': 5000, 'altitude_min': 20000, 'range': 100,
    },
    'attack': {
        'speed': 400, 'reference_altitude': 3000,
        'altitude_max': 5000, 'altitude_min': 20000, 'range': 100,
    },
    'usability': {'day': True, 'night': True, 'adverse_weather': False},
}

# ── Aircraft availability ─────────────────────────────────────────────────────

_AVAIL_STRIKE: List[Dict] = [
    {'model': 'F-15E Strike Eagle',    'loadout': 'Iron Bomb Strike',  'quantity': 15},
    {'model': 'A-10C II Thunderbolt II', 'loadout': 'Maverick/Gun CAS', 'quantity': 10},
]

_AVAIL_CAP: List[Dict] = [
    {'model': 'F-14A Tomcat', 'loadout': 'Phoenix Fleet Defense', 'quantity': 12},
]

_AVAIL_MIXED: List[Dict] = [
    {'model': 'F-14A Tomcat',          'loadout': 'Phoenix Fleet Defense', 'quantity': 12},
    {'model': 'F-15E Strike Eagle',    'loadout': 'Iron Bomb Strike',      'quantity': 15},
]

# ── Target data ───────────────────────────────────────────────────────────────

# Target terrestre (Strike / CAS)
_TARGET_GROUND: Dict = {
    'Soft': {
        'big':   {'quantity': 3,  'priority': 5},
        'med':   {'quantity': 5,  'priority': 6},
        'small': {'quantity': 10, 'priority': 4},
    },
    'Armored': {
        'big': {'quantity': 2, 'priority': 3},
        'med': {'quantity': 4, 'priority': 3},
    },
}

# Target aereo (CAP / Intercept) – quantità elevate per garantire total > 0
_TARGET_AIRCRAFT: Dict = {
    'Aircraft': {
        'big':   {'quantity': 20, 'priority': 8},
        'med':   {'quantity': 30, 'priority': 6},
        'small': {'quantity': 40, 'priority': 4},
    },
}

# Target singolo con due priorità diverse (per _reduce_target_data)
_TARGET_TWO_PRIO: Dict = {
    'Soft':    {'big': {'quantity': 10, 'priority': 2}},
    'Armored': {'big': {'quantity': 10, 'priority': 8}},
}

_MAX_AIRCRAFT:  int = 8
_MAX_MISSIONS:  int = 5
_DIRECTIVE:     str = 'balanced'

# ─────────────────────────────────────────────────────────────────────────────
#  SCENARIO FIXTURES — configurazioni per test di scenario e tabelle
# ─────────────────────────────────────────────────────────────────────────────

# Directory di output PDF (quattro livelli su dalla cartella Test → radice progetto / out)
_OUTPUT_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        *(['..'] * 4), 'out',
    )
)

# ── Strike ────────────────────────────────────────────────────────────────────
_AVAIL_STRIKE_SCENARIO: List[Dict] = [
    {'model': 'F-4E Phantom II',        'loadout': 'Strike',                  'quantity': 12},
    {'model': 'MiG-27K',                'loadout': 'Precision Ground Attack',  'quantity': 12},
    {'model': 'B-52H Stratofortress',   'loadout': 'Heavy Strike Mk-84',       'quantity': 6},
    {'model': 'Su-24M',                 'loadout': 'Heavy Strike',             'quantity': 8},
]
_TARGET_STRIKE_SCENARIO: Dict = {
    'Structure': {
        'big':   {'quantity': 3,  'priority': 10},
        'med':   {'quantity': 6,  'priority': 7},
        'small': {'quantity': 12, 'priority': 7},
    },
}

# ── CAS ───────────────────────────────────────────────────────────────────────
_AVAIL_CAS_SCENARIO: List[Dict] = [
    {'model': 'F-4E Phantom II',          'loadout': 'CAS',                  'quantity': 12},
    {'model': 'MiG-27K',                  'loadout': 'CAS Rocket Attack',    'quantity': 12},
    {'model': 'A-10C II Thunderbolt II',  'loadout': 'Maverick/Gun CAS',     'quantity': 12},
    {'model': 'Su-25T',                   'loadout': 'Anti-Tank Precision',   'quantity': 8},
]
_TARGET_CAS_SCENARIO: Dict = {
    'Soft': {
        'big':   {'quantity': 3,  'priority': 5},
        'med':   {'quantity': 5,  'priority': 6},
        'small': {'quantity': 10, 'priority': 6},
    },
    'Armored': {
        'big':   {'quantity': 2, 'priority': 3},
        'med':   {'quantity': 4, 'priority': 3},
        'small': {'quantity': 5, 'priority': 5},
    },
}

# ── SEAD ──────────────────────────────────────────────────────────────────────
_AVAIL_SEAD_SCENARIO: List[Dict] = [
    {'model': 'F-4E Phantom II',          'loadout': 'CAS',                  'quantity': 12},
    {'model': 'MiG-27K',                  'loadout': 'CAS Rocket Attack',    'quantity': 12},
    {'model': 'A-10C II Thunderbolt II',  'loadout': 'Maverick/Gun CAS',     'quantity': 12},
    {'model': 'Su-25T',                   'loadout': 'Anti-Tank Precision',   'quantity': 8},
]
_TARGET_SEAD_SCENARIO: Dict = {
    'Soft': {
        'big':   {'quantity': 3,  'priority': 5},
        'med':   {'quantity': 5,  'priority': 6},
        'small': {'quantity': 10, 'priority': 6},
    },
    'Armored': {
        'big':   {'quantity': 2, 'priority': 3},
        'med':   {'quantity': 4, 'priority': 3},
        'small': {'quantity': 5, 'priority': 5},
    },
}

# ── Anti_Ship ─────────────────────────────────────────────────────────────────
_AVAIL_ANTISHIP_SCENARIO: List[Dict] = [
    {'model': 'F/A-18C Hornet',  'loadout': 'Anti-Ship',                 'quantity': 12},
    {'model': 'Su-30',           'loadout': 'Anti-Ship',                 'quantity': 12},
    {'model': 'S-3B Viking',     'loadout': 'Anti-Ship Maritime Strike', 'quantity': 8},
    {'model': 'Tu-142',          'loadout': 'Maritime Strike',           'quantity': 7},
]
_TARGET_ANTISHIP_SCENARIO: Dict = {
    'ship': {
        'big':   {'quantity': 4, 'priority': 10},
        'med':   {'quantity': 4, 'priority': 6},
        'small': {'quantity': 6, 'priority': 3},
    },
}

# ── Fighter_Sweep ─────────────────────────────────────────────────────────────
_AVAIL_FIGHTER_SWEEP_SCENARIO: List[Dict] = [
    {'model': 'F-15C Eagle',       'loadout': 'Eagle Sweep',  'quantity': 12},
    {'model': 'Su-27',             'loadout': 'Flanker CAP',  'quantity': 12},
    {'model': 'AJ/ASJ 37 Viggen',  'loadout': 'Air-to-Air',   'quantity': 12},
    {'model': 'MiG-29S',           'loadout': 'CAP',          'quantity': 12},
]
_TARGET_FIGHTER_SWEEP_SCENARIO: Dict = {
    'Aircraft': {
        'big':   {'quantity': 4, 'priority': 10},
        'med':   {'quantity': 4, 'priority': 2},
        'small': {'quantity': 6, 'priority': 1},
    },
}

# ── Intercept ─────────────────────────────────────────────────────────────────
_AVAIL_INTERCEPT_SCENARIO: List[Dict] = [
    {'model': 'F-15C Eagle',  'loadout': 'Eagle Sweep',        'quantity': 12},
    {'model': 'Su-27',        'loadout': 'Flanker CAP',        'quantity': 12},
    {'model': 'MiG-21bis',    'loadout': 'Fishbed CAP',        'quantity': 12},
    {'model': 'MiG-31',       'loadout': 'Foxhound Intercept', 'quantity': 12},
]
_TARGET_INTERCEPT_SCENARIO: Dict = {
    'Aircraft': {
        'small': {'quantity': 10, 'priority': 10},
    },
}

# ── Lista globale degli scenari (usata anche per le tabelle) ──────────────────
_SCENARIO_CONFIGS: List[Dict] = [
    {
        'group':               'Strike',
        'task':                'Strike',
        'availability':        _AVAIL_STRIKE_SCENARIO,
        'target_data':         _TARGET_STRIKE_SCENARIO,
        'max_aircraft_values': [4, 8],
        'max_missions_values': [2, 4],
        'directives':          ['balanced', 'performance_high', 'economy_high'],
    },
    {
        'group':               'CAS',
        'task':                'CAS',
        'availability':        _AVAIL_CAS_SCENARIO,
        'target_data':         _TARGET_CAS_SCENARIO,
        'max_aircraft_values': [3, 6],
        'max_missions_values': [2, 4],
        'directives':          ['balanced', 'performance_high', 'economy_high'],
    },
    {
        'group':               'SEAD',
        'task':                'SEAD',
        'availability':        _AVAIL_SEAD_SCENARIO,
        'target_data':         _TARGET_SEAD_SCENARIO,
        'max_aircraft_values': [3, 6],
        'max_missions_values': [2, 4],
        'directives':          ['balanced', 'performance_high', 'economy_high'],
    },
    {
        'group':               'Anti_Ship',
        'task':                'Anti_Ship',
        'availability':        _AVAIL_ANTISHIP_SCENARIO,
        'target_data':         _TARGET_ANTISHIP_SCENARIO,
        'max_aircraft_values': [6, 10],
        'max_missions_values': [2, 4, 8],
        'directives':          ['balanced', 'performance_high'],
    },
    {
        'group':               'Fighter_Sweep',
        'task':                'Fighter_Sweep',
        'availability':        _AVAIL_FIGHTER_SWEEP_SCENARIO,
        'target_data':         _TARGET_FIGHTER_SWEEP_SCENARIO,
        'max_aircraft_values': [6, 10],
        'max_missions_values': [3, 6],
        'directives':          ['balanced', 'performance_high'],
    },
    {
        'group':               'Intercept',
        'task':                'Intercept',
        'availability':        _AVAIL_INTERCEPT_SCENARIO,
        'target_data':         _TARGET_INTERCEPT_SCENARIO,
        'max_aircraft_values': [6, 10],
        'max_missions_values': [3, 6],
        'directives':          ['balanced', 'performance_high'],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────────────────────────────────────

def _all_loggers_mocked() -> ExitStack:
    """Context manager: mocka tutti i logger necessari per get_aircraft_mission."""
    stack = ExitStack()
    for path in [_LOGGER_MRA, _LOGGER_LO, _LOGGER_AWD, _LOGGER_AD]:
        stack.enter_context(patch(path, MagicMock()))
    return stack


# ─────────────────────────────────────────────────────────────────────────────
#  1. _extract_quantities
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractQuantities(unittest.TestCase):
    """Unit test per _extract_quantities().

    Converte {type: {dim: {'quantity': int, 'priority': int}}} in
    {type: {dim: int}}.  Se il valore per una dimensione è già un intero
    (non dict), viene usato direttamente.
    """

    def test_dict_format_returns_quantities(self):
        """Formato dict → estrae i valori 'quantity'."""
        td = {
            'Soft': {
                'big':   {'quantity': 3, 'priority': 5},
                'small': {'quantity': 7, 'priority': 4},
            }
        }
        result = _extract_quantities(td)
        self.assertEqual(result['Soft']['big'],   3)
        self.assertEqual(result['Soft']['small'], 7)

    def test_int_format_passthrough(self):
        """Formato int (già estratto) → ritorna lo stesso valore."""
        td = {'Soft': {'big': 5, 'med': 3}}
        result = _extract_quantities(td)
        self.assertEqual(result['Soft']['big'], 5)
        self.assertEqual(result['Soft']['med'], 3)

    def test_multi_type_multi_dim(self):
        """Più target_type con più dimensioni → struttura preservata."""
        td = {
            'Soft':    {'big': {'quantity': 3, 'priority': 5},
                        'med': {'quantity': 5, 'priority': 6}},
            'Armored': {'big': {'quantity': 2, 'priority': 3}},
        }
        result = _extract_quantities(td)
        self.assertEqual(result['Soft']['big'],    3)
        self.assertEqual(result['Soft']['med'],    5)
        self.assertEqual(result['Armored']['big'], 2)

    def test_returns_dict(self):
        """Il risultato è sempre un dict."""
        result = _extract_quantities({'Soft': {'big': {'quantity': 1, 'priority': 1}}})
        self.assertIsInstance(result, dict)

    def test_empty_target_data(self):
        """Target data vuoto → dict vuoto."""
        self.assertEqual(_extract_quantities({}), {})

    def test_original_not_mutated(self):
        """L'input originale non viene modificato."""
        td = {'Soft': {'big': {'quantity': 3, 'priority': 5}}}
        _extract_quantities(td)
        self.assertEqual(td['Soft']['big']['quantity'], 3)


# ─────────────────────────────────────────────────────────────────────────────
#  2. _extract_target_lists
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractTargetLists(unittest.TestCase):
    """Unit test per _extract_target_lists().

    Restituisce (types_list, dims_list) senza duplicati.
    """

    def test_returns_tuple_of_two_lists(self):
        """Il risultato è una tupla di due liste."""
        types, dims = _extract_target_lists({'Soft': {'big': {}}})
        self.assertIsInstance(types, list)
        self.assertIsInstance(dims, list)

    def test_single_type_single_dim(self):
        """Un solo type/dim → liste unitarie."""
        types, dims = _extract_target_lists({'Soft': {'big': {'quantity': 3}}})
        self.assertEqual(types, ['Soft'])
        self.assertEqual(dims,  ['big'])

    def test_multi_type_multi_dim_no_duplicates(self):
        """Più type/dim → nessun duplicato nelle liste."""
        td = {
            'Soft':    {'big': {}, 'med': {}},
            'Armored': {'big': {}, 'small': {}},
        }
        types, dims = _extract_target_lists(td)
        self.assertEqual(sorted(types), sorted(['Soft', 'Armored']))
        self.assertEqual(sorted(dims),  sorted(['big', 'med', 'small']))
        self.assertEqual(len(types), len(set(types)))
        self.assertEqual(len(dims),  len(set(dims)))

    def test_aircraft_target(self):
        """Target Aircraft → restituisce (['Aircraft'], dims)."""
        td = {'Aircraft': {'big': {}, 'med': {}, 'small': {}}}
        types, dims = _extract_target_lists(td)
        self.assertIn('Aircraft', types)
        for dim in ('big', 'med', 'small'):
            self.assertIn(dim, dims)

    def test_empty_input(self):
        """Input vuoto → tuple di liste vuote."""
        types, dims = _extract_target_lists({})
        self.assertEqual(types, [])
        self.assertEqual(dims,  [])


# ─────────────────────────────────────────────────────────────────────────────
#  3. _check_mission_requirements
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckMissionRequirements(unittest.TestCase):
    """Unit test per _check_mission_requirements(loadout, mission_requirements).

    Il loadout deve soddisfare per entrambe le fasi (cruise, attack):
      - speed ≥ req speed
      - reference_altitude ≥ req reference_altitude
      - altitude_max ≥ req altitude_max
      - altitude_min ≤ req altitude_min  (loadout può volare abbastanza basso)
      - range(fuel_100%) ≥ req range

    Fixture: F-14A Phoenix Fleet Defense (dati reali da AIRCRAFT_LOADOUTS).
    """

    def test_f14a_passes_lenient_requirements(self):
        """F-14A Phoenix Fleet Defense supera requisiti permissivi → True."""
        self.assertTrue(_check_mission_requirements(_F14A_PHOENIX, _REQ_LENIENT))

    def test_f14a_fails_strict_speed(self):
        """F-14A non raggiunge la velocità richiesta (99999 km/h) → False."""
        self.assertFalse(_check_mission_requirements(_F14A_PHOENIX, _REQ_STRICT_SPEED))

    def test_f14a_fails_strict_range(self):
        """F-14A non raggiunge il range richiesto (999999 km) → False."""
        self.assertFalse(_check_mission_requirements(_F14A_PHOENIX, _REQ_STRICT_RANGE))

    def test_empty_loadout_returns_false(self):
        """Loadout vuoto (dict vuoto) → False (nessuna fase trovata)."""
        self.assertFalse(_check_mission_requirements({}, _REQ_LENIENT))

    def test_missing_cruise_phase_returns_false(self):
        """Loadout senza 'cruise' → False."""
        lo = {'attack': _F14A_PHOENIX['attack']}
        self.assertFalse(_check_mission_requirements(lo, _REQ_LENIENT))

    def test_missing_attack_phase_returns_false(self):
        """Loadout senza 'attack' → False."""
        lo = {'cruise': _F14A_PHOENIX['cruise']}
        self.assertFalse(_check_mission_requirements(lo, _REQ_LENIENT))

    def test_returns_bool(self):
        """Il risultato è sempre un bool."""
        result = _check_mission_requirements(_F14A_PHOENIX, _REQ_LENIENT)
        self.assertIsInstance(result, bool)

    def test_altitude_max_too_low_returns_false(self):
        """Loadout con altitude_max insufficiente → False."""
        req = {
            'cruise': {
                'speed': 100, 'reference_altitude': 1000,
                'altitude_max': 99999,   # richiede molto alta quota
                'altitude_min': 20000, 'range': 100,
            },
            'attack': {
                'speed': 100, 'reference_altitude': 1000,
                'altitude_max': 99999, 'altitude_min': 20000, 'range': 100,
            },
        }
        self.assertFalse(_check_mission_requirements(_F14A_PHOENIX, req))


# ─────────────────────────────────────────────────────────────────────────────
#  4. _usability_met
# ─────────────────────────────────────────────────────────────────────────────

class TestUsabilityMet(unittest.TestCase):
    """Unit test per _usability_met(loadout_usability, required_usability).

    Una condizione required_usability=True significa che la missione richiede
    quella capacità; il loadout deve esporla come True.
    Condizioni required_usability=False vengono ignorate.
    """

    def test_empty_required_always_true(self):
        """Nessun requisito → True (condizione trivialmente soddisfatta)."""
        lo_usab = {'day': True, 'night': False, 'adverse_weather': False}
        self.assertTrue(_usability_met(lo_usab, {}))

    def test_day_required_loadout_supports_day(self):
        """Missione richiede day=True; loadout: day=True → True."""
        lo_usab  = {'day': True,  'night': False, 'adverse_weather': False}
        req_usab = {'day': True,  'night': False, 'adverse_weather': False}
        self.assertTrue(_usability_met(lo_usab, req_usab))

    def test_night_required_loadout_supports_night(self):
        """Missione richiede night=True; loadout: night=True → True."""
        lo_usab  = {'day': True, 'night': True, 'adverse_weather': False}
        req_usab = {'day': True, 'night': True, 'adverse_weather': False}
        self.assertTrue(_usability_met(lo_usab, req_usab))

    def test_night_required_loadout_day_only(self):
        """Missione richiede night=True; loadout: night=False → False."""
        lo_usab  = {'day': True, 'night': False, 'adverse_weather': False}
        req_usab = {'day': True, 'night': True,  'adverse_weather': False}
        self.assertFalse(_usability_met(lo_usab, req_usab))

    def test_adverse_weather_required_not_supported(self):
        """Missione richiede adverse_weather=True; loadout: adverse_weather=False → False."""
        lo_usab  = {'day': True, 'night': True, 'adverse_weather': False}
        req_usab = {'day': True, 'night': False, 'adverse_weather': True}
        self.assertFalse(_usability_met(lo_usab, req_usab))

    def test_all_weather_loadout_all_conditions_required(self):
        """Loadout all-weather; missione richiede tutto → True."""
        lo_usab  = {'day': True, 'night': True, 'adverse_weather': True}
        req_usab = {'day': True, 'night': True, 'adverse_weather': True}
        self.assertTrue(_usability_met(lo_usab, req_usab))

    def test_condition_false_in_required_is_ignored(self):
        """Condizione required=False viene ignorata anche se loadout=False."""
        lo_usab  = {'day': True, 'night': False, 'adverse_weather': False}
        req_usab = {'day': False, 'night': False, 'adverse_weather': False}
        # Nessuna condizione richiesta → True
        self.assertTrue(_usability_met(lo_usab, req_usab))

    def test_returns_bool(self):
        """Il risultato è sempre un bool."""
        result = _usability_met({'day': True}, {'day': True})
        self.assertIsInstance(result, bool)


# ─────────────────────────────────────────────────────────────────────────────
#  5. _compute_score
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeScore(unittest.TestCase):
    """Unit test per _compute_score(combat_score, aircraft_cost_M, loadout_cost_k, directive).

    Formula: score = combat * (ws + wc * REFERENCE_COST_K / max(1, total_cost_k))
    dove total_cost_k = aircraft_cost_M * 1000 + loadout_cost_k.
    """

    def test_zero_combat_score_returns_zero(self):
        """combat_score=0 → score=0 per qualsiasi directive."""
        for d in _DIRECTIVE_WEIGHTS:
            with self.subTest(directive=d):
                self.assertEqual(_compute_score(0.0, 10.0, 100.0, d), 0.0)

    def test_performance_high_ignores_cost(self):
        """'performance_high': ws=1, wc=0 → score = combat_score (indipendente dal costo)."""
        score_cheap     = _compute_score(1.0,   6.0,    0.0, 'performance_high')
        score_expensive = _compute_score(1.0, 300.0, 2050.0, 'performance_high')
        self.assertAlmostEqual(score_cheap,     1.0, places=9)
        self.assertAlmostEqual(score_expensive, 1.0, places=9)

    def test_performance_high_equals_combat_score(self):
        """'performance_high': score == combat_score per qualsiasi costo."""
        for combat in (0.0, 0.5, 1.0, 2.5):
            with self.subTest(combat=combat):
                self.assertAlmostEqual(
                    _compute_score(combat, 50.0, 100.0, 'performance_high'),
                    combat, places=9,
                )

    def test_balanced_cheaper_scores_higher(self):
        """'balanced': aereo più economico (stesso combat_score) → score maggiore."""
        score_cheap     = _compute_score(1.0,   6.0,   0.0, 'balanced')
        score_expensive = _compute_score(1.0, 300.0, 2050.0, 'balanced')
        self.assertGreater(score_cheap, score_expensive)

    def test_economy_high_heavily_favors_cheap(self):
        """'economy_high': aereo economico ha score molto maggiore del costoso."""
        score_cheap     = _compute_score(1.0,   6.0,    0.0, 'economy_high')
        score_expensive = _compute_score(1.0, 300.0, 2050.0, 'economy_high')
        self.assertGreater(score_cheap, score_expensive)

    def test_non_negative_for_positive_inputs(self):
        """Score >= 0 per combat_score >= 0 e qualsiasi directive."""
        for d in _DIRECTIVE_WEIGHTS:
            with self.subTest(directive=d):
                score = _compute_score(0.5, 50.0, 500.0, d)
                self.assertGreaterEqual(score, 0.0)

    def test_invalid_directive_raises_key_error(self):
        """Directive sconosciuta → KeyError."""
        with self.assertRaises(KeyError):
            _compute_score(1.0, 10.0, 100.0, 'INVALID_DIRECTIVE_XYZ')

    def test_all_directives_return_float(self):
        """Tutti i directives validi restituiscono un float."""
        for d in _DIRECTIVE_WEIGHTS:
            with self.subTest(directive=d):
                result = _compute_score(0.8, 30.0, 250.0, d)
                self.assertIsInstance(result, float)


# ─────────────────────────────────────────────────────────────────────────────
#  6. _reduce_target_data
# ─────────────────────────────────────────────────────────────────────────────

class TestReduceTargetData(unittest.TestCase):
    """Unit test per _reduce_target_data(target_data, reduction_ratio).

    La riduzione è proporzionale alla priorità: target ad alta priorità
    perdono meno quantità rispetto ai target a bassa priorità.

    Formula per singolo dim: quantity = max(0, round(qty * ratio * (1 + weight)))
      con weight = priority / total_priority.

    Con due target di priorità diverse (2 e 8, totale=10):
      low  (prio=2): weight=0.2, qty = round(qty * ratio * 1.2)
      high (prio=8): weight=0.8, qty = round(qty * ratio * 1.8)
    """

    def test_returns_dict(self):
        """Restituisce un dizionario."""
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.5)
        self.assertIsInstance(result, dict)

    def test_original_not_mutated(self):
        """L'originale non viene modificato (deep copy)."""
        td = {
            'Soft': {'big': {'quantity': 10, 'priority': 5}},
        }
        _ = _reduce_target_data(td, 0.5)
        self.assertEqual(td['Soft']['big']['quantity'], 10)

    def test_zero_ratio_returns_zero_quantities(self):
        """reduction_ratio=0.0 → tutte le quantità diventano 0."""
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.0)
        for category, dims in result.items():
            for dim, data in dims.items():
                with self.subTest(category=category, dim=dim):
                    self.assertEqual(data['quantity'], 0)

    def test_high_priority_retains_more_than_low_priority(self):
        """Alta priorità perde meno quantità della bassa priorità (stesso qty iniziale)."""
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.5)
        qty_low  = result['Soft']['big']['quantity']     # priority=2
        qty_high = result['Armored']['big']['quantity']  # priority=8
        self.assertGreater(qty_high, qty_low)

    def test_structure_preserved(self):
        """La struttura (type → dim → dict) è preservata."""
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.5)
        self.assertIn('Soft',    result)
        self.assertIn('Armored', result)
        self.assertIn('big', result['Soft'])
        self.assertIn('big', result['Armored'])

    def test_quantities_are_non_negative(self):
        """Tutte le quantità risultanti sono >= 0."""
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.5)
        for category, dims in result.items():
            for dim, data in dims.items():
                with self.subTest(category=category, dim=dim):
                    self.assertGreaterEqual(data['quantity'], 0)

    def test_priority_preserved_in_output(self):
        """La chiave 'priority' è conservata nel risultato."""
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.5)
        self.assertIn('priority', result['Soft']['big'])
        self.assertIn('priority', result['Armored']['big'])

    def test_two_prio_exact_values(self):
        """Verifica i valori esatti per reduction_ratio=0.5 con due priorità (2 e 8).

        total_priority_weight = 10
        Soft/big    (prio=2): weight=0.2, qty = round(10 * 0.5 * 1.2) = round(6.0) = 6
        Armored/big (prio=8): weight=0.8, qty = round(10 * 0.5 * 1.8) = round(9.0) = 9
        """
        result = _reduce_target_data(_TARGET_TWO_PRIO, 0.5)
        self.assertEqual(result['Soft']['big']['quantity'],    6)
        self.assertEqual(result['Armored']['big']['quantity'], 9)


# ─────────────────────────────────────────────────────────────────────────────
#  7. get_aircraft_mission — target terrestre (Strike / CAS)
# ─────────────────────────────────────────────────────────────────────────────

class TestGetAircraftMission(unittest.TestCase):
    """Unit test per get_aircraft_mission() con target terrestre.

    Verifica struttura del risultato, validazione input, filtering per
    performance/usability, ordinamento per score e comportamento con
    directive differenti.

    Tutti i logger sono mockati tramite _all_loggers_mocked().
    """

    def setUp(self):
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    # ── Struttura del risultato ───────────────────────────────────────────────

    def test_returns_dict(self):
        """Input valido → restituisce un dict."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertIsInstance(result, dict)

    def test_result_has_fully_compliant_key(self):
        """Il risultato contiene la chiave 'fully_compliant'."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertIn('fully_compliant', result)

    def test_result_has_derated_key(self):
        """Il risultato contiene la chiave 'derated'."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertIn('derated', result)

    def test_both_values_are_lists(self):
        """'fully_compliant' e 'derated' sono entrambe liste."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertIsInstance(result['fully_compliant'], list)
        self.assertIsInstance(result['derated'],         list)

    def test_entries_have_required_fields(self):
        """Ogni entry nelle liste ha 'aircraft_model', 'loadout', 'score'."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        all_entries = result['fully_compliant'] + result['derated']
        for entry in all_entries:
            with self.subTest(entry=entry):
                self.assertIn('aircraft_model', entry)
                self.assertIn('loadout',        entry)
                self.assertIn('score',          entry)

    def test_scores_are_non_negative(self):
        """Tutti gli score nelle due liste sono >= 0."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        for entry in result['fully_compliant'] + result['derated']:
            with self.subTest(model=entry['aircraft_model']):
                self.assertGreaterEqual(entry['score'], 0.0)

    def test_fully_compliant_sorted_descending(self):
        """'fully_compliant' è ordinata per score decrescente."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        scores = [e['score'] for e in result['fully_compliant']]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_derated_sorted_descending(self):
        """'derated' è ordinata per score decrescente."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        scores = [e['score'] for e in result['derated']]
        self.assertEqual(scores, sorted(scores, reverse=True))

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_invalid_directive_raises_value_error(self):
        """Directive sconosciuta → ValueError."""
        with self.assertRaises(ValueError):
            get_aircraft_mission(
                'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
                _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, 'INVALID_DIR',
            )

    def test_none_task_raises_type_error(self):
        """task=None → TypeError."""
        with self.assertRaises(TypeError):
            get_aircraft_mission(
                None, _AVAIL_STRIKE, _REQ_LENIENT,
                _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
            )

    def test_invalid_task_string_raises_value_error(self):
        """Task non in AIR_TASK → ValueError."""
        with self.assertRaises(ValueError):
            get_aircraft_mission(
                'INVALID_TASK_XYZ', _AVAIL_STRIKE, _REQ_LENIENT,
                _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
            )

    # ── Filtering ─────────────────────────────────────────────────────────────

    def test_strict_speed_filters_all_aircraft(self):
        """Requisito velocità irraggiungibile → entrambe le liste vuote."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_STRICT_SPEED,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertEqual(result['fully_compliant'], [])
        self.assertEqual(result['derated'],         [])

    def test_strict_range_filters_all_aircraft(self):
        """Requisito range irraggiungibile → entrambe le liste vuote."""
        result = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_STRICT_RANGE,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertEqual(result['fully_compliant'], [])
        self.assertEqual(result['derated'],         [])

    def test_empty_availability_returns_empty_lists(self):
        """Lista disponibilità vuota → entrambe le liste vuote."""
        result = get_aircraft_mission(
            'Strike', [], _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertEqual(result['fully_compliant'], [])
        self.assertEqual(result['derated'],         [])

    def test_unknown_model_skipped(self):
        """Modello sconosciuto → skippato (non appare nel risultato)."""
        avail = [{'model': 'UNKNOWN_XYZ', 'loadout': 'Any Loadout', 'quantity': 5}]
        result = get_aircraft_mission(
            'Strike', avail, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        all_models = [e['aircraft_model'] for e in
                      result['fully_compliant'] + result['derated']]
        self.assertNotIn('UNKNOWN_XYZ', all_models)

    def test_unknown_loadout_skipped(self):
        """Loadout sconosciuto per modello valido → skippato."""
        avail = [{'model': 'F-15E Strike Eagle', 'loadout': 'NONEXISTENT_LOADOUT', 'quantity': 5}]
        result = get_aircraft_mission(
            'Strike', avail, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertEqual(result['fully_compliant'], [])
        self.assertEqual(result['derated'],         [])

    # ── Directives ───────────────────────────────────────────────────────────

    def test_all_directives_execute_without_exception(self):
        """Tutti i directive validi eseguono senza eccezione."""
        for directive in _DIRECTIVE_WEIGHTS:
            with self.subTest(directive=directive):
                try:
                    get_aircraft_mission(
                        'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
                        _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, directive,
                    )
                except Exception as exc:
                    self.fail(f"directive={directive!r} ha sollevato: {exc}")

    def test_performance_high_and_economy_high_give_different_scores(self):
        """'performance_high' e 'economy_high' producono score diversi con due aircraft."""
        res_perf = get_aircraft_mission(
            'Strike', _AVAIL_MIXED, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, 'performance_high',
        )
        res_econ = get_aircraft_mission(
            'Strike', _AVAIL_MIXED, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, 'economy_high',
        )
        scores_perf = {e['aircraft_model']: e['score'] for e in
                       res_perf['fully_compliant'] + res_perf['derated']}
        scores_econ = {e['aircraft_model']: e['score'] for e in
                       res_econ['fully_compliant'] + res_econ['derated']}
        # Almeno un modello comune deve avere score diverso tra i due directives
        common = set(scores_perf) & set(scores_econ)
        if common:
            different = any(
                abs(scores_perf[m] - scores_econ[m]) > 1e-9 for m in common
            )
            self.assertTrue(different,
                "I due directives non producono score diversi su nessun modello comune.")

    def test_usability_night_required_filters_day_only_loadout(self):
        """Missione notturna: loadout day-only viene escluso."""
        # F-15E Iron Bomb Strike: usability.night=False → escluso se night richiesto
        result_night = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_NIGHT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        result_day = get_aircraft_mission(
            'Strike', _AVAIL_STRIKE, _REQ_LENIENT,
            _TARGET_GROUND, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        all_night = [e['aircraft_model'] for e in
                     result_night['fully_compliant'] + result_night['derated']]
        all_day = [e['aircraft_model'] for e in
                   result_day['fully_compliant'] + result_day['derated']]
        # La lista notturna non può contenere più modelli di quella diurna
        self.assertLessEqual(len(all_night), len(all_day))


# ─────────────────────────────────────────────────────────────────────────────
#  8. get_aircraft_mission — target Aircraft (CAP / Intercept)
# ─────────────────────────────────────────────────────────────────────────────

class TestGetAircraftMissionAircraft(unittest.TestCase):
    """Unit test per get_aircraft_mission() con target Aircraft (aria-aria).

    Verifica che il sistema funzioni correttamente per missioni CAP con
    target_data di tipo Aircraft: i loadout con AAM devono essere valutati
    positivamente e comparire nel risultato.

    Fixture: F-14A Tomcat / Phoenix Fleet Defense, task='CAP'.
    """

    def setUp(self):
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    def test_cap_aircraft_target_returns_dict(self):
        """CAP + target Aircraft → restituisce un dict."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertIsInstance(result, dict)

    def test_cap_aircraft_target_has_required_keys(self):
        """Il risultato ha le chiavi 'fully_compliant' e 'derated'."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        self.assertIn('fully_compliant', result)
        self.assertIn('derated',         result)

    def test_cap_f14a_appears_in_result(self):
        """F-14A Tomcat con Phoenix Fleet Defense compare nel risultato."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        all_models = [e['aircraft_model'] for e in
                      result['fully_compliant'] + result['derated']]
        self.assertIn('F-14A Tomcat', all_models)

    def test_cap_aircraft_entries_have_required_fields(self):
        """Ogni entry ha 'aircraft_model', 'loadout', 'score'."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        all_entries = result['fully_compliant'] + result['derated']
        for entry in all_entries:
            with self.subTest(entry=entry):
                self.assertIn('aircraft_model', entry)
                self.assertIn('loadout',        entry)
                self.assertIn('score',          entry)

    def test_cap_aircraft_scores_non_negative(self):
        """Tutti gli score per CAP + Aircraft >= 0."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        for entry in result['fully_compliant'] + result['derated']:
            with self.subTest(model=entry['aircraft_model']):
                self.assertGreaterEqual(entry['score'], 0.0)

    def test_cap_aircraft_score_positive(self):
        """F-14A CAP con Phoenix Fleet Defense (8 AAM) → score > 0."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        all_entries = result['fully_compliant'] + result['derated']
        f14a_entries = [e for e in all_entries if e['aircraft_model'] == 'F-14A Tomcat']
        self.assertTrue(f14a_entries, "F-14A Tomcat non trovato nel risultato.")
        for entry in f14a_entries:
            with self.subTest(loadout=entry['loadout']):
                self.assertGreater(entry['score'], 0.0)

    def test_cap_aircraft_sorted_descending(self):
        """Entrambe le liste risultanti sono ordinate per score decrescente."""
        result = get_aircraft_mission(
            'CAP', _AVAIL_CAP, _REQ_LENIENT,
            _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
        )
        for list_name in ('fully_compliant', 'derated'):
            scores = [e['score'] for e in result[list_name]]
            with self.subTest(list_name=list_name):
                self.assertEqual(scores, sorted(scores, reverse=True))

    def test_all_tasks_execute_without_exception(self):
        """Tutti i task validi (CAP, Intercept, Escort, ...) eseguono senza eccezione."""
        from Code.Dynamic_War_Manager.Source.Context.Context import AIR_TASK
        for task in AIR_TASK:
            with self.subTest(task=task):
                try:
                    get_aircraft_mission(
                        task, _AVAIL_CAP, _REQ_LENIENT,
                        _TARGET_AIRCRAFT, _MAX_AIRCRAFT, _MAX_MISSIONS, _DIRECTIVE,
                    )
                except Exception as exc:
                    self.fail(f"task={task!r} ha sollevato: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
#  9. Scenario base class + 6 scenari parametrici
# ─────────────────────────────────────────────────────────────────────────────

class _ScenarioTestBase(unittest.TestCase):
    """Base class per i test di scenario parametrici.

    Le sottoclassi devono definire `_CFG` come uno degli elementi di
    `_SCENARIO_CONFIGS`.  I metodi di test iterano tutte le combinazioni
    (max_aircraft × max_missions × directive) tramite subTest.
    """

    _CFG: Dict = {}   # sovrascritta da ogni sottoclasse

    def setUp(self) -> None:
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self) -> None:
        self._mock_ctx.__exit__(None, None, None)

    def _run_for_params(self, max_aircraft: int, max_missions: int, directive: str) -> Dict:
        return get_aircraft_mission(
            self._CFG['task'],
            self._CFG['availability'],
            _REQ_LENIENT,
            self._CFG['target_data'],
            max_aircraft,
            max_missions,
            directive,
        )

    def _combinations(self):
        cfg = self._CFG
        for ma in cfg['max_aircraft_values']:
            for mm in cfg['max_missions_values']:
                for directive in cfg['directives']:
                    yield ma, mm, directive

    # ── test comuni ────────────────────────────────────────────────────────

    def test_result_structure_all_combinations(self):
        """Tutte le combinazioni restituiscono un dict con le chiavi attese."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                self.assertIsInstance(result, dict)
                self.assertIn('fully_compliant', result)
                self.assertIn('derated', result)
                self.assertIsInstance(result['fully_compliant'], list)
                self.assertIsInstance(result['derated'], list)

    def test_entries_have_required_fields(self):
        """Ogni entry ha 'aircraft_model', 'loadout', 'score' per tutte le combinazioni."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for entry in result['fully_compliant'] + result['derated']:
                    self.assertIn('aircraft_model', entry)
                    self.assertIn('loadout',        entry)
                    self.assertIn('score',          entry)

    def test_scores_non_negative(self):
        """Tutti gli score >= 0 per tutte le combinazioni."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for entry in result['fully_compliant'] + result['derated']:
                    self.assertGreaterEqual(entry['score'], 0.0)

    def test_lists_sorted_descending(self):
        """'fully_compliant' e 'derated' sono ordinate per score decrescente."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for list_name in ('fully_compliant', 'derated'):
                    scores = [e['score'] for e in result[list_name]]
                    self.assertEqual(scores, sorted(scores, reverse=True))

    def test_performance_high_vs_economy_high_differ(self):
        """'performance_high' e 'economy_high' producono score diversi (se entrambi nel CFG)."""
        directives = self._CFG['directives']
        if 'performance_high' not in directives or 'economy_high' not in directives:
            self.skipTest("Lo scenario non include entrambe le directive.")
        ma = self._CFG['max_aircraft_values'][0]
        mm = self._CFG['max_missions_values'][0]
        res_perf = self._run_for_params(ma, mm, 'performance_high')
        res_econ = self._run_for_params(ma, mm, 'economy_high')
        scores_p = {e['aircraft_model']: e['score']
                    for e in res_perf['fully_compliant'] + res_perf['derated']}
        scores_e = {e['aircraft_model']: e['score']
                    for e in res_econ['fully_compliant'] + res_econ['derated']}
        common = set(scores_p) & set(scores_e)
        if not common:
            return   # nessun modello comune, test non applicabile
        different = any(abs(scores_p[m] - scores_e[m]) > 1e-9 for m in common)
        self.assertTrue(different,
            "performance_high ed economy_high producono score identici su tutti i modelli.")


class TestStrikeScenario(_ScenarioTestBase):
    """Scenario Strike: F-4E, MiG-27K, B-52H, Su-24M — target Structure."""
    _CFG = _SCENARIO_CONFIGS[0]


class TestCASScenario(_ScenarioTestBase):
    """Scenario CAS: F-4E, MiG-27K, A-10C II, Su-25T — target Soft+Armored."""
    _CFG = _SCENARIO_CONFIGS[1]


class TestSEADScenario(_ScenarioTestBase):
    """Scenario SEAD: stessi loadout CAS — verifica ranking con task SEAD."""
    _CFG = _SCENARIO_CONFIGS[2]


class TestAntiShipScenario(_ScenarioTestBase):
    """Scenario Anti_Ship: F/A-18C, Su-30, S-3B Viking, Tu-142 — target ship."""
    _CFG = _SCENARIO_CONFIGS[3]


class TestFighterSweepScenario(_ScenarioTestBase):
    """Scenario Fighter_Sweep: F-15C, Su-27, Viggen, MiG-29S — target Aircraft."""
    _CFG = _SCENARIO_CONFIGS[4]


class TestInterceptScenario(_ScenarioTestBase):
    """Scenario Intercept: F-15C, Su-27, MiG-21bis, MiG-31 — target Aircraft small."""
    _CFG = _SCENARIO_CONFIGS[5]


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — utilità condivise
# ─────────────────────────────────────────────────────────────────────────────

def _format_target_str(target_data: Dict) -> str:
    """Ritorna una rappresentazione compatta di target_data."""
    parts = []
    for t_type, dims in target_data.items():
        dim_parts = [
            f"{dim}:{info['quantity']}(p{info['priority']})"
            for dim, info in dims.items()
        ]
        parts.append(f"{t_type}[{', '.join(dim_parts)}]")
    return '  '.join(parts)


def _build_mission_rows(cfg: Dict, max_aircraft: int, max_missions: int, directive: str) -> List[Dict]:
    """Chiama get_aircraft_mission e ritorna righe flat per la tabella."""
    with _all_loggers_mocked():
        result = get_aircraft_mission(
            cfg['task'],
            cfg['availability'],
            _REQ_LENIENT,
            cfg['target_data'],
            max_aircraft,
            max_missions,
            directive,
        )
    rows = []
    for entry in result['fully_compliant']:
        rows.append({
            'model':   entry['aircraft_model'],
            'loadout': entry['loadout'],
            'score':   entry['score'],
            'status':  'fully_compliant',
        })
    for entry in result['derated']:
        rows.append({
            'model':   entry['aircraft_model'],
            'loadout': entry['loadout'],
            'score':   entry['score'],
            'status':  'derated',
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — stampa a terminale
# ─────────────────────────────────────────────────────────────────────────────

def _print_scenario_table_terminal(
    cfg: Dict, max_aircraft: int, max_missions: int, directive: str
) -> None:
    """Stampa a terminale la tabella risultato per una combinazione di parametri."""
    rows = _build_mission_rows(cfg, max_aircraft, max_missions, directive)
    W = 96
    print(f"\n{'═' * W}")
    print(
        f"  Gruppo: {cfg['group']}  |  Task: {cfg['task']}"
        f"  |  max_aircraft: {max_aircraft}"
        f"  |  max_missions: {max_missions}"
        f"  |  directive: {directive}"
    )
    print(f"  Target: {_format_target_str(cfg['target_data'])}")
    print(f"{'─' * W}")
    if not rows:
        print("  (nessun risultato)")
        return
    hdr = f"  {'#':>3}  {'Aeromobile':<32}  {'Loadout':<28}  {'Score':>8}  {'Status':<16}"
    print(hdr)
    print(f"  {'─'*3}  {'─'*32}  {'─'*28}  {'─'*8}  {'─'*16}")
    for i, row in enumerate(rows, start=1):
        print(
            f"  {i:>3}  {row['model']:<32}  {row['loadout']:<28}"
            f"  {row['score']:>8.4f}  {row['status']:<16}"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — salvataggio PDF
# ─────────────────────────────────────────────────────────────────────────────

def _setup_matplotlib():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        return plt, PdfPages
    except ImportError:
        return None, None


def _header_style(tbl, n_cols: int) -> None:
    """Intestazione tabella: sfondo scuro, testo bianco in grassetto."""
    for col in range(n_cols):
        tbl[0, col].set_facecolor("#2c3e50")
        tbl[0, col].set_text_props(color="white", fontweight="bold")


def save_mission_scenario_tables_pdf(output_path: str) -> None:
    """Salva MRA_Scenario_Tables.pdf — una pagina per ogni combinazione di parametri.

    Ogni pagina riporta nel titolo: gruppo, task, max_aircraft, max_missions,
    directive e target_data.  Le colonne della tabella sono:
      #  |  Aeromobile  |  Loadout  |  Score  |  Status
    con heatmap RdYlGn sulla colonna Score (verde=alto, rosso=basso).
    """
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    col_labels = ["#", "Aeromobile", "Loadout", "Score", "Status"]
    n_cols = len(col_labels)

    with PdfPages(output_path) as pdf:
        for cfg in _SCENARIO_CONFIGS:
            for ma in cfg['max_aircraft_values']:
                for mm in cfg['max_missions_values']:
                    for directive in cfg['directives']:
                        rows = _build_mission_rows(cfg, ma, mm, directive)

                        cell_text   = []
                        cell_colors = []

                        scores = [r['score'] for r in rows] if rows else []
                        max_s  = max(scores) if scores else 1.0
                        min_s  = min(scores) if scores else 0.0
                        rng    = (max_s - min_s) if max_s != min_s else 1.0

                        if not rows:
                            cell_text.append(["—", "(nessun risultato)", "", "", ""])
                            cell_colors.append(["#f5f5f5"] * n_cols)
                        else:
                            for i, row in enumerate(rows, start=1):
                                score_str = f"{row['score']:.4f}"
                                cell_text.append([
                                    str(i),
                                    row['model'],
                                    row['loadout'],
                                    score_str,
                                    row['status'],
                                ])
                                norm = (row['score'] - min_s) / rng
                                score_color = plt.cm.RdYlGn(norm)
                                status_bg   = "#d4edda" if row['status'] == 'fully_compliant' else "#fff3cd"
                                cell_colors.append([
                                    "#f5f5f5", "#f0f4f8", "#f0f4f8",
                                    score_color, status_bg,
                                ])

                        n_rows = len(cell_text)
                        fig_w  = max(16.0, 2.2 * n_cols)
                        fig_h  = max(4.0, 0.40 * n_rows + 3.5)

                        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                        ax.axis("off")
                        target_str = _format_target_str(cfg['target_data'])
                        ax.set_title(
                            f"Gruppo: {cfg['group']}  |  Task: {cfg['task']}"
                            f"  |  max_aircraft: {ma}"
                            f"  |  max_missions: {mm}"
                            f"  |  directive: {directive}\n"
                            f"Target: {target_str}",
                            fontsize=9, fontweight="bold", pad=14,
                        )

                        tbl = ax.table(
                            cellText=cell_text,
                            colLabels=col_labels,
                            cellColours=cell_colors,
                            loc="center",
                            cellLoc="center",
                        )
                        tbl.auto_set_font_size(False)
                        tbl.set_fontsize(8)
                        tbl.auto_set_column_width(list(range(n_cols)))
                        _header_style(tbl, n_cols)
                        plt.tight_layout()
                        pdf.savefig(fig, bbox_inches="tight")
                        plt.close(fig)

    print(f"[PDF] MRA_Scenario_Tables → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in (
        TestExtractQuantities,
        TestExtractTargetLists,
        TestCheckMissionRequirements,
        TestUsabilityMet,
        TestComputeScore,
        TestReduceTargetData,
        TestGetAircraftMission,
        TestGetAircraftMissionAircraft,
        # Scenari parametrici
        TestStrikeScenario,
        TestCASScenario,
        TestSEADScenario,
        TestAntiShipScenario,
        TestFighterSweepScenario,
        TestInterceptScenario,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def _run_tables_terminal() -> None:
    """Stampa a terminale le tabelle di risultato per tutti gli scenari."""
    for cfg in _SCENARIO_CONFIGS:
        print(f"\n{'#' * 96}")
        print(f"  SCENARIO: {cfg['group']}  (task={cfg['task']})")
        print(f"{'#' * 96}")
        for ma in cfg['max_aircraft_values']:
            for mm in cfg['max_missions_values']:
                for directive in cfg['directives']:
                    _print_scenario_table_terminal(cfg, ma, mm, directive)
    print()


def _run_tables_pdf() -> None:
    """Salva le tabelle di scenario in PDF."""
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(_OUTPUT_DIR, "MRA_Scenario_Tables.pdf")
    save_mission_scenario_tables_pdf(out_path)


# ─────────────────────────────────────────────────────────────────────────────
#  MENU INTERATTIVO
# ─────────────────────────────────────────────────────────────────────────────

_MENU_ITEMS = [
    ("Esegui i test unitari",            _run_tests),
    ("Stampa le tabelle a terminale",    _run_tables_terminal),
    ("Salva le tabelle in PDF",          _run_tables_pdf),
    ("Esegui test + stampa a terminale", None),
    ("Esegui test + salva PDF",          None),
    ("Stampa a terminale + salva PDF",   None),
    ("Tutto (test + terminale + PDF)",   None),
    ("Esci",                             None),
]


def _print_menu() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   Test_Military_Resources_Assigner  —  Menu principale      ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    for idx, (label, _) in enumerate(_MENU_ITEMS, start=1):
        print(f"║  {idx}.  {label:<55}║")
    print("╚══════════════════════════════════════════════════════════════╝")


def _ask_choice() -> int:
    n = len(_MENU_ITEMS)
    while True:
        try:
            raw = input(f"\nScelta [1-{n}]: ").strip()
            choice = int(raw)
            if 1 <= choice <= n:
                return choice
            print(f"  Inserire un numero tra 1 e {n}.")
        except (ValueError, EOFError):
            print("  Input non valido. Riprovare.")


def _interactive_menu() -> None:
    test_result = None
    while True:
        _print_menu()
        choice = _ask_choice()
        label = _MENU_ITEMS[choice - 1][0]
        print(f"\n▶  {label}\n")

        if choice == 1:
            test_result = _run_tests()
        elif choice == 2:
            _run_tables_terminal()
        elif choice == 3:
            _run_tables_pdf()
        elif choice == 4:
            test_result = _run_tests()
            _run_tables_terminal()
        elif choice == 5:
            test_result = _run_tests()
            _run_tables_pdf()
        elif choice == 6:
            _run_tables_terminal()
            _run_tables_pdf()
        elif choice == 7:
            test_result = _run_tests()
            _run_tables_terminal()
            _run_tables_pdf()
        elif choice == 8:
            print("Uscita.")
            break

        input("\nPremi INVIO per tornare al menu...")

    if test_result is not None:
        sys.exit(0 if test_result.wasSuccessful() else 1)


if __name__ == '__main__':
    if '--tests-only' in sys.argv:
        result = _run_tests()
        sys.exit(0 if result.wasSuccessful() else 1)
    elif '--tables-only' in sys.argv:
        _run_tables_terminal()
        _run_tables_pdf()
    else:
        _interactive_menu()
