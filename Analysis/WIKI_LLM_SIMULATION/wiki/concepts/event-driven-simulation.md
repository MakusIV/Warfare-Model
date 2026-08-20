---
title: "Event-Driven Simulation — Gestione del Tempo nelle Simulazioni di Campagna"
type: concept
tags: [event-driven, time-step, simulation-structure, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[campaign-model]]", "[[stochastic-simulation]]", "[[modsim-ii]]"]
---

# Event-Driven Simulation (Event-Step Method)

## Definizione

Il metodo event-step è un approccio alla gestione del tempo nelle simulazioni in cui il passo temporale successivo è determinato **internamente dalla simulazione** come il tempo del prossimo evento previsto. Si contrappone al metodo time-step in cui i passi sono fissi e determinati esternamente.

## Confronto: Time-Step vs Event-Step

### Time-Step Method
- Il tempo avanza a passi fissi Δt
- Gli eventi nel passo vengono aggregati a fine/inizio intervallo
- **Pro**: semplice, controllo sull'ordine di elaborazione
- **Contro**: step grandi → errori; step piccoli → inefficienza; variable-resolution difficile
- **Usato in**: TACWAR, CEM, JANUS (all'estremità del range)

### Event-Step Method
- Il tempo avanza al prossimo evento previsto
- Ogni evento può schedulare/de-schedulare altri eventi futuri
- **Pro**: efficiente (grandi salti quando nulla accade), preciso, variable-resolution naturale
- **Contro**: richiede previsione del prossimo evento; ordine degli eventi simultanei complesso
- **Usato in**: TLC (con MODSIM II), simulatori moderni

```
Time-Step:
t₀──────t₁──────t₂──────t₃──────t₄──────t₅──
   E₀  E₁,E₂       E₃      E₄    E₅

Event-Step:
t₀─E₀─t₁─E₁──t₂─E₂──────────t₃─E₃──t₄─E₄──t₅─E₅
   (passi piccoli dove ci sono eventi, grandi dove non ce ne sono)
```

## Perché TLC ha Scelto Event-Step

1. **Efficienza**: voli aerei hanno periodi lunghi di inattività (transito) intervallati da eventi brevi (engagements)
2. **Precisione**: rilevamento SAM, intercetto radar, engagements sono eventi puntuali, non aggregabili su step grandi
3. **Variable resolution automatica**: il modello naturalmente usa step piccoli dove necessario
4. **Compatibilità con Monte Carlo**: le stochastic simulation traggono vantaggio dall'event-step

## Il Problema del Prossimo Evento

La sfida principale dell'event-step è predire il prossimo evento. Per il TLC:
- **Rilevamento**: quando un aereo entrerà nella detection region? → calcolo geometrico sul flight path
- **Intercetto**: quando l'intercettore raggiungerà il punto di intercetto? → cinematica
- **Engagement SAM**: quando l'aereo uscirà dalla SAM region? → geometria rete + velocità

La rete generalizzata con event-nodes pre-calcolati semplifica enormemente questo problema: il prossimo evento è semplicemente il prossimo nodo sul path.

## Ordine degli Eventi Simultanei

Nel TLC implementato con MODSIM II, due strategie:
1. **Piccolo offset temporale** tra eventi che devono accadere in ordine
2. **Controllo diretto della coda degli eventi** per eventi schedulati allo stesso tempo

## Applicabilità al Warfare-Model

Il DWM è strutturato come una simulazione con turni di campagna (non event-step puro). Tuttavia, i processi interni (engagement DCS, lancio di missioni) sono naturalmente event-based. La scelta tra time-step e event-step dipende dalla granularità temporale necessaria:

- **Attuale DWM**: turni giornalieri o per-sortita — compatibile con time-step semplificato
- **DWM avanzato**: se si vuole simulare interazioni dinamiche intra-missione, un approccio event-step sarebbe più appropriato

Il concetto di **event node pre-calcolato** è direttamente applicabile alla Route/Waypoint structure del DWM per pre-calcolare i punti critici di interazione lungo i percorsi di missione.
