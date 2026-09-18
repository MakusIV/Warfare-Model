---
title: "Component"
type: project-module
tags: [package-python, resource-manager, logistica, economia, dwm]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Component/Resource_Manager.py]
related_decisions: []
related: ["[[block]]"]
---

## Scopo

`Resource_Manager` è il componente che ogni `Block` possiede (relazione 1:1, istanziata
direttamente in `Block.__init__`, v. [[block]]) per governare il ciclo economico locale del
blocco: **produzione** delle risorse generate dagli `Asset` assegnati, **auto-consumo** delle
risorse necessarie al proprio funzionamento (con una logica di razionamento basata sull'autonomia
residua), e **ridistribuzione** verso altri blocchi collegati come "client" secondo una logica di
priorità strategica/tattica letta dalla `Region` (`block.region.blocks_priority`). Un blocco può
essere sia "server" (fornitore) per altri blocchi client, sia "client" di un proprio server, con
riferimenti bidirezionali mantenuti in modo coerente da `set_server`/`set_client`.

**Nota sullo stato di questa pagina**: sostituisce l'audit `Analysis/Modules/09_Component.md`
(2026-08-16). Rispetto a quell'audit, il codice di produzione (`Resource_Manager.py`) risulta
**invariato riga per riga** (stesse 570 righe, stessa struttura), ma il verdetto su copertura di
test è **completamente ribaltato**: il vecchio audit segnalava "0/12 test eseguibili" per un
disallineamento nella fixture di test; verificato a HEAD che quella fixture è stata corretta e la
suite oggi passa per intero. Vedi sezione "Stato attuale" per i dettagli verificati.

## File inclusi

- `Code/Dynamic_War_Manager/Source/Component/Resource_Manager.py` (570 righe) — unico file del
  sottosistema: classe `Resource_Manager` e dataclass ausiliaria `Resource_Manager_Params`
- `Code/Dynamic_War_Manager/Source/Test/Test_Resource_Manager.py` (fixture `MockBlock`/`MockPayload`
  proprie, non importa `Block` reale)
- `Analysis/UML/Resource_Manager.plantuml` (non riverificato in questa sessione)

## Classi e funzioni principali

### `Resource_Manager_Params` (dataclass)
Contenitore dati per la validazione dei parametri: `clients`, `server`, `warehouse`. Non risulta
ancora usato direttamente nel corpo della classe `Resource_Manager` (la validazione passa per
metodi `_validate_*` dedicati) — invariato dal vecchio audit, probabile artefatto di design non
completamente integrato.

### `Resource_Manager.__init__(block, clients=None, server=None, warehouse=None)`
- Solleva `ValueError` se `block is None`.
- Valida tutti i parametri con `_validate_all_params`.
- `self._id = f"Resource_Manager_{block.id}_{block.name}"` — costruisce l'id combinando `block.id`
  e `block.name` (v. sezione "Stato attuale" per la verifica di questo contratto contro `Block`
  reale e la fixture di test).
- Inizializza `_clients`/`_server` come dict vuoti se non forniti, `_warehouse` come `Payload()`
  vuoto se non fornito.
- `_resources_to_self_consume`/`_resources_needed` sono `None` (lazy loading), `_actual_production`
  è un `Payload()` vuoto.

### Proprietà principali
- `block` (get/set) — il set invalida la cache risorse (`_invalidate_resource_cache`).
- `warehouse` (get/set) — magazzino risorse (`Payload`); il setter valida il tipo e invalida la
  cache.
- `resources_needed` (lazy) — richiama `_evaluate_effective_resources_needed()` la prima volta.
- `resources_to_self_consume` (lazy) — richiama `_evaluate_resources_to_self_consume()` la prima
  volta.
- `actual_production` — ritorna `_actual_production`, aggiornato solo da `produce()`.
- `production_value` — indice sintetico ponderato della produzione attuale: somma di
  `actual_production[item] * Context.PRODUCTION_WEIGHT[item]` per ogni item di
  `PAYLOAD_ATTRIBUTES`, diviso per la somma dei pesi (`Context.PRODUCTION_WEIGHT`: goods=6,
  energy=8, hr=1, hc=10, hs=6, hb=3, totale=34). Ritorna `0.0` se la produzione attuale è
  vuota/nulla. Solleva `ValueError` se la somma dei pesi è 0.

### Gestione Server — questo blocco come *client* di un altro
- `server` (get/set), `list_server_keys()`, `get_server(key)`.
- `set_server(key, server)`: verifica `server.has_resource_manager()`, poi imposta il riferimento
  **bidirezionale** chiamando `server.resource_manager.set_client(self.block.id, self.block)`. In
  caso di eccezione fa rollback (`del self._server[key]`) e rilancia `RuntimeError`.
- `remove_server(key)`: rimuove un server esistente; `KeyError` se la chiave non esiste; chiama
  `deleted_server.resource_manager.remove_client(self.block.id)` per mantenere coerenza
  bidirezionale; `RuntimeError` se il server non ha più un resource manager.

