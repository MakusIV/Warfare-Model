# Ricerca dati — Blocco 0 BI, lotto L2 (ATGM e MANPADS)

Bozza del `oc-researcher`, 2026-11-07. Ambito: §5.1 "Blocco 0" della Proposta
`Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`, lotto **L2 — candidati piccoli:
ATGM e MANPADS**. Le voci sono quelle dei registri
`Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` (`AIR_WEAPONS['MISSILES_ASM']`): nessuna
delle sette voci compare in `Ship_Weapon_Data.py` `SHIP_WEAPONS['MISSILES_ASM']` (verificato con `grep -n`,
nessun risultato nel file navale).

**Ancore di confronto (date dal principale, non ricercate qui)**: Maverick AGM-65D = diametro 304,8 mm,
lunghezza 2,49 m, massa 218,25–220 kg; Harpoon AGM-84A aviolanciato = diametro 343 mm, lunghezza
3,79–3,85 m, massa 515,25 kg (556 kg nel testo CSIS; 691 kg = RGM/UGM con booster).

**Nota di lettura**: tutte le voci del lotto hanno diametro 90–180 mm e massa 19,7–49,5 kg, quindi tutte
cadono nella stessa fascia **molto inferiore** a entrambe le ancore. In termini del "metro del Maverick"
(§5.1) la risposta è per tutte "**non maggiore del Maverick**" e la proposta coerente è `ad_detectable`
False, salvo la questione di classe del Mistral (v. sotto).

## 1) Tabella riassuntiva

| Voce (registro) | Variante cercata / trovata | Classe proposta (ipotesi del piano) | Diametro | Lunghezza | Massa al lancio | RCS | Confronto con le ancore | Conf. |
|---|---|---|---|---|---|---|---|---|
| `AGM-114` | AGM-114 **generico**; il registro (1984, 8 km, testata 9 kg) corrisponde alla famiglia A/B/C (1982–92, 8 km) e in parte alla K (testata 9 kg). Dati di ingombro identici per A/B/C/K. | `tactical` — **ipotesi confermata** (ATGM aviolanciato a corto raggio) | 7 in = **180 mm** (Wikipedia) / 17,8 cm = **178 mm** (designation-systems) | 64 in = **1,63 m** | 100–108 lb = **45–49 kg**; 45,7 kg per B/C (designation-systems) | **non pubblicata** | **non maggiore del Maverick** (178–180 mm < 304,8 mm; 45,7 kg ≪ 218 kg) | A |
| `BGM-71D` | **BGM-71D = TOW 2** (TOW-2 della tabella Wikipedia). Il registro ha `start_service` 1970 (Basic TOW) e `warhead` 6,14 kg (valore del BGM-71F): incoerenze di registro, non di ingombro. | `tactical` — **ipotesi confermata** (ATGM, nonostante `task` includa SEAD/Anti_Ship) | **152 mm** | **1,17 m** (sonda chiusa) / **1,51 m** (sonda estesa) | **21,5 kg** (Wikipedia) / 21,52 kg (FAS) | **non pubblicata** | **non maggiore del Maverick** (152 mm; 21,5 kg) | A |
| `9M114` | **9M114 Kokon / 9K114 Shturm** (AT-6 Spiral). Il `range` 7 km del registro corrisponde alla variante **9M114M2**; gli ingombri sono quelli del Kokon base. | `tactical` — **ipotesi confermata** | **130 mm** | **1.625 mm** (Wikipedia) **oppure 1.830 mm** (Missilery.info, airwar.ru): v. Discordanze | **31,4 kg** (missile, Wikipedia) / **46,5 kg** con tubo di lancio (Missilery) | **non pubblicata** | **non maggiore del Maverick** (130 mm; 31,4 kg, oppure 46,5 kg con contenitore) | A |
| `9M120` | **9M120 Ataka** (AT-9 Spiral-2), variante base con testata tandem HEAT | `tactical` — **ipotesi confermata** | **130 mm** | **1.830 mm** | **49,5 kg** (Wikipedia) / **46–46,5 kg** (airwar.ru): v. Discordanze | **non pubblicata** | **non maggiore del Maverick** (130 mm; ≤49,5 kg) | A (diametro/lunghezza); M (massa) |
| `9M120-F` | **9M120F Ataka**, variante con testata **termobarica**. Il registro la scrive `9M120-F`; la grafia delle fonti è `9M120F`. | `tactical` — **ipotesi confermata** (stessa famiglia, ruolo antipersonale/bunker) | **130 mm** (cellula della famiglia, dato specifico non pubblicato) | **1.830 mm** (cellula della famiglia, dato specifico non pubblicato) | **≈49,5 kg** (cellula della famiglia; dato specifico non pubblicato) | **non pubblicata** | **non maggiore del Maverick** (130 mm; ≈49,5 kg) | B (ingombri specifici [S]) |
| `Hot-3` | **HOT-3** (Euromissile/MBDA). Il registro ha `start_service` 1978 (HOT 1 entrò in servizio nel 1978; **HOT-3 nel 1998**) e testata 6 kg (HOT-3 = 6,48 kg): il nome impone la variante HOT-3. | `tactical` — **ipotesi confermata** | **150 mm** (0,15 m) | **1,30 m** | **24,5 kg** (altre fonti 23,5–32,5 kg, v. Discordanze) | **non pubblicata** | **non maggiore del Maverick** (150 mm; 24,5 kg) | M |
| `Mistral` | **Mistral 1/2** (raggio 6 km, `start_service` 1985 nel registro; Mistral 1 in servizio dal 1990). **ANOMALIA confermata**: è un SAM/MANPADS, non un missile aria-superficie. | **`tactical` contestata**: la classe corretta è **`sam`** (fuori dalle quattro opzioni del compito), quindi **non bersaglio** secondo §2.3 (SAM → `sam`). Se si forza lo schema a quattro classi, `tactical` è la meno sbagliata solo perché "corto raggio". | **90 mm** (Wikipedia) / **~92 mm** (MBDA) | **1,86 m** (Wikipedia) / **1,88 m incluso motore di lancio** (MBDA) | **19,7 kg** (Wikipedia) / "less than 20kg" (MBDA) | **non pubblicata** | **non maggiore del Maverick** (90–92 mm; 19,7 kg) | A sulle dimensioni; classe: proposta, non dato |

