# Revisione — Proposta di revisione della regola L1 (lanciatore bersaglio immediato)

**Revisore**: `des-reviewer` (sessione Claude Code, Opus), revisione indipendente in sola lettura.
**Oggetto**: `Analysis/Document/Proposta_Revisione_L1_Lanciatore_Bersaglio.md` (1198 righe, `des-planner`).
**Commit**: `1f28b2b7` (branch `analysis/dce-dcs-persistence`); il codice citato dalla Proposta e' quello di `0c7263cd`,
identico per i file di codice (il commit `1f28b2b7` tocca solo la Proposta e la memoria).
**Data**: 2026-11-25. Convenzioni: **[V]** letto nel codice; **[E]** eseguito (script di sola lettura); **[NV]** non verificato.

## Verdetto

**ESEGUIBILE CON CORREZIONI** — nessun problema bloccante; tre punti da correggere nel testo prima di consegnarlo
all'esecutore (n. 1, 2, 3), gli altri sono note.

Le decisioni a=2, c=2, d=2, e=1, Q-L1-1..3 e SD-1..SD-6 sono rispettate dal piano (§2.4, §4.2). L'interruttore spento
riproduce per costruzione il percorso di oggi. I riferimenti al codice sono quasi tutti esatti; le discrepanze trovate
sono di riga o di nome, non di contenuto.

---

## 1. Problemi

