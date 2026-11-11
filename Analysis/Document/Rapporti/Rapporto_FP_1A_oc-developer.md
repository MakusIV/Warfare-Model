# Rapporto FP 1A — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-fp` · **piano eseguito**: `Analysis/Document/Proposta_Finestre_Per_Passaggio_Portata_Propria.md`
- **Data**: 2026-11-11

## 1. Esito in una riga
Completato: solo il sotto-blocco 1A (interruttore spento, `Detection`, `_join_passes`, `_detection_time_in_pass`,
`_own_intervals`, FP-6). Test nuovi verdi; suite del modulo `Ran 351 OK`. Il confronto parziale (step 7) NON e'
stato eseguito per un vincolo di permessi degli strumenti (dettaglio in §6 e §7).

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | Interruttore `FP_PER_PASS_DETECTION = False` con commento del piano (subito dopo `VA_ENGAGEMENT_ALTITUDE_BAND`); docstring + 4 campi `pass_*` su `Detection`; funzioni di modulo `_join_passes` e `_detection_time_in_pass` (dopo `registry_dwell_time`); metodo `_own_intervals` su `_EngagementRun`; ramo FP-6 di `_exposure_time` + docstring del metodo + docstring del modulo (sezione D-5); `_detection_time` che passa da `_own_intervals` (8-bis). |
| `Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py` | Classe nuova `TestDetectionPerPass` (geometria comune + test 1, 13, 30); test 14 e 23 in `TestDwellTimeInTheResolver`. |

## 3. Scostamenti dal piano
Nessuno di codice. Le righe citate dal piano sono del checkout `97620f55` e risultano spostate (il piano stesso lo
avverte in §4.0 punto 5): ho cercato **per nome** (`Detection`, `registry_dwell_time`, `_detection_time`,
`_exposure_time`, `_EngagementRun`, `D5_DWELL_TIME`, `VA_ENGAGEMENT_ALTITUDE_BAND`). Firme e interruttori coincidono
con il piano; `FP_PER_PASS_DETECTION` non esisteva prima (precondizione rispettata).

## 4. Scelte minori prese
- Geometria comune definita come costanti di classe di `TestDetectionPerPass` (`B1_LEGS`, `R1_LEGS`, `LEGS`,
  `WINDOW`); i test 14 e 23 in `TestDwellTimeInTheResolver` la richiamano a runtime (`TestDetectionPerPass.LEGS`,
  `.WINDOW`, `.B1_LEGS`).
- Test 23: i tratti "scambiati" di `r1` sono definiti in linea (non sono nella geometria comune), ma la gamba
  dell'osservatore riusa `TestDetectionPerPass.B1_LEGS`.
- Test 13: ho raggruppato valore restituito e predicato "visto" (`x is not None and x <= t + ER.TIME_EPS`) in un
  unico ciclo, provando entrambi gli ordini di `times` (`[210, 390]` e `[390, 210]`) con `subTest`.
- RNG dei test 14 e 23: `_ScriptedRng([0.5, 0.5])` (il piano non specifica i valori; l'asserzione riguarda
  `exposure_s` e `probability`, indipendenti dal draw).
- La nuova classe `TestDetectionPerPass` e' collocata subito prima di `TestDwellTimeInTheResolver`. Il logger e'
  mockato in `setUp` con `patch(_ER_LOGGER, MagicMock())` come negli altri test.

## 5. Costanti stimate
Nessuna. Le tolleranze sono `TIME_EPS` esistente; i dwell dei test (400 s) sono valori dichiarati di test.

## 6. Verifiche eseguite (copiare le righe dell'ESITO, non riassumerle)
- Conteggio di riferimento (prima di toccare il codice): `.direnv/python-3.12/bin/python3 -m unittest
  Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver` → `Ran 346 tests in 0.839s` / `OK`. **N_prima = 346**.
