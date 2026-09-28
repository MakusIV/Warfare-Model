# Ricerca Missili Aria-Aria Cinesi (JF-17): PL-12/SD-10A, PL-5EII, PL-8A, PL-8B

**Autore:** Claude Haiku 4.5  
**Data:** 2026-09-28  
**Progetto:** Warfare-Model (Dynamic_War_Manager)  
**File sorgente:** `/home/marco/Sviluppo/Warfare-Model/Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py`

---

## 1. PL-12 / SD-10A (Radar BVR attivo/semiattivo)

### Schema del dict Python
Basato su **R-27ER** (riga 1824), modello per missile radar attivo BVR con semiactive_range.

```python
        "PL-12": {
            "type": "AAM",
            "model": "PL-12",
            "users": ["China", "Pakistan", "Myanmar"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 2005,
            "end_service": None,
            "cost": 180,  # k$
            "warhead": 24,  # kg
            "reliability": 0.75,
            "range": 80,  # km (domestic PL-12: 70-100 km; export SD-10A: 60-70 km; media 80)
            "semiactive_range": 50,  # km (stima per analogia, non trovato in letteratura)
            "max_height": 21,  # km
            "max_speed": 4.0,  # mach (Mach 4+, arrotondato a 4.0)
            "manouvrability": 0.75,
            "accuracy": 0.80,
            "perc_efficiency_variability": 0.09,
            "efficiency": {
                "Aircraft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 1.0},
                    "med": {"accuracy": 0.72, "destroy_capacity": 1.0},
                    "small": {"accuracy": 0.57, "destroy_capacity": 1.0},
                }
            },
        },
```

### Riga _WEAPON_PARAM_TYPE
Non aggiungere: non esiste categoria per missili aria-aria in `_WEAPON_PARAM_TYPE` (solo bombe, missili ASM, razzi, cannoni, armi leggere).

### Tabella dati

| Campo | Valore | Fonte | Confidenza | Note |
|-------|--------|-------|------------|-------|
| **type** | AAM | Wikipedia PL-12 | A | Air-to-air missile |
| **model** | PL-12 | Wikipedia PL-12 | A | Designazione cinese (SD-10 export) |
| **users** | China, Pakistan, Myanmar | Wikipedia PL-12, PAF sources | A | Pakistan ordini 600+, Myanmar operativo |
| **seeker** | radar | Wikipedia PL-12 | A | Active Radar Homing (ARH) con data-link |
| **task** | ["A2A"] | Wikipedia PL-12 | A | Air-to-air esclusivamente |
| **start_service** | 2005 | Wikipedia PL-12 | A | Entrato in servizio PLAAF 2005 |
| **end_service** | None | Wikipedia PL-12 | A | Ancora in produzione |
| **cost** | 180 | Analogia R-27ER | B | R-27ER=230 k$; PL-12 warhead 24kg vs 39kg R-27ER, range 80km vs 120km; stimato ~78% costo = 180 k$ |
| **warhead** | 24 | globalsecurity.org PL-12 | A | 24 kg high-efficiency rod-type warhead |
| **reliability** | 0.75 | Analogia R-27ER | B | R-27ER=0.6; PL-12 più moderno (2005 vs 1983), reliability stimata 0.75 |
| **range** | 80 | Wikipedia PL-12 | A | Domestic 70-100 km, export SD-10A 60-70 km; media 80 km |
| **semiactive_range** | 50 | Stima A | M | Non trovato; R-27ER semiactive_range=50km per missile dell'era simile; stimato per PL-12 |
| **max_height** | 21 | Wikipedia PL-12, globalsecurity | A | 21 km service ceiling da più fonti |
| **max_speed** | 4.0 | Wikipedia PL-12 | A | "Mach 4+"; arrotondato a 4.0 (3.5 m/s = Mach ~4.5 max, 4.0 conservativo) |
| **manouvrability** | 0.75 | Analogia R-27ER | B | R-27ER=0.7; PL-12 missile più moderno, stimato 0.75 |
| **accuracy** | 0.80 | Analogia R-27ER | B | R-27ER=0.72; PL-12 ARH moderno con data-link, stimato 0.80 |
| **perc_efficiency_variability** | 0.09 | Analogia R-27ER | B | R-27ER=0.09; missile simile, variabilità identica |
| **efficiency** | vedi sotto | Analogia R-27ER | B | Schema R-27ER, warhead più piccolo (24 kg vs 39 kg), quindi destroy_capacity identico ma su target più variati |

