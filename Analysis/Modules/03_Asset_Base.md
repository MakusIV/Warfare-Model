# Asset — Classi Base

## Scopo

Il sottosistema `Asset` fornisce la gerarchia di classi che rappresenta ogni singola unità/oggetto militare, logistico o civile gestito dal Dynamic War Manager: un'unità DCS (unit → group → country → coalition), un edificio, un mezzo, una nave, un velivolo. `Asset` è la classe radice comune (stato, risorse, payload, evento, associazione al `Block` di appartenenza); `Mobile` specializza `Asset` per gli oggetti che si muovono e combattono (ereditato da `Vehicle`, `Ship`, `Aircraft`); `Structure` dovrebbe specializzare `Asset` per gli oggetti fissi/infrastrutturali (ponti, hangar, depositi, ecc.), ma — come emerso dall'analisi — non è né funzionante né usata da alcuna sottoclasse concreta.

## File inclusi

| File | Righe | Classe principale |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Asset.py` | 539 | `AssetParams` (dataclass), `Asset` |
| `Code/Dynamic_War_Manager/Source/Asset/Mobile.py` | 406 | `Mobile(Asset)` |
| `Code/Dynamic_War_Manager/Source/Asset/Structure.py` | 193 | `Structure(Asset)` |

Diagrammi UML di riferimento: `Analysis/UML/Asset.plantuml`, `Analysis/UML/Mobile.plantuml` (non esiste un `Structure.plantuml`).

## Classi e funzioni principali

### `Asset.py`

**`AssetParams`** (`@dataclass`, righe 34-52) — contenitore dati usato solo per documentare/validare i parametri di costruzione; non risulta usato attivamente altrove nel codice (nessun `AssetParams(...)` istanziato fuori da questo file).

**`class Asset`** (riga 54) — costruttore `__init__(block, name=None, description=None, category=None, asset_type=None, functionality=None, cost=None, value=None, resources_assigned=None, resources_to_self_consume=None, payload=None, production=None, position=None, volume=None, crytical=False, repair_time=0, role=None, dcs_unit_data=None)`.
- Se `name` è `None` genera un nome random (`"Asset_" + setName(6)`) ma **non lo assegna a `self._name`** (branch `if name is None: name = ...` senza `self._name = name`, riga 65-66) — l'attributo `_name` resta non impostato in quel ramo finché non interviene `dcs_unit_data` o un setter esterno. Comportamento sorprendente da verificare in caso di bug "AttributeError: _name" con asset senza nome esplicito.
- Inizializza sempre i 4 `Payload` (`resources_assigned`, `resources_to_self_consume`, `payload`, `production`) con default `Payload(goods=0, energy=0, hr=0, hc=0, hs=0, hb=0)` se non forniti.
- `_validate_all_params` (riga 483) e `_validate_param` (riga 512) fanno type-checking rigoroso via `isinstance`; `value` deve stare in `[MIN_VALUE=1, MAX_VALUE=10]`.

**Proprietà calcolate:**
- `efficiency` (riga 246): `balance_trade * health/100`, clampata a `1.0` se supera 1; **non è clampata verso il basso** (può restituire valori negativi se `balance_trade` è negativo, cosa che però non dovrebbe accadere dato che i `Payload` sono quantità non negative).
- `balance_trade` (riga 251): media dei rapporti `resources_assigned[i] / resources_to_self_consume[i]` calcolata solo sugli item con `resources_to_self_consume[i] > 0`; ritorna `0.0` se nessun item ha consumo richiesto (non `1.0`, quindi un asset senza `resources_to_self_consume` avrà sempre `efficiency = 0.0`, indipendentemente dalla salute).

**Metodi di stato** (righe 461-474): `is_operative()`, `is_damaged()`, `is_destroyed()`, `is_healtful()`, `is_critical()` — tutti deleganti a `self._state.isXxx()` con guardia `if self._state else False`.
- **Bug storico verificato risolto**: `is_critical()` chiama correttamente `self._state.isCritical()` (riga 474); `State.isCritical()` esiste in `DataType/State.py:174`. Il typo `isCrytical()` menzionato nella memoria **non è più presente** — verifica positiva.

**Gestione DCS** (`dcs_unit_data` setter, riga 345): valida via `_validate_dcs_data` (righe 522-539, controlla solo i campi presenti nel dict, tipizzazione soft) e poi popola `_name`, `_id`, `_position` (da `unit_x/unit_y/unit_alt`, unità: coordinate DCS grezze, non convertite), `_state.health` (da `unit_health`).

**Risorse**: `consume()`/`_consume()` (righe 384-404) decrementano `resources_assigned` in base a `resources_to_self_consume`, item per item, con esito booleano/`None` per item; `get_production()` (riga 411) e `produce()` (riga 434) gestiscono la produzione nominale — `get_production()` **preleva** dal payload esistente (consuma stock), mentre `produce()` **aggiunge** al payload moltiplicando la richiesta per `efficiency` (le due funzioni hanno semantiche opposte pur nome simile, attenzione a non confonderle).

`threat_volume()` (riga 477) è uno **stub non implementato** (`pass`).

### `Mobile.py`

**`class Mobile(Asset)`** (riga 32) — aggiunge `_speed` (dict `{"nominal": None, "max": None}` di default... ma il type-hint dichiarato è `{"nominal": None, "max": None}` mentre `checkParam` valida le chiavi `["cruise", "max"]`, **incoerenza tra le chiavi usate nel default e quelle validate**, vedi Bug §1), `_range`, `_weapon = {}` (mai popolato altrove nel file), `_combat_power` (dict annidato `{force: {task: 0.0}}` costruito da `Context.MILITARY_FORCES` / `Context.ACTION_TASKS`).

**`combat_power(force=None, action=None)`** (riga 110): accessor polimorfico — con `force` e `action` entrambi valorizzati ritorna un `float`; solo `force` → `Dict[task, float]`; solo `action` → `Dict[force, Dict[task, float]]` filtrato sui force che hanno quel task; nessuno dei due → l'intero dict. Validazione tipi/valori contro `MILITARY_FORCES`/`ACTION_TASKS`.

**`set_combat_power_value(combat_power: Dict)`** (riga 166): sovrascrive `_combat_power` con validazione strutturale (deve avere almeno una chiave in `MILITARY_FORCES` e sotto-chiavi in `ACTION_TASKS[force]`). Il calcolo del valore è demandato alle sottoclassi (`Vehicle`/`Ship`/`Aircraft`), qui c'è solo l'assegnazione validata.

**`air_defense_volume() → Optional[Cylinder]`** (riga 208, funzionalità recente confermata):
- Richiede `self._position` e `self._model` impostati; risolve i dati arma da `Vehicle_Data._registry` o `Ship_Data._registry` (import locale a runtime, per evitare l'import circolare a livello di modulo).
- Vehicle: considera solo `AA_CANNONS` e `MISSILES` con `min_altitude`/`max_altitude` presenti nel record arma, **esclusi** quelli il cui campo `task` (se presente) non contiene `'Anti_Air'` (`GROUND_WEAPON_TASK['Anti_Air']`).
- Ship: considera solo `MISSILES_SAM`; range convertito da km a metri (`* 1000.0`).
- Ritorna `Cylinder(center=bottom_center, radius=max_range, height=max_alt-min_alt)` con `bottom_center.z = pos.z + min_alt` (quota minima di ingaggio sommata alla quota dell'asset); `None` se nessuna arma AD valida o `max_range == 0.0`.
- **Unità di misura**: metri per raggio/altezza, coerenti tra Vehicle (già in metri nei dati) e Ship (convertiti da km).

**`combat_range() → Optional[float]`** (riga 280, funzionalità recente confermata):
- Vehicle: `CANNONS, ARTILLERY, MORTARS, ROCKETS, MISSILES, AUTO_CANNONS`; esclude i `MISSILES` con `min_altitude` (discriminante SAM) e qualunque arma con `'Anti_Air'` in `task`.
- Ship: `MISSILES_ASM, MISSILES_TORPEDO, GUNS`; range convertito km→m.
- Gestisce sia range "piatto" (numero) sia range a dizionario `{'direct':, 'indirect':}` prendendo il massimo dei due.
- Ritorna il **massimo** range fra tutte le armi offensive trovate, `None` se nessuna.

**`fire_range`**: la proprietà `fire_range` menzionata come "rimossa in sessione precedente" nella memoria **risulta effettivamente assente** dalla classe — l'unico residuo testuale è il nome del parametro nella firma (ormai orfana) di `checkParam(speed, fire_range)` (righe 345-358), che non viene mai chiamato con quel significato nel resto del file. L'UML `Mobile.plantuml` (righe 92, 99, 110) **è disallineato dal codice**: mostra ancora `-_fire_range: float`, `+fire_range: float` come proprietà e gli stub `attackRange()`/`airDefense()` che non esistono più nel sorgente attuale (sostituiti da `combat_range()`/`air_defense_volume()`).

**Import path**: verificato che sia `Mobile.py` che `Structure.py` importano ora correttamente con prefisso `Code.Dynamic_War_Manager.Source....` in tutte le righe (nessun residuo di `from Dynamic_War_Manager.Source...`) — il bug di import path menzionato come "corretto oggi" è confermato risolto in entrambi i file.

### `Structure.py`

**`class Structure(Asset)`** (riga 25) — pensata per rappresentare asset infrastrutturali fissi (bridge, hangar, depot, oil tank, farm, power plant, station, building, factory, barrack — via `Logistic_Asset_Type`), con metodi `isBridge()`, `isHangar()`, ecc. (righe 137-165, semplici confronti su `self.category`).

**Stato: la classe è strutturalmente non istanziabile** — vedi bug dettagliati sotto. Non risulta testata (nessun `Test_Structure.py`) né istanziata da alcuna sottoclasse concreta nel codebase.

## Dipendenze

Ricerca `class X(Asset)`, `class X(Mobile)`, `class X(Structure)` su tutto `Code/Dynamic_War_Manager/Source/`:

- **Eredita da `Asset`**: `Mobile` (`Asset/Mobile.py:32`), `Structure` (`Asset/Structure.py:25`).
- **Eredita da `Mobile`**: `Vehicle` (`Asset/Vehicle.py:33`), `Ship` (`Asset/Ship.py:24`), `Aircraft` (`Asset/Aircraft.py:26`).
- **Eredita da `Structure`**: nessuna classe nel codebase. I riferimenti a `'Structure'` in `Block/Block.py` e `Block/Military.py` sono confronti su stringa (`asset.__class__.__name__ == 'Structure'`, liste di valori ammessi per `asset_class`) usati per logica di filtro/categorizzazione, non istanziazioni reali.
- **Usa `Asset` direttamente** (import, non eredità): `Block/Block.py`, `Block/Military.py`, `DataType/Waypoint.py`, `DataType/Edge.py` (tipicamente per `validate_class(obj, "Asset")` o riferimenti in signature/type hint).
- `air_defense_volume()`/`combat_range()` in `Mobile.py` importano localmente (dentro il metodo, non a livello di modulo) `Vehicle_Data`, `Ship_Data`, `Ground_Weapon_Data`, `Ship_Weapon_Data` — scelta deliberata per aggirare l'import circolare `Aircraft ↔ Aircraft_Data ↔ Aircraft_Loadouts ↔ Aircraft_Weapon_Data ↔ Aircraft` che altrimenti impedirebbe l'import di `Mobile.py` a livello di modulo.
- `Military.py` (`Block/Military.py`) usa `hasattr(asset, 'air_defense_volume')` / `hasattr(asset, 'combat_range')` per iterare gli asset del blocco senza importare direttamente `Vehicle`/`Ship`/`Aircraft` (duck typing, workaround noto per l'import circolare).

## Stato attuale

**Test eseguiti** (`.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_XXX.py"`):
- `Test_Asset.py` → **41 test, OK** (init, property setters, payload ops, eventi, dcs data, associazione block, type checking, tutti gli stati `is_healtful/is_operative/is_damaged/is_critical/is_destroyed` con boundary test e mutua esclusione).
- `Test_Mobile.py` → **54 test, OK** — ma copre **esclusivamente** `air_defense_volume()` (Vehicle + Ship, 26 test circa) e `combat_range()` (Vehicle + Ship, 28 test circa) tramite uno stub (`_MobileStub`) che bypassa completamente `Mobile.__init__` (`air_defense_volume = Mobile.air_defense_volume` assegnato come attributo di classe). **Nessun test copre**: `__init__`, la property `speed`, `combat_power()`, `set_combat_power_value()`, `checkParam()`, `checkParamDCS()`.
- Nessun `Test_Structure.py` esiste: **zero copertura test** per `Structure`.

