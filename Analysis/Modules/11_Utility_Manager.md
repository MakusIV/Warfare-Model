# Utility e Manager (nucleo/entry point)

## Scopo

Questo sottosistema raggruppa due categorie di codice molto diverse per maturità:

1. **Utility trasversali** (`Utility/LoggerClass.py`, `Utility/Utility.py`, `Utility/visualizer.py`): funzioni di supporto generiche (logging, geometria, fuzzy logic, conversioni di unità, validazione di tipo) usate — o pensate per essere usate — da tutti gli altri sottosistemi. Sono "infrastruttura", non logica di dominio.
2. **`Manager.py`**, alla radice di `Source/`: il candidato più naturale per essere il "DWM" (Dynamic War Manager) descritto nello schizzo architetturale (`Analysis/Document/WM_Software_Structure.pdf`) — il nucleo che dovrebbe ricevere `mission_param` da DCS (via i moduli Lua/Python di scambio dati), aggiornare lo stato della campagna, e produrre `mission_result`.

La conclusione principale di questa analisi è che **nessuno dei due pezzi realizza oggi l'orchestrazione end-to-end descritta nel PDF**: le utility sono una cassetta degli attrezzi eterogenea con diversi bug mai esercitati da test, e `Manager.py` è uno scheletro che non si istanzia nemmeno con i parametri più semplici. Il layer Lua↔Python di scambio dati esiste solo come intenzione (commenti, un campo dati e una directory hard-coded), non come codice funzionante.

## File inclusi

