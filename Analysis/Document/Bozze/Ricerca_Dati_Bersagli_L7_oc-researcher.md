# Ricerca dati — Blocco 0 BI, LOTTO L7 (missili navali)

Bozza di `oc-researcher`, 2026-11-07. Fonti web lette in questa sessione; nessun valore inventato. Le due ancore
(AGM-65D, AGM-84A Harpoon aviolanciato) sono quelle fornite dal principale e **non** sono state ricercate: qui sono
solo richiamate per il confronto. `websearch` non disponibile: ricerca con `webfetch` su pagine note. Ho tentato anche
`https://html.duckduckgo.com/html/?q=...` per scoprire URL, ma DuckDuckGo ha risposto con un captcha; gli URL sono
stati quindi ricavati da pagine note e dai riferimenti delle voci Wikipedia.

Riferimenti nel repo (letti con `grep -n` / `sed -n`):
- §2.2 tabella armi→classe (righe 342-375) e §5.1 blocco 0 (righe 849-880):
  `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`.
- `Code/Dynamic_War_Manager/Source/Asset/Ship_Weapon_Data.py`, `SHIP_WEAPONS['MISSILES_ASM']`:
  `BGM-109-Tomahawk` (riga 1254), `P-700-Granit` (1268), `P-270-Moskit` (1282), `P-1000-Vulkan` (1296),
  `YJ-12` (1310), `YJ-18` (1324), `YJ-83` (1338). Valori del registro: `caliber` [mm], `warhead` [kg],
  `range` [km], `start_service`, `task`.

## 1) Tabella riassuntiva

