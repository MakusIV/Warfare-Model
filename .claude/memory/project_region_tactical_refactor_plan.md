---
name: project-region-tactical-refactor-plan
description: "Region.py refactor: extract 16 tactical functions (proposed by user) into new Tactical_Analysis.py (8 pure analysis functions) + existing Tactical_Evaluation.py (7 scoring functions), plus Context/Doctrine.py for weight config. 8-phase plan verified by Opus/high-effort Plan agent 2026-09-16 against real code. 4 design questions resolved by user. IMPLEMENTATION IN PROGRESS."
metadata:
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-16T17:04:51.200Z
---

# Region.py — refactoring strategico/tattico — piano verificato, implementazione in corso

**Origine**: proposta dell'utente (2026-09-16, sessione dopo il completamento del piano Fase 2 fog-of-war combat power, vedi [[project_fase2_recon_combat_power_plan]]). L'utente ha osservato che molte funzioni di `Region.py` sono di carattere strategico/tattico e non direttamente legate all'istanza Region, e vuole spostarle nei moduli dedicati `Strategical_Evaluation.py`/`Tactical_Evaluation.py`, mantenendo in Region solo le 8 funzioni sotto `# STRATEGIC CALCULATIONS`/`# PRIORITY UPDATES`. Ha esplicitamente richiesto di considerare che nel progetto mancano ancora: un analizzatore di informazioni strategiche/tattiche, un valutatore/decisore, e un pianificatore di missioni (centrale/stato-maggiore + regionale) — il refactoring deve predisporre basi pulite per questi componenti futuri, non solo spostare codice.

Analisi prodotta da un Plan agent Opus/high-effort che ha letto integralmente `Region.py`, `Strategical_Evaluation.py`, `Tactical_Evaluation.py`, i test e la memoria di progetto, verificando ogni riga citata e misurando in esecuzione costi di import e importabilità.

## Verifica della proposta — risultato chiave

**Nessuna delle 16 funzioni elencate dall'utente ha bisogno di un riferimento a `Region` non eliminabile passando i dati giusti come parametro.** Quindi lo spostamento è fattibile senza introdurre un ciclo di import `Logic → Context.Region → Logic`. Le 8 funzioni "STRATEGIC CALCULATIONS" (in realtà distribuite su due sezioni contigue: 5 sotto quel commento + 3 sotto "PRIORITY UPDATES" subito dopo — `calc_strategic_logistic_center`, `calc_combat_power_center`, `calc_total_warehouse`, `calc_total_production`, `calc_production_values`, `update_logistic_priorities`, `update_military_priorities`, `run_resource_management_cycle`) restano tutte in Region: scrivono `block_item.priority` o iterano `self._blocks`, sono operazioni sullo stato della regione, non valutazioni — confermato anche dall'intento originale del progetto (gli stub in Strategical_Evaluation.py erano già scritti per aggregare chiamate a metodi di Region, non per contenerli).

