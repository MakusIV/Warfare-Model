"""
Test_Aircraft_Loadouts.py
=========================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo
Aircraft_Loadouts.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Loadouts.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Loadouts.py            # menu interattivo

Bug nel modulo Aircraft_Loadouts (documentati nei test):
  BL1. loadout_eval(): `get_weapon_score(weapon_model=weapon[0])` usava il keyword
       argument `weapon_model` che non esiste nella firma di get_weapon_score()
       (la quale accetta `model` come parametro positivo) → TypeError su ogni
       loadout con almeno un'arma in stores.pylons.
       [CORRETTO: sostituito con get_weapon_score(weapon[0])]
  BL2. loadout_eval() e loadout_target_effectiveness(): alcuni loadout portano
       store non-arma nei pylons (serbatoi carburante: 1300L_tank, 150gal_tank,
       267gal_tank, 275gal_tank, 330gal_tank, 370gal_tank, 600gal_tank, 800L_tank,
       PTB-1500; pod: boom_refueling, buddy_refueling_pod, hose_drogue_pod) che
       non sono in AIR_WEAPONS → get_weapon_score() / get_weapon_score_target()
       chiamano Aircraft_Weapon_Data.logger.warning() → Bug B0 → AttributeError.
       [WORKAROUND nei test: patch di entrambi i logger (Aircraft_Loadouts e
       Aircraft_Weapon_Data). Score corretto = 0 per quelle store, non N/A.]
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAZIONE — modificare le liste per personalizzare le tabelle
# ─────────────────────────────────────────────────────────────────────────────

LOADOUT_TASKS: List[str] = ["CAP", "Strike", "CAS", "SEAD", "Escort", "Pinpoint_Strike", "Anti_Ship"]

TARGET_TYPE_LIST: List[str] = ["Soft", "Armored", "Structure", "Air_Defense", "ship"]

TARGET_DIMENSION_LIST: List[str] = ["small", "med", "big"]

# Override per-task di TARGET_TYPE_LIST per loadout_target_effectiveness.
# get_weapon_score_target normalizza lo score dividendo per il numero totale di
# combinazioni (t_type × t_dim) richieste, incluse quelle senza dati di efficienza.
# Le armi specializzate (es. missili anti-nave con efficiency solo su "ship") vengono
# penalizzate quando si passa una lista generica di 5 tipi → denominatore 15 invece
# di 3 → score diluito per 5×.
# Specificando solo i tipi di bersaglio pertinenti al task si ottengono valori
# comparabili e semanticamente corretti.
TASK_TARGET_TYPE_OVERRIDE: dict = {
    "Anti_Ship": ["ship"],
}

# Velocità e lunghezza rotta basse → tutti i loadout con speed>100 e range>100 superano la verifica
ROUTE_SPEED: float = 100.0   # km/h
ROUTE_LENGTH: float = 100.0  # km

# ─── Distribuzioni target per loadout_target_effectiveness_by_distribuition ──
# Distribuzione monotipo: solo Soft, tutte le dimensioni, somme = 1.0
_DIST_SOFT_ONLY: dict = {
    "Soft": {
        "perc_type": 1.0,
        "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3},
    }
}

# Distribuzione mista: Soft 70% + Armored 30%, somme = 1.0
_DIST_MIXED: dict = {
    "Soft": {
        "perc_type": 0.7,
        "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3},
    },
    "Armored": {
        "perc_type": 0.3,
        "perc_dimension": {"big": 0.3, "med": 0.4, "small": 0.3},
    },
}

# Distribuzione non valida: manca la chiave perc_dimension
_DIST_MISSING_DIM: dict = {
    "Soft": {
        "perc_type": 1.0,
    }
}

# Distribuzione non valida: perc_type > 1 (fuori range)
_DIST_PERC_TYPE_INVALID: dict = {
    "Soft": {
        "perc_type": 1.5,
        "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3},
    }
}

# Distribuzione non valida: somma perc_dimension != 1.0
_DIST_DIM_SUM_INVALID: dict = {
    "Soft": {
        "perc_type": 1.0,
        "perc_dimension": {"big": 0.5, "med": 0.5, "small": 0.5},  # sum = 1.5
    }
}

# Distribuzione non valida: somma perc_type != 1.0
_DIST_TYPE_SUM_INVALID: dict = {
    "Soft": {
        "perc_type": 0.5,
        "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3},
    },
    "Armored": {
        "perc_type": 0.1,  # somma totale = 0.6, non 1.0
        "perc_dimension": {"big": 0.3, "med": 0.4, "small": 0.3},
    },
}

# Directory di output per i PDF
OUTPUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "out")
)

# Costante per il patch del logger (from venv import logger in Aircraft_Loadouts)
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts.logger"
# Necessario anche per loadout_target_effectiveness che chiama get_weapon_score_target()
# la quale a sua volta invoca logger.debug() → Bug B0 di Aircraft_Weapon_Data
_LOGGER_PATH_WD = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  FIXTURE GLOBALI
# ─────────────────────────────────────────────────────────────────────────────

_AIRCRAFT_CAP    = "F-14A Tomcat"
_LOADOUT_CAP     = "Phoenix Fleet Defense"   # tasks: ["CAP", "Intercept"], all-weather

_AIRCRAFT_STRIKE = "F-15E Strike Eagle"
_LOADOUT_STRIKE  = "Laser Strike"            # tasks: ["Pinpoint_Strike"]

_AIRCRAFT_CAS    = "F/A-18A Hornet"
_LOADOUT_CAS     = "CAS"                     # tasks: ["CAS"], day-only

# Loadout con mandatory_support Escort=True — usato nei test di supporto
_AIRCRAFT_IRON   = "F-15E Strike Eagle"
_LOADOUT_IRON    = "Iron Bomb Strike"

# Loadout con serbatoi carburante nei pylons (267gal_tank non è in AIR_WEAPONS)
# → loadout_year_compatibility restituisce sempre False indipendentemente dall'anno
_AIRCRAFT_SPARROW = "F-14A Tomcat"
_LOADOUT_SPARROW  = "Sparrow CAP/Escort"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import (
    AIRCRAFT_LOADOUTS,
    get_aircraft_loadouts,
    get_aircraft_loadouts_by_task,
    get_loadout,
    get_loadout_tasks,
    get_loadout_attributes,
    evaluate_loadout_usability,
    evaluate_loadout_support_requirements,
    evaluate_loadout_range,
    evaluate_loadout_speed,
    evaluate_loadout_altitude,
    loadout_eval,
    loadout_target_effectiveness,
    loadout_target_effectiveness_by_distribuition,
    loadout_year_compatibility,
)

# ─────────────────────────────────────────────────────────────────────────────
#  UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────


class TestGetAircraftLoadouts(unittest.TestCase):
    """Unit test per get_aircraft_loadouts()."""

    def test_valid_aircraft_returns_dict(self):
        """Aircraft valido → restituisce un dizionario."""
        result = get_aircraft_loadouts(_AIRCRAFT_CAP)
        self.assertIsInstance(result, dict)

    def test_returns_nonempty_dict(self):
        """L'F-14A Tomcat ha almeno un loadout nel database."""
        result = get_aircraft_loadouts(_AIRCRAFT_CAP)
        self.assertTrue(result)

    def test_values_are_dicts(self):
        """Ogni valore nel dizionario restituito è a sua volta un dizionario (loadout config)."""
        result = get_aircraft_loadouts(_AIRCRAFT_CAP)
        for name, config in result.items():
            with self.subTest(loadout=name):
                self.assertIsInstance(config, dict)

    def test_each_loadout_has_tasks_key(self):
        """Ogni loadout config contiene la chiave 'tasks'."""
        result = get_aircraft_loadouts(_AIRCRAFT_CAP)
        for name, config in result.items():
            with self.subTest(loadout=name):
                self.assertIn("tasks", config)

    def test_known_loadout_present(self):
        """Il loadout noto 'Phoenix Fleet Defense' è presente per l'F-14A Tomcat."""
        result = get_aircraft_loadouts(_AIRCRAFT_CAP)
        self.assertIn(_LOADOUT_CAP, result)

    def test_multiple_aircraft_return_different_dicts(self):
        """Aeromobili diversi restituiscono loadout diversi."""
        result_cap    = get_aircraft_loadouts(_AIRCRAFT_CAP)
        result_strike = get_aircraft_loadouts(_AIRCRAFT_STRIKE)
        self.assertNotEqual(set(result_cap.keys()), set(result_strike.keys()))

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            get_aircraft_loadouts("INVALID_AIRCRAFT_XYZ")


