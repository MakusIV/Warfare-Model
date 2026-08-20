---
title: "CADEM — Calibrated Differential Equation Methodology"
type: concept
tags: [ground, attrition, cross-resolution, differential-equations, heterogeneous, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[cross-resolution-modeling]]", "[[janus-model]]", "[[killer-victim-scoreboard]]", "[[stochastic-simulation]]"]
---

# CADEM — Calibrated Differential Equation Methodology

## Definizione

CADEM è la metodologia di calcolo dell'attrito terrestre usata nel TLC. È un approccio **eterogeneo** (non aggrega le forze in un singolo score) basato su equazioni differenziali calibrate su killer-victim scoreboards generati da modelli ad alta risoluzione (principalmente [[janus-model]]).

È un'estensione RAND della metodologia ATCAL (Attrition Calibration) sviluppata dal Center for Army Analysis (CAA).

## Il Problema che CADEM Risolve

I metodi di attrito aggregati (tipo Lanchester con scoring) aggregano tutte le armi in un singolo valore numerico. Questo perde:
- Le relazioni tra tipi di arma (es. chi spara su chi)
- La capacità di valutare trade-off tra sistemi d'arma
- La coerenza quando il mix di forze cambia

CADEM mantiene le relazioni **eterogene** tra tipi di arma, permettendo allocazione dinamica dei fuochi.

## Processo CADEM

```
[Killer-Victim Scoreboards]   (da JANUS o esercitazioni)
         ↓
    [Calibration]             → Parameter Sets (per situazione)
         ↓
    [Extension]               → Extended Param. Sets (per ipotetica sistemi)
         ↓
    [Selection & Adjustment]  ← Situazione TLC corrente (S), Risorse (X), Tempo (t)
         ↓
    [Attrition Matrix A_t(X,S)]
         ↓
    [Augmentation]            ← Resource Dependencies (ammo, logistics)
         ↓
    dX_i = -A_i^Aug * X_i * dt   (sistema di equazioni differenziali)
         ↓
    [Losses as function of time]
```

## Formulazione Matematica

Il sistema di equazioni differenziali ha la forma:

$$dX_i = -A_i^{\text{Aug}} X_i \, dt$$

dove:
- $X_i$ = risorse di tipo $i$ al tempo $t$
- $A_i^{\text{Aug}}(X, S)$ = matrice di attrito aumentata, funzione delle risorse totali $X$ e della situazione $S$
- Il termine "aumentato" include dipendenze da risorse aggiuntive (munizioni, logistica, effetti fratricide)

## Allocazione del Fuoco

CADEM alloca il fuoco di ciascuna parte contro le armi dell'altra **in base al loro contributo all'efficacia combat dell'avversario**. Quando le capacità cambiano:
- Se il sistema 3 riduce il suo tasso di fuoco della metà → meno kills del sistema 1 e 2
- Il sistema 3 diventa meno prioritario come target per i sistemi 1 e 2
- I fuochi si riallocano verso il sistema 4 (ora più letale e quindi target prioritario)

Questo comportamento è **adattivo** e fisicamente motivato.

## Uso Stocastico

CADEM può essere usato in modalità stocastica: gli scoreboards da modelli ad alta risoluzione sono scelti casualmente (Monte Carlo) tra i campioni per la situazione specifica, invece di usare valori medi. Questo propaga l'incertezza del combattimento nell'attrito di campagna.

## Vantaggi vs ATCAL/Scoring

| Aspetto | Scoring (TACWAR) | CADEM |
|---------|-----------------|-------|
| Aggregazione | Sì (singolo score) | No (eterogeneo) |
| Link a modelli alta-res | Indiretto | Diretto (scoreboards) |
| Trade-off tra armi | Non rappresentabile | Rappresentabile |
| Comportamento adattivo | No | Sì (riallocazione fuochi) |
| Costo computazionale | Basso | Moderato (+50% vs ATCAL) |
| Costo dati | Basso | Alto (scoreboards da JANUS) |

## Limitazioni

- Richiede ampi dataset di scoreboards da modelli ad alta risoluzione
- L'estensione per situazioni/sistemi non nell'input richiede giudizio esperto
- Più lento di ATCAL (~50% in più) ma molto più preciso
- Sviluppo dei dati è costoso e dipende dalla cooperazione di altre organizzazioni

## Applicabilità al Warfare-Model

Se il DWM deve simulare perdite terrestri (ground combat tra forze opposte), CADEM è la metodologia di riferimento. In alternativa semplificata: usare direttamente equazioni Lanchester con parametri calibrati su scenari DCS tipici. Il concetto di "killer-victim scoreboard da simulazione ad alta risoluzione" si traduce in: usare risultati di missioni DCS (dati `tactical_evaluation_results.csv`) come input per calibrare modelli di attrito di campagna.
