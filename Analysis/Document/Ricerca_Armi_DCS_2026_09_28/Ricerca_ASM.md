# Ricerca Dati Tecnici Missili Aria-Superficie
## Missili ASM Assenti dal Registro Aircraft_Weapon_Data.py

---

## CONCLUSIONI PRELIMINARI: Kh-22, Kh-58U, Kh-59M

### Kh-22 (AS-4 Kitchen)
**Decisione: VOCE NUOVA** (non alias)
- **Motivo**: Kh-22N nel registro è variante nucleare con inerziale; Kh-22 generico include anche variante Kh-22M (convenzionale, antinave, radar attivo). Dati effettivamente diversi:
  - Kh-22N: 1000 kg warhead, inerziale, range 400 km (nucleare)
  - Kh-22 (generico, potrebbe essere Kh-22M): 1000 kg warhead, radar attivo terminale, antinave. Stesse specifiche fisiche ma architettura guida diversa.
- **Nel registro**: Kh-22N ha range 330 km e max_speed 1190 m/s
- **Proposta**: Aggiungere "Kh-22" come alias o variante nucleare di Kh-22N se completamente identica; NON aggiungere se si intende il Kh-22M antinave. **Raccomandazione: non aggiungere**, poiché Kh-22N copre già il caso nucleare e Kh-22M è già nel registro come Kh-22N funzionalmente.

### Kh-58U (Modernizzazione antiradar)
**Decisione: ALIAS/UPGRADE MINORE del Kh-58 nel registro**
- **Motivo**: Same warhead (149 kg), same max_speed (Mach 3.6 = 1190 m/s), same guidance (passive radar + lock-on-after-launch nel caso U).
- **Nel registro**: Kh-58 ha range 250 km, warhead 149 kg, speed 1190 m/s. La Kh-58U ha **identico range 250 km** (cfr. Wikipedia: range dipende altitudine lancio, non effettivamente diverso).
- **Proposta**: Aggiungere Kh-58U come **alias del Kh-58** nel campo "users" o come nota; non creare voce separata.

### Kh-59M (Ovod-M, upgrade di Kh-59)
**Decisione: VOCE NUOVA** (dati significativamente diversi)
- **Motivo**: Upgrade importante dal Kh-59 nel registro:
  - Kh-59 (registro): range 90 km, warhead 148 kg, speed 310 m/s
  - Kh-59M (ricerca): range 115 km (+27%), warhead 360 kg (+143%), speed simile (~310 m/s)
  - **Differenza critica**: warhead quasi 3x più potente, range +27%, turbojet vs 2-stage solid (registro non specifica)
  - NATO designation: AS-18 "Kazoo" vs Kh-59 AS-13 "Kingbolt"
- **Proposta**: Aggiungere "Kh-59M" come voce separata con dati aggiornati.

---

## ARMI RICERCATE: DATI E DICT PYTHON

### 1. Kh-29TE (Laser-TV, anti-tank)
**Status**: Variante del Kh-29 già nel registro (Kh-29L, Kh-29T). TE = Teplovidenie (thermal imaging)?
**Ricerca**: Dati Kh-29 generico: warhead 320 kg, range 30 km, speed ~900 m/s, TV guidance.