- `Code/Dynamic_War_Manager/Source/Utility/LoggerClass.py` (60 righe) — classe `Logger`, wrapper su `logging` standard
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py` (1127 righe) — funzioni di supporto generiche: geometria 2D/3D con `sympy`, fuzzy logic con `scikit-fuzzy`, conversioni di unità aeronautiche, validazione, hashing/naming
- `Code/Dynamic_War_Manager/Source/Utility/visualizer.py` (156 righe) — modulo di plotting 3D con `matplotlib` (classi `Cylinder`, `Path3D`, `Space`), **non importato da nessun altro modulo del progetto** — è uno script sperimentale a sé stante (ha un blocco `if __name__ == "__main__":` di demo)
- `Code/Dynamic_War_Manager/Source/Manager.py` (105 righe) — classe `Manager`, unico file alla radice di `Source/` oltre a `__init__.py`

Non esiste alcun file di test per nessuno dei quattro moduli: confermato con `ls Code/Dynamic_War_Manager/Source/Test/` — non compaiono `Test_Manager.py`, `Test_Utility.py`, `Test_LoggerClass.py` né `Test_visualizer.py` nell'elenco (che include invece `Test_Air_Resources_Assigner.py`, `Test_Region.py`, `Test_Military.py`, ecc. — quindi l'assenza non è un problema di naming, questi moduli semplicemente non sono mai stati testati).

## Utility — funzioni principali

### `LoggerClass.py`
- Classe `Logger(module_name, class_name, set_consolle_log_level=WARNING, set_file_log_level=DEBUG, name=None)`: wrapper su `logging.getLogger(module_name)` con due handler (console + file). Il file di log è `logs/log_<class_name>.log`, relativo alla working directory corrente (`os.getcwd()`), non al percorso del progetto — quindi il file di log finisce in posizioni diverse a seconda da dove viene lanciato il processo.
- Pattern d'uso standard in tutto il progetto: `logger = Logger(module_name=__name__, class_name='NomeClasse').logger`, poi `logger.debug/info/warning/error(...)`.
- `getLogger()` restituisce l'oggetto `logging.Logger` sottostante (ridondante con l'attributo pubblico `self.logger`, già usato ovunque).
- Bug noto: se `class_name` è fornito ma non corrisponde alla classe/modulo reale che istanzia il logger (vedi `Manager.py`, sotto), i log finiscono nel file sbagliato — non è un bug di `LoggerClass` in sé, ma un rischio strutturale del pattern (nessuna verifica automatica che `class_name` coincida con `__class__.__name__` del chiamante).
- Ogni chiamata a `Logger(...)` esegue `logging.basicConfig(level=DEBUG)` (riga 37) e crea nuovi handler che vengono aggiunti al logger nominato — poiché `logging.getLogger(module_name)` restituisce sempre la stessa istanza per lo stesso nome, istanziare più `Logger` con lo stesso `module_name` (es. import ripetuti/reload) accumula handler duplicati, con conseguente duplicazione dei messaggi in console/file. Non essendoci `Test_LoggerClass.py`, questo comportamento non è verificato.

### `Utility.py`
Funzioni raggruppabili per area:

- **Naming/ID**: `setId(name, id=None)` genera un id basato su hash SHA-256 + UUID se non fornito; `setName(name)` aggiunge un suffisso numerico casuale (1-9999) al nome.
- **Validazione**: `validate_class(obj, class_name: str) -> bool` (righe 948-953) — controlla se `class_name` è presente nella MRO (`inspect.getmro`) della classe di `obj`; è il meccanismo usato altrove nel progetto per evitare `isinstance()` diretto e aggirare gli import circolari (vedi memoria di progetto). `checkEventType(_type)` (riga 263-265) referenzia una costante globale `EVENT_TYPE` **mai definita né importata in questo file** → se chiamata, solleva `NameError`; è probabilmente un residuo di refactoring (la costante vive forse in `Context.py` ma non è importata qui). `check_side(side)` valida `side in ['Blue','Red','Neutral']`. `enemySide(side)` inverte `Blue`/`Red` (torna `'Neutral'` per qualunque altro valore, incluso `'Neutral'` stesso).
- **Geometria 2D/3D** (con `sympy`): `segment_equation`, `point_in_segment`, `get_Semisphere`, `line_Intersect`, `tangent_to_semisphere`, `mean_point` (baricentro di una lista di `Point2D`/`Point3D`, righe 824-850), `rotate_vector`, `normalize_vector`, `get_direction_vector`, `getFormattedPoint`.
  - `calcVectorDiff` (righe 293-295), `calcVectorSum` (righe 298-300): **bug** — la componente `z` del risultato usa erroneamente `vect2[1]`/`vect1[1]` invece di `vect2[2]`/`vect1[2]` (es. `calcVectorDiff` restituisce `(vect2[0]-vect1[0], vect2[1]-vect1[1], vect2[1]-vect1[2])`: il terzo termine mischia l'indice `1` di `vect2` con l'indice `2` di `vect1`).
  - `calcScalProd` (righe 303-306): **bug** analogo — il secondo termine del prodotto scalare usa `vect1[1]*vect2[2]` invece di `vect1[1]*vect2[1]` (il terzo termine `vect1[2]*vect2[2]` è invece corretto). Il prodotto scalare risultante è quindi matematicamente errato per qualunque vettore con componenti y/z diverse.
  - Nessuna di queste funzioni ha test associati: i bug non sono mai stati rilevati automaticamente.
- **Fuzzy logic** (`scikit-fuzzy`): `calc_Production_Target_Priority`, `calc_Storage_Target_Priority`, `calc_Transport_Line_Target_Priority`, `calc_Threat_Level`, `evaluateMorale` — sistemi di controllo fuzzy Mamdani con Antecedent/Consequent/Rule, usati (secondo i docstring) da `Military`/`Production`/`Storage`/`Transport` per calcolare priorità e morale. I docstring segnalano "TEST: OK CON JUPYTER NOTEBOOK" per tre di queste funzioni: la validazione è avvenuta storicamente fuori dal repository (notebook non incluso), non tramite `unittest`.
- **Conversioni aeronautiche**: `indicated_air_speed`, `true_air_speed`, `true_air_speed_at_new_altitude`, `mph_2_meters_per_second`, `meters_per_second_2_mph`, `convert_feet_to_meters/meters_to_feet`, `convert_mph_to_kmh/kmh_to_mph`.
  - **Bug grave** in `indicated_air_speed` (righe 972-975): `k = 9.44 * 10^-6` e `k = 2.876 * 10^-3` usano l'operatore `^` (XOR bit a bit su interi in Python), non l'elevamento a potenza (`**`). `10^-6` non vale `0.000001` ma `-16` (XOR bit a bit); il risultato è `k` negativo e enormemente sbagliato (verificato: `9.44 * (10^-6)` = `-151.04`, `2.876 * (10^-3)` = `-25.884` invece di `~0.0000094` e `~0.002876`). La funzione `indicated_air_speed()` produce quindi valori privi di senso fisico per qualunque input. `true_air_speed()` non ha lo stesso bug (usa una formula di densità diversa che non passa per `^`).
- **Varie**: `getClassName(obj)`, `get_sub_string(id_str, chiave)` (parsing di stringhe tipo `"chiave:valore."`).

### `visualizer.py`
- Contiene una **seconda implementazione** di `Cylinder` (righe 9-22), distinta e incompatibile con la classe `Cylinder` "ufficiale" di `Code/Dynamic_War_Manager/Source/DataType/Cylinder.py`, che è quella realmente usata dal resto del progetto (es. `Asset/Mobile.py` importa da `DataType.Cylinder`, non da qui — vedi memoria di progetto: `air_defense_volume() → Optional[Cylinder]`).
- Le altre classi (`Path3D`, `Space`) offrono visualizzazione 3D/2D con `matplotlib` (vista dall'alto, vista 3D, vista combinata) di cilindri (es. per rappresentare bolle di minaccia contraeree) e percorsi. Utile in teoria per debug visivo di `air_defense_volume()`/`combat_range()`, ma **non collegato a nessun punto reale del codice** — nessun modulo lo importa.
- `matplotlib.use('TkAgg')` in testa al file (riga 2) rende il modulo dipendente da un backend grafico interattivo disponibile a runtime: importarlo in un ambiente headless (es. CI, server) può fallire o richiedere configurazione aggiuntiva.
- Stato: prototipo/scratch isolato, probabilmente usato manualmente durante lo sviluppo per ispezionare geometrie, mai integrato né testato.

## Manager.py — analisi del nucleo DWM

### Cosa fa oggi
`Manager.__init__(region: str, blocks: Optional[Dict[str, Block]] = None)` fa tre cose:
1. Salva `region` (una stringa) e un dizionario opzionale di blocchi già pronti.
2. Istanzia `self._limes = Limes(self._region)` (riga 28).
3. Chiama `self._initialize_blocks()` (righe 35-41), che crea e assegna a `self._blocks` cinque blocchi hardcoded: `Military(self._region)`, `Production(self._region)`, `Storage(self._region)`, `Transport(self._region)`, `Urban(self._region)` — uno per ciascuna delle sottoclassi di `Block` esistenti nel progetto.

Oltre a questo, la classe definisce solo metodi di validazione (`_is_valid_block`, `_validate_block_param`, `_validate_all_params`, `_validate_dict_param`, `_validate_param`) e `__repr__`/`__str__`. **Non esiste alcun metodo pubblico di orchestrazione**: non c'è un `run()`, `step()`, `process_mission()`, `evaluate()` o equivalente. La sezione di commenti alle righe 49-53 elenca ad alto livello i tre "livelli" di valutazione previsti (coalizione → regione → blocco → resource manager del blocco) ma non è seguita da alcuna implementazione: sono commenti di intento, non codice.

**Verificato empiricamente che `Manager` non si può nemmeno istanziare**: chiamare `Manager('TestRegion')` solleva immediatamente
```
TypeError: Bad Arg: points must be a Dict:{ 'name': str, 'position': Point2D }
```
Il problema è alla riga 28: `Limes(self._region)` passa una stringa (il nome della regione) al costruttore di `Limes` (`Code/Dynamic_War_Manager/Source/DataType/Limes.py`, riga 22), che invece si aspetta `points: Dict` — un dizionario `{nome: {'name': str, 'position': Point2D}}` di punti che delimitano il confine geografico della regione. Non essendoci passaggio esplicito di questo dizionario nel costruttore di `Manager`, l'oggetto fallisce sempre, per qualunque input. Di conseguenza `_initialize_blocks()` (righe 35-41) non viene mai raggiunto.

Ulteriori problemi strutturali, indipendenti dal bug bloccante:
- **Riga 16**: `logger = Logger(module_name=__name__, class_name='Region')` — `class_name` è `'Region'`, non `'Manager'`. È quasi certamente un copia-incolla da `Region.py` mai corretto: i log di `Manager` finiscono nel file `logs/log_Region.log`, mescolati (o in conflitto) con quelli reali di `Region`.
- **Righe 57-59**: `_is_valid_block(block)` controlla `block.__class__.__name__ == 'Block'` — un confronto sul nome letterale della classe, non una `isinstance()` o una risalita della MRO (a differenza di `Utility.validate_class`, disponibile nello stesso progetto). Questo significa che nessuno dei blocchi realmente creati da `_initialize_blocks()` (`Military`, `Production`, `Storage`, `Transport`, `Urban` — tutte sottoclassi di `Block`, non istanze dirette di `Block`) supererebbe mai questa validazione: `_validate_dict_param` e `_validate_block_param`, se invocati sui blocchi reali del `Manager`, fallirebbero sempre.
- **Righe 97-106**: `__repr__` e `__str__` referenziano attributi che `Manager` non possiede (`self._name`, `self._description`, `self._side`, `self._clients`, `self._server`, `self._warehouse`) — anche questi sono copiati verbatim da `Region.py` (che possiede quegli attributi) e mai adattati a `Manager`. Chiamare `repr(manager_instance)` o `print(manager_instance)` solleverebbe `AttributeError`. In più `__repr__` (righe 97-102) ha un bug di sintassi indipendente: le righe della tupla restituita terminano con virgola dopo la parentesi di chiusura della f-string, per cui la funzione restituisce una **tupla di stringhe** invece di una singola stringa concatenata (violando la convenzione Python per cui `__repr__` deve restituire `str`).
- Il commento alla riga 18 (`# NOTA: valuda un preload di Block, Asset, della regione ecc`) conferma che anche l'autore considerava il modulo un punto di partenza, non un'implementazione conclusa.

