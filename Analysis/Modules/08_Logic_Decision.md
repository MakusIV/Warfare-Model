# Logic — Decisione Tattica e Strategica

## Scopo

Il pacchetto `Code/Dynamic_War_Manager/Source/Logic/` dovrebbe ospitare la
logica decisionale del Dynamic War Manager: valutazione tattica (esito di
scontri, stato del fronte, pericolosità di una rotta), valutazione
strategica (priorità di obiettivi/zone, direttive di comando) e
orchestrazione dello scenario/missione (loop di ricognizione, pianificazione,
scrittura/lettura dati DCS). A valle di queste valutazioni,
`Air_Resources_Assigner.py` assegna concretamente le risorse aeree
disponibili (velivoli + loadout) alle missioni richieste.

Nella visione di progetto, il flusso naturale sarebbe:
`Scenario_Manager` (loop di comando/controllo) → `Strategical_Evaluation`
(priorità di obiettivi/zone a livello di side) → `Tactical_Evaluation`
(esito/criticità dello scontro a livello di singolo blocco) →
`Air_Resources_Assigner` (allocazione concreta di velivoli/loadout alle
missioni derivate). Come descritto in "Stato attuale" e "Problemi aperti",
oggi questo flusso non è cablato: i quattro moduli non si richiamano a
vicenda e tre di essi non sono nemmeno importabili.

## File inclusi