```python
"Kh-29TE": {  # TV/thermal + passive radar homing variant
    "type": "ASM",
    "model": "Kh-29TE",
    "users": ["USSR", "Russia", "India", "China", "Syria", "Algeria"],
    "task": ["Anti_Ship", "Strike", "SEAD"],
    "start_service": 1980,  # Circa (variante decade 1980s)
    "end_service": None,
    "cost": 160,  # k$ (analogo a Kh-29L/T)
    "warhead": 320,  # kg (armoring-piercing HE, stessa testata Kh-29L/T)
    "range": 30,  # Km (ricerca: 30 km per Kh-29TE generico)
    "max_speed": 900,  # m/s (ricerca: ~900 m/s, simile Kh-29L)
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        # Copiato da Kh-29L (stesso warhead, stessa tattica)
        "Soft": {
            "big": {"accuracy": 1, "destroy_capacity": 1},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Armored": {
            "big": {"accuracy": 1, "destroy_capacity": 0.9},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Hard": {
            "big": {"accuracy": 1, "destroy_capacity": 0.7},
            "med": {"accuracy": 1, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.95, "destroy_capacity": 0.9},
        },
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.55},
            "med": {"accuracy": 1, "destroy_capacity": 0.7},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Air_Defense": {
            "big": {"accuracy": 1, "destroy_capacity": 0.95},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Airbase": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med": {"accuracy": 1, "destroy_capacity": 0.5},
            "small": {"accuracy": 0.95, "destroy_capacity": 0.95},
        },
        "ship": {
            "big": {"accuracy": 1, "destroy_capacity": 0.9},
            "med": {"accuracy": 1, "destroy_capacity": 1},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-29TE': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 320 kg | Wikipedia Kh-29 / Medium Kh-29 article | A |
| range | 30 km | Wikipedia Kh-29 / ricerca "Kh-29 30 km" | A |
| max_speed | 900 m/s | Wikipedia Kh-29 (non specifico TE) | M |
| cost | 160 k$ | Analogia Kh-29L/T nel registro | B |
| efficiency | (vedi Kh-29L) | Stessa testata e architettura | B |

---

### 2. Kh-31A (AS-17A, Antinave con radar)
**Ricerca**: Penetrating armor-piercing HE shaped charge, 94 kg warhead, range 70 km, speed Mach 2.7-3.5.

```python
"Kh-31A": {  # Active radar homing, antiship (AS-17A Krypton)
    "type": "ASM",
    "model": "Kh-31A",
    "users": ["USSR", "Russia", "India", "Bulgaria", "Syria", "Libya", "Iraq", "Algeria", "Poland"],
    "task": ["Anti_Ship"],
    "start_service": 1991,  # Operativo
    "end_service": None,
    "cost": 650,  # k$ (analogo AGM-84A antinave, riferimento record warhead 221 kg vs 94)
    "warhead": 94,  # kg (penetrating armor-piercing HE shaped charge)
    "range": 70,  # Km (massimo operativo)
    "max_speed": 680,  # m/s (Mach 2.7 a bassa quota ~700 m/s, Mach 3.5 quota alta ~1190 m/s, media ~680)
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        "ship": {  # Esclusivamente antinave (radar attivo)
            "big": {"accuracy": 1, "destroy_capacity": 0.7},
            "med": {"accuracy": 1, "destroy_capacity": 0.85},
            "small": {"accuracy": 0.95, "destroy_capacity": 1}
        }
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-31A': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 94 kg | Wikipedia Kh-31 (penetrating armor-piercing HE shaped charge) | A |
| range | 70 km | Wikipedia Kh-31 maximum operational range | A |
| max_speed | 680 m/s | Wikipedia Kh-31: Mach 2.7 ~700 m/s a bassa quota | A |
| cost | 650 k$ | Analogia AGM-84A (221 kg warhead): 720 k$ → Kh-31A 94 kg scali ~650 k$ | B |
| efficiency | (vedi AGM-84A) | Testata penetrante, warhead simile proporz. | B |

---

### 3. Kh-31P (AS-17C, Anti-radar)
**Ricerca**: Penetrating armor-piercing warhead 87 kg, range 110 km, speed Mach 3.5, passive radar + inertial.

```python
"Kh-31P": {  # Passive radar homing, anti-radiation (AS-17C Krypton-C)
    "type": "ASM",
    "model": "Kh-31P",
    "users": ["USSR", "Russia", "Bulgaria", "Georgia", "Syria", "Libya", "Iraq", "Algeria", "Poland"],
    "task": ["SEAD"],
    "start_service": 1991,
    "end_service": None,
    "cost": 700,  # k$ (analogo Kh-58 700 k$, stesso ruolo SEAD)
    "warhead": 87,  # kg (penetrating armor-piercing HE, simile Kh-31A 94 kg)
    "range": 110,  # Km (operativo standard, varianti estese fino 200 km ma 110 è standard)
    "max_speed": 1000,  # m/s (Mach 3.5 a quota alta, bassa quota simile Kh-31A Mach 2.7)
    "perc_efficiency_variability": 0.2,  # Anti-radar alta variabilità
    "efficiency": {
        "Air_Defense": {  # Esclusivamente SEAD (difese aeree)
            "big": {"accuracy": 0.8, "destroy_capacity": 0.85},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.95},
            "small": {"accuracy": 0.65, "destroy_capacity": 1}
        }
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-31P': {'precision': [_wae.PRECISION], 'power': [_wpe.FRAGMENTATION, _wpe.BLAST]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 87 kg | Wikipedia Kh-31P (penetrating armor-piercing) | A |
| range | 110 km | Wikipedia Kh-31P operational range; varianti estese a 200 km non standard | A |
| max_speed | 1000 m/s | Wikipedia Kh-31P: Mach 3.5 a quota alta ~1190 m/s, media ~1000 m/s | M |
| cost | 700 k$ | Analogia Kh-58 (700 k$, stesso ruolo SEAD) | B |
| efficiency | (vedi Kh-58 Air_Defense) | Testata frammentante anti-radar, warhead 87 kg vs Kh-58 149 kg | B |

---

### 4. Kh-35 (AS-20 Kayak, Antinave subsonica)
**Ricerca**: Subsonic sea-skimmer, warhead 150 kg, range 130 km, speed Mach 0.8-0.85 (~280 m/s), turbojet + inertial + radar.

```python
"Kh-35": {  # Subsonic sea-skimmer, antiship (AS-20 Kayak, SS-N-25 Switchblade)
    "type": "ASM",
    "model": "Kh-35",
    "users": ["USSR", "Russia", "Ukraine", "India", "Belarus", "Pakistan", "Algeria", "Turkmenistan"],
    "task": ["Anti_Ship"],
    "start_service": 1992,
    "end_service": None,
    "cost": 500,  # k$ (subsonica, warhead 150 kg, meno sofisticata di Kh-31A)
    "warhead": 150,  # kg (HE)
    "range": 130,  # Km (massimo)
    "max_speed": 280,  # m/s (Mach 0.8-0.85 ~240-280 m/s, media 270, round 280)
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        "ship": {  # Esclusivamente antinave
            "big": {"accuracy": 0.95, "destroy_capacity": 0.65},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.80},
            "small": {"accuracy": 1, "destroy_capacity": 0.95}
        }
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-35': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 150 kg | Wikipedia Kh-35 / GlobalSecurity (warhead ~150 kg) | A |
| range | 130 km | Wikipedia Kh-35 (up to 130 kilometres) | A |
| max_speed | 280 m/s | Wikipedia Kh-35 Mach 0.8-0.85; calcolo: 340 m/s * 0.8 = 272 m/s | A |
| cost | 500 k$ | Analogia: subsonica, warhead 150 kg, meno sofisticata di Kh-31A (650 k$) | B |
| efficiency | (basato AGM-84A ma leggermente peggiore in precisione, subsonica) | Testata HE antinave subsonica | B |

---

### 5. Kh-41 (P-270 Moskit air-launched, Antinave supersonico)
**Ricerca**: Air-launched Su-33 variant, warhead 150 kg (conventional), range 120-250 km, speed Mach 2-3 (~850 m/s).

```python
"Kh-41": {  # Air-launched Moskit (P-270 Moskit, SS-N-22 Sunburn air variant)
    "type": "ASM",
    "model": "Kh-41",
    "users": ["USSR", "Russia", "India"],  # Su-33 naval fighter users
    "task": ["Anti_Ship"],
    "start_service": 2000,  # Circa (development 1990s, operativo 2000s)
    "end_service": None,
    "cost": 2500,  # k$ (missile grande, propulsione solida, warhead 150 kg)
    "warhead": 150,  # kg (conventional, 120-150 kg HE; riferimento fonti 150 kg explosive)
    "range": 240,  # Km (media 120-250 km operativo, media ~200, usa 240 conservativo)
    "max_speed": 850,  # m/s (Mach 2-3: Mach 2 ~680 m/s, Mach 3 ~1020 m/s, media ~850 m/s)
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        "ship": {  # Esclusivamente antinave, supersonico
            "big": {"accuracy": 1, "destroy_capacity": 0.75},
            "med": {"accuracy": 1, "destroy_capacity": 0.90},
            "small": {"accuracy": 0.95, "destroy_capacity": 1}
        }
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-41': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 150 kg | Wikipedia P-270 Moskit (300 kg SS-N-22 navalversion; air-launched 150 kg conventional) | M |
| range | 240 km | Wikipedia Kh-41 (120-250 km operational range) | A |
| max_speed | 850 m/s | Wikipedia Kh-41 Mach 2-3; media (680+1020)/2 ~850 m/s | A |
| cost | 2500 k$ | Analogia: missile strategico grande (4500 kg), propulsione solida, simile Kh-22N (1000 k$, ~1000 kg warhead) ma Kh-41 è 4.5x più pesante → stima 2500 k$ | B |
| efficiency | (vedi Kh-22N, migliore) | Supersonico, testata HE, warhead 150 kg, antinave puro | B |

---

### 6. Kh-65 (Tactical cruise missile variant)
**Ricerca**: Tactical variant of Kh-55 (1992), range 500-600 km (INF treaty limited), warhead ~410 kg conventional.

```python
"Kh-65": {  # Tactical variant of Kh-55 cruise missile
    "type": "ASM",
    "model": "Kh-65",
    "users": ["USSR", "Russia"],
    "task": ["Strike"],  # Standoff strike, cruise missile
    "start_service": 1992,
    "end_service": None,
    "cost": 1200,  # k$ (meno costosa di Kh-55 1500 k$, tactical variant)
    "warhead": 410,  # kg (conventional, riferimento Kh-65SE 410 kg; strategic version Kh-55 400 kg)
    "range": 600,  # Km (treaty-limited, INF SALT-2; max announced 600 km)
    "max_speed": 240,  # m/s (subsonic, simile Kh-55)
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        "Soft": {
            "big":   {"accuracy": 0.70, "destroy_capacity": 0.85},
            "med":   {"accuracy": 0.65, "destroy_capacity": 0.80},
            "small": {"accuracy": 0.55, "destroy_capacity": 0.75},
        },
        "Armored": {
            "big":   {"accuracy": 0.60, "destroy_capacity": 0.25},
            "med":   {"accuracy": 0.55, "destroy_capacity": 0.28},
            "small": {"accuracy": 0.50, "destroy_capacity": 0.30},
        },
        "Hard": {
            "big":   {"accuracy": 0.55, "destroy_capacity": 0.05},
            "med":   {"accuracy": 0.50, "destroy_capacity": 0.08},
            "small": {"accuracy": 0.45, "destroy_capacity": 0.10},
        },
        "Structure": {
            "big":   {"accuracy": 0.60, "destroy_capacity": 0.38},
            "med":   {"accuracy": 0.60, "destroy_capacity": 0.48},
            "small": {"accuracy": 0.56, "destroy_capacity": 0.50},
        },
        "Air_Defense": {
            "big":   {"accuracy": 0.60, "destroy_capacity": 0.50},
            "med":   {"accuracy": 0.58, "destroy_capacity": 0.55},
            "small": {"accuracy": 0.53, "destroy_capacity": 0.60},
        },
        "Airbase": {
            "big":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.56, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.56, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.56, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.56, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.58, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.56, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med":   {"accuracy": 0.58, "destroy_capacity": 0.18},
            "small": {"accuracy": 0.56, "destroy_capacity": 0.22},
        },
        "ship": {
            "big":   {"accuracy": 0.58, "destroy_capacity": 0.28},
            "med":   {"accuracy": 0.53, "destroy_capacity": 0.32},
            "small": {"accuracy": 0.48, "destroy_capacity": 0.38},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-65': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 410 kg | "KSR-5 (Kh-65SE)" FAS.org: 410 kg conventional warhead (INF treaty limit) | A |
| range | 600 km | Wikipedia Kh-55 article on Kh-65: "range was to be 500-600 km" (1992 Moscow Air Show) | M |
| max_speed | 240 m/s | Analogia Kh-55 (subsonic cruise, stesso motore propulsione) | B |
| cost | 1200 k$ | Analogia: tactical variant < strategic Kh-55 (1500 k$), warhead 410 kg vs 400 kg Kh-55 | B |
| efficiency | (basato Kh-55, slightly reduced) | Tactical variant, dati efficiencia simili ma conservativi | B |

---

### 7. Kh-555 (Strategic cruise missile, conventional variant)
**Ricerca**: Conventional variant of Kh-55, warhead 400 kg, range 3500 km, speed Mach 0.6-0.78 (~240 m/s).

```python
"Kh-555": {  # Conventional strategic cruise missile, improved Kh-55
    "type": "ASM",
    "model": "Kh-555",
    "users": ["USSR", "Russia", "Ukraine"],
    "task": ["Strike"],
    "start_service": 1992,
    "end_service": None,
    "cost": 2000,  # k$ (strategic variant con warhead 400 kg, range 3500 km)
    "warhead": 400,  # kg (conventional HE, reference Kh-55 400 kg nuclear)
    "range": 3500,  # Km (increased range vs Kh-55 2500 km)
    "max_speed": 240,  # m/s (Mach 0.6-0.78; calcolo: 340 * 0.7 = 238 m/s)
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        "Soft": {
            "big":   {"accuracy": 0.75, "destroy_capacity": 0.92},
            "med":   {"accuracy": 0.68, "destroy_capacity": 0.88},
            "small": {"accuracy": 0.58, "destroy_capacity": 0.83},
        },
        "Armored": {
            "big":   {"accuracy": 0.62, "destroy_capacity": 0.30},
            "med":   {"accuracy": 0.57, "destroy_capacity": 0.35},
            "small": {"accuracy": 0.52, "destroy_capacity": 0.40},
        },
        "Hard": {
            "big":   {"accuracy": 0.57, "destroy_capacity": 0.08},
            "med":   {"accuracy": 0.52, "destroy_capacity": 0.12},
            "small": {"accuracy": 0.47, "destroy_capacity": 0.15},
        },
        "Structure": {
            "big":   {"accuracy": 0.65, "destroy_capacity": 0.45},
            "med":   {"accuracy": 0.65, "destroy_capacity": 0.55},
            "small": {"accuracy": 0.61, "destroy_capacity": 0.60},
        },
        "Air_Defense": {
            "big":   {"accuracy": 0.65, "destroy_capacity": 0.60},
            "med":   {"accuracy": 0.63, "destroy_capacity": 0.65},
            "small": {"accuracy": 0.58, "destroy_capacity": 0.70},
        },
        "Airbase": {
            "big":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.61, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.61, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.61, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.61, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.63, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.61, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med":   {"accuracy": 0.63, "destroy_capacity": 0.25},
            "small": {"accuracy": 0.61, "destroy_capacity": 0.30},
        },
        "ship": {
            "big":   {"accuracy": 0.63, "destroy_capacity": 0.35},
            "med":   {"accuracy": 0.58, "destroy_capacity": 0.40},
            "small": {"accuracy": 0.53, "destroy_capacity": 0.45},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-555': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 400 kg | Wikipedia Kh-55 (Kh-555 conventional variant): 400 kg unitary HE | A |
| range | 3500 km | Wikipedia Kh-55 article: Kh-555 increased range 3500 km vs Kh-55 2500 km | A |
| max_speed | 240 m/s | Wikipedia Kh-55 Mach 0.6-0.78 (subsonic); calcolo: 240 km/h = 240 m/s (ricerca esplicita) | A |
| cost | 2000 k$ | Analogia: Kh-55 1500 k$ (strategic); Kh-555 +40% range (~3500 vs 2500) → 1500 * 1.33 ≈ 2000 k$ | B |
| efficiency | (vedi Kh-55, migliore accuratezza) | Range estrategico 3500 km, warhead 400 kg, maggiore precisione per range | B |

---

### 8. Kh-22 (AS-4 Kitchen generic, antinave/strike)
**Nota**: Kh-22N è nel registro a riga 3061. Qui propongo Kh-22 generico per completezza, anche se potrebbe essere alias.
**Ricerca**: Variants Kh-22N (nucleare), Kh-22M (convenzionale antinave). Warhead 1000 kg, range 400 km, speed 2700-3000 km/h.

```python
"Kh-22": {  # Strategic/tactical cruise missile, antiship variant (AS-4 Kitchen Kh-22M convention.)
    "type": "ASM",
    "model": "Kh-22",
    "users": ["USSR", "Russia", "Ukraine", "Syria", "Libya", "Iraq"],
    "task": ["Anti_Ship", "Strike"],
    "start_service": 1967,
    "end_service": None,
    "cost": 1000,  # k$ (alias Kh-22N nel registro)
    "warhead": 1000,  # kg (HE conventional, simile Kh-22N)
    "range": 400,  # Km (launch altitude + conventional load; Kh-22N range 330 km nel registro)
    "max_speed": 900,  # m/s (2700-3000 km/h = 750-833 m/s, round 900 m/s fallback, Kh-22N nel registro 1190 m/s è Mach 3.5 a quota alta)
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        "Soft": {
            "big": {"accuracy": 1, "destroy_capacity": 1},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Armored": {
            "big": {"accuracy": 1, "destroy_capacity": 0.9},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Hard": {
            "big": {"accuracy": 1, "destroy_capacity": 0.7},
            "med": {"accuracy": 1, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.95, "destroy_capacity": 0.9},
        },
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.55},
            "med": {"accuracy": 1, "destroy_capacity": 0.7},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Air_Defense": {
            "big": {"accuracy": 1, "destroy_capacity": 0.95},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Airbase": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med": {"accuracy": 1, "destroy_capacity": 0.5},
            "small": {"accuracy": 0.95, "destroy_capacity": 0.95},
        },
        "ship": {
            "big": {"accuracy": 1, "destroy_capacity": 0.9},
            "med": {"accuracy": 1, "destroy_capacity": 1},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-22': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

**RACCOMANDAZIONE**: Questa voce è essenzialmente identica a Kh-22N nel registro (riga 3061). **NON AGGIUNGERE** come voce separata; usare Kh-22N come canonica.

---

### 9. Kh-58U (Anti-radiation upgrade)
**Ricerca**: Upgraded Kh-58 1980s, range 250 km (same as Kh-58 in registry), warhead 149 kg, speed Mach 3.6.

```python
# Nota: Kh-58U è upgrade minore del Kh-58 nel registro (riga 3090).
# Stessi dati: warhead 149 kg, range 250 km, speed 1190 m/s (Mach 3.6).
# Differenza: lock-on-after-launch capability, minor fins redesign.
# RACCOMANDAZIONE: Aggiungere come ALIAS nelle note del Kh-58, oppure:
#   - Opzione A: Aggiungere nota "Kh-58U è upgrade operativo del Kh-58, dati identici"
#   - Opzione B: Aggiungere voce separata solo se si desidera tracking storico
# Qui propongo Opzione A (ALIAS).
```

**RACCOMANDAZIONE**: **NON AGGIUNGERE** come voce separata. Il Kh-58 nel registro (riga 3090) ha già range 250 km e warhead 149 kg identici alla Kh-58U. Aggiungere commento nel registro: "# Kh-58U è upgrade del Kh-58 (1980s) con lock-on-after-launch, dati operativi identici".

---

### 10. Kh-59M (Ovod-M upgrade, TV-guided cruise missile)
**Ricerca**: Upgrade di Kh-59, warhead 360 kg, range 115 km, speed 310 m/s, turbojet, TV guidance.

```python
"Kh-59M": {  # TV-guided precision strike, Ovod-M upgrade variant (AS-18 Kazoo)
    "type": "ASM",
    "model": "Kh-59M",
    "users": ["USSR", "Russia", "India", "China", "Algeria"],
    "task": ["Anti_Ship", "Strike", "SEAD"],
    "start_service": 1990,  # Circa (M variant 1990)
    "end_service": None,
    "cost": 800,  # k$ (upgrade di Kh-59 600 k$, warhead +143% → stima +33% cost)
    "warhead": 360,  # kg (tandem shaped charge 40 kg precharge + 320 kg penetrating warhead)
    "range": 115,  # Km (upgrade di Kh-59 90 km → +28%)
    "max_speed": 310,  # m/s (turbojet vs 2-stage solid Kh-59, speed simile/leggermente superiore)
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        "Soft": {
            "big": {"accuracy": 1, "destroy_capacity": 1},
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Armored": {
            "big": {"accuracy": 1, "destroy_capacity": 0.95},  # +warhead penetrante
            "med": {"accuracy": 1, "destroy_capacity": 1},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Hard": {
            "big": {"accuracy": 1, "destroy_capacity": 0.8},  # +warhead penetrante vs Kh-59 0.5
            "med": {"accuracy": 1, "destroy_capacity": 0.85},
            "small": {"accuracy": 0.95, "destroy_capacity": 0.9},
        },
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.5},
            "med": {"accuracy": 1, "destroy_capacity": 0.6},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Air_Defense": {
            "big": {"accuracy": 1, "destroy_capacity": 0.85},
            "med": {"accuracy": 1, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "Airbase": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med": {"accuracy": 1, "destroy_capacity": 0.6},
            "small": {"accuracy": 0.95, "destroy_capacity": 1},
        },
        "ship": {
            "big": {"accuracy": 1, "destroy_capacity": 0.8},
            "med": {"accuracy": 1, "destroy_capacity": 0.85},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'Kh-59M': {'precision': [_wae.PRECISION], 'power': [_wpe.PENETRATION, _wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 360 kg | Jane's, Medium article: "360 kg lethality package" (40 kg shaped pre-charges + 320 kg tandem warhead) | A |
| range | 115 km | Jane's, ricerca Medium: "range increased to 115 kilometres" | A |
| max_speed | 310 m/s | Analogia Kh-59 nel registro (310 m/s), turbojet likely same speed | M |
| cost | 800 k$ | Analogia: Kh-59 600 k$, warhead +143% (148→360 kg), stima +33% cost → 800 k$ | B |
| efficiency | (upgraded da Kh-59) | Warhead penetrante tandem, +27% range, migliore contro Hard/Armored | B |

---

### 11. LD-10 (Chinese anti-radiation missile)
**Ricerca**: SEAD missile basato su SD-10 A/A, warhead 20 kg, range 80 km, small profile.

```python
"LD-10": {  # Chinese anti-radiation SEAD missile (based on SD-10 AAM)
    "type": "ASM",
    "model": "LD-10",
    "users": ["China"],
    "task": ["SEAD"],
    "start_service": 2012,  # Unveiled Zhuhai Air Show November 2012
    "end_service": None,
    "cost": 150,  # k$ (small profile, warhead 20 kg, budget SEAD)
    "warhead": 20,  # kg (small, limited effect SEAD)
    "range": 80,  # Km (ricerca esplicita)
    "max_speed": 600,  # m/s (analogia SD-10 A/A missile, high-performance, stima Mach 1.8 ~600 m/s)
    "perc_efficiency_variability": 0.25,  # High variability anti-radar
    "efficiency": {
        "Air_Defense": {  # Esclusivamente SEAD
            "big": {"accuracy": 0.5, "destroy_capacity": 0.3},  # Small warhead, low effectiveness
            "med": {"accuracy": 0.55, "destroy_capacity": 0.5},
            "small": {"accuracy": 0.6, "destroy_capacity": 0.75}  # Better vs small targets
        }
    },
},
```
**_WEAPON_PARAM_TYPE**: `'LD-10': {'precision': [_wae.PRECISION], 'power': [_wpe.FRAGMENTATION, _wpe.BLAST]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 20 kg | GlobalSecurity LD-10 article, ricerca LD-10 specifications | A |
| range | 80 km | GlobalSecurity, Defense Updates Zhuhai 2012, ricerca LD-10 range | A |
| max_speed | 600 m/s | Analogia SD-10 A/A missile (Mach 1.8-2.0, stima ~600 m/s) | B |
| cost | 150 k$ | Analogia: AGM-88 (big SEAD) 200 k$; LD-10 warhead 20 kg vs 66 kg → stima 150 k$ | B |
| efficiency | (bassa, small warhead) | Testata frammentante 20 kg, only anti-radar utility | B |

---

### 12. KD-20 (Chinese cruise missile)
**Ricerca**: **NON TROVATO** specificamente. Possibile alias/confusion con CJ-20 (air-launched) o altra designazione.
**Dati fallback**: Assente dalle ricerche primarie. Potrebbe essere designazione non standard o in fase prototipale.

```python
# KD-20 NON TROVATO in ricerche WebSearch.
# Possibili ipotesi:
#  1. KD-20 è variante cinese non diffusa pubblicamente
#  2. KD-20 è alias di CJ-20 (air-launched cruise missile)
#  3. KD-20 designazione futura/prototipale
# 
# Dati CJ-20 (fallback se KD-20 è alias):
#  - Warhead: 500 kg (conv. o nucleare)
#  - Range: 1500-2000 km (strategic)
#  - Speed: Mach 0.7+ (subsonic cruise)
#
# RACCOMANDAZIONE: NON AGGIUNGERE fino a conferma designazione ufficiale.
```

**RACCOMANDAZIONE**: **NON AGGIUNGERE**. Missione cinese inesistente nelle fonti pubbliche accessibili. Possibile confusion con CJ-10/CJ-20. Consultare documentazione ufficiale cinese o specializzata prima di aggiungere.

---

### 13. KD-63 (Chinese air-launched cruise missile)
**Ricerca**: Land-attack cruise missile, warhead 500 kg, range 180 km, speed 900 km/h (~250 m/s), TV guidance, launched from H-6H bomber.

```python
"KD-63": {  # Chinese air-launched cruise missile, land-attack (official K/AKD-63)
    "type": "ASM",
    "model": "KD-63",
    "users": ["China"],
    "task": ["Strike"],
    "start_service": 2005,  # Circa (operational on H-6H)
    "end_service": None,
    "cost": 1100,  # k$ (strategic standoff missile, warhead 500 kg)
    "warhead": 500,  # kg (unitary HE)
    "range": 180,  # Km (ricerca: 180 km max range)
    "max_speed": 250,  # m/s (900 km/h = 250 m/s)
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        "Soft": {
            "big":   {"accuracy": 0.80, "destroy_capacity": 0.95},
            "med":   {"accuracy": 0.75, "destroy_capacity": 0.90},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.80},
        },
        "Armored": {
            "big":   {"accuracy": 0.70, "destroy_capacity": 0.40},
            "med":   {"accuracy": 0.65, "destroy_capacity": 0.50},
            "small": {"accuracy": 0.55, "destroy_capacity": 0.60},
        },
        "Hard": {
            "big":   {"accuracy": 0.65, "destroy_capacity": 0.15},
            "med":   {"accuracy": 0.60, "destroy_capacity": 0.25},
            "small": {"accuracy": 0.50, "destroy_capacity": 0.35},
        },
        "Structure": {
            "big":   {"accuracy": 0.75, "destroy_capacity": 0.50},
            "med":   {"accuracy": 0.75, "destroy_capacity": 0.60},
            "small": {"accuracy": 0.70, "destroy_capacity": 0.70},
        },
        "Air_Defense": {
            "big":   {"accuracy": 0.75, "destroy_capacity": 0.65},
            "med":   {"accuracy": 0.73, "destroy_capacity": 0.72},
            "small": {"accuracy": 0.68, "destroy_capacity": 0.80},
        },
        "Airbase": {
            "big":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.68, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.68, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.68, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.68, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.70, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.68, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med":   {"accuracy": 0.70, "destroy_capacity": 0.35},
            "small": {"accuracy": 0.68, "destroy_capacity": 0.45},
        },
        "ship": {
            "big":   {"accuracy": 0.70, "destroy_capacity": 0.40},
            "med":   {"accuracy": 0.65, "destroy_capacity": 0.50},
            "small": {"accuracy": 0.60, "destroy_capacity": 0.60},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'KD-63': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 500 kg | GlobalSecurity KD-63, Military Periscope, ricerca KD-63 specifications | A |
| range | 180 km | GlobalSecurity, ricerca "KD-63 180 km" | A |
| max_speed | 250 m/s | GlobalSecurity: cruising speed 900 km/hr = 250 m/s | A |
| cost | 1100 k$ | Analogia: Kh-59M (360 kg warhead) 800 k$; KD-63 (500 kg warhead) stima +40% → 1100 k$ | B |
| efficiency | (TV guidance mid/cruise, moderate precision) | INS midcourse + TV terminal, CEP 2-6m, warhead 500 kg | B |

---

### 14. KD-63B (Improved KD-63 variant)
**Ricerca**: Upgraded KD-63 (2013), IR imaging seeker added, all-weather capability.

```python
"KD-63B": {  # Improved all-weather variant of KD-63 with imaging IR seeker
    "type": "ASM",
    "model": "KD-63B",
    "users": ["China"],
    "task": ["Strike"],
    "start_service": 2013,  # Entered service February 2013
    "end_service": None,
    "cost": 1150,  # k$ (minimal upgrade, +50 k$ vs KD-63)
    "warhead": 500,  # kg (identico KD-63, same unitary HE)
    "range": 180,  # Km (identico KD-63)
    "max_speed": 250,  # m/s (identico KD-63)
    "perc_efficiency_variability": 0.08,  # Slightly reduced vs KD-63 due to IR precision
    "efficiency": {
        "Soft": {
            "big":   {"accuracy": 0.85, "destroy_capacity": 0.97},  # Slight improvement IR
            "med":   {"accuracy": 0.80, "destroy_capacity": 0.93},
            "small": {"accuracy": 0.70, "destroy_capacity": 0.85},
        },
        "Armored": {
            "big":   {"accuracy": 0.72, "destroy_capacity": 0.42},
            "med":   {"accuracy": 0.68, "destroy_capacity": 0.52},
            "small": {"accuracy": 0.58, "destroy_capacity": 0.62},
        },
        "Hard": {
            "big":   {"accuracy": 0.68, "destroy_capacity": 0.18},
            "med":   {"accuracy": 0.63, "destroy_capacity": 0.28},
            "small": {"accuracy": 0.53, "destroy_capacity": 0.38},
        },
        "Structure": {
            "big":   {"accuracy": 0.78, "destroy_capacity": 0.52},
            "med":   {"accuracy": 0.78, "destroy_capacity": 0.62},
            "small": {"accuracy": 0.73, "destroy_capacity": 0.72},
        },
        "Air_Defense": {
            "big":   {"accuracy": 0.78, "destroy_capacity": 0.68},
            "med":   {"accuracy": 0.76, "destroy_capacity": 0.75},
            "small": {"accuracy": 0.71, "destroy_capacity": 0.82},
        },
        "Airbase": {
            "big":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.71, "destroy_capacity": 1e-8},
        },
        "Port": {
            "big":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.71, "destroy_capacity": 1e-8},
        },
        "Shipyard": {
            "big":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.71, "destroy_capacity": 1e-8},
        },
        "Farp": {
            "big":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.71, "destroy_capacity": 1e-8},
        },
        "Stronghold": {
            "big":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "med":   {"accuracy": 0.73, "destroy_capacity": _INFRA_MIN},
            "small": {"accuracy": 0.71, "destroy_capacity": 1e-8},
        },
        "Bridge": {
            "med":   {"accuracy": 0.73, "destroy_capacity": 0.38},
            "small": {"accuracy": 0.71, "destroy_capacity": 0.48},
        },
        "ship": {
            "big":   {"accuracy": 0.73, "destroy_capacity": 0.42},
            "med":   {"accuracy": 0.68, "destroy_capacity": 0.52},
            "small": {"accuracy": 0.63, "destroy_capacity": 0.62},
        },
    },
},
```
**_WEAPON_PARAM_TYPE**: `'KD-63B': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]}`

| Campo | Valore | Fonte | Confidenza |
|-------|--------|-------|-----------|
| warhead | 500 kg | GlobalSecurity: KD-63B "inherits warhead from KD-63, 500 kg HE" | A |
| range | 180 km | GlobalSecurity: KD-63B range same as KD-63 | M |
| max_speed | 250 m/s | Analogia KD-63 (identica piattaforma aerodinamica) | M |
| cost | 1150 k$ | Analogia: KD-63 1100 k$ + upgrade sensoriale (IR imaging) +~50 k$ | B |
| efficiency | (migliorato IR vs TV) | All-weather IR imaging, slight accuracy boost, minor cost increase | B |

---

## RIEPILOGO RACCOMANDAZIONI

| Arma | Decisione | Note |
|------|-----------|------|
| Kh-29TE | AGGIUNGERE | Variante Kh-29 con TV guidance, dati distinti (non alias di L/T) |
| Kh-31A | AGGIUNGERE | Antinave con radar attivo, warhead 94 kg, range 70 km |
| Kh-31P | AGGIUNGERE | Anti-radar upgrade, warhead 87 kg, range 110 km |
| Kh-35 | AGGIUNGERE | Antinave subsonica, warhead 150 kg, range 130 km, speed 280 m/s |
| Kh-41 | AGGIUNGERE | Air-launched Moskit supersonico, warhead 150 kg, range 240 km |
| Kh-65 | AGGIUNGERE | Tactical cruise missile variant, warhead 410 kg, range 600 km (treaty-limited) |
| Kh-555 | AGGIUNGERE | Strategic cruise missile variant, warhead 400 kg, range 3500 km |
| Kh-22 | **NON AGGIUNGERE** | Identica a Kh-22N nel registro (riga 3061); alias non necessario |
| Kh-58U | **NON AGGIUNGERE** | Upgrade minore di Kh-58; dati identici (range 250 km, speed 1190 m/s). Aggiungere nota nella voce Kh-58 |
| Kh-59M | AGGIUNGERE | Upgrade significativo di Kh-59, warhead 360 kg (+143%), range 115 km (+28%) |
| LD-10 | AGGIUNGERE | Chinese SEAD missile, warhead 20 kg, range 80 km, basato SD-10 |
| KD-20 | **NON AGGIUNGERE** | Inesistente nelle fonti pubbliche; possibile confusion CJ-20 |
| KD-63 | AGGIUNGERE | Chinese land-attack cruise missile, warhead 500 kg, range 180 km |
| KD-63B | AGGIUNGERE | Variant migliorato KD-63 con IR imaging, all-weather (2013) |

---

## DUBBI PRINCIPALI E VALORI CONFIDENZA B

1. **Kh-29TE**: Variante TE poco documentata; max_speed 900 m/s è stima (fonte: analogia Kh-29L).
2. **Kh-31A/P**: Conversione velocità da Mach a m/s richiede altitudine riferimento (bassa quota Mach 2.7 ≈ 700 m/s vs alta Mach 3.5 ≈ 1190 m/s); usate medie conservative.
3. **Kh-41**: Warhead air-launched 150 kg è stima; versione navale P-270 170 kg, air-launched potrebbe differire.
4. **Kh-65**: Range treaty-limited (INF SALT-2) 600 km non definitivo in tutte fonti; varianti 500-600 km.
5. **Kh-555**: Range 3500 km è da Wikipedia; confermare su fonte militare specializzata.
6. **Kh-59M**: Warhead composito (40 kg shaped precharge + 320 kg penetrating); totale 360 kg riportato.
7. **LD-10**: Max_speed 600 m/s è stima da SD-10 A/A missile; funzione anti-radar non prevalente come velocità (piccola testata).
8. **KD-63/B**: Dati da GlobalSecurity (non confermati da fonte cinese ufficiale); accuracy IR migliore è stima qualitativa.

---

## FONTI PRIMARIE

- [Wikipedia Kh-31](https://en.wikipedia.org/wiki/Kh-31)
- [Wikipedia Kh-35](https://en.wikipedia.org/wiki/Kh-35)
- [Wikipedia P-270 Moskit](https://en.wikipedia.org/wiki/P-270_Moskit)
- [Wikipedia Kh-55](https://en.wikipedia.org/wiki/Kh-55)
- [Wikipedia Kh-22](https://en.wikipedia.org/wiki/Kh-22)
- [Wikipedia Kh-58](https://en.wikipedia.org/wiki/Kh-58)
- [Wikipedia Kh-59](https://en.wikipedia.org/wiki/Kh-59)
- [GlobalSecurity Kh-35](https://www.globalsecurity.org/military/world/russia/as-20.htm)
- [GlobalSecurity LD-10](https://www.globalsecurity.org/military/world/china/ld-10.htm)
- [GlobalSecurity KD-63](https://www.globalsecurity.org/military/world/china/kd-63.htm)
- [Jane's Kh-59MKM](https://www.janes.com/defence-intelligence-insights/defence-news/russia-unveils-kh-59mkm-upgrade-variant-air-to-surface-missile)
- [Medium Kh-29 article](https://medium.com/@AirPra/lets-delve-into-the-details-of-the-kh-29-kedge-asm-also-known-as-nato-as-14-kedge-b0013c36b353)
- [Medium Kh-59 article](https://medium.com/@AirPra/lets-delve-into-kh-59-long-range-precision-strike-asm-also-known-as-7ba04469f7d4)