| # | Gravita' | Sezione Proposta | Riscontro nel codice | Correzione proposta |
|---|---|---|---|---|
| 1 | **da correggere** | §2.1, §2.4 SD-1, §4.2 punto 5 (`_immediate_target`) | Il pool prioritario di L2 non e' solo `_in_range_at`: i candidati passano prima dal filtro `viable` di `_schedule_next` (`Logic/Engagement_Resolver.py:2860-2896`): `exhausted`, bersaglio `operative` e non `_gone`, `t_fire` con `candidate.not_before` (`:2874-2875`), fine attivita' (`:2881`), tiratore a terra a `t_fire` (`:2885`), `_is_deferred` per ROE dipendenti dal tempo (`:2892`). Il chiamato `_in_range_at` e' a `:2906` | La Proposta esclude in modo esplicito solo `exhausted` (SD-1) e lo stato del lanciatore dopo il lancio (SD-6). Gli altri filtri (`not_before`, `_is_deferred`, fine attivita', intercettore a terra) sono ignorati senza dirlo, mentre c=2 dice "stessa condizione del pool prioritario di L2". Aggiungere una riga a SD-1 che dica quali di questi filtri si applicano e quali no, cosi' l'esecutore non deve decidere. Lettura minima coerente con SD-1/SD-6: nessuno dei filtri di stato (`exhausted`, `operative`, `_gone`), ma **si** `_is_deferred` a `t_fire` (una ROE che rimanda il bersaglio a quell'istante vuol dire che il lanciatore non e' un bersaglio immediato). E' una scelta dell'utente o del pianificatore, non del revisore |
| 2 | **da correggere** | §4.1 punto 1 (`_is_interceptor_weapon`) | Oggi: `if float(wdata.get('max_altitude', 0)) <= 0.0: continue` (`Asset/Mobile.py:1119-1120`). Proposta: `return float(...) > 0.0`. Le due forme differiscono solo per `NaN` (oggi l'arma resta, con la funzione nuova esce) | La Proposta dice "comportamento identico". Per avere identita' letterale scrivere `return not float(wdata.get('max_altitude', 0)) <= 0.0`, oppure dire che `NaN` non c'e' nei registri (valori letterali). Senza effetti sulla fotografia, ma il testo dice "identico" |
| 3 | **da correggere** | §1.4 tabella; §4.1 test 8 | Nomi che non sono chiavi del registro: `CV 1143.5 Kuznetsov` non si trova (nessuna chiave con quella stringa in `Vehicle_Data`/`Ship_Data` [E]); `Type 052B` e' `Type 052B Guangzhou-class` [E] | La tabella e' informativa, ma un esecutore che la usi per controlli o test non trova le chiavi. Scrivere le chiavi esatte del registro (o dire "nome abbreviato"). I modelli usati nei test (Rezky, Burke IIa) esistono |
| 4 | nota | §1.3, glossario L2 | `_in_range_at` usato da L2 e' a `:2906`, non `:2903` (che e' la fine del commento `:2901-2903`) | Correggere il riferimento |
| 5 | nota | §4.1 test del blocco 1 | `_STORES_MEMBERS` e' a `Test/Test_Mobile.py:1481-1491` (la Proposta dice `:1484-1491`) | Correggere la riga |
| 6 | nota | §5 R-1 | Oltre alla scorta, anche altri dati letti dalla condizione (2) sono allo **stato della risoluzione**, non al lancio: `_designated_destroyed` (`:3119-3130`, tramite `_attack_over` in `_fire_control`, `:3240-3243`) e gli insiemi ostili `hostile_by_domain` (`_is_hostile`, `:3086-3090`). Deterministico, nessuna estrazione | Allargare R-1 da "scorta" a "scorta e stato delle regole di bersaglio di missione (designati distrutti, ostili noti)" |
| 7 | nota | §4.2 punto 5 | `latest_ready = seen + total + TIME_EPS` lascia passare anche i candidati di passaggi **precedenti**; sono poi esclusi dal controllo `t_fire > t_end` (un passaggio precedente finisce prima di `t_launch`). Senza tratti (`own_passes_of` senza la coppia) `_detection_time_of` restituisce l'**ultimo** rilevamento (`:3757-3758`), e tutti i candidati precedenti passano il filtro su `t_ready` | Funziona, ma il docstring dice "candidato del passaggio del lancio": aggiungere "(i candidati di passaggi precedenti sono esclusi da `t_end`)". Utile anche un test unitario con due passaggi (vedi n. 8) |
| 8 | nota | §4.2 tabella dei test | Mancano casi che il piano non esercita: (a) due passaggi dell'intercettore sul lanciatore, rilevato solo nel primo, lancio nel secondo (FP-5 (d): non e' un bersaglio immediato); (b) BI acceso con colpo ammesso, per fissare l'ordine BI -> L1 rivista (oggi solo lo scenario S35 (B) n. 3, con colpo non ammesso); (c) intercettore di un'altra forza del dominio (difesa di dominio, `_on_resolve:3872-3880`) | Facoltativi: (a) e' il piu' utile, perche' e' il ramo in cui `_detection_time_of` e il filtro su `t_ready` interagiscono |
| 9 | nota | §4.6 (blocco 6) | Il blocco 6 dice "piano di dettaglio da riscrivere al momento"; e' coerente con la pratica (pulizia FP), ma non e' un contratto eseguibile oggi | Nessuna correzione: va solo detto nel prospetto per l'utente che il blocco 6 richiede una Proposta nuova |

---

## 2. Verificato e corretto

