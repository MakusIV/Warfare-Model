'''
Ship_Weapon_Data.py
===================
Dati e funzioni di scoring per le armi navali imbarcate.

Struttura analoga a Ground_Weapon_Data.py, adattata per le cinque categorie
di armamento navale presenti nei dizionari `weapons` delle navi in Ship_Data.py:

    MISSILES_SAM   — missili superficie-aria (SAM)
    MISSILES_ASM   — missili anti-nave / crociera (ASM)
    MISSILES_TORPEDO — siluri
    GUNS           — cannoni navali
    CIWS           — sistemi d'arma ravvicinati (Close-In Weapon System)

API pubblica:
    get_ship_weapon(model)                            → Dict | None
    get_weapon_score(weapon_type, weapon_model)       → float
    get_weapon_score_target(model, t_type, t_dim)     → float  (List-based)
    get_weapon_score_target_distribuition(model, ...) → float  (Dict-based)
'''

import random
import sys
from typing import Optional, List, Dict, Any

from Code.Dynamic_War_Manager.Source.Context.Context import TARGET_CLASSIFICATION
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# ── LOGGING ───────────────────────────────────────────────────────────────────

logger = Logger(module_name=__name__, class_name='Ship_Weapon_Data').logger

# ── COSTANTI ──────────────────────────────────────────────────────────────────

TARGET_DIMENSION = ['small', 'med', 'big']
TARGET_CLASSIFICATION = TARGET_CLASSIFICATION.keys()

_INFRA_MIN = sys.float_info.min   # capacità di distruzione quasi nulla per infrastrutture

# Parametri di valutazione per categoria (coeff / valore_max)
# Usato nelle funzioni get_<categoria>_score
WEAPON_PARAM: Dict[str, Dict[str, float]] = {

    'MISSILES_SAM': {
        'caliber':  0.15 / 530,    # mm — max ≈ S-300F (508 mm); lieve proxy per testata
        'warhead':  0.25 / 145,    # kg — max ≈ S-300F = 145 kg
        'range':    0.40 / 250,    # km — max ≈ SM-2ER = 240 km
        'speed':    0.20 / 2040,   # m/s — max ≈ S-300F Mach 6 ≈ 2040 m/s
    },

    'MISSILES_ASM': {
        'caliber':  0.10 / 880,    # mm — max ≈ P-1000 Vulkan = 880 mm
        'warhead':  0.35 / 750,    # kg — max ≈ P-700 Granit = 750 kg
        'range':    0.35 / 1600,   # km — max ≈ Tomahawk Block IV = 1600 km
        'speed':    0.20 / 1020,   # m/s — max ≈ YJ-12 Mach 3 ≈ 1020 m/s
    },

    'MISSILES_TORPEDO': {
        'caliber':  0.15 / 533,    # mm — standard pesante = 533 mm
        'warhead':  0.45 / 290,    # kg — max ≈ Mk-48 = 290 kg
        'range':    0.20 / 50,     # km — max ≈ Mk-48 = 50 km
        'speed':    0.20 / 55,     # kt  — max ≈ Mk-48 = 55 kt
    },

    'GUNS': {
        'caliber':      0.30 / 130,   # mm — max ≈ AK-130 = 130 mm
        'muzzle_speed': 0.15 / 980,   # m/s — max ≈ AK-176 = 980 m/s
        'fire_rate':    0.25 / 120,   # rpm — max ≈ OTO-Melara 76/62 = 120 rpm
        'range':        0.30 / 25,    # km  — max ≈ AK-130 = 25 km
    },

    'CIWS': {
        'caliber':   0.20 / 30,     # mm — max ≈ AK-630 / Type-730 = 30 mm
        'fire_rate': 0.50 / 5800,   # rpm — max ≈ Type-730 = 5800 rpm
        'range':     0.30 / 4.0,    # km  — max ≈ AK-630 = 4 km
    },
}

# ── TEMPLATE DI EFFICIENZA ────────────────────────────────────────────────────
#
# Struttura analoga a Ground_Weapon_Data: per ogni tipo di bersaglio (TARGET_CLASSIFICATION)
# e per ogni dimensione (big / med / small) → {accuracy, destroy_capacity}.
#
# NOTA: i SAM e i CIWS sono sistemi anti-aerei; le loro efficacy contro bersagli
# superficiali e navali sono quindi molto ridotte (come i _EFF_SAM_* terrestri).
# I siluri non hanno capacità contro bersagli a terra.

# ── SAM a corto raggio (SA-N-4, SA-N-9, HHQ-7, RIM-7M-Sea-Sparrow) ──────────
_EFF_SAM_SHORAD = {
    "Soft":        {"big": {"accuracy": 0.10, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.08, "destroy_capacity": 0.10},
                    "small": {"accuracy": 0.06, "destroy_capacity": 0.12}},
    "Armored":     {"big": {"accuracy": 0.05, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.04, "destroy_capacity": 0.03},
                    "small": {"accuracy": 0.03, "destroy_capacity": 0.04}},
    "Hard":        {"big": {"accuracy": 0.05, "destroy_capacity": 0.01},
                    "med": {"accuracy": 0.04, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.03, "destroy_capacity": 0.02}},
    "Structure":   {"big": {"accuracy": 0.05, "destroy_capacity": 0.005},
                    "med": {"accuracy": 0.04, "destroy_capacity": 0.008},
                    "small": {"accuracy": 0.03, "destroy_capacity": 0.01}},
    "Air_Defense": {"big": {"accuracy": 0.08, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.06}},
    "Airbase":     {"big": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.05, "destroy_capacity": 1e-9}},
    "Port":        {"big": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.05, "destroy_capacity": 1e-9}},
    "Shipyard":    {"big": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.05, "destroy_capacity": 1e-9}},
    "Farp":        {"big": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.05, "destroy_capacity": 1e-9}},
    "Stronghold":  {"big": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.05, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.05, "destroy_capacity": 1e-9}},
    "ship":        {"big": {"accuracy": 0.05, "destroy_capacity": 0.03},
                    "med": {"accuracy": 0.04, "destroy_capacity": 0.04},
                    "small": {"accuracy": 0.03, "destroy_capacity": 0.05}},
}

