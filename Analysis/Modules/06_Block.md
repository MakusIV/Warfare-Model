# Block — Unità Economico-Militari

## Scopo

Il sottosistema `Block` rappresenta le unità territoriali/logistiche che compongono una `Region` nella campagna: basi militari, impianti produttivi, magazzini, nodi di trasporto e centri urbani. Ogni `Block` possiede un insieme di `Asset` (veicoli, navi, aerei, strutture), un `Resource_Manager` per la gestione economica, uno `State` per salute/successo, e produce report di ricognizione (`get_recognition_report`) usati dal resto del modello (in particolare da `Region`) per calcolare metriche aggregate (morale, efficienza C2, efficienza di ricognizione, ecc.).

`Military` è la specializzazione con capacità di combattimento (potenza di fuoco, portata di tiro, difesa aerea, tempo di attacco). `Production`, `Storage`, `Transport`, `Urban` dovrebbero essere le altre specializzazioni (economica, logistica, civile) ma — come emerso dall'analisi — sono stub non funzionanti.

## File inclusi

| File | Righe | Stato |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Block/Block.py` | 735 | Implementato e testato |
| `Code/Dynamic_War_Manager/Source/Block/Military.py` | 570 | Implementato e testato, con bug residui |
| `Code/Dynamic_War_Manager/Source/Block/Production.py` | 45 | Stub non funzionante |
| `Code/Dynamic_War_Manager/Source/Block/Storage.py` | 45 | Stub non funzionante |
| `Code/Dynamic_War_Manager/Source/Block/Transport.py` | 46 | Stub non funzionante |
| `Code/Dynamic_War_Manager/Source/Block/Urban.py` | 45 | Stub non funzionante |
| `Code/Dynamic_War_Manager/Source/Block/__init__.py` | 0 | vuoto |

Diagrammi UML: `Analysis/UML/Block.plantuml`, `Analysis/UML/Military.plantuml` (entrambi presenti, ma **`Military.plantuml` è disallineato rispetto al codice attuale** — vedi Problemi aperti).

## Classi e funzioni principali

### `Block.py`

- **`BlockParams`** (dataclass, righe 46-56): contenitore di parametri per validazione; non risulta usato nel codice corrente (nessun riferimento a `BlockParams(...)` nel file), sembra vestigiale.
- **`Block.__init__(name, description, side, category, sub_category, functionality, value, region)`** (righe 66-119): inizializza id/nome via `setName`/`setId`, crea `State("Block", id)` e `Resource_Manager(block=self)`, valida i parametri con `_validate_params`. `value` è vincolato in `[MIN_VALUE=1, MAX_VALUE=10]`.
- Property standard con getter/setter validati: `name`, `id`, `description`, `side`, `category`, `sub_category`, `functionality`, `value`, `state`, `resource_manager`, `region`, `events`, `assets`.
- **`assets` setter** (righe 341-348): valida che tutti i valori siano istanze `Asset` tramite `validate_class` (basato su nome di classe MRO — funziona anche con stub/mock che impostano `__class__`).
- **`set_asset(key, asset)`** (righe 361-368): comportamento sorprendente — il controllo di tipo qui **non** usa `validate_class` come il setter di `assets`, ma un controllo diretto `asset.__class__.__name__ != 'Asset'`. Con oggetti `Vehicle`/`Ship`/`Aircraft` (sottoclassi di `Asset`), questo controllo fallirebbe se preso alla lettera; nei test la validazione passa perché gli stub/mock impostano `__class__` in modo mirato. Da verificare in fase di integrazione con le sottoclassi reali di `Asset`.
- **`position`** (righe 411-417): centroide (`mean_point`) delle posizioni degli asset non-`None`; `None` se nessun asset ha posizione.
- **`morale`** (righe 419-434): usa `evaluateMorale(mean_success_ratio, efficiency)`; ritorna `0.0` se non ci sono asset o se success_ratio/efficiency ≤ 0.
- **`efficiency`** (righe 436-442): media (`numpy.mean`) delle efficienze di tutti gli asset (nessun filtro `is_operative`).
- **`is_military()` / `is_logistic()` / `is_civilian()`** (righe 452-462): confronto diretto su `self._category` contro `BLOCK_CATEGORY`.
- **`enemy_side()`** (righe 467-474): **deprecato** (`DeprecationWarning`), redirige a `enemySide()` di `Utility`.
- **`get_recognition_report(region_c2_recon_efficiency=None)`** (righe 489-735): il metodo più complesso del modulo. Calcola probabilità di rilevamento per ciascun campo del report (`calcProbability`) pesate dall'efficienza C2/ricognizione della regione, poi filtra/oscura i dati non "rilevati" (restituendo `None`). Include:
  - classificazione dimensionale (`Big/Medium/Small`) per asset `Vehicle/Ship/Structure` via `get_dimension()` e per `Aircraft` via categoria (`Fighter/Helicopter/Attacker`→Small, `Fighter_Bomber/Recon`→Medium, `Bomber/Transport/Awacs/Tanker/Heavy_Bomber`→Big).
  - conteggio asset operativi/danneggiati/distrutti per tipo×dimensione.
  - campo **`'intelligence': self.intelligence() if hasattr(self, 'intelligence') else None`** (righe 514 e 708) — vedi sezione Problemi aperti: nessuna sottoclasse implementa `intelligence()`, quindi questo campo è **sempre `None`** in pratica.
  - Un ampio blocco di docstring (righe 496-589) contiene una **versione duplicata/vecchia** della struttura dati come commento — non più sincronizzata col dizionario `target_report` reale costruito più sotto (es. la versione in docstring usa `self.air_defense()`/`self.defense_aa_range()`/`self.combat_volume()`/`self.defense_aa_volume()`, mentre il codice reale usa `self.air_defense_volume()`/`self.air_defense_aaa_range()`/`self.combat_volume()`/`self.air_defense_aaa_volume()`). Da ripulire.
  - `hasattr(self, 'combat_volume')`, `hasattr(self, 'air_defense_aaa_range')`, `hasattr(self, 'air_defense_aaa_volume')` sono referenziati ma **nessuno di questi tre metodi è definito** né in `Block` né in `Military` — quindi questi tre campi del report sono sempre `None` (nessun crash, grazie a `hasattr`, ma funzionalità mai implementata).

### `Military.py` (estende `Block`)

- **`__init__(mil_category, name, side, description, category, sub_category, functionality, value, region)`** (righe 52-91): prefissa il nome con `"Military."`, valida `mil_category` contro l'unione di tutti i valori di `MILITARY_CATEGORY` (`Ground_Base`, `Air_Base`, `Naval_Base`).
- **`get_asset_list(asset_class, asset_type, asset_state)`** (righe 121-175): filtro combinato per classe/tipo/stato asset, ritorna dict annidato `{classe: {tipo: [asset,...]}}`; ritorna `None` (con `logger.warning`) se un filtro non è valido.
- **`combat_power(force, action)`** (righe 177-210): **la firma/docstring dichiara un `float`** ("Total combat power of applicable assets") e anche il diagramma UML lo descrive come `float`, ma il valore restituito è in realtà un **dizionario annidato completo** `{force: {task: valore, ...}, ...}` per tutte le `MILITARY_FORCES`/`ACTION_TASKS`, con solo la cella `[force][action]` effettivamente popolata (le altre restano a `0.0`). Il chiamante deve quindi accedere con `combat_power(...)[force][action]`. I test (`Test_Military.py:167-197`) confermano che questo è il comportamento atteso/testato, ma la documentazione (docstring + UML) è fuorviante.
- **`get_military_category()`** (righe 212-228) — **BUG confermato**: le tre condizioni usano `self.is_Air_Base`, `self.is_Ground_Base`, `self.is_Naval_Base` **senza parentesi** (righe 221/223/225), quindi valutano sempre l'oggetto *bound method* (sempre truthy) invece di chiamare il metodo. Risultato: la funzione ritorna **sempre `"Naval_Base"`** indipendentemente dalla reale categoria del blocco (l'ultimo `if` sovrascrive i precedenti). Verificato empiricamente:
  ```
  m = Military(mil_category='Airbase', ...)
  m.get_military_category()  # → 'Naval_Base'  (atteso: 'Air_Base')
  ```
  Nessun test copre `get_military_category()` (assente da `Test_Military.py`), quindi il bug non è mai stato rilevato. Questo si propaga a `Block.get_recognition_report()`, che chiama `self.get_military_category()` quando disponibile — quindi ogni report di ricognizione di un blocco `Military` riporta `military_category: "Naval_Base"` a prescindere dal tipo reale di base.
- **`is_Air_Base()` / `is_Ground_Base()` / `is_Naval_Base()`** (righe 231-241): implementazione corretta (con parentesi quando chiamati altrove, es. in `_is_attack_asset`), verificano appartenenza di `self._mil_category` alla tupla `MILITARY_CATEGORY[...]`.
- **`artillery_in_range(target_point)`** (righe 245-282) e **`_get_artillery_stats()`** (righe 284-310): usa `asset.combat_range()` filtrando per categoria — `Vehicle` con categoria in `{ARTILLERY_FIXED, ARTILLERY_SEMOVENT, TANK}`, `Ship` con categoria in `{CORVETTE, CRUISER, DESTROYER, FRIGATE}` (tutte confrontate correttamente con `.value`, coerente con la nota del 2026-05-22). **Verificato leggendo il codice attuale: confermato ancora valido.**
- **`time2attack(target, route, speed)`** (righe 349-358): dispatcher basato su `is_Air_Base`/`is_Ground_Base` — **stesso pattern di bug potenziale**: righe 354 e 357 usano `self.is_Air_Base and target` / `elif self.is_Ground_Base and route` **senza parentesi**. Essendo sempre truthy, il ramo `is_Air_Base` (riga 354) viene sempre scelto per primo se `target` è valorizzato, indipendentemente dal tipo di base — stesso difetto di `get_military_category()`. Nessun test copre questo dispatch per basi non-Air (`Test_Military.py` testa solo `test_time_to_direct_line_attack`, riga 443, non `time2attack` stesso).
- **`_is_attack_asset(asset)`** (righe 397-408) — **BUG confermato**: il terzo ramo `elif self.is_helibase() and validate_class(asset, "Aircraft")` (riga 403) chiama un metodo **`is_helibase()` mai definito** né in `Military` né in `Block`. Per un blocco `Naval_Base` (dove `is_Ground_Base()` e `is_Air_Base()` sono entrambi `False`), la valutazione di questo `elif` solleva `AttributeError: 'Military' object has no attribute 'is_helibase'` — verificato empiricamente:
  ```
  m = Military(mil_category='Port', ...)   # Naval_Base
  m._is_attack_asset(qualunque_asset)      # → AttributeError
  ```
  Questo rende `_get_attack_speeds()` (e quindi `time_to_direct_line_attack()`/`time2attack()`) **non utilizzabile per basi navali** con qualsiasi asset presente nel blocco. Nessun test in `Test_Military.py` copre `_is_attack_asset`/`_get_attack_speeds` per `Naval_Base`, quindi il bug non è mai stato rilevato dalla suite.
- **`get_recon_efficiency()`** (righe 424-437): sovrascrive quello di `Block` — usa `median` invece di `mean`, e filtra per `asset.role == Asset_Role.RECONNAISSANCE.value` invece che per `asset.category == "Reconnaissance"` (comportamento di `Block`). Le due implementazioni (base e derivata) sono quindi semanticamente diverse.
- **`get_c2_efficiency()`** (righe 440-452): mediana delle efficienze degli asset con `role == Asset_Role.C2.value`, filtrati per `is_operative()`. Confermato valido leggendo il codice attuale.
- **`air_defense_volume() → List[Cylinder]`** (righe 455-475): delega a `Mobile.air_defense_volume()` su ogni `Vehicle`/`Ship` operativo; esclude asset senza il metodo o che restituiscono `None`. Confermato valido.
- **`combat_range() → Optional[Tuple[max_range, med_range, ratio, quantity]]`** (righe 477-508): itera tutti gli asset operativi con metodo `combat_range`; ritorna `None` se nessuna portata trovata. Confermato valido.
- **`combat_state() → Optional[float]`** (righe 515-543): formula `(0.3 * operative_efficiency + 0.7 * c2_efficiency) * ratio_operative`, `None` se nessun asset. Confermato valido, corrisponde esattamente alla formula in memoria.
- **`intelligence()`** — **non implementato**: righe 510-513 contengono solo un metodo **commentato**:
  ```python
  # Non serve: c'è c2 efficiency, che è più specifico e pertinente per valutare la capacità di comando e controllo del blocco.
  #def intelligence(self) -> None:
  #    """Calculate intelligence level (to be implemented)."""
  #    pass
  ```
  Vedi sezione Problemi aperti per l'impatto su `Region`.
- **`get_recognition_report()`** (righe 547-569): override "vuoto" — aggiorna lo `state` e poi delega interamente a `super().get_recognition_report(...)`; nessuna logica aggiuntiva specifica per `Military` nonostante il commento al codice (riga 566) suggerisca che dovrebbe arricchire il report.

### `Production.py`, `Storage.py`, `Transport.py`, `Urban.py`

**Tutti e quattro i file sono stub identici nella struttura e non funzionanti.** Firma tipica (es. `Production.__init__`):

```python
def __init__(self, block: Block, mil_category: str, name: str|None, side: str|None,
             description: str|None, category: str|None, sub_category: str|None,
             functionality: str|None, value: int|None, acp: Payload|None,
             rcp: Payload|None, payload: Payload|None, region: Region|None):
    super().__init__(name, description, side, category, sub_category, functionality, value, acp, rcp, payload)
    ...
    check_results = self.checkParam(mil_category)
    if not check_results[1]:
        raise Exception(...)