**Piattaforma aerea nel registro**: per tutte e sette le voci il campo `users` contiene **Paesi**, non
piattaforme. Nessuna di queste armi compare in `AIRCRAFT_LOADOUTS` (verificato: le uniche occorrenze nel
file sono la tabella effetti e la voce di registro, nessuna nei loadout). Per il **Mistral** l'unica
versione aviolanciata documentata dalle fonti è l'**ATAM**, impiegata su elicotteri (Gazelle, Rooivalk,
Tiger) come arma aria-aria a corto raggio; il registro invece gli assegna `task` `["Strike",
"Anti_Ship"]`, che è coerente con l'uso contro mezzi veloci (FIAC) ma non con la sua natura di SAM.
`users` Mistral: France, Belgium, Brazil, Chile, Cyprus, Egypt, Finland, Indonesia, South Korea, Norway,
Singapore.

## 2) Dettaglio per voce

### 2.1 `AGM-114` (Hellfire) — variante AGM-114 generico / famiglia A-B-C

- **Denominazione cercata**: `AGM-114` (registro). **Trovato**: famiglia AGM-114 Hellfire; il registro non
  distingue la variante. `start_service` 1984, `range` 8 km, `warhead` 9 kg.
- **Diametro**: 7 in = **180 mm** — Wikipedia, https://en.wikipedia.org/wiki/AGM-114_Hellfire — estratto
  letterale (infobox): "Length64 in (1.6 m)Diameter7 in (180 mm)". Conf. A.
  Seconda fonte concorde: 17,8 cm = **178 mm** — Andreas Parsch, designation-systems.net,
  https://www.designation-systems.net/dusrm/m-114.html — estratto (tabella): "Diameter17.8 cm (7 in)".
  Il valore 180 mm della Wikipedia è arrotondato; 178 mm è il valore in cm della tabella. **Nessuna
  discordanza sostanziale** (7 in = 177,8 mm).
