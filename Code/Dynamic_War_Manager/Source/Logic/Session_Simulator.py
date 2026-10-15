"""Orchestratore di sessione — fa girare **una sessione virtuale vera**, dall'ordine all'esito.

FASE 6 del motore di sessioni virtuali (v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §6 e §8, e
[[project_virtual_session_engine_design]]): "orchestratore a coda eventi (heapq, clock in
secondi), risoluzione simultanea".

Le fasi 3-5 hanno prodotto i pezzi, ma nessuno li aveva mai messi in fila:

    SessionOrder ──> Contact_Scheduler.schedule_contacts      (strato 1: QUANDO)
                 ──> raggruppamento in componenti connesse di forze
                 ──> Engagement_Resolver.resolve_engagement    (strato 2: COME FINISCE)
                 ──> apply_engagement_result                   (strato 3: danno, munizioni)
                 ──> Fuel_Model.build/apply_fuel_event         (strato 3: carburante)
                 ──> Session_Types.assemble_session_outcome    (porta di uscita)

Questo modulo e' SOLO quella fila: non reimplementa geometria, Pd, latenze, salve, danno o
consumi. Ogni numero che produce viene da uno dei moduli chiamati.

## La coda eventi

Due tipi di evento di sessione, in un `heapq` con chiave `(t, tipo, id, sequenza)`:

- **ENGAGEMENT** — uno per componente connessa di forze (v. sotto): le forze legate,
  direttamente o per tramite di altre, da almeno una `ContactWindow`; istante = inizio
  della prima finestra fra QUALUNQUE coppia della componente. Risolve l'intera componente
  con UNA chiamata a `resolve_engagement` (che ha la propria coda interna di
  lanci/impatti) e ne applica subito l'esito agli asset reali di tutte le sue forze.
- **MOVEMENT** — uno per asset con rotta schedulabile nella sessione; istante = fine del
  suo movimento dentro la sessione (dalla F6-A troncato all'esaurimento del carburante). Produce e
  applica i `FuelEvent` del tragitto, uno per tratto (v. "Carburante").

## Missioni (Fase 3 del piano della Missione)

Dal 2026-10-05 le rotte arrivano SOLO dalle missioni dell'ordine (`SessionOrder.missions`):
`Logic/Mission_Adapter.session_movements` ne ricava le mappe `routes`/`starts`/`speeds` per
asset (rotta di riferimento + offset di formazione, partenza della missione, velocita' di
missione), che il resto della fila consuma esattamente come prima. I parametri `routes`/
`starts`/`speeds` di `run_session` sono stati RIMOSSI (decisione Q2 dell'utente: una sola
strada). Gli asset senza missione restano fermi, come gli asset senza rotta di prima (dalla
F5-B quelli di missione sono presenti anche prima della partenza e dopo la fine, v. sotto). Ogni
missione deve riferirsi a un blocco passato fra le forze, e ogni suo asset deve appartenere a
quel blocco (`Mission_Types.check_mission_assets`). Regola A (F4a, decisione dell'utente): la
missione si muove insieme, nessun tratto piu' veloce della velocita' massima del suo mezzo piu'
lento (`Mission_Adapter.check_mission_speed`; asset senza il dato esclusi con un warning).

## La missione come unita' d'ingaggio (F4b, D3.e)

Dalla F4b la FORZA d'ingaggio e' la missione (`_engagement_forces`): ogni missione diventa una
vista `Mission_Adapter.MissionForce` (asset della missione, lato del blocco, id e nome =
`mission_id`), e le finestre sono raggruppate per missione. Disingaggio, soglia di rottura
(tempra) e `committed` valgono quindi per missione: due missioni dello stesso blocco ingaggiano e
disingaggiano separatamente (decisione dell'utente, 2026-10-08). Lo scheduler riceve ancora i
BLOCCHI: le finestre sono per coppia di asset e la potatura per blocco non dipende da come gli
asset sono raggruppati in forze.

## Dominio di coordinamento (2026-10-11, decisioni dell'utente 6 e 7 del piano della Missione)

Ripartizione del fuoco (saturazione, tiratori impegnati, lanciatori prioritari), percezione del
nemico e (F4b++) difesa di salva NON sono per missione ma per dominio di coordinamento: missioni dello stesso blocco OPPURE
della stessa Operazione (`SessionOrder.operations`), per unione transitiva, mai a cavallo dei lati
(`Mission_Adapter.coordination_domains`; la vista residua e un blocco senza missioni hanno l'id del
blocco e quindi stanno nel dominio delle missioni del blocco). La mappa e' passata a ogni ingaggio
(`coordination_of` di `resolve_engagement`), condivisione istantanea senza latenza (dichiarato),
nessun cueing del tiro. Perche' la condivisione valga, le forze di uno stesso dominio sono messe
nella STESSA componente connessa anche quando non hanno nemici in comune
(`_connected_components`): due missioni dello stesso blocco su fronti disgiunti sono risolte in una
run, come lo era il blocco prima della F4b. Effetto sull'RNG: la componente unita ha l'`event_id`
delle sue forze riunite (v. "RNG: uno stream per ingaggio").

Asset del blocco senza missione: fermi per tutta la sessione, nella forza del blocco.
  * blocco senza missioni: entra nel risolutore come prima, l'oggetto blocco con il suo id;
  * blocco con missioni e asset non assegnati: questi formano la vista residua
    `MissionForce.unassigned` con l'id DEL BLOCCO.
Un `mission_id` non puo' coincidere con l'id di un blocco passato (sarebbero due forze con lo
stesso id).

## Postura continua degli asset senza missione (F4c, D1.c)

Decisioni dell'utente (2026-10-11), v. `Mission_Adapter.continuous_posture`: un AEREO senza
missione e' a terra (bersaglio di superficie passivo, non osserva e non spara mai); un'unita'
terrestre o navale senza missione e' in postura `Defense` dichiarata, con il tiro di prima. La
sessione calcola l'insieme degli aerei a terra (`Mission_Adapter.grounded_assets`, sugli asset dei
blocchi senza missioni e delle viste residue) e lo passa allo scheduler (`grounded`: bersaglio in
modo 'ground', nessun sensore) e a ogni ingaggio (`grounded` di `resolve_engagement`: niente
rilevamento ne' tiro, classificazione di superficie verso la fire control, peso di minaccia nullo,
nessun disingaggio per loro). Nessuno stato nuovo nell'asset, nessuna mutazione: l'insieme e'
della sessione. Senza aerei fuori missione l'insieme e' vuoto e la sessione e' identica a prima.
Dalla F5 l'insieme e' un programma nel tempo (sotto).

## Presenza e postura nell'esito (F5 passo (b), D1.a/b, deviazione 12 del piano della Missione)

Decisioni dell'utente: un asset di missione NON sparisce fuori dalla sua rotta.
  * unita' terrestri e navali: presenti FERME nella posizione di partenza prima di partire e in
    quella finale dopo la fine, in postura `Defense`, quindi rilevabili e ingaggiabili in quei
    tratti (il carro fermo a 4 km dal nemico resta un bersaglio, esperimenti E1/E3);
  * aerei che non partono in volo (parcheggio, pista): presenti e A TERRA fino al decollo,
    bersagli di superficie passivi come gli aerei senza missione; dopo la fine della rotta a terra
    SOLO se l'ultimo punto e' LAND su una base vera (`Mission_Adapter.lands_on_air_base`:
    riferimento del waypoint a un asset di una base, oppure punto nell'area di una base del lato
    della missione, calcolata qui dalle forze passate con `Mission_Adapter.air_base_points`),
    altrimenti escono di scena all'arrivo come prima (fino al rientro della F6).
La sessione ricava da `Mission_Adapter` i tratti di presenza (`movement_legs`, passati allo
scheduler come `legs` e al risolutore come tratti degli asset) e il programma degli aerei a terra
(`grounded_schedule`: sempre gli aerei senza missione, a intervalli quelli di missione), passato
allo scheduler (finestre spezzate a decolli e atterraggi) e a ogni ingaggio. Il carburante usa i
soli tratti di MOVIMENTO (`movement_legs(..., presence=False)`): la presenza ferma non consuma. Dalla
F6-A tratti e programma a terra sono corretti per l'esaurimento del carburante (v. "Carburante").
L'esito porta la postura di OGNI asset delle forze passate a fine sessione
(`SessionOutcome.postures`, `Mission_Adapter.session_postures`), anche dei blocchi senza missioni:
postura continua della F4c per gli asset senza missione, postura di fine missione per gli altri
(`Defense` a movimento finito o non ancora iniziato, tipo di missione in movimento, aereo a terra
`parking_cold`, aereo uscito di scena `off_scene`). Interruttore `Mission_Adapter.F5_PRESENCE`
(attivo): spento, i tratti sono quelli della sola rotta e la storia e' quella della F5-A (la
postura e' riportata comunque).

## Attese, ETA bloccate e TOT (F5 passi (c)-(d), cablati dalla F5-C)

Interruttore `Mission_Adapter.F5_WAITS` (attivo dalla F5-C): le azioni WAIT ('hold' e 'orbit',
entrambe presenza FERMA nel punto per la durata: l'orbita senza circuito geometrico e'
un'approssimazione dichiarata), le ETA bloccate e il TOT della missione (`Mission.tot`: il TOT e'
di ogni missione, anche nella stessa Operazione, decisione dell'utente del 2026-10-12) entrano nel
movimento di ogni asset come tratti fermi (`AssetMovement.holds`). Arrivano cosi' allo scheduler
(`legs`) e al risolutore con gli stessi tratti della presenza: una CAP in orbita ha finestre di
contatto per tutta l'attesa. Dalla F6-A attese e orbite consumano NEL TEMPO alla crociera, con un
`FuelEvent` per tratto (v. "Carburante"); nella F5-C non consumavano. Gli istanti effettivi di arrivo ai punti, attese comprese, sono nel `MissionOutcome.actual_etas`
(v. `_mission_outcome`).

`SessionOrder.committed` resta chiavato per BLOCCO (la lingua della porta): per ogni forza
d'ingaggio vale la restrizione del suo blocco intersecata con i suoi asset
(`_engagement_committed`).

**Esito di forza**: un `ForceOutcome` per forza d'ingaggio, quindi per MISSIONE (`force_id` =
`mission_id`, `block_id` = blocco; per la vista residua e per un blocco senza missioni `force_id` =
id del blocco). L'esito del blocco NON e' aggregato in un `ForceOutcome` sintetico: e' l'insieme
degli esiti delle sue forze (`SessionOutcome.outcomes_of_block`). Fondere erosione, perdite e
stato di forze che hanno combattuto separatamente vorrebbe dire reinventarne la semantica, la
stessa ragione per cui `SessionOutcome` non fonde gli esiti di ingaggi diversi.

**Esito di missione (prima forma)**, nel `SessionOutcome.mission_outcomes`. Per asset:
  * DESTROYED (stato e motivo), all'istante del DamageEvent che lo distrugge (o a `t0` se era
    gia' distrutto all'inizio);
  * ROUTE_COMPLETED all'istante d'arrivo all'ultimo punto, se lo raggiunge dentro la sessione
    (stato DAMAGED se la salute finale e' < 100, altrimenti OPERATIONAL);
  * altrimenti SESSION_END alla fine della sessione: rotta tagliata dalla fine della sessione, o
    missione senza rotta (sul posto), ancora in corso.
  * (F6-B1) la fine di attivita' per un criterio dichiarato (WINCHESTER, DAMAGE, TARGET_DESTROYED,
    MAX_DURATION) se precede l'arrivo, v. "Fine di attivita' e stato di missione".
Per missione (prima forma): DESTROYED se tutti gli asset sono distrutti; COMPLETED se almeno un asset ha
raggiunto l'ultimo punto PRIMA di un'eventuale distruzione; altrimenti FAILED ("non completata
entro la sessione": manca uno stato "in corso", v. D4.e, che lo distinguerebbe da un
fallimento vero); dalla F6-B1 la regola unica sotto. ETA effettive per punto: il primo passaggio fra gli asset non ancora
distrutti, None se nessuno ci arriva dentro la sessione; e' l'istante d'ARRIVO al punto (prima di
un'eventuale attesa nel punto), calcolato dai tratti con le attese (`Mission_Adapter.waypoint_times`,
F5-C), non dalle ETA pianificate.
Carburante (F6-A, v. "Carburante"): un aereo perso per esaurimento e' DESTROYED con motivo
FUEL_EXHAUSTED all'istante dell'esaurimento (una distruzione in combattimento precedente prevale);
un asset fermo (terra/mare) o atterrato in planata per esaurimento ha motivo FUEL_EXHAUSTED, stato
OPERATIONAL/DAMAGED, e i punti dopo l'esaurimento non sono raggiunti (ETA None). Dalla F6-B1 lo stato
di missione segue la regola unica di "Fine di attivita' e stato di missione" (sotto); la precedenza
provvisoria della F6-A (ABORTED(FUEL) se ALMENO un asset superstite e' a secco) resta solo con
`F6_END_CRITERIA` spento.

## Fine di attivita' e stato di missione (F6-B1 del piano della Missione, D2.a/D2.d)

Interruttore `F6_END_CRITERIA` (attivo). I criteri di stato DICHIARATI in `EndCriteria` (nei default
nessuno e' attivo) chiudono l'ATTIVITA' dell'asset senza cambiarne la rotta (D2.a): dall'istante della
fine l'asset non lancia piu' salve offensive (quelle partite arrivano, R4), prosegue PASSIVO sulla
rotta pianificata, resta presente, bersaglio e intercettore (v. "Fine di attivita'" in
`Engagement_Resolver`). Per asset (`_activity_plans`, `ActivityPlan`):
  * `winchester`: le voci della scorta per arma dell'asset nelle categorie elencate (categoria =
    chiave del registro d'arma del dominio, `Fire_Control.weapon_category`, la stessa della fire
    control dai registri); scatta quando sono TUTTE a zero nello stato ombra del risolutore. Criterio
    inattivo (warning) per un asset senza scorta per arma, senza armi di quelle categorie o con
    un'arma di quelle categorie non modellata (contata a unita': non si esaurisce mai). Gia' a zero
    alla partenza: fine alla partenza della missione;
  * `damage_threshold`: salute persa / salute a inizio sessione >= soglia (mission kill, asset non
    distrutto);
  * `target_destroyed`: bersaglio ASSET (l'asset) o GROUP (gli asset del blocco o della missione con
    quell'id); tutti distrutti (in combattimento, gia' all'inizio o persi per carburante) -> fine
    all'istante dell'ultima distruzione (non prima della partenza). Bersagli POINT/AREA: non
    rappresentabili prima della F7 (bersagli espliciti), criterio ignorato con un warning. Nel
    risolutore il criterio vede le distruzioni degli ingaggi gia' risolti e della propria run;
    l'esito lo valuta sull'intera sessione (`_activity_ends`);
  * `max_duration_s`: fine all'istante partenza della missione + durata (semantica scelta, la piu'
    semplice: "durata o tempo sulla stazione" contato dalla partenza), passata al risolutore come
    fine nota a monte (`until`).
Per asset la fine e' la PRIMA fra quelle scattate (a parita' d'istante: danno, winchester, bersaglio,
durata) se cade nella sessione e prima dell'esaurimento del carburante; un asset che completa la rotta
PRIMA della fine di attivita' resta ROUTE_COMPLETED, un arrivo DOPO non completa la missione.
`abort_on_threat` NON e' letto (fuori dal piano della F6); `bingo` lo legge la F6-B2 (v. "Bingo").

**Stato di missione, regola unica** (sostituisce la precedenza provvisoria della F6-A):
DESTROYED (tutti gli asset persi, anche per carburante) > COMPLETED (obiettivo raggiunto: con
`target_destroyed` dichiarato e rappresentabile i bersagli tutti distrutti nella sessione, altrimenti
un asset all'ultimo punto prima di distruzione e fine di attivita', oppure fine per durata massima,
che e' una fine regolare) > ABORTED (OGNI asset superstite ha chiuso per carburante, munizioni o
danno; motivo FUEL / AMMUNITION / DAMAGE di quello che ha chiuso per ULTIMO, a parita' d'istante
FUEL, poi AMMUNITION, poi DAMAGE) > FAILED (fine senza obiettivo e senza motivo, incluso "ancora in
corso" a fine sessione). Con `target_destroyed` dichiarato la sola rotta completata non e' l'obiettivo:
FAILED.

**Postura `destroyed`** (interruttore `F6_DESTROYED_POSTURE`, attivo): un asset distrutto a fine
sessione (in combattimento o per carburante) ha postura `Mission_Adapter.DESTROYED_POSTURE` nell'esito.

A parita' d'istante ENGAGEMENT < MOVEMENT, poi l'id (stringa canonica, mai l'ordine di un
dizionario Python). Le finestre di un asset mobile cadono tutte dentro lo span dei suoi
tratti, quindi quando il suo MOVEMENT viene estratto ogni ingaggio che lo coinvolge e' gia'
stato risolto: il regime di consumo (v. sotto) e' noto.

## Forze impegnate su piu' fronti: componenti connesse

**Prima (fino al 2026-09-23): un ingaggio per coppia.** Le finestre erano raggruppate per
coppia (forza del lato A, forza del lato B) e ogni coppia era un ENGAGEMENT separato;
`Session_Types.assemble_session_outcome` dichiara che se due ingaggi coinvolgono lo stesso
asset i `health_before/after` sono concatenabili solo se il primo esito e' applicato prima
di risolvere il secondo, e l'orchestratore lo garantiva applicando ogni esito subito.
Restava pero' un difetto, non solo un'approssimazione: se X era in contatto con A e con B
in finestre SOVRAPPOSTE, l'ingaggio (X,A) estratto per primo era svolto fino alla sua
conclusione e applicato, e (X,B) leggeva uno stato di X gia' consumato anche per le salve
che, in tempo di sessione, precedevano la fine di (X,A). L'ordine della coda decideva chi
"arrivava prima" alla salute e alle scorte di X: un artefatto d'implementazione, non la
fisica del combattimento.

**Ora: un ingaggio per componente connessa.** Si costruisce il grafo non orientato con un
nodo per forza e un arco per ogni coppia (lato A, lato B) con almeno una finestra (la
stessa appartenenza ai lati di prima, `_group_windows`), e se ne cercano le componenti
connesse (`_connected_components`, visita deterministica per id). Ogni componente e'
risolta con UNA chiamata a `resolve_engagement`, con tutte le finestre delle sue coppie:
`force_a`/`force_b` = le prime due forze per id, `extra_forces` = le altre, per id. Dentro
la run lo stato ombra di X evolve in un'unica timeline consumata da tutti i fronti, e un
disingaggio e' per-forza (v. "Forze rotte" in Engagement_Resolver): il disingaggio di X
non ferma un eventuale altro fronte della componente.

Le componenti sono disgiunte: nessuna forza compare in due ingaggi della stessa sessione,
quindi il limite di `assemble_session_outcome` non puo' piu' presentarsi, e l'ordine di
risoluzione delle componenti non influenza gli esiti (resta comunque deterministico).

**Deliberatamente conservativa rispetto al tempo:** non si distingue se le finestre di una
componente si sovrappongono davvero o sono in sequenza (X contro A al mattino, contro B
la sera): anche in quel caso {X, A, B} e' risolta con una sola run. E' sempre corretto,
perche' la coda eventi interna ordina comunque gli eventi nel tempo esatto; un clustering
per intervalli aggiungerebbe complessita' senza aggiungere correttezza.

## RNG: uno stream per ingaggio

`SessionOrder.rng(mission_id=None, event_id=engagement_event_id(*forze), counter=0)`:

- dalla F4b gli id delle forze sono i `mission_id` (o l'id del blocco per un blocco senza
  missioni e per la vista residua): il `mission_id` entra nell'RNG ATTRAVERSO l'`event_id`, e
  ogni ingaggio fra missioni ha il proprio stream. Lo slot `mission_id` di `Session_Rng` resta
  None (livello "di sessione"): un ingaggio e' fra DUE O PIU' forze, tipicamente missioni di
  entrambi i lati, e nessuna di esse ne possiede lo stream; lo slot resta per le estrazioni che
  appartengono a una sola missione (nessuna, oggi).
- `event_id`: codifica JSON di `['engagement', id_1, id_2, ...]` con gli id della
  componente ORDINATI — funzione pura dell'INSIEME delle forze (id di dominio), mai
  dell'ordine di iterazione o di passaggio a `run_session`, e non ambigua anche con id che
  contengono separatori (una concatenazione `"a:b"` non lo sarebbe).
- `counter=0`: ogni componente e' risolta una sola volta per sessione. Il contatore resta
  libero per un futuro re-ingaggio (re-scheduling dopo un disingaggio, R4 seconda parte,
  non implementato).

**Precondizione di riproducibilita':** gli id di forza devono essere STABILI fra le
esecuzioni. `Block.__init__` genera l'id con `Utility.setId`, che aggiunge un suffisso
casuale (`'Military.Blue_#822100'`): due `Military` costruite da zero con lo stesso nome
avrebbero id diversi, quindi seed diversi E un diverso ordine della coda. **Corretto
2026-09-23**: `Block.__init__`/`Military.__init__` accettano ora un parametro `id` esplicito
(passthrough opzionale, comportamento invariato se assente) — chi costruisce forze da zero
per un replay/test deve passarlo per avere id stabili, invece di mutare `.id` dopo la
costruzione. In campagna l'id e' comunque quello dell'istanza gia' in memoria (persistito),
quindi il caso comune non è mai stato a rischio.

Stream indipendenti per ingaggio significano che aggiungere o togliere un ingaggio non
sposta le estrazioni degli altri. Aggiungere una forza a una componente, invece, cambia il
suo event_id e quindi l'intero stream della componente: e' voluto, perche' e' un ingaggio
diverso.

## `fire_control`: una sola callable, iniettata

`fire_control(shooter, target) -> ShotSpec | None`, la stessa firma di
`resolve_engagement`, passata tale e quale a ogni ingaggio. Non una per lato: la callable
riceve gli asset REALI e puo' distinguere lato, blocco o modello da se', quindi una mappa
per lato non aggiungerebbe capacita' ma solo una seconda forma dello stesso contratto. La
selezione dell'arma dai registri non sta nell'orchestratore: la fa la callable iniettata
(`Fire_Control.make_registry_fire_control`). Dalla F4c una fire control
che dichiara la keyword `target_grounded` la riceve per i bersagli a terra (v.
`resolve_engagement`).

## Carburante (F6-A del piano della Missione, decisioni dell'utente del 2026-10-12)

Fino alla F5 il carburante era un vincolo A POSTERIORI: un solo `FuelEvent` per asset a fine
movimento, per distanza, e un asset a secco continuava a muoversi e a combattere (esperimento E5
dell'analisi: un carro a secco dopo 852 m di 7 km ingaggiato 3 km piu' avanti). Dalla F6-A, dietro
due interruttori del modulo (`F6_FUEL_PER_LEG`, `F6_FUEL_CONSTRAINT`, entrambi attivi):

**Tratti che consumano.** Per ogni asset di missione i tratti di MOVIMENTO ritagliati alla sessione
(`Mission_Adapter.movement_legs(..., presence=False)`: senza la presenza ferma prima e dopo, che non
consuma), comprese le attese (tratti fermi della F5-C). Le attese consumano NEL TEMPO alla crociera
dell'asset (`Fuel_Model.build_leg_fuel_event`; ipotesi dichiarata, pessimistica: il loiter reale
consuma meno); non consumano i tratti fermi di un aereo A TERRA (parcheggio prima del decollo, sosta
dopo l'atterraggio: `_consuming_legs`). Stesso criterio per terra e mare.

**Esaurimento a monte (`F6_FUEL_CONSTRAINT`).** Il carburante dipende solo dai tratti e dal carburante
di partenza, quindi l'istante e il punto dell'esaurimento si calcolano PRIMA dello scheduler
(`Fuel_Model.fuel_exhaustion`, al regime di crociera) e i tratti oltre quel punto NON esistono: i
tratti troncati vanno allo scheduler (`legs`, il meccanismo della F5-A) e al risolutore, quindi i
contatti sono calcolati sui tratti reali. Esito (`_fuel_end`, `FuelEnd`):
  * terra/mare (o aereo ancora a terra): FERMO nel punto di esaurimento fino alla fine della sessione
    (`FUEL_HALT`), presente e bersaglio come la presenza fuori rotta della F5-B, postura `Defense`;
    NON distrutto;
  * aereo in volo: planata in linea retta sulla base aerea DEL SUO LATO piu' vicina entro quota x
    `Fuel_Model.GLIDE_RATIO` (`FUEL_GLIDE`; basi = `Mission_Adapter.air_base_points`, l'idoneita' per
    tipo d'aereo, es. lunghezza della pista, NON e' modellata: approssimazione dichiarata), poi A TERRA
    sulla base (programma `grounded` dall'atterraggio, bersaglio di superficie passivo come in F5-B);
    durante la planata e' un aereo in volo come gli altri (limite noto: l'esaurimento non e' fra i
    criteri di fine di attivita' della F6-B1). Velocita' di planata = crociera dell'asset (semplificazione dichiarata); quota = quella del
    punto di esaurimento, interpolata fra i waypoint, trattata come altezza sulla base (terreno non
    modellato); punto d'atterraggio = l'asset di base piu' vicino, a quota 0;
  * aereo in volo senza base raggiungibile in planata: PERSO (`FUEL_CRASH`): i tratti finiscono
    all'esaurimento e, dopo gli ingaggi, la salute e' portata a 0 con `Asset.apply_damage` (lo stesso
    canale del danno da combattimento, stato asset `Destroyed`) SENZA un `DamageEvent` nell'esito (non
    e' un colpo: nessun tiratore ne' arma); l'esito per asset e' DESTROYED con motivo FUEL_EXHAUSTED
    e (F6-B1) la postura `destroyed`.
Un asset il cui consumo cambia per effetto di un ingaggio (regime 'max', sotto) puo' esaurire prima
del punto calcolato a monte: limite noto, nessun ri-scheduling (v. sotto).

**Contabilita' (`F6_FUEL_PER_LEG`).** All'evento MOVEMENT dell'asset (fine dei suoi tratti troncati)
un `FuelEvent` per tratto che consuma, in ordine, applicato subito (`Fuel_Model.apply_fuel_event`);
dopo un evento esaurito nessun altro. Spento: un solo FuelEvent per asset sulla distanza dei tratti di
movimento, le attese non consumano (come la F5-C).

Regime (scelta dichiarata, la piu' semplice che distingua combattimento da crociera):
`'max'` se l'asset ha **combattuto** nella sessione — ha lanciato una salva, e' stato
bersaglio di una salva, o ha intercettato — altrimenti `'nominal'`, per i tratti di MOVIMENTO; le
attese sempre alla crociera (`Fuel_Model.HOLD_REGIME`). Per gli aerei 'max'
legge il profilo `attack` del loadout, per veicoli e navi il registro non distingue (v.
FUEL_FULL in `Asset/Mobile.py`). Tutto il movimento e' consumato al regime scelto: per chi ha
combattuto e' una sovrastima **pessimistica** del consumo (il tratto di crociera e'
contato a regime di combattimento), preferita a una ripartizione per intervalli che
richiederebbe di inventare quando comincia e finisce la manovra di combattimento. Se il
regime 'max' non e' ricavabile per l'asset si ricade su 'nominal'.

**Limiti dichiarati:**
- il vincolo e' calcolato a monte al regime di CROCIERA: per un aereo che combatte la contabilita' al
  regime 'max' puo' esaurire il carburante prima del punto di troncamento (`FuelEvent.exhausted` con
  `distance_covered < distance` sull'ultimo tratto) senza che il movimento sia ricalcolato (nessun
  ri-scheduling dopo gli ingaggi, P2/R4); per veicoli e navi i due regimi coincidono e il limite non
  si presenta;
- un asset distrutto a meta' rotta consuma comunque il tragitto (troncato) intero (il carburante di un
  relitto non ha conseguenze di campagna);
- un asset senza rotta (fermo) non produce FuelEvent; il carburante di partenza e il rifornimento non
  sono toccati (rifornimento: F8); bingo in volo con rientro: F6-B2 e F6-B2bis (sotto).

## Bingo (F6-B2 del piano della Missione, decisione 14 dell'utente; rientro rifatto dalla F6-B2bis)

Regola della F6-B2 (rientro rettilineo con la riserva), valida con `F6_BINGO_REVERSE_ROUTE` SPENTO; con
l'interruttore acceso (default) il rientro e' lungo la rotta a ritroso, v. il paragrafo F6-B2bis sotto.
Interruttore `F6_BINGO` (attivo). Per ogni aereo di una missione AEREA con `EndCriteria.bingo` (default
True) e con almeno una base aerea del suo lato fra le forze passate (`Mission_Adapter.air_base_points`;
"base idonea" = qualunque base aerea amica, come la planata della F6-A: l'idoneita' per tipo d'aereo non
e' modellata), il bingo e' calcolato A MONTE sui tratti che consumano, prima dell'esaurimento e dello
scheduler (`Fuel_Model.bingo_point`, alla crociera): il primo istante in cui il residuo basta appena per
rientrare in linea retta alla base piu' vicina con la riserva `Fuel_Model.BINGO_RESERVE` (stima). Se
l'aereo rientra con la riserva dalla fine dei suoi tratti nella sessione, nessun bingo. Altrimenti
(`_bingo_end`, `BingoEnd`):
  * i tratti oltre il bingo NON esistono: dal punto di bingo l'aereo vola in linea retta alla base piu'
    vicina (punto d'atterraggio = l'asset di base a quota 0, alla crociera dell'asset, come la planata)
    e resta A TERRA sulla base fino a fine sessione (programma `grounded` dall'atterraggio, bersaglio di
    superficie passivo, postura `parking_cold`); i tratti con il rientro vanno a scheduler e risolutore e
    al carburante (il rientro consuma: arriva con la riserva alla crociera);
  * dal bingo l'aereo NON lancia piu' salve offensive (fine di attivita' nota a monte, `until` del
    risolutore, come la durata massima della F6-B1), resta bersaglio e intercettore;
  * esito per asset BINGO all'istante del bingo (stato OPERATIONAL/DAMAGED), punti successivi non
    raggiunti; per la missione la regola unica della F6-B1 con il motivo ABORTED(BINGO) (a parita'
    d'istante dopo FUEL);
  * a secco anche sul rientro (carburante gia' insufficiente per raggiungere la base, es. al decollo):
    le regole della F6-A sui tratti col rientro (planata su una base raggiungibile, ABORTED(FUEL); altrimenti
    perso, DESTROYED/FUEL_EXHAUSTED); il motivo dell'asset e' l'ultimo fatto, FUEL_EXHAUSTED.
Senza base idonea, o con `bingo` False, nessun rientro: l'aereo vola fino all'esaurimento (F6-A). Terra e
mare non hanno bingo (fermi nel punto di esaurimento, F6-A).
Il bingo A PRIORI e' del pianificatore (`Mission_Adapter.check_mission_bingo`, non chiamato qui): stesso
criterio, quindi la missione che quel validatore rifiuta e' esattamente quella che qui torna al bingo.
Limiti: il bingo e' calcolato alla CROCIERA come l'esaurimento (un aereo che combatte consuma di piu' nella
contabilita' e puo' arrivare a secco prima della base senza ri-scheduling); rientro in linea retta senza
quota di rientro ne' terreno; la riserva e' unica per tutti gli aerei.

**Rientro lungo la rotta a ritroso (F6-B2bis, decisioni dell'utente del 2026-10-15, interruttore
`F6_BINGO_REVERSE_ROUTE`, attivo).** Il bingo e il rientro sono calcolati sulla missione INTERA
(`Mission_Adapter.airborne_legs`: gli stessi tratti del validatore, anche oltre la fine della sessione) con
la regola della missione (`Mission_Adapter.bingo_return_rule`, `Fuel_Model.bingo_point`):
  * il rientro ripercorre AL CONTRARIO i tratti di movimento gia' volati (il DES non devia le rotte negli
    ingaggi, quindi sono quelli pianificati fino al bingo), alle quote dei waypoint, senza le soste
    (WAIT/orbite non si ripercorrono), fino al DEPARTURE, dove atterra; partita in volo (`start_mode` AIR):
    fino al punto di comparsa, poi un tratto diretto alla base del lato piu' vicina a quel punto, a quota 0
    (la discesa e' sul tratto finale); senza base del lato nessun bingo (regole della F6-A, come prima);
  * missione ad ANELLO (`Mission_Adapter.is_loop_mission`, LAND sulla base del DEPARTURE): la via piu' breve
    fra il ritroso e il resto della rotta fino al LAND (tratti di movimento rimanenti, senza le soste);
  * il LAND su un'altra base (divert) non conta: la destinazione finale e' esclusa;
  * fabbisogno di bingo = `Fuel_Model.BINGO_RETURN_FACTOR` (1,2, stima dell'utente) x il carburante del
    ritorno alla crociera, al posto della riserva fissa; il rientro si consuma alla crociera;
  * un bingo che cadrebbe dopo la fine della sessione non c'e' nella sessione;
  * i tratti del rientro (`_return_legs`, la spezzata `BingoEnd.route` a velocita' costante) vanno a
    scheduler, risolutore e carburante come il rientro rettilineo; tutto il resto (nessuna salva offensiva
    dal bingo, bersaglio e intercettore, a terra `parking_cold` sulla base raggiunta, BINGO /
    ABORTED(BINGO), a secco sul rientro le regole della F6-A) e' invariato.
Spento: la regola rettilinea con la riserva qui sopra, esattamente come la F6-B2.
Limiti: idoneita' della base per tipo d'aereo non modellata (qualunque base aerea amica); consumo
deterministico alla crociera (lo stesso limite della F6-B2 per chi combatte); il rientro non evita le
minacce incontrate all'andata (le ripercorre); un tratto di rotta lungo e quasi rettilineo rende il
ritroso piu' lungo della retta, un percorso tortuoso molto di piu'.

## Sessione aperta (`SessionOrder.t_end is None`)

Regola conservativa: la durata **non si deduce**. Con `t_end` None il chiamante deve
passare `horizon` esplicito; con `t_end` valorizzato `horizon` e' ricavato (se passato
comunque deve coincidere). Nessuna durata di default inventata.

## Attivita' oltre la fine della sessione

Una salva lanciata poco prima della fine arriva comunque (payload congelato, R4): impatti e
risoluzioni possono cadere dopo `t_start + horizon`. L'esito non viene troncato (sarebbe
cancellare danni gia' decisi): il `t_end` del `SessionOutcome` e' esteso fino all'ultima
attivita', con un log. I contatti invece sono cercati solo dentro la sessione.

## Cosa NON fa
- Non costruisce `Theater_Session_Manager`, non legge/scrive `Campaign_State`.
- Non seleziona l'arma (lo fa la fire control iniettata), non rifornisce (munizioni o carburante), non ri-instrada le forze
  che si disingaggiano (restano solo segnalate nell'esito).
- Nessun componente LLM, in nessuna forma.
"""

