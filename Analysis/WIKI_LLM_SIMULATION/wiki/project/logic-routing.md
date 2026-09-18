---
title: "Logic — Pianificazione Rotte"
type: project-module
tags: [package-python, air, ground, routing, dwm, implementation]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py, Code/Dynamic_War_Manager/Source/Logic/Ground_Route_Manager.py]
related_decisions: ["[[datatype-route-edge-waypoint]]"]
related: ["[[logic-decision]]"]
---

## Scopo

Il sottosistema calcola le rotte (aeree e terrestri) usate dal Dynamic War Manager per muovere gli asset nella campagna. Comprende due moduli indipendenti, non collegati tra loro:

- **`Air_Route_Manager.py`**: pianificazione di rotte aeree in ambiente 3D, con evitamento (o attraversamento controllato) di minacce contraeree modellate come volumi cilindrici (`ThreatAA`). Supporta strategie di elusione per cambio di quota (sopra/sotto la minaccia) o deviazione laterale, e attraversamento calcolato della minaccia quando il tempo di esposizione resta sotto una soglia di sicurezza.
- **`Ground_Route_Manager.py`**: pianificazione di rotte terrestri (2D/3D semplificate) tramite un grafo pesato e ricerca del percorso ottimo con Dijkstra, con penalità di pendenza per i percorsi su strada.

