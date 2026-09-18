---
name: project-dce-analysis
description: Analisi completa del Dynamic Campaign Engine (DCE/MBot) svolta il 2026-09-18 — dove sono i due documenti prodotti e quali sono le conclusioni chiave su persistenza DCS
metadata:
  type: project
---

Il 2026-09-18 ho analizzato il Dynamic Campaign Engine (DCE di MBot, ScriptsMod **20.47.105**,
package `NG`) in `Analysis/Document/documentazione_dcs/1975 Georgian War/DCE`. Prodotti due
documenti in `Analysis/Document/documentazione_dcs/`:

- **`ANALISI_DCE.md`** (~1275 righe) — analisi del codice: architettura, meccanismo di cattura
  eventi, modello dati di stato, formato `.miz`, moduli d'ispirazione, mapping su Warfare-Model,
  + Appendice A con riferimento piattaforma DCS (enum `S_EVENT_*` completo, 3 ambienti Lua,
  struttura `.miz`, 30 preset meteo da `pydcs`, identità unità/giocatori, MiST/MOOSE).
- **`COMPRENSIONE_PERSISTENZA_DCS.md`** (~440 righe) — report di auto-verifica con etichette di
  fonte (`[CODICE]`/`[DATI]`/`[DOC-LOC]`/`[WEB]`/`[INFER]`) e una Parte 3 esplicita sui confini
  della conoscenza.

**Conclusioni chiave da ricordare:**

1. **DCE non gira dentro DCS.** Gira in `luae.exe` (Lua standalone di DCS) lanciato da `.bat`.
   Dentro DCS c'è solo `Mission Scripts/EventsTracker.lua` (470 righe), che registra eventi via
   `world.addEventHandler` e a `S_EVENT_MISSION_END` scrive 3 file
   (`MissionEventsLog.lua` → `events`, `scen_destroyed.lua` → `scen_log`,
   `camp_status.lua` → `camp`) e lancia il debrief con `os.execute`.
2. **DCE NON usa il `debrief.log` nativo di DCS** — i commenti che lo dicono sono stale. Ne
   ha però **copiato lo schema** (`type`/`t`/`initiator`/`initiatorMissionID`/`target`/
   `targetMissionID`), estendendolo con `health` e `initiatorPilotName`.
2-bis. **`debrief.log` reale analizzato 2026-09-18** (l'utente ha fornito
   `documentazione_dcs/Logs/`, DCS **2.9.29.27468 build 559**) — v. `ANALISI_DCE.md` §2.5.
   È **molto più ricco** del log custom di DCE: 10 chiavi di primo livello fra cui
   **`world_state`** (stato finale di OGNI unità: `unitId`, pos, `dead`, **`life`**, e per gli
   aerei **`payload` con carburante e munizioni residue**), `graveyard` (relitti),
   `warehouses`, `triggers_state`, `result` (0-100), `events` (20 tipi).
   **`linked_event_id` dà la catena causale `shot→hit→kill→score`** (17/17 link risolti):
   **DCS fornisce l'attribuzione kill già fatta** — rende superflua tutta la macchina
   `hit_table`/"last hitter wins" di DCE. Ha anche `weapon_type`, `ammo_consumption`,
   `failure`, `ai abort mission`.
   ⚠️ Due insidie verificate: il file è **valido solo in Lua 5.1** (`world_state` ha un campo
   chiamato **`goto`**, riservato da 5.2 in poi → quotare le chiavi riservate prima di
   caricarlo con lupa); codifica **cp1252**. Il giocatore si riconosce dall'evento
   `under control` con `target='player'`, NON da `initiatorPilotName` (che per l'IA contiene
   il tipo di unità).
   Limiti reali del debrief.log: **niente scenery distrutto** (per quello serve comunque uno
   script in-mission) e formato degenere in multiplayer. → **Usare entrambi i canali.**
3. **Il `.miz` è l'interfaccia principale di scrittura verso DCS.** Una missione è senza stato
   in ingresso: lo stato vive fuori e va iniettato rigenerando il `.miz`. Le unità non possono
   essere istanziate in stato intermedio (vive o morte, nulla in mezzo).
   ⚠️ **CORRETTO 2026-09-18**: avevo scritto che i warehouse non sono accessibili via
   scripting — **era sbagliato**, quel dato era fermo a DCS 2.8. Da **2.8.8 (~ago 2023)**
   esiste la classe `Warehouse` (`getInventory`/`setItem`/`addItem`/`removeItem`/`addLiquid`/
   `Airbase.getWarehouse`) + `autoCapture`/`setCoalition`. Da **2.9.10 (dic 2024)** anche la
   nebbia è runtime (`world.weather.setFogThickness`/`setFogVisibilityDistance`/
   `setFogAnimation`); le **nuvole no**, restano solo da `.miz`.
