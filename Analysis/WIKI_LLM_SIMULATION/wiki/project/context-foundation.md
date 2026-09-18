---
title: "Context — Fondamenta e Dati Iniziali"
type: project-module
tags: [package-python, context, enum, dottrina, combat-power, dcs]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Context/Context.py, Code/Dynamic_War_Manager/Source/Context/Initial_Context.py, Code/Dynamic_War_Manager/Source/Context/Actual_Context.py, Code/Dynamic_War_Manager/Source/Context/Logistic_Lines.py]
related_decisions: ["[[region-tactical-strategic-refactor]]", "[[c2-hierarchy-design]]", "[[combat-power-priority-redesign]]"]
related: ["[[context-state]]", "[[logic-decision]]"]
---

## Scopo

Il sottosistema CONTEXT-FOUNDATION fornisce il vocabolario di dominio (enum, costanti, tabelle
statiche, funzioni di classificazione/scoring condivise) usato da praticamente tutti gli altri
sottosistemi (Asset, Block, Context, Logic). Comprende:

- `Context.py`: la base concettuale — enum, costanti e funzioni pure condivise, senza alcuna
  dipendenza da altri moduli applicativi del progetto (solo `enum`, `typing`, `Logger`). È anche,
  da settembre 2026, l'unico punto in cui vive la formula di combat power condivisa fra
  ground-truth e stima fog-of-war (`combat_power_from_score`), oltre al vocabolario dimensionale
  unificato (`DIMENSION_CLASSES`, `classify_asset_dimension`) usato dalla pipeline
  recon → priorità → efficacia armi.
- `Initial_Context.py`: dati statici di inizializzazione campagna (quantità/produzione/riparazione
  iniziali di asset, disponibilità armamenti, template di regione).
- `Actual_Context.py`: (nominalmente) stato runtime attuale della campagna, in gran parte una
  copia di `Initial_Context.py` con l'aggiunta di contatori di missione.
- `Logistic_Lines.py`: gestione delle linee logistiche (collegamento server↔trasporto↔cliente tra
  Block), pensato per la ridistribuzione delle risorse.

**Nota sullo stato di questa pagina**: sostituisce l'audit `Analysis/Modules/04_Context_Foundation.md`
(2026-08-16), ormai stale. `Context.py` è cresciuto da 1508 a **1781 righe** nell'ultimo mese per via
del redesign combat-power/priorità (Fase 2 del piano fog-of-war) e del refactoring tattico/strategico
di `Region.py`: gran parte del contenuto nuovo (dimensione fisica unificata, tabelle di efficacia
per-azione, `combat_power_from_score`, dottrina di loadout) NON esisteva ancora all'audit precedente
ed è verificata qui contro il sorgente attuale, non copiata dal vecchio documento.

## File inclusi

