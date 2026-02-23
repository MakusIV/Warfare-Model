"""
Test_Aircraft_Weapon_Data.py
============================
Unit tests (unittest) e tabelle di confronto punteggi per il modulo
Aircraft_Weapon_Data.

Utilizzo:
    python -m pytest Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Weapon_Data.py -v
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Weapon_Data.py            # test + tabelle
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Weapon_Data.py --tables-only
    python  Code/Dynamic_War_Manager/Source/Test/Test_Aircraft_Weapon_Data.py --tests-only

Bug nel modulo Aircraft_Weapon_Data (documentati nei test):
  B0. logger.warning() / logger.debug() chiamati sull'istanza Logger invece
      che su Logger.logger (l'oggetto logging.Logger interno) → AttributeError.
      Per isolare la logica dagli effetti del logger, i test usano setUp/tearDown
      con unittest.mock.patch per sostituire logger con un MagicMock.
  B1. get_bombs_score(): `if bomb_type != 'type_not_specified'` era invertita →
      ritornava 0.0 per TUTTE le bombe reali. [CORRETTO: cambiato != in ==]
  BM. get_missiles_score(): `weapon[param_name]` causava TypeError per i missili
      AIM-7 (SARH) che hanno `active_range: None`.
      [CORRETTO: sostituito con `weapon.get(param_name) or 0.0`]
  B2. get_weapon_score_target(): `score` non inizializzata → NameError.
  B3. get_weapon_score_target(): usa la lista `target_type` come chiave del
      dizionario efficiency invece della variabile di loop `t_type` → TypeError.
  B4. get_weapon_score_target(): stessa issue con `target_dimension` vs `t_dim`.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURAZIONE — modificare le liste per personalizzare le tabelle
# ─────────────────────────────────────────────────────────────────────────────

# Categorie per le tabelle get_weapon_score()
WEAPON_TYPE_SCORE: List[str] = [
    "MISSILES_AAM",
    "MISSILES_ASM",
    "BOMBS",
    "ROCKETS",
    "CANNONS",
    "MACHINE_GUNS",
]

# Categorie per le tabelle get_weapon_score_target()
WEAPON_TYPE_TARGET: List[str] = [
    "MISSILES_ASM",
    "BOMBS",
    "ROCKETS",
    "CANNONS",
    "MACHINE_GUNS",
]

# Tipi di bersaglio per get_weapon_score_target()
TARGET_TYPE: List[str] = ["Soft", "Armored", "Structure", "Air_Defense", "ship"]

# Dimensioni del bersaglio per get_weapon_score_target()
# Nota: le chiavi nei diz. efficiency sono "big"/"med"/"small" mentre il modulo
# definisce TARGET_DIMENSION = ['small', 'medium', 'large'] → "big" e "med"
# non superano la validazione interna (Bug B6 noto, documentato nei test).
TARGET_DIMENSION: List[str] = ["med"]

# Directory di output per i PDF
OUTPUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "out"))

# Costante per il patch del logger in tutti i test
_LOGGER_PATH = "Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data.logger"

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORT DEL MODULO SOTTO TEST
# ─────────────────────────────────────────────────────────────────────────────

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import (
    AIR_WEAPONS,
    get_weapon,
    is_missile,
    is_bomb,
    is_rocket,
    is_cannon,
    is_machine_gun,
    get_missiles_score,
    get_bombs_score,
    get_rockets_score,
    get_cannons_score,
    get_machine_guns_score,
    get_weapon_score,
    get_weapon_score_target,
)

# ─────────────────────────────────────────────────────────────────────────────
#  UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestGetWeapon(unittest.TestCase):
    """
    Unit test per get_weapon().
    Questa funzione non chiama logger direttamente → nessun patch necessario.
    """

    def test_aam_radar_found(self):
        """get_weapon restituisce il dizionario corretto per AIM-54A-MK47 (AAM radar)."""
        result = get_weapon("AIM-54A-MK47")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "MISSILES_AAM")
        self.assertIn("weapons_type", result)
        self.assertIn("weapons_data", result)

    def test_aam_infrared_found(self):
        """get_weapon restituisce la categoria corretta per un missile AAM IR."""
        result = get_weapon("AIM-9L")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "MISSILES_AAM")

    def test_asm_found(self):
        """get_weapon restituisce la categoria corretta per un missile ASM."""
        result = get_weapon("RB-05A")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "MISSILES_ASM")

    def test_bomb_found(self):
        """get_weapon restituisce la categoria corretta per una bomba."""
        result = get_weapon("Mk-84")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "BOMBS")

    def test_rocket_found(self):
        """get_weapon restituisce la categoria corretta per un razzo."""
        result = get_weapon("Zuni-Mk71")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "ROCKETS")

    def test_cannon_found(self):
        """get_weapon restituisce la categoria corretta per un cannone (UPK-23)."""
        result = get_weapon("UPK-23")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "CANNONS")

    def test_machine_gun_found(self):
        """get_weapon restituisce la categoria corretta per AN-M2 (MACHINE_GUNS)."""
        result = get_weapon("AN-M2")
        self.assertIsNotNone(result)
        self.assertEqual(result["weapons_category"], "MACHINE_GUNS")

    def test_weapons_data_is_nonempty_dict(self):
        """weapons_data deve essere un dizionario non vuoto."""
        result = get_weapon("AIM-54A-MK47")
        self.assertIsInstance(result["weapons_data"], dict)
        self.assertTrue(result["weapons_data"])

    def test_unknown_weapon_returns_none(self):
        """get_weapon restituisce None per un modello sconosciuto."""
        self.assertIsNone(get_weapon("WEAPON_NOT_EXISTING_XYZ"))

    def test_type_error_on_int(self):
        with self.assertRaises(TypeError):
            get_weapon(123)

    def test_type_error_on_none(self):
        with self.assertRaises(TypeError):
            get_weapon(None)

    def test_type_error_on_list(self):
        with self.assertRaises(TypeError):
            get_weapon(["AIM-9L"])


class TestIsWeaponType(unittest.TestCase):
    """
    Unit test per is_missile, is_bomb, is_rocket, is_cannon, is_machine_gun.
    Queste funzioni non invocano il logger → nessun patch necessario.
    """

    # ── is_missile ──────────────────────────────────────────────
    def test_is_missile_aam_radar_true(self):
        self.assertTrue(is_missile("AIM-54A-MK47"))

    def test_is_missile_aam_ir_true(self):
        self.assertTrue(is_missile("AIM-9L"))

    def test_is_missile_asm_true(self):
        self.assertTrue(is_missile("RB-05A"))

    def test_is_missile_bomb_false(self):
        self.assertFalse(is_missile("Mk-84"))

    def test_is_missile_rocket_false(self):
        self.assertFalse(is_missile("Zuni-Mk71"))

    def test_is_missile_cannon_false(self):
        self.assertFalse(is_missile("UPK-23"))

    def test_is_missile_unknown_false(self):
        self.assertFalse(is_missile("WEAPON_NOT_EXISTING_XYZ"))

    def test_is_missile_type_error(self):
        with self.assertRaises(TypeError):
            is_missile(42)

    # ── is_bomb ─────────────────────────────────────────────────
    def test_is_bomb_true(self):
        self.assertTrue(is_bomb("Mk-84"))

    def test_is_bomb_missile_false(self):
        self.assertFalse(is_bomb("AIM-54A-MK47"))

    def test_is_bomb_cannon_false(self):
        self.assertFalse(is_bomb("UPK-23"))

    def test_is_bomb_unknown_false(self):
        self.assertFalse(is_bomb("WEAPON_NOT_EXISTING_XYZ"))

    def test_is_bomb_type_error(self):
        with self.assertRaises(TypeError):
            is_bomb(None)

    # ── is_rocket ───────────────────────────────────────────────
    def test_is_rocket_true(self):
        self.assertTrue(is_rocket("Zuni-Mk71"))

    def test_is_rocket_cannon_false(self):
        self.assertFalse(is_rocket("UPK-23"))

    def test_is_rocket_missile_false(self):
        self.assertFalse(is_rocket("AIM-9L"))

    def test_is_rocket_unknown_false(self):
        self.assertFalse(is_rocket("WEAPON_NOT_EXISTING_XYZ"))

    def test_is_rocket_type_error(self):
        with self.assertRaises(TypeError):
            is_rocket(3.14)

    # ── is_cannon ───────────────────────────────────────────────
    def test_is_cannon_upk23_true(self):
        self.assertTrue(is_cannon("UPK-23"))

    def test_is_cannon_m61a1_true(self):
        self.assertTrue(is_cannon("M61A1"))

    def test_is_cannon_bomb_false(self):
        self.assertFalse(is_cannon("Mk-84"))

    def test_is_cannon_missile_false(self):
        self.assertFalse(is_cannon("AIM-9L"))

    def test_is_cannon_unknown_false(self):
        self.assertFalse(is_cannon("WEAPON_NOT_EXISTING_XYZ"))

    def test_is_cannon_machine_gun_false(self):
        """AN-M2 e M3-Browning sono solo in MACHINE_GUNS, non in CANNONS."""
        self.assertFalse(is_cannon("AN-M2"))
        self.assertFalse(is_cannon("M3-Browning"))

    def test_is_cannon_type_error(self):
        with self.assertRaises(TypeError):
            is_cannon(True)

    # ── is_machine_gun ──────────────────────────────────────────
    def test_is_machine_gun_an_m2_true(self):
        self.assertTrue(is_machine_gun("AN-M2"))

    def test_is_machine_gun_m3_browning_true(self):
        self.assertTrue(is_machine_gun("M3-Browning"))

    def test_is_machine_gun_cannon_false(self):
        """UPK-23 è solo in CANNONS, non in MACHINE_GUNS."""
        self.assertFalse(is_machine_gun("UPK-23"))

    def test_is_machine_gun_unknown_false(self):
        self.assertFalse(is_machine_gun("WEAPON_NOT_EXISTING_XYZ"))

    def test_is_machine_gun_type_error(self):
        with self.assertRaises(TypeError):
            is_machine_gun({})


class TestGetWeaponTypeScores(unittest.TestCase):
    """
    Unit test per le funzioni get_*_score() specializzate.
    Il logger viene sostituito con MagicMock per isolare i test dal Bug B0.
    """

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    # ── get_missiles_score ──────────────────────────────────────
    def test_missiles_score_aam_radar_positive(self):
        """Punteggio di AIM-54A-MK47 (AAM radar) deve essere > 0."""
        score = get_missiles_score("AIM-54A-MK47")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_missiles_score_aam_radar_c47_ge_a47(self):
        """AIM-54C-MK47 (versione migliorata) deve avere punteggio >= AIM-54A-MK47."""
        self.assertGreaterEqual(
            get_missiles_score("AIM-54C-MK47"),
            get_missiles_score("AIM-54A-MK47"),
        )

    def test_missiles_score_aam_ir_positive(self):
        """Punteggio di AIM-9L (AAM IR) deve essere > 0."""
        score = get_missiles_score("AIM-9L")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_missiles_score_aam_ir_9x_ge_9l(self):
        """AIM-9X (versione più recente) deve avere punteggio >= AIM-9L."""
        self.assertGreaterEqual(
            get_missiles_score("AIM-9X"),
            get_missiles_score("AIM-9L"),
        )

    def test_missiles_score_aam_radar_sarh_positive(self):
        """
        Bug BM corretto: AIM-7 (SARH) avevano `active_range: None` →
        TypeError con `weapon[param_name]`.
        Dopo la correzione (`weapon.get(param_name) or 0.0`) devono restituire > 0.
        """
        for model in ("AIM-7E", "AIM-7F", "AIM-7M", "AIM-7MH", "AIM-7P"):
            with self.subTest(model=model):
                score = get_missiles_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_missiles_score_asm_positive(self):
        """Punteggio di RB-05A (ASM) deve essere > 0."""
        score = get_missiles_score("RB-05A")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_missiles_score_unknown_zero(self):
        """Arma sconosciuta → 0.0 (logger mockato per evitare Bug B0)."""
        score = get_missiles_score("WEAPON_NOT_EXISTING_XYZ")
        self.assertEqual(score, 0.0)

    def test_missiles_score_type_error(self):
        with self.assertRaises(TypeError):
            get_missiles_score(99)

    # ── get_bombs_score ─────────────────────────────────────────
    def test_bombs_score_known_bomb_positive(self):
        """
        Bug B1 corretto: la condizione era `!= 'type_not_specified'` (invertita).
        Dopo la correzione (`== 'type_not_specified'`) le bombe reali calcolano
        il punteggio correttamente → deve essere > 0.
        """
        score = get_bombs_score("Mk-84")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_bombs_score_mk83_positive(self):
        """Bug B1 corretto: Mk-83 deve restituire un punteggio > 0."""
        score = get_bombs_score("Mk-83")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_bombs_score_unknown_zero(self):
        """Arma sconosciuta → 0.0."""
        self.assertEqual(get_bombs_score("WEAPON_NOT_EXISTING_XYZ"), 0.0)

    def test_bombs_score_type_error(self):
        with self.assertRaises(TypeError):
            get_bombs_score(3.14)

    # ── get_rockets_score ───────────────────────────────────────
    def test_rockets_score_positive(self):
        score = get_rockets_score("Zuni-Mk71")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_rockets_score_all_types(self):
        """Tutti i razzi in AIR_WEAPONS devono restituire un punteggio > 0."""
        for model in AIR_WEAPONS["ROCKETS"]:
            with self.subTest(model=model):
                score = get_rockets_score(model)
                self.assertIsInstance(score, float)
                self.assertGreater(score, 0.0)

    def test_rockets_score_unknown_zero(self):
        self.assertEqual(get_rockets_score("WEAPON_NOT_EXISTING_XYZ"), 0.0)

    def test_rockets_score_type_error(self):
        with self.assertRaises(TypeError):
            get_rockets_score(0)

    # ── get_cannons_score ───────────────────────────────────────
    def test_cannons_score_positive(self):
        score = get_cannons_score("UPK-23")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_cannons_score_gau8_greater_than_upk23(self):
        """GAU-8/A (30mm, 4200 rpm) deve avere punteggio > UPK-23 (23mm, 3000 rpm)."""
        self.assertGreater(get_cannons_score("GAU-8/A"), get_cannons_score("UPK-23"))

    def test_cannons_score_unknown_zero(self):
        self.assertEqual(get_cannons_score("WEAPON_NOT_EXISTING_XYZ"), 0.0)

    def test_cannons_score_type_error(self):
        with self.assertRaises(TypeError):
            get_cannons_score([])

    # ── get_machine_guns_score ──────────────────────────────────
    def test_machine_guns_score_an_m2_positive(self):
        score = get_machine_guns_score("AN-M2")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_machine_guns_score_m3_browning_positive(self):
        score = get_machine_guns_score("M3-Browning")
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.0)

    def test_machine_guns_score_unknown_zero(self):
        self.assertEqual(get_machine_guns_score("WEAPON_NOT_EXISTING_XYZ"), 0.0)

    def test_machine_guns_score_type_error(self):
        with self.assertRaises(TypeError):
            get_machine_guns_score(None)


class TestGetWeaponScore(unittest.TestCase):
    """
    Unit test per get_weapon_score() (dispatcher generale).
    Logger mockato per isolare il test dal Bug B0.
    """

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    def test_dispatches_aam_to_missiles(self):
        """get_weapon_score delega MISSILES_AAM a get_missiles_score."""
        self.assertEqual(get_weapon_score("AIM-54A-MK47"), get_missiles_score("AIM-54A-MK47"))

    def test_dispatches_aam_ir_to_missiles(self):
        self.assertEqual(get_weapon_score("AIM-9L"), get_missiles_score("AIM-9L"))

    def test_dispatches_asm_to_missiles(self):
        """get_weapon_score delega MISSILES_ASM a get_missiles_score."""
        self.assertEqual(get_weapon_score("RB-05A"), get_missiles_score("RB-05A"))

    def test_dispatches_bomb_to_bombs(self):
        """get_weapon_score delega BOMBS a get_bombs_score."""
        self.assertEqual(get_weapon_score("Mk-84"), get_bombs_score("Mk-84"))

    def test_dispatches_rocket_to_rockets(self):
        """get_weapon_score delega ROCKETS a get_rockets_score."""
        self.assertEqual(get_weapon_score("Zuni-Mk71"), get_rockets_score("Zuni-Mk71"))

    def test_dispatches_cannon_to_cannons(self):
        """get_weapon_score delega CANNONS a get_cannons_score."""
        self.assertEqual(get_weapon_score("UPK-23"), get_cannons_score("UPK-23"))

    def test_dispatches_machine_gun_to_machine_guns(self):
        """get_weapon_score delega MACHINE_GUNS a get_machine_guns_score."""
        self.assertEqual(get_weapon_score("AN-M2"), get_machine_guns_score("AN-M2"))

    def test_unknown_weapon_zero(self):
        """Arma sconosciuta → 0.0."""
        self.assertEqual(get_weapon_score("WEAPON_NOT_EXISTING_XYZ"), 0.0)

    def test_type_error(self):
        with self.assertRaises(TypeError):
            get_weapon_score(999)

    def test_return_type_is_float(self):
        """Tutti i modelli noti devono restituire un float."""
        for model in ("AIM-54A-MK47", "AIM-9L", "RB-05A", "Zuni-Mk71", "UPK-23", "AN-M2"):
            with self.subTest(model=model):
                self.assertIsInstance(get_weapon_score(model), float)

    def test_score_is_non_negative(self):
        """I punteggi devono essere >= 0. Non sono normalizzati a [0,1]."""
        for model in ("AIM-54A-MK47", "AIM-9L", "RB-05A", "Zuni-Mk71", "UPK-23", "AN-M2"):
            with self.subTest(model=model):
                self.assertGreaterEqual(get_weapon_score(model), 0.0)

    def test_aam_scores_ordered(self):
        """Verifica l'ordinamento atteso dei punteggi AAM."""
        aim54c = get_weapon_score("AIM-54C-MK47")
        aim54a = get_weapon_score("AIM-54A-MK47")
        aim9x  = get_weapon_score("AIM-9X")
        aim9l  = get_weapon_score("AIM-9L")
        self.assertGreaterEqual(aim54c, aim54a)
        self.assertGreaterEqual(aim9x, aim9l)