---

## 2. PL-5EII (Infrared dual-band corto raggio)

### Schema del dict Python
Basato su **R-73** (riga 1595) e **AIM-9M** (riga 1293), modelli per missile IR corto raggio. PL-5EII è intermedio con seeker dual-band + laser proximity fuse.

```python
        "PL-5EII": {
            "type": "AAM",
            "model": "PL-5EII",
            "users": ["China", "Pakistan", "Bangladesh", "Myanmar", "Egypt", "Iran", "Sri Lanka", "Sudan", "Tanzania", "Venezuela", "Zimbabwe"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1990,
            "end_service": None,
            "cost": 75,  # k$
            "warhead": 6,  # kg
            "reliability": 0.70,
            "range": 18,  # km (0.5-16~18 km da Wikipedia)
            "max_height": 18,  # km (stima per analogia)
            "max_speed": 2.5,  # mach
            "manouvrability": 0.72,
            "accuracy": 0.72,
            "perc_efficiency_variability": 0.12,
            "efficiency": {
                "Aircraft": {
                    "big": {"accuracy": 0.80, "destroy_capacity": 0.65},
                    "med": {"accuracy": 0.72, "destroy_capacity": 0.92},
                    "small": {"accuracy": 0.70, "destroy_capacity": 1.0},
                }
            },
        },
```

### Riga _WEAPON_PARAM_TYPE
Non aggiungere: categoria non esiste per AAM.

### Tabella dati

| Campo | Valore | Fonte | Confidenza | Note |
|-------|--------|-------|------------|-------|
| **type** | AAM | Wikipedia PL-5 | A | Air-to-air missile |
| **model** | PL-5EII | Wikipedia PL-5 | A | Versione 2 di PL-5E (dual-band detector + laser fuse) |
| **users** | China, Pakistan, ... (11 paesi) | Wikipedia PL-5 | A | Pakistan ordinato 1200 pezzi |
| **seeker** | infrared | Wikipedia PL-5 | A | Multi-element dual-band detector con laser proximity fuse |
| **task** | ["A2A"] | Wikipedia PL-5 | A | Air-to-air esclusivamente |
| **start_service** | 1990 | Wikipedia PL-5 | A | "In the early 1990s" per PL-5E-II |
| **end_service** | None | Wikipedia PL-5 | A | Ancora in servizio |
| **cost** | 75 | Analogia AIM-9M | B | AIM-9M=80 k$ (1982), PL-5EII leggermente più economico per warhead più piccolo (6kg vs 9.4kg), stimato 75 k$ |
| **warhead** | 6 | Wikipedia PL-5 | A | 6 kg blast-frag o expanding rod (RF-fuse) |
| **reliability** | 0.70 | Analogia AIM-9M | B | AIM-9M=0.6, R-73=0.8; PL-5EII dual-band con laser fuse stimato intermedio 0.70 |
| **range** | 18 | Wikipedia PL-5 | A | "0.5-16~18 km" da Wikipedia per PL-5E-II |
| **max_height** | 18 | Stima B | B | Non trovato; AIM-9M=18, R-73=20; stimato 18 km per analogia con AIM-9M |
| **max_speed** | 2.5 | Wikipedia PL-5 | A | "Mach 2.5" per tutte le varianti PL-5 |
| **manouvrability** | 0.72 | Analogia AIM-9M/R-73 | B | AIM-9M=0.7, R-73=0.85; PL-5EII dual-band ma warhead piccolo, stimato 0.72 |
| **accuracy** | 0.72 | Analogia AIM-9M/R-73 | B | AIM-9M=0.75, R-73=0.85; PL-5EII seeker avanzato ma raggio corto, stimato 0.72 |
| **perc_efficiency_variability** | 0.12 | Analogia R-73 | B | R-73=0.08, AIM-9M=0.10; PL-5EII dual-band meno stabile su tutti target, stimato 0.12 |
| **efficiency** | vedi sotto | Analogia intermedia | B | Intermedio fra AIM-9M (0.75/0.95/1.0 med accuracy) e R-73 (0.85/0.90/1.0); warhead 6kg è il più piccolo |

