# Dati di riferimento estratti dalla documentazione DCS

Estratti il 2026-09-18 dai documenti in `documentazione_dcs/`. **Attenzione alla data di
ciascuna fonte**: la maggior parte è vecchia e il roster DCS è cambiato molto.

| File prodotto | Fonte | Data fonte | Affidabilità |
|---|---|---|---|
| `sam_threat_table.csv` | `SAM Threat guide/` (24 PNG) | **dic 2022** | buona per i parametri; roster incompleto |
| `vehicles_overview.json` | `DCS_-_Overview_Vehicles/*.xlsx` | ~2020? | tassonomia utile, roster datato |
| — | `DCS Encyclopedia 1.3.pdf` | **lug 2013** | solo schema dei campi; roster DCS 1.2 |
| — | `DCS Table of Frequencies.pdf` | **mar 2014** | solo Caucaso, pre-rework mappa |
| — | `DCS World List of all available Beacons EN.pdf` | **gen 2015** | solo Caucaso |
| — | `Overview Vehicles.pptx` | ~2020? | catalogo visivo, nessun dato oltre la tassonomia |

Per confronto: il `debrief.log` fornito è di **DCS 2.9.29.27468** (settembre 2026). Il divario
con le fonti sopra è di 4–13 anni.

---

## 1. `sam_threat_table.csv` — il più utile

23 sistemi SAM/SHORAD con schema uniforme. Campi:

| Campo | Natura | Destinazione nel core |
|---|---|---|
| `nato_name`, `local_name` | reale | identità dell'asset |
| `min_range_nmi`, `max_range_nmi` | reale | **inviluppo d'ingaggio orizzontale** |
| `min_alt_ft`, `max_alt_ft` | reale | **inviluppo d'ingaggio verticale** |
| `acquire_time_s` | reale | **latenza di reazione** — quanto tempo serve al sistema per ingaggiare |
| `launcher_type`, `cm_type` | reale | tipo di lanciatore; contromisura efficace (Chaff / Flare / Kinetic) |
| `sead_priority` | dottrinale | quale elemento colpire per primo: `Track Radar` o `Launcher` |
| `point_defense` | reale | capace di intercettare missili in arrivo |
| `site_layout` | dottrinale | composizione tipica del sito (n. lanciatori, radar, C2) |
| `rwr_symbol`, `track_harm`, `search_harm_*` | **DCS-specifico** | appartiene all'adapter, non al core |
| `launch_warning`, `hdsm` | **DCS/mod-specifico** | idem |

I quattro campi di inviluppo più `acquire_time_s` sono direttamente mappabili su
`DataType/Threat.py` e `air_defense_volume` di Warfare-Model. Conversioni:
**nmi → km: ×1.852**, **ft → m: ×0.3048**.

Inviluppo in metrico, ordinato per portata:

| Sistema | R min (km) | R max (km) | H min (m) | H max (m) | Acq (s) | Priorità SEAD |
|---|---|---|---|---|---|---|
| SA-5 Gammon | 1.5 | 398.2 | 25 | 40000 | 40 | Track Radar |
| SA-20B Gargoyle | 4.0 | 200.0 | 10 | 27000 | 3 | Track Radar |
| SA-23 Gladiator/Giant | 5.0 | 200.0 | 25 | 37000 | 3 | Track Radar |
| SA-20A Gargoyle | 5.0 | 150.0 | 10 | 27000 | 3 | Track Radar |
| MIM-104 Patriot | 3.0 | 120.0 | 25 | 24232 | 16 | Track Radar |
| SA-12 Gladiator/Giant | 6.0 | 100.0 | 25 | 25000 | 3 | Track Radar |
| SA-10C Grumble-C | 5.0 | 90.0 | 10 | 25000 | 3 | Track Radar |
| SA-10B Grumble | 5.6 | 74.1 | 15 | 45720 | 3 | Track Radar |
| NASAMS | 0.7 | 60.9 | 1 | 25999 | 4 | Track Radar |
| SA-17 Grizzly | 1.0 | 50.0 | 15 | 50000 | 21 | Launcher |
| MIM-23 Hawk | 1.9 | 47.4 | 137 | 13716 | 12 | Track Radar |
| SA-2 Guideline | 7.0 | 40.0 | 100 | 19995 | 21 | Track Radar |
| SA-6 Gainful | 0.9 | 35.6 | 30 | 10058 | 21 | Track Radar |
| SA-11 Gadfly | 3.3 | 35.0 | 15 | 21976 | 21 | Launcher |
| SA-3 Goa | 5.9 | 25.0 | 213 | 19995 | 11 | Track Radar |
| SA-8 Gecko | 1.5 | 13.9 | 15 | 6401 | 19 | Launcher |
| SA-15 Gauntlet | 1.5 | 12.0 | 18 | 7925 | 9 | Launcher |
| HQ-7 | 0.5 | 12.0 | 30 | 4999 | 12 | Launcher |
| SA-13 Gopher | 0.7 | 8.0 | 23 | 4572 | 2.5 | Launcher |
| SA-19 Grison | 0.0 | 7.4 | 0 | 4877 | 4 | Launcher |
| Rapier | 0.4 | 6.9 | 50 | 2987 | 2 | Launcher |
| MIM-115 Roland ADS | 0.9 | 6.3 | 9 | 5944 | 11 | Launcher |
| SA-9 Gaskin | 0.7 | 4.6 | 30 | 3658 | 2.5 | Launcher |

**Osservazioni utili al modello:**

- **`acquire_time` e portata sono inversamente correlati**, ma non linearmente: i sistemi
  moderni a lungo raggio (S-300/S-400, 3 s) sono *più* rapidi dei vecchi a medio raggio
  (SA-2/SA-6/SA-11, 21 s). Non si può derivare la latenza dalla portata.