| Voce (registro) | Variante cercata | Classe proposta (ipotesi del piano) | Diametro | Lunghezza | Massa al lancio | RCS | Confronto con le ancore | Confidenza |
|---|---|---|---|---|---|---|---|---|
| **BGM-109-Tomahawk** (`:1254`, caliber 519, warhead 454, range 1600, 1983) | famiglia Tomahawk; il range 1600 km del registro punta alla **Block IV TLAM-E**; il `task` Land_Attack+Anti_Ship somma TLAM e TASM/Block Va MST | `cruise` — **confermata** | **0,52 m** (520 mm) | **5,55-5,56 m** senza booster; 6,25 m con booster | **1.300-1.315 kg** senza booster; 1.600 kg con booster | non pubblicata | **non minore dell'Harpoon** (0,52 > 0,343 m; 1.300 > 515,25 kg) | A |
| **P-700-Granit** (`:1268`, caliber 850, warhead 750, range 550, 1983) | 3M45 / SS-N-19 "Shipwreck", navale (nave e sottomarino) | `anti_ship` — **confermata** | **850 mm** | **10 m** | **7.000 kg** | non pubblicata | **non minore dell'Harpoon** (0,85 > 0,343 m; 7.000 > 515,25 kg) | A (classe) / M (dimensioni) |
| **P-270-Moskit** (`:1282`, caliber 760, warhead 300, range 120, 1984) | **3M80 / 3M80E** navale, SS-N-22 "Sunburn" (la variante aviolanciata Kh-41 è un'altra voce, `AIR_WEAPONS`) | `anti_ship` — **confermata** | **0,8 m** (800 mm) | **9,745 m** (infobox) / **9,385 m** (sezione specifiche) | **4.500 kg** (infobox) / **4.150 kg** (3M-80E) | non pubblicata | **non minore dell'Harpoon** (0,8 > 0,343 m; 4.150-4.500 > 515,25 kg) | A (classe) / M (dimensioni) |
| **P-1000-Vulkan** (`:1296`, caliber 880, warhead 500, range 700, 1987) | 3M70 / SS-N-12 mod.2 "Sandbox", navale (nave e sottomarino) | `anti_ship` — **confermata** | **880 mm** | **11,7 m** | **7.000-8.000 kg** (ru.wikipedia) / 4.800 kg (altra fonte, discordante) | non pubblicata | **non minore dell'Harpoon** (0,88 > 0,343 m; migliaia di kg > 515,25 kg) | M (dimensioni) / B (massa, fonti discordi) |
| **YJ-12** (`:1310`, caliber 500, warhead 205, range 400, 2015) | famiglia YJ-12; per il registro **navale** il più coerente è **YJ-12A** (lancio da nave, con booster) | `anti_ship` — **confermata** | **0,5 m** (GlobalSecurity) / **0,6 m** (zh.wikipedia, dichiarato "推测" = stimato) | **6-7 m** (GlobalSecurity) / **7 m** (zh.wikipedia, "modello iniziale") | **2-2,5 t** (GlobalSecurity) / **≈3 t** (zh.wikipedia) — dell'aviolanciata (la YJ-12A navale aggiunge un booster esterno) | non pubblicata | **non minore dell'Harpoon** (≥0,5 > 0,343 m; ≥2.000 > 515,25 kg) | B |
| **YJ-18** (`:1324`, caliber 540, warhead 300, range 540, 2015) | **YJ-18A** (lancio da VLS navale); la famiglia comprende anche YJ-18 (siluri) e YJ-18B/C land-attack | `anti_ship` — **confermata** | **514 mm** (CSIS, stima dichiarata) / 540 mm nel registro | **<8,2 m** con booster | **<1.579 kg** | non pubblicata | **non minore dell'Harpoon** (0,514 > 0,343 m; 1.579 > 515,25 kg) | M |
| **YJ-83** (`:1338`, caliber 360, warhead 165, range 180, 1998) | **YJ-83** (navale, testata 190 kg); il registro riporta 165 kg, che è la testata della **YJ-83K aviolanciata**: la voce mescola le due | `anti_ship` — **confermata** | **360 mm** | **6,38 m** | **800 kg** | non pubblicata | **non minore dell'Harpoon** (360 > 343 mm; 800 > 515,25 kg): è la voce più vicina all'ancora alta | M |

Nessuno dei sette missili è vicino all'ancora bassa (Maverick 304,8 mm / 218,25-220 kg): tutti superano l'ancora alta
(Harpoon 343 mm / 515,25 kg), quindi la proposta è "non minore dell'Harpoon" per tutte le voci.

## 2) Dettaglio per voce

### 2.1 BGM-109-Tomahawk (`Ship_Weapon_Data.py:1254`)

Voce del registro: `model` "BGM-109-Tomahawk", `start_service` 1983, `caliber` 519, `warhead` 454, `range` 1600,
`speed` 252 m/s, `guidance` "Inertial_TERCOM_GPS", `task` ["Land_Attack", "Anti_Ship"].

Variante identificata: il range di 1600 km corrisponde alla **Block IV TLAM-E** (1.600 km), mentre `start_service`
1983 è l'inizio del servizio della famiglia. Il `task` Anti_Ship corrisponde storicamente al **TASM (RGM/UGM-109B)**,
ritirato nel 1994, e oggi alla **Block Va Maritime Strike Tomahawk**; il registro li fonde in un unico modello. Ho
cercato la famiglia Tomahawk / Block IV.

Valori:
- **Diametro 0,52 m.** Wikipedia, infobox: "20.4 in (0.52 m)" — M; CSIS, scheda: "0.52 m" — M. Due secondarie
  concordi → **A**.
- **Lunghezza 5,55-5,56 m senza booster (6,25 m con).** CSIS: "5.55 m without booster; 6.25 m with booster" — M;
  Wikipedia: "18 ft 3 in (5.56 m) without booster" — M. Concordi entro 1 cm → **A**.
- **Massa 1.300-1.315 kg senza booster (1.600 kg con).** Wikipedia: "2,900 lb (1,300 kg)"; CSIS: "1,315 kg (without
  booster)"; Wikipedia riporta anche "3,500 lb (1,600 kg) with booster". Due secondarie concordi entro ~1,2% → **A**.
- **RCS:** non pubblicata (nessuna fonte consultata riporta una RCS per il Tomahawk).
- **Classe:** Wikipedia classifica il tipo come "Cruise missile" e "Anti-ship missile ... (Block V & TASM variants)";
  CSIS: "Subsonic, Intermediate Range Cruise Missile". **`cruise` confermata** (missile da crociera a lungo raggio,
  attacco a terra prevalente, con capacità antinave nelle sottovarianti).

