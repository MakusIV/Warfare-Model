# Asset — Terrestri e Navali

## Scopo

Questo sottosistema modella gli asset mobili terrestri (`Vehicle`) e navali (`Ship`) del Dynamic War Manager: veicoli da combattimento (carri, IFV/APC, artiglieria, contraerea/SAM) e unità navali (portaerei, incrociatori, cacciatorpediniere, fregate, sottomarini, ecc.). Per ciascuna famiglia esiste una tripletta di moduli con lo stesso schema architetturale:

- una classe **runtime** (`Vehicle`, `Ship`), sottoclasse di `Mobile`, che rappresenta l'istanza dell'asset dentro un `Block` di una `Region` durante la campagna;
- un modulo **dati/anagrafica** (`Vehicle_Data`, `Ship_Data`) che definisce un registro statico di modelli reali (specifiche tecniche, armamento, sensori, affidabilità) e calcola punteggi normalizzati (combat score, radar score, speed score, ecc.) usati per confronti tattici;
- un modulo **armi** (`Ground_Weapon_Data`, `Ship_Weapon_Data`) che definisce il catalogo delle armi imbarcabili e le funzioni di scoring arma-vs-bersaglio, riusate dai moduli dati per comporre il combat score complessivo del mezzo.

Lo scopo finale è fornire a `Military`/`Block` (livello superiore) dei punteggi di potenza di combattimento e capacità (range, air-defense volume, ecc.) coerenti tra asset di specie diversa (terrestri, navali, aerei), per alimentare le decisioni tattiche/strategiche del DWM.

## File inclusi

| File | Righe | Ruolo |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle.py` | 353 | Classe runtime `Vehicle(Mobile)` |
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py` | 4819 | Anagrafica/scoring statico veicoli terrestri, registro `Vehicle_Data._registry`, dict `VEHICLE` |
| `Code/Dynamic_War_Manager/Source/Asset/Ground_Weapon_Data.py` | 3098 | Catalogo armi terrestri `GROUND_WEAPONS`, funzioni di scoring arma-vs-bersaglio |
| `Code/Dynamic_War_Manager/Source/Asset/Ship.py` | 148 | Classe runtime `Ship(Mobile)` |
| `Code/Dynamic_War_Manager/Source/Asset/Ship_Data.py` | 1509 | Anagrafica/scoring statico navi, registro `Ship_Data._registry`, dict `SHIP` |
| `Code/Dynamic_War_Manager/Source/Asset/Ship_Weapon_Data.py` | 1437 | Catalogo armi navali `SHIP_WEAPONS` (SAM/ASM/Torpedo/Guns/CIWS), funzioni di scoring |

Diagrammi UML pertinenti: `Analysis/UML/Vehicle.plantuml`, `Analysis/UML/Vehicle_Data.plantuml`, `Analysis/UML/Ground_Weapon_Data.plantuml` (tutti aggiornati e coerenti col codice attuale). **Non esiste un UML per `Ship.py` / `Ship_Data.py` / `Ship_Weapon_Data.py`** — vedi Problemi aperti.

## Classi e funzioni principali

### `Vehicle.py`