| File | Righe | Note |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py` | 1183 | ex `Military_Resources_Assigner.py` (rinominato); unico modulo del pacchetto con logica sostanzialmente completa e ben coperta da test (bloccati solo dall'import circolare esterno) |
| `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py` | 243 | contiene la classe `CommandControl` (non un "manager di scenario" nel senso stretto); quasi interamente stub/pseudocodice, non importabile |
| `Code/Dynamic_War_Manager/Source/Logic/Strategical_Evaluation.py` | 281 | funzioni pubbliche tutte stub (`pass`); contiene inoltre uno schizzo di design (`ConflictGraph`, `PrioritySystem`) che rompe l'import del modulo |
| `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py` | 591 | logica implementata e in buona parte funzionante (fuzzy logic + calcoli numerici), ma il modulo non è **importabile** a causa di un bug nell'istanza del `Logger` (vedi Bug noti) |

Altri file dello stesso pacchetto (`Air_Route_Manager.py`,
`Ground_Route_Manager.py`) non fanno parte dell'incarico e non sono
analizzati qui.

## Classi e funzioni principali

### `Air_Resources_Assigner.py`

Modulo con API pubblica e privata ben separate (`# Public API` / `# Private
helpers`), interamente basato su funzioni (nessuna classe).

**Costanti**
- `_DIRECTIVE_WEIGHTS: Dict[str, Tuple[float,float]]` — pesi (combat, costo) per le 5 direttive: `performance_high` (1.00, 0.00), `performance` (0.75, 0.25), `balanced` (0.50, 0.50), `economy` (0.25, 0.75), `economy_high` (0.10, 0.90).
- `_REFERENCE_COST_K: float = 303_000.0` — costante di normalizzazione del fattore costo (≈ costo medio caccia + loadout, in k$).

**API pubblica**
- `get_aircraft_mission(task, aircraft_availability, mission_requirements, target_data, max_aircraft_for_mission, max_missions, directive) -> Dict` — funzione centrale del modulo. Per ogni combinazione aereo/loadout in `aircraft_availability`: verifica esistenza del loadout, requisiti di missione (`_check_mission_requirements`), usabilità (`_usability_met`); calcola il numero di velivoli/missioni necessari per coprire `target_data` tramite `Aircraft_Loadouts.get_aircrafts_quantity`; se il numero di missioni eccede `max_missions` applica una riduzione proporzionale pesata per priorità (`_reduce_target_data`) con una correzione analitica a due passi (vedi commento righe 838-890) per compensare la non linearità introdotta dal peso di priorità; calcola lo score con `Aircraft_Data.combat_score_target_effectiveness` combinato al costo (`_compute_score`); ripartisce i risultati in `{'fully_compliant': [...], 'derated': [...]}`, ciascuna lista ordinata discendente per `score`. Ogni entry: `{'aircraft_model', 'loadout', 'score', 'aircraft_per_mission', 'missions_needed', 'derating_factor', 'total_cost'}`.
- `get_loadouts_availability(weapons_availability, loadouts_list) -> Dict` — dato l'inventario di armi disponibili, calcola quanti loadout completi sono effettivamente allestibili (fattore limitante = arma più scarsa), deduce le armi consumate da `weapons_availability` **in-place** e restituisce `{aircraft_model: {loadout_name: {'quantity', 'reduction_percentage'}}}`.
- `get_ground_mission_task_list(aircraft_availability, mission_requirements, target_data, max_aircraft_for_mission, max_missions, directive) -> Dict` — deriva da `target_data` una tabella di task aria-terra tramite `_create_ground_mission_task_table`, quindi invoca `get_aircraft_mission` una volta per tipo di target, restituendo `{target_type: {'task', 'priority', 'fully_compliant', 'derated'}}`.
- `get_air_mission_task_list(aircraft_availability, task, mission_requirements, target_data, max_aircraft_for_mission, max_missions, directive) -> Dict` — variante per missioni aria-aria (Intercept, Fighter_Sweep, CAP, Escort, Recon). Contiene un bug che la rende inutilizzabile per `CAP`/`Escort` (vedi Bug noti).
- `get_aircraft_availability_list(airbase_name, aircraft_category=None)` — **stub**, corpo `pass`; solo docstring/commenti che descrivono il formato atteso e riferimenti a funzioni non ancora esistenti (`get_airbase`, `airbase.get_asset_type_list`).

**Helper privati principali**
- `_extract_quantities`, `_extract_target_lists` — normalizzano `target_data` (formato `{type: {dim: {'quantity','priority'}}}`) rispettivamente in `{type:{dim:int}}` e in liste piatte `(types, dims)`.
- `_check_mission_requirements(loadout, mission_requirements) -> bool` — confronta velocità/quota/raggio di `loadout['cruise']`/`['attack']` con i requisiti; nota: la condizione su `altitude_max` (riga 146) è scritta come catena `>= req.get('altitude_max',0) <= lo.get('altitude_min', inf)`, ridondante/di dubbia leggibilità (comparazione a catena Python), da rivedere.
- `_usability_met(loadout_usability, required_usability) -> bool` — un requisito `True` deve essere soddisfatto dal loadout; requisiti `False` sono ignorati.
- `_compute_score(combat_score, aircraft_cost_M, loadout_cost_k, directive) -> float` — `score = combat_score * (ws + wc * _REFERENCE_COST_K / max(1, total_cost_k))`.
- `_reduce_target_data(target_data, reduction_ratio) -> Dict` — riduzione proporzionale delle quantità pesata per priorità (`multiplier = reduction_ratio + weight*(1-reduction_ratio)`); `reduction_ratio<=0` azzera tutto, `>=1` restituisce copia invariata.
- `_find_weapon_in_availability`, `_pylons_to_weapons_dict`, `_loadout_availability`, `_reduction_weapons_availability`, `_increase_weapons_availability` — gestione a basso livello dell'inventario armi (ricerca, conversione piloni→dict piatto, calcolo loadout allestibili, decremento/incremento scorte con validazione preventiva e rollback implicito se una singola arma non basta).
- `_count_target_dimension` — somma le quantità in un blocco `{dim: {'quantity':...}}`.
- `_create_ground_mission_task_table(target_data) -> Dict` — per ciascun tipo di target sceglie il task aria-terra (o aria-aria per `Aircraft`) associato alla dimensione a priorità massima, tramite `get_task_from_target` (da `Context.Context`) più casi speciali per `Aircraft` (→ `Escort`), `Ship` (→ `Anti_Ship`), `Air_Defense` (→ `SEAD`).

Dipende da `skfuzzy`/`numpy` solo per l'import (non risultano usati
direttamente nel modulo — `fuzz`/`ctrl`/`np` importati ma non referenziati
nel corpo delle funzioni elencate; possibile residuo di refactoring).

### `Scenario_Manager.py` — classe `CommandControl`

Nonostante il nome del file, il modulo definisce un'unica classe,
`CommandControl(side, regions, blocks)`, pensata come nodo di comando e
controllo per una fazione (Blue/Red). Stato interno `_state` con
sotto-dizionari `morale`, `trade_balance` (goods/food/energy/human resource
per HC/HS/HB/HR) e `military` — tutti vuoti, mai popolati da nessun metodo.

**Metodi implementati (CRUD elementare su liste)**
- `checkParam(side, regions, blocks)` — validazione tramite un metodo `checkListOfObjects` **mai definito nella classe** (bug, vedi sotto); usato sia dal costruttore sia dal setter `blocks`.
- Proprietà `blocks` (getter/setter).
- `addBlock`, `getLastBlock`, `getBlock`, `removeBlock` — CRUD su `self._blocks`; **bug**: `addBlock` fa `self._events.append(block)` invece di `self._blocks.append(block)` (attributo `_events` mai definito altrove).
- `addRegion`, `getLastRegion`, `getRegion`, `removeRegion` — CRUD su `self._regions`; usano `isinstance(region, Region)` ma la classe `Region` **non è importata** nel modulo (bug bloccante, vedi sotto).
- `executeRecoinnassanceRequest(self)` — abbozzo di loop "richiedi ricognizione a ogni blocco militare di ogni lato": itera `Context.SIDE` e `self.regions[side]` (ma `self.regions` non esiste come attributo/proprietà — solo `self.blocks`/`self._regions` sono definiti; ulteriore bug), chiama `block.getRecon()` (metodo non presente nelle classi `Block`/`Military` viste in altri moduli del progetto).

**Metodi non implementati (solo `pass` o commenti)**
- Blocco di commenti "reading and loading DCS data", "evaluate mission
  result", "execute simulation for virtual mission result", "save mission
  result" — tutti seguiti da un singolo `pass` a livello di modulo (non
  dentro metodi: sono istruzioni no-op fuori da qualunque funzione,
  sintatticamente valide ma semanticamente inerti).
- Un lunghissimo docstring/commento (righe 159-235) descrive l'intento di un
  "evaluate strategic directive" ispirato al "C2 Planner" del modello
  Theater-Level Campaign (SAGE — Sequential Analytic Game Evaluation) e a
  un grafo di route con nodi/archi per il movimento — **puro materiale di
  design, nessun codice**.
- "execute strategical and tactical evaluation and planning" e "writing DCS
  data to lua table" — idem, solo commenti + `pass`.

In sintesi: `CommandControl` è uno scheletro con qualche metodo di
gestione lista funzionante ma non testato, alcuni bug che ne impediscono
l'uso reale, e nessuna delle funzionalità di comando/controllo descritte nei
commenti è implementata.

### `Strategical_Evaluation.py`

Nessuna classe funzionante. Contiene:

- **Blocco di design non funzionante** (righe 37-108): classi
  `ConflictGraph` (grafo di blocchi con DFS per `calculate_combat_power`) e
  `PrioritySystem` (genera `Report` di azione attack/defend tra blocchi
  amici/nemici, con una max-heap per ordinare per criticità). Usa i tipi
  `Block`, `Report`, `List`, `DijkstraModule`, `heapq` **senza importarli**
  — il modulo non è importabile per questo motivo (vedi Bug noti). È
  seguito da un blocco `if __name__ == "__main__":` di esempio d'uso e da
  un lungo commento esplicativo in italiano ("Caratteristiche principali",
  "Componenti da implementare") che descrive l'intento ma non è codice.
- **Funzioni pubbliche dichiarate, tutte stub (`pass`)**:
  `evaluateTacticalReport(report_list)`, `evaluateDefensePriorityZone(strategic_priority_list)`,
  `definePriorityPatrolZone(defense_priority_list, fighter_zone_cover)`,
  `evaluateResourceRequest(report)`, `evaluateTargetPriority(target_list)`,
  `evaluateTotalProduction(type, side)`, `evaluateStrategicPriority(block)`,
  `evaluateTotalTransport(type, side)`,
  `evaluateLogisticLineTransport(type, trans_from_request, trans_to_request)`,
  `evaluateTotalStorage(type, side)`, `calcCombatPowerCentrum(side, region)`.
  Le docstring/commenti indicano l'intento (es. valutare priorità di zona
  strategica per tipo — produzione, trasporto, stoccaggio, Military,
  urbano — ordinata per importanza) ma nessuna logica è presente.

In sintesi: modulo puramente di intenti/design, 0% di logica funzionante,
e non importabile nello stato attuale.

### `Tactical_Evaluation.py`

L'unico modulo del gruppo (oltre a `Air_Resources_Assigner`) con logica
realmente implementata — corrisponde abbastanza fedelmente al diagramma
`Analysis/UML/Tactical_Evaluation.plantuml` (firme di funzione, struttura
delle regole fuzzy, formule di calcolo). Nessuna classe; solo funzioni.

- `evaluateGroundTacticalAction(ground_superiority, fight_load_ratio, dynamic_increment, combat_load_sustainability) -> (str, float)` — sistema di controllo fuzzy (`skfuzzy`) a 4 antecedenti (`gs`, `flr`, `dyn_inc`, `cls`, ciascuno con 5 membership trapezoidali HI/MI/EQ/MS/HS o HS/MS/EQ/MI/HI) e un consequent `action` con 4 classi automatiche (`RETRAIT`, `DEFENSE`, `MAINTAIN`, `ATTACK`) generate da `action.automf(...)`. 20 regole fuzzy cablate esplicitamente. Restituisce l'etichetta (via `Utility.get_membership_label`) e il valore numerico [0,1]. Il commento in testa alla funzione segnala esplicitamente che le regole non sono ancora validate ("realizzare un test che visualizzi una tabella con tutte le combinazioni... per verificare la coerenza").
- `calcRecoAccuracy(parameter, recon_mission_success_ratio, recon_asset_efficiency) -> (str, float)` — fuzzy system separato (2 antecedenti `rmsr`/`rae`, 3 classi L/M/H, 9 regole) per stimare l'accuratezza di un report di ricognizione (numero asset o efficienza asset); soglia minima dell'intervallo di output diversa a seconda di `parameter` (`0.7` per `"Number"`, `0.5` per `"Efficiency"`). Validazione input con `ValueError` su valori negativi/parametro non ammesso; clamp a 1 con warning se `rmsr`/`rae` > 1.
- `calcFightResult(n_fr, n_en, eff_fr, eff_en) -> float` — calcolo (non fuzzy) del risultato di uno scontro tra due forze, basato su rapporto numerico e rapporto di efficienza, con interpolazione su una tabella di coefficienti `k_ratio` e stime probabilistiche (`random.uniform`) dei danni min/max per parte. Ritorna un valore continuo: `~0` vittoria amica netta, `1` parità, `~10+` vittoria nemica netta. Contiene un bug di validazione tipo (vedi Bug noti).
- `evaluateCombatSuperiority(action, asset_fr, asset_en) -> float` — dati due dizionari di asset per categoria (`{cat: {'num', 'combat_power': {'Attack','Defense','Maintain'}}}`), calcola la superiorità di combattimento in [0,1] sommando `num * combat_power[action]` per la parte amica e la contro-misura appropriata per il nemico (Defense se attacco, Attack se difesa/mantenimento, con `max` rispetto a Maintain). Valida `action` contro `GROUND_ACTION` e le chiavi asset contro `BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"]`.
- `evaluateCriticalityGroundEnemy(report_base, report_enemy) -> Dict` — chiama `evaluateCombatSuperiority` tre volte (Attack/Defense/Maintain) e sceglie l'azione con soglie fisse (`attack>0.55`, `maintain>0.45 and maintain>defense`, `defense>0.40`, altrimenti `retrait`), restituendo `{'action': str, 'value': int 0-100}`. Contiene una funzione interna morta (vedi Bug noti).
- `evaluateGroundRouteDangerLevel(enemy_bases, route, ground_speed, tot_time_route) -> (float,float,float)` — pensata per calcolare pericolosità aerea/terrestre/artiglieria lungo una rotta, iterando `Route.edges` (proprietà reale su `DataType.Route`) e basi nemiche. **Non eseguibile allo stato attuale**: usa `v_base.time2attack`, `v_base.efficiency`, `v_base.is_airbase`, `v_base.is_groundbase`, `v_base.artilleryInRange` — nessuno di questi attributi/metodi esiste sulle classi `Block`/`Military` viste negli altri sottosistemi già documentati; inoltre itera `for k, v_edge in Route.edges:` sulla **classe** `Route` invece che sull'istanza `route` passata come parametro (bug).
- `get_recongition_report(block)` — stub, `pass` (nome con refuso: "recongition" invece di "recognition").

