# Capitolo 3 — Lo strato 1: lo scheduler dei contatti

Modulo: `Logic/Contact_Scheduler.py`.

> **Aggiornato a `84a47670` (2026-10-11).** Fino a `533cd1f5` il modulo era invariato rispetto a `6754bf1c`.
> Dalla fase **F4c** della Missione (postura continua degli asset senza missione, `af2efbe6`) lo scheduler
> conosce un solo concetto nuovo, quello di **aereo a terra**: un insieme di id, `grounded`, che il chiamante
> passa a `schedule_contacts` e che cambia **solo le portate** con cui due asset si vedono (§3.5, §3.6).
> Tutto il resto — rotta↔cilindro, CPA/TCPA, potatura a livello blocco — è invariato, e lo scheduler
> **non conosce le missioni né il dominio di coordinamento**: le finestre sono per coppia di asset, quindi sono
> le stesse a prescindere da come il chiamante raggruppa gli asset in forze (capitolo 6 §6.12). Resta vero che
> gli argomenti `routes`/`starts`/`speeds` di `schedule_contacts` li produce
> `Logic/Mission_Adapter.session_movements` a partire dalle `Mission` dell'ordine (capitolo 6 §6.10). Il modulo
> ha 1332 righe; i riferimenti `:riga` sono ricalcolati su `84a47670`.

## 3.1 Scopo e confine

Risponde a **quando** due forze si incontrano. Non risolve alcun ingaggio: non decide chi rileva
davvero (Pd), chi spara per primo (latenze di reazione), chi colpisce (Pk) — è il lavoro dello
strato 2 (`Logic/Engagement_Resolver.py`), che consuma ciò che qui viene prodotto. Il confine è
netto di proposito: questo strato è **deterministico e verificabile con la sola
trigonometria**, quello stocastico e ha bisogno dell'RNG di sessione
(`Logic/Contact_Scheduler.py:12-19`).

## 3.2 I tre meccanismi

### A — Rotta contro volume di minaccia

`threat_windows`/`route_threat_windows` (`Logic/Contact_Scheduler.py:437-521`, `:588-616`). Una
rotta attraversa il cilindro di un `ThreatAA`: si compone `Cylinder.getIntersection` (geometria
già esistente e testata) con la scansione temporale della rotta (`route_legs`, equivalente a
`Route.travelTimeToEdge` + `Route.positionAtTime`). Si lavora **solo** su `DataType.Route/Edge/
Waypoint`, il modello canonico di dominio confermato dalla decisione Q1 (v. wiki
`decisions/route-model-unification`), mai sul modello interno di `Air_Route_Manager`
(`:22-29`).

Tre casi degeneri disambiguati (`:443-459`): arco interamente dentro il cilindro (nessun
attraversamento di superficie: `getIntersection` restituirebbe `(False, None)`, indistinguibile
da "nessuna intersezione" — disambiguato con `Cylinder.innerPoint` sugli estremi); arco con un
solo estremo dentro; tangenza (un solo punto, nessun estremo interno: `getIntersection` solleva
`ValueError` "Intersezione anomala", trattato come contatto di misura nulla, non un errore di
programmazione, `:453-455`, `:536-542`). Le finestre di archi consecutivi sono **fuse**: una
rotta che entra sull'arco *i* ed esce sull'arco *i+2* produce una sola `ThreatWindow`
(`:457-459`, `_merge_threat_intervals` a `:567-585`).

### B — CPA/TCPA fra mobili

`closest_point_of_approach` (`:687-754`) e `range_intervals` (`:757-818`). Due asset su rotte
proprie: `t* = -(Δr·Δv)/|Δv|²` dà l'istante di massimo avvicinamento, valido per moto relativo
rettilineo uniforme. Poiché una rotta è una **spezzata**, il calcolo non si fa una volta sulla
rotta intera ma su ogni sottointervallo delimitato dai waypoint **di entrambe** le rotte
(`_breakpoints`, `:638-662`), dove le due velocità sono costanti per costruzione; il risultato
globale è il minimo dei minimi locali. Il caso degenere `|Δv|² ~ 0` (fermi, o paralleli alla
stessa velocità) non divide per zero: la distanza è costante e si prende l'estremo iniziale
(`:731-733`, costante `VELOCITY_EPS` a `:94-98`).

Per il rilevamento non basta il solo CPA (dice *quanto* ci si è avvicinati, non *da quando a
quando* si è stati a tiro): `range_intervals` risolve l'equazione completa
`|Δr + Δv s|² = R²` su ogni sottointervallo, e fonde gli intervalli disgiunti risultanti
(due rotte che si incrociano più volte entrano e escono dal raggio più volte, `:757-818`).

