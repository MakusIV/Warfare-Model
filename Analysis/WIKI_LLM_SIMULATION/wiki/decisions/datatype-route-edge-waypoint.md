---
title: "Route/Edge/Waypoint: DataType canonico per il lato terrestre"
type: decision
tags: [architecture, dwm, datatype, routing, ground, military]
created: 2026-09-18
updated: 2026-09-18
status: accepted
affects: ["[[datatype]]", "[[logic-routing]]"]
related: []
---

## Nota sul nome "Fase 2"

La memoria di origine di questa pagina (`project_fase2_design_decisions.md`) usa "Fase 2" per indicare **le 9 decisioni di design aperte elencate in `Analysis/Modules/00_Sintesi.md`** (2026-08-21) — un ambito completamente diverso dalla "Fase 2" del [[combat-power-priority-redesign]] (stima fog-of-war del combat power, 2026-09-15/16). La memoria stessa segnala questa collisione di nome come fonte di confusione. Questa pagina la risolve nel wiki: qui "Fase 2" si riferisce **esclusivamente** alle 9 decisioni di design post-audit-moduli; per l'altra, vedi [[combat-power-priority-redesign]].

## Contesto

L'audit dei moduli del 2026-08-16 ([[module-audit-2026-08-16]]) aveva rilevato che il progetto aveva **due implementazioni incompatibili** del concetto di rotta: `Air_Route_Manager.py` con proprie classi locali `Route`/`Edge`/`Waypoint` (funzionanti, 22/22 test), e `DataType.Route`/`Edge`/`Waypoint` (mai istanziabili, `Edge.__init__` chiamava un metodo con nome sbagliato). `Region.py` esponeva già un'API di storage/query (`add_route`/`get_route`/`get_shortest_route`/...) costruita attorno a `DataType.Route`, e `Tactical_Evaluation.evaluateGroundRouteDangerLevel` la referenziava — ma nessuno dei due poteva effettivamente funzionare, perché `DataType.Edge` non era costruibile. Serviva una decisione su quale rappresentazione fosse quella canonica per il lato terrestre, dato che il lato aereo era già stato deciso a parte (restare su `Air_Route_Manager`, che funziona).

## Decisione

**`DataType.Route`/`Edge`/`Waypoint` sono il modello canonico per il lato terrestre** (il lato aereo resta su `Air_Route_Manager`, non toccato — le due rappresentazioni non vengono unificate, restano deliberatamente separate). Decisione confermata dall'utente il 2026-08-21 (commit `60335b5e`) dopo una verifica che ha corretto la ricostruzione iniziale del problema: `DataType.Edge`/`Waypoint` non erano import morti in `Tactical_Evaluation.py` come inizialmente sembrava da un grep letterale — erano referenziati indirettamente attraverso `Route`/`v_edge`, semplicemente mai eseguiti con successo per via dei bug di costruzione.

Delle 9 decisioni elencate in `00_Sintesi.md`, questa (Decisione 3) è stata l'unica a richiedere, oltre alla scelta stessa, un vero e proprio giro di riparazioni meccaniche per renderla vera nei fatti — circa 10 bug corretti in `Waypoint`/`Edge`/`Route`/`Military`/`Tactical_Evaluation`, tutti verificati costruendo oggetti reali (non ragionati in astratto):

