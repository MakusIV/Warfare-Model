# Ricerca dati — Blocco 0 BI, LOTTO L1 (ancore + famiglia Maverick)

Bozza di `oc-researcher`, 2026-11-07. Fonti web lette in questa sessione; nessun valore inventato. Le ancore
(AGM-65D, AGM-84A) sono quelle fornite dal principale e non sono state ricercate: qui vengono solo riportate con le
loro fonti. Ricerca fatta con `webfetch` (motore di ricerca: pagina risultati DuckDuckGo HTML), `websearch` non
disponibile.

Riferimenti nel repo (letti con `grep -n` / `sed -n`):
- §2.2 tabella armi→classe e §5.1 blocco 0: `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`.
- `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py`: `AGM-65D` (riga 2499), `RB-75T` (riga 2409),
  `AGM-65K` (riga 2569).
- `Code/Dynamic_War_Manager/Source/Asset/Ship_Weapon_Data.py`: `RGM-84-Harpoon` (riga 1240, `'caliber': 343`,
  `'warhead': 221`, `'range': 280`, `start_service` 1977).

## 1) Tabella riassuntiva

| Voce (registro) | Variante cercata | Classe proposta (ipotesi del piano) | Diametro | Lunghezza | Massa al lancio | RCS | Confronto con le ancore | Confidenza |
|---|---|---|---|---|---|---|---|---|
| **AGM-65D** (ancora, non ricercata) | AGM-65D IIR | `tactical` (confermata, decisione BI-6) | 304,8 mm (FAS) | 2,49 m (Wikipedia) | 218,25 kg (FAS) / 220 kg (d-s) | non pubblicata | **ancora bassa** (diametro di riferimento) | A |
| **AGM-84A** (ancora, non ricercata) | AGM-84A aviolanciato | `anti_ship` (confermata) | 343 mm | 3,79 m (FAS) / 3,85 m (d-s, AGM-84D) | 515,25 kg (FAS) | non pubblicata | **ancora alta** (diametro di riferimento) | A |
| **AGM-65K** (`Aircraft_Weapon_Data.py:2569`) | AGM-65K = AGM-65G ricostruito con seeker CCD, USAF | `tactical` — **confermata** | 304,8 mm (FAS) / 305 mm (d-s) | 2,49 m (d-s, Wikipedia) | 304 kg (d-s, colonna F/G) / 306 kg (Wikipedia, colonna K) / 301,5 kg (FAS, G) | non pubblicata | **zona grigia per massa**: diametro = Maverick, massa 301,5–306 kg > 218,25–220 kg del Maverick (stessa cellula, testata pesante 136 kg). La decisione BI-6 lo fissa comunque False | A (diametro, lunghezza) / A (massa, tre secondarie concordi entro ~1,5%) |
| **RB-75T** (`Aircraft_Weapon_Data.py:2409`) | Rb 75T svedese, variante dell'Rb 75 (AGM-65A/B) con "tung stridsdel" (testata pesante) | `tactical` — **confermata** (ma il registro sovrastima la portata e sottostima la testata) | **non trovato** per la T; ereditato 304,8 mm [S] (stessa cellula AGM-65) | 2,5 m | **295 kg** (Robotmuseum) — il registro dichiara 57 kg di testata, incompatibile con la "heavy warhead" | non pubblicata | **zona grigia per massa**: diametro = Maverick, massa 295 kg > 210–220 kg del Maverick. BI-6 lo fissa comunque False | M (massa) / M (lunghezza) / B [S] (diametro ereditato) |
| **RGM-84-Harpoon** (`Ship_Weapon_Data.py:1240`) | RGM-84 lanciato da nave **con booster** (famiglia RGM-84A, 1977) | `anti_ship` — **confermata** | 343 mm (13,5 in) | 4,55 m (FAS) / 4,6 m (Wikipedia) / 4,63 m (d-s, RGM/UGM-84D) | 661,5 kg (FAS, sea-launch) / 690 kg (d-s, RGM/UGM-84D) / 691 kg (Wikipedia) | non pubblicata | **non minore dell'Harpoon** (diametro uguale all'ancora; massa 661,5–691 kg > 515,25 kg dell'aviolanciata) → True | A (diametro) / M (lunghezza, massa: fonti discordi, v. §3) |

## 2) Dettaglio per voce

### 2.1 AGM-65D (ancora bassa — solo riporto, non ricercata)

- Diametro 304,8 mm. Fonte: `https://man.fas.org/dod-101/sys/smart/agm-65.htm`, estratto: "Diameter: 1 foot (30.48
  centimeters)" — confidenza A.
