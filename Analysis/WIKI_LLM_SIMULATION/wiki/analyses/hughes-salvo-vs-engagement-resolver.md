---
title: "Il modello a salva di Hughes contro l'Engagement_Resolver della Fase 4"
type: analysis
tags: [hughes, salvo-combat-model, discrete-event, combat-resolution, dwm, architecture]
created: 2026-09-22
updated: 2026-09-22
query: "La fonte su Hughes (RAW/Event_Driven_Salva_Hughes/) supera lo scetticismo dovuto e cosa cambia, in concreto, nella progettazione di Logic/Engagement_Resolver.py (Fase 4)?"
sources: ["[[source-hughes-salvo-event-driven]]", "[[virtual-session-engine-des]]"]
related: ["[[risolutore-ingaggio-salva-fase4]]", "[[salvo-combat-model]]", "[[soglie-disingaggio-e-attrito-aggregato]]", "[[lanchester-vs-motore-des]]"]
---

# Il modello a salva di Hughes contro l'Engagement_Resolver della Fase 4

## Domanda

[[virtual-session-engine-des]] ha già scelto il modello a salva di Hughes come risolutore del
molti-contro-molti dello strato 2. [[source-hughes-salvo-event-driven]] è la prima fonte ingerita che
lo descrive. Colma la lacuna dichiarata (*"nessuna fonte su Hughes"*, [[lanchester-models]] § Note) e,
soprattutto: **cosa cambia, in concreto, nella progettazione di `Logic/Engagement_Resolver.py`?**

## Risposta Sintetica

**D1 colma la lacuna, D2-D7 no — ma le loro proposte sono comunque utili come catalogo di meccanismi
da valutare uno per uno, non come fonte da cui prendere formule.** Applicando alla fonte la stessa
disciplina già usata per Lanchester e per l'LLM locale (si prende la *forma*, mai i *numeri*, e ogni
meccanismo si verifica contro il codice reale prima di essere adottato): **quattro meccanismi
strutturali passano** (termine difensivo a saturazione, soglia di shock, congelamento del payload
all'istante di fuoco, targeting anti-overkill), **uno introduce una precondizione nuova e già
documentata come mancante nel codice** (scorte di munizioni per asset), e **uno è un punto
architetturale che tocca lo strato 1, non lo strato 2** (il re-scheduling dopo lo spostamento
fisico). Nessun coefficiente, nessuna latenza, nessun tempo di volo della fonte è utilizzabile.
Proposta operativa in [[risolutore-ingaggio-salva-fase4]].

---

## 1. Cosa il progetto ha già, e dove Hughes si aggancia

`Logic/Damage_Model.py` (Q2, chiusa 2026-09-22) risolve **un colpo alla volta**:
`resolve_hit(accuracy, destroy_capacity, draw)` → KILL/DAMAGE/MISS, e
`build_damage_event`/`apply_damage_event` sono già **separate** apposta — calcolare tutti gli esiti,
ordinarli deterministicamente, applicarli solo dopo. Questa separazione è precisamente
l'infrastruttura che un risolutore a salva richiede (una salva **è** un insieme di colpi da valutare
insieme, non uno alla volta), e non richiede modifiche: `Engagement_Resolver` la chiama in un ciclo
per ogni colpo della salva, poi applica l'esito aggregato.

Quello che manca, verificato riga per riga nel codice prima di leggere la fonte:

- **nessun termine difensivo a saturazione**: `resolve_hit` valuta un colpo contro le probabilità
  dell'arma, non contro una capacità di intercettazione del bersaglio che si esaurisce dentro la
  stessa salva;
- **nessuna soglia di disingaggio** — già noto e proposto in [[soglie-disingaggio-e-attrito-aggregato]]
  § P1, prima ancora di leggere questa fonte;