- `class Vehicle(Mobile)` — `__init__(block, name, model, description, category, asset_type, functionality, cost, value, acp, rcp, payload, position, volume, crytical, repair_time, role, dcs_unit_data)`. Imposta `self._model`, carica `self._vehicle_scores = get_vehicle_scores(model=model)` e chiama subito `self.set_combat_power(ACTION_TASKS['ground'])`. **Nota critica**: `get_vehicle_scores` chiamato senza l'argomento `scores` (usa il default) fa scattare il bug di validazione descritto sotto — vedi Stato attuale. Di fatto **ogni istanziazione di `Vehicle` con un modello valido solleva `ValueError` nel costruttore**, non solo in casi limite.
- `loadAssetDataFromContext() -> bool` — popola `cost/value/requested_for_consume/repair_time/_payload_perc` da `Context.GROUND_MILITARY_VEHICLE_ASSET` / `AIR_DEFENSE_ASSET` (blocchi Military) o `BLOCK_INFRASTRUCTURE_ASSET` (blocchi Logistic). Solleva `Exception` generica se il blocco non è né Military né Logistic.
- `checkParam(category, asset_type) -> (bool, str)` — valida `asset_type` contro `BLOCK_ASSET_CATEGORY`.
- `get_physical_characteristics() -> Dict` — chiama `get_vehicle_data(model=self._model)` e fa `.get('physical_characteristics', None)`. **Bug**: `get_vehicle_data` restituisce `VEHICLE[model]`, il dizionario degli *score* costruito in `Vehicle_Data.py:4567-4581` (chiavi `'combat score'`, `'weapon score'`, ecc.), che **non contiene mai** la chiave `'physical_characteristics'`. Il metodo quindi ritorna sempre `None` silenziosamente (nessun log, perché usa `.get(..., None)` invece di un accesso diretto). I dati fisici reali vivono su `Vehicle_Data._registry[model].physical_characteristics`, mai esposti da `get_vehicle_data`.
- `set_volume_from_physical_characteristics()` — dipende dal metodo sopra: a causa del bug, logga sempre `"Unable to set volume: Physical characteristics not available"` e non imposta mai `self.volume` automaticamente.
- Proprietà booleane categoria: `isTank`, `isArmor`, `isMotorized`, `isArtillery_Semovent`, `isArtillery_Fixed`, `isArtillery`, `isAntiAircraft`, `isSAM`, `isSAM_Big/Medium/Small`, `isAAA`, `isEWR`, `isCommandControl` — tutte confrontano `self.category` con `Ground_Vehicle_Asset_Type.*.value`.
- `set_combat_power(actions=ACTION_TASKS["ground"])` — per ogni azione (`Attack/Defense/Maintain/Retrait`) calcola `combat_power[act] = relative_weight * score_modifier * self.efficiency`, dove `relative_weight = 1 + GROUND_COMBAT_EFFICACY[act][category] * 0.3/5` e `score_modifier = 1 + vehicle_scores['combat score']['global score']`. Se la categoria non è mappata in `GROUND_COMBAT_EFFICACY[act]` (es. SAM/AAA), `combat_power[act] = 0` con log di debug. Richiama `self.set_combat_power_value({"ground": combat_power})` di `Mobile`.

### `Vehicle_Data.py`