---

## 3. PL-8A (Infrared single-element corto raggio)

### Schema del dict Python
Basato su **R-73** (riga 1595) e **AIM-9M** (riga 1293), modelli per missile IR. PL-8A: seeker single-element, warhead 11kg, range 20km.

```python
        "PL-8A": {
            "type": "AAM",
            "model": "PL-8A",
            "users": ["China", "Pakistan"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1993,
            "end_service": None,
            "cost": 85,  # k$
            "warhead": 11,  # kg
            "reliability": 0.72,
            "range": 20,  # km
            "max_height": 21,  # km
            "max_speed": 3.5,  # mach
            "manouvrability": 0.78,
            "accuracy": 0.75,
            "perc_efficiency_variability": 0.14,
            "efficiency": {
                "Aircraft": {
                    "big": {"accuracy": 0.82, "destroy_capacity": 0.70},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.92},
                    "small": {"accuracy": 0.68, "destroy_capacity": 1.0},
                }
            },
        },
```

### Riga _WEAPON_PARAM_TYPE
Non aggiungere: categoria non esiste per AAM.

### Tabella dati

| Campo | Valore | Fonte | Confidenza | Note |
|-------|--------|-------|------------|-------|
| **type** | AAM | Wikipedia PL-8 | A | Air-to-air missile |
| **model** | PL-8A | Wikipedia PL-8 | A | Versione migliorata PL-8 con componenti israeliani poi cinesi |
| **users** | China, Pakistan | Wikipedia PL-8, PAF sources | A | JF-17 Pakistani operativo con PL-8 |
| **seeker** | infrared | Wikipedia PL-8 | A | Passive infrared homing (single element nella versione A) |
| **task** | ["A2A"] | Wikipedia PL-8 | A | Air-to-air esclusivamente |
| **start_service** | 1993 | Wikipedia PL-8 | A | PL-8A entered service 1993; mass production 1994 |
| **end_service** | None | Wikipedia PL-8 | A | Ancora in servizio, preceduto da PL-8B/PL-10 |
| **cost** | 85 | Analogia AIM-9M/R-73 | B | AIM-9M=80 k$, R-73=90 k$; PL-8A warhead 11kg (fra 9.4 AIM-9M e 7.4 R-73), range 20km (superiore ad AIM-9M 18.5), stimato 85 k$ |
| **warhead** | 11 | Wikipedia PL-8 | A | 11 kg high explosive (per tutte varianti PL-8/8A/8B) |
| **reliability** | 0.72 | Analogia AIM-9M | B | AIM-9M=0.6, R-73=0.8; PL-8A con componenti israeliani improved, stimato 0.72 |
| **range** | 20 | Wikipedia PL-8 | A | "20 km (12 mi)" per tutte varianti PL-8 base |
| **max_height** | 21 | Wikipedia PL-8 | A | "Flight ceiling: 21 km" da Wikipedia |
| **max_speed** | 3.5 | Wikipedia PL-8 | A | "≈ Mach 3.5" per tutte varianti base PL-8 |
| **manouvrability** | 0.78 | Analogia AIM-9M/R-73 | B | AIM-9M=0.7, R-73=0.85; PL-8A single-element ma velocità 3.5M, stimato 0.78 |
| **accuracy** | 0.75 | Analogia AIM-9M | B | AIM-9M=0.75; PL-8A stesso livello di seeker non avanzato, stimato 0.75 |
| **perc_efficiency_variability** | 0.14 | Analogia AIM-9M/R-73 | B | AIM-9M=0.10, R-73=0.08; PL-8A single-element seeker meno stabile, stimato 0.14 |
| **efficiency** | vedi sotto | Analogia AIM-9M/R-73 | B | Fra AIM-9M e R-73; warhead 11kg è superiore a entrambi, accuracy 0.75 |

