---
title: "Context — Stato Operativo e Persistenza"
type: project-module
tags: [package-python, context, region, campaign-state, dottrina, combat-power, c2]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Context/Region.py, Code/Dynamic_War_Manager/Source/Context/Campaign_State.py, Code/Dynamic_War_Manager/Source/Context/Target_Status_History.py, Code/Dynamic_War_Manager/Source/Context/Doctrine.py, Code/Dynamic_War_Manager/Source/Context/Combat_Power_Estimation.py, Code/Dynamic_War_Manager/Source/Context/Coalition.py, Code/Dynamic_War_Manager/Source/Context/Rinomina_Campaign_State.py]
related_decisions: ["[[region-tactical-strategic-refactor]]", "[[c2-hierarchy-design]]", "[[combat-power-priority-redesign]]"]
related: ["[[context-foundation]]", "[[logic-decision]]", "[[command]]"]
---

## Scopo

Il sottosistema `Context` (cartella `Code/Dynamic_War_Manager/Source/Context/`) rappresenta lo
stato operativo dinamico della campagna: la classe `Region` modella un'area geografica con i suoi
blocchi (`Block`) e le rotte (`Route`) che li collegano, e orchestra i cicli di
aggiornamento priorità/produzione. `Campaign_State` e `Target_Status_History` sono due meccanismi
di persistenza/storicizzazione complementari: il primo salva lo **stato interno completo e
mutabile** degli oggetti di gioco (per poterlo ripristinare), il secondo salva lo stato **come lo
vedrebbe un ricognitore nemico** (report di riconoscimento, per analisi strategiche/tattiche
post-missione). Il modulo include anche due file non collegati al normale flusso applicativo
(`Coalition.py`, orfano e non compilabile, e `Rinomina_Campaign_State.py`, riservato per riuso
futuro) documentati a parte più sotto.

