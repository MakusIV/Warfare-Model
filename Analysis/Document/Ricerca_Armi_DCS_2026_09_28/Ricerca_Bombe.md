# Ricerca Bombe Assenti dal Registro

**Data**: 2026-09-28  
**Stato**: Ricerca dati tecnici per bombe non presenti in `Aircraft_Weapon_Data.py`  
**Scope**: 24 armi (guidate russe, guidate cinesi, non guidate russe, USA AIR, cluster russe)

---

## 1. Bombe Guidate Russe

### KAB-500Kr-OD (variante OD = optical daylight)

**Dict Python** (pronto da incollare dopo testata):
```python
"KAB-500Kr-OD": {
    "type": "Guided bombs",
    "model": "KAB-500Kr-OD",
    "users": ["Russia"],
    "task": ["Strike"],
    "start_service": 1995,
    "end_service": None,
    "cost": 24,  # k$, stima: variante migliore della KAB-500Kr, B
    "warhead": 201,  # kg, stessa testata della KAB-500L/Kr
    # release: variante ottica della KAB-500Kr. Confidenza M: finestra identica a KAB-500Kr [F10],
    # solo il sistema di guida e' diverso (TV vs ottica). Drop-angle stimato per analogia (B).
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 500,  # m AGL
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1150,  # km/h
        'dive_angle': (0, 50),  # gradi (min, max), None se 'dive' non ammesso
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        # STIMA: identica a KAB-500Kr (analogia di famiglia, solo cambio sistema guida)
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.4},
            "med": {"accuracy": 1, "destroy_capacity": 0.45},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.5}
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.35},
            "med": {"accuracy": 1, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.45}
        },
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1},
            "small": {"accuracy": 0.65, "destroy_capacity": 1}
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.7, "destroy_capacity": 1}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.7, "destroy_capacity": 1}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'KAB-500Kr-OD': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 201 | Stessa carica della KAB-500L/Kr (ru.wikipedia KAB-500) | A |
| min_altitude (m) | 500 | KAB-500Kr, stessa famiglia [F10] | M |
| max_altitude (m) | 5000 | KAB-500Kr, stessa famiglia [F10] | M |
| min_speed (km/h) | 500 | KAB-500Kr [F10] | M |
| max_speed (km/h) | 1150 | KAB-500Kr [F10] | M |
| dive_angle (gradi) | (0, 50) | Analogia KAB-500Kr (sistema guida diverso, pero' stesse consegne) | B |
| drag | low | KAB-500Kr, stessa forma aerodinamica | M |
| glide_ratio | None | KAB-500Kr, non plana significativamente [F10] | M |
| cost (k$) | 24 | Stima: variante ottica piu' cara della base 23 | B |
| start_service | 1995 | Variante successiva a KAB-500Kr (~1980 base); periodo perestrojka sviluppi | B |

---

### KAB-500S (variante imaging infrarosso)

**Dict Python**:
```python
"KAB-500S": {
    "type": "Guided bombs",
    "model": "KAB-500S",
    "users": ["Russia"],
    "task": ["Strike"],
    "start_service": 1992,
    "end_service": None,
    "cost": 25,  # k$, stima: guida IR piu' sofisticata della OD, B
    "warhead": 201,  # kg
    # release: variante IR della KAB-500. Confidenza M: finestra identica a KAB-500Kr [F10],
    # come per KAB-500Kr-OD. Guida TV/IR non cambia la balistica.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 500,  # m AGL
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1150,  # km/h
        'dive_angle': (0, 50),  # gradi (min, max)
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        # Identica a KAB-500Kr: sensore IR non muta il danno, solo la precisione (gia' massima)
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.4},
            "med": {"accuracy": 1, "destroy_capacity": 0.45},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.5}
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.35},
            "med": {"accuracy": 1, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.45}
        },
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1},
            "small": {"accuracy": 0.65, "destroy_capacity": 1}
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.7, "destroy_capacity": 1}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.7, "destroy_capacity": 1}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'KAB-500S': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 201 | Stessa carica della FAB-500 base | A |
| min_altitude (m) | 500 | Famiglia KAB-500, sgancio guidato a distanza [F10] | M |
| max_altitude (m) | 5000 | Limite funzionale guida a IR (temperatura contrasto) | B |
| min_speed (km/h) | 500 | KAB-500 famiglia | M |
| max_speed (km/h) | 1150 | KAB-500 famiglia [F10] | M |
| dive_angle (gradi) | (0, 50) | Analogia KAB-500 | B |
| cost (k$) | 25 | Stima: guida IR (seconda generazione anni '90) | B |
| start_service | 1992 | Sviluppo post-Guerra Fredda, tecnologia infrarosso primi anni '90 | B |

---

### KAB-1500Kr (guida TV fuoco-e-dimentica, testata 667 kg)

**Dict Python**:
```python
"KAB-1500Kr": {
    "type": "Guided bombs",
    "model": "KAB-1500Kr",
    "users": ["Russia"],
    "task": ["Strike"],
    "start_service": 1988,
    "end_service": None,
    "cost": 40,  # k$, stima: bomba pesante guidata, piu' cara della base ~5x, B
    "warhead": 667,  # kg, stessa carica della FAB-1500M54
    # release: Confidenza M: dati tecnici non trovati in letteratura aperta. Stima per analogia
    # con KAB-500Kr e FAB-1500M54. La FAB-1500 è limitata a 850 m (§0.2) e la KAB-500Kr a 500 m
    # (sgancio guidato con distanza). Stima per KAB-1500Kr: 600 m (carica piu' grande, sgancio
    # a distanza; conservativa). Max_altitude: FAB-1500 testimoniata fino a 12500 m testata,
    # KAB-1500Kr probabilmente simile.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 600,  # m AGL, stima per carica 667 kg, §0.2 = 851 m; sgancio guidato riduce il minimo, B
        'max_altitude': 10000,  # m, stima per bomba pesante ma guidata; max_alt FAB-1500 = 12500 m testato, KAB ridotta per carica alta, B
        'min_speed': 500,  # km/h, analogia KAB-500Kr
        'max_speed': 1150,  # km/h, analogia KAB-500Kr; bomba pesante non varia significativamente
        'dive_angle': (0, 50),  # gradi, stima per analogia
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        # Testata molto potente. Efficienza superiore alla KAB-500Kr su bersagli grossi.
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.6},  # stima: 1.5x della KAB-500Kr
            "med": {"accuracy": 1, "destroy_capacity": 0.65},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.7}
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.55},
            "med": {"accuracy": 1, "destroy_capacity": 0.6},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.65}
        },
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1.2},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.2},
            "small": {"accuracy": 0.65, "destroy_capacity": 1.1}
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.2}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.2}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'KAB-1500Kr': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 667 | Equivalente FAB-1500 (ru.wikipedia "Soviet and Russian aerial bombs") | A |
| min_altitude (m) | 600 | Stima §0.2: carica 667 kg → 851 m non guidata; sgancio TV riduce di ~30%, B |
| max_altitude (m) | 10000 | Stima: FAB-1500 testata a 12500 m; KAB-1500 probabilmente simile o leggermente meno per carica alta, B |
| min_speed (km/h) | 500 | Analogia famiglia KAB-500 | B |
| max_speed (km/h) | 1150 | Analogia famiglia KAB-500 | B |
| dive_angle (gradi) | (0, 50) | Stima per analogia KAB-500 | B |
| cost (k$) | 40 | Stima: bomba pesante guidata; ratio 5x della KAB-500Kr (25 k$), B |
| start_service | 1988 | Sviluppo anni '80 (riportato in enciclopedie secondarie) | B |

---

### KAB-1500LG-Pr (laser-guida progressiva, testata 667 kg)

**Dict Python**:
```python
"KAB-1500LG-Pr": {
    "type": "Guided bombs",
    "model": "KAB-1500LG-Pr",
    "users": ["Russia"],
    "task": ["Strike"],
    "start_service": 1995,
    "end_service": None,
    "cost": 42,  # k$, stima: guida laser piu' costosa della TV, B
    "warhead": 667,  # kg
    # release: Confidenza M/B: stima per analogia con KAB-500L (guida laser) e KAB-1500Kr (TV).
    # KAB-500L: 500-5000 m. KAB-1500Kr: stimata 600-10000 m. KAB-1500LG-Pr: stima intermedia
    # per carica grande. "Pr" = progressive = SPO (flying wing) posteriore per aggiornamento.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 600,  # m AGL, come KAB-1500Kr
        'max_altitude': 10000,  # m, come KAB-1500Kr; laser non cambia il vincolo di carica
        'min_speed': 500,  # km/h, analogia famiglia
        'max_speed': 1150,  # km/h, analogia famiglia
        'dive_angle': (0, 50),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        # Identica a KAB-1500Kr: il tipo di guida (laser vs TV) non muta il danno a impatto.
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.6},
            "med": {"accuracy": 1, "destroy_capacity": 0.65},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.7}
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.55},
            "med": {"accuracy": 1, "destroy_capacity": 0.6},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.65}
        },
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1.2},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.2},
            "small": {"accuracy": 0.65, "destroy_capacity": 1.1}
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.2}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.2}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'KAB-1500LG-Pr': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 667 | Stessa carica della FAB-1500 | A |
| min_altitude (m) | 600 | Stima: come KAB-1500Kr, B |
| max_altitude (m) | 10000 | Stima: come KAB-1500Kr, B |
| min_speed (km/h) | 500 | Analogia famiglia | B |
| max_speed (km/h) | 1150 | Analogia famiglia | B |
| dive_angle (gradi) | (0, 50) | Stima per analogia | B |
| cost (k$) | 42 | Stima: guida laser leggermente piu' costosa della TV (~5% premium), B |
| start_service | 1995 | Sviluppo successivo a KAB-1500Kr (~1988) | B |

