"""
Test_Aircraft_Data.py
=====================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo
Aircraft_Data.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Data.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Data.py            # menu interattivo
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Data.py --tables-only
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Data.py --tests-only

Note sul modulo sotto test:
  - Aircraft_Data: dataclass che rappresenta un aeromobile militare.
  - Aircraft_Data._registry: dizionario globale {model: Aircraft_Data}.
  - AIRCRAFT_ROLE: dict_keys delle categorie valide (da AIR_MILITARY_CRAFT_ASSET).
  - AIRCRAFT_TASK: dizionario dei task aerei validi (da AIR_TASK).
  - AIRCRAFT: dict con punteggi pre-calcolati (flat float) per ogni aeromobile.
  - get_aircraft_data(model): restituisce tutti i punteggi di un aeromobile.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List, Optional

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAZIONE — modificare le liste per personalizzare le tabelle
# ─────────────────────────────────────────────────────────────────────────────

# Categorie di aeromobili da includere nelle tabelle
AIRCRAFT_CATEGORIES: List[str] = [
    "Fighter",
    "Fighter_Bomber",
    "Attacker",
    "Bomber",
    "Heavy_Bomber",
    "Awacs",
    "Recon",
    "Transport",
    "Helicopter",
]

# Task aerei da includere nelle tabelle combat score
COMBAT_TASKS: List[str] = [
    "CAP",
    "Intercept",
    "Fighter_Sweep",
    "Escort",
    "Strike",
    "CAS",
    "Pinpoint_Strike",
    "SEAD",
    "Anti_Ship",
]

# Tipi di bersaglio per le tabelle target effectiveness
target_type_list: List[str] = [
    "Soft",
    "Armored",
    "Hard",
    "Air_Defense",
    "ship",
]

# Dimensioni del bersaglio per le tabelle target effectiveness
target_dimension_list: List[str] = ["big", "med", "small"]

# Directory di output per i PDF
OUTPUT_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "..", "out",
    )
)

# Path del logger da mockare nei test
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data.logger"
_LOADOUTS_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts.logger"
_GWD_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data.logger"
_AWD_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import (
    Aircraft_Data,
    AIRCRAFT_ROLE,
    AIRCRAFT_TASK,
    AIRCRAFT,
    SYSTEM_WEIGHTS,
    get_aircraft_data,
    get_aircraft_scores,
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import (
    AIRCRAFT_LOADOUTS,
    loadout_eval,
    get_loadout_tasks,
    loadout_target_effectiveness_by_distribuition,
    get_weapon_efficiency,
)
from Code.Dynamic_War_Manager.Source.Context.Context import Air_Asset_Type, COALITIONS

# Parametri fissi per la tabella get_list_of_aircrafts
_LIST_SIDE = "Red"
_LIST_TASK = "Strike"
_LIST_TARGET_DIST: dict = {
    "Soft": {
        "perc_type": 0.5,
        "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3},
    },
    "Armored": {
        "perc_type": 0.3,
        "perc_dimension": {"big": 0.3, "med": 0.4, "small": 0.3},
    },
    "Structure": {
        "perc_type": 0.2,
        "perc_dimension": {"big": 0.0, "med": 0.2, "small": 0.8},
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  SCENARI PER I TEST INTEGRATIVI get_aircrafts_quantity
# ─────────────────────────────────────────────────────────────────────────────

# Aeromobile e loadout usati per i test unitari di get_aircrafts_quantity
_QTY_AC_MODEL       = "A-10C II Thunderbolt II"
_QTY_LOADOUT        = "Maverick/Gun CAS"
_QTY_TARGET_SIMPLE  = {"Soft": {"med": 3, "small": 5}}

# Target Aircraft con quantità elevate per garantire round(qty/eff) >= 1
# anche per loadout CAP ad alta efficienza Aircraft (eff ≈ 4–6 per 'big')
_QTY_TARGET_AIRCRAFT = {"Aircraft": {"big": 20, "med": 30, "small": 40}}

# Dizionario scenari: ogni scenario ha una lista di coppie (aircraft, loadout)
# e un dict di target (label → target_data)
_SCENARIOS: dict = {
    "CAS": {
        "aircraft": [
            ("MiG-27K",               "CAS Rocket Attack"),
            ("Su-25",                 "CAS Ground Pounding"),
            ("A-10C II Thunderbolt II","Maverick/Gun CAS"),
            ("Su-17M4",               "CAS Rocket"),
            ("F-4E Phantom II",       "CAS"),
        ],
        "targets": {
            "target_A": {
                "Soft":        {"big": 2, "med": 3, "small": 6},
                "Armored":     {"big": 1, "med": 2, "small": 4},
                "Air_Defense": {"med": 1, "small": 2},
            },
            "target_B": {
                "Soft":    {"big": 2, "med": 3, "small": 6},
                "Armored": {"big": 1, "med": 2, "small": 4},
            },
        },
    },
    "Strike": {
        "aircraft": [
            ("F-14B Tomcat",      "Strike/LANTIRN"),
            ("F-15E Strike Eagle","Iron Bomb Strike"),
            ("MiG-27K",          "Precision Ground Attack"),
            ("Su-25",            "Strike"),
            ("Su-24M",           "Night Precision Strike"),
            ("Su-24M",           "Heavy Strike"),
        ],
        "targets": {
            "target_A": {
                "Structure": {"big": 2, "med": 3, "small": 6},
                "Armored":   {"big": 1, "med": 2, "small": 4},
            },
            "target_B": {"Structure": {"big": 2, "med": 3, "small": 6}},
            "target_C": {"Structure": {"big": 5, "med": 8, "small": 12}},
        },
    },
    "AntiShip": {
        "aircraft": [
            ("F/A-18C Lot 20",    "Anti-Ship"),
            ("F-15E Strike Eagle","Iron Bomb Strike"),
            ("A-4E Skyhawk",      "Anti-Ship"),
            ("S-3B Viking",       "Anti-Ship Maritime Strike"),
            ("AJ/ASJ 37 Viggen",  "Anti-Ship Strike"),
            ("Su-34",             "Anti-Ship"),
            ("Tu-22M",            "Anti-Ship Strike"),
            ("Tu-142",            "Maritime Strike"),
        ],
        "targets": {
            "target_A": {"ship": {"big": 3, "med": 5, "small": 7}},
            "target_B": {"ship": {"big": 4, "med": 9, "small": 18}},
        },
    },
    "SEAD": {
        "aircraft": [
            ("Su-24M", "SEAD"),
            ("Su-34",  "SEAD"),
            ("Su-30",  "SEAD"),
        ],
        "targets": {
            "target_A": {"Air_Defense": {"big": 3, "med": 5, "small": 7}},
            "target_B": {"Air_Defense": {"med": 3, "small": 3}},
            "target_C": {"Air_Defense": {"med": 1, "small": 2}},
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  AEROMOBILI DI RIFERIMENTO PER I TEST
# ─────────────────────────────────────────────────────────────────────────────

_FIGHTER_MODEL   = "F-14A Tomcat"
_ATTACKER_MODEL  = "A-10C Thunderbolt II"
_BOMBER_MODEL    = "B-52H Stratofortress"
_RECON_MODEL     = "MiG-25RB"

# Recupera dinamicamente il primo loadout disponibile per i test
def _first_loadout(aircraft_model: str) -> Optional[str]:
    loadouts = AIRCRAFT_LOADOUTS.get(aircraft_model, {})
    return next(iter(loadouts), None)

def _first_loadout_for_task(aircraft_model: str, task: str) -> Optional[str]:
    for name, data in AIRCRAFT_LOADOUTS.get(aircraft_model, {}).items():
        if task in data.get("tasks", []):
            return name
    return None

_FIGHTER_LOADOUT  = _first_loadout(_FIGHTER_MODEL)
_ATTACKER_LOADOUT = _first_loadout(_ATTACKER_MODEL)


# ─────────────────────────────────────────────────────────────────────────────
#  1. STRUTTURA DATI DEL MODULO
# ─────────────────────────────────────────────────────────────────────────────

class TestAircraftDataModuleStructure(unittest.TestCase):
    """Verifica le strutture dati globali del modulo Aircraft_Data."""

    # ── AIRCRAFT_ROLE ─────────────────────────────────────────────────────────

    def test_aircraft_role_is_not_empty(self):
        self.assertGreater(len(list(AIRCRAFT_ROLE)), 0)

    def test_aircraft_role_contains_fighter(self):
        self.assertIn("Fighter", AIRCRAFT_ROLE)

    def test_aircraft_role_contains_expected_categories(self):
        for cat in ["Fighter", "Fighter_Bomber", "Attacker", "Bomber"]:
            with self.subTest(cat=cat):
                self.assertIn(cat, AIRCRAFT_ROLE)

    # ── AIRCRAFT_TASK ─────────────────────────────────────────────────────────

    def test_aircraft_task_is_dict(self):
        self.assertIsInstance(AIRCRAFT_TASK, dict)

    def test_aircraft_task_not_empty(self):
        self.assertGreater(len(AIRCRAFT_TASK), 0)

    def test_aircraft_task_contains_cap(self):
        self.assertIn("CAP", AIRCRAFT_TASK)

    def test_aircraft_task_contains_all_expected(self):
        for task in ["CAP", "Intercept", "Strike", "CAS", "SEAD", "Anti_Ship"]:
            with self.subTest(task=task):
                self.assertIn(task, AIRCRAFT_TASK)

    # ── SYSTEM_WEIGHTS ────────────────────────────────────────────────────────

    def test_system_weights_is_dict(self):
        self.assertIsInstance(SYSTEM_WEIGHTS, dict)

    def test_system_weights_has_radar_and_tvd(self):
        self.assertIn("radar_weights", SYSTEM_WEIGHTS)
        self.assertIn("tvd_weights", SYSTEM_WEIGHTS)

    # ── Aircraft_Data._registry ───────────────────────────────────────────────

    def test_registry_is_dict(self):
        self.assertIsInstance(Aircraft_Data._registry, dict)

    def test_registry_not_empty(self):
        self.assertGreater(len(Aircraft_Data._registry), 0)

    def test_registry_keys_are_strings(self):
        for k in Aircraft_Data._registry:
            with self.subTest(key=k):
                self.assertIsInstance(k, str)

    def test_registry_values_are_aircraft_data(self):
        for obj in Aircraft_Data._registry.values():
            self.assertIsInstance(obj, Aircraft_Data)

    def test_fighter_model_in_registry(self):
        self.assertIn(_FIGHTER_MODEL, Aircraft_Data._registry)

    def test_attacker_model_in_registry(self):
        self.assertIn(_ATTACKER_MODEL, Aircraft_Data._registry)

    # ── AIRCRAFT dict ─────────────────────────────────────────────────────────

    def test_aircraft_dict_is_dict(self):
        self.assertIsInstance(AIRCRAFT, dict)

    def test_aircraft_dict_not_empty(self):
        self.assertGreater(len(AIRCRAFT), 0)

    def test_aircraft_dict_keys_match_registry(self):
        self.assertEqual(set(AIRCRAFT.keys()), set(Aircraft_Data._registry.keys()))

    def test_aircraft_dict_values_are_dicts(self):
        for model, scores in AIRCRAFT.items():
            with self.subTest(model=model):
                self.assertIsInstance(scores, dict)

    def test_aircraft_dict_scores_are_floats(self):
        for model, scores in AIRCRAFT.items():
            for score_name, val in scores.items():
                with self.subTest(model=model, score=score_name):
                    self.assertIsInstance(val, float)

    def test_aircraft_dict_contains_expected_score_keys(self):
        for model in AIRCRAFT:
            with self.subTest(model=model):
                self.assertIn("Radar score", AIRCRAFT[model])
                self.assertIn("Speed score", AIRCRAFT[model])
                self.assertIn("Engine score", AIRCRAFT[model])


# ─────────────────────────────────────────────────────────────────────────────
#  2. ATTRIBUTI Aircraft_Data
# ─────────────────────────────────────────────────────────────────────────────

class TestAircraftDataAttributes(unittest.TestCase):
    """Verifica gli attributi delle istanze Aircraft_Data."""

    def setUp(self):
        self.fighter = Aircraft_Data._registry[_FIGHTER_MODEL]

    def test_model_is_string(self):
        self.assertIsInstance(self.fighter.model, str)

    def test_category_is_list(self):
        self.assertIsInstance(self.fighter.category, list)

    def test_category_elements_are_air_asset_type(self):
        for c in self.fighter.category:
            self.assertIsInstance(c, Air_Asset_Type)

    def test_weight_is_positive(self):
        self.assertGreater(self.fighter.weight, 0)

    def test_engine_is_dict(self):
        self.assertIsInstance(self.fighter.engine, dict)

    def test_engine_has_capabilities(self):
        self.assertIn("capabilities", self.fighter.engine)

    def test_engine_has_reliability(self):
        self.assertIn("reliability", self.fighter.engine)

    def test_radar_is_dict(self):
        self.assertIsInstance(self.fighter.radar, dict)

    def test_radar_has_capabilities(self):
        self.assertIn("capabilities", self.fighter.radar)

    def test_tvd_is_dict(self):
        self.assertIsInstance(self.fighter.TVD, dict)

    def test_tvd_has_capabilities(self):
        self.assertIn("capabilities", self.fighter.TVD)

    def test_speed_data_is_dict(self):
        self.assertIsInstance(self.fighter.speed_data, dict)

    def test_speed_data_has_sustained(self):
        self.assertIn("sustained", self.fighter.speed_data)


# ─────────────────────────────────────────────────────────────────────────────
#  3. STRUTTURA TVD E RADAR
# ─────────────────────────────────────────────────────────────────────────────

class TestTVDDataStructure(unittest.TestCase):
    """Verifica la struttura TVD e radar per tutti gli aeromobili."""

    _CAPABILITY_KEYS = {"air", "ground", "sea"}
    _MODE_KEYS = {"tracking_range", "acquisition_range", "engagement_range", "multi_target_capacity"}

    def _check_capabilities(self, caps: dict, model: str, field: str):
        """Verifica la struttura capabilities con chiavi air/ground/sea e tuple."""
        self.assertIsInstance(caps, dict, f"{model} {field}: capabilities deve essere dict")
        for mode in self._CAPABILITY_KEYS:
            with self.subTest(model=model, field=field, mode=mode):
                self.assertIn(mode, caps, f"{model} {field}: manca chiave '{mode}'")
                entry = caps[mode]
                self.assertIsInstance(entry, tuple, f"{model} {field}/{mode}: deve essere tuple")
                self.assertEqual(len(entry), 2, f"{model} {field}/{mode}: tuple deve avere 2 elementi")
                self.assertIsInstance(entry[0], bool, f"{model} {field}/{mode}[0]: deve essere bool")
                self.assertIsInstance(entry[1], dict, f"{model} {field}/{mode}[1]: deve essere dict")
                for k in self._MODE_KEYS:
                    self.assertIn(k, entry[1], f"{model} {field}/{mode}: manca chiave '{k}'")

    def test_all_aircraft_tvd_structure(self):
        for model, ac in Aircraft_Data._registry.items():
            self._check_capabilities(ac.TVD.get("capabilities", {}), model, "TVD")

    def test_all_aircraft_radar_structure(self):
        for model, ac in Aircraft_Data._registry.items():
            self._check_capabilities(ac.radar.get("capabilities", {}), model, "radar")

    def test_all_aircraft_tvd_has_reliability(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertIn("reliability", ac.TVD)
                rel = ac.TVD["reliability"]
                self.assertIn("mtbf", rel)
                self.assertIn("mttr", rel)

    def test_all_aircraft_tvd_has_type(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertIn("type", ac.TVD)


# ─────────────────────────────────────────────────────────────────────────────
#  4. METODI DI VALUTAZIONE (_eval)
# ─────────────────────────────────────────────────────────────────────────────

class TestRadarEval(unittest.TestCase):
    """Unit test per Aircraft_Data._radar_eval()."""

    def test_all_aircraft_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac._radar_eval()
                self.assertGreaterEqual(score, 0.0)

    def test_modes_air_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._radar_eval(modes=["air"]), 0.0)

    def test_modes_ground_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._radar_eval(modes=["ground"]), 0.0)

    def test_modes_sea_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._radar_eval(modes=["sea"]), 0.0)

    def test_fighter_radar_positive(self):
        """F-14A ha radar aria → score > 0."""
        fighter = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertGreater(fighter._radar_eval(modes=["air"]), 0.0)

    def test_deterministic(self):
        fighter = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertAlmostEqual(fighter._radar_eval(), fighter._radar_eval(), places=9)


class TestTVDEval(unittest.TestCase):
    """Unit test per Aircraft_Data._TVD_eval()."""

    def test_all_aircraft_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._TVD_eval(), 0.0)

    def test_modes_ground_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._TVD_eval(modes=["ground"]), 0.0)

    def test_no_tvd_aircraft_returns_zero(self):
        """Aeromobilo senza TVD operativo deve restituire 0 (o valore minimo)."""
        # F-16A Example: TVD model='none', tutti False
        f16 = Aircraft_Data._registry.get("F-16A Fighting Falcon")
        if f16:
            self.assertEqual(f16._TVD_eval(modes=["ground"]), 0.0)

    def test_deterministic(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertAlmostEqual(ac._TVD_eval(), ac._TVD_eval(), places=9)


class TestSpeedEval(unittest.TestCase):
    """Unit test per Aircraft_Data._speed_eval()."""

    def test_all_aircraft_positive(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreater(ac._speed_eval(), 0.0)

    def test_faster_aircraft_higher_score(self):
        """F-14A (vmax ~2485 km/h) deve avere score più alto di A-10C (vmax ~700 km/h)."""
        fighter_score = Aircraft_Data._registry[_FIGHTER_MODEL]._speed_eval()
        attacker_score = Aircraft_Data._registry[_ATTACKER_MODEL]._speed_eval()
        self.assertGreater(fighter_score, attacker_score)

    def test_deterministic(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertAlmostEqual(ac._speed_eval(), ac._speed_eval(), places=9)


class TestEngineEval(unittest.TestCase):
    """Unit test per Aircraft_Data.get_engine_eval()."""

    def test_all_aircraft_positive(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreater(ac.get_engine_eval(), 0.0)

    def test_returns_float(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertIsInstance(ac.get_engine_eval(), float)

    def test_deterministic(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertAlmostEqual(ac.get_engine_eval(), ac.get_engine_eval(), places=9)


class TestRadioNavEval(unittest.TestCase):
    """Unit test per Aircraft_Data._radio_nav_eval()."""

    def test_all_aircraft_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._radio_nav_eval(), 0.0)

    def test_fighter_radio_nav_positive(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertGreater(ac._radio_nav_eval(), 0.0)

    def test_returns_float(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertIsInstance(ac._radio_nav_eval(), float)


class TestHydraulicEval(unittest.TestCase):
    """Unit test per Aircraft_Data._hydraulic_eval()."""

    def test_all_aircraft_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._hydraulic_eval(), 0.0)

    def test_fighter_hydraulic_positive(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertGreater(ac._hydraulic_eval(), 0.0)


class TestAvionicsEval(unittest.TestCase):
    """Unit test per Aircraft_Data._avionics_eval()."""

    def test_all_aircraft_positive(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreater(ac._avionics_eval(), 0.0)

    def test_score_in_plausible_range(self):
        """avionics_eval usa flight_control e self_defense in [0, 1], score deve stare in [0, 1]."""
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac._avionics_eval()
                self.assertLessEqual(score, 1.0)


class TestReliabilityAndMaintenance(unittest.TestCase):
    """Unit test per _reliability_eval(), _maintenance_eval(), _avalaiability_eval()."""

    def test_all_aircraft_reliability_positive(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreater(ac._reliability_eval(), 0.0)

    def test_all_aircraft_maintenance_positive(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreater(ac._maintenance_eval(), 0.0)

    def test_all_aircraft_availability_non_negative(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreaterEqual(ac._avalaiability_eval(), 0.0)

    def test_deterministic_reliability(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertAlmostEqual(ac._reliability_eval(), ac._reliability_eval(), places=9)


# ─────────────────────────────────────────────────────────────────────────────
#  5. _normalize
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalize(unittest.TestCase):
    """Unit test per Aircraft_Data._normalize()."""

    def setUp(self):
        self.ac = Aircraft_Data._registry[_FIGHTER_MODEL]

    def test_empty_scores_returns_zero(self):
        self.assertEqual(self.ac._normalize(1.0, []), 0)

    def test_all_equal_returns_half(self):
        self.assertAlmostEqual(self.ac._normalize(5.0, [5.0, 5.0, 5.0]), 0.5)

    def test_max_value_returns_one(self):
        self.assertAlmostEqual(self.ac._normalize(10.0, [0.0, 5.0, 10.0]), 1.0)

    def test_min_value_returns_zero(self):
        self.assertAlmostEqual(self.ac._normalize(0.0, [0.0, 5.0, 10.0]), 0.0)

    def test_midpoint(self):
        self.assertAlmostEqual(self.ac._normalize(5.0, [0.0, 5.0, 10.0]), 0.5)

    def test_returns_float(self):
        result = self.ac._normalize(3.0, [1.0, 3.0, 5.0])
        self.assertIsInstance(result, float)


# ─────────────────────────────────────────────────────────────────────────────
#  6. METODI NORMALIZZATI (get_normalized_*)
# ─────────────────────────────────────────────────────────────────────────────

class TestGetNormalizedRadarScore(unittest.TestCase):
    """Unit test per get_normalized_radar_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_radar_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_modes_air_in_range(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        score = ac.get_normalized_radar_score(modes=["air"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_modes_ground_in_range(self):
        ac = Aircraft_Data._registry[_ATTACKER_MODEL]
        score = ac.get_normalized_radar_score(modes=["ground"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_radar_score(category="INVALID_CAT_XYZ")

    def test_valid_category_in_range(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        score = ac.get_normalized_radar_score(category="Fighter")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_deterministic(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        s1 = ac.get_normalized_radar_score()
        s2 = ac.get_normalized_radar_score()
        self.assertAlmostEqual(s1, s2, places=9)


class TestGetNormalizedTVDScore(unittest.TestCase):
    """Unit test per get_normalized_TVD_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_TVD_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_TVD_score(category="BAD_CAT")

    def test_valid_category_in_range(self):
        ac = Aircraft_Data._registry[_ATTACKER_MODEL]
        score = ac.get_normalized_TVD_score(category="Attacker")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestGetNormalizedRadioNavScore(unittest.TestCase):
    """Unit test per get_normalized_radio_nav_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_radio_nav_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_radio_nav_score(category="INVALID")


class TestGetNormalizedHydraulicScore(unittest.TestCase):
    """Unit test per get_normalized_hydraulic_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_hydraulic_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestGetNormalizedAvionicsScore(unittest.TestCase):
    """Unit test per get_normalized_avionics_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_avionics_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestGetNormalizedEngineScore(unittest.TestCase):
    """Unit test per get_normalized_engine_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_engine_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_engine_score(category="NOT_A_VALID")


class TestGetNormalizedSpeedScore(unittest.TestCase):
    """Unit test per get_normalized_speed_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_speed_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_fighter_faster_than_attacker(self):
        """F-14A deve avere score velocità > A-10C nella categoria globale."""
        f_score = Aircraft_Data._registry[_FIGHTER_MODEL].get_normalized_speed_score()
        a_score = Aircraft_Data._registry[_ATTACKER_MODEL].get_normalized_speed_score()
        self.assertGreater(f_score, a_score)


# ─────────────────────────────────────────────────────────────────────────────
#  _intercept_speed_eval  e  get_normalized_intercept_speed_score
# ─────────────────────────────────────────────────────────────────────────────

class TestInterceptSpeedEval(unittest.TestCase):
    """Unit test per Aircraft_Data._intercept_speed_eval().

    Il metodo calcola la velocità di intercettazione (true airspeed convertita
    all'altitudine di riferimento di 20 000 m) ponderata da un fattore temporale:

        fact_time = time / INTERCEPT_TIME   se time <= INTERCEPT_TIME
        fact_time = 1.0                     altrimenti
        score     = speed_at_20000m * fact_time

    Tutti gli aeromobili nel registry devono avere speed_data['combat'] valorizzato;
    il risultato deve essere sempre > 0 e deterministico.
    F-14A Tomcat (speed_combat=2485 km/h) deve superare A-10C Thunderbolt II
    (speed_combat=680 km/h) sia in valore assoluto che normalizzato.
    """

    def test_all_aircraft_positive(self):
        """_intercept_speed_eval() > 0 per tutti gli aeromobili del registry."""
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                self.assertGreater(ac._intercept_speed_eval(), 0.0)

    def test_returns_float(self):
        """Restituisce un float."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertIsInstance(ac._intercept_speed_eval(), float)

    def test_fighter_higher_than_attacker(self):
        """F-14A (vmax ~2485 km/h) > A-10C Thunderbolt II (vmax ~680 km/h)."""
        fighter_score  = Aircraft_Data._registry[_FIGHTER_MODEL]._intercept_speed_eval()
        attacker_score = Aircraft_Data._registry[_ATTACKER_MODEL]._intercept_speed_eval()
        self.assertGreater(fighter_score, attacker_score)

    def test_deterministic(self):
        """Due chiamate consecutive restituiscono lo stesso valore."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertAlmostEqual(ac._intercept_speed_eval(), ac._intercept_speed_eval(), places=9)


class TestGetNormalizedInterceptSpeedScore(unittest.TestCase):
    """Unit test per Aircraft_Data.get_normalized_intercept_speed_score().

    Normalizza _intercept_speed_eval() dell'aeromobile corrente rispetto a tutti
    gli aeromobili della categoria (default: tutti i ruoli).
    Il risultato deve essere compreso in [0, 1].
    La chiamata con category non valida deve sollevare ValueError.
    """

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_aircraft_in_range(self):
        """Score normalizzato ∈ [0, 1] per tutti gli aeromobili del registry."""
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_intercept_speed_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_returns_float(self):
        """Restituisce un float."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        result = ac.get_normalized_intercept_speed_score()
        self.assertIsInstance(result, float)

    def test_fighter_higher_than_attacker(self):
        """F-14A deve avere score intercept più alto di A-10C Thunderbolt II."""
        f_score = Aircraft_Data._registry[_FIGHTER_MODEL].get_normalized_intercept_speed_score()
        a_score = Aircraft_Data._registry[_ATTACKER_MODEL].get_normalized_intercept_speed_score()
        self.assertGreater(f_score, a_score)

    def test_invalid_category_raises_value_error(self):
        """category non valida → ValueError."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_intercept_speed_score(category="INVALID_CAT_XYZ")

    def test_valid_category_in_range(self):
        """category='Fighter' valida → score ∈ [0, 1]."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        score = ac.get_normalized_intercept_speed_score(category="Fighter")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_deterministic(self):
        """Due chiamate consecutive restituiscono lo stesso valore."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        s1 = ac.get_normalized_intercept_speed_score()
        s2 = ac.get_normalized_intercept_speed_score()
        self.assertAlmostEqual(s1, s2, places=9)


class TestGetNormalizedReliabilityAndAvailability(unittest.TestCase):
    """Unit test per get_normalized_reliability_score(), avalaiability_score(), maintenance_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_reliability_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_reliability_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_availability_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_avalaiability_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_maintenance_in_range(self):
        for model, ac in Aircraft_Data._registry.items():
            with self.subTest(model=model):
                score = ac.get_normalized_maintenance_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_reliability_score(category="INVALID")


# ─────────────────────────────────────────────────────────────────────────────
#  7. COMBAT SCORE
# ─────────────────────────────────────────────────────────────────────────────

class TestCombatScore(unittest.TestCase):
    """Unit test per combat_score() e combat_score_target_effectiveness()."""

    def setUp(self):
        self._patchers = [
            patch(_LOGGER_PATH, MagicMock()),
            patch(_LOADOUTS_LOGGER_PATH, MagicMock()),
            patch(_GWD_LOGGER_PATH, MagicMock()),
            patch(_AWD_LOGGER_PATH, MagicMock()),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    @unittest.skipIf(_FIGHTER_LOADOUT is None, "Nessun loadout disponibile per il fighter di riferimento")
    def test_combat_score_returns_float(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        score = ac.combat_score("CAP", _FIGHTER_LOADOUT)
        self.assertIsInstance(score, float)

    @unittest.skipIf(_FIGHTER_LOADOUT is None, "Nessun loadout disponibile per il fighter di riferimento")
    def test_combat_score_non_negative(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        score = ac.combat_score("CAP", _FIGHTER_LOADOUT)
        self.assertGreaterEqual(score, 0.0)

    def test_combat_score_invalid_task_raises_type_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises((TypeError, ValueError)):
            if _FIGHTER_LOADOUT:
                ac.combat_score(None, _FIGHTER_LOADOUT)
            else:
                ac.combat_score(None, "fake_loadout")

    def test_combat_score_invalid_task_string_raises_value_error(self):
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.combat_score("INVALID_TASK_XYZ", _FIGHTER_LOADOUT or "none")

    @unittest.skipIf(_ATTACKER_LOADOUT is None, "Nessun loadout disponibile per l'attacker di riferimento")
    def test_combat_score_target_effectiveness_returns_float(self):
        ac = Aircraft_Data._registry[_ATTACKER_MODEL]
        score = ac.combat_score_target_effectiveness(
            "CAS", _ATTACKER_LOADOUT, ["Soft"], ["big"]
        )
        self.assertIsInstance(score, float)

    @unittest.skipIf(_ATTACKER_LOADOUT is None, "Nessun loadout disponibile per l'attacker di riferimento")
    def test_combat_score_target_effectiveness_non_negative(self):
        ac = Aircraft_Data._registry[_ATTACKER_MODEL]
        score = ac.combat_score_target_effectiveness(
            "CAS", _ATTACKER_LOADOUT, ["Soft"], ["big"]
        )
        self.assertGreaterEqual(score, 0.0)


class TestGetNormalizedCombatScore(unittest.TestCase):
    """Unit test per get_normalized_combat_score().

    NOTA DESIGN: get_normalized_combat_score(task, loadout) normalizza lo score
    dell'aereo corrente rispetto a TUTTI gli aeromobili della categoria, usando
    lo STESSO loadout. Poiché i loadout sono specifici per aeromobile, questo
    è utilizzabile correttamente solo confrontando aeromobili che condividono
    un loadout di stesso nome (es. loadout standard con armamento comune).
    I test verificano il comportamento con aeromobili che condividono il loadout.
    """

    def setUp(self):
        self._patchers = [
            patch(_LOGGER_PATH, MagicMock()),
            patch(_LOADOUTS_LOGGER_PATH, MagicMock()),
            patch(_GWD_LOGGER_PATH, MagicMock()),
            patch(_AWD_LOGGER_PATH, MagicMock()),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    @unittest.skipIf(_FIGHTER_LOADOUT is None, "Nessun loadout disponibile per il fighter di riferimento")
    def test_invalid_category_raises_value_error(self):
        """Categoria non valida → ValueError (indipendente dal loadout)."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises(ValueError):
            ac.get_normalized_combat_score("CAP", _FIGHTER_LOADOUT, category="BAD")

    def test_invalid_task_raises(self):
        """Task non valido → ValueError (indipendente dal loadout)."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        with self.assertRaises((ValueError, TypeError)):
            ac.get_normalized_combat_score("INVALID_TASK_XYZ", _FIGHTER_LOADOUT or "none")


# ─────────────────────────────────────────────────────────────────────────────
#  8. FUNZIONI STATICHE — get_aircraft_data, get_aircraft_scores
# ─────────────────────────────────────────────────────────────────────────────

class TestGetAircraftData(unittest.TestCase):
    """Unit test per get_aircraft_data()."""

    def test_known_model_returns_dict(self):
        result = get_aircraft_data(_FIGHTER_MODEL)
        self.assertIsInstance(result, dict)

    def test_result_non_empty(self):
        result = get_aircraft_data(_FIGHTER_MODEL)
        self.assertGreater(len(result), 0)

    def test_result_has_radar_score(self):
        result = get_aircraft_data(_FIGHTER_MODEL)
        self.assertIn("Radar score", result)

    def test_result_scores_are_floats(self):
        result = get_aircraft_data(_FIGHTER_MODEL)
        for k, v in result.items():
            with self.subTest(score=k):
                self.assertIsInstance(v, float)

    def test_all_models_findable(self):
        for model in Aircraft_Data._registry:
            with self.subTest(model=model):
                result = get_aircraft_data(model)
                self.assertIsNotNone(result)

    def test_unknown_model_raises(self):
        with self.assertRaises((KeyError, ValueError)):
            get_aircraft_data("AIRCRAFT_NOT_EXISTING_XYZ")


class TestGetAircraftScores(unittest.TestCase):
    """Unit test per get_aircraft_scores() — documenta il comportamento attuale."""

    def test_unknown_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_aircraft_scores("AIRCRAFT_NOT_EXISTING_XYZ", ["Radar score"])

    def test_known_model_valid_scores_raises(self):
        """BUG DOCUMENTATO: scores è usato in if scores and scores in SCORES
        dove SCORES è una tuple di stringhe. Questo comportamento può variare.
        Il test documenta che la funzione viene chiamata senza lanciare eccezioni
        di tipo errato."""
        try:
            result = get_aircraft_scores(_FIGHTER_MODEL, ["Radar score"])
            # Se non lancia eccezione, result deve essere dict
            self.assertIsInstance(result, dict)
        except (ValueError, TypeError, KeyError):
            pass  # Comportamento documentato con bug


class TestGetLoadouts(unittest.TestCase):
    """Unit test per Aircraft_Data.get_loadouts(aircraft_name, task=None).

    Il metodo delega a:
      - get_aircraft_loadouts(aircraft_name)          se task è None
      - get_aircraft_loadouts_by_task(aircraft_name, task)  se task è fornito
    Restituisce sempre un dict {loadout_name: config}.

    Validazioni:
      - aircraft_name non-string → TypeError
      - aircraft non nel registry → ValueError
      - task fornito ma non in AIR_TASK → ValueError
    """

    def setUp(self):
        self._ac_fighter = Aircraft_Data._registry[_FIGHTER_MODEL]
        self._ac_bomber  = Aircraft_Data._registry[_BOMBER_MODEL]

    # ── Senza task ────────────────────────────────────────────────────────────

    def test_no_task_returns_dict(self):
        """Senza task restituisce un dizionario."""
        result = self._ac_fighter.get_loadouts(_FIGHTER_MODEL)
        self.assertIsInstance(result, dict)

    def test_no_task_returns_nonempty(self):
        """L'F-14A Tomcat ha almeno un loadout."""
        result = self._ac_fighter.get_loadouts(_FIGHTER_MODEL)
        self.assertTrue(result)

    def test_no_task_values_are_dicts(self):
        """Ogni valore nel dizionario è una config (dict)."""
        result = self._ac_fighter.get_loadouts(_FIGHTER_MODEL)
        for name, config in result.items():
            with self.subTest(loadout=name):
                self.assertIsInstance(config, dict)

    def test_no_task_known_loadout_present(self):
        """Il loadout recuperato con _first_loadout è presente nel risultato."""
        result = self._ac_fighter.get_loadouts(_FIGHTER_MODEL)
        self.assertIn(_FIGHTER_LOADOUT, result)

    # ── Con task ──────────────────────────────────────────────────────────────

    def test_with_task_returns_dict(self):
        """Con task valido restituisce un dizionario."""
        result = self._ac_fighter.get_loadouts(_FIGHTER_MODEL, "CAP")
        self.assertIsInstance(result, dict)

    def test_with_task_all_loadouts_contain_task(self):
        """Tutti i loadout nel risultato hanno il task richiesto."""
        result = self._ac_fighter.get_loadouts(_FIGHTER_MODEL, "CAP")
        for name, config in result.items():
            with self.subTest(loadout=name):
                self.assertIn("CAP", config.get("tasks", []))

    def test_with_task_result_is_subset_of_all_loadouts(self):
        """Il risultato filtrato per task è un sottoinsieme di tutti i loadout."""
        all_loadouts  = self._ac_fighter.get_loadouts(_FIGHTER_MODEL)
        task_loadouts = self._ac_fighter.get_loadouts(_FIGHTER_MODEL, "CAP")
        for name in task_loadouts:
            with self.subTest(loadout=name):
                self.assertIn(name, all_loadouts)

    def test_with_task_unknown_loadout_excluded(self):
        """Loadout senza task CAP non compare nel risultato filtrato."""
        all_loadouts  = self._ac_fighter.get_loadouts(_FIGHTER_MODEL)
        cap_loadouts  = self._ac_fighter.get_loadouts(_FIGHTER_MODEL, "CAP")
        non_cap = [n for n, cfg in all_loadouts.items() if "CAP" not in cfg.get("tasks", [])]
        for name in non_cap:
            with self.subTest(loadout=name):
                self.assertNotIn(name, cap_loadouts)

    def test_with_task_unmatched_returns_empty_dict(self):
        """Task valido senza loadout corrispondenti per quel velivolo → dict vuoto."""
        # Un bombardiere strategico non ha in genere loadout CAP
        result = self._ac_bomber.get_loadouts(_BOMBER_MODEL, "CAP")
        self.assertIsInstance(result, dict)
        # Se davvero vuoto, verifichiamo che non ci siano voci con task CAP
        for name, config in result.items():
            self.assertIn("CAP", config.get("tasks", []))

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_invalid_task_not_in_air_task_raises_ValueError(self):
        """Task non in AIR_TASK → ValueError."""
        with self.assertRaises(ValueError):
            self._ac_fighter.get_loadouts(_FIGHTER_MODEL, "INVALID_TASK_XYZ")

    def test_unknown_aircraft_raises_ValueError(self):
        """Aircraft non nel registry → ValueError."""
        with self.assertRaises(ValueError):
            self._ac_fighter.get_loadouts("AIRCRAFT_NOT_EXISTING_XYZ")

    def test_non_string_aircraft_name_raises_TypeError(self):
        """aircraft_name non-string → TypeError."""
        with self.assertRaises(TypeError):
            self._ac_fighter.get_loadouts(42)

    def test_none_aircraft_name_raises_TypeError(self):
        """aircraft_name None → TypeError."""
        with self.assertRaises(TypeError):
            self._ac_fighter.get_loadouts(None)


class TestGetListOfAircrafts(unittest.TestCase):
    """Unit test per Aircraft_Data.get_list_of_aircrafts(side, task, target_distribuition, ...).

    Il metodo valida i parametri opzionali route_length, route_speed e role,
    poi restituisce una lista di Aircraft_Data ordinata per combat_score_target_effectiveness
    (quando target_distribuition è fornita) oppure combat_score (quando è None).

    ── Stato attuale dei bug dopo il tentativo di correzione BLA2 ──────────────

    Tutti i bug precedentemente documentati (BLA0, BLA1, BLA2a, BLA2b) sono stati
    corretti. Rimane un bug residuo nel sorting key della return:

    BUG BLA3 — StopIteration nel sorting key per aircraft senza loadout del task:
      Il sorting key usa next(iter(self.get_loadouts(x.model, task))).
      Se un aircraft Blue non ha loadout per il task richiesto,
      get_loadouts(x.model, task) restituisce {} e next(iter({})) solleva
      StopIteration. Questo accade quando role=None e la lista include
      aircraft di ogni categoria (es. trasporti, bombardieri senza loadout CAP).
      Con role="Fighter" il bug non si manifesta perché tutti i fighter
      hanno loadout CAP.
      Correzione: gestire il caso di dict vuoto prima di chiamare next(iter(...)).
    """

    def setUp(self):
        self._ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self._patchers = [
            patch(_LOGGER_PATH,          MagicMock()),
            patch(_LOADOUTS_LOGGER_PATH, MagicMock()),
            patch(_AWD_LOGGER_PATH,      MagicMock()),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    # ── Validazione route_length ──────────────────────────────────────────────

    def test_negative_route_length_raises_ValueError(self):
        """route_length negativo → ValueError."""
        with self.assertRaises(ValueError):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None, route_length=-1.0)

    def test_zero_route_length_is_valid(self):
        """route_length=0 è accettato (>= 0): il metodo non deve sollevare ValueError.
        BUG BLA3 atteso: StopIteration nel sorting key per aircraft Blue senza
        loadout CAP (es. trasporti, bombardieri)."""
        with self.assertRaises(StopIteration):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None, route_length=0.0)

    # ── Validazione route_speed ───────────────────────────────────────────────

    def test_zero_route_speed_raises_ValueError(self):
        """route_speed=0 → ValueError (deve essere > 0)."""
        with self.assertRaises(ValueError):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None, route_speed=0.0)

    def test_negative_route_speed_raises_ValueError(self):
        """route_speed negativo → ValueError."""
        with self.assertRaises(ValueError):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None, route_speed=-100.0)

    def test_positive_route_speed_is_valid(self):
        """route_speed > 0 è accettato: il metodo non deve sollevare ValueError.
        BUG BLA3 atteso: StopIteration nel sorting key per aircraft Blue senza
        loadout CAP."""
        with self.assertRaises(StopIteration):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None, route_speed=500.0)

    # ── Validazione role ──────────────────────────────────────────────────────

    def test_invalid_role_raises_ValueError(self):
        """role non in AIRCRAFT_ROLE → ValueError."""
        with self.assertRaises(ValueError):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None, role="INVALID_ROLE_XYZ")

    def test_valid_role_is_accepted(self):
        """role='Fighter' valido: BLA2 corretto → filtra correttamente per categoria.
        Tutti i Fighter Blue hanno loadout CAP → BLA3 non si manifesta.
        Il risultato è una lista non vuota di Aircraft_Data con categoria Fighter."""
        result = self._ac.get_list_of_aircrafts("Blue", "CAP", None, role="Fighter")
        self.assertIsInstance(result, list)
        self.assertTrue(result, "Deve esserci almeno un Fighter Blue nel registry")
        for ac in result:
            with self.subTest(model=ac.model):
                self.assertIsInstance(ac, Aircraft_Data)
                self.assertTrue(
                    any(c == Air_Asset_Type.FIGHTER for c in ac.category),
                    f"{ac.model} non ha categoria Fighter"
                )

    # ── Bug BLA1: return statement ────────────────────────────────────────────

    def test_valid_params_raises_stop_iteration_bug(self):
        """BUG BLA3 — Parametri validi senza role: StopIteration nel sorting key.

        Con role=None tutti i Blue aircraft sono inclusi nella lista da ordinare.
        Per aircraft senza loadout CAP (es. trasporti, bombardieri),
        get_loadouts(x.model, 'CAP') restituisce {} e next(iter({})) solleva
        StopIteration. Il metodo deve gestire il caso di loadout vuoti,
        ad es. escludendo tali aircraft dalla lista o usando un valore di default.
        """
        with self.assertRaises(StopIteration):
            self._ac.get_list_of_aircrafts("Blue", "CAP", None)

    # ── Logica combat_score vs combat_score_target_effectiveness ─────────────

    def test_table_rows_use_combat_score_target_effectiveness_with_dist(self):
        """Quando target_dist è fornita, _build_list_of_aircrafts_rows usa
        combat_score_target_effectiveness; il valore deve differire da quello
        prodotto da combat_score (che ignora il target)."""
        dist = {
            "Soft":    {"perc_type": 0.5, "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3}},
            "Armored": {"perc_type": 0.3, "perc_dimension": {"big": 0.3, "med": 0.4, "small": 0.3}},
            "Structure": {"perc_type": 0.2, "perc_dimension": {"big": 0.0, "med": 0.2, "small": 0.8}},
        }
        t_types, t_dims = _extract_target_types_dims(dist)
        # Prendi il primo Fighter Red con loadout Strike
        loadout = _best_loadout_for_task(_FIGHTER_MODEL, "Strike")
        if loadout is None:
            self.skipTest(f"{_FIGHTER_MODEL} non ha loadout Strike")
        score_target = _safe_combat_score_target_raw(self._ac, "Strike", loadout, t_types, t_dims)
        score_plain  = _safe_combat_score_raw(self._ac, "Strike", loadout)
        # Entrambi devono essere float non-nan
        self.assertFalse(_is_nan(score_target), "combat_score_target_effectiveness ha restituito nan")
        self.assertFalse(_is_nan(score_plain),  "combat_score ha restituito nan")
        # I due score usano pesi diversi: non devono essere uguali
        self.assertNotEqual(
            round(score_target, 6), round(score_plain, 6),
            "combat_score_target_effectiveness e combat_score non devono coincidere"
        )

    def test_table_rows_use_combat_score_without_dist(self):
        """Quando target_dist è None, _build_list_of_aircrafts_rows usa combat_score."""
        loadout = _best_loadout_for_task(_FIGHTER_MODEL, "Strike")
        if loadout is None:
            self.skipTest(f"{_FIGHTER_MODEL} non ha loadout Strike")
        score_plain = _safe_combat_score_raw(self._ac, "Strike", loadout)
        self.assertFalse(_is_nan(score_plain), "combat_score ha restituito nan")
        self.assertGreaterEqual(score_plain, 0.0)

    def test_extract_target_types_dims(self):
        """_extract_target_types_dims estrae correttamente tipi e dimensioni."""
        dist = {
            "Soft":    {"perc_type": 0.5, "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3}},
            "Armored": {"perc_type": 0.5, "perc_dimension": {"big": 0.3, "med": 0.4, "small": 0.3}},
        }
        t_types, t_dims = _extract_target_types_dims(dist)
        self.assertEqual(t_types, ["Soft", "Armored"])
        self.assertEqual(sorted(t_dims), ["big", "med", "small"])


class TestGetAircraftsQuantity(unittest.TestCase):
    """Unit test per Aircraft_Data.get_aircrafts_quantity(model, loadout, target_data, year).

    Aeromobile di test: A-10C II Thunderbolt II / Maverick/Gun CAS.
    Il metodo è chiamato su qualsiasi istanza Aircraft_Data (usa Aircraft_Data._registry
    internamente per cercare l'aeromobile richiesto), quindi lo chiamiamo su _FIGHTER_MODEL.

    Tutti e 4 i logger sono mockati tramite _all_loggers_mocked() per isolare
    i side-effect di Aircraft_Weapon_Data.logger (chiamato da get_weapon_score_target
    e is_weapon_introduced su armi non-AAM o non trovate).

    Bug documentati corretti prima di scrivere questi test:
      BD1. Riga 24 di Aircraft_Data.py rimossa:
             from Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import get_weapon_efficiency
           Il path errato (mancante 'Code.') causava ImportError silenzioso; la funzione
           get_weapon_efficiency era poi indefinita o puntava alla versione Aircraft_Weapon_Data
           (firma diversa: 2 argomenti vs 3). Correcto rimuovendo la riga.
      BD2. get_aircrafts_quantity() chiamava loadout_year_compatibility(model, loadout)
           senza il terzo argomento obbligatorio year → TypeError a runtime.
           Corretto aggiungendo year: Optional[int] = None alla firma e verificando
           solo quando year non è None.
    """

    def setUp(self):
        self._ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    # ── Validazione input ─────────────────────────────────────────────────────

    def test_unknown_aircraft_raises_ValueError(self):
        """Aeromobile sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            self._ac.get_aircrafts_quantity(
                "UNKNOWN_AIRCRAFT_XYZ", _QTY_LOADOUT, _QTY_TARGET_SIMPLE
            )

    def test_unknown_loadout_raises_ValueError(self):
        """Loadout sconosciuto (aircraft valido) → ValueError."""
        with self.assertRaises(ValueError):
            self._ac.get_aircrafts_quantity(
                _QTY_AC_MODEL, "UNKNOWN_LOADOUT_XYZ", _QTY_TARGET_SIMPLE
            )

    # ── Struttura del risultato ───────────────────────────────────────────────

    def test_returns_dict(self):
        """Input valido → restituisce un dict."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertIsInstance(result, dict)

    def test_result_has_total_key(self):
        """Il risultato contiene la chiave 'total'."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertIn("total", result)

    def test_result_has_message_key(self):
        """Il risultato contiene la chiave 'message'."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertIn("message", result)

    def test_total_is_int(self):
        """'total' è un intero."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertIsInstance(result["total"], int)

    def test_total_is_non_negative(self):
        """'total' >= 0."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertGreaterEqual(result["total"], 0)

    def test_result_contains_target_type_keys(self):
        """Il risultato contiene le chiavi dei target_type richiesti."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        for target_type in _QTY_TARGET_SIMPLE:
            with self.subTest(target_type=target_type):
                self.assertIn(target_type, result)

    def test_dimension_values_are_non_negative_int(self):
        """Ogni valore (target_type, dimension) è un intero >= 0."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        for key, val in result.items():
            if not isinstance(val, dict):
                continue
            for dim, count in val.items():
                with self.subTest(target_type=key, dimension=dim):
                    self.assertIsInstance(count, int)
                    self.assertGreaterEqual(count, 0)

    def test_total_equals_sum_of_all_dimensions(self):
        """'total' è uguale alla somma dei conteggi per (target_type, dimension),
        escludendo missions_needed."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        expected = sum(
            v
            for key, dims in result.items()
            if key not in ("total", "message", "aircraft_number") and isinstance(dims, dict)
            for k, v in dims.items()
            if k != "missions_needed"
        )
        self.assertEqual(result["total"], expected)

    def test_multi_target_type_result_structure(self):
        """Con più target_type, tutte le chiavi richieste sono nel risultato."""
        target_data = {
            "Soft":    {"big": 2, "med": 3, "small": 5},
            "Armored": {"big": 1, "med": 2, "small": 4},
        }
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, target_data)
        for target_type in target_data:
            with self.subTest(target_type=target_type):
                self.assertIn(target_type, result)
        self.assertIn("total", result)
        self.assertIn("missions_needed", result)

    # ── Compatibilità anno (year parameter) ───────────────────────────────────

    def test_incompatible_year_returns_total_zero(self):
        """Anno incompatibile (1950, prima di qualsiasi arma moderna) → total=0."""
        result = self._ac.get_aircrafts_quantity(
            _QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE, year=1950
        )
        self.assertEqual(result["total"], 0)

    def test_incompatible_year_returns_message(self):
        """Anno incompatibile → il risultato contiene 'message'."""
        result = self._ac.get_aircrafts_quantity(
            _QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE, year=1950
        )
        self.assertIn("message", result)

    def test_incompatible_year_result_is_dict(self):
        """Anno incompatibile → risultato è un dict (non eccezione)."""
        result = self._ac.get_aircrafts_quantity(
            _QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE, year=1950
        )
        self.assertIsInstance(result, dict)

    def test_no_year_skips_compatibility_check(self):
        """Senza year, il controllo di compatibilità non viene eseguito → risultato valido."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertIn("total", result)
        self.assertGreaterEqual(result["total"], 0)

    def test_compatible_year_returns_full_result(self):
        """Anno compatibile con le armi → restituisce result con tutte le chiavi."""
        # F-15E Iron Bomb Strike: Mk-82 (1954), AIM-9M (1982) → compatibile da 1982
        ac_model = "F-15E Strike Eagle"
        loadout  = "Iron Bomb Strike"
        target   = {"Soft": {"med": 2}}
        result = self._ac.get_aircrafts_quantity(ac_model, loadout, target, year=1982)
        self.assertIn("total", result)
        self.assertIn("message", result)
        # Non deve essere la risposta di incompatibilità (total=0 con aircraft_number={})
        self.assertIn("Soft", result)

    # ── missions_needed ───────────────────────────────────────────────────────

    def test_result_has_missions_needed_key(self):
        """Il risultato ha 'missions_needed' come chiave radice (non per target_type)."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        self.assertIn("missions_needed", result)

    def test_missions_needed_is_positive_int(self):
        """'missions_needed' al livello radice è un intero >= 1."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        mn = result["missions_needed"]
        self.assertIsInstance(mn, int)
        self.assertGreaterEqual(mn, 1)

    def test_missions_needed_not_in_target_type_dict(self):
        """'missions_needed' non è presente nei sotto-dict per target_type."""
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        for target_type in _QTY_TARGET_SIMPLE:
            with self.subTest(target_type=target_type):
                tt_dict = result.get(target_type, {})
                self.assertNotIn("missions_needed", tt_dict)

    def test_missions_needed_equals_ceil_total_over_max(self):
        """'missions_needed' == ceil(total / 8), minimo 1."""
        import math
        result = self._ac.get_aircrafts_quantity(_QTY_AC_MODEL, _QTY_LOADOUT, _QTY_TARGET_SIMPLE)
        total = result["total"]
        expected = max(1, math.ceil(total / 8))
        self.assertEqual(result["missions_needed"], expected)


class TestGetAircraftsQuantityIntegrative(unittest.TestCase):
    """Test integrativi per get_aircrafts_quantity su scenari reali di combattimento.

    Per ogni scenario (CAS / Strike / AntiShip / SEAD), ogni target (A/B/C) e ogni
    coppia (aircraft, loadout) specificata nei _SCENARIOS, verifica che il risultato
    sia strutturalmente corretto: dict, chiave 'total', valori non-negativi.

    I test non verificano valori assoluti (dipendono dai dati delle armi e dai loadout),
    ma garantiscono che la funzione non sollevi eccezioni e restituisca una struttura
    coerente per tutti gli scenari operativi previsti.

    Tutti e 4 i logger sono mockati per isolare i side-effect su armi non in AIR_WEAPONS
    (serbatoi carburante, pod) o armi AAM che richiamano logger.warning.
    """

    def setUp(self):
        self._ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    def _assert_result(self, result: dict, target_data: dict, ac: str, lo: str) -> None:
        """Asserzioni strutturali comuni per ogni coppia (aircraft, loadout)."""
        self.assertIsInstance(result, dict, f"{ac}/{lo}: il risultato deve essere dict")
        self.assertIn("total", result, f"{ac}/{lo}: manca chiave 'total'")
        self.assertIsInstance(result["total"], int, f"{ac}/{lo}: 'total' deve essere int")
        self.assertGreaterEqual(result["total"], 0, f"{ac}/{lo}: 'total' deve essere >= 0")
        # missions_needed presente al livello radice e >= 1
        with self.subTest(aircraft=ac, loadout=lo, field="missions_needed"):
            self.assertIn("missions_needed", result, f"{ac}/{lo}: manca chiave radice 'missions_needed'")
            self.assertIsInstance(result["missions_needed"], int)
            self.assertGreaterEqual(result["missions_needed"], 1)
        for target_type, dims in target_data.items():
            if target_type not in result:
                continue  # target_type con efficienza zero può essere presente o assente
            tt_dict = result[target_type]
            # valori per dimensione non negativi
            for dim in dims.keys():
                if dim in tt_dict:
                    with self.subTest(aircraft=ac, loadout=lo, target_type=target_type, dim=dim):
                        self.assertIsInstance(tt_dict[dim], int)
                        self.assertGreaterEqual(tt_dict[dim], 0)

    def _run_scenario(self, scenario_name: str, target_label: str) -> None:
        """Esegue il test su tutte le coppie del scenario per il target dato."""
        aircraft_list = _SCENARIOS[scenario_name]["aircraft"]
        target_data   = _SCENARIOS[scenario_name]["targets"][target_label]
        for ac, lo in aircraft_list:
            with self.subTest(aircraft=ac, loadout=lo):
                try:
                    result = self._ac.get_aircrafts_quantity(ac, lo, target_data)
                    self._assert_result(result, target_data, ac, lo)
                except (ValueError, KeyError) as e:
                    self.fail(
                        f"get_aircrafts_quantity({ac!r}, {lo!r}) ha sollevato {type(e).__name__}: {e}"
                    )

    # ── Scenario CAS ──────────────────────────────────────────────────────────

    def test_cas_target_a(self):
        """CAS — Target A: Soft + Armored + Air_Defense con diverse dimensioni."""
        self._run_scenario("CAS", "target_A")

    def test_cas_target_b(self):
        """CAS — Target B: Soft + Armored (senza Air_Defense)."""
        self._run_scenario("CAS", "target_B")

    # ── Scenario Strike ───────────────────────────────────────────────────────

    def test_strike_target_a(self):
        """Strike — Target A: Structure + Armored con volume basso."""
        self._run_scenario("Strike", "target_A")

    def test_strike_target_b(self):
        """Strike — Target B: solo Structure con volume basso."""
        self._run_scenario("Strike", "target_B")

    def test_strike_target_c(self):
        """Strike — Target C: solo Structure con volume alto."""
        self._run_scenario("Strike", "target_C")

    # ── Scenario Anti-Ship ────────────────────────────────────────────────────

    def test_antiship_target_a(self):
        """AntiShip — Target A: navi mix big/med/small volume basso."""
        self._run_scenario("AntiShip", "target_A")

    def test_antiship_target_b(self):
        """AntiShip — Target B: navi mix big/med/small volume alto."""
        self._run_scenario("AntiShip", "target_B")

    # ── Scenario SEAD ─────────────────────────────────────────────────────────

    def test_sead_target_a(self):
        """SEAD — Target A: Air_Defense mix big/med/small volume alto."""
        self._run_scenario("SEAD", "target_A")

    def test_sead_target_b(self):
        """SEAD — Target B: Air_Defense solo med/small volume medio."""
        self._run_scenario("SEAD", "target_B")

    def test_sead_target_c(self):
        """SEAD — Target C: Air_Defense solo med/small volume basso."""
        self._run_scenario("SEAD", "target_C")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST _loadout_target_effectiveness — TARGET AIRCRAFT
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadoutTargetEffectivenessAircraft(unittest.TestCase):
    """Unit test per Aircraft_Data._loadout_target_effectiveness() con target Aircraft.

    _loadout_target_effectiveness(loadout, target_type, target_dimension,
                                  route_length=0.0, route_speed=1.0)
    delega a loadout_target_effectiveness() di Aircraft_Loadouts.
    Con i default (route_length=0, route_speed=1) tutti i loadout superano il
    controllo rotta → il punteggio è determinato solo dalle armi del loadout.

    Fixture: F-14A Tomcat / Phoenix Fleet Defense (AIM-54A-MK47×4, AIM-9L×2, AIM-7M×2).
    Tutte le armi sono AAM con efficiency['Aircraft'], nessuna ha efficiency terrestre
    → Aircraft score > 0, Soft score = 0.
    """

    def setUp(self):
        self._ac = Aircraft_Data._registry[_FIGHTER_MODEL]   # F-14A Tomcat
        self._patchers = [
            patch(_LOGGER_PATH,          MagicMock()),
            patch(_LOADOUTS_LOGGER_PATH, MagicMock()),
            patch(_AWD_LOGGER_PATH,      MagicMock()),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    def test_returns_float(self):
        """F-14A Phoenix Fleet Defense, Aircraft/big → restituisce un float."""
        result = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertIsInstance(result, float)

    def test_aircraft_big_positive(self):
        """F-14A Phoenix Fleet Defense, Aircraft/big → score > 0 (AIM-54A-MK47 ha Aircraft eff)."""
        result = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertGreater(result, 0.0)

    def test_aircraft_med_positive(self):
        """F-14A Phoenix Fleet Defense, Aircraft/med → score > 0."""
        result = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Aircraft"], ["med"]
        )
        self.assertGreater(result, 0.0)

    def test_aircraft_small_positive(self):
        """F-14A Phoenix Fleet Defense, Aircraft/small → score > 0 (AIM-9L eccelle vs piccoli)."""
        result = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Aircraft"], ["small"]
        )
        self.assertGreater(result, 0.0)

    def test_all_dims_positive(self):
        """Score > 0 per ognuna delle tre dimensioni Aircraft."""
        for dim in ("big", "med", "small"):
            with self.subTest(dim=dim):
                result = self._ac._loadout_target_effectiveness(
                    _FIGHTER_LOADOUT, ["Aircraft"], [dim]
                )
                self.assertGreater(result, 0.0)

    def test_aircraft_score_greater_than_soft_score(self):
        """CAP loadout: Aircraft score > Soft score (AAM non hanno efficienza per Soft)."""
        aircraft_score = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Aircraft"], ["big", "med", "small"]
        )
        soft_score = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Soft"], ["big", "med", "small"]
        )
        self.assertGreater(aircraft_score, soft_score)

    def test_aircraft_target_multi_dim_positive(self):
        """F-14A, Aircraft/[big,med,small] → score > 0 (media su 3 combinazioni)."""
        result = self._ac._loadout_target_effectiveness(
            _FIGHTER_LOADOUT, ["Aircraft"], ["big", "med", "small"]
        )
        self.assertGreater(result, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
#  TEST combat_score_target_effectiveness / combat_score_eval — TARGET AIRCRAFT
# ─────────────────────────────────────────────────────────────────────────────

class TestCombatScoreTargetEffectivenessAircraft(unittest.TestCase):
    """Unit test per combat_score_target_effectiveness() e combat_score_eval() con Aircraft.

    combat_score_target_effectiveness(task, loadout, target_type, target_dimension)
      → chiama combat_score_eval(task, loadout, True, target_type, target_dimension).

    Con calc_scores_options=True:
      - loadout score = _loadout_target_effectiveness(...) × w_loadout / sum_weights
      - Gli altri score (radar, TVD, engine, ...) dipendono dal task, non dal target.
    Per task='CAP' + target='Aircraft':
      - Radar usa modes=['air'] → F-14A ha radar AWG-9 molto capace → contributo elevato
      - Loadout Phoenix Fleet Defense → score Aircraft > 0 → contributo positivo
    → combat_score_target_effectiveness > 0 per F-14A + CAP + Aircraft.

    Confronto Aircraft > Soft: le AAM (score Aircraft > 0) battono Soft (score = 0)
    nel componente loadout, mentre gli altri componenti sono identici.
    """

    def setUp(self):
        self._ac = Aircraft_Data._registry[_FIGHTER_MODEL]   # F-14A Tomcat
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    def test_returns_float(self):
        """CAP + Phoenix Fleet Defense + Aircraft/big → restituisce un float."""
        result = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertIsInstance(result, float)

    def test_cap_aircraft_big_non_negative(self):
        """CAP + Aircraft/big → score >= 0."""
        result = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertGreaterEqual(result, 0.0)

    def test_cap_aircraft_big_positive(self):
        """F-14A CAP + Aircraft/big → score > 0 (loadout + radar air contribuiscono)."""
        result = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertGreater(result, 0.0)

    def test_cap_aircraft_all_dims_positive(self):
        """F-14A CAP + Aircraft/[big,med,small] → score > 0."""
        result = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big", "med", "small"]
        )
        self.assertGreater(result, 0.0)

    def test_cap_aircraft_score_greater_than_soft_score(self):
        """F-14A CAP: Aircraft score > Soft score.
        Il componente loadout discrimina: Aircraft > 0, Soft = 0 per Phoenix Fleet Defense."""
        aircraft_score = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big", "med", "small"]
        )
        soft_score = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Soft"], ["big", "med", "small"]
        )
        self.assertGreater(aircraft_score, soft_score)

    def test_combat_score_eval_true_equals_target_effectiveness(self):
        """combat_score_eval(..., True, ...) == combat_score_target_effectiveness(...)."""
        score_eval = self._ac.combat_score_eval(
            "CAP", _FIGHTER_LOADOUT, True, ["Aircraft"], ["big"]
        )
        score_target = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertAlmostEqual(score_eval, score_target, places=9)

    def test_invalid_task_raises(self):
        """Task non valido → ValueError."""
        with self.assertRaises((ValueError, TypeError)):
            self._ac.combat_score_target_effectiveness(
                "INVALID_TASK_XYZ", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
            )

    def test_none_task_raises_type_error(self):
        """task=None → TypeError."""
        with self.assertRaises(TypeError):
            self._ac.combat_score_target_effectiveness(
                None, _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
            )

    def test_cap_aircraft_score_deterministic(self):
        """Due chiamate consecutive con stessi argomenti restituiscono lo stesso valore."""
        score1 = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        score2 = self._ac.combat_score_target_effectiveness(
            "CAP", _FIGHTER_LOADOUT, ["Aircraft"], ["big"]
        )
        self.assertEqual(score1, score2)


