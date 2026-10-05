# Struttura della Missione: le 9 decisioni (D1-D6, N1-N3)

**Stato**: DECISO (2026-10-05), compresa **N3.f = B** (due assi: postura e tipo di missione). Decisioni dell'utente:
- tutte le raccomandazioni **(R)** applicate, **tranne N2.a = C**: un nuovo tipo `MissionWaypoint`
  che contiene un `Waypoint`, giudicato più pulito, manutenibile e leggibile di B;
- N3.a-bis: aggiunto **Supporto** al livello comune;
- `Retrait` → `Retreat`: **eseguito** (codice e test, 11 file; i documenti storici restano invariati).

Nota dell'utente su N3: la definizione di nuove azioni comporta l'aggiornamento delle tabelle di
decisione delle azioni (es. `evaluateGroundTacticalAction` in `Logic/Tactical_Evaluation.py`).
L'analisi di questo punto ha fatto emergere la questione **N3.f**.

Nessun file di codice modificato oltre al rename.
**Fonti**:
- `Analisi_Modello_Missione_Sessione.md` (P1-P7, esperimenti E1-E5): decisioni D1-D6;
- `Analisi_Informazioni_Missione.md` (§11): decisioni N1-N3;
- documento originale dell'utente `Architettura_esecuzione_sessioni_virtuali.txt`: terminologia
  di missione e operazione.

**Convenzioni**:
- **[V]** = verificato sul codice (cito modulo e funzione; le righe dell'analisi del 26/09 possono
  essersi spostate);
- **[I]** = mia ipotesi;
- ogni sotto-questione ha un identificativo (`D1.a`, `N2.b`, ...), così si può rispondere puntualmente;
- la raccomandazione è sempre l'opzione **(R)**.

