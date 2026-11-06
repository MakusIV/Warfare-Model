# Sonde della Proposta D-5 opzione 2 (`Proposta_Dwell_Time_Rilevamento.md`, §1.9)

Copia versionata degli script di sola lettura scritti da `des-planner` il 2026-11-05 (la cartella originale `.ai-run/` e' fuori dal versionamento).
Accendono la legge in memoria e rieseguono il confronto con la fotografia, senza installare nulla e senza toccare il repository.
**Tutte e tre le sonde sono complete** (S-1 il 2026-11-05, S-2 e S-3 il 2026-11-06 su osboxes).

| Sonda | Cosa | Esito | File |
|---|---|---|---|
| S-1 | legge accesa con i soli dati di fonte | 1009 IDENTICHE (1137,8 s) | `s1/log.txt`, `s1/stats.json` |
| S-2 | dwell uniforme di 10 s per ogni osservatore (valore fittizio) | 1009 confrontate, 2 cambiate (`S21/S21-5/control`: 42 valori, `S21/S21-7/control`: 56 valori; 946,5 s) | `s2/esito_riassunto.txt` (righe DIFF e traceback) |
| S-3 | geometria di S32-DWELL, 4 semi | tutte le asserzioni di §4.A.7 confermate (rc=0) | `s3/esito.txt` |

Note:
- Nel riepilogo di S-2 "44 difference lines" sono righe di stampa, non esecuzioni cambiate.
- Il log di S-2 finiva con un `TypeError` nel salvataggio di `stats.json` (`sort_keys=True` con una chiave `None`): difetto dello
  script, non dei dati del confronto. In questa copia di `probe_dwell.py` e' corretto (`sort_keys=False`); l'`stats.json` di S-2 su
  osboxes (`.ai-run/sonde_dwell/s2/`) resta parziale e non e' stato copiato. Il log completo di S-2 e di S-3 e' solo in `.ai-run/`.

Per rieseguirle su un'altra macchina (dalla root del repo; sul ProArt usare l'interprete del venv che `bash tools/ai/verifica.sh` stampa nell'ESITO, mai `python3` nudo; `PYTHONPATH=.`; mai in parallelo con suite o confronto):

    mkdir -p .ai-run/sonde_dwell && cp -r Analysis/Document/Rapporti/Sonde_Dwell_D5/* .ai-run/sonde_dwell/
    # S-3 (pochi minuti):
    <python> .ai-run/sonde_dwell/probe_s32.py > .ai-run/sonde_dwell/s3_log.txt 2>&1
    # S-2 (dwell uniforme di 10 s, circa 16 minuti su osboxes):
    mkdir -p .ai-run/sonde_dwell/s2 && <python> .ai-run/sonde_dwell/probe_dwell.py uniform:10 .ai-run/sonde_dwell/s2 > .ai-run/sonde_dwell/s2/log.txt 2>&1
    grep -E '^(compared|DIFF|PROBE_RC)' .ai-run/sonde_dwell/s2/log.txt

Contenuto: `probe_dwell.py` (S-1 e S-2), `probe_s32.py` (S-3), `s1/`, `s2/esito_riassunto.txt`, `s3/esito.txt`.
