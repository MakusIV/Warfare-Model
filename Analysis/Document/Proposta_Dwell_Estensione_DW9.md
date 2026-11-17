# Proposta: estensione dei `dwell_time_s` a SAM, AAA, TVD, vista, navi e AWACS (DW-9 rivista)

**Stato: BOZZA, decisioni DW9-1..DW9-9 aperte (§4).** Scritta il 2026-11-17 da `des-planner` su osboxes.
**Aggiornata il 2026-11-17 con la linea decisa dall'utente** dopo la lettura di `Dinamica dei Tempi di
Aggiornamento Radar - Google Gemini.md`: **valore FISSO per sensore** (niente dwell dipendente da distanza, modo o
carico del radar; §3.4), **regola sugli intervalli** "regime normale se citato, altrimenti valore centrale" con la
**banda di incertezza** di fonte accanto al valore (§3.5), sonda S-4 con due passate di sensibilita' agli estremi
(blocco 0). DW9-1, DW9-3 e DW9-6 sono diventate "quale valore fisso dentro l'intervallo".
**Contratto precedente, non modificato**: `Proposta_Dwell_Time_Rilevamento.md` (blocchi A e B eseguiti: legge L1,
interruttore `D5_DWELL_TIME`, lettori, S32-DWELL; DW-9 di allora = "solo il meccanismo, valori ai soli 10 EWR").
**Origine**: decisione dell'utente "DW-9 rivista" (vincolante, il "se" non si riapre; §1.1). Questo documento
discute solo il "come": quali valori, dove, con quali etichette, con quali test, e che cosa succede alla fotografia.

**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`) o eseguendolo; **[I]** = ipotesi o conoscenza
generale non verificata nel repository; **[S]** = stima o scelta di progetto, mai dato tarato; **F/D/S** = Fonte /
Dedotto (calcolo mostrato) / Stima. Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`. Decisioni
numerate **DW9-1, DW9-2, ...** ("DW9" = decisioni della DW-9 rivista; "DW-n" senza 9 sono quelle del contratto
precedente). Sonde numerate **S-4, S-5** (S-1..S-3 sono della Proposta precedente). Righe di codice lette al commit
`412faa7b` (2026-11-14).

**Nessun file di codice o di test modificato da questo documento.** Le sonde eseguite per scriverlo (§1.6) sono
script di sola lettura nella cartella temporanea della sessione: scrivono i valori **in memoria** e rieseguono parte
del confronto con la fotografia, senza installare nulla.

---

## 0. Sintesi

**Che cosa cambia.** Solo **dati**: la chiave opzionale `dwell_time_s` (periodo di rivisita della funzione di
**ricerca**) entra nel dizionario del sensore di 43 record (9 SAM/AAA con radar, 4 SAM con TVD, 2 AAA a vista, 3 EWR,
22 navi, 3 AWACS). Nessuna riga del motore cambia: la legge L1 `Pd = min(1, permanenza/dwell) x Pd(d)`, i lettori e
l'interruttore esistono gia' dal blocco A [V]. L'interruttore resta **`Engagement_Resolver.D5_DWELL_TIME = False`**
(`Logic/Engagement_Resolver.py:592`): non serve un interruttore nuovo (§3.2).

**Valore fisso e banda di incertezza (linea dell'utente, §3.4-§3.5).** Un solo valore per sensore, indipendente da
distanza, modo e carico del radar. Dove la fonte da' un intervallo: regime normale se citato, altrimenti **valore
centrale** (media geometrica degli estremi del periodo); l'intervallo di fonte e' riportato come **banda di
incertezza** nel commento del codice e nel registro dei dwell stimati. La sonda S-4 prova i valori raccomandati e i
due estremi di tutte le bande.

**Il punto di design (ricerca contro inseguimento).** Il codice legge il dwell **solo** insieme alla portata di
**acquisizione**: `registry_dwell_time` (`Logic/Engagement_Resolver.py:1303`) chiama
`Mobile.detection_dwell_time(mode)` con `range_type='acquisition_range'` di default (`Asset/Mobile.py:1692`), che
prende il sensore con la portata di acquisizione massima e ne legge `dwell_time_s` (`:1714-1735`). Il dwell non entra
in nessun calcolo di inseguimento (`tracking_range`), d'ingaggio o di tracciamento dei colpi (R-INT) [V]. Quindi il
registro **puo' ospitare il dwell di ricerca senza ambiguita' nel codice** anche nei record che fondono ricerca e
inseguimento (Buk: `model` = "9S35 Fire Dome" ma `acquisition_range` 85 km = 9S18; S-300PS: "30N6 Flap Lid", ricerca
= Big Bird): l'ambiguita' e' solo di **nome** e si risolve con il commento del record che nomina il radar di ricerca
(§1.3, DW9-2).

**Effetto sulla fotografia.**

| Stato | Esito atteso | Base |
|---|---|---|
| Interruttore SPENTO (default), dopo i blocchi 1-5 | **1103 identiche, 0 cambiate, 0 nuove** | `Session_Simulator` non passa il lettore (`Logic/Session_Simulator.py:2792-2794`); le sole unita' che accendono la D-5 dentro il test (S32 `long`/`short`/`ewr_on`, S33) restano identiche: sonda breve S-4a (§1.6) |
| Interruttore ACCESO (sonda S-4, sola lettura, tre passate: valori raccomandati, estremi minimi, estremi massimi) | parziale, **con la prima versione dei valori** (regola "rotazione piu' veloce", §1.6): **545 esecuzioni su 1103 provate, tutte IDENTICHE**; delle 558 restanti, 507 non contengono sensori con valore nuovo (identiche per costruzione), 51 (S17, S20, VAL, ORC) da provare. I valori attuali (centrali) e gli estremi vanno provati con la S-4 completa (blocco 0) | §1.6 |

**SAM e AAA sono tiratori**: con `D5_DWELL_TIME` acceso una Pd ridotta del loro sensore **cambia gli esiti di tiro**,
non solo la percezione (Proposta precedente §1.5). La sonda S-2 (10 s uniformi a ogni osservatore, 1009 esecuzioni)
aveva cambiato 2 esecuzioni (S21-5 e S21-7 `control`, osservatore Strela-10); con la prima versione dei valori
(Strela-10 3,94 s, Shilka 18 s) S21 resta identica (§1.6). L'effetto e' raro perche' con periodi di 1-20 s la Pd si riduce solo
per contatti **radenti** (corde di poche centinaia di metri, §1.7): il rischio principale gia' noto resta (la legge non
accorcia le rotte senza orizzonte radar nel DES). **Il confronto con l'interruttore acceso va riletto dall'utente
prima di qualunque accensione; la fotografia la installa solo l'utente.**

**Dimensione stimata**: ~43 righe di dato + ~50 righe di commento nei tre registri; 1 file di test nuovo
(`Test/Test_Dwell_Data.py`, ~170 righe) e 4 file di test ritoccati; **10 test nuovi** (suite attesa `Ran 4924`,
base `Ran 4914` da rileggere); 1 documento nuovo (`Registro_Dwell_Stimati.md`). Cinque blocchi piccoli (uno per
famiglia di asset) piu' il blocco 0 (sonda S-4 in tre passate, sessione principale, ~55 minuti su osboxes).

---

## 1. Problema e comportamento attuale

### 1.1 La decisione dell'utente da realizzare (DW-9 rivista, vincolante)

1. Dwell per **tutti** gli asset del DES **tranne gli aerei non AWACS**: SAM, AAA, navi, TVD, vista, AWACS (e gli EWR
   rimasti senza valore).
2. Dove manca il dato: **stima per confronto** con un analogo della stessa classe/epoca, indicato per nome; ogni stima
   marcata **[S]** nel commento del codice e raccolta in un **registro dei dwell stimati da aggiornare**.
3. Il dwell vale **solo per la funzione di RICERCA**; niente dwell per inseguimento/tracciamento (conical scan,
   monopulse: legge attuale). Esempio: Buk = dwell del 9S18 di ricerca, non del Fire Dome.
4. Vista e TVD: dwell stimato anch'esso con L1, annotato come **APPROSSIMAZIONE** da rivedere quando ci sara' una legge
   cumulativa (Koopman/esponenziale).
5. Effetto da dichiarare: SAM/AAA sono tiratori; con `D5_DWELL_TIME` acceso il confronto va riletto; con
   l'interruttore spento tutto deve restare identico; la fotografia la installa solo l'utente.

### 1.2 Che cosa fa il codice oggi [V]

- **Dato**: chiave opzionale `dwell_time_s` [s] nel dizionario del sensore (`record.radar`, `record.TVD`,
  `record.visual`), oggi presente solo nel `radar` di 10 EWR (`Asset/Vehicle_Data.py:4659-4661` intestazione,
  `:4688`, `:4737`, `:4764`, `:4788`, `:4814`, `:4841`, `:4866`, `:4952`, `:4980`, `:5058`; commento di Chain-Home
  `:4925`). Nessun valore in `Ship_Data.py` ne' in `Aircraft_Data.py` [V: inventario dei registri caricati, §1.4].
- **Lettore del dato**: `Mobile._sensor_dwell_s(record, sensor)` (`Asset/Mobile.py:1571-1590`): None se il sensore
  manca, la chiave manca o il valore non e' un numero finito > 0 (bool escluso); mai un'eccezione.
  `Mobile.sensor_dwell_time(sensor)` (`:1676-1690`) e `Mobile.detection_dwell_time(mode, range_type)` (`:1692-1735`):
  il secondo sceglie il sensore con la portata `range_type` **massima** (a parita' il primo di
  `DETECTION_SENSORS = ('radar', 'TVD', 'visual')`, `:84`), escludendo il visivo con `D4C_VISUAL_SENSOR` spento
  (`:1717-1718`), e ne restituisce il dwell.
- **Motore**: `registry_dwell_time(observer, target, mode)` (`Logic/Engagement_Resolver.py:1303-1318`) e' il lettore
  di default; `Session_Simulator.engage` lo passa al risolutore **solo** con `ER.D5_DWELL_TIME` acceso
  (`Logic/Session_Simulator.py:2792-2794`). Nel risolutore `_dwell_of` (`Engagement_Resolver.py:2494-2503`) legge il
  dwell per la direzione osservatore -> bersaglio (modo del bersaglio, `GROUNDED_DETECTION_MODE` se a terra); il dwell
  serve a due cose: (1) il fattore `dwell_factor(permanenza, dwell)` (`:1278-1300`, composto in `_detect_direction`
  `:2351-2353` e in `_detect_passes`); (2) l'**unione dei passaggi** separati da un'uscita <= dwell (FP-10,
  `_own_passes` `:2505-2522`, `_join_passes`). Il calcolo sta prima di `self._draw()` (`:2355`) e non estrae nulla.
- **Inseguimento e colpi**: nessun uso del dwell fuori da rilevamento e passaggi; R-INT (`_round_track_time`) non lo
  legge [V: `grep dwell` nel risolutore]. Le finestre di contatto in sessione usano sempre `acquisition_range`
  (`DEFAULT_DETECTION_RANGE_TYPE`, `Asset/Mobile.py:98`; nessun chiamante passa `tracking_range` o
  `engagement_range` a `schedule_contacts` [V: ricerca testuale]).
- **Pianificatore**: `build_detection_threat` (`Logic/Air_Route_Manager.py:740-805`) legge **sempre**
  `asset.sensor_dwell_time(sensor)` (`:799`) e lo mette in `DetectionThreat.dwell_time_s`; `compute_detection_metrics`
  lo usa solo con `ER.D5_DWELL_TIME` acceso (`:1132`). Il pianificatore non entra nella fotografia.
- **Scenari che accendono la D-5 nella fotografia**: S32-DWELL (`Test/Test_Session_Scenarios_S32.py:96`: varianti
  `long`, `short`, `ewr_on` accese) e S33-PASSES (`Test/Test_Session_Scenarios_S33.py:107`: entrambe le varianti
  accese). S32 `long`/`short` e S33 dichiarano il dwell della ZSU-57-2 con `F.declare_dwell` (modo 'air'), che
  scavalca il registro solo su quell'istanza (`Test/Scenario_Fixtures.py:306-335`); **S32 `ewr_on` no**: li' la ZSU-57-2
  legge il dwell del registro. E' l'unico punto in cui un dato nuovo puo' toccare la fotografia con l'interruttore
  spento di default (§5.7).

### 1.3 Ricerca contro inseguimento nel registro: che cosa dice il codice reale [V]

Il registro ha **un solo dizionario per sensore** (`radar`, `TVD`, `visual`) con, per modo, `acquisition_range`,
`tracking_range`, `engagement_range`, `multi_target_capacity` (`Asset/Mobile.py:61-81`). Nei SAM/AAA il `model` del
radar nomina spesso il radar di **inseguimento** o un insieme, mentre `acquisition_range` e' la portata della
**ricerca**:

| Record | `radar['model']` nel registro | `acquisition_range` aria [km] | Funzione di ricerca reale (fonte) |
|---|---|---|---|
| `9K37-Buk` | `9S35 Fire Dome` (inseguimento) | 85 | 9S18 / 9S18M1 "Snow Drift" (P1 §3) |
| `S-300PS` | `30N6 Flap Lid` (ingaggio) | 150 | 5N64S "Big Bird-B"; 76N6 "Clam Shell" a bassa quota (D2 §2.4) |
| `2K22-Tunguska` | `1RL144 Search + 1A26 Tracking` (1A26 e' il calcolatore, D1 §2.3) | 18 | 1RL144 "Hot Shot" |
| `Flakpanzer-Gepard` | `Search and Tracking Radar` | 15 | MPDR-12 |
| `ZSU-23-4-Shilka` | `1RL33 Gun Dish` (stessa antenna per ricerca e inseguimento) | 20 | 1RL33, modo di ricerca circolare |
| `2K12-Kub` | `1S91 Straight Flush` (due antenne) | 75 | antenna 1S11 (D2 §2.2) |
| `9K331-Tor` | `Multifunction 3D Radar` | 25 | radar di scoperta 3D ("Scrum Half" = nome collettivo) |
| navi con due radar | es. `AN/SPS-49 + AN/SPS-67` (CVN) | aria 450, mare 80 | aria = SPS-49, mare = SPS-67 (D3 §2.1) |

Conseguenze per il design, lette sul codice:
1. **Il dwell e' sempre associato alla ricerca**: il motore lo legge con il sensore vincente sulla portata di
   acquisizione e lo usa solo per l'estrazione di rilevamento e per l'unione dei passaggi; `tracking_range` e
   `engagement_range` non lo vedono. Quindi la regola 3 dell'utente ("solo ricerca, l'inseguimento resta alla legge
   attuale") e' **gia' garantita dal codice**: basta che il **valore** scritto sia quello del radar di ricerca.
2. **L'ambiguita' e' solo di nome**: chi legge `'model': '9S35 Fire Dome'` accanto a `'dwell_time_s': 4.5` potrebbe
   credere che 4,5 s sia del Fire Dome. Si risolve con il commento del valore, che nomina il radar di ricerca (DW9-2).
3. **Un dwell per sensore, non per modo**: nelle navi con due radar (aria SPS-49, mare SPS-67) il dwell vale per tutti
   i modi del dizionario. E' irrilevante per i bersagli lenti: una nave o un mezzo a terra resta nel volume per
   decine di minuti, quindi `g = 1` qualunque sia il dwell (§1.7). Il valore da scrivere e' quello della ricerca
   **aerea**, l'unica in cui la permanenza puo' essere breve.
4. **Limiti residui** (non nuovi): il sensore e' uno per asset (quello della portata massima: un SAM con radar e TVD
   userebbe solo il dwell del vincente; nessun veicolo del registro ha entrambi [V]); `declare_sensor` delle fixture
   cambia la portata ma non il dwell (il dwell resta quello del registro).

### 1.4 Inventario del perimetro [V: registri caricati in memoria]

| Famiglia | Record | Sensore | Oggi | Nel perimetro? |
|---|---|---|---|---|
| SAM/AAA con radar | ZSU-23-4-Shilka, Flakpanzer-Gepard, 2K22-Tunguska, 9A33-Osa, MIM-115-Roland, 9K331-Tor, 2K12-Kub, 9K37-Buk, S-300PS (9) | `radar` | nessun dwell | si' |
| SAM con TVD | Strela-1-9P31, MIM-72G-Chaparral, 9K35-Strela-10, M6-Linebacker (4) | `TVD` (aria e terra) | nessuno | si' |
| AAA a vista | ZSU-57-2, M163-VADS (2) | `visual` (solo aria) | nessuno | si' |
| EWR | 10 con dwell (invariati); FuMG-80-Freya, Wassermann, AN-FPS-117, Chain-Home, Mammut senza (5) | `radar` | 10 su 15 | si' (i 5) |
| Navi | 23 record di `Ship_Data` (22 radar + Type 093 con "sonar passivo" nel campo `radar`, solo modo mare) | `radar` | nessuno | si' |
| AWACS | E-3A Sentry, E-2D Advanced Hawkeye, A-50 (3) | `radar` | nessuno | si' |
| Aerei non AWACS | 62 record di `Aircraft_Data` | `radar`, `TVD` | nessuno | **no** (decisione 1) |
| Altri veicoli | carri, IFV, artiglieria: `radar`/`TVD` False | — | — | non hanno sensori di registro |

Totale nel perimetro: 46 record senza dwell oggi; il piano ne valorizza **43** e ne lascia **3** senza valore con un
motivo scritto (Chain-Home, Mammut, Type 093; DW9-8).

### 1.5 Le fonti e il loro stato

- **P1** = `Ricerca_Dwell_Sensori_2026_11_06.md` (prima ricerca). Dato pulito solo per E-3A (10 s), AN/SPS-49 (6/12
  giri/min) e Roland MPDR-16 (60 giri/min); confidenza bassa-media per Buk, Kub, Gepard, Tor, Fregat-MA, Type 364.
- **D1..D4** = bozze della seconda passata `Bozze/Ricerca_Dwell_Passata2_D1..D4_oc-researcher.md` (2026-11-08):
  D1 tiratori a corto raggio, D2 SAM a ricerca rotante, D3 navi e AWACS, D4 vista e ottici.
- **Valori NON verificati (dichiarati dal compito, riletti qui)**: tutto cio' che D2 attribuisce a una "lettura
  diretta" di **GlobalSecurity** (pagina che risponde 403 al lettore della sessione principale; P1 la dava gia' come
  402/403 e "via ricerca"): **Buk 9S18** (2,5-4,5 s settore, 4,5-18 s circolare; 9S18M1-3 4,5 s), **Tor** ("modo
  principale 3 s, modo a 3 fasci 1 s"), **64N6E** ("una rotazione ogni 12 s"). Qui sono trattati come **[S] fonte non
  verificata**, mai come dati (DW9-1, DW9-4). L'utente puo' promuoverli a FONTE incollando la frase della pagina.
- **Nota non tracciata** `Dinamica dei Tempi di Aggiornamento Radar - Google Gemini.md` (comparsa nella cartella
  durante la stesura, 2026-11-17): spiega in modo qualitativo perche' i radar a scansione elettronica dichiarano un
  intervallo di tempi di rivisita (allocazione dinamica fra ricerca e inseguimento). Coerente con la scelta di trattare
  SPY-1 e Type 346 come stime (DW9-5); **non** e' una fonte di numeri.
- **Verifica a campione delle bozze**: il pianificatore non ha accesso al web (lo ha solo `oc-researcher`); la
  verifica e' quindi di **coerenza interna** (estratti contro conclusioni, conti, confronto con P1). Incongruenze
  trovate in Appendice C (6 punti; le piu' rilevanti: il Tor "a settore di 32 gradi in azimut" di D2 non e' sostenuto
  dai suoi stessi estratti; 64N6E 6/12 giri/min in P1 contro 12 s in D2; Type 381 "mirror 5 giri/min" in P1 contro
  "nessun valore" in D3).

### 1.6 Sonde eseguite per questa Proposta (sola lettura, brevi)

Script di sola lettura nella cartella temporanea della sessione (testo completo della sonda S-4 in Appendice A):
accendono `ER.D5_DWELL_TIME` in memoria, scrivono i valori raccomandati di §2 nei dizionari dei registri caricati
(**solo in memoria**) e chiamano `Scenario_Baseline.main(['--compare', <fotografia>, '--only', <regex>])`. Contano le
letture del dwell per modello (avvolgendo `ER.registry_dwell_time`) e le chiamate con `g < 1` (avvolgendo
`ER.dwell_factor`). Interprete: `python3` di sistema (osboxes).

| Sonda | Unita' (regex `--only`) | Esecuzioni | Esito letto | Letture del dwell per modello (valore) | `g < 1` |
|---|---|---|---|---|---|
| S-4a (solo ZSU-57-2 visiva 3,94 s) | `^S32` | 20 | `compared 20 runs: IDENTICAL (13.8 s)` | ZSU-57-2 3,94: 16 (in `ewr_on`), tutte con `g = 1` | 0 |
| S-4 parziale 1 | `^S21` (S21 e S21R) | 22 | `compared 22 runs: IDENTICAL (16.0 s)` | Strela-10 3,94: 110; Shilka 18: 110 | 19 (tutte `g = 0`) |
| S-4 parziale 2 | `^(S19AD\|S28-[A-Z]+\|S34-BAND\|S35-ADTGT\|S2\|S4)/` | 180 | `compared 180 runs: IDENTICAL (104.9 s)` | Osa 1,82: 128; Tor 1,0: 80; Strela-10 3,94: 64; Buk 4,5: 224; Rezky 5,0: 32 | 24 (tutte `g = 0`) |
| S-4 parziale 3 | `^(S1\|S3\|S6\|S7\|S9\|S9R\|S19\|S10..S16\|S18)/` | 196 | `compared 196 runs: IDENTICAL (331.7 s)` | Shilka 18: 415; Strela-10 3,94: 519; Molniya 5,0: 176; Buk 4,5: 20; S-300PS 12: 16; Tor 1,0: 9; Gepard 1,0: 9; CG-65 5,0: 8; Arleigh Burke 5,0: 8 | 34 (tutte `g = 0`) |
| S-4 parziale 4 | `^(S31-VISUAL\|S5\|S33-PASSES\|S8\|S32-DWELL)/` | 147 | `compared 147 runs: IDENTICAL (235.2 s)` | Tunguska 1,82: 182; Buk 4,5: 202; S-300PS 12: 464; Shilka 18: 182; M163-VADS 3,94: 32; ZSU-57-2 3,94: 32 (S31) e dichiarati di test 2 / 30 / 600 (S33, S32); P-18 6: 16 | 16 (tutte di S32 `short`, dwell 600 dichiarato di test) |

Lettura:
- In **545** esecuzioni distinte provate (su 1103) con l'interruttore acceso e **tutti** i valori raccomandati,
  nessuna cambia (S32 compare in S-4a e in S-4 parziale 4: contata una volta). Fuori da S32 `short`, le direzioni con
  `g < 1` hanno tutte `g = 0`: permanenza nulla, cioe' nessun passaggio nel volume proprio che tocchi la finestra; in
  quei casi la distanza minima supera la portata propria e la Pd era gia' 0 (stessa osservazione di S-1, Proposta
  precedente §1.9) [I sul motivo, V sul conteggio].
- S21, dove S-2 (10 s a ogni osservatore) aveva cambiato 2 esecuzioni, resta identica con Strela-10 a 3,94 s e Shilka
  a 18 s. S31-VISUAL (ZSU-57-2 e M163 a vista, 3,94 s) resta identica.
- Restano **558** esecuzioni non provate. Di queste, **507** (S22-E1/E3/AIR, S23-*, S24-*, S25-*, S26, S27, S29, S30)
  usano solo modelli **senza** valore nuovo (F-16C, MiG-29S, BMP-2, M1A2, 2S19 [V: ricerca dei letterali nei file
  degli scenari]): con la D-5 accesa e nessun dwell la legge e' quella di prima (S-1), quindi sono identiche per
  costruzione. Le altre **51** contengono o possono contenere sensori con valore nuovo: S17 (15) e S20 (12) e VAL
  (7) usano la composizione di S1 con Shilka e Strela-10 (`Scenario_Fixtures.combined_arms_scenario`,
  `:1021-1049`); ORC (17) non ha letterali di difese aeree nel file ma usa gli helper delle fixture [I]. Vanno coperte
  dalla sonda **S-4 completa** del blocco 0 (una quarta sonda parziale su queste 51 e' stata negata dal sistema di
  permessi della sessione di pianificazione: non e' stata eseguita).
- **Le sonde parziali usano la prima versione dei valori** (regola "rotazione piu' veloce": Buk 4,5, Tor 1,0, Kub 3,0,
  vista/TVD 3,94, navi 5,0), scritta prima della linea "valore centrale" dell'utente. I valori attuali di §2 (Buk 9,0,
  Tor 1,7, Kub 3,5, vista/TVD 3,2, Fregat-MA/Head Net-A 7,1, Top Pair 10) cadono tutti dentro le bande, i cui estremi
  la S-4 completa prova in due passate (blocco 0). Lo script dell'Appendice A ha i valori attuali.
- Queste sonde **non** sostituiscono il confronto dell'esecutore: provano i valori in memoria, non il codice scritto.

### 1.7 I numeri della corda per le nuove famiglie [calcolo; velocita' I]

Con L1 la Pd si riduce solo se la permanenza `tau` e' minore del dwell, cioe' se la corda percorsa nel volume e'
`L < v * dwell`; la profondita' massima di una corda `L` in un cerchio di raggio `R` e' circa `L^2 / (8 R)`.
`Pd(d) = f * (1 - 0,5 * (d/R)^4)` (`PD_AT_ACQUISITION_RANGE = 0.5`, esponente 4, stime gia' dichiarate nel motore).

| Osservatore (valore raccomandato) | R [km] | bersaglio, v [m/s] | dwell [s] | corda con g<1 | profondita' massima |
|---|---|---|---|---|---|
| Shilka (18) | 20 | F-16, 250 [I] | 18 | 4,5 km | ~127 m |
| Shilka all'estremo minimo della banda (3 s) | 20 | F-16, 250 | 3 | 0,75 km | ~3,5 m |
| Buk (9; banda 4,3-20) | 85 | F-16, 250 | 9 / 20 | 2,25 / 5 km | ~7,4 / ~37 m |
| Tor (1,7; banda 1-3) | 25 | F-16, 250 | 1,7 / 3 | 0,43 / 0,75 km | ~0,9 / ~2,8 m |
| S-300PS (12) | 150 | F-16, 250 | 12 | 3 km | ~7,5 m |
| Strela-10 TVD (3,2; banda 1,75-6) | 10 | F-16, 250 | 3,2 / 6 | 0,8 / 1,5 km | ~8 / ~28 m |
| ZSU-57-2 vista (3,2) | 6 | A-10C, 155,6 [V: `speed['nominal']`] | 3,2 | 0,5 km | ~5,2 m |
| CVN SPS-49 (5) | 450 | F/A-18, 250 | 5 | 1,25 km | ~0,4 m |
| Moskva Top Pair (10; banda 5-20) | 450 | F/A-18, 250 | 10 / 20 | 2,5 / 5 km | ~1,7 / ~6,9 m |
| E-3A (10) | 400 | caccia, 450 relativi [I] | 10 | 4,5 km | ~6 m |

Lettura: la riduzione colpisce solo contatti **radenti** (il bersaglio sfiora il bordo del volume). Un esempio di Pd:
un F-16 che sfiora il volume della Shilka per 9 s (corda 2,25 km, `d ~ R`) ha oggi `Pd ~ 0,5`; con dwell 18 s
`g = 9/18 = 0,5` e `Pd ~ 0,25`; con dwell 6 s `g = 1` e `Pd ~ 0,5`. Anche agli estremi delle bande la riduzione resta
confinata in poche decine di metri dal bordo del volume: e' il motivo per cui la scelta dentro l'intervallo pesa poco
(§3.4 punto d).

---

## 2. Valori proposti (una riga per record del registro)

Legenda delle etichette (colonna "Etichetta", da riportare **identica** nel commento del codice):
- **FONTE**: giri/min o periodo di fonte, convertito con 60/giri al minuto (D); regola sugli intervalli di §3.5
  (regime normale se citato, altrimenti valore centrale = media geometrica degli estremi del periodo, un decimale).
- **FONTE DEBOLE [S]**: fonte unica di confidenza bassa (forum, infobox senza definizione, articolo divulgativo): il
  numero viene dalla fonte ma si tratta come stima.
- **FONTE NON VERIFICATA [S]**: fonte non leggibile al controllo (GlobalSecurity, 403).
- **STIMA PER CONFRONTO [S]**: nessun dato; valore dell'analogo nominato.
- **nessun valore**: chiave assente, con il motivo nel commento.

Per i record con dato di fonte la colonna "Conf." riporta la confidenza della bozza; per le stime e' "stima".
Le righe marcate (R) dipendono da una decisione aperta: il valore e' quello **raccomandato**.
**Banda [s]** = intervallo di incertezza da riportare accanto al valore (commento del codice e registro): per i dati
di fonte e' l'intervallo dichiarato dalla fonte (o fra le fonti); per le stime per confronto e' l'intervallo degli
analoghi candidati; "—" = valore unico, nessuna banda. La sonda S-4 prova gli estremi (blocco 0).

### 2.1 SAM e AAA con radar (`Asset/Vehicle_Data.py`, dizionario `radar`)

| Record (variabile, riga) | Funzione di ricerca | Dato di partenza | Valore [s] | Banda [s] | Etichetta | Fonte o analogo | Conf. |
|---|---|---|---|---|---|---|---|
| `ZSU-23-4-Shilka` (`ZSU_23_4_data`, `:3765`) (R, DW9-3) | 1RL33, ricerca (stessa antenna dell'inseguimento) | circolare 20 gradi/s (modo base, = regime normale citato); accelerata 45-60 gradi/s (8-6 s); settore 30-100 gradi a 20 gradi/s (rivisita 3-10 s) | **18.0** (360/20, D) | 3-18 | FONTE di variante, attribuzione [S] | D1 §2.1, manuale 1RL33M3 (ZSU-23-4M) | M |
| `Flakpanzer-Gepard` (`Flakpanzer_Gepard_data`, `:3886`) | MPDR-12 | 60 giri/min | **1.0** | — | FONTE | D1 §2.4 (radartutorial karte031, Military Periscope); P1 | M-A |
| `2K22-Tunguska` (`K2K22_Tunguska_data`, `:3944`) (R, DW9-4) | 1RL144 "Hot Shot" (360 gradi, giri/min non trovati) | — | **1.82** | 1.0-4.0 (analoghi Gepard 1 s, Osa 1,82 s, Pantsir 2RL80 2-4 s) | STIMA PER CONFRONTO [S] | 9A33-Osa Land Roll (33 giri/min) | stima |
| `9A33-Osa` (`A9A33_Osa_data`, `:4121`) | Land Roll, antenna di acquisizione | 33 giri/min | **1.82** (60/33 = 1,818, D, arrotondato al centesimo) | — | FONTE | D1 §2.2 (ausairpower APA-9K33, missilery) | A (per la bozza) |
| `MIM-115-Roland` (`MIM115_Roland_data`, `:4237`) | MPDR-16 | 60 giri/min | **1.0** | — | FONTE | P1; D1 §2.5 (missilery) | M-A |
| `9K331-Tor` (`K9K331_Tor_data`, `:4295`) (R, DW9-1) | radar di scoperta 3D del Tor-M1 | APA: "scanning interval 1 s" e "entire elevation zone ... within 3 s"; "modo principale 3 s" solo da GlobalSecurity (NON verificato: il regime normale non e' citato da una fonte leggibile) | **1.7** (centrale di 1-3 s: radice di 1 x 3 = 1,73) | 1-3 | FONTE, valore centrale, interpretazione [S] | D2 §2.3 (ausairpower APA-9K331, che cita Military Parade 1996) | M |
| `2K12-Kub` (`K2K12_Kub_data`, `:4412`) | antenna 1S11 del 1S91 | 15 o 20 giri/min (nessun regime normale) = 4 o 3 s | **3.5** (centrale: radice di 3 x 4 = 3,46) | 3-4 | FONTE, valore centrale | D2 §2.2 (radartutorial karte011) | M |
| `9K37-Buk` (`K9K37_Buk_data`, `:4470`) (R, DW9-1) | 9S18 / 9S18M1 (non il 9S35 Fire Dome) | circolare 4,5-18 s (GlobalSecurity, NON verificato); 3-14 giri/min = 20-4,3 s (radartutorial 9S18M, via ricerca); nessun regime normale | **9.0** (centrale di 4,5-18 s: radice di 81) | 4.3-20 | FONTE NON VERIFICATA [S], valore centrale | P1 §3; D2 §2.1 | bassa-media |
| `S-300PS` (`S300PS_data`, `:4528`) (R, DW9-4) | 5N64S "Big Bird-B" (giri/min non trovati), non il 30N6 | — | **12.0** | 5-12 (P1: 64N6E 6/12 giri/min = 10/5 s; D2: 12 s "regolare") | STIMA PER CONFRONTO [S] | 64N6/64N6E "Tombstone" (stessa famiglia, S-300PM): "rotazione ogni 12 s", regime "regolare" (D2 §2.4; GlobalSecurity non verificato, APA e valka.cz secondo la bozza) | stima |

### 2.2 SAM con TVD e AAA a vista (`Asset/Vehicle_Data.py`, dizionari `TVD` e `visual`) (R, DW9-6)

Tutti con lo **stesso** valore, la stessa banda e la stessa nota di approssimazione.

| Record (variabile, riga) | Sensore | Funzione di ricerca | Valore [s] | Banda [s] | Etichetta | Analogo |
|---|---|---|---|---|---|---|
| `Strela-1-9P31` (`Strela1_9P31_data`, `:4005`) | `TVD` "Optical sight" | ricerca a vista del servente (il mirino serve dopo la scoperta) | **3.2** (centrale di 1,75-6,00 s: radice di 10,5 = 3,24) | 1.75-6.0 | STIMA PER CONFRONTO [S], valore centrale, APPROSSIMAZIONE L1 | Poe 1974 (ADA017599, tab. 2): durata di una passata completa del settore da osservatori a terra, 1,75-6,00 s fra tutte le passate (medie 2,72 / 2,99 / 3,94 s per 30 / 60 / 120 gradi), nessun regime normale (D4 §2.1) |
| `MIM-72G-Chaparral` (`MIM72G_Chaparral_data`, `:4063`) | `TVD` FLIR | idem | **3.2** | 1.75-6.0 | idem | idem |
| `9K35-Strela-10` (`K9K35_Strela10_data`, `:4179`) | `TVD` "Optical-IR tracker" | idem (il telemetro 9S86 non scopre) | **3.2** | 1.75-6.0 | idem | idem |
| `M6-Linebacker` (`M6_Linebacker_data`, `:4353`) | `TVD` FLIR | idem (il cueing radar esterno non e' modellato) | **3.2** | 1.75-6.0 | idem | idem |
| `ZSU-57-2` (`ZSU_57_2_data`, `:3701`) | `visual` | vista dell'equipaggio | **3.2** | 1.75-6.0 | idem | idem |
| `M163-VADS` (`M163_VADS_data`, `:3823`) | `visual` | vista del puntatore | **3.2** | 1.75-6.0 | idem | idem |

### 2.3 EWR rimasti senza valore (`Asset/Vehicle_Data.py`, `radar`) (R, DW9-8)

| Record (variabile, riga) | Dato di partenza | Valore [s] | Banda [s] | Etichetta | Analogo o motivo |
|---|---|---|---|---|---|
| `FuMG-80-Freya` (`FuMG80_Freya_data`, `:4692`) | schiera orientabile 360 gradi, velocita' non data | **60.0** | 7.5-60 (analoghi AMES Type 7 e SCR-270) | STIMA PER CONFRONTO [S] | SCR-270 (EWR a rotazione 1940, 1 giro/min; stessa classe ed epoca) |
| `Wassermann` (`Wassermann_data`, `:4984`) | traliccio ruotabile, velocita' non data | **60.0** | 7.5-60 | STIMA PER CONFRONTO [S] | SCR-270 |
| `AN-FPS-117` (`AN_FPS117_data`, `:4876`) | array planare rotante, rotazione non riportata | **10.0** | — | STIMA PER CONFRONTO [S] | AN-TPS-43 (EWR 3D statunitense a rotazione, 6 giri/min) |
| `Chain-Home` (`Chain_Home_data`, `:4901`) | antenna fissa a illuminazione continua | — | — | nessun valore | invariato (commento esistente `:4925`) |
| `Mammut` (`Mammut_data`, `:5011`) | schiera fissa a scansione elettronica su 100 gradi, cadenza non data | — | — | nessun valore | nessun analogo credibile: l'unico radar fisso dei registri (Chain-Home) non ha periodo |

I 10 EWR con dato (SCR-270 60; P-12 e P-18 6; P-37, 1L13, 55Zh6, AN-TPS-43, P-14 10; AMES Type 7 7,5; AMES Type 80
15) restano **invariati** (contratto precedente). Nota: per quattro di loro la fonte da' un intervallo senza regime
normale e DW-2 aveva scelto la rotazione **piu' veloce**; con la regola di §3.5 il valore centrale sarebbe diverso
(P-37 e 1L13 3-6 giri/min: 14,1 s invece di 10; P-14 2-6: 17,3 invece di 10; AMES Type 7 0,5-8: 30 invece di 7,5).
Questo piano **non** li tocca (perimetro della linea dell'utente); il disallineamento e' dichiarato in §6 e
nell'elenco delle cose da decidere dopo.

### 2.4 Navi (`Asset/Ship_Data.py`, `radar`) (R, DW9-5)

| Record (variabile, riga `'radar'`) | `radar['model']` | Ricerca aerea usata | Dato di partenza | Valore [s] | Banda [s] | Etichetta | Fonte o analogo | Conf. |
|---|---|---|---|---|---|---|---|---|
| `CVN-70`..`CVN-75` (6: `CVN70_data` `:495`, `CVN71_data` `:534`, `CVN72_data` `:573`, `CVN73_data` `:612`, `CVN74_data` `:651`, `CVN75_data` `:690`) | AN/SPS-49 + AN/SPS-67 | SPS-49 | 6 giri/min lunga portata, 12 corta; default 12 sull'A(V)1 | **5.0** | 5-10 | FONTE (il default 12 giri/min e' il regime normale citato) | D3 §2.3 (Wikipedia, FAS, radartutorial) | A |
| `CV-59 USS Forrestal` (`CV59_data`, `:729`) | AN/SPS-43 + AN/SPS-30 | SPS-43 (non trovato) | — | **5.0** | 5-10 | STIMA PER CONFRONTO [S] | AN/SPS-49 (successore, ricerca aerea 2D US Navy) | stima |
| `CV 1143.5 Admiral Kuznetsov` (`KuznetsovAdmiral_data`, `:770`) | Sky Watch + Fregat-MA | Fregat-MA (Sky Watch fisso, non trovato) | 12 o 6 giri/min = 5 o 10 s, nessun regime normale | **7.1** (centrale: radice di 50 = 7,07) | 5-10 | FONTE, valore centrale | D3 §2.4 (radartutorial karte091) | M |
| `USS Arleigh Burke IIa` (`ArleighBurke_data`, `:817`) | AN/SPY-1D(V) | SPY-1 (schiera fissa) | "1 (orizzonte), 12 (sopra l'orizzonte) scan/min" (infobox, significato non definito): due funzioni di ricerca diverse, non un intervallo della stessa; per bersagli aerei vale "sopra l'orizzonte" | **5.0** (60/12) | 5-60 | FONTE DEBOLE [S] | D3 §2.2 | bassa |
| `Type 052B Guangzhou-class` (`Type052B_data`, `:859`) | Type 381 | Type 381 (non trovato) | — | **7.1** | 5-10 | STIMA PER CONFRONTO [S] | Fregat-MA (radar 3D navale rotante della stessa epoca; suo valore centrale) | stima |
| `Type 052C` (`Type052C_data`, `:901`) | Type 346 AESA | Type 346 (schiera fissa, non trovato) | — | **5.0** | 5-60 | STIMA PER CONFRONTO [S] | AN/SPY-1 (schiera fissa a fasci elettronici) | stima |
| `CG-65` (`CG65_data`, `:948`) | AN/SPY-1A | SPY-1 | come Arleigh Burke | **5.0** | 5-60 | FONTE DEBOLE [S] | D3 §2.2 | bassa |
| `CGN 1144.2 Piotr Velikiy` (`PiotrVelikiy_data`, `:990`) | Fregat-MA + Podkat + Top Pair | Fregat-MA (primo radar del record) | Fregat-MA 12 o 6 giri/min; Top Pair 3-12 giri/min | **7.1** (centrale del Fregat-MA) | 5-20 (i due radar) | FONTE, valore centrale | D3 §2.4, §2.5.1 | M |
| `CG 1164 Moskva` (`Moskva_data`, `:1032`) | MR-800 Voskhod + Top Dome | MR-800 "Top Pair" | 3-12 giri/min = 20-5 s, nessun regime normale | **10.0** (centrale: radice di 100) | 5-20 | FONTE, valore centrale | D3 §2.5.1 (radartutorial MR-600) | M |
| `FFG-46` (`FFG46_data`, `:1079`) | AN/SPS-49 + AN/SPS-55 | SPS-49 | come CVN | **5.0** | 5-10 | FONTE | D3 §2.3 | A |
| `FF 1135M Rezky` (`FF1135M_data`, `:1121`) | Head Net-C + Eye Bowl | Head Net-C (non trovato) | Head Net-A 6 o 12 giri/min | **7.1** | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (MR-310; la -C e' la versione a due facce della -A; suo valore centrale) | stima |
| `FFG 11540 Neustrashimy` (`FFG11540_data`, `:1163`) | Fregat-MA + Mineral-ME | Fregat-MA | 12 o 6 giri/min | **7.1** | 5-10 | FONTE, valore centrale | D3 §2.4 | M |
| `Type 054A` (`Type054A_data`, `:1205`) | Type 382 + MR-36 Podkat | Type 382 | ~30 giri/min (forum) | **2.0** | 2-10 (forum contro l'analogo Fregat MAE-3) | FONTE DEBOLE [S] | D3 §2.6.1 (Sino Defence Forum); alternativa: Fregat MAE-3 7,1 s | bassa |
| `FFL 1124.4 Grisha` (`FFL1124_data`, `:1252`) | Strut Curve + Muff Cob | MR-302 (campo di rotazione vuoto) | — | **7.1** | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (ricerca aerea navale sovietica coeva) | stima |
| `FSG 1241.1MP Molniya` (`FSG1241_data`, `:1293`) | Band Stand + Bass Tilt | nessun radar di ricerca nel record (Band Stand = radar di tiro, D3 §2.5.4) | — | **7.1** | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (la `acquisition_range` di 130 km rappresenta la ricerca della corvetta) | stima |
| `Type 093` (`Type093_data`, `:1337`) | None (passive sonar primary) | sonar passivo, solo modo mare | — | — | — | nessun valore | ascolto continuo, nessuna scansione (come Chain-Home) | — |
| `LHA-1 Tarawa` (`LHA1_data`, `:1382`) | AN/SPS-52 + AN/SPS-67 | SPS-52 (non trovato) | — | **5.0** | 5-10 | STIMA PER CONFRONTO [S] | AN/SPS-49 (ricerca aerea US Navy coeva) | stima |
| `Type 071` (`Type071_data`, `:1422`) | Type 360 + Type 364 | Type 364 (ricerca aerea; Type 360 non trovato) | 30 giri/min | **2.0** | — | FONTE | D3 §2.6.4 (Wikipedia Type 364) | M |

### 2.5 AWACS (`Asset/Aircraft_Data.py`, `radar`; chiavi con doppi apici) (R, DW9-7)

| Record (variabile, riga) | Radar | Dato di partenza | Valore [s] | Banda [s] | Etichetta | Fonte | Conf. |
|---|---|---|---|---|---|---|---|
| `E-3A Sentry` (`e3a_data`, `:2133`) | AN/APY-2 | 6 giri/min | **10.0** | — | FONTE | P1 §4 (Wikipedia E-3, schede USAF) | alta |
| `E-2D Advanced Hawkeye` (`e2d_data`, `:2097`) | AN/APY-9 | 6 giri/min | **10.0** | — | FONTE | D3 §2.7.1 (radartutorial karte083, Wikipedia) | M |
| `A-50` (`a50_data`, `:3393`) | Shmel | "circa sei giri al minuto" | **10.0** | — | FONTE DEBOLE [S] (coincide con l'analogo E-3A) | D3 §2.7.2 (zemelka.ua, divulgativo) | bassa |

### 2.6 Riepilogo dei conteggi

43 valori (invariati nel numero e nelle etichette dopo la linea "valore centrale"; rispetto alla prima versione
cambiano 17 valori: Buk, Tor, Kub; 6 vista/TVD; Kuznetsov, Neustrashimy, Piotr Velikiy, Moskva, Type 052B, Rezky,
Grisha, Molniya): **18 FONTE** (Gepard, Osa, Roland, Kub; 6 CVN, Kuznetsov, Piotr Velikiy, Moskva, FFG-46, Neustrashimy,
Type 071; E-3A, E-2D) e **25 [S]** (Shilka per l'attribuzione di variante, Tor per l'interpretazione, Buk, Tunguska,
S-300PS; 6 TVD/vista; Freya, Wassermann, AN-FPS-117; CV-59, Arleigh Burke, CG-65, Type 052B, Type 052C, Rezky,
Type 054A, Grisha, Molniya, LHA-1; A-50). 3 senza valore (Chain-Home, Mammut, Type 093). Tutte le 25 [S] entrano nel
registro dei dwell stimati (DW9-9, Appendice B).

---

## 3. Alternative e raccomandazione (temi trasversali)

### 3.1 Struttura del dato nei record che fondono ricerca e inseguimento (dettaglio in DW9-2)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **A1 chiave unica per sensore** | `dwell_time_s` nel dizionario del sensore, come gli EWR; il commento nomina il radar di ricerca | zero codice; il motore la legge gia' solo con la portata di acquisizione (§1.3); stessa forma dei 10 EWR | il nome del radar di ricerca e' solo in un commento |
| A2 chiave unica + chiave documentale | come A1 piu' `'search_model': '9S18'` nel dizionario, letta solo da un test | il nome del radar di ricerca e' un dato, verificabile | un campo che nessun codice di produzione legge; 9+ record da toccare in piu' |
| A3 dwell per modo | `dwell_time_s` dentro `capabilities[modo][1]`, accanto ad `acquisition_range` | precisione per le navi con radar aria/mare diversi | cambia `Mobile._sensor_dwell_s` e i lettori (codice e test), ricolloca i 10 EWR; nessun effetto fisico (bersagli lenti: `g = 1`, §1.3 punto 3) |

**Raccomandazione: A1.** Il codice garantisce gia' la regola "solo ricerca"; il resto e' documentazione.

### 3.2 Interruttore

L'intervento e' solo un dato per una regola che esiste: `D5_DWELL_TIME` (spento) basta. Spento, `Session_Simulator` non
passa il lettore e nessun dwell entra nel risolutore (§1.2); il pianificatore li copia nelle `DetectionThreat` ma li
usa solo con l'interruttore acceso (`Air_Route_Manager.py:1132`). Alternativa scartata: un interruttore per famiglia
(es. escludere vista e TVD per la loro natura approssimata): non chiesto, e riproducibile in una sonda o in un test con
`patch.dict` sui dizionari. **Raccomandazione: nessun interruttore nuovo.**

### 3.3 Registro dei dwell stimati (dettaglio in DW9-9)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **R1 documento + costanti di test** | `Analysis/Document/Registro_Dwell_Stimati.md` (tabella leggibile, Appendice B) e in `Test/Test_Dwell_Data.py` le costanti `DWELL_S`, `DWELL_ESTIMATED`, `NO_DWELL` con un test che verifica che ogni record del perimetro abbia un valore o un motivo | il documento si legge, il test impedisce che un asset nuovo entri senza decisione | due copie (documento e test) da tenere allineate a mano |
| R2 solo documento | tabella markdown | semplice | nessuna protezione contro record nuovi senza valore |
| R3 costante nel registro | dizionario `DWELL_ESTIMATED` in `Vehicle_Data.py`/`Ship_Data.py`/`Aircraft_Data.py` | vicino al dato | codice di produzione che serve solo alla documentazione; tre moduli |

**Raccomandazione: R1.**

### 3.4 Dwell fisso o variabile con distanza, modo e carico del radar (linea DECISA dall'utente, 2026-11-17)

Il documento `Dinamica dei Tempi di Aggiornamento Radar - Google Gemini.md` (qualitativo, soprattutto radar AESA)
elenca le cause per cui un radar dichiara un **intervallo** di tempi di rivisita: priorita' dei bersagli, modo di
ricerca o inseguimento, settore o 360 gradi, integrazione di piu' impulsi a grande distanza, clutter e disturbo.

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **F1 valore fisso per sensore** (DECISA) | un `dwell_time_s` per sensore, solo funzione di ricerca; l'intervallo di fonte diventa una banda di incertezza (§3.5) | nessun codice nuovo; nessun parametro nuovo da tarare; coerente con L1 | non rappresenta l'adattivita' dei radar a scansione elettronica |
| F2 dwell funzione della distanza | `dwell(d)` crescente con la distanza (integrazione degli impulsi) | segue la causa 4 del documento | **conta due volte la distanza**: la dipendenza dalla distanza e' gia' in sostanza in `Pd(d)` di L1 (`min(1, permanenza/dwell) x Pd(d)`); serve una legge `dwell(d)` senza dati |
| F3 dwell funzione del modo o del carico | valori diversi per ricerca a settore/360 gradi, RWS/TWS, numero di bersagli | segue le cause 1-3 del documento | il motore **non ha uno stato di modo del radar** (RWS/TWS non modellati; il parametro `mode` di `Mobile.detection_dwell_time` e' il dominio del bersaglio aria/terra/mare, non il modo del radar, `Asset/Mobile.py:1692`); per i radar meccanici l'intervallo di fonte viene dalla **geometria** (settore o 360 gradi, Shilka e Buk), non dalla distanza |

Motivi della scelta F1 (da riportare nel manuale):
- (a) la distanza e' gia' in `Pd(d)`: un dwell che cresce con la distanza la conterebbe due volte;
- (b) il motore non ha stato di modo del radar: un dwell per modo non avrebbe chi lo sceglie;
- (c) per i radar meccanici l'intervallo di fonte e' geometrico (settore contro giro completo), non di distanza;
- (d) **sensibilita' misurata** (sonde S-1 e S-2, Proposta precedente §1.9): dwell uniforme di 2 / 6 / 10 / 30 / 60 /
  120 s a **ogni** osservatore = 0 / 0 / 3 / 17 / 45 / 464 rilevamenti persi su 29 483; a 10 s, 2 esecuzioni
  cambiate su 1009. Nell'intervallo dei sensori reali (1-30 s) la scelta di un valore dentro l'intervallo pesa poco;
  la S-4 lo verifica sui valori di questo piano con le due passate agli estremi (blocco 0).

Il **rinvio** di un dwell dipendente da distanza, modo e carico del radar e' dichiarato in §6 e nel capitolo 9 del
manuale: da fare insieme all'orizzonte radar nel DES e a una legge cumulativa (Koopman/esponenziale).

### 3.5 Intervalli di fonte: valore fisso e banda di incertezza (linea DECISA dall'utente)

**Regola** (estende DW-2 del contratto precedente, che per gli intervalli senza regime normale prendeva la rotazione
piu' veloce):
1. se la fonte cita un **regime normale** (o "base", "default", "regolare", "modo principale" in una fonte leggibile),
   si usa quello;
2. altrimenti si usa il **valore centrale** dell'intervallo, calcolato come **media geometrica degli estremi del
   periodo** `sqrt(T_min x T_max)`, arrotondata a un decimale (stima di progetto [S]);
3. l'intervallo di fonte si riporta come **banda di incertezza** accanto al valore, nel commento del codice
   (`Banda <min>-<max> s.`) e nel registro dei dwell stimati (colonna "Banda di incertezza");
4. per le **stime per confronto** la banda e' l'intervallo dei valori degli analoghi candidati; per un valore unico
   non c'e' banda ("—").

**Intervalli asimmetrici.** La fonte da' spesso giri/min (3-12) e non secondi; la media aritmetica dei periodi
(12,5 s per 3-12 giri/min) pesa verso l'estremo lento, quella dei giri/min (7,5 giri/min = 8 s) verso il veloce. La
media geometrica da' lo **stesso** risultato partendo dai giri/min o dai secondi (`60 / sqrt(rpm_min x rpm_max)` =
`sqrt(T_min x T_max)`: 10 s per 3-12 giri/min) e sta a uguale distanza in rapporto dai due estremi: e' la scelta del
piano. Le forme "N (fino a M)" (AMES Type 80) si leggono come regime base N, quindi regola 1. Due numeri che
descrivono **funzioni diverse** (SPY-1: orizzonte contro sopra l'orizzonte) non sono un intervallo: si sceglie la
funzione che vede i bersagli aerei e l'altro numero entra solo nella banda.

**Effetto sui 10 EWR del contratto precedente**: non toccati (§2.3, nota; §6).

---

## 4. Decisioni aperte per l'utente

Una per volta, nell'ordine. Ogni decisione ha una raccomandazione; il piano di §5 e' scritto per le raccomandazioni e
la tabella di §2 va aggiornata dal pianificatore prima dell'esecuzione se l'utente sceglie diversamente. Formula usata
negli esempi: `Pd = g * Pd(d)`, `g = min(1, permanenza/dwell)`, `Pd(d) ~ 0,5` vicino al bordo del volume.

### DW9-1 — Buk e Tor: quale valore fisso dentro l'intervallo (dati in parte non verificati)

**Domanda.** Quale valore fisso, dentro l'intervallo di fonte, per il Buk e il Tor, i cui dati vengono in parte da
una pagina (GlobalSecurity) che il controllo non riesce a leggere? Il modo del radar non si sceglie (§3.4): si sceglie
un numero dentro la banda.
- **Buk (radar di ricerca 9S18)**, banda 4,3-20 s (giro circolare 4,5-18 s da GlobalSecurity, non verificato;
  3-14 giri/min = 20-4,3 s dalla scheda radartutorial del 9S18M, via ricerca; nessun regime normale): (a) **9,0 s,
  valore centrale** (radice di 4,5 x 18) [S, fonte non verificata]; (b) 4,5 s, estremo veloce (la regola "rotazione piu'
  veloce" della prima versione); (c) 3,5 s per confronto con il Kub 1S11 (predecessore, dato leggibile).
- **Tor**, banda 1-3 s: Air Power Australia (leggibile, cita Military Parade 1996) da' "scanning interval 1 s" e "intera
  zona di elevazione in 3 s", senza dire quale sia il regime normale; il "modo principale 3 s" e' solo in GlobalSecurity
  (non verificato). (a) **1,7 s, valore centrale** (radice di 1 x 3); (b) 3,0 s, regime normale, **se** l'utente
  incolla la frase di GlobalSecurity (regola 1 di §3.5); (c) 1,0 s, estremo veloce.
- In entrambi i casi l'utente puo' **incollare la frase** della pagina: il valore diventa FONTE (e, per il Tor, il
  regime normale citato fissa 3,0 s).

**Raccomandazione**: Buk (a) 9,0 s; Tor (a) 1,7 s (diventa 3,0 s se la frase "modo principale" e' verificata). Motivo:
la regola di §3.5 applicata alle sole fonti leggibili; nessun dato non verificato presentato come tale.

**Esempio.** Un F-16 a 250 m/s sfiora il volume del Tor (25 km) per 2 s: con 1,7 s `g = 1`, Pd ~ 0,5 (come oggi); con
3 s `g = 0,67`, Pd ~ 0,33. Per il Buk (85 km): con 9 s la Pd si riduce per corde sotto 2,25 km (entro ~7 m dal
bordo); un passaggio radente di 6 s ha Pd ~ 0,5 x 6/9 = 0,33; con 4,5 s `g = 1` e Pd ~ 0,5; con 20 s (estremo) 0,15.

### DW9-2 — Dove sta il dwell nei record che fondono ricerca e inseguimento

**Domanda.** Il registro ha un solo dizionario `radar` per Buk, S-300PS, Tunguska, Gepard, Shilka, Kub, Tor; il suo
`model` nomina spesso il radar di inseguimento. Come si scrive il dwell della **ricerca**?
- (A1) **chiave `dwell_time_s` nel dizionario del sensore, commento che nomina il radar di ricerca** (nessun codice);
- (A2) come A1 piu' una chiave documentale `search_model`;
- (A3) dwell per modo dentro `capabilities` (codice nuovo in `Mobile`).

**Raccomandazione: A1** (§3.1). Il motore legge il dwell solo con la portata di acquisizione: l'inseguimento resta
alla legge attuale per costruzione (§1.3).

**Esempio (Buk).** Il record dice `'model': '9S35 Fire Dome'`, `acquisition_range` 85 km, `tracking_range` 45 km. Con
A1 si aggiunge `'dwell_time_s': 9.0` e il commento "ricerca 9S18 (non il 9S35 di inseguimento) ... Banda 4.3-20 s".
Nel DES il Buk rileva un caccia entro 85 km con `g = min(1, permanenza/9)`; dopo il rilevamento il tiro (45 km) non legge il dwell.

### DW9-3 — Shilka: quale valore fisso dentro l'intervallo 3-18 s

**Domanda.** Il manuale del 1RL33**M3** (ZSU-23-4M) da' tempi di rivisita fra 3 e 18 s secondo la geometria di
ricerca: circolare a 20 gradi/s (18 s per giro, il modo base), circolare accelerata a 45-60 gradi/s (8-6 s), settore
di 30-100 gradi a 20 gradi/s (3-10 s). Il registro e' la ZSU-23-4 base del 1965 e il DES non modella il modo: quale
numero fisso?
- (a) **18 s**: il modo base circolare e' il **regime normale citato** (regola 1 di §3.5; l'accelerata e' presentata
  come modo a parte), con lettura analoga a quella dell'AMES Type 80 [S]; il DES non ha copertura angolare, quindi il
  giro completo e' la geometria piu' coerente;
- (b) 7,3 s: valore centrale della banda 3-18 s (radice di 54), se non si riconosce un regime normale;
- (c) 3 s: estremo minimo (settore di 30 gradi).
- In tutti i casi l'attribuzione del dato della variante M3 al 1RL33 base e' una stima [S]; la banda 3-18 s va nel
  commento e nel registro.

**Raccomandazione: (a) 18 s.** Regola di §3.5 punto 1; le sonde parziali (§1.6: S21, S10-S19 con la Shilka a 18 s)
non mostrano cambiamenti; la S-4 prova anche 3 s (passata al minimo).

**Esempio.** F-16 a 250 m/s contro il volume della Shilka (20 km): con 18 s la Pd si riduce per corde sotto 4,5 km
(entro ~127 m dal bordo); un passaggio radente di 12 s ha Pd ~ 0,5 x 12/18 = 0,33 invece di 0,5. Con 7,3 s lo stesso
passaggio ha `g = 1` (Pd 0,5) e la riduzione resta entro ~21 m dal bordo; con 3 s entro ~3,5 m.

### DW9-4 — S-300PS e Tunguska: quale analogo

**Domanda.** Nessuno dei due ha un dato per il proprio radar di ricerca.
- **S-300PS** (ricerca reale: 5N64S "Big Bird-B", non trovato): (a) **12 s [S]** per confronto con il 64N6/64N6E
  (stessa famiglia "Big Bird", sistema successivo S-300PM; la cifra 12 s viene da GlobalSecurity non verificato e,
  secondo la bozza, da una tabella di Air Power Australia e da valka.cz; P1 riportava invece 6 o 12 giri/min = 10 o
  5 s: Appendice C); (b) 3 s (76N6 "Clam Shell", 20 giri/min, FONTE ma e' il radar di **bassa quota** della batteria,
  non la ricerca principale); (c) nessun valore.
- **Tunguska** (1RL144, giri/min non trovati): (a) **1,82 s [S]** per confronto con il 9A33-Osa Land Roll (ricerca
  sovietica a 360 gradi con antenna separata dal tracker); (b) 1,0 s [S] con il Gepard MPDR-12 (stessa classe di
  semovente antiaereo, stessa epoca, occidentale); (c) 2 s [S] con il Pantsir 2RL80 (successore, 30 giri/min).

**Raccomandazione**: S-300PS (a) 12 s; Tunguska (a) 1,82 s. Motivo: l'analogo della stessa famiglia/scuola; per lo
S-300PS il 76N6 copre solo la bassa quota.

**Esempio.** S-300PS (150 km) contro un F-16 a 250 m/s: con 12 s la riduzione resta entro ~7,5 m dal bordo; con 3 s
entro ~0,5 m. Tunguska (18 km): con 1-2 s la riduzione resta entro ~1-2 m dal bordo: nessun effetto pratico.

### DW9-5 — Navi

**Domanda.** Che regola per le 23 navi? Proposta (tabella §2.4): radar rotanti con dato -> FONTE con la regola di
§3.5 (SPS-49 5 s, regime "default" citato; Fregat-MA 7,1 s e Top Pair 10 s, valori centrali; Type 364 2 s); fonti
deboli (SPY-1 "12 scan/min", Type 382 "30 giri/min" da forum) -> FONTE DEBOLE [S]; radar senza dato -> analogo della
stessa marina ed epoca, con il suo valore (5 o 7,1 s); Type 093 (sonar passivo) -> nessun valore. Bande in §2.4.
Sotto-scelte:
- SPS-49: (a) **5 s** (regola DW-2: "default 12 giri/min" e' il regime normale citato) oppure (b) 10 s (6 giri/min,
  il modo a lunga portata coerente con i 450 km di `acquisition_range`);
- Type 054A: (a) **2 s** (forum, [S]) oppure (b) 7,1 s per confronto con il Fregat MAE-3 (presunta origine del Type
  382 secondo Jane's 2015, citato da Wikipedia);
- Molniya (Band Stand = radar di tiro, non di ricerca): (a) **7,1 s [S]** per confronto con Head Net-A, perche' la sua
  `acquisition_range` rappresenta la ricerca della corvetta, oppure (b) nessun valore;
- SPY-1 e Type 346 (schiere fisse, il periodo dipende dal programma del calcolatore): (a) **5 s [S]** oppure (b)
  nessun valore.

**Raccomandazione**: le (a). Effetto pratico nullo nelle sessioni: volumi di 130-550 km.

**Esempio.** CVN (450 km) contro un F/A-18 a 250 m/s: con 5 s la riduzione resta entro ~0,4 m dal bordo, con 10 s
entro ~1,7 m. Bersagli navali (modo mare, 10-15 m/s) restano nel volume per ore: `g = 1` sempre.

### DW9-6 — Vista e TVD: quale valore fisso dentro l'intervallo 1,75-6,0 s, e nota di approssimazione

**Domanda.** La vista non ha un periodo di rotazione. Poe 1974 (ADA017599, tabella 2) misura la durata di una passata
completa del settore da osservatori a terra: 1,75-6,00 s fra tutte le passate, medie 2,72 / 2,99 / 3,94 s per settori
di 30 / 60 / 120 gradi, nessun regime normale. Quale numero fisso per ZSU-57-2, M163 e i SAM con TVD (Strela-1,
Chaparral, Strela-10, M6), sapendo che L1 e' un'approssimazione?
- (a) **3,2 s [S], valore centrale** della banda 1,75-6,0 s (radice di 1,75 x 6 = 3,24; vicino alla media del settore
  di 60 gradi);
- (b) 3,94 s [S]: media del settore di **120 gradi**, il piu' ampio misurato (il DES non ha copertura angolare e un
  servente sorveglia un settore ampio): scelta geometrica, come il giro completo della Shilka;
- (c) 2,0 s [S]: la stima dell'utente del 2026-11-08 ("osservatore umano piu' ottica"), gia' usata come valore
  **dichiarato di test** in S33-PASSES (`Test_Session_Scenarios_S33.py:62-66`); nessuna fonte, ma dentro la banda.
- I TVD dei SAM (mirini ottici, FLIR) prendono lo stesso valore e la stessa banda: la scoperta e' a vista del
  servente (P1 §5, D4 §2.5); per l'M6 il cueing radar esterno non e' modellato.

**Nota di approssimazione da scrivere** (nel codice, nel registro, nel manuale): "APPROSSIMAZIONE: la scoperta a vista
non ha un periodo di rivisita; la letteratura (Koopman; Poe 1974) la descrive con una probabilita' cumulata che cresce
a ogni colpo d'occhio (~3 al secondo). Il valore e' la durata di una passata del settore usata con la legge L1; da
rivedere quando il motore avra' una legge cumulativa (Koopman/esponenziale)."

**Raccomandazione: (a) 3,2 s.** Regola di §3.5 punto 2 su un riferimento misurato e nominato (regola 2 dell'utente);
(b) e' l'alternativa geometrica; (c) resta la stima dell'utente senza fonte. La S-4 prova 1,75 e 6,0 s.

**Esempio.** ZSU-57-2 (6 km) contro un A-10C a 155,6 m/s: con 3,2 s la riduzione resta entro ~5 m dal bordo; un
passaggio radente di 2 s ha Pd ~ 0,5 x 2/3,2 = 0,31 invece di 0,5; con 3,94 s 0,25; con 2,0 s `g = 1` (Pd 0,5).

### DW9-7 — AWACS

**Domanda.** E-3A ed E-2D hanno un dato (6 giri/min = 10 s); l'A-50 solo una fonte divulgativa ("circa sei giri al
minuto"). (a) **10 s a tutti e tre** (A-50 come FONTE DEBOLE [S], coincidente con l'analogo E-3A); (b) A-50 senza
valore.

**Raccomandazione: (a).** Gli AWACS non hanno armi: nel DES cambiano solo la percezione (Proposta precedente §1.5) e
nessuno scenario li usa [V: nessun letterale negli scenari].

**Esempio.** E-3A (400 km) contro un caccia a 450 m/s relativi: riduzione entro ~6 m dal bordo.

### DW9-8 — EWR senza dato e asset senza analogo credibile

**Domanda.** (1) Freya e Wassermann (EWR tedeschi a rotazione, velocita' non data): (a) **60 s [S]** per confronto
con lo SCR-270 (EWR, 1940, 1 giro/min: stessa classe ed epoca); (b) 7,5 s [S] con l'AMES Type 7 (radar GCI
britannico, piu' veloce); (c) nessun valore. (2) AN-FPS-117: (a) **10 s [S]** per confronto con l'AN-TPS-43 (EWR 3D
statunitense a rotazione); il valore "noto fuori dalla ricerca" non si usa (come in DW-2). (3) Chain-Home, Mammut,
Type 093: (a) **restano senza valore** con il motivo scritto (illuminazione continua; schiera fissa senza cadenza e
senza analogo; sonar passivo in ascolto continuo); (b) valore dell'analogo piu' vicino anche se debole.

**Raccomandazione**: (1)(a), (2)(a), (3)(a).

**Esempio.** Freya (120 km) contro un bombardiere a 100 m/s: con 60 s la riduzione arriva a ~37 m dal bordo (corda
6 km); con 7,5 s a ~0,6 m. Nessuno scenario usa gli EWR della seconda guerra mondiale: nessun effetto sulla fotografia.

### DW9-9 — Registro dei dwell stimati: file e formato

**Domanda.** Dove si raccolgono le stime da aggiornare?
- (R1) **`Analysis/Document/Registro_Dwell_Stimati.md`** (contenuto iniziale in Appendice B: una riga per record [S]
  con valore, **banda di incertezza**, etichetta, base, che cosa serve per chiuderlo) **piu'** le costanti di `Test/Test_Dwell_Data.py` con il
  test di completezza del perimetro;
- (R2) solo il documento;
- (R3) costanti nei moduli dei registri.

**Raccomandazione: R1** (§3.3). Il documento lo crea l'esecutore nel blocco 1 copiando l'Appendice B (contenuto
deciso qui); gli aggiornamenti successivi li fa chi chiude una stima (ricerca nuova -> riga tolta o promossa a
FONTE, valore e test aggiornati).

**Esempio di riga**: `| 9K37-Buk | radar (ricerca 9S18) | 9.0 | 4.3-20 | FONTE NON VERIFICATA [S], valore centrale |
GlobalSecurity 9s18.htm (403), circolare 4,5-18 s; 3-14 giri/min radartutorial via ricerca | frase di fonte leggibile
(GlobalSecurity o Jane's) | 2026-11-17 |`.

---

## 5. Piano di intervento (per le raccomandazioni di §4)

Branch unico `ai/oc-dwell-dw9` (o di `des-developer`), **un commit per blocco**, verifica parziale per blocco,
suite e confronto completi solo alla fine (blocco 5). Se il codice reale non corrisponde (righe, nomi delle
variabili, esiti dei test), l'esecutore si ferma e riferisce. Righe lette al commit `412faa7b`: dopo il primo blocco
le righe dei registri scorrono; l'esecutore localizza i record per **nome della variabile** (colonna di §2).

### Blocco 0 — Sonda S-4 completa in tre passate (sessione principale, prima dei blocchi, nessun file del repository)

1. Copiare lo script dell'Appendice A in `Analysis/Document/Rapporti/Sonde_Dwell_D5/probe_dw9.py` (copia versionata,
   come S-1..S-3) e in `.ai-run/sonde_dwell/`.
