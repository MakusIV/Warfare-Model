# DCS User Manual (2020) - Mission Editor, parte 3 (pp. 248-286)

Fonte: `DCS_User_Manual_EN_2020.pdf`, pagine 248-286, gruppi aerei (fixed wing / helicopter) in Advanced Actions Mode (Advanced Waypoint Actions). Termini DCS in inglese.
Note di lettura: il testo e' estratto dal PDF; in un secondo passaggio sono state esaminate TUTTE le figure (pannelli Action Properties, menu a tendina, schemi). Le integrazioni ricavate dalle figure sono marcate "(da figura, p. N)". Le pp. 254 e 258 contengono solo immagini 3D di formazioni (nessun parametro). Dove il manuale non da' un valore (range numerici, unita') e' scritto "non indicato".

Struttura generale di un'azione (dalle schermate): ogni azione ha TYPE (Perform Task / Start Enroute Task / Perform Command / Set Option), ACTION, NUMBER (ordine/priorita' nella lista del waypoint), ENABLE TASK (checkbox), NAME, CONDITION... (start condition) e, per i task, STOP CONDITION... (pp. 250, 273, 282-283, 285). Se nessuna Option e' impostata nella lista, valgono i default di tutte le opzioni (p. 282).

---

## 1. Perform Task residui

### WW2: Big Formation (pp. 248-258)
Organizza il bombardamento a tappeto di bersagli d'area, periodo WW2. Applicabile a: fixed-wing, soprattutto bombardieri WW2; Group Task "Ground Attack" (p. 248).

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| GROUP | gruppo "lead" scelto da lista | non indicato | la formazione viene costruita rispetto al lead (p. 248) |
| POSITION - Distance | m, avanti/indietro rispetto al gruppo seguito | auto dalla posizione scelta | modificabile a mano solo dopo aver scelto tutte le voci (p. 249) |
| POSITION - Elevation | m, differenza di quota | idem | p. 248 |
| POSITION - Interval | m, laterale | idem | p. 248 |
| Formation Type | "Combat Box", "Javelin Down" (cuneo) | non indicato | formazioni USAAF WW2 (p. 248) |
| Position in Wing | posizione nel wing rispetto al lead, max 500 m | non indicato | p. 248-249 |
| Position in Group | posizione nel gruppo intermedio, max 250 m | non indicato | p. 249 |
| Position in Box | posizione nel box, max 80 m | non indicato | p. 249; distanze troppo corte sono percepite dall'AI come critiche e provocano manovre anti-collisione |
| LAST WPT | waypoint fino al quale la formazione e' mantenuta (checkbox + selettore numerico) | disattivo | per i gruppi che seguono la rotta del lead (p. 249); (da figura, p. 248) il campo e' una checkbox che abilita un selettore di WPT |

Valori reali nei pannelli (da figura, pp. 248, 252, 256): GROUP default "NOTHING" nel lead, nei trailing e' il nome del lead (es. "B-17 Lead"); le tre quote di POSITION sono in metri (campo "m"). Lead (Leader/Leader/Leader): Distance -80, Elevation 50, Interval 120. Wing destro (Position in Box = Right): -80 / 50 / 120. Wing posteriore (Position in Box = Back): Distance -160, Elevation -50, Interval 0. I menu "Position in Wing / Position in Group / Position in Box" hanno valore "Leader" per il lead; per Combat Box i valori osservati in Position in Box sono Leader, Right, Back (il testo citava Left/Right/Rear). Per Javelin Down (da figura, p. 256) il terzo menu si chiama "Position in Squad" (non "Position in Box") e il valore osservato e' "Right High"; Distance -80, Elevation 50, Interval 120. Il tipo di Formation Type osservato e' "Combat Box" o "Javelin Down". Il pannello mostra anche, a sinistra, una linea gialla tra il gruppo e il lead (legame di formazione). Il pannello waypoint mostra la rotta del lead di esempio: 8 waypoint (0-7), quota 6096 m MSL, 370 km/h, Mach 0.329; i trailing a 6146 / 6196 / 6046 m (da figura, pp. 248, 250, 252, 256).