### Cosa importa (quanto è "collegato" al resto del sistema)
`Manager.py` importa: `Context` (modulo), `Block`, `Military`, `Production`, `Storage`, `Transport`, `Urban` (da `Block/`), `Limes` e `Payload` (da `DataType/`), `Logger` (da `Utility/`), oltre a `sympy` per tipi geometrici (`Point`, `Line`, `Point2D`, `Point3D`, `Line3D`, ecc. — nessuno di questi è però usato nel corpo della classe, sono importati e basta).

Questo elenco di import mostra che l'intenzione architetturale è corretta (il `Manager` dovrebbe aggregare tutti i blocchi funzionali di una regione), ma **l'integrazione si ferma alla riga di istanziazione**: nessun metodo chiama `military.get_recognition_report()`, `production.run_management_cycle()` o equivalenti sugli altri sottosistemi (`Component/Resource_Manager`, `Logic/Military_Resources_Assigner`, `Logic/Air_Resources_Assigner`, `Context/Campaign_State`, `Context/Target_Status_History` — tutti moduli maturi e testati, descritti in altre parti della knowledge base — non sono mai importati né citati in `Manager.py`).

**`Manager` non è mai importato da nessun altro file del progetto** (verificato con grep ricorsivo su tutto `Source/`): è un modulo completamente isolato, orfano, non raggiungibile da alcun punto di ingresso reale del sistema.