- Lunghezza 2,49 m. Fonte: `https://en.wikipedia.org/wiki/AGM-65_Maverick`, estratto (tabella varianti, riga Length):
  "2.49 m (8 ft 2 in)" — confidenza A.
- Massa 218,25 kg / 220 kg. Fonti: FAS (tabella, colonna AGM-65D) "485 lbs (218.25 kg)"; `https://www.designation-systems.net/dusrm/m-65.html`
  (tabella, colonna AGM-65D) "220 kg (485 lb)" — confidenza A (due concordi).
- RCS: non pubblicata (nessuna fonte consultata riporta una RCS per il Maverick).

### 2.2 AGM-84A Harpoon aviolanciato (ancora alta — solo riporto, non ricercata)

- Diametro 343 mm (13,5 in ≈ 34,3 cm). Fonti: FAS "Diameter: 13.5 inches (34.29 centimeters)"; d-s "Diameter34.3 cm
  (13.5 in)"; Wikipedia "13.5 in (34 cm)" — confidenza A.
- Lunghezza 3,79 m. Fonte: FAS (tabella, colonna air-launch) "12 feet, 7 inches (3.79 meters)" — A. d-s riporta per
  l'AGM-84D 3,85 m (colonna AGM-84D: "3.85 m (12 ft 7.5 in)"): le due misure si riferiscono a sottoversioni diverse
  (A vs D), non sono in contraddizione ma non sono identiche.