| File | Righe | Note |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Context/Context.py` | 1781 | enum/costanti/funzioni di dominio, nessuna dipendenza applicativa |
| `Code/Dynamic_War_Manager/Source/Context/Initial_Context.py` | 987 | dati di inizializzazione campagna |
| `Code/Dynamic_War_Manager/Source/Context/Actual_Context.py` | 1894 | stato runtime + duplicazione di Initial_Context |
| `Code/Dynamic_War_Manager/Source/Context/Logistic_Lines.py` | 191 | linee logistiche (stub non funzionante) |

Diagramma UML pertinente (non riverificato in questa sessione): `Analysis/UML/Logistic_Lines.plantuml`.

## File e classi principali

### Context.py — contenuto invariato dall'audit precedente (confermato)

- **Dimensioni fisiche (vecchio schema, ancora presente)**: `VEHICLE_SIZE_CATEGORY`,
  `SHIP_SIZE_CATEGORY`, `STRUCTURE_SIZE_CATEGORY`, `get_dimension(asset_type, length, width,
  height, weight, structure_type=None)`.
- **Task/azioni**: `Ground_Action`→`GROUND_ACTION`, `Air_To_Air_Task`/`Air_To_Ground_Task`→
  `AIR_TO_AIR_TASK`/`AIR_TO_GROUND_TASK`→`AIR_TASK`, `Sea_Task`→`SEA_TASK`, `ACTION_TASKS`,
  `MILITARY_FORCES = ['ground', 'air', 'sea']`.
- **Categorie asset terrestri**: `Ground_Vehicle_Asset_Type` (alias `ag`).
- **Tassonomia bersagli/armi**: `Weapon_Power_Effect`, `Weapon_Area_Effect`, `Target_Class_Name`
  (alias `tc`) + `WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE`, `TASK_FOR_WEAPON_PARAM`,
  `get_task_from_target()`.
- **Infrastrutture di blocco**: `BLOCK_INFRASTRUCTURE_ASSET`, `get_block_infrastructure_components`,
  `TARGET_CLASSIFICATION` + `get_target_classification` (bug strutturale ancora presente, v. sotto),
  `BLOCK_ASSET_CATEGORY` (ancora il simbolo più riusato del modulo).

### Context.py — contenuto NUOVO dall'ultimo mese (non nel vecchio audit, verificato a fronte del sorgente attuale)

- **`DIMENSION_CLASSES = ('big', 'med', 'small')`** (righe ~114): vocabolario dimensionale
  canonico condiviso da `VEHICLE_SIZE_CATEGORY`/`SHIP_SIZE_CATEGORY`/`STRUCTURE_SIZE_CATEGORY`/
  `AIRCRAFT_SIZE_CATEGORY` e dalle chiavi `TARGET_DIMENSION` nelle tabelle armi
  (`*_Weapon_Data.py`). Prima dell'unificazione (2026-09) erano tre vocabolari incompatibili
  lungo la pipeline recon → priorità → efficacia armi (bug B0 del redesign combat-power,
  v. [[combat-power-priority-redesign]]).
- **`AIRCRAFT_SIZE_CATEGORY`** (righe ~134-154): nuova tabella di soglie fisiche (length/height/
  width/weight in kg) per gli Aircraft, popolata con dati reali di 65 modelli (ricerca web,
  arrotondati a metri interi) — sostituisce la vecchia classificazione dimensione-da-ruolo
  (Fighter/Attacker/... → small) che produceva casi patologici (es. MiG-31 21820kg classificato
  "small" come un F-16). Soglie finali: `big` ≥30m/28m apertura/8m/25000kg, `med` ≥16/11/4/6000,
  `small` ≥6/6/1/300. Distribuzione risultante sul dataset reale: 13 small / 37 med / 15 big,
  nessun 'Unknown'.
- **`get_dimension`** ora accetta anche `asset_type='Aircraft'` (oltre a `'Vehicle'`/`'Ship'`/
  `'Structure'`), dispatching su `AIRCRAFT_SIZE_CATEGORY`.
- **`classify_asset_dimension(asset, valid_asset_types=None)`** (righe ~301-341): funzione
  pubblica nuova, **unico punto di verità** per la regola di classificazione dimensionale
  condivisa da `Block.get_recognition_report` (fog-of-war, con gating di probabilità) e da
  `Logic.Tactical_Analysis.target_profile_from_block` (ground-truth, senza gating) — entrambi
  costruiscono un target profile dalla stessa forma di asset e non devono poter divergere su
  questa regola. Gestisce Vehicle/Ship/Aircraft/Structure in modo uniforme via
  `asset.get_physical_characteristics()` + `get_dimension`; ritorna `None` se la classe
  dell'asset non è una delle quattro, se mancano le physical characteristics, o se
  `asset.asset_type` non è in `valid_asset_types` (quando fornito).
- **`MILITARY_CATEGORY_TO_FORCE`** (righe ~464-468): mappa `Military.get_military_category()`
  (`'Ground_Base'`/`'Air_Base'`/`'Naval_Base'`) → `force` (`'ground'`/`'air'`/`'sea'`), usata da
  `Logic.Tactical_Analysis`/`Logic.Tactical_Evaluation` per invocare `Military.combat_power(force,
  action)` con il force corretto. Spostata qui da `Region.py` durante la Fase 1 del refactoring
  tattico (era `Region`-locale, ora vocabolario condiviso).
- **`GROUND_COMBAT_EFFICACY`** ristrutturata: ora **indicizzata per azione**
  (`GROUND_ACTION['Attack']`/`['Defense']`/`['Maintain']`/`['Retrait']` → `{categoria: efficacia}`),
  non più una tabella piatta — riflette la scoperta del redesign combat-power che l'efficacia di
  classe (Tank/Armored/Motorized/...) dipende dalla postura tattica, non solo dalla categoria.
- **`SEA_COMBAT_EFFICACY`** (nuova, righe ~561-565): stesso schema per-azione per le navi
  (Attack/Defense/Retrait — niente Maintain, non in `SEA_TASK`), copre Carrier/Cruiser/Destroyer/
  Submarine/Frigate/Corvette/Amphibious_Assault_Ship/Transport/Civilian.
- **`AIR_COMBAT_EFFICACY`** (nuova, righe ~595+): tabella per ruolo aereo (`Air_Asset_Type`), **non**
  indicizzata per azione (per gli aerei i task — CAP, Strike, Intercept... — sono ruoli di
  missione, non posture tattiche mutuamente esclusive come per ground/sea) — a differenza
  di quanto suggeriva il vecchio audit ("valorizzata solo per F-15/F-4E"), oggi copre tutti i
  ruoli reali (Fighter 5.0, Fighter_Bomber 4.5, Attacker 4.0, Bomber 3.0, ...).
- **`combat_power_from_score(category, score, efficacy_table, efficiency=1.0, max_efficacy=5.0,
  efficacy_weight=0.3)`** (righe ~510-550): funzione pura nuova, estratta da
  `Vehicle.set_combat_power` per essere l'**unico punto di contatto** fra il calcolo ground-truth
  (per singolo modello noto) e la sua stima aggregata fog-of-war
  (`Combat_Power_Estimation.py`, v. [[context-state]]) — condivisa
  deliberatamente per evitare che i due calcoli divergano nel tempo. Formula:
  `relative_weight = 1 + efficacy_table[category]*efficacy_weight/max_efficacy`,
  `combat_power = relative_weight * (1+score) * efficiency`; ritorna `0.0` se `category` non è
  in `efficacy_table` (questo è il meccanismo per cui SAM/AAA/EWR hanno combat power
  identicamente zero per costruzione, v. [[combat-power-priority-redesign]]).
- **`WEAPON_TARGET_CLASS_MAP` + `get_weapon_target_class(target_type)`** (righe ~1559-1613):
  collassa i 26 valori di `Target_Class_Name` sulle 12 classi coperte dalle tabelle di efficacia
  armi. A differenza del collasso Generic/Helibase/Logistic→Structure|Airbase (fallback
  intenzionale), un `target_type` non valido solleva `ValueError` (non è un fallback, è un
  bug/typo da far esplodere).
- **`LOADOUT_DOCTRINE` + `get_doctrine_loadouts(model, side=None)`** (righe ~1616-1655): tabella
  sparsa di override di dottrina/politica di impiego loadout per `(side, model)`
  (`{'allowed': [...]}` o `{'denied': [...]}`, con `side='*'` come fallback cross-side).
  **Vuota per ora** (`LOADOUT_DOCTRINE = {}`): nessuna restrizione di dottrina è ancora stata
  modellata, solo l'infrastruttura è pronta. L'assenza di voce per una coppia `(model, side)` è
  il caso normale (nessuna eccezione), a differenza di `get_weapon_target_class`. Risolvere la
  regola grezza in un insieme di loadout concreti resta responsabilità del chiamante
  (`Air_Resources_Assigner.get_available_loadouts`), per non introdurre in `Context.py` una
  dipendenza da `Aircraft_Loadouts.py` (che già dipende da `Context.py`).

## Dipendenze

- **Context.py**: solo `enum`, `typing`, `Utility.LoggerClass` — nessuna dipendenza da altri
  moduli applicativi del progetto. È alla radice della gerarchia, nessun import circolare. Import
  a freddo costa **~0.67s** (misurato durante il refactoring tattico) — non per sotto-import
  pesanti, ma per il costo di costruzione a tempo di import dei grandi dizionari letterali di
  modulo; questo costo si propaga a ogni modulo che importa `Context.py` ed è irriducibile senza
  ristrutturare il modulo stesso.
- **Initial_Context.py / Actual_Context.py**: importano da `Context.py` (enum) e da
  `Asset.Aircraft_Loadouts` + `Asset.Aircraft_Data`.
- **Logistic_Lines.py**: `Context`, `Utility`, `Block.Transport`, `Block.Block`, `DataType.Payload`,
  `DataType.State`, `Utility.LoggerClass`.

## Stato attuale

**Context.py — solido, cresciuto.** Verificato con esecuzione reale:
```
.direnv/python-3.12/bin/python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Context.py"
→ Ran 168 tests — OK
```
(168 test, non più 145 come all'audit precedente — crescita coerente con le nuove funzioni
`classify_asset_dimension`/`combat_power_from_score`/`get_weapon_target_class`/
`get_doctrine_loadouts`).

**Bug fatale `asea.FAST_ATTACK` — RISOLTO.** Il vecchio audit segnalava che `Initial_Context.py:101`
e `Actual_Context.py:70` referenziassero `asea.FAST_ATTACK` (membro enum inesistente), bloccando
l'import di entrambi i moduli indipendentemente dal problema di import circolare. **Verificato
oggi**: entrambi i file usano correttamente `asea.CORVETTE.value` (il commento `# Fast_Attack`
accanto al membro reale `CORVETTE` in `Context.py:821` chiarisce la corrispondenza). Verificato con
esecuzione diretta che **entrambi i moduli si importano oggi senza errori**:
```
.direnv/python-3.12/bin/python3 -c "import Code.Dynamic_War_Manager.Source.Context.Initial_Context"
→ OK
.direnv/python-3.12/bin/python3 -c "import Code.Dynamic_War_Manager.Source.Context.Actual_Context"
→ OK
```
Non è chiaro se questo sia stato un fix mirato o un effetto collaterale di altro lavoro sul
progetto — non risulta menzionato in nessuna memoria di progetto consultata; segnalato qui come
fatto verificato, non come attribuzione. Resta vero che nessun test dedicato esiste per
`Initial_Context.py`/`Actual_Context.py` (copertura zero), e nessun modulo di produzione importa
`Actual_Context.py` in pratica (la persistenza runtime reale passa da `Campaign_State.py`, v.
[[context-state]]).

