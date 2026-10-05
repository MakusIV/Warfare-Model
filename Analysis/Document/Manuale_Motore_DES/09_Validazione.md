# Capitolo 8 — Validazione

Harness e test: `Test/Scenario_Fixtures.py` (fabbrica di scenari, non un modulo di test:
il nome non inizia con `Test_`), `Test/Test_Session_Validation.py` (determinismo + agnosticismo
come test di contratto), `Test/Test_Session_Scenarios.py` (S1-S9), `Test/
Test_Session_Scenarios_S10_S18.py` (S10-S18), `Test/Test_Session_Scenarios_S19.py` e
`Test/Test_Session_Scenarios_S19_Air_Defence.py` (S19, S19AD), più lo strumento di non regressione
`Test/Scenario_Baseline.py` (§8.7). Suite finale della Fase 7: **3371 test, OK
(skipped=5)** (wiki `decisions/virtual-session-engine-des`, sezione Fase 7).

**Aggiornamento rispetto alla stesura iniziale**: le estensioni successive alla Fase 7 (selezione
arma dai registri, nebbia di guerra, scorta per modello d'arma, cannone di bordo, finestre di
rilascio delle bombe, volumi di rilevamento/intercettazione distinti, pianificatore d'attacco —
v. capitolo 4 §4.16-4.20 e capitolo 7 §7.6-7.9) hanno portato la suite a **3645 test, OK
(skipped=5)** al commit `6754bf1c` (2026-09-27), tutte nello stesso harness di questo capitolo. **Aggiornamento a `533cd1f5`** (2026-10-05): la suite è a
**3922 test, OK (skipped=7)** (messaggio del commit `533cd1f5`), con le estensioni del 2026-09-28/30 (soglia
di rottura stocastica, E(N), RWR, A6, dottrina di tiro, R-INT) e le fasi F0-F3 della Missione; i moduli di
test nuovi e le classi aggiunte sono elencati in §8.8. Fra
i moduli di test aggiunti dall'ultimo aggiornamento: `Test/Test_Aircraft_Weapon_Data.py` (classe
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
(`straight_route`, `route_for`, `routes_for`, `:499-560`); **missioni** (`missions_for`, `:633-697`, dal
2026-10-05, v. sotto); un `fire_control` di riferimento (`make_fire_control`, §8.2);
esecuzione (`run(...)`, `Scenario.run(session_id)`, `combined_arms_scenario()`); letture
dell'esito (`losses_of`, `damage_by_source`, ...).

### Migrazione alle missioni (fase F3, 2026-10-05, `Test/Scenario_Fixtures.py:95-116`)

Dopo che `run_session` ha perso `routes`/`starts`/`speeds` (capitolo 6 §6.1), **ogni asset che prima riceveva
una rotta è ora asset di una `Mission`**; gli asset fermi (difese, siti SAM, blocchi in posizione) non sono
missioni (diventeranno la "postura continua" della fase F4). `missions_for(force, points, mission_type=...,
target=...)` riproduce **esattamente** la geometria di `routes_for`:

- una missione = asset di **un** blocco con la stessa velocità sugli archi (stesso profilo del registro: in un
  blocco misto, es. carri M1A2 + M2 Bradley, i due modelli procedono a velocità diverse e diventano **due
  missioni dello stesso blocco**);
- dentro una missione la rotta di riferimento è quella del primo asset (per id) e gli altri hanno l'offset di
  formazione che riproduce la loro rotta traslata; l'offset è accettato solo se `Mission_Adapter.asset_route`
  ridà gli **stessi punti** (confronto esatto), altrimenti l'asset ha una missione propria (succede con
  rotte che cambiano direzione: una traslata rigida non è un offset nella terna di marcia, capitolo 6 §6.10);
- **semplificazione di scenario dichiarata**: le rotte aeree degli scenari partono in volo (`start_mode` AIR) e
  finiscono sull'obiettivo o oltre, **senza rientro in base**; per non indebolire la validazione di `Mission`
  (D2.c: una missione aerea finisce con `LAND`) l'ultimo punto ha ruolo `LAND`. Il rientro vero (RTB) è delle
  fasi F5-F6.

Anche `Scenario` ha ora `missions` al posto di `routes` (`routes` resta come proprietà di sola lettura
derivata, `:880-884`) e `run(...)` accetta `missions=` (`:843-849`).

### Sensori dichiarati di test — lacuna dei registri documentata (`:45-58`)

