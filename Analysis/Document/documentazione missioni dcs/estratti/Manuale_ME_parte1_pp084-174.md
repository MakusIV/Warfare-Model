# DCS World User Manual (EN 2020) - Mission Editor, parte 1 (pp. 84-174)

Estratto per Warfare-Model: quali dati definiscono una missione DCS. Numeri di pagina = pagine del PDF (coincidono con la numerazione stampata). Termini DCS in inglese.

Nota di perimetro: nel PDF le pagine 84-174 trattano l'interfaccia generale del Mission Editor (ME), Resource Manager, briefing, meteo, trigger, goals, battlefield commanders. Il posizionamento di gruppi/unità, i pannelli di gruppo (aerei, terrestri, navali), waypoint, task e payload sono nel capitolo "Task Planning for Unit Groups" che inizia a p. 175 (fuori da questa porzione). Pagine senza testo estraibile: 110 e 111 (solo screenshot di cartelle Kneeboard e di un cockpit Su-25 con kneeboard, letti visivamente); tutte le altre sono leggibili. Alcuni pannelli (Mission Options p. 92-95, schermata coalizioni p. 87) sono stati verificati sugli screenshot.

---

## 1. Panoramica del Mission Editor (pp. 84-86)

Il ME crea missioni stand-alone, di campagna, di training e multiplayer (p. 84). Elementi: mappa interattiva, strumenti di piazzamento unità, weather editor, gestione file, goal tool, trigger tool, pannelli specializzati.

Aree dello schermo (p. 85): World Map, Mission and Map Bar (in basso), System Bar (in alto), Tool Bar (a sinistra).

Mission and Map Bar (p. 86): nome missione ("New Mission" finché non salvata), coordinate cursore, altitudine cursore (ft o m secondo Options/Gameplay/Units), formato coordinate commutabile Lat/Long, Lat/Long Decimal, MGRS (Options/Misc/Coordinate Display), modalità mappa (MAP/SAT/ALT), locale, orologio reale di Windows (NON il tempo di missione). Solo interfaccia: pan/zoom col mouse.

---

## 2. System Bar (pp. 87-98)

Menu: FILE, EDIT, FLIGHT, CAMPAIGN BUILDER, CUSTOMIZE, MISSION GENERATOR, MISC (p. 87).

### 2.1 FILE > NEW: Theater of War e Coalitions (pp. 87-88)

Dopo NEW compare la finestra "NEW MISSION SETTINGS" (screenshot p. 87): colonna "CHOOSE MAP" con le mappe Caucasus, Nevada, Normandy, Persian Gulf (descrizione di Caucasus: regione del Mar Nero orientale con territorio russo, georgiano e turco, molti aeroporti, aree urbane, linee di comunicazione, tutte e quattro le stagioni); area "ASSIGN COUNTRIES TO COALITIONS" con tre colonne (Red, non assegnati al centro, Blue).

| Campo | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| Map (theater) | Caucasus, Nevada, Normandy, Persian Gulf (come visibile nello screenshot p. 87; la lista può dipendere dai moduli posseduti: non specificato) | non leggibile | Definisce il terreno di tutta la missione |
| Coalition Presets | Custom (assegnazione manuale), Modern (realtà moderna), WWII (schieramenti della WWII) (p. 88) | Custom (screenshot) | Preset modificabili a piacere |
| Countries RED / BLUE | Ogni paese è in RED, in BLUE o non assegnato. Paesi visibili nello screenshot: Abkhazia, Belarus, China, Iran, Kazakhstan, North Korea, Russia, Serbia, South Ossetia, Syria, Venezuela (Red); Algeria, Austria, Bahrain, Brazil, Bulgaria, Chile, Cuba, Egypt, Ethiopia, Finland, Greece, Honduras, Hungary, India, Indonesia, Insurgents, Iraq (non assegnati, lista tagliata); Australia, Belgium, Canada, Croatia, Czech Republic, Denmark, France, Georgia, Germany, Israel, Italy, Norway, Poland, South Korea, Spain, Sweden, The Netherlands (Blue) | dipende da preset | I paesi non assegnati NON partecipano alla missione (p. 87). Il paese selezionato per un gruppo filtra i tipi di unità disponibili (p. 191, fuori porzione). Alleanze libere: "realistiche o fantasiose" (p. 88) |
| CLEAN COALITIONS | pulsante | - | Ripristina la distribuzione di default |
| SAVE | pulsante | - | Salva la distribuzione corrente e la rende default |
| OK | pulsante | - | Usa la distribuzione per questa missione senza salvarla come default |

### 2.2 FILE > OPEN / SAVE / SAVE AS / EXIT (pp. 88-89)

Le missioni sono file `*.miz`; Save As può salvare anche `*.trk` (track). Open: browser con DRIVE, PATH, FILE, tipo file. Exit chiude il ME. Solo interfaccia.

### 2.3 EDIT (p. 89)

Duplica i comandi della Tool Bar: ADD AIRPLANE, ADD HELICOPTER, ADD SHIP, ADD VEHICLE, ADD STATIC, ADD TEMPLATE, REMOVE, LOAD STATIC TEMPLATE, SAVE STATIC TEMPLATE. (Il manuale in questa porzione non dettaglia il formato dei template statici.)

### 2.4 FLIGHT (pp. 89-92)

- FLY MISSION: chiude il ME e avvia la simulazione; tempo di caricamento dipende da numero unità, quantità di scripting, RAM (pp. 89).
- PREPARE MISSION (p. 90): avvia la missione in modalità preparazione per salvare nel `.miz` configurazioni avionica dei moduli. Ka-50: `Scripts\World\GPS_GNSS.lua` (satelliti), `ABRIS\Database\ADDITIONAL.lua`, `NAVIGATION.lua`, `ROUTES.lua`. A-10C: CDU (tutto tranne il flight plan del ME), IFFCC, MFCD, SADL, TAD, TGP (codici laser, ecc.), DSMS (Mission Control Page, weapon profiles). Avviso: se si usa Prepare Mission il giocatore non deve usare il mission planner (conflitto fra script avionica salvati e nuova rotta/armi).
- RECORD AVI (pp. 90-92) e REPLAY: conversione track in video. Ignorabile.

### 2.5 CAMPAIGN BUILDER (p. 92)

Citato come "Staged Campaign System (SCS)"; dettaglio in un altro capitolo (fuori porzione).

### 2.6 CUSTOMIZE > MISSION OPTIONS (pp. 92-95)

