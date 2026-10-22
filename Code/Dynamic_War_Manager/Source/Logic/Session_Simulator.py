"""Orchestratore di sessione — fa girare **una sessione virtuale vera**, dall'ordine all'esito.

FASE 6 del motore di sessioni virtuali (v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §6 e §8, e
[[project_virtual_session_engine_design]]): "orchestratore a coda eventi (heapq, clock in
secondi), risoluzione simultanea".

Le fasi 3-5 hanno prodotto i pezzi, ma nessuno li aveva mai messi in fila:

    SessionOrder ──> Contact_Scheduler.schedule_contacts      (strato 1: QUANDO)
                 ──> raggruppamento in episodi d'ingaggio (G4a; spento: componenti connesse di forze)
                 ──> Engagement_Resolver.resolve_engagement    (strato 2: COME FINISCE)
                 ──> apply_engagement_result                   (strato 3: danno, munizioni)
                 ──> ri-pianificazione degli aerei dopo l'episodio e nuovi contatti (G4b)
                 ──> Fuel_Model.build/apply_fuel_event         (strato 3: carburante, passo finale dal G4a)
                 ──> Session_Types.assemble_session_outcome    (porta di uscita)

Questo modulo e' SOLO quella fila: non reimplementa geometria, Pd, latenze, salve, danno o
consumi. Ogni numero che produce viene da uno dei moduli chiamati.

## La coda eventi

Tre tipi di evento di sessione (il terzo dalla F7b), con chiave `(t, tipo, id, sequenza)`:

- **ENGAGEMENT** — dal G4a uno per EPISODIO d'ingaggio (v. "Episodi d'ingaggio (G4a)"): le finestre legate
  perche' condividono una forza (o il dominio di coordinamento) e si sovrappongono entro `EPISODE_GAP`;
  istante = inizio della prima finestra dell'episodio. Risolve l'episodio con UNA chiamata a
  `resolve_engagement` (che ha la propria coda interna di lanci/impatti) sulle sole sue finestre e ne applica
  subito l'esito agli asset reali di tutte le sue forze; gli episodi sono estratti in ordine di tempo (poi
  `event_id`). Con `G4_EPISODES` spento, uno per componente connessa di forze (v. sotto): le forze legate,
  direttamente o per tramite di altre, da almeno una `ContactWindow`, con istante = inizio della prima finestra
  fra QUALUNQUE coppia della componente (un `heapq`, come prima).
- **AREA_FIRE** (F7b) — uno per azione `Fire_At_Point` di un asset di missione di terra o di mare, all'istante d'impatto
  (v. "Fuoco su posizione (F7b)"); fra ENGAGEMENT e MOVEMENT a parita' d'istante. Senza azioni non c'e' nessun evento.
- **MOVEMENT** — uno per asset con rotta schedulabile nella sessione; istante = fine del
  suo movimento dentro la sessione (dalla F6-A troncato all'esaurimento del carburante). Produce e
  applica i `FuelEvent` del tragitto, uno per tratto (v. "Carburante").

Dal G4a la coda e' percorsa in DUE passi: prima tutti gli ENGAGEMENT (episodi, nell'ordine sopra), poi la
contabilita' del carburante, un `heapq` con gli ingaggi risolti alla loro chiave e i MOVEMENT, cioe' la stessa
coda di prima ripercorsa nello stesso ordine: stessi `FuelEvent` (per tratto e d'ingaggio) nello stesso ordine.
E' possibile perche' il risolutore non legge il carburante (nessun accesso a `fuel` in `Engagement_Resolver`,
fire control e profili di reazione leggono i registri, non il contatore) e il carburante non legge danno ne'
scorte (`Fuel_Model` legge solo il contatore, il loadout e i registri): spostare il passo non cambia nulla, e
il G4b conosce i tratti definitivi prima di contabilizzarli. Dal G4b, fra un episodio e il successivo gli aerei
ri-pianificati cambiano tratti e contatti (v. "Ri-pianificazione dopo l'episodio (G4b)"): gli episodi non ancora
risolti sono ricostruiti, la contabilita' usa i tratti definitivi.

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
delle sue forze riunite (v. "RNG: uno stream per ingaggio"). Dal G4a (`G4_EPISODES`) sono nello stesso
EPISODIO solo se le loro finestre si sovrappongono entro `EPISODE_GAP` (v. "Episodi d'ingaggio (G4a)").

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
raggiunto l'ultimo punto PRIMA di un'eventuale distruzione; con `F8_IN_PROGRESS` attivo la missione non
completata, non distrutta e non abortita con almeno un asset superstite che ha finito per SESSION_END e'
IN_PROGRESS (non "fallita", v. D4.e); altrimenti FAILED ("non completata entro la sessione"). Dalla F6-B1
la regola unica sotto. ETA effettive per punto: il primo passaggio fra gli asset non ancora
distrutti, None se nessuno ci arriva dentro la sessione; e' l'istante d'ARRIVO al punto (prima di
un'eventuale attesa nel punto), calcolato dai tratti con le attese (`Mission_Adapter.waypoint_times`,
F5-C), non dalle ETA pianificate.
Carburante (F6-A, v. "Carburante"): un aereo perso per esaurimento e' DESTROYED con motivo
FUEL_EXHAUSTED all'istante dell'esaurimento (una distruzione in combattimento precedente prevale);
dal G2 con l'equipaggio recuperato (`crew_recovered` True; None in ogni altro esito, comprese le perdite in
combattimento: l'equipaggio non e' modellato); un asset fermo (terra/mare) o atterrato in planata per
esaurimento ha motivo FUEL_EXHAUSTED, stato
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
    all'istante dell'ultima distruzione (non prima della partenza); per un GROUP con
    `Target.asset_ids` solo quel sottoinsieme (F7a). Bersagli POINT/AREA/ZONE: non
    rappresentabili (F7a, decisione 12 del 2026-10-18: nessun asset da distruggere), criterio ignorato con
    un warning. Nel
    risolutore il criterio vede le distruzioni degli ingaggi gia' risolti e della propria run;
    l'esito lo valuta sull'intera sessione (`_activity_ends`);
  * `max_duration_s`: fine all'istante partenza della missione + durata (semantica scelta, la piu'
    semplice: "durata o tempo sulla stazione" contato dalla partenza), passata al risolutore come
    fine nota a monte (`until`).
Per asset la fine e' la PRIMA fra quelle scattate (a parita' d'istante: danno, winchester, bersaglio,
durata) se cade nella sessione e prima dell'esaurimento del carburante; un asset che completa la rotta
PRIMA della fine di attivita' resta ROUTE_COMPLETED, un arrivo DOPO non completa la missione.
`abort_on_threat` NON e' letto (fuori dal piano della F6); `bingo` lo legge la F6-B2 (v. "Bingo"; dal G2
soglia con la riserva di disimpegno e albero di decisione).

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
stato risolto: il regime di consumo (v. sotto) e' noto. Dal G4a la contabilita' del carburante e'
comunque un passo finale, dopo tutti gli ingaggi (v. "La coda eventi").

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

**Deliberatamente conservativa rispetto al tempo (fino al G4a):** non si distingue se le finestre di una
componente si sovrappongono davvero o sono in sequenza (X contro A al mattino, contro B
la sera): anche in quel caso {X, A, B} e' risolta con una sola run. La coda eventi interna ordina comunque
gli eventi nel tempo esatto, ma l'ingaggio dura quanto la sessione: un solo consumo d'ingaggio (G3), un
disingaggio al mattino che vale anche la sera, nessuna decisione possibile "dopo l'ingaggio". Dal G4a
(`G4_EPISODES`) la componente e' spezzata nei suoi episodi (sotto); spento, questa regola esattamente come
prima.

## Episodi d'ingaggio (G4a del nuovo modello di bingo, decisioni dell'utente del 2026-10-17)

Interruttore `G4_EPISODES` (attivo). L'ingaggio diventa un EVENTO NEL TEMPO:

- **Episodio** (`_episodes`): gruppo di finestre di contatto legate, direttamente o per tramite di altre,
  perche' appartengono a coppie di forze che CONDIVIDONO una forza, o forze dello stesso dominio di
  coordinamento (`coordination`, come in `_connected_components`), E i loro intervalli si sovrappongono o
  distano al piu' `EPISODE_GAP` (300 s = `Fuel_Model.DISENGAGE_TIME`: ritrovare il contatto entro i 5 minuti
  del disimpegno e' lo stesso combattimento). La componente connessa di prima e' l'unione dei suoi episodi; con
  un intervallo infinito coincidono. Ordine deterministico: inizio della prima finestra, poi `event_id`, poi
  la prima finestra; le finestre dell'episodio nell'ordine della componente (coppie ordinate, poi l'ordine
  nella coppia).
- **Un ENGAGEMENT per episodio**, all'istante della sua prima finestra; `resolve_engagement` sulle sole finestre
  dell'episodio, con le sole sue forze (`force_a`/`force_b` = le prime due per id, le altre in
  `extra_forces`, come per la componente); esito applicato SUBITO, quindi un episodio successivo delle
  stesse forze parte dallo stato gia' consumato (salute e scorte) e i `health_before/after` sono concatenati
  (`assemble_session_outcome(..., chained=True)`).
- **Forza occupata** (`_trim_busy`, `Contact_Scheduler.trim_contact_window`): una forza e' impegnata dal primo
  istante del suo episodio fino al `t_end` del suo esito (salve in volo comprese). Gli episodi sono estratti in
  ordine di inizio, quindi ogni finestra non ancora risolta comincia non prima dell'episodio appena risolto:
  quelle delle sue forze che cominciano prima del `t_end` sono RITAGLIATE per partire da li' (CPA e reciproco
  ricalcolati sui tratti ritagliati), scartate se si svuotano; se qualcosa e' cambiato gli episodi rimasti sono
  ricostruiti con la stessa regola (un ritaglio puo' solo spostare in avanti un inizio, quindi l'ordine di
  estrazione resta non decrescente e la storia gia' risolta non cambia). Con l'intervallo di 300 s il caso si
  presenta solo con salve in volo per piu' di circa 300 s oltre l'ultima finestra (es. missili da crociera).
  Conseguenza dichiarata: una forza che entra tardi in un episodio lungo e' "occupata" dall'inizio
  dell'episodio, e un suo contatto in un altro episodio dentro quell'intervallo e' spostato alla fine.
- **RNG**: `event_id` = quello di prima (`engagement_event_id(*forze dell'episodio)`), `counter` = ordinale
  degli episodi con lo STESSO insieme di forze nella sessione (0 per il primo); stessa regola per la tempra
  (`temper_event_id`, tempra NUOVA per episodio). Una componente che e' un solo episodio ha esattamente lo
  stream, le finestre, l'ordine e quindi l'esito di prima.
- **Forza disingaggiata** (DISENGAGED in un episodio): negli episodi successivi della sessione e' PASSIVA, tutti
  i suoi asset: nessuna salva offensiva (`ActivityCriteria.until` = istante del cambio di esito, o fine
  dell'esito se manca, combinato con i criteri esistenti come per il bingo), resta bersaglio e intercettore.
  Nel solo G4a il DES non la ri-instrada (prosegue sulla rotta pianificata) e l'esito di missione non cambia; dal
  G4b gli AEREI di una missione disingaggiata rientrano (v. "Ri-pianificazione dopo l'episodio (G4b)"), le forze
  terrestri e navali restano come qui. Stessa regola per una fine di attivita' della F6-B1 (winchester, danno, bersaglio distrutto)
  scattata in un episodio precedente: l'asset resta passivo dall'istante della fine (dentro la run il
  risolutore non lo saprebbe fino al primo controllo). Erosione e shock della soglia di rottura sono contati
  sugli asset impegnati all'inizio dell'episodio (`ForceOutcome.committed`): le perdite degli episodi
  precedenti non entrano nell'erosione dell'episodio (ingaggio diverso, tempra nuova).
- **Soglia di danno** (`damage_threshold`): la salute di riferimento e' quella d'inizio SESSIONE
  (`ActivityCriteria.reference_health`), cosi' che il danno di episodi diversi si sommi.
- **Esiti di forza**: un `ForceOutcome` per forza PER EPISODIO (`SessionOutcome.outcomes_of` ne restituisce uno
  per episodio, nell'ordine di risoluzione).
- **Consumo d'ingaggio (G3)**: uno per episodio a cui l'aereo partecipa.
- **Distruzioni e fini di attivita'** (`_destruction_times`, `_known_destructions`, `_activity_ends`): gia'
  sull'insieme degli esiti (minimo per asset), corrette con piu' esiti per asset.
Spento: la componente connessa, esattamente come prima. Limiti: l'episodio e' risolto in blocco (le decisioni
dopo l'episodio sono del G4b, sotto); senza il G4b il DES non ri-instrada ne' la forza disingaggiata ne' l'aereo
sotto la soglia di bingo; la forza occupata e' per forza intera, non per asset.

## Ri-pianificazione dopo l'episodio (G4b del nuovo modello di bingo, decisioni dell'utente del 2026-10-17)

Interruttore `G4_REPLAN` (attivo), letto solo con `G4_EPISODES` acceso. Alla fine di ogni episodio (istante `t_r` =
`t_end` del suo esito, l'ultimo evento: salve in volo comprese) sono candidati gli aerei di MISSIONE (dominio
'air') che vi hanno CONSUMATO (G3: partecipazione in volo, la stessa regola della contabilita') o la cui FORZA
d'ingaggio vi e' DISINGAGGIATA (con `F6_BINGO` e `F6_BINGO_DISENGAGE_RESERVE` accesi: e' l'albero del G2). Per
ciascuno, in ordine di id:
  * **istante della decisione** `t_d` = `t_r` o, se i tratti di movimento dell'aereo nella sessione finiscono prima
    (rotta completata DENTRO l'episodio, es. S26 'transfer_continue'), la loro fine: in quel caso conta solo
    l'esaurimento (sotto), non c'e' piu' rotta da cui rientrare. Escluso se a terra a `t_d`, gia' a secco (planata
    o perso), distrutto, oltre la fine della sessione o con il carburante non modellato;
  * **residuo** a `t_d` calcolato ANALITICAMENTE (`Fuel_Model.fuel_at`): carburante d'inizio sessione - fabbisogno
    dei tratti che consumano fino a `t_d` alla crociera (tratto in corso in proporzione) - consumi d'ingaggio fino
    a `t_d`; stessa aritmetica della contabilita' finale (oltre la fine dei tratti coincide con il carburante
    finale);
  * **residuo zero** (esaurito in ingaggio): regole della F6-A dal punto in cui l'aereo e' a `t_d`
    (`_exhaustion_end`: planata in linea retta su una base del lato raggiungibile, poi a terra; altrimenti perso,
    DESTROYED/FUEL_EXHAUSTED con l'equipaggio recuperato). Sostituisce la soluzione minima del G3 (contatore a zero
    e l'aereo prosegue). Il punto e' quello a fine episodio e non quello dell'esaurimento analitico (anteriore):
    la storia dell'episodio, risolto in blocco con l'aereo in volo fino a `t_d`, resta fissata (causalita');
  * altrimenti, se l'aereo non e' gia' in rientro:
      - **bingo** (ha consumato, `EndCriteria.bingo`): `Mission_Adapter.mission_bingo_decision(..., time=t_d,
        fuel=residuo)` sui tratti della missione INTERA (`airborne_legs`, quelli che consumano, come
        `_decision_end`), albero del G2 per tipo di missione; qui le basi alternative entro 3 km dalla rotta contano
        davvero (all'inizio dei tratti non potevano vincere);
      - **rientro forzato dopo il disingaggio** (decisione dell'utente del 2026-10-17), se il bingo non fa rientrare:
        `mission_bingo_decision(..., forced=True)` (`Fuel_Model.bingo_decision`: nessun controllo di soglia), con la
        regola di COMBATTIMENTO qualunque sia il tipo di missione (base di partenza a ritroso o base alternativa,
        la raggiungibile col percorso piu' breve; altrimenti la base piu' vicina; altrimenti verso la piu' vicina e,
        a secco, la F6-A), INDIPENDENTEMENTE dal carburante. Il consumo d'ingaggio e il disingaggio coesistono:
        prima il consumo (residuo), poi la decisione; se entrambe le regole fanno rientrare vince il bingo (motivo
        BINGO);
      - **uscita di scena senza basi** (`G4_OFF_SCENE_EXIT`, decisione dell'utente del 2026-10-17): un aereo COMPARSO
        IN VOLO (`start_mode` AIR, nessuna base di partenza) senza alcuna base aerea del suo lato che, per l'una o
        l'altra regola sopra, deve rientrare (dove la regola darebbe `BINGO_NO_BASE`) ripercorre la rotta a ritroso
        fino al PUNTO DI COMPARSA (il primo punto dei tratti della missione; la meccanica del ritroso della
        F6-B2bis e del G2, alle quote dei waypoint, senza le soste e senza il tratto diretto finale) e li' ESCE DI
        SCENA (`Fuel_Model.BINGO_EXIT`, `BingoEnd.exits`): nessuna presenza dopo (come l'aereo che finisce la rotta
        senza atterrare su una base vera, F5-B), mai a terra, postura `off_scene` a fine sessione se uscito entro
        la fine (altrimenti il tipo di missione, in volo sul ritroso), non distrutto. Esito per asset e missione:
        il motivo del rientro (DISENGAGED o BINGO, ABORTED(...)) all'istante della decisione, come gli altri
        rientri. Il ritroso consuma alla crociera; se il residuo non basta a raggiungere il punto di comparsa
        valgono le regole della F6-A sul ritroso (planata su una base raggiungibile, che senza basi non c'e':
        perso, DESTROYED/FUEL_EXHAUSTED con l'equipaggio recuperato), come per un rientro irraggiungibile. SOLO
        nella ri-pianificazione dopo l'episodio: la decisione del G2 alla partenza (`_decision_end`) resta senza
        rientro (`BINGO_NO_BASE`, regole della F6-A). Spento: `BINGO_NO_BASE`, l'aereo resta passivo sulla rotta
        (G4a);
    il rientro deciso e' un `BingoEnd` da `t_d` con la meccanica del G2 (`_return_end`, `_legs_after_bingo`:
    rotta di rientro, nessuna salva offensiva da `t_d`, a terra `parking_cold` sulla base raggiunta, o uscito di
    scena al punto di comparsa), motivo `BingoEnd.reason` = BINGO (ABORTED(BINGO)) o DISENGAGED
    (`AssetEndReason.DISENGAGED`, missione ABORTED(DISENGAGED), precedenza a parita' d'istante subito dopo il
    bingo nella regola unica della F6-B1);
  * **esaurimento sui tratti da `t_d`** (nuovi o invariati): `Fuel_Model.fuel_exhaustion(..., fuel=residuo)`
    (planata o perdita della F6-A anche sul rientro). Un aereo gia' in rientro (bingo o disingaggio) puo' essere
    ri-pianificato di nuovo SOLO per esaurimento (residuo zero o nuovo esaurimento), mai per un nuovo rientro.
**Ri-scheduling** (se i tratti di almeno un aereo sono cambiati): tratti di presenza, di movimento e programma a
terra degli aerei ri-pianificati sostituiti da `t_d` in poi (`route_presence`/`route_moving` prima del troncamento
all'esaurimento, `_fuel_truncated`, `_grounded_after_bingo`/`_grounded_after_fuel` sul programma pianificato);
`Contact_Scheduler.schedule_contacts` rieseguito con i tratti aggiornati sulle sole coppie con un aereo
ri-pianificato (`only_assets`, lo stesso sottoinsieme delle finestre senza filtro); delle nuove finestre si tengono
quelle che finiscono dopo `t_r`, ritagliate a `t_r` (`Contact_Scheduler.trim_contact_window`) e poi alle forze
occupate (`_trim_busy`); le finestre non ancora risolte di quegli aerei sono scartate; gli episodi non ancora
risolti sono ricostruiti (`_episodes`, stessa regola, stesso ordine). Gli episodi gia' risolti non cambiano
(causalita'). Rientri, esaurimenti, presenza, programma a terra, posture ed esiti sono letti dai dizionari finali;
la contabilita' del carburante usa i tratti definitivi.
**Terminazione**: gli episodi sono estratti in ordine di inizio non decrescente e ogni finestra nuova comincia non
prima di `t_r` (ritaglio) e della fine delle forze occupate; ogni ri-pianificazione di un aereo ne accorcia i
tratti (rientro o esaurimento) e un aereo in rientro non ne decide un altro: il ciclo termina.
Terra e mare: nessun consumo d'ingaggio e nessun rientro; una forza terrestre o navale disingaggiata resta passiva
sulla rotta (G4a), dichiarato. Spento: il G4a esattamente.
Limiti dichiarati: la decisione e' presa alla FINE dell'episodio, non a meta' (l'episodio e' risolto in blocco
con i tratti di prima; la riserva di disimpegno e' il carburante di quella coda); un aereo ri-pianificato che
incontrerebbe una forza ancora occupata in un episodio gia' risolto la incontra solo dopo la fine di quell'episodio
(forza occupata); l'uscita di scena e' sempre al punto di comparsa, anche quando il resto della rotta in avanti
fosse piu' corto o portasse fuori dalla zona delle minacce (decisione dell'utente: ritroso), e vale solo nella
ri-pianificazione dopo un episodio, non alla partenza; lo scheduler rieseguito vede lo stato degli asset a `t_r` (un asset distrutto o non piu'
operativo negli episodi gia' risolti non ha finestre nuove, mentre le sue finestre del primo scheduling restano,
come nel G4a); la formazione si puo' dividere (le decisioni sul carburante sono per aereo, il rientro forzato per
forza); il rientro non evita le minacce dell'andata (il ritroso le ripercorre, in episodi nuovi); un aereo
danneggiato oltre la soglia della F6-B1 resta passivo sulla rotta (nessun rientro per danno); aerei di una forza
disingaggiata ancora a terra (non decollati) a `t_r` non sono ri-pianificati.

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
- `counter`: dal G4a l'ordinale degli episodi con lo stesso insieme di forze nella sessione (0 per il
  primo, quindi lo stream di prima per ogni componente che e' un solo episodio), per lo stream
  dell'ingaggio e per quello della tempra; con `G4_EPISODES` spento sempre 0 (ogni componente e'
  risolta una sola volta per sessione).

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
`resolve_engagement`). Dalla F7a la callable e' avvolta, per gli asset di missioni aeree, dalla politica
d'armi per tipo di missione (v. "Regole d'ingaggio di missione (F7a)"); il contratto verso il risolutore non
cambia.

## Regole d'ingaggio di missione (F7a del piano della Missione, decisioni dell'utente del 2026-10-18)

`Analysis/Document/Proposta_F7_Bersagli_Filtro_Armi.md` §5. Due strati, ciascuno col proprio interruttore:
  * `F7_WEAPON_POLICY` (attivo): strato W. La fire control iniettata e' avvolta da
    `Fire_Control.restrict_by_policy` con la politica d'armi di ogni asset di missione AEREA
    (`Mission_Adapter.weapon_policies`, tabella `Context.MISSION_WEAPON_POLICY`): le opzioni d'arma che il
    tipo di missione non ammette contro la classe del bersaglio (aereo, difesa aerea, nave, altra superficie)
    sono tolte, con l'autodifesa aria-aria solo per i loadout con `self_escort_capability`. Spento: la fire
    control iniettata com'e'.
  * `F7_TARGET_RULES` (attivo): strato T. Per ogni asset la cui missione dichiara una ROE diversa da
    `weapon_free` o armi designate (`MissionAsset.weapons`, o l'arma del `AttackProfile`) la sessione passa
    al risolutore una `Engagement_Resolver.TargetRules` (`Mission_Adapter.target_rules`): bersaglio designato
    (`Target`, con `asset_ids` per un sottoinsieme del gruppo; POINT/AREA/ZONE come area), ROE, armi designate
    (sul designato solo quelle, sui non designati riservate). La memoria di `return_fire` e' PER SESSIONE:
    gli asset che hanno lanciato contro un dominio di coordinamento in un episodio gia' risolto sono passati
    come `known_hostile_ids` agli episodi successivi (dentro la stessa run il risolutore reagisce al lancio di un
    nuovo ostile). `priority_designated` ha due fasi, avvicinamento senza tiro sulle opportunita' di superficie e
    dopo l'attacco con le opportunita' ammesse: la fine dell'attacco e' il passaggio sul punto ATTACK della
    rotta dell'asset (`TargetRules.attack_point`, letto dai tratti REALI di ogni episodio, ri-pianificazioni
    comprese) o il designato distrutto (`known_destroyed_ids` dagli episodi precedenti). Spento: nessuna regola
    al risolutore.
Gli interruttori sono indipendenti; con entrambi spenti il comportamento e' quello precedente alla F7a anche per
missioni che dichiarano ROE e armi. Le validazioni nuove di `Mission_Types` e la coerenza fra
`MissionAsset.loadout` e il loadout assegnato all'aereo (`_check_missions`, `ValueError`) NON dipendono dagli
interruttori. Nessuna estrazione RNG nuova: un filtro che cambia una scelta sposta le estrazioni successive
dello stesso ingaggio.

## Fuoco su posizione (F7b del piano della Missione, decisione 15 dell'utente del 2026-10-20)

`Analysis/Document/Proposta_F7_Bersagli_Filtro_Armi.md` §6, `Logic/Area_Fire`. Interruttore `F7_AREA_FIRE` (attivo). Una
missione di terra o di mare con bersaglio POINT o AREA e un'azione `Fire_At_Point` (`Mission_Types.FIRE_AT_POINT_ACTION`,
`params = {'rounds', 'weapon'}`) su un waypoint spara sulla posizione STIMATA del bersaglio (N3.e) anche se nessuno e' stato
rilevato lassu': l'artiglieria che spara dove i blu erano. E' un terzo tipo di evento di sessione, `AREA_FIRE_EVENT`
(a parita' d'istante ENGAGEMENT < AREA_FIRE < MOVEMENT), NON un ingaggio: nessuna finestra di contatto, nessuna forza
d'ingaggio (`EngagementResult.forces` vuoto: niente tempra, disingaggio o shock sul colpito). Per ogni asset della missione
`Area_Fire.fire_orders` ricava un ordine (istante dal waypoint e dalla condizione d'avvio); la sessione stima a monte
l'istante d'impatto (`t_fire + time_of_flight` dell'arma scelta senza la scorta) e risolve l'evento in ordine di tempo fra
gli episodi d'ingaggio (prima di quelli che cominciano dopo l'impatto; con `G4_EPISODES` spento nella coda degli
ingaggi). All'impatto la scorta e' letta e le condizioni sono quelle di `Area_Fire.resolve_area_fire` (tiratore non
distrutto, passivo o a secco a `t_fire`: `inactive_from`, dal piu' vecchio fra distruzione, `passive_from`, fine di attivita'
nota a monte e esaurimento del carburante; arma con scorta e portata; nemici del tiratore dell'altro schieramento, mai
fuoco amico). Estrazioni dall'RNG di sessione con `order.rng(mission_id=<missione>, event_id=area_fire_event_id(ordine),
counter=0)`: stream separato da quelli degli ingaggi e della tempra, quindi le sessioni senza l'azione sono identiche a
prima. L'esito e' applicato subito agli asset reali (tutti i blocchi) e accodato a `results`/`resolved`: i `DamageEvent`
sono a `t_impact`, gli `AmmunitionEvent` a `t_fire`, le distruzioni entrano nelle conoscenze degli episodi successivi
(`_known_destructions`) e nell'esito per missione. In `SessionOutcome.engagement_outcomes` l'evento compare come un
ingaggio con zero forze. Spento: le azioni sono ignorate con un warning.
Limiti dichiarati: l'istante d'impatto che ordina l'evento e' stimato con l'arma preferita senza la scorta (se all'impatto
quell'arma e' esaurita e ne subentra un'altra con un tempo di volo diverso, l'esito porta il suo istante e non quello
d'ordinamento); un nemico distrutto da un episodio gia' risolto con un impatto POSTERIORE a quello dell'evento e' visto come
gia' distrutto; modello volutamente semplice (dispersione uniforme, letalita' a soglia, costanti STIMATE, aerei esclusi,
niente intercettazione).

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
Un asset il cui consumo cambia per effetto di un ingaggio (regime 'max', o dal G3 consumo d'ingaggio,
sotto) puo' esaurire prima del punto calcolato a monte: dal G4b, per gli aerei con il consumo d'ingaggio, il
punto e' RICALCOLATO alla fine di ogni episodio dal residuo analitico (v. "Ri-pianificazione dopo l'episodio
(G4b)"); col regime 'max' (G3 spento) resta il limite noto.

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
regime 'max' non e' ricavabile per l'asset si ricade su 'nominal'. Dal G3 (sotto, interruttore
`G3_ENGAGEMENT_FUEL`) questa regola vale solo per terra e mare (per i quali i due regimi coincidono) e, a
interruttore spento, per gli aerei.

**Consumo in ingaggio (G3 del nuovo modello di bingo, decisioni dell'utente del 2026-10-15, interruttore
`G3_ENGAGEMENT_FUEL`, attivo).** Sostituisce, per gli aerei, la sovrastima "tutto il movimento al regime 'max'
perche' ha combattuto":
  * il movimento di un aereo e' SEMPRE contabilizzato alla crociera (attese comprese, come prima);
  * a ogni ingaggio (`resolve_engagement` di un episodio, G4a; spento, di una componente connessa) a cui l'aereo
    PARTECIPA, l'aereo consuma
    nell'ISTANTE della sua prima partecipazione `Fuel_Model.engagement_fuel(asset)` = il carburante di
    `Fuel_Model.DISENGAGE_TIME` (5 minuti) alla massima spinta militare, la stessa quantita' della riserva di
    disimpegno del G1 (`Fuel_Model.build_engagement_fuel_event`: un `FuelEvent` istantaneo, distanza e durata
    nulle, regime `Fuel_Model.ENGAGEMENT_REGIME`, limitato al disponibile). Il codice conta un consumo per
    esito d'ingaggio: dal G4a uno per EPISODIO a cui l'aereo partecipa (con `G4_EPISODES` spento ogni forza
    e' in una sola componente per sessione, quindi al piu' un consumo per aereo e per sessione);
  * PARTECIPA (`_engagement_instants`) = la definizione di "ha combattuto" della F6-A (`_engaged_assets`): ha
    lanciato una salva, e' stato bersaglio di una salva (anche mancato o intercettato), o ha intercettato;
    istante = il primo fra il lancio delle salve sue o dirette a lui (`Salvo.t_launch`) e le sue
    intercettazioni. Il solo rilevamento reciproco senza salve NON e' partecipazione (nessuna manovra
    decisa dal modello);
  * solo aerei di MISSIONE (dominio 'air') IN VOLO all'istante: un aereo a terra (`grounded`: parcheggio prima
    del decollo, dopo l'atterraggio, aerei senza missione) colpito sul parcheggio non consuma;
  * ordine nella contabilita': i consumi d'ingaggio sono inseriti fra gli eventi per tratto in ordine di tempo,
    PRIMA del tratto in cui cadono (l'evento di quel tratto, all'istante della sua fine, parte dal residuo gia'
    ridotto): nessun tratto e' spezzato, la forma "un `FuelEvent` per tratto" della F6-A resta;
  * ESAURIMENTO in ingaggio (consumo d'ingaggio > residuo, o tratti successivi non piu' coperti): il contatore
    va a ZERO (mai negativo, `FuelEvent.exhausted`), nessun evento dopo. Dal G4b (`G4_REPLAN`) l'aereo e'
    ri-pianificato alla fine dell'episodio: a secco, regole della F6-A dal punto in cui si trova (planata su una
    base raggiungibile, altrimenti perso con l'equipaggio recuperato); sotto la soglia di bingo, rientro con
    l'albero del G2; tratti successivi non piu' coperti, nuovo esaurimento (v. "Ri-pianificazione dopo l'episodio
    (G4b)"). Con il G4b spento (il G3 e il G4a) l'aereo NON e' fermato ne' perso: tratti, contatti e ingaggio sono
    quelli calcolati a monte alla crociera, l'esaurimento e' della sola contabilita' (lo stesso limite della
    F6-A per il regime 'max', sotto) e il bingo resta valutato alla partenza (G2).
Terra e mare non cambiano (nessun consumo d'ingaggio: il registro non ha consumi per regime).
Spento: la regola della F6-A qui sopra, esattamente come prima.

**Limiti dichiarati:**
- il vincolo e' calcolato a monte al regime di CROCIERA: per un aereo che combatte la contabilita' al
  regime 'max' (dal G3: con i consumi d'ingaggio) puo' esaurire il carburante prima del punto di troncamento (`FuelEvent.exhausted` con
  `distance_covered < distance` sull'ultimo tratto) senza che il movimento sia ricalcolato (nessun
  ri-scheduling dopo gli ingaggi, P2/R4); per veicoli e navi i due regimi coincidono e il limite non
  si presenta. Dal G4b, con il consumo d'ingaggio del G3, il movimento E' ricalcolato alla fine di ogni episodio
  (resta solo la decisione presa a fine episodio e non a meta', v. "Ri-pianificazione dopo l'episodio (G4b)");
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

**Soglia di bingo e albero di decisione (G2 del nuovo modello di bingo, decisioni dell'utente del 2026-10-15,
interruttore `F6_BINGO_DISENGAGE_RESERVE`, attivo).** Sostituisce la regola 1,2 della F6-B2bis (e
`F6_BINGO_REVERSE_ROUTE` non e' letto). Soglia: l'aereo e' in bingo al primo istante in cui il residuo e' sotto
il carburante per il resto della rotta pianificata fino al LAND (attese comprese, alla crociera) + la riserva
di disimpegno (`Fuel_Model.disengagement_reserve`, G1). La funzione di decisione e' GENERALE
(`Fuel_Model.bingo_decision`, via `Mission_Adapter.mission_bingo_decision`: posizione e residuo qualunque),
ma con il solo consumo di movimento residuo e resto della rotta calano insieme, quindi la soglia scatta
all'inizio dei tratti oppure mai: la sessione la valuta all'inizio dei tratti della missione intera
(`airborne_legs`, come la F6-B2bis), con il carburante di partenza (`_decision_end`). Dal G3 un ingaggio abbassa
il residuo e la soglia puo' scattare dopo: dal G4b la sessione la rivaluta alla fine di ogni episodio a cui
l'aereo ha partecipato, col residuo di quell'istante (v. "Ri-pianificazione dopo l'episodio (G4b)"; e' esatto, non
un campionamento, perche' il residuo scende a scatti solo ai consumi d'ingaggio). Albero per tipo di missione (`Mission_Adapter.is_transfer_mission`, categoria TRANSPORT):
  * TRASFERIMENTO: se il residuo basta a CONCLUDERE la rotta (senza riserva) l'aereo CONTINUA, consuma la
    riserva, nessun aborto; altrimenti ritroso fino al DEPARTURE (all'inizio: lunghezza zero, resta a terra
    sul DEPARTURE con esito BINGO all'istante della partenza; partito in volo: diretto alla base del lato piu'
    vicina al punto di comparsa); altrimenti la base piu' vicina in linea retta; altrimenti verso la base piu'
    vicina e, a secco, le regole della F6-A (planata: ABORTED(FUEL); altrimenti perso, DESTROYED /
    FUEL_EXHAUSTED con l'equipaggio recuperato, `AssetMissionOutcome.crew_recovered`);
  * COMBATTIMENTO (ogni altro tipo): la missione si interrompe sempre; la candidata raggiungibile col percorso
    piu' breve fra la base di partenza (via piu' breve della F6-B2bis) e le basi del lato entro
    `Fuel_Model.ALTERNATE_BASE_MAX_OFFSET` (3000 m) dalla rotta programmata (lungo la rotta fino al punto piu'
    vicino, poi diretto con discesa); parita': la base di partenza, poi (x, y); nessuna raggiungibile: i passi
    3 e 4 del trasferimento. All'inizio dei tratti: resta a terra sul DEPARTURE o, partito in volo, va alla
    candidata migliore (per la disuguaglianza triangolare il diretto alla base piu' vicina al punto di comparsa
    non e' mai piu' lungo del percorso verso una base alternativa: le alternative contano lungo la rotta, dal G4b
    quando il bingo scatta dopo un episodio).
Raggiungibile = il residuo basta per il solo percorso alla crociera. Senza alcuna base (partenza in volo senza
basi del lato): alla partenza nessun rientro, regole della F6-A (come la F6-B2bis); dopo un episodio d'ingaggio
(G4b, `G4_OFF_SCENE_EXIT`) uscita di scena lungo la rotta a ritroso fino al punto di comparsa (v. "Ri-pianificazione
dopo l'episodio (G4b)"). Il rientro deciso diventa un `BingoEnd`
con la stessa meccanica della F6-B2bis (`_return_legs`, `_legs_after_bingo`, nessuna salva offensiva dal bingo,
a terra `parking_cold` sulla base raggiunta, BINGO / ABORTED(BINGO), un bingo oltre la fine della sessione non
c'e'). Il validatore `Mission_Adapter.check_mission_bingo` (con `disengage_reserve` True) rifiuta esattamente le
missioni che qui vanno in bingo. Spento: la F6-B2bis o la F6-B2, esattamente come prima.

## Sessione aperta (`SessionOrder.t_end is None`)

Regola conservativa: la durata **non si deduce**. Con `t_end` None il chiamante deve
passare `horizon` esplicito; con `t_end` valorizzato `horizon` e' ricavato (se passato
comunque deve coincidere). Nessuna durata di default inventata.

## Attivita' oltre la fine della sessione

Una salva lanciata poco prima della fine arriva comunque (payload congelato, R4): impatti e
risoluzioni possono cadere dopo `t_start + horizon`. L'esito non viene troncato (sarebbe
cancellare danni gia' decisi): il `t_end` del `SessionOutcome` e' esteso fino all'ultima
attivita', con un log. I contatti invece sono cercati solo dentro la sessione.

## Validazione di sessione (F8)
Il validatore di sessione e' FUORI da `run_session` (`Logic/Session_Validator.check_session`):
l'esecutore, sintetico o DCS, esegue; il pianificatore valida. `run_session` emette solo un
**warning** per ogni missione la cui fine pianificata supera la fine della sessione (E4 non
piu' silenzioso, nessun cambio di comportamento).

## Esito per la campagna (F8)
Oltre alle posture, `run_session` chiude la porta di uscita con tre dati per la campagna:
- `final_positions`: `{asset_id: (x, y, z) [m]}` di ogni asset alla fine NOMINALE della sessione
  (`session_end`, non `latest`: le salve in volo non muovono nessuno). Gli asset senza tratti (aereo
  perso alla partenza) non hanno posizione; posizione non applicata agli asset.
- `movement_ends`: `{asset_id: istante [s]}` in cui l'asset di missione ha smesso di muoversi nella
  sessione (arrivo all'ultimo punto, esaurimento del carburante); assente per gli asset senza missione.
- `operation_outcomes`: `{operation_id: OperationOutcome}` per ogni Operazione dell'ordine, aggregato
  dalla regola dichiarata (`Command/Session_Types.operation_outcome`, tabella §2.H della Proposta F8).

## Cosa NON fa
- Non costruisce `Theater_Session_Manager`, non legge/scrive `Campaign_State`.
- Non valida l'ordine di sessione (lo fa `Logic/Session_Validator`, v. sopra).
- Non applica le `final_positions` agli asset (lo fa `Session_Campaign.apply_final_positions`, F8c):
  `run_session` non muta la posizione degli asset.
- Non seleziona l'arma (lo fa la fire control iniettata; la politica d'armi di missione, F7a, la restringe; per il fuoco su
  posizione della F7b la sceglie `Fire_Control.area_fire_weapon`), non rifornisce (munizioni o carburante), non ri-instrada le forze
  TERRESTRI e NAVALI che si disingaggiano (restano segnalate nell'esito e, dal G4a, passive negli episodi
  successivi); dal G4b gli aerei di missione disingaggiati rientrano alla base.
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
    FIRE_AT_POINT_ACTION,
    AbortReason,
    ActionKind,
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
    operation_outcome,
)
from Code.Dynamic_War_Manager.Source.Logic import Area_Fire as AF
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

# Tipi di evento di sessione, nell'ordine di risoluzione a parita' d'istante (v. docstring). `AREA_FIRE_EVENT` (F7b,
# fuoco su posizione) sta fra l'ingaggio e il movimento: ENGAGEMENT < AREA_FIRE < MOVEMENT.
ENGAGEMENT_EVENT = 0
AREA_FIRE_EVENT = 1
MOVEMENT_EVENT = 2

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

# F6-B2bis, interruttore dedicato (stessa ragione dei precedenti), letto solo con `F6_BINGO` acceso e (dal G2)
# `F6_BINGO_DISENGAGE_RESERVE` spento:
#   * `F6_BINGO_REVERSE_ROUTE` (ATTIVO): rientro al bingo lungo la rotta percorsa A RITROSO fino al DEPARTURE
#     (partenza in volo: fino al punto di comparsa, poi diretto alla base del lato piu' vicina; anello: il
#     piu' breve fra ritroso e resto della rotta), fabbisogno `Fuel_Model.BINGO_RETURN_FACTOR` x il ritorno,
#     calcolato sulla missione intera (v. "Bingo" nel docstring). Spento: il rientro rettilineo con la
#     riserva `Fuel_Model.BINGO_RESERVE` della F6-B2, esattamente come prima. Il validatore
#     `Mission_Adapter.check_mission_bingo` segue lo stesso criterio con il suo parametro `reverse_route`.
F6_BINGO_REVERSE_ROUTE = True

# G2 del nuovo modello di bingo, interruttore dedicato (stessa ragione dei precedenti), letto solo con `F6_BINGO`
# acceso:
#   * `F6_BINGO_DISENGAGE_RESERVE` (ATTIVO): soglia di bingo = resto della rotta + riserva di disimpegno e
#     albero di decisione per tipo di missione (`Fuel_Model.bingo_decision` via
#     `Mission_Adapter.mission_bingo_decision`, v. "Bingo" nel docstring), valutato una sola volta all'inizio
#     dei tratti della missione (consumo deterministico, fino a G4); SOSTITUISCE la regola 1,2 della F6-B2bis e
#     `F6_BINGO_REVERSE_ROUTE` non e' letto. Spento: la F6-B2bis o la F6-B2 secondo `F6_BINGO_REVERSE_ROUTE`,
#     esattamente come prima. Il validatore `Mission_Adapter.check_mission_bingo` lo segue con il parametro
#     `disengage_reserve`.
F6_BINGO_DISENGAGE_RESERVE = True

# G3 del nuovo modello di bingo, interruttore dedicato (stessa ragione dei precedenti):
#   * `G3_ENGAGEMENT_FUEL` (ATTIVO): un aereo IN VOLO che partecipa a un ingaggio consuma, nell'istante della sua
#     prima partecipazione, il carburante di `Fuel_Model.DISENGAGE_TIME` alla massima spinta militare
#     (`Fuel_Model.engagement_fuel`, la riserva di disimpegno del G1), con un `FuelEvent` istantaneo; il suo
#     movimento resta alla crociera (v. "Consumo in ingaggio" nel docstring). Spento: la regola della F6-A,
#     tutto il movimento di chi ha combattuto al regime 'max', esattamente come prima. Terra e mare non
#     cambiano in nessun caso.
G3_ENGAGEMENT_FUEL = True

# G4a del nuovo modello di bingo (episodi d'ingaggio), interruttore dedicato (stessa ragione dei precedenti):
#   * `G4_EPISODES` (ATTIVO): l'ingaggio e' un EPISODIO nel tempo, non piu' la componente connessa di forze
#     dell'intera sessione: finestre di contatto legate perche' condividono una forza (o il dominio di
#     coordinamento) e si sovrappongono entro `EPISODE_GAP`; un `resolve_engagement` per episodio, in ordine di
#     tempo, con forza occupata fino alla fine dell'esito, stream RNG con `counter` = ordinale, forza disingaggiata
#     passiva negli episodi successivi (v. "Episodi d'ingaggio (G4a)" nel docstring). Spento: la componente
#     connessa, esattamente come prima.
G4_EPISODES = True

# G4b del nuovo modello di bingo (ri-pianificazione dopo l'episodio d'ingaggio), interruttore dedicato (stessa ragione
# dei precedenti), letto solo con `G4_EPISODES` acceso:
#   * `G4_REPLAN` (ATTIVO): alla fine di ogni episodio ogni aereo di missione in volo che vi ha consumato (G3) o la
#     cui forza si e' disingaggiata e' ri-pianificato da quell'istante: residuo analitico (`Fuel_Model.fuel_at`),
#     esaurimento in ingaggio (regole della F6-A), bingo (albero del G2) o rientro forzato dopo il disingaggio
#     (regola di combattimento), esaurimento sui nuovi tratti; tratti, programma a terra e contatti non ancora
#     risolti sono ricalcolati (v. "Ri-pianificazione dopo l'episodio (G4b)" nel docstring). Spento: il G4a
#     esattamente (bingo valutato solo alla partenza, esaurimento in ingaggio nel solo contatore).
G4_REPLAN = True
#   * `G4_OFF_SCENE_EXIT` (ATTIVO, decisione dell'utente del 2026-10-17), letto solo con `G4_REPLAN` acceso: un aereo
#     comparso in volo senza alcuna base aerea del suo lato che nella ri-pianificazione deve rientrare (bingo dopo
#     l'episodio o rientro forzato per disingaggio) ripercorre la rotta a ritroso fino al punto di comparsa e li'
#     ESCE DI SCENA (`Fuel_Model.BINGO_EXIT`, `BingoEnd.exits`). Spento: `BINGO_NO_BASE`, resta passivo sulla
#     rotta (il G4b fino al 2026-10-17). Sotto-interruttore per isolarne l'effetto nel confronto degli scenari.
G4_OFF_SCENE_EXIT = True

# F7a, regole d'ingaggio di missione (decisioni dell'utente del 2026-10-18), due interruttori separati e
# indipendenti (stessa ragione dei precedenti: la fotografia attribuisce le differenze a una sola causa):
#   * `F7_WEAPON_POLICY` (ATTIVO): strato W, politica d'armi per tipo di missione come involucro della fire control
#     (`Fire_Control.restrict_by_policy`, v. "Regole d'ingaggio di missione (F7a)"). Spento: la fire control
#     iniettata com'e'.
#   * `F7_TARGET_RULES` (ATTIVO): strato T, bersaglio designato, ROE e armi designate come `TargetRules` nel
#     risolutore. Spento: nessuna regola al risolutore. Con entrambi spenti: comportamento precedente alla F7a.
F7_WEAPON_POLICY = True
F7_TARGET_RULES = True

# F7b, fuoco su posizione (decisione 15 dell'utente del 2026-10-20), interruttore dedicato (stessa ragione dei precedenti):
#   * `F7_AREA_FIRE` (ATTIVO): le azioni `Fire_At_Point` delle missioni di terra e di mare con bersaglio POINT o AREA
#     sono risolte come eventi di sessione (`Logic/Area_Fire`, v. "Fuoco su posizione (F7b)"). Spento: le azioni sono
#     ignorate con un warning, come prima della F7b. Nessuno scenario precedente alla F7b dichiara l'azione, quindi
#     con l'interruttore acceso nessuna sessione precedente cambia.
F7_AREA_FIRE = True

# F8, stato "in corso" (decisione 23 dell'utente):
#   * `F8_IN_PROGRESS` (ATTIVO): una missione non distrutta, non completata e non abortita con almeno un asset
#     superstite ancora sulla rotta o sul posto alla fine della sessione (SESSION_END) e' IN_PROGRESS. Spento: FAILED,
#     come prima. La fotografia non registra lo stato di missione.
F8_IN_PROGRESS = True

# Intervallo [s] entro cui due finestre (di una stessa forza o dominio) che non si sovrappongono sono ancora lo
# stesso episodio. Decisione dell'utente del 2026-10-17: 300 s, cioe' `Fuel_Model.DISENGAGE_TIME`, i 5 minuti del
# disimpegno (STIMA dell'utente, G1): ritrovare il contatto entro il tempo del disimpegno e' lo stesso
# combattimento. Legato per costruzione: cambiare la durata del disimpegno cambia anche questo intervallo.
EPISODE_GAP = FM.DISENGAGE_TIME

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
        reason: motivo del rientro nell'esito per asset: BINGO (carburante) o, dal G4b, DISENGAGED (rientro
            forzato dopo il disingaggio della forza d'ingaggio). Stessa meccanica per i due.
        exits: USCITA DI SCENA (G4b, `G4_OFF_SCENE_EXIT`, `Fuel_Model.BINGO_EXIT`): `landing_point` e' il punto
            di comparsa dell'aereo partito in volo senza basi del lato; li', a `landing_time`, l'aereo lascia la
            scena senza atterrare: nessuna presenza dopo, non a terra, postura `off_scene`.
    """
    asset_id: str
    time: float
    point: Tuple[float, float, float]
    landing_point: Tuple[float, float, float]
    landing_time: float
    route: Tuple[Tuple[float, float, float], ...] = ()
    reason: AssetEndReason = AssetEndReason.BINGO
    exits: bool = False


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