I registri **non** dichiarano alcun sensore in modo `'ground'` per carri, corazzati e artiglieria
(portate nulle in tutti i record `Tank`/`Armored`/`Artillery_*` di `Vehicle_Data`), né per le navi.
Con i soli registri, due forze terrestri **non si vedono mai**: è un dato mancante, non un errore
del motore (`Mobile.detection_range` lo dichiara esplicitamente), ma oggi nessun chiamante di
produzione lo compensa. Per gli scenari si usa quindi un sensore dichiarato di test
(`declare_sensor`), un'iniezione esplicita e visibile in ogni scenario — non un'alterazione
silenziosa dei registri.

### `fire_control` di riferimento — una tabella di ruoli, non la selezione dell'arma (`:59-86`)

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

## 8.3 Agnosticismo come test di contratto (`Test/Test_Session_Validation.py:1-47`, `:134-371`)

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

**(b) Funzionale end-to-end** (`TestAgnosticEndToEnd`, `:262-371`): l'intera catena gira con dati
costruiti **solo** in Python (nessun `.miz`, nessun `dcs_unit_data`) e produce un
`SessionOutcome` completo (ingaggi, danni, munizioni, carburante tutti presenti); ogni id
presente nell'esito è un id di dominio noto (di forza o di asset costruiti dal core), mai un id
di missione del simulatore; ogni `time` cade dentro `[t_start, t_end]` della sessione. Una
mini-campagna di **tre sessioni consecutive** sulle stesse forze verifica che lo stato passa solo
attraverso gli asset mutati (nessuno stato nascosto fuori dagli asset). Limite annotato nel test
stesso (`:281-285`): `run_session` non aggiorna `asset.position` a fine rotta (nessun movimento
fisico, v. capitolo 6 §6.5) — nelle sessioni successive le forze ripartono dalle posizioni
iniziali; non conta per verificare la concatenazione di salute/munizioni/carburante, ma è un
limite per una campagna vera (v. capitolo 10).

Quando l'adapter DCS esisterà, questo stesso test diventerà eseguibile alla lettera; fino ad
allora è il suo equivalente verificabile (`Test/Test_Session_Validation.py:44-47`).

## 8.4 La batteria di scenari S1-S19

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
| **S3** | `TestS3StealthVersusMass` | Pochi caccia "stealth" contro molti convenzionali, stesso modello per isolare il meccanismo: `detection_factor` degrada la Pd contro un bersaglio Blue. Verifica che il rapporto di scambio rifletta il vantaggio di rilevamento, non solo il numero. |
| **S4** | `TestS4SAMAsThirdComponent` | Scontro terra-terra con un sito SAM (terza forza, `extra_forces`) che interviene contro il CAS di un lato. Verifica che il SAM riduca l'efficacia del CAS ed entri nello stesso ingaggio dello scontro terrestre. |
| **S5** | `TestS5DeepInterdictionThreeLayers` | Missione aerea profonda contro un bersaglio composito dietro 3 strati di difesa (lungo, medio, punto) su una rotta di 950 km. Verifica che gli strati ingaggino in ordine geometrico e che la missione raggiunga il bersaglio o sia fermata prima. |
| **S6** | `TestS6CarrierGroupVersusCoastalDefence` | Gruppo da battaglia navale (CVN+CG+DDG) contro litorale difeso da terra e da mare. Esercita la fusione di finestre di contatto di dominio misto (aereo-veicolo, aereo-nave, nave-veicolo) nella stessa timeline. |
| **S7** | `TestS7LogisticInterdiction` | Attacco aereo contro un bersaglio **non militare** (`Block` generico `category='Logistic'`) con scorta di caccia. Verifica che il bersaglio non spari/intercetti mai ma riceva comunque un `ForceOutcome` e danno reale. |
| **S8** | `TestS8MultiFrontScale` | Decine di blocchi su più fronti (40 blocchi, 240 asset) — test di **scala**, non di correttezza tattica. Verifica che la potatura gerarchica scarti la maggioranza delle coppie in modo conservativo e che la sessione completi entro un limite di tempo. |
| **S9** | `TestS9PartialFogOfWar` | Stessa composizione di S1, con `detection_factor` degradato per il lato Blue. **Gap documentato**: il fog-of-war reale del progetto (`Region`/`Tactical_Analysis`, `recon_cp_snapshot`) non è collegato al motore di sessione — questo scenario esercita solo il punto di iniezione geometrico, non l'informazione C2 (v. capitolo 10). |
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
| **S19AD** | `TestS19AirDefenceAllocation` | Allocazione della difesa aerea fra intercettazione e tiro sul lanciatore (A6, capitolo 4 §4.24): 3 BMP-2 con una difesa a corto raggio, 1-4 A-10C con i soli AGM-65D, quattro varianti (Strela-10 in sorvolo, Strela-10 in standoff, Tor arretrato, Tor avanzato). Esito qualitativo, mai numerico. |

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