# ── SAM a medio raggio (RIM-162-ESSM, RIM-66-SM-1, HHQ-16, URK-5-Rastrub) ───
_EFF_SAM_MERAD = {
    "Soft":        {"big": {"accuracy": 0.12, "destroy_capacity": 0.10},
                    "med": {"accuracy": 0.10, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.08, "destroy_capacity": 0.15}},
    "Armored":     {"big": {"accuracy": 0.06, "destroy_capacity": 0.03},
                    "med": {"accuracy": 0.05, "destroy_capacity": 0.04},
                    "small": {"accuracy": 0.04, "destroy_capacity": 0.05}},
    "Hard":        {"big": {"accuracy": 0.06, "destroy_capacity": 0.01},
                    "med": {"accuracy": 0.05, "destroy_capacity": 0.02},
                    "small": {"accuracy": 0.04, "destroy_capacity": 0.03}},
    "Structure":   {"big": {"accuracy": 0.06, "destroy_capacity": 0.006},
                    "med": {"accuracy": 0.05, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.04, "destroy_capacity": 0.015}},
    "Air_Defense": {"big": {"accuracy": 0.10, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.08, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.06, "destroy_capacity": 0.10}},
    "Airbase":     {"big": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.06, "destroy_capacity": 1e-9}},
    "Port":        {"big": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.06, "destroy_capacity": 1e-9}},
    "Shipyard":    {"big": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.06, "destroy_capacity": 1e-9}},
    "Farp":        {"big": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.06, "destroy_capacity": 1e-9}},
    "Stronghold":  {"big": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.06, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.06, "destroy_capacity": 1e-9}},
    "ship":        {"big": {"accuracy": 0.08, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.08}},
}

# ── SAM a lungo raggio (RIM-66-SM-2, RIM-156-SM-2ER, S-300F, HHQ-9) ─────────
_EFF_SAM_LORAD = {
    "Soft":        {"big": {"accuracy": 0.15, "destroy_capacity": 0.12},
                    "med": {"accuracy": 0.12, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.10, "destroy_capacity": 0.18}},
    "Armored":     {"big": {"accuracy": 0.08, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.06}},
    "Hard":        {"big": {"accuracy": 0.08, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.03},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.04}},
    "Structure":   {"big": {"accuracy": 0.08, "destroy_capacity": 0.008},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.012},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.018}},
    "Air_Defense": {"big": {"accuracy": 0.12, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.10, "destroy_capacity": 0.10},
                    "small": {"accuracy": 0.08, "destroy_capacity": 0.12}},
    "Airbase":     {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-9}},
    "Port":        {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-9}},
    "Shipyard":    {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-9}},
    "Farp":        {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-9}},
    "Stronghold":  {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-9}},
    "ship":        {"big": {"accuracy": 0.12, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.10, "destroy_capacity": 0.10},
                    "small": {"accuracy": 0.08, "destroy_capacity": 0.12}},
}

# ── ASM anti-nave subsonico (RGM-84-Harpoon, YJ-83) ──────────────────────────
# accuracy = alta vs ship (guidance radar marino), bassa vs terra (seeker non ottimizzato)
# destroy_capacity = fragilità del bersaglio una volta colpito:
#   Soft: bersagli non protetti → quasi certamente distrutti da 220 kg HE
#   Armored: un carro colpito da 220 kg è certamente distrutto (testata sproporzionata)
#   ship: compartimentazione + damage control → il singolo colpo spesso non affonda la nave
# Ordine atteso: Soft > Armored > ship > Structure > Hard
_EFF_ASM_ANTISHIP_SUBSONIC = {
    "Soft":        {"big": {"accuracy": 0.72, "destroy_capacity": 0.78},
                    "med": {"accuracy": 0.68, "destroy_capacity": 0.82},
                    "small": {"accuracy": 0.62, "destroy_capacity": 0.88}},
    "Armored":     {"big": {"accuracy": 0.52, "destroy_capacity": 0.72},
                    "med": {"accuracy": 0.48, "destroy_capacity": 0.78},
                    "small": {"accuracy": 0.42, "destroy_capacity": 0.84}},
    "Hard":        {"big": {"accuracy": 0.58, "destroy_capacity": 0.14},
                    "med": {"accuracy": 0.52, "destroy_capacity": 0.18},
                    "small": {"accuracy": 0.45, "destroy_capacity": 0.22}},
    "Structure":   {"big": {"accuracy": 0.65, "destroy_capacity": 0.40},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.46},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.54}},
    "Air_Defense": {"big": {"accuracy": 0.55, "destroy_capacity": 0.16},
                    "med": {"accuracy": 0.50, "destroy_capacity": 0.20},
                    "small": {"accuracy": 0.45, "destroy_capacity": 0.24}},
    "Airbase":     {"big": {"accuracy": 0.60, "destroy_capacity": 0.12},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.18}},
    "Port":        {"big": {"accuracy": 0.65, "destroy_capacity": 0.28},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.33},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.38}},
    "Shipyard":    {"big": {"accuracy": 0.65, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.30},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.35}},
    "Farp":        {"big": {"accuracy": 0.62, "destroy_capacity": 0.16},
                    "med": {"accuracy": 0.57, "destroy_capacity": 0.20},
                    "small": {"accuracy": 0.52, "destroy_capacity": 0.24}},
    "Stronghold":  {"big": {"accuracy": 0.62, "destroy_capacity": 0.20},
                    "med": {"accuracy": 0.57, "destroy_capacity": 0.24},
                    "small": {"accuracy": 0.52, "destroy_capacity": 0.28}},
    "ship":        {"big": {"accuracy": 0.80, "destroy_capacity": 0.30},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.40},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.52}},
}

# ── ASM crociera (BGM-109-Tomahawk) — attacco a terra prevalente ──────────────
_EFF_ASM_CRUISE_LANDATTACK = {
    "Soft":        {"big": {"accuracy": 0.90, "destroy_capacity": 0.60},
                    "med": {"accuracy": 0.88, "destroy_capacity": 0.68},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.75}},
    "Armored":     {"big": {"accuracy": 0.80, "destroy_capacity": 0.22},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.28},
                    "small": {"accuracy": 0.70, "destroy_capacity": 0.35}},
    "Hard":        {"big": {"accuracy": 0.85, "destroy_capacity": 0.38},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.78, "destroy_capacity": 0.52}},
    "Structure":   {"big": {"accuracy": 0.88, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.52},
                    "small": {"accuracy": 0.82, "destroy_capacity": 0.60}},
    "Air_Defense": {"big": {"accuracy": 0.85, "destroy_capacity": 0.32},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.38},
                    "small": {"accuracy": 0.78, "destroy_capacity": 0.44}},
    "Airbase":     {"big": {"accuracy": 0.88, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.40},
                    "small": {"accuracy": 0.82, "destroy_capacity": 0.45}},
    "Port":        {"big": {"accuracy": 0.88, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.50},
                    "small": {"accuracy": 0.82, "destroy_capacity": 0.55}},
    "Shipyard":    {"big": {"accuracy": 0.85, "destroy_capacity": 0.40},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.78, "destroy_capacity": 0.50}},
    "Farp":        {"big": {"accuracy": 0.85, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.40},
                    "small": {"accuracy": 0.78, "destroy_capacity": 0.45}},
    "Stronghold":  {"big": {"accuracy": 0.85, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.48},
                    "small": {"accuracy": 0.78, "destroy_capacity": 0.55}},
    "ship":        {"big": {"accuracy": 0.65, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.70, "destroy_capacity": 0.50},
                    "small": {"accuracy": 0.60, "destroy_capacity": 0.55}},
}