Semantica/procedura: il wing lead ha rotta WPT 0-7; a WPT 0 si assegnano due azioni: Perform Task "WW2: Big Formation" (Combat Box, Leader in tutte le posizioni) e Set Option "Formation" tipo "WW2: Bomber Element" (variant es. "Close (30 m x 30 m)"); a WPT 1 Perform Task "WW2: Carpet Bombing" (da figura, p. 250: tipo Perform Task, ACTION "WW2: Carpet bombing", WEAPON "-Bombs", REL QTY "All", PATTERN LENGTH 500 m, ALTITUDE ABOVE checkbox opzionale in m; azione in lista come "WW2: Carpet bombing(H = Hept = 6096 m)"; sul WPT 0 il Set Option Formation e' "WW2: Bomber Element" con VARIANT "Close (30 m x 30 m)"). Gli altri wing replicano le azioni di WPT 0 indicando nel campo GROUP il wing lead (es. "B-17 Lead") e posizione Left / Right / Rear; i gruppi trailing seguono i task del lead (pp. 249-251). Per Javelin Down (cuneo) nel campo GROUP va scelto il wing piu' vicino verso il lead; ala sinistra costruita come la destra (pp. 255-257). Il bombardamento avviene "a cue del lead wing" (p. 253; da figura, p. 254: i bombardieri sganciano in sequenza a ondate lungo la traiettoria del lead, scatto di carpet bombing). Copia gruppo con CTRL+C / CTRL+V (p. 251). Esempio Combat Box: 4 wing da 3 aeroplani a quote diverse (p. 249).

---

## 2. Start Enroute Task (pp. 259-270)

Differenza chiave dai Task: i bersagli degli Enroute Task devono essere **rilevati autonomamente** dall'AI prima dell'attacco (p. 259). Elenco: No Enroute Task, Search Then Engage, Search Then Engage in Zone, Search Then Engage Group, Search Then Engage Unit, Refueling, AWACS, FAC, FAC - Engage Group (pp. 259-260). Non compaiono EWR o altri.

Fattori che influenzano il rilevamento (p. 259):
- Sensori: radar aria-aria, aria-superficie, multimodo, RWR, elettro-ottici diurni e notturni, vista (soggetta a limiti di visibilita' cockpit).
- AI attaccante: skill, velocita', limiti di visibilita' cockpit.
- Ambiente/bersaglio: illuminazione, sfondo (foresta, campo, strada, mare), nebbia/pioggia/neve, nubi, dimensione unita' bersaglio, dimensione gruppo bersaglio, velocita' bersaglio, attivita' di fuoco attorno al bersaglio.
Il manuale avverte: CAS diurno contro bersaglio notturno o nella nebbia puo' non rilevarlo; il bersaglio deve stare entro la portata di rilevamento dalla rotta.

### No Enroute Task (p. 260)
Disponibile per tutti i tipi di gruppo e task. Nessuna azione. Nessun parametro.

### Search Then Engage (pp. 260-262)
Finche' l'azione e' attiva l'AI cerca attivamente i tipi di bersaglio selezionati e ingaggia appena possibile senza confliggere con altri task. Gruppi: fixed wing ed elicotteri.

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| ENGAGE DIST | checkbox + valore in **km** (da figura, p. 260: campo grigio con valore 15 km quando disabilitato) | checkbox disattivo (nessun limite); valore predisposto 15 km | i bersagli oltre la distanza dal tratto di rotta non vengono attaccati (p. 261); (da figura, p. 261) la zona valida e' un corridoio attorno alla rotta che parte dal waypoint "Start task" e segue i tratti di rotta con estremita' arrotondate (capsule) |
| TYPES OF TARGETS | checkbox gerarchici, dipendono dal Group Task (vedi sotto) | non indicato | p. 261-262 |
| PRIORITY | intero, 0 = massima priorita' relativa alle altre azioni del waypoint | 0 (da figura, p. 260) | p. 262 |

Pannello (da figura, p. 260): TYPE "Start Enroute Task", ACTION "Search Then Engage", NUMBER (ordine, 2 nell'esempio), ENABLE TASK, NAME, CONDITION..., STOP CONDITION..., poi ENGAGE DIST, albero a checkbox con radice "ALL" (tutti selezionati di default: AIR > HELICOPTERS; GROUND > INFANTRY, FORTIFICATIONS, VEHICLES > ARMOR...), PRIORITY. Esempio: gruppo A-10C con Task AFAC (azioni: 1. FAC, 2. Search Then Engage).

Tassonomia bersagli per Group Task (pp. 261-262):
- **SEAD**: Air Defense > AAA; SAM > SR SAM, MR SAM, LR SAM.
- **Anti-Ship**: Naval > Ships > Armed Ships (Heavy Armed Ships: Aircraft Carrier, Cruisers, Destroyers, Fregates, Corvettes; Light Armed Ships), Unarmed Ships; Submarines.
- **CAS e AFAC**: All; Air > Helicopters; Ground > Infantry, Fortifications, Vehicles (Armor: Tanks, IVF, APC; Artillery; Unarmed), Air Defense (AAA; SAM: SR/MR/LR); Naval > Light Armed Ships.
- **Fighter Sweep e Intercept**: Airplanes > Fighters, Bombers.

Uso tipico: dopo un Orbit Task nella lista azioni, il gruppo resta in holding e attacca quanto scoperto entro i limiti (pp. 262).

### Search Then Engage in Zone (pp. 263-264)
Come Search Then Engage ma limitato a una zona circolare definita dall'utente. Gruppi: aerei ed elicotteri; Group Task: tutti tranne "Fighter Sweep" e "Intercept". La zona si piazza sulla mappa (marker triangolare), con una linea al waypoint dell'azione.

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| ZONE RADIUS | metri | 5000 m nell'esempio (da figura, p. 263) | raggio della zona bersaglio (p. 263) |
| TYPES OF TARGETS | come sopra, dipende dal Group Task; albero con ALL selezionato (da figura, p. 263) | tutti | |
| PRIORITY | intero, 0 = massima | 0 (da figura, p. 263) | |

Da figura (p. 263): la zona e' rappresentata da un cerchio giallo con un cerchio rosso interno centrati sul marker, collegati con una linea al waypoint dell'azione.

### Search Then Engage Group (p. 264)
Analogo ad Attack Group ma con rilevamento autonomo richiesto.

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| GROUP | gruppo nemico dalla lista | - | |
| VISIBLE | checkbox | disattivo (da figura, p. 264) | se l'unita' conosce la posizione del bersaglio all'inizio missione |
| WEAPON | tipi di arma autorizzati (menu a tendina gerarchico, stessa famiglia del menu di p. 282: No weapon, All, Unguided > -Cannon, -Rockets (--Light rockets, --Heavy rockets), -Bombs (--Iron bombs, --Cluster bombs, ...), Guided...); (da figura, p. 264) valore osservato "Guided" | non indicato | elenco completo troncato nelle figure |
| PRIORITY | intero, 0 = massima | 1 nell'esempio (da figura, p. 264) | |

### Search Then Engage Unit (pp. 265-266)
Analogo ad Attack Unit con rilevamento autonomo.

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| GROUP | gruppo nemico | - | |
| UNIT | unita' specifica del gruppo | - | |
| STATIC | oggetto statico (bunker, FARP, ecc.) | "NOTHING" (da figura, p. 265) | alternativo a GROUP/UNIT |
| VISIBLE | checkbox | non indicato | |
| WEAPON | tipi d'arma autorizzati; valore osservato "-Guided bombs" (da figura, p. 265) | non indicato | |
| REL QTY | quantita' di carico autorizzata; menu a tendina con valore "Auto" (da figura, p. 265; le altre voci non sono visibili, nel carpet bombing e' presente "All") | Auto | p. 265 |
| MAX ATTACK QTY | checkbox + intero, numero massimo di passaggi di attacco | spuntato, valore 1 (da figura, p. 265) | |
| GROUP ATTACK | checkbox: tutto il flight partecipa | nell'esempio spuntato; di default un bersaglio per velivolo | |
| DIRECTION FROM | checkbox + azimut di avvicinamento (gradi; il campo valore e' un cursore/knob) | disattivo (da figura, p. 265) | |
| ALTITUDE ABOVE | checkbox + quota in m (valore predisposto 2000 m) | disattivo (da figura, p. 265) | |
| PRIORITY | intero, 0 = massima | 1 nell'esempio (da figura, p. 265) | |

### Refueling (p. 266)
Rifornimento in volo. Gruppi: aerocisterna (IL-78, KC-135), Group Task "Refueling". Creato automaticamente come azione automatica sul waypoint iniziale quando si crea il Mission Task Refueling; non cancellabile ne' modificabile. Nessun parametro. (Da figura, p. 266: TYPE "Start Enroute Task", ACTION "Tanker" (nome interno dell'azione), nessun campo oltre a NUMBER/CONDITION/STOP CONDITION; esempio IL-78M, Task Refueling, azioni "1. Tanker", "2. Orbit(H = Hept = 4500 m)", quota 4500 m, 640 km/h, Mach 0.547, WPT SP-DP.)

### AWACS (p. 267)
Airborne Warning and Control. Gruppi: A-50, E-2B, E-3A; Group Task "AWACS". Rileva bersagli aerei e trasmette dati ad aerei amici via radio e datalink (utilizzabili dal giocatore). Creato automaticamente al waypoint iniziale, non cancellabile/modificabile. Nessun parametro. (Da figura, p. 267: ACTION "AWACS"; esempio A-50, Task AWACS, azioni "1. AWACS", "2. Orbit (H = 6500 m)", quota 4500 m al WP SP, 790 km/h, Mach 0.675, CALLSIGN 114; il pannello non ha altri campi.)

### FAC (pp. 267-268)
Airborne Forward Air Controller. Solo coalizione BLUE; fixed wing ed elicotteri; Task "AFAC". Il FAC prioritizza automaticamente i bersagli per giocatore o AI attaccanti ed emette ordini di ingaggio durante la fase di attacco. Poiche' non e' scelto un gruppo specifico, i bersagli possono non coincidere con quelli voluti dal designer.

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| CALLSIGN | menu a tendina di callsign (es. "Chevy") | "Chevy" nell'esempio (da figura, p. 268) | |
| NUMBER | intero | 1 (da figura, p. 268) | |
| FREQUENCY | MHz | 133 MHz nell'esempio (da figura, p. 268) | |
| MODULATION | AM / FM | AM (da figura, p. 268) | |

Esempio (da figura, p. 268): MQ-9 Reaper, Task AFAC, 2000 m, 160 km/h, Mach 0.132, azioni "1. FAC", "2. EPLRS(on)" (il FAC attiva tipicamente EPLRS).

### FAC - Engage Group (pp. 268-270)
Come FAC ma il designer sceglie il gruppo nemico da designare. Solo BLUE; Task "AFAC".

| Parametro | Valori ammessi / unita' | Default | Note |
|---|---|---|---|
| GROUP | gruppo nemico | - | se nessun gruppo e' assegnato l'AFAC non emette comandi (p. 270) |
| VISIBLE | checkbox | non indicato | |
| WEAPON | armi che l'AFAC chiedera' di impiegare contro il bersaglio; valore osservato "-ATGM" (da figura, p. 269) | non indicato | p. 269 |
| PRIORITY | intero, 0 = massima | 0 (da figura, p. 269) | |
| DESIGNATION | menu: No, Auto, WP (smoke "Willy Pete"), IR-Pointer, Laser, WP-Laser (da figura, p. 270) | Auto | designazione su richiesta radio del giocatore a portata fissa; se il FAC e' oltre la portata il menu mostra la distanza massima (da figura, p. 270): **WP 16 km, IR-Pointer 5 km, Laser 10 km, WP-Laser 16 km**; il FAC va avvicinato entro tali distanze |
| DATALINK | checkbox | spuntato nell'esempio (da figura, p. 269) | scambio automatico di informazioni sul bersaglio |
| CALLSIGN / NUMBER | come FAC | "Enfield" / 1 nell'esempio (da figura, p. 269) | |
| FREQUENCY / MODULATION | MHz / AM-FM | 133 MHz / AM (da figura, p. 269) | |

L'AFAC deve comunque rilevare autonomamente il gruppo (ostacoli terreno, meteo).

---

## 3. Perform Command (pp. 271-275)

Comandi eseguibili all'arrivo a un waypoint.

| Command | Parametri | Default | Note |
|---|---|---|---|
| No Action | nessuno | selezione di default | p. 271 |
| Run Script | Script File (file Lua) oppure testo Lua nello scratchpad | - | p. 271 |
| Set Frequency | FREQUENCY (MHz); MODULATION (AM / FM); POWER (potenza trasmettitore in **W**, influenza la portata; da figura, p. 271) | esempio 131 MHz, AM, 10 W (da figura, p. 271) | frequenza radio del gruppo (pp. 271-272) |
| Set Frequency for unit | FREQUENCY (MHz), MODULATION, POWER (W), UNIT (menu delle unita' del gruppo, es. "Pilot #009") | esempio 131 MHz, AM, 10 W (da figura, p. 272) | come sopra ma per una singola unita' (p. 272) |
| Transmit Message | FILE (audio *.ogg/*.wav, pulsante SELECT); SUBTITLE (area di testo); LOOP (checkbox); DURATION (secondi, campo "DUR"; da figura, p. 273) | LOOP disattivo | messaggio dal gruppo lead (pp. 272-273) |
| Stop Transmission | nessuno | - | ferma la trasmissione del lead (p. 273) |
| Switch Waypoint | campo "TO WAYPOINT" (selettore numerico del waypoint di destinazione; da figura, p. 274, azione in lista "Switch Waypoint(0 - 2)") | di default il waypoint successivo | dal waypoint corrente va direttamente a quello indicato (es. da 3 a 6); tutte le altre azioni del waypoint si fermano; task principali, comandi e opzioni dei waypoint saltati non sono eseguiti; con un waypoint precedente crea un loop, interrompibile con stop condition (tempo di missione o flag) (pp. 273-274) |
| Invisible | ENABLE (checkbox) | - | gruppo invisibile a tutte le unita' AI nemiche (utile per FAC a terra vicini al nemico) (p. 274) |
| Immortal | ENABLE (checkbox) | - | il gruppo e' rilevabile ma le armi nemiche non hanno effetto (scenari di ingaggio prolungato) (p. 274) |
| EPLRS | on/off (valore non dettagliato nel testo; nell'azione in lista compare "EPLRS(on)", da figura, p. 268) | - | datalink di posizione dell'unita' (pp. 274-275) |
| Smoke On_Off | VALUE (checkbox; l'unica opzione) | - | attiva il generatore di fumo sui piloni alari, se presente (p. 275) |

Non compaiono altri comandi in queste pagine (es. Start/Stop, Set Callsign, Set Unlimited Fuel, Activate Beacon/ICLS/ACLS): non fanno parte di questa porzione.

---

## 4. Set Option (pp. 276-286)

Opzioni impostabili come azioni a un waypoint. "No Option" e' la selezione di default.

### ROE (pp. 276-277)
Regola di fuoco del gruppo quando incontra nemici. **Default per tutti i gruppi: "Only designated"** (p. 277). Menu (da figura, p. 276): WEAPON FREE, PRIORITY DESIGNATED, ONLY DESIGNATED, RETURN FIRE, WEAPON HOLD - i nomi nel manuale sono questi cinque (non "Open Fire" ecc.). Azione in lista: "ROE = ONLY DESIGNATED".

| Valore | Semantica |
|---|---|
| Weapon free | ingaggia qualunque gruppo nemico in contatto; prioritizzazione automatica |
| Priority designated | ingaggia qualunque nemico in contatto, ma il gruppo designato come bersaglio dell'azione e' primario e ingaggiato per primo; dopo la sua distruzione, prioritizzazione automatica |
| Only designated | ingaggia solo il gruppo designato (default) |
| Return fire | risponde al fuoco, non ingaggia per primo |
| Weapon hold | non fa fuoco in nessuna circostanza |

### Reaction to Threat (pp. 277-278)
Regole difensive del gruppo. **Default: Allow Abort Mission.** Menu (da figura, p. 277): NO REACTION, PASSIVE DEFENCE, EVADE FIRE, EVASIVE VERTICAL MANEUVER, ALLOW ABORT MISSION, HORIZONTAL AAA FIRE EVADE (sei voci, scelta singola). Efficace solo in difesa: durante un'azione d'attacco prevale il ROE (ROE ha priorita' superiore) (p. 277).

| Valore | Semantica |
|---|---|
| No reaction | nessuna azione difensiva contro le minacce |
| Passive defense | misure difensive passive e attive, nessuna manovra difensiva contro minacce in arrivo |
| Evade fire | misure passive/attive piu' manovre difensive |
| Evasive vertical maneuver | il gruppo puo' salire/scendere per evitare una zona di minaccia nota, piu' misure passive/attive |
| Allow Abort Mission | permette al gruppo di interrompere la missione se ingaggiato (default) |
| Horizontal AAA fire evade | manovre evasive contro fuoco AAA senza cambiare quota |

### Radar Using (p. 278)
Default: **Use for search if required.** Menu (da figura, p. 278): NEVER USE, USE FOR ATTACK ONLY, USE FOR SEARCH IF REQUIRED, USE FOR CONTINUOUS SEARCH.

| Valore | Semantica |
|---|---|
| Never use | mai radar per ricerca o ingaggio (guida missili) |
| Use for attack only | niente ricerca radar, ma usato per l'ingaggio se necessario; la ricerca puo' avvenire con altri sensori |
| Use for search if required | radar per ricerca se serve (quando altri mezzi falliscono) |
| Use for continuous search | radar sempre acceso |

Nota: l'illuminazione radar e' una firma rivelatrice e annulla la sorpresa (p. 278).

### Chaff - Flare Using (p. 279)
Default: **Use when flying in SAM WEZ.** Menu (da figura, p. 279): NEVER USE, USE AGAINST FIRED MISSILE, USE WHEN FLYING IN SAM WEZ, USE WHEN FLYING NEAR ENEMIES (N/A).

| Valore | Semantica |
|---|---|
| Never use | nessun rilascio quando ingaggiato |
| Use against fired missiles | solo quando rilevati missili in arrivo |
| Use when flying in SAM WEZ | preventivo dentro zona minaccia SAM nota o entro portata di aereo nemico noto con missili IR (default) |
| Use when flying near enemies (n/a) | contromisure sopra territorio nemico (marcato "n/a" nel manuale: non operativo) |

### Formation (pp. 280-281)
Formazione assunta al waypoint. Default **Echelon Right** (aerei); **Wedge** (elicotteri).

| Parametro | Valori ammessi | Default | Note |
|---|---|---|---|
| TYPE (aerei) | Line Abreast, Trail, Wedge, Echelon Right, Echelon Left, Finger Four, Spread Four, WW2: Bomber Element, WW2: Bomber Element Height Separation, WW2: Fighter Vic | Echelon Right | p. 280 |
| TYPE (elicotteri) | Wedge, Front, Echelon, Column | Wedge | p. 280-281 |
| SIDE | port/starboard | non indicato | solo elicotteri, per line abreast/echelon (p. 281) |
| VARIANT | variante per dimensione (indicata in metri, es. "Close (30 m x 30 m)", p. 250; elicotteri "50x70", da figura, p. 280) | non indicato | |

Dettagli e illustrazioni nel Flight Manual (p. 281). Da figura (p. 280): per un gruppo di elicotteri (Mi-28N) il pannello Formation mostra TYPE "Echelon", SIDE "Right", VARIANT "50x70" (m); per gli aerei compare solo TYPE e VARIANT. La foto di p. 281 mostra una formazione a cuneo di Mi-28N (nessun dato).

### RTB on Bingo Fuel (p. 281)
Flag: consente/impedisce il ritorno alla base al raggiungimento di Bingo Fuel (carburante appena sufficiente per rientrare). **Default ON (allow).**

### RTB on out of ammo (p. 282)
Il gruppo rientra quando ha esaurito le munizioni; si sceglie dal menu quale categoria di armi conta. **Default: "No weapon"** (cioe' non attivo). Valori visibili nella schermata (menu, da figura, p. 282): No weapon, All, Unguided (-Cannon, -Rockets (--Light rockets, --Heavy rockets), -Bombs (--Iron bombs, --Cluster bombs, ...)); la lista e' scorrevole e tagliata nella figura: le voci successive (armi guidate ecc.) non sono leggibili. Stessa gerarchia del menu WEAPON dei task d'attacco (che mostra anche "Guided", "-Guided bombs", "-ATGM").

### Silence (p. 282)
Flag: forza il silenzio radio dal waypoint. **Default OFF** (radio consentita).

### ECM Using (pp. 282-283)
Procedura d'uso della suite di guerra elettronica di bordo. **Default: Use if only lock by radar.** Valori dal menu (da figura, p. 283): NEVER USE; USE IF ONLY LOCK BY RADAR; USE IF DETECTED OR LOCK BY RADAR; ALWAYS USE. Il testo non descrive le semantiche oltre i nomi.

### Restrict Air-to-Air Attack (p. 283)
VALUE checkbox: vieta di attaccare bersagli aerei. Default OFF.

### Restrict Jettison (p. 283)
VALUE checkbox: vieta di sganciare carichi esterni. Default OFF.

### Restrict Afterburner (p. 283)
VALUE checkbox: vieta il postbruciatore (riduce firma IR e migliora sopravvivenza contro missili a ricerca di calore). Default OFF.

### Restrict Air-to-Ground Attack (p. 284)
VALUE checkbox: vieta di attaccare bersagli a terra. Default OFF.

### AA Missile attack ranges (p. 284)
Distanza di lancio dei missili aria-aria. **Default: Launch by target threat estimate.**

| Valore | Semantica |
|---|---|
| Max range launch | lancio alla massima portata possibile |
| No escape zone launch | lancio solo con bersaglio dentro la no escape zone del missile |
| Half way max range - No escape zone launch | lancio a distanza intermedia tra portata massima e no escape zone |
| Launch by target threat estimate | secondo la minaccia: bersaglio ostile piu' vicino in avvicinamento, con radar attivo, agganciato o in attacco (default) |
| Random between max range and no escape zone launch | distanza casuale tra portata massima e no escape zone |

### No Report Waypoint Pass (p. 285)
VALUE checkbox: vieta il report radio al passaggio waypoint. Default OFF.

### Radio usage when contact / when engage / when kill target (pp. 285-286)
Tipo di bersagli per cui il gruppo fa comunicazioni radio quando: e' in contatto col nemico (contact); e' in combattimento (engage); ha danneggiato/distrutto un bersaglio (kill target). Pannello a checkbox gerarchico (da figura, p. 285): ALL (spuntato) > AIR > HELICOPTERS; GROUND > INFANTRY, FORTIFICATIONS, VEHICLES > ARMOR ... (la lista prosegue ma e' tagliata; stessa tassonomia dei bersagli CAS di p. 262); tutte le voci spuntate di default. Comportamento: il gruppo comunica via radio solo per i tipi di bersaglio spuntati. **Default per tutti e tre: ALL targets.** Pannelli di engage e kill identici a quello di contact.

---

## 5. Rilevanza per Warfare-Model

**Dottrina / regole d'ingaggio (da modellare)**
- ROE (5 livelli): corrisponde alla postura di fuoco; "Only designated" (default DCS) vs "Weapon free" cambia chi puo' essere ingaggiato. Mappa naturale su un campo `roe` per missione/gruppo; "Return fire" e "Weapon hold" sono posture difensive/di pace.
- Reaction to Threat: mappa su postura difensiva (evasione, abort). "Allow Abort Mission" interagisce con i criteri di fine missione (abbandono se ingaggiati); ROE prevale in attacco.
- Radar Using, ECM Using, Chaff-Flare Using, Restrict Afterburner, Silence: parametri di segnatura emessa/EMCON. Rilevanti per il modello di rilevamento/intercettazione (radar acceso = firma, cfr. volumi di rilevamento); Radar Using "Never"/"attack only" e Silence sono la leva per AVOID_DETECTION.
- AA Missile attack ranges: regola di lancio (Max range, No escape zone, Half way, By threat estimate, Random) - direttamente collegata a Engagement_Resolver / portate d'arma e al concetto di no escape zone.
- Restrict Air-to-Air / Air-to-Ground Attack, Restrict Jettison: vincoli di ruolo/arma per missione (utile a filtro armi per missione, A4).
- Search Then Engage (+ in Zone / Group / Unit): modello di ingaggio con rilevamento autonomo; target categories (SEAD, Anti-Ship, CAS/AFAC, Fighter Sweep/Intercept) corrispondono alla tassonomia bersagli per tipo di missione; ENGAGE DISTANCE = raggio di cattura dalla rotta; Zone Radius = zona di caccia; PRIORITY = ordine tra task; REL QTY / MAX ATTACK QTY / GROUP ATTACK / DIRECTION FROM / ALTITUDE ABOVE = parametri di attacco (profilo di attacco). Fattori di rilevamento (p. 259) elencano le variabili del modello di visibilita' (sensori, meteo, illuminazione, dimensione bersaglio).

**Criteri di fine missione**
- RTB on Bingo Fuel (default ON): fine missione per carburante, gia' coerente con Fuel_Model.
- RTB on out of ammo (default No weapon; scelta per categoria arma): fine missione "Winchester" per categoria di arma - ricade nella scorta per modello d'arma.
- Allow Abort Mission (Reaction to Threat) e Switch Waypoint (salto/loop con stop condition): flusso condizionale della rotta.

**Strutture di ruolo/supporto**
- Refueling, AWACS: task automatici non editabili legati al tipo di missione (tanker, AWACS); AWACS e' sensore e datalink, rilevante per la conoscenza condivisa del campo. FAC/FAC-Engage Group: solo BLUE, designazione (metodo con portata massima), datalink; utile solo se si modella la designazione.
- Formation (tipi aerei e elicotteri) e WW2 Big Formation (Combat Box, Javelin Down): geometria di formazione; pochi effetti sulla simulazione sintetica, necessari per l'esportazione .miz.

**Trascurabili per il motore (interfaccia/radio/effetti ME)**
Set Frequency / for unit (frequenza, modulazione, potenza), Transmit Message / Stop Transmission, Radio usage when contact/engage/kill, No Report Waypoint Pass, Callsign/Number/Frequency dei FAC, EPLRS, Smoke On_Off, Run Script, Invisible/Immortal (trucchi di scenario, non dottrina; Immortal puo' servire solo come strumento di test), Chaff "near enemies (n/a)".

Altre osservazioni dalle figure: nel pannello di ogni azione il campo NUMBER e' l'ordine di esecuzione nella lista del waypoint, e la lista "Advanced (Waypoint Actions)" ordina le azioni (esempio p. 276: 1. Attack Group, 2. Search Then Engage Unit, 3. Switch Waypoint(0-2), 4. Formation, 5. ROE); i task con durata hanno anche STOP CONDITION..., i comandi/opzioni solo CONDITION... (da figura, pp. 250, 273, 276). Le figure dei pannelli waypoint mostrano anche i dati di rotta associati (WAYPOINT n di N, TYPE "Turning point", ALTITUDE m MSL/AGL, SPEED km/h con GS, MACH, START hh:mm:ss con "Fix time"), ma non sono oggetto di questa porzione.

**Valori di default DCS da riportare nello schema** (se non specificato dalla missione): ROE = Only designated; Reaction to Threat = Allow Abort Mission; Radar Using = Use for search if required; Chaff/Flare = Use when flying in SAM WEZ; Formation = Echelon Right (aerei) / Wedge (elicotteri); RTB on Bingo = ON; RTB on out of ammo = No weapon; Silence = OFF; ECM = Use if only lock by radar; Restrict* = OFF; AA Missile attack ranges = Launch by target threat estimate; No Report Waypoint Pass = OFF; Radio usage = ALL.