URL e estratti:
- `https://en.wikipedia.org/wiki/Tomahawk_(missile)` — "20.4 in (0.52 m)"; "18 ft 3 in (5.56 m) without booster";
  "2,900 lb (1,300 kg)".
- `https://missilethreat.csis.org/missile/tomahawk/` — "Class Subsonic, Intermediate Range Cruise Missile";
  "Length 5.55 m without booster; 6.25 m with booster"; "Diameter 0.52 m"; "Launch Weight 1,315 kg (without booster)".

Confronto ancore: 0,52 m > 0,343 m e 1.300-1.315 kg > 515,25 kg → **non minore dell'Harpoon**.

### 2.2 P-700-Granit (`Ship_Weapon_Data.py:1268`)

Voce del registro: `model` "P-700-Granit", `start_service` 1983, `caliber` 850, `warhead` 750, `range` 550,
`speed` 850 m/s, `guidance` "Active_Radar_Inertial", `task` ["Anti_Ship"].

Variante identificata: **P-700 Granit 3M45**, SS-N-19 "Shipwreck", lanciato da nave e da sottomarino; il registro
(1983, 550 km, testata 750 kg) coincide con la variante base descritta dalle fonti.

Valori:
- **Diametro 0,85 m (850 mm).** Wikipedia, infobox: "Diameter 0.85 m (33 in)" — M. Coerente con `caliber` 850 del
  registro.
- **Lunghezza 10 m.** Wikipedia: "Length 10 m (33 ft)" — M.
- **Massa al lancio 7.000 kg.** Wikipedia: "Mass 7,000 kg (15,400 lb)" — M.
- **RCS:** non pubblicata.
- **Classe:** Wikipedia: "Long-range anti-ship cruise missile"; CSIS (notizia, ricerca interna del sito) elenca
  "P-1000 Vulkan, P-700 Granit, P-120 Malakhit and P-800 Oniks antiship cruise missiles" —
  `https://missilethreat.csis.org/russian-navy-tests-anti-ship-cruise-missiles/`. La missione primaria è antinave
  (con possibilità secondaria contro bersagli terrestri): **`anti_ship` confermata**.

URL ed estratti:
- `https://en.wikipedia.org/wiki/P-700_Granit` — "Mass 7,000 kg (15,400 lb)"; "Length 10 m (33 ft)";
  "Diameter 0.85 m (33 in)"; tipo dichiarato "Long-range anti-ship cruise missile".
- `https://missilethreat.csis.org/russian-navy-tests-anti-ship-cruise-missiles/` — estratto dal risultato di ricerca
  del sito: "fired P-1000 Vulkan, P-700 Granit, P-120 Malakhit and P-800 Oniks antiship cruise missiles".

Confronto ancore: 0,85 m > 0,343 m e 7.000 kg > 515,25 kg → **non minore dell'Harpoon**.

### 2.3 P-270-Moskit (`Ship_Weapon_Data.py:1282`)

Voce del registro: `model` "P-270-Moskit", `start_service` 1984, `caliber` 760, `warhead` 300, `range` 120,
`speed` 952 m/s, `guidance` "Active_Radar_Inertial", `task` ["Anti_Ship"].

Variante identificata: **3M80 / 3M80E navale**, SS-N-22 "Sunburn". La variante aviolanciata **Kh-41** è una voce
separata di `AIR_WEAPONS`; qui va considerata quella navale (il registro dà 1984 e 120 km, coerenti con la 3M80E).

Valori:
- **Diametro 0,8 m (800 mm).** Wikipedia, infobox: "Diameter 0.8 m (31 in)"; nella sezione "Specifications":
  "Body diameter: 0.8 m". Due punti della stessa fonte, concordi col `caliber` 760 del registro → **M**
  (una sola fonte secondaria; il registro non è una fonte esterna).
