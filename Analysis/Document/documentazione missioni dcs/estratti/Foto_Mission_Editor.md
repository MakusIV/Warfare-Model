# Foto del Mission Editor DCS World — trascrizione

Fonte: 22 fotografie scattate con il telefono allo schermo il 2026-10-05 (11:24–11:36), cartella
`Analysis/Document/documentazione missioni dcs/` (file `20261005_*.jpg`; `20261005_113405(1).jpg` è un
duplicato byte per byte di `20261005_113405.jpg`, stesso md5, e non è trascritto a parte).

Missione aperta in tutte le foto: **`1975 Georgian War_first.miz`** (titolo in alto a sinistra), mappa Caucaso.
La missione sembra generata da un motore di campagna: i gruppi si chiamano `Pack <n> - <reparto> - <ruolo> <n>`,
i waypoint hanno nomi standard (`Departure`, `Join`, `Nav`, `AI Descend Helper`, `IP`, `Attack`, `Egress`,
`Split`, `Station`) e il briefing Blue contiene un Air Tasking Order. Questa è un'ipotesi: va verificata sul
`.miz` presente nella stessa cartella.

Elementi comuni a tutte le schermate (solo interfaccia, non ripetuti nelle singole sezioni):

- barra menu `FILE VIEW EDIT FLIGHT CAMPAIGN CUSTOMIZE MISC`;
- barra strumenti verticale a sinistra con le sezioni `MIS` (file, meteo, trigger, obiettivi, ruoli, ecc.),
  `OBJ` (inserimento aerei, elicotteri, navi, veicoli, statici, ecc.) e `MAP` (`Draw`, righello, ecc.);
- barra di stato in basso: `DFLT`, `CCS X-…… Z+……` (coordinate del cursore), `ALT` (quota del terreno sotto il
  cursore), `6M +4.7°` (probabilmente la declinazione magnetica, interpretazione non verificata), `PAN/SELECT`,
  pulsanti `MAP` / `SAT` / `ALT` e orologio di sistema `5.10.2026 hh:mm:ss`.

Legenda: "(grigio)" = campo disabilitato o non modificabile; "☑" = casella spuntata; "☐" = non spuntata.

---

## 20261005_112430.jpg — AIRPLANE GROUP + tab Route (waypoint 0) con lista Advanced Waypoint Actions

Gruppo selezionato: **Pack 19 - F7 - Anti-ship Strike 1**, Sweden (coalizione Blue), 2 × AJS37.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| GROUP NAME | Pack 19 - F7 - Anti-ship Strike 1 | — | pulsante `?` a destra |
| CONDITION | (vuoto) % / 100 | — | due campi: un testo vuoto e uno spinner `100` (probabilità di presenza del gruppo, %) |
| COUNTRY | Sweden | menu chiuso | pallino blu = coalizione Blue; pulsante `COMBAT` accanto (funzione non visibile) |
| TASK | Anti-ship Strike | menu chiuso | task principale del gruppo |
| UNIT | 2 OF 2 | — | unità selezionata / numero di unità nel gruppo |
| TYPE | AJS37 | menu chiuso | |
| SKILL | Veteran | menu chiuso | |
| PILOT | Pack 19 - F7 - Anti-ship Strike 1-2 | — | nome dell'unità |
| TAIL # | 034 | — | pulsante di copia accanto |
| RADIO | ☑ | — | |
| FREQUENCY | 269.9 MHz | modulazione `AM` (menu chiuso) | |
| CALLSIGN | Ford / 7 / 2 | menu chiuso sul nome | nome, numero del volo, numero del gregario |
| HIDDEN ON MAP | ☐ | — | |
| HIDDEN ON PLANNER | ☐ | — | |
| HIDDEN ON MFD | ☐ | — | |
| GAME MASTER ONLY | ☐ | — | |
| UNCONTROLLED | ☑ | — | |
| LATE ACTIVATION | ☐ | — | |
| Tab (icone) | Route (attivo), Payload, Triggered Actions, Summary (Σ), `…` | — | 5 tab colorate (rosso, arancio, giallo, verde, azzurro); i nomi sono dedotti dal contenuto delle altre foto |
| WAYPOINT | 0 OF 10 | menu chiuso | frecce `<` `>` per scorrere |
| NAME | Departure | — | |
| TYPE | Takeoff from ran… (troncato, presumibilmente "Takeoff from runway") | menu chiuso | |
| ALTITUDE | 621 m | riferimento `AGL (Rdr Alti…)` (menu chiuso) | |
| SPEED | 677 kmh | — | `GS` ☑ |
| MACH | 0.565 | — | |
| START | 5 : 4 : 54 / 0 | — | `Fix time` ☑ (ore:min:sec / giorno) |
| Pulsanti waypoint | ADD, EDIT, DEL | — | |
| ADVANCED (WAYPOINT ACTIONS) | 1. Formation = Spread Four Open (116 m x 97 m)  2. Run Script  3. Reaction to Threat = EVADE FIRE  4. Restrict Jettison = on | — | lista azioni del waypoint 0 |
| Pulsanti azioni | ADD, INS, EDIT, DEL, UP, DOWN, CLONE | — | |
| ADVANCED WP AUTO FILL | pulsante | — | |

Mappa: zoom sulla costa di Sukhumi; il gruppo è sull'aeroporto **Sukhumi-Babushara** (beacon 395.00 kHz e
489.00 kHz AV visibili); la rotta bianca (gruppo selezionato) va verso ovest sul mare con i waypoint `1:Join` e
`8:Split`; molte altre rotte blu di altri gruppi; griglia MGRS (FH35, FH45, …).