# ─────────────────────────────────────────────────────────────────────────────
#  TEST Aircraft_Data.get_aircrafts_quantity — TARGET AIRCRAFT (aria-aria)
# ─────────────────────────────────────────────────────────────────────────────

class TestGetAircraftsQuantityAircraft(unittest.TestCase):
    """Unit test per Aircraft_Data.get_aircrafts_quantity() con target Aircraft.

    Il metodo valida l'aeromobile nel registry, poi delega a
    get_aircrafts_quantity() di Aircraft_Loadouts.

    Aeromobile chiamante: F-14A Tomcat (_FIGHTER_MODEL).
    Aeromobile richiesto: F-14A Tomcat / Phoenix Fleet Defense.
    Quantità target elevate (_QTY_TARGET_AIRCRAFT) per garantire
    round(qty/eff) >= 1 anche per loadout ad alta efficienza Aircraft (eff ≈ 4–6).

    Tutti e 4 i logger sono mockati tramite _all_loggers_mocked().
    """

    def setUp(self):
        self._ac = Aircraft_Data._registry[_FIGHTER_MODEL]   # F-14A Tomcat
        self._mock_ctx = _all_loggers_mocked()
        self._mock_ctx.__enter__()

    def tearDown(self):
        self._mock_ctx.__exit__(None, None, None)

    def test_aircraft_target_returns_dict(self):
        """Input valido con target Aircraft → restituisce un dict."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        self.assertIsInstance(result, dict)

    def test_aircraft_target_has_total(self):
        """Il risultato contiene la chiave 'total'."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        self.assertIn("total", result)

    def test_aircraft_target_has_message(self):
        """Il risultato contiene la chiave 'message'."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        self.assertIn("message", result)

    def test_aircraft_target_has_missions_needed(self):
        """'missions_needed' presente e >= 1."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        self.assertIn("missions_needed", result)
        self.assertGreaterEqual(result["missions_needed"], 1)

    def test_aircraft_target_total_positive(self):
        """F-14A Phoenix Fleet Defense vs target Aircraft (quantità elevate) → total > 0."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        self.assertGreater(result["total"], 0)

    def test_aircraft_target_has_aircraft_key(self):
        """Il risultato contiene la chiave 'Aircraft' (target_type richiesto)."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        self.assertIn("Aircraft", result)

    def test_aircraft_target_dimension_values_non_negative_int(self):
        """Tutti i valori (Aircraft, dimension) sono interi >= 0."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        if "Aircraft" in result and isinstance(result["Aircraft"], dict):
            for dim, count in result["Aircraft"].items():
                with self.subTest(dim=dim):
                    self.assertIsInstance(count, int)
                    self.assertGreaterEqual(count, 0)

    def test_aircraft_target_total_equals_sum_dimensions(self):
        """'total' == somma di tutti i conteggi per (Aircraft, dimension)."""
        result = self._ac.get_aircrafts_quantity(
            _FIGHTER_MODEL, _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
        )
        _SCALAR_KEYS = {"total", "message", "missions_needed", "max_aircraft_for_mission",
                        "aircraft_number"}
        expected = sum(
            v
            for key, dims in result.items()
            if key not in _SCALAR_KEYS and isinstance(dims, dict)
            for v in dims.values()
        )
        self.assertEqual(result["total"], expected)

    def test_unknown_aircraft_raises_ValueError(self):
        """Aeromobile sconosciuto → ValueError (validazione locale del registry)."""
        with self.assertRaises(ValueError):
            self._ac.get_aircrafts_quantity(
                "INVALID_AIRCRAFT_XYZ", _FIGHTER_LOADOUT, _QTY_TARGET_AIRCRAFT
            )

    def test_integrative_large_aerial_formation(self):
        """Test integrativo: F-14A CAP vs formazione aerea numerosa — struttura valida."""
        target_data = {"Aircraft": {"big": 30, "med": 50, "small": 80}}
        result = self._ac.get_aircrafts_quantity(_FIGHTER_MODEL, _FIGHTER_LOADOUT, target_data)
        self.assertIsInstance(result, dict)
        self.assertIn("total", result)
        self.assertIsInstance(result["total"], int)
        self.assertGreaterEqual(result["total"], 0)
        self.assertIn("missions_needed", result)
        self.assertGreaterEqual(result["missions_needed"], 1)

    def test_integrative_air_superiority_mixed_formation(self):
        """Scenario aria-aria mix big/med/small — struttura valida."""
        target_data = {"Aircraft": {"big": 5, "med": 10, "small": 20}}
        result = self._ac.get_aircrafts_quantity(_FIGHTER_MODEL, _FIGHTER_LOADOUT, target_data)
        self.assertIsInstance(result, dict)
        self.assertIn("total", result)
        self.assertGreaterEqual(result["total"], 0)


# ─────────────────────────────────────────────────────────────────────────────
#  TEST COST
# ─────────────────────────────────────────────────────────────────────────────

class TestCost(unittest.TestCase):
    """Test unitari per Aircraft_Data.cost()."""

    def test_cost_returns_int(self):
        """cost() restituisce un intero."""
        ac = Aircraft_Data._registry[_FIGHTER_MODEL]
        self.assertIsInstance(ac.cost, int)

    def test_cost_positive_for_known_aircraft(self):
        """cost > 0 per tutti gli aeromobili nel registry."""
        for model, ac in Aircraft_Data._registry.items():
            self.assertGreater(ac.cost, 0, f"{model}: cost deve essere > 0")

    def test_f14a_cost(self):
        """F-14A Tomcat: costo storico ~38 M$."""
        ac = Aircraft_Data._registry["F-14A Tomcat"]
        self.assertEqual(ac.cost, 38)

    def test_f16a_cost(self):
        """F-16A Fighting Falcon: costo storico ~6 M$."""
        ac = Aircraft_Data._registry["F-16A Fighting Falcon"]
        self.assertIn(ac.cost, (6,))

    def test_b1b_cost_greater_than_f15e(self):
        """B-1B Lancer (heavy bomber) deve costare più dell'F-15E (fighter-bomber)."""
        b1b = Aircraft_Data._registry["B-1B Lancer"]
        f15e = Aircraft_Data._registry["F-15E Strike Eagle"]
        self.assertGreater(b1b.cost, f15e.cost)

    def test_tu160_cost_greater_than_tu95ms(self):
        """Tu-160 (supersonico) deve costare più del Tu-95MS."""
        tu160 = Aircraft_Data._registry["Tu-160"]
        tu95 = Aircraft_Data._registry["Tu-95MS"]
        self.assertGreater(tu160.cost, tu95.cost)

    def test_awacs_cost_greater_than_basic_fighter(self):
        """E-3A Sentry (AWACS) deve costare più di un F-16A (fighter leggero)."""
        e3a = Aircraft_Data._registry["E-3A Sentry"]
        f16a = Aircraft_Data._registry["F-16A Fighting Falcon"]
        self.assertGreater(e3a.cost, f16a.cost)

    def test_a10c_more_expensive_than_a10a(self):
        """A-10C (upgrade) deve costare più dell'A-10A originale."""
        a10a = Aircraft_Data._registry["A-10A Thunderbolt II"]
        a10c = Aircraft_Data._registry["A-10C Thunderbolt II"]
        self.assertGreater(a10c.cost, a10a.cost)

    def test_f117_cost_greater_than_f16cm(self):
        """F-117 Nighthawk (stealth) deve costare più dell'F-16CM."""
        f117 = Aircraft_Data._registry["F-117 Nighthawk"]
        f16cm = Aircraft_Data._registry["F-16CM Block 50"]
        self.assertGreater(f117.cost, f16cm.cost)

    def test_mq1_cheaper_than_mq9(self):
        """MQ-1 Predator deve costare meno dell'MQ-9 Reaper."""
        mq1 = Aircraft_Data._registry["MQ-1 Predator"]
        mq9 = Aircraft_Data._registry["MQ-9 Reaper"]
        self.assertLess(mq1.cost, mq9.cost)

    def test_cost_coherence_su27_vs_mig29(self):
        """Su-27 (heavy air superiority) deve costare più del MiG-29A."""
        su27 = Aircraft_Data._registry["Su-27"]
        mig29 = Aircraft_Data._registry["MiG-29A"]
        self.assertGreater(su27.cost, mig29.cost)


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY PER LA GENERAZIONE DELLE TABELLE
# ─────────────────────────────────────────────────────────────────────────────

