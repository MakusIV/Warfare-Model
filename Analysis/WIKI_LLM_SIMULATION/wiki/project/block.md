---
title: "Block"
type: project-module
tags: [package-python, block, military, combat-power, fog-of-war, dcs]
created: 2026-09-18
updated: 2026-09-25
code_paths: [Code/Dynamic_War_Manager/Source/Block/Block.py, Code/Dynamic_War_Manager/Source/Block/Military.py, Code/Dynamic_War_Manager/Source/Block/Production.py, Code/Dynamic_War_Manager/Source/Block/Storage.py, Code/Dynamic_War_Manager/Source/Block/Transport.py, Code/Dynamic_War_Manager/Source/Block/Urban.py]
related_decisions: ["[[combat-power-priority-redesign]]", "[[region-tactical-strategic-refactor]]", "[[virtual-session-engine-des]]", "[[nebbia-di-guerra-ricognizione]]", "[[allocazione-munizioni-sam]]", "[[gerarchia-unita-militari]]"]
related: ["[[component]]", "[[context-foundation]]"]
---

## Scopo

Il sottosistema `Block` rappresenta le unità territoriali/logistiche che compongono una `Region`
nella campagna: basi militari, impianti produttivi, magazzini, nodi di trasporto e centri urbani.
Ogni `Block` possiede un insieme di `Asset` (veicoli, navi, aerei, strutture), un `Resource_Manager`
(composizione 1:1, v. [[component]]) per la gestione economica, uno `State` per salute/successo, e
produce report di ricognizione (`get_recognition_report`) usati dal resto del modello — in
particolare da `Region`/`Logic.Tactical_Analysis` — per calcolare metriche aggregate (morale,
efficienza C2, efficienza di ricognizione, stima fog-of-war del combat power nemico, ecc.).

`Military` è la specializzazione con capacità di combattimento (potenza di fuoco, portata di tiro,
difesa aerea, stato di combattimento) e partecipa direttamente alla catena
attacco/difesa/priorità descritta in [[combat-power-priority-redesign]] e
[[region-tactical-strategic-refactor]]. `Production`, `Storage`, `Transport`, `Urban` dovrebbero
essere le altre specializzazioni (economica, logistica, civile) ma restano — invariato rispetto al
vecchio audit — stub non funzionanti.

**Nota sullo stato di questa pagina**: sostituisce l'audit `Analysis/Modules/06_Block.md`
(2026-08-16), ormai superato su più punti concreti: nel frattempo sono stati corretti due bug
segnalati come "confermati" da quell'audit (`get_military_category`, il dispatch senza parentesi in
`time2attack`), è stato rimosso `Block.get_recon_efficiency` (dead code, v. Note), `Military.combat_power`
è stato riscritto per rispettare davvero il contratto `(force, action) -> float`, ed è stata
aggiunta la logica di split delle liste di priorità per `mil_category`. Ogni affermazione qui sotto
è stata riverificata a fronte del sorgente attuale e della suite di test reale, non copiata dal
vecchio documento.

## File e classi principali

