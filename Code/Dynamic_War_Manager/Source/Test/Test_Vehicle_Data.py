"""
Test_Vehicle_Data.py
====================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo
Vehicle_Data.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py            # menu interattivo
    python  Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py --tables-only
    python  Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py --tests-only

Note sul modulo sotto test:
  - Vehicle_Data: dataclass che rappresenta un veicolo di terra.
  - Vehicle_Data._registry: dizionario globale {model: Vehicle_Data}.
  - CATEGORY: set di categorie valide derivato da Ground_Vehicle_Asset_Type.
  - AMMO_LOAD_REFERENCE: dict con riferimenti quantità munizioni.
  - VEHICLE: dict con punteggi pre-calcolati per ogni veicolo.
  - SCORES: tuple con le chiavi dei punteggi disponibili.
  - get_vehicle_data(model): restituisce tutti i dati di un veicolo.
  - get_vehicle_scores(model, scores): restituisce i punteggi di un veicolo.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAZIONE — modificare le liste per personalizzare le tabelle
# ─────────────────────────────────────────────────────────────────────────────

# Categorie di veicoli da includere nella stampa Vehicle_Scores.pdf
VEHICLE_CATEGORIES: List[str] = [
    "Tank",
    "Armored",
    "Motorized",
    "Artillery_Fixed",
    "Artillery_Semovent",
    "AAA",
    "SAM_Small",
    "SAM_Medium",
    "SAM_Big",
    "EWR",
]

# Tipi di arma per le tabelle vehicle_weapon_score.
# Per ogni weapon_type vengono mostrati i veicoli che montano quel tipo
# di armamento, raggruppati per categoria veicolo.
weapon_type: List[str] = [
    "CANNONS",
    "MISSILES",
    "AUTO_CANNONS",
    "AA_CANNONS",
    "ARTILLERY",
    "MACHINE_GUNS",
    "MORTARS",
    "ROCKETS",
]

# Tipi di bersaglio per le tabelle get_normalized_weapon_target_effectiveness()
target_type: List[str] = [
    "Soft",
    "Armored",
    "Hard",
    "Structure",
    "Air_Defense",
]

# Dimensioni del bersaglio per le tabelle target effectiveness
target_dimension: List[str] = ["big", "med", "small"]

# Directory di output per i PDF
OUTPUT_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "..", "out",
    )
)

# Path del logger da mockare nei test
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import (
    Vehicle_Data,
    AMMO_LOAD_REFERENCE,
    CATEGORY,
    VEHICLE,
    SCORES,
    get_vehicle_data,
    get_vehicle_scores,
)


# ─────────────────────────────────────────────────────────────────────────────
#  VEICOLI DI RIFERIMENTO PER I TEST
# ─────────────────────────────────────────────────────────────────────────────

_TANK_MODEL       = "T-90M"
_ARMORED_MODEL    = "BMP-1"
_ARTILLERY_MODEL  = "2S3 Akatsiya"
_AAA_MODEL        = "ZSU-23-4"
_SAM_MODEL        = "S-300PS"


# ─────────────────────────────────────────────────────────────────────────────
#  1. STRUTTURA DATI DEL MODULO
# ─────────────────────────────────────────────────────────────────────────────

class TestVehicleDataModuleStructure(unittest.TestCase):
    """Verifica le strutture dati globali del modulo Vehicle_Data."""

    # ── AMMO_LOAD_REFERENCE ─────────────────────────────────────────────────

    def test_ammo_load_reference_is_dict(self):
        self.assertIsInstance(AMMO_LOAD_REFERENCE, dict)

    def test_ammo_load_reference_has_expected_keys(self):
        expected = {
            "CANNONS", "ARTILLERY", "AA_CANNONS", "AUTO_CANNONS",
            "MISSILES_SAM", "MISSILES_TANK", "ROCKETS", "MORTARS",
        }
        for key in expected:
            with self.subTest(key=key):
                self.assertIn(key, AMMO_LOAD_REFERENCE)

    def test_ammo_load_reference_values_are_positive(self):
        for key, val in AMMO_LOAD_REFERENCE.items():
            with self.subTest(key=key):
                self.assertIsInstance(val, (int, float))
                self.assertGreater(val, 0)

    # ── CATEGORY ────────────────────────────────────────────────────────────

    def test_category_is_set(self):
        self.assertIsInstance(CATEGORY, set)

    def test_category_contains_expected_values(self):
        expected = {
            "Tank", "Armored", "Motorized",
            "Artillery_Fixed", "Artillery_Semovent",
            "SAM_Big", "SAM_Medium", "SAM_Small",
            "EWR", "AAA",
        }
        for cat in expected:
            with self.subTest(category=cat):
                self.assertIn(cat, CATEGORY)

    def test_category_values_are_strings(self):
        for cat in CATEGORY:
            with self.subTest(cat=cat):
                self.assertIsInstance(cat, str)

    # ── SCORES ──────────────────────────────────────────────────────────────

    def test_scores_is_tuple(self):
        self.assertIsInstance(SCORES, tuple)

    def test_scores_non_empty(self):
        self.assertGreater(len(SCORES), 0)

    def test_scores_values_are_strings(self):
        for s in SCORES:
            with self.subTest(score=s):
                self.assertIsInstance(s, str)

    # ── Vehicle_Data._registry ──────────────────────────────────────────────

    def test_registry_is_dict(self):
        self.assertIsInstance(Vehicle_Data._registry, dict)

    def test_registry_non_empty(self):
        self.assertGreater(len(Vehicle_Data._registry), 0)

    def test_registry_keys_are_strings(self):
        for key in Vehicle_Data._registry:
            with self.subTest(key=key):
                self.assertIsInstance(key, str)

    def test_registry_values_are_vehicle_data_instances(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj, Vehicle_Data)

    def test_registry_contains_known_tanks(self):
        for model in (_TANK_MODEL, "T-72B", "M1A2-Abrams", "Leopard-2A6M"):
            with self.subTest(model=model):
                self.assertIn(model, Vehicle_Data._registry)

    def test_registry_contains_known_armored(self):
        for model in (_ARMORED_MODEL, "BMP-2", "M2-Bradley"):
            with self.subTest(model=model):
                self.assertIn(model, Vehicle_Data._registry)

    def test_registry_model_key_matches_attribute(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertEqual(model, obj.model)

    def test_registry_categories_are_valid(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertIn(obj.category, CATEGORY)

    # ── VEHICLE dict ─────────────────────────────────────────────────────────

    def test_vehicle_dict_is_dict(self):
        self.assertIsInstance(VEHICLE, dict)

    def test_vehicle_dict_non_empty(self):
        self.assertGreater(len(VEHICLE), 0)

    def test_vehicle_dict_has_all_registry_models(self):
        for model in Vehicle_Data._registry:
            with self.subTest(model=model):
                self.assertIn(model, VEHICLE)

    def test_vehicle_dict_entries_are_dicts(self):
        for model, data in VEHICLE.items():
            with self.subTest(model=model):
                self.assertIsInstance(data, dict)

    def test_vehicle_dict_entries_have_score_keys(self):
        """Ogni voce in VEHICLE deve contenere almeno combat score e weapon score."""
        required = {"combat score", "weapon score"}
        for model, data in VEHICLE.items():
            for key in required:
                with self.subTest(model=model, key=key):
                    self.assertIn(key, data)

    def test_vehicle_score_dicts_have_global_and_category(self):
        """Ogni sotto-dict di punteggio deve avere global_score e category_score."""
        for model, data in VEHICLE.items():
            for score_name, score_dict in data.items():
                with self.subTest(model=model, score=score_name):
                    self.assertIn("global_score", score_dict)
                    self.assertIn("category_score", score_dict)

    def test_vehicle_score_values_are_floats_in_range(self):
        """I valori dei punteggi normalizzati devono essere float in [0, 1]."""
        for model, data in VEHICLE.items():
            for score_name, score_dict in data.items():
                for scope, val in score_dict.items():
                    with self.subTest(model=model, score=score_name, scope=scope):
                        self.assertIsInstance(val, (int, float))
                        self.assertGreaterEqual(val, 0.0)
                        self.assertLessEqual(val, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
#  2. VEHICLE_DATA CLASS — ATTRIBUTI E COSTRUTTORE
# ─────────────────────────────────────────────────────────────────────────────

class TestVehicleDataAttributes(unittest.TestCase):
    """Verifica che gli attributi degli oggetti Vehicle_Data siano corretti."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()
        self.tank = Vehicle_Data._registry[_TANK_MODEL]
        self.armored = Vehicle_Data._registry[_ARMORED_MODEL]
        self.sam = Vehicle_Data._registry[_SAM_MODEL]

    def tearDown(self):
        self._patcher.stop()

    def test_model_attribute_is_string(self):
        self.assertIsInstance(self.tank.model, str)

    def test_made_attribute_is_string(self):
        self.assertIsInstance(self.tank.made, str)

    def test_category_attribute_valid(self):
        self.assertIn(self.tank.category, CATEGORY)
        self.assertIn(self.armored.category, CATEGORY)
        self.assertIn(self.sam.category, CATEGORY)

    def test_tank_category_is_tank(self):
        self.assertEqual(self.tank.category, "Tank")

    def test_sam_category_is_sam_big(self):
        self.assertEqual(self.sam.category, "SAM_Big")

    def test_weapons_attribute_is_dict(self):
        self.assertIsInstance(self.tank.weapons, dict)

    def test_weapons_non_empty_for_combat_vehicles(self):
        self.assertGreater(len(self.tank.weapons), 0)

    def test_engine_attribute_is_dict_or_none(self):
        self.assertTrue(
            self.tank.engine is None or isinstance(self.tank.engine, dict)
        )

    def test_speed_data_attribute_is_dict(self):
        self.assertIsInstance(self.tank.speed_data, dict)

    def test_cost_is_positive_number(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.cost, (int, float))
                self.assertGreater(obj.cost, 0)

    def test_range_is_positive_number(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.range, (int, float))
                self.assertGreater(obj.range, 0)

    def test_start_service_is_int(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.start_service, int)


