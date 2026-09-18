---
title: "Priorità aerea target-specific via miglior loadout disponibile"
type: decision
tags: [architecture, dwm, air, priority, loadout, aircraft]
created: 2026-09-18
updated: 2026-09-18
status: accepted
affects: ["[[asset-air]]", "[[logic-decision]]"]
related: []
---

## Contesto

`Aircraft.air_combat_power()` è deliberatamente target-indipendente: è il valore generico usato in `Military.combat_power` per il confronto di forza complessivo. Ma quando `Region._calc_air_priority` calcola la priorità di una base aerea che attacca un bersaglio *specifico*, usare solo quel valore generico ignora un'informazione reale e già disponibile nel codice: `Aircraft_Data.combat_score_target_effectiveness()` (a differenza di `combat_score()`) sa valutare quanto un loadout specifico è efficace contro un tipo/dimensione di bersaglio particolare. Mancava però il collegamento fra "quali loadout ha davvero a disposizione questa base" e questo scoring, e mancava un ponte fra il profilo aggregato di un bersaglio (asset visti/reali) e le liste `(target_type, target_dimension)` che quella funzione si aspetta.

Durante l'analisi sono stati trovati e corretti due bug bloccanti indipendenti: `Military.get_military_category()` ritornava sempre `"Naval_Base"` (parentesi mancanti su `is_Air_Base`/`is_Ground_Base`/`is_Naval_Base`, tre `if` semplici in cui l'ultimo vinceva sempre) — rompeva la ricerca della force in `_calculate_priority`/`_representative_combat_power` per ogni blocco terrestre/aereo dalla Fase 0 del [[combat-power-priority-redesign]] in poi; e `Context.TARGET_CLASSIFICATION` aveva `dict_keys(...)` non espanso per 7 classificazioni, mai matchabili.

## Decisione

Implementato un meccanismo a più livelli che modifica la priorità di attacco aereo con un **fattore moltiplicativo di affinità**, non una sostituzione del punteggio base:

1. **Profilo del bersaglio** (`TargetProfile = Dict[classificazione, Dict[dimensione, count]]`): due produttori nello stesso formato — `target_profile_from_block` (ground-truth, dagli asset reali del blocco) e `target_profile_from_report` (dal report di ricognizione, alias di `get_target_report`) — pensati per essere intercambiabili senza toccare i consumatori.
2. **Distribuzione pesata dei pesi** (`profile_to_weapon_distribution`): converte il profilo in `{classificazione: {perc_type, perc_dimension}}`, con ogni classe/dimensione presente nel profilo che contribuisce proporzionalmente al proprio peso reale — sostituisce un primo design a soglia di copertura (`coverage=0.85`, scartato) che avrebbe escluso arbitrariamente la coda lunga della composizione.
3. **Miglior loadout contro un bersaglio** (`Aircraft_Data.best_loadout_against_target`/`combat_aggregate_against_target`): analogo di `combat_aggregate()` ma con `max` sui task invece di somma — contro un bersaglio specifico conta il singolo modo migliore per colpirlo, non quanti modi esistono in generale.
4. **Disponibilità del loadout — 3 filtri in cascata**, ciascuno un no-op se il proprio argomento è `None`: compatibilità per anno (`loadout_year_compatibility`, preesistente), dottrina per lato (`Context.LOADOUT_DOCTRINE`/`get_doctrine_loadouts`, nuovo, spedito vuoto — nessuna regola reale ancora inserita), scorte (`Military.weapons_availability`, nuovo stato di munizioni discrete, deliberatamente separato da `Resource_Manager.warehouse` che modella risorse continue fungibili).
5. **`Region._target_affinity`** (`@lru_cache`, ora spostata in `Tactical_Evaluation.target_affinity` dal [[region-tactical-strategic-refactor]]): ritorna `1.0` (neutro) su bersaglio amico/ramo difesa, profilo vuoto/non classificabile, o nessun loadout disponibile; altrimenti calcola, per ogni modello di aeromobile presente nel blocco (pesato per conteggio), il rapporto fra lo score target-specific e lo score generico di riferimento, e clippa il risultato a `[0.25, 2.0]`. Applicato solo sul ramo di attacco (`block.side != target_block.side`) — il default `1.0` garantisce che `_calc_surface_priority` e il ramo difesa restino bit-identici (verificato con un test di regressione dedicato).

