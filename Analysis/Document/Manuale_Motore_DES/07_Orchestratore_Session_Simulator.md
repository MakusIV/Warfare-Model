# Capitolo 6 — L'orchestratore: `Session_Simulator.run_session`

Modulo: `Logic/Session_Simulator.py` (**2851 righe a `a784a9e7`**, 937 a `84a47670`, 774 a `533cd1f5`; il grosso della
crescita è il docstring del modulo, che è il documento di progetto di F5, F6 e G1-G5, e la nuova logica di sessione).
Mette in fila, per la prima volta, i pezzi prodotti dalle fasi precedenti (`Logic/Session_Simulator.py:1-19`); dalla
fase F3 della Missione (2026-10-05) la fila comincia dalle **missioni** dell'ordine, dalla F4 (2026-10-05/11) la
missione è anche la **forza d'ingaggio** e dai passi G4a-G4b (2026-10-17) l'ingaggio è un **episodio nel tempo**, dopo
il quale gli aerei sono **ri-pianificati**:

```
SessionOrder.missions ──> Mission_Adapter.mission_movements   (rotta, partenza, velocità, attese, presenza per asset)
                      ──> _engagement_forces                   (una forza per missione, §6.12)
                      ──> Mission_Adapter.coordination_domains (dominio di coordinamento, §6.13)
                      ──> Mission_Adapter.grounded_schedule    (aerei a terra nel tempo, §6.14-6.15)
                      ──> tratti: bingo alla partenza (G2) e esaurimento del carburante (F6-A), §6.17/6.19
SessionOrder ──> Contact_Scheduler.schedule_contacts          (strato 1: QUANDO)
             ──> raggruppamento in EPISODI d'ingaggio          (G4a; spento: componenti connesse di forze)
             ──> Engagement_Resolver.resolve_engagement        (strato 2: COME FINISCE), uno per episodio
             ──> apply_engagement_result                       (strato 3: danno, munizioni), subito
             ──> ri-pianificazione degli aerei + nuovi contatti (G4b), poi l'episodio successivo
             ──> Fuel_Model.build/apply_fuel_event             (strato 3: carburante, PASSO FINALE dal G4a)
             ──> esito di missione per ogni Mission            (regola unica dalla F6-B1, §6.11/6.18)
             ──> Session_Types.assemble_session_outcome        (porta di uscita)
```

Questo modulo è **solo** quella fila: non reimplementa geometria, Pd, latenze, salve, danno o consumi. Ogni numero che
produce viene da uno dei moduli chiamati; la geometria di formazione, la derivazione di partenza, velocità, attese e
presenza e i validatori di pianificazione sono in `Logic/Mission_Adapter` (§6.10, §6.15-6.16, §6.19), la vista di
missione, il dominio di coordinamento e la postura continua anch'essi (§6.12-6.14); i calcoli sul carburante e sul
bingo sono in `Logic/Fuel_Model` (capitolo 5 §5.2), non qui. Quel che resta qui è **quando** e **con quali dati**
usarli.

## 6.1 La funzione pubblica

```python
run_session(order, forces_a, forces_b, fire_control, *, horizon=None, margin=0.0,
            range_type=DEFAULT_DETECTION_RANGE_TYPE, thresholds=None,
            reaction_profile_for=None, detection_factor=None, provenance=DM.DERIVED,
            morale_for=None, enemy_estimate_for=None, fire_doctrine=None)
            -> SessionOutcome
```

(`Logic/Session_Simulator.py:2017-2851`, firma a `:2017-2028`; **la firma non è cambiata dalla F3** e non cambia
con F5, F6 e G1-G5: tutte le novità sono interruttori del modulo, §6.21, e nuovi dati nell'esito). **Muta gli asset**:
danno e munizioni sono applicati man mano che gli episodi d'ingaggio sono risolti, il carburante in un passo finale. Il
`SessionOutcome` restituito è il resoconto di ciò che è stato applicato. Si combatte solo fra `forces_a` e `forces_b`,
mai dentro lo stesso lato.

**Cambiamenti da `84a47670` a `a784a9e7` (fasi F5, F6 e G1-G5):** nessuna modifica alla firma. In ordine:

- **Presenza e attese** (F5): i tratti degli asset di missione comprendono la presenza ferma prima della partenza e
  dopo la fine e le attese WAIT; gli aerei di missione sono a terra a intervalli (`grounded_schedule`); l'esito porta la
  postura di ogni asset (§6.15-6.16).
- **Carburante** (F6-A): consumo per tratto e nel tempo, vincolo sul movimento e sui contatti, planata e perdita
  dell'aereo a secco (§6.17).
- **Fine di attività e stato di missione** (F6-B1): i criteri `EndCriteria` sono letti; regola unica
  `DESTROYED > COMPLETED > ABORTED(motivo) > FAILED`; postura `destroyed` (§6.18).
- **Bingo** (F6-B2, F6-B2bis e G1-G2): soglia con riserva di disimpegno e albero di decisione, valutati alla partenza
  (§6.19); validatori di pianificazione **non** chiamati da `run_session`.
- **Consumo in ingaggio, episodi, ri-pianificazione, uscita di scena** (G3, G4a, G4b): l'ingaggio diventa un
  episodio, dopo ogni episodio gli aerei interessati sono ri-pianificati e i loro contatti ricalcolati (§6.20).
- **Interruttori**: undici costanti del modulo, tutte attive (§6.21).

**Cambiamenti da `533cd1f5` a `84a47670` (fase F4):**

- **Validazione delle missioni** (`_check_missions`, `:1797-1813`): oltre a "la missione si riferisce a un blocco
  passato fra le forze" (`ValueError`, `:1803-1805`) e "ogni suo asset appartiene a quel blocco"
  (`Mission_Types.check_mission_assets`, `:1807`), dalla F4a vale la **regola A** — una missione si muove insieme,
  alla velocità del mezzo più lento: `Mission_Adapter.check_mission_speed(mission, assets, order.t_start)`
  (`:1809`, §6.10) solleva `ValueError` se un tratto pianificato supera la velocità massima del mezzo più
  lento; e dalla F4b un `mission_id` non può coincidere con l'id di un blocco passato (`:1811-1813`: sarebbero due
  forze con lo stesso id).
- **Le forze d'ingaggio sono missioni**, non blocchi (F4b): `_engagement_forces` (`:1816-1859`, §6.12). Lo
  scheduler riceve ancora i **blocchi** (`items_a`/`items_b`, `:2215`): le finestre sono per coppia di asset e la
  potatura per blocco non dipende da come gli asset sono raggruppati in forze.
- **Dominio di coordinamento** (F4b+): `coordination_domains` (`:2090`) è passato a `_connected_components` (`:2634`)
  e a `_episodes` (`:2596`) e a ogni `resolve_engagement` come `coordination_of` (`:2507`), §6.13.
- **Aerei a terra** (F4c, F5): il programma `grounded` (`:2103`) è passato a `schedule_contacts` (`grounded=`, `:2217`)
  e a ogni `resolve_engagement` (`grounded=`, `:2508`), §6.14-6.15.
- **`SessionOrder.committed`** resta chiavato per blocco; `_engagement_committed` (`:1862-1882`) lo traduce per forza
  d'ingaggio (§6.12).

**Cambiamenti da `6754bf1c` a `533cd1f5` (fase F3):**

