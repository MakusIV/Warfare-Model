# Sonde della Proposta D-5 opzione 2 (`Proposta_Dwell_Time_Rilevamento.md`, §1.9)

Copia versionata degli script di sola lettura scritti da `des-planner` il 2026-11-05 (la cartella originale `.ai-run/` e' fuori dal versionamento).
Accendono la legge in memoria e rieseguono il confronto con la fotografia, senza installare nulla e senza toccare il repository.

Per riprenderle su un'altra macchina (dalla root del repo; sul ProArt usare l'interprete del venv che `bash tools/ai/verifica.sh` stampa nell'ESITO, mai `python3` nudo; mai in parallelo con suite o confronto):

    mkdir -p .ai-run/sonde_dwell && cp -r Analysis/Document/Rapporti/Sonde_Dwell_D5/* .ai-run/sonde_dwell/
    # S-3 (geometria di S32-DWELL, pochi minuti, MAI eseguita):
    <python> .ai-run/sonde_dwell/probe_s32.py > .ai-run/sonde_dwell/s3_log.txt 2>&1
    # S-2 (dwell uniforme di 10 s, circa 19 minuti su osboxes, INCOMPLETA):
    mkdir -p .ai-run/sonde_dwell/s2 && <python> .ai-run/sonde_dwell/probe_dwell.py uniform:10 .ai-run/sonde_dwell/s2 > .ai-run/sonde_dwell/s2/log.txt 2>&1
    grep -E '^(compared|CHANGED|NEW|PROBE_RC)' .ai-run/sonde_dwell/s2/log.txt

Contenuto: `probe_dwell.py` (S-1 e S-2), `probe_s32.py` (S-3), `s1/stats.json` e `s1/log.txt` (esito completo di S-1: 1009 IDENTICHE con la legge accesa).
Il log parziale di S-2 non e' stato copiato (nessun esito).