# ── ASM supersonico (P-270-Moskit, YJ-12, YJ-18) ─────────────────────────────
# Testata ~300-320 kg, Mach 2-3: la massa cinetica aggiuntiva aumenta dc vs tutti i target.
# Un veicolo corazzato colpito da 320 kg a Mach 2 è completamente distrutto.
# Le navi rimangono bersagli duri (compartimentazione, damage control).
# Ordine atteso: Soft > Armored > ship > Structure > Hard
_EFF_ASM_SUPERSONIC = {
    "Soft":        {"big": {"accuracy": 0.72, "destroy_capacity": 0.82},
                    "med": {"accuracy": 0.68, "destroy_capacity": 0.86},
                    "small": {"accuracy": 0.62, "destroy_capacity": 0.90}},
    "Armored":     {"big": {"accuracy": 0.55, "destroy_capacity": 0.78},
                    "med": {"accuracy": 0.50, "destroy_capacity": 0.84},
                    "small": {"accuracy": 0.44, "destroy_capacity": 0.90}},
    "Hard":        {"big": {"accuracy": 0.60, "destroy_capacity": 0.22},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.28},
                    "small": {"accuracy": 0.48, "destroy_capacity": 0.34}},
    "Structure":   {"big": {"accuracy": 0.68, "destroy_capacity": 0.46},
                    "med": {"accuracy": 0.62, "destroy_capacity": 0.54},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.62}},
    "Air_Defense": {"big": {"accuracy": 0.58, "destroy_capacity": 0.22},
                    "med": {"accuracy": 0.52, "destroy_capacity": 0.28},
                    "small": {"accuracy": 0.46, "destroy_capacity": 0.33}},
    "Airbase":     {"big": {"accuracy": 0.62, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.56, "destroy_capacity": 0.18},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.22}},
    "Port":        {"big": {"accuracy": 0.68, "destroy_capacity": 0.32},
                    "med": {"accuracy": 0.62, "destroy_capacity": 0.38},
                    "small": {"accuracy": 0.56, "destroy_capacity": 0.44}},
    "Shipyard":    {"big": {"accuracy": 0.66, "destroy_capacity": 0.28},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.34},
                    "small": {"accuracy": 0.54, "destroy_capacity": 0.40}},
    "Farp":        {"big": {"accuracy": 0.62, "destroy_capacity": 0.18},
                    "med": {"accuracy": 0.56, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.26}},
    "Stronghold":  {"big": {"accuracy": 0.64, "destroy_capacity": 0.22},
                    "med": {"accuracy": 0.58, "destroy_capacity": 0.28},
                    "small": {"accuracy": 0.52, "destroy_capacity": 0.33}},
    "ship":        {"big": {"accuracy": 0.82, "destroy_capacity": 0.32},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.42},
                    "small": {"accuracy": 0.78, "destroy_capacity": 0.55}},
}

# ── ASM supersonico pesante (P-700-Granit, P-1000-Vulkan) ────────────────────
# Testata 750 kg (P-700) / 1000 kg (P-1000): distruzione totale per veicoli corazzati
# se colpiti (dc quasi 1.0). Le navi grandi resistono meglio: la loro massa, la
# compartimentazione e il damage control limitano l'effetto del singolo colpo.
# L'alta accuracy vs ship è bilanciata da dc moderata (le navi sono progettate per survivere).
# Ordine atteso: Soft > Armored > ship > Structure > Hard
_EFF_ASM_SUPERSONIC_HEAVY = {
    "Soft":        {"big": {"accuracy": 0.75, "destroy_capacity": 0.88},
                    "med": {"accuracy": 0.70, "destroy_capacity": 0.90},
                    "small": {"accuracy": 0.65, "destroy_capacity": 0.92}},
    "Armored":     {"big": {"accuracy": 0.58, "destroy_capacity": 0.90},
                    "med": {"accuracy": 0.52, "destroy_capacity": 0.94},
                    "small": {"accuracy": 0.46, "destroy_capacity": 0.98}},
    "Hard":        {"big": {"accuracy": 0.65, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.58, "destroy_capacity": 0.42},
                    "small": {"accuracy": 0.52, "destroy_capacity": 0.48}},
    "Structure":   {"big": {"accuracy": 0.72, "destroy_capacity": 0.58},
                    "med": {"accuracy": 0.66, "destroy_capacity": 0.68},
                    "small": {"accuracy": 0.60, "destroy_capacity": 0.78}},
    "Air_Defense": {"big": {"accuracy": 0.62, "destroy_capacity": 0.30},
                    "med": {"accuracy": 0.56, "destroy_capacity": 0.36},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.42}},
    "Airbase":     {"big": {"accuracy": 0.68, "destroy_capacity": 0.22},
                    "med": {"accuracy": 0.62, "destroy_capacity": 0.26},
                    "small": {"accuracy": 0.56, "destroy_capacity": 0.30}},
    "Port":        {"big": {"accuracy": 0.72, "destroy_capacity": 0.48},
                    "med": {"accuracy": 0.66, "destroy_capacity": 0.55},
                    "small": {"accuracy": 0.60, "destroy_capacity": 0.62}},
    "Shipyard":    {"big": {"accuracy": 0.70, "destroy_capacity": 0.44},
                    "med": {"accuracy": 0.64, "destroy_capacity": 0.50},
                    "small": {"accuracy": 0.58, "destroy_capacity": 0.56}},
    "Farp":        {"big": {"accuracy": 0.66, "destroy_capacity": 0.26},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.30},
                    "small": {"accuracy": 0.54, "destroy_capacity": 0.35}},
    "Stronghold":  {"big": {"accuracy": 0.68, "destroy_capacity": 0.32},
                    "med": {"accuracy": 0.62, "destroy_capacity": 0.38},
                    "small": {"accuracy": 0.56, "destroy_capacity": 0.44}},
    "ship":        {"big": {"accuracy": 0.85, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.57},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.72}},
}

