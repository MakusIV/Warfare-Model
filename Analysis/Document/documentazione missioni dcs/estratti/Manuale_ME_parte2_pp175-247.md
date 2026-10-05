# DCS User Manual (2020) - Mission Editor, parte 2 (pp. 175-247)

Fonte: `DCS_User_Manual_EN_2020.pdf`, numeri di pagina del PDF. Termini DCS lasciati in inglese. Dove un valore non e' riportato nel manuale lo si scrive esplicitamente ("non indicato"). Le schermate sono state lette (render a 90 dpi) per le pagine chiave (179, 190, 197, 201, 214, 217, 237, 241, 247); le tabelle di esempio dei lock speed/ETA (pp. 180-187) sono immagini non riproducibili in testo: il contenuto e' ricavato dal testo che le accompagna.

---

## 1. Task Planning for Unit Groups - concetti fondamentali (pp. 175-178)

Due approcci (p. 175): **Simple** (si piazzano gruppi e rotte, le azioni vengono generate automaticamente; l'AI muove lungo la rotta e ingaggia appena il nemico e' nel raggio di ingaggio, che varia con tipo unita' e task) e **Advanced** (Advanced Actions Panel del Group Properties per controllo manuale: p.es. attaccare solo certi tipi di bersaglio in aree diverse, restrizioni sulle armi).

Tipologie di azione (pp. 175-177):

| Tipo | Natura | Durata / stop | Priorita' | Note |
|---|---|---|---|---|
| **Perform Task** | azione di combattimento/targeting/manovra, eseguita nel tempo | stop automatico da AI (bersaglio distrutto, armi esaurite, non eseguibile) oppure da stop condition del designer | la piu' alta; un solo Task alla volta, in ordine di lista o priority | Tipicamente l'azione primaria del waypoint (p. 176) |
| **Start Enroute Task** | azione "Search for...": cerca e attacca solo se rileva il bersaglio; puo' eseguirsi piu' volte e in piu' luoghi | solo stop condition del designer, altrimenti attivo per tutta la "vita" dell'AI | sempre inferiore a un Task (salvo diversa impostazione manuale); piu' enroute attivi insieme ma uno solo eseguito alla volta, scelto per order/priority | Sospeso quando parte un Task, riattivato alla fine (p. 177, 212) |
| **Perform Command** | azione istantanea (p.es. Set Frequency) | eseguita subito all'attivazione | segue ordine/priority | Ha condizioni di start (p. 177) |
| **Set Option** | regola/limitazione per il gruppo, formato `<variabile>=<valore>` (es. `Formation=Trail`, `Radar Use=Never` per intercettazione radar-silent) | per tutta la missione, salvo start/stop a waypoint specifici | istantanea, segue ordine/priority | p. 177 |

Altri punti:
- **Group AI** (p. 176): oggetto virtuale rappresentato dal lead unit; le azioni sono impostate per **l'intero gruppo**, mai per singola unita'. Le azioni di un waypoint scattano quando il **leader** raggiunge il waypoint; sono eseguite in sequenza per ordine e/o **priority** (intero, 0 = massima).
- Le azioni possono essere legate ai waypoint oppure indipendenti dalla rotta tramite l'azione **AI Task** del Trigger Menu (eseguite quando le regole del trigger sono vere) (p. 177).
- Tutte le azioni hanno condizioni di start/stop: mission time, durata, stato flag (on/off), probabilita' di attivazione, codice Lua (p. 175).
- **Panel Flags** (p. 177): checkbox "lock" nel Group Properties (es. speed lock); non vanno confusi con i FLAG ON/OFF del Trigger Menu.
- Flusso di creazione mission (p. 178): creare gruppi, piazzare rotte, impostare task principale (aerei), configurare azioni avanzate, creare trigger per azioni aggiuntive.

---

## 2. Group Route Planning (pp. 179-189)

### 2.1 Speed / ETA e lock (p. 179)
Per ogni waypoint si impostano **SPEED** e **ETA**. Ciascuno puo' essere "locked" (fissato dall'utente) con la checkbox; l'altro viene calcolato dal Mission Editor usando la distanza tra waypoint consecutivi. La velocita' di un waypoint e' la velocita' **del tratto che arriva a quel waypoint** (quella assunta dopo aver passato il precedente) (p. 180). La coalizione Red usa designazioni **SP** (Starting Point), **WP n**, **DP** (Destination Point); la coalizione Blue ha tutti i WP a zero di default (p. 179-180). Schermata p. 179: pannello waypoint con campi WAYPOINT n/N, TYPE, ALTITUDE (m, MSL/AGL), SPEED (km/h) + checkbox GS, MACH, ETA (h:m:s/giorno) + "Fix time".

Regola: ogni rotta deve avere **almeno un waypoint con ETA locked** (riferimento temporale), che puo' essere il primo (ora di partenza gruppo) o uno successivo (p. 189). Per sbloccare sia speed sia ETA di un waypoint serve almeno un waypoint precedente e uno successivo con ETA locked (p. 181).

### 2.2 Esempi (rotta di 4 waypoint WP0..WP3; T = ETA, V = speed)

| Esempio | Pagine | Lock dell'utente | Calcolato dal ME | Insegnamento |
|---|---|---|---|---|
| 1 | 180-181 | T0 (start) e T3 (ETA finale) | velocita' media per arrivare a T3; ETA di WP1, WP2; V3 | L'AI regola la speed su WP1-3 per arrivare a T3 in tempo. Sbloccando T0 o T3 la rotta e' invalida (nessun riferimento temporale) |
| 2 | 181-182 | T0 e V0..V3 (speed di ogni waypoint) | ETA di WP1, WP2, WP3 dalle distanze | Tempo di percorrenza emergente dalla velocita' |
| 3 | 182-184 | T0, T1, T2, T3 (tutte le ETA) | V di ogni tratto | L'AI cerca di rispettare ogni ETA variando la speed per tratto |
| 4 | 184-185 | T0, V1, V3, T2 | ETA di WP1 e WP3, V2 | Mix di vincoli valido |
| 5 | 185-186 | T0, T3, V1, V3 | ETA di WP1/WP2, V2 | Valido perche' WP2 ha speed e ETA entrambi sbloccati e assorbe il vincolo |
| 6 | 187 | T3 (ETA finale) e V1..V3 | **ora di partenza T0** (ETA di WP0) | Si puo' fissare l'arrivo e ricavare l'ora di start all'indietro |

Il manuale dice che le combinazioni valide su 4 WP sono 6 (p. 179), mostrate negli esempi. Cosa insegnano sulla struttura rotta+task: la rotta e' una sequenza di waypoint con tre variabili legate (posizione/distanza, speed, tempo); due su tre determinano la terza per tratto; serve sempre un'ancora temporale; la validita' e' una proprieta' globale della rotta.

### 2.3 Errori e hint (pp. 188-189)
- Speed o ETA fuori dal range dell'unita' (es. speed sotto la minima di volo): campo in **rosso** ("invalid value warning"); messaggio alla chiusura del pannello o al salvataggio; si corregge inserendo un valore valido.
- Combinazione di lock non valida (es. speed locked ovunque + ETA locked su primo e ultimo): checkbox incorniciate in rosso ("invalid flag warning").
- Il ME non impedisce nessuna combinazione, segnala soltanto. Hint: usare il waypoint edit panel (frecce) per ciclare tra i waypoint, evitando messaggi ripetuti.

---

## 3. Place Airplane and Helicopter Group (pp. 190-210)