2. Eseguire le **tre passate in sequenza**, mai in parallelo fra loro ne' con suite o confronto, dalla root del repo
   con l'interprete che `verifica.sh` stampa, in background:
   - **S-4/rec** (valori raccomandati di §2): `mkdir -p .ai-run/sonde_dwell/s4_rec && <python>
     .ai-run/sonde_dwell/probe_dw9.py rec all .ai-run/sonde_dwell/s4_rec > .ai-run/sonde_dwell/s4_rec/log.txt 2>&1`;
   - **S-4/min** (ogni sensore con banda all'**estremo minimo**, gli altri al valore raccomandato): stesso comando
     con `min` e cartella `s4_min`;
   - **S-4/max** (ogni sensore con banda all'**estremo massimo**): stesso comando con `max` e cartella `s4_max`.
   Ognuna dura quanto un confronto (~17-19 minuti su osboxes): **~55 minuti in tutto** (la sonda unica della prima
   versione era ~18 minuti).
3. Per ciascuna: `grep -E '^(compared|PROBE_RC)' <cartella>/log.txt` e le statistiche in fondo al log (letture del
   dwell per modello e valore, chiamate con `g < 1`).
4. **Esito atteso** di S-4/rec: `compared 1103 runs: IDENTICAL` (545 esecuzioni identiche con la prima versione dei
   valori, 507 identiche per costruzione; da guardare per prime S17, S20, VAL, ORC, §1.6). S-4/min e S-4/max: nessuna
   attesa numerica (gli estremi massimi arrivano a 20 s per Buk e Top Pair, 60 s per SPY-1 e i due EWR tedeschi).
5. **Criterio di lettura** (linea dell'utente): se le tre passate danno lo stesso esito, **la scelta del valore dentro
   l'intervallo e' irrilevante** per la fotografia, e lo si scrive nel rapporto e in `F4_Differenze_Scenari.md`; se
   gli esiti cambiano fra le passate, le esecuzioni cambiate e i numeri (quali, quanti valori, quale famiglia) **vanno
   all'utente** prima di procedere con i valori. Per leggere un'esecuzione cambiata: `<python> -m
   Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare
   Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --against <cartella>/capture.json --summary`;
   per attribuirla a una famiglia, le varianti S-5 (`probe_dw9.py <rec|min|max> sam_aaa ...`, `tvd_vista`, `navi`,
   `awacs`, `ewr`, eventualmente con `--only` sull'unita'). Un cambiamento con l'interruttore acceso **non blocca** i
   blocchi 1-5 (che con l'interruttore spento non cambiano nulla), ma va descritto nel rapporto.
6. Copiare `log.txt` e `stats.json` delle tre passate in `Rapporti/Sonde_Dwell_D5/s4_rec|s4_min|s4_max/` e aggiornare
   il `LEGGIMI.md` della cartella (righe S-4).
7. Dopo le decisioni DW9-1..DW9-9, se un valore o una banda cambia rispetto alla raccomandazione, aggiornare il
   dizionario `VALUES` dello script e rieseguire almeno S-4/rec.

### Formato comune dei commenti nei registri (tutti i blocchi)

Ogni valore ha **una riga di commento subito sopra la chiave**, nello stile dei 10 EWR (`Vehicle_Data.py:4687-4688`):

```
# dwell_time_s <valore>: <ETICHETTA> -- <testo della riga nelle tabelle dei blocchi>. Banda <min>-<max> s. Solo ricerca. D-5 DW-9.
```

La frase `Banda <min>-<max> s.` usa la colonna "Banda [s]" di §2 (con l'origine fra parentesi quando §2 la indica,
es. `Banda 1.0-4.0 s (analoghi Gepard, Osa, Pantsir).`); per i valori senza banda ("—") la frase si omette.
`<ETICHETTA>` e testo sono quelli delle tabelle seguenti, **parola per parola**; l'esecutore puo' solo andare a capo
per la larghezza di riga (le righe di commento continuano con `#` e due spazi). Nei dizionari che finiscono con
`'reliability': {...}` senza virgola, aggiungere la virgola. In `Aircraft_Data.py` la chiave e' `"dwell_time_s"`
(doppi apici, stile del file). Valori `float` con il punto (`18.0`, `1.82`).

### Blocco 1 — SAM e AAA con radar (9 record) + infrastruttura dei test e del registro

**File**: `Asset/Vehicle_Data.py`; `Test/Test_Dwell_Data.py` (nuovo); `Test/Test_Mobile.py`;
`Test/Test_Threat_AA_Factory.py`; `Analysis/Document/Registro_Dwell_Stimati.md` (nuovo, dall'Appendice B).

1.1 **Intestazione** in `Vehicle_Data.py`, subito prima di `# ===== ZSU-57-2 Sparka =====` (`:3700`), dopo le due
righe "Nuovi veicoli AAA ...":

```
# D-5, DW-9 rivista (Proposta_Dwell_Estensione_DW9.md): 'dwell_time_s' [s] nel sensore = periodo di rivisita della
# sola funzione di RICERCA (quella che da' 'acquisition_range'), anche quando 'model' nomina il radar di inseguimento
# (Fire Dome, Flap Lid): il motore lo legge solo con la portata di acquisizione, mai per inseguimento o tiro.
# Valore FISSO per sensore: non dipende da distanza, modo o carico del radar (rinvio dichiarato, Proposta §3.4).
# Intervalli di fonte: regime normale se citato, altrimenti valore centrale = media geometrica degli estremi del
# periodo, un decimale (scelta [S]); l'intervallo e' riportato come "Banda <min>-<max> s".
# Etichette: FONTE (giri/min di fonte, 60/giri al minuto D) | FONTE DEBOLE [S] | FONTE NON VERIFICATA [S] |
# STIMA PER CONFRONTO [S] con l'analogo nominato. Stime [S] e bande in Analysis/Document/Registro_Dwell_Stimati.md.
```

1.2 **Valori** (nel dizionario `radar`, dopo `'reliability'`):

| Variabile | Valore | Testo del commento dopo `# dwell_time_s <v>: ` |
|---|---|---|
| `ZSU_23_4_data` | `18.0` | `FONTE di variante, attribuzione STIMA [S] -- ricerca circolare 20 gradi/s del 1RL33M3 (manuale ZSU-23-4M; modo base = regime normale citato; accelerata 45-60 gradi/s e settore 30-100 gradi a 20 gradi/s danno 3-10 s) -> 360/20 (D); dato della variante M3 attribuito al 1RL33 base [S]. Conf. media.` (banda 3-18) |
| `Flakpanzer_Gepard_data` | `1.0` | `FONTE -- ricerca MPDR-12, 60 giri/min -> 60/60 (D). Conf. media-alta.` |
| `K2K22_Tunguska_data` | `1.82` | `STIMA PER CONFRONTO [S] -- ricerca 1RL144 (giri/min non trovati; 1A26 e' il calcolatore): analogo 9A33-Osa Land Roll, 33 giri/min -> 60/33 (D).` (banda 1.0-4.0, analoghi Gepard, Osa, Pantsir) |
| `A9A33_Osa_data` | `1.82` | `FONTE -- antenna di acquisizione Land Roll, 33 giri/min -> 60/33 = 1,818 (D, al centesimo). Conf. alta (due fonti secondarie).` |
| `MIM115_Roland_data` | `1.0` | `FONTE -- ricerca MPDR-16, 60 giri/min -> 60/60 (D). Conf. media-alta.` |
| `K9K331_Tor_data` | `1.7` | `FONTE, valore centrale, interpretazione [S] -- radar di scoperta 3D del Tor-M1: 'scanning interval 1 s' e intera zona di elevazione in 3 s (Air Power Australia), nessun regime normale da fonte leggibile -> centrale di 1-3 s (D); il 'modo principale 3 s' di GlobalSecurity NON e' verificato. Conf. media.` (banda 1-3) |
| `K2K12_Kub_data` | `3.5` | `FONTE, valore centrale -- antenna di ricerca 1S11 del 1S91, 15 o 20 giri/min = 4 o 3 s (nessun regime normale citato) -> centrale 3,46 (D). Conf. media.` (banda 3-4) |
| `K9K37_Buk_data` | `9.0` | `FONTE NON VERIFICATA [S], valore centrale -- ricerca 9S18 (non il 9S35 Fire Dome di inseguimento): giro circolare 4,5-18 s (GlobalSecurity, pagina non leggibile al controllo), nessun regime normale -> centrale 9,0 (D); 3-14 giri/min = 20-4,3 s dalla scheda 9S18M (via ricerca). Conf. bassa-media.` (banda 4.3-20) |
| `S300PS_data` | `12.0` | `STIMA PER CONFRONTO [S] -- ricerca 5N64S Big Bird-B (giri/min non trovati; il 30N6 Flap Lid e' il radar d'ingaggio): analogo 64N6/64N6E della stessa famiglia, una rotazione ogni 12 s in regime regolare (fonte non verificata).` (banda 5-12) |

Il testo fra apici e' il commento; la banda fra parentesi va scritta in coda al commento nella forma
`Banda <min>-<max> s.` (formato comune). Gepard, Osa e Roland non hanno banda.

1.3 **`Test/Test_Dwell_Data.py` (nuovo)**. Docstring di modulo che rimanda a questa Proposta e al registro. Logger del
modulo `Mobile` mockato come in `Test_Mobile.py` (`patch("Code.Dynamic_War_Manager.Source.Asset.Mobile.logger",
MagicMock())`). Import dei tre registri reali con percorso completo. Stub locale (nessuna classe base condivisa):

```python
class _DwellReader:
    """Lettori D-5 di Mobile su un modello del registro reale (nessun Mobile costruito)."""
    detection_dwell_time = Mobile.detection_dwell_time
    sensor_dwell_time = Mobile.sensor_dwell_time
    _detection_registry_record = Mobile._detection_registry_record
    _sensor_range_km = staticmethod(Mobile._sensor_range_km)
    _sensor_dwell_s = staticmethod(Mobile._sensor_dwell_s)

    def __init__(self, model):
        self._model = model
```

Costanti di modulo (nel blocco 1 solo la parte SAM/AAA; i blocchi successivi le estendono):

```python
# D-5, DW-9 rivista: periodo di rivisita [s] della funzione di ricerca, per (registro, modello, sensore).
SAM_AAA_DWELL_S = {
    'ZSU-23-4-Shilka': 18.0, 'Flakpanzer-Gepard': 1.0, '2K22-Tunguska': 1.82, '9A33-Osa': 1.82,
    'MIM-115-Roland': 1.0, '9K331-Tor': 1.7, '2K12-Kub': 3.5, '9K37-Buk': 9.0, 'S-300PS': 12.0,
}
# Modelli con valore STIMATO [S] (registro Analysis/Document/Registro_Dwell_Stimati.md).
DWELL_ESTIMATED = {'ZSU-23-4-Shilka', '2K22-Tunguska', '9K331-Tor', '9K37-Buk', 'S-300PS'}
```

Classe **`TestSamAaaDwell(unittest.TestCase)`** (2 test):
1. `test_radar_dwell_values`: per ogni modello di `SAM_AAA_DWELL_S` (`subTest`),
   `Vehicle_Data._registry[model].radar['dwell_time_s'] == valore`.
2. `test_the_dwell_is_read_with_the_acquisition_range`: per ogni modello, `_DwellReader(model).detection_dwell_time('air')
   == valore` (lettura di default, `range_type='acquisition_range'`, quella del motore) e
   `sensor_dwell_time('radar') == valore`; per il Buk inoltre
   `Vehicle_Data._registry['9K37-Buk'].radar['capabilities']['air'][1]['acquisition_range'] == 85` (la portata del
   9S18 a cui il dwell si riferisce). Logger di `Mobile` mockato nel `setUp`/`tearDown` della classe.

1.4 **`Test/Test_Mobile.py`**, `TestDetectionDwellTime.test_records_without_dwell_give_none` (`:1428-1433`): sostituire
la riga del `'9K331-Tor'` con `'Chain-Home'` (resta senza valore). La riga `'AN-FPS-117'` resta fino al blocco 3.
Il test `test_dwell_follows_the_sensor_of_detection_range` della stessa classe (`:1441-1460`) fissa gia' la regola
"il dwell segue il vincitore della portata" con uno stub a due sensori (vincente per portata, parita' = primo di
`DETECTION_SENSORS`, vincente senza dwell = None): **non** va duplicato ne' modificato; deve restare verde (§6
punto 5).

1.5 **`Test/Test_Threat_AA_Factory.py`**, classe `TestBuildDetectionThreat`:
- `test_sensor_without_dwell_gives_none` (`:497-502`): modello `'Chain-Home'` con `category='EWR'` al posto del Tor;
  docstring: "D-5: un sensore che non dichiara `dwell_time_s` (Chain-Home: illuminazione continua) da' una minaccia
  senza dwell." Se `build_detection_threat` restituisse None per quel record (es. per l'altezza d'antenna), usare
  `'Mammut'` e riferirlo.
- test nuovo `test_sam_detection_threat_carries_the_search_dwell`: `_AssetStub(model='9K331-Tor',
  category=gat.SAM_SMALL.value)` a quota 1000 m -> `threat.sensor == 'radar'` e `threat.dwell_time_s == 1.7`.

1.6 **`Analysis/Document/Registro_Dwell_Stimati.md`**: creato copiando l'Appendice B **cosi' com'e'** (tutte le righe,
anche quelle dei blocchi successivi: e' il registro delle decisioni, non dello stato del codice) con la data del
commit.

1.7 **Verifica parziale del blocco 1** (singoli file, dalla root): `Test_Dwell_Data`, `Test_Mobile`,
`Test_Threat_AA_Factory`, `Test_Vehicle_Data`, `Test_Military`, `Test_Weapon_Delivery` -> tutti OK. Test nuovi: **3**.

### Blocco 2 — SAM con TVD e AAA a vista (6 record)

**File**: `Asset/Vehicle_Data.py`; `Test/Test_Dwell_Data.py`.

2.1 **Valori** `3.2` nei dizionari `TVD` di `Strela1_9P31_data`, `MIM72G_Chaparral_data`, `K9K35_Strela10_data`,
`M6_Linebacker_data` (dopo `'reliability'`) e `visual` di `ZSU_57_2_data`, `M163_VADS_data` (dopo `'capabilities'`).
Commento (identico per i sei, salvo la parentesi):

```
# dwell_time_s 3.2: STIMA PER CONFRONTO [S], valore centrale -- ricerca a vista del servente (<parentesi>): Poe 1974
#   (ADA017599, tab. 2), passata completa del settore da osservatori a terra 1,75-6,00 s (medie 2,72 / 2,99 / 3,94 s
#   per 30 / 60 / 120 gradi), nessun regime normale -> centrale 3,24 (D). Banda 1.75-6.0 s. APPROSSIMAZIONE: la
#   vista non ha un periodo di rivisita (probabilita' cumulata a ogni colpo d'occhio, Koopman); da rivedere con una
#   legge cumulativa. Solo ricerca. D-5 DW-9.
```

| Variabile | `<parentesi>` |
|---|---|
| `Strela1_9P31_data` | `il mirino ottico serve dopo la scoperta` |
| `MIM72G_Chaparral_data` | `il FLIR serve dopo la scoperta` |
| `K9K35_Strela10_data` | `il mirino ottico-IR serve dopo la scoperta; il telemetro 9S86 non scopre` |
| `M6_Linebacker_data` | `il FLIR serve dopo la scoperta; il cueing radar esterno non e' modellato` |
| `ZSU_57_2_data` | `equipaggio a torretta aperta` |
| `M163_VADS_data` | `puntatore; l'AN/VPS-2 misura solo la distanza` |

2.2 **`Test_Dwell_Data.py`**: costante `VISUAL_DWELL_S = 3.2` con commento "[S] Poe 1974, centrale della banda
1,75-6,0 s; APPROSSIMAZIONE (DW9-6)"; `TVD_MODELS = ('Strela-1-9P31', 'MIM-72G-Chaparral', '9K35-Strela-10', 'M6-Linebacker')`,
`VISUAL_MODELS = ('ZSU-57-2', 'M163-VADS')`; tutti e sei in `DWELL_ESTIMATED`. Classe **`TestVisualAndTvdDwell`**
(2 test):
1. `test_tvd_and_visual_values`: `record.TVD['dwell_time_s']` (TVD_MODELS) e `record.visual['dwell_time_s']`
   (VISUAL_MODELS) uguali a `VISUAL_DWELL_S`; nessuno dei sei ha `dwell_time_s` nel `radar` (che e' False).
2. `test_visual_dwell_follows_the_visual_switch`: `_DwellReader('ZSU-57-2').detection_dwell_time('air') == 3.2`; con
   `patch.object(<modulo Mobile>, 'D4C_VISUAL_SENSOR', False)` -> None (il visivo escluso non da' portata ne' dwell).

2.3 **Verifica parziale**: `Test_Dwell_Data`, `Test_Vehicle_Data`, `Test_Mobile`, `Test_Session_Scenarios_S32`
(S32 `ewr_on` legge ora il dwell della ZSU dal registro: `g = 1`, test invariati; sonda S-4a identica),
`Test_Session_Scenarios_S33`, `Test_Session_Scenarios_S31`. Test nuovi: **2**.

### Blocco 3 — EWR rimasti (3 record) e motivi dei 2 senza valore

**File**: `Asset/Vehicle_Data.py`; `Test/Test_EWR_Data.py`; `Test/Test_Mobile.py`.

3.1 **Valori** nel `radar` (dopo l'ultima chiave esistente del dizionario):

| Variabile | Valore | Testo del commento |
|---|---|---|
| `FuMG80_Freya_data` | `60.0` | `STIMA PER CONFRONTO [S] -- schiera orientabile, velocita' non data: analogo SCR-270 (EWR a rotazione del 1940, 1 giro/min). Banda 7.5-60 s (analoghi AMES Type 7 e SCR-270).` |
| `Wassermann_data` | `60.0` | `STIMA PER CONFRONTO [S] -- traliccio ruotabile, velocita' non data: analogo SCR-270 (EWR a rotazione del 1940, 1 giro/min). Banda 7.5-60 s (analoghi AMES Type 7 e SCR-270).` |
| `AN_FPS117_data` | `10.0` | `STIMA PER CONFRONTO [S] -- rotazione non riportata dalla ricerca (il valore noto fuori ricerca non si usa): analogo AN-TPS-43 (EWR 3D statunitense, 6 giri/min).` |

In `Mammut_data`, nel `radar`, solo il commento: `# nessun dwell_time_s: schiera fissa a scansione elettronica su
100 gradi, cadenza non data, nessun analogo credibile (Chain-Home, l'altro radar fisso, non ha periodo). D-5 DW-9.`
Chain-Home: commento esistente invariato.

3.2 **`Test/Test_EWR_Data.py`** (`:468-490`): `EWR_DWELL_S` con i 3 valori in piu' e commento aggiornato ("... ;
Freya e Wassermann 60 e AN-FPS-117 10: stime per confronto [S], DW-9 rivista"); `EWR_WITHOUT_DWELL = ('Chain-Home',
'Mammut')` con commento "illuminazione continua; schiera fissa senza cadenza ne' analogo". Docstring della classe:
"... dei 13 EWR con un valore".

3.3 **`Test/Test_Mobile.py`** (`:1431`): `'AN-FPS-117'` -> `'Mammut'`.

3.4 **`Test_Dwell_Data.py`**: `'FuMG-80-Freya'`, `'Wassermann'`, `'AN-FPS-117'` in `DWELL_ESTIMATED`.

3.5 **Verifica parziale**: `Test_EWR_Data`, `Test_Mobile`, `Test_Dwell_Data`. Test nuovi: **0** (solo `subTest` in
piu').

### Blocco 4 — Navi (22 record con valore, 1 senza)

**File**: `Asset/Ship_Data.py`; `Test/Test_Dwell_Data.py`.

4.1 **Intestazione** nel commento "DATI NAVI" (`Ship_Data.py:461-466`), dopo la riga `# Categoria ...`:

```
# dwell_time_s (D-5, DW-9 rivista, Proposta_Dwell_Estensione_DW9.md) -> periodo di rivisita [s] della ricerca AEREA
#   del record (un solo valore per il dizionario 'radar': per i bersagli navali, lenti, la permanenza supera sempre il
#   periodo). Etichette e stime [S] come in Vehicle_Data; registro in Analysis/Document/Registro_Dwell_Stimati.md.
```

4.2 **Valori** nel `radar`, dopo `'reliability'`, allineati allo stile del file (`'dwell_time_s': 5.0,`); qui la
frase della banda e' gia' dentro il testo del commento:

| Variabile | Valore | Testo del commento |
|---|---|---|
| `CVN70_data` .. `CVN75_data` (6) | `5.0` | `FONTE -- ricerca aerea AN/SPS-49: 6 giri/min lunga portata, 12 corta, default 12 sull'A(V)1 (regime normale citato) -> 60/12 (D). Banda 5-10 s. Conf. alta.` |
| `CV59_data` | `5.0` | `STIMA PER CONFRONTO [S] -- AN/SPS-43 (giri/min non trovati): analogo AN/SPS-49, successore nella ricerca aerea 2D US Navy. Banda 5-10 s.` |
| `KuznetsovAdmiral_data` | `7.1` | `FONTE, valore centrale -- ricerca 3D Fregat-MA (MR-750), 12 o 6 giri/min = 5 o 10 s, nessun regime normale -> centrale 7,07 (D); Sky Watch (schiera fissa) senza dato. Banda 5-10 s. Conf. media.` |
| `ArleighBurke_data` | `5.0` | `FONTE DEBOLE [S] -- AN/SPY-1 (schiera fissa): '1 (orizzonte), 12 (sopra l'orizzonte) scan/min' (infobox, significato non definito), per bersagli aerei la ricerca sopra l'orizzonte -> 60/12 (D). Banda 5-60 s. Conf. bassa.` |
| `Type052B_data` | `7.1` | `STIMA PER CONFRONTO [S] -- Type 381 (giri/min non trovati): analogo Fregat-MA (valore centrale), radar 3D navale rotante della stessa epoca. Banda 5-10 s.` |
| `Type052C_data` | `5.0` | `STIMA PER CONFRONTO [S] -- Type 346 (AESA fissa, periodo non trovato): analogo AN/SPY-1, schiera fissa a fasci elettronici. Banda 5-60 s.` |
| `CG65_data` | `5.0` | `FONTE DEBOLE [S] -- AN/SPY-1A (schiera fissa): '1 (orizzonte), 12 (sopra l'orizzonte) scan/min' (infobox, significato non definito), per bersagli aerei la ricerca sopra l'orizzonte -> 60/12 (D). Banda 5-60 s. Conf. bassa.` |
| `PiotrVelikiy_data` | `7.1` | `FONTE, valore centrale -- Fregat-MA 12 o 6 giri/min, nessun regime normale -> centrale 7,07 (D); Top Pair 3-12 giri/min. Banda 5-20 s (i due radar). Conf. media.` |
| `Moskva_data` | `10.0` | `FONTE, valore centrale -- MR-800 Top Pair, 3-12 giri/min = 20-5 s, nessun regime normale -> centrale 10,0 (D). Banda 5-20 s. Conf. media.` |
| `FFG46_data` | `5.0` | `FONTE -- ricerca aerea AN/SPS-49: default 12 giri/min (regime normale citato) -> 60/12 (D). Banda 5-10 s. Conf. alta.` |
| `FF1135M_data` | `7.1` | `STIMA PER CONFRONTO [S] -- Head Net-C (giri/min non trovati): analogo Head Net-A (MR-310), 6 o 12 giri/min, valore centrale; la -C e' la versione a due facce della -A. Banda 5-10 s.` |
| `FFG11540_data` | `7.1` | `FONTE, valore centrale -- Fregat-MA, 12 o 6 giri/min, nessun regime normale -> centrale 7,07 (D); Mineral-ME e' un radar di tiro. Banda 5-10 s. Conf. media.` |
| `Type054A_data` | `2.0` | `FONTE DEBOLE [S] -- Type 382, circa 30 giri/min (forum) -> 60/30 (D); alternativa per confronto con il Fregat MAE-3: 7,1 s. Banda 2-10 s. Conf. bassa.` |
| `FFL1124_data` | `7.1` | `STIMA PER CONFRONTO [S] -- MR-302 Strut Curve (rotazione non data): analogo Head Net-A (MR-310, valore centrale), ricerca aerea navale sovietica coeva. Banda 5-10 s.` |
| `FSG1241_data` | `7.1` | `STIMA PER CONFRONTO [S] -- Band Stand e' un radar di tiro, nessun radar di ricerca nel record: la portata di acquisizione rappresenta la ricerca della corvetta; analogo Head Net-A (MR-310, valore centrale). Banda 5-10 s.` |
| `LHA1_data` | `5.0` | `STIMA PER CONFRONTO [S] -- AN/SPS-52 (giri/min non trovati): analogo AN/SPS-49, ricerca aerea US Navy coeva. Banda 5-10 s.` |
| `Type071_data` | `2.0` | `FONTE -- ricerca aerea Type 364, 30 giri/min -> 60/30 (D); Type 360 senza dato. Conf. media.` |

`Type093_data`: solo il commento `# nessun dwell_time_s: sonar passivo in ascolto continuo, nessuna scansione. D-5 DW-9.`

4.3 **`Test_Dwell_Data.py`**: costante `SHIP_DWELL_S` (i 22 valori della tabella, chiavi = `model` del registro:
`'CVN-70 Carl Vinson'`, ..., `'Type 071'`), `NO_DWELL['Type 093'] = 'sonar passivo'`; in `DWELL_ESTIMATED` i 10
modelli [S] (`'CV-59 USS Forrestal'`, `'USS Arleigh Burke IIa'`, `'Type 052B Guangzhou-class'`, `'Type 052C'`,
`'CG-65'`, `'FF 1135M Rezky'`, `'Type 054A'`, `'FFL 1124.4 Grisha'`, `'FSG 1241.1MP Molniya'`, `'LHA-1 Tarawa'`).
Classe **`TestShipDwell`** (2 test):
1. `test_ship_radar_dwell_values`: `Ship_Data._registry[model].radar['dwell_time_s']` per i 22 (`subTest`).
2. `test_submarine_has_no_dwell`: `'dwell_time_s' not in Ship_Data._registry['Type 093'].radar`.

4.4 **Verifica parziale**: `Test_Dwell_Data`, `Test_Ship_Data`, `Test_Ship`, `Test_Threat_AA_Factory` (la minaccia
della CVN porta ora 5,0 s; `test_ship_uses_mast_height` non lo legge). Test nuovi: **2**.

### Blocco 5 — AWACS, test di completezza, testi del codice, suite e confronto

**File**: `Asset/Aircraft_Data.py`; `Test/Test_Dwell_Data.py`; `Logic/Engagement_Resolver.py` (solo docstring);
`Asset/Mobile.py` (solo docstring); `Test/Scenario_Baseline.py` (solo docstring).

5.1 **Valori** `10.0` nel `"radar"` di `e3a_data`, `e2d_data`, `a50_data`, dopo `"reliability"` (e dopo `"type"` dove
c'e'):

| Variabile | Testo del commento |
|---|---|
| `e3a_data` | `FONTE -- rotodome AN/APY-2, 6 giri/min -> 60/6 (D). Conf. alta.` |
| `e2d_data` | `FONTE -- rotodome AN/APY-9, 6 giri/min (rotazione meccanica; settori elettronici in aggiunta) -> 60/6 (D). Conf. media.` |
| `a50_data` | `FONTE DEBOLE [S] -- rotodome Shmel, 'circa sei giri al minuto' (fonte divulgativa unica) -> 60/6 (D); coincide con l'analogo E-3A. Conf. bassa.` |

Sopra `e2d_data` (`# ==================== US AWACS & RECON ====================`, `:2095`) una riga:
`# dwell_time_s (D-5, DW-9 rivista): solo gli AWACS; gli altri aerei NON lo dichiarano (decisione dell'utente).`

5.2 **`Test_Dwell_Data.py`**: `AWACS_DWELL_S = {'E-3A Sentry': 10.0, 'E-2D Advanced Hawkeye': 10.0, 'A-50': 10.0}`,
`'A-50'` in `DWELL_ESTIMATED`; `NO_DWELL = {'Chain-Home': 'illuminazione continua', 'Mammut': 'schiera fissa senza
cadenza ne' analogo', 'Type 093': 'sonar passivo'}` (completo). Classe **`TestDwellScope`** (3 test):
1. `test_awacs_dwell_values`: i 3 valori nel `radar`.
2. `test_non_awacs_aircraft_declare_no_dwell`: per ogni record di `Aircraft_Data._registry` che non e' in
   `AWACS_DWELL_S`, nessun dizionario fra `radar`, `TVD` (se dizionari) contiene `dwell_time_s` (decisione 1
   dell'utente).
3. `test_every_sensor_in_scope_has_a_value_or_a_reason`: insieme del perimetro = record di `Vehicle_Data` con almeno
   un sensore dizionario (`radar`, `TVD`, `visual`) + tutti i record di `Ship_Data` + `AWACS_DWELL_S`; ognuno sta in
   **esattamente uno** fra "ha `dwell_time_s` in un sensore" e `NO_DWELL`; `DWELL_ESTIMATED` e' contenuto
   nell'insieme dei modelli con valore; i valori del registro coincidono con l'unione di `SAM_AAA_DWELL_S`,
   `VISUAL_DWELL_S` (TVD e vista), `SHIP_DWELL_S`, `AWACS_DWELL_S` e di `EWR_DWELL_S` importato da
   `Test_EWR_Data` (import con percorso completo). Il messaggio d'errore elenca i modelli fuori regola.

5.3 **Testi del codice** (nessuna istruzione cambia):
- `Logic/Engagement_Resolver.py:172-173` (docstring "Permanenza nel volume"): "oggi solo nei 10 radar EWR" ->
  "valorizzata per EWR, SAM, AAA, TVD, vista, navi e AWACS, mai per gli altri aerei (DW-9 rivista,
  Proposta_Dwell_Estensione_DW9.md); e' il periodo della sola funzione di ricerca". Nella voce **Limiti** (`:195-196`)
  aggiungere: "vista e TVD: valore stimato con L1, APPROSSIMAZIONE da rivedere con una legge cumulativa".
- `Asset/Mobile.py:1692-1702` (docstring di `detection_dwell_time`): una frase "Il dwell e' quello della funzione di
  RICERCA del sensore (DW-9 rivista): si legge con la portata di acquisizione, non entra nell'inseguimento".
- `Test/Scenario_Baseline.py` (sezione "Permanenza nel volume dopo la D-5", `:176-180`): una frase in coda "I valori
  della DW-9 rivista (SAM, AAA, TVD, vista, navi, AWACS) non cambiano nessuna esecuzione: interruttore spento; S32
  `ewr_on` (acceso) legge il dwell visivo della ZSU-57-2 con permanenze di oltre 60 s (`g = 1`)."

5.4 **Verifica finale** (con `tools/ai/verifica.sh`, mai in parallelo): suite, poi confronto. Test nuovi: **3**.

### 5.5 Riepilogo dei test

| Blocco | File | Test nuovi | Test modificati |
|---|---|---|---|
| 1 | `Test_Dwell_Data.py` (nuovo), `Test_Threat_AA_Factory.py`, `Test_Mobile.py` | 2 + 1 = **3** | 2 (`test_records_without_dwell_give_none`, `test_sensor_without_dwell_gives_none`) |
| 2 | `Test_Dwell_Data.py` | **2** | — |
| 3 | `Test_EWR_Data.py`, `Test_Mobile.py`, `Test_Dwell_Data.py` | **0** | 3 (costanti `EWR_DWELL_S`, `EWR_WITHOUT_DWELL`; riga FPS-117) |
| 4 | `Test_Dwell_Data.py` | **2** | — |
| 5 | `Test_Dwell_Data.py` | **3** | — |
| Totale | | **10** | |

Suite attesa alla fine: **`Ran 4924 tests`, `OK (skipped=7)`**, sulla base dell'ultima suite valida letta in
`.ai-run/suite.log` (osboxes, 2026-11-13 08:53): `Ran 4914 tests`, `OK (skipped=7)`. **La base va riletta prima di
iniziare** (i commit successivi, `dad7c66f` e `412faa7b`, toccano solo testi e memoria [V: messaggi di commit], ma la
suite non e' stata rieseguita).

### 5.6 Vincoli

- **RNG**: nessuna estrazione nuova ne' spostata; nessuna riga del motore cambia. Con l'interruttore acceso il dwell
  influisce, come gia' previsto da FP-10, sull'unione dei passaggi e quindi sul numero di estrazioni dello stream
  `pass_rng` (comportamento esistente, non nuovo). Vietato il modulo `random`.
- **Interruttore**: `Engagement_Resolver.D5_DWELL_TIME = False`, invariato; nessun interruttore nuovo (§3.2).
- **Nomi stabili**: nessuna unita', variante o asset nuovo in `Test/Scenario_Baseline.py`; nessun nome esistente
  cambia. Le chiavi del registro sono quelle esistenti (`'ZSU-23-4-Shilka'`, `'CVN-70 Carl Vinson'`, `'A-50'`, ...).
- **Costanti**: nessuna costante del motore. I valori sono dati del registro con etichetta: 18 FONTE, 25 [S]
  dichiarate nel commento e nel registro dei dwell stimati (§2.6). `VISUAL_DWELL_S` in test replica il dato.
- **Core indifferente al simulatore**: dati nei registri del core, nessun import dall'adapter DCS.
- **Import** con il percorso completo; nessuna classe base condivisa nuova nei test; logger mockato come negli altri
  `Test_*.py`.
- **Il perimetro e' quello della decisione 1**: nessun `dwell_time_s` negli aerei non AWACS, nemmeno nei loro TVD
  (lo verifica `TestDwellScope.test_non_awacs_aircraft_declare_no_dwell`).

### 5.7 Esito atteso del confronto con la fotografia (`Test/baseline/scenario_baseline.json`, 1103 esecuzioni)

**Con l'interruttore spento (stato del repository dopo i blocchi): 1103 identiche, 0 cambiate, 0 nuove.**
- Le esecuzioni che non accendono la D-5: `Session_Simulator` non passa `dwell_time_for`, la chiamata al risolutore e'
  letteralmente quella di prima (`Session_Simulator.py:2792-2794`).
- Le esecuzioni che accendono la D-5 dentro il test:
  - S33-PASSES (10): la ZSU-57-2 ha il dwell **dichiarato** 2 s (`declare_dwell`, che scavalca il registro per il
    modo 'air'); gli altri osservatori (BMP-2 con sensore dichiarato, A-10C) non hanno dwell di registro -> identiche.
  - S32-DWELL `long` e `short` (8): ZSU dichiarata (30 s, 600 s); gli altri osservatori come sopra -> identiche.
  - S32-DWELL `ewr_on` (4): la ZSU-57-2 legge ora **3,2 s dal registro** (prima None); le sue permanenze sono di
    62,7-66,7 s (sonda S-3), quindi `g = 1`. La sonda S-4a, eseguita con 3,94 s, da' `compared 20 runs: IDENTICAL`
    [V]; con un dwell minore (3,2 s, o 2 s di DW9-6 c) le unioni di passaggi possono solo diminuire e `g` resta 1,
    quindi l'esito e' lo stesso [deduzione]; con l'estremo 6,0 s `g` resta 1 (permanenze oltre 60 s) e le unioni
    richiederebbero uscite di 6 s fra due passaggi, che in S32 (un solo sorvolo) non ci sono [I, da confermare con
    S-4/max]. Anche il test `test_ewr_source_dwell_changes_nothing_at_medium_altitude` resta valido (confronta solo
    munizioni e Detection del P-18).
- **Una sola esecuzione cambiata e' un errore** (valore nel sensore sbagliato, o un dato finito per sbaglio in un
  aereo non AWACS): l'esecutore si ferma e riferisce.

**Con l'interruttore acceso (non e' lo stato del repository; solo sonda S-4)**: per S-4/rec atteso `IDENTICAL` sulle
1103 per quanto provato con la prima versione dei valori (545 esecuzioni identiche e 507 identiche per costruzione; 51
da provare, §1.6); per S-4/min e S-4/max nessuna attesa numerica. Qualunque cambiamento va letto e attribuito con il
criterio del blocco 0 (punto 5) prima di proporre l'accensione, che resta una decisione separata dell'utente.

### 5.8 Documenti da aggiornare (dopo la verifica, non dall'esecutore salvo il registro)

- **`Registro_Dwell_Stimati.md`** (nuovo, blocco 1, dall'Appendice B).
- **Manuale DES** (`des-manual-writer`): cap. 4 §4.36 (`05_Strato2_Risolutore_Ingaggio.md:2967`, paragrafo "Il
  dato": famiglie valorizzate, regola "solo ricerca", nota di approssimazione per vista e TVD, rimando al registro);
  `10_Limiti_Estensioni_Divergenze.md:381` (voce "Dwell dichiarato solo per 10 radar EWR; DW-9 aperto" sostituita:
  DW-9 rivista, 43 valori di cui 25 stime, 3 senza valore, aerei non AWACS esclusi; valore fisso per sensore con
  banda di incertezza; vista/TVD approssimazione; esito delle tre passate S-4; **rinvio dichiarato** del "dwell
  dipendente da distanza, modo e carico del radar", da fare insieme all'orizzonte radar nel DES e a una legge
  cumulativa (Koopman/esponenziale), con i quattro motivi di §3.4 e il riferimento qualitativo `Dinamica dei Tempi di
  Aggiornamento Radar - Google Gemini.md`, che non contiene numeri utilizzabili); `09_Validazione.md` §8.14 (S32 `ewr_on` legge ora il dwell visivo della ZSU dal registro); atlante
  `11a_Atlante_Risolutore.md` se elenca i record con dwell.
- **`F4_Differenze_Scenari.md`**: sezione "D-5, DW-9 rivista (2026-11-xx)": nessuna esecuzione cambiata con
  l'interruttore spento; esito delle tre passate della sonda S-4 con l'interruttore acceso (e la frase del criterio:
  scelta dentro l'intervallo irrilevante, oppure i numeri); famiglie e conteggi (18 FONTE, 25 [S]).
- **`Piano_Implementazione_Missione.md`**: nella riga "D-5 (Pd con permanenza)" di §5, stato "valori estesi (DW-9
  rivista)", interruttore ancora spento.
- **`Rapporti/Sonde_Dwell_D5/LEGGIMI.md`**: riga S-4 (sessione principale, blocco 0).
- **`Proposta_Dwell_Time_Rilevamento.md`**: NON si modifica (contratto dei blocchi A e B); se serve, una nota della
  sessione principale in testa che rimanda a questo documento.

### 5.9 Esecutore consigliato

| Blocco | Esecutore | Motivo |
|---|---|---|
| 0 (sonda S-4) | sessione principale | sonda di sola lettura, lettura del confronto; gli agenti oc non hanno i permessi per il confronto parziale |
| 1 | `oc-developer` (alternativa `des-developer`) | dati e commenti testuali dati parola per parola; l'unica parte nuova e' lo scheletro di `Test_Dwell_Data.py`, descritto per intero |
| 2, 3, 4 | `oc-developer` | solo dati e costanti di test, nessuna logica |
| 5 | `oc-developer` (alternativa `des-developer` se il blocco 1 ha avuto intoppi) | test di completezza con un minimo di logica sugli insiemi; docstring; suite e confronto completi |

Un solo branch, blocchi in sequenza con verifica parziale fra uno e l'altro (memoria del progetto: blocchi piccoli,
suite e confronto completi solo alla fine).

---

## 6. Rischi e limiti

1. **La legge non accorcia le rotte e cambia pochissimo gli esiti** (rischio principale, invariato): con periodi di
   1-18 s (60 s solo per i due EWR tedeschi; bande fino a 20 s, e 60 s per SPY-1) la Pd si riduce solo per contatti
   radenti (§1.7). Per SAM e AAA, che
   sono tiratori, ogni rilevamento perso puo' cambiare un tiro, ma servono passaggi di pochi secondi nel volume; nelle
   545 esecuzioni provate nessuna cambia. Il volo basso "non visto" richiede l'orizzonte radar nel DES (attivita'
   separata, DW-7).
2. **25 valori su 43 sono stime [S]**, alcune deboli: Buk e S-300PS poggiano su una pagina non leggibile; il Tor su
   un'interpretazione; la Shilka su una variante successiva (M3); SPY-1 e Type 382 su fonti di confidenza bassa; i
   radar navali senza dato su analoghi. Il registro dei dwell stimati (DW9-9) e' il punto di raccolta per chiuderle.
3. **Vista e TVD con L1 sono un'approssimazione dichiarata**: la scoperta a vista e' cumulativa (Koopman; Poe 1974: un
   colpo d'occhio ogni ~0,33 s, probabilita' che cresce col tempo); L1 con 3,2 s riduce la Pd solo sotto i 3,2 s di
   permanenza e non la fa crescere oltre `Pd(d)` per permanenze lunghe. Da rivedere con una legge cumulativa.
10. **Rinvio dichiarato: dwell dipendente da distanza, modo e carico del radar** (linea dell'utente, §3.4). Il valore
    e' fisso per sensore; l'adattivita' dei radar a scansione elettronica (priorita' dei bersagli, ricerca/inseguimento,
    settore/360 gradi, integrazione degli impulsi a distanza, clutter e disturbo: riferimento qualitativo `Dinamica dei
    Tempi di Aggiornamento Radar - Google Gemini.md`, senza numeri utilizzabili) non e' modellata. Da riprendere
    insieme all'orizzonte radar nel DES e a una legge cumulativa (Koopman/esponenziale), non prima: la distanza e' gia'
    in `Pd(d)` e il motore non ha stato di modo del radar.
11. **Valore fisso dentro una banda**: per Buk (4,3-20 s), Top Pair e Piotr Velikiy (5-20 s), SPY-1 (5-60 s), Shilka
    (3-18 s) la banda e' larga; l'effetto della scelta e' misurato dalle passate S-4/min e S-4/max (blocco 0). Un esito
    diverso fra le passate torna all'utente.
12. **Due regole per gli intervalli nello stesso registro**: i 10 EWR del contratto precedente hanno la rotazione piu'
    veloce (DW-2), i record nuovi il valore centrale (§3.5). Per P-37, 1L13, P-14 e AMES Type 7 i valori centrali
    sarebbero 14,1 / 14,1 / 17,3 / 30 s invece di 10 / 10 / 10 / 7,5. Questo piano non li tocca (fuori dalla linea
    dell'utente); il riallineamento, se voluto, e' un intervento separato da decidere (nessuno scenario usa gli EWR).
4. **Un dwell per sensore, non per modo**: le navi con radar aria/mare diversi usano il valore della ricerca aerea
   anche in mare (nessun effetto: bersagli lenti, §1.3).
5. **Un sensore per asset; portata e dwell dallo stesso sensore solo con `acquisition_range`** [V]. Nel DES
   `Mobile.detection_range` (`Asset/Mobile.py:1592-1674`) prende la portata MASSIMA fra i sensori;
   `Mobile.detection_dwell_time` (`:1692-1735`) ripete lo stesso confronto (stesso `_sensor_range_km`, stessa
   esclusione del visivo con `D4C_VISUAL_SENSOR`, a parita' il primo di `DETECTION_SENSORS`, confronto stretto `>`)
   e restituisce il dwell del vincente; il modo del bersaglio e' ricavato con la stessa logica nello scheduler
   (`mutual_detection_ranges`, `Logic/Contact_Scheduler.py:1056`) e nel risolutore (`_dwell_of`,
   `Engagement_Resolver.py:2494-2503`, con `GROUNDED_DETECTION_MODE`). Quindi, con il default, portata della finestra
   e dwell vengono dallo stesso sensore per costruzione. Due casi residui:
   - **`range_type` diverso**: `registry_dwell_time` (`Engagement_Resolver.py:1303-1318`) chiama `reader(mode)`, cioe'
     sempre con `range_type='acquisition_range'`, mentre lo scheduler puo' costruire le finestre su
     `engagement_range` (parametro `range_type` di `Session_Simulator`, `Logic/Session_Simulator.py:2194`). In un
     asset con due sensori i cui vincenti differiscono fra i due `range_type`, la finestra sarebbe del sensore X e il
     dwell del sensore Y. Oggi non scatta: nessun veicolo del registro ha due sensori dizionario (§1.4) e nessun
     chiamante di produzione passa `engagement_range` o `tracking_range` [V: ricerca testuale in `Source/`, fuori
     dai test; le sessioni con un `range_type` passato a runtime non sono verificabili con una ricerca].
   - **Vincente senza dwell**: se il sensore con la portata maggiore non dichiara `dwell_time_s`, il dwell e' None
     anche se un sensore piu' corto ne dichiara uno: la D-5 non si applica a quella coppia.
   **Rinvio**: passare il `range_type` al lettore (`dwell_time_for(observer, target, mode, range_type)`) quando qualcuno
   usera' finestre "a tiro" con sensori multipli; richiede che il risolutore sappia con quale `range_type` e' stata
   costruita la finestra (oggi `ContactWindow` non lo porta). Nessuna modifica in questo piano.
   **Pianificatore** [V: `Logic/Air_Route_Manager.py:740-805`]: `build_detection_threat` e' coerente al suo interno
   ma con una regola diversa dal DES: sceglie il sensore con il raggio **effettivo** maggiore (`min(acquisition_range,
   orizzonte)` per sensore, modo sempre 'air', `range_type` sempre di default; a parita' il primo di `('radar', 'TVD',
   'visual')`, confronto stretto `>`) e prende `asset.sensor_dwell_time(sensor)` di **quel** sensore, quindi raggio
   del cilindro e dwell della `DetectionThreat` vengono dallo stesso sensore. Rispetto al DES (portata **nominale**
   massima) puo' scegliere un sensore diverso solo se l'orizzonte taglia il sensore piu' lungo sotto il piu' corto:
   limite gia' dichiarato nel docstring (`:750-752`) e nella Proposta precedente §5.2; oggi impossibile per i veicoli
   (un solo sensore dizionario ciascuno).
   La regola "il dwell segue il vincitore della portata, a parita' il primo di `DETECTION_SENSORS`, None se il
   vincente non lo dichiara" e' gia' fissata da `Test_Mobile.TestDetectionDwellTime.test_dwell_follows_the_sensor_of_detection_range`
   (`Test/Test_Mobile.py:1441-1460`: stub a due sensori, vincente per portata, parita', vincente senza dwell): il
   piano non aggiunge un test duplicato (blocco 1, punto 1.4).
6. **Fixture**: `declare_sensor` cambia la portata di un'istanza ma non il dwell, che resta quello del registro; uno
   scenario futuro che dichiari un sensore diverso su un SAM con dwell leggerebbe il dwell del registro.
7. **`range_type` diverso dall'acquisizione**: se un chiamante costruisse le finestre su `engagement_range`, il dwell
   resterebbe quello della ricerca (nessun chiamante lo fa oggi [V]); con due sensori anche di un altro sensore
   (punto 5).
8. **Test che dipendono dal "senza dwell"**: i 3 test che usavano Tor e AN-FPS-117 come esempi senza valore cambiano
   nei blocchi 1 e 3 (atteso). `TestDwellScope` rendera' rosso ogni record nuovo del perimetro aggiunto senza valore
   o motivo: e' il segnale voluto.
9. **Le sonde provano i valori in memoria**, non il codice scritto: se l'esecutore mettesse un valore nel sensore
   sbagliato (es. nel `radar` di un mezzo che vede con il `visual`), il confronto con l'interruttore spento non lo
   vedrebbe; lo vedono `Test_Dwell_Data` (blocchi 1-5) e la S-4 rieseguita dopo il merge con il codice reale.

---

## Appendice A — Script della sonda S-4 (`probe_dw9.py`)

Da copiare in `Analysis/Document/Rapporti/Sonde_Dwell_D5/probe_dw9.py` e in `.ai-run/sonde_dwell/` (blocco 0). Stessa
struttura dello script usato per le sonde parziali di §1.6 (che pero' aveva la prima versione dei valori e una sola
passata). Uso: `<python> probe_dw9.py <rec|min|max> <famiglie> <cartella_uscita> [regex --only]`, con `rec` = valori
raccomandati di §2, `min`/`max` = ogni sensore con banda al suo estremo (gli altri al valore raccomandato), e
`<famiglie>` = `all` oppure un elenco separato da virgole fra `sam_aaa`, `tvd_vista`, `ewr`, `navi`, `awacs`. Se una
decisione cambia un valore o una banda, si aggiorna `VALUES`.

```python
"""Sonda S-4 (sola lettura, Proposta_Dwell_Estensione_DW9.md): D-5 accesa e dwell scritti IN MEMORIA nei registri
(valori raccomandati o estremi delle bande di incertezza); confronto con la fotografia. Nessun file del repository
modificato.

uso: <python> probe_dw9.py <rec|min|max> <famiglie> <out_dir> [regex --only]
  famiglie = 'all' oppure elenco separato da virgole fra: sam_aaa, tvd_vista, ewr, navi, awacs
"""
import json
import logging
import sys
from collections import Counter

logging.disable(logging.CRITICAL)

from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as V
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as S
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as A
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

VISTA = (3.2, 1.75, 6.0)            # (raccomandato, minimo, massimo) della banda [s]
SPS49 = (5.0, 5.0, 10.0)
FREGAT = (7.1, 5.0, 10.0)
HEAD_NET = (7.1, 5.0, 10.0)
SPY1 = (5.0, 5.0, 60.0)
# famiglia -> {(registro, modello, sensore): (raccomandato, minimo, massimo)}; banda assente = tre valori uguali
VALUES = {
    'sam_aaa': {(V, 'ZSU-23-4-Shilka', 'radar'): (18.0, 3.0, 18.0), (V, 'Flakpanzer-Gepard', 'radar'): (1.0, 1.0, 1.0),
                (V, '2K22-Tunguska', 'radar'): (1.82, 1.0, 4.0), (V, '9A33-Osa', 'radar'): (1.82, 1.82, 1.82),
                (V, 'MIM-115-Roland', 'radar'): (1.0, 1.0, 1.0), (V, '9K331-Tor', 'radar'): (1.7, 1.0, 3.0),
                (V, '2K12-Kub', 'radar'): (3.5, 3.0, 4.0), (V, '9K37-Buk', 'radar'): (9.0, 4.3, 20.0),
                (V, 'S-300PS', 'radar'): (12.0, 5.0, 12.0)},
    'tvd_vista': {(V, m, s): VISTA for m, s in (('Strela-1-9P31', 'TVD'), ('MIM-72G-Chaparral', 'TVD'),
                                               ('9K35-Strela-10', 'TVD'), ('M6-Linebacker', 'TVD'),
                                               ('ZSU-57-2', 'visual'), ('M163-VADS', 'visual'))},
    'ewr': {(V, 'FuMG-80-Freya', 'radar'): (60.0, 7.5, 60.0), (V, 'Wassermann', 'radar'): (60.0, 7.5, 60.0),
            (V, 'AN-FPS-117', 'radar'): (10.0, 10.0, 10.0)},
    'navi': {(S, m, 'radar'): v for m, v in (
        ('CVN-70 Carl Vinson', SPS49), ('CVN-71 Theodore Roosevelt', SPS49), ('CVN-72 Abraham Lincoln', SPS49),
        ('CVN-73 George Washington', SPS49), ('CVN-74 John C. Stennis', SPS49), ('CVN-75 Harry S. Truman', SPS49),
        ('CV-59 USS Forrestal', SPS49), ('CV 1143.5 Admiral Kuznetsov', FREGAT), ('USS Arleigh Burke IIa', SPY1),
        ('Type 052B Guangzhou-class', FREGAT), ('Type 052C', SPY1), ('CG-65', SPY1),
        ('CGN 1144.2 Piotr Velikiy', (7.1, 5.0, 20.0)), ('CG 1164 Moskva', (10.0, 5.0, 20.0)), ('FFG-46', SPS49),
        ('FF 1135M Rezky', HEAD_NET), ('FFG 11540 Neustrashimy', FREGAT), ('Type 054A', (2.0, 2.0, 10.0)),
        ('FFL 1124.4 Grisha', HEAD_NET), ('FSG 1241.1MP Molniya', HEAD_NET), ('LHA-1 Tarawa', SPS49),
        ('Type 071', (2.0, 2.0, 2.0)))},   # Type 093: nessun valore
    'awacs': {(A, m, 'radar'): (10.0, 10.0, 10.0) for m in ('E-3A Sentry', 'E-2D Advanced Hawkeye', 'A-50')},
}

PASS = {'rec': 0, 'min': 1, 'max': 2}[sys.argv[1]]
chosen = list(VALUES) if sys.argv[2] == 'all' else sys.argv[2].split(',')
OUT = sys.argv[3]

for family in chosen:
    for (registry, model, sensor), triple in VALUES[family].items():
        getattr(registry._registry[model], sensor)['dwell_time_s'] = triple[PASS]   # solo in memoria

ER.D5_DWELL_TIME = True   # S32 'off'/'ewr_off' lo rimettono a False con patch.object attorno alla loro esecuzione

reads = Counter()
reduced = Counter()
original_reader = ER.registry_dwell_time
original_factor = ER.dwell_factor


def reader(observer, target, mode):
    value = original_reader(observer, target, mode)
    reads[(getattr(observer, '_model', None), value)] += 1
    return value


def factor(exposure_s, dwell_time_s):
    g = original_factor(exposure_s, dwell_time_s)
    if g < 1.0:
        reduced[(dwell_time_s, round(g, 3))] += 1
    return g


ER.registry_dwell_time = reader
ER.dwell_factor = factor

argv = ['--compare', 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json',
        '--save', f'{OUT}/capture.json', '--quiet']
if len(sys.argv) > 4:
    argv += ['--only', sys.argv[4]]
rc = SB.main(argv)
stats = {'pass': sys.argv[1], 'families': chosen,
         'reads': {f'{m} | {v}': n for (m, v), n in sorted(reads.items(), key=str)},
         'g_below_1': {f'dwell {d} g {g}': n for (d, g), n in sorted(reduced.items(), key=str)}}
with open(f'{OUT}/stats.json', 'w') as fh:
    json.dump(stats, fh, indent=1)
print('PROBE_RC', rc)
print(json.dumps(stats, indent=1))
```

Nota: `Session_Simulator` legge `ER.registry_dwell_time` e `ER.D5_DWELL_TIME` a ogni chiamata e il risolutore cerca
`dwell_factor` fra i globali del modulo a ogni chiamata [V: `Session_Simulator.py:2792-2794`,
`Engagement_Resolver.py:2353`], quindi le sostituzioni in memoria sono viste dal motore. Una chiave di modello
sbagliata in `VALUES` solleva `KeyError` all'avvio (nessun valore scritto in silenzio nel posto sbagliato).

## Appendice B — Contenuto iniziale di `Registro_Dwell_Stimati.md`

```markdown
# Registro dei dwell stimati da aggiornare (D-5, DW-9 rivista)

Periodi di rivisita (`dwell_time_s`, funzione di RICERCA) dei registri che NON sono dati di fonte verificati.
Origine: `Proposta_Dwell_Estensione_DW9.md` (decisioni DW9-1..DW9-9). Copia per i test: costanti `DWELL_S`/
`DWELL_ESTIMATED`/`NO_DWELL` di `Code/Dynamic_War_Manager/Source/Test/Test_Dwell_Data.py` (vanno aggiornate insieme).
Valore FISSO per sensore (nessuna dipendenza da distanza, modo o carico del radar: rinvio dichiarato, Proposta §3.4).
Intervalli di fonte: regime normale se citato, altrimenti valore centrale (media geometrica degli estremi del periodo);
la "banda di incertezza" e' l'intervallo di fonte o degli analoghi. Etichette: FONTE NON VERIFICATA [S] |
FONTE DEBOLE [S] | STIMA PER CONFRONTO [S] | FONTE, interpretazione/attribuzione [S].
Per chiudere una riga: fonte leggibile -> etichetta FONTE nel commento del registro, riga tolta da qui e da
`DWELL_ESTIMATED`; valore o banda cambiati -> registro, test, questo file e sonda S-4.

| Record | Sensore (funzione di ricerca) | Valore [s] | Banda di incertezza [s] | Etichetta | Base | Che cosa serve per chiuderla | Data |
|---|---|---|---|---|---|---|---|
| ZSU-23-4-Shilka | radar (1RL33, ricerca circolare) | 18.0 | 3-18 | FONTE di variante, attribuzione [S] | manuale 1RL33M3 (ZSU-23-4M), 20 gradi/s, modo base | dato del 1RL33 base (1965) | 2026-11-17 |
| 2K22-Tunguska | radar (1RL144) | 1.82 | 1.0-4.0 | STIMA PER CONFRONTO [S] | 9A33-Osa Land Roll, 33 giri/min (analoghi: Gepard 1 s, Pantsir 2-4 s) | giri/min del 1RL144 (manuale 2S6) | 2026-11-17 |
| 9K331-Tor | radar (scoperta 3D) | 1.7 | 1-3 | FONTE, valore centrale, interpretazione [S] | APA: "scanning interval 1 s", zona di elevazione in 3 s | frase GlobalSecurity "main mode 3 s" leggibile (-> 3,0 s) o fonte primaria | 2026-11-17 |
| 9K37-Buk | radar (ricerca 9S18) | 9.0 | 4.3-20 | FONTE NON VERIFICATA [S], valore centrale | GlobalSecurity 9s18.htm (403), circolare 4,5-18 s; 3-14 giri/min radartutorial via ricerca | frase di fonte leggibile (GlobalSecurity, Jane's) | 2026-11-17 |
| S-300PS | radar (ricerca 5N64S) | 12.0 | 5-12 | STIMA PER CONFRONTO [S] | 64N6/64N6E, rotazione ogni 12 s regolare (GlobalSecurity non verificato; P1: 6/12 giri/min) | giri/min del 5N64S | 2026-11-17 |
| Strela-1-9P31 | TVD (vista del servente) | 3.2 | 1.75-6.0 | STIMA PER CONFRONTO [S], valore centrale, APPROSSIMAZIONE L1 | Poe 1974, passata del settore 1,75-6,00 s | legge cumulativa (Koopman) o tempo di scoperta misurato | 2026-11-17 |
| MIM-72G-Chaparral | TVD (vista del servente) | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| 9K35-Strela-10 | TVD (vista del servente) | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| M6-Linebacker | TVD (vista del servente) | 3.2 | 1.75-6.0 | idem | idem | idem; cueing radar non modellato | 2026-11-17 |
| ZSU-57-2 | visual | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| M163-VADS | visual | 3.2 | 1.75-6.0 | idem | idem | idem | 2026-11-17 |
| FuMG-80-Freya | radar | 60.0 | 7.5-60 | STIMA PER CONFRONTO [S] | SCR-270, 1 giro/min (analogo alternativo AMES Type 7) | velocita' di rotazione del Freya | 2026-11-17 |
| Wassermann | radar | 60.0 | 7.5-60 | STIMA PER CONFRONTO [S] | SCR-270, 1 giro/min (analogo alternativo AMES Type 7) | velocita' di rotazione del Wassermann | 2026-11-17 |
| AN-FPS-117 | radar | 10.0 | — | STIMA PER CONFRONTO [S] | AN-TPS-43, 6 giri/min | giri/min dell'AN/FPS-117 da fonte leggibile | 2026-11-17 |
| CV-59 USS Forrestal | radar (AN/SPS-43) | 5.0 | 5-10 | STIMA PER CONFRONTO [S] | AN/SPS-49 | giri/min dell'AN/SPS-43 | 2026-11-17 |
| USS Arleigh Burke IIa | radar (AN/SPY-1D) | 5.0 | 5-60 | FONTE DEBOLE [S] | infobox "1 (orizzonte), 12 (sopra l'orizzonte) scan/min" | periodo di volume search dichiarato | 2026-11-17 |
| Type 052B Guangzhou-class | radar (Type 381) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Fregat-MA (valore centrale) | giri/min del Type 381 | 2026-11-17 |
| Type 052C | radar (Type 346) | 5.0 | 5-60 | STIMA PER CONFRONTO [S] | AN/SPY-1 | periodo di rivisita del Type 346 | 2026-11-17 |
| CG-65 | radar (AN/SPY-1A) | 5.0 | 5-60 | FONTE DEBOLE [S] | infobox "1 (orizzonte), 12 (sopra l'orizzonte) scan/min" | periodo di volume search dichiarato | 2026-11-17 |
| FF 1135M Rezky | radar (Head Net-C) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (MR-310), 6/12 giri/min, valore centrale | giri/min dell'MR-310U | 2026-11-17 |
| Type 054A | radar (Type 382) | 2.0 | 2-10 | FONTE DEBOLE [S] | forum, ~30 giri/min (alternativa Fregat MAE-3 7,1 s) | fonte tecnica | 2026-11-17 |
| FFL 1124.4 Grisha | radar (MR-302 Strut Curve) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (valore centrale) | giri/min dell'MR-302 | 2026-11-17 |
| FSG 1241.1MP Molniya | radar (record con Band Stand, radar di tiro) | 7.1 | 5-10 | STIMA PER CONFRONTO [S] | Head Net-A (valore centrale) | radar di ricerca della corvetta e suoi giri/min | 2026-11-17 |
| LHA-1 Tarawa | radar (AN/SPS-52) | 5.0 | 5-10 | STIMA PER CONFRONTO [S] | AN/SPS-49 | giri/min dell'AN/SPS-52 | 2026-11-17 |
| A-50 | radar (Shmel) | 10.0 | — | FONTE DEBOLE [S] | divulgativo "circa sei giri al minuto" | seconda fonte o fonte tecnica | 2026-11-17 |

Bande dei valori di FONTE (per completezza, non sono stime): 2K12-Kub 3.5 (3-4); CVN-70..75 e FFG-46 5.0 (5-10);
Kuznetsov e Neustrashimy 7.1 (5-10); Piotr Velikiy 7.1 (5-20); Moskva 10.0 (5-20). Gli altri valori di fonte sono
valori unici.

Senza valore (motivo): Chain-Home (illuminazione continua); Mammut (schiera fissa, cadenza non data, nessun analogo);
Type 093 (sonar passivo). Aerei non AWACS: esclusi per decisione dell'utente.

Rinviato (non e' una stima da chiudere, e' un modello da fare): dwell dipendente da distanza, modo e carico del radar,
insieme all'orizzonte radar nel DES e a una legge cumulativa (Koopman/esponenziale); riferimento qualitativo
`Dinamica dei Tempi di Aggiornamento Radar - Google Gemini.md`.
```

## Appendice C — Verifica a campione delle bozze (coerenza interna; nessun accesso al web)

| # | Dove | Incongruenza | Effetto sul piano |
|---|---|---|---|
| C-1 | D2 §2.3 (Tor) | Conclude "settore di 32 gradi in azimut, **non** 360 gradi", ma l'estratto APA che cita ("can be revolved mechanically through 32 deg with a detection zone of 32 to 64 deg") descrive un'inclinazione in **elevazione** (zona 32-64 gradi); P1 riportava "scansione circolare" e la stessa D2 cita "the entire elevation zone covers 32 deg". La lettura "settore in azimut" non e' sostenuta dagli estratti [I] | il valore 1 s resta; il significato ("periodo di rivisita di una ricerca circolare") e' un'interpretazione [S] |
| C-2 | D2 §2.3 | Confidenza "A (due fonti concordi)" con una delle due (GlobalSecurity) non leggibile al controllo | al massimo M (APA sola) |
| C-3 | D2 §2.1 (Buk) | "GlobalSecurity, letta direttamente", mentre P1 la dava 402/403 e "via ricerca" e la sessione principale riceve 403; la cella "4; five; 6; 9, -6" indica una pagina tradotta a macchina | valore trattato come FONTE NON VERIFICATA [S] |
| C-4 | P1 §3 contro D2 §2.4 (64N6E) | P1: "6 o 12 rpm -> 10 s o 5 s"; D2: "una rotazione ogni 12 s -> 5 rpm" (e 6/12 s in inseguimento). Le due bozze danno periodi diversi per lo stesso radar | l'analogo dello S-300PS (12 s) e' incerto anche nel numero: DW9-4 |
| C-5 | P1 §6 contro D3 §2.6.2 (Type 381) | P1: "un mirror riporta 5 rpm"; D3: "i mirror riportano lo stesso testo, senza valore" | nessun valore di fonte: si usa l'analogo |
| C-6 | D4 §7 punto 5 contro §1 e §2.5 (M6) | lo slew-to-cue dell'M6 e' etichettato **M** nella sintesi e **B** (snippet di pagina non letta) nella tabella e nel testo | nessuno (dato qualitativo, non usato) |

Controlli aritmetici rifatti, tutti corretti: 60/33 = 1,818; 360/20 = 18; 360/45 = 8; 360/60 = 6; 2 x 100/20 = 10;
60/14 = 4,29; 60/20 = 3; 60/12 = 5; 60/30 = 2; 60/6 = 10.