**Logistic_Lines.py — invariato, ancora non funzionale.** Riverificato a fronte del sorgente
attuale: tutti i bug strutturali del vecchio audit sono ancora presenti — `self._logistic_lines`
dichiarato come bare annotation senza inizializzazione, `_add_logistic_line` controlla
`self._lines` (attributo mai definito, il vero nome è `_logistic_lines`), `remove_logistic_line`
usa `self._blocks` (mai definito), `get_line` è vuoto (`pass` in ogni ramo),
`get_logistic_line_by_criteria` è `@lru_cache` su un metodo d'istanza (anti-pattern),
`setup_blocks_resource_manager` itera `self._lines` (mai definito) e legge `line.transport`
(il campo del dataclass è `transport_line`). Non importato da nessun altro modulo del progetto.
Nessun `Test_Logistic_Lines.py`.

## Decisioni architetturali rilevanti

- [[region-tactical-strategic-refactor]] — la separazione analizzatore/valutatore che ha portato
  `MILITARY_CATEGORY_TO_FORCE` in `Context.py` e ha reso necessaria una dottrina di targeting
  condivisa (`Context/Doctrine.py`, v. [[context-state]]).
- [[c2-hierarchy-design]] — la gerarchia C2 a due livelli che consumerà `LOADOUT_DOCTRINE`/
  `get_doctrine_loadouts` e la dottrina di targeting per-side quando i componenti `Command/`
  verranno costruiti.
