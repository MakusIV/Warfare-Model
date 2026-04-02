"""
Test_Ship_Weapon_Data.py
========================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo
Ship_Weapon_Data.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Ship_Weapon_Data.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ship_Weapon_Data.py            # menu interattivo
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ship_Weapon_Data.py --tables-only
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ship_Weapon_Data.py --tests-only

Note sul modulo sotto test:
  - SHIP_WEAPONS: dizionario principale con categorie MISSILES_SAM, MISSILES_ASM,
    MISSILES_TORPEDO, GUNS, CIWS.
  - TARGET_DIMENSION = ['small', 'med', 'big']: dimensioni valide per il target.
  - get_ship_weapon(model: str): cerca il modello in SHIP_WEAPONS e restituisce
    {"weapons_category": str, "weapons_data": dict} oppure None se non trovato.
    Lancia TypeError se model non è una stringa.
  - get_weapon_score(weapon_type, weapon_model): dispatcher con due argomenti;
    lancia ValueError per weapon_type sconosciuto, TypeError per tipi non stringa.
  - Tutte le funzioni di score usano .get() internamente → modello sconosciuto
    restituisce 0.0 (non KeyError).
  - get_weapon_score_target(model: str, target_type: List, target_dimension: List):
    media di accuracy * destroy_capacity su tutte le combinazioni valide.
    Deterministica (nessuna componente stocastica).
  - Siluri: efficacy 0.0 vs tutti i bersagli a terra (land-attack non supportato).
  - SAM e CIWS: efficacy molto ridotta vs bersagli di superficie e navali.
  - Non esiste AMMO_PARAM né AMMO_TARGET_EFFECTIVENESS in Ship_Weapon_Data.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List, Dict

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAZIONE — modificare le liste per personalizzare le tabelle
# ─────────────────────────────────────────────────────────────────────────────

# Categorie per le tabelle get_weapon_score()
WEAPON_TYPE_SCORE: List[str] = [
    "MISSILES_SAM",
    "MISSILES_ASM",
    "MISSILES_TORPEDO",
    "GUNS",
    "CIWS",
]

# Categorie per le tabelle get_weapon_score_target()
WEAPON_TYPE_TARGET: List[str] = [
    "MISSILES_SAM",
    "MISSILES_ASM",
    "MISSILES_TORPEDO",
    "GUNS",
    "CIWS",
]

# Tipi di bersaglio per get_weapon_score_target()
TARGET_TYPE: List[str] = [
    "Soft", "Armored", "Hard", "Structure", "ship",
]

# Dimensioni del bersaglio per get_weapon_score_target().
# Ogni voce genera una colonna nella tabella con distribuzione {dim: 1.0}.
TARGET_DIMENSION: List[str] = ["big", "med", "small"]

# Directory di output per i PDF
OUTPUT_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "..", "out",
    )
)

# Percorso del logger da sostituire con MagicMock nei test
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import (
    SHIP_WEAPONS,
    WEAPON_PARAM,
    TARGET_DIMENSION as SWD_TARGET_DIMENSION,
    get_sam_score,
    get_asm_score,
    get_torpedo_score,
    get_gun_score,
    get_ciws_score,
    get_weapon_score,
    get_ship_weapon,
    get_weapon_score_target,
    get_weapon_score_target_distribuition,
)

# ─────────────────────────────────────────────────────────────────────────────
#  UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# 1. Struttura dati del modulo
# ---------------------------------------------------------------------------

class TestShipWeaponsDataStructure(unittest.TestCase):
    """Verifica la correttezza strutturale dei dizionari SHIP_WEAPONS e WEAPON_PARAM."""

    # ── SHIP_WEAPONS ─────────────────────────────────────────────────────────

    def test_ship_weapons_has_expected_categories(self):
        """SHIP_WEAPONS deve contenere le cinque categorie navali attese."""
        expected = {
            "MISSILES_SAM", "MISSILES_ASM", "MISSILES_TORPEDO", "GUNS", "CIWS",
        }
        for cat in expected:
            with self.subTest(category=cat):
                self.assertIn(cat, SHIP_WEAPONS)

    def test_ship_weapons_all_values_are_dicts(self):
        """Ogni categoria deve essere un dizionario non vuoto."""
        for cat, content in SHIP_WEAPONS.items():
            with self.subTest(category=cat):
                self.assertIsInstance(content, dict)
                self.assertGreater(len(content), 0, f"Categoria '{cat}' è vuota")

    def test_missiles_sam_count(self):
        """MISSILES_SAM deve contenere esattamente 12 armi."""
        self.assertEqual(len(SHIP_WEAPONS["MISSILES_SAM"]), 12)

    def test_missiles_asm_count(self):
        """MISSILES_ASM deve contenere esattamente 8 armi."""
        self.assertEqual(len(SHIP_WEAPONS["MISSILES_ASM"]), 8)

    def test_missiles_torpedo_count(self):
        """MISSILES_TORPEDO deve contenere esattamente 5 armi."""
        self.assertEqual(len(SHIP_WEAPONS["MISSILES_TORPEDO"]), 5)

    def test_guns_count(self):
        """GUNS deve contenere esattamente 6 armi."""
        self.assertEqual(len(SHIP_WEAPONS["GUNS"]), 6)

    def test_ciws_count(self):
        """CIWS deve contenere esattamente 3 armi."""
        self.assertEqual(len(SHIP_WEAPONS["CIWS"]), 3)

    def test_sam_weapon_has_required_fields(self):
        """Ogni arma in MISSILES_SAM deve avere i campi fondamentali."""
        required = {"model", "caliber", "warhead", "range", "speed", "efficiency"}
        for model, data in SHIP_WEAPONS["MISSILES_SAM"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MISSILES_SAM/{model}")

    def test_asm_weapon_has_required_fields(self):
        """Ogni arma in MISSILES_ASM deve avere i campi fondamentali."""
        required = {"model", "caliber", "warhead", "range", "speed", "efficiency"}
        for model, data in SHIP_WEAPONS["MISSILES_ASM"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MISSILES_ASM/{model}")

    def test_torpedo_weapon_has_required_fields(self):
        """Ogni arma in MISSILES_TORPEDO deve avere i campi fondamentali."""
        required = {"model", "caliber", "warhead", "range", "speed", "efficiency"}
        for model, data in SHIP_WEAPONS["MISSILES_TORPEDO"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MISSILES_TORPEDO/{model}")

    def test_gun_weapon_has_required_fields(self):
        """Ogni arma in GUNS deve avere i campi fondamentali."""
        required = {"model", "caliber", "muzzle_speed", "fire_rate", "range", "efficiency"}
        for model, data in SHIP_WEAPONS["GUNS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in GUNS/{model}")

    def test_ciws_weapon_has_required_fields(self):
        """Ogni arma in CIWS deve avere i campi fondamentali (senza muzzle_speed e warhead)."""
        required = {"model", "caliber", "fire_rate", "range", "efficiency"}
        for model, data in SHIP_WEAPONS["CIWS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in CIWS/{model}")

    def test_efficiency_structure_has_all_target_types(self):
        """Per ogni arma, il template 'efficiency' deve contenere tutti i target type standard."""
        expected_types = {
            "Soft", "Armored", "Hard", "Structure", "Air_Defense",
            "Airbase", "Port", "Shipyard", "Farp", "Stronghold", "ship",
        }
        for cat in SHIP_WEAPONS:
            for model, data in SHIP_WEAPONS[cat].items():
                eff = data.get("efficiency", {})
                for t in expected_types:
                    with self.subTest(category=cat, model=model, target=t):
                        self.assertIn(t, eff,
                                      f"Target '{t}' mancante in efficiency di {cat}/{model}")

    def test_efficiency_structure_has_all_dimensions(self):
        """Ogni target_type nel template efficiency deve avere big/med/small."""
        for cat in ("MISSILES_SAM", "MISSILES_ASM", "GUNS"):
            for model, data in SHIP_WEAPONS[cat].items():
                eff = data.get("efficiency", {})
                for t_type, t_data in eff.items():
                    for dim in ("big", "med", "small"):
                        with self.subTest(cat=cat, model=model, target=t_type, dim=dim):
                            self.assertIn(dim, t_data,
                                          f"Dimensione '{dim}' mancante in {cat}/{model}/{t_type}")

    def test_efficiency_dim_has_accuracy_and_destroy_capacity(self):
        """Ogni cella efficiency deve contenere 'accuracy' e 'destroy_capacity'."""
        first_sam = next(iter(SHIP_WEAPONS["MISSILES_SAM"]))
        eff = SHIP_WEAPONS["MISSILES_SAM"][first_sam]["efficiency"]
        for t_type, t_data in eff.items():
            for dim in ("big", "med", "small"):
                cell = t_data.get(dim, {})
                with self.subTest(model=first_sam, target=t_type, dim=dim):
                    self.assertIn("accuracy", cell)
                    self.assertIn("destroy_capacity", cell)

    def test_caliber_is_positive_for_all_weapons(self):
        """Il calibro deve essere un numero positivo per tutte le armi."""
        for cat, weapons in SHIP_WEAPONS.items():
            for model, data in weapons.items():
                with self.subTest(category=cat, model=model):
                    self.assertIsInstance(data["caliber"], (int, float))
                    self.assertGreater(data["caliber"], 0)

    def test_perc_efficiency_variability_in_range(self):
        """perc_efficiency_variability deve essere float in (0, 1] per ogni arma."""
        for cat, weapons in SHIP_WEAPONS.items():
            for model, data in weapons.items():
                with self.subTest(category=cat, model=model):
                    pev = data.get("perc_efficiency_variability")
                    self.assertIsNotNone(pev, f"Campo mancante in {cat}/{model}")
                    self.assertIsInstance(pev, float)
                    self.assertGreater(pev, 0.0)
                    self.assertLessEqual(pev, 1.0)

    # ── WEAPON_PARAM ─────────────────────────────────────────────────────────

    def test_weapon_param_has_all_categories(self):
        """WEAPON_PARAM deve contenere le cinque categorie navali."""
        expected = {
            "MISSILES_SAM", "MISSILES_ASM", "MISSILES_TORPEDO", "GUNS", "CIWS",
        }
        for cat in expected:
            with self.subTest(category=cat):
                self.assertIn(cat, WEAPON_PARAM)

    def test_weapon_param_values_are_positive_floats(self):
        """Tutti i coefficienti in WEAPON_PARAM devono essere float > 0."""
        for cat, params in WEAPON_PARAM.items():
            for param, coeff in params.items():
                with self.subTest(category=cat, param=param):
                    self.assertIsInstance(coeff, float)
                    self.assertGreater(coeff, 0.0)

    def test_weapon_param_sam_has_expected_keys(self):
        """WEAPON_PARAM['MISSILES_SAM'] deve avere caliber, warhead, range, speed."""
        expected_keys = {"caliber", "warhead", "range", "speed"}
        self.assertEqual(set(WEAPON_PARAM["MISSILES_SAM"].keys()), expected_keys)

    def test_weapon_param_asm_has_expected_keys(self):
        """WEAPON_PARAM['MISSILES_ASM'] deve avere caliber, warhead, range, speed."""
        expected_keys = {"caliber", "warhead", "range", "speed"}
        self.assertEqual(set(WEAPON_PARAM["MISSILES_ASM"].keys()), expected_keys)

    def test_weapon_param_torpedo_has_expected_keys(self):
        """WEAPON_PARAM['MISSILES_TORPEDO'] deve avere caliber, warhead, range, speed."""
        expected_keys = {"caliber", "warhead", "range", "speed"}
        self.assertEqual(set(WEAPON_PARAM["MISSILES_TORPEDO"].keys()), expected_keys)

    def test_weapon_param_guns_has_expected_keys(self):
        """WEAPON_PARAM['GUNS'] deve avere caliber, muzzle_speed, fire_rate, range."""
        expected_keys = {"caliber", "muzzle_speed", "fire_rate", "range"}
        self.assertEqual(set(WEAPON_PARAM["GUNS"].keys()), expected_keys)

    def test_weapon_param_ciws_has_expected_keys(self):
        """WEAPON_PARAM['CIWS'] deve avere caliber, fire_rate, range."""
        expected_keys = {"caliber", "fire_rate", "range"}
        self.assertEqual(set(WEAPON_PARAM["CIWS"].keys()), expected_keys)

    # ── TARGET_DIMENSION ─────────────────────────────────────────────────────

    def test_target_dimension_has_three_values(self):
        """TARGET_DIMENSION del modulo deve contenere esattamente 'small', 'med', 'big'."""
        self.assertEqual(set(SWD_TARGET_DIMENSION), {"small", "med", "big"})

    def test_target_dimension_values_are_strings(self):
        """Tutti i valori di TARGET_DIMENSION devono essere stringhe."""
        for dim in SWD_TARGET_DIMENSION:
            with self.subTest(dim=dim):
                self.assertIsInstance(dim, str)


# ---------------------------------------------------------------------------
# 2. get_sam_score
# ---------------------------------------------------------------------------

class TestGetSamScore(unittest.TestCase):
    """Unit test per get_sam_score().
    Usa .get() internamente → modello sconosciuto restituisce 0.0 (non KeyError)."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_rim66_sm2_returns_positive(self):
        """RIM-66-SM-2 (SAM LORAD) deve restituire un punteggio > 0."""
        score = get_sam_score("RIM-66-SM-2")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_rim162_essm_returns_positive(self):
        """RIM-162-ESSM (SAM MERAD) deve restituire un punteggio > 0."""
        score = get_sam_score("RIM-162-ESSM")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_sa_n4_returns_positive(self):
        """SA-N-4-Gecko (SAM SHORAD) deve restituire un punteggio > 0."""
        score = get_sam_score("SA-N-4-Gecko")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_sam_return_positive(self):
        """Tutti i SAM in SHIP_WEAPONS devono restituire un punteggio > 0."""
        for model in SHIP_WEAPONS["MISSILES_SAM"]:
            with self.subTest(model=model):
                score = get_sam_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_lorad_scores_higher_than_shorad(self):
        """S-300F (LORAD, calibro 508mm, portata 150km) deve superare SA-N-4-Gecko (SHORAD)."""
        score_lorad = get_sam_score("S-300F")
        score_shorad = get_sam_score("SA-N-4-Gecko")
        self.assertGreater(score_lorad, score_shorad)

    def test_rim156_sm2er_scores_higher_than_rim7m(self):
        """RIM-156-SM-2ER (portata 240km) deve superare RIM-7M-Sea-Sparrow (19km)."""
        score_er = get_sam_score("RIM-156-SM-2ER")
        score_sp = get_sam_score("RIM-7M-Sea-Sparrow")
        self.assertGreater(score_er, score_sp)

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0 (usa .get() internamente)."""
        score = get_sam_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_sam_score(120)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_sam_score(None)

    def test_type_error_on_list(self):
        with self.assertRaises(TypeError):
            get_sam_score(["RIM-66-SM-2"])


# ---------------------------------------------------------------------------
# 3. get_asm_score
# ---------------------------------------------------------------------------

class TestGetAsmScore(unittest.TestCase):
    """Unit test per get_asm_score().
    Usa .get() internamente → modello sconosciuto restituisce 0.0."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_harpoon_returns_positive(self):
        """RGM-84-Harpoon (ASM subsonico anti-nave) deve restituire un punteggio > 0."""
        score = get_asm_score("RGM-84-Harpoon")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_tomahawk_returns_positive(self):
        """BGM-109-Tomahawk (ASM crociera, land-attack) deve restituire un punteggio > 0."""
        score = get_asm_score("BGM-109-Tomahawk")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_p700_granit_returns_positive(self):
        """P-700-Granit (ASM supersonico pesante) deve restituire un punteggio > 0."""
        score = get_asm_score("P-700-Granit")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_asm_return_positive(self):
        """Tutti i missili ASM in SHIP_WEAPONS devono restituire un punteggio > 0."""
        for model in SHIP_WEAPONS["MISSILES_ASM"]:
            with self.subTest(model=model):
                score = get_asm_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_heavy_supersonic_scores_higher_than_subsonic(self):
        """P-700-Granit (testata 750kg) deve superare RGM-84-Harpoon (testata 221kg)."""
        score_heavy = get_asm_score("P-700-Granit")
        score_sub   = get_asm_score("RGM-84-Harpoon")
        self.assertGreater(score_heavy, score_sub)

    def test_tomahawk_scores_high_due_to_range(self):
        """BGM-109-Tomahawk (portata 1600km, massima in ASM) deve avere uno score elevato."""
        score_toma = get_asm_score("BGM-109-Tomahawk")
        score_yj83 = get_asm_score("YJ-83")
        self.assertGreater(score_toma, score_yj83)

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_asm_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_asm_score(84)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_asm_score(None)


