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

Chiave `opencode-osboxes`: limite 10 $ (alzato il 2026-10-22); speso a questa data circa 4,3 $ (stima: 4,07 + 0,04 prove precedenti + 0,16).
Confronto F8a / F8b: con Azure/Relace 4,07 $ per un passo piu' piccolo, con Baidu 0,16 $ per F8b: ~25 volte meno a parita' di richieste.