class TestGetWeaponScoreTarget(unittest.TestCase):
    """
    Unit test per get_weapon_score_target().
    Logger mockato per isolare i test dal Bug B0.

    Bug documentati:
      B2. `score` non inizializzata prima del loop → NameError.
      B3. `weapon.get('efficiency').get(target_type)` usa la *lista* target_type
          invece della variabile di loop t_type → TypeError (unhashable list).
      B4. Stessa issue con target_dimension vs t_dim.
      B6. Le chiavi efficiency ("big"/"med"/"small") non corrispondono a
          TARGET_DIMENSION del modulo ['small','medium','large'] → "big" e "med"
          non superano la validazione e vengono sempre saltati.
    """

    def setUp(self):
        self._logger_patcher = patch(_LOGGER_PATH, MagicMock())
        self._logger_patcher.start()

    def tearDown(self):
        self._logger_patcher.stop()

    # ── casi che restituiscono 0.0 correttamente ─────────────────
    def test_aam_radar_returns_zero_early(self):
        """MISSILES_AAM: ritorno anticipato 0.0 (non implementato per AAM)."""
        self.assertEqual(get_weapon_score_target("AIM-54A-MK47", ["Soft"], ["small"]), 0.0)

    def test_aam_ir_returns_zero_early(self):
        """MISSILES_AAM IR: ritorno anticipato 0.0."""
        self.assertEqual(get_weapon_score_target("AIM-9L", ["Armored"], ["small"]), 0.0)

    def test_empty_target_type_returns_zero(self):
        """Lista target_type vuota → loop non eseguito → 0.0."""
        self.assertEqual(get_weapon_score_target("RB-05A", [], ["small"]), 0.0)

    def test_empty_target_dimension_returns_zero(self):
        """Lista target_dimension vuota → loop interno non eseguito → 0.0."""
        self.assertEqual(get_weapon_score_target("RB-05A", ["Soft"], []), 0.0)

    def test_all_unknown_target_types_returns_zero(self):
        """Tutti i target_type sconosciuti → skip completo del loop → 0.0."""
        self.assertEqual(
            get_weapon_score_target("RB-05A", ["UNKNOWN_XYZ"], ["small"]), 0.0
        )

    def test_all_unknown_target_dimensions_returns_zero(self):
        """
        Bug B6: "big" e "med" non sono in TARGET_DIMENSION del modulo
        ['small','medium','large'] → skip → 0.0.
        """
        self.assertEqual(
            get_weapon_score_target("RB-05A", ["Soft"], ["UNKNOWN_DIM_XYZ"]), 0.0
        )

    def test_target_dim_big_skipped_due_to_bug_b6(self):
        """
        Bug B6: "big" non è in TARGET_DIMENSION = ['small','medium','large'] →
        il loop interno lo salta → target_evaluation_count resta 0 → 0.0.
        """
        self.assertEqual(
            get_weapon_score_target("RB-05A", ["Soft"], ["big"]), 0.0
        )

    def test_target_dim_med_skipped_due_to_bug_b6(self):
        """Bug B6: "med" non è in TARGET_DIMENSION → 0.0."""
        self.assertEqual(
            get_weapon_score_target("RB-05A", ["Soft"], ["med"]), 0.0
        )

    def test_unknown_model_returns_zero(self):
        """Arma sconosciuta → get_weapon restituisce None → 0.0."""
        self.assertEqual(
            get_weapon_score_target("WEAPON_NOT_EXISTING_XYZ", ["Soft"], ["small"]), 0.0
        )

    # ── casi che evidenziano i bug B3/B4 ────────────────────────
    def test_valid_asm_valid_target_raises_error_bug_b3(self):
        """
        Bug B3: con un target_dim valido ("small" è in TARGET_DIMENSION),
        il loop interno avanza e chiama:
            weapon.get('efficiency').get(target_type)
        dove target_type = ['Soft'] (lista, non stringa) → TypeError.
        """
        with self.assertRaises((TypeError, NameError, AttributeError)):
            get_weapon_score_target("RB-05A", ["Soft"], ["small"])

    def test_valid_cannon_valid_target_raises_error_bug_b3(self):
        """Bug B3: stesso errore per un cannone."""
        with self.assertRaises((TypeError, NameError, AttributeError)):
            get_weapon_score_target("UPK-23", ["Armored"], ["small"])

    def test_valid_bomb_valid_target_raises_error_bug_b3(self):
        """Bug B3: stesso errore per una bomba."""
        with self.assertRaises((TypeError, NameError, AttributeError)):
            get_weapon_score_target("Mk-84", ["Soft"], ["small"])

    def test_valid_rocket_valid_target_raises_error_bug_b3(self):
        """Bug B3: stesso errore per un razzo."""
        with self.assertRaises((TypeError, NameError, AttributeError)):
            get_weapon_score_target("Zuni-Mk71", ["Soft"], ["small"])

    # ── validazione tipo parametro ───────────────────────────────
    def test_type_error_non_string_model_int(self):
        with self.assertRaises(TypeError):
            get_weapon_score_target(123, ["Soft"], ["small"])

    def test_type_error_non_string_model_none(self):
        with self.assertRaises(TypeError):
            get_weapon_score_target(None, ["Soft"], ["small"])


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITÀ CONDIVISE PER LA GENERAZIONE DELLE TABELLE
# ─────────────────────────────────────────────────────────────────────────────