**Bug confermati con verifica runtime diretta** (istanziazione reale di `Block`/`Ship`/`Vehicle`/`Aircraft`/`Structure`, non solo lettura del codice):

1. **`Mobile.checkParam` non richiama con `self` — rompe la property `speed` per ogni sottoclasse** (`Asset/Mobile.py:345-358`, chiamata da `speed.setter` a `Asset/Mobile.py:100`). `checkParam` è definito `def checkParam(speed: float, fire_range: float)` senza `self` esplicito (non è `@staticmethod`); quando il setter chiama `self.checkParam(speed=param)`, Python lega implicitamente `self` al primo parametro posizionale `speed`, e la keyword `speed=param` genera conflitto. **Verificato praticamente**: istanziare un `Ship(block=Block(...), name=..., model=...)` minimale solleva `TypeError: Ship.checkParam() got an unexpected keyword argument 'speed'` già dentro `Ship.__init__` (riga `Asset/Ship.py:33`, `self.speed = {...}`), perché `Ship`/`Vehicle`/`Aircraft` sovrascrivono `checkParam` con una firma incompatibile (`checkParam(self, asset_type=None)` in `Ship.py:86`/`Aircraft.py:86`). **Conseguenza: nessuna istanza di `Ship` (e presumibilmente `Vehicle`/`Aircraft`, stessa logica di `__init__`) può essere creata con i valori di default attuali** — bug bloccante non coperto da alcun test (i test esistenti bypassano `__init__` con stub).
2. **`Mobile.checkParamDCS` stesso problema di `self` mancante** (`Asset/Mobile.py:360`, chiamata a riga 75). Se venisse passato un `dcs_unit_data` non vuoto a `Mobile.__init__`, `self.checkParamDCS(dcs_unit_data)` fallirebbe con `TypeError: checkParamDCS() takes 1 positional argument but 2 were given` (verificato con riproduzione isolata del pattern). Percorso DCS quindi non funzionante nemmeno a costruttore riparato.
3. **`Structure.__init__` chiama `super()` con argomenti posizionali disallineati** (`Asset/Structure.py:46`): la firma di `Structure.__init__` include `physical_characteristics` come 5° parametro (dopo `category`), ma la chiamata `super().__init__(block, name, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data)` omette del tutto `physical_characteristics` e non compensa lo slot mancante (`production` in `Asset.__init__`). Risultato: ogni argomento da `position` in poi scala di una posizione — `position` (Point3D) finisce nello slot `production`, `volume` finisce nello slot `position`, `crytical` (bool) finisce nello slot `volume`, ecc. **Verificato praticamente**: istanziare `Structure(block=Block(...), name=..., category="Bridge")` solleva `TypeError: Invalid type for volume. Expected Volume, got bool` (il `crytical=False` di default finisce validato come `volume`). **`Structure` non è istanziabile in nessuna configurazione attuale.**
4. **`Structure.__init__` riga 55**: `if not super.checkParam(...)` usa `super` come **classe built-in** (senza parentesi `()`), non l'oggetto proxy `super()` — `AttributeError: type object 'super' has no attribute 'checkParam'`. Bug ridondante rispetto al #3 (mai raggiunto perché il #3 lo precede), ma confermerebbe comunque l'inutilizzabilità della classe se il #3 venisse corretto isolatamente.
5. **`Structure.__init__` riga 49**: `self.physical_characteristics = physical_characteristics if physical_characteristics else self.get_physical_characteristics()` — se `physical_characteristics` non è fornito, chiama `get_physical_characteristics()` che fa `return self.physical_characteristics`, ma l'attributo non è ancora stato assegnato in quel momento → `AttributeError`. Bug ulteriore, anch'esso mai raggiunto a runtime perché preceduto dal bug #3 nell'ordine del file (in realtà l'ordine reale di esecuzione è: riga 46 `super().__init__` fallisce **prima** di arrivare alla riga 49, quindi il #5 non si manifesta mai nella pratica finché il #3 non viene risolto).
6. **`Structure.getBlockInfo`** (`Asset/Structure.py:101-134`) referenzia `STRUCTURE_ASSET_CATEGORY` mai importato nel file → `NameError` se mai chiamato (codice morto, irraggiungibile finché `Structure` non è istanziabile).
7. **`Structure.loadAssetDataFromContext`** (`Asset/Structure.py:70`): `for k, v in asset_data[self.block.block_class][self.category]:` itera un `dict` **senza `.items()`** — `BLOCK_INFRASTRUCTURE_ASSET[classe][categoria]` è un `dict` (confermato in `Context/Context.py:1072` e uso con `.keys()` altrove), quindi l'unpacking `k, v` fallirebbe (`ValueError: too many values to unpack` o simile) se mai raggiunto.

