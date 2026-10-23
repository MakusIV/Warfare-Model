# Costi delle deleghe OpenCode (registro della sessione principale)

Solo la sessione principale lo aggiorna. Fonte dei costi REALI: OpenRouter, Logs/Sessions e CSV di Activity (chiave `opencode-osboxes`);
`oc export`/`oc stats` sono stime di OpenCode (fino al 2026-10-22 sottostimavano di ~1,95 volte; da quando `opencode.json` riporta il
prezzo reale del modello 0813 la stima coincide col costo reale). Fornitori e criteri: memoria `project_opencode_costi_misurati`.

| Data | Delega | Modello | Fornitore | Richieste | Costo OpenCode | Costo reale | Note |
|---|---|---|---|---|---|---|---|
| 2026-10-22 | F8a, sessione 1 (`ses_e9c69f02…`) | V4 Pro 0423 | Azure | 103 | 1,60 $ | **3,0868 $** | interrotta dal limite della chiave; contesto fino a 160k token |
| 2026-10-22 | F8a, sessione 2 (`ses_e9c38f3b…`) | V4 Pro 0423 | Relace (fp4) | 82 | 0,50 $ | **0,979 $** | completata, commit `e593bc9a` |
| 2026-10-22 | prova del routing (`oc-planner` "OK") | V4 Pro 0813 + Flash | Baidu + CoreWeave | 2 | — | 0,0013 $ | `order` verificato |
| 2026-10-22 | F8b (`ses_e9bd5a5f…`) | V4 Pro 0813 | Baidu | 120 + 1 titolo | 0,155 $ | **0,1552 $** | 120/120 passi, codice e test completi, rapporto e commit mancanti (scritti dalla sessione principale) |
| 2026-10-23 | F8c1 (`ses_e98066773ffe…`) | V4 Pro 0813 | Baidu (83) + StreamLake (2, 429 di Baidu probabile) | 85 | 0,169 $ | **1,40 $** | prezzo Baidu x9,1 rispetto al 22/10 (1,32/3,96/0,042 $/M); 2 passaggi a StreamLake a cache fredda = 0,137 $; 276 test mirati OK al primo colpo, rapporto e commit completi |
| 2026-10-23 | prova del routing per costo (`oc-planner` "ok") | V4 Pro 0813 + Flash | StreamLake (Flash: CoreWeave 429 -> StreamLake) | 2 | 0,0057 $ | 0,00567 $ | `order` da `tools/ai/prezzi_fornitori.py`: Pro servito dal primo della lista, senza fallback; costo = previsione |
| 2026-10-23 | F8c2 (`ses_e9797f1c1ffe…`) | V4 Pro 0813 + Flash | StreamLake (61 + titolo), nessun ripiego | 62 | 0,478 $ | **0,4785 $** | primo uso del routing per costo di `bin/oc` (prezzo StreamLake 0,66/1,98/0,022 $/M); 7,0 M token prompt al 94,9% di cache; stesso consumo su Baidu (1,32 $/M) ~0,94 $; qualita': test mirati verdi al primo colpo, rapporto e commit completi, nessuna regola violata (fornitore a quantizzazione non dichiarata, non fp4) |

Chiave `opencode-osboxes`: limite 10 $ (alzato il 2026-10-22); speso a questa data circa 4,3 $ (stima: 4,07 + 0,04 prove precedenti + 0,16).
Confronto F8a / F8b: con Azure/Relace 4,07 $ per un passo piu' piccolo, con Baidu 0,16 $ per F8b: ~25 volte meno a parita' di richieste.

## Qualita' per fornitore e quantizzazione
Per ogni delega registrare il fornitore e la quantizzazione effettivi (colonna `provider_name` del CSV Activity di OpenRouter; la
quantizzazione e' nella tabella di `python3 tools/ai/prezzi_fornitori.py`) e l'esito della verifica: test mirati al primo colpo, test
ripetutamente rossi, tool call con argomenti sbagliati, regole violate (es. `git add -A`). Un fornitore fp4 sta in coda a `order` (solo
ripiego, v. `APPROVATI_FP4` nello script): se una delega servita da un fp4 mostra piu' errori, si toglie l'approvazione. Finora nessuna
delega e' stata servita da un fp4 con V4 Pro 0813 (F8a su Relace fp4 era la 0423: completata, ma con 82 richieste e un ciclo a vuoto
precedente su Azure; nessun confronto di qualita' possibile).
