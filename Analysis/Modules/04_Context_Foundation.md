# Context — Fondamenta e Dati Iniziali

## Scopo

Il sottosistema CONTEXT-FOUNDATION fornisce il vocabolario di dominio (enum, costanti,
tabelle statiche) e i dati di inizializzazione/stato usati da praticamente tutti gli
altri sottosistemi (Asset, Block, Logic). Comprende:

- `Context.py`: la base concettuale — enum e costanti condivise, senza alcuna
  dipendenza da altri moduli applicativi del progetto (solo `enum`, `typing`, `Logger`).
- `Initial_Context.py`: dati statici di inizializzazione campagna (quantità/produzione/
  riparazione iniziali di asset, disponibilità armamenti, template di regione).
- `Actual_Context.py`: (nominalmente) stato runtime attuale della campagna, in gran
  parte una copia di `Initial_Context.py` con l'aggiunta di contatori di missione.
- `Logistic_Lines.py`: gestione delle linee logistiche (collegamento server↔trasporto↔
  cliente tra Block), pensato per la ridistribuzione delle risorse.

## File inclusi

| File                                                         | Righe | Note                                                     |
| ------------------------------------------------------------ | ----- | -------------------------------------------------------- |
| `Code/Dynamic_War_Manager/Source/Context/Context.py`         | 1508  | enum/costanti di dominio, nessuna dipendenza applicativa |
| `Code/Dynamic_War_Manager/Source/Context/Initial_Context.py` | 987   | dati di inizializzazione campagna                        |
| `Code/Dynamic_War_Manager/Source/Context/Actual_Context.py`  | 1894  | stato runtime + duplicazione di Initial_Context          |
| `Code/Dynamic_War_Manager/Source/Context/Logistic_Lines.py`  | 191   | linee logistiche (stub non funzionante)                  |

Diagramma UML pertinente: `Analysis/UML/Logistic_Lines.plantuml` (4 diagrammi: component,
class, activity `set_line`, sequence `setup_blocks_resource_manager`).

## Costanti, enum e funzioni principali

### Context.py

Nessuna dipendenza da moduli applicativi → è la vera "fondazione" priva di cicli
d'importazione. Contenuto organizzato in blocchi tematici:

- **Dimensioni fisiche**: `VEHICLE_SIZE_CATEGORY`, `SHIP_SIZE_CATEGORY`,
  `STRUCTURE_SIZE_CATEGORY` + `get_dimension(asset_type, length, width, height, weight,
  structure_type=None)` — classifica un asset in `'big'/'medium'/'small'` (veicoli/navi)
  o `'Big'/'Medium'/'Small'` (strutture). **Unico chiamante esterno**:
  `Block/Block.py:632`. Le tre tabelle di soglie non sono usate da nessun'altra parte
  del codice se non internamente a `get_dimension`.
- **Task/azioni**: `Ground_Action`→`GROUND_ACTION`, `Air_To_Air_Task`/
  `Air_To_Ground_Task`→`AIR_TO_AIR_TASK`/`AIR_TO_GROUND_TASK`→`AIR_TASK`, `Sea_Task`→
  `SEA_TASK`, `ACTION_TASKS` (dict `{'ground':…, 'air':…, 'sea':…}`). Vocabolario più
  riusato del modulo: `AIR_TASK` e `GROUND_ACTION` compaiono in 13 e 11 file
  rispettivamente (Military_Resources_Assigner, Air_Resources_Assigner, Tactical/
  Strategical_Evaluation, Aircraft_Data, ecc.).
- **Categorie asset terrestri**: `Ground_Vehicle_Asset_Type` (alias `ag`; 10 membri:
  TANK, ARMORED, MOTORIZED, ARTILLERY_FIXED/SEMOVENT, SAM_BIG/MEDIUM/SMALL, EWR, AAA) —
  usata in 9 file (Military.py, Mobile.py, Vehicle_Data.py, …). `WEIGHT_FORCE_GROUND_ASSET`
  e `GROUND_COMBAT_EFFICACY` sono pesi di bilanciamento per il calcolo della combat
  power; il primo risulta **senza alcun chiamante esterno** (0 file), il secondo è
  usato in 4 file.