---

## 20261005_112514.jpg — AIRPLANE GROUP + tab Route (waypoint 4, IP), vista di teatro

Stesso gruppo (Pack 19, Sweden, AJS37 ×2); campi del gruppo identici alla foto precedente.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| WAYPOINT | 4 OF 10 | — | |
| NAME | IP | — | |
| TYPE | Turning point | menu chiuso | |
| ALTITUDE | 1000 m | `AGL (Rdr Alti…)` | |
| SPEED | 903.6 kmh | — | `GS` ☐ |
| MACH | 0.757 | — | |
| ETA | 5 : 36 : 24 / 0 | — | `Fix time` ☑; per i waypoint successivi al primo l'etichetta diventa `ETA` invece di `START` |
| ADVANCED (WAYPOINT ACTIONS) | (lista vuota) | — | nessuna azione su questo waypoint |

Mappa: vista di tutto il teatro (Mar Nero orientale – Caucaso). Aeroporti con etichetta rossa (coalizione Red):
Krasnodar-Center, Krasnodar-Pashkovsky, Anapa-Vityazevo, Novorossiysk, Gelendzhik, Sochi-Adler, Mineralnye Vody,
Nalchik (parzialmente leggibile). Aeroporti blu: Gudauta, Sukhumi-Babushara e altri nella Georgia. Centinaia di
rotte blu con waypoint nominati (`Join`, `Nav`, `AI Descend Helper`, `IP`, `Attack`, `Egress`, `Split`,
`Station`, `Departure`). Riquadri rossi con icone di bersaglio ed etichette tipo `2(5) 3(5)`, `8(5) 33(5)`,
`5(5) 8(5)` (cifre parzialmente illeggibili). Beacon NDB/VOR con frequenze (es. 740.00 kHz, 866.00 kHz SN,
1210.00 kHz PR, 111.70 MHz, ecc.).

---

## 20261005_112529.jpg — AIRPLANE GROUP + tab Route (waypoint 5, Attack) con azioni di attacco

Stesso gruppo Pack 19.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| WAYPOINT | 5 OF 10 | — | |
| NAME | Attack | — | |
| TYPE | Fly over point | menu chiuso | |
| ALTITUDE | 1000 m | `AGL (Rdr Alti…)` | |
| SPEED | 776 kmh | — | `GS` ☑ |
| MACH | 0.65 | — | |
| ETA | 5 : 37 : 24 / 0 | — | `Fix time` ☐ |
| ADVANCED (WAYPOINT ACTIONS) | 1. Anti-Ship -a  2. Attack Group("Russian Convoy 2") | — | `Anti-Ship` sembra il task di default del task principale; il bersaglio è un gruppo navale nominato |

Mappa: la rotta bianca del gruppo selezionato esce in mare verso ovest (sud-ovest di Novorossiysk) con
`5:Attack` (giallo, selezionato), `6:Egress`, `3:AI Descend Helper`, `2:Nav`, `7:Nav`; un'altra rotta con
`3:Attack`, `2:IP`, `4:Egress` più a nord.

---

## 20261005_112548.jpg — PAINT AND LOADOUT (tab Payload)

Stesso gruppo Pack 19 (campi del gruppo identici). Finestra grande con anteprima 3D dell'AJS37.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| PAINT SCHEME | #1 Splinter F21 Norrbottens Flygflottilj | menu chiuso | livrea |
| PAYLOAD RESTRICTION | ☐ | — | |
| Colonne piloni | 7, 6, 5, 4, 3, 2, 1 | — | |
| Mission payload (carico attuale) | icone sui piloni 5, 4, 3 | — | pilone 4 icona di serbatoio/pod centrale, 5 e 3 icone a X (missili); corrisponde alla riga "Anti-ship (RB05)" o simile, non determinabile dalle icone |
| Lista carichi predefiniti | Empty | — | |
| | Anti-Ship (Modern): RB-15F*2, RB-74*2, XT | — | icone sui piloni 6–2 |
| | Anti-ship (Heavy Mav): RB-75T*4, XT | — | |
| | Anti-ship (Light Mav): RB-75*4, XT | — | |
| | Anti-ship (RB05): RB-05A*2, RB-74*2, XT | — | |
| | Anti-ship: RB-04E*2, RB-74*2, XT | — | |
| | ECM Escort Anti-ship: RB-04E, KB, RB-74*2, XT | — | la lista è filtrata sul task Anti-ship Strike |
| Pulsanti | NEW, COPY, DELETE, RENAME, EXPORT | — | |
| CIVIL PLANE | ☐ | — | colonna destra, tab Payload |
| INTERNAL FUEL | 100 % | slider | |
| FUEL WEIGHT | 5489 kg | — | |
| EMPTY | 10749 kg | — | |
| WEAPONS | 448 kg | — | |
| MAX | 20000 kg | — | |
| TOTAL | 16686 kg | — | e 83 % (slider) |
| CHAFF | 210 | (grigio) | |
| FLARE | 72 | (grigio) | |

---

## 20261005_112600.jpg — AIRPLANE GROUP + tab Triggered Actions (presumibile)

Stesso gruppo Pack 19. Terza tab (icona ⌘, gialla) attiva.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| Lista azioni | 1. Start "Pack 19 - F7 - Anti-ship Strike 1" | — | probabilmente un'azione `Start` (avvio del gruppo non controllato) richiamabile da un trigger |
| Pulsanti | ADD, INS, EDIT, DEL, UP, DOWN, CLONE | — | |

