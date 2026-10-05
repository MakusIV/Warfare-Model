# DCS User Manual 2020 - Mission Editor, parte 4 (pp. 287-357)

Fonte: `DCS_User_Manual_EN_2020.pdf`, pagine 287-357 (numero di pagina PDF = numero stampato in questa porzione). Tutte le pagine sono state lette (testo estratto per intero; schermate verificate a campione: pp. 292, 294, 311, 330, 343, 346). Nessuna pagina illeggibile. Secondo passaggio sulle figure fatto: vedi sezione "Integrazioni da figure" (voci F1-F17) prima della sezione finale. Termini DCS lasciati in inglese. Dove il manuale non dice un valore lo si scrive esplicitamente ("non specificato").

Nota di lettura: il manuale e' una guida all'interfaccia del Mission Editor (ME). Molte schermate sono solo contorno; le informazioni utili sono quasi tutte nel testo. Le schermate mostrano la forma dei pannelli (campi, checkbox) ma non aggiungono valori numerici nascosti, tranne la Route Summary (p. 294, esempio: START TIME 8:0:0/1, ROUTE TIME 0:41:47/1, ROUTE LENGTH 28 km, AVERAGE SPEED 40 kmh).

---

## 1. Place Ship Group (pp. 287-295)

Gruppo navale: da 1 a 99 navi per gruppo ("non raccomandato" averne molte), a differenza dei gruppi aerei (p. 287). Il piazzamento e' automaticamente limitato a "large bodies of water" (p. 287). Copia/incolla gruppo con CTRL+C / CTRL+V.

### 1.1 Pannello del gruppo (pp. 287-289)

