---
title: "Nebbia di guerra nel risolutore: fattore di rilevamento da ricognizione"
type: decision
tags: [architecture, dwm, fog-of-war, combat-resolution, discrete-event, recon]
created: 2026-09-25
updated: 2026-09-25
status: accepted
affects: ["[[block]]", "[[context-state]]"]
related: ["[[virtual-session-engine-des]]", "[[risolutore-ingaggio-salva-fase4]]", "[[combat-power-priority-redesign]]", "[[c2-hierarchy-design]]"]
---

## Contesto

[[virtual-session-engine-des]] segnalava fra i possibili seguiti, a motore DES completo, il
"collegamento fog-of-war reale (`Region`/`recon_cp_snapshot`) a `detection_factor` (gap
documentato in S9)": lo scenario S9 verificava la nebbia di guerra parziale con una lambda di
test, non con una vera istantanea di ricognizione presa da `Region`. Il meccanismo di ricognizione
stimata esisteva già altrove ([[combat-power-priority-redesign]]: `Tactical_Analysis.
build_recon_cp_snapshot`, consumato da `Region.update_military_priorities` per il combat power
stimato del nemico), ma non era mai stato collegato al **rilevamento** nel risolutore d'ingaggio.

## Decisione

In `Logic/Engagement_Resolver.py`, accanto a `meteo_detection_factor`, tre nuove funzioni
costruttrici — **nessuna modifica al motore esistente**, chi non le passa ottiene lo stesso
comportamento di prima:

- **`recon_detection_factor_fn(seen_block_ids, *, observer_side, unseen_factor, seen_factor=1.0)`**:
  per gli osservatori di `observer_side`, ritorna `seen_factor` se `target.block.id` è tra i
  blocchi visti, altrimenti `unseen_factor`; un bersaglio del proprio lato o senza blocco vale
  `seen_factor`/`unseen_factor` secondo lo stesso criterio; per l'altro lato il fattore è 1.0
  (nessun effetto). Non consuma l'RNG di sessione — sposta solo la soglia di un'estrazione che il
  motore fa comunque.
- **`combine_detection_factors(*fns)`**: prodotto dei fattori (es. meteo × ricognizione), sempre
  clampato in [0,1].
- **`region_recon_detection_factor(region, observer_side, *, unseen_factor, seen_factor, relief)`**:
  scatta l'istantanea **una volta, prima della sessione** (coerente con la decisione utente di non
  avere nebbia di guerra dinamica/RNG nel motore), con la stessa ricetta già usata da
  `update_military_priorities`: `Tactical_Analysis.build_recon_cp_snapshot(region.get_recon_reports
  (enemySide(side)))`.

### `unseen_factor` modulato dall'efficienza di ricognizione dell'osservatore

Decisione utente (2026-09-25): `unseen_factor` non è una costante fissa unica, ma viene scalato da
`Military.get_recon_efficiency()` (mediana `asset.efficiency` degli asset con ruolo
`RECONNAISSANCE` di una singola `Military`, v. [[block]]):

```
unseen = unseen_factor + (seen_factor - unseen_factor) × RECON_EFFICIENCY_FOG_RELIEF × e
```

con `e` l'efficienza aggregata in [0,1] (`None` → 0). Costanti dichiarate come **stime**, da
ricalibrare: `UNSEEN_DETECTION_FACTOR = 0.5`, `RECON_EFFICIENCY_FOG_RELIEF = 0.5` (la ricognizione
recupera al massimo metà della penalità — un blocco non confermato non diventa mai equivalente a
uno confermato).

**Aggregazione su più `Military` dello stesso lato in una regione**: il **massimo**, non la media.
`Region.get_region_recon_efficiency` esistente (media, resta intatta) misura quanto la
ricognizione è *diffusa* nella forza; per il *cueing* di un'area basta un solo buon sensore — cinque
battaglioni corazzati più un ottimo squadrone da ricognizione darebbero 0.18 in media ma devono
"illuminare" l'area come se il buon sensore fosse l'unico presente. Limite dichiarato: il massimo
ignora la copertura geografica (un sensore lontano dal bersaglio pesa quanto uno vicino).

## Motivazione

Stessa disciplina già applicata al resto del motore DES ([[virtual-session-engine-des]],
[[risolutore-ingaggio-salva-fase4]]): nessuna modifica al motore esistente, solo funzioni
costruttrici opzionali; nessuna estrazione casuale nel percorso critico; riuso della ricetta di
snapshot già validata da `update_military_priorities` invece di inventarne una nuova; ogni costante
introdotta dichiarata esplicitamente come stima.

## Conseguenze

**Implementato e verificato 2026-09-25** (agente `des-developer`, Opus, effort medio; verifica
della sessione principale su suite completa). File toccati: `Logic/Engagement_Resolver.py`,
`Test/Test_Engagement_Resolver.py` (+28 test), `Test/Test_Session_Scenarios.py` (nuova classe
`TestS9RegionReconSnapshot`, +6 test — S9 esistente invariato). Suite completa: **3478 test OK
(skipped=5)**, +34 sulla baseline 3444.

**Verificato su S9 con una `Region` vera**, quattro varianti a parità di seed: tasso di rilevamento
Blue 0.948 (nessun fattore / bersaglio nella regione, identico) → 0.726 (bersaglio fuori regione ma
ricognizione dell'osservatore forzata a 1.0) → 0.496 (bersaglio fuori regione, ricognizione nulla).
Red resta 1.0 in ogni variante (fattore applicato solo al lato osservatore passato).

**Limiti noti, non risolti qui**:
- **La nebbia è "debole" con la ricetta ereditata da `update_military_priorities`**:
  `get_recognition_report` produce sempre un `block_id` per ogni `Military` nemica della regione;
  "non visto" scatta oggi solo per blocco fuori regione, non militare, `mil_category` non mappata,
  o asset senza blocco — non per un criterio più stringente (es. `position is None` nel report).
  Scelta deliberata per restare fedele alla ricetta esistente; un criterio più forte è
  un'estensione futura, non decisa qui.
- **Bug scoperto durante l'implementazione, non corretto**: `get_blocks_by_criteria(category=
  'Military')` scarta `Military` reali con `category=''` — v. [[context-state]] per il dettaglio.
  Aggirato nei test passando `category='Military'` esplicitamente.
- `get_recognition_report` usa `random` globale, ma solo nella costruzione dell'istantanea
  pre-sessione, fuori dal percorso del motore — non tocca l'RNG di sessione (v.
  [[virtual-session-engine-des]] vincolo #2).

## Fonti

- `.claude/memory/project_session_2026_09_25_summary.md` (memoria di origine)
- [[virtual-session-engine-des]] — gap S9 originario, architettura del motore entro cui la
  proposta deve stare
- [[combat-power-priority-redesign]] — origine della ricetta `build_recon_cp_snapshot` riusata qui
- `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py`,
  `Code/Dynamic_War_Manager/Source/Block/Military.py:498` (`get_recon_efficiency`) — stato attuale
  verificato nel codice
