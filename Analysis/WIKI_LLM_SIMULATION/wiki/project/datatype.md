---
title: "DataType"
type: project-module
tags: [package-python, datatype, geometria, routing, architecture, dwm]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/DataType/]
related_decisions: ["[[datatype-route-edge-waypoint]]", "[[region-tactical-strategic-refactor]]"]
related: ["[[context-state]]", "[[block]]", "[[logic-routing]]"]
---

## Scopo

Il package `DataType` (`Code/Dynamic_War_Manager/Source/DataType/`) raccoglie i tipi dato "primitivi" del progetto, trasversali a tutti gli altri sottosistemi: geometria (aree, volumi, cilindri, sfere), stato di salute degli oggetti (`State`), carico economico (`Payload`), eventi generici (`Event`), minacce (`Threat`) e struttura di rotta (`Waypoint`, `Edge`, `Route`, `Limes`). Sono classi "foglia" pensate per essere importate da `Asset/`, `Block/`, `Context/`, `Logic/`, senza dipendenze verso quei package (eccezione nota: `Edge.py`/`Waypoint.py` importano `Asset` solo per un type hint).

Questa pagina **supera** il vecchio audit una-tantum `Analysis/Modules/10_DataType.md` (2026-08-16): rispetto ad allora, una parte consistente dei bug documentati è stata **corretta** nel frattempo (Fase 2 del refactoring routing, chiusa 2026-08-21 — vedi [[datatype-route-edge-waypoint]]), mentre altri sono rimasti intatti. Il quadro attuale resta eterogeneo: `State`, `Payload`, `Cylinder` restano solide e testate; `Edge` e `Waypoint` sono passate da "strutturalmente non istanziabili" a **funzionanti**; `Volume`, `Area`, `Limes`, `Sphere`/`Hemisphere`, `Threat` restano scheletri incompleti o non integrati; **`Classi.py`, il file orfano segnalato nel vecchio audit, è stato rimosso** — non compare più nel filesystem né in alcun grep sul codice sorgente (verificato 2026-09-18).

## File e classi principali

| File | Righe | Contenuto | Stato (2026-09-18) |
|---|---|---|---|
| `Area.py` | 118 | Area 2D (`SHAPE2D`, raggio, centro) alla base di `Volume`. | Invariato: validazione inerte, `inside()` stub, **bug aggiuntivo confermato**: i setter (`shape`/`radius`/`center`) chiamano `self.checkParam(shape=param)` ma `checkParam(self, shape, radius, center)` non ha default → `TypeError` immediato per argomenti mancanti, ancora prima del bug di indice già noto. |
| ~~`Classi.py`~~ | — | Reimplementazione giocattolo di `Payload`/`Point`/`Segment`/`Block`/`Asset` ecc., mai importata da nessuno. | **RIMOSSO.** File non più presente in `DataType/`; nessun residuo nel codice. Evidenza concreta di cleanup rispetto al vecchio audit. |
| `Cylinder.py` | 924 | Cilindro 3D standalone. Geometria completa: distanze, tangenti, intersezioni. | Invariato, maturo. Usato da `Mobile.air_defense_volume()` e `Logic/Air_Route_Manager.ThreatAA`. `Test_Cylinder.py`: 15 test OK. |
| `Edge.py` | 203 | Arco di rotta (wpA→wpB, tipo percorso, pericolo, velocità). | **BUG PRINCIPALI RISOLTI** (vedi sezione dedicata sotto). Ora istanziabile e usato realmente. |
| `Event.py` | 121 | Evento generico (`EventParams` + `Event`): tipo, timer, energia/potenza/massa, posizione, asset_id, destinazione. | Invariato: `isPush/isPop/isHit/isAssimilate/isMove` leggono `self._type` mai assegnato (solo `self._event_type` esiste) → `AttributeError` se chiamati. **Nuovo dettaglio trovato**: `destroy()` assegna `self._typ` (terza grafia diversa, né `_type` né `_event_type`) — refuso indipendente. **Nuovo dettaglio trovato**: `_validate_all_params` dichiara `'destination': str` in `type_checks`, ma `__init__` tipizza `destination: Optional[int]` — se `destination` viene passato come int (come da firma), la validazione lo rifiuta con `TypeError`. |
| `Hemisphere.py` | 201 | Semisfera 3D standalone, geometria completa. | Invariato, nessuna relazione con `Sphere`/`Volume`/`Cylinder`. |
| `Limes.py` | 112 | Confine poligonale di una `Region` (deque di punti). | Invariato: `Limes()` senza argomenti solleva ancora `AttributeError: 'NoneType' object has no attribute 'name'` (riconfermato leggendo il codice riga per riga). Inutilizzabile allo stato attuale. |
| `Payload.py` | 229 | Carico economico/risorse (`goods`, `energy`, `hr`, `hc`, `hs`, `hb`). | Invariato, maturo: validazione, operatori aritmetici/di confronto completi. `Test_Payload.py`: 7 test OK. |
| `Route.py` | 147 | Contenitore dati di una rotta: `route_type`, `edges: {(wpA,wpB): Edge}`, aggregati (lunghezza, tempo, danger level, velocità). | Invariato nella struttura; `checkParam` era già corretto (staticmethod, indice giusto). Ora però gli `Edge` che contiene sono realmente costruibili (vedi sotto), quindi i metodi aggregati (`length()`, `travelTime()`, ecc.) sono **davvero eseguibili**, non solo teorici. |
| `Sphere.py` | 137 | Sfera 3D standalone, geometria completa. | Invariato, nessuna relazione con `Volume`/`Cylinder`. |
| `State.py` | 240 | Stato di salute (`health`, `state_value: StateCategory`, `success_ratio`). | Invariato, maturo e ben testato. `Test_State.py`: 67 test OK. `isCritical()` corretto. |
| `Threat.py` | 58 | Minaccia generica (`level`, `name`, `id`). | Invariato: `self._obj = obj` con `obj` mai parametro di `__init__` → `NameError` garantito ad ogni istanziazione reale; mai istanziata in produzione (solo type-hint/`MagicMock(spec=Threat)` nei test). |
| `Volume.py` | 79 | Volume 3D (`Area` + `SHAPE3D` + eventuale `radius_at_height`). | Invariato: firma `__init__(area_base, volume_shape, radius_at_height=None)` ancora incompatibile con i chiamanti reali (`Asset/Vehicle.py:243`, `Asset/Structure.py:188`, entrambi chiamano `Volume(length=..., width=..., height=...)` — confermato riga per riga, stesso bug del vecchio audit). |
| `Waypoint.py` | 105 | Punto di rotta (`point: Point3D`, `name`, `reference: Asset` opzionale). | **BUG PRINCIPALI RISOLTI**, stesso pattern di `Edge.py` (vedi sotto). |

