---
title: "Soglie di disingaggio e forma del fallback aggregato"
type: decision
tags: [architecture, dwm, combat-resolution, discrete-event, lanchester, attrition]
created: 2026-09-22
updated: 2026-09-22
status: proposed
affects: ["[[logic-decision]]", "[[block]]"]
related: ["[[virtual-session-engine-des]]", "[[lanchester-models]]", "[[lanchester-vs-motore-des]]", "[[cadem]]"]
---

> **`status: proposed`** — questa pagina è una **raccomandazione**, non una decisione presa. Nessuna
> riga di codice è stata scritta o modificata. La decisione spetta all'utente; finché non è
> accettata, il comportamento vigente resta quello descritto in [[virtual-session-engine-des]].

## Contesto

L'ingestione di [[source-lanchester-scenari-ai]] (9 documenti, valutati in
[[lanchester-vs-motore-des]]) ha dato esito **in larga parte negativo**: nessuna evidenza nuova a
favore dei modelli Lanchester, nessun coefficiente utilizzabile, nessuna sovrapposizione con le
equazioni a salva di Hughes previste per lo strato 2. L'architettura di
[[virtual-session-engine-des]] non è messa in discussione e lo strato 1 (Fase 3) non è toccato.

Restano però **due punti concreti** emersi dalla lettura, che non dipendono dalla validità dei
modelli Lanchester e che vale la pena decidere esplicitamente invece di lasciarli impliciti.

## Decisione proposta

### P1 — Soglia di disingaggio come esito di ingaggio di prima classe

Ogni scenario dei documenti definisce una regola del tipo «A interrompe l'attacco se scende sotto i
70 carri o sotto i 12 velivoli CAS». Non è matematica Lanchester: è una **regola di transizione di
stato**, attribuita in letteratura al modello di Helmbold, e come tale è **ortogonale al
risolutore** — funziona identica sopra un DES a eventi.

Il motore oggi non ha nulla del genere. `Engagement_Resolver` (Fase 4, non ancora scritto) ha
bisogno di un criterio di fine ingaggio diverso dall'annientamento, altrimenti ogni contatto
risolve fino allo sterminio di una delle due parti — esito irrealistico e, peggio, che distorce
tutta la campagna a valle.

Proposta concreta:

- una **soglia per lato e per ingaggio**, espressa come frazione dell'organico impegnato e/o come
  conteggio minimo di una categoria critica, valutata dopo ogni evento di perdita;
- al superamento, l'ingaggio termina con esito **`DISENGAGED`** distinto da `DESTROYED`, e la forza
  che si disingaggia rientra nello scheduler dei contatti con una nuova rotta (non sparisce);
- il valore di soglia **non** va inventato: appartiene alla dottrina, quindi a `Context/Doctrine.py`
  o al livello C2 di [[c2-hierarchy-design]], dove è un parametro dichiarato del lato, non una
  costante nel risolutore;
- `SessionOutcome` deve poter esprimere l'esito, altrimenti l'informazione si perde al confine di
  [[core-simulator-agnostic]].