# ── Siluro leggero anti-sommergibile (Mk-46) ──────────────────────────────────
# Progettato principalmente per attacchi anti-sub; efficacia ridotta vs navi di
# superficie e nulla vs bersagli a terra.
_EFF_TORPEDO_LIGHT = {
    "Soft":        {"big": {"accuracy": 0.02, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.02, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.02, "destroy_capacity": 0.0}},
    "Armored":     {"big": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.01, "destroy_capacity": 0.0}},
    "Hard":        {"big": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.01, "destroy_capacity": 0.0}},
    "Structure":   {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Air_Defense": {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Airbase":     {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Port":        {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Shipyard":    {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Farp":        {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Stronghold":  {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "ship":        {"big": {"accuracy": 0.65, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.70, "destroy_capacity": 0.50},
                    "small": {"accuracy": 0.70, "destroy_capacity": 0.55}},
}

# ── Siluro pesante (Mk-48, TEST-71, USET-80, Type-93) ────────────────────────
_EFF_TORPEDO_HEAVY = {
    "Soft":        {"big": {"accuracy": 0.02, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.02, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.02, "destroy_capacity": 0.0}},
    "Armored":     {"big": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.01, "destroy_capacity": 0.0}},
    "Hard":        {"big": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.01, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.01, "destroy_capacity": 0.0}},
    "Structure":   {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Air_Defense": {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Airbase":     {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Port":        {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Shipyard":    {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Farp":        {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "Stronghold":  {"big": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "med": {"accuracy": 0.0, "destroy_capacity": 0.0},
                    "small": {"accuracy": 0.0, "destroy_capacity": 0.0}},
    "ship":        {"big": {"accuracy": 0.78, "destroy_capacity": 0.75},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.80},
                    "small": {"accuracy": 0.80, "destroy_capacity": 0.85}},
}

# ── Cannone navale 76 mm (OTO-Melara 76/62, AK-176) ──────────────────────────
# Un proiettile HE/SAPOM da 76 mm colpisce bersagli a terra con buona precisione
# (fire support navale). Veicoli corazzati colpiti sono quasi certamente distrutti
# (destroy_capacity alta), le navi assorbono più colpi (dc moderata per il tipo di
# target). Ordine atteso: Soft > Armored > ship > Hard > Structure
_EFF_NAVAL_GUN_76MM = {
    "Soft":        {"big": {"accuracy": 0.85, "destroy_capacity": 0.40},
                    "med": {"accuracy": 0.82, "destroy_capacity": 0.50},
                    "small": {"accuracy": 0.80, "destroy_capacity": 0.60}},
    "Armored":     {"big": {"accuracy": 0.55, "destroy_capacity": 0.40},
                    "med": {"accuracy": 0.50, "destroy_capacity": 0.52},
                    "small": {"accuracy": 0.45, "destroy_capacity": 0.65}},
    "Hard":        {"big": {"accuracy": 0.60, "destroy_capacity": 0.03},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.07}},
    "Structure":   {"big": {"accuracy": 0.60, "destroy_capacity": 0.010},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.018},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.028}},
    "Air_Defense": {"big": {"accuracy": 0.55, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.50, "destroy_capacity": 0.10},
                    "small": {"accuracy": 0.45, "destroy_capacity": 0.13}},
    "Airbase":     {"big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8}},
    "Port":        {"big": {"accuracy": 0.58, "destroy_capacity": 0.03},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.52, "destroy_capacity": 0.07}},
    "Shipyard":    {"big": {"accuracy": 0.55, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.52, "destroy_capacity": 0.04},
                    "small": {"accuracy": 0.48, "destroy_capacity": 0.06}},
    "Farp":        {"big": {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.58, "destroy_capacity": 1e-8}},
    "Stronghold":  {"big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8}},
    "ship":        {"big": {"accuracy": 0.55, "destroy_capacity": 0.20},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.65, "destroy_capacity": 0.30}},
}

# ── Cannone navale 100 mm (AK-100, Type-79A) ──────────────────────────────────
# Ordine atteso: Soft > Armored > ship > Hard > Structure
_EFF_NAVAL_GUN_100MM = {
    "Soft":        {"big": {"accuracy": 0.88, "destroy_capacity": 0.50},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.58},
                    "small": {"accuracy": 0.82, "destroy_capacity": 0.66}},
    "Armored":     {"big": {"accuracy": 0.60, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.58},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.72}},
    "Hard":        {"big": {"accuracy": 0.65, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.07},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.10}},
    "Structure":   {"big": {"accuracy": 0.65, "destroy_capacity": 0.015},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.025},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.038}},
    "Air_Defense": {"big": {"accuracy": 0.60, "destroy_capacity": 0.10},
                    "med": {"accuracy": 0.55, "destroy_capacity": 0.13},
                    "small": {"accuracy": 0.50, "destroy_capacity": 0.16}},
    "Airbase":     {"big": {"accuracy": 0.60, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.60, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.60, "destroy_capacity": 1e-8}},
    "Port":        {"big": {"accuracy": 0.62, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.58, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.09}},
    "Shipyard":    {"big": {"accuracy": 0.60, "destroy_capacity": 0.03},
                    "med": {"accuracy": 0.56, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.52, "destroy_capacity": 0.07}},
    "Farp":        {"big": {"accuracy": 0.62, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.62, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.62, "destroy_capacity": 1e-8}},
    "Stronghold":  {"big": {"accuracy": 0.60, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.60, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.60, "destroy_capacity": 1e-8}},
    "ship":        {"big": {"accuracy": 0.60, "destroy_capacity": 0.28},
                    "med": {"accuracy": 0.65, "destroy_capacity": 0.33},
                    "small": {"accuracy": 0.70, "destroy_capacity": 0.38}},
}