## Edge.py e Waypoint.py — bug del vecchio audit ora risolti (verificato leggendo il codice attuale)

Il vecchio audit (2026-08-16) documentava tre bug concatenati in `Edge.__init__`/`checkParam` e un pattern analogo in `Waypoint`. Rileggendo `Edge.py` e `Waypoint.py` oggi (2026-09-18), risulta che:

- **`checkParam` è ora un `@staticmethod` corretto** in entrambe le classi (`Edge.py` riga 44, `Waypoint.py` riga 30), invece del vecchio metodo senza `self` e senza decoratore. Le chiamate `self.checkParam(...)` nei setter ora si bindano correttamente (nessun conteggio argomenti errato).
- **L'indice del risultato è corretto**: `if not check_results[0]:` (booleano), non più `check_results[1]` (il messaggio, sempre truthy). La validazione è quindi **davvero attiva**, non più inerte.
- **Il refuso `calcLenght`/`self` extra è sparito**: `Edge.__init__` ora chiama `self.calcLength()` (spelling corretto, nessun argomento extra), che a sua volta chiama `self._wpA.distanceFrom(self._wpB)` — funzionante.
- Di conseguenza, `Edge(wpA, wpB, path_type, danger_level, speed, name)` e `Waypoint(point, name, obj_reference)` sono **oggi realmente istanziabili** con argomenti validi, cosa impossibile all'epoca del vecchio audit.

Questa correzione coincide con la chiusura della decisione [[datatype-route-edge-waypoint]] (Fase 2, 2026-08-21): la memoria di progetto associata riporta "richiesto il fix di ~10 bug meccanici tra Waypoint/Edge/Route/Military/Tactical_Evaluation per rendere `DataType.Route` davvero costruibile — verificato con oggetti reali, suite piena 2315/0/0". Coerentemente, anche il bug segnalato nel vecchio audit su `Logic/Tactical_Evaluation.evaluateGroundRouteDangerLevel` (riga ~559, iterazione su `Route.edges` come attributo di classe) risulta oggi corretto: il codice attuale usa `route.edges.items()` sul parametro istanza `route`, non sulla classe.

**Nota residua non bloccante**: `Edge.__init__` costruisce ancora `self._line`, `self._line2d`, `self._lenght`, `self._travel_time` **prima** di chiamare `checkParam` (righe 30-36) — se venissero passati oggetti non conformi (es. non `Waypoint`), l'errore arriverebbe come `AttributeError` sull'accesso a `.point`/`.point2d`/`.distanceFrom` invece che come eccezione di validazione esplicita. Con argomenti corretti (il solo percorso oggi esercitato) questo non ha effetti pratici.