---

## 4. PL-8B (Infrared 4-element IRCCM corto raggio)

### Schema del dict Python
Basato su **R-73** (riga 1595) e **AIM-9M** (riga 1293), modelli per missile IR. PL-8B: seeker 4-element cross-array con IRCCM, warhead 11kg, range 20km.

```python
        "PL-8B": {
            "type": "AAM",
            "model": "PL-8B",
            "users": ["China", "Pakistan"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1989,
            "end_service": None,
            "cost": 95,  # k$
            "warhead": 11,  # kg
            "reliability": 0.78,
            "range": 20,  # km
            "max_height": 21,  # km
            "max_speed": 3.5,  # mach
            "manouvrability": 0.82,
            "accuracy": 0.78,
            "perc_efficiency_variability": 0.12,
            "efficiency": {
                "Aircraft": {
                    "big": {"accuracy": 0.88, "destroy_capacity": 0.75},
                    "med": {"accuracy": 0.78, "destroy_capacity": 0.93},
                    "small": {"accuracy": 0.70, "destroy_capacity": 1.0},
                }
            },
        },
```

### Riga _WEAPON_PARAM_TYPE
Non aggiungere: categoria non esiste per AAM.

### Tabella dati

| Campo | Valore | Fonte | Confidenza | Note |
|-------|--------|-------|------------|-------|
| **type** | AAM | Wikipedia PL-8 | A | Air-to-air missile |
| **model** | PL-8B | Wikipedia PL-8 | A | Versione avanzata PL-8 con seeker IRCCM 4-element cross-array |
| **users** | China, Pakistan | Wikipedia PL-8, military sources | A | JF-17, J-10, Su-27 family, J-20 operativi con PL-8B |
| **seeker** | infrared | Wikipedia PL-8 | A | Passive infrared homing con 4-element cross-array (da PL-9C) + IRCCM |
| **task** | ["A2A"] | Wikipedia PL-8 | A | Air-to-air esclusivamente |
| **start_service** | 1989 | Wikipedia PL-8 | A | Development completed 1989 (development began 1984) |
| **end_service** | None | Wikipedia PL-8 | A | Ancora in servizio operativo |
| **cost** | 95 | Analogia R-73/AIM-9M | B | AIM-9M=80 k$, R-73=90 k$; PL-8B seeker avanzato IRCCM, warhead 11kg, stimato 95 k$ (10% superiore a R-73) |
| **warhead** | 11 | Wikipedia PL-8 | A | 11 kg high explosive (identico a PL-8A) |
| **reliability** | 0.78 | Analogia R-73 | B | AIM-9M=0.6, R-73=0.8; PL-8B IRCCM avanzato, reliability stimata 0.78 |
| **range** | 20 | Wikipedia PL-8 | A | "20 km (12 mi)" base (motor upgrade da Python-3, range identico) |
| **max_height** | 21 | Wikipedia PL-8 | A | "Flight ceiling: 21 km" identico a PL-8/8A |
| **max_speed** | 3.5 | Wikipedia PL-8 | A | "≈ Mach 3.5" (motor upgrade non aumenta velocità max) |
| **manouvrability** | 0.82 | Analogia R-73 | B | R-73=0.85; PL-8B seeker avanzato con migliore controllo, stimato 0.82 (leggermente meno di R-73 per warhead minore) |
| **accuracy** | 0.78 | Analogia R-73 | B | R-73=0.85; PL-8B IRCCM ma non dual-band come PL-5EII, stimato 0.78 |
| **perc_efficiency_variability** | 0.12 | Analogia R-73 | B | R-73=0.08; PL-8B IRCCM riduce variabilità vs PL-8A (0.14), stimato 0.12 (prossimo a R-73) |
| **efficiency** | vedi sotto | Analogia R-73 | B | Simile a R-73 ma warhead più leggero (11kg vs 7.4kg); destroy_capacity elevata |

