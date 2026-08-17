# Asset — Aviazione

## Scopo

Il sottosistema Asset-Air modella i velivoli militari gestiti dal Dynamic War Manager: dati tecnici/prestazionali del velivolo (`Aircraft_Data`), i carichi bellici installabili e la loro valutazione contro un target (`Aircraft_Loadouts`), il catalogo delle armi aria-aria/aria-suolo con i relativi punteggi di efficacia (`Aircraft_Weapon_Data`), e la classe applicativa `Aircraft` (sottoclasse di `Mobile`) che rappresenta l'istanza di velivolo come `Asset` di un `Block`. Il modulo alimenta gli algoritmi di assegnazione missione (`Military_Resources_Assigner`, `Air_Resources_Assigner`) con punteggi normalizzati di combattimento, per task e per efficacia contro tipologia/dimensione di target.

I quattro file formano una catena di dipendenza concettuale a strati (dati tecnico-velivolo → loadout → armi → istanza applicativa), ma — come dettagliato sotto — la catena si chiude anche a livello di **import Python**, creando un ciclo che oggi impedisce l'import pulito dell'intero sottosistema.

## File inclusi

| File                                                            | Righe | Contenuto principale                                                                                                                                                                             |
| --------------------------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft.py`             | 147   | `class Aircraft(Mobile)`                                                                                                                                                                         |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Data.py`        | 3477  | `class Aircraft_Data` (dataclass/registry), `AIRCRAFT` (dict punteggi precalcolati), `get_aircraft_data()`, `get_aircraft_scores()`                                                              |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Loadouts.py`    | 4042  | `AIRCRAFT_LOADOUTS` (dati), 17 funzioni modulo (`loadout_eval`, `loadout_target_effectiveness`, `loadout_target_effectiveness_by_distribuition`, `get_aircrafts_quantity`, `loadout_cost`, ecc.) |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` | 8146  | `AIR_WEAPONS` (dati), `WEAPON_PARAM`, 16 funzioni modulo (`get_weapon_score`, `get_weapon_score_target`, `get_weapon_efficiency`, `is_weapon_introduced`, `get_weapon_cost`, ecc.)               |

Diagrammi UML di riferimento: `Analysis/UML/Aircraft_Data.plantuml`, `Analysis/UML/Aircraft_Loadouts.plantuml`, `Analysis/UML/Aircraft_Weapon_Data.plantuml`. Non esiste un `Aircraft.plantuml` dedicato. I tre diagrammi esistenti sono coerenti con il codice attuale su nomi di funzioni/classi e dipendenze dichiarate (component diagram di `Aircraft_Data.plantuml` mostra correttamente `AD --> AL` verso `Aircraft_Loadouts`).

Test associati: `Test/Test_Aircraft_Data.py` (3202 righe, 210 metodi `test_*`), `Test/Test_Aircraft_Loadouts.py` (2605 righe, 178 metodi `test_*`), `Test/Test_Aircraft_Weapon_Data.py` (2363 righe, 267 metodi `test_*`). **Non esiste** `Test_Aircraft.py` — la classe `Aircraft` non ha copertura di test dedicata.

## Classi e funzioni principali

### `Aircraft.py`

`class Aircraft(Mobile)` (riga 26) — costruttore che delega quasi tutto a `Mobile.__init__`; aggiunge solo `self.speed = {"nominal": None, "max": None}`.

- `loadAssetDataFromContext()` (riga 45): popola `cost`/`value`/`requested_for_consume`/`repair_time`/`_payload_perc` da `AIR_MILITARY_CRAFT_ASSET` (ramo militare) o `BLOCK_INFRASTRUCTURE_ASSET` (ramo logistico). **Bug**: nessuno dei due nomi (`AIR_MILITARY_CRAFT_ASSET`, `BLOCK_INFRASTRUCTURE_ASSET`) è importato nel file → `NameError` certo se il metodo viene invocato. Anche `for k, v in asset_data[self.category]:` itera su un dict come se fosse una lista di coppie: se `asset_data[self.category]` è un `dict`, servirebbe `.items()` (probabile bug aggiuntivo, non verificabile a runtime senza i dati di `Context`).
- `checkParam(asset_type)` (riga 86): usa `AIR_MILITARY_CRAFT_ASSET` e `BLOCK_ASSET_CATEGORY`, anch'essi **non importati** → stesso bug di `NameError` a runtime.
- `combatPower` (riga 115): dichiarata `@property` ma con firma `def combatPower(self, task):` — una property in Python può accettare solo `self`; l'accesso `istanza.combatPower` solleverebbe `TypeError` (il protocollo property chiama `fget(obj)` con un solo argomento). Inoltre usa `AIR_COMBAT_EFFICACY`, non importato. Metodo di fatto non utilizzabile.
- Proprietà booleane `isFighter`, `isFighterBomber`, `isAttacker`, `isBomber`, `isHeavyBomber`, `isAwacs`, `isRecon`, `isTransport`, `isHelicopter` (righe 120-145): semplici confronti su `self.category`, corrette e funzionanti.

