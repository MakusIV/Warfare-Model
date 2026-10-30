# Manuale del motore DES di sessioni virtuali — Warfare-Model

Questo manuale descrive l'architettura e il funzionamento del motore di simulazione a eventi
discreti (DES, *discrete event simulation*) che risolve le **sessioni virtuali** della campagna,
cioè i turni sintetici eseguiti senza un giocatore DCS (e, per costruzione, anche quelli con un
giocatore: il core non distingue i due casi, v. capitolo 1).

> **Aggiornato al commit `fa5fbf1e`** (2026-10-23, "Memoria: F8-R applicata (dc53af99), prossimi passi F9, F8d, prova su osboxes"), branch
> `analysis/dce-dcs-persistence`. `fa5fbf1e` è un commit di sola memoria: **l'ultimo commit che tocca `Code/` è `dc53af99`** (F8-R, 2026-10-23), quindi il codice descritto è quello di
> `dc53af99`. Il manuale descrive **lo stato di `fa5fbf1e`**, cioè dopo le fasi F0-F8 del piano di implementazione della Missione (F4 = regola A, missione come unità d'ingaggio, dominio di
> coordinamento, difesa di salva per dominio, postura continua; F5 = presenza, `grounded` nel tempo, attese, TOT per missione; F6 = carburante per tratto, criteri di fine, stato di missione,
> bingo e rientro; F7 = regole d'ingaggio di missione e fuoco su posizione; **F8 = sessione e campagna**: validatore di sessione, esito per la campagna con lo stato di missione «in corso» e le
> posizioni finali, prontezza degli asset, conduttore di campagna, posizione persistente, scenario S30), i passi **G1-G5** del modello di bingo, la chiusura del **F6-B3** (S24-GLIDE lasciato
> con `bingo=False`, solo docstring) e i dati **F8-R** dei tempi di turnaround e riparazione. La **F9** (documentazione) è questo aggiornamento. **Non sono fatte** la logistica (F8d, per decisione
> dell'utente) né un chiamante di produzione del ciclo di campagna. **A `fa5fbf1e` — suite di test: 4701 OK (7 skipped); confronto con la fotografia: 986 esecuzioni IDENTICHE; fotografia di non regressione: 986
> esecuzioni** (contate sul file `Test/baseline/scenario_baseline.json`). **I numeri di suite e confronto sono quelli dichiarati dalla verifica della sessione principale al commit `dc53af99` (messaggio
> del commit e Piano §5, riga F8-R) e NON sono stati rieseguiti per questo aggiornamento.** Righe dei moduli (`grep -c ''`): `Command/Session_Types.py` 712, `Command/Mission_Types.py` 1387,
> `Context/Context.py` 2252, `Context/Campaign_State.py` 760, `Logic/Mission_Adapter.py` 2000, `Logic/Session_Simulator.py` 3163, `Test/Scenario_Baseline.py` 932; moduli nuovi
> `Command/Campaign_Types.py` 406, `Logic/Session_Validator.py` 269, `Logic/Session_Campaign.py` 153, `Logic/Readiness.py` 343.
> *(Stato precedente: `dcedc541`, 2026-10-20, suite 4555 e 982 esecuzioni; prima ancora `a784a9e7`, 2026-10-18, suite 4385 e 918 esecuzioni.)*
>
> **Aggiornamento 2026-10-30 — atlante dei diagrammi, parti A-C** (commit `42ffb851`, `4fe1225f`, `255f5bc4`; solo documentazione, il codice resta quello di `f009eb43`): capitolo 10 esteso con i diagrammi D67-D129 e le tabelle complete dei simboli di tutti i moduli del core; nessuna suite o confronto rieseguiti.
>
> **Aggiornamento 2026-10-29 — correzione del difetto 26** (codice `be8559d7`, docstring `f009eb43`, fotografia `643fff87`; il manuale è stato riverificato sul codice del branch `analysis/dce-dcs-persistence`).
> `Logic/Readiness.readiness_after_session` riporta ora i record di prontezza degli asset non passati alla sessione; `apply_campaign_processes` conserva il record concluso di un asset assente e lo applica al suo ritorno
> (scelta 3b, `logger.debug` al posto del warning); **nessun interruttore**; scenario nuovo **S30-ABSENT** (`TestS30AbsentForce`, 3 esecuzioni, 4 test). **Suite di test: 4710 OK (7 skipped); confronto con la fotografia: 989 esecuzioni
> (986 IDENTICHE + 3 nuove); fotografia di non regressione: 989 esecuzioni** (contate sul file). I numeri di suite e confronto sono quelli del rapporto dell'esecutore (`Rapporti/Rapporto_difetto26_des-developer.md`),
> verificati dalla sessione principale con `tools/ai/verifica.sh`, e **non sono stati rieseguiti** per questo aggiornamento. Cambiano il capitolo 6 §6.26-6.27 (regola, `apply_campaign_processes`, righe), il capitolo 7 (righe di
> `Campaign_State`, docstring), il capitolo 8 (§8.4, §8.7, §8.12, nuovo diagramma D56) e il capitolo 9 (limiti; **voci 24, 25, 26 e 27 di §9.6 ora CHIUSE**). I tempi di turnaround e riparazione sono quelli della ricerca F8-R (`dc53af99`),
> in parte ancora STIME DI PROGETTO dichiarate nei commenti di `Context`. Righe dei moduli toccati (`grep -c ''`): `Logic/Readiness.py` 357, `Logic/Session_Campaign.py` 154, `Context/Campaign_State.py` 764, `Test/Scenario_Baseline.py` 935.

**Aggiornamento 2026-10-20 → 2026-10-23 (da `dcedc541` a `fa5fbf1e`, fase F8: F8a, F8b, F8c e dati F8-R)**, in ordine di capitolo. I commit di codice sono
`c1182d8a` (F8a, unione; `e593bc9a` il commit di completamento), `33698fb4` (F8b, unione di `b19ab151`), `87aa7dea` (F8c blocco 1), `6d3497bc` (F8c blocco 2), `398ae3ef` (F8c blocco 3), `3fb25089` (chiusura della F8c:
due test di S30, fotografia a 986, docstring di S24, seme fisso di `testCalcFightResult`) e `dc53af99` (F8-R, solo dati); gli altri commit del tratto sono piano, memoria, registro dei costi e configurazione degli agenti
OpenCode e non toccano `Code/` (verificato con `git log dcedc541..HEAD -- Code`). Il codice toccato è `Command/Session_Types.py` (558 → 712 righe), `Command/Mission_Types.py` (1341 → 1387), `Context/Context.py` (2225 → 2252),
`Context/Campaign_State.py` (725 → 760), `Logic/Mission_Adapter.py` (1973 → 2000) e `Logic/Session_Simulator.py` (3102 → 3163), più i **quattro moduli nuovi** `Command/Campaign_Types.py`, `Logic/Session_Validator.py`,
`Logic/Session_Campaign.py` e `Logic/Readiness.py` e i test, lo scenario S30 e la fotografia. `Logic/Contact_Scheduler.py`, `Logic/Engagement_Resolver.py`, `Logic/Fire_Control.py`, `Logic/Fuel_Model.py`, `Logic/Damage_Model.py`, `Logic/Area_Fire.py`,
`Asset/*` e tutti i moduli di supporto trasversale restano invariati.

1. **Strato 0, porte e tipi della Missione** (capitolo 2 §2.1, §2.3-2.4, §2.6, §2.8, nuova **§2.10**): `SessionOutcome` guadagna `operation_outcomes`, `final_positions` e `movement_ends` (default vuoti); `assemble_session_outcome` tre parametri
   omonimi; la funzione pura `operation_outcome` (le tre regole `ALL`/`ANY`/`MAIN_MISSION`); `MissionStatus.IN_PROGRESS`, `OperationStatus`, `OperationOutcome`; il modulo nuovo `Command/Campaign_Types.py` (`SessionRules`, `CampaignLedger`,
   `ReadyRecord`, `SessionRecord`, `ViolationCode`, `SessionViolation`, `SessionValidationError`); il docstring «Cosa NON c'è» riscritto (le finestre di sessione di campagna esistono).
2. **Scheduler** (capitolo 3): **invariato** (usato solo per `position_on_legs`).
3. **Risolutore** (capitolo 4): **invariato**.
4. **Applicazione dello stato** (capitolo 5): invariata; il rifornimento, assente da questo strato, ha ora un chiamante fuori (`Readiness._rearm_and_refuel`).
5. **Orchestratore** (capitolo 6 §6.1, §6.5-6.8, §6.11, §6.19, §6.21, nuove **§6.24-6.27**): il warning per le missioni oltre la fine (E4), `session_blocks`, `F8_IN_PROGRESS` e il ramo `IN_PROGRESS` dello stato di missione,
   la porta di uscita con i tre dati per la campagna (§6.24); **il validatore di sessione** (§6.25), **la prontezza degli asset e i processi fra sessioni** (§6.26), **il conduttore di campagna e la posizione persistente** (§6.27);
   un interruttore nuovo (15 nel modulo).
6. **Supporto trasversale** (capitolo 7, nuova **§7.13**): le tabelle dei tempi di turnaround e riparazione in `Context/Context.py` con provenienza e livello di verifica di ogni valore (una sola fonte verificata; turnaround navale = stima senza fonte
   numerica) e `Campaign_State` (`restore_position`, `add_ledger`/`get_ledger`).
7. **Validazione** (capitolo 8 §8.3-8.4, §8.7, nuova **§8.12**): scenario **S30-CAMPAIGN** (4 esecuzioni, 10 test), fotografia a **986** esecuzioni con la cronologia da 982, i test aggiunti (146 netti, 4555 → 4701); dal 2026-10-29 anche **S30-ABSENT**
   (3 esecuzioni, 4 test), fotografia a **989**, suite **4710** (+9 netti per il difetto 26).
8. **Limiti** (capitolo 9): superati «missioni fuori finestra tagliate in silenzio», «missione sul posto `FAILED`», «esito d'Operazione non calcolato», «nessun produttore dei validatori», «posizione non persistente», «rifornimento assente», «F6-B3 aperto»; nuova sezione
   **«Limiti della campagna (F8)»**; stato del piano (§9.5) con F8a-F8c e F8-R fatte, F8d non fatta, F6-B3 chiuso; incoerenze (§9.6): **voci 7, 11 e 23 chiuse, voci 24-27 nuove**; verificato che nel manuale non resta nessuna affermazione su un «TOT comune» d'Operazione (voce 15).

**Riferimenti `:riga`.** Quelli delle sezioni nuove o riscritte sono stati verificati sul codice a `fa5fbf1e`. Quelli delle sezioni preesistenti sono stati **ricalcolati** con lo stesso metodo degli aggiornamenti
precedenti, automatizzato: la mappa delle righe da `git diff -U0 dcedc541..HEAD` per ogni modulo cambiato, spostando un riferimento solo se la riga (o l'estremo dell'intervallo) cade fuori da un blocco modificato e il testo della riga è
identico nelle due versioni. Il modulo a cui un riferimento senza percorso (`` `:riga` ``) si riferisce è stato dedotto dal contesto e controllato sull'identificatore citato nel testo vicino; nei capitoli 1, 3, 4, 5, 7 (file `02`, `04`-`06`, `08`)
sono stati rimappati solo i riferimenti con percorso esplicito, perché lì un riferimento breve punta quasi sempre a moduli **non cambiati** (`Contact_Scheduler`, `Engagement_Resolver`, `Fuel_Model`...), mentre nei capitoli 2, 6, 8, 9
(file `03`, `07`, `09`, `10`) sono stati rimappati anche quelli brevi, con revisione a mano dei casi in cui il file non era univoco (per esempio i riferimenti di §6.10 a `Mission_Adapter` e quelli di §2.7 a `Context`) e correzione di quelli
che cadevano in righe riscritte (`assemble_session_outcome`, `run_session`). Un controllo automatico del tipo «l'identificatore citato compare entro due righe dal riferimento» sui riferimenti di forma `` `nome` (`:riga`) `` ha trovato 45 mancanze su
324 riferimenti controllati: 39 stanno nei capitoli 3, 4, 5 e 7 (31 nel capitolo 4) e riguardano moduli **non cambiati** dalla F8 (già imprecise prima, perché la riga punta al corpo di una funzione e non alla sua definizione, o spostate da
modifiche anteriori): **non sono state corrette**, come nell'aggiornamento precedente; le altre 6 (2 nel capitolo 2, 3 nel capitolo 6, 1 nel capitolo 9) puntano al corpo di una funzione o a un modulo invariato. I riferimenti a moduli non toccati restano quelli di prima.

**Aggiornamento 2026-10-18 → 2026-10-20 (da `a784a9e7` a `dcedc541`, fase F7: F7a e F7b)**, in ordine di capitolo. I commit
sono `9f87a3ad` (F7a), `3cbb4226` (correzione dei dati dei loadout A-10C), `d1686b28` (pulizia documentale: commenti e docstring,
voci 14-18 di §9.6), `dcedc541` (F7b); gli altri commit del tratto (`234071d3`, il manuale precedente; `35c1336d`, `4f6fa196`, `6c3be1e9`,
`40c2813a`, proposta e decisioni della F7; `75c5b6c3`, `cac668d5`, `61c094e5`, `9b788342`, `256fb256`, `96a01bb4`, `f2d19dd0`, memoria,
protocollo multi-LLM e strumenti) non toccano nessun file sotto `Code/` (verificato con `git show --name-only` su ciascuno). Il codice
toccato è `Command/Mission_Types.py` (1250 → 1341 righe), `Context/Context.py` (2149 → 2225), `Logic/Engagement_Resolver.py` (3445 → 3872),
`Logic/Fire_Control.py` (810 → 1088), `Logic/Mission_Adapter.py` (1776 → 1973), `Logic/Session_Simulator.py` (2851 → 3102),
`Command/Session_Types.py` (556 → 558, un docstring) e il dato `Asset/Aircraft_Loadouts.py` (5 righe), più il **modulo nuovo**
`Logic/Area_Fire.py` (326 righe) e test, scenari e fotografia. `Logic/Contact_Scheduler.py`, `Logic/Damage_Model.py`, `Logic/Fuel_Model.py`,
`Asset/Asset.py` e tutti i moduli di supporto trasversale restano invariati.

1. **Strato 0, porte e tipi della Missione** (capitolo 2 §2.2, §2.6-2.8): le porte non cambiano; `Target.asset_ids`,
   `MissionAsset.weapons` e `designated_weapons`, `FIRE_AT_POINT_ACTION` e la sua validazione; la tabella
   `Context.MISSION_WEAPON_POLICY` (politica d'armi per tipo di missione, dato non tarato); lo slot `mission_id` dell'RNG ora usato.
2. **Scheduler** (capitolo 3): **invariato**.
3. **Risolutore e fire control** (capitolo 4 §4.4, §4.11-4.12, §4.14, §4.16, nuove **§4.32-4.34**): `TargetRules` e le regole di
   bersaglio (strato T: bersaglio designato, cinque ROE, armi designate, `priority_designated` a due fasi, `return_fire`, candidati
   rimandati e tipo di evento `_WAKE`); la politica d'armi come involucro della fire control (strato W: `restrict_by_policy`,
   `WeaponPolicy`, `target_class`); `area_fire_weapon` e `area_fire_pk` per il fuoco su posizione.
4. **Applicazione dello stato** (capitolo 5): invariata; `apply_engagement_result` accetta già un esito con `forces=()` (fuoco su posizione).
5. **Orchestratore** (capitolo 6 §6.1-6.2, §6.7-6.10, §6.18, §6.21, nuove **§6.22-6.23**): il **terzo tipo di evento di sessione**
   (`ENGAGEMENT=0 < AREA_FIRE=1 < MOVEMENT=2`), il cablaggio delle regole d'ingaggio (`weapon_policies`, `target_rules`, memoria di
   `return_fire`), le quattro funzioni nuove di `Mission_Adapter`, il controllo del loadout, `Logic/Area_Fire.py` con le costanti
   STIMATE, **tre interruttori nuovi** (14 nel modulo).
