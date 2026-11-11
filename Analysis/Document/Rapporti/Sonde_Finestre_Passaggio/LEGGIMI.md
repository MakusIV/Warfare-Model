# Sonde della Proposta "finestre per passaggio nella portata propria" (`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`)

Script di sola lettura scritti da `des-planner` il 2026-11-06; `probe_switch_on.py` (P-1) riscritto il 2026-11-08 con le
decisioni FP-1..FP-10 tutte prese (attesa confermata dall'utente la sera del 2026-11-08: solo testo, nessun cambio
di logica). **P-0 eseguita il 2026-11-07 sul ProArt** (esito sotto e in `esito_p0.txt`); **P-1 eseguita il 2026-11-11 sul ProArt**
dalla sessione principale dopo il blocco 2 (esito in `esito_p1.txt`: 44 esecuzioni cambiate = esattamente le 44 `AFTER_PASS`
di P-0, 0 `RINT_D`, 0 passaggi di durata zero su 34116, 0 cambiate fra le nuove S32/S34/S35).
Nessuno dei due installa una fotografia o scrive nel repository: l'uscita va nella cartella indicata (usare
`.ai-run/`, fuori dal versionamento). **Mai in parallelo con suite o confronto** (`tools/ai/verifica.sh`).

| Sonda | Quando | Cosa | Esito atteso | File |
|---|---|---|---|---|
| P-0 | prima di ogni codice (FATTA il 2026-11-07) | conta, per ogni esecuzione, le direzioni di rilevamento con >= 2 passaggi nel volume proprio dentro una finestra (estrazioni in piu'), piu' i contatori di FP-3 (salve dopo il passaggio) e FP-5 (R-INT) | confronto invariato, 0 righe DIFF | `probe_passes.py` |
| P-1 | dopo il blocco 1 | accende in memoria `FP_PER_PASS_DETECTION`, riesegue il confronto; conta i passaggi di durata zero e le decisioni R-INT cambiate da FP-5 (d) | righe `DIFF` (esecuzioni della fotografia cambiate) **al piu'** le 44 `AFTER_PASS` di P-0 **piu' le eventuali `RINT_D`** elencate dalla stessa P-1 (v. sotto); attesa NON misurata, confermata dall'utente il 2026-11-08 sera | `probe_switch_on.py` |

## Esito di P-0 (2026-11-07, ProArt; estratto in `esito_p0.txt`)

`compared 1029 runs: 20 difference lines` (tutte `NEW S32-DWELL/...`, 0 righe DIFF), `RUNS_WITH_MULTI 0`,
`RUNS_WITH_RINT 0`, `RUNS_WITH_AFTER_PASS 44` (151 salve: S13 2 esecuzioni, S14 1, S21 6, S24-ORBIT 1, S26-BINGO 32,
S28-CLASS 2), `HIST {"0": 946, "1": 32964}`. Nessuna direzione con piu' di un passaggio nel volume proprio. P-0 NON ha
contato i passaggi di durata zero (un passaggio tangente conta come 1 nell'istogramma) ne' l'effetto di FP-5 (d): li
conta P-1.

## Comandi (dalla root del repo)

`<python>` = l'interprete che `bash tools/ai/verifica.sh` stampa nell'ESITO (sul ProArt `.direnv/python-3.12/bin/python3`,
mai `python3` nudo se esiste il venv).

    # P-0 (gia' eseguita; da ripetere solo su richiesta):
    mkdir -p .ai-run/sonde_passaggi/p0
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_passes.py .ai-run/sonde_passaggi/p0 \
        > .ai-run/sonde_passaggi/p0/log.txt 2>&1
    grep -E '^(compared|DIFF|PROBE_RC|RUNS|TOTALS|HIST|UNITS|MODELS)' .ai-run/sonde_passaggi/p0/log.txt

    # P-1, solo dopo il blocco 1 (~8-10 minuti sul ProArt [stima sulla durata di P-0, 484 s]):
    mkdir -p .ai-run/sonde_passaggi/p1
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_switch_on.py .ai-run/sonde_passaggi/p1 \
        > .ai-run/sonde_passaggi/p1/log.txt 2>&1
    grep -E '^(compared|PROBE_RC|RUNS|ZERO_PASSES)' .ai-run/sonde_passaggi/p1/log.txt
    grep -E '^DIFF ' .ai-run/sonde_passaggi/p1/log.txt          # esecuzioni della fotografia cambiate
    grep -E '^(RINT_D|ZERO) ' .ai-run/sonde_passaggi/p1/log.txt
    # facoltativo: le esecuzioni NUOVE (S32, S35, S34; S33 se il blocco 2 e' fatto) con la regola accesa contro la
    # cattura di base del piano (regola spenta, salvata dall'esecutore prima del blocco 1, Proposta §4.0 punto 4):
    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare .ai-run/fp_base_capture.json \
        --against .ai-run/sonde_passaggi/p1/capture_on.json --ignore probe_fp_on | grep -E '^(DIFF|compared)'

## Come si legge P-1

- **Attesa** (Proposta §4.3, confermata dall'utente la sera del 2026-11-08): con la regola accesa cambiano, nella
  fotografia, **al piu' le 44 esecuzioni `AFTER_PASS` di P-0 piu' le eventuali `RINT_D`**. E' un'attesa **NON
  misurata**: P-0 ha contato le 44 `AFTER_PASS` (FP-3 (a): il candidato al tiro dell'osservatore con la portata minore
  vale fino alla fine del passaggio) senza sapere quali cambieranno, e non ha contato le `RINT_D`; i numeri veri sono
  quelli di questa sonda. `MULTI` e `RINT` di P-0 sono vuote; FP-6 (permanenza D-5 di un solo passaggio) e FP-10
  (unione dei passaggi entro il dwell) agiscono solo con la D-5 accesa, spenta in tutta la fotografia: non cambiano
  nulla qui.
- **Eccezione da leggere a parte: FP-5 (d)** (R-INT: un lancio e' "visto" solo se l'intercettore ha rilevato il
  lanciatore nel passaggio che contiene il lancio). P-0 ha misurato solo la differenza "primo contro ultimo"
  (`rint_last_not_earliest` 0), non questa. Le righe `RINT_D <esecuzione>: n su m` dicono in quante decisioni R-INT
  "visto" cambia rispetto alla regola precedente; un'esecuzione cambiata che e' `RINT_D` ma non `AFTER_PASS` si spiega
  con FP-5 (d) solo se nelle sue righe DIFF cambiano intercettazioni (`InterceptionEvent`, colpi al danno).
- Una cambiata che non e' ne' fra le 44 `AFTER_PASS` ne' fra le `RINT_D`: fermarsi e diagnosticare (implementazione
  diversa dalla regola della sonda, o un effetto del candidato esaurito che il ragionamento non copre).
- `ZERO_PASSES` e le righe `ZERO`: passaggi di durata zero (rotte tangenti al volume proprio) e passaggi ridotti a
  durata zero dal ritaglio alla finestra. Nessun esito atteso: e' un conteggio informativo per il limite di §5.2 della
  Proposta (un passaggio tangente e' un passaggio: Pd sul bordo = 0,5 x fattore; con FP-3 (a) il suo candidato non
  esiste se la reazione non e' nulla).
- Il confronto di P-1 copre le esecuzioni presenti al momento (dopo BI e VA: 1009 della fotografia + 20 S32 + 32 S35
  + 32 S34 = 1093; con il blocco 2 della FP anche le 20 S33). I conteggi `RUNS_WITH_*` distinguono fotografia e nuove.
  S33 fissa da se' gli interruttori in ogni variante (`off`/`cas_off` FP e D-5 spente; `on`/`cas_on` FP e D-5 accese
  con il dwell della ZSU 2 s, stima dell'utente): l'accensione globale di P-1 non la cambia. Nelle nuove con la D-5
  accesa (S32 `long`/`short`/`ewr_on`, S33 `on`/`cas_on`) i contatori `passes` sono dopo l'unione FP-10, che li'
  puo' agire (in S32 un passaggio per direzione, in S33 uscite molto piu' lunghe del dwell: nessuna unione attesa [I]).

I numeri di P-1 (righe compared, DIFF, RUNS_WITH_*, ZERO_PASSES ed elenchi) vanno riportati nella Proposta (§4.3) e in
`F4_Differenze_Scenari.md` dalla sessione principale, prima della decisione dell'utente sulla fotografia.