import dataclasses
import heapq
import json
from dataclasses import dataclass
from math import sqrt
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Asset.Mobile import DEFAULT_DETECTION_RANGE_TYPE
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AbortReason,
    AssetEndReason,
    AssetMissionOutcome,
    AssetState,
    MissionOutcome,
    MissionStatus,
    TargetKind,
    check_mission_assets,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import (
    SessionOrder,
    SessionOutcome,
    assemble_session_outcome,
)
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Session_Simulator').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Tipi di evento di sessione, nell'ordine di risoluzione a parita' d'istante (v. docstring).
ENGAGEMENT_EVENT = 0
MOVEMENT_EVENT = 1

# Etichetta del primo elemento dell'event_id di un ingaggio (v. engagement_event_id).
ENGAGEMENT_EVENT_TAG = 'engagement'
# Tag dell'event_id del flusso casuale SEPARATO della tempra delle forze (soglia di rottura
# stocastica, 2026-09-29): stesse forze, flusso diverso da quello di rilevamento e danno.
TEMPER_EVENT_TAG = 'temper'

# Regimi di consumo (Mobile.FUEL_REGIMES).
CRUISE_REGIME = 'nominal'
COMBAT_REGIME = 'max'

# F6-A, due interruttori separati (come F5_PRESENCE/F5_WAITS di Mission_Adapter), cosi' che la
# fotografia attribuisca le differenze a una sola causa (v. "Carburante" nel docstring):
#   * `F6_FUEL_PER_LEG` (ATTIVO): un `FuelEvent` per tratto e consumo nel tempo delle soste alla
#     crociera. Spento: un solo FuelEvent per asset sulla distanza dei tratti di movimento, le soste
#     non consumano (come la F5-C).
#   * `F6_FUEL_CONSTRAINT` (ATTIVO): il carburante vincola movimento e contatti; tratti troncati
#     all'esaurimento calcolato a monte, terra/mare fermi e presenti nel punto, aereo in planata su una
#     base o perso. Spento: nessun vincolo, l'asset a secco continua (come prima, esperimento E5).
F6_FUEL_PER_LEG = True
F6_FUEL_CONSTRAINT = True