- **S19** (`Test_Session_Scenarios_S19.py`, 7 test, `:117-172`): era già nella batteria ma non descritto nelle
  stesure precedenti del manuale; dalla F3 le rotte degli aerei sono tre missioni dello stesso blocco
  (CAS, scorta, bombardamento: tre modelli a velocità diverse), con bersagli `group_target`.
- **S19AD** (`Test_Session_Scenarios_S19_Air_Defence.py`, commit `aedd7fa5`): scenario **persistente** della
  riproduzione della proposta SAM (`Proposta_Regole_Allocazione_SAM.md` §1.1 e §7.8). Sei test
  (`:138-200`): i Maverick sono lanciati; lo Strela non intercetta mai (regola D); lo Strela spara i
  missili agli aerei in sorvolo e li conserva in standoff; il Tor arretrato intercetta lanci da fuori
  zona; il Tor avanzato spara ai lanciatori. Due stand-in di A4 (filtro armi per missione, rimandato alla
  F7): `maverick_only_fire_control` (l'A-10C usa solo AGM-65D, altrimenti il criterio Pk/costo sceglierebbe la
  Mk-82AIR, non intercettabile) e `ifv_only` (gli aerei attaccano solo i BMP-2). Con lo standoff ogni A-10C ha
  una missione propria (la rotta cambia direzione, §8.1).
- **S10** verifica il meccanismo del disingaggio con soglie **fisse** (`FIXED_THRESHOLDS`, `Test_Session_Scenarios_S10_S18.py:117`)
  e ha in più un caso DISPERSIONE con la dottrina di default (soglia di rottura stocastica, capitolo 4 §4.21);
  S5 verifica la distribuzione degli esiti; il docstring di S1 descrive la ritirata di Red con il nuovo modello.
- **S11, S13** e **S1 con CAS** hanno cambiato esito o composizione per la regola D (capitolo 4 §4.24):
  S13, il FARP con Shilka + Strela-10 non ha più intercettori; S11, difesa sostituita con Gepard + Tor perché
  le verifiche sulle scorte d'intercettazione avessero casi; S1 con CAS, i Maverick non sono più intercettati
  (`Proposta_Dati_Anti_Missile.md` §6).

## 8.7 Lo strumento di non regressione: `Test/Scenario_Baseline.py` (fase F0, commit `d3af6980`)

Dalla fase F3 la porta di sessione cambia e servono **numeri** per dimostrare che, a parità di input, il motore
produce la stessa storia (`Piano_Implementazione_Missione.md`, §0 punto 2 e Fase 0). `Scenario_Baseline.py`
(590 righe, **fuori** dalla discovery della suite: il nome non comincia con `Test_`) esegue gli scenari di
sessione esistenti, riassume ogni `SessionOutcome` in una forma deterministica e la salva su JSON, oppure la
confronta con una fotografia salvata.

**Come trova gli scenari: riuso, non duplicazione.** La tabella `UNITS` (`:138-182`) elenca le "unità" dei
test: per le classi di scenario (S1-S19, S19AD, validazione) esegue il loro `setUpClass`, che costruisce le
forze con `Scenario_Fixtures` e lancia tutte le repliche e varianti usate dai test; per
`Test_Session_Simulator` (nessun `setUpClass`) un elenco scelto di **metodi** di test (`ORC-*`). Durante
l'esecuzione `Session_Simulator.run_session` è sostituita da un registratore (`_Recorder`, `:354-365`) che chiama
l'originale e poi riassume l'esito **e** lo stato reale degli asset (letto subito dopo la chiamata: in S11 e
nella mini-campagna la sessione successiva muta di nuovo le stesse istanze). Le asserzioni dei test non sono
eseguite per le classi di scenario; per i metodi un'asserzione fallita è segnalata su stderr ma non impedisce la
registrazione.

**Nomi stabili**: chiave `<scenario>/<session_id>[/<variante>]`; la variante è l'indice di occorrenza dello
stesso `session_id` nell'unità, tradotto in un nome leggibile dalla tabella (es. `with_cas`/`without_cas` per
S1). Se un `setUpClass` cambia l'ordine delle varianti, le chiavi cambiano: va aggiornata la tabella.