### `Aircraft_Data.py`

`class Aircraft_Data` (riga 62, decorata `@dataclass` ma con `__init__` scritto a mano — nessun campo annotato a livello di classe, quindi il decoratore `@dataclass` è di fatto inerte: non essendoci field annotati non genera nulla, e comunque un `__init__` esplicito ha sempre precedenza).

- `_registry: Dict[str, Aircraft_Data]` (attributo di classe, riga 63) — ogni `Aircraft_Data(**kwargs)` si auto-registra in `_registry[self.model] = self` (riga 83), pattern registry/singleton condiviso con `Vehicle_Data`/`Ship_Data`.
- **Getter/setter rotti** (righe 86-108): `engine()`, `roles()`, `cost()`, `model()`, `made()` sono definiti come metodi normali **senza `@property`/`@x.setter`**, e per giunta `self.engine`, `self.model`, ecc. vengono già assegnati come attributi di istanza in `__init__` (righe 66-82). Il risultato è che questi metodi sono **codice morto e non richiamabile**: dopo `__init__`, `istanza.engine` è un dict, non una funzione — chiamarlo come `istanza.engine()` darebbe `TypeError: 'dict' object is not callable`.
- `combat_score_eval(task, loadout, calc_scores_options, target_type=None, target_dimension=None)` (riga 710) — motore di scoring centrale: somma pesata di `engine`, `radar`, `TVD`, `radio_nav`, `hydraulic`, `avionics`, `loadout`, `speed`, con pesi diversi per task (`Fighter_Sweep`, `Intercept`) e per `calc_scores_options` (se `True` usa `_loadout_target_effectiveness`, se `False` usa `_loadout_eval` generico). Se il `task` non rientra in nessuno dei tre gruppi gestiti (`CAP/Intercept/Fighter_Sweep/Escort/Recon`, `Strike/CAS/Pinpoint_Strike/SEAD`, `Anti_Ship`) ritorna silenziosamente `0.0` con solo un `logger.warning`.
- `combat_score(task, loadout)` (riga 797) → `combat_score_eval(..., calc_scores_options=False)`, nessuna informazione sul target.
- `combat_score_target_effectiveness(task, loadout, target_type, target_dimension)` (riga 793) → `combat_score_eval(..., calc_scores_options=True, ...)`. **Confermato**: il punteggio totale **non è vincolato a [0,1]**. La componente loadout (riga 741: `self._loadout_target_effectiveness(...) * scores_weights['loadout'] / sum_weights`) dipende da `loadout_target_effectiveness()` in `Aircraft_Loadouts.py`, che a sua volta somma `get_weapon_score_target(...) * quantità_arma` per ogni pilone armato — nessuna normalizzazione superiore, quindi loadout con molte armi ad alta efficacia (es. F-14A con carico Phoenix in missione Fleet Defense, riportato in memoria progetto a ~2.6) possono spingere il totale ben oltre 1.
- `get_normalized_combat_score(...)` / `get_normalized_combat_score_target_effectiveness(...)` (righe 801, 812): normalizzano rispetto alla distribuzione degli score di tutti gli `Aircraft_Data._registry` filtrati per `category`; usano `self._normalize()` (riga 692, min-max classico, ritorna `0.5` se `max==min`).
- `get_loadouts(aircraft_name, task=None)` (riga 823): la docstring dichiara `Returns: list`, ma **in realtà ritorna un `dict`** (`{loadout_name: config}`) — delega a `get_aircraft_loadouts_by_task()`/`get_aircraft_loadouts()` di `Aircraft_Loadouts.py`, entrambe basate su dict. Documentazione disallineata dal comportamento reale.
- `get_list_of_aircrafts(side, task, target_distribuition, role=None, route_length=None, route_speed=None)` (riga 846): **contiene due bug distinti, entrambi confermati leggendo il codice**:
  1. **Loop morto** (righe 893-919): calcola per ogni velivolo lo score migliore su tutti i loadout del task e lo salva in `aircraft_list['score']`/`aircraft_list['aircraft']`, ma questi valori **non vengono mai usati** — la funzione ritorna invece un'espressione `sorted(...)` indipendente (riga 922) che ricalcola tutto da zero. Tempo di calcolo sprecato, nessun impatto sul risultato finale.
  2. **`StopIteration` per velivoli senza loadout del task** (riga 922): la sort key è `key=lambda x: x.combat_score(task, loadout=next(iter(self.get_loadouts(x.model, task))))`. Se `self.get_loadouts(x.model, task)` ritorna un dict vuoto (nessun loadout di quel velivolo supporta il `task` richiesto), `next(iter({}))` solleva `StopIteration`. Dentro una lambda passata a `sorted()` (non un generatore), l'eccezione **si propaga inalterata** — non viene convertita in `RuntimeError` da PEP 479 (quella conversione si applica solo a `StopIteration` sollevate dentro un frame di generatore) — quindi qualunque chiamante di `get_list_of_aircrafts` che non gestisca esplicitamente `StopIteration` andrà in crash non gestito appena la lista dei velivoli disponibili include anche un solo modello senza loadout per il task.
  3. Bug collaterale alla stessa riga 913: `ac.loadout_target_effectiveness_by_distribuition(...)` viene chiamato come **metodo su un'istanza `Aircraft_Data`**, ma `loadout_target_effectiveness_by_distribuition` è una funzione a livello di modulo importata in `Aircraft_Data.py` (riga 23), non un metodo della classe — chiamata che solleva `AttributeError: 'Aircraft_Data' object has no attribute 'loadout_target_effectiveness_by_distribuition'`. Questo bug è nella sezione del loop morto (punto 1) quindi il suo impatto pratico coincide con quello: il ramo con `target_distribuition` valorizzato va comunque in crash prima ancora di arrivare al bug dello `StopIteration`.