- Massa 515,25 kg. Fonte: FAS (tabella, colonna air-launch) "1,145 pounds (515.25 kilograms)" — A (l'ancora cita CSIS
  concorde; CSIS non e' stato riletto in questa sessione).
- RCS: non pubblicata.

### 2.3 AGM-65K (`Aircraft_Weapon_Data.py:2569`)

Voce del registro: `model` "AGM-65K", `users` USA/South Korea/Taiwan, `task` Anti_Ship/Strike/SEAD,
`start_service` 1970, `warhead` 136 kg (WDU-24/B), `range` 15 km, `max_speed` 320 m/s.

Variante identificata: **AGM-65K**, cioè un **AGM-65G ricostruito con seeker TV CCD** (non un AGM-65G "normale").
Fonte: `https://www.designation-systems.net/dusrm/m-65.html`, estratto: "The AGM-65K is an AGM-65G upgraded with the
CCD seeker." — confidenza A. Conferma: Wikipedia AGM-65 ("Maverick K model is an AGM-65G upgraded with the CCD
seeker"; "replacing the AGM-65G's IR guidance system with an electro-optical television guidance system") e FAS
(sezione "AGM-65K": "The new missile will be known as the AGM-65K").

Valori:
- **Diametro 304,8 mm / 305 mm.** FAS: "Diameter: 1 foot (30.48 centimeters)"; d-s (tabella, comune a tutte le
  varianti): "Diameter30.5 cm (12 in)"; Wikipedia (tabella): "Diameter30 cm (12 in)". Confidenza A (tre concordi).
- **Lunghezza 2,49 m.** d-s (tabella): "Length2.49 m (98 in)"; Wikipedia (tabella): "2.49 m (8 ft 2 in)".
  Confidenza A.
- **Massa al lancio 301,5–306 kg.** Il K è un G ricostruito, quindi la massa è quella del G:
  - d-s (tabella, colonna AGM-65F/G): "Weight209 kg (462 lb)220 kg (485 lb)285 kg (630 lb)304 kg (670 lb)" →
    colonna F/G = **304 kg**;
  - Wikipedia (tabella varianti, colonna AGM-65K): **306 kg (675 lb)** ("Weight210 kg(462 lb)220 kg(485 lb)293 kg(645 lb)306 kg(675 lb)…");
  - FAS (tabella "Launch Weight", colonna AGM-65G): "670 lbs (301.50 kg)".
  Confidenza A per la fascia 301,5–306 kg (tre fonti secondarie concordi entro ~1,5%); il valore esatto dipende
  dalla variante.
- **RCS: non pubblicata.**

Classe: **`tactical`** — missile aria-superficie tattico a corto raggio (close air support / interdizione), stessa
cellula del Maverick. Ipotesi del piano **confermata**. Nota: il registro dichiara `start_service` 1970 e
`range` 15 km; le fonti danno il K come conversione tarda ("The most modern versions of the Maverick are the
AGM-65H/K, which were in production as of 2007", Wikipedia) e una portata "Greater than 22 km (12 nmi)" (Wikipedia)
o "> 27 km (17 miles)" (d-s). Il `start_service` 1970 del registro non corrisponde alla variante K (sembra quello
del modello A); lo segnalo, non lo modifico.

### 2.4 RB-75T (`Aircraft_Weapon_Data.py:2409`)

Voce del registro: `model` "RB-75T", `users` Sweden, `task` Anti_Ship/Strike/SEAD, `start_service` 1972,
`warhead` **57 kg** (commento "WDU-20/B shaped-charge"), `range` 15 km, `max_speed` 320 m/s.

Variante identificata: **Rb 75T**, designazione svedese della variante dell'**Rb 75** (AGM-65 Maverick) con
**testata pesante** ("T" = *tung stridsdel*), impiegata in ruolo antinave. Fonti:
- `https://en.wikipedia.org/wiki/Swedish_Air_Force_weapons`, estratto: "RB 75T: Swedish domestically modified
  variant of the RB 75 with heavier warhead. Used in AShM role." e "The T denotes tung stridsdel, 'heavy
  warhead'." — confidenza A per l'identificazione (due frasi della stessa pagina, coerenti).
- `https://www.robotmuseum.se/robotar/rb-75-2/` (Arboga Robotmuseum, fonte svedese specialistica): "Robot 75 är en
  TV-styrd attackrobot som finns i två versioner för flygvapnet, Robot 75 och Robot 75T, där skillnaden ligger i
  stridsdelens utformning (T=tung stridsdel)." — confidenza A.

Valori:
- **Massa al lancio 295 kg.** Robotmuseum (tabella "Data"): "Vikt RB75 210 kg, RB75T 295 kg". Confidenza M (una
  fonte specialistica; Wikipedia conferma solo qualitativamente "heavier warhead"). Confronto: lo stesso museo dà
  Rb 75 "normale" a 210 kg, coerente con i 207,9–209 kg dell'AGM-65A/B delle fonti USA → la differenza di 85 kg è
  la testata pesante.
- **Lunghezza 2,5 m.** Robotmuseum (tabella): "Längd 2,5 m". Confidenza M. `https://www.aef.se/Flygvapnet/Notiser/Robot_75_Notis.htm`
  (AEF, tabella): "RB75 2,5 m 215 kg" (riferito all'Rb 75, non alla T; pagina in Latin-1, leggibile nei numeri).
- **Diametro: non trovato** per l'Rb 75T. Le fonti svedesi non lo riportano. Essendo una modifica della cellula
  AGM-65 (stessa fusoliera, testata più pesante come nelle AGM-65E/F/G, che conservano il diametro di 30,5 cm),
  propongo per eredità **304,8 mm** — **stima [S]**, non un dato: il ragionamento è che l'Rb 75T è descritto come
  "domestically modified variant of the RB 75" e nessuna fonte indica un cambio di diametro; confidenza B.
- **RCS: non pubblicata.**

Classe: **`tactical`** (missile aria-superficie tattico a corto raggio, con impiego anche antinave). Ipotesi del
piano **confermata**. **Osservazione importante sul registro**: `warhead` 57 kg (WDU-20/B) corrisponde all'Rb 75
"normale" (AGM-65A/B: 57 kg), **non** all'Rb 75T, che per definizione ha testata pesante (~136 kg nella famiglia
AGM-65E/F/G) e massa 295 kg. Il commento "WDU-20/B shaped-charge" sulla voce RB-75T è quindi incoerente con la
variante. La portata del registro (15 km) è inoltre maggiore del dato svedese: "Räckvidd <10 km (skjuthöjd <500 m)"
(Robotmuseum). Non modifico nulla: segnalo per il blocco 1.

### 2.5 RGM-84-Harpoon (`Ship_Weapon_Data.py:1240`)

Voce del registro: `model` "RGM-84-Harpoon", `start_service` 1977, `caliber` 343, `warhead` 221 kg,
`range` 280 km, `speed` 289 m/s (Mach 0.85), `task` Anti_Ship.

Variante identificata: **RGM-84 lanciato da nave, con booster** (famiglia RGM-84A, entrata in servizio nel 1977;
il registro non distingue la sottoversione). Fonte per la distinzione: Wikipedia Harpoon, "Surface ships (RGM-84),
fitted with a solid-fuel rocket booster that detaches when expended". Fonte: `https://en.wikipedia.org/wiki/Harpoon_(missile)`.

Valori (versione da nave, con booster):
- **Diametro 343 mm.** Wikipedia: "13.5 in (34 cm)"; FAS: "Diameter: 13.5 inches (34.29 centimeters)"; d-s:
  "Diameter34.3 cm (13.5 in)". Confidenza A. Coincide con il `caliber` 343 del registro navale.
- **Lunghezza 4,55 m / 4,6 m / 4,63 m.**
  - FAS (tabella, colonna sea-launch): "15 feet (4.55 meters)";
  - Wikipedia: "15 ft (4.6 m), surface- and submarine-launched";
  - d-s (tabella, colonna RGM/UGM-84D): "4.63 m (15 ft 2.2 in)".
  Le fonti **discordano** di ~8 cm; riporto tutte e tre (v. §3). Confidenza M.
- **Massa al lancio 661,5 kg / 690 kg / 691 kg.**
  - FAS (tabella, colonna sea-launch): "1,470 pounds (661.5 kilograms)";
  - d-s (tabella, colonna RGM/UGM-84D, "incl. booster"): "690 kg (1520 lb)";
  - Wikipedia: "1,523 lb (691 kg) including booster".
  Le fonti **discordano** di ~30 kg (probabile differenza RGM-84A vs RGM-84D, oppure peso del booster); riporto
  tutte e tre senza scegliere (v. §3). Confidenza M.
- **Differenza dalla aviolanciata**: l'AGM-84A non ha booster e pesa 515,25 kg, è lungo 3,79 m (FAS); la versione
  da nave è più lunga (4,55–4,63 m) e più pesante (661,5–691 kg) proprio per il booster, che si separa dopo
  l'esaurimento ("The Booster Section separates from the missile before sustained flight begins", FAS).
- **RCS: non pubblicata.**

Classe: **`anti_ship`** — missile antinave a volo radente con turbogetto e ricerca radar attiva; missione primaria
antinave, non bombardamento terrestre (la variante terrestre è lo SLAM, AGM-84E, altra designazione). Ipotesi del
piano **confermata**. Nel confronto con le ancore: diametro uguale all'ancora alta, massa 661,5–691 kg
**maggiore** di quella dell'aviolanciata (515,25 kg) → **non minore dell'Harpoon** → `ad_detectable` True coerente
con BI-7 (a).

## 3) Discordanze fra fonti

1. **RGM-84 da nave, massa**: FAS 1.470 lb = **661,5 kg** (colonna "sea-launch", presumibilmente RGM-84A);
   designation-systems **690 kg** (colonna RGM/UGM-84D, "incl. booster"); Wikipedia **691 kg** ("including
   booster"). Differenza ~4,5%. Non scelgo: probabile differenza di sottoversione/booster. Il principale aveva
   indicato 691 kg come "RGM/UGM con booster": confermato da Wikipedia e d-s, ma FAS dà un valore più basso.
2. **RGM-84 da nave, lunghezza**: FAS 4,55 m; Wikipedia 4,6 m; d-s 4,63 m (RGM/UGM-84D). Concordi entro 8 cm.
3. **AGM-65K, massa**: 304 kg (d-s, colonna F/G da cui il K deriva) vs 306 kg (Wikipedia, colonna K) vs 301,5 kg
   (FAS, colonna G). Concordi entro ~1,5%.
4. **AGM-65K, portata**: Wikipedia "> 22 km"; d-s "> 27 km"; registro 15 km. (Non è un dato richiesto per la
   classe, ma spiega che il `range` 15 del registro non viene dalle fonti.)
5. **RB-75T, testata/massa**: registro 57 kg (testata WDU-20/B, tipica di AGM-65A/B) vs fonti svedesi: Rb 75T
   **295 kg di massa** e "heavy warhead". Il registro descrive di fatto l'Rb 75 "normale", non la T.
6. **RB-75T, portata**: registro 15 km vs Robotmuseum "<10 km (skjuthöjd <500 m)".
7. **AGM-65K, `start_service`**: registro 1970; le fonti collocano la conversione K molto più tardi (in produzione
   nel 2007 secondo Wikipedia; l'AGM-65G da cui deriva è del 1989). 1970 sembra il valore del modello A.

## 4) Cosa non ho trovato / non ho potuto verificare

- **RCS**: nessuna delle tre voci (e nessuna delle due ancore) ha una RCS pubblicata nelle fonti lette. Scritto
  "non pubblicata" per tutte.
- **RB-75T, diametro**: non pubblicato dalle fonti svedesi; ho proposto 304,8 mm per eredità dalla cellula AGM-65
  come **stima [S]** (confidenza B), non come dato.
- **RB-75T, identificazione della testata esatta**: le fonti dicono "heavier warhead" / "tung stridsdel" ma non
  danno il peso della testata né il modello (es. WDU-24/B). Non ho trovato una fonte che quantifichi la testata
  dell'Rb 75T. (La massa totale di 295 kg è invece documentata.)
- **RGM-84A specifico (1977)**: non ho trovato una scheda che dia massa e lunghezza della **RGM-84A** con booster
  separatamente dalla RGM-84D; FAS sembra riferirsi alla versione base, d-s/Wikipedia alla D o alla famiglia. Non
  ho potuto stabilire con certezza quale valore corrisponda alla RGM-84A.
- **CSIS Missile Threat**: non riletta in questa sessione (l'ancora Harpoon cita CSIS; i valori CSIS non sono
  stati verificati da me). Non ho aperto `missilethreat.csis.org`.
- **Siti dei costruttori** (Raytheon/Boeing): non tentati (rischio 403 e nessun dato aggiuntivo rispetto a
  FAS/d-s/Wikipedia già concordi).
- Non ho verificato la pagina `sv.wikipedia.org` dell'AGM-65 (vista solo come risultato di ricerca, non letta).

## 5) Metodo

- `websearch` non disponibile: usato `webfetch`. Scoperta degli URL con la pagina di risultati
  `https://html.duckduckgo.com/html/?q=RB+75T+Maverick+Sweden+AGM-65` (dai risultati ho preso solo gli URL:
  en.wikipedia, sv.wikipedia, designation-systems, robotmuseum, aef.se).
- Pagine lette (10):
  1. `https://en.wikipedia.org/wiki/AGM-65_Maverick` (tabella varianti: lunghezza, diametro, pesi per colonna K;
     sezione varianti: K = G con seeker CCD; portata);
  2. `https://en.wikipedia.org/wiki/Harpoon_(missile)` (infobox: massa 691 kg con booster, lunghezze 3,8/4,6 m,
     diametro; testo su booster delle versioni da nave);
  3. `https://man.fas.org/dod-101/sys/smart/agm-65.htm` (tabella specifiche: diametro 30,48 cm, pesi A/B/D/G/E/F;
     sezione AGM-65K);
  4. `https://man.fas.org/dod-101/sys/smart/agm-84.htm` (tabella: lunghezze e pesi sea-launch/air-launch; booster;
     separazione del booster);
  5. `https://html.duckduckgo.com/html/?q=RB+75T+Maverick+Sweden+AGM-65` (solo URL);
  6. `https://en.wikipedia.org/wiki/Swedish_Air_Force_weapons` (RB 75 e RB 75T, "heavy warhead");
  7. `https://www.robotmuseum.se/robotar/rb-75-2/` (Arboga Robotmuseum: RB75 210 kg / RB75T 295 kg, lunghezza
     2,5 m, portata <10 km);
  8. `https://www.aef.se/Flygvapnet/Notiser/Robot_75_Notis.htm` (AEF: RB75 2,5 m / 215 kg; pagina in Latin-1,
     numeri leggibili, testo accentato illeggibile — non ricostruito);
  9. `https://www.designation-systems.net/dusrm/m-65.html` (tabella A/B/D/E/F/G; K = G con CCD);
  10. `https://www.designation-systems.net/dusrm/m-84.html` (tabella AGM-84D/RGM-UGM-84D: 3,85/4,63 m, 540/690 kg).
- Passi usati: 19 (di cui 1 scrittura del file). Limite 80 rispettato.

## 6) Sintesi per l'utente

- **AGM-65K**: `tactical` confermata. 304,8 mm × 2,49 m, 301,5–306 kg. È la stessa cellula del Maverick ma con la
  testata pesante da 136 kg: **per massa sta sopra l'ancora Maverick** (218–220 kg) pur avendo lo stesso diametro.
  Con la regola stretta di BI-6 ("diametro **e** massa non maggiori") non sarebbe "non maggiore del Maverick", ma
  è coperto dalla decisione esplicita dell'utente (Maverick = False in ogni contesto). Segnalo il caso perché il
  test di coerenza del §5.2 (regola 5) riguarda solo le voci True, quindi non si rompe.
- **RB-75T**: `tactical` confermata. 295 kg, 2,5 m, diametro ereditato 304,8 mm [S]. Il **registro è incoerente**:
  dichiara 57 kg di testata (Rb 75 normale) mentre la T ha testata pesante e massa 295 kg; anche il `range` 15 km
  non corrisponde al dato svedese (<10 km a bassa quota). Da correggere nel blocco 1 con la fonte Robotmuseum/
  Wikipedia svedese.
- **RGM-84-Harpoon**: `anti_ship` confermata. Versione da nave con booster: 343 mm, 4,55–4,63 m, 661,5–691 kg
  (fonti discordi sulla massa, ~4,5%); è **non minore dell'ancora Harpoon** (diametro uguale, massa maggiore
  dell'aviolanciata da 515,25 kg) → True.