Mappa: costa Sochi–Sukhumi, rotta bianca del gruppo (`1:Join`, `8:Split`), aeroporti Sochi-Adler (rosso, ILS
111.10 MHz 62°), Gudauta (blu, 395.00 kHz XC), molte rotte blu con `Station`, `Join`, `Split`.

---

## 20261005_112610.jpg — AIRPLANE GROUP + tab Summary (Σ)

Stesso gruppo Pack 19.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| START TIME | 5:4:54/1 | — | formato h:m:s/giorno |
| ROUTE TIME | 0:51:14/1 | — | |
| ROUTE LENGTH | 550 km | — | |
| AVERAGE SPEED | 645 kmh | — | calcolati dal ME, sola lettura |

---

## 20261005_112622.jpg — PAINT AND LOADOUT + tab `…` (proprietà specifiche dell'aereo)

Stesso gruppo Pack 19; a sinistra la stessa lista carichi della foto 112548.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| RB-04 Group Target Selection | Random | menu chiuso | proprietà specifica dell'AJS37 |
| RB-04 Angle Jump Target Selectic(on) | None | menu chiuso | etichetta troncata |
| Weapon safety height | Medium | menu chiuso | |
| Cartridge restrictions | Allow all | menu chiuso | |

---

## 20261005_112647.jpg — BRIEFING

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| SORTIE | 1975 Georgian War - 1 | — | |
| Red | Abkhazia, Belarus, China, Iran, Kazakhstan, North… (troncato) | — | paesi della coalizione Red |
| Blue | Australia, Belgium, Canada, Croatia, Czech Repu… (troncato) | — | paesi della coalizione Blue |
| BRIEFING IMAGES PANEL | pulsante | — | |
| SITUATION | "September 13, 1975, 04:51: After the effective political action of the Minister of the Interior, a group of Georgian nationalists led by the Army Corps General Baaka Kobakhidze, carried out a coup by supporting Georgian military forces and with the political and military support of some western countries coordinated by the USA." | — | testo che continua oltre (scrollbar) |
| RED TASK | (vuoto) | — | |
| BLUE TASK | Air Tasking Order: / Sorties Mission TOT / 1 CVN-71 Theodore Roosevelt Alert 04:51:16 / 11 203 SA-2 Site A-3 06:11:58 / 7 206 SA-2 Site B-3 06:15:13 / 3 204 SA-6 Site B-1 06:13:43 / 3 106 SA-2 Site C-6 06:11:11 | — | ATO in forma testuale: numero di sortite, nome missione (numero + bersaglio), TOT; continua oltre (scrollbar) |
| NEUTRALS TASK | (vuoto) | — | |

---

## 20261005_112657.jpg — TIME AND WEATHER (tab STATIC)

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| START (data) | 13 / September / 1975 | mese da menu (chiuso) | |
| START (ora) | 4 : 51 : 16 | — | |
| Slider orario | `-1 h` … `+1 h` | — | |
| Sun And Moon | voce espandibile (`>`) | — | contenuto non visibile |
| Modalità meteo | STATIC (attiva) / DYNAMIC | — | |
| CONDITIONS – T | 8 °C | — | temperatura |
| CLOUDS AND ATMOSPHERE – PRESET | High Scattered 2 | anteprima immagine | preset di nubi |
| BASE | 2200 m | slider | base delle nubi |
| QNH | 774 mmHg | — | |
| ICE HALO – APPEARANCE | Off | menu chiuso | |
| NAVIGATIONAL WIND SETTINGS – at 8000 m | 8 m/s, BLOWS TO DIR 217° | — | rosa dei venti grafica |
| at 2000 m | 2 m/s, 217° | — | |
| at 500 m | 6 m/s, 217 (grigio) | — | direzione non editabile a questa quota |
| at 10 m | 3 m/s, 217° | — | |
| TURBULENCE | 0.9 m/s | — | |
| FOG – MODE | Off | menu chiuso | |
| DUST STORM – DUST STORM ENABLE | ☐ | — | |
| VISIBILITY | 300 m (grigio) | slider | attiva solo con dust storm |
| Random preset | pulsante | — | il pannello ha una scrollbar: altri campi potrebbero stare più in basso |

---

## 20261005_112727.jpg — TRIGGERS

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| Lista TRIGGERS | 4 MISSION START (Trigger 2) … 4 MISSION START (Trigger 10); 1 ONCE (Trigger 11, NO EVENT) … 1 ONCE (Trigger 21, NO EVENT) | — | lista scorrevole; selezionato `1 ONCE (Trigger 12, NO EVENT)` |
| Pulsanti trigger | CLONE, ↑, ↓, NEW, DELETE | — | |
| TYPE | 1 ONCE | menu chiuso | |
| NAME | Trigger 12 | — | |
| EVENT | NO EVENT | menu chiuso | |
| COLOR | R 255, G 255, B 255 | tavolozza colori | |
| CONDITIONS (lista) | TIME MORE (2272.4672413242) | — | |
| Condizione – TYPE | TIME MORE | menu chiuso | |
| Condizione – SECONDS | 2272 | — | secondi dall'inizio missione |
| Pulsanti condizioni | CLONE, ↑, ↓, NEW, OR, DELETE | — | |
| ACTIONS (lista) | GROUP ACTIVATE (Pack 2 - VF-101 - Escort 1) | — | |
| Azione – ACTION | GROUP ACTIVATE | menu chiuso | |
| Azione – GROUP | Pack 2 - VF-101 - Escort 1 | menu chiuso | |
| Pulsanti azioni | CLONE, ↑, ↓, NEW, DELETE | — | |
| INITIALIZATION SCRIPT | (vuoto) | — | pulsanti OPEN, RESET, espandi; campo CODE vuoto |

