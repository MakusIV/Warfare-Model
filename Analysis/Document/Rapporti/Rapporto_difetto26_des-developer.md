# Rapporto difetto26 — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5 high (Pro). In due fasi (A: correzione e test; B: docstring P1-P10). Non committa: i commit sono della sessione principale, che ha compilato questo rapporto dai due rapporti degli agenti e dalle proprie verifiche.
- **Branch**: `ai/cc-difetto26` · **piano eseguito**: `Analysis/Document/Proposta_Difetto26_Readiness_Ledger.md`
- **Data**: 2026-10-29

## 1. Esito in una riga
Completato, nessuno scostamento di design dal piano. Scelte: A, nessun interruttore, 3b, registrare S30-ABSENT, stesso branch con commit separato.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Logic/Readiness.py` | `readiness_after_session` parte dai record degli asset non passati (A); `apply_campaign_processes` conserva il record concluso di un asset assente (3b, `logger.debug` al posto del warning); docstring; P1 |
| `Logic/Session_Campaign.py` | solo docstring di `run_campaign_session` |
| `Test/Test_Readiness.py` | test 1, 2, 3, 4 (riscritto), 5; P5 |
| `Test/Test_Session_Campaign.py` | test 6 |
| `Test/Test_Session_Scenarios_S30.py` | `A1..A3`, `_mbt1_movement_mission`, classe `TestS30AbsentForce` (test 7-10); P2, P3, P4 |
| `Test/Scenario_Baseline.py` | voce `S30-ABSENT` in coda a `UNITS` |
| `Test/Test_Context.py`, `Context/Campaign_State.py` | solo docstring (P6-P10) |

## 3. Scostamenti dal piano
Nessuno di design. Nei test 4 e 10 il codice vecchio dà ERROR (`KeyError`) invece di FAIL, perche' l'accesso diretto `readiness[...]` a un record mancante solleva `KeyError`: stessa causa del piano.

## 4. Scelte minori prese
Docstring dei test in una riga; separatore `# ── Test ──` come in `TestS30CampaignSequence`; riga dell'unita' S30-ABSENT in forma di frase nel docstring del modulo S30; nessuna sezione S30 aggiunta al docstring di `Scenario_Baseline` (non c'e' neppure per S30-CAMPAIGN); in P5 fuse le due parentesi consecutive; P7: la riga `"ledger"` e' a livello di `mission_id`, fratello di `"regions"`; P10 su due righe; in `apply_campaign_processes` aggiunta al docstring la frase sullo stato vecchio dell'asset assente (§5 del piano).

## 5. Costanti stimate
Nessuna nuova. I test calcolano gli istanti dal registro e da `Context` (turnaround a terra 21 600 s STIMA DI PROGETTO, riparazione 86 400 s a confidenza bassa, gia' dichiarati in `Context.py`).

## 6. Verifiche eseguite
- Prima della correzione (codice vecchio, verificato anche dalla sessione principale): falliscono i 9 test attesi (Test_Readiness 36 test: 3 FAIL + 1 ERROR; Test_Session_Campaign 10: 1 FAIL; Test_Session_Scenarios_S30 14: 3 FAIL + 1 ERROR); il test 2 (guardia) passa.
- Dopo: Test_Readiness 36 OK, Test_Session_Campaign 10 OK, Test_Session_Scenarios_S30 14 OK, Test_Campaign_Types 41 OK, Test_Session_Validator 16 OK; dopo la fase B anche Test_Context 203 OK e Test_Campaign_State 85 OK.
- Suite (sessione principale, `tools/ai/verifica.sh`, `.direnv/python-3.12/bin/python3`): `Ran 4710 tests in 549.779s` · `OK (skipped=7)`. Atteso dal piano con 3b: 4710 OK (7 skipped).
- Confronto: `compared 989 runs`, `UNCHANGED (986)`, 0 cambiate, 3 nuove (`S30-ABSENT/S30-ABSENT-1..3`, verificato confrontando le chiavi del capture con la fotografia). Atteso: 986 identiche + 3 nuove. S30-CAMPAIGN identico.

## 7. Limiti noti e dubbi per la sessione principale
- Nessun chiamante di produzione: la correzione si vede solo negli scenari.
- Un id che non ricompare piu' lascia il suo record nel registro per sempre; lo stato (salute, carburante) di un asset assente resta vecchio finche' non torna (§5 del piano).
- `.ai-run/confronto.log` non elenca le righe `CHANGED`/`NEW` (solo il riepilogo): le 3 nuove sono state verificate dal capture.

## 8. Stato git
Vedi il log del branch `ai/cc-difetto26`: `d7594a13` (scelte), `be8559d7` (correzione e test), `f009eb43` (docstring P1-P10).