Costanti modulo: `LOW_LIMIT_DAMAGE = 0.35`, `DELTA_PERC_LIMIT = 0.05`.

## Dipendenze

- **`Air_Resources_Assigner.py`**: `Asset.Aircraft` (→ innesca la catena
  circolare, vedi sotto), `Block.Military`, `Context.Context`
  (`AIR_TASK`, `AIR_TO_AIR_TASK`, `AIR_TO_GROUND_TASK`, `Air_To_Air_Task`,
  `Air_To_Ground_Task`, `TARGET_CLASSIFICATION`, `Target_Class_Name`,
  `Weapon_Power_Effect`, `Weapon_Area_Effect`,
  `get_block_infrastructure_components`, `get_task_from_target`),
  `Asset.Aircraft_Loadouts` (`AIRCRAFT_LOADOUTS`, `get_aircrafts_quantity`,
  `loadout_cost`, `get_loadout`, `get_aircraft_loadouts_by_task`,
  `get_weapons_by_loadout`), `Asset.Aircraft_Data.Aircraft_Data`,
  `Utility.LoggerClass.Logger`; esterne: `skfuzzy`, `numpy`, `random`
  (import presenti ma non usati nel corpo del modulo).
- **`Scenario_Manager.py`**: `Context.Context`, `Utility.Utility`,
  `Block.Block`, `Block.Military.Military`, `Block.Urban.Urban`,
  `Block.Production.Production`, `Block.Storage.Storage`,
  `Block.Transport.Transport`, `Asset.Asset`,
  `Component.Resource_Manager.Resource_Manager`,
  `Utility.LoggerClass.Logger`, `Context.Context.STATE`; esterna: `sympy`
  (`Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And` — importati
  ma non usati in nessun metodo).