**Engagement_Resolver (`Logic/Engagement_Resolver.py`)** [V]
- `_may_intercept` `:3719-3742`, cache `:3726-3742`, confronto `allowed = not (horizontal <= radius and bottom <= height <= top)` `:3738`, dato mancante `:3729/:3734`; `_interception_zone` `:3684-3702`; `_position_at` `:3669-3682`; `zone_cache` `:2044`; `may_intercept_cache` `:2050`.
- `_detection_time_of` `:3744-3767`; `_in_time` (R-INT) `:3824-3849`, lancio osservato `seen <= t_launch + TIME_EPS` `:3842`; `_admissible` `:3711-3717`.
- `_on_resolve` `:3851`, ciclo per salva `:3917-3938`, condizioni in OR `:3929-3930` nell'ordine canali -> BI -> L1 -> R-INT; canali `:3906-3911`, sottrazione per altre forze `:3887-3892`; commento L1 `:3894-3901`; estrazione di danno `:3976-3978`.
- `_in_range_at` `:3301-3322` (non muta il candidato; ramo VA `:3312`), `_first_with_stock` `:3404-3421`, `_range_entry` `:3423-3465` (solo memo `range_cache`), `_altitude_deferral` `:3508-3557`, `_fire_control` `:3230-3243`, `_call_fire_control` con warning `target_grounded` `:3263-3275`, `_register_launcher` (L3) `:3325-3375` con `_in_range_at` a `:3367`.
- `_Candidate` `:1794-1807`; candidati creati in `_detect_direction` `:2422-2427` e `_detect_passes` `:2640-2646` con `t_ready = istante + total`.
- Interruttori: `BI_AD_TARGET_RULE` `:625` letto a `:2058`; `VA_ENGAGEMENT_ALTITUDE_BAND` `:636`; `D5_DWELL_TIME` `:610-619`; `self.ad_domain_cache` `:2059` (punto d'inserimento di §4.2 punto 2 corretto).
- `Salvo` (`:820-838`) ha `salvo_id`, `t_launch`, `t_impact`, `shooter_id`, `target_id`, `rounds`, `spec`; `TIME_EPS` e' importato da `Contact_Scheduler` (`:535`); `Optional`, `Tuple`, `Dict` sono importati (`:525`).
- Docstring del modulo punto 4 (`:40-52`) e menzione di `_may_intercept` a `:298`: esistono come citato.

**Determinismo** [V]
- Le sole estrazioni restano `_draw` in `:2402`, `:2623`, `:3977` (e `:4107` come dichiarato); nessuno dei metodi nuovi (`_interceptor_envelopes`, `_immediate_target`, `_may_intercept_revised`) ne chiama.
- `_detection_time_of` costruisce `detected_at`/`detection_times_of` in modo pigro da `self.detections`; i rilevamenti sono calcolati tutti nel pre-passo `_detect` (`:2328-2347`) prima della coda eventi, quindi chiamarla prima (da L1) non cambia i valori che R-INT legge dopo.
- Interruttore spento: `_may_intercept` -> `_may_intercept_volume` con le stesse chiamate, nello stesso ordine e con la stessa cache. La riproduzione bit a bit della fotografia e' plausibile per costruzione (vedi §3 per cio' che non ho eseguito).

**Mobile (`Asset/Mobile.py`)** [V]
- `INTERCEPTOR_TASK = 'Anti_Missile'` `:208`, commento CIWS `:210`; `GROUND_WEAPON_TASK` importato `:13-21`; `INTERCEPTOR_WEAPON_TYPES_VEHICLE/SHIP` `:199-200`, `INTERCEPTOR_GUN_WEAPON_TYPES` `:201`.
- `interceptor_weapons_from_registry` `:1059-1129`, docstring "non possano divergere" `:1062-1065`, filtro `:1112-1120`, riga `result[...]` `:1122`; `interceptor_capability` `:1131`; `_valid_item` `:859-869`.
- `air_defense_volume` `:1396-1464`: navi solo `MISSILES_SAM` (`:1429-1432`), veicoli `AA_CANNONS`+`MISSILES` con task `Anti_Air` (`:1434-1440`); stesse letture di raggio previste da `interceptor_envelopes` (km x 1000 per le navi, `range['direct']` per i veicoli, `:1448-1451`).
- La rifattorizzazione di §4.1 punto 2 non cambia `interceptor_weapons_from_registry` (stesse condizioni nello stesso ordine), salvo la nota n. 2 su `NaN`. `interceptor_envelopes` e' un metodo nuovo senza chiamanti fuori dal risolutore: `air_defense_volume`, scorte, `Military.salvo_interceptors` non cambiano.
- Il meccanismo dei test di Test_Mobile (`_with_stores_members` copia `Mobile.__dict__[name]`) funziona per un metodo che chiama una funzione di modulo (risolta nei globali di `Mobile`).

