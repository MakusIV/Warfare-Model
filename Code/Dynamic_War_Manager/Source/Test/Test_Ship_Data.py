"""
Test_Ship_Data.py
=================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo Ship_Data.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Ship_Data.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ship_Data.py            # menu interattivo
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ship_Data.py --tables-only
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ship_Data.py --tests-only

Note sul modulo sotto test:
  - Ship_Data: dataclass che rappresenta un asset navale.
  - Ship_Data._registry: dizionario globale {model: Ship_Data}.
  - CATEGORY: set di categorie valide derivato da Sea_Asset_Type.
  - AMMO_LOAD_REFERENCE: dict con riferimenti quantità munizioni navali.
  - SHIP_WEAPON_SCORE: dict con score base per tipo di arma navale.
  - SHIP: dict con punteggi pre-calcolati per ogni nave.
  - SCORES: tuple con le chiavi dei punteggi disponibili.
  - get_ship_data(model): restituisce tutti i dati di una nave.
  - get_ship_scores(model, scores): restituisce i punteggi di una nave.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAZIONE — modificare le liste per personalizzare le tabelle
# ─────────────────────────────────────────────────────────────────────────────

# Categorie di navi da includere nella stampa Ship_Scores.pdf
SHIP_CATEGORIES: List[str] = [
    "Carrier",
    "Cruiser",
    "Destroyer",
    "Frigate",
    "Corvette",
    "Submarine",
    "Amphibious_Assault_Ship",
]

# Tipi di arma navale per le tabelle ship_weapon_score.
# Per ogni weapon_type vengono mostrate le navi che montano quel tipo
# di armamento, raggruppate per categoria nave.
weapon_type: List[str] = [
    "MISSILES_SAM",
    "MISSILES_ASM",
    "MISSILES_TORPEDO",
    "GUNS",
    "CIWS",
]

# Directory di output per i PDF
OUTPUT_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "..", "out",
    )
)

# Path del logger da mockare nei test
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Ship_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import (
    Ship_Data,
    AMMO_LOAD_REFERENCE,
    SHIP_WEAPON_SCORE,
    CATEGORY,
    SHIP,
    SCORES,
    get_ship_data,
    get_ship_scores,
)

# ─────────────────────────────────────────────────────────────────────────────
#  NAVI DI RIFERIMENTO PER I TEST
# ─────────────────────────────────────────────────────────────────────────────

_CARRIER_MODEL    = "CVN-70 Carl Vinson"
_DESTROYER_MODEL  = "USS Arleigh Burke IIa"
_CRUISER_MODEL    = "CG-65"
_FRIGATE_MODEL    = "FFG-46"
_CORVETTE_MODEL   = "FFL 1124.4 Grisha"
_SUBMARINE_MODEL  = "Type 093"
_AMPHIBIOUS_MODEL = "LHA-1 Tarawa"


# ─────────────────────────────────────────────────────────────────────────────
#  1. STRUTTURA DATI DEL MODULO
# ─────────────────────────────────────────────────────────────────────────────

class TestShipDataModuleStructure(unittest.TestCase):
    """Verifica le strutture dati globali del modulo Ship_Data."""

    # ── AMMO_LOAD_REFERENCE ─────────────────────────────────────────────────

    def test_ammo_load_reference_is_dict(self):
        self.assertIsInstance(AMMO_LOAD_REFERENCE, dict)

    def test_ammo_load_reference_has_expected_keys(self):
        expected = {"MISSILES_SAM", "MISSILES_ASM", "MISSILES_TORPEDO", "GUNS", "CIWS"}
        for key in expected:
            with self.subTest(key=key):
                self.assertIn(key, AMMO_LOAD_REFERENCE)

    def test_ammo_load_reference_values_are_positive(self):
        for key, val in AMMO_LOAD_REFERENCE.items():
            with self.subTest(key=key):
                self.assertIsInstance(val, (int, float))
                self.assertGreater(val, 0)

    # ── SHIP_WEAPON_SCORE ────────────────────────────────────────────────────

    def test_ship_weapon_score_is_dict(self):
        self.assertIsInstance(SHIP_WEAPON_SCORE, dict)

    def test_ship_weapon_score_non_empty(self):
        self.assertGreater(len(SHIP_WEAPON_SCORE), 0)

    def test_ship_weapon_score_keys_are_strings(self):
        for key in SHIP_WEAPON_SCORE:
            with self.subTest(key=key):
                self.assertIsInstance(key, str)

    def test_ship_weapon_score_values_are_positive_floats(self):
        for key, val in SHIP_WEAPON_SCORE.items():
            with self.subTest(key=key):
                self.assertIsInstance(val, (int, float))
                self.assertGreater(val, 0)

    def test_ship_weapon_score_contains_known_weapons(self):
        expected = {"RIM-162-ESSM", "RGM-84-Harpoon", "Mk-48", "Mk-45-5in", "Mk-15-Phalanx"}
        for w in expected:
            with self.subTest(weapon=w):
                self.assertIn(w, SHIP_WEAPON_SCORE)

    # ── CATEGORY ────────────────────────────────────────────────────────────

    def test_category_is_set(self):
        self.assertIsInstance(CATEGORY, set)

    def test_category_contains_expected_values(self):
        expected = {
            "Carrier", "Cruiser", "Destroyer", "Frigate", "Corvette",
            "Submarine", "Amphibious_Assault_Ship", "Transport", "Civilian",
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

    def test_scores_contains_expected_keys(self):
        expected = {
            "combat score", "weapon score", "radar score",
            "radar score air", "radar score sea",
            "speed score", "range score", "avalaibility",
            "manutenability score (mttr)", "reliability score (mtbf)",
        }
        for key in expected:
            with self.subTest(key=key):
                self.assertIn(key, SCORES)

    # ── Ship_Data._registry ──────────────────────────────────────────────────

    def test_registry_is_dict(self):
        self.assertIsInstance(Ship_Data._registry, dict)

    def test_registry_non_empty(self):
        self.assertGreater(len(Ship_Data._registry), 0)

    def test_registry_keys_are_strings(self):
        for key in Ship_Data._registry:
            with self.subTest(key=key):
                self.assertIsInstance(key, str)

    def test_registry_values_are_ship_data_instances(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj, Ship_Data)

    def test_registry_contains_known_carriers(self):
        for model in (_CARRIER_MODEL, "CVN-71 Theodore Roosevelt", "CV 1143.5 Admiral Kuznetsov"):
            with self.subTest(model=model):
                self.assertIn(model, Ship_Data._registry)

    def test_registry_contains_known_destroyers(self):
        for model in (_DESTROYER_MODEL, "Type 052B Guangzhou-class", "Type 052C"):
            with self.subTest(model=model):
                self.assertIn(model, Ship_Data._registry)

    def test_registry_contains_known_cruisers(self):
        for model in (_CRUISER_MODEL, "CGN 1144.2 Piotr Velikiy", "CG 1164 Moskva"):
            with self.subTest(model=model):
                self.assertIn(model, Ship_Data._registry)

    def test_registry_model_key_matches_attribute(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertEqual(model, obj.model)

    def test_registry_categories_are_valid(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIn(obj.category, CATEGORY)

    # ── SHIP dict ─────────────────────────────────────────────────────────────

    def test_ship_dict_is_dict(self):
        self.assertIsInstance(SHIP, dict)

    def test_ship_dict_non_empty(self):
        self.assertGreater(len(SHIP), 0)

    def test_ship_dict_has_all_registry_models(self):
        for model in Ship_Data._registry:
            with self.subTest(model=model):
                self.assertIn(model, SHIP)

    def test_ship_dict_entries_are_dicts(self):
        for model, data in SHIP.items():
            with self.subTest(model=model):
                self.assertIsInstance(data, dict)

    def test_ship_dict_entries_have_score_keys(self):
        """Ogni voce in SHIP deve contenere almeno combat score e weapon score."""
        required = {"combat score", "weapon score"}
        for model, data in SHIP.items():
            for key in required:
                with self.subTest(model=model, key=key):
                    self.assertIn(key, data)

    def test_ship_score_dicts_have_global_and_category(self):
        """Ogni sotto-dict di punteggio deve avere global_score e category_score."""
        for model, data in SHIP.items():
            for score_name, score_dict in data.items():
                with self.subTest(model=model, score=score_name):
                    self.assertIn("global_score", score_dict)
                    self.assertIn("category_score", score_dict)

    def test_ship_score_values_are_floats_in_range(self):
        """I valori dei punteggi normalizzati devono essere float in [0, 1]."""
        for model, data in SHIP.items():
            for score_name, score_dict in data.items():
                for scope, val in score_dict.items():
                    with self.subTest(model=model, score=score_name, scope=scope):
                        self.assertIsInstance(val, (int, float))
                        self.assertGreaterEqual(val, 0.0)
                        self.assertLessEqual(val, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
#  2. SHIP_DATA CLASS — ATTRIBUTI E COSTRUTTORE
# ─────────────────────────────────────────────────────────────────────────────

class TestShipDataAttributes(unittest.TestCase):
    """Verifica che gli attributi degli oggetti Ship_Data siano corretti."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()
        self.carrier   = Ship_Data._registry[_CARRIER_MODEL]
        self.destroyer = Ship_Data._registry[_DESTROYER_MODEL]
        self.submarine = Ship_Data._registry[_SUBMARINE_MODEL]

    def tearDown(self):
        self._patcher.stop()

    def test_model_attribute_is_string(self):
        self.assertIsInstance(self.carrier.model, str)

    def test_made_attribute_is_string(self):
        self.assertIsInstance(self.carrier.made, str)

    def test_ship_class_attribute_is_string(self):
        """ship_class deve essere una stringa (es. 'Nimitz-class')."""
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.ship_class, str)
                self.assertGreater(len(obj.ship_class), 0)

    def test_category_attribute_valid(self):
        self.assertIn(self.carrier.category, CATEGORY)
        self.assertIn(self.destroyer.category, CATEGORY)
        self.assertIn(self.submarine.category, CATEGORY)

    def test_carrier_category_is_carrier(self):
        self.assertEqual(self.carrier.category, "Carrier")

    def test_destroyer_category_is_destroyer(self):
        self.assertEqual(self.destroyer.category, "Destroyer")

    def test_submarine_category_is_submarine(self):
        self.assertEqual(self.submarine.category, "Submarine")

    def test_weapons_attribute_is_dict(self):
        self.assertIsInstance(self.carrier.weapons, dict)

    def test_weapons_non_empty_for_combat_ships(self):
        self.assertGreater(len(self.destroyer.weapons), 0)

    def test_engine_attribute_is_dict_or_none(self):
        self.assertTrue(
            self.carrier.engine is None or isinstance(self.carrier.engine, dict)
        )

    def test_speed_data_attribute_is_dict(self):
        self.assertIsInstance(self.carrier.speed_data, dict)

    def test_radar_attribute_present(self):
        """radar deve essere definito (dict, False o None) per tutti."""
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertTrue(
                    obj.radar is False or obj.radar is None or isinstance(obj.radar, dict)
                )

    def test_cost_is_positive_number(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.cost, (int, float))
                self.assertGreater(obj.cost, 0)

    def test_range_is_positive_number(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.range, (int, float))
                self.assertGreater(obj.range, 0)

    def test_start_service_is_int(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.start_service, int)

    def test_roles_attribute_is_list(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.roles, list)
                self.assertGreater(len(obj.roles), 0)

    def test_carrier_ship_class_is_nimitz(self):
        """I portaerei Nimitz devono avere ship_class='Nimitz-class'."""
        self.assertEqual(self.carrier.ship_class, "Nimitz-class")

    def test_physical_characteristics_attribute_is_dict(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.physical_characteristics, dict)

    def test_physical_characteristics_has_correct_keys(self):
        expected_keys = {'length', 'width', 'height', 'weight'}
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertTrue(expected_keys.issubset(obj.physical_characteristics))

    def test_physical_characteristics_values_are_positive_ints(self):
        for model, obj in Ship_Data._registry.items():
            for key in ('length', 'width', 'height', 'weight'):
                with self.subTest(model=model, key=key):
                    val = obj.physical_characteristics[key]
                    self.assertIsInstance(val, int)
                    self.assertGreater(val, 0)


