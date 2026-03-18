"""
Test_Air_Resources_Assigner.py
=====================================
Unit tests per il modulo Air_Resources_Assigner.py.

Funzioni testate
----------------
  Helpers privati (unit test puri, nessun mock):
    _extract_quantities           – conversione target_data → {type: {dim: int}}
    _extract_target_lists         – estrazione liste type/dim da target_data
    _check_mission_requirements   – verifica requisiti di performance (cruise/attack)
    _usability_met                – verifica condizioni di usabilità (day/night/aw)
    _compute_score                – calcolo score ponderato combat × costo
    _reduce_target_data           – riduzione proporzionale target per priorità
    _find_weapon_in_availability  – ricerca weapon in struttura {type:{name:qty}}
    _pylons_to_weapons_dict       – converti pylons {id:[name,qty]} → {name:total_qty}
    _loadout_availability         – n° di loadout allestibili con armi disponibili
    _reduction_weapons_availability – sottrai armi dalla disponibilità (atomico)
    _increase_weapons_availability  – aggiungi armi alla disponibilità

  Funzioni pubbliche (test con mock del logger):
    get_aircraft_mission          – selezione e ranking aircraft/loadout per missione
                                    (include test con target terrestre e target Aircraft)
    get_loadouts_availability     – verifica e assegna loadout in base alle armi

Dati di riferimento
-------------------
  weapons_availability: basata su _WEAPONS_AVAILABILITY['air_weapons'] (Initial_Context.py)
  loadouts: AIRCRAFT_LOADOUTS (Aircraft_Loadouts.py)
  Aereo di riferimento: F-14A Tomcat / "Phoenix Fleet Defense"
    pyloni: 4x AIM-54A-MK47, 2x AIM-9L, 2x AIM-7M

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Air_Resources_Assigner.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Air_Resources_Assigner.py
    python  Code/Dynamic_War_Manager/Source/Test/Test_Air_Resources_Assigner.py --tests-only
"""

import copy
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