**Valori dei registri (§1.4)** [E, script di sola lettura con la stessa selezione]
- Tor 9M331 12 km 10-6000; Buk 9M38 35 km 15-22000; S-300PS 5V55R 75 km 25-27000; Tunguska 2A38M 4 km 0-3500 + 9M311 8 km 15-3500; Gepard 4 km 0-3000.
- Burke IIa e CG-65: SM-2ER 240 km 25-33000, ESSM 50 km 15-15000, Phalanx 1,5 km 0-1500. Type 052C: HHQ-9 200 km + Type-730 3 km. Moskva: S-300F 150 km + AK-630 4 km. Piotr Velikiy: S-300F 150, SA-N-9 15, AK-630 4. Type 054A 70 + 3; Type 071 13 + 3; Neustrashimy 15 + 4.
- **Rezky, Grisha, Molniya: solo AK-630, 4 km, 0-3000**; **FFG-46: solo Phalanx 1,5 km, 0-1500**. Il test 8 del blocco 1 (`('AK-630', 4000.0, 0.0, 3000.0)` e Burke 240000.0) e' coerente col registro.
- Unica difformita': i nomi della nota n. 3.

**Test e scenari** [V]
- `Test_Engagement_Resolver.py`: `_ER_LOGGER` `:46`; `_ScriptedRng` `:78`; `_profiles` `:106`; `_miss` `:114`; `REACTION_TOF` `:121`; `_ZonedInterceptor` `:1798` (firma `(asset_id, position, radius, bottom=0.0, height=6_000.0, **kwargs)`, compatibile con `_ArmedInterceptor`); `TestLauncherInsideInterceptionZone` `:1811-1876`, **7 test** come dichiarato; `test_launch_inside_the_escort_zone_is_not_intercepted` `:3155-3164`; `test_switch_on_filter_is_applied_before_not_instead_of_l1` `:4857-4860`. I cinque stub che descrivono la regola di oggi sono fissati spenti dal piano: i 7 test di (a) con `patch` in `_run`, i 2 di (a2) con `patch` nel corpo; con l'interruttore spento di default non cambiano nemmeno senza `patch`.
- `Test_Mobile.py`: `TestInterceptorStockFromRegistry` `:1903-2057`, `_InterceptorStub` `:1745`, `_FAKE_GW`, `_FakeVehicleData`, `_FakeAircraftData`, `_ship_record`, `_vd_mod` presenti.
- `Test_Session_Scenarios_S19_Air_Defence.py`: `run_variant` `:81` (restituisce una terna, `[::2]` a `:138`), `TOR_FORWARD_X` `:59`, `OVERFLIGHT` `:55`, `MAVERICK` `:50`, `_interceptions` `:118`, `_rounds_fired` `:122`, `setUpClass` `:131-146`, `test_forward_tor_engages_launchers_inside_its_zone` `:200`, `TestS19AdTargetRule` `:253`. La chiamata di (A) coincide con quella di `cls.tor_forward`.
- `Test_Session_Scenarios_S35.py`: `SEEDS` `:40`, `SHIP` `:60`, `run_variant(session_id, variant)` `:123`, `_interceptions` `:138`, `_events` `:146`.
- `Test_Session_Scenarios_S10_S18.py`: `TestS16NavalInstallation` `:1065`, `SHIPS` `:1123`, `LOW_LEVEL_FACTOR` `:1125` (costante di scenario dichiarata), `SALVO_WINDOW` `:1126`, `_build` `:1130`, spia su `ER.resolve_engagement` `:1151-1168` (il precedente dello spy di (A) esiste e funziona con `patch.object`), `# ── S17` `:1281`, `BOTH_HOLD` `:110`.
- `Scenario_Baseline.py`: `FORMAT_VERSION` `:251`, `ROUND_DIGITS` `:252`, `UNITS` `:298`, `capture(only, verbose)` `:749`, `dump(snapshot, path)` `:807`, opzioni `--against`, `--only`, `--quiet`, `--summary` (`:1007-1013`): l'Appendice A usa API esistenti.