- `class Vehicle_Data` (dataclass, pattern registry-singleton) — costruttore valida `physical_characteristics` (deve contenere `length/width/height/weight`, interi positivi) e si auto-registra in `Vehicle_Data._registry[self.model] = self`. Contiene metodi di valutazione privati: `_radar_eval(modes)`, `_TVD_eval`, `_reliability_eval`, `_maintenance_eval`, `_avalaiability_eval`, `_speed_eval` (usa `convert_mph_to_kmh`), `_weapon_eval` (line 304, usa `AMMO_LOAD_REFERENCE` per pesare la quantità di munizioni ±20%), `_protection_eval`, `_communication_eval`, `_hydraulic_eval`, `_range_eval`, `_combat_eval` (line 560, media pesata delle sotto-score con pesi diversi per categoria, es. TANK pesa `protection:10, weapon:10, speed:5, range:5, TVD:3, radar:1, communication:1, hydraulic:1`). API pubblica `get_normalized_*_score(category=None)` normalizza lo score assoluto rispetto a min/max della categoria (se specificata) o dell'intero registro.
- **Getter/setter morti**: `def engine(self): return self.engine` seguito da `def engine(self, engine): self.engine = engine` (righe ~101-105) — il secondo `def` sovrascrive il primo nel namespace di classe, e comunque l'attributo istanza `self.engine` impostato in `__init__` maschera qualunque metodo con lo stesso nome. Stesso pattern per `made` e `model`. Codice morto/non funzionale, presumibilmente un tentativo di getter/setter senza `@property`.
- `CATEGORY = set(item.value for item in Ground_Vehicle_Asset_Type)` — 9/10 categorie note (Tank, Armored, Motorized, Artillery_Fixed, Artillery_Semovent, SAM_Big, SAM_Medium, SAM_Small, EWR, AAA).
- `AA_CANNONS_ALLOWED_CATEGORIES` — sottoinsieme di categorie che possono montare `AA_CANNONS` (AAA + le tre categorie SAM, per sistemi combinati SPAAGM tipo 2K22 Tunguska).
- `SCORES = ('combat score', 'radar score', 'radar score air', 'radar score ground', 'speed score', 'avalaibility', 'manutenability score (mttr)', 'reliability score (mtbf)')` (riga 4471).
- `VEHICLE: Dict` (riga 4472) — popolato in loop a riga 4567-4581 iterando `Vehicle_Data._registry.values()`; per ogni modello calcola `combat score`, `weapon score`, una chiave dinamica `weapon target effectiveness ['Armored'] ['med']`, `radar score`, `radar score ground`, `speed score`, `communication score`, `hydraulic score`, `range score`, `avalaibility`, `manutenability score (mttr)`, `reliability score (mtbf)` — **nota**: `SCORES` a riga 4471 elenca solo 8 chiavi, ma `VEHICLE[model]` in realtà ne contiene 12 (mancano da `SCORES`: `'weapon score'`, la chiave dinamica di target-effectiveness, `'communication score'`, `'hydraulic score'`, `'range score'`) — inconsistenza tra la tupla dichiarata e il contenuto reale del dizionario.
- `get_vehicle_data(model: str) -> Dict` (riga 4588) — ritorna `VEHICLE[model]` (l'intero dict di score), solleva `ValueError` se il modello non è registrato.
- `get_vehicle_scores(model: str, scores: Optional[List]=SCORES) -> Dict` (riga 4608) — **bug confermato** a riga 4646: `if scores and scores not in SCORES: raise ValueError(...)`. Questo verifica se l'intero oggetto `scores` (una lista/tupla) è un *elemento* della tupla `SCORES` (che contiene singole stringhe), invece di verificare che ogni elemento di `scores` sia *contenuto in* `SCORES`. Di conseguenza:
  - Chiamata col default (`scores` non passato → `scores is SCORES`): `SCORES not in SCORES` è `True` (la tupla non è elemento di se stessa) → **solleva sempre `ValueError`**.
  - Chiamata con qualunque lista esplicita, anche valida (es. `['combat score']`): stessa dinamica, quasi certamente solleva `ValueError` a meno che l'intera lista non coincida per identità/uguaglianza con un singolo elemento stringa di `SCORES` (impossibile, essendo una lista).
  - **Conseguenza pratica**: `get_vehicle_scores()` non è mai realmente utilizzabile nella forma attuale. Poiché `Vehicle.__init__` la chiama senza argomenti extra (riga 61 di `Vehicle.py`), **l'istanziazione di un `Vehicle` con un modello valido fallisce sempre** con `ValueError: scores unknow`.
  - Fix corretto già presente altrove nel codice come riferimento: `Ship_Data.get_ship_scores` (riga 1505 di `Ship_Data.py`) implementa la validazione giusta — `invalid = [s for s in scores if s not in SCORES]` — a dimostrazione che il bug in `Vehicle_Data` è una regressione/dimenticanza rispetto al pattern poi corretto lato Ship.
- `STAMPA` (riga 4669) — **aggiornamento rispetto alla memoria del progetto**: oggi vale `STAMPA = False` (non più `True`), quindi il blocco di stampa tabelle + generazione PDF a fine file **non viene eseguito all'import**. Il fatto noto storico risulta risolto/non più valido allo stato attuale del codice.

### `Ground_Weapon_Data.py`

- `GROUND_WEAPONS: Dict` — 9 categorie di primo livello: `AUTO_CANNONS`, `CANNONS`, `AA_CANNONS`, `MISSILES`, `ROCKETS`, `MORTARS`, `ARTILLERY`, `MACHINE_GUNS`, `FLAME_TRHOWERS` (vuota — sic, typo nel nome mai corretto), `GRENADE_LAUNCHERS`.
- `get_weapon(model: str) -> Optional[Dict]` (riga 859) — cerca `model` in tutte le categorie di `GROUND_WEAPONS`, ritorna `{"weapons_category": ..., "weapons_data": ...}` o `None`.
- `get_cannon_score`, `get_aa_cannon_score`, `get_auto_cannon_score`, `get_missiles_score`, `get_machine_gun_score`, `get_rockets_score`, `get_mortars_score`, `get_artillery_score` — uno scorer per categoria, somma pesata `WEAPON_PARAM[categoria][campo] * valore_campo`, con casi speciali per `range` (media pesata `direct*0.7 + indirect*0.3`) e `ammo_type` (usa la munizione con `AMMO_PARAM` più alto).
- `get_weapon_score(weapon_type: str, weapon_model: str)` (riga 1232) — dispatcher verso gli scorer di categoria in base a `weapon_type`.
- `get_weapon_score_single_target(weapon_type, weapon_model, target_type: str, target_dimension_distribution: dict) -> float` (riga 1273) — formula: `raw = Σ_dim distribution[dim] * accuracy[dim] * destroy_capacity[dim]`, poi `result = raw * (1 - variability)` con `variability = random.uniform(0, perc_efficiency_variability)`. **Nota**: la docstring descrive anche un `caliber_factor` e un `ammo_factor` correttivi, ma nel codice attuale (righe 1349-1377) questi due fattori sono **completamente commentati/disattivati** — restano solo `raw` e la variabilità stocastica. Documentazione (docstring) disallineata dal comportamento reale.
- `get_weapon_score_target(model: str, target_type: List, target_dimension: List) -> float` (riga 1388) — usa `get_weapon(model)` (ricerca per solo nome modello, non richiede `weapon_type`), poi per ogni combinazione `(t_type, t_dim)` valida somma `accuracy*destroy_capacity` da `weapon['efficiency'][t_type][t_dim]` e fa la media sul conteggio di combinazioni valide. Richiede **liste** per `target_type`/`target_dimension` (conferma fatto noto).
- `get_weapon_score_target_distribuition(model: str, target_type: Dict, target_dimension: Dict) -> float` (riga 1440) — variante pesata: somma `accuracy*destroy_capacity*peso_tipo*peso_dimensione` per ogni combinazione, senza media (i pesi in input devono già sommare a 1).
- Import di `Aircraft` a riga 5 (`from ...Asset.Aircraft import Aircraft`) — **è il punto di aggancio esatto della catena di import circolare** che coinvolge Vehicle/Vehicle_Data (vedi Stato attuale). Grep sull'intero file mostra che il simbolo `Aircraft` importato **non viene mai referenziato altrove nel modulo** (l'unica altra occorrenza di "Aircraft" nel file è un commento che cita il nome del file `Aircraft_Weapon_Data.py`, riga 1116) — è quindi un import morto/superfluo che sta causando un problema strutturale reale senza fornire alcun beneficio funzionale visibile in questo file.