- **Lunghezza 9,745 m (infobox) / 9,385 m (sezione specifiche).** Wikipedia: "Length 9.745 m (31 ft 11.7 in)" e
  "Length: 9.385 m". Le due misure della stessa pagina **discordano** (probabilmente 3M80 vs 3M80E/3M82): riportate
  entrambe, non scelgo → **M**.
- **Massa al lancio 4.500 kg (infobox) / 4.150 kg (3M-80E).** Wikipedia: "Mass 4,500 kg (9,900 lb)" e, nella sezione
  specifiche, "3M-80E missile 4,150 kg (9,150 lb)" (più "3M-80E1 missile 3,970 kg (8,750 lb)"). Riporto la fascia
  3.970-4.500 kg, con 4.150 kg per la 3M-80E → **M**.
- **RCS:** non pubblicata.
- **Classe:** Wikipedia: "Anti-ship missile" e nel testo "anti-ship cruise missile"; CSIS (notizia):
  "Russia Test Fires P-270 Moskit Antiship Missile" — `https://missilethreat.csis.org/russia-test-fires-p-270-moskit-antiship-missile/`.
  **`anti_ship` confermata** (missile antinave supersonico a ramjet; la lunga autonomia non ne fa un cruise da attacco
  a terra).

URL ed estratti:
- `https://en.wikipedia.org/wiki/P-270_Moskit` — "Mass 4,500 kg (9,900 lb)"; "Length 9.745 m (31 ft 11.7 in)";
  "Diameter 0.8 m (31 in)"; "Length: 9.385 m"; "3M-80E missile 4,150 kg (9,150 lb)".
- `https://missilethreat.csis.org/russia-test-fires-p-270-moskit-antiship-missile/` — titolo/estratto:
  "Russia Test Fires P-270 Moskit Antiship Missile".

Confronto ancore: 0,8 m > 0,343 m e 3.970-4.500 kg > 515,25 kg → **non minore dell'Harpoon**.

### 2.4 P-1000-Vulkan (`Ship_Weapon_Data.py:1296`)

Voce del registro: `model` "P-1000-Vulkan", `start_service` 1987, `caliber` 880, `warhead` 500, `range` 700,
`speed` 850 m/s, `guidance` "Active_Radar_Inertial", `task` ["Anti_Ship"].

Variante identificata: **P-1000 Vulkan 3M70**, SS-N-12 mod.2 "Sandbox", sviluppo del P-500 Bazalt; navale (incrociatori
progetto 1164 e sottomarini progetto 675MKV).

Valori:
- **Diametro 0,88 m (880 mm).** ru.wikipedia, sezione ТТХ: "Диаметр: 0,88 м" — M; coerente con `caliber` 880 del
  registro.
- **Lunghezza 11,7 m.** ru.wikipedia: "Длина: 11,7 м" — M. La stessa misura compare nella pagina
  cruiser-moskva.info (archiviata) come "11700" mm, ma il testo della pagina è illeggibile per codifica
  windows-1251 (v. §3).
- **Massa al lancio 7.000-8.000 kg.** ru.wikipedia: "Стартовая масса: 7000—8000 кг" — M. Fonte discordante:
  cruiser-moskva.info (archiviata) riporta "4800" kg, valore identico a quello che la stessa pagina dà per il P-500
  (probabile copia dei dati del Bazalt) → v. §3.
- **RCS:** non pubblicata.
- **Classe:** ru.wikipedia: "противокорабельный ракетный комплекс" e "противокорабельной ракеты"; CSIS (notizia)
  elenca il "P-1000 Vulkan" tra gli "antiship cruise missiles". **`anti_ship` confermata**.

URL ed estratti:
- `https://ru.wikipedia.org/wiki/П-1000_«Вулкан»` — "Длина: 11,7 м"; "Диаметр: 0,88 м";
  "Стартовая масса: 7000—8000 кг"; "фугасно-кумулятивная: 500 кг".
- `https://web.archive.org/web/20151003015443/http://www.cruiser-moskva.info/arms/p1000.htm` — pagina in
  windows-1251, testo non leggibile; leggibili solo i numeri ASCII "11700", "2600", "4800".
- `https://missilethreat.csis.org/russian-navy-tests-anti-ship-cruise-missiles/` — "antiship cruise missiles".