- **`Strategical_Evaluation.py`**: `Utility.LoggerClass.Logger`,
  `Block.Military.Military`, `Context.Context`
  (`BLOCK_ASSET_CATEGORY, VALUE, GROUND_Military_VEHICLE_ASSET,
  GROUND_ACTION` — il terzo nome è errato, vedi Bug noti).
- **`Tactical_Evaluation.py`**: `Utility.Utility.get_membership_label`,
  `Context.Context` (`BLOCK_ASSET_CATEGORY, GROUND_ACTION,
  GROUND_COMBAT_EFFICACY` — quest'ultima importata ma non referenziata nel
  corpo del modulo), `DataType.Waypoint.Waypoint`, `DataType.Edge.Edge`,
  `DataType.Route.Route` (import presenti ma `Waypoint`/`Edge` non
  referenziati direttamente), `Utility.LoggerClass.Logger`; esterne:
  `skfuzzy`, `numpy`, `random`.

**Nessuno dei quattro moduli importa un altro modulo del pacchetto
`Logic/`** — non c'è alcun collegamento diretto in codice tra
`Scenario_Manager`, `Strategical_Evaluation`, `Tactical_Evaluation` e
`Air_Resources_Assigner` (confermato via `grep`: nessun file del
sottosistema referenzia gli altri tre per nome, a parte i commenti
descrittivi in `Context.py` righe 556-557).

