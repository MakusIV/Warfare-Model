---
title: "Stochastic Simulation — Simulazione Stocastica nei Warfare Models"
type: concept
tags: [monte-carlo, stochastic, deterministic, attrition, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[cadem]]", "[[campaign-model]]", "[[event-driven-simulation]]"]
---

# Stochastic Simulation nei Warfare Models

## Definizione

Una simulazione stocastica rappresenta i processi casuali usando variabili aleatorie (numeri casuali) invece di sostituire ogni variabile con il suo valore atteso. In un warfare model, questo significa che kills, rilevamenti e outcomes tattici vengono determinati da estrazioni casuali (Bernoulli trials) invece di essere calcolati come medie deterministiche.

## Il Problema della Mean Equivalence

Il nucleo dell'argomento stocastico del documento TLC è la **fallacia dell'equivalenza della media**:

> "The repeatability of a mean value equivalent simulation gives false security that the effects of the variance associated with the stochastic model have been eliminated." (p. 41)

Se una funzione $f$ descrive un processo, allora in generale:
$$E[f(X)] \neq f(E[X])$$

cioè la funzione valutata sulla media NON è uguale al valore atteso della funzione della variabile. La mean equivalence si applica solo se $f$ è **lineare** vicino al valore atteso — raramente vero nei sistemi di combattimento.

## Esempio: Battaglie 3:1 a Terra

Con parametri deterministici, una battaglia 3:1 con σ=0 produce sempre un pareggio (il ratio rimane costante). Con σ=0.7:
- Alcune simulazioni mostrano vittoria schiacciante del rosso (ratio 3.5+)
- Alcune mostrano vittoria del blu (ratio 2.0-)
- La probabilità di pareggio è zero
- **I risultati deterministici e stocastici sono qualitativamente diversi**

## Perché la Simulazione Deterministica Sbaglia

1. **Entità indivisibili**: 0.6 portaerei non esiste. Forze deterministiche trattano entità come flussi divisibili, creando problemi per sistemi di alto valore e bassa numerosità.

2. **Code e congestione**: la varianza dei tempi di servizio contribuisce alla lunghezza media delle code. Un modello deterministico sottostima sistematicamente la congestione.

3. **Processi discreti**: un aereo viene rilevato o non rilevato, non "rilevato al 50%". Un missiletto kill o non killa. La simulazione deterministica impone mean-equivalence su processi intrinsecamente discreti.

4. **Interazioni non-lineari**: il numero di veicoli da riparare è una funzione non-lineare dei colpi ricevuti.

## Approccio Stocastico in TLC

TLC usa:
- **Bernoulli trials** per ogni kill/survival nelle battaglie aria-aria e superficie-aria
- **Monte Carlo** per scelta dei killer-victim scoreboards (CADEM stocastico)
- **Multiple run** per stimare distribuzioni di esiti invece di valori singoli

## Numero di Run Necessarie

Il documento discute la stima del numero di run per una confidenza statistica prefissata. Con modelli di campagna che richiedono ore di CPU per run, questo era tradizionalmente il principale argomento contro la simulazione stocastica. Con le capacità computazionali moderne, questo problema è molto ridimensionato.

## Applicabilità al Warfare-Model

Il DWM usa già `tactical_evaluation_results.csv` che contiene dati di outcome tattico — probabilmente già stocastici (risultati di missioni DCS individuali). Il valore aggiunto di un approccio Monte Carlo esplicito nel DWM:

1. **Valutazione dell'incertezza**: invece di un singolo outcome di campagna, produrre una distribuzione di possibili esiti
2. **Analisi di sensitività**: quanto è robusto un piano di campagna alle variazioni casuali degli esiti tattici?
3. **C² e adattività**: le strategie adattive (SAGE-like) hanno più valore in contesti stocastici dove reagire all'informazione è essenziale

**Nota**: il `tactical_evaluation_results.ods` in `Analysis/` suggerisce che già si fa analisi degli esiti — potrebbe essere un punto di partenza per formalizzare l'approccio stocastico.