- `get_aircrafts_quantity(model, loadout, target_data, year=None)` (riga 924): valida l'esistenza del modello in `_registry` poi delega alla funzione omonima di `Aircraft_Loadouts.py` — corretto.
- **Effetto collaterale a livello di modulo** (righe 3432-3472): al termine del file, un blocco esegue un ciclo su tutti gli `Aircraft_Data._registry.values()` per popolare `AIRCRAFT[model]` con 14 punteggi normalizzati, seguito da un secondo blocco marcato `#TEST` (righe 3469-3472) che fa `print()` di ogni punteggio di ogni velivolo. **Qualunque `import` del modulo** (diretto o transitivo) stampa decine/centinaia di righe su stdout — verificato empiricamente durante l'analisi (vedi sezione Import circolare). Pattern analogo al noto `STAMPA=True` di `Vehicle_Data.py`, ma qui senza nemmeno un flag per disattivarlo.
- `get_aircraft_scores(model, scores=None)` (riga 3455): bug di validazione strutturalmente identico (ma con logica invertita) al bug noto di `Vehicle_Data.get_vehicle_scores()`. La condizione `if scores and scores in SCORES: raise ValueError(...)` confronta l'intera lista `scores` (parametro) contro la tupla `SCORES` di stringhe — `scores in SCORES` è sempre `False` perché una lista non è mai uguale a una stringa, quindi la validazione **non scatta mai**, qualunque contenuto abbia `scores`. Con l'uso previsto (`scores=None`, valore di default) il metodo va comunque in crash: `if scores and ...` è `False` per `scores=None` (nessun raise), ma poi `for score in scores:` itera su `None` → `TypeError: 'NoneType' object is not iterable`. La funzione è quindi **inutilizzabile con la firma di default** e non valida correttamente l'input anche quando viene passata una lista esplicita.

### `Aircraft_Loadouts.py`

`AIRCRAFT_LOADOUTS` (dict dati, dalla riga 40): loadout per modello velivolo, chiavi coerenti con `model` in `Aircraft_Data.py` e nomi arma coerenti con `AIR_WEAPONS` in `Aircraft_Weapon_Data.py`. Struttura per singolo loadout: `tasks`, `attributes`, `Lock_Down_Shoot_Down`, `self_escort_capability`, `cruise`/`attack` (performance), `usability`, `mandatory_support`, `stores.pylons` (`{n: [weapon_model, qty]}`).