### `Ship.py`

- `class Ship(Mobile)` — `__init__` analogo a `Vehicle` ma **non chiama `get_ship_scores`, non calcola `_ship_scores` e non richiama alcun `set_combat_power`** in fase di costruzione: la classe `Ship` non ha un equivalente di `Vehicle.set_combat_power()`. Imposta solo `self._model` e `self.speed = {"nominal": None, "max": None}`.
- `loadAssetDataFromContext() -> bool` — **due bug**:
  1. Chiama `self.block.isMilitary()` e `self.block.isLogistic()` (righe 53, 66), ma `Block` espone `is_military()` e `is_logistic()` (snake_case, verificato in `Block.py:452,456`). Queste chiamate sollevano `AttributeError` a runtime — il metodo non è mai stato eseguito con successo con l'attuale `Block`.
  2. Anche ignorando il bug precedente, itera `for k, v in asset_data[self.category]:` (righe 56, 69) su un `dict` senza `.items()` — su un dizionario, l'iterazione diretta produce solo le chiavi (stringhe), quindi `k, v = <chiave>` fallirebbe con `ValueError: too many values to unpack` (o simile) non appena eseguito. Il metodo equivalente in `Vehicle.py` usa correttamente `.items()`.
- `checkParam(asset_type: str) -> (bool, str)` — diversamente da `Vehicle.checkParam`, solleva `ValueError` (non ritorna `(False, msg)`) nei casi di modello Military con `asset_type` sconosciuto, e accede a `BLOCK_ASSET_CATEGORY[self.block.block_class][self.category]` senza `.get()` (rischio `KeyError` non gestito).
- `combatPower` — dichiarata come `@property` ma con firma `def combatPower(self, task): pass` (righe 113-115): un property non può accettare argomenti oltre `self`; l'attributo è comunque un semplice `pass` (non implementato). Codice inutilizzabile/placeholder.
- `isDestroyer`, `isCarrier`, `isCruiser`, `isFrigate`, `isFastAttackShip`, `isTransport`, `isSubmarine` — proprietà booleane che confrontano `self.category` con stringhe letterali (non con un Enum, a differenza di `Vehicle` che usa `Ground_Vehicle_Asset_Type.*.value`).
- `get_physical_characteristics() -> Dict` — stesso pattern e stesso bug di `Vehicle.get_physical_characteristics()`: chiama `get_ship_data(model=self._model)` che ritorna `SHIP[model]` (dict di score, costruito in `Ship_Data.py:1451-1464`), il quale **non contiene mai** `'physical_characteristics'`. Ritorna sempre `None`.

### `Ship_Data.py`