**Vincolo di fondo** (indicazione dell'utente, 2026-10-05): la struttura è **di dominio**. DCS è solo
uno spunto. Gli adapter verso i simulatori verranno dopo il completamento del DES (mappe, sessioni,
missioni, motore).

---

## 0. Quadro d'insieme e ordine suggerito

| # | Decisione | Sotto-questioni | Blocca |
|---|---|---|---|
| **D3** | Unità della missione e terminologia | 5 | tutto il resto: è la forma dell'entità |
| **N2** | Dove vivono tempi, ruoli e azioni dei waypoint | 4 | la struttura dati della Missione |
| **N3** | Tassonomia dei tipi di missione e dei bersagli | 5 | A4 (filtro armi per missione) |
| **D2** | Criteri di fine missione | 5 | esito di missione, contratto `SessionOutcome` |
| **D1** | Presenza prima della partenza e dopo la fine | 4 | `Contact_Scheduler` |
| **D4** | Durata e sovrapposizione delle sessioni | 5 | pianificatore, validazione |
| **D6** | Turnaround e numero di sortite | 4 | stato di campagna |
| **D5** | Rifornimento durante la missione | 3 | `Fuel_Model`, contratto |
| **N1** | Esecuzione degli attacchi nell'adapter DCS | 1 | nulla ora (adapter) |

L'ordine suggerito è quello della tabella: le prime tre definiscono **com'è fatta** una Missione, le
altre **come vive** nel tempo. Si può rispondere anche a gruppi.

Lo stato di partenza in una riga [V]: oggi la Missione non esiste. Il motore riceve, fuori dalla
porta `SessionOrder`, tre mappe per asset (`routes`, `starts`, `speeds`, argomenti di
`Session_Simulator.run_session`). La fine di una missione è solo geometrica (ultimo waypoint).
L'unità di ingaggio è la forza, cioè il blocco `Military`.

---

## D3. Unità della missione e terminologia

**Contesto.** Il tuo documento originale definisce già i termini:
- **missione** = azioni di attacco, trasporto o posizionamento svolte da *"un determinato tipo e
  numero di asset appartenenti ad uno specifico blocco"*, con obiettivo un blocco o una zona; in ogni
  missione *"sono definiti gli asset utilizzati, il ruolo ad essi assegnato, le direttive di missione
  (ROE, ..) e un percorso (Route)"*;
- **operazione** = insieme di missioni di asset di **blocchi diversi** per uno stesso scopo.

In `Analisi_Informazioni_Missione.md` §1 avevo proposto "Missione = pacchetto ⊃ Elemento": la tua
terminologia lo dice meglio. In DCS, la tua missione corrisponde a un **gruppo** e la tua operazione
al **pack** di DCE.

**Oggi nel motore** [V]:
- `Engagement_Resolver` lavora per **forza** (un `Military`): disingaggio (`DISENGAGED`),
  `committed` (sottoinsieme impegnato) e intercettazione di salva sono per forza;
- ogni asset ha la **propria** rotta (`routes` è `{asset_id: Route}`): non esiste una rotta di
  gruppo.

### D3.a Terminologia
- **A (R)**: adottare la tua: **Operazione ⊃ Missione**. La Missione è svolta da asset di un solo
  blocco, ha un obiettivo e una rotta di riferimento. L'Operazione è facoltativa: una missione
  isolata non ha bisogno di un'operazione.
- **B**: Missione (pacchetto) ⊃ Elemento, come nella mia sintesi.

Scelgo A perché è già la lingua del progetto. La sintesi va corretta di conseguenza.

### D3.b Una missione, quante rotte?
Il documento originale dice "un percorso". Nella realtà gli asset di una missione volano o marciano
**insieme** sulla stessa rotta, con offset di formazione.
- **A (R)**: **una rotta di riferimento per missione**, con un offset di formazione per asset (o
  nessuno). Il motore ricava la rotta di ogni asset dalla rotta di missione. `routes` per asset
  resta l'interfaccia interna del DES, popolata dalla Missione.
- **B**: una rotta per asset dentro la missione. È più flessibile, ma ricrea il problema di oggi:
  nessuna nozione di "gruppo".

### D3.c Ruoli degli asset
"Il ruolo ad essi assegnato." Esempi: in un volo, capo formazione e gregari; in una missione dello
stesso blocco, attacco e soppressione SEAD; in una colonna, testa, grosso e retroguardia.
- **A (R)**: un **ruolo per asset** dentro la missione, da un elenco chiuso per dominio. Il ruolo
  sceglie le azioni e le armi che l'asset usa (lega A4).
- **B**: nessun ruolo; tutti gli asset della missione fanno la stessa cosa. Se servono compiti
  diversi, si fanno missioni diverse coordinate da un'Operazione.

### D3.d Fine e aborto: per asset o per missione?
- **A (R)**: **per missione**, con eccezioni individuali. La missione finisce o abortisce come
  gruppo: la coppia rientra insieme, come vuole la dottrina [I]. L'asset distrutto o in "mission
  kill" esce individualmente.
- **B**: per asset. Ognuno finisce quando finisce la sua rotta (è il comportamento di oggi).

### D3.e Disingaggio e `committed`: per forza o per missione?
Problema P6: due missioni dello stesso blocco nella stessa sessione (es. 2 CAP e 4 Strike dello
stesso stormo) oggi condividono l'esito `DISENGAGED`.
- **A (R)**: **la missione diventa l'unità di ingaggio** del risolutore. Ogni missione è vista come
  una "forza" a sé, con id = `mission_id`. Il blocco resta l'unità di appartenenza, rifornimento e
  comando. Costo: costruire nel resolver una vista "forza" per missione invece di passare il
  `Military` [I: da verificare quanto il resolver dipenda dal tipo `Military`].
- **B**: resta per blocco. Si accetta che un blocco abbia **al più una missione per sessione**. È
  semplice, ma limita molto il pianificatore.
- **C**: per blocco, ma il disingaggio di una missione non trascina le altre. È una variante di A più
  complicata da giustificare.

**Impatto**:
- `SessionOrder` trasporta le missioni e non più `force_ids`/`committed` sciolti;
- `Engagement_Resolver` (forze → missioni);
- la sintesi `Analisi_Informazioni_Missione.md` §1 va corretta.

---

## N2. Dove vivono tempi, ruoli e azioni dei waypoint

**Contesto** [V]:
- `DataType.Waypoint` ha solo `point`, `name` e `reference` (asset);
- `DataType.Edge` ha `path_type` (`onroad`/`offroad`/`air`/`water`), `speed` e `danger_level`;
- non ci sono tempi, né ruolo del punto (decollo, IP, attacco, atterraggio...), né azioni;
- `Command/Attack_Types.AttackProfile` è dichiarato *"attributo della futura `Mission`, non della
  rotta"*.

Da DCS [T, M]: ogni waypoint porta ETA, velocità del tratto, tipo di quota, ruolo e una **lista
ordinata di azioni** (compiti, regole, comandi) con condizioni. I compiti partono all'arrivo al
waypoint (posizione e istante di tiro).

### N2.a Dove mettere tempi, ruoli e azioni
- **A**: estendere `DataType.Waypoint` con ETA, ruolo, tipo di quota e azioni. È semplice, ma lega la
  geometria alla missione: la stessa rotta non è più riusabile e i pianificatori di rotta (Ground e
  Air Route Manager) dovrebbero conoscere le missioni.
- **B (R)**: la **Rotta resta geometrica** (`DataType.Route`, come oggi). La Missione porta un
  **piano** parallelo: per ogni waypoint ruolo, ETA pianificata, velocità del tratto, tipo di quota
  e azioni. È la stessa scelta già fatta per `AttackProfile`.
- **C**: un nuovo tipo `MissionWaypoint` che *contiene* un `Waypoint`. Equivale a B con un livello di
  oggetti in più.

### N2.b ETA: dato pianificato o calcolato?
- **A (R)**: **entrambi**. La Missione porta l'**ETA pianificata** (o il TOT sull'obiettivo, da cui
  si ricavano gli altri istanti a ritroso); il DES calcola l'**ETA effettiva** e la riporta
  nell'esito. Come in DCS: almeno un istante "bloccato" (partenza o TOT), gli altri derivati da
  distanza e velocità.
