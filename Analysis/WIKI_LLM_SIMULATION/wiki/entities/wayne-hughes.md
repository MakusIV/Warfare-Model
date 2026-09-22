---
title: "Wayne P. Hughes"
type: entity
tags: [author, naval, salvo-combat-model, warfare-model]
created: 2026-09-22
updated: 2026-09-22
sources: ["[[source-hughes-salvo-event-driven]]"]
related: ["[[salvo-combat-model]]", "[[lanchester-models]]", "[[hughes-salvo-vs-engagement-resolver]]"]
---

## Descrizione

Capitano (poi professore) US Navy, autore di *Fleet Tactics* (1986, poi *Fleet Tactics and Coastal
Combat*, 2000), il testo che introduce il **modello a salva** (salvo combat model) come alternativa
alle equazioni di Lanchester per il combattimento navale con missili guidati. L'attribuzione,
il grado e l'anno sono stati **verificati** in [[source-hughes-salvo-event-driven]] (D1) e risultano
corretti — l'unica affermazione bibliografica solida dell'intero set di documenti ingeriti.

## Caratteristiche Principali

- Osservazione di partenza: nell'era dei missili antinave il combattimento non è un flusso continuo
  di danno (adatto a un'equazione differenziale) ma una successione di **impulsi discreti** — ogni
  salva altera bruscamente lo stato delle forze in campo.
- Formalizza il principio dottrinale *"attack effectively first"*: chi lancia per primo una salva
  efficace ottiene un vantaggio che nessun rapporto di forze medio cattura.
- Il modello base ha tre gruppi di parametri per lato: **offensivi** ($\alpha$, $\beta$ — colpi
  lanciati e probabilità di colpire), **difensivi** ($y$, $z$ — capacità di intercettazione, non
  probabilità per colpo) e di **staying power** ($w$, $x$ — capacità di assorbire danno prima della
  perdita di efficacia).

## Relazioni

- Origina: [[salvo-combat-model]]
- Distinto da: [[lanchester-models]] — famiglia di ODE continue e aggregate; il modello di Hughes è
  a impulsi discreti, nativamente compatibile con un motore event-driven
- Applicato a: [[hughes-salvo-vs-engagement-resolver]] — valutazione per `Logic/Engagement_Resolver.py`

## Fonti

- Esposizione corretta (D1) e sei estensioni non verificate (D2-D7, senza citazioni, con difetti
  aritmetici/logici propri) in [[source-hughes-salvo-event-driven]]

## Note

Il wiki non ha ancora una fonte primaria (*Fleet Tactics* stesso o un articolo accademico che ne
riporti le equazioni con provenienza verificabile) — solo una sessione conversazionale con un
assistente AI che lo espone correttamente in un solo documento su sette. Se si vuole calibrare il
modello con numeri reali, questa fonte non basta: serve il testo originale o un articolo che lo citi
con equazioni e parametri tracciabili.