---

### KAB-1500LG-Pr-E (esportazione)

**Dict Python**:
```python
"KAB-1500LG-Pr-E": {
    "type": "Guided bombs",
    "model": "KAB-1500LG-Pr-E",
    "users": ["Russia", "Syria", "Iran", "North Korea"],
    "task": ["Strike"],
    "start_service": 1998,
    "end_service": None,
    "cost": 43,  # k$, stima: variante esportazione +2%, B
    "warhead": 667,  # kg
    # release: identica a KAB-1500LG-Pr. Confidenza M/B.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 600,  # m AGL
        'max_altitude': 10000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1150,  # km/h
        'dive_angle': (0, 50),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.05,
    "efficiency": {
        # Identica a KAB-1500LG-Pr
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.6},
            "med": {"accuracy": 1, "destroy_capacity": 0.65},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.7}
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.55},
            "med": {"accuracy": 1, "destroy_capacity": 0.6},
            "small": {"accuracy": 0.9, "destroy_capacity": 0.65}
        },
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1.2},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.2},
            "small": {"accuracy": 0.65, "destroy_capacity": 1.1}
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.2}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 1},
            "med": {"accuracy": 0.75, "destroy_capacity": 1.1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.2}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'KAB-1500LG-Pr-E': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 667 | Stessa carica della FAB-1500 | A |
| users | Russia, Syria, Iran, North Korea | Rosoboronexport (varianti esportazione storiche) | B |
| min/max_altitude (m) | 600/10000 | Identica a KAB-1500LG-Pr | B |
| cost (k$) | 43 | Stima: variante esportazione +2% rispetto versione domestica | B |
| start_service | 1998 | Probabilmente posteriore alla versione domestica ~1995 | B |

---

## 2. Bombe Guidate Cinesi

### LS-6 (500 kg, JDAM cinese)

**Dict Python**:
```python
"LS-6": {
    "type": "Guided bombs",
    "model": "LS-6",
    "users": ["China", "Pakistan"],
    "task": ["Strike"],
    "start_service": 2008,
    "end_service": None,
    "cost": 18,  # k$, stima: GPS cinese inerziale, meno costosa della JDAM occidentale, B
    "warhead": 250,  # kg, testata HE da bomba standard 500 kg
    # release: Confidenza B: nessun dato primario trovato. Stima per analogia con GBU-12 (Mk-82)
    # e JDAM. LS-6 e' supportata da J-10, JF-17, J-16 come bomba da attacco al suolo.
    # Minima stima come GBU-12 (450 m), GPS non riduce il volume di schegge.
    # Massima: JDAM da media quota, ~7500 m operativo.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 450,  # m AGL, analogia JDAM/GBU-12, B
        'max_altitude': 7500,  # m, stima media-quota JDAM cinese, B
        'min_speed': 400,  # km/h, stima per velivoli cinesi meno veloci, B
        'max_speed': 1100,  # km/h, conservativa per aviazione cinese, B
        'dive_angle': (0, 45),  # gradi, analogia JDAM, B
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.08,
    "efficiency": {
        # Analogia JDAM: precisione media-alta, non eccellente come Paveway III.
        "Structure": {
            "big": {"accuracy": 0.95, "destroy_capacity": 0.5},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.55},
            "small": {"accuracy": 0.85, "destroy_capacity": 0.6}
        },
        "Bridge": {
            "big": {"accuracy": 0.95, "destroy_capacity": 0.45},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.5},
            "small": {"accuracy": 0.85, "destroy_capacity": 0.55}
        },
        "Soft": {
            "big": {"accuracy": 0.8, "destroy_capacity": 1},
            "med": {"accuracy": 0.7, "destroy_capacity": 1},
            "small": {"accuracy": 0.6, "destroy_capacity": 1}
        },
        "Armored": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.7},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.9}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.7},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.9}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'LS-6': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 250 | Stima: bomba 500 kg con ~50% carica, analogia Mk-82 (92 kg su ~244 kg totale) | B |
| min_altitude (m) | 450 | Analogia JDAM (GBU-12 su Mk-82), no dati primari | B |
| max_altitude (m) | 7500 | Stima: GPS cinese meno sofisticato della JDAM USA, minore max_alt | B |
| min_speed (km/h) | 400 | Stima: aviazione cinese piu' lenta della NATO | B |
| max_speed (km/h) | 1100 | Stima conservativa, B |
| dive_angle (gradi) | (0, 45) | Analogia JDAM | B |
| cost (k$) | 18 | Stima: GPS cinese meno costoso di JDAM USA, B |
| start_service | 2008 | Primo impiego operativo in Cina (letteratura secondaria) | B |