### Layer Lua↔Python / mission_param / mission_result: gap rispetto all'architettura target
Cercando riferimenti a `Lua`, `mission_param`, `mission_result` e `DCS_DATA_DIRECTORY` in tutto `Source/` (non solo in `Manager.py`), il quadro è il seguente:

- **`mission_param` e `mission_result`**: nessuna occorrenza in tutto il codice sorgente. Questi due concetti, centrali nello schizzo del PDF (DCS scambia "mission param"/"mission result" con i moduli Lua, che poi dialogano con il DWM), non esistono ancora come strutture dati o funzioni in nessun punto del progetto.
- **`Context.py`, riga 15**: `DCS_DATA_DIRECTORY = 'E:\\Sviluppo\Warfare_Model\\Code\\Persistence\\DCS_Data'` — una directory hardcoded per Windows (commento: *"att dcs funziona solo in windows quindi path solo per formato windows"*), pensata per contenere le tabelle di scambio Lua↔Python descritte nel PDF. **Questa costante non è mai letta né scritta da nessun altro punto del codice** (grep conferma che appare solo nella propria definizione): è un placeholder, non un meccanismo funzionante di I/O.
- **`Logic/Scenario_Manager.py`** (242 righe): è il file che, più di `Manager.py`, contiene i segnali di intenzione relativi al layer Lua/DCS — ma è interamente un abbozzo. La classe definita si chiama `CommandControl` (non "Scenario_Manager": il nome del file non corrisponde al nome della classe). Contiene commenti-segnaposto seguiti da `pass`:
  - riga 130: `# reading and loading DCS data: reading from lua table and loading to python object` → `pass`
  - riga 133-134: `# evaluate mission result: from python object evaluate mission results` → `pass`
  - riga 136-137: `# execute simulation for virtual mission result...` → `pass`
  - riga 139-140: `# save mission result...` → `pass`
  - riga 239-240: `# execute strategical and tactical evaluation and planning...` → `pass`
  - riga 242-243: `# writing DCS data to lua table: writing from python object to lua table` → `pass`
  - Un lungo blocco di commenti/docstring (righe 159-235) descrive concettualmente un "C2 Planner" ispirato al modello TLC (Sequential Analytic Game Evaluation) e la creazione di percorsi/grafi DCS↔WM, ma resta pura documentazione di intento.
  - Bug che confermano lo stato di abbozzo: `checkParam` (righe 55-66) referenzia una classe `Region` mai importata nel file → `NameError` se invocato; `addBlock` (righe 80-84) fa `self._events.append(block)`, ma `self._events` non viene mai inizializzato in `__init__` (solo `self._blocks`/`self._regions` lo sono) → `AttributeError` certo alla prima chiamata.
  - **`CommandControl`/`Scenario_Manager.py` non è mai importato da nessun altro modulo** (le uniche corrispondenze di "CommandControl" altrove nel progetto sono occorrenze coincidenti della property `Vehicle.isCommandControl`, semanticamente non correlata).