- **Lunghezza**: **1,63 m** — Wikipedia, estratto: "Length64 in (1.6 m)"; designation-systems, estratto:
  "Length1.63 m (64 in)". Conf. A.
- **Massa al lancio**: **45–49 kg** (famiglia) / **45,7 kg** per AGM-114B/C — Wikipedia, estratto:
  "Mass100–108 lb (45–49 kg)[3]"; designation-systems, estratto (tabella, colonna AGM-114B/C):
  "Weight45.7 kg (100 lb)". Conf. A.
- **Testata (per coerenza col registro)**: 8 kg nella famiglia A/B/C, 9 kg nella K — designation-systems,
  estratto: "Warhead8 kg (18 lb) shaped-charge". Il `warhead` 9 kg del registro è quindi della K/L, mentre
  `start_service` 1984 e `range` 8 km sono della A/B/C. Ingombri invariati.
- **RCS**: nessuna delle pagine consultate pubblica la RCS del missile. **Non trovata**.
- **Classe**: `tactical` — missile guidato aria-superficie a corto raggio (8 km), non `cruise` (non ha volo
  autonomo a lunga distanza), non `arm` (non è antiradar), non `anti_ship` (la `task` `Anti_Ship` del
  registro riflette l'uso secondario contro unità navali, non la classe del missile). Ipotesi del piano
  **confermata**.
- **Confronto ancore**: 178–180 mm < 304,8 mm e 45,7 kg < 218,25 kg → **non maggiore del Maverick**.

### 2.2 `BGM-71D` (TOW 2) — variante BGM-71D

- **Denominazione cercata**: `BGM-71D`. **Trovato**: BGM-71D = **TOW 2** (la tabella Wikipedia lo dice
  esplicitamente). Attenzione: `start_service` 1970 nel registro è l'anno del **Basic TOW**, non del TOW 2
  (1983); `warhead` 6,14 kg è il valore del **BGM-71F** (EFP), mentre il TOW 2 (BGM-71D) ha 5,9 kg. Sono
  incoerenze interne del registro, da segnalare nel blocco 1.
- **Diametro**: **152 mm** — Wikipedia, https://en.wikipedia.org/wiki/BGM-71_TOW — estratto (infobox):
  "Diameter152 mm". Conf. A. (FAS conferma indirettamente: "TOW 2 Missile has a 6-inch diameter warhead",
  cioè 152 mm di testata.)
- **Lunghezza**: **1,17 m** sonda chiusa, **1,51 m** sonda estesa — Wikipedia, estratto (tabella varianti):
  "BGM-71D BGM-71C variant; TOW-2, improved guidance, motor and enlarged main warhead 1.51 m (probe
  extended)1.17 m (probe folded)". Conf. A.
- **Massa al lancio**: **21,5 kg** — Wikipedia, estratto (tabella): "21.5 kg"; seconda fonte concorde:
  FAS, http://man.fas.org/dod-101/sys/land/tow.htm, estratto: "TOW 2 Missile:  		47.4 pounds (21.52
  kilograms)". Conf. A.
- **RCS**: **non pubblicata**.
- **Classe**: `tactical` — ATGM a guida SACLOS, 3–3,75 km, impiegato anche da elicotteri; non `anti_ship`
  anche se il registro ha `task` `SEAD`/`Strike` (il TOW non è un ARM né un missile antinave). Ipotesi
  **confermata**.
- **Confronto ancore**: 152 mm e 21,5 kg → **non maggiore del Maverick**.

### 2.3 `9M114` (Shturm / Kokon) — variante 9M114 / 9K114

- **Denominazione cercata**: `9M114`. **Trovato**: **9M114 Kokon**, missile del sistema **9K114 Shturm**
  (NATO AT-6 Spiral). Il nome comune "Shturm" del piano è **confermato** (è il nome del sistema, non del
  missile). Il `range` 7 km del registro non è quello del Kokon base (5 km) ma della variante **9M114M2**
  (7 km, secondo la tabella delle varianti). Gli ingombri restano quelli del corpo Kokon.