- [[combat-power-priority-redesign]] — l'origine di `combat_power_from_score`,
  `DIMENSION_CLASSES`/`classify_asset_dimension`, `AIRCRAFT_SIZE_CATEGORY` e delle tabelle di
  efficacia per-azione/per-ruolo qui documentate.

## Note

- Il bug preesistente nella struttura dati di `TARGET_CLASSIFICATION` (chiavi con valore
  `[dict.keys()]` invece di una lista piatta, che rompe silenziosamente
  `get_target_classification` per `AIRBASE`/`HELIBASE`/`PORT`/`SHIPYARD`/`FARP`/`STRONGHOLD`/
  `SHIP`/`GENERIC`) non è stato riverificato riga per riga in questa sessione (fuori dal
  perimetro esplicito dell'incarico, che riguardava Context-Foundation/Context-State); si segnala
  solo che non risulta in nessuna memoria di progetto come risolto.
- Un bug indipendente, scoperto durante il redesign combat-power e non ancora corretto: la
  collisione fra `Air_Asset_Type.TRANSPORT.value == 'Transport'` e la stessa stringa usata in
  `SEA_MILITARY_CRAFT_ASSET` fa sì che `get_target_classification` (che prende il primo match e
  itera con `tc.SHIP` prima di `tc.AIRCRAFT`) classifichi un C-130 come nave. Fuori scope per
  questa pagina di documentazione, riportato solo come nota.
