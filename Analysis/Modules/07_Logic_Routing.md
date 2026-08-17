# Logic — Pianificazione Rotte

## Scopo

Il sottosistema calcola le rotte (aeree e terrestri) usate dal Dynamic War Manager per muovere gli asset nella campagna. Comprende due moduli indipendenti, non collegati tra loro e non integrati nel resto del progetto:

- **`Air_Route_Manager.py`**: pianificazione di rotte aeree in ambiente 3D, con evitamento (o attraversamento controllato) di minacce contraeree modellate come volumi cilindrici (`ThreatAA`). Supporta strategie di elusione per cambio di quota (sopra/sotto la minaccia) o deviazione laterale, e attraversamento calcolato della minaccia quando il tempo di esposizione resta sotto una soglia di sicurezza.
- **`Ground_Route_Manager.py`**: pianificazione di rotte terrestri (o comunque 2D/3D semplificate) tramite un grafo pesato e ricerca del percorso ottimo con Dijkstra, con penalità di pendenza per i percorsi su strada.

I due moduli non condividono classi: ciascuno definisce le proprie `Waypoint`/`Edge` locali, incompatibili tra loro e con la classe `Edge` "ufficiale" di `DataType/Edge.py`.

## File inclusi

| File | Righe | Contenuto |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py` | 1–1475 | `ThreatAA`, `Waypoint`, `Edge`, `Route`, `Path`, `PathCollection`, `RoutePlanner` |
| `Code/Dynamic_War_Manager/Source/Logic/Ground_Route_Manager.py` | 1–135 | `Waypoint`, `Edge`, `NavigationGraph` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Air_Route_Manager.py` | 1–1848 | `GPT_TestModule` (22 test, integrazione reale su `RoutePlanner`), `TestThreatAA`, `TestWaypoint`, `TestEdge`, `TestPath`, `TestPathCollection`, `TestRoutePlanner` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Ground_Route_Manager.py` | 1–338 | `TestNavigationSystem` (8 test) |

File di contesto consultati (non leggibili in questo ambiente — mancano `poppler-utils`/`pypdf`/`pymupdf`, quindi nessun renderer PDF disponibile; l'analisi sotto si basa esclusivamente sul codice sorgente):
- `Analysis/Document/Route-2024-12-03-17-34.pdf`
- `Analysis/Document/front movement-2025-03-16-17-04.pdf`
- Notare inoltre in `Analysis/Document/` una serie di file GeoGebra (`Test_Air_Route_Manager. calc_route_with_{4,5,6,9,13}_threat.ggb`) usati evidentemente per validare a mano gli scenari di test con più minacce.

## Classi e funzioni principali

### `Air_Route_Manager.py`

- **`ThreatAA(danger_level, interception_speed: float, min_fire_time: float, min_detection_time: float, cylinder: Cylinder)`** — righe 32–116. Rappresenta una minaccia contraerea come cilindro 3D (`cylinder.bottom_center.z` → `min_altitude`, `+ height` → `max_altitude`).
  - `edgeIntersect(edge) -> (bool, Optional[Segment3D])` (43–58): delega a `Cylinder.getIntersection`.
  - `innerPoint(point: Point3D) -> bool` (60–64).
  - `calcMaxLenghtCrossSegment(aircraft_speed, aircraft_altitude, time_to_inversion) -> float` (66–94): risolve un'equazione quadratica per stimare la lunghezza massima di segmento attraversabile nella zona di minaccia prima di una possibile intercettazione (basata su velocità di intercettazione, tempo di inversione e tempo minimo di fuoco).

- **`Waypoint(name: str, point: Point3D, id: str|None)`** — righe 119–165. Punto 3D con proiezione 2D precalcolata; `__eq__`/`__hash__` basati sulle coordinate (due waypoint con stesse coordinate sono considerati uguali, indipendentemente dal nome).

- **`Edge(name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float)`** — righe 169–216. Segmento di rotta; `length` calcolata a `__init__` come `wpA.point.distance(wpB.point)`; `danger` inizializzato a 0 e valorizzato solo quando l'edge attraversa una minaccia (vedi `_handle_threat_crossing`). Metodo `getSegment3D()` (181–183).

- **`Route(name, length, danger)`** — righe 218–286. Contenitore ordinato di edge (dict `{(wpA,wpB): edge}`); `getWaypoints()` ricostruisce l'ordine seguendo i collegamenti a partire dal punto senza archi entranti.

- **`Path`** (dataclass) — righe 290–353. Percorso candidato durante la ricerca; ricalcola `total_length`/`total_danger`/`waypoints` ad ogni `add_edge` (`__post_init__` + `_calculate_metrics`). `to_route()` converte il risultato finale in `Route`.

- **`PathCollection`** — righe 357–434. Gestisce i percorsi candidati generati durante la ricorsione: `add_path`, `mark_path_completed`, `get_active_paths`, `get_best_path(max_range)` (min per `(total_danger, total_length)` tra i percorsi completati entro il range massimo).

- **`RoutePlanner(start, end, threats)`** — righe 437–1474. Motore di calcolo.
  - `calcRoute(...)` (447–558): entry point pubblico. Esclude le minacce che contengono i punti di partenza/arrivo (`excludeThreat`) e, se richiesto, quelle la cui quota massima è inferiore alla quota di rotta dell'aereo. Instrada poi la ricerca su due algoritmi ricorsivi alternativi a seconda del flag `intersecate_threat`.
  - `calcPathWithoutThreat(...)` (665–749): ricorsione che **non** consente mai l'attraversamento di una minaccia — se un edge la interseca, delega a `_handle_threat_avoidance` (cambio quota o deviazione laterale).
  - `calcPathWithThreat(...)` (751–877): ricorsione che valuta anche l'attraversamento controllato (delega a `_handle_threat_crossing` quando l'intersezione è "completa", cioè attraversa il cilindro da parte a parte).
  - `_handle_threat_crossing(...)` (879–1120): calcola il segmento di attraversamento (accorciandolo con `Cylinder.find_chord_coordinates` se supera `calcMaxLenghtCrossSegment`), verifica che il punto di uscita non ricada in un'altra minaccia (altrimenti tenta una deviazione laterale ±90°), quindi prosegue la ricorsione dal punto di uscita rimuovendo la minaccia attraversata dalla lista.
  - `_handle_threat_avoidance(...)` (1122–1463): se `change_alt_option` lo consente e i margini di quota (`MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN/MAX_VALUE`) lo permettono, sposta il percorso sopra/sotto la minaccia; altrimenti calcola punti esterni alla circonferenza estesa della minaccia (`RADIUS_EXTENSION_THREAT_CIRCONFERENCE`, `Cylinder.getExtendedPoints`) e biforca la ricerca in due path paralleli (uno per ciascun punto esterno), scartando il ramo la cui deviazione è più del doppio dell'altra.
  - Costanti di tuning a livello di modulo (righe 20–29): `MAX_PATHS=50`, `MAX_COMPLETED=10`, `MAX_RECURSION=10`, `MAX_EDGES=30` (**mai referenziata nel corpo del file**, costante morta), `MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX/MIN_VALUE`, `RADIUS_EXTENSION_THREAT_CIRCONFERENCE`, `MIN_SECURE_LENGTH_EDGE` (**anch'essa mai referenziata**), `MIN_DISTANCE_TO_CHANGE_ALTITUDE`, `TOLERANCE_FOR_INTERSECTION_CALCULUS`.

  Algoritmo complessivo: ricerca ricorsiva a più rami (non un vero A*/Dijkstra) che esplora alternative locali ogni volta che una minaccia viene incontrata, accumulando percorsi candidati in `PathCollection` e scegliendo alla fine quello con minor `(danger, length)` tra quelli completati e sotto il range massimo.

### `Ground_Route_Manager.py`

- **`Waypoint(name, x, y, z, state='inactive')`** — righe 10–31. `distance_to(other, type='3D'|'2D')` restituisce `(distance, dz)`.
- **`Edge(start, end, danger_level, path_type, max_speed)`** — righe 33–69. `path_type` in `{'onroad','offroad','air','water'}`; per i tipi non aerei applica un vincolo di pendenza massima (`max_slope = 10%`) allungando artificialmente la distanza se la pendenza reale eccede il limite (righe 50–64).
- **`NavigationGraph`** — righe 71–136. Grafo semplice `{Waypoint: [Edge]}`. `find_optimal_path` è un **Dijkstra generico** parametrizzato da `weight_func`; sopra di esso sono costruite tre varianti: `find_min_danger_path` (peso = `danger_level`), `find_fastest_path` (peso = `distance/max_speed`), `find_min_danger_fastest_path` (combinazione pesata `perc_danger`/`perc_time`, default 0.5/0.5).

Algoritmo: Dijkstra puro su un grafo esplicito costruito a mano (nessun evitamento minacce geometrico come nel modulo aereo — qui il "pericolo" è solo un peso scalare per arco).

## Dipendenze

- `Air_Route_Manager.py` → `sympy` (`Point3D/2D`, `Segment3D`, `Line3D/2D`, `Circle`), `Code...DataType.Cylinder.Cylinder`, `Code...Utility.Utility` (`rotate_vector`, `get_direction_vector`, `getFormattedPoint`). **Non importa `DataType/Edge.py` né `DataType/Waypoint.py`**: definisce le proprie classi `Edge`/`Waypoint` interne.
- `Ground_Route_Manager.py` → solo `heapq` (stdlib). Nessuna dipendenza da `sympy`, `DataType` o `Asset`.
- Nessun modulo di `Source/` (Military, Region, Block, Asset, Context…) importa `Air_Route_Manager` o `Ground_Route_Manager` (verificato con grep incrociato) — **i due moduli sono al momento isole, non collegate al resto del motore di campagna**. Restano tracce di cache compilate di versioni precedenti/parallele mai committate come sorgente: `Code/Dynamic_War_Manager/__pycache__/Air_Route_Manager_Solid.cpython-312.pyc` e `Air_Route_Manager_Solid_Manus.cpython-312.pyc`, segno di tentativi di refactoring (probabilmente con GitHub Copilot/altro agente, dato il suffisso "Manus") mai finalizzati nel sorgente attuale.

## Stato attuale

- **`Ground_Route_Manager.py`**: completo per lo scopo limitato che implementa (Dijkstra su grafo esplicito). Test: `Test_Ground_Route_Manager.py`, **8/8 test OK** (`TestNavigationSystem`).
- **`Air_Route_Manager.py`**: algoritmo di pianificazione con evitamento/attraversamento minacce **funzionante e testato in modo sostanziale** tramite la classe `GPT_TestModule` (22 test, tutti passano), che esercita `RoutePlanner.calcRoute` end-to-end su scenari con 0, 1, 2, 3, 4, 5, 6, 9 e 16 minacce, incluse varianti di elusione (alto/basso/laterale) e attraversamento. Anche `TestWaypoint` (4 test) passa.
- Il resto del file di test (`TestThreatAA`, `TestEdge`, `TestPath`, `TestPathCollection`, `TestRoutePlanner` — introdotto presumibilmente in una fase precedente del refactoring, prima che venissero aggiunti il parametro `order_position` a `Edge` e `min_detection_time` a `ThreatAA`) **è completamente rotto**: 26 errori su 52 test totali eseguiti (comando: `python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Air_Route_Manager.py"`, verificato in questo ambiente).
  - Risultato osservato: `Ran 52 tests ... FAILED (errors=26)`.
