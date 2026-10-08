---
name: feedback-model-effort-delegation
description: "Regola concordata 2026-10-08 su quale modello/sforzo usare per il principale e per i sub-agenti, e come proporlo all'utente"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4b5fdb17-4e5b-46ee-ad95-08f076180fc8
  modified: 2026-10-08T13:17:45.491Z
---

Modello principale: **Opus 5.5, sforzo high** (deciso dall'utente 2026-10-08). Decide con l'utente, orchestra i sub-agenti e verifica prima del commit.

Assegnazione per tipo di attività:
- Decisioni di design, analisi, revisione piani → principale (Opus high), insieme all'utente
- Implementazione con criteri già decisi (fasi F4b, F4c…) → `des-developer`, Opus medium
- Modifiche meccaniche/ripetitive (rinomine, test a schema fisso, inserimento dati armi DCS) → sub-agente Sonnet medium
- Manuale DES / doc Markdown+Mermaid → `des-manual-writer`, Sonnet high
- Ricerche nel codice → `Explore`, Haiku o Sonnet low
- Ingestione documenti lunghi (PDF, doc DCS) → sub-agente Sonnet medium
- Bug difficili/causa ignota → principale o `des-developer`, Opus high

**Why:** l'utente vuole che il principale lo aiuti a decidere l'uso di modelli e sforzi adeguati; il risparmio viene dal delegare l'esecuzione, non dall'abbassare il principale.

**How to apply:** prima di delegare, proporre in una riga "compito → agente, modello, sforzo, motivo" e attendere conferma; se una scelta si ripete senza obiezioni diventa regola e non si chiede più. Le verifiche pre-commit restano sempre al principale (v. [[feedback-parallel-agents-verification]]).
