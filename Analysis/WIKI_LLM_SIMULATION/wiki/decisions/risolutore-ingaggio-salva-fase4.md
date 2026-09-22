---
title: "Termini del modello a salva da adottare in Logic/Engagement_Resolver.py (Fase 4)"
type: decision
tags: [architecture, dwm, salvo-combat-model, combat-resolution, discrete-event, naval, ground, air]
created: 2026-09-22
updated: 2026-09-22
status: proposed
affects: ["[[logic-decision]]", "[[asset-base]]", "[[block]]"]
related: ["[[hughes-salvo-vs-engagement-resolver]]", "[[salvo-combat-model]]", "[[virtual-session-engine-des]]", "[[soglie-disingaggio-e-attrito-aggregato]]", "[[core-simulator-agnostic]]"]
---

> **`status: proposed`** — questa pagina è una **raccomandazione**, non una decisione presa. Nessuna
> riga di codice è stata scritta o modificata. La decisione spetta all'utente; finché non è
> accettata, `Logic/Engagement_Resolver.py` non è ancora scritto e il comportamento di riferimento
> resta quello descritto in [[virtual-session-engine-des]] (Pk = accuracy × destroy_capacity per
> singolo colpo, nessun termine di saturazione, nessuna soglia di disingaggio, munizioni infinite
> per costruzione).

## Contesto

[[virtual-session-engine-des]] ha già scelto il modello a salva di Hughes come risolutore del
molti-contro-molti dello strato 2 (Fase 4). [[source-hughes-salvo-event-driven]] è la prima fonte
ingerita che lo descrive con provenienza verificabile (D1), e [[hughes-salvo-vs-engagement-resolver]]
ne valuta l'applicabilità componente per componente. Questa pagina raccoglie le **proposte concrete**
che ne discendono, nella stessa forma già usata per [[soglie-disingaggio-e-attrito-aggregato]] e
[[llm-locale-ruolo-e-confini]]: si prende la *forma* dalla fonte, mai i *numeri*.

## Decisione proposta

### R1 — Termine difensivo a capacità di intercettazione per salva (saturazione)