### Blocco cross-cutting confermato (import circolare Asset-Air)

Import diretto e via test entrambi fanno fallire l'import di
`Air_Resources_Assigner.py` con lo stesso traceback:

```
Code/.../Logic/Air_Resources_Assigner.py:17
  from Code.Dynamic_War_Manager.Source.Asset import Aircraft
    → Aircraft.py:4 from ...Aircraft_Data import get_aircraft_data, get_aircraft_scores
      → Aircraft_Data.py:23 from ...Aircraft_Loadouts import ...
        → Aircraft_Loadouts.py:33 from ...Aircraft_Weapon_Data import AIR_WEAPONS, ...
          → Aircraft_Weapon_Data.py:5 from ...Aircraft import Aircraft
ImportError: cannot import name 'Aircraft' from partially initialized module
'Code.Dynamic_War_Manager.Source.Asset.Aircraft' (most likely due to a
circular import)
```

Questo è il ciclo `Aircraft → Aircraft_Data → Aircraft_Loadouts →
Aircraft_Weapon_Data → Aircraft` già noto e di competenza del sottosistema
Asset-Air (vedi nota memoria progetto). Non è stato toccato codice per
questa analisi; qui si conferma solo il blocco.

## Stato attuale

| Modulo | Stato | Importabile oggi? |
|---|---|---|
| `Air_Resources_Assigner.py` | Logica completa e ben documentata (docstring estese, esempi), ~196 test dedicati scritti | **No** — bloccato dall'import circolare Asset-Air (esterno al pacchetto) |
| `Scenario_Manager.py` | Scheletro (`CommandControl`): pochi metodi CRUD funzionanti ma con bug, resto solo commenti/`pass`; nessun test | **No** — `TypeError: unsupported operand type(s) for |: 'module' and 'NoneType'` (type hint `blocks: Block|None` dove `Block` è il **modulo** importato, non una classe) |
| `Strategical_Evaluation.py` | Stub totale: tutte le funzioni pubbliche sono `pass`; contiene solo uno schizzo di design non funzionante | **No** — `ImportError: cannot import name 'GROUND_Military_VEHICLE_ASSET'` (refuso: il nome reale in `Context.py` è `GROUND_MILITARY_VEHICLE_ASSET`, tutto maiuscolo) |
| `Tactical_Evaluation.py` | Logica implementata (fuzzy + calcoli), aderente al diagramma UML esistente; ma 2 funzioni su 7 (`evaluateGroundRouteDangerLevel`, `get_recongition_report`) non sono realmente utilizzabili | **No** — `Exception: Invalid parameters! Logger not istantiate.` (vedi Bug noti, `Logger.__init__`) |

### Test — copertura reale

- **`Test_Air_Resources_Assigner.py`** (2862 righe, 196 funzioni `def
  test_*`): sospeso al 100% dal blocco import circolare. Comando eseguito:
  `.direnv/python-3.12/bin/python3 -m unittest discover -s
  Code/Dynamic_War_Manager/Source/Test -p
  "Test_Air_Resources_Assigner.py"` → `ImportError` come sopra, `Ran 1 test
  in 0.000s — FAILED (errors=1)`. Il file di test include già
  l'infrastruttura di mocking dei logger (`_LOGGER_MRA`, `_LOGGER_LO`,
  `_LOGGER_AWD`, `_LOGGER_AD`) usata altrove nel progetto per test di
  `Aircraft_Data`/`Aircraft_Loadouts`, ma **non** applica il workaround
  "moduli fittizi in `sys.modules`" usato in `Test_Mobile.py` per aggirare
  la stessa catena — quindi oggi non parte nemmeno con mock parziali.