### Gestione Client — questo blocco come *server* per altri
- `clients` (get/set), `list_client_keys()`, `get_client(key)`.
- `set_client(key, client)`: normalmente invocato automaticamente da `set_server` del client, non
  direttamente. Verifica che il client abbia un resource manager e che il riferimento bidirezionale
  sia coerente (`client_rm.get_server(self.block.id) != self.block` → `ValueError`).
- `remove_client(key)`: analogo, con lo stesso controllo di coerenza; `KeyError` se la chiave non
  esiste.

### Operazioni sulle risorse
Ordine dichiarato nel codice: **I - consume(), II - produce(), III - delivery() (usa receive)**.

- **`consume() -> bool`**: preleva da `_warehouse` la quantità pari a `resources_to_self_consume`.
  Se il magazzino è insufficiente (`self._warehouse < resources_needed`) logga un warning e
  ritorna `False` senza modificare nulla. Tutte le eccezioni interne sono catturate e loggate come
  errore, ritornando `False`.
- **`receive(payload) -> bool`**: somma un `Payload` ricevuto al magazzino
  (`self._warehouse += payload`). Valida il tipo del payload; `ValueError` se il warehouse non è
  impostato. Cattura le eccezioni e ritorna `False` in caso di errore.
- **`delivery() -> Dict[str, bool]`**: distribuisce le risorse disponibili ai client in base alla
  priorità: calcola `clients_priority` (`_evaluate_clients_priority()`), per ciascun client
  `priority_ratio = client_priority / total_priority`, `max_delivery = available_resources *
  priority_ratio`; la consegna effettiva per parametro (`RESOURCE_PARAMS`) è il **minimo** fra la
  richiesta del client e la quota massima assegnata. Chiama `client.resource_manager.receive(...)`;
  se ha successo sottrae la quantità sia da `self._warehouse` sia da `available_resources` (copia
  locale). Ritorna `{client_id: bool}`; client senza priorità valida → `False` + warning. Solleva
  `ValueError` se `resources_to_self_consume`/`warehouse` non sono impostati.
- **`produce() -> Dict[str, Optional[bool]]`**: resetta `_actual_production`, poi itera
  `self.block.assets`; per ciascun asset chiama `asset.get_production()` e somma ogni item positivo
  sia al `warehouse` sia a `_actual_production` (`results[item] = True`), altrimenti `False`.
  L'efficienza dell'asset è già applicata a monte, dentro `asset.get_production()`.
- **`run_management_cycle() -> Dict[str, Optional[bool]]`**: orchestratore che esegue in sequenza
  `consume()`, `produce()`, `delivery()` e ne aggrega i risultati in
  `{'consume':…, 'produce':…, 'delivery':…}`.

### Metodi privati di calcolo
- `_evaluate_resources_to_self_consume()`: somma `asset.resources_to_self_consume` su tutti gli
  asset del blocco. Ritorna `Payload()` vuoto se il blocco non ha asset.
- `_evaluate_effective_resources_needed()`: calcola l'autonomia come
  `warehouse.division(resources_to_consume)` e applica un moltiplicatore per parametro in base a
  soglie di autonomia. Ritorna `Payload()` se manca consumo o magazzino.
- `_get_autonomy_multiplier(autonomy_value)`: usa `AUTONOMY_THRESHOLDS` — `[0,2)→1.0`,
  `[2,3)→0.5`, `[3,5)→0.25`, `[5,∞)→0.1`; default `0.1` se nessuna soglia combacia. Più autonomia
  (scorte rispetto al consumo), meno risorse aggiuntive richieste in proporzione.
- `_evaluate_clients_priority()`: legge `self.block.region.blocks_priority`
  (`{block_id: priority}` mantenuto dalla `Region`) e per ogni client presente in `self._clients`
  recupera la sua priorità; logga warning e ritorna `{}` se blocco/regione non impostati; salta con
  warning un client non trovato nella regione.
- `_invalidate_resource_cache()`: azzera `_resources_to_self_consume`/`_resources_needed`,
  forzando il ricalcolo lazy al prossimo accesso.

### Validazione
- `_is_valid_block(block)`: verifica per nome di classe nella MRO (`cls.__name__ == 'Block'`)
  invece di `isinstance` — scelta deliberata per supportare mock/stub nei test che sovrascrivono
  `__class__`, e per evitare l'import circolare `Block → Resource_Manager → Block` (a runtime
  `Block` è importato solo sotto `TYPE_CHECKING`).
- `_validate_block_param`, `_validate_all_params`, `_validate_dict_param`, `_validate_param`:
  validazioni di tipo generiche, basate sul confronto per nome di classe, stesso motivo.

### `__repr__` / `__str__`
Rappresentazioni testuali con id del blocco associato, conteggio client/server, stato del
warehouse. Invariate.

## Dipendenze

- `Utility/Utility.py` — `validate_class`, `setName`, `setId`, `mean_point` (importati ma **ancora
  non usati** direttamente nel corpo della classe — residuo di refactoring, invariato dal vecchio
  audit).
