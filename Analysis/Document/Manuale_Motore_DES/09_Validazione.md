# Capitolo 8 — Validazione

Harness e test: `Test/Scenario_Fixtures.py` (fabbrica di scenari, non un modulo di test:
il nome non inizia con `Test_`), `Test/Test_Session_Validation.py` (determinismo + agnosticismo
come test di contratto), `Test/Test_Session_Scenarios.py` (S1-S9), `Test/
Test_Session_Scenarios_S10_S18.py` (S10-S18), `Test/Test_Session_Scenarios_S19.py` e
`Test/Test_Session_Scenarios_S19_Air_Defence.py` (S19, S19AD), `Test/Test_Session_Scenarios_S20.py` (S20) e
`Test/Test_Session_Scenarios_S21.py` (S21, S21R), `Test/Test_Session_Scenarios_S22.py` ... `_S27.py` (S22-S27, §8.10),
più lo strumento di non regressione `Test/Scenario_Baseline.py` (§8.7). Suite finale della Fase 7: **3371 test, OK
(skipped=5)** (wiki `decisions/virtual-session-engine-des`, sezione Fase 7). **Suite a `a784a9e7`: 4385 test, OK
(skipped=7)**; fotografia di non regressione: **918 esecuzioni** (§8.7, §8.10).

**Aggiornamento rispetto alla stesura iniziale**: le estensioni successive alla Fase 7 (selezione
arma dai registri, nebbia di guerra, scorta per modello d'arma, cannone di bordo, finestre di
rilascio delle bombe, volumi di rilevamento/intercettazione distinti, pianificatore d'attacco —
v. capitolo 4 §4.16-4.20 e capitolo 7 §7.6-7.9) hanno portato la suite a **3645 test, OK
(skipped=5)** al commit `6754bf1c` (2026-09-27), tutte nello stesso harness di questo capitolo. **Aggiornamento a `533cd1f5`** (2026-10-05): la suite è a
**3922 test, OK (skipped=7)** (messaggio del commit `533cd1f5`), con le estensioni del 2026-09-28/30 (soglia
di rottura stocastica, E(N), RWR, A6, dottrina di tiro, R-INT) e le fasi F0-F3 della Missione; i moduli di
test nuovi e le classi aggiunte sono elencati in §8.8. **Aggiornamento a `a784a9e7`** (2026-10-18): la suite è a **4385 test, OK (skipped=7)** (`F4_Differenze_Scenari.md`,
sezione G5, verificata dall'utente il 2026-10-18; i totali intermedi sono in §8.10), con le fasi F5 (presenza, attese,
`grounded` nel tempo), F6 (carburante per tratto, criteri di fine, bingo) e i passi G1-G5 del modello di bingo (riserva di
disimpegno, soglia e albero, consumo in ingaggio, episodi, ri-pianificazione, uscita di scena); sei scenari nuovi (S22-S27,
§8.10) e S5 portato a otto varianti. Il processo di non regressione (§8.7) è lo stesso. **Aggiornamento a `84a47670`** (2026-10-11): la suite è a
**4039 test, OK** (messaggio del commit `af2efbe6`, F4c; i commit di F4b, `a4d8acf0`, e della F4a, `951b0ee2`,
dichiaravano 3951 e 3929, con 7 test saltati; l'ultimo messaggio non ripete il numero dei saltati), con la fase
F4 della Missione (missione come unità d'ingaggio, dominio di coordinamento, difesa di salva per dominio,
postura continua), la riprogettazione dei test S3 e S5 e tre scenari nuovi (S20, S21, S21R: §8.9); i moduli e
le classi aggiunte sono in §8.8. Fra
i moduli di test aggiunti dall'aggiornamento a `6754bf1c` (2026-09-27): `Test/Test_Aircraft_Weapon_Data.py` (classe
`TestBombsReleaseField`, campo `release` del registro bombe), `Test/Test_Fire_Control.py`
(`TestFireControlOnboardGun`, cannone di bordo candidato; `TestFireControlBombRelease`, gittata e
tempo di caduta dalla balistica), `Test/Test_Air_Route_Manager.py` e
`Test/Test_Threat_AA_Factory.py` (volumi di rilevamento/intercettazione distinti,
`TestDetectionAndInterceptionVolumes`, `TestBuildDetectionThreat`, `TestBuildAirDefenseThreats`),
`Test/Test_Military.py` (`test_air_detection_threats_*`), e il nuovo
`Test/Test_Weapon_Delivery.py` (balistica e pianificazione del profilo d'attacco, classi
`TestReleaseWindows`/`TestBallistics`/`TestBombEngagementEstimate`/`TestPlanFeasibility`/
`TestPlanGeometry`/`TestPlanThreats`/`TestExposureRule`/`TestTransitAndRealAssets`).

## 8.1 `Test/Scenario_Fixtures.py` — la fabbrica di scenari

Costruisce con **oggetti reali** gli ingredienti comuni agli scenari: nessuna logica del motore
è duplicata (niente Pd, salve, danno, carburante) — ogni numero di un esito viene da
`Session_Simulator.run_session` e dai moduli che chiama (`Test/Scenario_Fixtures.py:1-11`).

Fornisce (`:13-43`): asset reali dai registri (`make_vehicle`, `make_aircraft`, `make_ship`, con
id sempre esplicito — `Asset.__init__` genererebbe altrimenti un suffisso casuale); forze
(`make_force`, `add_assets`, `build_force`); infrastrutture reali (`make_infrastructure`,
`make_structure`: `Production`/`Storage`/`Transport`/`Urban`, costruibili solo dal 2026-09-23 dopo
la correzione di 5 bug preesistenti nei loro costruttori, v. §8.4); rotte
(`straight_route`, `route_for`, `routes_for`, `:513-574`); **missioni** (`missions_for`, `:664-730`, dal
2026-10-05, v. sotto); un `fire_control` di riferimento (`make_fire_control`, §8.2);
esecuzione (`run(...)`, `Scenario.run(session_id)`, `combined_arms_scenario()`); letture
dell'esito (`losses_of`, `damage_by_source`, ...).

### Migrazione alle missioni (fase F3, 2026-10-05, `Test/Scenario_Fixtures.py:99-130`)

Dopo che `run_session` ha perso `routes`/`starts`/`speeds` (capitolo 6 §6.1), **ogni asset che prima riceveva
una rotta è ora asset di una `Mission`**; gli asset fermi (difese, siti SAM, blocchi in posizione) non sono
missioni: dalla fase F4c restano nella forza del loro blocco con la **postura continua** (unità di superficie
in difesa, tiro invariato; un *aereo* senza missione è a terra, ruolo `'parked'` della tabella di fuoco, sotto).
`missions_for(force, points, mission_type=..., target=...)` riproduce **esattamente** la geometria di
`routes_for`:

- una missione = asset di **un** blocco e di **un** dominio sulla stessa geometria. In F3 la velocità sugli
  archi divideva anche le missioni (in un blocco misto, es. carri M1A2 + M2 Bradley, i due modelli procedevano a
  velocità diverse e diventavano **due missioni dello stesso blocco**); **dalla F4a vale la regola A**
  (capitolo 6 §6.10): `missions_for` riunisce gli asset che differiscono *solo* per velocità in una missione la
  cui rotta di riferimento ha, tratto per tratto, la velocità **minima** fra quelle dei suoi asset
  (`_slowest_reference`, `Test/Scenario_Fixtures.py:639-653`). Gli offset di formazione sono quelli di F3 (la
  velocità non entra nell'offset): la geometria non cambia, cambia solo la velocità degli asset più veloci, che
  procedono al passo del più lento. Chi vuole velocità diverse chiama `missions_for` più volte con `only=`
  (missioni separate). Restano divisi in più missioni i blocchi con tipi di missione diversi (S7, S18, S19) o
  con geometria non riducibile a un offset (S19AD standoff: formazione rigida con virata);
- dentro una missione la rotta di riferimento è quella del primo asset (per id) e gli altri hanno l'offset di
  formazione che riproduce la loro rotta traslata; l'offset è accettato solo se `Mission_Adapter.asset_route`
  ridà gli **stessi punti** (confronto esatto), altrimenti l'asset ha una missione propria (succede con
  rotte che cambiano direzione: una traslata rigida non è un offset nella terna di marcia, capitolo 6 §6.10);
- **semplificazione di scenario dichiarata**: le rotte aeree degli scenari partono in volo (`start_mode` AIR) e
  finiscono sull'obiettivo o oltre, **senza rientro in base**; per non indebolire la validazione di `Mission`
  (D2.c: una missione aerea finisce con `LAND`) l'ultimo punto ha ruolo `LAND`. Il rientro vero (RTB) è delle
  fasi F5-F6.

Anche `Scenario` ha ora `missions` al posto di `routes` (`routes` resta come proprietà di sola lettura
derivata, `:921-925`) e `run(...)` accetta `missions=` (`:884-890`).

**Aggiunte della F4** (`Test/Scenario_Fixtures.py`):

- **ruolo `'parked'`** (`PARKED_ROLE`, `:792`; `role_of(asset, roles, grounded=False)`, `:795`): un aereo a terra
  è un bersaglio di superficie come `'structure'` (lo colpiscono `'ground'`, `'artillery'`, `'air'`, `'strike'`;
  mai `'sam'`, `'aaa'`, `'fighter'`, `'sead'`) e non spara mai. `make_fire_control` dichiara il parametro
  `target_grounded` (`:843`), quindi `role_of` lo classifica `'parked'` solo quando il risolutore glielo dice
  (capitolo 4 §4.4, §4.30);