**Bug storici risolti, confermati**:
- `Asset.is_critical()` → `self._state.isCritical()` corretto (non più `isCrytical`).
- Import path in `Mobile.py`/`Structure.py` → tutti con prefisso `Code.Dynamic_War_Manager.Source...`, nessun residuo `from Dynamic_War_Manager...`.
- La property `fire_range` è effettivamente assente da `Mobile` (nessuna definizione `@property fire_range`), solo il nome del parametro sopravvive nella firma orfana di `checkParam`.

**Import circolare** (verificato con riproduzione diretta, non solo da memoria): `from Code.Dynamic_War_Manager.Source.Asset.Vehicle import Vehicle` e `from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft` sollevano entrambi `ImportError: cannot import name 'Aircraft' from partially initialized module ... (most likely due to a circular import)` quando importati come primo modulo di uno script/processo Python pulito. La catena è `Aircraft → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft`, e `Vehicle → Vehicle_Data → Ground_Weapon_Data → Aircraft` la eredita indirettamente. **`Ship` invece si importa senza problemi** (non attraversa la catena `Aircraft_Data`). Questo impedisce a qualunque test o script di importare `Vehicle`/`Aircraft` direttamente: è necessario passare per `Ship` prima, per un altro modulo che triangoli l'import, o per stub/mock (come fa `Test_Mobile.py`).