- **Diametro**: **130 mm** — Wikipedia, https://en.wikipedia.org/wiki/9K114_Shturm — estratto: "Diameter:
  130 mm (5.1 in)". Conf. A. Seconda fonte: Missilery.info, https://en.missilery.info/missile/shturms/9m114
  — estratto (tabella): "Caliber, mm 130".
- **Lunghezza**: **1.625 mm** (Wikipedia: "Length: 1,625 mm (5.3 ft)") **oppure 1.830 mm** (Missilery:
  "Length, mm 1830"; airwar.ru riporta "1830-1840"). **Discordanza da riportare, non risolta**.
- **Massa**: **31,4 kg** (peso del missile, Wikipedia: "Launch weight: 31.4 kg (69 lb)") oppure **46,5 kg**
  (Missilery: "Mass with launch tube-container, kg 46.5"). Non è una discordanza: la seconda include il
  tubo di lancio. Airwar.ru dà "31,4 - 35,4" per la massa (probabilmente secondo variante).
- **RCS**: **non pubblicata**.
- **Classe**: `tactical` — ATGM a corto raggio (5–7 km), impiegato da elicotteri e veicoli; il registro ha
  `task` `Anti_Ship` perché esiste una versione navale imbarcata (Wikipedia: "There is also a shipborne
  version of the missile"), ma la classe del missile resta `tactical`. Ipotesi **confermata**.
- **Confronto ancore**: 130 mm; 31,4 kg (o 46,5 kg col tubo) → **non maggiore del Maverick**.

### 2.4 `9M120` (Ataka) — variante 9M120 base

- **Denominazione cercata**: `9M120`. **Trovato**: **9M120 Ataka** (NATO AT-9 Spiral-2), variante base con
  testata tandem HEAT da 7,4 kg. Il nome comune "Ataka" è **confermato**. `range` 6 km e `warhead` 7,4 kg
  del registro coincidono con la variante base.
- **Diametro**: **130 mm** — Wikipedia, https://en.wikipedia.org/wiki/9M120_Ataka — estratto (infobox):
  "Mass49.5 kg (109 lb)Length1,830 mm (72 in)Diameter130 mm (5.1 in)". Conf. A.
- **Lunghezza**: **1.830 mm** — stessa fonte, estratto: "Length1,830 mm (72 in)". Seconda fonte (airwar.ru,
  http://www.airwar.ru/weapon/aat/shturm.html, pagina in windows-1251 illeggibile nel testo ma con numeri
  ASCII leggibili): nella tabella compaiono "1830-1840", "130", "46 -46,5"; conferma indiretta di calibro
  130 mm e lunghezza ≈1.830 mm. Conf. A.
- **Massa**: **49,5 kg** — Wikipedia, estratto: "Mass49.5 kg (109 lb)". Conf. M: airwar.ru riporta
  "46 -46,5" kg (v. Discordanze); la massa 49,5 kg non è quindi confermata da una seconda fonte.
- **RCS**: **non pubblicata**.
- **Classe**: `tactical` — ATGM a corto raggio (6 km) per elicotteri e veicoli; `Anti_Ship` nel registro è
  uso secondario. Ipotesi **confermata**.
- **Confronto ancore**: 130 mm e 49,5 kg → **non maggiore del Maverick**.

### 2.5 `9M120-F` (Ataka termobarico) — variante 9M120F

- **Denominazione cercata**: `9M120-F`. **Trovato**: **9M120F**, la variante Ataka con **testata
  termobarica** (9,5 kg di equivalente TNT), per fanteria e bunker. La grafia corretta è senza trattino.
- **Dimensioni specifiche**: **non pubblicate separatamente** nella tabella Wikipedia (le celle
  lunghezza/diametro/massa della riga 9M120F sono vuote). Poiché la famiglia usa la stessa cellula del
  9M120 [S: ragionamento, non dato], si riportano 130 mm / 1.830 mm / ≈49,5 kg **marcati [S]**.
  Wikipedia, estratto (tabella varianti): "9M120F Anti-personnel variant Thermobaric warhead with 9.5 kg
  (21 lb) TNT equivalent —N/a 1–5.8 km (0.62–3.60 mi)". Conf. **B** (dato specifico [S]).
- **Testata**: 9,5 kg equivalente TNT (termobarica) — Wikipedia, https://en.wikipedia.org/wiki/9M120_Ataka.
- **RCS**: **non pubblicata**.
- **Classe**: `tactical` — stessa famiglia, ruolo antipersonale/bunker a corto raggio. Ipotesi
  **confermata**. La distinzione `9M120` / `9M120-F` è solo di testata.
- **Confronto ancore**: 130 mm / ≈49,5 kg [S] → **non maggiore del Maverick**.

### 2.6 `Hot-3` (HOT 3) — variante HOT-3

- **Denominazione cercata**: `Hot-3`. **Trovato**: **HOT-3** (Euromissile, ora MBDA), variante con testata
  tandem HEAT del 1998. Il registro ha `start_service` 1978 (HOT 1) ma il nome impone la HOT-3; ingombri e
  massa sono quelli della HOT-3. `warhead` 6 kg nel registro vs 6,48 kg reali: approssimazione.
- **Diametro**: **150 mm** (0,15 m) — Wikipedia, https://en.wikipedia.org/wiki/HOT_(missile) — estratto
  (infobox): "Mass24.5 kgLength1.30 mDiameter0.15 m". Conf. M (una secondaria). Tabella stessa pagina:
  "HOT-3 1.30 150 0.31 24.5[27] 6.48 tandem HEAT 1250 75–4,300".
- **Lunghezza**: **1,30 m** — Wikipedia, estratto: "Length1.30 m"; tabella: "HOT-3 1.30".
- **Massa**: **24,5 kg** — Wikipedia, estratto: "Mass24.5 kg"; **discordanza interna alla stessa pagina**:
  "Various sources show the weight varying from 23.5 to 32.5 kilograms." → riportare entrambe, conf. M.
- **RCS**: **non pubblicata**.
- **Classe**: `tactical` — ATGM a corto raggio (4,3 km) per veicoli ed elicotteri; non `anti_ship` anche se
  il registro ha `task` `Anti_Ship`. Ipotesi **confermata**.
- **Confronto ancore**: 150 mm e 24,5 kg (o 32,5 kg) → **non maggiore del Maverick** in ogni caso.

### 2.7 `Mistral` (MANPADS / ATAM) — variante Mistral 1/2

- **Denominazione cercata**: `Mistral`. **Trovato**: famiglia **Mistral** (Matra/MBDA), missile SAM IR a
  cortissimo raggio. Il registro lo classifica `type: ASM`, `task: ["Strike", "Anti_Ship"]`, `range` 6 km,
  `start_service` 1985: il raggio 6 km e l'anno indicano **Mistral 1/2** (Mistral 1 in servizio dal 1990;
  Mistral 3 = 8 km). **ANOMALIA confermata**: non è un missile aria-superficie; è un SAM portatile, con
  versione aviolanciata **ATAM** (aria-aria) su elicotteri.