### C — Potatura gerarchica a livello `Block`

`block_pair_candidates`/`region_block_pairs` (`:1115-1212`). Valutare il CPA di tutte le coppie
di asset è O(N²), impraticabile fino al limite dichiarato di 10.000 asset
(`Logic/Contact_Scheduler.py:41-48`). Si scartano prima le coppie di `Block`/`Military` il cui
**inviluppo di movimento** nella finestra considerata non può in nessun caso produrre un
contatto: due blocchi più distanti di

```
(v_max_A + v_max_B) * orizzonte + portata_A + portata_B [+ margin]
```

non si incontrano, punto (`:1118-1132`). Il test è un confronto fra due numeri per coppia di
**blocchi**, ordini di grandezza meno numerosi degli asset. Il criterio è **conservativo**: un
blocco senza posizione nota non viene mai scartato (`:1130-1132`, l'assenza di dato non è una
prova di lontananza — la stessa logica, applicata al contrario, della memoria
`feedback_no_visibility_low_priority`). `block_max_speed` (`:1025-1060`) considera anche il ramo
`off_road` dei veicoli, perché il movimento tattico non avviene su strada e usare solo il regime
stradale sottostimerebbe l'inviluppo — sottostimare l'inviluppo scarterebbe coppie che si
sarebbero incontrate, l'unico errore inaccettabile per un filtro conservativo.

## 3.3 Convenzioni rispettate da tutto il modulo

(`Logic/Contact_Scheduler.py:50-65`)

- **Tempo in secondi assoluti**: ogni rotta ha il proprio `t0`, due asset che partono in momenti
  diversi sono la norma.
- **Nessuna sorgente di casualità**: lo strato è puramente geometrico.
- **Ordinamento deterministico dei risultati**: fa parte del contratto di riproducibilità
  (v. capitolo 1, §1.3, vincolo 2).
- **Mai eccezioni per dati mancanti** (asset senza rotta, senza `detection_range`, rotta con
  velocità indefinita): `None` o lista vuota, più un log. Le eccezioni restano per gli argomenti
  fuori dominio.

## 3.4 Da rotta a `Leg`: `route_legs`/`static_legs`

`route_legs(route, t0=0.0, speed=None, horizon=None)` (`:266-325`) è la porta d'ingresso di
tutto il modulo: da qui in poi non si parla più di rotte ma di `Leg` (tratto a velocità costante,
in tempo assoluto). Lista vuota se la rotta è vuota o ha un arco a velocità indefinita — mai
un'eccezione (`:287-290`).

`static_legs(position, t_start, t_end)` (`:328-349`) produce il `Leg` unico di un asset **fermo**
(sito SAM, deposito, blocco in posizione): il caso più frequente di contatto in campagna non è
rotta contro rotta ma rotta contro bersaglio fermo, e senza questa funzione il chiamante dovrebbe
fabbricare una rotta fittizia solo per interrogare lo scheduler (`:328-334`).

## 3.5 Da rilevamento geometrico a `ContactWindow`

`contact_windows(asset_a, legs_a, asset_b, legs_b, range_a=None, range_b=None, range_type=...)`
(`:907-984`) è l'uscita principale del modulo verso lo strato 2. Le portate, se non fornite dal
chiamante, sono ricavate da `mutual_detection_ranges` (`:856-904`), che interroga ciascun asset
**sul dominio dell'altro** — `Mobile.detection_range(mode, range_type=...)`, dove `mode` è
'ground'/'air'/'sea' a seconda della classe del bersaglio (`DETECTION_MODE_BY_CLASS`,
`:104-109`) — perché lo stesso radar ha portate diverse contro un carro e contro un aereo.
`range_type` di default `DEFAULT_DETECTION_RANGE_TYPE = 'acquisition_range'`
(`Asset/Mobile.py:85`); con `'engagement_range'` la stessa funzione risponde a "quando sono a
tiro" invece che "quando si vedono" (`:923-925`).