| File | Righe | Stato |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Block/Block.py` | 696 | Implementato e testato (91 test) |
| `Code/Dynamic_War_Manager/Source/Block/Military.py` | 615 | Implementato e testato (92 test), con bug residui su percorsi Naval_Base |
| `Code/Dynamic_War_Manager/Source/Block/Production.py` | 45 | Stub non funzionante, invariato |
| `Code/Dynamic_War_Manager/Source/Block/Storage.py` | 45 | Stub non funzionante, invariato |
| `Code/Dynamic_War_Manager/Source/Block/Transport.py` | 46 | Stub non funzionante, invariato |
| `Code/Dynamic_War_Manager/Source/Block/Urban.py` | 45 | Stub non funzionante, invariato |
| `Code/Dynamic_War_Manager/Source/Block/__init__.py` | 0 | vuoto |

Verificato con esecuzione reale (`.direnv/python-3.12/bin/python3 -m unittest discover -s
Code/Dynamic_War_Manager/Source/Test -p "Test_Block.py"` → 91 test OK; stesso comando con
`Test_Military.py` → 92 test OK). La suite completa del progetto è **2519 test OK (5 skipped)**.

### `Block.py`

- **`BlockParams`** (dataclass): contenitore di parametri, ancora non referenziato nel corpo della
  classe — invariato, probabile codice vestigiale.
- **`Block.__init__(name, description, side, category, sub_category, functionality, value,
  region)`**: crea `State("Block", id)` e `Resource_Manager(block=self)`; `value` vincolato in
  `[1, 10]`.
- Property standard con getter/setter validati: `name`, `id`, `side`, `category`, `sub_category`,
  `functionality`, `value`, `state`, `resource_manager`, `region`, `events`, `assets`.
- **Doppio criterio di validazione tra `assets` (setter) e `set_asset`**: il setter di `assets`
  valida con `validate_class(asset, "Asset")` (basato su MRO, supporta subclassi reali), mentre
  `set_asset(key, asset)` valida con `asset.__class__.__name__ != 'Asset'` — un controllo letterale
  che fallirebbe per `Vehicle`/`Ship`/`Aircraft` reali (sottoclassi di `Asset`, non istanze dirette).
  **Ancora presente**, incoerenza non risolta dal vecchio audit.
- **`position`**: centroide (`mean_point`) delle posizioni degli asset non-`None`.
- **`morale`**: `evaluateMorale(mean_success_ratio, efficiency)`; `0.0` se non ci sono asset o se
  ratio/efficiency ≤ 0.
- **`efficiency`**: media (`numpy.mean`) delle efficienze di tutti gli asset (nessun filtro
  `is_operative`).
- **`enemy_side()`**: deprecato (`DeprecationWarning`), redirige a `enemySide()` di `Utility`; nuovo
  **`is_enemy(side)`** confronta direttamente `side == enemySide(self._side)`.
- **`get_recognition_report(region_c2_recon_efficiency=None)`**: il metodo più complesso del
  modulo. Calcola probabilità di rilevamento per campo (`calcProbability`, pesate dall'efficienza
  C2/ricognizione della regione) e oscura (`None`) i dati non "rilevati". Classifica dimensione
  (Big/Medium/Small) via la funzione **unificata** `Context.classify_asset_dimension` (condivisa con
  `Logic.Tactical_Analysis.target_profile_from_block` per la via ground-truth, v.
  [[context-foundation]]) — non più la logica ad hoc per-classe descritta dal vecchio audit.
  Include ancora, invariati:
  - il campo `'intelligence'` (`self.intelligence() if hasattr(...) else None`): **sempre `None`
    in pratica**, nessuna sottoclasse implementa `intelligence()` — ma la conseguenza segnalata dal
    vecchio audit (test rotto in `Test_Region.py` per `get_region_intelligence_efficiency`) è
    **risolta**: quel metodo è stato **rimosso da `Region.py`** (opzione "b" delle proposte del
    vecchio audit), niente più riferimenti a `intelligence` in `Region.py`/`Test_Region.py`.
  - una docstring-blocco (righe iniziali del metodo) con una versione duplicata/vecchia della
    struttura dati, non più sincronizzata col dizionario reale — stessa incoerenza segnalata dal
    vecchio audit, non ripulita.
  - `hasattr(self, 'combat_volume')`, `hasattr(self, 'air_defense_aaa_range')`,
    `hasattr(self, 'air_defense_aaa_volume')`: nessuno di questi tre metodi è definito né in `Block`
    né in `Military` — i tre campi del report restano sempre `None` (nessun crash grazie a
    `hasattr`). Invariato dal vecchio audit.

### `Military.py` (estende `Block`)

- **`__init__(mil_category, ...)`**: prefissa il nome con `"Military."`, valida `mil_category`
  contro l'unione dei valori di `MILITARY_CATEGORY`; nuovo attributo `_weapons_availability`
  (scorte munizioni per loadout, `None` = non modellato) non presente nel vecchio audit.
- **`get_asset_list(asset_class, asset_type, asset_state)`**: invariato, filtro combinato,
  ritorna `{classe: {tipo: [asset,...]}}` o `None` con `logger.warning` per filtro non valido.
- **`combat_power(force, action)`** — **riscritto rispetto al vecchio audit**: ora rispetta
  davvero il contratto dichiarato, mirror di `Mobile.combat_power(force, action)` — `float` se
  entrambi gli argomenti sono dati (somma su `asset.combat_power(force, action)` per gli asset
  operativi), `Dict` altrimenti. Il bug storico ("dichiara float, ritorna sempre un dict annidato")
  è stato corretto nella Fase 0 del redesign combat-power (v. [[combat-power-priority-redesign]]).
- **`get_military_category()` — bug RISOLTO** (commit `b38bab1f`, verificato a HEAD): le tre
  condizioni ora chiamano correttamente `self.is_Air_Base()` / `self.is_Ground_Base()` /
  `self.is_Naval_Base()` **con le parentesi**; test di regressione dedicato presente
  (`Test_Military.py::test_get_military_category`). Il vecchio audit segnalava questo come bug
  "confermato" (ritorno sempre `"Naval_Base"`) — non più vero.
- **`time2attack(target, route, speed)` — bug RISOLTO**: il dispatch `if self.is_Air_Base() and
  target: ... elif (self.is_Ground_Base() or self.is_Naval_Base()) and route: ...` ora chiama
  correttamente i metodi (con parentesi). Il vecchio audit segnalava lo stesso pattern di bug di
  `get_military_category()` qui — anche questo risulta corretto a HEAD, pur senza un test dedicato
  esplicito per il dispatch stesso.
- **`_is_attack_asset(asset)` — bug ANCORA PRESENTE**: il terzo ramo
  `elif self.is_helibase() and validate_class(asset, "Aircraft")` chiama un metodo `is_helibase()`
  **mai definito** (verificato: unico riferimento nel repo è questo call-site). Per un blocco
  `Naval_Base` (dove `is_Ground_Base()`/`is_Air_Base()` sono `False`) la valutazione solleva
  `AttributeError` non appena si valuta un asset. Nessun test in `Test_Military.py` copre
  `_is_attack_asset`/`_get_attack_speeds` per `Naval_Base` — confermato con grep mirato, il bug non
  è testato né corretto.
- **`get_recon_efficiency()`**: mediana delle efficienze degli asset con
  `role == Asset_Role.RECONNAISSANCE.value`. Ora è l'**unica** implementazione nel sottosistema
  (v. sezione Note) — non più "override" nel senso del vecchio audit, dato che la versione in
  `Block.py` è stata rimossa. **Nuovo consumatore 2026-09-25**: `Logic.Engagement_Resolver.
  region_recon_detection_factor` la usa per modulare `unseen_factor` della nebbia di guerra nel
  risolutore, aggregando per **massimo** fra le `Military` dello stesso lato in una regione (non
  per media) — v. [[nebbia-di-guerra-ricognizione]].
- **`get_c2_efficiency()`**: mediana delle efficienze degli asset con `role == Asset_Role.C2.value`,
  filtrati per `is_operative()`. Invariato, confermato valido.
- **`air_defense_volume() -> List[Cylinder]`**: delega a `Mobile.air_defense_volume()` su ogni
  `Vehicle`/`Ship` operativo. Invariato, confermato valido (fa parte del lavoro 2026-05-22, v.
  memoria `project_asset_military_2026_05_22`).
- **`combat_range() -> Optional[Tuple[max_range, med_range, ratio, quantity]]`**: itera gli asset
  operativi con metodo `combat_range`. Invariato, confermato valido.
- **`air_defense_threats() -> List[ThreatAA]` e `detection_range(mode, sensor) -> Optional[Tuple[max, med, ratio, quantity]]` — nuovi 2026-09-22 (Fase 2 motore sessioni virtuali, v. [[virtual-session-engine-des]])**: pendant a livello Block dei corrispondenti metodi `Mobile`. `air_defense_threats()` chiama la fabbrica `Logic.Air_Route_Manager.build_threat_aa(asset)` (import locale al metodo, per non far dipendere `Block` da `Logic` a tempo di import) su ogni `Vehicle`/`Ship` operativo — un `ThreatAA` per asset AD, non solo la geometria come `air_defense_volume()`. `detection_range()` aggrega `Mobile.detection_range()` con la stessa forma statistica (max/mediana/rapporto/quantità) di `combat_range()`.
- **`air_defense_power() -> float` — nuovo 2026-09-22 (Q3 delle "3 questioni aperte", v. [[virtual-session-engine-des]])**: in [0,1], `1 − Π(1 − danger_level_i)` sui `ThreatAA` di `air_defense_threats()` ("almeno una delle difese è efficace"). Non è una combat power e non è confrontabile con `combat_range()`/`combat_state()`: SAM/AAA/EWR restano a combat power 0 **per definizione** in `Context.GROUND_COMBAT_EFFICACY` (misura fuoco/manovra terra-terra, che questi asset non hanno) — questa è la dimensione separata che cattura la loro potenza reale. **Collegata alla priorità di targeting SEAD il 2026-09-22** (v. [[virtual-session-engine-des]]): `Tactical_Evaluation.calculate_priority` la legge quando l'attaccante è aereo e il bersaglio ha combat power 0. Ancora nessun consumatore per il risolutore d'ingaggio aria-superficie (Fase 4).
- **`combat_state() -> Optional[float]`**: formula `(0.3 * operative_efficiency + 0.7 *
  c2_efficiency) * ratio_operative`. Invariato, confermato valido, coerente con la memoria
  2026-05-22.
- **`intelligence()`**: resta **deliberatamente commentato** (non implementato) — stesso commento
  del vecchio audit ("c'è c2_efficiency, più pertinente"); v. sezione Note per l'impatto (risolto)
  su `Region`.
- **`get_recognition_report()`**: override "vuoto" — aggiorna lo `state` e delega interamente a
  `super().get_recognition_report(...)`. Invariato.
- **Partecipazione al fog-of-war (`use_recon`)**: `Military` non ha logica propria di
  ricognizione stimata — il lavoro vive in `Logic.Tactical_Analysis`/`Tactical_Evaluation` e in
  `Context.Combat_Power_Estimation` (v. [[combat-power-priority-redesign]]). Il contributo di
  `Military` alla catena è duplice: (1) `combat_power(force, action)` come float diretto è il punto
  di lettura ground-truth usato da `_representative_combat_power`/`Tactical_Evaluation`; (2)
  `get_recognition_report()` (via `Block`) produce l'`asset_summary` `{asset_type: {dimensione:
  conteggio}}` che alimenta `Combat_Power_Estimation.estimate_combat_power_from_asset_summary`
  quando `use_recon=True`. `Region.run_resource_management_cycle` chiama comunque
  `update_military_priorities(side=side)` **senza** `use_recon=True` — verificato a HEAD, resta
  sempre ground-truth in produzione.
- **Split priorità per `mil_category`**: `Military.mil_category` (già presente prima) è la chiave
  usata da `Region.get_blocks_by_criteria(..., mil_category=...)` e
  `Region.get_priority_lists_by_mil_category(side, sort_by)` (implementate 2026-09-14, commit
  `3fe680c4`) per separare le liste di priorità per scala/ruolo (Battallion, Regiment, Airbase,
  ...) — nessuna modifica a `Military.py` stesso è stata necessaria, il dato esisteva già.

### `Production.py`, `Storage.py`, `Transport.py`, `Urban.py`

**Invariati rispetto al vecchio audit — riverificati a HEAD, stessi identici problemi.** Firma
tipica (es. `Production.__init__`):

```python
def __init__(self, block: Block, mil_category: str, name: str|None, side: str|None,
             description: str|None, category: str|None, sub_category: str|None,
             functionality: str|None, value: int|None, acp: Payload|None,
             rcp: Payload|None, payload: Payload|None, region: Region|None):
    super().__init__(name, description, side, category, sub_category, functionality, value, acp, rcp, payload)
    ...
    check_results = self.checkParam(mil_category)