```

Problemi verificati per istanziazione diretta:
1. **`super().__init__(...)` passa 10 argomenti posizionali** (`name, description, side, category, sub_category, functionality, value, acp, rcp, payload`) all'attuale `Block.__init__`, che accetta solo 8 parametri dopo `self` (`name..value, region`) — **`TypeError` immediato**. Verificato empiricamente:
   ```
   TypeError: Block.__init__() takes from 1 to 9 positional arguments but 11 were given
   ```
2. Anche risolvendo (1), il codice chiama **`self.checkParam(mil_category)`**, metodo mai esistito né in `Block` né in queste classi (esiste solo `_validate_params` in `Block`) — `AttributeError` immediato dopo il fix di (1).
3. Il parametro `block` (primo argomento del costruttore) non viene mai assegnato a `self` — sembra un residuo di una vecchia firma "composition over inheritance" mai completata.
4. `region` è dichiarato come parametro ma non passato a `super().__init__()` — verrebbe perso, il blocco non avrebbe mai una `Region` associata anche corrigendo (1).

**Nessun file di test esiste** per `Production`, `Storage`, `Transport`, `Urban` (verificato: `find ... -iname "*Production*" -o -iname "*Storage*" -o -iname "*Transport*" -o -iname "*Urban*"` in `Test/` non produce risultati). Ultimo commit che tocca questi 4 file: `a695fca6` ("debugging Resource_Manager...", 29 maggio 2025) — oltre un anno fa, mai più toccati da allora nonostante `Block.py`/`Military.py` abbiano ricevuto refactoring sostanziali nel frattempo (es. rimozione di `Vehicle`/`Ship`/`Aircraft` dagli import diretti). Questi 4 moduli sono con ogni evidenza **codice abbandonato/pre-refactoring**, incompatibile con l'attuale `Block.__init__`.

## Dipendenze

- `Component/Resource_Manager.py` (composizione 1:1 in `Block`)
- `Utility/Utility.py`: `validate_class`, `setName`, `setId`, `mean_point`, `evaluateMorale`, `enemySide`, `calcProbability`
- `Utility/LoggerClass.py`: `Logger`
- `DataType/Event.py`, `DataType/State.py`, `DataType/Payload.py` (import presente in `Block.py` ma **`Payload` non risulta usato** nel corpo della classe — probabile import residuo)
- `Context/Context.py`: `BLOCK_CATEGORY`, `SIDE`, `Ground_Vehicle_Asset_Type`, `Sea_Asset_Type`, `Air_Asset_Type`, `get_dimension`, `GROUND_ACTION`, `AIR_TASK`, `SEA_TASK`, `MILITARY_CATEGORY`, `MILITARY_FORCES`, `ACTION_TASKS`, `Asset_Role`
- `DataType/Route.py` (usato da `Military.time_to_ground_intercept`)
- Solo `TYPE_CHECKING`: `Asset`, `Region` (in `Block.py`); `Region`, `Vehicle`, `Aircraft`, `Ship`, `Asset` (in `Military.py`)
- Librerie esterne: `numpy` (`mean`, `median`), `sympy` (`Point`, `Point2D`, `Point3D`), `heapq` (importato in `Military.py` ma **non utilizzato** nel corpo del file — `heappop`/`heappush` non compaiono altrove)

**Verifica import circolare (richiesta esplicita)**: confermato che `Block.py` **non importa più** `Vehicle`/`Ship`/`Aircraft` direttamente — l'unico import relativo a queste classi è sotto `if TYPE_CHECKING:` (righe 23-25), quindi non genera dipendenza a runtime. `Military.py` segue lo stesso pattern (righe 24-29). La sessione precedente che ha rimosso questi import ha quindi risolto il problema per questi due file specifici (il resto della catena circolare `Aircraft → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft` documentata in memoria resta un problema di altri moduli, non di `Block`).

## Stato attuale

| File | Stato | Copertura test |
|---|---|---|
| `Block.py` | Completo e funzionante per l'uso attuale | `Test_Block.py`: **95 test, tutti OK** |
| `Military.py` | Funzionante per i percorsi testati; bug residui su percorsi non testati (basi navali, `get_military_category`) | `Test_Military.py`: **83 test, tutti OK** |
| `Production.py` | Non funzionante (stub pre-refactoring) | Nessun test |
| `Storage.py` | Non funzionante (stub pre-refactoring) | Nessun test |
| `Transport.py` | Non funzionante (stub pre-refactoring) | Nessun test |
| `Urban.py` | Non funzionante (stub pre-refactoring) | Nessun test |

Comando eseguito e confermato in questa sessione:
```
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Block.py"
→ Ran 95 tests in 0.129s — OK