**Aereo a terra (F4c).** `mutual_detection_ranges(asset_a, asset_b, range_type, *, grounded_a=False,
grounded_b=False)` (`:856-904`) e `contact_windows(..., *, grounded_a=False, grounded_b=False)` (`:907-984`)
hanno due parametri keyword nuovi che dicono se l'asset è un aereo parcheggiato (nessuna missione, capitolo 4
§4.30). L'effetto è confinato alla funzione interna `_range(observer, target, observer_grounded,
target_grounded)` (`:879-902`):

- come **osservatore** un aereo a terra non ha portata (`None`: sensori spenti, passivo);
- come **bersaglio** è interrogato nel modo `GROUNDED_DETECTION_MODE = 'ground'` (`:113`), cioè come un veicolo
  o una struttura, non come un aereo (`'air'`): il suo rilevatore usa la portata contro bersagli di superficie.

Con entrambi i flag `False` (default) il comportamento è quello di prima. I flag valgono solo per le portate
**derivate**: una portata imposta dal chiamante (`range_a`/`range_b`) resta quella (`:927-928`). La finestra
risultante, quando solo uno dei due ha portata, è **unidirezionale** (`t_mutual_start`/`t_mutual_end` `None`,
`:959`, `first_detector` è chi vede).

La distinzione fra rilevamento **unidirezionale** e **bidirezionale** è esplicita perché decide
chi spara per primo (`:200-208`):

- `[t_start, t_end]` usa la portata **maggiore** delle due: il primo contatto in assoluto, e chi
  lo ottiene è `first_detector`;
- `[t_mutual_start, t_mutual_end]` usa la portata **minore**: da quel momento entrambi si vedono;
  `None` se uno dei due non vede mai l'altro.

## 3.6 Orchestrazione: `schedule_contacts`

`schedule_contacts(blocks_a, blocks_b, horizon, routes=None, starts=None, speeds=None, t0=0.0,
margin=0.0, range_type=..., skip_same_side=True, grounded=None)` (`:1217-1303`) mette insieme i tre meccanismi
nell'ordine che li rende trattabili: prima la potatura a livello blocco (C), poi il CPA solo
sulle coppie di asset superstiti (B). Un asset senza rotta in `routes` non è ignorato: se ha una
posizione, è trattato come **fermo** per tutta la finestra (`static_legs`, `:1231-1233`) — il
caso più comune in campagna (un sito SAM, un deposito, una base). Dal 2026-10-05 le tre mappe
`routes`/`starts`/`speeds` arrivano a `schedule_contacts` da `Mission_Adapter.session_movements`
(`Logic/Session_Simulator.py:813-818`): la firma dello scheduler non è cambiata per le missioni, e un asset
senza missione è "senza rotta", cioè fermo.

**`grounded` (F4c).** L'unico parametro aggiunto è `grounded: Optional[Iterable[str]]`, l'insieme degli id
degli aerei a terra calcolato dalla sessione (`Mission_Adapter.grounded_assets`, capitolo 6 §6.14). Diventa un
`frozenset` (`:1261`) e, per ogni coppia di asset superstite alla potatura, `contact_windows` riceve
`grounded_a=_asset_id(asset_a) in grounded` e `grounded_b=...` (`:1296-1299`). `None` o insieme vuoto =
comportamento di prima, percorso per percorso. **La potatura per blocco non cambia**: `block_max_speed` e
`block_reach` (§3.2 C) continuano a contare velocità e portata degli aerei a terra nell'inviluppo del loro
blocco, anche se sono fermi e senza sensori. È una scelta **conservativa** dichiarata nel docstring
(`:1246-1248`): si esaminano più coppie di blocchi di quante servirebbero, ma nessun contatto va perso. Resta
quindi un costo, non un errore.

Restituisce una lista di `ContactWindow` ordinata per `(t_start, asset_a_id, asset_b_id)`:
**l'ordine è parte del contratto**, è ciò che rende la sessione riproducibile a parità di seed,
non il seed da solo (`:1249-1252`).

## 3.7 Diagramma D3 — tipi di dominio dello scheduler

```mermaid
classDiagram
    class Leg {
        +float t_start
        +float t_end
        +tuple p_start
        +tuple p_end
        +str edge_name
        +duration() float
    }

    class ThreatWindow {
        +float t_entry
        +float t_exit
        +Point3D entry_point
        +Point3D exit_point
        +str threat_id
        +float danger_level
        +str route_name
        +tuple edge_names
        +duration() float
    }

    class CPA {
        +float time
        +float distance
        +Point3D point_a
        +Point3D point_b
        +bool degenerate
    }

    class ContactWindow {
        +str asset_a_id
        +str asset_b_id
        +float t_start
        +float t_end
        +float t_cpa
        +float distance_cpa
        +float range_a
        +float range_b
        +float t_mutual_start
        +float t_mutual_end
        +str first_detector
        +duration() float
        +is_mutual() bool
    }

    Leg <.. ThreatWindow : prodotta scansionando i Leg di una rotta
    Leg <.. CPA : calcolata sui Leg di due asset
    CPA <.. ContactWindow : t_cpa/distance_cpa presi dal CPA nella finestra
```

Le frecce tratteggiate (`<..`) indicano una dipendenza funzionale (una funzione che consuma un
tipo per produrne un altro), non un'associazione strutturale permanente: nessuno di questi
oggetti mantiene un riferimento agli altri dopo la costruzione.
