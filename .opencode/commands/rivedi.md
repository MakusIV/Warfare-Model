---
description: Revisione indipendente di un branch rispetto al suo piano. Uso - /rivedi <branch> <Proposta_X.md> [branch base]
agent: oc-reviewer
---
Rivedi il lavoro sul branch e rispetto al piano indicati qui: $ARGUMENTS
(se il branch base non e' indicato usa `analysis/dce-dcs-persistence`).
Controlla aderenza al piano, correttezza, vincoli di AGENTS.md, copertura dei test (sezione "Copertura dei test") e veridicita' del rapporto dell'esecutore.
Scrivi `Analysis/Document/Rapporti/Revisione_<tema>_oc-reviewer.md` con i problemi ordinati per gravita', ciascuno con `file:riga`, scenario e correzione suggerita.