| Campo | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| NAME | testo, univoco | generato automaticamente | Usato dai Trigger (es. Activate Unit). Non assegnare lo stesso nome a due gruppi (p. 287) |
| CONDITION | espressione Lua (Simulator Scripting Engine) | vuoto | Condizione di spawn casuale del gruppo; lo script di inizializzazione va caricato nel pannello trigger, viene eseguito prima del caricamento missione (p. 288) |
| COUNTRY | paesi assegnati a RED/BLUE alla creazione missione | - | Filtra i TYPE di nave disponibili (p. 288). Il country determina anche la coalizione |
| UNIT | due campi: indice nave corrente / numero totale navi (1-99) | non specificato | p. 288 |
| TYPE | elenco navi dipendente dal country | - | p. 288 |
| UNIT NAME | testo, univoco per unita' | generato | Usato nelle condizioni trigger basate su unita' (es. unita' distrutta) (p. 288) |
| SKILL | Average / Good / High / Excellent / Random (Random sceglie fra i 4 precedenti) | non specificato | Influenza raggi di rilevamento, tempi di reazione, errori di puntamento (p. 288). Il testo parla di "pilota" ma e' la stessa descrizione dei gruppi aerei |
| HEADING | dial, gradi | non specificato | Rotta di stazionamento quando non c'e' route (p. 288) |
| HIDDEN ON MAP | checkbox | off | Nasconde il gruppo dalla World Map del ME; visibile con Units List (p. 288) |
| HIDDEN ON PLANNER | checkbox | off | Nasconde dal mission planner (p. 288) |
| VISIBLE bef. ACTIVATION | checkbox | non specificato | Con Activate Group/Unit trigger: se spuntato il gruppo e' visibile ma inattivo prima dell'attivazione (p. 288) |
| GAME MASTER ONLY | checkbox | off | Gruppo disponibile solo al game master (p. 289) |
| LATE ACTIVATION | checkbox | off | Il gruppo viene generato dopo una condizione/evento (p. 289) |
| FREQUENCY | MHz + modulazione (esempio: 127.5 MHz AM) | non specificato | Frequenza radio del gruppo AI (p. 289) |

Cinque modal button: ROUTE, AMMO, TRIGGERED ACTIONS, SUMMARY, SUPPLIERS (p. 289). I gruppi terrestri ne hanno 4 (manca SUPPLIERS, p. 305).

### 1.2 Route Mode (pp. 289-292)

Waypoint = punto arbitrario (Lat/Long) concatenato in route; il gruppo "steers" da un waypoint al successivo (p. 289). Il primo click sulla mappa piazza il gruppo = waypoint 1. Colori marker/linea: bianco = selezionato, rosso = unita' RED non selezionata, blu = unita' BLUE non selezionata (p. 289). Al waypoint 1 c'e' un'icona del tipo di unita' (set icone navali Russian/NATO: Submarine, Frigate, Aircraft carrier, Heavy cruiser, Cruiser, Medium ship/frigate, Cargo (commercial) ship, pp. 289-290). Trascinando il leader si sposta tutto il gruppo; trascinando una nave si regola la sua posizione relativa al leader (p. 290).

| Campo waypoint | Valori / unita' | Default | Note |
|---|---|---|---|
| WAYPOINT | indice corrente / totale | - | Navigazione fra waypoint; il selezionato e' giallo (p. 291) |
| NAME | testo | vuoto | Mostrato sulla mappa (p. 291) |
| TYPE | per le navi solo "Turning Point" | Turning Point | Il gruppo passa e prosegue (p. 291). Nessun tipo di formazione (a differenza dei terrestri) |
| ALTITUDE | non regolabile per i gruppi navali | - | p. 291 |
| SPEED | km/h (attenzione: km/h, non nodi) | non specificato | Velocita' che il gruppo avra' raggiunto al waypoint; il massimo di gruppo non supera quello della nave piu' lenta (p. 291) |
| GS (ground speed lock) | checkbox | non applicabile al waypoint iniziale | Se bloccata, il gruppo cerca di tenere la velocita' sul tratto dal waypoint precedente (p. 291) |
| START/ETA | Hour:Minute:Second/Day (es. 12:15:00/1) | calcolato dal ME se non bloccato | Per il wp 1 e' l'orario di start del gruppo (p. 291) |
| Fix Time (ETA lock) | checkbox | bloccato per il wp iniziale | Se bloccato l'ETA e' input utente; se sbloccato lo calcola il ME (p. 291) |

Attivazione ritardata tramite ETA del wp 1: se missione parte alle 12:00:00/1 e ETA wp1 = 12:15:00/1 il gruppo appare dopo 15 minuti; ETA = 12:00:00/100 (100 giorni dopo) = il gruppo non appare finche' non lo attiva un trigger (pp. 291-292). Se ETA implica una velocita' troppo bassa/alta per il tipo di unita', il testo diventa rosso e viene dato un errore alla chiusura del pannello o al salvataggio (p. 292).

Waypoint Mode Buttons (p. 292): ADD (default quando il pannello e' aperto; ogni click aggiunge un waypoint), EDIT, DEL.

### 1.3 Ammo Mode (p. 292)

ATTENZIONE: nonostante il nome, l'AMMO button apre il "LOADOUTS EDITOR" che per le navi (e per i veicoli, p. 311) serve solo a scegliere lo "color scheme" (livrea/paint scheme) dell'unita'. NON c'e' alcuna definizione di munizioni per nave o veicolo in questa porzione: la schermata (p. 311) mostra il modello 3D del veicolo e il campo PAINT SCHEME = Default. Le munizioni delle unita' terrestri sono fisse per tipo di unita' e riforniti da supply vehicle (sez. 3.7).

### 1.4 Triggered Actions e Route Summary (pp. 293-294)

- Triggered Actions: pannello analogo alle Advanced Actions ma attivato da trigger con l'azione AI TASK del menu Triggers (p. 293).
- Route Summary (p. 294): START TIME (Hour:Minute:Second/Day), ROUTE TIME (tempo stimato, h:m:s/Day), ROUTE LENGTH (km totali), AVERAGE SPEED (media delle velocita' assegnate ai tratti diviso il numero di tratti: media semplice, non pesata sulla distanza; p. 294). Sono valori derivati, sola lettura.

### 1.5 Suppliers (pp. 294-295)

Pannello informativo con i fornitori di munizioni del gruppo navale (p. 294). Pulsanti: FULL INFO (apre il Resource Manager), ADD (aggiunge un warehouse: tutti i gruppi navali e gli aeroporti vengono marcati con checkbox; quelli spuntati diventano supplier, e il ME disegna linee con freccia dal supplier al gruppo navale), DEL (rimuove i supplier selezionati) (p. 295). Il manuale non spiega raggio, quantita' o logica di consumo qui: il rifornimento navale e' una relazione gruppo-fornitore (nave/aeroporto) gestita attraverso il Resource Manager (che non e' in questa porzione). Valori non specificati.

---

## 2. Advanced Actions Mode - gruppi navali (pp. 296-302)

Pannello che elenca le azioni del waypoint selezionato (Perform Task, Start Enroute Task, Perform Command, Set Option), aggiunte dall'utente o generate automaticamente dal ME (p. 296). Pulsanti: ADD (crea un "No Task" di default), INS (inserisce sopra la selezione), EDIT (apre il popup Action Settings; stesso effetto del click su un waypoint), DEL, UP, DOWN, CLONE (p. 296). Ogni azione ha anche condizioni di start/stop (p. 297). Le azioni disponibili differiscono da quelle aeree (p. 297).

### 2.1 Perform Task (pp. 297-299)

| Task | Parametri | Note |
|---|---|---|
| No Task | - | Nessuna azione (p. 297) |
| Fire at Point | ZONE RADIUS (m, non specificato il default), WEAPON (menu dipendente dalle armi della nave), ROUNDS EXPEND (flag + numero intero di colpi/lanci consumabili, esempio 3, da figura p. 297; vedi F6) | Punto = marker triangolare da trascinare sulla mappa. Artiglieria: i colpi sono distribuiti su tutta l'area della zona; missili da crociera: bersaglio = coordinata centrale (pp. 297-298) |
| Attack Group | GROUP (gruppo bersaglio aria/terra/mare), WEAPON, REL QTY (quota di payload autorizzata), MAX ATTACK QTY (max numero di attacchi), GROUP ATTACK (checkbox), DIRECTION FROM (azimut di avvicinamento) | L'attacco termina se il bersaglio e' distrutto anche prima di raggiungere MAX ATTACK QTY; termina anche se il bersaglio non e' colpito entro il numero di attacchi. Default per GROUP ATTACK: una nave per bersaglio. Bersaglio marcato con marker triangolare e linea dal waypoint (pp. 298-299) |

Il manuale non elenca altri task navali (nessun Attack Unit, Orbit, ecc. in questa porzione).

### 2.2 Start Enroute Task (p. 299)

Navi: nessun Enroute Task disponibile, solo "No Enroute Task". DIFFERENZA forte con l'aereo (Search Then Engage, Refueling, AWACS, FAC...).

### 2.3 Perform Command (pp. 299-300)

Disponibili per le navi: No Action, Run Script (script Lua dallo scratchpad), Script File (file Lua), Invisible (invisibile alle unita' AI nemiche; checkbox ENABLE), Immortal (rilevabile ma le armi nemiche non hanno effetto). Assenti rispetto agli aerei: Set Frequency, Transmit Message, Switch Waypoint, EPLRS, Smoke, ecc. (nella lista navale di p. 299-300 non compaiono).

### 2.4 Set Option (pp. 300-302)

| Opzione | Valori | Default | Note |
|---|---|---|---|
| ROE | WEAPON FREE (ingaggia qualunque gruppo nemico in contatto, priorita' automatica); RETURN FIRE (solo risposta); WEAPONS HOLD (mai fuoco) | WEAPON FREE | Mancano rispetto all'aereo "Priority designated" e "Only designated" (default aereo: Only designated). Le opzioni agiscono indipendentemente dal task attivo; senza opzioni nella lista valgono i default (p. 301) |
| Alarm State | Auto / GREEN / RED | Auto | Auto: passa dalla modalita' di navigazione all'allerta di combattimento quando rileva un nemico e ritorna alla navigazione se non ce ne sono. GREEN: non pronto al combattimento, sensori e armi stivati. RED: pronto, armi e sensori pronti al fuoco, ricerca attiva dei bersagli (pp. 301-302) |

---

## 3. Place Ground Unit (pp. 303-325)

Gruppo terrestre = da 1 a 99 veicoli. Alla minima zoom si vede solo il leader. I SAM battery (SA-10, SA-11, ecc.) devono avere TUTTE le unita' necessarie nello stesso Vehicle Group (p. 304). Un JTAC richiede un'unita' armata e con sensori (es. HMMWV armato) (p. 304).

### 3.1 Pannello del gruppo (pp. 303-305)

| Campo | Valori / unita' | Default | Note |
|---|---|---|---|
| NAME | testo univoco | generato | Usato da trigger (Activate Unit) (p. 303) |
| CONDITION | espressione Lua | vuoto | Spawn casuale, come per le navi (p. 304) |
| COUNTRY | paesi RED/BLUE | - | Filtra i TYPE (p. 304) |
| UNIT | indice / totale (1-99) | non specificato | p. 304 |
| CATEGORY | Air Defence, Armor, Artillery, Fortification, Infantry, Missiles, Train, Unarmed | non specificato | Specifico dei terrestri (p. 304). "Unarmed" e' una categoria, non un flag |
| TYPE | elenco dipendente dal country | - | p. 304 |
| UNIT NAME | testo univoco | generato | Per condizioni trigger (p. 304) |
| SKILL | Average / Good / High / Excellent / Random | non specificato | Influenza raggio di attacco/precisione, rilevamento, reazione, errori di puntamento. Nota: i velivoli AI hanno grande difficolta' a individuare la fanteria a meno che si muova o spari (pp. 304-305) |
| HEADING | dial gradi | non specificato | Orientamento a riposo senza route (p. 305) |
| HIDDEN ON MAP / HIDDEN ON PLANNER | checkbox | off | come navi (p. 305) |
| VISIBLE before ACTIVATION | checkbox | non specificato | p. 305 |
| LATE ACTIVATION | checkbox | off | p. 305 |
| GAME MASTER ONLY | checkbox | off | p. 305 |
| PLAYER CAN DRIVE | checkbox | non specificato | Il giocatore guida le unita' con RAlt+J (p. 305). Solo terrestri |
| TRANSPORTABLE | checkbox | non specificato | Fanteria, trasporto, corazzati e cargo trasportabili da elicottero (p. 305). Solo terrestri |

Non esiste un campo FREQUENCY nel pannello terrestre (si imposta con il comando Set Frequency, sez. 4.3).

Quattro modal button: ROUTE, AMMO, TRIGGERED ACTIONS, SUMMARY (p. 305).

### 3.2 Route Mode e icone (pp. 305-308)

Come per le navi: il primo click piazza il gruppo (wp 1), colori bianco/rosso/blu. Icone unita' al wp 1 (Russian/NATO): Tank, IFV, Combat reconnaissance vehicle, APC, Transport, Civilian vehicle, Engineers, SPG, MLRS (leggero/medio/pesante), ATGM tracked/wheeled, FAC vehicle, Infantry, MANPAD SAM, Stinger SAM, AAA (self-propelled, radar-guided, wheeled, tracked), SAM short range (wheeled/tracked, anche radar-guided), SAM medium range (tracked/wheeled/radar-guided), SAM long range (tracked radar-guided/wheeled), Avenger, M6 Linebacker, Chaparral, M-163 Vulcan, Mobile radar, Radio-navigation beacon, Stationary radar, Air controller, Air defense direction center, Battle command center, FAC, Command center, Bunker, Checkpoint, Storage, Fuel depot, Structure (building) (pp. 306-308). Questo elenco e' di fatto una tassonomia dei ruoli terrestri usata dal ME.

### 3.3 Waypoint terrestri (pp. 309-310)

| Campo | Valori / unita' | Default | Note |
|---|---|---|---|
| WAYPOINT, NAME | come navi | - | p. 309 |
| TYPE | Offroad (in fila indiana, uno davanti all'altro); On road (il waypoint si aggancia alla strada piu' vicina; fra due On Road consecutivi il ME traccia il percorso sulla rete stradale; evitare gli incroci; tenere almeno 500 m fra gruppi sulla stessa strada); Line Abreast; Cone; Vee; Diamond; Echelon Left; Echelon Right; Custom (template scelto da menu, creati con Templates Menu) | non specificato (nelle schermate p. 343 appare "Off road") | Il TYPE del waypoint e' contemporaneamente tipo di movimento E formazione che il gruppo assume (p. 309). Nota: il tipo "Rank" citato nella richiesta NON compare in questa porzione; i tipi sono solo quelli elencati |
| ALTITUDE | non regolabile; mostra la quota del waypoint (terreno) | - | p. 309 |
| SPEED | km/h | non specificato | Velocita' per raggiungere il waypoint successivo (p. 310). Nelle navi: velocita' raggiunta AL waypoint |
| GS (lock) | checkbox | n/a per wp iniziale | p. 310 |
| START/ETA e Fix Time | Hour:Minute:Second/Day | ETA bloccato sul wp 1 | Stessa logica e stesso trucco dei 100 giorni delle navi (p. 310). Errore rosso se la velocita' implicita e' fuori dai limiti (p. 310; il testo dice "aircraft type", refuso del manuale) |

Waypoint Mode Buttons: ADD / EDIT / DEL (p. 310).

Consigli tattici del manuale (pp. 310-311): il fuoco in movimento e' meno preciso; ogni veicolo ha corazza diversa per fronte, lati, retro, sommita' (tenere il fronte verso il nemico); formazioni Line Abreast / Echelon puntano piu' canne sul nemico; studiare la line of sight del terreno per decidere cosa e' rilevabile.

### 3.4 Ammo Mode (p. 311)

Vedi sez. 1.3: solo selezione PAINT SCHEME (colore/livrea) nel LOADOUTS EDITOR. Le munizioni NON sono configurabili qui.

### 3.5 Triggered Actions e Route Summary (pp. 311-312)

Uguali alle navi. Route Summary: START TIME, ROUTE TIME (tempo di viaggio a velocita' data), ROUTE LENGTH (km), AVERAGE SPEED (p. 312).

### 3.6 Supporto a terra di aeroporti e FARP (pp. 313-315)

Nei FARP le risorse a terra sono tracciate per stabilire il livello di supporto fornibile a giocatore e AI: ground power, comunicazioni radio, carburante, armamento (p. 313). I veicoli di supporto devono stare entro 150 m dal centro del FARP (dimensione FARP circa 200x200 m) (pp. 313-314). Se un'unita' richiesta manca o e' distrutta, la risorsa corrispondente non e' disponibile; si puo' prevedere un trigger che sposti nuovi veicoli entro 150 m (p. 314).

| Servizio | Unita' richieste RED | Unita' richieste BLUE | Condizioni |
|---|---|---|---|
| Airfield, ATC | Tower | Tower | Non distrutta |
| Airfield, ground crew, rearming, refueling, ground power, aircraft repair | non richieste | non richieste | La riparazione avviene automaticamente 3 minuti dopo l'arresto dei rotori (eliche) |
| FARP, ATC | CP SKP-11 ATC, FARP Command Post | APC M1025 HMMWV, FARP Command Post | Entro 150 m dal centro |
| FARP, rearming | GAZ-3308, GAZ-66, KAMAZ-43101, KrAZ-6322, Ural-375 KUNG, Ural-375, Ural-4320-09-31, Ural-4320T, FARP Ammo Storage | M818, FARP Ammo Storage | Entro 150 m |
| FARP, refueling | ATMZ-5, ATZ-10, FARP Fuel Depot | Tanker M978 HEMTT, FARP Fuel Depot | Entro 150 m |
| FARP, ground power | GPU APA-5D, GPU APA-80 | M818 | Entro 150 m |
| FARP, night lighting | CP SKP-11 ATC | APC M1025 HMMWV | Entro 150 m |
| FARP, repair | UAZ-469, Ural-4320-09-31, Ural-4320T, ZIL-131 KUNG, KAMAZ-43101, FARP Tent | M818, FARP Tent | Entro 150 m; riparazione 3 min dopo arresto rotori |

Esempio: per comunicazioni radio e corrente al FARP servono almeno due veicoli (CP SKP-11 + un APA per RED; M1025 HMMWV + M818 per BLUE) (p. 314). Negli aeroporti, rearm/refuel/ground power NON dipendono dai veicoli; dipende dalla torre solo la comunicazione per richiederli; se la torre e' distrutta si ripristina con SKP-11 (RED) o HMMWV M1025 (BLUE) (p. 314). Le pp. 314-315 mostrano esempi di "service column" RED e BLUE (colonne di servizio con scorta); contenuto in immagine, composizione non leggibile come testo.

### 3.7 Ammo supply for ground units (pp. 316-325) - sezione chiave

Regole (p. 316):
- Le unita' terrestri (difesa aerea, missili, semoventi, IFV, carri) che esauriscono le munizioni possono essere rifornite da supply vehicle.
- I supply vehicle sono "unlimited warehouses" (magazzino illimitato): niente scorte da modellare.
- Possono far parte sia di gruppi statici (siti SAM) sia di gruppi mobili (convogli di semoventi o corazzati). Un gruppo puo' avere piu' supply vehicle.
- Un supply vehicle rifornisce tutte le unita' entro 200 m da se'. Fuori dai 200 m niente rifornimento: il mission designer deve tenerne conto in colonne lunghe.
- Il tempo di rifornimento dipende dal tipo di unita' (tabelle sotto) e comprende spostamento di lanciatori/munizioni, sostituzione e collegamento (p. 318).
- Non e' dichiarato nel manuale un tempo di reazione/avvio, ne' se piu' unita' sono rifornite in parallelo o in serie (supposto parallelo per il testo "all units within 200 m", ma non specificato).

Supply vehicle riconosciuti (p. 316), condizione per tutti: entro 200 m dal veicolo:

| Veicolo | Paese |
|---|---|
| GAZ-3308, GAZ-66, KAMAZ-43101, Ural-375 KUNG, Ural-375, Ural-4320-09-31, Ural-4320T | Russia |
| KrAZ-6322 | Ukraine |
| M818 | USA |

Esempi di disposizione (pp. 317-318, solo immagini): 1) un supply vehicle ogni 4 semoventi in colonna; 2) un supply vehicle per ogni lanciatore a un sito Patriot; 3) un supply vehicle per tutti i lanciatori a un sito S-300PS.

Tempi di rifornimento da supply vehicle, in secondi (pp. 318-325). Per le armi multiple si indica una riga per arma (il valore e' il tempo di rifornimento di quell'arma):

SAM e AAA (pp. 318-319)

| Sistema | Arma | Secondi |
|---|---|---|
| SA-19 Tunguska 2S6M | cannoni 2x30 mm / missili | 2400 / 960 |
| SA-6 Kub LN 2P25 | missili | 1800 |
| SA-3 S-125 LN 5P73 | missili | 600 |
| SA-10 S-300PS LN 5P85C(D) | missili | 7200 |
| SA-8 Osa 9A33 | missili | 1800 |
| SA-9 Strela-1 9P31 | missili | 1200 |
| SA-13 Strela-10M3 9A35M3 | missili | 960 |
| SA-11 Buk LN 9A310M1 | missili | 780 |
| SA-15 Tor 9A331 | missili | 1080 |
| Patriot LN M901 | missili | 3600 |
| SPAAA Gepard-1A2 | cannoni 2x35 mm | 1800 |
| Hawk LN M192 | missili | 420 |
| SA-18 Igla MANPADS | missili | 120 |
| Linebacker M6 | missili / cannone 25 mm | 200 / 880 |
| Chaparral M48 | missili | 360 |
| Vulcan M163 | cannone 20 mm | 1200 |
| Avenger M1097 | missili | 400 |
| Roland ADS | missili | 300 |
| Stinger MANPADS | missili | 120 |
| SPAAA ZSU-23-4 Shilka | cannoni 4x23 mm | 20 |
| ZU-23 Emplacement / Closed / on Ural-375 | cannoni 2x23 mm | 60 (ciascuno) |

MLRS (p. 320)

| Sistema | Arma | Secondi |
|---|---|---|
| 9K51 Grad BM-21 | razzi 40x122 mm | 420 |
| 9K57 Uragan BM-27 | razzi 16x220 mm | 840 |
| 9A52 Smerch | razzi 12x300 mm | 2160 |
| M270 MLRS | razzi 12x227 mm | 560 |

Obici e mortai (p. 320)

| Sistema | Arma | Secondi |
|---|---|---|
| 2B11 Mortar | tubo 120 mm | 30 |
| 2S1 Gvozdika | cannone 122 mm | 940 |
| 2S3 Akatsia | cannone 152 mm | 1186 |
| 2S9 Nona-S | cannone 120 mm | 500 |
| 2S19 Msta-S | cannone 152 mm / mitragliatrice 12,7 mm | 1080 / 110 |
| M109 Paladin | cannone 155 mm | 936 |
| SpGH vz.77 Dana | cannone 152 mm | 1488 |

IFV/APC (pp. 321-323), tempi per arma in secondi

| Veicolo | Armi: secondi |
|---|---|
| AAV7 | lanciagranate 40 mm 210; MG 12,7 mm 90 |
| BMD-1 | cannone 73 mm 600; ATGM Malutka 80; MG 3x7,62 60 |
| BMP-1 | cannone 73 mm 600; ATGM Malutka 80; MG 7,62 60 |
| BMP-2 | cannone 30 mm 1800; ATGM Konkurs 120; MG 7,62 600 |
| BMP-3 | cannone 30 mm 1800; cannone 100 mm 710; ATGM Kastet 120; MG 3x7,62 600 |
| MT-LB | MG 7,62 150 |
| BRDM-2 | MG 14,5 230; MG 7,62 140 |
| BTR-80 | MG 14,5 230; MG 7,62 140 |
| BTR-RD | ATGM Konkurs 125; MG 2x7,62 60 |
| Cobra | MG 12,7 100 |
| LAV-25 | cannone 25 mm 1200; MG 2x7,62 480 |
| M2A2 Bradley | cannone 25 mm 240; ATGM TOW 140; MG 7,62 480 |
| M113 | MG 12,7 75 |
| M1043 HMMWV | MG 12,7 75 |
| M1045 HMMWV | ATGM TOW 180 |
| M1126 Stryker ICV | MG 12,7 125 |
| M1134 Stryker ATGM | ATGM TOW 280; MG 7,62 "-" (nessun tempo) |
| Marder | cannone 20 mm 2000; MG 7,62 400 |
| MCV-80 Warrior | cannone 20 mm 380; MG 7,62 75 |
| TPz 1 Fuchs | MG 7,62 120 |
| ZBD-04A | cannone 30 mm 1800; cannone 100 mm 710; ATGM Kastet 120; MG 7,62 600 |

Carri (pp. 323-325): per i cannoni principali sono indicati due tempi AP/HE (seconda cifra = HE). Voce "-" = nessun tempo indicato.

| Carro | Cannone (AP / HE) | Altre armi |
|---|---|---|
| Challenger 2 | 120 mm 450 / 440 | MG 7,62 - |
| Leclerc | 120 mm 530 / 230 | MG 7,62 - |
| Leopard 1A3 | 105 mm 515 / 290 | MG 7,62 40 |
| Leopard 2A5 | 120 mm 400 / 275 | MG 7,62 126 |
| M1A2 Abrams | 120 mm 400 / 260 | MG 12,7 90; MG 7,62 580 |
| M1128 Stryker MGS | 105 mm 260 / 140 | MG 12,7 95; MG 7,62 500 |
| Merkava Mk.4 | 120 mm 465 / 300 | MG 2x7,62 545 |
| T-55 | 100 mm 495 / 184 | MG 12,7 110; MG 7,62 - |
| T-72B | 125 mm 416 / 308 | ATGM Refleks 130; MG 12,7 110; MG 7,62 - |
| T-80U | 125 mm 406 / 316 | ATGM Refleks 120; MG 12,7 150; MG 7,62 - |
| T-90A | 125 mm 408 / 310 | ATGM Refleks 130; MG 12,7 50; MG 7,62 - |

Nota di interpretazione: i numeri sono chiamati "Supply ammo time from a supply vehicle (warehouse), sec." Il manuale NON dichiara le dimensioni dei caricatori (colpi per arma); la tabella dice solo quanto tempo serve a ricaricare quell'arma. I valori sono in secondi (es. S-300PS 7200 s = 2 ore).

---

## 4. Advanced Actions Mode - gruppi terrestri (pp. 326-345)

Stessi controlli e stessa struttura del pannello navale/aereo: ADD, INS, EDIT, DEL, UP, DOWN, CLONE (p. 326). Le azioni disponibili sono diverse da quelle degli aerei (p. 327). Ogni azione ha condizioni di start/stop (sezione "CONDITION..." e "STOP CONDITION...", visibili nelle schermate di pp. 330, 343).

### 4.1 Perform Task (pp. 327-333)

| Task | Parametri | Note |
|---|---|---|
| No Task | - | p. 327 |
| FAC - Assign Group | GROUP (gruppo nemico bersaglio), WEAPON (armi che il FAC chiedera' agli attaccanti), DESIGNATION (Auto, smoke "Willy Pete" WP, IR-Pointer, Laser, WP-Laser; effettuata su richiesta radio del giocatore a raggio fisso), DATALINK, CALLSIGN, NUMBER, FREQUENCY (MHz), MODULATION (AM/FM) | Il FAC dovrebbe essere un veicolo armato con LOS diretta al bersaglio entro pochi km. Assume piena conoscenza della situazione: la posizione del bersaglio e' sempre nota. Dirige solo contro il gruppo designato. L'azione inizia quando unita' amiche arrivano e stabiliscono comunicazione. Il menu mostra la distanza massima di designazione per ogni apparato; se il FAC e' piu' lontano il designatore non funziona. Messaggio "problem: no LOS" se il bersaglio e' oscurato dal terreno. DATALINK: solo unita' con EPLRS abilitato possono trasmettere la posizione via datalink ad aerei compatibili (pp. 327-329) |
| Fire at Point | ZONE RADIUS (m; non specificato il default), WEAPON (dipende dal veicolo), ROUNDS EXPEND (flag + quantita') | Marker triangolare da trascinare. Artiglieria: spara su tutta la zona; missili: colpiscono solo il centro (p. 330). Nessun parametro "raggio massimo" o "numero di colpi" numerico documentato oltre il flag |
| Hold | formazione personalizzabile nel Lower Action Properties Panel | Si ferma nel punto del waypoint e mantiene la posizione finche' l'azione e' attiva. Utile per pattuglie fisse o fuoco di artiglieria (una batteria puo' tenere la "fire mission formation") (p. 331) |
| Embark to Transport (work in progress) | VEHICLE GROUP (gruppo veicolo di trasporto), ZONE RADIUS (m, raggio dell'area di imbarco delle squadre) | Solo gruppi di categoria INFANTRY. Ogni squadra deve avere il task Embark to transport e il flag TRANSPORTABLE nel pannello gruppo (pp. 331-332). Il manuale non descrive Disembark in questa porzione |
| Go to Waypoint | TO WAYPOINT (waypoint di destinazione) | Il gruppo segue la route fino al waypoint indicato (pp. 332-333) |

Non compaiono task terrestri di attacco (Attack Group/Unit) in questa porzione: il combattimento terrestre e' governato da ROE/Alarm State e dalla presenza di nemici, oltre a Fire at Point.

### 4.2 Start Enroute Task (pp. 333-337)

| Task | Parametri | Note |
|---|---|---|
| No Enroute Task | - | p. 333 |
| FAC | CALLSIGN, NUMBER, FREQUENCY (MHz), MODULATION (AM/FM) | Il FAC dirige per priorita' automatica; la scelta dei bersagli puo' non coincidere con quella voluta dal designer (pp. 333-334) |
| FAC - Engage Group | GROUP, VISIBLE (se conosce la posizione del bersaglio a inizio missione), WEAPON, PRIORITY (0 = massima), DESIGNATION, DATALINK, CALLSIGN, NUMBER, FREQUENCY, MODULATION | Il FAC deve rilevare da solo il gruppo (dipende da terreno, meteo...); senza gruppo designato non emette ordini. Solo unita' armate possono designare con fumo e laser (es. HMMWV armato). Stessi vincoli LOS e distanza massima di designazione di FAC - Assign Group (pp. 334-337) |

DIFFERENZA con l'aereo: niente Search Then Engage / in Zone / Group / Unit, Refueling, AWACS (p. 259-270 sezione aerea). Il FAC terrestre e' disponibile come task e come enroute task.

### 4.3 Perform Command (pp. 338-342)

| Comando | Parametri | Note |
|---|---|---|
| No Action | - | p. 338 |
| Run Script / Script File | script Lua / file | p. 338 |
| Set Callsign | callsign (per i Western: nome + ID numerico, es. "Warrior 4") | p. 338 |
| Set Frequency | FREQUENCY (MHz), MODULATION (AM/FM), POWER (W, esempio 10 W, da figura, p. 339) | p. 339 |
| Transmit Message | FILE (audio .ogg/.wav), SUBTITLE (testo), LOOP (ripetizione), DURATION (s) | Dal gruppo leader (pp. 339-340) |
| Stop Transmission | nessuna opzione | p. 340 |
| Go to Waypoint | waypoint di destinazione (default: il successivo) | Il gruppo va direttamente dal waypoint corrente a quello indicato, anche all'indietro; i task, comandi e opzioni dei waypoint saltati non vengono eseguiti; permette rotte circolari (es. dopo WPT 2 tornare a WPT 0), limitabili con CONDITION (es. un limite di tempo) (pp. 340-341). Equivale a "Switch Waypoint" dell'aereo |
| Invisible | ENABLE | Invisibile a tutte le unita' AI nemiche; utile per FAC terrestri vicini al nemico, per simulare una posizione mimetizzata (p. 341) |
| Immortal | ENABLE | Rilevabile, ma le armi nemiche non hanno effetto; utile per scenari di scontro prolungato (p. 341) |
| EPLRS | ENABLE (on/off) | Abilita il sistema EPLRS e la trasmissione dei dati agli altri del gruppo (p. 342). Necessario per il datalink FAC |

Non presente per i terrestri: Smoke On_Off (aereo, p. 275).

### 4.4 Set Option (pp. 343-345)

| Opzione | Valori | Default | Note |
|---|---|---|---|
| ROE | WEAPON FREE; RETURN FIRE; WEAPONS HOLD | WEAPONS FREE | p. 343. Come per le navi, senza Priority/Only designated (default aereo: Only designated) |
| Disperse Under Fire | Allow / non allow; durata dispersione in secondi (esempio 600 s, da figura p. 344) | Allow | Se attivo, il gruppo si disperde quando una sua unita' e' distrutta o danneggiata; dopo la durata indicata (s) torna in formazione e riprende la route. Se non attivo, il gruppo continua in formazione sotto il fuoco (pp. 343-344). Il valore di durata di default non e' leggibile |
| Alarm State | Auto / GREEN / RED | Auto | Auto: non e' pronto finche' non si rileva la presenza del nemico (l'AI puo' "percepirla" senza rilevarla con i propri sensori). GREEN: non pronto, nessuna ricerca ne' ingaggio, sensori spenti/stivati se possibile. RED: pronto e in ricerca attiva; a seconda dell'unita' puo' o non puo' muoversi in stato di allerta di combattimento (pp. 344-345) |
| Engage Air Weapons | checkbox (consenti/vieta) | non specificato | Permette al gruppo terrestre di intercettare e distruggere armi lanciate da aerei durante l'avvicinamento al bersaglio (p. 345) |

Mancano rispetto all'aereo: Reaction to Threat, Radar Using, Chaff/Flare, Formation (qui la formazione e' il TYPE del waypoint), RTB on Bingo/out of ammo, Silence, ECM Using, Restrict *, AA Missile attack ranges, Radio usage, No Report Waypoint Pass (tutte nella sezione aerea pp. 276-286).

---

## 5. Place Static Object (pp. 346-347)

Gli oggetti statici condividono il modello esterno degli oggetti attivi, ma sono immobili e non usano sensori ne' armi. Un solo oggetto per gruppo (p. 346).

| Campo | Valori | Default | Note |
|---|---|---|---|
| NAME | testo univoco | generato | Usato da trigger (es. Unit Dead) (p. 346) |
| COUNTRY | paesi RED/BLUE della missione | - | p. 347 (la schermata mostra USA) |
| CATEGORY | Airfield and deck equipment; Animals; Cargos (carichi per elicotteri); Effects (fumi); Ground Vehicles; Helicopters; Heliports (FARP: con CALLSIGN a menu e FREQUENCY in MHz); Planes; Sea Shelf Objects (piattaforme petrolifere/gas); Ships; Structures (bunker e vari edifici militari e civili); Warehouses (magazzini e serbatoi) | - | Il testo dice "six general categories" ma ne elenca dodici (p. 347) |
| TYPE | dipende dalla categoria | - | p. 347 |
| HEADING | gradi (dial, frecce o testo) | non specificato | p. 347 |
| HIDDEN | checkbox | off | Nasconde dalla World Map e dalla mappa di briefing (p. 347) |
| HIDDEN ON PLANNER | checkbox | off | p. 347 |
| DEAD | checkbox | off | Popola il mondo con la versione distrutta dell'oggetto (p. 347) |
| PAINT SCHEME | scelta della livrea | Default | p. 347 |

Nessuna route, nessuna azione, nessuna skill, nessun trigger action per gli statici. Il FARP e' definito come static (Heliport) con callsign e frequenza; il suo supporto dipende dai veicoli entro 150 m (sez. 3.6).

---

## 6. Place Initial Point (A-10C only) (pp. 348-349)

Punto di navigazione per il sistema dell'A-10C del giocatore. Campi: COALITION, CALLSIGN (uno di 8 ID disponibili), COMMENT (visibile sulla mappa ME), SCALE, STEER, VNAV, VANGLE, ANGLE (questi ultimi cinque sono specifici del sistema di navigazione e "non hanno funzione nell'A-10C" secondo il manuale; ANGLE vale con VNAV=3D e VANGLE=ENTERED) (pp. 348-349). Valori ammessi di SCALE/STEER/VNAV/VANGLE non specificati. Irrilevante per la campagna AI.

## 7. Place Bullseye (p. 349)

Un solo Bullseye per coalizione (punto di riferimento per comunicare posizioni). Si sposta trascinandolo; la finestra mostra la coalizione e le coordinate mondo correnti. Dato di missione: coordinate per coalizione.

## 8. Create Area Trigger Zone (pp. 350-351)

Zona per condizioni trigger (unita' che entra/esce). Posizionabile ovunque, di qualunque dimensione e colore; tutte le zone sono circolari (p. 350). Puo' essere assegnata a un'unita' mobile (la zona si muove con essa) o a una struttura al suolo (click destro su un edificio, "assign as ...") (pp. 350-351).

| Campo | Valori | Default | Note |
|---|---|---|---|
| NAME | testo | generato | Usato nelle condizioni trigger (p. 350) |
| RADIUS | metri | non specificato | p. 350 |
| COLOR | 28 colori predefiniti oppure RGB + A (alpha, trasparenza) personalizzati | non specificato | Solo estetico (p. 351) |
| HIDDEN | checkbox | off | Nasconde la zona ai giocatori (p. 351) |

## 9. Create Unit Template (pp. 352-353)

Salva la composizione di un gruppo terrestre (es. batteria di artiglieria con munizionamento, comando, APC di sicurezza; sito SA-10) per riutilizzarla; utile con l'azione STOP AND DEPLOY TO TEMPLATE del menu Trigger (p. 352). Procedura: crea gruppo, posiziona le unita', pulsante Create and Modify Templates, scegli COUNTRY, verifica SELECTED GROUP, inserisci TEMPLATE NAME, SAVE TEMPLATE. Salvataggio in `Saved Games\DCS\MissionEditor\templates.lua` (p. 352). Per il piazzamento: scelta country, scelta template, click sulla mappa, HEADING (gradi) (p. 353). I template sono per country e sono usati come TYPE "Custom" nei waypoint terrestri.

## 10. Area Trigger Zone List, Unit List, Delete, Map Options, Distance Tool, Exit (pp. 354-357)

- Area Trigger Zone List (pp. 354-355): elenco zone con colonne NAME, STATE (vuoto o HIDDEN), RADIUS (m). Pulsanti: Show All, Hide All, Toggle Selection. Interfaccia pura.
- Unit List (pp. 355-356): elenco gruppi attivi e statici con filtri (Show Hidden Units, Helicopters, Planes, Vehicles, Ships, Statics). Sette colonne: GROUP NAME, UNIT NAME, UNIT TYPE, UNIT ID, COUNTRY, STATUS (vuoto/HIDDEN), MODULE (modulo richiesto, es. WWII). Doppio click = nascondi/mostra. Esiste un bottone che centra la mappa sull'aereo del giocatore. Utile: ogni unita' ha un UNIT ID e un MODULE.
- Delete Unit/Object (p. 356): tasto DELETE rimuove il gruppo intero con i waypoint.
- Map Options (p. 356): rimanda al capitolo System Bar (fuori porzione).
- Distance Tool (p. 356): misura sulla World Map; distanza in metri, rilevamento in gradi.
- Exit Mission Editor (p. 357): pulsante Exit.

---

## Integrazioni da figure (secondo passaggio, schermate viste una per una)

Tutte le pagine con figure delle pp. 287-357 sono state riviste a 150 dpi (con ritagli a 250 dpi per i pannelli azione). Quanto segue integra o corregge le sezioni precedenti; ogni voce e' marcata "(da figura, p. N)". I valori mostrati nelle schermate sono ESEMPI dell'autore del manuale, non sempre i default del programma: dove si dice "esempio" non va letto come default.

### F1. Pannello gruppo navale e terrestre (pp. 287, 303)
- CONDITION non e' solo testo Lua: accanto al campo c'e' un campo "%" con frecce, valore 100 (da figura, pp. 287, 303). Interpretazione: probabilita' percentuale di spawn del gruppo (100 = sempre). Il manuale non lo spiega a parole.
- Pannello navale, esempio: NAME "New Naval Group #003", COUNTRY USA, UNIT 1 OF 1, TYPE "Oliver Hazzard Perry class", UNIT NAME "Unit #004", SKILL Average, HEADING 345, FREQUENCY 127.5 MHz, MODULATION AM (da figura, p. 287). Quindi 127.5 AM e' il valore proposto per un nuovo gruppo navale. Il checkbox VISIBLE bef. ACTIVATION appare grigio (non attivo) finche' non si imposta late activation.
- Pannello terrestre, esempio: Group C, Russia, UNIT 2 OF 2, CATEGORY ARMOR, TYPE IFV BMP-3, SKILL Average, HEADING 155 (campo grigio perche' c'e' una route), con un checkbox INITIAL accanto al dial HEADING (da figura, p. 303; non spiegato a parole: presumibilmente fissa l'orientamento iniziale). PLAYER CAN DRIVE e VISIBLE bef. ACTIVATION risultano spuntati in quell'esempio.
- Nel pannello terrestre NON c'e' il campo FREQUENCY e c'e' CATEGORY (da figura, p. 303); le icone dei moduli sono 4 (ROUTE, AMMO, TRIGGERED ACTIONS, SUMMARY) contro 5 delle navi (da figura, pp. 287 e 303).

### F2. Waypoint (pp. 287, 291, 303, 309)
- Navi, nuovo gruppo: TYPE "Turning point", ALTITUDE 0 m (grigio, non editabile), SPEED 20 km/h con GS spuntato, START 8:0:0 / giorno 0 con Fix time spuntato (da figura, p. 287). Un waypoint successivo mostra SPEED 40 km/h, ETA 8:15:21/0, Fix time non spuntato (da figura, p. 291). La Route Summary di p. 294 invece mostra giorno "/1" (START TIME 8:0:0/1): la numerazione del giorno nella schermata del pannello waypoint e' /0, in quella di sintesi /1; il manuale non spiega la differenza. Nella schermata di p. 296 il waypoint 0 ha SPEED 40 e Fix time spuntato.
- Il pannello waypoint navale ha anche il campo TEMPLATE, grigio (valido solo per i terrestri Custom) (da figura, p. 291).
- Terrestri: il waypoint iniziale del gruppo si chiama "SP" (start point) e l'ultimo "DP" (da figura, pp. 303, 332-333); SPEED 20 km/h come valore di partenza; ALTITUDE grigia con la quota del terreno (es. 234 m); TYPE "Custom" con TEMPLATE; l'elenco TEMPLATE di esempio contiene: SA-10 SAM Battery Iran, SA-11 SAM Battery, SA-11 SAM Battery Iran, SA-2 SAM Battery, SA-2 SAM Battery Iran, SA-3 SAM Battery, SA-6 SAM Battery, SA-6 SAM Battery Iran, "insurgents mortar crew with car", "default" (da figura, p. 309). Quindi i template sono per unita' complete (battery SAM, squadre), non solo formazioni geometriche.
- Waypoint TYPE nel menu: nelle schermate compare "Off road" (non "Offroad") e "On road" (pp. 296-345); le formazioni sono quelle del testo p. 309.

### F3. Ammo, Triggered Actions, Summary (pp. 293, 311, 312)
- AMMO navale: la schermata (p. 293) mostra il modello 3D di un incrociatore classe Ticonderoga e nel pannello a destra, sotto le icone, un solo campo PAINT SCHEME = Default. Confermato: nessuna munizione editabile (da figura, p. 293). Stesso per il veicolo BMP-3 (da figura, p. 311).
- Route Summary terrestre, esempio: START TIME 6:50:0/1, ROUTE TIME 0:37:4/1, ROUTE LENGTH 12 km, AVERAGE SPEED 20 kmh (da figura, p. 312): coerente con 12 km a 20 km/h = 36 min circa. Navale esempio: 8:0:0/1, 0:41:47/1, 28 km, 40 kmh (p. 294).

### F4. Suppliers navali (p. 295)
La schermata mostra: pulsante FULL INFO, sezione SUPPLIERS con una lista di tre voci ("New Naval Group #002" due volte e "Kobuleti", che e' un aeroporto), pulsanti ADD e DEL. Sulla mappa le frecce partono dai fornitori (gruppi navali e l'aeroporto di Kobuleti) verso il gruppo navale (da figura, p. 295). Conferma: fornitori = altri gruppi navali e aeroporti; nessun parametro numerico (raggio, quantita') nel pannello; i dettagli stanno nel Resource Manager (non in questa porzione).

### F5. Pannello azione (Action Settings) comune (pp. 296-297, 326, 301, 302)
Campi comuni a tutte le azioni, navali e terrestri (da figura, pp. 296, 297, 326):
| Campo | Valori | Note |
|---|---|---|
| TYPE | Perform Task / Start Enroute Task / Perform Command / Set Option | Primo livello |
| ACTION | dipende dal TYPE | es. Fire at Point, Attack Group, ROE, ALARM STATE, FAC - Engage Group, Hold, go to waypoint, Disperse under fire |
| NUMBER | intero con frecce (indice di posizione nella lista del waypoint) | Esempio 1, 3, 4, 5 |
| ENABLE TASK | checkbox, spuntato di default | Per i Set Option di p. 301-302 e' presente |
| NAME | testo libero | Facoltativo |
| CONDITION... / STOP CONDITION... | bottoni | Perform Task e Start Enroute mostrano entrambi; i Set Option mostrano solo CONDITION... (da figura, pp. 301, 302, 343-345); anche i Perform Command (p. 338-341) mostrano solo CONDITION... |
La lista azioni del waypoint mostra righe testuali: es. navale `1. Attack Group("New Naval Group")`, `2. Invisible(on)`, `3. ROE = RETURN FIRE` (p. 296); terrestre `1. Hold -a`, `2. Set Callsign("Warrior 4")`, `3. Set Frequency(131)`, `4. FAC - Engage Group`, `5. ROE = WEAPON HOLD` (p. 326); `5. Disperse under fire = 600`, `ALARM STATE = Auto` (pp. 297, 344, 345). Questo fornisce il formato di serializzazione "umano" delle azioni.
I menu ROE e Alarm State navali mostrano esattamente: ROE = WEAPON FREE / RETURN FIRE / WEAPON HOLD (WEAPON FREE evidenziato come default), Alarm State = Auto / GREEN state / RED state (Auto evidenziato) (da figura, pp. 301, 302). Terrestri: stessi valori (da figura, pp. 343, 345).

### F6. Fire at Point - parametri risolti (pp. 297, 330)
Pannello (da figura, p. 297, ritaglio 250 dpi): ZONE RADIUS 5 con unita' "m" (esempio; il campo ha frecce); WEAPON = Auto (menu a tendina con default "Auto"); ROUNDS EXPEND = checkbox (spuntato) + campo numerico con frecce (esempio 3). Quindi: ROUNDS EXPEND e' un flag che abilita un numero di colpi/lanci (numero intero, unita' "colpi" nel senso di salve/lanci del sistema d'arma, il manuale non precisa l'unita') che l'arma puo' consumare nell'azione; se il flag e' spento il consumo non e' limitato dall'azione. ZONE RADIUS e' in metri. Non c'e' un campo di portata massima: il vincolo di portata e' implicito nell'arma scelta. Lo stesso pannello vale per i terrestri (p. 330).

### F7. Attack Group navale - campi risolti (p. 298)
Dalla schermata: GROUP (menu con il nome del gruppo), WEAPON = Auto (default), REL QTY = Auto (grigio finche' non si sceglie un'arma), MAX ATTACK QTY (numerico grigio con valore 1), GROUP ATTACK (checkbox), DIRECTION FROM (checkbox + quadrante azimut). I campi REL QTY e MAX ATTACK QTY sono abilitati solo con un'arma specifica (da figura, p. 298). Il bersaglio e' un gruppo (anche aereo o terrestre, "Selecting the target air/ground/ship group", p. 298).

### F8. Hold, Embark, Go to Waypoint (pp. 331-333, 340-341)
- Hold: il pannello azione mostra solo un menu TEMPLATE (stessa lista di sez. F2) per la formazione/template da assumere durante la sosta (da figura, p. 331). Quindi Hold ha un solo parametro: template (opzionale).
- Embark to Transport: VEHICLE GROUP (nell'esempio "Mi-8MTV2": il gruppo di trasporto puo' essere un gruppo di ELICOTTERI, non solo veicoli) e ZONE RADIUS in metri (esempio 200 m). La mappa mostra il punto di imbarco "DP" con un cerchio e, intorno al gruppo di trasporto, anelli concentrici rossi (area/direzione di avvicinamento dell'elicottero). Le fanterie del gruppo (10 unita' INFANTRY nell'esempio) hanno TRANSPORTABLE spuntato e velocita' 14 km/h, ETA non bloccato (da figura, p. 332). Nessuna azione di sbarco (Disembark) e' visibile.
- Go to Waypoint (task e comando): menu a tendina con i waypoint esistenti per numero e nome (1, 2, 3, DP nell'esempio; 1-5 nell'altro) (da figura, pp. 333, 341). Si sceglie per indice/nome. Corrisponde a "Switch Waypoint" aereo.

### F9. FAC terrestre - campi risolti (pp. 326, 328-329, 334-336)
- DESIGNATION: menu con sei voci: No, Auto, WP, IR-Pointer, Laser, WP-Laser (da figura, p. 328). Le portate massime di designazione mostrate dal ME quando il FAC e' troppo lontano: WP 16 km, IR-Pointer 5 km, Laser 10 km, WP-Laser 16 km (da figura, p. 329: "problem: D > 16 km", "D > 5 km", "D > 10 km", "D > 16 km"). Senza linea di vista tutte le voci mostrano "(problem: no LOS)".
- Esempi di valori nel pannello (non default garantiti): GROUP "Group C", VISIBLE (checkbox non spuntato nell'esempio), WEAPON "-Bombs" oppure "-Cluster bombs" (il menu WEAPON elenca categorie di armi aeree che il FAC richiedera'), PRIORITY 0, DESIGNATION Auto, DATALINK spuntato, CALLSIGN "Axeman", NUMBER 1, FREQUENCY 133 MHz, MODULATION AM (da figura, pp. 326, 328, 335). Il callsign e' un menu a tendina con nomi di callsign occidentali (es. Axeman, Warrior).
- Il gruppo FAC dell'esempio e' "JTAC" con TYPE "APC M1043 HMMWV Armament", CATEGORY ARMOR (da figura, p. 334): conferma il consiglio testuale (veicolo armato).

### F10. Perform Command - campi risolti (pp. 338-342)
| Comando | Campi dalla figura |
|---|---|
| Set Callsign | CALLSIGN (menu, es. "Warrior"), NUMBER (es. 4) (p. 338) |
| Set Frequency | FREQUENCY 131 MHz (esempio), MODULATION AM, POWER 10 W (esempio, unita' W) (p. 339). POWER e' quindi presente anche per i terrestri, contrariamente a quanto ipotizzato nel testo precedente |
| Transmit Message | FILE con bottone SELECT, SUBTITLE (area di testo), LOOP (checkbox), DUR 5 (secondi) (p. 340) |
| Go to Waypoint | vedi F8 |
| Invisible / Immortal / EPLRS | un solo checkbox ENABLE (pp. 341-342) |

### F11. Disperse Under Fire - valore risolto (p. 344)
Il pannello mostra: checkbox spuntato "Disperse" + valore numerico 600 con unita' "s" (da figura, p. 344; esempio 600 s = 10 minuti). Lista azioni: "5. Disperse under fire = 600". Quindi durata di dispersione espressa in secondi; il default numerico non e' leggibile (600 e' l'esempio mostrato).

### F12. Supply vehicle: disposizione sulle schermate (pp. 314-318)
- p. 315 Service column RED (vista 3D e icone ME, da sinistra a destra lungo una fila su un'area aeroportuale): SPAAA ZSU-23-4 Shilka, Transport Ural-375, fire-engine Ural ATsP-6, Fuel Truck ATZ-10, Transport Ural-4320-31 Armored, CP SKP-11 ATC Mobile Command Post, GPU APA-80 on ZiL-131, ARV BRDM-2 (da figura, p. 315). 8 veicoli in colonna.
- p. 315 Service column BLUE: AAA Vulcan M163, Transport M818 (x2), HEMTT TFFF (autopompa), Tanker M978 HEMTT, Transport M818, APC M1025 HMMWV, APC M1043 HMMWV Armament (da figura, p. 315). Anche qui 8 veicoli. Gli esempi includono un'unita' AAA (Shilka / Vulcan) come scorta di colonna.
- p. 317, Esempio 1 ("un supply vehicle ogni 4 semoventi"): il gruppo si chiama "Template Heavy Artillery Paladin", 5 unita' (UNIT 3 OF 5 selezionata e' un "Transport M818", CATEGORY UNARMED), SKILL Excellent, HEADING 80. La mappa mostra, con scala 50 m, quattro veicoli in due coppie e un supply vehicle al centro, ciascuno con un piccolo cerchio verde (area di servizio) di raggio dell'ordine di 20-30 m sulla scala della figura; un grande cerchio nero molto piu' ampio racchiude tutto (raggio 200 m del supply vehicle, secondo il testo di p. 316). L'esempio mostra quindi le 4 SPG tutte DENTRO il cerchio da 200 m del singolo supply vehicle; la dimensione esatta non e' leggibile con precisione (da figura, p. 317).
- p. 317, Esempio 2 ("un supply vehicle per ogni lanciatore" a un sito Patriot): gruppo "Patriot", 17 unita', supply vehicle "Transport M818" (unita' 17 di 17), SKILL High, HEADING 210; scala 300 m. La mappa mostra circa cinque cerchi neri di dimensione simile attorno ad altrettante coppie veicolo/lanciatore ai quattro angoli e al centro (centro: il radar/posto comando del sito con icona di comando). Ogni cerchio e' l'area di 200 m di un supply vehicle; i cerchi coprono ciascuno un lanciatore (da figura, p. 317).
- p. 318, Esempio 3 ("un supply vehicle per tutti i lanciatori" a un sito S-300PS): gruppo "S-300PS", 11 unita' tra cui un "Transport Ural-4320T" (CATEGORY UNARMED, SKILL High, HEADING 0), scala 60 m. Un solo grande cerchio nero (200 m) contiene i 6 lanciatori (due file da 3), il radar a sinistra e le antenne al centro; l'icona di posto comando e un'antenna a destra restano FUORI dal cerchio (da figura, p. 318): quelle unita' non sarebbero rifornite, ma non hanno munizioni.

### F13. Static Object (p. 346)
Pannello (esempio USA, CATEGORY Planes, TYPE A-20G): NAME "New Static Object", COUNTRY, CATEGORY, TYPE, HEADING con dial, checkbox HIDDEN, HIDDEN ON PLANNER, DEAD, menu PAINT SCHEME (esempio "645th BS, 410th BG, 9th AF") con anteprima 3D (da figura, p. 346). Il pannello degli statici NON ha CONDITION, SKILL, UNIT, route, ne' tab modali. Un oggetto statico non ha azioni; la vita/morte e' solo DEAD.

### F14. Initial Point e Bullseye (pp. 348-349) - valori risolti
- Initial Point (da figura, p. 348): COALITION menu (esempio Blue), CALLSIGN menu (esempio CHEVY; il manuale dice otto scelte), COMMENT (esempio "The point of entry to the battlefield."), SCALE = ENROUTE, STEER = TO TO, VNAV = 3D, VANGLE = COMPUTED (valori mostrati nell'esempio), ANGLE grigio (attivo solo con VANGLE = ENTERED). Gli elenchi completi di valori ammessi per SCALE/STEER/VNAV/VANGLE non sono leggibili dalla sola schermata: sono visibili solo i valori correnti ENROUTE / TO TO / 3D / COMPUTED. Il punto appare sulla mappa con il callsign e il commento.
- Bullseye (da figura, p. 349): la finestra si chiama "BULLSEYE LOCATION" e contiene COALITION (menu, esempio Blue) e due campi di sola lettura LONG e LAT in gradi-primi-secondi (esempio 37 59' 25" E, 44 56' 29" N). Posizione espressa in lat/long, non in MGRS.

### F15. Area Trigger Zone (pp. 350-351, 354)
- Nuova zona: NAME "New Trigger Zone", RADIUS 3000 m (valore del nuovo trigger zone mostrato in p. 350: default presumibile 3000 m), COLOR: palette di 28 colori e campi R, G, B, A con valori 255, 255, 255, 38 (da figura, p. 350: bianco quasi trasparente, alpha 38), HIDDEN, e sotto una tabella Name/Value con pulsante Add (proprieta' aggiuntive) (da figura, pp. 350-351).
- Zona agganciata a un edificio (p. 351): la tabella proprieta' contiene ROLE, VALUE, OBJECT ID (valore numerico, es. 81527743); cioe' una zona assegnata a un oggetto mappa conserva l'ID dell'oggetto (da figura, p. 351). Un raggio di esempio e' 44 m.
- Zone List (p. 354): colonne NAME, HIDDEN (checkbox per riga, non "STATE" come dice il testo), RADIUS (m); pulsanti Show all, Hide all, Toggle. Esempi di raggi: 300, 60000, 8000, 1500, 13000, 10000, 1500, 2000, 30000 m (da figura, p. 354): le zone possono avere raggi anche di decine di km.

### F16. Template (p. 353)
Il pannello "TEMPLATES" ha due blocchi: CREATE GROUP FROM TEMPLATE (menu country, menu template, es. "SA-10 (S-300PS) site", dial HEADING in gradi) e CREATE NEW TEMPLATE (SELECTED GROUP, TEMPLATE NAME, bottone SAVE TEMPLATE). Nella barra di stato in basso compare il comando "ADD TEMPLATE" (da figura, p. 353). L'esempio e' un sito S-300PS completo: sei lanciatori in due file, radar, antenne, posto comando; i supply vehicle fanno parte del template.

### F17. Unit List (p. 355)
Filtri con contatori per categoria (esempio: Helicopters 4, Planes 9, Vehicles 61, Ships 5, Statics 38, Total 117 units), un menu "ALL" (filtro, probabilmente per coalizione) e la tabella GROUP NAME, UNIT NAME, UNIT TYPE, UNIT ID, COUNTRY, STATUS (HIDDEN), MODULE. Gli UNIT ID sono interi (es. 329, 330, 262, 268...) assegnati dal ME alle singole unita' (da figura, p. 355). Utile come riferimento: ogni unita' ha un ID numerico univoco oltre al nome.

---

## Rilevanza per Warfare-Model

### A. Confronto strutturale con i gruppi aerei (differenze esplicite)

| Aspetto | Aereo | Navale | Terrestre | Statico |
|---|---|---|---|---|
| Unita' per gruppo | piu' limitato (p. 287: "Unlike aircraft groups, you can place up to 99 units"); limite aereo non indicato in questa porzione | 1-99 | 1-99 | esattamente 1 |
| Quota waypoint | si' | non regolabile | non regolabile (quota terreno) | n/a |
| Tipo waypoint | molti (Takeoff, Land, ecc.) | solo Turning Point | Offroad, On road, formazioni (Line Abreast, Cone, Vee, Diamond, Echelon L/R), Custom | n/a |
| Formazione | opzione Set Option Formation | nessuna | codificata nel TYPE del waypoint | n/a |
| Velocita' | - | km/h al waypoint; limite = nave piu' lenta | km/h per raggiungere il waypoint successivo | n/a |
| Munizioni (pannello AMMO) | loadout editor reale (pylon) | solo livrea | solo livrea | n/a (solo paint scheme) |
| Rifornimento | tanker/aeroporto | relazione Suppliers (gruppi navali/aeroporti) | supply vehicle entro 200 m | FARP + veicoli entro 150 m |
| Enroute Task | molti | solo No Enroute Task | No / FAC / FAC Engage Group | n/a |
| Task | molti (CAP, CAS, SEAD, Strike...) | No Task, Fire at Point, Attack Group | No Task, FAC Assign Group, Fire at Point, Hold, Embark to Transport, Go to Waypoint | n/a |
| ROE | 5 livelli | 3 | 3 | n/a |
| Alarm State | n/a (reaction to threat ecc.) | Auto/GREEN/RED | Auto/GREEN/RED | n/a |
| Campi specifici | Late activation ecc. | FREQUENCY nel pannello | CATEGORY, PLAYER CAN DRIVE, TRANSPORTABLE | DEAD, PAINT SCHEME |

### B. Cosa e' dato di MISSIONE (da esprimere nel .miz e nel simulatore sintetico)

- Gruppo: name, country (quindi coalition), categoria/tipo e numero unita' (1-99), nomi unita', skill (Average/Good/High/Excellent/Random), heading, late activation, hidden (map/planner), visible-before-activation, frequenza/modulazione (navi; terrestri via comando).
- Route: lista di waypoint con posizione, nome, tipo (terrestri: movimento/formazione; navali: turning point), velocita' (km/h), ETA/ora di start con lock. L'orario di start del gruppo e' l'ETA del wp 1 (trucco per attivazione ritardata o triggerata a +100 giorni).
- Azioni per waypoint: task (Fire at Point con zona/arma/rounds expend, Attack Group, Hold, Go to Waypoint, Embark, FAC), comandi (Invisible, Immortal, EPLRS, Set Callsign/Frequency, script), opzioni (ROE, Alarm State, Disperse Under Fire + secondi, Engage Air Weapons), ciascuna con condizioni di start/stop e priorita'.
- Statici: country, categoria, tipo, heading, dead, hidden, paint scheme; FARP: callsign e frequenza.
- Zone trigger circolari (centro, raggio in metri, eventualmente ancorate a unita'), Bullseye per coalizione, template di gruppo (per country).
- Supplier navali: relazione gruppo navale <- (navi/aeroporti), da modellare come grafo di fornitura.

### C. Cosa e' dato di ASSET / STATO DEL MONDO (non di missione)

- Munizioni per tipo di unita' terrestre (non editabili nel pannello AMMO): vanno nel registro armi/asset (come Weapon_Stores per modello). I tempi di rifornimento per arma (sez. 3.7) sono dati di asset: tabella `unit_type -> [(arma, secondi)]`.
- Velocita' massima di unita' e di gruppo (nave piu' lenta), corazza per facciata, portata e capacita' dei sensori, raggio di designazione dei designatori FAC (fumo, IR pointer, laser).
- Regola di supply: un supply vehicle = magazzino illimitato, raggio 200 m, la lista dei supply vehicle e il paese (Russia/Ukraine/USA); regola FARP: veicoli di servizio entro 150 m, area circa 200x200 m, tabella veicoli per servizio e coalizione, riparazione 3 minuti dopo arresto rotori. Sono regole di mondo/ruolo (un asset "supply" abilita il rifornimento entro un raggio), utilizzabili anche dal simulatore sintetico.
- Stato dinamico: unita' distrutta/danneggiata (disperse under fire e' un comportamento reattivo), munizioni residue, condizione dei veicoli di supporto FARP (se distrutti il servizio non e' disponibile).

### D. Cosa e' SOLO interfaccia (ignorabile per il modello)

Pulsanti ADD/INS/EDIT/DEL/UP/DOWN/CLONE, colori di selezione (bianco/rosso/blu), icone al wp 1, copia/incolla, Unit List/Area Trigger Zone List (filtri, Show/Hide), Distance Tool, Map Options, Exit, Place Initial Point (solo A-10C), colori delle zone, Route Summary (valori derivati: START TIME, ROUTE TIME, ROUTE LENGTH, AVERAGE SPEED = media semplice sui tratti).

### E. Punti di attenzione per la modellazione

1. Ammo Mode NON e' un editor di munizioni per navi e terrestri: e' solo la livrea. Le scorte sono implicite per tipo unita' e il rifornimento passa da supply vehicle (terra, entro 200 m, magazzino illimitato, tempi in secondi per arma) e da Suppliers (navi). Per il sintetico: modellare consumo e ricarica a livello asset e regola di supporto, non come dato di missione.
2. Velocita' in km/h (anche per le navi), quota non esiste a terra/mare; il wp ha ETA con lock: la start time del gruppo e' l'ETA del primo waypoint.
3. Il TYPE del waypoint terrestre fonde movimento (offroad/on road) e formazione; On Road richiede rete stradale (dato mappa), con vincolo di 500 m fra gruppi sulla stessa strada. Rilevante per il futuro modulo mappe.
4. Alarm State (Auto/GREEN/RED) e ROE a 3 livelli sono i parametri comportamentali per navi e terrestri; i gruppi di difesa aerea vanno definiti con tutte le unita' del battery nello stesso gruppo.
5. Fire at Point: zona circolare con raggio; artiglieria/razzi distribuiscono i colpi sull'area, missili/cruise sul centro; "Rounds expend" limita le munizioni consumate (valori non documentati). Naval Attack Group usa REL QTY e MAX ATTACK QTY come per l'aereo, con arrivo da DIRECTION FROM.
6. Hold, Go to Waypoint (ciclo con condizioni), Embark to Transport (solo INFANTRY, zona di imbarco in metri, "work in progress"), Invisible/Immortal sono i soli task/comandi terrestri non di combattimento documentati; nessun Disembark nella porzione.
7. FAC terrestre: parametri completi (callsign, numero, frequenza, modulazione, designation, datalink con EPLRS, vincolo LOS e distanza massima di designazione). Utile per modellare il supporto CAS.
8. Statici: un oggetto per gruppo, flag DEAD per la versione distrutta, nessuna azione; sono il canale naturale per rappresentare infrastrutture, magazzini, FARP e il relativo stato (integro/distrutto) nello stato del mondo.
9. Dati ancora incerti dopo il passaggio sulle figure: default veri di molti campi (le schermate mostrano esempi), significato esatto del checkbox INITIAL e del campo % di CONDITION (interpretato come probabilita' di spawn), elenchi completi dei valori ammessi di SCALE/STEER/VNAV/VANGLE (visibili solo ENROUTE, TO TO, 3D, COMPUTED), elenco completo delle armi per nave, comportamento del Resource Manager (quantita' warehouse, raggi per le navi), unita' esatta di ROUNDS EXPEND. Risolti con le figure: ROUNDS EXPEND (flag + intero), ZONE RADIUS in metri, durata di Disperse Under Fire in secondi (esempio 600), POWER radio in W (esempio 10), portate di designazione FAC (WP 16 km, IR-Pointer 5 km, Laser 10 km, WP-Laser 16 km), default 127.5 MHz AM per navi, raggio trigger default 3000 m.
10. Nuovi dati dalle figure rilevanti per il modello: la probabilita' di spawn (%) del gruppo, i template per unita' complete (battery SAM) come tipo di waypoint Custom/Hold, il gruppo di trasporto per Embark che puo' essere un gruppo di elicotteri, il formato testuale delle azioni (es. "ROE = WEAPON FREE"), l'ID numerico univoco di ogni unita' e di ogni oggetto agganciato a una trigger zone.