**Nota sullo stato di questa pagina**: sostituisce l'audit `Analysis/Modules/05_Context_State.md`
(2026-08-16), ormai stale su più punti chiave. Nell'ultimo mese `Region.py` è stato oggetto di un
refactoring strategico/tattico in 8 fasi (v. [[region-tactical-strategic-refactor]]) che ha
estratto **16 funzioni** in due nuovi moduli `Logic/Tactical_Analysis.py` e
`Logic/Tactical_Evaluation.py`, più un nuovo `Context/Doctrine.py` per la configurazione di
dottrina — `Region.py` è sceso da 1279 (all'audit) a **923 righe**. In parallelo, la Fase 2 del
redesign combat-power/priorità ha aggiunto un intero nuovo modulo, `Combat_Power_Estimation.py`
(stima fog-of-war), e una prima fase del design C2 a due livelli ha reso la dottrina di targeting
per-side invece che per-Region. Ogni affermazione sotto è stata riverificata contro il sorgente
attuale, non copiata dal vecchio documento.

## File inclusi

| File | Righe | Classi/contenuto principali |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Context/Region.py` | 923 | `Region`, `BlockItem` (dataclass), `RegionParams` (dataclass, ancora inutilizzata), `BlockCategory` (Enum) |
| `Code/Dynamic_War_Manager/Source/Context/Campaign_State.py` | 725 | `CampaignState` |
| `Code/Dynamic_War_Manager/Source/Context/Target_Status_History.py` | 298 | `TargetStatusHistory` |
| `Code/Dynamic_War_Manager/Source/Context/Doctrine.py` | 57 | **NUOVO** — `DEFAULT_WEIGHT_PRIORITY_TARGET`, `validate_weight_priority_target` |
| `Code/Dynamic_War_Manager/Source/Context/Combat_Power_Estimation.py` | 210 | **NUOVO** — stima combat power fog-of-war |
| `Code/Dynamic_War_Manager/Source/Context/Coalition.py` | 88 | `Coalition` — **orfano, non compilabile, marcato per cancellazione (non ancora rimosso)** |
| `Code/Dynamic_War_Manager/Source/Context/Rinomina_Campaign_State.py` | 140 (~44 di codice) | `Campaign_State` (vecchia versione) — **riservato per riuso futuro, NON toccare** |

Moduli correlati fuori da questa cartella ma parte dello stesso refactoring (documentazione
completa in [[logic-decision]], qui solo cross-reference):
`Code/Dynamic_War_Manager/Source/Logic/Tactical_Analysis.py` (281 righe, 8 funzioni pure di
analisi — `get_target_report`, `target_profile_from_block`, `build_recon_cp_snapshot`, ecc.) e
`Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py` (937 righe, include le 7 funzioni
di scoring estratte da `Region` — `select_weight`, `calculate_priority`, `calc_surface_priority`,
`calc_air_priority`, `calc_attack_priority`, `calc_defense_priority`, `target_affinity` — più le
funzioni di valutazione tattica preesistenti al refactoring).

## Classi e funzioni principali

### `Region` (Region.py)

Dal refactoring in 8 fasi (COMPLETO, v. [[region-tactical-strategic-refactor]]), `Region` gestisce
**solo stato di istanza e orchestrazione** (blocchi, route, cicli di produzione/priorità); tutta
l'analisi strategico-tattica (target profiling, stima combat power, scoring di priorità
attacco/difesa) vive fuori, in `Logic.Tactical_Analysis` (leggero, nessuna cache, importato
eager) e `Logic.Tactical_Evaluation` (pesante — tira dentro `Aircraft_Data`+`skfuzzy` — importato
**lazy** dentro `update_military_priorities`, per non gravare sull'import di `Region.py` per i
chiamanti che non calcolano mai una priorità militare).

- `__init__(name, limes=None, description=None, blocks=None, routes=None)` — valida i parametri
  con `_validate_init_params`.
- **Dottrina di targeting per-side (NUOVO, TASK 1 del design C2)**: `_attack_weight` e
  `_weight_priority_target` sono ora `Dict[str, ...]` chiavati `'Blue'`/`'Red'` (non più uno
  scalare/dict unico per Region). Le vecchie property dirette `attack_weight`/
  `weight_priority_target` sono state **rimosse** (una property non può accettare un parametro
  `side`) e sostituite da coppie get/set esplicite: `get_attack_weight(side)`/
  `set_attack_weight(side, value)`, `get_weight_priority_target(side)`/
  `set_weight_priority_target(side, value)`, con guard `_validate_belligerent_side(side)`
  (accetta solo `'Blue'`/`'Red'`, non `'Neutral'`). Nessuno shim di retrocompatibilità: non
  esistevano snapshot in formato scalare da migrare. `set_weight_priority_target` valida tramite
  `Doctrine.validate_weight_priority_target`.
- **Gestione blocchi**: `add_block(block, priority=0.0)`, `remove_block(block_id)`,
  `get_block_by_id(block_id)`, `get_blocks_by_criteria(side=None, category=None,
  block_class=None, mil_category=None)` (`@lru_cache(maxsize=128)`, ora con filtro aggiuntivo
  `mil_category` — valida contro `Context.MILITARY_CATEGORY`), `get_sorted_priority_blocks`,
  `get_normalized_priority_blocks`, e **`get_priority_lists_by_mil_category(side, sort_by=
  "highest")` (NUOVO)** — divide la lista di priorità di un side in una lista ordinata per ogni
  `Military.mil_category` effettivamente presente (categorie senza blocchi omesse), costruita
  sopra `get_sorted_priority_blocks`.
- **Gestione rotte**: `add_route`, `get_route` (`@lru_cache`), `get_shortest_route`,
  `get_safest_route`, `get_shortest_and_safest_route` — invariati.
- **Calcoli strategici** (`@lru_cache(maxsize=3)`, restano tutti in `Region` per decisione
  esplicita del refactoring: scrivono `block_item.priority` o iterano `self._blocks`, sono
  operazioni sullo stato della regione, non valutazioni pure): `calc_strategic_logistic_center`,
  `calc_combat_power_center`, `calc_total_warehouse`, `calc_total_production`,
  `calc_production_values`.
- **Aggiornamento priorità**: `update_logistic_priorities(side)`,
  **`update_military_priorities(side, use_recon=False)`** (v. sotto per il dettaglio fog-of-war),
  `run_resource_management_cycle(side)`.
- **Metriche aggregate**, sopra l'helper comune `_get_region_average_metric` (`getattr` +
  `callable()`, silenzioso se il blocco non espone il metodo): `get_block_morale`,
  `get_region_morale(side)`, `get_region_recon_efficiency(side)`,
  `get_region_resource_efficiency(side)`, `get_c2_efficiency(side)`.
  **`get_region_intelligence_efficiency` è stata RIMOSSA** rispetto all'audit precedente (che la
  segnalava come "funzionalmente morta", sempre `0.0` perché `Military.intelligence()` non è mai
  stato implementato a favore di `get_c2_efficiency()`) — il metodo morto e il test drift
  associato non esistono più nel codice attuale.
- `get_recon_reports(side)` — C2 usato è quello dell'**osservatore** (`Utility.enemySide(side)`,
  fix della Fase 1 del piano fog-of-war — prima usava erroneamente il C2 del lato osservato).
- `get_meteorological_reports(side, date, time)` — **implementato 2026-09-18** (TASK 2 / Fase A
  del design C2, v. [[c2-hierarchy-design]]): firma cresciuta con `date`/`time` (nessun chiamante
  esisteva, nessun problema di retrocompatibilità), delega a `Logic.Meteo_Analysis.get_meteo_conditions`
  (placeholder deterministico, non `random`) e restituisce `[condizioni]` — una lista di un solo
  elemento per simmetria con `get_recon_reports`, dato che il meteo non varia per blocco.
- `limes` — **property pubblica, sola lettura, implementata 2026-09-18** (TASK 2): restituisce una
  copia difensiva di `self._limes`. Nessun setter (nessun caso d'uso esistente per la mutazione
  dopo la costruzione).
- `build_info_report(side, date, time) -> RegionInfoReport` — **nuovo 2026-09-18** (TASK 2): puro
  orchestratore che assembla lo snapshot "(*) INFO" di pag. 3 del PDF sorgente da questi stessi
  metodi già testati. Dataclass `RegionInfoReport` e dettagli in [[command]].

**`update_military_priorities(side, use_recon=False)` — il cuore del redesign fog-of-war
(Fase 2 completa, v. [[combat-power-priority-redesign]]):**

- Guard `side == 'Neutral'`: log warning e `return` immediato, senza toccare blocchi — chiude un
  bug preesistente per cui un blocco Neutral avrebbe calcolato una "priorità di attacco" verso se
  stesso (`enemySide('Neutral')` degenera in `'Neutral'`).
- Se `use_recon=True`: `recon_reports = self.get_recon_reports(enemySide(side))` (una sola volta
  per sweep, mai per singola coppia blocco/bersaglio) poi
  `self._recon_cp_snapshot = Tactical_Analysis.build_recon_cp_snapshot(recon_reports)`, dentro un
  blocco `try/finally` che riporta `self._recon_cp_snapshot = None` a fine sweep (anche in caso di
  eccezione) — lo snapshot è valido **solo** dentro lo sweep che lo ha costruito.
- Per ogni blocco amico: `Tactical_Evaluation.calc_attack_priority(military_block, enemy_items,
  weight_priority_target[side], self.get_shortest_route, recon_cp_snapshot=...)` e
  `calc_defense_priority(...)` (quest'ultima **mai** riceve `recon_cp_snapshot`: il ramo difesa
  opera solo su alleati, sempre ground-truth). `overall_priority = attack*attack_weight[side] +
  defense*(1-attack_weight[side])`.
- `use_recon` di default `False` ovunque nel codice — **nessun chiamante di produzione lo attiva
  ancora**; attivarlo nel ciclo di simulazione reale resta una decisione applicativa separata dal
  piano già completato.
- No-visibility → bassa priorità: un `block_id` osservato ma assente dallo snapshot recon vale
  `target_cp = 0.0` (non "ground-truth di ripiego"), che si aggancia al gate esistente per dare
  bassa priorità — coerente con la policy esplicita dell'utente
  (v. `.claude/memory/feedback_no_visibility_low_priority.md`): l'assenza di ricognizione non è
  un segnale di alto rischio, è evidenza che le risorse di ricognizione sono state spese altrove.

**Comportamenti sorprendenti / bug ancora presenti (riverificati sul sorgente attuale, NON
risolti dal refactoring — fuori dal suo perimetro):**

- **Bug di mutazione della cache LRU** (`get_blocks_by_criteria` + `get_sorted_priority_blocks`,
  righe ~328-329): `get_sorted_priority_blocks` chiama `blocks =
  self.get_blocks_by_criteria(...)` (risultato cachato) e poi fa `blocks.sort(...)` **in-place**
  sulla stessa lista — muta permanentemente il contenuto della cache. Confermato ancora presente
  riga per riga, identico al comportamento documentato nell'audit 2026-08-16.
- **`get_route` — docstring disallineata**: dichiara di restituire un singolo `Route` ma
  restituisce sempre una `List[Route]` (o `None`) — ancora vero.
- **`RegionParams` — dataclass ancora inutilizzata** in tutto il codebase (verificato con grep,
  0 riferimenti esterni) — non toccata dal refactoring.
- **`get_normalized_priority_blocks` — nessun guard contro `delta == 0`** (tutti i blocchi con
  la stessa priorità) → `ZeroDivisionError` non gestita. Ancora presente.

### `CampaignState` (Campaign_State.py)

Contenitore di snapshot completi dello stato di gioco (Region, Block, State, Resource_Manager,
Asset, Route), indicizzato per **`mission_id`** (chiave top-level, invariata — v. nota sotto).

- Schema aggiornato per riflettere la dottrina per-side (TASK 1 del design C2, verificato nel
  sorgente): la sezione region dello snapshot ora contiene `"attack_weight": {"Blue": float,
  "Red": float}` e `"weight_priority_target": {"Blue": dict, "Red": dict}` (prima erano scalari
  unici). `_serialize_region` legge `getattr(region, '_attack_weight', {})` e
  `getattr(region, '_weight_priority_target', {})` — dizionari interi, non più un valore scalare.
  `restore()` itera `attack_weight_snap.items()` e chiama `region.set_attack_weight(side,
  float(value))` per ogni side presente nello snapshot (idem per `weight_priority_target` via
  `set_weight_priority_target`), con logging di warning (non eccezione) se il restore fallisce
  per un side. **Nessuno shim di retrocompatibilità** per snapshot salvati in formato scalare
  pre-TASK-1 — nessuno esisteva in produzione al momento della migrazione.
- **Write API**: `add_campaign_snapshot(mission_id, date, time, regions: List)`,
  `add_region_snapshot`, `add_block_snapshot` — invariate.
- **Read API**: `missions`, `get_mission`, `get_region_snapshot`, `get_block_snapshot`,
  `get_block_history`, `get_field_trend`, `get_asset_history` — invariate.
- **Restore API**: `restore(mission_id, regions: List)` — applica lo snapshot a oggetti live;
  oggetti presenti nello snapshot ma assenti nel grafo live vengono loggati come warning e saltati.
- **Persistenza**: `save(path)` (JSON UTF-8), `CampaignState.load(path)` (classmethod) — invariate.
- Suite di test riverificata: `Test_Campaign_State.py` — **78 test, tutti OK** (`_RegionStub` e i
  test interessati sono stati aggiornati per la dottrina per-side).

### `TargetStatusHistory` (Target_Status_History.py)

Invariato dall'audit precedente. Storicizza i `recognition_report` (vista "bersaglio militare")
per ogni blocco, indicizzati per `mission_id`/regione. API simmetrica a `CampaignState` ma senza
Restore API. **44 test, tutti OK** (riverificato). Ancora usa `mission_id` come unica chiave
top-level (v. nota sotto), coerente con `CampaignState`.

### `Doctrine.py` — NUOVO (non esiste nell'audit 2026-08-16)

Modulo nato dalla Fase 1 del refactoring tattico/strategico, per estrarre la configurazione di
dottrina di targeting da `Region.py` (che la usava, non la possedeva concettualmente) e da
`Context.py` (già molto esteso). Contenuto:

- `DEFAULT_WEIGHT_PRIORITY_TARGET: Dict` — pesi di default per la selezione del bersaglio nel
  calcolo delle priorità militari, strutturati `[block_category]["attack"|"defense"][target_category]
  → peso [0,1]`, per `Ground_Base`/`Air_Base`/`Naval_Base`. Usato da
  `Logic.Tactical_Evaluation.select_weight` e come valore iniziale di
  `Region._weight_priority_target[side]` (una copia indipendente per `'Blue'` e per `'Red'`).
- `validate_weight_priority_target(value)` — valida la struttura (dict, chiavi `attack`/`defense`
  obbligatorie e non vuote, pesi numerici in `[0,1]`); non più un metodo `Region._validate_...`,
  ora funzione standalone chiamata direttamente dal setter `set_weight_priority_target`.
- Test dedicato `Test_Doctrine.py` — **7 test, tutti OK**.

### `Combat_Power_Estimation.py` — NUOVO (non esiste nell'audit 2026-08-16)

Modulo standalone (Fase 3 del piano fog-of-war, v. [[combat-power-priority-redesign]]), non
importato da `Region.py` a livello di modulo per Region stesso ma consumato da
`Logic.Tactical_Analysis`/`Logic.Tactical_Evaluation` nella catena `use_recon`. Stima la combat
power di un bersaglio osservato via ricognizione, di cui si conosce solo
`asset_summary['operative']` (`{asset_type: {dimensione: conteggio}}`), applicando ai conteggi la
**mediana del punteggio di combattimento reale** dei modelli del registro che ricadono in ciascun
bucket `(asset_type, dimensione)`, con catena di fallback a 3 livelli quando il bucket ha pochi
campioni:

1. bucket `(asset_type, dimensione)` se ha almeno `min_samples=3` campioni;
2. altrimenti bucket `asset_type`-solo (tutte le dimensioni);
3. altrimenti mediana globale della force, **escludendo** gli `asset_type` senza alcuna efficacia
   in nessuna azione (SAM/AAA/EWR sul ground — popolazione strutturalmente diversa, combat power
   identicamente zero per costruzione via `Context.combat_power_from_score`);
4. altrimenti `0.0`.

API pubblica: `estimated_model_score(asset_type, dimension, force, side=None, min_samples=3)`,
`build_estimated_combat_power_table(force, action, *, side=None, efficiency=1.0, min_samples=3)`
(diagnostica/test), `estimate_combat_power_from_asset_summary(operative, force, action, *,
side=None, efficiency=1.0, min_samples=3)` (il vero punto d'ingresso, usato da
`Tactical_Analysis`/`Region.update_military_priorities` via lo snapshot recon). Usa
**deliberatamente** la stessa formula del ground-truth (`Context.combat_power_from_score`),
**mai** `Context.TARGET_CLASSIFICATION`/`get_target_classification` (vocabolario per una domanda
diversa — "con quale arma attaccare", non "quanto vale in combattimento"). Import di
`Vehicle_Data`/`Ship_Data`/`Aircraft_Data` sono lazy (dentro le funzioni), per lo stesso motivo di
performance/disaccoppiamento del refactoring tattico. Filtro `side`/`users`: **inclusivo** (un
modello senza `users` è sempre incluso, a differenza del pattern usato altrove in
`Aircraft_Data.py`). Test dedicato `Test_Combat_Power_Estimation.py` — **20 test, tutti OK**.

## Cross-reference: Logic/Tactical_Analysis.py e Logic/Tactical_Evaluation.py

Le 16 funzioni tattiche estratte da `Region.py` (documentazione completa in [[logic-decision]],
pagina scritta in parallelo — qui solo il collegamento):

- **`Tactical_Analysis.py`** (analisi, produce fatti non punteggi, nessuna `@lru_cache`, nessuna
  dipendenza da `self`): `estimate_target_combat_power`, `build_recon_cp_snapshot`,
  `get_target_report`, `profile_to_weapon_distribution`, `target_profile_from_report`,
  `representative_combat_power`, `target_profile_from_block`, `operative_aircraft_by_model`.
- **`Tactical_Evaluation.py`** (valutazione, ritorna un punteggio float, importato lazy da
  `Region` per il costo di `Aircraft_Data`+`skfuzzy`): `target_affinity`, `select_weight`,
  `calculate_priority`, `calc_surface_priority`, `calc_air_priority`, `calc_attack_priority`,
  `calc_defense_priority` — più le funzioni di valutazione tattica preesistenti al refactoring
  (`evaluateGroundTacticalAction`, `calcRecoAccuracy`, `calcFightResult`,
  `evaluateCombatSuperiority`, `evaluateCriticalityGroundEnemy`,
  `evaluateGroundRouteDangerLevel`).

**Decisione deliberata**: nessuna `@lru_cache` residua su nessuna delle 16 funzioni spostate
(erano 7/16 nel codice pre-refactoring) — precondizione esplicita per un futuro pianificatore
"what-if" che valuti scenari ipotetici senza contaminazione di cache condivisa fra istanze/scenari
diversi.

## Dipendenze

- **Region.py** dipende da: `Context.Context`, `Context.Doctrine`, `Logic.Tactical_Analysis`
  (eager), `Logic.Tactical_Evaluation` (**lazy**, solo dentro `update_military_priorities`),
  `Utility.Utility`, `Block.Block`/`Military`/`Production`/`Storage`/`Transport`/`Urban`,
  `DataType.Limes`/`Route`/`Payload`, più `sympy.Point2D`.
- **Campaign_State.py** e **Target_Status_History.py** restano deliberatamente "leggeri":
  `json`, `pathlib`, `datetime`, `typing`, `Utility.LoggerClass` — accedono ai dati via `getattr`
  duck-typing, testabili con stub, senza il problema di import circolare.
- **Doctrine.py**: solo `typing` — nessuna dipendenza applicativa.
- **Combat_Power_Estimation.py**: `Context.Context` a livello di modulo; `Vehicle_Data`/
  `Ship_Data`/`Aircraft_Data` lazy dentro le funzioni.
- Nessuno dei file "vivi" usa `Coalition.py` o `Rinomina_Campaign_State.py`.

## Stato attuale

### Completezza

- **Region.py**: completo per le operazioni core dopo il refactoring; l'analisi/scoring vive
  fuori (v. sopra). TASK 2 del design C2 (`get_meteorological_reports`, `limes` pubblico,
  `build_info_report`) è **completato** (2026-09-18, v. sopra e [[c2-hierarchy-design]]).
- **Campaign_State.py**: completo per lo scopo dichiarato, aggiornato per la dottrina per-side.
- **Target_Status_History.py**: completo per lo scopo dichiarato (nessun restore, per design).
- **Doctrine.py / Combat_Power_Estimation.py**: completi per lo scopo per cui sono stati costruiti
  in questa fase (configurazione di dottrina; stima fog-of-war). Nessun chiamante di produzione
  attiva ancora `use_recon=True`.

### Copertura test reale (eseguita in questa sessione)

| Suite | Risultato |
|---|---|
| `Test_Region.py` | **81 test, OK** |
| `Test_Campaign_State.py` | **78 test, OK** |
| `Test_Target_Status_History.py` | **44 test, OK** |
| `Test_Doctrine.py` | **7 test, OK** |
| `Test_Combat_Power_Estimation.py` | **20 test, OK** |
| `Test_Tactical_Analysis.py` (Logic/, cross-reference) | **64 test, OK** |
| `Test_Tactical_Evaluation.py` (Logic/, cross-reference) | **27 test, OK** |

Tutte le suite verificate sono verdi; nessun ERROR/FAILURE residuo (a differenza dell'audit
2026-08-16, che segnalava 1 ERROR in `Test_Region.py` per `get_region_intelligence_efficiency` —
quel metodo e il test corrispondente sono stati rimossi, non solo corretti).

## File orfani/riservati

### `Coalition.py` — orfano, marcato per cancellazione (non ancora rimosso)

Riverificato riga per riga sul sorgente attuale: **identico** ai bug già documentati
nell'audit 2026-08-16, nessuna modifica nell'ultimo mese. Usa import pre-refactoring incompatibili
con l'attuale struttura a sottocartelle (`from Dynamic_War_Manager.Source.Block import Block`,
manca sia `Code.` sia le sottocartelle `DataType`/`Context`/`Block`) — confermato con esecuzione
diretta che il modulo **non si importa** (`ModuleNotFoundError` sul primo import). Contiene inoltre
bug logici indipendenti dagli import: `regions()` assegna `regions_dict` ma fa `return
region_dict` (nome mai definito, `NameError` se mai eseguito); `getTacticalReport()` usa
`self.getBlocks`/`self.side` mai definiti sulla classe (solo `_side`).

**Novità rispetto all'audit**: la memoria di progetto `.claude/memory/project_c2_hierarchy_design.md`
registra che l'utente ha **esplicitamente approvato la cancellazione** di questo file ("Delete
Context/Coalition.py (doesn't compile, unused) — no salvage needed", 2026-09-17) come parte del
cleanup collegato al design C2 a due livelli — **ma il file è ancora presente nel repository**,
la cancellazione non è stata ancora eseguita. Stato corretto da riflettere: **marcato per
cancellazione, non ancora rimosso** (non più "probabile relitto, nessuna proposta di
cancellazione" come diceva l'audit 2026-08-16 — la decisione è stata presa, manca solo
l'esecuzione).

### `Rinomina_Campaign_State.py` — riservato per riuso futuro, NON toccare

L'utente ha esplicitamente richiesto di **non cancellarlo**: intende riutilizzarlo in futuro
rinominandolo (v. `.claude/memory/project_rinomina_campaign_state.md`). Nessuna proposta di
cancellazione qui né altrove.

Contiene una vecchia classe `Campaign_State` (nome diverso, senza CamelCase separato, dall'attuale
`CampaignState`), con `_last_mission`/`_asset_availability`/`_global_success_mission_ratio`/
`_global_damaged_asset_ratio`/`_state` — solo `__init__` implementato, nessun metodo pubblico
oltre al costruttore. **Bug di import riverificato ancora presente**: riga 29 importa
`ASSET_AVAILABILITY` da `Initial_Context`, ma l'attributo reale ha underscore iniziale
(`_ASSET_AVAILABILITY`) — confermato con esecuzione diretta:
```
ImportError: cannot import name 'ASSET_AVAILABILITY' from '...Initial_Context'
(Did you mean: '_ASSET_AVAILABILITY'?)
```
Il fix del bug `asea.FAST_ATTACK` in `Initial_Context.py` (v. [[context-foundation]]) non ha risolto questo secondo bug indipendente — il file resta non importabile as-is.
Coerente con l'istruzione della memoria di progetto: non è "codice morto da ripulire", è materiale
riservato per un riuso futuro non ancora pianificato in dettaglio.

## Problemi aperti

- **Bug di mutazione della cache LRU in `get_sorted_priority_blocks`** — non risolto dal
  refactoring (fuori perimetro), v. sopra.
- **`get_route` — docstring disallineata dal comportamento reale** — non risolto.
- **`RegionParams` inutilizzata** — non risolta, non toccata dal refactoring.
- **`get_normalized_priority_blocks` — nessun guard `delta == 0`** — non risolto.
- **Rinomina della chiave `mission_id` → `session_id` in `Campaign_State`/`Target_Status_History`
  — CONFERMATA ma NON implementata**: la memoria di progetto `project_c2_hierarchy_design.md`
  registra che `mission_id` (oggi l'unica chiave top-level di `CampaignState._state`) verrà
  rinominata in `session_id`, con `mission_id` ripristinato un livello più sotto per identificare
  le singole missioni (air/ground/sea) che il C2 di un side definisce dentro una sessione. **Questa
  rinomina non è ancora avvenuta nel codice**: sia `Campaign_State.py` sia
  `Target_Status_History.py` usano oggi `mission_id` come unica chiave top-level, ed è il
  comportamento corretto per quello che esiste attualmente (non c'è ancora un concetto di
  missione distinto da una sessione — solo lo snapshot "a forma di sessione"). La migrazione è
  esplicitamente rimandata a quando il pacchetto `Command/` (`Session.py`/
  `Session_Mission_Planner.py`) verrà costruito, non prima — non va eseguito un find-replace ora.
- **`Coalition.py`** — cancellazione approvata dall'utente ma non ancora eseguita (v. sopra).
- **TASK 2 del design C2 (Fase A) — completato 2026-09-18** (v. sopra e [[c2-hierarchy-design]]).

## Decisioni architetturali rilevanti

- [[region-tactical-strategic-refactor]] — l'origine di questa intera riorganizzazione: 16
  funzioni tattiche estratte da `Region.py` in `Logic.Tactical_Analysis`/`Logic.Tactical_Evaluation`,
  nuovo `Context/Doctrine.py`, rimozione totale delle `@lru_cache` dalle funzioni spostate (per
  precondizionare un futuro pianificatore what-if).
- [[c2-hierarchy-design]] — TASK 1 (dottrina di targeting per-side, `get_attack_weight(side)`/
  `set_attack_weight(side, value)` ecc., aggiornamento `Campaign_State`) e TASK 2 (`limes`
  pubblico, `get_meteorological_reports`, `build_info_report`/`RegionInfoReport` — v. [[command]])
  sono entrambi **fatti**; include anche la decisione confermata-ma-non-implementata sul rename
  `mission_id`→`session_id` e la decisione approvata (ma non eseguita) di cancellare `Coalition.py`.
- [[combat-power-priority-redesign]] — Fase 2 (fog-of-war): C2 fix in `get_recon_reports`,
  `use_recon` end-to-end in `Region.update_military_priorities`, nuovo
  `Context/Combat_Power_Estimation.py`, campo `users` reale su Vehicle/Ship per il filtro
  side-aware della stima.

## Note

- **`Rinomina_Campaign_State.py`** — riservato per riuso futuro su richiesta esplicita
  dell'utente; non proporne mai la cancellazione né trattarlo come materiale di pulizia.
- **Diff `Region.py` del 2026-09-10** (rimozione dead-code + comparsa dello stub
  `get_meteorological_reports`) fu inizialmente scambiato per una modifica non attribuita, poi
  confermato dall'utente come proprio autosave dell'editor in parallelo alla sessione — nessuna
  azione necessaria, solo commit (74065590). Riportato qui solo come nota storica sul modulo.