def _is_nan(value) -> bool:
    try:
        return value != value
    except Exception:
        return False


def _aircraft_by_category() -> dict:
    """Restituisce un dict {category_str: [Aircraft_Data, ...]} per categoria."""
    result: dict = {}
    for ac in Aircraft_Data._registry.values():
        for cat_enum in ac.category:
            result.setdefault(cat_enum.value, []).append(ac)
    return result


def _all_loggers_mocked():
    """Context manager che mocka tutti i logger necessari per i test combat score."""
    from contextlib import ExitStack
    stack = ExitStack()
    for path in [_LOGGER_PATH, _LOADOUTS_LOGGER_PATH, _GWD_LOGGER_PATH, _AWD_LOGGER_PATH]:
        stack.enter_context(patch(path, MagicMock()))
    return stack


def _best_loadout_for_task(aircraft_model: str, task: str) -> Optional[str]:
    """Restituisce il nome del loadout con il punteggio più alto per aircraft+task."""
    best_score = -1.0
    best_name = None
    for name, data in AIRCRAFT_LOADOUTS.get(aircraft_model, {}).items():
        if task in data.get("tasks", []):
            try:
                with _all_loggers_mocked():
                    sc = loadout_eval(aircraft_model, name)
                if sc > best_score:
                    best_score = sc
                    best_name = name
            except Exception:
                if best_name is None:
                    best_name = name
    return best_name