---

### LS-6-100 (100 kg, versione leggera)

**Dict Python**:
```python
"LS-6-100": {
    "type": "Guided bombs",
    "model": "LS-6-100",
    "users": ["China"],
    "task": ["Strike"],
    "start_service": 2010,
    "end_service": None,
    "cost": 10,  # k$, stima: proporzionale al peso 100 kg, B
    "warhead": 50,  # kg, stima: ~50% carica come famiglia LS-6
    # release: Confidenza B: stima per analogia con LS-6 base. Bomba piu' leggera, minimo ridotto.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 300,  # m AGL, stima §0.2 per carica 50 kg ~ FAB-50 (270 m), B
        'max_altitude': 8000,  # m, stima: bomba leggera piu' agile, B
        'min_speed': 350,  # km/h, stima per velivoli leggeri, B
        'max_speed': 1100,  # km/h, analogia famiglia, B
        'dive_angle': (0, 45),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.08,
    "efficiency": {
        # Testata ridotta, efficienza inferiore a LS-6, superiore a munizioni dumb.
        "Structure": {
            "big": {"accuracy": 0.95, "destroy_capacity": 0.3},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.35},
            "small": {"accuracy": 0.85, "destroy_capacity": 0.4}
        },
        "Bridge": {
            "big": {"accuracy": 0.95, "destroy_capacity": 0.25},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.3},
            "small": {"accuracy": 0.85, "destroy_capacity": 0.35}
        },
        "Soft": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.6, "destroy_capacity": 0.9}
        },
        "Armored": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.4},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.6}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.4},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.6}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'LS-6-100': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 50 | Stima: 50% di 100 kg totale, analogia famiglia | B |
| min_altitude (m) | 300 | Stima §0.2: carica 50 kg ~ FAB-50 (270 m), B |
| max_altitude (m) | 8000 | Stima: bomba leggera ha envelope piu' agile, B |
| cost (k$) | 10 | Stima proporzionale al peso (LS-6 500kg=18k$, ratio ~1.8x), B |
| start_service | 2010 | Posteriore a LS-6 base (2008) | B |

---

### LS-6-250 (250 kg, versione media)

**Dict Python**:
```python
"LS-6-250": {
    "type": "Guided bombs",
    "model": "LS-6-250",
    "users": ["China"],
    "task": ["Strike"],
    "start_service": 2009,
    "end_service": None,
    "cost": 14,  # k$, stima: intermedia tra LS-6-100 e LS-6, B
    "warhead": 125,  # kg, stima 250 kg * 50%
    # release: Confidenza B: stima per analogia con LS-6, bomba media. Minimo tra LS-6-100 e LS-6.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 375,  # m AGL, stima §0.2 per carica 125 kg, interpolata tra 300 e 450, B
        'max_altitude': 7750,  # m, stima intermedia
        'min_speed': 375,  # km/h, stima intermedia
        'max_speed': 1100,  # km/h
        'dive_angle': (0, 45),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.08,
    "efficiency": {
        # Efficienza intermedia.
        "Structure": {
            "big": {"accuracy": 0.95, "destroy_capacity": 0.4},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.45},
            "small": {"accuracy": 0.85, "destroy_capacity": 0.5}
        },
        "Bridge": {
            "big": {"accuracy": 0.95, "destroy_capacity": 0.35},
            "med": {"accuracy": 0.95, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.85, "destroy_capacity": 0.45}
        },
        "Soft": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.9},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.6, "destroy_capacity": 0.95}
        },
        "Armored": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.55},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.65},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.75}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.55},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.65},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.75}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'LS-6-250': {'precision': [_wae.PRECISION], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 125 | Stima 250 kg * 50%, B |
| min_altitude (m) | 375 | Stima §0.2 interpolata tra LS-6-100 e LS-6, B |
| max_altitude (m) | 7750 | Stima intermedia, B |
| cost (k$) | 14 | Stima intermedia tra LS-6-100 (10) e LS-6 (18), B |
| start_service | 2009 | Stima posteriore a LS-6 (2008) | B |

---

## 3. Bombe Non Guidate Russe

### OFAB-100-120 (bomba HE standard 120 kg)

**Dict Python**:
```python
"OFAB-100-120": {
    "type": "Bombs",
    "model": "OFAB-100-120",
    "users": ["USSR", "Russia", "India", "Syria", "Iraq"],
    "task": ["Strike"],
    "start_service": 1960,
    "end_service": None,
    "cost": 1.2,  # k$, stima: bomba piccola standard, B
    "warhead": 60,  # kg HE, stima: bomba 120 kg ~ 50% carica (FAB-100 = 39 kg)
    # release: Confidenza B: nessun dato primario. OFAB = General Purpose Fragmentation.
    # Stima per analogia con FAB-100 (39 kg), minimo §0.2 = 330 m.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 330,  # m AGL, stima §0.2 per carica ~60 kg, B
        'max_altitude': 12000,  # m, analogia FAB-100
        'min_speed': 500,  # km/h, famiglia sovietica
        'max_speed': 1150,  # km/h, famiglia sovietica
        'dive_angle': (0, 60),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Analoga a FAB-100: anti-personale/soft target.
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.6},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.7},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.8}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.2},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.25},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.3}
        },
        "Hard": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.15},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.18},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.2}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.25},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.3},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.35}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'OFAB-100-120': {'precision': [_wae.LOCALIZED], 'power': [_wpe.BLAST, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 60 | Stima: bomba 120 kg ~50% carica, B |
| min_altitude (m) | 330 | Stima §0.2 per carica 60 kg, B |
| max_altitude (m) | 12000 | Analogia FAB-100, B |
| min_speed (km/h) | 500 | Famiglia sovietica standard | B |
| max_speed (km/h) | 1150 | Famiglia sovietica standard | B |
| cost (k$) | 1.2 | Stima: bomba piccola standard, B |
| start_service | 1960 | Periodo sovietico standard anni '60 | B |

---

### OFAB-100-120 TU (con paracadute, freno alta resistenza)

**Dict Python**:
```python
"OFAB-100-120 TU": {
    "type": "Bombs",
    "model": "OFAB-100-120 TU",
    "users": ["USSR", "Russia", "India", "Syria"],
    "task": ["Strike"],
    "start_service": 1965,
    "end_service": None,
    "cost": 1.5,  # k$, stima: paracadute aumenta il costo 20%, B
    "warhead": 60,  # kg
    # release: Confidenza M: variante TU = paracadute. Stima per analogia con Mk-82AIR.
    # Minimo bassissimo (paracadute), massimo ridotto (paracadute perde senso sopra 1500 m).
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 50,  # m AGL, stima: paracadute consente bassissima quota, B
        'max_altitude': 1500,  # m, analogia Mk-82AIR
        'min_speed': 450,  # km/h, paracadute richiede velocita' piu' alta (forze aerodinamiche)
        'max_speed': 1000,  # km/h, limitata da paracadute
        'dive_angle': (0, 30),  # gradi, solo livellato o picchiata leggera
        'drag': 'high',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Identica a OFAB-100-120: paracadute non cambia il danno, solo il profilo di sgancio.
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.6},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.7},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.8}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.2},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.25},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.3}
        },
        "Hard": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.15},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.18},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.2}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.25},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.3},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.35}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'OFAB-100-120 TU': {'precision': [_wae.LOCALIZED], 'power': [_wpe.BLAST, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 60 | Stessa carica della OFAB-100-120 base | A |
| min_altitude (m) | 50 | Stima: paracadute consente bassissima quota, analogia Mk-82AIR (60 m), B |
| max_altitude (m) | 1500 | Analogia Mk-82AIR con paracadute | B |
| min_speed (km/h) | 450 | Stima: paracadute richiede velocita' piu' alta | B |
| max_speed (km/h) | 1000 | Limitata da paracadute | B |
| dive_angle (gradi) | (0, 30) | Stima: paracadute riduce manovra | B |
| cost (k$) | 1.5 | Stima: +20% rispetto versione base per paracadute | B |
| start_service | 1965 | Posteriore a versione base (1960) | B |

---

### OFAB-100-110TU "Jupiter" (versione migliorata, ~110 kg, variante con dispersante)

**Dict Python**:
```python
"OFAB-100-110TU": {
    "type": "Bombs",
    "model": "OFAB-100-110TU",
    "users": ["USSR", "Russia", "Syria"],
    "task": ["Strike"],
    "start_service": 1975,
    "end_service": None,
    "cost": 1.8,  # k$, stima: versione migliorata anni '70, B
    "warhead": 55,  # kg, stima: bomba 110 kg ~50% carica, leggermente meno della OFAB-100-120
    # release: Confidenza B: "Jupiter" e' uno dei nomi comuni per OFAB-100-110TU (anche KAB-100).
    # Variante con paracadute, envelope simile a OFAB-100-120 TU. "TU" = paracadute.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 50,  # m AGL, paracadute
        'max_altitude': 1500,  # m
        'min_speed': 450,  # km/h
        'max_speed': 1000,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'high',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Leggera variante della OFAB-100-120 TU.
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.58},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.68},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.78}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.19},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.24},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.29}
        },
        "Hard": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.14},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.17},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.19}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.24},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.29},
            "small": {"accuracy": 0.65, "destroy_capacity": 0.34}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'OFAB-100-110TU': {'precision': [_wae.LOCALIZED], 'power': [_wpe.BLAST, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 55 | Stima: bomba 110 kg ~50% carica, B |
| min_altitude (m) | 50 | Paracadute, analogia OFAB-100-120 TU | B |
| max_altitude (m) | 1500 | Paracadute, analogia OFAB-100-120 TU | B |
| cost (k$) | 1.8 | Stima: versione migliorata anni '70, +50% rispetto base, B |
| start_service | 1975 | Sviluppo anni '70 sovietico | B |

---

### OFAB-250-270 (bomba HE 270 kg)

**Dict Python**:
```python
"OFAB-250-270": {
    "type": "Bombs",
    "model": "OFAB-250-270",
    "users": ["USSR", "Russia", "India", "Syria", "Iraq"],
    "task": ["Strike"],
    "start_service": 1965,
    "end_service": None,
    "cost": 2.5,  # k$, stima: bomba media standard, B
    "warhead": 135,  # kg, stima: 270 kg ~50% carica
    # release: Confidenza B: nessun dato primario. Stima per analogia con FAB-250M54 (94 kg carica).
    # Minimo §0.2 per carica 135 kg → 480 m (stima conservativa).
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 480,  # m AGL, stima §0.2 per 135 kg, B
        'max_altitude': 12000,  # m, analogia famiglia FAB
        'min_speed': 500,  # km/h
        'max_speed': 1180,  # km/h
        'dive_angle': (0, 60),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Analoga a FAB-250: tra FAB-100 e FAB-500.
        "Soft": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.7},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.9}
        },
        "Armored": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.3},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.5}
        },
        "Hard": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.2},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.25},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.3}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.35},
            "med": {"accuracy": 0.75, "destroy_capacity": 0.45},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.55}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'OFAB-250-270': {'precision': [_wae.WIDE], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 135 | Stima: bomba 270 kg ~50% carica, B |
| min_altitude (m) | 480 | Stima §0.2 per carica 135 kg, B |
| max_altitude (m) | 12000 | Analogia famiglia FAB, B |
| cost (k$) | 2.5 | Stima proporzionale al peso, B |
| start_service | 1965 | Periodo sovietico standard | B |

---

### ODAB-500PM (bomba aerosol, 525 kg con paracadute)

**Dict Python**:
```python
"ODAB-500PM": {
    "type": "Bombs",
    "model": "ODAB-500PM",
    "users": ["USSR", "Russia", "Syria", "Iraq"],
    "task": ["Strike"],
    "start_service": 1985,
    "end_service": None,
    "cost": 8,  # k$, stima: bomba speciale aerosol, piu' cara della FAB-500, B
    "warhead": 300,  # kg, stima: carica esplosivo aerosol (ossido di alluminio sospeso)
    # release: Confidenza B: ODAB = bomba dispersive thermobaric (vacuum bomb).
    # Paracadute per dispersione e ritardo detonazione. Minimo molto basso (paracadute).
    # Massimo basso (dispersione ottimale a quota media-bassa).
    # Velocita' limitata da paracadute.
    "release": {
        'modes': ['level'],  # solo sgancio livellato; paracadute non ammette picchiata
        'min_altitude': 200,  # m AGL, stima: paracadute con ritardo, piu' basso di FAB-500, B
        'max_altitude': 2000,  # m, stima: dispersione ottimale a quota media-bassa, B
        'min_speed': 400,  # km/h, paracadute richiede velocita' non troppo alta
        'max_speed': 900,  # km/h, paracadute limita molto
        'dive_angle': None,  # nessuna picchiata ammessa
        'drag': 'high',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.15,  # variabilita' maggiore per questo tipo di arma (effetti meteorologici)
    "efficiency": {
        # Bomba a effetto d'area, anti-soft target. Efficacia limitata su bersagli corazzati/fissi.
        "Soft": {
            "big": {"accuracy": 0.9, "destroy_capacity": 1.5},  # effetto massivo su aree soft
            "med": {"accuracy": 0.85, "destroy_capacity": 2},
            "small": {"accuracy": 0.8, "destroy_capacity": 2.5}
        },
        "Armored": {
            "big": {"accuracy": 0.6, "destroy_capacity": 0.3},  # termobarica non penetra
            "med": {"accuracy": 0.5, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.4, "destroy_capacity": 0.5}
        },
        "Hard": {
            "big": {"accuracy": 0.5, "destroy_capacity": 0.1},
            "med": {"accuracy": 0.4, "destroy_capacity": 0.15},
            "small": {"accuracy": 0.3, "destroy_capacity": 0.2}
        },
        "Structure": {
            "big": {"accuracy": 0.8, "destroy_capacity": 0.3},  # effetto su strutture limita
            "med": {"accuracy": 0.75, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.5}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'ODAB-500PM': {'precision': [_wae.WIDE], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 300 | Stima: 525 kg totali, ~57% carica esplosiva aerosol, B |
| min_altitude (m) | 200 | Stima: paracadute + ritardo detonazione, B |
| max_altitude (m) | 2000 | Stima: effetto dispersione aerosol ottimale a media-bassa quota, B |
| min_speed (km/h) | 400 | Stima: paracadute richiede velocita' minima controllata | B |
| max_speed (km/h) | 900 | Stima: paracadute limita molto la velocita' | B |
| dive_angle | None | Nessuna picchiata ammessa (paracadute) | B |
| cost (k$) | 8 | Stima: bomba speciale, piu' cara di FAB-500 (3-4 k$), B |
| start_service | 1985 | Sviluppo anni '80 periodo sovietico tardivo | B |

---

## 4. Bombe Mk-84 Varianti Coda Frenante (USA)

### Mk-84 AIR GP HD (General Purpose, High Drag)

**Dict Python**:
```python
"Mk-84 AIR GP HD": {
    "type": "Bombs",
    "model": "Mk-84 AIR GP HD",
    "users": ["USA", "UK", "Italy"],
    "task": ["Strike", "Anti_Ship"],
    "start_service": 1965,
    "end_service": None,
    "cost": 5.5,  # k$, stima: +25% rispetto Mk-84 base per ballute, B
    "warhead": 429,  # kg
    # release: Confidenza M: variante con ballute (BSU-50 AIR) della Mk-84 base.
    # Envelope simile a Mk-82AIR ma per bomba piu' pesante. Min piu' alto (Mk-82AIR ~ 60 m con ballute,
    # Mk-84 maggior peso richiede piu' spazio di frenatura). Stima conservativa: 90 m.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 90,  # m AGL, stima: Mk-84 piu' pesante di Mk-82AIR (60 m), B
        'max_altitude': 2000,  # m, limitato da ballute; Mk-82AIR ~ 1500 m, Mk-84 un po' piu' alta, B
        'min_speed': 520,  # km/h, come Mk-82AIR (FMU-139 min 280 KCAS)
        'max_speed': 1300,  # km/h, come Mk-82AIR
        'dive_angle': (0, 30),  # gradi, solo livellato/picchiata leggera con ballute
        'drag': 'high',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Efficienza identica a Mk-84 base: il danno non cambia, solo il profilo di sgancio.
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.95},
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
            "med": {"accuracy": 0.8, "destroy_capacity": 1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1},
        },
        "Hard": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.65},
            "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.8},
        },
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.9, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.8, "destroy_capacity": 1},
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
            "med": {"accuracy": 0.8, "destroy_capacity": 1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1},
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.7},
            "med": {"accuracy": 0.9, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.8, "destroy_capacity": 0.9},
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'Mk-84 AIR GP HD': {'precision': [_wae.WIDE], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 429 | Stessa carica della Mk-84 base | A |
| min_altitude (m) | 90 | Stima: Mk-84 piu' pesante di Mk-82AIR (60 m), richiede piu' spazio frenatura, B |
| max_altitude (m) | 2000 | Stima: ballute limite operativo Mk-82AIR ~1500 m, Mk-84 un po' piu' alta | B |
| min_speed (km/h) | 520 | Identica a Mk-82AIR (FMU-139 min 280 KCAS = ~519 km/h) [F3] | M |
| max_speed (km/h) | 1300 | Identica a Mk-82AIR [F3] | M |
| dive_angle (gradi) | (0, 30) | Analogia Mk-82AIR (ballute limitano manovra) | B |
| cost (k$) | 5.5 | Stima: +25% rispetto Mk-84 base (4.4) per ballute BSU-50 | B |
| start_service | 1965 | BSU-50 sviluppato per Mk-82AIR, applicato a Mk-84 successivamente | B |

---

### Mk-84 AIR TP HD (Thermally Protected, High Drag)

**Dict Python**:
```python
"Mk-84 AIR TP HD": {
    "type": "Bombs",
    "model": "Mk-84 AIR TP HD",
    "users": ["USA", "UK"],
    "task": ["Strike", "Anti_Ship"],
    "start_service": 1975,
    "end_service": None,
    "cost": 6.5,  # k$, stima: +50% rispetto Mk-84 base per protezione termica + ballute, B
    "warhead": 429,  # kg
    # release: Confidenza B: variante con ballute + rivestimento termico (scudo calore per resistenza).
    # Envelope identica a Mk-84 AIR GP HD: il rivestimento non muta la balistica.
    "release": {
        'modes': ['level', 'dive'],
        'min_altitude': 90,  # m AGL, come Mk-84 AIR GP HD
        'max_altitude': 2000,  # m, come Mk-84 AIR GP HD
        'min_speed': 520,  # km/h, come Mk-84 AIR GP HD
        'max_speed': 1300,  # km/h, come Mk-84 AIR GP HD
        'dive_angle': (0, 30),  # gradi, come Mk-84 AIR GP HD
        'drag': 'high',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Identica a Mk-84 AIR GP HD: rivestimento termico non cambia il danno a impatto.
        "Soft": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.95},
        },
        "Armored": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
            "med": {"accuracy": 0.8, "destroy_capacity": 1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1},
        },
        "Hard": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.65},
            "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
            "small": {"accuracy": 0.7, "destroy_capacity": 0.8},
        },
        "Structure": {
            "big": {"accuracy": 1, "destroy_capacity": 0.8},
            "med": {"accuracy": 0.9, "destroy_capacity": 0.9},
            "small": {"accuracy": 0.8, "destroy_capacity": 1},
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
            "med": {"accuracy": 0.8, "destroy_capacity": 1},
            "small": {"accuracy": 0.7, "destroy_capacity": 1},
        },
        "Bridge": {
            "big": {"accuracy": 1, "destroy_capacity": 0.7},
            "med": {"accuracy": 0.9, "destroy_capacity": 0.8},
            "small": {"accuracy": 0.8, "destroy_capacity": 0.9},
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'Mk-84 AIR TP HD': {'precision': [_wae.WIDE], 'power': [_wpe.BLAST, _wpe.HIGH_EXPLOSIVE, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| warhead (kg) | 429 | Stessa carica della Mk-84 | A |
| min_altitude (m) | 90 | Identica a Mk-84 AIR GP HD | B |
| max_altitude (m) | 2000 | Identica a Mk-84 AIR GP HD | B |
| min_speed (km/h) | 520 | Identica a Mk-84 AIR GP HD | B |
| max_speed (km/h) | 1300 | Identica a Mk-84 AIR GP HD | B |
| cost (k$) | 6.5 | Stima: +50% rispetto Mk-84 base per protezione termica aggiuntiva | B |
| start_service | 1975 | Sviluppo anni '70 per resistenza termica (rientri, ambiente caldo) | B |

---

## 5. Bombe a Grappolo Russe (Submunizioni Specificate)

### RBK-250 PTAB-2.5M (250 kg, anticarro)

**Dict Python**:
```python
"RBK-250 PTAB-2.5M": {
    "type": "Cluster bombs",
    "model": "RBK-250 PTAB-2.5M",
    "users": ["USSR", "Russia", "India", "Syria", "Iraq"],
    "task": ["Strike"],
    "start_service": 1970,
    "end_service": None,
    "cost": 16,  # k$, stima: analoga a RBK-250AO, B
    "weight": 250,  # kg
    # release: Confidenza M/B: dato [F21] nel documento Proposta_Dati_Rilascio_Bombe.md.
    # PTAB-2.5M = Protivotankovaya (anticarro) + calibro 2.5 cm. ~32-40 submunizioni anticarro carica cava.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 250,  # m AGL, come RBK-250AO
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1400,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Anticarro: efficienza alta su corazzati, bassa su soft.
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 2.5},  # lievemente piu' alta di RBK-250AO
            "med": {"accuracy": 0.7, "destroy_capacity": 3.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 4.5}
        },
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 1.5},  # meno efficace su soft
            "med": {"accuracy": 0.7, "destroy_capacity": 2},
            "small": {"accuracy": 0.65, "destroy_capacity": 2.5}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 4},  # molto piu' alta su corazzati
            "med": {"accuracy": 0.8, "destroy_capacity": 5.5},
            "small": {"accuracy": 0.7, "destroy_capacity": 7}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-250 PTAB-2.5M': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.PENETRATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 250 | RBK-250 standard [F21] | A |