3-bis. **`Mission State Save` nativo — da valutare prima di replicare DCE.** Da **DCS
   2.9.14.8222 (20 mar 2025)** ED salva lo stato generando un nuovo `.miz` (unità distrutte,
   data/ora, posizione velivoli, waypoint; i warehouse persistono). In espansione nella
   roadmap 2026, che annuncia anche una Dynamic Campaign ufficiale in test interno.
   **Non approfondito**: è il primo punto da chiarire prima di progettare la pipeline.
4. **Esiste un'alternativa migliore che DCE non usa: l'ambiente Hooks**
   (`Saved Games\DCS\Scripts\Hooks\*.lua`) — non sandboxato (niente de-sanitizzazione di
   `MissionScripting.lua`), persiste fra missioni, dà `DCS.getMissionResult(side)` e
   `net.get_player_info().ucid` (unico ID giocatore stabile). Ma **non vede gli eventi di
   combattimento**: serve architettura ibrida Mission Scripting + Hooks.
5. **Il punto più fragile di DCE è l'identità**: rigenerando il `.miz` cambiano anche i mission
   ID, quindi resta solo il nome, risolto per sottostringa
   (`string.find(initiator, " "..unit.name.." ")`). Per Warfare-Model: usare un ID di dominio
   stabile trasportato nel nome in posizione parsabile.
6. **Attribuzione kill DCE = "last hitter wins"** (`hit_table[target] = initiator`). DCS espone
   `S_EVENT_KILL` (id 28) che DCE non usa — probabilmente non esisteva nel 2020.
   DCE mappa 19 eventi su 61 disponibili.

**Tre cose di DCE che valgono per Warfare-Model** (v. `ANALISI_DCE.md` §7):
- `DC_Weather.lua` → sostituisce il placeholder `Logic/Meteo_Analysis.py`: modello sinottico a
  5 zone (`high`, `low front cold/warm`, `low sector cold/warm`) con durate differenziate,
  transizioni su `P(high)=pHigh/(pHigh+pLow)` e gradiente termico, `strength` interpolato sulla
  durata del fronte, modulazione diurna, nebbia condizionata, generazione METAR.
  ⚠️ la sua tabella preset ha 3 imprecisioni vs `pydcs` — usare quella in Appendice A.
- `DC_Tactical.commander()` + `airDirective()` → riferimento per `Logic/Strategical_Evaluation.py`
  (stub): metriche **differenziali** (delta perdite e delta *costo* perdite), interpolazione
  lineare fra soglie, 5 leve di attuazione separate dalla decisione, reset ciclico, audit trail
  in `report_commander`. `airDirective` è esattamente la forma dell'"indirizzo strategico" del
  design C2 — v. [[project-c2-hierarchy-design]].
- `camp_triggers` → DSL dichiarativo per eventi di campagna (namespace `Return.*`/`Action.*`),
  che Warfare-Model non ha. `Action.AddGroundTargetIntel(side)` si lega al lavoro fog-of-war
  di [[project-fase2-recon-combat-power-plan]].

**Vantaggio già disponibile:** `Code/Persistence/Source/DCS_Data_Management.py` ha già
`convert_lua_to_python_module()`. ⚠️ Ma **`lupa` è in `requirements.txt` e NON installato nel
venv**, quindi quel modulo oggi non è importabile. Verificato a parte con lupa 2.8: **tutti e
14 i file di `Active/` si caricano correttamente** (attenzione: sono in **cp1252**, non UTF-8).
Valutare **`pydcs`** prima di scrivere codice di generazione `.miz` — nota però che pydcs
scrive `mission.version = 20` mentre i file reali misurati sono 22 (template DCE) e 23
(Warfare_Model_Test_Mission.miz, giu 2026).

**Non ancora analizzati** (~630 KB, il materiale più utile che resta): `ATO_Generator.lua`,
`ATO_FlightPlan.lua`, `ATO_RouteGenerator.lua`, `DC_LoadoutsAssignment.lua`, `DC_Briefing.lua`
— corrispettivi di `Air_Resources_Assigner` + `Air_Route_Manager`. Anche `db_firepower.lua`
(318 KB) e `db_loadouts.lua` (331 KB), tabelle dati confrontabili con i modelli di firepower di
Warfare-Model ([[project-priority-calc-combat-power-redesign]]).