**Copertura test invariata**: nonostante il fix, non esistono ancora `Test_Edge.py`/`Test_Waypoint.py`/`Test_Route.py` dedicati — `Edge`/`Waypoint`/`Route` restano esercitati solo indirettamente tramite i moduli consumatori (`Military.py`, `Tactical_Evaluation.py`, `Region.py`), non da una suite propria del package `DataType`.

## Dipendenze e relazioni tra tipi

Nessuna gerarchia di ereditarietà tra `Volume`, `Cylinder`, `Sphere`, `Hemisphere`, `Threat` — restano classi sorelle indipendenti, come nel vecchio audit:

- `Volume` compone un `Area` + una forma `SHAPE3D`; importa ma non usa mai `Sphere`/`Hemisphere`.
- `Cylinder` è del tutto autonomo, la classe geometrica più matura e completa del package.
- `Sphere`/`Hemisphere` sono geometrie autonome quasi gemelle, senza collegamento a `Volume`/`Cylinder`.
- `Threat` importa `Sphere`/`Hemisphere` ma non li usa mai nel corpo della classe.
- Nel codice realmente usato oggi, il "volume di minaccia/difesa aerea" resta rappresentato con **`Cylinder`**, non con `Threat`/`Sphere`/`Volume`: `Mobile.air_defense_volume() -> Optional[Cylinder]` e `Logic.Air_Route_Manager.ThreatAA` sono gli usi concreti, invariati.

Altre dipendenze verificate ancora valide:
- `Context/Coalition.py:15` — `from Dynamic_War_Manager.Source.Volume import Volume`, path di import ancora errato (manca `Code.` e il segmento `DataType`), a differenza di `Waypoint.py`/`Edge.py` dove questo pattern è stato corretto. Bug persistente, fuori scope diretto di `DataType/` ma segnalato per completezza.
- `Asset/Vehicle.py:243`, `Asset/Structure.py:188` — chiamano ancora `Volume(length=..., width=..., height=...)`, incompatibile con la firma reale. Bug del chiamante, persistente.

## Divisione responsabilità Route.py vs Logic/*_Route_Manager.py — duplicazione ancora presente

Verificato di nuovo (2026-09-18) che la duplicazione descritta nel vecchio audit **non è stata eliminata**, solo resa meno "rotta" sul lato `DataType`:

- **`Logic/Air_Route_Manager.py` continua a NON importare `DataType.Waypoint`/`Edge`/`Route`** (unico import da `DataType` resta `Cylinder`, per `ThreatAA`). Ridefinisce e istanzia le proprie classi locali `Waypoint(name, position, ref)`, `Edge(name, order_position, wpA, wpB, speed)`, `Route(name, length, danger)` — firme diverse e incompatibili con le omonime di `DataType` (confermato con nuove istanziazioni reali in produzione, es. righe 330, 709-798, 978-1030, 1257-1268 di `Air_Route_Manager.py`).
- **`Logic/Ground_Route_Manager.py` continua a NON importare nulla da `DataType`** (verificato di nuovo via grep sugli import). Le proprie classi locali `Waypoint`/`Edge` e l'algoritmica di `NavigationGraph` restano separate.
- **`DataType.Route`/`Edge`/`Waypoint` restano il modello "ufficiale"** consumato da `Region._routes`, `Military.time_to_ground_intercept`/`time2attack`, `Tactical_Evaluation.evaluateGroundRouteDangerLevel` — ma **nessun punto del codice di produzione istanzia mai un `DataType.Route`/`Edge`/`Waypoint` reale**: l'unica ricerca di `= Route(`/`= Edge(`/`= Waypoint(` nel codice di produzione trova solo le classi locali di `Air_Route_Manager.py`. `Region.add_route()` risulta ancora **mai chiamato** da alcun modulo di produzione (l'unica occorrenza di `.add_route(` trovata via grep è `Utility/visualizer.py:210`, un metodo omonimo ma non correlato di una classe di debug `Space`, non `Region.add_route`).

**Conclusione aggiornata**: il fatto che `Edge`/`Waypoint` siano ora costruibili correttamente **non ha ancora prodotto un ponte tra i due mondi**. Resta da scrivere il pezzo che converte l'output di `Air_Route_Manager`/`Ground_Route_Manager` (i loro `Path`/`Route` locali) in `DataType.Route` da inserire in `Region` — esplicitamente definito come lavoro non ancora iniziato ("Fase 3") nella memoria di progetto associata alla decisione [[datatype-route-edge-waypoint]].