.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Military.py"
→ Ran 83 tests in 0.158s — OK
```

### Bug noti (con file:riga)

1. **`Military.py:221-226`** — `get_military_category()` usa `self.is_Air_Base` / `self.is_Ground_Base` / `self.is_Naval_Base` senza chiamarli (mancano le parentesi `()`); il metodo ritorna sempre `"Naval_Base"`. Verificato empiricamente. Nessun test lo copre. Impatta `Block.get_recognition_report()` (campo `military_category` sempre errato per basi non navali).
2. **`Military.py:403`** — `_is_attack_asset()` chiama `self.is_helibase()`, metodo mai definito. Provoca `AttributeError` per qualsiasi blocco `Naval_Base` non appena si valuta un asset (indipendentemente dal tipo dell'asset). Impatta `_get_attack_speeds()`, `time_to_direct_line_attack()`, `time2attack()` per basi navali.
3. **`Military.py:354,357`** — `time2attack()` usa `self.is_Air_Base` / `self.is_Ground_Base` senza parentesi (stesso pattern del bug #1); il ramo `is_Air_Base` viene selezionato sempre per primo se `target` è valorizzato, a prescindere dal tipo di base reale. Non testato direttamente.
4. **`Military.py:177-210`** — `combat_power()`: firma/docstring/UML dichiarano `float`, il valore ritornato è in realtà un dizionario annidato `{force: {task: float}}`. Comportamento testato/intenzionale ma documentazione fuorviante.
5. **`Block.py:514,708` / `Military.py`** — campo `'intelligence'` del report di ricognizione sempre `None` perché nessuna classe implementa `intelligence()` — vedi Problemi aperti.
6. **`Block.py:583,732` (e docstring 496-589)** — riferimenti a `combat_volume`, `air_defense_aaa_range`, `air_defense_aaa_volume`: nessuno di questi tre metodi è implementato in `Block` o `Military`; i campi risultanti nel report sono sempre `None` (nessun crash grazie a `hasattr`, ma funzionalità dichiarata e mai realizzata).
7. **`Production.py`/`Storage.py`/`Transport.py`/`Urban.py`** — non istanziabili: `TypeError` da `super().__init__()` con troppi argomenti posizionali (verificato empiricamente), seguito da `AttributeError` su `self.checkParam(...)` (metodo inesistente) se il primo errore venisse corretto.
8. **`Block.py:365`** — `set_asset()` valida il tipo con `asset.__class__.__name__ != 'Asset'` invece di `validate_class(asset, "Asset")` come fa il setter `assets` (righe 341-348); le due vie di inserimento asset nel blocco usano criteri di validazione diversi e potenzialmente incoerenti con le sottoclassi reali (`Vehicle`, `Ship`, `Aircraft`, `Structure`).

## Problemi aperti

- **Verifica esplicita richiesta — attributo/metodo `intelligence` su `Military`**: **confermato che non esiste**. In `Military.py` (righe 510-513) è presente solo una definizione **commentata**:
  ```python
  # Non serve: c'è c2 efficiency, che è più specifico e pertinente per valutare la capacità di comando e controllo del blocco.
  #def intelligence(self) -> None:
  #    """Calculate intelligence level (to be implemented)."""
  #    pass
  ```
  cioè lo sviluppatore ha deliberatamente scelto di **non implementarlo**, ritenendo `get_c2_efficiency()` sufficiente/più pertinente. Tuttavia `Context/Region.py:759-761` espone ancora:
  ```python
  def get_region_intelligence_efficiency(self, side: str) -> float:
      """Calculate the region's intelligence efficiency for a side."""
      return self._get_region_average_metric(side, BlockCategory.MILITARY.value, 'intelligence')
  ```
  che tenta di chiamare `getattr(block, 'intelligence', None)` per ogni blocco militare della regione. Nel codice di produzione questo è **innocuo** (usa `getattr(..., None)` + `callable()`, quindi ritorna semplicemente `0.0` se il metodo manca). **Ma il test `Test_Region.py::TestRegionMetrics::test_get_region_intelligence_efficiency_returns_mean` (riga 631-635) fallisce** con:
  ```
  AttributeError: Mock object has no attribute 'intelligence'
  ```
  Causa: il test usa `MagicMock(spec=Military)` (riga 478/496 area di `Test_Region.py`) — con `spec=`, `MagicMock` limita gli attributi accessibili a quelli realmente presenti sulla classe `Military`; poiché `intelligence` non esiste su `Military`, l'assegnazione `self.mil1.intelligence.return_value = 0.9` solleva `AttributeError`. Verificato empiricamente eseguendo il singolo test:
  ```
  .direnv/python-3.12/bin/python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Region.TestRegionMetrics.test_get_region_intelligence_efficiency_returns_mean
  → AttributeError: Mock object has no attribute 'intelligence'
  ```
  **Diagnosi per il documento Region/Context**: il fallimento non è un bug di `Region.py` in sé (la sua logica difensiva con `getattr`/`callable` è corretta e non solleverebbe mai `AttributeError` in produzione), ma una **feature mancante in `Military`**: `intelligence()` non è mai stato implementato (deliberatamente, secondo il commento), e il test associato in `Test_Region.py` presuppone erroneamente che lo sia. Le opzioni sono: (a) implementare `Military.intelligence()` con una formula dedicata, (b) rimuovere `get_region_intelligence_efficiency()` da `Region.py` e il test corrispondente se si conferma che `get_c2_efficiency` la sostituisce concettualmente, o (c) far usare a `get_region_intelligence_efficiency()` il nome di metodo `'get_c2_efficiency'` invece di `'intelligence'` se sono concettualmente equivalenti.

- **UML `Military.plantuml` disallineato col codice**: il diagramma di classe (sezione "Stubs (to be implemented)", righe 126-132) elenca `air_defense()`, `combat_range()`, `defense_aa_range()`, `combat_volume()`, `intelligence()`, `combat_state()` come tutti da implementare/ritornanti `None`. Nella realtà `air_defense_volume()`, `combat_range()` e `combat_state()` **sono già implementati e testati** (aggiornamento 2026-05-22, non riflesso nel diagramma); solo `intelligence()`, `combat_volume()`, `defense_aa_range()`(rinominato `air_defense_aaa_range` nel codice) restano non implementati. Il diagramma andrebbe rigenerato/aggiornato.
- **Duplicazione/incoerenza nella docstring di `Block.get_recognition_report()`** (righe 496-589 vs. codice reale 690-735): la struttura dati documentata in commento non corrisponde più esattamente a quella prodotta (nomi di metodo diversi per i campi `defense_status`). Da ripulire per evitare confusione futura.
- **`Production`/`Storage`/`Transport`/`Urban` da riscrivere da zero o rimuovere**: sono stub abbandonati, incompatibili con l'attuale `Block.__init__`, senza test, e riferiscono un metodo (`checkParam`) mai esistito nella codebase attuale. Va deciso se questi sottotipi di blocco sono ancora nella roadmap (in tal caso vanno riscritti seguendo il pattern di `Military.py`) o se vanno rimossi/marcati come `NotImplemented` espliciti.
- **`BlockParams` dataclass** (`Block.py:46-56`) risulta non referenziata nel resto del codice — verificare se è pensata per un uso futuro (es. validazione strutturata in ingresso) o se è codice morto da rimuovere.
- **Import inutilizzati residui**: `Payload` in `Block.py` (riga 13) e `heapq.heappop`/`heappush` in `Military.py` (riga 3) risultano importati ma mai usati nel corpo dei rispettivi file — pulizia minore consigliata.
