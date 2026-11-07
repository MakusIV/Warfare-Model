# Ricerca dati — Blocco 0 BI, M1 (riduzione incertezza su 7 voci discordi)

Agente: `oc-researcher` (DeepSeek V4.1 Flash). File di uscita unico autorizzato.
Scopo: ridurre l'incertezza su diametro/massa di 7 voci dei registri `MISSILES_ASM`, usando fonti
**indipendenti** da quelle già usate dalle bozze L1–L7. Per ogni voce riporto la variante esatta del
registro, i valori, l'URL preciso, un estratto **copiato letteralmente** (max 25 parole) e la confidenza
A/M/B. Le voci del registro sono lette da `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py`.

Regola del metro (dal compito): "non maggiore del Maverick" = diametro ≤ 304,8 mm **e** massa ≤ 304 kg;
"non minore dell'Harpoon" = diametro ≥ 343 mm **e** massa ≥ 515,25 kg; altrimenti zona grigia.

---

## 1. Tabella riassuntiva

| voce | variante (registro) | diametro | massa | nuove fonti indipendenti | confidenza | cambia vs L1–L7? |
|---|---|---|---|---|---|---|
| AGM-65K (`:2569`) | AGM-65K (AGM-65G + seeker CCD) | 304,8 mm (12 in) | 306 kg (675 lb) — solo Wikipedia K; d-s non dà K | 0 nuove di massa K (d-s riletto: niente K) | A diametro / M massa | No (conferma 304–306) |
| Kh-25MR (`:3523`) | Kh-25MR izd.714 (radiocomando) | 275 mm | **299 kg** (missilery.info) | 1 (missilery.info) | A | **Sì**: 320 kg ru-wiki respinto |
| RB-05A (`:2115`) | Rb 05A (Saab 305) | 300 mm (0,30 m) | 304–305 kg | 2 (AEF/FMV, Astronautix) | A | **Sì**: 2 fonti nuove confermano |
| LD-10 (`:4644`) | LD-10 base (da SD-10/PL-12) | 200 mm / 203 mm | 200 kg / 234 kg | 0 utili (militarydrones solo portata/tesata) | M | No (massa/diametro ancora discordi) |
| Kormoran (`:2279`) | Kormoran 1 (1973, testata 165 kg) | 344 mm / 340 mm | **600 kg** | 2 (globalmilitary, cmano-db) | A massa / M diametro | **Sì**: 660 kg missilery respinto |
| Kh-22N (`:3243`) | Kh-22N (AS-4 Kitchen) | 920 mm (0,92 m) | 5.820 kg (5.635–5.900 per fonte) | 2 (Globalsecurity, weaponsparade) | A diametro / M massa | **Sì**: N = nucleare, 2 fonti concordi |
| KD-63 (`:4675`) | KD-63 / K/AKD-63 (ex YJ-63) | 0,76 m | ~2.000 kg | 0 (solo Globalsecurity riletta) | M (fonte unica) | No (nessuna seconda fonte trovata) |

---

## 2. Dettaglio per voce

### 2.1 AGM-65K (`Aircraft_Weapon_Data.py:2569`)