## Stato attuale

**Bug noti tuttora presenti (verificati con lettura del codice attuale):**

| File:riga | Bug |
|---|---|
| `DataType/Area.py:101-114` | `checkParam(self, shape, radius, center)` senza default: i setter la chiamano con un solo kwarg → `TypeError` immediato, prima ancora di raggiungere il bug noto `check_results[1]` invece di `[0]` (quest'ultimo tuttora presente). |
| `DataType/Limes.py:24` | `Limes()` (nessun argomento) solleva `AttributeError: 'NoneType' object has no attribute 'name'`. Classe inutilizzabile allo stato attuale. |
| `DataType/Threat.py:36` | `self._obj = obj` — `obj` non è mai un parametro di `__init__` → `NameError` garantito ad ogni istanziazione reale. Mai istanziata in produzione. |
| `DataType/Volume.py` (firma) | Incompatibile con `Asset/Vehicle.py:243` e `Asset/Structure.py:188` (`length=/width=/height=` vs `area_base/volume_shape/radius_at_height`). |
| `DataType/Event.py` | `isPush/isPop/isHit/isAssimilate/isMove` leggono `self._type` mai assegnato; `destroy()` assegna invece `self._typ` (terzo refuso); `type_checks['destination']` (`str`) contraddice l'annotazione `Optional[int]` di `__init__`. |
| `Context/Coalition.py:15` | Import path errato (`from Dynamic_War_Manager...` invece di `from Code.Dynamic_War_Manager...`), pattern già corretto altrove ma non qui. |

**Bug del vecchio audit confermati RISOLTI:**

| File | Bug (vecchio audit) | Stato oggi |
|---|---|---|
| `DataType/Edge.py` | `calcLenght(self)` refuso + arg extra; `checkParam` senza `self`/`@staticmethod`; `check_results[1]` invece di `[0]` | **Risolto**: `calcLength()` corretto, `checkParam` è `@staticmethod`, indice `[0]` corretto. |
| `DataType/Waypoint.py` | Stesso pattern di `checkParam` | **Risolto**, stesso fix. |
| `Logic/Tactical_Evaluation.py:559` | `for k, v_edge in Route.edges:` (attributo di classe) | **Risolto**: ora `route.edges.items()` sul parametro istanza. |
| `DataType/Classi.py` | File orfano non importato | **Rimosso** dal filesystem. |

**Copertura test:** invariata rispetto al vecchio audit nei numeri assoluti — `Test_Cylinder.py` (15 OK), `Test_Payload.py` (7 OK), `Test_State.py` (67 OK) sono le uniche suite dedicate del package. Nessun `Test_Edge.py`/`Test_Waypoint.py`/`Test_Route.py`/`Test_Area.py`/`Test_Limes.py`/`Test_Threat.py`/`Test_Volume.py`/`Test_Event.py` esiste, nonostante `Edge`/`Waypoint` siano oggi funzionanti — occasione di copertura non ancora colta.

## Decisioni architetturali rilevanti

- [[datatype-route-edge-waypoint]] — decisione (Fase 2, chiusa 2026-08-21) di rendere `DataType.Route`/`Edge`/`Waypoint` il modello dati canonico per il routing terrestre/aereo, con conseguente fix dei bug di validazione/istanziazione documentati sopra. Resta aperta la Fase 3 (ponte reale tra `Logic/*_Route_Manager.py` e `DataType.Route`), non ancora iniziata.
- [[region-tactical-strategic-refactor]] — il refactoring di `Region.py` (16 funzioni tattiche estratte in `Tactical_Analysis.py`/`Tactical_Evaluation.py`) ha toccato il codice consumatore di `DataType.Route`/`Edge`, ma non ha modificato le classi di `DataType` stesse.

## Note

- `Waypoint.distanceFrom()` gestisce tre casi (`Point2D`, `Point3D`, `Waypoint`) con un bug preesistente e minore nel ramo `Point2D` (righe 92-95: usa due volte `self._point.x` invece di `x` e poi `y` per la formula della distanza) — non aggiornato dal fix di Fase 2, resta un potenziale calcolo errato se mai il ramo `Point2D` venisse esercitato (oggi non risulta chiamato con un `Point2D` in nessun percorso di produzione verificato).
- `Route.py.checkParam` era già corretto anche nel vecchio audit (unica classe del gruppo Edge/Waypoint/Area/Route ad avere fin da subito `@staticmethod` e indice `[0]` giusto) — nessun cambiamento necessario qui.
