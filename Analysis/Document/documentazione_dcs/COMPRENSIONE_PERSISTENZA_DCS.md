# Report di comprensione — persistenza dei risultati di missione e API Lua in DCS

Documento di **auto-verifica**, richiesto per valutare quanto ho effettivamente capito.
Non è un tutorial: ogni affermazione porta l'etichetta della sua fonte e, dove serve, il
livello di confidenza. Complementare a `ANALISI_DCE.md` (che descrive *come DCE risolve il
problema*); questo descrive *cosa DCS offre e quali sono i vincoli reali*.

**Legenda delle fonti**

| Tag | Significato |
|---|---|
| `[CODICE]` | letto direttamente nel sorgente DCE in questa sessione — verificabile riga per riga |
| `[DATI]` | verificato su file di dati reali della campagna (log eventi, `.miz`, file di stato) |
| `[DOC-LOC]` | documentazione ED locale in `documentazione_dcs/dcs_lua/*.md` |
| `[WEB]` | ricerca web (Hoggitworld, pydcs, MiST, MOOSE, forum ED) — seconda mano |
| `[INFER]` | mia inferenza dai precedenti, non un fatto riportato da una fonte |

---

## Parte 1 — Il modello mentale della persistenza in DCS

### 1.1 La tesi centrale

**DCS non ha un sistema di campagna dinamica. Ha un simulatore di singole missioni, con un
solo canale di uscita strutturato (il `debrief.log`) che è debole, e una sandbox Lua che
permette di costruirsi il proprio.** Ogni motore di campagna serio — DCE, DCS Liberation —
finisce per ignorare il canale nativo e costruirsi il proprio meccanismo di export.

Ne discende il punto che considero il più importante da aver capito:

> **Una missione DCS è senza stato in ingresso e quasi senza stato in uscita.** Tutto lo
> stato di campagna vive *fuori* da DCS, e viene **iniettato** nella missione riscrivendo il
> `.miz`, non impostato via API. Il `.miz` è l'unica interfaccia di scrittura verso DCS.

Questo ha una conseguenza di progetto per Warfare-Model: non esiste un "salva partita" da
chiamare. Il ciclo è necessariamente
**stato esterno → genera `.miz` → DCS gioca → esporta eventi → aggiorna stato esterno**,
e il costo architetturale sta tutto nei due lati della conversione.

### 1.2 Il ciclo completo, passo per passo

```
   [stato esterno]                                         [dentro DCS]
        │
   (1)  ├─ leggi stato campagna
   (2)  ├─ unzip template.miz → tabelle Lua                 
   (3)  ├─ muta le tabelle (unità, meteo, data, trigger)
   (4)  ├─ inietta lo script di cattura nel .miz
   (5)  └─ zip → missione.miz  ────────────────────────────▶ (6) caricamento
                                                             (7) trigger triggerStart
                                                                 → a_do_script_file
                                                             (8) world.addEventHandler
                                                             (9) ... gioco ...
                                                            (10) S_EVENT_MISSION_END
   (12) ◀────── file di export su disco ◀───────────────────(11) io.open():write()
   (13) parsing eventi → aggiorna stato
   (14) → torna a (1)
```

Punti di attenzione che ho verificato:

- **(3)** la mutazione avviene su **tabelle Lua in memoria**, non su testo. `mission`,
  `options`, `warehouses`, `dictionary`, `mapResource` sono sorgente Lua eseguibile:
  `loadstring(contenuto)()` le carica come globali, poi si riserializzano. `[CODICE]`
  `MAIN_NextMission.lua:56-78` e `418-422`.
- **(4)** l'iniezione richiede **tre strutture sincronizzate**: `mapResource["ResKey_Action_n"]`
  (risoluzione nome file), `mission.trig.{flag,conditions,actions,funcStartup}[n]`
  (esecuzione runtime) e `mission.trigrules[n]` (rappresentazione per il Mission Editor).
  `[CODICE]` `AddFileTrigger`, `MAIN_NextMission.lua:147-174`.
- **(11)** la scrittura su disco **richiede la de-sanitizzazione** di `MissionScripting.lua`
  se fatta dallo script di missione. `[CODICE]` + `[WEB]`
- **(12)** il passaggio da DCS al processo esterno in DCE è
  `os.execute('start cmd /k ... luae.exe DEBRIEF_Master.lua')`: Windows-only, via shell.
  `[CODICE]` `EventsTracker.lua:285`.

### 1.3 I tre modi di far uscire dati da una missione