6. **Supporto trasversale** (capitolo 7 §7.7, §7.12): la `fire_control` avvolta dall'involucro, `target_rules` come ingresso ricavato
   dalle missioni, la correzione dei dati A-10C (`self_escort_capability`).
7. **Validazione** (capitolo 8 §8.4, §8.6-8.7, nuova **§8.11**): scenari **S28** (52 esecuzioni) e **S29** (12), S19AD migrato dai
   filtri di test alle regole di missione, fotografia a **982** esecuzioni con la cronologia da 918, `Test_Area_Fire` (49 test).
8. **Limiti** (capitolo 9): nuovi limiti della F7a e della F7b (costanti STIMATE del fuoco su posizione); superati «nessun filtro
   per missione/bersaglio», «salva su area non rappresentabile»; stato del piano (§9.5) con F7a e F7b fatte; incoerenze (§9.6):
   **voci 14-18 chiuse**, voci 11, 12, 19, 21 riverificate (12 chiusa; 11, 19, 21 aperte), nuove 22-23.

**Riferimenti `:riga`.** Quelli delle sezioni nuove o riscritte sono stati verificati sul codice a `dcedc541`. Quelli delle sezioni
preesistenti sono stati **ricalcolati** con un allineamento riga per riga fra `a784a9e7` e `dcedc541`: per ogni modulo cambiato si è
costruita la mappa delle righe dai blocchi di `git diff -U0`, e un riferimento è stato spostato solo se la riga (o l'estremo
dell'intervallo) cade fuori da un blocco modificato e il testo della riga è identico nelle due versioni; per un intervallo la cui
fine coincide con un'inserzione *in coda* a un blocco (per esempio una proprietà aggiunta a una classe) l'estremo è stato rivisto a
mano; i riferimenti a righe riscritte (docstring della F7a o della pulizia `d1686b28`) sono stati rivisti a mano. Il modulo a cui un
riferimento senza percorso (`` `:riga` ``) si riferisce è stato dedotto dal contesto e controllato sull'identificatore citato; i
riferimenti a moduli non cambiati (per esempio `Contact_Scheduler`, `Fuel_Model`, `Doctrine`) sono rimasti quelli di prima. **Non è stato
rifatto un controllo indipendente di ogni riferimento già scorretto prima dell'allineamento**: ne è emerso uno, `_fire_control` a
`:2058-2079` nel capitolo 4 §4.4 (a `a784a9e7` il metodo stava a `:2293`), corretto.

**Stato del codice descritto, storia degli aggiornamenti.** Stesura iniziale al commit `f61aa2b7`
(2026-09-23); aggiornamenti a `1d0c1127` (2026-09-26), `6754bf1c` (2026-09-27; manuale committato in
`fb914f0e`), `533cd1f5` (2026-10-05; manuale committato in `004d26e8`), `84a47670` (2026-10-11; manuale committato in `355b1017`), `a784a9e7`
(2026-10-18; manuale committato in `234071d3`), `dcedc541` (2026-10-20; manuale aggiornato in questa sede) e, ora, `fa5fbf1e` (2026-10-23). Il motore è
**completo** nelle sue 7 fasi originali (wiki
`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md`); tutto ciò che è venuto dopo è
estensione: fino al 2026-09-27 sui moduli satellite che lo alimentano dall'esterno (selezione dell'arma,
nebbia di guerra, scorta per arma, cannone di bordo, volumi di rilevamento/intercettazione, pianificatore
d'attacco), dal 2026-09-28 **anche nel risolutore e nella porta di sessione**, e dal 2026-10-05 nella
**definizione di "forza d'ingaggio"**, dal 2026-10-11 nel **tempo** (presenza, carburante, episodi), dal 2026-10-18 nelle **regole
d'ingaggio di missione** (contro chi e con che arma si spara) e nel **fuoco su posizione** e, dal 2026-10-22, nel **ciclo di campagna intorno al motore** (validatore di sessione,
prontezza degli asset, posizione persistente: fase F8, quasi tutta *fuori* da `run_session`).