- **Diametro**: **90 mm** — Wikipedia, https://en.wikipedia.org/wiki/Mistral_(missile) — estratto
  (infobox): "Mass19.7 kg [2]Length 1.86 m 1.88m (including initial booster)[3]Diameter90 mm". Conf. A
  come dato, ma **discordanza** con la fonte primaria MBDA: "**~92mm**" (v. sotto).
- **Lunghezza**: **1,86 m** (Wikipedia) / **1,88 m incluso il motore di lancio** — MBDA, datasheet
  "MISTRAL 3", https://www.mbda-systems.com/media/19388/download — estratto (testo del PDF, tabella
  "Technical characteristics"): "Length:  1.88m (incl. launch motor)".
- **Massa**: **19,7 kg** (Wikipedia: "Mass19.7 kg") / "less than 20kg" — MBDA, estratto: "Weight: less than
  20kg". Concordi in sostanza. **Massa senza booster**: non pubblicata separatamente; il motore di lancio è
  compreso nei valori indicati (MBDA: "1.88m (incl. launch motor)").
- **Testata**: 2,95 kg (Wikipedia: "Warhead weight2.95 kg") / 3kg — MBDA, estratto: "3kg warhead".
- **RCS**: **non pubblicata**.
- **Classe**: **proposta `sam`** (fuori dalle quattro classi del compito). Motivazione: è un missile
  superficie-aria a guida IR, non un'arma aria-superficie; §2.3 della Proposta deriva i SAM a `sam` e li
  dichiara non bersaglio. L'ipotesi del piano (`tactical piccolo`) è quindi **contestata**: `tactical`
  descriverebbe solo il raggio, non il ruolo. La versione ATAM è aria-aria, quindi al più `aam`, mai
  `anti_ship`. Se l'utente vuole comunque tenerlo nello schema a quattro classi, va deciso esplicitamente
  e motivato, non dedotto dai dati.
