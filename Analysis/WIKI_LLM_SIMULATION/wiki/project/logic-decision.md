---
title: "Logic — Decisione Tattica e Strategica"
type: project-module
tags: [package-python, dwm, architecture, implementation]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Logic/Tactical_Analysis.py, Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py, Code/Dynamic_War_Manager/Source/Logic/Strategical_Evaluation.py, Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py, Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py]
related_decisions: ["[[region-tactical-strategic-refactor]]", "[[c2-hierarchy-design]]", "[[datatype-route-edge-waypoint]]"]
related: ["[[logic-routing]]"]
---

## Scopo

Il pacchetto `Code/Dynamic_War_Manager/Source/Logic/` ospita la logica decisionale del Dynamic War Manager: analisi/raccolta di informazioni tattiche, valutazione/scoring tattico (esito di scontri, priorità di attacco/difesa di un blocco militare), valutazione strategica (priorità di teatro, aggregazione multi-regione) e assegnazione concreta delle risorse aeree alle missioni.

Questa pagina **supersede** l'audit storico `Analysis/Modules/08_Logic_Decision.md` (2026-08-16), che è ormai pesantemente superato sul lato "decisione": nel settembre 2026 un refactoring ha estratto 16 funzioni tattiche da `Context/Region.py` in due nuovi moduli — `Tactical_Analysis.py` (analisi, 8 funzioni) e un `Tactical_Evaluation.py` ampliato (scoring, +7 funzioni) — v. [[region-tactical-strategic-refactor]] per il dettaglio dell'8-fasi. L'audit del 2026-08-16 descriveva `Tactical_Evaluation.py` come "non importabile" e `Strategical_Evaluation.py` come "0% di logica funzionante e non importabile": **entrambe le affermazioni sono oggi false**, verificate contro il codice attuale il 2026-09-18 (v. "Stato attuale").

Nella visione di progetto corrente (v. [[c2-hierarchy-design]]), il flusso naturale è: un futuro `Command/C2_Manager`/`C2_Region_Manager` (non ancora costruiti) → `Strategical_Evaluation`/`Strategical_Analysis` (priorità di teatro/regione) → `Tactical_Analysis`+`Tactical_Evaluation` (analisi/scoring a livello di singolo blocco) → `Air_Resources_Assigner` (allocazione concreta di velivoli/loadout alle missioni derivate). Oggi questo flusso non è ancora cablato end-to-end da un orchestratore: `Region.update_military_priorities` è il solo chiamante reale di `Tactical_Analysis`/`Tactical_Evaluation`, e nessun modulo chiama `Strategical_Evaluation` o `Air_Resources_Assigner` da un ciclo di comando superiore (quel livello — `Command/` — non esiste ancora nel codice, v. sotto).

## File e classi principali