- **Rimossi `routes`, `starts`, `speeds`** (decisione Q2 dell'utente: una sola strada): rotta, partenza e velocità di
  ogni asset vengono **solo** dalle missioni dell'ordine (`order.missions`); `Mission_Adapter.session_movements(
  order.missions, t0)` ne ricava le tre mappe che il resto della fila consuma (`:2100`). Gli asset senza missione
  restano fermi, come gli asset senza rotta di prima (dalla F4c con una postura, §6.14).
- **Aggiunti `morale_for`, `enemy_estimate_for`, `fire_doctrine`** (2026-09-29): inoltrati a
  `resolve_engagement`; a questi si aggiunge il flusso `breakpoint_rng` della tempra, costruito
  dall'orchestratore (§6.4). `rwr_catalogue` di `resolve_engagement` **non** è inoltrato da `run_session`
  (disponibile solo chiamando il risolutore direttamente; capitolo 9 §9.6).
- Il valore restituito porta un `MissionOutcome` per ogni missione dell'ordine (§6.11).

## 6.2 La coda eventi di sessione

Due tipi di evento, `ENGAGEMENT_EVENT = 0` e `MOVEMENT_EVENT = 1` (`:700-701`), con chiave
`(t, tipo, id, sequenza)` (docstring `:21-45`):

- **ENGAGEMENT** — dal G4a uno per **episodio d'ingaggio** (§6.20); istante = inizio della prima finestra
  dell'episodio. Risolve l'episodio con **una** chiamata a `resolve_engagement` sulle sole sue finestre e forze, e ne
  applica subito l'esito (`engage`, `:2449-2543`). Con `G4_EPISODES` spento, uno per componente connessa di forze
  (§6.3), come prima del G4a.
- **MOVEMENT** — uno per asset con rotta schedulabile nella sessione; istante = fine del suo movimento dentro la
  sessione (dalla F6-A troncato all'esaurimento del carburante). Produce e applica i `FuelEvent` del tragitto, **uno
  per tratto** (§6.17).

**Dal G4a la coda è percorsa in due passi**, non in uno (`:2585-2642`, `:2644-2778`):

1. **tutti gli ENGAGEMENT**, in ordine di tempo (poi `event_id`), ciascuno seguito dalla ri-pianificazione degli aerei
   interessati (G4b, §6.20);
2. **poi la contabilità del carburante**: un `heapq` con gli ingaggi già risolti, alla loro chiave
   `(istante, ENGAGEMENT, event_id)`, e un MOVEMENT per asset alla fine dei suoi tratti **definitivi**
   (`:2660-2669`) — cioè la stessa coda di prima ripercorsa nello stesso ordine, che produce gli stessi `FuelEvent`.

È lecito spostare il carburante in coda perché **il risolutore non legge il carburante** (nessun accesso a `fuel` in
`Engagement_Resolver`: capitolo 4 §4.31) e il carburante **non legge danno né scorte** (`Fuel_Model` legge solo il
contatore, il loadout e i registri). E serve, perché il G4b conosce i tratti definitivi di ogni aereo solo dopo l'ultimo
episodio. A parità d'istante `ENGAGEMENT_EVENT(0) < MOVEMENT_EVENT(1)`, poi l'id (stringa canonica, mai l'ordine di un
dizionario Python).

## 6.3 Forze impegnate su più fronti: componenti connesse (e, dal G4a, episodi)

**Prima del 2026-09-23**: un ingaggio per coppia (lato A, lato B), applicato subito. Restava un
difetto: se X era in contatto con A e con B in finestre **sovrapposte**, l'ingaggio (X,A)
estratto per primo veniva svolto fino in fondo e applicato, e (X,B) leggeva uno stato di X già
consumato anche per le salve che, in tempo di sessione, precedevano la fine di (X,A). L'ordine
della coda decideva chi "arrivava prima" alla salute e alle scorte di X — un artefatto
d'implementazione, non la fisica del combattimento (docstring `:230-242`).

**Dal 2026-09-23 al G4a**: un ingaggio per **componente connessa** di forze d'ingaggio. Si costruisce il grafo non
orientato con un nodo per forza e un arco per ogni coppia (lato A, lato B) con almeno una finestra (`_group_windows`,
`:1009-1031`: raggruppa le finestre per coppia di *forze* d'ingaggio, dalla mappa `{asset_id: (lato, id di
forza)}`), e se ne cercano le componenti connesse (`_connected_components`, `:1034-1099`, visita in ampiezza
deterministica per id — mai l'ordine di un dizionario). **Dalla F4b+ il grafo ha anche archi fra forze dello
stesso dominio di coordinamento** (`domain_of`, `:1057-1066`): le forze di uno stesso dominio sono messe nella
stessa run **anche se non hanno nemici in comune**, perché la condivisione di fuoco, percezione e difesa di salva
(capitolo 4 §4.28-4.29) vale solo dentro una run. Senza questi archi due missioni di un blocco su fronti
disgiunti sarebbero risolte in run separate, mentre il blocco prima della F4b era una forza sola. I nodi restano
le sole forze che compaiono in almeno una coppia con finestre (`:1051-1055`): una forza di un dominio senza
nessuna finestra non entra in nessuna run. La componente unita ha l'`event_id` delle forze riunite (§6.4).

Ogni ingaggio è risolto con **una** chiamata a `resolve_engagement`: `force_a`/`force_b` = le prime due forze
per id, `extra_forces` = le altre, per id (`:2492-2494`). Dentro la run lo stato ombra di X evolve in un'unica
timeline consumata da tutti i fronti; un disingaggio è per-forza (capitolo 4, §4.8), non ferma un eventuale altro
fronte della componente — nemmeno un'altra missione dello stesso blocco.

Le componenti sono **disgiunte**: nessuna forza compare in due componenti della stessa sessione, quindi senza episodi
il limite di `assemble_session_outcome` (capitolo 2, §2.4) non si presenta mai.

**Era deliberatamente conservativa rispetto al tempo**: la componente non distingueva se le sue finestre si
sovrappongono davvero o sono in sequenza (X contro A al mattino, contro B la sera): anche in quel caso {X, A, B} era
risolta con una sola run, e questo significava **un solo consumo d'ingaggio, un disingaggio del mattino che vale anche la
sera e nessuna decisione possibile "dopo l'ingaggio"** (docstring `:258-264`). **Il G4a la spezza** nei suoi episodi
(§6.20); la componente connessa è oggi il comportamento a `G4_EPISODES` spento, mantenuto per la controprova degli
scenari (S5 `episodes_off`, S27 `episodes_off`).

**Che cosa è cambiato con la F4.** A `533cd1f5` l'unità d'ingaggio era la forza = il blocco: ingaggi, RNG e
disingaggio erano per blocco, e due missioni dello stesso blocco condividevano lo stesso destino. Dalla F4b
(`a4d8acf0`) l'unità è la **missione**: ogni missione ha il proprio ingaggio, la propria tempra e il proprio
disingaggio (capitolo 4 §4.27); dalla F4b+ (`098671d7`) fuoco e percezione sono condivisi nel dominio, e le
componenti ne tengono conto (sopra).

## 6.4 RNG: uno stream per ingaggio, uno stream per la tempra

`order.rng(mission_id=None, event_id=engagement_event_id(*forze), counter=ordinale)` (`:2493`):

- `mission_id=None`: è il livello "di sessione" di `Session_Rng`. **Dalla F4b il `mission_id` entra nell'RNG
  attraverso l'`event_id`**, non attraverso lo slot `mission_id`: un ingaggio è fra DUE O PIÙ forze, tipicamente
  missioni di entrambi i lati, e nessuna ne possiede lo stream. Lo slot resta `None` (livello "di sessione") per le
  estrazioni che appartengono a una sola missione (nessuna, oggi; docstring `:400-418`). **Nota**: il piano della
  Missione prevedeva il `mission_id` reale già in F3; il codice l'ha rimandato a F4b (deviazione 1 del piano, con
  l'`event_id` al posto dello slot, deviazione 4: capitolo 9 §9.6).
- `event_id`: `engagement_event_id(*force_ids)` (`:884-905`) è la codifica JSON di
  `['engagement', id_1, id_2, ...]` con gli id dell'ingaggio **ordinati** — funzione pura
  dell'**insieme** delle forze, mai dell'ordine di iterazione o di passaggio a `run_session`. Dalla F4b gli id sono
  quelli delle **forze d'ingaggio**: i `mission_id` (o l'id del blocco per un blocco senza missioni e per la vista
  residua). Rinominare una missione cambia solo lo stream degli ingaggi che la coinvolgono
  (`test_renaming_a_mission_changes_its_stream_only`), e l'unione di una componente per dominio cambia l'`event_id`
  (è un ingaggio diverso, con forze diverse).
- **`counter` (G4a)**: l'**ordinale degli episodi con lo stesso insieme di forze** nella sessione (`ordinals`,
  `:2251`, `:2453-2454`): 0 per il primo, 1 per il secondo che coinvolge esattamente le stesse forze, e così via.
  Vale sia per lo stream dell'ingaggio sia per quello della tempra. Una componente che è un solo episodio ha quindi
  esattamente lo stream, le finestre, l'ordine e l'esito di prima; con `G4_EPISODES` spento è sempre 0 (ogni componente
  è risolta una sola volta per sessione). Il vecchio "contatore libero per un futuro re-ingaggio" è dunque stato
  consumato dal G4a.

**Secondo stream: la tempra delle forze** (2026-09-29). `temper_event_id(*force_ids)` (`:908-918`) ha
la stessa forma e gli stessi vincoli ma il tag `'temper'` (`TEMPER_EVENT_TAG`, `:707`) invece di
`'engagement'`; `run_session` lo passa a `resolve_engagement` come `breakpoint_rng`
(`order.rng(mission_id=None, event_id=temper_event_id(*force_ids), counter=counter)`, `:2501-2503`). Così estrarre
la tempra non sposta le estrazioni di rilevamento e danno dell'ingaggio (capitolo 4 §4.11, §4.21), e **la tempra è
nuova per ogni episodio** (stesso `counter`).

**Precondizione di riproducibilità**: gli id di forza devono essere **stabili** fra le
esecuzioni. `Block.__init__` genera l'id con `Utility.setId`, che aggiunge un suffisso casuale —
due `Military` costruite da zero con lo stesso nome avrebbero id diversi, quindi seed diversi e
un diverso ordine della coda. Corretto 2026-09-23: `Block.__init__`/`Military.__init__`
accettano ora un parametro `id` esplicito (docstring `:419-428`); chi costruisce forze da zero per un
replay/test deve passarlo. In campagna l'id è comunque quello dell'istanza già in memoria
(persistito), quindi il caso comune non è mai stato a rischio.

## 6.5 Carburante: la panoramica

Il carburante è oggi una **funzione a sé** dell'orchestratore, descritta in dettaglio nelle sezioni seguenti. In sintesi
(dal G4a, nell'ordine in cui avviene):

1. **prima dello scheduler** (F6-A, G2): per ogni asset di missione, dai tratti di movimento si calcolano a monte
   l'eventuale **bingo** alla partenza (§6.19) e l'**esaurimento** del carburante (§6.17); i tratti sono troncati o
   sostituiti dal rientro, e passati a scheduler e risolutore;
2. **durante gli episodi** (G3, G4b): ogni aereo di missione in volo che partecipa a un ingaggio ha un consumo
   istantaneo; alla fine dell'episodio è ri-pianificato dal **residuo analitico** (§6.20);
3. **dopo l'ultimo episodio** (passo finale, §6.2): la contabilità produce i `FuelEvent` — uno per tratto che
   consuma, più uno istantaneo per ogni consumo d'ingaggio — e li applica agli asset.

**Regime** (F6-A, `COMBAT_REGIME = 'max'`, `CRUISE_REGIME = 'nominal'`, `:710-711`). Per **terra e mare** vale ancora la
regola della F6-A: `'max'` se l'asset ha **combattuto** nella sessione (ha lanciato una salva, è stato bersaglio di una
salva o ha intercettato: `_engaged_assets`, `:1212-1226`), altrimenti `'nominal'`; per veicoli e navi il registro ha
un'unica autonomia e i due regimi coincidono. Per gli **aerei di missione**, dal G3, il movimento è **sempre alla
crociera** e il combattimento è nei consumi d'ingaggio (`regime = COMBAT_REGIME if key in engaged and not g3 else
CRUISE_REGIME`, `:2719`). Se il regime `'max'` non è ricavabile si ricade su `'nominal'` (`_build_fuel`,
`_build_leg_fuel`, `:1252-1275`).

**Limiti dichiarati** (in parte superati): un asset distrutto a metà rotta consuma comunque il tragitto (troncato)
intero (il carburante di un relitto non ha conseguenze di campagna); un asset senza rotta (fermo) non produce
`FuelEvent`; il carburante di partenza e il rifornimento non sono toccati (rifornimento: F8). Il limite storico "nessun
movimento fisico: un asset a secco continua" è superato dalla F6-A (§6.17); il limite "un aereo che combatte consuma di
più nella contabilità senza che il movimento sia ricalcolato" è superato dal G4b per gli aerei con consumo d'ingaggio
(§6.20).

## 6.6 Sessione aperta e attività oltre la fine

`SessionOrder.t_end is None` (sessione aperta): la durata **non si deduce**, il chiamante deve
passare `horizon` esplicito; con `t_end` valorizzato, `horizon` è ricavato (se passato comunque
deve coincidere) — `_session_horizon`, `:923-942`. Nessuna durata di default inventata
(docstring `:641-645`).

Una salva lanciata poco prima della fine arriva comunque (payload congelato): impatti e
risoluzioni possono cadere dopo `t_start + horizon`. L'esito non viene troncato (sarebbe
cancellare danni già decisi): il `t_end` del `SessionOutcome` è esteso fino all'ultima
attività, con un log (`:2780-2797`). I contatti invece sono cercati **solo** dentro la sessione
(docstring `:647-652`); allo stesso modo la ri-pianificazione dopo un episodio non agisce oltre la fine della sessione
(`:2323-2325`).

## 6.7 Cosa non fa (docstring `:654-659`)

Non costruisce `Theater_Session_Manager`, non legge/scrive `Campaign_State`. Non rifornisce (munizioni o carburante). Non
ri-instrada le forze **terrestri e navali** che si disingaggiano (restano segnalate nell'esito e, dal G4a, passive negli
episodi successivi); **gli aerei** di una missione disingaggiata, invece, rientrano alla base dal G4b (§6.20). La
selezione dell'arma dai registri non è dell'orchestratore: la `fire_control` è **una sola callable iniettata**,
passata tale e quale a ogni ingaggio (può essere `Fire_Control.make_registry_fire_control`, capitolo 4 §4.16;
le frasi del docstring del modulo sulla selezione dell'arma sono state corrette e rimandano alla fabbrica, v. capitolo 9
§9.6). **Non chiama i validatori di pianificazione** del carburante (`Mission_Adapter.check_mission_fuel`,
`check_mission_bingo`), che sono del pianificatore (§6.19, capitolo 9 §9.1). Non modella il filtro delle armi per tipo di
missione (fase F7). Non legge `abort_on_threat` né `last_waypoint` di `EndCriteria`. Nessun componente LLM.

## 6.8 Diagramma D8 — flusso dati di `run_session`

Aggiornato a `a784a9e7`: dopo la validazione delle missioni (con la regola A) l'orchestratore costruisce le
**forze d'ingaggio**, il **dominio di coordinamento** e il **programma degli aerei a terra**; prepara i **tratti**
degli asset di missione (presenza, attese, bingo alla partenza, troncamento per esaurimento); lo scheduler riceve i
blocchi, `grounded` e `legs`; gli ingaggi sono **episodi** seguiti dalla ri-pianificazione; il carburante è un passo
finale.

```mermaid
flowchart TD
    ORD["SessionOrder<br/>(session_id, t_start/t_end, force_ids, committed, salvo_window,<br/>missions, operations)"]
    FORCES["forces_a, forces_b<br/>(Military/Block/BlockItem)"]

    ORD --> COLLECT["_collect_forces<br/>normalizza lati, mappa asset -> blocco"]
    FORCES --> COLLECT
    COLLECT --> CHECK["_check_missions<br/>blocco passato, asset del blocco,<br/>regola A, mission_id != id di blocco"]
    ORD --> CHECK
    CHECK --> MA["Mission_Adapter.mission_movements<br/>rotta, partenza, velocita', attese, presenza"]
    CHECK --> EF["_engagement_forces<br/>MissionForce per missione + vista residua"]
    EF --> DOM["coordination_domains"]
    EF --> GRD["grounded_schedule<br/>(aerei a terra nel tempo)"]

    MA --> LEGS["tratti di ogni asset (movement_legs):<br/>bingo alla partenza (_decision_end),<br/>esaurimento (_fuel_end), _fuel_truncated"]
    GRD --> LEGS
    LEGS --> SCHED["Contact_Scheduler.schedule_contacts<br/>(potatura Block + CPA/TCPA, grounded, legs)"]
    COLLECT --> SCHED
    SCHED --> WINDOWS["List[ContactWindow]"]
    WINDOWS --> GROUP["_group_windows + _episodes<br/>(forze, domini, EPISODE_GAP)"]
    EF --> GROUP
    DOM --> GROUP

    GROUP --> LOOP["per ogni episodio, in ordine di tempo"]
    LOOP --> ER["Engagement_Resolver.resolve_engagement<br/>(rng + breakpoint_rng, coordination_of, grounded, activity_criteria)"]
    ER --> APPLY["apply_engagement_result<br/>(danno + munizioni + intercettazioni)"]
    APPLY --> STATE["stato reale degli asset (mutato)"]
    APPLY --> REPLAN["replan: aerei che hanno consumato o disingaggiati<br/>(bingo, esaurimento, rientro forzato)"]
    REPLAN -->|tratti cambiati| RESCHED["reschedule: schedule_contacts(only_assets),<br/>episodi rimasti ricostruiti"]
    RESCHED --> LOOP

    LOOP -->|fine episodi| FUEL["passo finale: coda ingaggi risolti + MOVEMENT<br/>build_leg_fuel_event / build_engagement_fuel_event + apply"]
    FUEL --> STATE
    ER --> RESULTS["List[EngagementResult]"]
    FUEL --> FEVENTS["List[FuelEvent]"]

    RESULTS --> MOUT["_destruction_times + _activity_ends<br/>+ _mission_outcome (regola unica, §6.11)"]
    LEGS --> MOUT
    STATE --> MOUT
    MOUT --> MOS["mission_outcomes + postures"]

    RESULTS --> ASSEMBLE["Session_Types.assemble_session_outcome<br/>(chained=True)"]
    FEVENTS --> ASSEMBLE
    MOS --> ASSEMBLE
    ASSEMBLE --> OUT["SessionOutcome"]