Gruppi di **1-4 unita'** (aerei o elicotteri; stessa interfaccia, p. 190). Copia/incolla gruppo con CTRL+C / CTRL+V (proprieta' identiche).

### 3.1 Pannello del gruppo (pp. 190-194)

| Campo | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| NAME | stringa; deve essere unica | nome generato automaticamente | Usato nei Trigger (es. Group Dead). Non duplicare (p. 191) |
| CONDITION | espressione Lua per lo spawn casuale del gruppo; accanto un campo percentuale (screenshot p. 190: "%" con valore 100) | vuoto / 100 | Lo script di inizializzazione va caricato nel trigger panel prima; eseguito prima del caricamento missione (p. 191). Il campo % accanto a CONDITION e' un contatore con default 100 (da figura, p. 190); significato non spiegato nel testo |
| COUNTRY | paesi assegnati a RED/BLUE alla creazione della missione | n.d. | Filtra i TYPE disponibili (p. 191) |
| TASK | Nothing, AFAC, Anti-ship Strike, AWACS, CAP, CAS, Escort, Fighter Sweep, Ground Attack, Intercept, Pinpoint Strike, Reconnaissance, Refueling, Runway Attack, SEAD, Transport | n.d. | Vedi 3.2. Vale per tutta la missione; **filtra** azioni avanzate e payload di default (pp. 191-193) |
| UNIT (2 campi) | sinistro: seleziona unita' del gruppo; destro: numero totale unita' 1-4 | 1 di 1 (non indicato esplicitamente) | Frecce sinistra/destra (p. 193). Screenshot p. 190: "1 OF 4" |
| TYPE | elenco aerei filtrato da Country e Task | n.d. | p. 193 |
| SKILL | AI: Average, Good, High, Excellent, Random (a caso fra i quattro). Non-AI: **Client** (umano in multiplayer), **Player** (umano in single-player) | n.d. | Skill influenza G sostenibili, portata di attacco, precisione di rilascio (p. 193), portate di rilevamento, tempi di reazione, errori di puntamento (p. 194). Non usare Player in multiplayer |
| PILOT | stringa, per ogni unita' | nome generato | Usato per le condizioni di Trigger (p. 194) |
| TAIL # | numero a 2 o 3 cifre | n.d. | Scritto sul velivolo (p. 194) |
| COMM | frequenza in MHz + modulazione (es. 124 MHz AM); checkbox accanto al campo | n.d. (screenshot: 124 MHz AM, campo inattivo se non spuntato) | Frequenza di comunicazione del gruppo AI (p. 194) |
| CALLSIGN | stringa; per aerei russi numero a tre cifre; screenshot: nome (es. "Springfield") + due numeri | n.d. | Usato nelle comunicazioni con flight, AWACS, controllori (p. 194) |
| HIDDEN ON MAP | checkbox | off | Nasconde il gruppo da mappa ME, briefing e F10; vedibili dalla Units List (p. 194) |
| UNCONTROLLED | checkbox | off | Con start "Takeoff from Ramp" (cold): il gruppo appare parcheggiato e non avvia lo spool-up finche' un trigger AI TASK non esegue il comando START (p. 194) |
| HIDDEN ON PLANNER | checkbox | off | Nasconde dall'mission planner (p. 194) |
| LATE ACTIVATION | checkbox | off | Il gruppo viene generato dopo una certa condizione/evento (p. 194); l'attivazione avviene da trigger |

Modal buttons in basso (pp. 194-195): AI groups = route, payload, triggered actions, route summary; aerei del giocatore in piu' = INU fix point, navigation target points, failures, waypoint properties, radio presets. Dal testo p. 190 appare anche, sotto il pannello waypoint, il tasto **ADVANCED (WAYPOINT ACTIONS)**.

### 3.2 Significato dei TASK di gruppo (pp. 191-193)

| Task | Descrizione (manuale) |
|---|---|
| Nothing | Volo non combattivo lungo la rotta; non partecipa ad azioni attive; sotto minaccia tenta di evadere |
| AFAC | Airborne FAC: marca bersagli con razzi fumogeni o flare illuminanti; utile di notte a supporto di CAS di un giocatore |
| Anti-ship Strike | Attacca navi con missili antinave |
| AWACS | Rotta rettilinea o circolare con waypoint in loop; avvisa velivoli alleati, SAM e navi quando rileva aerei nemici; alcuni SAM ricevono dati di tiro da AWACS anche con radar di acquisizione distrutti; rilevamento limitato da portata, quota molto bassa, mascheramento del terreno |
| CAP | Race-track ampio con waypoint in loop per difendere un'area; non cerca bersagli a terra ne' devia molto per intercettare. CAP alta facilita il volo a bassa quota nemico; sandwich alta/bassa e' il piu' bilanciato; il fattore limite e' il carburante. Salvo disabilitazione manuale, tutti gli aerei AI interrompono il pattugliamento e rientrano alla base appena il carburante scende al minimo garantito per il ritorno (**Bingo fuel**) |
| CAS | Ricerca attiva e distruzione di bersagli a terra in supporto a truppe amiche; adatto ad attack e elicotteri |
| Escort | Per caccia ed elicotteri d'attacco: scorta trasporti, bombardieri o attack e li difende da aerei e difese aeree; non deve ingaggiare minacce irrilevanti o troppo lontane dalla rotta |
| Fighter Sweep | Penetra nello spazio aereo nemico per attaccare caccia o altri aerei, ottiene superiorita' aerea; carburante cruciale |
| Ground Attack | Attacco a bersagli a terra con armi aria-superficie (tipicamente bombe non guidate 500-20000 lb e razzi). Salvo opzioni avanzate l'AI privilegia armi a lunga portata (missili guidati) su quelle corte (razzi, cannone) |
| Intercept | Difensivo; ricerca attiva di aerei in arrivo e/o dati da radar a terra o in volo; per difesa su larga scala e pattugliamento attivo, non per aree piccole (puo' deviare molto dalla rotta) |
| Pinpoint Strike | Rilevamento e attacco di bersagli di superficie con armi a guida di precisione |
| Reconnaissance | Sorvola direttamente il waypoint di ricognizione per acquisire intelligence |
| Refueling | Riservato ai tanker; rifornisce alleati in volo |
| Runway Attack | Attacco al suolo specializzato: allinea l'asse di attacco con la pista; utile con armi da runway denial. Si imposta la Targeting area sull'aeroporto e la categoria Airfields |
| SEAD | Come CAS ma contro difese aeree, con missili anti-radiazione o altre armi |
| Transport | Come Nothing: volo non combattivo, evasione sotto minaccia |

**Importante (p. 221)**: il task di gruppo **non influenza di per se' il comportamento in gioco**; serve a filtrare le azioni disponibili e i payload. Il comportamento e' determinato dalle azioni, incluse quelle generate automaticamente (3.9).

### 3.3 Route Mode e waypoint (pp. 195-200)

Un waypoint e' un punto arbitrario (Lat, Long, quota). Il gruppo vola da uno al successivo; a ogni waypoint si assegnano caratteristiche. Si piazza il gruppo cliccando sulla mappa con aereo selezionato: il punto diventa **waypoint 1** (icona dell'unita' al posto del cerchio). Colori: bianco = selezionato, rosso = Red non selezionato, blu = Blue non selezionato; waypoint selezionato in giallo (pp. 195, 197). Le icone per tipo unita' (p. 196, Russia/NATO): utility/attack/recon/anti-ship-ASW helicopter; fighter, attack, recon, bomber, transport, AWACS, anti-ship/ASW aircraft, tanker, UAV (immagini non leggibili in testo, solo le categorie).

| Campo waypoint | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| WAYPOINT n / N | indice corrente / totale | n.d. | Click sulla mappa in ADD aggiunge (p. 197) |
| NAME | stringa | vuoto | Mostrato sulla mappa (p. 197) |
| TYPE | vedi tabella sotto | Turning point | p. 197-198 |
| ALTITUDE | metri; tipo **MSL** (livello mare, volo livellato salvo ostacoli) o **AGL** (segue il terreno) | n.d. (screenshot: 2000 m MSL, 6096 m MSL) | p. 199 |
| SPEED | ground speed in km/h (screenshot) | calcolata se non locked | Ground speed, diversa dall'indicated airspeed del cockpit (a quota e' molto maggiore) (p. 199) |
| GS (checkbox) | lock della velocita' | off; non applicabile al waypoint iniziale | Se locked l'AI mantiene la speed sul tratto dal waypoint precedente (p. 199) |
| MACH | numero di Mach, calcolato | - | Dipende da quota, temperatura e pressione dell'editor; solo nel pannello gruppo aereo (p. 199) |
| START / ETA | h:m:s/giorno | per WP1: ora di start missione | Ora di arrivo desiderata; per il WP iniziale e' l'ora di start del gruppo (p. 199) |
| Fix time (ETA lock) | checkbox | **locked di default sul waypoint iniziale** | Se bloccata si imposta l'ETA a mano; sul WP1 consente attivazione ritardata (es. missione 12:00:00/1, gruppo a 12:15:00/1); per attivazione da evento ignoto si imposta 12:00:00/100 (100 giorni dopo) cosi' il gruppo appare solo da trigger o a quell'ora (p. 199) |

