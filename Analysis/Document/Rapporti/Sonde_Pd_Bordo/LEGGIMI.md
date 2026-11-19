# Sonde PB (Pd al bordo della portata), blocco 2

Eseguite il 2026-11-19 sul ProArt dalla sessione principale, a codice `598af98e` (blocco 1 mergiato), contro la fotografia da 1219 (`fdb78b86`). Nessun file del repository modificato.

- `probe_pd_edge.py` / `suite_pd_edge.py`: script delle Appendici A e B della Proposta (`PYTHONPATH=. <python> probe_pd_edge.py <on|off> <dir_uscita> <fotografia>`; `suite_pd_edge.py <on|off>`). Controllo con `off` su `S36-GRAZE|S23`: 96 esecuzioni, 0 cambiate.
- `gen_report.py`: genera le sezioni 1-4 di `../PB_Esecuzioni_Cambiate.md` da `report_on.json`.
- `report_on.json`: riepilogo della cattura con interruttore acceso (la cattura completa, ~14 MB, non e' conservata: si rigenera con la sonda).
- `changed_list_on.txt`: le 752 esecuzioni cambiate = **esito atteso esatto** del confronto del blocco 3 (le altre 467 devono restare identiche).
- `suite_on_falliti.txt`: esito della suite con l'interruttore acceso (10 falliti).