- `from venv import logger` (riga 31): **import copiato male** — non è il `Logger` custom del progetto (`Utility.LoggerClass`), ma il logger stdlib del modulo `venv` (quello usato internamente da `python -m venv` per creare virtualenv). Verificato: l'import non fallisce (`venv.logger` esiste davvero come `logging.Logger` di libreria standard, livello `WARNING` di default), quindi il file si comporta "normalmente" senza eccezioni, ma le 8 chiamate `logger.info(...)`/`logger.warning(...)` nel file (righe 3824, 3855, 3889, 3894, 3903, 3907, 3910, 4004) **non passano mai per la configurazione di logging del progetto** (niente file handler dedicato, niente formattazione coerente con gli altri moduli) e all'atto pratico, essendo il logger a livello `WARNING`, i `logger.info(...)` non producono output. Comportamento silenzioso, non un crash — quindi facile da non notare in test/uso normale.
- `loadout_eval(aircraft_name, loadout_name)` (riga 3776): punteggio generico = `weapons_score*0.5 + score_phases*0.3 + score_ranges*0.2`, senza considerare alcun target. `weapons_score` somma `get_weapon_score(weapon[0]) * qty` su tutti i piloni.
- `loadout_target_effectiveness(aircraft_name, loadout_name, target_type: List, target_dimension: List, route_length, route_speed)` (riga 3800): prima verifica l'idoneità del loadout alla rotta (velocità/gittata effettiva con fattore di incremento fino a 1.3×), ritorna `0.0` se non approvato; altrimenti somma `get_weapon_score_target(weapon[0], target_type, target_dimension) * qty` — qui `target_type`/`target_dimension` sono già liste (parametro della funzione), passate direttamente, corretto.
- `loadout_target_effectiveness_by_distribuition(aircraft_name, loadout_name, target_distribution, route_length, route_speed)` (riga 3833): stessa logica di approvazione rotta, poi valuta lo score pesato su una distribuzione di target (`{tipo: {perc_type, perc_dimension: {dim: pct}}}`) con validazione delle somme (`perc_type_sum≈1`, `perc_dimension_sum≈1` per ogni tipo, tolleranza `0.01`). **Confermato**: la chiamata a `get_weapon_score_target` (riga 3923) avvolge esplicitamente i valori in liste — `get_weapon_score_target(weapon[0], [target_type], [target_dimension])` — perché la funzione richiede liste e qui si itera su tipo/dimensione singoli per volta; il bug storico (accumulo con `score *=` invece di variabile locale `dim_score`, citato in memoria) **non è presente** nel codice attuale: si usa correttamente `dim_score` locale per ogni combinazione (tipo × dimensione).
- `get_weapon_efficiency`, `loadout_year_compatibility`, `get_aircrafts_quantity`, `loadout_cost` (righe 3929, 3957, 3968, 4032): funzioni di supporto, lette e coerenti con le rispettive docstring/firme.

### `Aircraft_Weapon_Data.py`

`AIR_WEAPONS` (dict dati, riga 952) — catalogo armi per categoria (`MISSILES_AAM`, `MISSILES_ASM`, `BOMBS`, `ROCKETS`, `CANNONS`, `MACHINE_GUNS`, …), ciascuna con `weapons_data.efficiency[target_type][dimension] = {accuracy, destroy_capacity}`.

- `get_weapon(model)` (riga 281): ricerca lineare del modello in tutte le categorie di `AIR_WEAPONS`.
- `is_missile/is_bomb/is_rocket/is_cannon/is_machine_gun(model)` (righe 302-405): dispatch per categoria.
- `get_weapon_score(model)` (riga 730) e `get_weapon_score_target(model, target_type: List, target_dimension: List)` (riga 765): il secondo **richiede esplicitamente liste**, non stringhe — verificato leggendo l'implementazione (righe 803-819): itera `for t_type in target_type: ... for t_dim in target_dimension:`. Se invece di una lista si passasse una stringa (es. `"Soft"` invece di `["Soft"]`), Python la itererebbe comunque (le stringhe sono iterabili) ma carattere per carattere (`'S'`, `'o'`, `'f'`, `'t'`), ognuno confrontato contro `TARGET_CLASSIFICATION`/`TARGET_DIMENSION` e scartato con un warning perché nessun singolo carattere è un tipo di target valido → la funzione non solleva eccezione ma **restituisce silenziosamente `0.0`**, un errore logico difficile da diagnosticare senza conoscere questo vincolo.
- `get_weapon_efficiency`, `is_weapon_introduced`, `get_weapon_cost` (righe 823, 896, 930): funzioni di supporto coerenti con le rispettive firme.
- Post-processing a livello di modulo (righe ~970 in avanti): assegna `weapon_param_type` a ogni voce di `AIR_WEAPONS` che compare in `_WEAPON_PARAM_TYPE`. Nessun effetto collaterale di stampa (a differenza di `Aircraft_Data.py`).
- **Import inutilizzato e strutturalmente pericoloso** (riga 5): `from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft`. Verificato con `grep` mirato su tutto il file: il nome `Aircraft` (la classe importata) **non viene mai usato** nel corpo del file — le uniche occorrenze della stringa `"Aircraft"` sono chiavi di dizionario (`weapon['efficiency']['Aircraft']`, decine di occorrenze), non riferimenti alla classe. Questo import è la causa diretta della chiusura del ciclo di import (vedi sezione dedicata) ed è del tutto superfluo.