- **nessuna scorta di munizioni per asset** — cercato esplicitamente in tutto `Asset/`, `Block/`: i
  soli usi di "ammo" nel codice (`Ground_Weapon_Data.AMMO_PARAM`/`AMMO_TARGET_EFFECTIVENESS`) sono
  parametri statici di **scoring dell'arma** (che munizione è più efficace contro quale bersaglio),
  non uno stock che si consuma. Il gap è già annotato dagli sviluppatori:
  `Block/Military.py:720`, nel placeholder di `get_recognition_report`, elenca esplicitamente
  *"Stato dei rifornimenti (munizionamento, energy, fuel e hr)"* fra le cose che il report dovrebbe
  un giorno coprire e oggi non copre.

## 2. Il termine difensivo a saturazione — passa, è il contributo reale

**Cosa propone la fonte** (D1-D2, v. [[salvo-combat-model]]): $y$/$z$ non è una probabilità per
colpo, è una **capacità di intercettazione per salva**. Sopra quella capacità il surplus penetra
integralmente. È l'unico elemento della fonte che **non ha equivalente** in `Damage_Model.py` oggi.

**Perché è strutturale e non un dettaglio**: senza saturazione, un attaccante che concentra 20 colpi
in un istante e uno che ne lancia 1 al secondo per 20 secondi producono lo stesso danno atteso
(stessa somma di `resolve_hit` indipendenti). Con la saturazione non è vero: il primo supera la
capacità di intercettazione del bersaglio e infligge danno concentrato, il secondo viene intercettato
colpo per colpo. È esattamente la distinzione che rende "chi spara per primo con un attacco
concentrato" dottrinalmente diverso da "chi spara per primo", e il progetto ha già le basi fisiche
per costruirla: `ThreatAA` (Fase 2) ha già una nozione di capacità della difesa aerea
(`danger_level`, `Military.air_defense_power()`), ma nessuna delle due è oggi una *capacità di
intercettazione per salva* nel senso di Hughes — sono aggregati per il targeting, non un contatore
che si consuma dentro un ingaggio.

**Verdetto**: adottare la forma (capacità finita di intercettazione consumata all'interno di una
singola salva, surplus che penetra), non i simboli $y$/$z$ né alcun valore numerico. Dettaglio
operativo in [[risolutore-ingaggio-salva-fase4]] § R1.

## 3. La doppia soglia di ritirata (perdite cumulate + shock da salva) — passa, estende P1

[[soglie-disingaggio-e-attrito-aggregato]] § P1 propone già una soglia di disingaggio come esito di
prima classe (`DISENGAGED` distinto da `DESTROYED`), basata su **perdite cumulate**. La fonte (D4)
aggiunge una seconda soglia indipendente: **shock da salva**, cioè la frazione di forza persa in un
**singolo impulso**, distinta dal totale accumulato nel tempo. È una distinzione reale: una forza che
perde il 40% in una salva sola si comporta diversamente (rotta immediata) da una che perde il 40%
in venti impulsi diluiti su un'ora (nessuna singola salva supera lo shock threshold, l'erosione è
lenta). Il modello a colpo-singolo di `Damage_Model.py` non ha una nozione di "impulso": la
introdurrebbe solo un risolutore a salva.