- **Piattaforma**: l'ATAM è la versione per elicotteri (Gazelle, Rooivalk, Tiger), come arma **aria-aria**
  a corto raggio — Wikipedia, estratto: "ATAM: Helicopter version used as an air-to-air weapon with 2
  missiles on each module." Nel registro non c'è alcun loadout che lo impieghi.
- **Confronto ancore**: 90–92 mm e 19,7 kg → **non maggiore del Maverick**.

## 3) Discordanze fra fonti

1. **AGM-114 diametro**: 180 mm (Wikipedia, 7 in arrotondati) vs 178 mm (designation-systems, 17,8 cm).
   Non sostanziale: 7 in = 177,8 mm.
2. **9M114 lunghezza**: **1.625 mm** (Wikipedia) vs **1.830 mm** (Missilery.info, e "1830-1840" in
   airwar.ru). Non risolta; la massa 31,4 kg (Wikipedia) è il missile, 46,5 kg (Missilery) è col tubo.
3. **HOT-3 massa**: 24,5 kg (infobox e tabella Wikipedia) vs "23.5 to 32.5 kilograms" (nota della stessa
   pagina). Riportate entrambe.
4. **Mistral diametro**: 90 mm (Wikipedia) vs "~92mm" (MBDA, fonte primaria). Riportate entrambe.
5. **9M120 massa**: **49,5 kg** (Wikipedia) vs **46–46,5 kg** (airwar.ru, numeri ASCII della tabella). Non
   risolta; entrambe riportate.
6. **Incoerenze registro vs fonti** (non sono discordanze fra fonti, ma vanno segnalate al blocco 1):
   - `BGM-71D`: `start_service` 1970 = Basic TOW, non TOW 2 (1983); `warhead` 6,14 kg = BGM-71F, non
     BGM-71D (5,9 kg).
   - `Hot-3`: `start_service` 1978 = HOT 1; HOT-3 entrò in servizio nel 1998; `warhead` 6 kg vs 6,48 kg.
   - `Mistral`: `start_service` 1985 vs Mistral 1 dal 1990; `type` ASM e `task` Anti_Ship per un SAM.
   - `9M114`: `range` 7 km = variante 9M114M2, non Kokon base (5 km).
   - `9M120-F`: `range` 6 km del registro vs **1–5,8 km** della tabella Wikipedia per la variante F.

## 4) Cosa non ho trovato / non ho potuto verificare

- **RCS**: non pubblicata per **nessuna** delle sette voci. Nessuna pagina consultata (Wikipedia, FAS,
  designation-systems, Missilery, MBDA) riporta la sezione radar equivalente. Voce lasciata "non trovata".
- **9M120F — dimensioni e massa specifiche**: non pubblicate separatamente; ho usato la cellula del 9M120
  marcandole **[S]**. Se il blocco 1 vuole un dato per la variante F, serve una fonte tecnica russa
  (es. manuale Degtyarev/KBM) non raggiunta in questa sessione.
- **9M114 — lunghezza**: le due fonti discordano (1.625 vs 1.830 mm); non ho trovato una terza fonte
  autorevole che sciolga il dubbio.
- **HOT-3 — massa**: la stessa pagina Wikipedia ammette un intervallo 23,5–32,5 kg senza indicare la
  variante; non ho una seconda fonte indipendente.
- **Mistral — variante esatta**: il registro (6 km, 1985) non coincide né con Mistral 1 (1990) né con
  Mistral 3 (8 km); ho assunto Mistral 1/2, ma è un'inferenza [S] basata su raggio e anno.