I due moduli non condividono classi: ciascuno definisce le proprie `Waypoint`/`Edge` locali, incompatibili tra loro e con la classe `Edge`/`Waypoint`/`Route` "ufficiale" di `DataType/` (v. [[datatype-route-edge-waypoint]] per la decisione che ha reso quest'ultima canonica solo per il lato ground — Air resta deliberatamente sulle sue classi locali).

## File e classi principali

| File | Righe | Contenuto |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py` | 1474 | `ThreatAA`, `Waypoint`, `Edge`, `Route`, `Path`, `PathCollection`, `RoutePlanner` |
| `Code/Dynamic_War_Manager/Source/Logic/Ground_Route_Manager.py` | 135 | `Waypoint`, `Edge`, `NavigationGraph` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Air_Route_Manager.py` | 1802 | `GPT_TestModule` (integrazione reale su `RoutePlanner`), `TestThreatAA`, `TestWaypoint`, `TestEdge`, `TestPath`, `TestPathCollection`, `TestRoutePlanner` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Ground_Route_Manager.py` | 338 | `TestNavigationSystem` |

### `Air_Route_Manager.py`

- **`ThreatAA(danger_level, interception_speed, min_fire_time, min_detection_time, cylinder: Cylinder)`** — minaccia contraerea come cilindro 3D. `edgeIntersect`, `innerPoint`, `calcMaxLenghtCrossSegment` (risolve un'equazione quadratica per stimare la lunghezza massima di segmento attraversabile prima di una possibile intercettazione).
- **`Waypoint(name, point: Point3D, id)`** — punto 3D con proiezione 2D precalcolata; `__eq__`/`__hash__` basati sulle coordinate.
- **`Edge(name, order_position, wpA, wpB, speed)`** — segmento di rotta; `length` calcolata a `__init__`; `danger` valorizzato solo quando l'edge attraversa una minaccia.
- **`Route`** — contenitore ordinato di edge; `getWaypoints()` ricostruisce l'ordine seguendo i collegamenti.
- **`Path`** (dataclass) — percorso candidato durante la ricerca; ricalcola le metriche ad ogni `add_edge`; `to_route()` converte il risultato finale in `Route`.
- **`PathCollection`** — gestisce i percorsi candidati generati durante la ricorsione: `add_path`, `mark_path_completed`, `get_best_path(max_range)` (min per `(total_danger, total_length)`).
- **`RoutePlanner(start, end, threats)`** — motore di calcolo. `calcRoute(...)` è l'entry point pubblico; instrada la ricerca su due algoritmi ricorsivi alternativi (`calcPathWithoutThreat`/`calcPathWithThreat`) a seconda che l'attraversamento controllato sia ammesso. `_handle_threat_crossing`/`_handle_threat_avoidance` gestiscono rispettivamente l'attraversamento e l'elusione (cambio quota o biforcazione laterale del percorso).

  Algoritmo complessivo: ricerca ricorsiva a più rami (non un vero A*/Dijkstra) che esplora alternative locali ogni volta che una minaccia viene incontrata, accumulando percorsi candidati e scegliendo alla fine quello con minor `(danger, length)` tra quelli completati entro il range massimo.

### `Ground_Route_Manager.py`

- **`Waypoint(name, x, y, z, state='inactive')`** — `distance_to(other, type='3D'|'2D')` restituisce `(distance, dz)`.
- **`Edge(start, end, danger_level, path_type, max_speed)`** — `path_type` in `{'onroad','offroad','air','water'}`; per i tipi non aerei applica un vincolo di pendenza massima (10%), allungando artificialmente la distanza se la pendenza reale eccede il limite.
- **`NavigationGraph`** — grafo semplice `{Waypoint: [Edge]}`. `find_optimal_path` è un Dijkstra generico parametrizzato da `weight_func`; sopra di esso: `find_min_danger_path`, `find_fastest_path`, `find_min_danger_fastest_path` (combinazione pesata 0.5/0.5 di default).

Algoritmo: Dijkstra puro su un grafo esplicito costruito a mano — nessun evitamento minacce geometrico come nel modulo aereo, il "pericolo" è solo un peso scalare per arco.

## Dipendenze

- `Air_Route_Manager.py` → `sympy` (`Point3D/2D`, `Segment3D`, `Line3D/2D`, `Circle`), `DataType.Cylinder.Cylinder`, `Utility.Utility`. **Non importa `DataType/Edge.py` né `DataType/Waypoint.py`**: usa le proprie classi.
- `Ground_Route_Manager.py` → solo `heapq` (stdlib). Nessuna dipendenza da `sympy`/`DataType`/`Asset`.
- Nessun modulo di `Source/` (Military, Region, Block, Asset, Context…) importa `Air_Route_Manager` o `Ground_Route_Manager` (verificato con grep) — **i due moduli sono isole, non collegate al resto del motore di campagna**.

## Stato attuale

Verificato eseguendo la suite reale il 2026-09-18 (non solo lettura di codice):

- **`Ground_Route_Manager.py`**: completo per lo scopo limitato che implementa. Test: **8/8 OK** (`TestNavigationSystem`).
- **`Air_Route_Manager.py`**: **48/48 test OK** (`python -m unittest discover ... -p "Test_Air_Route_Manager.py"`, 89s). Questo **supera lo stato riportato dal vecchio audit** (`Analysis/Modules/07_Logic_Routing.md`, 2026-08-16), che documentava 26 errori su 52 test per un disallineamento di firma tra i fixture di `TestThreatAA`/`TestEdge`/`TestPath`/`TestPathCollection`/`TestRoutePlanner` e le classi reali (`Edge` mancava `order_position`, `ThreatAA` mancava `min_detection_time`). Il fix (lato test, non toccando `Air_Route_Manager.py`) è stato applicato in una sessione successiva non ancora tracciata da una memoria dedicata di questo refactoring — oggi tutte e sette le classi di test passano, incluse quelle che l'audit descriveva come "completamente rotte".
  - Copertura: `GPT_TestModule` esercita `RoutePlanner.calcRoute` end-to-end su scenari con 0–16 minacce (elusione alto/basso/laterale, attraversamento); `TestThreatAA`/`TestWaypoint`/`TestEdge`/`TestPath`/`TestPathCollection`/`TestRoutePlanner` coprono le classi/metodi di supporto isolatamente.
- **Route/Edge/Waypoint duplicati, per decisione esplicita** (v. [[datatype-route-edge-waypoint]]): lato Air restano le classi locali di `Air_Route_Manager.py` (funzionano, sono testate); lato Ground `DataType.Route`/`Edge`/`Waypoint` sono stati resi canonici e riparati (bug di costruzione risolti — `Edge.calcLenght`→`calcLength`, `checkParam` non-static, indicizzazione errata dei risultati di validazione), e sono oggi usati realmente da `Region.add_route`/`get_shortest_route` e da `Military.time_to_ground_intercept`/`time2attack`. **`Ground_Route_Manager.py` stesso non è però stato aggiornato**: le sue classi locali (`Waypoint`/`Edge`/`NavigationGraph`) restano quelle originarie, distinte da `DataType.Route`/`Edge`, e il modulo non produce ancora oggetti `DataType.Route` — quindi nulla in `Ground_Route_Manager.py` alimenta oggi `Region.add_route`. Questa parte della decisione (Fase 3, "costruzione del layer mancante") **non è stata iniziata**: verificato di persona il 2026-09-18, nessun riferimento a `DataType` nei due file del modulo (`grep` negativo).

## Problemi aperti

- **Moduli isolati**: né `Air_Route_Manager.py` né `Ground_Route_Manager.py` sono importati da alcun altro modulo di `Source/`. Il calcolo delle rotte esiste ma non è agganciato al resto del motore di campagna dinamica.
- **`Ground_Route_Manager.py` non produce `DataType.Route`**: come sopra, resta il gap più concreto per collegare questo modulo al resto del sistema (`Region.add_route` esiste e funziona, ma nessun produttore reale lo alimenta lato ground).
- **Tre classi `Edge` e tre classi `Waypoint` distinte nel progetto**: `DataType/Edge.py`+`DataType/Waypoint.py` (ora funzionanti e canoniche per il ground "logico"), `Logic/Air_Route_Manager.py` (locali, canoniche per l'air), `Logic/Ground_Route_Manager.py` (locali, ancora in uso, mai migrate). Nessuna condivide un'interfaccia comune.
- **`Ground_Route_Manager.Edge.__repr__`** referenzia `self.slope`, attributo mai impostato → `AttributeError` se mai invocato `repr()`/`print()` su un'istanza (non coperto da test).
- **Costanti morte** in `Air_Route_Manager.py`: `MAX_EDGES` e `MIN_SECURE_LENGTH_EDGE`, definite ma mai referenziate nel corpo del file.
- **Complessità di `RoutePlanner`**: `_handle_threat_crossing`/`_handle_threat_avoidance` sono fortemente ricorsive, con parametri lunghissimi duplicati identici in quasi ogni chiamata — candidato naturale per un oggetto di contesto/dataclass (`SearchContext`).

## Decisioni architetturali rilevanti

- [[datatype-route-edge-waypoint]] — decisione che ha reso `DataType.Route`/`Edge`/`Waypoint` canonici per il lato ground (riparandone i bug di costruzione) mantenendo invariate le classi locali di `Air_Route_Manager.py`; la "Fase 3" di quella decisione (far produrre `DataType.Route` a `Ground_Route_Manager.py`) resta non iniziata, come documentato sopra.