def session_blocks(order: SessionOrder, forces_a: Iterable, forces_b: Iterable) -> Dict[str, object]:
    """I blocchi della sessione per id di dominio, con le stesse verifiche di `run_session`
    (F8: li usa il validatore di sessione). `_collect_forces(order, forces_a, forces_b)[2]`."""
    return _collect_forces(order, forces_a, forces_b)[2]


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


def _episodes(groups: Mapping[Tuple[str, str], List[CS.ContactWindow]],
              domain_of: Optional[Mapping[str, str]] = None,
              gap: Optional[float] = None) -> List[Tuple[Tuple[str, ...], List[CS.ContactWindow]]]:
    """Episodi d'ingaggio (G4a, v. "Episodi d'ingaggio (G4a)" nel docstring del modulo), con le finestre di ciascuno.

    Nodi: le finestre di `groups`; due finestre sono legate se hanno una forza in comune o (con `domain_of`) forze
    dello stesso dominio di coordinamento, E i loro intervalli si sovrappongono o distano al piu' `gap` secondi
    (default `EPISODE_GAP`). Episodio = componente connessa di questo grafo. Per ogni chiave (forza o dominio) le
    sue finestre, in ordine di `(t_start, t_end, posizione)`, sono scandite una volta come una fusione di
    intervalli: una finestra che comincia entro `gap` dalla fine piu' lontana raggiunta finora e' legata alla
    precedente (e' la componente di un grafo di intervalli); le chiavi sono unite con un union-find. La
    componente connessa di `_connected_components` e' l'unione dei suoi episodi; con `gap` infinito coincidono.

    Returns:
        `[(force_ids ordinati, finestre), ...]` in ordine di `(inizio della prima finestra, engagement_event_id)`,
        poi della prima finestra (mai l'ordine di un dizionario). Le finestre di un episodio sono nell'ordine di
        `_connected_components` (coppie ordinate, poi l'ordine nella coppia): una componente che e' un solo
        episodio ha esattamente le finestre di oggi, nello stesso ordine.

    Raises:
        ValueError: `gap` negativo.
    """
    gap = EPISODE_GAP if gap is None else float(gap)

    if gap < 0:
        raise ValueError(f"gap must be non-negative, got {gap!r}")

    entries = [(pair, window) for pair in sorted(groups) for window in groups[pair]]
    parent = list(range(len(entries)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    by_key: Dict[str, List[int]] = {}

    for index, (pair, _) in enumerate(entries):
        for key in sorted({(domain_of or {}).get(force_id, force_id) for force_id in pair}):
            by_key.setdefault(key, []).append(index)

    for key in sorted(by_key):
        reach, previous = None, None

        for index in sorted(by_key[key], key=lambda i: (entries[i][1].t_start, entries[i][1].t_end, i)):
            window = entries[index][1]

            if previous is not None and window.t_start <= reach + gap + CS.TIME_EPS:
                low, high = sorted((find(previous), find(index)))
                parent[high] = low
                reach = max(reach, window.t_end)
            else:
                reach = window.t_end

            previous = index

    members: Dict[int, List[int]] = {}

    for index in range(len(entries)):
        members.setdefault(find(index), []).append(index)

    episodes = []

    for indices in members.values():
        force_ids = tuple(sorted({force_id for index in indices for force_id in entries[index][0]}))
        windows = [entries[index][1] for index in indices]
        episodes.append(((min(w.t_start for w in windows), engagement_event_id(*force_ids), indices[0]),
                         force_ids, windows))

    episodes.sort(key=lambda episode: episode[0])
    return [(force_ids, windows) for _, force_ids, windows in episodes]


def _trim_busy(left: Dict[Tuple[str, str], List[CS.ContactWindow]], busy_until: Mapping[str, float],
               legs: Mapping[str, List[CS.Leg]]) -> bool:
    """Forza occupata (G4a): ritaglia SUL POSTO le finestre non ancora risolte in `left` perche' non comincino
    prima della fine dell'episodio gia' risolto di una delle due forze (`busy_until`); scarta quelle che si
    svuotano (`Contact_Scheduler.trim_contact_window`). True se qualcosa e' cambiato (gli episodi rimasti vanno
    ricostruiti)."""
    changed = False

    for pair in sorted(left):
        limit = max(busy_until.get(pair[0], float('-inf')), busy_until.get(pair[1], float('-inf')))
        kept = []

        for window in left[pair]:
            if limit <= window.t_start + CS.TIME_EPS:
                kept.append(window)
                continue

            changed = True
            trimmed = CS.trim_contact_window(window, limit, legs.get(window.asset_a_id, ()),
                                             legs.get(window.asset_b_id, ()))

            if trimmed is None:
                logger.info(f"run_session: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                            f"[{window.t_start:.1f}, {window.t_end:.1f}] dropped: force of {pair} busy in an "
                            f"earlier engagement episode until t={limit:.1f}")
            else:
                logger.info(f"run_session: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                            f"[{window.t_start:.1f}, {window.t_end:.1f}] trimmed to start at t={limit:.1f}: force "
                            f"of {pair} busy in an earlier engagement episode")
                kept.append(trimmed)

        left[pair] = kept

    return changed


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


def _engagement_instants(result: ER.EngagementResult) -> Dict[str, float]:
    """Istante della PRIMA partecipazione di ogni asset all'ingaggio (G3, v. "Consumo in ingaggio").

    Partecipa chi ha combattuto secondo `_engaged_assets` (tiratore, bersaglio di una salva, intercettore);
    l'istante e' il primo fra il lancio delle salve che ha sparato o che lo hanno avuto per bersaglio
    (`Salvo.t_launch`) e le sue intercettazioni (`InterceptionEvent.time`). Gli `AmmunitionEvent` hanno lo
    stesso istante del lancio della salva e non aggiungono nulla."""
    instants: Dict[str, float] = {}

    def note(asset_id, time):
        if asset_id is not None and (asset_id not in instants or time < instants[asset_id]):
            instants[asset_id] = float(time)

    for salvo in result.salvos:
        note(salvo.shooter_id, salvo.t_launch)
        note(salvo.target_id, salvo.t_launch)

    for event in result.interception_events:
        note(event.asset_id, event.time)

    return instants


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
              air_bases, fuel: Optional[float] = None) -> Optional[FuelEnd]:
    """Esaurimento del carburante dell'asset sui suoi tratti e suo esito (F6-A), o None se basta.

    `fuel` (G4b): residuo all'inizio di `consuming` (None = il carburante attuale dell'asset), per ricalcolare
    l'esaurimento da un istante qualunque (`Fuel_Model.fuel_exhaustion`). Esito: `_exhaustion_end`."""
    exhaustion = FM.fuel_exhaustion(asset, consuming, regime=CRUISE_REGIME, fuel=fuel)

    if exhaustion is None:
        return None

    return _exhaustion_end(asset, asset_id, domain, exhaustion.time, exhaustion.point, consuming, grounded, air_bases)


def _exhaustion_end(asset, asset_id: str, domain: str, time: float, point, consuming, grounded: CS.GroundedSchedule,
                    air_bases) -> FuelEnd:
    """Esito dell'esaurimento del carburante all'istante `time` nel punto `point` (F6-A).

    Terra/mare, o aereo ancora A TERRA all'esaurimento (o a quota <= 0): FUEL_HALT (fermo nel punto;
    l'aereo a terra, `on_ground`). Aereo in volo:
    planata in linea retta sulla base del suo lato (`air_bases`, `Mission_Adapter.air_base_points`)
    piu' vicina entro il raggio di planata (`Fuel_Model.nearest_reachable_base`), FUEL_GLIDE; nessuna
    base raggiungibile: FUEL_CRASH. Punto d'atterraggio = la posizione dell'asset di base piu' vicino,
    a quota 0 (il terreno non e' modellato). Velocita' di planata = la crociera dell'asset (in mancanza
    quella del tratto in corso): semplificazione dichiarata. Dal G4b anche per l'esaurimento IN INGAGGIO
    (punto e istante = quelli dell'aereo alla fine dell'episodio)."""
    point = tuple(float(c) for c in point)

    if domain != 'air':
        return FuelEnd(asset_id, FUEL_HALT, float(time), point)

    if grounded.at(asset_id, time) or point[2] <= 0.0:
        # A terra (o a quota nulla, es. serbatoio vuoto al decollo): resta fermo a terra nel punto.
        return FuelEnd(asset_id, FUEL_HALT, float(time), point, on_ground=True)

    base = FM.nearest_reachable_base(point, air_bases)

    if base is None:
        return FuelEnd(asset_id, FUEL_CRASH, float(time), point)

    landing = (base[0], base[1], 0.0)
    speed = FM.cruise_speed(asset) or _moving_speed(consuming, time)
    length = sqrt(sum((e - s) ** 2 for s, e in zip(point, landing)))
    duration = length / speed if speed else 0.0
    return FuelEnd(asset_id, FUEL_GLIDE, float(time), point, landing_time=float(time) + duration, landing_point=landing)


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


def _fuel_truncated(presence, moving, end: Optional[FuelEnd], t0: float, session_end: float
                    ) -> Tuple[Optional[List[CS.Leg]], List[CS.Leg]]:
    """(tratti di presenza, tratti di movimento) dell'asset con l'esaurimento `end` (F6-A): presenza troncata con
    l'esito (`_truncate_at_fuel_end`, lista anche vuota = l'asset non esiste nella sessione), movimento troncato
    all'esaurimento. Senza esaurimento i tratti dati; presenza None se vuota (asset fermo in posizione)."""
    if end is None:
        return (presence or None), moving

    return (_truncate_at_fuel_end(presence, end, t0, session_end),
            [leg for leg in CS.clamp_legs(moving, t0, end.time) if leg.duration > CS.TIME_EPS])


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

def _return_end(asset, asset_id: str, consuming, found) -> BingoEnd:
    """Il `BingoEnd` di un rientro gia' deciso (`Fuel_Model.BingoPoint` o `Fuel_Model.BingoDecision`: istante,
    punto, spezzata `route`, `base` e `return_length`), volato alla crociera dell'asset (in mancanza quella del
    tratto in corso), come la planata della F6-A. Una decisione d'uscita di scena (`BingoDecision.exits`, G4b) da'
    un `BingoEnd` con `exits`."""
    speed = FM.cruise_speed(asset) or _moving_speed(consuming, found.time)
    duration = found.return_length / speed if speed else 0.0
    return BingoEnd(asset_id, found.time, found.point, found.base, found.time + duration, found.route,
                    exits=bool(getattr(found, 'exits', False)))


def _bingo_end(asset, asset_id: str, consuming, air_bases, rule: Optional[FM.ReturnRule] = None) -> Optional[BingoEnd]:
    """Bingo dell'aereo sui suoi tratti che consumano e suo rientro, o None se non arriva al bingo (o il
    controllo non e' possibile).

    `rule` None (F6-B2): rientro in linea retta dal punto di bingo alla base del lato piu' vicina con la
    riserva. `rule` dato (F6-B2bis): rientro lungo la spezzata `Fuel_Model.BingoPoint.route` (rotta a
    ritroso, o resto della rotta sull'anello), e `consuming` sono i tratti della missione intera. In
    entrambi i casi alla crociera dell'asset (`_return_end`)."""
    bingo = FM.bingo_point(asset, consuming, air_bases, rule=rule)
    return None if bingo is None else _return_end(asset, asset_id, consuming, bingo)


def _decision_end(asset, asset_id: str, mission, movement, consuming, air_bases) -> Optional[BingoEnd]:
    """G2: la decisione al bingo all'inizio dei tratti della missione intera (`consuming`, quelli che consumano
    di `Mission_Adapter.airborne_legs`), con il carburante attuale (`Mission_Adapter.mission_bingo_decision`), e
    il suo rientro; None se l'aereo non e' in bingo, se CONTINUA (trasferimento: il residuo basta a concludere)
    o se non ha alcuna base a cui tornare (regole della F6-A). Rientro irraggiungibile (`BINGO_UNREACHABLE`):
    il `BingoEnd` verso la base piu' vicina; l'esaurimento lungo il rientro lo trattano poi le regole della
    F6-A."""
    decision = MA.mission_bingo_decision(mission, movement, asset, air_bases, legs=consuming)

    if decision is None:
        return None

    if not decision.returns:
        logger.info(f"run_session: asset {asset_id!r} starts under the bingo threshold (fuel {decision.fuel:.4f} < "
                    f"{decision.threshold:.4f}): {decision.action}, no return")
        return None

    return _return_end(asset, asset_id, consuming, decision)


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
    della sessione; un'uscita di scena (`end.exits`, G4b) non ha sosta: la presenza finisce al punto di
    comparsa (come l'aereo che finisce la rotta senza atterrare su una base vera, F5-B). Senza tratti degeneri."""
    kept = [leg for leg in CS.clamp_legs(legs, t0, end.time) if leg.duration > CS.TIME_EPS]
    kept.extend(_return_legs(end))

    if park and not end.exits:
        kept.append(CS.Leg(t_start=end.landing_time, t_end=max(float(session_end), end.landing_time),
                           p_start=end.landing_point, p_end=end.landing_point))

    return [leg for leg in CS.clamp_legs(kept, t0, session_end) if leg.duration > CS.TIME_EPS]


def _grounded_after_bingo(grounded: CS.GroundedSchedule, ends: Mapping[str, BingoEnd]) -> CS.GroundedSchedule:
    """Programma degli aerei a terra corretto per i rientri al bingo (F6-B2): gli intervalli a terra che
    cominciano dopo il bingo (atterraggio pianificato mai raggiunto) cadono; l'aereo e' a terra sulla base
    dall'atterraggio del rientro, tranne dopo un'uscita di scena (`BingoEnd.exits`, G4b: mai a terra)."""
    if not ends:
        return grounded

    intervals = {asset_id: list(grounded.intervals(asset_id)) for asset_id in grounded.ids()}

    for asset_id, end in ends.items():
        spans = [(lo, min(hi, end.time)) for lo, hi in intervals.get(asset_id, ()) if lo < end.time]

        if not end.exits:
            spans.append((end.landing_time, float('inf')))

        intervals[asset_id] = spans

    return CS.GroundedSchedule(intervals)


def _postures_after_bingo(postures: Dict[str, str], ends: Mapping[str, BingoEnd], mission_types: Mapping[str, str],
                          grounded: CS.GroundedSchedule, session_end: float) -> Dict[str, str]:
    """Postura a fine sessione degli aerei rientrati al bingo (F6-B2): a terra sulla base `PARKED_POSTURE`,
    ancora in volo verso la base il tipo di missione (un esaurimento successivo la corregge dopo, F6-A); uscito di
    scena al punto di comparsa entro la fine della sessione (`BingoEnd.exits`, G4b) `OFF_SCENE_POSTURE`."""
    for asset_id, end in ends.items():
        if asset_id not in postures:
            continue

        if end.exits and end.landing_time <= session_end + CS.TIME_EPS:
            postures[asset_id] = MA.OFF_SCENE_POSTURE
        else:
            postures[asset_id] = MA.PARKED_POSTURE if grounded.at(asset_id, session_end) else mission_types[asset_id]

    return postures


# ── FINE DI ATTIVITA' (F6-B1) ─────────────────────────────────────────────────

# Precedenza a parita' d'istante fra le fini di attivita' di un asset (scelta dichiarata, conta solo
# per fini simultanee): danno, winchester, bersaglio distrutto, durata.
_ACTIVITY_ORDER = (AssetEndReason.DAMAGE, AssetEndReason.WINCHESTER, AssetEndReason.TARGET_DESTROYED,
                   AssetEndReason.MAX_DURATION)
# Motivi di fine di un asset che fanno ABORTIRE la missione e il motivo d'aborto corrispondente.
# L'ordine e' la precedenza a parita' d'istante (F6-B2: il bingo subito dopo il carburante esaurito; G4b: il rientro
# forzato dopo il disingaggio subito dopo il bingo, scelta conservativa: prima i motivi di carburante, fatti fisici,
# poi la decisione tattica, poi munizioni e danno come prima).
_ABORT_REASON_OF = {AssetEndReason.FUEL_EXHAUSTED: AbortReason.FUEL,
                    AssetEndReason.BINGO: AbortReason.BINGO,
                    AssetEndReason.DISENGAGED: AbortReason.DISENGAGED,
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


def _restrict_to_asset_ids(mission, members: frozenset) -> frozenset:
    """`members` ristretto a `Target.asset_ids` se la missione lo dichiara (F7a), altrimenti `members`."""
    wanted = mission.target.asset_ids

    if not wanted:
        return members

    unknown = sorted(set(wanted) - members)

    if unknown:
        logger.warning(f"run_session: mission {mission.mission_id!r}: target asset_ids {unknown} are not in the "
                       f"target group, ignored")

    return members & frozenset(wanted)


def _mission_target_ids(mission, blocks: Mapping[str, object], mission_of: Mapping[str, object],
                        assets: Mapping[str, object]) -> frozenset:
    """Asset bersaglio della missione per il criterio `target_destroyed` (F6-B1).

    ASSET: l'asset `target_id`. GROUP: gli asset del blocco `target_id` fra quelli passati, oppure della
    missione `target_id` (un gruppo di missione), oppure l'asset `target_id`; con `Target.asset_ids` (F7a)
    solo quel sottoinsieme del gruppo (gli id fuori dal gruppo sono ignorati con un warning). POINT/AREA/ZONE:
    il bersaglio non e' un asset del modello (decisione 12 della F7a: nessun asset da distruggere), criterio
    non rappresentabile (warning). Non filtra per lato (S25-TGT).
    Vuoto (con un warning) se l'id non corrisponde a nulla fra le forze passate.
    """
    target = mission.target

    if target.kind not in (TargetKind.ASSET, TargetKind.GROUP):
        logger.warning(f"run_session: mission {mission.mission_id!r} declares target_destroyed on a "
                       f"{target.kind.name} target: not representable (no asset to destroy), ignored")
        return frozenset()

    target_id = target.target_id

    if target.kind is TargetKind.GROUP and target_id in blocks:
        members = frozenset(asset_id for asset_id in (_domain_id(a) for a in (getattr(blocks[target_id], 'assets', None)
                                                                              or {}).values())
                            if asset_id is not None)
        return _restrict_to_asset_ids(mission, members)

    if target.kind is TargetKind.GROUP and target_id in mission_of:
        return _restrict_to_asset_ids(mission, frozenset(mission_of[target_id].asset_ids))

    if target_id in assets:
        return _restrict_to_asset_ids(mission, frozenset((target_id,)))

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


def _activity_criteria(plans: Mapping[str, ActivityPlan], known: Optional[Mapping[str, float]],
                       reference_health: Optional[Mapping[str, int]] = None) -> Dict[str, ER.ActivityCriteria]:
    """I criteri nella forma del risolutore (`ER.ActivityCriteria`) per un ingaggio, con le distruzioni
    dei bersagli gia' note (`known`, None se nessun piano ha bersagli) e (G4a) la salute d'inizio sessione
    come riferimento della soglia di danno (`reference_health`, None = la salute all'ingresso nella run)."""
    criteria = {}

    for asset_id, plan in plans.items():
        destroyed = {target_id: known[target_id] for target_id in plan.target_ids if target_id in known} \
            if known is not None and plan.target_ids else {}
        reference = (reference_health or {}).get(asset_id) if plan.damage_threshold is not None else None
        criteria[asset_id] = ER.ActivityCriteria(
            winchester_weapons=plan.winchester_weapons, damage_threshold=plan.damage_threshold,
            target_ids=plan.target_ids, destroyed_targets=destroyed,
            until=plan.static_end[0] if plan.static_end is not None else None,
            reference_health=reference)

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
    """Ogni missione si riferisce a un blocco passato, i suoi asset gli appartengono, nessun suo
    tratto e' piu' veloce del mezzo piu' lento (regola A, `Mission_Adapter.check_mission_speed`) e il loadout
    dichiarato di ogni asset e' quello assegnato all'aereo (F7a, `ValueError`)."""
    for mission in order.missions:
        block = blocks.get(mission.block_id)

        if block is None:
            raise ValueError(f"mission {mission.mission_id!r}: block {mission.block_id!r} is not among the "
                             f"forces passed ({sorted(blocks)})")

        check_mission_assets(mission, block)
        assets = {_domain_id(asset): asset for asset in (getattr(block, 'assets', None) or {}).values()}
        MA.check_mission_speed(mission, assets, order.t_start)

        for mission_asset in mission.assets:
            # F7a (decisione 13): il motore usa `Aircraft.assigned_loadout`, la politica d'armi deve leggere lo
            # stesso loadout che la missione dichiara.
            if mission_asset.loadout is not None \
                    and mission_asset.loadout != getattr(assets.get(mission_asset.asset_id), 'assigned_loadout', None):
                raise ValueError(f"mission {mission.mission_id!r}: asset {mission_asset.asset_id!r} declares "
                                 f"loadout {mission_asset.loadout!r} but its assigned loadout is "
                                 f"{getattr(assets.get(mission_asset.asset_id), 'assigned_loadout', None)!r}")

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
            # Aereo a secco in volo senza base raggiungibile (F6-A, anche sul rientro al bingo del G2): perso per
            # carburante, con l'equipaggio recuperato (decisione dell'utente del 2026-10-15).
            outcome = AssetMissionOutcome(asset_id, AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, crashed_at,
                                          crew_recovered=True)
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
                # Rientro al bingo (F6-B2) o, dal G4b, rientro forzato dopo il disingaggio (motivo DISENGAGED):
                # l'asset ha lasciato la rotta all'istante della decisione.
                outcome = AssetMissionOutcome(asset_id, state, bingo.reason, bingo.time)
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
    elif F8_IN_PROGRESS and any(o.end_reason is AssetEndReason.SESSION_END for o in survivors):
        status = MissionStatus.IN_PROGRESS
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

    Danno e munizioni sono applicati agli asset reali man mano che gli ingaggi sono risolti (dal
    G4a un ingaggio per episodio, con `G4_EPISODES` spento uno per componente connessa di forze, v.
    docstring del modulo), il carburante in un passo finale. Dal G4b, dopo ogni episodio, gli aerei di
    missione sotto la soglia di bingo, a secco o la cui forza si e' disingaggiata sono ri-pianificati e i
    loro contatti non ancora risolti ricalcolati (v. "Ri-pianificazione dopo l'episodio (G4b)"). Il
    `SessionOutcome` restituito e' il resoconto di cio' che e' stato applicato.

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
            `order.rng(event_id=temper_event_id(*forze), counter=ordinale dell'episodio)`, separato da
            quello dell'ingaggio. Il
            dominio di coordinamento (`coordination_of`) e' ricavato dalle missioni e da
            `order.operations` (v. "Dominio di coordinamento").

    Returns:
        Il `SessionOutcome`, con un `MissionOutcome` per missione dell'ordine, un `ForceOutcome`
            per forza d'ingaggio (missione) che ha combattuto e per episodio (G4a) e la postura a fine sessione di ogni
            asset delle forze passate (`postures`, F5-B); senza ingaggi ne' movimenti resta valido,
            con le sole posture.

    Raises:
        TypeError: `order` non e' un SessionOrder, `fire_control` non chiamabile.
        ValueError: durata mancante o incoerente, forze/asset duplicati o fuori
            `order.force_ids`, missione di un blocco non passato o con asset di altri blocchi,
            `mission_id` uguale all'id di un blocco, loadout di missione diverso da quello assegnato
            all'aereo (F7a), e gli errori di dominio dei moduli chiamati.
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
    # F8: warning per le missioni pianificate oltre la fine della sessione (E4).
    # Il validatore di sessione (Logic/Session_Validator) le rifiuta; qui solo il warning.
    for mission in order.missions:
        end = MA.mission_planned_end(mission, mission_movements[mission.mission_id])
        if end is not None and end > session_end + CS.TIME_EPS:
            logger.warning(f"run_session: mission {mission.mission_id!r} is planned to end at t={end:.1f}, "
                           f"after the session end t={session_end:.1f}: its route is cut (E4); the session "
                           f"validator (Logic/Session_Validator) rejects it")
    routes, starts, speeds = MA.session_movements(order.missions, t0)
    # Aerei a terra nel tempo (F4c + F5): sempre gli aerei senza missione, a intervalli quelli di
    # missione prima del decollo e dopo l'atterraggio su una base vera. V. docstring del modulo.
    grounded = MA.grounded_schedule(forces, movement_of.values())
    # G4b: il programma a terra PIANIFICATO, base delle correzioni per bingo ed esaurimento (ricalcolate dopo ogni
    # ri-pianificazione con gli stessi `_grounded_after_bingo` / `_grounded_after_fuel`).
    planned_grounded = grounded
    assets_by_id: Dict[str, object] = {}

    for force_id in sorted(blocks):
        for asset in (getattr(blocks[force_id], 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is not None:
                assets_by_id[asset_id] = asset

    # F7a: strato W (politica d'armi per tipo di missione) come involucro della fire control, PRIMA di ogni suo
    # uso (tutti gli episodi e la ri-pianificazione); strato T (regole di bersaglio) per il risolutore.
    if F7_WEAPON_POLICY:
        policies = MA.weapon_policies(order.missions, assets_by_id)

        if policies:
            fire_control = FC.restrict_by_policy(fire_control, policies)

    target_rules = MA.target_rules(order.missions, blocks, {m.mission_id: m for m in order.missions}, assets_by_id,
                                   {block_id: getattr(block, 'side', None) for block_id, block in blocks.items()}) \
        if F7_TARGET_RULES else {}
    # Memoria di `return_fire` per sessione: chi ha lanciato contro ciascun dominio di coordinamento negli
    # episodi gia' risolti.
    hostile_of: Dict[str, set] = {}

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
    # LAND); un bingo che cadrebbe dopo la fine della sessione non c'e' nella sessione. G2
    # (`F6_BINGO_DISENGAGE_RESERVE`): soglia resto della rotta + riserva e albero di decisione, valutati una
    # volta all'inizio dei tratti della missione intera (`_decision_end`).
    bingo_ends: Dict[str, BingoEnd] = {}

    for asset_id, movement in movement_of.items():
        asset = assets_by_id.get(asset_id)
        mission = mission_of[movement.mission_id]

        if not F6_BINGO or asset is None or not moving_legs[asset_id] or mission.domain != 'air' \
                or not mission.end_criteria.bingo:
            continue

        bases = air_bases.get(getattr(blocks[mission.block_id], 'side', None), ())

        if F6_BINGO_DISENGAGE_RESERVE:
            end = _decision_end(asset, asset_id, mission, movement,
                                _consuming_legs(asset_id, MA.airborne_legs(movement), grounded), bases)

            if end is not None and end.time >= session_end - CS.TIME_EPS:
                end = None
        elif F6_BINGO_REVERSE_ROUTE:
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
    # G4b: tratti di presenza e di movimento PRIMA del troncamento all'esaurimento (con l'eventuale rientro al bingo),
    # da cui la ri-pianificazione ricava i tratti definitivi con un nuovo esaurimento (`_fuel_truncated`).
    route_presence: Dict[str, List[CS.Leg]] = {}
    route_moving: Dict[str, List[CS.Leg]] = {}

    for asset_id, movement in movement_of.items():
        legs = MA.movement_legs(movement, t0, session_end)

        if asset_id in bingo_ends:
            # F6-B2: fino al bingo, rientro e sosta a terra sulla base.
            legs = _legs_after_bingo(legs, bingo_ends[asset_id], t0, session_end, park=True)

        route_presence[asset_id], route_moving[asset_id] = legs, moving_legs[asset_id]
        presence, moving_legs[asset_id] = _fuel_truncated(legs, moving_legs[asset_id], fuel_ends.get(asset_id), t0,
                                                          session_end)

        if presence is not None:
            presence_legs[asset_id] = presence

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

    for force_id in sorted(blocks):
        for asset in (getattr(blocks[force_id], 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is None:
                continue

            if asset_id in presence_legs:
                all_legs[asset_id] = presence_legs[asset_id]
            else:
                all_legs[asset_id] = CS.static_legs(getattr(asset, 'position', None), t0, session_end)

    # ── strato 2: ingaggi (coda eventi ENGAGEMENT) ────────────────────────────
    committed = _engagement_committed(order, forces)
    results: List[Optional[ER.EngagementResult]] = []
    # Ingaggi risolti nell'ordine di risoluzione, con l'istante e l'id della loro voce di coda: la contabilita'
    # del carburante (passo finale, sotto) li ripercorre nello stesso ordine (G4a).
    resolved: List[Tuple[float, str, Optional[ER.EngagementResult]]] = []
    # G4a (v. "Episodi d'ingaggio (G4a)"): salute d'inizio sessione (riferimento della soglia di danno), istante
    # dal quale un asset e' PASSIVO per un disingaggio o una fine di attivita' in un episodio gia' risolto, fine
    # dell'ultimo episodio di ogni forza (forza occupata) e ordinale degli episodi per insieme di forze (`counter`
    # dell'RNG). Con un solo episodio per componente sono tutti senza effetto.
    start_health = {asset_id: asset.health for asset_id, asset in assets_by_id.items()
                    if isinstance(getattr(asset, 'health', None), int) and not isinstance(asset.health, bool)} \
        if G4_EPISODES else None
    passive_from: Dict[str, float] = {}
    busy_until: Dict[str, float] = {}
    ordinals: Dict[str, int] = {}

    # G4b (v. "Ri-pianificazione dopo l'episodio (G4b)"): carburante d'inizio sessione (la contabilita' e' il passo
    # finale, quindi durante gli episodi il contatore e' ancora quello di partenza; copiato per chiarezza), consumi
    # d'ingaggio gia' avvenuti per aereo `(istante, quantita')` (la stessa regola della contabilita') e aerei di
    # missione, i soli che consumano in ingaggio.
    air_assets = {asset_id for asset_id, movement in movement_of.items()
                  if mission_of[movement.mission_id].domain == 'air'}
    start_fuel = {asset_id: getattr(asset, 'fuel', None) for asset_id, asset in assets_by_id.items()}
    charges_of: Dict[str, List[Tuple[float, float]]] = {}
    replanning = G4_EPISODES and G4_REPLAN

    # F7b: fuoco su posizione (v. "Fuoco su posizione (F7b)"). Gli ordini di fuoco delle azioni `Fire_At_Point` delle
    # missioni di terra e di mare, per istante d'impatto stimato A MONTE (arma scelta senza la scorta, che e' letta al
    # momento della risoluzione) e id: un evento di sessione per ordine, risolto in ordine di tempo fra gli episodi
    # d'ingaggio (ENGAGEMENT < AREA_FIRE < MOVEMENT a parita' d'istante).
    area_events: List[Tuple[float, str, AF.FireOrder]] = []

    def position_of(asset_id, time):
        legs = all_legs.get(asset_id)
        return CS.position_on_legs(legs, time) if legs else None

    def inactive_from(asset_id):
        """Istante dal quale l'asset non spara piu': distrutto, passivo (disingaggio, fine di attivita' scattata in un
        episodio gia' risolto), fine di attivita' nota a monte (durata massima, winchester) o a secco; None = attivo."""
        instants = []
        destroyed = _destruction_times(results, assets_by_id, t0)

        if asset_id in destroyed:
            instants.append(destroyed[asset_id])

        if asset_id in passive_from:
            instants.append(passive_from[asset_id])

        plan = activity_plans.get(asset_id)

        if plan is not None and plan.static_end is not None:
            instants.append(plan.static_end[0])

        fuel_end = fuel_ends.get(asset_id)

        if fuel_end is not None:
            instants.append(fuel_end.time)

        return min(instants) if instants else None

    def fire_area(fire_order: AF.FireOrder) -> None:
        shooter = assets_by_id.get(fire_order.asset_id)
        side = block_owner[fire_order.asset_id][0]
        # Solo i nemici del tiratore (l'altro schieramento): niente fuoco amico (decisione 15d).
        enemies = [asset for asset_id, asset in assets_by_id.items()
                   if asset_id in block_owner and block_owner[asset_id][0] != side]
        event_id = AF.area_fire_event_id(fire_order)
        result = AF.resolve_area_fire(fire_order, shooter, enemies, position_of,
                                      order.rng(mission_id=fire_order.mission_id, event_id=event_id, counter=0),
                                      provenance, inactive_from=inactive_from(fire_order.asset_id),
                                      grounded_at=lambda asset_id, time: grounded.at(asset_id, time))

        if result is None:
            return

        results.append(result)
        resolved.append((result.t_end, event_id, result))
        # Applicato SUBITO, a tutti i blocchi: tiratore (scorta) e colpiti (salute); le distruzioni entrano nelle
        # conoscenze degli episodi successivi (`_known_destructions` sui `results`).
        ER.apply_engagement_result(result, *blocks.values())

    def fire_due(before: Optional[float] = None) -> None:
        """Risolve gli eventi di fuoco su posizione con istante d'impatto STRETTAMENTE anteriore a `before` (a parita'
        d'istante l'ingaggio precede, v. AREA_FIRE_EVENT), o tutti quelli rimasti con `before` None."""
        while area_events and (before is None or area_events[0][0] < before - CS.TIME_EPS):
            fire_area(area_events.pop(0)[2])

    if F7_AREA_FIRE:
        for asset_id, movement in movement_of.items():
            mission = mission_of[movement.mission_id]
            shooter = assets_by_id.get(asset_id)

            for fire_order in AF.fire_orders(mission, movement, t0):
                weapon = AF.plan_shot(fire_order, shooter, position_of) if shooter is not None else None

                if weapon is None or fire_order.t_fire > session_end + CS.TIME_EPS:
                    logger.warning(f"run_session: {AF.area_fire_event_id(fire_order)!r} not scheduled: no usable "
                                   f"weapon, range or position at t={fire_order.t_fire:.1f}, or after the session end")
                    continue

                area_events.append((AF.impact_time(fire_order, weapon), AF.area_fire_event_id(fire_order),
                                    fire_order))

        area_events.sort(key=lambda event: (event[0], event[1]))
    elif any(action.kind is ActionKind.TASK and action.name == FIRE_AT_POINT_ACTION
             for mission in order.missions for waypoint in mission.waypoints for action in waypoint.actions):
        logger.warning(f"run_session: F7_AREA_FIRE is off: the {FIRE_AT_POINT_ACTION!r} actions of the missions "
                       f"are ignored")

    def replan(result) -> Dict[str, float]:
        """G4b: ri-pianifica, alla fine dell'episodio risolto `result`, gli aerei di missione in volo che vi hanno
        consumato o la cui forza si e' disingaggiata; aggiorna rientri, esaurimenti, tratti e programma a terra.
        Restituisce `{asset_id: istante da cui i suoi tratti sono cambiati}` (vuoto = nulla da ri-schedulare)."""
        nonlocal grounded
        t_r = result.t_end

        if t_r is None:
            return {}

        t_r = float(t_r)
        consumed = set()

        if G3_ENGAGEMENT_FUEL:
            # Stessa regola della contabilita' (G3): aerei di missione IN VOLO all'istante della prima partecipazione.
            for asset_id, instant in sorted(_engagement_instants(result).items()):
                asset = assets_by_id.get(asset_id)

                if asset is None or asset_id not in air_assets or grounded.at(asset_id, instant):
                    continue

                amount = FM.engagement_fuel(asset)

                if amount is not None:
                    charges_of.setdefault(asset_id, []).append((instant, amount))
                    consumed.add(asset_id)

        disengaged = set()

        if F6_BINGO and F6_BINGO_DISENGAGE_RESERVE:
            # Decisione dell'utente del 2026-10-17: un aereo di missione la cui FORZA d'ingaggio si e' disingaggiata
            # nell'episodio rientra con la regola di combattimento, indipendentemente dal carburante.
            for force_outcome in result.forces:
                mission = mission_of.get(force_outcome.force_id)

                if force_outcome.outcome == ER.DISENGAGED and mission is not None and mission.domain == 'air':
                    disengaged.update(mission.asset_ids)

        changed: Dict[str, float] = {}

        for asset_id in sorted(consumed | disengaged):
            asset = assets_by_id.get(asset_id)
            movement = movement_of.get(asset_id)

            if asset is None or movement is None or getattr(asset, 'is_destroyed', lambda: False)() \
                    or start_fuel.get(asset_id) is None:
                continue

            moving = moving_legs.get(asset_id) or []
            exhausted = fuel_ends.get(asset_id)

            if not moving:
                continue

            # Istante della decisione per l'aereo: la fine dell'episodio o, se la sua rotta nella sessione finisce
            # prima (rotta completata DENTRO l'episodio), la fine dei suoi tratti di movimento; in quel caso conta
            # solo l'esaurimento (A.2), non c'e' piu' rotta da cui rientrare.
            t_d = min(t_r, float(moving[-1].t_end))
            completed = t_d < t_r - CS.TIME_EPS

            if t_d >= session_end - CS.TIME_EPS:
                # Nessuna ri-pianificazione oltre la sessione (come un bingo che cadrebbe dopo la fine).
                continue

            # In volo a `t_d`: dentro i suoi tratti di movimento, non a terra, non gia' a secco (planata o perso).
            if t_d < moving[0].t_start - CS.TIME_EPS or grounded.at(asset_id, t_d) \
                    or (exhausted is not None and exhausted.time <= t_d + CS.TIME_EPS):
                continue

            mission = mission_of[movement.mission_id]
            bases = air_bases.get(getattr(blocks[mission.block_id], 'side', None), ())
            residual = FM.fuel_at(asset, _consuming_legs(asset_id, moving, grounded), t_d,
                                  charges_of.get(asset_id, ()), fuel=start_fuel[asset_id], regime=CRUISE_REGIME)

            if residual is None:
                continue

            previous = bingo_ends.get(asset_id)
            # Gia' in rientro (bingo o disingaggio): nessun nuovo rientro, solo l'esaurimento (A.2/A.4).
            returning = previous is not None and previous.time <= t_d + CS.TIME_EPS
            bingo = previous

            if residual <= 0.0:
                # A.2: esaurito in ingaggio, regole della F6-A dal punto in cui l'aereo e' alla fine dell'episodio (un
                # bingo calcolato a monte per piu' tardi, regole a G2 spento, non avviene piu').
                point = CS.position_on_legs(route_presence.get(asset_id) or moving, t_d) \
                    or CS.position_on_legs(moving, t_d)

                if point is None:
                    continue

                bingo = previous if returning else None
                end = _exhaustion_end(asset, asset_id, mission.domain, t_d, point, moving, grounded, bases)
            elif completed:
                continue
            else:
                if not returning and F6_BINGO and F6_BINGO_DISENGAGE_RESERVE:
                    mission_legs = _consuming_legs(asset_id, MA.airborne_legs(movement), grounded)
                    decision, reason = None, AssetEndReason.BINGO
                    # Partenza in volo senza basi del lato: uscita di scena al punto di comparsa (decisione
                    # dell'utente del 2026-10-17) invece di `BINGO_NO_BASE`, solo qui (non alla partenza, G2).
                    exit_scene = G4_OFF_SCENE_EXIT

                    if asset_id in consumed and mission.end_criteria.bingo:
                        # A.3: bingo con il residuo dopo il consumo d'ingaggio, albero del G2 sulla missione intera.
                        decision = MA.mission_bingo_decision(mission, movement, asset, bases, time=t_d, fuel=residual,
                                                             legs=mission_legs, exit_scene=exit_scene)

                        if decision is not None and not decision.returns:
                            logger.info(f"run_session: asset {asset_id!r} under the bingo threshold after the "
                                        f"engagement episode at t={t_d:.1f} (fuel {decision.fuel:.4f} < "
                                        f"{decision.threshold:.4f}): {decision.action}, no return")
                            decision = None

                    if decision is None and asset_id in disengaged:
                        # B: rientro forzato dopo il disingaggio, regola di combattimento, nessuna soglia.
                        decision = MA.mission_bingo_decision(mission, movement, asset, bases, time=t_d, fuel=residual,
                                                             legs=mission_legs, forced=True, exit_scene=exit_scene)
                        reason = AssetEndReason.DISENGAGED

                        if decision is not None and not decision.returns:
                            logger.info(f"run_session: asset {asset_id!r} disengaged at t={t_d:.1f} has no base to "
                                        f"return to ({decision.action}): it stays on its route, passive")
                            decision = None

                    if decision is not None:
                        bingo = dataclasses.replace(_return_end(asset, asset_id, mission_legs, decision), reason=reason)
                        logger.info(f"run_session: asset {asset_id!r} returns after the engagement episode "
                                    f"({reason.value}) at t={t_d:.1f} to {bingo.landing_point}, "
                                    f"{'leaving the scene' if bingo.exits else 'landing'} at "
                                    f"t={bingo.landing_time:.1f}")

                if bingo != previous:
                    # Rotta nuova da `t_d`: i tratti pianificati fino a `t_d`, poi il rientro (come al bingo del G2).
                    presence = _legs_after_bingo(MA.movement_legs(movement, t0, session_end), bingo, t0, session_end,
                                                 park=True)
                    moving_route = _legs_after_bingo(MA.movement_legs(movement, t0, session_end, presence=False), bingo,
                                                     t0, session_end, park=False)
                elif asset_id in consumed:
                    presence, moving_route = route_presence[asset_id], route_moving[asset_id]
                else:
                    # Nessun consumo in questo episodio e nessuna rotta nuova: l'esaurimento noto resta valido.
                    continue

                # A.4: esaurimento sui tratti da `t_d` con il residuo.
                after = [leg for leg in CS.clamp_legs(_consuming_legs(asset_id, moving_route, grounded), t_d,
                                                      float('inf')) if leg.duration > CS.TIME_EPS]
                end = _fuel_end(asset, asset_id, mission.domain, after, grounded, bases, fuel=residual)
                route_presence[asset_id], route_moving[asset_id] = presence, moving_route

            if bingo is None:
                bingo_ends.pop(asset_id, None)
            else:
                bingo_ends[asset_id] = bingo

            if end is None:
                fuel_ends.pop(asset_id, None)
            else:
                fuel_ends[asset_id] = end
                logger.info(f"run_session: asset {asset_id!r} runs out of fuel at t={end.time:.1f} ({end.kind}), "
                            f"re-planned at t={t_d:.1f} after the engagement episode ending at t={t_r:.1f}")

            if bingo == previous and end == exhausted:
                continue

            # Istante da cui i tratti cambiano: la decisione (rientro, esaurimento in ingaggio) o il primo dei due
            # esaurimenti, vecchio e nuovo (solo esaurimento anticipato sui tratti di prima).
            since = [t_d] if bingo != previous else []
            since += [e.time for e in (end, exhausted) if e is not None] if end != exhausted else []
            presence, moving_legs[asset_id] = _fuel_truncated(route_presence[asset_id], route_moving[asset_id], end,
                                                              t0, session_end)

            if presence is not None:
                presence_legs[asset_id] = presence
                all_legs[asset_id] = presence
            else:
                presence_legs.pop(asset_id, None)
                all_legs[asset_id] = CS.static_legs(getattr(asset, 'position', None), t0, session_end)

            changed[asset_id] = min(since)

        if changed:
            grounded = _grounded_after_fuel(_grounded_after_bingo(planned_grounded, bingo_ends), fuel_ends)

        return changed

    def engage(time, force_ids, group, event_id):
        component = [forces[force_id] for force_id in force_ids]
        # G4a: `counter` = ordinale degli episodi con lo STESSO insieme di forze (0 per il primo: lo stream di
        # prima), per lo stream dell'ingaggio e per quello della tempra (tempra nuova per episodio).
        counter = ordinals.get(event_id, 0)
        ordinals[event_id] = counter + 1
        # F6-B1: criteri passati solo se dichiarati (senza, la chiamata e' quella di prima), con le
        # distruzioni dei bersagli note a questo punto (ingaggi gia' risolti, carburante).
        extra = {}
        criteria = {}

        if activity_plans:
            known = _known_destructions(results, assets_by_id, t0, fuel_ends) if plans_with_targets else None
            criteria = _activity_criteria(activity_plans, known, start_health)

        # F6-B2: dal bingo l'aereo rientra e non lancia piu' salve offensive (fine nota a monte, `until`).
        for asset_id, bingo in bingo_ends.items():
            known_criteria = criteria.get(asset_id)

            if known_criteria is None:
                criteria[asset_id] = ER.ActivityCriteria(until=bingo.time)
            elif known_criteria.until is None or bingo.time < known_criteria.until:
                criteria[asset_id] = dataclasses.replace(known_criteria, until=bingo.time)

        if passive_from:
            # G4a: passivo (nessuna salva offensiva, resta bersaglio e intercettore) l'asset che si e' disingaggiato
            # o ha chiuso l'attivita' in un episodio precedente; stesso meccanismo del bingo, solo per gli asset
            # delle forze di questo episodio.
            members = {_domain_id(asset) for force in component
                       for asset in (getattr(force, 'assets', None) or {}).values()}

            for asset_id in sorted(members & set(passive_from)):
                until = passive_from[asset_id]
                known_criteria = criteria.get(asset_id)

                if known_criteria is None:
                    criteria[asset_id] = ER.ActivityCriteria(until=until)
                elif known_criteria.until is None or until < known_criteria.until:
                    criteria[asset_id] = dataclasses.replace(known_criteria, until=until)

        if criteria:
            extra['activity_criteria'] = criteria

        if target_rules:
            # F7a: regole di bersaglio, con gli ostili noti del dominio di coordinamento di ogni tiratore.
            rules_now = {}

            for asset_id, rules in target_rules.items():
                if asset_id not in owner:
                    continue

                hostile = hostile_of.get(coordination.get(owner[asset_id][1]))
                # Designati gia' distrutti (episodi precedenti): fine dell'attacco di `priority_designated`.
                destroyed = frozenset(
                    designated for designated in rules.designated_ids
                    if callable(getattr(assets_by_id.get(designated), 'is_destroyed', None))
                    and assets_by_id[designated].is_destroyed()) if rules.designated_ids else frozenset()
                rules_now[asset_id] = dataclasses.replace(rules, known_hostile_ids=frozenset(hostile or ()),
                                                          known_destroyed_ids=destroyed) \
                    if hostile or destroyed else rules

            extra['target_rules'] = rules_now

        result = ER.resolve_engagement(component[0], component[1], group, fire_control,
                                       order.rng(mission_id=None, event_id=event_id, counter=counter),
                                       extra_forces=component[2:],
                                       legs=all_legs, committed=committed,
                                       thresholds=thresholds,
                                       reaction_profile_for=reaction_profile_for,
                                       detection_factor=detection_factor,
                                       salvo_window=order.salvo_window,
                                       provenance=provenance,
                                       breakpoint_rng=order.rng(mission_id=None,
                                                                event_id=temper_event_id(*force_ids),
                                                                counter=counter),
                                       morale_for=morale_for,
                                       enemy_estimate_for=enemy_estimate_for,
                                       fire_doctrine=fire_doctrine,
                                       coordination_of=coordination,
                                       grounded=grounded, **extra)
        results.append(result)
        resolved.append((time, event_id, result))

        if result is None:
            return None

        # Applicato SUBITO, a tutte le forze dell'ingaggio: un episodio successivo delle stesse forze (G4a) parte
        # dallo stato gia' consumato (salute e scorte), i `health_before/after` sono concatenati.
        ER.apply_engagement_result(result, *component)

        for salvo in result.salvos:
            # F7a: ostili noti per `return_fire`, agli episodi successivi.
            hostile_of.setdefault(coordination.get(salvo.target_force_id, salvo.target_force_id),
                                  set()).add(salvo.shooter_id)

        if not G4_EPISODES:
            return result

        # G4a: forza occupata fino alla fine dell'esito (salve in volo comprese) e passivita' dopo un disingaggio
        # (dall'istante del cambio di esito, o dalla fine dell'esito se manca) o una fine di attivita'.
        for force_id in force_ids:
            if result.t_end is not None:
                busy_until[force_id] = max(busy_until.get(force_id, float('-inf')), float(result.t_end))

        for force_outcome in result.forces:
            if force_outcome.outcome != ER.DISENGAGED:
                continue

            since = force_outcome.time if force_outcome.time is not None else result.t_end

            for asset in (getattr(forces.get(force_outcome.force_id), 'assets', None) or {}).values():
                asset_id = _domain_id(asset)

                if asset_id is not None and since is not None:
                    passive_from[asset_id] = min(float(since), passive_from.get(asset_id, float('inf')))

        for event in result.activity_ends:
            passive_from[event.asset_id] = min(float(event.time), passive_from.get(event.asset_id, float('inf')))

        return result

    def reschedule(changed, t_r, left, pairs_of) -> None:
        """G4b: contatti degli aerei ri-pianificati `changed` (`{asset_id: istante da cui i tratti cambiano}`)
        ricalcolati con i tratti aggiornati (`schedule_contacts` rieseguito, solo per le coppie con uno di loro,
        `only_assets`): le loro finestre non ancora risolte in `left` sono scartate e sostituite dalle nuove che
        finiscono dopo `t_r`, ritagliate a `t_r` (la storia prima e' fissata) e poi alle forze occupate
        (`_trim_busy`, dal chiamante). Il tratto di una finestra nuova gia' coperto da una finestra RISOLTA della
        stessa coppia di asset (`covered`) con la geometria di prima (cioe' prima dell'istante da cui i tratti
        cambiano) e' tolto anch'esso: l'episodio risolto ha gia' deciso che li' non succede altro, un secondo
        episodio sullo stesso intervallo con gli stessi tratti sarebbe una seconda estrazione."""
        fresh = CS.schedule_contacts(items_a, items_b, horizon, routes=routes, starts=starts, speeds=speeds, t0=t0,
                                     margin=margin, range_type=range_type, grounded=grounded, legs=presence_legs,
                                     only_assets=changed)
        kept = []

        for window in fresh:
            since = min(changed.get(window.asset_a_id, float('inf')), changed.get(window.asset_b_id, float('inf')))
            start = max(t_r, min(covered.get((window.asset_a_id, window.asset_b_id), float('-inf')), since))

            if window.t_end <= start + CS.TIME_EPS:
                continue

            trimmed = CS.trim_contact_window(window, start, all_legs.get(window.asset_a_id, ()),
                                             all_legs.get(window.asset_b_id, ()))

            if trimmed is not None:
                kept.append(trimmed)

        for pair in sorted(left):
            left[pair] = [window for window in left[pair]
                          if window.asset_a_id not in changed and window.asset_b_id not in changed]

        for pair, windows in sorted(_group_windows(kept, owner).items()):
            if pair not in left:
                for force_id in pair:
                    pairs_of.setdefault(force_id, []).append(pair)

            # Ordine dello scheduler, `(t_start, asset_a_id, asset_b_id)`, sulle finestre della coppia (sort stabile).
            left[pair] = sorted(left.get(pair, []) + windows,
                                key=lambda w: (w.t_start, str(w.asset_a_id), str(w.asset_b_id)))

    if G4_EPISODES:
        # G4a: un ENGAGEMENT per EPISODIO, in ordine di tempo (inizio della prima finestra, poi l'event_id). Dopo
        # ogni episodio le finestre non ancora risolte delle sue forze sono ritagliate alla fine del suo esito
        # (forza occupata) e, se qualcosa e' cambiato, gli episodi rimasti sono ricostruiti con la stessa regola.
        left = {pair: list(windows) for pair, windows in groups.items()}
        pairs_of: Dict[str, List[Tuple[str, str]]] = {}

        for pair in sorted(left):
            for force_id in pair:
                pairs_of.setdefault(force_id, []).append(pair)

        pending = _episodes(left, coordination)
        # G4b: fine della finestra RISOLTA piu' tarda per coppia di asset (v. `reschedule`).
        covered: Dict[Tuple[str, str], float] = {}

        while pending:
            force_ids, group = pending.pop(0)
            # F7b: i fuochi su posizione che colpiscono prima dell'inizio dell'episodio (a parita' d'istante dopo).
            fire_due(min(w.t_start for w in group))
            result = engage(min(w.t_start for w in group), force_ids, group, engagement_event_id(*force_ids))
            done = {id(window) for window in group}

            for window in group:
                key = (window.asset_a_id, window.asset_b_id)
                covered[key] = max(covered.get(key, float('-inf')), float(window.t_end))

            for pair in {(owner[w.asset_a_id][1], owner[w.asset_b_id][1]) for w in group}:
                left[pair] = [window for window in left.get(pair, ()) if id(window) not in done]

            # G4b: ri-pianificazione degli aerei alla fine dell'episodio e, se qualche tratto e' cambiato, nuovi
            # contatti per loro (v. "Ri-pianificazione dopo l'episodio (G4b)").
            changed = replan(result) if replanning and result is not None else {}

            if changed:
                # Le finestre nuove possono toccare forze occupate da episodi gia' risolti: ritaglio su tutte.
                reschedule(changed, float(result.t_end), left, pairs_of)
                _trim_busy(left, busy_until, all_legs)
                pending = _episodes({pair: windows for pair, windows in left.items() if windows}, coordination)
                continue

            touched = {pair: left[pair] for force_id in force_ids for pair in pairs_of.get(force_id, ())
                       if left.get(pair)}

            if _trim_busy(touched, busy_until, all_legs):
                left.update(touched)
                pending = _episodes({pair: windows for pair, windows in left.items() if windows}, coordination)

        fire_due()
    else:
        # Prima del G4a: un evento per COMPONENTE connessa di forze d'ingaggio, cioe' di missioni (F4b).
        queue: List = []
        sequence = 0

        for force_ids, group in _connected_components(groups, coordination):
            event_id = engagement_event_id(*force_ids)
            sequence += 1
            heapq.heappush(queue, (min(w.t_start for w in group), ENGAGEMENT_EVENT, event_id,
                                   sequence, (force_ids, group)))

        for impact, event_id, fire_order in area_events:
            sequence += 1
            heapq.heappush(queue, (impact, AREA_FIRE_EVENT, event_id, sequence, fire_order))

        area_events.clear()

        while queue:
            time, kind, key, _, payload = heapq.heappop(queue)

            if kind == AREA_FIRE_EVENT:
                fire_area(payload)
                continue

            force_ids, group = payload
            engage(time, force_ids, group, key)

    # Tratti di MOVIMENTO definitivi (G4b: dopo le ri-pianificazioni) per la contabilita' del carburante.
    movements: List[Tuple[str, object, List[CS.Leg]]] = []

    for force_id in sorted(blocks):
        for asset in (getattr(blocks[force_id], 'assets', None) or {}).values():
            asset_id = _domain_id(asset)
            moving = moving_legs.get(asset_id, []) if asset_id is not None else []

            if moving:
                movements.append((asset_id, asset, moving))

    # ── strato 3: carburante (coda eventi MOVEMENT + ingaggi risolti) ─────────
    # G4a: la contabilita' del carburante e' un passo FINALE, dopo tutti gli ingaggi (il risolutore non legge il
    # carburante e il carburante non legge danno ne' scorte). La coda e' quella di prima: gli ingaggi risolti
    # alla loro chiave `(istante, ENGAGEMENT, event_id)` e un MOVEMENT per asset alla fine dei suoi tratti;
    # ripercorsa nello stesso ordine produce gli stessi `FuelEvent` nello stesso ordine.
    queue = []
    sequence = 0

    for time, event_id, result in resolved:
        sequence += 1
        heapq.heappush(queue, (time, ENGAGEMENT_EVENT, event_id, sequence, result))

    for asset_id, asset, legs in movements:
        sequence += 1
        heapq.heappush(queue, (legs[-1].t_end, MOVEMENT_EVENT, asset_id, sequence, (asset, legs)))

    fuel_events: List[FM.FuelEvent] = []
    engaged: set = set()
    # G3: consumi d'ingaggio in attesa dell'evento MOVEMENT dell'asset (per metterli in ordine di tempo fra i tratti)
    # e asset gia' contabilizzati (`air_assets`, gli aerei di missione, i soli che consumano in ingaggio: sopra).
    with_movement = {asset_id for asset_id, _, _ in movements}
    pending_charges: Dict[str, List[float]] = {}
    accounted: set = set()

    def charge(asset, time):
        # G3: consumo istantaneo d'ingaggio, applicato subito (dopo l'esaurimento nessun evento).
        event = FM.build_engagement_fuel_event(asset, time, provenance=provenance)

        if event is not None:
            FM.apply_fuel_event(asset, event)
            fuel_events.append(event)

        return event

    while queue:
        time, kind, key, _, payload = heapq.heappop(queue)

        if kind == ENGAGEMENT_EVENT:
            result = payload

            if result is not None:
                engaged |= _engaged_assets(result)

                if G3_ENGAGEMENT_FUEL:
                    # G3: consumo d'ingaggio degli aerei IN VOLO all'istante della loro prima partecipazione
                    # (un aereo a terra colpito sul parcheggio non manovra), uno per ingaggio risolto (dal G4a uno
                    # per episodio). In attesa dell'evento MOVEMENT dell'asset, per l'ordine di tempo fra i tratti;
                    # subito se l'asset e' gia' contabilizzato o non ha tratti di movimento.
                    for asset_id, instant in sorted(_engagement_instants(result).items()):
                        asset = assets_by_id.get(asset_id)

                        if asset is None or asset_id not in air_assets or grounded.at(asset_id, instant):
                            continue

                        if asset_id in with_movement and asset_id not in accounted:
                            pending_charges.setdefault(asset_id, []).append(instant)
                        else:
                            charge(asset, instant)
        else:
            asset, legs = payload
            accounted.add(key)
            g3 = G3_ENGAGEMENT_FUEL and key in air_assets
            # F6-A: chi ha combattuto consuma il movimento al regime 'max'; G3 (aerei): sempre alla crociera, il
            # combattimento e' nei consumi d'ingaggio.
            regime = COMBAT_REGIME if key in engaged and not g3 else CRUISE_REGIME
            charges = sorted(pending_charges.pop(key, ()))

            if F6_FUEL_PER_LEG:
                # F6-A: un FuelEvent per tratto che consuma (movimento al regime della sessione, soste
                # nel tempo alla crociera), applicato in ordine; dopo l'esaurimento nessun evento. G3: i
                # consumi d'ingaggio in ordine di tempo, prima del tratto in cui cadono (v. docstring).
                steps = []

                for leg in _consuming_legs(key, legs, grounded):
                    while charges and charges[0] < leg.t_end - CS.TIME_EPS:
                        steps.append((charges.pop(0), None))

                    steps.append((None, leg))

                steps.extend((instant, None) for instant in charges)

                for instant, leg in steps:
                    if leg is None:
                        event = charge(asset, instant)
                    else:
                        event = _build_leg_fuel(asset, leg, regime, provenance)

                        if event is not None:
                            FM.apply_fuel_event(asset, event)
                            fuel_events.append(event)

                    if event is not None and event.exhausted:
                        break

                continue

            # Senza eventi per tratto (un solo evento a fine movimento): i consumi d'ingaggio prima di esso.
            emptied = False

            for instant in charges:
                event = charge(asset, instant)

                if event is not None and event.exhausted:
                    emptied = True
                    break

            if emptied:
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

    # F8, esito per la campagna (v. docstring del modulo): posizioni finali [m] alla fine NOMINALE della sessione
    # (`session_end`, non `latest`: le salve in volo non muovono nessuno), istante in cui ogni asset di missione ha
    # smesso di muoversi ed esito aggregato di ogni Operazione dell'ordine.
    final_positions = {}

    for asset_id in sorted(assets_by_id):
        legs = all_legs.get(asset_id)
        point = CS.position_on_legs(legs, session_end) if legs else None

        if point is not None:
            final_positions[asset_id] = tuple(float(c) for c in point)

    movement_ends = {asset_id: float(legs[-1].t_end) for asset_id, legs in sorted(moving_legs.items()) if legs}
    operation_outcomes = {op.operation_id: operation_outcome(op, mission_outcomes) for op in order.operations}

    # Ogni esito e' applicato prima di risolvere il successivo: i `health_before/after` sono concatenati anche
    # quando lo stesso asset e' in piu' episodi (G4a).
    return assemble_session_outcome(order.session_id, results, fuel_events,
                                    t_start=t0, t_end=latest, mission_outcomes=mission_outcomes,
                                    postures=postures, chained=True,
                                    operation_outcomes=operation_outcomes,
                                    final_positions=final_positions,
                                    movement_ends=movement_ends)