Tipi di waypoint (pp. 197-198):

| TYPE | Disponibilita' | Effetto |
|---|---|---|
| Turning point | tutti | Il piu' comune; il velivolo anticipa la virata (lead turn) per allinearsi al waypoint successivo |
| Fly over point | tutti | Sequenzia solo dopo il sorvolo diretto; richiede correzione di rotta dopo |
| Takeoff from runway | solo WP1 | Parte in soglia pista con sistemi attivi; il waypoint si aggancia al piu' vicino airfield o FARP |
| Takeoff from ramp | solo WP1 | Parte sul piazzale a sistemi spenti (cold start); aggancio all'airfield o FARP piu' vicino |
| Takeoff from parking hot | solo WP1 | Parte sul piazzale con sistemi attivi (hot); aggancio al parcheggio piu' vicino |
| LandingReFuAr | ogni WP tranne il 1 | Landing/Refuel/Rearm: si aggancia all'airfield o FARP piu' vicino |
| Landing | solo ultimo WP | Si aggancia automaticamente all'airfield o FARP piu' vicino |
| Takeoff from ground | solo WP1 (tipicamente elicotteri) | Parte da terra a sistemi spenti; richiede tempo di preparazione |
| Takeoff from ground hot | solo WP1 | Parte da terra con sistemi attivi |

Pulsanti modo waypoint (p. 200): **ADD** (default; un click aggiunge un waypoint), **EDIT** (seleziona waypoint esistenti), **DEL** (cancella il selezionato).

### 3.4 Payload Mode (pp. 201-204)

Contenuto della schermata (p. 201, immagine): disegno frontale dell'aereo con i **numeri di stazione**, Loading Chart con una riga per ogni payload package (nome + contenuto per stazione), pannello a destra con carburante, countermeasure, gun, paint scheme. Click destro su una cella stazione: elenco dei carichi ammessi per quella stazione (armi, serbatoi, pod) e voce **Remove**. I package di default dipendono dal Task del gruppo.

