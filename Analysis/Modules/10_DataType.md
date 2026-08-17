# DataType — Tipi Dato di Base

## Scopo

Il package `DataType` (`Code/Dynamic_War_Manager/Source/DataType/`) raccoglie i tipi dato "primitivi" del progetto, trasversali a tutti gli altri sottosistemi: geometria (aree, volumi, cilindri, sfere), stato di salute degli oggetti (`State`), carico economico (`Payload`), eventi generici (`Event`), minacce (`Threat`) e struttura di rotta (`Waypoint`, `Edge`, `Route`, `Limes`). Sono classi "foglia" pensate per essere importate da `Asset/`, `Block/`, `Context/`, `Logic/`, senza dipendenze verso quei package (con l'eccezione di `Edge.py`, che importa `Asset` solo per un type hint — vedi sotto).

Lo stato del package è eterogeneo: alcune classi sono solide e testate (`State`, `Payload`, `Cylinder`), altre sono scheletri incompleti mai finiti (`Volume`, `Area`, `Limes`, `Sphere`/`Hemisphere` come classi indipendenti), una (`Threat`) è strutturalmente non istanziabile, una (`Classi.py`) è codice orfano non collegato al resto del progetto, e due (`Edge`, `Waypoint`) hanno bug di validazione che le rendono di fatto "non protette" pur funzionando nel percorso comune.

## File inclusi

| File | Righe | Descrizione |
|---|---|---|
| `Area.py` | 118 | Area 2D (`SHAPE2D`, raggio, centro) alla base di `Volume`. `checkParam` presente ma logicamente inerte (vedi bug); `inside()` è uno stub. |
| `Classi.py` | 188 | File anomalo: definisce da zero `Payload`, `Point`, `Segment`, `Block`, `Asset`, `Production`, `Urban`, `Storage`, `Transport`, `Military` — nomi che duplicano classi reali altrove nel progetto ma con implementazioni giocattolo/incomplete (metodi `pass`). **Non importato da nessun altro modulo** (verificato via grep in tutto `Code/Dynamic_War_Manager/Source`). È scratch/prototipo residuo, non un modulo attivo. |
| `Cylinder.py` | 924 | Cilindro 3D standalone (non eredita da `Volume`). Geometria completa: distanze, tangenti, intersezioni con segmenti/rette, verifica punto interno. Usato realmente da `Mobile.air_defense_volume()` e da `Logic/Air_Route_Manager.py` (classe `ThreatAA`). Ha test dedicati (`Test_Cylinder.py`, 15 test, OK). |
| `Edge.py` | 203 | Arco di rotta (waypoint A→B con tipo percorso, pericolo, velocità). **Vedi sezione dedicata sotto** — firma reale documentata con precisione, più bug critici nel corpo di `__init__`. |
| `Event.py` | 121 | Evento generico con `EventParams` (dataclass ausiliaria) e `Event` (tipo, timer, energia/potenza/massa, posizione, asset_id, destinazione). Validazione tramite `_validate_all_params`/`_validate_param`, corretta e funzionante. Alcuni metodi (`isPush`, `isPop`, `isHit`, ecc.) leggono `self._type` che non viene mai impostato in `__init__` (solo `self._event_type` esiste) — bug latente. |
| `Hemisphere.py` | 201 | Semisfera 3D standalone (centro + raggio), geometria analoga a `Sphere` (area, volume, punto interno/esterno, distanza da superficie). Nessuna relazione di classe con `Sphere`/`Volume`/`Cylinder`. |
| `Limes.py` | 112 | Confine poligonale di una `Region`, definito da punti in coda (`deque`). `__init__` è rotto (vedi Stato attuale): solleva `AttributeError` anche chiamato senza argomenti. `calcDistance` (logica vicino/lontano da un punto) e `inside()` (stub) sono gli altri metodi. |
| `Payload.py` | 229 | Carico economico/risorse (`goods`, `energy`, `hr`, `hc`, `hs`, `hb`). Classe matura: validazione, `__repr__/__str__`, operatori di confronto e aritmetici (`+ - * / division`) tutti implementati e coerenti. Ha test dedicati (`Test_Payload.py`, 7 test, OK). |
| `Route.py` | 147 | Contenitore dati di una rotta: `route_type`, dizionario `edges` (`{(wpA,wpB): Edge}`), calcoli aggregati (lunghezza, tempo di viaggio, danger level, velocità). Nessun algoritmo di pathfinding. **Vedi sezione dedicata sotto.** |
| `Sphere.py` | 137 | Sfera 3D standalone, geometria completa (area, volume, intersezioni con segmenti/rette/altre sfere, tangenti da punto esterno). Nessuna relazione con `Volume`/`Cylinder`. |
| `State.py` | 240 | Stato di salute di un `Block`/`Asset`: `health` (0-100), `state_value` (`StateCategory`: Healthful/Damaged/Critical/Destroyed/Unknow), `success_ratio` per task. Classe matura e ben testata (`Test_State.py`, 67 test, OK). `isCritical()` verificato corretto (vedi sotto). |
| `Threat.py` | 58 | Minaccia generica (`level`, `name`, `id`). **Strutturalmente non istanziabile** — vedi Stato attuale. Importa `Sphere`/`Hemisphere` ma non li usa mai nel corpo della classe. |
| `Volume.py` | 79 | Volume 3D basato su `Area` + `SHAPE3D` (+ `radius_at_height` per forme "solide"). Non eredita da/verso `Cylinder` o `Sphere` nonostante li importi (import inutilizzati). `inside()` è uno stub. Firma `__init__` incompatibile con le chiamate reali nel codice (vedi Stato attuale). |
| `Waypoint.py` | 105 | Punto di rotta: `point` (sympy `Point3D`), `name`, `reference` (`Asset` opzionale). Stesso pattern di validazione "inerte" di `Edge`/`Area` (vedi Stato attuale). |

## Classi principali

### `Edge.py` — firma reale e comportamento (analisi richiesta per 07_Logic_Routing.md)

Firma **attuale e autoritativa** di `Edge.__init__` (riga 15-21 di `Code/Dynamic_War_Manager/Source/DataType/Edge.py`), verificata anche con `inspect.signature`:

```python
def __init__(self,
             wpA: Waypoint,
             wpB: Waypoint,
             path_type: str,
             danger_level: float | None,
             speed: float | None,
             name: str | None):
```

Ordine parametri: **`wpA, wpB, path_type, danger_level, speed, name`** — nessun parametro ha un default, tutti e 6 sono obbligatori (oltre a `self`). Nessuna keyword-only, nessun `*args`/`**kwargs`.

**Bug nel corpo di `__init__` (righe 32-33)**, entrambi mai raggiunti se mancano argomenti (Python valida il binding dei parametri prima di eseguire il corpo):
- Riga 32: `self._lenght = self.calcLenght(self)` — chiama un metodo **inesistente** (`calcLenght`, refuso: il metodo reale definito a riga 154 si chiama `calcLength`), e per giunta passa `self` come argomento extra. Se questa riga venisse eseguita (cioè se tutti e 6 gli argomenti fossero forniti correttamente), l'istanza fallirebbe con `AttributeError: 'Edge' object has no attribute 'calcLenght'` **prima ancora che venga eseguita la validazione** (`checkParam`, riga 36).
- Riga 33: `self._travel_time = self.calcTravelTime(self)` — stesso pattern: `calcTravelTime` esiste (riga 158) ma prende solo `self`, quindi passare un `self` esplicito extra causerebbe `TypeError: calcTravelTime() takes 1 positional argument but 2 were given` (mai raggiunto perché la riga 32 fallisce prima).
- `checkParam` (riga 44) è definito **senza il parametro `self`** e senza `@staticmethod`: `def checkParam(wpA, wpB, path_type, danger_level, speed, name)`. Chiamato come `self.checkParam(wpA, wpB, path_type, danger_level, speed, name)` (riga 36), Python antepone implicitamente `self`, producendo **7 argomenti per 6 parametri** → `TypeError`. Nei setter delle proprietà (es. `self.checkParam(name=param)`, riga 71) il binding "funziona" per conteggio ma è semanticamente errato: `self` occupa lo slot di `wpA`, e gli altri parametri restano non forniti (nessun default) → `TypeError: missing required positional arguments`.
- Anche se `checkParam` venisse chiamato correttamente, il controllo del risultato è inerte: riga 38 `if not check_results[1]:` legge l'indice 1 (il messaggio stringa, sempre truthy sia in caso di successo `"OK"` sia di errore) invece dell'indice 0 (il booleano) → la validazione **non solleva mai eccezioni**, qualunque sia l'esito. La riga 39 referenzia inoltre `check_results[2]`, indice inesistente su una tupla a 2 elementi (mai raggiunta per via del bug precedente, quindi mascherata).

**Conclusione per l'indagine 07_Logic_Routing.md**: il test fallito `Test_Air_Route_Manager.py` **non usa affatto `DataType.Edge`**. Il file di test importa con wildcard `from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import *` (riga 10), che porta in scope una classe `Edge` **locale e completamente diversa**, definita in `Logic/Air_Route_Manager.py` (riga 172):

```python
def __init__(self, name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float):
```

La chiamata del test `Edge("Test Edge", self.wp_a, self.wp_b, 100)` (riga 1163) fornisce 4 argomenti posizionali che si legano a `name, order_position, wpA, wpB` lasciando `speed` non risolto → `TypeError: Edge.__init__() missing 1 required positional argument: 'speed'`, **riprodotto ed esattamente confermato** eseguendo il codice (vedi sotto). Il bug è quindi nel test (o nella classe `Logic.Air_Route_Manager.Edge`, che ha un parametro `order_position` in più rispetto a quanto il test si aspetta), **non** in `DataType.Edge` — che ha una firma diversa e propri bug indipendenti, mai toccati da questo test.

Verifica eseguita:
```
>>> inspect.signature(Air_Route_Manager.Edge.__init__)
(self, name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float)
>>> Edge("Test Edge", wp_a, wp_b, 100)
TypeError: Edge.__init__() missing 1 required positional argument: 'speed'
```
che coincide esattamente col messaggio riportato nel task.

### `Route.py`

```python
def __init__(self, route_type: str, edges: dict, name: str | None)
```
`edges` è un dizionario `{(wpA, wpB): Edge}`. A differenza di `Edge`/`Waypoint`/`Area`, il `checkParam` di `Route` è un `@staticmethod` corretto, con default (`name=None, route_type=None, edges=None`) e con controllo `if not check_results[0]` (indice giusto) — la validazione qui **funziona davvero**. Metodi aggregati: `minDistance`, `travelTime` (somma `v.calcTravelTime()`), `travelTimeToEdge`, `length` (somma `v.calcLength()` — nota: chiama il metodo con lo spelling corretto, coerente con la definizione reale di `Edge`, ma se un `Edge` viene mai istanziato la creazione stessa fallirebbe per il bug di `__init__` sopra descritto), `max/min/avg_danger_level`, `max/avg_speed`.

### `Cylinder.py`

Classe standalone (non eredita da `Volume`): `__init__(self, center: Point3D, radius: float, height: float)`. Metodi principali: `distanceFromCirconference`, `distanceFromCenter`, `pointOfCirconference`, `innerPoint` (verifica altezza + raggio), `getTangentPoints`/`getTangents`/`getTangents2D`, `getIntersectionA`/`getIntersection` (con `Segment3D`), `getExtendedPoints`, `find_chord_coordinates`/`find_chord_endpoint`. È la classe geometrica più matura e completa del package (924 righe), usata realmente da `Mobile.air_defense_volume()` (che restituisce `Optional[Cylinder]`) e da `Logic/Air_Route_Manager.ThreatAA` per il calcolo delle intersezioni rotta/minaccia.

### `State.py`

`isCritical()` (righe 174-175):
```python
def isCritical(self):
    return self._state_value == StateCategory.CRITICAL.value
```
**Confermato corretto** — nessun refuso residuo (`isCrytical` non esiste più nel file). Presenti e coerenti anche `isOperative`, `isHealtful`, `isDestroyed`, `isDamaged`. La transizione di stato è pilotata da `update()` in base a soglie fisse in `HEALTH_LEVEL` (Damaged=0.8, Critical=0.5, Destroyed=0.15, su `health/100`).

## Dipendenze e relazioni tra tipi

**Non esiste una gerarchia di ereditarietà tra `Volume`, `Cylinder`, `Sphere`, `Hemisphere`, `Threat`.** Sono quattro/cinque classi *sorelle indipendenti*, non collegate da `class X(Y)`:

- `Volume` compone un `Area` (2D) + una forma `SHAPE3D` + eventualmente `radius_at_height`; importa (ma non usa mai) `Sphere` e `Hemisphere`.
- `Cylinder` è del tutto autonomo: nessun import né uso di `Volume`/`Area`/`Sphere`.
- `Sphere` e `Hemisphere` sono geometrie autonome, quasi gemelle (stesso stile di implementazione, probabilmente scritte nella stessa sessione), nessun collegamento a `Volume`/`Cylinder`.
- `Threat` importa `Sphere` e `Hemisphere` (righe 2-3) ma **non li usa mai** nel corpo della classe — l'idea originaria era probabilmente di rappresentare il volume di una minaccia con una `Sphere`/`Hemisphere`/`Cylinder`, ma l'implementazione non è mai stata completata (attributo `self._obj = obj`, riga 36, referenzia un parametro `obj` mai dichiarato in `__init__`).
- Nel codice realmente usato oggi, il "volume di minaccia/difesa aerea" è rappresentato con **`Cylinder`**, non con `Threat`/`Sphere`/`Volume`: `Mobile.air_defense_volume() -> Optional[Cylinder]` (package `Asset`) e `Logic.Air_Route_Manager.ThreatAA` (che incapsula un `Cylinder` insieme a `danger_level`, `interception_speed`, ecc.) sono gli usi concreti.

Altre dipendenze rilevate:
- `Edge.py` → `Waypoint`, `Context.PATH_TYPE`, `Asset` (solo per l'annotazione `obj_reference: Asset` interna a `Waypoint`, indirettamente), `sympy` (`Point3D`, `Line3D`, `Line2D`).
- `Route.py` → `Edge`, `Waypoint`, `Context.ROUTE_TYPE`.
- `Area.py`/`Volume.py`/`Limes.py` → `Context.SHAPE2D`/`SHAPE3D`/`AREA_FOR_VOLUME`.
- `Threat` è importato ed usato come **type-hint/validazione** in `Asset.py` (proprietà `threat`, riga 312-317) e in `Aircraft.py`, ma **mai istanziato realmente** nel codice di produzione (nessun `Threat(...)` trovato fuori da `DataType/Threat.py` stesso); in `Test_Asset.py` viene usato solo come `MagicMock(spec=Threat)`. Questo spiega perché il bug fatale di `Threat.__init__` (variabile `obj` non definita) non è mai emerso: la classe non viene mai concretamente costruita.
- `Volume` è importato e istanziato (con firma **incompatibile**) in `Asset/Vehicle.py:242` e `Asset/Structure.py:188`: `Volume(length=length, width=width, height=height)` — ma `Volume.__init__` accetta `(area_base, volume_shape, radius_at_height=None)`. Questa chiamata solleverebbe `TypeError: __init__() got an unexpected keyword argument 'length'` se il ramo di codice venisse eseguito (vedi Stato attuale).

## Divisione responsabilità Route.py vs Logic/*_Route_Manager.py

**Verifica effettuata leggendo `Route.py`, `Logic/Air_Route_Manager.py` (1474 righe) e `Logic/Ground_Route_Manager.py` (135 righe).**

L'ipotesi "Route.py contiene solo strutture dati, gli algoritmi di pianificazione stanno in Logic" è **vera solo per metà**: `Route.py` è davvero privo di logica di pathfinding (nessun algoritmo di ricerca, solo aggregazioni su un `edges` dict già costruito). Ma la parte sorprendente, verificata col grep degli import, è che:

- **`Logic/Air_Route_Manager.py` NON importa affatto `DataType.Waypoint`, `DataType.Edge` o `DataType.Route`.** Ridefinisce localmente proprie classi con lo stesso nome — `Waypoint` (riga 119), `Edge` (riga 169), `Route` (riga 218), più `Path` e `PathCollection` (righe 291+, assenti in `DataType`) e `ThreatAA` (riga 32, che invece **usa** `DataType.Cylinder`, unico import da `DataType` in questo file). Le firme sono diverse e incompatibili con le omonime di `DataType`: `Air_Route_Manager.Edge.__init__(self, name, order_position, wpA, wpB, speed)` vs `DataType.Edge.__init__(self, wpA, wpB, path_type, danger_level, speed, name)`; `Air_Route_Manager.Route.__init__(self, name, length, danger)` vs `DataType.Route.__init__(self, route_type, edges, name)`.
- **`Logic/Ground_Route_Manager.py` NON importa nulla da `DataType`** (nessun `from ... DataType ...` nel file). Definisce anch'esso proprie classi locali `Waypoint`, `Edge`, più `NavigationGraph` con gli algoritmi veri e propri (`find_optimal_path`, `find_min_danger_path`, `find_fastest_path`, `find_min_danger_fastest_path`).
- **`DataType.Route`/`Edge`/`Waypoint` sono comunque usati altrove come modello dati "ufficiale"**: `Context/Region.py` li usa per il campo `Region._routes: Dict[str, Route]` con API `add_route`/`get_route`/`get_shortest_route`/`get_safest_route`; `Block/Military.py` li usa nei type hint di `time_to_ground_intercept`/`time2attack`; `Logic/Tactical_Evaluation.py` li importa e li usa nei type hint di `evaluateGroundRouteDangerLevel` (con un probabile bug d'uso a riga 559: `for k, v_edge in Route.edges:` itera sull'attributo di **classe** — un oggetto `property` — anziché su un'istanza, il che solleverebbe `TypeError` se eseguito; bug fuori scope di questo documento, appartiene a `Logic/Tactical_Evaluation.py`).
- **Non esiste, nel codice attuale, alcun punto di integrazione tra i due mondi**: `Region.add_route()` non risulta mai chiamato da nessun modulo di produzione (solo definito), quindi non c'è oggi una pipeline che prenda l'output di `Air_Route_Manager`/`Ground_Route_Manager` (i loro `Path`/`Route` locali) e lo converta in `DataType.Route` da inserire in `Region`.

**Conclusione**: la separazione dati/algoritmi esiste solo a livello di intento — `DataType.Route/Edge/Waypoint` sono il modello "canonico" consumato da `Region`/`Military`/`Tactical_Evaluation`, mentre `Logic/Air_Route_Manager.py` e `Logic/Ground_Route_Manager.py` mantengono **proprie reimplementazioni locali e incompatibili** degli stessi concetti per i calcoli di pathfinding, senza alcun ponte che le colleghi. Questa duplicazione è la causa diretta della confusione riscontrata in `Test_Air_Route_Manager.py` (che testa la `Edge` locale di `Air_Route_Manager`, non quella di `DataType`).

## Stato attuale

**Bug noti (verificati con lettura del codice ed esecuzione):**

| File:riga | Bug |
|---|---|
| `DataType/Edge.py:32` | `self.calcLenght(self)` — refuso (metodo reale è `calcLength`, riga 154) + argomento `self` extra → `AttributeError` se raggiunta. |
| `DataType/Edge.py:33` | `self.calcTravelTime(self)` — argomento `self` extra su un metodo che accetta solo `self` → `TypeError` (mai raggiunta, mascherata dal bug precedente). |
| `DataType/Edge.py:44-59` | `checkParam` definito senza `self`/`@staticmethod` → chiamato come metodo d'istanza produce conteggio argomenti errato ovunque (righe 36, 71, 86, 100, 114, 129, 145). |
| `DataType/Edge.py:38` | `if not check_results[1]:` legge il messaggio anziché il booleano (indice 0) → validazione sempre inerte; riga 39 referenzia `check_results[2]` inesistente (dead code). |
| `DataType/Waypoint.py:30-39` | Stesso pattern di `checkParam` senza `self` e stesso bug `if not check_results[1]:` — validazione inerte + conteggio argomenti errato nei setter. |
| `DataType/Area.py:101-114` / `Area.py:26` | `checkParam` qui *ha* `self` (binding corretto), ma `__init__` controlla `check_results[1]` invece di `[0]` e referenzia `check_results[2]` inesistente → stesso esito: validazione mai attiva. |
| `DataType/Limes.py:24` | `Limes()` (nessun argomento, uso del default `points=None`) solleva subito `AttributeError: 'NoneType' object has no attribute 'name'` — riprodotto con esecuzione diretta. La classe è **inutilizzabile allo stato attuale**, anche nel caso più semplice. |
| `DataType/Threat.py:36` | `self._obj = obj` — `obj` non è mai un parametro di `__init__` (che ha solo `level, name, id`) → `NameError` **garantito** ad ogni istanziazione, se mai venisse chiamata (righe 26/31 referenziano anche `General`, mai importato, ma sono raggiunte solo se `name`/`id` non forniti). In pratica non emerge perché `Threat` non è mai istanziata nel codice reale, solo importata per type-hint/validazione in `Asset.py`/`Aircraft.py` e usata come `MagicMock(spec=Threat)` nei test. |
| `Asset/Vehicle.py:242`, `Asset/Structure.py:188` | Chiamano `Volume(length=..., width=..., height=...)`, incompatibile con la firma reale `Volume(area_base, volume_shape, radius_at_height=None)` → `TypeError` se il ramo venisse eseguito. Bug del chiamante, non di `DataType/Volume.py`, ma dimostra che l'API di `Volume` non è integrata col resto del codice. |
| `Context/Coalition.py:15` | `from Dynamic_War_Manager.Source.Volume import Volume` — path di import errato (manca `Code.` e il segmento `DataType`), stesso pattern di bug già corretto oggi in `Waypoint.py`/`Edge.py` ma non qui. Fuori scope diretto (`Context/`), segnalato per completezza. |
| `DataType/Event.py` | Metodi `isPush/isPop/isHit/isAssimilate/isMove` leggono `self._type`, mai assegnato in `__init__` (solo `self._event_type` esiste) → `AttributeError` se chiamati. |

**Copertura test:** non esiste un `Test_DataType.py` unico (confermato). Esistono però tre file di test dedicati a singole classi del package, tutti verdi:
- `Test/Test_Cylinder.py` — 15 test, **OK**.
- `Test/Test_Payload.py` — 7 test, **OK**.
- `Test/Test_State.py` — 67 test, **OK**.

Le restanti classi (`Area`, `Classi`, `Edge`, `Event`, `Hemisphere`, `Limes`, `Route`, `Sphere`, `Threat`, `Volume`, `Waypoint`) **non hanno test dedicati** e sono esercitate solo indirettamente (quando lo sono) tramite i test dei moduli consumatori: `Test_Air_Route_Manager.py` e `Test_Ground_Route_Manager.py` in realtà testano le classi *locali* di `Logic/Air_Route_Manager.py`/`Ground_Route_Manager.py`, non quelle di `DataType`; `Test_Vehicle.py`/`Test_Asset.py` istanziano `Volume`/`Threat` solo con mock o con la firma "giusta" isolata, senza esercitare i percorsi realmente rotti descritti sopra. Di fatto, `Edge`, `Waypoint`, `Area`, `Limes`, `Threat`, `Volume` **non hanno oggi alcuna copertura di test reale** dei propri bug.

**Import puliti:** verificato che `Waypoint.py` (riga 1: `from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset`) ed `Edge.py` (riga 2, stesso import) usano ora correttamente il prefisso `Code.Dynamic_War_Manager.Source...`. Nessun residuo del vecchio path errato `from Dynamic_War_Manager.Source...` in questi due file.

## Problemi aperti

1. **`Classi.py` è codice orfano.** Non importato da nessun altro file del progetto (verificato via grep esaustivo). Contiene una reimplementazione giocattolo di `Payload`, `Point`, `Segment`, `Block`, `Asset` e sottoclassi (`Production`, `Urban`, `Storage`, `Transport`, `Military`) che duplicano nomi di classi reali altrove nel codebase con logica minima/assente (molti metodi sono solo `pass`). Da decidere se eliminarlo, o se conteneva idee di design (es. gerarchia `Block`→`Asset`, pattern `add_asset`/`remove_asset` bidirezionale) da recuperare per l'implementazione reale.
2. **`Edge`/`Waypoint`/`Area` sono validati "a vuoto".** Il bug ricorrente `if not check_results[1]:` (invece di `[0]`) rende la validazione dei parametri completamente inerte in tre classi diverse — non è un caso isolato ma un pattern copincollato. Da correggere in tutte e tre le sedi in un'unica passata, insieme al problema di `checkParam` privo di `self` in `Edge`/`Waypoint`.
3. **`Edge.__init__` non è instanziabile nemmeno con argomenti corretti**, per via del refuso `calcLenght`/`calcLength`. Questo significa che **nessun `DataType.Edge` reale esiste mai in memoria** nel codice attuale, nonostante sia il tipo dichiarato per `Route.edges`, `Region._routes[...]`. Va verificato se questo blocca silenziosamente qualche funzionalità a runtime (es. `Region.add_route`, mai chiamato — vedi punto successivo — potrebbe essere proprio per questo).
4. **Duplicazione Waypoint/Edge/Route tra `DataType` e `Logic/Air_Route_Manager.py` + `Logic/Ground_Route_Manager.py`**, senza alcun ponte di conversione. Da chiarire con l'altra indagine (`07_Logic_Routing.md`) se l'intento è unificare su `DataType` (correggendone i bug) o mantenere le versioni locali di `Logic` come implementazione definitiva e deprecare le omonime in `DataType`.
5. **`Threat.py` non è mai stato completato** (`obj` mai dichiarato, `General` mai importato) e oggi sopravvive solo come type-hint mai concretizzato. Va chiarito se il modello di minaccia dovrebbe usare `Cylinder` (già usato realmente da `Mobile.air_defense_volume`/`ThreatAA`) come rappresentazione geometrica, deprecando `Threat`/`Sphere`/`Hemisphere`/`Volume` come classi indipendenti mai collegate.
6. **`Volume.py` ha una firma mai allineata ai chiamanti reali** (`Vehicle.py`, `Structure.py` la chiamano con `length/width/height`, che non esistono nella firma `area_base/volume_shape/radius_at_height`). Va deciso se riscrivere `Volume` per accettare dimensioni lineari dirette, o correggere i chiamanti per costruire prima un `Area`.
7. **`Limes.py` è inutilizzabile allo stato attuale** anche nel caso base (`Limes()` senza argomenti solleva `AttributeError`). Nessun test lo esercita. Va deciso se è ancora nella roadmap (rappresentazione del confine poligonale di una `Region`) o va riscritto da zero.