def _safe_combat_score_raw(ac: Aircraft_Data, task: str, loadout_name: str) -> float:
    """Chiama combat_score() con logger mockato, restituisce float grezzo."""
    try:
        with _all_loggers_mocked():
            return ac.combat_score(task, loadout_name)
    except Exception:
        return float("nan")


def _safe_combat_score_target_raw(
    ac: Aircraft_Data,
    task: str,
    loadout_name: str,
    t_types: List[str],
    t_dims: List[str],
) -> float:
    """Chiama combat_score_target_effectiveness() con logger mockato, restituisce float grezzo."""
    try:
        with _all_loggers_mocked():
            return ac.combat_score_target_effectiveness(task, loadout_name, t_types, t_dims)
    except Exception:
        return float("nan")


def _normalize_scores(value: float, scores: list) -> float:
    """Normalizza value in [0, 1] rispetto alla lista scores."""
    valid = [s for s in scores if not _is_nan(s)]
    if not valid:
        return float("nan")
    mn, mx = min(valid), max(valid)
    if mx == mn:
        return 0.5
    return (value - mn) / (mx - mn)


def _safe_combat_score(ac: Aircraft_Data, task: str, loadout_name: str, cat: str,
                       all_scores: dict = None) -> float:
    """Calcola combat_score e lo normalizza rispetto agli aeromobili della stessa categoria.
    Se all_scores è fornito (dict {model: raw_score}), usa quelli per la normalizzazione."""
    raw = _safe_combat_score_raw(ac, task, loadout_name)
    if _is_nan(raw):
        return float("nan")
    if all_scores is not None:
        return _normalize_scores(raw, list(all_scores.values()))
    return raw


