---
name: feedback-oc-blocchi-piccoli-verifica-parziale
description: Per i lavori affidati ad agenti oc: provare blocchi piu' piccoli (costo cresce col contesto) e verifica parziale per blocco, suite+confronto completi solo a fine task (decisione utente 2026-11-10)
metadata:
  type: feedback
---

Per i lavori affidati ad agenti OpenCode si prova a dividere in blocchi piu' piccoli e a verificare per blocco solo i test significativi (moduli toccati e vicini con `python -m unittest <modulo>`, confronto parziale con `Scenario_Baseline --compare --only REGEX` sugli scenari vicini), lanciando suite e confronto completi solo alla fine dell'intero task.

**Why:** VA blocco 1 con un solo agente = 129 richieste e 1,399 $ perche' il contesto riletto a ogni passo cresce (76k -> 270k token; l'ultimo terzo vale il 44% della spesa; piano di 1238 righe letto intero). Su osboxes suite+confronto = ~40 minuti a giro.

**How to apply:** nel compito di ogni blocco elencare moduli di test e `--only`; il criterio diventa default per i soli lavori oc solo se la prova su FP risulta meno costosa e con tempi accettabili (verdetto dell'utente). AGENTS.md non si tocca (e' dell'utente). Collegata a [[project-opencode-costi-misurati]] e [[project-session-2026-11-07-summary]].
