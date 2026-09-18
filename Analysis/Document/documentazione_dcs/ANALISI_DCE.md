# Analisi del Dynamic Campaign Engine (DCE) — MBot / ScriptsMod.NG

Analisi del codice in `Analysis/Document/documentazione_dcs/1975 Georgian War/DCE`,
versione ScriptsMod **20.47.105** (package `NG`).

Obiettivo primario: capire **come DCS salva risultati e stato delle missioni svolte**.
Obiettivo secondario: estrarre soluzioni riusabili per Warfare-Model.

---

## 1. Architettura d'insieme

Il fatto architetturale più importante è che **DCE non gira dentro DCS**. Gira in un
interprete Lua standalone (`luae.exe`, distribuito con DCS) lanciato da file `.bat`.
Dentro DCS gira solo un piccolo script di missione (`EventsTracker.lua`) il cui unico
compito è **registrare eventi e scrivere tre file su disco a fine missione**.

```
                 ┌─────────────────────────── DCS World ──────────────────────────┐
                 │                                                                │
 .miz generato ──┼─▶ missione giocata                                             │
                 │      │                                                         │
                 │      │  EventsTracker.lua  (world.addEventHandler)             │
                 │      │  attaccato via trigger a_do_script_file                 │
                 │      ▼                                                         │
                 │   S_EVENT_MISSION_END ──▶ scrive 3 file + os.execute(luae.exe)  │
                 └────────────────────────────────┬───────────────────────────────┘
                                                  │
     MissionEventsLog.lua / scen_destroyed.lua / camp_status.lua
                                                  │
                 ┌────────────────────────────────▼───────────────────────────────┐
                 │            luae.exe   (Lua standalone, fuori da DCS)            │
                 │                                                                 │
                 │  DEBRIEF_Master.lua                                             │
                 │    ├─ DEBRIEF_StatsEvaluation.lua   events → oob/clientstats     │
                 │    ├─ DC_DestroyTarget / DC_UpdateTargetlist                     │
                 │    ├─ DC_Logistic.UpdateOobAir()    supply → efficiency          │
                 │    ├─ DEBRIEF_Text.lua              → Debriefing N.txt           │
                 │    └─ MAIN_NextMission.lua                                       │
                 │         ├─ unzip base_mission.miz (minizip)                      │
                 │         ├─ DC_Time / DC_Weather / DC_Tactical / ATO_*            │
                 │         └─ zip → <campagna>_ongoing.miz  + salva stato Active/   │
                 └─────────────────────────────────────────────────────────────────┘
```

### 1.1 Punti d'ingresso

| File | Ruolo |
|---|---|
| `Init/path.bat` | **unico file da editare**: `pathDCS`, `pathSavedGames`, `versionPackageICM` |
| `FirstMission.bat` | `luae.exe ScriptsMod.NG/BAT_FirstMission.lua` — reset + prima missione |
| `SkipMission.bat` | `luae.exe ScriptsMod.NG/BAT_SkipMission.lua` — salta una missione |
| `DEBUG_DebriefMission.bat` | rilancia a mano il debrief (normalmente invocato da DCS) |
| `entry.lua` | manifest del mod DCS (`declare_plugin`) — solo registrazione |

I `*Testing.bat` puntano a un `luae.exe` locale invece che a quello di DCS: servono a
eseguire la pipeline senza DCS installato. La costante `ACTIVATE_TESTING_ENVIROMENTS`
in `Init/conf_mod.lua` commuta il caricamento sui file `*.2t.lua` (fixture di test).

### 1.2 Catena di caricamento

Non esiste un module system: tutto è `dofile()`/`require()` su **variabili globali**.
`camp`, `oob_air`, `oob_ground`, `targetlist`, `mission`, `warehouses`, `dictionary`
sono globali condivise fra tutti i moduli. Ogni file è uno *script*, non un modulo.

`MAIN_NextMission.lua` è la sequenza canonica (righe 387-411):

```
DC_Refpoints → DC_MissionScore → DC_Time → DC_Weather → DC_DestroyTarget
→ DC_NavalEnvironment → DC_UpdateTargetlist → DC_CheckTriggers → DC_UpdateTargetlist
→ DC_UpdateOOBGround → DC_Tactical
→ ATO_ThreatEvaluation → ATO_RouteGenerator → ATO_Generator → ATO_PlayerAssign
→ ATO_Timing → ATO_FlightPlan
→ DC_StaticAircraft → DC_Prune → DC_Briefing → DC_EndCampaign
```

L'ordine è significativo: `DC_UpdateTargetlist` è invocato **due volte**, prima e dopo
`DC_CheckTriggers`, perché i trigger di campagna possono attivare/disattivare target.

---

## 2. Come DCS salva risultati e stato delle missioni (obiettivo primario)

### 2.1 Risultato chiave: DCE **non** usa il `debrief.log` di DCS

I commenti d'intestazione lo dicono ancora (`DEBRIEF_Master.lua:1`, "To evaluate the DCS
debrief.log"), ma è **documentazione stale**: nella versione NG non esiste alcun codice che
legga `debrief.log`. Verificato con grep su tutto `ScriptsMod.NG`: le uniche occorrenze
della stringa sono nei commenti. DCE si è costruito **il proprio meccanismo di export**.

La motivazione è esplicitata a `EventsTracker.lua:269`:

> `--export data for destroyed static objects (this is not tracked in DCS's debrief.log)`

Il `debrief.log` di DCS non copre gli oggetti di scenario distrutti (ponti, edifici), che
sono target primari in una campagna d'interdizione. Da qui la scelta di intercettare
direttamente gli eventi del Simulator Scripting Engine.

### 2.2 Il meccanismo di cattura: `Mission Scripts/EventsTracker.lua`

Questo è **il file centrale per l'obiettivo primario**. 470 righe, iniettato nel `.miz`
come `l10n/DEFAULT/EventsTracker.lua` ed eseguito da un trigger `triggerStart` con azione
`a_do_script_file`.

**Prerequisito obbligatorio — de-sanitizzazione.** Lo script serve `io` e `os`, che DCS
blocca di default. Righe 26-34, un controllo elegante:

```lua
local function WarningText() ... trigger.action.outText(text, 600) end
local ErrorMessage = timer.scheduleFunction(WarningText, {}, timer.getTime() + 1)
local check = os.time()            -- se os è sanitizzato, qui lo script muore
timer.removeFunction(ErrorMessage) -- se arriviamo qui, os funziona: annulla il warning
```

Si pianifica un messaggio d'errore a T+1s, poi si chiama `os.time()`. Se `os` è
sanitizzato lo script si interrompe e il messaggio viene mostrato al giocatore; se
funziona, il messaggio viene rimosso prima di comparire. Richiede di commentare le
`sanitizeModule('os')` / `('io')` / `('lfs')` in `Scripts/MissionScripting.lua`, cosa che
**ogni aggiornamento di DCS ripristina** (il testo del warning lo dice esplicitamente).

**L'event handler.** Un singolo `world.addEventHandler(EventHandler)` con un
`onEvent(event)` che mappa `event.id` su una stringa:

| `world.event.*` | `log_entry.type` |
|---|---|
| `S_EVENT_SHOT` | `shot` |
| `S_EVENT_HIT` | `hit` |
| `S_EVENT_TAKEOFF` | `takeoff` |
| `S_EVENT_LAND` | `land` |
| `S_EVENT_CRASH` | `crash` |
| `S_EVENT_EJECTION` | `eject` |
| `S_EVENT_REFUELING` / `S_EVENT_REFUELING_STOP` | `refueling` / `refueling stop` |
| `S_EVENT_DEAD` | `dead` |
| `S_EVENT_PILOT_DEAD` | `pilot dead` |
| `S_EVENT_BASE_CAPTURED` | `base captured` |
| `S_EVENT_MISSION_START` / `S_EVENT_MISSION_END` | `mission start` / `mission end` |
| `S_EVENT_TOOK_CONTROL` | `took control` |
| `S_EVENT_BIRTH` | `birth` |
| `S_EVENT_HUMAN_FAILURE` | `human failure` |
| `S_EVENT_ENGINE_STARTUP` / `S_EVENT_ENGINE_SHUTDOWN` | `engine startup` / `engine shutdown` |
| `S_EVENT_PLAYER_ENTER_UNIT` / `S_EVENT_PLAYER_LEAVE_UNIT` | `player enter unit` / `player leave unit` |

Gli eventi non mappati (`S_EVENT_KILL`, `S_EVENT_SHOOTING_START/END`, ecc.) vengono
scartati: `log_entry.type` resta `nil` e il filtro di riga 160 li esclude.

**Filtro anti-rumore** (riga 160):

```lua
if log_entry.type and ((log_entry.type == "hit" and event.initiator) or log_entry.type ~= "hit") then
```

Gli `hit` senza `initiator` (collisioni, impatti col terreno) sono scartati: altrimenti
inquinerebbero la catena di attribuzione dei kill.

**Campi estratti per ogni evento:**

| Campo | Origine | Condizione |
|---|---|---|
| `t` | `timer.getTime()` | sempre |
| `type` | mappatura sopra | sempre |
| `initiator` | `event.initiator:getName()` | se `getDesc().displayName` esiste |
| `initiatorPilotName` | `event.initiator:getPlayerName()` | solo se `Object.Category.UNIT` ed è un player |
| `initiatorMissionID` | `event.initiator:getID()` | se non è `Object.Category.SCENERY` |
| `target` | `event.target:getName()` | idem initiator |
| `targetPilotName` | `event.target:getPlayerName()` | se target è UNIT |
| `targetMissionID` | `event.target:getID()` | se target non è SCENERY né WEAPON |
| `health` | `ceil(100 / getLife0() * getLife())` | **solo** su `hit` e solo se il target è aereo/elicottero (`getGroup():getCategory()` 0 o 1) |

Nota: **`weapon` non viene mai registrato**, pur essendo disponibile in `event.weapon`.
Confermato sull'evidenza: nei log campione non compare nessuna chiave `weapon`. Il tipo
d'arma non entra quindi nel modello di campagna.

**Oggetti di scenario — tracciamento a due fasi** (righe 288-311). Lo scenery non ha
`getID()` stabile né compare utilmente negli eventi `dead`, quindi:

1. su `S_EVENT_HIT` con `target:getCategory() == 5` e `getDesc().life > 20`, si registra
   `scenLog[name] = { health0 = descr.life, lasthit = initiator:getName() }`;
2. su `S_EVENT_DEAD` con `initiator:getCategory() == 5`, si **arricchisce** la stessa voce
   con `x`, `y`, `z` da `getPoint()`.

La soglia `life > 20` esclude oggetti irrilevanti (cespugli, recinzioni). Solo le voci che
arrivano ad avere `x`/`z` sono considerate effettivamente distrutte a valle.

**Salute delle navi — campionamento a inizio/fine missione** (righe 199-230, 316-334).
Le navi non producono eventi `dead` affidabili quando sono solo danneggiate, quindi DCE
itera `env.mission.coalition[*].country[*].ship.group[*].units[*]`, risolve ogni unità con
`Unit.getByName()` e legge `getLife()`:

- a **inizio missione** → `camp.ShipHealth0[unit.name]` (salute massima);
- a **fine missione** → `camp.ShipHealth[unit.name]` come percentuale, e
  `camp.ShipDamagedLast[unit.name] = true` se la salute è calata di oltre 5 punti.

Il danno è poi **riapplicato alla missione successiva** (righe 336-356) con un loop di
`trigger.action.explosion(point, power)` sulla nave finché `getLife()` non scende al
livello memorizzato — con `power = health0/100` e un contatore di sicurezza a 100
iterazioni. È un workaround: DCS non permette di istanziare una nave già danneggiata.

**Export a `S_EVENT_MISSION_END`** (righe 263-285). Tre file, serializzati con una
`TableSerialization` locale (duplicata nello script perché l'ambiente di missione non può
fare `dofile` su `UTIL_Functions.lua`):

| File | Contenuto | Variabile globale |
|---|---|---|
| `MissionEventsLog.lua` | array di eventi | `events` |
| `scen_destroyed.lua` | scenery distrutto | `scen_log` |
| `camp_status.lua` | stato campagna aggiornato (ShipHealth, ecc.) | `camp` |

Il path di destinazione è ricostruito da `camp.path` (salvato in `camp_status` alla
generazione, letto da `os.getenv('pathSavedGames')`), con gestione esplicita del caso
"Saved Games su un disco diverso da C:".

**Auto-innesco del debrief** (riga 285). L'ultima istruzione è:

```lua
os.execute('start "Debriefing" cmd /k "set "DCSDIR=%cd%" & '..pathDD..' & cd '..path..
           ' & call "%DCSDIR%\bin\luae.exe" ..\..\..\ScriptsMod.'..camp.versionPackageICM..'\DEBRIEF_Master.lua"')
```

DCS lancia una console che esegue il motore di campagna. È **fortemente Windows-specific**
e passa per la shell — è il punto più fragile dell'intera architettura.

### 2.3 Formato di `MissionEventsLog.lua`

