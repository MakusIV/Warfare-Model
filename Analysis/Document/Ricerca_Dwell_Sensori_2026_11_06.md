# Ricerca dati di scansione / permanenza (dwell) dei sensori NON EWR (2026-11-06)

> Rapporto di ricerca (web + lettura del codice in sola lettura). **Non e' una fonte finale dei dati**: serve a
> decidere quali valori di `dwell_time_s` inserire e dove il concetto non si applica. Complemento di
> `Ricerca_EWR_2026_10_29.md` (i 10 EWR gia' trattati) e di `Proposta_Dwell_Time_Rilevamento.md`. Nessun file del
> repository e' stato modificato (questo e' l'unico file nuovo). Nessuna scelta di valore e' fatta qui.

## 0. Metodo, limiti, convenzioni

**Definizione usata.** `dwell_time_s` = periodo di rivisita = tempo fra due illuminazioni successive dello stesso
punto. Per un radar a rotazione meccanica a velocita' costante: 60 / (giri/min). Per un sensore che illumina il
bersaglio di continuo (inseguimento) o che non scandisce (ottico a campo fisso, ricerca a vista) **non e' definito**:
lo dichiaro "non applicabile" con il motivo.

**Strumenti e limiti reali (da leggere prima dei numeri).**
- Le pagine sono lette con uno strumento che le passa a un piccolo modello riassuntore; i numeri sono quelli
  riportati dal riassunto, non una lettura diretta del sorgente. Dove ho potuto, ho riletto la stessa pagina
  con un secondo prompt; dove no, la confidenza e' abbassata.
- **radartutorial.eu non e' scaricabile** (404 su ogni scheda provata: karte011, 014, 028, 088, 093). I suoi dati
  arrivano da (a) snippet del motore di ricerca ("via ricerca") e (b) una pagina del sito armsnet.duckdns.org
  che ricopia la scheda radartutorial dell'1S91 (letta direttamente, cita karte011). Il campo "antenna rotation"
  delle schede radartutorial e' spesso vuoto nella versione indicizzata (Flap Lid 30N6E, 1RL144).
- **Non raggiungibili / pagina chiusa**: GlobalSecurity (402/403: i dati del 9S18 sono dallo snippet di ricerca,
  che cita anche Army Recognition), DTIC (403: i rapporti sulla scoperta visiva ADA017599, ADA020657, ADA025823
  esistono ma NON sono stati letti), Military Periscope (paywall: leggibile solo l'incipit; la pagina MPDR-16 pero'
  conteneva il dato), ru.wikipedia 9К33/9К37 (404; 2К22 e Куб lette ma senza dati di scansione), Hoggit wiki,
  manuale F-14 Heatblur (404). Non ho consultato nessun manuale tecnico primario ne' Jane's.
- Wikipedia: per quasi tutti i radar la pagina **non riporta** giri/min o periodo di scansione (verificato
  pagina per pagina: ZSU-23-4, 9K37, 9K33, 2K12, Tor, APG-63/66/68/73, AWG-9, MiG-29, A-50, E-2, Type 381/360,
  SPS-43/52). Dove c'e' il dato lo cito; dove non c'e' scrivo "non trovato".
- **Fonti da gioco/simulatore** (War Thunder wiki, forum DCS, guide DCS/Falcon BMS, articoli flyandwire) sono
  usate solo come ultima risorsa, **sempre confidenza bassa**, e dichiarate come tali.

**Scala di confidenza** (come nella ricerca EWR): **alta** = piu' fonti indipendenti concordi o fonte tecnica
primaria; **media** = una fonte tecnica secondaria seria o piu' fonti non indipendenti; **bassa** = fonte unica o
debole (forum, gioco, mirror di Wikipedia, giornalismo, snippet di ricerca non verificabile).

**Tipo di dato (colonna T)**: **F** = dato di fonte; **D** = dedotto con calcolo mostrato; **S** = stima mia
dichiarata. "non trovato" = cercato e non reperito (esito valido).

**Applicabilita' del dwell**, categorie usate nelle tabelle:
- **A** = ricerca a rotazione meccanica 360 gradi: dwell = 60/rpm (applicabile).
- **B** = ricerca a scansione di settore o a fascio elettronico (phased array su torretta o fisso): il periodo non
  e' 60/rpm ma dipende dal settore/dal programma di fascio; applicabile solo se la fonte da' un periodo.
- **C** = inseguimento continuo (conical scan, monopulse, STT): **non applicabile**.
- **D** = ottico/IR a campo fisso o ricerca a vista: **non applicabile come periodo di rivisita**; la domanda e'
  un'altra (tempo di acquisizione).

**Importante per il registro (osservazione dal codice, sez. 1)**: molte voci `radar` dei SAM/AAA fondono ricerca e
inseguimento in un solo record (es. `1RL144 Search + 1A26 Tracking`, `9S35 Fire Dome` con `acquisition_range` 85 km
che e' la portata del radar di ricerca 9S18M1, non del Fire Dome). `acquisition_range` (la R della Pd) e' del radar
di **ricerca**: il `dwell_time_s` da associare e' quello del radar di ricerca, non dell'inseguimento.

## 1. Cosa c'e' nel repo (lettura in sola lettura)

Struttura: `record['radar'|'TVD'|'visual'] = {'model', 'capabilities': {'air'|'ground'|'sea': (bool, {tracking_range,
acquisition_range, engagement_range, multi_target_capacity})}}` (esempi: `Vehicle_Data.py:3729` per `visual`,
`:4549` per `30N6 Flap Lid`). Lettura: `Mobile.detection_range` (`Asset/Mobile.py:1570`), massimo fra radar, TVD e
visual (`visual` escluso se `D4C_VISUAL_SENSOR` e' spento). Inventario ricavato caricando i tre registri
(`Vehicle_Data/Ship_Data/Aircraft_Data._registry`): **30** veicoli con almeno un sensore, **23** navi, **65** aerei.

Veicoli (30): 15 EWR/radar di scoperta a terra (gia' trattati: 1L13, 55Zh6, AMES Type 7/80, FPS-117, TPS-43, Chain Home,
Freya, Mammut, P-12, P-14, P-18, P-37, SCR-270, Wassermann) + **15 non EWR (oggetto di questa ricerca)**:
- SAM con radar: `2K12-Kub` (1S91 Straight Flush), `2K22-Tunguska` (1RL144 Search + 1A26 Tracking), `9A33-Osa` (Land Roll),
  `9K331-Tor` (Multifunction 3D Radar), `9K37-Buk` (9S35 Fire Dome), `S-300PS` (30N6 Flap Lid), `MIM-115-Roland` (MPDR 16).
- SAM/MANPADS con solo TVD: `9K35-Strela-10` ("Optical-IR tracker"), `Strela-1-9P31` ("Optical sight"),
  `MIM-72G-Chaparral` ("Forward Looking Infrared"), `M6-Linebacker` ("FLIR and targeting system").
- AAA: `ZSU-23-4-Shilka` (1RL33 Gun Dish), `Flakpanzer-Gepard` ("Search and Tracking Radar"); con solo `visual`
  (D-4c): `ZSU-57-2`, `M163-VADS`.

Navi (23): 22 con radar (SPY-1A/1D Aegis, SPS-49+SPS-67, SPS-43+SPS-30, SPS-52+SPS-67, Fregat-MA, Top Pair, Head Net-C,
Strut Curve/Band Stand, Type 381/346/382/360/364...) + 1 sottomarino Type 093 senza radar (sonar passivo; non e'
oggetto della ricerca). Nessuna nave ha `TVD`/`visual`.

Aerei (65): 48 con radar vero, 32 con TVD (25 con entrambi), 10 senza sensori. Gruppi: caccia con radar (F-16, F-15,
F/A-18, F-14, MiG-29, Su-27/30/33/34, MiG-21/23/25/31, Mirage 2000, Viggen, F-4E, F-5E, F-86, MiG-15/19), AWACS
(E-3A, E-2D, A-50), pattugliatori/bombardieri con radar di superficie (S-3B, Tu-142, B-52H, B-1B, Tu-95/160/22M, Il-76),
pod TVD (LITENING, Sniper, LANTIRN, Pave Tack, NITE Hawk, AN/AAS-44, Shkval/Mercury, IRST OEPS-27/OEPrNK-29/OLS-30/OLS-35).

**Modelli usati negli scenari di prova** (conteggio dei letterali in `Scenario_Fixtures.py`, `Scenario_Baseline.py`,
`Test_Session_Scenarios*.py`; la fotografia `scenario_baseline.json` non contiene i nomi di modello):
`F-16C Block 52d` (25), `ZSU-23-4-Shilka` (12), `MiG-29S` (11), `9K35-Strela-10` (11), `A-10C Thunderbolt II` (9),
`F-15C Eagle` (6), `9K37-Buk` (4), `ZSU-57-2` (3), `M163-VADS` (3), `F-15E` (3), `9K331-Tor` (3), `S-300PS` (2),
`F/A-18C` (2), `Flakpanzer-Gepard`, `2K22-Tunguska`, `USS Arleigh Burke IIa`, `CVN-70 Carl Vinson`, `CG-65`, `B-52H` (1 ciascuno).
In piu' appaiono nei test unitari: `2K12-Kub`, `9A33-Osa`, `MIM-115-Roland`, `M6-Linebacker`, `MIM-72G-Chaparral`.
Priorita' seguita: AAA e SAM degli scenari, poi aerei e navi degli scenari, poi il resto.

## 2. Radar di inseguimento: perche' il dwell non si applica (fondamento generale)

- **Conical scan**: "il feed viene fatto ruotare, il bersaglio sulla linea mediana genera un ritorno costante e il
  sistema di controllo ruota l'antenna per mantenerlo costante" ([W-ConScan], pagina letta). Il fascio e' puntato sul
  bersaglio di continuo; la "scansione" e' una nutazione interna allo strumento di misura, non una ricerca. Esempio
  del documento: il Mk 25 USN usa uno "spiral scan" per l'acquisizione e poi commuta in conical scan per
  l'inseguimento. Confidenza: **media** (pagina enciclopedica ma coerente con la teoria standard); T = F.
- **Monopulse**: "estrae distanza e direzione da un singolo impulso" ([W-Monopulse], letta): l'errore d'angolo e'
  disponibile a ogni impulso, quindi nessun periodo di rivisita. Confidenza **media**; T = F.
- **Track-while-scan (TWS)**: l'aggiornamento della traccia e' quello della **scansione di ricerca** (la pagina Monopulse
  dice che fra le misure la posizione e' estrapolata con la velocita'); il periodo di rivisita e' quindi il periodo
  della ricerca, non quello dell'inseguimento. Per gli aerei in TWS i valori sono in sez. 4.
- Conseguenza per il registro: per `tracking_range`/`engagement_range` (Fire Dome, 1S31, Land Roll tracking,
  1A26, Gun Dish in tracking, MPDR tracker del Gepard, i radar di tiro) **nessun `dwell_time_s`**. Un SAM la cui ricerca
  e' un radar separato dal tracker ha dwell solo per la ricerca (acquisition_range).

## 3. SAM e AAA (veicoli non EWR)

Le colonne: rpm = giri/min di fonte; Periodo = 60/rpm (D) o periodo dichiarato (F); "Regime normale?" = la fonte indica
un regime normale/tipico (la regola di progetto lo preferisce, altrimenti rotazione piu' veloce).

| Modello / chiave nel repo | Radar di ricerca e scansione | rpm / periodo (estremi) | Regime normale? | Applicabilita' | Fonte | Conf. | T |
|---|---|---|---|---|---|---|---|
| **9K37-Buk** (registro: `9S35 Fire Dome`; acquisition 85 km) | Ricerca = 9S18M1 "Snow Drift/Kupol": pannello planare, rotazione meccanica in azimut, scansione elettronica in elevazione. Tracking 9S35 = Cassegrain a scansione meccanica (tracking/CW), non e' ricerca | **(a)** 9S18M "Kupol-M": **3 ... 14 rpm** -> **20 ... 4,3 s** (60/3 = 20; 60/14 = 4,29). **(b)** forum army.ca (9S18): 6,7 / 10 / 18 rpm -> 9,0 / 6,0 / 3,3 s. **(c)** GlobalSecurity (via ricerca, anche Army Recognition): periodo di "rivista" **settore 30 gradi: 2,5 ... 4,5 s; circolare: 4,5 ... 18 s** (secondo settore e disturbo); per la variante 9S18M1-3 valori singoli 2,5 s e 4,5 s | **No** (fonte (a),(c) danno intervalli; (c) lega l'estremo al disturbo) | **A/B**: 9S18 e' circolare 360 gradi, con modo settoriale 30 gradi | (a) [RT-9S18M] via ricerca, scheda del Kupol-M, NON 9S18M1; (b) [AC-Forum]; (c) [GS-9S18] via ricerca; scansione: [MP-9S18M1] (paywall, incipit); inseguimento: [W-Buk] | **bassa-media** (tre fonti non indipendenti e di varianti diverse; (a) e (c) concordano su ~4,3-4,5 s come estremo veloce) | F (rpm e periodi di fonte); D (periodi da rpm) |
| **2K12-Kub** (registro: `1S91 Straight Flush`; acquisition 75 km) | 1S91 = due antenne indipendenti sul veicolo: 1S11 (ricerca/acquisizione, banda C, fascio 1 gradi in azimut) e 1S31 (inseguimento fine + illuminazione CW). La scheda dice "scan 360 gradi, antenna ruotante" | **15 o 20 rpm** -> **4 s o 3 s** (D) | **Non indicato** | **A** per la ricerca; **C** per la 1S31 | [RT-1S91] (scheda radartutorial letta tramite la pagina armsnet che la ricopia; 404 diretto), [APA-Kvadrat] (architettura, nessun rpm) | **media-bassa** (fonte unica; la scheda non dice quale delle due antenne ruota a 15/20; assegnazione alla 1S11 e' mia deduzione) | F (rpm), D (periodo) |
| **9K331-Tor** (registro: `Multifunction 3D Radar`; acquisition 25 km) | Ricerca = 9S18 "Scrum Half": 3D pulse-Doppler, scansione **circolare**, scansione meccanica (poi elettronica) con "settore di 32 gradi" (ambiguo: verosimilmente l'elevazione; non verificato); inseguimento 9S36 a PESA con 570 sfasatori | **tempo di scansione = 1 s** (-> 60 rpm, D) da un solo documento (riassunto di Army Recognition su carte trapelate) | n/a (valore singolo) | **A** (ricerca) ; **C** (9S36) | [AR-Tor] via ricerca; [W-Tor] (letta: 32 gradi, 48 bersagli rilevabili, nessun rpm); [Armsnet-9S18] (letta: "S-band cage mechanical scan", rotazione non indicata) | **bassa** (fonte unica, documenti trapelati) | F (1 s), D (60 rpm) |
| **9A33-Osa** (`Land Roll`; acq. 30 km) | Antenna di ricerca ellittica rotante in banda H (6-8 GHz); inseguimento a **conical scan** in banda H/J; backup elettro-ottico 9Sh33 | rpm / periodo: **non trovato** (nessuna fonte letta li riporta) | - | **A** per la ricerca (periodo ignoto); **C** per l'inseguimento | [W-Osa] (letta), [MP-LandRoll] (paywall) | **media** per il tipo di scansione, il numero e' **non trovato** | - |
| **2K22-Tunguska** (`1RL144 Search + 1A26 Tracking`; acq. 18 km) | 1RL144 "Hot Shot": radar di ricerca/acquisizione 3D in banda S, antenna stabilizzata e **attiva anche in movimento**, fasci multipli larghi ~5 gradi in elevazione fino a 15 gradi (scheda radartutorial via ricerca); inseguimento 1A26 banda X | rpm: **non trovato** (campo vuoto nella scheda radartutorial indicizzata; nessun'altra fonte) | - | **A** presumibile (ricerca rotante), periodo ignoto; **C** per 1A26 | [RT-1RL144] via ricerca; [GS-HotShot] via ricerca (portate 18/13 km) | **bassa** | - |
| **S-300PS** (registro: `30N6 Flap Lid`; acq. 150 km, trk 90) | Il registro nomina il **30N6** (radar di ingaggio/illuminazione a phased array su **torretta rotante** che orienta l'array su un **settore di 60 o 100 gradi**, steering digitale del fascio, TVM): non e' un radar di ricerca a rotazione. La ricerca dell'S-300PS e' il 5N64S "Big Bird-B"; il 64N6 "Tombstone" (S-300PM) e' il successivo | **30N6**: **non applicabile come rpm** (array a fasci elettronici su settore); periodo di rivisita: **non trovato**. **64N6E**: **6 o 12 rpm** -> **10 s o 5 s** (D). **5N64S Big Bird-B**: rpm **non trovato** | **64N6E: no** | **B** (30N6, array a settore); **A** (64N6E/5N64S) | [MP-FlapLid] (paywall, "phased-array", letto), [APA-DKB] (letto: 64N6 "due punti di traccia per rotazione"; l'array del 30N6E "su torretta rotabile"), [RT-64N6E] via ricerca, [CAV-S300] via ricerca (settore 60/100 gradi) | **bassa-media**; il 64N6E e' del sistema successivo, NON attribuire al 5N64S | F; D (10/5 s) |
| **MIM-115-Roland** (`MPDR 16`; acq. 18 km) | Radar di acquisizione MPDR-16 pulse-Doppler, antenna 2x1 m, **360 gradi** (separato dal tracker) | **60 rpm** -> **1 s** (D) | n/a (valore singolo) | **A** | [MP-MPDR16] (letta; l'incipit riporta "rotates at 60 rpm", portata 1,5-16,5 km) | **media** (una fonte tecnica secondaria, concorda con il 60 rpm trovato per l'MPDR-12 del Gepard) | F (rpm), D (1 s) |
| **Flakpanzer-Gepard** (`Search and Tracking Radar`; acq. 15 km) | Ricerca MPDR-12 (S-band, doppler, su braccio oscillante a poppa torretta, poi MPDR-18 S-band); tracker Ku-band frontale, ruota di 180 gradi a sx/dx, inseguimento automatico in az/elev/distanza | **60 rpm** -> **1 s** (D) | n/a | **A** (ricerca); **C** (tracker) | [TE-Gepard] (letta: "ruota 60 volte al minuto", 15 km), [Brickmania] via ricerca (stesso 60 rpm) | **media-bassa** (due fonti divulgative, probabilmente non indipendenti) | F, D |
| **ZSU-23-4-Shilka** (`1RL33 Gun Dish`; acq. 20 km, trk 8) | RPK-2 Tobol (Gun Dish): ricerca + inseguimento sulla stessa antenna in torretta. **Tipo di scansione della ricerca: non trovato** (Wikipedia letta: nessun dato). Solo gioco: War Thunder wiki dice arco di ricerca di default 90 gradi (selezionabili 30/60/360), "scansione molto lenta" senza numeri | rpm / periodo: **non trovato** | - | **B** (verosimile settore) ; in inseguimento **C** | [W-ZSU234] (letta, 20 km, mancanza di scansione), [WT-1RL33] gioco, **da non usare** | **bassa** (solo gioco) | - |
| **9K35-Strela-10** (`Optical-IR tracker`, TVD) | Sensore ottico/IR a fotocontrasto e IR del puntatore; il radar telemetro 9S86 "Snap Shot" misura distanza e velocita' radiale, **non scopre**; la scoperta e' a vista dell'operatore (o da radar esterni) | vedi sez. 5 | - | **D** (non applicabile) | [APA-Strela10] (letta), [GS-SA13] via ricerca (portata di acquisizione ottica 2000-8000 m, IR 2300-5300 m) | **media** (portate) | F |
| **Strela-1-9P31** (`Optical sight`), **MIM-72G-Chaparral** (`FLIR`), **M6-Linebacker** (`FLIR and targeting`) | Mirino ottico (Strela-1: solo cielo sereno, forum), FLIR (Chaparral: nessun dato trovato), FLIR di Bradley (M6) | vedi sez. 5 | - | **D** | sez. 5 | - | - |
| **ZSU-57-2**, **M163-VADS** (`visual`) | Nessun radar di scoperta (AN/VPS-2 e' range-only); scoperta solo visiva a occhio nudo | vedi sez. 5 | - | **D** | `Ricerca_Sensore_Visivo_ZSU57_M163_2026_10_29.md` (gia' fatta) | - | - |

Note e dubbi della sez. 3 (da non dimenticare):
- **Buk**: il `model` del registro ("9S35 Fire Dome") e' il radar di inseguimento; la `acquisition_range` 85 km e' del
  9S18M1 (Wikipedia: 85 km). Il dwell va preso dal 9S18M1, non dal Fire Dome. Le tre fonti concordano che la
  rotazione veloce corrisponde a ~4,3-4,5 s; non c'e' un regime normale dichiarato.
- **Kub**: 15/20 rpm e' sulla scheda dell'**1S91 nel suo insieme**; potrebbe riferirsi alla sola 1S11.
- **Tor**: il "32 gradi" di Wikipedia e' ambiguo (azimut o elevazione); non va confuso con una scansione settoriale
  in azimut: la scheda leaked dice "scansione circolare".
- **S-300PS**: il registro associa `acquisition_range` 150 km al Flap Lid; fisicamente la ricerca e' il Big Bird/64N6.
  Decisione per voi: dwell del radar di ricerca (non trovato per il 5N64S) oppure nessun dwell.
- **Osa, Tunguska, Gun Dish**: tipo di scansione noto solo a grandi linee, periodo **non trovato**.

## 4. Radar di bordo degli aerei e AWACS

Per i radar di caccia il concetto "giri/min" non c'e': la ricerca e' una scansione a barre (azimut x barre di
elevazione) su un volume limitato al cono frontale; il periodo di rivisita e' il tempo del **frame** (un passaggio
completo del volume), dipende da larghezza azimutale e numero di barre scelti dal pilota (RWS/TWS/ACM/STT). I
dati ufficiali di tempo di frame **non sono pubblici nelle fonti raggiunte**.

| Modello / chiave nel repo | Tipo di scansione | Tempo di frame / periodo (estremi) | Applicabilita' | Fonte | Conf. | T |
|---|---|---|---|---|---|---|
| **F-16C Block 52d / CM Block 50** (`AN/APG-68(V)5`, `(V)9`) | Antenna planare **meccanica**; azimut ±10 / ±30 / ±60 gradi; cono di ricerca 120x120 gradi; 4 barre di default ("da 4 a 2 barre = meta' volume al doppio della frequenza di aggiornamento", forum DCS) | Tempo di frame **non trovato**. Aneddotici (utenti di simulatore): ~0,5 s a ±10 gradi; ~1,5 s e ~5 s per altre combinazioni, snippet parzialmente illeggibile | **B** (frame di barre su volume limitato); in STT **C** | [W-APG68] (letta: azimut e cono), [DCS-APG68] via ricerca (forum, gioco) | **bassa** (e **non trovato** il dato ufficiale) | F (geometria), tempi non usabili |
| **F-15C Eagle** (`AN/APG-63(V)1`), **F-15E** (`APG-70`) | Meccanica (planare con elaboratore programmabile); azimut/barre/tempo di frame **non trovato** | **non trovato** | B | [W-APG63] (letta: nessuna scansione) | - | - |
| **F/A-18C** (`AN/APG-73`), **F/A-18A** (`APG-65`) | non trovato | **non trovato** | B | [W-APG73] (letta) | - | - |
| **MiG-29S/A** (`N019M Topaz`, `N019 Rubin`) | Antenna Cassegrain a polarizzazione twist (N019); settore e frame **non trovati** | **non trovato** | B | [W-MiG29] (letta, prime 100k caratteri) | - | - |
| **Su-30 / Su-34 / Su-33 / Su-27** (`N011M Bars`, `V004`, `N001`) | N011M: array planare a **scansione elettronica** (±70 az, ±45 el fissa; ±90 con motori); posizionamento fascio 400 microsecondi; frame **non trovato**. N011/N001: planare meccanica ±85 gradi (N011) | **non trovato** | **B** (N011M: il periodo e' di software) | [W-Bars] (letta) | **media** per il tipo, tempo di frame **non trovato** | F |
| **F-14A/B** (`AN/AWG-9`) | Meccanica; 8 barre ±65 gradi; **~13-14 s** per il frame (130 gradi) -> ~9-10 gradi/s (D); TWS: **~2 s** (due settori da 40 gradi o quattro da 20 gradi) | 13-14 s (ricerca 8 barre), 2 s (TWS ristretta) | **B** | [FW-Bars] (articolo DCS letto: "8B ±65 gradi sempre ~14 s"), [Key-AWG9] forum (13 s per 130 gradi), [HB-TWS] snippet Heatblur (2 s) | **bassa** (guide di simulatore; nessuna fonte tecnica) | F (da gioco), D |
| **E-3A Sentry** (`AN/APY-2`) | Rotodome a **360 gradi**, scansione meccanica in azimut + elettronica in elevazione | **6 rpm -> 10 s** (D; la fonte dice "copre 200.000 miglia quadrate ogni 10 s"); a radar spento il dome gira 1 giro/4 minuti | **A** | [W-E3] (letta, "6 giri/min"), [AFT-E3] e [DM-E3] via ricerca (concordi, 10 s) | **alta** (piu' fonti concordi, non indipendenti dalla scheda USAF) | F, D |
| **E-2D** (`AN/APY-9`) | Rotodome + AESA (meccanica + elettronica) | rpm / periodo **non trovato** (Wikipedia letta: nessuno) | **A/B** | [W-E2] | - | - |
| **A-50** (`Shmel`) | Rotodome; rpm **non trovato** | **non trovato** | A | [W-A50] (letta) | - | - |
| **Bombardieri/pattugliatori, ricognitori** (`APQ-166/-164`, `Obzor-*`, `AN/APS-137`, `Kupol-76`...) | Radar di superficie/mappatura: non rilevanti per rilevamento aria-aria; non cercati | **non cercato** | - | - | - | - |

Considerazioni: (1) per un caccia il periodo di rivisita **non e' una proprieta' del radar ma del modo scelto**; il
DES non modella RWS/TWS/STT, quindi qualunque valore sarebbe una scelta di modello. (2) Il limite di
~60 gradi/s citato per le parabole meccaniche generiche ([WTP-Radar], letta: "scan rates topped out near 60 deg/s";
confidenza **bassa**, divulgativo, non attribuito esplicitamente all'APG-63) darebbe, per una barra a ±60 gradi
(120 gradi), un tempo minimo di **2 s** per passaggio (D, solo ordine di grandezza; non e' un dato dell'APG-68).

## 5. TVD (pod e mirini elettro-ottici) e ricerca a vista

**Pod di puntamento (LITENING, Sniper, LANTIRN, Pave Tack, NITE Hawk, Kaira, Shkval, Mercury, AFA-xx)**:
- sono sensori **a campo fisso (staring)** montati su gimbal: l'immagine e' continua, non c'e' una scansione che
  ripassi sullo stesso punto -> **dwell non applicabile (D)**. Il "tempo per trovare un bersaglio" e' di
  operatore/designazione esterna, **non trovato come dato di fonte**.
- Dati geometrici (non usabili come dwell): LITENING campo largo 18,4x24,1 gradi, medio 3,5x3,5, stretto 1x1, campo di
  regard +45/-150 gradi (scheda variante LITENING; **bassa-media**, [W-Litening] via ricerca); Sniper XR campo largo 4x4,
  stretto 1x1, regard +35/-155 gradi ([DU-Sniper] via ricerca, **bassa-media**; altra fonte dice -155/+5: contraddizione).
- **IRST** (OEPrNK-29, OEPS-27, OLS-30, OLS-35): sono sensori che scandiscono un settore e quindi avrebbero un
  periodo di rivisita; **non cercati** in questa passata (priorita' bassa: non negli scenari).

**TVD di terra** (Strela-10, Strela-1, Chaparral, M6): sono mirini/seeker usati dall'operatore dopo la scoperta
visiva (o dopo un cueing radar esterno). Dati trovati:
- **Strela-10**: portata di acquisizione ottica (fotocontrasto) 2000-8000 m, IR 2300-5300 m ([GS-SA13] via ricerca,
  **media-bassa**, snippet). Tempo di reazione del sistema 6,5 s (10SV), 8,5 s (10M), 6,5 s (10M2), 7,0 s (10M3)
  dalla tabella di [APA-Strela10] (letta): **la fonte non definisce che cosa misuri** ("Reaction time [s]"), quindi
  **NON e' un tempo di acquisizione**; non va usato come tale. 9K35M3: sensore 9Sh127 con campo largo/stretto (senza numeri);
  Kolchan: sensore a FPA con campo 12x16 gradi (variante moderna, non del repo).
- **M6 Linebacker**: la scoperta e' demandata al cueing radar (AN/MPQ-64 Sentinel, con slew-to-cue) e al FLIR del
  Bradley; i campi del FLIR di 2a generazione IBAS (M2A3/M3A3, **non** confermato per l'M6 su M2A2): largo 13,33x7,5 gradi,
  stretto 3,56x2,0 gradi ([DRS-IBAS], [FAS-M6] via ricerca; **bassa**). Tempo di acquisizione: **non trovato**.
- **Chaparral FLIR**, **Strela-1 mirino** (campo di vista): **non trovato**.

**Ricerca a vista**:
- Dati gia' presenti in `Ricerca_Sensore_Visivo_ZSU57_M163_2026_10_29.md` (Howell: piloti 5,5-8,7 km; osservatore vigile
  17,3-23 km come limite alto; stima 5-6 km per caccia a bassa quota). **Sono distanze, non tempi**.
- Tempo di scoperta visiva, letteratura:
  - **Koopman**: il modello di ricerca visiva assume "colpi d'occhio" (glimpse) come prove indipendenti; soglia di
    contrasto = quella che da' probabilita' 1/2 su **un glimpse di ~1/3 - 1 s**; la probabilita' cumulata di
    scoperta e' esponenziale nel tempo ([Koopman56] via ricerca, [Koopman86] via ricerca). **Media-bassa** (snippet; non sono i dati
    di un osservatore antiaereo). Utile come **forma** della legge (esponenziale), non come numero.
  - **Rapporti militari USA** esistenti e **non letti** (DTIC 403): Poe (1974) "A Model for Visual Detection of
    Aircraft by Ground Observers", ADA017599 (osservatori che cercano in un settore, curve di probabilita'
    cumulata di scoperta in funzione del tempo); ADA020657 "Ground Observer Ability to Detect and Estimate the Range of Jet
    Aircraft Flying over Hilly Terrain" (osservatori che cercano un settore di **180 gradi**, tempo alla scoperta registrato);
    ADA025823 (elicotteri a 1-5 km). Il contenuto numerico e' **non trovato** perche' non raggiungibile. Sono la pista
    migliore per un "tempo medio di scoperta visiva".
  - Altri riferimenti (civili, UAS): soglia angolare ~12' di arco (0,2 gradi) per scoperta di aerei in rotta di collisione
    (ERAU/Gibb via ricerca); osservatori a terra scoprono l'aereo prima del pilota ~60% delle volte a 200 e 1.400 m
    (ASSURE review via ricerca). **Bassa**, non pertinenti ai tempi dei serventi di AAA.
- **Conclusione sul dwell**: la ricerca a vista non ha un periodo di rivisita (non scandisce un volume con ripasso
  regolare); la Pd del tempo alla scoperta segue una legge cumulativa (verosimilmente esponenziale) che e' **un altro
  modello** rispetto al `min(1, permanenza/dwell)` della Proposta. Per il DES e' una decisione di design (non un dato).

## 6. Navi (radar di bordo)

Molti radar navali sono "combinati" (es. `AN/SPS-49 + AN/SPS-67`, `Fregat-MA + Podkat + Top Pair`): il registro li
fonde in un solo `acquisition_range` (di norma quello del radar a lunga portata). Il dwell dovrebbe seguire il radar di
ricerca aerea a lunga portata.

| Modello / chiave nel repo | Radar e scansione | rpm / periodo (estremi) | Regime normale? | Applicabilita' | Fonte | Conf. | T |
|---|---|---|---|---|---|---|---|
| **CVN-70..75, FFG-46** (`AN/SPS-49`) | 2D, 360 gradi, rotazione meccanica | **6 rpm (portata lunga) o 12 rpm (portata corta)** -> **10 s o 5 s** (D). L'AN/SPS-49A(V)1 ha **12 rpm come default** | **Si'** (Wikipedia: "(V)1 defaults to 12 rpm") -> 5 s | **A** | [W-SPS49] (letta; una pagina derivata inverte l'associazione portata-giri, riportato dal riassunto di ricerca) | **media-alta** (piu' fonti concordi sui due valori; incertezza sull'associazione) | F, D |
| **CVN, LHA-1** (`AN/SPS-67`; anche `AN/SPS-30` della Forrestal) | SPS-67: ricerca di superficie 2D | infobox Wikipedia **15/30 rpm** -> **4 s / 2 s**; **contraddizione**: una scheda radartutorial della serie naval (via ricerca) indica **2 o 4 rpm** -> **30 s / 15 s** | non indicato | **A** | [W-SPS67] (letta), [RT-SPS67] via ricerca (la scheda potrebbe riferirsi a un altro radar) | **bassa** (contraddizione fra fonti) | F, D |
| **CG-65, USS Arleigh Burke IIa** (`AN/SPY-1A / SPY-1D(V)`) | Phased array a 4 facce, fasci elettronici; il periodo di rivisita e' gestito dal software (volume search, horizon search, track) | infobox Wikipedia (serie SPY-1A/B/D): **"Scan rate (scan/min): 1 (orizzonte), 12 (sopra l'orizzonte)"** -> **60 s / 5 s** (D). Significato **non spiegato** dalla pagina | non indicato | **B** | [W-SPY1] (letta) | **bassa** (cifra di infobox, senza definizione) | F, D |
| **CV-59 Forrestal** (`AN/SPS-43`), **LHA-1** (`AN/SPS-52`) | SPS-43: 2D lungo raggio; SPS-52: 3D, meccanica in azimut ed elettronica in elevazione | rpm **non trovato** (Wikipedia: assente) | - | A | [W-SPS43], [W-SPS52] (lette) | - | - |
| **CGN 1144.2 Piotr Velikiy, CV 1143.5 Kuznetsov, FFG 11540** (`Fregat-MA` = MR-750 "Top Plate") | 3D, banda D/E, array a scansione in frequenza, rotante | **12 o 6 rpm** (scheda radartutorial via ricerca) -> **5 s / 10 s** (D); Deagel (via ricerca): 12-15 rpm per le varianti MAE e un 30 rpm isolato | non indicato | **A** | [RT-TopPlate] via ricerca; [Deagel-Fregat] via ricerca | **media-bassa** | F, D |
| **Kuznetsov** (`Sky Watch` = Mars-Passat) | Array fissi a fasci elettronici (non ruota) | rpm: **non applicabile**; periodo di rivisita **non trovato** | - | **B** | non letta | - | - |
| **CG 1164 Moskva, FF 1135M Rezky, FFL Grisha, FSG Molniya** (`Top Pair`, `Head Net-C`, `Strut Curve`, `Band Stand`, `Voskhod`) | Radar di ricerca aerea/superficie a rotazione | rpm: **non trovato** (nessun risultato nelle fonti raggiunte; Wikipedia NATO-names list classifica solo il ruolo) | - | A | non trovata | - | - |
| **Type 054A / 052B / 052C / 071** (`Type 382`, `Type 381`, `Type 346 AESA`, `Type 360`, `Type 364`) | 382: 2 pannelli planari back-to-back rotanti; 381: 3D banda G; 364: 2D; 346: AESA fissa | **Type 364: 30 rpm** (Wikipedia, infobox "Rotation speed: 30RPM") -> **2 s** (D). **Type 382**: Wikipedia letta non da' rpm; un mirror dice "da 12/min a quasi 30/min" -> 5 s / 2 s (**bassa**). Type 381: non trovato (un mirror riporta 5 rpm, **bassa**, non confermato dalla pagina letta). Type 360: non trovato. Type 346: AESA, **non applicabile come rpm** | n/a | A (364, 382, 381, 360); B (346) | [W-T364] (letta), [W-T382] (letta), [W-T381] (letta), [W-T360] (letta) | **media-bassa** per il 364, **bassa** per gli altri | F, D |

## 7. Cosa e' coperto / cosa manca / dati piu' utili per primi

**Coperto (con almeno un dato di fonte)**: dei 15 veicoli non EWR: Buk (intervallo), Kub, Tor, Roland, Gepard, 64N6E
(per l'S-300PM, non il PS). Aerei: E-3A (alta), F-14 (bassa, da gioco). Navi: SPS-49 (media-alta), SPS-67 (bassa, contraddittorio),
Fregat/Top Plate, Type 364 (media-bassa), SPY-1 (bassa, ambiguo), Type 382 (bassa).

**Esito per classe (conteggio per modello/gruppo di modelli di registro)**:

| Esito | Gruppi/modelli |
|---|---|
| Con dato di fonte di periodo/rpm (conf. media-alta) | E-3A (6 rpm), SPS-49 (6/12 rpm, 12 default), Roland MPDR-16 (60 rpm) |
| Con dato di fonte (conf. bassa-media) | Buk 9S18 (3-14 rpm; 2,5-18 s), Kub 1S91 (15/20 rpm), Gepard MPDR-12 (60 rpm), Tor 9S18 (1 s), Fregat-MA (6/12 rpm), Type 364 (30 rpm), 64N6E (6/12 rpm, non e' il radar del registro) |
| Dato dubbio/contraddittorio o di simulatore (conf. bassa) | SPS-67 (15/30 vs 2/4 rpm), SPY-1 (1 e 12 scan/min), AWG-9 (13-14 s), APG-68 (aneddotico), Type 382 |
| **Non applicabile** (motivo dichiarato) | Fire Dome 9S35, 1S31, 1A26, 9S36, Gun Dish/Gepard/Osa in inseguimento (inseguimento continuo, sez. 2); pod TVD (staring); Strela-10/Strela-1/Chaparral/M6 TVD (mirini); ricerca a vista (ZSU-57-2, M163: legge diversa); radar a fascio elettronico senza ricerca rotante (30N6, Mars-Passat, Type 346) per cui il periodo non e' 60/rpm |
| **Non trovato** | Osa Land Roll (rpm), Tunguska 1RL144 (rpm), Gun Dish (scansione di ricerca), 5N64S Big Bird, 30N6 (periodo di rivisita), APG-63/-70/-73, N019/N001, N011M (frame), E-2D, A-50, SPS-43/-52, navi sovietiche (Top Pair, Head Net-C, Strut Curve, Band Stand, Voskhod), Type 360/381, tempi di scoperta visiva in letteratura (rapporti DTIC esistenti non letti), IRST (non cercato), radar di superficie dei bombardieri (non cercati) |

**Non cercato (dichiarato)**: IRST degli aerei; radar di mappatura/superficie dei bombardieri; Type 093; il resto dei radar
di caccia minori (MiG-15/19/21/23/25/31, F-4E, F-5E, F-86, Mirage 2000, Viggen): i periodi di scansione dei radar d'epoca a
conical scan o a bassa tecnologia andrebbero cercati nei manuali (non reperiti).

**Dati piu' utili per primi, per il DES** (in ordine d'impatto sugli scenari):
1. **ZSU-23-4 Gun Dish** (12 scenari): il tipo di scansione della ricerca e il periodo di settore **non sono stati
   trovati**: serve un manuale tecnico RPK-2 / il TO della ZSU-23-4. Senza questo dato, il dwell dell'osservatore piu'
   usato (con la F-16 bersaglio) resta senza fonte (la legge si spegne, come previsto dalla Proposta).
2. **MiG-29S / F-16C / F-15C / A-10C** (gli aerei piu' presenti): tempo di frame dei radar di bordo; le fonti raggiunte
   non lo danno. Per un caccia il periodo dipende dal modo e il DES non modella i modi: decisione di design prima di cercare
   altro.
3. **9K35 Strela-10 / ZSU-57-2 / M163** (sensori ottici/a vista): non serve un dwell ma un **tempo di scoperta visiva**
   (DTIC ADA017599/ADA020657/ADA025823, da leggere via un percorso diverso da quello bloccato) e va deciso se il modello e'
   `min(1, permanenza/dwell)` o una legge cumulativa esponenziale (Koopman).
4. **Buk, Kub, Tor** (SAM a ricerca rotante): i valori ci sono ma di confidenza bassa-media; una fonte primaria (Jane's, manuale)
   chiuderebbe i dubbi (3-14 rpm vs 6,7/10/18 rpm; 15/20 rpm; 1 s).
5. **Navi**: SPS-49 (utilizzabile) e il valore ambiguo dell'SPY-1; per le navi sovietiche e cinesi mancano rpm di fonte.

**Tre punti da portare con se'** (riassunto per decisione): (i) il dwell esiste con dato di fonte pulito solo per E-3A,
SPS-49 e Roland; per Buk, Kub, Tor e Gepard c'e' un dato ma debole; (ii) per ZSU-23-4, Osa, Tunguska, S-300PS,
caccia con radar e navi sovietiche **non e' stato trovato nulla** di affidabile; (iii) per inseguimento, TVD e vista il dwell
**non e' applicabile** e non va forzato.

## 8. Fonti (abbreviazioni usate sopra)

Letti direttamente (a seconda mano, tramite riassunto):
- [W-ConScan] https://en.wikipedia.org/wiki/Conical_scanning ; [W-Monopulse] https://en.wikipedia.org/wiki/Monopulse_radar
- [W-ZSU234] https://en.wikipedia.org/wiki/ZSU-23-4_Shilka ; [W-Buk] https://en.wikipedia.org/wiki/9K37_Buk ; [W-Osa] https://en.wikipedia.org/wiki/9K33_Osa ; [W-Kub] https://en.wikipedia.org/wiki/2K12_Kub ; [W-Tor] https://en.wikipedia.org/wiki/9K330_Tor (titolo reale "Tor missile system")
- [APA-DKB] https://ausairpower.net/APA-Russian-SAM-Radars-DKB.html ; [APA-Kvadrat] https://ausairpower.net/APA-2K12-Kvadrat.html ; [APA-Strela10] https://www.ausairpower.net/APA-9K35-Strela-10.html ; (APA 9K37 Buk letta: nessun rpm)
- [RT-1S91] pagina armsnet che ricopia radartutorial karte011: https://armsnet.duckdns.org/equipment/833bf1fa-7791-493d-89da-08decb838d08 ; [Armsnet-9S18] https://armsnet.duckdns.org/equipment/fce0ad8d-2ca7-4677-2a24-08de7ebf1f0c
- [MP-MPDR16] https://www.militaryperiscope.com/weapons/electronics/ground-radars/mpdr-16/overview/ ; [MP-FlapLid] https://www.militaryperiscope.com/weapons/sensorselectronics/ground-radars/30n6-flap-lid/ ; [MP-LandRoll], [MP-9S18M1] (incipit)
- [TE-Gepard] https://tanks-encyclopedia.com/coldwar/bundeswehr/flakpanzer-1-gepard/
- [W-APG68] https://en.wikipedia.org/wiki/AN/APG-68 ; [W-APG66] .../AN/APG-66 ; [W-APG63] .../AN/APG-63 ; [W-APG73] .../AN/APG-73 ; [W-AWG9] .../AN/AWG-9 ; [W-MiG29] https://en.wikipedia.org/wiki/Mikoyan_MiG-29 ; [W-Bars] https://en.wikipedia.org/wiki/Bars_radar
- [W-E3] https://en.wikipedia.org/wiki/Boeing_E-3_Sentry ; [W-E2] https://en.wikipedia.org/wiki/Northrop_Grumman_E-2_Hawkeye ; [W-A50] https://en.wikipedia.org/wiki/Beriev_A-50
- [W-SPS49] https://en.wikipedia.org/wiki/AN/SPS-49 ; [W-SPS67] .../AN/SPS-67 ; [W-SPS43] .../AN/SPS-43 ; [W-SPS52] .../AN/SPS-52 ; [W-SPY1] https://en.wikipedia.org/wiki/SPY-1
- [W-T364] https://en.wikipedia.org/wiki/Type_364_radar ; [W-T382] .../Type_382_radar ; [W-T381] .../Type_381_radar ; [W-T360] .../Type_360_radar
- [FW-Bars] https://flyandwire.com/2020/09/09/back-to-basics-radar-elevation-bars-and-scan-azimuth/ (guida DCS) ; [WTP-Radar] https://www.whothatplane.com/learn/how-radar-works.html

Solo tramite snippet del motore di ricerca ("via ricerca", pagina non letta o non leggibile):
- [RT-9S18M] https://www.radartutorial.eu/19.kartei/02.surv/karte093.en.html ; [RT-1RL144] https://www.radartutorial.eu/19.kartei/04.battle/karte057.en.html ; [RT-64N6E] https://www.radartutorial.eu/19.kartei/06.missile/karte014.ru.html ; [RT-SPS67] https://www.radartutorial.eu/19.kartei/07.naval/karte036.en.html ; [RT-TopPlate] https://www.radartutorial.eu/19.kartei/07.naval/karte091.en.html
- [GS-9S18] https://www.globalsecurity.org/military/world/russia/9s18.htm (+ Army Recognition https://www.armyrecognition.com/focus-analysis-conflicts/army/conflicts-in-the-world/russia-ukraine-war-2022/ukrainian-forces-destroy-russian-buk-m1-detection-radar-alongside-full-system) ; [GS-HotShot] .../hot-shot.htm ; [GS-SA13] .../sa-13.htm
- [AR-Tor] https://www.armyrecognition.com/archives/archives-land-defense/land-defense-2024/russian-leaks-discover-how-russias-tor-m1-air-defense-system-counters-ukrainian-drones ; [CAV-S300] https://cavac.at/cavacopedia/S-300_missile_system
- [AC-Forum] https://army.ca/forums/threads/name-this-photo-the-afv-recognition-thread.48893/page-14 (forum, **bassa**) ; [Brickmania] https://www.brickmania.com/flakpanzer-gepard-self-propelled-anti-aircraft-gun/ ; [Deagel-Fregat] https://www.deagel.com/Sensor%20Systems/Fregat/a001879
- [AFT-E3] https://www.airforce-technology.com/?p=1518 ; [DM-E3] https://www.defensemirror.com/news/28543/U_S_A_F__Orders_Northrop_E_3_Sentry_AWACS_Surveillance_Radars
- [DCS-APG68] https://forum.dcs.world/topic/303895-agp-68v5-radar-azimuth-and-elevation-bar-issue ; [Key-AWG9] https://www.key.aero/forum/modern-military-aviation/90089-fighter-radars-and-rcss ; [HB-TWS] https://www.bilibili.com/read/cv111479/ (traduzione cinese del post di sviluppo Heatblur)
- [WT-1RL33] https://old-wiki.warthunder.com/ZSU-23-4 (gioco, non usare)
- [W-Litening] https://en.wikipedia.org/wiki/AN/AAQ-28_Litening ; [DU-Sniper] https://defense-update.com/?p=31120 ; [DRS-IBAS] https://www.leonardodrs.com/media/3295/ibas_datasheet.pdf ; [FAS-M6] https://man.fas.org/dod-101/sys/land/m6.htm
- [Koopman56] https://ideas.repec.org/a/inm/oropre/v4y1956i3p324-346.html ; [Koopman86] https://ideas.repec.org/a/inm/oropre/v34y1986i3p377-383.html ; DTIC (non letti, 403) https://apps.dtic.mil/sti/pdfs/ADA017599.pdf , https://apps.dtic.mil/sti/tr/pdf/ADA020657.pdf , https://apps.dtic.mil/sti/tr/pdf/ADA025823.pdf ; ASSURE https://assureuas.com/wp-content/uploads/2021/06/Appendix-A-ASSURE-A46-Literature-Review_v2.pdf

**Fonti piu' deboli usate**: forum (army.ca, DCS, key.aero), guide di simulatore (DCS, Falcon BMS), War Thunder wiki, mirror di
Wikipedia, snippet di ricerca di schede radartutorial non scaricabili, riassunto di Army Recognition su documenti trapelati.