- **letture dell'esito per forze d'ingaggio**: `force_outcome(outcome, force_id)` (`:987`) accetta un `mission_id`
  o l'id di un blocco con **una sola** forza d'ingaggio che ha combattuto, e solleva `ValueError` per un blocco con
  più missioni in combattimento (l'esito del blocco non è unico: chiedere quello della missione);
  `engagement_blocks(outcome)` (`:1008`) restituisce per ogni ingaggio i **blocchi** coinvolti (dal `block_id`
  degli esiti, con gli stessi valori attesi di prima della F4b) e `engagement_forces(outcome)` (`:1019`) gli id
  delle forze d'ingaggio (missioni). Le verifiche di struttura "quali blocchi combattono nello stesso ingaggio"
  leggono i blocchi, quelle sugli id di forza le missioni.

### Sensori dichiarati di test — lacuna dei registri documentata (`:45-58`)

I registri **non** dichiarano alcun sensore in modo `'ground'` per carri, corazzati e artiglieria
(portate nulle in tutti i record `Tank`/`Armored`/`Artillery_*` di `Vehicle_Data`), né per le navi.
Con i soli registri, due forze terrestri **non si vedono mai**: è un dato mancante, non un errore
del motore (`Mobile.detection_range` lo dichiara esplicitamente), ma oggi nessun chiamante di
produzione lo compensa. Per gli scenari si usa quindi un sensore dichiarato di test
(`declare_sensor`), un'iniezione esplicita e visibile in ogni scenario — non un'alterazione
silenziosa dei registri.

### `fire_control` di riferimento — una tabella di ruoli, non la selezione dell'arma (`:59-90`)

`make_fire_control` classifica tiratore e bersaglio in un **ruolo** (`'air'`, `'sea'`, `'sam'`/
`'aaa'`, `'artillery'`, `'ground'`, `'logistic'`, `'structure'`, più i ruoli di missione imposti
per id: `'fighter'`, `'strike'`, `'sead'`) e consulta una tabella `(ruolo tiratore, ruolo
bersaglio) -> ShotSpec | None`. Le `ShotSpec` sono **costanti di test dichiarate**, di ordine di
grandezza plausibile ma **non calibrate e non prese da una fonte**: gli scenari ne verificano
l'effetto qualitativo (chi perde di più, cosa accade prima), mai un numero assoluto.

## 8.2 Determinismo (`Test/Test_Session_Validation.py:72-131`)

`TestDeterminism` verifica su `combined_arms_scenario()` (la composizione di S1): stesso
`SessionOrder` + forze ricostruite identiche (stessi id, precondizione verificata
esplicitamente) → `SessionOutcome` identico, campo per campo e come oggetto intero (le dataclass
sono frozen e comparabili), **e** stato reale degli asset dopo l'applicazione identico
(`health`, `ammunition`, `fuel`). Accompagnato dal controllo di **non vacuità**: un `session_id`
diverso (quindi un seed diverso) deve cambiare gli eventi prodotti ma **non** la struttura
deterministica (le stesse componenti di forze in contatto, che dipendono solo dalla geometria,
non dal seed) — altrimenti l'uguaglianza del primo test potrebbe dipendere da un motore che
ignora il seed anziché da un motore davvero deterministico.

## 8.3 Agnosticismo come test di contratto (`Test/Test_Session_Validation.py:1-47`, `:134-373`)

Il vincolo "core indifferente al simulatore" (capitolo 1, §1.4) si formula come "cancellando
l'adapter DCS la campagna deve continuare a girare". A questo commit **non esiste alcun adapter
DCS** nell'albero Python: non c'è nulla da rimuovere. Il test è quindi un test di **contratto**,
in due parti:

**(a) Strutturale** (`TestAgnosticContractStructure`, `:188-237`): verificato con
`typing.get_type_hints` + AST-check, non a runtime. **Esteso nella fase F3** (§2.9 del capitolo 2):
`Operation`, `MissionOutcome` e `AssetMissionOutcome` sono fra i tipi della catena delle porte; gli enum di
dominio e i mapping sono tipi ammessi; la `Mission` è accettata come foglia composta (porta `DataType.Route`
e `AttackProfile`) e coperta da `Test_Mission_Types`, ma i **nomi dei campi** di tutti i tipi di
`Command/Mission_Types` sono comunque controllati contro il lessico del simulatore:

- ogni campo delle porte (`SessionOrder`, `SessionOutcome`, `ForceOutcome`, `DamageEvent`,
  `AmmunitionEvent`, `InterceptionEvent`, `FuelEvent`) è di tipo atomico (str/float/int/bool/None)
  o composto solo di tipi atomici e tipi della catena stessa (Union/tuple/mapping ricorsivamente,
  `_type_is_domain`, `:165-185`);
- nessun nome di campo contiene lessico del simulatore (`dcs`, `miz`, `unitid`, `unitname`,
  `groupid`, `groupname`, `airdrome`, `dictkey`, `missiontime`, `modeltime`, `lua` —
  `_SIMULATOR_WORDS`, `:155-156`);
- ogni campo `time`/`t_*` è `float` (mai un orologio del simulatore);
- i moduli del motore (`Session_Types`, `Session_Simulator`, `Engagement_Resolver`,
  `Contact_Scheduler`, `Damage_Model`, `Fuel_Model`, `Session_Rng`) non importano `lupa`,
  `zipfile`, `minizip`, né nulla con `'dcs'` nel nome, e non chiamano `timer.getTime`
  (l'orologio nativo di DCS/Lua).

**(b) Funzionale end-to-end** (`TestAgnosticEndToEnd`, `:262-373`): l'intera catena gira con dati
costruiti **solo** in Python (nessun `.miz`, nessun `dcs_unit_data`) e produce un
`SessionOutcome` completo (ingaggi, danni, munizioni, carburante tutti presenti); ogni id
presente nell'esito è un id di dominio noto (di blocco, di missione — i `mission_id` sono id di dominio
dalla F4b — o di asset costruiti dal core), mai un id di missione del simulatore; i campi controllati sono
`target_id`, `source_id`, `asset_id`, `force_id` e, dalla F4b, `block_id`; ogni `time` cade dentro `[t_start, t_end]` della sessione. Una
mini-campagna di **tre sessioni consecutive** sulle stesse forze verifica che lo stato passa solo
attraverso gli asset mutati (nessuno stato nascosto fuori dagli asset). Limite annotato nel test
stesso (`:281-285`): `run_session` non aggiorna `asset.position` a fine rotta (nessun movimento
fisico, v. capitolo 6 §6.5) — nelle sessioni successive le forze ripartono dalle posizioni
iniziali; non conta per verificare la concatenazione di salute/munizioni/carburante, ma è un
limite per una campagna vera (v. capitolo 9).

**Effetto della F4c sulla mini-campagna** (`F4_Differenze_Scenari.md`, sezione F4c): la seconda e la terza
sessione sono *senza missioni*, quindi i 2 A-10C di Blue-CAS, che prima restavano fermi **in volo** nella
posizione iniziale (x = −60 km, 3000 m) e sparavano, dalla F4c sono a terra (decisione 1) e non sparano più:
`S7-agn-2` passa da 2 colpi di Blue-CAS a 0 e Red-Line da `DISENGAGED` a `HELD`, `S7-agn-3` da 2 colpi a 0 e da 3
asset distrutti di Red-Line a 2. Sono le uniche due esecuzioni della fotografia con aerei fuori missione; l'utente
ha scelto di accettare il cambio (l'alternativa, dare a Blue-CAS una missione nelle sessioni 2-3, avrebbe
snaturato il test "senza missioni, forze ferme"). I test di `TestAgnosticEndToEnd` verificano la concatenazione
dello stato, non gli esiti, e passano.

Quando l'adapter DCS esisterà, questo stesso test diventerà eseguibile alla lettera; fino ad
allora è il suo equivalente verificabile (`Test/Test_Session_Validation.py:44-47`).

## 8.4 La batteria di scenari S1-S27

Origine: S1-S5 adattano le composizioni di forza dei documenti Lanchester ingeriti (**senza i
loro numeri**: solo composizione e domanda, v. wiki
`decisions/soglie-disingaggio-e-attrito-aggregato` §P3); S6-S11 sono definiti per questo
progetto per colmare le lacune di dominio/meccanismo che S1-S5 non toccano (navale, bersagli
non-militari, scala, fog-of-war, soglia di disingaggio, confine sessione DCS/sintetica); S12-S18
estendono la batteria (richiesta esplicita dell'utente) legandola alla classificazione reale di
`Block`/`mil_category` del progetto (C2, FARP, impianto `Production`, installazione navale,
prossimità `Urban`, scala gerarchica, rete `Transport` multi-nodo).

| Scenario | Classe di test | Cosa esercita |
|---|---|---|
| **S1** | `TestS1CombinedArmsWithCAS` | Armi combinate con CAS: corazzati+meccanizzati (con/senza A-10C) contro meccanizzata+artiglieria+AAA/VSHORAD in difesa. Verifica che il CAS sposti l'esito verso l'attaccante e che senza CAS prevalga la difesa. |
| **S2** | `TestS2PreliminarySEAD` | Missione SEAD prima dell'attacco principale contro un sito SAM (Buk). Due sessioni concatenate sugli stessi seed: senza SEAD lo strike attraversa il SAM intatto, con SEAD la seconda sessione eredita lo stato mutato dalla prima (test di concatenazione fra sessioni). |
| **S3** | `TestS3StealthVersusMass` | Pochi caccia "stealth" (4) contro molti convenzionali (8 F-15C), stesso modello per isolare il meccanismo: `detection_factor` degrada la Pd contro un bersaglio Blue. 20 repliche. **Riprogettato l'11 ottobre 2026** (§8.9): senza stealth si confronta la *frazione* di aerei persi, con stealth la differenza assoluta a coppie con una soglia statistica di 3 errori standard, e il rapporto di scambio migliora con lo stealth. |
| **S4** | `TestS4SAMAsThirdComponent` | Scontro terra-terra con un sito SAM (terza forza, `extra_forces`) che interviene contro il CAS di un lato. Verifica che il SAM riduca l'efficacia del CAS ed entri nello stesso ingaggio dello scontro terrestre. |
| **S5** | `TestS5DeepInterdictionThreeLayers` | Missione aerea profonda (4 F-15E) contro un bersaglio composito dietro 3 strati di difesa (lungo, medio, punto) su una rotta di 950 km. Verifica che gli strati ingaggino in ordine geometrico e che la missione raggiunga il bersaglio o sia fermata prima. 12 repliche, tre varianti (dottrina di default, ad oltranza, **«formazione resistente»**); **riprogettato l'11 ottobre 2026** (§8.9); **dal G4a/G4b otto varianti** (con la base aerea, episodi e uscita di scena spenti: §8.10). |
| **S6** | `TestS6CarrierGroupVersusCoastalDefence` | Gruppo da battaglia navale (CVN+CG+DDG) contro litorale difeso da terra e da mare. Esercita la fusione di finestre di contatto di dominio misto (aereo-veicolo, aereo-nave, nave-veicolo) nella stessa timeline. |
| **S7** | `TestS7LogisticInterdiction` | Attacco aereo contro un bersaglio **non militare** (`Block` generico `category='Logistic'`) con scorta di caccia. Verifica che il bersaglio non spari/intercetti mai ma riceva comunque un `ForceOutcome` e danno reale. |
| **S8** | `TestS8MultiFrontScale` | Decine di blocchi su più fronti (40 blocchi, 240 asset) — test di **scala**, non di correttezza tattica. Verifica che la potatura gerarchica scarti la maggioranza delle coppie in modo conservativo e che la sessione completi entro un limite di tempo. |
| **S9** | `TestS9PartialFogOfWar` | Stessa composizione di S1, con `detection_factor` degradato per il lato Blue. **Gap documentato**: il fog-of-war reale del progetto (`Region`/`Tactical_Analysis`, `recon_cp_snapshot`) non è collegato al motore di sessione — questo scenario esercita solo il punto di iniezione geometrico, non l'informazione C2 (v. capitolo 9). |
| **S10** | `TestS10DisengagementThreshold` | Scenario minimo costruito apposta: verifica che la dottrina di default (erosione 0.30, shock 0.20) faccia scattare `DISENGAGED` sia per erosione cumulata sia per shock di una singola salva, a metà di un ingaggio già in corso. |
| **S11** | `TestS11SessionBoundary` | Confine fra due `SessionOrder` consecutive sulle stesse istanze di forza: non è un test di combattimento, è il test end-to-end del contratto porte (v. anche §8.3). |
| **S12** | `TestS12C2Decapitation` | Colpo mirato contro un nodo C2 isolato (`mil_category='Command_&_Control_C2'`) con presidio minimo, più una forza di controllo lontana e fuori portata (verifica dell'isolamento). |
| **S13** | `TestS13ForwardFARPInterdiction` | Missione aerea contro un FARP: `Block` a composizione eterogenea (strutture — piazzole/elicotteri parcheggiati, serbatoio — più veicoli AD e di supporto). |
| **S14** | `TestS14StrategicBombingOfProduction` | Bombardamento di una centrale elettrica (`Production` reale, `sub_category='Power_Plant'`), non una `Military`. Verifica il ramo bersaglio-logistico del `fire_control` di riferimento. |
| **S15** | `TestS15UrbanProximityROEContract` | Una `Military` accanto a un'area `Urban` — test di **contratto**, non di modello: dimostra che un `fire_control` esterno può implementare una politica di non-ingaggio selettiva (ROE), non che il motore ha un modello di danno collaterale (non ce l'ha). |
| **S16** | `TestS16NavalInstallation` | Missione aeronavale contro un porto militare con navi ormeggiate (`Ship` senza rotta, ferme) e difesa costiera minima. |
| **S17** | `TestS17HierarchicalScaleSweep` | La composizione di S1 (senza CAS) ripetuta alle taglie gerarchiche di `MILITARY_CATEGORY['Ground_Base']` (Company→Division), con asset per Block scalati. Parametrizzazione, non scenario narrativo: verifica che il motore si risolva senza errori a ogni taglia. |
| **S18** | `TestS18TransportNetworkInterdiction` | Missione aerea scortata contro **più nodi fissi** di una rete `Transport` (ferrovia, rete elettrica, strada) lungo una rotta, con una CAP avversaria in pattugliamento. |
| **S19** | `TestS19RegistryFireControl` | Sessione con la `fire_control` **dei registri** (`make_registry_fire_control`, capitolo 4 §4.16) invece della tabella a ruoli: 2 A-10C, 2 F-16C CAP e 1 B-52H in transito a 3000 m su una difesa rossa (Buk, Strela-10, Shilka, 2 BMP-2); dottrina ad oltranza. Verifica riproducibilità, armi reali del registro del tiratore, solo armi con righe aeree sugli aerei e mai SAM/AAM sulla superficie, filtro di quota (l'AZP-23, tetto 1500 m, non colpisce aerei a 3000 m), fuoco prodotto, controllo di portata. |
| **S19AD** | `TestS19AirDefenceAllocation` | Allocazione della difesa aerea fra intercettazione e tiro sul lanciatore (A6, capitolo 4 §4.24): 3 BMP-2 con una difesa a corto raggio, 1-4 A-10C con i soli AGM-65D, quattro varianti (Strela-10 in sorvolo, Strela-10 in standoff, Tor arretrato, Tor avanzato). Esito qualitativo, mai numerico. Nella variante standoff i 4 A-10C sono 4 missioni dello stesso blocco: dalla F4b+ condividono ripartizione del fuoco e saturazione nel dominio (test `test_standoff_missions_share_the_fire`, §8.9). |
| **S20** | `TestS20TwoMissionsOfOneBlock` | Due missioni dello stesso blocco ingaggiano e disingaggiano separatamente (F4b, capitolo 4 §4.27): la composizione di S1 senza CAS, con Blue-Armor in due missioni d'attacco sulla stessa rotta ('Blue-Armor:Tanks', 3 M1A2; 'Blue-Armor:IFV', 2 M2) contro la stessa linea Red; variante 'single' con una sola missione. 6 seed (§8.9). |
| **S21** | `TestS21ParkedAircraftStrike` | Attacco a una base con aerei parcheggiati (F4c, capitolo 4 §4.30), tabella a ruoli: Red-Airbase (4 MiG-29S sul piazzale, Strela-10, Shilka, nessuna missione) contro Blue-Strike (4 F-16C in missione Strike, sorvolo a 3000 m); variante di controllo senza aerei. 8 seed (§8.9). |
| **S21R** | `TestS21RParkedAircraftRegistry` | Come S21 con la `fire_control` dei **registri**: Red-Apron (4 MiG-29S a terra, un blocco di soli bersagli passivi) + Red-AD (Strela-10 + Shilka) contro 2 A-10C 'Maverick/Gun CAS'. 6 seed (§8.9). |
| **S22** | `TestS22E1FinishedMissionStaysEngageable`, `TestS22E3LateDepartureIsPresent`, `TestS22AircraftOnTheGround` | Presenza fuori dalla rotta (F5-B): unità di terra ferme dopo l'arrivo e prima della partenza, aerei a terra fino al decollo e dopo l'atterraggio su una base vera (capitolo 6 §6.15). 72 esecuzioni (§8.10). |
| **S23** | `TestS23CapOrbit`, `TestS23GroundHold`, `TestS23TotPerMission` | Azione WAIT (orbita di una CAP, sosta di un carro), **TOT per missione** nella stessa Operazione, ETA effettive (F5-C, capitolo 6 §6.16). 80 esecuzioni (§8.10). |
| **S24** | `TestS24DryTank`, `TestS24DryAircraft`, `TestS24OrbitExhaustion` | Carburante per tratto, esaurimento a monte, planata e perdita dell'aereo a secco (F6-A, capitolo 6 §6.17). 88 esecuzioni (§8.10). |
| **S25** | `TestS25Winchester`, `TestS25MaxDuration`, `TestS25DestroyedPosture`, `TestS25DamageThreshold`, `TestS25TargetDestroyed` | Criteri di fine attività, stato di missione, postura `destroyed` (F6-B1, capitolo 6 §6.18). 112 esecuzioni (§8.10). |
| **S26** | `TestS26Bingo` | Il bingo nel modello finale G1-G4 e la controprova di ogni interruttore (capitolo 6 §6.19-6.20). 96 esecuzioni (§8.10). |
| **S27** | `TestS27DoubleEngagement` | Doppio ingaggio dello stesso aereo: due consumi d'ingaggio, ri-pianificazione dopo ciascun episodio, bingo dopo il secondo con rientro sulla base alternativa (G5). 40 esecuzioni (§8.10). |

Tutti gli scenari condividono la stessa regola: si prende la composizione delle forze e la
domanda che pongono, mai coefficienti o esiti numerici precalcolati — per S6-S19 la domanda è
"il meccanismo X del motore si comporta correttamente", non un risultato storico o di dominio da
riprodurre (wiki `decisions/soglie-disingaggio-e-attrito-aggregato` §P3).

## 8.5 Bug trovati durante la Fase 7

Cinque bug preesistenti, mai istanziati con successo in produzione (zero rischio di regressione),
corretti durante la costruzione della batteria S12-S18: costruttori rotti da sempre di
`Transport`/`Storage`/`Urban`/`Production`/`Structure`, e `Block.set_asset` che rifiutava ogni
sottoclasse di `Asset` (confrontava il nome classe esatto invece di usare `isinstance`) — wiki
`decisions/virtual-session-engine-des`, sezione Fase 7.

## 8.6 Scenari modificati o aggiunti dopo `6754bf1c`

- **S19** (`Test_Session_Scenarios_S19.py`, 7 test, `:119-174`): era già nella batteria ma non descritto nelle
  stesure precedenti del manuale; dalla F3 le rotte degli aerei sono tre missioni dello stesso blocco
  (CAS, scorta, bombardamento: tre modelli a velocità diverse), con bersagli `group_target`. **Dalla F4b**
  ciascuna è una forza d'ingaggio: la missione di Strike, un solo B-52H, è `DESTROYED` alla prima perdita
  (`S19-2/run`: prima il blocco di 5 aerei restava `HELD`), e gli esiti di forza hanno il `mission_id` come
  `force_id` (capitolo 4 §4.27).
- **S19AD** (`Test_Session_Scenarios_S19_Air_Defence.py`, commit `aedd7fa5`): scenario **persistente** della
  riproduzione della proposta SAM (`Proposta_Regole_Allocazione_SAM.md` §1.1 e §7.8). Sette test
  (`:136-224`): i Maverick sono lanciati; lo Strela non intercetta mai (regola D); lo Strela spara i
  missili agli aerei in sorvolo e li conserva in standoff; **le quattro missioni dello standoff si dividono il
  fuoco** (`test_standoff_missions_share_the_fire`, F4b+: 8-10 Maverick lanciati e Red-Line distrutta, Strela
  compreso, in tutti e 6 i seed; senza il dominio di coordinamento erano 16 e lo Strela restava in piedi);
  il Tor arretrato intercetta lanci da fuori zona; il Tor avanzato spara ai lanciatori. Due stand-in di A4 (filtro armi per missione, rimandato alla
  F7): `maverick_only_fire_control` (l'A-10C usa solo AGM-65D, altrimenti il criterio Pk/costo sceglierebbe la
  Mk-82AIR, non intercettabile) e `ifv_only` (gli aerei attaccano solo i BMP-2). Con lo standoff ogni A-10C ha
  una missione propria (la rotta cambia direzione, §8.1): dalla F4b l'ingaggio e il disingaggio sono per
  missione, dalla F4b+ la ripartizione del fuoco è per dominio (stesso blocco, capitolo 4 §4.28).
- **S10** verifica il meccanismo del disingaggio con soglie **fisse** (`FIXED_THRESHOLDS`, `Test_Session_Scenarios_S10_S18.py:117`)
  e ha in più un caso DISPERSIONE con la dottrina di default (soglia di rottura stocastica, capitolo 4 §4.21);
  S5 verifica la distribuzione degli esiti; il docstring di S1 descrive la ritirata di Red con il nuovo modello.
- **S11, S13** e **S1 con CAS** hanno cambiato esito o composizione per la regola D (capitolo 4 §4.24):
  S13, il FARP con Shilka + Strela-10 non ha più intercettori; S11, difesa sostituita con Gepard + Tor perché
  le verifiche sulle scorte d'intercettazione avessero casi; S1 con CAS, i Maverick non sono più intercettati
  (`Proposta_Dati_Anti_Missile.md` §6).

## 8.7 Lo strumento di non regressione: `Test/Scenario_Baseline.py` (fase F0, commit `d3af6980`; esteso da F4a a G5)

Dalla fase F3 la porta di sessione cambia e servono **numeri** per dimostrare che, a parità di input, il motore
produce la stessa storia (`Piano_Implementazione_Missione.md`, §0 punto 2 e Fase 0). `Scenario_Baseline.py`
(901 righe a `a784a9e7`, 693 a `84a47670`, 590 a `533cd1f5`; **fuori** dalla discovery della suite: il nome non comincia con
`Test_`) esegue gli scenari di sessione esistenti, riassume ogni `SessionOutcome` in una forma deterministica e la
salva su JSON, oppure la confronta con una fotografia salvata.

**Come trova gli scenari: riuso, non duplicazione.** La tabella `UNITS` (`:234-345`) elenca le "unità" dei
test: per le classi di scenario (S1-S21, S19AD, S21R, validazione) esegue il loro `setUpClass`, che costruisce le
forze con `Scenario_Fixtures` e lancia tutte le repliche e varianti usate dai test; per
`Test_Session_Simulator` (nessun `setUpClass`) un elenco scelto di **metodi** di test (`ORC-*`). Le unità S21 e
S21R sono messe **in coda** alla tabella (nomi stabili: non spostano le chiavi delle altre). Durante
l'esecuzione `Session_Simulator.run_session` è sostituita da un registratore (`_Recorder`, `:550-561`) che chiama
l'originale e poi riassume l'esito **e** lo stato reale degli asset (letto subito dopo la chiamata: in S11 e
nella mini-campagna la sessione successiva muta di nuovo le stesse istanze). Le asserzioni dei test non sono
eseguite per le classi di scenario; per i metodi un'asserzione fallita è segnalata su stderr ma non impedisce la
registrazione.

**Nomi stabili**: chiave `<scenario>/<session_id>[/<variante>]`; la variante è l'indice di occorrenza dello
stesso `session_id` nell'unità, tradotto in un nome leggibile dalla tabella (es. `with_cas`/`without_cas` per
S1; `default`/`press_on`/`resistant` per S5; `split`/`single` per S20; `parked`/`control` per S21). Se un
`setUpClass` cambia l'ordine delle varianti, le chiavi cambiano: va aggiornata la tabella.

**Cosa registra** (`summarize_run`, `:446-545`): intervallo della sessione, forze dei due lati e parametri di
chiamata riconoscibili, esiti di forza per ingaggio (con tempi, perdite, erosione, shock, soglia e, dalla F4b,
il `block_id` quando c'è), stato finale per asset (salute, operativo, distrutto, munizioni, scorta per arma,
intercettori, carburante), munizioni consumate per asset e per arma, intercettazioni per asset e per arma,
eventi di carburante, conteggi (salve, intercettazioni, danni, distruzioni) e le liste complete degli eventi.
**Dalla F4b la voce `force_outcomes` è chiavata per blocco** (gli esiti delle sue forze d'ingaggio, nell'ordine
degli ingaggi, `block_id or force_id`): con una missione per blocco ha la stessa forma di prima, e il confronto con
le fotografie precedenti resta possibile. I float sono arrotondati a 6 decimali
(`ROUND_DIGITS`, `:188`; `-0.0` normalizzato, `norm`, `:366-390`), le chiavi ordinate: **due catture dello stesso
codice sono identiche byte per byte**. `FORMAT_VERSION = 1` (`:187`).

**Parametri di chiamata dopo la F3**: `run_session` non ha più `routes`; perché la fotografia della Fase 0 resti
confrontabile, la voce `call.parameters.routes` è **ricostruita dalle missioni** (`Mission_Adapter.mission_routes`,
`_call_parameters`, `:419-443`), e una lista vuota equivale all'assenza della voce (`_without_empty_routes`,
`:685-693`).

**Uso** (dalla radice del repository, con l'interprete della macchina):

```
python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --capture out.json
python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
    --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json
python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
    --compare <a.json> --against <b.json> --summary
```

`--only <regex>` limita il confronto a unità o chiavi; `--compare a.json --against b.json` confronta due file
già catturati senza eseguire nulla. `compare` (`:725-773`) segnala `ERROR`, `MISSING`, `NEW` e `DIFF` (con al più
20 righe di differenza per esecuzione). **`--summary` (dalla F4a)** sostituisce l'elenco grezzo con un riepilogo
leggibile per esecuzione (`summarize_differences`, `:817-845`, che usa `run_digest`, `:776-814`): per ogni
esecuzione che differisce, le sole grandezze cambiate come `vecchio -> nuovo` — esito per forza (e, per i blocchi
con più forze d'ingaggio, l'esito di ciascuna: `<mission_id>.mission_outcome`), asset distrutti, colpi,
intercettazioni, carburante e fine del movimento, istante del primo colpo e del primo danno — poi l'elenco delle
esecuzioni invariate. Non cambia il formato della fotografia; si può usare solo con `--compare`. Codice d'uscita
(`main`, `:848-897`): 0 identiche, 1 differenze o errori di unità, 2 uso errato.

**Opzione `--ignore KEY`** (dalla F5-B) esclude dal confronto una voce di primo livello: `--ignore postures` (la sola
postura nell'esito, F5-B), `--ignore actual_etas` (le ETA effettive, F5-C), `--ignore fuel_events` (F6-A: la voce `fuel`
e i conteggi `counts.fuel_events`/`counts.fuel_exhausted`, cioè la sola *forma* degli eventi di carburante; il carburante
finale per asset resta nel confronto, quindi un cambio di sostanza resta visibile). Serve ad attribuire le differenze a una
sola causa. **Voci nuove del riassunto**: `postures` (F5-B, se l'esito le porta) e `actual_etas` (F5-C, `{mission_id: [ETA |
None]}`, solo se l'esito porta esiti di missione); le fasi F6-B1, F6-B2, G1-G5 **non** aggiungono voci (lo stato di
missione, i motivi di fine per asset e `crew_recovered` sono nell'esito di missione, che la fotografia non registra: si
verificano nei test, S25-S27, e con catture estese fuori dal repository). Il G3 aggiunge solo eventi `FuelEvent` con
`regime` `'engagement'` nella voce `fuel`; il G4a una voce in `engagements` per episodio.

**La fotografia di riferimento** è `Test/baseline/scenario_baseline.json` (**918 esecuzioni** a `a784a9e7`, contate sul
file; chiavi `errors`/`meta`/`runs`, `errors` vuoto; 370 a `84a47670`). Ne è stata fatta la cattura iniziale su una copia
isolata di `18a772d6` (292 esecuzioni, identica in due catture separate); è stata **rigenerata più volte**, sempre dopo un
confronto spiegato e con due catture consecutive identiche (determinismo). La storia, dal documento delle differenze
`Analysis/Document/F4_Differenze_Scenari.md` (le righe da F5-A in poi sono nuove di questo aggiornamento; le esecuzioni
sono quelle della fotografia **installata** nel commit indicato, come risulta da `git log` sul file):

| Passo | Commit | Esecuzioni | Esito del confronto con la fotografia precedente |
|---|---|---|---|
| F0, F2, F3 | `d3af6980`, `4e18d7d8`, `533cd1f5` | 292 | F2 e F3: **292 identiche** (nessun cambio di comportamento, solo tipi e porta) |
| F4a, regola A | `951b0ee2` | 292 | 90 cambiate, **nessun esito di forza diverso**: i Bradley procedono a 55 invece di 56 km/h (tempo di arrivo +12 s su S1) e, in poche esecuzioni, cambiano istanti e asset colpiti; rigenerata |
| F4b, missione = forza | `a4d8acf0` | 328 (+36: S20 ×12, S3 ×20, S5 ×4) | 270 delle 292 coincidono *byte per byte* con F4a una volta riportato l'RNG agli id di blocco (cambia solo lo stream); 22 cambiano anche nel comportamento (blocchi con più missioni: S7, S18 `network`, S19, S19AD standoff); rigenerata |
| F4b+, dominio | `098671d7` | 328 | 8 cambiate: S19AD standoff (6, decisione 6) e S20 'split' (2, decisione 7); rigenerata |
| F4b++, difesa di dominio | `e6f59d21` | 328 | **328 identiche**: nessuno scenario esercita il caso; non rigenerata |
| S3/S5 riprogettati | `8bf7b11f` | 348 (+20: S5 ×20) | **328 identiche** + 20 nuove; il motore non è toccato |
| F4c, postura continua | `af2efbe6` | 370 (+22: S21 ×16, S21R ×6) | 346 identiche, **2 cambiate** (`VAL-agn/S7-agn-2` e `S7-agn-3`: A-10C senza missione ora a terra), cambio accettato dall'utente; rigenerata |
| F5-A, `grounded` nel tempo | `e723e82a` | 370 | **370 identiche**; non rigenerata (cambia la forma, non i dati) |
| F5-B, presenza e postura | `90f2d4de` | 442 (+72: S22) | storia: 368 identiche, **2 cambiate** (S6-0, S6-2: il gruppo navale resta dopo l'arrivo), accettate dall'utente il 2026-10-12; in tutte le 370 la voce `postures` è nuova; rigenerata |
| F5-C, attese, TOT | `4da618b1` | 522 (+80: S23) | storia: **442 identiche**; la voce `actual_etas` è nuova in 401; rigenerata. Rifatto il TOT per missione (`03d77640`): in S23-TOT 8 rimosse, 16 cambiate, 8 nuove, le altre 498 identiche; ancora 522 |
| F6-A, carburante per tratto | `00b6b531` | 610 (+88: S24) | storia: **522 identiche**; 126 cambiate nel carburante (88 solo nella *forma* degli eventi, 32 nel consumo delle attese, 6 per un arrotondamento all'ultima cifra); accettate il 2026-10-12; rigenerata |
| F6-B1, fine di attività | `15ac3d3d` | 722 (+112: S25) | storia ed esiti di missione: **610 identiche**; 429 cambiate nella sola voce `postures` (1431 asset distrutti passano a `destroyed`); rigenerata |
| F6-B2, bingo | `6b1b7225` | 722 | **722 identiche** con S24-GLIDE che dichiara `bingo=False`; le 40 esecuzioni nuove di S26 non sono installate in questo commit; con il bingo di default cambierebbero 24 esecuzioni di S24-GLIDE (F6-B3 aperto) |
| F6-B2bis, ritroso (+G1) | `96942ca7` | 770 (+48: S26 rifatto) | rientro a ritroso con la regola 1,2; installata |
| G2, soglia e albero | `e5465b31` | 794 | di 770: 762 identiche, **8 cambiate** (S26 'bingo', carburante di test 0,27), 24 nuove; approvato il 2026-10-16 |
| G3, consumo in ingaggio | `20f0e0db` | 802 (+8) | di 794: 372 identiche, **422 cambiate nelle sole voci di carburante** (verificato chiave per chiave), 8 nuove; approvato il 2026-10-17 |
| G4a + G4b + uscita di scena | `9de461e0` | 878 (+76) | di 802: **637 identiche, 165 cambiate** (40 per gli episodi: S5 ×36, S6 ×4; 16 per la ri-pianificazione per carburante; 109 per l'uscita di scena), 76 nuove; approvato il 2026-10-17 |
| G5, S26 riorganizzato + S27 | `6e7a9b81` | 918 (+40: S27) | di 878: **878 identiche** (S26: 96 su 96), 0 cambiate, 40 nuove; il motore non è toccato; approvato il 2026-10-18 |

**Il processo di non regressione, come applicato dalla F4** (ogni passo dichiara la propria differenza prima di
essere committato): (1) la fotografia *prima* del passo viene ricontrollata **identica** al codice di partenza;
(2) si modifica il codice; (3) si confronta con `--compare ... --against ... --summary` per vedere cosa cambia in
ogni esecuzione; (4) le differenze sono **attribuite alla loro causa** con catture di controllo su copie del
codice con un interruttore per ciascuna causa (solo misura, non nel repository: ad esempio, per la F4b, l'RNG
riportato agli id di blocco; per il dominio, la percezione per forza, le componenti non unite e i lanciatori per
forza); (5) le differenze sono documentate con la loro spiegazione fisica in `F4_Differenze_Scenari.md`; (6) solo
allora la fotografia è rigenerata (`--capture` nel percorso standard). Una differenza è ammessa solo se la fase la
prevede e il documento la spiega; il piano prevedeva una fotografia identica per la F4c, e il cambio di
`VAL-agn` è stato quindi sottoposto all'utente prima di rigenerare.

## 8.8 Test aggiunti dopo `6754bf1c` (per modulo; per quelli dopo `84a47670` v. §8.10)

| Modulo di test | Cosa copre |
|---|---|
| `Test_Mission_Types.py` (nuovo, 838 righe) | tipi della Missione: `TestTarget`, `TestStartCondition`, `TestMissionAction`, `TestMissionWaypoint`, `TestMissionAsset`, `TestEndCriteria`, `TestMissionRules`, `TestMissionValid`/`Invalid`, `TestRouteWaypoints`, `TestCheckMissionAssets`, `TestOperation`, `TestAssetMissionOutcome`, `TestMissionOutcome` |
| `Test_Mission_Adapter.py` (nuovo) | `TestZeroOffsetIdentity`, `TestFormationOffset`, `TestSpeeds`, `TestStart`, `TestSessionMovements` (capitolo 6 §6.10); dalla F4: `TestRuleASlowestSpeed` (regola A), `TestMissionForce` (vista di missione e vista residua, `can_disengage`, interceptor ristretti), `TestContinuousPosture` (postura per classe, vista residua mista, `grounded_assets`, nessuna mutazione), `TestCoordinationDomains` (stesso blocco, stessa Operazione, transitività, lati separati, determinismo, accettazione da parte del risolutore) (capitolo 6 §6.12-6.14) |
| `Test_Session_Types.py` | `TestSessionOrderMissions`, `TestSessionOutcomeMissions` (capitolo 2 §2.2-2.3) |
| `Test_Context.py` | tassonomia dei tipi di missione, tabelle di categoria e posture, rename `Retreat` |
| `Test_Air_Defense_Efficacy.py` (nuovo) | `TestExpectedKills`, `TestSharedDirector`, `TestDirectorsFromTheRegistry`, `TestSamCategoryAndRwr`, `TestRwrClassThreat`, `TestRwrTable` (completezza della tabella RWR) |
| `Test_Doctrine.py` | `TestBreakpointParameters`, `TestFireDoctrine` |
| `Test_Engagement_Resolver.py` | `TestStochasticBreakpoint`, `TestAirForceRatio`, `TestRwrPerception`, `TestRwrClassThreat`, `TestFireDoctrine`, `TestLauncherInsideInterceptionZone` (L1), `TestLauncherPriority` (L2/L3), `TestInterceptionReaction` (R-INT), con i 19 test esistenti portati a `REACTION_TOF = 20 s`; dalla F4: `TestCoordinationDomainFire` (saturazione dall'altra forza, attesa, ripartizione, tetto per tiratore, mappa identità, nessuna estrazione in più, lanciatori sul dominio, lati, tipi), `TestCoordinationDomainPerception` (fuoco con risposta e rapporto percepito da un rilevamento della gemella, stesse estrazioni, nessun cueing), `TestCoordinationDomainSalvoDefence` (scorta del dominio, regressione senza mappa, lancio dentro il V_I, scorta senza tempo di reagire, scorta scalata, canali non contati due volte nello stesso istante, ordine indipendente dalle forze), `TestGroundedAircraft`, `TestGroundedForceDisengagement`, `TestGroundedTargetIsASurfaceLauncherTarget` (§4.30) |
| `Test_Session_Simulator.py` | flusso separato della tempra (`test_temper_stream_is_distinct_and_order_independent`), `TestMissions` (missioni nell'orchestratore, esito di prima forma); dalla F4: regola A (`test_mission_faster_than_its_slowest_asset_raises`, `test_unknown_max_speed_does_not_block`), `TestMissionAsEngagementUnit` (stream chiavati per `mission_id`, due missioni = due forze, `committed` per blocco applicato per missione, vista residua con l'id del blocco, mappa dei domini passata a ogni ingaggio, Operazione fra blocchi diversi in una sola run, insieme `grounded` passato a scheduler e risolutore, postura della vista residua, `mission_id` uguale a un id di blocco rifiutato), componenti unite per dominio |
| `Test_Contact_Scheduler.py` | `TestGroundedAircraftRanges` (modo 'ground' per il bersaglio a terra, nessuna portata come osservatore, default invariato, `schedule_contacts(grounded=...)`) (capitolo 3 §3.5-3.6) |
| `Test_Fire_Control.py` | `TestFireControlGroundedAircraft` (chiave 'Soft', tabella dei tipi parcheggiati, SAM e AAM esclusi, righe 'Soft' delle armi CAS, gittata della bomba dalla quota reale, estensione dichiarata) (capitolo 4 §4.30) |
| `Test_Session_Scenarios.py`, `_S10_S18.py`, `_S19.py`, `_S19_Air_Defence.py` | asserzioni sugli id di forza adeguate (dalla F4b l'id di forza è il `mission_id`; le verifiche di struttura leggono i blocchi con `engagement_blocks`); S3/S5 riprogettati (§8.9); S19AD: `test_standoff_missions_share_the_fire` |
| `Test_Session_Scenarios_S20.py`, `Test_Session_Scenarios_S21.py` (nuovi) | S20, S21, S21R (§8.9) |
| `Test_Session_Validation.py` | contratto di agnosticismo esteso alle porte della Missione (§8.3); `mission_id` come id di dominio ammessi nell'esito |
| `Test_Mobile.py`, `Test_Military.py`, `Test_Aircraft*.py` | capacità `Anti_Missile`, ordine F, CIWS, task di supporto, dati delle armi aggiunte |

## 8.9 Scenari e verifiche della fase F4 (2026-10-05/11)

> **Nota (2026-10-18).** Le misure di S3 e S5 riportate in questa sezione sono quelle della riprogettazione dell'11 ottobre
> (fotografia a 348 esecuzioni). Dopo i passi G4a e G4b (episodi, ri-pianificazione, uscita di scena) alcune sono cambiate —
> per S5 in modo sostanziale: le nuove misure e le varianti aggiunte sono in §8.10.

Le misure qui riportate vengono da `Analysis/Document/F4_Differenze_Scenari.md` e dai docstring dei moduli di
test; i test asseriscono sempre **proprietà qualitative o statistiche con soglie dichiarate**, mai un numero
calibrato.

**S20 — due missioni dello stesso blocco** (`Test_Session_Scenarios_S20.py`, F4b). Criterio "Fatto quando" della
F4b: *un nuovo scenario con due missioni dello stesso blocco mostra disingaggi indipendenti*. Composizione di S1
senza CAS (Blue-Armor: 3 M1A2 + 2 M2 contro la linea ferma Red-Line con 3 BMP-2, obice 2S19-Msta, Shilka,
Strela-10), fire control a ruoli di test, 6 seed, due varianti con la stessa geometria: 'split' (due missioni
d'attacco sulla stessa rotta, 'Blue-Armor:Tanks' e 'Blue-Armor:IFV') e 'single' (una missione, come S1).
Verifiche (sei test): nella variante 'split' il blocco combatte come due forze d'ingaggio, ciascuna con il proprio
`ForceOutcome`; una forza rotta non lancia più salve; **le missioni si rompono indipendentemente** e in almeno un
seed gli asset di una sparano dopo il disingaggio dell'altra; con una missione, dopo la rottura nessun asset del
blocco spara più. Misura: nella variante divisa le due missioni finiscono diversamente in 5 seed su 6 (es. S20-0:
Tanks `DISENGAGED` a 231,9 s, IFV continua a sparare fino a 318,7 s e disingaggia a 319,0 s; S20-5: Tanks
`DISENGAGED` a 294,4 s, IFV `HELD` e Red-Line rompe a 319,3 s), e in 4 seed gli asset di una missione sparano dopo
il disingaggio dell'altra. Con il dominio di coordinamento (F4b+) cambiano solo grandezze fini in due seed
(S20-1, S20-3: rapporto percepito e soglia di rottura di 'Blue-Armor:IFV', che ora percepisce i nemici rilevati
dai carri; gli esiti non cambiano).

**S21 / S21R — aerei parcheggiati** (`Test_Session_Scenarios_S21.py`, F4c). Criterio "Fatto quando" della
Fase 4: *un nuovo scenario con aerei parcheggiati mostra che sono colpibili*.

- **S21** (tabella a ruoli, 8 seed, varianti 'parked' e 'control'): Red-Airbase (`Military` 'Airbase' senza
  missioni, mista: 4 MiG-29S sul piazzale con loadout 'CAP', Strela-10, Shilka) attaccata da Blue-Strike (4
  F-16C 'Strike', missione Strike in sorvolo a 3000 m); controllo: la stessa base senza aerei. Misura: 21 MiG-29S
  su 32 distrutti (0,66; per seed 3, 2, 3, 3, 3, 3, 1, 3 su 4). In ogni seed i MiG-29S non sparano, non
  intercettano, non infliggono danno; sono colpiti solo dall'arma aria-suolo dello strike (`'test:agm'`); le
  difese colpiscono solo gli F-16C; la base perde 4 asset su 6 ma resta `HELD` (prima della F4c l'erosione 4/6
  l'avrebbe fatta disingaggiare e gli aerei sarebbero diventati irraggiungibili). Nel controllo lo strike non
  spara mai (nessun bersaglio di superficie che il ruolo 'strike' possa ingaggiare).
- **S21R** (fire control dei registri, 6 seed): Red-Apron (4 MiG-29S, un blocco di soli aerei a terra) + Red-AD
  (Strela-10 + Shilka), Blue-CAS 2 A-10C 'Maverick/Gun CAS'. Misura: MiG-29S distrutti 4, 4, 4, 4, 3, 4 (23 su
  24); armi sui parcheggiati: AGM-65D e Mk-82AIR (riga 'Soft'), mai l'AIM-9M; Red-Apron `DESTROYED` in 5 seed,
  `HELD` in 1, mai `DISENGAGED`; Red-AD distrutto in tutti i seed (la fire control dei registri non ha ruoli: gli
  A-10C attaccano anche le difese); Blue-CAS perde 0-2 aerei.
- **Asserzioni**: invarianti per replica (nessun colpo, intercettazione o danno dai parcheggiati; bersagli delle
  difese solo Blue; danni sui parcheggiati solo da `'test:agm'` in S21 o da armi non AAM in S21R; Red-Airbase e
  Red-Apron mai `DISENGAGED`; controllo senza colpi Blue, variante 'parked' con colpi Blue in ogni seed) più una
  frazione aggregata di distruzione `>= MIN_DESTROYED_FRACTION = 0,5` (soglia di test dichiarata, non tarata,
  circa due deviazioni standard sotto la misura).

**S3 e S5 riprogettati** (`Test_Session_Scenarios.py`, 2026-10-11, commit `8bf7b11f`, solo test e docstring: il
motore non è toccato). Dalla F4b i due test passavano solo aumentando le repliche, perché misuravano una metrica
sbagliata (S3) o un evento raro (S5). Le misure vengono da 40 seed (S3) e 24 seed (S5), con script fuori dal
progetto.

- **S3** (stealth contro massa, 4 contro 8 F-15C, 20 repliche). Senza stealth le perdite *assolute* dei due lati
  sono indistinguibili (Blue 3,90, Red 3,68, z = −1,4), ma la *frazione* persa è 97,5 % contro 46 % (Blue peggio in
  40 seed su 40); con stealth Blue 1,85 e Red 3,80 aerei persi, frazione 46 % contro 47,5 %, differenza assoluta a
  coppie Red − Blue +1,95 (sd 1,22, z = 10), rapporto di scambio 2,05-2,4 contro 0,94-1,0. Nuove verifiche: (1)
  senza stealth la frazione persa da Blue supera quella di Red (aggregato e differenza a coppie per seed ≥ 3 errori
  standard; sui 20 seed di test z = 16,4); (2) con stealth Red perde più aerei assoluti di Blue (differenza media a
  coppie ≥ 3 errori standard; sui 20 seed media 2,3, z = 12,8); (3) il rapporto di scambio migliora con lo stealth
  e Blue perde meno aerei. Helper `_paired_z` e soglia `MIN_Z = 3` dichiarata, non tarata. Con lo stealth il
  vantaggio è nel rapporto di scambio, non nella frazione persa.
- **S5** (3 strati, 4 F-15E, ora 12 seed). Con la dottrina di default 23 formazioni su 24 si fermano al primo
  strato; con `PRESS_ON` (ad oltranza) il terzo strato è raggiunto 1 volta su 24. Nuova struttura: *default* con
  asserzione di maggioranza (si fermano al primo strato più che proseguire; 11 su 12 nei seed di test) più
  invarianti per replica (strati in ordine geometrico, nessun lancio rosso dopo la rottura, chi si ferma al primo
  strato non vede sparare nemmeno il terzo); una **variante «formazione resistente»** con la dottrina Blue di
  default ma `RESISTANT_EROSION = 0,65` (costante di scenario, stima non calibrata; frequenza di «prosegue oltre il
  primo strato»: 0,5 → 4/24, 0,6 → 7/24, 0,65 → 23/40, 0,7 → 28/40, 0,75 → 18/24), in cui l'asserzione è «entrambi
  gli esiti compaiono» (7 proseguono e 5 si fermano nei 12 seed di test) più le stesse invarianti; `PRESS_ON` resta
  con «almeno due strati in ogni replica» e l'ordine geometrico, senza asserzione sul terzo strato (nessuna
  variante per numero di aerei misurata cade fra il 30 % e il 70 %: 4 → 1/24, 5 → 19/24, 6 e 8 → 24/24).
- Fotografia: nessuna esecuzione esistente cambiata, 20 nuove (S5-8..11 default e `PRESS_ON`, S5-0..11
  `resistant`), 348 totali.

## 8.10 Scenari e verifiche delle fasi F5, F6 e G1-G5 (2026-10-11/18)

Le misure vengono da `Analysis/Document/F4_Differenze_Scenari.md` (sezioni «F5 passo (a)», «(b)», «(c)-(d)», «F6 passo
A», «B1», «B2», «B2bis», «G2», «G3», «G4a», «G4b», «G5») e dai docstring dei moduli di test; i test asseriscono sempre
**proprietà qualitative, strutturali o statistiche con soglie dichiarate**, mai un numero calibrato. Sei scenari nuovi,
tutti in coda alla tabella `UNITS` di `Scenario_Baseline` (nomi stabili: non spostano le chiavi delle altre unità).

| Scenario | Classe di test | Fase | Cosa esercita | Esecuzioni |
|---|---|---|---|---|
| **S22** | `TestS22E1FinishedMissionStaysEngageable`, `TestS22E3LateDepartureIsPresent`, `TestS22AircraftOnTheGround` | F5-B | presenza fuori dalla rotta: unità di terra ferme prima/dopo; aerei a terra fino al decollo e dopo l'atterraggio su una base vera | 72 (E1 16, E3 16, AIR 40) |
| **S23** | `TestS23CapOrbit`, `TestS23GroundHold`, `TestS23TotPerMission` | F5-C | azione WAIT (orbita di una CAP, sosta di un carro), TOT per missione, ETA effettive | 80 (CAP 32, HOLD 24, TOT 24) |
| **S24** | `TestS24DryTank`, `TestS24DryAircraft`, `TestS24OrbitExhaustion` | F6-A | carburante per tratto, esaurimento a monte, planata e perdita dell'aereo a secco, orbita che esaurisce il carburante | 88 (E5 32, GLIDE 32, ORBIT 24) |
| **S25** | `TestS25Winchester`, `TestS25MaxDuration`, `TestS25DestroyedPosture`, `TestS25DamageThreshold`, `TestS25TargetDestroyed` | F6-B1 | criteri di fine attività, stato di missione, postura `destroyed` | 112 (WIN 24, DUR 24, POST 16, DMG 24, TGT 24) |
| **S26** | `TestS26Bingo` | F6-B2 → G5 | il bingo nel modello finale G1-G4 e la controprova di ogni interruttore | 96 (12 varianti × 8 seed) |
| **S27** | `TestS27DoubleEngagement` | G5 | doppio ingaggio dello stesso aereo: due consumi d'ingaggio, ri-pianificazione dopo ciascun episodio, bingo dopo il secondo | 40 (5 varianti × 8 seed) |

Metodi di test definiti nei moduli (contati sul codice a `a784a9e7`): S22 13, S23 16, S24 13, S25 12, S26 16, S27 8; i test dei
mixin di appoggio (`_GroundChecks` in S22, `_EtaChecks` in S23) sono eseguiti una volta per ogni classe che li eredita, quindi gli
eseguiti sono di più (S22: 16, come dice `F4_Differenze_Scenari.md`). Ogni scenario con un
interruttore ha una **variante di controllo con l'interruttore spento**, registrata nella fotografia come le altre: è
come si dimostra che lo scenario *distingue* la fase (con l'interruttore spento molti test falliscono: 7 su 17 per S23,
10 su 12 per S25, misurati con sonde fuori dal repository).

**S22 — presenza fuori dalla rotta** (F5-B). *S22-E1* (esperimento E1 dell'analisi, 8 seed): 3 BMP-2 fermi con sensore
`'ground'` dichiarato di 4,2 km contro un M1A2 la cui missione arriva a 4 km e finisce a 800 s; varianti 'finished'
(la missione è finita) e 'static' (lo stesso carro senza missione, riferimento): Red spara in 8/8 repliche in entrambe, in
'finished' ogni colpo parte **dopo** l'arrivo (811-828 s) e il carro è messo fuori combattimento in 8/8. *S22-E3*
(partenza a 1000 s verso l'esterno del sensore; 'not_departed' oltre la fine): Red spara in 7/8, ogni colpo **prima** della
partenza. *S22-AIR* (5 varianti): Red-Airbase (2 MiG-29S 'CAP' più un deposito, riferimento della base) contro Blue-Strike
(2 F-16C in sorvolo a 3000 m, fuoco solo sui bersagli parcheggiati): 'parked' (decollo a 900 s, strike a 0) MiG colpiti
in 8/8 (16/16 danneggiati, 9/16 distrutti), solo da `'test:agm'`, tutti i colpi prima del decollo; 'airborne' (strike a
1500 s, MiG già usciti di scena) nessun colpo; 'landed' (LAND sul deposito a 240 s) di nuovo a terra e colpiti, postura
`parking_cold`; 'no_base' (LAND senza riferimento a 30 km) escono di scena, postura `off_scene`; 'base_area' (LAND a
1,9 km dal deposito, senza riferimento) a terra e colpiti. Con `F5_PRESENCE` spento E1 'finished' e E3 'late' danno 0
colpi su 8 seed e nessun danno ai MiG in 'parked' e 'landed'.

**S23 — attese, TOT, ETA** (F5-C, rifatto il 2026-10-12 per il TOT per missione). *S23-CAP* (4 varianti: 'during',
'after', 'no_wait', 'waits_off'): 2 MiG-29S da -75 km al punto O in orbita per 1500 s; bombardieri che non sparano per O
a 1000 s ('during') o a 2200 s ('after'): la CAP spara in 8/8 (32 lanci tutti fra 877 e 927 s, dentro l'orbita,
13/16 bombardieri distrutti) solo nel passaggio dentro l'orbita; senza WAIT o con `F5_WAITS` spento nessun lancio. *S23-HOLD*:
un M1A2 con sosta di 600 s al punto W1 contro 3 BMP-2 con tiro dichiarato senza effetto: i colpi proseguono fino a
1541 s (con la sosta) contro 941 s (senza), ETA effettive (0, 800, 2600) contro (0, 800, 2000). *S23-TOT*: il caso
dell'utente, **TOT diversi per missioni della stessa Operazione** — uno *sweep* (2 F-16C 'Fighter_Sweep') anticipa lo
strike di `SWEEP_LEAD` = 120 s (stima di test), varianti 'own_tot' (partenza 0: attese di 300 s e 180 s al punto di
partenza), 'derived' (nessuna partenza: derivata), 'waits_off'; ciascuna missione raggiunge il **proprio** TOT.

**S24 — carburante** (F6-A). *S24-E5* (8 seed, 4 varianti): M1A2 con `fuel` = 0,002 (autonomia 426 km: 852 m) su 7 km,
esaurimento a 85,2 s; 'far' (rotta verso i BMP, fermo a 6,65 km): nessun colpo in 8/8; 'far_off' (vincolo spento,
l'esperimento E5 di prima): Red spara in 8/8 a 361-363 s, **oltre** il punto di esaurimento; 'near' (fermo a 3,9 km):
Red spara in 8/8 anche dopo 664 s. Esito: carro non distrutto, `FUEL_EXHAUSTED` a 85,2 s, missione `ABORTED`/`FUEL`.
*S24-GLIDE* (F-16C con carburante per 50 km a 5000 m, esaurimento a 200 s): 'glide' (base Blue a 20 km) planata fino a
~277 s e a terra (strike Red lancia solo dopo l'atterraggio); 'no_base' e 'enemy_base' perso a 200 s,
`DESTROYED`/`FUEL_EXHAUSTED`, salute 0 senza `DamageEvent`, missione `DESTROYED`; 'off' (vincolo spento) rotta completata
a secco. Le fixture dichiarano `EndCriteria(bingo=False)`: **con il bingo di default cambierebbero 24 esecuzioni di
S24-GLIDE** (decisione dell'utente da prendere: F6-B3 aperto, capitolo 9 §9.1). *S24-ORBIT* (MiG-29S in orbita):
'full' tre `FuelEvent` per tratto, la CAP spara in 8/8; 'dry' (carburante per mezza orbita) orbita esaurita dopo 750 s,
MiG perso, nessun lancio; 'per_leg_off' (`F6_FUEL_PER_LEG` spento) l'orbita non consuma, un solo evento.

**S25 — fine di attività** (F6-B1; ogni scenario ha i controlli 'undeclared' e 'switch_off', identici fra loro). *S25-WIN*:
F-16C con scorta imposta {AIM-9M: 2, M61A1: 500} (`winchester=('MISSILES_AAM',)`): due salve AIM-9M, poi nessuna, cannone
intatto, `WINCHESTER` a 16,5 s, missione `ABORTED`/`AMMUNITION`, e **prosegue passivo** (la scorta Red gli lancia contro
32 salve dopo la fine); i controlli lanciano 12 salve. *S25-DUR*: `max_duration_s` = 120, nessun lancio dopo, `COMPLETED`
(la durata è una fine regolare). *S25-POST*: postura `destroyed` per i distrutti, `off_scene` per gli altri; spento,
nessuna `destroyed`. *S25-DMG*: soglia 0,05 con un colpo che graffia, un solo lancio, `DAMAGE` alla prima risoluzione
(32,5 s), `ABORTED`/`DAMAGE`. *S25-TGT*: 2 F-16C su un deposito bersaglio GROUP, distrutto in 8/8 fra 133 e 149 s, nessun
lancio successivo sul deposito, `TARGET_DESTROYED`, `COMPLETED`.

**S26 — il bingo nel modello finale** (F6-B2 → G5; riorganizzato il 2026-10-18, **le 96 esecuzioni sono identiche** a quelle
di prima). *Blue-Flight*: un F-16C 'Strike' (autonomia di crociera del registro col loadout: 1570 km, 'max' 1140 km;
riserva di disimpegno ~0,085 del pieno) in volo a 5000 m da (10 km, 0) a (310 km, 0) a 250 m/s: rotta 0,191 alla
crociera (0,263 al regime di combattimento), soglia del G2 ~0,276. *Blue-Base* a (0, 0), ~11,2 km dal punto di comparsa e
a 10 km dalla rotta (non è una base alternativa); *Red-Site*, un BMP-2 a 260 km con sensore `'air'` dichiarato di 40 km e
tiro dichiarato senza effetto. Le varianti sono divise per ruolo:

- **modello finale**: 'none' (pieno: nessun bingo, un solo consumo d'ingaggio); 'bingo' (combattimento, 0,27, sotto la
  soglia: bingo alla partenza, scende subito sulla base, ~42 s, Red non spara mai; il validatore rifiuta);
  'transfer_return' (`Transport`, 0,15: ritroso e diretto alla base); 'transfer_continue' (`Transport`, 0,27: **continua**,
  ma se Red spara il consumo d'ingaggio rende il residuo insufficiente e, con la ri-pianificazione, l'aereo è **perso per
  carburante a fine rotta** con l'equipaggio recuperato); 'no_base' (nessuna base: perso per carburante a ~235,5 km);
  'bingo_off' (`EndCriteria(bingo=False)`, criterio della missione, non un interruttore: nessun controllo, perdita come
  'no_base'); 'post_engagement_bingo' (0,28, sopra la soglia alla partenza; secondo sito Red-Near a 100 km e **base
  alternativa sulla rotta** a (180 km, 2 km), sensore `'ground'` dell'F-16C dichiarato di 20 km perché le finestre dei due
  siti siano due episodi: dopo l'episodio con Red-Near il residuo è ~0,110 sotto il resto della rotta ~0,106 più la riserva
  ~0,085: **bingo alla fine dell'episodio**, regola di combattimento, la base alternativa (~42 km lungo la rotta e discesa)
  batte il ritroso (~145 km), atterraggio ~690 s, `ABORTED(BINGO)`, Red-Site mai incontrato);
- **controprova degli interruttori** (`SWITCH_CHECKS`): 'switch_off' (`F6_BINGO` spento), 'reverse_off' (`F6_BINGO_REVERSE_ROUTE`
  e `F6_BINGO_DISENGAGE_RESERVE` spenti: la F6-B2, rientro rettilineo con la riserva 0,1 a x ≈ 146,3 km), 'reserve_off'
  (`F6_BINGO_DISENGAGE_RESERVE` spento: la F6-B2bis, bingo a x ≈ 203,7 km), 'engagement_fuel_off' (`G3_ENGAGEMENT_FUEL`
  spento: la regola `'max'` della F6-A), 'replan_off' (`G4_REPLAN` spento, lo scenario di 'post_engagement_bingo': nessuna
  ri-pianificazione, l'aereo prosegue, incontra Red-Site, consuma due volte e il contatore arriva a zero con la rotta
  completata: il limite del G3). Un test (`test_variants_split_into_final_model_and_switch_checks`) verifica che le due
  liste partizionino le varianti; un test per regola storica verifica validatore, istante del bingo, tratti ed esito.

Le costanti di carburante dello scenario (`G2_FUEL` 0,27, `BINGO_FUEL` 0,28, `DRY_FUEL` 0,15) sono **di test**, verificate
nel test (`test_declared_fuels`) contro la rotta e la riserva ricalcolate dal registro.

**S27 — doppio ingaggio** (G5, 2026-10-18). *Blue-Flight*: un F-16C 'Strike' (consumo d'ingaggio = riserva 0,0852 del
pieno) in volo a 5000 m da (10 km, 0) a (510 km, 0) a 250 m/s (2000 s; rotta 0,318 alla crociera, 0,439 al regime `'max'`),
sensore `'ground'` dichiarato di 20 km; *Red-First* (BMP-2 a 100 km) e *Red-Second* (a 300 km), sensore `'air'` dichiarato di
40 km, tiro marcatore senza effetto; *Blue-Alternate* a (400 km, 2 km), entro 3 km dalla rotta e 60 km oltre la finestra
di Red-Second. Finestre ~[160, 520] s e ~[1000, 1320] s: **due episodi**. Carburante `DOUBLE_FUEL` = 0,53, dimostrato nel
test fra rotta + 2 riserve (~0,489) e rotta + 3 riserve (~0,574). Esito per variante (8 seed, in tutti sparano entrambi i
siti):

| Variante | Interruttore spento | Consumi d'ingaggio | Decisioni dopo l'episodio | Esito | Carburante finale |
|---|---|---|---|---|---|
| 'double' | — | 2 | ~524-532 s: nessun bingo (residuo ~0,361); ~1323-1327 s: `BINGO_ALTERNATE` (residuo ~0,149) | `ABORTED(BINGO)`, a terra su Blue-Alternate (`parking_cold`) | 0,1077 |
| 'transfer' (`Transport`) | — | 2 | nessun bingo; poi `BINGO_CONTINUE` | `COMPLETED`, `off_scene` a fine rotta | 0,0411 |
| 'replan_off' | `G4_REPLAN` | 2 | nessuna | `COMPLETED` | 0,0411 |
| 'episodes_off' | `G4_EPISODES` | 1 (un solo ingaggio: la componente connessa) | nessuna | `COMPLETED` | 0,1263 |
| 'engagement_fuel_off' | `G3_ENGAGEMENT_FUEL` | 0 (movimento al regime `'max'`) | nessuna | `COMPLETED` | 0,0914 |

Mostra: due consumi d'ingaggio dello stesso aereo nella stessa sessione (il limite «un consumo per sessione» del G3 è
risolto dal G4a, e 'episodes_off' ne è la controprova); la ri-pianificazione dopo **ciascun** episodio con il residuo
analitico (letta da una spia su `Mission_Adapter.mission_bingo_decision`, nessuna voce nuova nell'esito né nella
fotografia); il bingo con la regola di combattimento, dove la base alternativa in avanti (~60 km più la discesa) batte il
ritroso (~340 km, che ripasserebbe sopra entrambi i siti); il trasferimento che, sotto la soglia ma con carburante per la
rotta, continua consumando la riserva. Scelte: gli «ingaggi» sono di siti terrestri con tiro marcatore, **non di
intercettori aerei veri** (storia deterministica: nessun danno, nessun disingaggio, che farebbe scattare il rientro
forzato al posto del bingo); nessuna variante «senza base alternativa» (il ritroso ripasserebbe su Red-Second e
mescolerebbe due effetti, e il ritroso dopo l'episodio è già coperto da S5 e S24-ORBIT).

**S5 e le altre esecuzioni toccate da G4a e G4b.** Gli episodi (G4a) e la ri-pianificazione con l'uscita di scena (G4b)
hanno cambiato le esecuzioni in cui un aereo partecipa a più episodi o si disingaggia (in totale 165 delle 802 della
fotografia del G3; §8.7). S5 passa da tre a **otto varianti** (96 esecuzioni): 'press_on', 'default', 'resistant' più
'episodes_off' (G4a spento: la vecchia 'default'), 'with_base' e 'with_base_resistant' (una base aerea Blue 10 km dietro il
punto di comparsa, perché la formazione disingaggiata abbia dove rientrare), 'replan_off' (base, G4b spento) ed 'exit_off'
(senza base, uscita di scena spenta). Misura su 12 seed, «Blue distrutti» (L1/L2/L3 = strato che li ha distrutti): 'default'
(G4b + uscita di scena, senza base) 20, L2 spara in 1 replica, esito `ABORTED(DISENGAGED)` in 12; 'resistant' 31, L2 in 9,
`ABORTED(DISENGAGED)` 8, `COMPLETED` 1, `DESTROYED` 3; 'exit_off' 28, L2 in 12, `COMPLETED` 12; 'with_base' come 'default'
(storia identica, cambia solo il tratto finale, il carburante e la postura: `parking_cold` invece di `off_scene`);
'press_on' (non disingaggia) invariata 41; 'episodes_off' invariata 17. Con la dottrina di default e la base la formazione
disingaggiata a L1 (11 repliche) **rientra** dalla fine dell'episodio lungo la rotta a ritroso fino al punto di comparsa:
L2 non spara mai; sul ritroso ripassa su L1 (nuovo episodio, passiva) e in alcune repliche perde un altro aereo. Le misure
di S3 e S5 del §8.9 sono quelle della riprogettazione dell'11 ottobre e **non sono più quelle di oggi** per S5; gli
invarianti dei test sono stati aggiornati, non la composizione degli scenari (`Scenario_Fixtures.losses_of` somma le
perdite sugli episodi della stessa forza d'ingaggio; S13/S14/S21 leggono gli esiti per episodio; S7/S18 accettano episodi
successivi fra le sole forze aeree dopo un disingaggio).

**Test aggiunti dopo `84a47670`, per modulo** (a `a784a9e7`; i test di scenario sono nelle righe precedenti):

| Modulo di test | Cosa copre |
|---|---|
| `Test_Fuel_Model.py` (91 test; nuovo contenuto) | `TestLegFuelEvent`, `TestFuelExhaustion`, `TestGlide` (F6-A); `TestBingo`, `TestReverseRouteBingo` (F6-B2, F6-B2bis); `TestDisengagementReserve`, `TestEngagementFuel` (G1, G3); `TestBingoDecision` (G2: soglia, posizioni e residui arbitrari, rami dei due alberi, alternative avanti/indietro, limite 3,0/3,1 km, parità, nessuna base); `TestFuelAt`, `TestExhaustionFromAResidual`, `TestForcedReturn`, `TestExitScene` (G4b) |
| `Test_Mission_Adapter.py` | `TestHoldsAndEffectiveEtas`, `TestPresenceBeforeAndAfter`, `TestFinalPosture`, `TestF5Switches`, `TestTotPerMission`, `TestAirBaseArea` (F5); `TestBingoValidator`, `TestReverseRouteBingoValidator`, `TestReserveBingoValidator`, `TestMissionFuelMinimum` (i validatori, F6-B2 → G2) |
| `Test_Session_Simulator.py` | `TestPresenceAndPostures`, `TestWaitsAndEtas`, `TestEndCriteria`, `TestFuelExhaustion` (riscritta), `TestBingo`, `TestReserveBingo`, `TestEngagementFuel`, `TestEpisodes`, `TestEngagementEpisodes`, `TestReplanAfterEpisode` (G4b, con l'uscita di scena) |
| `Test_Contact_Scheduler.py` | `TestGroundedSchedule`, `TestGroundedTransitionsSplitWindows` (F5-A); il ritaglio `trim_contact_window` e `only_assets` (G4a/G4b) |
| `Test_Engagement_Resolver.py` | `TestGroundedInTime` (F5-A), `TestActivityEnd` (F6-B1) |
| `Test_Fire_Control.py`, `Test_Aircraft.py`, `Test_Mission_Types.py` | `TestWeaponCategory`; `emergency_fuel_flow` (3 test); `crew_recovered`, `Operation` senza `tot`, `FUEL_EXHAUSTED` |

**Suite attuale: 4385 test, OK (7 skipped)** (`F4_Differenze_Scenari.md`, sezione G5, verificata dall'utente il 2026-10-18; 10
in più dei 4375 del G4b: S26 +2, S27 +8). Numeri dichiarati dai documenti attraverso le fasi: 4039 (F4c) → 4072 (F5-A) → 4101 (F5-B) → 4131 (F5-C) → 4133 (TOT per missione) → 4166 (F6-A) → 4195 (F6-B1) → 4224 (F6-B2) → 4245 (F6-B2bis) → 4344 (G4a) → 4368 (G4b) → 4375 (uscita di scena) → 4385 (G5); G1, G2 e G3 non dichiarano un totale nel documento. I conteggi dei test di questo manuale sono quelli dei messaggi di
commit e di `F4_Differenze_Scenari.md`; **non sono stati rieseguiti** per questo aggiornamento (a differenza della
fotografia, il cui numero di esecuzioni è stato contato sul file).