- **Categorie asset aerei/navali**: `Air_Asset_Type` (alias non definito nel modulo,
  usata in 7 file), `Sea_Asset_Type` (alias `asea`, 9 membri, usata in 7 file),
  `AIR_MILITARY_CRAFT_ASSET`, `SEA_MILITARY_CRAFT_ASSET`, `AIR_DEFENSE_ASSET`,
  `GROUND_MILITARY_VEHICLE_ASSET` — dizionari "economici" (cost/value/t2r/rcp/
  payload%) con **`'cost': None` mai popolato** in nessuna voce: dato predisposto ma
  non ancora valorizzato.
- **Tassonomia bersagli/armi**: `Weapon_Power_Effect`, `Weapon_Area_Effect`,
  `Target_Class_Name` (alias `tc`) + `WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE`,
  `TASK_FOR_WEAPON_PARAM`, `_get_task_from_weapon_param()`,
  `_get_weapon_param_from_target()`, `get_task_from_target()` — logica che deriva il
  task aria-suolo (Strike/Pinpoint_Strike) dal tipo/dimensione/quantità del bersaglio.
  Ben testata (vedi sotto).
- **Infrastrutture di blocco**: `BLOCK_INFRASTRUCTURE_ASSET` (dizionario nidificato
  enorme: block_class → asset_category → asset_type → dati economici) +
  `get_block_infrastructure_components(block_class, asset_category)` (1 solo
  chiamante esterno). `TARGET_CLASSIFICATION` + `get_target_classification(target_type)`
  mappano ogni asset/parked-unit alla classificazione di bersaglio (Soft/Armored/Hard/
  Structure/Air_Defense/Airbase/…): `TARGET_CLASSIFICATION` è usata in 6 file,
  `get_target_classification` in 2.
- **`BLOCK_ASSET_CATEGORY`**: dizionario derivato a tempo di import (loop su
  `BLOCK_INFRASTRUCTURE_ASSET`, `GROUND_MILITARY_VEHICLE_ASSET`, `AIR_DEFENSE_ASSET`,
  `AIR_MILITARY_CRAFT_ASSET`, `SEA_MILITARY_CRAFT_ASSET`). È il **simbolo più usato
  di tutto il modulo (13 file client)**, nonostante sia preceduto (Context.py:1424) da
  un commento `# DEPRECATED (prima vedi di sostituire BLOCK_ASSET_CATEGORY)` la cui
  collocazione è ambigua (vedi Problemi aperti).
- Enum di supporto generiche: `Asset_Role`, `Logistic_Asset_Type` (alias `la`/`lat`),
  `SHAPE3D`, `SHAPE2D`, `VALUE`, `FOOD_CATEGORY`, `COUNTRY`, `SKILL`, `GROUP_CATEGORY`,
  `Parked_Asset_Type`, `SIDE`, `AREA_FOR_VOLUME`, `COALITIONS`, `PATH_TYPE`,
  `ROUTE_TYPE`, `BLOCK_CATEGORY`, `MILITARY_CATEGORY`, `MILITARY_FORCES`,
  `PRODUCTION_WEIGHT` (usata in 1 file), `STATE`, `MAX_AIRCRAFT_TYPE_FOR_MISSION`.
- `AIRCRAFT_TYPE` (commentato dallo stesso autore con `# necessario?`) e
  `AIR_COMBAT_EFFICACY` (valorizzato solo per 'F-15' e 'F-4E') sono dati orfani/
  incompleti, senza chiamanti esterni.

### Initial_Context.py

Dati statici organizzati per side-neutral pool: `PRODUCTION_ASSET`
(capacità produttiva per categoria, tutta a valore 1 — placeholder), `_ASSET_AVAILABILITY`
(quantità/produzione/riparazione iniziali per ogni modello air/ground/sea, con tabella
di riferimento estesa in docstring), `REGIONS_ASSET` (template per regione: basi aeree/
navali/terrestri con infrastruttura e asset operativi iniziali), `_MILITARY_BASE_ASSETS`
(dizionario **vuoto**, mai popolato), `navi` (dizionario locale nave→classe/nazionalità,
usato solo come riferimento incrociato in un commento di `Ship_Data.py:464`, mai
importato programmaticamente), `_WEAPONS_AVAILABILITY` (disponibilità iniziale
armamenti aria/terra/mare), `_REFERENCE_COST_K`.