Confronto ancore: 0,88 m > 0,343 m e migliaia di kg > 515,25 kg → **non minore dell'Harpoon**.

### 2.5 YJ-12 (`Ship_Weapon_Data.py:1310`)

Voce del registro: `model` "YJ-12", `start_service` 2015, `caliber` 500, `warhead` 205, `range` 400,
`speed` 1020 m/s, `guidance` "Active_Radar_Inertial", `task` ["Anti_Ship"].

Variante identificata: famiglia **YJ-12 / YJ-12A / YJ-12B**. Il registro è navale e dà 2015 e 400 km, quindi il
riferimento più coerente è **YJ-12A** (lancio da nave, entrato in servizio circa 2020 secondo en.wikipedia; il YJ-12
base è aviolanciato). Attenzione: la versione navale aggiunge un **booster** al posto della velocità iniziale fornita
dall'aereo, e questo allunga il corpo — zh.wikipedia: "鹰击-12A...需要在尾部增加一个助推段，导致弹体总长拉长".

Valori (dell'aviolanciata YJ-12 base; la versione navale YJ-12A aggiunge un booster esterno che allunga e
appesantisce il missile, ma il valore navale non è stato trovato):
- **Diametro 0,5 m (GlobalSecurity) / 0,6 m (zh.wikipedia, dichiarato stimato).** GlobalSecurity: "the projectile
  diameter is about 0.5 meters"; zh.wikipedia, infobox: "Diameter = 0.6m（推测）" (推测 = stimato). **Discordi**:
  riporto entrambi, non scelgo → **B**.
- **Lunghezza 6-7 m / 7 m.** GlobalSecurity: "the length of the Eagle 12 projectile is about 6 to 7 meters";
  zh.wikipedia: "Length = 7m（初期型号）" (modello iniziale). Concordi → **M**.
- **Massa al lancio 2-2,5 t / ≈3 t.** GlobalSecurity: "weighs between 2 and 2.5 tons"; zh.wikipedia, infobox:
  "total_mass = ≈3吨"; lo stesso testo zh.wikipedia cita anche i dati Jane's "重约2-2.5吨，长约7米". **Discordi**:
  riporto 2-3 t → **B**.
- **RCS:** non pubblicata.
- **Classe:** en.wikipedia: "Type Anti-ship cruise missile / Land-attack cruise missile"; zh.wikipedia: "Function =
  飛航式反艦飛彈" (missile antinave tipo cruise). CSIS (notizia): "the YJ-12 antiship cruise missile". La missione
  primaria è antinave (la variante CM-302 è offerta anche per attacco a terra): **`anti_ship` confermata**.

URL ed estratti:
- `https://www.globalsecurity.org/military/world/china/yj-12.htm` — "the length of the Eagle 12 projectile is about
  6 to 7 meters, and the projectile diameter is about 0.5 meters"; "weighs between 2 and 2.5 tons".
- `https://zh.wikipedia.org/wiki/鹰击12反舰导弹` — "Length = 7m（初期型号）"; "Diameter = 0.6m（推测）";
  "total_mass = ≈3吨"; "Warhead = 250∼300千克高爆半穿甲重战斗部".
- `https://en.wikipedia.org/wiki/YJ-12` — "Type Anti-ship cruise missile / Land-attack cruise missile".

Confronto ancore: ≥0,5 m > 0,343 m e ≥2.000 kg > 515,25 kg → **non minore dell'Harpoon** (anche nel caso dei valori
più bassi).

### 2.6 YJ-18 (`Ship_Weapon_Data.py:1324`)

Voce del registro: `model` "YJ-18", `start_service` 2015, `caliber` 540, `warhead` 300, `range` 540,
`speed` 850 m/s, `guidance` "Active_Radar_Inertial", `task` ["Anti_Ship"].

Variante identificata: **YJ-18A** (lancio da VLS di superficie), coerente con la voce navale e con il `start_service`
2015. La famiglia comprende YJ-18 (siluri), YJ-18B (VLS subacqueo, land-attack) e YJ-18C (container, land-attack).