**Vincoli di AGENTS.md**
- Determinismo, nessun `random` globale: rispettato [V].
- Interruttore con default che riproduce il comportamento attuale, letto una volta per run in `__init__`: rispettato (§4.2 punti 1-2, §4.6bis).
- Core indifferente al simulatore: `interceptor_envelopes` legge solo `Vehicle_Data`, `Ship_Data`, `Ground_Weapon_Data`, `Ship_Weapon_Data`; nessun import dall'adapter DCS [V].
- Nessuna costante nuova: raggi e quote sono dati di registro; le quote dei CIWS sono gia' marcate "STIMA B" nel registro; i numeri nei docstring dei test di scenario sono dichiarati come misure.
- Import assoluti; classi di test `unittest.TestCase` come le vicine, nessuna classe base nuova; logger mockato con `patch(_ER_LOGGER)` e `F.LoggerSilencer`.

**Coerenza interna**
- Conteggi: blocco 1 = 8 test, blocco 2 = 14, blocco 3 = 4 + 3 + 2 = 9; totale "base + 31" coerente con §4.3.
- Confronto atteso: 1219 identiche a interruttore spento; 6 CHANGED acceso (§4.8 = §1.5 L-2 = Appendice A).
- Sigle (L1, L2, L3, R-INT, BI, FP-5 (d), VA, SD-1..6, Q-L1-1..4, PD-1/2, R-1..R-6) definite e usate in modo coerente; rimandi fra sezioni corretti.

---

## 3. Non verificato