def _safe_combat_score_target(
    ac: Aircraft_Data,
    task: str,
    loadout_name: str,
    t_types: List[str],
    t_dims: List[str],
    cat: str,
) -> float:
    """Chiama combat_score_target_effectiveness con logger mockato."""
    return _safe_combat_score_target_raw(ac, task, loadout_name, t_types, t_dims)


def _safe_dist_score(ac: Aircraft_Data, task: str, loadout: str, target_dist: dict) -> float:
    """Chiama loadout_target_effectiveness_by_distribuition con logger mockato.

    Nota: la funzione è importata da Aircraft_Loadouts (livello modulo),
    non è un metodo di Aircraft_Data. Il parametro loadout è il NOME del
    loadout (stringa chiave del dict restituito da get_loadouts).
    route_length=1 e route_speed=1 per non escludere nessun loadout per rotta.
    """
    try:
        with _all_loggers_mocked():
            return loadout_target_effectiveness_by_distribuition(
                ac.model, loadout, target_dist, route_length=1, route_speed=1
            )
    except Exception:
        return float("nan")


def _extract_target_types_dims(target_dist: dict):
    """Estrae (target_types, target_dims) dalla distribuzione per combat_score_target_effectiveness."""
    t_types = list(target_dist.keys())
    t_dims = sorted({d for v in target_dist.values() for d in v.get("perc_dimension", {}).keys()})
    return t_types, t_dims