**Aggiornamento 2026-10-11 → 2026-10-18 (da `84a47670` a `a784a9e7`, fasi F5, F6 e passi G1-G5)**, in ordine di capitolo. Il
codice toccato è `Command/Mission_Types.py`, `Command/Session_Types.py`, `Asset/Aircraft.py`, `Logic/Contact_Scheduler.py`,
`Logic/Engagement_Resolver.py`, `Logic/Fire_Control.py`, `Logic/Fuel_Model.py` (da 165 a 1576 righe),
`Logic/Mission_Adapter.py` (da 926 a 1776), `Logic/Session_Simulator.py` (da 937 a 2851), più test, scenari e fotografia;
`Logic/Damage_Model.py`, `Asset/Asset.py` e tutti i moduli di supporto trasversale restano invariati.

1. **Strato 0, porte** (capitolo 2 §2.3-2.4, §2.6, §2.8): `SessionOutcome.postures` (F5-B) e il parametro `chained` di
   `assemble_session_outcome` (G4a, niente più warning sui bersagli condivisi); un `ForceOutcome` per forza **e per episodio**;
   `Operation` senza TOT comune (il TOT è di ogni missione); `AssetMissionOutcome.crew_recovered`, `AssetEndReason` a 12
   valori (`FUEL_EXHAUSTED`, `DISENGAGED`), `AbortReason` a 7 (`BINGO`, `DISENGAGED`); i validatori del carburante **non**
   sono chiamati da `run_session`.
2. **Scheduler** (capitolo 3 §3.6-3.8): `GroundedSchedule` (aerei a terra nel tempo, finestre spezzate a decollo e
   atterraggio), parametri `legs` e `only_assets` di `schedule_contacts`, `trim_contact_window`.
3. **Risolutore** (capitolo 4 §4.9, §4.12-4.13, §4.30, nuova §4.31): `grounded` dipendente dal tempo, la **fine di attività**
   (`ActivityCriteria`, `ActivityEnd`, `activity_criteria`), `Fire_Control.weapon_category`; il risolutore **non legge il
   carburante** e non sa che l'ingaggio è un episodio.
4. **Applicazione dello stato** (capitolo 5 §5.2, riscritta): `Fuel_Model` per tratto e nel tempo, esaurimento a monte e
   residuo analitico, planata, bingo (storia F6-B2/B2bis), riserva di disimpegno (G1), soglia e **albero di decisione** (G2,
   diagramma D38), consumo in ingaggio (G3), uscita di scena (G4b), tipi (D39).
5. **Orchestratore** (capitolo 6 §6.1-6.11, §6.14, nuove §6.15-6.21): coda in due passi, episodi, RNG con `counter`;
   presenza e postura nell'esito (D41), attese e TOT per missione, carburante e vincolo del movimento (D42), fine di attività
   e regola unica dello stato di missione (D19 aggiornato), bingo in sessione e validatori, consumo in ingaggio, episodi e
   ri-pianificazione (D40), tabella degli **interruttori** e dei loro default.
6. **Supporto trasversale** (capitolo 7 §7.6-7.7): `Aircraft.fuel_capacity_kg` e il nuovo `Aircraft.emergency_fuel_flow`
   (dato non tarato, unità dedotta), nuovi ingressi del risolutore ricavati dalle missioni, assenza di punti di iniezione
   per il carburante.
7. **Validazione** (capitolo 8 §8.4, §8.7, §8.10): scenari **S22-S27**, S5 a otto varianti, la fotografia a **918**
   esecuzioni con la cronologia da 370, l'opzione `--ignore`, i test aggiunti per modulo.
8. **Limiti** (capitolo 9): superati i limiti su presenza, attese, esito di prima forma, carburante e re-scheduling; nuovi i
   limiti della deviazione 22 del Piano (dati `emergency` non tarati, regola WW2 non implementata, validatori fuori da
   `run_session`, nessuna salva dopo il bingo, F6-B3 aperto, S27 senza intercettori aerei veri, ...); stato del piano (§9.5);
   incoerenze documenti/codice (§9.6, voci 15-21 nuove).

**Riferimenti `:riga`.** Quelli delle sezioni nuove o riscritte sono stati verificati sul codice a `a784a9e7`. Quelli delle
sezioni preesistenti sono stati **ricalcolati** con un allineamento riga per riga fra `84a47670` e `a784a9e7` (le righe
invariate seguono lo spostamento, con la verifica che il testo della riga sia identico; i riferimenti a righe riscritte sono
stati rivisti a mano). Non sono stati ricalcolati i riferimenti ai moduli **non toccati** dal `git diff` (restano validi) né
quelli storici esplicitamente datati (per esempio «a `533cd1f5` quelle righe erano ...»).

