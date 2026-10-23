# Rapporto F8c blocco 3 — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-f8c3` · **piano eseguito**: `Analysis/Document/Proposta_F8_Sessione_Campagna.md` (§4.4, §4.8)
- **Data**: 2026-10-23

## 1. Esito in una riga
Completato: scenario S30-CAMPAIGN (4 sessioni) con i test del §4.4, riga `S30-CAMPAIGN` in
`Scenario_Baseline.UNITS`, e i soli ritocchi di docstring di §4.8. Tutti i test mirati verdi.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/.../Test/Test_Session_Scenarios_S30.py` | NUOVO: `TestS30CampaignSequence` con la sequenza a 4 sessioni via `Session_Campaign.run_campaign_session` e gli 8 test del §4.4. |
| `Code/.../Test/Scenario_Baseline.py` | Aggiunta in coda a `UNITS` la voce `('S30-CAMPAIGN', 'Test_Session_Scenarios_S30', 'TestS30CampaignSequence', None, _single_or_index)`. |
| `Code/.../Command/Session_Types.py` | Docstring "Cosa NON c'e'" (§4.8): le finestre di campagna esistono (F8, `SessionRules`/`Session_Validator`); l'applicazione dell'esito e' del conduttore di campagna. |
| `Code/.../Logic/Mission_Adapter.py` | Docstring (§4.8): `check_mission_bingo` e `check_mission_fuel` ora chiamati anche dal validatore di sessione (`Logic/Session_Validator`, F8), non solo dal futuro C2. |
| `Code/.../Test/Test_Session_Scenarios_S10_S18.py` | Docstring S11 (§4.8): il limite della posizione resta per chi chiama `run_session`; la persistenza e' del conduttore di campagna (S30). |
| `Code/.../Test/Test_Session_Validation.py` | Commento mini-campagna (§4.8): idem, riferito al conduttore di campagna (S30). |

## 3. Scostamenti dal piano
Nessuno di sostanza. Unica precisazione (non una deviazione di design): nel punto 2 della sequenza il
piano scrive `final_positions['mbt0'] = (10 km, -20 km)` per la sessione senza missioni. Verificato sul
codice gia' presente (F8b): `final_positions` usa `all_legs`, che include anche i tratti statici degli
asset fermi (`Session_Simulator.py:3144-3151`, `:2392-2404`), quindi l'asserzione del piano e' esatta:
senza `apply_final_positions` della sessione 1, mbt0 sarebbe ripartito da (0, -20 km). Il test verifica
entrambe le cose (`final_positions` e `asset.position` ai checkpoint).

## 4. Scelte minori prese
- Forze e geometria (dettaglio lasciato all'esecutore dal piano): `Blue-Base` = Military `AIR_UNIT` con
  `Structure` 'Farp'/'Oil_Tank' in (0, 0) come riferimento d'atterraggio; `Blue-Wing` = 2 F-16C 'Strike'
  parcheggiati in (0,0,0) e (0,150,0) con la stessa formazione di S22-AIR 'parked' (`right_m=-150` sul
  gregario); `Blue-Mech` = 2 M1A2-Abrams in (0,-20 km) e (0,-19,8 km); `Red-Depot` = bloccco Red con
  `Structure` a (300 km, 0). Missione aerea costruita a mano (`_loop_mission`) perche' `F.missions_for`
  produce solo missioni a partenza in volo; la missione `Movement` usa `F.missions_for(..., only=[mbt0])`.
- Velocita': aerea e terrestre dal registro (`speed['nominal']`), mai scritte a mano. Gli istanti delle
  sessioni 2-4 sono `max(ledger.last_end, ledger.ready_at(...))` calcolati nel `setUpClass`.
- `test_turnaround_rearms_and_refuels` verifica il rifornimento confrontando il carburante dopo la sessione
  3 con `FUEL_FULL - consumed_s3` (il solo consumo della rotta 3): se il rifornimento non fosse avvenuto
  il carburante sarebbe `FUEL_FULL - consumed_s1 - consumed_s3`.
- `test_ledger_round_trip` e `test_restore_position` usano `Campaign_State` reale con snapshot della
  sessione 1 catturato nel `setUpClass` (posizioni gia' applicate) e `Region` reale (`Context/Region`).
- `test_ready_assets` calcola l'atteso da `ledger.is_ready` (non scrive l'elenco a mano).

## 5. Costanti stimate
Nessuna nuova rispetto alla tabella §4.4 gia' presente (`Context/Context.py`, dichiarata STIMA DI
PROGETTO). Le posizioni dello scenario sono "dichiarate di test" nel docstring (posizioni di scenario, non
dati tarati). Le soglie dei test sono confronti strutturali calcolati dal registro, non numeri calibrati.

## 6. Verifiche eseguite (copiare le righe dell'ESITO, non riassumerle)
Il compito vieta esplicitamente suite e confronto ("NON eseguire suite ne' confronto"): non eseguiti. Solo
test mirati, per singola classe:
- `python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S30`:
  `Ran 8 tests in 0.242s` · `OK`
- `python3 -m unittest ...Test_Session_Scenarios_S10_S18.TestS11SessionBoundary`:
  `Ran 12 tests in 6.014s` · `OK (skipped=2)`
- `python3 -m unittest ...Test_Session_Validation.TestAgnosticEndToEnd`:
  `Ran 7 tests in 1.403s` · `OK`

Interprete usato: il `python3` di sistema (il piano per S30 non richiede suite/confronto, quindi non e'
stato lanciato `tools/ai/verifica.sh`). Compilazione con `py_compile` dei file Python modificati: OK.

## 7. Limiti noti e dubbi per la sessione principale
- La fotografia NON e' stata installata (come da compito): dopo l'installazione la colonna attesa e'
  `982 identiche, 4 nuove (S30-CAMPAIGN-1..4)`. Le 4 sessioni sono eseguite nel `setUpClass` della nuova
  classe, quindi `Scenario_Baseline.capture` le registrera' come 4 esecuzioni.
- `test_restore_position` esegue una sessione 1 in piu' dentro il metodo di test (fuori dal `setUpClass`):
  non compare nella fotografia (che esegue solo `setUpClass`/`tearDownClass`).
- `test_turnaround_rearms_and_refuels` usa la distanza identica delle rotte 1 e 3 per distinguere il
  rifornimento; se la ricerca F8-R cambiasse `GROUND_TURNAROUND_S` resterebbe valido (dipende solo dal
  consumo, non dal tempo).
- Il rumore in stdout delle "score" di `Aircraft_Data` durante la costruzione degli asset e' preesistente
  e non tocca l'esito.

## 8. Stato git
`git status --short`:
```
 M Code/Dynamic_War_Manager/Source/Command/Session_Types.py
 M Code/Dynamic_War_Manager/Source/Logic/Mission_Adapter.py
 M Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S10_S18.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Session_Validation.py
?? Analysis/Document/Rapporti/Rapporto_F8c3_oc-developer.md
?? Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S30.py
```
`git log --oneline -5`:
```
8042ad19 OpenCode: routing dei fornitori spostato in ai-multimodel (...)
637e27ef Registro costi: F8c2 reale 0,4785 $ con StreamLake; memoria: blocco 2 fatto, ...
6d3497bc Merge ai/oc-f8c2: F8c blocco 2 (...)
97ea2c57 F8c blocco 2: rapporto dell'esecuzione (...)
3846dc99 WIP: F8c blocco 2 — Session_Campaign (...)
```