# Capitolo 8 — Validazione

Harness e test: `Test/Scenario_Fixtures.py` (fabbrica di scenari, non un modulo di test:
il nome non inizia con `Test_`), `Test/Test_Session_Validation.py` (determinismo + agnosticismo
come test di contratto), `Test/Test_Session_Scenarios.py` (S1-S9), `Test/
Test_Session_Scenarios_S10_S18.py` (S10-S18). Suite finale della Fase 7: **3371 test, OK
(skipped=5)** (wiki `decisions/virtual-session-engine-des`, sezione Fase 7).

## 8.1 `Test/Scenario_Fixtures.py` — la fabbrica di scenari

Costruisce con **oggetti reali** gli ingredienti comuni agli scenari: nessuna logica del motore
è duplicata (niente Pd, salve, danno, carburante) — ogni numero di un esito viene da
`Session_Simulator.run_session` e dai moduli che chiama (`Test/Scenario_Fixtures.py:1-11`).

Fornisce (`:13-40`): asset reali dai registri (`make_vehicle`, `make_aircraft`, `make_ship`, con
id sempre esplicito — `Asset.__init__` genererebbe altrimenti un suffisso casuale); forze
(`make_force`, `add_assets`, `build_force`); infrastrutture reali (`make_infrastructure`,
`make_structure`: `Production`/`Storage`/`Transport`/`Urban`, costruibili solo dal 2026-09-23 dopo
la correzione di 5 bug preesistenti nei loro costruttori, v. §8.4); rotte
(`straight_route`, `route_for`); un `fire_control` di riferimento (`make_fire_control`, §8.2);
esecuzione (`run(...)`, `Scenario.run(session_id)`, `combined_arms_scenario()`); letture
dell'esito (`losses_of`, `damage_by_source`, ...).

### Sensori dichiarati di test — lacuna dei registri documentata (`:41-53`)

I registri **non** dichiarano alcun sensore in modo `'ground'` per carri, corazzati e artiglieria
(portate nulle in tutti i record `Tank`/`Armored`/`Artillery_*` di `Vehicle_Data`), né per le navi.
Con i soli registri, due forze terrestri **non si vedono mai**: è un dato mancante, non un errore
del motore (`Mobile.detection_range` lo dichiara esplicitamente), ma oggi nessun chiamante di
produzione lo compensa. Per gli scenari si usa quindi un sensore dichiarato di test
(`declare_sensor`), un'iniezione esplicita e visibile in ogni scenario — non un'alterazione
silenziosa dei registri.

### `fire_control` di riferimento — una tabella di ruoli, non la selezione dell'arma (`:55-81`)

`make_fire_control` classifica tiratore e bersaglio in un **ruolo** (`'air'`, `'sea'`, `'sam'`/
`'aaa'`, `'artillery'`, `'ground'`, `'logistic'`, `'structure'`, più i ruoli di missione imposti
per id: `'fighter'`, `'strike'`, `'sead'`) e consulta una tabella `(ruolo tiratore, ruolo
bersaglio) -> ShotSpec | None`. Le `ShotSpec` sono **costanti di test dichiarate**, di ordine di
grandezza plausibile ma **non calibrate e non prese da una fonte**: gli scenari ne verificano
l'effetto qualitativo (chi perde di più, cosa accade prima), mai un numero assoluto.

## 8.2 Determinismo (`Test/Test_Session_Validation.py:66-125`)

`TestDeterminism` verifica su `combined_arms_scenario()` (la composizione di S1): stesso
`SessionOrder` + forze ricostruite identiche (stessi id, precondizione verificata
esplicitamente) → `SessionOutcome` identico, campo per campo e come oggetto intero (le dataclass
sono frozen e comparabili), **e** stato reale degli asset dopo l'applicazione identico
(`health`, `ammunition`, `fuel`). Accompagnato dal controllo di **non vacuità**: un `session_id`
diverso (quindi un seed diverso) deve cambiare gli eventi prodotti ma **non** la struttura
deterministica (le stesse componenti di forze in contatto, che dipendono solo dalla geometria,
non dal seed) — altrimenti l'uguaglianza del primo test potrebbe dipendere da un motore che
ignora il seed anziché da un motore davvero deterministico.

