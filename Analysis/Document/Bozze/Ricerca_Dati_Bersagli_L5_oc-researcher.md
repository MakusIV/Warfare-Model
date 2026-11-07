# Ricerca dati — Blocco 0 BI, LOTTO L5 (antinave aerei)

Bozza di `oc-researcher`, 2026-11-07. Fonti web lette in questa sessione; nessun valore inventato. `websearch`
non disponibile: ricerca con `webfetch` su pagine note e su pagine di risultati DuckDuckGo HTML. Le due ancore
(AGM-65D e AGM-84A aviolanciato) sono quelle fornite dal principale e non sono state ricercate: qui vengono solo
usate per il confronto.

Riferimenti nel repo (letti con `grep -n` / `sed -n`):
- §2.2 (tabella armi→classe) e §5.1 (blocco 0): `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`.
- `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` — voci `AIR_WEAPONS['MISSILES_ASM']`:
  `RB-15F` (riga 2190), `Kormoran` (2279), `RB-04E` (2369), `Sea Eagle` (2389), `RB-15` (2479), `Kh-31A` (3981),
  `Kh-35` (4043), `Kh-41` (4074). Nessuna di queste voci è nei registri navali (`Ship_Weapon_Data.py` non le
  contiene).

Ancore di confronto (non ricercate; dal compito):
- **Maverick AGM-65D**: diametro 304,8 mm, lunghezza 2,49 m, massa 218,25–220 kg.
- **Harpoon AGM-84A aviolanciato**: diametro 343 mm, lunghezza 3,79–3,85 m, massa 515,25 kg (556 kg nel testo
  CSIS; 691 kg è RGM/UGM con booster).

## 1) Tabella riassuntiva

| Voce (registro) | Variante cercata | Classe proposta (ipotesi del piano) | Diametro | Lunghezza | Massa al lancio | RCS | Confronto con le ancore | Confidenza |
|---|---|---|---|---|---|---|---|---|
| **RB-04E** (`:2369`) | RB 04E, versione per AJ 37 Viggen (1975) | `anti_ship` — **confermata** | 500 mm | 4,45 m (Wikipedia) / 4 453 mm (museo) | 625 kg (museo) / 600 kg (Wikipedia) | non pubblicata | **non minore dell'Harpoon** (500 > 343 mm; 600–625 > 515,25 kg) | A (diametro, lunghezza); M con discordanza (massa) |
| **RB-15** (`:2479`) | RB 15M / RBS 15 Mk I–II **navale e costiero** (non aviolanciato) | `anti_ship` — **confermata** | 500 mm | 4 334 mm (museo) / 4,35 m (Wikipedia) | 568 kg senza SRM, 746 kg con SRM | non pubblicata | **non minore dell'Harpoon** (500 > 343 mm; 568 > 515,25 kg) | A (diametro, massa) |
| **RB-15F** (`:2190`) | RB 15F, **aviolanciato** (AJ 37 Viggen, poi JAS 39) | `anti_ship` — **confermata** | 500 mm | 4,4 m (museo) / 4,35 m (Wikipedia, famiglia) | 565 kg (museo) / 568 kg (Wikipedia, Mk1 in flight) | non pubblicata | **non minore dell'Harpoon** (500 > 343 mm; 565–568 > 515,25 kg) | A (diametro, massa) |
| **Kormoran** (`:2279`) | **Kormoran 1** (1973, testata 165 kg); non Kormoran 2 (1991, 220 kg) | `anti_ship` — **confermata** | 344 mm (Wikipedia) / 340 mm (missilery) | 4,40 m (entrambe) | 600 kg (Wikipedia, Kormoran 1) / 660 kg (missilery) / 630 kg (Kormoran 2) | non pubblicata | **non minore dell'Harpoon** per massa (600–660 > 515,25 kg); diametro 340–344 mm ≈ 343 mm → sostanzialmente pari all'ancora alta | A (lunghezza); M con discordanza (diametro, massa, anno) |
| **Sea Eagle** (`:2389`) | BAe Sea Eagle P3T aviolanciato (1985) | `anti_ship` — **confermata** | 400 mm (entrambe) | 4,14 m (Wikipedia) / 4,10 m (missilery) | 580 kg (Wikipedia) / 600–730 kg (missilery) | non pubblicata | **non minore dell'Harpoon** (400 > 343 mm; 580–730 > 515,25 kg) | A (diametro); M con discordanza (lunghezza, massa) |
| **Kh-31A** (`:3981`) | Kh-31A, versione antinave (AS-17 Krypton); non Kh-31P | `anti_ship` — **confermata** | 360 mm (entrambe) | 4,7 m (entrambe) | 610 kg (entrambe) | non pubblicata | **non minore dell'Harpoon** (360 > 343 mm; 610 > 515,25 kg) | A (due secondarie concordi) |
| **Kh-35** (`:4043`) | Kh-35 base / 3M-24; dati della **versione aerea** (520 kg, 3,85 m) | `anti_ship` — **confermata** | 420 mm | 3,85 m (aerea) / 4,40 m (navale e elicottero) | 520 kg (aerea) / 610 kg (superficie) | non pubblicata | **non minore dell'Harpoon** per diametro (420 > 343 mm); massa aerea 520 kg > 515,25 kg di soli 4,75 kg (e < 556 kg CSIS) → zona grigia sul solo parametro massa | M (una secondaria; v. §3) |
| **Kh-41** (`:4074`) | Kh-41 (ASM-MSS), **Moskit 3M-80 aviolanciato** (Su-33/Su-34) | `anti_ship` — **confermata** | 760 mm (testpilot/airwar) / 800 mm (Wikipedia) | 9,385 m (testpilot/airwar) / 9,745 m (Wikipedia) | 3 950 kg (testpilot/airwar) / 4 500 kg (Wikipedia) | non pubblicata | **non minore dell'Harpoon** (760–800 mm; 3 950–4 500 kg) | A per i due concordi testpilot+airwar; M per Wikipedia (discorde) |

