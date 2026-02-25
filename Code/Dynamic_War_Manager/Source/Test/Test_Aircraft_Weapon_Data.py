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
      [CORRETTO: aggiunta inizializzazione `score = 0.0`]
  B3. get_weapon_score_target(): usava la lista `target_type` come chiave del
      dizionario efficiency invece della variabile di loop `t_type` → TypeError.
      [CORRETTO: sostituito con `.get(t_type, {})`]
  B4. get_weapon_score_target(): stessa issue con `target_dimension` vs `t_dim`.
      [CORRETTO: sostituito con `.get(t_dim, {})`]
  B6. TARGET_DIMENSION = ['small','medium','large'] non corrispondeva alle chiavi
      efficiency 'small'/'med'/'big' → validazione sempre falliva → ritornava 0.
      [CORRETTO: aggiornato a ['small','med','big']]
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
    WEAPON_PARAM,
    WARHEAD_TYPE_PARAM,
    WARHEAD_TYPE_TARGET_EFFECTIVENESS,
    TARGET_DIMENSION,
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

class TestAircraftWeaponsDataStructure(unittest.TestCase):
    """Verifica la correttezza strutturale dei dizionari AIR_WEAPONS,
    WEAPON_PARAM, WARHEAD_TYPE_PARAM, WARHEAD_TYPE_TARGET_EFFECTIVENESS
    e della costante TARGET_DIMENSION.

    Differenze strutturali rispetto a Ground_Weapon_Data:
    - Il dizionario principale è AIR_WEAPONS (non GROUND_WEAPONS).
    - I tipi di testata sono in WARHEAD_TYPE_PARAM (non AMMO_PARAM) e includono
      FRAG (assente in Ground).
    - L'efficacia testata/bersaglio è in WARHEAD_TYPE_TARGET_EFFECTIVENESS.
    - MISSILES_AAM NON ha il campo 'efficiency': il punteggio è calcolato
      esclusivamente dai parametri balistici via WEAPON_PARAM['MISSILES_AAM_RAD']
      e WEAPON_PARAM['MISSILES_AAM_INF'], sottocategorie interne al solo scoring.
    - Tutti gli AAM hanno il campo 'seeker' ('radar'/'infrared'); i missili SARH
      (AIM-7x) hanno active_range=None — Bug BM documentato e corretto.
    """

    # ── AIR_WEAPONS: struttura generale ─────────────────────────────────────

    def test_air_weapons_has_expected_categories(self):
        """AIR_WEAPONS deve contenere le 6 categorie attese."""
        expected = {
            "MISSILES_AAM", "MISSILES_ASM", "BOMBS",
            "ROCKETS", "CANNONS", "MACHINE_GUNS",
        }
        for cat in expected:
            with self.subTest(category=cat):
                self.assertIn(cat, AIR_WEAPONS)

    def test_all_categories_are_dicts(self):
        """Ogni categoria deve essere un dizionario."""
        for cat, content in AIR_WEAPONS.items():
            with self.subTest(category=cat):
                self.assertIsInstance(content, dict)

    def test_all_categories_are_non_empty(self):
        """Tutte le categorie devono contenere almeno un'arma."""
        for cat, content in AIR_WEAPONS.items():
            with self.subTest(category=cat):
                self.assertGreater(len(content), 0, f"Categoria '{cat}' è vuota")

    # ── AIR_WEAPONS: campi obbligatori per categoria ─────────────────────────

    def test_missiles_aam_weapon_has_common_fields(self):
        """Ogni AAM deve avere i campi comuni (model, type, warhead, range,
        max_speed, manouvrability, task). NON ha 'efficiency'."""
        required = {"model", "type", "warhead", "range", "max_speed", "manouvrability", "task"}
        for model, data in AIR_WEAPONS["MISSILES_AAM"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MISSILES_AAM/{model}")

    def test_missiles_asm_weapon_has_required_fields(self):
        """Ogni ASM deve avere model, type, warhead, range, efficiency, task."""
        required = {"model", "type", "warhead", "range", "efficiency", "task"}
        for model, data in AIR_WEAPONS["MISSILES_ASM"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MISSILES_ASM/{model}")

    def test_bombs_weapon_has_required_fields(self):
        """Ogni bomba deve avere model, type, efficiency, task; e 'warhead' OPPURE
        'weight' (le cluster bomb usano 'weight' invece di 'warhead')."""
        common = {"model", "type", "efficiency", "task"}
        for model, data in AIR_WEAPONS["BOMBS"].items():
            with self.subTest(model=model):
                for field in common:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in BOMBS/{model}")
                self.assertTrue(
                    "warhead" in data or "weight" in data,
                    f"Nessun campo 'warhead' né 'weight' in BOMBS/{model}",
                )

    def test_rockets_weapon_has_required_fields(self):
        """Ogni razzo deve avere model, type, caliber, warhead, warhead_type,
        range, speed, efficiency."""
        required = {"model", "type", "caliber", "warhead", "warhead_type",
                    "range", "speed", "efficiency"}
        for model, data in AIR_WEAPONS["ROCKETS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in ROCKETS/{model}")

    def test_cannons_weapon_has_required_fields(self):
        """Ogni cannone deve avere model, type, caliber, fire_rate, range, efficiency."""
        required = {"model", "type", "caliber", "fire_rate", "range", "efficiency"}
        for model, data in AIR_WEAPONS["CANNONS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in CANNONS/{model}")

    def test_machine_guns_weapon_has_required_fields(self):
        """Ogni mitragliatrice deve avere model, type, caliber, fire_rate, range,
        efficiency."""
        required = {"model", "type", "caliber", "fire_rate", "range", "efficiency"}
        for model, data in AIR_WEAPONS["MACHINE_GUNS"].items():
            with self.subTest(model=model):
                for field in required:
                    self.assertIn(field, data,
                                  f"Campo '{field}' mancante in MACHINE_GUNS/{model}")

    # ── MISSILES_AAM: struttura specifica ────────────────────────────────────

    def test_aam_weapons_have_no_efficiency_field(self):
        """Gli AAM non devono avere il campo 'efficiency': il loro punteggio è
        calcolato esclusivamente dai parametri balistici (warhead, range,
        max_speed, manouvrability, ...) tramite WEAPON_PARAM['MISSILES_AAM_RAD/INF']."""
        for model, data in AIR_WEAPONS["MISSILES_AAM"].items():
            with self.subTest(model=model):
                self.assertNotIn(
                    "efficiency", data,
                    f"MISSILES_AAM/{model} NON dovrebbe avere 'efficiency'",
                )

    def test_aam_weapons_have_seeker_field(self):
        """Tutti gli AAM devono avere il campo 'seeker'."""
        for model, data in AIR_WEAPONS["MISSILES_AAM"].items():
            with self.subTest(model=model):
                self.assertIn("seeker", data,
                              f"Campo 'seeker' mancante in MISSILES_AAM/{model}")

    def test_aam_seeker_values_are_valid(self):
        """Il campo 'seeker' deve essere 'radar' o 'infrared' per tutti gli AAM."""
        valid_seekers = {"radar", "infrared"}
        for model, data in AIR_WEAPONS["MISSILES_AAM"].items():
            with self.subTest(model=model):
                self.assertIn(
                    data.get("seeker"), valid_seekers,
                    f"Seeker non valido per {model}: {data.get('seeker')!r}",
                )

    def test_aim54c_mk47_is_radar_with_positive_active_range(self):
        """AIM-54C-MK47 (Phoenix active radar) deve avere seeker='radar' e
        active_range > 0."""
        data = AIR_WEAPONS["MISSILES_AAM"]["AIM-54C-MK47"]
        self.assertEqual(data.get("seeker"), "radar")
        self.assertIsNotNone(data.get("active_range"))
        self.assertGreater(data["active_range"], 0)

    def test_aim9l_is_infrared(self):
        """AIM-9L (Sidewinder IR) deve avere seeker='infrared'."""
        data = AIR_WEAPONS["MISSILES_AAM"]["AIM-9L"]
        self.assertEqual(data.get("seeker"), "infrared")

    def test_aim7_sarh_active_range_is_none_documented(self):
        """Bug BM documentato: i missili AIM-7 (SARH) non hanno guida attiva
        terminale e hanno active_range=None. Questo causava TypeError in
        get_missiles_score() per l'accesso diretto weapon['active_range'].
        [CORRETTO: sostituito con weapon.get(param_name) or 0.0]"""
        sarh_models = ["AIM-7E", "AIM-7F", "AIM-7M", "AIM-7MH", "AIM-7P"]
        for model in sarh_models:
            with self.subTest(model=model):
                data = AIR_WEAPONS["MISSILES_AAM"][model]
                self.assertIsNone(
                    data.get("active_range"),
                    f"{model} dovrebbe avere active_range=None (SARH puro, nessun terminale attivo)",
                )

    def test_aam_warhead_positive(self):
        """Il warhead deve essere > 0 per tutti gli AAM."""
        for model, data in AIR_WEAPONS["MISSILES_AAM"].items():
            with self.subTest(model=model):
                self.assertIsInstance(data["warhead"], (int, float))
                self.assertGreater(data["warhead"], 0)

    def test_aam_range_positive(self):
        """La gittata massima deve essere > 0 per tutti gli AAM."""
        for model, data in AIR_WEAPONS["MISSILES_AAM"].items():
            with self.subTest(model=model):
                self.assertIsInstance(data["range"], (int, float))
                self.assertGreater(data["range"], 0)

    # ── efficiency: struttura ────────────────────────────────────────────────

    def test_non_aam_weapons_have_efficiency_field(self):
        """Tutte le categorie non-AAM devono avere 'efficiency' in ogni arma."""
        for cat in ("MISSILES_ASM", "BOMBS", "ROCKETS", "CANNONS", "MACHINE_GUNS"):
            for model, data in AIR_WEAPONS[cat].items():
                with self.subTest(category=cat, model=model):
                    self.assertIn(
                        "efficiency", data,
                        f"Campo 'efficiency' mancante in {cat}/{model}",
                    )

    def test_efficiency_structure_has_all_standard_target_types(self):
        """Per le armi a impiego generale (ROCKETS, CANNONS, MACHINE_GUNS)
        l'efficiency deve coprire tutti gli 11 target type standard.
        MISSILES_ASM e BOMBS sono escluse: le armi specializzate (anti-nave,
        ARM, cluster) coprono solo i target rilevanti per la loro missione."""
        expected_types = {
            "Soft", "Armored", "Hard", "Structure", "Air_Defense",
            "Airbase", "Port", "Shipyard", "Farp", "Stronghold", "ship",
        }
        for cat in ("ROCKETS", "CANNONS", "MACHINE_GUNS"):
            for model, data in AIR_WEAPONS[cat].items():
                eff = data.get("efficiency", {})
                for t in expected_types:
                    with self.subTest(category=cat, model=model, target=t):
                        self.assertIn(
                            t, eff,
                            f"Target '{t}' mancante in efficiency di {cat}/{model}",
                        )

    def test_missiles_asm_efficiency_is_non_empty(self):
        """Tutti i MISSILES_ASM devono avere un efficiency dict non vuoto,
        anche se specializzato per un sottoinsieme di target."""
        for model, data in AIR_WEAPONS["MISSILES_ASM"].items():
            with self.subTest(model=model):
                eff = data.get("efficiency", {})
                self.assertGreater(
                    len(eff), 0,
                    f"efficiency vuota in MISSILES_ASM/{model}",
                )

    def test_asm_antiship_efficiency_covers_ship_target(self):
        """I missili anti-nave (RB-15F, AGM-84A, Kormoran, RB-04E, Sea Eagle,
        Kh-22N) devono avere 'ship' come target type nella loro efficiency."""
        antiship_models = ["RB-15F", "AGM-84A", "Kormoran", "RB-04E", "Sea Eagle", "Kh-22N"]
        for model in antiship_models:
            with self.subTest(model=model):
                eff = AIR_WEAPONS["MISSILES_ASM"][model].get("efficiency", {})
                self.assertIn("ship", eff,
                              f"Missile anti-nave {model}: 'ship' mancante in efficiency")

    def test_asm_arm_efficiency_covers_air_defense_target(self):
        """I missili anti-radiazione (AGM-45, AGM-88, Kh-58, Kh-25MP, Kh-25MPU)
        devono avere 'Air_Defense' come target type nella loro efficiency."""
        arm_models = ["AGM-45", "AGM-88", "Kh-58", "Kh-25MP", "Kh-25MPU"]
        for model in arm_models:
            with self.subTest(model=model):
                eff = AIR_WEAPONS["MISSILES_ASM"][model].get("efficiency", {})
                self.assertIn("Air_Defense", eff,
                              f"Missile ARM {model}: 'Air_Defense' mancante in efficiency")

    def test_cluster_bombs_efficiency_covers_area_targets(self):
        """Le cluster bomb (Mk-20, CBU-52B, BLG66, BK-90MJ1, RBK-*, KGBU-*)
        devono coprire i target di area (Soft, Armored, Air_Defense)."""
        cluster_models = [
            "Mk-20", "CBU-52B", "BLG66", "BK-90MJ1", "BK-90MJ1-2", "BK-90MJ2",
            "RBK-250AO", "RBK-500AO", "RBK-500PTAB",
            "KGBU-2AO", "KGBU-2PTAB", "KGBU-96r",
        ]
        area_targets = {"Soft", "Armored", "Air_Defense"}
        for model in cluster_models:
            with self.subTest(model=model):
                eff = AIR_WEAPONS["BOMBS"][model].get("efficiency", {})
                for t in area_targets:
                    self.assertIn(t, eff,
                                  f"Cluster bomb {model}: target '{t}' mancante in efficiency")

    def test_efficiency_dims_have_accuracy_and_destroy_capacity(self):
        """Ogni cella (target_type, dim) nell'efficiency deve contenere
        'accuracy' e 'destroy_capacity'."""
        for cat in ("ROCKETS", "CANNONS", "MACHINE_GUNS"):
            first_model = next(iter(AIR_WEAPONS[cat]))
            eff = AIR_WEAPONS[cat][first_model]["efficiency"]
            for t_type, t_data in eff.items():
                for dim in ("big", "med", "small"):
                    cell = t_data.get(dim, {})
                    with self.subTest(cat=cat, model=first_model, target=t_type, dim=dim):
                        self.assertIn("accuracy", cell)
                        self.assertIn("destroy_capacity", cell)

    def test_efficiency_accuracy_in_range_0_to_1(self):
        """accuracy deve essere in [0, 1] per ogni cella efficiency."""
        for cat in ("MISSILES_ASM", "ROCKETS", "CANNONS", "MACHINE_GUNS"):
            first_model = next(iter(AIR_WEAPONS[cat]))
            eff = AIR_WEAPONS[cat][first_model]["efficiency"]
            for t_type, t_data in eff.items():
                for dim in ("big", "med", "small"):
                    cell = t_data.get(dim, {})
                    acc = cell.get("accuracy")
                    if acc is not None:
                        with self.subTest(cat=cat, model=first_model, t=t_type, dim=dim):
                            self.assertGreaterEqual(acc, 0.0)
                            self.assertLessEqual(acc, 1.0)

    def test_efficiency_destroy_capacity_non_negative(self):
        """destroy_capacity deve essere >= 0 (vicino allo zero per infrastrutture)."""
        for cat in ("CANNONS", "MACHINE_GUNS"):
            first_model = next(iter(AIR_WEAPONS[cat]))
            eff = AIR_WEAPONS[cat][first_model]["efficiency"]
            for t_type, t_data in eff.items():
                for dim in ("big", "med", "small"):
                    cell = t_data.get(dim, {})
                    dc = cell.get("destroy_capacity")
                    if dc is not None:
                        with self.subTest(cat=cat, model=first_model, t=t_type, dim=dim):
                            self.assertGreaterEqual(dc, 0.0)

    def test_caliber_positive_for_cannons(self):
        """Il calibro deve essere > 0 per tutti i cannoni."""
        for model, data in AIR_WEAPONS["CANNONS"].items():
            with self.subTest(model=model):
                self.assertGreater(data["caliber"], 0)

    def test_caliber_positive_for_rockets(self):
        """Il calibro deve essere > 0 per tutti i razzi."""
        for model, data in AIR_WEAPONS["ROCKETS"].items():
            with self.subTest(model=model):
                self.assertGreater(data["caliber"], 0)

    def test_perc_efficiency_variability_in_range(self):
        """perc_efficiency_variability deve essere in [0, 1] per tutte le armi
        non-AAM che lo definiscono."""
        for cat in ("MISSILES_ASM", "BOMBS", "ROCKETS", "CANNONS", "MACHINE_GUNS"):
            for model, data in AIR_WEAPONS[cat].items():
                pev = data.get("perc_efficiency_variability")
                if pev is not None:
                    with self.subTest(cat=cat, model=model):
                        self.assertGreaterEqual(pev, 0.0)
                        self.assertLessEqual(pev, 1.0)

    # ── WEAPON_PARAM ─────────────────────────────────────────────────────────

    def test_weapon_param_has_expected_keys(self):
        """WEAPON_PARAM deve contenere: CANNONS, MISSILES_AAM_RAD, MISSILES_AAM_INF,
        MISSILES_ASM, ROCKETS, MACHINE_GUNS, BOMBS."""
        expected = {
            "CANNONS", "MISSILES_AAM_RAD", "MISSILES_AAM_INF",
            "MISSILES_ASM", "ROCKETS", "MACHINE_GUNS", "BOMBS",
        }
        for key in expected:
            with self.subTest(key=key):
                self.assertIn(key, WEAPON_PARAM)

    def test_weapon_param_does_not_have_missiles_aam_key(self):
        """WEAPON_PARAM usa sottocategorie interne MISSILES_AAM_RAD/INF per il
        calcolo del punteggio; la chiave generica 'MISSILES_AAM' (uguale ai
        tasti di AIR_WEAPONS) non deve essere presente direttamente."""
        self.assertNotIn("MISSILES_AAM", WEAPON_PARAM)

    def test_weapon_param_coefficients_positive(self):
        """Tutti i coefficienti in WEAPON_PARAM devono essere float > 0."""
        for cat, params in WEAPON_PARAM.items():
            for param, coeff in params.items():
                with self.subTest(category=cat, param=param):
                    self.assertIsInstance(coeff, float)
                    self.assertGreater(coeff, 0.0)

    def test_weapon_param_cannons_has_expected_keys(self):
        """WEAPON_PARAM['CANNONS'] deve avere: caliber, speed, fire_rate, range."""
        expected = {"caliber", "speed", "fire_rate", "range"}
        self.assertEqual(set(WEAPON_PARAM["CANNONS"].keys()), expected)

    def test_weapon_param_rockets_has_expected_keys(self):
        """WEAPON_PARAM['ROCKETS'] deve avere: caliber, warhead, range,
        warhead_type, speed."""
        expected = {"caliber", "warhead", "range", "warhead_type", "speed"}
        self.assertEqual(set(WEAPON_PARAM["ROCKETS"].keys()), expected)

    def test_weapon_param_machine_guns_has_expected_keys(self):
        """WEAPON_PARAM['MACHINE_GUNS'] deve avere: caliber, fire_rate, range."""
        expected = {"caliber", "fire_rate", "range"}
        self.assertEqual(set(WEAPON_PARAM["MACHINE_GUNS"].keys()), expected)

    def test_weapon_param_missiles_asm_has_expected_keys(self):
        """WEAPON_PARAM['MISSILES_ASM'] deve avere: warhead, range, max_speed."""
        expected = {"warhead", "range", "max_speed"}
        self.assertEqual(set(WEAPON_PARAM["MISSILES_ASM"].keys()), expected)

    def test_weapon_param_aam_rad_has_active_range_key(self):
        """WEAPON_PARAM['MISSILES_AAM_RAD'] deve avere 'active_range' (per i
        missili radar con guida attiva terminale)."""
        self.assertIn("active_range", WEAPON_PARAM["MISSILES_AAM_RAD"])

    def test_weapon_param_aam_rad_has_semiactive_range_key(self):
        """WEAPON_PARAM['MISSILES_AAM_RAD'] deve avere 'semiactive_range' (per
        i missili SARH e BVR semiattivi)."""
        self.assertIn("semiactive_range", WEAPON_PARAM["MISSILES_AAM_RAD"])

    def test_weapon_param_bombs_has_warhead_and_weight(self):
        """WEAPON_PARAM['BOMBS'] deve avere sia 'warhead' che 'weight': le bombe
        convenzionali usano 'warhead', quelle a submunizioni usano 'weight'."""
        self.assertIn("warhead", WEAPON_PARAM["BOMBS"])
        self.assertIn("weight", WEAPON_PARAM["BOMBS"])

    # ── WARHEAD_TYPE_PARAM ───────────────────────────────────────────────────

    def test_warhead_type_param_has_expected_types(self):
        """WARHEAD_TYPE_PARAM deve contenere: HE, HEAT, AP, 2HEAT, APFSDS, FRAG."""
        expected = {"HE", "HEAT", "AP", "2HEAT", "APFSDS", "FRAG"}
        for t in expected:
            with self.subTest(warhead=t):
                self.assertIn(t, WARHEAD_TYPE_PARAM)

    def test_warhead_type_param_values_in_range(self):
        """Tutti i valori di WARHEAD_TYPE_PARAM devono essere float in (0, 1]."""
        for wt, val in WARHEAD_TYPE_PARAM.items():
            with self.subTest(warhead=wt):
                self.assertIsInstance(val, float)
                self.assertGreater(val, 0.0)
                self.assertLessEqual(val, 1.0)

    def test_2heat_highest_in_warhead_type_param(self):
        """2HEAT (carica cava doppia) deve avere il valore più alto in
        WARHEAD_TYPE_PARAM."""
        self.assertEqual(max(WARHEAD_TYPE_PARAM, key=WARHEAD_TYPE_PARAM.get), "2HEAT")

    def test_frag_present_in_warhead_type_param(self):
        """FRAG deve essere presente in WARHEAD_TYPE_PARAM.
        Differenza rispetto a Ground_Weapon_Data: in quest'ultimo modulo FRAG
        è solo in AMMO_TARGET_EFFECTIVENESS ma non in AMMO_PARAM."""
        self.assertIn("FRAG", WARHEAD_TYPE_PARAM)

    # ── WARHEAD_TYPE_TARGET_EFFECTIVENESS ────────────────────────────────────

    def test_warhead_target_effectiveness_has_all_warhead_types(self):
        """WARHEAD_TYPE_TARGET_EFFECTIVENESS deve contenere tutti i tipi
        di WARHEAD_TYPE_PARAM."""
        for wt in WARHEAD_TYPE_PARAM:
            with self.subTest(warhead=wt):
                self.assertIn(wt, WARHEAD_TYPE_TARGET_EFFECTIVENESS)

    def test_warhead_target_effectiveness_values_in_range(self):
        """Tutti i valori di efficacia devono essere float in [0, 1]."""
        for wt, targets in WARHEAD_TYPE_TARGET_EFFECTIVENESS.items():
            for t_type, val in targets.items():
                with self.subTest(warhead=wt, target=t_type):
                    self.assertIsInstance(val, float)
                    self.assertGreaterEqual(val, 0.0)
                    self.assertLessEqual(val, 1.0)

    def test_he_effectiveness_vs_soft_is_max(self):
        """HE deve avere efficacia 1.0 contro Soft (massimo valore della riga)."""
        self.assertAlmostEqual(
            WARHEAD_TYPE_TARGET_EFFECTIVENESS["HE"]["Soft"], 1.0
        )

    def test_apfsds_effectiveness_vs_armored_high(self):
        """APFSDS deve avere alta efficacia (>= 0.9) contro Armored."""
        self.assertGreaterEqual(
            WARHEAD_TYPE_TARGET_EFFECTIVENESS["APFSDS"]["Armored"], 0.9
        )

    def test_frag_effectiveness_vs_soft_high(self):
        """FRAG deve avere alta efficacia (>= 0.8) contro Soft."""
        self.assertGreaterEqual(
            WARHEAD_TYPE_TARGET_EFFECTIVENESS["FRAG"]["Soft"], 0.8
        )

    def test_all_warhead_types_cover_standard_target_types(self):
        """Ogni tipo di testata in WARHEAD_TYPE_TARGET_EFFECTIVENESS deve coprire
        tutti i target type standard."""
        expected_targets = {
            "Soft", "Armored", "Hard", "Structure", "Air_Defense",
            "Airbase", "Port", "Shipyard", "Farp", "Stronghold", "ship",
        }
        for wt, targets in WARHEAD_TYPE_TARGET_EFFECTIVENESS.items():
            for t in expected_targets:
                with self.subTest(warhead=wt, target=t):
                    self.assertIn(
                        t, targets,
                        f"Target '{t}' mancante in WARHEAD_TYPE_TARGET_EFFECTIVENESS['{wt}']",
                    )

    # ── TARGET_DIMENSION ─────────────────────────────────────────────────────

    def test_target_dimension_contains_correct_keys(self):
        """TARGET_DIMENSION deve contenere 'small', 'med', 'big'."""
        for key in ("small", "med", "big"):
            with self.subTest(key=key):
                self.assertIn(key, TARGET_DIMENSION)

    def test_target_dimension_does_not_contain_medium_or_large(self):
        """TARGET_DIMENSION NON deve contenere 'medium' o 'large' (Bug B6 corretto):
        le chiavi nelle efficiency template sono 'med' e 'big', non le forme estese.
        Prima della correzione TARGET_DIMENSION = ['small','medium','large'] causava
        la validazione fallita e il ritorno sistematico di 0 in get_weapon_score_target()."""
        self.assertNotIn("medium", TARGET_DIMENSION)
        self.assertNotIn("large", TARGET_DIMENSION)

    def test_efficiency_uses_target_dimension_as_keys(self):
        """Le chiavi di TARGET_DIMENSION ('big','med','small') devono corrispondere
        alle chiavi usate nelle efficiency template delle armi non-AAM."""
        first_cannon = next(iter(AIR_WEAPONS["CANNONS"]))
        eff = AIR_WEAPONS["CANNONS"][first_cannon]["efficiency"]
        for t_type, t_data in eff.items():
            for dim in TARGET_DIMENSION:
                with self.subTest(target=t_type, dim=dim):
                    self.assertIn(
                        dim, t_data,
                        f"Dimensione '{dim}' di TARGET_DIMENSION non trovata "
                        f"in efficiency di CANNONS/{first_cannon}/{t_type}",
                    )


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

    Bug corretti:
      B2. `score` non inizializzata → inizializzata a 0.0 prima del loop.
      B3. `weapon.get('efficiency').get(target_type)` usava la lista target_type
          invece della variabile t_type → corretto in .get(t_type, {}).
      B4. Stessa correzione per target_dimension → .get(t_dim, {}).
      B6. TARGET_DIMENSION era ['small','medium','large'] mentre le chiavi
          efficiency sono 'small'/'med'/'big' → corretto in ['small','med','big'].
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

    def test_target_dim_big_valid(self):
        """
        Bug B6 corretto: "big" è ora in TARGET_DIMENSION = ['small','med','big'] →
        il loop elabora la dimensione e restituisce un punteggio >= 0.
        """
        score = get_weapon_score_target("RB-05A", ["Soft"], ["big"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_target_dim_med_valid(self):
        """Bug B6 corretto: "med" è ora in TARGET_DIMENSION → punteggio >= 0."""
        score = get_weapon_score_target("RB-05A", ["Soft"], ["med"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_unknown_model_returns_zero(self):
        """Arma sconosciuta → get_weapon restituisce None → 0.0."""
        self.assertEqual(
            get_weapon_score_target("WEAPON_NOT_EXISTING_XYZ", ["Soft"], ["small"]), 0.0
        )

    # ── test post-correzione B2/B3/B4 ────────────────────────────
    def test_valid_asm_valid_target_returns_score(self):
        """
        Bug B2/B3/B4 corretti: get_weapon_score_target su un ASM con target
        valido deve restituire un float >= 0 senza eccezioni.
        """
        score = get_weapon_score_target("RB-05A", ["Soft"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_valid_cannon_valid_target_returns_score(self):
        """Bug B2/B3/B4 corretti: stesso test per un cannone."""
        score = get_weapon_score_target("UPK-23", ["Armored"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_valid_bomb_valid_target_returns_score(self):
        """Bug B2/B3/B4 corretti: stesso test per una bomba."""
        score = get_weapon_score_target("Mk-84", ["Soft"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_valid_rocket_valid_target_returns_score(self):
        """Bug B2/B3/B4 corretti: stesso test per un razzo."""
        score = get_weapon_score_target("Zuni-Mk71", ["Soft"], ["small"])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

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
        TestAircraftWeaponsDataStructure,
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