- Dopo le modifiche: stesso comando → `Ran 351 tests in 0.843s` / `OK` (= 346 + 5 attesi).
- Test singoli nuovi, tutti `OK`:
  - `TestDetectionPerPass.test_switch_is_off_by_default`
  - `TestDetectionPerPass.test_detection_time_in_pass`
  - `TestDetectionPerPass.test_join_passes_boundary`
  - `TestDwellTimeInTheResolver.test_exposure_is_the_pass_containing_the_cpa`
  - `TestDwellTimeInTheResolver.test_exposure_falls_back_to_the_longest_pass`
- `grep -n "range_intervals(" .../Engagement_Resolver.py` → solo `engagement_intervals` (`:1885`) e `_own_intervals`
  (`:2467`): come richiesto dal piano (nessuna funzione VA chiama `range_intervals` direttamente).
- Compilazione: `py_compile` su entrambi i file → nessun errore.
- **Confronto parziale (step 7): NON eseguito.** Il comando richiesto
  `.direnv/python-3.12/bin/python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare
  .ai-run/fp_base_capture.json --only 'S32' --quiet` non e' fra i comandi consentiti dall'harness (l'allow-list
  copre solo `*python3 -m unittest*`, i due `py_compile` e `bash tools/ai/verifica.sh suite|confronto`): la chiamata
  e' stata respinta. Non ho lanciato `verifica.sh suite`/`confronto` perche' il compito li vieta esplicitamente per
  il sotto-blocco 1A. `.ai-run/fp_base_capture.json` esiste (13,4 MB, 2026-11-11 16:43), quindi la precondizione
  dello step 7 (file presente) e' soddisfatta: manca solo l'esecuzione del confronto.

## 7. Limiti noti e dubbi per la sessione principale
- Il confronto parziale S32 (step 7) non e' stato eseguito per il vincolo di permessi di cui sopra. Atteso dal piano:
  nessuna differenza (exit 0: S32 ha la D-5 accesa e un solo passaggio per direzione, quindi FP-6 non cambia nulla).
  La correttezza di FP-6 e' comunque coperta dai test 14 e 23 (che esercitano esattamente il ramo nuovo di
  `_exposure_time`) e dall'invariabilita' dei 346 test preesistenti (`Ran 351 OK`).
- Da fare a fine blocco 1 dal **principale** (non da questo esecutore): suite completa, confronto completo e verifica
  `IDENTICAL` sulle 1093 esecuzioni.
- Non ho toccato `Session_Simulator.py`, `Scenario_Baseline.py`/la fotografia, la Proposta, il manuale, `.claude/`,
  `AGENTS.md`, `.opencode/`, `tools/ai/`.
- Le parti "inerti" con l'interruttore spento (campi `pass_*`, `_join_passes`, `_detection_time_in_pass`,
  `_own_intervals`, rinvio di `_detection_time` via `_own_intervals`) sono state verificate solo per assenza di
  regressioni, non da test dedicati (i test funzionali dei passaggi arrivano in 1B/1C/1D).

## 8. Stato git
`git status --short`:
```
 M Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py
?? Analysis/WIKI_LLM_SIMULATION/RAW/Logistica/
```
`git log --oneline -5`:
```
613d1cf0 Memoria: ripresa dal ProArt (stato, base 4876/1093:84, prossime attivita')
436b5905 Costi e memoria: VA blocco 2 mergiato (suite 4876, confronto 1093:84), VA completa
2e4203fe Merge ai/oc-va-blocco2: VA blocco 2 (scenario S34-BAND, 9 test, 32 esecuzioni nuove) ...
1b412618 VA blocco 2: tolta la copia della sonda come modulo unittest dalla cartella dei test ...
5d87f03d VA blocco 2: scenario S34-BAND ... e riga S34-BAND in Scenario_Baseline ...
```
Il file non tracciato `Analysis/WIKI_LLM_SIMULATION/RAW/Logistica/` e' da ignorare (indicato dal compito); non lo
committo.