| min_altitude (m) | 250 | RBK-250 PTAB-2.5M [F21] da Proposta_Dati_Rilascio_Bombe.md §4 | M |
| max_altitude (m) | 5000 | Stima analogia RBK-250 generale | B |
| min_speed (km/h) | 500 | RBK-250 PTAB-2.5M [F21] | M |
| max_speed (km/h) | 1400 | RBK-250 PTAB-2.5M [F21] | M |
| dive_angle (gradi) | (0, 30) | RBK-250 PTAB-2.5M [F21] | M |
| cost (k$) | 16 | Stima: analogia RBK-250AO | B |
| start_service | 1970 | Periodo di sviluppo sovietico standard | B |
| submunizioni | ~32-40 PTAB-2.5M | mass-destruction-weapon.blogspot.com (numero stimato, non confermato) | B |

---

### RBK-250 ZAB-2.5 (incendiaria, dispenser per bombe incendiarie)

**Dict Python**:
```python
"RBK-250 ZAB-2.5": {
    "type": "Cluster bombs",
    "model": "RBK-250 ZAB-2.5",
    "users": ["USSR", "Russia", "Syria", "Iraq"],
    "task": ["Strike"],
    "start_service": 1972,
    "end_service": None,
    "cost": 12,  # k$, stima: bomba incendiaria meno costosa dell'anticarro, B
    "weight": 250,  # kg
    # release: Confidenza B: stima per analogia con RBK-250 generale. ZAB = Zaporivayushchaya (incendiaria).
    # ~180-200 bomblet incendiari da ~1 kg. Envelope simile a RBK-250 general purpose.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 250,  # m AGL, come RBK-250
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1400,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.15,  # variabilita' maggiore per effetti incendiari (vento, umidita')
    "efficiency": {
        # Incendiaria: anti-soft/infrastruttura, inefficace su corazzati.
        "Soft": {
            "big": {"accuracy": 0.7, "destroy_capacity": 5},  # alta efficacia su soft (fuoco)
            "med": {"accuracy": 0.65, "destroy_capacity": 7},
            "small": {"accuracy": 0.6, "destroy_capacity": 9}
        },
        "Armored": {
            "big": {"accuracy": 0.4, "destroy_capacity": 0.3},  # poco efficace
            "med": {"accuracy": 0.35, "destroy_capacity": 0.4},
            "small": {"accuracy": 0.3, "destroy_capacity": 0.5}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.5, "destroy_capacity": 1.5},  # moderate on AD
            "med": {"accuracy": 0.45, "destroy_capacity": 2},
            "small": {"accuracy": 0.4, "destroy_capacity": 2.5}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-250 ZAB-2.5': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 250 | RBK-250 standard | A |
| min_altitude (m) | 250 | Analogia RBK-250 generale | B |
| max_altitude (m) | 5000 | Analogia RBK-250 generale | B |
| min_speed (km/h) | 500 | Analogia RBK-250 generale | B |
| max_speed (km/h) | 1400 | Analogia RBK-250 generale | B |
| cost (k$) | 12 | Stima: incendiaria meno costosa dell'anticarro | B |
| start_service | 1972 | Sviluppo sovietico incendiaria anni '70 | B |
| submunizioni | ~180-200 ZAB-2.5 | Stima per numero (Fenix Insight METIS) | B |

---

### RBK-250-275 AO-1SCh (frammentazione, 150 submunizioni)

**Dict Python**:
```python
"RBK-250-275 AO-1SCh": {
    "type": "Cluster bombs",
    "model": "RBK-250-275 AO-1SCh",
    "users": ["USSR", "Russia", "Syria", "Iraq"],
    "task": ["Strike"],
    "start_service": 1980,
    "end_service": None,
    "cost": 15,  # k$, stima: frammentazione standard, B
    "weight": 250,  # kg
    # release: Confidenza M: già nel registro come RBK-250AO (vedere commento anomalia A3 in Proposta_Dati_Rilascio_Bombe.md).
    # AO-1SCh = Antiobshyego Naznacheniya (general purpose fragment). 150 submunizioni a frammentazione/scoppio.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 250,  # m AGL, come RBK-250
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1400,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Frammentazione general purpose: come RBK-250AO del registro.
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 2},
            "med": {"accuracy": 0.7, "destroy_capacity": 3},
            "small": {"accuracy": 0.65, "destroy_capacity": 4}
        },
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 3.2},
            "med": {"accuracy": 0.7, "destroy_capacity": 4.3},
            "small": {"accuracy": 0.65, "destroy_capacity": 7.5}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 0.3},
            "med": {"accuracy": 0.7, "destroy_capacity": 0.6},
            "small": {"accuracy": 0.65, "destroy_capacity": 1.0}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-250-275 AO-1SCh': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 250 | RBK-250 standard | A |
