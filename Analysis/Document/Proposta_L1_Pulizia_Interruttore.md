# Proposta: pulizia dell'interruttore L1 (`Engagement_Resolver.L1_IMMEDIATE_TARGET_RULE`) e della regola del 2026-09-28

**Stato: PIANO ESEGUIBILE.** Scritta il 2026-11-25 da `des-planner` sul checkout principale, branch
`analysis/dce-dcs-persistence`, codice al merge `170f4e0b` (working tree senza modifiche ai file di codice). E' il
**blocco 6** di `Proposta_Revisione_L1_Lanciatore_Bersaglio.md` (§2.5, §3 Q-L1-1, §4.6), che lo lasciava "da
ripianificare riga per riga sul codice di allora": questo documento lo sostituisce come contratto.

- **Precondizioni soddisfatte** (dalla sessione principale e dal registro git): `L1_IMMEDIATE_TARGET_RULE = True` dal
  2026-11-25 (decisione dell'utente, commit `3bd4058b`); fotografia nuova da 1219 esecuzioni **installata** dall'utente
  (`79e500e9`); suite `Ran 5005` `OK` e confronto con la fotografia nuova `IDENTICAL` (1219) al merge `170f4e0b`;
  **Q-L1-1 = A** confermata dall'utente: l'interruttore e' temporaneo e la regola del 2026-09-28 **non** e' un'alternativa
  valida (criterio dell'utente del 2026-11-08 sugli interruttori).
- **Formulazione ufficiale della regola** (resta l'unica): *"Se il lanciatore spara da dentro la zona dell'arma e
  l'intercettore puo' gia' colpirlo, e' un bersaglio: le sue salve non si intercettano."*
- **Esecutore**: `des-developer` (Claude), sul branch creato dalla sessione principale (nome proposto
  `ai/des-l1-pulizia`), a blocchi A, B, C (§4.2-§4.4), poi verifica completa (§4.5). Il manuale e' un blocco separato
  per `des-manual-writer` (§4.8). L'esecutore segue il piano cosi' com'e'; se il codice reale non corrisponde (righe,
  firme, esiti), **si ferma e riferisce**.
- **Nessun file di codice o di test e' modificato da questo documento.** Le sonde di §1.6 sono script di sola lettura
  nello scratchpad della sessione (fuori dal repo), eseguiti sul codice attuale.

**Convenzioni**: **[V]** = verificato leggendo il codice al commit `170f4e0b` (`file:riga`) o con `grep`; **[M]** = misurato
con una sonda di sola lettura (§1.6) o contato con il caricatore di `unittest` senza eseguire; **[I]** = deduzione non
eseguita; **[S]** = scelta di chi pianifica (non di modello, non un dato). Percorsi di codice relativi a
`Code/Dynamic_War_Manager/Source/`. Nessuna costante nuova, ne' stimata ne' di registro.

**Sigle**: L1 = regola dell'idoneita' del colpo per intercettore (`_may_intercept`); V_I = volume d'intercettazione di
`Mobile.air_defense_volume` (cilindro di tutte le armi antiaeree); "zona dell'arma" = cilindro di una sola arma
intercettrice (`Mobile.interceptor_envelopes`); "bersaglio immediato" = lanciatore rilevato dall'intercettore all'istante
del lancio e a portata di un'arma con scorta (`_immediate_target`); BI = filtro dei bersagli intercettabili
(`BI_AD_TARGET_RULE`, spento); R-INT = vincolo del tempo di reazione (`_in_time`); SD-n = scelte derivate della Proposta
di revisione; SP-n = scelte di chi pianifica in questo documento (§2.4).

---

## 0. Sintesi

| Cosa | Esito |
|---|---|
| Interruttore `L1_IMMEDIATE_TARGET_RULE` e il suo commento | eliminati; nessun interruttore nuovo |
| `self.l1_immediate_target`, `self.zone_cache` | eliminati da `_EngagementRun.__init__` |
| `_interception_zone`, `_may_intercept_volume` (regola del 2026-09-28) | eliminati |
| `_may_intercept` | applica direttamente la regola rivista, con la cache: il corpo di `_may_intercept_revised` entra in `_may_intercept` (stesse chiamate, stesso ordine, stesse letture); `_may_intercept_revised` eliminato |
| `_interceptor_envelopes`, `_immediate_target`, `envelope_cache`, `may_intercept_cache` | restano invariati (codice); ritocchi solo di docstring |
| `Mobile.air_defense_volume` | **resta**: serve al pianificatore di rotta (`Air_Route_Manager.build_threat_aa`), a `Military.air_defense_volume`, ai riepiloghi di `Block`, e ai suoi test (§1.4). Solo il risolutore smette di leggerlo |
| Test | 18 tolti, 4 nuovi (casi migrati), 8 riscritti senza interruttore (§4.6) |
| Suite | **`Ran 4991`** (da 5005: -14), `OK` |
| Confronto con la fotografia nuova (1219) | **`UNCHANGED (1219)`**, nessuna `CHANGED`/`NEW`/`MISSING`, `compared 1219 runs: IDENTICAL` |
| Fotografia | invariata: **nessuna fotografia nuova** da installare |

**Dimensione stimata** [S]: ~350 righe toccate, quasi tutte tolte (risolutore ~-75 e ~+15; `Test_Engagement_Resolver`
~-110 e ~+45; tre file di scenario ~-150 e ~+50; docstring ~40). Tre blocchi piccoli di codice/test (A, B, C), la verifica
finale, un blocco di manuale.

---

## 1. Problema e comportamento attuale

### 1.1 Stato di partenza nel risolutore [V, `Logic/Engagement_Resolver.py` a `170f4e0b`, 4730 righe]

- Costante `L1_IMMEDIATE_TARGET_RULE = True` (`:658`), commento `:645-657` ("interruttore dedicato e TEMPORANEO (si
  elimina dopo l'accensione e la fotografia nuova, se l'utente conferma Q-L1-1)").
- `_EngagementRun.__init__`: `self.zone_cache` (`:2066`, solo per la regola del 2026-09-28); commento `:2082-2083` e
  `self.l1_immediate_target = L1_IMMEDIATE_TARGET_RULE` (`:2084`); `self.envelope_cache` (`:2085`, regola rivista: resta);
  `self.may_intercept_cache` (`:2072`, resta).
- `_interception_zone(self, shadow)` (`:3710-3729`): legge `shadow.asset.air_defense_volume()` e lo memoizza in
  `zone_cache`; docstring "Usata solo con L1_IMMEDIATE_TARGET_RULE spento". Unico chiamante: `_may_intercept_volume`
  (`:3789`).
- `_interceptor_envelopes(self, shadow)` (`:3731-3748`): resta (zone per arma, `envelope_cache`).
- `_may_intercept(self, shadow, salvo)` (`:3765-3778`): cache per `(shadow.id, salvo.salvo_id)` e scelta
  `self._may_intercept_revised(...) if self.l1_immediate_target else self._may_intercept_volume(...)` (`:3775-3776`).
- `_may_intercept_volume` (`:3780-3799`): regola del 2026-09-28 (lancio fuori dal V_I). Chiamata solo da `_may_intercept`.
- `_may_intercept_revised` (`:3801-3819`): regola rivista. Chiamata solo da `_may_intercept`.
- `_immediate_target` (`:3846-3876`): resta.
- Unico chiamante di `_may_intercept` nel codice di produzione: `_on_resolve`, `:4042` (condizioni in OR: `free <= 0 or
  not self._admissible(...) or not self._may_intercept(...)` poi `_in_time`).
- Testi che descrivono l'interruttore o la regola del 2026-09-28: docstring del modulo `:47-57` (in particolare `:48` e
  `:54-57`); commento della costante `:645-657`; docstring `:3713`, `:3768-3769`, `:3781`; commento di `_on_resolve`
  `:4005-4014` (che oggi descrive ancora "FUORI dal proprio V_I" come regola e la rivista come variante).

### 1.2 Chi nomina l'interruttore o i simboli da eliminare [V, `grep -rn` su `Code/`, `tools/`, `Analysis/`]

| File | Righe | Uso |
|---|---|---|
| `Logic/Engagement_Resolver.py` | 48, 645-658, 2066, 2082-2084, 3710-3729, 3768-3819, 4007-4009 | costante, campi, metodi, commenti |
| `Asset/Mobile.py` | 1146 | solo docstring di `interceptor_envelopes` ("interruttore L1_IMMEDIATE_TARGET_RULE") |
| `Block/Military.py` | 752-753 | solo docstring di `salvo_interception_capacity` ("dentro il cui volume V_I e' partito il lancio": regola del 2026-09-28) |
| `Test/Test_Engagement_Resolver.py` | 1820, 1836, 1934, 1944, 1955-1956, 1985, 2003, 2006-2010, 2015-2022, 3332-3333, 5037-5038 | `patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', ...)`, test sul default, confronti fra stati |
| `Test/Test_Session_Scenarios_S19_Air_Defence.py` | 15, 25-26, 316-381 (`TestS19AdL1ImmediateTarget`, patch a `:348`) | docstring e classe |
| `Test/Test_Session_Scenarios_S35.py` | 24-26, 275-312 (`TestS35L1Revised`, patch a `:291`) | docstring e classe |
| `Test/Test_Session_Scenarios_S10_S18.py` | 1281-1320 (`TestS16L1Revised`, patch a `:1303`) | classe |
| `Analysis/Document/Rapporti/Sonde_L1_Revisione/probe_l1.py` | 3, 24, 28-57 | sonda storica del blocco 4: legge `_may_intercept_volume`, `_may_intercept_revised`, `_interception_zone` (§2.3) |
| `Analysis/Document/Rapporti/Sonde_L1_Revisione/suite_l1_on.py` | 1, 9 | sonda storica: assegna la costante in memoria (§2.3) |

Nessun uso nell'adapter DCS, in `Session_Simulator`, in `Scenario_Baseline` (ne' nel docstring) o in `tools/` [V].

**Test che fissano l'interruttore** (elenco completo, `grep "L1_IMMEDIATE_TARGET_RULE"` sui test) [V]:
1. `Test_Engagement_Resolver.TestLauncherInsideInterceptionZone._run` (`:1836`, False): 7 test della regola del 2026-09-28.
2. `Test_Engagement_Resolver.TestL1ImmediateTarget._run` (`:1934`, parametro `switch=True`) e
   `test_switch_is_on_by_default` (`:1943-1944`).
3. `Test_Engagement_Resolver.TestCoordinationDomainSalvoDefence.test_launch_inside_the_escort_zone_is_not_intercepted`
   (`:3330-3342`, False) — test (a2) del blocco 2.
4. `Test_Engagement_Resolver.TestAirDefenceTargetRule.test_switch_on_filter_is_applied_before_not_instead_of_l1`
   (`:5035-5040`, False) — test (a2) del blocco 2.
5. `Test_Session_Scenarios_S19_Air_Defence.TestS19AdL1ImmediateTarget._run` (`:348`, False/True).
6. `Test_Session_Scenarios_S35.TestS35L1Revised.setUpClass` (`:291`, False/True).
7. `Test_Session_Scenarios_S10_S18.TestS16L1Revised._run` (`:1303`, False/True).

Nessun altro. Le tre classi di scenario (5-7) **non** sono in `UNITS` di `Test/Scenario_Baseline.py` (le unita' di S16,
S19AD e S35-ADTGT sono `TestS16NavalInstallation`, `TestS19AirDefenceAllocation`, `TestS35AirDefenceTargets`, righe
`:327`, `:332`, `:432`) [V]: la fotografia non dipende da loro.

### 1.3 Perche' togliere il `patch` non basta

La Proposta di revisione (§4.6) diceva che "i test che fissavano lo stato perdono il `patch`". Sul codice reale non
basta: quasi tutti confrontano lo stato acceso con quello spento (es. `assertGreater(acceso, spento)`); tolto lo stato
spento, il confronto diventa `acceso` contro `acceso` e fallisce, oppure (test 1, 3, 4) fissano la regola del 2026-09-28
e con la sola regola rivista falliscono (gli stub `_ZonedInterceptor` non hanno `interceptor_envelopes` e non vedono il
lanciatore: nessun vincolo, si intercetta). Ogni test va quindi tolto, migrato o riscritto: §2.2 e §4.

### 1.4 `Mobile.air_defense_volume` resta [V, grep]

Dopo la pulizia il risolutore non lo chiama piu', ma ha altri chiamanti di produzione:
- `Logic/Air_Route_Manager.py:592-599` (`build_threat_aa`: cilindro della minaccia per il pianificatore di rotta,
  `ThreatAA`, esposizioni e `danger_level`; v. anche `Context/Context.py:783`);
- `Block/Military.py:530-550` (`Military.air_defense_volume`, lista dei volumi del blocco), letto da `Block/Block.py:704`
  (riepilogo) e `Context/Rinomina_Campaign_State.py:68`;
- test: `Test_Mobile.py` (~30 chiamate), `Test_Threat_AA_Factory.py`, `Test_Military.py`.
Si **conserva** senza modifiche. Anche lo stub di test `_ZonedInterceptor.air_defense_volume`
(`Test_Engagement_Resolver.py:1798-1808`) **resta**: con la regola rivista serve a provare che il risolutore **non**
ripiega sul V_I (SD-4: `test_without_envelopes_the_rule_does_not_apply`), ed e' la base di `_ArmedInterceptor`,
`_TrackingInterceptor` e `Ship`.

### 1.5 Corrispondenza dei 7 casi di `TestLauncherInsideInterceptionZone` [V, lettura; M, §1.6]

| Caso (2026-09-28) | Corrispondente nella regola rivista | Decisione |
|---|---|---|
| `test_launch_outside_the_zone_is_intercepted` (15 km -> 3, consumi `{'r2': 3}`) | `test_zones_are_per_weapon_not_an_envelope` caso `(15_000.5, 1000, 3)` e `test_launch_outside_every_zone_is_the_same_in_both_states` (che oggi confronta gli stati) | **migrato**: quest'ultimo diventa `test_launch_outside_every_zone_is_intercepted` con le due asserzioni del caso |
| `test_launch_inside_the_zone_is_never_intercepted` (8 km: `interceptable_rounds` 5, `capacity` 3 "tetto", 0 fermati, nessun evento, 5 eventi di danno) | `test_seen_launcher_in_range_inside_the_zone_is_not_intercepted` (solo `intercepted == 0` e nessun evento di r2) | **migrato**: le asserzioni su `interceptable_rounds`, `capacity` (tetto) e 5 eventi di danno **su r1** si aggiungono a quel test |
| `test_zone_boundary_counts_as_inside` (12 km -> 0) | `test_zones_are_per_weapon_not_an_envelope` caso `(15_000, 1000, 0)` (bordo della SAM = dentro) | coperto, nessuna migrazione |
| `test_launch_above_the_zone_ceiling_is_outside` | `test_zones_are_per_weapon_not_an_envelope` caso `(8000, 7000, 3)` | coperto |
| `test_zone_is_per_interceptor` (r2 12 km, r3 5 km: paga solo r3) | `test_rule_is_per_interceptor` distingue gli intercettori per **rilevamento** con zone uguali, non per **zona** | **migrato** come nuovo `test_zone_is_per_interceptor` (zone diverse, entrambi rilevano) |
| `test_without_zone_data_the_rule_does_not_apply` | `test_without_envelopes_the_rule_does_not_apply` | coperto |
| `test_non_interceptable_rounds_are_unaffected` | `TestL1ImmediateTarget.test_non_interceptable_rounds_are_unaffected` (identico) | coperto |

### 1.6 Sonde di sola lettura (2026-11-25, sul codice `170f4e0b`, interruttore `True`) [M]

Script nello scratchpad (fuori dal repo) che importano i moduli di test e chiamano i loro `_run` / `setUpClass` senza
modificare file. Risultati:

| Sonda | Esito |
|---|---|
| `TestL1ImmediateTarget._run(x=8000)` | risoluzione di `red`: `interceptable_rounds` 5, `capacity` 3, `intercepted` 0; nessun `InterceptionEvent`; eventi di danno 6, di cui **5 con `target_id == 'r1'`** e 1 su `b1` (il colpo di r2 sul lanciatore) |
| `_run(x=15000)` | `intercepted` 3, `interceptions_consumed() == {'r2': 3}` |
| r2 zona 12 km in (0,0,0), r3 zona 5 km in (0,300,0), `observers=('r2','r3')`, x = 8000 | `intercepted` 3, consumi `{'r3': 3}`; rilevamenti di r2 e r3 su b1 entrambi `True` |
| x = 8000 rilevato, regola contro `patch.object(ER._EngagementRun, '_may_intercept', return_value=True)` | fermati 0 contro 3; stesse `(observer, target, draw)`; `rng.calls` 8 contro 5 (**differenza 3**) |
| Scorta e1 (zona 12 km) di `m1`, dominio `_SHARED`, `random.Random(0)`, finestra e1 -> a1 e arma `_miss(rounds=1, max_range=20000, weapon='sam')` | x = 8000 rilevato: risoluzione di `m2` `(5, 3, 0)`, consumi `{}`; x = 15000 rilevato: `(5, 3, 3)`, `{'e1': 3}`; x = 8000 non rilevato: `(5, 3, 3)`, `{'e1': 3}`. Con la finestra e1 -> a1 compare anche una risoluzione della forza `red` (il colpo di e1), **prima** di quella di `m2` |
| Classe `TestL1ImmediateTarget` intera sul codice attuale | `Ran 15`, `OK` |
| `TestS19AirDefenceAllocation.setUpClass`, seme `S19-4` (indice 4 di `SEEDS`) | lanci di `Blue-CAS/cas1` a 162,66 e 164,16 s, rilevamento del Tor a 183,84 s (premessa vera); intercettazioni del Tor 2; l'unico `InterceptionEvent` del Tor contiene una salva di `cas1`; colpi sparati dal Tor 6 |
| `TestS35AirDefenceTargets.setUpClass`, `naval_maverick_off` | intercettazioni della Rezky per seme 6, 6, 4, 4; `Red-Navy` `held` in tutti e 4 (coincide con la fotografia installata) |
| `TestS16NavalInstallation.setUpClass` | corvette perse per seme: S16-0, -1, -2 entrambe; S16-3 nessuna (44 intercettazioni, `Red-Port` `held`) |
| Conteggio dei test (caricatore di `unittest`, senza eseguire) | suite 5005; `Test_Engagement_Resolver` 396 (`TestLauncherInsideInterceptionZone` 7, `TestL1ImmediateTarget` 15, `TestCoordinationDomainSalvoDefence` 8, `TestAirDefenceTargetRule` 12); `Test_Session_Scenarios_S19_Air_Defence` 16 (`TestS19AdL1ImmediateTarget` 4, `TestS19AirDefenceAllocation` 7); `Test_Session_Scenarios_S35` 18 (`TestS35L1Revised` 3, `TestS35AirDefenceTargets` 15); `Test_Session_Scenarios_S10_S18` 59 (`TestS16L1Revised` 2); `Test_Mobile` 220; `Test_Military` 134; `Test_Threat_AA_Factory` 66 |

Fotografia installata (lettura del JSON) [V]: `S19AD/S19-4/tor_forward_ifv_only` intercettazioni `{'Red-Line/ad0':
{'9M331-SAM': 2}}`; `S35-ADTGT/S35-ADTGT-k/naval_maverick_off` `{'Red-Navy/ff0': {'AK-630': 6|6|4|4}}`, `Red-Navy` `held`;
`S16/S16-3` `Red-Port` `held`.

---

## 2. Alternative e raccomandazioni

### 2.1 Codice del risolutore

Nessuna alternativa reale: Q-L1-1 = A decide l'eliminazione. L'unica scelta di forma e' come far entrare il corpo di
`_may_intercept_revised` in `_may_intercept` (che deve tenere la cache):
- **(i) inline con variabile `allowed`** (raccomandata, SP-1): un solo metodo, i `return` anticipati diventano rami `if`;
  stesse chiamate nello stesso ordine (`_interceptor_envelopes`, `_position_at` del lanciatore, `_position_at`
  dell'intercettore, poi `_immediate_target` solo se il lancio e' dentro una zona). Codice esatto in §4.4.
- (ii) tenere `_may_intercept_revised` come metodo privato senza interruttore: meno righe toccate, ma resta un nome che
  presuppone una regola "non rivista" che non esiste piu'. Scartata (il compito chiede il corpo dentro `_may_intercept`).

### 2.2 Test che confrontavano i due stati

| Gruppo | Opzioni | Raccomandazione [S] |
|---|---|---|
| `TestLauncherInsideInterceptionZone` (7) | (a) eliminarla migrando i casi senza corrispondente; (b) riscriverla sulla regola rivista | **(a)**: 4 casi gia' coperti, 3 migrati (§1.5); una classe in meno che descrive una regola che non c'e' |
| `TestL1ImmediateTarget` (15) | togliere il parametro `switch`, il test sul default, le meta' "spento"; riscrivere i due test che confrontavano gli stati | come a sinistra; `test_rule_draws_nothing_from_the_rng` confronta la regola con `_may_intercept` forzato a True (nessuna L1): prova "nessuna estrazione" senza lo stato spento (§1.6) |
| (a2) scorta di dominio (`TestCoordinationDomainSalvoDefence`) | (a) riscriverlo sulla regola rivista (scorta con zone, rilevamento e arma contro il lanciatore); (b) eliminarlo | **(a)**: e' l'unico test che prova L1 su un intercettore di **un'altra forza** del dominio; la sonda conferma gli attesi con lo stesso `random.Random(0)` della classe. Non e' il test facoltativo rifiutato dall'utente il 2026-11-25 (quello era un test nuovo): qui si conserva l'intento di un test esistente |
| (a2) BI prima di L1 (`TestAirDefenceTargetRule`) | (a) eliminarlo; (b) riscriverlo | **(a)**: e' esattamente `TestL1ImmediateTarget.test_bi_admitted_round_then_the_revised_l1_applies` (BI acceso, colpo ammesso, poi L1 rivista), aggiunto nel blocco 2 per questo |
| `TestS19AdL1ImmediateTarget` (4; due sessioni `S19-4` in piu') | (A) eliminarla e migrare in `TestS19AirDefenceAllocation` (che esegue gia' `S19-4` col Tor avanzato e ne cattura i risultati del risolutore) la premessa e la verifica "il Tor intercetta il lanciatore che non aveva visto"; (B) tenerla con una sola sessione e 3 test | **(A)**: nessuna sessione in piu', il caso resta come regressione della regola; "il Tor spara ancora ai lanciatori" e' gia' verificato per ogni seme (`test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones`, `:233`); "spento: nessuna intercettazione" non ha piu' senso |
| `TestS35L1Revised` (3; 16 sessioni in piu') | (A) eliminarla e migrare in `TestS35AirDefenceTargets` una verifica per seme su `naval_maverick_off`; (B) eliminarla senza migrazione | **(A)**: le esecuzioni ci sono gia'; la verifica "la Rezky ferma Maverick in ogni seme e non e' mai distrutta" esprime la zona dell'AK-630 (con la regola del 2026-09-28 la nave era distrutta in 4 semi su 4 e nel seme 2 non intercettava). Il terzo test ("con BI acceso l'interruttore L1 non cambia nulla") non ha piu' oggetto; "BI acceso: nessuna intercettazione" e' gia' il test 8 della classe |
| `TestS16L1Revised` (2; 2 sessioni in piu') | (A) eliminarla; (B) migrare in `TestS16NavalInstallation` "nel seme S16-3 nessuna corvetta persa" | **(A)**: la differenza fra le regole riguarda un solo seme (negli altri tre le corvette si perdono comunque, §1.6), quindi una verifica migrata sarebbe un esito di un singolo seme gia' fissato dalla fotografia (`S16/S16-3`); il meccanismo (fascia di quota dell'AK-630 sotto gli F/A-18C a 6000 m) e' coperto dai test unitari (`test_zones_are_per_weapon_not_an_envelope`, caso sopra il tetto; `test_zone_is_the_interceptor_weapon_not_the_air_defence_volume`) |

### 2.3 Sonde storiche del blocco 4 (`Rapporti/Sonde_L1_Revisione/`)

`probe_l1.py` sostituisce `_may_intercept` con una spia che chiama `_may_intercept_volume`, `_may_intercept_revised` e
`_interception_zone`: dopo la pulizia fallisce con `AttributeError` alla prima coppia valutata. `suite_l1_on.py`
assegna `ER.L1_IMMEDIATE_TARGET_RULE = True` in memoria: dopo la pulizia gira ancora ma l'assegnazione non ha effetto
(misura una suite qualunque).

| Opzione | Pro | Contro |
|---|---|---|
| **(a) lasciarle invariate come documento storico, con un `LEGGIMI.md` nella cartella** | il rapporto `L1_Esecuzioni_Cambiate.md` e l'Appendice A/B della Proposta di revisione le citano per percorso; stessa scelta della pulizia FP (`Sonde_Finestre_Passaggio/LEGGIMI.md`) | non eseguibili sul codice nuovo (dichiarato nel `LEGGIMI`) |
| (b) cancellarle (restano nella storia git) | nessun file morto | i riferimenti dei documenti puntano a file assenti |
| (c) adattarle al codice nuovo | — | il loro scopo era confrontare le due regole: senza la regola del 2026-09-28 non misurano nulla |

**Raccomandazione: (a)** [S]. Il `LEGGIMI.md` lo scrive la **sessione principale** (cartella dei rapporti, non
dell'esecutore), testo in §4.9. L'esecutore **non** tocca la cartella.

### 2.4 Scelte di chi pianifica (dichiarate, confermabili)

| Sigla | Scelta | Motivo |
|---|---|---|
| SP-1 | `_may_intercept` con la variabile `allowed` (§2.1 (i)) | un solo punto della regola, ordine delle chiamate invariato |
| SP-2 | Ordine dei blocchi: A (scenari), B (test unitari), C (risolutore e docstring) | finche' esiste la costante ogni blocco lascia la suite verde: A e B smettono di nominarla, C la toglie (con la costante tolta un `patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', ...)` solleverebbe `AttributeError`) |
| SP-3 | Test tolti senza sostituto: `test_switch_is_on_by_default` e i test "spento" | non si prova l'assenza di una costante (come il test 1 della pulizia FP) |
| SP-4 | Migrazioni di §2.2 (S19 e S35 nelle classi della fotografia, nessuna sessione in piu'); S16 senza migrazione | §2.2 |
| SP-5 | Docstring e commenti: la regola del 2026-09-28 si nomina solo come **storia** ("eliminata il ... con Proposta_L1_Pulizia_Interruttore.md"), mai come stato alternativo | il criterio dell'utente: lo stato precedente non e' un'alternativa |
| SP-6 | `_interceptor_envelopes`, `_immediate_target` e le cache restano con i nomi di oggi | nessun cambio di comportamento; rinominare toccherebbe il manuale senza beneficio |

---

## 3. Decisioni aperte per l'utente

**Nessuna decisione di design aperta**: la regola e la sua permanenza sono decise (a, c, d, e del 2026-11-24; scelta A
del 2026-11-25; Q-L1-1 = A). Restano confermabili le scelte tecniche SP-1..SP-6 (§2.4) e le raccomandazioni di §2.2
(migrazioni dei test) e §2.3 (sonde storiche); il piano di §4 le adotta. Se l'utente ne sceglie un'altra, chi pianifica
aggiorna §4 prima dell'esecuzione.

---

## 4. Piano di intervento

### 4.1 Precondizioni (la sessione principale le verifica; l'esecutore si ferma se mancano)

- **P-1**: branch di lavoro creato dalla sessione principale (`git branch --show-current`, nome proposto
  `ai/des-l1-pulizia`), partito da `170f4e0b` o da un commit successivo che non tocchi i file di §1.2.
- **P-2**: fotografia installata = quella di `79e500e9` (1219 esecuzioni, regola rivista accesa); confronto al punto di
  partenza `IDENTICAL` (1219) [V dalla sessione principale al merge `170f4e0b`].
- **P-3**: base della suite `Ran 5005` `OK` (l'unico fallimento noto ammesso e' il test di tempo
  `TestS17HierarchicalScaleSweep.test_every_size_runs_within_a_loose_bound`, rumore della macchina).
- **P-4**: le righe citate corrispondono al codice (ricerca per nome se spostate di poche righe; se una funzione, un test
  o un ramo non c'e', fermarsi e riferire).

`<python>` = interprete stampato nell'ESITO di `tools/ai/verifica.sh` (ProArt `.direnv/python-3.12/bin/python3`, VM
osboxes `python3`). Comandi dalla root del repo.

### 4.2 Blocco A — test di scenario (solo test; il risolutore non si tocca)

**File**: `Test/Test_Session_Scenarios_S19_Air_Defence.py`, `Test/Test_Session_Scenarios_S35.py`,
`Test/Test_Session_Scenarios_S10_S18.py`.

`Test_Session_Scenarios_S19_Air_Defence.py`:
1. **Togliere** la classe `TestS19AdL1ImmediateTarget` (`:316-381`, con le righe vuote che la precedono fino a lasciare
   due righe vuote prima di `if __name__ == '__main__':`). Test tolti (4): `test_premise_the_launcher_fires_before_the_tor_sees_it`
   (migrato, punto 2), `test_switch_off_the_tor_does_not_intercept` (regola eliminata), `test_switch_on_the_tor_intercepts_the_unseen_launcher`
   (migrato, punto 2), `test_switch_on_the_tor_still_fires_at_the_launchers` (gia' coperto per ogni seme da
   `test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones`, `:233`).
2. In `TestS19AirDefenceAllocation` (`:129`), subito dopo `AD = 'Red-Line/ad0'` (`:132`), aggiungere:
   ```python
    # Regola L1 (rivista il 2026-11-24): il seme in cui il lanciatore spara da dentro la zona del Tor prima di essere
    # rilevato (misure della Proposta di revisione: lanci a ~163 e ~164 s, rilevamento a ~184 s).
    L1_SEED = 'S19-4'
    L1_LAUNCHER = 'Blue-CAS/cas1'
   ```
   e, subito dopo `test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones` (che finisce a `:250`), prima di
   `class TestS19MissionRulesReplaceTheTestFilters`:
   ```python
    def _tor_forward_of(self, seed):
        """`(outcome, [EngagementResult, ...])` del Tor avanzato nel seme `seed` (le sessioni di `setUpClass`)."""
        index = self.SEEDS.index(seed)
        return self.tor_forward[index][2], self.tor_forward_results[index]

    def test_premise_in_s19_4_the_launcher_fires_before_the_tor_sees_it(self):
        """Premessa del test seguente: nel seme S19-4 `cas1` lancia AGM-65D prima che il Tor lo rilevi."""
        _, results = self._tor_forward_of(self.L1_SEED)
        launches = [s.t_launch for r in results for s in r.salvos
                    if s.shooter_id == self.L1_LAUNCHER and s.spec.weapon == MAVERICK]
        seen = [d.time for r in results for d in r.detections
                if d.observer_id == self.AD and d.target_id == self.L1_LAUNCHER and d.detected]
        self.assertTrue(launches)
        self.assertTrue(not seen or min(seen) > min(launches))

    def test_in_s19_4_the_tor_intercepts_the_launcher_it_had_not_seen(self):
        """Regola L1 (rivista il 2026-11-24): `cas1` lancia da dentro i 12 km del Tor ma non e' un suo bersaglio
        immediato (non ancora rilevato al lancio): il Tor ne intercetta i colpi. Con la regola del 2026-09-28, eliminata
        (Proposta_L1_Pulizia_Interruttore.md), non li intercettava. Caso migrato da TestS19AdL1ImmediateTarget."""
        outcome, results = self._tor_forward_of(self.L1_SEED)
        self.assertGreater(_interceptions(outcome, self.AD), 0)

        for result in results:
            shooter_of = {s.salvo_id: s.shooter_id for s in result.salvos}

            for event in result.interception_events:
                if event.asset_id == self.AD:
                    with self.subTest(time=event.time):
                        self.assertTrue(any(shooter_of.get(salvo_id) == self.L1_LAUNCHER
                                            for salvo_id in event.salvo_ids))
   ```
   `setUpClass` (`:134-168`) **non cambia** (e' l'unita' `S19AD` della fotografia: nessuna sessione in piu').
3. Docstring del modulo (`:10-27`): sostituire il punto **L** e il paragrafo "Misura del 2026-09-28" con questo contenuto
   (testo esatto libero entro il contenuto):
   - punto **L**: "(L1 implementata il 2026-09-28, passo 4; rivista il 2026-11-24 e accesa il 2026-11-25; interruttore e
     regola precedente eliminati con Proposta_L1_Pulizia_Interruttore.md): se il lanciatore spara da dentro la zona
     dell'arma e l'intercettore puo' gia' colpirlo, e' un bersaglio: le sue salve non si intercettano. Un lanciatore
     dentro la zona ma non ancora rilevato non e' un bersaglio: i suoi colpi si intercettano. Il Tor arretrato ... (resto
     invariato: fuori dai 12 km intercetta; col Tor avanzato i lanci partono a ~9,5 km, il Tor spara ai lanciatori e
     intercetta solo i colpi di quelli che non aveva ancora rilevato al lancio)." **Togliere** la frase "La regola del
     2026-09-28 (interruttore L1_IMMEDIATE_TARGET_RULE spento) escludeva ogni lancio da dentro il V_I." e il rimando
     "(v. TestS19AdL1ImmediateTarget)".
   - paragrafo "Misura del 2026-09-28 (passo 3)": invariato fino a "...spende gli 8 missili su di lui."; poi "Con la regola
     rivista l'unico seme in cui cambia l'esito e' `S19-4` (`cas1` lancia prima di essere rilevato: il Tor intercetta 2
     colpi), verificato qui (`TestS19AirDefenceAllocation`, test sul seme S19-4). Il caso a geometria controllata
     (intercettore con scorta in avanzo e lancio da dentro la zona) e' nei test unitari del risolutore:
     Test_Engagement_Resolver.TestL1ImmediateTarget." **Togliere** "e TestLauncherInsideInterceptionZone (regola del
     2026-09-28)".
4. `test_rear_tor_intercepts_standoff_launches` (`:212-213`): docstring invariata (vera).

`Test_Session_Scenarios_S35.py`:
5. **Togliere** la classe `TestS35L1Revised` (`:275-312`), lasciando due righe vuote prima di `if __name__ == '__main__':`.
   Test tolti (3): `test_switch_on_the_ship_intercepts_more_mavericks` e `test_switch_on_the_ship_is_destroyed_less_often`
   (confronti con la regola eliminata; il loro contenuto per la regola rivista migra al punto 6),
   `test_bi_on_makes_the_l1_switch_irrelevant` (senza oggetto; "BI acceso: nessuna intercettazione" e' il test 8,
   `test_naval_maverick_on_the_ship_never_intercepts`, `:240`).
6. In `TestS35AirDefenceTargets`, in coda alla classe (dopo `test_runs_are_deterministic`, che finisce a `:272`):
   ```python
    def test_naval_maverick_off_the_ship_intercepts_and_holds_in_every_seed(self):
        """13. Regola L1 (rivista il 2026-11-24): la zona della Rezky e' quella dell'AK-630 (4 km, unica arma
        'Anti_Missile'), non il V_I della SA-N-4 (12 km); i Maverick partono a 7,1-14,7 km (misura della Proposta di
        revisione), fuori zona: con BI spento la nave ne ferma in ogni seed e non e' mai distrutta (con la regola del
        2026-09-28, eliminata, era distrutta in tutti e 4: misura, Rapporti/L1_Esecuzioni_Cambiate.md). Caso migrato
        da TestS35L1Revised (Proposta_L1_Pulizia_Interruttore.md)."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('naval_maverick_off')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, SHIP), 0)
                self.assertNotEqual(F.force_outcome(outcome, 'Red-Navy').outcome, 'destroyed')
   ```
   `setUpClass` invariato (unita' `S35-ADTGT` della fotografia).
7. Docstring del modulo (`:22-26`): "La Rezky e non l'Arleigh Burke (decisione P-1 del 2026-11-08): con il V_I di 240 km
   del Burke la regola L1 del 2026-09-28 (eliminata con Proposta_L1_Pulizia_Interruttore.md) vietava ogni intercettazione
   dei lanci da aereo. Con la regola L1 rivista (dal 2026-11-25) la zona della Rezky e' quella dell'AK-630 (4 km) e la
   nave ferma i Maverick in ogni seed (test 13); il Burke resterebbe escluso solo per i lanciatori che vede e puo'
   colpire." Il seguito ("Il sensore `sea` di 20 km ...") invariato. Commento di `SHIP_MODEL` (`:61`): "# intercettore
   AK-630 (task 'Anti_Missile', zona L1 di 4 km); V_I 12 km (SA-N-4)". Le altre righe con "V_I" (`:14`, `:17`, `:18`)
   descrivono la geometria e restano.

`Test_Session_Scenarios_S10_S18.py`:
8. **Togliere** la classe `TestS16L1Revised` (`:1281-1320`), lasciando due righe vuote prima del commento
   `# ── S17 — SWEEP DI SCALA GERARCHICA` (`:1323`). Test tolti (2): `test_switch_on_the_corvettes_intercept_more`,
   `test_switch_on_fewer_corvettes_are_lost` (confronti con la regola eliminata; nessuna migrazione, §2.2). Gli import
   `patch` e `ER` restano usati nel file (`:82`, `:240`, spia di S16) [V].

**Vincoli**: nessun file di `Logic/` o `Asset/` toccato; nessun `setUpClass` di una classe della fotografia cambia;
`Scenario_Baseline.py` non si tocca. Dopo il blocco nessun file di scenario nomina `L1_IMMEDIATE_TARGET_RULE`.

**Verifica dell'esecutore**: `<python> -m py_compile` dei tre file; poi, uno per volta:

    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence   # Ran 14, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S35               # Ran 16, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18           # Ran 57, OK

(`Test_Session_Scenarios_S10_S18` contiene il test di tempo S17: un suo fallimento isolato va riportato, non corretto.)

**Verifica parziale** (l'esecutore se ha il permesso, altrimenti la sessione principale):

    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json \
        --only '^(S16|S19AD|S35-ADTGT)/' --quiet --summary

Atteso: `compared 60 runs: IDENTICAL` [V: 60 chiavi della fotografia corrispondono all'espressione].

### 4.3 Blocco B — test unitari del risolutore (solo `Test/Test_Engagement_Resolver.py`)

1. **Togliere** la classe `TestLauncherInsideInterceptionZone` (`:1811-1878`), lasciando due righe vuote fra
   `_ZonedInterceptor` (`:1798-1808`) e `_ArmedInterceptor` (`:1880`). Test tolti (7), con il motivo: i 4 casi coperti e i
   3 migrati di §1.5.
2. **Stub** (solo docstring):
   - `_ZonedInterceptor` (`:1799`): "Intercettore con posizione e volume d'intercettazione V_I (come
     Mobile.air_defense_volume). Il risolutore non legge piu' il V_I (regola del 2026-09-28 eliminata,
     Proposta_L1_Pulizia_Interruttore.md): senza `interceptor_envelopes` nessun vincolo L1; il V_I resta per provare che
     non c'e' ripiego (SD-4)."
   - `_ArmedInterceptor` (`:1881`): "Intercettore con zone delle armi intercettrici (Mobile.interceptor_envelopes); il V_I
     ereditato (air_defense_volume) non e' letto dal risolutore."
   - `_TrackingInterceptor` (`:2053`): "Intercettore senza zone per arma (nessun vincolo L1) con raggio di rilevamento
     aereo (Mobile.detection_range)."
   - docstring di `TestInterceptionReaction` (`:2070`): "intercettore senza V_I" -> "intercettore senza zone per arma
     (nessun vincolo L1)".
3. **`TestL1ImmediateTarget`** (`:1891-2049`):
   - docstring (`:1892-1902`): "Geometria come TestLauncherInsideInterceptionZone:" -> "Geometria:"; togliere l'ultima
     frase "L'interruttore e' fissato a ogni run."; aggiungere in coda "Dal blocco di pulizia
     (Proposta_L1_Pulizia_Interruttore.md) e' l'unica regola L1: nessun interruttore."
   - `_run` (`:1907-1936`): togliere il parametro `switch=True` dalla firma; `with patch(_ER_LOGGER),
     patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', switch):` -> `with patch(_ER_LOGGER):`. Nient'altro cambia.
   - **tolto** `test_switch_is_on_by_default` (`:1943-1944`): SP-3.
   - `test_seen_launcher_in_range_inside_the_zone_is_not_intercepted` (`:1946-1949`): corpo nuovo (asserzioni migrate dal
     caso "dentro la zona" della classe tolta; attesi misurati, §1.6):
     ```python
        result = self._run(x=8_000.0)
        resolution = self._salvo_resolution(result)
        self.assertEqual(resolution.interceptable_rounds, 5)
        self.assertEqual(resolution.capacity, 3)          # tetto, non garantita
        self.assertEqual(resolution.intercepted, 0)
        self.assertEqual([e for e in result.interception_events if e.asset_id == 'r2'], [])
        self.assertEqual(len([e for e in result.damage_events if e.target_id == 'r1']), 5)
     ```
   - `test_unseen_launcher_inside_the_zone_is_intercepted` (`:1951-1956`): togliere il commento `:1955` e la riga `:1956`
     (stato spento).
   - `test_zone_is_the_interceptor_weapon_not_the_air_defence_volume` (`:1980-1985`): docstring "... Lancio a 8 km,
     rilevato e a portata della SAM: fuori dalla zona del CIWS -> intercettato (con la regola del 2026-09-28, eliminata,
     sarebbe stato dentro il V_I)."; togliere la riga `:1985` (stato spento).
   - `test_without_envelopes_the_rule_does_not_apply` (`:1999-2003`): docstring "SD-4: senza `interceptor_envelopes`
     nessun vincolo, e nessun ripiego sul V_I (`air_defense_volume`, che lo stub ha)."; togliere la riga `:2003`.
   - `test_launch_outside_every_zone_is_the_same_in_both_states` (`:2005-2010`) -> **`test_launch_outside_every_zone_is_intercepted`**:
     ```python
    def test_launch_outside_every_zone_is_intercepted(self):
        """Lancio a 15 km, fuori dai 12 km dell'unica arma: intercettato anche se il lanciatore e' rilevato e a portata
        (caso migrato da TestLauncherInsideInterceptionZone.test_launch_outside_the_zone_is_intercepted)."""
        result = self._run(x=15_000.0)
        self.assertEqual(self._salvo_resolution(result).intercepted, 3)
        self.assertEqual(result.interceptions_consumed(), {'r2': 3})
     ```
   - `test_rule_draws_nothing_from_the_rng` (`:2012-2022`), stesso nome, corpo nuovo:
     ```python
    def test_rule_draws_nothing_from_the_rng(self):
        """La regola non estrae: lanciatore rilevato e a portata, dentro la zona (escluso), contro la stessa esecuzione
        con `_may_intercept` forzato a True (nessuna L1). Stesse estrazioni di rilevamento; la differenza e' solo il
        danno: con la regola 3 colpi in piu' arrivano al modello di danno (tre estrazioni)."""
        rng_rule, rng_free = _ScriptedRng([0.0] * 40), _ScriptedRng([0.0] * 40)
        rule = self._run(x=8_000.0, rng=rng_rule)

        with patch.object(ER._EngagementRun, '_may_intercept', return_value=True):
            free = self._run(x=8_000.0, rng=rng_free)

        self.assertEqual(self._salvo_resolution(rule).intercepted, 0)
        self.assertEqual(self._salvo_resolution(free).intercepted, 3)
        self.assertEqual([(d.observer_id, d.target_id, d.draw) for d in rule.detections],
                         [(d.observer_id, d.target_id, d.draw) for d in free.detections])
        self.assertEqual(rng_rule.calls - rng_free.calls, 3)
     ```
     (misura: 8 contro 5 chiamate). Se la differenza non e' 3, **fermarsi** e riferire (indicherebbe un'estrazione nella regola).
   - **nuovo** `test_zone_is_per_interceptor`, subito dopo `test_rule_is_per_interceptor` (`:2024-2030`):
     ```python
    def test_zone_is_per_interceptor(self):
        """Q1: la zona e' quella del singolo intercettore. Entrambi rilevano b1 e lo hanno a portata; il lancio (8 km) e'
        dentro i 12 km di r2 (escluso) ma fuori dai 5 km di r3, che intercetta (e paga) da solo. Caso migrato da
        TestLauncherInsideInterceptionZone.test_zone_is_per_interceptor."""
        r2 = _ArmedInterceptor('r2', (0.0, 0.0, 0.0), self.ZONES)
        r3 = _ArmedInterceptor('r3', (0.0, 300.0, 0.0), (('sam', 5_000.0, 0.0, 6_000.0),))
        result = self._run(x=8_000.0, interceptors=[r2, r3], observers=('r2', 'r3'))
        self.assertEqual(self._salvo_resolution(result).intercepted, 3)
        self.assertEqual(result.interceptions_consumed(), {'r3': 3})
     ```
   - invariati: `test_launcher_seen_after_the_launch_is_intercepted`, `test_seen_launcher_out_of_weapon_range_is_intercepted`,
     `test_seen_launcher_without_stock_is_intercepted`, `test_roe_none_means_not_an_immediate_target`,
     `test_zones_are_per_weapon_not_an_envelope`, `test_rule_is_per_interceptor`, `test_non_interceptable_rounds_are_unaffected`,
     `test_bi_admitted_round_then_the_revised_l1_applies`.
4. **`TestCoordinationDomainSalvoDefence`** (`:3281`):
   - `_run` (`:3290-3307`): firma `def _run(coordination_of=None, escort=None, channels=3, spec=None, legs=None, x=None,
     escort_sees=False, escort_fire=None):`; la fire control diventa
     ```python
        def fire(shooter, target):
            if shooter.id == 'a1':
                return spec

            return escort_fire if shooter.id == 'e1' and target.id == 'a1' else None
     ```
     (con `escort_fire` None identica a oggi); dopo la riga di `window` (`:3301-3302`):
     ```python
        windows = [window]

        if escort_sees:
            # L1: la scorta rileva a1 dall'inizio (bersaglio immediato se ha anche un'arma a portata).
            windows.append(ContactWindow('e1', 'a1', t_start=0.0, t_end=2.9, t_cpa=2.9, distance_cpa=x,
                                         range_a=50_000.0, range_b=None))
     ```
     e nella chiamata `ER.resolve_engagement(m1, m2, [window], ...)` -> `ER.resolve_engagement(m1, m2, windows, ...)`; resto
     invariato (stesso `random.Random(0)`). Commento `:3300`: "come in TestLauncherInsideInterceptionZone" -> "come in
     TestL1ImmediateTarget". Gli altri 7 test della classe non passano i parametri nuovi: comportamento identico.
   - `test_launch_inside_the_escort_zone_is_not_intercepted` (`:3330-3342`), stesso nome, corpo nuovo (attesi misurati, §1.6):
     ```python
    def test_launch_inside_the_escort_zone_is_not_intercepted(self):
        """Regola L1 anche per la scorta di un'altra forza del dominio: a1 lancia da 8 km, dentro i 12 km della zona
        dell'arma della scorta, che lo rileva e lo ha a portata -> non fermato; da 15 km (fuori zona) o non rilevato ->
        fermato."""
        fire_e1 = _miss(rounds=1, max_range=20_000.0, weapon='sam')

        for x, sees, expected in ((8_000.0, True, 0), (15_000.0, True, 3), (8_000.0, False, 3)):
            escort = _ArmedInterceptor('e1', (0.0, 0.0, 0.0), (('sam', 12_000.0, 0.0, 6_000.0),))
            legs = {'a1': [Leg(0.0, 100.0, (x, 0.0, 0.0), (x, 0.0, 0.0))],
                    't1': [Leg(0.0, 100.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))],
                    'e1': [Leg(0.0, 100.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))]}

            with self.subTest(x=x, sees=sees):
                result = self._run(_SHARED, escort=escort, legs=legs, x=x, escort_sees=sees, escort_fire=fire_e1)
                self.assertEqual([r.intercepted for r in result.resolutions if r.force_id == 'm2'], [expected])
     ```
     (la risoluzione si sceglie per forza: con la finestra e1 -> a1 ce n'e' anche una della forza `red`, prima di `m2`).
5. **`TestAirDefenceTargetRule`** (`:4961`):
   - **tolto** `test_switch_on_filter_is_applied_before_not_instead_of_l1` (`:5035-5040`): duplicato di
     `TestL1ImmediateTarget.test_bi_admitted_round_then_the_revised_l1_applies` (BI acceso, colpo ammesso, poi la L1).
   - docstring della classe (`:4967-4968`): "Geometria: bersaglio r1 nell'origine, tiratore b1 fermo a (x, 0, 0), una
     salva di 5 colpi intercettabili a t = 2 s; intercettori nell'origine, 3 canali ciascuno, senza zone per arma
     (`_ZonedInterceptor`/`Ship`: la regola L1 non li vincola; l'ordine BI -> L1 e' in TestL1ImmediateTarget)."
6. Controllo finale del blocco: `grep -n "L1_IMMEDIATE_TARGET_RULE\|TestLauncherInsideInterceptionZone" Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py`
   -> **nessuna riga**.

**Vincoli**: nessun file di `Logic/` toccato; nessuno stub nuovo; classi che non ereditano da `TestCase` invariate;
logger mockato con `patch(_ER_LOGGER)` come oggi.

**Verifica dell'esecutore**: `py_compile`; `<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver`
-> **`Ran 388`, `OK`** (396 - 7 - 1 - 1 + 1). Nessun confronto (solo test unitari, nessuna classe della fotografia).

### 4.4 Blocco C — risolutore e docstring (`Logic/Engagement_Resolver.py`, `Asset/Mobile.py`, `Block/Military.py`)

`Logic/Engagement_Resolver.py`:
1. **Costante**: togliere le righe `:645-659` (commento `:645-657`, `L1_IMMEDIATE_TARGET_RULE = True` a `:658` e la riga
   vuota `:659`), cosi' fra `VA_ENGAGEMENT_ALTITUDE_BAND = False` (`:643`) e il commento di `AD_DOMAINS` (`:660`) resta
   una sola riga vuota.
2. **`_EngagementRun.__init__`**: togliere `self.zone_cache: ...` (`:2066`); sostituire `:2082-2085` con
   ```python
        # Regola L1 (rivista il 2026-11-24): zone delle armi intercettrici per intercettore ((raggio, quota min, quota max)
        # relativi; None = non modellate), memoizzate per id.
        self.envelope_cache: Dict[str, Optional[Tuple[Tuple[float, float, float], ...]]] = {}
   ```
   (togliere `self.l1_immediate_target = L1_IMMEDIATE_TARGET_RULE`). Nessun altro campo cambia.
3. **Togliere** `_interception_zone` (`:3710-3729`) con la riga vuota che segue.
4. **`_interceptor_envelopes`** (`:3731-3748`): codice invariato; docstring "(L1 rivista)" -> "(regola L1)"; il resto
   ("nessun ripiego su `air_defense_volume`") resta.
5. **`_may_intercept`**: sostituire l'intero tratto `:3765-3819` (`_may_intercept`, `_may_intercept_volume`,
   `_may_intercept_revised`) con:
   ```python
    def _may_intercept(self, shadow: "_Shadow", salvo: Salvo) -> bool:
        """Regola L1 (rivista il 2026-11-24, Proposta_Revisione_L1_Lanciatore_Bersaglio.md): se il lanciatore spara da
        dentro la zona dell'arma e l'intercettore puo' gia' colpirlo, e' un bersaglio: le sue salve non si intercettano.

        False solo se il punto di lancio (posizioni all'istante del lancio) e' nel cilindro di almeno un'arma
        intercettrice (bordo = dentro) E il lanciatore e' un bersaglio immediato (`_immediate_target`). Senza zone per
        arma o senza posizioni: True (dato mancante = non modellato; nessun ripiego sul V_I di `air_defense_volume`).
        Memoizzato per (intercettore, salva): ogni salva e' risolta una volta sola. Nessuna estrazione. La regola del
        2026-09-28 (lancio dentro il V_I = mai intercettato) e il suo interruttore sono stati eliminati
        (Proposta_L1_Pulizia_Interruttore.md).
        """
        key = (shadow.id, salvo.salvo_id)

        if key not in self.may_intercept_cache:
            allowed = True
            zones = self._interceptor_envelopes(shadow)
            launch = self._position_at(self.shadows[salvo.shooter_id], salvo.t_launch)
            here = self._position_at(shadow, salvo.t_launch)

            if zones is not None and launch is not None and here is not None:
                horizontal = ((launch[0] - here[0]) ** 2 + (launch[1] - here[1]) ** 2) ** 0.5
                height = launch[2] - here[2]

                if any(horizontal <= radius and bottom <= height <= top for radius, bottom, top in zones):
                    allowed = not self._immediate_target(shadow, salvo)

            self.may_intercept_cache[key] = allowed

        return self.may_intercept_cache[key]
   ```
   **Equivalenza con oggi** (interruttore True) [V, lettura di `:3774-3776` e `:3806-3819`]: stesse letture
   (`_interceptor_envelopes`, poi `_position_at` del lanciatore, poi dell'intercettore), nello stesso ordine e con gli
   stessi argomenti; `_immediate_target` chiamata solo se il lancio e' dentro una zona, come oggi (`:3816-3819`); stesso
   valore in ogni ramo (dato mancante -> True; fuori da ogni zona -> True; dentro -> `not _immediate_target`); stessa
   chiave e stessa cache. Nessun metodo chiamato in piu' o in meno.
6. **`_immediate_target`** (`:3846-3876`): codice invariato; prima riga del docstring "L1 rivista, condizione (2): ..." ->
   "Regola L1, condizione (2): ...".
7. **Docstring del modulo** (`:47-57`): da "Regola L1 (rivista il 2026-11-24," a "Nessuna estrazione." diventa
   (contenuto vincolante, forma libera):
   "Regola L1 (rivista il 2026-11-24, Proposta_Revisione_L1_Lanciatore_Bersaglio.md, accesa il 2026-11-25; l'interruttore
   temporaneo e la regola del 2026-09-28 sono stati eliminati con Proposta_L1_Pulizia_Interruttore.md): se il lanciatore
   spara da dentro la zona dell'arma e l'intercettore puo' gia' colpirlo, e' un bersaglio: le sue salve non si
   intercettano. "Dentro la zona" = ... (invariato) ... In ogni altro caso il colpo e' intercettabile (salvo R-INT,
   canali, scorta, BI). Nessuna estrazione." Si toglie la frase "Con l'interruttore spento vale la regola del 2026-09-28:
   colpo intercettabile solo se il punto di lancio e' fuori dal volume d'intercettazione V_I (`Mobile.air_defense_volume`),
   e il lanciatore da dentro e' un bersaglio." (`:54-56`).
8. **Commento di `_on_resolve`** (`:4005-4014`; solo commento, nessuna riga di codice): sostituire le righe `:4005-4014`
   con
   ```python
        # Allocazione PER SALVA (regola L1, 2026-09-28, Proposta_Regole_Allocazione_SAM.md §7; rivista il 2026-11-24,
        # Proposta_Revisione_L1_Lanciatore_Bersaglio.md): un intercettore NON ferma i colpi di una salva se il lanciatore
        # spara da dentro la zona di una sua arma intercettrice e lui puo' gia' colpirlo (rilevato al lancio e a portata
        # di un'arma con scorta), v. `_may_intercept`: un lanciatore cosi' e' un bersaglio, non si inseguono i suoi
        # colpi. Salve nell'ordine (impatto, salva), intercettori nell'ordine della regola F, ogni
        # intercettore fino a min(canali, scorta) per evento. Senza vincoli geometrici (nessun
        # dato di zona o di posizione) il risultato coincide con l'allocazione sul totale usata
        # fino al 2026-09-28: stessi consumi per intercettore, stesse salve fermate.
   ```
   Le due righe seguenti ("La capacita' registrata ...", `:4015-4016`) restano. Nessun'altra riga di `_on_resolve` si tocca.
9. Righe che **restano** come sono (vere anche dopo): `:305` ("geometria L1 (`_may_intercept`)"), `:870-875` (`capacity`
   tetto "dal 2026-09-28, regola L1"), `:210` ("APPROSSIMAZIONE L1": e' un'altra cosa, approssimazione del primo ordine).

`Asset/Mobile.py`:
10. Docstring di `interceptor_envelopes` (`:1146-1147`): "Usata dalla regola L1 rivista (Engagement_Resolver, interruttore
    L1_IMMEDIATE_TARGET_RULE): un lancio e' ..." -> "Usata dalla regola L1 del risolutore (Engagement_Resolver._may_intercept):
    un lancio e' ...". Nessun'altra riga. `air_defense_volume` (`:1483`) **non** si tocca (§1.4).

`Block/Military.py`:
11. Docstring di `salvo_interception_capacity` (`:752-753`): "Dal 2026-09-28 e' un TETTO: la regola L1 del risolutore
    (Engagement_Resolver._may_intercept, rivista il 2026-11-24) esclude, salva per salva, gli intercettori per cui il
    lanciatore, rilevato e a portata, ha sparato da dentro la zona di una loro arma intercettrice." Nessun'altra riga.

12. Controllo finale del blocco (dalla root del repo):

        grep -rn "L1_IMMEDIATE_TARGET_RULE\|l1_immediate_target\|_may_intercept_volume\|_may_intercept_revised\|_interception_zone\|zone_cache" Code/

    -> **nessuna riga**. (`envelope_cache` e `may_intercept_cache` restano e non corrispondono all'espressione.)

**Vincoli**:
- **RNG**: nessuna estrazione nuova, tolta o spostata. Nessuno dei metodi toccati chiama `_draw`, `rng`, `pass_rng` o
  `breakpoint_rng` [V]; `_draw`, `_detect_direction`, `_detect_passes` non si toccano; di `_on_resolve` si toccano solo le
  righe di commento del punto 8 (la riga `:4042` resta identica).
- **Nessuna costante nuova**, nessun interruttore nuovo. **Core indifferente al simulatore**: nessun import nuovo.
- `Session_Simulator`, `Scenario_Baseline`, `Air_Route_Manager`, l'adapter DCS **non** si toccano.

**Verifica dell'esecutore**: `py_compile` dei tre file; poi, uno per volta:

    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver          # Ran 388, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Mobile                       # Ran 220, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Military                     # Ran 134, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Threat_AA_Factory            # Ran 66, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence   # Ran 14, OK
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S35       # Ran 16, OK

**Verifica parziale** (unita' con intercettori, le stesse della sonda della revisione):

    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json \
        --only '^(S2|S6|S11|S16|S19AD|S35-ADTGT)/' --quiet --summary

Atteso: `compared 94 runs: IDENTICAL` [V: 94 chiavi corrispondono]. Una differenza qui e' un errore nel punto 5 (ordine o
rami): fermarsi.

### 4.5 Verifica finale (esecutore con `tools/ai/verifica.sh`, mai in parallelo)

    bash tools/ai/verifica.sh suite start        # poi: bash tools/ai/verifica.sh suite wait  (ripetere fino a ESITO)
    bash tools/ai/verifica.sh confronto start    # SOLO dopo l'ESITO della suite; poi: confronto wait

Attesi:
- Suite: **`Ran 4991`**, `OK` (con gli stessi `skipped` di prima, se presenti). Il solo test di tempo S17, se fallisce,
  va riportato com'e' (rumore noto), non corretto.
- Confronto: **`UNCHANGED (1219)`**, nessuna riga `CHANGED`/`NEW`, **`compared 1219 runs: IDENTICAL`**, exit code 0.
  `grep -E '^(CHANGED|NEW)' .ai-run/confronto.log` -> nessuna riga.

Rapporto dell'esecutore: `Analysis/Document/Rapporti/Rapporto_L1_Pulizia_des-developer.md` secondo
`Rapporti/TEMPLATE.md`, con i numeri letti dagli ESITI, l'elenco dei test tolti/migrati/riscritti (§4.6) e le scelte
minori (§4.7).

### 4.6 Conteggio dei test (da `Ran 5005`) [M, caricatore di `unittest`]

| Modulo | Prima | Dopo | Differenza | Dettaglio |
|---|---|---|---|---|
| `Test_Engagement_Resolver` | 396 | 388 | -8 | -7 `TestLauncherInsideInterceptionZone`; -1 `test_switch_is_on_by_default`; -1 `test_switch_on_filter_is_applied_before_not_instead_of_l1`; +1 `test_zone_is_per_interceptor` |
| `Test_Session_Scenarios_S19_Air_Defence` | 16 | 14 | -2 | -4 `TestS19AdL1ImmediateTarget`; +2 in `TestS19AirDefenceAllocation` |
| `Test_Session_Scenarios_S35` | 18 | 16 | -2 | -3 `TestS35L1Revised`; +1 in `TestS35AirDefenceTargets` |
| `Test_Session_Scenarios_S10_S18` | 59 | 57 | -2 | -2 `TestS16L1Revised` |
| **Suite** | **5005** | **4991** | **-14** | 18 tolti, 4 nuovi |

**Test tolti (18), con il motivo**:

| Test | Motivo |
|---|---|
| `TestLauncherInsideInterceptionZone.test_launch_outside_the_zone_is_intercepted` | regola eliminata; caso migrato in `test_launch_outside_every_zone_is_intercepted` |
| `...test_launch_inside_the_zone_is_never_intercepted` | regola eliminata; asserzioni migrate in `test_seen_launcher_in_range_inside_the_zone_is_not_intercepted` |
| `...test_zone_boundary_counts_as_inside` | coperto da `test_zones_are_per_weapon_not_an_envelope` (bordo della SAM) |
| `...test_launch_above_the_zone_ceiling_is_outside` | coperto da `test_zones_are_per_weapon_not_an_envelope` (sopra il tetto) |
| `...test_zone_is_per_interceptor` | regola eliminata; caso migrato nel nuovo `TestL1ImmediateTarget.test_zone_is_per_interceptor` |
| `...test_without_zone_data_the_rule_does_not_apply` | coperto da `test_without_envelopes_the_rule_does_not_apply` |
| `...test_non_interceptable_rounds_are_unaffected` | identico in `TestL1ImmediateTarget` |
| `TestL1ImmediateTarget.test_switch_is_on_by_default` | non si prova l'assenza di una costante (SP-3) |
| `TestAirDefenceTargetRule.test_switch_on_filter_is_applied_before_not_instead_of_l1` | duplicato di `test_bi_admitted_round_then_the_revised_l1_applies` |
| `TestS19AdL1ImmediateTarget.test_premise_the_launcher_fires_before_the_tor_sees_it` | migrato in `TestS19AirDefenceAllocation` |
| `TestS19AdL1ImmediateTarget.test_switch_off_the_tor_does_not_intercept` | descrive la regola eliminata |
| `TestS19AdL1ImmediateTarget.test_switch_on_the_tor_intercepts_the_unseen_launcher` | migrato in `TestS19AirDefenceAllocation` |
| `TestS19AdL1ImmediateTarget.test_switch_on_the_tor_still_fires_at_the_launchers` | coperto per ogni seme da `test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones` |
| `TestS35L1Revised.test_switch_on_the_ship_intercepts_more_mavericks` | confronto con la regola eliminata; contenuto migrato nel test 13 di `TestS35AirDefenceTargets` |
| `TestS35L1Revised.test_switch_on_the_ship_is_destroyed_less_often` | idem |
| `TestS35L1Revised.test_bi_on_makes_the_l1_switch_irrelevant` | senza oggetto; "BI acceso: nessuna intercettazione" e' il test 8 |
| `TestS16L1Revised.test_switch_on_the_corvettes_intercept_more` | confronto con la regola eliminata; nessuna migrazione (§2.2) |
| `TestS16L1Revised.test_switch_on_fewer_corvettes_are_lost` | idem |

**Test nuovi (4)**: `TestL1ImmediateTarget.test_zone_is_per_interceptor`;
`TestS19AirDefenceAllocation.test_premise_in_s19_4_the_launcher_fires_before_the_tor_sees_it` e
`...test_in_s19_4_the_tor_intercepts_the_launcher_it_had_not_seen`;
`TestS35AirDefenceTargets.test_naval_maverick_off_the_ship_intercepts_and_holds_in_every_seed`.

**Test riscritti (8, stesso numero)**: in `TestL1ImmediateTarget` `test_seen_launcher_in_range_inside_the_zone_is_not_intercepted`,
`test_unseen_launcher_inside_the_zone_is_intercepted`, `test_zone_is_the_interceptor_weapon_not_the_air_defence_volume`,
`test_without_envelopes_the_rule_does_not_apply`, `test_launch_outside_every_zone_is_the_same_in_both_states` (rinominato
`test_launch_outside_every_zone_is_intercepted`), `test_rule_draws_nothing_from_the_rng`; piu' `_run` della classe;
`TestCoordinationDomainSalvoDefence.test_launch_inside_the_escort_zone_is_not_intercepted` (e il suo `_run`).

### 4.7 Scelte minori lasciate all'esecutore (da elencare nel rapporto)

Testo esatto di commenti e docstring entro il contenuto indicato; nomi delle variabili locali; posizione esatta delle
costanti `L1_SEED`/`L1_LAUNCHER` dentro `TestS19AirDefenceAllocation` purche' a livello di classe; righe vuote fra le
classi secondo lo stile del file (due).

### 4.8 Blocco D — manuale (`des-manual-writer`, separato, dopo il merge dei blocchi A-C)

Scrivere lo **stato finale**: una sola regola L1 (la rivista), nessun interruttore; la regola del 2026-09-28 resta solo
come storia (perche' e' stata sostituita, quando, con quale effetto: le 6 esecuzioni cambiate), mai come stato
riproducibile. Fotografia nuova da 1219 **installata** (`79e500e9`), confronto `IDENTICAL`. Righe di codice da
riallineare dopo il blocco C (il risolutore perde ~75 righe: tutte le citazioni successive a `:645` si spostano).
Sezioni:

1. `Manuale_Motore_DES/05_Strato2_Risolutore_Ingaggio.md` (cap. 4):
   - tabella iniziale / riquadro `:66` (interruttore "ora acceso") -> regola senza interruttore;
   - `:327` (elenco delle regole: "Con `L1_IMMEDIATE_TARGET_RULE` spento (regola del 2026-09-28) ...") -> togliere il ramo spento;
   - `:525` (campi di `_EngagementRun`: `zone_cache`, `l1_immediate_target`) -> restano `envelope_cache`, `may_intercept_cache`;
   - §4.24, sottosezione "Regola L1" (`:1796-1906`): titolo (citazione di `_may_intercept` con le righe nuove);
     paragrafo **"Interruttore."** (`:1806-1812`) -> "Nessun interruttore dal <data> (Proposta_L1_Pulizia_Interruttore.md);
     `_may_intercept` applica la regola con la cache"; paragrafo **"Regola del 2026-09-28 (interruttore spento ...)"**
     (`:1864-1874`) -> sottosezione **storica** breve ("Regola del 2026-09-28, eliminata": che cosa faceva, perche' e'
     stata sostituita, rimando alla Proposta di revisione §1.2); citazioni di `TestLauncherInsideInterceptionZone`,
     `TestS16L1Revised`, `TestS19AdL1ImmediateTarget`, `TestS35L1Revised` (`:1874`, `:1905`) -> i test di §4.6 (unitari
     `TestL1ImmediateTarget`; scenari `TestS19AirDefenceAllocation` seme S19-4 e test 13 di `TestS35AirDefenceTargets`);
     "**La fotografia nuova non e' ancora installata**" (`:1897-1899`) -> installata, `IDENTICAL`;
   - `:2050` e §"Verifica: lo scenario S19AD" (`:2052-2068`): citazioni di `TestS35L1Revised`,
     `TestLauncherInsideInterceptionZone`, `TestS19AdL1ImmediateTarget` -> i test nuovi;
   - **Diagramma D24** (didascalia `:2074` e corpo): togliere "con `L1_IMMEDIATE_TARGET_RULE` ..." e ogni ramo "spento".
2. `Manuale_Motore_DES/07_Orchestratore_Session_Simulator.md` (cap. 6): riquadro `:3`; §6.21 "Interruttori e valori di
   default" (`:1442`), paragrafo `:1485-1486` "cinque interruttori" -> **quattro** (D-5, BI, VA, PB) e "L1 eliminato"
   accanto a "FP eliminato"; riga della tabella `L1_IMMEDIATE_TARGET_RULE` (`:1494`) **tolta**, e un capoverso come quello
   di `FP_PER_PASS_DETECTION` ("non esiste piu': era temporaneo, acceso il 2026-11-25, eliminato il <data>").
3. `Manuale_Motore_DES/08_Supporto_Trasversale.md` (cap. 7): `:287-289` (ramo "con `L1_IMMEDIATE_TARGET_RULE` spento,
   gli intercettori dentro il cui V_I ...") e `:355` ("Lo consuma solo il risolutore, con `L1_IMMEDIATE_TARGET_RULE`
   acceso") -> senza interruttore; dove si descrive `Mobile.air_defense_volume`, precisare che il risolutore non lo legge
   piu' e che resta per pianificatore di rotta, blocchi e riepiloghi (§1.4).
4. `Manuale_Motore_DES/09_Validazione.md` (cap. 8): riquadro `:43`; `:318` (S19AD); `:485` (elenco delle classi di
   `Test_Engagement_Resolver`: togliere `TestLauncherInsideInterceptionZone`); `:1050` (S35: "15 test (12 asserzioni e 3
   premesse)" -> **16 test (13 asserzioni e 3 premesse)** in `TestS35AirDefenceTargets`; nessuna classe `TestS35L1Revised`);
   conteggi di suite se citati (4991).
5. `Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md` (cap. 9): riquadro `:3`; §9.1 "Bersagli intercettabili"
   (`:368`); §9.1 "Regola L1 rivista" (`:387` e seguenti, in particolare `:396-401` "Interruttore temporaneo, ora `True`"
   e "il blocco 6 non e' fatto", `:419-423`, `:448`): interruttore **eliminato**, blocco 6 fatto, fotografia installata;
   tabella di stato §9.4 (`:962`); aggiornamento `:1072`; `:1194`; voce di divergenza 42 (`:1393`) se cita l'interruttore;
   nuova voce di stato "pulizia L1" con commit e numeri (4991, `IDENTICAL` 1219).
6. `Manuale_Motore_DES/11a_Atlante_Risolutore.md`: riquadro `:630`; nodo R9 del grafo (`:898`: togliere
   `_may_intercept_volume`, `_may_intercept_revised`, `_interception_zone`); lettura `:924`; `:1324` (passo `_may_intercept`
   con "interruttore `True`"); tabella dei simboli (`:1512-1519`): togliere le righe di `_interception_zone`,
   `_may_intercept_volume`, `_may_intercept_revised`; descrizione di `_may_intercept` (`:1515`) = la regola con la cache;
   righe aggiornate di `_interceptor_envelopes` e `_immediate_target`.
7. `Manuale_Motore_DES/Manuale_Motore_DES.md` (indice): riquadro `:8`; voce D24 (`:392`) se serve.
8. `Manuale_Motore_DES/Guida_Concettuale_DES.md`: riquadro `:16-19` (fotografia nuova installata, interruttore
   eliminato); §11 `:2446-2448` ("il suo interruttore e' **temporaneo** e spegnendolo si torna alla regola del
   2026-09-28 ... la fotografia nuova non e' ancora installata") -> regola senza interruttore, fotografia installata.

Il manual-writer verifica ogni riga citata sul codice dopo il blocco C (le righe qui sono quelle del manuale al
`170f4e0b`).

### 4.9 Documenti da aggiornare (sessione principale, non l'esecutore)

- **`Rapporti/Sonde_L1_Revisione/LEGGIMI.md`** (nuovo, §2.3 (a)): "Sonde del blocco 4 della revisione L1 (2026-11-25),
  eseguite sul codice `a1559ad9`. Dopo la pulizia (`Proposta_L1_Pulizia_Interruttore.md`, <data>, <commit>)
  `probe_l1.py` non e' piu' eseguibile (chiama `_may_intercept_volume`, `_may_intercept_revised`, `_interception_zone`,
  eliminati: `AttributeError`); `suite_l1_on.py` gira ma l'assegnazione di `L1_IMMEDIATE_TARGET_RULE` non ha effetto.
  Documenti storici; per rieseguirle serve il codice di un commit fino a `170f4e0b` nel checkout principale (mai in un
  git worktree)."
- **`Rapporti/L1_Esecuzioni_Cambiate.md`**: una riga in testa "Interruttore eliminato il <data> (Proposta_L1_Pulizia_Interruttore.md);
  gli script di questa sonda sono storici (v. `Sonde_L1_Revisione/LEGGIMI.md`)".
- **`Proposta_Revisione_L1_Lanciatore_Bersaglio.md`** §4.6 e tabella di §4: nota "ripianificato ed eseguito con
  Proposta_L1_Pulizia_Interruttore.md" (file del pianificatore: su richiesta, da `des-planner`).
- **`F4_Differenze_Scenari.md`**: oggi non ha una sezione "L1 rivista" (la §4.9 della Proposta di revisione la
  prevedeva) [V, grep]: aggiungerla in coda con tre punti: accensione (6 esecuzioni cambiate, rimando a
  `Rapporti/L1_Esecuzioni_Cambiate.md`), fotografia nuova `79e500e9`, pulizia (0 esecuzioni cambiate, suite 4991).
- **`Piano_Implementazione_Missione.md`** §5 (righe fuori dalla numerazione F, come BI a `:311` e FP a `:312`): riga
  "L1 rivista" con stato "FATTA, ACCESA e SENZA INTERRUTTORE", commit dei blocchi, numeri.
- **`Stato_Progetto_DES.md`**: riga della L1 nella tabella delle decisioni aperte -> chiusa.
- **Memoria** (solo la sessione principale): interruttore L1 eliminato, numeri della verifica; prossimo passo per gli
  interruttori: restano D-5, BI, VA, PB (analisi mirata degli interruttori).

---

## 5. Esito atteso del confronto con la fotografia nuova (1219 esecuzioni, `79e500e9`)

| Gruppo | Esecuzioni | Esito | Perche' |
|---|---|---|---|
| Tutte le unita' | 1219 | **identiche** | la fotografia e' stata catturata con l'interruttore `True`, cioe' con `_may_intercept_revised`; dopo la pulizia `_may_intercept` esegue lo stesso corpo con le stesse letture nello stesso ordine (§4.4 punto 5); la regola del 2026-09-28 non era mai eseguita (`_interception_zone` e `zone_cache` erano letti solo da `_may_intercept_volume`); nessuna estrazione cambiata; i `setUpClass` delle unita' della fotografia (S16, S19AD, S35-ADTGT) non cambiano |
| Cambiate | 0 | — | nessun cambio di comportamento |
| Nuove / mancanti | 0 / 0 | — | nessuna unita', variante o chiave nuova in `UNITS`; le tre classi tolte non erano unita' della fotografia |

Nessuna fotografia nuova da installare.

---

## 6. Rischi e limiti

- **Equivalenza del punto 5 (§4.4)**: e' il solo cambiamento di codice eseguito; un errore di ramo (es. `allowed = False`
  senza `_immediate_target`, o `_immediate_target` chiamato anche fuori zona) cambierebbe esiti solo dove la regola
  esclude, cioe' **in nessuna esecuzione della fotografia** (la regola rivista non esclude nessuna delle 414 coppie
  valutate, `Rapporti/L1_Esecuzioni_Cambiate.md` §3). Il confronto quindi **non** basta a provarlo: lo provano i test
  unitari di `TestL1ImmediateTarget` (rami: rilevato dentro, non rilevato, dopo il lancio, fuori portata, senza scorta,
  ROE, zona per arma, bordo, sopra il tetto, dato mancante, nessuna estrazione) e il test della scorta di dominio. Se
  uno di questi cambia esito al blocco C, fermarsi.
- **Ramo "bersaglio immediato dentro la zona" ancora non esercitato dalla fotografia** (limite R-3 della Proposta di
  revisione, invariato): resta provato solo dai test unitari. Uno scenario dedicato (S37, Q-L1-4 (B)) resta proponibile
  separatamente.
- **Regola del 2026-09-28 non piu' riproducibile** se non dalla storia git (conseguenza accettata con Q-L1-1 = A); le
  sonde del blocco 4 diventano documenti storici (§2.3).
- **Test migrati con esiti di sessione** (S19-4: intercettazioni del Tor > 0; S35: nave mai distrutta in
  `naval_maverick_off`): sono esiti qualitativi, ma una ricalibrazione futura non legata a L1 (Pd, dottrina, registri)
  potrebbe renderli falsi; in quel caso vanno riletti, non adattati a mano. Stessa natura dei test che sostituiscono.
- **Test di tempo S17** su macchine cariche: puo' fallire per rumore, indipendente da questo lavoro.
- Punti di dottrina e upgrade **invariati** (Proposta di revisione §5, §5.1): PD-1 (missile fire-and-forget gia' in volo),
  PD-2 (lanciatore abbattuto prima della risoluzione), UF-1 (ROE a tempo nella condizione (2)), UF-2 (guida del missile).
  Se un giorno si realizzano, vanno dietro un interruttore **nuovo** spento (la pulizia non ne lascia nessuno da riusare).