# F6-B1, due interruttori separati (stessa ragione di quelli della F6-A):
#   * `F6_END_CRITERIA` (ATTIVO): i criteri di stato DICHIARATI in `EndCriteria` (winchester, soglia di
#     danno, bersaglio distrutto, durata massima) chiudono l'attivita' dell'asset (v. "Fine di
#     attivita' e stato di missione" nel docstring) e l'esito di missione segue la regola unica
#     DESTROYED > COMPLETED > ABORTED(motivo) > FAILED. Spento: i criteri non sono letti (come prima
#     della F6-B1). Nei default di `EndCriteria` nessuno di questi criteri e' attivo.
#   * `F6_DESTROYED_POSTURE` (ATTIVO): un asset DISTRUTTO a fine sessione ha postura
#     `Mission_Adapter.DESTROYED_POSTURE` nell'esito invece dell'etichetta di dominio. Spento: la
#     postura della F5-B/F6-A (`off_scene`, `Defense`, ...). Cambia solo `SessionOutcome.postures`.
F6_END_CRITERIA = True
F6_DESTROYED_POSTURE = True

# F6-B2, interruttore dedicato (stessa ragione dei precedenti):
#   * `F6_BINGO` (ATTIVO): bingo in volo con rientro (v. "Bingo" nel docstring): un aereo di una missione
#     con `EndCriteria.bingo` che arriva al bingo (`Fuel_Model.bingo_point`) torna alla base (dalla F6-B2bis
#     lungo la rotta a ritroso, `F6_BINGO_REVERSE_ROUTE`; senza, in linea retta alla base del lato piu'
#     vicina con la riserva `Fuel_Model.BINGO_RESERVE`), smette di lanciare salve offensive dal bingo, e
#     l'esito e' BINGO / ABORTED(BINGO). Spento: nessun bingo, l'aereo
#     vola fino all'esaurimento (come la F6-A/F6-B1). Il bingo A PRIORI (`Mission_Adapter.check_mission_bingo`)
#     e' del pianificatore e non dipende dall'interruttore.
F6_BINGO = True

