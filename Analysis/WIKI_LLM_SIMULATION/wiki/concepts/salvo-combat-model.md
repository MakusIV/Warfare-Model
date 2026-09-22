---
title: "Modello a salva (Salvo Combat Model)"
type: concept
tags: [salvo-combat-model, discrete-event, naval, combat-resolution, warfare-model, dwm]
created: 2026-09-22
updated: 2026-09-22
sources: ["[[source-hughes-salvo-event-driven]]"]
related: ["[[wayne-hughes]]", "[[lanchester-models]]", "[[event-driven-simulation]]", "[[virtual-session-engine-des]]", "[[hughes-salvo-vs-engagement-resolver]]"]
---

# Modello a salva (Salvo Combat Model)

## Definizione

Modello di combattimento a **impulsi discreti**: lo scambio non è un flusso continuo di danno
(come nelle equazioni di Lanchester) ma una successione di eventi puntuali — le salve — ciascuno dei
quali altera bruscamente lo stato delle forze. Formulazione base ([[wayne-hughes]], *Fleet Tactics*):

$$\Delta A = -\frac{\beta B - y A}{w}$$

dove $\beta B$ è il volume di fuoco offensivo del lato $B$ (numero di colpi lanciati × probabilità
di colpire), $yA$ è la capacità difensiva del lato $A$ (colpi intercettati prima dell'impatto), e
$w$ è la *staying power* — quanto danno può assorbire un'unità di $A$ prima di perdere efficacia.
Il numeratore è **clampato a 0**: se la difesa assorbe l'intera salva, non c'è danno netto (non
danno negativo). L'effetto è a **cascata**: una salva che riduce la difesa disponibile rende la
salva successiva più efficace.

## Applicazione nel Dominio

Nasce per lo scambio missilistico navale (l'unità di salva è naturale: un cacciatorpediniere lancia
N missili in un lancio, non uno al secondo per un'ora), ma la struttura si generalizza a qualunque
scambio a colpi discreti e capacità di intercettazione finita — difesa aerea puntuale (SHORAD/AAA
contro una formazione CAS), fuoco di controbatteria, qualunque ingaggio molti-contro-molti dove
"quanti colpi arrivano insieme" conta quanto "quanti ne arrivano in totale".

**Il termine strutturale che lo distingue da un conteggio ingenuo** ([[source-hughes-salvo-event-driven]]
§ Contributi 2): $y$/$z$ non è una probabilità per colpo applicata a ciascun proiettile — è una
**capacità di intercettazione per salva**. Sopra quella capacità, il surplus penetra *integralmente*
le difese (saturazione). È un meccanismo qualitativamente diverso da "ogni colpo ha probabilità p di
essere intercettato", ed è ciò che rende un attacco concentrato più efficace di uno diluito nel
tempo a parità di volume totale.

## Vantaggi e Limitazioni

| Aspetto | Dettaglio |
|---|---|
| Vantaggio | Nativamente compatibile con un motore event-driven: una salva **è** un evento |
| Vantaggio | Cattura la saturazione difensiva, che un tasso di attrito continuo non può rappresentare |
| Vantaggio | Compatibile per costruzione con perdite per-asset (ogni salva ha un mittente, un bersaglio, un volume tracciabile) |
| Limitazione | Il modello base è aggregato per lato ($A$, $B$ scalari); l'eterogeneità (più tipi di unità, più tipi di minaccia) richiede vettorializzazione — non parte della formulazione originale |
| Limitazione | Non specifica *quando* una salva viene lanciata né *se* i contendenti si incontrano — quello resta compito dello scheduler dei contatti, non del risolutore d'ingaggio |
| Limitazione | Il payload di una salva è fisicamente fissato all'istante di lancio: un modello che lo ricalcola all'istante d'impatto viola la causalità (v. [[hughes-salvo-vs-engagement-resolver]] § Lacuna A) |

## Relazioni con altri Concetti

- [[lanchester-models]] — famiglia distinta, spesso accostata per errore: ODE continue e aggregate
  contro impulsi discreti. Nessuna sovrapposizione matematica, nessuna fonte Lanchester ingerita
  tratta le salve (verificato in [[lanchester-vs-motore-des]] § 2b)
- [[event-driven-simulation]] — il modello a salva è il caso naturale di risolutore per un motore a
  coda eventi: ogni salva è un evento che il DES può schedulare e ordinare
- [[virtual-session-engine-des]] — **il progetto ha già scelto questo modello** come risolutore del
  molti-contro-molti nello strato 2 (`Logic/Engagement_Resolver.py`, Fase 4, non ancora scritta)

## Applicabilità al Warfare-Model

Valutazione componente per componente in [[hughes-salvo-vs-engagement-resolver]]. In sintesi: il
termine difensivo a capacità-per-salva con saturazione è l'unico pezzo strutturale che il progetto
oggi non ha in nessuna forma (`Logic/Damage_Model.resolve_hit` risolve un colpo alla volta, non una
salva), ed è direttamente costruibile sopra `build_damage_event`/`apply_damage_event` — già separate
proprio per permettere di calcolare tutti gli esiti di una salva, ordinarli deterministicamente, e
applicarli in un solo passo.

## Fonti

- [[source-hughes-salvo-event-driven]] — D1 (esposizione verificata e corretta del modello base)