# ─────────────────────────────────────────────────────────────────────────────
#  2b. PHYSICAL_CHARACTERISTICS — VALIDAZIONE STRUTTURA E VALORI
# ─────────────────────────────────────────────────────────────────────────────

class TestShipDataPhysicalCharacteristics(unittest.TestCase):
    """Verifica la struttura e i valori di physical_characteristics per tutte le navi."""

    _PC_KEYS = {'length', 'width', 'height', 'weight'}

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()
        self.carrier   = Ship_Data._registry[_CARRIER_MODEL]
        self.cruiser   = Ship_Data._registry[_CRUISER_MODEL]
        self.destroyer = Ship_Data._registry[_DESTROYER_MODEL]
        self.frigate   = Ship_Data._registry[_FRIGATE_MODEL]
        self.corvette  = Ship_Data._registry[_CORVETTE_MODEL]

    def tearDown(self):
        self._patcher.stop()

    def test_all_ships_have_physical_characteristics(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertTrue(hasattr(obj, 'physical_characteristics'))

    def test_all_ships_physical_characteristics_is_dict(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertIsInstance(obj.physical_characteristics, dict)

    def test_all_ships_physical_characteristics_has_required_keys(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                self.assertTrue(self._PC_KEYS.issubset(obj.physical_characteristics))

    def test_all_ships_physical_characteristics_values_are_positive_ints(self):
        for model, obj in Ship_Data._registry.items():
            for key in self._PC_KEYS:
                with self.subTest(model=model, key=key):
                    val = obj.physical_characteristics[key]
                    self.assertIsInstance(val, int)
                    self.assertGreater(val, 0)

    def test_length_ge_width_for_all_ships(self):
        """La lunghezza deve essere >= larghezza per ogni nave."""
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                pc = obj.physical_characteristics
                self.assertGreaterEqual(pc['length'], pc['width'])

    def test_length_ge_height_for_all_ships(self):
        """La lunghezza deve essere >= altezza per ogni nave."""
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                pc = obj.physical_characteristics
                self.assertGreaterEqual(pc['length'], pc['height'])

    def test_carrier_larger_than_destroyer(self):
        """Il portaerei deve essere più pesante e lungo del cacciatorpediniere."""
        self.assertGreater(
            self.carrier.physical_characteristics['weight'],
            self.destroyer.physical_characteristics['weight'],
        )
        self.assertGreater(
            self.carrier.physical_characteristics['length'],
            self.destroyer.physical_characteristics['length'],
        )

    def test_cruiser_larger_than_frigate(self):
        """L'incrociatore deve essere più pesante e lungo della fregata."""
        self.assertGreater(
            self.cruiser.physical_characteristics['weight'],
            self.frigate.physical_characteristics['weight'],
        )
        self.assertGreater(
            self.cruiser.physical_characteristics['length'],
            self.frigate.physical_characteristics['length'],
        )

    def test_frigate_larger_than_corvette(self):
        """La fregata deve essere più pesante e lunga della corvetta."""
        self.assertGreater(
            self.frigate.physical_characteristics['weight'],
            self.corvette.physical_characteristics['weight'],
        )
        self.assertGreater(
            self.frigate.physical_characteristics['length'],
            self.corvette.physical_characteristics['length'],
        )

    def test_constructor_raises_for_missing_key(self):
        """Il costruttore deve sollevare ValueError se manca una chiave in physical_characteristics."""
        ref = Ship_Data._registry[_CARRIER_MODEL]
        bad_pc = {'length': 333, 'width': 77, 'height': 76}  # manca 'weight'
        with self.assertRaises(ValueError):
            Ship_Data(
                constructor=ref.constructor,
                made=ref.made,
                model="_test_missing_key",
                category=ref.category,
                ship_class=ref.ship_class,
                physical_characteristics=bad_pc,
                start_service=ref.start_service,
                end_service=ref.end_service,
                cost=ref.cost,
                range=ref.range,
                roles=ref.roles,
                engine=ref.engine,
                weapons=ref.weapons,
                radar=ref.radar,
                speed_data=ref.speed_data,
            )

    def test_constructor_raises_for_wrong_type(self):
        """Il costruttore deve sollevare ValueError se physical_characteristics non è un dict."""
        ref = Ship_Data._registry[_CARRIER_MODEL]
        with self.assertRaises(ValueError):
            Ship_Data(
                constructor=ref.constructor,
                made=ref.made,
                model="_test_wrong_type",
                category=ref.category,
                ship_class=ref.ship_class,
                physical_characteristics="not_a_dict",
                start_service=ref.start_service,
                end_service=ref.end_service,
                cost=ref.cost,
                range=ref.range,
                roles=ref.roles,
                engine=ref.engine,
                weapons=ref.weapons,
                radar=ref.radar,
                speed_data=ref.speed_data,
            )

    def test_constructor_raises_for_non_positive_value(self):
        """Il costruttore deve sollevare ValueError se un valore di physical_characteristics è <= 0."""
        ref = Ship_Data._registry[_CARRIER_MODEL]
        bad_pc = {'length': 333, 'width': 77, 'height': 0, 'weight': 104000}
        with self.assertRaises(ValueError):
            Ship_Data(
                constructor=ref.constructor,
                made=ref.made,
                model="_test_zero_value",
                category=ref.category,
                ship_class=ref.ship_class,
                physical_characteristics=bad_pc,
                start_service=ref.start_service,
                end_service=ref.end_service,
                cost=ref.cost,
                range=ref.range,
                roles=ref.roles,
                engine=ref.engine,
                weapons=ref.weapons,
                radar=ref.radar,
                speed_data=ref.speed_data,
            )

    def test_constructor_raises_for_float_value(self):
        """Il costruttore deve sollevare ValueError se un valore non è int (es. float)."""
        ref = Ship_Data._registry[_CARRIER_MODEL]
        bad_pc = {'length': 333.5, 'width': 77, 'height': 76, 'weight': 104000}
        with self.assertRaises(ValueError):
            Ship_Data(
                constructor=ref.constructor,
                made=ref.made,
                model="_test_float_value",
                category=ref.category,
                ship_class=ref.ship_class,
                physical_characteristics=bad_pc,
                start_service=ref.start_service,
                end_service=ref.end_service,
                cost=ref.cost,
                range=ref.range,
                roles=ref.roles,
                engine=ref.engine,
                weapons=ref.weapons,
                radar=ref.radar,
                speed_data=ref.speed_data,
            )


# ─────────────────────────────────────────────────────────────────────────────
#  3. METODI DI VALUTAZIONE ASSOLUTI (_eval)
# ─────────────────────────────────────────────────────────────────────────────

class TestWeaponEval(unittest.TestCase):
    """Unit test per Ship_Data._weapon_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_destroyer_weapon_eval_positive(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship._weapon_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_ships_weapon_eval_non_negative(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._weapon_eval()
                self.assertIsInstance(score, (int, float))
                self.assertGreaterEqual(score, 0.0)

    def test_cruiser_weapon_eval_greater_than_corvette(self):
        """Un incrociatore pesante deve avere weapon_eval >= corvetta."""
        cruiser_score  = Ship_Data._registry[_CRUISER_MODEL]._weapon_eval()
        corvette_score = Ship_Data._registry[_CORVETTE_MODEL]._weapon_eval()
        self.assertGreater(cruiser_score, corvette_score)

    def test_deterministic(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._weapon_eval(), ship._weapon_eval(), places=9)

    def test_unknown_weapon_model_triggers_warning(self):
        """Un'arma non presente in SHIP_WEAPON_SCORE deve emettere un warning."""
        obj = object.__new__(Ship_Data)
        obj.model    = "_test_ship_unknown_weapon"
        obj.weapons  = {"MISSILES_SAM": [("WEAPON_NOT_IN_DICT_XYZ", 8)]}

        fresh_mock = MagicMock()
        with patch(_LOGGER_PATH, fresh_mock):
            obj._weapon_eval()
        fresh_mock.warning.assert_called()


class TestRadarEval(unittest.TestCase):
    """Unit test per Ship_Data._radar_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_false_radar_returns_zero(self):
        obj = object.__new__(Ship_Data)
        obj.radar = False
        obj.model = "_test_no_radar"
        obj.made  = "Test"
        obj.category = "Corvette"
        self.assertEqual(obj._radar_eval(), 0.0)

    def test_none_radar_returns_zero_with_warning(self):
        fresh_mock = MagicMock()
        obj = object.__new__(Ship_Data)
        obj.radar    = None
        obj.model    = "_test_none_radar"
        obj.made     = "Test"
        obj.category = "Corvette"
        with patch(_LOGGER_PATH, fresh_mock):
            score = obj._radar_eval()
        self.assertEqual(score, 0.0)
        fresh_mock.warning.assert_called()

    def test_destroyer_radar_eval_positive(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship._radar_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_invalid_modes_raises_type_error(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        with self.assertRaises(TypeError):
            ship._radar_eval(modes="air")

    def test_invalid_modes_element_raises_type_error(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        with self.assertRaises(TypeError):
            ship._radar_eval(modes=["invalid_mode"])

    def test_valid_modes_subset_air(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship._radar_eval(modes=["air"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_valid_modes_subset_sea(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship._radar_eval(modes=["sea"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_all_ships_radar_eval_non_negative(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._radar_eval()
                self.assertGreaterEqual(score, 0.0)

    def test_aegis_destroyer_radar_greater_than_corvette(self):
        """Un cacciatorpediniere AEGIS deve avere radar_eval > corvetta."""
        destroyer_score = Ship_Data._registry[_DESTROYER_MODEL]._radar_eval()
        corvette_score  = Ship_Data._registry[_CORVETTE_MODEL]._radar_eval()
        self.assertGreater(destroyer_score, corvette_score)

    def test_submarine_air_radar_zero(self):
        """Il sottomarino Type 093 non ha radar aria (False per 'air')."""
        sub = Ship_Data._registry[_SUBMARINE_MODEL]
        score_air = sub._radar_eval(modes=["air"])
        self.assertEqual(score_air, 0.0)

    def test_submarine_sea_radar_positive(self):
        """Il sottomarino Type 093 ha sonar/radar di superficie."""
        sub = Ship_Data._registry[_SUBMARINE_MODEL]
        score_sea = sub._radar_eval(modes=["sea"])
        self.assertGreater(score_sea, 0.0)

    def test_deterministic(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._radar_eval(), ship._radar_eval(), places=9)


class TestSpeedEval(unittest.TestCase):
    """Unit test per Ship_Data._speed_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_carrier_speed_eval_positive(self):
        ship = Ship_Data._registry[_CARRIER_MODEL]
        score = ship._speed_eval()
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_ships_speed_eval_positive(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._speed_eval()
                self.assertGreater(score, 0.0)

    def test_corvette_faster_than_carrier(self):
        """Una corvetta deve avere speed_eval > portaerei."""
        corvette_score = Ship_Data._registry[_CORVETTE_MODEL]._speed_eval()
        carrier_score  = Ship_Data._registry[_CARRIER_MODEL]._speed_eval()
        self.assertGreater(corvette_score, carrier_score)

    def test_deterministic(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._speed_eval(), ship._speed_eval(), places=9)

    def test_invalid_metric_raises_value_error(self):
        """Metrica sconosciuta in speed_data deve sollevare ValueError."""
        obj = object.__new__(Ship_Data)
        obj.model      = "_test_bad_metric"
        obj.made       = "Test"
        obj.speed_data = {'max': {'metric': 'UNKNOWN_METRIC', 'speed': 30}}
        with patch(_LOGGER_PATH, MagicMock()):
            with self.assertRaises(ValueError):
                obj._speed_eval()

    def test_nautical_metric_accepted(self):
        """Velocità espressa in nodi (metric='nautical') non deve sollevare errori."""
        obj = object.__new__(Ship_Data)
        obj.model      = "_test_nautical"
        obj.made       = "Test"
        obj.speed_data = {
            'sustained': {'metric': 'nautical', 'speed': 20},
            'max':       {'metric': 'nautical', 'speed': 28},
            'flank':     {'metric': 'nautical', 'speed': 30},
        }
        with patch(_LOGGER_PATH, MagicMock()):
            score = obj._speed_eval()
        self.assertGreater(score, 0.0)


class TestRangeEval(unittest.TestCase):
    """Unit test per Ship_Data._range_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_ships_range_eval_positive(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._range_eval()
                self.assertGreater(score, 0.0)

    def test_nuclear_carrier_range_capped(self):
        """Le portaerei nucleari (range 20000 nm) devono avere range_eval <= 1.5."""
        carrier = Ship_Data._registry[_CARRIER_MODEL]
        score = carrier._range_eval()
        self.assertLessEqual(score, 1.5)

    def test_nuclear_carrier_greater_than_corvette(self):
        """Una portaerei nucleare deve avere range_eval >> corvetta."""
        carrier_score  = Ship_Data._registry[_CARRIER_MODEL]._range_eval()
        corvette_score = Ship_Data._registry[_CORVETTE_MODEL]._range_eval()
        self.assertGreater(carrier_score, corvette_score)

    def test_range_proportional(self):
        """Nave con range maggiore deve avere _range_eval più alto."""
        cruiser  = Ship_Data._registry[_CRUISER_MODEL]          # 6000 nm
        corvette = Ship_Data._registry[_CORVETTE_MODEL]          # 2000 nm
        self.assertGreater(cruiser._range_eval(), corvette._range_eval())

    def test_deterministic(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._range_eval(), ship._range_eval(), places=9)


class TestReliabilityAndMaintenance(unittest.TestCase):
    """Unit test per _reliability_eval(), _maintenance_eval(), _avalaiability_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_ships_reliability_positive(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._reliability_eval()
                self.assertGreater(score, 0.0)

    def test_all_ships_maintenance_positive(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._maintenance_eval()
                self.assertGreater(score, 0.0)

    def test_all_ships_availability_non_negative(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._avalaiability_eval()
                self.assertGreaterEqual(score, 0.0)

    def test_nuclear_carrier_high_reliability(self):
        """Portaerei nucleari (mtbf=500) devono avere reliability_eval elevato."""
        carrier = Ship_Data._registry[_CARRIER_MODEL]
        corvette = Ship_Data._registry[_CORVETTE_MODEL]
        self.assertGreater(carrier._reliability_eval(), corvette._reliability_eval())

    def test_deterministic_reliability(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._reliability_eval(), ship._reliability_eval(), places=9)

    def test_deterministic_maintenance(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._maintenance_eval(), ship._maintenance_eval(), places=9)


class TestCombatEval(unittest.TestCase):
    """Unit test per Ship_Data._combat_eval()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_all_ships_combat_eval_positive(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj._combat_eval()
                self.assertGreater(score, 0.0)

    def test_deterministic(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        self.assertAlmostEqual(ship._combat_eval(), ship._combat_eval(), places=9)

    def test_destroyer_combat_higher_than_amphibious(self):
        """Un cacciatorpediniere deve avere combat_eval > nave da sbarco."""
        destroyer_score  = Ship_Data._registry[_DESTROYER_MODEL]._combat_eval()
        amphibious_score = Ship_Data._registry[_AMPHIBIOUS_MODEL]._combat_eval()
        self.assertGreater(destroyer_score, amphibious_score)


# ─────────────────────────────────────────────────────────────────────────────
#  4. METODO _normalize
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalize(unittest.TestCase):
    """Unit test per Ship_Data._normalize()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()
        self.obj = Ship_Data._registry[_CARRIER_MODEL]

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
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_weapon_score()
                self.assertIsInstance(score, (int, float))
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_category_scope_in_range(self):
        ship = Ship_Data._registry[_CRUISER_MODEL]
        score = ship.get_normalized_weapon_score(category="Cruiser")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        with self.assertRaises(ValueError):
            ship.get_normalized_weapon_score(category="INVALID_CATEGORY_XYZ")

    def test_cruiser_weapon_score_ge_corvette(self):
        """Un incrociatore deve avere weapon score >= corvetta a livello globale."""
        cruiser_score  = Ship_Data._registry[_CRUISER_MODEL].get_normalized_weapon_score()
        corvette_score = Ship_Data._registry[_CORVETTE_MODEL].get_normalized_weapon_score()
        self.assertGreaterEqual(cruiser_score, corvette_score)

    def test_deterministic(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        s1 = ship.get_normalized_weapon_score()
        s2 = ship.get_normalized_weapon_score()
        self.assertAlmostEqual(s1, s2, places=9)


class TestGetNormalizedRadarScore(unittest.TestCase):
    """Unit test per get_normalized_radar_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_radar_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        with self.assertRaises(ValueError):
            ship.get_normalized_radar_score(category="BAD_CAT")

    def test_aegis_destroyer_radar_greater_than_corvette(self):
        """Un cacciatorpediniere AEGIS ha radar superiore a una corvetta."""
        destroyer_score = Ship_Data._registry[_DESTROYER_MODEL].get_normalized_radar_score()
        corvette_score  = Ship_Data._registry[_CORVETTE_MODEL].get_normalized_radar_score()
        self.assertGreater(destroyer_score, corvette_score)

    def test_modes_sea_subset_in_range(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship.get_normalized_radar_score(modes=["sea"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_modes_air_subset_in_range(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship.get_normalized_radar_score(modes=["air"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_radar_score_air_and_sea_in_ship_dict(self):
        """SHIP dict deve contenere 'radar score air' e 'radar score sea'."""
        data = SHIP[_DESTROYER_MODEL]
        self.assertIn("radar score air", data)
        self.assertIn("radar score sea", data)


class TestGetNormalizedSpeedScore(unittest.TestCase):
    """Unit test per get_normalized_speed_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_speed_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            Ship_Data._registry[_CARRIER_MODEL].get_normalized_speed_score(
                category="NOT_A_VALID_CATEGORY"
            )

    def test_corvette_faster_than_carrier_normalized(self):
        """Corvette più veloce di portaerei a livello di score globale."""
        corvette_score = Ship_Data._registry[_CORVETTE_MODEL].get_normalized_speed_score()
        carrier_score  = Ship_Data._registry[_CARRIER_MODEL].get_normalized_speed_score()
        self.assertGreater(corvette_score, carrier_score)


class TestGetNormalizedRangeScore(unittest.TestCase):
    """Unit test per get_normalized_range_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_returns_float_in_range(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_range_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            Ship_Data._registry[_CARRIER_MODEL].get_normalized_range_score(
                category="INVALID_CATEGORY"
            )

    def test_nuclear_carrier_range_ge_corvette_normalized(self):
        """Portaerei nucleare ha range score >= corvetta."""
        carrier_score  = Ship_Data._registry[_CARRIER_MODEL].get_normalized_range_score()
        corvette_score = Ship_Data._registry[_CORVETTE_MODEL].get_normalized_range_score()
        self.assertGreaterEqual(carrier_score, corvette_score)


class TestGetNormalizedReliabilityAndAvailability(unittest.TestCase):
    """Unit test per get_normalized_reliability_score(), get_normalized_avalaiability_score(),
    get_normalized_maintenance_score()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_reliability_in_range(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_reliability_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_availability_in_range(self):
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_avalaiability_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_maintenance_in_range(self):
        for model, obj in Ship_Data._registry.items():
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
        for model, obj in Ship_Data._registry.items():
            with self.subTest(model=model):
                score = obj.get_normalized_combat_score()
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_category_scope_in_range(self):
        ship = Ship_Data._registry[_DESTROYER_MODEL]
        score = ship.get_normalized_combat_score(category="Destroyer")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            Ship_Data._registry[_CARRIER_MODEL].get_normalized_combat_score(
                category="BAD"
            )

    def test_destroyer_combat_ge_amphibious_normalized(self):
        """Cacciatorpediniere ha combat score >= nave da sbarco."""
        destroyer_score  = Ship_Data._registry[_DESTROYER_MODEL].get_normalized_combat_score()
        amphibious_score = Ship_Data._registry[_AMPHIBIOUS_MODEL].get_normalized_combat_score()
        self.assertGreaterEqual(destroyer_score, amphibious_score)


# ─────────────────────────────────────────────────────────────────────────────
#  6. FUNZIONI STATICHE — get_ship_data, get_ship_scores
# ─────────────────────────────────────────────────────────────────────────────

class TestGetShipData(unittest.TestCase):
    """Unit test per get_ship_data()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_known_model_returns_dict(self):
        result = get_ship_data(_CARRIER_MODEL)
        self.assertIsInstance(result, dict)

    def test_result_non_empty(self):
        result = get_ship_data(_CARRIER_MODEL)
        self.assertGreater(len(result), 0)

    def test_result_has_combat_score(self):
        result = get_ship_data(_CARRIER_MODEL)
        self.assertIn("combat score", result)

    def test_result_has_weapon_score(self):
        result = get_ship_data(_CARRIER_MODEL)
        self.assertIn("weapon score", result)

    def test_result_has_all_scores(self):
        result = get_ship_data(_DESTROYER_MODEL)
        for key in SCORES:
            with self.subTest(key=key):
                self.assertIn(key, result)

    def test_all_models_findable(self):
        for model in Ship_Data._registry:
            with self.subTest(model=model):
                result = get_ship_data(model)
                self.assertIsNotNone(result)

    def test_unknown_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_ship_data("SHIP_NOT_EXISTING_XYZ")

    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_ship_data("")


class TestGetShipScores(unittest.TestCase):
    """Unit test per get_ship_scores()."""

    def setUp(self):
        self._patcher = patch(_LOGGER_PATH, MagicMock())
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_unknown_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_ship_scores("SHIP_NOT_EXISTING_XYZ")

    def test_default_scores_returns_all(self):
        """Senza parametro scores, restituisce tutti i punteggi."""
        result = get_ship_scores(_CARRIER_MODEL)
        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), set(SCORES))

    def test_single_score_returns_subset(self):
        """Con scores=['combat score'], restituisce solo combat score."""
        result = get_ship_scores(_CARRIER_MODEL, scores=["combat score"])
        self.assertIsInstance(result, dict)
        self.assertIn("combat score", result)
        self.assertEqual(len(result), 1)

    def test_multiple_scores_returns_requested_subset(self):
        result = get_ship_scores(
            _DESTROYER_MODEL,
            scores=["combat score", "weapon score", "radar score"],
        )
        self.assertIn("combat score", result)
        self.assertIn("weapon score", result)
        self.assertIn("radar score", result)
        self.assertEqual(len(result), 3)

    def test_invalid_score_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_ship_scores(_CARRIER_MODEL, scores=["INVALID_SCORE_XYZ"])

    def test_result_values_have_global_and_category(self):
        result = get_ship_scores(_CARRIER_MODEL, scores=["combat score"])
        score_dict = result["combat score"]
        self.assertIn("global_score", score_dict)
        self.assertIn("category_score", score_dict)


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY PER LA GENERAZIONE DELLE TABELLE
# ─────────────────────────────────────────────────────────────────────────────

def _is_nan(value) -> bool:
    try:
        return value != value
    except Exception:
        return False


def _safe_normalized_weapon_score(ship: Ship_Data, cat: str) -> float:
    """Restituisce get_normalized_weapon_score(category=cat) con logger mockato."""
    try:
        with patch(_LOGGER_PATH, MagicMock()):
            return ship.get_normalized_weapon_score(category=cat)
    except Exception:
        return float("nan")


def _ships_by_category() -> dict:
    """Restituisce un dict {category: [Ship_Data, ...]} ordinato per categoria."""
    result: dict = {}
    for obj in Ship_Data._registry.values():
        result.setdefault(obj.category, []).append(obj)
    return result


def _ships_with_weapon_type(wtype: str) -> dict:
    """Restituisce {category: [Ship_Data, ...]} per le navi che montano
    armi del tipo specificato (es. 'MISSILES_SAM', 'GUNS', ...)."""
    result: dict = {}
    for obj in Ship_Data._registry.values():
        if wtype in obj.weapons and obj.weapons[wtype]:
            result.setdefault(obj.category, []).append(obj)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  STAMPA A TERMINALE
# ─────────────────────────────────────────────────────────────────────────────

def print_ship_scores_tables() -> None:
    """Stampa a terminale Ship_Scores: per ogni categoria nave, la tabella
    con tutti i punteggi normalizzati (global e category)."""
    cat_map = _ships_by_category()

    for cat, ships in sorted(cat_map.items()):
        if cat not in SHIP_CATEGORIES:
            continue
        header = f"  CATEGORIA: {cat}  —  punteggi normalizzati"
        width = max(80, len(header) + 4)
        print()
        print("═" * width)
        print(header)
        print("═" * width)

        # Raccoglie score names dal primo modello disponibile
        sample_model = ships[0].model
        score_names = list(SHIP.get(sample_model, {}).keys())

        col_m = max(16, max(len(s.model) for s in ships))
        col_s = 12

        for score_name in score_names:
            print(f"\n  [ {score_name} ]")
            header_row = f"  {'Model':<{col_m}}   {'global':>{col_s}}   {'category':>{col_s}}"
            print("─" * len(header_row))
            print(header_row)
            print("─" * len(header_row))

            rows = []
            for s in ships:
                sd = SHIP.get(s.model, {}).get(score_name, {})
                gs = sd.get("global_score", float("nan"))
                cs = sd.get("category_score", float("nan"))
                rows.append((s.model, gs, cs))
            rows.sort(key=lambda x: x[2] if not _is_nan(x[2]) else -1, reverse=True)

            for model, gs, cs in rows:
                gs_str = f"{gs:.4f}" if not _is_nan(gs) else "   N/A  "
                cs_str = f"{cs:.4f}" if not _is_nan(cs) else "   N/A  "
                print(f"  {model:<{col_m}}   {gs_str:>{col_s}}   {cs_str:>{col_s}}")
        print()


def print_weapon_score_tables(weapon_type_list: List[str]) -> None:
    """Stampa a terminale la tabella get_normalized_weapon_score() per ogni
    tipo di arma navale e per ogni categoria che monta quell'arma."""
    for wtype in weapon_type_list:
        cat_map = _ships_with_weapon_type(wtype)
        if not cat_map:
            print(f"\n[SKIP] Nessuna nave con armamento '{wtype}'.\n")
            continue

        for cat, ships in sorted(cat_map.items()):
            header = f"  WEAPON TYPE: {wtype}  |  CATEGORIA: {cat}   —   get_normalized_weapon_score()"
            width = max(80, len(header) + 4)
            print()
            print("═" * width)
            print(header)
            print("═" * width)

            col_m = max(16, max(len(s.model) for s in ships))
            col_s = 14
            print(f"  {'Model':<{col_m}}   {'category_score':>{col_s}}")
            print("─" * (col_m + col_s + 8))

            rows = [
                (s.model, _safe_normalized_weapon_score(s, cat))
                for s in ships
            ]
            rows.sort(key=lambda x: x[1] if not _is_nan(x[1]) else -1, reverse=True)

            for model, score in rows:
                s_str = f"{score:.6f}" if not _is_nan(score) else "     N/A     "
                print(f"  {model:<{col_m}}   {s_str:>{col_s}}")
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


def save_ship_scores_pdf(output_path: str) -> None:
    """Salva Ship_Scores.pdf con una pagina per categoria nave.
    Ogni pagina mostra tutti i punteggi normalizzati (global_score, category_score)
    per ogni nave nella categoria, con colorazione heatmap (verde=alto, rosso=basso)."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cat_map = _ships_by_category()

    with PdfPages(output_path) as pdf:
        for cat in SHIP_CATEGORIES:
            ships = cat_map.get(cat, [])
            if not ships:
                continue

            sample_model = ships[0].model
            score_names = list(SHIP.get(sample_model, {}).keys())

            col_labels = ["Score", "Scope"] + [s.model for s in ships]
            cell_text = []
            score_matrix = []

            for score_name in score_names:
                for scope in ("global_score", "category_score"):
                    row_vals = []
                    for s in ships:
                        val = SHIP.get(s.model, {}).get(score_name, {}).get(scope, float("nan"))
                        row_vals.append(val)
                    score_matrix.append(row_vals)
                    row_str = [score_name, scope.replace("_score", "")] + [
                        f"{v:.3f}" if not _is_nan(v) else "N/A" for v in row_vals
                    ]
                    cell_text.append(row_str)

            all_vals = [v for row in score_matrix for v in row if not _is_nan(v)]
            max_s = max(all_vals) if all_vals else 1.0
            min_s = min(all_vals) if all_vals else 0.0
            rng = (max_s - min_s) if max_s != min_s else 1.0

            cell_colors = []
            for row_vals in score_matrix:
                row_colors = ["#f0f4f8", "#e8ecf0"]
                for v in row_vals:
                    if not _is_nan(v):
                        row_colors.append(plt.cm.RdYlGn((v - min_s) / rng))
                    else:
                        row_colors.append((0.87, 0.87, 0.87, 1.0))
                cell_colors.append(row_colors)

            n_rows = len(cell_text)
            n_cols = len(col_labels)
            fig_w = max(14.0, 1.8 * len(ships) + 4.0)
            fig_h = max(5.0, 0.32 * n_rows + 2.5)

            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.axis("off")
            ax.set_title(
                f"Ship Scores — Categoria: {cat}\n"
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

    print(f"[PDF] Ship_Scores → {output_path}")


def save_ship_weapon_score_pdf(
    weapon_type_list: List[str],
    output_path: str,
) -> None:
    """Salva ship_weapon_score_tables.pdf.
    Per ogni tipo di arma e per ogni categoria nave che monta quell'arma:
    una pagina con la tabella get_normalized_weapon_score() ordinata per punteggio
    decrescente, con colorazione heatmap (verde=alto, rosso=basso)."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    with PdfPages(output_path) as pdf:
        for wtype in weapon_type_list:
            cat_map = _ships_with_weapon_type(wtype)
            if not cat_map:
                continue

            for cat in SHIP_CATEGORIES:
                ships = cat_map.get(cat, [])
                if not ships:
                    continue

                rows = [
                    (s.model, _safe_normalized_weapon_score(s, cat))
                    for s in ships
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
                    colLabels=["#", "Modello Nave", "Score Normalizzato"],
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

    print(f"[PDF] ship_weapon_score_tables → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        TestShipDataModuleStructure,
        TestShipDataAttributes,
        TestWeaponEval,
        TestRadarEval,
        TestSpeedEval,
        TestRangeEval,
        TestReliabilityAndMaintenance,
        TestCombatEval,
        TestNormalize,
        TestGetNormalizedWeaponScore,
        TestGetNormalizedRadarScore,
        TestGetNormalizedSpeedScore,
        TestGetNormalizedRangeScore,
        TestGetNormalizedReliabilityAndAvailability,
        TestGetNormalizedCombatScore,
        TestGetShipData,
        TestGetShipScores,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def _run_tables_terminal() -> None:
    print("\n" + "=" * 70)
    print("  SHIP SCORES — punteggi per categoria")
    print("=" * 70)
    print_ship_scores_tables()

    print("\n" + "=" * 70)
    print("  WEAPON SCORE — get_normalized_weapon_score()")
    print("=" * 70)
    print_weapon_score_tables(weapon_type)


def _run_tables_pdf() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_ship_scores_pdf(
        os.path.join(OUTPUT_DIR, "Ship_Scores.pdf"),
    )
    save_ship_weapon_score_pdf(
        weapon_type,
        os.path.join(OUTPUT_DIR, "ship_weapon_score_tables.pdf"),
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
    print("║       Test_Ship_Data  —  Menu principale                    ║")
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