# ── Cannone navale 127 mm / 5-in (Mk-45) ──────────────────────────────────────
# Ordine atteso: Soft > Armored > ship > Hard > Structure
_EFF_NAVAL_GUN_127MM = {
    "Soft":        {"big": {"accuracy": 0.90, "destroy_capacity": 0.55},
                    "med": {"accuracy": 0.87, "destroy_capacity": 0.63},
                    "small": {"accuracy": 0.84, "destroy_capacity": 0.71}},
    "Armored":     {"big": {"accuracy": 0.65, "destroy_capacity": 0.50},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.62},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.75}},
    "Hard":        {"big": {"accuracy": 0.70, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.65, "destroy_capacity": 0.09},
                    "small": {"accuracy": 0.60, "destroy_capacity": 0.13}},
    "Structure":   {"big": {"accuracy": 0.70, "destroy_capacity": 0.020},
                    "med": {"accuracy": 0.65, "destroy_capacity": 0.032},
                    "small": {"accuracy": 0.60, "destroy_capacity": 0.045}},
    "Air_Defense": {"big": {"accuracy": 0.65, "destroy_capacity": 0.12},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.18}},
    "Airbase":     {"big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-8}},
    "Port":        {"big": {"accuracy": 0.68, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.63, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.58, "destroy_capacity": 0.11}},
    "Shipyard":    {"big": {"accuracy": 0.65, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.60, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.55, "destroy_capacity": 0.09}},
    "Farp":        {"big": {"accuracy": 0.68, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.68, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.68, "destroy_capacity": 1e-8}},
    "Stronghold":  {"big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-8}},
    "ship":        {"big": {"accuracy": 0.65, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.70, "destroy_capacity": 0.40},
                    "small": {"accuracy": 0.72, "destroy_capacity": 0.45}},
}

# ── Cannone navale 130 mm (AK-130) ────────────────────────────────────────────
# Ordine atteso: Soft > Armored > ship > Hard > Structure
_EFF_NAVAL_GUN_130MM = {
    "Soft":        {"big": {"accuracy": 0.90, "destroy_capacity": 0.60},
                    "med": {"accuracy": 0.87, "destroy_capacity": 0.68},
                    "small": {"accuracy": 0.84, "destroy_capacity": 0.76}},
    "Armored":     {"big": {"accuracy": 0.68, "destroy_capacity": 0.52},
                    "med": {"accuracy": 0.62, "destroy_capacity": 0.65},
                    "small": {"accuracy": 0.56, "destroy_capacity": 0.78}},
    "Hard":        {"big": {"accuracy": 0.72, "destroy_capacity": 0.07},
                    "med": {"accuracy": 0.67, "destroy_capacity": 0.10},
                    "small": {"accuracy": 0.62, "destroy_capacity": 0.14}},
    "Structure":   {"big": {"accuracy": 0.72, "destroy_capacity": 0.025},
                    "med": {"accuracy": 0.67, "destroy_capacity": 0.038},
                    "small": {"accuracy": 0.62, "destroy_capacity": 0.052}},
    "Air_Defense": {"big": {"accuracy": 0.68, "destroy_capacity": 0.14},
                    "med": {"accuracy": 0.62, "destroy_capacity": 0.17},
                    "small": {"accuracy": 0.56, "destroy_capacity": 0.20}},
    "Airbase":     {"big": {"accuracy": 0.68, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.68, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.68, "destroy_capacity": 1e-8}},
    "Port":        {"big": {"accuracy": 0.70, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.65, "destroy_capacity": 0.09},
                    "small": {"accuracy": 0.60, "destroy_capacity": 0.13}},
    "Shipyard":    {"big": {"accuracy": 0.68, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.63, "destroy_capacity": 0.07},
                    "small": {"accuracy": 0.58, "destroy_capacity": 0.10}},
    "Farp":        {"big": {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.70, "destroy_capacity": 1e-8}},
    "Stronghold":  {"big": {"accuracy": 0.68, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.68, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.68, "destroy_capacity": 1e-8}},
    "ship":        {"big": {"accuracy": 0.68, "destroy_capacity": 0.40},
                    "med": {"accuracy": 0.72, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.50}},
}

# ── CIWS (Mk-15-Phalanx, AK-630, Type-730) ───────────────────────────────────
# Sistema di difesa ravvicinata anti-missile / anti-aereo.
# Efficacia molto ridotta vs bersagli superficiali; i proiettili 20-30 mm non
# penetrano la corazza dei carri ma possono danneggiare APCs, ottiche e sistemi
# esterni (dc > ship). Le navi assorbono 20-30 mm senza effetti significativi.
# Ordine atteso: Soft > Armored > ship (tutti i valori sono molto bassi)
_EFF_CIWS = {
    "Soft":        {"big": {"accuracy": 0.30, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.25, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.20, "destroy_capacity": 0.07}},
    "Armored":     {"big": {"accuracy": 0.10, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.08, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.06, "destroy_capacity": 0.08}},
    "Hard":        {"big": {"accuracy": 0.08, "destroy_capacity": 0.005},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.005},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.005}},
    "Structure":   {"big": {"accuracy": 0.08, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.06, "destroy_capacity": 0.002},
                    "small": {"accuracy": 0.05, "destroy_capacity": 0.003}},
    "Air_Defense": {"big": {"accuracy": 0.10, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.08, "destroy_capacity": 0.03},
                    "small": {"accuracy": 0.06, "destroy_capacity": 0.04}},
    "Airbase":     {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-10}},
    "Port":        {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-10}},
    "Shipyard":    {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-10}},
    "Farp":        {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-10}},
    "Stronghold":  {"big": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.08, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.08, "destroy_capacity": 1e-10}},
    "ship":        {"big": {"accuracy": 0.15, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.10, "destroy_capacity": 0.03},
                    "small": {"accuracy": 0.08, "destroy_capacity": 0.04}},
}


# ── FUNZIONI DI SCORING ───────────────────────────────────────────────────────

def get_sam_score(model: str) -> float:
    """Restituisce il punteggio SAM calcolato dai parametri dell'arma.

    Args:
        model: modello del SAM (chiave in SHIP_WEAPONS['MISSILES_SAM'])

    Returns:
        float: punteggio arma
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    weapon = SHIP_WEAPONS['MISSILES_SAM'].get(model)
    if not weapon:
        logger.warning(f"MISSILES_SAM {model!r} unknown")
        return 0.0

    return sum(weapon[p] * c for p, c in WEAPON_PARAM['MISSILES_SAM'].items())


def get_asm_score(model: str) -> float:
    """Restituisce il punteggio ASM calcolato dai parametri dell'arma.

    Args:
        model: modello del missile anti-nave (chiave in SHIP_WEAPONS['MISSILES_ASM'])

    Returns:
        float: punteggio arma
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    weapon = SHIP_WEAPONS['MISSILES_ASM'].get(model)
    if not weapon:
        logger.warning(f"MISSILES_ASM {model!r} unknown")
        return 0.0

    return sum(weapon[p] * c for p, c in WEAPON_PARAM['MISSILES_ASM'].items())


def get_torpedo_score(model: str) -> float:
    """Restituisce il punteggio siluro calcolato dai parametri dell'arma.

    Args:
        model: modello del siluro (chiave in SHIP_WEAPONS['MISSILES_TORPEDO'])

    Returns:
        float: punteggio arma
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    weapon = SHIP_WEAPONS['MISSILES_TORPEDO'].get(model)
    if not weapon:
        logger.warning(f"MISSILES_TORPEDO {model!r} unknown")
        return 0.0

    return sum(weapon[p] * c for p, c in WEAPON_PARAM['MISSILES_TORPEDO'].items())


def get_gun_score(model: str) -> float:
    """Restituisce il punteggio cannone navale calcolato dai parametri dell'arma.

    Args:
        model: modello del cannone (chiave in SHIP_WEAPONS['GUNS'])

    Returns:
        float: punteggio arma
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    weapon = SHIP_WEAPONS['GUNS'].get(model)
    if not weapon:
        logger.warning(f"GUNS {model!r} unknown")
        return 0.0

    return sum(weapon[p] * c for p, c in WEAPON_PARAM['GUNS'].items())


