# Sonde della Proposta "finestre per passaggio nella portata propria" (`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`)

Script di sola lettura scritti da `des-planner` il 2026-11-06. **Nessuna sonda e' stata ancora eseguita**: P-0 e' il
primo passo della prossima sessione (ProArt), P-1 si esegue solo dopo il blocco 1 del piano.
Nessuno dei due installa una fotografia o scrive nel repository: l'uscita va nella cartella indicata (usare
`.ai-run/`, fuori dal versionamento). **Mai in parallelo con suite o confronto** (`tools/ai/verifica.sh`).

| Sonda | Quando | Cosa | Esito atteso | File |
|---|---|---|---|---|
| P-0 | prima di ogni codice | conta, per ogni esecuzione, le direzioni di rilevamento con >= 2 passaggi nel volume proprio dentro una finestra (estrazioni in piu'), piu' i contatori di FP-3 (salve dopo il passaggio) e FP-5 (R-INT) | confronto invariato: `compared 1029 runs: 20 difference lines`, tutte `NEW S32-DWELL/...`, **0 righe DIFF** | `probe_passes.py` |
| P-1 | dopo il blocco 1 | accende in memoria `FP_PER_PASS_DETECTION` e riesegue il confronto | le esecuzioni cambiate sono un sottoinsieme delle righe MULTI (o RINT) di P-0 | `probe_switch_on.py` |

## Comandi (dalla root del repo)

`<python>` = l'interprete che `bash tools/ai/verifica.sh` stampa nell'ESITO (sul ProArt `.direnv/python-3.12/bin/python3`,
mai `python3` nudo se esiste il venv).

    mkdir -p .ai-run/sonde_passaggi/p0
    # prova rapida (secondi): una sola unita'
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_passes.py .ai-run/sonde_passaggi/p0 'ORC-base'
    # sonda completa: ~11-13 minuti sul ProArt [stima: confronto ~10 min + misura], ~20-22 su osboxes (confronto 1175 s)
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_passes.py .ai-run/sonde_passaggi/p0 \
        > .ai-run/sonde_passaggi/p0/log.txt 2>&1
    grep -E '^(compared|DIFF|PROBE_RC|RUNS|TOTALS|HIST|UNITS|MODELS)' .ai-run/sonde_passaggi/p0/log.txt
    grep -c '^DIFF' .ai-run/sonde_passaggi/p0/log.txt          # deve essere 0
    grep -E '^(MULTI|AFTER_PASS|RINT) ' .ai-run/sonde_passaggi/p0/log.txt

    # P-1, solo dopo il blocco 1:
    mkdir -p .ai-run/sonde_passaggi/p1
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_switch_on.py .ai-run/sonde_passaggi/p1 \
        > .ai-run/sonde_passaggi/p1/log.txt 2>&1
    grep -E '^(compared|DIFF|NEW|PROBE_RC)' .ai-run/sonde_passaggi/p1/log.txt

Il `PROBE_RC` di P-0 vale 1 (le 20 righe NEW di S32 contano come differenze): e' atteso. Una sola riga `DIFF` in P-0
significa che la sonda ha alterato il motore: fermarsi e riferire.

## Come si leggono le righe di P-0

- `RUNS_WITH_MULTI n (in fotografia m)`: esecuzioni con almeno una direzione a piu' passaggi. Con la regola accesa
  **solo queste** (piu' quelle RINT, v. sotto) possono cambiare; con lo stream separato raccomandato (FP-2) ne
  cambia un sottoinsieme, quello in cui l'occasione in piu' (o la Pd del primo passaggio, o la fine del candidato)
  cambia una decisione.
- `TOTALS.extra_draws`: estrazioni in piu' su tutta la fotografia; `HIST`: direzioni per numero di passaggi.
- `multi_outer` deve essere 0 (un osservatore con la portata maggiore ha un solo passaggio per finestra per
  costruzione); diverso da 0 = segnalare.
- `cpa_not_first`, `flip_d1`: direzioni in cui il CPA della finestra non e' nel primo passaggio, e rilevamenti di
  oggi che con la distanza del solo primo passaggio non ci sarebbero (FP-4).
- `salvos_next_pass`, `salvos_gap`: salve che dipendono dalla fine del candidato (FP-3); `AFTER_PASS`: salve di un
  osservatore con portata minore e un solo passaggio dopo la fine del passaggio (cambierebbero solo con FP-3 (a)).
- `RINT`: coppie con piu' rilevamenti a istanti diversi in cui l'ultimo non e' il primo (cambiano solo con FP-5 (a)).

I numeri della sonda (righe RUNS/TOTALS/HIST/UNITS/MODELS ed elenco MULTI) vanno riportati nella Proposta, §1.8
("Esito"), da chi pianifica (`des-planner`), prima delle decisioni FP.