Tabella Lua piatta, indicizzata da 1, ordinata cronologicamente:

```lua
events = {
    [1] = {
        ['initiatorMissionID'] = '100168',
        ['t'] = 1,
        ['type'] = 'birth',
        ['initiator'] = 'Pack 1 - 790.IAP - CAP 1-1',
    },
    [215] = {
        ['type'] = 'hit',
        ['health'] = 95,
        ['initiator'] = 'Maykop SA-2-2',
        ['target'] = 'Pack 1 - VF-101 - Intercept 1-1',
        ['t'] = 694.46,
        ['targetMissionID'] = '100036',
        ['initiatorMissionID'] = '1142',
    },
    [219] = { ['type'] = 'mission end', ['t'] = 778.742 },
}
```

Distribuzione reale su un log completo (`Debug/MissionEventsLog.2t.lua`, 2808 eventi):

| tipo | n | tipo | n |
|---|---|---|---|
| `hit` | 1041 | `crash` | 97 |
| `shot` | 786 | `pilot dead` | 80 |
| `birth` | 284 | `dead` | 66 |
| `engine startup` | 238 | `eject` | 43 |
| `takeoff` | 140 | `land` | 23 |
| | | `engine shutdown` | 9 |
| | | `mission end` | 1 |

Osservazioni rilevanti:

- **La convenzione di naming è il vero identificatore.** I `MissionID` numerici sono
  volatili (rigenerati a ogni `.miz`); l'attribuzione si fa sui **nomi**, con il pattern
  `Pack <n> - <squadron> - <task> <flight>-<ship>`. `DEBRIEF_StatsEvaluation` risolve
  l'unità di OOB con `string.find(events[e].initiator, " "..killer_unit.name.." ", 1, true)`
  — cioè cerca il nome squadriglia *delimitato da spazi* dentro il nome dell'unità. È
  fragile: un nome squadriglia che sia sottostringa di un altro rompe l'attribuzione.
- **`t` è il tempo modello della missione**, non l'ora di campagna. La durata reale della
  missione è calcolata a posteriori: `events[#events].t - events[1].t`
  (`DEBRIEF_Master.lua:158`) e sommata a `camp.time`.
- Il `mission end` finale è garanzia implicita di completezza del file.

### 2.4 Da eventi a stato: `DEBRIEF_StatsEvaluation.lua`

Il modulo fa **due passate** sull'array `events`.

**Passata 1 — mappa unità→player** (righe 244-252). Solo per gli eventi con
`initiatorPilotName`, popola `client_control[initiator_name] = pilot_name`. Questo è ciò
che permette in seguito di attribuire a un giocatore reale ciò che fa la sua unità.

**Passata 2 — valutazione** (riga 258 in poi), con tre tabelle di lavoro:

| tabella | semantica |
|---|---|
| `hit_table[target]` | **ultimo** initiator che ha colpito `target` (le hit successive sovrascrivono) |
| `health_table[target]` | salute residua registrata sull'ultima hit |
| `client_hit_table[target]` | nome del player che ha colpito, o `nil` |

L'**attribuzione dei kill è "last hitter wins"**: quando arriva un `crash`/`dead`, si
guarda chi è l'ultimo ad aver colpito la vittima e gli si assegna il kill. Semplice,
deterministico, e sistematicamente sbagliato nei casi di fuoco combinato — ma sufficiente.

Logica per tipo di evento:

- **`hit`** → aggiorna le tre tabelle di lavoro. Nient'altro.
- **`crash`** → cerca l'unità in `oob_air` per sottostringa del nome; incrementa
  `roster.lost` e `score_last.lost`, decrementa `roster.ready` e `score_last.ready`
  (entrambi con guardia `> 0`). Poi risale a `hit_table[initiator]` per assegnare il kill
  al killer: `score.kills_air` + `score_last.kills_air`, **se e solo se i due lati
  differiscono** — altrimenti è `friendly_kills_air`. Infine `hit_table[initiator] = nil`,
  così le unità che restano in `hit_table` a fine ciclo sono per definizione *danneggiate
  ma vive*.
- **`dead`** → itera `oob_ground[side][country].vehicle|ship|static.group[].units[]` e
  confronta `unit.unitId == tonumber(events[e].initiatorMissionID)`. Al match:
  `unit.dead = true`, `unit.dead_last = true`, `unit.CheckDay = camp.day` (data di
  distruzione, usata dalla logica di riparazione). Poi stessa attribuzione kill.
- **`eject` / `pilot dead` / `takeoff`** → solo statistiche player (`clientstats`).
  `takeoff` incrementa il contatore missioni **solo al primo decollo** della missione
  (`if score_last.mission == 0`), per non contare doppio i touch-and-go.

Il pattern `score` / `score_last` (totale campagna / ultima missione) è sistematico e
viene azzerato in testa al modulo.

### 2.5 Il `debrief.log` reale — analisi empirica

**Questa sezione sostituisce una precedente basata su fonti secondarie.** Ora dispongo di un
`debrief.log` reale (427 KB, 18 680 righe, singleplayer, campagna *Fw 190 A-8 Horrido*,
**DCS 2.9.29.27468 build 559**), che ho caricato e analizzato. Quello che segue è misurato,
non riportato.

#### Formato e insidia di parsing

Il file è **sorgente Lua** con assegnazioni separate da tabulazioni (`chiave\t=\tvalore`).
Si carica come chunk Lua — **ma non in Lua 5.2 o successivi**:

```
LuaSyntaxError: unexpected symbol near 'goto'
```

Le unità di `world_state` hanno un campo letteralmente chiamato **`goto`** (25 occorrenze),
che è **parola riservata da Lua 5.2 in poi**. Il file è quindi valido solo in **Lua 5.1**.
Con lupa (Lua 5.5) serve un pre-processing che metta fra virgolette le chiavi riservate:

```python
RESERVED = {"and","break","do","else","elseif","end","false","for","function","goto",
            "if","in","local","nil","not","or","repeat","return","then","true","until","while"}
src = re.sub(r'(?m)^([ \t]*)([A-Za-z_]\w*)[ \t]*=',
             lambda m: f'{m.group(1)}["{m.group(2)}"]\t=' if m.group(2) in RESERVED else m.group(0),
             src)
```

Con questa sola modifica il file si carica interamente. Da notare anche la codifica: **cp1252**,
non UTF-8.

#### Le dieci chiavi di primo livello

| Chiave | Tipo | Contenuto misurato |
|---|---|---|
| `mission_file_path` | str | `"./Mods/campaigns/Fw 190 A-8 Horrido/Horrido - 10.miz"` |
| `callsign` | str | callsign del giocatore |
| `mission_file_mark` | int | timestamp Unix del `.miz` |
| `mission_time` | float | durata missione in secondi (`1330.72`) |
| `result` | int | **punteggio missione 0–100** (`100`) |
| `graveyard` | array | relitti: `{type, coalition, country, x, y, alt, heading}` — 9 voci |
| `world_state` | array | **stato finale di ogni unità** — 115 voci |
| `warehouses` | table | `{airports[id], warehouses[id]}` — stato finale magazzini |
| `triggers_state` | map | flag utente → `{time, value}` — valore finale e istante in cui è stato posto |
| `events` | array | 932 eventi |

#### `world_state` — il pezzo che cambia tutto

DCS restituisce **lo stato finale di ogni unità della missione**, non solo chi è morto:

| Campo | Sempre presente | Note |
|---|---|---|
| `unitId`, `type`, `country`, `coalition` | sì | `unitId` è il mission ID, ricollegabile al `.miz` |
| `x`, `y`, `alt`, `heading` | sì | posizione finale |
| `dead`, `hidden` | sì | 12 morte su 115 nel campione |
| `life` | quasi sempre | **punti vita residui** (es. `18`) |
| `speed`, `groupId`, `N_obj` | spesso | |
| `inAir` | solo aerei | |
| `goto` | solo aerei | indice del waypoint corrente |
| `payload` | solo aerei | `{gun, fuel, chaff, flare, ammo_type, pylons}` |

Otto forme distinte, dalla più povera (statici: 10 campi) alla più ricca (aereo in volo:
17 campi). Esempio reale di un Bf-109K-4 vivo a fine missione: `life = 18`,
`payload = {gun: 100, fuel: 296, chaff: 0, flare: 0, ammo_type: 1, pylons: {...}}`,
`inAir = true`, `speed = 133.6`, `goto = 1`.

**Conseguenza per un motore di campagna**: `world_state` fornisce *già fatto* ciò che
`DEBRIEF_StatsEvaluation.lua` ricostruisce a mano percorrendo gli eventi per marcare
`unit.dead = true` in `oob_ground`. Basta un join su `unitId`. E in più dà **danno parziale
(`life`), carburante e munizioni residue** — dati che DCE non ha in nessuna forma e che
dovrebbe altrimenti stimare.

Analogamente `graveyard` fornisce i relitti con posizione e assetto — proprio ciò che
`DC_UpdateOOBGround.createStaticDeadGroup()` ricostruisce sinteticamente.

#### `events` — venti tipi, molto oltre i diciannove di DCE

Distribuzione misurata sui 932 eventi:

| tipo | n | | tipo | n |
|---|---|---|---|---|
| `shot` | 288 | | `ai abort mission` | 9 |
| `start shooting` | 206 | | `engine shutdown` | 6 |
| `end shooting` | 206 | | `eject` | 3 |
| `hit` | 93 | | `crash` | 3 |
| `bda` | 46 | | `pilot landing` | 2 |
| `failure` | 29 | | `mission start`, `took control`, `under control`, `pilot dead`, `takeoff`, `mission end` | 1 ciascuno |
| `engine startup` | 27 | | `kill` | 4 |
| | | | `score` | 4 |

Campi per evento, con frequenza:

| n | campo | n | campo |
|---|---|---|---|
| 932 | `type`, `t` | 372 | `target`, `targetMissionID` |
| 931 | `event_id`, `linked_event_id` | 371 | `target_coalition`, `target_unit_type`, `target_object_id`, `target_ws_type1`, `targetPilotName` |
| 905 | `initiatorPilotName`, `initiator_coalition`, `initiator_object_id`, `initiator_unit_type` | 206 | **`ammo_consumption`** |
| 904 | `initiatorMissionID`, `initiator_ws_type1` | 84 | `uin64_t_value` |
| 814 | **`weapon`** | 29 | `failure`, `failureDisplayName` |
| 582 | **`weapon_type`** | 6 | `place`, 5 `placeDisplayName`, 5 `comment`, 4 `amount` |

#### La catena causale: `linked_event_id`

**Il risultato più importante.** Ogni evento ha un `event_id` univoco e un `linked_event_id`
che punta all'evento che lo ha causato. Verificato su tutto il file, **17 link su 17
risolti, zero orfani**:

```
shot ──(hit.linked_event_id)──▶ hit ──(kill.linked_event_id)──▶ kill ──(score.linked_event_id)──▶ score
```

Catena reale estratta dal file:

```
t=8.92   hit    ev=109  link=0    init=Bf-109K-4/361  tgt=Bf-109K-4/359  w='Bf 109 K-4'
t=8.92   kill   ev=112  link=109  init=Bf-109K-4/361  tgt=Bf-109K-4/359  w='Bf 109 K-4'
```

**DCS fornisce l'attribuzione dei kill già fatta**, con iniziatore, bersaglio, arma e il
collegamento all'impatto che l'ha prodotta. Tutta la macchina `hit_table` /
"last hitter wins" di `DEBRIEF_StatsEvaluation.lua` (§2.4) ricostruisce — peggio — un dato
che era già disponibile. È la singola semplificazione più grande che Warfare-Model può
prendersi rispetto a DCE.

Gli eventi `score` portano `amount` (±20 nel campione) e `comment` (`'air'`): il punteggio è
negativo per le perdite proprie, positivo per gli abbattimenti.

#### Identificare il giocatore

`initiatorPilotName` **non** è un discriminante: per le unità IA contiene semplicemente il
tipo (`'Bf-109K-4'`, `'flak30'`). Il giocatore si identifica dall'evento `under control`:

```lua
{ type='under control', t=0, target='player', initiatorPilotName='New callsign',
  targetMissionID='2', initiator_unit_type='FW-190A8', initiator_object_id=16800256 }
```

`target = 'player'` e `initiatorPilotName` = il callsign vero. Da lì si ricava
`targetMissionID`, e tutti gli eventi successivi di quell'unità sono del giocatore.

⚠️ Attenzione: questo è **diverso** dall'omonimo campo che DCE costruisce con
`Unit.getPlayerName()`, che invece restituisce `nil` per l'IA. Stesso nome, semantica diversa.

#### `weapon` è inaffidabile come chiave, `weapon_type` no

Valori realmente presenti nel campo `weapon`: `'Sprgr. L/4.5 Kz.'` (307), `'Flak38_2_cm'`
(244), `'Browning .50 M2'` (156), `'50Browning_API_M8'` (28), `'Bf 109 K-4'` (22),
**`'Aw shoot.'` (14)**, `'weapons.shells.50Browning_API_M8'` (6), `''` (in un `kill`).