| submunizioni | 150 AO-1SCh | METIS/Fenix Insight, Brown Moses (cluster munitions Syrian civil war) | M |
| min_altitude (m) | 250 | RBK-250 standard | A |
| max_altitude (m) | 5000 | RBK-250 standard | A |
| cost (k$) | 15 | Stima: frammentazione standard | B |
| start_service | 1980 | Sviluppo sovietico anni '80 | B |

---

### RBK-250 ShOAB-0.5 (submunizioni speciali, variante moderna)

**Dict Python**:
```python
"RBK-250 ShOAB-0.5": {
    "type": "Cluster bombs",
    "model": "RBK-250 ShOAB-0.5",
    "users": ["Russia"],
    "task": ["Strike"],
    "start_service": 1995,
    "end_service": None,
    "cost": 18,  # k$, stima: submunizioni speciali moderne, B
    "weight": 250,  # kg
    # release: Confidenza B: nessun dato primario. ShOAB = Slozhnotargetovaya Aviacionnaya Bomba (multi-purpose air bomb).
    # Submunizioni speciali, variante moderna (anni '90). Stima: 60-80 submunizioni di tipo ibrido.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 250,  # m AGL, come RBK-250
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 1400,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.12,
    "efficiency": {
        # Multi-purpose: efficienza bilanciata su piu' target.
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 3.5},
            "med": {"accuracy": 0.7, "destroy_capacity": 4.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 6}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 1.5},
            "med": {"accuracy": 0.7, "destroy_capacity": 2},
            "small": {"accuracy": 0.65, "destroy_capacity": 3}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 2.3},
            "med": {"accuracy": 0.7, "destroy_capacity": 3},
            "small": {"accuracy": 0.65, "destroy_capacity": 4}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-250 ShOAB-0.5': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 250 | RBK-250 standard | A |
| submunizioni | ~60-80 ShOAB-0.5 | Stima per enciclopedie secondarie (numero non verificato) | B |
| min_altitude (m) | 250 | Analogia RBK-250 generale | B |
| max_altitude (m) | 5000 | Analogia RBK-250 generale | B |
| cost (k$) | 18 | Stima: submunizioni moderne speciali | B |
| start_service | 1995 | Sviluppo anni '90 russo post-Guerra Fredda | B |

---

### RBK-500 ShOAB-0.5 (versione 500 kg, submunizioni speciali)

**Dict Python**:
```python
"RBK-500 ShOAB-0.5": {
    "type": "Cluster bombs",
    "model": "RBK-500 ShOAB-0.5",
    "users": ["Russia"],
    "task": ["Strike"],
    "start_service": 1995,
    "end_service": None,
    "cost": 22,  # k$, stima: proporzionale al peso, B
    "weight": 500,  # kg
    # release: Confidenza B: stima per analogia con RBK-500 generale. ShOAB versione 500 kg.
    # Submunizioni speciali, stessa generazione di RBK-250 ShOAB-0.5 ma raddoppiato.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 300,  # m AGL, come RBK-500
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 2300,  # km/h, limite RBK-500
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.12,
    "efficiency": {
        # Multi-purpose: efficienza alta su soft, moderata su armored/AD.
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 5},
            "med": {"accuracy": 0.7, "destroy_capacity": 6.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 8}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 2},
            "med": {"accuracy": 0.7, "destroy_capacity": 2.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 4}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 3},
            "med": {"accuracy": 0.7, "destroy_capacity": 4},
            "small": {"accuracy": 0.65, "destroy_capacity": 5}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-500 ShOAB-0.5': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 500 | RBK-500 standard | A |
