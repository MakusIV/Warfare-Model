---
title: "Soglie di disingaggio e forma del fallback aggregato"
type: decision
tags: [architecture, dwm, combat-resolution, discrete-event, lanchester, attrition]
created: 2026-09-22
updated: 2026-09-23
status: accepted
affects: ["[[logic-decision]]", "[[block]]"]
related: ["[[virtual-session-engine-des]]", "[[lanchester-models]]", "[[lanchester-vs-motore-des]]", "[[cadem]]"]
---

> **`status: accepted`** (2026-09-23) — **P1 e P3 accettate dall'utente**; P2 resta una nota di
> orientamento, senza azione richiesta. Risposte ai punti aperti: la soglia (sia erosione P1 sia
> shock, v. [[risolutore-ingaggio-salva-fase4]] R2) vive in `Context/Doctrine.py` come parametro
> dottrinale di lato; il disingaggio è deciso **per forza intera**, non per singolo asset;
> `calcFightResult` resta intatto fino a dopo la Fase 4; gli scenari S1-S11 (S6-S11 inclusi,
> confermati come batteria ufficiale) entrano **solo nella Fase 7**, nessun test anticipato in
> Fase 4. **Implementazione COMPLETATA 2026-09-23**:
> `Context/Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS` (erosion 0.30, shock 0.20, stessi valori per
> i 3 lati, dichiarati come stima di partenza non validata) + `Logic/Engagement_Resolver._check_doctrine`,
> esito `DISENGAGED` per forza intera distinto da `DESTROYED`. V. [[virtual-session-engine-des]].

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

### P3 — Batteria di scenari di validazione (S1-S11)

Le cinque strutture di scenario dei documenti (S1 combined arms con CAS; S2 SEAD preliminare che
sottrae assetti alla missione principale; S3 aereo asimmetrico stealth vs massa; S4 SAM come terza
componente; S5 interdizione profonda contro difesa a 3 strati e bersaglio composito) sono adottate
come **casi di test** per la Fase 7, **senza** i loro numeri: si prende la composizione delle forze
e la domanda che lo scenario pone, non i coefficienti né gli esiti. Dettaglio in
[[lanchester-vs-motore-des]] § 2(c).

**S1-S5 coprono solo il dominio terra/aria a due parti, ingaggio singolo, forze già in contatto.**
Non toccano affatto: il dominio navale, i bersagli economici/logistici (il caso più comune di
targeting non-militare nel progetto), la scala (il limite superiore dichiarato di 10.000 asset),
il fog-of-war, la soglia di disingaggio proposta in P1 (nessuno scenario la esercita, perché nessun
documento sorgente la implementava), e il confine sessione-DCS/sessione-sintetica che è il punto
centrale di [[core-simulator-agnostic]]. **S6-S11 colmano queste lacune**, definiti per questo
progetto (non derivati dai documenti Lanchester) proprio per esercitare i meccanismi che S1-S5 non
toccano — ciascuno mirato a un componente specifico del motore, non a una situazione tattica
generica:

- **S6 — gruppo da battaglia navale contro difesa costiera.** Portaerei/incrociatore/cacciatorpediniere
  in attacco contro un litorale con SAM costieri + batterie AAA + unità navali di superficie
  leggere. Esercita `Ship.set_combat_power`/`air_defense_power` sul lato mare (mai testati insieme
  in S1-S5, che sono tutti terra/aria), e la fusione delle finestre di contatto di
  `Contact_Scheduler` quando le minacce sono sia a terra (costiere) sia in mare.
- **S7 — interdizione di una linea logistica.** Attacco aereo contro blocchi `Production`/
  `Storage`/`Transport` (non `Military`) lungo una rotta di rifornimento, con scorta di caccia a
  protezione del convoglio. Esercita il ramo bersaglio-logistico di
  `Tactical_Evaluation.calculate_priority` (quello che usa `target_priority` invece di
  `combat_power_ratio`) e il calcolo di produzione/warehouse di `Region` — nessuno scenario S1-S5
  ha un bersaglio non-militare.
