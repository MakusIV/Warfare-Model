# Sonde della Proposta "bersagli intercettabili dalla difesa aerea" (`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`)

Script di sola lettura scritto da `des-planner` il 2026-11-07. Non installa fotografie e non scrive nel codice: l'uscita
completa va nella cartella indicata (`.ai-run/`, fuori dal versionamento); qui sono copiati solo i riassunti (`b0/`).
**Mai in parallelo con suite o confronto** (`tools/ai/verifica.sh`).

| Sonda | Quando | Cosa | Esito | File |
|---|---|---|---|---|
| B-0 | prima di ogni codice | per esecuzione: colpi intercettabili arrivati su forze con intercettori e colpi fermati, per arma/categoria, lanciatore, bersaglio e intercettore; esecuzioni che cambierebbero con la regola nuova in due varianti per le armi di test | **eseguita il 2026-11-07 sul ProArt**, v. sotto | `probe_intercepts.py` |
| B-1 | dopo il blocco 2 del piano | accende `BI_AD_TARGET_RULE` in memoria e riesegue il confronto | da scrivere dall'esecutore (modello: `../Sonde_Finestre_Passaggio/probe_switch_on.py`) | — |

## Comandi (dalla root del repo)

`<python>` = l'interprete che `bash tools/ai/verifica.sh` stampa nell'ESITO (sul ProArt `.direnv/python-3.12/bin/python3`).

    mkdir -p .ai-run/sonde_bersagli/b0
    # prova rapida (~12 s): solo S19
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/probe_intercepts.py .ai-run/sonde_bersagli/test 'S19'
    # sonda completa
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Bersagli_Intercettabili/probe_intercepts.py .ai-run/sonde_bersagli/b0 \
        > .ai-run/sonde_bersagli/b0/log.txt 2>&1
    grep -E '^(compared|DIFF|PROBE_RC|RUNS|TOTALS|UNITS_WITH|CHANGED|STOPPED|FACING|RINT)' .ai-run/sonde_bersagli/b0/log.txt
    grep -c '^DIFF' .ai-run/sonde_bersagli/b0/log.txt     # deve essere 0

## Tempi (ProArt, 2026-11-07)

- prova rapida su S19 (28 esecuzioni): 12,5 s;
- sonda completa: avvio 13:19:51, fine 13:28:02 (~8 minuti); confronto interno `487.6 s`.

## Esito B-0 (copiato in `b0/esito.txt`, `b0/stats.json`, `b0/esecuzioni_con_intercettazioni.txt`)

    compared 1029 runs: 20 difference lines (487.6 s)      # tutte NEW S32-DWELL, 0 DIFF: la sonda non altera il motore
    PROBE_RC 1                                              # atteso (le righe NEW contano come differenze)
    RUNS 1029 (in fotografia 1009, nuove 20)
    TOTALS {"interceptable_rounds": 2847, "interceptable_rounds_facing_interceptors": 615, "replay_mismatch": 0,
            "resolutions": 23721, "resolutions_with_interceptors": 308, "stopped_rounds": 397}
    RUNS_WITH_STOPS 16 (in fotografia 16)
    UNITS_WITH_STOPS {"S16": 4, "S19AD": 6, "S2": 2, "S6": 4}
    CHANGED[unmodelled_as_before] 6 (in fotografia 6) UNITS {"S19AD": 6}
    CHANGED[by_role] 8 (in fotografia 8) UNITS {"S19AD": 6, "S2": 2}

`replay_mismatch` 0: la ricostruzione dell'allocazione colpo -> intercettore coincide con quella del motore.
`CHANGED[...]` = esecuzioni in cui almeno un colpo escluso dalla regola e' stato fermato (le sole che possono cambiare,
v. docstring dello script): `unmodelled_as_before` = armi di test senza vincolo (BI-8 (a)); `by_role` = armi di test per
ruolo (BI-8 (b)). La classificazione dei missili dei registri usata dalla sonda e' quella proposta in §2.2 della
Proposta (stima [S]); sulla fotografia conta solo l'AGM-65D, l'unico missile dei registri fermato.
