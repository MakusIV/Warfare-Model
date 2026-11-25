# Rapporto L1_Pulizia — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/des-l1-pulizia` · **piano eseguito**: `Analysis/Document/Proposta_L1_Pulizia_Interruttore.md` (blocchi A, B, C e verifica finale; il blocco D, manuale, e i documenti di §4.9 non sono miei)
- **Data**: 2026-11-25

## 1. Esito in una riga
Completato, nessuno scostamento di design: suite `Ran 4991` OK, confronto con la fotografia `IDENTICAL` (1219), come atteso dal piano.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S19_Air_Defence.py` | tolta `TestS19AdL1ImmediateTarget` (4 test); in `TestS19AirDefenceAllocation` aggiunte `L1_SEED`, `L1_LAUNCHER`, `_tor_forward_of` e 2 test sul seme S19-4; docstring del modulo (punto L e "Misura del 2026-09-28") |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S35.py` | tolta `TestS35L1Revised` (3 test); nuovo test 13 in `TestS35AirDefenceTargets`; docstring del modulo e commento di `SHIP_MODEL` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S10_S18.py` | tolta `TestS16L1Revised` (2 test), nessuna migrazione |
| `Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py` | tolta `TestLauncherInsideInterceptionZone` (7); `TestL1ImmediateTarget` senza parametro `switch` e senza patch (tolto `test_switch_is_on_by_default`, 6 test riscritti/rinominati, nuovo `test_zone_is_per_interceptor`); `TestCoordinationDomainSalvoDefence._run` con `escort_sees`/`escort_fire` e test della scorta riscritto; tolto `test_switch_on_filter_is_applied_before_not_instead_of_l1`; docstring degli stub e delle classi |
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | eliminati `L1_IMMEDIATE_TARGET_RULE` (e commento), `self.l1_immediate_target`, `self.zone_cache`, `_interception_zone`, `_may_intercept_volume`, `_may_intercept_revised`; il corpo della regola entra in `_may_intercept` (variabile `allowed`, SP-1); docstring del modulo, di `_interceptor_envelopes`, `_immediate_target` e commento di `_on_resolve` |
| `Code/Dynamic_War_Manager/Source/Asset/Mobile.py` | solo docstring di `interceptor_envelopes` |
| `Code/Dynamic_War_Manager/Source/Block/Military.py` | solo docstring di `salvo_interception_capacity` |
| `Analysis/Document/Rapporti/Rapporto_L1_Pulizia_des-developer.md` | questo rapporto |

Commit: `13046d5f` (A), `b0e3f813` (B), `436a0ef0` (C), piu' il commit del rapporto (verifica finale).

## 3. Scostamenti dal piano
Nessuno di design. Una sola incoerenza interna al piano, senza effetto sul comportamento: il controllo finale del blocco B (§4.3 punto 6) dice che `grep "TestLauncherInsideInterceptionZone"` su `Test_Engagement_Resolver.py` non deve dare righe, ma i docstring dei due test migrati, che il piano detta testualmente ("Caso migrato da TestLauncherInsideInterceptionZone...", §4.3 punti 3), nominano la classe tolta. Ho tenuto i docstring come da piano: restano 2 righe (`:1941`, `:1973`) di sola storia. Il grep di `L1_IMMEDIATE_TARGET_RULE` sullo stesso file e' vuoto; il controllo del blocco C (§4.4 punto 12) su tutto `Code/` e' vuoto.

## 4. Scelte minori prese
- Reflow degli a capo dei docstring/commenti riscritti (docstring del modulo del risolutore, di S35, di S19) entro il contenuto indicato dal piano.
- Docstring del test `test_zone_is_the_interceptor_weapon_not_the_air_defence_volume` e di `test_without_envelopes_the_rule_does_not_apply` ripartiti su due righe.
- `L1_SEED`/`L1_LAUNCHER` messe subito dopo `AD` a livello di classe; `_tor_forward_of` subito dopo `test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones`.
- Due righe vuote fra le classi come nello stile dei file.
- Nel commento di `_on_resolve` ho tenuto il testo del piano alla lettera (nessuna riga di codice toccata).
- Non ho aggiunto test: i 4 nuovi sono quelli del piano.

## 5. Costanti stimate
Nessuna (nessuna costante nuova; il piano non ne introduce).

## 6. Verifiche eseguite (numeri letti dai log/ESITO)
Interprete `.direnv/python-3.12/bin/python3`.
- Blocco A, singoli file: S19_Air_Defence `Ran 14` OK; S35 `Ran 16` OK; S10_S18 `Ran 57` `OK (skipped=2)`. Confronto parziale `--only '^(S16|S19AD|S35-ADTGT)/'`: `compared 60 runs: IDENTICAL`.
- Blocco B: `Test_Engagement_Resolver` `Ran 388` OK. La differenza di estrazioni di `test_rule_draws_nothing_from_the_rng` e' 3, come misurato dal piano.
- Blocco C: `Test_Engagement_Resolver` `Ran 388` OK; `Test_Mobile` `Ran 220` OK; `Test_Military` `Ran 134` OK; `Test_Threat_AA_Factory` `Ran 66` OK; S19 `Ran 14` OK; S35 `Ran 16` OK. Confronto parziale `--only '^(S2|S6|S11|S16|S19AD|S35-ADTGT)/'`: `compared 94 runs: IDENTICAL`. Nessun test unitario di `TestL1ImmediateTarget` e nessun test della scorta ha cambiato esito al blocco C.
- Verifica finale, suite completa (`tools/ai/verifica.sh suite`): `ESITO suite: exit code 0` · `Ran 4991 tests in 627.347s` · `OK (skipped=7)`. Atteso dal piano: 4991 OK. (Il numero di `skipped` della base 5005 non l'ho rilevato, quindi non lo confronto.)
- Verifica finale, confronto (`tools/ai/verifica.sh confronto`): `ESITO confronto: exit code 0` · `UNCHANGED (1219)` · `compared 1219 runs: IDENTICAL (523.8 s)`; `grep -cE '^(CHANGED|NEW|MISSING)' .ai-run/confronto.log` = 0. Atteso dal piano: `IDENTICAL` 1219, nessuna CHANGED/NEW/MISSING. Corrisponde. Fotografia non installata ne' modificata.
- Conteggi per modulo uguali a §4.6 (ER 388, S19 14, S35 16, S10_S18 57; totale 4991 = 5005 - 14).

## 7. Limiti noti e dubbi per la sessione principale
- Come dichiarato dal piano (§6), il confronto non prova l'equivalenza di `_may_intercept`: la provano i test unitari di `TestL1ImmediateTarget` e il test della scorta, tutti verdi. Ho verificato per lettura che l'ordine delle chiamate coincide con quello di prima (`_interceptor_envelopes`, `_position_at` del lanciatore, `_position_at` dell'intercettore, `_immediate_target` solo con lancio dentro una zona).
- Il ramo "bersaglio immediato dentro la zona" resta esercitato solo dai test unitari (limite R-3 della Proposta di revisione).
- Documenti di §4.9 e blocco D (manuale) non toccati, come da compito; le sonde storiche in `Rapporti/Sonde_L1_Revisione/` non toccate (ora non eseguibili: `probe_l1.py` darebbe `AttributeError`).
- `.ai-run/` e' ignorata da git.

## 8. Stato git
Vedi l'output finale riportato nella risposta alla sessione principale (untracked preesistenti: tre cartelle sotto `Analysis/WIKI_LLM_SIMULATION/RAW/`; `git stash list` vuota).