| submunizioni | ~120-160 ShOAB-0.5 | Stima raddoppiata rispetto RBK-250 | B |
| min_altitude (m) | 300 | RBK-500 standard | A |
| max_altitude (m) | 5000 | RBK-500 standard | A |
| cost (k$) | 22 | Stima proporzionale al peso | B |
| start_service | 1995 | Stessa generazione di RBK-250 ShOAB-0.5 | B |

---

### RBK-500 SPBE-D (anticarro autoguidato, dispenser avanzato)

**Dict Python**:
```python
"RBK-500 SPBE-D": {
    "type": "Cluster bombs",
    "model": "RBK-500 SPBE-D",
    "users": ["Russia"],
    "task": ["Strike", "Anti_Ship"],
    "start_service": 2000,
    "end_service": None,
    "cost": 35,  # k$, stima: submunizioni autoguidate molto costose, B
    "weight": 500,  # kg
    # release: Confidenza M/B: SPBE-D = Smart-seeking anti-armour submunitions. Versione avanzata di RBK-500
    # con sensori IR autoguidati (cercare bersagli tramite firma termica durante la caduta).
    # ~30-40 submunizioni anticarro autoguidate. Envelope simile a RBK-500 generale.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 300,  # m AGL, come RBK-500; submunizioni autoguidate scendono da questa quota
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 2300,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Anticarro autoguidato: altissima efficacia su corazzati, bassa su soft.
        "Soft": {
            "big": {"accuracy": 0.8, "destroy_capacity": 1},  # meno efficace su soft
            "med": {"accuracy": 0.75, "destroy_capacity": 1.2},
            "small": {"accuracy": 0.7, "destroy_capacity": 1.5}
        },
        "Armored": {
            "big": {"accuracy": 0.9, "destroy_capacity": 6},  # altissima efficacia
            "med": {"accuracy": 0.85, "destroy_capacity": 8},
            "small": {"accuracy": 0.8, "destroy_capacity": 10}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.85, "destroy_capacity": 5},
            "med": {"accuracy": 0.8, "destroy_capacity": 6.5},
            "small": {"accuracy": 0.75, "destroy_capacity": 8}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-500 SPBE-D': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.PENETRATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 500 | RBK-500 standard | A |
| submunizioni | ~30-40 SPBE-D autoguidate | GlobalSecurity / METIS (numero stimato) | B |
| min_altitude (m) | 300 | RBK-500 standard | A |
| max_altitude (m) | 5000 | RBK-500 standard | A |
| min_speed (km/h) | 500 | RBK-500 standard | A |
| max_speed (km/h) | 2300 | RBK-500 standard [F23] | A |
| cost (k$) | 35 | Stima: submunizioni autoguidate IR molto costose (~10x della base) | B |
| start_service | 2000 | Sviluppo russo post-2000 con guida IR | B |

---

### RBK-500-255 PTAB-10-5 (anticarro, submunizioni grandi da 10mm)

**Dict Python**:
```python
"RBK-500-255 PTAB-10-5": {
    "type": "Cluster bombs",
    "model": "RBK-500-255 PTAB-10-5",
    "users": ["Russia", "Syria"],
    "task": ["Strike"],
    "start_service": 1985,
    "end_service": None,
    "cost": 25,  # k$, stima: PTAB-10-5 sottocaliber, piu' costoso di PTAB-1M, B
    "weight": 500,  # kg
    # release: Confidenza B: nessun dato primario. PTAB-10-5 = Protivotankovaya (anticarro) carica cava
    # sottocalibro 10 mm. Submunizioni più pesanti e potenti di PTAB-2.5M. ~20-25 submunizioni.
    # Stima: envelope identico a RBK-500 generale.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 300,  # m AGL, come RBK-500
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 2300,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Anticarro pesante: altissima efficacia su corazzati.
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 4.5},
            "med": {"accuracy": 0.8, "destroy_capacity": 6},
            "small": {"accuracy": 0.7, "destroy_capacity": 8}
        },
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 1},
            "med": {"accuracy": 0.7, "destroy_capacity": 1.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 2}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 3},
            "med": {"accuracy": 0.7, "destroy_capacity": 4},
            "small": {"accuracy": 0.65, "destroy_capacity": 5}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-500-255 PTAB-10-5': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.PENETRATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 500 | RBK-500 standard | A |