Valori:
- **Diametro 514 mm (CSIS) / 540 mm (registro).** CSIS: "likely approximates the 3M-54E's 8.2 m length, 0.514 m
  diameter, and 1,579 kg weight" — è una **stima dichiarata** ("likely"), non un dato ufficiale; il registro dà 540.
  Riporto entrambi → **B/M**.
- **Lunghezza <8,2 m con booster.** CSIS, scheda: "Length <8.2 m (inc. booster)"; en.wikipedia, infobox:
  "length={{cvt|8.2|m|ft}} (with booster)" (che cita CSIS). Le due fonti non sono indipendenti (Wikipedia cita CSIS)
  → **M**.
- **Massa al lancio <1.579 kg.** CSIS: "Launch Weight <1,579 kg"; en.wikipedia: "weight={{cvt|1579|kg|lb}}" (cita
  CSIS) → **M**.
- **RCS:** non pubblicata.
- **Classe:** CSIS: "Class Cruise Missile" e "a Chinese cruise missile with variants for antiship and land-attack
  missions"; en.wikipedia: "Anti-ship cruise missile / land-attack cruise missile". Poiché la missione della
  variante a registro è antinave (task Anti_Ship, seeker radar attivo terminale, sprint supersonico finale),
  **`anti_ship` confermata**; segnalo che la classificazione "cruise" di CSIS è generica e comprende le varianti
  land-attack.

URL ed estratti:
- `https://missilethreat.csis.org/missile/yj-18/` — "Length <8.2 m (inc. booster)"; "Launch Weight <1,579 kg";
  "likely approximates the 3M-54E's 8.2 m length, 0.514 m diameter, and 1,579 kg weight"; "Class Cruise Missile".
- `https://en.wikipedia.org/wiki/YJ-18` — "Anti-ship cruise missile"; "8.2 m"; "1579 kg".

Confronto ancore: 0,514-0,540 m > 0,343 m e 1.579 kg > 515,25 kg → **non minore dell'Harpoon**.

### 2.7 YJ-83 (`Ship_Weapon_Data.py:1338`)

Voce del registro: `model` "YJ-83", `start_service` 1998, `caliber` 360, `warhead` 165, `range` 180,
`speed` 306 m/s, `guidance` "Active_Radar", `task` ["Anti_Ship"].

Variante identificata: **YJ-83** di famiglia (YJ-83, YJ-83A/J, YJ-83K, YJ-83KH; export C-802/C-802A). Il registro è
navale, ma la `warhead` di 165 kg è quella della **YJ-83K aviolanciata** (seminfrangente), mentre la YJ-83 navale ha
190 kg HE-frammentazione: la voce mescola le due varianti. Dimensioni e massa sono comuni alla famiglia.

Valori:
- **Diametro 360 mm.** en.wikipedia, infobox: "diameter=360 mm" (cita Gormley-Erickson-Yuan 2014) — M. Coincide con
  `caliber` 360 del registro.
- **Lunghezza 6,38 m.** en.wikipedia: "length=6.38 m" (stessa fonte) — M.
- **Massa al lancio 800 kg.** en.wikipedia: "weight= 800 kg" (stessa fonte) — M.
- **RCS:** non pubblicata.
- **Classe:** en.wikipedia: "Type Anti-ship cruise missile"; nel testo "Chinese subsonic anti-ship cruise missile".
  **`anti_ship` confermata** (missile antinave subsonico, non cruise da attacco a terra).

URL ed estratti:
- `https://en.wikipedia.org/wiki/YJ-83` — "Type Anti-ship cruise missile"; "weight= 800 kg"; "length=6.38 m";
  "diameter=360 mm"; "190 kg high-explosive fragmentation (YJ-83)"; "165 kg high-explosive, semi-armour piercing
  (YJ-83K)".

Confronto ancore: 360 mm > 343 mm e 800 kg > 515,25 kg → **non minore dell'Harpoon**, ma è la voce più vicina
all'ancora alta (diametro +5%, massa +55%).

## 3) Discordanze fra fonti