- **S8 — fronte multiplo, stress di scala.** Decine di blocchi su più regioni con ingaggi
  simultanei, dimensionato per avvicinarsi (non raggiungere) il limite superiore dichiarato di
  10.000 asset. Verifica che la potatura gerarchica a livello Block (meccanismo C di
  `Contact_Scheduler`) scarti davvero la maggioranza delle coppie prima del calcolo CPA/TCPA per
  singolo asset — è l'unico scenario pensato per misurare tempo di calcolo, non correttezza
  tattica.
- **S9 — targeting sotto fog-of-war parziale.** Stessa composizione di forze di S1, ma con
  ricognizione incompleta (`recon_cp_snapshot` non vuoto ma parziale) invece di ground-truth.
  Verifica che la policy "non visto → priorità bassa" (v. `feedback_no_visibility_low_priority`)
  interagisca correttamente con `detection_range`/`Contact_Scheduler`: un bersaglio rilevato
  geometricamente (nel raggio di un sensore) ma non ancora ricognito dal lato C2 deve restare a
  priorità bassa finché lo snapshot non lo conferma — due nozioni di "visibilità" diverse
  (geometrica vs. informativa) che oggi nessun test mette in tensione tra loro.
- **S10 — regressione mirata sulla soglia di disingaggio.** Scenario minimo, costruito apposta
  (non un caso tattico realistico): una forza subisce perdite fino a superare la soglia proposta in
  P1 a metà di un ingaggio già in corso. Verifica che l'esito sia `DISENGAGED` (con la forza
  superstite che rientra nello scheduler dei contatti su una nuova rotta) e non l'annientamento
  implicito che il motore produce oggi in assenza di P1. Se P1 non viene accettata, questo scenario
  va rimosso o riscritto per verificare esplicitamente che l'annientamento è il comportamento
  voluto.
- **S11 — confine sessione DCS/sessione sintetica.** Un ingaggio inizia dentro una sessione
  sintetica (nessun giocatore) e la forza superstite deve comparire, con lo stato corretto
  (perdite, munizioni, posizione), nella sessione DCS successiva. Non è un test di combattimento:
  è il test end-to-end del contratto `SessionOrder`/`SessionOutcome` (v.
  [[core-simulator-agnostic]]) e dell'unico vincolo esplicitamente citato per la Fase 7 nella
  roadmap originale ("test di agnosticismo": cancellando l'adapter DCS la campagna deve continuare
  a girare). Nessuno degli scenari S1-S9 tocca il confine fra i due tipi di sessione.

**Tutti gli 11 scenari** condividono la stessa regola di P3 originale: si prende la composizione
delle forze e la domanda che pongono, mai coefficienti o esiti numerici precalcolati — per S6-S11
la domanda è "il meccanismo X del motore si comporta correttamente", non un risultato storico o
di dominio da riprodurre.

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
- gli scenari S1-S11 (S1-S5 dai documenti, S6-S11 definiti per colmare le lacune di dominio/
  meccanismo che S1-S5 non coprono, v. P3) entrano nel piano di validazione della Fase 7; S10 in
  particolare è il test di non-regressione di questa stessa decisione.

**Se respinta**: nulla cambia; [[lanchester-vs-motore-des]] resta come analisi archiviata e questa
pagina va marcata `status: superseded` o rimossa.

**Esplicitamente fuori perimetro**: lo strato 1 (scheduler dei contatti, Fase 3) — verificato riga
per riga che nulla in questa fonte lo tocca.

## Punti aperti — RISOLTI dall'utente 2026-09-23

1. ~~Dove vive la soglia di disingaggio~~ → **dottrina di lato** (`Context/Doctrine.py`).
2. ~~Per forza o per singolo asset~~ → **per forza intera**.
3. ~~`calcFightResult` toccato prima o dopo la Fase 4~~ → **lasciato intatto** fino a dopo la Fase 4
   (default raccomandato, adottato senza obiezioni).
4. ~~S1-S11 in Fase 7 o anche test anticipati di Fase 4~~ → **solo Fase 7**.
5. ~~S6-S11 batteria ufficiale o proposta di partenza~~ → **confermati come batteria ufficiale**.

## Fonti

- [[lanchester-vs-motore-des]] — analisi che origina questa proposta
- [[source-lanchester-scenari-ai]] — fonte ingerita
- [[virtual-session-engine-des]] — architettura e vincoli entro cui la proposta deve stare
- `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:251` — stato attuale di
  `calcFightResult`, verificato