- Copertura test reale sull'algoritmo core (`RoutePlanner`, `PathCollection`, `Path`): **presente solo tramite `GPT_TestModule`** (test di integrazione black-box su `calcRoute`); i test unitari dedicati a `RoutePlanner` (metodi `excludeThreat`, `firstThreatIntersected`, `calcPathWithoutThreat`, `calcPathWithThreat`, `_handle_threat_crossing`, `_handle_threat_avoidance`, in `TestRoutePlanner`) non sono eseguibili nello stato attuale (falliscono tutti in `setUp`).

## Bug: Edge.__init__ signature mismatch

### Esito dell'investigazione

1. **`Edge` istanziata dal test non è quella di `DataType/Edge.py`.** `Test_Air_Route_Manager.py` importa con `from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import *` (riga 12 del test). `Air_Route_Manager.py` definisce una **propria classe `Edge`** (righe 169–216), che con lo `import *` sovrascrive/precede qualunque riferimento a `DataType.Edge.Edge`, mai importata nel file di test. La firma realmente in uso è quindi:
   ```python
   Edge(self, name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float)   # Air_Route_Manager.py:172
   ```
   e non quella di `DataType/Edge.py` (`Edge(self, wpA, wpB, path_type, danger_level, speed, name)`, righe 15–21) — le due classi non sono correlate e hanno perfino l'ordine dei parametri diverso.