| File | Righe | Contenuto |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Tactical_Analysis.py` | 281 | 8 funzioni di analisi (fatti, non punteggi): `estimate_target_combat_power`, `build_recon_cp_snapshot`, `get_target_report`, `profile_to_weapon_distribution`, `target_profile_from_report`, `representative_combat_power`, `target_profile_from_block`, `operative_aircraft_by_model` |
| `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py` | 937 | 7 funzioni di scoring nuove (`target_affinity`, `select_weight`, `calculate_priority`, `calc_surface_priority`, `calc_air_priority`, `calc_attack_priority`, `calc_defense_priority`) + le funzioni tattiche preesistenti (`evaluateGroundTacticalAction`, `calcRecoAccuracy`, `calcFightResult`, `evaluateCombatSuperiority`, `evaluateCriticalityGroundEnemy`, `evaluateGroundRouteDangerLevel`) |
| `Code/Dynamic_War_Manager/Source/Logic/Strategical_Evaluation.py` | 89 | 11 funzioni pubbliche, **tutte stub** (`raise NotImplementedError`) — livello strategico multi-regione, non ancora implementato |
| `Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py` | 1245 | ex `Military_Resources_Assigner.py`; allocazione aeromobile/loadout a missioni, con cascata di disponibilità loadout (anno/dottrina/scorte) |
| `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py` | 242 | classe `CommandControl`; scheletro non importabile, candidato a eliminazione (v. `Manager.py` sotto e [[c2-hierarchy-design]]) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Tactical_Analysis.py` | 678 (64 test) | tutte le 8 funzioni di `Tactical_Analysis.py` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Tactical_Evaluation.py` | 952 (27 test) | le 7 funzioni di scoring nuove, spostate/ampliate qui durante il refactoring; le funzioni tattiche preesistenti (fuzzy) restano solo parzialmente coperte |
| `Code/Dynamic_War_Manager/Source/Test/Test_Air_Resources_Assigner.py` | 2986 (252 test) | copertura estesa di `Air_Resources_Assigner.py` |

### `Tactical_Analysis.py` (nuovo, dal refactoring 2026-09-16)

Analisi/raccolta di informazioni: producono FATTI (profili di composizione di un bersaglio, potenza di combattimento stimata/rappresentativa, inventario di asset), mai un punteggio. Nessuna funzione riceve o importa una `Region` — vincolo deliberato per permettere a un futuro pianificatore di valutare bersagli/scenari ipotetici senza costruire una `Region` reale, e per evitare qualunque ciclo di import verso `Context.Region`.

- `estimate_target_combat_power(report, force, action)` — combat power stimata (fog-of-war) di un bersaglio per una specifica azione, da un report di ricognizione; delega a `Combat_Power_Estimation`.
- `build_recon_cp_snapshot(reports)` — `{block_id: combat_power stimata}` per una lista di report già recuperati dal chiamante (non chiama più `get_recon_reports` internamente — cambio di firma rispetto alla versione pre-refactoring che viveva in `Region`, dove riceveva `observed_side`).
- `get_target_report(report)` — classifica un bersaglio da un report di ricognizione; include il fix "conteggi tutti a zero → nessuna visibilità" (v. [[air-priority-target-specific-loadout]]).
- `profile_to_weapon_distribution(profile)` — converte un `TargetProfile` nella forma a distribuzione pesata usata da `Aircraft_Data.combat_score_target_effectiveness_by_distribution`.
- `target_profile_from_report(report)` — alias/wrapper di `get_target_report`, stesso formato del produttore ground-truth.
- `representative_combat_power(block, force, action=None)` — combat power di un blocco per una forza/azione, usata dal rapporto di priorità.
- `target_profile_from_block(target_block)` — produttore ground-truth (non-random) del profilo bersaglio, tramite `Context.classify_asset_dimension`.
- `operative_aircraft_by_model(block)` — `{model: [Aircraft operativi]}`, usato per pesare `target_affinity` per numero di velivoli.

**Nessuna `@lru_cache`** su queste funzioni (né sulle 7 di `Tactical_Evaluation.py` sotto): rimossa deliberatamente durante il refactoring. Motivazione precisa (v. [[region-tactical-strategic-refactor]]): la cache era su metodo bound di `Region`, quindi condivisa fra **tutte** le istanze `Region` (non una per regione), veniva svuotata quasi a ogni iterazione di `update_military_priorities` (hit-rate reale basso) e 5 punti nei test già la bypassavano con `.__wrapped__`. Più a fondo: un futuro pianificatore "what-if" ha bisogno di valutare scenari ipotetici isolati — con una cache condivisa, due valutazioni ipotetiche sugli stessi blocchi darebbero la stessa risposta congelata. Le due memoizzazioni potenzialmente utili (`target_profile_from_block`, `target_affinity`) verranno reintrodotte solo se una misura futura dimostra un regresso di performance reale, non preventivamente.

### `Tactical_Evaluation.py` (ampliato dal refactoring)

Scoring: assegnano un punteggio/priorità a un'opzione.

**7 funzioni nuove (spostate da `Region.py`)**:
- `target_affinity(block, target_block)` — fattore moltiplicativo `[0.25, 2.0]` che modula la priorità di attacco in base a quanto bene i loadout disponibili di una flotta aerea rendono contro la composizione reale del bersaglio (v. [[air-priority-target-specific-loadout]]).
- `select_weight(target_block, task, block_category, weight_priority_target)` — seleziona il peso di dottrina; `weight_priority_target` ora passato esplicitamente dal chiamante (v. `Context/Doctrine.py` sotto), non più letto da `self`.
- `calculate_priority(...)` — nucleo del calcolo di priorità (militare/logistico/civile), con `recon_cp_snapshot: Optional[Dict]` che sostituisce il vecchio flag `use_recon: bool` (v. sotto).
- `calc_surface_priority`, `calc_air_priority` — priorità per blocchi ground/naval e air rispettivamente; `calc_air_priority` ora riceve `target_item: Tuple[float, Block]` invece di un `target_block` più lookup separato.
- `calc_attack_priority`, `calc_defense_priority` — aggregano su liste di bersagli/alleati; ricevono `route_provider: Callable[[str,str],Optional[Route]]` invece di accedere direttamente a `self.get_shortest_route`.

Il parametro `use_recon: bool` che attraversava 5 firme prima del refactoring è sparito ovunque, sostituito da `recon_cp_snapshot: Optional[Dict[str,float]]` esplicito: `None` = ground-truth ovunque, `{}` = sweep di ricognizione eseguito ma nulla osservato — combinazione oggi non più esprimibile in modo ambiguo (miglioramento, non solo rinomina).

**Funzioni tattiche preesistenti** (non toccate dal refactoring, verificate ancora presenti e nella stessa forma dell'audit 2026-08-16):
- `evaluateGroundTacticalAction` — sistema fuzzy (`skfuzzy`) a 4 antecedenti/20 regole per RETRAIT/DEFENSE/MAINTAIN/ATTACK; commento originale segnala ancora le regole come "non validate".
- `calcRecoAccuracy` — fuzzy a 2 antecedenti per l'accuratezza di un report di ricognizione.
- `calcFightResult` — calcolo non-fuzzy del risultato di uno scontro, con interpolazione su tabella di coefficienti e stime probabilistiche.
- `evaluateCombatSuperiority`, `evaluateCriticalityGroundEnemy` — combat superiority/criticality per azione, su dizionari di asset per categoria.
- `evaluateGroundRouteDangerLevel` — **ancora non funzionante**: usa `v_base.time2attack`, `v_base.efficiency`, `v_base.is_airbase`, `v_base.is_groundbase`, `v_base.artilleryInRange`, nessuno dei quali esiste sulle classi `Block`/`Military` reali; nessun chiamante nel codice.
- `evaluateCriticalityAirdefense` — definita ma **dopo** un `return` nel corpo di `evaluateCriticalityGroundEnemy`: codice morto, mai raggiungibile, oltre a essere essa stessa solo uno stub.

Import morti residui, verificati ancora presenti: `Waypoint`/`Edge` (da `DataType`) importati ma mai usati direttamente (solo `Route` è realmente usato, tramite `route.edges`); commento "da testare" ancora sopra `evaluateCriticalityGroundEnemy`/`evaluateGroundRouteDangerLevel`.

### `Strategical_Evaluation.py`

**Stub intenzionale, non un difetto**: tutte le 11 funzioni pubbliche sollevano `NotImplementedError` (non più `pass` silenzioso come nell'audit 2026-08-16) — `evaluateTacticalReport`, `evaluateDefensePriorityZone`, `definePriorityPatrolZone`, `evaluateResourceRequest`, `evaluateTargetPriority`, `evaluateTotalProduction`, `evaluateStrategicPriority`, `evaluateTotalTransport`, `evaluateLogisticLineTransport`, `evaluateTotalStorage`, `calcCombatPowerCentrum`. Il modulo **è importabile** (bug del `Logger` con `class_name=''` e l'`ImportError` su `GROUND_Military_VEHICLE_ASSET` documentati dall'audit 2026-08-16 sono stati corretti; i blocchi di codice-esempio morto `ConflictGraph`/`PrioritySystem` sono stati rimossi).

Questo stato è il risultato della "Fase 0" del refactoring tattico (v. [[region-tactical-strategic-refactor]]): gli stub restano deliberatamente come documentazione dell'architettura voluta — un analizzatore/valutatore/pianificatore strategico multi-regione — ma non sono stati implementati. Il prossimo passo esplicitamente annotato in quella memoria è "costruire l'analizzatore/valutatore/pianificatore strategico-tattico ancora stubbato in Strategical_Evaluation.py".

**Sviluppo successivo pianificato, non ancora costruito** (v. [[c2-hierarchy-design]]): `Strategical_Evaluation.py` è destinato a restringersi ulteriormente — 4 delle sue 11 funzioni (`evaluateTotalProduction`, `evaluateTotalTransport`, `evaluateTotalStorage`, `calcCombatPowerCentrum`) sono in realtà FATTI di aggregazione multi-regione, non punteggi, e sono previste per uno spostamento in un nuovo `Logic/Strategical_Analysis.py` (pendant di `Tactical_Analysis.py`, non ancora creato) quando quel lavoro verrà ripreso. `Strategical_Evaluation.py` conserverebbe solo le funzioni di vero scoring strategico.

### `Air_Resources_Assigner.py`

Non toccato dal refactoring tattico di settembre, ma esteso rispetto all'audit 2026-08-16 con la cascata di disponibilità loadout (v. [[air-priority-target-specific-loadout]]):

- **API pubblica principale**: `get_aircraft_mission(task, aircraft_availability, mission_requirements, target_data, max_aircraft_for_mission, max_missions, directive)` → `{'fully_compliant': [...], 'derated': [...]}`; `get_loadouts_availability`, `get_ground_mission_task_list`, `get_air_mission_task_list`, `get_available_loadouts` (nuova, cascata anno→dottrina→scorte, v. `project_mra_state`/`project_air_priority_target_specific_loadout`).
- **Costanti**: `_DIRECTIVE_WEIGHTS` (pesi combat/costo per le 5 direttive `performance_high`…`economy_high`), `_REFERENCE_COST_K = 303_000.0`.
- **Derating formula**: `_reduce_target_data` — `multiplier = reduction_ratio + weight*(1-reduction_ratio)`, interpolazione lineare pesata per priorità, con guard su `ratio<=0`/`ratio>=1`.
- **Bug residuo verificato ancora presente** (2026-09-18, non coperto da alcun test — `grep` su `get_air_mission_task_list` nel file di test non trova occorrenze): in `get_air_mission_task_list`, la condizione `if task in [Air_To_Air_Task.FIGHTER_SWEEP.value, Air_To_Air_Task.INTERCEPT.value, Air_To_Air_Task.CAP, Air_To_Air_Task.ESCORT]` confronta `task` (sempre una stringa) con gli ultimi due elementi come membri Enum non `.value` — il confronto per `CAP`/`Escort` non può mai risultare vero, la funzione salta sia l'`if` sia l'`elif` (che gestisce solo `RECON`, con lo stesso problema) e va in `KeyError: 'Aircraft'` alla riga successiva. Stesso identico difetto dell'audit 2026-08-16, mai corretto, tuttora invisibile perché non testato.

### `Scenario_Manager.py` — classe `CommandControl`

**Ancora non importabile**, verificato eseguendo l'import il 2026-09-18: stesso identico bug dell'audit 2026-08-16 — `def __init__(self, side: str, regions: List|None, blocks: Block|None)` usa `Block` come nome del **modulo** importato (`from ...Block import Block`, che importa il package, non la classe), non un tipo → `TypeError: unsupported operand type(s) for |: 'module' and 'NoneType'` alla definizione della classe. Nessun altro bug di questo modulo è stato corretto nel frattempo (stessi problemi su `checkListOfObjects` mai definito, `addBlock` che scrive su `self._events` mai inizializzato, `self.regions`/`Region` mai importati in `executeRecoinnassanceRequest`/`addRegion`).

**Decisione presa, non ancora eseguita** (v. [[c2-hierarchy-design]], item 6 confermato dall'utente): `CommandControl` va eliminato, ma prima va estratto il suo docstring (righe ~159-235, che descrive livelli di operazione aria/terra/mare e livelli di risorse) perché è probabilmente il contenuto letterale dell'"indirizzo strategico" che il futuro `Command/` dovrà implementare.

### `Manager.py` (a livello radice di `Source/`, non nel pacchetto `Logic/`)

Non fa parte di questo pacchetto ma è direttamente rilevante per l'architettura di decisione: `Code/Dynamic_War_Manager/Source/Manager.py` (106 righe, classe `Manager`) è uno scheletro rotto — verificato di persona: `__repr__` referenzia `self._name`/`self._description`/`self._side`/`self._clients`/`self._server`/`self._warehouse`, nessuno dei quali è mai impostato in `__init__` (solo `self._region`, `self._blocks`, `self._limes`, `self._assets`, `self._payloads` lo sono), quindi `repr()`/`print()` su un'istanza fallirebbe. È stato storicamente indicato (erroneamente) in un vecchio audit del wiki come "il naturale candidato entry-point del DWM"/"C² Planner". **Una nuova decisione architetturale lo destina alla cancellazione o rinomina** (v. [[c2-hierarchy-design]]): libererebbe il nome `C2_Manager` per il nuovo componente stateful pianificato in un package `Command/` non ancora esistente (verificato: `Code/Dynamic_War_Manager/Source/Command/` non esiste, 2026-09-18). La documentazione completa di `Manager.py` vive in una pagina dedicata (`utility-manager.md`, in lavorazione da un altro agente) — qui si menziona solo per la rilevanza diretta sull'architettura Logic/decisione: il piano C2 tratta `Manager.py` e `Scenario_Manager.CommandControl` come due doppioni concettuali parziali dello stesso ruolo mai completato, entrambi da rimuovere/sostituire con lo stesso lavoro di costruzione di `Command/`.

## Dipendenze

- **`Tactical_Analysis.py`**: `Context.Context`, `Context.Combat_Power_Estimation`, `Block.Block` (+`ASSET_TYPE`), `Block.Military`, `Utility.LoggerClass`. Nessuna dipendenza da `Region`, da `skfuzzy` o da `Aircraft_Data` — deliberatamente leggero (v. sopra).
- **`Tactical_Evaluation.py`**: oltre a quanto sopra, `Asset.Aircraft_Data.Aircraft_Data`, `skfuzzy`/`numpy` (per le funzioni fuzzy preesistenti), `DataType.Waypoint`/`Edge`/`Route` (solo `Route` realmente usato). Import **lazy** da `Context/Region.py` (dentro `update_military_priorities`/`_calc_air_priority` prima del refactoring, ora dentro i punti equivalenti in `Region.py`) — non a livello di modulo, per non gravare su chi non calcola mai una priorità aerea (costo di import misurato: `skfuzzy`+`Aircraft_Data` ≈ 0.6s aggiuntivi).
- **`Strategical_Evaluation.py`**: `Utility.LoggerClass` soltanto, più import `TYPE_CHECKING`-only di `Block`/`Region` (coerente con l'essere puro stub).
- **`Air_Resources_Assigner.py`**: `Block.Military` (a livello di modulo — verificato **non più bloccato** dal ciclo `Aircraft→Aircraft_Data→Aircraft_Loadouts→Aircraft_Weapon_Data→Aircraft` che l'audit 2026-08-16 descriveva come bloccante: l'import diretto del modulo oggi riesce, ~0.95s), `Context.Context`, `Asset.Aircraft_Loadouts`, `Asset.Aircraft_Data`.
- **`Scenario_Manager.py`**: come da audit precedente, non importabile — dipendenze non verificabili oltre il punto di fallimento.

## Stato attuale

Verificato eseguendo realmente la suite (`.direnv/python-3.12/bin/python3 -m unittest discover`) il 2026-09-18, non solo leggendo il codice:

| Modulo | Importabile? | Test |
|---|---|---|
| `Tactical_Analysis.py` | **Sì** | 64/64 OK |
| `Tactical_Evaluation.py` | **Sì** | 27/27 OK |
| `Strategical_Evaluation.py` | **Sì** (stub `NotImplementedError`, nessun test — coerente con lo stato di puro stub) | — |
| `Air_Resources_Assigner.py` | **Sì** | 252 OK (skipped=3) |
| `Scenario_Manager.py` | **No** — stesso bug `Block|None` dell'audit 2026-08-16, mai corretto | nessun test presente |

Questo **corregge sostanzialmente** l'audit 2026-08-16, che riportava `Tactical_Evaluation.py` e `Strategical_Evaluation.py` come non importabili e `Air_Resources_Assigner.py` come bloccato al 100% dal ciclo di import Asset-Air: tutti e tre questi blocchi risultano oggi risolti (`Strategical_Evaluation.py` dalla "Fase 0" del refactoring tattico; `Tactical_Evaluation.py` dallo stesso refactoring che vi ha spostato le 7 funzioni di scoring, correggendo il bug del `Logger` nel farlo; `Air_Resources_Assigner.py` da un fix di import morto già registrato in una memoria di progetto precedente all'audit stesso, mai riflesso nel documento). Solo `Scenario_Manager.py` resta esattamente nello stato documentato nell'audit.

## Problemi aperti

- **`get_air_mission_task_list` (`Air_Resources_Assigner.py`) ha ancora il bug Enum-vs-`.value` su CAP/Escort/Recon**, verificato tuttora presente e non testato (v. sopra).
- **`Strategical_Evaluation.py` resta senza alcuna implementazione reale** — 11 stub, nessun collegamento a `Tactical_Evaluation`/`Air_Resources_Assigner`; è lavoro esplicitamente futuro, non un difetto da correggere di corsa.
- **`Scenario_Manager.CommandControl` è marcato per eliminazione ma il codice non è stato ancora toccato** — resta non importabile, zero test, zero chiamanti nel resto del progetto.
- **Nessun orchestratore di livello superiore collega ancora i quattro moduli** in un ciclo coerente analizza→pianifica→assegna risorse: `Region.update_military_priorities` è l'unico chiamante reale di `Tactical_Analysis`/`Tactical_Evaluation` oggi; il livello `Command/` che dovrebbe chiudere il cerchio (v. [[c2-hierarchy-design]]) non esiste ancora nel codice.
- **`evaluateGroundRouteDangerLevel`/`evaluateCriticalityAirdefense`** in `Tactical_Evaluation.py` restano esattamente nello stato non funzionante documentato dall'audit 2026-08-16 (API su `Block`/`Military` inesistente la prima, codice irraggiungibile la seconda) — non toccate dal refactoring tattico perché fuori dal suo perimetro (le 7 funzioni spostate sono tutte diverse da queste).

## Note

- `Manager.py` (root di `Source/`, non in `Logic/`) è destinato a eliminazione/rinomina per liberare il nome `C2_Manager` nel futuro package `Command/` — v. sezione dedicata sopra e [[c2-hierarchy-design]]; documentazione completa in una pagina `utility-manager.md` separata (in lavorazione), non duplicata qui.
- Le 7 funzioni di scoring nuove in `Tactical_Evaluation.py` e le 8 di `Tactical_Analysis.py` usano `snake_case`, mentre le funzioni fuzzy preesistenti nello stesso `Tactical_Evaluation.py` usano `camelCase` (`evaluateGroundTacticalAction` ecc.) — coesistenza deliberata, nessuna rinomina in blocco pianificata (romperebbe i chiamanti di test esistenti).

## Decisioni architetturali rilevanti

- [[region-tactical-strategic-refactor]] — il refactoring a 8 fasi che ha creato `Tactical_Analysis.py` ed esteso `Tactical_Evaluation.py`, estraendole da `Context/Region.py`; motiva la rimozione di `@lru_cache` documentata sopra.
- [[c2-hierarchy-design]] — architettura C2 a due livelli (globale/regionale) che userà `Strategical_Evaluation`/`Tactical_Evaluation` come livelli di valutazione; decide la cancellazione di `Scenario_Manager.CommandControl` e la rinomina/eliminazione di `Manager.py`; introduce il concetto (non ancora costruito) di `Logic/Strategical_Analysis.py` e del package `Command/`.
- [[datatype-route-edge-waypoint]] — canonicità di `DataType.Route`/`Edge` per il lato ground, di cui `Tactical_Evaluation.evaluateGroundRouteDangerLevel` è un consumatore mai completato.
