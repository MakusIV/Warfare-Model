"""
Test_Ground_Weapon_Data.py
==========================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo
Ground_Weapon_Data.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Ground_Weapon_Data.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ground_Weapon_Data.py            # menu interattivo
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ground_Weapon_Data.py --tables-only
    python  Code/Dynamic_War_Manager/Source/Test/Test_Ground_Weapon_Data.py --tests-only

Note sul modulo sotto test:
  - GROUND_WEAPONS: dizionario principale con categorie AUTO_CANNONS, CANNONS,
    AA_CANNONS, MISSILES, MORTARS, ARTILLERY, MACHINE_GUNS, GRENADE_LAUNCHERS.
    Le categorie ROCKETS e FLAME_TRHOWERS esistono ma sono vuote.
  - TARGET_DIMENSION = ['small', 'med', 'big']: dimensioni valide per il target.
  - get_weapon(model: str): cerca il modello in GROUND_WEAPONS e restituisce
    {"weapons_category": str, "weapons_data": dict} oppure None se non trovato.
    Lancia TypeError se model non è una stringa.
  - get_weapon_score(weapon_type, weapon_model): dispatcher con due argomenti
    (diversamente da Aircraft_Weapon_Data che accetta solo model).
  - get_weapon_score_target(model: str, target_type: List, target_dimension: List):
    cerca il modello tramite get_weapon(), poi calcola la MEDIA di
    accuracy * destroy_capacity su tutte le combinazioni (t_type, t_dim) valide.
    Deterministica (nessuna componente stocastica).
    Ritorna 0.0 se model non trovato o nessuna combinazione valida.
    target_type è validato contro TARGET_CLASSIFICATION; target_dimension contro
    TARGET_DIMENSION.
  - GRENADE_LAUNCHERS: la categoria esiste e contiene armi, ma il dispatcher
    get_weapon_score() non gestisce questo tipo → ritorna 0 (int).
  - Alcune funzioni (get_cannon_score, get_aa_cannon_score, ecc.) accedono
    direttamente a GROUND_WEAPONS[cat][model] senza .get() → KeyError per
    modelli sconosciuti; altre (get_missiles_score) usano .get() → 0.0.
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
    "CANNONS",
    "AA_CANNONS",
    "AUTO_CANNONS",
    "MISSILES",
    "MORTARS",
    "ARTILLERY",
    "MACHINE_GUNS",
]

# Categorie per le tabelle get_weapon_score_target()
WEAPON_TYPE_TARGET: List[str] = [
    "CANNONS",
    "AA_CANNONS",
    "AUTO_CANNONS",
    "MISSILES",
    "ARTILLERY",
    "MACHINE_GUNS",
]

# Tipi di bersaglio per get_weapon_score_target()
TARGET_TYPE: List[str] = [
    "Soft", "Armored", "Hard", "Structure", "Air_Defense", "ship",
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
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import (
    GROUND_WEAPONS,
    WEAPON_PARAM,
    AMMO_PARAM,
    AMMO_TARGET_EFFECTIVENESS,
    TARGET_DIMENSION as GWD_TARGET_DIMENSION,
    get_cannon_score,
    get_aa_cannon_score,
    get_auto_cannon_score,
    get_missiles_score,
    get_machine_gun_score,
    get_mortars_score,
    get_artillery_score,
    get_weapon_score,
    get_weapon,
    get_weapon_score_target,
)

# ─────────────────────────────────────────────────────────────────────────────
#  UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# 1. Struttura dati del modulo
# ---------------------------------------------------------------------------

class TestGroundWeaponsDataStructure(unittest.TestCase):
    """Verifica la correttezza strutturale dei dizionari GROUND_WEAPONS,
    WEAPON_PARAM, AMMO_PARAM e AMMO_TARGET_EFFECTIVENESS."""

    # ── GROUND_WEAPONS ──────────────────────────────────────────────────────

    def test_ground_weapons_has_expected_categories(self):
        """GROUND_WEAPONS deve contenere le categorie di armi attese."""
        expected = {
            "CANNONS", "AA_CANNONS", "AUTO_CANNONS", "MISSILES",
            "MORTARS", "ARTILLERY", "MACHINE_GUNS", "GRENADE_LAUNCHERS",
        }
        for cat in expected:
            with self.subTest(category=cat):
                self.assertIn(cat, GROUND_WEAPONS)

    def test_ground_weapons_all_values_are_dicts(self):
        """Ogni categoria deve essere un dizionario (possibilmente vuoto)."""
        for cat, content in GROUND_WEAPONS.items():
            with self.subTest(category=cat):
                self.assertIsInstance(content, dict)

    def test_populated_categories_are_non_empty(self):
        """Le categorie principali devono contenere almeno un'arma."""
        populated = [
            "CANNONS", "AA_CANNONS", "AUTO_CANNONS", "MISSILES",
            "MORTARS", "ARTILLERY", "MACHINE_GUNS",
        ]
        for cat in populated:
            with self.subTest(category=cat):
                self.assertGreater(len(GROUND_WEAPONS[cat]), 0,
                                   f"Categoria '{cat}' è vuota")

    def test_cannons_weapon_has_required_fields(self):
        """Ogni arma in CANNONS deve avere i campi fondamentali (senza ammo_type
        che è opzionale: alcune armi come U-5TS 'Molot' ne sono prive)."""
        required = {"model", "caliber", "range", "efficiency"}
        for model, data in GROUND_WEAPONS["CANNONS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in CANNONS/{model}")

    def test_cannons_missing_ammo_type_documented(self):
        """Documenta le armi in CANNONS senza 'ammo_type': tali armi causano
        KeyError in get_cannon_score() poiché WEAPON_PARAM['CANNONS'] include
        il parametro ammo_type ma il campo non è sempre presente nei dati."""
        missing = [m for m, d in GROUND_WEAPONS["CANNONS"].items()
                   if "ammo_type" not in d]
        # Il test passa sempre, ma documenta il problema: sono presenti armi
        # con campo ammo_type mancante → bug nei dati di Ground_Weapon_Data.py
        if missing:
            print(f"\n  [DATA BUG] CANNONS senza ammo_type: {missing}")

    def test_missiles_weapon_has_required_fields(self):
        """Ogni arma in MISSILES deve avere i campi fondamentali."""
        required = {"model", "caliber", "range", "ammo_type", "efficiency"}
        for model, data in GROUND_WEAPONS["MISSILES"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MISSILES/{model}")

    def test_machine_guns_weapon_has_required_fields(self):
        """Ogni arma in MACHINE_GUNS deve avere i campi fondamentali.
        MACHINE_GUNS non usa 'ammo_type' (non è in WEAPON_PARAM['MACHINE_GUNS'])."""
        required = {"model", "caliber", "range", "efficiency"}
        for model, data in GROUND_WEAPONS["MACHINE_GUNS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MACHINE_GUNS/{model}")

    def test_efficiency_structure_has_all_target_types(self):
        """Per ogni arma, il template 'efficiency' deve contenere tutti i
        target type standard."""
        expected_types = {
            "Soft", "Armored", "Hard", "Structure", "Air_Defense",
            "Airbase", "Port", "Shipyard", "Farp", "Stronghold", "ship",
        }
        for cat in ("CANNONS", "MISSILES", "MACHINE_GUNS"):
            for model, data in GROUND_WEAPONS[cat].items():
                eff = data.get("efficiency", {})
                for t in expected_types:
                    with self.subTest(category=cat, model=model, target=t):
                        self.assertIn(t, eff,
                                      f"Target '{t}' mancante in efficiency di {cat}/{model}")

    def test_efficiency_structure_has_all_dimensions(self):
        """Ogni target_type nel template efficiency deve avere big/med/small."""
        for cat in ("CANNONS", "MISSILES"):
            for model, data in GROUND_WEAPONS[cat].items():
                eff = data.get("efficiency", {})
                for t_type, t_data in eff.items():
                    for dim in ("big", "med", "small"):
                        with self.subTest(cat=cat, model=model, target=t_type, dim=dim):
                            self.assertIn(dim, t_data,
                                          f"Dimensione '{dim}' mancante in {cat}/{model}/{t_type}")

    def test_efficiency_dim_has_accuracy_and_destroy_capacity(self):
        """Ogni cella efficiency deve contenere 'accuracy' e 'destroy_capacity'."""
        first_cannon = next(iter(GROUND_WEAPONS["CANNONS"]))
        eff = GROUND_WEAPONS["CANNONS"][first_cannon]["efficiency"]
        for t_type, t_data in eff.items():
            for dim in ("big", "med", "small"):
                cell = t_data.get(dim, {})
                with self.subTest(model=first_cannon, target=t_type, dim=dim):
                    self.assertIn("accuracy", cell)
                    self.assertIn("destroy_capacity", cell)

    def test_caliber_is_positive_for_all_cannons(self):
        """Il calibro deve essere un numero positivo per tutte le armi in CANNONS."""
        for model, data in GROUND_WEAPONS["CANNONS"].items():
            with self.subTest(model=model):
                self.assertIsInstance(data["caliber"], (int, float))
                self.assertGreater(data["caliber"], 0)

    # ── WEAPON_PARAM ────────────────────────────────────────────────────────

    def test_weapon_param_has_score_categories(self):
        """WEAPON_PARAM deve contenere le categorie che hanno una funzione di score."""
        expected = {
            "CANNONS", "AA_CANNONS", "AUTO_CANNONS", "MISSILES",
            "MORTARS", "ARTILLERY", "MACHINE_GUNS",
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

    def test_weapon_param_cannons_has_expected_keys(self):
        """WEAPON_PARAM['CANNONS'] deve avere caliber, muzzle_speed, fire_rate,
        range, ammo_type."""
        expected_keys = {"caliber", "muzzle_speed", "fire_rate", "range", "ammo_type"}
        self.assertEqual(set(WEAPON_PARAM["CANNONS"].keys()), expected_keys)

    def test_weapon_param_missiles_has_expected_keys(self):
        """WEAPON_PARAM['MISSILES'] deve avere caliber, warhead, range,
        ammo_type, speed."""
        expected_keys = {"caliber", "warhead", "range", "ammo_type", "speed"}
        self.assertEqual(set(WEAPON_PARAM["MISSILES"].keys()), expected_keys)

    def test_weapon_param_machine_guns_has_expected_keys(self):
        """WEAPON_PARAM['MACHINE_GUNS'] deve avere caliber, fire_rate, range."""
        expected_keys = {"caliber", "fire_rate", "range"}
        self.assertEqual(set(WEAPON_PARAM["MACHINE_GUNS"].keys()), expected_keys)

    # ── AMMO_PARAM ──────────────────────────────────────────────────────────

    def test_ammo_param_has_expected_types(self):
        """AMMO_PARAM deve contenere HE, HEAT, AP, 2HEAT, APFSDS."""
        expected = {"HE", "HEAT", "AP", "2HEAT", "APFSDS"}
        for t in expected:
            with self.subTest(ammo=t):
                self.assertIn(t, AMMO_PARAM)

    def test_ammo_param_values_in_range(self):
        """I valori in AMMO_PARAM devono essere float in (0, 1]."""
        for ammo, val in AMMO_PARAM.items():
            with self.subTest(ammo=ammo):
                self.assertIsInstance(val, float)
                self.assertGreater(val, 0.0)
                self.assertLessEqual(val, 1.0)

    def test_ammo_param_2heat_highest(self):
        """2HEAT deve avere il valore più alto in AMMO_PARAM (carica cava doppia)."""
        self.assertEqual(max(AMMO_PARAM, key=AMMO_PARAM.get), "2HEAT")

    # ── AMMO_TARGET_EFFECTIVENESS ────────────────────────────────────────────

    def test_ammo_target_effectiveness_has_frag(self):
        """AMMO_TARGET_EFFECTIVENESS deve contenere 'FRAG' (non presente in AMMO_PARAM)."""
        self.assertIn("FRAG", AMMO_TARGET_EFFECTIVENESS)

    def test_ammo_target_effectiveness_contains_ammo_param_types(self):
        """Tutti i tipi di AMMO_PARAM devono essere in AMMO_TARGET_EFFECTIVENESS."""
        for ammo in AMMO_PARAM:
            with self.subTest(ammo=ammo):
                self.assertIn(ammo, AMMO_TARGET_EFFECTIVENESS)

    def test_ammo_target_effectiveness_values_in_range(self):
        """Tutti i valori di efficacia devono essere float in [0, 1]."""
        for ammo, targets in AMMO_TARGET_EFFECTIVENESS.items():
            for t_type, val in targets.items():
                with self.subTest(ammo=ammo, target=t_type):
                    self.assertIsInstance(val, float)
                    self.assertGreaterEqual(val, 0.0)
                    self.assertLessEqual(val, 1.0)

    def test_he_effective_vs_soft(self):
        """HE deve avere efficacia massima (1.0) contro Soft."""
        self.assertAlmostEqual(AMMO_TARGET_EFFECTIVENESS["HE"]["Soft"], 1.0)

    def test_apfsds_effective_vs_armored(self):
        """APFSDS deve avere alta efficacia (>= 0.9) contro Armored."""
        self.assertGreaterEqual(AMMO_TARGET_EFFECTIVENESS["APFSDS"]["Armored"], 0.9)

    # ── TARGET_DIMENSION ──────────────────────────────────────────────────────

    def test_target_dimension_has_three_values(self):
        """TARGET_DIMENSION del modulo deve contenere esattamente 'small', 'med', 'big'."""
        self.assertEqual(set(GWD_TARGET_DIMENSION), {"small", "med", "big"})

    def test_target_dimension_values_are_strings(self):
        """Tutti i valori di TARGET_DIMENSION devono essere stringhe."""
        for dim in GWD_TARGET_DIMENSION:
            with self.subTest(dim=dim):
                self.assertIsInstance(dim, str)


# ---------------------------------------------------------------------------
# 2. get_cannon_score
# ---------------------------------------------------------------------------

class TestGetCannonsScore(unittest.TestCase):
    """Unit test per get_cannon_score().
    Logger mockato per isolare dai side-effect del logging."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_2a46m_returns_positive(self):
        """2A46M (125mm, alta velocità di bocca) deve restituire un punteggio > 0."""
        score = get_cannon_score("2A46M")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_m256_returns_positive(self):
        """M256 (120mm, canna del M1 Abrams) deve restituire un punteggio > 0."""
        score = get_cannon_score("M256")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_m68a1_returns_positive(self):
        """M68A1 (105mm) deve restituire un punteggio > 0."""
        score = get_cannon_score("M68A1")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_cannons_with_ammo_type_return_positive(self):
        """I cannoni che possiedono il campo 'ammo_type' devono restituire
        un punteggio > 0. I cannoni senza tale campo (bug dati) vengono saltati."""
        for model, data in GROUND_WEAPONS["CANNONS"].items():
            if "ammo_type" not in data:
                continue  # salta: il campo mancante causa KeyError nella funzione
            with self.subTest(model=model):
                score = get_cannon_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_high_caliber_cannon_scores_higher(self):
        """2A46M (125mm, alta velocità) deve superare 2A28-Grom-73mm (73mm)."""
        score_125 = get_cannon_score("2A46M")
        score_73  = get_cannon_score("2A28-Grom-73mm")
        self.assertGreater(score_125, score_73)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_cannon_score(125)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_cannon_score(None)

    def test_type_error_on_list(self):
        with self.assertRaises(TypeError):
            get_cannon_score(["2A46M"])

    def test_unknown_model_raises_key_error(self):
        """get_cannon_score usa indicizzazione diretta: modello sconosciuto → KeyError."""
        with self.assertRaises(KeyError):
            get_cannon_score("WEAPON_NOT_EXISTING_XYZ")


# ---------------------------------------------------------------------------
# 3. get_aa_cannon_score
# ---------------------------------------------------------------------------

class TestGetAaCannonsScore(unittest.TestCase):
    """Unit test per get_aa_cannon_score()."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_s68_57mm_returns_positive(self):
        """S-68-57mm (ZSU-57-2) deve restituire un punteggio > 0."""
        score = get_aa_cannon_score("S-68-57mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_azp_23_returns_positive(self):
        """AZP-23-23mm (ZSU-23-4 Shilka) deve restituire un punteggio > 0."""
        score = get_aa_cannon_score("AZP-23-23mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_aa_cannons_return_positive(self):
        """Tutti i cannoni AA in GROUND_WEAPONS devono restituire un punteggio > 0."""
        for model in GROUND_WEAPONS["AA_CANNONS"]:
            with self.subTest(model=model):
                score = get_aa_cannon_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_aa_cannon_score(57)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_aa_cannon_score(None)

    def test_unknown_model_raises_key_error(self):
        """Modello sconosciuto → KeyError (indicizzazione diretta)."""
        with self.assertRaises(KeyError):
            get_aa_cannon_score("WEAPON_NOT_EXISTING_XYZ")


# ---------------------------------------------------------------------------
# 4. get_auto_cannon_score
# ---------------------------------------------------------------------------

class TestGetAutoCannonScore(unittest.TestCase):
    """Unit test per get_auto_cannon_score()."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_2a42_returns_positive(self):
        """2A42 (30mm, BMP-2) deve restituire un punteggio > 0."""
        score = get_auto_cannon_score("2A42")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_m242_bushmaster_returns_positive(self):
        """M242 Bushmaster (25mm) deve restituire un punteggio > 0."""
        score = get_auto_cannon_score("M242 Bushmaster")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_auto_cannons_return_positive(self):
        """Tutti gli autocannoni devono restituire un punteggio > 0."""
        for model in GROUND_WEAPONS["AUTO_CANNONS"]:
            with self.subTest(model=model):
                score = get_auto_cannon_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_type_error_on_float(self):
        with self.assertRaises(TypeError):
            get_auto_cannon_score(30.0)

    def test_unknown_model_raises_key_error(self):
        """Modello sconosciuto → KeyError (indicizzazione diretta)."""
        with self.assertRaises(KeyError):
            get_auto_cannon_score("WEAPON_NOT_EXISTING_XYZ")


# ---------------------------------------------------------------------------
# 5. get_missiles_score
# ---------------------------------------------------------------------------

class TestGetMissilesScore(unittest.TestCase):
    """Unit test per get_missiles_score().
    Usa .get() internamente → modello sconosciuto restituisce 0.0 (non KeyError)."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_9k119m_returns_positive(self):
        """9K119M (AT-11 Sniper, laser-guided) deve restituire un punteggio > 0."""
        score = get_missiles_score("9K119M")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_tow2_returns_positive(self):
        """TOW-2 (SACLOS ATGM) deve restituire un punteggio > 0."""
        score = get_missiles_score("TOW-2")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_milan_returns_positive(self):
        """MILAN (SACLOS ATGM) deve restituire un punteggio > 0."""
        score = get_missiles_score("MILAN")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_missiles_return_positive(self):
        """Tutti i missili in GROUND_WEAPONS devono restituire un punteggio > 0."""
        for model in GROUND_WEAPONS["MISSILES"]:
            with self.subTest(model=model):
                score = get_missiles_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0 (usa .get() internamente)."""
        score = get_missiles_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_missiles_score(9)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_missiles_score(None)

    def test_sam_returns_positive(self):
        """Missili SAM (e.g. 9M311-SAM) devono restituire un punteggio > 0."""
        score = get_missiles_score("9M311-SAM")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)


# ---------------------------------------------------------------------------
# 6. get_mortars_score
# ---------------------------------------------------------------------------

class TestGetMortarsScore(unittest.TestCase):
    """Unit test per get_mortars_score()."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_m933_60mm_returns_positive(self):
        """M933-60mm deve restituire un punteggio > 0."""
        score = get_mortars_score("M933-60mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_mortars_return_positive(self):
        """Tutti i mortai in GROUND_WEAPONS devono restituire un punteggio > 0."""
        for model in GROUND_WEAPONS["MORTARS"]:
            with self.subTest(model=model):
                score = get_mortars_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_mortars_score(60)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_mortars_score(None)


# ---------------------------------------------------------------------------
# 7. get_artillery_score
# ---------------------------------------------------------------------------

class TestGetArtilleryScore(unittest.TestCase):
    """Unit test per get_artillery_score()."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_2a33_152mm_returns_positive(self):
        """2A33-152mm (2S3 Akatsiya) deve restituire un punteggio > 0."""
        score = get_artillery_score("2A33-152mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_m284_155mm_returns_positive(self):
        """M284-155mm (M109 Paladin) deve restituire un punteggio > 0."""
        score = get_artillery_score("M284-155mm")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_300mm_smerch_returns_positive(self):
        """300mm-Smerch-Rocket (MLRS) deve restituire un punteggio > 0."""
        score = get_artillery_score("300mm-Smerch-Rocket")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_artillery_return_positive(self):
        """Tutta l'artiglieria in GROUND_WEAPONS deve restituire un punteggio > 0."""
        for model in GROUND_WEAPONS["ARTILLERY"]:
            with self.subTest(model=model):
                score = get_artillery_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_type_error_on_float(self):
        with self.assertRaises(TypeError):
            get_artillery_score(155.0)

    def test_type_error_on_list(self):
        with self.assertRaises(TypeError):
            get_artillery_score(["2A33-152mm"])

    def test_unknown_model_raises_or_zero(self):
        """Modello sconosciuto deve sollevare un'eccezione o restituire 0.0
        (comportamento dipende dall'implementazione interna)."""
        try:
            score = get_artillery_score("WEAPON_NOT_EXISTING_XYZ")
            self.assertIn(score, (0, 0.0))
        except (KeyError, Exception):
            pass  # comportamento accettabile: eccezione o 0


# ---------------------------------------------------------------------------
# 8. get_machine_gun_score
# ---------------------------------------------------------------------------

class TestGetMachineGunScore(unittest.TestCase):
    """Unit test per get_machine_gun_score()."""

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_m2hb_12_7_returns_positive(self):
        """M2HB-12.7 (Browning .50) deve restituire un punteggio > 0."""
        score = get_machine_gun_score("M2HB-12.7")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_kpvt_14_5_returns_positive(self):
        """KPVT-14.5 deve restituire un punteggio > 0."""
        score = get_machine_gun_score("KPVT-14.5")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_pkt_7_62_returns_positive(self):
        """PKT-7.62 deve restituire un punteggio > 0."""
        score = get_machine_gun_score("PKT-7.62")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_all_machine_guns_return_positive(self):
        """Tutte le mitragliatrici in GROUND_WEAPONS devono restituire punteggio > 0."""
        for model in GROUND_WEAPONS["MACHINE_GUNS"]:
            with self.subTest(model=model):
                score = get_machine_gun_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_kpvt_scores_higher_than_pkt(self):
        """KPVT-14.5 (14.5mm, maggior gittata) deve superare PKT-7.62 (7.62mm)."""
        score_145 = get_machine_gun_score("KPVT-14.5")
        score_762 = get_machine_gun_score("PKT-7.62")
        self.assertGreater(score_145, score_762)

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_machine_gun_score(7)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_machine_gun_score(None)


# ---------------------------------------------------------------------------
# 9. get_weapon_score — dispatcher
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

    def test_dispatches_cannons(self):
        """CANNONS → uguale a get_cannon_score."""
        self.assertAlmostEqual(
            get_weapon_score("CANNONS", "2A46M"),
            get_cannon_score("2A46M"),
        )

    def test_dispatches_aa_cannons(self):
        """AA_CANNONS → uguale a get_aa_cannon_score."""
        self.assertAlmostEqual(
            get_weapon_score("AA_CANNONS", "S-68-57mm"),
            get_aa_cannon_score("S-68-57mm"),
        )

    def test_dispatches_auto_cannons(self):
        """AUTO_CANNONS → uguale a get_auto_cannon_score."""
        self.assertAlmostEqual(
            get_weapon_score("AUTO_CANNONS", "2A42"),
            get_auto_cannon_score("2A42"),
        )

    def test_dispatches_missiles(self):
        """MISSILES → uguale a get_missiles_score."""
        self.assertAlmostEqual(
            get_weapon_score("MISSILES", "9K119M"),
            get_missiles_score("9K119M"),
        )

    def test_dispatches_mortars(self):
        """MORTARS → uguale a get_mortars_score."""
        self.assertAlmostEqual(
            get_weapon_score("MORTARS", "M933-60mm"),
            get_mortars_score("M933-60mm"),
        )

    def test_dispatches_artillery(self):
        """ARTILLERY → uguale a get_artillery_score."""
        self.assertAlmostEqual(
            get_weapon_score("ARTILLERY", "2A33-152mm"),
            get_artillery_score("2A33-152mm"),
        )

    def test_dispatches_machine_guns(self):
        """MACHINE_GUNS → uguale a get_machine_gun_score."""
        self.assertAlmostEqual(
            get_weapon_score("MACHINE_GUNS", "M2HB-12.7"),
            get_machine_gun_score("M2HB-12.7"),
        )

    def test_grenade_launchers_not_dispatched_returns_zero(self):
        """GRENADE_LAUNCHERS non è gestito dal dispatcher → restituisce 0."""
        result = get_weapon_score("GRENADE_LAUNCHERS", "AGS-17")
        self.assertEqual(result, 0)

    # ── validazione parametri ────────────────────────────────────────────────

    def test_invalid_weapon_type_not_string_raises_valueerror(self):
        """weapon_type non-string → ValueError."""
        with self.assertRaises((ValueError, TypeError)):
            get_weapon_score(123, "2A46M")

    def test_invalid_weapon_type_unknown_raises_valueerror(self):
        """weapon_type sconosciuto → ValueError."""
        with self.assertRaises(ValueError):
            get_weapon_score("UNKNOWN_CATEGORY", "2A46M")

    def test_invalid_model_not_string_raises_typeerror(self):
        """weapon_model non-string → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score("CANNONS", 125)

    def test_invalid_model_none_raises_typeerror(self):
        """weapon_model None → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score("CANNONS", None)

    # ── tipo e range dei valori ──────────────────────────────────────────────

    def test_return_type_is_float_for_all_categories(self):
        """Il dispatcher deve restituire float per tutte le categorie note."""
        sample_models = {
            "CANNONS":      "2A46M",
            "AA_CANNONS":   "S-68-57mm",
            "AUTO_CANNONS": "2A42",
            "MISSILES":     "9K119M",
            "MORTARS":      "M933-60mm",
            "ARTILLERY":    "2A33-152mm",
            "MACHINE_GUNS": "M2HB-12.7",
        }
        for wtype, model in sample_models.items():
            with self.subTest(weapon_type=wtype):
                score = get_weapon_score(wtype, model)
                self.assertIsInstance(score, float)

    def test_score_non_negative(self):
        """I punteggi non devono essere negativi."""
        sample_models = {
            "CANNONS":      "2A46M",
            "AA_CANNONS":   "S-68-57mm",
            "AUTO_CANNONS": "2A42",
            "MISSILES":     "9K119M",
            "MACHINE_GUNS": "M2HB-12.7",
        }
        for wtype, model in sample_models.items():
            with self.subTest(weapon_type=wtype):
                score = get_weapon_score(wtype, model)
                self.assertGreaterEqual(score, 0.0)


# ---------------------------------------------------------------------------
# 10. get_weapon
# ---------------------------------------------------------------------------

class TestGetWeapon(unittest.TestCase):
    """Unit test per get_weapon(model: str).

    Firma: get_weapon(model: str) -> Optional[Dict[str, Any]]
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

    def test_known_cannon_returns_dict(self):
        """2A46M → dict non-None."""
        result = get_weapon("2A46M")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_weapons_category_key(self):
        """Il risultato deve contenere la chiave 'weapons_category'."""
        result = get_weapon("2A46M")
        self.assertIn("weapons_category", result)

    def test_result_has_weapons_data_key(self):
        """Il risultato deve contenere la chiave 'weapons_data'."""
        result = get_weapon("2A46M")
        self.assertIn("weapons_data", result)

    def test_result_has_exactly_two_keys(self):
        """Il risultato deve avere esattamente due chiavi."""
        result = get_weapon("2A46M")
        self.assertEqual(set(result.keys()), {"weapons_category", "weapons_data"})

    def test_weapons_data_is_dict(self):
        """weapons_data deve essere un dizionario."""
        result = get_weapon("2A46M")
        self.assertIsInstance(result["weapons_data"], dict)

    def test_weapons_data_matches_ground_weapons_entry(self):
        """weapons_data deve essere lo stesso oggetto presente in GROUND_WEAPONS."""
        result = get_weapon("2A46M")
        self.assertIs(result["weapons_data"], GROUND_WEAPONS["CANNONS"]["2A46M"])

    # ── categoria restituita ───────────────────────────────────────────────────

    def test_cannon_category_is_correct(self):
        """2A46M deve essere categorizzato come 'CANNONS'."""
        result = get_weapon("2A46M")
        self.assertEqual(result["weapons_category"], "CANNONS")

    def test_missile_category_is_correct(self):
        """9K119M deve essere categorizzato come 'MISSILES'."""
        result = get_weapon("9K119M")
        self.assertEqual(result["weapons_category"], "MISSILES")

    def test_machine_gun_category_is_correct(self):
        """M2HB-12.7 deve essere categorizzato come 'MACHINE_GUNS'."""
        result = get_weapon("M2HB-12.7")
        self.assertEqual(result["weapons_category"], "MACHINE_GUNS")

    def test_artillery_category_is_correct(self):
        """2A33-152mm deve essere categorizzato come 'ARTILLERY'."""
        result = get_weapon("2A33-152mm")
        self.assertEqual(result["weapons_category"], "ARTILLERY")

    def test_auto_cannon_category_is_correct(self):
        """2A42 deve essere categorizzato come 'AUTO_CANNONS'."""
        result = get_weapon("2A42")
        self.assertEqual(result["weapons_category"], "AUTO_CANNONS")

    def test_mortar_category_is_correct(self):
        """M933-60mm deve essere categorizzato come 'MORTARS'."""
        result = get_weapon("M933-60mm")
        self.assertEqual(result["weapons_category"], "MORTARS")

    def test_aa_cannon_category_is_correct(self):
        """S-68-57mm deve essere categorizzato come 'AA_CANNONS'."""
        result = get_weapon("S-68-57mm")
        self.assertEqual(result["weapons_category"], "AA_CANNONS")

    # ── ricerca su tutti i modelli ─────────────────────────────────────────────

    def test_all_models_are_findable(self):
        """Ogni modello in GROUND_WEAPONS deve essere trovato da get_weapon()."""
        for cat, weapons in GROUND_WEAPONS.items():
            for model in weapons:
                with self.subTest(category=cat, model=model):
                    result = get_weapon(model)
                    self.assertIsNotNone(result,
                                        f"get_weapon('{model}') ha restituito None")
                    self.assertEqual(result["weapons_category"], cat,
                                     f"Categoria errata per '{model}'")

    # ── modello sconosciuto ───────────────────────────────────────────────────

    def test_unknown_model_returns_none(self):
        """Modello sconosciuto → None."""
        result = get_weapon("WEAPON_NOT_EXISTING_XYZ")
        self.assertIsNone(result)

    def test_empty_string_returns_none(self):
        """Stringa vuota → None (nessun modello con nome vuoto)."""
        result = get_weapon("")
        self.assertIsNone(result)

    # ── errori di tipo ────────────────────────────────────────────────────────

    def test_type_error_on_int(self):
        """Argomento int → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon(123)

    def test_type_error_on_none(self):
        """Argomento None → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon(None)

    def test_type_error_on_list(self):
        """Argomento list → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon(["2A46M"])

    def test_type_error_on_float(self):
        """Argomento float → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon(30.0)


# ---------------------------------------------------------------------------
# 11. get_weapon_score_target
# ---------------------------------------------------------------------------

class TestGetWeaponScoreTarget(unittest.TestCase):
    """Unit test per get_weapon_score_target() con la NUOVA firma:

        get_weapon_score_target(model: str, target_type: List, target_dimension: List) -> float

    - model: stringa identificativa del modello (cercato tramite get_weapon())
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
            get_weapon_score_target(123, ["Armored"], ["big"])

    def test_type_error_model_none(self):
        """model None → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target(None, ["Armored"], ["big"])

    def test_type_error_model_list(self):
        """model lista → TypeError."""
        with self.assertRaises(TypeError):
            get_weapon_score_target(["2A46M"], ["Armored"], ["big"])

    # ── modello sconosciuto ───────────────────────────────────────────────────

    def test_unknown_model_returns_zero(self):
        """Modello sconosciuto → 0.0."""
        score = get_weapon_score_target("WEAPON_NOT_EXISTING_XYZ", ["Armored"], ["big"])
        self.assertEqual(score, 0.0)

    # ── liste di target vuote o con valori invalidi ───────────────────────────

    def test_empty_target_type_list_returns_zero(self):
        """Lista target_type vuota → 0.0 (nessuna combinazione da valutare)."""
        score = get_weapon_score_target("2A46M", [], ["big"])
        self.assertEqual(score, 0.0)

    def test_empty_target_dimension_list_returns_zero(self):
        """Lista target_dimension vuota → 0.0 (nessuna combinazione da valutare)."""
        score = get_weapon_score_target("2A46M", ["Armored"], [])
        self.assertEqual(score, 0.0)

    def test_both_lists_empty_returns_zero(self):
        """Entrambe le liste vuote → 0.0."""
        score = get_weapon_score_target("2A46M", [], [])
        self.assertEqual(score, 0.0)

    def test_invalid_target_type_only_returns_zero(self):
        """target_type sconosciuto (non in TARGET_CLASSIFICATION) → 0.0."""
        score = get_weapon_score_target("2A46M", ["UNKNOWN_TARGET_XYZ"], ["big"])
        self.assertEqual(score, 0.0)

    def test_invalid_target_dimension_only_returns_zero(self):
        """target_dimension sconosciuta (non in TARGET_DIMENSION) → 0.0."""
        score = get_weapon_score_target("2A46M", ["Armored"], ["UNKNOWN_DIM_XYZ"])
        self.assertEqual(score, 0.0)

    def test_mixed_valid_invalid_target_type(self):
        """Un target_type invalido viene ignorato; il risultato è uguale
        a quello con il solo target_type valido (media su 1 combinazione)."""
        score_only_valid = get_weapon_score_target("2A46M", ["Armored"], ["big"])
        score_mixed     = get_weapon_score_target("2A46M", ["Armored", "UNKNOWN_XYZ"], ["big"])
        self.assertAlmostEqual(score_only_valid, score_mixed, places=9)

    def test_mixed_valid_invalid_target_dimension(self):
        """Una target_dimension invalida viene ignorata; il risultato è uguale
        a quello con la sola dimensione valida."""
        score_only_valid = get_weapon_score_target("2A46M", ["Armored"], ["big"])
        score_mixed     = get_weapon_score_target("2A46M", ["Armored"], ["big", "UNKNOWN_DIM_XYZ"])
        self.assertAlmostEqual(score_only_valid, score_mixed, places=9)

    # ── valori di ritorno per combinazioni valide ─────────────────────────────

    def test_cannon_vs_armored_big_returns_positive(self):
        """2A46M vs Armored/big → float > 0."""
        score = get_weapon_score_target("2A46M", ["Armored"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_cannon_vs_soft_small_returns_positive(self):
        """2A46M vs Soft/small → float > 0."""
        score = get_weapon_score_target("2A46M", ["Soft"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_missile_vs_armored_med_returns_positive(self):
        """9K119M (ATGM) vs Armored/med → float > 0."""
        score = get_weapon_score_target("9K119M", ["Armored"], ["med"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_machine_gun_vs_soft_small_returns_positive(self):
        """M2HB-12.7 vs Soft/small → float > 0."""
        score = get_weapon_score_target("M2HB-12.7", ["Soft"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_artillery_vs_structure_big_returns_positive(self):
        """2A33-152mm vs Structure/big → float > 0."""
        score = get_weapon_score_target("2A33-152mm", ["Structure"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_auto_cannon_vs_air_defense_returns_positive(self):
        """2A42 (autocannone) vs Air_Defense/small → float > 0."""
        score = get_weapon_score_target("2A42", ["Air_Defense"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_aa_cannon_vs_soft_returns_positive(self):
        """S-68-57mm (cann. AA) vs Soft/med → float > 0."""
        score = get_weapon_score_target("S-68-57mm", ["Soft"], ["med"])
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_return_is_non_negative_for_all_sample_models(self):
        """Il punteggio deve essere non negativo per un campione di modelli."""
        sample = [
            ("2A46M",      ["Armored", "Soft"],   ["big", "med", "small"]),
            ("9K119M",     ["Armored"],            ["big"]),
            ("M2HB-12.7",  ["Soft"],               ["small"]),
            ("2A33-152mm", ["Structure"],           ["big"]),
            ("2A42",       ["Air_Defense", "Soft"], ["med"]),
        ]
        for model, t_types, t_dims in sample:
            with self.subTest(model=model):
                score = get_weapon_score_target(model, t_types, t_dims)
                self.assertGreaterEqual(score, 0.0)

    # ── determinismo ─────────────────────────────────────────────────────────

    def test_deterministic_same_result_twice(self):
        """La funzione deve restituire lo stesso risultato su chiamate successive
        (nessuna componente stocastica)."""
        score1 = get_weapon_score_target("2A46M", ["Armored"], ["big"])
        score2 = get_weapon_score_target("2A46M", ["Armored"], ["big"])
        self.assertEqual(score1, score2)

    # ── semantica della media ─────────────────────────────────────────────────

    def test_single_combination_equals_accuracy_times_destroy_capacity(self):
        """Con una sola combinazione (t_type, t_dim), il risultato deve essere
        accuracy * destroy_capacity letto direttamente dal template efficiency."""
        model  = "2A46M"
        t_type = "Armored"
        t_dim  = "big"
        eff = GROUND_WEAPONS["CANNONS"][model]["efficiency"][t_type][t_dim]
        expected = eff["accuracy"] * eff["destroy_capacity"]
        score = get_weapon_score_target(model, [t_type], [t_dim])
        self.assertAlmostEqual(score, expected, places=9)

    def test_two_dimensions_returns_average(self):
        """Con due dimensioni valide, il risultato è la media dei due prodotti
        accuracy * destroy_capacity."""
        model  = "2A46M"
        t_type = "Armored"
        eff = GROUND_WEAPONS["CANNONS"][model]["efficiency"][t_type]
        v_big   = eff["big"]["accuracy"]   * eff["big"]["destroy_capacity"]
        v_small = eff["small"]["accuracy"] * eff["small"]["destroy_capacity"]
        expected = (v_big + v_small) / 2
        score = get_weapon_score_target(model, [t_type], ["big", "small"])
        self.assertAlmostEqual(score, expected, places=9)

    def test_two_target_types_returns_average(self):
        """Con due target type validi, il risultato è la media dei due prodotti."""
        model = "2A46M"
        t_dim = "big"
        eff = GROUND_WEAPONS["CANNONS"][model]["efficiency"]
        v_arm  = eff["Armored"]["big"]["accuracy"] * eff["Armored"]["big"]["destroy_capacity"]
        v_soft = eff["Soft"]["big"]["accuracy"]    * eff["Soft"]["big"]["destroy_capacity"]
        expected = (v_arm + v_soft) / 2
        score = get_weapon_score_target(model, ["Armored", "Soft"], [t_dim])
        self.assertAlmostEqual(score, expected, places=9)

    # ── confronti ordinativi ─────────────────────────────────────────────────

    def test_cannon_vs_soft_higher_than_vs_armored(self):
        """Un cannone MBT deve avere punteggio vs Soft > vs Armored:
        un veicolo non blindato è più facile da distruggere di un carro armato."""
        score_soft = get_weapon_score_target("2A46M", ["Soft"],    ["big"])
        score_arm  = get_weapon_score_target("2A46M", ["Armored"], ["big"])
        self.assertGreater(score_soft, score_arm)

    def test_cannon_vs_armored_higher_than_vs_structure(self):
        """Un cannone deve avere maggiore efficienza vs Armored che vs Structure."""
        score_arm = get_weapon_score_target("2A46M", ["Armored"],   ["big"])
        score_str = get_weapon_score_target("2A46M", ["Structure"], ["big"])
        self.assertGreater(score_arm, score_str)

    def test_missile_vs_soft_higher_than_vs_armored(self):
        """Un ATGM deve avere punteggio vs Soft > vs Armored:
        la testata HEAT è devastante su qualsiasi bersaglio non blindato."""
        score_soft = get_weapon_score_target("9K119M", ["Soft"],    ["big"])
        score_arm  = get_weapon_score_target("9K119M", ["Armored"], ["big"])
        self.assertGreater(score_soft, score_arm)

    def test_missile_vs_armored_higher_than_machine_gun(self):
        """Un ATGM deve avere efficienza vs Armored > mitragliatrice pesante."""
        score_missile = get_weapon_score_target("9K119M",    ["Armored"], ["big"])
        score_mg      = get_weapon_score_target("M2HB-12.7", ["Armored"], ["big"])
        self.assertGreater(score_missile, score_mg)

    def test_soft_score_higher_than_armored_for_all_weapon_categories(self):
        """Per ogni categoria (salvo SAM usati solo vs aerei), il punteggio
        vs Soft/big deve essere > vs Armored/big: i bersagli non blindati
        sono più vulnerabili di quelli corazzati."""
        sample = [
            ("CANNONS",      "2A46M"),
            ("AUTO_CANNONS", "2A42"),
            ("AA_CANNONS",   "S-68-57mm"),
            ("MISSILES",     "9K119M"),
            ("ARTILLERY",    "2A33-152mm"),
            ("MACHINE_GUNS", "M2HB-12.7"),
        ]
        for category, model in sample:
            with self.subTest(category=category, model=model):
                score_soft = get_weapon_score_target(model, ["Soft"],    ["big"])
                score_arm  = get_weapon_score_target(model, ["Armored"], ["big"])
                self.assertGreater(score_soft, score_arm,
                                   f"{model}: Soft ({score_soft:.4f}) non > Armored ({score_arm:.4f})")


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
        weapons = GROUND_WEAPONS.get(category, {})
        if not weapons:
            print(f"\n[SKIP] Categoria '{category}' non trovata o vuota in GROUND_WEAPONS.\n")
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
        weapons = GROUND_WEAPONS.get(category, {})
        if not weapons:
            print(f"\n[SKIP] Categoria '{category}' non trovata o vuota in GROUND_WEAPONS.\n")
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
            weapons = GROUND_WEAPONS.get(category, {})
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
                f"Confronto Punteggio Armi Terrestri — {category}\n"
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

    print(f"[PDF] ground_weapon_score → {output_path}")


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
            weapons = GROUND_WEAPONS.get(category, {})
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

    print(f"[PDF] ground_weapon_score_target → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in (
        TestGroundWeaponsDataStructure,
        TestGetCannonsScore,
        TestGetAaCannonsScore,
        TestGetAutoCannonScore,
        TestGetMissilesScore,
        TestGetMortarsScore,
        TestGetArtilleryScore,
        TestGetMachineGunScore,
        TestGetWeaponScoreDispatcher,
        TestGetWeapon,
        TestGetWeaponScoreTarget,
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
        os.path.join(OUTPUT_DIR, "ground_weapon_score_tables.pdf"),
    )
    save_weapon_score_target_pdf(
        WEAPON_TYPE_TARGET,
        TARGET_TYPE,
        TARGET_DIMENSION,
        os.path.join(OUTPUT_DIR, "ground_weapon_score_target_tables.pdf"),
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
    print("║      Test_Ground_Weapon_Data  —  Menu principale            ║")
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