**Perché serve una decisione dell'utente e non un'implementazione diretta**: dove vive la soglia
(dottrina vs C2 vs profilo d'asset) e se il disingaggio sia deciso per forza o per singolo asset
sono scelte di modello, non dettagli.

### P2 — Se il fallback aggregato verrà rifatto, la forma è la matrice eterogenea

`Logic/Tactical_Evaluation.calcFightResult` resta, come già deciso, un **fallback aggregato mai
primario**. Questa proposta **non** ne chiede la riscrittura: fissa solo il bersaglio, *se e quando*
la riscrittura avverrà, così che la decisione non venga presa di fretta dentro la Fase 4.

Stato attuale verificato nel codice: la funzione è **omogenea** — prende `n_fr`, `n_en` e due
efficienze scalari — interpola una tabella `k_ratio` di quattro righe di coefficienti scelti a mano
(`[4, 10, 0.2]`, `[3, 1.9, 0.5]`, `[2, 1.5, 0.66]`, `[1, 1, 1]`) e restituisce un rapporto di danno,
estraendo da `random.uniform` del `random` di modulo — **non seedato**, precondizione bloccante già
nell'elenco di [[virtual-session-engine-des]].

Bersaglio proposto:

1. **forma eterogenea a matrice di letalità incrociata** ([[cadem]], già documentata in wiki), non
   un rapporto di forze scalare — il progetto ha già accanto la funzione eterogenea giusta su cui
   innestarla, `evaluateCombatSuperiority(action, asset_fr, asset_en)`, che ragiona per categoria e
   combat power;
2. **coefficienti esclusivamente da ATCAL interno** — il risolutore fine della Fase 4 fatto girare
   offline produce i killer-victim scoreboard ([[killer-victim-scoreboard]]), da cui si stimano i
   coefficienti. Mai tabelle a mano, mai numeri da fonti non validate, e in particolare **nessun
   coefficiente di [[source-lanchester-scenari-ai]]**;
3. **RNG iniettato**, mai `random` di modulo, coerentemente con il contratto della Fase 0 e con la
   scelta già fatta in `Damage_Model.resolve_hit` (che riceve `draw` dal chiamante).

Come metodo di stima, **SINDy** è un candidato da tenere presente perché ricava la forma funzionale
oltre ai coefficienti (v. [[lanchester-models]] § SINDy) — ma è una nota, non parte della proposta.

### P3 — Batteria di scenari di validazione (S1-S5)

Le cinque strutture di scenario dei documenti (combined arms con CAS; SEAD preliminare che sottrae
assetti alla missione principale; aereo asimmetrico stealth vs massa; SAM come terza componente;
interdizione profonda contro difesa a 3 strati e bersaglio composito) sono adottate come **casi di
test** per la Fase 7, **senza** i loro numeri: si prende la composizione delle forze e la domanda
che lo scenario pone, non i coefficienti né gli esiti. Dettaglio in
[[lanchester-vs-motore-des]] § 2(c).

## Motivazione

P1 è l'unico elemento della famiglia Lanchester direttamente trapiantabile in un motore a eventi,
proprio perché non è un'equazione. Ed è un buco reale: senza criterio di disingaggio il DES della
Fase 4 produce solo esiti di annientamento.

P2 non cambia nulla oggi e costa nulla: mette per iscritto il bersaglio prima che la Fase 4 obblighi
a improvvisare. Fissa anche il confine importante — è legittimo prendere dai documenti la *forma*
(che è pubblica e nota da decenni), mai i *numeri* (che sono inventati).

P3 dà alla Fase 7 casi di test costruiti su composizioni di forze plausibili e non auto-generati dal
progetto stesso, il che ha valore indipendentemente dalla matematica con cui sono stati risolti.

## Conseguenze

**Se accettata**:

- `Logic/Engagement_Resolver.py` (Fase 4) nasce con un criterio di terminazione a soglia, e
  `SessionOutcome` con un esito `DISENGAGED`;
- la soglia diventa un parametro dottrinale dichiarato, con impatto su `Context/Doctrine.py` e/o sul
  livello C2 di [[c2-hierarchy-design]];
- nessun impatto immediato su `calcFightResult`, che resta com'è;
- gli scenari S1-S5 entrano nel piano di validazione della Fase 7.

**Se respinta**: nulla cambia; [[lanchester-vs-motore-des]] resta come analisi archiviata e questa
pagina va marcata `status: superseded` o rimossa.

**Esplicitamente fuori perimetro**: lo strato 1 (scheduler dei contatti, Fase 3) — verificato riga
per riga che nulla in questa fonte lo tocca.

## Punti aperti da confermare con l'utente

1. Dove vive la soglia di disingaggio: dottrina di lato, direttiva C2 per-sessione, o profilo
   d'asset?
2. Il disingaggio è deciso per **forza** (tutta l'unità rompe il contatto) o per **singolo asset**,
   coerentemente con il vincolo «perdite per singolo asset»?
3. `calcFightResult` va lasciato intatto fino a dopo la Fase 4 (raccomandato), o va toccato prima?
4. Gli scenari S1-S5 entrano nella Fase 7, o servono anche come test di integrazione anticipati
   della Fase 4?

## Fonti

- [[lanchester-vs-motore-des]] — analisi che origina questa proposta
- [[source-lanchester-scenari-ai]] — fonte ingerita
- [[virtual-session-engine-des]] — architettura e vincoli entro cui la proposta deve stare
- `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:251` — stato attuale di
  `calcFightResult`, verificato