Nota: lo schema "trigger ONCE + TIME MORE + GROUP ACTIVATE" è il modo con cui la missione attiva un gruppo in
late activation a un'ora data.

---

## 20261005_112741.jpg — MISSION GOALS

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| Lista obiettivi | Assign Mission Score (51, OFFLINE) | — | pulsante NEW |
| CONDITIONS | (vuoto) | — | pulsante NEW |

---

## 20261005_112749.jpg — BATTLEFIELD COMMANDERS

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| PILOT CAN CONTROL VEHICLES | ☐ | — | |
| MISSION/MULTIPLAYER ROLES – Red | GAME MASTER 0, TACTICAL CMDR 0, JTAC/Operator 0, OBSERVER 0 | — | ogni riga ha una casella `Lock` (tutte ☐) |
| Blue | GAME MASTER 0, TACTICAL CMDR 0, JTAC/Operator 0, OBSERVER 1 | — | Lock tutte ☐ |
| Neutrals | GAME MASTER 0, TACTICAL CMDR 0, JTAC/Operator 0, OBSERVER 0 | — | Lock tutte ☐ |
| Password Settings (Red/Blue/Neutrals × GAME MASTER, TACTICAL CMDR, JTAC/Operator, OBSERVER) | tutti vuoti | — | |

---

## 20261005_112835.jpg — BULLSEYE LOCATION

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| COALITION | RED | menu chiuso | un bullseye per coalizione |
| LAT | N 42°14'28" | — | |
| LONG | E 42°02'57" | — | |

---

## 20261005_113217.jpg — AIRPLANE GROUP + editor di azione: Set Option / Formation

Gruppo selezionato: **Pack 32 - F7 - Strike 1**, Sweden, 2 × AJS37.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| GROUP NAME | Pack 32 - F7 - Strike 1 | — | |
| CONDITION | (vuoto) % / 100 | — | |
| COUNTRY | Sweden | — | |
| TASK | Pinpoint Strike | — | |
| UNIT | 2 OF 2 | — | |
| TYPE | AJS37 | — | |
| SKILL | Trained | — | |
| PILOT | Pack 32 - F7 - Strike 1-2 | — | |
| TAIL # | 015 | — | |
| RADIO / FREQUENCY | ☑ / 346.425 MHz AM | — | |
| CALLSIGN | Springfield / 8 / 2 | — | |
| HIDDEN ON MAP / PLANNER / MFD | ☐ / ☐ / ☐ | — | |
| GAME MASTER ONLY / LATE ACTIVATION | ☐ / ☐ | — | la casella **UNCONTROLLED non compare**: il waypoint 0 è un `Turning point` (partenza in volo), per cui l'opzione non è disponibile |
| WAYPOINT | 0 OF 10 | — | |
| NAME | Departure | — | |
| TYPE | Turning point | — | partenza in volo, a differenza del Pack 19 (Takeoff from runway) |
| ALTITUDE | 621 m | `AGL (Rdr Alti…)` | |
| SPEED / MACH | 677 kmh / 0.565 | — | `GS` ☑ |
| START | 4 : 41 : 3 / 0 | — | `Fix time` ☑ |
| Lista azioni WP0 | 1. Formation = Spread Four Open (116 m x 97 m) 2. Run Script 3. Reaction to Threat = EVADE FIRE 4. Restrict Jettison = on | — | selezionata la 1 |
| **Editor di condizione (in alto)** | | | |
| TIME MORE | ☐ 4 : 41 : 3 / 0 (grigio) | — | |
| IS USER FLAG | ☐ 0 IS ☑ | — | flag numerica e valore booleano atteso |
| PROBABILITY | ☐ 100 % (grigio) | — | |
| CONDITION (LUA PREDICATE) | ☐, area di testo vuota | — | |
| **Editor di azione** | | | |
| TYPE | Set Option | menu chiuso | |
| ACTION | Formation | menu chiuso | |
| NUMBER | 1 | — | posizione nella lista |
| ENABLE TASK | ☑ | — | |
| NAME | (vuoto) | — | |
| CONDITION… | pulsante | — | |
| TYPE (formazione) | Spread Four | menu chiuso | |
| VARIANT | Open (116 m x 97 m) | menu chiuso | |

Mappa: zoom molto stretto (scala 90 m) su una pista di **Sukhumi-Babushara** con `0:Departure` e icone di
gruppi (`A`, `F`).

---

## 20261005_113232.jpg — editor di azione: Perform Command / Run Script

Stesso gruppo Pack 32, WP0 (stessi valori della foto precedente), azione 2 selezionata.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| TYPE | Perform Command | menu chiuso | |
| ACTION | Run Script | menu chiuso | |
| NUMBER | 2 | — | |
| ENABLE TASK | ☑ | — | |
| NAME | (vuoto) | — | |
| Testo dello script | `OrbitPosition("Pack 32 - F7 - Strike 1", 620.6, 167.22222222222, 187.06886121031)` | — | funzione non nativa di DCS (definita da uno script della missione); i parametri sembrano quota (≈621 m), velocità (167.2 m/s ≈ 602 km/h) e un terzo valore numerico, interpretazione da verificare |

---

