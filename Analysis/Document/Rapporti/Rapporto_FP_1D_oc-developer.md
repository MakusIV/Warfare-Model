# Rapporto FP sotto-blocco 1D — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-fp` · **piano eseguito**: `Analysis/Document/Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (§4.1.2, punto 12 di §4.1.1, test 15-17)
- **Data**: 2026-11-11

## 1. Esito in una riga
Completato: cablaggio nel simulatore (`PASS_EVENT_TAG`, `pass_event_id`, blocco in `engage` che passa
`pass_rng` solo con l'interruttore acceso) e docstring del risolutore (punto 12); 3 test nuovi in
`TestPerPassDetectionSwitch`. Modulo `Test_Session_Simulator` a 170 test OK.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Session_Simulator.py` | Aggiunti `PASS_EVENT_TAG = 'detection_pass'` (dopo `TEMPER_EVENT_TAG`), la funzione `pass_event_id(*force_ids)` (dopo `temper_event_id`), il blocco in `engage` subito dopo il blocco D-5 che passa `extra['pass_rng']` solo se `ER.FP_PER_PASS_DETECTION` (testo TALE E QUALE del piano), e la sezione di docstring `## Rilevamento per passaggio (FP)` dopo quella della D-5. |
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | SOLO docstring del modulo, punto 12: (i) parentesi del contratto RNG estesa "(invariato dalla D-5 e dal rilevamento per passaggio: ...)"; (ii) frase su FP-5 (d) nel punto 4 (R-INT); (iii) sezione nuova `## Rilevamento per passaggio nella portata propria (FP, interruttore FP_PER_PASS_DETECTION, temporaneo)`. Nessuna riga di codice. |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Simulator.py` | Aggiunta la classe `TestPerPassDetectionSwitch(_Base)` con i 3 test 15, 16, 17 (nomi del piano), modellata su `TestDwellTimeSwitch`. |
| `Analysis/Document/Rapporti/Rapporto_FP_1D_oc-developer.md` | Questo rapporto. |

## 3. Scostamenti dal piano
Nessuno. I testi di `Session_Simulator.py` (punti 1-4 di §4.1.2) e le parti (i) e (ii) del punto 12 sono
stati trascritti parola per parola. Le righe del piano indicavano `TEMPER_EVENT_TAG` a `:798` e `engage`
a `:2707`, ma nel file attuale i simboli erano gia' spostati (`:798` -> `:798`, `:2707` -> `:2707` coerenti;
i nomi trovati con `grep` come da consegna). Nessun disallineamento di contenuto.

Nota: la parte (iii) del punto 12 descrive il TITOLO e i CONTENUTI della sezione del docstring del
risolutore, ma non ne fornisce il testo letterale (a differenza dei punti 1-4 e di (i)/(ii)): il testo e'
stato redatto seguendo la descrizione del piano e lo stile delle sezioni esistenti (D-5). V. §4.

## 4. Scelte minori prese
- Sezione (iii) del docstring del risolutore: redatta (non trascritta) perche' il piano ne da' titolo e
  contenuti, non il testo. Ho riportato tutte le voci richieste: regola dell'utente (un'occasione per
  passaggio, mai la somma), passaggi dai tratti (`_own_passes`, `_own_intervals`), FP-2=O3, FP-4=(a),
  FP-3=(a) (candidato fino alla fine del passaggio per l'osservatore con la portata minore, salve gia'
  lanciate non cambiano), FP-5=(d), FP-6=(a), FP-10=(c) (unione entro il dwell del sensore, solo con la
  D-5 accesa), ripiego senza tratti, la frase "spento (`pass_rng` None) il rilevamento e' quello di prima"
  e il criterio di rimozione (ripreso dal commento dell'interruttore gia' presente: sonda P-1, lettura
  delle esecuzioni cambiate dall'utente, fotografia nuova installata dall'utente, blocco di pulizia).
- Test 16: "metodo `random` chiamabile" trascritto come `callable(kwargs['pass_rng'].random)`, piu' fedele
  al testo del piano rispetto a un controllo di tipo.
- Test 17: usa le funzioni di modulo `SS.pass_event_id` / `SS.engagement_event_id` / `SS.temper_event_id`,
  senza passare da `_run` (test puro).

## 5. Costanti stimate
Nessuna: nessuna costante numerica nuova in nessuno dei tre file.

## 6. Verifiche eseguite (copiare le righe dell'ESITO, non riassumerle)
- `Test_Session_Simulator` (intero modulo, prima del commit): `Ran 170 tests` · `OK` (atteso 167+3=170).
- `Test_Engagement_Resolver`: `Ran 373 tests` · `OK`.
- `Test_Fire_Control`: `Ran 111 tests` · `OK`.
- `py_compile` su `Session_Simulator.py`, `Engagement_Resolver.py`, `Test_Session_Simulator.py`: OK.
- **NON eseguiti** (spettano alla sessione principale): suite completa `verifica.sh suite` e confronto
  con la fotografia (`verifica.sh confronto`), completo e parziale; la conferma che le ~1093 esecuzioni
  restino IDENTICAL spetta al principale (come per 1A/1B/1C).

## 7. Limiti noti e dubbi per la sessione principale
- A interruttore spento (default) `engage` non passa `pass_rng` e la chiamata e' letteralmente quella di
  prima: comportamento invariato (coperto dal test 15 e dal fatto che i 373 test del risolutore restano OK).
- Il testo della sezione (iii) del docstring del risolutore e' stato redatto da me: la sessione principale
  puo' verificare fedelta' lessicale ai contenuti del piano se lo ritiene necessario.
- Non ho eseguito il confronto con la fotografia: la conferma delle esecuzioni IDENTICAL spetta al principale.

## 8. Stato git
Output di `git status --short` e `git log --oneline -5` al momento della scrittura (prima del commit).