## Problemi aperti

1. **Bloccante — `Ship`/`Vehicle`/`Aircraft` non sono istanziabili con i parametri di default correnti** a causa del bug `Mobile.checkParam` (self mancante + firme incompatibili nelle sottoclassi). Va deciso se: (a) rendere `checkParam` uno `@staticmethod` con firma coerente e farlo chiamare esplicitamente come `Mobile.checkParam(...)`, oppure (b) rinominare/rimuovere il meccanismo `checkParam` per `speed` a favore di validazione inline nel setter, coerentemente con come `Vehicle`/`Ship`/`Aircraft` hanno già un proprio `checkParam(asset_type=...)` con scopo diverso (validazione categoria) che va in conflitto di firma con quello ereditato da `Mobile`.
2. **Bloccante — `Structure` è totalmente non funzionante e priva di test.** Da decidere se il sottosistema `Structure` è ancora nella roadmap (per rappresentare asset infrastrutturali fissi) o se è stato di fatto abbandonato a favore di un'altra modellazione (es. asset infrastrutturali gestiti come categorie di `Block` piuttosto che sottoclasse `Asset`). Se resta nella roadmap, richiede una riscrittura del costruttore (allineamento argomenti con `Asset.__init__`, gestione `production` mancante, fix `super().checkParam` → `self.checkParam` o rimozione, fix `get_physical_characteristics`), oltre a `Test_Structure.py` da creare da zero.
3. **Import circolare irrisolto** (`Aircraft ↔ Aircraft_Data ↔ Aircraft_Loadouts ↔ Aircraft_Weapon_Data ↔ Aircraft`, che si propaga a `Vehicle`): impedisce l'uso diretto di `Vehicle`/`Aircraft` in test o script isolati, costringendo a workaround (stub, mock, import via `Ship` prima). Root cause architetturale da affrontare separatamente (probabilmente serve rompere la dipendenza `Aircraft_Weapon_Data → Aircraft` o `Ground_Weapon_Data → Aircraft`, che sembrano usare `Aircraft` solo per type-hint/isinstance e potrebbero usare import lazy o `TYPE_CHECKING`).
4. **`Mobile._weapon`** (riga 61) è inizializzato come dict vuoto ma non risulta mai letto/scritto altrove nel file: verificare se è usato dalle sottoclassi (`Vehicle`/`Ship`/`Aircraft`) o se è dead code residuo da rimuovere.
5. **UML `Mobile.plantuml` disallineato dal codice**: mostra ancora `_fire_range`/`fire_range`, `attackRange()`, `airDefense()` (stub mai implementati/rimossi) invece di `air_defense_volume()`/`combat_range()`. Da rigenerare.
6. **`Asset.__init__` — branch `name is None`** (riga 65-66) non assegna `self._name`, lasciando l'istanza priva dell'attributo `_name` finché non interviene `dcs_unit_data` o un `name` esplicito via property; da verificare se questo produce `AttributeError` in scenari reali (es. asset creato senza nome e senza dcs_unit_data, poi si accede a `.name`).
7. **`Asset.balance_trade`** ritorna `0.0` (non `1.0`) quando nessun item di `resources_to_self_consume` è impostato, il che forza `efficiency = 0.0` per qualunque asset senza consumo dichiarato — comportamento da confermare come intenzionale (un asset "senza bisogni" viene trattato come 0% efficiente anziché 100%) perché impatta a cascata `produce()`/`is_operative()`-correlati in `Military.py`.