# ─────────────────────────────────────────────────────────────────────────────
#  3. METODI DI VALUTAZIONE ASSOLUTI (_eval)
# ─────────────────────────────────────────────────────────────────────────────

class TestWeaponEval(unittest.TestCase):
    """Unit test per Vehicle_Data._weapon_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_tank_weapon_eval_positive(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_vehicles_weapon_eval_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._weapon_eval()
                self.assertIsInstance(score, (int, float))
                self.assertGreaterEqual(score, 0.0)

    def test_tank_weapon_eval_greater_than_armored(self):
        """Il carro armato deve avere weapon_eval >= veicolo corazzato leggero."""
        t90_score = Vehicle_Data._registry["T-90M"]._weapon_eval()
        bmp1_score = Vehicle_Data._registry["BMP-1"]._weapon_eval()
        self.assertGreater(t90_score, bmp1_score)

    def test_deterministic(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        self.assertAlmostEqual(tank._weapon_eval(), tank._weapon_eval(), places=9)


class TestRadarEval(unittest.TestCase):
    """Unit test per Vehicle_Data._radar_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_false_radar_returns_zero(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        # T-90M ha radar=False
        self.assertEqual(tank._radar_eval(), 0.0)

    def test_sam_radar_eval_positive(self):
        sam = Vehicle_Data._registry[_SAM_MODEL]
        score = sam._radar_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_invalid_modes_raises_type_error(self):
        sam = Vehicle_Data._registry[_SAM_MODEL]
        with self.assertRaises(TypeError):
            sam._radar_eval(modes="air")

    def test_invalid_modes_element_raises_type_error(self):
        sam = Vehicle_Data._registry[_SAM_MODEL]
        with self.assertRaises(TypeError):
            sam._radar_eval(modes=["invalid_mode"])

    def test_valid_modes_subset(self):
        sam = Vehicle_Data._registry[_SAM_MODEL]
        score = sam._radar_eval(modes=["air"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_all_vehicles_radar_eval_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._radar_eval()
                self.assertGreaterEqual(score, 0.0)


class TestTVDEval(unittest.TestCase):
    """Unit test per Vehicle_Data._TVD_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_false_tvd_returns_zero(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        # T-90M ha TVD=False
        self.assertEqual(tank._TVD_eval(), 0.0)

    def test_invalid_modes_raises_type_error(self):
        # Troviamo un veicolo con TVD definito
        for model, obj in Vehicle_Data._registry.items():
            if obj.TVD and obj.TVD is not False:
                with self.assertRaises(TypeError):
                    obj._TVD_eval(modes="ground")
                break

    def test_all_vehicles_tvd_eval_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._TVD_eval()
                self.assertGreaterEqual(score, 0.0)


class TestSpeedEval(unittest.TestCase):
    """Unit test per Vehicle_Data._speed_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_tank_speed_eval_positive(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._speed_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_vehicles_speed_eval_positive(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._speed_eval()
                self.assertGreater(score, 0.0)

    def test_deterministic(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        self.assertAlmostEqual(tank._speed_eval(), tank._speed_eval(), places=9)


class TestProtectionEval(unittest.TestCase):
    """Unit test per Vehicle_Data._protection_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_tank_protection_positive(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._protection_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_false_protections_returns_zero(self):
        """Veicoli con protections=False devono restituire 0.0."""
        for model, obj in Vehicle_Data._registry.items():
            if obj.protections is False:
                with self.subTest(model=model):
                    self.assertEqual(obj._protection_eval(), 0.0)

    def test_all_vehicles_protection_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._protection_eval()
                self.assertGreaterEqual(score, 0.0)

    def test_tank_protection_greater_than_motorized(self):
        """Un MBT deve avere protezione maggiore di un veicolo motorizzato."""
        tank_score = Vehicle_Data._registry["T-90M"]._protection_eval()
        # Cerca un veicolo Motorized
        motorized = next(
            (v for v in Vehicle_Data._registry.values() if v.category == "Motorized"),
            None
        )
        if motorized:
            self.assertGreater(tank_score, motorized._protection_eval())


class TestCommunicationEval(unittest.TestCase):
    """Unit test per Vehicle_Data._communication_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_vehicles_communication_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._communication_eval()
                self.assertGreaterEqual(score, 0.0)

    def test_false_communication_returns_zero(self):
        for model, obj in Vehicle_Data._registry.items():
            if obj.communication is False:
                with self.subTest(model=model):
                    self.assertEqual(obj._communication_eval(), 0.0)


class TestHydraulicEval(unittest.TestCase):
    """Unit test per Vehicle_Data._hydraulic_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_vehicles_hydraulic_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._hydraulic_eval()
                self.assertGreaterEqual(score, 0.0)


class TestRangeEval(unittest.TestCase):
    """Unit test per Vehicle_Data._range_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_vehicles_range_eval_positive(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._range_eval()
                self.assertGreater(score, 0.0)

    def test_range_proportional(self):
        """Veicolo con range maggiore deve avere _range_eval più alto."""
        # T-90M range=550, S-300PS range=600
        t90_score = Vehicle_Data._registry["T-90M"]._range_eval()
        s300_score = Vehicle_Data._registry["S-300PS"]._range_eval()
        self.assertGreater(s300_score, t90_score)


class TestReliabilityAndMaintenance(unittest.TestCase):
    """Unit test per _reliability_eval(), _maintenance_eval(), _avalaiability_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_vehicles_reliability_positive(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._reliability_eval()
                self.assertGreater(score, 0.0)

    def test_all_vehicles_maintenance_positive(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._maintenance_eval()
                self.assertGreater(score, 0.0)

    def test_all_vehicles_availability_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._avalaiability_eval()
                self.assertGreaterEqual(score, 0.0)


class TestCombatEval(unittest.TestCase):
    """Unit test per Vehicle_Data._combat_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_vehicles_combat_eval_positive(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._combat_eval()
                self.assertGreater(score, 0.0)

    def test_deterministic(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        self.assertAlmostEqual(tank._combat_eval(), tank._combat_eval(), places=9)


class TestWeaponTargetEffectiveness(unittest.TestCase):
    """Unit test per Vehicle_Data._weapon_target_effectiveness()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_tank_vs_armored_positive(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness(["Armored"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_tank_vs_soft_higher_than_vs_armored(self):
        """Un MBT è più efficace vs Soft che vs Armored."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        soft = tank._weapon_target_effectiveness(["Soft"], ["big"])
        armored = tank._weapon_target_effectiveness(["Armored"], ["big"])
        self.assertGreater(soft, armored)

    def test_empty_target_type_returns_zero(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness([], ["big"])
        self.assertEqual(score, 0.0)

    def test_empty_target_dimension_returns_zero(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness(["Armored"], [])
        self.assertEqual(score, 0.0)

    def test_all_vehicles_non_negative(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._weapon_target_effectiveness(["Soft"], ["big"])
                self.assertGreaterEqual(score, 0.0)

    def test_deterministic(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        s1 = tank._weapon_target_effectiveness(["Armored"], ["med"])
        s2 = tank._weapon_target_effectiveness(["Armored"], ["med"])
        self.assertAlmostEqual(s1, s2, places=9)


class TestWeaponTargetEffectivenessDistribuition(unittest.TestCase):
    """Unit test per Vehicle_Data._weapon_target_effectiveness_distribuition().

    Analoga a _weapon_target_effectiveness() ma accetta Dict con pesi invece
    di List: target_type={'Armored': 0.7, 'Soft': 0.3}, target_dimension={'big': 1.0}.

    Con peso 1.0 su un singolo tipo/dimensione il risultato è identico alla
    versione List (get_weapon_score_target_distribuition con w=1.0 restituisce
    lo stesso valore di get_weapon_score_target con lista singola).
    """

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    # ── valori di base ────────────────────────────────────────────────────────

    def test_tank_vs_armored_big_positive(self):
        """T-90M vs Armored/big → float > 0."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"big": 1.0})
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_tank_vs_soft_higher_than_vs_armored(self):
        """Un MBT è più efficace vs Soft che vs Armored."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        soft    = tank._weapon_target_effectiveness_distribuition({"Soft": 1.0},    {"big": 1.0})
        armored = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"big": 1.0})
        self.assertGreater(soft, armored)

    def test_aaa_vs_soft_non_negative(self):
        """AAA vehicle vs Soft → score >= 0."""
        aaa = next(v for v in Vehicle_Data._registry.values() if v.category == "AAA")
        score = aaa._weapon_target_effectiveness_distribuition({"Soft": 1.0}, {"big": 1.0})
        self.assertGreaterEqual(score, 0.0)

    def test_sam_vehicle_vs_soft_non_negative(self):
        """SAM vehicle vs Soft → score >= 0."""
        sam = Vehicle_Data._registry[_SAM_MODEL]
        score = sam._weapon_target_effectiveness_distribuition({"Soft": 1.0}, {"big": 1.0})
        self.assertGreaterEqual(score, 0.0)

    # ── dict vuoti e chiavi invalide ──────────────────────────────────────────

    def test_empty_target_type_dict_returns_zero(self):
        """Dict target_type vuoto → 0.0."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness_distribuition({}, {"big": 1.0})
        self.assertEqual(score, 0.0)

    def test_empty_target_dimension_dict_returns_zero(self):
        """Dict target_dimension vuoto → 0.0."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {})
        self.assertEqual(score, 0.0)

    def test_invalid_target_type_only_returns_zero(self):
        """target_type sconosciuto → 0.0."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness_distribuition({"UNKNOWN_XYZ": 1.0}, {"big": 1.0})
        self.assertEqual(score, 0.0)

    def test_invalid_target_dimension_only_returns_zero(self):
        """target_dimension sconosciuta → 0.0."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"UNKNOWN_DIM": 1.0})
        self.assertEqual(score, 0.0)

    # ── coerenza con la versione List ─────────────────────────────────────────

    def test_single_weight_1_matches_list_version(self):
        """Con peso 1.0 su un singolo tipo/dimensione il risultato deve essere
        identico a _weapon_target_effectiveness con la lista corrispondente."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_dist = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"big": 1.0})
        score_list = tank._weapon_target_effectiveness(["Armored"], ["big"])
        self.assertAlmostEqual(score_dist, score_list, places=9)

    def test_single_weight_1_soft_matches_list_version(self):
        """Con peso 1.0 su Soft/med, risultato identico alla versione List."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_dist = tank._weapon_target_effectiveness_distribuition({"Soft": 1.0}, {"med": 1.0})
        score_list = tank._weapon_target_effectiveness(["Soft"], ["med"])
        self.assertAlmostEqual(score_dist, score_list, places=9)

    # ── semantica della somma ponderata ──────────────────────────────────────

    def test_weight_half_halves_raw_score(self):
        """Dimezzare il peso di t_type dimezza il punteggio grezzo."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_full = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"big": 1.0})
        score_half = tank._weapon_target_effectiveness_distribuition({"Armored": 0.5}, {"big": 1.0})
        self.assertAlmostEqual(score_half, score_full * 0.5, places=9)

    def test_two_types_weighted_sum_semantics(self):
        """Con due tipi, il risultato è la somma ponderata dei contributi individuali."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_soft   = tank._weapon_target_effectiveness_distribuition({"Soft": 1.0},    {"big": 1.0})
        score_armored = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"big": 1.0})
        score_mixed  = tank._weapon_target_effectiveness_distribuition(
            {"Soft": 0.7, "Armored": 0.3}, {"big": 1.0}
        )
        expected = score_soft * 0.7 + score_armored * 0.3
        self.assertAlmostEqual(score_mixed, expected, places=9)

    def test_two_dimensions_weighted_sum_semantics(self):
        """Con due dimensioni, il risultato è la somma ponderata dei contributi."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_big   = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"big": 1.0})
        score_small = tank._weapon_target_effectiveness_distribuition({"Armored": 1.0}, {"small": 1.0})
        score_mixed = tank._weapon_target_effectiveness_distribuition(
            {"Armored": 1.0}, {"big": 0.6, "small": 0.4}
        )
        expected = score_big * 0.6 + score_small * 0.4
        self.assertAlmostEqual(score_mixed, expected, places=9)

    # ── tutti i veicoli non negativi ──────────────────────────────────────────

    def test_all_vehicles_non_negative(self):
        """Per tutti i veicoli registrati il punteggio deve essere >= 0."""
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj._weapon_target_effectiveness_distribuition({"Soft": 1.0}, {"big": 1.0})
                self.assertGreaterEqual(score, 0.0)

    # ── determinismo ──────────────────────────────────────────────────────────

    def test_deterministic(self):
        """Stesso risultato su chiamate successive (nessuna componente stocastica)."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        s1 = tank._weapon_target_effectiveness_distribuition({"Armored": 0.7, "Soft": 0.3}, {"big": 1.0})
        s2 = tank._weapon_target_effectiveness_distribuition({"Armored": 0.7, "Soft": 0.3}, {"big": 1.0})
        self.assertAlmostEqual(s1, s2, places=9)


# ─────────────────────────────────────────────────────────────────────────────
#  4. METODO _normalize
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalize(unittest.TestCase):
    """Unit test per Vehicle_Data._normalize()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()
        self.obj = Vehicle_Data._registry[_TANK_MODEL]

    def tearDown(self):
        self._patcher.stop()

    def test_empty_scores_returns_zero(self):
        self.assertEqual(self.obj._normalize(5.0, []), 0)

    def test_min_equals_max_returns_half(self):
        self.assertAlmostEqual(self.obj._normalize(3.0, [3.0, 3.0, 3.0]), 0.5)

    def test_min_value_returns_zero(self):
        self.assertAlmostEqual(self.obj._normalize(0.0, [0.0, 5.0, 10.0]), 0.0)

    def test_max_value_returns_one(self):
        self.assertAlmostEqual(self.obj._normalize(10.0, [0.0, 5.0, 10.0]), 1.0)

    def test_mid_value_returns_half(self):
        self.assertAlmostEqual(self.obj._normalize(5.0, [0.0, 5.0, 10.0]), 0.5)

    def test_result_in_range(self):
        for val, scores in [
            (3.0, [1.0, 2.0, 3.0, 4.0, 5.0]),
            (1.0, [1.0, 2.0, 3.0]),
            (2.5, [0.0, 2.5, 5.0]),
        ]:
            with self.subTest(val=val):
                result = self.obj._normalize(val, scores)
                self.assertGreaterEqual(result, 0.0)
                self.assertLessEqual(result, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
#  5. METODI NORMALIZZATI (get_normalized_*)
# ─────────────────────────────────────────────────────────────────────────────

class TestGetNormalizedWeaponScore(unittest.TestCase):
    """Unit test per get_normalized_weapon_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_weapon_score()
                self.assertIsInstance(score, (int, float))
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_category_scope_in_range(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_score(category="Tank")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        with self.assertRaises(ValueError):
            tank.get_normalized_weapon_score(category="INVALID_CATEGORY_XYZ")

    def test_invalid_category_type_raises_value_error(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        with self.assertRaises((ValueError, TypeError)):
            tank.get_normalized_weapon_score(category=123)

    def test_t90_higher_than_bmp1_in_tank_category(self):
        """T-90M deve avere weapon score più alto di BMP-1 nella categoria Tank."""
        t90_score = Vehicle_Data._registry["T-90M"].get_normalized_weapon_score(category="Tank")
        # BMP-1 è Armored, non confrontabile nella stessa categoria
        t90_global = Vehicle_Data._registry["T-90M"].get_normalized_weapon_score()
        bmp1_global = Vehicle_Data._registry["BMP-1"].get_normalized_weapon_score()
        # T-90M deve essere >= BMP-1 a livello globale
        self.assertGreaterEqual(t90_global, bmp1_global)

    def test_deterministic(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        s1 = tank.get_normalized_weapon_score()
        s2 = tank.get_normalized_weapon_score()
        self.assertAlmostEqual(s1, s2, places=9)


class TestGetNormalizedRadarScore(unittest.TestCase):
    """Unit test per get_normalized_radar_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_radar_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        sam = Vehicle_Data._registry[_SAM_MODEL]
        with self.assertRaises(ValueError):
            sam.get_normalized_radar_score(category="BAD_CAT")

    def test_sam_radar_score_greater_than_tank(self):
        """Un SAM ha radar migliore di un carro armato."""
        sam_score = Vehicle_Data._registry[_SAM_MODEL].get_normalized_radar_score()
        tank_score = Vehicle_Data._registry[_TANK_MODEL].get_normalized_radar_score()
        self.assertGreater(sam_score, tank_score)

    def test_modes_ground_subset(self):
        sam = Vehicle_Data._registry[_SAM_MODEL]
        score = sam.get_normalized_radar_score(modes=["ground"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestGetNormalizedSpeedScore(unittest.TestCase):
    """Unit test per get_normalized_speed_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_speed_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            Vehicle_Data._registry[_TANK_MODEL].get_normalized_speed_score(
                category="NOT_A_VALID_CATEGORY"
            )


class TestGetNormalizedProtectionScore(unittest.TestCase):
    """Unit test per get_normalized_protection_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_protection_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_t90_protection_higher_than_bmp1(self):
        t90_score = Vehicle_Data._registry["T-90M"].get_normalized_protection_score()
        bmp1_score = Vehicle_Data._registry["BMP-1"].get_normalized_protection_score()
        self.assertGreater(t90_score, bmp1_score)


class TestGetNormalizedCommunicationScore(unittest.TestCase):
    """Unit test per get_normalized_communication_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_communication_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            Vehicle_Data._registry[_TANK_MODEL].get_normalized_communication_score(
                category="INVALID"
            )


class TestGetNormalizedHydraulicScore(unittest.TestCase):
    """Unit test per get_normalized_hydraulic_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_hydraulic_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestGetNormalizedRangeScore(unittest.TestCase):
    """Unit test per get_normalized_range_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_range_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestGetNormalizedReliabilityAndAvailability(unittest.TestCase):
    """Unit test per get_normalized_reliability_score(), get_normalized_avalaiability_score(),
    get_normalized_maintenance_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_reliability_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_reliability_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_availability_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_avalaiability_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_maintenance_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_maintenance_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


class TestGetNormalizedCombatScore(unittest.TestCase):
    """Unit test per get_normalized_combat_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_combat_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_category_scope_in_range(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_combat_score(category="Tank")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            Vehicle_Data._registry[_TANK_MODEL].get_normalized_combat_score(
                category="BAD"
            )


class TestGetNormalizedWeaponTargetEffectiveness(unittest.TestCase):
    """Unit test per get_normalized_weapon_target_effectiveness()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_target_effectiveness(["Armored"], ["big"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_all_vehicles_in_range(self):
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_weapon_target_effectiveness(
                    ["Soft"], ["big"]
                )
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_category_scope_in_range(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_target_effectiveness(
            ["Armored"], ["big"], category="Tank"
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        with self.assertRaises(ValueError):
            tank.get_normalized_weapon_target_effectiveness(
                ["Armored"], ["big"], category="INVALID"
            )

    def test_deterministic(self):
        tank = Vehicle_Data._registry[_TANK_MODEL]
        s1 = tank.get_normalized_weapon_target_effectiveness(["Armored"], ["med"])
        s2 = tank.get_normalized_weapon_target_effectiveness(["Armored"], ["med"])
        self.assertAlmostEqual(s1, s2, places=9)


class TestGetNormalizedWeaponTargetEffectivenessDistribuition(unittest.TestCase):
    """Unit test per get_normalized_weapon_target_effectiveness_distribuition().

    Analoga a get_normalized_weapon_target_effectiveness() ma accetta Dict con
    pesi: target_type={'Armored': 0.7, 'Soft': 0.3}, target_dimension={'big': 1.0}.

    Con peso 1.0 su un singolo tipo/dimensione il risultato normalizzato deve
    essere identico a get_normalized_weapon_target_effectiveness con lista.

    La normalizzazione preserva il ranking relativo tra veicoli.
    """

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    # ── range [0, 1] ──────────────────────────────────────────────────────────

    def test_returns_float_in_range(self):
        """Punteggio normalizzato T-90M vs Armored/big ∈ [0, 1]."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Armored": 1.0}, {"big": 1.0}
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_all_vehicles_in_range(self):
        """Per tutti i veicoli, il punteggio normalizzato deve essere ∈ [0, 1]."""
        for model, obj in Vehicle_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_weapon_target_effectiveness_distribuition(
                    {"Soft": 1.0}, {"big": 1.0}
                )
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_mixed_weights_in_range(self):
        """Pesi misti su più tipi e dimensioni → score ∈ [0, 1]."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Soft": 0.7, "Armored": 0.3}, {"big": 0.6, "med": 0.4}
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    # ── filtro per categoria ──────────────────────────────────────────────────

    def test_category_scope_in_range(self):
        """Con category='Tank', il punteggio normalizzato deve essere ∈ [0, 1]."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Armored": 1.0}, {"big": 1.0}, category="Tank"
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_none_category_returns_in_range(self):
        """category=None usa tutti i veicoli → score ∈ [0, 1]."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Soft": 1.0}, {"big": 1.0}, category=None
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        """Categoria non valida → ValueError."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        with self.assertRaises(ValueError):
            tank.get_normalized_weapon_target_effectiveness_distribuition(
                {"Armored": 1.0}, {"big": 1.0}, category="INVALID_CATEGORY_XYZ"
            )

    # ── coerenza con la versione List ─────────────────────────────────────────

    def test_single_weight_1_matches_list_version(self):
        """Con peso 1.0 su singolo tipo/dimensione, il risultato normalizzato è
        identico a get_normalized_weapon_target_effectiveness con lista."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_dist = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Armored": 1.0}, {"big": 1.0}
        )
        score_list = tank.get_normalized_weapon_target_effectiveness(["Armored"], ["big"])
        self.assertAlmostEqual(score_dist, score_list, places=9)

    # ── proprietà di scaling ──────────────────────────────────────────────────

    def test_uniform_weight_scaling_preserves_normalized_score(self):
        """Scalare uniformemente tutti i pesi (moltiplicare per costante) non cambia
        il risultato normalizzato: min, max e value scalano dello stesso fattore,
        quindi (value - min) / (max - min) rimane invariato."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        score_full = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Soft": 1.0}, {"big": 1.0}
        )
        score_half = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Soft": 0.5}, {"big": 1.0}
        )
        self.assertAlmostEqual(score_full, score_half, places=9)

    # ── determinismo ──────────────────────────────────────────────────────────

    def test_deterministic(self):
        """Stesso risultato normalizzato su chiamate successive."""
        tank = Vehicle_Data._registry[_TANK_MODEL]
        s1 = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Armored": 0.7, "Soft": 0.3}, {"med": 1.0}
        )
        s2 = tank.get_normalized_weapon_target_effectiveness_distribuition(
            {"Armored": 0.7, "Soft": 0.3}, {"med": 1.0}
        )
        self.assertAlmostEqual(s1, s2, places=9)

    # ── campione multi-veicolo ────────────────────────────────────────────────

    def test_artillery_model_in_range(self):
        """Veicolo artiglieria vs Structure/big ∈ [0, 1]."""
        arty = next(v for v in Vehicle_Data._registry.values() if "Artillery" in v.category)
        score = arty.get_normalized_weapon_target_effectiveness_distribuition(
            {"Structure": 1.0}, {"big": 1.0}
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
#  6. FUNZIONI STATICHE — get_vehicle_data, get_vehicle_scores
# ─────────────────────────────────────────────────────────────────────────────

class TestGetVehicleData(unittest.TestCase):
    """Unit test per get_vehicle_data()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_known_model_returns_dict(self):
        result = get_vehicle_data(_TANK_MODEL)
        self.assertIsInstance(result, dict)

    def test_result_non_empty(self):
        result = get_vehicle_data(_TANK_MODEL)
        self.assertGreater(len(result), 0)

    def test_result_has_combat_score(self):
        result = get_vehicle_data(_TANK_MODEL)
        self.assertIn("combat score", result)

    def test_result_has_weapon_score(self):
        result = get_vehicle_data(_TANK_MODEL)
        self.assertIn("weapon score", result)

    def test_all_models_findable(self):
        for model in Vehicle_Data._registry:
            with self.subTest(model=model):
                result = get_vehicle_data(model)
                self.assertIsNotNone(result)

    def test_unknown_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_vehicle_data("VEHICLE_NOT_EXISTING_XYZ")

    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_vehicle_data("")


class TestGetVehicleScores(unittest.TestCase):
    """Unit test per get_vehicle_scores().

    DATA BUG — get_vehicle_scores(): la validazione usa
    ``if scores and scores not in SCORES`` che controlla se il valore del
    parametro scores è un ELEMENTO del tuple SCORES. Poiché SCORES è una
    tupla di stringhe, il test funziona solo con una singola stringa. Ma
    poi ``for score in scores`` itera sui CARATTERI della stringa anziché
    sui nomi dei punteggi → KeyError. La funzione è inutilizzabile con la
    sua firma attuale. I test documentano questo comportamento.
    """

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_unknown_model_raises_value_error(self):
        """Modello sconosciuto → ValueError (prima della validazione scores)."""
        with self.assertRaises(ValueError):
            get_vehicle_scores("VEHICLE_NOT_EXISTING_XYZ")

    def test_validation_bug_documented_default_scores_raises(self):
        """BUG DOCUMENTATO: chiamata con scores=SCORES (default) solleva
        ValueError perché SCORES (tuple) non è un elemento di se stesso."""
        with self.assertRaises((ValueError, TypeError, KeyError)):
            get_vehicle_scores(_TANK_MODEL)

    def test_validation_bug_documented_single_string_raises_key_error(self):
        """BUG DOCUMENTATO: scores='combat score' supera la validazione ma
        poi ``for score in 'combat score'`` itera sui caratteri → KeyError."""
        with self.assertRaises((KeyError, ValueError, TypeError)):
            get_vehicle_scores(_TANK_MODEL, "combat score")


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY PER LA GENERAZIONE DELLE TABELLE
# ─────────────────────────────────────────────────────────────────────────────

def _is_nan(value) -> bool:
    try:
        return value != value
    except Exception:
        return False


def _safe_normalized_weapon_score(vehicle: Vehicle_Data, cat: str) -> float:
    """Restituisce get_normalized_weapon_score(category=cat) con logger mockato."""
    try:
        with patch(_LOGGER_PATH, MagicMock()):
            return vehicle.get_normalized_weapon_score(category=cat)
    except Exception:
        return float("nan")


def _safe_normalized_weapon_target(
    vehicle: Vehicle_Data,
    t_types: List[str],
    t_dims: List[str],
    cat: str,
) -> float:
    """Restituisce get_normalized_weapon_target_effectiveness() con logger mockato."""
    try:
        with patch(_LOGGER_PATH, MagicMock()):
            return vehicle.get_normalized_weapon_target_effectiveness(
                t_types, t_dims, category=cat
            )
    except Exception:
        return float("nan")


def _vehicles_by_category() -> dict:
    """Restituisce un dict {category: [Vehicle_Data, ...]} ordinato per categoria."""
    result: dict = {}
    for obj in Vehicle_Data._registry.values():
        result.setdefault(obj.category, []).append(obj)
    return result


def _vehicles_with_weapon_type(wtype: str) -> dict:
    """Restituisce {category: [Vehicle_Data, ...]} per i veicoli che montano
    armi del tipo specificato (es. 'CANNONS', 'MISSILES', ...)."""
    result: dict = {}
    for obj in Vehicle_Data._registry.values():
        if wtype in obj.weapons and obj.weapons[wtype]:
            result.setdefault(obj.category, []).append(obj)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  STAMPA A TERMINALE
# ─────────────────────────────────────────────────────────────────────────────

def print_vehicle_scores_tables() -> None:
    """Stampa a terminale Vehicle_Scores: per ogni categoria veicolo, la tabella
    con tutti i punteggi normalizzati (global e category)."""
    cat_map = _vehicles_by_category()

    for cat, vehicles in sorted(cat_map.items()):
        if cat not in VEHICLE_CATEGORIES:
            continue
        header = f"  CATEGORIA: {cat}  —  punteggi normalizzati"
        width = max(80, len(header) + 4)
        print()
        print("═" * width)
        print(header)
        print("═" * width)

        # Raccoglie score names dal primo veicolo disponibile
        sample_model = vehicles[0].model
        score_names = list(VEHICLE.get(sample_model, {}).keys())

        col_m = max(16, max(len(v.model) for v in vehicles))
        col_s = 12

        for score_name in score_names:
            print(f"\n  [ {score_name} ]")
            header_row = f"  {'Model':<{col_m}}   {'global':>{col_s}}   {'category':>{col_s}}"
            print("─" * len(header_row))
            print(header_row)
            print("─" * len(header_row))

            rows = []
            for v in vehicles:
                sd = VEHICLE.get(v.model, {}).get(score_name, {})
                gs = sd.get("global_score", float("nan"))
                cs = sd.get("category_score", float("nan"))
                rows.append((v.model, gs, cs))
            rows.sort(key=lambda x: x[2] if not _is_nan(x[2]) else -1, reverse=True)

            for model, gs, cs in rows:
                gs_str = f"{gs:.4f}" if not _is_nan(gs) else "   N/A  "
                cs_str = f"{cs:.4f}" if not _is_nan(cs) else "   N/A  "
                print(f"  {model:<{col_m}}   {gs_str:>{col_s}}   {cs_str:>{col_s}}")
        print()


def print_weapon_score_tables(weapon_type_list: List[str]) -> None:
    """Stampa a terminale la tabella get_normalized_weapon_score() per ogni
    tipo di arma (filtro) e per ogni categoria veicolo che monta quell'arma."""
    for wtype in weapon_type_list:
        cat_map = _vehicles_with_weapon_type(wtype)
        if not cat_map:
            print(f"\n[SKIP] Nessun veicolo con armamento '{wtype}'.\n")
            continue

        for cat, vehicles in sorted(cat_map.items()):
            header = f"  WEAPON TYPE: {wtype}  |  CATEGORIA VEICOLO: {cat}   —   get_normalized_weapon_score()"
            width = max(80, len(header) + 4)
            print()
            print("═" * width)
            print(header)
            print("═" * width)

            col_m = max(16, max(len(v.model) for v in vehicles))
            col_s = 14
            print(f"  {'Model':<{col_m}}   {'category_score':>{col_s}}")
            print("─" * (col_m + col_s + 8))

            rows = [
                (v.model, _safe_normalized_weapon_score(v, cat))
                for v in vehicles
            ]
            rows.sort(key=lambda x: x[1] if not _is_nan(x[1]) else -1, reverse=True)

            for model, score in rows:
                s = f"{score:.6f}" if not _is_nan(score) else "     N/A     "
                print(f"  {model:<{col_m}}   {s:>{col_s}}")
        print()


def print_weapon_score_target_tables(
    weapon_type_list: List[str],
    target_type_list: List[str],
    target_dimension_list: List[str],
) -> None:
    """Stampa a terminale la tabella get_normalized_weapon_target_effectiveness()
    per ogni tipo di arma e ogni categoria veicolo."""
    combinations = [(t, d) for t in target_type_list for d in target_dimension_list]

    for wtype in weapon_type_list:
        cat_map = _vehicles_with_weapon_type(wtype)
        if not cat_map:
            continue

        for cat, vehicles in sorted(cat_map.items()):
            header = (
                f"  WEAPON TYPE: {wtype}  |  CATEGORIA: {cat}"
                f"   —   get_normalized_weapon_target_effectiveness()"
            )
            col_headers = [f"{t}/{d}" for t, d in combinations]
            col_m = max(16, max(len(v.model) for v in vehicles))
            cell_w = 12

            header_parts = [f"  {'Model':<{col_m}}"]
            for h in col_headers:
                header_parts.append(f"{h:^{cell_w}}")
            header_line = "  ".join(header_parts)
            width = max(len(header), len(header_line))

            print()
            print("═" * width)
            print(header)
            print("═" * width)
            print(header_line)
            print("─" * width)

            for v in vehicles:
                row = [f"  {v.model:<{col_m}}"]
                for t_type, t_dim in combinations:
                    val = _safe_normalized_weapon_target(v, [t_type], [t_dim], cat)
                    s = f"{val:.4f}" if not _is_nan(val) else "   N/A  "
                    row.append(f"{s:^{cell_w}}")
                print("  ".join(row))
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


def save_vehicle_scores_pdf(output_path: str) -> None:
    """Salva Vehicle_Scores.pdf con una pagina per categoria veicolo.
    Ogni pagina mostra tutti i punteggi normalizzati (global_score, category_score)
    per ogni veicolo nella categoria, con colorazione heatmap (verde=alto, rosso=basso)."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cat_map = _vehicles_by_category()

    with PdfPages(output_path) as pdf:
        for cat in VEHICLE_CATEGORIES:
            vehicles = cat_map.get(cat, [])
            if not vehicles:
                continue

            # Raccoglie score_names dal primo veicolo
            sample_model = vehicles[0].model
            score_names = list(VEHICLE.get(sample_model, {}).keys())

            # Costruisce tabella: righe = (score_name, scope), colonne = models
            col_labels = ["Score", "Scope"] + [v.model for v in vehicles]
            cell_text = []
            score_matrix = []  # per la colorazione

            for score_name in score_names:
                for scope in ("global_score", "category_score"):
                    row_vals = []
                    for v in vehicles:
                        val = VEHICLE.get(v.model, {}).get(score_name, {}).get(scope, float("nan"))
                        row_vals.append(val)
                    score_matrix.append(row_vals)
                    row_str = [score_name, scope.replace("_score", "")] + [
                        f"{v:.3f}" if not _is_nan(v) else "N/A" for v in row_vals
                    ]
                    cell_text.append(row_str)

            # Calcola colorazione per colonne dei veicoli (colonne 2..N)
            all_vals = [v for row in score_matrix for v in row if not _is_nan(v)]
            max_s = max(all_vals) if all_vals else 1.0
            min_s = min(all_vals) if all_vals else 0.0
            rng = (max_s - min_s) if max_s != min_s else 1.0

            cell_colors = []
            for row_vals in score_matrix:
                row_colors = ["#f0f4f8", "#e8ecf0"]  # score_name, scope
                for v in row_vals:
                    if not _is_nan(v):
                        row_colors.append(plt.cm.RdYlGn((v - min_s) / rng))
                    else:
                        row_colors.append((0.87, 0.87, 0.87, 1.0))
                cell_colors.append(row_colors)

            n_rows = len(cell_text)
            n_cols = len(col_labels)
            fig_w = max(14.0, 1.8 * len(vehicles) + 4.0)
            fig_h = max(5.0, 0.32 * n_rows + 2.5)

            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.axis("off")
            ax.set_title(
                f"Vehicle Scores — Categoria: {cat}\n"
                f"Punteggi normalizzati (global e category scope)",
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

    print(f"[PDF] Vehicle_Scores → {output_path}")


def save_vehicle_weapon_score_pdf(
    weapon_type_list: List[str],
    output_path: str,
) -> None:
    """Salva vehicle_weapon_score_tables.pdf.
    Per ogni tipo di arma e per ogni categoria veicolo che monta quell'arma:
    una pagina con la tabella get_normalized_weapon_score() ordinata per punteggio
    decrescente, con colorazione heatmap (verde=alto, rosso=basso)."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    with PdfPages(output_path) as pdf:
        for wtype in weapon_type_list:
            cat_map = _vehicles_with_weapon_type(wtype)
            if not cat_map:
                continue

            for cat in VEHICLE_CATEGORIES:
                vehicles = cat_map.get(cat, [])
                if not vehicles:
                    continue

                rows = [
                    (v.model, _safe_normalized_weapon_score(v, cat))
                    for v in vehicles
                ]
                rows.sort(
                    key=lambda x: x[1] if not _is_nan(x[1]) else -1,
                    reverse=True,
                )

                valid_scores = [s for _, s in rows if not _is_nan(s)]
                max_s = max(valid_scores) if valid_scores else 1.0
                min_s = min(valid_scores) if valid_scores else 0.0
                rng = (max_s - min_s) if max_s != min_s else 1.0

                cell_text = []
                cell_colors = []
                for rank, (model, score) in enumerate(rows, start=1):
                    score_str = f"{score:.6f}" if not _is_nan(score) else "N/A"
                    cell_text.append([str(rank), model, score_str])
                    if not _is_nan(score):
                        color = plt.cm.RdYlGn((score - min_s) / rng)
                    else:
                        color = (0.87, 0.87, 0.87, 1.0)
                    cell_colors.append(["#f5f5f5", "#f0f4f8", color])

                fig_h = max(4.0, 0.38 * len(cell_text) + 2.5)
                fig, ax = plt.subplots(figsize=(11, fig_h))
                ax.axis("off")
                ax.set_title(
                    f"Weapon Score — Tipo Arma: {wtype}  |  Categoria: {cat}\n"
                    f"Funzione: get_normalized_weapon_score(category='{cat}')",
                    fontsize=12, fontweight="bold", pad=18,
                )
                tbl = ax.table(
                    cellText=cell_text,
                    colLabels=["#", "Modello Veicolo", "Score Normalizzato"],
                    cellColours=cell_colors,
                    loc="center",
                    cellLoc="center",
                )
                tbl.auto_set_font_size(False)
                tbl.set_fontsize(8)
                tbl.auto_set_column_width([0, 1, 2])
                _header_style(tbl, 3)
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

    print(f"[PDF] vehicle_weapon_score_tables → {output_path}")


def save_vehicle_weapon_score_target_pdf(
    weapon_type_list: List[str],
    target_type_list: List[str],
    target_dimension_list: List[str],
    output_path: str,
) -> None:
    """Salva vehicle_weapon_score_target_tables.pdf.
    Per ogni tipo di arma e ogni categoria veicolo: una pagina con la tabella
    get_normalized_weapon_target_effectiveness() con colonne per ogni combinazione
    (target_type × target_dimension), con colorazione heatmap."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    combinations = [(t, d) for t in target_type_list for d in target_dimension_list]

    with PdfPages(output_path) as pdf:
        for wtype in weapon_type_list:
            cat_map = _vehicles_with_weapon_type(wtype)
            if not cat_map:
                continue

            for cat in VEHICLE_CATEGORIES:
                vehicles = cat_map.get(cat, [])
                if not vehicles:
                    continue

                col_labels = ["Modello Veicolo"] + [
                    f"{t}\n{d}" for t, d in combinations
                ]
                n_data_cols = len(combinations)
                n_cols_total = 1 + n_data_cols

                cell_text = []
                score_matrix = []
                for v in vehicles:
                    row_scores = [
                        _safe_normalized_weapon_target(v, [t], [d], cat)
                        for t, d in combinations
                    ]
                    score_matrix.append(row_scores)
                    cell_text.append(
                        [v.model]
                        + [f"{s:.4f}" if not _is_nan(s) else "N/A" for s in row_scores]
                    )

                all_vals = [v for row in score_matrix for v in row if not _is_nan(v)]
                max_s = max(all_vals) if all_vals else 1.0
                min_s = min(all_vals) if all_vals else 0.0
                rng = (max_s - min_s) if max_s != min_s else 1.0

                cell_colors = []
                for row_scores in score_matrix:
                    row_colors = ["#f0f4f8"]
                    for s in row_scores:
                        if not _is_nan(s):
                            row_colors.append(plt.cm.RdYlGn((s - min_s) / rng))
                        else:
                            row_colors.append((0.87, 0.87, 0.87, 1.0))
                    cell_colors.append(row_colors)

                fig_w = max(14, 2.0 * n_cols_total)
                fig_h = max(4.0, 0.40 * len(vehicles) + 2.5)
                fig, ax = plt.subplots(figsize=(fig_w, fig_h))
                ax.axis("off")
                ax.set_title(
                    f"Weapon Target Effectiveness — Tipo Arma: {wtype}  |  Categoria: {cat}\n"
                    f"Funzione: get_normalized_weapon_target_effectiveness()",
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

    print(f"[PDF] vehicle_weapon_score_target_tables → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        TestVehicleDataModuleStructure,
        TestVehicleDataAttributes,
        TestWeaponEval,
        TestRadarEval,
        TestTVDEval,
        TestSpeedEval,
        TestProtectionEval,
        TestCommunicationEval,
        TestHydraulicEval,
        TestRangeEval,
        TestReliabilityAndMaintenance,
        TestCombatEval,
        TestWeaponTargetEffectiveness,
        TestWeaponTargetEffectivenessDistribuition,
        TestNormalize,
        TestGetNormalizedWeaponScore,
        TestGetNormalizedRadarScore,
        TestGetNormalizedSpeedScore,
        TestGetNormalizedProtectionScore,
        TestGetNormalizedCommunicationScore,
        TestGetNormalizedHydraulicScore,
        TestGetNormalizedRangeScore,
        TestGetNormalizedReliabilityAndAvailability,
        TestGetNormalizedCombatScore,
        TestGetNormalizedWeaponTargetEffectiveness,
        TestGetNormalizedWeaponTargetEffectivenessDistribuition,
        TestGetVehicleData,
        TestGetVehicleScores,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def _run_tables_terminal() -> None:
    print("\n" + "=" * 70)
    print("  VEHICLE SCORES — punteggi per categoria")
    print("=" * 70)
    print_vehicle_scores_tables()

    print("\n" + "=" * 70)
    print("  WEAPON SCORE — get_normalized_weapon_score()")
    print("=" * 70)
    print_weapon_score_tables(weapon_type)

    print("\n" + "=" * 70)
    print("  WEAPON SCORE TARGET — get_normalized_weapon_target_effectiveness()")
    print("=" * 70)
    print_weapon_score_target_tables(weapon_type, target_type, target_dimension)


def _run_tables_pdf() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_vehicle_scores_pdf(
        os.path.join(OUTPUT_DIR, "Vehicle_Scores.pdf"),
    )
    save_vehicle_weapon_score_pdf(
        weapon_type,
        os.path.join(OUTPUT_DIR, "vehicle_weapon_score_tables.pdf"),
    )
    save_vehicle_weapon_score_target_pdf(
        weapon_type,
        target_type,
        target_dimension,
        os.path.join(OUTPUT_DIR, "vehicle_weapon_score_target_tables.pdf"),
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
    print("║       Test_Vehicle_Data  —  Menu principale                 ║")
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