| submunizioni | ~20-25 PTAB-10-5 | Stima inversamente proporzionale al peso singolo | B |
| min_altitude (m) | 300 | RBK-500 standard | A |
| max_altitude (m) | 5000 | RBK-500 standard | A |
| cost (k$) | 25 | Stima: PTAB-10-5 piu' costoso di PTAB-1M (~5x), B |
| start_service | 1985 | Sviluppo sovietico anni '80 | B |

---

### RBK-500U (versione modernizzata, carico standard)

**Dict Python**:
```python
"RBK-500U": {
    "type": "Cluster bombs",
    "model": "RBK-500U",
    "users": ["Russia", "Syria", "Iran"],
    "task": ["Strike"],
    "start_service": 1992,
    "end_service": None,
    "cost": 20,  # k$, stima: modernizzazione costi-efficace, B
    "weight": 500,  # kg
    # release: Confidenza M: "U" = Modernizovannaya (modernizzata). Versione standard aggiornata di RBK-500
    # con dispenser migliorato per affidabilità. Carico submunizioni standard (AO o PTAB scelto al montaggio).
    # Envelope identico a RBK-500 generale.
    "release": {
        'modes': ['level', 'dive', 'loft'],
        'min_altitude': 300,  # m AGL
        'max_altitude': 5000,  # m
        'min_speed': 500,  # km/h
        'max_speed': 2300,  # km/h
        'dive_angle': (0, 30),  # gradi
        'drag': 'low',
        'glide_ratio': None,
    },
    "perc_efficiency_variability": 0.1,
    "efficiency": {
        # Profilo bilanciato: puo' essere caricata con AO (general purpose) o PTAB (anticarro).
        # Qui si propone un profilo generico medio.
        "Soft": {
            "big": {"accuracy": 0.75, "destroy_capacity": 3.5},
            "med": {"accuracy": 0.7, "destroy_capacity": 4.5},
            "small": {"accuracy": 0.65, "destroy_capacity": 6}
        },
        "Armored": {
            "big": {"accuracy": 0.75, "destroy_capacity": 2},
            "med": {"accuracy": 0.75, "destroy_capacity": 3},
            "small": {"accuracy": 0.7, "destroy_capacity": 4}
        },
        "Air_Defense": {
            "big": {"accuracy": 0.75, "destroy_capacity": 2.5},
            "med": {"accuracy": 0.7, "destroy_capacity": 3.2},
            "small": {"accuracy": 0.65, "destroy_capacity": 4}
        },
    },
},
```