| Campo | Valori / unita' | Default | Note |
|---|---|---|---|
| Payload package (riga) | nome + carico per stazione | package associati al Task | NEW (crea e nomina), COPY (duplica e modifica), DELETE, RENAME, EXPORT (associa un package a un altro Task, p.es. package ATGM da CAS a Ground Attack) (p. 202) |
| INTERNAL FUEL | slider, % del massimo | n.d. | p. 203 |
| FUEL WEIGHT | kg (sola lettura) | - | Carburante interno caricato |
| EMPTY | kg | - | Peso a vuoto senza carburante e payload |
| WEAPONS | kg | - | Peso totale degli stores |
| MAX | kg | - | Peso massimo sicuro |
| TOTAL | kg | - | Vuoto + carburante + payload; barra di carico non interattiva sotto MAX/TOTAL |
| CHAFF | numero bundle (frecce < >) | n.d. | Chaff + flare limitati dal numero di cartucce: aumentandone uno cala l'altro (p. 203) |
| FLARE | numero | n.d. | idem |
| GUN | % del massimo di colpi di cannone | n.d. | p. 204 |
| AMMO TYPE | tipo di munizione del cannone | n.d. | p. 204 |
| ROPE LENGTH | lunghezza fune del carico sospeso (elicotteri) | n.d. (screenshot: 15 m con slider; unita' non scritta nel testo) | p. 204 |
| PAINT SCHEME | livrea (skin) | n.d. | Numero di scelte dipende dall'aereo (p. 204). Nello screenshot p. 201 "Demo 'Werewolf'" |

### 3.5 Triggered Actions e Route Summary (p. 204)
- **Triggered Actions**: pannello analogo all'Advanced Actions ma attivato dalle regole del Trigger Menu tramite l'azione AI TASK.
- **Route Summary**: START TIME (h:m:s/giorno), ROUTE TIME (durata assumendo nessuna deviazione, h:m:s/giorno), ROUTE LENGTH (metri), AVERAGE SPEED (media della indicated airspeed assegnata a ogni tratto, sommata e divisa per il numero di tratti: media semplice per tratto, non pesata sulla distanza).

### 3.6 Solo aerei del giocatore (pp. 205-210)
| Modo | Contenuto |
|---|---|
| INU Fix Point (p. 205) | Punti di riferimento con coordinate note per aggiornare l'INU sorvolandoli o designandoli; ADD/EDIT/DEL; coordinate mostrate nel pannello |
| Target Point (pp. 206-207) | Punti bersaglio per il sistema di navigazione (Ka-50: fino a 10, TRG01..., selezionabili dal pilota con "OT" e mostrati su PVI-800 e ABRIS); ADD/EDIT (drag)/DEL; coordinate lat/long e campo Comment |
| Failures (pp. 207-208) | Solo per aerei Player. Lista DEVICE (dipende dal tipo); per ciascuno: checkbox, **AFTER** (hh:mm da inizio missione), **WITHIN** (mm, finestra in cui puo' avvenire), **PROBABILITY** (0-100 %). Es.: L-ENGINE, After 01:00, Within 15, 50 %. Pulsanti RAND (devices/finestre/probabilita' casuali) e CLEAR (azzera tutto) |
| Waypoint Properties (p. 209) | Attributi dello steerpoint (es. A-10C: scala, steer, vertical navigation 2D/3D, vertical angle, selected vertical angle); dettagli nel manuale del velivolo/NS 430 |
| Radio Presets (p. 210) | Frequenze preimpostate sui canali delle radio dell'aereo; salvate nel file missione |

---

## 4. Advanced Actions Mode - gruppi aerei (pp. 211-221)

### 4.1 Pannello e Actions List (pp. 211-213)
Il tab Advanced mostra le azioni associate al **waypoint selezionato** (cioe' all'arrivo del lead unit a quel waypoint). Pulsanti: ADD (crea di default un "No Task"), INS (inserisce sopra la selezionata), EDIT (apre le Action Settings; stesso effetto del click sul waypoint in mappa), DEL, UP, DOWN, CLONE (clona l'azione verso il basso).

Regole di esecuzione (p. 212): un solo Task alla volta; piu' Enroute Task attivi ma uno eseguito; tutti gli Enroute Task sono fermati se serve un Task e riattivati al termine; Command e Option istantanei in ordine di lista/priority.

Formato di una riga: `<numero>.<tipo>(<param1>, ..., <paramN>)"<nome>" -<attr1> ... -<attrN>`. Il nome azione e' opzionale. Attributi:

| Attributo | Significato |
|---|---|
| `-x` | azione disabilitata |
| `-a` | generata automaticamente |
| `-!` | azione non valida (tipicamente incompatibile con il task di gruppo, p.es. se il task e' stato cambiato dopo) |
| `-?/` | ha condizione di start |
| `-/?` | ha condizione di stop |
| `-?/?` | start e stop |
| `-ref` | azione partita a un waypoint precedente |

Colori: grigio = automatica, bianco = valida, rosso = non valida. Esempio p. 213 (gruppo Su-25 attack a WP1): azione automatica CAS (grigia), Task orbit, Task Attack group, Command set frequency, Option flare using, con indicazioni grafiche di azione ereditata, stop condition, start condition, azione disabilitata.

**Esempio di sequenza (pp. 214-215)**, 6 azioni: #1 Enroute Task 1 (Search Then Engage in Zone), #2 Task 1 (Attack Group), #3 Command (Set Frequency), #4 Option (Flare Using), #5 Enroute Task 2 (Search Then Engage Group, Priority=0), #6 Task 2 (Attack Unit). All'avvio: l'AI esegue #2 (Task > Enroute) tenendo #1 in memoria; finito #2 esegue #3, #4, #6 e avvia #5 in memoria; mentre #6 e' in corso gli enroute non vengono eseguiti; finito #6, #1 e #5 competono: se le condizioni di #1 si verificano prima parte #1, ma quando diventano vere quelle di #5 (priority 0, piu' alta) #1 si ferma ed esegue #5; finito #5 riprende #1.

Triggered Tasks (p. 215): hanno priorita' **superiore** ai Task di waypoint; un Task di waypoint in corso viene sospeso e impilato e ripreso al termine di quello triggerato (o se saltato perche' impossibile). Triggered Enroute Tasks: aggiunti alla lista degli enroute attivi, restano attivi fino a stop condition.

### 4.2 Action Properties Panel (pp. 216-219)
Si apre con ADD/INS/EDIT o doppio click; NUMBER < > cicla le azioni.

| Campo | Valori | Default | Note |
|---|---|---|---|
| TYPE | Perform Task / Start Enroute Task / Perform Command / Set Option | No Task (con ADD) | p. 216-217 |
| ACTION | azione specifica del tipo scelto; dipende da tipo gruppo e task di gruppo | - | p. 217, 220 |
| NUMBER | indice nella lista | - | |
| ENABLE TASK | checkbox | on | Se tolta: attributo `-x`; utile per testare il comportamento senza cancellare |
| NAME | stringa libera | vuoto | Solo identificazione |
| CONDITION (Start) | pannello condizioni di start | nessuna | Operano in **OR**: basta una vera per attivare l'azione (p. 217) |
| STOP CONDITION | pannello condizioni di stop | nessuna | vedi tabelle |

Start Conditions (pp. 217-218):

| Condizione | Parametri | Note |
|---|---|---|
| TIME MORE | tempo di missione (h:m:s/giorno) | La condizione e' vera dopo quell'istante. Screenshot: 10:02:33/0 |
| IS USER FLAG | numero flag + stato (on/true o off/false, via checkbox) | Flag impostati dal Trigger Menu |
| PROBABILITY | percentuale (default 100 nello screenshot) | Probabilita' di avvio dell'azione |
| CONDITION (LUA PREDICATE) | espressione Lua; generato come `function <generated_name>() return <lua code> end`, eseguita periodicamente dalla simulazione | p. 218 |

Stop Conditions (pp. 218-219):

| Condizione | Valido per | Note |
|---|---|---|
| TIME MORE, IS USER FLAG, PROBABILITY, CONDITION (LUA PREDICATE) | Task e Enroute Task | Identiche alle start |
| DURATION ("DUR", h:m:s/giorno; screenshot: 0:15:0/0) | Task e Enroute Task (presente in entrambi i pannelli) | Durata massima dall'inizio dell'azione; utile per limitare il tempo on-station dell'Orbit |
| LAST WPT (menu numero waypoint) | solo Enroute Task (assente nel pannello Task, p. 218; presente in quello Enroute, p. 219) | Waypoint al quale l'azione viene fermata |

I Task possono essere fermati da stop condition o dall'AI (completamento o impossibilita'); gli Enroute Task **solo** da stop condition (p. 218). Dagli screenshot (pp. 218-219) il campo PROBABILITY appare disattivato (grigio) nei pannelli di stop; il pannello Task ha TIME MORE, IS USER FLAG, CONDITION e DUR; quello Enroute aggiunge LAST WPT.

### 4.3 Configurare azioni e Automatic Actions (pp. 220-221)
- Le azioni selezionabili dipendono dal tipo di gruppo e dal task. Cambiando il task dopo, le azioni incompatibili diventano rosse con `-!` e compare un messaggio alla chiusura/salvataggio (p. 220).
- **Automatic Actions** (p. 221): al waypoint iniziale viene generata un'azione che ripete il task di gruppo e che **determina il comportamento in gioco**; e' marcata `-a` e ripetuta come riferimento `-ref` negli altri waypoint. Cambiando il task cambiano le automatiche. Generate per i task: AWACS, Refueling, CAS, CAP, Fighter Sweep, SEAD, Anti-ship. Tranne AWACS e Refueling, sono in realta' **Enroute Task** di ricerca-poi-ingaggio dei bersagli adatti; le loro proprieta' sono predefinite e **non modificabili**.

---

## 5. Perform Task aerei (pp. 222-247)

Elenco (p. 222): No Task, Aerobatics, Attack Group, Attack Map Object, Attack Unit, Bombing, Bombing Runway, Cargo Transportation, Embarking, Disembarking, Escort, Follow, Ground Escort, FAC - Assign Group, Orbit, Land, Refueling, WW2: Big Formation, WW2: Carpet Bombing. **Nota**: per "WW2: Big Formation" il manuale (nel range letto) elenca solo il nome; non esiste una sezione dedicata in queste pagine (dalla nota di p. 247 si evince che al waypoint di partenza si impostano costruzione e tipo di formazione di battaglia).

Parametri comuni dei task di attacco (Attack Group/Map Object/Unit/Bombing/Bombing Runway/Carpet Bombing), con descrizione del manuale:

| Parametro | Descrizione | Note |
|---|---|---|
| WEAPON | Tipo/categoria di arma autorizzata; default **Auto** | Se l'arma scelta manca o e' esaurita l'attacco non viene eseguito (p. 224, 226). La lista cambia con il task |
| REL QTY | Quantita' di carico autorizzata da impiegare | Da figura (pp. 228-230, 247): **menu a tendina**; valori visti: Auto, Two, All; disattivato quando WEAPON e' Auto |
| MAX ATTACK QTY | Numero massimo di passaggi d'attacco | Da figura (pp. 227-229): checkbox di abilitazione + intero, default 1 (nel Bombing Runway il campo e' "ATTACK QTY") |
| GROUP ATTACK | Tutto il flight partecipa all'attacco | Default: ogni aereo e' assegnato a un bersaglio (p. 226) |
| DIRECTION FROM | Azimut di avvicinamento al bersaglio | Da figura (pp. 227-230): checkbox + quadrante; unita' (gradi) non scritta |
| ALTITUDE ABOVE | Quota del gruppo in avvicinamento | Da figura: checkbox + valore in m; default mostrato 2000 m (6096 m nel Carpet Bombing) |