- **`DataType/Waypoint.py`**: `point2d` leggeva `self._point.x` due volte invece di x/y; `checkParam` non era `@staticmethod` (chiamato come metodo d'istanza, `self` si legava silenziosamente al primo parametro, sfalsando tutti gli argomenti di una posizione); `__init__` leggeva gli indici sbagliati del risultato di `checkParam`; il setter di `point` chiamava `checkParam` con un parametro inesistente. Questi bug si annullavano parzialmente a vicenda, facendo sembrare che `Waypoint` si costruisse correttamente quando in realtà la validazione interna falliva sempre senza mai sollevare l'eccezione.
- **`DataType/Edge.py`**: stessi bug di `checkParam`/indicizzazione di `Waypoint`; `Line3D` riceveva oggetti `Waypoint` dove sympy si aspettava `Point3D` (corretto in `.point`); aggiunto un parametro opzionale `speed` a `calcTravelTime`.
- **`DataType/Route.py`**: `travelTime()` ha ricevuto un parametro opzionale `speed` (propagato a ogni `Edge.calcTravelTime`), che ha evitato di dover inventare una semantica di copia (`Route.copy()`/un `Route.speed` settabile, nessuno dei due esisteva) per `Military.time_to_ground_intercept`.
- **`Block/Military.py`**: `time_to_ground_intercept` aggiornato per usare `route.travelTime(speed=speed)`; `time2attack` corretto (default `Optional[X] = None` mancanti su `route`/`speed`/`target`, guard `if not target and not route` invece di `if not(target and route)` che richiedeva erroneamente entrambi presenti, controlli `is_Air_Base`/`is_Ground_Base` senza parentesi — sempre truthy come riferimento a bound method — e aggiunta `is_Naval_Base()` mancante nel ramo "surface", che escludeva silenziosamente i blocchi navali).
- **`Logic/Tactical_Evaluation.py`**: corretto solo il bug puntuale `for k, v_edge in Route.edges:` (iterava il descrittore di classe, non l'istanza) → `route.edges.items()`. **Deliberatamente non completata oltre questo**: `evaluateGroundRouteDangerLevel` è marcata `# da testare` nel proprio docstring ed è strutturalmente più rotta di un semplice refactoring meccanico (usa attributi/proprietà che non esistono su `Military` sotto quei nomi, inizializza un dict con il tipo `list` anziché liste vuote) — completarla è lavoro di progettazione (Fase 3, "costruzione del layer mancante"), non un fix. Nessun chiamante nel codebase la invoca oggi.

Verificato end-to-end con costruzione di oggetti reali: `Waypoint → Edge → Route → Military.time2attack → time_to_ground_intercept → Route.travelTime()`, incluso il percorso con override di velocità. Suite completa rimasta a 2315 test / 0 errori / 0 fallimenti dopo tutte le correzioni.

## Motivazione

`Region` (storage/query) e `Tactical_Evaluation` (consumo) erano già entrambi costruiti attorno a `DataType.Route`/`Edge`/`Waypoint` nell'intento originale del progetto — mancava solo che quel percorso fosse davvero eseguibile. Riparare i bug meccanici di costruzione era quindi meno rischioso e più coerente con l'architettura esistente che introdurre una terza rappresentazione locale (l'alternativa scartata: dare a `Ground_Route_Manager.py` proprie classi locali come sul lato aereo).

## Conseguenze

Delle 9 decisioni del set "Fase 2" (design post-audit), questa pagina copre solo la #3. Sintesi dello stato di tutte le 9, per completezza del quadro decisionale di quella sessione: **7 risolte e attuate** (#1 `Structure.py` resta in roadmap; #2 `Production`/`Storage`/`Transport`/`Urban` da riscrivere seguendo `Military.py`; #3 questa pagina; #4 `Cylinder` confermato come modello di geometria delle minacce, `Threat`/`Sphere`/`Hemisphere`/`Volume` deprecati; #5 `Military.get_c2_efficiency()` unico metro di intelligence, `Region.get_region_intelligence_efficiency()` eliminato; #8 `Classi.py` eliminato; #9 `visualizer.py` mantenuto e riparato) e **2 esplicitamente rimandate** dall'utente (#6 `Manager.py` vs `Scenario_Manager.CommandControl`; #7 `Coalition.py`).

**Gap ancora aperto, non affrontato da questa decisione**: `Ground_Route_Manager.py` non produce ancora oggetti `DataType.Route`/`Edge` — ha tuttora proprie classi locali `Waypoint`/`Edge`/`NavigationGraph` (verificato a HEAD: `Logic/Ground_Route_Manager.py` definisce ancora le proprie `Waypoint`/`Edge`/`NavigationGraph` con `find_optimal_path`/`find_min_danger_path`/ecc., nessun riferimento a `DataType.Route` o a `Region.add_route` nel file). Significa che, sebbene la catena `Waypoint→Edge→Route→Military` sia ora funzionalmente corretta in isolamento, **nulla nel codice la alimenta ancora in pratica** — descritto nella memoria di origine come lavoro di Fase 3, non iniziato. Confermato non iniziato anche a questa data (2026-09-18).

## Fonti

- [[project_fase2_design_decisions]] (memoria di origine, 9 decisioni)
- [[module-audit-2026-08-16]] (origine dell'elenco delle 9 decisioni)