### Actual_Context.py

Stessa impalcatura, con `REGION_ASSETS_STATUS` al posto di `REGIONS_ASSET`: struttura
quasi identica (region → military_bases → airbases/naval_bases/ground_bases →
infrastructure/operative asset) più un blocco `'mission'` per base con contatori
`success_count`/`total_count` per ciascun task aria-aria/aria-suolo. Le uniche
funzioni realmente definite nel file sono `update_mission_count()` (riga 1530) e
`get_mission_success_rate()` (riga 1573), che operano su questi contatori.

### Logistic_Lines.py

`@dataclass Logistic_Line` (id, side, name, transport_line, server, client,
bidirectional, state) + classe `Logistic_Lines` con `set_line()`, `get_line()`,
`get_logistic_line_by_id()`, `get_logistic_line_by_criteria()` (`@lru_cache`),
`setup_blocks_resource_manager()`, `_add_logistic_line()`, `_invalidate_caches()`.
Concettualmente rappresenta il collegamento Resource_Server → Transport → Resource_Client.

## Dipendenze

- **Context.py**: solo `enum`, `typing`, `Utility.LoggerClass` — nessuna dipendenza da
  altri moduli applicativi del progetto. È alla radice della gerarchia, nessun import
  circolare.
- **Initial_Context.py / Actual_Context.py**: importano da `Context.py` (enum) e da
  `Asset.Aircraft_Loadouts` + `Asset.Aircraft_Data` → questo li aggancia alla catena di
  import circolare nota `Aircraft → Aircraft_Data → Aircraft_Loadouts →
  Aircraft_Weapon_Data → Aircraft`, quindi **non sono importabili in isolamento** nei
  test (stesso problema già documentato per Vehicle/Ship/Aircraft in memoria progetto).
- **Logistic_Lines.py**: `Context`, `Utility`, `Block.Transport`, `Block.Block`,
  `DataType.Payload`, `DataType.State`, `Utility.LoggerClass`.

## Stato attuale

**Context.py — solido.** Eseguito realmente:
```
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Context.py"
→ Ran 145 tests in 0.009s — OK
```
Coperti: tutti gli enum, `get_dimension`, `_get_task_from_weapon_param`,
`_get_weapon_param_from_target`, `get_task_from_target`. **Non coperti**:
`TARGET_CLASSIFICATION`, `get_target_classification`, `BLOCK_ASSET_CATEGORY`,
`get_block_infrastructure_components`, `BLOCK_INFRASTRUCTURE_ASSET`,
`AIR_DEFENSE_ASSET`, `GROUND_MILITARY_VEHICLE_ASSET`, `AIR_MILITARY_CRAFT_ASSET`,
`SEA_MILITARY_CRAFT_ASSET` — nonostante `BLOCK_ASSET_CATEGORY` sia il simbolo più
riusato dell'intero sottosistema (13 file client).

**Initial_Context.py e Actual_Context.py — non importabili.** Verificato realmente:
```python
from Code.Dynamic_War_Manager.Source.Context.Context import Sea_Asset_Type as asea
asea.FAST_ATTACK.value
→ AttributeError: type object 'Sea_Asset_Type' has no attribute 'FAST_ATTACK'
```
`Initial_Context.py:101` e `Actual_Context.py:70` referenziano `asea.FAST_ATTACK`, che
non esiste nell'enum (il membro reale è `CORVETTE = 'Corvette'  # Fast_Attack`, come
confermato dal commento nel sorgente e da `Ship_Data.py:1204`
`# corrispondono alla categoria 'Fast Attack' nel dizionario navi`). Import di
entrambi i moduli fallisce con `AttributeError` **indipendentemente** dal problema di
import circolare. Nessun test dedicato esiste per nessuno dei due file.
`Test_Air_Resources_Assigner.py` (che importa `_WEAPONS_AVAILABILITY` da
`Initial_Context`) fallisce comunque, ma per una causa diversa — eseguito realmente:
```
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Air_Resources_Assigner.py"
→ ImportError: cannot import name 'Aircraft' from partially initialized module
  '...Asset.Aircraft' (most likely due to a circular import)
```
(il problema di import circolare maschera di fatto anche il bug FAST_ATTACK: il test
fallisce prima ancora di arrivare a valutare `Initial_Context.py`).