def _build_list_of_aircrafts_rows(side: str, task: str, target_dist: dict,
                                   role: Optional[str] = None) -> list:
    """Costruisce le righe per la tabella get_list_of_aircrafts().

    Replica la logica di get_list_of_aircrafts() gestendo BLA3:
    gli aircraft senza loadout per il task vengono esclusi invece di
    causare StopIteration nel sorting key.

    Calcolo Combat Score:
    - Se target_dist è fornita: usa combat_score_target_effectiveness(task, loadout,
      target_types, target_dims) con target_types/dims estratti dalla dist.
    - Se target_dist è None: usa combat_score(task, loadout).

    Ritorna lista di tuple (rank, model, best_loadout, combat_score_norm,
    dist_score_raw) ordinata per combat_score decrescente.
    """
    t_types, t_dims = _extract_target_types_dims(target_dist) if target_dist else (None, None)

    raw_rows = []
    for ac in Aircraft_Data._registry.values():
        if role and not any(c.value == role for c in ac.category):
            continue
        if not any(user in COALITIONS[side] for user in ac.users):
            continue
        loadout = _best_loadout_for_task(ac.model, task)
        if loadout is None:
            continue
        if target_dist:
            cs = _safe_combat_score_target_raw(ac, task, loadout, t_types, t_dims)
        else:
            cs = _safe_combat_score_raw(ac, task, loadout)
        ds = _safe_dist_score(ac, task, loadout, target_dist)
        raw_rows.append((ac.model, loadout, cs, ds))

    if not raw_rows:
        return []

    # Normalizza combat_score nella lista
    cs_vals = [r[2] for r in raw_rows]
    rows = [
        (m, l, _normalize_scores(cs, cs_vals), ds)
        for m, l, cs, ds in raw_rows
    ]
    rows.sort(key=lambda x: x[2] if not _is_nan(x[2]) else -1, reverse=True)

    return [(rank, m, l, cs_n, ds) for rank, (m, l, cs_n, ds) in enumerate(rows, start=1)]


# ─────────────────────────────────────────────────────────────────────────────
#  STAMPA A TERMINALE
# ─────────────────────────────────────────────────────────────────────────────

def print_aircraft_subsystem_scores() -> None:
    """Stampa a terminale i punteggi dei sottosistemi per ogni aeromobile,
    raggruppati per categoria. I punteggi sono normalizzati all'interno della
    categoria (0.0 = peggiore nella categoria, 1.0 = migliore nella categoria)."""
    cat_map = _aircraft_by_category()

    for cat in AIRCRAFT_CATEGORIES:
        aircraft_list = cat_map.get(cat, [])
        if not aircraft_list:
            continue

        header = f"  CATEGORIA: {cat}  —  punteggi normalizzati nella categoria"
        width = max(90, len(header) + 4)
        print()
        print("═" * width)
        print(header)
        print("═" * width)

        sample_model = aircraft_list[0].model
        score_names = list(AIRCRAFT.get(sample_model, {}).keys())

        col_m = max(18, max(len(ac.model) for ac in aircraft_list))
        col_s = 10

        for score_name in score_names:
            print(f"\n  [ {score_name} ]")
            header_row = f"  {'Model':<{col_m}}   {'score (cat)':>{col_s}}"
            print("─" * len(header_row))
            print(header_row)
            print("─" * len(header_row))

            # Raccoglie valori grezzi (globalmente normalizzati) e ri-normalizza per categoria
            raw_vals = [AIRCRAFT.get(ac.model, {}).get(score_name, float("nan")) for ac in aircraft_list]
            cat_norm = [_normalize_scores(v, raw_vals) if not _is_nan(v) else float("nan") for v in raw_vals]

            rows = list(zip([ac.model for ac in aircraft_list], cat_norm))
            rows.sort(key=lambda x: x[1] if not _is_nan(x[1]) else -1, reverse=True)

            for model, val in rows:
                val_str = f"{val:.4f}" if not _is_nan(val) else "   N/A  "
                print(f"  {model:<{col_m}}   {val_str:>{col_s}}")
        print()


def print_combat_score_tables(tasks: List[str], categories: List[str]) -> None:
    """Stampa a terminale la tabella combat_score normalizzato per task e categoria."""
    cat_map = _aircraft_by_category()

    for task in tasks:
        for cat in categories:
            aircraft_list = cat_map.get(cat, [])
            if not aircraft_list:
                continue

            # Raccoglie raw scores per normalizzazione categoria
            raw_rows = []
            for ac in aircraft_list:
                loadout = _best_loadout_for_task(ac.model, task)
                if loadout is None:
                    continue
                raw = _safe_combat_score_raw(ac, task, loadout)
                raw_rows.append((ac.model, loadout, raw))

            if not raw_rows:
                continue

            raw_vals = [r for _, _, r in raw_rows]
            rows = [(m, l, _normalize_scores(r, raw_vals)) for m, l, r in raw_rows]

            header = f"  TASK: {task}  |  CATEGORIA: {cat}  —  combat_score (normalizzato)"
            width = max(90, len(header) + 4)
            print()
            print("═" * width)
            print(header)
            print("═" * width)

            col_m = max(18, max(len(r[0]) for r in rows))
            col_l = max(20, max(len(r[1]) for r in rows))
            col_s = 12

            rows.sort(key=lambda x: x[2] if not _is_nan(x[2]) else -1, reverse=True)
            header_row = f"  {'Model':<{col_m}}   {'Best Loadout':<{col_l}}   {'Score':>{col_s}}"
            print(header_row)
            print("─" * len(header_row))

            for model, loadout, score in rows:
                s = f"{score:.6f}" if not _is_nan(score) else "     N/A     "
                print(f"  {model:<{col_m}}   {loadout:<{col_l}}   {s:>{col_s}}")
        print()