def _is_nan(value: float) -> bool:
    try:
        return value != value
    except Exception:
        return False


def _safe_score(model: str) -> float:
    """
    Chiama get_weapon_score() con il logger mockato.
    Ritorna float('nan') in caso di eccezione non gestita.
    """
    try:
        mock_logger = MagicMock()
        with patch(_LOGGER_PATH, mock_logger):
            return get_weapon_score(model)
    except Exception:
        return float("nan")


def _safe_score_target(model: str, t_type: str, t_dim: str) -> float:
    """
    Chiama get_weapon_score_target() per una singola combinazione
    (target_type, target_dimension) con il logger mockato.
    Ritorna float('nan') in caso di eccezione (Bug B2/B3/B4).
    """
    try:
        mock_logger = MagicMock()
        with patch(_LOGGER_PATH, mock_logger):
            return get_weapon_score_target(model, [t_type], [t_dim])
    except Exception:
        return float("nan")


# ─────────────────────────────────────────────────────────────────────────────
#  TABELLE — STAMPA A TERMINALE
# ─────────────────────────────────────────────────────────────────────────────

def print_weapon_score_tables(weapon_type_list: List[str]) -> None:
    """
    Stampa a terminale una tabella get_weapon_score() per ogni categoria,
    ordinata per punteggio decrescente.
    """
    for category in weapon_type_list:
        weapons = AIR_WEAPONS.get(category, {})
        if not weapons:
            print(f"\n[SKIP] Categoria '{category}' non trovata in AIR_WEAPONS.\n")
            continue

        rows = [(model, _safe_score(model)) for model in weapons]
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
    """
    Stampa a terminale una tabella get_weapon_score_target() per ogni categoria,
    con colonne per ogni combinazione (target_type × target_dimension).
    """
    combinations = [(t, d) for t in target_type_list for d in target_dimension_list]

    for category in weapon_type_list:
        weapons = AIR_WEAPONS.get(category, {})
        if not weapons:
            print(f"\n[SKIP] Categoria '{category}' non trovata in AIR_WEAPONS.\n")
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
    """
    Salva un PDF con una pagina per categoria.
    Ogni pagina: tabella get_weapon_score() ordinata per punteggio decrescente,
    con colorazione heatmap (verde=alto, rosso=basso).
    """
    plt, PdfPages = _setup_matplotlib()
    if plt is None:
        print("[PDF] matplotlib non disponibile — generazione PDF saltata.")
        return

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with PdfPages(output_path) as pdf:
        for category in weapon_type_list:
            weapons = AIR_WEAPONS.get(category, {})
            if not weapons:
                continue

            rows = [(model, _safe_score(model)) for model in weapons]
            rows.sort(key=lambda x: (float("-inf") if _is_nan(x[1]) else x[1]), reverse=True)

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
                f"Confronto Punteggio Armi — {category}\nFunzione: get_weapon_score()",
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

    print(f"[PDF] weapon_score → {output_path}")