- `Utility/LoggerClass.Logger` — logger di modulo.
- `DataType/Payload.py` — `Payload`, `PAYLOAD_ATTRIBUTES` (operazioni aritmetiche `+`, `-`, `*`,
  confronto `<`, `division()`, `copy()`).
- `Context/Context.py` — `PRODUCTION_WEIGHT` (usato in `production_value`).
- `Block` (solo `TYPE_CHECKING`, nessun import reale a runtime — evita l'import circolare).
- `inspect` (stdlib) — `inspect.getmro` per `_is_valid_block`.
- `dataclasses`, `collections.defaultdict`, `typing` (stdlib) — `defaultdict` importato ma **ancora
  non usato** nel codice attuale.

**Dipendenza inversa**: `Block.__init__` importa `Resource_Manager` e crea
`self._resource_manager = Resource_Manager(block=self)` in ogni istanza di `Block` — quindi ogni
`Block` ha sempre esattamente un `Resource_Manager` associato fin dalla creazione (v. [[block]]).

Altri moduli che referenziano `Resource_Manager` nel codice di produzione (non riverificati in
profondità in questa sessione, fuori scope): `Context/Logistic_Lines.py` (stub non funzionante, v.
[[context-foundation]]), `Logic/Scenario_Manager.py`, `Context/Context.py`,
`Context/Campaign_State.py`.

## Stato attuale

**Codice di produzione: invariato e funzionale.** `Resource_Manager.py` non ha subito modifiche
misurabili dal vecchio audit (stesse 570 righe). La logica di produzione, auto-consumo con
razionamento da autonomia, distribuzione pesata per priorità e ciclo orchestrato
`run_management_cycle` è quella già descritta in precedenza.

**Copertura di test: risolta, ribaltando il verdetto del vecchio audit.** Il vecchio audit
riportava "0/12 test eseguibili" per un disallineamento fra `Resource_Manager.__init__` (che legge
`block.name`, oltre a `block.id`, per costruire `self._id`) e la fixture `MockBlock` di
`Test_Resource_Manager.py`, che impostava solo `self.id` senza mai impostare `self.name`.
**Verificato a HEAD**: la fixture è stata corretta —
`Code/Dynamic_War_Manager/Source/Test/Test_Resource_Manager.py:109-113` ora imposta esplicitamente
`self.name = block_id` nel costruttore di `MockBlock`, esattamente il fix suggerito (non applicato)
dal vecchio audit. Eseguendo la suite oggi:
```
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Resource_Manager.py"
→ Ran 12 tests — OK
```
Tutti e 12 i test passano. Non è più vero che "l'intera suite di test è rotta" né che serva un fix:
il fix è già stato applicato da una sessione precedente, non attribuita in nessuna memoria di
progetto consultata (nessun riferimento a `Test_Resource_Manager` in
`.claude/memory/project_*.md`). Nessuna evidenza di modifiche a `Resource_Manager.py` stesso — il
fix ha toccato solo la fixture di test, coerentemente con la diagnosi originale del vecchio audit
("bug nella fixture, non nel codice di produzione").

## Decisioni architetturali rilevanti

Nessuna decisione architetturale dedicata registrata in `wiki/decisions/` per questo sottosistema
al momento della stesura di questa pagina. Il componente è indirettamente interessato da
[[combat-power-priority-redesign]] solo in quanto consumatore di `Context.PRODUCTION_WEIGHT`
(invariato da quel lavoro) — nessun impatto diretto sulla logica di `Resource_Manager`.

## Note

- **`Resource_Manager_Params`** resta non referenziata all'interno della classe stessa — da
  chiarire se sia pensata per uso esterno o sia codice morto, invariato dal vecchio audit.
- **Import inutilizzati residui**: `setName`, `setId`, `mean_point`, `validate_class` (da
  `Utility.Utility`) e `defaultdict` (da `collections`) risultano importati ma non usati nel corpo
  di `Resource_Manager.py` — pulizia minore consigliata, invariato.
- **Nessun controllo di conservazione delle risorse in `delivery()`**: `min(request, max_delivery)`
  per parametro è corretto per evitare consegne eccedenti, ma non c'è verifica esplicita che
  `sum(actual_delivery su tutti i client) <= warehouse iniziale` in caso di arrotondamenti — il
  codice si affida alla sottrazione progressiva di `available_resources`. Non testato
  esplicitamente, invariato.
- **Ordine di iterazione dei client in `delivery()`**: l'ordine di servizio (`self._clients.items()`,
  ordine di inserimento del dict) non è basato sulla priorità calcolata — la priorità influenza solo
  la *quota massima*, non l'ordine. Con risorse scarse, il primo client nell'ordine di inserimento
  potrebbe avere un vantaggio implicito non documentato. Invariato.
- **Relazione con `Logistic_Lines.py`, `Scenario_Manager.py`, `Campaign_State.py`**: questi moduli
  referenziano `Resource_Manager` ma non sono stati riverificati in profondità in questa sessione
  (fuori scope) — `Logistic_Lines.py` risulta comunque non funzionale/stub a sé (v.
  [[context-foundation]]), indipendentemente da `Resource_Manager`.