_LOGGER_MRA   = "Code.Dynamic_War_Manager.Source.Logic.Air_Resources_Assigner.logger"
_LOGGER_LO    = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts.logger"
_LOGGER_AWD   = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data.logger"
_LOGGER_AD    = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Dynamic_War_Manager.Source.Logic.Air_Resources_Assigner import (
    get_aircraft_mission,
    get_loadouts_availability,
    _extract_quantities,
    _extract_target_lists,
    _check_mission_requirements,
    _usability_met,
    _compute_score,
    _reduce_target_data,
    _find_weapon_in_availability,
    _pylons_to_weapons_dict,
    _loadout_availability,
    _reduction_weapons_availability,
    _increase_weapons_availability,
    _DIRECTIVE_WEIGHTS,
    _REFERENCE_COST_K,
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS
from Code.Dynamic_War_Manager.Source.Context.Initial_Context import _WEAPONS_AVAILABILITY

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
        'altitude_max':        0,       # 0 → req.altitude_max ≤ lo.altitude_min sempre vero
        'altitude_min':        20000,   # loadout alt_min ≤ 20000 → supera il check
        'range':               100,
    },
    'attack': {
        'speed':               400,
        'reference_altitude':  3000,
        'altitude_max':        0,       # 0 → req.altitude_max ≤ lo.altitude_min sempre vero
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
        'altitude_max': 0, 'altitude_min': 20000, 'range': 100,
    },
    'attack': {
        'speed': 400, 'reference_altitude': 3000,
        'altitude_max': 0, 'altitude_min': 20000, 'range': 100,
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

# ── Weapons availability — basata su _WEAPONS_AVAILABILITY['air_weapons'] ─────
#
# Aereo di riferimento: F-14A Tomcat / "Phoenix Fleet Defense"
#   pyloni: 4x AIM-54A-MK47, 2x AIM-9L, 2x AIM-7M
#
# Struttura: {weapon_type: {weapon_name: quantity}}
# La struttura specchia _WEAPONS_AVAILABILITY['air_weapons'] da Initial_Context.py.

# Tutti i tipi di arma con quantità zero, usato come base per costruire i fixture.
_WEAPONS_AVAIL_EMPTY_TYPES: Dict = {
    'MISSILES_AAM': {},
    'MISSILES_ASM': {},
    'BOMBS':        {},
    'ROCKETS':      {},
    'CANNONS':      {},
    'MACHINE_GUNS': {},
}

# Sufficiente per esattamente 2 loadout "Phoenix Fleet Defense":
#   AIM-54A-MK47: 8 // 4 = 2,  AIM-9L: 4 // 2 = 2,  AIM-7M: 4 // 2 = 2
_WEAPONS_AVAIL_NOMINAL: Dict = {
    'MISSILES_AAM': {
        'AIM-54A-MK47': 8,   # 8 // 4 = 2 loadout
        'AIM-9L':        4,   # 4 // 2 = 2 loadout
        'AIM-7M':        4,   # 4 // 2 = 2 loadout
    },
    'MISSILES_ASM': {},
    'BOMBS':        {},
    'ROCKETS':      {},
    'CANNONS':      {},
    'MACHINE_GUNS': {},
}

# AIM-7M è il fattore limitante (1 loadout):
#   AIM-54A-MK47: 12 // 4 = 3,  AIM-9L: 8 // 2 = 4,  AIM-7M: 2 // 2 = 1
_WEAPONS_AVAIL_AIM7_LIMITED: Dict = {
    'MISSILES_AAM': {
        'AIM-54A-MK47': 12,
        'AIM-9L':        8,
        'AIM-7M':        2,  # ← fattore limitante
    },
    'MISSILES_ASM': {},
    'BOMBS':        {},
    'ROCKETS':      {},
    'CANNONS':      {},
    'MACHINE_GUNS': {},
}

# AIM-54A-MK47 insufficiente (3 < 4 necessari) → 0 loadout
_WEAPONS_AVAIL_INSUFFICIENT: Dict = {
    'MISSILES_AAM': {
        'AIM-54A-MK47': 3,   # 3 < 4 necessari → 0 loadout
        'AIM-9L':        10,
        'AIM-7M':        10,
    },
    'MISSILES_ASM': {},
    'BOMBS':        {},
    'ROCKETS':      {},
    'CANNONS':      {},
    'MACHINE_GUNS': {},
}

# Abbondante: 10 loadout disponibili per ogni arma
_WEAPONS_AVAIL_ABUNDANT: Dict = {
    'MISSILES_AAM': {
        'AIM-54A-MK47': 40,  # 40 // 4 = 10
        'AIM-9L':        20,  # 20 // 2 = 10
        'AIM-7M':        20,  # 20 // 2 = 10
    },
    'MISSILES_ASM': {},
    'BOMBS':        {},
    'ROCKETS':      {},
    'CANNONS':      {},
    'MACHINE_GUNS': {},
}

# Pyloni reali F-14A Tomcat "Phoenix Fleet Defense" (estratti da AIRCRAFT_LOADOUTS)
_F14A_PHOENIX_PYLONS: Dict = (
    AIRCRAFT_LOADOUTS["F-14A Tomcat"]["Phoenix Fleet Defense"]["stores"]["pylons"]
)

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
    {'model': 'F-16CM Block 50',          'loadout': 'SEAD/DEAD',                  'quantity': 12},
    {'model': 'Su-24M',                   'loadout': 'SEAD',                       'quantity': 12},
    {'model': 'F/A-18C Lot 20',           'loadout': 'SEAD',                       'quantity': 12},
    {'model': 'Su-25TM',                  'loadout': 'SEAD/Anti-Radar',            'quantity': 8},
]
_TARGET_SEAD_SCENARIO: Dict = {
    'Air_Defense': {
        'big':   {'quantity': 3,  'priority': 5},
        'med':   {'quantity': 5,  'priority': 6},
        'small': {'quantity': 10, 'priority': 6},
    }   
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


def _mra_logger_mocked() -> ExitStack:
    """Context manager: mocka solo il logger di Air_Resources_Assigner."""
    stack = ExitStack()
    stack.enter_context(patch(_LOGGER_MRA, MagicMock()))
    return stack


# ─────────────────────────────────────────────────────────────────────────────
#  1. _find_weapon_in_availability
# ─────────────────────────────────────────────────────────────────────────────

class TestFindWeaponInAvailability(unittest.TestCase):
    """Unit test per _find_weapon_in_availability(weapons_availability, weapon_name).

    Ricerca un'arma nella struttura annidata::

        {weapon_type: {weapon_name: quantity}, ...}

    Restituisce ``(type_key, quantity)`` se trovata, ``(None, 0)`` altrimenti.

    Fixture: basata su _WEAPONS_AVAILABILITY['air_weapons'] (Initial_Context.py)
    con overrides locali per garantire valori deterministi nei test.
    """

    def setUp(self):
        # Costruisce una weapons_availability realistica a partire dai dati reali,
        # sovrascrivendo le quantità per renderle deterministiche nei test.
        base = copy.deepcopy(_WEAPONS_AVAILABILITY['air_weapons'])
        base['MISSILES_AAM']['AIM-54A-MK47'] = 50
        base['BOMBS']['Mk-84'] = 30
        self._wa = base

    # ── Weapon trovata ────────────────────────────────────────────────────────

    def test_aim54_found_in_missiles_aam(self):
        """AIM-54A-MK47 → trovato nel bucket MISSILES_AAM."""
        wtype, qty = _find_weapon_in_availability(self._wa, 'AIM-54A-MK47')
        self.assertEqual(wtype, 'MISSILES_AAM')

    def test_mk84_found_in_bombs(self):
        """Mk-84 → trovato nel bucket BOMBS."""
        wtype, _ = _find_weapon_in_availability(self._wa, 'Mk-84')
        self.assertEqual(wtype, 'BOMBS')

    def test_returns_correct_quantity(self):
        """La quantità restituita corrisponde al valore presente nel dizionario."""
        _, qty = _find_weapon_in_availability(self._wa, 'AIM-54A-MK47')
        self.assertEqual(qty, 50)

    def test_mk84_correct_quantity(self):
        """La quantità per Mk-84 corrisponde al valore impostato."""
        _, qty = _find_weapon_in_availability(self._wa, 'Mk-84')
        self.assertEqual(qty, 30)

    def test_returns_tuple(self):
        """Il risultato è sempre una tupla di due elementi."""
        result = _find_weapon_in_availability(self._wa, 'AIM-54A-MK47')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    # ── Weapon non trovata ────────────────────────────────────────────────────

    def test_unknown_weapon_returns_none_zero(self):
        """Weapon inesistente → (None, 0)."""
        wtype, qty = _find_weapon_in_availability(self._wa, 'UNKNOWN_WEAPON_XYZ')
        self.assertIsNone(wtype)
        self.assertEqual(qty, 0)

    def test_empty_availability_returns_none_zero(self):
        """Dizionario vuoto → (None, 0)."""
        wtype, qty = _find_weapon_in_availability({}, 'AIM-54A-MK47')
        self.assertIsNone(wtype)
        self.assertEqual(qty, 0)

    def test_weapon_in_last_bucket_found(self):
        """Weapon in un bucket successivo al primo → trovata correttamente."""
        # AIM-7M è in MISSILES_AAM; verifichiamo che non importi la posizione
        wtype, _ = _find_weapon_in_availability(self._wa, 'AIM-7M')
        self.assertEqual(wtype, 'MISSILES_AAM')

    def test_rockets_bucket(self):
        """Weapon nel bucket ROCKETS → trovata con il tipo corretto."""
        base = copy.deepcopy(_WEAPONS_AVAILABILITY['air_weapons'])
        base['ROCKETS']['Zuni-Mk71'] = 15
        wtype, qty = _find_weapon_in_availability(base, 'Zuni-Mk71')
        self.assertEqual(wtype, 'ROCKETS')
        self.assertEqual(qty, 15)


# ─────────────────────────────────────────────────────────────────────────────
#  2. _pylons_to_weapons_dict
# ─────────────────────────────────────────────────────────────────────────────

class TestPylonsToWeaponsDict(unittest.TestCase):
    """Unit test per _pylons_to_weapons_dict(pylons).

    Converte::

        {pylon_id: [weapon_name, quantity, ...], ...}

    in::

        {weapon_name: total_quantity}

    somma le quantità per armi sullo stesso tipo montate su più piloni.

    Fixture: pyloni reali di F-14A Tomcat "Phoenix Fleet Defense"
    (4x AIM-54A-MK47, 2x AIM-9L, 2x AIM-7M).
    """

    # ── Casi nominali ────────────────────────────────────────────────────────

    def test_f14a_phoenix_aggregates_correctly(self):
        """Pyloni F-14A Phoenix Fleet Defense → 4 AIM-54A-MK47, 2 AIM-9L, 2 AIM-7M."""
        result = _pylons_to_weapons_dict(_F14A_PHOENIX_PYLONS)
        self.assertEqual(result.get('AIM-54A-MK47'), 4)
        self.assertEqual(result.get('AIM-9L'),        2)
        self.assertEqual(result.get('AIM-7M'),         2)

    def test_same_weapon_multiple_pylons_summed(self):
        """Stessa arma su più piloni → quantità sommate."""
        pylons = {
            1: ['AIM-9L', 1],
            2: ['AIM-9L', 1],
            3: ['AIM-9L', 1],
        }
        result = _pylons_to_weapons_dict(pylons)
        self.assertEqual(result['AIM-9L'], 3)

    def test_single_pylon(self):
        """Un solo pilone → un'arma con la quantità corretta."""
        pylons = {1: ['AIM-54A-MK47', 2]}
        result = _pylons_to_weapons_dict(pylons)
        self.assertEqual(result.get('AIM-54A-MK47'), 2)

    def test_empty_pylons_returns_empty_dict(self):
        """Pyloni vuoti → dizionario vuoto."""
        self.assertEqual(_pylons_to_weapons_dict({}), {})

    def test_returns_dict(self):
        """Il risultato è sempre un dict."""
        self.assertIsInstance(_pylons_to_weapons_dict(_F14A_PHOENIX_PYLONS), dict)

    def test_different_weapons_no_cross_contamination(self):
        """Armi diverse su piloni distinti → non si sommano tra loro."""
        pylons = {1: ['AIM-9L', 1], 2: ['AIM-7M', 1]}
        result = _pylons_to_weapons_dict(pylons)
        self.assertEqual(result['AIM-9L'], 1)
        self.assertEqual(result['AIM-7M'], 1)

    def test_pylon_with_extra_fields_accepted(self):
        """Pilone con campo extra (es. peso) → accettato senza errore."""
        pylons = {1: ['AIM-54A-MK47', 4, 450]}  # terzo campo = peso
        result = _pylons_to_weapons_dict(pylons)
        self.assertEqual(result.get('AIM-54A-MK47'), 4)

    # ── Dati non validi ───────────────────────────────────────────────────────

    def test_invalid_pylon_entry_skipped(self):
        """Voce di pilone malformata (non lista/tupla) → saltata, nessuna eccezione."""
        pylons = {1: ['AIM-9L', 1], 2: 'invalid_entry'}
        result = _pylons_to_weapons_dict(pylons)
        self.assertIn('AIM-9L', result)
        self.assertNotIn('invalid_entry', result)

    def test_pylon_too_short_skipped(self):
        """Lista pilone con meno di 2 elementi → saltata."""
        pylons = {1: ['AIM-9L'], 2: ['AIM-7M', 1]}
        result = _pylons_to_weapons_dict(pylons)
        self.assertNotIn('AIM-9L', result)
        self.assertEqual(result.get('AIM-7M'), 1)

    def test_non_dict_input_raises_type_error(self):
        """Input non dict → TypeError."""
        with self.assertRaises(TypeError):
            _pylons_to_weapons_dict([['AIM-9L', 1]])


# ─────────────────────────────────────────────────────────────────────────────
#  3. _loadout_availability
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadoutAvailability(unittest.TestCase):
    """Unit test per _loadout_availability(weapons_availability, aircraft_model, loadout_name).

    Calcola quanti loadout completi si possono allestire con le armi disponibili.
    Il fattore limitante è l'arma con il rapporto ``disponibile // richiesta`` minore.

    Aereo di riferimento: F-14A Tomcat / "Phoenix Fleet Defense"
      (4x AIM-54A-MK47, 2x AIM-9L, 2x AIM-7M per loadout)

    Tabella attesa con _WEAPONS_AVAIL_NOMINAL (8/4/4):
      AIM-54A-MK47: 8 // 4 = 2
      AIM-9L:        4 // 2 = 2
      AIM-7M:        4 // 2 = 2
      → loadout disponibili = 2
    """

    _AIRCRAFT = 'F-14A Tomcat'
    _LOADOUT  = 'Phoenix Fleet Defense'

    def setUp(self):
        self._mock_ctx = _mra_logger_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    # ── Casi nominali ────────────────────────────────────────────────────────

    def test_nominal_returns_two_loadouts(self):
        """_WEAPONS_AVAIL_NOMINAL (8/4/4) → 2 loadout disponibili."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(result, 2)

    def test_aim7_is_limiting_factor(self):
        """Con AIM-7M=2 (fattore limitante) → 1 loadout disponibile."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_AIM7_LIMITED)
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(result, 1)

    def test_abundant_returns_ten_loadouts(self):
        """_WEAPONS_AVAIL_ABUNDANT (40/20/20) → 10 loadout disponibili."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_ABUNDANT)
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(result, 10)

    def test_returns_int(self):
        """Il risultato è sempre un intero."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertIsInstance(result, int)

    def test_returns_non_negative(self):
        """Il risultato è sempre >= 0."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertGreaterEqual(result, 0)

    def test_does_not_mutate_availability(self):
        """La funzione non modifica weapons_availability (sola lettura)."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        before = copy.deepcopy(wa)
        _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(wa, before)

    # ── Insufficienza / assenza ───────────────────────────────────────────────

    def test_insufficient_aim54_returns_zero(self):
        """AIM-54A-MK47=3 (< 4 necessari) → 0 loadout."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_INSUFFICIENT)
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(result, 0)

    def test_weapon_missing_from_availability_returns_zero(self):
        """Arma non presente nel dizionario → 0 loadout."""
        wa = {'MISSILES_AAM': {'AIM-9L': 10, 'AIM-7M': 10}}  # AIM-54A-MK47 assente
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(result, 0)

    def test_zero_quantity_weapon_returns_zero(self):
        """Arma con quantità 0 → 0 loadout."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wa['MISSILES_AAM']['AIM-54A-MK47'] = 0
        result = _loadout_availability(wa, self._AIRCRAFT, self._LOADOUT)
        self.assertEqual(result, 0)

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_invalid_weapons_availability_raises_type_error(self):
        """weapons_availability non dict → TypeError."""
        with self.assertRaises(TypeError):
            _loadout_availability("not_a_dict", self._AIRCRAFT, self._LOADOUT)

    def test_empty_aircraft_model_raises_type_error(self):
        """aircraft_model stringa vuota → TypeError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(TypeError):
            _loadout_availability(wa, '', self._LOADOUT)

    def test_empty_loadout_name_raises_type_error(self):
        """loadout_name stringa vuota → TypeError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(TypeError):
            _loadout_availability(wa, self._AIRCRAFT, '')

    def test_non_string_aircraft_model_raises_type_error(self):
        """aircraft_model non stringa → TypeError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(TypeError):
            _loadout_availability(wa, 42, self._LOADOUT)


# ─────────────────────────────────────────────────────────────────────────────
#  4. _reduction_weapons_availability
# ─────────────────────────────────────────────────────────────────────────────

class TestReductionWeaponsAvailability(unittest.TestCase):
    """Unit test per _reduction_weapons_availability(weapons_availability, weapons_list).

    Sottrae le quantità in *weapons_list* da *weapons_availability* in-place.

    Comportamento chiave:
      - Validazione atomica: verifica PRIMA tutte le armi, poi applica le riduzioni.
        Se anche solo un'arma è insufficiente, nessuna modifica viene applicata.
      - Arma non trovata: warning + skip (non blocca l'operazione).
      - Ritorna True se tutte le operazioni sono riuscite, False se una quantità
        è insufficiente.

    Struttura weapons_availability: {weapon_type: {weapon_name: quantity}}
    Struttura weapons_list:         {weapon_name: quantity}
    """

    def setUp(self):
        self._mock_ctx = _mra_logger_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    # ── Casi nominali ────────────────────────────────────────────────────────

    def test_normal_reduction_returns_true(self):
        """Riduzione normale con scorte sufficienti → True."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wl = {'AIM-54A-MK47': 4, 'AIM-9L': 2, 'AIM-7M': 2}
        result = _reduction_weapons_availability(wa, wl)
        self.assertTrue(result)

    def test_quantities_correctly_reduced(self):
        """Le quantità vengono ridotte dei valori corretti."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        # Iniziale: AIM-54A-MK47=8, AIM-9L=4, AIM-7M=4
        wl = {'AIM-54A-MK47': 4, 'AIM-9L': 2, 'AIM-7M': 2}
        _reduction_weapons_availability(wa, wl)
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], 4)  # 8 - 4
        self.assertEqual(wa['MISSILES_AAM']['AIM-9L'],        2)  # 4 - 2
        self.assertEqual(wa['MISSILES_AAM']['AIM-7M'],         2)  # 4 - 2

    def test_full_depletion_to_zero(self):
        """Riduzione dell'intera scorta → quantità = 0."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wl = {'AIM-54A-MK47': 8, 'AIM-9L': 4, 'AIM-7M': 4}
        result = _reduction_weapons_availability(wa, wl)
        self.assertTrue(result)
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], 0)

    def test_empty_weapons_list_returns_true(self):
        """Lista armi vuota → True (niente da ridurre)."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        before = copy.deepcopy(wa)
        result = _reduction_weapons_availability(wa, {})
        self.assertTrue(result)
        self.assertEqual(wa, before)

    # ── Insufficienza scorte ──────────────────────────────────────────────────

    def test_insufficient_quantity_returns_false(self):
        """Richiesta superiore alla scorta → False."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wl = {'AIM-54A-MK47': 100}  # 100 > 8 disponibili
        result = _reduction_weapons_availability(wa, wl)
        self.assertFalse(result)

    def test_atomicity_no_partial_update_on_failure(self):
        """Atomicità: se una riduzione fallisce, NESSUNA modifica viene applicata.

        Scenario: riduco AIM-54A-MK47=4 (ok) e AIM-9L=100 (fail).
        Il AIM-54A-MK47 NON deve essere diminuito.
        """
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        # AIM-9L=4 disponibili, richiediamo 100 → fallisce
        wl = {'AIM-54A-MK47': 4, 'AIM-9L': 100}
        result = _reduction_weapons_availability(wa, wl)
        self.assertFalse(result)
        # Verifica: AIM-54A-MK47 NON è stato toccato
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], 8)
        # Verifica: AIM-9L NON è stato toccato
        self.assertEqual(wa['MISSILES_AAM']['AIM-9L'], 4)

    # ── Weapon non trovata ────────────────────────────────────────────────────

    def test_unknown_weapon_skipped_others_reduced(self):
        """Weapon sconosciuta → saltata con warning; le altre vengono ridotte."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wl = {'UNKNOWN_WEAPON_XYZ': 5, 'AIM-9L': 2}
        result = _reduction_weapons_availability(wa, wl)
        self.assertTrue(result)
        self.assertEqual(wa['MISSILES_AAM']['AIM-9L'], 2)  # 4 - 2

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_weapons_availability_not_dict_raises_type_error(self):
        """weapons_availability non dict → TypeError."""
        with self.assertRaises(TypeError):
            _reduction_weapons_availability("not_a_dict", {'AIM-9L': 1})

    def test_weapons_list_not_dict_raises_type_error(self):
        """weapons_list non dict → TypeError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(TypeError):
            _reduction_weapons_availability(wa, [('AIM-9L', 1)])

    def test_negative_quantity_raises_value_error(self):
        """Quantità negativa in weapons_list → ValueError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(ValueError):
            _reduction_weapons_availability(wa, {'AIM-9L': -1})


# ─────────────────────────────────────────────────────────────────────────────
#  5. _increase_weapons_availability
# ─────────────────────────────────────────────────────────────────────────────

class TestIncreaseWeaponsAvailability(unittest.TestCase):
    """Unit test per _increase_weapons_availability(weapons_availability, weapons_list).

    Aggiunge le quantità in *weapons_list* a *weapons_availability* in-place.

    Comportamento:
      - Sempre True (l'incremento non può fallire per carenza di scorte).
      - Arma non trovata: warning + skip.
      - Quantità negative → ValueError.

    Struttura weapons_availability: {weapon_type: {weapon_name: quantity}}
    Struttura weapons_list:         {weapon_name: quantity}
    """

    def setUp(self):
        self._mock_ctx = _mra_logger_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    # ── Casi nominali ────────────────────────────────────────────────────────

    def test_normal_increase_returns_true(self):
        """Incremento normale → True."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wl = {'AIM-54A-MK47': 4, 'AIM-9L': 2}
        result = _increase_weapons_availability(wa, wl)
        self.assertTrue(result)

    def test_quantities_correctly_increased(self):
        """Le quantità vengono incrementate dei valori corretti."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        # Iniziale: AIM-54A-MK47=8, AIM-9L=4
        wl = {'AIM-54A-MK47': 4, 'AIM-9L': 2}
        _increase_weapons_availability(wa, wl)
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], 12)  # 8 + 4
        self.assertEqual(wa['MISSILES_AAM']['AIM-9L'],         6)  # 4 + 2

    def test_zero_increase_no_change(self):
        """Incremento di 0 → quantità invariata."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        before_aim54 = wa['MISSILES_AAM']['AIM-54A-MK47']
        _increase_weapons_availability(wa, {'AIM-54A-MK47': 0})
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], before_aim54)

    def test_empty_weapons_list_returns_true(self):
        """Lista armi vuota → True (niente da aggiungere)."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        before = copy.deepcopy(wa)
        result = _increase_weapons_availability(wa, {})
        self.assertTrue(result)
        self.assertEqual(wa, before)

    def test_reduction_then_increase_roundtrip(self):
        """Riduzione + incremento identico → disponibilità invariata (roundtrip)."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        before = copy.deepcopy(wa)
        wl = {'AIM-54A-MK47': 4, 'AIM-9L': 2, 'AIM-7M': 2}
        _reduction_weapons_availability(wa, wl)
        _increase_weapons_availability(wa, wl)
        self.assertEqual(wa, before)

    # ── Weapon non trovata ────────────────────────────────────────────────────

    def test_unknown_weapon_returns_true(self):
        """Weapon sconosciuta → True (skip con warning)."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        result = _increase_weapons_availability(wa, {'UNKNOWN_WEAPON_XYZ': 5})
        self.assertTrue(result)

    def test_unknown_weapon_does_not_alter_others(self):
        """Weapon sconosciuta saltata → le altre armi vengono comunque incrementate."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        wl = {'UNKNOWN_WEAPON_XYZ': 5, 'AIM-9L': 3}
        _increase_weapons_availability(wa, wl)
        self.assertEqual(wa['MISSILES_AAM']['AIM-9L'], 7)  # 4 + 3

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_weapons_availability_not_dict_raises_type_error(self):
        """weapons_availability non dict → TypeError."""
        with self.assertRaises(TypeError):
            _increase_weapons_availability(None, {'AIM-9L': 1})

    def test_weapons_list_not_dict_raises_type_error(self):
        """weapons_list non dict → TypeError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(TypeError):
            _increase_weapons_availability(wa, [('AIM-9L', 1)])

    def test_negative_quantity_raises_value_error(self):
        """Quantità negativa → ValueError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(ValueError):
            _increase_weapons_availability(wa, {'AIM-9L': -1})