Albero delle categorie WEAPON (pp. 225-226): Auto; **Unguided** (Cannon; Rockets: Smoke rockets, Light rockets, Candle rockets [illuminanti], Heavy rockets; Bombs: Iron bombs, Cluster bombs, Candle bombs); **Guided** (Guided bombs; Missiles = tutti i missili guidati aria-superficie e aria-aria; ASM: ATGM, Standard ASM [solo bersagli terrestri], ARM [anti-radiazione], Antiship missiles, Cruise missiles; AAM: SR AAM, MR AAM, LR AAM).

### 5.1 Schede dei task

**No Task** (p. 222): disponibile per tutti i tipi di gruppo e tutti i task; non imposta alcuna azione.

**Aerobatics** (pp. 222-223): manovre e figure acrobatiche. Gruppi fixed-wing; task: Nothing, CAP, CAS, Fighter Sweep, Ground Attack, Intercept, Reconnaissance, Transport. Pannello: lista manovre da aggiungere (+) alla colonna "Maneuver sequence", DEL/UP/DOWN per ordinare, SAVE PRESET / LOAD PRESET per serie di figure.

| Parametro (per manovra) | Note |
|---|---|
| RepeatQty | numero di ripetizioni |
| InitAltitude | quota iniziale |
| InitSpeed | velocita' iniziale |
| UseSmoke | abilita il fumo |
| StartImmediately | esegue subito all'avvio missione |
| Flight time | durata dell'esecuzione |
Da figura (p. 223): manovre disponibili Turn, Edge Flight, Loop, Skewed Loop, Wingover Flight; valori di esempio RepeatQty 1, InitAltitude 2000, InitSpeed 610, UseSmoke spuntato, StartImmediately non spuntato, Flight time 10 (unita' non scritte).

**Attack Group** (pp. 223-226): attacca uno specifico gruppo aereo, terrestre o navale. Fixed-wing ed elicotteri. Task: SEAD, CAS, AFAC (solo gruppi terrestri), Anti-ship (solo navali), Intercept (solo aerei). Campi: GROUP (tra i gruppi nemici applicabili; selezionabile anche cliccando in mappa; un triangolo rosso e una linea tratteggiata collegano bersaglio e waypoint), WEAPON (default Auto), REL QTY, MAX ATTACK QTY, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE.

**Attack Map Object** (pp. 226-227): attacca la struttura/oggetto piu' vicino a una coordinata (ponte, bunker...) perche' le strutture non sono selezionabili singolarmente; il punto bersaglio (triangolo rosso) si trascina in mappa. Fixed-wing ed elicotteri. Task: Pinpoint Strike, Ground Attack, Runway Attack. Campi: WEAPON, REL QTY, MAX ATTACK QTY, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE.

**Attack Unit** (pp. 227-229): come Attack Group ma su una singola unita' del gruppo bersaglio, oppure su un oggetto **statico** (bunker, FARP...). Fixed-wing ed elicotteri. Task: Pinpoint Strike, Ground Attack, Runway Attack (il testo p. 227-228 indica questi task). Campi: GROUP, UNIT, STATIC, WEAPON, REL QTY, MAX ATTACK QTY, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE.

**Bombing** (pp. 229-230): rilascia sulla coordinata esatta (anche terreno vuoto), non sull'oggetto piu' vicino. Fixed-wing ed elicotteri. Task: Pinpoint Strike, Ground Attack, Runway Attack. Campi: WEAPON, REL QTY, MAX ATTACK QTY, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE, **DIVE BOMB** (usabile contro bersagli per cui l'attacco a bassa quota e' impossibile per terreno, tipo di bersaglio o mancanza di munizioni adatte).

**Bombing Runway** (pp. 230-231): attacco alle piste di un aeroporto nemico. Solo fixed-wing; task Runway Attack. Campi: RUNWAY (airbase bersaglio, da menu o click su mappa), WEAPON, REL QTY, MAX ATTACK QTY, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE.

**Cargo Transportation** (pp. 231-232): trasporto carico con elicotteri. Gruppi elicottero; task Anti-ship Strike, CAS, Transport, Escort. Campi: GROUP (gruppo di cargo), ZONE (trigger zone di consegna). Il marker triangolare si associa al gruppo cargo; l'elicottero va al carico, lo preleva e lo consegna.

**Embarking** (pp. 232-234): imbarco di fanteria d'assalto. Elicotteri; task Ground Attack, CAS, Transport. Campi: ON LAND (flag + tempo h:m:s/giorno: l'elicottero resta a terra per l'intero tempo anche a imbarco concluso; se off decolla subito a fine imbarco), Distribution (pilota/elicottero), List of divisions (squadre fanteria; ogni squadra deve avere Perform Task "Embark to transport" e il flag **TRANSPORTABLE** nel pannello del gruppo veicoli), ADD / REMOVE, Total size .../... (fanti totali / posti totali nel gruppo elicotteri), Current size .../... (fanti nell'unita' selezionata / posti per elicottero), VEHICLE GROUP, ZONE RADIUS (metri). Marker triangolare da trascinare sul punto di imbarco. L'imbarco inizia dopo l'atterraggio dentro il raggio. Nota: non esistono modelli in-game dei fanti in cabina.

**Disembarking** (pp. 235-236): sbarco. Elicotteri; task Ground Attack, CAS, Transport. Campi: List of divisions (squadre disponibili; devono avere main task "Embarking"), ADD / REMOVE. Marker triangolare per il punto di sbarco; poi l'elicottero decolla e prosegue rotta e task.

**Escort** (p. 237): un gruppo aereo ne scorta un altro e ingaggia le minacce. Fixed-wing; task Escort, SEAD. Campi: GROUP (gruppo scortato; anche click su mappa); offsets formazione **Distance** (avanti/indietro), **Elevation** (differenza di quota), **Interval** (laterale), in **m** (da figura, p. 237: 20 / 0 / 50); LAST WPT (waypoint di fine); ENGAGE DIST (distanza minaccia-scortato che fa scattare l'ingaggio; da figura p. 237: 60 km); **Threat Type List** (tipi minaccia autorizzati; screenshot: Airplanes con sotto-voci Fighters, Bombers, Helicopters).

**Follow** (p. 238): segue un altro gruppo aereo. Fixed-wing ed elicotteri; qualsiasi task. Campi: GROUP, Distance/Elevation/Interval, LAST WPT.

**Ground Escort** (p. 239): elicottero scorta un gruppo terrestre lungo la sua rotta. Elicotteri; task CAS, Ground Attack, Escort. Campi: GROUP (gruppo terrestre), LAST WPT, FORWARD DISTANCE (metri, distanza in avanti verso l'area bersaglio del gruppo terrestre).

**FAC - Assign Group** (pp. 240-241): crea un AFAC che dirige velivoli amici su un gruppo bersaglio. Fixed-wing ed elicotteri, **solo coalizione BLUE**; task AFAC. Il targeting inizia quando le unita' amiche arrivano e stabiliscono comunicazione; il task assume piena situational awareness (posizione bersaglio sempre nota, l'AFAC tenta sempre di condurre l'attacco). Campi: GROUP (solo quel gruppo sara' designato), WEAPON (armi che l'AFAC richiede agli attaccanti), DESIGNATION (No, Auto, WP [smoke Willy Pete], IR-Pointer, Laser, WP-Laser; il menu mostra la distanza massima oltre cui il metodo non e' utilizzabile, nello screenshot WP e WP-Laser 16 km, IR-Pointer 5 km, Laser 10 km, come "problem: D > ... km"), DATALINK, CALLSIGN, NUMBER, FREQUENCY (MHz), MODULATION (AM/FM). La designazione avviene su richiesta radio del giocatore a distanza fissa.

**Orbit** (pp. 242-244): il gruppo orbita "on station" in attesa di condizioni. Fixed-wing ed elicotteri; tutti i task. Campi: PATTERN (**Race-Track**: ciclo tra waypoint corrente e successivo; **Circle**: centrato sul waypoint), SPEED (km/h), ALTITUDE (m). Si ferma automaticamente al **Bingo fuel** (carburante appena sufficiente per RTB) o con stop condition (tipicamente DURATION). Usi: attesa di un comando radio scriptato da trigger, distruzione di un'unita' nemica (es. SAM), presenza di unita' in una zona; le azioni successive all'orbita vanno in lista sotto l'Orbit Task. Da figura (p. 242) il pannello Orbit ha solo PATTERN, SPEED (421 km/h) e ALTITUDE (2000 m), senza selettore MSL/AGL.

**Land** (p. 244): soste intermedie di elicotteri lungo la rotta. Elicotteri; tutti i task. Campi: ON LAND (flag + tempo di attesa a terra h:m:s/giorno), area bersaglio posizionata in mappa (marker triangolare collegato al waypoint).

**Refueling** (pp. 245-246): rifornimento forzato presso il tanker piu' vicino. Fixed-wing; tutti i task. Quando il gruppo raggiunge un livello critico di carburante va al tanker amico piu' vicino, esegue l'avvicinamento e rifornisce (UPAZ sospesi dell'Il-78M: apparato di fusoliera per bombardieri pesanti, doppie unita' sotto-ala per caccia; opzioni diverse per tanker NATO); poi riprende la rotta. Nessun campo parametrico elencato nel testo.

**WW2: Carpet Bombing** (p. 247): bombardamento a tappeto di bersagli ad area (WW2). Fixed-wing (bombardieri WW2); task Ground Attack. Campi: WEAPON, REL QTY, PATTERN LENGTH (lunghezza della formazione, in m, esempio 500; da figura p. 247), ALTITUDE ABOVE; esempi WEAPON "-Bombs", REL QTY "All". L'area bersaglio si posiziona in mappa (triangolo collegato al waypoint; aree industriali, citta', gruppi terrestri). Va impostato su un waypoint **successivo** a quello di partenza; al waypoint di partenza si impostano costruzione e tipo di formazione. Se le armi non sono disponibili al momento, non attacca.

---

## 5bis. Integrazioni dalle figure (secondo passaggio, resa a 150-250 dpi)

### Esempi di lock speed/ETA (pp. 180-188) - da figura
Tutti gli esempi usano la stessa rotta di 4 waypoint (WAYPOINT n "OF 4"), numerati da 0. Valori mostrati (da figura, pp. 180-187):

| WP | Tipo | Quota (m, MSL) | Speed (km/h) | Mach | ETA (h:m:s/giorno) |
|---|---|---|---|---|---|
| 0 | Turning point | 6000 | 450 | 0.385 | START 16:10:00/0 |
| 1 | Turning point | 2880 | 298.8 (299 se locked) | 0.246 | 16:19:30/0 |
| 2 | Turning point | 675 | 298.8 (299) | 0.24 | 16:25:29/0 |
| 3 | Landing, campo PRK = auto | 45 (nessun menu MSL/AGL) | 298.8 (299) | 0.239 | 16:37:49/0 |

I campi con lock sono evidenziati da riquadri rossi. Un valore intero (es. 299) indica un campo locked/inserito dall'utente, un decimale (es. 298.8) un campo calcolato non modificabile, con la checkbox non spuntata.
- Ex. 1 (pp. 180-181): WP0 START locked (16:10:00) e WP3 ETA locked (16:37:49); speed ed ETA di WP1/WP2 calcolate (298.8; 16:19:30, 16:25:29), checkbox non spuntate.
- Ex. 2 (pp. 181-183): WP0 start locked, speed locked su tutti i waypoint (450, 299, 299, 299); ETA di WP1-3 calcolate (16:19:30, 16:25:29, 16:37:49).
- Ex. 3 (pp. 183-184): ETA locked su tutti (16:10:00, 16:19:30, 16:25:29, 16:37:49); speed calcolate 298.8 su WP1, WP2, WP3.
- Ex. 4 (pp. 184-185): WP0 start, WP1 speed 299 locked, WP2 ETA 16:25:29 locked, WP3 speed 299 locked; speed di WP2 (298.8) ed ETA di WP1 e WP3 calcolate.
- Ex. 5 (pp. 185-186): WP0 start, WP1 speed 299, WP3 speed 299 e ETA 16:37:49 locked; WP2 con speed 298.8 e ETA 16:25:29 entrambi sbloccati (waypoint "assorbente").
- Ex. 6 (p. 187): WP0 START **non** locked (16:10:00 calcolato, riquadro rosso senza spunta), WP0 speed 450 locked; speed locked 299 su WP1-WP2 (e WP3); ETA finale locked (il testo dice T3 e V1-V3). Il WP3 non e' mostrato in questa figura.
- Errori (p. 188): (a) valore fuori range: WP3 con 299 km/h e ETA 16:37:50 (1 s di scarto dal valore coerente 16:37:49) evidenzia in rosso i campi; (b) flag non valido: WP1 speed 840 km/h (Mach 0.694) con speed e ETA incorniciati in rosso. La finestra di errore e' titolata "Mission cannot be saved due to errors!" con testo del tipo "Player: All waypoints (3-3) have locked speed and surrounded by waypoints 2 and 3 with locked time!": un errore blocca il salvataggio della missione.
- Tipo `Landing` (pp. 181, 184): compare il campo **PRK** (parcheggio, valore "auto"), la quota e' in m senza selettore MSL/AGL e il pulsante ADVANCED (WAYPOINT ACTIONS) e' disabilitato (grigio) sull'ultimo waypoint.
- Figura p. 198: turning point = traiettoria curva con virata anticipata; fly over point = traiettoria che passa sul punto e poi corregge (disegni).

### Pannello del gruppo (pp. 190-191, da figura)
- Menu TASK (p. 191) in quest'ordine: Nothing, AFAC, Anti-ship Strike, AWACS, CAP, CAS, Escort, Fighter Sweep, Ground Attack, Intercept, Pinpoint Strike, Reconnaissance, Refueling, Runway Attack, SEAD, Transport (16 voci).
- Esempio p. 190: NAME "US F-15C (Player)", CONDITION vuoto con "% 100", COUNTRY USA, TASK Fighter Sweep, UNIT 1 OF 4, TYPE F-15C, SKILL Player, PILOT Player, TAIL # 511, COMM spuntato 124 MHz AM, CALLSIGN "Springfield" 1 1 (tre campi: nome, numero flight, numero unita'); waypoint 2 di 4, Turning point, 6096 m MSL, 740 km/h con GS locked, Mach 0.645, ETA 11:44:20/0.
- Gli elicotteri (Ka-52 p. 201, UH-1H pp. 231-244) hanno nella barra dei modali un'icona aggiuntiva "..."; valori tipici di esempio: 100-500 m e 160 km/h.
- Barra modali (pp. 195, 204-205, 209-210): icone in ordine route, payload, triggered actions, route summary, INU fix point, target point, failures, waypoint properties, radio presets.

### Payload (p. 203, da figura, esempio elicottero Ka-52)
INTERNAL FUEL 50 %, FUEL WEIGHT 725 kg, EMPTY 8030 kg, WEAPONS 1809 kg, MAX 11900 kg, TOTAL 10564 kg, barra di carico 89 %, CHAFF 0 (campo disattivato), FLARE 128, GUN 100 %, ROPE LENGTH 15 **m** (slider), PAINT SCHEME "Demo 'Werewolf'". Verifica: 8030 + 725 + 1809 = 10564. Il pannello a destra e' scorrevole.

### Route Summary (p. 204, da figura)
Esempio: START TIME 5:30:0/1, ROUTE TIME 0:38:51/1, ROUTE LENGTH 97 km (la figura usa km, il testo scrive metri), AVERAGE SPEED 150 km/h.

### INU Fix Point (p. 205) e Target Point (pp. 206-207) - da figura
INU: pulsanti ADD/EDIT/DEL, selettore "# n OF N", LONGITUDE e LATITUDE in gradi/primi/secondi (es. 0°43'54" E, 0°43'33" N). Target Point: stessa struttura, con in piu' un campo Comment (es. "Primary"); sulla mappa i punti appaiono come quadratini blu col commento.

### Failures (p. 208, da figura)
Lista DEVICE (esempio Ka-50, dipende dal tipo): HYDRO MAIN, HYDRO COMMON, L-ENGINE, R-ENGINE, ASC PITCH, ASC ROLL, ASC YAW, ASC ALT, ABRIS SOFTWARE, ABRIS HARDWARE, LASER FAILURE, RALT FAILURE. Colonne: checkbox, After (hh:mm), Within (mm), Probability (%). Default di riga: After 0:0, Within 1, Probability 100; esempio L-ENGINE spuntato, After 1:0, Within 15, Probability 50. Pulsanti RAND e CLEAR.

### Waypoint Properties (p. 209) e Radio Presets (p. 210) - da figura
Waypoint Properties (A-10C): WAYPNT n OF N (esempio 1 di 6), SCALE (ENROUTE), STEER (TO TO), VNAV (3D), VANGLE (COMPUTED), ANGLE (0, disattivato con COMPUTED); sotto una tabella Name/Value di proprieta' libere (PROPERTY_1) con Add, cestino, frecce su/giu. Radio Presets: per ogni radio un elenco di canali con frequenza e modulazione, es. R-828 Channel 1-10 = 21.5, 25.7, 27, 28, 30, 32, 40, 50, 55.5, 59.9 MHz FM; ARK-22 Channel 1..8 Outer/Inner in kHz AM (625/303, 289/591, 408/803, 443/215, 525/1065, 718/350, 583/283, 995/...).

### Advanced Actions (pp. 211-216, 220-221, da figura)
- Esempio p. 211: Perform Task / Attack Group, NUMBER 3, NAME "Attack", ENABLE TASK; lista azioni WP1: `1. CAS -a -ref`, `1. Orbit(H = Hwpt = 2000 m) -/?`, `2. Attack Group("LAV-25") "Attack" -?/`, `3. Set Frequency(131) -x`, `4. Chaff - Flare Using = USE AGAINST FIRED MISSILE`. Le azioni mostrano i parametri tra parentesi: l'Orbit prende la quota del waypoint (H = Hwpt), l'opzione flare ha il valore "USE AGAINST FIRED MISSILE", il Set Frequency e' un valore (131). Attack Group in figura: GROUP "LAV-25", WEAPON Auto, REL QTY Auto (disattivato), MAX ATTACK QTY (checkbox) 1, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE 2000 m.
- Grafico di priorita' (p. 214): asse tempo/priorita'; Task 1 (rosso) > Command (verde) e Option (azzurro) istantanei > Task 2 > Enroute Task 2 (arancio) > Enroute Task 1 (verde chiaro, pending o execute); conferma il testo.
- **Start Enroute Task "Search Then Engage In Zone"** (p. 216, da figura): ZONE RADIUS (2000 m), albero dei tipi di bersaglio con checkbox ALL > AIR (HELICOPTERS) e GROUND (INFANTRY, FORTIFICATIONS, VEHICLES > ARMOR), PRIORITY (0); la zona e' un cerchio sulla mappa attorno al marker. Altri Enroute citati: "Search Then Engage Group" (p. 214, Priority 0).
- Esempio p. 220: cambiando il task del gruppo a Reconnaissance le azioni `Attack Group("New Vehicle Group")` e `Search Then Engage in Zone` diventano rosse (`-!`), mentre l'Option `Chaff - Flare Using = USE AGAINST FIRED MISSILE` resta valida (le Option sono compatibili con ogni task).
- Esempio p. 221: con task CAS la lista mostra `1. CAS -a -ref` come azione automatica evidenziata.

### Perform Task - valori nei pannelli (da figura)
- Attack Group (p. 224): GROUP "Group C", WEAPON Auto, REL QTY Auto; azione automatica `2. Attack Group("Group C") -a`.
- Attack Map Object (p. 227): WEAPON "-Bombs", REL QTY Auto, MAX ATTACK QTY spuntato 1.
- Attack Unit (p. 228): GROUP "Group C", UNIT "Unit #001", STATIC "NOTHING", WEAPON Unguided, REL QTY "Two", MAX ATTACK QTY spuntato 1.
- Bombing (p. 229): WEAPON Auto, REL QTY Auto (disattivato), ATTACK QTY 1, GROUP ATTACK, DIRECTION FROM, ALTITUDE ABOVE (2000 m), DIVE BOMB.
- Bombing Runway (p. 230): RUNWAY "Sukhumi-Babushara", WEAPON "--Iron bombs", REL QTY Auto, ATTACK QTY 1, GROUP ATTACK spuntato.
- Cargo Transportation (p. 231): GROUP "Ammo", ZONE "Delivery zone" (trigger zone); gruppo UH-1H, task Transport, 100 m, 160 km/h.
- Embarking (p. 232): ON LAND spuntato con tempo 0:5:0/0, Distribution (pilota, es. "Pilot #001"), lista Division, ADD/REMOVE, "Total size 20 / 28", "Current size 20 / 14". Lato fanteria (p. 233): azione `Embark to transport` con VEHICLE GROUP "UH-1H" e ZONE RADIUS 200 m; il vehicle group (CATEGORY INFANTRY, TYPE Soldier M249, SKILL Average, HEADING, INITIAL, waypoint TYPE "Off road", TEMPLATE, speed 14 km/h) ha i flag HIDDEN ON MAP, GAME MASTER ONLY, HIDDEN ON PLANNER, PLAYER CAN DRIVE, VISIBLE bef. ACTIVATION, TRANSPORTABLE, LATE ACTIVATION.
- Disembarking (p. 235): lista Division #001, ADD/REMOVE, "Total size 0 / 28".
- Follow (p. 238): GROUP "New Airplane Group #001", Distance 10 m, Elevation 0 m, Interval 75 m, LAST WPT spuntato "DP" (ultimo waypoint della rotta).
- Ground Escort (p. 239): GROUP "New ground group", LAST WPT 3, FORWARD DIST 500 m.
- FAC - Assign Group (pp. 240-241): GROUP "Group B", WEAPON "--ATGM", DESIGNATION Auto, DATALINK spuntato, CALLSIGN "Enfield", NUMBER 1, FREQUENCY 133 MHz, MODULATION AM. Menu DESIGNATION: No, Auto, WP, IR-Pointer, Laser, WP-Laser, con limiti in rosso (WP e WP-Laser 16 km, IR-Pointer 5 km, Laser 10 km).
- Escort (p. 237): Distance 20 m, Elevation 0 m, Interval 50 m, LAST WPT spuntato "DP", ENGAGE DIST 60 km; albero minacce: AIR > AIRPLANES (spuntato) > FIGHTERS, BOMBERS (spuntati), HELICOPTERS (non spuntato).
- Orbit (pp. 242-243): PATTERN "Race-Track", SPEED 421 km/h, ALTITUDE 2000 m; i disegni mostrano il cerchio (centrato sul waypoint) e lo stadio tra waypoint corrente e successivo.
- Land (p. 244): ON LAND non spuntato (tempo 0:5:0/0 disattivato); marker triangolare sul punto di atterraggio.
- Refueling (p. 245): figura con interfaccia in russo: task di gruppo "Patrolling" (Pattugliamento), lista `1. Patrolling -a`, `2. Refueling`; nessun campo parametrico.
- WW2 Carpet Bombing (p. 247): WEAPON "-Bombs", REL QTY "All", PATTERN LENGTH 500 m, ALTITUDE ABOVE (checkbox, 6096 m).

### Correzioni rispetto al testo
- ROUTE LENGTH nella figura e' in km (p. 204).
- Nei pannelli di stop il campo PROBABILITY e' disattivato e "DUR" ha formato h:m:s/giorno (es. 0:15:0/0) (p. 218); LAST WPT solo per gli Enroute (p. 219).

---

## 6. Rilevanza per Warfare-Model

### 6.1 Dato di missione (cio' che il pianificatore deve produrre)
- **Gruppo**: nome univoco, country (coalizione), task di gruppo (enum di 16 valori), numero unita' 1-4, tipo, skill (Average/Good/High/Excellent/Random; Client/Player per umani), nomi pilota, tail number, frequenza+modulazione, callsign, flag di visibilita'/attivazione (late activation, uncontrolled, hidden), condition Lua di spawn.
- **Rotta**: lista ordinata di waypoint con (lat, long, quota + tipo MSL/AGL, tipo waypoint, speed ground km/h, ETA h:m:s/giorno, lock di speed e ETA). Vincolo di validita': almeno un ETA locked; 2 grandezze su 3 fra distanza/speed/tempo determinano la terza; range di speed e' dell'asset (min/max di volo).
- **Ora di start del gruppo** = ETA del WP1 (locked di default); l'attivazione ritardata o da evento si ottiene spostando l'ETA oltre la durata missione (es. giorno 100) o con Late Activation.
- **Start type** = tipo del WP1 (runway / ramp cold / parking hot / ground / ground hot / air quando il WP1 non e' un takeoff, che nel manuale non e' descritto esplicitamente in queste pagine); **end** = Landing/LandingReFuAr che si aggancia ad airfield/FARP.
- **Modello di task a tre livelli**: (1) task di gruppo (filtro + azione automatica al WP1 ripetuta con `-ref`); (2) lista ordinata di azioni **per waypoint** (Task, Enroute Task, Command, Option), con priority intera (0 = massima), enable, nome, start condition (OR di time more, user flag, probability, Lua) e stop condition (time more, flag, probability, Lua, duration, last wpt); (3) azioni **triggered** indipendenti dalla rotta (AI Task nel Trigger Menu), con priorita' superiore.
- **Semantica di esecuzione da riprodurre nel simulatore sintetico**: Task > Enroute Task; un Task alla volta; Task triggerato sospende il Task di waypoint (stack) e questo riprende; Enroute sospesi durante un Task e riattivati; stop automatico per bersaglio distrutto/armi esaurite/non eseguibile; Orbit e CAP terminano a **Bingo fuel** con RTB.
- **Parametri dei task** utili al modello: bersaglio (gruppo/unita'/static/coordinata/map object/runway), arma autorizzata per categoria (albero a due-tre livelli), REL QTY, MAX ATTACK QTY, GROUP ATTACK, DIRECTION FROM (azimut), ALTITUDE ABOVE (quota di attacco), DIVE BOMB, pattern orbit (circle / race-track) con speed e quota, offset di formazione (distance/elevation/interval), ENGAGE DIST e threat type per le scorte, last waypoint, designazione/frequenza per FAC, zone e liste per trasporto/imbarco/sbarco.
- **Payload** (a livello di gruppo, per missione): package per stazione (arma/serbatoio/pod), % carburante interno, chaff e flare (con vincolo di cartucce condivise), % gun e tipo munizione, rope length, livrea. Check di peso: empty + fuel + weapons <= MAX (kg).

### 6.2 Dato di asset (non di missione)
- Per tipo di velivolo: stazioni disponibili e carichi ammessi per stazione, pesi (EMPTY, MAX), capacita' carburante, cartucce countermeasure totali, munizioni cannone, tipi di munizione, skin disponibili, range di speed/quota (usato per la validita' di speed/ETA), numero di posti per imbarco fanteria, equipaggiamento di designazione e relative portate (WP 16 km, IR-Pointer 5 km, Laser 10 km, WP-Laser 16 km nello screenshot), apparati di rifornimento, Bingo fuel, effetti dello skill sui parametri (G, portata di attacco, precisione, tempi di reazione, portate di rilevamento).
- Il tipo di velivolo determina categoria (fighter, attack, bomber, tanker, AWACS, UAV, utility/attack/recon helicopter...) e quindi i task e i payload compatibili.

### 6.3 Solo interfaccia (non modellare)
Colori di waypoint, icone, frecce di navigazione, pulsanti ADD/INS/EDIT/DEL/UP/DOWN/CLONE, CTRL+C/V, attributi di visualizzazione della lista (`-x -a -! -ref` sono solo marcatori; ma "automatico" e "invalido" riflettono dati reali: origine dell'azione e compatibilita' task), Hidden on planner (briefing), Radio presets, INU fix point, Target Point, Failures (solo Player), Waypoint Properties dei cockpit, NAME dell'azione.

### 6.4 Osservazioni e rischi di modellazione
- Il task di gruppo non pilota il comportamento: e' un filtro. Il comportamento e' nelle azioni, e quelle automatiche (CAS, CAP, Fighter Sweep, SEAD, Anti-ship = Enroute "search then engage"; AWACS e Refueling = task stessi) non sono modificabili. Per una esportazione in `.miz` conviene generare esplicitamente le azioni del WP1 coerenti con il task di gruppo.
- Le attese condizionate (Orbit + stop condition) sono il meccanismo per sincronizzare gruppi; un modello sintetico dovrebbe avere un equivalente (condizione di sblocco: flag, tempo, distruzione, zona).
- Speed e ETA sono ground speed e ora di arrivo del tratto che *termina* nel waypoint; la lista Average speed del Route Summary e' una media per tratto (indicated), non per distanza.
- Differenze fra categorie: gli elicotteri hanno task esclusivi (Cargo Transportation, Embarking, Disembarking, Ground Escort, Land); i fixed-wing hanno Aerobatics, Bombing Runway, Escort, Refueling, Carpet Bombing; Orbit e Follow sono comuni; FAC - Assign Group solo Blue. Le differenze con gruppi terrestri/navali non sono coperte in queste pagine (esulano dalla porzione).
- Ancora non specificati dopo il secondo passaggio sulle figure: unita' della DIRECTION FROM (gradi presunti) e dei parametri dell'Aerobatics, significato del campo % di CONDITION, default di TASK/TYPE/SKILL; il tipo di waypoint per "start in air" non e' nell'elenco TYPE di p. 198.