**Aggiornamento 2026-10-05 → 2026-10-11 (da `533cd1f5` a `84a47670`, fase F4 della Missione)**, in ordine di
capitolo. Il codice toccato è `Command/Session_Types.py`, `Logic/Contact_Scheduler.py`,
`Logic/Engagement_Resolver.py`, `Logic/Fire_Control.py`, `Logic/Mission_Adapter.py`, `Logic/Session_Simulator.py`
(più test, fixture e fotografia); nessun altro modulo di supporto è cambiato.

1. **Strato 0, porte** (capitolo 2 §2.2-2.3, §2.8): le porte non cambiano di forma, cambia il significato di
   `force_id` negli esiti (ora il `mission_id`); `ForceOutcome.block_id` e `SessionOutcome.outcomes_of_block`
   (l'esito di un blocco è un *insieme* di esiti di missione, non un esito sintetico); `SessionOrder.committed`
   resta per blocco; il `mission_id` entra nell'RNG attraverso l'`event_id`.
2. **Scheduler** (capitolo 3 §3.5-3.6): il parametro `grounded` di `schedule_contacts` e i flag
   `grounded_a`/`grounded_b` di `mutual_detection_ranges`/`contact_windows` (un aereo a terra come bersaglio è
   interrogato nel modo `'ground'`, come osservatore non ha portata); la potatura per blocco è invariata e
   conservativa.
3. **Risolutore** (capitolo 4 §4.1, §4.4-4.5, §4.7-4.8, §4.10-4.15, §4.23-4.26, nuove §4.27-4.30): la forza è la
   missione (`can_disengage` dichiarato, `block_id`, §4.27); il **dominio di coordinamento** (`coordination_of`:
   ripartizione del fuoco, saturazione, lanciatori prioritari e percezione condivisi, §4.28); la **difesa di
   salva per dominio** (`domain_interceptors`, `instant_interceptions`; `_capacity` rimossa, §4.29); gli **aerei a
   terra** (`grounded`, keyword `target_grounded` verso la fire control, classe `'Soft'`, peso di minaccia nullo,
   nessun disingaggio, §4.30).
4. **Orchestratore** (capitolo 6 §6.1-6.4, §6.7-6.14): la validazione con la regola A
   (`Mission_Adapter.check_mission_speed`); `_engagement_forces` e la vista `MissionForce` (§6.12);
   `coordination_domains` (§6.13); `continuous_posture` e `grounded_assets` (§6.14); componenti connesse anche
   per dominio.
5. **Supporto trasversale** (capitolo 7 §7.7): l'estensione facoltativa `target_grounded` del protocollo di
   `fire_control`; `coordination_of` e `grounded` come ingressi ricavati dalle missioni.
6. **Validazione** (capitolo 8 §8.1, §8.4, §8.6-8.9): regola A negli scenari (`_slowest_reference`), ruolo
   `'parked'`, letture per forza d'ingaggio; scenari **S20**, **S21**, **S21R**; test S3 e S5 riprogettati; la
   fotografia di non regressione a **370 esecuzioni** con `--summary` e il processo di non regressione.
7. **Limiti** (capitolo 9): superati «l'unità d'ingaggio è il blocco», «il `mission_id` non entra nell'RNG»,
   «nessuna condivisione dei rilevamenti»; nuovi i limiti della F4 (nessun cueing, condivisione istantanea,
   canali condivisi solo nello stesso istante, `grounded` per tutta la sessione, nessuno shelter, postura
   `Defense` solo dichiarata, missione di un solo asset `DESTROYED` alla prima perdita, potatura conservativa);
   stato del piano (§9.5) e incoerenze documenti/codice (§9.6, rivista voce per voce).

**Aggiornamento 2026-09-28 → 2026-10-05 (da `6754bf1c` a `533cd1f5`)** (testo conservato per riferimento; i
numeri di riga e di esecuzioni citati qui sono quelli di allora), in ordine di capitolo:

1. **Strato 0, la Missione** (capitolo 2 §2.2-2.9): `Command/Mission_Types.py` (tipi di dominio di Missione,
   Operazione, esiti), la tassonomia dei tipi di missione in `Context/Context.py` (`Mission_Category`, tipi per
   dominio, `AIR_COMBAT_TASK` e `AIR_SUPPORT_TASK`, `MISSION_TYPE_POSTURES`: postura e tipo di missione su due
   assi distinti), `SessionOrder.missions`/`operations` e `SessionOutcome.mission_outcomes`; rename della
   postura `Retrait` → `Retreat`.
2. **Orchestratore** (capitolo 6 §6.1, §6.10-6.11): `run_session` non ha più `routes`/`starts`/`speeds`
   (una sola strada: le missioni); `Logic/Mission_Adapter.py` ricava rotta, partenza e velocità per asset
   (offset di formazione che ruota con la rotta sulla bisettrice); esito di missione di prima forma;
   secondo flusso RNG per la tempra.
3. **Risolutore d'ingaggio** (capitolo 4 §4.5, §4.7, §4.21-4.26): soglia di rottura stocastica; efficacia
   antiaerea E(N) e pesi di minaccia; RWR per classi e modalità, classificazione SAM, regola R-CLS; difesa dai
   missili A6 (capacità `Anti_Missile`, ordine F, regole L1/L2/L3); dottrina di tiro contro l'overkill;
   intercettazione con traccia del colpo e tempo di reazione (R-INT).
4. **Supporto trasversale** (capitolo 7 §7.2, §7.5-7.7, §7.10-7.12): `Doctrine` (parametri della soglia,
   dottrina di tiro), `salvo_interceptors` con regola D, CIWS, `Asset/Aircraft_Rwr_Data.py`,
   `Context/Air_Defense_Efficacy.py`, armi DCS aggiunte (39), KMGU-2, Tu-95MS.
5. **Validazione** (capitolo 8 §8.6-8.8): S19 e S19AD, migrazione degli scenari alle missioni, lo strumento
   di non regressione `Test/Scenario_Baseline.py` (292 esecuzioni, `--capture`/`--compare`).
6. **Limiti** (capitolo 9): limiti nuovi e superati, stato del piano della Missione (§9.5) e le incoerenze
   trovate fra documenti di progetto e codice (§9.6).

A `533cd1f5` i capitoli 3 (scheduler) e 5 (applicazione dello stato) risultavano **invariati**
(`Logic/Contact_Scheduler.py`, `Logic/Damage_Model.py`, `Logic/Fuel_Model.py` non cambiavano da `6754bf1c`); a
`84a47670` il capitolo 5 è ancora invariato nei moduli, mentre lo scheduler (capitolo 3) ha acquisito il
parametro `grounded`.

**Storia degli aggiornamenti precedenti** (testo conservato per riferimento):

- *Nota di perimetro 2026-09-24/25*: selezione dell'arma dai registri (`Logic/Fire_Control.py`, commit
  `15350cc5`) e nebbia di guerra come fattore di rilevamento (`region_recon_detection_factor`, commit
  `388e6ea3`), capitolo 4 §4.16-4.18.
- *2026-09-26 (`1d0c1127`, "Proposta A")*: la scorta **per modello d'arma** (`Mobile._stores`,
  `Asset/Weapon_Stores.py`) sostituisce il contatore aggregato; la regola del "SAM puro" è eliminata;
  capitolo 4 §4.4/§4.5/§4.10/§4.16/§4.17/§4.19, capitolo 7 §7.6.
- *2026-09-26/27 (`4ddbb089`, `8bd69727`, `815dc35f`, `6754bf1c`)*: finestre di rilascio delle bombe (dato di
  registro), cannone di bordo come arma candidata (capitolo 4 §4.16bis), volumi di rilevamento e
  intercettazione distinti nel pianificatore di rotta (capitolo 7 §7.8), pianificatore d'attacco con quota e
  profilo di sgancio (capitolo 4 §4.20, capitolo 7 §7.9).

## Convenzioni di questo manuale

- Ogni affermazione su codice è verificata leggendo il file, con riferimento `percorso:riga`
  valido per `fa5fbf1e`. I percorsi sono dati **relativi a `Code/Dynamic_War_Manager/Source/`** (es.
  `Logic/Engagement_Resolver.py:2474` sta per
  `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py:2474`); dentro una sezione una forma breve
  `` `:riga` `` si riferisce al file nominato nell'intestazione del capitolo o della sezione. I documenti di
  progetto sono citati con il percorso sotto `Analysis/Document/`.