Blocca opzioni di gioco per la missione. Ogni opzione ha un pulsante ENFORCE (sinistra: impone l'opzione al giocatore) e un VALUE (destra: ON se spuntato, OFF altrimenti). Se in Options\Gameplay la casella "USE THESE OPTIONS FOR ALL MISSIONS" e' spuntata, prevalgono le opzioni principali; se non spuntata prevalgono quelle bloccate dalla missione (p. 92).

| Opzione | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| Permit Crash RCVR | on/off | VALUE on (da figura, p. 93) | Respawn in velivolo integro dopo distruzione/eiezione (p. 93) |
| External Views | on/off | VALUE on (da figura, p. 93) | |
| F10 View Options | mutuamente esclusivi: Map Only (nessun aereo/veicolo/nave), My A/C, Fog of War (nasconde l'attività nemica nelle zone non esplorate), Allies Only, All | ENFORCE spuntato, selezionato All (da figura, p. 93) | Visibilità sulla mappa F10 (p. 93) |
| Labels | menu a tendina (visibile 'NONE'; altri valori non leggibili) | NONE (da figura, p. 93) | Vicino: tipo + distanza; medio: solo distanza; lontano: solo tacca (pp. 93-94) |
| Game Flight Mode | on/off | non leggibile | Easy flight, arcade |
| Game Avionic Mode | on/off | non leggibile | Marker 3D di orientamento |
| Immortal | on/off | non leggibile | Velivolo indistruttibile |
| Unlimited Fuel | on/off | non leggibile | Carburante sempre 100% |
| Unlimited Weapons | on/off | non leggibile | Armi consumate si rigenerano |
| Easy Communication | on/off | non leggibile | |
| Radio Assists | on/off | non leggibile | Cue vocali su minacce, parametri di lancio, allarmi |
| Unrestricted SATNAV | on/off | non leggibile | Navigazione satellitare per tutti i velivoli capaci, indipendentemente da paese e data/ora |
| Padlock | on/off | non leggibile | |
| Tool Tips | on/off | non leggibile | |
| Wake turbulence | on/off | non leggibile | |
| G-Effect | NONE, GAME, SIMULATION | ENFORCE spuntato, Simulation (da figura, p. 93) | |
| Random System Failures | on/off | non leggibile | Guasti casuali per l'unità del giocatore |
| Mini HUD | on/off | non leggibile | Solo Flaming Cliffs 3 |
| Cockpit Visual Recon Mode | on/off | non leggibile | Marca un oggetto a terra e ne rivela la posizione alle mappe degli alleati (RMB croce, LMB seleziona) |
| F10 Map User Marks | on/off | ENFORCE e VALUE on (da figura, p. 93) | Segnalini utente sulla mappa |
| Civ Traffic | OFF, LOW, MEDIUM, HIGH | ENFORCE spuntato, Medium (da figura, p. 93) | Auto, camion, treni civili nell'area dettagliata (p. 95) |
| BIRD % | 0-1000 (%): 100 = probabilita' realistica, 0 = nessun uccello, 1000 = moltiplicatore x10; vale sotto 200 m | non leggibile | Probabilita' di bird strike (p. 95) |
| Overlay: Cockpit Status Bar | on/off | non leggibile | Parametri di volo e coordinate |
| Overlay: Battle Damage Assessment | on/off | VALUE on (da figura, p. 93) | Mostra % danno inflitto (distrutto in rosso, danneggiato in giallo con %) |
| Overlay: Compass Tape | on/off | non leggibile | |
| Overlay: Aircraft Mode Indicators | on/off | non leggibile | Sistemi, modi di combattimento, armi, CM |

Tutte opzioni di esperienza del giocatore umano: nessun effetto sul modello di combattimento AI (eccetto Immortal/Unlimited Fuel/Unlimited Weapons che valgono solo per il giocatore).

### 2.7 CUSTOMIZE > MAP OPTIONS (pp. 95-96)

Filtri di layer sulla World Map: AIRFIELDS, BUILDINGS (off di default), ELECTRIC POWER TRANSMISSION, FORESTS, GEOGRAPHICAL GRID, ISOLINES, MGRS GRID, PARKINGS, RAILWAYS, RIVERS, ROADS, TOWNS, USER OBJECTS. Solo visualizzazione (p. 96).

Classi di icone aeroporto (p. 96): Helipad (schieramento temporaneo aviazione dell'esercito); campo/aviazione generale/3a classe (1200-1700 m) non presenti in gioco; 2a classe pista 1800-2400 m; 1a classe pista 2500-3000 m. Dato utile come classificazione di basi.

### 2.8 CUSTOMIZE > LOCALE PANEL e SET POSITION (pp. 96-97)

Locale: gestione di versioni di localizzazione della missione (lingua scelta da elenco, pulsante create; testi e immagini del briefing possono avere versione per lingua). SET POSITION: imposta le coordinate geografiche del teatro (campi non leggibili in dettaglio).

### 2.9 MISSION GENERATOR (pp. 97-98)

Voci: GENERATE (apre Fast Create Mission, Advanced Mode), NODES (pannello Mission Nodes: definiscono dove possono essere generate forze blue e red; creare/modificare/rimuovere), TEMPLATES (Templates Editor: tipi, numeri e formazioni di unita' usate per popolare i nodi), SAVE (salva nodi e template). Concetto interessante per un generatore: nodi di spawn + template di forza.

### 2.10 MISC (p. 98)

Encyclopedia e crediti. Ignorabile.

---

## 3. Resource Manager e magazzini (pp. 99-105)

Il Resource Manager (RM) definisce quantita' di aerei, carburante ed equipaggiamento in ogni warehouse di aeroporto o warehouse indipendente; ogni warehouse puo' rifornirne altre con velocita', periodicita' e dimensione definite (p. 99). Serve a limitare aerei/carburante/armi disponibili ai giocatori (e all'AI).

Regola di default (p. 99): gli aeroporti sono NEUTRI e hanno risorse INFINITE (produzione illimitata di aerei, carburante, armi). Le risorse si consumano dalla propria warehouse e possono essere rifornite da altre.

### 3.1 Pannello "WAREHOUSE IN AIRPORT" (pp. 99-100)

Aperto con click sinistro sul cerchio dell'aeroporto.

| Campo | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| COALITION | Neutral, Blue, Red | Neutral | Gli aeroporti lavorano solo con aerei della propria coalizione: va impostata per tutte le basi coinvolte prima di pianificare (p. 100) |
| NAME | testo (sola lettura per airbase, es. "Maykop-Khanskaya") | nome base | |
| TOWER FREQUENCY | frequenze MHz (esempio screenshot: 39.200, 125.000, 254.000, 3.950 MHz) | per base | Frequenze del controllore |
| FULL INFO | pulsante | - | Apre la finestra RM completa |
| SUPPLIERS | lista di warehouse collegati; ADD / DEL | vuota | Catene di rifornimento (p. 100). Nota testuale: la finestra mostra le warehouse "che la warehouse selezionata sta rifornendo" |

### 3.2 Resource Manager, Full Info (pp. 101-104)

Supply rates (in alto a sinistra, pp. 101-102):

| Campo | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| Speed | km/h (campo dello screenshot "kmh") | 60 (screenshot) | Velocita' su strada dei convogli virtuali dal fornitore alla warehouse rifornita |
| Periodicity | minuti | 30 (screenshot) | Ogni quanto parte un convoglio; solo dopo una richiesta di rifornimento; se il warehouse collegato non e' il richiedente non fornisce |
| Size | tonnellate | 100 (screenshot) | Quantita' consegnata a ogni consegna |
| Copy to | seleziona airbase di destinazione + checkbox air-to-air?, fuel, equipment (nello screenshot le caselle visibili sono "air-to-air", "fuel", "equipment"; il testo parla di AIRCRAFT, FUEL, EQUIPMENT) | - | Copia la configurazione RM per le categorie spuntate |
| Operating level, % | percentuale | 10 (screenshot, campo grigio) | Quando la risorsa scende a questo livello, il fornitore piu' vicino avvia una consegna; la warehouse invia la richiesta alla warehouse collegata a monte |

I valori di default indicati sono quelli visibili negli screenshot (pp. 101-103), non dichiarati nel testo.

Inventario (colonna centrale, tre schede A/C, LIQUIDS, EQP; pulsante "Clear col" azzera tutti i valori della categoria) (p. 102):

| Scheda | Contenuto | Default | Note |
|---|---|---|---|
| A/C | Tipo di aereo e numero iniziale ("Initial"). Esempi in elenco: A-10A, A-10C, A-50, AH-1W, AH-64A, AH-64D, AJS37, An-26B, An-30M, AV-8B N/A, B-17G, B-1B, B-52H, Bf 109 K-4, C-101CC, C-101EB, C-130, C-17A, CH-47D, CH-53E, Christen Eagle II, E-2D, E-3A, F-111F, F-117A ... | 100 per ogni tipo (screenshot) | Checkbox "Unlimited Aircraft": base sempre a forza massima (100). Checkbox "Hide Not Flyable": mostra solo aerei pilotabili dal giocatore |
| LIQUIDS | Initial Fuel Amount, tonnellate, per: Jet fuel, Aviation gasoline, Water-methanol mixture MW50, Diesel fuel (voci visibili nello screenshot p. 103) | 100 t se "Unlimited" (testo: "always at 100 tons") | Checkbox "Unlimited Liquids/Fuel". Operating level % anche qui |
| EQP | Armi, pod, serbatoi: nome dello store e numero iniziale | non leggibile | Modificabile solo se "Unlimited Munitions" NON e' spuntato. Sette filtri di categoria: AA missiles, AG missiles, AG Rockets (non guidati), AG Bombs (non guidate), AG Guided Bombs (laser/GPS), Fuel tanks (esterni), Misc (pod ECM, fumo, gun pod, targeting pod, ecc.) (pp. 103-104) |

Copy to Other Warehouses (p. 104): sceglie le risorse da copiare (A/C, Fuel, Eqp) e l'airbase di destinazione.

### 3.3 Warehouse indipendenti e catene (pp. 104-105)

- Si piazza una warehouse indipendente da "Add or Modify Static Object" (tipo Warehouse); inventario impostabile come per le basi (p. 104).
- Collegando warehouse, devono appartenere alla stessa coalizione (p. 104).
- Si possono concatenare piu' warehouse in serie; piu' fornitori e piu' consumatori su una singola warehouse (p. 105).
- Con piu' fornitori, la richiesta va prima al piu' vicino; se non soddisfa tutta la lista richiesta si passa al piu' distante, ecc. (p. 105).
- Il testo non specifica FARP in questo capitolo (i FARP compaiono come helipad/landing in altri punti, p. 198 e p. 126).

---

## 4. Tool Bar (pp. 106-107)

Pulsanti (p. 106): Create New Mission, Open Mission File, Save Mission File, Create Mission Briefing, Create Weather Conditions, Set Rules for Triggers, Define Mission Goals, Set Mission Options, Fly Mission, Place Airplane Group, Place Helicopter Group, Place Naval Group, Place Ground Vehicle Group, Place Static Object, Create Area Trigger Zone, Create Template, Area Trigger Zone List, Unit List, Delete Unit/Object, Map Options, Distance Tool, Close Editor, Create IP Navigation Point, Edit Bullseye Locations, Battlefield Commanders. Il piazzamento dei gruppi, la zona trigger, template, bullseye, IP nav point sono dettagliati dopo p. 174 (fuori porzione).

Categorie di oggetti piazzabili (quindi categorie di "gruppo" di missione): Airplane, Helicopter, Ship (naval), Vehicle (ground), Static.

### 4.1 Mission Briefing (pp. 107-109)

| Campo | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| SORTIE | testo | - | Titolo della missione nel briefing |
| RED / BLUE | elenco automatico dei paesi assegnati alle coalizioni | - | Sola lettura |
| Briefing images (per coalizione e per locale) | jpg/jpeg/png, minimo 512x512 px, consigliato 1024x1024 | vuoto | Salvate nel `.miz`; schermata p. 108: griglia con righe per locale (DFLT, RU, DE, CS, CN) e schede Blue / Red |
| SITUATION | testo libero | - | Testo generale (campo SITUATION del briefing) |
| RED TASK / BLUE TASK | testo libero | - | Testo per coalizione, mostrato nel campo OBJECTIVE |
| Data e ora di inizio | giorno / mese / anno + hh:mm:ss (pannello meteo p. 113) | 1 June 2011, 08:00:00 nello screenshot | Vedi nota sotto |

Nota data/ora: il testo di p. 108 (probabilmente di versione precedente) dice che il calendario parte dal 1 giugno come "giorno 0", es. 1 luglio = giorno 30, 1 novembre = giorno 153; formato `hh:mm:ss/giorno`; default 12:00:00/0. Nella versione dell'interfaccia mostrata a p. 113 e p. 115 la data di inizio e' invece un campo giorno/mese/anno + ora (default screenshot 1 June 2011, 8:0:0). Il formato `hh:mm:ss/N` (N = giorni dall'inizio) resta usato per gli orari di partenza dei gruppi (es. 12:00:00/1, 12:15:00/1; p. 199 fuori porzione). Data e ora determinano posizione di sole, luna e stelle (p. 109); per notti piu' buie scegliere una data con luna poco visibile.

### 4.2 Kneeboard (p. 109-111)

Carte personalizzate (jpg/png, nomi senza caratteri non latini, dimensioni 1024x680 o 1024x768) si mettono in `C:\Users\<utente>\Saved Games\DCS\Kneeboard\<nome cartella modulo>\` (le cartelle devono corrispondere ai nomi in `...\Mods\aircraft`); appaiono in coda alle carte standard; apertura con RShift+K. Gli screenshot (pp. 110-111) mostrano cartelle per modulo (A-10C, F-86F Sabre, Ka-50, L-39C, Mi-8MT, MIG-15bis, MIG-21bis, P-51D, Su-25, Su-25T, TF-51D, Uh-1H) e un cockpit Su-25 con kneeboard. Dato di missione solo come asset grafico per giocatori umani.

---

## 5. Meteo (pp. 112-116)

Pannello "TIME AND WEATHER" con due modalita': Static (meteo fisso definito dall'utente) e Dynamic (generato da differenze di pressione, evolve nella missione) (p. 112). In cima c'e' il blocco START con data/ora (screenshot p. 113: giorno, mese, anno; ore:min:sec).

### 5.1 Static conditions (pp. 112-114)

Sezioni: Season, Clouds and Atmosphere, Wind, Turbulence, Fog, Dust Smoke, Weather Templates.

| Campo | Valori ammessi / unità | Default (screenshot p. 113) | Note |
|---|---|---|---|
| Season | Summer, Winter, Spring, Fall | non leggibile | Cambia l'aspetto del terreno e mimetizzazione di molti veicoli (p. 112). Il drop-down non e' visibile nello screenshot di p. 113 |
| Temperature (T °C) | gradi Celsius a livello del mare | 20 | Influenza le prestazioni degli aerei (p. 112) |
| Cloud BASE | 300-5000 m (sul livello del mare) | 2300 m (screenshot) | Quota della base dello strato (p. 112) |
| Cloud THICKNESS | metri dalla base | 1540 m (screenshot) | Si applica solo a copertura solida (Density 9-10), non a nubi sparse (1-8). Es.: base 2000 + spessore 1000 = nubi fra 2000 e 3000 m |
| Cloud DENSITY | 0-10 | 4 (screenshot) | 0 nessuna nube; 1-8 nubi sparse a densita' crescente; 9-10 strato solido (overcast). La copertura nuvolosa e' uniforme su tutto il mondo; le nubi in Static sono fisse (p. 112) |
| PRECPTNS | None, Rain, Thunderstorm, Snow, Snowstorm | NONE | Le scelte variano con stagione, temperatura e densita' nubi (p. 113) |
| QNH | mmHg | 747 (screenshot) | Pressione barometrica ("Q code") (p. 113) |
| Wind (4 fasce) | Quote: 10 m, 500 m, 2000 m, 8000 m (testo p. 114: "10 - 500 - 2,000 - 8,000 meters"); per ciascuna: velocita' in m/s e direzione in gradi | screenshot: 8000 m = 22 m/s dir 120; 2000 m = 9 m/s dir 63; 500 m = 6 m/s (dir campo disabilitato, mostra 42); 10 m = 3 m/s dir 42 | Vento costante, senza raffiche. La direzione e' quella VERSO cui soffia il vento nell'interfaccia (0 gradi = vento che soffia dal sud verso il nord, p. 114). Nord = alto del quadrante. A 500 m la direzione nello screenshot e' disabilitata (probabilmente derivata dalle fasce adiacenti: non dichiarato nel testo) |
| TURBULENCE | incrementi di 0.1 m/s al suolo; decresce con la quota | 16 (screenshot, unita' mostrata "0.1* m") | Interpretazione dell'unita' nello screenshot: non del tutto leggibile |
| FOG ENABLE | on/off | on (screenshot) | |
| FOG VISIBILITY | metri | 4190 m (screenshot) | Visibilita' di oggetti oscurati dalla nebbia |
| FOG THICKNESS | metri dal livello del mare (0 = livello del mare) | 110 m (screenshot) | Es. 50 = strato uniforme da 0 a 50 m sul livello del mare (p. 114) |
| DUST SMOKE ENABLE | on/off | off (screenshot) | Effetto polvere/fumo |
| DUST SMOKE VISIBILITY | metri | 300 m (campo disabilitato, screenshot) | Visibilita' durante tempesta di polvere |
| Weather Templates | elenco di template salvati; LOAD, SAVE, REMOVE | "DEFAULT WEATHER" | Utili per campagne (p. 114) |

### 5.2 Dynamic conditions (pp. 115-116)

Sezioni: Start, Dynamic Weather, Turbulence, Fog, Weather Templates. Season, temperatura, turbolenza, nebbia, polvere e template identici allo Static. Differisce il blocco DYNAMIC WEATHER:

| Campo | Valori ammessi / unità | Default (screenshot p. 115) | Note |
|---|---|---|---|
| BARIC SYSTEM | cyclone (bassa pressione), anticyclone (alta pressione), none | CYCLONE | |
| SYSTEMS QUANTITY | numero di sistemi barici sulla mappa (campo "N OF M": 1 di 2 nello screenshot) | 1 | |
| PRESSURE DEVIATION | Pascal, deviazione al centro del sistema rispetto a ISA | -1318 Pa (screenshot) | |
| GENERATE | pulsante | - | Genera un sistema meteo randomizzato dai parametri impostati |

Nubi e venti sono generati dinamicamente su tutta la mappa in base a tipo, posizione e deviazione di pressione dei sistemi; il vento evolve durante la missione al variare di pressioni e posizioni (p. 116). Nel Dynamic il blocco Clouds/Wind manuale non e' presente.

---

## 6. Trigger (pp. 117-170)

Il sistema trigger e' "a condizione", non "a evento": un trigger scatta quando una condizione diventa TRUE, non quando accade qualcosa (p. 117) (eccetto l'uso del campo EVENT, vedi sotto). Missioni e campagne usano lo stesso scripting. Procedura: 1) creare un trigger, 2) definire condizioni, 3) definire azioni. Ogni trigger puo' avere un colore (palette) solo per comodita'.

### 6.1 Struttura della finestra TRIGGERS (pp. 117-123)

Quattro riquadri: Trigger List, Trigger Conditions, Trigger Actions, Initialization Script.

**Initialization Script** (pp. 118-119): carica/resetta (OPEN / RESET) un file Lua nella missione, eseguito prima del caricamento della missione, per impostare condizioni di spawn casuale dei gruppi. Nel campo CONDITION del pannello gruppo (aereo/elicottero/nave/terrestre) si scrive una espressione Lua con strumenti SSE (Simulator Scripting Engine). Mostra nome del file script.

**Trigger List** (pp. 120-123): ogni trigger e' elencato come "TIPO (nome)", es. `ONCE (Set Area 01)`. Pulsanti NEW, DELETE, CLONE, frecce su/giu' (ordine).

| Campo | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| TYPE | ONCE; REPETITIVE ACTION; SWITCHED CONDITION; MISSION START | non leggibile | Vedi descrizioni sotto |
| NAME | testo (univoco consigliato) | - | |
| EVENT | NO EVENT, ON DESTROY, ON SHOT, ON CRASH, ON EJECT, ON REFUEL, ON PILOT DEAD, ON BASE CAPTURED, ON TAKE CONTROL, ON REFUEL STOP, ON FAILURE, ON MISSION START, ON MISSION ENDS | NO EVENT | Senza evento le condizioni sono valutate una volta al secondo per tutta la missione (costo CPU); con evento solo quando accade (pp. 122-123). Rilevanti per un motore: ON DESTROY, ON BASE CAPTURED, ON MISSION START/ENDS |

Semantica dei TYPE (pp. 120-122):
- ONCE: condizione valutata continuamente fino a TRUE, poi rimossa; azione eseguita una volta. Esempio: attivare un gruppo AAA di rinforzo quando un gruppo corazzato e' distrutto (Group Dead -> Activate Group; il gruppo AAA va impostato con start time ritardato, es. 23 ore).
- REPETITIVE ACTION: condizioni controllate ogni secondo; azioni eseguite ogni secondo in cui sono TRUE.
- SWITCHED CONDITION: azioni eseguite a ogni transizione FALSE->TRUE della condizione.
- MISSION START: valutato ed eseguito una sola volta all'avvio (es. attivazione casuale di gruppi con condizione RANDOM 10%).

### 6.2 Conditions (pp. 124-137)

Piu' condizioni su un trigger: operatore AND implicito; il pulsante OR separa blocchi in OR (p. 124). Pulsanti NEW, DELETE, CLONE, su/giu'. Catalogo (parametri in una riga):

Zone/coalizione/gruppo (pp. 125-130):
- ALL OF COALITION IN ZONE / OUT OF ZONE: coalition, zone (tutti gli aerei/veicoli/navi della coalizione dentro/fuori).
- PART OF COALITION IN ZONE / OUT OF ZONE: coalition, zone (almeno uno).
- ALL OF GROUP IN ZONE / OUT OF ZONE: group, zone.
- PART OF GROUP IN ZONE / OUT OF ZONE: group, zone.
- UNIT INSIDE ZONE / UNIT OUTSIDE ZONE: unit, zone.
- UNIT INSIDE MOVING ZONE / UNIT OUTSIDE MOVING ZONE: zone unit (a cui la zona e' attaccata, al centro dell'unita'), zone, unit.
- DEAD ZONE: zone (regola sullo stato della zona; semantica non dettagliata).
- BOMB IN ZONE: tipo e quantita' di bomba, zone.
- MISSILE IN ZONE: tipo e quantita' di missile, zone.
- CARGO UNHOOKED IN ZONE: cargo, zone.

Basi (p. 126) [RILEVANTE]:
- COALITION HAS AIRDROME: coalition, airfield. Regola di cattura: un aeroporto senza aerei assegnati al decollo/atterraggio e senza unita' di terra entro 2000 m e' neutrale; un'unita' di terra entro 2000 m lo cattura per la propria coalizione; unita' di terra di entrambe entro 2000 m: conteso, non assegnato; unita' armate di una coalizione contro unita' non armate dell'altra: vince la coalizione delle armate.
- COALITION HAS HELIPAD: coalition, FARP. Regole di cattura identiche all'airfield.

Flag (pp. 127-128) [RILEVANTE]:
- FLAG IS TRUE / FLAG IS FALSE: flag.
- FLAG EQUALS: flag, value. FLAG EQUALS FLAG: flag, flag.
- FLAG IS LESS / FLAG IS MORE: flag, value. FLAG IS LESS THAN FLAG: flag, flag.

Gruppi/unita' (pp. 128-135) [RILEVANTE]:
- GROUP ALIVE: group (vero se almeno un'unita' viva).
- GROUP ALIVE LESS THAN: group, % (es. 10 unita' e 40% -> scatta quando ne restano 3; testo come scritto nel manuale).
- GROUP DEAD: group (tutte distrutte).
- UNIT ALIVE / UNIT DEAD / UNIT DAMAGED: unit.
- UNIT'S LIFE LESS THAN: unit, % di "vita".
- UNIT HITS: target object, numero di colpi a segno (unita' giocatore).
- MAP OBJECT IS DEAD: nome della trigger zone assegnata all'oggetto mappa (edificio, ponte...) con click destro (p. 129).

Punteggio (pp. 129-131):
- MISSION SCORE HIGHER THAN / LOWER THAN: coalition, score.
- PLAYER SCORES MORE / LESS: score.

Tempo e probabilita' (pp. 131-132) [RILEVANTE]:
- RANDOM: 0-100 (% di probabilita').
- TIME MORE / TIME LESS: secondi dall'inizio missione.
- TIME SINCE FLAG: flag, secondi di ritardo dopo che il flag e' TRUE.

Stato cinematico unita' (pp. 134-136):
- UNIT'S ALTITUDE HIGHER/LOWER THAN (MSL, metri); UNIT'S AGL ALTITUDE HIGHER/LOWER THAN (metri AGL): unit, altitudine.
- UNIT'S SPEED HIGHER/LOWER THAN: unit, velocita' in m/s indicati.
- UNIT'S BANK IN LIMITS; HEADING IN LIMITS; PITCH IN LIMITS; VERTICAL SPEED IN LIMITS (m/s): unit, min, max (bank: negativo = sinistra; pitch negativo = muso in basso).
- UNIT'S ARGUMENT IN RANGE / PLAYER'S UNIT ARGUMENT IN RANGE: oggetto, numero argomento animazione, min, max.

Altri:
- LUA PREDICATE: codice Lua che restituisce true/false (esempio p. 129: gruppo che vede un nemico via `Controller:getDetectedTargets()`).
- Condizioni con prefisso "X:" servono ai cockpit trigger (vedi 6.4) (p. 137).

### 6.3 Actions (pp. 138-154)

Pulsanti NEW, DELETE; campo ACTION + parametri. Piu' azioni per trigger. Catalogo compatto (parametri):

Controllo di gruppi/unita' [RILEVANTE per campagna]:
- GROUP ACTIVATE: group (appare in missione; il gruppo deve avere start time oltre ogni tempo di gioco previsto, es. almeno 1 giorno dopo: 12:00:11/2 se la missione parte 12:00:00/1; pp. 141-142). Nel pannello gruppo esiste anche l'opzione di visibilita' prima dell'attivazione (p. 170).
- GROUP DEACTIVATE: group (rimosso dalla missione).
- GROUP AI OFF / GROUP AI ON: group (AI disattivata: nessun movimento, sensori, combattimento; ON solo dopo OFF).
- UNIT AI OFF / UNIT AI ON: unit.
- GROUP STOP: group (solo terrestri; ferma il movimento). GROUP RESUME: group (riprende la rotta).
- STOP AND DEPLOY TO TEMPLATE: group, template (posizione di formazione, es. batteria di artiglieria).
- UNIT EMISSION ON / OFF: unit (radar). Nota: nel manuale (p. 154) le descrizioni sono scambiate rispetto ai nomi; l'intento e' accendere/spegnere l'emissione radar di una unita'.
- AI TASK PUSH: group, task da eseguire (aggiunge il task in testa). AI TASK SET: group, nome dell'azione definita nel pannello "Triggered Actions" del gruppo (pp. 138-139).
- STATIC ACTIVATE: gruppo di oggetti statici (spawn ritardato).
- EXPLODE UNIT: unit, volume (dimensione esplosione). SET INTERNAL CARGO: massa in kg (elicotteri).
- BEGIN PLAYING ACTOR / STOP PLAYING ACTOR: numero giocatore. START/STOP PLAYER SEAT LOCK: numero sedile.

Flag [RILEVANTE]:
- FLAG ON (valore 1 di default), FLAG OFF (valore 0, flag rimosso).
- FLAG INCREASE / FLAG DECREASE: flag, value (se il valore diventa 0 il flag e' rimosso; sono ammessi negativi).
- FLAG SET RANDOM VALUE: flag, VALUE LIM MIN, VALUE LIM MAX.
- SET FLAG VALUE: flag, value. I flag hanno nome (numero naturale) e valore (numero naturale; con negativi ammessi dalla sottrazione) (pp. 140-141, 149).

Scripting e flusso missione:
- DO SCRIPT (testo Lua), DO SCRIPT FILE (file Lua).
- END MISSION: testo mostrato alla vittoria di una parte.
- LOAD MISSION: carica un'altra missione (solo multiplayer; permette campagne multiplayer) (p. 143).
- SET BRIEFING: coalition, testo, immagine opzionale.

Effetti e ambiente:
- EXPLOSION: zona, quota, volume. SHELLING ZONE: zona, TNT per proiettile, numero di proiettili. ILLUMINATING BOMB: zona, quota (illumina 2 minuti, scende ~1000 m). SIGNAL FLARE (zona, colore) / SIGNAL FLARE ON UNIT. SMOKE MARKER (zona, quota, WP bianco) / SMOKE MARKER ON UNIT. EFFECT - SMOKE: zona, preset, densita'.
- SCENERY DESTRUCTION ZONE: zona, % di distruzione. SCENERY REMOVE OBJECTS ZONE: zona, tipo (ALL, TREES ONLY, OBJECTS ONLY).
- PLAY ARGUMENT: argomento di animazione di un oggetto statico.

Comunicazioni e interfaccia giocatore (poco rilevanti per un motore): MESSAGE TO ALL / COALITION / COUNTRY / GROUP (testo, durata s, CLEARVIEW, START DELAY s); SOUND TO ALL / COALITION / COUNTRY / GROUP (file ogg/wav, START DELAY); STOP LAST SOUND; RADIO TRANSMISSION (file, zona, modulazione AM/FM, loop, freq MHz, potenza W, nome, start delay) e STOP RADIO TRANSMISSION; RADIO ITEM ADD / REMOVE (anche FOR COALITION, FOR GROUP; testo + flag da alzare; ADD non funziona in multiplayer); MARK TO ALL / COALITION / GROUP (valore, testo, zona, [coalizione/gruppo], read-only, commento) e REMOVE MARK; SET FAILURE (guasto, PROBABILITY %, WITHIN); SET ACTIVE HELPER GATE TO POINT, SHOW HELPER GATES (coordinate, rotta), SHOW HELPER GATES FOR UNIT.

### 6.4 Cockpit Triggers (pp. 155-164)

Condizioni/azioni "X:" per missioni di addestramento: valutano e manipolano interruttori/strumenti del cockpit di un velivolo flyable tramite argomenti e comandi dei file Lua del modulo (`command_defs.lua`, `clickabledata.lua`, `devices.lua`, `mainpanel_init.lua`, `device_init.lua`). Non rilevanti per un motore di campagna con AI. Elenco sintetico: condizioni X: COCKPIT ARGUMENT IN RANGE (argomento, min/max in [-1,1]), COCKPIT HIGHLIGHT IS VISIBLE, COCKPIT INDICATION TEXT IS EQUAL TO, COCKPIT PARAM EQUAL TO / IN RANGE / IS EQUAL TO ANOTHER (alcune richiedono console); azioni X: COCKPIT HIGHLIGHT ELEMENT / INDICATION / POINT, PARAM SAVE AS, PERFORM CLICKABLE ACTION (device, command da 3000, value), REMOVE HIGHLIGHT, PREVENT CONTROLS SYNCHRONIZATION, SET COMMAND, SET COMMAND WITH VALUE, START LISTEN COCKPIT EVENT (solo Ka-50; eventi: setup_HMS, setup_NVG, DisableTurboGear, EnableTurboGear, GroundPowerOn/Off, OnNewNetHelicopter, OnNewNetPlane, initChaffFlarePayload, switch_datalink, WeaponRearmFirstStep, WeaponRearmComplete, repair, LinkNOPtoNet, UnlinkNOPfromNet), START LISTEN COMMAND (comando, flag, hit count, val min/max, device), START/STOP WAIT USER RESPONSE (barra spaziatrice -> flag).

### 6.5 Esempio pratico (pp. 165-170)

Missione dimostrativa con quattro/cinque trigger di tipo ONCE: (1) UNIT INSIDE ZONE (giocatore in zona "Start Artillery") -> GROUP ACTIVATE di un gruppo artiglieria; (2) giocatore in zona "FAC Message" -> MESSAGE TO ALL + SOUND TO ALL; (3) unita' amica in zona "Objective" -> messaggio+suono di successo; (4) GROUP DEAD sul blocco corazzato nemico -> GROUP ACTIVATE della colonna amica che avanza; (5) condizione RANDOM 50% -> GROUP ACTIVATE di un gruppo AAA nemico. Punto chiave: i gruppi attivati dai trigger devono avere start time oltre il tempo di gioco previsto.

---

## 7. Define Mission Goals (pp. 171-172)

Esito della missione basato su punti assegnati dal mission builder (p. 171): totale <= 49 = fallimento; = 50 = pareggio; >= 51 = successo. Il punteggio determina anche quale stage/missione scegliere dopo in una campagna. Si usano le stesse condizioni dei trigger.

| Campo | Valori ammessi / unità | Default | Note |
|---|---|---|---|
| Goal list | elenco di goal "nome (score, assegnatario)"; es. screenshot: "RTB (100, OFFLINE)", "Player damaged (-20, OFFLINE)", "Player killed (-30, OFFLINE)" | vuota | Pulsanti NEW, DELETE, CLONE |
| NAME | testo | - | |
| SCORE | intero (anche negativo, vedi esempi) | - | Punti del goal |
| Assegnatario | OFFLINE (missione singola, solo giocatore), RED, BLUE | - | Chi riceve i punti |
| CONDITIONS | una o piu' condizioni, stesso catalogo dei trigger (es. UNIT INSIDE ZONE (82, Airfield), UNIT'S ALTITUDE LOWER THAN (82, 25)) | - | Il goal e' raggiunto quando TUTTE le sue condizioni sono vere (p. 172) |

---

## 8. Battlefield Commanders (pp. 173-174)

| Campo | Valori ammessi / unità | Default (screenshot p. 173) | Note |
|---|---|---|---|
| PILOT CAN CONTROL VEHICLES | on/off | off | Permette al giocatore in aereo di dare comandi di movimento/targeting alle unita' di terra AI dalla mappa F10; da abilitare in single player |
| GAME MASTER (Red, Blue) | numero di slot per coalizione | Red 0, Blue 1 | Osserva e gioca come JTAC controllando unita' di entrambe le parti, vede tutte le unita'; i due ruoli sono equivalenti. Sconsigliato nel head-to-head |
| TACTICAL CMDR | numero di slot | Red 0, Blue 1 | Controllo strategico di unita' di terra dalla mappa F10, incluse artiglieria e MLRS; anche controllo in prima persona e JTAC |
| JTAC / Operator | numero di slot | Red 0, Blue 1 | Controllo in prima persona e JTAC, senza controllo strategico |
| OBSERVER | numero di slot | Red 0, Blue 1 | Solo camera illimitata |

I ruoli sono scelti dai giocatori in una finestra "Choose Role" all'avvio. Gli aerei a controllo umano compaiono anch'essi nell'elenco (p. 174).

---

## 9. Set Mission Options e Fly Mission (p. 174)

Set Mission Options riapre il pannello descritto in 2.6. Fly Mission (pulsante verde) esce dal ME e apre il Briefing in preparazione al volo.

---

## 10. Rilevanza per Warfare-Model

### 10.1 Cosa e' DATO DI MISSIONE (da generare nel .miz)

- Mappa (theater) e assegnazione paesi a RED/BLUE (paesi non assegnati esclusi); coalition preset (pp. 87-88).
- Data/ora di avvio e calendario (formato `hh:mm:ss/giorno`; luna/sole derivati); orari di start dei gruppi come ETA del primo waypoint (p. 108, 199).
- Meteo statico: stagione, temperatura a livello del mare (C), una sola fascia di nubi (base 300-5000 m, spessore, densita' 0-10, precipitazione), QNH (mmHg), vento a 4 quote (10, 500, 2000, 8000 m) con velocita' m/s e direzione, turbolenza, nebbia (visibilita', spessore), polvere (visibilita'). Meteo dinamico: tipo e numero di sistemi barici, deviazione di pressione in Pa. Il meteo e' uniforme su tutto il mondo e le nubi statiche non cambiano (pp. 112-116). Per un modello sintetico basta replicare questi parametri.
- Obiettivi: Mission Goals con punteggio per coalizione (OFFLINE/RED/BLUE), soglie 49/50/51 per fallimento/pareggio/successo, condizioni scelte dallo stesso catalogo dei trigger (p. 171). Utile come interfaccia di esito missione per la campagna.
- Trigger: tipo (ONCE/REPETITIVE/SWITCHED/MISSION START), evento, lista condizioni (AND, con OR), lista azioni. Per un motore di campagna sono rilevanti: condizioni su flag, zone (unita'/gruppo/coalizione dentro/fuori), GROUP DEAD / GROUP ALIVE LESS THAN / UNIT DEAD / UNIT'S LIFE LESS THAN, COALITION HAS AIRDROME / HELIPAD (con regola di cattura a 2000 m), MAP OBJECT IS DEAD, TIME MORE / TIME SINCE FLAG, RANDOM, MISSION SCORE; azioni GROUP ACTIVATE / DEACTIVATE (attivazione ritardata e rinforzi), GROUP AI ON/OFF, GROUP STOP/RESUME, UNIT EMISSION ON/OFF, AI TASK PUSH/SET, SET FLAG/INCREASE/DECREASE/SET RANDOM, END MISSION, STATIC ACTIVATE, SCENERY DESTRUCTION, SHELLING ZONE, DO SCRIPT. Pattern chiave: flag come variabili di stato condivise; attivazione ritardata impostando lo start time del gruppo molto in avanti (>= 1 giorno).
- Initialization script Lua e condizione Lua di spawn per gruppo (spawn casuale) (pp. 118, 191).
- Briefing: SORTIE, SITUATION, RED TASK, BLUE TASK, immagini per coalizione e locale (testo/grafica, utile per output ma non per la simulazione).
- Ruoli multiplayer (Battlefield Commanders): slot per coalizione di Game Master, Tactical Cmdr, JTAC/Operator, Observer; flag "pilot can control vehicles".

### 10.2 Cosa e' STATO DEL MONDO / CAMPAGNA (persistente fra missioni)

- Warehouse: coalizione dell'airbase (default Neutral con risorse infinite), inventario aerei per tipo, carburante per tipo (jet fuel, avgas, MW50, diesel, in tonnellate), equipaggiamento (armi/pod/serbatoi per categoria, numeri), operating level %, fornitori collegati con speed (km/h), periodicity (min), size (t). Il RM modella una catena logistica con richieste a soglia; in un motore di campagna corrisponde alla scorta per base e al rifornimento fra depositi (stessa coalizione). I warehouse indipendenti sono oggetti statici di tipo Warehouse.
- Proprieta' delle basi: coalizione, frequenza torre, tipo (helipad, 1a/2a classe con lunghezza pista), cattura per presenza di unita' terrestri entro 2000 m. Il passaggio di proprieta' di una base e' uno stato di campagna.
- Punteggio cumulativo (goal) che decide lo stage successivo in una campagna (p. 171).
- Stato di vita dei gruppi/unita' (alive/dead/damaged, % vita) e dei map object (distrutti) usati dalle condizioni.

### 10.3 Cosa e' SOLO INTERFACCIA / ASSET e si puo' ignorare

Navigazione mappa, barre, layer della Map Options, Locale (salvo testi localizzati), AVI/Replay, Kneeboard (asset grafico), cockpit triggers X: (solo training), messaggi/suoni/radio item/mark F10, helper gates, opzioni di gioco del giocatore (Mission Options: tranne Fog of War/F10 visibility e Civ Traffic che hanno effetto sul mondo), icone di unita', pulsanti di file.

### 10.4 Altre osservazioni utili

- Il manuale (in questa porzione) non fornisce i valori ammessi delle opzioni AI di gruppo, dei task, dei payload e dei waypoint: sono nel capitolo da p. 175 (task: Nothing, AFAC, Anti-ship Strike, AWACS, CAP, CAS, Escort, Fighter Sweep, Ground Attack, Intercept, Pinpoint Strike, Reconnaissance, Refueling, Runway Attack, SEAD, Transport; skill Average/Good/High/Excellent/Random/Client/Player; 1-4 aerei per gruppo; tipi di waypoint e lock di speed/ETA), esplorato dagli altri estratti.
- Le condizioni dei trigger sono valutate a ogni secondo di simulazione (se senza evento), un modello a tempo discreto con granularita' di 1 s; un motore a eventi (DES) puo' tradurre condizioni in eventi notevoli (distruzione unita', ingresso in zona, scadenza tempo).
- I goal e i trigger condividono lo stesso catalogo di condizioni: un unico modello di "Condition" in Warfare-Model puo' alimentare sia goal sia trigger e sia l'esito sintetico sia l'export .miz.
- Unita' di misura DCS: quote in metri (MSL o AGL), velocita' in m/s (condizioni) o km/h (supply speed), pressione QNH in mmHg e deviazione in Pa, temperatura in C, rifornimenti in tonnellate, tempi in secondi (condizioni, messaggi) e minuti (periodicity).


---

## 11. Integrazioni dalle figure (secondo passaggio)

Sono state riesaminate le schermate delle pagine 87, 93, 95, 97, 99-105, 108, 113, 115, 118-120, 124-153, 170-171, 173-174. Le pagine 156-169 (cockpit trigger ed esempio pratico) mostrano solo pannelli di quegli stessi campi e non aggiungono valori; le pagine 84, 85, 88, 89, 91, 106 sono schermate di interfaccia gia' coperte dal testo.

### 11.1 Mission Options, valori di default visibili (da figura, p. 93)
Il pannello ha colonne ENFORCE / OPTION / VALUE. Stato mostrato: ENFORCE spuntato solo su F10 View Options, G-Effects, F10 Map User Marks, Civ. Traffic. VALUE spuntato su Permit Crash RCVR, External Views, F10 Map User Marks, Battle Damage Assessment; F10 View Options = All; Labels = NONE (disabilitato); G-Effects = Simulation; Civ. Traffic = Medium; BIRD % ha uno slider con campo numerico (valore non leggibile). Le altre opzioni sono off e non imposte. Il nome mostrato nel pannello e' "G-Effects" (testo: G-Effect). Map Options (da figura, p. 95): 13 layer tutti spuntati di default (AIRFIELDS, BUILDINGS, ELECTRIC POWER TRANSMISSION, FORESTS, GEOGRAPHICAL GRID, ISOLINES, MGRS GRID, PARKINGS, RAILWAYS, RIVERS, ROADS, TOWNS, USER OBJECTS), contrariamente al testo p. 96 che dice BUILDINGS off di default.

### 11.2 Locale e posizione (da figura, p. 97)
"Locale control panel": Current locale (DEFAULT), Select locale (elenco), pulsanti OK e DELETE LOCALE; a destra "Create new locale" con Select locale (es. "EN English") e CREATE LOCALE. SET POSITION: nessuno screenshot dedicato.

### 11.3 Resource Manager (da figura, pp. 99-105)
- Warehouse in Airport (p. 99): Coalition = Neutral (menu), NAME = Maykop-Khanskaya, TOWER FREQUENCY elenca 4 frequenze (39.200, 125.000, 254.000, 3.950 MHz); sulla mappa l'aeroporto ha cerchio di zona e frequenze radionavigazione/ILS (es. 591.00 kHz, 289.00 kHz, 334.00 MHz DG Chan 34): dati di aiuti alla navigazione per base.
- Finestra Resource Manager (pp. 101-104): campi Speed 60 kmh, Periodicity 30 min, Size 100 t; pulsante Copy to con elenco airbase (esempio "Anapa-Vityazevo") e tre caselle: air-to-air, fuel, equipment (le tre etichette effettive nella UI; il testo parla di AIRCRAFT/FUEL/EQUIPMENT); Operating level % = 10 (campo disabilitato se Unlimited).
- Scheda A/C (p. 102): checkbox "Unlimited Aircraft" (spuntata nello screenshot), "Hide Not Flyable"; tabella Type of Aircraft / Initial con valore 100.
- Scheda LIQUIDS (p. 103): checkbox "Unlimited Liquids" spuntata; campi Jet fuel tons, Aviation gasoline tons, Water-methanol mixture MW50 tons, Diesel fuel tons (valori disabilitati leggibili come 100); Operating level %.
- Scheda EQP (p. 104): checkbox "Unlimited Munitions" (non spuntata nello screenshot) e 7 radio button di categoria: AA missiles (selezionato), AG missiles, AG Rockets, AG Bombs, AG Guided Bombs, Fuel tanks, Misc. Tabella Type / Initial con valore 100. Esempi AA missiles: AIM-120B, AIM-120C, AIM-54C, AIM-7E, AIM-7F, AIM-7M, AIM-7MH, AIM-9L, AIM-9M Sidewinder IR AAM, AIM-9P Sidewinder IR AAM, AIM-9P5, AIM-9X Sidewinder IR AAM, CAP-9M, GAR-8, Matra Magic II, Matra S530D, MBDA Mistral, MICA IR, MICA RF, PL-12, PL-8A, PL-8B, R-13M, R-13M1, R-24R, R-24T... Pulsante "Clear col".
- Catena di rifornimento (p. 105): la lista SUPPLIERS mostra i warehouse collegati per nome (es. "Novyj statich. objekt", "... #001" in cirillico/inglese); sulla mappa i collegamenti sono frecce fra warehouse (icone rosse) con direzione dal fornitore al rifornito; gli oggetti warehouse hanno il nome dell'oggetto statico.

### 11.4 Briefing e meteo (da figura, pp. 108, 113, 115)
- Briefing (p. 108): SORTIE, righe Red e Blue con elenchi di paesi, pulsante BRIEFING IMAGES PANEL, riquadri SITUATION / RED TASK / BLUE TASK. Il pannello immagini ha schede Blue / Red e righe per locale (DFLT, RU, DE, CS, CN) con 6 slot immagine per riga.
- Meteo (pp. 113, 115): confermati i valori gia' riportati; il pannello ha tab STATIC / DYNAMIC, la sezione "CONDITIONS" contiene la temperatura. Nel Dynamic, "SYSTEMS QUANTITY" mostra "1 OF 2" e PRESSURE DEVIATION -1318 Pa con pulsante GENERATE. Il selettore Season non e' visibile in nessuno screenshot dei pannelli (resta non leggibile).

### 11.5 Trigger: struttura e campi visibili (da figura, pp. 118-120, 124, 170)
- Finestra TRIGGERS a 3 colonne (TRIGGERS, CONDITIONS, ACTIONS) con CLONE e frecce; sotto la lista trigger: TYPE, NAME, EVENT e una palette COLOR con campi R, G, B (0-255, default 192/192/192; es. rosso 255/0/0). In basso INITIALIZATION SCRIPT con OPEN, RESET, nome file (es. Export.lua) e campo CODE (p. 118, 170).
- Il selettore del file script e' un browser "Choose Lua script" con filtro "Scripts (*.lua)" (p. 119).
- Elenco di trigger di esempio: "1 ONCE (LZ Alpha 1, NO EVENT)", "1 ONCE (SAM1, NO EVENT)", "1 ONCE (I'm hit! (501), NO EVENT)", "1 ONCE (comms - engine start, NO EVENT)": il prefisso "1" davanti a ONCE e' il codice del tipo (p. 120). Menu TYPE mostra "1 ONCE".
- Condizioni mostrate con parametri tra parentesi, es. "FLAG IS FALSE (1)", "TIME MORE (1620)", "[OR]", "UNIT INSIDE ZONE (501, SAM1)", "FLAG IS TRUE (11)" (p. 124).

### 11.6 Nomi esatti dei campi delle condizioni (da figura, pp. 125-136)
- ALL/PART OF COALITION IN/OUT OF ZONE: COALITION (Red/Blue), ZONE.
- ALL/PART OF GROUP IN/OUT OF ZONE: GROUP, ZONE.
- BOMB IN ZONE: TYPE BOMB (es. AGM-62), BOMB QUANTITY (default 1), ZONE. MISSILE IN ZONE: TYPE MISSILE (es. TGM-65G Maverick), VALUE (quantita'), ZONE.
- CARGO UNHOOKED IN ZONE: CARGO (es. Ammo), ZONE. COALITION HAS AIRDROME: COALITION, AIRDROME. COALITION HAS HELIPAD: COALITION, FARP. DEAD ZONE: ZONE. MAP OBJECT IS DEAD: ZONE.
- FLAG EQUALS / IS LESS / IS MORE: FLAG, VALUE. FLAG EQUALS FLAG / LESS THAN FLAG: FLAG, FLAG. FLAG IS TRUE / FALSE: FLAG.
- GROUP ALIVE / DEAD: GROUP. GROUP ALIVE LESS THAN: GROUP, %.
- MISSION SCORE HIGHER/LOWER THAN: COALITION, SCORE (esempio 50). PLAYER SCORES LESS/MORE: SCORES.
- RANDOM: % (campo numerico). TIME LESS/MORE: SECONDS. TIME SINCE FLAG: FLAG, SECONDS.
- UNIT ALIVE / DEAD / DAMAGED: UNIT. UNIT HITS: UNIT, HITS NUMBER. UNIT'S LIFE LESS THAN: UNIT, %.
- UNIT INSIDE/OUTSIDE ZONE: UNIT, ZONE. UNIT INSIDE/OUTSIDE MOVING ZONE: UNIT, ZONE, ZONE UNIT.
- UNIT'S ALTITUDE / AGL ALTITUDE HIGHER/LOWER THAN: UNIT, ALTITUDE (metri, es. 2500).
- UNIT'S SPEED HIGHER/LOWER THAN: UNIT, SPEED; nello screenshot l'unita' mostrata e' **kmh** (es. 360 kmh), mentre il testo (pp. 136) dice metri al secondo: discrepanza, da verificare nell'implementazione.
- UNIT'S BANK / HEADING / PITCH / VERTICAL SPEED IN LIMITS: UNIT, MIN, MAX. UNIT'S ARGUMENT IN RANGE: UNIT, ARGUMENT, MIN, MAX. PLAYER'S UNIT ARGUMENT IN RANGE: ARGUMENT, MIN, MAX.
- LUA PREDICATE: campo TEXT (codice Lua).

### 11.7 Nomi esatti dei campi delle azioni (da figura, pp. 138-153)
- AI TASK PUSH: AI ACTION. AI TASK SET: AI TASK. BEGIN PLAYING ACTOR: NUMBER. DO SCRIPT: TEXT. DO SCRIPT FILE: FILE (+OPEN).
- END MISSION: WINNER (menu, es. Red), TEXT (es. "Red victory!"), START DELAY (s).
- EFFECT - SMOKE: ZONE, PRESET (es. "small smoke and fire"), DENSITY. EXPLODE UNIT: UNIT, VOLUME (es. 1000). EXPLOSION: ZONE, ALTITUDE, VOLUME.
- FLAG ON/OFF: FLAG. FLAG INCREASE/DECREASE/SET FLAG VALUE: FLAG, VALUE. FLAG SET RANDOM VALUE: FLAG, VAL LIM MIN, VAL LIM MAX.
- GROUP STOP: GROUP. ILLUMINATING BOMB: ZONE, ALTITUDE (es. 600). LOAD MISSION: FILE (+OPEN).
- MARK TO ALL: VALUE (id marker), TEXT, ZONE, READONLY, COMMENT; MARK TO COALITION aggiunge COALITION; MARK TO GROUP aggiunge GROUP. REMOVE MARK: VALUE.
- MESSAGE TO ALL/COALITION/COUNTRY/GROUP: [COALITION | COUNTRY | GROUP], TEXT, SECONDS (default 20 negli screenshot, 60 nell'esempio), CLEARVIEW, START DELAY (default 0).
- PLAY ARGUMENT: UNIT, ARGUMENT, START, STOP, SPEED m/s. RADIO ITEM ADD: NAME, FLAG, VALUE (default 1, 1); ... FOR COALITION: COALITION, NAME, FLAG, VALUE; ... FOR GROUP: GROUP, NAME, FLAG, VALUE. RADIO ITEM REMOVE: NAME; ... FOR COALITION: COALITION, NAME; ... FOR GROUP: GROUP, NAME.
- RADIO TRANSMISSION (p. 148): FILE (+OPEN, play/stop), ZONE, MODULATION (es. FM), LOOP (Off), FREQ MHz (es. 124), POWER W (es. 100), NAME, START DELAY.
- SCENERY DESTRUCTION ZONE: ZONE, DESTRUCTION LEVEL % (es. 90). SCENERY REMOVE OBJECTS ZONE: ZONE, OBJECTS MASK (es. OBJECTS ONLY).
- SET ACTIVE HELPER GATE TO POINT: UNIT, NUMBER (waypoint). SET BRIEFING: COALITION, FILE, TEXT. SET FAILURE: FAILURE (es. HYDRO MAIN), Probability (%) (es. 100), Within (min) (etichetta "Within (mm)", unita' non del tutto leggibile).
- SET INTERNAL CARGO: Mass kg (es. 250). SHELLING ZONE: ZONE, TNT Eq (es. 0.5), SHELLS COUNT (es. 100). SHOW HELPER GATES: X, Z, Y, COURSE. SHOW HELPER GATES FOR UNIT: UNIT, FLAG.
- SIGNAL FLARE: ZONE, ALTITUDE (600), COLOR (GREEN), BEARING. SIGNAL FLARE ON UNIT: UNIT, COLOR, BEARING. SMOKE MARKER: ZONE, ALTITUDE, COLOR (es. ORANGE). SMOKE MARKER ON UNIT: UNIT, COLOR (es. BLUE).
- SOUND TO ALL/COALITION/COUNTRY/GROUP: [COALITION | COUNTRY | GROUP], FILE (+OPEN, play/stop), START DELAY. START PLAYER SEAT LOCK: NUMBER. STATIC ACTIVATE: GROUP (gruppo di statici). STOP AND DEPLOY TO TEMPLATE: GROUP, TEMPLATE (es. "Hawk SAM Battery").
- Esempio di elenco azioni (p. 138): FLAG OFF (2), GROUP ACTIVATE (Alpha_UAZ), MESSAGE TO ALL (testo radio, 20 s), FLAG ON (10), SOUND TO ALL (file ogg).

### 11.8 Esempio pratico, schermata finale (da figura, p. 170)
Trigger "Random AAA": TYPE 1 ONCE, EVENT NO EVENT, condizione RANDOM con % = 50, azione GROUP ACTIVATE gruppo AAA; i trigger hanno colori diversi (palette).

### 11.9 Battlefield Commanders e Choice of role (da figura, pp. 173-174)
Valori di default confermati (Red 0 / Blue 1 per tutti e quattro i ruoli; "Pilot can control vehicles" non spuntato). Finestra "Choice of role" (p. 174) con colonne Role, Unit, Onboard, Country, Task, Group name, Start Position; righe: Pilot (esempio A-10C/2, onboard 10, USA, CAS, group CSAR, Start Position Air), TACTICAL CMDR, JTAC/Operator, GAME MASTER, OBSERVER; pulsanti BACK, OK. Mostra quali attributi di un gruppo con slot umani compaiono nel briefing: unita', numero di coda, paese, task, nome gruppo, posizione di partenza (Air / Ramp / ecc., valore completo non leggibile).

### 11.10 Goals (da figura, p. 171)
Confermato: goal "RTB (100, OFFLINE)" con condizioni "UNIT INSIDE ZONE (82, Airfield)" e "UNIT'S ALTITUDE LOWER THAN (82, 25)"; altri goal "Player damaged (-20, OFFLINE)" e "Player killed (-30, OFFLINE)". Campi: NAME, SCORE (con frecce), menu assegnatario (OFFLINE), TYPE, UNIT, ZONE.
