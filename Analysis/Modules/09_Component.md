# Component — Gestione Risorse

## Scopo

`Resource_Manager` è il componente che ogni `Block` possiede (relazione 1:1, istanziata direttamente in `Block.__init__`) per governare il ciclo economico locale del blocco: **produzione** delle risorse generate dagli `Asset` assegnati, **auto-consumo** delle risorse necessarie al proprio funzionamento, e **ridistribuzione** verso altri blocchi collegati come "client" secondo una logica di priorità strategica/tattica letta dalla `Region`.

È quindi il modulo che implementa concretamente l'obiettivo di progetto relativo a "produzione e ridistribuzione dei rifornimenti": ogni blocco produce risorse tramite i propri asset, le consuma per l'autosostentamento (con una logica di razionamento basata sull'autonomia residua), e — se ha capacità eccedente — le smista verso i blocchi che dipendono da esso, in proporzione alla loro priorità nella regione. Un blocco può essere sia "server" (fornitore) per altri blocchi client, sia "client" di un proprio server, con riferimenti bidirezionali mantenuti in modo coerente.

## File inclusi

- `Code/Dynamic_War_Manager/Source/Component/Resource_Manager.py` (570 righe) — unico file del sottosistema: classe `Resource_Manager` (righe 36–571) e dataclass ausiliaria `Resource_Manager_Params` (righe 29–34)
- `Code/Dynamic_War_Manager/Source/Test/Test_Resource_Manager.py` (400 righe) — suite di test con fixture `MockBlock`/`MockPayload` proprie (non importa `Block` reale)
- `Analysis/UML/Resource_Manager.plantuml` (273 righe) — 4 diagrammi: component/dependency, class diagram, activity diagram di `run_management_cycle()`, sequence diagram di `delivery()`

(Nota: `Resource_Manager old.py`, versione pre-refactoring, è già stata rimossa dal repository — non esiste più.)

## Classi e funzioni principali

### `Resource_Manager_Params` (dataclass, righe 29–34)
Contenitore dati per la validazione dei parametri: `clients: Optional[Dict[str, Block]]`, `server: Optional[Dict[str, Block]]`, `warehouse: Optional[Payload]`. Non risulta usato direttamente nel corpo della classe `Resource_Manager` (la validazione è fatta con metodi `_validate_*` separati) — sembra un artefatto di design non completamente integrato.

### `Resource_Manager.__init__(block, clients=None, server=None, warehouse=None)` (righe 53–81)
- Solleva `ValueError` se `block is None`.
- Valida tutti i parametri con `_validate_all_params`.
- **Riga 71**: `self._id = f"Resource_Manager_{block.id}_{block.name}"` — costruisce l'id combinando `block.id` e `block.name` (vedi sezione bug dedicata).
- Inizializza `_clients`/`_server` come dict vuoti se non forniti, `_warehouse` come `Payload()` vuoto se non fornito.
- `_resources_to_self_consume` e `_resources_needed` sono `None` (lazy loading), `_actual_production` è un `Payload()` vuoto.

### Proprietà principali
- `block` (get/set) — set invalida la cache risorse (`_invalidate_resource_cache`).
- `warehouse` (get/set) — magazzino risorse del blocco (oggetto `Payload`); il setter valida il tipo e invalida la cache.
- `resources_needed` (lazy) — richiama `_evaluate_effective_resources_needed()` la prima volta e mette in cache.
- `resources_to_self_consume` (lazy) — richiama `_evaluate_resources_to_self_consume()` la prima volta e mette in cache.
- `actual_production` — ritorna `_actual_production`, aggiornato solo da `produce()`.
- `production_value` (righe 125–140) — indice sintetico ponderato della produzione attuale: somma di `actual_production[item] * Context.PRODUCTION_WEIGHT[item]` per ogni item di `PAYLOAD_ATTRIBUTES`, diviso per la somma dei pesi (`Context.PRODUCTION_WEIGHT` in `Context/Context.py:266-273`: goods=6, energy=8, hr=1, hc=10, hs=6, hb=3, totale=34). Ritorna `0.0` se la produzione attuale è vuota/nulla. Solleva `ValueError` se la somma dei pesi è 0.

### Gestione Server (righe 149–216) — questo blocco come *client* di un altro
- `server` (get/set), `list_server_keys()`, `get_server(key)`.
- `set_server(key, server)`: aggiunge/aggiorna un server; verifica che `server.has_resource_manager()`, poi imposta il riferimento **bidirezionale** chiamando `server.resource_manager.set_client(self.block.id, self.block)`. In caso di eccezione fa rollback (`del self._server[key]`) e rilancia `RuntimeError`.
- `remove_server(key)`: rimuove un server esistente; solleva `KeyError` se la chiave non esiste; chiama `deleted_server.resource_manager.remove_client(self.block.id)` per mantenere coerenza bidirezionale; solleva `RuntimeError` se il server non ha più un resource manager (situazione anomala).

### Gestione Client (righe 218–285) — questo blocco come *server* per altri
- `clients` (get/set), `list_client_keys()`, `get_client(key)`.
- `set_client(key, client)`: **normalmente invocato automaticamente da `set_server` del client**, non direttamente. Verifica che il client abbia un resource manager e che il riferimento bidirezionale sia coerente (`client_rm.get_server(self.block.id) != self.block` → `ValueError`).
- `remove_client(key)`: analogo, con lo stesso controllo di coerenza; solleva `KeyError` se la chiave non esiste.

### Operazioni sulle risorse (righe 287–450)
Ordine dichiarato nel codice: **I - consume(), II - produce(), III - delivery() (usa receive)**.

- **`consume() -> bool`** (righe 293–319): preleva da `_warehouse` la quantità pari a `resources_to_self_consume`. Se il magazzino è insufficiente (`self._warehouse < resources_needed`) logga un warning e ritorna `False` senza modificare nulla. Se ha successo, sottrae dal magazzino, logga info, invalida la cache e ritorna `True`. Tutte le eccezioni interne sono catturate e loggate come errore, ritornando `False`.
- **`receive(payload) -> bool`** (righe 321–347): riceve un `Payload` (tipicamente da un server) e lo somma al magazzino (`self._warehouse += payload`). Valida il tipo del payload; solleva `ValueError` se il warehouse non è impostato. Cattura le eccezioni e ritorna `False` in caso di errore (incluso passare un payload di tipo non valido, come testato con una stringa).
- **`delivery() -> Dict[str, bool]`** (righe 349–410): distribuisce le risorse disponibili ai client in base alla priorità:
  1. Calcola `clients_priority` con `_evaluate_clients_priority()`.
  2. `total_priority = sum(clients_priority.values())`.
  3. Per ciascun client: `priority_ratio = client_priority / total_priority`; `max_delivery = available_resources * priority_ratio`; la consegna effettiva per ciascun parametro (`RESOURCE_PARAMS`) è il **minimo** fra la richiesta del client (`client.resource_manager.resources_needed`) e la quota massima assegnata (`max_delivery`).
  4. Chiama `client.resource_manager.receive(actual_delivery)`; se ha successo sottrae la quantità consegnata sia da `self._warehouse` sia da `available_resources` (variabile locale di lavoro, copia del warehouse a inizio ciclo).
  5. Ritorna un dizionario `{client_id: bool}` con l'esito per ciascun client. Client senza priorità valida vengono segnalati con `False` e loggati come warning.
  - Solleva `ValueError` se `resources_to_self_consume` o `warehouse` non sono impostati (falsy) prima di iniziare.
- **`produce() -> Dict[str, Optional[bool]]`** (righe 412–430): resetta `_actual_production` a `Payload()` vuoto, poi itera su `self.block.assets`; per ciascun asset chiama `asset.get_production()` e per ogni item di `PAYLOAD_ATTRIBUTES` con valore positivo somma sia al `warehouse` sia a `_actual_production`, segnando `results[item] = True`; altrimenti `False`. Nota: l'efficienza dell'asset è già applicata a monte, dentro `asset.get_production()` (commentato esplicitamente nel codice).
- **`run_management_cycle() -> Dict[str, Optional[bool]]`** (righe 432–450): orchestratore che esegue in sequenza `consume()`, `produce()`, `delivery()` e ne aggrega i risultati in un unico dizionario `{'consume':…, 'produce':…, 'delivery':…}`.

### Metodi privati di calcolo (righe 452–514)
- `_evaluate_resources_to_self_consume()`: somma `asset.resources_to_self_consume` su tutti gli asset del blocco (se l'attributo esiste ed è valorizzato). Ritorna `Payload()` vuoto se il blocco non ha asset.
- `_evaluate_effective_resources_needed()`: calcola l'autonomia come `warehouse.division(resources_to_consume)` e applica un moltiplicatore per parametro in base a soglie di autonomia (vedi sotto). Ritorna `Payload()` se manca consumo o magazzino.
- `_get_autonomy_multiplier(autonomy_value)`: usa `AUTONOMY_THRESHOLDS` — `[0,2)→1.0`, `[2,3)→0.5`, `[3,5)→0.25`, `[5,∞)→0.1`; default `0.1` se nessuna soglia combacia. Logica: più il blocco ha autonomia (scorte rispetto al consumo), meno "richiede" risorse aggiuntive in proporzione.
- `_evaluate_clients_priority()`: legge `self.block.region.blocks_priority` (dizionario `{block_id: priority}` mantenuto dalla `Region`) e per ogni client presente in `self._clients` recupera la sua priorità; se il blocco o la regione non sono impostati, logga warning e ritorna `{}`; se un client non è trovato nella regione, viene saltato con un warning.
- `_invalidate_resource_cache()`: azzera `_resources_to_self_consume` e `_resources_needed`, forzando il ricalcolo lazy al prossimo accesso.

### Validazione (righe 516–561)
- `_is_valid_block(block)`: verifica per nome di classe nella MRO (`cls.__name__ == 'Block'`) invece di `isinstance` — scelta deliberata per supportare mock/stub nei test che sovrascrivono `__class__` con una classe fittizia chiamata `Block` (pattern visto anche in `Test_Military.py`, vedi Known Issue "circular import" in memoria di progetto).
- `_validate_block_param`, `_validate_all_params`, `_validate_dict_param`, `_validate_param`: validazioni di tipo generiche, tutte basate sul confronto per nome di classe (`value.__class__.__name__ == expected_type`) piuttosto che `isinstance`, verosimilmente per lo stesso motivo (evitare import diretti che causerebbero import circolari con `Block`/`Payload`).

### `__repr__` / `__str__` (righe 563–571)
Rappresentazioni testuali che includono l'id del blocco associato, conteggio client/server e stato del warehouse.

## Dipendenze

- `Code.Dynamic_War_Manager.Source.Utility.Utility` — `validate_class`, `setName`, `setId`, `mean_point` (import presenti; `setName`/`setId`/`mean_point`/`validate_class` non risultano usati direttamente nel corpo attuale della classe — probabile residuo di refactoring)
- `Code.Dynamic_War_Manager.Source.Utility.LoggerClass.Logger` — logger di modulo (`logger = Logger(module_name=__name__, class_name='Resource_Manager')`)
- `Code.Dynamic_War_Manager.Source.DataType.Payload` — `Payload`, `PAYLOAD_ATTRIBUTES` (operazioni aritmetiche `+`, `-`, `*`, confronto `<`, `division()`, `copy()`)
- `Code.Dynamic_War_Manager.Source.Context.Context` — `PRODUCTION_WEIGHT` (usato in `production_value`)
- `Block` (solo `TYPE_CHECKING`, per annotazioni — nessun import reale a runtime, evita l'import circolare `Block → Resource_Manager → Block`)
- `inspect` (stdlib) — `inspect.getmro` per `_is_valid_block`
- `dataclasses`, `collections.defaultdict`, `typing` (stdlib) — `defaultdict` importato ma non risulta usato nel codice attuale

**Dipendenza inversa**: `Block.__init__` (riga 8 e 107 di `Block.py`) importa `Resource_Manager` e crea `self._resource_manager = Resource_Manager(block=self)` in ogni istanza di `Block` — quindi ogni `Block` ha sempre esattamente un `Resource_Manager` associato fin dalla creazione.

Altri moduli che referenziano `Resource_Manager` nel codice di produzione (non test): `Context/Logistic_Lines.py`, `Logic/Scenario_Manager.py`, `Context/Context.py`, `Context/Campaign_State.py`.

## Stato attuale

**Parziale/non verificabile allo stato attuale.** Il codice di produzione è completo dal punto di vista funzionale (produzione, auto-consumo con logica di autonomia, distribuzione pesata per priorità, ciclo orchestrato `run_management_cycle`), ma **l'intera suite di test è rotta**: tutti i 12 metodi di test in `Test_Resource_Manager.py` fanno affidamento su `setUp()`, che fallisce sistematicamente nella creazione del `Resource_Manager` (vedi sezione bug). Di conseguenza:

- Copertura di test reale: **0/12 test eseguibili** (12 errori su 12, tutti con la stessa causa radice in `setUp`).
- Non è quindi possibile oggi verificare tramite test automatici la correttezza delle logiche di `consume`, `produce`, `delivery`, `_evaluate_clients_priority`, ecc. — anche se, leggendo il codice, la logica appare internamente coerente e ben documentata con docstring.
- Il file di test è comunque ben strutturato concettualmente (mock `MockBlock`/`MockPayload` isolati per evitare l'import circolare con `Block`/`Payload` reali) e con un fix minimo (una riga) tornerebbe verosimilmente operativo, permettendo poi di validare le assunzioni sui calcoli (es. `test_production_calculations` verifica anche `production_value` con un calcolo atteso esplicito).

## Bug: MockBlock.name mismatch

**Esito investigazione: confermato — bug nella fixture di test, non nel codice di produzione.**

1. **Codice di produzione** — `Code/Dynamic_War_Manager/Source/Component/Resource_Manager.py:71`:
   ```python
   self._id = f"Resource_Manager_{block.id}_{block.name}"
   ```
   `Resource_Manager.__init__` si aspetta legittimamente che il `block` passato esponga sia `.id` sia `.name`.

2. **Classe `Block` reale** (`Code/Dynamic_War_Manager/Source/Block/Block.py`):
   - `.name` è una property vera e propria (getter righe 198–201, setter righe 203–207), supportata da `self._name` impostato in `__init__` riga 95: `self._name = name if name else setName('Unnamed')` — quindi **sempre valorizzato**, anche se il parametro `name` non è passato al costruttore.
   - `.id` è analogamente una property (righe 209–219), derivata da `self._id = setId(self._name, None)` (riga 96).
   - Conclusione: ogni istanza reale di `Block` espone sempre sia `.id` sia `.name`. `Resource_Manager.__init__` (riga 71) è quindi coerente con il contratto reale della classe `Block`.

3. **Fixture di test `MockBlock`** (`Code/Dynamic_War_Manager/Source/Test/Test_Resource_Manager.py:109–136`):
   ```python
   class MockBlock:
       def __init__(self, block_id: str, has_rm: bool = True):
           self.id = block_id
           self.region = MagicMock(spec=Region)
           self.assets = []
           self._resource_manager = None
           if has_rm:
               self._resource_manager = MagicMock()
               self._resource_manager.block = self
       ...
   ```
   `MockBlock.__init__` imposta `self.id` ma **non imposta mai `self.name`** (né come attributo diretto né come property). Il fallimento avviene quindi in `setUp()` (righe 141, 145–147, 154–159) al momento della creazione di `Resource_Manager(block=self.mock_block, ...)`, non essendo `.name` presente sull'istanza mock.

   Questa è una fixture disallineata: quasi certamente `Resource_Manager.__init__` è stato modificato in un refactoring successivo per includere `block.name` nell'id (probabilmente per rendere l'id più leggibile/debuggabile, es. `Resource_Manager_test_block_MyBlockName`), ma `MockBlock` non è mai stato aggiornato di conseguenza.

**Nota quantitativa**: il prompt di incarico menzionava "13 test falliti"; l'esecuzione effettiva (`python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Resource_Manager.py"`) mostra **12 test totali, 12 errori** (100% falliti in `setUp`, coerente con la causa radice unica). Il file contiene 12 metodi `def test_...` (verificato con grep).

**Proposta di fix (non applicata, solo raccomandazione)**: aggiungere in `MockBlock.__init__` (dopo la riga `self.id = block_id`) una riga equivalente a:
```python
self.name = f"MockBlock_{block_id}"
```
oppure, se si vuole mantenere `id` e `name` disaccoppiati come nella classe reale, aggiungere un parametro opzionale `name: str = None` al costruttore di `MockBlock` con default derivato da `block_id`. Questo allineerebbe la fixture al contratto reale di `Block` senza toccare `Resource_Manager.py` (che è corretto). Nessuna modifica al codice sorgente è stata applicata in questa sessione, come da vincolo di sola analisi.

## Problemi aperti

- **Test suite non eseguibile**: bug descritto sopra blocca tutti e 12 i test; nessuna verifica automatica delle logiche di business è attualmente possibile per questo componente.
- **Import inutilizzati**: `setName`, `setId`, `mean_point`, `validate_class` (da `Utility.Utility`) e `defaultdict` (da `collections`) sono importati ma non risultano usati nel corpo di `Resource_Manager.py` — possibile residuo di refactoring, da verificare/pulire.
- **`Resource_Manager_Params` dataclass apparentemente non utilizzata**: definita ma non referenziata all'interno della classe `Resource_Manager` stessa (la validazione passa invece per metodi `_validate_*` dedicati); da chiarire se sia pensata per uso esterno (es. costruzione parametri prima dell'istanziazione) o sia codice morto.
- **Nessun controllo di conservazione delle risorse in `delivery()`**: la funzione usa `min(request, max_delivery)` per parametro (`goods`, `energy`, ecc. indipendentemente), il che è corretto per evitare consegne eccedenti la richiesta o la quota, ma non c'è una verifica esplicita che `sum(actual_delivery per tutti i client) <= warehouse iniziale` in caso di arrotondamenti o valori limite — il codice si affida alla sottrazione progressiva di `available_resources`, che sembra sufficiente ma non è testata.
- **Ordine di iterazione dei client in `delivery()`**: l'ordine con cui i client vengono serviti (`self._clients.items()`, ordine di inserimento del dict) non è esplicitamente basato sulla priorità calcolata — la priorità influenza solo la *quota massima* (`max_delivery`), non l'ordine di assegnazione; con risorse scarse e più client ad alta priorità, il primo servito nell'ordine di inserimento del dizionario potrebbe avere un vantaggio implicito non documentato.
- **Comportamento di `production_value` con pesi a zero**: solleva `ValueError` se `Context.PRODUCTION_WEIGHT` ha somma zero — dipendenza implicita dalla corretta configurazione di un modulo esterno (`Context.py`), senza validazione locale che i pesi individuali siano non negativi.
- **Relazione con `Logistic_Lines.py`, `Scenario_Manager.py`, `Campaign_State.py`**: questi moduli referenziano `Resource_Manager` ma non sono stati analizzati in profondità in questo incarico (fuori scope) — andrebbe verificato in una fase successiva come interagiscono con il ciclo `run_management_cycle()` e la persistenza dello stato (`Campaign_State`, coerente con quanto già noto in memoria di progetto: "Resource_Manager (warehouse, actual_production, clients_ids, server_ids)" viene serializzato).