# ---------------------------------------------------------------------------
# 4. get_torpedo_score
# ---------------------------------------------------------------------------

class TestGetTorpedoScore(unittest.TestCase):
    """Unit test per get_torpedo_score().
    Usa .get() internamente → modello sconosciuto restituisce 0.0."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_mk48_returns_positive(self):
        """Mk-48 (siluro pesante, testata 290kg) deve restituire un punteggio > 0."""
        score = get_torpedo_score("Mk-48")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_mk46_returns_positive(self):
        """Mk-46 (siluro leggero anti-sub) deve restituire un punteggio > 0."""
        score = get_torpedo_score("Mk-46")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_torpedoes_return_positive(self):
        """Tutti i siluri in SHIP_WEAPONS devono restituire un punteggio > 0."""
        for model in SHIP_WEAPONS["MISSILES_TORPEDO"]:
            with self.subTest(model=model):
                score = get_torpedo_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_heavy_torpedo_scores_higher_than_light(self):
        """Mk-48 (siluro pesante, testata 290kg, portata 50km) deve superare Mk-46
        (siluro leggero, testata 44kg, portata 11km)."""
        score_heavy = get_torpedo_score("Mk-48")
        score_light = get_torpedo_score("Mk-46")
        self.assertGreater(score_heavy, score_light)

    def test_test71_returns_positive(self):
        """TEST-71 (siluro russo pesante) deve restituire un punteggio > 0."""
        score = get_torpedo_score("TEST-71")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_torpedo_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_torpedo_score(533)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_torpedo_score(None)

    def test_type_error_on_float(self):
        with self.assertRaises(TypeError):
            get_torpedo_score(48.0)


# ---------------------------------------------------------------------------
# 5. get_gun_score
# ---------------------------------------------------------------------------

class TestGetGunScore(unittest.TestCase):
    """Unit test per get_gun_score().
    Usa .get() internamente → modello sconosciuto restituisce 0.0."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_ak130_returns_positive(self):
        """AK-130-130mm (calibro massimo) deve restituire un punteggio > 0."""
        score = get_gun_score("AK-130-130mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_oto_melara_76mm_returns_positive(self):
        """OTO-Melara-76mm deve restituire un punteggio > 0."""
        score = get_gun_score("OTO-Melara-76mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_mk45_5in_returns_positive(self):
        """Mk-45-5in (127mm, cannone US standard) deve restituire un punteggio > 0."""
        score = get_gun_score("Mk-45-5in")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_guns_return_positive(self):
        """Tutti i cannoni navali in SHIP_WEAPONS devono restituire un punteggio > 0."""
        for model in SHIP_WEAPONS["GUNS"]:
            with self.subTest(model=model):
                score = get_gun_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_large_caliber_scores_higher_than_small(self):
        """AK-130-130mm (calibro 130mm, portata 25km) deve superare OTO-Melara-76mm
        (calibro 76mm, portata 16km)."""
        score_130 = get_gun_score("AK-130-130mm")
        score_76  = get_gun_score("OTO-Melara-76mm")
        self.assertGreater(score_130, score_76)

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_gun_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_gun_score(130)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_gun_score(None)

    def test_type_error_on_list(self):
        with self.assertRaises(TypeError):
            get_gun_score(["AK-130-130mm"])


# ---------------------------------------------------------------------------
# 6. get_ciws_score
# ---------------------------------------------------------------------------

class TestGetCiwsScore(unittest.TestCase):
    """Unit test per get_ciws_score().
    Usa .get() internamente → modello sconosciuto restituisce 0.0."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_phalanx_returns_positive(self):
        """Mk-15-Phalanx deve restituire un punteggio > 0."""
        score = get_ciws_score("Mk-15-Phalanx")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_ak630_returns_positive(self):
        """AK-630 (30mm, cadenza 5000rpm) deve restituire un punteggio > 0."""
        score = get_ciws_score("AK-630")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_type730_returns_positive(self):
        """Type-730 (cadenza massima 5800rpm) deve restituire un punteggio > 0."""
        score = get_ciws_score("Type-730")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_ciws_return_positive(self):
        """Tutti i CIWS in SHIP_WEAPONS devono restituire un punteggio > 0."""
        for model in SHIP_WEAPONS["CIWS"]:
            with self.subTest(model=model):
                score = get_ciws_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_higher_fire_rate_scores_higher(self):
        """Type-730 (5800rpm, portata 4km) deve superare Mk-15-Phalanx (4500rpm, portata 1.5km)."""
        score_730     = get_ciws_score("Type-730")
        score_phalanx = get_ciws_score("Mk-15-Phalanx")
        self.assertGreater(score_730, score_phalanx)

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_ciws_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_ciws_score(20)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_ciws_score(None)


# ---------------------------------------------------------------------------
# 7. get_weapon_score — dispatcher
# ---------------------------------------------------------------------------

class TestGetWeaponScoreDispatcher(unittest.TestCase):
    """Unit test per get_weapon_score() (dispatcher).
    Verifica che delega correttamente alle funzioni specializzate e
    valida i parametri di ingresso."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    # ── delega corretta ──────────────────────────────────────────────────────

    def test_dispatches_missiles_sam(self):
        """MISSILES_SAM → uguale a get_sam_score."""
        self.assertAlmostEqual(
            get_weapon_score("MISSILES_SAM", "RIM-66-SM-2"),
            get_sam_score("RIM-66-SM-2"),
        )

    def test_dispatches_missiles_asm(self):
        """MISSILES_ASM → uguale a get_asm_score."""
        self.assertAlmostEqual(
            get_weapon_score("MISSILES_ASM", "RGM-84-Harpoon"),
            get_asm_score("RGM-84-Harpoon"),
        )

    def test_dispatches_missiles_torpedo(self):
        """MISSILES_TORPEDO → uguale a get_torpedo_score."""
        self.assertAlmostEqual(
            get_weapon_score("MISSILES_TORPEDO", "Mk-48"),
            get_torpedo_score("Mk-48"),
        )

    def test_dispatches_guns(self):
        """GUNS → uguale a get_gun_score."""
        self.assertAlmostEqual(
            get_weapon_score("GUNS", "AK-130-130mm"),
            get_gun_score("AK-130-130mm"),
        )

    def test_dispatches_ciws(self):
        """CIWS → uguale a get_ciws_score."""
        self.assertAlmostEqual(
            get_weapon_score("CIWS", "Mk-15-Phalanx"),
            get_ciws_score("Mk-15-Phalanx"),
        )

    # ── validazione parametri ────────────────────────────────────────────────

    def test_invalid_weapon_type_not_string_raises_typeerror(self):
        """weapon_type non-string → TypeError."""
        with self.assertRaises((ValueError, TypeError)):
            get_weapon_score(123, "RIM-66-SM-2")

    def test_invalid_weapon_type_unknown_raises_valueerror(self):
        """weapon_type sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            get_weapon_score("UNKNOWN_CATEGORY", "RIM-66-SM-2")

    def test_invalid_model_not_string_raises_typeerror(self):
        """weapon_model non-string → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score("MISSILES_SAM", 120)

    def test_invalid_model_none_raises_typeerror(self):
        """weapon_model None → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score("MISSILES_SAM", None)

    # ── tipo e range dei valori ──────────────────────────────────────────────

    def test_return_type_is_float_for_all_categories(self):
        """Il dispatcher deve restituire float per tutte le categorie."""
        sample_models = {
            "MISSILES_SAM":     "RIM-66-SM-2",
            "MISSILES_ASM":     "RGM-84-Harpoon",
            "MISSILES_TORPEDO": "Mk-48",
            "GUNS":             "AK-130-130mm",
            "CIWS":             "Mk-15-Phalanx",
        }
        for wtype, model in sample_models.items():
            with self.subTest(weapon_type=wtype):
                score = get_weapon_score(wtype, model)
                self.assertIsInstance(score, float)

    def test_score_non_negative(self):
        """I punteggi non devono essere negativi."""
        sample_models = {
            "MISSILES_SAM":     "RIM-66-SM-2",
            "MISSILES_ASM":     "RGM-84-Harpoon",
            "MISSILES_TORPEDO": "Mk-48",
            "GUNS":             "AK-130-130mm",
            "CIWS":             "Mk-15-Phalanx",
        }
        for wtype, model in sample_models.items():
            with self.subTest(weapon_type=wtype):
                score = get_weapon_score(wtype, model)
                self.assertGreaterEqual(score, 0.0)


# ---------------------------------------------------------------------------
# 8. get_ship_weapon
# ---------------------------------------------------------------------------

class TestGetShipWeapon(unittest.TestCase):
    """Unit test per get_ship_weapon(model: str).

    Firma: get_ship_weapon(model: str) -> Optional[Dict[str, Any]]
    - model: stringa identificativa del modello
    - Ritorna {"weapons_category": str, "weapons_data": dict} se trovato, None altrimenti
    - Lancia TypeError se model non è una stringa
    """

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    # ── tipo e struttura del risultato ────────────────────────────────────────

    def test_known_sam_returns_dict(self):
        """RIM-66-SM-2 → dict non-None."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_weapons_category_key(self):
        """Il risultato deve contenere la chiave 'weapons_category'."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertIn("weapons_category", result)

    def test_result_has_weapons_data_key(self):
        """Il risultato deve contenere la chiave 'weapons_data'."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertIn("weapons_data", result)

    def test_result_has_exactly_two_keys(self):
        """Il risultato deve avere esattamente due chiavi."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertEqual(set(result.keys()), {"weapons_category", "weapons_data"})

    def test_weapons_data_is_dict(self):
        """weapons_data deve essere un dizionario."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertIsInstance(result["weapons_data"], dict)

    def test_weapons_data_matches_ship_weapons_entry(self):
        """weapons_data deve essere lo stesso oggetto presente in SHIP_WEAPONS."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertIs(result["weapons_data"], SHIP_WEAPONS["MISSILES_SAM"]["RIM-66-SM-2"])

    # ── categoria restituita ───────────────────────────────────────────────────

    def test_sam_category_is_correct(self):
        """RIM-66-SM-2 deve essere categorizzato come 'MISSILES_SAM'."""
        result = get_ship_weapon("RIM-66-SM-2")
        self.assertEqual(result["weapons_category"], "MISSILES_SAM")

    def test_asm_category_is_correct(self):
        """RGM-84-Harpoon deve essere categorizzato come 'MISSILES_ASM'."""
        result = get_ship_weapon("RGM-84-Harpoon")
        self.assertEqual(result["weapons_category"], "MISSILES_ASM")

    def test_torpedo_category_is_correct(self):
        """Mk-48 deve essere categorizzato come 'MISSILES_TORPEDO'."""
        result = get_ship_weapon("Mk-48")
        self.assertEqual(result["weapons_category"], "MISSILES_TORPEDO")

    def test_gun_category_is_correct(self):
        """AK-130-130mm deve essere categorizzato come 'GUNS'."""
        result = get_ship_weapon("AK-130-130mm")
        self.assertEqual(result["weapons_category"], "GUNS")

    def test_ciws_category_is_correct(self):
        """Mk-15-Phalanx deve essere categorizzato come 'CIWS'."""
        result = get_ship_weapon("Mk-15-Phalanx")
        self.assertEqual(result["weapons_category"], "CIWS")

    def test_russian_ciws_category_is_correct(self):
        """AK-630 deve essere categorizzato come 'CIWS'."""
        result = get_ship_weapon("AK-630")
        self.assertEqual(result["weapons_category"], "CIWS")

    def test_tomahawk_category_is_correct(self):
        """BGM-109-Tomahawk deve essere categorizzato come 'MISSILES_ASM'."""
        result = get_ship_weapon("BGM-109-Tomahawk")
        self.assertEqual(result["weapons_category"], "MISSILES_ASM")

    # ── ricerca su tutti i modelli ─────────────────────────────────────────────

    def test_all_models_are_findable(self):
        """Ogni modello in SHIP_WEAPONS deve essere trovato da get_ship_weapon()."""
        for cat, weapons in SHIP_WEAPONS.items():
            for model in weapons:
                with self.subTest(category=cat, model=model):
                    result = get_ship_weapon(model)
                    self.assertIsNotNone(result,
                                        f"get_ship_weapon('{model}') ha restituito None")
                    self.assertEqual(result["weapons_category"], cat,
                                     f"Categoria errata per '{model}'")

    # ── modello sconosciuto ───────────────────────────────────────────────────

    def test_unknown_model_returns_none(self):
        """Modello sconosciuto → None."""
        result = get_ship_weapon("WEAPON_NOT_EXISTING_XYZ")
        self.assertIsNone(result)

    def test_empty_string_returns_none(self):
        """Stringa vuota → None (nessun modello con nome vuoto)."""
        result = get_ship_weapon("")
        self.assertIsNone(result)

    # ── errori di tipo ────────────────────────────────────────────────────────

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_ship_weapon(123)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_ship_weapon(None)

    def test_type_error_on_list(self):
        with self.assertRaises(TypeError):
            get_ship_weapon(["RIM-66-SM-2"])

    def test_type_error_on_float(self):
        with self.assertRaises(TypeError):
            get_ship_weapon(66.0)


# ---------------------------------------------------------------------------
# 9. get_weapon_score_target
# ---------------------------------------------------------------------------

class TestGetWeaponScoreTarget(unittest.TestCase):
    """Unit test per get_weapon_score_target() con la firma:

        get_weapon_score_target(model: str, target_type: List, target_dimension: List) -> float

    - model: stringa identificativa del modello (cercato tramite get_ship_weapon())
    - target_type: lista di tipi di bersaglio (validati contro TARGET_CLASSIFICATION)
    - target_dimension: lista di dimensioni (validati contro TARGET_DIMENSION)
    - Ritorna la MEDIA di accuracy * destroy_capacity su tutte le combinazioni valide
    - Deterministica (nessuna componente stocastica)
    - Ritorna 0.0 se model non trovato, liste vuote, o nessuna combinazione valida
    """

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    # ── validazione dei parametri ────────────────────────────────────────────

    def test_type_error_model_not_string(self):
        """model non-stringa → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target(123, ["ship"], ["big"])

    def test_type_error_model_none(self):
        """model None → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target(None, ["ship"], ["big"])

    def test_type_error_model_list(self):
        """model lista → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target(["RGM-84-Harpoon"], ["ship"], ["big"])

    # ── modello sconosciuto ───────────────────────────────────────────────────

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_weapon_score_target("WEAPON_NOT_EXISTING_XYZ", ["ship"], ["big"])
        self.assertEqual(score, 0.0)

    # ── liste di target vuote o con valori invalidi ───────────────────────────

    def test_empty_target_type_list_returns_zero(self):
        """Lista target_type vuota → 0.0."""
        score = get_weapon_score_target("RGM-84-Harpoon", [], ["big"])
        self.assertEqual(score, 0.0)

    def test_empty_target_dimension_list_returns_zero(self):
        """Lista target_dimension vuota → 0.0."""
        score = get_weapon_score_target("RGM-84-Harpoon", ["ship"], [])
        self.assertEqual(score, 0.0)

    def test_both_lists_empty_returns_zero(self):
        """Entrambe le liste vuote → 0.0."""
        score = get_weapon_score_target("RGM-84-Harpoon", [], [])
        self.assertEqual(score, 0.0)

    def test_invalid_target_type_only_returns_zero(self):
        """target_type sconosciuto → 0.0."""
        score = get_weapon_score_target("RGM-84-Harpoon", ["UNKNOWN_TARGET_XYZ"], ["big"])
        self.assertEqual(score, 0.0)

    def test_invalid_target_dimension_only_returns_zero(self):
        """target_dimension sconosciuta → 0.0."""
        score = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["UNKNOWN_DIM_XYZ"])
        self.assertEqual(score, 0.0)

    def test_mixed_valid_invalid_target_type(self):
        """Un target_type invalido viene ignorato; risultato uguale al solo valido."""
        score_only_valid = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big"])
        score_mixed      = get_weapon_score_target("RGM-84-Harpoon", ["ship", "UNKNOWN_XYZ"], ["big"])
        self.assertAlmostEqual(score_only_valid, score_mixed, places=9)

    def test_mixed_valid_invalid_target_dimension(self):
        """Una target_dimension invalida viene ignorata; risultato uguale alla sola valida."""
        score_only_valid = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big"])
        score_mixed      = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big", "UNKNOWN_DIM_XYZ"])
        self.assertAlmostEqual(score_only_valid, score_mixed, places=9)

    # ── valori di ritorno per combinazioni valide ─────────────────────────────

    def test_asm_vs_ship_big_returns_positive(self):
        """RGM-84-Harpoon vs ship/big → float > 0 (missione primaria anti-nave)."""
        score = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_asm_vs_soft_big_returns_positive(self):
        """RGM-84-Harpoon vs Soft/big → float > 0."""
        score = get_weapon_score_target("RGM-84-Harpoon", ["Soft"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_torpedo_vs_ship_returns_positive(self):
        """Mk-48 vs ship/big → float > 0 (siluro contro nave di superficie)."""
        score = get_weapon_score_target("Mk-48", ["ship"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_gun_vs_soft_returns_positive(self):
        """AK-130-130mm vs Soft/big → float > 0."""
        score = get_weapon_score_target("AK-130-130mm", ["Soft"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_sam_vs_air_defense_returns_positive(self):
        """RIM-66-SM-2 vs Air_Defense/med → float > 0 (SAM contro difesa aerea)."""
        score = get_weapon_score_target("RIM-66-SM-2", ["Air_Defense"], ["med"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    # ── proprietà navali specifiche ──────────────────────────────────────────

    def test_torpedo_vs_land_target_returns_zero(self):
        """Un siluro vs bersaglio a terra (Soft) → 0.0 (destroy_capacity = 0 vs terra)."""
        score = get_weapon_score_target("Mk-48", ["Soft"], ["big"])
        self.assertEqual(score, 0.0)

    def test_torpedo_vs_armored_returns_zero(self):
        """Un siluro vs Armored/big → 0.0 (siluro inefficace su bersagli terrestri corazzati)."""
        score = get_weapon_score_target("Mk-46", ["Armored"], ["big"])
        self.assertEqual(score, 0.0)

    def test_heavy_torpedo_vs_ship_higher_than_light(self):
        """Mk-48 (pesante) deve avere efficacia vs ship > Mk-46 (leggero)."""
        score_heavy = get_weapon_score_target("Mk-48", ["ship"], ["big"])
        score_light = get_weapon_score_target("Mk-46", ["ship"], ["big"])
        self.assertGreater(score_heavy, score_light)

    def test_supersonic_asm_vs_ship_higher_than_subsonic(self):
        """P-700-Granit (supersonico pesante) deve avere efficacia vs ship > RGM-84-Harpoon."""
        score_super = get_weapon_score_target("P-700-Granit", ["ship"], ["big"])
        score_sub   = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big"])
        self.assertGreater(score_super, score_sub)

    def test_asm_vs_armored_higher_than_vs_ship(self):
        """Un missile anti-nave ha accuracy alta vs ship ma destroy_capacity bassa
        (le navi resistono a colpi singoli). Contro Armored l'accuracy è minore ma
        la dc è quasi 1.0 (un carro colpito da 220 kg è certamente distrutto).
        Il prodotto acc×dc risulta: Armored > ship."""
        score_ship    = get_weapon_score_target("RGM-84-Harpoon", ["ship"],    ["big"])
        score_armored = get_weapon_score_target("RGM-84-Harpoon", ["Armored"], ["big"])
        self.assertGreater(score_armored, score_ship)

    def test_return_is_non_negative_for_all_sample_models(self):
        """Il punteggio deve essere non negativo per un campione di modelli."""
        sample = [
            ("RGM-84-Harpoon",   ["ship", "Soft"],   ["big", "med", "small"]),
            ("P-700-Granit",     ["ship"],            ["big"]),
            ("Mk-48",            ["ship"],            ["big"]),
            ("AK-130-130mm",     ["Soft", "Structure"], ["big"]),
            ("Mk-15-Phalanx",    ["Air_Defense"],     ["med"]),
        ]
        for model, t_types, t_dims in sample:
            with self.subTest(model=model):
                score = get_weapon_score_target(model, t_types, t_dims)
                self.assertGreaterEqual(score, 0.0)

    # ── determinismo ─────────────────────────────────────────────────────────

    def test_deterministic_same_result_twice(self):
        """La funzione deve restituire lo stesso risultato su chiamate successive."""
        score1 = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big"])
        score2 = get_weapon_score_target("RGM-84-Harpoon", ["ship"], ["big"])
        self.assertEqual(score1, score2)

    # ── semantica della media ─────────────────────────────────────────────────

    def test_single_combination_equals_accuracy_times_destroy_capacity(self):
        """Con una sola combinazione (t_type, t_dim), il risultato deve essere
        accuracy * destroy_capacity letto direttamente dal template efficiency."""
        model  = "RGM-84-Harpoon"
        t_type = "ship"
        t_dim  = "big"
        eff = SHIP_WEAPONS["MISSILES_ASM"][model]["efficiency"][t_type][t_dim]
        expected = eff["accuracy"] * eff["destroy_capacity"]
        score = get_weapon_score_target(model, [t_type], [t_dim])
        self.assertAlmostEqual(score, expected, places=9)

    def test_two_dimensions_returns_average(self):
        """Con due dimensioni valide, il risultato è la media dei due prodotti."""
        model  = "RGM-84-Harpoon"
        t_type = "ship"
        eff = SHIP_WEAPONS["MISSILES_ASM"][model]["efficiency"][t_type]
        v_big   = eff["big"]["accuracy"]   * eff["big"]["destroy_capacity"]
        v_small = eff["small"]["accuracy"] * eff["small"]["destroy_capacity"]
        expected = (v_big + v_small) / 2
        score = get_weapon_score_target(model, [t_type], ["big", "small"])
        self.assertAlmostEqual(score, expected, places=9)

    def test_two_target_types_returns_average(self):
        """Con due target type validi, il risultato è la media dei due prodotti."""
        model = "AK-130-130mm"
        t_dim = "big"
        eff = SHIP_WEAPONS["GUNS"][model]["efficiency"]
        v_soft = eff["Soft"]["big"]["accuracy"]      * eff["Soft"]["big"]["destroy_capacity"]
        v_str  = eff["Structure"]["big"]["accuracy"] * eff["Structure"]["big"]["destroy_capacity"]
        expected = (v_soft + v_str) / 2
        score = get_weapon_score_target(model, ["Soft", "Structure"], [t_dim])
        self.assertAlmostEqual(score, expected, places=9)


# ---------------------------------------------------------------------------
# 10. get_weapon_score_target_distribuition
# ---------------------------------------------------------------------------

class TestGetWeaponScoreTargetDistribuition(unittest.TestCase):
    """Unit test per get_weapon_score_target_distribuition():

        get_weapon_score_target_distribuition(
            model: str, target_type: Dict, target_dimension: Dict
        ) -> float

    - model: stringa identificativa del modello (TypeError se non str)
    - target_type: Dict {tipo: peso} — chiavi validate contro TARGET_CLASSIFICATION
    - target_dimension: Dict {dimensione: peso} — chiavi validate contro TARGET_DIMENSION
    - Ritorna la SOMMA PONDERATA di accuracy * destroy_capacity * w_type * w_dim
      su tutte le combinazioni (t_type, t_dim) valide. NON diviso per il numero
      di combinazioni (a differenza di get_weapon_score_target che calcola la media).
    - Ritorna 0.0 se model non trovato, dict vuoti, o nessuna combinazione valida.
    """

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    # ── validazione tipo model ────────────────────────────────────────────────

    def test_type_error_model_int(self):
        """model int → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target_distribuition(123, {"ship": 1.0}, {"big": 1.0})

    def test_type_error_model_none(self):
        """model None → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target_distribuition(None, {"ship": 1.0}, {"big": 1.0})

    def test_type_error_model_list(self):
        """model lista → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target_distribuition(
                ["RGM-84-Harpoon"], {"ship": 1.0}, {"big": 1.0}
            )

    # ── modello sconosciuto ───────────────────────────────────────────────────

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_weapon_score_target_distribuition(
            "WEAPON_NOT_EXISTING_XYZ", {"ship": 1.0}, {"big": 1.0}
        )
        self.assertEqual(score, 0.0)

    # ── dict vuoti ────────────────────────────────────────────────────────────

    def test_empty_target_type_dict_returns_zero(self):
        """Dict target_type vuoto → 0.0."""
        score = get_weapon_score_target_distribuition("RGM-84-Harpoon", {}, {"big": 1.0})
        self.assertEqual(score, 0.0)

    def test_empty_target_dimension_dict_returns_zero(self):
        """Dict target_dimension vuoto → 0.0."""
        score = get_weapon_score_target_distribuition("RGM-84-Harpoon", {"ship": 1.0}, {})
        self.assertEqual(score, 0.0)

    def test_both_dicts_empty_returns_zero(self):
        """Entrambi i dict vuoti → 0.0."""
        score = get_weapon_score_target_distribuition("RGM-84-Harpoon", {}, {})
        self.assertEqual(score, 0.0)

    # ── chiavi non valide (ignorate con warning) ──────────────────────────────

    def test_invalid_target_type_only_returns_zero(self):
        """target_type sconosciuto → 0.0."""
        score = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"UNKNOWN_TARGET_XYZ": 1.0}, {"big": 1.0}
        )
        self.assertEqual(score, 0.0)

    def test_invalid_target_dimension_only_returns_zero(self):
        """target_dimension sconosciuta → 0.0."""
        score = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0}, {"UNKNOWN_DIM_XYZ": 1.0}
        )
        self.assertEqual(score, 0.0)

    def test_invalid_target_type_ignored_mixed(self):
        """target_type invalido ignorato; risultato uguale a solo la chiave valida."""
        score_valid = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0}, {"big": 1.0}
        )
        score_mixed = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0, "UNKNOWN_XYZ": 0.5}, {"big": 1.0}
        )
        self.assertAlmostEqual(score_valid, score_mixed, places=9)

    def test_invalid_target_dimension_ignored_mixed(self):
        """target_dimension invalida ignorata; risultato uguale a solo la chiave valida."""
        score_valid = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0}, {"big": 1.0}
        )
        score_mixed = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0}, {"big": 1.0, "UNKNOWN_DIM_XYZ": 0.5}
        )
        self.assertAlmostEqual(score_valid, score_mixed, places=9)

    # ── semantica della somma ponderata ──────────────────────────────────────

    def test_single_combination_weight_one_equals_acc_times_dc(self):
        """Con peso 1.0 per entrambe le chiavi, il risultato è accuracy * destroy_capacity."""
        model  = "RGM-84-Harpoon"
        t_type = "ship"
        t_dim  = "big"
        eff = SHIP_WEAPONS["MISSILES_ASM"][model]["efficiency"][t_type][t_dim]
        expected = eff["accuracy"] * eff["destroy_capacity"]
        score = get_weapon_score_target_distribuition(
            model, {t_type: 1.0}, {t_dim: 1.0}
        )
        self.assertAlmostEqual(score, expected, places=9)

    def test_weight_half_halves_single_combination(self):
        """Un peso 0.5 su t_type dimezza il risultato rispetto a peso 1.0."""
        model  = "RGM-84-Harpoon"
        t_type = "ship"
        t_dim  = "big"
        score_full = get_weapon_score_target_distribuition(
            model, {t_type: 1.0}, {t_dim: 1.0}
        )
        score_half = get_weapon_score_target_distribuition(
            model, {t_type: 0.5}, {t_dim: 1.0}
        )
        self.assertAlmostEqual(score_half, score_full * 0.5, places=9)

    def test_two_types_weighted_sum(self):
        """Con due tipi (0.7 + 0.3), il risultato è la somma ponderata, NON la media."""
        model = "RGM-84-Harpoon"
        t_dim = "big"
        eff = SHIP_WEAPONS["MISSILES_ASM"][model]["efficiency"]
        v_ship = eff["ship"]["big"]["accuracy"]  * eff["ship"]["big"]["destroy_capacity"]
        v_soft = eff["Soft"]["big"]["accuracy"]  * eff["Soft"]["big"]["destroy_capacity"]
        expected = v_ship * 0.7 + v_soft * 0.3
        score = get_weapon_score_target_distribuition(
            model, {"ship": 0.7, "Soft": 0.3}, {t_dim: 1.0}
        )
        self.assertAlmostEqual(score, expected, places=9)
        # Verifica esplicita che il risultato NON sia diviso per il numero di combinazioni
        self.assertNotAlmostEqual(score, expected / 2, places=9)

    def test_two_dimensions_weighted_sum(self):
        """Con due dimensioni (0.6 + 0.4), il risultato è la somma ponderata."""
        model  = "AK-130-130mm"
        t_type = "Soft"
        eff = SHIP_WEAPONS["GUNS"][model]["efficiency"][t_type]
        v_big   = eff["big"]["accuracy"]   * eff["big"]["destroy_capacity"]
        v_small = eff["small"]["accuracy"] * eff["small"]["destroy_capacity"]
        expected = v_big * 0.6 + v_small * 0.4
        score = get_weapon_score_target_distribuition(
            model, {t_type: 1.0}, {"big": 0.6, "small": 0.4}
        )
        self.assertAlmostEqual(score, expected, places=9)

    def test_weight_zero_returns_zero(self):
        """Pesi 0.0 su tutte le chiavi → risultato 0.0."""
        score = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 0.0}, {"big": 0.0}
        )
        self.assertEqual(score, 0.0)

    def test_differs_from_uniform_average_with_two_types(self):
        """La somma ponderata (distribuzione) è diversa dalla media uniforme
        di get_weapon_score_target quando i pesi non sono uniformi."""
        model = "RGM-84-Harpoon"
        t_dim = "big"
        eff = SHIP_WEAPONS["MISSILES_ASM"][model]["efficiency"]
        v_ship = eff["ship"]["big"]["accuracy"] * eff["ship"]["big"]["destroy_capacity"]
        v_soft = eff["Soft"]["big"]["accuracy"] * eff["Soft"]["big"]["destroy_capacity"]
        expected_weighted = v_ship * 0.7 + v_soft * 0.3
        expected_avg = (v_ship + v_soft) / 2
        score = get_weapon_score_target_distribuition(
            model, {"ship": 0.7, "Soft": 0.3}, {t_dim: 1.0}
        )
        self.assertAlmostEqual(score, expected_weighted, places=9)
        # Le due semantiche devono produrre valori diversi (ship ≠ Soft per Harpoon)
        self.assertNotAlmostEqual(expected_weighted, expected_avg, places=9)

    # ── valori di ritorno positivi ────────────────────────────────────────────

    def test_asm_vs_ship_returns_positive(self):
        """RGM-84-Harpoon vs ship/big con peso 1.0 → float > 0."""
        score = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0}, {"big": 1.0}
        )
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_gun_vs_soft_returns_positive(self):
        """AK-130-130mm vs Soft/big con peso 1.0 → float > 0."""
        score = get_weapon_score_target_distribuition(
            "AK-130-130mm", {"Soft": 1.0}, {"big": 1.0}
        )
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_torpedo_vs_ship_returns_positive(self):
        """Mk-48 vs ship/big con peso 1.0 → float > 0."""
        score = get_weapon_score_target_distribuition(
            "Mk-48", {"ship": 1.0}, {"big": 1.0}
        )
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_torpedo_vs_land_returns_zero(self):
        """Siluro vs Soft/big con peso 1.0 → 0.0 (destroy_capacity = 0 vs terra)."""
        score = get_weapon_score_target_distribuition(
            "Mk-48", {"Soft": 1.0}, {"big": 1.0}
        )
        self.assertEqual(score, 0.0)

    def test_return_is_non_negative_for_sample_models(self):
        """Il risultato deve essere non negativo per un campione di modelli."""
        sample = [
            ("RGM-84-Harpoon",  {"ship": 0.8, "Soft": 0.2},   {"big": 1.0}),
            ("P-700-Granit",    {"ship": 1.0},                 {"big": 0.6, "med": 0.4}),
            ("Mk-48",           {"ship": 1.0},                 {"big": 1.0}),
            ("AK-130-130mm",    {"Soft": 0.7, "Structure": 0.3}, {"big": 1.0}),
            ("Mk-15-Phalanx",   {"Air_Defense": 1.0},          {"med": 1.0}),
        ]
        for model, t_type, t_dim in sample:
            with self.subTest(model=model):
                score = get_weapon_score_target_distribuition(model, t_type, t_dim)
                self.assertGreaterEqual(score, 0.0)

    # ── determinismo ──────────────────────────────────────────────────────────

    def test_deterministic(self):
        """Stesso risultato su chiamate successive (nessuna componente stocastica)."""
        score1 = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 0.7, "Soft": 0.3}, {"big": 1.0}
        )
        score2 = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 0.7, "Soft": 0.3}, {"big": 1.0}
        )
        self.assertEqual(score1, score2)

    # ── confronti ordinativi ──────────────────────────────────────────────────

    def test_asm_armored_score_higher_than_ship(self):
        """Harpoon: score vs Armored > score vs ship.
        La dc vs Armored è quasi 1.0 (carro distrutto da 220 kg con certezza),
        mentre vs ship la dc è moderata (compartimentazione e damage control)."""
        score_ship    = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 1.0}, {"big": 1.0}
        )
        score_armored = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"Armored": 1.0}, {"big": 1.0}
        )
        self.assertGreater(score_armored, score_ship)

    def test_higher_soft_weight_gives_higher_score_for_asm(self):
        """Peso maggiore su Soft produce score più alto di peso maggiore su ship,
        poiché score(Soft) > score(ship) per Harpoon (Soft è il bersaglio più fragile)."""
        score_ship_heavy = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 0.8, "Soft": 0.2}, {"big": 1.0}
        )
        score_soft_heavy = get_weapon_score_target_distribuition(
            "RGM-84-Harpoon", {"ship": 0.2, "Soft": 0.8}, {"big": 1.0}
        )
        self.assertGreater(score_soft_heavy, score_ship_heavy)


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITÀ CONDIVISE PER LA GENERAZIONE DELLE TABELLE
# ─────────────────────────────────────────────────────────────────────────────

def _is_nan(value: float) -> bool:
    try:
        return value != value
    except Exception:
        return False


def _safe_score(weapon_type: str, model: str) -> float:
    """Chiama get_weapon_score() con il logger mockato.
    Ritorna float('nan') in caso di eccezione non gestita."""
    try:
        with patch(_LOGGER_PATH, MagicMock()):
            return get_weapon_score(weapon_type, model)
    except Exception:
        return float("nan")


def _safe_score_target(model: str, t_type: str, t_dim: str) -> float:
    """Chiama get_weapon_score_target() per una singola combinazione
    (target_type, target_dimension). Ritorna float('nan') in caso di eccezione."""
    try:
        with patch(_LOGGER_PATH, MagicMock()):
            return get_weapon_score_target(model, [t_type], [t_dim])
    except Exception:
        return float("nan")


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — STAMPA A TERMINALE
# ─────────────────────────────────────────────────────────────────────────────

def print_weapon_score_tables(weapon_type_list: List[str]) -> None:
    """Stampa a terminale una tabella get_weapon_score() per ogni categoria,
    ordinata per punteggio decrescente."""
    for category in weapon_type_list:
        weapons = SHIP_WEAPONS.get(category, {})
        if not weapons:
            print(f"\n[SKIP] Categoria '{category}' non trovata o vuota in SHIP_WEAPONS.\n")
            continue

        rows = [(model, _safe_score(category, model)) for model in weapons]
        rows.sort(key=lambda x: (float("-inf") if _is_nan(x[1]) else x[1]), reverse=True)

        col_m = max(len("Weapon Model"), max(len(m) for m, _ in rows))
        col_s = 14
        width = col_m + col_s + 6

        print()
        print("═" * width)
        print(f"  CATEGORIA: {category}   —   get_weapon_score()")
        print("═" * width)
        print(f"  {'Weapon Model':<{col_m}}   {'Score':>{col_s}}")
        print("─" * width)
        for model, score in rows:
            s = f"{score:.8f}" if not _is_nan(score) else "      N/A     "
            print(f"  {model:<{col_m}}   {s:>{col_s}}")
        print()


def print_weapon_score_target_tables(
    weapon_type_list: List[str],
    target_type_list: List[str],
    target_dimension_list: List[str],
) -> None:
    """Stampa a terminale una tabella get_weapon_score_target() per ogni categoria,
    con colonne per ogni combinazione (target_type × target_dimension).
    Il punteggio di ogni cella è la media accuracy * destroy_capacity
    per la singola combinazione (t_type, t_dim)."""
    combinations = [(t, d) for t in target_type_list for d in target_dimension_list]

    for category in weapon_type_list:
        weapons = SHIP_WEAPONS.get(category, {})
        if not weapons:
            print(f"\n[SKIP] Categoria '{category}' non trovata o vuota in SHIP_WEAPONS.\n")
            continue

        models = list(weapons.keys())
        col_m = max(len("Weapon Model"), max(len(m) for m in models))
        cell_w = 12
        col_headers = [f"{t}/{d}" for t, d in combinations]

        header_parts = [f"  {'Weapon Model':<{col_m}}"]
        for h in col_headers:
            header_parts.append(f"{h:^{cell_w}}")
        header = "  ".join(header_parts)
        width = len(header)

        print()
        print("═" * width)
        print(f"  CATEGORIA: {category}   —   get_weapon_score_target()")
        print("═" * width)
        print(header)
        print("─" * width)

        for model in models:
            row = [f"  {model:<{col_m}}"]
            for t_type, t_dim in combinations:
                v = _safe_score_target(model, t_type, t_dim)
                s = f"{v:.4f}" if not _is_nan(v) else "   N/A   "
                row.append(f"{s:^{cell_w}}")
            print("  ".join(row))
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


def save_weapon_score_pdf(weapon_type_list: List[str], output_path: str) -> None:
    """Salva un PDF con una pagina per categoria.
    Ogni pagina: tabella get_weapon_score() ordinata per punteggio decrescente,
    con colorazione heatmap (verde=alto, rosso=basso)."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with PdfPages(output_path) as pdf:
        for category in weapon_type_list:
            weapons = SHIP_WEAPONS.get(category, {})
            if not weapons:
                continue

            rows = [(model, _safe_score(category, model)) for model in weapons]
            rows.sort(
                key=lambda x: (float("-inf") if _is_nan(x[1]) else x[1]),
                reverse=True,
            )

            valid_scores = [s for _, s in rows if not _is_nan(s)]
            max_s = max(valid_scores) if valid_scores else 1.0
            min_s = min(valid_scores) if valid_scores else 0.0
            rng = (max_s - min_s) if max_s != min_s else 1.0

            cell_text = []
            cell_colors = []
            for rank, (model, score) in enumerate(rows, start=1):
                score_str = f"{score:.8f}" if not _is_nan(score) else "N/A"
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
                f"Confronto Punteggio Armi Navali — {category}\n"
                f"Funzione: get_weapon_score()",
                fontsize=13, fontweight="bold", pad=20,
            )
            tbl = ax.table(
                cellText=cell_text,
                colLabels=["#", "Weapon Model", "Score"],
                cellColours=cell_colors,
                loc="center", cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)
            tbl.auto_set_column_width([0, 1, 2])
            _header_style(tbl, 3)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"[PDF] ship_weapon_score → {output_path}")


def save_weapon_score_target_pdf(
    weapon_type_list: List[str],
    target_type_list: List[str],
    target_dimension_list: List[str],
    output_path: str,
) -> None:
    """Salva un PDF con una pagina per categoria.
    Ogni pagina: tabella get_weapon_score_target() con colonne per ogni
    combinazione (target_type × target_dimension), con colorazione heatmap.
    La distribuzione per ogni cella è concentrata sulla singola dimensione ({dim: 1.0})."""
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    combinations = [(t, d) for t in target_type_list for d in target_dimension_list]

    with PdfPages(output_path) as pdf:
        for category in weapon_type_list:
            weapons = SHIP_WEAPONS.get(category, {})
            if not weapons:
                continue

            models = list(weapons.keys())
            col_labels = ["Weapon Model"] + [f"{t}\n{d}" for t, d in combinations]
            n_data_cols = len(combinations)
            n_cols_total = 1 + n_data_cols

            cell_text, score_matrix = [], []
            for model in models:
                row_scores = [
                    _safe_score_target(model, t, d)
                    for t, d in combinations
                ]
                score_matrix.append(row_scores)
                cell_text.append(
                    [model]
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
            fig_h = max(4.0, 0.40 * len(models) + 2.5)
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.axis("off")
            ax.set_title(
                f"Confronto Punteggio vs Bersaglio — {category}\n"
                f"Funzione: get_weapon_score_target()",
                fontsize=12, fontweight="bold", pad=20,
            )
            tbl = ax.table(
                cellText=cell_text,
                colLabels=col_labels,
                cellColours=cell_colors,
                loc="center", cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(7)
            tbl.auto_set_column_width(list(range(n_cols_total)))
            _header_style(tbl, n_cols_total)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"[PDF] ship_weapon_score_target → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in (
        TestShipWeaponsDataStructure,
        TestGetSamScore,
        TestGetAsmScore,
        TestGetTorpedoScore,
        TestGetGunScore,
        TestGetCiwsScore,
        TestGetWeaponScoreDispatcher,
        TestGetShipWeapon,
        TestGetWeaponScoreTarget,
        TestGetWeaponScoreTargetDistribuition,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def _run_tables_terminal() -> None:
    print("\n" + "=" * 70)
    print("  TABELLE PUNTEGGIO — get_weapon_score()")
    print("=" * 70)
    print_weapon_score_tables(WEAPON_TYPE_SCORE)

    print("\n" + "=" * 70)
    print("  TABELLE PUNTEGGIO vs BERSAGLIO — get_weapon_score_target()")
    print("=" * 70)
    print_weapon_score_target_tables(WEAPON_TYPE_TARGET, TARGET_TYPE, TARGET_DIMENSION)


def _run_tables_pdf() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_weapon_score_pdf(
        WEAPON_TYPE_SCORE,
        os.path.join(OUTPUT_DIR, "ship_weapon_score_tables.pdf"),
    )
    save_weapon_score_target_pdf(
        WEAPON_TYPE_TARGET,
        TARGET_TYPE,
        TARGET_DIMENSION,
        os.path.join(OUTPUT_DIR, "ship_weapon_score_target_tables.pdf"),
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
    print("║      Test_Ship_Weapon_Data  —  Menu principale              ║")
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
        label  = _MENU_ITEMS[choice - 1][0]
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