- **Piattaforma aerea**: `users` nel registro elenca solo Paesi; **non** c'è una piattaforma. Nessuna delle
  sette armi è in `AIRCRAFT_LOADOUTS`. Per il Mistral l'unica piattaforma aviolanciata documentata è
  l'elicottero (ATAM), non un aereo.
- **airwar.ru**: pagina raggiunta ma in windows-1251 illeggibile nel testo; ho letto solo i numeri ASCII
  della tabella (calibro 130, lunghezza 1830-1840, masse 31,4-35,4 e 46-46,5). Non ho ricostruito il testo.
- **METIS/Fenix Insight (9M120F)**: pagina raggiunta ma le specifiche sono dietro paywall; usata solo per
  confermare che la variante è termobarica.
- **FAS AGM-114 e FAS Mistral**: URL tentati `man.fas.org/dod-101/sys/smart/agm-114.htm` e
  `man.fas.org/dod-101/sys/missile/mistral.htm` → **404**. Ripiegato su designation-systems.net e MBDA.
- **Siti dei costruttori**: la pagina MBDA "Mistral family" e la pagina "ATAM" restituiscono HTML senza le
  specifiche nel testo estratto (menu e contenuti dinamici); il datasheet PDF è invece leggibile.

## 5) Metodo (pagine tentate/lette, passi)

**Come ho cercato**: `websearch` non disponibile; ho usato `webfetch` su URL noti e su pagine di risultati
`https://html.duckduckgo.com/html/?q=...`, prendendo dai risultati **solo gli URL** (mai i dati). Le
pagine di risultati sono servite per scoprire: MBDA datasheet, Missilery.info, METIS, weaponsystems.net.

**Pagine lette con successo** (10):
1. https://en.wikipedia.org/wiki/AGM-114_Hellfire
2. https://en.wikipedia.org/wiki/BGM-71_TOW
3. https://en.wikipedia.org/wiki/9K114_Shturm
4. https://en.wikipedia.org/wiki/9M120_Ataka
5. https://en.wikipedia.org/wiki/HOT_(missile)
6. https://en.wikipedia.org/wiki/Mistral_(missile)
7. https://www.designation-systems.net/dusrm/m-114.html
8. http://man.fas.org/dod-101/sys/land/tow.htm
9. https://en.missilery.info/missile/shturms/9m114
10. https://www.mbda-systems.com/media/19388/download (datasheet PDF MISTRAL 3)

**Pagine lette solo in parte / con problemi** (4):
- http://www.airwar.ru/weapon/aat/shturm.html (windows-1251: solo numeri ASCII)
- https://metis.fenixinsight.com/munition/missile/9m120f (paywall)
- https://www.mbda-systems.com/products/force-protection/mistral-family/mistral-3 (HTML senza specifiche)
- https://www.mbda-systems.com/products/force-protection/mistral-family/mistral-atam (HTML senza specifiche)

**URL tentati e falliti**: `https://en.wikipedia.org/wiki/9M114_Shturm` (404),
`http://man.fas.org/dod-101/sys/smart/agm-114.htm` (404),
`http://man.fas.org/dod-101/sys/missile/mistral.htm` (404),
`https://weaponsystems.net/system/522-9K114+Shturm` (trasport error),
`https://www.mbda-systems.com/products/mistral-family-of-vshorad-systems/` (404).
**Pagine di risultati DuckDuckGo consultate**: 3 (per 9M120F, per 9M114/weaponsystems, per Mistral/MBDA).

**Passi usati**: 38 chiamate di strumento (letture di piano/registri incluse) e **14 pagine web**
scaricate (10 lette integralmente, 4 parziali), oltre a 3 pagine di risultati.

**Sintesi**: tutte e sette le voci sono **molto più piccole del Maverick** (diametro 90–180 mm, massa
19,7–49,5 kg), quindi con il "metro del Maverick" la proposta è `ad_detectable` False per tutte; le
ipotesi di classe `tactical` sono confermate per i sei ATGM (con la precisazione che il registro confonde
varianti e assegna `Anti_Ship`/`SEAD` impropri), mentre per il **Mistral** la classe corretta è **`sam`**:
l'ipotesi `tactical` del piano va contestata e la voce trattata come anomalia (SAM in un registro ASM).