- **`Asset/Asset.py`**: il costruttore accetta un parametro opzionale `dcs_unit_data` (riga ~99-101) e un metodo `_validate_dcs_data(data)` (righe ~522-540) verifica la struttura di un dizionario con chiavi tipiche DCS (`unit_name`, `unit_type`, `unitId`, `unit_frequency`, `unit_x`, `unit_y`, `unit_alt`, `unit_alt_type`, `unit_health`). Questo è il punto di ingresso concettualmente più vicino a un vero adattatore Lua→Python: **si aspetta di ricevere dati DCS già convertiti in un dict Python**, ma non fa nulla per produrre quel dict (nessuna lettura di file, nessun parsing Lua).
- **`Asset/Mobile.py`**: analogamente, `checkParamDCS(data: dict)` (righe 360-403) valida un set più ampio di campi DCS (posizione, velocità, payload, callsign, ecc.). Bug di robustezza: accede direttamente a `data["campo"]` senza `.get()`, quindi se un campo manca dal dizionario la validazione solleva `KeyError` invece di trattarlo come opzionale/assente — fragile per dati reali provenienti da un parser Lua incompleto o da versioni diverse dello schema.
- **`Context/Logistic_Lines.py`**, riga 41: il commento `#costruisce la classe con un DCS data seT` precede un `__init__` che in realtà non processa alcun dato DCS — dichiara solo un'annotazione di tipo senza assegnazione (`self._logistic_lines: Dict[str: Logistic_Line]`, riga 42), che **non inizializza l'attributo**: verificato empiricamente che dopo `Logistic_Lines()` l'attributo `_logistic_lines` non esiste sull'istanza (`hasattr` → `False`). Non è nello scope diretto di questo documento ma rinforza il quadro: ogni punto del codice che menziona "DCS data" nei commenti è, ad oggi, non implementato.