**Correzione del 2026-09-14 — deduplicazione dei produttori**: `_target_profile_from_block` reimplementava la stessa regola di classificazione asset→(classificazione, dimensione) già presente in `Block.get_recognition_report`. Estratta una funzione condivisa `Context.classify_asset_dimension(asset, valid_asset_types=None)`, ora unica fonte di verità, usata sia da `Block.get_recognition_report` sia da `Region._target_profile_from_block` (~30 righe duplicate rimosse da ciascuno). Scartata l'alternativa (far chiamare a `_target_profile_from_block` `get_recognition_report(efficiency=1.0)` e riusare `get_target_report`) perché avrebbe invocato un effetto collaterale (`self.state.update()`) solo per una query, e perché `calcProbability(1.0)` non è garantito matematicamente `True`, il che avrebbe minato la purezza richiesta dalla cache di `_target_profile_from_block`.

**Correzione del 2026-09-14 — fix no-visibility su `get_target_report`**: `Region.get_target_report` controllava solo se il dict `operative` fosse falsy/vuoto, ma `Block.get_recognition_report` popola sempre le chiavi scheletro `asset_type`/`dimensione` a zero per ogni asset reale, indipendentemente dal fatto che il gate probabilistico di rilevamento sia passato — quindi un report "non rilevato" produceva un dict non vuoto con conteggi tutti a zero, interpretato erroneamente come "il bersaglio ha zero asset di questo tipo" invece di "non lo sappiamo". Corretto controllando il conteggio grezzo totale (sommato prima del raggruppamento in classificazioni) e ritornando `None` quando è zero — il caso distinto e preesistente "asset reali non-zero ma non classificabili" continua correttamente a ritornare `{}`.

## Motivazione

- **Moltiplicatore, non sostituzione**: il rapporto `target_cp / combat_power` in `_calculate_priority` è omogeneo (stessa scala, stesso clip `[0.1, 10.0]`); sostituire il numeratore con un valore di `combat_score_target_effectiveness` (scala diversa, non normalizzata) avrebbe rotto il rapporto. Un fattore di affinità dimensionless applicato solo al ramo di attacco preserva la scala esistente.
- Riuso del precedente reale già presente in `Air_Resources_Assigner.get_aircraft_mission` (liste, non distribuzione pesata bypassando `combat_score_eval`) come punto di partenza, poi migliorato con la variante a distribuzione per non perdere le componenti radar/TVD/avionica/velocità dello scoring.
- Separazione esplicita fra `weapons_availability` (munizioni, stato discreto nuovo) e `Payload`/`warehouse` (risorse continue) — modellano concetti diversi, unificarli avrebbe forzato una semantica innaturale.

## Conseguenze

- Feature completa e committata (`ed4d74d5` per gli item 4-8; `b38bab1f` per i due bug bloccanti preliminari; `6ab1e6dc` per l'unificazione del vocabolario di dimensione).
- `Context.LOADOUT_DOCTRINE` spedito vuoto (`{}`) — il filtro di dottrina esiste ed è testato ma non contiene ancora regole reali.
- **Deferito indefinitamente, non un gap temporaneo**: la propagazione di `route_length`/`route_speed` reali in `combat_score_target_effectiveness` (oggi sempre `0.0`/`1.0` di default, il range gate è di fatto disattivato) — l'utente ha chiarito che oggi e per il prevedibile futuro la priorità è guidata solo da velocità e distanza-al-bersaglio (`time_to_intercept`), e la gittata dell'arma non entra nel calcolo per scelta, non per dimenticanza.
- Bug pre-esistente non toccato, segnalato: `get_list_of_aircrafts`/una chiamata a `loadout_target_effectiveness_by_distribuition` con un nome di metodo che non esiste, indipendente da questa feature.
- Suite passata da 2332 (dopo i 2 fix preliminari) a 2465 test OK/5 skipped a fine sessione (2026-09-14), includendo anche il fix no-visibility e la deduplicazione.

## Fonti

- [[project_air_priority_target_specific_loadout]] (memoria di origine)