**Verifica di coerenza interna alla fonte**: il confronto D3→D4 (§ Lacuna F in
[[source-hughes-salvo-event-driven]]) mostra che applicando la soglia di shock del 35% introdotta in
D4 allo scenario *senza* SEAD di D3, anche lì la forza Blu sarebbe andata in rotta (perde il 50% in
un solo impulso) — cioè la fonte stessa, se applicasse le proprie regole in modo coerente, non
otterrebbe il risultato dottrinale che dichiara. Questo **non invalida l'idea della doppia soglia**
(è indipendente dall'errore di applicazione), ma è un promemoria concreto del motivo per cui il
progetto non importa mai conclusioni dagli esercizi numerici di questa fonte, solo i meccanismi.

**Verdetto**: aggiungere lo shock da salva come seconda soglia indipendente in P1, stessa sede
(dottrina/C2, mai costante nel risolutore). Dettaglio in [[risolutore-ingaggio-salva-fase4]] § R2.

## 4. Munizioni come risorsa per-asset — nuova precondizione, non un'estensione opzionale

D4/D7 trattano le munizioni come uno stock decrementato per salva: a zero, l'unità non è neutra —
è un **bersaglio inerme** o si ritira per ragioni logistiche. Non esiste nel progetto in nessuna
forma (v. § 1), e non era nell'elenco delle undici precondizioni bloccanti di
[[virtual-session-engine-des]] perché nessuna delle due strategie originarie dell'utente lo
richiedeva esplicitamente.

**Perché un risolutore a salva lo richiede e uno a colpo-singolo poteva ignorarlo**: `resolve_hit`
oggi assume implicitamente che un'arma possa sempre sparare. È un'approssimazione ragionevole per un
singolo colpo isolato, ma un risolutore che deve decidere **quanti colpi compongono la prossima
salva** di un asset non può rispondere senza sapere quanti colpi gli restano — altrimenti ogni asset
ha munizioni infinite per costruzione, il che rende irrilevante ogni soglia di esaurimento e falsa
qualunque sessione lunga (un blocco che ha sparato per un'ora intera resta offensivamente identico a
uno appena schierato).

**Verdetto**: precondizione nuova per la Fase 4, non opzionale se si vuole un risolutore a salva
fedele. Non è un problema di modello — è un campo mancante su `Asset`/`Ground_Weapon_Data` — e va
trattato con la stessa disciplina di `Asset.apply_damage`: un consumo esplicito, mai implicito,
mai stimato "a occhio". Dettaglio in [[risolutore-ingaggio-salva-fase4]] § R3.

## 5. Targeting anti-overkill (D3) — passa, è indipendente dal resto

Allocare fuoco a un bersaglio fino a saturazione o distruzione stimata, poi passare al successivo.
Non richiede alcuna equazione di Hughes: è un algoritmo di allocazione greedy applicabile a
qualunque risolutore molti-contro-molti, e risolve un problema reale — senza di esso un risolutore
a eventi indipendenti sovra-alloca fuoco su bersagli già neutralizzati (spreco di salve, non un
errore di correttezza ma di realismo). Compatibile per costruzione con `build_damage_event`, che
calcola gli esiti prima di applicarli: il ciclo di allocazione può controllare lo stato-salute
proiettato fra un colpo calcolato e il successivo nella stessa salva.

## 6. Congelamento del payload e re-scheduling dopo spostamento — punto architetturale, tocca lo strato 1

**Lacuna A della fonte** (v. [[source-hughes-salvo-event-driven]] § Lacune): D5/D6 ricalcolano
retroattivamente il volume di una salva già in volo quando il lanciatore viene colpito dopo il
lancio — violazione di causalità (i proiettili in aria non spariscono se il pezzo che li ha sparati
viene distrutto). La correzione che la fonte stessa suggerisce implicitamente, e che qui si adotta
in positivo: **il payload di una salva va congelato all'istante di fuoco**, mai ricalcolato
all'istante d'impatto. Per `Engagement_Resolver` questo è un vincolo di progettazione da rispettare
fin dall'inizio, non un bug da correggere dopo: il numero di colpi e il bersaglio di una salva sono
decisi al momento dello scheduling dell'evento "lancio", e nessun evento successivo (compresa la
distruzione del lanciatore stesso) altera quella salva già schedulata — al più ne impedisce di
future.

**Il punto collegato, e più rilevante per l'architettura**: D7 introduce `EVENT_UNIT_DISPLACEMENT`,
uno spostamento fisico dell'unità *durante* l'ingaggio, come evento di prima classe. Nel progetto
questo non è compito dell'`Engagement_Resolver`: è `Logic/Contact_Scheduler.py` (Fase 3, già scritto)
che calcola `ContactWindow`/`ThreatWindow` a partire da rotte fissate. **Se un asset cambia rotta a
metà di una finestra di contatto già calcolata, quella finestra è invalidata** — lo scheduler non ha
oggi un meccanismo di ricalcolo incrementale, perché finora nessun consumatore modificava una rotta
dopo che le finestre erano state prodotte. È un punto che la Fase 4 **scopre** ma che **non le
appartiene**: la decisione se e come re-schedulare va presa quando `Engagement_Resolver` (o un
livello sopra di esso, es. un C2 che ordina una ritirata) può effettivamente modificare la rotta di
un asset in corso di sessione. Non toccato in questa analisi; registrato come punto aperto in
[[risolutore-ingaggio-salva-fase4]] § R4.

