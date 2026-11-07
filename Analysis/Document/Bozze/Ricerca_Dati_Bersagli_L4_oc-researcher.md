# Ricerca dati — Blocco 0 BI, LOTTO L4 (ARM e RB 05 svedesi)

Bozza di `oc-researcher`, 2026-11-07. Fonti web lette in questa sessione; nessun valore inventato e nessuna
stima `[S]` usata: tutti i numeri sotto hanno un estratto letterale e un URL. `websearch` non disponibile:
ricerca con `webfetch`, pagine note e pagine risultati DuckDuckGo HTML (l'ultima ricerca ha incontrato la
verifica anti-bot; v. §5). Le due ancore (AGM-65D e AGM-84A aviolanciato) sono quelle fornite dal principale e
non sono state ricercate: qui vengono solo usate per il confronto.

Riferimenti nel repo (letti con `grep -n` / `sed -n`):
- §2.2 (tabella armi→classe) e §5.1 (blocco 0): `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`.
- `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` — voci `AIR_WEAPONS['MISSILES_ASM']`:
  `RB-05A` (riga 2115), `RB-05E` (2299), `AGM-45` (2219), `AGM-88` (2259), `Kh-58` (3272), `Kh-31P` (4012),
  `LD-10` (4644). Nessuna di queste voci è nei registri navali (`Ship_Weapon_Data.py` non contiene questi nomi).
- Decisione BI-3 letta in §4: ARM esclusi per le difese **terrestri**; per le navali vale il flag `ad_detectable`.

Ancore di confronto (non ricercate; dal compito):
- **Maverick AGM-65D**: diametro 304,8 mm, lunghezza 2,49 m, massa 218,25–220 kg.
- **Harpoon AGM-84A aviolanciato**: diametro 343 mm, lunghezza 3,79–3,85 m, massa 515,25 kg.

## 1) Tabella riassuntiva

