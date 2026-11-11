---
name: feedback-oc-blocchi-piccoli-verifica-parziale
description: Per i lavori affidati ad agenti oc: provare blocchi piu' piccoli (costo cresce col contesto) e verifica parziale per blocco, suite+confronto completi solo a fine task (decisione utente 2026-11-10)
metadata:
  type: feedback
---

Per i lavori affidati ad agenti OpenCode si prova a dividere in blocchi piu' piccoli e a verificare per blocco solo i test significativi (moduli toccati e vicini con `python -m unittest <modulo>`, confronto parziale con `Scenario_Baseline --compare --only REGEX` sugli scenari vicini), lanciando suite e confronto completi solo alla fine dell'intero task.

**Why:** VA blocco 1 con un solo agente = 129 richieste e 1,399 $ perche' il contesto riletto a ogni passo cresce (76k -> 270k token; l'ultimo terzo vale il 44% della spesa; piano di 1238 righe letto intero). Su osboxes suite+confronto = ~40 minuti a giro.

**How to apply:** nel compito di ogni blocco elencare moduli di test e `--only`; il criterio diventa default per i soli lavori oc solo se la prova su FP risulta meno costosa e con tempi accettabili (verdetto dell'utente). AGENTS.md non si tocca (e' dell'utente). Collegata a [[project-opencode-costi-misurati]] e [[project-session-2026-11-07-summary]].

## Prova su FP (2026-11-11): dati
- Branch unico `ai/oc-fp`, un commit per sotto-blocco (1A, 1B, 1C, 1D; poi blocco 2 S33). Compito = solo le righe del piano pertinenti (`sed -n`), budget ~50 passi.
- **1A**: 46 richieste, **0,292 $**, contesto medio ~57k (VA blocco 1: 173k, VA blocco 2: 126k), un ciclo, nessuna fermata. Da confrontare col totale dei sotto-blocchi (VA blocco 1 = 1,399 $ da solo).
- **Permessi dell'agente oc-developer**: puo' lanciare solo `python3 -m unittest`, `py_compile` e `verifica.sh suite|confronto`; `Scenario_Baseline --compare --only` e' RESPINTO. Il confronto parziale lo esegue il principale dopo il commit (S32 = 8 s). Non scriverlo nei compiti come passo dell'agente.
- Cattura di base per la verifica IDENTICAL: `.ai-run/fp_base_capture.json` (1093 esecuzioni, locale, ProArt 2026-11-11).
- Dipendenza scoperta: `_exposure_time` (FP-6) e il punto 8-bis chiamano `_own_intervals` (punto 7): va in 1A; il test 20 va in 1B.
- **1B**: 65 richieste, **0,4472 $**, contesto medio ~73k; un ciclo, nessuna fermata. Totale 1A+1B = 0,7392 $ (restano 1C, 1D, blocco 2). `git stash list` e' vietato all'agente (deny): lo controlla il principale.
