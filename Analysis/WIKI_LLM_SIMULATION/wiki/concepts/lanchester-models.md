---
title: "Modelli Lanchester — famiglia, varianti e stato di validazione"
type: concept
tags: [lanchester, attrition, differential-equations, combat-simulation, historical, warfare-model]
created: 2026-09-22
updated: 2026-09-22
sources: ["[[source-lanchester-scenari-ai]]", "[[source-theater-level-campaign-model]]"]
related: ["[[cadem]]", "[[killer-victim-scoreboard]]", "[[nonlinear-combat]]", "[[stochastic-simulation]]", "[[event-driven-simulation]]", "[[virtual-session-engine-des]]", "[[lanchester-vs-motore-des]]"]
---

# Modelli Lanchester

## Definizione

Con **modelli Lanchester** si indica la famiglia di modelli di attrito in cui le perdite di ciascun
contendente sono descritte da un sistema di equazioni differenziali ordinarie nelle sole
*numerosità* delle forze, con coefficienti di letalità costanti o parametrici. Sono **aggregati**
(la forza è un numero, non un insieme di entità), **continui** (le perdite sono reali, non intere)
e nella formulazione classica **deterministici**.

Le due forme originali (F. W. Lanchester, 1916):

| Legge | Equazioni | Ipotesi fisica | Invariante |
|---|---|---|---|
| **Lineare** | $\dot{R} = -g\,R\,G$, $\dot{G} = -r\,R\,G$ | fuoco d'area / non mirato: si colpisce un'area, non un bersaglio | $rR - gG$ |
| **Quadratica** | $\dot{R} = -g\,G$, $\dot{G} = -r\,R$ | fuoco mirato: ogni tiratore ingaggia un bersaglio individuato | $rR^2 - gG^2$ |

La legge quadratica è l'origine della nozione di "massa che conta al quadrato": raddoppiare il
numero di tiratori quadruplica l'effetto netto. È anche l'origine della regola pratica 3:1.

## Varianti documentate

### Forma generalizzata di Bracken

$$\frac{dR}{dt} = -g\,R^{q}G^{p} \qquad \frac{dG}{dt} = -r\,R^{p}G^{q}$$

Gli esponenti $p,q$ interpolano fra le due leggi classiche: $(p,q)=(1,0)$ dà la quadratica,
$(1,1)$ la lineare. Secondo [[source-lanchester-scenari-ai]] il fit su Ardenne (1944) e Kursk
(1943) dà $p \approx q \approx 0{,}5$ — **una via di mezzo, cioè: nessuna delle due leggi classiche
tiene su quei dati**. Si veda la § Stato di validazione: è un fit a posteriori su una singola
battaglia con due parametri liberi, non una validazione predittiva.

### Legge a potenza frazionaria "1.5" (Battaglia d'Inghilterra)

Esponente intermedio usato per i duelli aerei del 1940, dove la superiorità numerica conta ma è
mitigata dalla reattività della difesa radar. La fonte è internamente incoerente (dichiara 1.5 e
scrive $\Delta B \sim G^{1.2}$) e un'altra parte della stessa fonte la definisce superata.

### Modelli eterogenei (vettoriali)

La forza è un vettore di categorie d'arma e l'attrito è governato da una **matrice di letalità
incrociata**:

$$\frac{d\vec{R}}{dt} = -\mathbf{M}_{G \to R}\,\vec{G}
\qquad\text{es.}\qquad
\frac{dC_R}{dt} = -\big(\alpha_{F\to C}F_B + \alpha_{C\to C}C_B + \alpha_{A\to C}A_B + \alpha_{D\to C}D_B\big)$$

È la famiglia realmente usata nei modelli di campagna: [[cadem]] è la sua versione *calibrata* —
stessa struttura matematica, ma i coefficienti $\alpha$ provengono da
[[killer-victim-scoreboard]] generati da modelli ad alta risoluzione ([[janus-model]]) invece che
dal giudizio dell'analista. **La differenza fra un modello eterogeneo e CADEM non è la matematica:
è la provenienza dei coefficienti.**

### Modelli a soglia (Helmbold)

Introducono il rapporto di forze e la **postura** (difesa fortificata vs attacco affrettato) e,
soprattutto, una **regola di arresto**: quando una forza scende sotto una frazione critica
dell'organico iniziale, l'equazione di attrito si interrompe e si passa alla ritirata. È l'unico
elemento della famiglia che non è un'equazione differenziale ma una *regola di transizione di
stato*, ed è per questo l'unico direttamente trapiantabile in un motore a eventi discreti.

### Modelli logaritmici (Peterson)

Attrito **non** da combattimento — malattie, diserzioni, logoramento psicologico da prontezza
prolungata, ambiente NBC. Ortogonale ai precedenti: si somma, non sostituisce.

### Fattore di superiorità informativa

Variante che moltiplica i coefficienti di efficacia $g, r$ per un fattore C2 $\mu$: chi possiede
superiorità informativa (ISR, satelliti, droni) tira col fuoco *mirato* (legge quadratica), chi ne
è privato ricade sul fuoco *d'area* (legge lineare). È un modo aggregato di rappresentare ciò che
un modello a entità ottiene per costruzione dalla probabilità di detezione.

### SINDy — identificazione dell'equazione dai dati

**Sparse Identification of Nonlinear Dynamics**: invece di postulare l'equazione e verificarne il
fit, si parte dalle serie temporali delle perdite e si ricerca la combinazione *più sparsa* di
termini candidati che le riproduce. Applicato ai dati open-source del conflitto russo-ucraino
avrebbe mostrato che la guerra non segue un'unica legge ma si comporta da **sistema a commutazione
di fase** (*switched system*): fasi di movimento con firma quadratica, fasi di logoramento statico
con firma lineare/frazionaria, con commutazioni legate a disponibilità di munizioni, guerra
elettronica e stagione.