# F6-B2bis, interruttore dedicato (stessa ragione dei precedenti), letto solo con `F6_BINGO` acceso:
#   * `F6_BINGO_REVERSE_ROUTE` (ATTIVO): rientro al bingo lungo la rotta percorsa A RITROSO fino al DEPARTURE
#     (partenza in volo: fino al punto di comparsa, poi diretto alla base del lato piu' vicina; anello: il
#     piu' breve fra ritroso e resto della rotta), fabbisogno `Fuel_Model.BINGO_RETURN_FACTOR` x il ritorno,
#     calcolato sulla missione intera (v. "Bingo" nel docstring). Spento: il rientro rettilineo con la
#     riserva `Fuel_Model.BINGO_RESERVE` della F6-B2, esattamente come prima. Il validatore
#     `Mission_Adapter.check_mission_bingo` segue lo stesso criterio con il suo parametro `reverse_route`.
F6_BINGO_REVERSE_ROUTE = True

# Esiti dell'esaurimento del carburante (F6-A, decisioni dell'utente).
FUEL_HALT = 'halt'      # terra/mare (o aereo ancora a terra): fermo e presente nel punto
FUEL_GLIDE = 'glide'    # aereo in volo: planata sulla base raggiungibile piu' vicina, poi a terra
FUEL_CRASH = 'crash'    # aereo in volo senza base raggiungibile in planata: perso


@dataclass(frozen=True)
class FuelEnd:
    """Fine del movimento di un asset per esaurimento del carburante (F6-A), calcolata a monte.

    Attributes:
        asset_id: id di dominio.
        kind: FUEL_HALT, FUEL_GLIDE o FUEL_CRASH.
        time/point: istante [s] e posizione (x, y, z) dell'esaurimento (`Fuel_Model.FuelExhaustion`).
        landing_time/landing_point: fine della planata sulla base (solo FUEL_GLIDE).
        on_ground: aereo fermo A TERRA nel punto (FUEL_HALT di un aereo: a terra all'esaurimento, o a
            quota <= 0, es. serbatoio vuoto al decollo).
    """
    asset_id: str
    kind: str
    time: float
    point: Tuple[float, float, float]
    landing_time: Optional[float] = None
    landing_point: Optional[Tuple[float, float, float]] = None
    on_ground: bool = False


@dataclass(frozen=True)
class BingoEnd:
    """Rientro di un aereo al bingo (F6-B2, F6-B2bis), calcolato a monte.

    Attributes:
        asset_id: id di dominio.
        time/point: istante [s] e posizione (x, y, z) del bingo (`Fuel_Model.BingoPoint`).
        landing_point: punto d'atterraggio, l'ultimo di `route` (`Fuel_Model.BingoPoint.base`).
        landing_time: fine del rientro alla crociera dell'asset.
        route: punti del rientro dal punto di bingo a `landing_point` compresi (F6-B2: la retta (point,
            landing_point); F6-B2bis: la rotta a ritroso o, sull'anello, il resto della rotta), volati a
            velocita' costante; vuota = (point, landing_point).
    """
    asset_id: str
    time: float
    point: Tuple[float, float, float]
    landing_point: Tuple[float, float, float]
    landing_time: float
    route: Tuple[Tuple[float, float, float], ...] = ()


# ── IDENTITA' ─────────────────────────────────────────────────────────────────