Questa è la tassonomia che considero il vero risultato dell'analisi.

| # | Meccanismo | Ambiente | Sandbox | Struttura dati | Verdetto |
|---|---|---|---|---|---|
| 1 | **`debrief.log` nativo** | motore DCS | n/a | eventi, ma formato instabile SP/MP | insufficiente da solo |
| 2 | **Export custom da Mission Scripting** | script nel `.miz` | **sì**, va de-sanitizzato | qualsiasi — la decidi tu | ciò che fa DCE |
| 3 | **Export da Hooks** | `Scripts/Hooks/*.lua` | **no** | qualsiasi + `DCS.getMissionResult` | il più robusto, DCE non lo usa |

**Il canale 1 è molto più ricco di quanto credessi** `[DATI]`. Avendo ora analizzato un
`debrief.log` reale (427 KB, singleplayer, DCS 2.9.29.27468) **correggo il giudizio che avevo
dato**: contiene dieci chiavi di primo livello, fra cui

- **`world_state`** — stato finale di **ogni** unità: `unitId`, posizione, `dead`, **`life`**
  (danno parziale), e per gli aerei **`payload`** con carburante e munizioni residue;
- **`graveyard`** — relitti con posizione e assetto;
- `warehouses`, `triggers_state` (flag con valore finale e istante), `result` (0–100);
- **`events`** con `event_id` / **`linked_event_id`**, cioè la **catena causale esplicita**
  `shot → hit → kill → score` (17 link su 17 risolti nel campione), più `weapon_type`,
  `ammo_consumption`, `failure`, `ai abort mission`.

**DCS fornisce quindi l'attribuzione dei kill già fatta**, e lo stato finale di ogni unità.
DCE ricostruisce entrambe le cose a mano, peggio.

**I limiti reali del canale 1** sono due, non quattro:
- non registra gli oggetti di **scenery** distrutti — motivazione dichiarata in
  `EventsTracker.lua:269` `[CODICE]`, e confermata: nel file reale non c'è traccia di scenery;
- in **multiplayer** il formato degenera in righe testuali `event:type=...` non ben formate
  `[WEB]`; `dcs_liberation` mantiene un parser regex di fallback per questo.

Due insidie pratiche che ho verificato di persona `[DATI]`:
- il file è valido **solo in Lua 5.1**: `world_state` ha un campo chiamato **`goto`**, parola
  riservata da Lua 5.2 in poi. Lupa (Lua 5.5) lo rifiuta finché non si quotano le chiavi
  riservate. Codifica **cp1252**.
- il giocatore **non** si riconosce da `initiatorPilotName` (per l'IA contiene il tipo di
  unità), ma dall'evento `under control` con `target = 'player'`.

**Perché il canale 3 è superiore al 2** `[WEB]`, e perché lo segnalo come raccomandazione
principale per Warfare-Model:
- `io`/`lfs` sono disponibili **senza toccare `MissionScripting.lua`** — quindi niente
  riapplicazione a ogni update DCS, e nessuna esposizione a codice arbitrario da server terzi;
- l'environment **sopravvive al cambio missione**, mentre lo script di missione è ricreato;
- dà `DCS.getMissionResult(side)` (esito 0–100 dichiarato dal simulatore),
  `DCS.getCurrentMission()`, `DCS.getMissionFilename()`, `DCS.writeDebriefing(str)`;
- dà i callback di rete (`onPlayerConnect`, `onPlayerChangeSlot`, `onSimulationStop`) e
  **`net.get_player_info(id).ucid`**, l'unico identificatore di giocatore stabile fra
  sessioni.

Il limite del canale 3 `[INFER]`: **gli eventi di combattimento non arrivano lì**. `world.event`
vive nel Mission Scripting environment. Serve quindi un'architettura ibrida, e il ponte fra i
due ambienti (che non condividono globali) è il problema tecnico da risolvere — via `env.info()`
con prefisso riconoscibile intercettato dall'hook, oppure accettando la de-sanitizzazione.

### 1.4 Cosa DCS **non** persiste, e va ricostruito

Verificato leggendo cosa DCE è costretto a fare a mano:

| Cosa manca | Workaround DCE | Fonte |
|---|---|---|
| Danno parziale alle navi fra missioni | campiona `getLife()` a inizio/fine; alla missione dopo applica `trigger.action.explosion()` in loop finché la salute non riscende al valore salvato | `[CODICE]` `EventsTracker.lua:199-230, 336-356` |
| Scenery distrutto | traccia in due fasi (hit → registra; dead → aggiungi coordinate), poi ricrea trigger zone di raggio 1 con `a_scenery_destruction_zone(zone, 100)` | `[CODICE]` `EventsTracker.lua:288-311`, `MAIN_NextMission.lua:103-141` |
| Relitti dei veicoli distrutti | converte ogni unità `dead` in un gruppo statico "Dead Static" con `hidden = true` | `[CODICE]` `DC_UpdateOOBGround.lua:29-130` |
| Contenuto dei warehouse (carburante, munizioni) | — **non è pilotabile via scripting**, va riscritto nel `.miz` offline | `[WEB]` |
| Meteo della sessione successiva | riscritto nel blocco `mission.weather` del `.miz` | `[CODICE]` `DC_Weather.lua` |
| Stato del giocatore fra sessioni | tabella `clientstats` mantenuta fuori, indicizzata per nome giocatore | `[CODICE]` + `[DATI]` |

Il pattern comune: **DCS non permette di istanziare un'unità in uno stato intermedio.** Puoi
crearla viva o morta, non al 40% di salute. Ogni forma di danno persistente è un workaround.

### 1.5 Il problema dell'identità — dove ho capito che sta il rischio maggiore

Tre spazi di nomi distinti, che vanno tenuti allineati `[DATI]` `[WEB]`:

| Identificatore | Stabile? | Dove vive |
|---|---|---|
| `Unit.getID()` — **runtime ID** | **no**, solo nella sessione | eventi live |
| **mission ID** (assegnato dall'editor) | sì, finché il `.miz` non è rigenerato | `unitId` nel file `mission`; `initiatorMissionID` nel log |
| **nome unità** (stringa) | dipende dalla convenzione del generatore | tutto |

DCE rigenera il `.miz` a ogni missione, quindi **anche i mission ID cambiano**: di fatto
l'unico identificatore stabile che gli resta è **il nome**. Da lì la convenzione
`Pack <n> - <squadriglia> - <task> <volo>-<gregario>` `[DATI]` e la risoluzione per
sottostringa:

```lua
string.find(events[e].initiator, " " .. killer_unit.name .. " ", 1, true)
```
`[CODICE]` `DEBRIEF_StatsEvaluation.lua:280+`

**È il punto più fragile dell'intero sistema** `[INFER]`: se un nome squadriglia è
sottostringa di un altro, le statistiche vengono attribuite alla squadriglia sbagliata,
silenziosamente. Per Warfare-Model la lezione è: **assegnare un ID di dominio stabile,
generato dal motore di campagna e trasportato nel nome dell'unità in una posizione parsabile**
(es. un prefisso o un suffisso delimitato), invece di affidarsi al match di sottostringa.

In multiplayer si aggiunge un quarto spazio di nomi: l'identità del **giocatore**.
`getPlayerName()` non è stabile (il giocatore può rinominarsi) e su moduli multi-crew può
restituire il nome del RIO `[WEB]`. L'identificatore corretto è **`ucid`**, accessibile solo
lato server dall'ambiente Hooks — che è un'altra ragione a favore dell'architettura ibrida.

### 1.6 Semantica degli eventi — le trappole

| Trappola | Dettaglio | Fonte |
|---|---|---|
| `hit` senza `initiator` | collisioni e impatti col terreno generano `S_EVENT_HIT` senza iniziatore; se non li filtri inquinano l'attribuzione dei kill | `[CODICE]` `EventsTracker.lua:160` |
| `weapon` può essere `nil` in MP | anche su un `S_EVENT_HIT` valido, per desync/timing | `[WEB]` |
| `health` solo per aerei | DCE calcola `ceil(100/getLife0()*getLife())` solo se `getGroup():getCategory()` è 0 o 1 — mezzi terrestri e navi non hanno percentuale di danno negli eventi | `[CODICE]` `EventsTracker.lua:180-186` |
| `takeoff` multipli | un touch-and-go genera più eventi; DCE conta la missione solo al primo | `[CODICE]` |
| `t` è tempo modello | non ora di campagna; la durata reale è `events[#events].t - events[1].t` | `[CODICE]` + `[DATI]` |
| `eject` doppio | nel log campione compaiono due `eject` consecutivi per lo stesso aereo a 1 s di distanza (biposto, o due fasi del seggiolino) | `[DATI]` |
| Attribuzione kill | DCE usa "last hitter wins": `hit_table[target] = initiator`, sovrascritto a ogni hit. Sistematicamente sbagliato nel fuoco combinato | `[CODICE]` |

Su quest'ultimo punto: **DCS espone `S_EVENT_KILL` (id 28)**, cioè l'attribuzione fatta dal
simulatore `[WEB]`. DCE non lo usa — plausibilmente perché non esisteva nella versione di
riferimento del 2020 `[INFER]`. Per Warfare-Model userei quello, con `hit_table` come
fallback.

### 1.7 Copertura: DCE cattura 19 eventi su 61

`world.event` espone **61 costanti** (0–60, più `S_EVENT_MAX = 61`) `[WEB]`.
`EventsTracker.lua` ne mappa **19** `[CODICE]`. Fra gli ignorati, quelli che cambierebbero il
modello: `S_EVENT_KILL` (28), `S_EVENT_UNIT_LOST` (30), `S_EVENT_BDA` (37),
`S_EVENT_SHOOTING_START/END` (23/24), `S_EVENT_LANDING_QUALITY_MARK` (36),
`S_EVENT_EMERGENCY_LANDING` (43), `S_EVENT_MISSION_WINNER` (53),
`S_EVENT_WEAPON_ADD/REARM/DROP` (34/47/48). Elenco completo in `ANALISI_DCE.md` §A.2.

---

## Parte 2 — Le funzionalità Lua gestite da DCS

### 2.1 I tre ambienti — la distinzione che conta di più

| | Mission Scripting | GUI / Hooks | Export |
|---|---|---|---|
| **Dove** | dentro il `.miz` | `Saved Games\DCS\Scripts\Hooks\*.lua` | `Saved Games\DCS\Scripts\Export.lua` |
| **Come si esegue** | trigger `DO SCRIPT`/`DO SCRIPT FILE`, AI task `Script`/`Script File`, init script | caricato all'avvio di DCS | idem |
| **`os`/`io`/`lfs`** | **bloccati** (`sanitizeModule`) | disponibili | disponibili |
| **Vita** | ricreato a ogni missione | persiste | persiste |
| **Vede gli eventi di combattimento** | **sì** (`world.event`) | no | no |
| **API** | `world`, `coalition`, `trigger`, `Unit`, `Group`, `Controller`, `timer`, `env`, `land`, `atmosphere`, `coord`, `missionCommands`, `Airbase`, `StaticObject`, `Weapon`, `Spot`, `Warehouse`, `net`, `VoiceChat` | `DCS.*`, `net.*`, callback `on*` | `LoGet*`, `LuaExport*` |
| **Isolamento** | uno per missione | **ogni script Hooks in un environment isolato**: non condividono globali | — |

`[DOC-LOC]` per la colonna Mission Scripting (`Lua environment.md`, `Game objects.md`),
`[WEB]` per Hooks ed Export.

### 2.2 Superficie API del Mission Scripting environment

Estratta dalla documentazione ED locale `[DOC-LOC]`. Nota: è uno **snapshot datato** — ad
esempio `Unit.getLife0()`, che `EventsTracker.lua` usa, non compare in `Unit.md`. Va
considerata una base minima, non l'elenco attuale.

**Singleton**

| Singleton | Funzioni |
|---|---|
| `env` | `info`, `warning`, `error`, `setErrorMessageBoxEnabled` |
| `timer` | `getTime` (tempo modello), `getAbsTime` (tempo missione), `scheduleFunction`, `removeFunction`, `setFunctionTime` |
| `world` | `addEventHandler`, `removeEventHandler`, `getPlayer`, `getAirbases`, `searchObjects` |
| `coalition` | `addGroup`, `addStaticObject`, `getGroups`, `getStaticObjects`, `getAirbases`, `getPlayers`, `getServiceProviders`, `addRefPoint`, `getRefPoints`, `getMainRefPoint`, `getCountryCoalition` |
| `trigger.action` | `outText[ForCoalition/Country/Group]`, `outSound[...]`, `explosion`, `smoke`, `signalFlare`, `illuminationBomb`, `radioTransmission`, `setUserFlag`, `activateGroup`, `deactivateGroup`, `setGroupAIOn/Off`, `groupStopMoving/ContinueMoving`, `setAITask`, `pushAITask`, `addOtherCommand[...]`, `removeOtherCommand[...]` |
| `trigger.misc` | `getUserFlag`, `getZone` |
| `land` | `getHeight`, `getSurfaceType`, `isVisible`, `getIP`, `profile` |
| `atmosphere` | `getWind`, `getWindWithTurbulence` |
| `coord` | `LLtoLO`, `LOtoLL`, `LLtoMGRS`, `MGRStoLL` |
| `missionCommands` | `addCommand[ForCoalition/Group]`, `addSubMenu[...]`, `removeItem[...]` |

**Classi**

| Classe | Funzioni principali |
|---|---|
| `Object` (base) | `getName`, `getTypeName`, `getCategory`, `getDesc`, `getPoint`, `getPosition`, `getVelocity`, `inAir`, `isExist`, `destroy`, `hasAttribute` |
| `CoalitionObject` | `getCoalition`, `getCountry` |
| `Unit` | `getByName`, `getID`, `getNumber`, `getGroup`, `getController`, `getPlayerName`, `getLife` (+`getLife0`), `getFuel`, `getAmmo`, `getSensors`, `hasSensors`, `getRadar`, `getCallsign`, `isActive`, `getDesc` |
| `Group` | `getByName`, `getID`, `getName`, `getCategory`, `getCoalition`, `getUnit`, `getUnits`, `getSize`, `getController`, `isExist`, `destroy` |
| `Airbase` | `getByName`, `getID`, `getCallsign`, `getUnit`, `getDescByName` |
| `StaticObject` | `getByName`, `getID`, `getDesc` |
| `Weapon` | `getLauncher`, `getTarget`, `getDesc` |
| `Controller` | tasking, comandi, opzioni AI; **detection** (vedi sotto) |

**`Object.Category`** — le categorie che contano per il filtraggio degli eventi
(`[CODICE]`, uso reale in `EventsTracker.lua`): `UNIT`, `WEAPON`, `SCENERY` (valore
numerico **5**, usato direttamente nel codice), `STATIC`, `BASE`. Le categorie di **gruppo**
sono diverse: `0` = aereo, `1` = elicottero (usate per decidere se calcolare `health`).

### 2.3 Detection e fog of war — rilevante per `use_recon` di Warfare-Model

`Controller` espone un modello di rilevamento a informazione parziale `[DOC-LOC]`:

```lua
Controller.Detection = { VISUAL, OPTIC, RADAR, IRST, RWR, DLINK }

Controller.isTargetDetected(self, target, [detection1, ...])
  → detected, visible, lastTime, type, distance, lastPos, lastVel

Controller.getDetectedTargets(self, [detection1, ...])
  → array di DetectedTarget { object, visible, type, distance }

Controller.knowTarget(self, object, type, distance)   -- forza la conoscenza
```

La semantica è **esattamente la gradazione di conoscenza parziale** del modello fog-of-war:
un target può essere `detected` ma non `visible` (allora valgono `lastPos`/`lastTime`/
`lastVel`), rilevato ma con `type` sconosciuto, rilevato ma con `distance` sconosciuta. Sono
quattro assi indipendenti di incertezza, per metodo di sensore.

Lo segnalo perché è **direttamente allineato al lavoro di Fase 2 su `use_recon` e
`Combat_Power_Estimation`**: DCS ha già il vocabolario per "so che c'è qualcosa lì, non so
cosa, e il dato ha età *t*". `knowTarget()` è inoltre il modo per **iniettare** intelligence
acquisita fuori sessione dentro la missione — l'equivalente runtime di
`Action.AddGroundTargetIntel(side)` di DCE.

Nota di cautela `[INFER]`: DCE **non usa** nessuna di queste funzioni. Non ho quindi evidenza
di prima mano sul loro comportamento reale — solo la documentazione.

### 2.4 Il modello temporale di DCS

| Concetto | API | Semantica |
|---|---|---|
| **Model time** | `timer.getTime()` | tempo che guida la simulazione; può essere fermato, accelerato, rallentato |
| **Mission time** | `timer.getAbsTime()` | model time + orario di inizio missione |
| **Real time** | `DCS.getRealTime()` (Hooks) | tempo reale dall'avvio di DCS |
| **Data di missione** | `mission.date = {Day, Month, Year}` | nel `.miz` |
| **Orario di inizio** | `mission.start_time` | secondi da mezzanotte |

`[DOC-LOC]` `Basic terms and types.md`, `[WEB]` per `DCS.getRealTime`.

Gli eventi portano `t = timer.getTime()`, cioè **model time**. Ne segue `[INFER]` che per
correlare eventi con l'ora di campagna serve conoscere `mission.start_time`, e che
**il tempo negli eventi non è direttamente confrontabile fra missioni diverse**.

DCE gestisce questo con tre scale separate `[CODICE]` `DC_Time.lua`:
`camp.time` (ora del giorno, per alba/tramonto), `camp.date` (calendario, per la narrativa),
`elapsed_time = (camp.day-1)*86400 + camp.time` (monotòno, per i processi continui come il
meteo sinottico). Trovo questa separazione corretta e da replicare.

### 2.5 Cosa DCS espone e cosa no — con una mia correzione

**Correzione a quanto avevo scritto prima.** Avevo affermato che non esiste API di scripting
per i warehouse. **Era sbagliato**: quel dato era fermo a DCS 2.8. Da **DCS 2.8.8
(~agosto 2023)** esiste una classe `Warehouse` completa `[WEB]`:

| Metodi d'istanza | Statici / correlati |
|---|---|
| `getInventory`, `getItemCount`, `addItem`, `setItem`, `removeItem` | `Warehouse.getByName` |
| `addLiquid`, `getLiquidAmount`, `setLiquidAmount`, `removeLiquid` | `Warehouse.getResourceMap` |
| `getOwner` | `Warehouse.getCargoAsWarehouse`, `Airbase.getWarehouse` |

più `autoCapture` / `autoCaptureIsOn` / `setCoalition` per lo stato di cattura basi.
`getInventory()` ritorna `{weapon, liquids, aircraft}`; liquidi: `0` jet fuel, `1` aviation
gasoline, `2` MW50, `3` diesel.

Conseguenza: DCE si è costruito una logistica parallela (`supply_tab`/`airbase_tab`) perché
nel 2020 **era l'unica strada possibile**; oggi non lo è più. Resta una scelta legittima
(disaccoppia il modello di campagna dal simulatore), ma è una scelta, non un obbligo.

**Quel che resta effettivamente vincolato:**

| | Runtime da Lua | Solo riscrivendo il `.miz` |
|---|---|---|
| Nebbia | **sì** — `world.weather.setFogThickness/setFogVisibilityDistance/setFogAnimation` (da 2.9.10, dic 2024) | — |
| Nuvole / preset | **no** — nessuna API trovata | sì |
| Vento, QNH, temperatura | non verificato | sì |
| Warehouse | **sì** (da 2.8.8) | sì |
| Unità già danneggiate | **no** — vivo o morto, nessuno stato intermedio | no (workaround: esplosioni) |

### 2.6 `Mission State Save` — la persistenza nativa che nel 2020 non c'era

Segnalo separatamente perché **cambia il quadro del progetto** e non lo conoscevo `[WEB]`.

Da **DCS 2.9.14.8222 (20 marzo 2025)** ED ha introdotto un salvataggio di stato di missione
che **genera un nuovo file `.miz`** applicando a una missione rigenerata gli eventi del
teatro: unità distrutte, data/ora, posizione corrente dei velivoli e waypoint. I warehouse
persistono. Funziona solo su missioni custom non protette. La roadmap 2026 ne annuncia
l'estensione a waypoint avanzati e comportamento IA.

Non è un save-game classico: è **concettualmente lo stesso ciclo di DCE**, ma nativo. Prima
di replicare l'intera pipeline di DCE varrebbe la pena capire quanta parte di quel lavoro
questo meccanismo già copre. Non l'ho approfondito — è il primo punto da chiarire.

Sempre dalla roadmap 2026: ED ha dichiarato una **Dynamic Campaign** in test interno, con
strumenti per interagire con l'Air Tasking Order. Non rilasciata.

### 2.7 Librerie di comunità — cosa risolvono davvero

| | MiST | MOOSE |
|---|---|---|
| **Event handling** | `mist.addEventHandler(f)` / `removeEventHandler(id)` — wrapper con ID rimovibile | classe `EVENT` + `_EVENTDISPATCHER`; `obj:HandleEvent(EVENTS.Dead)` + `obj:OnEventDead(data)` |
| **Scope** | globale | **per oggetto**: `UNIT` → una unità, `GROUP` → il gruppo, globale → tutto |
| **Database** | `mist.DBs.{unitsByName, unitsById, unitsByCat, groupsByName, humansByName, activeHumans, aliveUnits, zonesByName, navPoints}` | `_DATABASE` interno |
| **Oggetti morti** | **`mist.DBs.deadObjects`** con metatable `__newindex`: scrivendo una voce, recupera automaticamente i dati completi dell'unità al momento della morte | — |
| **Payload evento** | grezzo DCS | `EVENTDATA` molto ricco: `IniUnitName`, `IniGroupName`, `IniPlayerName`, **`IniPlayerUCID`**, `IniCoalition`, `IniTypeName`, `IniObjectCategory`, `Tgt*` equivalenti, `WeaponName`/`WeaponTypeName`/`WeaponCategory` |
| **Serializzazione** | `mist.utils.serialize`, `basicSerialize`, `tableShow` | — |
| **Persistenza su file** | **no** — si usa `io`/`lfs` direttamente | **no** — nessuna classe dedicata |

`[WEB]`. Conclusione che ne traggo `[INFER]`: **nessuna delle due risolve la persistenza.**
Risolvono la *raccolta* e la *normalizzazione* dei dati in sessione. `mist.DBs.deadObjects`
e `EVENTDATA.IniPlayerUCID` sono i due elementi che farebbero risparmiare più codice rispetto
all'approccio DCE — ma il salvataggio va comunque scritto a mano.

---

## Parte 3 — Confini della mia conoscenza

Sezione deliberata: quello che **non** so, e come lo verificherei.

### 3.1 Certezza alta — verificato su codice e dati in questa sessione

- Il meccanismo di cattura eventi di DCE, campo per campo, e i suoi filtri.
- Il formato dei tre file di export e i tipi di evento effettivamente presenti
  (contati su un log reale da 2808 eventi).
- Il formato interno del `.miz`: elenco entry, chiavi di `mission`, blocco `weather` prima e
  dopo la generazione — **estratto e ispezionato direttamente**.
- La logica di attribuzione kill, la propagazione della logistica, il modello meteo
  sinottico, il comandante AI: letti nel sorgente.
- La forma dei file di stato di campagna: **tutti e 14 caricati con lupa** e attraversati
  programmaticamente, non campionati (v. `ANALISI_DCE.md` §3.6).
- Il **`debrief.log` reale**: caricato e analizzato per intero — dieci chiavi di primo
  livello, schema di `world_state` (8 forme), 20 tipi di evento, catena `linked_event_id`
  verificata su tutti i link, vocabolario di `weapon`, `ammo_consumption`.
- La versione DCS di riferimento: **2.9.29.27468 build 559** (da `Logs/dcs.log`).

### 3.2 Certezza media — da fonti secondarie, non verificato da me

- L'elenco completo dei 61 `S_EVENT_*` con i rispettivi ID numerici. I nomi legati alle
  modalità MAC/LMS (51, 56) sono poco documentati.
- Il comportamento esatto dell'ambiente Hooks e la lista dei callback `DCS.*`. Proviene da un
  file di documentazione API di terze parti, non da documentazione ED ufficiale.
- I range di quota dei 30 preset nuvole (`pydcs`). **Ho però trovato una discrepanza reale**:
  la tabella di `DC_Weather.lua` diverge da `pydcs` su `Preset1` (4100 vs 4200) e
  `RainyPreset1` (2500 vs 2940). Non so quale delle due sia corretta rispetto a DCS attuale.
- `net.get_player_info` e i campi disponibili, incluso `ucid`.
- Il comportamento di `Controller.getDetectedTargets` / `knowTarget`: solo documentazione.

### 3.3 Non so — e va verificato empiricamente

1. ~~Il formato esatto del `debrief.log` singleplayer.~~ **RISOLTO** — analizzato un file
   reale, v. `ANALISI_DCE.md` §2.5. Resta da verificare **il formato multiplayer**, che le
   fonti descrivono come degenere e di cui non ho un campione.
2. ~~Se l'attribuzione dei kill sia fornita dal simulatore.~~ **RISOLTO** — sì: eventi `kill`
   con `linked_event_id` verso l'`hit`, ed eventi `score` con `amount`. Resta da verificare
   se `world.event.S_EVENT_KILL` sia ugualmente affidabile **dallo scripting in-mission**
   (il `debrief.log` è un canale diverso).
3. **Se l'ambiente Hooks possa davvero ricevere gli eventi di combattimento** per qualche via
   che non ho trovato. Se sì, l'architettura ibrida diventa superflua.
4. **Quale sia la versione di DCS di riferimento.** La documentazione locale in `dcs_lua/` è
   uno snapshot datato (manca `Unit.getLife0`, che il codice usa); DCE dichiara compatibilità
   2.7.0; le fonti web arrivano a 2.8. Il vincolo sui warehouse potrebbe essere cambiato.
5. **Come si comporta il sistema in multiplayer con server dedicato.** DCE ha modalità
   dedicate (`SinglePlayer with Dedicated Server`) e il codice segnala bug noti, ma non ho
   evidenza del comportamento reale.
6. **Il contenuto di `db_firepower.lua` (318 KB) e `db_loadouts.lua` (331 KB).** Non li ho
   aperti: sono tabelle dati, non logica. Se servono i modelli di firepower di DCE per
   confrontarli con quelli di Warfare-Model, è lì che guardare — ed è un'analisi a sé.
7. **`ATO_Generator.lua` (144 KB), `ATO_FlightPlan.lua` (175 KB), `ATO_RouteGenerator.lua`
   (131 KB), `DC_Briefing.lua` (75 KB), `DC_LoadoutsAssignment.lua` (108 KB).** Ho mappato
   il loro ruolo nella pipeline e letto i parametri di configurazione, ma **non ho analizzato
   i loro algoritmi**. Sono ~630 KB di logica di pianificazione — il diretto corrispettivo di
   `Air_Resources_Assigner` + `Air_Route_Manager` di Warfare-Model, e probabilmente il
   materiale più utile che resta da analizzare.

### 3.4 Tre domande di progetto, e le mie risposte

Test di comprensione applicata.

**D1 — Warfare-Model deve leggere lo stato di una campagna DCE esistente. Qual è la strada
più corta?**

`lupa` è già in `requirements.txt` e `Persistence/Source/DCS_Data_Management.py` ha già
`convert_lua_to_python_module(lua_file_path, output_module_path, table_name)`. I file di stato
DCE (`Active/*.lua`) sono **sorgente Lua che dichiara una singola tabella globale**: si
eseguono in un `LuaRuntime` e si legge la globale. Nessun parser da scrivere. Per il `.miz`:
`zipfile` per estrarre, poi lo stesso trattamento su `mission`/`warehouses`/`dictionary`.
Attenzione all'encoding (i file DCE contengono caratteri accentati mal codificati —
`DCS_Data_Management` ha già una `normalize_text`) e al fatto che le tabelle Lua indicizzate
da 1 diventano dict Python, non liste.

