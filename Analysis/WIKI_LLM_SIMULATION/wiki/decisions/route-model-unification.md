---
title: "Modello di rotta unico: DataType.Route confermato, frontiera di conversione"
type: decision
tags: [architecture, dwm, routing, datatype, air, ground]
created: 2026-09-22
updated: 2026-09-22
status: accepted
supersedes: ["[[datatype-route-edge-waypoint]]"]
affects: ["[[logic-routing]]", "[[virtual-session-engine-des]]"]
related: []
---

## Contesto

Una delle 3 questioni aperte prima della Fase 3 del motore DES per le sessioni virtuali (v.
[[virtual-session-engine-des]]): il futuro `Contact_Scheduler` deve calcolare CPA/TCPA e
intersezioni rotta↔volume su **un solo** modello di rotta, ma il progetto ne aveva 3
indipendenti e incompatibili — `DataType.Route`/`Edge`/`Waypoint` (canonico per il ground dalla
decisione di agosto, v. [[datatype-route-edge-waypoint]]), e le classi locali di
`Logic/Air_Route_Manager.py` e `Logic/Ground_Route_Manager.py`, mai unificate con esso.

**Fatto decisivo trovato verificando il codice**: nessun consumatore di produzione chiama
`RoutePlanner.calcRoute` o `NavigationGraph.find_optimal_path` — solo i test e
`Utility/visualizer.py`. `Region`/`Military`/`Tactical_Evaluation`/`Command_Types` consumano
**solo** il tipo canonico. La migrazione non rompe quindi alcun contratto di produzione.

## Decisione

1. **`DataType.Route`/`Edge`/`Waypoint` resta l'unico modello di rotta del dominio** —
   conferma della decisione di agosto 2026, estesa esplicitamente anche al lato aereo: era già
   pensato per l'aria (`path_type == 'air'`, `Point3D`/`Line3D`) ed è l'unico a portare
   `positionAtTime`/`travelTimeToEdge`, esattamente ciò che serve al `Contact_Scheduler`.
2. **I modelli interni di `Air_`/`Ground_Route_Manager` restano**, ma come stato di lavoro
   privato dell'algoritmo di ricerca (code di priorità, ricorsione, metriche di ramo) — non
   escono mai dal proprio modulo. Non è duplicazione da eliminare ad ogni costo: riscrivere la
   ricorsione per lavorare direttamente su `DataType.Edge` (due oggetti sympy `Line` per arco)
   sarebbe più lento e più rischioso.
3. **La conversione avviene in un solo punto**: l'uscita pubblica del path-finding. Un solo
   verso, interno → canonico, mai un adattatore bidirezionale.
4. **`Air_Route_Manager.Route` è duplicazione pura e va eliminata** (Fase 4 del piano): costruita
   solo da `Path.to_route()`, non porta nulla che `Path` non abbia già. Stesso discorso per
   `Ground_Route_Manager.Waypoint`/`Edge` (sono un grafo, non una rotta).

## Motivazione

`Region` (storage/query) e `Tactical_Evaluation` (consumo) sono già costruiti attorno a
`DataType.Route` nell'intento originale del progetto — mancava solo un produttore reale lato
Air/Ground. Estendere il tipo canonico anche all'aria, invece di introdurre un quarto modello o
lasciare la triplicazione, è la scelta meno rischiosa proprio perché nessun consumatore di
produzione dipende oggi dai tipi locali.

## Conseguenze

**Piano a 5 fasi** (dettaglio completo in [[project_route_model_unification_plan]]):

1. **Frontiera di conversione — FATTA 2026-09-22** (commit `6c421579`): nuovo
   `Logic/Route_Adapter.py` (`to_canonical_route`, `ground_path_to_route`,
   `route_type_from_path_types`); `RoutePlanner.calcCanonicalRoute` e
   `NavigationGraph.find_canonical_route` come nuove uscite pubbliche; `DataType/Edge.py` reso
   robusto ai segmenti degeneri (una salita verticale pura, stessa x/y, rendeva l'arco non
   costruibile con sympy — **era il vero blocco tecnico** della migrazione, non la scelta
   architetturale) e fix del logger mancante `.logger`. 26 nuovi test
   (`Test_Route_Adapter.py`), verifica end-to-end con un `RoutePlanner` e una `ThreatAA` reali.
2. Migrare `Utility/visualizer.py` a `calcCanonicalRoute` — non ancora fatto.
3. Collegare `Military.air_defense_threats()` alla pianificazione reale; costruire un produttore
   per `NavigationGraph` (**non esiste ancora — il grafo di navigazione terrestre non è
   costruito da nessuna parte**, è il lavoro mancante più concreto lato ground) — non ancora
   fatto.
4. Rendere private le classi interne (`Waypoint`→`_SearchWaypoint` ecc.), eliminare `Route`
   interna e `Path.to_route()` — rompe `Test_Air_Route_Manager.py` (`import *`), va fatto in un
   commit unico — non ancora fatto. `ThreatAA`/`build_threat_aa` non toccati da questo piano.
5. `Contact_Scheduler` (Fase 3 del motore) consumerà solo `DataType.Route` — test di
   non-regressione della decisione.

**Non deciso qui**: il sistema di riferimento (piano locale vs. coordinate geodetiche, v.
[[core-simulator-agnostic]] §8).

**`Edge.calcLength()` — chiuso 2026-09-22** (v. [[virtual-session-engine-des]]): il commento
("2D per onroad/offroad/water, 3D per air") era il bug, non il codice — corretto il commento.
`calcLength()` ha sempre calcolato la distanza 3D per ogni `path_type`; le posizioni asset
portano già una quota reale anche a terra, quindi è la scelta fisicamente corretta. Il codice
(e i numeri già in uso) non sono stati toccati.

**`Edge.intersectPoint(Line2D)` — bug trovato e corretto nello stesso giro** (non parte del
piano sopra, emerso rileggendo il fix): usava `self._line` (3D) invece di `self._line2d`,
producendo un'intersezione vuota silenziosa per ogni edge non a quota zero. V. commit
`5a87ebb2`, nuovo `Test_Edge.py` (prima nessuna copertura per questo metodo).

## Fonti

- [[project_route_model_unification_plan]] (memoria di origine, piano a 5 fasi completo)
- [[project_virtual_session_engine_design]] (contesto §9, le 3 questioni)
- `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §9 (aggiornato in
  place con i marcatori di stato)