2. **Il codice di produzione in `Air_Route_Manager.py` usa sempre la firma corretta a 5 argomenti** (`name, order_position, wpA, wpB, speed`). Tutte le istanze di `Edge(...)` nel file (righe 711, 798, 978, 987, 1015, 1030, 1260, 1268) passano correttamente `order_position` come secondo argomento. **Non c'è quindi nessun bug live nel codice di produzione**: la funzione `calcRoute` è verificata funzionante dai 22 test di `GPT_TestModule`, che coprono scenari con più minacce e passano tutti.

3. **La causa è un disallineamento del fixture di test**, isolato alle classi `TestEdge`, `TestPath`, `TestPathCollection` (e per estensione `TestRoutePlanner`, che condivide lo stesso pattern con `ThreatAA`). Il test istanzia:
   ```python
   self.edge = Edge("Test Edge", self.wp_a, self.wp_b, 100)   # Test_Air_Route_Manager.py:1163
   ```
   cioè 4 argomenti posizionali, mentre la classe reale richiede 5 (`name, order_position, wpA, wpB, speed`) → manca `order_position`, da cui `TypeError: Edge.__init__() missing 1 required positional argument: 'speed'` (l'errore riporta `speed` come mancante perché con lo shift di un parametro `100` viene assegnato a `wpB` e l'ultimo parametro, appunto `speed`, resta scoperto).
   Occorrenze identiche: righe 1163, 1215, 1270 (11 test totali: `TestEdge` × 4, `TestPath` × 3, `TestPathCollection` × 4).

   Un secondo difetto della stessa natura, distinto ma strutturalmente identico, riguarda `ThreatAA`: la classe reale richiede 5 argomenti (`danger_level, interception_speed, min_fire_time, min_detection_time, cylinder` — riga 34), ma i test in `TestThreatAA` (riga 1080) e `TestRoutePlanner` (riga 1349) la istanziano con soli 4 argomenti (`ThreatAA(5, 500, 2, cylinder)`), mancando `min_detection_time` → `TypeError: ThreatAA.__init__() missing 1 required positional argument: 'cylinder'`. Questo spiega altri 15 dei 26 errori osservati (11 in `TestRoutePlanner`, 4 in `TestThreatAA`).
   Da notare che, anche correggendo questi due argomenti mancanti, altri test in questo stesso blocco fallirebbero comunque per ulteriore drift della firma verso l'implementazione reale:
   - `TestThreatAA.test_innerPoint` chiama `self.threat.innerPoint(inside_point, 0.1)` (2 argomenti), ma `ThreatAA.innerPoint(self, point)` (riga 60) ne accetta uno solo.
   - `TestThreatAA.test_calcMaxLenghtCrossSegment` chiama `calcMaxLenghtCrossSegment(200, 100, 5, segment)` (4 argomenti), ma il metodo reale (riga 66) ne accetta 3 (`aircraft_speed, aircraft_altitude, time_to_inversion`).
   - `TestEdge.test_calculate_danger`/`test_intersects_threat` chiamano metodi `calculate_danger`/`intersects_threat` che **non esistono affatto** sulla classe `Edge` reale (che espone solo `getSegment3D`, `to_dict`, e le proprietà impostate in `__init__`).

   Conclusione: il blocco di test `TestThreatAA` / `TestEdge` / `TestPath` / `TestPathCollection` / `TestRoutePlanner` non è un semplice fixture con un argomento dimenticato, ma una **suite di test scritta contro una versione precedente (o mai esistita/pianificata) dell'API**, non aggiornata quando l'API attuale ha aggiunto `order_position` a `Edge`, `min_detection_time` a `ThreatAA`, e ha consolidato `ThreatAA.innerPoint`/`calcMaxLenghtCrossSegment` alle firme attuali. La suite `GPT_TestModule`, molto più recente (nota nel file come test scritti/rivisti con ChatGPT), usa correttamente le firme attuali ovunque (es. riga 59: `Edge("edge1", 0, wpA, wpB, speed=250)`).