def get_ciws_score(model: str) -> float:
    """Restituisce il punteggio CIWS calcolato dai parametri dell'arma.

    Args:
        model: modello CIWS (chiave in SHIP_WEAPONS['CIWS'])

    Returns:
        float: punteggio arma
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    weapon = SHIP_WEAPONS['CIWS'].get(model)
    if not weapon:
        logger.warning(f"CIWS {model!r} unknown")
        return 0.0

    return sum(weapon[p] * c for p, c in WEAPON_PARAM['CIWS'].items())


def get_weapon_score(weapon_type: str, weapon_model: str) -> float:
    """Dispatcher: restituisce il punteggio dell'arma navale specificata.

    Analogo a get_weapon_score() di Ground_Weapon_Data.

    Args:
        weapon_type:  categoria ('MISSILES_SAM', 'MISSILES_ASM', 'MISSILES_TORPEDO', 'GUNS', 'CIWS')
        weapon_model: modello specifico

    Returns:
        float: punteggio arma
    """
    if not weapon_type or not isinstance(weapon_type, str):
        raise TypeError("weapon_type must be a non-empty str")
    if weapon_type not in SHIP_WEAPONS:
        raise ValueError(
            f"weapon_type must be in {list(SHIP_WEAPONS.keys())}. Got {weapon_type!r}"
        )
    if not weapon_model or not isinstance(weapon_model, str):
        raise TypeError("weapon_model must be a non-empty str")

    if weapon_type == 'MISSILES_SAM':
        return get_sam_score(weapon_model)
    elif weapon_type == 'MISSILES_ASM':
        return get_asm_score(weapon_model)
    elif weapon_type == 'MISSILES_TORPEDO':
        return get_torpedo_score(weapon_model)
    elif weapon_type == 'GUNS':
        return get_gun_score(weapon_model)
    elif weapon_type == 'CIWS':
        return get_ciws_score(weapon_model)
    else:
        logger.warning(f"weapon_type unknown: {weapon_type!r}")
        return 0.0


# ── API ───────────────────────────────────────────────────────────────────────

def get_ship_weapon(model: str) -> Optional[Dict[str, Any]]:
    """Cerca un modello di arma navale in tutte le categorie di SHIP_WEAPONS.

    Analogo a get_weapon() di Ground_Weapon_Data.

    Args:
        model: nome del modello

    Returns:
        Dict con chiavi 'weapons_category' e 'weapons_data', oppure None se non trovato.
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    for category, weapons in SHIP_WEAPONS.items():
        if model in weapons:
            return {"weapons_category": category, "weapons_data": weapons[model]}

    return None