Voce del registro: `model "AGM-65K"`, `users` USA/South Korea/Taiwan, `task` Anti_Ship/Strike/SEAD,
`start_service` 1970, `warhead` 136 kg (# WDU-24/B), `range` 15 km, `max_speed` 320 m/s.
Variante: **AGM-65K = AGM-65G ricostruito con seeker CCD** (confermato).

- **Massa al lancio.** L'unica fonte che pubblica una massa **specifica della K** è la tabella delle
  varianti di Wikipedia EN: **306 kg (675 lb)**.
  - `https://en.wikipedia.org/wiki/AGM-65_Maverick`, tabella "Variants", colonna AGM-65K:
    "AGM-65F/G — 306 kg (675 lb) … AGM-65K — 306 kg (675 lb)". Estratto letterale:
    "306 kg (675 lb)" (riga della colonna K).
  - designation-systems **non** pubblica una massa K: la sua tabella "Specifications" copre solo
    "AGM-65A/B/D/E/F/G" e dà per F/G "304 kg (670 lb)". Non è una massa della K.
    `https://designation-systems.net/dusrm/m-65.html`: "Weight … 304 kg (670 lb)" (colonna F/G);
    il testo descrive "The AGM-65K is an AGM-65G upgraded with the CCD seeker" senza peso proprio.
  - Non trovata massa K da fonte primaria libera: le fact sheet USAF `af.mil` e US Navy `navy.mil`
    restituiscono **403 Forbidden**. La FAS (man.fas.org) era già stata usata in L1 (AGM-65G = 301,5 kg).
- **Diametro.** 12 in = **304,8 mm** (30,5 cm). Fonti concordi:
  - designation-systems: "Diameter 30.5 cm (12 in)";
  - Wikipedia EN: "Diameter 12 in (30 cm)".
  Confidenza **A**.

Sintesi: massa K = **306 kg** (Wikipedia, unica K-specifica); diametro 304,8 mm (concorde). Il valore di
riferimento "Maverick" del metro (304 kg / 304,8 mm) coincide con la K cellula G (304 kg, d-s). La
differenza 304 vs 306 kg è la precisione di arrotondamento in libbre (670 vs 675 lb). **Nessuna fonte
primaria libera per la massa K.**

### 2.2 Kh-25MR (`Aircraft_Weapon_Data.py:3523`)

Voce del registro: commento `# radar guided`, `users` USSR/Russia/India/Syria/Iraq/Libya/Algeria,
`task` Anti_Ship/Strike/SEAD, `start_service` 1975, `warhead` 140 kg, `range` 11 km, `max_speed` 870 m/s.
Variante: **Kh-25MR / X-25MR izdeliye 714, guida radiocomandata** (non "radar" in senso di ARH).

Fonte nuova (indipendente da ru-wiki, en-wiki, Astronautix, FAS, airwar): **Missilery.info**, scheda
dedicata del missile, che cita fonti russe primarie (Karpenko/Ganin, Shirokorad).
`https://en.missilery.info/missile/x25mr` — tabella "Characteristics":

- **Start weight, kg: 299**
- **case diameter: 275** (mm)
- **length: 3686** (mm); wingspan 755 mm; warhead 140 kg; max speed 870 m/s; range 2.5–10 km.

Estratti letterali: "Start weight , kg 299"; "case diameter 275".

Confronto (aggiorna §2.2 di L3):
- Massa: ru-wiki **320 kg** vs missilery.info **299 kg** vs Astronautix **300 kg** ("Gross mass 300 kg
  (660 lb)"). La massa **320 kg** di ru-wiki è un'eccezione (probabile confusione con la massa di famiglia
  316–320 kg di airwar.ru). Consenso: **~299–300 kg**.
- Diametro: **275 mm** confermato (missilery.info + en-wiki "27.5 cm" + Astronautix 0.27 m).

Confidenza **A** (massa 299 kg e diametro 275 mm, fonte dedicata con bibliografia russa + Astronautix
concorde). **Il dato ru-wiki 320 kg è respinto.**

### 2.3 RB-05A (`Aircraft_Weapon_Data.py:2115`) — e la inesistente "Rb 05E"

Voce del registro: `model "RB-05A"`, `users` Sweden, `seeker` "electro-optical", `task`
Anti_Ship/Strike/SEAD, `start_service` 1972, `end_service` 2005, `warhead` 160 kg, `range` 9 km, `speed` 340.
Variante: **Rb 05A** (Saab 305/305A, di serie, MCLOS radiocomandato con tracciante).

Due fonti nuove indipendenti da Wikipedia en/sv:

1. **AEF (Flygvapnets historia)**, pagina sul Robot 05, compilata da Stig Hertze e basata su
   "Det bevingade verket, FMV" (1986) e Robotmuseet Arboga.
   `https://www.aef.se/Flygvapnet/Notiser/Robot_05_Notis.htm`:
   - "RB05 Längd 3,6 m" / "Vikt 305 kg". Estratto letterale: "Vikt 305 kg".
2. **Encyclopedia Astronautica**, "Rb 05".
   `http://www.astronautix.com/r/rb05.html`:
   - "Gross mass 304 kg (670 lb)"; "Diameter 0.30 m (0.98 ft)"; "Height 3.60 m (11.80 ft)".
   Estratto letterale: "Gross mass 304 kg (670 lb)"; "Diameter 0.30 m (0.98 ft)".

- **Massa**: 305 kg (AEF/FMV) e 304 kg (Astronautix), oltre ai 305 kg di Wikipedia → **304–305 kg**,
  essenzialmente 305 kg. Confidenza **A** (due fonti indipendenti sono entrambe nuove).
- **Diametro**: **300 mm** (0,30 m, Astronautix) + Wikipedia 300 mm. Confidenza **A**. (AEF non dà il
  diametro.)
- **Lunghezza**: 3,6 m (AEF e Astronautix concordi).

Nota sul metro: diametro 300 < 304,8 mm ma massa 305 > 304 kg → resta **zona grigia** a 1 kg dal confine
della massa; i 305 kg sono ora confermati da due fonti indipendenti aggiuntive.

**"Rb 05E": non esiste come designazione storica.** Nessuna delle fonti nuove (AEF, Astronautix) né quelle
di L4 (robotmuseum.se, Wikipedia en/sv) elenca una variante "E". Le varianti note sono: Rb 05 (di serie,
= Rb 05A), **Rb 05B** (proposta TV, non adottata; si scelse l'AGM-65 Maverick), Rb 05C (proposta). "RB-05E"
resta una designazione del simulatore DCS/Heatblur, non una fonte storica. Confermato il giudizio di L4
(confidenza B per la voce RB-05E del registro).

### 2.4 LD-10 (`Aircraft_Weapon_Data.py:4644`)

Voce del registro: `model "LD-10"`, `users` China, `task` SEAD, `start_service` 2012, `warhead` 20 kg,
`range` 80 km, `max_speed` 600 m/s. Variante: **LD-10 base (雷電/雷电-10), derivato dall'SD-10/PL-12**.

Fonte nuova trovata: **militarydrones.org.cn** (sito cinese "China Defence Website").
`https://www.militarydrones.org.cn/ld-10-anti-radiation-missile-p00775p1.html`:
- "The LD-10 anti-radiation missile has a maximum range of **80 kilometers** and a warhead weighing **20 kilograms**".
  Estratto letterale: "has a maximum range of 80 kilometers and a warhead weighing 20 kilograms".
- Questa pagina conferma portata 80 km e testata 20 kg (coerenti col registro) ma **NON dà massa,
  lunghezza o diametro**.

Massa e diametro restano le due letture discordi di L4, senza una terza fonte:
- Massa: **200 kg** (zh-wiki, GlobalSecurity) vs **234 kg** (Deagel). Non risolto.
- Diametro: **200 mm** (zh-wiki) vs **203 mm** (Deagel). Non risolto (la differenza 3 mm è quasi certa
  arrotondamento dello stesso corpo del PL-12, che è 203 mm).

Non trovata una fonte primaria cinese (CASIC/AVIC/NORINCO) con massa/diametro: Baidu Baike restituisce
**403**. Confidenza **M** (complessivo). **Massa e diametro NON ulteriormente verificati con fonte nuova.**

### 2.5 Kormoran (`Aircraft_Weapon_Data.py:2279`)

Voce del registro: `model "Kormoran"`, `users` Germany/Italy, `task` Anti_Ship, `start_service` 1973,
`warhead` 165 kg, `range` 30 km, `max_speed` 313 m/s. Variante: **Kormoran 1** (AS.34 Kormoran 1).
(Identificata da `start_service` 1973 + `warhead` 165 kg: la Kormoran 2 è del 1991 con testata 220 kg e
portata 35 km; il registro _non_ etichetta "1" o "2". Nota: l'utente "Italy" è insolito — Kormoran 1 fu
tedesca, MBB; non è compito di questa bozza correggerlo.)

Due fonti nuove indipendenti da Wikipedia e missilery.info:

1. **GlobalMilitary.net** `https://www.globalmilitary.net/missiles/kormoran/`:
   - "Diameter 344 mm (13.5 in)"; "Length 4,400 mm (173.2 in)"; "Weight 600 kg (1,323 lb)";
     "Warhead weight 165 kg (364 lb)". Estratto letterale: "Weight 600 kg (1,323 lb)"; "Diameter 344 mm (13.5 in)".
2. **CMANO database** `https://cmano-db.com/weapon/501/` (scheda "AS.34 Kormoran 1 (1978)"):
   - "Weight: 600 kg"; "Length: 4.4 m"; "Diameter: 0.34"; "Span: 1 m". Estratto letterale: "Weight: 600 kg".

- **Massa (Kormoran 1): 600 kg** — ora tre fonti concordi (Wikipedia EN, GlobalMilitary, CMANO) contro i
  660 kg di missilery.info (L5), che risultano un'eccezione. Confidenza **A**.
- **Diametro**: **344 mm** (Wikipedia EN + GlobalMilitary) vs **340 mm** (missilery.info + CMANO 0.34 m).
  Resta discorde 340 vs 344 mm (4 mm ≈ 1%). Confidenza **M**.
- **Lunghezza 4,40 m** (concorde).
- Testata 165 kg confermata (GlobalMilitary, Wikipedia, registro) → variante **Kormoran 1** confermata.

Sul metro: massa 600 kg > 515,25 kg (sopra l'ancora Harpoon), diametro 340–344 mm ≈ 343 mm (a cavallo).
Per la massa la voce è decisamente "non minore dell'Harpoon".

### 2.6 Kh-22N (`Aircraft_Weapon_Data.py:3243`)

Voce del registro: `model "Kh-22N"`, `users` USSR/Russia/Ukraine, `task` Anti_Ship, `start_service` 1967,
`warhead` 1000 kg, `range` 330 km, `max_speed` 1190 m/s. Variante: **Kh-22N** (AS-4 Kitchen).

**Designazione "N": due fonti nuove concordi dicono N = versione NUCLEARE (a guida inerziale).**

- GlobalSecurity (pagina Raduga Kh-22/AS-4): `https://www.globalsecurity.org/wmd/world/russia/as-4.htm`:
  "The Kh-22 missile came in three variants: 1. Kh-22N with a nuclear warhead and inertial guidance;
  2. Kh-22M with a conventional load for use against ships and with an active-radar …". Estratto
  letterale: "Kh-22N with a nuclear warhead and inertial guidance".
  La stessa pagina precisa le sottovarianti "X-22M, X-22MA, X-22N, X-22NA" e che la Kh-22NA è
  "inertial guidance system with route correction … digital terrain map".
- Weapons Parade: `https://weaponsparade.com/weapon/kh-22-as-4-kitchen-anti-ship-cruise-missile/`:
  "One of them is a 1,000 kg conventional shaped charge, designated as Kh-22, and the other is a nuclear
  type with a 350kt or 1Mt yield, and designated as Kh-22N." Estratto letterale: "nuclear type with a
  350kt or 1Mt yield, and designated as Kh-22N".

Quindi: **Kh-22N = nucleare** (GlobalSecurity + Weapons Parade, due fonti indipendenti, in accordo anche
con Wikipedia EN). La lettura alternativa russa (N = antinave convenzionale a bassa quota) resta in
Wikipedia RU/airwar.ru (già in L6). **Segnalazione per l'utente**: il registro assegna alla voce Kh-22N
`task Anti_Ship` e `warhead 1000 kg` (convenzionale), che non coincidono con la lettura "nucleare/inerziale"
(N); la variante antinave convenzionale a radar attivo è Kh-22M/MA. Non è compito di questa bozza correggere
il registro, ma la discrepanza va valutata.

**Massa e diametro:**

- **Massa 5.820 kg** — Weapons Parade: "Missile/bomb weight 5,820 kg" (per il 22 base/22N). Estratto
  letterale: "Missile/bomb weight 5,820 kg".
  Altre fonti (L6 + nuove): testpilot.ru "launch weight of missile was 5900 kg" (base, lunghezza 11,3 m);
  airwar.ru 5.635–5.780 kg; grokipedia ~5.800 kg. Intervallo **5.635–5.900 kg** a seconda di variante/fonte.
  Confidenza **M** (variante-dipendente).
- **Diametro 920 mm (0,92 m)** — Weapons Parade: "dimensions, (length x diameter) 11.65 x 0.92 meters".
  Estratto letterale: "11.65 x 0.92 meters". Concordano grokipedia ("diameter of 0.92 meters") e
  Wikipedia EN. Confidenza **A**.
- **Lunghezza 11,65 m** (Weapons Parade, grokipedia, Wikipedia EN) vs 11,3 m (testpilot.ru, base).

### 2.7 KD-63 (`Aircraft_Weapon_Data.py:4675`)

Voce del registro: `model "KD-63"`, `users` China, `task` Strike, `start_service` 2005, `warhead` 500 kg,
`range` 180 km, `max_speed` 250 m/s. Variante: **KD-63 / K/AKD-63 (ex YJ-63)**.

Ho riletto **interamente** la scheda Globalsecurity (già citata in L6) ottenendo i numeri precisi; **non
ho trovato una seconda fonte indipendente** (CSIS Missile Threat 404; missilery.info non ha la voce;
zh.wikipedia non ha una pagina KD-63 distinta; Baidu/Ecosia/Startpage inaccessibili o bot-check).

`https://www.globalsecurity.org/military/world/china/kd-63.htm`:
- **Lunghezza 7 m, diametro 0,76 m, apertura 2,4 m**: "Missile length 7 meters, Bullet diameter 0.76 m,
  Main wing wingspan 2.4 meters". Estratto letterale: "Missile length 7 meters, Bullet diameter 0.76 m".
- **Massa ~2.000 kg**: "the total weight is about 2000 kg" e "the KD-63 weighs about 2 tons". Estratto
  letterale: "the total weight is about 2000 kg".
- **Piattaforma: SOLO bombardiere H-6** (versione H-6H). "the forces of the Chinese Air Force can carry
  KD-63 only the H-6 bomber". La pagina conferma la correzione di L6: NON è lanciabile da cacciabombardieri.
- Testata 500 kg; portata ~240 km; guida inerziale + radiocomando + TV "man-in-the-loop".

Confidenza **M** (fonte unica, sebbene dettagliata; "~2.000 kg" è dichiaratamente approssimato dalla
fonte stessa).

**Varianti KD-63 / KD-63B**: il registro separa KD-63 (`:4675`) e KD-63B (`:4856`). Le fonti pubbliche
lette (GlobalSecurity, Wikipedia YJ-6) conoscono solo "KD-63 / K/AKD-63 / YJ-63"; **nessuna menziona
"KD-63B"**. Quindi: la variante KD-63B esiste solo come voce di registro e i suoi dati specifici
(diametro/lunghezza/massa/piattaforme) restano **non trovati** (come in L6). Nessuna fonte disponibile
conferma una KD-63B né una sua possibile piattaforma diversa dall'H-6.

---

## 3. Discordanze fra fonti

1. **AGM-65K massa**: 306 kg (Wikipedia K) vs 304 kg (d-s F/G); FAS G = 301,5 kg. La K non ha una massa
   propria in d-s/FAS; tre fonti indipendenti collocano la cellula G-pesante fra 301,5 e 306 kg.
2. **Kh-25MR massa**: 320 kg (ru-wiki) vs **299 kg** (missilery.info) vs 300 kg (Astronautix). ru-wiki è
   l'outlier.
3. **RB-05 massa**: 305 kg (AEF/FMV, Wikipedia) vs 304 kg (Astronautix). Arrotondamento lb/kg, non
   contraddizione sostanziale.
4. **LD-10 massa/diametro**: 200 kg / 200 mm (zh-wiki, GlobalSecurity) vs 234 kg / 203 mm (Deagel). Non
   risolta da terza fonte.
5. **Kormoran massa**: 600 kg (Wikipedia, GlobalMilitary, CMANO) vs 660 kg (missilery.info). Diametro:
   344 mm (Wikipedia, GlobalMilitary) vs 340 mm (missilery.info, CMANO).
6. **Kh-22N designazione**: N = nucleare/inerziale (GlobalSecurity, WeaponsParade, Wikipedia EN) vs
   N = antinave convenzionale (Wikipedia RU, airwar.ru). **Massa**: 5.635–5.900 kg a seconda della
   variante/fonte. **Diametro**: 920 mm (3 fonti) vs 900 mm in alcune fonti russe.
7. **KD-63**: una sola fonte (GlobalSecurity) per 7 m / 0,76 m / ~2.000 kg; nessuna seconda fonte per
   confermare o smentire.

---

## 4. Cosa NON ho trovato / non ho potuto verificare

- **AGM-65K**: massa specifica della K da fonte primaria (USAF/Navy fact sheet) — `af.mil` e `navy.mil`
  danno **403 Forbidden**; nessuna fact sheet libera con la massa della sola K.
- **LD-10**: massa e diametro da una fonte diversa da Deagel e GlobalSecurity. militarydrones.org.cn
  conferma solo portata 80 km e testata 20 kg. Baidu Baike 403. Nessun foglio dati CASIC/AVIC/NORINCO
  accessibile.
- **KD-63 e KD-63B**: una **seconda fonte indipendente** (Janes/CSIS/enciclopedie cinesi/missilery) per
  i dati dimensionali del KD-63. CSIS `missile/yj-63` 404; missilery.info non ha la voce. La **KD-63B**
  resta non documentata da qualunque fonte pubblica.
- **Rb 05E**: nessuna conferma storica della designazione "E" (solo DCS/Heatblur).
- **RCS**: non pubblicata per nessuna delle 7 voci nelle pagine lette.
- Motori di ricerca secondari: DuckDuckGo (html e lite) è entrato in **blocco anti-bot** ("select all
  squares with a duck") dalla seconda metà della sessione; Bing restituisce risultati commerciali generati
  da AI irrilevanti; Startpage richiede JavaScript (Anubis); Ecosia 403; Baidu Baike 403.

---

## 5. Metodo

Ricerca effettuata con `webfetch` (nessun `websearch` disponibile). Per scoprire gli URL ho usato pagine di
risultati `html.duckduckgo.com` (fino al blocco anti-bot) e poi fonti note direttamente (designation-systems,
missilery.info, Globalsecurity, AEF/Flygvapnet, Astronautix, Weapons Parade, GlobalMilitary, CMANO,
militarydrones.org.cn, Wikipedia).

**Pagine tentate**: 39 passi `webfetch`. **Pagine lette con dati utili**: 18
(assiro: anche le pagine di risultati DDG sono state usate solo per gli URL, mai per i dati).
Pagine lette con contenuto rilevante: Astronautix Rb05, AEF Robot 05, designation-systems m-65, Wikipedia
AGM-65, airforce-technology AGM-65, missilery.info X-25MR, GlobalMilitary Kormoran, CMANO Kormoran 1,
WeaponsParade Kh-22, militarydrones.org.cn LD-10, Globalsecurity AS-4.htm, Globalsecurity KD-63.htm,
più 6 pagine di risultati DDG. Fallite (403/404/captcha/anti-bot) o senza dati: 21.

**Sintesi degli esiti** (vedi tabella §1): la ricerca M1 **risolve** la massa del Kh-25MR (299 kg, respinge
320 kg), del Kormoran (600 kg, respinge 660 kg), conferma la massa/diametro della RB-05A con due fonti
indipendenti nuove, conferma il diametro del Kh-22N a 920 mm e chiarisce (due fonti concordi) che la "N"
del Kh-22 sta per **nucleare**. Restano irrisolti: massa/diametro della **LD-10** (nessuna terza fonte) e
dati della **KD-63** (fonte unica Globalsecurity, nessuna seconda fonte; **KD-63B** non documentata).
Per l'**AGM-65K** la massa specifica della K è 306 kg (Wikipedia) ma manca una conferma primaria libera.