**Riga `_WEAPON_PARAM_TYPE`**:
```python
'RBK-500U': {'precision': [_wae.WIDE], 'power': [_wpe.CLUSTER, _wpe.FRAGMENTATION]},
```

**Tabella dati**:

| Campo | Valore | Fonte | Confidenza |
|---|---|---|---|
| weight (kg) | 500 | RBK-500 standard | A |
| submunizioni | variabili | Carico scelto al montaggio (AO o PTAB), non universale | B |
| min_altitude (m) | 300 | RBK-500 standard | A |
| max_altitude (m) | 5000 | RBK-500 standard | A |
| min_speed (km/h) | 500 | RBK-500 standard | A |
| max_speed (km/h) | 2300 | RBK-500 standard | A |
| cost (k$) | 20 | Stima: modernizzazione costi-efficace | B |
| start_service | 1992 | Modernizzazione inizi anni '90 russo | B |

---

## Riepilogo Armi Ricercate

**Totale**: 24 armi ricercate

**Per categoria**:
- Guidate russe: 5 (KAB-500Kr-OD, KAB-500S, KAB-1500Kr, KAB-1500LG-Pr, KAB-1500LG-Pr-E)
- Guidate cinesi: 3 (LS-6, LS-6-100, LS-6-250)
- Non guidate russe: 5 (OFAB-100-120, OFAB-100-120 TU, OFAB-100-110TU, OFAB-250-270, ODAB-500PM)
- USA (Mk-84 varianti): 2 (Mk-84 AIR GP HD, Mk-84 AIR TP HD)
- Cluster russe: 9 (RBK-250 PTAB-2.5M, RBK-250 ZAB-2.5, RBK-250-275 AO-1SCh, RBK-250 ShOAB-0.5, RBK-500 ShOAB-0.5, RBK-500 SPBE-D, RBK-500-255 PTAB-10-5, RBK-500U, e implicitamente RBK-250AO/RBK-500AO/RBK-500PTAB già nel registro)

---

## Dubbi Principali e Limitazioni

### Dubbi su dati mancanti (confidenza B)

1. **KAB-1500Kr/LG-Pr/E**: nessun dato primario trovato. Stime ricavate per analogia e fisica (carica cubica).
2. **LS-6 cinese**: poco documentata in fonti aperte occidentali. Stime per analogia JDAM USA.
3. **OFAB-* russe**: designazioni poco chiare in letteratura inglese. Stime per analogia con FAB e PTAB.
4. **ODAB-500PM**: bomba termobarica, effetti meteorologicamente variabili. Confidenza alta su struttura fisica, bassa su efficienza operativa.
5. **Mk-84 AIR varianti**: gli standard USA sono noti, ma il mix ballute + protezione termica non è documentato in un unico prodotto nei manuali aperti.
6. **RBK-500 SPBE-D**: submunizioni autoguidate moderne, pochissimo documentate (segretezza militare). Stime per analogia e comunicati Rosoboronexport.

### Valori interamente in confidenza B

- **KAB-1500Kr**: quasi tutti i campi
- **KAB-1500LG-Pr/E**: quasi tutti i campi
- **LS-6, LS-6-100, LS-6-250**: tutti i campi tranne warhead
- **OFAB-100-120**: tutti i campi tranne warhead standard
- **OFAB-100-120 TU / OFAB-100-110TU**: tutti i campi
- **OFAB-250-270**: quasi tutti i campi
- **ODAB-500PM**: quasi tutti i campi
- **Mk-84 AIR GP HD / TP HD**: dive_angle e cost
- **RBK-250 ShOAB-0.5 / RBK-500 ShOAB-0.5**: numero submunizioni
- **RBK-500 SPBE-D**: numero e efficienza submunizioni autoguidate
- **RBK-500-255 PTAB-10-5**: numero submunizioni, efficienza
- **RBK-500U**: designazione come "carico generico"

### Verifiche Richieste all'Utente

1. **Mk-84 AIR varianti**: Mk-84 AIR GP HD e Mk-84 AIR TP HD sono designazioni vere DCS/USA, o sono composte? Verificare se il rivestimento termico esiste come prodotto finito o come opzione di montaggio.

2. **RBK-500U**: Nel registro esiste RBK-500PTAB e RBK-500AO come voci separate. RBK-500U è una vera variante o un profilo di base montabile con carichi diversi?

3. **ODAB-500PM**: La designazione PM = "Podvisnaya Modernizovannaya" (moderna, sospeso). Verificare se in DCS è presente e come è implementata (il registro ha bombe, non pod specifici).

4. **RBK-500 SPBE-D**: Confermare se in DCS è caricabile da qualche aereo russo moderno (Su-34, Su-24, Mi-28).

---

## Note Metodologiche

Tutte le stime sono costruite per analogia usando:
1. **Regola §0.2 della Proposta**: scala della quota minima per carica esplosiva
2. **Famiglia di riferimento**: confronto con armi simili già nel registro
3. **Fonti secondarie**: ru.wikipedia, enciclopedie tecniche, Rosoboronexport comunicati (con confidenza M/B)
4. **Dati fisici**: peso, carica, data di sviluppo da fonti dichiarate

Nessun manuale d'impiego primario (AFTTP 3-3, serie -34 sovietica) è stato consultato per questa ricerca.
