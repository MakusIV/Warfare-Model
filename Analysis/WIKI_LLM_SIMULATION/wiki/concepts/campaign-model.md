---
title: "Campaign Model — Modello di Campagna Militare"
type: concept
tags: [campaign-model, joint, theater-level, defense-analysis]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[generalized-network]]", "[[cross-resolution-modeling]]", "[[sage-algorithm]]"]
---

# Campaign Model — Modello di Campagna Militare

## Definizione

Un modello di campagna (detto anche "theater model") rappresenta un insieme di missioni, operazioni o battaglie nell'ambito di un obiettivo di campagna militare. Copre il livello operativo/teatro, che include le azioni congiunte di forze aeree, terrestri e navali.

> "The campaign model shows the big picture in terms of the total forces involved, including the joint actions of army, air, and naval forces, as well as the play of coalition forces." (Hillestad & Moore, p. 3-4)

## Tassonomia dei Modelli di Difesa

Dal livello più basso al più alto:

| Livello | Scope | Esempi |
|---------|-------|--------|
| **Engineering/System** | Singolo sottosistema (es. radar) | Modelli di sistemi d'arma |
| **Engagement** | Singolo engagement (es. SAM vs aereo) | EADSIM, TAC BRAWLER |
| **Mission** | Missione completa (decollo → attacco → ritorno) | TAC THUNDER (parziale) |
| **Campaign** | Campagna completa, forze congiunte, settimane/mesi | **TLC**, TACWAR, CEM, JICM |
| **Global** | Conflitti multi-teatro | JICM |

## Perché il Livello Campagna è Fondamentale

A livello di campagna si possono rispondere domande che i livelli inferiori non possono:
- "Quante forze sono sufficienti?" (force structure)
- Trade-off aria/terra/mare
- Effetti cumulativi nel tempo (non solo singole battaglie)
- Logistics e deployment
- Sinergie joint e combined arms
- Impatto dei sistemi C⁴I sull'esito della campagna

## Caratteristiche di un Campaign Model Post-Guerra Fredda

Dall'analisi TLC, un modello di campagna moderno deve:
1. **Rappresentare il combattimento non-lineare** (manovre, accerchiamento, profondità)
2. **Essere flessibile per nuovi scenari** (non solo Europa centrale)
3. **Supportare variable-resolution** (analisi rapide + analisi dettagliate)
4. **Modellare C⁴I esplicitamente** (non assumere informazione perfetta)
5. **Usare simulazione adattiva** (non script fissi di decisione)
6. **Collegarsi a modelli ad alta risoluzione** (cross-resolution modeling)

## Misure di Esito (MOE/MOP) Tipiche

- Territorio perso/guadagnato
- Raggiungimento della superiorità aerea
- Attrito complessivo nella campagna
- Rapporto di forza finale
- Distruzione di obiettivi strategici

## Relazioni con altri Concetti

- [[generalized-network]] — struttura game board del campaign model
- [[cross-resolution-modeling]] — collegamento con modelli a risoluzione superiore
- [[event-driven-simulation]] — metodo di avanzamento del tempo
- [[stochastic-simulation]] — trattamento dei processi casuali
- [[cadem]] — metodologia di attrito terrestre per campaign models
- [[sage-algorithm]] — allocazione adattiva delle risorse nel campaign model
- [[nonlinear-combat]] — fenomeni da rappresentare nel campaign model post-GF

## Applicabilità al Warfare-Model

Il Warfare-Model DWM è un campaign model specializzato per missioni DCS. La tassonomia TLC si applica direttamente: DWM opera al livello "campaign", usando dati di engagement (sortite DCS) per gestire l'evoluzione della campagna a livello di sessione multi-giorno.