**Sintesi del gap**: esistono (a) un punto dati di ingresso già pensato a livello di singolo `Asset`/`Mobile` (`dcs_unit_data`, `checkParamDCS`) che si aspetta dizionari Python già pronti, e (b) un file (`Scenario_Manager.py`) con l'intenzione dichiarata di fare da ponte lettura/scrittura Lua↔Python a livello di scenario/campagna — ma **nessun codice reale legge o scrive file Lua, nessun parser Lua→Python esiste, nessuna funzione produce o consuma `mission_param`/`mission_result`, e la directory di scambio dati (`DCS_DATA_DIRECTORY`) non è mai acceduta**. L'intero layer Lua↔Python descritto nello schizzo architetturale è, allo stato attuale, assente: solo l'intenzione (commenti, nomi di campi dati, un path hardcoded) è tracciata nel codice.

## Stato attuale

| Modulo | Stato | Note |
|---|---|---|
| `LoggerClass.py` | Funzionante, usato ovunque | Nessun test dedicato; rischio di handler duplicati su import ripetuti; path di log relativo a `os.getcwd()` |
| `Utility.py` | Parzialmente funzionante | Diverse funzioni geometriche/di conversione con bug matematici mai rilevati (nessun test) |
| `visualizer.py` | Prototipo isolato | Non importato da nessuno; `Cylinder` duplicato/incompatibile con `DataType/Cylinder.py` |
| `Manager.py` | Non funzionante / orfano | Non si istanzia (`TypeError` da `Limes`); non importato da nessun altro modulo; nessun metodo di orchestrazione |
| `Logic/Scenario_Manager.py` (`CommandControl`) | Abbozzo puro | Bug bloccanti (`NameError`, `AttributeError`); tutte le sezioni "core" sono `pass`; non importato da nessuno |

Bug puntuali con riferimento file:riga:
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py:265` — `checkEventType` usa `EVENT_TYPE` non definito/importato → `NameError` se invocata
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py:293-295` — `calcVectorDiff`: componente z errata (usa indice 1 invece di 2)
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py:298-300` — `calcVectorSum`: stesso bug della componente z
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py:303-306` — `calcScalProd`: secondo termine errato (`vect2[2]` invece di `vect2[1]`)
- `Code/Dynamic_War_Manager/Source/Utility/Utility.py:973,975` — `indicated_air_speed`: `10^-6`/`10^-3` sono XOR bit a bit, non potenze; risultato numerico privo di senso (verificato: -151.04 e -25.884 invece di ~0.0000094 e ~0.002876)
- `Code/Dynamic_War_Manager/Source/Manager.py:16` — logger istanziato con `class_name='Region'` invece di `'Manager'`
- `Code/Dynamic_War_Manager/Source/Manager.py:28` — `Limes(self._region)` con stringa invece di `Dict` di punti → `Manager()` non si istanzia mai (verificato empiricamente)
- `Code/Dynamic_War_Manager/Source/Manager.py:57-59` — `_is_valid_block` confronta `__class__.__name__ == 'Block'` letteralmente, escludendo tutte le sottoclassi reali (`Military`, `Production`, `Storage`, `Transport`, `Urban`)
- `Code/Dynamic_War_Manager/Source/Manager.py:97-106` — `__repr__`/`__str__` referenziano attributi inesistenti su `Manager` (copiati da `Region.py`); `__repr__` inoltre restituisce una tupla invece di una stringa
- `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py:60` — `checkParam` usa `Region`, mai importato → `NameError`
- `Code/Dynamic_War_Manager/Source/Logic/Scenario_Manager.py:82` — `addBlock` usa `self._events`, mai inizializzato → `AttributeError`