## 20261005_113245.jpg — editor di azione: Set Option / Reaction to Threat

Stesso gruppo Pack 32, WP0, azione 3.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| TYPE | Set Option | — | |
| ACTION | Reaction to Threat | — | |
| NUMBER | 3 | — | |
| ENABLE TASK | ☑ | — | |
| Valore | EVADE FIRE | menu chiuso | |
| Tooltip | "List of actions / Note: actions will being performed in order they are enlisted!" | — | le azioni vengono eseguite nell'ordine della lista |

---

## 20261005_113303.jpg — editor di azione: Set Option / Restrict Jettison

Stesso gruppo Pack 32, WP0, azione 4.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| TYPE | Set Option | — | |
| ACTION | Restrict Jettison | — | |
| NUMBER | 4 | — | |
| ENABLE TASK | ☑ | — | |
| VALUE | ☑ | — | opzione booleana |

---

## 20261005_113356.jpg — waypoint 5 (Attack) + editor: Perform Task / Attack Map Object

Gruppo Pack 32 (campi del gruppo invariati).

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| WAYPOINT | 5 OF 10 | — | |
| NAME | Attack | — | |
| TYPE | Fly over point | — | |
| ALTITUDE | 5572 m | `MSL (Barome…)` | riferimento barometrico, diverso dai WP precedenti (AGL) |
| SPEED | 1262 kmh | — | `GS` ☑ |
| MACH | 1.119 | — | |
| ETA | 5 : 14 : 4 / 0 | — | `Fix time` ☐ |
| Lista azioni WP5 | 1.–5. Attack Map Object -x (la lista prosegue, scrollbar) | — | il suffisso `-x` compare sulle azioni con ENABLE TASK ☐ |
| Condizione: TIME MORE | ☐ 5 : 14 : 4 / 0 (grigio) | — | |
| IS USER FLAG | ☐ 0 IS ☑ | — | |
| PROBABILITY | ☐ 100 % (grigio) | — | |
| CONDITION (LUA PREDICATE) | ☐ vuoto | — | |
| TYPE | Perform Task | — | |
| ACTION | Attack Map Object | — | |
| NUMBER | 1 | — | |
| ENABLE TASK | ☐ | — | |
| NAME | (vuoto) | — | |
| CONDITION… / STOP CONDITION… | pulsanti | — | per i Perform Task c'è anche STOP CONDITION |
| WEAPON | Auto | menu chiuso | |
| REL QTY | All | menu chiuso | |
| MAX ATTACK QTY | ☐ 1 (grigio) | — | |
| GROUP ATTACK | ☑ | — | |
| DIRECTION FROM | ☐ 0° | quadrante grafico | |
| ALTITUDE ABOVE | ☐ 5572 m (grigio) | — | |

Mappa: zoom (scala 2 km) su **Beslan** (rosso); bersagli `Attack Map Object` (edifici) a est, `5:Attack` in
giallo, beacon 1050.00 kHz CX e 250.00 kHz, quadrato MGRS MN68.

---

## 20261005_113405.jpg — STOP CONDITION del task Attack Map Object

Stesso contesto della foto precedente; la sezione condizione mostra ora la stop condition (tooltip
"The condition to stop the task").

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| TIME MORE | ☐ 5 : 29 : 4 / 0 | — | 15 minuti dopo l'ETA del waypoint |
| IS USER FLAG | ☐ 0 IS ☑ | — | |
| PROBABILITY | ☐ 100 % (grigio, etichetta grigia) | — | |
| CONDITION (LUA PREDICATE) | ☐ vuoto | — | |
| DUR | ☐ 0 : 15 : 0 / 0 | — | durata massima del task, presente solo nella stop condition |
| Restanti campi | come foto 113356 (Perform Task / Attack Map Object, n. 1, ENABLE TASK ☐, WEAPON Auto, REL QTY All, GROUP ATTACK ☑, ALTITUDE ABOVE 5572 m grigio) | — | |

---

## 20261005_113421.jpg — editor di azione: Perform Command / Run Script (attacco a oggetti mappa)