- **B**: solo la partenza più le velocità (com'è oggi), con le ETA sempre derivate.

### N2.c Attese e soste sulla rotta
Oggi una rotta non può contenere soste: il tempo di un arco è solo lunghezza / velocità, e un'orbita
si può rappresentare solo come circuito geometrico [V].
- **A (R)**: un'azione "**attendi**" su un waypoint, con durata o "fino all'istante t" (orbita,
  sosta, schieramento in attesa). Serve a sincronizzare le missioni di un'Operazione (TOT comune),
  alla CAP (tempo sulla stazione) e a terra (Hold).
- **B**: nessuna attesa; la sincronizzazione si ottiene solo regolando le velocità.

### N2.d Condizioni delle azioni
DCS ammette condizioni di avvio e di arresto: tempo, flag, probabilità, durata, ultimo waypoint.
- **A (R)**: nella prima versione **solo condizioni calcolabili prima della sessione**: istante,
  durata, arrivo a un waypoint. Le condizioni sullo stato (evento avvenuto, bersaglio distrutto)
  vengono con il re-scheduling (lega D2).
- **B**: nessuna condizione; le azioni partono sempre all'arrivo al waypoint.
- **C**: condizioni complete subito (richiede il re-scheduling, R4 seconda parte).

---

## N3. Tassonomia dei tipi di missione e dei bersagli

**Contesto** [V]:
- in `Context/Context.py`:
  - `Air_To_Air_Task` = CAP, Fighter_Sweep, Intercept, Escort, Recon;
  - `Air_To_Ground_Task` = CAS, Strike, Pinpoint_Strike, SEAD, Anti_Ship;
  - `Ground_Action` = Attack, Defense, Maintain, Retrait;
  - `Sea_Task` = Attack, Defense, Retrait;
- il tuo documento: azioni di **attacco, trasporto e posizionamento**, con obiettivo un blocco o una
  zona;
- DCS ha 16 tipi aerei; per terra e mare nessun tipo significativo (`Ground Nothing`) [T].

### N3.a Livello superiore comune ai tre domini
- **A (R)**: un livello superiore **Attacco / Trasporto / Posizionamento**, dal tuo documento,
  comune a tutti i domini. Sotto, i tipi specifici per dominio. Il livello superiore decide la forma
  dell'obiettivo (blocco nemico, blocco amico, zona) e i criteri di fine di default.
- **B**: solo tipi per dominio, come oggi.

Nota: il "posizionamento" copre difesa, presidio e schieramento. Il supporto (AWACS, Tanker,
ricognizione) potrebbe essere un quarto valore, **Supporto**, oppure rientrare nel posizionamento
(stazionare in una zona). **Domanda N3.a-bis**: aggiungere "Supporto" o no? Lo consiglio, perché il
supporto non ha bersaglio né si schiera per difendere.

### N3.b Tipi aerei da aggiungere
I candidati vengono da DCS e DCE; i 10 tipi esistenti restano:
- **AWACS** (supporto: sensore e coordinamento);
- **Tanker** (supporto; prerequisito di D5);
- **Transport** (trasporto: risorse, truppe);
- **AFAC/FAC** (designazione bersagli per la CAS);
- **Runway_Attack** (attacco alle piste);
- **Interdiction** [I] (attacco alle colonne in movimento dietro il fronte).

La **(R)** è aggiungere **AWACS, Tanker e Transport** subito: senza di essi non si rappresentano
supporto e logistica aerea. Runway_Attack, AFAC e Interdiction sono da valutare: Runway_Attack può
restare uno Strike con bersaglio "pista".

### N3.c Tipi terrestri e navali da aggiungere
Proposta [I]:
- **terra**: Attack, Defense, Maintain e Retrait restano. Si aggiungono **Fire_Support** (fuoco
  indiretto, verificato in [T]), **Movement** (trasferimento senza contatto previsto), **Recon** e
  **Supply** (colonna logistica: è il "trasporto" del tuo documento);
- **mare**: Attack, Defense e Retrait restano. Si aggiungono **Patrol**, **Escort** (scorta a
  convoglio), **Shore_Bombardment** (fuoco contro terra, verificato in [T]) e **Transport/Supply**.