**Logistic_Lines.py — non funzionale.** Nessun bug di import (dipende solo da moduli
sani), ma la classe `Logistic_Lines` non è utilizzabile nemmeno isolatamente: vedi
dettaglio bug in Problemi aperti. Non è importato da nessun altro modulo del progetto
(unico riferimento a "Logistic_Lines" nel repo è nel file stesso). Nessun test dedicato
esiste (`Test_Logistic_Lines.py` assente).

**Copertura test complessiva del sottosistema**: 1508 righe testate (Context.py, 145
test) su un totale di ~4580 righe (Context.py + Initial_Context.py + Actual_Context.py
+ Logistic_Lines.py) — le restanti ~3072 righe (Initial_Context, Actual_Context,
Logistic_Lines) hanno **copertura zero**.

## Problemi aperti

1. **Bug fatale `asea.FAST_ATTACK`** (`Initial_Context.py:101`, `Actual_Context.py:70`):
   blocca l'import di entrambi i moduli. Fix banale (`asea.CORVETTE`), ma finché non è
   applicato nessun codice che dipende da questi moduli può essere realmente eseguito
   in isolamento.
2. **Naming mismatch** in `Rinomina_Campaign_State.py:29`: importa `ASSET_AVAILABILITY`
   da `Initial_Context`, ma l'attributo reale ha underscore iniziale
   (`_ASSET_AVAILABILITY`) — ulteriore `ImportError` se questo script fosse mai eseguito
   (oltre al bug FAST_ATTACK a monte).
3. **Duplicazione strutturale massiccia tra Initial_Context.py e Actual_Context.py**:
   `PRODUCTION_ASSET`, `_ASSET_AVAILABILITY` e `_WEAPONS_AVAILABILITY` sono copiati
   **identici** (diff vuoto verificato per `_WEAPONS_AVAILABILITY`) tra i due file,
   invece di essere importati da un'unica fonte. Anche la docstring di modulo e il
   `class_name` del logger (`Actual_Context.py:36` dichiara ancora
   `class_name='Initial_Context'`) tradiscono un copia-incolla mai ripulito. Rischio
   concreto di divergenza silenziosa tra i due dataset nel tempo.
4. **Sovrapposizione concettuale non risolta tra `REGIONS_ASSET` (Initial_Context) e
   `REGION_ASSETS_STATUS` (Actual_Context)**: strutturalmente quasi identici, differiscono
   solo per il blocco `'mission'`. Ci si aspetterebbe una funzione che inizializzi
   `REGION_ASSETS_STATUS` copiando `REGIONS_ASSET` a inizio campagna, ma **non esiste
   alcun codice che lo fa** — il collegamento tra i due resta solo concettuale/
   implicito, mai implementato.
5. **Relazione con `Campaign_State.py`** (altro modulo della cartella Context, fuori
   scope qui ma da chiarire in altro documento): stando alla memoria di progetto,
   `Campaign_State` è il meccanismo di persistenza/snapshot dello stato runtime già
   testato (78 test OK). `Actual_Context.py` sembra un tentativo precedente/parallelo,
   mai completato, di ottenere lo stesso risultato con dizionari statici mutabili in
   memoria — possibile codice ridondante o superato, da verificare.
6. **Bug di struttura dati in `TARGET_CLASSIFICATION`** (Context.py:1331-1340): le
   chiavi `AIRBASE`, `HELIBASE`, `PORT`, `SHIPYARD`, `FARP`, `STRONGHOLD`, `SHIP`,
   `GENERIC` hanno come valore `[dict.keys()]` — una lista con **un solo elemento**
   che è un oggetto `dict_keys`, non una lista piatta di stringhe. La funzione
   `get_target_classification()` prova a intercettare errori di nidificazione con
   `isinstance(tg_type_element, list)`, ma un `dict_keys` non è un'istanza di `list`,
   quindi il controllo non scatta e il confronto `target_type == tg_type_element`
   (stringa contro `dict_keys`) non è mai vero: la classificazione di un target di
   questi tipi fallisce silenziosamente restituendo `None` anziché la classificazione
   corretta o un errore esplicito. Nessun test copre questa funzione, quindi il bug
   non è mai stato rilevato.