class TestGetAircraftLoadoutsByTask(unittest.TestCase):
    """Unit test per get_aircraft_loadouts_by_task()."""

    def test_valid_task_returns_dict(self):
        """Aircraft valido + task valido → restituisce un dizionario."""
        result = get_aircraft_loadouts_by_task(_AIRCRAFT_CAP, "CAP")
        self.assertIsInstance(result, dict)

    def test_known_loadout_present_for_task(self):
        """'Phoenix Fleet Defense' deve comparire tra i loadout CAP dell'F-14A Tomcat."""
        result = get_aircraft_loadouts_by_task(_AIRCRAFT_CAP, "CAP")
        self.assertIn(_LOADOUT_CAP, result)

    def test_all_returned_loadouts_have_task(self):
        """Tutti i loadout nel risultato devono contenere il task richiesto."""
        task = "CAP"
        result = get_aircraft_loadouts_by_task(_AIRCRAFT_CAP, task)
        for name, config in result.items():
            with self.subTest(loadout=name):
                self.assertIn(task, config.get("tasks", []))

    def test_result_is_subset_of_all_loadouts(self):
        """Il risultato per un task è un sottoinsieme di get_aircraft_loadouts()."""
        all_loadouts  = get_aircraft_loadouts(_AIRCRAFT_CAP)
        task_loadouts = get_aircraft_loadouts_by_task(_AIRCRAFT_CAP, "CAP")
        for name in task_loadouts:
            with self.subTest(loadout=name):
                self.assertIn(name, all_loadouts)

    def test_strike_task_returns_strike_loadout(self):
        """'Laser Strike' deve comparire tra i loadout Pinpoint_Strike dell'F-15E."""
        result = get_aircraft_loadouts_by_task(_AIRCRAFT_STRIKE, "Pinpoint_Strike")
        self.assertIn(_LOADOUT_STRIKE, result)

    def test_unknown_task_returns_empty_dict(self):
        """Task inesistente → dizionario vuoto (non ValueError)."""
        result = get_aircraft_loadouts_by_task(_AIRCRAFT_CAP, "TASK_THAT_DOES_NOT_EXIST_XYZ")
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_loadout_not_in_task_is_excluded(self):
        """Un loadout che non ha il task richiesto non deve comparire nel risultato."""
        # "Phoenix Fleet Defense" ha tasks CAP e Intercept, non "CAS"
        result = get_aircraft_loadouts_by_task(_AIRCRAFT_CAP, "CAS")
        self.assertNotIn(_LOADOUT_CAP, result)

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft sconosciuto → ValueError (propagato da get_aircraft_loadouts)."""
        with self.assertRaises(ValueError):
            get_aircraft_loadouts_by_task("INVALID_AIRCRAFT_XYZ", "CAP")


class TestGetLoadout(unittest.TestCase):
    """Unit test per get_loadout()."""

    def test_valid_returns_dict(self):
        """Coppia valida (aircraft, loadout) restituisce un dizionario non vuoto."""
        result = get_loadout(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)

    def test_contains_required_keys(self):
        """Il dizionario contiene le chiavi obbligatorie."""
        result = get_loadout(_AIRCRAFT_CAP, _LOADOUT_CAP)
        for key in ("cruise", "attack", "stores", "tasks", "loadout_code"):
            with self.subTest(key=key):
                self.assertIn(key, result)

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            get_loadout("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP)

    def test_invalid_loadout_raises_ValueError(self):
        """Loadout sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            get_loadout(_AIRCRAFT_CAP, "INVALID_LOADOUT_XYZ")


