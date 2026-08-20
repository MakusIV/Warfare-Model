---
title: "Wargaming — Gioco di Guerra come Strumento di Analisi"
type: concept
tags: [wargame, simulation, historical, training, academic, manual-simulation]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-simulation-techniques-past-conflicts]]", "[[source-theater-level-campaign-model]]"]
related: ["[[campaign-model]]", "[[comparative-dynamic-modelling]]", "[[historical-conflict-simulation]]", "[[anti-hindsight]]", "[[philip-sabin]]", "[[tlc-model]]"]
---

# Wargaming

## Definizione

Il wargaming è la simulazione di un conflitto militare come "contesa dialettica tra volontà opposte" (Clausewitz). Si distingue dalla simulazione computazionale pura per la presenza di **giocatori umani** che prendono decisioni, introducendo le dimensioni di agency, incertezza e interazione strategica.

> "War and games are both dialectical strategic contests between opposing wills, each struggling to prevail." (Sabin, 2008)

> "Clausewitz said that 'In the whole range of human activities, war most closely resembles a game of cards'."

## Tipologie

### Per Supporto
| Tipo | Caratteristiche | Esempi |
|------|----------------|--------|
| **Manuale** | Mappa, contatori, dado — nessun computer | Wargames commerciali, simulazioni Sabin |
| **Semi-computerizzato** | Computer per calcoli, decisioni umane | Maggior parte dei wargame moderni |
| **Computerizzato** | Tutto automatizzato; eventuale human-in-the-loop | TLC, TACWAR, DCS |

### Per Scopo
| Scopo | Caratteristiche |
|-------|----------------|
| **Addestramento** | Sviluppare abilità decisionali in contesti operativi |
| **Pianificazione** | Esplorare opzioni e conseguenze prima di operazioni reali |
| **Analisi** | Valutare forze, dottrine, equipaggiamenti (uso RAND/DoD) |
| **Ricerca storica** | Risolvere controversie, comprendere dinamiche (Sabin) |
| **Didattica** | Insegnamento di storia militare e strategia |

## Tre Ruoli delle Simulazioni (Sabin)

Sabin identifica tre funzioni fondamentali che simulazioni e wargame svolgono rispetto ai metodi tradizionali:

1. **Coinvolgimento**: gli utenti partecipano attivamente invece di assorbire passivamente contenuti scritti/video
2. **Anti-hindsight**: riducono il "problema della conoscenza retrospettiva" — rendono di nuovo incerto ciò che sappiamo essere accaduto, ricordando la natura contingente degli eventi
3. **Comprensione sistemica**: richiedono una comprensione logica, comprensiva e ampia del "cosa e perché" — evidenziano domande neglette e forniscono basi per analisi comparativa

## Il Problema dell'Hindsight Bias

Il **hindsight bias** (pregiudizio retrospettivo) è la tendenza a ritenere gli eventi storici più prevedibili di quanto fossero al momento. Le simulazioni combattono questo bias perché:
- L'esito non è noto a priori al giocatore
- Le stesse condizioni iniziali possono portare a esiti diversi
- La contingenza degli eventi diventa tangibile

Questo si lega direttamente all'argomento stocastico di TLC ([[stochastic-simulation]]): anche in una simulazione operativa, presentare esiti certi (deterministici) rimuove informazione critica sulla distribuzione dei possibili esiti.

## Sfide nell'Uso Accademico

1. **Accuratezza vs drammaticità**: i wargame commerciali spesso sacrificano l'accuratezza per l'appeal
2. **Problema di immagine**: percepiti come non-accademici rispetto a game theory e modelli matematici
3. **Logistica**: difficile provision bibliotecaria e utilizzo in aula rispetto a libri/video

## Relazione con Campaign Models Computerizzati

I wargame manuali e i campaign models computerizzati (TLC, TACWAR) risolvono lo stesso problema da angoli diversi:

| Aspetto | Wargame Manuale (Sabin) | Campaign Model Computerizzato (TLC) |
|---------|------------------------|--------------------------------------|
| Decisori | Umani (giocatori) | Algoritmi (SAGE, scripts, C²) |
| Velocità | Lenta (ore/giorni per partita) | Veloce (secondi/minuti per run) |
| Fedeltà | Moderata (abstrazione necessaria) | Alta (dati alta risoluzione) |
| Scopo | Comprensione, formazione | Analisi di policy, pianificazione |
| Incertezza | Intrinseca (dado, decisioni umane) | Esplicita (Monte Carlo) |

## Applicabilità al Warfare-Model

Il DWM è fondamentalmente un "wargame computerizzato" per campagne DCS. I tre ruoli di Sabin si applicano:
1. **Coinvolgimento**: i giocatori DCS partecipano attivamente — il DWM gestisce la coerenza della campagna
2. **Anti-hindsight**: gli esiti delle missioni DCS dovrebbero influenzare la campagna in modo stocastico (non deterministico) per mantenere l'incertezza
3. **Comprensione sistemica**: il DWM richiede e genera una comprensione delle dinamiche di campagna aerea

La "dialettica tra volontà opposte" di Clausewitz è il fondamento del modulo di decisione avversaria del DWM — vedi [[sage-algorithm]] per come SAGE gestisce questa dialettica in modo algoritmico.
