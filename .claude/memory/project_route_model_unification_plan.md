---
name: project-route-model-unification-plan
description: "Unificazione dei tre modelli Route/Edge/Waypoint incompatibili. DECISIONE PRESA 2026-09-22: DataType.Route/Edge/Waypoint e' l'unico modello di dominio, i modelli interni ai due Route Manager sono stato di lavoro privato dell'algoritmo di ricerca. Piano a 5 fasi; Fase 1 (frontiera di conversione Logic/Route_Adapter.py) FATTA."
metadata:
  type: project
---

# Modello di rotta unico — decisione e piano a 5 fasi

**Origine**: prima delle tre questioni aperte del §9 di
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`, bloccante per la
Fase 3 del motore di sessioni virtuali (`Logic/Contact_Scheduler.py`): lo scheduler deve
calcolare CPA/TCPA e intersezioni rotta↔volume su **un solo** modello di rotta.

## La situazione trovata (verificata riga per riga, 2026-09-22)

Tre implementazioni indipendenti e incompatibili:

| Modello | Dove | Chi lo consuma |
|---|---|---|
| **`DataType/Waypoint.py` + `Edge.py` + `Route.py`** (canonico) | 219+206+106 righe, `Point3D`/`Line3D`, `positionAtTime`, `travelTimeToEdge`, `min/max/avg_danger_level` | `Context/Region.py`, `Block/Military.py`, `Logic/Tactical_Evaluation.py`, `Command/Command_Types.py` |
| `Waypoint`/`Edge`/`NavigationGraph` in `Logic/Ground_Route_Manager.py` (135 righe totali) | Dijkstra con funzione di peso configurabile | **nessuno in produzione** — solo `Test_Ground_Route_Manager.py` |
| `Waypoint`/`Edge`/`Route`/`Path`/`PathCollection`/`RoutePlanner` in `Logic/Air_Route_Manager.py` (righe 411-760 circa) | ricerca ricorsiva con evitamento `ThreatAA` | **nessuno in produzione** — `Test_Air_Route_Manager.py` e `Utility/visualizer.py` |

**Fatto decisivo trovato**: nessun consumatore di produzione chiama `RoutePlanner.calcRoute`
o `NavigationGraph.find_optimal_path`. I due generatori sono scollegati dall'ecosistema, e
l'ecosistema consuma solo il tipo canonico. Quindi la migrazione non ha da rompere alcun
contratto esistente: il costo vero e' la ~100 di test di scenario in
`Test_Air_Route_Manager.py` che asseriscono sui tipi interni.

## Decisione (ferma)

1. **`DataType.Route`/`Edge`/`Waypoint` e' l'unico modello di rotta del dominio.** Conferma
   della decisione di agosto 2026, che resta valida per le stesse ragioni piu' due nuove:
   e' gia' progettato per l'aria (`path_type == 'air'`, `Point3D`/`Line3D`) ed e' l'unico che
   porta `positionAtTime`/`travelTimeToEdge`, cioe' esattamente cio' che serve alla Fase 3.
2. **I modelli interni ai due Route Manager restano, ma come stato di lavoro privato**
   dell'algoritmo di ricerca (code di priorita', ricorsione, metriche parziali di un ramo).
   Non e' duplicazione da eliminare a tutti i costi: `Path`/`PathCollection` servono davvero
   alla ricerca, e riscrivere la ricorsione perche' lavori direttamente su `DataType.Edge`
   (che costruisce due oggetti sympy `Line` per arco) sarebbe piu' lento e piu' rischioso.
   **Non devono pero' mai uscire dal loro modulo.**
3. **La conversione avviene in un solo punto**, l'uscita pubblica del path-finding. Non si
   scrive un "adattatore bidirezionale": la direzione e' una sola, interno → canonico.
4. **`Air_Route_Manager.Route` e' invece duplicazione pura** e sparisce: e' costruita solo da
   `Path.to_route()` e non porta nulla che `Path` non abbia gia'. Idem per
   `Ground_Route_Manager.Waypoint`/`Edge`, che sono un grafo, non una rotta.

## Piano a 5 fasi

### Fase 1 — frontiera di conversione — **FATTA 2026-09-22**
Additiva, nessun comportamento esistente cambiato.
- **`Logic/Route_Adapter.py`** (nuovo): `to_canonical_route(container, name, path_type,
  route_type, speed)` per l'aria (duck-typed su `.edges` lista **o** dizionario, cosi'
  accetta sia `Path` sia la `Route` interna), `ground_path_to_route(graph, waypoints, ...)`
  per il terreno (prende anche il grafo perche' il path-finding a terra restituisce la sola
  sequenza di nodi e gli archi — `danger_level`, `path_type`, `max_speed` — li sa solo il
  grafo), `route_type_from_path_types` (deduce `ground`/`air`/`water`/`mixed`).
  **Non importa ne' Air_ ne' Ground_Route_Manager**: dipendenza a senso unico, nessun ciclo.
- **`RoutePlanner.calcCanonicalRoute(*args, canonical_speed=None, **kwargs)`** e
  **`NavigationGraph.find_canonical_route(start, end, name, speed, weight_func)`**: le uscite
  pubbliche supportate. Import di `Route_Adapter` locale al metodo.
- **`DataType/Edge.py` reso robusto ai segmenti degeneri**: prima `Line3D`/`Line2D` erano
  costruite nel `__init__` e sympy rifiuta due punti coincidenti, quindi una **salita
  verticale pura** (stessa x,y) — che il pianificatore aereo produce normalmente scavalcando
  una minaccia — rendeva l'arco **non costruibile**. Era il vero blocco tecnico della
  migrazione (limite gia' annotato in Fase 1 del motore e lasciato aperto). Ora `_buildLine`
  registra `None` + log di debug, e `minDistance`/`intersectPoint` degradano.
  Corretto anche il logger del modulo (mancava `.logger`: ogni chiamata avrebbe sollevato
  AttributeError, stesso difetto gia' corretto in `DataType/Route.py`).
- **Due trappole trovate e gestite nell'adattatore**, non nel tipo canonico:
  (a) `Route.getWaypoints()` mette i waypoint in un heap di tuple `(nome, waypoint)` e a
  parita' di nome confronta i `Waypoint`, che non hanno `__lt__` → TypeError. I generatori
  riusano gli stessi nomi (`wp_A0_1` e `wp_A0_1_alt` su rami diversi), quindi i nomi vengono
  de-duplicati in conversione (`nome#k`);
  (b) gli archi consecutivi hanno waypoint distinti con lo stesso punto: l'adattatore riusa
  l'oggetto canonico gia' creato, cosi' la rotta e' una spezzata connessa.