- **`sead_priority` si divide nettamente**: i sistemi con radar di tracciamento separato
  → colpisci il radar; quelli con radar integrato nel lanciatore (SA-8, SA-11, SA-13, SA-15,
  SA-17, SA-19, Rapier, Roland) → colpisci il lanciatore. È una regola derivabile dalla
  struttura, non un dato indipendente.
- **`cm_type` distingue tre regimi**: Chaff (radar SARH/comando), Flare (IR: SA-9, SA-13,
  HQ-7), Kinetic (non contrastabile: SA-19, Rapier). Rilevante per stimare la probabilità
  di sopravvivenza in `Combat_Power_Estimation`.
- Il `site_layout` dà la **composizione tipica** (es. SA-2: 6 lanciatori + track radar +
  search radar + C2), utile per generare siti plausibili e per stimare quanti elementi
  servono per neutralizzare un sito.

⚠️ La guida è del dicembre 2022: mancano i sistemi aggiunti dopo, e i valori riflettono il
comportamento di DCS di allora, non necessariamente la realtà né DCS 2.9.29.

## 2. `vehicles_overview.json` — tassonomia e anno di servizio

Sei fogli: `Planes` (66), `AAA-SAM` (36), `Armor` (53), `Artillery` (18), `Missiles` (3),
`Infantry` (11).

Il campo **`In service`** (anno) è direttamente utile per il filtraggio d'epoca — lo stesso
problema che la campagna *1975 Georgian War* risolve a mano.

Tassonomie estratte:

- `AAA-SAM.TYPE`: `AAA` (7), `MERAD` (5), `SHORAD` (8), `LORAD` (2), `MANPADS` (3),
  `TGT RAD*` (11 — radar di puntamento censiti come entità separate).
- `AAA-SAM.Danger (1~10)`: scala di pericolosità soggettiva, es. S-300PS e Patriot = 10,
  Buk = 8, Hawk/Kub/Osa/Tor = 7, ZPU = 1.
- `Planes.Category`: `Fighter` (27), `Bomber` (21), `Transport` (6), `Refueling` (5),
  `Recon` (4), `AWACS` (3).
- `Armor.Role`: `Main battle tank` (18), `Infantry fighting vehicle` (11),
  `Armored personnel carrier` (9), `Scout & Recon` (7), `Self-Propelled ATGM` (4),
  `Tank` (3), `Self-Propelled Gun` (1).

Nota: `TGT RAD*` nel foglio AAA-SAM tratta i radar come **asset a sé**, con anno di servizio
proprio. Coerente con quanto emerge dalla SAM guide, dove il radar è un bersaglio distinto
con codice HARM proprio. Warfare-Model dovrebbe fare lo stesso: **un sito SAM è un gruppo di
asset eterogenei, non un asset singolo.**

## 3. `DCS Encyclopedia 1.3.pdf` — valore residuo: lo schema dei campi

170 pagine, luglio 2013 (DCS 1.2.x). Il roster è inservibile, ma lo **schema dei campi** per
categoria è un buon punto di partenza per il catalogo asset del core:

| Sezione | Campi ricorrenti |
|---|---|
| AIRPLANES | `Name`, `Type`, `Crew`, `Length`, `Height`, `Wing span`, `Wing area`, `Weight empty/Normal/Maximum`, `G limit`, `Maximum fuel`, `Maximum Mach at S/L`, `Maximum Mach at height`, `Range with nominal load`, `Maximum range`, `Service ceiling`, `Take-off speed`, `Landing speed`, `Armament` |
| HELICOPTERS | come sopra + `Main rotor diameter`, `Maximum speed`, `Passengers` |
| SHIPS | `Type`, `Complement`, `Armament` (molto povero) |
| VEHICLES | `Type`, `Combat weight`, `Engine`, `Max road speed`, `Operational range`, `Crew`, `Armament`, `Armor`, `Ground clearance`, `Ground pressure`, `Power-to-weight ratio`, `Wheel formula`, `Chassis`, `Rate of fire`, `Gun elevation/depression`, `Turret traverse`, `Caliber` |
| **AIR DEFENSE** | come VEHICLES + **`Max/Min effective range`**, **`Max/Min effective altitude`**, **`Max target speed`**, `Launch weight`, `Warhead`, `Frequency` |
| WEAPONS | `Name`, `Type`, `Developed`, `Guidance`, `G limit`, `Maximum Mach number`, `Payload`, `Warhead type`, `Fuze type`, `Motor`, `Maximum range` |

`AIR DEFENSE` conferma dall'altro lato lo schema della SAM guide, e aggiunge
**`Max target speed`** — un vincolo d'ingaggio che la SAM guide non ha.

## 4. Frequenze e beacon — valore basso

`DCS Table of Frequencies.pdf` (2014): 21 aeroporti del Caucaso con ICAO, coordinate,
pista, frequenza torre, ILS, TACAN. `DCS World List of all available Beacons EN.pdf` (2015):
~200 righe con `ID, Location, Position, Runway, Type, Frequency/Channel, Band, Morse,
Callsign, Nation, Lat, Lon`. Tipi: ILS (58), NDB (47), LOC (45), VOR (17), DME (12),
PRMG (8), TACAN (6), RSBN (4).

Entrambi coprono **solo il Caucaso pre-rework** e sono superati. Il valore residuo è lo
**schema**: se il core deve modellare infrastrutture di navigazione e comunicazione, questi
sono i campi. Ma il dato va ripreso dal `.miz` o da `Init/db_airbases.lua` di DCE, non da qui.

DCE già gestisce le frequenze per conto proprio in `Init/radios_freq_compatible.lua` (36 KB).