class TestGetLoadoutTasks(unittest.TestCase):
    """Unit test per get_loadout_tasks()."""

    def test_returns_list(self):
        """Restituisce una lista."""
        result = get_loadout_tasks(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertIsInstance(result, list)

    def test_returns_nonempty_list(self):
        """F-14A Phoenix Fleet Defense ha task noti (CAP, Intercept)."""
        result = get_loadout_tasks(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertTrue(result)
        self.assertIn("CAP", result)
        self.assertIn("Intercept", result)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            get_loadout_tasks("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP)


class TestGetLoadoutAttributes(unittest.TestCase):
    """Unit test per get_loadout_attributes()."""

    def test_returns_list(self):
        """Restituisce una lista (anche vuota)."""
        result = get_loadout_attributes(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertIsInstance(result, list)

    def test_strike_loadout_has_attributes(self):
        """Laser Strike ha attributi non vuoti (Precision, Laser-guided)."""
        result = get_loadout_attributes(_AIRCRAFT_STRIKE, _LOADOUT_STRIKE)
        self.assertIsInstance(result, list)
        self.assertTrue(result)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            get_loadout_attributes("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP)


class TestEvaluateLoadoutUsability(unittest.TestCase):
    """Unit test per evaluate_loadout_usability()."""

    def test_day_condition_met(self):
        """F-14A Phoenix Fleet Defense, ['day'] → True (day=True)."""
        result = evaluate_loadout_usability(_AIRCRAFT_CAP, _LOADOUT_CAP, ["day"])
        self.assertTrue(result)

    def test_all_conditions_met(self):
        """Loadout all-weather: ['day','night','adverse_weather'] → True."""
        result = evaluate_loadout_usability(
            _AIRCRAFT_CAP, _LOADOUT_CAP, ["day", "night", "adverse_weather"]
        )
        self.assertTrue(result)

    def test_condition_not_met(self):
        """F/A-18A CAS ha night=False → ['night'] → False."""
        result = evaluate_loadout_usability(_AIRCRAFT_CAS, _LOADOUT_CAS, ["night"])
        self.assertFalse(result)

    def test_adverse_weather_not_met(self):
        """F/A-18A CAS ha adverse_weather=False → ['adverse_weather'] → False."""
        result = evaluate_loadout_usability(
            _AIRCRAFT_CAS, _LOADOUT_CAS, ["adverse_weather"]
        )
        self.assertFalse(result)

    def test_empty_conditions_returns_true(self):
        """Lista condizioni vuota: nessuna condizione da soddisfare → True."""
        result = evaluate_loadout_usability(_AIRCRAFT_CAP, _LOADOUT_CAP, [])
        self.assertTrue(result)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            evaluate_loadout_usability("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, ["day"])


class TestEvaluateLoadoutSupportRequirements(unittest.TestCase):
    """Unit test per evaluate_loadout_support_requirements()."""

    def test_no_support_required_returns_true(self):
        """Phoenix Fleet Defense: tutto mandatory_support=False → True."""
        result = evaluate_loadout_support_requirements(
            _AIRCRAFT_CAP, _LOADOUT_CAP, {}
        )
        self.assertTrue(result)

    def test_support_available_returns_true(self):
        """Iron Bomb Strike richiede Escort → fornito → True."""
        result = evaluate_loadout_support_requirements(
            _AIRCRAFT_IRON, _LOADOUT_IRON, {"Escort": True}
        )
        self.assertTrue(result)

    def test_support_unavailable_returns_false(self):
        """Iron Bomb Strike richiede Escort → non fornito → False."""
        result = evaluate_loadout_support_requirements(
            _AIRCRAFT_IRON, _LOADOUT_IRON, {}
        )
        self.assertFalse(result)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            evaluate_loadout_support_requirements(
                "INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, {}
            )


class TestEvaluateLoadoutRange(unittest.TestCase):
    """Unit test per evaluate_loadout_range()."""

    def test_cruise_fuel_100(self):
        """Raggio cruise a fuel_100% deve essere > 0."""
        result = evaluate_loadout_range(_AIRCRAFT_CAP, _LOADOUT_CAP, 100, "cruise")
        self.assertGreater(result, 0)

    def test_attack_fuel_100(self):
        """Raggio attack a fuel_100% deve essere > 0."""
        result = evaluate_loadout_range(_AIRCRAFT_CAP, _LOADOUT_CAP, 100, "attack")
        self.assertGreater(result, 0)

    def test_cruise_fuel_50(self):
        """Raggio cruise a fuel_50% deve essere > 0."""
        result = evaluate_loadout_range(_AIRCRAFT_CAP, _LOADOUT_CAP, 50, "cruise")
        self.assertGreater(result, 0)

    def test_invalid_fuel_key_returns_zero(self):
        """Chiave fuel inesistente (fuel_999%) → 0."""
        result = evaluate_loadout_range(_AIRCRAFT_CAP, _LOADOUT_CAP, 999, "cruise")
        self.assertEqual(result, 0)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            evaluate_loadout_range("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, 100, "cruise")


class TestEvaluateLoadoutSpeed(unittest.TestCase):
    """Unit test per evaluate_loadout_speed()."""

    def test_cruise_speed_positive(self):
        """Velocità cruise deve essere > 0."""
        result = evaluate_loadout_speed(_AIRCRAFT_CAP, _LOADOUT_CAP, "cruise")
        self.assertGreater(result, 0)

    def test_attack_speed_positive(self):
        """Velocità attack deve essere > 0."""
        result = evaluate_loadout_speed(_AIRCRAFT_CAP, _LOADOUT_CAP, "attack")
        self.assertGreater(result, 0)

    def test_attack_speed_ge_cruise_speed(self):
        """La velocità attack deve essere >= cruise per i caccia supersonici."""
        cruise = evaluate_loadout_speed(_AIRCRAFT_CAP, _LOADOUT_CAP, "cruise")
        attack = evaluate_loadout_speed(_AIRCRAFT_CAP, _LOADOUT_CAP, "attack")
        self.assertGreaterEqual(attack, cruise)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            evaluate_loadout_speed("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, "cruise")


class TestEvaluateLoadoutAltitude(unittest.TestCase):
    """Unit test per evaluate_loadout_altitude()."""

    def test_returns_dict_with_three_keys(self):
        """Restituisce un dizionario con le tre chiavi di altitudine."""
        result = evaluate_loadout_altitude(_AIRCRAFT_CAP, _LOADOUT_CAP, "cruise")
        self.assertIsInstance(result, dict)
        for key in ("reference_altitude", "altitude_max", "altitude_min"):
            with self.subTest(key=key):
                self.assertIn(key, result)

    def test_values_are_non_negative(self):
        """Tutti i valori di altitudine devono essere >= 0."""
        result = evaluate_loadout_altitude(_AIRCRAFT_CAP, _LOADOUT_CAP, "cruise")
        for key, val in result.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(val, 0)

    def test_attack_altitude_dict_valid(self):
        """La fase attack restituisce un dizionario con valori >= 0."""
        result = evaluate_loadout_altitude(_AIRCRAFT_CAP, _LOADOUT_CAP, "attack")
        self.assertIsInstance(result, dict)
        for val in result.values():
            self.assertGreaterEqual(val, 0)

    def test_invalid_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            evaluate_loadout_altitude("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, "cruise")

class TestLoadoutEval(unittest.TestCase):
    """
    Unit test per loadout_eval(). Entrambi i logger mockati per isolare dai side-effect.

    Bug BL1 corretto: get_weapon_score() veniva chiamato con keyword argument
    `weapon_model=` inesistente → TypeError. Dopo la correzione
    (argomento posizionale) la funzione calcola correttamente lo score.

    Alcuni loadout portano store non-arma (serbatoi, pod di rifornimento) assenti da
    AIR_WEAPONS → get_weapon_score chiama Aircraft_Weapon_Data.logger.warning() →
    Bug B0. Per questo si patchano entrambi i logger.
    """

    def setUp(self):
        self._logger_patcher    = patch(_LOGGER_PATH,    MagicMock())
        self._logger_patcher_wd = patch(_LOGGER_PATH_WD, MagicMock())
        self._logger_patcher.start()
        self._logger_patcher_wd.start()

    def tearDown(self):
        self._logger_patcher_wd.stop()
        self._logger_patcher.stop()

    def test_returns_float(self):
        """Restituisce un float."""
        result = loadout_eval(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertIsInstance(result, float)

    def test_score_non_negative(self):
        """Punteggio >= 0."""
        result = loadout_eval(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertGreaterEqual(result, 0.0)

    def test_strike_loadout_positive_score(self):
        """F-15E Laser Strike → punteggio > 0."""
        result = loadout_eval(_AIRCRAFT_STRIKE, _LOADOUT_STRIKE)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0.0)

    def test_cap_loadout_positive_score(self):
        """F-14A Phoenix Fleet Defense → punteggio > 0."""
        result = loadout_eval(_AIRCRAFT_CAP, _LOADOUT_CAP)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0.0)

    def test_different_loadouts_different_scores(self):
        """Due loadout diversi producono punteggi diversi."""
        score_cap    = loadout_eval(_AIRCRAFT_CAP, _LOADOUT_CAP)
        score_strike = loadout_eval(_AIRCRAFT_STRIKE, _LOADOUT_STRIKE)
        self.assertNotEqual(score_cap, score_strike)

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            loadout_eval("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP)

    def test_invalid_loadout_raises_ValueError(self):
        """Loadout non valido → ValueError."""
        with self.assertRaises(ValueError):
            loadout_eval(_AIRCRAFT_CAP, "INVALID_LOADOUT_XYZ")


class TestLoadoutTargetEffectiveness(unittest.TestCase):
    """
    Unit test per loadout_target_effectiveness(). Logger mockato.

    Questa funzione chiama internamente get_weapon_score_target() di
    Aircraft_Weapon_Data, che invoca logger.debug() su armi valide →
    Bug B0 di Aircraft_Weapon_Data. Per isolare i test occorre mockare
    entrambi i logger (Aircraft_Loadouts e Aircraft_Weapon_Data).
    """

    def setUp(self):
        self._logger_patcher    = patch(_LOGGER_PATH,    MagicMock())
        self._logger_patcher_wd = patch(_LOGGER_PATH_WD, MagicMock())
        self._logger_patcher.start()
        self._logger_patcher_wd.start()

    def tearDown(self):
        self._logger_patcher_wd.stop()
        self._logger_patcher.stop()

    def test_returns_float(self):
        """Restituisce un float."""
        result = loadout_target_effectiveness(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE,
            ["Structure"], ["big"], ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertIsInstance(result, float)

    def test_score_non_negative(self):
        """Punteggio >= 0."""
        result = loadout_target_effectiveness(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE,
            ["Structure"], ["big"], ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertGreaterEqual(result, 0.0)

    def test_excessive_route_speed_returns_zero(self):
        """Velocità rotta irraggiungibile → loadout non approvato → 0.0."""
        result = loadout_target_effectiveness(
            _AIRCRAFT_CAP, _LOADOUT_CAP,
            ["Soft"], ["small"], ROUTE_LENGTH, 99999.0,
        )
        self.assertEqual(result, 0.0)

    def test_excessive_route_length_returns_zero(self):
        """Lunghezza rotta irraggiungibile → loadout non approvato → 0.0."""
        result = loadout_target_effectiveness(
            _AIRCRAFT_CAP, _LOADOUT_CAP,
            ["Soft"], ["small"], 99999.0, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    def test_valid_params_strike_loadout(self):
        """F-15E Laser Strike, target Structure/big, rotta breve → punteggio >= 0."""
        result = loadout_target_effectiveness(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE,
            ["Structure"], ["big"], ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_valid_params_cas_loadout(self):
        """F/A-18A CAS, target Soft/small, rotta breve → punteggio >= 0."""
        result = loadout_target_effectiveness(
            _AIRCRAFT_CAS, _LOADOUT_CAS,
            ["Soft"], ["small"], ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft non valido → ValueError."""
        with self.assertRaises(ValueError):
            loadout_target_effectiveness(
                "INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP,
                ["Soft"], ["small"], ROUTE_LENGTH, ROUTE_SPEED,
            )

    def test_invalid_loadout_raises_ValueError(self):
        """Loadout non valido → ValueError."""
        with self.assertRaises(ValueError):
            loadout_target_effectiveness(
                _AIRCRAFT_CAP, "INVALID_LOADOUT_XYZ",
                ["Soft"], ["small"], ROUTE_LENGTH, ROUTE_SPEED,
            )


# ─────────────────────────────────────────────────────────────────────────────
#  FUNZIONI HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _is_nan(value: float) -> bool:
    try:
        return value != value
    except Exception:
        return False


def _safe_loadout_eval(aircraft: str, loadout: str) -> float:
    """Chiama loadout_eval con entrambi i logger mockati; ritorna float('nan') su eccezione.

    È necessario patchare anche Aircraft_Weapon_Data.logger perché alcuni loadout
    portano store non-arma (serbatoi, pod) assenti da AIR_WEAPONS → get_weapon_score
    chiama logger.warning() su quel modulo → Bug B0.
    """
    try:
        with patch(_LOGGER_PATH, MagicMock()), patch(_LOGGER_PATH_WD, MagicMock()):
            return loadout_eval(aircraft, loadout)
    except Exception:
        return float("nan")


def _safe_loadout_target_eff(
    aircraft: str,
    loadout: str,
    t_types: List[str],
    t_dims: List[str],
    r_len: float,
    r_spd: float,
) -> float:
    """Chiama loadout_target_effectiveness con entrambi i logger mockati; ritorna float('nan') su eccezione."""
    try:
        with patch(_LOGGER_PATH, MagicMock()), patch(_LOGGER_PATH_WD, MagicMock()):
            return loadout_target_effectiveness(aircraft, loadout, t_types, t_dims, r_len, r_spd)
    except Exception:
        return float("nan")


def _safe_loadout_target_eff_by_dist(
    aircraft: str,
    loadout: str,
    distribution: dict,
    r_len: float,
    r_spd: float,
) -> float:
    """Chiama loadout_target_effectiveness_by_distribuition con entrambi i logger mockati; ritorna float('nan') su eccezione."""
    try:
        with patch(_LOGGER_PATH, MagicMock()), patch(_LOGGER_PATH_WD, MagicMock()):
            return loadout_target_effectiveness_by_distribuition(aircraft, loadout, distribution, r_len, r_spd)
    except Exception:
        return float("nan")


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — STAMPA A TERMINALE
# ─────────────────────────────────────────────────────────────────────────────

def print_loadout_eval_tables(task_list: List[str]) -> None:
    """
    Stampa a terminale una sezione per ogni task in task_list.
    Ogni sezione elenca i loadout con quel task, ordinati per score loadout_eval
    decrescente.
    Colonne: #, Aircraft, Loadout Name, Loadout Code, Score
    """
    for task in task_list:
        rows = []
        for aircraft_name, loadouts in AIRCRAFT_LOADOUTS.items():
            for loadout_name, data in loadouts.items():
                if task in data.get("tasks", []):
                    score = _safe_loadout_eval(aircraft_name, loadout_name)
                    code  = data.get("loadout_code", "")
                    rows.append((aircraft_name, loadout_name, code, score))

        if not rows:
            print(f"\n[SKIP] Nessun loadout trovato per il task '{task}'.\n")
            continue

        rows.sort(key=lambda x: float("-inf") if _is_nan(x[3]) else x[3], reverse=True)

        col_a = max(len("Aircraft"),     max(len(r[0]) for r in rows))
        col_l = max(len("Loadout Name"), max(len(r[1]) for r in rows))
        col_c = max(len("Loadout Code"), max(len(r[2]) for r in rows))
        col_s = 14
        rank_w = 3
        sep = "  "

        width = rank_w + len(sep) + col_a + len(sep) + col_l + len(sep) + col_c + len(sep) + col_s + 2

        print()
        print("═" * width)
        print(f"  TASK: {task}   —   loadout_eval()")
        print("═" * width)
        print(
            f"  {'#':<{rank_w}}{sep}"
            f"{'Aircraft':<{col_a}}{sep}"
            f"{'Loadout Name':<{col_l}}{sep}"
            f"{'Loadout Code':<{col_c}}{sep}"
            f"{'Score':>{col_s}}"
        )
        print("─" * width)
        for rank, (aircraft_name, loadout_name, code, score) in enumerate(rows, start=1):
            s = f"{score:.6f}" if not _is_nan(score) else "     N/A     "
            print(
                f"  {rank:<{rank_w}}{sep}"
                f"{aircraft_name:<{col_a}}{sep}"
                f"{loadout_name:<{col_l}}{sep}"
                f"{code:<{col_c}}{sep}"
                f"{s:>{col_s}}"
            )
        print()


def print_loadout_target_eff_tables(
    task_list: List[str],
    target_type_list: List[str],
    target_dim_list: List[str],
    route_length: float,
    route_speed: float,
) -> None:
    """
    Stampa a terminale una sezione per ogni task in task_list.
    Ogni sezione elenca i loadout con quel task, ordinati per score
    loadout_target_effectiveness decrescente (usando le liste target_type e
    target_dimension passate direttamente alla funzione).
    Colonne: #, Aircraft, Loadout Name, Loadout Code, Score
    """
    for task in task_list:
        if task in ["CAP", "Escort", "Intercept", "Fighter Sweep"]:
            print(f"\n[SKIP] Il task '{task}' non è adatto a loadout_target_effectiveness().\n")
            continue
        eff_target_types = TASK_TARGET_TYPE_OVERRIDE.get(task, target_type_list)
        rows = []
        for aircraft_name, loadouts in AIRCRAFT_LOADOUTS.items():
            for loadout_name, data in loadouts.items():
                if task in data.get("tasks", []):
                    score = _safe_loadout_target_eff(
                        aircraft_name, loadout_name,
                        eff_target_types, target_dim_list,
                        route_length, route_speed,
                    )
                    code = data.get("loadout_code", "")
                    rows.append((aircraft_name, loadout_name, code, score))

        if not rows:
            print(f"\n[SKIP] Nessun loadout trovato per il task '{task}'.\n")
            continue

        rows.sort(key=lambda x: float("-inf") if _is_nan(x[3]) else x[3], reverse=True)

        col_a = max(len("Aircraft"),     max(len(r[0]) for r in rows))
        col_l = max(len("Loadout Name"), max(len(r[1]) for r in rows))
        col_c = max(len("Loadout Code"), max(len(r[2]) for r in rows))
        col_s = 14
        rank_w = 3
        sep = "  "

        width = rank_w + len(sep) + col_a + len(sep) + col_l + len(sep) + col_c + len(sep) + col_s + 2

        t_label = "/".join(target_type_list)
        d_label = "/".join(target_dim_list)
        print()
        print("═" * width)
        print(f"  TASK: {task}   —   loadout_target_effectiveness()  [{t_label}] × [{d_label}]")
        print("═" * width)
        print(
            f"  {'#':<{rank_w}}{sep}"
            f"{'Aircraft':<{col_a}}{sep}"
            f"{'Loadout Name':<{col_l}}{sep}"
            f"{'Loadout Code':<{col_c}}{sep}"
            f"{'Score':>{col_s}}"
        )
        print("─" * width)
        for rank, (aircraft_name, loadout_name, code, score) in enumerate(rows, start=1):
            s = f"{score:.6f}" if not _is_nan(score) else "     N/A     "
            print(
                f"  {rank:<{rank_w}}{sep}"
                f"{aircraft_name:<{col_a}}{sep}"
                f"{loadout_name:<{col_l}}{sep}"
                f"{code:<{col_c}}{sep}"
                f"{s:>{col_s}}"
            )
        print()


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — GENERAZIONE PDF
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
    """Stile intestazione tabella: sfondo scuro, testo bianco in grassetto."""
    for col in range(n_cols):
        tbl[0, col].set_facecolor("#2c3e50")
        tbl[0, col].set_text_props(color="white", fontweight="bold")


def save_loadout_eval_pdf(task_list: List[str], output_path: str) -> None:
    """
    Salva un PDF con una pagina per task.
    Ogni pagina: tabella loadout_eval() ordinata per score decrescente,
    con colorazione heatmap RdYlGn sulla colonna Score.
    Colonne: #, Aircraft, Loadout Name, Loadout Code, Score
    """
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with PdfPages(output_path) as pdf:
        for task in task_list:
            rows = []
            for aircraft_name, loadouts in AIRCRAFT_LOADOUTS.items():
                for loadout_name, data in loadouts.items():
                    if task in data.get("tasks", []):
                        score = _safe_loadout_eval(aircraft_name, loadout_name)
                        code  = data.get("loadout_code", "")
                        rows.append((aircraft_name, loadout_name, code, score))

            if not rows:
                continue

            rows.sort(key=lambda x: float("-inf") if _is_nan(x[3]) else x[3], reverse=True)

            valid_scores = [r[3] for r in rows if not _is_nan(r[3])]
            max_s = max(valid_scores) if valid_scores else 1.0
            min_s = min(valid_scores) if valid_scores else 0.0
            rng   = (max_s - min_s) if max_s != min_s else 1.0

            cell_text, cell_colors = [], []
            for rank, (aircraft_name, loadout_name, code, score) in enumerate(rows, start=1):
                score_str = f"{score:.6f}" if not _is_nan(score) else "N/A"
                cell_text.append([str(rank), aircraft_name, loadout_name, code, score_str])
                if not _is_nan(score):
                    heat = plt.cm.RdYlGn((score - min_s) / rng)
                else:
                    heat = (0.87, 0.87, 0.87, 1.0)
                cell_colors.append(["#f5f5f5", "#f0f4f8", "#f0f4f8", "#f0f4f8", heat])

            n_cols = 5
            fig_h = max(4.0, 0.38 * len(cell_text) + 2.5)
            fig, ax = plt.subplots(figsize=(14, fig_h))
            ax.axis("off")
            ax.set_title(
                f"Confronto Loadout — Task: {task}\nFunzione: loadout_eval()",
                fontsize=13, fontweight="bold", pad=20,
            )
            tbl = ax.table(
                cellText=cell_text,
                colLabels=["#", "Aircraft", "Loadout Name", "Loadout Code", "Score"],
                cellColours=cell_colors,
                loc="center", cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)
            tbl.auto_set_column_width(list(range(n_cols)))
            _header_style(tbl, n_cols)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"[PDF] loadout_eval → {output_path}")


def save_loadout_target_eff_pdf(
    task_list: List[str],
    t_types: List[str],
    t_dims: List[str],
    r_len: float,
    r_spd: float,
    output_path: str,
) -> None:
    """
    Salva un PDF con una pagina per task.
    Ogni pagina: tabella loadout_target_effectiveness() ordinata per score
    decrescente, con colorazione heatmap RdYlGn sulla colonna Score.
    Colonne: #, Aircraft, Loadout Name, Loadout Code, Score
    """
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with PdfPages(output_path) as pdf:
        for task in task_list:
            if task in ["CAP", "Escort", "Intercept", "Fighter Sweep"]:
                continue
            eff_t_types = TASK_TARGET_TYPE_OVERRIDE.get(task, t_types)
            rows = []
            for aircraft_name, loadouts in AIRCRAFT_LOADOUTS.items():
                for loadout_name, data in loadouts.items():
                    if task in data.get("tasks", []):
                        score = _safe_loadout_target_eff(
                            aircraft_name, loadout_name,
                            eff_t_types, t_dims, r_len, r_spd,
                        )
                        code = data.get("loadout_code", "")
                        rows.append((aircraft_name, loadout_name, code, score))

            if not rows:
                continue

            rows.sort(key=lambda x: float("-inf") if _is_nan(x[3]) else x[3], reverse=True)

            valid_scores = [r[3] for r in rows if not _is_nan(r[3])]
            max_s = max(valid_scores) if valid_scores else 1.0
            min_s = min(valid_scores) if valid_scores else 0.0
            rng   = (max_s - min_s) if max_s != min_s else 1.0

            cell_text, cell_colors = [], []
            for rank, (aircraft_name, loadout_name, code, score) in enumerate(rows, start=1):
                score_str = f"{score:.6f}" if not _is_nan(score) else "N/A"
                cell_text.append([str(rank), aircraft_name, loadout_name, code, score_str])
                if not _is_nan(score):
                    heat = plt.cm.RdYlGn((score - min_s) / rng)
                else:
                    heat = (0.87, 0.87, 0.87, 1.0)
                cell_colors.append(["#f5f5f5", "#f0f4f8", "#f0f4f8", "#f0f4f8", heat])

            n_cols = 5
            t_label = "/".join(t_types)
            d_label = "/".join(t_dims)
            fig_h = max(4.0, 0.38 * len(cell_text) + 2.5)
            fig, ax = plt.subplots(figsize=(14, fig_h))
            ax.axis("off")
            ax.set_title(
                f"Confronto Loadout vs Bersaglio — Task: {task}\n"
                f"Funzione: loadout_target_effectiveness()  [{t_label}] × [{d_label}]",
                fontsize=12, fontweight="bold", pad=20,
            )
            tbl = ax.table(
                cellText=cell_text,
                colLabels=["#", "Aircraft", "Loadout Name", "Loadout Code", "Score"],
                cellColours=cell_colors,
                loc="center", cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)
            tbl.auto_set_column_width(list(range(n_cols)))
            _header_style(tbl, n_cols)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"[PDF] loadout_target_eff → {output_path}")


class TestLoadoutTargetEffectivenessByDistribution(unittest.TestCase):
    """
    Unit test per loadout_target_effectiveness_by_distribuition().

    La funzione esegue due fasi distinte prima di calcolare lo score:
      1. Approvazione rotta (stessa logica di loadout_target_effectiveness):
         se route_speed > velocità loadout o route_length > gittata effettiva → 0.0
      2. Validazione della distribuzione target:
         - perc_dimension deve essere presente e non vuota → altrimenti 0.0
         - perc_type deve essere in [0, 1] → altrimenti 0.0
         - somma perc_dimension ≈ 1.0 (±0.01) → altrimenti 0.0
         - somma perc_type ≈ 1.0 (±0.01) → altrimenti 0.0
      3. Calcolo score pesato per (target_type × target_dimension × weapon).

    Entrambi i logger sono mockati per isolare dai side-effect di
    Aircraft_Loadouts e Aircraft_Weapon_Data.
    """

    def setUp(self):
        self._logger_patcher    = patch(_LOGGER_PATH,    MagicMock())
        self._logger_patcher_wd = patch(_LOGGER_PATH_WD, MagicMock())
        self._logger_patcher.start()
        self._logger_patcher_wd.start()

    def tearDown(self):
        self._logger_patcher_wd.stop()
        self._logger_patcher.stop()

    # ── Comportamento base ────────────────────────────────────────────────────

    def test_returns_float(self):
        """Distribuzione valida, rotta breve → restituisce un float."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_SOFT_ONLY,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertIsInstance(result, float)

    def test_score_non_negative(self):
        """Distribuzione valida → score >= 0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_SOFT_ONLY,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertGreaterEqual(result, 0.0)

    def test_mixed_distribution_returns_float(self):
        """Distribuzione mista (Soft 70% + Armored 30%) → float >= 0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_MIXED,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)

    # ── Approvazione rotta ────────────────────────────────────────────────────

    def test_excessive_route_speed_returns_zero(self):
        """Velocità rotta irraggiungibile → loadout non approvato → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_CAP, _LOADOUT_CAP, _DIST_SOFT_ONLY,
            ROUTE_LENGTH, 99999.0,
        )
        self.assertEqual(result, 0.0)

    def test_excessive_route_length_returns_zero(self):
        """Lunghezza rotta irraggiungibile → loadout non approvato → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_CAP, _LOADOUT_CAP, _DIST_SOFT_ONLY,
            99999.0, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    # ── Validazione distribuzione: perc_dimension ─────────────────────────────

    def test_missing_perc_dimension_returns_zero(self):
        """Chiave 'perc_dimension' assente nel target type → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_MISSING_DIM,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    def test_perc_dimension_sum_not_one_returns_zero(self):
        """Somma dei valori di perc_dimension != 1.0 → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_DIM_SUM_INVALID,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    # ── Validazione distribuzione: perc_type ─────────────────────────────────

    def test_perc_type_out_of_range_returns_zero(self):
        """perc_type > 1 → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_PERC_TYPE_INVALID,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    def test_perc_type_none_returns_zero(self):
        """Chiave 'perc_type' assente (None) → 0.0."""
        dist = {
            "Soft": {
                "perc_dimension": {"big": 0.2, "med": 0.5, "small": 0.3},
            }
        }
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, dist,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    def test_perc_type_sum_not_one_returns_zero(self):
        """Somma dei perc_type di tutti i target type != 1.0 → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, _DIST_TYPE_SUM_INVALID,
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    def test_empty_distribution_returns_zero(self):
        """Distribuzione vuota → somma perc_type = 0.0 ≠ 1.0 → 0.0."""
        result = loadout_target_effectiveness_by_distribuition(
            _AIRCRAFT_STRIKE, _LOADOUT_STRIKE, {},
            ROUTE_LENGTH, ROUTE_SPEED,
        )
        self.assertEqual(result, 0.0)

    # ── Errori di input ───────────────────────────────────────────────────────

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            loadout_target_effectiveness_by_distribuition(
                "INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, _DIST_SOFT_ONLY,
                ROUTE_LENGTH, ROUTE_SPEED,
            )

    def test_invalid_loadout_raises_ValueError(self):
        """Loadout sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            loadout_target_effectiveness_by_distribuition(
                _AIRCRAFT_CAP, "INVALID_LOADOUT_XYZ", _DIST_SOFT_ONLY,
                ROUTE_LENGTH, ROUTE_SPEED,
            )


class TestLoadoutYearCompatibility(unittest.TestCase):
    """
    Unit test per loadout_year_compatibility(aircraft_name, loadout_name, year).

    La funzione restituisce True se tutte le armi nei pylons del loadout erano
    in servizio entro l'anno specificato, False se almeno una non lo era.

    Logica interna:
      1. Chiama get_loadout() → ValueError per aircraft/loadout sconosciuti.
      2. Itera sui pylons e chiama is_weapon_introduced(weapon_model, year) per
         ciascun'arma → TypeError se year non è int (propagato da is_weapon_introduced).
      3. Restituisce False appena trova un'arma non ancora introdotta, True se
         tutte le armi superano il controllo.

    Store non-arma nei pylons (serbatoi, pod) non sono in AIR_WEAPONS:
      is_weapon_introduced() → False + logger.warning → loadout incompatibile.
      Il logger di Aircraft_Weapon_Data viene mockato per isolare questo side-effect.

    Dati di riferimento (start_service delle armi chiave):
      AIM-54A-MK47 → 1974   AIM-7M  → 1982   GBU-12 → 1970
      AIM-9L       → 1975   AIM-9M  → 1982   Mk-82  → 1954
      267gal_tank  → NON in AIR_WEAPONS (sempre False)

    Loadout usati:
      F-14A "Phoenix Fleet Defense": AIM-54A-MK47, AIM-9L, AIM-7M → compat. da 1982
      F-14A "Sparrow CAP/Escort":   AIM-7M, AIM-9L, 267gal_tank   → sempre False
      F-15E "Laser Strike":         GBU-12, AIM-9M, AIM-7M        → compat. da 1982
      F-15E "Iron Bomb Strike":     Mk-82, AIM-9M                  → compat. da 1982
    """

    def setUp(self):
        # Aircraft_Weapon_Data.logger viene chiamato da is_weapon_introduced()
        # quando trova store non-arma (es. 267gal_tank) non presenti in AIR_WEAPONS.
        self._logger_patcher_wd = patch(_LOGGER_PATH_WD, MagicMock())
        self._logger_patcher_wd.start()

    def tearDown(self):
        self._logger_patcher_wd.stop()

    # ── Propagazione TypeError da year non-int ─────────────────────────────

    def test_type_error_on_str_year(self):
        """year come str → TypeError propagato da is_weapon_introduced."""
        with self.assertRaises(TypeError):
            loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, "1982")

    def test_type_error_on_float_year(self):
        """year come float (anche intero) → TypeError propagato da is_weapon_introduced."""
        with self.assertRaises(TypeError):
            loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 1982.0)

    def test_type_error_on_none_year(self):
        """year None → TypeError propagato da is_weapon_introduced."""
        with self.assertRaises(TypeError):
            loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, None)

    def test_type_error_on_list_year(self):
        """year come lista → TypeError propagato da is_weapon_introduced."""
        with self.assertRaises(TypeError):
            loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, [1982])

    # ── Propagazione ValueError da aircraft/loadout sconosciuti ───────────

    def test_invalid_aircraft_raises_ValueError(self):
        """Aircraft sconosciuto → ValueError da get_loadout."""
        with self.assertRaises(ValueError):
            loadout_year_compatibility("INVALID_AIRCRAFT_XYZ", _LOADOUT_CAP, 2000)

    def test_invalid_loadout_raises_ValueError(self):
        """Loadout sconosciuto → ValueError da get_loadout."""
        with self.assertRaises(ValueError):
            loadout_year_compatibility(_AIRCRAFT_CAP, "INVALID_LOADOUT_XYZ", 2000)

    # ── True: tutte le armi introdotte entro l'anno ────────────────────────

    def test_cap_loadout_compatible_exact_year(self):
        """F-14A 'Phoenix Fleet Defense': anno esatto del missile più recente (AIM-7M: 1982) → True."""
        self.assertTrue(loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 1982))

    def test_cap_loadout_compatible_after_all_weapons(self):
        """F-14A 'Phoenix Fleet Defense': anno 2000, tutte le armi introdotte entro il 1982 → True."""
        self.assertTrue(loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 2000))

    def test_strike_loadout_compatible_exact_year(self):
        """F-15E 'Laser Strike': anno esatto del sistema più recente (AIM-9M/AIM-7M: 1982) → True."""
        self.assertTrue(loadout_year_compatibility(_AIRCRAFT_STRIKE, _LOADOUT_STRIKE, 1982))

    def test_strike_loadout_compatible_after_all_weapons(self):
        """F-15E 'Laser Strike': anno 1990, tutte le armi introdotte entro il 1982 → True."""
        self.assertTrue(loadout_year_compatibility(_AIRCRAFT_STRIKE, _LOADOUT_STRIKE, 1990))

    def test_iron_bomb_compatible_exact_year(self):
        """F-15E 'Iron Bomb Strike': anno 1982 (Mk-82:1954, AIM-9M:1982) → True."""
        self.assertTrue(loadout_year_compatibility(_AIRCRAFT_IRON, _LOADOUT_IRON, 1982))

    def test_iron_bomb_compatible_after_all_weapons(self):
        """F-15E 'Iron Bomb Strike': anno 2000 → True."""
        self.assertTrue(loadout_year_compatibility(_AIRCRAFT_IRON, _LOADOUT_IRON, 2000))

    # ── False: almeno un'arma non ancora introdotta ────────────────────────

    def test_cap_loadout_not_compatible_one_year_before(self):
        """F-14A 'Phoenix Fleet Defense': anno 1981 → AIM-7M (1982) non ancora introdotto → False."""
        self.assertFalse(loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 1981))

    def test_cap_loadout_not_compatible_much_earlier(self):
        """F-14A 'Phoenix Fleet Defense': anno 1970, nessuna arma introdotta → False."""
        self.assertFalse(loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 1970))

    def test_strike_loadout_not_compatible_one_year_before(self):
        """F-15E 'Laser Strike': anno 1981 → AIM-9M/AIM-7M (1982) non ancora introdotti → False."""
        self.assertFalse(loadout_year_compatibility(_AIRCRAFT_STRIKE, _LOADOUT_STRIKE, 1981))

    def test_iron_bomb_not_compatible_one_year_before(self):
        """F-15E 'Iron Bomb Strike': anno 1981 → AIM-9M (1982) non ancora introdotto → False."""
        self.assertFalse(loadout_year_compatibility(_AIRCRAFT_IRON, _LOADOUT_IRON, 1981))

    # ── False: store non-arma nei pylons (serbatoi carburante) ────────────

    def test_loadout_with_fuel_tank_always_false_recent_year(self):
        """F-14A 'Sparrow CAP/Escort': contiene 267gal_tank (non in AIR_WEAPONS)
        → is_weapon_introduced restituisce False → loadout_year_compatibility False,
        anche con anno recente (2000)."""
        self.assertFalse(loadout_year_compatibility(_AIRCRAFT_SPARROW, _LOADOUT_SPARROW, 2000))

    def test_loadout_with_fuel_tank_always_false_exact_weapon_year(self):
        """F-14A 'Sparrow CAP/Escort': anno 1982 (AIM-7M introdotto) ma 267gal_tank
        non è in AIR_WEAPONS → False."""
        self.assertFalse(loadout_year_compatibility(_AIRCRAFT_SPARROW, _LOADOUT_SPARROW, 1982))

    # ── Tipo di ritorno ───────────────────────────────────────────────────

    def test_return_type_is_bool_true_case(self):
        """Il valore restituito è bool (caso True)."""
        result = loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 2000)
        self.assertIsInstance(result, bool)

    def test_return_type_is_bool_false_case(self):
        """Il valore restituito è bool (caso False — anno precedente)."""
        result = loadout_year_compatibility(_AIRCRAFT_CAP, _LOADOUT_CAP, 1981)
        self.assertIsInstance(result, bool)


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in (
        TestGetAircraftLoadouts,
        TestGetAircraftLoadoutsByTask,
        TestGetLoadout,
        TestGetLoadoutTasks,
        TestGetLoadoutAttributes,
        TestEvaluateLoadoutUsability,
        TestEvaluateLoadoutSupportRequirements,
        TestEvaluateLoadoutRange,
        TestEvaluateLoadoutSpeed,
        TestEvaluateLoadoutAltitude,
        TestLoadoutEval,
        TestLoadoutTargetEffectiveness,
        TestLoadoutTargetEffectivenessByDistribution,
        TestLoadoutYearCompatibility,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def _run_tables_terminal() -> None:
    print("\n" + "=" * 70)
    print("  TABELLE PUNTEGGIO LOADOUT — loadout_eval()")
    print("=" * 70)
    print_loadout_eval_tables(LOADOUT_TASKS)

    print("\n" + "=" * 70)
    print("  TABELLE PUNTEGGIO LOADOUT vs BERSAGLIO — loadout_target_effectiveness()")
    print("=" * 70)
    print_loadout_target_eff_tables(
        LOADOUT_TASKS, TARGET_TYPE_LIST, TARGET_DIMENSION_LIST,
        ROUTE_LENGTH, ROUTE_SPEED,
    )


def _run_tables_pdf() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_loadout_eval_pdf(
        LOADOUT_TASKS,
        os.path.join(OUTPUT_DIR, "loadout_eval_tables.pdf"),
    )
    save_loadout_target_eff_pdf(
        LOADOUT_TASKS,
        TARGET_TYPE_LIST, TARGET_DIMENSION_LIST,
        ROUTE_LENGTH, ROUTE_SPEED,
        os.path.join(OUTPUT_DIR, "loadout_target_eff_tables.pdf"),
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
    print("║       Test_Aircraft_Loadouts  —  Menu principale            ║")
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
    """Ciclo principale del menu interattivo."""
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
    _interactive_menu()
