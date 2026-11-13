# Capitolo 10, parte A — Atlante dei diagrammi: scheduler, fire control e risolutore d'ingaggio

Questo file è la **parte A** del capitolo 10 (l'atlante dei diagrammi). Il pilota, con la scala dei livelli L0-L4, le convenzioni e i diagrammi D57-D66, è in
[`11_Atlante_Diagrammi.md`](11_Atlante_Diagrammi.md): qui non si ripete la scala, si **estende** il livello L2 (tipi e API pubblica, con la tabella completa dei simboli)
e il livello L3 (sequenze di chiamata) a tre moduli del core che nel pilota erano «parziali» o «da fare»: `Logic/Contact_Scheduler`, `Logic/Fire_Control` e
`Logic/Engagement_Resolver`. I diagrammi nuovi sono **D67-D87**, più **D133** (aggiunto il 2026-11-13) e il **D82 riscritto** (v. §10A.4). I diagrammi D1-D56 dei capitoli 1-8 non sono toccati: dove una regola ha già il suo diagramma (livello L4)
il nuovo diagramma rimanda a quello e non lo duplica.

**Come leggere.** I riferimenti sono `percorso:riga`, **relativi a `Code/Dynamic_War_Manager/Source/`**, come nel resto del manuale; una riga senza percorso (`:1379`) è del modulo di cui si sta parlando.
Nei diagrammi di sequenza `X->>X` è la chiamata a una funzione privata dello stesso modulo; nei diagrammi di funzioni per ruolo (flowchart) una freccia `A --> B` significa «le funzioni di `A`
**chiamano** funzioni di `B`» (non «i dati vanno da `A` a `B`»). Le didascalie hanno la forma `*Diagramma Dnn — ... (livello Lx, verificato a f009eb43).*`.

**Come sono stati verificati.** Codice a `f009eb43` (ultimo commit che tocca il codice sotto `Code/`; `git diff f009eb43 HEAD -- Code/` mostra solo `Test/baseline/scenario_baseline.json`,
nessun sorgente cambia). Elenchi di classi, campi, metodi e funzioni con `_strumenti/inventario.py --tabella` (estrazione con `ast`, sola lettura); chiamanti **dentro il modulo** e **nel core**
con una seconda estrazione `ast` dei nomi chiamati (scritta per questo capitolo, non è nello strumento); ordine delle chiamate nelle sequenze **letto nel codice, riga per riga**,
perché l'estrazione non dice in quale ramo si chiama. Nessun test eseguito: nessun codice è stato toccato.

## 10A.1 I diagrammi di questa parte

| Dnn | Livello | Tipo | Titolo | Modulo | Sezione | Si collega a |
|---|---|---|---|---|---|---|
| D67 | L2 | `classDiagram` | Tipi dello scheduler con tutti i membri (`Leg`, `ThreatWindow`, `CPA`, `ContactWindow`, `GroundedSchedule`) | `Contact_Scheduler` | 10A.2 | D3, D34 |
| D68 | L2 | `flowchart TD` | Le funzioni dello scheduler per ruolo e le dipendenze fra i gruppi | `Contact_Scheduler` | 10A.2 | D1, D58 |
| D69 | L3 | `sequenceDiagram` | `schedule_contacts`: dalla potatura per blocco alle finestre di coppia | `Contact_Scheduler` | 10A.2 | D34, D65 |
| D70 | L3 | `sequenceDiagram` | `contact_windows`: portate, intervalli, CPA e finestre | `Contact_Scheduler` | 10A.2 | D3, D65 |
| D71 | L2 | `classDiagram` | Tipi della fire control (`_Weapon`, `WeaponPolicy`, `AreaWeapon`) e `ShotSpec` | `Fire_Control` | 10A.3 | D47, D4 |
| D72 | L2 | `flowchart TD` | Le funzioni della fire control per ruolo e le dipendenze | `Fire_Control` | 10A.3 | D10, D58 |
| D73 | L3 | `sequenceDiagram` | La fire control dai registri: dalla coppia (tiratore, bersaglio) alla tupla di `ShotSpec` | `Fire_Control` | 10A.3 | D10, D13, D11 |
| D74 | L3 | `sequenceDiagram` | L'involucro `restrict_by_policy`: dalla politica d'armi alla chiamata nel risolutore | `Fire_Control` | 10A.3 | D46, D48, D43 |
| D75 | L3 | `sequenceDiagram` | L'arma per il fuoco su posizione: `area_fire_weapon` e `area_fire_pk` | `Fire_Control` | 10A.3 | D49, D50 |
| D76 | L2 | `classDiagram` | I tipi interni della run (`_Shadow`, `_Candidate`, `_ForceState`, `_PendingGroup`, `_EngagementRun`) | `Engagement_Resolver` | 10A.4 | D4, D47 |
| D77 | L2 | `flowchart TD` | Le funzioni di modulo e i tipi per ruolo | `Engagement_Resolver` | 10A.4 | D58 |
| D78 | L2 | `flowchart TD` | Le fabbriche del fattore di rilevamento `detection_factor` | `Engagement_Resolver` | 10A.4 | D12 |
| D79 | L2 | `flowchart TD` | I metodi di `_EngagementRun` per ruolo 1/2: costruzione, rilevamento, scelta del tiro | `Engagement_Resolver` | 10A.4 | D5, D25, D26 |
| D80 | L2 | `flowchart TD` | I metodi di `_EngagementRun` per ruolo 2/2: risoluzione, intercettazione, disingaggio, regole F7a | `Engagement_Resolver` | 10A.4 | D6, D22, D24, D37, D43 |
| D81 | L3 | `sequenceDiagram` | `resolve_engagement`: validazione, costruzione della run e ciclo principale | `Engagement_Resolver` | 10A.4 | D5 |
| D82 | L3 | `sequenceDiagram` | `_detect_direction`: dai passaggi nel volume proprio all'estrazione e al candidato (**riscritto 2026-11-13**; prima: «una estrazione di rilevamento») | `Engagement_Resolver` | 10A.4 | D5, D23, D131, D133 |
| D83 | L3 | `sequenceDiagram` | `_schedule_next`: l'ordine delle chiamate della scelta del tiro | `Engagement_Resolver` | 10A.4 | D11, D13, D25, D26, D43, D44 |
| D84 | L3 | `sequenceDiagram` | `_on_launch`: dal lancio alla salva in volo | `Engagement_Resolver` | 10A.4 | D5, D25, D37, D45 |
| D85 | L3 | `sequenceDiagram` | `_on_resolve`: intercettazione, danno per colpo e dottrina | `Engagement_Resolver` | 10A.4 | D5, D22, D24, D27, D33 |
| D86 | L3 | `sequenceDiagram` | `apply_engagement_result`: danni e consumi sugli asset reali | `Engagement_Resolver` | 10A.4 | D9, D13 |
| D87 | L2 | `flowchart LR` | Che cosa il core importa da `Engagement_Resolver`, e chi | `Engagement_Resolver` | 10A.4 | D58, D59 |
| D133 | L3 | `sequenceDiagram` | `_detect_passes`: un'estrazione per passaggio, permanenza D-5, CPA e candidato per passaggio (**nuovo 2026-11-13**) | `Engagement_Resolver` | 10A.4 | D82, D131 |

Conteggio: **L2** = D67, D68, D71, D72, D76, D77, D78, D79, D80, D87 (10); **L3** = D69, D70, D73, D74, D75, D81, D82, D83, D84, D85, D86, **D133** (12); totale **22** (D67-D87 più D133, numerato fuori sequenza perché assegnato nel 2026-11-13 dopo D129: i D130-D132 e D134 sono diagrammi L4 del capitolo 4, v. `11_Atlante_Diagrammi.md`).

Sequenze già esistenti, **non duplicate**: D5 (la coda degli eventi dentro un ingaggio), D11 (rimando `not_before`), D25 (prelazione ai lanciatori), D45 (`return_fire` e `_WAKE`), D50 (fuoco su posizione nella coda di sessione),
D65 (`run_session` 2/3, che chiama `schedule_contacts` e `resolve_engagement` come scatole). I nuovi diagrammi L3 mostrano **dentro** queste scatole.

## 10A.2 L2 e L3 — `Logic/Contact_Scheduler` (1662 righe, 63 simboli)

> **Aggiornamento 2026-11-13.** Il modulo è cambiato con la VA (`585dbc65`): **un'unica inserzione di 84 righe** dopo `_merge_intervals` (due funzioni nuove, `altitude_intervals` `:955` e `intersect_intervals` `:1013`, gruppo «B - CPA e intervalli di portata»). La tabella di fondo è rigenerata (63 righe, righe di `a389cadb`: riga ≤ 954 invariata, ≥ 955 più 84); **le righe nel testo di D67-D70 restano a f009eb43** (stessa regola: ≥ 955 → +84).

Lo strato 1 calcola **quando**: tratti di rotta (`Leg`), finestre di contatto (`ContactWindow`), CPA/TCPA, potatura per blocco. È puramente geometrico, senza RNG
(docstring del modulo, «Nessuna sorgente di casualità»). Il modulo ha **cinque tipi** (quattro `dataclass(frozen=True)`: `Leg` `:122`, `ThreatWindow` `:147`, `CPA` `:181`, `ContactWindow` `:197`,
più `GroundedSchedule` `:243`, classe normale con `__slots__ = ('_intervals',)` `:259`), **39 funzioni** di primo livello e nessun'altra classe. Costanti: `DEFAULT_INTERSECTION_TOLERANCE` `:86`,
`TIME_EPS` `:92`, `VELOCITY_EPS` `:98`, `DETECTION_MODE_BY_CLASS` `:104`, `GROUNDED_DETECTION_MODE` `:113`, `ALWAYS` `:116`.

I tre «meccanismi» del docstring sono tre gruppi di funzioni: **A** rotta contro volume di minaccia (`threat_windows`, `route_threat_windows`), **B** CPA/TCPA e intervalli di portata
(`closest_point_of_approach`, `range_intervals`, `contact_windows`), **C** potatura gerarchica per blocco (`block_pair_candidates`, `region_block_pairs`). Un fatto che il codice mostra e che il pilota
non diceva: **il meccanismo A (`threat_windows`, `route_threat_windows`) e `region_block_pairs` non hanno nessun chiamante sotto `Source/` fuori dal modulo e dai test** (`grep` sui sorgenti non di test;
`Logic/Weapon_Delivery.py:73` li nomina solo in un commento). Il percorso di produzione del core usa `schedule_contacts` (che usa `block_pair_candidates`), `trim_contact_window`, `route_legs`,
`static_legs`, `clamp_legs`, `position_on_legs`, `range_intervals`, `GroundedSchedule`.

### Tipi (D67)

*Diagramma D67 — i tipi di `Contact_Scheduler` con tutti i membri pubblici e i loro legami funzionali (livello L2, verificato a f009eb43).*

```mermaid
classDiagram
    class Leg {
        <<dataclass frozen>>
        +float t_start
        +float t_end
        +tuple p_start
        +tuple p_end
        +str edge_name
        +duration() float
    }
    class ThreatWindow {
        <<dataclass frozen>>
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
        <<dataclass frozen>>
        +float time
        +float distance
        +Point3D point_a
        +Point3D point_b
        +bool degenerate
    }
    class ContactWindow {
        <<dataclass frozen>>
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
    class GroundedSchedule {
        <<classe con __slots__>>
        -dict _intervals
        +__init__(intervals)
        +of(grounded) GroundedSchedule
        +at(asset_id, t) bool
        +always(asset_id) bool
        +ever(asset_id) bool
        +intervals(asset_id) tuple
        +transitions(asset_id) tuple
        +always_ids() frozenset
        +ids() frozenset
        +__bool__() bool
        +__eq__(other) bool
        +__hash__() int
        +__repr__() str
    }

    Leg ..> ThreatWindow : threat_windows
    Leg ..> CPA : closest_point_of_approach
    CPA ..> ContactWindow : t_cpa e distance_cpa
    GroundedSchedule ..> ContactWindow : finestre spezzate a decollo e atterraggio
```

Rapporto con **D3** (capitolo 3 §3.9), che resta: D3 disegna gli stessi cinque tipi. Qui si aggiungono la stereotipia (`frozen`, `__slots__`) e **tutti** i membri di `GroundedSchedule`, compresi quelli del protocollo Python.
Una differenza trovata nel confronto: D3 mostra in `GroundedSchedule` un campo `+dict intervals`; nel codice `intervals` è un **metodo** (`intervals(asset_id)`, `:327`) e l'unico attributo è `_intervals` (privato, `:259`). **Non ho corretto D3**
(regola: non toccare i capitoli 1-8). `Leg.duration`, `ThreatWindow.duration` e `ContactWindow.duration` sono `@property` (`:141`, `:174`, `:233`), come `ContactWindow.is_mutual` (`:237`): si leggono come attributi, non si chiamano.
`GroundedSchedule.of` è un `@classmethod` (`:292`); il diagramma non ha un marcatore per questo. `Leg`, `CPA`, `ThreatWindow` non sono mai modificati dopo la costruzione (frozen): i consumatori ne creano di nuovi
(es. `Mission_Adapter._timeline` costruisce `CS.Leg(...)`, `Logic/Mission_Adapter.py:991`).

### Le funzioni per ruolo (D68)

*Diagramma D68 — i gruppi di funzioni di `Contact_Scheduler` e le chiamate fra gruppi; «consumatori» = `Session_Simulator`, `Mission_Adapter`, `Engagement_Resolver` (livello L2, verificato a f009eb43; il nodo B aggiornato a `a389cadb` con le due primitive della VA).*

```mermaid
flowchart TD
    O["orchestrazione<br/>schedule_contacts, _pair_windows,<br/>_asset_legs, _operative_assets, _asset_id"]
    P["C - potatura per blocco<br/>block_pair_candidates, _block_profile,<br/>block_max_speed, block_reach,<br/>region_block_pairs, _as_block"]
    W["finestre di contatto<br/>contact_windows, trim_contact_window,<br/>mutual_detection_ranges, detection_mode_for,<br/>_first_detector, _first_contained"]
    C["B - CPA e intervalli di portata<br/>closest_point_of_approach, range_intervals,<br/>altitude_intervals, intersect_intervals,<br/>_overlap, _breakpoints,<br/>_relative_motion, _merge_intervals"]
    L["tratti<br/>route_legs, static_legs, clamp_legs,<br/>legs_span, position_on_legs"]
    M["A - minacce<br/>threat_windows, route_threat_windows,<br/>_cylinder_of, _edge_threat_fractions,<br/>_fraction_along, _merge_threat_intervals"]
    V["vettori<br/>_to_xyz, _to_point, _sub, _dot, _lerp"]
    G["GroundedSchedule<br/>of, at, transitions, always, ..."]
    EXT["consumatori nel core<br/>SS, MA, ER"]

    O --> P
    O --> W
    O --> L
    O --> C
    O --> G
    W --> C
    W --> L
    C --> L
    C --> V
    L --> V
    M --> L
    M --> V
    P --> M
    P --> V
    EXT --> O
    EXT --> W
    EXT --> L
    EXT --> C
    EXT --> G
```

Lettura: le frecce sono le chiamate a nome di funzione fra gruppi (estrazione `ast`; un riferimento passato come valore non è contato). `P --> M` esiste per un solo motivo: `block_reach` usa `_cylinder_of`
(`:1226`, `:536`) per includere il raggio dei volumi di difesa nel raggio d'azione del blocco; per il resto il meccanismo A è isolato dal percorso di produzione. I consumatori nel core chiamano:
`Session_Simulator` → `schedule_contacts`, `trim_contact_window`, `clamp_legs`, `static_legs`, `position_on_legs`, `GroundedSchedule`, `Leg`; `Mission_Adapter` → `route_legs`, `clamp_legs`, `Leg`, `GroundedSchedule`;
`Engagement_Resolver` → `position_on_legs`, `range_intervals`, `GroundedSchedule`, `TIME_EPS` e, dal 2026-11, `altitude_intervals`, `intersect_intervals` (VA), `clamp_legs`, `closest_point_of_approach` (FP, `_pass_cpa`) (import `Logic/Engagement_Resolver.py:436-441`). Rimando a **D58** (import fra i moduli) e a **D34** (come `GroundedSchedule` attraversa scheduler, risolutore e fire control).

### La sequenza di `schedule_contacts` (D69)

*Diagramma D69 — `schedule_contacts`: potatura per blocco, tratti degli asset e finestre di ogni coppia (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant SS as run_session
    participant SC as schedule_contacts
    participant BP as block_pair_candidates
    participant GS as GroundedSchedule
    participant AL as _asset_legs
    participant PW as _pair_windows
    participant CW as contact_windows
    SS->>SC: schedule_contacts(items_a, items_b, horizon, routes, starts, speeds, t0, margin, range_type, grounded, legs, only_assets)
    SC->>GS: GroundedSchedule.of(grounded)
    SC->>BP: block_pair_candidates(blocks_a, blocks_b, horizon, margin, skip_same_side)
    Note over BP: per ogni blocco _block_profile con block_max_speed e block_reach, scarto se la distanza dei centroidi supera la somma degli inviluppi piu margin
    BP-->>SC: coppie (item_a, item_b), oggetti originali
    opt nessuna coppia superstite
        SC-->>SS: lista vuota
    end
    loop per ogni coppia
        SC->>SC: _operative_assets(_as_block(item_a)) e _operative_assets(_as_block(item_b))
        loop per ogni asset A, poi per ogni asset B (filtro only_assets)
            SC->>AL: _legs_for(asset) con cache per id(asset)
            AL-->>SC: tratti dati dal chiamante, dalla rotta o fermo
            SC->>PW: _pair_windows(asset_a, legs_a, asset_b, legs_b, range_type, grounded)
            PW->>GS: transitions(id_a) e transitions(id_b), poi at(id, istante) per lo stato
            PW->>CW: contact_windows(...) una volta, o una per sottointervallo a stato costante
            CW-->>PW: ContactWindow
            PW-->>SC: finestre della coppia
        end
    end
    SC->>SC: windows.sort per (t_start, asset_a_id, asset_b_id)
    SC-->>SS: lista di ContactWindow
```

Righe: `GroundedSchedule.of` `:1441`; `block_pair_candidates` `:1443-1444` (uscita se vuota `:1445-1446`); `only_assets` → `wanted` `:1451`; `_legs_for` `:1453` (cache `legs_cache`, chiave `id(asset)`; chiama `_asset_legs` `:1457`);
`_operative_assets(_as_block(...))` `:1462-1463`; `_pair_windows` `:1485`; ordinamento finale `:1487`. Dentro `_asset_legs` (`:1538`) l'ordine è: lista **vuota** data dal chiamante = asset assente dalla sessione (ritorna `[]`, F6-A);
lista data non vuota = tratti usati tali e quali se stanno nella finestra, altrimenti `clamp_legs`; altrimenti `route_legs` + `clamp_legs` dalla rotta (`routes`, `starts`, `speeds`); altrimenti `static_legs` sulla posizione.
Dentro `_pair_windows` (`:1492`): `_overlap` `:1503`, tagli alle transizioni di `GroundedSchedule` dentro la sovrapposizione `:1507`; senza tagli una sola `contact_windows` con lo stato letto al punto medio (`:1512`), con tagli una per sottointervallo
con `clamp_legs` e lo stato al punto medio (`:1520`). L'**ordine delle finestre fa parte del contratto** di riproducibilità (docstring di `schedule_contacts`): è la riga `:1487`. Per il chiamante in sessione v. **D65** (`only_assets` dopo una ri-pianificazione, D40).

### La sequenza di `contact_windows` (D70)

*Diagramma D70 — `contact_windows`: portate derivate, intervalli di portata maggiore e minore, CPA e finestra (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant PW as _pair_windows
    participant CW as contact_windows
    participant MD as mutual_detection_ranges
    participant AST as asset A e asset B
    participant RI as range_intervals
    participant CL as clamp_legs
    participant CP as closest_point_of_approach
    PW->>CW: contact_windows(asset_a, legs_a, asset_b, legs_b, range_type, grounded_a, grounded_b)
    opt range_a o range_b non imposti dal chiamante
        CW->>MD: mutual_detection_ranges(asset_a, asset_b, range_type, grounded_a, grounded_b)
        MD->>AST: detection_range(mode, range_type) di A sul dominio di B e di B sul dominio di A
        MD-->>CW: range_a e range_b, None se non dichiarate o osservatore a terra
    end
    CW->>RI: range_intervals(legs_a, legs_b, portata maggiore)
    RI-->>CW: intervalli di contatto, se vuoti ritorna lista vuota
    opt due portate disponibili
        CW->>RI: range_intervals(legs_a, legs_b, portata minore)
        RI-->>CW: intervalli di rilevamento reciproco
    end
    CW->>CW: _first_detector(range_a, range_b)
    loop per ogni intervallo di contatto
        CW->>CL: clamp_legs(legs_a, start, end) e clamp_legs(legs_b, start, end)
        CW->>CP: closest_point_of_approach(legs_a ritagliati, legs_b ritagliati)
        CP-->>CW: CPA con time e distance
        CW->>CW: _first_contained(intervalli reciproci, start, end)
    end
    CW-->>PW: lista di ContactWindow
```

Righe: `mutual_detection_ranges` `:1056` (solo se una delle due portate è `None`; chiamata da `_pair_windows` senza portate imposte, quindi **sempre** nel percorso di sessione); `range_intervals` portata maggiore `:1070`, minore `:1075`
(solo con due portate, `:1075`); `_first_detector` `:1079`; per intervallo: `clamp_legs` e `closest_point_of_approach` `:1084-1085`, `_first_contained` `:1086`, `ContactWindow(...)` `:1088`. Dentro `range_intervals` (`:874`) l'ordine è
`_overlap`, `_breakpoints`, poi `_relative_motion` per ogni sottointervallo (risolve `|Δr + Δv s|² = R²`), infine `_merge_intervals`; `closest_point_of_approach` (`:804`) ha lo stesso scheletro con `t* = -(Δr·Δv)/|Δv|²` clampato al sottointervallo
e il caso degenere `|Δv|² <= VELOCITY_EPS`. `mutual_detection_ranges` (`:972`): un osservatore a terra ha portata `None` (sensori spenti); un bersaglio a terra è interrogato nel modo `GROUNDED_DETECTION_MODE` (`'ground'`), altrimenti nel modo
di `detection_mode_for(target)` (dalla classe del bersaglio, `DETECTION_MODE_BY_CLASS`). **`trim_contact_window`** (`:1129`) non ha un diagramma proprio: riusa gli stessi pezzi (`clamp_legs`, `closest_point_of_approach`, `_first_contained`, `range_intervals`
solo con due portate) su `[t_from, t_end]` e mantiene portate e `first_detector` della finestra originale; la usa `Session_Simulator` per la «forza occupata» (v. D40 e D65).

### Tabella completa dei simboli di `Logic/Contact_Scheduler`

Le colonne «Tipo», «Simbolo», «Firma» e «Riga» sono l'uscita di `inventario.py --tabella Logic/Contact_Scheduler` (63 righe a `a389cadb`, nell'ordine del file). «Gruppo» è il ruolo di D68; «Che cosa fa» è una sintesi dai docstring;
«Chiamata da» elenca i chiamanti **dentro il modulo** e **nel core** (`SS` = `Session_Simulator`, `MA` = `Mission_Adapter`, `ER` = `Engagement_Resolver`), ricavati con l'estrazione `ast` dei nomi chiamati: i test non sono contati.

| Gruppo | Tipo | Simbolo | Firma | Riga | Che cosa fa | Chiamata da |
|---|---|---|---|---|---|---|
| tipi | classe | `Leg` | `Leg`; campi: t_start, t_end, p_start, p_end, edge_name | `:122` | Tratto di rotta a velocità costante, in tempo assoluto. | `clamp_legs`, `route_legs`, `static_legs`, `MA:_timeline`, `MA:movement_legs`, `SS:_legs_after_bingo`, `SS:_return_legs`, `SS:_truncate_at_fuel_end` |
| tipi | metodo | `Leg.duration` | `duration(self)` | `:142` | Proprietà: `t_end - t_start`. | lettura dell'attributo in `SS:_consuming_legs`, `SS:_moving_speed`, `MA:airborne_legs` (`:1228`), `MA:mission_holds` (`:834`) |
| tipi | classe | `ThreatWindow` | `ThreatWindow`; campi: t_entry, t_exit, entry_point, exit_point, threat_id, danger_level, route_name, edge_names | `:147` | Intervallo in cui una rotta si trova dentro un volume di minaccia. | `threat_windows` |
| tipi | metodo | `ThreatWindow.duration` | `duration(self)` | `:175` | Tempo di esposizione alla minaccia [s]. | nessun chiamante nel core (solo test) |
| tipi | classe | `CPA` | `CPA`; campi: time, distance, point_a, point_b, degenerate | `:181` | Punto di massimo avvicinamento fra due mobili (Closest Point of Approach). | `closest_point_of_approach` (costruttore) |
| tipi | classe | `ContactWindow` | `ContactWindow`; campi: asset_a_id, asset_b_id, t_start, t_end, t_cpa, distance_cpa, range_a, range_b, t_mutual_start, t_mutual_end, first_detector | `:197` | Intervallo in cui due asset sono nel raggio di rilevamento (almeno unidirezionale). | `contact_windows`, `trim_contact_window` (costruttore); annotazione di tipo in `SS:_group_windows`; `ER:_detect` ne legge gli attributi senza importarla |
| tipi | metodo | `ContactWindow.duration` | `duration(self)` | `:234` | Proprietà: `t_end - t_start`. | nessun chiamante nel core |
| tipi | metodo | `ContactWindow.is_mutual` | `is_mutual(self)` | `:238` | True se esiste un intervallo in cui entrambi rilevano l'altro. | nessun chiamante nel core |
| GroundedSchedule | classe | `GroundedSchedule` | `GroundedSchedule`; campi: __slots__ | `:243` | Aerei a terra nel tempo (F5): per asset, gli intervalli `[t_inizio, t_fine)` a terra. | `MA:grounded_schedule`, `SS:_grounded_after_bingo`, `SS:_grounded_after_fuel` |
| GroundedSchedule | metodo | `GroundedSchedule.__init__` | `__init__(self, intervals)` | `:261` | Normalizza `{asset_id: [(lo, hi)]}`: ordina, fonde e valida gli intervalli. | `GroundedSchedule.of`; `MA:grounded_schedule` (costruttore) |
| GroundedSchedule | metodo | `GroundedSchedule.of` | `of(cls, grounded)` | `:293` | Normalizza None, `GroundedSchedule`, mappa di intervalli o iterabile di id (sempre a terra su `ALWAYS`). | `schedule_contacts`; `ER:_EngagementRun.__init__` (`:1669`) |
| GroundedSchedule | metodo | `GroundedSchedule.at` | `at(self, asset_id, t)` | `:311` | L'asset è a terra all'istante `t`. | `_pair_windows`; `ER` (`_gone`, `_grounded_in`, `_schedule_next`, `_on_launch`, `_on_resolve`, ...); `SS` (es. `_consuming_legs`); `MA:final_posture` |
| GroundedSchedule | metodo | `GroundedSchedule.always` | `always(self, asset_id)` | `:319` | L'asset è a terra su tutta la linea del tempo (insieme semplice, asset senza missione). | `always_ids`; `ER` (`_build_forces`, `_interceptors_of`, `_schedule_next`, `_init_breakpoints`) |
| GroundedSchedule | metodo | `GroundedSchedule.ever` | `ever(self, asset_id)` | `:323` | L'asset è a terra in qualche istante. | nessun chiamante nel core (solo test) |
| GroundedSchedule | metodo | `GroundedSchedule.intervals` | `intervals(self, asset_id)` | `:327` | Gli intervalli `(lo, hi)` a terra dell'asset (tupla vuota se non ne ha). | `SS:_grounded_after_fuel` (`:1498`), `SS:_grounded_after_bingo` (`:1645`) |
| GroundedSchedule | metodo | `GroundedSchedule.transitions` | `transitions(self, asset_id)` | `:330` | Istanti finiti in cui lo stato dell'asset cambia (decollo, atterraggio), ordinati. | `_pair_windows` |
| GroundedSchedule | metodo | `GroundedSchedule.always_ids` | `always_ids(self)` | `:335` | Id degli asset sempre a terra (l'insieme della F4c). | nessun chiamante nel core (solo test) |
| GroundedSchedule | metodo | `GroundedSchedule.ids` | `ids(self)` | `:339` | Id degli asset a terra in qualche istante. | `SS:_grounded_after_fuel` (`:1498`), `SS:_grounded_after_bingo` (`:1645`) |
| GroundedSchedule | metodo | `GroundedSchedule.__bool__` | `__bool__(self)` | `:343` | Protocollo Python: vero se almeno un asset ha intervalli. | implicito (`if grounded`) |
| GroundedSchedule | metodo | `GroundedSchedule.__eq__` | `__eq__(self, other)` | `:346` | Protocollo Python: uguaglianza per intervalli. | implicito |
| GroundedSchedule | metodo | `GroundedSchedule.__hash__` | `__hash__(self)` | `:349` | Protocollo Python: hash dei soli intervalli ordinati. | implicito |
| GroundedSchedule | metodo | `GroundedSchedule.__repr__` | `__repr__(self)` | `:352` | Protocollo Python: rappresentazione ordinata per asset. | implicito |
| vettori | funzione | `_to_xyz` | `_to_xyz(point)` | `:358` | `Point3D` (o qualunque oggetto con x/y/z) → terna di float. | `_block_profile`, `_edge_threat_fractions`, `route_legs`, `static_legs` |
| vettori | funzione | `_to_point` | `_to_point(xyz)` | `:363` | Terna di float → `Point3D`. | `closest_point_of_approach`, `threat_windows` |
| vettori | funzione | `_sub` | `_sub(u, v)` | `:367` | Differenza fra due terne. | `_fraction_along`, `_relative_motion`, `block_pair_candidates`, `closest_point_of_approach`, `range_intervals` |
| vettori | funzione | `_dot` | `_dot(u, v)` | `:371` | Prodotto scalare fra due terne. | `_fraction_along`, `block_pair_candidates`, `closest_point_of_approach`, `range_intervals` |
| vettori | funzione | `_lerp` | `_lerp(p0, p1, f)` | `:375` | Interpolazione lineare fra due terne con frazione `f`. | `clamp_legs`, `position_on_legs` |
| tratti | funzione | `route_legs` | `route_legs(route, t0, speed, horizon)` | `:383` | Scompone una `DataType.Route` nei suoi tratti, in tempo assoluto. | `_asset_legs`, `threat_windows`, `MA:_timeline`, `MA:_travel_time_to`, `MA:mission_holds` |
| tratti | funzione | `static_legs` | `static_legs(position, t_start, t_end)` | `:445` | Tratto unico di un asset fermo: un sito SAM, un deposito, un blocco in posizione. | `_asset_legs`, `SS:run_session` |
| tratti | funzione | `clamp_legs` | `clamp_legs(legs, lo, hi)` | `:469` | Ritaglia i tratti all'intervallo `[lo, hi]`, interpolando gli estremi tagliati. | `_asset_legs`, `_pair_windows`, `contact_windows`, `route_legs`, `trim_contact_window`, `MA:movement_legs`, `SS:_fuel_truncated`, `SS:_legs_after_bingo`, `SS:_truncate_at_fuel_end`, `SS:run_session` |
| tratti | funzione | `legs_span` | `legs_span(legs)` | `:495` | Intervallo di validità `[primo istante, ultimo istante]`, None se non ci sono tratti. | `_overlap` |
| tratti | funzione | `position_on_legs` | `position_on_legs(legs, t)` | `:508` | Posizione all'istante assoluto `t`, terna di float. None se non ci sono tratti. | `_relative_motion`, `closest_point_of_approach`, `range_intervals`, `threat_windows`, `ER:_position_at`, `SS:run_session` |
| minacce (A) | funzione | `_cylinder_of` | `_cylinder_of(threat)` | `:536` | Il `Cylinder` di una minaccia: accetta un `ThreatAA` o direttamente un `Cylinder`. | `block_reach`, `threat_windows` |
| minacce (A) | funzione | `_fraction_along` | `_fraction_along(p_start, p_end, point)` | `:541` | Frazione in [0, 1] del punto proiettato sul tratto `p_start -> p_end`. | `_edge_threat_fractions` |
| minacce (A) | funzione | `threat_windows` | `threat_windows(route, threat, t0, speed, horizon, threat_id, tolerance)` | `:554` | Intervalli di tempo assoluto in cui `route` attraversa il volume di `threat`. | `route_threat_windows`; nessun altro chiamante fuori dai test |
| minacce (A) | funzione | `_edge_threat_fractions` | `_edge_threat_fractions(cylinder, edge, tolerance)` | `:641` | Frazioni di ingresso/uscita di un arco nel cilindro, None se l'arco non lo tocca. | `threat_windows` |
| minacce (A) | funzione | `_merge_threat_intervals` | `_merge_threat_intervals(raw)` | `:684` | Fonde gli intervalli contigui (fine di uno == inizio del successivo, entro `TIME_EPS`). | `threat_windows` |
| minacce (A) | funzione | `route_threat_windows` | `route_threat_windows(route, threats, t0, speed, horizon, tolerance)` | `:705` | `threat_windows` su più minacce in una volta. | nessun chiamante nel core (solo test) |
| CPA e portata (B) | funzione | `_overlap` | `_overlap(legs_a, legs_b)` | `:738` | Intervallo in cui entrambi gli asset esistono, None se non si sovrappongono. | `_pair_windows`, `closest_point_of_approach`, `range_intervals` |
| CPA e portata (B) | funzione | `_breakpoints` | `_breakpoints(legs_a, legs_b, lo, hi)` | `:755` | Istanti in cui almeno uno dei due cambia velocità, più gli estremi. | `closest_point_of_approach`, `range_intervals` |
| CPA e portata (B) | funzione | `_relative_motion` | `_relative_motion(legs_a, legs_b, u, v)` | `:782` | (Δr, Δv, durata) del moto relativo sul sottointervallo `[u, v]`. | `closest_point_of_approach`, `range_intervals` |
| CPA e portata (B) | funzione | `closest_point_of_approach` | `closest_point_of_approach(legs_a, legs_b)` | `:804` | Istante e distanza di massimo avvicinamento fra due mobili. | `contact_windows`, `trim_contact_window` |
| CPA e portata (B) | funzione | `range_intervals` | `range_intervals(legs_a, legs_b, radius)` | `:874` | Intervalli in cui la distanza fra i due mobili è `<= radius`. | `contact_windows`, `trim_contact_window`, `ER:_detection_time`, `ER:engagement_intervals` |
| CPA e portata (B) | funzione | `_merge_intervals` | `_merge_intervals(intervals)` | `:938` | Fonde gli intervalli che si toccano o si sovrappongono (entro `TIME_EPS`). | `range_intervals` |
| B (intervalli) | funzione | `altitude_intervals` | `altitude_intervals(legs_a, legs_b, z_min, z_max, relative)` | `:955` | Intervalli in cui la quota di B è in `[z_min, z_max]`, relativa ad A o assoluta (VA); stessi sottointervalli di `range_intervals`, quota lineare; `ValueError` se `z_min > z_max`. | `ER:engagement_intervals` |
| B (intervalli) | funzione | `intersect_intervals` | `intersect_intervals(first, second)` | `:1013` | Intersezione di due liste ordinate di intervalli disgiunti (VA): due intervalli che si toccano entro `TIME_EPS` danno un intervallo nullo. | `ER:engagement_intervals` |
| finestre di contatto | funzione | `detection_mode_for` | `detection_mode_for(asset)` | `:1041` | Modo di rilevamento con cui un bersaglio di questa classe va interrogato. | `mutual_detection_ranges` |
| finestre di contatto | funzione | `mutual_detection_ranges` | `mutual_detection_ranges(asset_a, asset_b, range_type, grounded_a, grounded_b)` | `:1056` | Portate [m] con cui A vede B e B vede A. | `contact_windows` |
| finestre di contatto | funzione | `contact_windows` | `contact_windows(asset_a, legs_a, asset_b, legs_b, range_a, range_b, range_type, grounded_a, grounded_b)` | `:1107` | Finestre in cui due asset sono a portata di rilevamento l'uno dell'altro. | `_pair_windows` |
| finestre di contatto | funzione | `_first_detector` | `_first_detector(range_a, range_b)` | `:1187` | Chi ottiene il primo contatto: chi ha la portata più lunga. | `contact_windows` |
| finestre di contatto | funzione | `_first_contained` | `_first_contained(intervals, start, end)` | `:1201` | Il primo intervallo che cade dentro `[start, end]`, ritagliato ad esso. | `contact_windows`, `trim_contact_window` |
| finestre di contatto | funzione | `trim_contact_window` | `trim_contact_window(window, t_from, legs_a, legs_b)` | `:1213` | La finestra ritagliata a `[t_from, t_end]`, oppure None se il ritaglio la svuota (G4a). | `SS:_trim_busy`, `SS:run_session` |
| orchestrazione | funzione | `_asset_id` | `_asset_id(asset)` | `:1259` | Identificativo di dominio di un asset o di un blocco. Mai un id del simulatore. | `_asset_legs`, `_pair_windows`, `contact_windows`, `schedule_contacts` |
| potatura per blocco (C) | funzione | `block_max_speed` | `block_max_speed(block)` | `:1272` | Velocità massima [m/s] fra gli asset operativi del blocco, 0.0 se nessuno si muove. | `_block_profile` |
| potatura per blocco (C) | funzione | `block_reach` | `block_reach(block, mode)` | `:1310` | Raggio d'azione [m] del blocco: la più lunga fra portata di fuoco e di rilevamento. | `_block_profile` |
| potatura per blocco (C) | funzione | `_as_block` | `_as_block(item)` | `:1357` | Accetta indifferentemente un `Block` o un `BlockItem` (che lo incapsula in `.block`). | `block_pair_candidates`, `schedule_contacts` |
| potatura per blocco (C) | funzione | `block_pair_candidates` | `block_pair_candidates(blocks_a, blocks_b, horizon, margin, skip_same_side)` | `:1362` | Coppie di blocchi per cui un contatto non è escludibile nella finestra `horizon`. | `schedule_contacts`, `region_block_pairs` |
| potatura per blocco (C) | funzione | `_block_profile` | `_block_profile(block, horizon)` | `:1437` | (side, posizione, inviluppo) di un blocco: tutto ciò che serve alla potatura. | `block_pair_candidates` |
| potatura per blocco (C) | funzione | `region_block_pairs` | `region_block_pairs(region, side_a, side_b, horizon, category, margin)` | `:1446` | `block_pair_candidates` applicata ai blocchi di due schieramenti di una `Region`. | nessun chiamante nel core (solo test) |
| orchestrazione | funzione | `schedule_contacts` | `schedule_contacts(blocks_a, blocks_b, horizon, routes, starts, speeds, t0, margin, range_type, skip_same_side, grounded, legs, only_assets)` | `:1463` | Tutte le finestre di contatto fra due insiemi di blocchi, in `[t0, t0 + horizon]`. | `SS:run_session` |
| orchestrazione | funzione | `_pair_windows` | `_pair_windows(asset_a, legs_a, asset_b, legs_b, range_type, grounded)` | `:1576` | Finestre di una coppia, spezzate agli istanti di decollo/atterraggio dei due asset (F5). | `schedule_contacts` |
| orchestrazione | funzione | `_operative_assets` | `_operative_assets(block)` | `:1611` | Asset operativi di un blocco; lista vuota se il blocco non ne ha. | `schedule_contacts` |
| orchestrazione | funzione | `_asset_legs` | `_asset_legs(asset, routes, starts, speeds, t0, horizon, given)` | `:1622` | Tratti dell'asset: quelli dati dal chiamante, altrimenti dalla rotta (`route_legs`), altrimenti fermo (`static_legs`). | `schedule_contacts` |

## 10A.3 L2 e L3 — `Logic/Fire_Control` (1217 righe, 36 simboli)

> **Aggiornamento 2026-11-13.** Dalla BI (`munition_class`, `intercept_domains_for`) e dalla VA (`altitudes` nella fire control di registro, tre campi di quota in `shot_spec_for`) il modulo cresce da 1088 a 1217 righe e **tutte le righe della tabella di fondo sono rigenerate** (36 simboli, nessun simbolo nuovo dopo la BI). **Le righe nel testo di D71-D75 restano a f009eb43** e sono sfasate (la BI e la VA aggiungono righe in testa al file: costanti `AD_*` a `:293-302`, `in_altitude_envelope` a `:649`). La firma della fire control di registro è ora `fire_control(shooter, target, target_grounded=False, altitudes=None)` (`:934-935`), v. capitolo 4 §4.4, §4.37.

La fire control sceglie **con che cosa** spara un tiratore. Il risolutore la riceve come funzione iniettata `fire_control(shooter, target) -> ShotSpec | sequenza | None`; questo modulo ne fornisce una che legge i registri
d'arma (`make_registry_fire_control`), un involucro che la ristringe con la politica d'armi di missione (`restrict_by_policy`, F7a) e due funzioni per il fuoco su posizione (`area_fire_weapon`, `area_fire_pk`, F7b). Il modulo ha
**tre tipi** (`_Weapon` `:355`, classe con `__slots__` e non dataclass; `WeaponPolicy` `:882` e `AreaWeapon` `:993`, `dataclass(frozen=True)`), **29 funzioni** di primo livello (27 a f009eb43, più `munition_class` e `intercept_domains_for` della BI) e, dentro `make_registry_fire_control`,
**tre funzioni locali** che non sono nella tabella dell'inventario perché non sono di primo livello: `candidates` `:829`, `fire_control` `:838` (la callable che il risolutore chiama), e dentro `restrict_by_policy` `restrict` `:949`
e `restricted` `:972`/`:978` (due definizioni alternative a seconda di `ER.accepts_target_grounded`).

Importa i sette registri di dati (`Aircraft_Data`, `Aircraft_Loadouts`, `Aircraft_Weapon_Data`, `Ground_Weapon_Data`, `Ship_Data`, `Ship_Weapon_Data`, `Vehicle_Data`, `:198-204`), `Context.Context`, il risolutore (`ER`, per
`accepts_target_grounded`, e `ShotSpec`) e `Weapon_Delivery.bomb_engagement_estimate` (`:208`). Costanti del modulo: `AIR_ONLY_TASKS` `:219`, `FALLBACK_DIMENSION` `:224`, `ENGAGEMENT_RANGE_FRACTION` `:228`, `DEFAULT_TIME_OF_FLIGHT_S` `:234`,
`SALVO_ROUNDS` `:240`, `AUTOMATIC_FIRE_RATE_RPM` `:245`, `GUN_BURST_ROUNDS` `:250`, `WEAPON_COST_EXPONENT` `:273`, `SPEED_OF_SOUND_MS` `:278`, `KNOT_MS` `:281`, `PARKED_TYPE_BY_AIR_TYPE` `:287`, `PARKED_FALLBACK_TYPE` `:299`,
`AREA_FIRE_TASKS` `:989`; dalla BI `AD_LAND`/`AD_NAVAL` `:293`, `AD_TARGET_DOMAINS` `:294`, `AD_SIZE_GATED_NAVAL` `:295`, `AD_DETECTABLE_DEFAULT` `:297` (righe riverificate il 2026-11-10; le altre righe di questo capitolo sono a f009eb43). **Stime dichiarate dal codice** (i commenti sopra le costanti le chiamano «STIMA non tarata»): `FALLBACK_DIMENSION`, `ENGAGEMENT_RANGE_FRACTION`, `DEFAULT_TIME_OF_FLIGHT_S`, `SALVO_ROUNDS`,
`AUTOMATIC_FIRE_RATE_RPM`, `GUN_BURST_ROUNDS`, `WEAPON_COST_EXPONENT`, e dalla BI `AD_DETECTABLE_DEFAULT` (commento «STIMA [S]», BI-7); `AD_TARGET_DOMAINS` e `AD_SIZE_GATED_NAVAL` sono **scelte di progetto [S]** (regola dell'utente del 2026-11-07, decisione BI-12 (a)), non dati tarati; `SPEED_OF_SOUND_MS` e `KNOT_MS` sono invece definizioni fisiche. Questo capitolo non le ricalibra: le riporta come sono.

### Tipi (D71)

*Diagramma D71 — i tipi di `Fire_Control` e la `ShotSpec` del risolutore che essi producono o filtrano (livello L2, verificato a f009eb43).*

```mermaid
classDiagram
    class Weapon {
        <<_Weapon classe con __slots__>>
        +str model
        +str weapon_type
        +str domain
        +str kind
        +dict data
        +float range_m
        +float air_range_m
        +float speed_ms
        +float fire_rate
        +float min_alt
        +float max_alt
        +float max_height_m
        +frozenset tasks
        +float cost
        +dict efficiency
    }
    class WeaponPolicy {
        <<dataclass frozen>>
        +str mission_id
        +str domain
        +Mapping rules
        +bool self_escort
        +allows(weapon, target_class_name) bool
    }
    class AreaWeapon {
        <<dataclass frozen>>
        +str model
        +float caliber_mm
        +float max_range_m
        +float time_of_flight
        +int stock_per_round
        +object entry
    }
    class ShotSpec {
        <<da Engagement_Resolver, D4>>
        +str weapon
        +float max_range
        +float time_of_flight
        +int stock_per_round
        +frozenset intercept_domains
    }

    Weapon ..> ShotSpec : shot_spec_for
    AreaWeapon o-- Weapon : entry
    WeaponPolicy ..> ShotSpec : restrict_by_policy filtra weapon
```

Note a D71: i campi di `Weapon` sono gli `__slots__` di `_Weapon` (`:358`); `efficiency` è una `@property` (`:379`) che restituisce il sotto-dizionario `data['efficiency']` o `{}`. Nel diagramma il nome privato compare senza il trattino basso
iniziale (`Weapon` = `_Weapon`, `:355`) per non dipendere da come il renderer tratta i nomi che cominciano con `_`; lo stereotipo porta il nome vero. `ShotSpec` è del risolutore (D4 mostra tutti i suoi dieci campi, `intercept_domains` dalla BI; qui sono cinque,
quelli che questo modulo legge o imposta). `AreaWeapon.entry` è il record `_Weapon` scelto (campo con `repr=False`, `compare=False`, `:1010`), che `area_fire_pk` usa per leggere le righe d'efficacia del template. `WeaponPolicy.rules` diventa un
`MappingProxyType` in `__post_init__` (`:897`). Rimando a **D47** (i tipi nuovi della F7 e chi li consuma), che resta.

### Le funzioni per ruolo (D72)

*Diagramma D72 — i gruppi di funzioni di `Fire_Control`, le chiamate fra gruppi e i moduli esterni da cui prendono tipi o dati (livello L2, verificato a f009eb43).*

```mermaid
flowchart TD
    FAB["fabbrica<br/>make_registry_fire_control<br/>(e le funzioni locali candidates, fire_control)"]
    ARM["armi candidate<br/>_Weapon, _shooter_key, _candidate_weapons,<br/>_range_m, _air_range_m, _speed_ms,<br/>_number, _positive"]
    BER["bersaglio<br/>target_key, target_class, air_target_class_of,<br/>parked_target_class, _z"]
    SCE["filtri, ordine, ShotSpec<br/>rank_weapons, select_weapon, shot_spec_for,<br/>munition_class, intercept_domains_for,<br/>in_altitude_envelope, _surface_capable,<br/>_cell, preference_score, _attack_speed_kmh"]
    POL["politica d'armi<br/>WeaponPolicy, restrict_by_policy,<br/>weapon_category, weapon_tasks, _asset_id"]
    POS["fuoco su posizione<br/>AreaWeapon, area_fire_weapon,<br/>area_fire_pk"]
    ER["Engagement_Resolver<br/>ShotSpec, accepts_target_grounded"]
    WD["Weapon_Delivery<br/>bomb_engagement_estimate"]
    REG["registri d'arma e di piattaforma<br/>Aircraft_*, Ground_*, Ship_*, Vehicle_Data"]
    CTX["Context<br/>classi di bersaglio, dimensione"]

    FAB --> ARM
    FAB --> BER
    FAB --> SCE
    POS --> ARM
    POS --> BER
    POS --> SCE
    POL --> BER
    POL --> REG
    POL --> ER
    ARM --> REG
    BER --> CTX
    BER --> REG
    SCE --> ER
    SCE --> WD
```

Lettura: `SCE --> ER` perché `shot_spec_for` costruisce una `ShotSpec` (dalla BI con `intercept_domains`, calcolato da `intercept_domains_for` → `munition_class`, funzioni dello stesso gruppo, `Fire_Control.py:799`, `:761`); `SCE --> WD` perché `shot_spec_for` chiama `bomb_engagement_estimate` per le bombe contro la superficie (`:761`); `POL --> ER` perché `restrict_by_policy`
chiama `ER.accepts_target_grounded` (`:971`); `BER --> REG` perché `air_target_class_of` legge `Aircraft_Data._registry`. Chi chiama il modulo, nel core: `Session_Simulator` → `restrict_by_policy` (`:2277`) e `weapon_category`
(`_winchester_weapons`, `:1780`, `:1787`); `Mission_Adapter` → `WeaponPolicy` (`weapon_policies`, `:1918`); `Area_Fire` → `area_fire_weapon` (`plan_shot`, `:213`) e `area_fire_pk` (`resolve_area_fire`, `:285`). **Nessun chiamante nel core**
per `make_registry_fire_control` (la fire control è un argomento di `run_session`: la costruisce il chiamante) e per `select_weapon` (solo test). Rimando a **D10** (la selezione come flowchart di regola) e a **D58** (import).

### La sequenza della fire control dai registri (D73)

*Diagramma D73 — la callable `fire_control` di `make_registry_fire_control` per una coppia (tiratore, bersaglio): dalle armi candidate alla tupla ordinata di `ShotSpec` (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant RUN as _EngagementRun
    participant FCL as fire_control (locale)
    participant CAN as _candidate_weapons
    participant TK as target_key
    participant RK as rank_weapons
    participant SP as shot_spec_for
    participant WD as Weapon_Delivery
    RUN->>FCL: fire_control(shooter.asset, target.asset), con target_grounded=True se il bersaglio e a terra
    FCL->>FCL: _shooter_key(shooter), None se il tiratore non ha modello
    FCL->>CAN: candidates(key), _candidate_weapons solo al primo uso se memoize
    CAN-->>FCL: tupla di _Weapon, se vuota ritorna None
    FCL->>TK: target_key(target, grounded=target_grounded)
    TK-->>FCL: chiavi di efficacia, dimensione, e aereo, oppure None
    FCL->>FCL: _z(shooter) e _z(target) se il bersaglio e aereo o il tiratore e un aereo contro superficie
    FCL->>FCL: cache_key in choice_cache, se memoize e presente ritorna la scelta
    FCL->>RK: rank_weapons(weapons, keys, dimension, is_air, shooter_z, target_z, altitude_filter)
    Note over RK: per ogni arma _surface_capable se superficie, _cell, Pk, in_altitude_envelope se aereo, poi preference_score
    RK-->>FCL: tupla (arma, accuracy, destroy_capacity) in ordine di preferenza
    opt bombardiere con le due quote note
        FCL->>FCL: _attack_speed_kmh(shooter_key)
    end
    loop per ogni arma ordinata
        FCL->>SP: shot_spec_for(arma, accuracy, destroy_capacity, is_air, release_altitude_m, attack_speed_kmh)
        opt bomba contro superficie con quota di rilascio
            SP->>WD: bomb_engagement_estimate(weapon.data, quota di rilascio, velocita di attacco)
        end
        SP->>SP: intercept_domains_for(arma), classe di munizione e ad_detectable (BI)
        SP-->>FCL: ShotSpec
    end
    FCL-->>RUN: tupla di ShotSpec, oppure None se nessuna arma e adatta
```

Righe: `fire_control` locale `:838`; `_shooter_key` `:839`; `candidates` `:829` (cache `candidates_cache`); `target_key` `:849`; quote `:858-859` (solo se `is_air or bomber`, `bomber = not is_air and shooter_key[0] == 'Aircraft'`);
cache `:862-863`; `rank_weapons` `:865`; `_attack_speed_kmh` `:867` (solo se `release_altitude` è noto); `shot_spec_for` per ogni scelta `:868`; salvataggio in cache `:872`. Dentro `rank_weapons` (`:698`): `_surface_capable` solo per bersagli non
aerei, `_cell` per la riga di efficacia, scarto se Pk ≤ 0, `in_altitude_envelope` solo per bersagli aerei con `altitude_filter`, ordine per `preference_score` (col costo solo se **tutte** le armi adatte lo hanno, `use_cost`), poi Pk, nome del modello,
tipo d'arma. La risposta è la stessa per la stessa chiave `(shooter_key, keys, dimension, is_air, shooter_z, target_z)`: la memoizzazione non cambia il risultato (docstring). Il risolutore sceglie poi la prima opzione con scorta: v. **D13** e **D83**. Dalla BI `shot_spec_for` calcola anche `intercept_domains` con `intercept_domains_for` (`Fire_Control.py:799`, `:865`), che usa `munition_class` (`:761`) e legge `munition_class` e `ad_detectable` dal registro dell'arma: nessuna chiamata a `Weapon_Delivery` e nessun accesso nuovo al bersaglio. Le righe di questo paragrafo sono quelle di f009eb43 e non sono state ricalcolate dopo la BI.

### La sequenza dell'involucro di politica (D74)

*Diagramma D74 — `restrict_by_policy`: dalla costruzione della politica in `run_session` alla chiamata dentro il risolutore (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant SS as run_session
    participant MA as Mission_Adapter
    participant RP as restrict_by_policy
    participant ER as Engagement_Resolver
    participant RUN as _EngagementRun
    participant BASE as fire_control base
    participant WP as WeaponPolicy
    SS->>MA: weapon_policies(missions, assets_by_id)
    MA-->>SS: dict asset_id -> WeaponPolicy, con WeaponPolicy(mission_id, domain, rules, self_escort)
    opt F7_WEAPON_POLICY acceso e dict non vuoto
        SS->>RP: restrict_by_policy(fire_control, policies)
        RP->>ER: accepts_target_grounded(fire_control)
        RP-->>SS: restricted, con o senza il parametro target_grounded
    end
    SS->>ER: resolve_engagement(..., fire_control, ...)
    RUN->>RUN: _call_fire_control(shooter, target, time)
    opt bersaglio a terra, una sola volta per run
        RUN->>ER: accepts_target_grounded(self.fire_control)
    end
    RUN->>RP: restricted(shooter.asset, target.asset), con target_grounded=True se serve
    RP->>BASE: fire_control(shooter, target)
    BASE-->>RP: None, una ShotSpec o una sequenza
    RP->>RP: restrict(): policy_of.get(_asset_id(shooter))
    opt il tiratore ha una politica e la risposta non e vuota
        RP->>RP: target_class(target, grounded)
        loop per ogni opzione
            RP->>WP: allows(option.weapon, classe del bersaglio)
            WP->>WP: weapon_tasks(domain, weapon) che usa weapon_category
        end
    end
    RP-->>RUN: lo stesso oggetto se tutte tenute, altrimenti la tupla delle tenute oppure None
    RUN->>RUN: apply_target_rules se il tiratore ha TargetRules
```

Righe: `if F7_WEAPON_POLICY` `Logic/Session_Simulator.py:2273` (interruttore definito a `:894`, acceso), `weapon_policies` `:2274`, `restrict_by_policy` `:2277`; `accepts_target_grounded` in `restrict_by_policy` `:971`; `restricted` `:972`/`:978`;
`restrict` `:949` (politica cercata con `_asset_id` `:950`; `target_class` `:963`; `allows` `:964`); `_call_fire_control` `Logic/Engagement_Resolver.py:2691` (`accepts_target_grounded` `:2708`, una volta per run, memoizzato in
`fire_control_knows_grounded`; v. D43). Un tiratore **senza** politica, o una risposta `None`, riceve lo stesso oggetto della base (`restrict`, `:952-953`). Rimando a **D46** (la regola di `allows`), **D48** (il cablaggio F7a in `run_session`) e **D43** (le regole di bersaglio applicate dopo).

### La sequenza dell'arma per il fuoco su posizione (D75)

*Diagramma D75 — `area_fire_weapon` e `area_fire_pk`, chiamate da `Area_Fire.plan_shot` e `Area_Fire.resolve_area_fire` (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant AF as Area_Fire
    participant FW as area_fire_weapon
    participant CAN as _candidate_weapons
    participant SP as shot_spec_for
    participant PK as area_fire_pk
    participant TK as target_key
    AF->>FW: area_fire_weapon(shooter, distanza orizzontale, order.weapon, stock_of)
    FW->>FW: _shooter_key(shooter), esce se non e Vehicle o Ship
    FW->>CAN: _candidate_weapons(shooter_key)
    CAN-->>FW: armi candidate nell'ordine (tipo, modello)
    loop per ogni arma candidata
        FW->>FW: salta i missili, salta se weapon dichiarata e diversa, o senza task in AREA_FIRE_TASKS
        FW->>FW: salta se la distanza supera range_m
        FW->>SP: shot_spec_for(entry, 1.0, 1.0)
        SP-->>FW: ShotSpec con time_of_flight e stock_per_round
        FW->>FW: salta se stock_of(model) e inferiore a stock_per_round
    end
    FW-->>AF: AreaWeapon (model, caliber_mm, max_range_m, time_of_flight, stock_per_round, entry) oppure None
    AF->>AF: impact_time(order, weapon) e lethal_radius(weapon)
    loop per ogni nemico vivo e con posizione all'impatto
        AF->>PK: area_fire_pk(weapon, enemy, grounded)
        PK->>TK: target_key(target, grounded)
        PK->>PK: _cell(weapon.entry, keys, dimension)
        PK-->>AF: destroy_capacity, None se aereo in volo, non classificabile o Pk nulla
    end
```

Righe: `area_fire_weapon` `:1013` (`_shooter_key` `:1025`, `_candidate_weapons` `:1030`, `shot_spec_for(entry, 1.0, 1.0)` `:1043`, `AreaWeapon(...)` `:1052`); `area_fire_pk` `:1058` (`target_key` `:1062`, `_cell` `:1072`); chiamanti in
`Logic/Area_Fire.py`: `plan_shot` `:202` (chiama `FC.area_fire_weapon` `:213`), `resolve_area_fire` `:259` (`plan_shot`), `:272-273` (`impact_time`, `lethal_radius`), `:285` (`FC.area_fire_pk`). In sessione `plan_shot` è chiamata **due volte** per ordine:
senza `stock_of` per stimare l'istante d'impatto a monte (`Logic/Session_Simulator.py:2500`, v. D65), con `stock_of` al momento del tiro (`resolve_area_fire`). Questo diagramma mostra le sole parti di `Fire_Control`; la regola di tiro con le estrazioni è **D49** e la coda di sessione è **D50**.

### Tabella completa dei simboli di `Logic/Fire_Control`

Colonne «Tipo», «Simbolo», «Firma» e «Riga» da `inventario.py --tabella Logic/Fire_Control` (36 righe a `a389cadb`, nell'ordine del file); «Gruppo» come D72; «Chiamata da»: chiamanti dentro il modulo e nel core (`SS` = `Session_Simulator`, `MA` = `Mission_Adapter`, `AF` = `Area_Fire`); le funzioni locali di `make_registry_fire_control` e `restrict_by_policy` sono attribuite alla funzione che le contiene.

| Gruppo | Tipo | Simbolo | Firma | Riga | Che cosa fa | Chiamata da |
|---|---|---|---|---|---|---|
| armi candidate | classe | `_Weapon` | `_Weapon`; campi: __slots__ | `:376` | Arma candidata: dati del registro normalizzati in unità SI (`__slots__`, non dataclass). | `_candidate_weapons` |
| armi candidate | metodo | `_Weapon.__init__` | `__init__(self, model, weapon_type, domain, data)` | `:382` | Normalizza il record di registro in unità SI: `kind`, `range_m`, `air_range_m`, `speed_ms`, `fire_rate`, quote, `tasks`, `cost`. | `_candidate_weapons` (costruttore `_Weapon`) |
| armi candidate | metodo | `_Weapon.efficiency` | `efficiency(self)` | `:401` | Proprietà: la tabella `efficiency` del record (`{}` se assente). | `_cell` (lettura dell'attributo) |
| politica d'armi | classe | `WeaponPolicy` | `WeaponPolicy`; campi: mission_id, domain, rules, self_escort | `:990` | Politica d'armi di UN asset di missione (v. «Politica d'armi per tipo di missione»). | `MA:weapon_policies` |
| politica d'armi | metodo | `WeaponPolicy.__post_init__` | `__post_init__(self)` | `:1005` | Rende `rules` un mapping immutabile (`MappingProxyType`). | implicito alla costruzione della dataclass |
| politica d'armi | metodo | `WeaponPolicy.allows` | `allows(self, weapon, target_class_name)` | `:1008` | L'arma `weapon` (modello) è ammessa contro la classe `target_class_name`? | `restrict_by_policy` (funzione `restrict`) |
| fuoco su posizione | classe | `AreaWeapon` | `AreaWeapon`; campi: model, caliber_mm, max_range_m, time_of_flight, stock_per_round, entry | `:1122` | Arma scelta per il fuoco su posizione (F7b), con i campi che servono a `Logic/Area_Fire`. | `area_fire_weapon` (costruttore); letta da `AF:lethal_radius`, `AF:impact_time` |
| politica d'armi | funzione | `weapon_category` | `weapon_category(domain, model)` | `:338` | Categoria d'arma del registro del dominio (es. `MISSILES_AAM`) che contiene il modello, o None. | `weapon_tasks`, `SS:_winchester_weapons` |
| politica d'armi | funzione | `weapon_tasks` | `weapon_tasks(domain, model)` | `:359` | Task del modello nel registro del dominio (`frozenset`), None se il modello non è a registro. | `WeaponPolicy.allows` |
| armi candidate | funzione | `_number` | `_number(value)` | `:406` | Il valore come float se è un numero (non bool), altrimenti None. | `_Weapon.__init__`, `_cell`, `_positive`, `_range_m` |
| armi candidate | funzione | `_positive` | `_positive(value)` | `:412` | Il valore se è un numero > 0, altrimenti None. | `_Weapon.__init__`, `_air_range_m`, `_attack_speed_kmh`, `_speed_ms`, `area_fire_weapon` |
| armi candidate | funzione | `_range_m` | `_range_m(domain, data)` | `:417` | Portata massima [m]: Ground in metri (dict direct/indirect o numero), Ship e Air in km. | `_Weapon.__init__` |
| armi candidate | funzione | `_air_range_m` | `_air_range_m(domain, data, range_m)` | `:433` | Portata [m] contro bersagli aerei: per Ground il tiro diretto se dichiarato, altrimenti `range_m`. | `_Weapon.__init__` |
| armi candidate | funzione | `_speed_ms` | `_speed_ms(domain, weapon_type, data)` | `:448` | Velocità dell'arma/proietto [m/s], nelle unità di ogni registro (v. commenti costanti). | `_Weapon.__init__` |
| armi candidate | funzione | `_shooter_key` | `_shooter_key(shooter)` | `:467` | (classe, modello, loadout) del tiratore, o None se non ha un modello. | `area_fire_weapon`, `make_registry_fire_control` |
| armi candidate | funzione | `_candidate_weapons` | `_candidate_weapons(shooter_key)` | `:479` | Armi candidate di un tiratore, in ordine deterministico (tipo, modello). | `area_fire_weapon`, `make_registry_fire_control` |
| bersaglio | funzione | `air_target_class_of` | `air_target_class_of(target)` | `:547` | Classe di bersaglio aereo (`Context.AIR_TARGET_CLASSES`) di un `Aircraft` in volo. | `target_key` |
| bersaglio | funzione | `parked_target_class` | `parked_target_class(target)` | `:563` | Classe d'efficacia (di superficie) di un aereo a terra (F4c, v. «Aerei a terra»). | `target_key` |
| bersaglio | funzione | `target_key` | `target_key(target, grounded)` | `:576` | (chiavi di efficacia in ordine di ricerca, dimensione, è aereo) del bersaglio. | `area_fire_pk`, `make_registry_fire_control` |
| bersaglio | funzione | `target_class` | `target_class(target, grounded)` | `:614` | Classe del bersaglio per la politica d'armi (F7a, `Context.TARGET_CLASSES`). | `restrict_by_policy` |
| bersaglio | funzione | `_z` | `_z(asset)` | `:637` | Quota `position.z` dell'asset, None se non leggibile. | `make_registry_fire_control` |
| filtri, ordine, ShotSpec | funzione | `in_altitude_envelope` | `in_altitude_envelope(weapon, shooter_z, target_z)` | `:649` | True se il bersaglio aereo è nell'inviluppo di quota dell'arma (v. «Quota»). | `rank_weapons` |
| filtri, ordine, ShotSpec | funzione | `_surface_capable` | `_surface_capable(weapon)` | `:680` | Un'arma spara a superficie se ha almeno un task non puramente antiaereo (o nessun task). | `rank_weapons` |
| filtri, ordine, ShotSpec | funzione | `_cell` | `_cell(weapon, keys, dimension)` | `:685` | (accuracy, destroy_capacity) grezzi della prima chiave presente nel template. | `area_fire_pk`, `rank_weapons` |
| filtri, ordine, ShotSpec | funzione | `preference_score` | `preference_score(pk, cost, use_cost)` | `:707` | Punteggio di preferenza di un'arma (decisione A5, v. `WEAPON_COST_EXPONENT`). | `rank_weapons` |
| filtri, ordine, ShotSpec | funzione | `rank_weapons` | `rank_weapons(weapons, keys, dimension, is_air, shooter_z, target_z, altitude_filter)` | `:719` | Tutte le armi adatte, in ordine di preferenza: tuple (arma, accuracy, destroy_capacity). | `make_registry_fire_control`, `select_weapon` |
| filtri, ordine, ShotSpec | funzione | `select_weapon` | `select_weapon(weapons, keys, dimension, is_air, shooter_z, target_z, altitude_filter)` | `:758` | L'arma preferita fra quelle adatte (la prima di `rank_weapons`), o None. | nessun chiamante nel core (solo test) |
| filtri, ordine, ShotSpec | funzione | `munition_class` | `munition_class(weapon)` | `:766` | Classe di munizione dell'arma (BI): dichiarata nel registro (`MISSILES_ASM`) o derivata da categoria e task; `None` se non classificabile. | `intercept_domains_for` |
| filtri, ordine, ShotSpec | funzione | `intercept_domains_for` | `intercept_domains_for(weapon)` | `:804` | Domini di difesa aerea (`land`, `naval`) che possono considerare il colpo un bersaglio (BI): dalla classe e, per i navali, dal flag `ad_detectable`; `None` se la classe è ignota. | `shot_spec_for` |
| filtri, ordine, ShotSpec | funzione | `shot_spec_for` | `shot_spec_for(weapon, accuracy, destroy_capacity, is_air, release_altitude_m, attack_speed_kmh)` | `:824` | `ShotSpec` della scelta, con i campi derivati del docstring del modulo (dalla BI anche `intercept_domains`). | `area_fire_weapon`, `make_registry_fire_control` |
| filtri, ordine, ShotSpec | funzione | `_attack_speed_kmh` | `_attack_speed_kmh(shooter_key)` | `:885` | Velocità `attack` [km/h] del loadout assegnato a un aereo, None se non disponibile. | `make_registry_fire_control` |
| fabbrica | funzione | `make_registry_fire_control` | `make_registry_fire_control(altitude_filter, memoize)` | `:898` | Fabbrica della fire control `(shooter, target, target_grounded)`: tupla ordinata di `ShotSpec` o None; cache opzionali. | nessun chiamante nel core: la fire control è un argomento di `run_session` |
| politica d'armi | funzione | `restrict_by_policy` | `restrict_by_policy(fire_control, policy_of)` | `:1034` | Involucro puro: `fire_control` con le opzioni ristrette dalla politica d'armi del tiratore (F7a). | `SS:run_session` |
| fuoco su posizione | funzione | `area_fire_weapon` | `area_fire_weapon(shooter, distance_m, weapon, stock_of)` | `:1142` | L'arma con cui `shooter` spara una posizione a `distance_m` [m] in orizzontale (F7b), o None. | `AF:plan_shot` |
| fuoco su posizione | funzione | `area_fire_pk` | `area_fire_pk(weapon, target, grounded)` | `:1187` | `destroy_capacity` della riga del template per la classe del bersaglio, None se non classificabile, Pk nulla o aereo in volo. | `AF:resolve_area_fire` |
| politica d'armi | funzione | `_asset_id` | `_asset_id(asset)` | `:1209` | Id di dominio di un asset (`id`, poi `name`), copia del criterio di `ER._domain_id`. | `restrict_by_policy` |

## 10A.4 L2 e L3 — `Logic/Engagement_Resolver` (4569 righe, 146 simboli)

> **Aggiornamento 2026-11-13 (codice `a389cadb`).** Questa sezione era verificata a `f009eb43` (con la BI aggiunta il 2026-11-10). Da allora il risolutore ha guadagnato la **D-5**, la **VA** e la **FP** (capitolo 4 §4.35-§4.37): **la tabella dei simboli di fondo è rigenerata** (146 righe, `inventario.py --tabella`, righe di `a389cadb`, 17 simboli nuovi con «Che cosa fa» e «Chiamata da» scritti sul codice), **D82 è riscritto** (la sequenza finale di `_detect_direction`, con i passaggi),
> **D133 è nuovo** (`_detect_passes`), e i diagrammi D76, D77, D79 e D83 sono aggiornati nei nodi e nelle liste di metodi. **Nessuna costante FP esiste**: l'interruttore `FP_PER_PASS_DETECTION` è stato eliminato il 2026-11-13. **I `:riga` nel testo dei diagrammi non aggiornati** (D78, D80, D81, D84-D87 e le «Letture») **restano a `f009eb43`** e sono sfasati per il risolutore, da circa 300 a circa 700 righe secondo il punto del file: la tabella di fondo è la fonte delle righe di oggi.
> Didascalie «verificato a f009eb43» = sequenza e nomi non toccati da D-5/BI/VA/FP e letti a quel commit, **non riletti** per questo aggiornamento (salvo D79, D82, D83, D133, D76-D77, riletti sul codice a `a389cadb`).

Lo strato 2 risponde a **come finisce** un ingaggio: `resolve_engagement` (`:4294`) consuma le `ContactWindow` dello scheduler e restituisce un `EngagementResult` **senza mutare nessun asset**; `apply_engagement_result` (`:4488`) è il passo separato
che applica danni e consumi agli asset veri. Il modulo contiene **16 classi** (11 `dataclass(frozen=True)` di scambio, `_Shadow` con `__slots__`, tre `dataclass` interne `_Candidate`, `_ForceState`, `_PendingGroup`, e `_EngagementRun`),
**99 metodi** (84 di `_EngagementRun`) e **31 funzioni** di primo livello: 16 + 99 + 31 = 146 simboli, tutti nella tabella di fondo.

Costanti del modulo (non sono nella tabella dell'inventario), righe a `a389cadb`: parametri della legge di rilevamento `PD_AT_ACQUISITION_RANGE` `:549` e `PD_RANGE_EXPONENT` `:554`; fattori ambientali `NIGHT_DETECTION_FACTOR` `:567`, `ADVERSE_WEATHER_DETECTION_FACTOR` `:568`;
nebbia di guerra `UNSEEN_DETECTION_FACTOR` `:582`, `RECON_EFFICIENCY_FOG_RELIEF` `:583`; **i tre interruttori, tutti `False`**: `D5_DWELL_TIME` `:591`, `BI_AD_TARGET_RULE` `:597`, `VA_ENGAGEMENT_ALTITUDE_BAND` `:608` (**nessun interruttore FP**); `AD_DOMAINS` `:611` (`land`, `naval`);
soglie `OPERATIVE_HEALTH_FLOOR` `:615`, `FRACTION_EPS` `:619`, `BREAKPOINT_U_EPS` `:623`, `STATIONARY_EPS` `:624`, `ATTACK_POINT_TOLERANCE_M` `:648`; esiti di forza `HELD`/`DISENGAGED`/`DESTROYED` `:627-629`; motivi `TRIGGER_*` `:633-635` e `ACTIVITY_*` `:641-644`; livelli di ROE `ROE_*` `:652-657`; le keyword facoltative della fire control
`TARGET_GROUNDED_KEYWORD` `:1832` e `ALTITUDES_KEYWORD` `:1836`; i cinque tipi di evento della coda `_LAUNCH` 0, `_IMPACT` 1, `_RESOLVE` 2, `_DECIDE` 3, `_WAKE` 4 (`:659-667`, in questo ordine
a parità d'istante). **Stime dichiarate dal codice** (commento «STIMA DICHIARATA»): `PD_AT_ACQUISITION_RANGE`, `NIGHT_DETECTION_FACTOR`, `ADVERSE_WEATHER_DETECTION_FACTOR`, `UNSEEN_DETECTION_FACTOR`, `RECON_EFFICIENCY_FOG_RELIEF`; `PD_RANGE_EXPONENT` ha la forma dall'equazione radar
(commento sopra `:554`) ma la curva è una semplificazione monotona. **D-5, BI, VA e FP non introducono nessuna costante stimata nel risolutore**: la forma `min(1, permanenza / dwell)` è una scelta di progetto [S] senza costanti (capitolo 4 §4.36), e le tabelle di classe della BI stanno in `Fire_Control` (capitolo 4 §4.24, `AD_DETECTABLE_DEFAULT` è una stima [S]). Questo capitolo non le ricalibra.

I **tipi di scambio** (livello L2) hanno già due diagrammi che restano: **D4** (`ShotSpec`, `Detection`, `Salvo`, `SalvoResolution`, `ForceOutcome`, `AmmunitionEvent`, `InterceptionEvent`, `EngagementResult`, `ActivityEnd`, `ActivityCriteria`, capitolo 4 §4.13) e
**D47** (`TargetRules`, `WeaponPolicy`, `AreaWeapon`). Qui si aggiungono i **tipi interni** della run, che nessun diagramma mostrava (D76), le funzioni di modulo per ruolo (D77, D78) e i 72 metodi della run per ruolo (D79, D80).

### I tipi interni della run (D76)

*Diagramma D76 — i tipi interni di `Engagement_Resolver` e i campi principali della run; i nomi privati compaiono senza il trattino basso iniziale (livello L2, verificato a f009eb43).*

```mermaid
classDiagram
    class Shadow {
        <<_Shadow classe con __slots__>>
        +str id
        +object asset
        +str force_id
        +int health
        +dict stores
        +int anonymous
        +frozenset unmodelled
        +dict interceptor_weapons
        +int anonymous_interceptors
        +int ammunition
        +int interceptor_stock
        +bool operative
        +bool destroyed
        +available(weapon) int
        +has_stock() bool
        +consume(weapon, units) int
        +consume_interceptions(amount) list
    }
    class Candidate {
        <<_Candidate dataclass>>
        +float t_ready
        +str target_id
        +float t_end
        +bool exhausted
        +float t_cpa
        +float distance_cpa
        +float not_before
    }
    class ForceState {
        <<_ForceState dataclass>>
        +str force_id
        +str side
        +tuple committed
        +dict thresholds
        +list interceptors
        +str outcome
        +float time
        +tuple triggers
        +float max_shock
        +object force
        +bool air
        +float temper
        +float temper_z
        +float morale
        +float enemy_estimate
        +bool stationary
        +dict loss_shooters
        +float breakpoint
        +float force_ratio
        +float unanswered_fraction
        +dict fire
        +str block_id
    }
    class PendingGroup {
        <<_PendingGroup dataclass>>
        +float resolve_time
        +list salvos
    }
    class EngagementRun {
        <<_EngagementRun>>
        +list queue
        +int sequence
        +float now
        +bool usable
        +dict shadows
        +dict force_states
        +list force_order
        +dict candidates
        +dict domain_of
        +dict domain_interceptors
        +dict assigned
        +dict assigned_shot
        +dict in_flight
        +dict pending
        +dict launch_generation
        +set pending_decide
        +dict launchers_against
        +dict hostile_by_domain
        +dict seen_by
        +dict identified_by
        +dict rwr_class
        +dict activity_criteria
        +dict activity_end
        +dict target_rules
        +GroundedSchedule grounded
        +set broken_forces
        +object pass_rng
        +object dwell_time_for
        +dict own_passes_of
        +dict detection_times_of
        +bool ad_target_rule
        +bool altitude_band
    }
    class Salvo {
        <<tipo di scambio, D4>>
    }

    EngagementRun "1" *-- "many" Shadow : shadows
    EngagementRun "1" *-- "many" ForceState : force_states
    EngagementRun "1" *-- "many" Candidate : candidates per tiratore
    EngagementRun "1" *-- "many" PendingGroup : pending per forza
    EngagementRun "1" o-- "many" Salvo : in_flight
    PendingGroup "1" o-- "many" Salvo : salvos
    ForceState "1" o-- "many" Shadow : interceptors
```

Note a D76: `Shadow.ammunition`, `interceptor_stock`, `operative` e `destroyed` sono `@property` (`:1441`, `:1458`, `:1476`, `:1480`); `Shadow` espone `id` e `health` perché `Damage_Model.build_damage_event` la tratta come un asset (duck typing), e la sua contabilità delle scorte
è quella di `Asset/Weapon_Stores` (`WS`), la stessa dell'asset reale: per questo `apply_engagement_result` ritrova sull'asset i consumi che l'ombra ha concesso. `Candidate.exhausted` e `not_before` sono i due campi che `_schedule_next` modifica (candidato esaurito, o rimandato all'ingresso in portata,
D11). `ForceState.interceptors` è la lista `[(Shadow, canali)]` costruita da `_interceptors_of`; `EngagementRun.domain_interceptors` raccoglie quelle di tutte le forze di un dominio di coordinamento (D32, D33). La coda `queue` contiene tuple `(time, kind, key, sequence, payload)`
(`_push` `:2111`); `sequence` rompe i pareggi. **Dal 2026-11-13** il diagramma mostra anche i sei campi della D-5, della FP, della BI e della VA: `pass_rng` (stream separato dei passaggi, `None` ammesso solo senza direzioni a più passaggi), `dwell_time_for` (lettore del dwell, `None` = D-5 spenta), `own_passes_of` (passaggi `(start, end)` per coppia `(osservatore, bersaglio)`, per R-INT) e `detection_times_of` (istanti di rilevamento per coppia, costruito alla prima richiesta), `ad_target_rule` e `altitude_band` (gli interruttori BI e VA, letti una volta per run). **Omessi** dal diagramma (esistono in `__init__`, `:1942-2082` a `a389cadb`, più `ad_domain_cache`, `fire_control_knows_altitudes`): le cache `zone_cache`, `may_intercept_cache`, `in_time_cache`, `range_cache`, `air_range_cache`, `class_weights`, `surface_weights`, `profiles`; `legs`, `contacts`, `initial_health`, `destroyed_at`, `woken_by_destruction`,
`attack_pass`, `fire_control_knows_grounded`; le callable iniettate (`rng`, `breakpoint_rng`, `morale_for`, `enemy_estimate_for`, `reaction_profile_for`, `detection_factor`); le liste di esito (`detections`, `salvos`, `resolutions`, `damage_events`, `ammunition_events`, `interception_events`, `activity_ends`).

### Le funzioni di modulo per ruolo (D77)

*Diagramma D77 — i gruppi di funzioni e di tipi di modulo di `Engagement_Resolver` e chi li chiama (livello L2, verificato a f009eb43; aggiornato a `a389cadb` nei nodi P, G, CS e RUN per D-5, FP e VA).*

```mermaid
flowchart TD
    A["A - API pubblica<br/>resolve_engagement,<br/>apply_engagement_result,<br/>_call_with_weapon"]
    RUN["_EngagementRun<br/>84 metodi in 12 gruppi<br/>(D79, D80)"]
    T["T - tipi di scambio<br/>ShotSpec, Detection, Salvo, SalvoResolution,<br/>eventi, ActivityCriteria, ActivityEnd,<br/>TargetRules, ForceOutcome, EngagementResult"]
    B["B - regole di bersaglio pure<br/>_id_set, rules_defer, apply_target_rules"]
    P["P - probabilita di rilevamento, permanenza e passaggi<br/>_check_factor, _check_dwell, detection_probability,<br/>detection_radius, dwell_factor, registry_dwell_time,<br/>_join_passes, _detection_time_in_pass"]
    F["F - fabbriche del fattore (D78)<br/>weather_*, meteo_*, recon_*,<br/>combine_detection_factors"]
    G["G - ponti<br/>accepts_keyword, accepts_target_grounded,<br/>accepts_altitudes, engagement_intervals,<br/>engagement_intervals_without_legs"]
    S["S - stato di lavoro<br/>_Shadow, _Candidate, _ForceState,<br/>_PendingGroup, _domain_id, _can_disengage"]
    CS["Contact_Scheduler<br/>position_on_legs, range_intervals,<br/>altitude_intervals, intersect_intervals,<br/>closest_point_of_approach, clamp_legs,<br/>GroundedSchedule, TIME_EPS"]
    DM["Damage_Model<br/>build_damage_event, apply_damage_event"]
    FCM["Fire_Control<br/>restrict_by_policy"]
    ARP["Air_Route_Manager<br/>fuori dal core"]

    A --> RUN
    A --> S
    A --> DM
    RUN --> T
    RUN --> B
    RUN --> P
    RUN --> G
    RUN --> S
    RUN --> CS
    RUN --> DM
    RUN -.->|detection_factor iniettato| F
    T --> B
    F --> P
    G --> CS
    FCM --> G
    ARP --> P
```

Lettura: `RUN --> T` raccoglie le costruzioni di `Detection`, `Salvo`, `SalvoResolution`, `AmmunitionEvent`, `InterceptionEvent`, `ActivityEnd`, `ForceOutcome`, `EngagementResult`; `T --> B` è il solo legame fra tipi e funzioni pure (`TargetRules.__post_init__` chiama `_id_set`, `:836`);
`F --> P` è `_check_factor`; la freccia tratteggiata `RUN -.-> F` non è una chiamata alle fabbriche (nessuna funzione di `RUN` le chiama) ma alla callable che esse **restituiscono** e che il chiamante passa come `detection_factor`. `FCM --> G`: `Fire_Control` (`restrict_by_policy`, `:971`) chiama
`accepts_target_grounded`. `ARP --> P`: `Air_Route_Manager` importa localmente `detection_probability` (`Logic/Air_Route_Manager.py:1103`), un modulo **fuori dal core**: la legge di Pd del risolutore è riusata dal pianificatore di rotta come metrica (decisione D-5 citata nel suo docstring).

### Le fabbriche del fattore di rilevamento (D78)

*Diagramma D78 — le funzioni che costruiscono la callable `detection_factor(observer, target) -> float` e da quali dati dipendono (livello L2, verificato a f009eb43).*

```mermaid
flowchart TD
    DF["detection_factor(observer, target) -> float<br/>callable passata a resolve_engagement"]
    USE["_detect_direction<br/>self.detection_factor(...) poi _check_factor"]
    MET["meteo_detection_factor<br/>region_name, date, time"]
    WFN["weather_detection_factor_fn<br/>conditions"]
    WF["weather_detection_factor<br/>conditions"]
    REG["region_recon_detection_factor<br/>region, observer_side"]
    SRE["side_recon_efficiency<br/>region, side"]
    RUF["recon_unseen_factor<br/>efficiency, unseen, seen, relief"]
    RFN["recon_detection_factor_fn<br/>seen_block_ids, observer_side, ..."]
    COMB["combine_detection_factors<br/>fns: prodotto dei fattori"]
    MA2["Meteo_Analysis.get_meteo_conditions<br/>import locale"]
    TA["Tactical_Analysis.build_recon_cp_snapshot<br/>import locale"]

    DF --> USE
    MET --> WFN
    MET --> MA2
    WFN --> WF
    REG --> SRE
    REG --> RUF
    REG --> RFN
    REG --> TA
    MET -.->|restituisce| DF
    RFN -.->|restituisce| DF
    COMB -.->|restituisce| DF
```

Lettura: ogni fabbrica **restituisce** una callable con la firma `(observer, target) -> float`; `combine_detection_factors` ne fa il prodotto (ogni componente è riportato in [0, 1], `:1249`). `weather_detection_factor` (`:1105`) dà `NIGHT_DETECTION_FACTOR` per la notte e
`ADVERSE_WEATHER_DETECTION_FACTOR` per il meteo avverso, moltiplicati; `recon_detection_factor_fn` (`:1209`) dà `seen_factor` se il blocco del bersaglio è nell'istantanea di ricognizione dell'osservatore o è dello stesso lato, `unseen_factor` altrimenti, e 1.0 per un osservatore
dell'altro lato. Import locali: `Meteo_Analysis` `:1179`, `Region.BlockCategory` `:1337`, `Tactical_Analysis` e `enemySide` `:1384-1385`. **Nessuna di queste fabbriche ha un chiamante nel core**: `run_session` non le chiama (nessuna occorrenza in `Session_Simulator.py`), le usa chi prepara la sessione
(test e scenari: `Test/Test_Session_Scenarios.py:1334` usa `ER.region_recon_detection_factor`). Il docstring di `region_recon_detection_factor` (`:1359`) dichiara che l'istantanea è presa **una volta, prima della sessione**, e che `Block.get_recognition_report` estrae con il modulo `random` di Python
(`Utility.calcProbability`) *fuori* dal percorso del motore: non l'ho verificato in `Block`, lo riporto come dichiarazione del codice. Regola e formula: **D12** (capitolo 4 §4.18), che resta.

### I metodi di `_EngagementRun` per ruolo (D79, D80)

Gli **84 metodi** della run a `a389cadb` (più la classe, `:1939`) sono divisi in 12 gruppi di ruolo, con il codice `R1`-`R12` usato anche nella tabella di fondo. Conteggi: R1 costruzione 8; R2 rilevamento **13** (6 a f009eb43, più i sette della D-5 e della FP: `_exposure_time`, `_own_intervals`, `_dwell_of`, `_own_passes`, `_pass_cpa`, `_pass_detection_time`, `_detect_passes`); R3 coda ed esito 5; R4 scelta del tiro **11** (8, più i tre della VA: `_band_of`, `_altitudes_at`, `_altitude_deferral`); R5 dottrina di tiro 6;
R6 lanciatori L2/L3 4; R7 regole di bersaglio F7a 11; R8 lancio e impatto 2; R9 intercettazione 9 (7 a f009eb43, più `_ad_domain` e `_admissible` della BI); R10 risoluzione della salva 1; R11 disingaggio e rottura 10; R12 fine di attività 4 (totale 84: 72 a f009eb43, più 2 della BI, 7 di D-5/FP e 3 della VA). Le frecce sono chiamate a nome di metodo (`self._x(...)`) fra gruppi;
i gruppi che accodano un evento chiamano tutti `_push` (R3): quegli archi non sono disegnati. Il raggruppamento è mio (i metodi non sono raggruppati nel codice), ma segue le intestazioni di sezione del file («fase 1: rilevamento», «coda eventi», «fase 2: scelta del bersaglio e lancio»,
«dottrina di tiro», «fase 3: impatto, saturazione, danno», «fase 4: disingaggio», «soglia di rottura stocastica»).

*Diagramma D79 — `_EngagementRun` 1/2: costruzione, rilevamento, ciclo principale, scelta del tiro, dottrina di tiro, prelazione ai lanciatori, lancio e impatto (livello L2, verificato a f009eb43; nodi R2 e R4 aggiornati a `a389cadb`).*

```mermaid
flowchart TD
    RE["resolve_engagement<br/>funzione di modulo"]
    R1["R1 costruzione<br/>__init__, _build_forces, _build_domains,<br/>_shadow_of, _interceptors_of,<br/>_profile, _same_domain, _init_breakpoints"]
    R2["R2 rilevamento<br/>_detect, _detect_direction, _detect_passes, _detection_time,<br/>_pass_detection_time, _pass_cpa, _own_passes, _own_intervals,<br/>_dwell_of, _exposure_time, _perceive, _perceive_rwr, _grounded_in"]
    R3["R3 coda ed esito<br/>run, _push, _draw, _touch, _result"]
    R4["R4 scelta del tiro<br/>_schedule_next, _fire_control,<br/>_call_fire_control, _first_with_stock, _options,<br/>_range_entry, _band_of, _altitudes_at, _altitude_deferral,<br/>_refire_interval, _gone"]
    R5["R5 dottrina di tiro<br/>_blocked, _coverage, _force_shots_on,<br/>_rounds_in_flight, _engaged_shooters, _wait"]
    R6["R6 lanciatori L2-L3<br/>_register_launcher, _is_launcher_against,<br/>_in_range_at, _on_decide"]
    R8["R8 lancio e impatto<br/>_on_launch, _on_impact"]
    S["S stato di lavoro<br/>_Shadow, _ForceState,<br/>_Candidate, _PendingGroup"]

    RE --> R1
    RE --> R3
    R1 --> S
    R3 --> R2
    R3 --> R4
    R3 --> R6
    R3 --> R8
    R2 --> R1
    R2 --> S
    R4 --> R5
    R4 --> R6
    R6 --> R4
    R8 --> R4
    R8 --> R6
```

Lettura: `R3 --> R4` è la prima `_schedule_next` per ogni tiratore in `run` (`:3566-3567`); `R3 --> R6` è `_on_decide` (evento `_DECIDE`); `R6 --> R4` è doppia: `_on_decide` richiama `_schedule_next`, `_in_range_at` richiama `_fire_control`, `_first_with_stock` e `_range_entry` per sapere se
un lanciatore è ingaggiabile; `R8 --> R4` è `_on_launch` che richiama `_schedule_next` (`:2919`, `:2930`, `:2955`) e `_gone` (`:2913`). `R2 --> R1` è `_profile` (il tempo di reazione del tiratore). Le sequenze interne a questi gruppi sono D81-D84; i diagrammi di regola sono D5 (coda), D25 (prelazione), D26 (dottrina di tiro).

*Diagramma D80 — `_EngagementRun` 2/2: risoluzione della salva, intercettazione, disingaggio, fine di attività e regole di bersaglio F7a (livello L2, verificato a f009eb43).*

```mermaid
flowchart TD
    R3["R3 dispatch<br/>run"]
    R10["R10 risoluzione<br/>_on_resolve"]
    R9["R9 intercettazione<br/>_admissible, _ad_domain, _may_intercept, _in_time, _interception_zone,<br/>_round_track_time, _air_detection_range,<br/>_detection_time_of, _position_at"]
    R11["R11 disingaggio e rottura<br/>_check_doctrine, _breakpoint, _perceived_ratio,<br/>_air_threat, _surface_weight, _unanswered_fraction,<br/>_morale_of, _enemy_estimate_of, _stationary, _is_enemy"]
    R12["R12 fine di attivita<br/>_check_activity, _end_activity,<br/>_activity_end_time, _targets_destroyed_at"]
    R7["R7 regole di bersaglio F7a<br/>_is_deferred, _is_designated, _is_hostile,<br/>_attack_over, _attack_pass_time, _designated_destroyed,<br/>_designated_first, _react_to_hostile,<br/>_schedule_phase_wakes, _wake_after_destruction, _on_wake"]
    R8["R8 lancio e impatto<br/>_on_launch, _on_impact"]
    R4["R4 scelta del tiro<br/>_schedule_next, _fire_control"]
    R1["R1 costruzione<br/>_init_breakpoints"]
    DM["Damage_Model<br/>build_damage_event"]
    DOC["Doctrine e Air_Defense_Efficacy"]

    R3 --> R10
    R3 --> R7
    R10 --> R9
    R10 --> R11
    R10 --> R12
    R10 --> R7
    R10 --> DM
    R11 --> DOC
    R8 --> R12
    R8 --> R7
    R4 --> R7
    R7 --> R4
    R7 --> R9
    R1 --> R11
```

Lettura: `R10 --> R9` sono `_admissible` (filtro BI, che a sua volta usa `_ad_domain`; solo con `BI_AD_TARGET_RULE` acceso, altrimenti risponde sempre «ammesso»), `_may_intercept` (regola L1) e `_in_time` (regola R-INT) chiamate per ogni coppia (salva, intercettore); `R10 --> R11` è `_check_doctrine`, che chiama `_breakpoint` → `_perceived_ratio` e `_unanswered_fraction`; `R10 --> R7` è
`_wake_after_destruction` (solo con `target_rules`); `R10 --> R12` è `_check_activity` (solo con `activity_criteria`); `R7 --> R9` è `_position_at` usato da `_is_designated`; `R1 --> R11` sono le chiamate di `_init_breakpoints` a `_morale_of`, `_enemy_estimate_of`, `_stationary`
(il gruppo R1 contiene `_init_breakpoints` per costruzione, ma la sua logica è del gruppo R11). `R4 --> R7` e `R7 --> R4`: `_schedule_next` e `_fire_control` consultano `_is_deferred`, `_is_designated`, `_is_hostile`, `_attack_over`; `_on_wake` richiama `_schedule_next`.
Rimando a **D22** (soglia di rottura B(t)), **D23** (peso di un nemico percepito), **D24** (allocazione delle intercettazioni), **D27** (regola R-INT), **D37** (fine di attività), **D43-D45** (regole di bersaglio di missione).

### La sequenza di `resolve_engagement` (D81)

*Diagramma D81 — `resolve_engagement`: validazione degli argomenti, costruzione della run e ciclo principale; le sequenze interne a ogni gestore di evento sono D82-D85 (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant SS as Session_Simulator
    participant RE as resolve_engagement
    participant RUN as _EngagementRun
    participant DOC as Doctrine
    participant GS as GroundedSchedule
    SS->>RE: resolve_engagement(force_a, force_b, contacts, fire_control, rng, extra_forces, legs, ...)
    RE->>RE: controlla rng.random, fire_control chiamabile, salvo_window, provenance
    RE->>RE: controlla breakpoint_rng, morale_for, enemy_estimate_for
    RE->>RE: controlla che activity_criteria e target_rules siano mappe di ActivityCriteria e di TargetRules
    RE->>RUN: _EngagementRun((force_a, force_b) + extra_forces, contacts, fire_control, rng, ...)
    RUN->>GS: GroundedSchedule.of(grounded)
    RUN->>RUN: _build_forces(forces, committed, thresholds)
    loop per ogni forza nell ordine di ingresso
        RUN->>RUN: _shadow_of(asset_id, asset, force_id, health) per ogni asset operativo e impegnato
        RUN->>DOC: get_disengagement_thresholds(side, thresholds), se la forza puo disingaggiarsi
        RUN->>DOC: get_fire_doctrine(side, fire_doctrine)
        RUN->>RUN: _interceptors_of(force, force_id)
    end
    RUN->>RUN: _build_domains(coordination_of)
    opt run.usable
        RUN->>RUN: _init_breakpoints(), estrazione dal solo breakpoint_rng
        opt activity_criteria non vuoto
            RUN->>RUN: initial_health, poi _check_activity(meno infinito, targets_only=True)
        end
    end
    RUN-->>RE: run
    opt non run.usable
        RE-->>SS: None
    end
    RE->>RUN: run.run()
    RUN->>RUN: _detect(), una _detect_direction per direzione (D82)
    loop per ogni tiratore con candidati, in ordine di id
        RUN->>RUN: _schedule_next(shooter_id, meno infinito) (D83)
    end
    RUN->>RUN: _schedule_phase_wakes()
    loop finche la coda non e vuota
        RUN->>RUN: heappop, poi self.now = time
        alt kind e _LAUNCH
            RUN->>RUN: _on_launch(time, key, payload) (D84)
        else kind e _IMPACT
            RUN->>RUN: _on_impact(time, key, payload) (D5)
        else kind e _RESOLVE
            RUN->>RUN: _on_resolve(time, key) (D85)
        else kind e _DECIDE
            RUN->>RUN: _on_decide(time, key, payload) (D25)
        else kind e _WAKE
            RUN->>RUN: _on_wake(time, key) (D45)
        end
    end
    RUN->>RUN: _result()
    RUN-->>RE: EngagementResult
    RE-->>SS: EngagementResult
```

Lettura: le validazioni sono tutte in testa e prima di costruire la run (`:3728-3766`); sollevano `TypeError`/`ValueError` e non toccano nessuna forza. La run si costruisce in `:3768-3774` e il suo `__init__` (`:1645`) fa, in questo ordine: copia dei parametri
e creazione degli stati vuoti (`:1650-1750`), `GroundedSchedule.of(grounded)` (`:1669`), `_build_forces` (`:1752`), `_build_domains` (`:1753`); solo se la run è risolvibile, `_init_breakpoints` (`:1756`) e, con criteri di fine attività, `initial_health` e `_check_activity(float('-inf'), targets_only=True)`
(`:1758-1767`). `_build_forces` (`:1771`) scorre le forze nell'ordine dato e gli asset **ordinati per id** (`:1786`); salta l'asset senza id di dominio (`:1789`), non incluso in `committed` (`:1793`), senza salute intera leggibile (`:1799-1803`), non operativo (`:1805-1811`);
crea l'ombra (`:1813`) e lo stato di forza con `thresholds=None` per blocchi non militari (`_can_disengage`, `:1818`) e per forze di soli aerei sempre a terra (`:1823`), altrimenti con la dottrina del lato (`:1830`); chiama `_interceptors_of` (`:1841`) dopo aver creato le ombre **di quella forza**.
Restituisce `False` (e `resolve_engagement` `None`, `:3776-3777`) se meno di due forze hanno asset impegnabili (`:1850-1853`); con 3 o più forze una forza vuota resta nell'esito con `committed=0` (`:1858-1860`). Due forze con lo stesso id o un asset in due forze sono `ValueError` (`:1776`, `:1797`);
una mappa `coordination_of` mal formata o un dominio a cavallo di due lati lo sono in `_build_domains` (`:1875`, `:1890`).

Il ciclo principale è `run` (`:3563-3586`): `_detect`, poi una `_schedule_next` per ogni tiratore **in ordine di id** (`:3566-3567`), poi `_schedule_phase_wakes`, poi lo svuotamento della coda con il dispatch per tipo (`:3575-3584`). L'ordine degli eventi a pari istante è quello dei tipi
(`_LAUNCH` 0 < `_IMPACT` 1 < `_RESOLVE` 2 < `_DECIDE` 3 < `_WAKE` 4, `:536-544`), poi la chiave, poi `sequence`. **Ordine delle estrazioni** (fatto che il codice rende verificabile): il `breakpoint_rng` è consultato una volta per forza **in costruzione** (`:3384`), prima di tutto il resto; l'`rng` di sessione
è consultato solo da `_draw` (`:2115`), cioè una volta per direzione in `_detect_direction` (`:2001`) e una volta per ogni colpo non fermato su un bersaglio non ancora distrutto in `_on_resolve` (`:3254`). Rimando a **D5** (la coda nella sua forma generale), **D25** (prelazione), **D45** (`_WAKE`).

### La sequenza di `_detect_direction` (D82, riscritto) e di `_detect_passes` (D133)

*Diagramma D82 — `_detect_direction`: dal calcolo dei passaggi nel volume proprio all'estrazione, fino al candidato e alla percezione; con due o più passaggi delega a `_detect_passes` (D133) (livello L3, riscritto e verificato a `a389cadb`: sostituisce la versione a «una estrazione per direzione» verificata a f009eb43, anteriore a D-5 e FP).*

```mermaid
sequenceDiagram
    participant DET as _detect
    participant DD as _detect_direction
    participant GS as GroundedSchedule
    participant DF as detection_factor
    participant OP as _dwell_of e _own_passes
    participant CS as Contact_Scheduler
    participant DPS as _detect_passes
    participant EX as _exposure_time
    participant PD as detection_probability / detection_radius / dwell_factor
    participant DT as _detection_time
    participant ADE as Air_Defense_Efficacy
    DET->>DD: _detect_direction(window, osservatore, bersaglio, own_range, other_range)
    opt own_range assente o non positiva
        DD-->>DET: esce senza estrazione
    end
    DD->>GS: _grounded_in(observer.id, window), stato al punto medio della finestra
    opt osservatore a terra
        DD-->>DET: esce senza estrazione
    end
    opt detection_factor iniettato
        DD->>DF: detection_factor(observer.asset, target.asset)
        DD->>DD: _check_factor(valore), fuori da 0 e 1 e errore
    end
    DD->>OP: _dwell_of(window, observer, target), None senza dwell_time_for o senza dato
    DD->>OP: _own_passes(window, observer.id, target.id, own_range, dwell)
    OP->>CS: _own_intervals, poi range_intervals(legs_observer, legs_target, own_range)
    OP->>OP: _join_passes(intervalli, dwell), uniti se l uscita non supera il dwell
    OP-->>DD: lista (lo, hi, start, end), oppure None senza i tratti di entrambi
    alt passes non e None
        DD->>DD: own_passes_of della coppia, esteso con (start, end), per R-INT
        alt almeno due passaggi
            DD->>DPS: _detect_passes(window, observer, target, own_range, factor, dwell, passes) (D133)
            DPS-->>DD: una estrazione e una Detection per passaggio
            DD-->>DET: esce
        else nessun passaggio
            DD->>DD: pass_exposure = 0.0
        else un solo passaggio
            DD->>DD: pass_exposure = min(end, t_end) - start
            DD->>DD: FP-3 a, candidate_end = hi se la portata propria e la minore
        end
    end
    opt dwell non None
        opt passes e None, ripiego senza tratti
            DD->>EX: _exposure_time(window, own_range, other_range)
        end
        DD->>PD: factor = factor x dwell_factor(permanenza, dwell)
    end
    DD->>DD: _draw(), una sola estrazione dallo stream rng
    DD->>DD: distance = max(distance_cpa della finestra, 0)
    opt distance non oltre own_range
        DD->>PD: detection_probability(distance, own_range, factor)
    end
    Note over DD: detected = draw minore della probabilita, altrimenti probabilita 0
    opt detected
        DD->>PD: detection_radius(draw, own_range, factor)
        DD->>DT: _detection_time(window, observer.id, target.id, own_range, other_range, radius)
        DT-->>DD: istante del rilevamento
        DD->>DD: _perceive(observer.force_id, target.id, time)
        DD->>DD: identified_by del dominio, minimo fra i tempi
        opt bersaglio non a terra
            DD->>ADE: rwr_perception(target.asset, observer.asset)
        end
        opt risposta PERCEIVED_AT_DETECTION
            DD->>DD: _perceive_rwr(target, observer, time), poi ADE.rwr_class_of
        end
        DD->>DD: t_ready = time + _profile(observer.id).total
        opt t_ready non oltre candidate_end piu TIME_EPS
            DD->>DD: candidates[observer.id].append(_Candidate(t_end = candidate_end))
        end
    end
    DD->>DD: detections.append(Detection(...)), anche se non rilevato
```

Lettura: `_detect` (`:2280`) ordina le finestre per `(t_start, asset_a_id, asset_b_id, t_end)` (`:2281-2282`), scarta quelle con un asset non impegnato o con i due asset della stessa forza (`:2288-2294`) e per ognuna chiama `_detect_direction` **due volte**: prima A osserva B con `range_a`, poi B osserva A con `range_b`
(`:2298-2299`). **Le uscite senza estrazione sono due** (`:2303-2310`): portata assente o non positiva, e osservatore a terra (sensori spenti); **un terzo caso è un errore**: con almeno due passaggi e `pass_rng` mancante `_detect_passes` solleva `ValueError` **prima di ogni estrazione** (`:2560-2562`). Ogni altro caso consuma **una estrazione per passaggio** se i passaggi sono due o più (D133), **esattamente una** altrimenti,
anche quando la distanza minima supera la portata (la probabilità è allora 0.0, `:2356`).
**Tre casi dopo `_own_passes`** (`:2325`): `None` (nessun tratto: il **ripiego senza tratti**, la sola strada in cui `_exposure_time` è chiamata, `:2351`); lista vuota (permanenza D-5 0, `:2337`); un passaggio (permanenza del passaggio, `:2342`; FP-3 (a) con `candidate_end = hi`, `:2344-2348`). La stessa estrazione decide se e quando: `detection_radius` ne ricava il raggio (`:2361`) e `_detection_time` (`:2434`) il primo istante
in cui la distanza scende sotto quel raggio, con `Contact_Scheduler.range_intervals` se ci sono i tratti di rotta di entrambi, altrimenti l'istante geometrico di ingresso in portata o `t_cpa`. Il candidato nasce solo se il tiratore è pronto entro `candidate_end` (`:2376-2379`: la fine della finestra, o la fine del passaggio con FP-3 (a)); il `Detection` è registrato sempre (`:2381-2384`, senza `pass_index`). L'RWR del bersaglio è consultato solo se il bersaglio non è a terra
(`:2370-2372`). **Nessuna costante, nessun interruttore FP**: dalla pulizia del 2026-11-13 il ramo `if self.pass_rng is not None` non esiste più, e i passaggi si calcolano sempre quando ci sono i tratti. La formula della Pd e la regola del dominio di coordinamento sono in **D12** e **D23**; la percezione che ne deriva è usata da `_perceived_ratio` (D22); la regola in forma di flusso è **D131** (capitolo 4 §4.35).

*Diagramma D133 — `_detect_passes`: un'estrazione per passaggio, con la permanenza D-5, il CPA del passaggio e il candidato fino alla fine del passaggio (livello L3, verificato a `a389cadb`).*

```mermaid
sequenceDiagram
    participant DD as _detect_direction
    participant DPS as _detect_passes
    participant RNG as rng e pass_rng
    participant PC as _pass_cpa
    participant CS as Contact_Scheduler
    participant PD as detection_probability / detection_radius / dwell_factor
    participant PT as _pass_detection_time
    DD->>DPS: _detect_passes(window, observer, target, own_range, factor, dwell, passes)
    opt pass_rng is None
        DPS-->>DD: ValueError, prima di ogni estrazione
    end
    loop per ogni passaggio (lo, hi, start, end), indice 0, 1, ...
        opt dwell non None
            DPS->>PD: exposure = max(0, min(end, t_end) - start), poi factor x dwell_factor(exposure, dwell)
        end
        alt indice 0
            DPS->>RNG: _draw(), dallo stream rng dell ingaggio
        else dal secondo passaggio
            DPS->>RNG: _draw(self.pass_rng), dallo stream separato dei passaggi
        end
        DPS->>PC: _pass_cpa(window, observer.id, target.id, lo, hi)
        PC->>CS: clamp_legs e closest_point_of_approach, sui tratti ritagliati a [lo, hi]
        PC-->>DPS: (t_cpa, distanza del passaggio)
        DPS->>PD: detection_probability(distanza, own_range, pass_factor), 0 se oltre la portata
        opt detected
            DPS->>PD: detection_radius(draw, own_range, pass_factor)
            DPS->>PT: _pass_detection_time(observer.id, target.id, own_range, lo, hi, radius, t_cpa)
            DPS->>DPS: _perceive, identified_by, RWR come in _detect_direction
            opt t_ready non oltre hi piu TIME_EPS
                DPS->>DPS: candidates.append(_Candidate(t_end = hi, t_cpa e distance_cpa del passaggio))
            end
        end
        DPS->>DPS: detections.append(Detection con pass_index, pass_count, pass_start = lo, pass_end = hi)
    end
```

Lettura: `_detect_passes` (`:2550-2604`) è chiamata **solo** da `_detect_direction` con almeno due passaggi (`:2332-2334`); per due passaggi la direzione ha **due** estrazioni, la prima da `self.rng` e la seconda da `self.pass_rng` (`:2575`), nell'ordine di tempo dei passaggi. **Ordine delle estrazioni** (parte del contratto, capitolo 4 §4.11): lo stream `rng` consuma una sola estrazione per direzione, nella posizione di sempre, qualunque sia il numero di passaggi; `pass_rng` consuma una estrazione per ogni passaggio dal secondo. La permanenza D-5 è quella del **proprio** passaggio
(`:2569-2573`, non tagliata all'inizio della finestra, mai la somma); il candidato vale fino a `hi`, la fine del passaggio ritagliata alla finestra (`:2594-2598`, FP-3 (a)), con CPA e distanza **del passaggio** (FP-4, `_pass_cpa`, `:2528`); le salve già lanciate non cambiano. `_pass_detection_time` (`:2540`) cerca il primo istante **dentro il passaggio** in cui la distanza scende sotto il raggio estratto (`_own_intervals(..., radius)`), con ripiego il CPA del passaggio.
Rimando a **D131** (flusso di `_detect_direction`), **D134** (regola R-INT con i passaggi, che consuma `own_passes_of`) e a capitolo 4 §4.35.

### La sequenza di `_schedule_next` (D83)

*Diagramma D83 — `_schedule_next`: l'ordine delle chiamate con cui un tiratore sceglie bersaglio, arma e istante del prossimo lancio (livello L3, verificato a f009eb43; aggiornato a `a389cadb` con il rinvio di quota e la fascia della VA).*

```mermaid
sequenceDiagram
    participant CH as run, _on_launch, _on_decide, _on_wake
    participant SN as _schedule_next
    participant DOT as _blocked e _wait
    participant FCT as _fire_control
    participant EXT as fire_control iniettata
    participant ALT as _altitude_deferral
    participant RNG as _range_entry
    participant Q as coda eventi
    CH->>SN: _schedule_next(shooter_id, t_earliest)
    opt forza rotta, aereo sempre a terra, non operativo o senza scorta
        SN-->>CH: esce
    end
    SN->>SN: _activity_end_time(shooter_id), esce se t_earliest raggiunge la fine
    loop finche non si assegna un lancio
        loop per ogni candidato non esaurito
            SN->>SN: bersaglio non operativo o _gone(target), il candidato diventa exhausted
            SN->>SN: t_fire = max(t_ready, t_earliest, not_before), exhausted se oltre t_end
            SN->>SN: scarta il candidato se t_fire e dopo la fine di attivita o il tiratore e a terra
            opt target_rules non vuoto
                SN->>SN: _is_deferred(shooter, target, t_fire), il candidato resta ma fuori scelta
            end
        end
        opt nessun candidato viabile
            SN-->>CH: esce
        end
        SN->>SN: priority = viabili con _is_launcher_against e _in_range_at
        SN->>SN: pool = priority, altrimenti _designated_first, altrimenti viable
        SN->>DOT: _blocked(shooter, target_id, bool(priority)) per ogni elemento del pool
        opt open_pool vuoto
            SN->>DOT: _wait(shooter, pool, t_earliest)
            DOT->>Q: _push(DECIDE) al primo impatto previsto
            DOT-->>SN: True, e _schedule_next esce
        end
        SN->>SN: primo istante utile t_first, poi _engaged_shooters per ogni candidato e chiave minima
        SN->>FCT: _fire_control(shooter, target, t_fire)
        FCT->>EXT: _call_fire_control, con target_grounded=True se a terra e altitudes se VA acceso e la fire control le dichiara
        EXT-->>FCT: None, una ShotSpec o una sequenza
        FCT->>FCT: apply_target_rules(...) se il tiratore ha TargetRules
        FCT-->>SN: risposta ristretta
        SN->>SN: _first_with_stock(shooter, risposta), (spec, colpi) o None
        opt choice e None
            SN->>ALT: _altitude_deferral(shooter, candidato, t_fire), solo con VA acceso (D132)
            ALT-->>SN: un istante successivo imposta not_before e il ciclo riparte, oppure l opzione al bordo della fascia, oppure nulla
        end
        opt choice ancora None
            SN->>SN: candidato exhausted, il ciclo riparte
        end
        opt spec.max_range definita
            SN->>RNG: _range_entry(shooter_id, candidato, max_range, t_fire, band = _band_of(spec))
            RNG-->>SN: None esaurisce, un istante successivo imposta not_before e il ciclo riparte
        end
        SN->>SN: assigned[shooter_id] e assigned_shot[shooter_id]
        SN->>Q: _push(t_fire, LAUNCH, shooter_id, (index, spec, rounds, generation))
    end
```

Lettura (righe a `a389cadb`): i controlli iniziali sono `:2793-2805`; il ciclo `while True` (`:2809`) si ripete finché una scelta non è accodata o non resta nulla (`return` a `:2851`, `:2868`, `:2925`); ricomincia (`continue`) quando un candidato viene esaurito o rimandato (`:2895`, `:2901`, `:2916`, `:2920`). **Valutazione pigra** (`:2856-2863`): `_designated_first` è chiamata
solo se `priority` è vuota (`priority or self._designated_first(...) or viable`); `_in_range_at` (`:3253`) è chiamata solo per i candidati che sono già lanciatori contro la forza (corto circuito di `and`) e a sua volta passa da `_fire_control`, `_first_with_stock`, **`_altitude_deferral`** (un rinvio non è «a portata adesso») e `_range_entry` **senza** modificare il candidato. `_blocked` usa `_rounds_in_flight` per il tetto «due missili, poi guarda» e `_coverage`
(che itera `_force_shots_on`) per la saturazione; i lanciatori prioritari sono esenti dalla saturazione, non dal tetto. Se `_wait` ritorna `False` (nessun impatto da attendere, `:2867`) il pool **resta quello non filtrato** e il tiratore procede. Il filtro «primo istante utile» (`:2873-2878`) non vale per i lanciatori prioritari (`not priority`). `_fire_control` (`:3182`) applica `apply_target_rules` solo se il tiratore ha regole;
`_call_fire_control` (`:3197-3247`) passa `target_grounded=True` solo se il bersaglio è a terra all'istante `time` e la fire control lo accetta, e `altitudes` solo con VA acceso, i tratti e una fire control che la dichiara (`_altitudes_at`, `:3429`). **Dalla VA**: dopo `_first_with_stock` senza opzioni (`:2887-2891`), `_altitude_deferral` (`:3460-3510`) può rinviare la decisione (`not_before`, `:2893-2895`) o restituire l'opzione al bordo della fascia;
il controllo di portata passa la `band` della `ShotSpec` (`:2911-2912`). Il payload accodato `(index, spec, rounds, generation)` (`:2924`) è congelato: `_on_launch` non richiama la fire control (D84). Rimando alle regole: **D11** (`not_before`), **D13** (opzioni con scorta), **D25** (prelazione), **D26** (dottrina di tiro), **D43** e **D44** (regole di bersaglio), **D132** (fascia di quota).

### La sequenza di `_on_launch` (D84)

*Diagramma D84 — `_on_launch`: dal lancio programmato alla salva in volo, con le uscite anticipate, i consumi e le reazioni al lancio (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant RUN as run
    participant OL as _on_launch
    participant SH as _Shadow del tiratore
    participant SN as _schedule_next
    participant Q as coda eventi
    participant RL as _register_launcher e _react_to_hostile
    RUN->>OL: _on_launch(time, shooter_id, payload), payload = (index, spec, rounds, generation)
    opt generation diversa da launch_generation
        OL-->>RUN: esce, lancio annullato dalla prelazione o dalla fine di attivita
    end
    OL->>OL: assigned.pop(shooter_id)
    opt forza rotta, tiratore non operativo o dopo la fine di attivita
        OL-->>RUN: esce, nessun nuovo lancio
    end
    OL->>OL: candidate = candidates[shooter_id][index], next_time = time + _refire_interval(shooter_id, spec)
    alt bersaglio non operativo, _gone o time oltre candidate.t_end
        OL->>OL: candidate.exhausted = True
        OL->>SN: _schedule_next(shooter_id, next_time)
    else scorta dell arma inferiore a rounds per stock_per_round
        OL->>SN: _schedule_next(shooter_id, next_time)
    else il lancio parte
        OL->>SH: consume(spec.weapon, units)
        OL->>OL: ammunition_events.append(AmmunitionEvent(...))
        OL->>OL: Salvo(...) in salvos e in_flight
        OL->>OL: hostile_by_domain del dominio del bersaglio, newly_hostile
        OL->>OL: _touch(time)
        OL->>Q: _push(t_impact, IMPACT, target.force_id, salvo)
        opt activity_criteria non vuoto
            OL->>OL: _check_activity(time)
        end
        OL->>SN: _schedule_next(shooter_id, next_time)
        opt bersaglio non a terra e rwr_perception uguale a PERCEIVED_AT_LAUNCH
            OL->>OL: _perceive_rwr(target, shooter, time)
        end
        opt tiratore Aircraft e bersaglio non Aircraft oppure a terra
            OL->>RL: _register_launcher(time, shooter, target.force_id)
        end
        opt newly_hostile e target_rules non vuoto
            OL->>RL: _react_to_hostile(time, shooter, target.force_id)
        end
    end
```

Lettura: nel codice i tre rami della `alt` sono `return` successivi (`:2909-2931`); la `alt` li mostra come alternative per leggibilità. Le uscite senza alcun effetto sono quattro, nell'ordine `:2882` (generazione), `:2893` (forza rotta), `:2898` (non operativo), `:2904` (fine di attività); `assigned.pop` (`:2889`) precede le ultime tre, quindi un lancio
che esce lì non copre più nulla. `_refire_interval` (`:2911`) è calcolato **prima** dei controlli sul bersaglio e sulla scorta, perché serve ai due rami che riprogrammano. `units = rounds * spec.stock_per_round` (`:2922`); il controllo `stock < units` (`:2925`) difende l'invariante «la scorta non va mai sotto zero» quando le
intercettazioni, fra scheduling e lancio, hanno consumato la stessa voce. Il lancio avvenuto ordina: consumo, `AmmunitionEvent`, `Salvo`, `in_flight`, ostile del dominio, `_touch`, evento `_IMPACT`, eventuale `_check_activity` (winchester), **poi** il nuovo `_schedule_next` del tiratore (`:2955`) e **solo dopo** le reazioni
(RWR `:2959-2961`, `_register_launcher` `:2965-2967`, `_react_to_hostile` `:2969-2970`): il tiratore decide il proprio prossimo lancio senza ancora conoscere la reazione che il suo lancio provoca sugli altri (una reazione al lancio che lo riguarda arriva come `_DECIDE`, D25). L'evento `_IMPACT` produce il gruppo da risolvere in `_on_impact`
(`:2974`), che accoda il `_RESOLVE` (D5, D85). Rimando a **D37** (fine di attività) e **D45** (`return_fire` e `_WAKE`).

### La sequenza di `_on_resolve` (D85)

*Diagramma D85 — `_on_resolve`: la risoluzione di un evento-salva contro una forza, in tre blocchi (intercettazione, danno per colpo, dottrina) (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant RUN as _on_resolve
    participant IC as _admissible, _may_intercept e _in_time
    participant SH as _Shadow
    participant DM as Damage_Model
    participant DOC as _check_doctrine
    RUN->>RUN: group = pending.pop(force_id), esce se assente o senza salve
    RUN->>RUN: before, ordered per (t_impact, salvo_id), in_flight.pop, rounds e interceptable
    Note over RUN,IC: blocco 1 - intercettazione per dominio (D24)
    RUN->>RUN: interceptors del dominio, instant_interceptions e canali gia spesi per le altre forze
    loop per ogni intercettore operativo e non a terra
        RUN->>SH: interceptor_stock
        RUN->>RUN: available[id] = min(canali meno spesi, scorta)
    end
    RUN->>RUN: capacity = somma delle disponibilita
    loop per ogni salva intercettabile
        loop per ogni intercettore, finche restano colpi
            RUN->>IC: _admissible(shadow, salvo), filtro BI (sempre vero se la regola e spenta)
            RUN->>IC: _may_intercept(shadow, salvo), regola L1, solo se il precedente e vero
            RUN->>IC: _in_time(shadow, salvo), regola R-INT, solo se i precedenti sono veri
            RUN->>RUN: take = min(free, left), used e left aggiornati
        end
    end
    RUN->>RUN: stopped per salva e intercepted
    loop per ogni intercettore con used maggiore di zero
        RUN->>SH: consume_interceptions(count_used)
        SH-->>RUN: ripartizione (arma, n)
        RUN->>RUN: interception_events.append(InterceptionEvent), uno per arma
    end
    Note over RUN,DM: blocco 2 - danno per colpo non fermato
    loop per ogni salva e per ogni colpo non fermato
        alt il bersaglio e gia distrutto
            RUN->>RUN: wasted aumenta di uno, nessuna estrazione
        else il colpo va a segno
            RUN->>RUN: _draw(), una estrazione dell rng di sessione
            RUN->>DM: build_damage_event(target, accuracy, destroy_capacity, draw, ...)
            DM-->>RUN: DamageEvent
            RUN->>RUN: target.health = event.health_after, damage_events.append, destroyed_at, loss_shooters
        end
    end
    RUN->>RUN: after, losses, shock, erosion e SalvoResolution
    RUN->>RUN: _touch(time)
    opt target_rules non vuoto
        RUN->>RUN: _wake_after_destruction(time)
    end
    opt activity_criteria non vuoto
        RUN->>RUN: _check_activity(time)
    end
    Note over RUN,DOC: blocco 3 - dottrina di disingaggio (D22)
    RUN->>DOC: _check_doctrine(time, state, shock, erosion, len(after), len(losses), withdrawable)
    DOC->>DOC: operative_left uguale a zero, esito DESTROYED e broken_forces
    DOC->>DOC: altrimenti _breakpoint(time, state), poi confronto di erosione e shock
    DOC->>DOC: se scatta un motivo, esito DISENGAGED e broken_forces
```

Lettura: **Blocco 1** (`:3157-3239`). I canali sono per evento-salva e per dominio: quelli già spesi dalle *altre* forze dello stesso dominio nello stesso istante si sottraggono (`:3161-3170`), le disponibilità si calcolano solo per intercettori operativi e non a terra (`:3186-3189`). Le salve si scorrono nell'ordine `(t_impact, salvo_id)`
e gli intercettori nell'ordine della regola F (`:3195-3215`); dalla BI la condizione del ciclo è `free <= 0 or not _admissible or not _may_intercept or not _in_time` (`Engagement_Resolver.py:3881-3882` a `a389cadb`, corto circuito di `or`): `_may_intercept` è chiamata solo se `_admissible` è vera e `_in_time` solo se lo sono entrambe (riga riverificata il 2026-11-10; le altre righe di questo paragrafo sono a f009eb43). Anche `_admissible` non fa estrazioni. Né `_may_intercept` né `_in_time` (e dalla BI nemmeno `_admissible`) fanno estrazioni (docstring di `_in_time`, `:3115`): il flusso dell'`rng` non cambia. Le intercettazioni consumano la scorta
dell'intercettore **prima** del danno (`:3236`), e generano un `InterceptionEvent` per arma (`:3237-3239`). **Blocco 2** (`:3241-3264`): per ogni colpo non fermato su un bersaglio già distrutto si conta `wasted` senza estrarre (payload congelato); altrimenti `_draw()` è valutata come argomento di `build_damage_event`
(`:3253-3255`), quindi **una estrazione per colpo che arriva su un bersaglio vivo**, nell'ordine salve, colpi. Se il colpo mette fuori combattimento un asset operativo, `loss_shooters` ricorda chi (`:3262-3264`; serve a `_unanswered_fraction`). **Blocco 3** (`:3266-3301`): `shock = perdite / impegnati`, `erosion = (impegnati - operativi dopo) / impegnati`
(`:3267-3269`); `_check_doctrine` (`:3305`) riceve le frazioni dell'intera forza, oppure, se alcuni impegnati sono aerei a terra, quelle calcolate sui soli combattenti e `withdrawable=bool(fighting_after)` (`:3286-3301`). Dentro `_check_doctrine`: l'annientamento prevale su un disingaggio già deciso (`:3321-3329`);
senza dottrina (`thresholds` `None`), con esito già deciso o senza possibilità di ritirarsi non c'è altro (`:3331-3332`); altrimenti `_breakpoint` (`:3516`, che chiama `_perceived_ratio` e `_unanswered_fraction`) dà B(t) e si confrontano erosione e shock (`:3334-3349`). Rimando a **D5** (la coda), **D22** (soglia di rottura), **D24** (allocazione delle intercettazioni),
**D27** (regola R-INT) e **D33** (difesa di dominio).

**Dal 2026-11-11 (FP-5 (d))** il vincolo `_in_time` non legge più «l'ultimo rilevamento» dell'intercettore sul lanciatore: chiede `_detection_time_of(shadow.id, salvo.shooter_id, salvo.t_launch)`, che cerca il rilevamento **nel passaggio** del lanciatore nel volume dell'intercettore **che contiene il lancio** (`_detection_time_in_pass`); senza i tratti resta l'ultimo rilevamento. Nessuna estrazione: flusso in **D134** (capitolo 4 §4.26). Le righe di questa «Lettura» (salvo la `:3881-3882` appena aggiornata) restano a f009eb43.

### La sequenza di `apply_engagement_result` (D86)

*Diagramma D86 — `apply_engagement_result`: dall'`EngagementResult` agli asset reali, con danni prima e consumi poi (livello L3, verificato a f009eb43).*

```mermaid
sequenceDiagram
    participant SS as Session_Simulator
    participant AER as apply_engagement_result
    participant DID as _domain_id
    participant DM as Damage_Model
    participant CW as _call_with_weapon
    participant AST as asset reale
    SS->>AER: apply_engagement_result(result, *forze)
    AER->>AER: TypeError se result non e un EngagementResult
    loop per ogni forza e per ogni asset della forza
        AER->>DID: _domain_id(asset)
        DID-->>AER: id, oppure None e l asset e saltato
    end
    loop per ogni evento di danno nell ordine di produzione
        alt target_id non trovato
            AER->>AER: warning e missing_assets aumenta di uno
        else asset trovato
            AER->>DM: apply_damage_event(asset, event)
            AER->>AER: damage_events aumenta di uno
        end
    end
    AER->>AER: consumptions = ammunition_events e interception_events ordinati per (time, tipo, indice)
    loop per ogni consumo
        alt asset non trovato
            AER->>AER: warning con ruolo shooter o interceptor, missing_assets aumenta di uno
        else evento di munizioni (tipo 0)
            AER->>AST: getattr(asset, consume_ammunition)
            AER->>CW: _call_with_weapon(consume, event.rounds, event.weapon)
            CW->>AST: consume(amount) se weapon e None, altrimenti consume(amount, weapon=weapon)
            AER->>AER: ammunition_events aumenta di uno
        else evento di intercettazione (tipo 1)
            AER->>AST: getattr(asset, consume_interceptor_stock)
            AER->>CW: _call_with_weapon(consume, event.interceptions, event.weapon)
            CW->>AST: consume(amount) se weapon e None, altrimenti consume(amount, weapon=weapon)
            AER->>AER: interception_events aumenta di uno
        end
    end
    AER-->>SS: summary, quattro contatori
```

Lettura: `apply_engagement_result` (`:3794`) è il solo punto in cui l'esito tocca gli asset veri; in sessione la chiama `engage` dopo ogni `resolve_engagement` (`Logic/Session_Simulator.py:2790`, con `*component`) e `fire_area` dopo ogni fuoco su posizione (`:2486`, con `*blocks.values()`: D50). L'indice degli asset è costruito
con `_domain_id` su tutte le forze passate (`:3814-3821`). I **danni** si applicano per primi e nell'ordine in cui la run li ha prodotti (`:3825-3834`), perché i `health_before`/`health_after` sono concatenati. I **consumi** si ordinano per `(time, tipo, indice)` (`:3843-3845`): a parità d'istante i lanci (tipo 0) precedono le intercettazioni (tipo 1),
come nella coda (`_LAUNCH` < `_RESOLVE`), per lasciare sull'asset lo stato che l'ombra ha descritto (commento a `:3836-3842`). `_call_with_weapon` (`:3782`) esiste per gli asset duck-typed con la firma precedente al 2026-09-26: senza arma si chiama `consume(amount)`, con arma `consume(amount, weapon=weapon)`.
**Fatto da non fraintendere**: i contatori `ammunition_events` e `interception_events` del riepilogo aumentano anche se l'asset non ha un `consume_ammunition`/`consume_interceptor_stock` chiamabile (`:3859-3862`, `:3867-3870`): contano gli eventi elaborati, non i consumi effettivamente eseguiti. Un asset non trovato non è un errore:
è un warning e `missing_assets` (`:3828-3831`, `:3850-3854`). Rimando a **D9** (applicazione dell'esito) e **D13** (scorta per arma).

### Che cosa il core importa da `Engagement_Resolver`, e chi (D87)

*Diagramma D87 — i nomi di `Engagement_Resolver` usati dal resto del core e i moduli che li usano; l'arco è «usa il nome» (livello L2, verificato a f009eb43).*

```mermaid
flowchart LR
    SS["Session_Simulator"]
    MA["Mission_Adapter"]
    AF["Area_Fire"]
    FCO["Fire_Control"]
    ST["Session_Types"]
    ARM["Air_Route_Manager<br/>fuori dal core"]

    API["funzioni<br/>resolve_engagement<br/>apply_engagement_result<br/>accepts_target_grounded<br/>detection_probability"]
    TIP["tipi<br/>EngagementResult, ForceOutcome<br/>AmmunitionEvent, InterceptionEvent<br/>ActivityCriteria, TargetRules, ShotSpec"]
    COS["costanti<br/>ACTIVITY_TARGET_DESTROYED, DISENGAGED<br/>ROE_WEAPON_FREE, ROE_PRIORITY_DESIGNATED"]

    SS -->|"chiama"| API
    SS -->|"costruisce e legge"| TIP
    SS -->|"confronta"| COS
    MA -->|"costruisce TargetRules"| TIP
    MA -->|"confronta"| COS
    AF -->|"costruisce un EngagementResult"| TIP
    FCO -->|"chiama"| API
    FCO -->|"costruisce ShotSpec"| TIP
    ST -->|"importa quattro tipi"| TIP
    ARM -->|"import locale"| API
```

Lettura: i cinque moduli del core che importano il risolutore sono `Session_Simulator` (`:771`), `Mission_Adapter` (`:332`), `Area_Fire` (`:77`), `Fire_Control` (`:206-207`) e `Command/Session_Types` (`:63-68`); `Air_Route_Manager` (`:1103`) è **fuori dal core**. Nessun altro modulo del core lo importa (`grep` sui sorgenti non di test: gli altri, come `Fuel_Model`, `Contact_Scheduler`, `Damage_Model`, `Session_Rng`, `Mission_Types`, lo nominano al più in commenti e docstring). Dettaglio per modulo: `Session_Simulator` chiama `ER.resolve_engagement` (`:2765`) e `ER.apply_engagement_result` (`:2486`, `:2790`), costruisce `ER.ActivityCriteria` (`:1867`, `:2722`, `:2738`), annota con `ER.EngagementResult`
(`:1327`, `:1344`, `:2408`, `:2411`), confronta con `ER.DISENGAGED` (`:2551`, `:2807`) e `ER.ACTIVITY_TARGET_DESTROYED` (`:1903`); `Mission_Adapter` costruisce `ER.TargetRules` (`:1995`) e confronta con `ER.ROE_WEAPON_FREE`/`ER.ROE_PRIORITY_DESIGNATED` (`:1985`, `:1998`); `Area_Fire.resolve_area_fire` costruisce **a mano** un `ER.AmmunitionEvent` e un `ER.EngagementResult` (`:311`, `:314`) senza passare dal risolutore,
così che `apply_engagement_result` e il resto della sessione trattino il fuoco su posizione come un ingaggio (D50); `Fire_Control` costruisce `ShotSpec` (`:786`) e chiama `ER.accepts_target_grounded` (`:971`); `Session_Types` importa `AmmunitionEvent`, `EngagementResult`, `ForceOutcome`, `InterceptionEvent` per aggregarli in `SessionOutcome`. `Fire_Control`, `Area_Fire` e `Session_Simulator` ripetono in locale il criterio di `_domain_id`
(`_asset_id` in `Fire_Control.py:1080` e `Area_Fire.py:318`, `_domain_id` in `Session_Simulator.py:974`) invece di importarlo: i loro docstring dichiarano «stesso criterio», non è verificato qui che il corpo sia identico. Per il grafo completo degli import del core v. **D58** e **D59**.

### Tabella completa dei simboli di `Logic/Engagement_Resolver`

Colonne «Tipo», «Simbolo», «Firma» e «Riga» da `inventario.py --tabella Logic/Engagement_Resolver` (127 righe, nell'ordine dello strumento: prima classi e metodi, poi le funzioni di primo livello, ciascuna sezione in ordine di riga); «Gruppo»: per le funzioni e i tipi di modulo il codice di D77 (**A** API pubblica, **T** tipi di scambio, **B** regole di bersaglio pure, **P** probabilità di rilevamento,
**F** fabbriche del fattore, **G** ponti, **S** stato di lavoro), per i metodi di `_EngagementRun` il codice **R1-R12** di D79/D80 (la classe stessa è «run»); «Chiamata da»: chiamanti dentro il modulo (estrazione `ast` dei nomi chiamati, verificata caso per caso; i metodi della run sono indicati col solo nome) e nel core (`SS` = `Session_Simulator`, `MA` = `Mission_Adapter`, `AF` = `Area_Fire`, `FCO` = `Fire_Control`, `ST` = `Session_Types`, `ARM` = `Air_Route_Manager`, fuori dal core); «implicito» = chiamato dal costruttore o da una proprietà, non da una chiamata esplicita.

| Gruppo | Tipo | Simbolo | Firma | Riga | Che cosa fa | Chiamata da |
|---|---|---|---|---|---|---|
| T | classe | `ShotSpec` | `ShotSpec`; campi: accuracy, destroy_capacity, rounds, weapon, time_of_flight, interceptable, cycle_time, max_range, stock_per_round, intercept_domains, min_altitude, max_altitude, max_target_z | `:673` | Che cosa spara un tiratore contro un bersaglio (accuracy e destroy_capacity, colpi, arma, volo, portata, unità di scorta per colpo, domini di difesa aerea che possono fermarne il colpo (BI), fascia di quota relativa `min_altitude`/`max_altitude` e tetto assoluto `max_target_z` (VA)): è la risposta della fire control. | `FCO:shot_spec_for` (costruttore); letta da `_first_with_stock`, `_options`, `_refire_interval` |
| T | metodo | `ShotSpec.__post_init__` | `__post_init__(self)` | `:718` | Valida i campi (tipi e intervalli; `intercept_domains` deve essere `None` o un `frozenset` incluso in `AD_DOMAINS`) e solleva `TypeError`/`ValueError`. | implicito alla costruzione |
| T | classe | `Detection` | `Detection`; campi: observer_id, target_id, sensor_range, distance_cpa, probability, draw, detected, time, exposure_s, dwell_time_s, pass_index, pass_count, pass_start, pass_end | `:767` | Esito di un'estrazione di rilevamento: una per passaggio nel volume proprio (FP) se la direzione ha due o più passaggi, altrimenti una per direzione; porta anche permanenza e dwell (D-5) e i dati del passaggio (`pass_index`, `pass_count`, `pass_start`, `pass_end`). | `_detect_direction`, `_detect_passes` (costruttore) |
| T | classe | `Salvo` | `Salvo`; campi: salvo_id, t_launch, t_impact, shooter_id, target_id, target_force_id, rounds, spec | `:792` | Una salva lanciata, a payload congelato. | `_on_launch` (costruttore) |
| T | classe | `SalvoResolution` | `SalvoResolution`; campi: time, force_id, salvo_ids, rounds, interceptable_rounds, capacity, intercepted, wasted, losses, shock, erosion | `:814` | Un evento-salva risolto contro una forza: unità di saturazione e di shock. | `_on_resolve` (costruttore) |
| T | classe | `AmmunitionEvent` | `AmmunitionEvent`; campi: time, asset_id, rounds, weapon | `:844` | Consumo esplicito di munizioni offensive (unità di scorta). | `_on_launch`, `AF:resolve_area_fire` (costruttore); `ST` (import) |
| T | classe | `InterceptionEvent` | `InterceptionEvent`; campi: time, asset_id, interceptions, force_id, salvo_ids, weapon | `:868` | Intercettazioni effettuate da un intercettore, uno per arma. | `_on_resolve` (costruttore); `ST` (import) |
| T | classe | `ActivityCriteria` | `ActivityCriteria`; campi: winchester_weapons, damage_threshold, target_ids, destroyed_targets, until, reference_health | `:902` | Criteri di fine di attività di un asset, nella forma del risolutore (F6-B1). | `SS:_activity_criteria` (costruttore); letta da `_check_activity`, `_targets_destroyed_at`, `_activity_end_time` |
| T | classe | `ActivityEnd` | `ActivityEnd`; campi: time, asset_id, reason | `:940` | Fine di attività scattata nella run. | `_end_activity` (costruttore) |
| T | classe | `TargetRules` | `TargetRules`; campi: roe, designated_ids, designated_area, designated_weapons, air_self_defence, known_hostile_ids, attack_point, known_destroyed_ids | `:963` | Regole di bersaglio di un asset tiratore (F7a). | `MA:target_rules` (costruttore, `:1995`); lette da `_is_deferred`, `_fire_control` e altri metodi del gruppo R7 |
| T | metodo | `TargetRules.__post_init__` | `__post_init__(self)` | `:996` | Valida `roe`, normalizza gli insiemi di id e verifica `attack_point` e `designated_area`. | implicito alla costruzione |
| T | classe | `ForceOutcome` | `ForceOutcome`; campi: force_id, side, outcome, time, triggers, committed, lost, erosion, max_shock, temper, breakpoint, morale, force_ratio, unanswered_fraction, block_id | `:1088` | Esito di una forza: HELD, DISENGAGED o DESTROYED, con i motivi e le grandezze di dottrina. | `_result` (costruttore); `ST` (import) |
| T | classe | `EngagementResult` | `EngagementResult`; campi: t_start, t_end, forces, detections, salvos, resolutions, damage_events, ammunition_events, interception_events, activity_ends | `:1127` | Esito completo e immutabile di un ingaggio. | `_result` (costruttore); `AF:resolve_area_fire` (costruttore); `SS` (tipo e lettura); `ST` (import) |
| T | metodo | `EngagementResult.outcome_of` | `outcome_of(self, force_id)` | `:1146` | L'esito della forza `force_id`, `None` se non partecipa. | nessun chiamante nel core (solo test) |
| T | metodo | `EngagementResult.ammunition_consumed` | `ammunition_consumed(self)` | `:1154` | Unità di scorta spese offensivamente per asset (solo le salve). | nessun chiamante nel core su `EngagementResult` (solo test); `Readiness.py:191` chiama il metodo omonimo di `SessionOutcome` |
| T | metodo | `EngagementResult.ammunition_consumed_by_weapon` | `ammunition_consumed_by_weapon(self)` | `:1169` | Come `ammunition_consumed`, ripartito per arma: `{asset: {arma: unità}}`. | nessun chiamante nel core su `EngagementResult` (solo test); esiste un metodo omonimo in `SessionOutcome` (`Session_Types.py:494`) |
| T | metodo | `EngagementResult.interceptions_consumed` | `interceptions_consumed(self)` | `:1179` | Intercettazioni effettuate per asset. | nessun chiamante nel core su `EngagementResult` (solo test); `Readiness.py:192` chiama il metodo omonimo di `SessionOutcome` |
| S | classe | `_Shadow` | `_Shadow`; campi: __slots__ | `:1669` | Copia di lavoro di un asset impegnato: salute e scorte evolvono qui, non sull'asset. | `_shadow_of` (costruttore) |
| S | metodo | `_Shadow.__init__` | `__init__(self, asset_id, asset, force_id, health, ammunition, interceptor_stock, stores, unmodelled, interceptor_weapons)` | `:1687` | Copia le scorte per arma (o i pool anonimi) e prepara la vista degli intercettori. | `_shadow_of` |
| S | metodo | `_Shadow.ammunition` | `ammunition(self)` | `:1702` | Proprietà: scorta totale (vista, come `Mobile.ammunition`). | implicito (proprietà) |
| S | metodo | `_Shadow.available` | `available(self, weapon)` | `:1706` | Unità spendibili da `weapon`, `None` = nessun vincolo. | `_first_with_stock`, `_on_launch` |
| S | metodo | `_Shadow.has_stock` | `has_stock(self)` | `:1710` | Esiste almeno un'arma con scorta (le armi non modellate non hanno vincolo). | `_schedule_next` |
| S | metodo | `_Shadow.consume` | `consume(self, weapon, units)` | `:1713` | Consuma `units` di scorta dalla voce dell'arma (o dall'aggregato) e ritorna il consumato. | `_on_launch` |
| S | metodo | `_Shadow.interceptor_stock` | `interceptor_stock(self)` | `:1719` | Proprietà: scorta di intercettori (vista sulle voci AD o pool anonimo). | `_on_resolve` (proprietà) |
| S | metodo | `_Shadow.consume_interceptions` | `consume_interceptions(self, amount)` | `:1722` | Consuma `amount` intercettazioni e ritorna la ripartizione `[(arma, n)]`. | `_on_resolve` |
| S | metodo | `_Shadow.operative` | `operative(self)` | `:1737` | Proprietà: la salute supera `OPERATIVE_HEALTH_FLOOR`. | molti metodi della run (`_build_forces`, `_schedule_next`, `_on_launch`, `_on_resolve`, `_result`, ...) |
| S | metodo | `_Shadow.destroyed` | `destroyed(self)` | `:1741` | Proprietà: la salute è sotto la soglia di distruzione di `Damage_Model`. | `_on_resolve`, `_check_activity`, `_designated_destroyed` |
| S | classe | `_Candidate` | `_Candidate`; campi: t_ready, target_id, t_end, exhausted, t_cpa, distance_cpa, not_before | `:1746` | Un bersaglio rilevato da un tiratore, ingaggiabile in `[t_ready, t_end]`. | `_detect_direction` (costruttore); modificata da `_schedule_next`, `_on_launch` |
| S | classe | `_ForceState` | `_ForceState`; campi: force_id, side, committed, thresholds, interceptors, outcome, time, triggers, max_shock, force, air, temper, temper_z, morale, enemy_estimate, stationary, loss_shooters, breakpoint, force_ratio, unanswered_fraction, fire, block_id | `:1763` | Stato di una forza nella run: impegnati, dottrina, esito e grandezze della soglia di rottura. | `_build_forces` (costruttore) |
| S | classe | `_PendingGroup` | `_PendingGroup`; campi: resolve_time, salvos | `:1792` | Salve che atterrano su una forza entro la finestra di salva, da risolvere insieme. | `_on_impact` (costruttore) |
| run | classe | `_EngagementRun` | `_EngagementRun`; campi: - | `:1939` | Stato e coda eventi di un ingaggio a due o più forze. | `resolve_engagement` (costruttore) |
| R1 | metodo | `_EngagementRun.__init__` | `__init__(self, forces, contacts, fire_control, rng, legs, committed, thresholds, reaction_profile_for, detection_factor, salvo_window, provenance, breakpoint_rng, morale_for, enemy_estimate_for, fire_doctrine, rwr_catalogue, coordination_of, grounded, activity_criteria, target_rules, dwell_time_for, pass_rng)` | `:1942` | Crea gli stati vuoti, legge una volta `BI_AD_TARGET_RULE` e `VA_ENGAGEMENT_ALTITUDE_BAND`, riceve `dwell_time_for` e `pass_rng`, costruisce forze e domini, inizializza le soglie di rottura e la fine di attività (D81). | `resolve_engagement` (costruttore) |
| R1 | metodo | `_EngagementRun._build_forces` | `_build_forces(self, forces, committed, thresholds)` | `:2086` | Ombre e `_ForceState` di ogni forza; `False` se meno di due forze hanno asset impegnabili. | `__init__` |
| R1 | metodo | `_EngagementRun._build_domains` | `_build_domains(self, coordination_of)` | `:2177` | Dominio di coordinamento di ogni forza e intercettori per dominio, in ordine della regola F. | `__init__` |
| R1 | metodo | `_EngagementRun._same_domain` | `_same_domain(self, force_a, force_b)` | `:2218` | Le due forze sono nello stesso dominio di coordinamento? | `_engaged_shooters`, `_force_shots_on`, `_register_launcher` |
| R1 | metodo | `_EngagementRun._shadow_of` | `_shadow_of(asset_id, asset, force_id, health)` | `:2222` | Metodo statico: stato ombra dalle scorte dell'asset, con letture difensive. | `_build_forces` |
| R1 | metodo | `_EngagementRun._interceptors_of` | `_interceptors_of(self, force, force_id)` | `:2249` | Lista `[(ombra, canali)]` degli intercettori della forza, esclusi gli aerei sempre a terra. | `_build_forces` |
| R1 | metodo | `_EngagementRun._profile` | `_profile(self, shooter_id)` | `:2272` | Profilo di reazione del tiratore, memoizzato. | `_detect_direction`, `_in_time`, `_react_to_hostile`, `_refire_interval`, `_register_launcher` |
| R2 | metodo | `_EngagementRun._detect` | `_detect(self)` | `:2280` | Una `_detect_direction` per direzione di ogni finestra, in ordine canonico. | `run` |
| R2 | metodo | `_EngagementRun._detect_direction` | `_detect_direction(self, window, observer, target, own_range, other_range)` | `:2301` | Per direzione di una finestra: legge fattore e dwell, calcola i passaggi nel volume proprio (`_own_passes`); con due o più delega a `_detect_passes`, altrimenti una estrazione (distanza e permanenza del passaggio, FP-3 (a)); se rileva, percezione e candidato (D82, D131). | `_detect` |
| R2 | metodo | `_EngagementRun._perceive` | `_perceive(self, force_id, asset_id, time)` | `:2386` | Il dominio della forza percepisce l'asset nemico dall'istante `time`. | `_detect_direction`, `_perceive_rwr` |
| R2 | metodo | `_EngagementRun._perceive_rwr` | `_perceive_rwr(self, aircraft, emitter, time)` | `:2392` | Percezione dell'emettitore da parte dell'RWR dell'aereo, con la classe dell'emettitore (R-CLS). | `_detect_direction`, `_on_launch` |
| R11 | metodo | `_EngagementRun._air_threat` | `_air_threat(self, state, shadow, time, n_aircraft)` | `:2401` | Peso di un nemico percepito da una forza aerea (R-CLS). | `_perceived_ratio` |
| R2 | metodo | `_EngagementRun._detection_time` | `_detection_time(self, window, observer_id, target_id, own_range, other_range, radius)` | `:2434` | Istante del rilevamento dentro la finestra (estrazione unica); dentro un passaggio lo dà `_pass_detection_time`. | `_detect_direction` |
| R2 | metodo | `_EngagementRun._exposure_time` | `_exposure_time(self, window, own_range, other_range)` | `:2462` | Permanenza D-5 [s] nel **ripiego senza tratti** (chiamate dirette senza `legs`): tutta la finestra se la portata propria è la maggiore, altrimenti l'intervallo reciproco, altrimenti 0. Con i tratti la permanenza è quella del passaggio (`_detect_direction`, `_detect_passes`; mai la somma, FP-6). Nessuna estrazione. | `_detect_direction` |
| R2 | metodo | `_EngagementRun._own_intervals` | `_own_intervals(self, observer_id, target_id, own_range, radius)` | `:2476` | Intervalli in cui il bersaglio è nella sfera di raggio `own_range` (o `radius`, il raggio estratto) centrata sull'osservatore, da `range_intervals` sui tratti; `None` senza i tratti di entrambi. **Unico punto di chiamata del volume proprio** (decisione VA-6 (a)). | `_detection_time`, `_own_passes`, `_pass_detection_time` |
| R2 | metodo | `_EngagementRun._dwell_of` | `_dwell_of(self, window, observer, target)` | `:2493` | Periodo di rivisita [s] del sensore dell'osservatore contro il bersaglio (D-5): `None` senza lettore (`dwell_time_for`) o senza dato; il modo è quello del bersaglio (a terra: `GROUNDED_DETECTION_MODE`). Nessuna estrazione. | `_detect_direction` |
| R2 | metodo | `_EngagementRun._own_passes` | `_own_passes(self, window, observer_id, target_id, own_range, dwell)` | `:2504` | Passaggi `(lo, hi, start, end)` del bersaglio nel volume proprio dentro la finestra, uniti se separati da un'uscita ≤ dwell (FP-10, `_join_passes`); `None` senza i tratti (ripiego). | `_detect_direction` |
| R2 | metodo | `_EngagementRun._pass_cpa` | `_pass_cpa(self, window, observer_id, target_id, lo, hi)` | `:2528` | `(t_cpa, distanza)` del massimo avvicinamento dentro il passaggio `[lo, hi]` (FP-4), con `clamp_legs` e `closest_point_of_approach`; ripiego il CPA della finestra, con un `logger.debug`. | `_detect_passes` |
| R2 | metodo | `_EngagementRun._pass_detection_time` | `_pass_detection_time(self, observer_id, target_id, own_range, lo, hi, radius, t_cpa)` | `:2540` | Istante del rilevamento dentro il passaggio: primo istante con la distanza sotto il raggio estratto; ripiego il CPA del passaggio. | `_detect_passes` |
| R2 | metodo | `_EngagementRun._detect_passes` | `_detect_passes(self, window, observer, target, own_range, factor, dwell, passes)` | `:2550` | Una estrazione per passaggio (due o più passaggi): il primo da `rng`, gli altri da `pass_rng`; `ValueError` se `pass_rng` manca; CPA, permanenza D-5 e candidato fino alla fine del proprio passaggio, una `Detection` per passaggio (D133). | `_detect_direction` |
| R3 | metodo | `_EngagementRun._push` | `_push(self, time, kind, key, payload)` | `:2608` | Accoda un evento `(time, kind, key, sequence, payload)`. | `_on_impact`, `_on_launch`, `_react_to_hostile`, `_register_launcher`, `_schedule_next`, `_schedule_phase_wakes`, `_wait`, `_wake_after_destruction` |
| R3 | metodo | `_EngagementRun._draw` | `_draw(self, rng)` | `:2612` | Una estrazione dallo stream indicato (default l'`rng` di sessione; `pass_rng` per i passaggi dal secondo in poi), validata in `[0, 1)`. | `_detect_direction`, `_detect_passes`, `_on_resolve` |
| R3 | metodo | `_EngagementRun._touch` | `_touch(self, time)` | `:2620` | Aggiorna `t_end` al massimo istante visto. | `_on_launch`, `_on_resolve` |
| R12 | metodo | `_EngagementRun._activity_end_time` | `_activity_end_time(self, asset_id)` | `:2625` | Istante dal quale l'asset non lancia più, `None` se nessuno. | `_on_launch`, `_schedule_next` |
| R12 | metodo | `_EngagementRun._targets_destroyed_at` | `_targets_destroyed_at(self, criteria)` | `:2639` | Istante in cui tutti i bersagli del criterio sono distrutti, `None` se qualcuno no. | `_check_activity` |
| R12 | metodo | `_EngagementRun._check_activity` | `_check_activity(self, time, targets_only)` | `:2655` | Verifica i criteri di fine di attività (danno, winchester, bersagli distrutti) e registra quelli scattati. | `__init__`, `_on_launch`, `_on_resolve` |
| R12 | metodo | `_EngagementRun._end_activity` | `_end_activity(self, time, asset_id, reason)` | `:2691` | Registra la fine di attività e annulla il lancio programmato se è già in vigore. | `_check_activity` |
| R5 | metodo | `_EngagementRun._engaged_shooters` | `_engaged_shooters(self, target_id, force_id, exclude)` | `:2706` | Quanti altri tiratori del dominio sono impegnati ora su `target_id`. | `_schedule_next` |
| R4 | metodo | `_EngagementRun._schedule_next` | `_schedule_next(self, shooter_id, t_earliest)` | `:2727` | Decide il prossimo lancio del tiratore e lo accoda con payload congelato (D83). | `run`, `_on_decide`, `_on_launch`, `_on_wake` |
| R5 | metodo | `_EngagementRun._force_shots_on` | `_force_shots_on(self, target_id, force_id)` | `:2929` | Generatore delle salve del dominio dirette a `target_id`: in volo o schedulate. | `_coverage`, `_wait` |
| R5 | metodo | `_EngagementRun._coverage` | `_coverage(self, target_id, force_id)` | `:2949` | Probabilità che le salve già dirette dal dominio distruggano il bersaglio. | `_blocked` |
| R5 | metodo | `_EngagementRun._rounds_in_flight` | `_rounds_in_flight(self, shooter_id, target_id)` | `:2962` | Colpi in volo del tiratore contro il bersaglio. | `_blocked` |
| R5 | metodo | `_EngagementRun._blocked` | `_blocked(self, shooter, target_id, exempt_from_saturation)` | `:2966` | Il tiratore non deve aggiungere salve (tetto o saturazione). | `_schedule_next` |
| R5 | metodo | `_EngagementRun._wait` | `_wait(self, shooter, pool, t_earliest)` | `:2981` | Tutti i bersagli bloccati: ridecisione al primo impatto previsto. | `_schedule_next` |
| R4 | metodo | `_EngagementRun._gone` | `_gone(self, target)` | `:3003` | Il bersaglio non è raggiungibile perché la sua forza ha rotto il contatto (salvo aerei a terra). | `_on_launch`, `_schedule_next` |
| R2 | metodo | `_EngagementRun._grounded_in` | `_grounded_in(self, asset_id, window)` | `:3012` | L'asset è a terra nella finestra (stato al punto medio). | `_detect_direction` |
| R7 | metodo | `_EngagementRun._is_designated` | `_is_designated(self, rules, target, time)` | `:3021` | Il bersaglio è designato dalla missione del tiratore a `time` (id o area). | `_designated_first`, `_fire_control`, `_is_deferred` |
| R7 | metodo | `_EngagementRun._is_hostile` | `_is_hostile(self, shooter, target_id)` | `:3038` | Il bersaglio ha già lanciato contro il dominio del tiratore (`return_fire`). | `_fire_control`, `_is_deferred` |
| R7 | metodo | `_EngagementRun._attack_pass_time` | `_attack_pass_time(self, shooter_id, rules)` | `:3044` | Istante in cui il tiratore ha raggiunto e superato il punto ATTACK, `None`; memoizzato. | `_attack_over`, `_schedule_phase_wakes` |
| R7 | metodo | `_EngagementRun._designated_destroyed` | `_designated_destroyed(self, rules)` | `:3071` | Tutti i bersagli designati per id sono distrutti. | `_attack_over`, `_wake_after_destruction` |
| R7 | metodo | `_EngagementRun._attack_over` | `_attack_over(self, shooter_id, rules, time)` | `:3084` | Fine dell'attacco di `priority_designated` a `time`. | `_fire_control`, `_is_deferred` |
| R7 | metodo | `_EngagementRun._is_deferred` | `_is_deferred(self, shooter, target, time)` | `:3093` | La regola di bersaglio esclude il bersaglio ora per una ragione che dipende dal tempo. | `_schedule_next` |
| R7 | metodo | `_EngagementRun._designated_first` | `_designated_first(self, shooter, viable)` | `:3108` | I candidati designati e a portata, solo con ROE `priority_designated`. | `_schedule_next` |
| R7 | metodo | `_EngagementRun._react_to_hostile` | `_react_to_hostile(self, time, launcher, target_force_id)` | `:3122` | Riesamina dopo il `refire_interval` i tiratori `return_fire` del dominio che hanno il nuovo ostile fra i candidati. | `_on_launch` |
| R7 | metodo | `_EngagementRun._schedule_phase_wakes` | `_schedule_phase_wakes(self)` | `:3146` | Risveglio dei tiratori `priority_designated` al passaggio sul punto ATTACK. | `run` |
| R7 | metodo | `_EngagementRun._wake_after_destruction` | `_wake_after_destruction(self, time)` | `:3160` | Dopo una risoluzione, risveglia una volta i tiratori il cui designato è distrutto. | `_on_resolve` |
| R7 | metodo | `_EngagementRun._on_wake` | `_on_wake(self, time, shooter_id)` | `:3171` | Riesame di un tiratore dopo un cambio di fase o un nuovo ostile. | `run` |
| R4 | metodo | `_EngagementRun._fire_control` | `_fire_control(self, shooter, target, time, altitudes)` | `:3182` | La fire control sulla coppia (con le quote all'istante se `altitudes`), ristretta dalle regole di bersaglio del tiratore. | `_altitude_deferral`, `_in_range_at`, `_schedule_next` |
| R4 | metodo | `_EngagementRun._call_fire_control` | `_call_fire_control(self, shooter, target, time, altitudes)` | `:3197` | Chiama la fire control iniettata, con le estensioni `target_grounded` per un aereo a terra (F4c) e `altitudes` (VA; `(None, None)` = quote ignote). | `_fire_control` |
| R6 | metodo | `_EngagementRun._is_launcher_against` | `_is_launcher_against(self, asset_id, force_id)` | `:3249` | L'asset ha lanciato armi aria-superficie contro il dominio della forza (L2). | `_register_launcher`, `_schedule_next` |
| R6 | metodo | `_EngagementRun._in_range_at` | `_in_range_at(self, shooter, index, candidate, t_fire)` | `:3253` | Il candidato è ingaggiabile (arma con scorta, entro portata e fascia) a `t_fire`, senza effetti sul candidato; un rinvio VA-2.1 non è «a portata adesso». | `_designated_first`, `_register_launcher`, `_schedule_next` |
| R6 | metodo | `_EngagementRun._register_launcher` | `_register_launcher(self, time, launcher, target_force_id)` | `:3277` | Primo lancio aria-superficie di un aereo contro una forza: i difensori ridecidono dopo il `refire_interval` (L3). | `_on_launch` |
| R6 | metodo | `_EngagementRun._on_decide` | `_on_decide(self, time, shooter_id, generation)` | `:3329` | Fine della valutazione dopo una prelazione: nuova decisione con lo stato attuale. | `run` |
| R4 | metodo | `_EngagementRun._options` | `_options(result)` | `:3338` | Metodo statico: le opzioni di una risposta della fire control (`None`, una `ShotSpec` o una sequenza). | `_first_with_stock`, `apply_target_rules` |
| R4 | metodo | `_EngagementRun._first_with_stock` | `_first_with_stock(self, shooter, result)` | `:3356` | `(ShotSpec, colpi)` della prima opzione con scorta per almeno un colpo, o `None`. | `_in_range_at`, `_schedule_next` |
| R4 | metodo | `_EngagementRun._range_entry` | `_range_entry(self, shooter_id, candidate, max_range, t_from, band)` | `:3375` | Primo istante con il bersaglio entro la portata (con VA e `band`: sfera ∩ fascia), o `None`; memoizzato. | `_in_range_at`, `_schedule_next` |
| R4 | metodo | `_EngagementRun._band_of` | `_band_of(self, spec)` | `:3419` | La fascia/tetto `(min_altitude, max_altitude, max_target_z)` della `ShotSpec`; `None` a VA spenta o con i tre campi `None`. | `_altitude_deferral`, `_in_range_at`, `_schedule_next` |
| R4 | metodo | `_EngagementRun._altitudes_at` | `_altitudes_at(self, shooter_id, target_id, time)` | `:3429` | `(z_tiratore, z_bersaglio)` all'istante dato, dai tratti; `None` a VA spenta, se la fire control non dichiara `altitudes` o senza tratti (VA-2 (d)). | `_altitude_deferral`, `_call_fire_control` |
| R4 | metodo | `_EngagementRun._altitude_deferral` | `_altitude_deferral(self, shooter, candidate, t_fire)` | `:3460` | Rinvio della decisione fuori fascia (VA-2.1): `(istante, None)` col primo ingresso in sfera ∩ fascia, `(None, (spec, colpi))` se l'ingresso è già a `t_fire`, `(None, None)` se nessuna arma entrerà (D132). | `_in_range_at`, `_schedule_next` |
| R4 | metodo | `_EngagementRun._refire_interval` | `_refire_interval(self, shooter_id, spec)` | `:3513` | Intervallo fra due salve: `cycle_time` della `ShotSpec` o `refire_interval` del profilo. | `_on_launch` |
| R8 | metodo | `_EngagementRun._on_launch` | `_on_launch(self, time, shooter_id, payload)` | `:3516` | Esegue un lancio programmato: consumo, `Salvo`, evento d'impatto, reazioni (D84). | `run` |
| R8 | metodo | `_EngagementRun._on_impact` | `_on_impact(self, time, force_id, salvo)` | `:3611` | Raggruppa le salve che atterrano sulla forza entro la finestra e accoda la risoluzione. | `run` |
| R9 | metodo | `_EngagementRun._position_at` | `_position_at(self, shadow, t)` | `:3621` | Posizione `(x, y, z)` a `t`, dai tratti di rotta o dalla posizione dell'asset; `None` se ignota. | `_is_designated`, `_may_intercept`, `_round_track_time` |
| R9 | metodo | `_EngagementRun._interception_zone` | `_interception_zone(self, shadow)` | `:3636` | Zona d'intercettazione V_I come (raggio, quota base, quota tetto) relativi; memoizzata. | `_may_intercept` |
| R9 | metodo | `_EngagementRun._ad_domain` | `_ad_domain(self, shadow)` | `:3656` | Dominio di difesa aerea dell'intercettore (BI-5): `naval` per una nave (`Ship`), altrimenti `land`; memoizzato in `ad_domain_cache`. | `_admissible` |
| R9 | metodo | `_EngagementRun._admissible` | `_admissible(self, shadow, salvo)` | `:3663` | Filtro BI: vero se `BI_AD_TARGET_RULE` è spento o la `ShotSpec` non dichiara i domini; altrimenti solo se il dominio dell'intercettore è fra gli `intercept_domains` della salva. Nessuna estrazione. | `_on_resolve` |
| R9 | metodo | `_EngagementRun._may_intercept` | `_may_intercept(self, shadow, salvo)` | `:3671` | Regola L1: il punto di lancio della salva è fuori dal V_I dell'intercettore. | `_on_resolve` |
| R9 | metodo | `_EngagementRun._detection_time_of` | `_detection_time_of(self, observer_id, target_id, at)` | `:3696` | R-INT, FP-5 (d): il rilevamento dell'osservatore **nel passaggio che contiene `at`** (il lancio), `None` se non visto; senza tratti l'ultimo rilevamento in lista. | `_in_time` |
| R9 | metodo | `_EngagementRun._air_detection_range` | `_air_detection_range(self, shadow)` | `:3721` | Raggio di rilevamento aereo dell'intercettore [m]; memoizzato. | `_round_track_time` |
| R9 | metodo | `_EngagementRun._round_track_time` | `_round_track_time(self, shadow, salvo)` | `:3738` | Istante in cui l'intercettore scopre dalla geometria un colpo di cui non ha visto il lancio. | `_in_time` |
| R9 | metodo | `_EngagementRun._in_time` | `_in_time(self, shadow, salvo)` | `:3776` | Regola R-INT: l'intercettore ha traccia e tempo di reagire prima dell'impatto; il lancio è «osservato» solo con un rilevamento nel passaggio che lo contiene (FP-5 (d)). | `_on_resolve` |
| R10 | metodo | `_EngagementRun._on_resolve` | `_on_resolve(self, time, force_id)` | `:3803` | Risolve un evento-salva: intercettazione, danno per colpo, dottrina (D85). | `run` |
| R11 | metodo | `_EngagementRun._check_doctrine` | `_check_doctrine(self, time, state, shock, erosion, operative_left, salvo_losses, withdrawable)` | `:3980` | Confronta le perdite con la dottrina del lato per la forza intera. | `_on_resolve` |
| R1 | metodo | `_EngagementRun._init_breakpoints` | `_init_breakpoints(self)` | `:4031` | Tempra, morale, stima a priori e postura di ogni forza con dottrina. | `__init__` |
| R11 | metodo | `_EngagementRun._morale_of` | `_morale_of(self, state)` | `:4068` | Morale della forza in `[0, 1]`, `None` se ignoto o fuori intervallo. | `_init_breakpoints` |
| R11 | metodo | `_EngagementRun._enemy_estimate_of` | `_enemy_estimate_of(self, state)` | `:4084` | Stima a priori della forza nemica, `None` se ignota o non valida. | `_init_breakpoints` |
| R11 | metodo | `_EngagementRun._stationary` | `_stationary(self, state)` | `:4100` | `True` se tutti gli asset con tratti sono fermi, `None` se nessuno ne ha. | `_init_breakpoints` |
| R11 | metodo | `_EngagementRun._is_enemy` | `_is_enemy(self, state, shadow)` | `:4118` | L'ombra è un nemico della forza (lato diverso o lato ignoto). | `_perceived_ratio` |
| R11 | metodo | `_EngagementRun._perceived_ratio` | `_perceived_ratio(self, time, state)` | `:4126` | Rapporto di forze percepito rho, `None` se non definito. | `_breakpoint` |
| R11 | metodo | `_EngagementRun._surface_weight` | `_surface_weight(self, shadow)` | `:4171` | Peso di minaccia di un asset di superficie, memoizzato. | `_perceived_ratio` |
| R11 | metodo | `_EngagementRun._unanswered_fraction` | `_unanswered_fraction(self, state)` | `:4180` | Quota delle perdite causate da tiratori non rilevati dal dominio. | `_breakpoint` |
| R11 | metodo | `_EngagementRun._breakpoint` | `_breakpoint(self, time, state)` | `:4191` | Soglia di rottura B(t) = logistica della mediana modulata, con la tempra della forza. | `_check_doctrine` |
| R3 | metodo | `_EngagementRun.run` | `run(self)` | `:4238` | Ciclo principale: rilevamento, prime decisioni, svuotamento della coda con dispatch per tipo. | `resolve_engagement` |
| R3 | metodo | `_EngagementRun._result` | `_result(self)` | `:4263` | Costruisce `ForceOutcome` ed `EngagementResult` dalle liste di esito. | `run` |
| B | funzione | `_id_set` | `_id_set(label, value)` | `:948` | `frozenset` di id (stringhe non vuote) da un iterabile. | `TargetRules.__post_init__` |
| B | funzione | `rules_defer` | `rules_defer(rules, designated, hostile, air_target, after_attack)` | `:1032` | Funzione pura: la regola esclude il bersaglio per una ragione che dipende dal tempo. | `_is_deferred`, `apply_target_rules` |
| B | funzione | `apply_target_rules` | `apply_target_rules(rules, result, designated, hostile, air_target, after_attack)` | `:1045` | Funzione pura: la risposta della fire control ristretta dalle regole di un tiratore. | `_fire_control` |
| P | funzione | `_check_factor` | `_check_factor(factor)` | `:1191` | Valida un fattore di rilevamento in `[0, 1]`. | `_detect_direction`, `detection_probability`, `detection_radius`, `recon_detection_factor_fn`, `recon_unseen_factor` |
| P | funzione | `_check_dwell` | `_check_dwell(value)` | `:1201` | Periodo di rivisita validato (D-5): `None` o 0 → `None`; `TypeError`/`ValueError` per valori non validi. | `dwell_factor`, `_dwell_of` |
| P | funzione | `detection_probability` | `detection_probability(distance, sensor_range, factor)` | `:1215` | Pd di un sensore contro un bersaglio a `distance`: legge di quarta potenza, stima dichiarata. | `_detect_direction`; `ARM` (import locale, `Air_Route_Manager.py:1103`) |
| P | funzione | `detection_radius` | `detection_radius(draw, sensor_range, factor)` | `:1245` | Inversa di `detection_probability`: raggio al quale l'estrazione produce il rilevamento. | `_detect_direction` |
| P | funzione | `dwell_factor` | `dwell_factor(exposure_s, dwell_time_s)` | `:1277` | Fattore di permanenza D-5 `min(1, permanenza / dwell)` (1.0 senza dwell); scelta di progetto [S], nessuna costante. | `_detect_direction`, `_detect_passes`; `ARM:Path.compute_detection_metrics` (fuori dal core) |
| P | funzione | `registry_dwell_time` | `registry_dwell_time(observer, target, mode)` | `:1302` | Lettore di default del dwell: `observer.detection_dwell_time(mode)`; `None` senza modo o senza il metodo. | passata come valore da `SS:engage` (`:2793`, solo con `D5_DWELL_TIME` acceso) e chiamata come `dwell_time_for` da `_dwell_of` |
| P | funzione | `_join_passes` | `_join_passes(intervals, max_gap)` | `:1319` | Unione FP-10: gli intervalli separati da un'uscita ≤ `max_gap` (+ `TIME_EPS`) diventano un passaggio; `None` = nessuna unione. | `_own_passes` |
| P | funzione | `_detection_time_in_pass` | `_detection_time_in_pass(passes, times, at)` | `:1344` | R-INT con i passaggi (FP-5 (d)): primo rilevamento dentro il primo passaggio che contiene `at`; `None` altrimenti. | `_detection_time_of` |
| F | funzione | `weather_detection_factor` | `weather_detection_factor(conditions)` | `:1365` | Fattore di degradazione della Pd da notte e meteo avverso. | `weather_detection_factor_fn` |
| F | funzione | `weather_detection_factor_fn` | `weather_detection_factor_fn(conditions)` | `:1415` | La callable `(observer, target) -> float` per le condizioni meteo date. | `meteo_detection_factor` |
| F | funzione | `meteo_detection_factor` | `meteo_detection_factor(region_name, date, time)` | `:1432` | Come la precedente, leggendo le condizioni da `Meteo_Analysis`. | nessun chiamante nel core (v. D78) |
| F | funzione | `_block_attribute` | `_block_attribute(asset, name)` | `:1456` | `asset.block.<name>`, `None` se l'asset non ha blocco o il blocco non ha l'attributo. | `recon_detection_factor_fn` (funzione interna `detection_factor`, `:1238`, `:1241`, `:1244`) |
| F | funzione | `_check_side` | `_check_side(side)` | `:1462` | Valida un lato fra `Blue`, `Red`, `Neutral`. | `recon_detection_factor_fn`, `region_recon_detection_factor` |
| F | funzione | `recon_detection_factor_fn` | `recon_detection_factor_fn(seen_block_ids, observer_side, unseen_factor, seen_factor)` | `:1469` | La callable della nebbia di guerra di un lato, dall'istantanea dei blocchi visti. | `region_recon_detection_factor` |
| F | funzione | `combine_detection_factors` | `combine_detection_factors(*fns)` | `:1509` | Una sola callable dal prodotto di più fattori. | nessun chiamante nel core (v. D78) |
| F | funzione | `recon_unseen_factor` | `recon_unseen_factor(recon_efficiency, unseen_factor, seen_factor, relief)` | `:1546` | Fattore dei bersagli non visti, modulato dall'efficienza di ricognizione. | `region_recon_detection_factor` |
| F | funzione | `side_recon_efficiency` | `side_recon_efficiency(region, side)` | `:1578` | Efficienza di ricognizione di un lato in una regione: il massimo fra le sue `Military`. | `region_recon_detection_factor` |
| F | funzione | `region_recon_detection_factor` | `region_recon_detection_factor(region, observer_side, unseen_factor, seen_factor, relief)` | `:1619` | `recon_detection_factor_fn` per un lato, dall'istantanea di ricognizione della regione. | nessun chiamante nel core (v. D78) |
| S | funzione | `_domain_id` | `_domain_id(obj)` | `:1797` | Identificativo di dominio di un asset o di una forza (`id`, poi `name`). | `_build_forces`, `_interceptors_of`, `apply_engagement_result` |
| S | funzione | `_can_disengage` | `_can_disengage(force)` | `:1808` | La forza ha diritto a una politica di disingaggio (`Military` sì, `Block` non militare no). | `_build_forces` |
| G | funzione | `accepts_keyword` | `accepts_keyword(fire_control, name)` | `:1839` | Vera se la fire control accetta la keyword data (o `**kwargs`); firma non leggibile → falso. | `accepts_target_grounded`, `accepts_altitudes` |
| G | funzione | `accepts_target_grounded` | `accepts_target_grounded(fire_control)` | `:1861` | La fire control accetta la keyword `target_grounded` (o `**kwargs`), per introspezione della firma. | `_call_fire_control`; `FCO:restrict_by_policy` |
| G | funzione | `accepts_altitudes` | `accepts_altitudes(fire_control)` | `:1866` | La fire control accetta la keyword `altitudes` (VA), per introspezione della firma. | `_altitudes_at`; `FCO:restrict_by_policy` |
| G | funzione | `engagement_intervals` | `engagement_intervals(legs_shooter, legs_target, max_range, band)` | `:1885` | Intervalli in cui il bersaglio è nel volume d'ingaggio: sfera di raggio `max_range` (`range_intervals`); con `band` (VA) intersecata con la fascia di quota (`altitude_intervals`, `intersect_intervals`). | `_range_entry` (via `self.engagement_intervals`, assegnato in `__init__`) |
| G | funzione | `engagement_intervals_without_legs` | `engagement_intervals_without_legs(t_cpa, distance_cpa, t_end, max_range)` | `:1918` | Ripiego senza tratti di rotta: dal solo CPA. | `_range_entry` |
| A | funzione | `resolve_engagement` | `resolve_engagement(force_a, force_b, contacts, fire_control, rng, extra_forces, legs, committed, thresholds, reaction_profile_for, detection_factor, salvo_window, provenance, breakpoint_rng, morale_for, enemy_estimate_for, fire_doctrine, rwr_catalogue, coordination_of, grounded, activity_criteria, target_rules, dwell_time_for, pass_rng)` | `:4294` | Risolve un ingaggio fra due o più forze in un'unica timeline, senza mutare asset (D81). | `SS:run_session` (funzione interna `engage`, `:2800`) |
| A | funzione | `_call_with_weapon` | `_call_with_weapon(consume, amount, weapon)` | `:4476` | `consume(amount, weapon=weapon)`, o la chiamata storica `consume(amount)` senza arma. | `apply_engagement_result` |
| A | funzione | `apply_engagement_result` | `apply_engagement_result(result, *forces)` | `:4488` | Applica danni e consumi di un esito agli asset reali e ritorna un riepilogo (D86). | `SS:run_session` (funzioni interne `engage` `:2790`, `fire_area` `:2486`) |

### Limiti e domande

- **Tre accessori di `EngagementResult` duplicati in `SessionOutcome`** *(esito 2026-10-30: lasciati, nessuna azione)*. `ammunition_consumed`, `ammunition_consumed_by_weapon` e `interceptions_consumed` hanno lo stesso corpo in `EngagementResult` (`Engagement_Resolver.py:994`, `:1009`, `:1019`) e in `SessionOutcome` (`Command/Session_Types.py:478`, `:494`, `:509`); nel core si usano
  solo quelli di `SessionOutcome` (`Logic/Readiness.py:191-192`), quelli di `EngagementResult` hanno chiamanti solo nei test. Non è un errore di comportamento, ma due punti da tenere allineati. Non verificato se sia voluto.
- **Contatori di `apply_engagement_result`** *(esito 2026-10-30: docstring corretta in `191b7d37`, il codice non cambia)*. I contatori `ammunition_events` e `interception_events` del riepilogo contano gli eventi elaborati anche se l'asset non ha il metodo di consumo chiamabile (`:3859-3862`, `:3867-3870`); chi legge il riepilogo come «consumi eseguiti» sbaglia. Riportato come fatto del codice, non come difetto.
- **`_domain_id` ripetuto.** Almeno tre moduli del core ripetono il criterio di `_domain_id` invece di importarlo (D87); i docstring dichiarano l'equivalenza, il corpo non è stato confrontato riga per riga.
- **Ordine dei simboli nella tabella.** Lo strumento stampa prima classi e metodi, poi le funzioni di primo livello: l'ordine di lettura del file (ad esempio `_id_set` `:788` prima di `TargetRules`) non coincide con quello della tabella.

**Righe dopo `191b7d37`.** I `:riga` di questa parte sono quelli di `f009eb43`. Il commit `191b7d37` (solo docstring, commenti, un import e un parametro inutilizzati) sposta in avanti di 3-4 righe i simboli che stanno dopo il punto toccato in `Fuel_Model.py` (da `:933`), `Engagement_Resolver.py` (da `:3807`), `Damage_Model.py` (da `:162`) e `Mission_Types.py` (da `:1004`); in `Session_Validator.py` le righe non cambiano.

**Nota 2026-11-04 (dopo `cbc75634`).** I commit `37816355` (D-4c, sensore visivo) e `cbc75634` (D-4b, radar EWR) **non toccano nessun modulo del core** descritto in questa parte: toccano `Asset/Mobile.py`, `Asset/Vehicle_Data.py`, `Logic/Air_Route_Manager.py` (fuori dal core) e i test; `git diff 191b7d37 HEAD -- Code` non
compare per `Contact_Scheduler`, `Fire_Control` ed `Engagement_Resolver`, quindi **i `:riga` di questa parte a quei tre moduli restano validi**. Aggiornati qui solo i tre riferimenti a `Logic/Air_Route_Manager.py:1095` (l'import locale di `detection_probability`), ora `:1099` (+4). **Nel diagramma D70** il messaggio
`detection_range(mode, range_type)` di `mutual_detection_ranges` verso l'asset resta corretto come chiamata, ma dal 2026-11-04 la portata che ritorna è il massimo di **tre** sensori (`radar`, `TVD`, `visual`) e il terzo sta dietro `Mobile.D4C_VISUAL_SENSOR` (capitolo 3 §3.5); il diagramma non è stato modificato. **Non ricontrollato**: ogni altro `:riga` a `Asset/Mobile.py` o `Asset/Vehicle_Data.py`
eventualmente citato in questo file (cercati per nome del file: nessuno oltre ai tre sopra).

**Nota 2026-11-05 (dopo `efa8f353`, blocco C della D-4b: siti EWR fissi).** Il blocco C tocca solo `Asset/Vehicle_Data.py` (sette record e un marcatore), `Logic/Air_Route_Manager.py` (un commento, +1 riga) e i test (`git diff 6dee967b efa8f353 -- Code`): **nessun modulo del core** di questa parte cambia, i `:riga` a `Contact_Scheduler`, `Fire_Control` ed `Engagement_Resolver` restano validi e **nessun diagramma cambia**
(D70 compreso: lo scheduler legge le portate dei sette siti con la stessa chiamata `detection_range(mode, range_type)`, capitolo 3 §3.5). Il riferimento a `Logic/Air_Route_Manager.py` (import locale di `detection_probability`) era `:1099` dopo il 2026-11-04 e **ora è `:1103`** (+4: +3 per il commit `ed8d0fa3`, solo commenti e docstring, +1 per `efa8f353`, solo commento); aggiornato nei tre punti in cui compare.

**Nota 2026-11-13 (D-5, BI, VA, FP: il risolutore, la fire control e lo scheduler cambiano).** Da `f009eb43` (con la BI aggiunta il 2026-11-10) a `a389cadb` cambiano tre moduli di questa parte, **in contrasto con le note del 2026-11-04 e 2026-11-05 qui sopra, che restano vere alla loro data**: `Engagement_Resolver.py` (+697 righe, 3872 → 4569: D-5, VA, FP, più la BI già riportata), `Fire_Control.py` (+129, 1088 → 1217: BI e VA) e `Contact_Scheduler.py` (+84, 1578 → 1662: due primitive della VA).
Le **tabelle di fondo dei tre moduli sono rigenerate** con `inventario.py --tabella` (righe di `a389cadb`: 146, 36 e 63 righe; 17 simboli nuovi nel risolutore, 2 nello scheduler, nessuno nella fire control dopo la BI); i «Che cosa fa» e i «Chiamata da» dei 19 simboli nuovi sono scritti sul codice (i chiamanti con un'estrazione `ast` dei nomi chiamati, per i moduli del core letti; `ARM` = `Air_Route_Manager`, fuori dal core, usa `dwell_factor`).
**Diagrammi toccati**: D82 riscritto, D133 nuovo, D76/D77/D79/D83/D68 aggiornati nei nodi; **non toccati** D78, D80, D81, D84-D87, D67, D69-D75: i loro `:riga` nel testo restano a f009eb43 (sfasati). **Costanti**: nessuna costante FP (l'interruttore `FP_PER_PASS_DETECTION` è stato eliminato il 2026-11-13); `D5_DWELL_TIME`, `BI_AD_TARGET_RULE`, `VA_ENGAGEMENT_ALTITUDE_BAND` sono in §10A.4.
- **`registry_dwell_time` non è chiamata da nessuno nel core**: `Session_Simulator.engage` la passa **come valore** (`extra['dwell_time_for'] = ER.registry_dwell_time`, `:2793`) solo con `D5_DWELL_TIME` acceso, e la chiama il risolutore dietro il nome `dwell_time_for` (`_dwell_of`, `:2493`). Il «Chiamata da» della tabella lo dice così.
- **Differenza fra conteggi**: il testo di §10A.4 dava 127 simboli a `f009eb43` mentre la tabella ne aveva 129 (la BI ne aggiunge due: `_ad_domain`, `_admissible`); ora il testo e la tabella dicono 146.