### Proposta di fix (non applicata)

Non modificare `Edge`/`ThreatAA` in `Air_Route_Manager.py` (sono corrette e usate coerentemente in produzione e nei 26 test funzionanti di `GPT_TestModule`). Il fix va fatto lato test:
- Aggiungere l'argomento mancante `order_position` a ogni chiamata `Edge(name, wp_a, wp_b, speed)` in `TestEdge.setUp` (riga 1163), `TestPath.setUp` (riga 1215), `TestPathCollection.setUp` (riga 1270) → es. `Edge("Test Edge", 0, self.wp_a, self.wp_b, 100)`.
- Aggiungere l'argomento mancante `min_detection_time` a ogni chiamata `ThreatAA(danger_level, interception_speed, min_fire_time, cylinder)` in `TestThreatAA.setUp` (riga 1080) e `TestRoutePlanner.setUp` (riga 1349).
- Successivamente correggere le chiamate a `innerPoint`/`calcMaxLenghtCrossSegment` con firme errate e **rimuovere o riscrivere** `test_calculate_danger`/`test_intersects_threat` in `TestEdge`, poiché testano metodi (`calculate_danger`, `intersects_threat`) inesistenti sulla classe reale — non è chiaro se debbano essere reintrodotti come funzionalità mancante o semplicemente eliminati come residuo di una API mai realizzata.
- In alternativa più radicale: dato che `GPT_TestModule` copre già `RoutePlanner.calcRoute` end-to-end con 22 scenari, si potrebbe valutare di eliminare l'intero blocco `TestThreatAA`/`TestEdge`/`TestPath`/`TestPathCollection`/`TestRoutePlanner` e riscriverlo da zero contro l'API attuale, invece di rincorrere un disallineamento su più livelli.