def _domain_id(obj) -> Optional[str]:
    """Id di dominio: stesso criterio di Engagement_Resolver/Contact_Scheduler (id, poi name).

    Deve coincidere con quello del risolutore, perche' e' la chiave dei `ForceOutcome` e di
    `committed`: un criterio diverso qui farebbe ignorare in silenzio `committed`.
    """
    for attribute in ('id', 'name'):
        value = getattr(obj, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


def _as_block(item):
    """`Block` o `BlockItem` (che lo incapsula in `.block`): stesso criterio dello scheduler."""
    return getattr(item, 'block', item)


def engagement_event_id(*force_ids: str) -> str:
    """`event_id` dell'RNG per l'ingaggio fra le forze date (2 o piu', una componente).

    JSON di `['engagement', id_1, id_2, ...]` con gli id ORDINATI: funzione pura
    dell'INSIEME degli id — indipendente dall'ordine in cui sono passati e quindi
    dall'ordine con cui le forze arrivano a `run_session` — e non ambigua anche con id che
    contengono separatori.

    Raises:
        ValueError: meno di due id, id non stringa o vuoti, id ripetuti.
    """
    if len(force_ids) < 2:
        raise ValueError(f"an engagement needs at least two force ids, got {force_ids!r}")

    if any(not isinstance(force_id, str) or not force_id for force_id in force_ids):
        raise ValueError(f"force ids must be non-empty strings, got {force_ids!r}")

    if len(set(force_ids)) != len(force_ids):
        raise ValueError(f"force ids must be distinct, got {force_ids!r}")

    return json.dumps([ENGAGEMENT_EVENT_TAG, *sorted(force_ids)],
                      ensure_ascii=True, separators=(',', ':'))


def temper_event_id(*force_ids: str) -> str:
    """`event_id` del flusso della tempra per l'ingaggio fra le forze date.

    Stessa forma e stessi vincoli di `engagement_event_id`, tag diverso: il flusso della
    tempra e' indipendente da quello dell'ingaggio, cosi' che estrarre la tempra non sposti
    le estrazioni di rilevamento e danno.
    """
    engagement_event_id(*force_ids)  # stessa validazione

    return json.dumps([TEMPER_EVENT_TAG, *sorted(force_ids)],
                      ensure_ascii=True, separators=(',', ':'))


# ── PREPARAZIONE ──────────────────────────────────────────────────────────────

def _session_horizon(order: SessionOrder, horizon: Optional[float]) -> float:
    """Durata [s] della sessione (v. "Sessione aperta" nel docstring del modulo)."""
    if horizon is not None:
        if isinstance(horizon, bool) or not isinstance(horizon, (int, float)) or horizon < 0:
            raise ValueError(f"horizon must be a non-negative number, got {horizon!r}")

        horizon = float(horizon)

    if order.t_end is None:
        if horizon is None:
            raise ValueError(f"session {order.session_id!r} is open (t_end is None): "
                             f"an explicit horizon is required")
        return horizon

    declared = order.t_end - order.t_start

    if horizon is not None and abs(horizon - declared) > CS.TIME_EPS:
        raise ValueError(f"horizon ({horizon}) disagrees with the order interval ({declared})")

    return declared


def _collect_forces(order: SessionOrder, forces_a: Iterable, forces_b: Iterable):
    """Normalizza le forze dei due lati e costruisce la mappa asset -> blocco.

    Returns:
        (items_a, items_b, blocks, owner): gli oggetti come passati (per lo scheduler), i
        blocchi per id, e `{asset_id: (lato, block_id)}` con lato 0 (A) o 1 (B). Le forze
        d'ingaggio (missioni) le ricava `_engagement_forces`.

    Raises:
        ValueError: forza senza id, forza ripetuta o su entrambi i lati, forza non elencata
            in `order.force_ids` (se non vuoto), asset appartenente a due forze.
    """
    items = (list(forces_a or []), list(forces_b or []))
    blocks: Dict[str, object] = {}
    owner: Dict[str, Tuple[int, str]] = {}

    for side_index, side_items in enumerate(items):
        for item in side_items:
            block = _as_block(item)
            force_id = _domain_id(block)

            if force_id is None:
                raise ValueError("every force must have a domain id (id or name)")

            if force_id in blocks:
                raise ValueError(f"force {force_id!r} is passed more than once")

            if order.force_ids and force_id not in order.force_ids:
                raise ValueError(f"force {force_id!r} is not in the order's force_ids {order.force_ids}")

            blocks[force_id] = block

            for asset in (getattr(block, 'assets', None) or {}).values():
                asset_id = _domain_id(asset)

                if asset_id is None:
                    continue

                if asset_id in owner:
                    raise ValueError(f"asset {asset_id!r} belongs to both {owner[asset_id][1]!r} "
                                     f"and {force_id!r}")

                owner[asset_id] = (side_index, force_id)

    if order.committed is not None:
        unknown = sorted(set(order.committed) - set(blocks))

        if unknown:
            logger.warning(f"run_session: committed forces {unknown} match no force passed "
                           f"(force ids are {sorted(blocks)}): their restriction is ignored")

    return items[0], items[1], blocks, owner


def _legs_distance(legs) -> float:
    """Lunghezza [m] del tragitto: somma delle lunghezze dei tratti."""
    total = 0.0

    for leg in legs:
        total += sqrt(sum((e - s) ** 2 for s, e in zip(leg.p_start, leg.p_end)))

    return total


def _group_windows(windows, owner) -> Dict[Tuple[str, str], List[CS.ContactWindow]]:
    """Finestre raggruppate per coppia (forza lato A, forza lato B), ordine preservato."""
    groups: Dict[Tuple[str, str], List[CS.ContactWindow]] = {}

    for window in windows:
        own_a = owner.get(window.asset_a_id)
        own_b = owner.get(window.asset_b_id)

        if own_a is None or own_b is None:
            logger.debug(f"run_session: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                         f"involves an asset of no known force, skipped")
            continue

        if own_a[0] != 0 or own_b[0] != 1:
            # Non puo' accadere con schedule_contacts (itera A x B), ma il raggruppamento non
            # deve mai scambiare i lati in silenzio.
            logger.warning(f"run_session: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                           f"does not go from side A to side B, skipped")
            continue

        groups.setdefault((own_a[1], own_b[1]), []).append(window)

    return groups


def _connected_components(groups: Mapping[Tuple[str, str], List[CS.ContactWindow]],
                          domain_of: Optional[Mapping[str, str]] = None
                          ) -> List[Tuple[Tuple[str, ...], List[CS.ContactWindow]]]:
    """Componenti connesse del grafo delle forze, con le finestre di ciascuna.

    Nodi: le forze che compaiono in almeno una coppia di `groups`; archi: le coppie con
    almeno una finestra e (dal 2026-10-11, con `domain_of`) le coppie di forze dello stesso
    dominio di coordinamento, perche' la condivisione del dominio vale dentro una run (v.
    "Dominio di coordinamento"). Visita in ampiezza deterministica: si parte dalle forze in
    ordine di id e i vicini sono visitati in ordine di id — mai l'ordine di un dizionario.

    Returns:
        `[(force_ids ordinati, finestre), ...]`, componenti ordinate per id minimo. Le
        finestre di una componente sono quelle di tutte le sue coppie, concatenate
        nell'ordine delle coppie ordinate (il risolutore le riordina comunque in modo
        canonico, v. `Engagement_Resolver._detect`).
    """
    neighbours: Dict[str, set] = {}

    for force_a, force_b in groups:
        neighbours.setdefault(force_a, set()).add(force_b)
        neighbours.setdefault(force_b, set()).add(force_a)

    if domain_of:
        by_domain: Dict[str, List[str]] = {}

        for force_id in sorted(neighbours):
            by_domain.setdefault(domain_of.get(force_id, force_id), []).append(force_id)

        for same in by_domain.values():
            for force_a, force_b in zip(same, same[1:]):
                neighbours[force_a].add(force_b)
                neighbours[force_b].add(force_a)

    component_of: Dict[str, int] = {}
    members: List[List[str]] = []

    for start in sorted(neighbours):
        if start in component_of:
            continue

        index = len(members)
        component_of[start] = index
        frontier = [start]
        found = [start]

        while frontier:
            following = []

            for force_id in frontier:
                for other in sorted(neighbours[force_id]):
                    if other not in component_of:
                        component_of[other] = index
                        found.append(other)
                        following.append(other)

            frontier = following

        members.append(sorted(found))

    windows: List[List[CS.ContactWindow]] = [[] for _ in members]

    for pair in sorted(groups):
        windows[component_of[pair[0]]].extend(groups[pair])

    return [(tuple(ids), group) for ids, group in zip(members, windows)]


def _engaged_assets(result: ER.EngagementResult) -> set:
    """Asset che hanno combattuto: tiratori, bersagli di salve, intercettori."""
    engaged = set()

    for salvo in result.salvos:
        engaged.add(salvo.shooter_id)
        engaged.add(salvo.target_id)

    for event in result.ammunition_events:
        engaged.add(event.asset_id)

    for event in result.interception_events:
        engaged.add(event.asset_id)

    return engaged


def _build_fuel(asset, distance: float, time: float, regime: str, provenance: str):
    """`build_fuel_event` al regime dato, con ricaduta su 'nominal' (v. docstring)."""
    event = FM.build_fuel_event(asset, distance, time=time, regime=regime, provenance=provenance)

    if event is None and regime != CRUISE_REGIME:
        logger.debug(f"run_session: no '{regime}' fuel autonomy for {_domain_id(asset)!r}, "
                     f"falling back to '{CRUISE_REGIME}'")
        event = FM.build_fuel_event(asset, distance, time=time, regime=CRUISE_REGIME,
                                    provenance=provenance)

    return event


def _build_leg_fuel(asset, leg, regime: str, provenance: str):
    """`build_leg_fuel_event` al regime dato, con la stessa ricaduta su 'nominal' di `_build_fuel`
    (le soste consumano comunque alla crociera, `Fuel_Model.HOLD_REGIME`)."""
    event = FM.build_leg_fuel_event(asset, leg, regime=regime, provenance=provenance)

    if event is None and regime != CRUISE_REGIME and not FM.is_stationary(leg):
        logger.debug(f"run_session: no '{regime}' fuel autonomy for {_domain_id(asset)!r}, "
                     f"falling back to '{CRUISE_REGIME}'")
        event = FM.build_leg_fuel_event(asset, leg, regime=CRUISE_REGIME, provenance=provenance)

    return event


# ── CARBURANTE: ESAURIMENTO A MONTE (F6-A) ────────────────────────────────────

def _consuming_legs(asset_id: str, legs, grounded: CS.GroundedSchedule) -> List[CS.Leg]:
    """Tratti di movimento che CONSUMANO (v. "Carburante" nel docstring del modulo).

    Esclusi i tratti degeneri (durata nulla) e i tratti FERMI di un aereo A TERRA (sosta sul
    parcheggio prima del decollo o dopo l'atterraggio: motori spenti, nessun consumo). Con
    `F6_FUEL_PER_LEG` spento i tratti fermi non consumano mai (come prima della F6-A)."""
    consuming = []

    for leg in legs:
        stationary = FM.is_stationary(leg)

        if stationary and (leg.duration <= CS.TIME_EPS or not F6_FUEL_PER_LEG
                           or grounded.at(asset_id, 0.5 * (leg.t_start + leg.t_end))):
            continue

        consuming.append(leg)

    return consuming


def _moving_speed(legs, time: float) -> Optional[float]:
    """Velocita' [m/s] del tratto di movimento in corso (o dell'ultimo prima) a `time`; in mancanza
    quella del primo tratto di movimento; None se l'asset non ha tratti di movimento."""
    moving = [leg for leg in legs if not FM.is_stationary(leg) and leg.duration > CS.TIME_EPS]
    before = [leg for leg in moving if leg.t_start <= time + CS.TIME_EPS]
    leg = before[-1] if before else (moving[0] if moving else None)

    if leg is None:
        return None

    return sqrt(sum((e - s) ** 2 for s, e in zip(leg.p_start, leg.p_end))) / leg.duration


def _fuel_end(asset, asset_id: str, domain: str, consuming, grounded: CS.GroundedSchedule,
              air_bases) -> Optional[FuelEnd]:
    """Esaurimento del carburante dell'asset sui suoi tratti e suo esito (F6-A), o None se basta.

    Terra/mare, o aereo ancora A TERRA all'esaurimento (o a quota <= 0): FUEL_HALT (fermo nel punto;
    l'aereo a terra, `on_ground`). Aereo in volo:
    planata in linea retta sulla base del suo lato (`air_bases`, `Mission_Adapter.air_base_points`)
    piu' vicina entro il raggio di planata (`Fuel_Model.nearest_reachable_base`), FUEL_GLIDE; nessuna
    base raggiungibile: FUEL_CRASH. Punto d'atterraggio = la posizione dell'asset di base piu' vicino,
    a quota 0 (il terreno non e' modellato). Velocita' di planata = la crociera dell'asset (in mancanza
    quella del tratto in corso): semplificazione dichiarata."""
    exhaustion = FM.fuel_exhaustion(asset, consuming, regime=CRUISE_REGIME)

    if exhaustion is None:
        return None

    if domain != 'air':
        return FuelEnd(asset_id, FUEL_HALT, exhaustion.time, exhaustion.point)

    if grounded.at(asset_id, exhaustion.time) or exhaustion.point[2] <= 0.0:
        # A terra (o a quota nulla, es. serbatoio vuoto al decollo): resta fermo a terra nel punto.
        return FuelEnd(asset_id, FUEL_HALT, exhaustion.time, exhaustion.point, on_ground=True)

    base = FM.nearest_reachable_base(exhaustion.point, air_bases)

    if base is None:
        return FuelEnd(asset_id, FUEL_CRASH, exhaustion.time, exhaustion.point)

    landing = (base[0], base[1], 0.0)
    speed = FM.cruise_speed(asset) or _moving_speed(consuming, exhaustion.time)
    length = sqrt(sum((e - s) ** 2 for s, e in zip(exhaustion.point, landing)))
    duration = length / speed if speed else 0.0
    return FuelEnd(asset_id, FUEL_GLIDE, exhaustion.time, exhaustion.point,
                   landing_time=exhaustion.time + duration, landing_point=landing)


def _truncate_at_fuel_end(legs, end: FuelEnd, t0: float, session_end: float) -> List[CS.Leg]:
    """Tratti di presenza dell'asset fino all'esaurimento, poi l'esito (F6-A): fermo nel punto fino
    alla fine della sessione (FUEL_HALT), planata e sosta a terra sulla base (FUEL_GLIDE), nulla
    (FUEL_CRASH). Senza tratti degeneri; lista vuota = l'asset non esiste nella sessione."""
    kept = [leg for leg in CS.clamp_legs(legs, t0, end.time) if leg.duration > CS.TIME_EPS]

    if end.kind == FUEL_HALT:
        kept.append(CS.Leg(t_start=end.time, t_end=float(session_end), p_start=end.point, p_end=end.point))
    elif end.kind == FUEL_GLIDE:
        kept.append(CS.Leg(t_start=end.time, t_end=end.landing_time, p_start=end.point, p_end=end.landing_point))
        kept.append(CS.Leg(t_start=end.landing_time, t_end=max(float(session_end), end.landing_time),
                           p_start=end.landing_point, p_end=end.landing_point))

    return [leg for leg in CS.clamp_legs(kept, t0, session_end) if leg.duration > CS.TIME_EPS]


def _grounded_after_fuel(grounded: CS.GroundedSchedule, ends: Mapping[str, FuelEnd]) -> CS.GroundedSchedule:
    """Programma degli aerei a terra corretto per gli esaurimenti (F6-A): gli intervalli a terra che
    cominciano dopo l'esaurimento (atterraggio pianificato mai raggiunto) cadono; un aereo a terra
    all'esaurimento ci resta; un aereo in planata e' a terra dall'atterraggio sulla base."""
    if not ends:
        return grounded

    intervals = {asset_id: list(grounded.intervals(asset_id)) for asset_id in grounded.ids()}

    for asset_id, end in ends.items():
        spans = []

        for lo, hi in intervals.get(asset_id, ()):
            if lo <= end.time < hi:
                spans.append((lo, float('inf')))
            elif lo < end.time:
                spans.append((lo, hi))

        if end.kind == FUEL_GLIDE:
            spans.append((end.landing_time, float('inf')))
        elif end.on_ground:
            spans.append((end.time, float('inf')))

        if spans:
            intervals[asset_id] = spans
        else:
            intervals.pop(asset_id, None)

    return CS.GroundedSchedule(intervals)


def _postures_after_fuel(postures: Dict[str, str], ends: Mapping[str, FuelEnd], domains: Mapping[str, str],
                         mission_types: Mapping[str, str], grounded: CS.GroundedSchedule,
                         session_end: float) -> Dict[str, str]:
    """Postura a fine sessione degli asset a secco (F6-A): aereo perso `OFF_SCENE_POSTURE`
    (dalla F6-B1, con `F6_DESTROYED_POSTURE` attivo, `run_session` la sostituisce con `destroyed`, come
    per le distruzioni in combattimento), a terra
    `PARKED_POSTURE`, in planata il tipo di missione; terra/mare fermi in `Defense`."""
    for asset_id, end in ends.items():
        if asset_id not in postures:
            continue

        if end.kind == FUEL_CRASH:
            postures[asset_id] = MA.OFF_SCENE_POSTURE
        elif grounded.at(asset_id, session_end):
            postures[asset_id] = MA.PARKED_POSTURE
        elif end.kind == FUEL_GLIDE:
            postures[asset_id] = mission_types[asset_id]
        else:
            postures[asset_id] = MA.SEA_DEFENSE_POSTURE if domains[asset_id] == 'sea' else MA.GROUND_DEFENSE_POSTURE

    return postures


# ── BINGO: RIENTRO IN VOLO (F6-B2) ────────────────────────────────────────────

def _bingo_end(asset, asset_id: str, consuming, air_bases, rule: Optional[FM.ReturnRule] = None) -> Optional[BingoEnd]:
    """Bingo dell'aereo sui suoi tratti che consumano e suo rientro, o None se non arriva al bingo (o il
    controllo non e' possibile).

    `rule` None (F6-B2): rientro in linea retta dal punto di bingo alla base del lato piu' vicina con la
    riserva. `rule` dato (F6-B2bis): rientro lungo la spezzata `Fuel_Model.BingoPoint.route` (rotta a
    ritroso, o resto della rotta sull'anello), e `consuming` sono i tratti della missione intera. In
    entrambi i casi alla crociera dell'asset (in mancanza quella del tratto in corso), come la planata della
    F6-A."""
    bingo = FM.bingo_point(asset, consuming, air_bases, rule=rule)

    if bingo is None:
        return None

    speed = FM.cruise_speed(asset) or _moving_speed(consuming, bingo.time)
    duration = bingo.return_length / speed if speed else 0.0
    return BingoEnd(asset_id, bingo.time, bingo.point, bingo.base, bingo.time + duration, bingo.route)


def _return_legs(end: BingoEnd) -> List[CS.Leg]:
    """Tratti del rientro al bingo lungo `end.route`, a velocita' costante da `end.time` a `end.landing_time`
    (istanti proporzionali alla lunghezza percorsa). Nessun tratto se il rientro e' nullo."""
    points = end.route or (end.point, end.landing_point)
    lengths = [sqrt(sum((e - s) ** 2 for s, e in zip(a, b))) for a, b in zip(points, points[1:])]
    total = sum(lengths)

    if total <= 0.0:
        return []

    legs, done = [], 0.0

    for (a, b), length in zip(zip(points, points[1:]), lengths):
        t_start = end.time + (end.landing_time - end.time) * done / total
        done += length
        t_end = end.landing_time if done >= total else end.time + (end.landing_time - end.time) * done / total
        legs.append(CS.Leg(t_start=t_start, t_end=t_end, p_start=tuple(a), p_end=tuple(b)))

    return legs


def _legs_after_bingo(legs, end: BingoEnd, t0: float, session_end: float, park: bool) -> List[CS.Leg]:
    """Tratti dell'asset fino al bingo, poi il rientro sulla base (`_return_legs`: la retta della F6-B2 o la
    spezzata della F6-B2bis) e, con `park` (tratti di presenza), la sosta a terra sulla base fino alla fine
    della sessione. Senza tratti degeneri."""
    kept = [leg for leg in CS.clamp_legs(legs, t0, end.time) if leg.duration > CS.TIME_EPS]
    kept.extend(_return_legs(end))

    if park:
        kept.append(CS.Leg(t_start=end.landing_time, t_end=max(float(session_end), end.landing_time),
                           p_start=end.landing_point, p_end=end.landing_point))

    return [leg for leg in CS.clamp_legs(kept, t0, session_end) if leg.duration > CS.TIME_EPS]


def _grounded_after_bingo(grounded: CS.GroundedSchedule, ends: Mapping[str, BingoEnd]) -> CS.GroundedSchedule:
    """Programma degli aerei a terra corretto per i rientri al bingo (F6-B2): gli intervalli a terra che
    cominciano dopo il bingo (atterraggio pianificato mai raggiunto) cadono; l'aereo e' a terra sulla base
    dall'atterraggio del rientro."""
    if not ends:
        return grounded

    intervals = {asset_id: list(grounded.intervals(asset_id)) for asset_id in grounded.ids()}

    for asset_id, end in ends.items():
        spans = [(lo, min(hi, end.time)) for lo, hi in intervals.get(asset_id, ()) if lo < end.time]
        spans.append((end.landing_time, float('inf')))
        intervals[asset_id] = spans

    return CS.GroundedSchedule(intervals)


def _postures_after_bingo(postures: Dict[str, str], ends: Mapping[str, BingoEnd], mission_types: Mapping[str, str],
                          grounded: CS.GroundedSchedule, session_end: float) -> Dict[str, str]:
    """Postura a fine sessione degli aerei rientrati al bingo (F6-B2): a terra sulla base `PARKED_POSTURE`,
    ancora in volo verso la base il tipo di missione (un esaurimento successivo la corregge dopo, F6-A)."""
    for asset_id, end in ends.items():
        if asset_id in postures:
            postures[asset_id] = MA.PARKED_POSTURE if grounded.at(asset_id, session_end) else mission_types[asset_id]

    return postures


# ── FINE DI ATTIVITA' (F6-B1) ─────────────────────────────────────────────────

# Precedenza a parita' d'istante fra le fini di attivita' di un asset (scelta dichiarata, conta solo
# per fini simultanee): danno, winchester, bersaglio distrutto, durata.
_ACTIVITY_ORDER = (AssetEndReason.DAMAGE, AssetEndReason.WINCHESTER, AssetEndReason.TARGET_DESTROYED,
                   AssetEndReason.MAX_DURATION)
# Motivi di fine di un asset che fanno ABORTIRE la missione e il motivo d'aborto corrispondente.
# L'ordine e' la precedenza a parita' d'istante (F6-B2: il bingo subito dopo il carburante esaurito).
_ABORT_REASON_OF = {AssetEndReason.FUEL_EXHAUSTED: AbortReason.FUEL,
                    AssetEndReason.BINGO: AbortReason.BINGO,
                    AssetEndReason.WINCHESTER: AbortReason.AMMUNITION,
                    AssetEndReason.DAMAGE: AbortReason.DAMAGE}


@dataclass(frozen=True)
class ActivityPlan:
    """Criteri di fine di attivita' di un asset di missione, letti da `EndCriteria` (F6-B1).

    Attributes:
        asset_id/mission_id: id di dominio.
        winchester_weapons: voci della scorta dell'asset nelle categorie del criterio winchester (vuota
            = criterio non attivo per l'asset).
        damage_threshold: soglia di danno dichiarata, None = non attiva.
        target_ids: asset bersaglio della missione (vuoto = criterio non attivo o non rappresentabile).
        static_end: fine nota prima di ogni ingaggio, `(istante, AssetEndReason)`: durata massima
            (partenza della missione + `max_duration_s`) o winchester gia' all'inizio (alla partenza);
            None se nessuna.
    """
    asset_id: str
    mission_id: str
    winchester_weapons: frozenset = frozenset()
    damage_threshold: Optional[float] = None
    target_ids: frozenset = frozenset()
    static_end: Optional[Tuple[float, AssetEndReason]] = None


def _mission_target_ids(mission, blocks: Mapping[str, object], mission_of: Mapping[str, object],
                        assets: Mapping[str, object]) -> frozenset:
    """Asset bersaglio della missione per il criterio `target_destroyed` (F6-B1).

    ASSET: l'asset `target_id`. GROUP: gli asset del blocco `target_id` fra quelli passati, oppure della
    missione `target_id` (un gruppo di missione), oppure l'asset `target_id`. POINT/AREA: il bersaglio
    non e' un asset del modello (bersagli espliciti: F7), criterio non rappresentabile (warning).
    Vuoto (con un warning) se l'id non corrisponde a nulla fra le forze passate.
    """
    target = mission.target

    if target.kind not in (TargetKind.ASSET, TargetKind.GROUP):
        logger.warning(f"run_session: mission {mission.mission_id!r} declares target_destroyed on a "
                       f"{target.kind.name} target: not representable before F7 (explicit targets), ignored")
        return frozenset()

    target_id = target.target_id

    if target.kind is TargetKind.GROUP and target_id in blocks:
        return frozenset(asset_id for asset_id in (_domain_id(a) for a in (getattr(blocks[target_id], 'assets', None)
                                                                          or {}).values())
                         if asset_id is not None)

    if target.kind is TargetKind.GROUP and target_id in mission_of:
        return frozenset(mission_of[target_id].asset_ids)

    if target_id in assets:
        return frozenset((target_id,))

    logger.warning(f"run_session: mission {mission.mission_id!r}: target {target_id!r} matches no asset, "
                   f"block or mission passed: target_destroyed ignored")
    return frozenset()


def _winchester_weapons(asset, asset_id: str, domain: str, categories) -> frozenset:
    """Voci della scorta per arma dell'asset nelle categorie `categories` del registro d'arma del suo
    dominio (`Fire_Control.weapon_category`). Vuota, con un warning, se l'asset non ha scorta per arma,
    non ha armi di quelle categorie, o ne ha una NON MODELLATA (contata a unita', senza vincolo di
    scorta: non si esaurisce mai, quindi il criterio non puo' scattare)."""
    stores = getattr(asset, 'stores', None)
    wanted = set(categories)

    if not isinstance(stores, Mapping):
        logger.warning(f"run_session: asset {asset_id!r} has no per-weapon stores: winchester ignored")
        return frozenset()

    unmodelled = [weapon for weapon in (getattr(asset, 'unmodelled_weapons', None) or ())
                  if FC.weapon_category(domain, weapon) in wanted]

    if unmodelled:
        logger.warning(f"run_session: asset {asset_id!r} has unmodelled weapons {sorted(unmodelled)} in the "
                       f"winchester categories {sorted(wanted)}: they never run out, winchester ignored")
        return frozenset()

    weapons = frozenset(weapon for weapon in stores if FC.weapon_category(domain, weapon) in wanted)

    if not weapons:
        logger.warning(f"run_session: asset {asset_id!r} has no weapon of the winchester categories "
                       f"{sorted(wanted)}: winchester ignored")

    return weapons


def _activity_plans(order: SessionOrder, movement_of: Mapping[str, object], mission_of: Mapping[str, object],
                    assets: Mapping[str, object], blocks: Mapping[str, object]) -> Dict[str, ActivityPlan]:
    """Piani di fine di attivita' degli asset delle missioni che dichiarano un criterio di stato o una
    durata (F6-B1). Vuoto con `F6_END_CRITERIA` spento o senza criteri dichiarati (i default)."""
    if not F6_END_CRITERIA:
        return {}

    plans: Dict[str, ActivityPlan] = {}

    for mission in order.missions:
        criteria = mission.end_criteria

        if not (criteria.winchester or criteria.damage_threshold is not None or criteria.target_destroyed
                or criteria.max_duration_s is not None):
            continue

        targets = _mission_target_ids(mission, blocks, mission_of, assets) if criteria.target_destroyed \
            else frozenset()

        for asset_id in mission.asset_ids:
            movement = movement_of.get(asset_id)
            asset = assets.get(asset_id)

            if movement is None or asset is None:
                continue

            weapons = _winchester_weapons(asset, asset_id, mission.domain, criteria.winchester) \
                if criteria.winchester else frozenset()
            ends = []

            if criteria.max_duration_s is not None:
                ends.append((movement.start + criteria.max_duration_s, AssetEndReason.MAX_DURATION))

            stores = getattr(asset, 'stores', None) or {}

            if weapons and all(stores.get(weapon, 0) <= 0 for weapon in weapons):
                # Gia' senza le armi del criterio alla partenza: fine di attivita' alla partenza.
                ends.append((movement.start, AssetEndReason.WINCHESTER))

            static_end = min(ends, key=lambda end: (end[0], _ACTIVITY_ORDER.index(end[1]))) if ends else None
            plans[asset_id] = ActivityPlan(asset_id, mission.mission_id, weapons, criteria.damage_threshold,
                                           targets, static_end)

    return plans


def _known_destructions(results, assets: Mapping[str, object], t0: float,
                        fuel_ends: Mapping[str, FuelEnd]) -> Dict[str, float]:
    """`{asset_id: istante}` delle distruzioni note: in combattimento (ingaggi gia' risolti) o gia'
    distrutti all'inizio (`_destruction_times`), e i persi per carburante (FUEL_CRASH, istante noto a
    monte)."""
    known = _destruction_times(results, assets, t0)

    for asset_id, end in fuel_ends.items():
        if end.kind == FUEL_CRASH:
            known[asset_id] = min(end.time, known.get(asset_id, end.time))

    return known


def _activity_criteria(plans: Mapping[str, ActivityPlan], known: Optional[Mapping[str, float]]
                       ) -> Dict[str, ER.ActivityCriteria]:
    """I criteri nella forma del risolutore (`ER.ActivityCriteria`) per un ingaggio, con le distruzioni
    dei bersagli gia' note (`known`, None se nessun piano ha bersagli)."""
    criteria = {}

    for asset_id, plan in plans.items():
        destroyed = {target_id: known[target_id] for target_id in plan.target_ids if target_id in known} \
            if known is not None and plan.target_ids else {}
        criteria[asset_id] = ER.ActivityCriteria(
            winchester_weapons=plan.winchester_weapons, damage_threshold=plan.damage_threshold,
            target_ids=plan.target_ids, destroyed_targets=destroyed,
            until=plan.static_end[0] if plan.static_end is not None else None)

    return criteria


def _targets_destroyed_time(target_ids, destroyed: Mapping[str, float]) -> Optional[float]:
    """Istante in cui tutti i bersagli sono distrutti (l'ultima distruzione), None se qualcuno non lo e'
    o non ci sono bersagli."""
    if not target_ids or any(target_id not in destroyed for target_id in target_ids):
        return None

    return max(destroyed[target_id] for target_id in target_ids)


def _activity_ends(plans: Mapping[str, ActivityPlan], movement_of: Mapping[str, object], results,
                   destroyed: Mapping[str, float]) -> Tuple[Dict[str, Tuple[float, AssetEndReason]],
                                                            Dict[str, Optional[float]]]:
    """Fine di attivita' di ogni asset con un piano (la prima fra: fine nota a monte, winchester o danno
    scattati negli ingaggi, bersagli tutti distrutti) e istante di distruzione dei bersagli per missione.

    Il bersaglio distrutto e' valutato QUI sulle distruzioni dell'intera sessione (`destroyed`), non
    sulle fini del risolutore: un ingaggio risolto prima puo' non sapere di una distruzione avvenuta in
    un ingaggio risolto dopo (limite dichiarato del risolutore, v. docstring); l'esito usa il dato
    completo. La fine per bersaglio distrutto non e' anteriore alla partenza della missione.
    """
    dynamic: Dict[str, Tuple[float, AssetEndReason]] = {}

    for result in results:
        if result is None:
            continue

        for event in result.activity_ends:
            if event.reason == ER.ACTIVITY_TARGET_DESTROYED:
                continue

            reason = AssetEndReason(event.reason)
            known = dynamic.get(event.asset_id)

            if known is None or (event.time, _ACTIVITY_ORDER.index(reason)) < (known[0], _ACTIVITY_ORDER.index(known[1])):
                dynamic[event.asset_id] = (event.time, reason)

    target_times: Dict[str, Optional[float]] = {}
    ends: Dict[str, Tuple[float, AssetEndReason]] = {}

    for asset_id, plan in plans.items():
        if plan.target_ids and plan.mission_id not in target_times:
            target_times[plan.mission_id] = _targets_destroyed_time(plan.target_ids, destroyed)

        candidates = [end for end in (plan.static_end, dynamic.get(asset_id)) if end is not None]
        target_time = target_times.get(plan.mission_id) if plan.target_ids else None

        if target_time is not None:
            candidates.append((max(target_time, movement_of[asset_id].start), AssetEndReason.TARGET_DESTROYED))

        if candidates:
            ends[asset_id] = min(candidates, key=lambda end: (end[0], _ACTIVITY_ORDER.index(end[1])))

    return ends, target_times


def _check_missions(order: SessionOrder, blocks: Mapping[str, object]) -> None:
    """Ogni missione si riferisce a un blocco passato, i suoi asset gli appartengono e nessun suo
    tratto e' piu' veloce del mezzo piu' lento (regola A, `Mission_Adapter.check_mission_speed`)."""
    for mission in order.missions:
        block = blocks.get(mission.block_id)

        if block is None:
            raise ValueError(f"mission {mission.mission_id!r}: block {mission.block_id!r} is not among the "
                             f"forces passed ({sorted(blocks)})")

        check_mission_assets(mission, block)
        assets = {_domain_id(asset): asset for asset in (getattr(block, 'assets', None) or {}).values()}
        MA.check_mission_speed(mission, assets, order.t_start)

        if mission.mission_id in blocks:
            raise ValueError(f"mission {mission.mission_id!r}: its id is also the id of a block passed; "
                             f"missions and blocks are both engagement forces, their ids must differ")


def _engagement_forces(order: SessionOrder, blocks: Mapping[str, object],
                       block_owner: Mapping[str, Tuple[int, str]]):
    """Le forze d'ingaggio della sessione (F4b, v. "La missione come unita' d'ingaggio").

    Per ogni blocco, in ordine di id: una `MissionForce` per missione (nell'ordine dell'ordine di
    sessione) e, se restano asset senza missione, la vista residua con l'id del blocco; un blocco
    senza missioni e' passato tale e quale.

    Returns:
        (forces, owner): `{force_id: forza}` e `{asset_id: (lato, force_id)}`.
    """
    by_block: Dict[str, List] = {}

    for mission in order.missions:
        by_block.setdefault(mission.block_id, []).append(mission)

    forces: Dict[str, object] = {}

    for block_id in sorted(blocks):
        block = blocks[block_id]
        missions = by_block.get(block_id, [])

        if not missions:
            forces[block_id] = block
            continue

        for mission in missions:
            forces[mission.mission_id] = MA.MissionForce.of_mission(mission, block)

        residual = MA.MissionForce.unassigned(block, missions)

        if residual is not None:
            forces[block_id] = residual

    owner: Dict[str, Tuple[int, str]] = {}

    for force_id, force in forces.items():
        for asset in (getattr(force, 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is not None and asset_id in block_owner:
                owner[asset_id] = (block_owner[asset_id][0], force_id)

    return forces, owner


def _engagement_committed(order: SessionOrder, forces: Mapping[str, object]
                          ) -> Optional[Dict[str, Tuple[str, ...]]]:
    """`committed` per forza d'ingaggio: la restrizione del blocco (`order.committed`, chiavato per
    blocco) intersecata con gli asset della forza. None se l'ordine non restringe nulla."""
    committed = order.committed_map()

    if committed is None:
        return None

    translated: Dict[str, Tuple[str, ...]] = {}

    for force_id, force in forces.items():
        block_id = getattr(force, 'block_id', None) if isinstance(force, MA.MissionForce) else force_id

        if block_id not in committed:
            continue

        own = {_domain_id(asset) for asset in (getattr(force, 'assets', None) or {}).values()}
        translated[force_id] = tuple(asset_id for asset_id in committed[block_id] if asset_id in own)

    return translated


def _destruction_times(results, assets: Mapping[str, object], t0: float) -> Dict[str, float]:
    """`{asset_id: istante di distruzione}`: primo DamageEvent `destroyed` della sessione, o `t0`
    per un asset gia' distrutto all'inizio (nessun evento che lo distrugga in sessione)."""
    destroyed: Dict[str, float] = {}

    for result in results:
        if result is None:
            continue

        for event in result.damage_events:
            if event.destroyed and event.target_id is not None:
                destroyed[event.target_id] = min(event.time, destroyed.get(event.target_id, event.time))

    for asset_id, asset in assets.items():
        if asset_id not in destroyed and getattr(asset, 'is_destroyed', lambda: False)():
            destroyed[asset_id] = t0

    return destroyed


def _mission_outcome(mission, movements, assets: Mapping[str, object], destroyed: Mapping[str, float],
                     session_end: float, fuel_ends: Optional[Mapping[str, FuelEnd]] = None,
                     activity_ends: Optional[Mapping[str, Tuple[float, AssetEndReason]]] = None,
                     target_declared: bool = False, target_time: Optional[float] = None,
                     bingo_ends: Optional[Mapping[str, BingoEnd]] = None) -> MissionOutcome:
    """Esito di missione (regola nel docstring del modulo, "Fine di attivita' e stato di missione"):
    esaurimento del carburante della F6-A in `fuel_ends`, fini di attivita' della F6-B1 in
    `activity_ends` (`{asset_id: (istante, motivo)}`, `_activity_ends`), criterio del bersaglio
    distrutto dichiarato e rappresentabile in `target_declared` con l'istante in `target_time`,
    rientri al bingo della F6-B2 in `bingo_ends`."""
    asset_outcomes = {}
    reached = False
    passages: List[Tuple[Tuple[float, ...], Optional[float]]] = []

    for movement in movements:
        asset_id = movement.asset_id
        end = (fuel_ends or {}).get(asset_id)
        bingo = (bingo_ends or {}).get(asset_id)
        planned = MA.waypoint_times(movement)
        # Oltre l'esaurimento (F6-A) o il bingo (F6-B2) l'asset non segue piu' la rotta: i punti successivi
        # non sono raggiunti.
        stop = min([e.time for e in (end, bingo) if e is not None], default=None)
        times = planned if stop is None else tuple(t for t in planned if t <= stop + CS.TIME_EPS)
        arrival = times[-1] if times and len(times) == len(planned) else None
        destroyed_at = destroyed.get(asset_id)
        crashed_at = end.time if end is not None and end.kind == FUEL_CRASH else None
        arrives = arrival is not None and arrival <= session_end + CS.TIME_EPS
        # Fine di attivita' (F6-B1) dentro la sessione: l'asset prosegue passivo sulla rotta, quindi
        # un arrivo all'ultimo punto DOPO la fine non completa la missione.
        activity = (activity_ends or {}).get(asset_id)

        if activity is not None and activity[0] > session_end + CS.TIME_EPS:
            activity = None

        completes = arrives and (activity is None or arrival <= activity[0] + CS.TIME_EPS)

        if completes and (destroyed_at is None or destroyed_at > arrival + CS.TIME_EPS):
            reached = True

        if destroyed_at is not None and (crashed_at is None or destroyed_at <= crashed_at + CS.TIME_EPS):
            outcome = AssetMissionOutcome(asset_id, AssetState.DESTROYED, AssetEndReason.DESTROYED, destroyed_at)
        elif crashed_at is not None:
            # Aereo a secco in volo senza base raggiungibile (F6-A): perso per carburante.
            outcome = AssetMissionOutcome(asset_id, AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, crashed_at)
            destroyed_at = crashed_at
        else:
            asset = assets.get(asset_id)
            health = getattr(asset, 'health', None)
            state = AssetState.DAMAGED if isinstance(health, (int, float)) and health < 100 else AssetState.OPERATIONAL

            if completes:
                outcome = AssetMissionOutcome(asset_id, state, AssetEndReason.ROUTE_COMPLETED, arrival)
            elif activity is not None and (stop is None or activity[0] < stop - CS.TIME_EPS):
                outcome = AssetMissionOutcome(asset_id, state, activity[1], activity[0])

                if activity[1] is AssetEndReason.MAX_DURATION:
                    # Durata / tempo sulla stazione esaurito: fine REGOLARE, come l'ultimo punto.
                    reached = True
            elif end is not None:
                # Fermo nel punto (terra/mare) o a terra sulla base dopo la planata (aereo), F6-A; anche a
                # secco sul rientro dopo il bingo (F6-B2): conta l'ultimo fatto, l'esaurimento.
                outcome = AssetMissionOutcome(asset_id, state, AssetEndReason.FUEL_EXHAUSTED, end.time)
            elif bingo is not None:
                # Rientro al bingo (F6-B2): l'asset ha lasciato la rotta all'istante del bingo.
                outcome = AssetMissionOutcome(asset_id, state, AssetEndReason.BINGO, bingo.time)
            else:
                outcome = AssetMissionOutcome(asset_id, state, AssetEndReason.SESSION_END, session_end)

        asset_outcomes[asset_id] = outcome
        passages.append((times, destroyed_at))

    # Regola unica (F6-B1, sostituisce la precedenza provvisoria della F6-A):
    # DESTROYED (tutti persi) > COMPLETED (obiettivo raggiunto: bersagli distrutti se il criterio e'
    # dichiarato, altrimenti ultimo punto o durata) > ABORTED (ogni asset superstite ha chiuso per
    # carburante, munizioni o danno; motivo = quello dell'ultima chiusura) > FAILED.
    # Con `F6_END_CRITERIA` spento resta la precedenza provvisoria della F6-A: ABORTED(FUEL) se ALMENO
    # un asset superstite e' fermo o atterrato per carburante.
    reason = None
    survivors = [o for o in asset_outcomes.values() if o.state is not AssetState.DESTROYED]
    aborts = [o for o in survivors if o.end_reason in _ABORT_REASON_OF]
    aborted = (len(aborts) == len(survivors)) if F6_END_CRITERIA else bool(aborts)

    if not survivors:
        status = MissionStatus.DESTROYED
    elif (target_time is not None) if target_declared else reached:
        status = MissionStatus.COMPLETED
    elif aborted:
        last = max(aborts, key=lambda o: (o.end_time, -list(_ABORT_REASON_OF).index(o.end_reason)))
        status, reason = MissionStatus.ABORTED, _ABORT_REASON_OF[last.end_reason]
    else:
        status = MissionStatus.FAILED

    # ETA effettive: per punto, il primo passaggio dentro la sessione fra gli asset non ancora
    # distrutti. Con il percorso di riferimento i punti della rotta sono quelli della missione.
    count = max((len(MA.waypoint_times(movement)) for movement in movements), default=0)
    etas = []

    for index in range(count):
        candidates = [times[index] for times, destroyed_at in passages
                      if index < len(times) and times[index] <= session_end + CS.TIME_EPS
                      and (destroyed_at is None or destroyed_at > times[index] + CS.TIME_EPS)]
        etas.append(min(candidates) if candidates else None)

    return MissionOutcome(mission.mission_id, status, reason=reason, asset_outcomes=asset_outcomes,
                          actual_etas=tuple(etas))


# ── API PUBBLICA ──────────────────────────────────────────────────────────────

def run_session(order: SessionOrder, forces_a: Iterable, forces_b: Iterable,
                fire_control: Callable, *,
                horizon: Optional[float] = None,
                margin: float = 0.0,
                range_type: str = DEFAULT_DETECTION_RANGE_TYPE,
                thresholds: Optional[Dict] = None,
                reaction_profile_for: Optional[Callable] = None,
                detection_factor: Optional[Callable] = None,
                provenance: str = DM.DERIVED,
                morale_for: Optional[Callable] = None,
                enemy_estimate_for: Optional[Callable] = None,
                fire_doctrine: Optional[Dict] = None) -> SessionOutcome:
    """Esegue una sessione virtuale e restituisce il suo `SessionOutcome`. **Muta gli asset.**

    Danno, munizioni e carburante sono applicati agli asset reali man mano che gli eventi
    sono risolti (ogni componente connessa di forze e' un solo ingaggio, v. docstring del
    modulo). Il `SessionOutcome` restituito e' il resoconto di cio' che e' stato applicato.

    Args:
        order: il `SessionOrder`. Ne vengono usati `session_id` (radice del seed),
            `t_start`, `t_end`, `force_ids` (se non vuoto: le forze passate devono esservi
            elencate), `committed` (chiavato per blocco, tradotto per forza d'ingaggio da
            `_engagement_committed`), `salvo_window`, passato tale e quale al risolutore, e
            `missions`, da cui vengono rotta, partenza e velocita' di ogni asset
            (`Mission_Adapter.session_movements`) e le forze d'ingaggio (una per missione, F4b).
            Asset senza missione = fermo in posizione, nella forza del suo blocco, con la postura
            continua della F4c (aereo a terra, unita' di superficie in difesa); asset di missione
            presenti anche prima della partenza e dopo la fine (F5-B, v. docstring del modulo).
        forces_a/forces_b: `Military`/`Block`/`BlockItem` dei due schieramenti contrapposti.
            Si combatte solo fra A e B, mai dentro lo stesso lato.
        fire_control: `(shooter, target) -> ShotSpec | None`, v. `resolve_engagement`.
        horizon: durata [s]; obbligatoria se `order.t_end` e' None, altrimenti ricavata.
        margin/range_type: passati a `schedule_contacts` (range_type decide se le finestre
            sono "a vista" o "a tiro").
        thresholds/reaction_profile_for/detection_factor/provenance/morale_for/
            enemy_estimate_for/fire_doctrine: passati a `resolve_engagement`; `provenance` vale anche per i
            FuelEvent. La tempra delle forze (soglia di rottura) e' estratta dal flusso
            `order.rng(event_id=temper_event_id(*forze))`, separato da quello dell'ingaggio. Il
            dominio di coordinamento (`coordination_of`) e' ricavato dalle missioni e da
            `order.operations` (v. "Dominio di coordinamento").

    Returns:
        Il `SessionOutcome`, con un `MissionOutcome` per missione dell'ordine, un `ForceOutcome`
            per forza d'ingaggio (missione) che ha combattuto e la postura a fine sessione di ogni
            asset delle forze passate (`postures`, F5-B); senza ingaggi ne' movimenti resta valido,
            con le sole posture.

    Raises:
        TypeError: `order` non e' un SessionOrder, `fire_control` non chiamabile.
        ValueError: durata mancante o incoerente, forze/asset duplicati o fuori
            `order.force_ids`, missione di un blocco non passato o con asset di altri blocchi,
            `mission_id` uguale all'id di un blocco, e gli errori di dominio dei moduli chiamati.
    """
    if not isinstance(order, SessionOrder):
        raise TypeError(f"order must be a SessionOrder, got {type(order).__name__}")

    if not callable(fire_control):
        raise TypeError("fire_control must be callable")

    if provenance not in DM.PROVENANCES:
        raise ValueError(f"provenance must be one of {DM.PROVENANCES}, got {provenance!r}")

    horizon = _session_horizon(order, horizon)
    t0 = order.t_start
    session_end = t0 + horizon

    items_a, items_b, blocks, block_owner = _collect_forces(order, forces_a, forces_b)
    _check_missions(order, blocks)
    forces, owner = _engagement_forces(order, blocks, block_owner)
    coordination = MA.coordination_domains(forces, order.operations)
    # Area delle basi aeree per lato (F5-B): un aereo atterra su una base vera anche senza
    # riferimento del waypoint, se l'ultimo punto e' nell'area di una base del suo lato.
    air_bases = {side: MA.air_base_points(blocks.values(), side)
                 for side in {getattr(blocks[mission.block_id], 'side', None) for mission in order.missions
                              if mission.domain == 'air'}}
    mission_movements = {mission.mission_id: MA.mission_movements(
        mission, t0, air_bases.get(getattr(blocks[mission.block_id], 'side', None), ()))
        for mission in order.missions}
    movement_of = {movement.asset_id: movement for movements in mission_movements.values() for movement in movements}
    routes, starts, speeds = MA.session_movements(order.missions, t0)
    # Aerei a terra nel tempo (F4c + F5): sempre gli aerei senza missione, a intervalli quelli di
    # missione prima del decollo e dopo l'atterraggio su una base vera. V. docstring del modulo.
    grounded = MA.grounded_schedule(forces, movement_of.values())
    assets_by_id: Dict[str, object] = {}

    for force_id in sorted(blocks):
        for asset in (getattr(blocks[force_id], 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is not None:
                assets_by_id[asset_id] = asset

    # Tratti di MOVIMENTO di ogni asset di missione (senza la presenza ferma prima e dopo, che non
    # consuma) e, dalla F6-A, esaurimento del carburante calcolato A MONTE (v. "Carburante").
    mission_of = {mission.mission_id: mission for mission in order.missions}
    moving_legs: Dict[str, List[CS.Leg]] = {}
    fuel_ends: Dict[str, FuelEnd] = {}

    for asset_id, movement in movement_of.items():
        moving_legs[asset_id] = MA.movement_legs(movement, t0, session_end, presence=False)

    # F6-B2: bingo in volo, calcolato A MONTE sui tratti che consumano (come l'esaurimento, v. "Bingo"):
    # oltre il bingo l'aereo torna alla base. Prima dell'esaurimento, che e' poi cercato sui tratti con il
    # rientro (a secco sul rientro: planata o perdita, F6-A). F6-B2bis (`F6_BINGO_REVERSE_ROUTE`): rientro
    # lungo la rotta a ritroso, calcolato sulla missione INTERA (`Mission_Adapter.airborne_legs`, gli stessi
    # tratti del validatore, anche oltre la fine della sessione: l'anello legge il resto della rotta fino al
    # LAND); un bingo che cadrebbe dopo la fine della sessione non c'e' nella sessione.
    bingo_ends: Dict[str, BingoEnd] = {}

    for asset_id, movement in movement_of.items():
        asset = assets_by_id.get(asset_id)
        mission = mission_of[movement.mission_id]

        if not F6_BINGO or asset is None or not moving_legs[asset_id] or mission.domain != 'air' \
                or not mission.end_criteria.bingo:
            continue

        bases = air_bases.get(getattr(blocks[mission.block_id], 'side', None), ())

        if F6_BINGO_REVERSE_ROUTE:
            end = _bingo_end(asset, asset_id, _consuming_legs(asset_id, MA.airborne_legs(movement), grounded),
                             bases, MA.bingo_return_rule(mission))

            if end is not None and end.time >= session_end - CS.TIME_EPS:
                end = None
        else:
            end = _bingo_end(asset, asset_id, _consuming_legs(asset_id, moving_legs[asset_id], grounded), bases) \
                if bases else None

        if end is not None:
            bingo_ends[asset_id] = end
            moving_legs[asset_id] = _legs_after_bingo(moving_legs[asset_id], end, t0, session_end, park=False)
            logger.info(f"run_session: asset {asset_id!r} reaches bingo at t={end.time:.1f}: it returns to the "
                        f"air base at {end.landing_point}, landing at t={end.landing_time:.1f}")

    grounded = _grounded_after_bingo(grounded, bingo_ends)

    for asset_id, movement in movement_of.items():
        asset = assets_by_id.get(asset_id)

        if not F6_FUEL_CONSTRAINT or asset is None or not moving_legs[asset_id]:
            continue

        mission = mission_of[movement.mission_id]
        side = getattr(blocks[mission.block_id], 'side', None)
        end = _fuel_end(asset, asset_id, mission.domain, _consuming_legs(asset_id, moving_legs[asset_id], grounded),
                        grounded, air_bases.get(side, ()))

        if end is not None:
            fuel_ends[asset_id] = end
            logger.info(f"run_session: asset {asset_id!r} runs out of fuel at t={end.time:.1f} "
                        f"({end.kind}): its legs end there")

    # Tratti di presenza degli asset di missione (F5-B): movimento + presenza ferma prima della
    # partenza e dopo la fine (`Mission_Adapter.movement_legs`); vuoti = asset fermo in posizione.
    # F6-A: troncati all'esaurimento del carburante (una lista VUOTA data allo scheduler = l'asset non
    # esiste nella sessione, aereo perso alla partenza).
    presence_legs: Dict[str, List[CS.Leg]] = {}

    for asset_id, movement in movement_of.items():
        legs = MA.movement_legs(movement, t0, session_end)

        if asset_id in bingo_ends:
            # F6-B2: fino al bingo, rientro e sosta a terra sulla base.
            legs = _legs_after_bingo(legs, bingo_ends[asset_id], t0, session_end, park=True)

        end = fuel_ends.get(asset_id)

        if end is not None:
            presence_legs[asset_id] = _truncate_at_fuel_end(legs, end, t0, session_end)
            moving_legs[asset_id] = [leg for leg in CS.clamp_legs(moving_legs[asset_id], t0, end.time)
                                     if leg.duration > CS.TIME_EPS]
        elif legs:
            presence_legs[asset_id] = legs

    grounded = _grounded_after_fuel(grounded, fuel_ends)
    # F6-B1: criteri di fine di attivita' dichiarati dalle missioni (vuoto senza criteri o spento).
    activity_plans = _activity_plans(order, movement_of, mission_of, assets_by_id, blocks)
    plans_with_targets = any(plan.target_ids for plan in activity_plans.values())

    # ── strato 1: tutti i contatti della sessione ─────────────────────────────
    windows = CS.schedule_contacts(items_a, items_b, horizon, routes=routes, starts=starts,
                                   speeds=speeds, t0=t0, margin=margin, range_type=range_type,
                                   grounded=grounded, legs=presence_legs)
    groups = _group_windows(windows, owner)

    # Tratti di ogni asset (presenza o posizione fissa): servono al risolutore per l'istante
    # esatto di rilevamento; i soli tratti di MOVIMENTO (senza la presenza ferma) al carburante.
    all_legs: Dict[str, List[CS.Leg]] = {}
    movements: List[Tuple[str, object, List[CS.Leg]]] = []

    for force_id in sorted(blocks):
        for asset in (getattr(blocks[force_id], 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is None:
                continue

            moving = moving_legs.get(asset_id, [])

            if moving:
                movements.append((asset_id, asset, moving))

            if asset_id in presence_legs:
                all_legs[asset_id] = presence_legs[asset_id]
            else:
                all_legs[asset_id] = CS.static_legs(getattr(asset, 'position', None), t0, session_end)

    # ── coda eventi ───────────────────────────────────────────────────────────
    queue: List = []
    sequence = 0

    # Un evento per COMPONENTE connessa di forze d'ingaggio, cioe' di missioni (F4b).
    for force_ids, group in _connected_components(groups, coordination):
        event_id = engagement_event_id(*force_ids)
        sequence += 1
        heapq.heappush(queue, (min(w.t_start for w in group), ENGAGEMENT_EVENT, event_id,
                               sequence, (force_ids, group)))

    for asset_id, asset, legs in movements:
        sequence += 1
        heapq.heappush(queue, (legs[-1].t_end, MOVEMENT_EVENT, asset_id, sequence, (asset, legs)))

    committed = _engagement_committed(order, forces)
    results: List[Optional[ER.EngagementResult]] = []
    fuel_events: List[FM.FuelEvent] = []
    engaged: set = set()

    while queue:
        time, kind, key, _, payload = heapq.heappop(queue)

        if kind == ENGAGEMENT_EVENT:
            force_ids, group = payload
            component = [forces[force_id] for force_id in force_ids]
            # F6-B1: criteri passati solo se dichiarati (senza, la chiamata e' quella di prima), con le
            # distruzioni dei bersagli note a questo punto (ingaggi gia' risolti, carburante).
            extra = {}
            criteria = {}

            if activity_plans:
                known = _known_destructions(results, assets_by_id, t0, fuel_ends) if plans_with_targets else None
                criteria = _activity_criteria(activity_plans, known)

            # F6-B2: dal bingo l'aereo rientra e non lancia piu' salve offensive (fine nota a monte, `until`).
            for asset_id, bingo in bingo_ends.items():
                known_criteria = criteria.get(asset_id)

                if known_criteria is None:
                    criteria[asset_id] = ER.ActivityCriteria(until=bingo.time)
                elif known_criteria.until is None or bingo.time < known_criteria.until:
                    criteria[asset_id] = dataclasses.replace(known_criteria, until=bingo.time)

            if criteria:
                extra['activity_criteria'] = criteria

            result = ER.resolve_engagement(component[0], component[1], group, fire_control,
                                           order.rng(mission_id=None, event_id=key, counter=0),
                                           extra_forces=component[2:],
                                           legs=all_legs, committed=committed,
                                           thresholds=thresholds,
                                           reaction_profile_for=reaction_profile_for,
                                           detection_factor=detection_factor,
                                           salvo_window=order.salvo_window,
                                           provenance=provenance,
                                           breakpoint_rng=order.rng(mission_id=None,
                                                                    event_id=temper_event_id(*force_ids),
                                                                    counter=0),
                                           morale_for=morale_for,
                                           enemy_estimate_for=enemy_estimate_for,
                                           fire_doctrine=fire_doctrine,
                                           coordination_of=coordination,
                                           grounded=grounded, **extra)
            results.append(result)

            if result is not None:
                # Applicato SUBITO, a tutte le forze della componente. Le componenti sono
                # disgiunte: nessun altro ingaggio della sessione legge queste forze.
                ER.apply_engagement_result(result, *component)
                engaged |= _engaged_assets(result)
        else:
            asset, legs = payload
            regime = COMBAT_REGIME if key in engaged else CRUISE_REGIME

            if F6_FUEL_PER_LEG:
                # F6-A: un FuelEvent per tratto che consuma (movimento al regime della sessione, soste
                # nel tempo alla crociera), applicato in ordine; dopo l'esaurimento nessun evento.
                for leg in _consuming_legs(key, legs, grounded):
                    event = _build_leg_fuel(asset, leg, regime, provenance)

                    if event is None:
                        continue

                    FM.apply_fuel_event(asset, event)
                    fuel_events.append(event)

                    if event.exhausted:
                        break

                continue

            distance = _legs_distance(legs)

            if distance <= 0.0:
                continue

            event = _build_fuel(asset, distance, time, regime, provenance)

            if event is not None:
                FM.apply_fuel_event(asset, event)
                fuel_events.append(event)

                if event.exhausted and event.distance_covered < event.distance:
                    logger.info(f"run_session: asset {key!r} runs out of fuel after "
                                f"{event.distance_covered:.0f} of {event.distance:.0f} m "
                                f"(position not updated, see FuelEvent)")

    # ── porta di uscita ───────────────────────────────────────────────────────
    latest = session_end

    for result in results:
        if result is None:
            continue

        times = [e.time for e in result.damage_events + result.ammunition_events]

        if result.t_end is not None:
            times.append(result.t_end)

        if times and max(times) > latest:
            latest = max(times)

    if latest > session_end + CS.TIME_EPS:
        logger.info(f"run_session: session {order.session_id!r} has activity up to t={latest} "
                    f"beyond its end t={session_end} (salvos in flight): outcome interval extended")

    destroyed = _destruction_times(results, assets_by_id, t0)
    # F6-B1: fine di attivita' per asset e distruzione dei bersagli per missione (sull'intera sessione).
    activity_ends, target_times = _activity_ends(activity_plans, movement_of, results,
                                                 _known_destructions(results, assets_by_id, t0, fuel_ends)) \
        if activity_plans else ({}, {})
    mission_outcomes = {mission.mission_id: _mission_outcome(mission, mission_movements[mission.mission_id],
                                                             assets_by_id, destroyed, session_end, fuel_ends,
                                                             activity_ends,
                                                             target_declared=mission.mission_id in target_times,
                                                             target_time=target_times.get(mission.mission_id),
                                                             bingo_ends=bingo_ends)
                        for mission in order.missions}

    # F6-A: un aereo perso per carburante (nessuna base raggiungibile in planata) e' distrutto come in
    # combattimento: salute a 0 con `Asset.apply_damage`, lo stesso canale del danno, ma SENZA un
    # DamageEvent nell'esito (non e' un colpo: nessun tiratore ne' arma). Il motivo e' nell'esito per
    # asset (FUEL_EXHAUSTED). Applicata dopo gli ingaggi: oltre l'esaurimento l'aereo non ha tratti.
    for asset_id, end in sorted(fuel_ends.items()):
        asset = assets_by_id.get(asset_id)

        if end.kind != FUEL_CRASH or asset is None or getattr(asset, 'is_destroyed', lambda: False)():
            continue

        health = getattr(asset, 'health', None)

        if isinstance(health, int) and not isinstance(health, bool) and health > 0 and \
                callable(getattr(asset, 'apply_damage', None)):
            asset.apply_damage(-health)

    # Postura di ogni asset a fine sessione (F5-B, deviazione 12): anche dei blocchi senza missioni.
    postures = MA.session_postures(forces, movement_of, grounded, session_end)
    postures = _postures_after_bingo(postures, bingo_ends,
                                     {a: mission_of[m.mission_id].mission_type for a, m in movement_of.items()},
                                     grounded, session_end)
    postures = _postures_after_fuel(postures, fuel_ends,
                                    {a: mission_of[m.mission_id].domain for a, m in movement_of.items()},
                                    {a: mission_of[m.mission_id].mission_type for a, m in movement_of.items()},
                                    grounded, session_end)

    if F6_DESTROYED_POSTURE:
        # F6-B1 (postura rimandata dalla F5-B, decisione dell'utente del 2026-10-12): un asset DISTRUTTO
        # a fine sessione, in combattimento o per carburante (F6-A), ha postura `destroyed`.
        for asset_id in postures:
            asset = assets_by_id.get(asset_id)

            if asset is not None and getattr(asset, 'is_destroyed', lambda: False)():
                postures[asset_id] = MA.DESTROYED_POSTURE

    return assemble_session_outcome(order.session_id, results, fuel_events,
                                    t_start=t0, t_end=latest, mission_outcomes=mission_outcomes,
                                    postures=postures)