- **`Test_Tactical_Evaluation.py`** (569 righe, ma **1 sola** classe/`def
  test_*` trovata — `TestEvaluateGroundTacticalAction`, il file sembra
  incompleto/troncato rispetto al numero di funzioni pubbliche del modulo:
  copre solo `evaluateGroundTacticalAction`, `calcRecoAccuracy`,
  `calcFightResult`, `evaluateCombatSuperiority` sono importate ma non
  risultano testate da classi dedicate nel file). Comando eseguito → stesso
  discover → `ImportError` per il bug del `Logger` (`class_name=''`), `Ran 1
  test in 0.000s — FAILED (errors=1)`. **Nessun test è mai stato
  effettivamente eseguibile con l'attuale bug** — a meno che in una sessione
  precedente `Logger` accettasse `class_name=''`, questo modulo di test non
  ha mai potuto passare nella sua forma attuale.
- **`Scenario_Manager.py`**: **nessun file di test presente**
  (`Test_Scenario_Manager.py` non esiste). Coerente con lo stato di
  scheletro del modulo.
- **`Strategical_Evaluation.py`**: **nessun file di test presente**
  (`Test_Strategical_Evaluation.py` non esiste). Coerente con lo stato di
  puro stub.
- File di supporto trovati: `Analysis/tactical_evaluation_results.ods`
  esiste (50KB, presumibilmente risultati/tabelle di verifica manuale delle
  regole fuzzy di `evaluateGroundTacticalAction`, coerente col commento nel
  codice che chiede di costruire "una tabella con tutte le combinazioni gs,
  flr, dyn_inc e cls"); non è stato aperto/parsato in questa analisi (fuori
  scope, richiederebbe apertura di uno spreadsheet ODS).

### Bug noti (file:riga)

1. `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:42` —
   `logger = Logger(module_name=__name__, class_name='').logger`.
   `Utility/LoggerClass.py:21` solleva `Exception("Invalid parameters!
   Logger not istantiate.")` se `not (module_name and class_name)`: una
   stringa vuota è falsy, quindi **questa riga fa fallire l'import del
   modulo ogni volta**, indipendentemente da qualunque altro problema.
   Stesso identico pattern (stesso bug) in
   `Strategical_Evaluation.py:28`.
2. `Code/Dynamic_War_Manager/Source/Logic/Strategical_Evaluation.py:17` —
   `from ...Context.Context import BLOCK_ASSET_CATEGORY, VALUE,
   GROUND_Military_VEHICLE_ASSET, GROUND_ACTION`: il nome reale esportato
   da `Context.py` è `GROUND_MILITARY_VEHICLE_ASSET` (tutto maiuscolo);
   `ImportError` immediato, a monte anche del bug (1).
3. `Code/Dynamic_War_Manager/Source/Logic/Strategical_Evaluation.py:37-108`
   — le classi `ConflictGraph`/`PrioritySystem` usano negli annotation di
   funzione i nomi `Block`, `Report`, `List`, `DijkstraModule` mai
   importati; poiché il modulo non usa `from __future__ import
   annotations`, gli annotation vengono valutati eagerly alla definizione
   della funzione → `NameError` alla definizione della classe (bloccante
   quanto (1) e (2), scoperto solo dopo averli risolti).
4. `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py:29` —
   `def __init__(self, side: str, regions: List|None, blocks: Block|None)`:
   `Block` qui è il **modulo** importato con `from
   ...Block import Block` (riga 10, che in realtà importa il package
   `Block`, non la classe `Block`), non un tipo; `TypeError: unsupported
   operand type(s) for |: 'module' and 'NoneType'` alla definizione della
   classe. Anche `List` non è importato (manca `from typing import List`).
5. `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py:82` —
   `addBlock()` fa `self._events.append(block)` invece di
   `self._blocks.append(block)`; `_events` non è mai inizializzato in
   `__init__` → `AttributeError` se chiamato.
6. `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py:57,60` —
   `checkParam()` chiama `self.checkListOfObjects(...)`, metodo mai
   definito nella classe `CommandControl` né altrove nel file →
   `AttributeError` a ogni istanziazione/assegnazione di `blocks`/`regions`.
7. `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py:105,152` —
   `addRegion()` e `executeRecoinnassanceRequest()` usano `Region` e
   `self.regions` mai definiti/importati nel modulo (solo `self._regions`
   esiste come attributo, senza property `regions`) → `NameError`/
   `AttributeError`.