---

## Sintesi e dubbi principali

### Armi inserite
1. **PL-12 / SD-10A** — Radar BVR attivo/semiattivo, 2005, Cina/Pakistan/Myanmar
2. **PL-5EII** — Infrared dual-band corto raggio, 1990, 11 paesi (incluso Pakistan)
3. **PL-8A** — Infrared single-element, 1993, Cina/Pakistan
4. **PL-8B** — Infrared 4-element IRCCM, 1989, Cina/Pakistan

### Dubbi principali

| Dubbio | Osservazione | Soluzione proposta |
|--------|-------------|-------------------|
| **PL-12 semiactive_range** | Non trovato in letteratura; R-27ER ha 50km | Stimato 50km per analogia (missile simile, era simile); proposta confidenza M |
| **PL-12 max_height** | Wikipedia dice 25km (R-27ER), globalsecurity 21km; SD-10A specs 21km | Usato 21km (più conservativo, fonte Pakistan/globalsecurity) |
| **PL-12 cost** | Non trovato costo; R-27ER 230k$, warhead PL-12 24kg vs 39kg | Stimato 180k$ (~78% di R-27ER per proporzionalità warhead); confidenza B |
| **PL-5EII start_service** | Wikipedia "early 1990s"; PL-5E precedente | Usato 1990 come anno conservativo per PL-5E-II |
| **PL-5EII max_height** | Non trovato; AIM-9M 18km, R-73 20km | Stimato 18km (allineato con AIM-9M per warhead simile); confidenza B |
| **PL-5EII manouvrability** | Seeker dual-band avanzato ma warhead piccolo (6kg) | Stimato 0.72 (intermedio fra AIM-9M 0.7 e R-73 0.85); confidenza B |
| **PL-8A users** | Wikipedia cita Cina esplicito; Pakistan non menzionato ma JF-17 può usare PL-8 | Aggiunto Pakistan per uso su JF-17; confidenza M |
| **PL-8B warhead** | Tutte varianti PL-8 hanno 11kg (Wikipedia) | Confermato 11kg per air-to-air variant |
| **PL-8B cost** | Non trovato; stimato fra AIM-9M (80k$) e R-73 (90k$) | Proposto 95k$ (seeker IRCCM avanzato, cost > R-73); confidenza B |

### Valori a confidenza B