## Dipendenze

- `Aircraft.py` → `Block.Block`, `Asset.Mobile`, **`Asset.Aircraft_Data`** (import inutilizzato, vedi sopra), `Utility.Utility`, `Utility.LoggerClass`, `DataType.{Event,Volume,Threat,Payload,State}`, `sympy.Point3D`.
- `Aircraft_Data.py` → `Context.Context` (`AIR_MILITARY_CRAFT_ASSET`, `AIR_TASK`, `Air_Asset_Type`, `COALITIONS`), `Utility.LoggerClass`, `Utility.Utility`, **`Asset.Aircraft_Loadouts`**, `sympy.Point3D`.
- `Aircraft_Loadouts.py` → `Context.Context` (`AIR_TASK`, `MAX_AIRCRAFT_TYPE_FOR_MISSION`), stdlib `venv.logger` (bug, vedi sopra), **`Asset.Aircraft_Weapon_Data`**.
- `Aircraft_Weapon_Data.py` → `Context.Context` (`AIR_MILITARY_CRAFT_ASSET`, `AIR_TASK`, `TARGET_CLASSIFICATION`, `AIR_TO_AIR_TASK`, `AIR_TO_GROUND_TASK`, `Weapon_Area_Effect`, `Weapon_Power_Effect`), **`Asset.Aircraft`** (import inutilizzato, vedi sopra), `Utility.Utility`, `Utility.LoggerClass`, `sympy.Point3D`.

Moduli esterni al sottosistema Asset-Air che dipendono da questi 4 file (dipendenza in ingresso): `Logic/Military_Resources_Assigner.py`, `Logic/Air_Resources_Assigner.py`, `Logic/Strategical_Evaluation.py`/`Logic/Tactical_Evaluation.py` (uso indiretto tramite `Aircraft`), e transitivamente `Asset/Mobile.py` (che importa `Vehicle_Data`/`Ship_Data`/`Ground_Weapon_Data`/`Ship_Weapon_Data` **localmente dentro i metodi**, proprio per evitare di dover importare la catena `Aircraft_*` a livello di modulo — workaround già documentato in `Analysis/Modules/03_Asset_Base.md`).

## Stato attuale

**Verificato oggi (2026-08-16) con esecuzione reale, non solo lettura statica:**

- **L'intero sottosistema non è importabile in un processo Python pulito**, in nessuna delle 4 combinazioni testate (`from ... import Aircraft_Data`, `Aircraft_Loadouts`, `Aircraft_Weapon_Data`, `Aircraft`, sia da riga di comando sia via `unittest discover`/`python -m`). Tutte falliscono con `ImportError: cannot import name '...' from partially initialized module '...' (most likely due to a circular import)`. Vedi sezione dedicata per l'analisi della catena e le proposte di fix.
- **`Test_Aircraft_Data.py`, `Test_Aircraft_Loadouts.py`, `Test_Aircraft_Weapon_Data.py` falliscono tutti e tre già in fase di `import`** quando eseguiti con `unittest discover` da repo root (comando standard del progetto), con `errors=1` e nessun test effettivamente eseguito. Confermato con:
  ```
  .direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Aircraft_Data.py"
  .direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Aircraft_Loadouts.py"
  .direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Aircraft_Weapon_Data.py"
  ```
  Tutti e tre terminano con `FAILED (errors=1)`. A differenza di altri moduli del progetto (es. `Test_Mobile.py`, `Test_Vehicle.py`), **questi tre file di test non pre-iniettano mock in `sys.modules` prima dell'import** — importano direttamente il modulo sotto test in testa al file — quindi non hanno alcun meccanismo di bypass del ciclo. Le note di memoria che riportano "210/178/267 test" come base di partenza numerica sono corrette come conteggio di metodi `test_*` presenti nel sorgente, ma **nessuno di questi test è oggi effettivamente eseguibile**: 0 test passano, 0 falliscono per motivi applicativi — l'intera suite è bloccata all'import.