1. **P-270-Moskit — lunghezza e massa (stessa pagina Wikipedia).** Infobox: "Length 9.745 m" e "Mass 4,500 kg";
   sezione "Specifications": "Length: 9.385 m" e "3M-80E missile 4,150 kg" (3M-80E1 3,970 kg). Le due sezioni
   descrivono probabilmente varianti diverse (3M80/3M82 vs 3M80E). Riportate entrambe, non scelgo.
2. **P-1000-Vulkan — massa.** ru.wikipedia: "Стартовая масса: 7000—8000 кг"; la pagina archiviata
   cruiser-moskva.info riporta "4800" kg (e "11700" mm di lunghezza), lo stesso valore che essa dà per il P-500:
   sospetta copia dei dati del Bazalt. La pagina è in windows-1251 e il testo non è leggibile: ho potuto leggere solo
   i numeri ASCII. Preferisco 7.000-8.000 kg (ru.wikipedia), con riserva.
3. **YJ-12 — diametro e massa.** GlobalSecurity: "about 0.5 meters" e "between 2 and 2.5 tons"; zh.wikipedia:
   "0.6m（推测）" e "≈3吨". Riportati entrambi. La stessa pagina GlobalSecurity contiene un errore evidente
   ("the 3M80E projectile ... projectile diameter reaches 1.3 meters": 1,3 m è l'apertura alare ripiegata, non il
   diametro), quindi la sua affidabilità è bassa.
4. **YJ-18 — diametro.** CSIS: 0,514 m (dichiarato come stima "likely approximates the 3M-54E"); registro: 540 mm.
   Riportati entrambi; prevale il dato del registro finché non c'è una fonte ufficiale.
5. **YJ-83 — testata.** Il registro dichiara 165 kg, che è la testata della YJ-83K aviolanciata; la YJ-83 navale ha
   190 kg HE-frammentazione (en.wikipedia). La voce del registro (navale) mescola due varianti.
6. **YJ-12 — portata.** Il registro dà 400 km; GlobalSecurity "about 150-300 kilometers" (testo) e zh.wikipedia una
   portata "≥200 km (bassa quota), 400-500 km (alta quota)". La portata non era un dato richiesto, ma la segnalo.

## 4) Cosa non ho trovato / non ho potuto verificare

- **RCS: non pubblicata per nessuna delle sette voci.** Non esistono valori pubblici affidabili; non ho inventato
  nulla.
- **YJ-12:** nessuna fonte primaria (costruttore o forza armata) con dimensioni ufficiali; i valori disponibili sono
  stime di fonti secondarie e discordano. La lunghezza della **YJ-12A navale con booster** non è stata trovata
  (zh.wikipedia dice solo che il corpo si allunga); il valore 7 m è dell'aviolanciata iniziale.
- **YJ-18:** diametro ufficiale non trovato; CSIS lo dichiara espressamente come stima basata sul 3M-54E.
- **P-1000:** diametro 0,88 m confermato solo da ru.wikipedia (e dal `caliber` del registro, che non è fonte esterna);
  massa discordante. La pagina cruiser-moskva.info è illeggibile per codifica.
- **Pagine non raggiungibili (404 o errore):**
  `https://missilethreat.csis.org/missile/yj-12/` (404), `/missile/yj-12a/` (404),
  `/missile/ss-n-19-shipwreck/` (404), `/missile/ss-n-22-sunburn/` (404), `/missile/yj-83/` (404);
  `http://www.airwar.ru/weapon/pkr/vulkan.html` (404); `http://rbase.new-factoria.ru/missile/wobb/p1000/p1000.shtml`
  (errore di trasporto); `https://man.fas.org/dod-101/sys/missile/row/ss-n-12.htm` (404) e
  `.../row/moskit.htm` (404); `https://man.fas.org/dod-101/sys/missile/row/index.html` (404);
  `http://www.testpilot.ru/russia/chelomei/p/1000/index.htm` (restituisce solo il titolo, pagina con frames).