`Logic/Damage_Model.resolve_hit` risolve un colpo alla volta contro `accuracy`/`destroy_capacity`
dell'arma — nessuna nozione di quanti colpi il bersaglio può intercettare **nella stessa salva**.
Si propone di introdurre, a livello del bersaglio che riceve una salva (non dell'arma che spara),
una **capacità di intercettazione consumabile** entro l'evento-salva: i primi $N$ colpi della salva
vengono valutati contro questa capacità (intercettati, non raggiungono `resolve_hit`), il surplus
oltre $N$ la raggiunge integralmente.

- **Non è una probabilità per colpo**: è un contatore che si esaurisce dentro l'evento. Va tenuto
  distinto da `accuracy`/`destroy_capacity`, che restano proprietà dell'arma che spara, non del
  bersaglio che subisce.
- **Dove vive il numero**: candidato naturale è una funzione della difesa aerea/puntuale già
  esistente — `Military.air_defense_power()` (Q3) o una nuova aggregazione su `ThreatAA` — ma
  **il valore stesso non va inventato qui**: se calibrato, va dallo stesso processo con cui si
  calibrerebbe un fallback aggregato (v. P2 di [[soglie-disingaggio-e-attrito-aggregato]]), mai da
  [[source-hughes-salvo-event-driven]], che non fornisce numeri utilizzabili.
- **Compatibilità con l'esistente**: `build_damage_event`/`apply_damage_event` restano invariate —
  la saturazione decide **quali** colpi di una salva raggiungono `resolve_hit`, non come
  `resolve_hit` stesso funziona.

### R2 — Soglia di shock da salva, seconda soglia indipendente da P1

[[soglie-disingaggio-e-attrito-aggregato]] § P1 propone già una soglia di disingaggio basata su
**perdite cumulate**. Si propone di aggiungere una seconda soglia, indipendente e verificata
separatamente dopo ogni salva (non dopo ogni colpo): la frazione di forza persa in un **singolo
impulso**. Le due soglie coesistono — una forza può disingaggiarsi per erosione lenta (P1
originale) o per shock improvviso (questa estensione), qualunque delle due scatti per prima.

- Stessa sede di P1: parametro dottrinale dichiarato in `Context/Doctrine.py` o al livello C2, mai
  costante nel risolutore.
- Stesso esito `DISENGAGED` di P1, nessun nuovo tipo di esito richiesto in `SessionOutcome`.
- **Non eredita gli errori della fonte**: la fonte stessa, applicando la propria soglia di shock in
  modo incoerente fra due scenari altrimenti identici (v.
  [[hughes-salvo-vs-engagement-resolver]] § 3), produce una conclusione dottrinale che non regge. Il
  meccanismo (soglia di shock) è indipendente da quell'errore di applicazione e resta valido; va
  solo verificato — con un test dedicato — che la soglia si applichi allo stesso modo a entrambi i
  lati e in ogni scenario, non solo dove conviene alla narrazione.

### R3 — Scorte di munizioni per asset (precondizione nuova)

Verificato che il progetto non ha, in nessuna forma, uno stock di munizioni che si esaurisce: i soli
campi `ammo_type`/`AMMO_PARAM` in `Ground_Weapon_Data.py` sono parametri statici di scoring
dell'arma, non un contatore. Il gap è già annotato dagli sviluppatori
(`Block/Military.py:720`, placeholder di `get_recognition_report`) ma mai implementato.

Si propone di introdurre un contatore di munizioni per asset (o per arma installata sull'asset, la
granularità è un punto aperto, v. sotto), con la stessa disciplina già adottata per
`Asset.apply_damage`:

- **consumo esplicito**, mai implicito: ogni colpo/salva risolta lo decrementa, mai stimato a
  posteriori;
- **a zero munizioni**, l'asset non spara più (offensivamente neutro) ma resta un bersaglio valido —
  coerente con `apply_damage`, che non tocca la salute per questo motivo;
- **nessuna estrazione casuale**: il consumo è deterministico (N colpi sparati = N in meno), la
  sola fonte di varianza resta `resolve_hit`.

**Perché serve una decisione dell'utente e non un'implementazione diretta**: dove vive il contatore
(su `Asset`, su un'istanza d'arma, su `Component` del `Block`) e se il rifornimento fa parte della
Fase 4/5 o è materia del ciclo di campagna (rientra nel possibile scope di
`Rinomina_Campaign_State.py`, riservato) sono scelte di modello che eccedono questa proposta.

### R4 — Congelamento del payload all'istante di fuoco; re-scheduling dopo spostamento fisico

Due proposte di livello diverso, tenute insieme perché la fonte le presenta insieme (D5-D7) ma
**appartengono a strati diversi dell'architettura**:

- **Congelamento del payload (Fase 4, adottabile subito)**: il numero di colpi e il bersaglio di una
  salva sono decisi al momento dello scheduling dell'evento "lancio" e **non vengono mai
  ricalcolati** da eventi successivi, inclusa la distruzione del lanciatore stesso dopo il lancio.
  È un vincolo di progettazione per `Engagement_Resolver`, non un meccanismo da costruire: evita per
  costruzione la violazione di causalità diagnosticata come Lacuna A in
  [[source-hughes-salvo-event-driven]] (una salva già in volo non si riduce perché il pezzo che
  l'ha sparata viene colpito dopo).
- **Re-scheduling dopo spostamento fisico (punto architetturale, NON Fase 4)**: se un asset cambia
  rotta durante una finestra di contatto già calcolata da `Logic/Contact_Scheduler.py` (Fase 3), la
  finestra andrebbe invalidata e ricalcolata — meccanismo che oggi non esiste, perché finora nessun
  consumatore modificava una rotta dopo che le finestre erano state prodotte. **Questa proposta non
  include un'implementazione**: registra solo che la Fase 4, quando un C2 o l'`Engagement_Resolver`
  stesso ordinerà una ritirata a metà ingaggio, scoprirà questo buco, e che la sua soluzione
  appartiene allo strato 1, non allo strato 2.

## Motivazione

Le quattro proposte condividono lo stesso criterio: risolvono un buco **già verificato nel codice**
(saturazione assente, soglia di shock assente, munizioni assenti, nessun vincolo esplicito di
causalità sul payload), non un'osservazione teorica della fonte. Nessuna richiede di importare un
numero non verificato — è la stessa disciplina già applicata a Lanchester
([[lanchester-vs-motore-des]]) e alla proposta LLM ([[llm-locale-ruolo-e-confini]]).

## Conseguenze

**Se accettata**:

- `Logic/Engagement_Resolver.py` nasce con: allocazione di salva verso `resolve_hit` filtrata da una
  capacità di intercettazione consumabile (R1); una seconda soglia di disingaggio per shock,
  accanto a quella cumulata di P1 (R2); un vincolo esplicito di non-ricalcolo del payload dopo il
  lancio (R4, prima parte);
- nasce anche una precondizione nuova, non elencata nelle undici originarie di
  [[virtual-session-engine-des]]: un contatore di munizioni per asset (R3), con proprio design da
  decidere prima o durante la Fase 4;
- si registra, senza risolverlo, un punto aperto per lo strato 1: re-scheduling delle finestre di
  contatto dopo un cambio di rotta a ingaggio in corso (R4, seconda parte) — da riprendere quando il
  primo consumatore reale (probabile: un ordine di ritirata C2) lo renderà necessario.

**Se respinta**: nulla cambia; [[hughes-salvo-vs-engagement-resolver]] resta come analisi archiviata
e questa pagina va marcata `status: superseded` o rimossa. `Engagement_Resolver` nascerebbe allora
a colpo-singolo puro, senza saturazione né munizioni, come già previsto in
[[virtual-session-engine-des]] prima di questa ingestione.

**Esplicitamente fuori perimetro**: qualunque coefficiente, latenza o tempo di volo della fonte
(v. [[hughes-salvo-vs-engagement-resolver]] § 7); la progettazione dettagliata del contatore
munizioni (R3, granularità e persistenza); l'implementazione del re-scheduling (R4, seconda parte).

## Punti aperti da confermare con l'utente

1. **R1** — dove vive il numero di capacità di intercettazione: una nuova funzione su `Military`
   accanto ad `air_defense_power()`, o un riuso diretto di quest'ultima con una scala diversa?
2. **R2** — la soglia di shock è per **forza** o per **singolo asset**, stessa domanda già aperta
   per P1 in [[soglie-disingaggio-e-attrito-aggregato]] — le due risposte devono essere coerenti?
3. **R3** — granularità del contatore munizioni (per asset, per arma installata, per tipo di
   munizione) e se il rifornimento è materia della Fase 4/5 o del ciclo di campagna più ampio?
4. **R4** — il re-scheduling delle finestre di contatto va progettato ora, anticipando il bisogno,
   o si rimanda al momento in cui un consumatore reale (probabile: ordine di ritirata C2) lo rende
   necessario?

## Fonti

- [[hughes-salvo-vs-engagement-resolver]] — analisi che origina questa proposta, con la valutazione
  componente per componente
- [[source-hughes-salvo-event-driven]] — fonte ingerita, D1 (solida) e D2-D7 (meccanismi utili,
  numeri da scartare)
- [[salvo-combat-model]] — formulazione del modello di riferimento
- [[virtual-session-engine-des]] — architettura e vincoli entro cui la proposta deve stare
- [[soglie-disingaggio-e-attrito-aggregato]] — P1, la soglia di disingaggio a cui R2 si affianca
- `Code/Dynamic_War_Manager/Source/Logic/Damage_Model.py`,
  `Code/Dynamic_War_Manager/Source/Block/Military.py:720` — stato attuale verificato nel codice