## Problemi aperti

- **Moduli isolati**: né `Air_Route_Manager.py` né `Ground_Route_Manager.py` sono importati da alcun altro modulo di `Source/` (Military, Region, Block, Route/Asset...). Il calcolo delle rotte esiste ma non è ancora agganciato al resto del motore di campagna dinamica.
- **26/52 test falliti in `Test_Air_Route_Manager.py`** per drift di firma tra fixture di test e classi reali (`Edge`, `ThreatAA`), come descritto sopra; il fix è puramente lato test, nessuna azione richiesta sul codice di produzione.
- **`DataType/Edge.py` (la classe "ufficiale" del sottosistema DataType, distinta da quella locale di `Air_Route_Manager.py`) è rotta e non istanziabile in nessun caso**: `__init__` (riga 32) chiama `self.calcLenght(self)` — metodo inesistente (il metodo reale si chiama `calcLength`, riga 154, senza la "h" invertita, e non accetta comunque l'argomento extra `self` passato) — e alla riga 33 chiama `self.calcTravelTime(self)` passando anch'esso un argomento `self` in più rispetto alla firma reale (`def calcTravelTime(self):`, riga 158, zero parametri). Verificato: `hasattr(Edge, 'calcLenght')` → `False`, `hasattr(Edge, 'calcLength')` → `True`. Qualunque tentativo di istanziare `DataType.Edge.Edge` solleva `AttributeError` immediatamente. Segnalare al proprietario del sottosistema DataType (`Analysis/Modules/10_DataType.md`, se/quando prodotto), ma vale la pena annotarlo qui perché era l'ipotesi iniziale d'indagine su questo bug e va invece esclusa come causa dei fallimenti di `Test_Air_Route_Manager.py`.
- **Tre classi `Edge` e tre classi `Waypoint` distinte e incompatibili nel progetto**: `DataType/Edge.py` + `DataType/Waypoint.py` (firma `Waypoint(point, name, obj_reference)`), `Logic/Air_Route_Manager.py` (locali, firma `Waypoint(name, point, id)` / `Edge(name, order_position, wpA, wpB, speed)`), `Logic/Ground_Route_Manager.py` (locali, con `x,y,z` invece di `Point3D`, `Edge(start, end, danger_level, path_type, max_speed)`). Nessuna condivide un'interfaccia comune: un consolidamento (o quantomeno un'interfaccia comune/adapter) sarebbe da valutare prima di collegare questi moduli al resto del sistema.
- **`Ground_Route_Manager.Edge.__repr__`** (riga 69) referenzia `self.slope`, attributo mai impostato nella classe → `AttributeError` se mai invocato `repr()`/`print()` su un'istanza (non coperto da alcun test, dato che nessun test chiama `repr(edge)`).
- **Costanti morte** in `Air_Route_Manager.py`: `MAX_EDGES` (riga 23) e `MIN_SECURE_LENGTH_EDGE` (riga 27) sono definite ma mai referenziate nel corpo del file — probabile refactoring incompleto o funzionalità di limitazione del numero di edge/lunghezza minima mai implementata.
- **Cache compilate orfane** (`Air_Route_Manager_Solid.cpython-312.pyc`, `Air_Route_Manager_Solid_Manus.cpython-312.pyc` in `Code/Dynamic_War_Manager/__pycache__/`) indicano l'esistenza pregressa di varianti del modulo non presenti nei sorgenti attuali — da verificare con la cronologia git se contengono logica utile non ancora migrata, o se sono solo residui da eliminare.
- **Complessità e leggibilità di `RoutePlanner`**: la logica di `_handle_threat_crossing`/`_handle_threat_avoidance` è fortemente ricorsiva, con parametri lunghissimi (14+ argomenti posizionali) duplicati identici in quasi ogni chiamata ricorsiva — un candidato naturale per essere raggruppato in un oggetto di contesto/dataclass (`AircraftProfile`/`SearchContext`) per ridurre il rischio di errori di trascrizione tra le tante chiamate ricorsive e migliorare la manutenibilità.
- **Documenti di contesto non consultabili**: i PDF `Route-2024-12-03-17-34.pdf` e `front movement-2025-03-16-17-04.pdf` non sono stati letti in questo ambiente per mancanza di strumenti di rendering PDF (`poppler-utils`/`pypdf`/`pymupdf` non installati nel venv). Se contengono decisioni di design rilevanti (es. la scelta di ricorsione vs. A*, o i criteri di "front movement" per le rotte terrestri), andrebbero recuperate in una sessione con questi strumenti disponibili.