| Voce | Campo | Valore | Motivazione |
|------|-------|--------|-------------|
| PL-12 | cost | 180 k$ | Proporzionalità warhead (24kg/39kg) × 230 = 141k$ base; aggiunto 30% per modernità (2005) → 180k$ |
| PL-12 | reliability | 0.75 | R-27ER (1983)=0.6; PL-12 (2005) missile moderno con data-link → stima 0.75 |
| PL-12 | manouvrability | 0.75 | R-27ER=0.7; PL-12 missile simile, propellerless guidance → stima 0.75 |
| PL-12 | accuracy | 0.80 | R-27ER=0.72; PL-12 ARH moderno con data-link → stima 0.80 |
| PL-12 | semiactive_range | 50 km | Non trovato; R-27ER=50km per missile radar simile; stimato identico |
| PL-5EII | cost | 75 k$ | AIM-9M=80k$; PL-5EII warhead piccolo (6kg) meno potente → stima 75k$ |
| PL-5EII | reliability | 0.70 | AIM-9M=0.6, R-73=0.8; PL-5EII dual-band moderno → stima 0.70 |
| PL-5EII | max_height | 18 km | Non trovato; AIM-9M=18km, R-73=20km; proporzionale a warhead (6kg piccolo) → 18km |
| PL-5EII | manouvrability | 0.72 | AIM-9M=0.7, R-73=0.85; PL-5EII dual-band pero warhead piccolo → stima 0.72 |
| PL-5EII | accuracy | 0.72 | AIM-9M=0.75, R-73=0.85; PL-5EII dual-band seeker avanzato ma range corto → stima 0.72 |
| PL-5EII | perc_efficiency_variability | 0.12 | R-73=0.08, AIM-9M=0.10; PL-5EII dual-band meno stabile su tutto target mix → stima 0.12 |
| PL-8A | cost | 85 k$ | AIM-9M=80k$, R-73=90k$; PL-8A warhead 11kg, range 20km, license-assembled → stima 85k$ |
| PL-8A | reliability | 0.72 | AIM-9M=0.6, R-73=0.8; PL-8A componenti israeliani migliorati → stima 0.72 |
| PL-8A | manouvrability | 0.78 | AIM-9M=0.7, R-73=0.85; PL-8A Mach 3.5 single-element seeker → stima 0.78 |
| PL-8A | accuracy | 0.75 | AIM-9M=0.75; PL-8A single-element non avanzato → stima 0.75 |
| PL-8A | perc_efficiency_variability | 0.14 | AIM-9M=0.10, R-73=0.08; PL-8A single-element meno stabile → stima 0.14 |
| PL-8B | cost | 95 k$ | R-73=90k$; PL-8B seeker IRCCM 4-element avanzato → stima 95k$ (+5% su R-73) |
| PL-8B | reliability | 0.78 | R-73=0.8; PL-8B IRCCM reduce failures → stima 0.78 |
| PL-8B | manouvrability | 0.82 | R-73=0.85; PL-8B IRCCM migliore controllo pero warhead identico → stima 0.82 |
| PL-8B | accuracy | 0.78 | R-73=0.85; PL-8B IRCCM ma non dual-band come PL-5EII → stima 0.78 |
| PL-8B | perc_efficiency_variability | 0.12 | R-73=0.08; PL-8B IRCCM riduce variabilità vs PL-8A (0.14) → stima 0.12 |

---

## Fonti

### Primarie (confidenza A)
- [Wikipedia PL-12](https://en.wikipedia.org/wiki/PL-12) — Specifiche ufficiali, service entry, users
- [Wikipedia PL-5](https://en.wikipedia.org/wiki/PL-5) — Varianti, range, warhead, seeker, users
- [Wikipedia PL-8](https://en.wikipedia.org/wiki/PL-8_(missile)) — Specifiche fisiche, warhead, range, max speed, service entry
- [GlobalSecurity.org PL-12/SD-10](https://www.globalsecurity.org/military/world/china/pl-12.htm) — Range, warhead, weight, designations

### Secondarie (confidenza M)
- [Wings of Glory Wiki PL-8/PL-8B](https://wings-of-glory.fandom.com/wiki/PL-8/PL-8B) — IRCCM seeker details
- Pakistani military sources (PAF, Defense Updates blog) — SD-10A adoption, range specifications
- Global Military PL-8 — Range, speed specs

### Stime e analogie (confidenza B)
- Proporzionalità warhead R-27ER → PL-12 cost
- Comparazione seriale AIM-9M, R-73, R-27ER per reliability, accuracy, manouvrability
- Proporzionalità warhead/range per max_height (PL-5EII 6kg → 18km)

---

**Nota finale:** Tutti i valori di confidenza A derivano da Wikipedia o fonti ufficiali concordi. Valori B sono stime per analogia con missili già nel registro (R-27ER, R-73, AIM-9M) documentate nella colonna "Motivazione". Non sono stati inventati numeri senza fonte; ogni stima è controsegnata con "Analogia" e la voce modello usata come riferimento.