8. `Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py:1127` —
   `get_air_mission_task_list()`: `if task in [Air_To_Air_Task.FIGHTER_SWEEP.value,
   Air_To_Air_Task.INTERCEPT.value, Air_To_Air_Task.CAP, Air_To_Air_Task.ESCORT]`
   — gli ultimi due elementi della lista sono membri Enum, non `.value`
   stringa; `task` è sempre una stringa (validata a monte contro
   `AIR_TO_AIR_TASK`, un dict di stringhe), quindi il confronto con `CAP` ed
   `ESCORT` non può mai risultare vero. Per `task='CAP'` o `'Escort'` la
   funzione salta sia il ramo `if` sia l'`elif` (che gestisce solo `RECON`),
   lascia `aircraft_mission_task_list = {}` e poi va in `KeyError:
   'Aircraft'` alla riga successiva (`aircraft_mission_task_list['Aircraft']['task'] = task`).
9. `Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py:1133-1136` —
   ramo `elif task in [Air_To_Air_Task.RECON]` (stesso problema:
   `Air_To_Air_Task.RECON` è un membro Enum non `.value`, quindi
   irraggiungibile): anche se raggiunto, il risultato di
   `get_aircraft_mission(...)` non viene assegnato a nessuna variabile (la
   chiamata è "a vuoto"), quindi `aircraft_mission_task_list['Aircraft']`
   non esisterebbe comunque → stesso `KeyError`.
