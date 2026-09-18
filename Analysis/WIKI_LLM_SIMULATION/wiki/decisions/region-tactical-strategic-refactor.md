---
title: "Estrazione tattica/strategica da Region.py"
type: decision
tags: [architecture, dwm, region, tactical, doctrine, refactoring]
created: 2026-09-18
updated: 2026-09-18
status: accepted
affects: ["[[context-state]]", "[[logic-decision]]"]
related: []
---

## Contesto

`Context/Region.py` aveva accumulato, oltre alla gestione dello stato di istanza (blocchi, rotte, cicli di produzione/priorità), 16 funzioni di natura schiettamente tattica: profilazione dei bersagli, stima del combat power in condizioni di fog-of-war, e l'intero nucleo di scoring delle priorità di attacco/difesa. Queste funzioni non avevano bisogno reale di un riferimento a `Region` non eliminabile — passavano già (o potevano passare) tutti i dati necessari come parametri — ma vivevano lì per accumulo storico, rendendo il file voluminoso (1678 righe) e mescolando due responsabilità distinte: orchestrazione dello stato regionale e valutazione tattica.

Il problema non era solo dimensionale: il progetto manca ancora di un analizzatore di informazioni strategiche/tattiche, di un valutatore/decisore e di un pianificatore di missioni (livello centrale/stato-maggiore + regionale) — componenti futuri che avrebbero dovuto consumare esattamente questo tipo di logica. Lasciarla dentro `Region` avrebbe reso più difficile costruire quei componenti senza un'ulteriore dipendenza circolare verso `Context.Region`.

Un'analisi approfondita (Plan agent, verifica riga per riga del codice reale, dei test e della memoria di progetto) ha confermato che le 16 funzioni si dividono naturalmente in due famiglie coerenti: 8 funzioni di **analisi** (producono fatti, non punteggi: nessuna tocca `self`, quasi nessuna aveva cache) e 7 funzioni di **valutazione** (ritornano un punteggio float; 6 delle 7 avevano `@lru_cache` — qui erano concentrate tutte le dipendenze reali residue da `self`).

## Decisione

Le 16 funzioni sono state estratte da `Region.py` in tre nuovi moduli, secondo la separazione analizzatore/valutatore/dottrina emersa dal codice:

- **`Logic/Tactical_Analysis.py`** (nuovo, leggero, nessun import pesante a livello di modulo) — le 8 funzioni di analisi pura: `get_target_report`, `target_profile_from_block`, `target_profile_from_report`, `profile_to_weapon_distribution`, `estimate_target_combat_power` (`_estimated_target_combat_power`), `build_recon_cp_snapshot`, `operative_aircraft_by_model`, `representative_combat_power`.
- **`Logic/Tactical_Evaluation.py`** (esistente, "pesante" — importa `Aircraft_Data` e `skfuzzy`) — le 7 funzioni di scoring: `select_weight`, `calculate_priority`, `calc_surface_priority`, `calc_air_priority`, `calc_attack_priority`, `calc_defense_priority`, `target_affinity`.
- **`Context/Doctrine.py`** (nuovo) — la configurazione di dottrina: `DEFAULT_WEIGHT_PRIORITY_TARGET` e `validate_weight_priority_target` (prima un metodo privato `Region._validate_weight_priority_target`).

`Region.py` importa `Tactical_Analysis` a livello di modulo (leggero) e `Tactical_Evaluation` **lazy**, dentro `_calc_air_priority`/le funzioni che ne hanno davvero bisogno — stesso pattern già adottato in `Combat_Power_Estimation.py` — per non gravare sui chiamanti che non calcolano mai una priorità aerea.

`Region.py` è sceso da 1678 a **~908-923 righe** (verificato a HEAD: 923) e oggi contiene solo le 8 funzioni STRATEGIC CALCULATIONS/PRIORITY UPDATES che scrivono `block_item.priority` o iterano `self._blocks` — cioè operazioni sullo stato della regione, non valutazioni.