**Domanda a margine**: correggere `Retrait` in `Retreat` (refuso dell'inglese) mentre si
interviene? È un rename su più file e va deciso esplicitamente.

### N3.d Bersaglio: forme ammesse
Dalla missione di prova [T]:
- **A (R)**: tre forme comuni ai tre domini:
  - **asset o gruppo nemico** (bersaglio mobile, inseguito);
  - **punto/area** (posizione con raggio, fissa);
  - **zona** (per posizionamento, pattugliamento, ricerca e ingaggio).

  Più "**nessun bersaglio**": ingaggia ciò che entra in portata secondo le regole.
- **B**: solo asset o gruppo, come oggi (Fire_Control sceglie fra i nemici rilevati).

### N3.e Conoscenza su cui si basa il bersaglio
In [T] l'artiglieria rossa colpisce il punto dove i blu **erano**. Un bersaglio scelto in
pianificazione usa l'informazione disponibile in quel momento (nebbia di guerra C).
- **A (R)**: la Missione registra la **provenienza del bersaglio**:
  - asset identificato (id), con l'istante dell'ultima osservazione;
  - oppure posizione stimata, con istante e incertezza.

  Il DES usa la **posizione stimata** per i bersagli di posizione e non "sa" dove sia davvero il
  nemico.
- **B**: il bersaglio è sempre l'asset reale. È semplice, ma annulla la nebbia di guerra nella
  pianificazione.

**Legame con A4**: il filtro armi per missione deriva da tipo di missione + ruolo (D3.c) + forma
del bersaglio. È questo che sostituirà il filtro di test `ifv_only` di S19.

### N3.f Posture tattiche e tipi di missione: un asse o due? (DECISO: B)

**Cosa ho trovato** verificando le tabelle di decisione [V]:

1. `evaluateGroundTacticalAction` (`Logic/Tactical_Evaluation.py`) è un controllore fuzzy. L'output
   è un valore in [0, 1] diviso da `automf` in quattro etichette **ordinate per aggressività**:
   RETREAT < DEFENSE < MAINTAIN < ATTACK. Le 21 regole spostano il valore lungo quell'asse a
   seconda di quattro grandezze: superiorità terrestre `gs`, rapporto delle perdite `flr`, loro
   tendenza `dyn_inc`, sostenibilità `cls`. Funziona solo perché le etichette sono **gradi di una
   stessa scala**.
2. `Ground_Action` e `Sea_Task`, attraverso `Context.ACTION_TASKS`, non alimentano solo quel
   controllore. Sono le **chiavi** di:
   - la combat power per azione di ogni asset (`Mobile`, `Vehicle.set_combat_power`,
     `Ship.set_combat_power`, `Military`);
   - le tabelle di efficacia `GROUND_COMBAT_EFFICACY` e `SEA_COMBAT_EFFICACY` (`Context.py`);
   - le tabelle di `Actual_Context`;
   - il vettore di priorità di `Region` (Attack/Defense/Maintain/Retreat);
   - `evaluateCombatSuperiority` ed `evaluateGroundCriticality` (`Tactical_Evaluation`);
   - i registri `Vehicle_Data.VEHICLE_TASK` e `Ship_Data.SHIP_TASK`;
   - una decina di test che verificano gli insiemi esatti.
3. Per gli aerei la situazione è già diversa. `AIR_TASK` (CAP, Strike, SEAD...) è un elenco di **tipi
   di missione**, non di posture: il commento di `AIR_COMBAT_EFFICACY` lo dice esplicitamente (*"per
   gli aerei i task sono ruoli di missione, non posture tattiche mutuamente esclusive"*).
   Aggiungere AWACS, Tanker e Transport ad `AIR_TASK` è coerente. Inoltre 14 loadout in
   `Aircraft_Loadouts` hanno la lista `tasks` vuota: sono probabilmente proprio tanker, AWACS e
   trasporti, che oggi non hanno un task in cui ricadere [I: da verificare in implementazione].

**Il problema.** I nuovi tipi terrestri e navali di N3.c (Fire_Support, Movement, Recon, Supply;
Patrol, Escort, Shore_Bombardment, Transport) **non sono gradi della scala di aggressività**. Fire
Support non sta "fra Defense e Attack": si può fare fuoco di supporto in attacco o in difesa.

**Opzioni**:
- **A**: aggiungerli a `Ground_Action` / `Sea_Task` (un solo asse). Va aggiornato tutto il punto 2:
  - ogni veicolo e ogni nave avrebbero una combat power anche per "Supply" e "Movement" (senza
    significato);
  - le tabelle di efficacia avrebbero righe nuove senza dati;
  - il controllore fuzzy dovrebbe scegliere fra 8 etichette non ordinate, cosa che `automf` su un
    solo asse non può rappresentare: andrebbe riscritto come classificatore.
- **B (R)**: **due assi distinti**.
  - **Postura tattica** (`Ground_Action`, `Sea_Task`), invariata (solo il rename già fatto). Resta
    l'output di `evaluateGroundTacticalAction` e la chiave della combat power.
  - **Tipo di missione** (nuovi enum per dominio, sotto il livello comune Attacco / Trasporto /
    Posizionamento / Supporto). È un attributo della Missione.

  Si collegano con una **nuova tabella di decisione** `tipo di missione → posture ammesse e
  postura di riferimento per la combat power`. Esempi [I]:
  - Fire_Support → Attack o Defense, valutato con la combat power della postura;
  - Movement → Maintain;
  - Supply e Recon → nessuna postura offensiva, combat power di autodifesa (Defense);
  - Patrol → Defense; Shore_Bombardment → Attack.

  La scelta del tipo di missione diventa un **secondo stadio** dopo la postura: data la postura
  decisa dal controllore e gli asset disponibili (es. artiglieria presente → Fire_Support possibile),
  il pianificatore sceglie i tipi di missione compatibili. Il secondo stadio va progettato a parte,
  quando si costruirà il pianificatore. Fino ad allora la tabella di compatibilità è un dato in
  `Context`.
- **C**: come B, ma senza tabella di collegamento. Ogni tipo di missione dichiara da sé la postura
  da usare. Più semplice, ma la logica si disperde nei tipi.

**Impatto di B**:
- `Context.py`: nuovi enum dei tipi di missione e tabella di compatibilità; `AIR_TASK` + AWACS,
  Tanker, Transport;
- `Ground_Action`, `Sea_Task`, `ACTION_TASKS`, combat power, tabelle di efficacia e controllore fuzzy
  restano invariati;
- per gli aerei: verificare l'effetto dei tre nuovi task su `Aircraft_Data` (punteggio per task del
  miglior loadout), `Air_Resources_Assigner` e la combat power aggregata dell'aereo, e assegnare i
  task ai loadout oggi senza task.

---

## D2. Criteri di fine missione

**Contesto** [V]:
- la fine è solo geometrica (ultimo waypoint della rotta);
- l'asset continua finché la rotta è in corso, è operativo, la sua forza non ha rotto il contatto e
  ha munizioni. Con munizioni a zero non spara, ma resta bersaglio e continua la rotta;
- le finestre di contatto sono calcolate **una volta, prima** della risoluzione
  (`Contact_Scheduler.schedule_contacts`); il re-scheduling è rimandato (R4 seconda parte,
  `Engagement_Resolver`, docstring);
- il carburante è contabilizzato **a posteriori** e **in distanza** (`Fuel_Model.FuelEvent`, un
  evento per asset a fine rotta): un asset a secco continua a muoversi (E5).

Da DCS [M, F, Z]: Land / ultimo waypoint; durata (`DUR`, `stopCondition.time`); "RTB on Bingo"
(default ON); "RTB on out of ammo" per categoria d'arma; "Allow Abort Mission" (aborto per minaccia);
condizioni su flag.

### D2.a Criteri ammessi nella prima versione
I criteri si dividono in due famiglie:
- **pre-calcolabili** (decisi prima della sessione): ultimo waypoint, cioè rientro e atterraggio
  inclusi; durata o tempo sulla stazione; **bingo calcolato a priori** sulla rotta pianificata
  (la rotta si accorcia o si nega in pianificazione);
- **di stato** (decisi durante la sessione): winchester, bersaglio distrutto, aborto per danni,
  aborto per minaccia, perdita del tanker.

Opzioni:
- **A**: solo i pre-calcolabili.
- **B (R)**: i pre-calcolabili **più una "fine di attività" senza cambio di rotta** per i criteri di
  stato. Al winchester, a bersaglio distrutto o a danno oltre soglia l'asset smette di ingaggiare
  (diventa passivo) ma resta sulla rotta pianificata, che comprende già l'uscita e il rientro. Non
  serve il re-scheduling: il resolver ha già la nozione di asset che non spara più. L'esito registra
  il motivo. Il rientro anticipato vero arriva col re-scheduling.
- **C**: tutti i criteri con rotta modificata subito (implementa R4 seconda parte ora).

### D2.b I criteri di stato sono comunque **dichiarati** nella Missione?
- **A (R)**: sì. La Missione dichiara quali criteri valgono (bingo sì/no, winchester per categoria
  d'arma, aborto per minaccia sì/no, soglia di danno). Il DES li applica come in D2.a; un futuro
  esecutore che li supporta nativamente (come DCS) li applica per intero.
- **B**: no; li fissa la dottrina per tipo di missione.

### D2.c Il rientro (RTB) è sempre parte della rotta pianificata?
Oggi nessuna rotta di scenario include il rientro [V], e il consumo del ritorno non è contabilizzato.
- **A (R)**: sì per le missioni aeree (partenza da una base, arrivo a una base: anche diversa,
  "divert"). Per terra e mare la rotta finisce nella posizione di destinazione (D1).
- **B**: facoltativo, deciso dal pianificatore.

### D2.d Esito di missione
- **A (R)**: un esito **per missione** e un esito **per asset**.
  - Missione: COMPLETATA, ABORTITA (con motivo: minaccia, danni, carburante, munizioni, supporto
    mancato), FALLITA (obiettivo non raggiunto entro la fine), DISTRUTTA (tutti gli asset persi).
  - Asset: operativo, danneggiato, distrutto, più il motivo della propria fine.

  Serve al C2 e a `success_ratio` del morale (D9).
- **B**: solo esiti per asset; quello di missione si ricava dopo.

### D2.e Esito di un'Operazione
- **A (R)**: si ricava dagli esiti delle sue missioni con una regola dichiarata nell'Operazione
  (es. "riuscita se la missione principale è COMPLETATA").
- **B**: rimandato finché non esiste il C2.

**Impatto**: `SessionOutcome` (esiti di missione), `Engagement_Resolver` (fine di attività),
pianificatore (bingo a priori, RTB).

---

## D1. Presenza prima della partenza e dopo la fine

**Contesto** [V]:
- per lo scheduler, un asset con rotta **non esiste** prima della partenza né dopo l'arrivo
  (`Contact_Scheduler.legs_span`, `_asset_legs`). In E1 un carro fermo a 4 km dal nemico "sparisce"
  per 3400 s;
- un asset senza rotta è presente per tutta la sessione (`static_legs`);
- gli asset **non impegnati** di una forza sono esclusi dalla risoluzione (`committed`).

Da DCS [M, Z, T]:
- gli aerei `uncontrolled` stanno sul parcheggio, sono bersagli e partono a comando;
- i gruppi terrestri restano fermi all'ultimo waypoint;
- gli statici esistono sempre (eventualmente distrutti).

### D1.a Dopo la fine della missione
- **A**: sparisce (oggi).
- **B (R)**: **resta presente, fermo, nella posizione finale** fino alla fine della sessione. Diventa
  bersaglio e si comporta secondo una **postura di fine missione**:
  - aereo atterrato: bersaglio passivo, non spara;
  - unità terrestre o navale: difesa secondo ROE e allerta, come un asset senza missione.
- **C**: resta presente ma sempre passivo, anche a terra.

### D1.b Prima della partenza
- **A**: assente (oggi).
- **B (R)**: **presente nella posizione di partenza** dall'inizio della sessione: aereo sul
  parcheggio o in shelter, colonna nell'area di raccolta. Comportamento come in D1.a.

### D1.c Asset non impegnati in alcuna missione
È il caso che decide se un attacco a una base colpisce gli aerei parcheggiati.
- **A**: esclusi (oggi).
- **B (R)**: **presenti come bersagli** nella loro posizione, passivi gli aerei a terra e in postura
  difensiva le unità terrestri e navali. Equivale a una **postura continua** (P7) per tutto ciò che
  non è in missione.
- **C**: presenti solo se nella zona di un'altra missione della sessione. È un'ottimizzazione di B
  che si può fare dopo: lo scheduler scarta già le coppie lontane.

### D1.d Posizione a fine sessione
- **A (R)**: la posizione finale di ogni asset **persiste** nello stato di campagna e la sessione
  successiva parte da lì. Copre il divert, l'avanzata terrestre e il pattugliamento navale (D4.e).
- **B**: ogni asset torna alla posizione iniziale (oggi la posizione non persiste [V]).

**Impatto**:
- `Contact_Scheduler._asset_legs`: tratti fermi prima e dopo la rotta;
- `Engagement_Resolver`: postura passiva;
- `Campaign_State`: posizione persistente.

---

## D4. Durata e sovrapposizione delle sessioni

**Contesto**:
- la durata di una sessione non è mai stata fissata: le fixture usano 3600 s, e "1-2 h" del design
  C2 è lo **scarto** fra sessioni, non la durata [V];
- il design C2 prevede 6 sessioni virtuali fra due sessioni DCS;
- DCE usa 5400 s di missione più 10800-14400 s di tempo morto [Z];
- oggi una missione più lunga della sessione è **tagliata in silenzio** (E4).

### D4.a Le sessioni sono finestre disgiunte dell'orologio di campagna?
- **A (R)**: sì: `[t_start, t_end]` disgiunte, in sequenza. Una sessione DCS ne occupa una come una
  virtuale.
- **B**: possono sovrapporsi (sessioni parallele su teatri diversi). Va escluso che uno stesso asset
  sia in due sessioni sovrapposte.

### D4.b Durata di riferimento
- **A (R)**: **parametro di campagna** con un default (proposta: **2 h**), modificabile per sessione
  dal pianificatore entro un massimo (proposta: 4 h).
- **B**: fissa per tutta la campagna.
- **C**: decisa per ogni sessione come la durata della missione più lunga pianificata.

### D4.c Missioni più lunghe della finestra
- **A (R)**: **rifiutate in pianificazione** (validazione). Il pianificatore accorcia la missione o
  allunga la sessione entro il massimo di D4.b. Nessun taglio silenzioso.
- **B**: spezzate su più sessioni. Contraddice la regola "una missione dentro la sessione".

### D4.d Cosa accade fra due sessioni
- **A (R)**: solo **processi di campagna**, ciascuno con la sua durata: riarmo, rifornimento,
  riparazione (D6), produzione e logistica. **Nessun movimento tattico** fuori sessione: gli
  spostamenti avvengono solo dentro le sessioni.
- **B**: anche movimenti "amministrativi" fuori sessione (es. trasferimenti a grande distanza
  risolti senza contatti).

### D4.e Missioni terrestri e navali più lunghe di una sessione
Un'avanzata di 100 km o un pattugliamento navale di giorni non stanno in 2 h. In DCE le rotte navali
sono stato di campagna (`ShipMissions`) [Z].
- **A (R)**: la regola "una missione dentro la sessione" vale per **tutti** i domini. Le attività
  lunghe diventano una **sequenza di missioni**, una per sessione, legate da un **ordine permanente**
  dell'Operazione o del C2. La continuità è garantita dalla posizione persistente (D1.d).
- **B**: per terra e mare sono ammesse missioni multi-sessione, in deroga alla regola.

---

## D6. Turnaround e numero di sortite

**Contesto** [V]:
- il riarmo e il pieno avvengono all'assegnazione del loadout (`Aircraft.assigned_loadout`) e il
  `Theater_Session_Manager` progettato riarma dopo ogni sessione;
- nessun tempo di turnaround o manutenzione: il numero di sortite al giorno è un **artefatto della
  cadenza delle sessioni**;
- DCE tiene per squadriglia aerei assegnati, disponibili e in manutenzione, con l'istante di rientro
  in servizio (`camp.aircraft_availability`) [Z].

### D6.a Modello di disponibilità
- **A**: solo cadenza delle sessioni (oggi).
- **B (R)**: **disponibilità per asset con istante di "pronto da"**. Al rientro da una missione
  l'asset è indisponibile per un **tempo di turnaround** (riarmo e rifornimento), più un **tempo di
  riparazione** se danneggiato. Il pianificatore vede solo gli asset pronti all'inizio della
  sessione.
- **C**: B più limiti di sortite giornaliere ed effetti di fatica degli equipaggi.

### D6.b Dati di turnaround
I tempi dipendono dal tipo di aereo (caccia leggero vs bombardiere pesante) e dalla base.
- **A (R)**: un tempo per **classe** di velivolo (caccia, attacco, bombardiere, supporto,
  elicottero) in `Context`, ricavato da una ricerca dedicata (agente Sonnet, come per le RWR). Poi
  eventuale raffinamento per tipo.
- **B**: un unico tempo per tutti.

### D6.c Riparazioni
- **A (R)**: tempo di riparazione funzione del danno, perché la salute dell'asset c'è già. Un asset
  in "mission kill" torna disponibile dopo la riparazione, se la base ha le risorse.
- **B**: danneggiato = indisponibile fino a una riparazione decisa a mano dal C2.

### D6.d Si applica anche a terra e mare?
- **A (R)**: sì, con tempi diversi: riorganizzazione e rifornimento di un reparto, rifornimento di
  una nave in porto. Nella prima versione basta un tempo per dominio.
- **B**: solo aerei.

---

## D5. Rifornimento durante la missione

**Contesto** [V]:
- non esiste nessuna forma di rifornimento: `consume_fuel` rifiuta quantità negative;
- il consumo è in distanza, non nel tempo: un asset che orbita o è fermo non consuma;
- i dati del fornitore ci sono (pod tanker e carburante cedibile in `Aircraft_Loadouts`), quelli
  del ricevente no.

Da DCS e DCE: il tanker è un gruppo con task `Tanker`; il ricevente ha un compito `Refueling` (va al
tanker più vicino, rifornisce e riprende la rotta). A terra: veicolo di rifornimento entro 200 m. In
mare: rifornimento in navigazione [M, Z].

### D5.a Rifornimento in volo
- **A (R)**: **ora solo come vincolo di pianificazione**. Le missioni sono pianificate entro
  l'autonomia senza rifornimento. Le missioni Tanker esistono (N3.b) e sono bersagli, ma il
  travaso non è simulato. Il rifornimento vero arriva con il re-scheduling, perché la perdita del
  tanker deve poter abortire la missione ricevente.
- **B**: modellarlo ora: `RefuelEvent` nel contratto, `FuelEvent` per tratto, tanker come dipendenza
  fra missioni, capacità di ricevere per tipo di aereo.

### D5.b Consumo nel tempo (indipendente dal rifornimento)
Senza questo, una CAP in orbita o un'attesa (N2.c) non consumano.
- **A (R)**: **sì**: consumo per tratto in movimento (distanza) e per attesa (tempo, a regime di
  crociera o di attesa). È prerequisito del bingo a priori (D2.a) e del tempo sulla stazione.
- **B**: resta solo in distanza.

### D5.c Rifornimento terrestre e navale in missione
- **A (R)**: escluso dalla prima versione. Il rifornimento avviene fra sessioni (D4.d, D6). Le
  colonne logistiche sono missioni Supply (N3.c) con effetto a fine sessione.
- **B**: veicoli o navi di rifornimento che ricaricano gli asset vicini durante la sessione, come la
  regola DCS dei 200 m.

---

## N1. Esecuzione degli attacchi nell'adapter DCS

**Contesto**: DCE disabilita 587 task di attacco nativi su 590 e usa funzioni Lua
(`CustomGroupAttack`, `OrbitPosition`...) per controllare quota e tipo di attacco [Z].

### N1.a Decidere ora?
- **A (R)**: **no, rimandata all'adapter** (dopo il DES, come da tua indicazione). Ora vale solo un
  vincolo sul nucleo: la Missione deve contenere **tutto** ciò che serve a entrambe le strade, cioè
  identità del bersaglio, arma o categoria, quantità, direzione e quota d'attacco (`AttackProfile`),
  attese (N2.c) e criteri di fine dichiarati (D2.b).
- **B**: decidere ora tra task nativi e script.

---

## Riepilogo delle decisioni (raccomandazioni applicate salvo dove indicato)

| Id | Raccomandazione in breve |
|---|---|
| D3.a | Operazione ⊃ Missione (terminologia dell'utente); operazione facoltativa |
| D3.b | Una rotta di riferimento per missione, offset di formazione per asset |
| D3.c | Ruolo per asset, da elenco chiuso per dominio |
| D3.d | Fine e aborto per missione, con eccezioni individuali (distrutto, mission kill) |
| D3.e | La missione è l'unità di ingaggio del risolutore; il blocco resta unità di appartenenza |
| N2.a | **DECISO C**: tipo `MissionWaypoint` che contiene un `Waypoint`; la Rotta resta geometrica |
| N2.b | ETA pianificata nella missione, ETA effettiva nell'esito |
| N2.c | Azione "attendi" (durata o fino a t) |
| N2.d | Solo condizioni pre-calcolabili nella prima versione |
| N3.a | Livello comune Attacco / Trasporto / Posizionamento / Supporto |
| N3.b | Aggiungere AWACS, Tanker, Transport |
| N3.c | Terra: + Fire_Support, Movement, Recon, Supply; mare: + Patrol, Escort, Shore_Bombardment, Transport; rename `Retrait` → `Retreat` FATTO |
| N3.f | **DECISO B**: due assi, postura tattica (invariata) e tipo di missione, con tabella di compatibilità |
| N3.d | Bersaglio: asset/gruppo, punto/area, zona, nessuno |
| N3.e | Provenienza del bersaglio (osservato con istante, o stimato) |
| D2.a | Criteri pre-calcolabili + "fine di attività" senza cambio di rotta per quelli di stato |
| D2.b | Criteri di stato dichiarati nella Missione |
| D2.c | Rientro sempre nella rotta aerea |
| D2.d | Esito per missione (COMPLETATA/ABORTITA+motivo/FALLITA/DISTRUTTA) e per asset |
| D2.e | Esito dell'Operazione da regola dichiarata |
| D1.a-b | Presente fermo prima della partenza e dopo la fine, con postura di fine missione |
| D1.c | Asset non impegnati presenti come bersagli (postura continua) |
| D1.d | Posizione persistente fra sessioni |
| D4.a | Sessioni disgiunte |
| D4.b | Durata parametro di campagna (default 2 h, massimo 4 h) |
| D4.c | Missioni troppo lunghe rifiutate in pianificazione |
| D4.d | Fra sessioni solo processi di campagna, nessun movimento tattico |
| D4.e | Attività lunghe come sequenza di missioni con ordine permanente |
| D6.a | Disponibilità "pronto da t" con turnaround e riparazione |
| D6.b | Tempi per classe di velivolo da ricerca dedicata |
| D6.c | Riparazione funzione del danno |
| D6.d | Anche terra e mare, un tempo per dominio |
| D5.a | Rifornimento in volo solo come vincolo di pianificazione; Tanker come missione bersaglio |
| D5.b | Consumo anche nel tempo (attese, orbite) |
| D5.c | Rifornimento terrestre e navale solo fra sessioni |
| N1.a | Rimandata all'adapter; la Missione porta tutti i dati necessari |