Gruppo Pack 32, WP5.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| Lista azioni WP5 (scorsa in fondo) | 7.–10. Attack Map Object -x, 11. Run Script | — | quindi 10 task `Attack Map Object` disabilitati + 1 script |
| TYPE | Perform Command | — | |
| ACTION | Run Script | — | |
| NUMBER | 11 | — | |
| ENABLE TASK | ☑ | — | |
| Testo dello script | `CustomMapObjectAttack("Pack 32 - F7 - Strike 1", {{ x = -148962.921875, y = 843620.0625}, { x = -148993.71875, y = 843839.625}, { x = -149028.84375, y = 843837.375}, { x = -149005.96875, y = 843724.125}, { x = -149021.625, y = 844018.875}, { x = -149043.3125, y = 844111.125}, { x = -149049.53125, y = 844187}, { x = -148948.96875, y = 843511.75}, { x = -149149.171875, y = 843921.…` (il resto è fuori dall'area visibile) | — | lista di coordinate interne DCS (x, y in metri) degli oggetti da attaccare; funzione non nativa |

Mappa: come foto 113356; etichetta `7. Attack Map Object` sui bersagli.

---

## 20261005_113547.jpg — AIRPLANE GROUP F-4E + editor: Perform Task / Attack Group

Gruppo selezionato: **Pack 10 - VMFA-159 - Strike 1**, USA (Blue).

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| GROUP NAME | Pack 10 - VMFA-159 - Strike 1 | — | |
| CONDITION | (vuoto) % / 100 | — | |
| COUNTRY | USA | — | |
| TASK | CAS | — | |
| UNIT | 4 OF 4 | — | |
| TYPE | F-4E | — | testo del tipo in **rosso** (significato non verificato, forse modulo non installato/disponibile) |
| SKILL | Trained | — | |
| PILOT | Pack 10 - VMFA-159 - Strike 1-4 | — | |
| TAIL # | 014 | — | |
| RADIO / FREQUENCY | ☑ / 369.4 MHz AM | — | |
| CALLSIGN | Dodge / 7 / 4 | — | |
| HIDDEN ON MAP / PLANNER / MFD | ☐ / ☐ / ☐ | — | |
| GAME MASTER ONLY / UNCONTROLLED / LATE ACTIVATION | ☐ / ☑ / ☐ | — | |
| Tab | solo 4 (Route, Payload, Triggered Actions, Σ) | — | manca la tab `…`: l'F-4E qui non ha proprietà aggiuntive |
| WAYPOINT | 5 OF 10 | — | |
| NAME | Attack | — | |
| TYPE | Fly over point | — | |
| ALTITUDE | 2572 m | `MSL (Barome…)` | |
| SPEED / MACH | 999 kmh / 0.853 | — | `GS` ☑ |
| ETA | 6 : 20 : 21 / 0 | — | `Fix time` ☐ |
| Lista azioni WP5 | 1. Attack Group("LENIGORI FARP MM56") -x  2. Attack Group("LENIGORI FARP MM56 - 1") -x  3. Attack Group("LENIGORI FARP MM56 - 2") -x  4. Attack Group("LENIGORI FARP MM56 - 3") -x  5. Run Script | — | |
| Condizione: TIME MORE | ☐ 6 : 20 : 21 / 0 (grigio) | — | |
| IS USER FLAG / PROBABILITY / LUA PREDICATE | ☐ 0 IS ☑ / ☐ 100 % / ☐ | — | |
| TYPE | Perform Task | — | |
| ACTION | Attack Group | — | |
| NUMBER | 1 | — | |
| ENABLE TASK | ☐ | — | |
| CONDITION… / STOP CONDITION… | pulsanti | — | |
| GROUP | (vuoto) | menu chiuso | il gruppo bersaglio non risulta nel menu, pur comparendo nel nome dell'azione; il bersaglio potrebbe non esistere più nella missione o essere statico (interpretazione) |
| WEAPON | -Bombs | menu chiuso | categoria di armi |
| REL QTY | All | menu chiuso | |
| MAX ATTACK QTY | ☐ 1 | — | |
| GROUP ATTACK | ☐ | — | |
| DIRECTION FROM | ☐ 0° | — | |
| ALTITUDE ABOVE | ☐ 2572 m (grigio) | — | |

Mappa: zona di Tskhinvali–Karaleti–Ruisi–Khashuri (Georgia centrale), molte zone circolari rosse (probabilmente
raggi di minaccia/ingaggio di difese aeree), riquadro rosso `5(5) 8(5)` in alto, rotte con `2:Nav`, `3:AI
Descend Helper`, `4:IP`, `5:Attack`, `6:Egress`, `7:Nav`, `2:Station`; località Leningori/Ikoti a est.

---

## 20261005_113619.jpg — editor di azione: Perform Command / Run Script (attacco a statici)

Gruppo Pack 10 - VMFA-159 - Strike 1 (stessi valori della foto precedente), WP5, azione 5.

| Campo | Valore visibile | Opzioni del menu (se visibili) | Note |
|---|---|---|---|
| TYPE | Perform Command | — | |
| ACTION | Run Script | — | |
| NUMBER | 5 | — | |
| ENABLE TASK | ☑ | — | |
| Testo dello script | `CustomStaticAttack("Pack 10 - VMFA-159 - Strike 1", {"LENIGORI FARP MM56", "LENIGORI FARP MM56 - 1", "LENIGORI FARP MM56 - 2", "LENIGORI FARP MM56 - 3", }, "All", "2032", "nil", 2572)` | — | funzione non nativa; parametri: gruppo, lista di oggetti statici, quantità di rilascio ("All"), un codice arma/flag ("2032", significato da verificare), direzione ("nil"), quota (2572 = ALTITUDE del WP) |

Spiegazione plausibile, da verificare sul `.miz`: i task nativi `Attack Group` / `Attack Map Object` sono
lasciati disabilitati (`-x`) e l'attacco reale è delegato agli script `Custom*Attack`.

---

# Catalogo degli input del Mission Editor

Campi visti nelle foto, raggruppati per pannello e senza duplicati. "Valori visti" riporta solo ciò che compare
nelle foto, non l'elenco completo delle opzioni DCS (nessun menu a tendina era aperto in nessuna foto).

### AIRPLANE GROUP (intestazione del gruppo)

| Campo | Tipo di input | Valori visti |
|---|---|---|
| GROUP NAME | testo | Pack 19 - F7 - Anti-ship Strike 1; Pack 32 - F7 - Strike 1; Pack 10 - VMFA-159 - Strike 1 |
| CONDITION | testo + spinner % | vuoto / 100 |
| COUNTRY | menu (determina la coalizione) | Sweden, USA |
| COMBAT | pulsante | — |
| TASK | menu | Anti-ship Strike, Pinpoint Strike, CAS |
| UNIT … OF … | spinner (unità corrente / numero di unità) | 2/2, 4/4 |
| TYPE | menu | AJS37, F-4E |
| SKILL | menu | Veteran, Trained |
| PILOT | testo (nome unità) | `<group name>-<n>` |
| TAIL # | testo | 034, 015, 014 |
| RADIO | checkbox | ☑ |
| FREQUENCY + modulazione | numero MHz + menu | 269.9 / 346.425 / 369.4, AM |
| CALLSIGN | menu nome + numero volo + numero membro | Ford 7 2, Springfield 8 2, Dodge 7 4 |
| HIDDEN ON MAP / HIDDEN ON PLANNER / HIDDEN ON MFD | checkbox | ☐ |
| GAME MASTER ONLY | checkbox | ☐ |
| UNCONTROLLED | checkbox (solo con partenza a terra) | ☑ |
| LATE ACTIVATION | checkbox | ☐ |

### Tab Route (waypoint)

| Campo | Tipo di input | Valori visti |
|---|---|---|
| WAYPOINT n OF N | selettore | 0, 4, 5 di 10 |
| NAME | testo | Departure, IP, Attack (sulla mappa anche Join, Nav, AI Descend Helper, Egress, Split, Station) |
| TYPE | menu | Takeoff from runway, Turning point, Fly over point |
| ALTITUDE + riferimento | numero (m) + menu | 621, 1000, 2572, 5572; AGL (Rdr Alti…), MSL (Barome…) |
| SPEED + GS | numero (kmh) + checkbox ground speed | 677, 776, 903.6, 999, 1262 |
| MACH | numero (legato a SPEED) | 0.565 – 1.119 |
| START (WP0) / ETA (altri WP) | h : m : s / giorno | 5:4:54/0, 4:41:3/0, 5:36:24/0, 5:37:24/0, 5:14:4/0, 6:20:21/0 |
| Fix time | checkbox | ☑ / ☐ |
| ADD / EDIT / DEL | pulsanti | — |
| ADVANCED (WAYPOINT ACTIONS) | lista ordinata di azioni | v. sotto |
| ADVANCED WP AUTO FILL | pulsante | — |

### Advanced Waypoint Actions (editor di azione)

| Campo | Tipo di input | Valori visti |
|---|---|---|
| TYPE | menu | Perform Task, Perform Command, Set Option |
| ACTION | menu (dipende da TYPE) | Perform Task: Attack Group, Attack Map Object (in lista anche Anti-Ship); Perform Command: Run Script (in lista anche Start); Set Option: Formation, Reaction to Threat, Restrict Jettison |
| NUMBER | spinner (ordine di esecuzione) | 1–11 |
| ENABLE TASK | checkbox (☐ ⇒ suffisso `-x` nella lista) | ☑ / ☐ |
| NAME | testo | vuoto |
| CONDITION… | pannello | TIME MORE (h:m:s/g), IS USER FLAG (n. flag + IS ☑/☐), PROBABILITY (%), CONDITION (LUA PREDICATE) |
| STOP CONDITION… (solo Perform Task) | pannello | come CONDITION + DUR (h:m:s/g), es. 0:15:0/0 |
| Formation: TYPE / VARIANT | menu | Spread Four / Open (116 m x 97 m) |
| Reaction to Threat: valore | menu | EVADE FIRE |
| Restrict Jettison: VALUE | checkbox | ☑ |
| Run Script: testo | area di testo Lua | OrbitPosition(...), CustomMapObjectAttack(...), CustomStaticAttack(...) |
| Attack Group: GROUP | menu | vuoto |
| WEAPON | menu | Auto, -Bombs |
| REL QTY | menu | All |
| MAX ATTACK QTY | checkbox + spinner | ☐ 1 |
| GROUP ATTACK | checkbox | ☑ / ☐ |
| DIRECTION FROM | checkbox + angolo (°) | ☐ 0 |
| ALTITUDE ABOVE | checkbox + quota (m) | ☐ quota del WP |
| Lista azioni: ADD, INS, EDIT, DEL, UP, DOWN, CLONE | pulsanti | — |

### Tab Payload (PAINT AND LOADOUT)

| Campo | Tipo di input | Valori visti |
|---|---|---|
| PAINT SCHEME | menu | #1 Splinter F21 Norrbottens Flygflottilj |
| PAYLOAD RESTRICTION | checkbox | ☐ |
| Mission payload (per pilone 1…7) | griglia di icone | piloni 3, 4, 5 carichi |
| Carichi predefiniti | lista (filtrata per task) | 6 carichi anti-ship AJS37 + Empty |
| NEW / COPY / DELETE / RENAME / EXPORT | pulsanti | — |
| CIVIL PLANE | checkbox | ☐ |
| INTERNAL FUEL | slider + % | 100 % |
| FUEL WEIGHT / EMPTY / WEAPONS / TOTAL | kg (calcolati) | 5489 / 10749 / 448 / 16686 |
| MAX | kg | 20000 (83 %) |
| CHAFF / FLARE | spinner | 210 / 72 (grigi) |

### Tab Triggered Actions

Lista di azioni come le waypoint actions (vista: `Start "<gruppo>"`), con ADD/INS/EDIT/DEL/UP/DOWN/CLONE.

### Tab Summary (Σ)

START TIME, ROUTE TIME, ROUTE LENGTH, AVERAGE SPEED — sola lettura.

### Tab `…` (proprietà specifiche del modulo, AJS37)

RB-04 Group Target Selection (Random), RB-04 Angle Jump Target Selection (None), Weapon safety height (Medium),
Cartridge restrictions (Allow all).

### BRIEFING

SORTIE (testo), liste paesi Red / Blue, BRIEFING IMAGES PANEL, SITUATION, RED TASK, BLUE TASK, NEUTRALS TASK
(testi liberi).

### TIME AND WEATHER

START (giorno, mese, anno, h:m:s), slider ±1 h, Sun And Moon, STATIC/DYNAMIC, T °C, preset nubi + BASE (m), QNH
(mmHg), ICE HALO APPEARANCE, vento a 8000 / 2000 / 500 / 10 m (velocità m/s + direzione "blows to" °),
TURBULENCE (m/s), FOG MODE, DUST STORM ENABLE + VISIBILITY (m), Random preset.

### TRIGGERS

Trigger: TYPE (1 ONCE, 4 MISSION START visti), NAME, EVENT (NO EVENT), COLOR (RGB). Conditions: TYPE (TIME MORE),
SECONDS; pulsante OR. Actions: ACTION (GROUP ACTIVATE), GROUP. INITIALIZATION SCRIPT (OPEN/RESET/CODE).

### MISSION GOALS

Lista obiettivi (es. Assign Mission Score (51, OFFLINE)) + CONDITIONS.

### BATTLEFIELD COMMANDERS

PILOT CAN CONTROL VEHICLES; per Red/Blue/Neutrals: numero di slot GAME MASTER, TACTICAL CMDR, JTAC/Operator,
OBSERVER con Lock; password per ruolo e coalizione.

### BULLSEYE LOCATION

COALITION, LAT, LONG.

---

# Rilevanza per Warfare-Model

**Dati di missione che il motore di campagna deve produrre** (decisioni del pianificatore, cambiano a ogni
sessione):

- gruppo: nome, paese/coalizione, task principale, numero di unità, condizione (probabilità di presenza),
  partenza controllata o no (UNCONTROLLED), LATE ACTIVATION;
- rotta: sequenza di waypoint con tipo (Takeoff from runway / Turning point / Fly over point), quota con
  riferimento AGL o MSL, velocità (GS), START/ETA con Fix time. Corrisponde a `DataType.Route/Waypoint` più il
  profilo di attacco (`AttackProfile`) della Proposta B: la quota e la velocità al waypoint di attacco e
  DIRECTION FROM / ALTITUDE ABOVE sono esattamente i parametri di consegna dell'arma;
- azioni ai waypoint, in ordine: formazione, regole di reazione alla minaccia (EVADE FIRE), Restrict Jettison,
  task di attacco con bersaglio (gruppo, oggetto mappa, statico), WEAPON (categoria), REL QTY, GROUP ATTACK,
  condizioni di avvio e di stop (TIME MORE, user flag, probabilità, DUR);
- carico scelto (preset per pilone), carburante interno %, chaff/flare: devono derivare dalla scorta per modello
  d'arma (`Weapon_Stores.py`) e dal modello di carburante (`Fuel_Model.py`);
- trigger di attivazione temporizzata (ONCE + TIME MORE + GROUP ACTIVATE): il modo per tradurre in DCS la
  cadenza dell'ATO (decollo a ora data);
- data, ora di inizio e meteo (T, nubi, QNH, vento per quota, turbolenza, nebbia): uscita naturale di
  `Meteo_Analysis.py`;
- briefing (situazione, ATO testuale con sortite e TOT per coalizione), bullseye per coalizione, ruoli
  multiplayer;
- callsign, frequenza radio, tail number, nomi di pilota e gruppo: dati amministrativi senza valore tattico, ma
  da generare in modo coerente e univoco.

**Dati di asset già noti al progetto** (registri esistenti, non decisioni di missione): tipo di aereo, peso a
vuoto e massimo, capacità di carburante, preset di carico ammessi per tipo e task (`Aircraft_Loadouts`), armi
per pilone, quote e velocità/Mach operative, livello di skill (equivalente all'esperienza dell'equipaggio),
proprietà specifiche del modulo (RB-04, Weapon safety height). Sono dati che `Aircraft_Data` / i registri d'arma
già descrivono o dovrebbero descrivere.

**Solo interfaccia** (non vanno generati): HIDDEN ON MAP/PLANNER/MFD (salvo scelte di nebbia di guerra per i
giocatori), PAINT SCHEME, COLOR dei trigger, pulsanti di editing (ADD/INS/CLONE/EXPORT…), ADVANCED WP AUTO FILL,
tab Summary (valori calcolati), barra di stato, Random preset meteo, BRIEFING IMAGES PANEL.

**Osservazioni utili per il generatore:**

1. La missione fotografata delega gli attacchi reali a funzioni Lua personalizzate (`OrbitPosition`,
   `CustomMapObjectAttack`, `CustomStaticAttack`) e lascia disabilitati (`-x`) i task nativi di attacco. Le
   funzioni non sono native di DCS: vanno cercate nell'initialization script o nei file Lua dentro il `.miz`
   prima di decidere se Warfare-Model userà task nativi o script.
2. I bersagli "map object" sono passati come coordinate interne DCS (x, y in metri): il generatore deve saper
   convertire le posizioni degli asset nel sistema di coordinate della mappa DCS.
3. UNCONTROLLED esiste solo per i gruppi che partono a terra; con partenza in volo (`Turning point` al WP0) la
   casella sparisce.
4. Le azioni di un waypoint vengono eseguite nell'ordine della lista (tooltip del ME), quindi l'ordine è un dato
   di missione.
5. La stop condition di un task ha in più il campo DUR: serve a limitare la durata di un attacco o di
   un'orbita, ed è un parametro naturale per il motore DES.
