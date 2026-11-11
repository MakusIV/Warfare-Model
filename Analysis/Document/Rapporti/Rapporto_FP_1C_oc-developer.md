# Rapporto FP sotto-blocco 1C — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-fp` · **piano eseguito**: `Analysis/Document/Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (punto 10)
- **Data**: 2026-11-11

## 1. Esito in una riga
Completato: regola R-INT con il rilevamento per passaggio (FP-5 (d)) — `_detection_time_of(at)` e la sua unica
chiamata in `_in_time`, piu' i 3 test del piano (21, 22, 29). Modulo `Test_Engagement_Resolver` a 373 test OK.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | `_detection_time_of`: aggiunto il parametro `at` con la logica del punto 10 (testo TALE E QUALE del piano); in `_in_time` la chiamata e' ora `self._detection_time_of(shadow.id, salvo.shooter_id, salvo.t_launch)` e nel suo docstring la frase sui passaggi (FP-5 (d)). |
| `Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py` | Aggiunti i 3 test 21, 22, 29 nella classe `TestDetectionPerPass` (nomi del piano). |
| `Analysis/Document/Rapporti/Rapporto_FP_1C_oc-developer.md` | Questo rapporto. |

## 3. Scostamenti dal piano
Nessuno. Il testo del punto 10 e' stato trascritto parola per parola; i tre test seguono
i nomi, le geometrie e le costanti del piano. La riga del piano indicava `_detection_time_of` a
`:3229-3235`, ma nel file attuale il simbolo era gia' spostato a `:3702` (come previsto dalla
nota "cerca per NOME, le righe del piano sono spostate"): nessun disallineamento di contenuto.

## 4. Scelte minori prese
- Test 21: helper privato `_rint_intercepted(self, x, t_out, pass_rng)` che replica lo schema di
  `TestInterceptionReaction._run` (`:1742-1771`) con la geometria del punto 21; restituisce
  `resolutions[0].intercepted`.
- Test 22: funzione annidata `run_for(pass_rng)` che costruisce `ER._EngagementRun` direttamente
  (due finestre, senza `legs`); "fire control None" trascritto come `lambda s, t: None`, coerente con
  la traduzione che fa gia' `_run_direct` (`fire if fire is not None else (lambda s, t: None)`).
- Commento di sezione `# ── sotto-blocco 1C: ... ──` allineato ai marcatori gia' presenti (1A/1B).

## 5. Costanti stimate
Nessuna: nessuna costante numerica nuova nel motore ne' nei test (i dwell 140/139, la portata
1500 m, le velocita' 1000/500 m/s sono tutti valori dichiarati di test nel piano).

## 6. Verifiche eseguite (copiare le righe dell'ESITO, non riassumerle)
- `Test_Engagement_Resolver` (intero modulo): `Ran 373 tests` · `OK`.
- `Test_Fire_Control`: `Ran 111 tests` · `OK`.
- `Test_Session_Simulator`: `Ran 167 tests` · `OK`.
- `Test_Anti_Missile`: non esiste (`ls Code/Dynamic_War_Manager/Source/Test | grep -i missile` vuoto);
  nessun altro modulo "missile" presente.
- `py_compile` su `Engagement_Resolver.py` e `Test_Engagement_Resolver.py`: compilati senza errori.
- Test singoli nuovi eseguiti in isolamento: tutti e 3 OK prima del modulo intero.
- **NON eseguiti** (spettano alla sessione principale): suite completa `verifica.sh suite` e
  confronto con la fotografia (`verifica.sh confronto`), completo e parziale.

## 7. Limiti noti e dubbi per la sessione principale
- Con `pass_rng` assente o `at` None, `_detection_time_of` restituisce lo stesso valore di prima
  (stesso dizionario `detected_at`, stesso ordine di costruzione): verificato con il modulo intero (373 OK)
  e dal test 22 (`on == off`).
- Non ho eseguito il confronto con la fotografia: la conferma che le esecuzioni esistenti restino
  IDENTICAL spetta al principale (come per 1A e 1B).

## 8. Stato git
Output di `git status --short` e `git log --oneline -5` al momento della scrittura (prima del commit).