Per il Warfare-Model SINDy è interessante **non** come modello di attrito ma come **metodo di
stima**: è un candidato concreto per l'"ATCAL interno" previsto da [[virtual-session-engine-des]]
(far girare offline il risolutore fine e ricavarne i coefficienti aggregati), perché ricava la
forma funzionale oltre ai coefficienti.

## Stato di validazione

Questo è il punto discriminante, e va tenuto separato dall'eleganza matematica della famiglia.

| Evidenza | Esito |
|---|---|
| Test delle leggi classiche su Ardenne e Kursk | **9 test falliti** (bibliografia di [[virtual-session-engine-des]]) |
| Regola 3:1 in versione RAND usata da [[jicm-model]], su 98 ingaggi storici | **19% di successo** — peggio del caso |
| Fit della forma di Bracken su Ardenne/Kursk | $p \approx q \approx 0{,}5$: *conferma* che né lineare né quadratica tengono |
| Database KDB (Dupuy Institute) | Le equazioni "funzionano" solo restringendosi alle *contact forces*, escluse le riserve |

Le quattro righe raccontano la stessa storia: **la famiglia si adatta ai dati a posteriori,
aggiungendo parametri liberi, ma non predice**. Un fit riuscito con due esponenti liberi su una
battaglia non è un test; un test è prevedere la battaglia successiva.

## Vantaggi e Limitazioni

| Aspetto | Dettaglio |
|---|---|
| Vantaggio | Costo computazionale trascurabile: chiuso in forma o poche integrazioni |
| Vantaggio | Poche variabili di stato, quindi leggibile e analizzabile analiticamente |
| Vantaggio | La forma eterogenea consente trade-off fra sistemi d'arma (cuore di [[cadem]]) |
| Limitazione | **Aggregato**: la forza è un numero, le perdite sono frazionarie — nessuna identità per-asset |
| Limitazione | **Non dice mai *quando* e *se* le forze si incontrano**: il contatto è un'ipotesi in ingresso |
| Limitazione | Nessuna nozione di chi spara per primo (detezione, latenza di reazione, portata) |
| Limitazione | Coefficienti senza provenienza fisica, salvo calibrazione esterna ([[cadem]]/ATCAL) |
| Limitazione | Deterministico: nessuna varianza, mentre l'esito reale è stocastico ([[stochastic-simulation]]) |
| Limitazione | Validazione storica negativa (v. sopra) |

## Relazioni con altri Concetti

- [[cadem]] — la versione calibrata della forma eterogenea; **il modo corretto** di usare questa famiglia
- [[killer-victim-scoreboard]] — la sorgente di coefficienti che rende legittima una calibrazione
- [[event-driven-simulation]] — la famiglia alternativa adottata dal progetto; risolve ciò che
  Lanchester per costruzione non tocca (quando avviene il contatto, chi spara per primo)
- **Modello a salva di Hughes** — spesso accostato a Lanchester ma è una **famiglia distinta**: è
  un modello a *impulsi discreti* (salve di missili con potenza offensiva, difensiva e capacità di
  assorbimento), non un sistema di ODE continue, e nasce per lo scambio navale molti-contro-molti.
  È il risolutore previsto dallo strato 2 di [[virtual-session-engine-des]]. Nessuna delle fonti
  Lanchester finora ingerite lo tratta: **resta una lacuna del wiki**.

## Applicabilità al Warfare-Model

Posizione del progetto, stabilita in [[virtual-session-engine-des]] e **non modificata** da questa
pagina:

1. Il risolutore primario del motore di sessioni virtuali **non** è Lanchester: è event-driven per
   singolo colpo, con $P_k = \text{accuracy} \times \text{destroy\_capacity}$ scomposta in
   $P_h \times P_{k|h}$ (`Logic/Damage_Model.py`) e modello a salva di Hughes per il
   molti-contro-molti.
2. `Logic/Tactical_Evaluation.calcFightResult` — modello a rapporto di forze con coefficienti
   tabellati a mano, appartenente a questa famiglia — resta un **fallback aggregato**, mai il
   risolutore primario.
3. Se servirà un livello aggregato, i suoi coefficienti vanno stimati con un **ATCAL interno**
   (risolutore fine offline → coefficienti), mai presi da tabelle non validate.

L'unico elemento della famiglia con applicabilità diretta e immediata è la **regola di soglia alla
Helmbold**, perché non è un'equazione ma un criterio di arresto — e un motore a eventi discreti ha
comunque bisogno di sapere quando un ingaggio finisce senza annientamento. Proposta concreta in
[[soglie-disingaggio-e-attrito-aggregato]].

## Fonti

- [[source-lanchester-scenari-ai]] — mappa delle varianti (doc 04, 09); **citazioni non
  verificabili**, i nomi vanno trattati come piste bibliografiche da confermare
- [[source-theater-level-campaign-model]] — CADEM come superamento dei metodi aggregati tipo
  Lanchester con scoring (pp. relative a [[cadem]])
- `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` — bibliografia con i
  dati di validazione negativa (9 test Ardenne/Kursk, 19% su 98 ingaggi)

## Note

**Lacuna da colmare**: nessuna fonte primaria di questa famiglia è ancora nel wiki. Servono, in
ordine di utilità: (a) Bracken sulla calibrazione Ardenne/Kursk; (b) Lawrence / Dupuy Institute sul
KDB e sui test falliti; (c) Hughes, *Fleet Tactics*, per le salvo equations — che è la famiglia
effettivamente adottata dal progetto e su cui il wiki non ha **nulla**.