def save_weapon_score_target_pdf(
    weapon_type_list: List[str],
    target_type_list: List[str],
    target_dimension_list: List[str],
    output_path: str,
) -> None:
    """
    Salva un PDF con una pagina per categoria.
    Ogni pagina: tabella get_weapon_score_target() con colonne per ogni
    combinazione (target_type × target_dimension), con colorazione heatmap.
    """
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
            weapons = AIR_WEAPONS.get(category, {})
            if not weapons:
                continue

            models = list(weapons.keys())
            col_labels = ["Weapon Model"] + [f"{t}\n{d}" for t, d in combinations]
            n_data_cols = len(combinations)
            n_cols_total = 1 + n_data_cols

            cell_text, score_matrix = [], []
            for model in models:
                row_scores = [_safe_score_target(model, t, d) for t, d in combinations]
                score_matrix.append(row_scores)
                cell_text.append(
                    [model] + [f"{s:.4f}" if not _is_nan(s) else "N/A" for s in row_scores]
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

            fig_w = max(12, 1.9 * n_cols_total)
            fig_h = max(4.0, 0.42 * len(models) + 2.5)
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

    print(f"[PDF] weapon_score_target → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def _run_tests() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        TestGetWeapon,
        TestIsWeaponType,
        TestGetWeaponTypeScores,
        TestGetWeaponScore,
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
        os.path.join(OUTPUT_DIR, "weapon_score_tables.pdf"),
    )
    save_weapon_score_target_pdf(
        WEAPON_TYPE_TARGET,
        TARGET_TYPE,
        TARGET_DIMENSION,
        os.path.join(OUTPUT_DIR, "weapon_score_target_tables.pdf"),
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
    print("║       Test_Aircraft_Weapon_Data  —  Menu principale         ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    for idx, (label, _) in enumerate(_MENU_ITEMS, start=1):
        print(f"║  {idx}.  {label:<55}║")
    print("╚══════════════════════════════════════════════════════════════╝")


def _ask_choice() -> int:
    """Chiede all'utente di selezionare una voce del menu; ritorna l'indice (1-based)."""
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

        if choice == 1:                          # test unitari
            test_result = _run_tests()

        elif choice == 2:                        # tabelle a terminale
            _run_tables_terminal()

        elif choice == 3:                        # tabelle PDF
            _run_tables_pdf()

        elif choice == 4:                        # test + terminale
            test_result = _run_tests()
            _run_tables_terminal()

        elif choice == 5:                        # test + PDF
            test_result = _run_tests()
            _run_tables_pdf()

        elif choice == 6:                        # terminale + PDF
            _run_tables_terminal()
            _run_tables_pdf()

        elif choice == 7:                        # tutto
            test_result = _run_tests()
            _run_tables_terminal()
            _run_tables_pdf()

        elif choice == 8:                        # esci
            print("Uscita.")
            break

        input("\nPremi INVIO per tornare al menu...")

    # codice di uscita basato sull'ultimo risultato dei test (se eseguiti)
    if test_result is not None:
        sys.exit(0 if test_result.wasSuccessful() else 1)


if __name__ == "__main__":
    _interactive_menu()
