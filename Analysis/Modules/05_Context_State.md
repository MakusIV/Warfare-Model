# Context — Stato Operativo e Persistenza

## Scopo

Il sottosistema `Context` (cartella `Code/Dynamic_War_Manager/Source/Context/`) rappresenta lo stato operativo dinamico della campagna: la classe `Region` modella un'area geografica con i suoi blocchi (`Block`) e le rotte (`Route`) che li collegano, e fornisce i calcoli strategici (priorità di attacco/difesa, centri di potenza di combattimento, efficienze aggregate) usati dal motore decisionale. `Campaign_State` e `Target_Status_History` sono due meccanismi di persistenza/storicizzazione complementari ma con scopi diversi: il primo salva lo **stato interno completo e mutabile** degli oggetti di gioco (per poterlo ripristinare), il secondo salva lo stato **come lo vedrebbe un ricognitore nemico** (report di riconoscimento, usato per analisi strategiche/tattiche post-missione). Il modulo include anche due file non collegati al resto del progetto (`Coalition.py`, orfano, e `Rinomina_Campaign_State.py`, riservato per riuso futuro) che sono documentati separatamente più sotto.

## File inclusi

| File | Righe | Classi principali |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Context/Region.py` | 1279 | `Region`, `BlockItem` (dataclass), `RegionParams` (dataclass, inutilizzata), `BlockCategory` (Enum) |
| `Code/Dynamic_War_Manager/Source/Context/Campaign_State.py` | 720 | `CampaignState` |
| `Code/Dynamic_War_Manager/Source/Context/Target_Status_History.py` | 298 | `TargetStatusHistory` |
| `Code/Dynamic_War_Manager/Source/Context/Coalition.py` | 88 | `Coalition` — **orfano** |
| `Code/Dynamic_War_Manager/Source/Context/Rinomina_Campaign_State.py` | 140 (di cui solo ~44 codice, resto docstring/commenti) | `Campaign_State` (vecchia versione) — **riservato per riuso futuro** |

Diagrammi UML pertinenti (non verificati riga per riga contro il codice attuale in questa sessione, ma consultati come riferimento): `Analysis/UML/Region.plantuml` (330 righe, component/dependency diagram), `Analysis/UML/Region.Sequence.Diagram.plantuml` (1315 righe).

## Classi e funzioni principali

### `Region` (Region.py)

Gestisce blocchi e rotte di un'area operativa. Costruita attorno a un dizionario `_blocks: Dict[str, BlockItem]` (accesso O(1) per id) e `_routes: Dict[str, Route]`.

- `__init__(name, limes=None, description=None, blocks=None, routes=None)` — valida i parametri con `_validate_init_params`; inizializza `attack_weight=0.5` e `weight_priority_target` da `DEFAULT_WEIGHT_PRIORITY_TARGET`.
- Proprietà: `name`, `description`, `attack_weight` (setter valida 0≤x≤1), `weight_priority_target` (copia difensiva in getter/setter), `blocks` (lista di `BlockItem`), `routes` (copia del dict).
- **Gestione blocchi**: `add_block(block, priority=0.0)`, `remove_block(block_id)`, `get_block_by_id(block_id)`, `get_blocks_by_criteria(side=None, category=None, block_class=None)` (con `@lru_cache(maxsize=128)`), `get_sorted_priority_blocks(count, side, sort_by='highest'|'lowest', category=None)`, `get_normalized_priority_blocks(...)`.
- **Gestione rotte**: `add_route(key, route)`, `get_route(block_id, target_block_id=None)` (con `@lru_cache`), `get_shortest_route`, `get_safest_route`, `get_shortest_and_safest_route`.
- **Calcoli strategici** (tutti `@lru_cache(maxsize=3)`, una entry per side): `calc_strategic_logistic_center(side) -> Optional[Point2D]`, `calc_combat_power_center(side) -> Dict[force, Dict[task, Point2D]]`, `calc_total_warehouse(side) -> Payload`, `calc_total_production(side) -> Payload`, `calc_production_values(side) -> Dict[str, float]`.
- **Aggiornamento priorità**: `update_logistic_priorities(side)`, `update_military_priorities(side)`, `run_resource_management_cycle(side)` (orchestratore: logistica → militare → ciclo risorse per blocco).
- **Metriche aggregate** — tutte costruite sopra l'helper comune `_get_region_average_metric(side, category, method_name)` (usa `getattr(block, method_name, None)` + `callable()`, quindi silenzioso se il blocco non espone il metodo):
  - `get_region_morale(side)` → media di `block.morale()` sui blocchi Military
  - `get_region_recon_efficiency(side)` → media di `block.get_recon_efficiency()`
  - `get_region_resource_efficiency(side)` → media di `block.resource_efficiency()` sui blocchi Logistic
  - `get_region_intelligence_efficiency(side)` → media di `block.intelligence()` sui blocchi Military — **vedi Problemi aperti: `intelligence` non esiste su `Military`, quindi restituisce sempre 0.0 in produzione**
  - `get_c2_efficiency(side)` → media di `block.get_c2_efficiency()`
- `get_recon_reports(side)` — calcola una volta `get_c2_efficiency(side)` e lo passa a `block.get_recognition_report(region_c2_recon_efficiency)` per ogni blocco Military del lato.
- `get_target_report(report)` — classifica gli asset di un recognition report per categoria target (`Context.get_target_classification`), sommando le quantità per tipo/dimensione.
- Metodi privati di calcolo priorità: `_calc_attack_priority`, `_calc_defense_priority`, `_select_weight`, `_calculate_priority`, `_calc_surface_priority`, `_calc_air_priority` — tutti decorati `@lru_cache`, operano su tuple hashabili costruite con `_get_tuple_hashable_block_item` per evitare di invalidare la cache ad ogni chiamata.
- `_invalidate_caches(cache_type=None)` — invalida selettivamente o tutte le cache lru; il commento nel codice chiarisce che nella pratica viene sempre invalidato tutto, perché qualsiasi modifica a blocchi/rotte altera priorità e centri strategici.

**Comportamenti sorprendenti / bug rilevati in Region.py:**

- **Bug di mutazione della cache LRU** (`Region.py:239-282` + `Region.py:305-306`): `get_blocks_by_criteria` è decorato con `@lru_cache` e ritorna sempre lo **stesso oggetto lista** per una data combinazione di argomenti. `get_sorted_priority_blocks` chiama `blocks = self.get_blocks_by_criteria(...)` e poi esegue `blocks.sort(key=..., reverse=sort_by)` **in-place** su quella stessa lista (riga 306). Questo muta permanentemente il contenuto della cache: la prossima chiamata a `get_blocks_by_criteria` con gli stessi argomenti restituirà l'elenco già ordinato dall'ultima chiamata di `get_sorted_priority_blocks`, indipendentemente dall'ordine con cui i blocchi sono stati aggiunti. Confermato sperimentalmente con un caso minimale isolato (`lru_cache` + `.sort()` in-place → stesso oggetto, mutazione persistente). Non coperto dalla suite di test attuale (gli 80 test che passano non verificano l'ordine cross-call). Non modificato in questa sessione di sola analisi.
- `get_route(...)` — la docstring dichiara `Returns: The shortest matching Route object, or None` ma il metodo restituisce in realtà una **lista** di `Route` corrispondenti (o `None` se vuota); sono `get_shortest_route`/`get_safest_route`/`get_shortest_and_safest_route` a ridurre la lista a un singolo oggetto. Docstring disallineata dal comportamento reale.
- `RegionParams` (dataclass, righe 82-89) è definita ma **mai utilizzata** in tutto il codebase (verificato con grep) — probabile relitto di una vecchia validazione via dataclass, ora sostituita da `_validate_init_params`.
- `get_normalized_priority_blocks` — se tutti i blocchi hanno la stessa priorità, `delta = blocks[0].priority - min == 0` e la normalizzazione produce una `ZeroDivisionError` (nessun guard).
- `calc_combat_power_center` ha un commento nel codice ("verifica se i risultati coincidono con quelli attesi con la logica del vecchio metodo") che suggerisce che la riscrittura rispetto alla versione precedente (lasciata commentata subito sopra, righe ~448-481) non è stata formalmente validata.
- Uso estensivo di `@lru_cache` su metodi di istanza (incluso su metodi che accettano `Military`/`Block` come argomento, es. `_calc_attack_priority`, `_select_weight`): funziona perché gli oggetti sono hashable di default (identità), ma lega la cache al ciclo di vita della classe (non dell'istanza) — un pattern noto per trattenere riferimenti e potenzialmente perdere memoria se le istanze vengono ricreate frequentemente; il codice ne è consapevole (commenti in `_invalidate_caches`) ma non lo risolve.

### `CampaignState` (Campaign_State.py)

Contenitore di snapshot completi dello stato di gioco (Region, Block, State, Resource_Manager, Asset, Route), indicizzato per `mission_id`. Vedi già documentato in memoria di progetto; conferme dalla lettura del sorgente attuale:

- **Write API**: `add_campaign_snapshot(mission_id, date, time, regions: List)` (delega a `add_region_snapshot` per ogni regione), `add_region_snapshot(mission_id, date, time, region)`, `add_block_snapshot(mission_id, date, time, region_name, block, priority=0.0)` (crea l'entry di regione con metadati nulli se non esiste ancora).
- **Read API**: `missions` (property), `get_mission`, `get_region_snapshot`, `get_block_snapshot`, `get_block_history`, `get_field_trend`, `get_asset_history`.
- **Restore API**: `restore(mission_id, regions: List)` — applica lo snapshot a oggetti live (`Region.attack_weight`/`weight_priority_target`, `BlockItem.priority`, `Block/Asset.state.health`/`success_ratio`, payload fields, `Route.Edge.danger_level`/`speed`); oggetti presenti nello snapshot ma assenti nel grafo live vengono loggati come warning e saltati (nessuna eccezione).
- **Persistenza**: `save(path)` (JSON UTF-8, `json.dumps(..., default=str)`), `CampaignState.load(path)` (classmethod).
- Serializzazione basata su `getattr(obj, '_attr', None)` diffuso — resiliente a oggetti mock/parziali nei test, ma significa che la struttura serializzata dipende dai nomi interni (`_state`, `_warehouse`, `_health`, ecc.) degli oggetti `Block`/`Asset`/`Route`: un refactoring dei nomi di attributo privati in quei moduli romperebbe silenziosamente la serializzazione (nessun controllo di tipo esplicito).
- `_ensure_mission` solleva `ValueError` se si tenta di registrare la stessa `mission_id` con `date`/`time` diversi da quelli già presenti — comportamento voluto (una missione ha una sola data/ora).

### `TargetStatusHistory` (Target_Status_History.py)

Storicizza i `recognition_report` (vista "bersaglio militare", non stato operativo interno) per ogni blocco, indicizzati per missione/regione. API strutturalmente simmetrica a `CampaignState` ma più semplice (nessuna Restore API, dato che un recognition report non è uno stato da ripristinare):

- **Write**: `add_block_snapshot(mission_id, date, time, region_name, block_id, recognition_report: Dict)`, `add_region_snapshot(mission_id, date, time, region_name, blocks: Dict[block_id, report])`.
- **Read**: `missions`, `get_mission`, `get_region_snapshot`, `get_block_snapshot`, `get_block_history`, `get_field_trend`.
- **Persistenza**: `save`/`load` (stesso pattern JSON di `CampaignState`).
- Il docstring della classe contiene una tabella markdown "incollata" a mano (righe 35-90) che duplica in italiano la stessa documentazione già presente sopra in inglese — ridondante ma non un bug funzionale.
- Nessuna dipendenza da altri moduli `Context`/`Block`/`Asset`: il modulo tratta i report come `Dict[str, Any]` opachi, quindi è completamente disaccoppiato dalla forma esatta del recognition report prodotto da `Military`/`Block`.

## Dipendenze

- **Region.py** dipende da: `Context.Context` (enum azioni, `MILITARY_FORCES`, `ACTION_TASKS`, `get_target_classification`), `Utility.Utility` (`check_side`, `enemySide`), `Block.Block` (`Block`, `MAX_VALUE`, `MIN_VALUE`), `Block.Military`, `Block.Production`, `Block.Storage`, `Block.Transport`, `Block.Urban`, `DataType.Limes`, `DataType.Route`, `DataType.Payload`, `Utility.LoggerClass.Logger`, più le librerie esterne `sympy.Point2D` e `numpy.clip`. Questo rende `Region` un modulo centrale con forte accoppiamento verso l'intero sottosistema `Block`.
- **Campaign_State.py** e **Target_Status_History.py** sono invece deliberatamente "leggeri": dipendono solo da `json`, `pathlib`, `datetime`, `typing` e `Utility.LoggerClass.Logger`. Non importano `Region`/`Block`/`Asset` direttamente — accedono ai dati via `getattr` duck-typing, il che li rende testabili con semplici stub/oggetti fittizi senza incorrere nel problema di import circolare descritto sotto.
- Nessuno dei tre file usa `Coalition.py` o `Rinomina_Campaign_State.py`.
- **Import circolare noto** (non in questo sottosistema ma che lo tocca indirettamente tramite `Region → Block.Military`): la catena `Aircraft.py → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft.py` è irrisolta; poiché `Military.py` importa (indirettamente) asset concreti, i test di `Region` che coinvolgono `Military` reale possono risentirne — la suite `Test_Region.py` usa `MagicMock(spec=Military)` per aggirare il problema.

## Stato attuale

### Completezza

- **Region.py**: funzionalmente completo per le operazioni core (gestione blocchi/rotte, calcolo priorità, centri strategici, metriche aggregate). Contiene codice morto commentato (vecchie versioni di `calc_combat_power_center`, `_calc_surface_priority`, `_calc_air_priority` — righe ~448-481 e ~1057-1186) lasciato come riferimento storico, non eliminato.
- **Campaign_State.py**: completo per il proprio scopo dichiarato (snapshot + restore + persistenza JSON). Nessun placeholder o `TODO` individuato nel sorgente.
- **Target_Status_History.py**: completo per il proprio scopo (write/read/persist); non prevede restore, coerente con la sua natura di vista "bersaglio" e non di stato interno.

### Bug noti (con riferimento file:riga)

1. `Region.py:239-282` (definizione `get_blocks_by_criteria`) + `Region.py:305-306` (uso in `get_sorted_priority_blocks`) — mutazione in-place della lista restituita da un metodo `@lru_cache`, che corrompe la cache per chiamate successive con gli stessi argomenti. Vedi dettaglio sopra.
2. `Region.py:344-384` — docstring di `get_route` disallineata: dichiara di restituire un singolo `Route` ma restituisce una `List[Route]` (o `None`).
3. `Region.py:759-761` (`get_region_intelligence_efficiency`) — chiama `_get_region_average_metric(..., 'intelligence')`, ma `Military.intelligence` non è mai stato implementato (vedi Problemi aperti). In produzione la funzione non solleva eccezioni (perché `_get_region_average_metric` usa `getattr(..., None)` + `callable()`), ma restituisce sempre `0.0` — un comportamento silenzioso che potrebbe passare inosservato.
4. `Region.py:310-325` (`get_normalized_priority_blocks`) — nessun guard contro `delta == 0` (tutti i blocchi con priorità uguale) → `ZeroDivisionError` non gestita.

### Copertura test reale (eseguita in questa sessione con `.direnv/python-3.12/bin/python3 -m unittest discover ...`)

| Suite | Risultato |
|---|---|
| `Test_Region.py` | **81 test, 80 OK, 1 ERROR** (`test_get_region_intelligence_efficiency_returns_mean`, vedi Problemi aperti) |
| `Test_Campaign_State.py` | **78 test, tutti OK** |
| `Test_Target_Status_History.py` | **44 test, tutti OK** |

Totale: 203 test eseguiti, 202 passano, 1 fallisce per la causa identificata sotto.

## File orfani/riservati

### `Coalition.py` — orfano

Non importato da nessun altro file del progetto (verificato con `grep -rln "Coalition" Code/Dynamic_War_Manager/Source` → l'unico hit è il file stesso). Usa una struttura di import pre-refactoring incompatibile con l'organizzazione attuale a sottocartelle (es. `from Dynamic_War_Manager.Source.Event import Event`, `from Dynamic_War_Manager.Source.Region import Region`, `from Dynamic_War_Manager.Source.Military import Military` — mancano sia il prefisso `Code.` sia le sottocartelle `DataType`/`Context`/`Block` dell'attuale layout) e quindi **non è nemmeno importabile as-is** (fallirebbe su `ModuleNotFoundError`). Contiene:

- `class Coalition.__init__(self, side: str, blocks: Block|None)` — imposta `_side`, `_blocks`.
- `regions(self) -> list` — **corpo rotto**: assegna `regions_dict = None` ma fa `return region_dict` (nome diverso, mai definito) → solleverebbe `NameError` se mai chiamato.
- `getTacticalReport(self) -> dict` — itera `self.getBlocks(blockCategory="Military", side=self.side)` (metodo `getBlocks`/attributo `self.side` mai definiti nella classe, solo `_side`), tenta `tactical_reports[block.region][block.name] = report` senza aver mai inizializzato le chiavi annidate → solleverebbe `KeyError`/`AttributeError`.

Stato: probabile relitto storico, verosimilmente superato da `Region.py` (gestione blocchi/rotte) e `Block/Military.py` (report tattici via `get_recognition_report`). Come da indicazione dell'utente, **non se ne propone la cancellazione**; qui è documentato solo as-is.

### `Rinomina_Campaign_State.py` — riservato per riuso futuro

**L'utente ha esplicitamente richiesto di NON cancellarlo**: intende riutilizzarlo in futuro rinominandolo. Nessuna proposta di cancellazione in questo documento.

Contiene una vecchia classe `Campaign_State` (nome diverso, senza CamelCase separato, dall'attuale `CampaignState` di `Campaign_State.py`) con struttura sensibilmente diversa:

- Import da `Context.Initial_Context.ASSET_AVAILABILITY` e da `Context.Context` (`STATE`, `Ground_Action`, `Air_To_Air_Task`, `Air_To_Ground_Task`, `Sea_Task`) — dipendenze non presenti nella nuova `CampaignState`.
- `__init__` inizializza:
  - `_last_mission`, `_last_mission_date`, `_last_mission_time` — tracciamento dell'ultima missione registrata (assente nella nuova classe, che invece espone `missions` come lista ordinata).
  - `_last_asset_availability` — dict `{'air'|'ground'|'sea': {'asset_type': None, 'quantity': None}}`.
  - `_asset_availability` — dict annidato `{'date', 'time', 'mil_force': {'air','ground','sea'}}`.
  - `_global_success_mission_ratio` — struttura annidata per lato (`Red`/`Blue`) × dominio (`Air`/`Ground`/`Sea`) × task specifico (es. `Ground_Action.ATTACK.value`), pensata per tracciare il rapporto missioni riuscite/totali. **Nota strutturale**: nel dizionario per `"Blue"` manca la chiave `"Air"` esplicita — il primo valore `{"Air_To_Air": ..., "Air_To_Ground": ..., "Air_To_Sea": ...}` è posizionato come valore diretto della chiave `"Blue"` invece che sotto `"Blue"]["Air"]`, e le chiavi `"Ground"`/`"Sea"` successive nello stesso dict-literal sarebbero sintatticamente un errore se non fosse che in Python un dict-literal con chiavi duplicate (`"Ground"` compare sia per `"Red"` che come sotto-chiave orfana qui) semplicemente sovrascrive silenziosamente — la struttura per `"Blue"` risulta quindi malformata rispetto a quella per `"Red"`. Non essendo mai istanziato/usato, il difetto non ha impatto pratico ma è degno di nota per un futuro riuso.
  - `_global_damaged_asset_ratio` — dict per lato × dominio (`Air`/`Ground`/`Sea`), verosimilmente per tracciare il tasso di asset danneggiati.
  - `_state: Dict[str, Dict]` — placeholder per lo storico stato per missione/regione (mai popolato: solo l'`__init__` è implementato).
- Il file termina subito dopo `__init__` con un solo commento (`# le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)`) — **nessun metodo pubblico implementato oltre al costruttore**. Il docstring iniziale del modulo (righe 36-93) contiene però una bozza dettagliata, mai realizzata, di un dizionario `blocks_state` con campi quali `intelligence`, `combat_state`, `defense_status` (con `air_defense_volume`, `air_defense_aaa_range`, `combat_range`, `combat_volume`, `air_defense_aaa_volume`) e `supply_status` — verosimilmente il progetto originario di reporting che ha ispirato sia `Target_Status_History` (recognition report) sia i metodi placeholder oggi presenti in `Block/Military.py` (`air_defense_volume`, `combat_range`, `combat_state`).
- Verificato con grep: nessun file del progetto importa `Rinomina_Campaign_State` né la vecchia classe `Campaign_State` da questo modulo (confermato dopo la rimozione odierna di un riferimento morto in `Air_Resources_Assigner.py`, secondo quanto riportato dall'utente). È codice morto nel senso di "non eseguito", ma **conservato deliberatamente** per essere rinominato e riutilizzato in futuro.

## Problemi aperti

### Investigazione: `Test_Region.py::test_get_region_intelligence_efficiency_returns_mean` — esito

**Confermato con esecuzione diretta**:
```
.direnv/python-3.12/bin/python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Region.TestRegionMetrics.test_get_region_intelligence_efficiency_returns_mean
```
```
AttributeError: Mock object has no attribute 'intelligence'
  File ".../Test_Region.py", line 633, in test_get_region_intelligence_efficiency_returns_mean
    self.mil1.intelligence.return_value = 0.9
```

**Causa radice**: in `Test_Region.py` (metodo `_make_military`, righe ~478) i doppi di `Military` sono creati con `MagicMock(spec=Military)`. Con `spec=`, `MagicMock` limita gli attributi accessibili a quelli realmente presenti sulla classe reale. In `Block/Military.py`, un metodo `intelligence()` è stato **abbozzato ma esplicitamente lasciato commentato** (righe 510-513):
```python
# Non serve: c'è c2 efficiency, che è più specifico e pertinente per valutare la capacità di comando e controllo del blocco.
#def intelligence(self) -> None:
#    """Calculate intelligence level (to be implemented)."""
#    pass
```
Il commento indica una decisione di design deliberata: l'autore ha giudicato `get_c2_efficiency()` (già implementato e testato in `Military.py:440-452`) più pertinente e ha rinunciato a implementare `intelligence()` separatamente.

**Verdetto**: è il caso **(a) drift del test** — non manca un'implementazione dimenticata, ma un test scritto contro un'interfaccia (`intelligence()`) che è stata intenzionalmente scartata a favore di `get_c2_efficiency()`, mentre sia il test sia il metodo produttivo `Region.get_region_intelligence_efficiency` (che chiama `_get_region_average_metric(side, ..., 'intelligence')`, `Region.py:759-761`) non sono stati aggiornati di conseguenza. In produzione questo non causa un crash (perché `_get_region_average_metric` usa `getattr(obj, method_name, None)` con guard `callable()`, quindi su un `Military` reale — che non ha `intelligence` — la chiamata restituisce silenziosamente `0.0`), ma significa che `get_region_intelligence_efficiency` è **funzionalmente morto**: restituirà sempre `0.0` per qualunque configurazione di blocchi Military reali, finché non si decide (a) di implementare `Military.intelligence()`, oppure (b) di eliminare/reindirizzare `get_region_intelligence_efficiency` verso `get_c2_efficiency` come suggerito dal commento in `Military.py`, aggiornando di conseguenza sia `Region.py:759-761` sia il test. Questa decisione di design spetta al proprietario del sottosistema `Block` (Military.py non è nello scope di questa analisi) — qui si segnala solo l'incoerenza.

### Altri problemi aperti

- **Mutazione della cache LRU in `get_sorted_priority_blocks`** (`Region.py:305-306`, vedi sopra) — bug funzionale non coperto da test, da correggere restituendo una copia (`list(blocks)`) prima di ordinare, oppure ordinando con `sorted(...)` invece di `.sort()` in-place.
- **`get_route` — docstring disallineata dal comportamento reale** (restituisce lista, non singolo oggetto) — rischio di uso scorretto da parte di futuri chiamanti che si fidino della docstring.
- **`RegionParams` inutilizzata** — dataclass morta, da valutare se rimuovere o effettivamente adottare come validatore dei parametri di `__init__`.
- **Accoppiamento implicito di `Campaign_State.py` e `Target_Status_History.py` ai nomi di attributo privati** di `Block`/`Asset`/`Route`/`State`/`Resource_Manager` (tramite `getattr(obj, '_xxx', None)`) — un refactoring dei nomi interni in quei moduli romperebbe silenziosamente (nessuna eccezione, solo dati mancanti/`None`) la serializzazione, senza che i test di `Campaign_State`/`Target_Status_History` (che usano stub controllati) se ne accorgano necessariamente.
- **`Coalition.py`** contiene almeno due bug bloccanti (`regions()` referenzia una variabile mai definita; `getTacticalReport()` usa attributi/metodi mai definiti sulla classe) oltre a import non risolvibili nell'attuale struttura a sottocartelle — se in futuro si decidesse di recuperarlo andrebbe sostanzialmente riscritto, non solo corretto negli import.
- **`Rinomina_Campaign_State.py`** — la struttura `_global_success_mission_ratio` per il lato `"Blue"` è malformata (chiavi annidate mancanti/sovrascritte, vedi sopra); da correggere se/quando il file verrà recuperato e rinominato.