**Sintesi del confronto.** Tutte le voci del lotto sono **non minori dell'Harpoon** per massa (minimo 520 kg,
Kh-35 aereo, 4,75 kg sopra i 515,25 kg) e per diametro, con l'unica eccezione del Kormoran, che ha diametro
340–344 mm contro i 343 mm dell'ancora alta (differenza entro l'arrotondamento delle fonti) ma massa 600–660 kg,
nettamente superiore. Non c'è quindi nessuna voce che possa essere classificata "piccola" col metro del Maverick.
Le uniche due sfumature: (a) il Kormoran 1 è sostanzialmente **pari** all'ancora alta sul diametro e sopra sulla
massa; (b) il Kh-35 aereo ha massa appena sopra l'ancora di 515,25 kg, ma il CSIS riporta 556 kg per l'Harpoon:
se si usa 556 kg la massa del Kh-35 cade in zona grigia, mentre il diametro (420 mm) resta decisamente sopra
l'ancora alta.

**Classificazione.** Tutte le voci sono `anti_ship`; l'ipotesi del piano è **confermata** per tutte. Il fatto che
alcune fonti le chiamino "anti-ship cruise missile" descrive il profilo di volo (crociera autonoma) e **non**
contraddice `anti_ship`: la classe del piano distingue il ruolo (antinave) dal profilo (cruise), e il §2.2
assegna comunque queste voci ad `anti_ship`. Dettaglio per voce: RB-15/RB-15F **sì** "Anti-ship cruise missile"
(Wikipedia); Sea Eagle **sì** "cruises at speeds of Mach 0.85" e categoria "Anti-ship cruise missiles"; Kh-35
**sì** "subsonic cruise anti-ship missile"; Kh-41/Moskit **sì** "anti-ship cruise missile"; RB-04E **no**
("sea skimming ... anti-ship missile"); Kormoran **no** ("Medium-range, active radar homing air-to-surface
missile"); Kh-31A **no** ("supersonic anti-ship missile").

## 2) Dettaglio per voce

### 2.1 RB-04E (`Aircraft_Weapon_Data.py:2369`)

Voce del registro: `model` "RB-04E", `users` ["Sweden"], `task` ["Anti_Ship"], `start_service` 1975,
`end_service` 2000, `warhead` 300 kg, `range` 32 km, `max_speed` 306 m/s. Variante identificata: **RB 04E**
(Saab Robot 04E), la versione per l'AJ 37 Viggen entrata in servizio nel 1975: il museo conferma "RB 04E blev
operativ 1975" e il registro dà 1975. Non è la RB 04C/D.

- **Diametro 500 mm.** Fonte: `https://robotmuseum.se/robotar/rb-04e/`, tabella "Data": "Diameter 500 mm";
  `https://en.wikipedia.org/wiki/RB_04`, infobox: "Diameter 50 cm (20 in)". Due fonti concordi → **A**.
- **Lunghezza 4,45 m / 4 453 mm.** Fonti: `https://robotmuseum.se/robotar/rb-04e/`, tabella "Data":
  "Längd 4 453 mm"; `https://en.wikipedia.org/wiki/RB_04`, infobox: "Length 4.45 m (14 ft 7 in)". Concordi
  (arrotondamento) → **A**.
- **Massa al lancio 625 kg / 600 kg.** Fonti: `https://robotmuseum.se/robotar/rb-04e/`, tabella "Data":
  "Vikt 625 kg"; `https://en.wikipedia.org/wiki/RB_04`, infobox: "Mass 600 kg (1,300 lb)". **Discordanza**
  (25 kg, ~4%): riporto entrambe, non scelgo → **M** per ciascuna.
- **RCS: non pubblicata** (nessuna delle fonti consultate riporta una RCS).
- **Nota "cruise":** la fonte non usa la parola "cruise"; descrive un missile antinave "sea skimming" a guida
  radar attiva. Nessuna qualifica esplicita come cruise.

Classe: **`anti_ship`** — missile antinave aviolanciato, guida radar attiva, portata 32 km. Ipotesi del piano
**confermata**. Confronto: diametro 500 mm > 343 mm e massa 600–625 kg > 515,25 kg → **non minore dell'Harpoon**;
proposta `ad_detectable` **True**.

### 2.2 RB-15 (`Aircraft_Weapon_Data.py:2479`) e RB-15F (`:2190`)

Voci del registro:
- **RB-15**: `users` ["Sweden", "Finland", "Croatia"], `task` ["Anti_Ship"], `start_service` 1989,
  `warhead` 200 kg, `range` 70 km, `max_speed` 306 m/s.
- **RB-15F**: `users` ["Sweden"], `task` ["Anti_Ship"], `start_service` 1985, `warhead` 200 kg, `range` 75 km,
  `max_speed` 306 m/s.

**Differenza verificata.** `RB-15` corrisponde al **Robotsystem 15 navale/costiero** (RB 15M / RBS 15 Mk I–II,
lanciato da navi e batterie costiere; in Finlandia MTO 85); `RB-15F` è la **versione aviolanciata** (AJ 37
Viggen, poi JAS 39 Gripen). Fonte: `https://en.wikipedia.org/wiki/RBS_15`, sezione "Variants": "Air-launched:
RBS-15F, launched exclusively from Swedish fighters (AJS37 Viggen, Fpl AJ37 Viggen, JAS-39 Gripen)" e "Ship
launched: RBS15 Mk1"; `https://robotmuseum.se/robotar/rb-15f/`: "Roboten kunde bäras av Fpl AJS37 Viggen och nu
av Fpl JAS39 Gripen". Il registro tiene entrambe in `MISSILES_ASM` aerei, ma solo la F è aviolanciata: il
`users` di RB-15 (Finlandia, Croazia) è coerente con la versione navale/costiera.

**RB-15 (navale/costiero):**
- **Diametro 500 mm.** Fonte: `https://robotmuseum.se/robotar/rb-15m/`, tabella "Data robot": "Diameter 500 mm";
  `https://en.wikipedia.org/wiki/RBS_15`, infobox: "Diameter 500 mm (1 ft 8 in)". **A**.
- **Lunghezza 4 334 mm / 4,35 m.** Fonti: `https://robotmuseum.se/robotar/rb-15m/`, "Längd 4 334 mm";
  `https://en.wikipedia.org/wiki/RBS_15`, "Length 4,350 mm (14 ft 3 in)". Concordi → **A**.
- **Massa 568 kg senza SRM, 746 kg con SRM.** Fonte: `https://robotmuseum.se/robotar/rb-15m/`, tabella:
  "Vikt 568 kg (Exkl. SRM)", "Vikt SRM 178 kg", "Total vikt 746 kg"; `https://en.wikipedia.org/wiki/RBS_15`,
  infobox: "746 kg (1,645 lb) (with boosters)" / "568 kg (1,252 lb) (in flight)". Concordi → **A**. Per il
  confronto con l'ancora aviolanciata uso la massa **senza boosters, 568 kg**.
- **RCS: non pubblicata.**
- **Nota "cruise":** Wikipedia classifica la famiglia come "Anti-ship cruise missile" ("RBS 15 Mk1: Anti-ship
  cruise missile (air-launched and ship-launched)"). Quindi la fonte la qualifica anche cruise, ma il ruolo è
  antinave.

**RB-15F (aviolanciato):**
- **Diametro 500 mm.** Fonte: `https://robotmuseum.se/robotar/rb-15f/`, tabella "Data": "Diameter 500 mm";
  `https://en.wikipedia.org/wiki/RBS_15` dà 500 mm per la famiglia. **A**.
- **Lunghezza 4,4 m / 4,35 m.** Fonti: `https://robotmuseum.se/robotar/rb-15f/`, "Längd 4,4 m";
  `https://en.wikipedia.org/wiki/RBS_15`, "Length 4,350 mm" (dato di famiglia). Concordi entro 5 cm → **A**.
- **Massa 565 kg / 568 kg.** Fonti: `https://robotmuseum.se/robotar/rb-15f/`, tabella: "Vikt 565 kg";
  `https://en.wikipedia.org/wiki/RBS_15`, "568 kg (1,252 lb) (in flight)" per la Mk1. Concordi entro 3 kg →
  **A**.
- **RCS: non pubblicata.**
- **Nota "cruise":** vedi sopra, "Anti-ship cruise missile".

Classe: **`anti_ship`** per entrambe. Ipotesi del piano **confermata**. Confronto: diametro 500 mm > 343 mm;
massa 565–568 kg > 515,25 kg → **non minore dell'Harpoon**; proposta `ad_detectable` **True** per entrambe.
Nota sulle date: il registro dà `start_service` 1985 alla RB-15F e 1989 alla RB-15; il museo dà "RB 15F blev
operativ ... 1989" e la versione navale in produzione dal 1984 (Wikipedia: "first missiles were delivered to the
Navy in June 1984"). Le due date del registro sembrano quindi invertite rispetto alle fonti, ma la variante
identificata non cambia (v. §3).

### 2.3 Kormoran (`Aircraft_Weapon_Data.py:2279`)

Voce del registro: `model` "Kormoran", `users` ["Germany", "Italy"], `task` ["Anti_Ship"], `start_service` 1973,
`end_service` None, `warhead` 165 kg, `range` 30 km, `max_speed` 313 m/s. Variante identificata: **Kormoran 1**
(AS.34 Kormoran 1): il registro dà 1973 e testata 165 kg, che sono i dati della **Kormoran 1** (missilery dà
anno 1976, testata 160 kg, portata 30 km); la Kormoran 2 è del 1991 con testata 220 kg e portata 35 km. Il
`range` 30 km del registro coincide con missilery e non con i 23 km (Wikipedia, Kormoran 1) né con i 35 km
(Kormoran 2); `start_service` 1973, `warhead` 165 kg e il `range` 30 km indicano comunque la **Kormoran 1**.

- **Diametro 344 mm (Wikipedia) / 340 mm (missilery).** Fonti: `https://en.wikipedia.org/wiki/AS.34_Kormoran`,
  infobox: "Diameter 344 mm"; `https://en.missilery.info/missile/kormoran`, tabella "Characteristics":
  "The diameter of the rocket body, mm 340". **Discordanza** di 4 mm (1,2%), entro l'arrotondamento:
  riporto entrambe → **M**.
- **Lunghezza 4,40 m.** Fonti: `https://en.wikipedia.org/wiki/AS.34_Kormoran`, infobox: "Length 4.40 m";
  `https://en.missilery.info/missile/kormoran`, tabella: "The length of the rocket, mm 4400". Concordi → **A**.
- **Massa al lancio 600 kg (Kormoran 1) / 630 kg (Kormoran 2) / 660 kg (missilery).** Fonti:
  `https://en.wikipedia.org/wiki/AS.34_Kormoran`, infobox: "Mass 600 kg/630 kg"; sezione "Specifications":
  "Weight: 600/630 kg"; `https://en.missilery.info/missile/kormoran`, tabella: "Start weight , kg 660".
  Per la variante del registro (Kormoran 1) Wikipedia dà **600 kg**, missilery **660 kg**: **discordanza**
  (10%), riporto entrambe → **M**. La conclusione (massa > 515,25 kg) non cambia.
- **RCS: non pubblicata.**
- **Anno:** Wikipedia "Produced Kormoran 1: 1973"; missilery "adopted by the German Navy in 1976". Il registro
  dà 1973. Riporto entrambe (v. §3).
- **Nota "cruise":** nessuna delle due fonti la chiama cruise: Wikipedia "Type Medium-range, active radar homing
  air-to-surface missile" / "anti-ship missile"; missilery la classifica "Anti-ship".

Classe: **`anti_ship`** — missile antinave aviolanciato a guida radar attiva, portata 23–35 km (il registro dà
30 km, come missilery). Ipotesi del piano **confermata**. Confronto: diametro 340–344 mm vs 343 mm dell'Harpoon
(differenza entro l'arrotondamento delle fonti) e massa 600–660 kg > 515,25 kg → **non minore dell'Harpoon** per
massa; sul diametro è **sostanzialmente pari** all'ancora alta. Proposta `ad_detectable` **True**.

### 2.4 Sea Eagle (`Aircraft_Weapon_Data.py:2389`)

Voce del registro: `model` "Sea Eagle", `users` ["UK", "India", "Saudi Arabia"], `task` ["Anti_Ship"],
`start_service` 1985, `end_service` None, `warhead` 230 kg, `range` 100 km, `max_speed` 315 m/s. Variante
identificata: **BAe Sea Eagle P3T aviolanciato** (produzione 1982, in servizio 1985), coerente con `users` e
`start_service`.

- **Diametro 400 mm.** Fonti: `https://en.wikipedia.org/wiki/Sea_Eagle_(missile)`, infobox: "Diameter 0.4 m";
  sezione "Specifications": "Body Diameter : 0.4 metres (1 foot 4 inches)"; `https://en.missilery.info/missile/seaeagle`,
  tabella "Characteristics": "Diameter, m 0.40". Concordi → **A**.
- **Lunghezza 4,14 m (Wikipedia) / 4,10 m (missilery).** Fonti: `https://en.wikipedia.org/wiki/Sea_Eagle_(missile)`,
  infobox "Length 4.14 m"; `https://en.missilery.info/missile/seaeagle`, tabella: "Length, m 4.10". **Discordanza**
  di 4 cm (1%), entro l'arrotondamento: riporto entrambe → **M**.
- **Massa al lancio 580 kg (Wikipedia) / 600–730 kg (missilery).** Fonti: `https://en.wikipedia.org/wiki/Sea_Eagle_(missile)`,
  infobox "Mass 580 kg"; `https://en.missilery.info/missile/seaeagle`, tabella: "Weight, kg 600-730".
  **Discordanza** ampia (580 vs 600–730 kg); riporto entrambe, non scelgo → **M**. La conclusione
  (massa > 515,25 kg) non cambia.
- **RCS: non pubblicata.**
- **Nota "cruise":** Wikipedia la descrive come "medium-weight sea-skimming anti-ship missile" e dice che
  "cruises at speeds of Mach 0.85 (1,040 km/h, 645 mph) throughout its 110 kilometre (68 mile) plus range";
  la voce è nella categoria "Anti-ship cruise missiles". Missilery parla di "cruising subsonic speed (0.85 M)".
  Quindi **sì, qualificata anche cruise**.

Classe: **`anti_ship`** — missile antinave aviolanciato a turbogetto, portata 110 km. Ipotesi del piano
**confermata**. Confronto: 400 mm > 343 mm e 580–730 kg > 515,25 kg → **non minore dell'Harpoon**; proposta
`ad_detectable` **True**.

### 2.5 Kh-31A (`Aircraft_Weapon_Data.py:3981`)

Voce del registro: `model` "Kh-31A", `users` ['USSR', 'Russia', 'India', 'Bulgaria', 'Syria', 'Libya', 'Iraq',
'Algeria', 'Poland'], `task` ['Anti_Ship'], `start_service` 1991, `warhead` 94 kg, `range` 70 km, `max_speed`
680 m/s. Variante identificata: **Kh-31A** (versione antinave, seeker radar attivo; NATO AS-17 Krypton), **non**
la Kh-31P antiradar.

- **Diametro 360 mm.** Fonti: `https://en.wikipedia.org/wiki/Kh-31`, infobox: "Diameter 360 mm (14 in)"
  (citazione Rosoboronexport); `https://en.missilery.info/missile/x31a`, tabella "Characteristics":
  "Dimensions, mm: - length 4700 - maximum housing diameter 360". Concordi → **A**.
- **Lunghezza 4,7 m.** Fonti: stessa pagina Wikipedia, infobox: "Length Mod 1 : 4.7 m (15 ft 5 in)";
  missilery, tabella: "length 4700". La variante Mod. 2 (AD/PD) è 5,3 m / 5340 mm; il registro descrive la
  Kh-31A base → **4,7 m**. **A**.
- **Massa al lancio 610 kg.** Fonti: Wikipedia, infobox: "Mass Kh-31A :610 kg (1,340 lb)" (Rosoboronexport);
  missilery, tabella: "Start weight , kg 610". Concordi → **A**.
- **RCS: non pubblicata.**
- **Nota "cruise":** le fonti **non** la chiamano cruise: Wikipedia "Kh-31A - is a supersonic anti-ship
  missile"; missilery "tactical anti-ship supersonic aircraft missile". Il profilo è supersonico a
  statoreattore, non una crociera subsonica a lungo raggio.
- **Discordanza sulle date:** Wikipedia "In service 1988–present" e "the Kh-31A anti-shipping version in
  1989"; missilery, riquadro "Year 1988"; il registro dà `start_service` 1991. Due fonti dicono 1988, il
  registro 1991: riporto (v. §3).

Classe: **`anti_ship`** — missile antinave supersonico aviolanciato, portata 70 km. Ipotesi del piano
**confermata**. Confronto: 360 mm > 343 mm e 610 kg > 515,25 kg → **non minore dell'Harpoon**; proposta
`ad_detectable` **True**.

### 2.6 Kh-35 (`Aircraft_Weapon_Data.py:4043`)

Voce del registro: `model` "Kh-35", `users` ['USSR', 'Russia', 'Ukraine', 'India', 'Belarus', 'Pakistan',
'Algeria', 'Turkmenistan'], `task` ['Anti_Ship'], `start_service` 1992, `warhead` 150 kg, `range` 130 km,
`max_speed` 280 m/s. Variante identificata: **Kh-35 / 3M-24** (AS-20 Kayak; versione base, non Kh-35U/UE).
Poiché il registro è tra le armi aeree, uso i dati della **versione aerea** (la più leggera), come richiesto.

- **Diametro 420 mm.** Fonte: `https://en.wikipedia.org/wiki/Kh-35`, infobox: "Diameter 42.0 cm (16.5 in)";
  tabella: "Diameter 0.42 m (17 in)". **M**.
- **Lunghezza 3,85 m (versione aerea) / 4,40 m (superficie ed elicottero).** Fonte: stessa pagina, infobox:
  "Length 385 cm (152 in) (air version) 440 cm (173 in) (surface & heli version)"; tabella: "Aircraft-launched
  3.85 m (12.6 ft)". Uso **3,85 m** per la versione aerea → **M**.
- **Massa al lancio 520 kg (aerea) / 610 kg (superficie).** Fonte: stessa pagina, infobox: "Mass 520 kg
  (1,150 lb) (air version) 610 kg (1,340 lb) (surface & heli version)"; tabella: "Aircraft-launched 520 kg
  (1,150 lb)". Uso **520 kg** → **M**.
- **RCS: non pubblicata.**
- **Nota "cruise":** la fonte la qualifica esplicitamente: "subsonic cruise anti-ship missile" (introduzione);
  "Type ... Cruise missile ... Anti-ship missile".
- **Discordanza minore:** Wikipedia dà "In service 2003" e "Produced 1996 for export, 2003 for Russia"; il
  registro dà `start_service` 1992. Riporto entrambe (v. §3).

Classe: **`anti_ship`** — missile antinave subsonico a turbofan, portata 130 km, con varianti aeree, navali,
costiere ed elicotteristiche. Ipotesi del piano **confermata**. Confronto: diametro 420 mm > 343 mm; massa
aerea 520 kg > 515,25 kg (margine 4,75 kg) → **non minore dell'Harpoon**, ma con la massa appena sopra
l'ancora; se si usa il valore CSIS 556 kg per l'Harpoon la massa cade in zona grigia. Il diametro resta
decisamente sopra l'ancora alta. Proposta `ad_detectable` **True**.

### 2.7 Kh-41 (`Aircraft_Weapon_Data.py:4074`)

Voce del registro: `model` "Kh-41", `users` ['USSR', 'Russia', 'India'], `task` ['Anti_Ship'], `start_service`
2000, `warhead` 320 kg, `range` 240 km, `max_speed` 850 m/s. Variante identificata: **Kh-41 (ASM-MSS)**, la
versione **aviolanciata del P-270 Moskit / 3M-80**, per Su-33 (e possibile Su-34); non il 3M-80E navale.

- **Diametro 760 mm / 800 mm.** Fonti: `http://www.testpilot.ru/russia/raduga/kh/41/moskit.htm`, tabella:
  "Диаметр корпуса, м 0,76"; `http://www.airwar.ru/weapon/pkr/moskit.html`, tabella finale (etichette in
  windows-1251 illeggibili, numeri ASCII leggibili): "9385", "760", "3950". **Discordanza**:
  `https://en.wikipedia.org/wiki/P-270_Moskit`, infobox: "Diameter 0.8 m (31 in)". Riporto entrambe (v. §3).
- **Lunghezza 9,385 m / 9,745 m.** Fonti: `http://www.testpilot.ru/.../moskit.htm`: "Длина ракеты 9,385 м" e
  tabella "Длина, м 9,385"; `http://www.airwar.ru/weapon/pkr/moskit.html`, tabella: "9385". **Discordanza**:
  Wikipedia, infobox: "Length 9.745 m (31 ft 11.7 in)" (la sezione "Specifications" della stessa pagina dà però
  "Length: 9.385 m", quindi Wikipedia è internamente discorde). Riporto entrambe.
- **Massa al lancio 3 950 kg / 4 500 kg.** Fonti: `http://www.testpilot.ru/.../moskit.htm`: "Стартовый вес
  ракеты 3950 кг" e tabella "3М-80 3950"; `http://www.airwar.ru/weapon/pkr/moskit.html`, tabella: "3950".
  **Discordanza**: Wikipedia, infobox: "Mass 4,500 kg (9,900 lb)"; la stessa pagina, sezione "Specifications",
  dà "3M-80E missile 4,150 kg (9,150 lb)" e "3M-80E1 missile 3,970 kg (8,750 lb)". Il valore 3 950 kg è quello
  specifico del 3M-80/Kh-41 ed è concorde fra testpilot e airwar.
- **RCS: non pubblicata.**
- **Nota "cruise":** Wikipedia la qualifica esplicitamente: "The P-270 Moskit ... is a Soviet supersonic
  ramjet powered anti-ship cruise missile"; "air launched variant is the Kh-41".
- **Discordanza sulle date:** Wikipedia dice Kh-41 "(1993 air-launched version)" e "accettato tra il 1992 e il
  1994" (testpilot: "принят на вооружение между 1992 и 1994 г."); il registro dà `start_service` 2000.
  Riporto entrambe (v. §3).

Classe: **`anti_ship`** — missile antinave supersonico a statoreattore, aviolanciato da Su-33/Su-34, portata
fino a 250 km nella versione aerea. Ipotesi del piano **confermata**. Confronto: 760–800 mm > 343 mm e
3 950–4 500 kg > 515,25 kg → **non minore dell'Harpoon**; proposta `ad_detectable` **True**.

## 3) Discordanze fra fonti

1. **RB-04E, massa:** 625 kg (`robotmuseum.se`) vs 600 kg (Wikipedia). ~4% di differenza. Uso il valore del
   museo come più specifico della versione E (scheda dedicata), ma riporto entrambe. La proposta di classe non
   cambia.
2. **RB-04E, diametro:** 500 mm in entrambe; solo l'unità di misura cambia (50 cm in Wikipedia).
3. **RB-15/RB-15F, date:** registro `start_service` 1985 (F) e 1989 (RB-15); robotmuseum dà RB 15F operativa
   nel **1989** e la versione navale in produzione dal 1984 (Wikipedia). Le date del registro sembrano
   invertite. Nessuna delle fonti consultate dà 1985 come anno di entrata in servizio della F; Wikipedia dice
   che la RBS 15 Mk I (navale) fu operativa dal 1985 e che l'aviazione ricevette i missili "a couple of years
   later".
4. **Kormoran, portata, diametro, massa e anno:** registro 30 km; Wikipedia 23 km (Kormoran 1) / 35 km
   (Kormoran 2); missilery 30 km (coincide col registro). Diametro 344 mm (Wikipedia) vs 340 mm (missilery);
   massa 600 kg (Wikipedia, Kormoran 1) vs 660 kg (missilery); anno 1973 (Wikipedia/registro) vs 1976
   (missilery). Variante identificata come Kormoran 1 per `start_service` e `warhead` (165 kg; missilery dà
   160 kg).
5. **Sea Eagle, lunghezza, massa e anno:** Wikipedia 4,14 m / 580 kg / in servizio 1985; missilery 4,10 m /
   600–730 kg / adottato 1986. Diametro concorde a 0,40 m. Riporto entrambe; il registro dà 1985.
6. **Kh-31A, `start_service`:** registro 1991; Wikipedia "In service 1988–present" e Kh-31A "in 1989";
   missilery "Year 1988". Due fonti su 1988, il registro 1991: non scelgo; il dato dimensionale non è
   influenzato.
7. **Kh-35, `start_service`:** registro 1992; Wikipedia "In service 2003" e produzione export dal 1996.
8. **Kh-35, massa:** 520 kg (aerea) vs 610 kg (superficie/elicottero) nella stessa fonte; 520 kg è la versione
   aerea richiesta dal compito. Il confronto con l'Harpoon è al limite: 520 kg > 515,25 kg (ancora del
   compito), ma < 556 kg (valore CSIS citato nel compito).
9. **Kh-41, dimensioni:** testpilot + airwar danno 9,385 m / 760 mm / 3 950 kg; Wikipedia dà 9,745 m / 800 mm /
   4 500 kg (e nella sua stessa sezione "Specifications" 9,385 m e 4 150 kg per il 3M-80E). Riporto entrambe
   le famiglie di valori, senza scegliere. Le due fonti russe concordano fra loro e sono specifiche del 3M-80.
10. **Kh-41, date:** registro 2000; Wikipedia 1993 (versione aviolanciata) e testpilot "tra il 1992 e il 1994".

## 4) Cosa non ho trovato / non ho potuto verificare

- **Seconda fonte indipendente**: trovata per Kormoran, Sea Eagle (missilery.info) e Kh-31A (missilery.info),
  che concordano sui valori principali salvo le discordanze elencate in §3. **Non** trovata per la **versione
  aerea del Kh-35** (massa 520 kg, lunghezza 3,85 m): il dato è nella pagina Wikipedia Kh-35 (infobox e
  tabella) ma non ho una seconda fonte che lo confermi separatamente. Le pagine FAS tentate —
  `man.fas.org/dod-101/sys/missile/row/as34.htm`, `man.fas.org/man/dod-101/sys/missile/row/as34.htm`,
  `man.fas.org/dod-101/sys/missile/row/as-17.htm` — danno 404; le pagine CSIS
  `missilethreat.csis.org/missile/kh-31/` e `/kh-31a/` danno 404; `en.missilery.info/missile/x35` e `/x35e`
  danno 404.
- **RCS (sezione radar) di tutte le voci: non trovata / non pubblicata.** Nessuna delle pagine consultate
  riporta una RCS per RB-04E, RB-15/RB-15F, Kormoran, Sea Eagle, Kh-31A, Kh-35, Kh-41. La valutazione di
  "ad_detectable" resta quindi basata su diametro e massa (metro delle due ancore), non su una RCS misurata.
- **Scheda specifica della versione aerea del Kh-35**: vedi sopra, una sola fonte. **M**.
- **Variante esatta del Kormoran:** il registro non dice "1" o "2"; l'identificazione con la Kormoran 1 è mia
  deduzione da `start_service` 1973 e `warhead` 165 kg (dati della Kormoran 1), non un'etichetta del registro.
  Missilery.info dà anno 1976 e testata 160 kg: resta coerente con la Kormoran 1 (non con la 2, 1991/220 kg).
- **Anno di entrata in servizio della RB-15F:** le fonti danno 1989, il registro 1985; non ho trovato una fonte
  che confermi il 1985. Segnalato, non risolto.
- **Dati della versione RB-15 navale "base" (Mk I) senza booster:** il museo dà 568 kg "Exkl. SRM" (la sigla
  SRM = startraketer/booster); è il valore usato. Non ho trovato una scheda separata per la versione costiera
  finlandese MTO 85.
- **Nessuna fonte** consultata qualifica RB-04E, Kormoran o Kh-31A come "cruise": per queste tre la risposta
  alla domanda del lotto è **no** (non sono chiamate cruise), pur restando `anti_ship`. Sea Eagle, Kh-35,
  Kh-41 e la famiglia RB-15/RB-15F sono invece qualificati "cruise" (o "cruising") dalle fonti.

## 5) Metodo

`websearch` non disponibile. Ho usato `webfetch` su:
- `https://en.wikipedia.org/wiki/RB_04` (letta)
- `https://en.wikipedia.org/wiki/RBS_15` (letta; output troncato dal tool, ma le sezioni usate sono state lette)
- `https://en.wikipedia.org/wiki/AS.34_Kormoran` (letta)
- `https://en.wikipedia.org/wiki/Sea_Eagle_(missile)` (letta)
- `https://en.wikipedia.org/wiki/Kh-31` (letta)
- `https://en.wikipedia.org/wiki/Kh-35` (letta)
- `https://en.wikipedia.org/wiki/P-270_Moskit` (letta)
- `https://robotmuseum.se/robotar/rb-04e/` (letta: scheda tecnica)
- `https://robotmuseum.se/robotar/rb-15f/` (letta: scheda tecnica)
- `https://robotmuseum.se/robotar/rb-15m/` (letta: scheda tecnica)
- `http://www.airwar.ru/weapon/pkr/moskit.html` (letta: numeri ASCII leggibili, etichette in windows-1251
  illeggibili; usati solo i numeri della tabella)
- `http://www.testpilot.ru/russia/raduga/kh/41/moskit.htm` (letta)
- `https://en.missilery.info/missile/kormoran` (letta)
- `https://en.missilery.info/missile/seaeagle` (letta)
- `https://en.missilery.info/missile/x31a` (letta)
- `https://html.duckduckgo.com/html/?q=FAS+AS.34+Kormoran+man.fas.org` (pagina di risultati: presi solo URL)
- tentate e fallite (404): `https://man.fas.org/dod-101/sys/missile/row/as34.htm`,
  `https://man.fas.org/man/dod-101/sys/missile/row/as34.htm`,
  `https://man.fas.org/dod-101/sys/missile/row/as-17.htm`, `https://missilethreat.csis.org/missile/kh-31/`,
  `https://missilethreat.csis.org/missile/kh-31a/`, `https://en.missilery.info/missile/x35`,
  `https://en.missilery.info/missile/x35e`
- tentata e bloccata (captcha DuckDuckGo): `https://html.duckduckgo.com/html/?q=CSIS+missilethreat+Kh-31`

Passi usati: **circa 41 chiamate a tool** in totale (33 prima delle correzioni: 10 `grep`/`sed` sul repo,
1 `ls`, 1 `read` di confronto, 20 `webfetch`, 1 `write`; più le modifiche di aggiornamento della bozza).
Pagine web **lette con successo**: **15** (7 Wikipedia, 3 robotmuseum, 1 airwar, 1 testpilot, 3 missilery.info),
più 1 pagina di risultati DuckDuckGo. URL tentati senza successo: **8** (5 FAS/CSIS 404, 2 missilery 404,
1 captcha).

Nessun valore è inventato: dove la fonte non c'era ho scritto "non trovato/non pubblicata". Le uniche
deduzioni sono dichiarate (variante Kormoran 1; confronto col valore CSIS 556 kg per l'Harpoon).