**Cosa registra** (`summarize_run`, `:283-349`): intervallo della sessione, forze dei due lati e parametri di
chiamata riconoscibili, esiti di forza per ingaggio (con tempi, perdite, erosione, shock, soglia), stato finale
per asset (salute, operativo, distrutto, munizioni, scorta per arma, intercettori, carburante), munizioni
consumate per asset e per arma, intercettazioni per asset e per arma, eventi di carburante, conteggi (salve,
intercettazioni, danni, distruzioni) e le liste complete degli eventi. I float sono arrotondati a 6 decimali
(`ROUND_DIGITS`, `:92`; `-0.0` normalizzato, `norm`, `:203-227`), le chiavi ordinate: **due catture dello stesso
codice sono identiche byte per byte**. `FORMAT_VERSION = 1` (`:91`).

**Parametri di chiamata dopo la F3**: `run_session` non ha più `routes`; perché la fotografia della Fase 0 resti
confrontabile, la voce `call.parameters.routes` è **ricostruita dalle missioni** (`Mission_Adapter.mission_routes`,
`_call_parameters`, `:256-280`), e una lista vuota equivale all'assenza della voce (`_without_empty_routes`,
`:489-497`).

**Uso** (dalla radice del repository, con l'interprete della macchina):

```
python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --capture out.json
python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
    --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json
```

`--only <regex>` limita il confronto a unità o chiavi; `--compare a.json --against b.json` confronta due file
già catturati senza eseguire nulla. `compare` (`:500-537`) segnala `ERROR`, `MISSING`, `NEW` e `DIFF` (con al più
20 righe di differenza per esecuzione). Codice d'uscita (`main`, `:542-586`): 0 identiche, 1 differenze o errori
di unità, 2 uso errato.

**La fotografia di riferimento** è `Test/baseline/scenario_baseline.json` (circa 2,8 MB, **292 esecuzioni**,
chiavi `errors`/`meta`/`runs`), catturata su una copia isolata di `18a772d6` e identica in due catture
separate. Le fasi F2 e F3 l'hanno confrontata con il codice nuovo: **292 esecuzioni identiche** (messaggi dei
commit `4e18d7d8` e `533cd1f5`). Il piano prevede di rigenerarla **una volta**, in un commit dedicato che lo
dichiari, quando il `mission_id` entrerà nell'RNG (fase F4, che cambia le estrazioni); altre differenze sono
ammesse solo se la fase le prevede e il commit le spiega.

## 8.8 Test aggiunti dopo `6754bf1c` (per modulo)

| Modulo di test | Cosa copre |
|---|---|
| `Test_Mission_Types.py` (nuovo, 838 righe) | tipi della Missione: `TestTarget`, `TestStartCondition`, `TestMissionAction`, `TestMissionWaypoint`, `TestMissionAsset`, `TestEndCriteria`, `TestMissionRules`, `TestMissionValid`/`Invalid`, `TestRouteWaypoints`, `TestCheckMissionAssets`, `TestOperation`, `TestAssetMissionOutcome`, `TestMissionOutcome` |
| `Test_Mission_Adapter.py` (nuovo) | `TestZeroOffsetIdentity`, `TestFormationOffset`, `TestSpeeds`, `TestStart`, `TestSessionMovements` (capitolo 6 §6.10) |
| `Test_Session_Types.py` | `TestSessionOrderMissions`, `TestSessionOutcomeMissions` (capitolo 2 §2.2-2.3) |
| `Test_Context.py` | tassonomia dei tipi di missione, tabelle di categoria e posture, rename `Retreat` |
| `Test_Air_Defense_Efficacy.py` (nuovo) | `TestExpectedKills`, `TestSharedDirector`, `TestDirectorsFromTheRegistry`, `TestSamCategoryAndRwr`, `TestRwrClassThreat`, `TestRwrTable` (completezza della tabella RWR) |
| `Test_Doctrine.py` | `TestBreakpointParameters`, `TestFireDoctrine` |
| `Test_Engagement_Resolver.py` | `TestStochasticBreakpoint`, `TestAirForceRatio`, `TestRwrPerception`, `TestRwrClassThreat`, `TestFireDoctrine`, `TestLauncherInsideInterceptionZone` (L1), `TestLauncherPriority` (L2/L3), `TestInterceptionReaction` (R-INT), con i 19 test esistenti portati a `REACTION_TOF = 20 s` |
| `Test_Session_Simulator.py` | flusso separato della tempra (`test_temper_stream_is_distinct_and_order_independent`), `TestMissions` (missioni nell'orchestratore, esito di prima forma) |
| `Test_Session_Validation.py` | contratto di agnosticismo esteso alle porte della Missione (§8.3) |
| `Test_Mobile.py`, `Test_Military.py`, `Test_Aircraft*.py` | capacità `Anti_Missile`, ordine F, CIWS, task di supporto, dati delle armi aggiunte |