**Decisione collaterale, deliberata e non un effetto collaterale**: tutte le `@lru_cache` sulle funzioni spostate sono state **rimosse**, non riportate nei nuovi moduli. Verificato che a HEAD nessuna funzione in `Tactical_Analysis.py`/`Tactical_Evaluation.py` porta il decoratore (solo commenti che ne spiegano l'assenza).

## Motivazione

La rimozione della cache non è una scelta di stile ma di correttezza, per due ragioni verificate sul codice prima del refactoring:

1. **La cache era già più dannosa che utile.** `@lru_cache` su un metodo bound è condivisa fra **tutte** le istanze di `Region` (è sulla funzione di classe, non per-istanza); `_invalidate_caches()` la svuotava quasi a ogni iterazione di `update_military_priorities` (hit-rate reale basso); e 5 punti nei test bypassavano già la cache con `.__wrapped__` per ottenere risultati prevedibili — segno che la cache interferiva anche con la testabilità.
2. **Precondizione per un futuro pianificatore "what-if".** Un pianificatore che deve valutare scenari ipotetici (ad es. "cosa succede se attacco con questa configurazione?") ha bisogno di contesti di valutazione isolati. Con una `lru_cache` condivisa fra istanze/scenari, due valutazioni ipotetiche sugli stessi blocchi avrebbero prodotto la stessa risposta congelata — un bug di correttezza silenzioso, non solo un problema di performance.

Il flag `use_recon: bool`, che prima attraversava 5 firme di funzione, è stato eliminato insieme alla cache: `self._recon_cp_snapshot` (prima un attributo di istanza con gestione try/finally) è diventato un parametro esplicito `recon_cp_snapshot: Optional[Dict[str, float]]` — `None` significa ground-truth, `{}` significa "sweep eseguito ma nulla osservato". Questo elimina anche una combinazione patologica non più esprimibile (`use_recon=True` con snapshot ancora `None`).

Le due memoizzazioni potenzialmente utili dal punto di vista prestazionale (`target_profile_from_block`, `target_affinity`) sono state deliberatamente **non** reintrodotte in nessuna forma — la linea guida adottata è che si reintroducano solo se una misura post-refactoring dimostra un regresso di performance reale, mai preventivamente.

Sul piano organizzativo, la scelta di **due moduli tattici separati** (invece di uno solo) è motivata da un costo di import misurato: `Aircraft_Data` (tirato dentro solo da `target_affinity`) costa la parte dominante del tempo di import di `Tactical_Evaluation.py`. Separando analisi (leggera) da valutazione (pesante), `Region` può importare la prima a livello di modulo e la seconda solo quando serve davvero.

## Conseguenze

- `Region.py` gestisce ora solo stato di istanza e orchestrazione; tutta la logica di analisi/scoring tattico vive in `Logic/Tactical_Analysis.py` e `Logic/Tactical_Evaluation.py`; la dottrina in `Context/Doctrine.py`.
- Nessuna `@lru_cache` residua su funzioni di analisi o valutazione tattica in tutto il codice spostato — precondizione esplicita per un futuro pianificatore what-if.
- Il refactoring **non ha implementato** l'analizzatore di informazioni strategiche/tattiche di alto livello, il valutatore/decisore, né il pianificatore di missioni: questi restano stub `NotImplementedError` in `Strategical_Evaluation.py` (ripulito dal codice di esempio morto nella Fase 0 del piano). Ha però creato la separazione pulita analizzatore/valutatore/dottrina che quei componenti futuri consumeranno.
- Effetto collaterale positivo verificato: l'eliminazione della cache ha anche eliminato `_get_tuple_hashable_block_item` (esisteva solo per rendere hashabili gli argomenti delle funzioni cache-ate) e un costo O(n²) nascosto che ricreava quella tupla ad ogni iterazione di un loop.
- Refactoring completato in 8 fasi indipendentemente committabili, suite di test invariata a **2519 OK / 5 skipped** al termine (rispetto ai 2516 di partenza, riorganizzati non persi), con un test di caratterizzazione numerica end-to-end dedicato al nucleo di scoring (Fase 6) per garantire che il "cablaggio" fra le funzioni separate producesse lo stesso risultato di prima.

## Fonti

- [[project_region_tactical_refactor_plan]] (memoria di origine, piano completo in 8 fasi)
- [[project_fase2_recon_combat_power_plan]] (piano precedente che ha reso evidente l'esigenza di questo refactoring)