Convivono nomi di visualizzazione, nomi interni, percorsi completi e almeno un segnaposto
scherzoso di ED. **Usare `weapon_type`** (intero, es. `16843249`, `2566`, `9243142`), che è
stabile.

#### Altri dati utili

- **`ammo_consumption`** su `end shooting`: 206 eventi, 84 con valore non nullo, massimo 27.
  È il consumo munizioni reale per raffica — la base per un modello di logistica delle
  munizioni che DCE non può avere.
- **`failure`** (29) con `failureDisplayName`: guasti del velivolo del giocatore.
- **`place` / `placeDisplayName`** su `engine startup`, `takeoff`, `pilot landing`:
  l'aeroporto o la nave coinvolta.
- **`ai abort mission`** (9): l'IA ha rinunciato al compito — segnale di efficacia della
  difesa che DCE ignora completamente.
- `mission start` porta `ta = 68100`: ora del giorno di inizio, in secondi.
- `triggers_state`: valore finale di ogni flag utente **e l'istante in cui è stato posto**.
  Le chiavi sono nomi di flag, numerici (`"601"`) o nominali (`gogo`).

#### Perché DCE ha comunque rinunciato — e cosa ci perde

La motivazione dichiarata in `EventsTracker.lua:269` resta valida: il `debrief.log`
**non traccia gli oggetti di scenario distrutti**, e ponti ed edifici sono bersagli primari
di una campagna d'interdizione. A questo si aggiunge che in **multiplayer** il formato
degenera in righe testuali `event:type=...,t=...` non ben formate — motivo per cui progetti
come `dcs_liberation` mantengono un parser regex di fallback.

Ma il prezzo pagato è alto. Rispetto al `debrief.log`, il log custom di DCE **perde**:
`world_state` completo (stato, `life`, carburante, munizioni residue di ogni unità),
`graveyard`, `warehouses`, `triggers_state`, `result`, l'attribuzione dei kill fatta dal
simulatore, la catena causale `linked_event_id`, l'arma usata, il consumo munizioni, i
guasti, gli abbandoni di missione dell'IA.

**Per Warfare-Model la conclusione è: usare entrambi.** Il `debrief.log` per tutto quanto
sopra, e uno script di missione custom in stile `EventsTracker` **solo** per ciò che manca —
in pratica lo scenery distrutto e, se serve multiplayer, un canale strutturato che non
dipenda dal formato degenere del debrief in MP.

### 2.6 Copertura degli eventi: cosa DCE ignora

Il Simulator Scripting Engine espone **61 valori `S_EVENT_*`** (0–60, più `S_EVENT_MAX`).
`EventsTracker.lua` ne mappa **19**. Fra quelli ignorati, alcuni sarebbero utili a un motore
di campagna:

| Evento | ID | Perché interessa |
|---|---|---|
| `S_EVENT_KILL` | 28 | attribuzione kill **fornita dal simulatore**, invece che dedotta con "last hitter wins" |
| `S_EVENT_UNIT_LOST` | 30 | perdita unità distinta da `dead`/`crash` |
| `S_EVENT_BDA` | 37 | battle damage assessment |
| `S_EVENT_SHOOTING_START` / `_END` | 23/24 | consumo munizioni ad area (cannoni, AAA) |
| `S_EVENT_LANDING_QUALITY_MARK` | 36 | qualità dell'atterraggio (rilevante per portaerei) |
| `S_EVENT_RUNWAY_TAKEOFF` / `_TOUCH` | 54/55 | decollo/contatto pista distinti da `takeoff`/`land` |
| `S_EVENT_EMERGENCY_LANDING` | 43 | atterraggio d'emergenza — recuperabilità del velivolo |
| `S_EVENT_MISSION_WINNER` | 53 | esito dichiarato dal simulatore |
| `S_EVENT_WEAPON_ADD` / `_REARM` / `_DROP` | 34/47/48 | consumo e riarmo armamento |

`S_EVENT_KILL` in particolare renderebbe superflua tutta la macchina `hit_table` di
`DEBRIEF_StatsEvaluation.lua`. DCE è stato scritto su una versione di DCS in cui parte di
questi eventi non esisteva ancora: l'elenco riflette il 2020, non lo stato attuale.

### 2.7 I tre file di stato che DCS produce, in sintesi

| File | Chi lo scrive | Quando | Contiene |
|---|---|---|---|
| `MissionEventsLog.lua` | `EventsTracker.lua` in DCS | `S_EVENT_MISSION_END` | `events[]` — cronologia eventi |
| `scen_destroyed.lua` | idem | idem | `scen_log{}` — scenery distrutto con coordinate |
| `camp_status.lua` | idem | idem | `camp{}` — stato campagna + `ShipHealth`/`ShipDamagedLast` |

Sono **temporanei**: `DEBRIEF_Master.lua` li consuma e li cancella in coda
(`os.remove`, righe 673-675), con copia opzionale in `Debug/` se `local_debug`.

---

## 3. Modello dati dello stato di campagna

Tutto lo stato vive in `Missions/Campaigns/<campagna>/Active/*.lua`, file Lua che
dichiarano una singola tabella globale. Sono insieme **formato di persistenza e formato di
caricamento**: si rileggono con `dofile`/`require`, si riscrivono con
`TableSerialization`. Nessun parser, nessuno schema, nessuna migrazione.

| File | Globale | Ruolo |
|---|---|---|
| `camp_status.lua` | `camp` | stato di campagna: tempo, data, meteo, config, pacchetto player |
| `oob_air.lua` | `oob_air` | ordine di battaglia aereo per lato (squadriglie) |
| `oob_ground.lua` | `oob_ground` | ordine di battaglia terrestre/navale/statico (700 KB) |
| `oob_scen.lua` | `oob_scen` | oggetti di scenario distrutti, cumulativo |
| `targetlist.lua` | `targetlist` | target di campagna con stato e priorità |
| `camp_triggers.lua` | `camp_triggers` | eventi scriptati di campagna |
| `clientstats.lua` | `clientstats` | statistiche per giocatore umano |
| `airbase_tab.lua` | `airbase_tab` | efficienza/integrità/supply per base |
| `supply_tab.lua` | `supply_tab` | grafo delle linee di rifornimento |
| `statistic_data.lua` | `statistic_data` | perdite aggregate per categoria e costo |
| `report_commander.lua` | `report_commander` | storico delle direttive del comandante AI |

I corrispondenti `Init/*_init.lua` sono i valori iniziali, copiati in `Active/` da
`UTIL_ResetCampaign.lua` alla prima missione.

### 3.1 `camp` — lo stato di campagna

```lua
camp = {
  ['title'] = '1975 Georgian War',   ['version'] = 'V0.1',
  ['mission'] = 1,                   -- contatore missioni
  ['day'] = 2,                       -- giorno di campagna (1-based)
  ['time'] = 21376,                  -- ora del giorno in secondi
  ['date'] = { ['day']=14, ['month']=9, ['year']=1975 },
  ['mission_duration'] = 5400,
  ['idle_time_min'] = 10800, ['idle_time_max'] = 14400,  -- salto temporale fra missioni
  ['dawn'] = 21600, ['dusk'] = 65700,
  ['weather'] = { zone, zoneNext, zoneStart, zoneEnd, zoneTemp, zoneNextTemp, refTemp, pHigh, pLow },
  ['player'] = { ['pack_n']=N, ['pack']={ [role][flight] = {...route, eta, livery...} } },
  ['ShipHealth'] = {...}, ['ShipHealth0'] = {...}, ['ShipDamagedLast'] = {...},
  ['aircraft_availability'] = {...},
  ['module_config'] = { ['ATO_Generator'] = {...}, ... },   -- config runtime per-lato
  ['SCORE_TASK_FACTOR'] = { CAP=1, Strike={armor=1, soft=1, SAM=1, ...}, ... },
  ['flag'] = {},                     -- flag di campagna per i trigger
  ['path'] = 'C:/Users/.../Saved Games/DCS.openbeta_server/',
  ['MissionFilename'] = '1975 Georgian War_ongoing.miz',
}
```

`camp` è **l'unica struttura che attraversa il confine DCS/esterno in entrambe le
direzioni**: viene scritta nel `.miz` (`l10n/DEFAULT/camp_status.lua`), letta e mutata
dallo script di missione, riesportata a fine missione e riletta dal debrief. È il canale
di comunicazione fra i due ambienti.

### 3.2 `oob_air` — squadriglie

```lua
oob_air = {
  ['blue'] = {
    [2] = {
      ['name'] = 'GAH 2rd', ['type'] = 'Mi-24V', ['country'] = 'Georgia',
      ['base'] = 'AMBROLAURI FARP LN41', ['number'] = 8, ['skill'] = 'High',
      ['helicopter'] = true, ['livery'] = '',
      ['tasks'] = { ['Strike'] = true, ['Transport'] = true },  -- set di task ammessi
      ['roster'] = { ['ready'] = 16, ['damaged'] = 0, ['lost'] = 0 },
      ['score'] = { ['kills_air']=0, ['kills_ground']=0, ['kills_ship']=0 },
      ['score_last'] = { ..., ['lost']=0, ['damaged']=0, ['ready']=0 },
    },
    [1] = { ['name'] = 'R/GAH 2rd', ['base'] = 'Reserves', ['inactive'] = true, ... },
  },
  ['red'] = { ... },
}
```

Note: `number` è l'organico nominale, `roster.ready` gli aerei effettivamente disponibili
(può eccedere `number` — è un pool, non un vincolo). Le unità con prefisso `R/` e
`base = 'Reserves'` sono riserve attivabili via trigger `Action.AirUnitReinforce`.

### 3.3 `targetlist` — target di campagna

```lua
targetlist = {
  ['blue'] = {
    ['209 SA-2 Site R-3'] = {
      ['name'] = '209 SA-2 Site R-3', ['class'] = 'vehicle', ['groupId'] = 424,
      ['task'] = 'Strike', ['attributes'] = { [1] = 'SAM' },
      ['priority'] = 6, ['ATO'] = true,
      ['firepower'] = { ['min'] = 3, ['max'] = 6 },
      ['x'] = -83928.37, ['y'] = 845506.11,
      ['alive'] = 100,       -- % elementi vivi
      ['dead_last'] = 0,     -- % elementi distrutti nell'ultima missione
      ['foundOobGround'] = true,
      ['elements'] = { [1] = { ['name']='...-1', ['dead_last']=false }, ... },
      ['picture'] = { [1] = 'Vladikavkaz_Bridge.png' },
    },
  },
}
```

`alive` e `dead_last` sono ricalcolati da `DC_UpdateTargetlist.lua` per differenza sugli
`elements`: `target.alive -= 100 / #elements` per ogni elemento morto. `ATO = false`
rimuove il target dalla pianificazione. Sotto `campMod.KillTargetValue` il target viene
forzato a 0 (`KillTarget()`): un bersaglio quasi distrutto non merita altre sortite.

`GroundTarget[side].percent` — percentuale di target ancora vivi per lato — è la metrica
aggregata usata dai trigger di fine campagna.

### 3.4 `oob_ground` — specchio della missione

`oob_ground` replica **esattamente** la gerarchia del file `mission` del `.miz`
(`coalition[side].country[n].<categoria>.group[].units[]`, con `route.points`,
`groupId`, `unitId`, `heading`, `x`/`y`), aggiungendo tre campi di campagna:
`dead`, `dead_last`, `CheckDay`.

⚠️ **Il nome inganna: non contiene solo forze terrestri.** Caricando il file si trovano le
categorie `vehicle`, `ship`, `static` **e `helicopter`** (gli SH-60B "Pedro" di soccorso
basati sulle portaerei), con la struttura DCS completa: `route.points[].task`,
`units[].payload.pylons`, `callsign`, `livery_id`, `onboard_num`, `psi`, `ropeLength`.
È a tutti gli effetti **lo specchio dell'albero `coalition → country → categoria` del file
`mission`**, non un OOB terrestre. Composizione reale della campagna analizzata:

| lato | vehicle | ship | static | helicopter |
|---|---|---|---|---|
| blue | 247 (7 dead) | 31 | 109 (3 dead) | 3 |
| red | 314 (11 dead) | 28 (3 dead) | 165 (20 dead) | — |

`CheckDay` risulta valorizzato su **tutte** le unità `dead` e solo su quelle (7/7, 11/11,
20/20, 3/3): è affidabile come data di distruzione.

`DC_UpdateOOBGround.lua` fa la trasformazione inversa prima di riscrivere il `.miz`: per
ogni unità `dead`, crea un **gruppo statico "Dead Static"** alla stessa posizione (stesso
`type`, `heading`, `hidden = true`) e rimuove l'unità viva dal gruppo. Il relitto resta
visibile senza essere un bersaglio. Se il gruppo resta senza unità viene rimosso; altrimenti
il punto di rotta del gruppo viene riancorato alla prima unità superstite.

### 3.5 `supply_tab` / `airbase_tab` — la logistica

`DC_Logistic.lua` è un grafo a tre livelli con propagazione moltiplicativa:

```
supply plant (integrity)  →  supply line (integrity)  →  airbase (supply)
                                                          ↓
                                    airbase integrity (danno diretto alla base)
                                                          ↓
                                    airbase efficiency = f(supply, integrity)
                                                          ↓
                                    oob_air[].roster.ready  (rigenerazione velivoli)
```

Funzioni in ordine di chiamata dentro `UpdateOobAir()`:
`UpdateSupplyPlantIntegrity` → `UpdateSupplyLineIntegrity` → `UpdateAirbaseSupply` →
`UpdateAirbaseIntegrity` → `UpdateAirbaseEfficiency`.

Nel debriefing l'efficienza compare per unità con notazione a cancelletti
(`89 ##`, `75 ###`, `32 #######`): un cancelletto ogni ~5 punti persi.

---

### 3.6 Schema verificato caricando i file con `lupa`

Le sezioni precedenti descrivono la forma dei file per campionamento. Per chiudere la
questione ho **caricato tutti e 14 i file di `Active/` in un `LuaRuntime` (lupa 2.8)** e
camminato le tabelle. Tutti e 14 si caricano senza errori. Di seguito ciò che il
campionamento aveva mancato o reso impreciso.

**Nota di codifica**: i file contengono accenti in **cp1252**, non UTF-8. Vanno letti in
binario e decodificati con fallback, altrimenti il caricamento fallisce.

#### Campi non documentati sopra

`oob_air[side][i]` — oltre a quanto già descritto:

| Campo | Tipo | Significato |
|---|---|---|
| **`tasksCoef`** | map task → float | **coefficiente di resa della squadriglia per task** (es. `Strike = 1.5`, `SEAD = 2`, `Laser Illumination = 1`). Ortogonale a `tasks` (che è solo booleano di ammissibilità) |
| `player` | bool | marca la squadriglia del giocatore (una sola in tutta la campagna) |
| `liveryModex` | array str | varianti di livrea |
| `sidenumber` | array int | numeri di fusoliera |
| `livery` | **`str` \| `table`** | **polimorfico**: stringa singola oppure array di stringhe |