## 8.3 Agnosticismo come test di contratto (`Test/Test_Session_Validation.py:1-44`, `:128-319`)

Il vincolo "core indifferente al simulatore" (capitolo 1, §1.4) si formula come "cancellando
l'adapter DCS la campagna deve continuare a girare". A questo commit **non esiste alcun adapter
DCS** nell'albero Python: non c'è nulla da rimuovere. Il test è quindi un test di **contratto**,
in due parti:

**(a) Strutturale** (`TestAgnosticContractStructure`, `:170-219`): verificato con
`typing.get_type_hints` + AST-check, non a runtime:

- ogni campo delle porte (`SessionOrder`, `SessionOutcome`, `ForceOutcome`, `DamageEvent`,
  `AmmunitionEvent`, `InterceptionEvent`, `FuelEvent`) è di tipo atomico (str/float/int/bool/None)
  o composto solo di tipi atomici e tipi della catena stessa (Union/tuple/mapping ricorsivamente,
  `_type_is_domain`, `:150-167`);
- nessun nome di campo contiene lessico del simulatore (`dcs`, `miz`, `unitid`, `unitname`,
  `groupid`, `groupname`, `airdrome`, `dictkey`, `missiontime`, `modeltime`, `lua` —
  `_SIMULATOR_WORDS`, `:140-141`);
- ogni campo `time`/`t_*` è `float` (mai un orologio del simulatore);
- i moduli del motore (`Session_Types`, `Session_Simulator`, `Engagement_Resolver`,
  `Contact_Scheduler`, `Damage_Model`, `Fuel_Model`, `Session_Rng`) non importano `lupa`,
  `zipfile`, `minizip`, né nulla con `'dcs'` nel nome, e non chiamano `timer.getTime`
  (l'orologio nativo di DCS/Lua).

**(b) Funzionale end-to-end** (`TestAgnosticEndToEnd`, `:239-319`): l'intera catena gira con dati
costruiti **solo** in Python (nessun `.miz`, nessun `dcs_unit_data`) e produce un
`SessionOutcome` completo (ingaggi, danni, munizioni, carburante tutti presenti); ogni id
presente nell'esito è un id di dominio noto (di forza o di asset costruiti dal core), mai un id
di missione del simulatore; ogni `time` cade dentro `[t_start, t_end]` della sessione. Una
mini-campagna di **tre sessioni consecutive** sulle stesse forze verifica che lo stato passa solo
attraverso gli asset mutati (nessuno stato nascosto fuori dagli asset). Limite annotato nel test
stesso (`:259-261`): `run_session` non aggiorna `asset.position` a fine rotta (nessun movimento
fisico, v. capitolo 6 §6.5) — nelle sessioni successive le forze ripartono dalle posizioni
iniziali; non conta per verificare la concatenazione di salute/munizioni/carburante, ma è un
limite per una campagna vera (v. capitolo 10).

Quando l'adapter DCS esisterà, questo stesso test diventerà eseguibile alla lettera; fino ad
allora è il suo equivalente verificabile (`Test/Test_Session_Validation.py:42-44`).

## 8.4 La batteria di scenari S1-S18

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

Tutti gli scenari condividono la stessa regola: si prende la composizione delle forze e la
domanda che pongono, mai coefficienti o esiti numerici precalcolati — per S6-S18 la domanda è
"il meccanismo X del motore si comporta correttamente", non un risultato storico o di dominio da
riprodurre (wiki `decisions/soglie-disingaggio-e-attrito-aggregato` §P3).

## 8.5 Bug trovati durante la Fase 7

Cinque bug preesistenti, mai istanziati con successo in produzione (zero rischio di regressione),
corretti durante la costruzione della batteria S12-S18: costruttori rotti da sempre di
`Transport`/`Storage`/`Urban`/`Production`/`Structure`, e `Block.set_asset` che rifiutava ogni
sottoclasse di `Asset` (confrontava il nome classe esatto invece di usare `isinstance`) — wiki
`decisions/virtual-session-engine-des`, sezione Fase 7.