- I diagrammi sono in blocchi ```mermaid```, tenuti piccoli e leggibili: dove un diagramma
  avrebbe avuto decine di nodi è stato spezzato in più diagrammi per strato o per famiglia di
  tipi.
- "STIMA DICHIARATA" (termine che ricorre nel codice) significa: un numero o una forma
  funzionale scelta come punto di partenza plausibile, non calibrata su dati validati, con la
  provenienza dichiarata nel codice stesso. Questo manuale le riporta come tali, senza
  presentarle come dati misurati.
- Dove il manuale e la wiki di progetto (`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/`)
  divergono, prevale il codice; le divergenze trovate sono raccolte nel capitolo 9 (§9.2 per la wiki,
  §9.6 per i documenti di progetto della Missione e delle regole SAM, con lo stato di ciascuna voce).
- I diagrammi hanno un numero progressivo `D1`-`D129` (elenco in fondo; D88 e D89 non sono usati): D1-D56 nei capitoli 1-8, D57-D129 nel capitolo 10 (atlante, parti 10, 10A, 10B, 10C); le didascalie sono nel capitolo
  che li contiene. Il capitolo 10 assegna ogni diagramma a un livello di dettaglio (L0-L4).

## Indice dei capitoli

1. [Scopo e motivazioni](02_Scopo_e_Motivazioni.md) — perché un DES a coda eventi e non il tick
   a 1 ms, i quattro strati, i vincoli di progetto non negoziabili.
2. [Lo strato 0: il contratto delle porte](03_Strato0_Contratto_Porte.md) —
   `Command/Session_Types.py`: `SessionOrder`, `SessionOutcome`, `assemble_session_outcome`; dal
   2026-10-05 le missioni alla porta (`SessionOrder.missions`/`operations`, `mission_outcomes`),
   `Command/Mission_Types.py` (§2.6) e la tassonomia dei tipi di missione di `Context/Context.py` (§2.7); dal
   2026-10-08 `ForceOutcome.block_id` e `SessionOutcome.outcomes_of_block` (§2.3), il `mission_id` nell'RNG
   (§2.8); **dal 2026-10-12/18** `SessionOutcome.postures`, `chained`, `Operation` senza TOT comune,
   `crew_recovered` e i nuovi motivi di fine e di aborto (§2.3, §2.4, §2.6); **dal 2026-10-18/20** `Target.asset_ids`,
   `MissionAsset.weapons`, l'azione `Fire_At_Point` e la tabella della politica d'armi per tipo di missione (§2.6, §2.7);
   **dal 2026-10-22/23 (fase F8)** i tre campi della campagna di `SessionOutcome` (`operation_outcomes`, `final_positions`, `movement_ends`, §2.3), la funzione `operation_outcome` (§2.4),
   `MissionStatus.IN_PROGRESS` e `OperationOutcome` (§2.6) e il modulo nuovo `Command/Campaign_Types.py` (registro di campagna, regole di finestra, violazioni, **§2.10**).
3. [Lo strato 1: lo scheduler dei contatti](04_Strato1_Scheduler_Contatti.md) —
   `Logic/Contact_Scheduler.py`: rotta↔cilindro, CPA/TCPA, potatura gerarchica,
   `ContactWindow`; dal 2026-10-11 il parametro `grounded` per gli aerei a terra (§3.5-3.6); **dal 2026-10-12/17**
   `GroundedSchedule` (§3.7), `legs` e `only_assets` (§3.6), `trim_contact_window` (§3.8).