`targetlist[side][nome]` — oltre a quanto già descritto: `radius` (int, per bersagli d'area
come le zone CAP), `refpoint` (str, riferimento a un refpoint nominato), `slaved`
(array misto `int|str`, aggancio a un'unità mobile: nome + bearing + distanza), `unit`
(`{name, number, type}` — il bersaglio *è* una squadriglia aerea, per gli allarmi/intercetti),
`text` (descrizione testuale della posizione), `inactive` (bool).

#### Tre trappole di tipo per un layer di persistenza Python

1. **`nil` significa "assente", non `false`.** In `targetlist`, `dead` **non compare** quando
   l'elemento è vivo — non vale `false`. Gli `elements[i]` hanno esattamente **6 forme**:

   | n | chiavi |
   |---|---|
   | 408 | `dead_last, name, x, y` |
   | 339 | `dead_last, name` |
   | 214 | `dead_last, foundOobGround, groupId, name` |
   | 21 | `CheckDay, dead, dead_last, name, x, y` |
   | 20 | `dead, dead_last, foundOobGround, groupId, name` |
   | 9 | `CheckDay, dead, dead_last, name` |

   Un mapping a dataclass deve trattare le chiavi mancanti come default, non come errore.

2. **Campi polimorfici**: `oob_air[].livery` è `str|table`; `targetlist[].x`/`.y` sono
   `float|int`; `targetlist[].slaved[i]` è `int|str`;
   `statistic_data.global_losses.*.last_mission.{k}` mescola `'blue'`/`'tie'` con numeri.

3. **`class` è opzionale**: presente solo su 71 target su 170. Distribuzione reale
   `class × task`:

   | n | class | task |
   |---|---|---|
   | 66 | *(assente)* | Strike |
   | 42 | `vehicle` | Strike |
   | 14 | `static` | Strike |
   | 11 | *(assente)* | Intercept |
   | 9 | `airbase` | Strike |
   | 9 | *(assente)* | CAP |
   | 6 | `ship` | Anti-ship Strike |
   | 4 | *(assente)* | Fighter Sweep / Refueling |
   | 3 | *(assente)* | AWACS |
   | 2 | *(assente)* | Transport |

   `class` esiste solo per i target risolti in `oob_ground`; i bersagli "virtuali"
   (zone CAP, tracce tanker, allarmi) ne sono privi.

#### `attributes` non è un enum

Vocabolario realmente presente nei dati, con frequenza:

`Bridge` 43 · `soft` 28 · `Structure` 28 · `SAM` 23 · `Parked Aircraft` 9 · `ship` 6 ·
`Air Forces` 2 · `AEW` 1 · `CV CAP` 1 · `medium` 1 · `low` 1 · `KC135` 1 · `KC135MPRS` 1 ·
`Sentry` 1

È un **sacchetto di tag eterogenei**: categorie di bersaglio (`Bridge`, `SAM`), durezza
(`soft`), livelli (`medium`, `low`), ruoli (`AEW`, `CV CAP`) e perfino tipi di velivolo
(`KC135`, `Sentry`) convivono nello stesso campo. Inoltre `armor` e `hard`, che
`DC_Tactical.changePriorityTask()` e `camp.SCORE_TASK_FACTOR` sanno trattare, **non
compaiono affatto** in questa campagna: il vocabolario del codice è più ampio di quello dei
dati. Per Warfare-Model: non modellarlo come enum chiuso.

#### Formula logistica verificata

Sui dati reali vale esattamente, su **73 basi su 73**:

```
efficiency = supply × integrity
```

Esempio: base rossa con `supply = 0.44`, `integrity = 0.72` → `efficiency = 0.32`.
I tre valori sono float in [0, 1]; nella campagna analizzata la stragrande maggioranza è a
1.0, con poche basi degradate.

#### Il DSL dei trigger è usato solo in minima parte

`Active/camp_triggers.lua` contiene **105 trigger** e **92 azioni**. Ma delle ~20
`Action.*` e ~13 `Return.*` documentate nell'intestazione di `camp_triggers_init.lua`, la
campagna ne usa rispettivamente **4** e **5**:

| `Action.*` usate | n | | `Return.*` usate | n |
|---|---|---|---|---|
| `Text` | 36 | | `TargetAlive` | 35 |
| `AddImage` | 16 | | `AirUnitReady` | 19 |
| `TargetActive` | 9 | | `Mission` | 6 |
| `CampaignEnd` | 8 | | `AirUnitAlive` | 5 |
| | | | `UnitDead` | 2 |

Sei condizioni accedono inoltre a `GroundTarget[...]` **come globale nuda**, scavalcando il
namespace `Return.*`. La lista nell'intestazione è quindi l'**API disponibile**, non quella
in uso: utile come catalogo di capacità, non come indicazione di ciò che serve davvero.

Sui 105 trigger: 68 non hanno `once` (quindi ripetibili), 37 sì; 8 sono `active = false`.

#### I due file non descritti sopra

`oob_scen.lua` — chiavi = **ID numerici** degli oggetti di scenario (non nomi), valori
`{x, y, z, lasthit, health0}`. È l'accumulo cumulativo di `scen_log` attraverso le missioni.
16 oggetti nella campagna analizzata.

`target_priority_default.lua` — `{side: {nome_target: int}}`, priorità di riferimento
(80 target blue, 95 red). È la **baseline** che `DC_Tactical.resetPriorityTask()` ripristina
al reset ciclico, e rispetto alla quale `changePriorityTask()` applica gli scostamenti.

`computed_target_efficiency.lua` — cache: chiave stringa composita
(`'<firepower><side><mix><attr><task><bool><livello>'`, es. `'8bluemixSAMStriketruemed'`) →
intero. Memoizza il costo/efficacia calcolato per una combinazione di parametri.

---

## 4. Formato `.miz`

Un `.miz` è uno **zip senza estensione**. Contenuto di `Init/base_mission.miz` (template
pulito prodotto dal Mission Editor):

| Entry | Globale dichiarata | Contenuto |
|---|---|---|
| `mission` | `mission` | tutta la missione (1.9 MB) |
| `options` | `options` | opzioni di difficoltà/visualizzazione |
| `warehouses` | `warehouses` | magazzini di aeroporti e basi |
| `l10n/DEFAULT/dictionary` | `dictionary` | tutte le stringhe, indicizzate `DictKey_*` |
| `l10n/DEFAULT/mapResource` | `mapResource` | mappa `ResKey_*` → nome file |
| `theatre` | *(testo semplice)* | `Caucasus` |

Ogni entry (tranne `theatre`) è **sorgente Lua eseguibile** che assegna una globale. Si
legge con `loadstring(contenuto)()`, si riscrive con `TableSerialization`.

Il `.miz` generato da DCE aggiunge sotto `l10n/DEFAULT/`: `EventsTracker.lua`,
`GCIdata.lua`, `GCIscript.lua`, `ARM_Defence_Script.lua`, `CustomTasksScript.lua`,
`CarrierIntoWindScript.lua`, `AddCommandRadioF10.lua`, `Pedro.lua`, `camp_status.lua`,
i `.png` di briefing e `alarme.wav`.

### 4.1 Chiavi principali di `mission`

`requiredModules`, `date` (`Day`/`Month`/`Year`), `start_time`, `theatre`, `weather`,
`coalition` (→ `blue`/`red`/`neutrals` → `country[]` → `plane`/`helicopter`/`vehicle`/
`ship`/`static` → `group[]` → `units[]`), `coalitions` (mappa lato → lista di country id),
`triggers.zones[]`, `trig` (`flag`/`conditions`/`actions`/`funcStartup`), `trigrules[]`,
`goals[]`, `result` (`offline`/`blue`/`red`), `failures`, `forcedOptions`, `map`,
`groundControl`, `drawings`, `maxDictId`, `currentKey`, `version`, `sortie`,
`descriptionText` / `descriptionBlueTask` / `descriptionRedTask` (tutti `DictKey_*`).

`mission.version` è un numero di schema: `MAIN_NextMission.lua:80` avverte se `< 19`
(pre-DCS 2.7.0). Valori misurati direttamente sui file a disposizione:

| File | `version` |
|---|---|
| `Init/base_mission.miz` (template DCE) | **22** |
| `Analysis/DCE Files/Warfare_Model_Test_Mission.miz` (giugno 2026) | **23** |

⚠️ **`pydcs` scrive `version = 20`** (bump fermo all'ottobre 2021). Le feature successive —
halo 2.8.0, scripting warehouse 2.8.8, nuova nebbia 2.9.10, Mission State Save 2.9.14 — sono
state introdotte come **campi additivi retrocompatibili**, senza bump formale di schema. Se
si usa `pydcs` per generare `.miz`, va verificato che DCS accetti senza problemi un file
dichiarato `version = 20` mentre l'editor corrente ne scrive 23.

### 4.2 Come DCE inietta script nel `.miz`

Pattern elegante (`MAIN_NextMission.lua`, `AddFileTrigger`), riusabile:

```lua
mapResource["ResKey_Action_" .. n]  = "EventsTracker.lua"
mission.trig.flag[n]               = true
mission.trig.conditions[n]         = "return(true)"
mission.trig.actions[n]            = 'a_do_script_file(getValueResourceByKey("ResKey_Action_'..n..'"));'
mission.trig.funcStartup[n]        = 'if mission.trig.conditions['..n..']() then mission.trig.actions['..n..']() end'
mission.trigrules[n]               = { predicate='triggerStart', actions={{ file='ResKey_Action_'..n,
                                       predicate='a_do_script_file', ai_task={'',''} }}, rules={}, eventlist='' }
```

Il file va poi aggiunto allo zip in `l10n/DEFAULT/<nome>`. **Le tre strutture vanno tenute
sincronizzate**: `mapResource` (risoluzione nome), `mission.trig` (esecuzione runtime),
`mission.trigrules` (rappresentazione per il Mission Editor).

Nota tecnica curiosa: `mission.currentKey = 999999` (riga 415) — commentato
`"not clear how this works but is required for multiplayer clients to be available"`.

### 4.3 Distruzione di scenario nel `.miz`

Gli oggetti di scenario distrutti nelle missioni precedenti vengono **ri-distrutti**
all'avvio: per ogni voce di `oob_scen` con coordinate si crea una trigger zone di raggio 1
(`hidden = true`) e si concatena `a_scenery_destruction_zone(<zoneId>, 100);` nell'unica
azione del trigger 1. È l'unico modo per rendere persistente il danno allo scenario.

---

## 5. Moduli d'ispirazione per Warfare-Model

### 5.1 `DC_Weather.lua` — modello sinottico a catena di Markov

È il modulo più direttamente riusabile, e quello che l'utente ha indicato. Non genera
meteo casuale per missione: **simula sistemi di pressione che persistono nel tempo di
campagna**.

**Cinque stati sinottici**, ciascuno con una durata estratta all'ingresso:

| Stato | Durata |
|---|---|
| `high` (alta pressione) | 1–5 giorni (86 400–432 000 s) |
| `low front cold` (fronte freddo) | 4–8 ore |
| `low front warm` (fronte caldo) | 12–24 ore |
| `low sector cold` (settore freddo) | 6–48 ore |
| `low sector warm` (settore caldo) | 6–48 ore |

**Transizioni** — non uniformi, ma meteorologicamente plausibili:

```
P(high) = pHigh / (pHigh + pLow)          -- da camp.weather, es. 60/40

se non high:
    da "front cold"  → "sector cold"       (il fronte passa, resta il settore)
    da "front warm"  → "sector warm"
    da un settore    → fronte, scelto dal gradiente termico:
                       zoneTemp > zoneNextTemp → "front cold"
                       zoneTemp < zoneNextTemp → "front warm"
                       uguali                  → resta nello stesso settore
```

Lo stato vive in `camp.weather`: `zone`, `zoneNext`, `zoneStart`, `zoneEnd`, `zoneTemp`,
`zoneNextTemp`, `refTemp`, `pHigh`, `pLow`. Il cambio scatta quando
`elapsed_time > camp.weather.zoneEnd`, con `elapsed_time = (camp.day-1)*86400 + camp.time`.

**Intensità del fronte.** Durante un fronte, `strength` è interpolato linearmente sulla
durata residua:

```lua
strength = 10 - front_remaining * 10 / front_duration      -- 0 all'inizio, 10 alla fine
temperature = ceil(zoneTemp + strength * (zoneNextTemp - zoneTemp) / 10)
```

Il fronte caldo scala anche nubi e precipitazioni su `strength`:
`thickness = ceil(strength*200)`, `density = min(ceil(strength*1.5), 10)`,
`iprecptns = floor(strength*0.2)`.

**Parametri derivati per stato:**

| Stato | preset nubi | densità | precip. | turbolenza | QNH |
|---|---|---|---|---|---|
| `high` | 0–5 (per temperatura) | 0 | 0 | 0–10 | 760–780 |
| `front cold` | 25–30 | 9–10 | 1–2 | 10–60 | 740–760 |
| `front warm` | 10–20 | ∝ strength | ∝ strength | 5–30 | 740–760 |
| `sector cold` | 20–25 | 0–1 | 0 | 5–30 | 740–760 |
| `sector warm` | 5–20 | 1–4 | 0 | 5–30 | 740–760 |

Nell'alta pressione il preset dipende dalla temperatura: `T ≥ 30` → nessuna nube;
`T ≥ 25` → preset 0–2; altrimenti 1–5. Vento coerente su tre livelli da un'unica direzione:
`atGround = v`, `at2000 = v*0.8`, `at8000 = v*2.5`.

**Presets volumetrici.** Tabella di **esattamente 30 voci** con
`altiMin`/`altiMax`/`name`/`nameVignette` (`Preset1..Preset27`, `RainyPreset1..3`), che mappano
i preset nuvole volumetriche di DCS 2.7+ sul range di quota base ammesso. Gli indici usati per
stato: alta pressione 0–5 (per temperatura), fronte freddo 25–30, fronte caldo 10–20,
settore freddo 20–25, settore caldo 5–20.

> **Attenzione se si riusa la tabella.** Confrontata con la lista canonica di `pydcs`
> (`dcs/cloud_presets.py`), la tabella di DC_Weather contiene tre imprecisioni:
> `Preset1` ha `altiMax = 4100` invece di 4200; `RainyPreset1` ha `altiMax = 2500` invece di
> 2940; `RainyPreset3` ha `nameVignette = "Overcast And Rain 2"` (dovrebbe essere 3). C'è
> anche un refuso ricorrente `"Hight Scattered"` per `"High Scattered"`. Nessuna è grave —
> restringono leggermente il range di quota — ma per Warfare-Model conviene prendere la
> tabella da `pydcs`, riportata per intero in Appendice A. La base è estratta in `[altiMin, altiMax]` del preset scelto,
sommata a `FieldElevation` (quota della base del player) nei casi con nubi basse — così il
player non si ritrova la base aerea dentro le nuvole.

**Nebbia** — condizionata, non casuale: vento al suolo `< 2 m/s` **e** temperatura fra
−2 °C e 12 °C, poi 50% di probabilità → `thickness ∈ [0,1000]`, `visibility ∈ [0,10000]`.

> **Nota**: i range che DCE usa non coincidono con quelli che DCS accetta dall'API runtime
> (`thickness` [100, 5000], `visibility` [100, 100000]). In particolare `thickness = 0`
> significa "nessuna nebbia", quindi il `math.random(0, 1000)` di DCE può produrre valori
> sotto il minimo accettato.

> ⚠️ **`turbulence` per fascia di quota: probabilmente ignorato da DCS.** DC_Weather scrive
> `mission.weather.turbulence = {atGround, at2000, at8000}`, e quel blocco compare nei `.miz`
> generati. Ma **non compare nel `base_mission.miz` salvato dal Mission Editor**, che ha solo
> `groundTurbulence` — e `pydcs` modella solo `turbulence_at_ground`. L'indizio è forte: DCE
> sta scrivendo un campo che il simulatore non legge, e la turbolenza effettiva resta quella
> di `groundTurbulence` (che DCE lascia a 0). **Da verificare in gioco prima di replicarlo.**

**Modulazione diurna** — minimo alle 5, massimo alle 17, 1 °C/ora:
`h ≤ 5 → T - 7 - h`; `h ≤ 17 → T - 17 + h`; `h > 17 → T + 17 - h`.

**Generazione METAR** — il modulo produce un METAR testuale conforme dai parametri
generati: `ddhhmm`, vento `dddffKT|MPS` (con inversione di 180° da direzione *verso cui*
soffia a direzione *da cui* proviene), visibilità/`CAVOK`, `FG`, `RA`/`SN`/`TS`/`NSW`,
copertura `SKC`/`FEW`/`SCT`/`BKN`/`OVC` + ceiling in centinaia di piedi, `Qxxxx`
(conversione mmHg→hPa: `qnh / 760 * 1013.25`). Supporta unità metriche e imperiali via
`camp.units`.

### 5.2 `camp_triggers` — DSL per eventi di campagna

Motore di eventi scriptati minimale ma espressivo. Ogni trigger:

```lua
["Campaign End Victory 1"] = {
    active = true,
    once   = true,
    condition = 'GroundTarget["blue"].percent < 40',      -- stringa Lua valutata
    action = {
        [1] = 'Action.CampaignEnd("win")',
        [2] = 'Action.Text("...")',
        [3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
    },
}
```

Condizioni e azioni sono **stringhe Lua valutate a runtime** contro due namespace
documentati in testa al file (`Return.*` e `Action.*`):

`Return.Time()`, `Day()`, `Month()`, `Year()`, `Mission()`, `CampFlag(n)`,
`AirUnitActive/Ready/Alive/Base/Player(name)`, `TargetAlive(name)`, `UnitDead(name)`,
`GroupHidden(name)`, `GroupProbability(name)`, `ShipGroupInPoly(name, zones)`.

`Action.Text()`, `TextPlayMission()`, `SetCampFlag()`, `AddCampFlag()`, `AddImage()`,
`CampaignEnd("win"/"draw"/"loss")`, `TargetActive()`, `AirUnitActive/Base/Player()`,
`AirUnitReinforce(src, dst, n)`, `AirUnitRepair()`, `GroundUnitRepair()`,
`AddGroundTargetIntel(side)`, `GroupHidden()`, `GroupProbability()`,
`GroupMove(group, zone)`, `GroupSlave(group, master, bearing, dist)`,
`ShipMission(group, wp, cruise, patrol, start)`, `TemplateActive(tab)`.

Il pattern rilevante: **la narrativa di campagna è dati, non codice**, e il campaign maker
la scrive senza toccare il motore.

### 5.3 `DC_Tactical.commander()` — comandante AI adattivo

Ciclo di feedback che regola i parametri dell'ATO in base all'andamento della campagna.
Per **ciascun lato** (rosso e blu, simmetricamente):

**Input** — da `statistic_data.global_losses`: `winner` (aria/terra/mare),
`delta_loss_perc` (differenziale perdite fra vincitore e perdente),
`delta_loss_cost_perc` (differenziale di *costo*), `diff_loss_perc` (trend fra missioni).
Il flag `checkDifferential` sceglie se pilotare sul valore assoluto o sul trend.

**Mapping intensità → parametri** — interpolazione lineare fra soglie
(`min_perc_for_condition = 5`, `max_perc_for_condition = 80`):

| leva | a 5% | a 80% |
|---|---|---|
| `perc-CNAFT` (numero velivoli) | 0.1 | 0.5 |
| `perc-CPT` (priorità task) | 0.1 | 0.8 |
| `w-CWS` incremento peso | 1.5 | 6 |
| `w-CWS` decremento peso | 0.75 | 0.15 |

**Cinque leve di attuazione:**
`changeNumberAircraftForTactics(side, perc, ruolo)` — min/max/richiesti per ruolo;
`changeWeightScore(side, w, categoria)` — peso nello scoring dei target;
`airCostPolicy(side, policy)` — propensione a impiegare asset costosi;
`changePriorityTask(side, task, attributo, classe, perc)` — priorità per coppia
task×attributo; `resetPriorityTask(...)` — ripristino.

**Regola centrale** — chi sta vincendo *risparmia*, chi sta perdendo *insiste*. Es.
vincitore sia in aria che a terra: decrementa caccia e attacco al suolo, riduce l'uso di
asset costosi, e **sposta** la priorità da `Strike/soft`+`armor` verso
`Strike/Structure`+`Bridge` — cioè dal tattico allo strategico, perché la superiorità
tattica è già acquisita.

**Reset ciclico** — ogni `RESET_PERIOD` missioni tutti i parametri tornano ai default,
per impedire la deriva cumulativa. Le direttive attuate sono archiviate in
`report_commander[]` con `mission`, `winner`, `directive_executed`, `target_priority`,
`config_module` — uno storico completo e ispezionabile delle decisioni del comandante.

Esiste anche un livello superiore, `airDirective(side, tactic)`, con un vocabolario di
tattiche nominali su tre gradi d'intensità (`moderate` / normale / `significative`) e
quattro assi (`offensive action`, `offensive strategic action`, `air superiority`, …),
ciascuna espansa in una combinazione fissa delle cinque leve. **È esattamente la forma di
"indirizzo strategico" del design C2 di Warfare-Model**: un comando di alto livello che si
traduce meccanicamente in parametri di pianificazione.

### 5.4 Altri meccanismi notevoli

- **`DC_MissionScore.lua`** — trucco per il sistema campagne di DCS: la prima missione ha
  score 51 (avanza di stage), tutte le successive 50 (resta nello stage). La progressione
  reale è gestita da DCE, non da DCS. Fine campagna: 51 = vittoria/pareggio, 49 = sconfitta.
- **`DC_Time.lua`** — salto temporale casuale in `[idle_time_min, idle_time_max]` fra una
  missione e l'altra; con `OnlyDayMission` scorre in avanti a passi di 1 ora finché la
  finestra missione non cade fra alba e tramonto (con tolleranza `HourlyTolerance` %).
  Classifica la missione come `day` / `night` / `day-night` / `night-day`.
- **Loop di generazione con criteri di giocabilità** (`DEBRIEF_Master.lua:573-655`) — la
  missione viene rigenerata finché non esiste un volo assegnabile al player, fino a 50
  tentativi. I `playability_criterium` diagnosticano il fallimento: `active_unit`, `base`,
  `ready_aircraft`, `tot`, `target`, `target_firepower`, `weather`, `target_range`,
  `coop`, `intercept`. Ogni fallimento avanza il tempo e riprova.
- **`DC_EndCampaign.lua`** — a campagna finita svuota tutte le `country.plane/vehicle/ship/
  helicopter/static`, azzera i trigger e i briefing, lasciando un `.miz` vuoto con solo il
  titolo `CAMPAIGN VICTORY`/`DRAW`/`DEFEAT`.
- **`UTIL_Log.lua`** — logger con livelli (`trace`, `traceVeryLow`, `traceLow`, `debug`,
  `info`, `warn`, `error`, `fatal`) e un file per modulo per missione
  (`LOG_<Modulo>.<n>.log`). Ogni modulo crea la propria istanza con `dofile` — non è un
  singleton, quindi ognuno ha il suo `outfile`.

---

## 6. Debolezze strutturali di DCE (da non replicare)

1. **Stato globale condiviso senza incapsulamento.** `camp`, `oob_air`, `targetlist`, ecc.
   sono globali mutate da ~30 script in sequenza. L'ordine di `dofile` in
   `MAIN_NextMission.lua` è semantica implicita e non verificabile.
2. **Identità basata su nomi e sottostringhe.**
   `string.find(events[e].initiator, " "..unit.name.." ", 1, true)` per risolvere l'unità
   di appartenenza: un nome squadriglia che sia sottostringa di un altro rompe
   silenziosamente le statistiche.
3. **Attribuzione kill "last hitter wins"** — sistematicamente errata nel fuoco combinato,
   e senza traccia del contributo parziale.
4. **Dipendenza da Windows e dalla shell**: `os.execute('start cmd /k ...')`, `notepad.exe`,
   path con backslash, `os.getenv('USERPROFILE')`.
5. **Fragilità della de-sanitizzazione**: ogni update DCS ripristina `MissionScripting.lua`
   e la campagna smette silenziosamente di progredire (mitigato solo dal messaggio
   in-game).
6. **Nessuno schema né versionamento dei file di stato.** `TableSerialization` non emette
   metadati; se cambia la forma di `targetlist`, le campagne in corso si rompono.
7. **Path assoluti hard-coded** nel codice di test (`DC_Logistic.lua:372-376`,
   `E://DCE/DCE_GW_1975/...`).
8. **Perdita d'informazione in cattura**: `event.weapon` è disponibile ma mai registrato;
   `health` solo per aerei/elicotteri, mai per mezzi terrestri.

---

## 7. Applicazione a Warfare-Model

### 7.1 Il vantaggio che Warfare-Model ha già

`lupa` è in `requirements.txt` e `Code/Persistence/Source/DCS_Data_Management.py`
espone `convert_lua_to_python_module(lua_file_path, output_module_path, table_name)`.

⚠️ **`lupa` non risulta però installato nel venv del progetto** (`venv/bin/python -c
"import lupa"` fallisce), quindi oggi `DCS_Data_Management.py` non è importabile. Va
installato prima di poterlo usare. Verificato a parte con lupa 2.8 su un interprete
separato: **tutti e 14 i file di stato DCE si caricano correttamente** (v. §3.6).
Warfare-Model può quindi **leggere nativamente in Python tutti i formati analizzati**
(`mission`, `warehouses`, `dictionary`, `camp_status.lua`, `MissionEventsLog.lua`) senza
scrivere un parser Lua. Il `.miz` è uno zip: `zipfile` + `lupa` bastano.

### 7.2 Corrispondenze dirette

| DCE | Warfare-Model | Nota |
|---|---|---|
| `camp` | `Context/Campaign_State.py` (`CampaignState`) | WM ha già snapshot per missione + `save`/`load`/`restore` |
| `targetlist` | `Context/Target_Status_History.py` | WM ha già lo storico per-blocco |
| `oob_air[].roster` | `Block/Military.py`, `Asset/Aircraft.py` | WM è più granulare (asset individuali) |
| `supply_tab`/`airbase_tab` | `Context/Logistic_Lines.py` | propagazione integrità → efficienza |
| `DC_Tactical.commander()` | `Logic/Strategical_Evaluation.py` (ancora stub) | vedi 7.4 |
| `DC_Weather.lua` | `Logic/Meteo_Analysis.py` (placeholder) | vedi 7.3 |
| `camp_triggers` | *(assente)* | vedi 7.5 |
| `ATO_Generator`/`ATO_FlightPlan` | `Logic/Air_Resources_Assigner.py`, `Air_Route_Manager.py` | |
| `EventsTracker.lua` | *(assente)* | vedi 7.6 |

### 7.3 `Meteo_Analysis.py` — sostituire il placeholder con il modello sinottico

`Logic/Meteo_Analysis.py` è dichiaratamente un placeholder deterministico: 69 righe,
`has_adverse_weather()` guarda solo il mese e la parità di
`date.day + sum(ord(c) for c in region_name)`. La docstring dice esplicitamente che è
"pensata per essere sostituita in futuro da una generazione meteo vera senza dover cambiare
la forma dei dati che consuma".

`DC_Weather.lua` fornisce quel modello, già validato su anni di campagne:

- stato sinottico persistente a 5 zone con durate differenziate, in un
  `WeatherState(zone, zone_next, zone_start, zone_end, zone_temp, zone_next_temp)`
  serializzato dentro `CampaignState`;
- transizioni pilotate da `P(high) = pHigh/(pHigh+pLow)` e dal gradiente termico;
- `strength` interpolato sulla durata del fronte → intensità di nubi/precipitazioni/temperatura;
- modulazione diurna 1 °C/ora con minimo alle 5 e massimo alle 17;
- nebbia condizionata a vento < 2 m/s e temperatura in [−2, 12] °C.

Il contratto attuale (`{'day': bool, 'night': bool, 'adverse_weather': bool}`) resta
compatibile: `adverse_weather` diventa una funzione della zona attiva e della `strength`,
non più della parità del giorno. Il modello copre anche il caso multi-regione previsto dal
design C2: **una zona sinottica per Region**, con `refTemp`/`pHigh`/`pLow` per regione.

Un dettaglio da riusare: la scala presets con `altiMin`/`altiMax` e il vincolo
`base += FieldElevation`. Se WM genererà `.miz`, serve per non mettere le basi dentro le
nuvole.

### 7.4 `Strategical_Evaluation.py` — il comandante come ciclo di feedback

`commander()` di `DC_Tactical.lua` è il riferimento più prezioso per il layer
strategico/tattico ancora stub. Gli elementi trasferibili:

1. **Metrica di vantaggio come differenziale, non come valore assoluto.** DCE non guarda
   "quante perdite ho", ma `delta_loss_perc` fra vincitore e perdente, e in parallelo
   `delta_loss_cost_perc` (differenziale di *costo*) — che cattura il caso "perdo pochi
   aerei ma costosissimi". Rilevante per la memoria
   `feedback_combat_power_action_selection`: è un vettore di metriche, non uno scalare.
2. **Interpolazione lineare fra soglie** invece di if-then a scalini: `value(type, v, sign)`
   mappa `[min_perc, max_perc]` su range diversi per ogni leva. Facile da tarare, continuo.
3. **Leve separate dalla decisione.** `changeNumberAircraftForTactics`, `changeWeightScore`,
   `airCostPolicy`, `changePriorityTask` sono attuatori puri; `commander()` decide *quali*
   e *quanto*. Questa separazione mappa bene sulla divisione
   `Tactical_Analysis` (misura) / `Tactical_Evaluation` (punteggia) / planner (decide) già
   adottata nel refactor di `Region.py`.
4. **Simmetria rosso/blu nello stesso ciclo** — `for i, side_name in ipairs(side)` con
   `enemy_side_name = side[i%2+1]`. Coerente con la dottrina per-side già implementata in
   TASK 1 del design C2.
5. **Reset ciclico** ogni `RESET_PERIOD` missioni contro la deriva cumulativa.
6. **`report_commander` come audit trail**: ogni direttiva archiviata con missione,
   vincitore, priorità risultanti e config. È il modello per il `RegionInfoReport` /
   protocollo propose-approve del design C2 — **le decisioni del comandante sono dati
   persistenti e ispezionabili**, non effetti collaterali.
7. **`airDirective(side, tactic)` è l'indirizzo strategico.** Vocabolario chiuso di tattiche
   nominali (`"increment air superiority"`, `"moderate increment offensive strategic
   action"`, …) su 3 intensità × N assi, ciascuna espansa in una combinazione fissa di
   leve. È la forma esatta che serve al C2 globale per emettere un indirizzo che il C2
   regionale traduce in pianificazione.

### 7.5 `camp_triggers` — motore di eventi di campagna

Warfare-Model non ha un equivalente. Il valore del pattern non è il DSL a stringhe (in
Python conviene un registry di callable o una piccola grammatica dichiarativa, non
`eval`), ma **la separazione fra motore e narrativa**: condizioni e azioni con nomi
stabili, trigger `active`/`once`, narrativa in un file di dati.

Le azioni DCE più interessanti da replicare:
`AirUnitReinforce(src, dst, n)` (attivazione riserve), `AirUnitRepair`/`GroundUnitRepair`
(rigenerazione), `AddGroundTargetIntel(side)` (**rivelazione di intelligence — si lega
direttamente al lavoro fog-of-war/`use_recon` di Fase 2**), `GroupMove(group, zone)` e
`ShipMission(...)` (movimento di forze fuori dal ciclo ATO).

### 7.6 Ingestione dei risultati missione — cosa serve davvero

Se Warfare-Model dovrà consumare risultati da DCS, l'architettura DCE dice chiaramente
**cosa va fatto dentro DCS e cosa fuori**:

Dentro DCS, il minimo indispensabile:
- un `world.addEventHandler` che registri gli eventi con `getName()`, `getID()`,
  `getPlayerName()`, `getLife()/getLife0()`;
- il tracciamento a due fasi dello scenery (hit → registra; dead → aggiungi coordinate);
- il campionamento salute navi a inizio/fine (non esistono eventi utili);
- l'export su `S_EVENT_MISSION_END`.

Miglioramenti rispetto a DCE, a costo quasi nullo:
- **registrare `event.weapon`** (`getTypeName()`, `getDesc()`) — DCE lo butta via, ma è il
  dato che permetterebbe di verificare i modelli di firepower di WM contro l'esito reale;
- **registrare `health` anche per veicoli e navi**, non solo per aerei;
- **registrare tutti gli hit** con l'identità del colpitore, invece di sovrascrivere in
  `hit_table`, così l'attribuzione del danno può essere proporzionale invece che
  "last hitter wins";
- emettere **JSON** invece di sorgente Lua (più semplice lato Python, e verificabile);
- includere un **header di versione di schema** nel file esportato.

Fuori da DCS, il ciclo `debrief → update stato → genera` mappa su:
`CampaignState.add_campaign_snapshot()` → aggiornamento `Region`/`Block`/`Asset` →
`Strategical_Evaluation` → `Air_Resources_Assigner` → serializzazione `.miz`.

**L'alternativa che DCE non usa: l'ambiente Hooks.** DCE fa tutto dallo script di missione,
che è sandboxato e richiede la de-sanitizzazione. Esiste però un secondo ambiente Lua,
`Saved Games\DCS\Scripts\Hooks\*.lua`, che:

- **non è sandboxato** — `io` e `lfs` sono disponibili senza toccare `MissionScripting.lua`,
  quindi niente da riapplicare a ogni update DCS e niente rischio di sicurezza;
- **persiste fra un caricamento missione e l'altro**, mentre lo script di missione viene
  ricreato ex-novo ogni volta;
- espone il namespace `DCS.*`, fra cui **`DCS.getMissionResult(side)`** (esito 0–100 per
  lato), `DCS.getCurrentMission()` (l'intera tabella missione), `DCS.getMissionFilename()`,
  `DCS.getModelTime()`, `DCS.getUnitProperty(missionId, prop)` e `DCS.writeDebriefing(str)`;
- espone i callback di ciclo di vita via `DCS.setUserCallbacks`: `onMissionLoadEnd`,
  `onSimulationStart`, `onSimulationStop`, `onSimulationFrame`, `onPlayerConnect`,
  `onPlayerChangeSlot`, `onPlayerDisconnect`, …;
- dà accesso a **`net.get_player_info(playerID)`** lato server, che include lo **`ucid`** —
  identificatore di client **stabile fra sessioni diverse**, l'unico modo corretto per
  tenere statistiche per-giocatore in multiplayer (DCE usa `getPlayerName()`, che cambia se
  il giocatore rinomina l'account, e su moduli multi-crew come l'F-14 può restituire il nome
  del RIO invece del pilota).

Architettura consigliata per Warfare-Model, **ibrida**:

| Dove | Cosa | Perché lì |
|---|---|---|
| Script di missione | `world.addEventHandler` sugli `S_EVENT_*`, accumulo in memoria | solo qui si vedono gli eventi di combattimento |
| Hook `Scripts/Hooks/` | scrittura file su `onSimulationStop`, `DCS.getMissionResult`, `net.get_player_info`, notifica al processo Python | `io`/`lfs` senza de-sanitizzazione, sopravvive alla missione |

Il ponte fra i due ambienti è il problema da risolvere (non condividono globali): la via
usuale è che lo script di missione scriva in `env.info()` con un prefisso riconoscibile e
l'hook lo intercetti, oppure — se si accetta la de-sanitizzazione — che scriva direttamente
su file come fa DCE.

Attenzione ai due punti di frizione dell'approccio DCE: la **de-sanitizzazione di
`MissionScripting.lua`** (ripristinata da ogni update DCS — va documentata e verificata a
runtime come fa DCE, oppure evitata passando agli Hooks) e l'**auto-innesco via
`os.execute('start cmd /k ...')`**, che è Windows-only e andrebbe sostituito con polling su
file da parte del processo Python (più portabile e testabile).

**Warehouse: il vincolo è caduto.** Da **DCS 2.8.8 (~agosto 2023)** esiste la classe
`Warehouse` con lettura e scrittura a runtime dell'inventario (`getInventory`, `setItem`,
`addItem`, `removeItem`, `addLiquid`/`setLiquidAmount`, `Airbase.getWarehouse`) — v. §A.4.
DCE si è costruito una logistica parallela (`supply_tab`/`airbase_tab`) perché nel 2020 era
l'unica strada; **oggi non lo sarebbe più**. Warfare-Model può scegliere: modello logistico
proprio (come DCE), oppure agganciarsi ai warehouse nativi, oppure entrambi con
sincronizzazione.

**Il meteo invece resta parzialmente vincolato**: la nebbia è controllabile a runtime
(`world.weather.setFogThickness` / `setFogVisibilityDistance` / `setFogAnimation`, da DCS
2.9.10, dicembre 2024), le **nuvole no** — il preset si imposta solo scrivendo il `.miz`.

**Da valutare prima di progettare: il `Mission State Save` nativo.** Da **DCS 2.9.14.8222
(20 marzo 2025)** ED ha introdotto un salvataggio di stato che genera un **nuovo `.miz`**
applicando a una missione rigenerata gli eventi del teatro: unità distrutte, data/ora,
posizione corrente dei velivoli e waypoint. I warehouse persistono. Funziona solo su
missioni custom non protette, e la roadmap 2026 ne annuncia l'estensione a waypoint avanzati
e comportamento IA. **È concettualmente lo stesso ciclo di DCE, ma nativo.** Prima di
replicare la pipeline di DCE conviene capire se questo meccanismo copre già parte del
lavoro — merita un giro di ricerca dedicato, non l'ho approfondito.

### 7.7 Nota sul design C2 — modello temporale

Il modello temporale di DCE è rilevante per il design C2 di Warfare-Model
(sessioni DCS/virtuali interleaved con offset 1-2h). DCE usa:
`camp.time` (ora del giorno, secondi) + `camp.day` (contatore giorni) + `camp.date`
(data di calendario), con avanzamento per **salto casuale** in
`[idle_time_min, idle_time_max]` (3h–4h nella campagna analizzata) e
`mission_duration = 5400` (1h30). Il tempo sinottico del meteo usa una terza scala,
`elapsed_time = (camp.day-1)*86400 + camp.time`, monotòna dall'inizio campagna.

Tre scale temporali distinte per tre scopi (ora del giorno per alba/tramonto, calendario
per la narrativa, tempo assoluto per i processi continui) è una separazione che vale la
pena replicare.

---

## 8. Inventario dei file analizzati

**Motore** (`DCE/ScriptsMod.NG/`, ~1.5 MB di Lua):
`MAIN_NextMission.lua` (572 righe), `DEBRIEF_Master.lua` (681),
`DEBRIEF_StatsEvaluation.lua`, `DEBRIEF_Text.lua`, `BAT_FirstMission.lua`,
`BAT_SkipMission.lua`, `DC_Weather.lua` (782), `DC_Time.lua`, `DC_Tactical.lua`,
`DC_Logistic.lua`, `DC_UpdateTargetlist.lua`, `DC_UpdateOOBGround.lua`,
`DC_CheckTriggers.lua`, `DC_DestroyTarget.lua`, `DC_Briefing.lua`, `DC_Prune.lua`,
`DC_MissionScore.lua`, `DC_EndCampaign.lua`, `DC_NavalEnvironment.lua`,
`DC_StaticAircraft.lua`, `DC_Refpoints.lua`, `DC_LoadoutsAssignment.lua`,
`ATO_Generator.lua`, `ATO_FlightPlan.lua`, `ATO_RouteGenerator.lua`,
`ATO_ThreatEvaluation.lua`, `ATO_Timing.lua`, `ATO_PlayerAssign.lua`,
`UTIL_Functions.lua`, `UTIL_Log.lua`, `UTIL_inspect.lua`, `UTIL_ResetCampaign.lua`,
`UTIL_HelpBalancePower.lua`, `conf_mod_check.lua`.

**Script di missione** (`ScriptsMod.NG/Mission Scripts/`, girano *dentro* DCS):
`EventsTracker.lua` (470 righe — **il file chiave**), `GCIscript.lua`,
`AddCommandRadioF10.lua`, `CustomTasksScript.lua`, `CarrierIntoWindScript.lua`,
`ARM_Defence_Script.lua`, `Pedro.lua`, `EWR_Detection.lua`.

**Stato/config** (`Missions/Campaigns/1975 Georgian War/`):
`Active/` (11 file), `Init/` (12 file incl. `db_firepower.lua` 318 KB,
`db_loadouts.lua` 331 KB), `Debriefing/Debriefing 1.txt`,
`Debug/MissionEventsLog.2t.lua` (481 KB, 2808 eventi — campione principale).

**Archivi**: `Init/base_mission.miz` (template), `1975 Georgian War_first.miz`,
`1975 Georgian War_ongoing.miz` (generato).

**Launcher**: `FirstMission.bat`, `SkipMission.bat`, `DEBUG_DebriefMission.bat`,
`Init/path.bat` + varianti `*Testing.bat`.


---

## Appendice A — Riferimento piattaforma DCS

Materiale raccolto da fonti esterne (Hoggitworld, pydcs, MiST, MOOSE, forum ED) a
complemento dell'analisi del codice DCE. Utile come riferimento se Warfare-Model dovrà
generare o consumare file DCS.

### A.1 I tre ambienti Lua di DCS

| Ambiente | Dove | Sandbox | Persiste fra missioni | API principali |
|---|---|---|---|---|
| **Mission Scripting** | dentro il `.miz`, via trigger `DO SCRIPT (FILE)` o init script | **sì** — `os`/`io`/`lfs` disabilitati | no, ricreato ogni volta | `world`, `coalition`, `trigger`, `Unit`, `Group`, `Controller`, `timer`, `env`, `land`, `atmosphere`, `coord`, `missionCommands`, `net`, `VoiceChat`, `Warehouse` |
| **GUI / Hooks** | `Saved Games\DCS\Scripts\Hooks\*.lua` | no | **sì** | `DCS.*`, `net.*`, callback `on*` |
| **Export** | `Saved Games\DCS\Scripts\Export.lua` | no | sì | `LoGet*` (telemetria ownship), `LuaExportStart/BeforeNextFrame/AfterNextFrame/Stop` |

Gli script Hooks sono caricati **ciascuno in un environment isolato**: non condividono
globali fra loro, solo lo stato del simulatore.

### A.2 `world.event` — enum completo

| ID | Evento | ID | Evento |
|---|---|---|---|
| 0 | `S_EVENT_INVALID` | 31 | `S_EVENT_LANDING_AFTER_EJECTION` |
| 1 | `S_EVENT_SHOT` | 32 | `S_EVENT_PARATROOPER_LENDING` |
| 2 | `S_EVENT_HIT` | 33 | `S_EVENT_DISCARD_CHAIR_AFTER_EJECTION` |
| 3 | `S_EVENT_TAKEOFF` | 34 | `S_EVENT_WEAPON_ADD` |
| 4 | `S_EVENT_LAND` | 35 | `S_EVENT_TRIGGER_ZONE` |
| 5 | `S_EVENT_CRASH` | 36 | `S_EVENT_LANDING_QUALITY_MARK` |
| 6 | `S_EVENT_EJECTION` | 37 | `S_EVENT_BDA` |
| 7 | `S_EVENT_REFUELING` | 38 | `S_EVENT_AI_ABORT_MISSION` |
| 8 | `S_EVENT_DEAD` | 39 | `S_EVENT_DAYNIGHT` |
| 9 | `S_EVENT_PILOT_DEAD` | 40 | `S_EVENT_FLIGHT_TIME` |
| 10 | `S_EVENT_BASE_CAPTURED` | 41 | `S_EVENT_PLAYER_SELF_KILL_PILOT` |
| 11 | `S_EVENT_MISSION_START` | 42 | `S_EVENT_PLAYER_CAPTURE_AIRFIELD` |
| 12 | `S_EVENT_MISSION_END` | 43 | `S_EVENT_EMERGENCY_LANDING` |
| 13 | `S_EVENT_TOOK_CONTROL` | 44 | `S_EVENT_UNIT_CREATE_TASK` |
| 14 | `S_EVENT_REFUELING_STOP` | 45 | `S_EVENT_UNIT_DELETE_TASK` |
| 15 | `S_EVENT_BIRTH` | 46 | `S_EVENT_SIMULATION_START` |
| 16 | `S_EVENT_HUMAN_FAILURE` | 47 | `S_EVENT_WEAPON_REARM` |
| 17 | `S_EVENT_DETAILED_FAILURE` | 48 | `S_EVENT_WEAPON_DROP` |
| 18 | `S_EVENT_ENGINE_STARTUP` | 49 | `S_EVENT_UNIT_TASK_COMPLETE` |
| 19 | `S_EVENT_ENGINE_SHUTDOWN` | 50 | `S_EVENT_UNIT_TASK_STAGE` |
| 20 | `S_EVENT_PLAYER_ENTER_UNIT` | 51 | `S_EVENT_MAC_EXTRA_SCORE` |
| 21 | `S_EVENT_PLAYER_LEAVE_UNIT` | 52 | `S_EVENT_MISSION_RESTART` |
| 22 | `S_EVENT_PLAYER_COMMENT` | 53 | `S_EVENT_MISSION_WINNER` |
| 23 | `S_EVENT_SHOOTING_START` | 54 | `S_EVENT_RUNWAY_TAKEOFF` |
| 24 | `S_EVENT_SHOOTING_END` | 55 | `S_EVENT_RUNWAY_TOUCH` |
| 25 | `S_EVENT_MARK_ADDED` | 56 | `S_EVENT_MAC_LMS_RESTART` |
| 26 | `S_EVENT_MARK_CHANGE` | 57 | `S_EVENT_SIMULATION_FREEZE` |
| 27 | `S_EVENT_MARK_REMOVED` | 58 | `S_EVENT_SIMULATION_UNFREEZE` |
| 28 | `S_EVENT_KILL` | 59 | `S_EVENT_HUMAN_AIRCRAFT_REPAIR_START` |
| 29 | `S_EVENT_SCORE` | 60 | `S_EVENT_HUMAN_AIRCRAFT_REPAIR_FINISH` |
| 30 | `S_EVENT_UNIT_LOST` | 61 | `S_EVENT_MAX` (sentinella) |

⚠️ **Conflitto fra fonti da risolvere.** Questa tabella (61 valori, 0–60) viene da una lettura
di `DCS_singleton_world`. Una seconda ricerca su `DCS_enum_world` riporta invece **47 valori
(0–46)** e nega l'esistenza di `S_EVENT_HUMAN_AIRCRAFT_REPAIR_*`. Le due liste non sono
conciliabili: probabilmente riflettono pagine wiki di epoche diverse, o una include voci non
ancora rilasciate. **Non ho verificato nessuna delle due su un DCS reale.** Prima di
dipendere da un evento specifico oltre i primi ~30, va controllato in gioco con
`env.info(tostring(world.event.S_EVENT_XXX))`.

Versioni di introduzione confermate puntualmente: `S_EVENT_LANDING_QUALITY_MARK` in **2.7**;
`S_EVENT_RUNWAY_TAKEOFF` / `S_EVENT_RUNWAY_TOUCH` in **2.9.6** (aggiunti per gestire i
*bolter* su portaerei, dove un touch-and-go non genera un vero `land`/`takeoff`). I nomi
legati alle modalità MAC/LMS (51, 56) sono poco documentati.

Campi possibili della tabella `event`: `id`, `time`, `initiator`, `target`, `weapon`,
`place`, `subPlace`, `comment`, `idx`, `coalition`, `cost`, `key` — variano per tipo.

**`S_EVENT_HIT`** (id 2): `{ id, time, initiator = Unit, weapon = Weapon, target = Object }`.
⚠️ In multiplayer `weapon` può essere `nil` per desync/timing anche su un hit valido: un
consumatore non deve darlo per scontato.

### A.3 De-sanitizzazione di `MissionScripting.lua`

File: `<installazione DCS>\Scripts\MissionScripting.lua`, righe 17-19.

```lua
sanitizeModule('os')     -->  --sanitizeModule('os')
sanitizeModule('io')     -->  --sanitizeModule('io')
sanitizeModule('lfs')    -->  --sanitizeModule('lfs')
```

`sanitizeModule(name)` azzera il riferimento globale e rimuove la voce da `package.loaded`.

Pattern di scrittura tipico dallo script di missione:

```lua
local path = lfs.writedir() .. [[Logs\MissionState.lua]]   -- writedir() = Saved Games\DCS\
local f = io.open(path, "w")
f:write("return " .. serialize(myTable))
f:close()
```

Rischi: (a) il file è **sovrascritto da ogni update di DCS**; (b) una volta de-sanitizzato,
**qualsiasi missione o server a cui ci si connette può eseguire codice arbitrario** sul
filesystem locale — sconsigliato su server pubblici non fidati. L'ambiente Hooks (A.1) evita
entrambi i problemi.

### A.4 Struttura `.miz` — riferimento

File core: `mission`, `options`, `theatre`, `warehouses`, `l10n/DEFAULT/dictionary`,
`l10n/DEFAULT/mapResource`. A runtime il file `mission` è accessibile come **`env.mission`**.

**`warehouses`** — due tabelle:

```lua
airports   = { [airbaseId] = warehouseTable }   -- aeroporti
warehouses = { [unitId]    = warehouseTable }   -- FARP, navi, unità con logistica
```

`warehouseTable`: `gasoline`, `jet_fuel`, `diesel`, `methanol_mixture`, `size`, `speed`,
`periodicity`, `coalition`, `unlimitedFuel`/`unlimitedMunitions`/`unlimitedAircrafts`,
`OperatingLevel_Air`/`_Fuel`/`_Eqp`, `aircrafts` (per type-name, con `initialAmount` e
`wsType`), `weapons` (con `wsType` a 4 elementi), `suppliers`.

⚠️ **CORREZIONE — dato superato.** Fino a **DCS 2.8** non esisteva accesso di scripting ai
warehouse, ed è quanto riporta ancora la pagina Hoggitworld sulla struttura `warehouses`. Ma
con **DCS 2.8.8 (~agosto 2023)** è stata introdotta una classe `Warehouse` completa:

| Metodi d'istanza | Statici / correlati |
|---|---|
| `getInventory`, `getItemCount`, `addItem`, `setItem`, `removeItem` | `Warehouse.getByName` |
| `addLiquid`, `getLiquidAmount`, `setLiquidAmount`, `removeLiquid` | `Warehouse.getResourceMap` |
| `getOwner` | `Warehouse.getCargoAsWarehouse`, `Airbase.getWarehouse` |

`getInventory()` ritorna `{weapon={}, liquids={}, aircraft={}}`; i liquidi sono indicizzati
`0` = jet fuel, `1` = aviation gasoline, `2` = MW50, `3` = diesel. Una categoria impostata
come "unlimited" ritorna tabella vuota. Nella stessa release sono arrivati
`autoCapture` / `autoCaptureIsOn` / `setCoalition` per lo stato di cattura delle basi.

La logistica per base è quindi **leggibile e modificabile a runtime**, non solo riscrivibile
offline nel `.miz`.

**`l10n/<locale>/dictionary`** — mappa `DictKey_*` / `ResKey_*` → stringa. Nel file `mission`
i nomi di gruppo, unità e i testi di briefing sono quasi sempre chiavi, non testo. A runtime
si risolvono con `env.getValueDictByKey(key)`.

### A.5 Blocco `weather` — default e range

Da `pydcs/dcs/weather.py`:

| Campo | Tipo | Default |
|---|---|---|
| `atmosphere_type` | int | 0 |
| `season.temperature` | float | 20.0 °C |
| `qnh` | float | 760.0 mmHg |
| `clouds.base` | int | 300 m |
| `clouds.thickness` | int | 200 m |
| `clouds.density` | int 0–10 | 0 |
| `clouds.iprecptns` | enum | `None_=0`, `Rain=1`, `Thunderstorm=2` |
| `fog.thickness` | int | 0 m |
| `fog.visibility` | int | 25 m |
| `enable_fog` | bool | false |
| `visibility.distance` | int | 80000 m |
| `groundTurbulence` | int | 0 |
| `enable_dust` / `dust_density` | bool / int | false / 0 |
| `type_weather` | int | 0 |

`halo.preset`: `"off"`, `"auto"`, `"AtmoHighClouds"`, `"VolumetricOnly"`, `"HighClouds"`,
`"CirrusOnly"`; `halo.crystalsPreset` (opzionale): `AllKinds`, `BasicHaloCircle`,
`BasicHaloWithSundogs`, `BasicSundogsTangents`, `SundogsArcs`, `Tangents`. Il blocco `halo`
è stato **aggiunto con DCS 2.8.0 (novembre 2022)**, insieme a arcobaleno e glory — quindi è
posteriore a `DC_Weather.lua`, che infatti non lo tocca.

Due divergenze fra fonti secondarie e file reali, dove **il file reale ha ragione**:
`modifiedTime` non è modellato da `pydcs` ma è presente in entrambi i `.miz` esaminati;
`fog.density` esisteva fino al 2.7 ed è stato poi rimosso dallo schema. `cyclones[]`: `{ pressure_spread, centerX, centerZ, ellipticity, rotation,
pressure_excess }`, con tipo `Cyclone=0`, `AntiCyclone=1`, `None_=2`.

I campi `density`/`thickness`/`base`/`iprecptns` (sistema classico) e `preset` (volumetrico)
**coesistono** nella stessa tabella: quando `preset` è valorizzato, gli altri sono dati
inattivi/legacy.

### A.6 Preset nuvole volumetriche — lista canonica

Da `pydcs/dcs/cloud_presets.py`. **Usare questa, non quella di `DC_Weather.lua`** (v. §5.1).

| Preset | Nome UI | base min | base max | | Preset | Nome UI | base min | base max |
|---|---|---|---|---|---|---|---|---|
| Preset1 | Light Scattered 1 | 840 | 4200 | | Preset16 | Broken 4 | 1260 | 4200 |
| Preset2 | Light Scattered 2 | 1260 | 2520 | | Preset17 | Broken 5 | 0 | 2520 |
| Preset3 | High Scattered 1 | 840 | 2520 | | Preset18 | Broken 6 | 0 | 3780 |
| Preset4 | High Scattered 2 | 1260 | 2520 | | Preset19 | Broken 7 | 0 | 2940 |
| Preset5 | Scattered 1 | 1260 | 4620 | | Preset20 | Broken 8 | 0 | 3780 |
| Preset6 | Scattered 2 | 1260 | 4200 | | Preset21 | Overcast 1 | 1260 | 4200 |
| Preset7 | Scattered 3 | 1680 | 5040 | | Preset22 | Overcast 2 | 420 | 4200 |
| Preset8 | High Scattered 3 | 3780 | 5460 | | Preset23 | Overcast 3 | 840 | 3360 |
| Preset9 | Scattered 4 | 1680 | 3780 | | Preset24 | Overcast 4 | 420 | 2520 |
| Preset10 | Scattered 5 | 1260 | 4200 | | Preset25 | Overcast 5 | 420 | 3360 |
| Preset11 | Scattered 6 | 2520 | 5460 | | Preset26 | Overcast 6 | 420 | 2940 |
| Preset12 | Scattered 7 | 1680 | 3360 | | Preset27 | Overcast 7 | 420 | 2520 |
| Preset13 | Broken 1 | 1680 | 3360 | | RainyPreset1 | Overcast And Rain 1 | 420 | 2940 |
| Preset14 | Broken 2 | 1680 | 3360 | | RainyPreset2 | Overcast And Rain 2 | 840 | 2520 |
| Preset15 | Broken 3 | 840 | 5040 | | RainyPreset3 | Overcast And Rain 3 | 840 | 2520 |

### A.7 Identificazione unità e giocatori

**Due ID distinti per unità**, entrambi necessari:

- **runtime ID** — `Unit.getID()`, valido solo nella sessione corrente;
- **mission ID** — assegnato dal Mission Editor, persistente; lato Hooks si legge con
  `DCS.getUnitProperty(missionId, "UNIT_MISSION_ID")`. È quello che compare come
  `initiatorMissionID` nel debrief.log e nel log di DCE.

Altre proprietà via `DCS.getUnitProperty`: `UNIT_RUNTIME_ID`, `UNIT_NAME`, `UNIT_TYPE`,
`UNIT_CATEGORY`.

**Giocatori** — `net.get_player_info(playerID [, attr])` (lato server):

| Campo | Note |
|---|---|
| `id` | playerID di rete |
| `name` | nome visualizzato — **non stabile** |
| `side` | 0 = spettatori, 1 = red, 2 = blue |
| `slot` | slot occupato (formato `unitID_seatID`) |
| `ping` | ms |
| `ipaddr` | solo lato server |
| **`ucid`** | **Unique Client ID — stabile fra sessioni**, solo lato server |

`Unit.getPlayerName()` (Mission Scripting) restituisce `nil` per l'IA; su moduli multi-crew
(F-14) può restituire il nome del RIO invece che del pilota.

Il debrief.log **non** contiene il nome del giocatore negli eventi: l'associazione
giocatore↔unità va costruita durante la sessione correlando `S_EVENT_PLAYER_ENTER_UNIT` /
`net.get_player_info` con gli eventi di combattimento — esattamente quello che fa DCE con
`client_control[]`.

### A.8 MiST e MOOSE — cosa offrono per cattura eventi e persistenza

**MiST** (`mist.lua`, mrSkortch/MissionScriptingTools):

- `mist.addEventHandler(f)` / `mist.removeEventHandler(id)` — wrapper con ID rimovibile.
- Database pronti: `mist.DBs.unitsByName`, `unitsById`, `unitsByCat`, `groupsByName`,
  `groupsById`, `humansByName`, `humansById`, `activeHumans`, `aliveUnits`,
  `zonesByName`, `navPoints`, `markList`.
- **`mist.DBs.deadObjects`** — usa una metatable con `__newindex`: scrivendo una voce, MiST
  recupera automaticamente i dati completi dell'unità (da `aliveUnits`/`removedAliveUnits`)
  al momento della morte. Popolato da un handler interno su `S_EVENT_DEAD` e
  `S_EVENT_CRASH`. È la soluzione pronta al problema che DCE risolve a mano.
- Serializzazione: `mist.utils.serialize`, `mist.utils.basicSerialize`,
  `mist.utils.tableShow` (derivata da slmod). MiST **non** offre funzioni di scrittura su
  file: la persistenza si fa con `io`/`lfs` diretti.

**MOOSE** (FlightControl-Master):

- Classe `EVENT` con `_EVENTDISPATCHER` globale; sottoscrizione con
  `obj:HandleEvent(EVENTS.Dead)` + metodo `obj:OnEventDead(EventData)`. Lo scope dipende
  dall'oggetto: `UNIT` → solo quell'unità, `GROUP` → tutte le unità del gruppo, oggetto
  globale → tutta la missione.
- `EVENTDATA` è molto più ricco di quanto DCE estragga: `IniUnitName`, `IniGroupName`,
  `IniPlayerName`, **`IniPlayerUCID`**, `IniCoalition`, `IniTypeName`, `IniObjectCategory`
  (+ gli equivalenti `Tgt*`), e per l'arma `WeaponName`, `WeaponTypeName`,
  `WeaponCategory`, `WeaponCoalition`.
- **Non esiste una classe MOOSE di persistenza su file.** MOOSE è un framework per la
  sessione live; la persistenza nei progetti MOOSE-based è costruita sopra, con `io`/`lfs`.

### A.9 Fonti

- Hoggitworld: [Simulator Scripting Engine](https://wiki.hoggitworld.com/view/Simulator_Scripting_Engine_Documentation),
  [singleton world](https://wiki.hoggitworld.com/view/DCS_singleton_world),
  [addEventHandler](https://wiki.hoggitworld.com/view/DCS_func_addEventHandler),
  [event hit](https://wiki.hoggitworld.com/view/DCS_event_hit),
  [Miz mission structure](https://wiki.hoggitworld.com/view/Miz_mission_structure),
  [Miz warehouses structure](https://wiki.hoggitworld.com/view/Miz_warehouses_structure),
  [get_player_info](https://wiki.hoggitworld.com/view/DCS_func_get_player_info),
  [getPlayerName](https://wiki.hoggitworld.com/view/DCS_func_getPlayerName),
  [DCS export](https://wiki.hoggitworld.com/view/DCS_export),
  [singleton env](https://wiki.hoggitworld.com/view/DCS_singleton_env)
- pydcs: [`dcs/weather.py`](https://raw.githubusercontent.com/pydcs/dcs/master/dcs/weather.py),
  [`dcs/cloud_presets.py`](https://raw.githubusercontent.com/pydcs/dcs/master/dcs/cloud_presets.py),
  [`dcs/mission.py`](https://github.com/pydcs/dcs/blob/master/dcs/mission.py) — libreria
  Python che legge/scrive `.miz`: **riferimento implementativo diretto per Warfare-Model**
- [MiST `mist.lua`](https://github.com/mrSkortch/MissionScriptingTools/blob/master/mist.lua)
- MOOSE: [Core.Event](https://flightcontrol-master.github.io/MOOSE_DOCS/Documentation/Core.Event.html),
  [de-sanitize DCS](https://flightcontrol-master.github.io/MOOSE/advanced/desanitize-dcs.html)
- [`DCS_ControlAPI.md`](https://github.com/Zaretto/acEFM/blob/master/DCS-API/DCS_ControlAPI.md) — namespace `DCS.*`
- [`dcs_liberation/userdata/debriefing.py`](https://github.com/shdwp/dcs_liberation/blob/master/userdata/debriefing.py) — parser debrief.log con fallback MP
- Forum ED: [debrief.log](https://forum.dcs.world/topic/115576-debrieflog/),
  [DCS debrief / Log file](https://forum.dcs.world/topic/244228-dcs-debrief-log-file/),
  [Debrief.log parser](https://forum.dcs.world/topic/233456-debrieflog-parser/),
  [lfs/io in ME script env](https://forum.dcs.world/topic/159065-making-lfs-and-io-available-in-me-script-environment/)

**Punti non confermati** (segnalati come tali dalla ricerca, da verificare prima di
farci affidamento): il dump completo campo-per-campo del debrief.log singleplayer in forma
di tabella Lua canonica; la mappatura ufficiale 1:1 fra ogni `S_EVENT_*` e la riga
corrispondente nel debrief.log (evidenza diretta solo per `crash` e `dead`); l'esistenza di
una classe MOOSE dedicata alla persistenza.