```

Problemi confermati ancora presenti, identici al vecchio audit:
1. `super().__init__(...)` passa più argomenti posizionali di quelli accettati dall'attuale
   `Block.__init__` (8 parametri dopo `self`) → `TypeError` immediato a ogni istanziazione reale.
2. Chiamano `self.checkParam(mil_category)`, metodo mai esistito né in `Block` né in queste classi.
3. Il parametro `block` non viene mai assegnato a `self`.
4. `region` è dichiarato ma mai passato a `super().__init__()`.

Nessun file di test esiste per questi 4 moduli. Ultimo commit che li tocca resta quello segnalato
dal vecchio audit (>1 anno fa) — nessuna evoluzione nel frattempo, nonostante `Block.py`/
`Military.py` abbiano ricevuto refactoring sostanziali.

## Dipendenze

- `Component/Resource_Manager.py` (composizione 1:1 in `Block`, v. [[component]])
- `Utility/Utility.py`: `validate_class`, `setName`, `setId`, `mean_point`, `evaluateMorale`,
  `enemySide`, `calcProbability`
- `Context/Context.py`: `BLOCK_CATEGORY`, `SIDE`, `Ground_Vehicle_Asset_Type`, `Sea_Asset_Type`,
  `Air_Asset_Type`, `classify_asset_dimension` (v. [[context-foundation]] — sostituisce la logica
  dimensionale ad hoc del vecchio audit), `GROUND_ACTION`, `AIR_TASK`, `SEA_TASK`,
  `MILITARY_CATEGORY`, `MILITARY_FORCES`, `ACTION_TASKS`, `Asset_Role`
- `DataType/Route.py` (usato da `Military.time_to_ground_intercept`)
- `Logic/Air_Resources_Assigner.py` (import **locale**, dentro `get_available_loadouts`, per
  evitare un import circolare — `Air_Resources_Assigner` importa `Block.Military` a livello di
  modulo)
- Solo `TYPE_CHECKING`: `Asset`, `Region` (in `Block.py`); `Region`, `Vehicle`, `Aircraft`, `Ship`,
  `Asset` (in `Military.py`) — nessuna dipendenza circolare a runtime, confermato ancora valido.
- Librerie esterne: `numpy` (`mean`, `median`), `sympy` (`Point`, `Point2D`, `Point3D`), `heapq`
  (importato in `Military.py` ma **ancora non utilizzato** nel corpo del file)

## Stato attuale

| File | Stato | Copertura test |
|---|---|---|
| `Block.py` | Completo e funzionante | `Test_Block.py`: **91 test, tutti OK** |
| `Military.py` | Funzionante per i percorsi testati; bug residuo su `Naval_Base`/`_is_attack_asset` | `Test_Military.py`: **92 test, tutti OK** |
| `Production.py` / `Storage.py` / `Transport.py` / `Urban.py` | Non funzionanti (stub pre-refactoring, invariati) | Nessun test |

Comando eseguito e confermato in questa sessione:
```
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Block.py"
→ Ran 91 tests — OK
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Military.py"
→ Ran 92 tests — OK
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"
→ Ran 2519 tests — OK (skipped=5)
```

### Bug noti residui (con file:riga)

1. **`Military.py:448`** (`_is_attack_asset`) — chiama `self.is_helibase()`, mai definito.
   `AttributeError` per qualsiasi blocco `Naval_Base` non appena si valuta un asset. Impatta
   `_get_attack_speeds()`/`time_to_direct_line_attack()`/`time2attack()` per basi navali. Non
   testato, non corretto.
2. **`Block.py`** (`set_asset` vs. setter `assets`) — due criteri di validazione del tipo asset
   diversi e potenzialmente incoerenti con le sottoclassi reali (`Vehicle`, `Ship`, `Aircraft`,
   `Structure`). Non corretto.
3. **`Block.py`** — campo `'intelligence'` del report di ricognizione sempre `None` (nessuna
   sottoclasse implementa `intelligence()`) — comportamento voluto/accettato, non un bug attivo
   (il consumer lato `Region` che ne soffriva è stato rimosso).
4. **`Block.py`** (`combat_volume`, `air_defense_aaa_range`, `air_defense_aaa_volume`) — nessuno di
   questi tre metodi è implementato in `Block` o `Military`; i campi risultanti nel report restano
   sempre `None`. Non corretto.
5. **`Production.py`/`Storage.py`/`Transport.py`/`Urban.py`** — non istanziabili (`TypeError` poi
   `AttributeError` su `checkParam`). Invariato dal vecchio audit.

### Bug del vecchio audit RISOLTI (non più presenti)

- ~~`Military.py` — `get_military_category()` sempre `"Naval_Base"` per assenza di parentesi~~ →
  corretto (commit `b38bab1f`), test di regressione presente.
- ~~`Military.py` — `time2attack()` stesso pattern di bug senza parentesi~~ → corretto a HEAD.
- ~~`Military.py` — `combat_power()` dichiara `float` ma ritorna sempre un dict annidato~~ →
  riscritto per rispettare davvero il contratto (Fase 0 del redesign combat-power).
- ~~`Block.py` — campo `intelligence` sempre `None` rompe `Test_Region.py` via
  `get_region_intelligence_efficiency`~~ → il metodo è stato rimosso da `Region.py`, nessun test
  rotto residuo.

## Decisioni architetturali rilevanti

- [[combat-power-priority-redesign]] — riscrittura di `Military.combat_power`, aggiunta di
  `air_defense_volume`/`combat_range`/`combat_state`/`get_c2_efficiency`, e ruolo di
  `get_recognition_report` come sorgente dell'`asset_summary` consumato dalla stima fog-of-war
  quando `Region.update_military_priorities(side, use_recon=True)`.
- [[region-tactical-strategic-refactor]] — sposta la logica di calcolo priorità/estrazione target
  fuori da `Region.py` in `Logic.Tactical_Analysis`/`Tactical_Evaluation`; `Block`/`Military`
  restano il livello dati/report, non calcolano più direttamente priorità.
- [[virtual-session-engine-des]] — `Military.air_defense_threats()`/`detection_range()` (Fase 2)
  sono il livello Block del motore DES per le sessioni virtuali; nessun consumatore reale li
  chiama ancora, verranno usati dal `Contact_Scheduler` (Fase 3).
- [[nebbia-di-guerra-ricognizione]] — nuovo consumatore di `get_recon_efficiency()` (v. sopra).
- [[allocazione-munizioni-sam]] — proposta (non ancora decisa) che interviene su
  `salvo_interceptors`/`interceptor_stock` per i SAM a pool condiviso.
- [[gerarchia-unita-militari]] — proposta (non ancora decisa) che conferma `Military` come unità
  atomica della gerarchia militare, senza modificarne l'implementazione.

## Note

- **`Block.get_recon_efficiency` rimosso** (2026-09-10, v. memoria
  `project_block_get_recon_efficiency_removed`): era shadowato in ogni percorso di produzione
  dalla versione in `Military` (`Region.get_region_recon_efficiency` interroga solo blocchi
  `BlockCategory.MILITARY`), quindi la versione in `Block` era dead code già segnalato da un
  TODO dello sviluppatore stesso (`#Nota: è iimplementata in Military: da togliere!?`). Unico
  effetto collaterale: le sottoclassi non-`Military` (`Production`/`Storage`/`Urban`/`Transport`,
  comunque mai istanziabili) ora restituirebbero `recon_efficiency: None` invece di un falso `0.0`
  in un ipotetico `get_recognition_report()`. `Test_Block.py` aggiornato di conseguenza (4 test
  rimossi, 1 assert corretta) — coerente con il conteggio attuale di 91 test (95 dell'audit
  precedente meno 4).
- `BlockParams` (dataclass, `Block.py`) resta non referenziata — verificare se serve ancora.
- Import inutilizzati residui: `heapq.heappop`/`heappush` in `Military.py` non risultano usati nel
  corpo del file.