Correzione minore: `_calc_air_priority` chiama oggi `self.get_block_by_id(...)` in modo ridondante (l'informazione è già nel parametro ricevuto, come fa già `_calc_surface_priority`) — la firma va uniformata a `target_item: Tuple[float, Block]`, eliminando l'ultima dipendenza reale da `self`.

## Simmetria analizzatore/valutatore emersa dal codice (8+7)

Le 16 funzioni si dividono da sole in due gruppi con caratteristiche tecniche coerenti:

**Analizzatore (produce fatti, non punteggi) — 8 funzioni, nessuna tocca `self`, quasi nessuna ha cache:**
`get_target_report`, `_target_profile_from_block` (unica con `@lru_cache`), `_target_profile_from_report`, `_profile_to_weapon_distribution` (già `@staticmethod`), `_estimated_target_combat_power`, `_build_recon_cp_snapshot`, `_operative_aircraft_by_model`, `_representative_combat_power`.

**Valutatore (ritorna un punteggio float) — 7 funzioni, 6/7 hanno `@lru_cache`, qui sono tutte le dipendenze reali da `self`:**
`_select_weight`, `_calculate_priority`, `_calc_surface_priority`, `_calc_air_priority`, `_calc_attack_priority`, `_calc_defense_priority`, `_target_affinity`.

**Dottrina (configurazione):** `_validate_weight_priority_target` + `DEFAULT_WEIGHT_PRIORITY_TARGET` — né strategico né tattico, va in modulo dedicato.

**Pianificatore: 0 funzioni** — nessuna delle 16 sceglie un'azione o compone una missione, confermando che quel livello non esiste ancora in nessuna forma (il più vicino è `Air_Resources_Assigner.get_aircraft_mission`, ma quello *alloca* risorse a missioni già decise).

## Decisioni prese dall'utente (2026-09-16, tramite AskUserQuestion)

1. **Due moduli tattici separati** (non uno): nuovo `Tactical_Analysis.py` (8 funzioni di analisi, leggero) + `Tactical_Evaluation.py` esistente (+7 funzioni di scoring, pesante — importa `Aircraft_Data`+`skfuzzy`). Motivo misurato: `Aircraft_Data` costa 0.76s degli 0.87s di import di `Region.py`; con due moduli, `Region` può importare la parte leggera a livello di modulo e quella pesante lazy (dentro `update_military_priorities`), preservando il beneficio di import-lazy già ottenuto in `Combat_Power_Estimation.py`.
2. **Nuovo `Context/Doctrine.py`** per `DEFAULT_WEIGHT_PRIORITY_TARGET` + `validate_weight_priority_target` (non in coda a `Context.py`, già enorme).
3. **Stub in `Strategical_Evaluation.py`**: i 3 blocchi di codice-esempio morto (`ConflictGraph`/`PrioritySystem`/`if __name__=="__main__"`/il commento-saggio, righe ~37-210) vanno **eliminati**; gli 11 stub funzione (`evaluateTacticalReport` ecc., righe ~218-275) restano ma `pass` → `raise NotImplementedError(...)` (oggi ritornano silenziosamente `None`, un bug silenzioso in attesa; da tenere come documentazione dell'architettura voluta).
4. **Fase 6 (nucleo di scoring) avrà un test di caratterizzazione numerica prima/dopo**: uno scenario fisso il cui output di `update_military_priorities` viene confrontato bit-a-bit (entro tolleranza) prima e dopo il refactoring di quella fase specifica, oltre alla normale copertura dei test spostati.

Punti minori NON ri-chiesti esplicitamente all'utente, adottata la raccomandazione del piano stesso (basso rischio, reversibili):
- Nomenclatura: coesistenza `snake_case` (funzioni nuove) / camelCase legacy (`evaluateCombatSuperiority` ecc.) nello stesso modulo, nessuna rinomina in blocco (romperebbe `Test_Tactical_Evaluation.py:12`).
- `get_target_report` mantiene il nome pubblico anche da funzione di modulo (nonostante sia usata solo da `_target_profile_from_report`, oggi un alias di una riga) — la ridondanza resta segnalata ma non risolta in questa fase.

## Estensioni verificate alla proposta originale

- **`get_recon_reports` (non nell'elenco utente) resta in Region** — query sui blocchi di questa regione, come `get_blocks_by_criteria`. `_build_recon_cp_snapshot` (che si sposta) cambia firma: **non riceve più `observed_side`, riceve `reports: List[Dict]` già recuperati** dal chiamante (`Region.update_military_priorities` chiama `self.get_recon_reports(...)` e passa il risultato). Il guard `side=='Neutral'` non può più stare nella funzione pura (non ha più un `side`) — resta in Region, dove c'è già il guard primario.
- **`_get_tuple_hashable_block_item` si ELIMINA del tutto** (non "va da qualche parte"): esisteva solo per rendere hashabili gli argomenti delle funzioni `@lru_cache`d; se la cache sparisce (v. sotto), sparisce anche lui — bonus verificato: era chiamato dentro un loop O(n) per ogni blocco amico, quindi eliminarlo toglie anche un costo O(n²) nascosto.
- **`_is_logistic_block` resta in Region**, ricollocata accanto a `update_logistic_priorities` (unico chiamante).
- **`_target_profile_from_block` legge oggi `target_block._assets` (privato di Block)** — nel trasloco va corretto in `block.assets` (property pubblica già esistente, `Block.py:336-339`); i test che fanno `self.target_block._assets = {...}` continuano a funzionare (stesso dict).
- **Import morti da rimuovere nell'occasione** (verificati, 1 sola occorrenza = l'import stesso): `MIN_VALUE`, `field`, `defaultdict` in Region.py.
- **Codice morto da eliminare**: due blocchi `""" superata """` dentro il file (vecchie versioni di `_calc_surface_priority`/`_calc_air_priority`, ~130 righe) — segnalati come falso allarme di duplicazione in una sessione precedente, ora da cancellare fisicamente nell'occasione del refactoring.

## Il problema del caching — risolto

**7 delle 16 funzioni hanno `@lru_cache` su metodo bound.** Verificato che è già oggi più dannoso che utile: cache condivisa fra TUTTE le istanze Region (non una per regione, perché è sulla funzione di classe), `_invalidate_caches()` la svuota quasi a ogni iterazione di `update_military_priorities` (quindi il hit-rate reale è basso), e 5 punti nei test bypassano già la cache con `.__wrapped__` per avere risultati prevedibili.

**Decisione: eliminare tutte le `@lru_cache` dalle funzioni spostate.** `self._recon_cp_snapshot` (oggi attributo di istanza con try/finally in `update_military_priorities`) diventa una variabile locale passata esplicitamente come parametro (`recon_cp_snapshot: Optional[Dict[str,float]]`) — il flag `use_recon: bool` che oggi attraversa 5 firme sparisce, sostituito dalla presenza/assenza del dict stesso (`None`=ground truth, `{}`=sweep eseguito ma nulla osservato). Motivazione principale: un futuro pianificatore che valuta scenari ipotetici ("what-if") ha bisogno di contesti di valutazione isolati — con lru_cache condivisa, due valutazioni ipotetiche sugli stessi blocchi darebbero la stessa risposta congelata. Le due memoizzazioni potenzialmente utili (`_target_profile_from_block`, `_target_affinity`) si reintroducono SOLO se una misura post-refactoring dimostra un regresso di performance reale — non preventivamente.

**Vincolo di import verificato** (misurato in esecuzione): import di `Context.Region` 0.87s, di cui `Aircraft_Data` da solo 0.76s (tirato dentro dalla sola `_target_affinity`); `Tactical_Evaluation.py` costerebbe altri 0.63s (0.28s dei quali `skfuzzy`). Region deve importare **solo** il modulo leggero (`Tactical_Analysis.py`, + `Context`/`Combat_Power_Estimation`) a livello di modulo; il modulo pesante (`Tactical_Evaluation.py`) va importato **lazy**, dentro `update_military_priorities` — stesso pattern già usato in `Combat_Power_Estimation.py`.

## Piano di migrazione — tabella sintetica (dettaglio completo nel report dell'agente, non ripetuto qui)

| Funzione | Destinazione | Note principali |
|---|---|---|
| `_profile_to_weapon_distribution` | `Tactical_Analysis.py` | già `@staticmethod`, firma invariata |
| `get_target_report` | `Tactical_Analysis.py` | mantiene nome pubblico |
| `_target_profile_from_report` | `Tactical_Analysis.py` | oggi alias di una riga |
| `_estimated_target_combat_power` | `Tactical_Analysis.py` | firma invariata |
| `_operative_aircraft_by_model` | `Tactical_Analysis.py` | |
| `_representative_combat_power` | `Tactical_Analysis.py` | firma invariata |
| `_target_profile_from_block` | `Tactical_Analysis.py` | `@lru_cache` rimossa, `_assets`→`assets` |
| `_build_recon_cp_snapshot` | `Tactical_Analysis.py` | firma cambia: `reports` invece di `observed_side`, guard Neutral resta in Region |
| `_target_affinity` | `Tactical_Evaluation.py` | `@lru_cache` rimossa, porta `_AFFINITY_MIN/_MAX` + import `Aircraft_Data` |
| `_select_weight` | `Tactical_Evaluation.py` | `@lru_cache` rimossa, `weight_priority_target` come parametro, `BlockCategory`→`Context.BLOCK_CATEGORY` |
| `_calculate_priority` | `Tactical_Evaluation.py` | `@lru_cache` non c'era; `use_recon`→`recon_cp_snapshot: Optional[Dict]` |
| `_calc_surface_priority` | `Tactical_Evaluation.py` | `@lru_cache` rimossa |
| `_calc_air_priority` | `Tactical_Evaluation.py` | `@lru_cache` rimossa, `target_block`→`target_item: Tuple[float,Block]` (elimina `get_block_by_id`) |
| `_calc_attack_priority` | `Tactical_Evaluation.py` | `@lru_cache` rimossa, `route_provider: Callable[[str,str],Optional[Route]]` sostituisce l'accesso diretto a `self.get_shortest_route` |
| `_calc_defense_priority` | `Tactical_Evaluation.py` | idem, MAI riceve `recon_cp_snapshot` (ramo difesa sempre ground-truth) |
| `_validate_weight_priority_target` | `Context/Doctrine.py` | con `DEFAULT_WEIGHT_PRIORITY_TARGET` |

Elementi non-funzione: `MILITARY_CATEGORY_TO_FORCE`→`Context.py` (accanto a `MILITARY_CATEGORY`); `TargetProfile`→`Tactical_Analysis.py` (aggiornare riferimenti in `Context.py:312`, `Aircraft_Data.py:832,872`); `_AFFINITY_MIN/_MAX`→con `_target_affinity`; `DEFAULT_WEIGHT_PRIORITY_TARGET`+validatore→`Context/Doctrine.py`; `DEFAULT_ATTACK_WEIGHT` e `BlockCategory` restano in Region.py.

Stima dimensionale: `Region.py` scende da 1678 a ~950-1000 righe.

## Impatto sui test

`Test_Region.py`: 171 test in 21 classi. **~88 test (51%) si spostano** in nuovo `Test_Tactical_Analysis.py` (~66 test, 8 classi) e ampliamento di `Test_Tactical_Evaluation.py` (~24 test, 6 classi in arrivo — oggi quel file ha una sola classe di test reale). La riscrittura è in gran parte meccanica (`self.region._foo(args)` → `tactical_module.foo(args)`, le fixture non cambiano) e 5 test *migliorano* perdendo il bypass `__wrapped__` della cache che non serve più. `TestUpdateMilitaryPrioritiesUseRecon` e il test di cache-invalidation restano in Region (adattati). Baseline da misurare prima di iniziare con `.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"` (attesa: 2516 test, l'ultima misurata a fine Fase 5 del piano combat-power).

## Piano in 8 fasi (indipendentemente committabili, rischio crescente)

- **Fase 0** — pulizia `Strategical_Evaluation.py` (rischio nullo, indipendente da tutto).
- **Fase 1** — vocabolario/dottrina condivisi: `MILITARY_CATEGORY_TO_FORCE`→Context.py, nuovo `Context/Doctrine.py`, rimozione import morti. Prerequisito delle fasi 5-6.
- **Fase 2** — le 6 funzioni di analisi completamente disaccoppiate (no cache, no self): `_profile_to_weapon_distribution`, `get_target_report`, `_target_profile_from_report`, `_estimated_target_combat_power`, `_operative_aircraft_by_model`, `_representative_combat_power` → `Tactical_Analysis.py`. Nasce `Test_Tactical_Analysis.py`.
- **Fase 3** — `_target_profile_from_block` (cache + incapsulamento `_assets`→`assets`, isolata per via dei 12 test dedicati).
- **Fase 4** — `_build_recon_cp_snapshot` (cambio firma, guard Neutral spostato in Region).
- **Fase 5** — `_target_affinity` (rimozione cache su funzione costosa — qui si misura se serve reintrodurre memoizzazione di contesto; porta fuori `Aircraft_Data` da Region, beneficio import misurabile 0.87s→~0.15s; introduce l'import lazy di `Tactical_Evaluation` in Region).
- **Fase 6** — il nucleo di scoring (`_select_weight`, `_calculate_priority`, `_calc_surface_priority`, `_calc_air_priority` insieme, sono una catena di chiamate mutue): introduzione parametri espliciti, `use_recon`→`recon_cp_snapshot`, cambio firma `_calc_air_priority`. **CON test di caratterizzazione numerica prima/dopo** (deciso dall'utente).
- **Fase 7** — `_calc_attack_priority`/`_calc_defense_priority` + riscrittura `update_military_priorities` (route_provider, eliminazione `_get_tuple_hashable_block_item`, svuotamento ramo "priority" di `_invalidate_caches`).
- **Fase 8** — pulizia finale Region.py (eliminazione docstring `""" superata """` morte, ricollocazione `_is_logistic_block`, riordino sezioni).

## Stato di avanzamento

- **Fase 0 — FATTA** (commit 1e4af9e1): `Strategical_Evaluation.py` reso importabile, codice-esempio morto rimosso, stub → `NotImplementedError`. Suite 2516 OK invariata.
- **Fase 1 — FATTA**: `MILITARY_CATEGORY_TO_FORCE` spostato in `Context.py` (accanto a `MILITARY_CATEGORY`); nuovo `Context/Doctrine.py` con `DEFAULT_WEIGHT_PRIORITY_TARGET` + `validate_weight_priority_target` (funzione standalone, non più metodo `Region._validate_weight_priority_target` — il setter `weight_priority_target` ora chiama `Doctrine.validate_weight_priority_target(value)` direttamente); rimossi import morti (`MIN_VALUE`, `field`, `defaultdict`) da `Region.py`. Nuovo `Test_Doctrine.py` (7 test, il test esistente spostato + 2 nuovi: struttura mancante attack/defense, default valido). Suite completa: **2522 OK/5 skipped** (2516-1+7). Da committare nello stesso turno in cui questa memoria viene aggiornata.

## Prossimi passi

Fase 2 (le 6 funzioni di analisi completamente disaccoppiate → nuovo `Tactical_Analysis.py`), poi Fase 3 (`_target_profile_from_block`), Fase 4 (`_build_recon_cp_snapshot`), Fase 5 (`_target_affinity`), Fase 6 (nucleo di scoring, con test di caratterizzazione numerica), Fase 7 (`_calc_attack_priority`/`_calc_defense_priority` + `update_military_priorities`), Fase 8 (pulizia finale). Suite verde ad ogni commit.
