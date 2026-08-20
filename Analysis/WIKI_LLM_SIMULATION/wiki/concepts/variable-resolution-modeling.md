---
title: "Variable-Resolution Modeling — Variazione Dinamica del Livello di Dettaglio"
type: concept
tags: [simulation, resolution, campaign-model, cross-resolution, generalized-network]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[generalized-network]]", "[[cross-resolution-modeling]]", "[[tlc-model]]", "[[campaign-model]]", "[[cadem]]"]
---

# Variable-Resolution Modeling

## Definizione

Il **variable-resolution modeling** è la capacità di un singolo modello di **variare il livello di dettaglio della simulazione** — più alta risoluzione dove necessario (aree di combattimento attivo, settori critici), più bassa dove è sufficiente (retrovie, settori secondari).

**Distinzione fondamentale** con [[cross-resolution-modeling]]:
- *Cross-resolution*: collegamento tra **modelli separati** a risoluzioni diverse
- *Variable-resolution*: **un singolo modello** che cambia risoluzione internamente

## Motivazione

Simulare tutto ad alta risoluzione è proibitivo in termini di costo computazionale. Simulare tutto a bassa risoluzione perde dettaglio critico. La variable-resolution è il compromesso: alta risoluzione dove conta, bassa dove non conta.

```
Scenario tipico:
─────────────────────────────────────────────
│ Retrovie (bassa res) │ FRONTE (alta res) │ Retrovie (bassa res) │
│    risorse, logistica │ combattimento     │    riserve           │
─────────────────────────────────────────────
```

## Come la Generalized Network Abilita Variable-Resolution

La [[generalized-network]] del TLC supporta variable-resolution grazie alla sua struttura flessibile:

- **Regioni di dimensione variabile**: zone ad alta risoluzione hanno regioni più piccole e più dettagliate
- **Grids embeddati**: griglie ad alta risoluzione possono essere inserite all'interno della rete per settori specifici
- **Multiple reti indipendenti**: reti separate per aria, terra, mare con risoluzioni diverse per ciascuna

> "The generalized network allows variable resolution: areas of intense activity can be modeled at high resolution while areas far from the fight use low resolution." (p. 18)

## Il Problema della Combinatoria

Un limite fondamentale del variable-resolution è la **crescita combinatoria** delle interazioni:

- Con N tipi di oggetti e 2 risoluzioni: N² × 4 combinazioni di interazione (alta-alta, alta-bassa, bassa-alta, bassa-bassa)
- Per 10 tipi di oggetti: fino a **20 miliardi** di combinazioni potenziali
- Ogni combinazione richiede una regola di interazione specifica

Questo è uno dei **limiti riconosciuti dagli autori TLC**: la variable-resolution è concettualmente desiderabile ma operativamente molto complessa da implementare completamente.

## Variable-Resolution vs. Cross-Resolution: Trade-off

| Aspetto | Variable-Resolution | Cross-Resolution |
|---------|--------------------|--------------------|
| Architettura | Un modello | Modelli separati |
| Coerenza interna | Alta (stesso modello) | Problematica (interfacce) |
| Complessità implementativa | Molto alta (combinatoria) | Alta (accoppiamento) |
| Flessibilità | Massima | Buona |
| Usato in TLC | Parzialmente (in sviluppo 1994) | Sì (CADEM, TAC BRAWLER, RJARS) |

## Applicabilità al Warfare-Model

Il DWM può beneficiare del concetto di variable-resolution per:
- **Gestione campagna**: livello di dettaglio ridotto per settori non attivi
- **Scalabilità**: supportare scenari piccoli (poche unità) e grandi (decine di unità) con lo stesso engine
- **Missioni DCS**: la singola missione è il punto di massima risoluzione (DCS engine); tra le missioni si usa il DWM a risoluzione più bassa

**Implicazione pratica**: non simulare con lo stesso dettaglio un settore inattivo da 3 giorni e il fronte attivo — ottimizzazione computazionale e concettuale.

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 18-22 — generalized network, variable resolution)