- Archi di lunghezza nulla scartati con log di debug (non sono percorrenza).
- **`Test/Test_Route_Adapter.py`**, 26 test, oggetti reali su entrambi i lati.
  Verifica end-to-end eseguita anche su un `RoutePlanner` vero con una `ThreatAA` vera.

### Fase 2 — migrare i consumatori esistenti al tipo canonico
- `Utility/visualizer.py` passa a `calcCanonicalRoute` (usa `route.getPoints()`, che sul tipo
  canonico non esiste: serve un helper o l'iterazione sugli archi).
- I ~100 test di scenario di `Test_Air_Route_Manager.py` continuano a testare `calcRoute`
  (la ricerca), e si aggiunge una manciata di test su `calcCanonicalRoute` (la frontiera).
  **Non convertire i test di scenario**: verificano l'algoritmo, non il tipo di uscita.
- Rischio: basso. Nessun consumatore di produzione da toccare.

### Fase 3 — collegare la pianificazione ai dati reali
- `RoutePlanner` riceve oggi minacce costruite a mano nei test: collegare
  `Military.air_defense_threats()` (Fase 2 del motore) alla pianificazione vera.
- `NavigationGraph` non ha alcun produttore: il grafo di navigazione terrestre non viene
  costruito da nessuna parte. **Questo e' il vero lavoro mancante a terra**, non la
  conversione di tipo.
- Rischio: medio. E' lavoro nuovo, non migrazione.

### Fase 4 — rendere private le classi interne
- Rinominare `Waypoint`/`Edge`/`Route`/`Path`/`PathCollection` di `Air_Route_Manager` in
  `_SearchWaypoint`/`_SearchEdge`/`_SearchPath`/`_SearchPathCollection` (e le due di
  `Ground_Route_Manager` in `_GraphWaypoint`/`_GraphEdge`), **eliminando** `Route` interna e
  `Path.to_route()`.
- Attenzione: `Test_Air_Route_Manager.py:10` fa `from ... import *`, quindi il rename rompe
  la suite in blocco — va fatto insieme ai test, in un commit solo.
- Attenzione: **non toccare `ThreatAA`, `build_threat_aa`, `threat_reaction_times`,
  `threat_danger_level`, `_air_defense_weapons`** (Fase 2 del motore): `ThreatAA.edgeIntersect`
  lavora sull'`Edge` interno e continuera' a farlo — e' logica di ricerca, non di dominio.
- Rischio: medio-alto solo per volume di modifiche meccaniche. Nessun rischio concettuale.

### Fase 5 — il Contact_Scheduler consuma solo il tipo canonico
- `Logic/Contact_Scheduler.py` (Fase 3 della roadmap del motore) prende `DataType.Route` e
  nient'altro. E' il test di non-regressione della decisione: se lo scheduler ha bisogno di
  qualcosa che solo il modello interno sa, la separazione e' sbagliata.

## Cosa NON e' stato deciso qui
- **Il sistema di riferimento** (piano cartesiano locale per teatro vs. coordinate
  geodetiche) resta aperto, §9 del documento e §8 di `ARCHITETTURA_CORE_AGNOSTICO.md`.
  Il tipo canonico usa `Point3D` in metri e non prende posizione.
- `Edge.calcLength()` **non** distingue per `path_type`, nonostante il commento nel codice
  dica il contrario: calcola sempre la distanza 3D. Va deciso se il commento e' il bug o se
  lo e' il codice (per `onroad`/`water` la lunghezza dovrebbe essere la proiezione 2D).
  Non toccato in Fase 1 per non cambiare numeri gia' usati altrove.

**How to apply:** chiunque debba far produrre o consumare rotte a un modulo usa
`DataType.Route` e, se sta scrivendo un generatore, converte con `Logic/Route_Adapter.py`.
V. [[project_virtual_session_engine_design]] per il contesto del motore.