- **DuckDuckGo:** la pagina di risultati HTML ha risposto con un captcha ("Please complete the following
  challenge"), quindi non ho potuto usarla per scoprire URL. Bing ha restituito risultati irrilevanti (interpretava
  "YJ" come Jeep). Gli URL sono stati presi da pagine note e dai riferimenti delle voci Wikipedia.
- **Pagine CSIS complete per Granit, Moskit, Vulkan, YJ-12, YJ-83:** non esistono o non sono state trovate; per la
  classe ho usato le schede/notizie CSIS trovate con la ricerca interna del sito (solo titolo/estratto).

## 5) Metodo

- Strumento: `webfetch` (formato markdown o text; per Wikipedia ho usato anche `action=raw` per ridurre il rumore).
  `websearch` non disponibile.
- Pagine lette con successo (17):
  1. `https://en.wikipedia.org/wiki/Tomahawk_(missile)`
  2. `https://en.wikipedia.org/wiki/P-700_Granit`
  3. `https://en.wikipedia.org/wiki/P-270_Moskit`
  4. `https://en.wikipedia.org/wiki/P-1000_Vulkan` (redirect a P-500 Bazalt)
  5. `https://en.wikipedia.org/wiki/YJ-12`
  6. `https://en.wikipedia.org/w/index.php?title=YJ-18&action=raw`
  7. `https://en.wikipedia.org/w/index.php?title=YJ-83&action=raw`
  8. `https://missilethreat.csis.org/missile/yj-18/`
  9. `https://missilethreat.csis.org/missile/tomahawk/`
  10. `https://zh.wikipedia.org/w/index.php?title=鹰击12反舰导弹&action=raw`
  11. `https://ru.wikipedia.org/w/index.php?title=П-1000_«Вулкан»&action=raw`
  12. `https://ru.wikipedia.org/w/index.php?title=П-500_«Базальт»&action=raw` (redirect)
  13. `https://web.archive.org/web/20151003015443/http://www.cruiser-moskva.info/arms/p1000.htm`
  14. `https://www.globalsecurity.org/military/world/china/yj-12.htm`
  15. `https://missilethreat.csis.org/?s=YJ-12` (risultati di ricerca, solo URL/estratti)
  16. `https://missilethreat.csis.org/?s=Granit`
  17. `https://missilethreat.csis.org/?s=Moskit`
- Pagine tentate e fallite: 11 (elencate al §4, piu' la pagina captcha di DuckDuckGo e la ricerca Bing, inutile).
- Passi usati: **46** chiamate a strumento (di cui 6 di lettura del repo: `grep`/`sed` su Proposta e registro,
  `glob`/`read` per il formato della bozza). Pagine web lette con successo: **17**.

## 6) Sintesi

Tutte e sette le voci del lotto L7 sono **grandi**: superano l'ancora alta (Harpoon aviolanciato, 343 mm /
515,25 kg) sia in diametro sia in massa, e sono lontanissime dall'ancora bassa (Maverick). Per il criterio del blocco 0
("non minore dell'Harpoon" → True) la proposta è **`ad_detectable` True / intercettabili dalle difese navali** per
tutte, senza zona grigia dimensionale.

Le ipotesi di classe del piano sono **tutte confermate**:
- **Tomahawk → `cruise`**: missile da crociera subsonico a lungo raggio, attacco a terra prevalente (la capacità
  antinave è nelle sottovarianti TASM/Block Va).
- **Granit, Moskit, Vulkan, YJ-12, YJ-18, YJ-83 → `anti_ship`**: la missione primaria e il seeker sono antinave.
  Granit/Moskit/Vulkan/YJ-18 sono tecnicamente "anti-ship cruise missiles" (volo autonomo), ma la classe `anti_ship`
  è quella corretta perché distingue la missione, non il profilo di volo. YJ-18 e YJ-12 hanno anche varianti
  land-attack, ma la voce a registro è la variante antinave.

Dati più solidi (confidenza A): Tomahawk (diametro, lunghezza, massa, classe; due secondarie concordi). Dati buoni
(M): Granit, Moskit (con discordanzze interne), Vulkan, YJ-18, YJ-83. Dati deboli (B): YJ-12 (fonti discordi) e
massa del Vulkan.