- **Causa radice identificata con precisione chirurgica**: la chiusura del ciclo dipende da **due singole righe di import, entrambe inutilizzate nel corpo del rispettivo file**:
  - `Aircraft.py:4` — `from ...Aircraft_Data import get_aircraft_data, get_aircraft_scores`: nessuna delle due funzioni è mai chiamata nel file.
  - `Aircraft_Weapon_Data.py:5` — `from ...Aircraft import Aircraft`: la classe non è mai referenziata nel corpo del file (le uniche occorrenze della stringa `"Aircraft"` sono chiavi di dict).
  Rimuovendo **anche solo una delle due** (verificato empiricamente in una copia isolata del repository, vedi sezione dedicata), l'intera catena si importa senza errori.
- **Il modulo `Aircraft_Data.py` stampa su stdout ad ogni import** (righe 3432-3472): un doppio ciclo su tutti gli aeromobili registrati che calcola e poi ristampa 14 punteggi per velivolo. Verificato empiricamente: l'import di prova ha prodotto centinaia di righe di `print()` (es. `An-30M Radar score air: 0.00`, ecc.) prima di completarsi. Effetto collaterale rumoroso ma non bloccante, analogo al pattern `STAMPA` di `Vehicle_Data.py` citato in memoria, qui però privo di un flag di disattivazione.
- Nessun bug è stato osservato nella logica di dominio "core" già isolabile dalla lettura statica (calcolo degli score radar/TVD/motore/idraulica/avionica, valutazione loadout contro distribuzione target, catalogo armi) — questi appaiono internamente coerenti; tutti i bug trovati sono di natura **strutturale** (import, naming, type mismatch tra dict e list, property mal dichiarate) piuttosto che di formula.

**Bug puntuali con riferimento file:riga:**