4. [Lo strato 2: il risolutore d'ingaggio](05_Strato2_Risolutore_Ingaggio.md) —
   `Logic/Engagement_Resolver.py`: rilevamento, latenze di reazione, salva di Hughes,
   saturazione, disingaggio, ingaggi a N forze; `Logic/Fire_Control.py` (selezione dell'arma dai
   registri e controllo di portata, §4.16-4.17; cannone di bordo candidato, §4.16bis); nebbia di
   guerra come fattore di rilevamento da ricognizione (§4.18); scorta per modello d'arma,
   `Asset/Weapon_Stores.py` (§4.19); gittata e caduta delle bombe dalla balistica di
   `Weapon_Delivery`, §4.20; **dal 2026-09-28**: soglia di rottura stocastica (§4.7, §4.21), efficacia
   antiaerea E(N) (§4.22), RWR e classi SAM con regola R-CLS (§4.23), difesa dai missili A6 con regole
   D/F/L1/L2/L3 (§4.24), dottrina di tiro contro l'overkill (§4.25), intercettazione con tempo di reazione
   R-INT (§4.26); **dal 2026-10-08 (fase F4 della Missione)**: la forza d'ingaggio è la missione (§4.27), il
   dominio di coordinamento per fuoco e percezione (§4.28), la difesa di salva per dominio (§4.29), gli aerei a
   terra e la postura continua (§4.30, esteso dalla F5 al tempo); **dal 2026-10-12**: la fine di attività dei
   criteri di missione (§4.31); **dal 2026-10-18/20 (fase F7 della Missione)**: le regole di bersaglio di missione nel risolutore
   (§4.32), la politica d'armi per tipo di missione come involucro della fire control (§4.33) e l'arma per il fuoco su posizione
   (§4.34).
5. [Lo strato 3: applicazione dello stato](06_Strato3_Applicazione_Stato.md) —
   `Logic/Damage_Model.py`, `Asset.apply_damage`, `Logic/Fuel_Model.py` (riscritta: carburante per tratto, planata, bingo,
   riserva di disimpegno, albero di decisione, consumo in ingaggio, §5.2), `apply_engagement_result`.
6. [L'orchestratore: `Session_Simulator.run_session`](07_Orchestratore_Session_Simulator.md) —
   componenti connesse e **episodi d'ingaggio**, coda eventi di sessione in due passi, RNG con `counter`; la firma senza
   `routes`/`starts`/`speeds`, `Logic/Mission_Adapter.py` (§6.10) e l'esito di missione a regola unica (§6.11); le forze
   d'ingaggio e la vista `MissionForce` (§6.12), il dominio di coordinamento (§6.13), la postura continua (§6.14);
   **nuove §6.15-6.21**: presenza e postura nell'esito, attese e TOT per missione, carburante e vincolo del movimento, fine di
   attività, bingo e validatori, consumo in ingaggio / episodi / ri-pianificazione / uscita di scena, interruttori e default;
   **nuove §6.22-6.23 (F7)**: le regole d'ingaggio di missione in sessione e il fuoco su posizione (`Logic/Area_Fire.py`, terzo
   tipo di evento di sessione); **nuove §6.24-6.27 (F8)**: l'esito per la campagna (`final_positions`, `movement_ends`, `operation_outcomes`, stato `IN_PROGRESS`), il validatore di sessione
   (`Logic/Session_Validator.py`), la prontezza degli asset e i processi fra sessioni (`Logic/Readiness.py`), il conduttore di campagna e la posizione persistente (`Logic/Session_Campaign.py`).
7. [Moduli di supporto trasversali](08_Supporto_Trasversale.md) — `Session_Rng`, `Doctrine`,
   `Reaction_Profile`, le dimensioni militari di `Military`, munizioni/carburante su
   `Mobile`/`Aircraft` (con `fuel_capacity_kg` e `emergency_fuel_flow`), i punti di iniezione meteo (`detection_factor`) e arma
   (`fire_control`, con l'estensione facoltativa `target_grounded`) e della soglia di rottura (`morale_for`,
   `enemy_estimate_for`, `fire_doctrine`, `rwr_catalogue`); `Doctrine` con parametri della soglia e dottrina di
   tiro (§7.2); `Asset/Aircraft_Rwr_Data.py` (§7.10), `Context/Air_Defense_Efficacy.py` (§7.11), dati di registro
   aggiunti (§7.12, compresa la correzione dei loadout A-10C); la `fire_control` avvolta dalla politica d'armi e `target_rules`
   come ingresso ricavato dalle missioni (§7.7); il pianificatore di rotta aerea con volumi di rilevamento e
   intercettazione distinti (§7.8, `Logic/Air_Route_Manager.py`) e il pianificatore d'attacco
   a monte del motore (§7.9, `Logic/Weapon_Delivery.py`, `Command/Attack_Types.py`); **nuova §7.13 (F8)**: i tempi di turnaround e riparazione in `Context/Context.py`
   con la provenienza e il livello di verifica di ogni valore, e `Context/Campaign_State.py` (`restore_position`, `add_ledger`/`get_ledger`).
8. [Validazione](09_Validazione.md) — determinismo, test di agnosticismo come test di
   contratto (esteso alle porte della Missione), la batteria di scenari S1-S30 (§8.4), la
   migrazione alle missioni e la regola A negli scenari, lo strumento di non regressione
   `Test/Scenario_Baseline.py` con il processo di non regressione e la cronologia della fotografia fino a 989 esecuzioni
   (§8.7), i test aggiunti (§8.8), gli scenari della fase F4 (§8.9), gli scenari S22-S27 e i test delle fasi F5, F6 e
   G1-G5 (§8.10), gli scenari S28-S29 e i test della fase F7 (§8.11), **gli scenari S30-CAMPAIGN e S30-ABSENT e i test della fase F8 (§8.12)**.
9. [Limiti noti, punti di estensione e divergenze codice/wiki](10_Limiti_Estensioni_Divergenze.md) —
   limiti nuovi e superati (compresi quelli della fase F4, delle fasi F5, F6, G1-G5, della fase F7, con le costanti STIMATE
   del fuoco su posizione, e **della campagna, F8**, con i tempi non tarati e l'assenza di logistica), stato del piano della Missione F0-F9 e dei passi G1-G5 (§9.5, F8a-F8c e F8-R fatte,
   F8d non fatta, F6-B3 chiuso), incoerenze trovate fra documenti di progetto e codice (§9.6, con lo stato di ciascuna voce: voci 7, 11 e 23 chiuse, **voci 24-27 nate con la F8 e chiuse il 2026-10-29**).
10. [Atlante dei diagrammi](11_Atlante_Diagrammi.md) — la scala dei livelli L0-L4 (contesto, architettura, moduli, interazione, algoritmo), la tabella-atlante di tutti i diagrammi
    e lo stato di copertura per modulo; i diagrammi nuovi **D57-D66**: contesto del core (D57), grafo reale degli import in tre parti (D58-D60), `Session_Simulator` e `Mission_Adapter` (tipi, gruppi di funzioni e
    tabelle complete con `:riga`, D61-D63), la sequenza di chiamate di `run_session` in tre parti (D64-D66). Verificato a `f009eb43`.
    Estensione a tutto il core in tre parti, ciascuna con la tabella completa dei simboli (`:riga`) di ogni modulo: **parte A**
    [`11a_Atlante_Risolutore.md`](11a_Atlante_Risolutore.md) (`Contact_Scheduler`, `Fire_Control`, `Engagement_Resolver`, D67-D87), **parte B**
    [`11b_Atlante_Missione_Carburante.md`](11b_Atlante_Missione_Carburante.md) (`Mission_Types`, `Fuel_Model`, `Area_Fire`, D90-D109), **parte C**
    [`11c_Atlante_Porte_Campagna.md`](11c_Atlante_Porte_Campagna.md) (`Session_Types`, `Campaign_Types`, `Session_Validator`, `Session_Campaign`, `Readiness`,
    `Damage_Model`, `Session_Rng` e la mappa dei dati, D110-D129). Ogni parte ha una sezione «Limiti e domande» con le cose non ovvie trovate nel codice.

## Elenco dei diagrammi

| # | Diagramma | Tipo mermaid | Capitolo |
|---|---|---|---|
| D1 | Moduli e dipendenze dei quattro strati | `flowchart TD` | 1 |
| D2 | Tipi di dominio — porte di sessione (`SessionOrder`/`SessionOutcome`) | `classDiagram` | 2 |
| D3 | Tipi di dominio — geometria dei contatti (`Contact_Scheduler`) | `classDiagram` | 3 |
| D4 | Tipi di dominio — ingaggio (`Engagement_Resolver`) | `classDiagram` | 4 |
| D5 | Sequenza della coda eventi dentro un ingaggio | `sequenceDiagram` | 4 |
| D6 | Stati di una forza durante un ingaggio | `stateDiagram-v2` | 4 |
| D7 | Stati operativi di un asset (salute) | `stateDiagram-v2` | 5 |
| D8 | Flusso dati di `run_session` | `flowchart TD` | 6 |
| D9 | Coda eventi di sessione (ENGAGEMENT/MOVEMENT) | `sequenceDiagram` | 6 |
| D10 | `Fire_Control`: catena di selezione dell'arma dai registri | `flowchart TD` | 4 |
| D11 | Controllo di portata: rimando `not_before` di un candidato | `sequenceDiagram` | 4 |
| D12 | Nebbia di guerra: composizione del fattore di rilevamento | `flowchart TD` | 4 |
| D13 | Scorta per modello d'arma: dalla fire control al consumo | `flowchart TD` | 4 |
| D14 | Volumi di rilevamento e intercettazione: tipi e modalità del pianificatore di rotta | `classDiagram` | 7 |
| D15 | Il pianificatore d'attacco: da `plan_attack_profile` all'`AttackProfile`, verso DES e DCS | `flowchart TD` | 7 |
| D16 | Modello dei tipi della Missione (`Mission`, `MissionAsset`, `MissionWaypoint`, ...) | `classDiagram` | 2 |
| D17 | Esiti della Missione (`MissionOutcome`, `AssetMissionOutcome`) | `classDiagram` | 2 |
| D18 | I due assi: postura tattica e tipo di missione | `flowchart LR` | 2 |
| D19 | Esito di missione, regola unica (era: prima forma) | `flowchart TD` | 6 |
| D20 | Pipeline di `Mission_Adapter` | `flowchart TD` | 6 |
| D21 | Offset di formazione ai cambi di direzione | `flowchart TD` | 6 |
| D22 | Composizione della soglia di rottura B(t) | `flowchart TD` | 4 |
| D23 | Minaccia percepita: sistema esatto o classe RWR (R-CLS) | `flowchart TD` | 4 |
| D24 | Allocazione delle intercettazioni per salva (ordine F, L1, R-INT; intercettori del dominio) | `flowchart TD` | 4 |
| D25 | Priorità ai lanciatori: prelazione L3 (registrata sul dominio) | `sequenceDiagram` | 4 |
| D26 | Dottrina di tiro: bersagli bloccati, attesa, round-robin (saturazione per dominio) | `flowchart TD` | 4 |
| D27 | Regola R-INT: traccia del colpo e tempo di reazione | `flowchart TD` | 4 |
| D28 | `Air_Defense_Efficacy`: profili, dati RWR, funzioni | `classDiagram` | 7 |
| D29 | Fasi F0-F9 del piano della Missione e passi G1-G5 | `flowchart LR` | 9 |
| D30 | La vista di missione `MissionForce` e ciò che il risolutore ne legge | `classDiagram` | 6 |
| D31 | Come `_engagement_forces` costruisce le forze di un blocco | `flowchart TD` | 6 |
| D32 | Che cosa condivide un dominio di coordinamento e che cosa resta per forza | `flowchart LR` | 4 |
| D33 | Difesa di salva per dominio e canali condivisi nello stesso istante | `flowchart TD` | 4 |
| D34 | Come l'insieme `grounded` attraversa scheduler, risolutore e fire control | `flowchart TD` | 4 |
| D35 | Regole di unione di `coordination_domains` | `flowchart TD` | 6 |
| D36 | Postura continua di un asset senza missione | `flowchart TD` | 6 |
| D37 | Fine di attività: come il risolutore applica `ActivityCriteria` | `flowchart TD` | 4 |
| D38 | Albero di decisione al bingo (`Fuel_Model.bingo_decision`) | `flowchart TD` | 5 |
| D39 | Tipi di `Fuel_Model` (`FuelEvent`, `FuelExhaustion`, `ReturnRule`, `BingoPoint`, `BingoDecision`) | `classDiagram` | 5 |
| D40 | Ciclo episodio → ri-pianificazione → ri-scheduling dei contatti → contabilità del carburante | `sequenceDiagram` | 6 |
| D41 | Ciclo di vita di un aereo di missione in sessione | `stateDiagram-v2` | 6 |
| D42 | Composizione dei tratti di un asset prima dello scheduler (bingo alla partenza, esaurimento) | `flowchart TD` | 6 |
| D43 | Come `_fire_control` e `_schedule_next` applicano le regole di bersaglio di missione | `flowchart TD` | 4 |
| D44 | Le due fasi di `priority_designated` | `stateDiagram-v2` | 4 |
| D45 | `return_fire`: attesa di un ostile e risveglio `_WAKE` | `sequenceDiagram` | 4 |
| D46 | `WeaponPolicy.allows`: un'opzione d'arma contro una classe di bersaglio | `flowchart TD` | 4 |
| D47 | I tipi nuovi della F7 (`TargetRules`, `WeaponPolicy`, `AreaWeapon`) e chi li consuma | `classDiagram` | 4 |
| D48 | Il cablaggio delle regole d'ingaggio di missione in `run_session` (F7a) | `flowchart TD` | 6 |
| D49 | `resolve_area_fire`: dalla condizione di tiro alle estrazioni | `flowchart TD` | 6 |
| D50 | Il fuoco su posizione nella coda di sessione | `sequenceDiagram` | 6 |
| D51 | I tipi di `Command/Campaign_Types.py` (regole, registro, prontezza, violazioni) | `classDiagram` | 2 |
| D52 | I controlli di `validate_session` | `flowchart TD` | 6 |
| D53 | La regola di `readiness_after_session` per un asset | `flowchart TD` | 6 |
| D54 | Un passo del ciclo di campagna (`run_campaign_session`) | `sequenceDiagram` | 6 |
| D55 | La sequenza di S30-CAMPAIGN e i punti in cui gli asset tornano pronti | `flowchart LR` | 8 |
| D56 | La sequenza di S30-ABSENT e dove sta il record di ciascun asset (difetto 26) | `flowchart LR` | 8 |
| D57 | Il core DES nel suo contesto (livello L0) | `flowchart LR` | 10 |
| D58 | Import reali: porte, scheduler, risolutore, stato (livello L1) | `flowchart TD` | 10 |
| D59 | Import reali: orchestratore, adapter di missione, fuoco su posizione (livello L1) | `flowchart TD` | 10 |
| D60 | Import reali: il ciclo di campagna (livello L1) | `flowchart TD` | 10 |
| D61 | `Session_Simulator`: tipi interni, voce di coda e tipi di evento (livello L2) | `classDiagram` | 10 |
| D62 | `Session_Simulator`: le funzioni per ruolo (livello L2) | `flowchart TD` | 10 |
| D63 | `Mission_Adapter`: i gruppi di funzioni e le loro dipendenze (livello L2) | `flowchart TD` | 10 |
| D64 | `run_session` 1/3: preparazione e validazione (livello L3) | `sequenceDiagram` | 10 |
| D65 | `run_session` 2/3: contatti, episodi, risolutore, stato e ri-pianificazione (livello L3) | `sequenceDiagram` | 10 |
| D66 | `run_session` 3/3: passo finale del carburante, esiti e `assemble_session_outcome` (livello L3) | `sequenceDiagram` | 10 |
| D67 | Tipi dello scheduler con tutti i membri (`Leg`, `ThreatWindow`, `CPA`, `ContactWindow`, `GroundedSchedule`) (livello L2) | `classDiagram` | 10 |
| D68 | Le funzioni dello scheduler per ruolo e le dipendenze fra i gruppi (livello L2) | `flowchart TD` | 10 |
| D69 | `schedule_contacts`: dalla potatura per blocco alle finestre di coppia (livello L3) | `sequenceDiagram` | 10 |
| D70 | `contact_windows`: portate, intervalli, CPA e finestre (livello L3) | `sequenceDiagram` | 10 |
| D71 | Tipi della fire control (`_Weapon`, `WeaponPolicy`, `AreaWeapon`) e `ShotSpec` (livello L2) | `classDiagram` | 10 |
| D72 | Le funzioni della fire control per ruolo e le dipendenze (livello L2) | `flowchart TD` | 10 |
| D73 | La fire control dai registri: dalla coppia (tiratore, bersaglio) alla tupla di `ShotSpec` (livello L3) | `sequenceDiagram` | 10 |
| D74 | L'involucro `restrict_by_policy`: dalla politica d'armi alla chiamata nel risolutore (livello L3) | `sequenceDiagram` | 10 |
| D75 | L'arma per il fuoco su posizione: `area_fire_weapon` e `area_fire_pk` (livello L3) | `sequenceDiagram` | 10 |
| D76 | I tipi interni della run (`_Shadow`, `_Candidate`, `_ForceState`, `_PendingGroup`, `_EngagementRun`) (livello L2) | `classDiagram` | 10 |
| D77 | Le funzioni di modulo e i tipi per ruolo (livello L2) | `flowchart TD` | 10 |
| D78 | Le fabbriche del fattore di rilevamento `detection_factor` (livello L2) | `flowchart TD` | 10 |
| D79 | I metodi di `_EngagementRun` per ruolo 1/2: costruzione, rilevamento, scelta del tiro (livello L2) | `flowchart TD` | 10 |
| D80 | I metodi di `_EngagementRun` per ruolo 2/2: risoluzione, intercettazione, disingaggio, regole F7a (livello L2) | `flowchart TD` | 10 |
| D81 | `resolve_engagement`: validazione, costruzione della run e ciclo principale (livello L3) | `sequenceDiagram` | 10 |
| D82 | `_detect_direction`: una estrazione di rilevamento (livello L3) | `sequenceDiagram` | 10 |
| D83 | `_schedule_next`: l'ordine delle chiamate della scelta del tiro (livello L3) | `sequenceDiagram` | 10 |
| D84 | `_on_launch`: dal lancio alla salva in volo (livello L3) | `sequenceDiagram` | 10 |
| D85 | `_on_resolve`: intercettazione, danno per colpo e dottrina (livello L3) | `sequenceDiagram` | 10 |
| D86 | `apply_engagement_result`: danni e consumi sugli asset reali (livello L3) | `sequenceDiagram` | 10 |
| D87 | Che cosa il core importa da `Engagement_Resolver`, e chi (livello L2) | `flowchart LR` | 10 |
| D90 | Le tredici enumerazioni della Missione con tutti i membri (livello L2) | `classDiagram` | 10 |
| D91 | Gli elementi della Missione con tutti i membri (`Target`, `StartCondition`, `MissionAction`, `MissionWaypoint`, `MissionAsset`) (livello L2) | `classDiagram` | 10 |
| D92 | La Missione e l'Operazione con tutti i membri (`Mission`, `MissionRules`, `EndCriteria`, `Operation`) (livello L2) | `classDiagram` | 10 |
| D93 | Gli esiti con tutti i membri (`AssetMissionOutcome`, `MissionOutcome`, `OperationOutcome`) (livello L2) | `classDiagram` | 10 |
| D94 | Le funzioni di `Mission_Types` per ruolo e le dipendenze fra i gruppi (livello L2) | `flowchart TD` | 10 |
| D95 | `Mission.__post_init__`: l'ordine delle validazioni alla costruzione (livello L3) | `sequenceDiagram` | 10 |
| D96 | Dalla costruzione della Missione alla porta di sessione: `SessionOrder`, `_check_missions`, `validate_session` (livello L3) | `sequenceDiagram` | 10 |
| D97 | Dagli esiti per asset all'esito di sessione: `_mission_outcome`, `operation_outcome`, `assemble_session_outcome` (livello L3) | `sequenceDiagram` | 10 |
| D98 | I tipi di `Fuel_Model` con tutti i membri, compresi `_Step` e `_Segment` (livello L2) | `classDiagram` | 10 |
| D99 | Le funzioni di `Fuel_Model` per ruolo e le dipendenze fra i gruppi (livello L2) | `flowchart TD` | 10 |
| D100 | Il consumo di un tratto: `build_leg_fuel_event`, `build_fuel_event`, `apply_fuel_event` (livello L3) | `sequenceDiagram` | 10 |
| D101 | Esaurimento e residuo analitico: `fuel_exhaustion` e `fuel_at` (livello L3) | `sequenceDiagram` | 10 |
| D102 | La riserva di disimpegno e il consumo in ingaggio: `build_engagement_fuel_event` (livello L3) | `sequenceDiagram` | 10 |
| D103 | Il punto di bingo: `bingo_point` nelle regole F6-B2bis e F6-B2 (livello L3) | `sequenceDiagram` | 10 |
| D104 | L'albero di decisione al bingo: l'ordine delle chiamate di `bingo_decision` (livello L3) | `sequenceDiagram` | 10 |
| D105 | Che cosa il core importa da `Fuel_Model`, e chi (livello L2) | `flowchart LR` | 10 |
| D106 | `FireOrder` e `_Hit` con tutti i membri e i tipi esterni (livello L2) | `classDiagram` | 10 |
| D107 | Le funzioni di `Area_Fire` per ruolo e le dipendenze (livello L2) | `flowchart TD` | 10 |
| D108 | Gli ordini di fuoco: `fire_orders`, `plan_shot` senza scorta, `impact_time` (livello L3) | `sequenceDiagram` | 10 |
| D109 | `resolve_area_fire`: ordine delle chiamate e delle estrazioni (livello L3) | `sequenceDiagram` | 10 |
| D110 | `SessionOrder` con tutti i membri e i tipi da cui dipende (livello L2) | `classDiagram` | 10 |
| D111 | `SessionOutcome` con tutti i membri e i tipi degli eventi che contiene (livello L2) | `classDiagram` | 10 |
| D112 | Le funzioni di `Session_Types` per ruolo e le chiamate fra i gruppi (livello L2) | `flowchart TD` | 10 |
| D113 | `assemble_session_outcome`: controlli, raggruppamento, costruzione e `SessionOutcome.__post_init__` (livello L3) | `sequenceDiagram` | 10 |
| D114 | `ViolationCode`, `SessionRules`, `SessionViolation` e `SessionValidationError` con tutti i membri (livello L2) | `classDiagram` | 10 |
| D115 | `SessionRecord`, `ReadyRecord` e `CampaignLedger` con tutti i membri (livello L2) | `classDiagram` | 10 |
| D116 | La vita del registro: costruzione, `with_session`, `with_readiness` e andata e ritorno su `Campaign_State` (livello L3) | `sequenceDiagram` | 10 |
| D117 | `check_session` e `validate_session`: l'ordine delle chiamate verso registro, simulatore e adapter (livello L3) | `sequenceDiagram` | 10 |
| D118 | `apply_final_positions`: dalle posizioni dell'esito alla posizione degli asset (livello L3) | `sequenceDiagram` | 10 |
| D119 | Le funzioni di `Readiness` per ruolo, le dipendenze e il solo chiamante (livello L2) | `flowchart TD` | 10 |
| D120 | `record_session` e `readiness_after_session`: dal registro vecchio al registro nuovo (livello L3) | `sequenceDiagram` | 10 |
| D121 | Il difetto 26: il record di un asset assente attraverso `apply_campaign_processes` e `readiness_after_session` (livello L3) | `sequenceDiagram` | 10 |
| D122 | `DamageEvent`, le funzioni e le costanti di `Damage_Model` e i tipi che lo usano (livello L2) | `classDiagram` | 10 |
| D123 | `build_damage_event`: controlli, esito e delta di salute dentro il modulo (livello L3) | `sequenceDiagram` | 10 |
| D124 | Il percorso di un `DamageEvent`: dove nasce, dove è applicato, chi lo legge (frecce = dati) (livello L2) | `flowchart LR` | 10 |
| D125 | Dalla chiave all'istanza: `SessionOrder.rng`, `session_rng`, `session_seed` (livello L3) | `sequenceDiagram` | 10 |
| D126 | Chi apre quale stream: le chiavi di `engage` e `fire_area` e i consumatori (frecce = stream) (livello L2) | `flowchart LR` | 10 |
| D127 | Mappa dei dati: il percorso in una sessione, dagli argomenti di `run_session` al `SessionOutcome` (frecce = dati) (livello L1) | `flowchart LR` | 10 |
| D128 | Mappa dei dati: le versioni del `CampaignLedger` e i dati in un passo di `run_campaign_session` (frecce = dati) (livello L2) | `flowchart LR` | 10 |
| D129 | Mappa dei dati: i campi del `SessionOutcome`, chi li produce e chi li legge (frecce = dati) (livello L2) | `flowchart LR` | 10 |

I diagrammi D30-D36 sono quelli della fase F4 (a `84a47670`). **Aggiornati a `a784a9e7`**: D1 (il carburante è dell'orchestratore,
non del risolutore), D2 (`postures`), D3 (`GroundedSchedule`), D4 (`ActivityCriteria`, `ActivityEnd`, `activity_ends`), D8 e D9
(episodi, ri-pianificazione, passo finale del carburante), D17 (`crew_recovered`, `AssetEndReason`, nuovi motivi di aborto),
D19 (esito di missione a regola unica: sostituisce la «prima forma»), D20 (attese e presenza), D29 (fasi F5, F6, G1-G5 fatte),
D34 (`GroundedSchedule`), D36 (postura nell'esito). Sono **nuovi** D37-D42. D5, D6, D7, D10-D16, D18, D21-D28 e D30-D33, D35
sono invariati.

**Aggiornati a `dcedc541`** (fase F7): D1 (nodi `Fire_Control` e `Area_Fire`, iniezione di `WeaponPolicy` e `TargetRules`), D8 e D9 (politica
d'armi, regole di bersaglio, fuochi su posizione intercalati agli episodi), D16 (`Target.asset_ids`, `MissionAsset.weapons`),
D29 (F7a e F7b fatte, F8 prossima). Sono **nuovi** D43-D50. Gli altri diagrammi sono invariati (D4 non mostra i tipi nuovi della F7,
raccolti in D47; D5 resta quello dell'ingaggio senza regole di bersaglio, il testo di §4.14 dice dove si inseriscono).

**Aggiornati a `fa5fbf1e`** (fase F8): D1 (blocco «Ciclo di campagna»: `Session_Campaign`, `Session_Validator`, `Readiness`, `Campaign_Types`, `Campaign_State`), D2 (`operation_outcomes`,
`final_positions`, `movement_ends`, `OperationOutcome`), D8 e D9 (esito per la campagna e warning E4 in `run_session`), D17 (`MissionStatus.IN_PROGRESS`, `OperationStatus`, `OperationOutcome`),
D19 (ramo `IN_PROGRESS`), D29 (F8a-F8c e F8-R fatte, F6-B3 chiuso, F8d non fatta). Sono **nuovi** D51-D55. Gli altri diagrammi sono invariati.

**Aggiornamento 2026-10-29** (difetto 26): nuovo D56 (S30-ABSENT); la didascalia di D53 precisa che la regola vale per gli asset passati alla sessione (i record degli asset non passati sono riportati prima, §6.26). Gli altri diagrammi sono invariati.

**Aggiornamento 2026-10-29** (atlante dei diagrammi, pilota): nuovo capitolo 10 (`11_Atlante_Diagrammi.md`) con i diagrammi **D57-D66**, la scala dei livelli L0-L4 e la tabella-atlante che assegna un livello anche a D1-D56. Nessun capitolo preesistente è stato modificato; D1-D56 sono invariati. Il livello di ciascun diagramma non è una colonna di questo elenco (richiederebbe di riscrivere le 56 righe esistenti): è nel capitolo 10 §10.2.

**Aggiornamento 2026-10-30** (atlante dei diagrammi, parti A-C): i file `11a_Atlante_Risolutore.md`, `11b_Atlante_Missione_Carburante.md` e `11c_Atlante_Porte_Campagna.md` aggiungono i diagrammi **D67-D87**, **D90-D109** e **D110-D129** (D88 e D89 non sono usati), con la tabella completa dei simboli di tutti i moduli del core. Verificati a `f009eb43`; nessun sorgente cambia. Il livello di ciascun diagramma è nella colonna «(livello Lx)» del titolo e nella tabella-atlante del capitolo 10 §10.2. In sequenze preesistenti (D50 nel capitolo 6, una del capitolo 10) e in due della parte A l'id di partecipante `AS` (parola chiave di Mermaid, possibile errore di resa) e' stato rinominato `AST`: nessun altro contenuto di D1-D66 cambia.