Copertura test: **0%** per tutti e cinque i moduli analizzati (`LoggerClass.py`, `Utility.py`, `visualizer.py`, `Manager.py`, `Logic/Scenario_Manager.py`). Nessun file `Test_*.py` corrispondente esiste; nessuna funzione di `Utility.py` risulta chiamata/asserita direttamente da alcuna suite di test esistente (`grep "Utility\."` sui file `Test_*.py` non produce corrispondenze), quindi anche l'uso indiretto tramite mock non fornisce copertura reale del comportamento di queste funzioni.

## Problemi aperti

Cosa manca per rendere `Manager.py` un vero entry point funzionante (DWM end-to-end):

1. **Bug bloccante di istanziazione**: va risolto il mismatch fra `Manager.__init__` e `Limes.__init__` — o `Manager` deve costruire/ricevere un dizionario di punti valido per `Limes`, o `Limes` deve essere reso opzionale/lazy finché non servono davvero i calcoli geografici.
2. **Nessun metodo di orchestrazione**: manca completamente la logica che i commenti alle righe 49-53 di `Manager.py` promettono (valutazione priorità a livello coalizione → regione → blocco → resource manager). Serve almeno un metodo `run_cycle()`/`step()` che invochi in sequenza i moduli già maturi e testati altrove nel progetto (`Component/Resource_Manager.run_management_cycle()`, `Block/Military.get_recognition_report()`/`combat_state()`, `Logic/Military_Resources_Assigner.get_aircraft_mission()`, `Context/Campaign_State`, `Context/Target_Status_History`) — nessuno di questi è oggi collegato a `Manager`.
3. **Layer Lua↔Python assente**: non esiste alcun parser/writer Lua, nessuna funzione che legga da o scriva verso `DCS_DATA_DIRECTORY`, nessuna definizione di formato per `mission_param`/`mission_result`. Questo è il gap più rilevante rispetto allo schizzo architetturale: il PDF presuppone uno scambio file-based fra moduli Lua e Python (via "Data LVA" e storage intermedio), di cui nel codice Python non c'è traccia operativa — solo punti di validazione dati "già pronti" (`Asset.dcs_unit_data`, `Mobile.checkParamDCS`) che presuppongono un adattatore a monte mai scritto.
4. **`Logic/Scenario_Manager.py` va deciso**: è l'altro candidato naturale per il ruolo di orchestratore/ponte DCS, ma è ancora più indietro di `Manager.py` (bug bloccanti immediati, classe non importata da nessuno, corpo quasi interamente `pass`). Va chiarito se il progetto intende unificare `Manager` e `CommandControl` in un solo modulo, o mantenerli come livelli distinti (es. `Manager` = orchestratore di regione, `CommandControl`/scenario = orchestratore di campagna/scambio DCS).
5. **`Manager` è orfano**: nessun altro modulo lo importa. Prima di aggiungere funzionalità, va deciso chi dovrà istanziarlo e con quali parametri reali (oggi il costruttore richiede solo `region: str`, ma nessun chiamante esiste nel repository per validare che questa firma sia sufficiente).
6. **Bug nelle utility geometriche/di conversione** (`calcVectorDiff`, `calcVectorSum`, `calcScalProd`, `indicated_air_speed`) vanno corretti prima che qualunque modulo di dominio (es. calcoli di rotta, portata, geometria di minaccia) li usi in produzione: oggi sarebbero silenziosamente sbagliati, senza test a fare da rete di sicurezza.
7. **Assenza totale di test** per questo intero sottosistema: prima ancora di scrivere nuove funzionalità, servirebbero test di regressione minimi su `Utility.py` (in particolare le funzioni geometriche/di conversione, per fissare comportamento e intercettare i bug elencati) e su `Manager.py` (anche solo per documentare via test l'attuale non-istanziabilità, come baseline da cui partire per il fix).
8. **`visualizer.py`**: da decidere se integrarlo (es. come strumento di debug per `air_defense_volume()`/`combat_range()` di `Mobile`/`Military`) o rimuoverlo — nella forma attuale è codice morto che duplica una classe (`Cylinder`) già definita altrove in modo incompatibile, rischio di confusione futura.