| # | File:riga | Descrizione | Severità |
|---|---|---|---|
| 1 | `Aircraft_Weapon_Data.py:5` | Import inutilizzato di `Aircraft`, chiude il ciclo circolare | Alta — blocca l'intero sottosistema |
| 2 | `Aircraft.py:4` | Import inutilizzato di `get_aircraft_data`/`get_aircraft_scores`, chiude anch'esso il ciclo | Alta — blocca l'intero sottosistema |
| 3 | `Aircraft_Data.py:922` | `next(iter(...))` su loadout potenzialmente vuoto → `StopIteration` non gestita in `get_list_of_aircrafts` | Alta — crash a runtime su input realistico (velivolo senza loadout per il task) |
| 4 | `Aircraft_Data.py:913` | `ac.loadout_target_effectiveness_by_distribuition(...)` chiamato come metodo su istanza `Aircraft_Data`, ma è funzione di modulo → `AttributeError` | Alta — ma dentro un loop i cui risultati sono comunque scartati (vedi #5), quindi impatto pratico limitato al fatto che l'eccezione va comunque sollevata prima |
| 5 | `Aircraft_Data.py:893-919` | Loop che calcola score/aircraft ma il risultato non è mai usato dal `return` effettivo | Media — spreco di calcolo, nessun impatto sul risultato (se non ci fosse il bug #4 a monte) |
| 6 | `Aircraft_Data.py:3455-3467` | `get_aircraft_scores()`: validazione `scores in SCORES` sempre falsa (lista vs tupla di stringhe) + crash `TypeError` con `scores=None` (default) | Alta — funzione pubblica non utilizzabile con la firma di default |
| 7 | `Aircraft_Data.py:86-108` | Getter/setter (`engine`, `roles`, `cost`, `model`, `made`) senza `@property`, resi permanentemente irraggiungibili dagli attributi di istanza omonimi impostati in `__init__` | Bassa — codice morto, nessun impatto se non vengono mai chiamati (verificato: non lo sono, nel resto del sottosistema si accede sempre a `.model`, `.cost` ecc. come attributi diretti) |
| 8 | `Aircraft.py:54,67,93,102` | `AIR_MILITARY_CRAFT_ASSET`, `BLOCK_INFRASTRUCTURE_ASSET`, `BLOCK_ASSET_CATEGORY` usati ma non importati → `NameError` certo se `loadAssetDataFromContext()`/`checkParam()` vengono invocati | Alta — ma probabilmente mai esercitata a runtime (nessun test, nessuna chiamata trovata da altri moduli nel sottosistema) |
| 9 | `Aircraft.py:117` | `AIR_COMBAT_EFFICACY` non importato + `combatPower` dichiarata `@property` con parametro extra `task` → doppio motivo di crash se invocata | Alta (stesso discorso su probabile non uso) |
| 10 | `Aircraft_Loadouts.py:31` | `from venv import logger` invece del `Logger` di progetto — logging silenzioso/non configurato, non un crash | Bassa — funzionale ma "invisibile" |
| 11 | `Aircraft_Data.py:3432-3472` | Print massivo su stdout ad ogni import del modulo | Bassa — rumore, non blocca, ma inquina l'output di qualunque comando che importi (anche indirettamente) il modulo |
| 12 | `Aircraft_Data.py:823-829` (docstring) | `get_loadouts()` dichiara `Returns: list` ma ritorna `dict` | Bassa — solo documentazione fuorviante, il codice chiamante (`get_list_of_aircrafts`) gestisce correttamente il dict |

## Import circolare — proposte di risoluzione

**Catena confermata (letta negli import di ciascun file ed eseguita per riprodurre l'errore):**

```
Aircraft.py  --(riga 4)-->  Aircraft_Data.py  --(riga 23)-->  Aircraft_Loadouts.py  --(riga 33)-->  Aircraft_Weapon_Data.py  --(riga 5)-->  Aircraft.py
```

Riprodotto con:
```
.direnv/python-3.12/bin/python3 -c "from Code.Dynamic_War_Manager.Source.Asset import Aircraft_Data"
→ ImportError: cannot import name 'get_aircraft_data' from partially initialized module
  'Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data' (most likely due to a circular import)
```

Nota di contesto: prima della correzione odierna del bug sistemico di import path, `Aircraft.py` importava `Mobile` con il percorso errato `from Dynamic_War_Manager.Source.Asset.Mobile import Mobile` (senza prefisso `Code.`), il che faceva fallire l'import di `Aircraft.py` **immediatamente**, con un `ModuleNotFoundError` diverso e più a monte, prima ancora di poter innescare il ciclo. È plausibile che il vero problema del ciclo fosse già presente da tempo ma **mascherato** da questo bug più superficiale — coerente col fatto che i test esistenti si affidano tutti a mock pesanti in `sys.modules` invece di un import reale, e nessuno lo ha mai notato.

**Scoperta chiave**: entrambe le importazioni che "chiudono" il ciclo (`Aircraft.py:4` verso `Aircraft_Data`, e `Aircraft_Weapon_Data.py:5` verso `Aircraft`) sono **codice morto** — nessun nome importato viene mai usato nel corpo del rispettivo file (verificato con grep mirato: `get_aircraft_data`/`get_aircraft_scores` non compaiono altrove in `Aircraft.py`; il simbolo `Aircraft` non compare altrove in `Aircraft_Weapon_Data.py`, solo la stringa `"Aircraft"` come chiave di dizionario in decine di voci `efficiency`). Questo cambia la natura del problema: non serve un refactoring architetturale per rompere il ciclo, bastano rimozioni di import inutilizzati.

**Verifica empirica** (eseguita in una copia isolata del repository sotto `/tmp`, simlink a livello di file per tutto tranne il file modificato, nessuna modifica al repository reale): rimuovendo **una sola** delle due righe, l'intera catena `Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft` si importa senza eccezioni in entrambi i casi testati separatamente.

### Opzione 1 (consigliata) — Rimuovere l'import inutilizzato in `Aircraft_Weapon_Data.py:5`

Eliminare `from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft`.

- **Pro**: una riga, zero righe di logica toccate, nessun comportamento cambia (l'import non era usato). Rompe il ciclo alla radice. `Aircraft_Weapon_Data.py` concettualmente non ha alcuna ragione di dipendere da `Aircraft` (è un catalogo dati arma, sotto ogni aspetto architetturale dovrebbe essere il livello più "a monte", senza dipendenze verso l'alto). Coerente con la direzione naturale delle dipendenze (dati → loadout → velivolo → istanza `Aircraft`).
- **Contro**: nessuno strutturale. Unico rischio è che in futuro qualcuno aggiunga codice in `Aircraft_Weapon_Data.py` che genuinamente necessiti della classe `Aircraft` (es. `isinstance` check) — in quel caso andrebbe reintrodotta con un import locale (dentro funzione) o `TYPE_CHECKING`, non a livello di modulo.

### Opzione 2 (equivalente) — Rimuovere l'import inutilizzato in `Aircraft.py:4`

Eliminare `from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import get_aircraft_data, get_aircraft_scores`.

- **Pro**: stesso beneficio dell'Opzione 1, stessa dimensione dell'intervento (una riga). Verificata empiricamente anch'essa sufficiente da sola.
- **Contro**: leggermente meno "naturale" architetturalmente — è plausibile che `Aircraft.py` in futuro debba effettivamente consultare `Aircraft_Data` (per popolare le proprietà del velivolo dai dati tecnici, cosa che oggi `loadAssetDataFromContext()` fa in modo diverso, guardando `Context`), quindi questo import potrebbe tornare utile prima di quello dell'Opzione 1.

### Opzione 3 (difensiva, cumulativa alle precedenti) — `TYPE_CHECKING` guard sui type hint

Se in futuro servisse comunque un riferimento al tipo `Aircraft` per annotazioni (es. `def foo(ac: "Aircraft") -> ...`) in `Aircraft_Weapon_Data.py` o riferimenti a `Aircraft_Data`/`Aircraft_Loadouts`/`Aircraft_Weapon_Data` per annotazioni in `Aircraft.py`, usare `if TYPE_CHECKING: from ... import X` (già presente come import in tutti e 4 i file, mai sfruttato per questo scopo) invece di import a livello di modulo. Questo pattern è **già lo standard nel resto del progetto** (vedi `Mobile.py.air_defense_volume()`/`combat_range()` che importano `Vehicle_Data`/`Ship_Data` localmente dentro il metodo proprio per evitare di reintrodurre questo stesso ciclo).

- **Pro**: risolve in modo permanente e "a prova di futuro" il problema, indipendentemente da quali import risultino usati o meno in un dato momento; pattern già adottato altrove nel progetto (consistenza).
- **Contro**: più invasivo delle Opzioni 1/2 se applicato da subito (richiederebbe toccare 4 file invece di 1); da solo non serve oggi (gli import da eliminare sono già dead code, non servono nemmeno come type hint).

**Raccomandazione**: applicare l'Opzione 1 (o equivalentemente la 2) subito — è la modifica minima, a rischio pressoché nullo, che sblocca l'intero sottosistema e i suoi test. Adottare la disciplina dell'Opzione 3 (import locali o `TYPE_CHECKING`) come convenzione per qualunque futura dipendenza incrociata fra questi 4 file, per evitare di reintrodurre lo stesso problema.

## Problemi aperti

- **Perché `Aircraft_Weapon_Data.py` importava `Aircraft` se non lo usa?** Possibile residuo di refactoring (una funzione che faceva `isinstance(x, Aircraft)` poi rimossa) oppure import "per abitudine"/autocompletamento mai ripulito. Da chiedere all'autore se c'è un uso previsto non ancora implementato, prima di rimuoverlo definitivamente.
- **`loadAssetDataFromContext()` e `checkParam()` in `Aircraft.py` sono mai stati eseguiti con successo?** Usano 3-4 nomi mai importati nel file (`AIR_MILITARY_CRAFT_ASSET`, `BLOCK_INFRASTRUCTURE_ASSET`, `BLOCK_ASSET_CATEGORY`, `AIR_COMBAT_EFFICACY`). Nessun test esiste per `Aircraft.py`, quindi non è chiaro se questi metodi siano mai stati validati o se siano rimasti allo stato di stub abbozzato. Da chiarire se vadano completati (aggiungendo gli import mancanti + verificando la logica `for k,v in dict:` vs `.items()`) o riscritti da zero.
- **`combatPower` come `@property` con parametro `task`**: è chiaramente non funzionante così com'è. Va convertita in metodo normale (`def combatPower(self, task):`, senza `@property`) oppure va ripensata come property senza argomenti se il task deve essere ricavato altrimenti? Da chiedere l'intento originale.
- **`get_list_of_aircrafts()` — qual è il comportamento voluto quando nessun loadout del velivolo copre il task richiesto?** Oggi crasha con `StopIteration`. Va escluso silenziosamente il velivolo dalla lista (coerente con l'omonimo controllo già presente nel loop morto, righe 903-905, che fa `continue` con un `logger.warning`), o deve essere un errore esplicito? Il loop morto (righe 893-919) suggerisce che l'intento originale fosse proprio quello di scartare i velivoli senza loadout — la funzione va probabilmente riscritta per usare quel loop come base reale invece del secondo blocco `sorted()` indipendente.
- **`get_aircraft_scores()` — qual è l'uso previsto?** Nessun chiamante di questa funzione è stato individuato all'interno del sottosistema Asset-Air stesso (sarebbe da verificare con una ricerca sui moduli `Logic/`); prima di sistemare la validazione bisognerebbe capire se è ancora utile così com'è o se va allineata all'equivalente (anch'esso buggato, per un motivo diverso) in `Vehicle_Data.get_vehicle_scores()`.
- **Priorità di intervento**: vista la severità (blocca l'intero sottosistema e tre file di test da centinaia di test complessivi), si raccomanda di trattare la rimozione dell'import circolare (Opzione 1) come prerequisito quasi immediato per qualunque altro lavoro su questi 4 file — oggi nessuna modifica a `Aircraft_Data`/`Aircraft_Loadouts`/`Aircraft_Weapon_Data` può essere verificata con un test reale (solo con mock), il che rende rischiosa qualunque futura modifica.