```

## 6.9 Diagramma D9 — coda eventi di sessione (schema)

Esempio minimo: due episodi d'ingaggio dello stesso aereo, ciascuno con la ri-pianificazione, e la contabilità finale
del carburante. Aggiornato a `a784a9e7`: due passi, un `resolve_engagement` per episodio; il dettaglio del ciclo
episodio → ri-pianificazione → ri-scheduling è nel D40 (§6.20).

```mermaid
sequenceDiagram
    participant Q as coda di sessione
    participant CS as Contact_Scheduler
    participant ER as Engagement_Resolver
    participant FM as Fuel_Model
    participant OUT as assemble_session_outcome

    CS->>Q: ContactWindow, raggruppate in episodi (forze, domini, EPISODE_GAP)
    Note over Q: PASSO 1: tutti gli ENGAGEMENT, in ordine di tempo
    Q->>ER: pop ENGAGEMENT, episodio 1 (rng con counter 0)
    ER-->>Q: EngagementResult, applicato subito (apply_engagement_result)
    Q->>Q: replan degli aerei coinvolti, eventuale reschedule
    Q->>ER: pop ENGAGEMENT, episodio 2 (stesse forze: counter 1, tempra nuova)
    ER-->>Q: EngagementResult, applicato subito
    Q->>Q: replan, eventuale reschedule
    Note over Q,FM: PASSO 2: contabilita' del carburante (tratti definitivi)
    Q->>FM: ingaggi risolti (consumo d'ingaggio, G3) + MOVEMENT per asset
    FM->>FM: build_leg_fuel_event / build_engagement_fuel_event + apply_fuel_event
    FM-->>OUT: FuelEvent (uno per tratto, uno istantaneo per ingaggio)
    ER-->>OUT: EngagementResult (uno per episodio)
    OUT->>OUT: assemble_session_outcome(..., mission_outcomes, postures, chained=True)
```

## 6.10 La Missione nell'orchestratore: `Logic/Mission_Adapter.py` (fase F3, commit `533cd1f5`; esteso da F4 a G4b)

Modulo nato in F3 (483 righe), arrivato a 926 righe a `84a47670` e a **1776 righe a `a784a9e7`**: la **logica** che ricava,
per ogni asset di una `Mission`, la forma che `run_session` consuma — le tre mappe `routes`/`starts`/`speeds` di
`Contact_Scheduler.schedule_contacts` e, dalla F5, le **attese**, la **presenza** prima e dopo la rotta e il **programma a
terra** (§6.15-6.16). Dalla F4 contiene anche la **regola A** (velocità del mezzo più lento, sotto), la **vista
d'ingaggio** `MissionForce` (§6.12), il **dominio di coordinamento** (§6.13) e la **postura continua** con gli aerei a
terra (§6.14); dalla F6 i **validatori di pianificazione** del carburante e le funzioni che alimentano il bingo (§6.19).
`Command/Mission_Types` (capitolo 2 §2.6) è solo struttura. Funzioni pure: nessun RNG, nessuna mutazione
(`Logic/Mission_Adapter.py:1-284`, docstring del modulo).

### Rotta per asset: rotta di riferimento + offset di formazione (D3.b)

La missione ha **una** rotta di riferimento (`Mission.route`, o in mancanza la spezzata dei
`MissionWaypoint`, `reference_route`, `:443-458`; `_route_from_waypoints`, `:420-440`, richiede la velocità
dichiarata su ogni punto d'arrivo, altrimenti `ValueError`); ogni `MissionAsset` dichiara un offset
(`forward_m`, `right_m`, `up_m`) nella terna della direzione di marcia, con la convenzione del progetto
(nord = +y, est = +x, azimut orario):

- **avanti**: versore **orizzontale** della direzione di marcia (la quota non inclina la formazione);
- **destra**: avanti ruotato di 90° in senso orario visto dall'alto, `(hy, −hx)` (`:564`);
- **alto**: `+z`.

`asset_route(mission, mission_asset)` (`:598-626`) restituisce `(rotta, velocità uniforme)`. **Offset nullo e
nessuna velocità per tratto = la STESSA rotta** (lo stesso oggetto `Route`): i tratti sono identici a quelli
della rotta di riferimento, senza alcuna aritmetica in mezzo.

**Regola ai cambi di direzione, decisa in F3: la formazione ruota con la rotta, sulla bisettrice**
(`offset_points`, `:533-571`; `_point_frame`, `:513-530`). L'offset si applica **punto per punto**, non tratto
per tratto (applicarlo per tratto staccherebbe i tratti consecutivi):

- primo punto: terna del primo tratto; ultimo punto: terna dell'ultimo tratto;
- punto intermedio: terna della **bisettrice** `b = normalizzato(h_entrata + h_uscita)`, la direzione media
  fra il tratto in arrivo e quello in partenza;
- la componente **laterale** è scalata di `1/cos(θ/2)` (θ = angolo di virata; giunzione "a spigolo", la
  stessa delle spezzate parallele): i tratti dell'asset restano **paralleli** a quelli di riferimento, a
  distanza `right_m`, prima e dopo la virata. Il fattore è limitato a `MITER_LIMIT = 2.0` (`:321`, **stima di
  progetto**, esatto fino a virate di 120°, tagliato oltre); la componente **avanti** è presa lungo la
  bisettrice, senza scala;
- **inversione esatta** (`h_uscita = −h_entrata`, bisettrice indefinita): si usa la terna del tratto in
  **entrata**; il tratto successivo porta l'asset nella terna d'uscita al punto dopo (in una virata di 180° il
  gregario di destra finisce dall'altra parte del riferimento, come in una formazione vera);
- i tratti senza componente orizzontale (salita o discesa sulla verticale, punti ripetuti) ereditano la
  direzione dal tratto orizzontale più vicino (prima il precedente, `_leg_headings`, `:493-510`); una rotta
  senza alcun tratto orizzontale ammette solo `up_m` (altrimenti `ValueError`);
- le coordinate sono arrotondate al micrometro (`OFFSET_DECIMALS = 6`, `:324`): il rumore della rotazione
  (ordine 1e-12 m) non ha significato fisico e non deve comparire come differenza di posizione (sympy
  `Point3D` conserva i float come razionali).

**Conseguenza da sapere**: una formazione che trasla *rigidamente* (stesso spostamento per ogni punto)
coincide con "rotta di riferimento + offset" **solo** se la rotta non cambia direzione; con virate la traslata
è un'altra geometria. Per questo `Scenario_Fixtures.missions_for` (capitolo 8 §8.1) accetta un offset solo se
`asset_route` riproduce **esattamente** la rotta traslata dell'asset, altrimenti l'asset ha una missione
propria.

### Velocità

`MissionWaypoint.speed_kmh` è la velocità del tratto **in arrivo** al punto (`None` = quella dell'arco della
rotta, in m/s); quella del primo punto non ha tratto in arrivo ed è ignorata (`_leg_speeds`, `:461-478`).
Nessuna velocità dichiarata: valgono quelle degli archi, nessuna voce in `speeds`. Tutti i tratti dichiarano la
**stessa** velocità: una voce in `speeds` [m/s] (sostituisce quella degli archi, semantica di `route_legs`),
rotta invariata. Dichiarazioni diverse o parziali: la rotta per asset è ricostruita (`_rebuild_route`,
`:574-593`) con la velocità dichiarata sui tratti che la dichiarano e quella dell'arco sugli altri.
Conversione `kmh_to_ms` (`:380-382`): `km/h / 3.6`.

**Regola A: la missione si muove insieme, alla velocità del mezzo più lento** (F4a, `951b0ee2`, decisione
dell'utente: una missione è un gruppo, come un gruppo DCS; chi vuole velocità diverse fa missioni separate,
eventualmente coordinate da un'Operazione). `check_mission_speed(mission, assets, t0)` (`:1108-1156`, chiamata da
`Session_Simulator._check_missions`, `:1807-1809`) verifica che la velocità pianificata di ogni tratto
(`planned_speeds`, `:1097-1105`: quella di missione, o in mancanza quella dell'arco) non superi la velocità
**massima** (`asset.speed['max']`, m/s, `_max_speed`, `:1086-1094`) del mezzo più lento della missione; altrimenti
`ValueError`. Ritorna il limite applicato, o `None` se nessun asset ha il dato o la missione non si muove.
Dettagli (docstring `:76-91`):

- un asset senza velocità massima nota (modello senza dato, asset non `Mobile`) è **escluso dal confronto con un
  warning**, non blocca la missione (`:1136-1139`);
- il limite è il regime `'max'` **generico**, non quello per terreno (`speed['off_road']['max']`): gli scenari
  pianificano oggi i mezzi terrestri al regime nominale su archi 'offroad', e il vincolo per tipo d'arco va
  deciso con il modulo mappe (limite noto);
- tolleranza `SPEED_TOLERANCE = 1e-6` m/s (`:337`): rumore di conversione delle unità, non un margine fisico.

Negli scenari il controllo non scatta mai: le velocità pianificate sono le nominali del registro, sotto le
massime. Esempio verificato sul registro (`Asset/Vehicle_Data.py`): M1A2 con velocità sostenuta 55 km/h e massima
67 km/h (18,611 m/s), M2-Bradley 56 e 66 km/h (18,333 m/s); la missione Blue-Armor procede a 55 km/h
(15,278 m/s), la nominale del più lento (capitolo 8 §8.1).

### Partenza (`mission_start`, `:642-697`)

Gli istanti di una missione sono in secondi dall'inizio della sessione; la partenza assoluta è `t0 + ...` con
`t0 = SessionOrder.t_start`. In ordine di precedenza: (1) `start_time` (dalla F5-C **ritardata** da un'ETA bloccata più
tarda sul punto di partenza, `:656-659`); (2) il primo waypoint con `eta_locked`: partenza = ETA − tempo di percorrenza
fino a quel punto sulla rotta di riferimento (con le velocità di missione, `_travel_time_to`, `:629-639`, e le attese di
durata nota prima del punto, `:689-691`); (3) `tot`, ancorato al primo waypoint `ATTACK` (o, in mancanza, `OBJECTIVE`,
`_TOT_ANCHOR_ROLES`, `:340`): stessa derivazione; senza punto d'ancoraggio `ValueError`. **Il TOT è della missione**, non
dell'Operazione (§6.16). Tutti gli asset di una missione partono **insieme** (la formazione è una). Una partenza derivata
**anteriore all'inizio della sessione** è un errore (le missioni fuori finestra saranno rifiutate dal validatore della fase
F8; qui non si tagliano in silenzio). `Activation.ON_EVENT` è solo dichiarabile: `ValueError`.

### API

`AssetMovement(mission_id, asset_id, route, start, speed, holds, present_before, present_after, grounded_before,
grounded_after)` (`:387-415`; gli ultimi cinque campi sono della F5 e hanno default «nessuna attesa, nessuna presenza»);
`mission_movements(mission, t0, air_bases)` (`:909-926`, uno per asset nell'ordine degli asset; `air_bases` serve al
criterio d'atterraggio, §6.15); `session_movements(missions, t0)` (`:1041-1076`): `(routes, starts, speeds)` per
`schedule_contacts`, **solo** per gli asset con rotta (gli altri restano fermi) e `speeds` solo per quelli con velocità
uniforme dichiarata; **non portano le attese né la presenza** (in sessione i tratti completi vanno allo scheduler come
`legs`, §6.15); solleva `ValueError` se un asset è in due missioni (già vietato da `SessionOrder`, qui per chi chiama
direttamente); `waypoint_times(movement)` (`:1079-1083`): gli istanti assoluti d'**arrivo** ai punti della rotta
dell'asset, **attese comprese** (F5-C), senza taglio alla sessione (base delle ETA effettive, §6.11); `mission_routes`
(`:1457-1459`); `check_mission_speed` (regola A, sopra).

Le funzioni delle fasi successive, tutte descritte nelle sezioni indicate:

| Funzione | Fase | Sezione |
|---|---|---|
| `mission_holds`, `_wait_end`, `_locked_targets`, `_timeline` | F5-C | §6.16 |
| `movement_legs`, `grounded_intervals`, `grounded_schedule`, `lands_on_air_base`, `air_base_points`, `final_posture`, `session_postures` | F5-A/B | §6.15 |
| `airborne_legs`, `is_loop_mission`, `bingo_return_rule`, `is_transfer_mission`, `mission_bingo_decision`, `check_mission_bingo`, `check_mission_fuel`, `route_fuel_demand` | F6-B2 → G4b | §6.19 |

**Cosa non fa** (docstring `:277-283`): nessun circuito d'orbita (le orbite sono presenza ferma, §6.16); il carburante non è
calcolato qui (`Fuel_Model`); non usa **ruoli, regole e bersaglio** della missione (ROE, allerta, EMCON, reazione alla
minaccia, formazione: validati e portati dalla porta ma non letti da `Logic`; il bersaglio è letto solo dai criteri di
fine, §6.18); nessun rientro (RTB) nella rotta: lo costruisce la sessione, dalla decisione di `mission_bingo_decision`
(§6.19). Nessun RNG, nessuna mutazione: funzioni pure (la vista non copia né muta gli asset).

## 6.11 Esito di missione (`_mission_outcome`, `:1905-2012`; prima forma alla F3, regola unica dalla F6-B1)

Dopo che tutti gli eventi sono stati applicati, `run_session` calcola un `MissionOutcome` per ogni missione
dell'ordine (`:2804-2810`), con gli asset nello stato **finale** (salute dopo l'applicazione, rientri ed esaurimenti
come risultano dopo tutte le ri-pianificazioni). Alla F3 la regola era una «prima forma» a tre casi (completata,
distrutta, non completata); dalla F6-A/F6-B in poi è la **regola unica** qui sotto, che legge fino a quattro fonti:
le distruzioni in combattimento (`_destruction_times`, `:1885-1902`), le fini di attività dei criteri di missione
(`_activity_ends`, `:1751-1794`, §6.18), l'esaurimento del carburante (`fuel_ends`, §6.17) e i rientri
(`bingo_ends`, §6.19-6.20).

**Per asset** (`AssetMissionOutcome`), nell'ordine in cui i casi sono provati:

1. `DESTROYED`/`DESTROYED` all'istante del primo `DamageEvent` che lo distrugge, o a `t0` se era già distrutto
   all'inizio, **a meno che** non sia stato perso per carburante prima;
2. `DESTROYED`/`FUEL_EXHAUSTED` all'istante dell'esaurimento, con **`crew_recovered=True`**, per un aereo a secco in
   volo senza base raggiungibile in planata (`FUEL_CRASH`, §6.17; l'equipaggio recuperato è decisione dell'utente del
   2026-10-15, vale per il solo aereo perso per carburante: le perdite in combattimento hanno `crew_recovered=None`);
3. altrimenti (stato `DAMAGED` se la salute finale è < 100, altrimenti `OPERATIONAL`):
   - `ROUTE_COMPLETED` all'istante d'arrivo all'ultimo punto, se lo raggiunge dentro la sessione **e** non dopo una
     fine di attività (l'asset a fine attività prosegue passivo sulla rotta: un arrivo successivo non completa);
   - altrimenti la **fine di attività** (`WINCHESTER`, `DAMAGE`, `TARGET_DESTROYED`, `MAX_DURATION`) al suo istante, se
     cade dentro la sessione e prima dell'esaurimento o del rientro;
   - altrimenti `FUEL_EXHAUSTED` all'istante dell'esaurimento (asset di terra/mare fermo nel punto, aereo atterrato in
     planata), anche se a secco sul rientro: conta l'ultimo fatto;
   - altrimenti il **rientro**: `BINGO` o, dal G4b, `DISENGAGED` (`BingoEnd.reason`), all'istante della decisione;
   - altrimenti `SESSION_END` alla fine della sessione: rotta tagliata, o missione senza rotta (sul posto), ancora
     in corso.

**Per missione** (regola unica, F6-B1/D2.d, confermata dall'utente il 2026-10-12; `:1979-1998`):

`DESTROYED` (tutti gli asset persi, anche per carburante) **>** `COMPLETED` **>** `ABORTED(motivo)` **>** `FAILED`.

- `COMPLETED` = **obiettivo raggiunto**: con `target_destroyed` dichiarato **e rappresentabile** (bersaglio `ASSET` o
  `GROUP`) i bersagli tutti distrutti nella sessione; altrimenti un asset all'ultimo punto **prima** di una distruzione
  e di una fine di attività, oppure la fine per `MAX_DURATION` (durata o tempo sulla stazione esaurito: una fine
  *regolare*). Con `target_destroyed` dichiarato la sola rotta completata **non** è l'obiettivo: `FAILED`.
- `ABORTED` = **ogni asset superstite** ha chiuso per carburante, bingo, disingaggio, munizioni o danno
  (`_ABORT_REASON_OF`, `:1570-1574`); il motivo è quello dell'asset che ha chiuso per **ultimo** e, a parità d'istante,
  la precedenza è `FUEL > BINGO > DISENGAGED > AMMUNITION > DAMAGE` (prima i fatti fisici sul carburante, poi la
  decisione tattica, poi munizioni e danno). Un gregario in winchester con il capo ancora in missione **non** fa
  abortire la missione (prima della F6-B1, con la precedenza provvisoria della F6-A, bastava un asset a secco).
- `FAILED` = fine senza obiettivo e senza motivo, compreso «ancora in corso» a fine sessione.

Con `F6_END_CRITERIA` spento resta la precedenza provvisoria della F6-A (`ABORTED(FUEL)` se *almeno* un asset
superstite è fermo o atterrato per carburante, `:1988`).

**ETA effettive** per punto (`actual_etas`): il primo passaggio, fra gli asset non ancora distrutti a quell'istante,
dentro la sessione, calcolato dai tratti con le attese (`Mission_Adapter.waypoint_times`, F5-C), **non** dalle ETA
pianificate; `None` se nessuno ci arriva (oltre un esaurimento o un bingo i punti successivi non sono raggiunti,
`:1926-1928`). È l'istante d'**arrivo** al punto, prima di un'eventuale attesa (`:2000-2012`).

Conseguenza dichiarata dal codice, non dal piano: una missione **senza rotta** (sul posto) e con almeno un
asset sopravvissuto risulta `FAILED` (nessun asset raggiunge "l'ultimo punto"); il piano della Missione la
descrive come "ancora in corso", stato che il `MissionStatus` non ha (capitolo 9 §9.5).

*Diagramma D19 — esito di missione, regola unica (`_mission_outcome`). Aggiornato a `a784a9e7`.*

```mermaid
flowchart TD
    A0["per ogni asset della missione"] --> D{"distrutto in combattimento<br/>(non prima perso per carburante)?"}
    D -->|si| AD["DESTROYED"]
    D -->|no| CR{"aereo a secco in volo,<br/>nessuna base in planata?"}
    CR -->|si| AF["DESTROYED / FUEL_EXHAUSTED<br/>crew_recovered = True"]
    CR -->|no| RC{"arriva all'ultimo punto in sessione<br/>e non dopo una fine di attivita'?"}
    RC -->|si| AR["ROUTE_COMPLETED"]
    RC -->|no| AC{"fine di attivita' prima<br/>dell'esaurimento o del rientro?"}
    AC -->|si| AE["WINCHESTER / DAMAGE /<br/>TARGET_DESTROYED / MAX_DURATION"]
    AC -->|no| FX{"esaurimento (fermo o atterrato)?"}
    FX -->|si| AX["FUEL_EXHAUSTED"]
    FX -->|no| BG{"rientro deciso?"}
    BG -->|si| AB["BINGO o DISENGAGED"]
    BG -->|no| SE["SESSION_END"]
    AD --> M{"nessun superstite?"}
    AF --> M
    AR --> M
    AE --> M
    AX --> M
    AB --> M
    SE --> M
    M -->|si| ST1["MissionStatus.DESTROYED"]
    M -->|no| O{"obiettivo raggiunto?<br/>(bersagli distrutti se dichiarati,<br/>altrimenti ultimo punto o MAX_DURATION)"}
    O -->|si| ST2["COMPLETED"]
    O -->|no| AB2{"ogni superstite ha chiuso per<br/>carburante, bingo, disingaggio,<br/>munizioni o danno?"}
    AB2 -->|si| ST3["ABORTED(motivo dell'ultimo,<br/>FUEL > BINGO > DISENGAGED ><br/>AMMUNITION > DAMAGE)"]
    AB2 -->|no| ST4["FAILED"]
```

*Diagramma D20 — pipeline di `Mission_Adapter`: dalla `Mission` a rotta, partenza e velocità per asset.*

```mermaid
flowchart TD
    MI["Mission + t0"] --> RR["reference_route<br/>(Mission.route o spezzata dei MissionWaypoint)"]
    MI -.-> RA["check_mission_speed, regola A:<br/>nessun tratto oltre la velocita' massima<br/>del mezzo piu' lento (ValueError)"]
    MI --> MS["mission_start<br/>start_time, poi eta_locked, poi tot"]
    MI --> HL["mission_holds: attese WAIT, ETA e TOT bloccati (F5-C)"]
    MI --> PR["_presence: presenza e stato a terra prima/dopo (F5-B)"]
    RR --> AR["asset_route per ogni MissionAsset"]
    AR --> Z{"offset nullo e nessuna<br/>velocita' per tratto?"}
    Z -->|si| SAME["stesso oggetto Route"]
    Z -->|no| OFF["offset_points: terna per punto<br/>(bisettrice, 1/cos(theta/2), MITER_LIMIT)"]
    OFF --> REB["_rebuild_route con velocita' per tratto"]
    SAME --> MOV["AssetMovement(route, start, speed,<br/>holds, present_*, grounded_*)"]
    REB --> MOV
    MS --> MOV
    HL --> MOV
    PR --> MOV
    MOV --> SM["session_movements -> routes, starts, speeds<br/>movement_legs / grounded_schedule -> tratti e programma a terra"]
```

*Diagramma D21 — regola dell'offset di formazione ai cambi di direzione (`_point_frame`).*

```mermaid
flowchart TD
    P["punto i della rotta di riferimento"] --> F{"primo punto?"}
    F -->|si| T1["terna del primo tratto, fattore 1"]
    F -->|no| L{"ultimo punto?"}
    L -->|si| T2["terna dell'ultimo tratto, fattore 1"]
    L -->|no| B{"h_entrata + h_uscita = 0?<br/>(inversione esatta)"}
    B -->|si| T3["terna del tratto in entrata, fattore 1"]
    B -->|no| T4["terna della bisettrice<br/>laterale x min(1/cos(theta/2), 2.0)"]
```

## 6.12 La missione come forza d'ingaggio: `_engagement_forces` e `MissionForce` (F4b, `a4d8acf0`)

**Che cosa fa.** Dalla F4b `run_session` non passa al risolutore i blocchi ma una *forza d'ingaggio* per
missione. Lo scheduler continua a ricevere i blocchi (`items_a`/`items_b`): le finestre di contatto sono per
coppia di asset e la potatura per blocco non dipende da come gli asset sono raggruppati in forze, quindi le
finestre sono **le stesse di prima**. Il raggruppamento in forze avviene dopo lo scheduler.

**`_engagement_forces(order, blocks, block_owner)`** (`:1816-1859`) costruisce, per ogni blocco in ordine di id:

- **blocco senza missioni**: la forza è il blocco stesso (stesso id e stessa classe di prima della F4b);
- **blocco con missioni**: una `MissionForce.of_mission(mission, block)` per missione, nell'ordine dell'ordine di
  sessione (`id` = `mission_id`); e, se restano asset del blocco in nessuna missione, la **vista residua**
  `MissionForce.unassigned(block, missions)` con l'id del blocco.

Restituisce `forces` (`{id di forza: forza}`) e `owner` (`{asset_id: (lato, id di forza)}`), che
`_group_windows` usa per raggruppare le finestre per coppia di forze (§6.3). Un `mission_id` uguale all'id di un
blocco passato è rifiutato in `_check_missions` (`:1811-1813`).

**`MissionForce`** (`Logic/Mission_Adapter.py:1594-1691`) è una *vista*, non una copia: i suoi `assets` sono gli
oggetti **reali** del blocco ristretti a quelli della vista (con le chiavi e nell'ordine del blocco), quindi danno,
munizioni e carburante applicati dal motore arrivano al blocco; il blocco resta l'unità di appartenenza,
rifornimento e comando (`asset.block` non cambia). Espone solo ciò che il risolutore legge (capitolo 4 §4.27):

| Attributo | Significato |
|---|---|
| `id`, `name` | `mission_id` (vista residua: id e nome del blocco) |
| `mission_id`, `mission` | l'id e la `Mission` (entrambi `None` per la vista residua); il risolutore non li legge |
| `owner_block`, `block_id` | il blocco d'appartenenza e il suo id di dominio. Il riferimento si chiama `owner_block`, **non** `block`: `Contact_Scheduler._as_block` e `Session_Simulator._as_block` scartano un `.block` (forma del `BlockItem`) e scambierebbero la vista per il suo blocco |
| `side` | lato del blocco |
| `assets` | `{chiave: asset}` del blocco ristretto alla vista |
| `can_disengage` | calcolato sul **blocco** con la regola di `_can_disengage` (`validate_class(block, 'Military') or not validate_class(block, 'Block')`, `:1636`): adattatore, perché la vista non è né `Military` né `Block` (capitolo 4 §4.7) |
| `postures`, `grounded` | postura continua e insieme degli aerei a terra della vista: valorizzati **solo** per la vista residua, vuoti per una vista di missione (`:1643-1645`, §6.14) |
| `salvo_interceptors()` | quella del blocco ristretta agli asset della vista, stesso ordine (`:1678-1687`) |

Non c'è nessuna delega generica degli attributi al blocco (niente `__getattr__`): le grandezze aggregate del
blocco (potenza di combattimento, volumi, ...) riguardano **tutti** i suoi asset e, lette sulla vista, sarebbero
sbagliate in silenzio. Un asset che non appartiene al blocco, o un blocco senza id di dominio, solleva
`ValueError`; `of_mission` solleva `TypeError` se non riceve una `Mission` e `ValueError` se il blocco non è
quello della missione.

**`SessionOrder.committed` per forza.** La porta lo chiavava per blocco e continua a farlo.
`_engagement_committed` (`:1862-1882`) lo traduce: per ogni forza d'ingaggio, se il blocco della forza è in
`committed`, la restrizione vale **intersecata con gli asset della forza**; una forza di un blocco non elencato
non ha restrizione. `None` se l'ordine non restringe nulla.

**Esito.** Un `ForceOutcome` per forza d'ingaggio **e per episodio** (G4a, §6.20), con `force_id` = `mission_id` e `block_id` = blocco; per la
vista residua e per un blocco senza missioni `force_id` è l'id del blocco (capitolo 2 §2.3). L'esito di un blocco
è `SessionOutcome.outcomes_of_block`, un insieme. **Il `MissionOutcome` non dipende dalla F4b**: è calcolato per missione
come in §6.11, a prescindere dall'ingaggio.

*Diagramma D30 — la vista di missione `MissionForce` e ciò che il risolutore ne legge (§6.12).*

```mermaid
classDiagram
    class MissionForce {
        +str id
        +str name
        +str mission_id
        +str block_id
        +str side
        +dict assets
        +bool can_disengage
        +dict postures
        +frozenset grounded
        +of_mission(mission, block) MissionForce
        +unassigned(block, missions) MissionForce
        +salvo_interceptors() list
    }
    class Mission {
        <<da Mission_Types>>
    }
    class Block {
        <<Block o Military>>
    }
    class resolve_engagement {
        <<risolutore>>
    }

    MissionForce --> Mission : mission, None se vista residua
    MissionForce --> Block : owner_block
    resolve_engagement ..> MissionForce : forza d'ingaggio
```

*Diagramma D31 — come `_engagement_forces` costruisce le forze di un blocco (§6.12).*

```mermaid
flowchart TD
    B["per ogni blocco, in ordine di id"] --> Q{"il blocco ha missioni nell'ordine?"}
    Q -->|no| W["forza = il blocco stesso<br/>id del blocco, nessun block_id"]
    Q -->|si| M["una MissionForce per missione<br/>id = mission_id, block_id = blocco"]
    M --> R{"restano asset del blocco<br/>in nessuna missione?"}
    R -->|si| V["vista residua MissionForce.unassigned<br/>id del blocco, con postures e grounded"]
    R -->|no| E["nessuna vista residua"]
    W --> O["owner: asset -> lato, id di forza"]
    M --> O
    V --> O
    E --> O
```

## 6.13 Il dominio di coordinamento: `coordination_domains` (F4b+, `098671d7`)

`Mission_Adapter.coordination_domains(forces, operations)` (`Logic/Mission_Adapter.py:1696-1776`) assegna a ogni
forza d'ingaggio la **chiave del suo dominio di coordinamento** che il risolutore riceve come `coordination_of`
(capitolo 4 §4.28). La regola è dell'utente (decisioni 6 e 7 del 2026-10-11): due forze **dello stesso lato**
sono nello stesso dominio se hanno lo stesso **blocco** *oppure* appartengono alla stessa **Operazione**, con
**unione transitiva**. Realizzata con un union-find (`find`/`union`, `:1725-1738`) su nodi `('force', id)`,
`('block', lato, id del blocco)` e `('operation', lato, id dell'Operazione)`:

- ogni forza è unita al proprio nodo-blocco (`:1756`): per una `MissionForce` è `block_id`, per un blocco senza
  missioni è l'id del blocco; **la vista residua e il blocco senza missioni hanno l'id del blocco, quindi stanno
  nel dominio delle missioni del blocco**;
- se la forza è una missione in un'Operazione, è unita anche al nodo-Operazione (`:1758-1763`). L'appartenenza si
  legge da `Operation.mission_ids` e da `Mission.operation_id` (`SessionOrder` ne garantisce la coerenza);
- **mai a cavallo di due lati**: i nodi-blocco e -Operazione portano il lato nella chiave, quindi un'Operazione
  che elenca missioni di lati diversi (`SessionOrder` non conosce i blocchi e non può vietarlo) lega solo le
  missioni dello stesso lato — **un dominio per lato**, con un `warning` (`:1765-1769`). È una scelta dichiarata:
  l'Operazione è un raggruppamento di scopo, non di comando, quindi l'ordine non è rifiutato. Il risolutore
  verifica comunque l'invariante (`ValueError`, capitolo 4 §4.28);
- **chiave** = l'id di forza minore (ordine delle stringhe) fra i membri del dominio (`:1771-1776`): è l'id di una
  delle sue forze, quindi non può coincidere con la chiave di un altro dominio, e senza legami la chiave di una
  forza è il suo id (comportamento precedente). La funzione è pura, deterministica, indipendente dall'ordine dei
  dizionari.

Solleva `TypeError` se `forces` non è una mappa o se `operations` contiene altro che `Operation`
(`:1711-1718`). Chi la usa: `run_session` (`:2090`) la passa a `_connected_components` (le forze di un dominio vanno
nella stessa run, §6.3) e a ogni `resolve_engagement`.

*Diagramma D35 — regole di unione di `coordination_domains` (§6.13).*

```mermaid
flowchart TD
    F["per ogni forza d'ingaggio, in ordine di id"] --> N["nodo forza"]
    N --> B["unione con il nodo blocco: lato e id del blocco<br/>vista residua e blocco senza missioni: id del blocco"]
    N --> O{"la missione e' in un'Operazione?<br/>Operation.mission_ids o Mission.operation_id"}
    O -->|si| U["unione con il nodo Operazione: lato e id Operazione"]
    O -->|no| X["nessuna altra unione"]
    U --> L{"l'Operazione ha missioni di lati diversi?"}
    L -->|si| W["un dominio per lato, con warning"]
    L -->|no| K["un solo dominio"]
    B --> C["chiave del dominio = id di forza minore del gruppo"]
    W --> C
    K --> C
    X --> C
```

## 6.14 Postura continua e aerei a terra: `continuous_posture`, `grounded_assets` (F4c, `af2efbe6`; esteso dalla F5)

**La decisione** (utente, 2026-10-11, D1.c): gli asset di un blocco **senza missione** non sono più semplicemente
"fermi": hanno una *postura continua*. Un **aereo** è a terra; un'**unità terrestre o navale** è in postura
`Defense` dichiarata, con il tiro invariato (capitolo 4 §4.30).

**`continuous_posture(asset)`** (`Logic/Mission_Adapter.py:1477-1490`) è una funzione pura che legge solo la classe
dell'asset (`validate_class`), senza leggere né mutare il suo stato: `Aircraft` → `PARKED_POSTURE`
(`StartMode.PARKING_COLD.value`, cioè `'parking_cold'`, "l'aereo sul parcheggio a motori spenti"); `Ship` →
`SEA_DEFENSE_POSTURE` (`Sea_Task.DEFENSE.value`, `'Defense'`); ogni altro asset (veicolo, struttura, stub) →
`GROUND_DEFENSE_POSTURE` (`Ground_Action.DEFENSE.value`, `'Defense'`); le costanti sono a `:345-347`. Le etichette
sono **valori già esistenti** di `Context`/`Mission_Types`, non costanti nuove. `unassigned_postures(assets)`
(`:1493-1503`) dà `{asset_id: postura}` saltando gli asset senza id.

**`grounded_assets(forces)`** (`:1506-1529`) raccoglie gli id degli aerei a terra fra le forze d'ingaggio della
sessione: per una `MissionForce` residua è `force.grounded` (`:1644-1645`, aerei con postura `PARKED_POSTURE`);
per un **blocco senza missioni** (passato tale e quale) si applica la stessa regola agli asset del blocco
(`:1526-1527`); gli aerei di una vista di **missione** non sono a terra (`grounded` vuoto, `postures` vuota,
`:1643`). Restituisce un `frozenset`; vuoto se non ci sono aerei fuori missione, e allora la sessione è identica a
quella precedente alla F4c. Alla F4c `run_session` lo passava tale e quale a scheduler e risolutore; **dalla F5** lo
include come intervalli `ALWAYS` nel programma `Mission_Adapter.grounded_schedule` (`:1024-1038`), calcolato una volta
(`Session_Simulator.py:2103`) e passato allo scheduler e a ogni ingaggio (§6.1, §6.15).

**La postura è un dato della vista, non un effetto.** `MissionForce.postures` non cambia estrazioni né esiti
(`Defense` non entra nel fattore di postura della soglia di rottura, che si legge dai tratti di rotta: capitolo 4
§4.21) e **non è nell'esito di forza**: `ForceOutcome` non ha un campo postura. L'utente ha deciso che la postura
sarebbe entrata nell'esito con la F5, e così è stato: dalla F5-B ogni asset ha la sua postura finale in
`SessionOutcome.postures` (§6.15), non in `ForceOutcome`.

**La F5 (realizzata).** Il criterio è un *programma passato al motore*, non una proprietà della forza: la F5 lo ha reso
dipendente dal tempo (presenza prima della partenza, dove anche un aereo con missione non ancora partita è a terra,
§6.15) senza toccare la vista né il protocollo di fire control; per gli aerei senza missione resta «sempre a terra»
(`ALWAYS`, capitolo 3 §3.7).

*Diagramma D36 — postura continua di un asset senza missione (§6.14).*

```mermaid
flowchart TD
    A["asset senza missione"] --> C{"classe dell'asset"}
    C -->|Aircraft| P["PARKED_POSTURE, parking_cold<br/>a terra: entra in grounded"]
    C -->|Ship| S["Sea_Task.DEFENSE"]
    C -->|altro: veicolo, struttura, stub| G["Ground_Action.DEFENSE"]
    P --> GR["grounded_assets: aerei della vista residua<br/>e dei blocchi senza missioni"]
    S --> PO["MissionForce.postures: dato della vista, tiro invariato;<br/>postura finale in SessionOutcome.postures (F5-B)"]
    G --> PO
```

## 6.15 Presenza e postura nell'esito (F5-A, F5-B)

**La decisione** (utente, 2026-10-11/12, D1.a/b, deviazioni 12-13 del piano): un asset di missione **non sparisce
fuori dalla sua rotta**. Prima della F5 un asset con missione esisteva per lo scheduler solo fra la partenza e l'arrivo;
ora (`F5_PRESENCE`, attivo dalla F5-B, `Mission_Adapter:376`):

- **unità terrestri e navali**: presenti **ferme** nella posizione di partenza prima di partire e in quella finale dopo
  la fine, in postura `Defense`, quindi rilevabili e ingaggiabili in quei tratti (il carro fermo a 4 km dal nemico
  resta un bersaglio: esperimenti E1/E3 dell'analisi, scenario S22);
- **aerei che non partono in volo** (`start_mode` parcheggio o pista, cioè diverso da `AIR`): presenti e **a terra**
  dall'inizio della sessione al decollo — bersagli di superficie passivi come gli aerei senza missione della F4c
  (capitolo 4 §4.30);
- **aerei dopo la fine della rotta**: a terra **solo se** l'ultimo punto è un `LAND` su una **base vera**
  (`lands_on_air_base`, `Mission_Adapter:876-896`: il riferimento del waypoint è un asset di un blocco `is_Air_Base()`,
  oppure il punto cade entro `AIR_BASE_AREA_RADIUS_M = 3000 m` — **STIMA di progetto**, `:362` — da un asset non aereo
  di una base del **lato della missione**, `air_base_points`, `:844-873`); altrimenti **escono di scena all'arrivo**
  (postura `off_scene`). Atterrare su una base nemica non è un atterraggio.

**Come lo realizza `Mission_Adapter`.** `AssetMovement` (`:387-415`) ha quattro campi nuovi (`present_before`,
`present_after`, `grounded_before`, `grounded_after`) che `_presence` (`:899-906`) riempie per missione: terra e mare
presenti prima e dopo e mai a terra; aria presente e a terra prima se non parte in volo, presente e a terra dopo se
atterra su una base vera. Poi:

| Funzione | Cosa dà | Riga |
|---|---|---|
| `movement_legs(movement, t0, t_end, presence=True)` | i tratti di un asset nella sessione: movimento con attese (`_timeline`) più, con `presence`, il tratto fermo da `t0` alla partenza e dalla fine a `t_end`; ritagliati a `[t0, t_end]`. `presence=False` = solo movimento (carburante) | `:972-997` |
| `grounded_intervals(movement)` | gli intervalli `[lo, hi)` a terra: prima `(-inf, fine delle attese al punto di partenza)`, dopo `[arrivo all'ultimo punto, +inf)` | `:1000-1021` |
| `grounded_schedule(forces, movements)` | un `GroundedSchedule` (capitolo 3 §3.7): `ALWAYS` per gli aerei senza missione (`grounded_assets`, §6.14), gli intervalli sopra per gli aerei di missione | `:1024-1038` |
| `final_posture(mission, movement, grounded, session_end)` | la postura di un asset di missione a fine sessione | `:1534-1561` |
| `session_postures(forces, movements, grounded, session_end)` | `{asset_id: postura}` di **tutti** gli asset delle forze (di missione: `final_posture`; senza missione: la postura continua della F4c) | `:1564-1591` |

**Le posture** (`final_posture`): a terra a fine sessione → `PARKED_POSTURE` (`parking_cold`); aereo in volo → il tipo di
missione; aereo uscito di scena alla fine della rotta → `OFF_SCENE_POSTURE = 'off_scene'` (`:351`, etichetta, non un
valore di `Context`); terra e mare → `Defense` a movimento finito o non ancora iniziato (D1.a/b), altrimenti la postura
di riferimento del tipo di missione (`Context.postures_for`). `Session_Simulator` la corregge poi per i casi che
`Mission_Adapter` non vede — il rientro (`_postures_after_bingo`, `:1543-1557`) e l'esaurimento
(`_postures_after_fuel`, `:1419-1439`) — e per i distrutti (`destroyed`, §6.18) in tre passi successivi
(`:2829-2845`). `SessionOutcome.postures` è un'**uscita**: non cambia la storia (contatti, colpi, danni), è riportata
in ogni caso anche con `F5_PRESENCE` spento.

**Il cablaggio in `run_session`.** `mission_movements(mission, t0, air_bases)` riceve le basi del lato della missione
(`:2093-2098`); `grounded = MA.grounded_schedule(forces, movement_of.values())` (`:2103`) è passato a scheduler e
risolutore; i **tratti di movimento** senza presenza (`presence=False`, `:2122-2123`) vanno al carburante (la presenza
ferma non consuma), quelli con presenza (`movement_legs(movement, t0, session_end)`, `:2196`) allo scheduler come `legs`
e al risolutore come tratti degli asset (`all_legs`, `:2222-2234`).

*Diagramma D41 — ciclo di vita di un aereo di missione in sessione (stati e transizioni che la sessione modella).*

```mermaid
stateDiagram-v2
    state "A terra, prima del decollo (grounded)" as Parked
    state "In volo sulla rotta" as Airborne
    state "In attesa nel punto (WAIT, tratto fermo)" as Waiting
    state "Rientro (bingo o disingaggio)" as Returning
    state "Planata" as Gliding
    state "A terra su una base (parking_cold)" as Landed
    state "Uscito di scena (off_scene)" as OffScene
    state "Perso per carburante" as Lost
    state "Distrutto (destroyed)" as Destroyed

    [*] --> Parked: start_mode parcheggio o pista
    [*] --> Airborne: start_mode AIR (comparsa in volo)
    Parked --> Airborne: decollo (fine delle attese al punto di partenza)
    Parked --> Destroyed: colpito sul parcheggio
    Airborne --> Waiting: azione WAIT, ETA o TOT bloccati
    Waiting --> Airborne: fine dell'attesa
    Airborne --> Landed: ultimo punto LAND su una base vera
    Airborne --> OffScene: ultimo punto LAND non su una base
    Airborne --> Returning: bingo alla partenza o dopo un episodio, disingaggio
    Returning --> Landed: raggiunge la base (di partenza o alternativa)
    Returning --> OffScene: BINGO_EXIT, comparso in volo senza basi
    Airborne --> Gliding: esaurimento con una base in planata
    Returning --> Gliding: a secco sul rientro, base in planata
    Gliding --> Landed
    Airborne --> Lost: esaurimento senza base in planata
    Returning --> Lost: a secco sul rientro, nessuna base
    Airborne --> Destroyed: DamageEvent
    Returning --> Destroyed: DamageEvent
    Landed --> Destroyed: colpito a terra
    Lost --> [*]
    Destroyed --> [*]
    OffScene --> [*]
```

**Limiti dichiarati** (`F4_Differenze_Scenari.md`, sezione F5-B): un aereo che parte dal parcheggio è a terra nel
**primo punto** della rotta, alla sua quota (la rotta deve cominciare sulla base: il motore non la porta a terra);
nessuna fase di rullaggio; l'area di una base è un cerchio di `AIR_BASE_AREA_RADIUS_M` (stima) intorno a ciascun
asset non aereo, non il perimetro reale (modulo mappe), e una base senza asset non aerei ha area vuota (resta il
criterio del riferimento); la presenza dopo la fine è nella posizione finale della rotta; due esecuzioni esistenti
cambiarono nella storia (S6-0, S6-2: il gruppo navale, che prima spariva all'arrivo, resta nel punto finale e continua
a lanciare), accettate dall'utente il 2026-10-12.

## 6.16 Attese, ETA bloccate e TOT per missione (F5-C)

Interruttore `Mission_Adapter.F5_WAITS` (attivo dalla F5-C, `:377`). Le azioni **WAIT** di una missione
(`MissionAction` con `ActionKind.WAIT`, modo `'hold'` o `'orbit'`, durata `wait_duration_s` **oppure** fino a un
istante `wait_until`), le **ETA bloccate** dei punti (`MissionWaypoint.eta_locked`) e il **TOT** della missione
entrano nel movimento come **tratti fermi** nel punto della rotta (`AssetMovement.holds`, `((indice del punto, durata
[s]), ...)`): `_timeline` (`:929-969`) li inserisce e sposta i successivi della durata. Le attese sono **le stesse per
tutti gli asset della missione** (la formazione attende insieme: regola A).

- **`hold` e `orbit` sono la stessa cosa per il motore**: presenza ferma nel punto per la durata. Per l'orbita è
  un'**approssimazione dichiarata**: nessun circuito geometrico (`MissionAction` non dichiara raggio né velocità
  d'orbita, e non se ne inventano); le finestre di contatto coprono quindi tutta l'attesa intorno al punto, con
  un errore di posizione pari al raggio del circuito reale (qualche km per un caccia).
- **`mission_holds(mission, start, t0)`** (`:768-823`) le calcola una volta sulla rotta di riferimento con le
  velocità di missione (la stessa temporizzazione di `mission_start`). Per ogni punto: le azioni WAIT del punto
  (`_wait_end`, `:723-746`, con la condizione d'avvio `ON_ARRIVAL`/`AT_TIME`/`AFTER_DURATION`) e la **sincronizzazione**:
  se il punto *successivo* ha un'ETA bloccata (o è l'ancoraggio del TOT) e sarebbe raggiunto in anticipo, l'attesa si
  allunga fino a raggiungerlo esattamente all'istante bloccato (attesa *prima* del punto). In **ritardo**: un warning;
  la velocità non cambia, e le ETA effettive lo riportano. Restituisce `()` senza rotta, senza attese o se la rotta non
  ha un tratto per ogni coppia di waypoint.
- **La partenza** (`mission_start`, `:642-697`): precedenza `start_time` (ritardata, dalla F5-C, da un'ETA bloccata sul
  punto di partenza più tarda, `:656-659`), poi la prima ETA bloccata, poi il `tot`. Senza `start_time` la partenza è
  derivata **all'indietro** dall'istante bloccato meno la percorrenza **e** le attese di durata nota dei punti prima
  dell'ancoraggio (`_relative_wait`, `:706-720`, anticipo `:689-691`); le attese fino a un istante assoluto non anticipano
  (dipendono dalla partenza stessa). Con `start_time` la missione attende prima del punto d'ancoraggio.
- **Il TOT è di ogni missione, non dell'Operazione** (decisione dell'utente, 2026-10-12, commit `03d77640`). La F5-C
  (`4da618b1`) aveva introdotto un TOT comune d'Operazione (`Operation.tot`, `operation_tots`) usato per le missioni
  che non ne dichiaravano uno; l'utente l'ha **rimosso** lo stesso 2026-10-12: missioni coordinate dichiarano ciascuna il
  proprio TOT, uguali o sfalsati. L'esempio dell'utente: una *Fighter Sweep* su una zona che anticipa di qualche minuto
  l'arrivo dei bombardieri di un'altra missione sulla stessa zona ha un TOT diverso da quello dei bombardieri,
  anche se le due missioni partono insieme nella stessa Operazione. `_locked_targets` (`:749-765`) usa solo il
  `Mission.tot`, ancorato al primo waypoint `ATTACK` (o, in mancanza, `OBJECTIVE`, `_TOT_ANCHOR_ROLES`, `:340`); un TOT
  senza punto d'ancoraggio e con `start_time` è ignorato con un warning (`:762-763`), senza `start_time` è un `ValueError`
  (`:672-674`). Nell'Operazione resta solo la regola d'esito (`OutcomeRule`), che nessuno calcola ancora.
- **ETA effettive** (`waypoint_times`, `:1079-1083`): gli istanti d'**arrivo** ai punti dai tratti, attese comprese; vanno
  in `MissionOutcome.actual_etas`, mentre le ETA pianificate restano nei `MissionWaypoint`.
- **Carburante**: dalla F6-A le attese consumano **nel tempo alla crociera** dell'asset, con un `FuelEvent` per tratto
  (§6.17); nella F5-C non consumavano.
- **`Activation.ON_EVENT`** resta solo dichiarabile (`ValueError`).

Con `F5_WAITS` spento: nessuna attesa, partenza e ETA come prima della F5 (il TOT della missione deriva comunque la
partenza, come dalla F3). Scenari: S23 (CAP in orbita, sosta di un carro, TOT per missione; capitolo 8 §8.10).

## 6.17 Carburante per tratto e vincolo del movimento (F6-A)

**La decisione** (utente, 2026-10-12): fino alla F5 il carburante era un vincolo *a posteriori* — un solo `FuelEvent` a
fine movimento — e un asset a secco continuava a muoversi e a combattere (esperimento E5 dell'analisi: un carro a secco
dopo 852 m di 7 km ingaggiato 3 km più avanti). Dalla F6-A il carburante **vincola il movimento e i contatti**, dietro
due interruttori separati (`F6_FUEL_PER_LEG`, `F6_FUEL_CONSTRAINT`, `:721-722`) per attribuire le differenze a una sola
causa.

**Quali tratti consumano** (`_consuming_legs`, `:1280-1297`): per ogni asset di missione i tratti di **movimento**
ritagliati alla sessione (`movement_legs(..., presence=False)`), attese comprese; esclusi i tratti degeneri (durata
nulla) e i tratti **fermi di un aereo a terra** (parcheggio prima del decollo, sosta dopo l'atterraggio: motori
spenti). Con `F6_FUEL_PER_LEG` spento i tratti fermi non consumano mai (come prima della F6-A).

**Esaurimento a monte (`F6_FUEL_CONSTRAINT`).** Il carburante dipende solo dai tratti e dal carburante di partenza, quindi
istante e punto dell'esaurimento si calcolano **prima** dello scheduler (`Fuel_Model.fuel_exhaustion`, alla crociera,
capitolo 5 §5.2.3) e i tratti oltre quel punto **non esistono**: i tratti troncati vanno allo scheduler (`legs`) e al
risolutore, quindi i contatti sono calcolati sui tratti reali. L'esito (`_fuel_end` → `_exhaustion_end`, `:1313-1357`,
`FuelEnd`, `:814-831`) dipende dall'asset:

| Esito (`FuelEnd.kind`) | Chi | Che cosa succede |
|---|---|---|
| `FUEL_HALT` | terra/mare, o aereo ancora a terra o a quota ≤ 0 (serbatoio vuoto al decollo, `on_ground`) | **fermo** nel punto di esaurimento fino a fine sessione, presente e bersaglio (come la presenza fuori rotta, §6.15), postura `Defense`; **non** distrutto |
| `FUEL_GLIDE` | aereo in volo con una base aerea **del suo lato** entro quota × `GLIDE_RATIO` | **planata** in linea retta sulla base più vicina alla velocità di crociera (semplificazione dichiarata), poi **a terra** sulla base (programma `grounded` dall'atterraggio, bersaglio di superficie passivo, postura `parking_cold`); durante la planata è un aereo in volo come gli altri |
| `FUEL_CRASH` | aereo in volo senza base raggiungibile in planata | **perso** all'esaurimento: i tratti finiscono lì e, dopo gli ingaggi, la salute è portata a 0 con `Asset.apply_damage` (`:2816-2826`) — lo stesso canale del danno da combattimento, stato `Destroyed` — **senza un `DamageEvent`** nell'esito (non è un colpo: nessun tiratore, nessuna arma); esito per asset `DESTROYED`/`FUEL_EXHAUSTED` con `crew_recovered=True` |

Il punto di atterraggio è la posizione dell'asset di base più vicino, a quota 0 (terreno non modellato); la quota è
quella del punto di esaurimento, interpolata fra i waypoint, trattata come altezza sulla base. L'idoneità della base per
tipo d'aereo (lunghezza della pista, elicotteri, portaerei) **non è modellata**: qualunque base aerea amica va bene
(`air_base_points`).

Le funzioni di supporto: `_truncate_at_fuel_end` (`:1360-1373`) tronca i tratti di presenza e li chiude con l'esito
(fermo nel punto, planata e sosta sulla base, nulla se perso; lista **vuota** = l'asset non esiste nella sessione, aereo
perso alla partenza); `_grounded_after_fuel` (`:1376-1404`) corregge il programma a terra (gli intervalli che
cominciano dopo l'esaurimento cadono; un aereo a terra all'esaurimento ci resta; uno in planata è a terra
dall'atterraggio); `_fuel_truncated` (`:1407-1416`) applica il troncamento a presenza e movimento insieme;
`_postures_after_fuel` (`:1419-1439`) la postura finale.

**Contabilità (`F6_FUEL_PER_LEG`).** Nel passo finale (§6.2), all'evento MOVEMENT dell'asset, **un `FuelEvent` per tratto
che consuma**, in ordine, applicato subito (`Fuel_Model.apply_fuel_event`); dopo un evento esaurito nessun altro
(`:2722-2749`). Spento: un solo `FuelEvent` per asset sulla distanza dei tratti di movimento, le attese non consumano
(`:2751-2778`).

*Diagramma D42 — come si compongono i tratti di un asset di missione prima dello scheduler.*

```mermaid
flowchart TD
    MV["mission_movements:<br/>rotta, partenza, velocita', attese, presenza"] --> ML["movement_legs(presence=False):<br/>tratti di movimento, con le attese"]
    MV --> PL["movement_legs(presence=True):<br/>+ presenza prima e dopo"]
    ML --> BD{"aereo con EndCriteria.bingo<br/>e F6_BINGO?"}
    BD -->|si| DE["_decision_end sulla missione INTERA<br/>(airborne_legs): bingo alla partenza?"]
    BD -->|no| FE
    DE -->|rientro| RB["tratti fino al bingo + rientro<br/>(_legs_after_bingo), BingoEnd"]
    DE -->|"no / continua / nessuna base"| FE
    RB --> FE["_fuel_end sui tratti che consumano:<br/>esaurimento a monte (fuel_exhaustion)"]
    FE -->|"FUEL_HALT / GLIDE / CRASH"| TR["_fuel_truncated: presenza e movimento<br/>troncati, programma a terra corretto"]
    FE -->|"il carburante basta"| SC
    PL -->|"stesso rientro e stesso troncamento"| TR
    TR --> SC["Contact_Scheduler.schedule_contacts(<br/>grounded, legs = tratti di presenza)"]
```

**Limiti dichiarati**: il vincolo è calcolato a monte alla **crociera**; per i veicoli e le navi i due regimi coincidono,
per gli aerei il consumo d'ingaggio (G3) e il ri-calcolo del G4b chiudono il limite (§6.20); consumo delle soste =
crociera anche per il loiter e per terra/mare (sovrastima); un asset distrutto a metà rotta consuma comunque i tratti
(troncati) interi; durante la planata l'aereo può essere ingaggiato e sparare (l'esaurimento non è fra i criteri di
fine attività); terreno non modellato; idoneità della base non modellata.

## 6.18 Fine di attività e stato di missione (F6-B1)

**La decisione** (utente, 2026-10-12, D2.a/D2.d): i criteri di stato *dichiarati* in `EndCriteria` chiudono l'**attività**
dell'asset senza cambiargli la rotta (per il risolutore, capitolo 4 §4.31): dall'istante della fine l'asset non lancia
più salve offensive, prosegue **passivo** sulla rotta pianificata, resta presente, bersaglio e intercettore. Interruttori
`F6_END_CRITERIA` e `F6_DESTROYED_POSTURE` (`:733-734`), entrambi attivi; nei default di `EndCriteria` nessun criterio è
attivo, quindi nessuno scenario preesistente cambia.

**Costruzione dei criteri** (`_activity_plans`, `:1662-1705`, un `ActivityPlan` per asset, `:1578-1596`):

| Criterio | Come la sessione lo legge |
|---|---|
| `winchester` | le **voci della scorta per arma** dell'asset nelle categorie elencate (`_winchester_weapons`, `:1633-1659`; categoria = chiave di primo livello del registro d'arma del dominio, `Fire_Control.weapon_category`, capitolo 4 §4.31). Scatta quando sono **tutte** a zero nello stato ombra. **Inattivo con un warning** per un asset senza scorta per arma, senza armi di quelle categorie, o con un'arma di quelle categorie **non modellata** (contata a unità: non si esaurisce mai). Già a zero alla partenza: fine alla partenza della missione |
| `damage_threshold` | salute persa / salute **a inizio sessione** ≥ soglia (*mission kill*, asset non distrutto) |
| `target_destroyed` | bersaglio `ASSET` (l'asset) o `GROUP` (gli asset del blocco, o della missione, con quell'id: `_mission_target_ids`, `:1599-1630`); tutti distrutti (in combattimento, già all'inizio, o persi per carburante) → fine all'istante dell'ultima distruzione, non prima della partenza. Bersagli `POINT`/`AREA`/`ZONE`: **non rappresentabili prima della F7**, criterio ignorato con un warning; id sconosciuto: ignorato con un warning |
| `max_duration_s` | fine all'istante di **partenza della missione** + durata (la semantica più semplice: «durata o tempo sulla stazione» contata dalla partenza), passata al risolutore come fine nota a monte (`until`) |

`_activity_criteria` (`:1722-1739`) li traduce in `ER.ActivityCriteria`, con le distruzioni già note
(`_known_destructions`, `:1708-1719`: ingaggi già risolti, asset distrutti all'inizio, persi per carburante) e, dal G4a,
la salute d'inizio sessione come `reference_health`; `engage` li passa al risolutore (`:2457-2462`). Il bingo
aggiunge `until=bingo.time` agli asset che rientrano (`:2464-2471`) e, dal G4a, la passività da episodi precedenti
(`passive_from`, `:2473-2487`).

**L'esito per asset** (`_activity_ends`, `:1751-1794`) è la **prima** fra: la fine nota a monte (`static_end`), le fini
scattate nel risolutore (`EngagementResult.activity_ends`, escluso il bersaglio distrutto) e il **bersaglio
distrutto valutato sull'intera sessione** — non sulle fini del risolutore, perché un ingaggio risolto prima può non
sapere di una distruzione avvenuta in un ingaggio risolto dopo (limite dichiarato del risolutore); la fine per bersaglio
non è anteriore alla partenza. A parità d'istante: danno, winchester, bersaglio, durata (`_ACTIVITY_ORDER`, `:1564`).
Un asset che completa la rotta *prima* della fine resta `ROUTE_COMPLETED` (per esempio un'unità terrestre in `Defense`
danneggiata dopo l'arrivo smette comunque di sparare); un arrivo *dopo* non completa la missione.

**Lo stato di missione** è la regola unica del §6.11. **Motivi di aborto** (`_ABORT_REASON_OF`, `:1570-1574`):

| Motivo di fine dell'asset (`AssetEndReason`) | Motivo di aborto (`AbortReason`) | Prodotto da |
|---|---|---|
| `FUEL_EXHAUSTED` | `FUEL` | F6-A (§6.17) |
| `BINGO` | `BINGO` | F6-B2, G2 (§6.19) |
| `DISENGAGED` | `DISENGAGED` | G4b (§6.20) |
| `WINCHESTER` | `AMMUNITION` | F6-B1 |
| `DAMAGE` | `DAMAGE` | F6-B1 |

`THREAT` e `MISSION_ABORTED` (i gregari che seguono la missione che abortisce, D3.d) **non sono prodotti**, e
`abort_on_threat` non è letto.

**Postura `destroyed`** (`F6_DESTROYED_POSTURE`, decisione dell'utente del 2026-10-12, rimandata dalla F5-B): un asset
**distrutto a fine sessione** — in combattimento o per carburante — ha postura `Mission_Adapter.DESTROYED_POSTURE =
'destroyed'` (`:356`) nell'esito (`:2838-2845`). `Mission_Adapter.session_postures` resta la postura di piano (non legge
lo stato dell'asset). Cambia solo `SessionOutcome.postures`: 429 esecuzioni della fotografia cambiarono nella sola voce
`postures` (capitolo 8 §8.10).

**Limiti dichiarati**: `target_destroyed` su bersagli `POINT`/`AREA`/`ZONE` non rappresentabile (F7); nel risolutore il
bersaglio distrutto vede solo le distruzioni della propria run e degli ingaggi già risolti; nessuna latenza di valutazione;
`abort_on_threat` e `last_waypoint` non letti; **nessun cambio di rotta** per i criteri di questa fase (il rientro è
dell'albero di bingo, §6.19-6.20); un aereo in planata per carburante non chiude l'attività.

## 6.19 Il bingo in sessione: dal rientro rettilineo al modello G1-G5

**Che cos'è e dove vive.** Il bingo è l'istante in cui un aereo deve interrompere la missione e tornare. Il calcolo (soglia,
albero, geometria) è di `Fuel_Model` (capitolo 5 §5.2.5-5.2.8, con il diagramma D38); qui c'è **quando** si valuta, **chi**
è interessato e **come** il rientro diventa tratti, contatti ed esito. Il modello è stato costruito in tre tempi:

| Tempo | Data | Regola | Stato |
|---|---|---|---|
| F6-B2 | 2026-10-13 | bingo a priori (validatore) e in volo; rientro **in linea retta** alla base idonea più vicina con la riserva fissa `BINGO_RESERVE` = 0,10 | dietro interruttori spenti |
| F6-B2bis | 2026-10-15 | rientro lungo la **rotta a ritroso**, fabbisogno 1,2 × il ritorno | dietro interruttore spento (`F6_BINGO_DISENGAGE_RESERVE` False) |
| **G1-G5** | 2026-10-15/18 | **riserva di disimpegno**, minimo di pianificazione, soglia = resto della rotta + riserva, albero trasferimento/combattimento con basi alternative entro 3 km, consumo in ingaggio, episodi, ri-pianificazione | **modello finale, tutto attivo** |

**Il modello finale in tre grandezze** (decisioni dell'utente, 2026-10-15): la **riserva** = 5 minuti (`DISENGAGE_TIME`
= 300 s, **stima** dell'utente: il tempo per disimpegnarsi da un'intercettazione e tornare in rotta) alla **massima spinta
militare** (`emergency.consume` del registro, kg/h **dedotti**, dato **non tarato**: capitolo 5 §5.2.6); il **minimo di
pianificazione** = carburante caricato > rotta intera + riserva; la **soglia di bingo** = residuo < resto della rotta +
riserva. Al bingo l'**albero** dipende dal tipo di missione (trasferimento `TRANSPORT`: continua / ritroso / base più
vicina / regole F6-A; combattimento: interrompe sempre, base di partenza o base alternativa entro 3 km dalla rotta
(`ALTERNATE_BASE_MAX_OFFSET`, stima), la più breve raggiungibile; poi base più vicina in linea retta; poi regole F6-A).

**La valutazione alla partenza (G2)** (`:2125-2167`). Per ogni asset di missione **aerea** con `EndCriteria.bingo`
(default `True`), con `F6_BINGO` acceso e almeno un tratto di movimento: con `F6_BINGO_DISENGAGE_RESERVE` acceso
`_decision_end` (`:1467-1484`) chiama `Mission_Adapter.mission_bingo_decision` **all'inizio dei tratti della missione
intera** (`airborne_legs`, anche oltre la fine della sessione, perché l'anello legge il resto della rotta fino al
`LAND`) con il carburante di partenza. Se la decisione è «non in bingo», «continua» (trasferimento: il residuo basta a
concludere) o «nessuna base» (`NO_BASE`: regole della F6-A), nessun rientro; altrimenti `_return_end` (`:1444-1452`)
costruisce il `BingoEnd` (`:835-859`: `time`, `point`, `landing_point`, `landing_time` a velocità di crociera, `route`,
`reason`, `exits`) e un bingo che cadrebbe **dopo la fine della sessione non c'è** (`:2149-2150`). Con **il solo consumo di
movimento** residuo e resto della rotta calano insieme, quindi la soglia scatta all'inizio dei tratti **o mai**:
l'istante del bingo è l'inizio del primo tratto che consuma (dopo un'eventuale sosta a terra). Dal G3 il consumo
d'ingaggio abbassa il residuo e la soglia può scattare *dopo*: lo rivaluta la ri-pianificazione (§6.20).

**Il rientro.** Dal bingo i tratti dell'asset sono quelli pianificati **fino al bingo**, poi la spezzata del rientro
(`_return_legs`, `:1487-1505`, a velocità costante da `time` a `landing_time`, istanti proporzionali alla lunghezza) e,
nei tratti di presenza, la sosta a terra sulla base fino a fine sessione (`_legs_after_bingo`, `:1508-1520`, con
`park`); `_grounded_after_bingo` (`:1523-1540`) fa cadere gli intervalli a terra che cominciano dopo il bingo e mette
l'aereo a terra dall'atterraggio; `_postures_after_bingo` (`:1543-1557`) dà `parking_cold` a terra, il tipo di missione se
ancora in volo, `off_scene` se uscito di scena. I tratti del rientro vanno a scheduler, risolutore e carburante come
tutti gli altri (il rientro consuma, alla crociera). Dal bingo l'aereo **non lancia più salve offensive** (fine di
attività nota a monte, `until=bingo.time`, `:2464-2471`) ma resta **bersaglio e intercettore**; a **secco anche sul
rientro** valgono le regole della F6-A sui tratti col rientro (planata: `ABORTED(FUEL)`; perso: `DESTROYED`/
`FUEL_EXHAUSTED`); l'esito per asset è `BINGO` all'istante del bingo, per la missione `ABORTED(BINGO)` (§6.11). Terra e mare
non hanno bingo. `EndCriteria.bingo = False` = nessun controllo e nessun rientro (l'aereo vola fino all'esaurimento, regole
F6-A); il rientro **forzato** dopo il disingaggio (§6.20) non dipende da questo criterio.

**I validatori di pianificazione — fuori da `run_session`.** Le due funzioni di `Mission_Adapter` sono del
**pianificatore** (il futuro C2, fase F8, da confermare), non dell'esecutore:

- **`check_mission_fuel`** (G1, `:1394-1454`): ogni aereo della missione deve caricare **più** del carburante della rotta
  *intera* (`airborne_legs` alla crociera, attese comprese, `route_fuel_demand`, `:1378-1391`) più la riserva di
  disimpegno (`Fuel_Model.disengagement_reserve_with_source`); altrimenti `ValueError` con asset, carburante,
  fabbisogno, riserva con la provenienza e mancanza. Restituisce `{asset: margine}`.
- **`check_mission_bingo`** (F6-B2, rifatto dal G2, `:1252-1341`): con `disengage_reserve=True` (default,
  `_check_reserve_bingo`, `:1344-1375`) rifiuta **esattamente** le missioni che in sessione vanno in bingo alla partenza
  (anche un trasferimento che poi continua consumando la riserva: è sotto il minimo), con soglia, riserva, istante e
  decisione nel messaggio; le basi non sono richieste. Con `disengage_reserve=False` applica la regola F6-B2bis
  (`reverse_route=True`) o F6-B2 (`False`), dove serve una base idonea e `reserve` è la riserva fissa.

Le due sono **funzioni separate** perché sono regole diverse (il carico contro il criterio del rientro in volo
dell'esecutore) e si possono chiamare entrambe; la prima rifiuta con carburante ≤ minimo, la seconda con carburante <
soglia: differiscono solo all'uguaglianza esatta. Entrambe non si applicano alle missioni non aeree né a quelle con
`EndCriteria.bingo` False, e non controllano un asset senza carburante o riserva modellati. **Nessun codice di produzione
le chiama**: le chiamano solo i test (`Test_Mission_Adapter`, `Test_Session_Simulator`) e lo scenario S26, che ne verifica l'accordo con
la sessione. `run_session` **non rifiuta** un ordine per carburante: un rifiuto dentro `run_session` renderebbe irraggiungibile il
bingo in volo, e l'esecutore (come DCS con «RTB on bingo») fa tornare l'aereo.

Le funzioni di `Mission_Adapter` che servono al bingo: `airborne_legs` (`:1161-1183`, i tratti che consumano della
missione intera), `is_loop_mission` (`:1186-1210`, anello: `LAND` sulla stessa base del `DEPARTURE`, per blocco del
riferimento o entro `AIR_BASE_AREA_RADIUS_M`), `bingo_return_rule` (`:1213-1219`, `Fuel_Model.ReturnRule`),
`is_transfer_mission` (`:1222-1226`, categoria `TRANSPORT`), `mission_bingo_decision` (`:1229-1249`, il tramite verso
`Fuel_Model.bingo_decision`, con `forced` ed `exit_scene`). Le usano allo stesso modo il validatore e l'esecutore: **stesso
criterio**.

**Limiti dichiarati**: idoneità della base per tipo d'aereo non modellata (qualunque base aerea amica); terreno non
modellato (discesa rettilinea a quota 0); il ritroso ripassa sulle minacce dell'andata; nessuna salva offensiva dopo il
bingo (scelta della F6-B2: dal rientro l'aereo resta solo bersaglio e intercettore, anche se reincontra la minaccia);
nessun rientro per danno (un aereo oltre la soglia di danno della F6-B1 resta passivo sulla rotta); un trasferimento che
continua consumando la riserva ha un margine ridotto; i dati `emergency` del registro non sono tarati e la regola per gli
aerei WW2 non è implementata (capitolo 9 §9.1).

## 6.20 Consumo in ingaggio, episodi d'ingaggio e ri-pianificazione (G3, G4a, G4b)

### Il consumo in ingaggio (G3, `G3_ENGAGEMENT_FUEL`)

A ogni ingaggio a cui un aereo **partecipa**, nell'istante della sua prima partecipazione, l'aereo consuma
`Fuel_Model.engagement_fuel` (la quantità della riserva di disimpegno, capitolo 5 §5.2.8) con un `FuelEvent` istantaneo.
**Partecipa** (`_engagement_instants`, `:1229-1249`) chi ha **combattuto** secondo la definizione della F6-A
(`_engaged_assets`): ha lanciato una salva, è stato **bersaglio** di una salva (anche mancato o intercettato) o ha
**intercettato**; l'istante è il primo fra il lancio delle salve sue o dirette a lui (`Salvo.t_launch`) e le sue
intercettazioni. Il solo rilevamento reciproco senza salve **non** è partecipazione (nessuna manovra decisa dal
modello). Solo gli **aerei di missione** (`air_assets`, dominio `'air'`) **in volo** all'istante: un aereo a terra colpito
sul parcheggio non consuma (`grounded.at`). Terra e mare invariati. Il codice conta un consumo per esito d'ingaggio: dal
G4a **uno per episodio** a cui l'aereo partecipa.

Nella contabilità (`:2698-2712`, `:2720-2749`) i consumi d'ingaggio di un aereo sono messi in attesa (`pending_charges`)
e inseriti **in ordine di tempo fra gli eventi per tratto, prima del tratto in cui cadono** (nessun tratto è spezzato,
«un evento per tratto» resta), applicati con `charge` (`:2679-2687`); se l'asset non ha movimento o è già contabilizzato,
subito. Il movimento di un aereo è **sempre alla crociera**: il consumo d'ingaggio sostituisce, per gli aerei, la
sovrastima «tutto il movimento al regime `'max'`» (`g3`, `:2716-2719`). Esaurimento in ingaggio: il contatore va a zero,
nessun evento dopo; per il resto vedi la ri-pianificazione.

### Gli episodi d'ingaggio (G4a, `G4_EPISODES`)

**Il problema**: fino al G3 l'ingaggio era un blocco unico per la sessione (§6.3): X contro A al mattino e contro B la
sera era un solo ingaggio, un solo consumo, nessuna decisione possibile «dopo l'ingaggio». **La soluzione** (decisioni
dell'utente del 2026-10-17, `Proposta_G4_Ri_scheduling.md`): l'ingaggio diventa un evento *nel tempo*.

- **Episodio** (`_episodes`, `:1102-1173`): gruppo di finestre di contatto legate, direttamente o per tramite di altre,
  perché appartengono a coppie di forze che **condividono una forza** (o forze dello **stesso dominio di coordinamento**,
  §6.13) **e** i loro intervalli si sovrappongono o distano al più **`EPISODE_GAP` = 300 s** (`:805`, `= Fuel_Model.
  DISENGAGE_TIME`: ritrovare il contatto entro i 5 minuti del disimpegno è lo stesso combattimento; **legato per
  costruzione**: cambiare la durata del disimpegno cambia anche questo intervallo). Per ogni chiave (forza o dominio) le sue
  finestre, in ordine `(t_start, t_end, posizione)`, sono scandite una volta come una fusione di intervalli; le chiavi sono
  unite con un union-find. La componente connessa di prima è l'**unione dei suoi episodi**; con intervallo infinito
  coincidono. Ordine deterministico: inizio della prima finestra, poi `event_id`, poi la prima finestra.
- **Coda**: un ENGAGEMENT per episodio all'istante della sua prima finestra; `resolve_engagement` sulle sole finestre e
  forze dell'episodio; esito **applicato subito** (concatenazione di salute e scorte fra episodi,
  `assemble_session_outcome(chained=True)`, capitolo 2 §2.4).
- **Forza occupata** (`_trim_busy`, `:1176-1209`; `busy_until`, aggiornato in `engage`, `:2524-2526`): una forza è
  impegnata dal primo istante del suo episodio al `t_end` del suo esito (salve in volo comprese); le finestre non ancora
  risolte delle sue forze che cominciano prima sono **ritagliate** per partire da lì (`Contact_Scheduler.trim_contact_window`,
  capitolo 3 §3.8: CPA e reciproco ricalcolati), **scartate** se si svuotano, e gli episodi rimasti sono **ricostruiti**
  (un ritaglio può solo spostare in avanti un inizio, quindi l'ordine di estrazione resta non decrescente e la storia già
  risolta non cambia). Con l'intervallo di 300 s il caso si presenta solo con salve in volo per più di circa 300 s oltre
  l'ultima finestra (per esempio missili da crociera). Una forza che entra tardi in un episodio lungo è «occupata»
  dall'inizio dell'episodio.
- **RNG**: `counter` = ordinale degli episodi con lo stesso insieme di forze (§6.4).
- **Forza disingaggiata passiva** (`passive_from`, `:2249`, `:2522-2541`): negli episodi successivi tutti i suoi asset non
  lanciano salve offensive (`ActivityCriteria.until` = istante del disingaggio, combinato con i criteri esistenti come per il
  bingo, `:2473-2487`), restano bersaglio e intercettore; stessa regola per una fine di attività della F6-B1 scattata in un
  episodio precedente. Nel solo G4a il DES non la ri-instrada e l'esito di missione non cambia; dal G4b gli **aerei** di una
  missione disingaggiata rientrano (sotto).
- **Soglia di danno** (`ActivityCriteria.reference_health`): la salute d'inizio **sessione** (`start_health`, `:2246-2248`),
  così il danno di episodi diversi si somma. Erosione e shock della soglia di rottura sono contati sugli asset impegnati
  all'inizio dell'episodio: le perdite degli episodi precedenti non entrano nell'erosione di quello successivo (ingaggio
  diverso, tempra nuova).
- **Esiti di forza**: un `ForceOutcome` per forza **per episodio** (`SessionOutcome.outcomes_of` ne restituisce uno per
  episodio, nell'ordine di risoluzione).
- **Carburante**: la contabilità è un passo finale (§6.2).

### La ri-pianificazione dopo l'episodio (G4b, `G4_REPLAN`)

**Il problema**: col G3, un aereo che dopo un ingaggio è sotto la soglia di bingo prosegue la rotta, e uno che finisce il
carburante in ingaggio ha il contatore a zero ma vola e combatte (S26 `transfer_continue`); col G4a, una forza
disingaggiata prosegue **passiva** sulla rotta e incontra gli strati successivi (S5).

**Quando e chi** (`replan`, `:2263-2447`, chiamata dopo ogni episodio, `:2614`). Alla fine dell'episodio (istante `t_r` =
`t_end` dell'esito: l'ultimo evento, salve in volo comprese) sono candidati gli aerei di **missione** (dominio `'air'`)
che vi hanno **consumato** (G3, la stessa regola della contabilità, `:2276-2288`) **o** la cui **forza** d'ingaggio vi è
stata **disingaggiata** (con `F6_BINGO` e `F6_BINGO_DISENGAGE_RESERVE` accesi, `:2290-2299`); esclusi quelli distrutti, a
terra a `t_d`, già a secco (planata o persi), oltre la fine della sessione, o con il carburante non modellato
(`:2307-2330`). Per ciascuno, in ordine di id:

1. **Istante della decisione** `t_d = min(t_r, fine dei tratti di movimento dell'aereo)` (`:2320`): se la rotta finisce
   *dentro* l'episodio (S26 `transfer_continue`, dove l'episodio dura oltre la fine della rotta) conta solo
   l'esaurimento, non c'è più rotta da cui rientrare (`completed`, `:2321`, `:2356-2357`).
2. **Residuo analitico** a `t_d` (`Fuel_Model.fuel_at`, `:2334-2335`): carburante d'inizio sessione (`start_fuel`) meno i
   tratti che consumano fino a `t_d` alla crociera meno i consumi d'ingaggio fino a `t_d` (`charges_of`). Non è letto
   dall'asset perché la contabilità è un passo finale e durante gli episodi il contatore è ancora quello di partenza.
3. **Residuo zero** (esaurito in ingaggio): regole della F6-A **dal punto in cui l'aereo è a `t_d`** (`_exhaustion_end`,
   `:2345-2355`): planata su una base raggiungibile, o perso con l'equipaggio recuperato. Il punto è quello a fine
   episodio e non quello dell'esaurimento analitico (anteriore): la storia dell'episodio, risolto in blocco con l'aereo in
   volo fino a `t_d`, resta fissata (causalità).
4. **Altrimenti, se non è già in rientro** (`:2358-2393`):
   - **bingo** (ha consumato e `EndCriteria.bingo`): `mission_bingo_decision(..., time=t_d, fuel=residuo, legs=missione
     intera)`, albero del G2 per tipo di missione; **qui le basi alternative entro 3 km dalla rotta contano davvero**
     (all'inizio dei tratti non potevano vincere); se la decisione non fa rientrare (continua, nessuna base) è scartata;
   - **rientro forzato dopo il disingaggio** (decisione dell'utente del 2026-10-17), se il bingo non fa rientrare:
     `mission_bingo_decision(..., forced=True)`, regola di **combattimento** qualunque sia il tipo di missione, nessun
     controllo di soglia, **indipendentemente dal carburante**; motivo `AssetEndReason.DISENGAGED` / `AbortReason.DISENGAGED`
     (precedenza a parità d'istante subito dopo il bingo). Consumo d'ingaggio e disingaggio coesistono: prima il consumo
     (residuo), poi la decisione; se entrambe le regole fanno rientrare **vince il bingo**;
   - il rientro deciso è un `BingoEnd` da `t_d` con la meccanica del G2 (`_return_end`, `_legs_after_bingo`; reason
     BINGO o DISENGAGED, `dataclasses.replace`, `:2388-2393`).
5. **Esaurimento sui nuovi tratti** (`_fuel_end(..., fuel=residuo)`, `:2407-2411`): `fuel_exhaustion` da `t_d` con il
   residuo (planata o perdita della F6-A anche sul rientro). Un aereo già in rientro è ri-pianificato di nuovo **solo per
   esaurimento**, mai per un nuovo rientro.
6. **Aggiornamento** (`:2413-2442`): `bingo_ends`, `fuel_ends`, tratti di presenza (`presence_legs`, `all_legs`) e di
   movimento (`moving_legs`) sostituiti da `t_d` in poi (`_fuel_truncated` sui tratti pianificati, `route_presence`/
   `route_moving`); programma a terra ricalcolato dal programma **pianificato** (`planned_grounded`) con
   `_grounded_after_bingo` e `_grounded_after_fuel` (`:2444-2445`). `replan` restituisce `{asset: istante da cui i suoi
   tratti sono cambiati}`.

**Ri-scheduling** (`reschedule`, `:2545-2583`, se `replan` ha restituito qualcosa, `:2616-2621`): `schedule_contacts` è
rieseguito con i tratti aggiornati sulle sole coppie con un aereo ri-pianificato (`only_assets`, capitolo 3 §3.6); delle
finestre nuove si tengono quelle che finiscono dopo `t_r`, **ritagliate a `t_r`** (la storia prima è fissata) e poi alle
forze occupate (`_trim_busy`); le finestre non ancora risolte di quegli aerei sono **scartate** (`left[pair]`); gli
episodi rimasti sono **ricostruiti** (`_episodes`, stessa regola, stesso ordine). Scelta aggiunta: il tratto di una finestra
nuova già coperto da una finestra **risolta** della stessa coppia di asset con la geometria di prima (`covered`) è
**tolto** — niente seconda estrazione sullo stesso intervallo con gli stessi tratti (visto in S24-ORBIT `per_leg_off`).
Gli episodi già risolti non cambiano (causalità).

**Terminazione.** Gli episodi sono estratti in ordine di inizio non decrescente e ogni finestra nuova comincia non prima di
`t_r` (ritaglio) e della fine delle forze occupate; ogni ri-pianificazione di un aereo ne accorcia i tratti (rientro o
esaurimento) e un aereo in rientro non ne decide un altro: il ciclo termina.

### L'uscita di scena senza basi (G4b, `G4_OFF_SCENE_EXIT`, decisione dell'utente del 2026-10-17)

Un aereo **comparso in volo** (`start_mode` `AIR`, nessuna base di partenza) **senza alcuna base aerea del suo lato** che
nella ri-pianificazione deve rientrare (bingo dopo l'episodio o rientro forzato per disingaggio) non resta più passivo sulla
rotta (`BINGO_NO_BASE`): ripercorre la rotta **a ritroso fino al punto di comparsa** e lì **esce di scena**
(`Fuel_Model.BINGO_EXIT`, `BingoEnd.exits`): nessuna presenza dopo (come l'aereo che finisce la rotta senza atterrare su
una base vera, F5-B), **mai a terra**, postura `off_scene` a fine sessione se uscito entro la fine (altrimenti il tipo di
missione, in volo sul ritroso), non distrutto; nessuna salva offensiva dal rientro; esito per asset e missione = il motivo del
rientro (`DISENGAGED` o `BINGO`, `ABORTED(...)`) all'istante della decisione. Il ritroso consuma alla crociera; se il
residuo non basta per raggiungere il punto di comparsa valgono le regole della F6-A (senza basi: perso,
`DESTROYED`/`FUEL_EXHAUSTED`, equipaggio recuperato). **Ambito conservativo**: SOLO la ri-pianificazione dopo un episodio
(`exit_scene = G4_OFF_SCENE_EXIT` nelle due chiamate, `:2364`); la decisione del G2 alla partenza (`_decision_end`) e il
validatore restano senza uscita (`BINGO_NO_BASE`, regole della F6-A).

*Diagramma D40 — il ciclo episodio → contabilità del carburante → ri-pianificazione → ri-scheduling dei contatti.*

```mermaid
sequenceDiagram
    participant RS as run_session
    participant EP as _episodes
    participant ER as Engagement_Resolver
    participant FM as Fuel_Model
    participant MA as Mission_Adapter
    participant CS as Contact_Scheduler

    RS->>EP: finestre raggruppate per coppia di forze
    EP-->>RS: episodi in ordine (inizio, event_id)
    loop per ogni episodio, in ordine di tempo
        RS->>ER: resolve_engagement(finestre e forze dell'episodio,<br/>rng counter = ordinale, activity_criteria)
        ER-->>RS: EngagementResult (t_end, forze, activity_ends)
        RS->>RS: apply_engagement_result, busy_until, passive_from
        RS->>RS: replan: aerei che hanno consumato (G3)<br/>o la cui forza e' DISENGAGED
        RS->>FM: fuel_at(tratti, t_d, consumi d'ingaggio) -> residuo
        alt residuo zero
            RS->>RS: _exhaustion_end: planata o perso (F6-A)
        else sotto la soglia, o forza disingaggiata
            RS->>MA: mission_bingo_decision(time=t_d, fuel=residuo,<br/>forced, exit_scene)
            MA->>FM: bingo_decision (albero, D38)
            FM-->>RS: BingoDecision -> BingoEnd (BINGO / DISENGAGED)
        end
        RS->>FM: fuel_exhaustion(nuovi tratti, fuel=residuo)
        opt tratti cambiati
            RS->>CS: schedule_contacts(only_assets=aerei ri-pianificati)
            CS-->>RS: finestre nuove
            RS->>RS: ritaglio a t_r e alle forze occupate (trim_contact_window),<br/>scarto delle finestre vecchie, episodi ricostruiti
        end
    end
    Note over RS,FM: passo finale: coda degli ingaggi risolti + MOVEMENT
    RS->>FM: build_leg_fuel_event / build_engagement_fuel_event
    FM-->>RS: FuelEvent (uno per tratto, uno per ogni consumo d'ingaggio)
```

**Terra e mare**: nessun consumo d'ingaggio e nessun rientro; una forza terrestre o navale disingaggiata resta passiva sulla
rotta (G4a), dichiarato.

**Limiti dichiarati**: la decisione è presa alla **fine** dell'episodio, non a metà (l'episodio è risolto in blocco con i tratti
di prima; la riserva di disimpegno è il carburante di quella coda); un aereo ri-pianificato che incontrerebbe una forza ancora
occupata in un episodio già risolto la incontra solo dopo la fine di quell'episodio (forza occupata, per forza intera e non
per asset); l'uscita di scena è sempre al punto di comparsa, anche se il resto della rotta in avanti fosse più corto o
portasse fuori dalla zona delle minacce (decisione dell'utente: ritroso), e solo dopo un episodio; lo scheduler rieseguito
vede lo stato degli asset a `t_r` (un asset distrutto o non più operativo negli episodi già risolti non ha finestre nuove,
mentre le sue finestre del primo scheduling restano); la formazione si può dividere (le decisioni sul carburante sono per
aereo, il rientro forzato per forza); il rientro non evita le minacce dell'andata (il ritroso le ripercorre, in episodi nuovi);
un aereo danneggiato oltre la soglia della F6-B1 resta passivo sulla rotta (nessun rientro per danno); gli aerei di una forza
disingaggiata ancora a terra (non decollati) a `t_r` non sono ri-pianificati; episodi «vuoti» per finestre di aerei già
distrutti (lo scheduler non le tronca).

## 6.21 Interruttori e valori di default

Tutti i comportamenti introdotti dalle fasi F5, F6 e G1-G5 sono dietro **interruttori del modulo**, ciascuno pensato per
attribuire le differenze della fotografia a una sola causa e per fornire una **controprova** negli scenari. Sono
costanti a livello di modulo (nessun parametro di `run_session`): **tutti attivi** nel default, e spegnerli riporta
esattamente il comportamento della fase precedente.

| Interruttore | Modulo | Default | Fase | Effetto se spento |
|---|---|---|---|---|
| `F5_PRESENCE` | `Mission_Adapter` (`:376`) | `True` | F5-B | nessuna presenza prima/dopo: i tratti sono quelli della sola rotta (la storia è quella della F5-A); la postura è riportata comunque |
| `F5_WAITS` | `Mission_Adapter` (`:377`) | `True` | F5-C | nessuna attesa WAIT, ETA bloccate e TOT non sincronizzano; partenza come prima della F5 |
| `F6_FUEL_PER_LEG` | `Session_Simulator` (`:721`) | `True` | F6-A | un solo `FuelEvent` per asset sulla distanza dei tratti di movimento; le soste non consumano |
| `F6_FUEL_CONSTRAINT` | `Session_Simulator` (`:722`) | `True` | F6-A | nessun vincolo: l'asset a secco continua (come prima, esperimento E5) |
| `F6_END_CRITERIA` | `Session_Simulator` (`:733`) | `True` | F6-B1 | i criteri `EndCriteria` non sono letti; stato di missione con la precedenza provvisoria della F6-A |
| `F6_DESTROYED_POSTURE` | `Session_Simulator` (`:734`) | `True` | F6-B1 | un asset distrutto ha la postura di prima (`off_scene`, `Defense`, ...) |
| `F6_BINGO` | `Session_Simulator` (`:744`) | `True` | F6-B2 | nessun bingo: l'aereo vola fino all'esaurimento (F6-A/F6-B1); il validatore a priori non dipende dall'interruttore |
| `F6_BINGO_REVERSE_ROUTE` | `Session_Simulator` (`:754`) | `True` | F6-B2bis | rientro rettilineo con la riserva `BINGO_RESERVE` (F6-B2); **letto solo** con `F6_BINGO` acceso e `F6_BINGO_DISENGAGE_RESERVE` spento |
| `F6_BINGO_DISENGAGE_RESERVE` | `Session_Simulator` (`:765`) | `True` | G2 | la regola 1,2 della F6-B2bis (o la F6-B2); **sostituisce** `F6_BINGO_REVERSE_ROUTE` quando è acceso; letto solo con `F6_BINGO` |
| `G3_ENGAGEMENT_FUEL` | `Session_Simulator` (`:774`) | `True` | G3 | nessun consumo d'ingaggio: la regola della F6-A (tutto il movimento di chi ha combattuto al regime `'max'`); terra e mare non cambiano mai |
| `G4_EPISODES` | `Session_Simulator` (`:783`) | `True` | G4a | l'ingaggio è la componente connessa di forze (§6.3) |
| `G4_REPLAN` | `Session_Simulator` (`:793`) | `True` | G4b | il G4a esattamente: bingo valutato solo alla partenza, esaurimento in ingaggio nel solo contatore; **letto solo** con `G4_EPISODES` (`replanning`, `:2261`) |
| `G4_OFF_SCENE_EXIT` | `Session_Simulator` (`:799`) | `True` | G4b (uscita) | `BINGO_NO_BASE`: l'aereo senza basi resta passivo sulla rotta (il G4b prima dell'uscita di scena); **letto solo** con `G4_REPLAN` |

Costanti non-interruttore che il modulo definisce: `EPISODE_GAP = FM.DISENGAGE_TIME` (`:805`), le etichette
`FUEL_HALT`/`FUEL_GLIDE`/`FUEL_CRASH` (`:808-810`) e i regimi `CRUISE_REGIME`/`COMBAT_REGIME` (`:710-711`).

*Dipendenze fra gli interruttori*: `G4_OFF_SCENE_EXIT` ⊂ `G4_REPLAN` ⊂ `G4_EPISODES`; il bingo dopo l'episodio richiede
anche `F6_BINGO` e `F6_BINGO_DISENGAGE_RESERVE` (l'albero del G2); il consumo d'ingaggio (`G3_ENGAGEMENT_FUEL`) alimenta la
ri-pianificazione (gli aerei «che hanno consumato»). La **controprova** negli scenari: S26 espone una variante per ogni
interruttore del bingo (`switch_off`, `reverse_off`, `reserve_off`, `engagement_fuel_off`, `replan_off`), S27 per i
tre del G3/G4, S5 `episodes_off` e `exit_off` (capitolo 8 §8.10).