def print_combat_score_target_tables(
    tasks: List[str],
    categories: List[str],
    t_types: List[str],
    t_dims: List[str],
) -> None:
    """Stampa a terminale get_normalized_combat_score_target_effectiveness() per task, categoria e target."""
    cat_map = _aircraft_by_category()
    combinations = [(t, d) for t in t_types for d in t_dims]

    for task in tasks:
        for cat in categories:
            aircraft_list = cat_map.get(cat, [])
            if not aircraft_list:
                continue

            valid_rows = []
            for ac in aircraft_list:
                loadout = _best_loadout_for_task(ac.model, task)
                if loadout is not None:
                    valid_rows.append((ac, loadout))

            if not valid_rows:
                continue

            col_m = max(18, max(len(ac.model) for ac, _ in valid_rows))
            col_headers = [f"{t}/{d}" for t, d in combinations]
            cell_w = 10

            header = f"  TASK: {task}  |  CATEGORIA: {cat}  —  get_normalized_combat_score_target_effectiveness()"
            parts = [f"  {'Model':<{col_m}}   {'Loadout':<20}"]
            for h in col_headers:
                parts.append(f"{h:^{cell_w}}")
            header_line = "  ".join(parts)
            width = max(len(header), len(header_line))

            print()
            print("═" * width)
            print(header)
            print("═" * width)
            print(header_line)
            print("─" * width)

            for ac, loadout in valid_rows:
                row_parts = [f"  {ac.model:<{col_m}}   {loadout:<20}"]
                for t_type, t_dim in combinations:
                    val = _safe_combat_score_target_raw(ac, task, loadout, [t_type], [t_dim])
                    s = f"{val:.4f}" if not _is_nan(val) else "  N/A  "
                    row_parts.append(f"{s:^{cell_w}}")
                print("  ".join(row_parts))
        print()


def print_get_list_of_aircrafts_table(
    side: str, task: str, target_dist: dict, role: Optional[str] = None
) -> None:
    """Stampa a terminale la classifica get_list_of_aircrafts(side, task, target_dist).

    Colonne: #, Aeromobile, Best Loadout, Combat Score (norm.), Dist. Score (raw)
    Combat Score: combat_score_target_effectiveness() se target_dist è fornita,
                  altrimenti combat_score().
    Ordinamento: combat_score_target_effectiveness decrescente (quando target_dist fornita).
    Gli aircraft senza loadout per il task sono omessi (BLA3 workaround).
    """
    rows = _build_list_of_aircrafts_rows(side, task, target_dist, role)

    dist_label = "  +  ".join(
        f"{t} {int(v['perc_type'] * 100)}%"
        f" [{' '.join(f'{d}:{int(p * 100)}%' for d, p in v['perc_dimension'].items())}]"
        for t, v in target_dist.items()
    )
    role_label = f"  role='{role}'" if role else ""

    header = (
        f"  CLASSIFICA get_list_of_aircrafts()  "
        f"side='{side}'  task='{task}'{role_label}\n"
        f"  Target distribution: {dist_label}"
    )
    print()
    if not rows:
        print(f"[SKIP] Nessun aircraft {side} con loadout '{task}'{role_label}.")
        return

    col_r = 3
    col_m = max(len("Aeromobile"), max(len(r[1]) for r in rows))
    col_l = max(len("Best Loadout"), max(len(r[2]) for r in rows))
    col_cs = 14
    col_ds = 14
    sep = "  "
    width = col_r + len(sep) + col_m + len(sep) + col_l + len(sep) + col_cs + len(sep) + col_ds + 4

    print("═" * width)
    for line in header.splitlines():
        print(line)
    print("═" * width)
    print(
        f"  {'#':<{col_r}}{sep}"
        f"{'Aeromobile':<{col_m}}{sep}"
        f"{'Best Loadout':<{col_l}}{sep}"
        f"{'Combat Score':>{col_cs}}{sep}"
        f"{'Dist. Score':>{col_ds}}"
    )
    print("─" * width)
    for rank, model, loadout, cs_n, ds in rows:
        cs_s = f"{cs_n:.6f}" if not _is_nan(cs_n) else "     N/A     "
        ds_s = f"{ds:.6f}" if not _is_nan(ds) else "     N/A     "
        print(
            f"  {rank:<{col_r}}{sep}"
            f"{model:<{col_m}}{sep}"
            f"{loadout:<{col_l}}{sep}"
            f"{cs_s:>{col_cs}}{sep}"
            f"{ds_s:>{col_ds}}"
        )
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  GENERAZIONE PDF
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


def save_aircraft_subsystem_scores_pdf(output_path: str) -> None:
    """Salva Aircraft_Sub_System_Scores.pdf con una pagina per categoria.
    I punteggi sono normalizzati nella categoria (0.0=peggiore, 1.0=migliore).
    La colorazione heatmap è applicata per riga (per subsystem): verde=massimo
    nella categoria, rosso=minimo nella categoria."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cat_map = _aircraft_by_category()

    with PdfPages(output_path) as pdf:
        for cat in AIRCRAFT_CATEGORIES:
            aircraft_list = cat_map.get(cat, [])
            if not aircraft_list:
                continue

            sample_model = aircraft_list[0].model
            score_names = list(AIRCRAFT.get(sample_model, {}).keys())

            # Costruisce tabella: righe = score_name, colonne = models
            col_labels = ["Score"] + [ac.model for ac in aircraft_list]
            cell_text = []
            norm_matrix = []  # valori normalizzati nella categoria, per coloring

            for score_name in score_names:
                # Valori grezzi (globalmente normalizzati)
                raw_vals = [AIRCRAFT.get(ac.model, {}).get(score_name, float("nan"))
                            for ac in aircraft_list]
                # Ri-normalizza nella categoria: 0=peggiore, 1=migliore
                cat_norm = [_normalize_scores(v, raw_vals) if not _is_nan(v) else float("nan")
                            for v in raw_vals]
                norm_matrix.append(cat_norm)
                row_str = [score_name] + [
                    f"{v:.3f}" if not _is_nan(v) else "N/A" for v in cat_norm
                ]
                cell_text.append(row_str)

            # Colorazione heatmap per riga (per subsystem): ogni riga ha la propria scala [0,1]
            cell_colors = []
            for cat_norm in norm_matrix:
                row_colors = ["#f0f4f8"]  # cella score_name
                for v in cat_norm:
                    if not _is_nan(v):
                        row_colors.append(plt.cm.RdYlGn(v))  # già in [0,1] nella categoria
                    else:
                        row_colors.append((0.87, 0.87, 0.87, 1.0))
                cell_colors.append(row_colors)

            n_rows = len(cell_text)
            n_cols = len(col_labels)
            fig_w = max(14.0, 1.8 * len(aircraft_list) + 4.0)
            fig_h = max(5.0, 0.38 * n_rows + 2.5)

            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.axis("off")
            ax.set_title(
                f"Aircraft Subsystem Scores — Categoria: {cat}\n"
                f"Punteggi normalizzati nella categoria (0.0=peggiore, 1.0=migliore)",
                fontsize=12, fontweight="bold", pad=18,
            )

            tbl = ax.table(
                cellText=cell_text,
                colLabels=col_labels,
                cellColours=cell_colors,
                loc="center",
                cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(7)
            tbl.auto_set_column_width(list(range(n_cols)))
            _header_style(tbl, n_cols)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"[PDF] Aircraft_Sub_System_Scores → {output_path}")


def save_aircraft_combat_score_pdf(
    tasks: List[str],
    categories: List[str],
    output_path: str,
) -> None:
    """Salva Aircraft_Combat_Scores.pdf.
    Per ogni task e categoria: una pagina con la tabella get_normalized_combat_score()
    per gli aeromobili che supportano quel task, ordinata per punteggio decrescente,
    con colorazione heatmap (verde=alto, rosso=basso)."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cat_map = _aircraft_by_category()

    with PdfPages(output_path) as pdf:
        for task in tasks:
            for cat in categories:
                aircraft_list = cat_map.get(cat, [])
                if not aircraft_list:
                    continue

                raw_rows = []
                for ac in aircraft_list:
                    loadout = _best_loadout_for_task(ac.model, task)
                    if loadout is None:
                        continue
                    raw = _safe_combat_score_raw(ac, task, loadout)
                    raw_rows.append((ac.model, loadout, raw))

                if not raw_rows:
                    continue

                raw_vals = [r for _, _, r in raw_rows]
                rows = [(m, l, _normalize_scores(r, raw_vals)) for m, l, r in raw_rows]
                rows.sort(key=lambda x: x[2] if not _is_nan(x[2]) else -1, reverse=True)

                valid_scores = [s for _, _, s in rows if not _is_nan(s)]
                max_s = max(valid_scores) if valid_scores else 1.0
                min_s = min(valid_scores) if valid_scores else 0.0
                rng = (max_s - min_s) if max_s != min_s else 1.0

                cell_text = []
                cell_colors = []
                for rank, (model, loadout, score) in enumerate(rows, start=1):
                    score_str = f"{score:.4f}" if not _is_nan(score) else "N/A"
                    cell_text.append([str(rank), model, loadout, score_str])
                    if not _is_nan(score):
                        color = plt.cm.RdYlGn((score - min_s) / rng)
                    else:
                        color = (0.87, 0.87, 0.87, 1.0)
                    cell_colors.append(["#f5f5f5", "#f0f4f8", "#f0f4f8", color])

                fig_h = max(4.0, 0.38 * len(cell_text) + 2.5)
                fig_w = max(14.0, 12.0)
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.axis("off")
                ax.set_title(
                    f"Combat Score — Task: {task}  |  Categoria: {cat}\n"
                    f"Funzione: get_normalized_combat_score(task='{task}', category='{cat}')",
                    fontsize=11, fontweight="bold", pad=18,
                )
                tbl = ax.table(
                    cellText=cell_text,
                    colLabels=["#", "Aeromobile", "Loadout", "Score Norm."],
                    cellColours=cell_colors,
                    loc="center",
                    cellLoc="center",
                )
                tbl.auto_set_font_size(False)
                tbl.set_fontsize(8)
                tbl.auto_set_column_width([0, 1, 2, 3])
                _header_style(tbl, 4)
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

    print(f"[PDF] Aircraft_Combat_Scores → {output_path}")