10. `Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py:43` —
    `logger = Logger(module_name=__name__, class_name='Military_Resources_Assigner')`:
    residuo del vecchio nome del modulo (`Military_Resources_Assigner`) non
    aggiornato dopo il rename in `Air_Resources_Assigner`; non impedisce
    l'esecuzione ma è fuorviante nei log/file di log (`log_
    Military_Resources_Assigner.log`) e nell'unico riferimento residuo al
    vecchio nome trovato nel codice sorgente.
11. `Code/Dynamic_War_Manager/Source/Logic/Air_Resources_Assigner.py:146` —
    `_check_mission_requirements`: condizione a catena
    `lo.get('altitude_max',0) >= req.get('altitude_max',0) <=
    lo.get('altitude_min', float('inf'))` — comparazione incatenata Python
    (`a >= b <= c`) che confronta `altitude_max` del loadout con
    `altitude_max` richiesto E SEPARATAMENTE `altitude_max` richiesto con
    `altitude_min` del loadout; espressione di dubbia intenzionalità/
    leggibilità che mischia due grandezze eterogenee (richiesta vs.
    loadout) nello stesso confronto a tre termini — da rivedere anche se
    non necessariamente "rotta" in senso stretto.
12. `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:526-529` —
    `evaluateCriticalityAirdefense` è definita **dentro**
    `evaluateCriticalityGroundEnemy`, ma **dopo** l'istruzione `return
    criticality` (riga 523): codice morto, mai eseguito, mai raggiungibile
    (una `def` innestata dopo un `return` nello stesso blocco viene comunque
    "saltata" a runtime — la funzione esterna termina prima di arrivarci).
    La funzione stessa è comunque solo uno stub (`pass`).
13. `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:559-580` —
    `evaluateGroundRouteDangerLevel`: `for k, v_edge in Route.edges:` itera
    sulla **classe** `Route` (il parametro dell'istanza si chiama `route`,
    non `Route`) — anche correggendo il refuso, `Route.edges` è una
    `@property` che richiede un'istanza, non è iterabile direttamente sulla
    classe. Inoltre usa `v_base.time2attack`, `v_base.efficiency`,
    `v_base.is_airbase`, `v_base.is_groundbase`,
    `v_base.artilleryInRange` — nessuno di questi membri risulta
    implementato nelle classi `Block`/`Military`/`Mobile` documentate negli
    altri sottosistemi (Asset, Block).
14. `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:24-25` —
    `print("\nPYTHONPATH during execution:")` + `print("\n".join(sys.path))`
    eseguiti a livello di modulo (side-effect a ogni import, anche nei
    test — visibile infatti nell'output di `unittest discover`); debug
    residuo da rimuovere.

## Problemi aperti

- **Nessun collegamento reale tra i 4 moduli.** L'obiettivo di progetto
  descrive esplicitamente un DWM che "decide azioni tattiche/strategiche"
  e "assegna risorse aeree" come pipeline coerente; nel codice attuale
  `Scenario_Manager` (comando/controllo), `Strategical_Evaluation`
  (priorità strategiche) e `Tactical_Evaluation` (esito tattico) non
  importano né chiamano `Air_Resources_Assigner`, e viceversa. L'unico
  punto che produce input strutturati coerenti con ciò che
  `Air_Resources_Assigner.get_aircraft_mission` si aspetta (`task`,
  `target_data`, `mission_requirements`) sembra dover essere
  `Strategical_Evaluation`/`Scenario_Manager`, ma nessuna delle due
  produce oggi quella struttura — è tutto ancora manuale/esterno.
- **Tre moduli su quattro non sono importabili nello stato attuale**, per
  tre cause distinte e indipendenti (bug (1)/(2)/(3) per
  `Strategical_Evaluation`, bug (4) per `Scenario_Manager`, bug (1) per
  `Tactical_Evaluation`). Nessuno di questi tre bug ha relazione con il
  blocco cross-cutting dell'import circolare Asset-Air: sono difetti
  locali al pacchetto `Logic/`, risolvibili senza toccare `Asset/`.
  Questo significa che, contrariamente a quanto la nota di progetto lascia
  intendere per `Air_Resources_Assigner` (unico blocco noto = import
  circolare esterno), gli altri tre moduli sono bloccati da problemi
  **propri**, più semplici da correggere ma non ancora affrontati.
- **`Strategical_Evaluation.py` contiene ~110 righe di codice
  "esemplificativo" generato (classi `ConflictGraph`/`PrioritySystem`,
  `if __name__ == "__main__"` con dati di prova, commento esplicativo in
  italiano che descrive "componenti da implementare" come
  `DijkstraModule`) che non corrisponde ad alcuna funzione pubblica del
  modulo e usa nomi/tipi (`Block`, `Report`) diversi da quelli realmente
  presenti nel progetto (`Block` è un package con più sottoclassi:
  `Military`, `Urban`, `Production`, ecc., non una classe monolitica con
  attributi `type`/`faction`/`combat_power`/`connections` come ipotizzato
  nello schizzo). Va deciso se questo materiale è ancora rilevante come
  riferimento di design o va rimosso perché fuorviante (oggi impedisce
  persino l'import del modulo).
- **`Scenario_Manager.py`/`CommandControl` è un doppione concettuale
  parziale di `Region`/`Military`.** I metodi di gestione
  `blocks`/`regions` duplicano responsabilità già presenti (con
  implementazione reale) in `Region.py` e `Block/Military.py`
  (documentati in note di progetto precedenti: `Region._get_region_average_metric`,
  `Military.get_recognition_report`, ecc.). Non è chiaro se
  `CommandControl` debba diventare l'orchestratore di livello superiore
  (un "side controller" che aggrega più `Region`) o se sia materiale
  superato da quando `Region`/`Military` sono stati sviluppati
  autonomamente. Il file non è referenziato da nessun altro modulo del
  progetto (confermato via grep), è verosimilmente codice orfano.
  Il commento su "C2 Planner"/SAGE (righe 202-207) suggerisce un'origine
  comune con `Analysis/Document/The Theater-Level Campaign Model.pdf`
  (non aperto in questa analisi, ma il nome dell'algoritmo — Sequential
  Analytic Game Evaluation — è troppo specifico per essere invenzione
  locale).
- **`Tactical_Evaluation.evaluateGroundRouteDangerLevel` presuppone
  un'API su `Block`/`Military` (basi nemiche) che non esiste** —
  `time2attack`, `efficiency`, `is_airbase`, `is_groundbase`,
  `artilleryInRange`. Questo suggerisce che la funzione sia stata scritta
  prima (o indipendentemente) dal refactoring di `Block`/`Military`/`Mobile`
  documentato nelle note di progetto (dove i concetti equivalenti sono
  `Military.combat_range()`, `Military.air_defense_volume()`, `Mobile.
  combat_range()`) — un disallineamento tra design storico e
  implementazione attuale del sottosistema Asset/Block, da riconciliare
  quando si riprenderà questa funzione.
- **`Test_Tactical_Evaluation.py` copre solo 1 delle 5 funzioni pubbliche
  utilizzabili** (`evaluateGroundTacticalAction`, `calcRecoAccuracy`,
  `calcFightResult`, `evaluateCombatSuperiority`, `evaluateCriticalityGroundEnemy`
  sono importate all'inizio del file ma risultano usate/testate solo
  parzialmente in un'unica classe di test) — anche una volta risolto il
  bug del `Logger`, la copertura reale andrà verificata e probabilmente
  estesa.
- **Import inutilizzati / residui di refactoring** in più file
  (`skfuzzy`/`ctrl`/`numpy` in `Air_Resources_Assigner.py`; `sympy` in
  `Scenario_Manager.py`; `Waypoint`/`Edge` in `Tactical_Evaluation.py`;
  `GROUND_COMBAT_EFFICACY` in `Tactical_Evaluation.py`) — indicano che
  questi moduli sono stati modificati più volte senza una pulizia finale;
  utile un passaggio di lint (es. `pyflakes`) su tutto il pacchetto
  `Logic/` una volta sbloccati gli import.