| Voce (registro) | Variante cercata | Classe proposta (ipotesi del piano) | Diametro | Lunghezza | Massa al lancio | RCS | Confronto con le ancore | Confidenza |
|---|---|---|---|---|---|---|---|---|
| **AGM-45** (`:2219`) | AGM-45A/B Shrike; dati della **B** (vedi §2.1) | `arm` — **confermata**; proposta `ad_detectable` **False** | 203 mm | 3,05 m | 177 kg | non pubblicata | **non maggiore del Maverick** per diametro e massa (203 < 304,8 mm; 177 < 218,25 kg) → False | A (due secondarie concordi) |
| **AGM-88** (`:2259`) | AGM-88A/B/C HARM (non AARGM-ER) | `arm` — **confermata**; **zona grigia**, proposta **False** | 254 mm | 4,14–4,17 m | 360–361 kg | non pubblicata | **zona grigia**: 254 < 304,8 mm ma 360–361 > 218–220 kg; 254 < 343 mm e 360–361 < 515,25 kg; lunghezza 4,14–4,17 > 3,79–3,85 m | A (tre fonti concordi) |
| **Kh-58** (`:3272`) | **Kh-58U** (il registro dà `range` 250, commento "vers. U"); dimensioni dal **Kh-58E** (export dell'U) | `arm` — **confermata**; zona grigia **contestata**: proposta **True** | 380 mm | 4,8 m | 650 kg | non pubblicata | **non minore dell'Harpoon** (380 > 343 mm; 650 > 515,25 kg; 4,8 > 3,79–3,85 m) → True | A (primaria KTRV + Wikipedia concorde) |
| **Kh-31P** (`:4012`) | Kh-31P (izdeliye 77P) | `arm` — **confermata**; zona grigia **contestata**: proposta **True** | 360 mm | 4,7 m | 600 kg | non pubblicata | **non minore dell'Harpoon** (360 > 343 mm; 600 > 515,25 kg; 4,7 > 3,79–3,85 m) → True | A (primaria Rosoboronexport + Wikipedia concorde) |
| **LD-10** (`:4644`) | LD-10 (base, derivato SD-10/PL-12) | `arm` — **confermata**; zona grigia **contestata**: con i dati cinesi **non maggiore del Maverick** → **False**; con Deagel **zona grigia** | 200–203 mm | 3,5 m (zh-wiki/GlobalSecurity) / 4,1 m (Deagel) | 200 kg (zh-wiki/GlobalSecurity) / 234 kg (Deagel) | non pubblicata | 200 mm e 200 kg: **non maggiore del Maverick** (200 < 304,8; 200 < 218,25) → False; 203 mm e 234 kg: **zona grigia** (203 < 304,8 ma 234 > 218,25) | M sul complesso (fonti discordi su massa/lunghezza); **A sul diametro** (tutte 200–203 mm) |
| **RB-05A** (`:2115`) | Rb 05A (Saab 305A), MCLOS radiocomandato | `tactical` — **confermata** (ma "piccolo" solo per diametro); proposta **False** | 300 mm | 3,6 m | 305 kg | non pubblicata | **zona grigia**: 300 < 304,8 mm ma 305 > 218–220 kg; 300 < 343 mm e 305 < 515,25 kg; lunghezza 3,6 > 2,49 m → proposta False | A (due secondarie concordi) |
| **RB-05E** (`:2299`) | **"Rb 05E": designazione non trovata**; dati della famiglia Rb 05 (come Rb-05A) | `tactical` — **confermata** con riserva sul nome; proposta **False** | 300 mm | 3,6 m | 305 kg | non pubblicata | **zona grigia** come RB-05A (300 < 304,8 mm; 305 > 218–220 kg) → proposta False | B (designazione non verificata; dati di famiglia A) |

Sintesi del confronto: **le due ARM russe (Kh-58 e Kh-31P) superano l'ancora Harpoon in diametro e massa**,
quindi la "zona grigia" ipotizzata dal piano si risolve verso l'alto (**True**), non verso il basso. L'AGM-88
resta in zona grigia (diametro sotto il Maverick, massa sopra il Maverick e metà dell'Harpoon). L'AGM-45 è
sotto entrambe le ancore (False). L'LD-10 è più stretto e più leggero del Maverick secondo due fonti (False),
ma una terza fonte lo porta appena sopra la massa del Maverick (zona grigia): la discordanza va mostrata
all'utente. Gli RB 05 hanno diametro da 300 mm (sotto il Maverick di 4,8 mm) ma massa 305 kg (sopra il
Maverick del 39% e sotto l'Harpoon del 41%): zona grigia. Nessuna RCS è pubblicata per queste armi.

Nota sulla lunghezza: la regola del §2.5 cita "diametro e massa (e, se nota, lunghezza)". Se la lunghezza
fosse condizione necessaria, **AGM-45** (3,05 m), **LD-10** (3,5 m) e **RB-05** (3,6 m) non sarebbero "non
maggiori del Maverick" (2,49 m) e finirebbero in zona grigia nonostante diametro e massa favorevoli. Qui
seguo la definizione operativa del compito (diametro e massa) e segnalo il punto all'utente.

## 2) Dettaglio per voce

### 2.1 AGM-45 (`Aircraft_Weapon_Data.py:2219`)

Voce del registro: `model` "AGM-45", `users` USA/Israel/UK, `task` ["SEAD"], `start_service` 1966,
`end_service` 1992, `warhead` 66 kg, `range` 10 km, `max_speed` 680 m/s. **Variante**: il registro non
distingue A e B. Il `range` 10 km non coincide con nessuna delle due (A: 16 km; B: 40 km); la `warhead` 66 kg
è vicina alla WAU-9/B (66,6 kg) della **AGM-45B**. Ho quindi cercato la **AGM-45B** (specifiche più comuni).

- **Diametro 203 mm.** Fonti:
  - `https://en.wikipedia.org/wiki/AGM-45_Shrike`, infobox: "Diameter 8 inches (203 mm)". Confidenza **M**.
  - `https://www.designation-systems.net/dusrm/m-45.html`, tabella "Data for AGM-45B:": "Diameter20.3 cm (8 in)"
    (riga di tabella, resa senza spazio dal convertitore). Confidenza **M**.
  Due secondarie concordi → **A**.
- **Lunghezza 3,05 m.** Fonti: Wikipedia, "Length 10 feet (3.05 m)"; designation-systems, "Length3.05 m (10 ft)"
  (tabella). **A**.
- **Massa al lancio 177 kg.** Fonti: Wikipedia, "Mass 390 pounds (177.06 kg)"; designation-systems,
  "Weight177 kg (390 lb)" (tabella). **A**.
- **RCS: non pubblicata** (nessuna delle pagine lette riporta una RCS).
- Guida: "passive radar homing" (Wikipedia), coerente con il `task` SEAD.

Classe: **`arm`** — missile antiradiazione a guida radar passiva, non un missile tattico a corto raggio
generico. Ipotesi del piano **confermata**. Confidenza A.

Confronto: 203 mm < 304,8 mm e 177 kg < 218,25 kg → **non maggiore del Maverick** (proposta `ad_detectable`
False). In coerenza con BI-3, come ARM è comunque escluso dalle difese terrestri; il flag conta solo per le
navali.

### 2.2 AGM-88 (`Aircraft_Weapon_Data.py:2259`)

Voce del registro: `model` "AGM-88", `users` USA/Germania/Italia/Spagna/Grecia/Turchia/Israel/Australia/
Corea del Sud/Taiwan, `task` ["SEAD"], `start_service` 1985, `warhead` 66 kg (commento "WDU-21/B
blast-fragmentation"), `range` 80 km. **Variante**: la `range` 80 km corrisponde alla quota "Medium-level —
43 nmi (80 km)" della famiglia AGM-88A/B/C; non è un AARGM-ER (292 mm, 4,06 m, 467 kg). Ho cercato
**AGM-88A/B/C**.

- **Diametro 254 mm.** Fonti:
  - `https://en.wikipedia.org/wiki/AGM-88_HARM`, infobox: "Diameter 10 in (254 mm)".
  - `https://man.fas.org/dod-101/sys/smart/agm-88.htm`, specifiche: "Diameter: 10 inches (25.40 centimeters)".
  - `https://www.designation-systems.net/dusrm/m-88.html`, tabella: "Diameter 25.4 cm (10 in)".
  Tre concordi → **A**.
- **Lunghezza 4,14/4,17 m (discordanza).** FAS: "Length: 13 feet, 8 inches (4.14 meters)"; Wikipedia:
  "Length 13 ft 8 in (4.17 m)"; designation-systems: "Length 4.17 m (13 ft 8 in)". Riporto entrambe le
  coppie (4,14 e 4,17 m) senza scegliere: la differenza (3 cm) è compatibile con arrotondamenti, ma le fonti
  non sono identiche. Confidenza **A** sul valore "circa 4,1–4,2 m".
- **Massa al lancio 360/361 kg (discordanza).** FAS: "Launch Weight: 800 pounds (360 kilograms)";
  designation-systems: "Weight 360 kg (800 lb)"; Wikipedia: "Mass 796 lb (361 kg)". Due fonti danno 360,
  una 361: confidenza **A** su "360–361 kg".
- **RCS: non pubblicata** (nessuna delle pagine lette riporta una RCS).
- Nota: in FAS la `warhead` è "WAU-7/B, 143.51bs." mentre Wikipedia dà "Warhead weight 150 lb (68 kg)" e
  il registro 66 kg; designation-systems dà "66 kg (146 lb) WDU-21/B". Il registro (66 kg) è coerente con
  WGU/WDU-21/B; non è un dato dimensionale e non incide sul confronto.

Classe: **`arm`** — antiradiazione a guida radar passiva con memoria inerziale, velocità Mach 2+. Ipotesi del
piano **confermata**. Confidenza A.

Confronto: 254 mm < 304,8 mm, ma 360–361 kg > 218–220 kg e < 515,25 kg; 4,14–4,17 m > 3,79–3,85 m.
**Zona grigia** (tra le due ancore). Proposta: **False**, perché il diametro è 17% sotto il Maverick e la
massa è il 70% dell'Harpoon; è una scelta da approvare voce per voce (BI-6), non un automatismo.

### 2.3 Kh-58 (`Aircraft_Weapon_Data.py:3272`)

Voce del registro: `model` "Kh-58", `users` USSR/Russia/India/Siria/Libia/Iraq/Algeria, `task` ["SEAD"],
`start_service` 1975 con commento "# 1978 --1982 vers. U", `warhead` 149 kg, `range` 250 km, `max_speed`
1190 m/s. **Variante**: la `range` 250 km è quella della **Kh-58U** (la Kh-58 base è data "up to 120 km";
la E "46–200 km"). Le dimensioni pubblicate dalla KTRV sono per la **Kh-58E**, export della Kh-58U; non ho
trovato una tabella dimensionale separata per la U, quindi uso la E dichiarando l'approssimazione.

- **Diametro 380 mm.** Fonti:
  - `https://web.archive.org/web/20070928104055/http://eng.ktrv.ru/production_eng/323/511/516/`
    (Tactical Missiles Corporation, scheda Kh-58E, primaria): "body diameter 0.38" (riga di tabella).
  - `https://en.wikipedia.org/wiki/Kh-58`, infobox: "Diameter 38 cm (15.0 in)".
  Due concordi (una primaria) → **A**.
- **Lunghezza 4,8 m.** Fonti: KTRV, "length 4.8" (tabella); Wikipedia, "Length 480 cm (15 ft 9 in)". **A**.
- **Massa al lancio 650 kg.** Fonti: KTRV, "Missile launch weight, kg 650" (tabella); Wikipedia,
  "Mass 650 kg (1,430 lb)". **A**.
- **RCS: non pubblicata**.
- Nota: la scheda KTRV dichiara per la Kh-58E una `range` "46 – 200" km, non 250: il registro parla della U.
  Le dimensioni della cellula sono le stesse nella famiglia, ma non le ho verificate separatamente per la U.

Classe: **`arm`** — antiradiazione a guida radar passiva, velocità Mach 3,6. Ipotesi del piano **confermata**.
Confidenza A.

Confronto: 380 mm > 343 mm e 650 kg > 515,25 kg; 4,8 m > 3,79–3,85 m → **non minore dell'Harpoon**. La
"zona grigia" del piano è **contestata**: per la regola delle ancore il valore proposto è **True**. Resta
comunque un ARM, quindi escluso dalle difese terrestri da BI-3.

### 2.4 Kh-31P (`Aircraft_Weapon_Data.py:4012`)

Voce del registro: `model` "Kh-31P", `users` USSR/Russia/Bulgaria/Georgia/Siria/Libia/Iraq/Algeria/Polonia,
`task` ["SEAD"], `start_service` 1991, `warhead` 87 kg, `range` 110 km, `max_speed` 1000 m/s. **Variante**:
Kh-31P base (izdeliye 77P, AS-17 Krypton); la `range` 110 km e la `warhead` 87 kg coincidono con la scheda
Rosoboronexport. Non è la Kh-31PD/AD allungata (5,3 m).

- **Diametro 360 mm.** Fonti:
  - `http://www.roe.ru/en/production/aerospace-forces/air-weapons/guided-weapons/aviatsionnye-upravlyaemye-rakety-klassa-vozdukh-rls-aviatsionnye-protivoradiolokatsionnye-rakety/kh-31p/`
    (Rosoboronexport, primaria): "Dimensions: length/diameter/wingspan, m 4,7 х 0,36 х 0,914".
  - `https://en.wikipedia.org/wiki/Kh-31`, infobox: "Diameter 360 mm (14 in)".
  Due concordi (una primaria) → **A**.
- **Lunghezza 4,7 m.** Fonti: Rosoboronexport (stessa riga: "4,7 х 0,36"); Wikipedia: "Length Mod 1 : 4.7 m
  (15 ft 5 in)". **A**.
- **Massa al lancio 600 kg.** Fonti: Rosoboronexport: "Launch/warhead weight, kg 600/87±2,5"; Wikipedia:
  "Kh-31P :600 kg (1,320 lb)". **A**.
- **RCS: non pubblicata**.

Classe: **`arm`** — antiradiazione a guida radar passiva, statoreattore, Mach 3+. Ipotesi del piano
**confermata**. Confidenza A.

Confronto: 360 mm > 343 mm e 600 kg > 515,25 kg; 4,7 m > 3,79–3,85 m → **non minore dell'Harpoon**. Anche
qui la "zona grigia" del piano è **contestata**: proposta **True**.

### 2.5 LD-10 (`Aircraft_Weapon_Data.py:4644`)

Voce del registro: `model` "LD-10", `users` ["China"], `task` ["SEAD"], `start_service` 2012, `warhead`
20 kg, `range` 80 km, `max_speed` 600 m/s. **Variante**: LD-10 base (cinese, derivato dell'SD-10/PL-12).

- **Diametro 200–203 mm.** Fonti:
  - `https://zh.wikipedia.org/wiki/雷電-10反輻射飛彈`, tabella: "直径 0.2米".
  - `https://www.globalsecurity.org/military/world/china/ld-10.htm`, tabella: "diameter 0.2m".
  - `https://www.deagel.com/Weapons/LD-10/a003171`, specifiche: "Diameter 203 millimeter".
  Tutte concordano su 200–203 mm → **A** sul diametro.
- **Lunghezza 3,5 m oppure 4,1 m (fonti discordi).** zh-wiki: "长度 3.5米"; GlobalSecurity: "length 3.5 meters";
  Deagel: "Length 4.1 meter". Riporto entrambe, senza scegliere.
- **Massa al lancio 200 kg oppure 234 kg (fonti discordi).** zh-wiki: "重量 200公斤"; GlobalSecurity:
  "weight 200 kg"; Deagel: "MassWeight 234 kilogram". Riporto entrambe, senza scegliere. Nota: il `range`
  80 km del registro coincide con zh-wiki/GlobalSecurity ("射程大约为80千米" / "range of approximately 80
  kilometers"), mentre Deagel dà 60 km; questo suggerisce che la coppia 3,5 m/200 kg descriva la variante
  del registro, ma **non è una verifica** e non scelgo il valore.
- **RCS: non pubblicata**.

Classe: **`arm`** — antiradiazione leggera a guida radar passiva/attiva, derivata da un AAM. Ipotesi del piano
**confermata** (la classe non dipende dalla taglia). Confidenza A sulla classe, M sui numeri.

Confronto: con 200 mm e 200 kg → **non maggiore del Maverick** (entrambi sotto le ancore; proposta False);
con 203 mm e 234 kg → **zona grigia** (diametro sotto, massa sopra di 16 kg, molto sotto l'Harpoon). La
"zona grigia" ipotizzata dal piano è quindi **confermata solo dalla fonte Deagel** e **contestata dalle due
fonti cinesi/GlobalSecurity**. La discordanza va risolta dall'utente o con una fonte primaria cinese (non
trovata).

### 2.6 RB-05A (`Aircraft_Weapon_Data.py:2115`)

Voce del registro: `model` "RB-05A", `users` ["Sweden"], `seeker` "electro-optical", `task`
["Anti_Ship", "Strike", "SEAD"], `start_service` 1972, `end_service` 2005, `warhead` 160 kg, `range` 9 km.
**Variante**: **Rb 05A** (Saab 305A), la versione di serie con guida **MCLOS via radiolink** e tracciante
(la versione TV era solo il prototipo Rb 05B). Il campo `seeker` del registro ("electro-optical") **non
corrisponde** alle fonti: v. §3.

- **Diametro 300 mm.** Fonti:
  - `https://en.wikipedia.org/wiki/Saab_RB05`, infobox: "Diameter 0.3 m (11.8 in)".
  - `https://sv.wikipedia.org/wiki/Robot_05`, tabella: "Diameter 0,3 meter".
  Due concordi → **A**.
- **Lunghezza 3,6 m.** Fonti: Wikipedia EN "Length 3.6 m (11.8 ft)"; Wikipedia SV "Längd 3,6 meter". **A**.
- **Massa al lancio 305 kg.** Fonti: Wikipedia EN "Mass 305 kg (672 lb)"; Wikipedia SV "Vikt 305 kg". **A**.
- **RCS: non pubblicata**.
- Ruolo confermato dal museo: `https://robotmuseum.se/robotar/rb-05a/`: "RB 05A var en attackrobot avsedd
  för beväpning på flygplan AJ37 Viggen, för bekämpning av markmål, men var även användbar mot vissa sjömål."
  (fonte museale svedese; conferma il doppio uso terra/nave del registro).
- Velocità/portata: il museo conferma "RB 05A blev operativ 1972"; Wikipedia dà "Operational range 9 km
  (5.6 mi; 4.9 nmi)", coerente con il registro.

Classe: **`tactical`** — missile aria-superficie a corto raggio (9 km), guida MCLOS radiocomandata, con uso
secondario antinave. Ipotesi del piano **confermata** sulla classe. Confidenza A.

Confronto: 300 mm < 304,8 mm (di 4,8 mm) ma 305 kg > 218–220 kg (del 39%) e < 515,25 kg; 3,6 m > 2,49 m.
**Zona grigia**: la premessa del piano ("taglia pari o minore del Maverick") è **contestata dalla massa**,
non dal diametro. Proposta: **False** (diametro quasi identico al Maverick, massa meno del 60%
dell'Harpoon, corto raggio), da approvare voce per voce.

### 2.7 RB-05E (`Aircraft_Weapon_Data.py:2299`)

Voce del registro: `model` "RB-05E", `users` ["Sweden"], `task` ["Anti_Ship", "Strike", "SEAD"],
`start_service` 1972, `end_service` 2005, `warhead` 160 kg, `range` 9 km. **Variante**: la designazione
**"Rb 05E" non è stata trovata in nessuna fonte di riferimento**. La pagina del museo elenca solo RB05A e
RB05B/C; Wikipedia EN elenca Saab 305A (Rb 05A), 305B (Rb 05B, TV, prototipo) e 305C (Rb 05C, proposta).
L'unica occorrenza di "RB-05E" trovata è un video DCS (`https://www.youtube.com/watch?v=H1dB65NbWwU`,
titolo "DCS: AJS-37 Viggen [RB-05E Radio Controlled]"), cioé una designazione di simulatore, non una fonte
storica. I numeri sotto sono quindi quelli della **famiglia Rb 05** (identici al Rb 05A) e valgono per la
voce di registro solo come ipotesi.

- **Diametro 300 mm.** Fonti: Wikipedia EN "Diameter 0.3 m (11.8 in)"; Wikipedia SV "Diameter 0,3 meter".
  **A** per la famiglia, **B** per la voce "RB-05E".
- **Lunghezza 3,6 m.** Wikipedia EN "Length 3.6 m (11.8 ft)"; Wikipedia SV "Längd 3,6 meter". **A** famiglia.
- **Massa al lancio 305 kg.** Wikipedia EN "Mass 305 kg (672 lb)"; Wikipedia SV "Vikt 305 kg". **A** famiglia.
- **RCS: non pubblicata**.

Classe: **`tactical`** — come RB-05A. Ipotesi del piano **confermata** con riserva sul nome: se "RB-05E" è
davvero una variante Rb 05, resta un missile a corto raggio radiocomandato, non un ARM, e la classe
`tactical` è corretta. Confidenza **B** (designazione non verificata).

Confronto: **zona grigia** come RB-05A (300 < 304,8 mm; 305 > 218–220 kg) → proposta **False**, con la
stessa riserva.

## 3) Discordanze fra fonti

1. **AGM-45 — variante e portata.** Il registro dà `range` 10 km; le fonti danno 16 km (AGM-45A) e 40 km
   (AGM-45B). La `warhead` 66 kg del registro è vicina alla WAU-9/B (66,6 kg) della B, ma la portata non
   corrisponde a nessuna delle due. La variante esatta non è determinabile dal registro.
2. **AGM-45 — testata.** Wikipedia: 67,5 kg (MK 5 MOD 1 / MK 86 MOD 1) oppure 66,6 kg (WAU-9/B);
   designation-systems: 67,5 kg oppure 66,6 kg. Il registro (66 kg) arrotonda la WAU-9/B. Nessuna
   discordanza sostanziale.
3. **AGM-88 — lunghezza.** FAS "4.14 meters"; Wikipedia e designation-systems "4.17 m". Riportate entrambe.
4. **AGM-88 — massa.** FAS e designation-systems "360 kg"; Wikipedia "361 kg" (796 lb). Riportate entrambe.
5. **AGM-88 — testata.** FAS: "WAU-7/B, 143.51bs."; Wikipedia: 150 lb (68 kg); designation-systems: 66 kg
   (WDU-21/B). Il registro (66 kg) segue designation-systems. Non incide sulle dimensioni.
6. **Kh-58 — variante/portata.** Il registro dà 250 km (Kh-58U); la scheda KTRV della Kh-58E dà "46 – 200"
   km. Le dimensioni (4,8 m / 380 mm / 650 kg) sono quelle della E; non ho una tabella separata per la U.
7. **LD-10 — massa e lunghezza.** Due fonti (zh-wikipedia e GlobalSecurity) danno 200 kg / 3,5 m;
   Deagel dà 234 kg / 4,1 m. Il diametro è 200 mm per le prime due e 203 mm per Deagel. Il `range` del
   registro (80 km) coincide con le prime due, non con Deagel (60 km). **Non scelgo**: riporto entrambe.
8. **LD-10 — diritti/derivazione.** zh-wiki e GlobalSecurity concordano che deriva dall'SD-10/PL-12 e che
   il corpo è comune ("弹体通用"); GlobalSecurity sembra una traduzione della pagina cinese, quindi le due
   non sono del tutto indipendenti (per questo la confidenza complessiva è M, non A).
9. **RB 05 — designazione "E" e seeker.** Il registro `RB-05A` dichiara `seeker` "electro-optical"; le
   fonti dicono **MCLOS radiocomandato con tracciante** per la Rb 05A, e **TV** solo per il prototipo
   Rb 05B. La voce `RB-05E` non ha riscontro storico: sembra una designazione DCS. Segnalato, non corretto
   (non modifico i registri).
10. **RB 05 — massa.** 305 kg (Wikipedia EN/SV). Il museo non dà la massa; non c'è una seconda fonte
    indipendente oltre alle due Wikipedia (che condividono la stessa origine). Confidenza A secondo la
    regola "due secondarie concordi", ma con la riserva che le due pagine sono della stessa famiglia.

## 4) Cosa non ho trovato / non ho potuto verificare

- **RCS**: nessuna RCS pubblicata per AGM-45, AGM-88, Kh-58, Kh-31P, LD-10, RB-05A/E nelle pagine lette.
  Non ho cercato stime non ufficiali e non ne invento.
- **"RB-05E"**: nessuna fonte storica, militare o del costruttore. Solo un video DCS. Non ho potuto
  verificare se sia una variante reale, un errore di designazione o un nome di simulatore.
- **Kh-58U**: non ho trovato una scheda dimensionale specifica per la U; uso la Kh-58E (export della U).
  La portata del registro (250 km) non è quella della scheda KTRV (46–200 km).
- **AGM-45**: non ho trovato la scheda FAS (`man.fas.org/dod-101/sys/smart/agm-45.htm` restituisce 404) né
  una fonte primaria USAF raggiungibile; le due secondarie concordano.
- **LD-10**: non ho trovato una fonte primaria cinese (AVIC/CATIC) con i dati dimensionali; le fonti
  secondarie discordano su massa e lunghezza.
- **Kh-31P**: la pagina ktrv.ru (costruttore) dà errore di trasporto; ho usato Rosoboronexport (primaria)
  e Wikipedia (secondaria), concordi.
- **CSIS Missile Threat**: le URL provate (`/missile/kh-58/`, `/missile/kh-31/`) restituiscono 404; non ho
  trovato gli slug corretti e non ho insistito.
- **airwar.ru**: le URL provate (`/weapon/pvo/x58.html`, `/weapon/pvo/x31.html`) restituiscono 404; non ho
  riprovato con altri percorsi.
- **Ricerca DuckDuckGo**: l'ultima ricerca ("RB-05E" Heatblur) ha restituito la verifica anti-bot; le
  ricerche precedenti hanno funzionato. Dalle pagine risultati ho preso solo URL, mai dati.

## 5) Metodo (pagine tentate/lette, passi)

Strumenti: `webfetch` su pagine note e su `https://html.duckduckgo.com/html/?q=<ricerca>` per scoprire URL
(nessun dato preso dai risultati), più `grep -n`/`sed -n` sul repo. Nessun `websearch`.

Pagine lette con successo (dati):
1. `https://en.wikipedia.org/wiki/AGM-45_Shrike`
2. `https://www.designation-systems.net/dusrm/m-45.html`
3. `https://en.wikipedia.org/wiki/AGM-88_HARM`
4. `https://man.fas.org/dod-101/sys/smart/agm-88.htm`
5. `https://www.designation-systems.net/dusrm/m-88.html`
6. `https://en.wikipedia.org/wiki/Kh-58`
7. `https://web.archive.org/web/20070928104055/http://eng.ktrv.ru/production_eng/323/511/516/` (KTRV, Kh-58E)
8. `https://en.wikipedia.org/wiki/Kh-31`
9. `http://www.roe.ru/en/production/aerospace-forces/air-weapons/guided-weapons/aviatsionnye-upravlyaemye-rakety-klassa-vozdukh-rls-aviatsionnye-protivoradiolokatsionnye-rakety/kh-31p/` (Rosoboronexport)
10. `https://zh.wikipedia.org/wiki/雷電-10反輻射飛彈`
11. `https://www.globalsecurity.org/military/world/china/ld-10.htm`
12. `https://www.deagel.com/Weapons/LD-10/a003171`
13. `https://www.militarydrones.org.cn/ld-10-anti-radiation-missile-p00775p1.html` (solo testo, nessuna dimensione)
14. `https://en.wikipedia.org/wiki/Saab_RB05`
15. `https://sv.wikipedia.org/wiki/Robot_05`
16. `https://robotmuseum.se/robotar/rb-05a/` (Arboga Robotmuseum)
17. `https://web.archive.org/web/20180828004655/http://eng.ktrv.ru/production_eng/323/511/` (indice, sola navigazione)

Pagine tentate e fallite: `https://man.fas.org/dod-101/sys/smart/agm-45.htm` (404), `https://missilethreat.csis.org/missile/kh-58/` (404), `https://missilethreat.csis.org/missile/kh-31/` (404), `http://www.airwar.ru/weapon/pvo/x58.html` (404), `http://www.airwar.ru/weapon/pvo/x31.html` (404), `http://roe.ru/eng/catalog/aerospace-systems/air-to-air-missile/kh-31p/` (404), `http://www.roe.ru/en/production/...` vecchia URL (404); `https://ktrv.ru/...kh-31p.html` (errore di trasporto); ultima ricerca DuckDuckGo (verifica anti-bot).

Passi usati: **circa 49** chiamate a tool (16 letture del repo con `grep`/`sed`/`ls`, 29 `webfetch`, 1
scrittura della bozza, 2 modifiche e 1 `grep` di verifica). Pagine web lette con successo: **17**; di queste **14** hanno fornito i
dati dimensionali usati nella tabella, 1 (militarydrones) è solo descrittiva, 1 (archivio KTRV 323/511) è un
indice di navigazione e 1 (robotmuseum) ha confermato ruolo e data di servizio. Richieste web fallite: **8**
(6 risposte 404, 1 errore di trasporto, 1 verifica anti-bot di DuckDuckGo). Nessun valore è stato ricostruito
da pagine non lette.