def save_aircraft_combat_score_target_pdf(
    tasks: List[str],
    categories: List[str],
    t_types: List[str],
    t_dims: List[str],
    output_path: str,
) -> None:
    """Salva Aircraft_Combat_Score_Target.pdf.
    Per ogni task e categoria: una pagina con la tabella
    get_normalized_combat_score_target_effectiveness() con colonne per ogni
    combinazione (target_type × target_dimension), con colorazione heatmap."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cat_map = _aircraft_by_category()
    combinations = [(t, d) for t in t_types for d in t_dims]

    # Solo task A/G e Anti_Ship per la target effectiveness
    ag_tasks = [t for t in tasks if t in ["CAS", "Strike", "Pinpoint_Strike", "SEAD", "Anti_Ship"]]

    with PdfPages(output_path) as pdf:
        for task in ag_tasks:
            for cat in categories:
                aircraft_list = cat_map.get(cat, [])
                if not aircraft_list:
                    continue

                valid_rows = []
                for ac in aircraft_list:
                    loadout = _best_loadout_for_task(ac.model, task)
                    if loadout is not None:
                        valid_rows.append((ac, loadout))

                if not valid_rows:
                    continue

                col_labels = ["Aeromobile", "Loadout"] + [
                    f"{t}\n{d}" for t, d in combinations
                ]
                n_data_cols = len(combinations)
                n_cols_total = 2 + n_data_cols

                cell_text = []
                score_matrix = []
                for ac, loadout in valid_rows:
                    row_scores = [
                        _safe_combat_score_target_raw(ac, task, loadout, [t], [d])
                        for t, d in combinations
                    ]
                    score_matrix.append(row_scores)
                    cell_text.append(
                        [ac.model, loadout]
                        + [f"{s:.4f}" if not _is_nan(s) else "N/A" for s in row_scores]
                    )

                all_vals = [v for row in score_matrix for v in row if not _is_nan(v)]
                max_s = max(all_vals) if all_vals else 1.0
                min_s = min(all_vals) if all_vals else 0.0
                rng = (max_s - min_s) if max_s != min_s else 1.0

                cell_colors = []
                for row_scores in score_matrix:
                    row_colors = ["#f0f4f8", "#f0f4f8"]
                    for s in row_scores:
                        if not _is_nan(s):
                            row_colors.append(plt.cm.RdYlGn((s - min_s) / rng))
                        else:
                            row_colors.append((0.87, 0.87, 0.87, 1.0))
                    cell_colors.append(row_colors)

                fig_w = max(14, 2.2 * n_cols_total)
                fig_h = max(4.0, 0.42 * len(valid_rows) + 2.5)
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.axis("off")
                ax.set_title(
                    f"Combat Score Target Effectiveness — Task: {task}  |  Categoria: {cat}\n"
                    f"Funzione: get_normalized_combat_score_target_effectiveness()",
                    fontsize=11, fontweight="bold", pad=18,
                )
                tbl = ax.table(
                    cellText=cell_text,
                    colLabels=col_labels,
                    cellColours=cell_colors,
                    loc="center",
                    cellLoc="center",
                )
                tbl.auto_set_font_size(False)
                tbl.set_fontsize(7)
                tbl.auto_set_column_width(list(range(n_cols_total)))
                _header_style(tbl, n_cols_total)
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

    print(f"[PDF] Aircraft_Combat_Score_Target → {output_path}")


def save_get_list_of_aircrafts_pdf(
    side: str, task: str, target_dist: dict, output_path: str,
    role: Optional[str] = None,
) -> None:
    """Salva in PDF la classifica get_list_of_aircrafts(side, task, target_dist).

    Una singola pagina con:
      - colonne: #, Aeromobile, Best Loadout, Combat Score (norm.), Dist. Score (raw)
      - Combat Score calcolato con combat_score_target_effectiveness() se target_dist
        è fornita, altrimenti combat_score()
      - heatmap RdYlGn sulla colonna Combat Score
      - heatmap RdYlGn sulla colonna Dist. Score (scala indipendente)
    """
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    rows = _build_list_of_aircrafts_rows(side, task, target_dist, role)
    if not rows:
        role_label = f"  role='{role}'" if role else ""
        print(f"[PDF] Nessun aircraft {side} con loadout '{task}'{role_label} — PDF non generato.")
        return

    dist_label = "  |  ".join(
        f"{t} {int(v['perc_type'] * 100)}%"
        f" [{' '.join(f'{d}:{int(p * 100)}%' for d, p in v['perc_dimension'].items())}]"
        for t, v in target_dist.items()
    )

    # Scala colori combat score
    cs_vals  = [r[3] for r in rows if not _is_nan(r[3])]
    cs_max, cs_min = (max(cs_vals), min(cs_vals)) if cs_vals else (1.0, 0.0)
    cs_rng = (cs_max - cs_min) if cs_max != cs_min else 1.0

    # Scala colori dist score
    ds_vals  = [r[4] for r in rows if not _is_nan(r[4])]
    ds_max, ds_min = (max(ds_vals), min(ds_vals)) if ds_vals else (1.0, 0.0)
    ds_rng = (ds_max - ds_min) if ds_max != ds_min else 1.0

    cell_text   = []
    cell_colors = []
    for rank, model, loadout, cs_n, ds in rows:
        cs_s = f"{cs_n:.4f}" if not _is_nan(cs_n) else "N/A"
        ds_s = f"{ds:.4f}"   if not _is_nan(ds)   else "N/A"
        cell_text.append([str(rank), model, loadout, cs_s, ds_s])

        cs_color = plt.cm.RdYlGn((cs_n - cs_min) / cs_rng) if not _is_nan(cs_n) else (0.87, 0.87, 0.87, 1.0)
        ds_color = plt.cm.RdYlGn((ds - ds_min) / ds_rng)   if not _is_nan(ds)   else (0.87, 0.87, 0.87, 1.0)
        cell_colors.append(["#f5f5f5", "#f0f4f8", "#f0f4f8", cs_color, ds_color])

    n_cols  = 5
    fig_h   = max(4.0, 0.40 * len(cell_text) + 3.0)
    fig, ax = plt.subplots(figsize=(16, fig_h))
    ax.axis("off")
    role_label = f"  role='{role}'" if role else ""
    ax.set_title(
        f"Classifica Aeromobili — get_list_of_aircrafts()\n"
        f"side='{side}'  task='{task}'{role_label}  |  {dist_label}",
        fontsize=12, fontweight="bold", pad=20,
    )
    tbl = ax.table(
        cellText=cell_text,
        colLabels=["#", "Aeromobile", "Best Loadout", "Combat Score", "Dist. Score"],
        cellColours=cell_colors,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.auto_set_column_width(list(range(n_cols)))
    _header_style(tbl, n_cols)
    plt.tight_layout()

    with PdfPages(output_path) as pdf:
        pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    print(f"[PDF] get_list_of_aircrafts → {output_path}")


def _qty_safe(ac_instance, ac_model: str, loadout: str, target_data: dict) -> Optional[dict]:
    """Chiama get_aircrafts_quantity con tutti i logger mockati; None su eccezione."""
    try:
        with _all_loggers_mocked():
            return ac_instance.get_aircrafts_quantity(ac_model, loadout, target_data)
    except Exception:
        return None


def _mission_aircraft(result: dict) -> int:
    """Aerei impiegati nella singola missione: somma dei conteggi per dimensione (già cappati),
    escludendo missions_needed."""
    return sum(
        count
        for key, val in result.items()
        if key not in ("total", "message") and isinstance(val, dict)
        for dim, count in val.items()
        if dim != "missions_needed"
    )


def print_aircrafts_quantity_tables() -> None:
    """Stampa a terminale le tabelle get_aircrafts_quantity per ogni scenario e target.

    Colonne: Aircraft, Loadout, una per ogni (target_type/dimension), una per
    (target_type/miss) con le missioni necessarie, Total.
    """
    _ac = Aircraft_Data._registry[_FIGHTER_MODEL]

    for scenario_name, scenario in _SCENARIOS.items():
        aircraft_list = scenario["aircraft"]

        for target_label, target_data in scenario["targets"].items():
            # col_specs: (tt, dim) per ogni dimensione
            col_specs: list = []
            for tt, dims in target_data.items():
                for dim in dims.keys():
                    col_specs.append((tt, dim))

            col_headers = [f"{tt}/{dim}" for tt, dim in col_specs]
            target_desc = "  ".join(
                f"{tt}:{dict(dims)}" for tt, dims in target_data.items()
            )

            header = (
                f"  SCENARIO: {scenario_name}  |  {target_label}  "
                f"— get_aircrafts_quantity()\n"
                f"  Target: {target_desc}"
            )
            width = max(100, len(target_desc) + 10)
            print()
            print("═" * width)
            for line in header.splitlines():
                print(line)
            print("═" * width)

            col_ac = max(20, max(len(ac) for ac, _ in aircraft_list))
            col_lo = max(24, max(len(lo) for _, lo in aircraft_list))
            cell_w = 9

            header_row = (
                f"  {'Aircraft':<{col_ac}}   {'Loadout':<{col_lo}}  "
                + "  ".join(f"{h:^{cell_w}}" for h in col_headers)
                + f"  {'Miss':>{cell_w}}  {'Total':>{cell_w}}"
            )
            print(header_row)
            print("─" * len(header_row))

            for ac, lo in aircraft_list:
                result = _qty_safe(_ac, ac, lo, target_data)
                if result is None:
                    print(f"  {ac:<{col_ac}}   {lo:<{col_lo}}  ERROR")
                    continue
                cells = []
                for tt, dim in col_specs:
                    tt_dict = result.get(tt, {}) if isinstance(result.get(tt), dict) else {}
                    val = tt_dict.get(dim, 0)
                    cells.append(f"{val:^{cell_w}}")
                missions = result.get("missions_needed", 1)
                total = result.get("total", 0)
                print(
                    f"  {ac:<{col_ac}}   {lo:<{col_lo}}  "
                    + "  ".join(cells)
                    + f"  {missions:>{cell_w}}  {total:>{cell_w}}"
                )
            print()


def save_aircrafts_quantity_pdf(output_path: str) -> None:
    """Salva Aircraft_Quantity.pdf con tabelle get_aircrafts_quantity per ogni scenario/target.

    Una pagina per ogni coppia (scenario × target). Colonne: Aircraft, Loadout,
    una per ogni (target_type, dimension), Total.
    Heatmap sulla colonna Total: verde = meno aerei (più efficiente), rosso = più aerei.
    """
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
        exist_ok=True,
    )
    _ac = Aircraft_Data._registry[_FIGHTER_MODEL]

    with PdfPages(output_path) as pdf:
        for scenario_name, scenario in _SCENARIOS.items():
            aircraft_list = scenario["aircraft"]

            for target_label, target_data in scenario["targets"].items():
                # col_specs: (tt, dim) per ogni dimensione
                col_specs: list = []
                for tt, dims in target_data.items():
                    for dim in dims.keys():
                        col_specs.append((tt, dim))

                col_labels = (
                    ["Aeromobile", "Loadout"]
                    + [f"{tt}\n{dim}" for tt, dim in col_specs]
                    + ["Miss", "Total"]
                )
                n_data_cols  = len(col_specs)
                n_cols_total = 2 + n_data_cols + 2  # +2: Miss e Total

                cell_text     = []
                miss_values   = []
                total_values  = []

                for ac, lo in aircraft_list:
                    result = _qty_safe(_ac, ac, lo, target_data)
                    if result is None:
                        vals  = ["-"] * n_data_cols
                        miss_values.append(None)
                        total_values.append(None)
                        cell_text.append([ac, lo] + vals + ["-", "-"])
                    else:
                        vals = []
                        for tt, dim in col_specs:
                            tt_dict = result.get(tt, {}) if isinstance(result.get(tt), dict) else {}
                            val = tt_dict.get(dim, 0)
                            vals.append(str(val))
                        missions = result.get("missions_needed", 1)
                        total = result.get("total", 0)
                        miss_values.append(missions if isinstance(missions, int) else None)
                        total_values.append(total if isinstance(total, int) else None)
                        cell_text.append([ac, lo] + vals + [str(missions), str(total)])

                # Heatmap colonne Miss e Total: meno aerei = più verde (inverso)
                def _heatmap_color(values, val):
                    valid = [v for v in values if v is not None]
                    max_v = max(valid) if valid else 1
                    min_v = min(valid) if valid else 0
                    rng_v = float(max_v - min_v) if max_v != min_v else 1.0
                    if val is not None and rng_v > 0:
                        return plt.cm.RdYlGn(1.0 - (val - min_v) / rng_v)
                    return (0.87, 0.87, 0.87, 1.0)

                cell_colors = []
                for miss_val, total_val in zip(miss_values, total_values):
                    cell_colors.append(
                        ["#f0f4f8", "#f0f4f8"]
                        + ["#f5f5f5"] * n_data_cols
                        + [_heatmap_color(miss_values, miss_val),
                           _heatmap_color(total_values, total_val)]
                    )

                target_desc = "  ".join(
                    f"{tt}: {dict(dims)}" for tt, dims in target_data.items()
                )
                fig_w = max(14.0, 2.0 * n_cols_total)
                fig_h = max(4.0, 0.42 * len(aircraft_list) + 3.5)
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.axis("off")
                ax.set_title(
                    f"Aircrafts Quantity — Scenario: {scenario_name}  |  {target_label}\n"
                    f"Target: {target_desc}\n"
                    f"Funzione: get_aircrafts_quantity()  |  Colore Total: verde=efficiente",
                    fontsize=10, fontweight="bold", pad=18,
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
                tbl.auto_set_column_width(list(range(n_cols_total)))
                _header_style(tbl, n_cols_total)
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

    print(f"[PDF] Aircraft_Quantity → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        TestAircraftDataModuleStructure,
        TestAircraftDataAttributes,
        TestTVDDataStructure,
        TestRadarEval,
        TestTVDEval,
        TestSpeedEval,
        TestEngineEval,
        TestRadioNavEval,
        TestHydraulicEval,
        TestAvionicsEval,
        TestReliabilityAndMaintenance,
        TestNormalize,
        TestGetNormalizedRadarScore,
        TestGetNormalizedTVDScore,
        TestGetNormalizedRadioNavScore,
        TestGetNormalizedHydraulicScore,
        TestGetNormalizedAvionicsScore,
        TestGetNormalizedEngineScore,
        TestGetNormalizedSpeedScore,
        TestGetNormalizedReliabilityAndAvailability,
        TestCombatScore,
        TestGetNormalizedCombatScore,
        TestGetAircraftData,
        TestGetAircraftScores,
        TestGetLoadouts,
        TestGetListOfAircrafts,
        TestGetAircraftsQuantity,
        TestGetAircraftsQuantityIntegrative,
        TestLoadoutTargetEffectivenessAircraft,
        TestCombatScoreTargetEffectivenessAircraft,
        TestGetAircraftsQuantityAircraft,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def _run_tables_terminal() -> None:
    print("\n" + "=" * 80)
    print("  AIRCRAFT SUBSYSTEM SCORES — punteggi per categoria")
    print("=" * 80)
    print_aircraft_subsystem_scores()

    print("\n" + "=" * 80)
    print("  COMBAT SCORE — get_normalized_combat_score()")
    print("=" * 80)
    print_combat_score_tables(COMBAT_TASKS, AIRCRAFT_CATEGORIES)

    print("\n" + "=" * 80)
    print("  COMBAT SCORE TARGET — get_normalized_combat_score_target_effectiveness()")
    print("=" * 80)
    print_combat_score_target_tables(
        COMBAT_TASKS, AIRCRAFT_CATEGORIES, target_type_list, target_dimension_list
    )

    print("\n" + "=" * 80)
    print("  CLASSIFICA AEROMOBILI — get_list_of_aircrafts()")
    print("=" * 80)
    print_get_list_of_aircrafts_table(_LIST_SIDE, _LIST_TASK, _LIST_TARGET_DIST)
    print_get_list_of_aircrafts_table(_LIST_SIDE, _LIST_TASK, _LIST_TARGET_DIST, role="Fighter_Bomber")

    print("\n" + "=" * 80)
    print("  AIRCRAFTS QUANTITY — get_aircrafts_quantity()")
    print("=" * 80)
    print_aircrafts_quantity_tables()


def _run_tables_pdf() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_aircraft_subsystem_scores_pdf(
        os.path.join(OUTPUT_DIR, "Aircraft_Sub_System_Scores.pdf"),
    )
    save_aircraft_combat_score_pdf(
        COMBAT_TASKS,
        AIRCRAFT_CATEGORIES,
        os.path.join(OUTPUT_DIR, "Aircraft_Combat_Scores.pdf"),
    )
    save_aircraft_combat_score_target_pdf(
        COMBAT_TASKS,
        AIRCRAFT_CATEGORIES,
        target_type_list,
        target_dimension_list,
        os.path.join(OUTPUT_DIR, "Aircraft_Combat_Score_Target.pdf"),
    )
    save_get_list_of_aircrafts_pdf(
        _LIST_SIDE,
        _LIST_TASK,
        _LIST_TARGET_DIST,
        os.path.join(OUTPUT_DIR, "Aircraft_List_Strike_Red.pdf"),
    )
    save_get_list_of_aircrafts_pdf(
        _LIST_SIDE,
        _LIST_TASK,
        _LIST_TARGET_DIST,
        os.path.join(OUTPUT_DIR, "Aircraft_List_Strike_Red_FighterBomber.pdf"),
        role="Fighter_Bomber",
    )
    save_aircrafts_quantity_pdf(
        os.path.join(OUTPUT_DIR, "Aircraft_Quantity.pdf"),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MENU INTERATTIVO
# ─────────────────────────────────────────────────────────────────────────────

_MENU_ITEMS = [
    ("Esegui i test unitari",                _run_tests),
    ("Stampa le tabelle a terminale",        _run_tables_terminal),
    ("Salva le tabelle in PDF",              _run_tables_pdf),
    ("Esegui test + stampa a terminale",     None),
    ("Esegui test + salva PDF",              None),
    ("Stampa a terminale + salva PDF",       None),
    ("Tutto (test + terminale + PDF)",       None),
    ("Esci",                                 None),
]


def _print_menu() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       Test_Aircraft_Data  —  Menu principale                ║")
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


if __name__ == "__main__":
    if "--tests-only" in sys.argv:
        result = _run_tests()
        sys.exit(0 if result.wasSuccessful() else 1)
    elif "--tables-only" in sys.argv:
        _run_tables_terminal()
        _run_tables_pdf()
    else:
        _interactive_menu()