- `class Ship_Data` (dataclass, registry-singleton, analogo a `Vehicle_Data`) — costruttore valida `physical_characteristics` allo stesso modo; si auto-registra in `Ship_Data._registry[self.model]`. Campi aggiuntivi rispetto a `Vehicle_Data`: `ship_class` (es. `'Nimitz-class'`), `cost` in miliardi di $, `range` in miglia nautiche (nm).
- Metodi di valutazione: `_radar_eval` (valori di riferimento molto più alti dei veicoli terrestri: `tracking_range=500km`, `engagement_range=400km`), `_reliability_eval`/`_maintenance_eval` (compositi motore+radar, `min*0.3 + media*0.7`), `_avalaiability_eval` (`mtbf/mttr`), `_speed_eval` (normalizzato su 35 nodi di riferimento, converte `metric`/`imperial`→nodi), `_weapon_eval`, `_combat_eval`, e le rispettive `get_normalized_*_score(category=None)`.
- `SCORES` (riga 85) — 10 chiavi: `'combat score', 'radar score', 'radar score air', 'radar score sea', 'weapon score', 'speed score', 'range score', 'avalaibility', 'manutenability score (mttr)', 'reliability score (mtbf)'`.
- `SHIP: Dict` (riga 1449) — popolato righe 1451-1464 iterando `Ship_Data._registry.values()`, con esattamente le 10 chiavi elencate in `SCORES` (**qui coerente**, a differenza di `VEHICLE`/`SCORES` in `Vehicle_Data.py`). Nessuna chiave `physical_characteristics`.
- `get_ship_data(model) -> Dict` (riga 1469) — ritorna `SHIP[model]`, `ValueError` se non registrato.
- `get_ship_scores(model, scores: Optional[List]=None) -> Dict` (riga 1486) — **implementazione corretta** (a differenza dell'equivalente in `Vehicle_Data`): `scores=None` di default → usa `list(SCORES)`; validazione per-elemento `invalid = [s for s in scores if s not in SCORES]`. Funziona come atteso.

### `Ship_Weapon_Data.py`

- Struttura dichiaratamente analoga a `Ground_Weapon_Data.py` ma per 5 categorie: `MISSILES_SAM`, `MISSILES_ASM`, `MISSILES_TORPEDO`, `GUNS`, `CIWS`.
- Template di efficienza (`_EFF_SAM_SHORAD/MERAD/LORAD`, `_EFF_ASM_ANTISHIP_SUBSONIC/CRUISE_LANDATTACK/SUPERSONIC/SUPERSONIC_HEAVY`, `_EFF_TORPEDO_LIGHT/HEAVY`, `_EFF_NAVAL_GUN_76/100/127/130MM`, `_EFF_CIWS`) — principio dichiarato nella memoria di progetto: `score = accuracy × destroy_capacity`, ordine atteso `Soft > Armored > ship > Structure > Hard`; `accuracy` = specializzazione dell'arma, `destroy_capacity` = fragilità del bersaglio una volta colpito. Verificato coerente con la struttura dati osservata (dizionari `efficiency[target_type][dim] = {'accuracy':..., 'destroy_capacity':...}`), stesso schema di `Ground_Weapon_Data`.
- `get_sam_score`, `get_asm_score`, `get_torpedo_score`, `get_gun_score`, `get_ciws_score` — scorer per categoria.
- `get_weapon_score(weapon_type, weapon_model) -> float` — dispatcher.
- `get_ship_weapon(model) -> Optional[Dict]` — ricerca per nome modello su tutte le categorie (analogo a `get_weapon` in `Ground_Weapon_Data`).
- `get_weapon_score_target(model, target_type: List, target_dimension: List) -> float` / `get_weapon_score_target_distribuition(model, target_type: Dict, target_dimension: Dict) -> float` — stesso schema List-based / Dict-based di `Ground_Weapon_Data`.
- Import: **nessuna dipendenza da `Aircraft`** — `Ship_Data.py` e `Ship_Weapon_Data.py` importano solo da `Context`, `Utility.LoggerClass`, `dataclasses`, `typing`. Modulo pulito rispetto al problema di import circolare (vedi sotto).

## Dipendenze

- `Vehicle.py` → `Mobile`, `Vehicle_Data` (`get_vehicle_data`, `get_vehicle_scores`), `Block`, `Utility`, `LoggerClass`, `DataType.Event/Payload/Volume`, `Context.Context` (`GROUND_COMBAT_EFFICACY, GROUND_ACTION, AIR_DEFENSE_ASSET, BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET, ACTION_TASKS, GROUND_MILITARY_VEHICLE_ASSET, Ground_Vehicle_Asset_Type`), `sympy.Point3D`.
- `Vehicle_Data.py` → `Ground_Weapon_Data` (`get_weapon_score`, `get_weapon_score_target`, `get_weapon_score_target_distribuition`), `Context.Context` (`GROUND_ACTION, ACTION_TASKS, BLOCK_ASSET_CATEGORY, Ground_Vehicle_Asset_Type`), `Utility.LoggerClass`, `Utility.Utility.convert_mph_to_kmh`, `sympy`, `tabulate`, `pandas`, `dataclasses`.
- `Ground_Weapon_Data.py` → **`Asset.Aircraft`** (import non utilizzato nel modulo, causa della catena di import circolare — vedi sotto), `Utility.Utility`, `Context.Context` (`TARGET_CLASSIFICATION, GROUND_WEAPON_TASK`), `Utility.LoggerClass`, `Utility.Utility` (`true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude`), `sympy`.
- `Ship.py` → `Utility.Utility`, `Mobile`, `Ship_Data` (`get_ship_data`, `get_ship_scores`), `Block`, `LoggerClass`, `DataType.Event/Payload/Volume`, `Context.Context` (`SEA_MILITARY_CRAFT_ASSET, BLOCK_ASSET_CATEGORY, BLOCK_INFRASTRUCTURE_ASSET`), `sympy.Point3D`.
- `Ship_Data.py` → `Context.Context` (`SEA_TASK, ACTION_TASKS, Sea_Asset_Type`), `Utility.LoggerClass`, `dataclasses`. **Nessun import di `Aircraft` o `Ground_Weapon_Data`.**
- `Ship_Weapon_Data.py` → `Context.Context` (`TARGET_CLASSIFICATION`), `Utility.LoggerClass`. **Nessun import di `Aircraft`.**

### Import circolare — punto di aggancio confermato

`Ground_Weapon_Data.py:5` esegue `from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft`. Questo aggancia la catena:

```
Ground_Weapon_Data → Aircraft → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft (partially initialized)
```

Verificato con test diretto da root del repository:

```
$ .direnv/python-3.12/bin/python3 -c "from Code.Dynamic_War_Manager.Source.Asset import Vehicle"
ImportError: cannot import name 'Aircraft' from partially initialized module
'Code.Dynamic_War_Manager.Source.Asset.Aircraft' (most likely due to a circular import)
```

Poiché `Vehicle.py → Vehicle_Data.py → Ground_Weapon_Data.py → Aircraft.py`, **qualunque import di `Vehicle` (diretto o transitivo tramite `Vehicle_Data`/`Ground_Weapon_Data`) fallisce oggi**, in ambiente pulito (senza mock/stub pre-iniettati in `sys.modules`).

Al contrario, `Ship.py → Ship_Data.py` e `Ship_Weapon_Data.py` **non importano `Aircraft`** e non sono coinvolti in questa catena:

```
$ .direnv/python-3.12/bin/python3 -c "from Code.Dynamic_War_Manager.Source.Asset import Ship"
Ship import OK
```

Questo è confermato anche dai risultati dei test (vedi sotto): i test di `Ship_Data`/`Ship_Weapon_Data` passano interamente, mentre quelli di `Vehicle_Data`/`Ground_Weapon_Data`/`Vehicle` falliscono già in fase di `import` del modulo di test, prima di eseguire un solo test.

Nota importante per chi lavora sul sottosistema Asset-Air: l'import `Aircraft` in `Ground_Weapon_Data.py` risulta **inutilizzato** nel corpo del file (nessun riferimento al simbolo `Aircraft` al di fuori del commento di riga 1116). La rimozione di questo singolo import (di competenza del sottosistema Asset-Air, qui solo segnalata) sembrerebbe sufficiente a disaccoppiare `Vehicle`/`Vehicle_Data`/`Ground_Weapon_Data` dalla catena circolare, senza toccare `Ship`.

## Stato attuale

### Bug noti (con riferimento file:riga)

1. **`Vehicle_Data.get_vehicle_scores` — validazione rotta, blocca ogni istanziazione di `Vehicle`.** `Vehicle_Data.py:4646` — `if scores and scores not in SCORES:` confronta l'intero argomento `scores` (lista/tupla) contro gli elementi stringa di `SCORES`, anziché validare elemento-per-elemento. Con l'uso di default (`Vehicle.py:61`, chiamata senza l'argomento `scores`) la condizione è sempre vera → `ValueError` sistematico. **Confermato per lettura statica del codice** (non eseguibile a runtime a causa del bug di import circolare — vedi punto 4 — quindi non verificabile con un test diretto in questo momento, ma la logica è inequivocabile). Confronto: `Ship_Data.get_ship_scores` (`Ship_Data.py:1505`) implementa la validazione corretta con una list comprehension — il pattern giusto esiste già nel codice, solo non applicato a `Vehicle_Data`.
2. **`Vehicle.get_physical_characteristics()` / `Ship.get_physical_characteristics()` — sempre `None`.** `Vehicle.py:218-226`, `Ship.py:140-148`. Entrambi i metodi leggono `get_vehicle_data(model)` / `get_ship_data(model)`, che restituiscono rispettivamente `VEHICLE[model]` (`Vehicle_Data.py:4567-4581`) e `SHIP[model]` (`Ship_Data.py:1451-1464`) — dizionari di **soli punteggi normalizzati**, che non includono mai la chiave `'physical_characteristics'`. I dati fisici reali risiedono solo su `Vehicle_Data._registry[model].physical_characteristics` / `Ship_Data._registry[model].physical_characteristics`, mai esposti tramite le funzioni pubbliche usate da queste due classi. Effetto a cascata: `Vehicle.set_volume_from_physical_characteristics()` non imposta mai `self.volume` automaticamente (logga solo un warning).
3. **`Ship.loadAssetDataFromContext()` — due bug indipendenti che ne impediscono l'esecuzione.** `Ship.py:53,66` — chiama `self.block.isMilitary()`/`isLogistic()` (camelCase), ma `Block` espone solo `is_military()`/`is_logistic()` (snake_case, verificato in `Block.py:452,456`) → `AttributeError` certo alla prima chiamata. Anche correggendo il naming, `Ship.py:56,69` itera `for k, v in asset_data[self.category]:` su un `dict` senza `.items()` → fallirebbe comunque nello spacchettamento. Il metodo equivalente in `Vehicle.py:98,127` usa correttamente `.items()`.
4. **Import circolare `Ground_Weapon_Data → Aircraft`** — `Ground_Weapon_Data.py:5`. Rende **non importabile** `Vehicle`, `Vehicle_Data` e lo stesso `Ground_Weapon_Data` in un ambiente Python pulito (verificato con test diretto, vedi sopra e sezione Dipendenze). L'import risulta inutilizzato nel file. `Ship`/`Ship_Data`/`Ship_Weapon_Data` non sono coinvolti e si importano correttamente.
5. **`Ship.combatPower`** — `Ship.py:113-115` — dichiarato `@property` con un parametro `task` extra (incompatibile con la semantica di property) e corpo `pass`. Non implementato, non richiamabile con l'API prevista. A differenza di `Vehicle`, la classe `Ship` **non ha alcun equivalente funzionante di `set_combat_power()`**: `Ship.__init__` non calcola punteggi di combattimento né chiama `set_combat_power_value` di `Mobile`.
6. **Getter/setter morti in `Vehicle_Data`** — righe ~101-117 (`engine`, `model`, `made` definiti due volte come metodi senza `@property`, poi mascherati dagli attributi istanza omonimi impostati in `__init__`). Codice inerte, nessun impatto funzionale osservato ma fonte di confusione.
7. **Docstring disallineata in `Ground_Weapon_Data.get_weapon_score_single_target`** — `Ground_Weapon_Data.py:1273-1386`. La docstring descrive `caliber_factor` e `ammo_factor` come parte della formula, ma il codice li ha commentati (righe 1349-1377): la formula realmente eseguita è solo `raw * (1 - variability)`.
8. **`SCORES` vs contenuto reale di `VEHICLE`** — `Vehicle_Data.py:4471` dichiara 8 chiavi di score, ma il dict `VEHICLE[model]` popolato a righe 4567-4581 ne contiene 12 (mancano da `SCORES`: `weapon score`, la chiave dinamica `weapon target effectiveness [...]`, `communication score`, `hydraulic score`, `range score`). In `Ship_Data.py` le due strutture (`SCORES` a riga 85, `SHIP[model]` a righe 1451-1464) sono invece coerenti tra loro.
9. **`FLAME_TRHOWERS`** — `Ground_Weapon_Data.py` — categoria dichiarata in `GROUND_WEAPONS` ma vuota (`{}`) e con refuso nel nome (manca la "o": dovrebbe essere `FLAME_THROWERS`). Nessuna arma definita in questa categoria.

### Fatti storici da aggiornare nella memoria di progetto

- `STAMPA` in `Vehicle_Data.py` **non è più `True`**: allo stato attuale del codice (`Vehicle_Data.py:4669`) vale `STAMPA = False`. Il side-effect di stampa tabelle + generazione PDF all'import **non si verifica più**. Il fatto noto storico riportato nella memoria è superato.
- Il nome file veicolo con trattini (`"M1A2-Abrams"`, `"Leopard-2A6M"`, `"M2-Bradley"`) è confermato nella lista di istanziazioni `Vehicle_Data(**...)` a fine file (righe ~4474-4550).

### Copertura test e risultati reali (eseguiti oggi con `.direnv/python-3.12/bin/python3 -m unittest discover ...`)

| Test file | Risultato |
|---|---|
| `Test_Vehicle_Data.py` | **FALLISCE in import** — `ImportError` per la catena circolare `Ground_Weapon_Data → Aircraft` (0 test eseguiti) |
| `Test_Ground_Weapon_Data.py` | **FALLISCE in import** — stessa causa (0 test eseguiti) |
| `Test_Ship_Data.py` | **OK — 145 test, tutti superati** |
| `Test_Ship_Weapon_Data.py` | **OK — 153 test, tutti superati** |
| `Test_Vehicle.py` | **FALLISCE in import** — stessa causa circolare (0 test eseguiti) |
| `Test_Ship.py` | **File inesistente** — nessun test dedicato alla classe `Ship` (solo `Ship_Data`/`Ship_Weapon_Data` hanno copertura) |

In sintesi: **l'intera metà "terrestre" del sottosistema (Vehicle/Vehicle_Data/Ground_Weapon_Data) è oggi non testabile e non importabile** in un ambiente pulito a causa del bug di import circolare (punto 4 sopra), il che significa che i bug 1 e 2 (get_vehicle_scores, get_physical_characteristics) non possono nemmeno essere verificati con un test automatico finché il problema di import non è risolto — sono confermati solo per lettura statica del codice. La metà "navale" (Ship_Data/Ship_Weapon_Data) è invece pienamente testata e verde, ma la classe runtime `Ship` stessa non ha alcuna copertura di test.

## Problemi aperti

- **Gap UML Ship**: non esiste alcun diagramma PlantUML per `Ship.py`, `Ship_Data.py`, `Ship_Weapon_Data.py` in `Analysis/UML/` (esistono solo `Vehicle.plantuml`, `Vehicle_Data.plantuml`, `Ground_Weapon_Data.plantuml`). Da valutare se produrre `Ship.plantuml`, `Ship_Data.plantuml`, `Ship_Weapon_Data.plantuml` seguendo lo stesso stile (component/class/activity diagram) usato per gli equivalenti terrestri.
- **Priorità di fix**: il bug di `get_vehicle_scores` (punto 1) blocca *ogni* uso pratico della classe `Vehicle` con un modello valido — è probabilmente il bug singolo più impattante dell'intero sottosistema terrestre e andrebbe corretto prima di qualunque altro lavoro su `Vehicle`. Va deciso se il fix debba rispecchiare esattamente il pattern già corretto in `Ship_Data.get_ship_scores` (list comprehension `[s for s in scores if s not in SCORES]`).
- **Chi possiede la rimozione dell'import `Aircraft` in `Ground_Weapon_Data.py`?** L'import è inutilizzato in questo file e sembra la causa diretta del blocco totale di `Vehicle`/`Vehicle_Data`/`Ground_Weapon_Data`. La rimozione tocca però un file che il sottosistema Asset-Air considera di sua competenza (`Ground_Weapon_Data → Aircraft` fa parte della catena documentata anche lì) — va coordinato tra i due sottosistemi per evitare fix duplicati o in conflitto.
- **`Ship` è strutturalmente meno maturo di `Vehicle`**: non ha un `set_combat_power()` funzionante né un `combatPower` implementato, e `loadAssetDataFromContext()` ha due bug che ne impediscono l'esecuzione. Va chiarito se `Ship` sia effettivamente usato altrove nel motore di campagna oggi (nessun test lo esercita) o se sia ancora in fase di stub — questo determina l'urgenza dei fix.
- **`get_physical_characteristics()` rotto su entrambe le classi**: va deciso se il fix corretto è (a) far restituire a `get_vehicle_data`/`get_ship_data` anche i dati fisici accanto ai punteggi, oppure (b) far accedere `Vehicle`/`Ship` direttamente a `Vehicle_Data._registry[model]`/`Ship_Data._registry[model]` per questo dato specifico, bypassando le funzioni "scores".
- **Incoerenza `SCORES` vs `VEHICLE[model]`** (punto 8): da chiarire se `SCORES` in `Vehicle_Data.py` debba essere esteso alle 12 chiavi realmente popolate (allineandolo al pattern corretto già presente in `Ship_Data.py`), una volta risolto anche il bug di validazione del punto 1.
- **`FLAME_TRHOWERS`**: categoria vuota con refuso nel nome — da chiarire se è un placeholder per sviluppo futuro (lanciafiamme non ancora modellati) o va rimossa.