- **Misure [M]** di §1.5 (412/414 coppie, 13 esclusioni, 6 esecuzioni cambiate, rapporti di distanza, 6 test che falliscono con la regola accesa): non rieseguite. Gli script del prototipo sono nella cartella temporanea di **un'altra sessione** (`/tmp/claude-1000/.../db4537e6-.../l1rev/`) e potrebbero non esistere piu'; il blocco 4 le rimisura con l'interruttore vero.
- **Esiti attesi dei 14 test unitari del blocco 2** (in particolare il n. 12, "3 estrazioni di differenza", e il n. 6 con `stores=`/`interceptor_weapons=` passati a `_ArmedInterceptor` -> `_ZonedInterceptor` -> `_Asset`): non provati; non ho controllato che `_Asset` accetti quei parametri.
- **Suite e confronto completi**: non eseguiti (fuori dal compito). Ne' suite ne' singoli file di test eseguiti.
- **Righe dei documenti del manuale** citate in §4.9 (`05_...:1781-1797`, `10_...:299/316/364-367/860/890`, `08_...:287`): non controllate.
- Il numero di esecuzioni filtrate da `--only '^(S6|S11|S16|S19AD|S35-ADTGT)/'` nel confronto parziale (la Proposta lascia N non specificato: va letto dall'esito).

---

## 4. Nota per un upgrade futuro (SD-6)

**Stato di oggi.** SD-6 (lo stato del lanciatore **dopo** il lancio non entra nella condizione (2)) e' confermata e il
piano la rispetta: `_immediate_target` non guarda `operative`/`destroyed` del lanciatore. E' coerente con una lettura
in cui ogni colpo in volo prosegue da solo, indipendentemente da quello che succede al lanciatore.

**Limite.** In futuro l'operativita' del colpo in volo potrebbe dipendere dal tipo di asset e dal tipo di guida
dell'arma. Per le armi la cui guida dipende ancora dal lanciatore dopo il lancio, mettere fuori uso il lanciatore puo'
far perdere la guida al colpo. Per le armi autonome dopo il lancio (*fire-and-forget*) no. Oggi il motore tratta tutti i
colpi come autonomi: il payload e' congelato al lancio (R4, `_call_fire_control` docstring `:3258-3261`) e il danno si
applica all'impatto senza guardare il lanciatore (`_on_resolve:3966-3987`).

**Dati gia' nei registri** [V, ricerca dei nomi di campo]:
- `Asset/Ship_Weapon_Data.py`: campo `'guidance'` sulle voci missilistiche (es. valori `'Active_Radar'`,
  `'Semi_Active_Radar'`, `:1053-1117`), 25 occorrenze.
- `Asset/Aircraft_Weapon_Data.py`: campo `'seeker'` (es. `'radar'`, `'infrared'`, letto a `:524-526`), che descrive il
  sensore terminale ma non distingue in modo esplicito la dipendenza dal lanciatore.
- `Asset/Ground_Weapon_Data.py`: nessun campo di guida o seeker.
- Nessun registro ha un campo diretto "dipende dal lanciatore dopo il lancio"; andrebbe derivato da `guidance`
  (dove c'e') con una tabella di corrispondenza dichiarata come scelta di progetto [S], oppure aggiunto come campo
  nuovo nei registri, con le stesse regole dei dati (fonte o stima dichiarata).

**Come si aggancerebbe** (solo descrizione, nessuna modifica proposta ora, Proposta invariata):
1. **Dato**: una proprieta' derivata per arma, es. "colpo dipendente dal lanciatore" (si/no/ignoto), letta da chi
   conosce l'arma (`Fire_Control.shot_spec_for`) e portata nella `ShotSpec` come campo opzionale in coda (default
   None = "ignoto = autonomo", cioe' il comportamento di oggi). E' lo stesso schema di `intercept_domains` della BI.
2. **Regola nel risolutore**, dietro un interruttore nuovo spento di default: alla risoluzione di una salva, se il colpo
   dipende dal lanciatore e il lanciatore non e' piu' operativo all'istante utile, i colpi non arrivano al danno (o
   arrivano con una precisione ridotta, da decidere). Nessuna estrazione nuova se la regola e' deterministica; se si
   volesse una probabilita', servirebbe uno stream dedicato per non spostare le estrazioni di danno.
3. **Legame con PD-1 e PD-2** (§5 della Proposta):
   - **PD-2** (lanciatore abbattuto prima della risoluzione: oggi i suoi colpi restano esclusi per l'intercettore che
     lo aveva come bersaglio immediato). Con il dato di guida, per i colpi dipendenti dal lanciatore il caso si risolve
     da solo: abbattuto il lanciatore, i colpi perdono la guida e la questione dell'esclusione non si pone. Per i colpi
     autonomi resta aperta la domanda di PD-2 (rivalutare la condizione (2) alla risoluzione, cioe' rivedere SD-6 solo
     per questi).
   - **PD-1** (la priorita' al lanciatore ha senso per la salva successiva, non per quella in volo). Il tipo di guida
     dice **quale** delle due letture e' sensata per ogni arma: per un colpo dipendente dal lanciatore, colpire il
     lanciatore protegge anche dalla salva in volo, quindi l'esclusione L1 e' coerente; per un colpo autonomo protegge
     solo dalla salva successiva, quindi intercettare comunque con la capacita' che avanza (l'opzione scartata di Q2
     del 2026-09-28) torna a essere un'alternativa ragionevole. Un upgrade potrebbe rendere l'esclusione L1
     condizionata anche alla guida: esclusione solo per i colpi dipendenti dal lanciatore.
4. **Ordine consigliato**: prima la decisione dottrinale su PD-1/PD-2 (Proposta separata, con esempi), poi il dato di
   guida nei registri (con fonti o stime dichiarate), poi la regola nel motore dietro un interruttore. Per la
   fotografia il cambio e' nullo finche' l'interruttore e' spento, e la sonda di L1 (Appendice A) e' riusabile per
   misurarlo.