def get_weapon_score_target(model: str, target_type: List, target_dimension: List) -> float:
    """Restituisce l'efficacia dell'arma navale contro una lista di bersagli.

    Analogo a get_weapon_score_target() di Ground_Weapon_Data.

    Args:
        model:            modello arma
        target_type:      lista di tipi di bersaglio (es. ['ship', 'Port'])
        target_dimension: lista di dimensioni (es. ['big', 'med'])

    Returns:
        float: punteggio medio di efficacia (accuracy × destroy_capacity)
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    weapon_dict = get_ship_weapon(model)
    if not weapon_dict:
        logger.warning(f"ship weapon {model!r} unknown")
        return 0.0

    weapon = weapon_dict.get('weapons_data', {})
    score = 0.0
    count = 0

    for t_type in target_type:
        if t_type not in TARGET_CLASSIFICATION:
            logger.warning(
                f"target_type {t_type!r} unknown, got {target_type}. Continue."
            )
            continue
        for t_dim in target_dimension:
            if t_dim not in TARGET_DIMENSION:
                logger.warning(
                    f"target_dimension {t_dim!r} unknown, got {target_dimension}. Continue."
                )
                continue
            eff = weapon.get('efficiency', {}).get(t_type, {}).get(t_dim, {})
            score += eff.get('accuracy', 0.0) * eff.get('destroy_capacity', 0.0)
            count += 1

    return score / count if count > 0 else 0.0


def get_weapon_score_target_distribuition(
    model: str,
    target_type: Dict,
    target_dimension: Dict,
) -> float:
    """Restituisce l'efficacia dell'arma navale con distribuzione ponderata dei bersagli.

    Analogo a get_weapon_score_target_distribuition() di Ground_Weapon_Data.

    Args:
        model:            modello arma
        target_type:      dict {tipo: peso}  es. {'ship': 0.7, 'Port': 0.3}
        target_dimension: dict {dim:  peso}  es. {'big': 0.6, 'med': 0.4}

    Returns:
        float: punteggio ponderato di efficacia
    """
    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")
    if not isinstance(target_type, dict):
        raise TypeError(f"target_type must be dict, got {type(target_type).__name__}")
    if not isinstance(target_dimension, dict):
        raise TypeError(f"target_dimension must be dict, got {type(target_dimension).__name__}")

    weapon_dict = get_ship_weapon(model)
    if not weapon_dict:
        logger.warning(f"ship weapon {model!r} unknown")
        return 0.0

    weapon = weapon_dict.get('weapons_data', {})
    score = 0.0

    for t_type, t_type_w in target_type.items():
        if t_type not in TARGET_CLASSIFICATION:
            logger.warning(
                f"target_type {t_type!r} unknown, got {target_type}. Continue."
            )
            continue
        for t_dim, t_dim_w in target_dimension.items():
            if t_dim not in TARGET_DIMENSION:
                logger.warning(
                    f"target_dimension {t_dim!r} unknown, got {target_dimension}. Continue."
                )
                continue
            eff = weapon.get('efficiency', {}).get(t_type, {}).get(t_dim, {})
            score += (
                eff.get('accuracy', 0.0)
                * eff.get('destroy_capacity', 0.0)
                * t_type_w
                * t_dim_w
            )

    return score


# ── DATI ARMI NAVALI ──────────────────────────────────────────────────────────
#
# Struttura:
#   SHIP_WEAPONS[weapon_type][model] = {
#       'model':       str,
#       'start_service': int,
#       'end_service': int | None,
#       ... parametri fisici (caliber, warhead, range, speed, ...) ...
#       'task':        List[str],
#       'perc_efficiency_variability': float,
#       'efficiency':  dict (template)
#   }
#
# Unità:
#   caliber   → mm
#   warhead   → kg
#   range     → km
#   speed     → m/s  (SAM, ASM) | kt (siluri)
#   muzzle_speed → m/s
#   fire_rate → rpm

SHIP_WEAPONS: Dict[str, Dict[str, Any]] = {

    # ─────────────────────────────────────────────────────────────────────────
    'MISSILES_SAM': {

        'RIM-162-ESSM': {
            'model':          'RIM-162-ESSM',
            'start_service':  2004,
            'end_service':    None,
            'caliber':        254,     # mm
            'warhead':        39,      # kg
            'range':          50,      # km
            'speed':          1360,    # m/s  (Mach 4)
            'guidance':       'Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_SAM_MERAD,
        },

        'RIM-7M-Sea-Sparrow': {
            'model':          'RIM-7M-Sea-Sparrow',
            'start_service':  1976,
            'end_service':    None,
            'caliber':        203,
            'warhead':        39,
            'range':          19,
            'speed':          850,     # m/s  (Mach 2.5)
            'guidance':       'Semi_Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_SAM_SHORAD,
        },

        'RIM-66-SM-1': {
            'model':          'RIM-66-SM-1',
            'start_service':  1967,
            'end_service':    None,
            'caliber':        343,
            'warhead':        62,
            'range':          74,
            'speed':          1190,    # m/s  (Mach 3.5)
            'guidance':       'Semi_Active_Radar',
            'task':           ['Anti_Air'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_SAM_MERAD,
        },

        'RIM-66-SM-2': {
            'model':          'RIM-66-SM-2',
            'start_service':  1978,
            'end_service':    None,
            'caliber':        343,
            'warhead':        62,
            'range':          167,
            'speed':          1190,
            'guidance':       'Semi_Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.12,
            'efficiency':     _EFF_SAM_LORAD,
        },

        'RIM-156-SM-2ER': {
            'model':          'RIM-156-SM-2ER',
            'start_service':  1990,
            'end_service':    None,
            'caliber':        343,
            'warhead':        115,
            'range':          240,
            'speed':          1190,
            'guidance':       'Semi_Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_SAM_LORAD,
        },

        'SA-N-4-Gecko': {
            'model':          'SA-N-4-Gecko',
            'start_service':  1967,
            'end_service':    None,
            'caliber':        120,
            'warhead':        15,
            'range':          12,
            'speed':          850,
            'guidance':       'Radio_Command',
            'task':           ['Anti_Air'],
            'perc_efficiency_variability': 0.20,
            'efficiency':     _EFF_SAM_SHORAD,
        },

        'SA-N-9-Gauntlet': {
            'model':          'SA-N-9-Gauntlet',
            'start_service':  1989,
            'end_service':    None,
            'caliber':        152,
            'warhead':        15,
            'range':          15,
            'speed':          950,
            'guidance':       'Radio_Command',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_SAM_SHORAD,
        },

        'S-300F': {
            'model':          'S-300F',
            'start_service':  1984,
            'end_service':    None,
            'caliber':        508,
            'warhead':        145,
            'range':          150,
            'speed':          2040,    # m/s  (Mach 6)
            'guidance':       'Semi_Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile', 'Anti_Ballistic'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_SAM_LORAD,
        },

        'HHQ-7': {
            'model':          'HHQ-7',
            'start_service':  1989,
            'end_service':    None,
            'caliber':        156,
            'warhead':        15,
            'range':          13,
            'speed':          780,
            'guidance':       'Radio_Command',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.18,
            'efficiency':     _EFF_SAM_SHORAD,
        },

        'HHQ-9': {
            'model':          'HHQ-9',
            'start_service':  2004,
            'end_service':    None,
            'caliber':        212,
            'warhead':        180,
            'range':          200,
            'speed':          1430,    # m/s  (Mach 4.2)
            'guidance':       'Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile', 'Anti_Ballistic'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_SAM_LORAD,
        },

        'HHQ-16': {
            'model':          'HHQ-16',
            'start_service':  2012,
            'end_service':    None,
            'caliber':        220,
            'warhead':        60,
            'range':          70,
            'speed':          1190,
            'guidance':       'Active_Radar',
            'task':           ['Anti_Air', 'Anti_Missile'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_SAM_MERAD,
        },

        'URK-5-Rastrub': {
            # Dual-purpose: anti-submarine rocket + limited anti-ship capability
            'model':          'URK-5-Rastrub',
            'start_service':  1985,
            'end_service':    None,
            'caliber':        533,
            'warhead':        185,
            'range':          15,
            'speed':          306,     # m/s  (subsonic, rocket-propelled torpedo)
            'guidance':       'Inertial',
            'task':           ['Anti_Air', 'Anti_Submarine'],
            'perc_efficiency_variability': 0.20,
            'efficiency':     _EFF_SAM_MERAD,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    'MISSILES_ASM': {

        'RGM-84-Harpoon': {
            'model':          'RGM-84-Harpoon',
            'start_service':  1977,
            'end_service':    None,
            'caliber':        343,
            'warhead':        221,
            'range':          280,
            'speed':          289,     # m/s  (Mach 0.85)
            'guidance':       'Active_Radar',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_ASM_ANTISHIP_SUBSONIC,
        },

        'BGM-109-Tomahawk': {
            'model':          'BGM-109-Tomahawk',
            'start_service':  1983,
            'end_service':    None,
            'caliber':        519,
            'warhead':        454,
            'range':          1600,
            'speed':          252,     # m/s  (Mach 0.74)
            'guidance':       'Inertial_TERCOM_GPS',
            'task':           ['Land_Attack', 'Anti_Ship'],
            'perc_efficiency_variability': 0.05,
            'efficiency':     _EFF_ASM_CRUISE_LANDATTACK,
        },

        'P-700-Granit': {
            'model':          'P-700-Granit',
            'start_service':  1983,
            'end_service':    None,
            'caliber':        850,
            'warhead':        750,
            'range':          550,
            'speed':          850,     # m/s  (Mach 2.5, sea-skimming phase)
            'guidance':       'Active_Radar_Inertial',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_ASM_SUPERSONIC_HEAVY,
        },

        'P-270-Moskit': {
            'model':          'P-270-Moskit',
            'start_service':  1984,
            'end_service':    None,
            'caliber':        760,
            'warhead':        300,
            'range':          120,
            'speed':          952,     # m/s  (Mach 2.8)
            'guidance':       'Active_Radar_Inertial',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_ASM_SUPERSONIC,
        },

        'P-1000-Vulkan': {
            'model':          'P-1000-Vulkan',
            'start_service':  1987,
            'end_service':    None,
            'caliber':        880,
            'warhead':        500,
            'range':          700,
            'speed':          850,
            'guidance':       'Active_Radar_Inertial',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_ASM_SUPERSONIC_HEAVY,
        },

        'YJ-12': {
            'model':          'YJ-12',
            'start_service':  2015,
            'end_service':    None,
            'caliber':        500,
            'warhead':        205,
            'range':          400,
            'speed':          1020,    # m/s  (Mach 3)
            'guidance':       'Active_Radar_Inertial',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_ASM_SUPERSONIC,
        },

        'YJ-18': {
            'model':          'YJ-18',
            'start_service':  2015,
            'end_service':    None,
            'caliber':        540,
            'warhead':        300,
            'range':          540,
            'speed':          850,     # m/s  (terminal sprint, Mach 2.5)
            'guidance':       'Active_Radar_Inertial',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_ASM_SUPERSONIC,
        },

        'YJ-83': {
            'model':          'YJ-83',
            'start_service':  1998,
            'end_service':    None,
            'caliber':        360,
            'warhead':        165,
            'range':          180,
            'speed':          306,     # m/s  (Mach 0.9)
            'guidance':       'Active_Radar',
            'task':           ['Anti_Ship'],
            'perc_efficiency_variability': 0.12,
            'efficiency':     _EFF_ASM_ANTISHIP_SUBSONIC,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    'MISSILES_TORPEDO': {

        'Mk-46': {
            'model':          'Mk-46',
            'start_service':  1965,
            'end_service':    None,
            'caliber':        324,     # mm
            'warhead':        44,      # kg
            'range':          11,      # km
            'speed':          40,      # kt
            'guidance':       'Active_Passive_Acoustic',
            'task':           ['Anti_Submarine', 'Anti_Ship'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_TORPEDO_LIGHT,
        },

        'Mk-48': {
            'model':          'Mk-48',
            'start_service':  1972,
            'end_service':    None,
            'caliber':        533,
            'warhead':        290,
            'range':          50,
            'speed':          55,
            'guidance':       'Wire_Active_Passive_Acoustic',
            'task':           ['Anti_Submarine', 'Anti_Ship'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_TORPEDO_HEAVY,
        },

        'TEST-71': {
            'model':          'TEST-71',
            'start_service':  1971,
            'end_service':    None,
            'caliber':        533,
            'warhead':        205,
            'range':          20,
            'speed':          40,
            'guidance':       'Wire_Active_Passive_Acoustic',
            'task':           ['Anti_Submarine', 'Anti_Ship'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_TORPEDO_HEAVY,
        },

        'USET-80': {
            'model':          'USET-80',
            'start_service':  1980,
            'end_service':    None,
            'caliber':        533,
            'warhead':        200,
            'range':          18,
            'speed':          45,
            'guidance':       'Active_Passive_Acoustic',
            'task':           ['Anti_Submarine', 'Anti_Ship'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_TORPEDO_HEAVY,
        },

        'Type-93': {
            'model':          'Type-93',
            'start_service':  1998,
            'end_service':    None,
            'caliber':        533,
            'warhead':        267,
            'range':          30,
            'speed':          45,
            'guidance':       'Active_Passive_Acoustic',
            'task':           ['Anti_Submarine', 'Anti_Ship'],
            'perc_efficiency_variability': 0.12,
            'efficiency':     _EFF_TORPEDO_HEAVY,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    'GUNS': {

        'Mk-45-5in': {
            'model':          'Mk-45-5in',
            'start_service':  1971,
            'end_service':    None,
            'caliber':        127,     # mm
            'muzzle_speed':   810,     # m/s
            'fire_rate':      20,      # rpm
            'range':          24,      # km
            'ammo_type':      ['HE', 'APFSDS'],
            'task':           ['Naval_Gunfire_Support', 'Anti_Ship', 'Anti_Air'],
            'perc_efficiency_variability': 0.12,
            'efficiency':     _EFF_NAVAL_GUN_127MM,
        },

        'OTO-Melara-76mm': {
            'model':          'OTO-Melara-76mm',
            'start_service':  1969,
            'end_service':    None,
            'caliber':        76,
            'muzzle_speed':   925,
            'fire_rate':      120,
            'range':          16,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Air', 'Anti_Ship', 'Naval_Gunfire_Support'],
            'perc_efficiency_variability': 0.12,
            'efficiency':     _EFF_NAVAL_GUN_76MM,
        },

        'AK-100-100mm': {
            'model':          'AK-100-100mm',
            'start_service':  1980,
            'end_service':    None,
            'caliber':        100,
            'muzzle_speed':   880,
            'fire_rate':      60,
            'range':          21,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Air', 'Anti_Ship', 'Naval_Gunfire_Support'],
            'perc_efficiency_variability': 0.13,
            'efficiency':     _EFF_NAVAL_GUN_100MM,
        },

        'AK-130-130mm': {
            'model':          'AK-130-130mm',
            'start_service':  1985,
            'end_service':    None,
            'caliber':        130,
            'muzzle_speed':   850,
            'fire_rate':      40,
            'range':          25,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Air', 'Anti_Ship', 'Naval_Gunfire_Support'],
            'perc_efficiency_variability': 0.12,
            'efficiency':     _EFF_NAVAL_GUN_130MM,
        },

        'AK-176-76mm': {
            'model':          'AK-176-76mm',
            'start_service':  1979,
            'end_service':    None,
            'caliber':        76,
            'muzzle_speed':   980,
            'fire_rate':      120,
            'range':          15,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Air', 'Anti_Ship'],
            'perc_efficiency_variability': 0.13,
            'efficiency':     _EFF_NAVAL_GUN_76MM,
        },

        'Type-79A-100mm': {
            'model':          'Type-79A-100mm',
            'start_service':  1988,
            'end_service':    None,
            'caliber':        100,
            'muzzle_speed':   900,
            'fire_rate':      25,
            'range':          22,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Air', 'Anti_Ship', 'Naval_Gunfire_Support'],
            'perc_efficiency_variability': 0.15,
            'efficiency':     _EFF_NAVAL_GUN_100MM,
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    'CIWS': {

        'Mk-15-Phalanx': {
            'model':          'Mk-15-Phalanx',
            'start_service':  1980,
            'end_service':    None,
            'caliber':        20,      # mm
            'fire_rate':      4500,    # rpm
            'range':          1.5,     # km
            'ammo_type':      ['APFSDS'],
            'task':           ['Anti_Missile', 'Anti_Air'],
            'perc_efficiency_variability': 0.08,
            'efficiency':     _EFF_CIWS,
        },

        'AK-630': {
            'model':          'AK-630',
            'start_service':  1976,
            'end_service':    None,
            'caliber':        30,
            'fire_rate':      5000,
            'range':          4.0,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Missile', 'Anti_Air'],
            'perc_efficiency_variability': 0.10,
            'efficiency':     _EFF_CIWS,
        },

        'Type-730': {
            'model':          'Type-730',
            'start_service':  2004,
            'end_service':    None,
            'caliber':        30,
            'fire_rate':      5800,
            'range':          3.0,
            'ammo_type':      ['HE', 'FRAG'],
            'task':           ['Anti_Missile', 'Anti_Air'],
            'perc_efficiency_variability': 0.09,
            'efficiency':     _EFF_CIWS,
        },
    },
}