**D2 — Se Warfare-Model dovesse generare i `.miz`, qual è il lavoro minimo?**

Tre cose, in ordine di costo crescente:
1. leggere/scrivere lo zip e serializzare tabelle Python in sorgente Lua nel formato che DCS
   accetta (`TableSerialization` di DCE è il riferimento; attenzione a virgole finali e al
   fatto che la parentesi di chiusura di livello 0 **non** vuole la virgola);
2. mantenere la coerenza di `dictionary`/`mapResource` — ogni nome e testo è una `DictKey_*`,
   e `maxDictId`/`currentKey` vanno aggiornati;
3. rispettare gli invarianti non documentati: `mission.version ≥ 19`, `currentKey = 999999`
   per gli slot multiplayer, la tripla sincronizzazione `mapResource`/`trig`/`trigrules` per
   ogni script iniettato.

Esiste `pydcs` che fa già tutto questo in Python. **Prima di scrivere codice, valuterei se
usarla** — è il consiglio che darei.

**D3 — Che cosa di DCE ha più valore per Warfare-Model?**

In ordine:
1. **`DC_Weather.lua`** — il modello sinottico a 5 zone con durate e transizioni sostituisce
   direttamente il placeholder `Logic/Meteo_Analysis.py`, che è dichiaratamente in attesa di
   un modello vero. Pronto all'uso, contratto dati compatibile.
2. **`DC_Tactical.commander()` + `airDirective()`** — è un "indirizzo strategico" funzionante:
   vocabolario chiuso di tattiche nominali su 3 intensità, ciascuna espansa in una
   combinazione fissa di cinque leve, pilotato da metriche differenziali e con audit trail
   (`report_commander`). Corrisponde a ciò che serve al design C2 a due livelli, e
   `Logic/Strategical_Evaluation.py` è ancora uno stub.
3. **`camp_triggers`** — separazione fra motore di eventi e narrativa di campagna.
   Warfare-Model non ha un equivalente.
4. **`EventsTracker.lua`** — non come codice da copiare, ma come **elenco esatto dei problemi
   da risolvere** se si vorrà ingerire risultati da DCS: de-sanitizzazione, scenery a due
   fasi, campionamento salute navi, identità delle unità, innesco del processo esterno.

---

## Riferimenti incrociati

- `ANALISI_DCE.md` — analisi completa del codice DCE, con Appendice A (riferimento
  piattaforma DCS: enum eventi, ambienti Lua, struttura `.miz`, preset meteo, identità).
- `dcs_lua/*.md` — documentazione ED locale (snapshot datato).
- `Analysis/DCE Files/` — copia di lavoro già estratta dei file di stato DCE.