## 7. Cosa NON è utilizzabile, e perché

Stessa disciplina già applicata in [[lanchester-vs-motore-des]] § 3: si prende la forma, mai i
numeri. Nello specifico, dalla fonte non si importa:

1. **Nessun coefficiente** ($\alpha,\beta,\gamma,\sigma$ di D2-D7) — tutti dichiaratamente scelti a
   mano, senza calibrazione, e con almeno cinque difetti aritmetici/logici accertati nella stessa
   fonte (v. [[source-hughes-salvo-event-driven]] § Lacune B-E, G-K).
2. **Nessuna latenza sensore→C2→lancio** — il progetto ha già dati reali e ricercati
   (`Air_Route_Manager.threat_reaction_times()` → `(min_detection_time, min_fire_time)` dalla
   tabella SAM di riferimento, Fase 2), la fonte inventa numeri diversi in due documenti diversi per
   lo stesso scenario (5+15 s in D6, 3+7 s in D7).
3. **Nessun tempo di volo balistico** — D7 usa moto rettilineo uniforme ($T=d/v$), sottostimando di
   un fattore 2 il tempo reale d'artiglieria a lungo raggio (§ Lacuna K).
4. **Nessuna delle tre composizioni di forze usate come esempio** — sono illustrative, non scenari
   di test come le cinque strutture di [[lanchester-vs-motore-des]] § 2c: qui la fonte non le
   presenta come casi indipendenti dalla matematica, sono inscindibili dai coefficienti sbagliati che
   le accompagnano.

## Fonti Utilizzate

- [[source-hughes-salvo-event-driven]] — tutti i sette documenti, letti integralmente, incluse le
  undici lacune accertate
- [[salvo-combat-model]] — formulazione base del modello, distillata da D1
- [[virtual-session-engine-des]] — architettura a 4 strati, roadmap, Fase 4 come destinazione
- [[soglie-disingaggio-e-attrito-aggregato]] — P1, la soglia di disingaggio già proposta prima di
  questa fonte
- `Code/Dynamic_War_Manager/Source/Logic/Damage_Model.py` — `resolve_hit`,
  `build_damage_event`/`apply_damage_event`, letti per verificare cosa già esiste
- `Code/Dynamic_War_Manager/Source/Block/Military.py:720` — placeholder che documenta l'assenza di
  stato dei rifornimenti
- `Code/Dynamic_War_Manager/Source/Asset/Ground_Weapon_Data.py` — verificato che `ammo_type`/
  `AMMO_PARAM` sono parametri di scoring statici, non uno stock consumabile

## Conclusioni e Implicazioni per Warfare-Model

**Cosa non cambia**: l'architettura a 4 strati resta invariata; il modello a salva di Hughes resta
la scelta per lo strato 2, confermata non messa in discussione da questa lettura più approfondita.

**Cosa la fonte aggiunge di concreto, subordinato a conferma dell'utente** (dettaglio in
[[risolutore-ingaggio-salva-fase4]]):

1. termine difensivo a capacità di intercettazione per salva con saturazione (§ 2);
2. soglia di shock da salva, seconda soglia indipendente accanto a quella cumulata di P1 (§ 3);
3. scorte di munizioni per asset — precondizione nuova (§ 4);
4. targeting anti-overkill nell'allocazione di fuoco di una salva (§ 5);
5. congelamento del payload all'istante di fuoco come vincolo di progettazione fin dall'inizio, e
   segnalazione (non risoluzione) del punto sul re-scheduling dopo spostamento fisico, che riguarda
   lo strato 1 più che la Fase 4 (§ 6).

**Da non fare**: importare un coefficiente, una latenza o un tempo di volo da questa fonte, in
qualunque modulo — stessa regola già applicata a Lanchester.