7. **`get_weapons_param_for_asset_type` è una funzione "fantasma"**: il testo esiste
   nel file (righe ~1062-1066, insieme a un vecchio duplicato di
   `WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE`), ma è racchiuso in un blocco stringa
   letterale `"""..."""` (righe 1024-1068) — non viene mai eseguito da Python e non
   esiste come attributo reale del modulo (coerente con gli 0 chiamanti esterni
   trovati). Da rimuovere definitivamente o riattivare consapevolmente.
8. **Commento "DEPRECATED" ambiguo** (Context.py:1424): `# DEPRECATED (prima vedi di
   sostituire BLOCK_ASSET_CATEGORY)` precede immediatamente il blocco di codice che
   *genera* `BLOCK_ASSET_CATEGORY`. Non è chiaro se il commento intenda dire che tutto
   ciò che segue è deprecato, o che va sostituito qualcos'altro prima di toccare
   `BLOCK_ASSET_CATEGORY` — che resta comunque il simbolo più usato del sottosistema
   (13 file client).
9. **Costanti orfane o palesemente incomplete**: `WEIGHT_FORCE_GROUND_ASSET` (0
   chiamanti esterni), `VEHICLE_SIZE_CATEGORY`/`SHIP_SIZE_CATEGORY` (usate solo
   internamente a `get_dimension`), `navi` e `_MILITARY_BASE_ASSETS` (vuoto) in
   `Initial_Context.py`, `AIRCRAFT_TYPE` (l'autore stesso lo marca `# necessario?`),
   `AIR_COMBAT_EFFICACY` (valorizzato solo per 2 modelli su decine presenti nel
   dataset) — candidate a pulizia o completamento consapevole.
10. **Logistic_Lines.py non funzionale e non wired**: è il modulo che concettualmente
    dovrebbe implementare la "gestione rifornimenti" (consumi/produzione/
    ridistribuzione) richiesta dall'obiettivo di progetto, ma:
    - `__init__`: `self._logistic_lines: Dict[str: Logistic_Line]` è una bare
      annotation senza `= {}` — l'attributo non viene mai realmente creato.
    - `set_line()` costruisce `Logistic_Line(id=id, transport_line=..., server=...,
      client=...)` omettendo i campi obbligatori del dataclass `side`, `name`,
      `bidirectional`, `state` → `TypeError` certo a runtime.
    - `_add_logistic_line()` controlla `lgs_line.id in self._lines`, ma l'attributo si
      chiama `_logistic_lines`, non `_lines` → `AttributeError`.
    - `remove_logistic_line()` usa `self._blocks.pop(...)` — attributo mai definito
      → `AttributeError`.
    - `get_line(**args)` è vuoto (solo `pass` in ogni ramo) e comunque `args.search`
      non è valido su un dict prodotto da `**args` (serve `args['search']` o
      `args.get('search')`).
    - `get_logistic_line_by_criteria()` è decorata `@lru_cache` su un metodo
      d'istanza (tiene `self` vivo indefinitamente — anti-pattern) e dichiara tutti i
      filtri `Optional[str] = None`, ma nel corpo fa `isinstance(side, str)` ecc.,
      quindi **anche la chiamata più semplice senza filtri solleva `TypeError`**.
    - `setup_blocks_resource_manager()` itera `self._lines` (mai definito) e legge
      `line.transport` (il campo del dataclass è `transport_line`, non `transport`).
    - Il diagramma `Analysis/UML/Logistic_Lines.plantuml` documenta fedelmente il
      codice "as-written" (compresa la chiamata incompleta a `Logistic_Line(...)`
      nell'activity diagram) — riflette quindi il design bacato attuale, non un
      target corretto.
    - Non è importato da nessun altro modulo del progetto: è codice isolato, mai
      collegato al resto del sistema. La gestione reale dei rifornimenti (se esiste)
      va cercata nel sottosistema Block/Resource_Manager (fuori scope di questo
      documento).
11. **Copertura test zero** per `Initial_Context.py`, `Actual_Context.py`,
    `Logistic_Lines.py` (~3072 righe totali su ~4580 dell'intero sottosistema) — a
    fronte delle 1508 righe ben testate di `Context.py`.