# ─────────────────────────────────────────────────────────────────────────────
#  6. get_loadouts_availability
# ─────────────────────────────────────────────────────────────────────────────

class TestGetLoadoutsAvailability(unittest.TestCase):
    """Unit test per get_loadouts_availability(weapons_availability, loadouts_list).

    Verifica e assegna i loadout in base alla disponibilità corrente delle armi.
    Deduce atomicamente le armi consumate da *weapons_availability*.

    Formato input::

        loadouts_list = {aircraft_model: {loadout_name: requested_quantity}}

    Formato output::

        {aircraft_model: {loadout_name: {'quantity': int, 'reduction_percentage': int}}}

    Aereo di riferimento: F-14A Tomcat / "Phoenix Fleet Defense"
      (4x AIM-54A-MK47, 2x AIM-9L, 2x AIM-7M per loadout)

    Tabella di riferimento con _WEAPONS_AVAIL_NOMINAL (8/4/4):
      max 2 loadout disponibili.
      - richiesta 2 → assegnati 2, reduction_percentage=100
      - richiesta 3 → assegnati 2, reduction_percentage=66
      - richiesta 1 con _INSUFFICIENT → assegnati 0, reduction_percentage=0
    """

    _AIRCRAFT = 'F-14A Tomcat'
    _LOADOUT  = 'Phoenix Fleet Defense'

    def setUp(self):
        self._mock_ctx = _mra_logger_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    # ── Struttura del risultato ───────────────────────────────────────────────

    def test_returns_dict(self):
        """Input valido → restituisce un dict."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        result = get_loadouts_availability(wa, loadouts)
        self.assertIsInstance(result, dict)

    def test_result_contains_aircraft_model_key(self):
        """Il risultato contiene la chiave del modello aereo."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        result = get_loadouts_availability(wa, loadouts)
        self.assertIn(self._AIRCRAFT, result)

    def test_result_contains_loadout_name_key(self):
        """Il risultato contiene la chiave del nome loadout."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        result = get_loadouts_availability(wa, loadouts)
        self.assertIn(self._LOADOUT, result[self._AIRCRAFT])

    def test_entry_has_quantity_and_reduction_percentage(self):
        """Ogni entry ha 'quantity' e 'reduction_percentage'."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertIn('quantity', entry)
        self.assertIn('reduction_percentage', entry)

    # ── Assegnazione piena ────────────────────────────────────────────────────

    def test_full_assignment_quantity_and_percentage(self):
        """Richiesta soddisfatta per intero → quantity=richiesta, reduction_percentage=100."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}  # max disponibile = 2
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertEqual(entry['quantity'], 2)
        self.assertEqual(entry['reduction_percentage'], 100)

    def test_single_loadout_assigned(self):
        """Richiesta di 1 loadout con scorte nominali → assegnato 1 (100%)."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 1}}
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertEqual(entry['quantity'], 1)
        self.assertEqual(entry['reduction_percentage'], 100)

    # ── Assegnazione parziale ─────────────────────────────────────────────────

    def test_partial_assignment_quantity_reduced(self):
        """Richiesta 3, disponibili 2 → quantity=2."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 3}}
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertEqual(entry['quantity'], 2)

    def test_partial_assignment_correct_percentage(self):
        """Richiesta 3, assegnati 2 → reduction_percentage = int(2/3*100) = 66."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 3}}
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertEqual(entry['reduction_percentage'], 66)  # int(2*100/3)

    # ── Nessuna disponibilità ─────────────────────────────────────────────────

    def test_no_availability_quantity_zero(self):
        """Armi insufficienti → quantity=0."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_INSUFFICIENT)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertEqual(entry['quantity'], 0)

    def test_no_availability_percentage_zero(self):
        """Armi insufficienti → reduction_percentage=0."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_INSUFFICIENT)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        result = get_loadouts_availability(wa, loadouts)
        entry = result[self._AIRCRAFT][self._LOADOUT]
        self.assertEqual(entry['reduction_percentage'], 0)

    # ── Deduzione armi ────────────────────────────────────────────────────────

    def test_weapons_deducted_from_availability(self):
        """Dopo l'assegnazione, weapons_availability è ridotta delle armi usate.

        2 loadout "Phoenix Fleet Defense" consumano: 8 AIM-54A-MK47, 4 AIM-9L, 4 AIM-7M.
        Partendo da NOMINAL (8/4/4) → tutti a 0.
        """
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        get_loadouts_availability(wa, loadouts)
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], 0)
        self.assertEqual(wa['MISSILES_AAM']['AIM-9L'],        0)
        self.assertEqual(wa['MISSILES_AAM']['AIM-7M'],         0)

    def test_no_deduction_when_zero_assigned(self):
        """Se quantity=0 (armi insufficienti), la disponibilità non cambia."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_INSUFFICIENT)
        before = copy.deepcopy(wa)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        get_loadouts_availability(wa, loadouts)
        self.assertEqual(wa, before)

    def test_sequential_loadouts_reduce_stock_progressively(self):
        """Più loadout per lo stesso aereo scalano le scorte progressivamente.

        2 loadout "Phoenix Fleet Defense" consumano 8 AIM-54A-MK47 totali.
        Partendo da ABUNDANT (40 AIM-54A-MK47) → rimangono 40 - 2*4 = 32.
        """
        wa = copy.deepcopy(_WEAPONS_AVAIL_ABUNDANT)
        loadouts = {self._AIRCRAFT: {self._LOADOUT: 2}}
        get_loadouts_availability(wa, loadouts)
        self.assertEqual(wa['MISSILES_AAM']['AIM-54A-MK47'], 32)  # 40 - 2*4

    # ── Più modelli e loadout ─────────────────────────────────────────────────

    def test_multiple_aircraft_models_in_result(self):
        """Più modelli di aereo nella richiesta → tutti presenti nel risultato."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_ABUNDANT)
        loadouts = {
            'F-14A Tomcat': {'Phoenix Fleet Defense': 1},
            'F-14B Tomcat': {'Phoenix Fleet Defense': 1},
        }
        result = get_loadouts_availability(wa, loadouts)
        self.assertIn('F-14A Tomcat', result)
        self.assertIn('F-14B Tomcat', result)

    def test_multiple_loadouts_same_aircraft_in_result(self):
        """Più loadout dello stesso aereo → tutti presenti nel risultato."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_ABUNDANT)
        loadouts = {
            'F-14A Tomcat': {
                'Phoenix Fleet Defense': 1,
                'Sparrow CAP/Escort':    1,
            }
        }
        result = get_loadouts_availability(wa, loadouts)
        self.assertIn('Phoenix Fleet Defense', result['F-14A Tomcat'])
        self.assertIn('Sparrow CAP/Escort',    result['F-14A Tomcat'])

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_weapons_availability_not_dict_raises_type_error(self):
        """weapons_availability non dict → TypeError."""
        with self.assertRaises(TypeError):
            get_loadouts_availability("not_a_dict", {self._AIRCRAFT: {self._LOADOUT: 1}})

    def test_loadouts_list_not_dict_raises_type_error(self):
        """loadouts_list non dict → TypeError."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        with self.assertRaises(TypeError):
            get_loadouts_availability(wa, [(self._AIRCRAFT, {self._LOADOUT: 1})])

    def test_invalid_loadout_format_skipped(self):
        """loadouts per un aereo con formato non dict → saltato, result non contiene l'aereo."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        loadouts = {'F-14A Tomcat': 'invalid_format'}
        result = get_loadouts_availability(wa, loadouts)
        # L'aereo viene saltato, non deve comparire nel risultato
        self.assertNotIn('F-14A Tomcat', result)

    def test_empty_loadouts_list_returns_empty_dict(self):
        """loadouts_list vuota → dict vuoto."""
        wa = copy.deepcopy(_WEAPONS_AVAIL_NOMINAL)
        result = get_loadouts_availability(wa, {})
        self.assertEqual(result, {})


# ─────────────────────────────────────────────────────────────────────────────
#  7. _extract_quantities
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

    Formula (interpolazione lineare):
      multiplier = ratio + weight * (1 - ratio)   ∈ [ratio, 1.0]
      weight = priority / total_priority_weight
      quantity = max(0, round(qty * multiplier))

    Con due target di priorità diverse (2 e 8, totale=10):
      low  (prio=2): weight=0.2, multiplier = ratio + 0.2*(1-ratio)
      high (prio=8): weight=0.8, multiplier = ratio + 0.8*(1-ratio)

    Casi limite:
      ratio ≤ 0 → tutte le quantità diventano 0
      ratio ≥ 1 → nessuna riduzione (deep copy invariata)
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
        Soft/big    (prio=2): weight=0.2, multiplier = 0.5 + 0.2*0.5 = 0.6, qty = round(10 * 0.6) = 6
        Armored/big (prio=8): weight=0.8, multiplier = 0.5 + 0.8*0.5 = 0.9, qty = round(10 * 0.9) = 9
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

class _ScenarioTestBase:
    """Base class per i test di scenario parametrici.

    Le sottoclassi devono definire `_CFG` come uno degli elementi di
    `_SCENARIO_CONFIGS`.  I metodi di test iterano tutte le combinazioni
    (max_aircraft × max_missions × directive) tramite subTest.

    Non eredita direttamente da unittest.TestCase per evitare che i runner
    (pytest, -m unittest) la scoprano e la eseguano con _CFG = {} vuoto.
    Le sottoclassi concrete usano ereditarietà multipla:
        class TestFoo(_ScenarioTestBase, unittest.TestCase): ...
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
        """Ogni entry ha i campi obbligatori per tutte le combinazioni."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for entry in result['fully_compliant'] + result['derated']:
                    self.assertIn('aircraft_model',      entry)
                    self.assertIn('loadout',             entry)
                    self.assertIn('score',               entry)
                    self.assertIn('aircraft_per_mission',entry)
                    self.assertIn('missions_needed',     entry)
                    self.assertIn('derating_factor',     entry)

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

    def test_derating_factor_in_range(self):
        """derating_factor ∈ [0, 1) per tutte le combinazioni."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for entry in result['fully_compliant'] + result['derated']:
                    df = entry['derating_factor']
                    self.assertGreaterEqual(df, 0.0)
                    self.assertLess(df, 1.0)

    def test_fully_compliant_derating_is_zero(self):
        """Tutte le entry fully_compliant hanno derating_factor == 0.0."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for entry in result['fully_compliant']:
                    self.assertEqual(entry['derating_factor'], 0.0)

    def test_derated_derating_is_positive(self):
        """Tutte le entry derated hanno derating_factor > 0.0."""
        for ma, mm, directive in self._combinations():
            with self.subTest(max_aircraft=ma, max_missions=mm, directive=directive):
                result = self._run_for_params(ma, mm, directive)
                for entry in result['derated']:
                    self.assertGreater(entry['derating_factor'], 0.0)

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


class TestStrikeScenario(_ScenarioTestBase, unittest.TestCase):
    """Scenario Strike: F-4E, MiG-27K, B-52H, Su-24M — target Structure."""
    _CFG = _SCENARIO_CONFIGS[0]


class TestCASScenario(_ScenarioTestBase, unittest.TestCase):
    """Scenario CAS: F-4E, MiG-27K, A-10C II, Su-25T — target Soft+Armored."""
    _CFG = _SCENARIO_CONFIGS[1]


class TestSEADScenario(_ScenarioTestBase, unittest.TestCase):
    """Scenario SEAD: stessi loadout CAS — verifica ranking con task SEAD."""
    _CFG = _SCENARIO_CONFIGS[2]


class TestAntiShipScenario(_ScenarioTestBase, unittest.TestCase):
    """Scenario Anti_Ship: F/A-18C, Su-30, S-3B Viking, Tu-142 — target ship."""
    _CFG = _SCENARIO_CONFIGS[3]


class TestFighterSweepScenario(_ScenarioTestBase, unittest.TestCase):
    """Scenario Fighter_Sweep: F-15C, Su-27, Viggen, MiG-29S — target Aircraft."""
    _CFG = _SCENARIO_CONFIGS[4]


class TestInterceptScenario(_ScenarioTestBase, unittest.TestCase):
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


def _format_availability_str(availability: List[Dict]) -> str:
    """Ritorna una rappresentazione compatta della disponibilità aerei: 'Modello(qty)', ..."""
    return ',  '.join(f"{e['model']}({e['quantity']})" for e in availability)


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
            'model':               entry['aircraft_model'],
            'loadout':             entry['loadout'],
            'score':               entry['score'],
            'aircraft_per_mission': entry.get('aircraft_per_mission', 0),
            'missions_needed':     entry.get('missions_needed', 0),
            'derating_factor':     entry.get('derating_factor', 0.0),
            'status':              'fully_compliant',
        })
    for entry in result['derated']:
        rows.append({
            'model':               entry['aircraft_model'],
            'loadout':             entry['loadout'],
            'score':               entry['score'],
            'aircraft_per_mission': entry.get('aircraft_per_mission', 0),
            'missions_needed':     entry.get('missions_needed', 0),
            'derating_factor':     entry.get('derating_factor', 0.0),
            'status':              'derated',
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
    W = 130
    print(f"\n{'═' * W}")
    print(
        f"  Gruppo: {cfg['group']}  |  Task: {cfg['task']}"
        f"  |  max_aircraft: {max_aircraft}"
        f"  |  max_missions: {max_missions}"
        f"  |  directive: {directive}"
    )
    print(f"  Disponibili: {_format_availability_str(cfg['availability'])}")
    print(f"  Target: {_format_target_str(cfg['target_data'])}")
    print(f"{'─' * W}")
    if not rows:
        print("  (nessun risultato)")
        return
    hdr = (
        f"  {'#':>3}  {'Aeromobile':<32}  {'Loadout':<28}"
        f"  {'Score':>8}  {'Ac/Miss':>7}  {'Missioni':>8}  {'Derating':>8}  {'Status':<16}"
    )
    print(hdr)
    print(f"  {'─'*3}  {'─'*32}  {'─'*28}  {'─'*8}  {'─'*7}  {'─'*8}  {'─'*8}  {'─'*16}")
    for i, row in enumerate(rows, start=1):
        print(
            f"  {i:>3}  {row['model']:<32}  {row['loadout']:<28}"
            f"  {row['score']:>8.4f}  {row['aircraft_per_mission']:>7}  {row['missions_needed']:>8}"
            f"  {row['derating_factor']:>7.1%}  {row['status']:<16}"
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

    col_labels = ["#", "Aeromobile", "Loadout", "Score", "Ac/Miss", "Missioni", "Derating", "Status"]
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
                            cell_text.append(["—", "(nessun risultato)", "", "", "", "", "", ""])
                            cell_colors.append(["#f5f5f5"] * n_cols)
                        else:
                            for i, row in enumerate(rows, start=1):
                                score_str    = f"{row['score']:.4f}"
                                derating_str = f"{row['derating_factor']:.1%}"
                                cell_text.append([
                                    str(i),
                                    row['model'],
                                    row['loadout'],
                                    score_str,
                                    str(row['aircraft_per_mission']),
                                    str(row['missions_needed']),
                                    derating_str,
                                    row['status'],
                                ])
                                norm = (row['score'] - min_s) / rng
                                score_color   = plt.cm.RdYlGn(norm)
                                # Derating: verde=0% (nessun taglio), rosso=100% (taglio totale)
                                derating_color = plt.cm.RdYlGn(1.0 - row['derating_factor'])
                                status_bg      = "#d4edda" if row['status'] == 'fully_compliant' else "#fff3cd"
                                cell_colors.append([
                                    "#f5f5f5", "#f0f4f8", "#f0f4f8",
                                    score_color, "#f0f4f8", "#f0f4f8", derating_color, status_bg,
                                ])

                        n_rows = len(cell_text)
                        fig_w  = max(20.0, 2.2 * n_cols)
                        fig_h  = max(4.0, 0.40 * n_rows + 3.5)

                        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                        ax.axis("off")
                        target_str = _format_target_str(cfg['target_data'])
                        avail_str  = _format_availability_str(cfg['availability'])
                        ax.set_title(
                            f"Gruppo: {cfg['group']}  |  Task: {cfg['task']}"
                            f"  |  max_aircraft: {ma}"
                            f"  |  max_missions: {mm}"
                            f"  |  directive: {directive}\n"
                            f"Disponibili: {avail_str}\n"
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
        # ── Helpers weapons/loadout (nuovi) ───────────────────────────────
        TestFindWeaponInAvailability,
        TestPylonsToWeaponsDict,
        TestLoadoutAvailability,
        TestReductionWeaponsAvailability,
        TestIncreaseWeaponsAvailability,
        TestGetLoadoutsAvailability,
        # ── Helpers target/mission (esistenti) ───────────────────────────
        TestExtractQuantities,
        TestExtractTargetLists,
        TestCheckMissionRequirements,
        TestUsabilityMet,
        TestComputeScore,
        TestReduceTargetData,
        TestGetAircraftMission,
        TestGetAircraftMissionAircraft,
        # ── Scenari parametrici (esistenti) ──────────────────────────────
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
    print("║   Test_Air_Resources_Assigner  —  Menu principale      ║")
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
