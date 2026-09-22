---
title: "Asset — Terrestri e Navali"
type: project-module
tags: [package-python, warfare-model, dwm, architecture, asset, ground, naval]
created: 2026-09-18
updated: 2026-09-22
code_paths: [Code/Dynamic_War_Manager/Source/Asset/Vehicle.py, Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py, Code/Dynamic_War_Manager/Source/Asset/Ship.py, Code/Dynamic_War_Manager/Source/Asset/Ship_Data.py, Code/Dynamic_War_Manager/Source/Asset/Ground_Weapon_Data.py, Code/Dynamic_War_Manager/Source/Asset/Ship_Weapon_Data.py]
related_decisions: ["[[asset-type-vs-category]]", "[[combat-power-priority-redesign]]", "[[virtual-session-engine-des]]"]
related: ["[[asset-base]]", "[[asset-air]]"]
---

## Scopo

Modella gli asset mobili terrestri (`Vehicle`) e navali (`Ship`) del Dynamic War Manager: veicoli da combattimento (carri, IFV/APC, artiglieria, AAA/SAM) e unità navali (portaerei, incrociatori, cacciatorpediniere, fregate, sottomarini). Per ciascuna famiglia: una classe runtime (`Vehicle`/`Ship`, sottoclassi di `Mobile`, vedi [[asset-base]]), un modulo dati/anagrafica (`Vehicle_Data`/`Ship_Data`, registry statico + punteggi normalizzati), un modulo armi (`Ground_Weapon_Data`/`Ship_Weapon_Data`, catalogo + scoring arma-vs-bersaglio).

Questa pagina supersede, per lo stato attuale, `Analysis/Modules/02_Asset_Ground_Naval.md` (audit one-shot del 2026-08-16, oggi in larga parte superato — vedi §Note).

## File e classi principali

| File | Righe | Ruolo |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle.py` | 357 | `class Vehicle(Mobile)` |
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py` | 4893 | Registry/scoring veicoli terrestri, `VEHICLE` dict |
| `Code/Dynamic_War_Manager/Source/Asset/Ground_Weapon_Data.py` | 3090 | Catalogo armi terrestri `GROUND_WEAPONS`, scoring |
| `Code/Dynamic_War_Manager/Source/Asset/Ship.py` | 207 | `class Ship(Mobile)` |
| `Code/Dynamic_War_Manager/Source/Asset/Ship_Data.py` | 1539 | Registry/scoring navi, `SHIP` dict |
| `Code/Dynamic_War_Manager/Source/Asset/Ship_Weapon_Data.py` | 1422 | Catalogo armi navali `SHIP_WEAPONS`, scoring |

Test (eseguiti realmente il 2026-09-18, `unittest discover`): `Test_Vehicle.py` **24 test — OK**, `Test_Vehicle_Data.py` **164 test — OK**, `Test_Ground_Weapon_Data.py` **162 test — OK**, `Test_Ship.py` **7 test — OK**, `Test_Ship_Data.py` **145 test — OK**, `Test_Ship_Weapon_Data.py` **155 test — OK**. Tutti verdi.

## Stato attuale

### Il ciclo di import è stato rotto (stesso fix documentato in [[asset-air]])

L'audit 2026-08-16 documentava che `Ground_Weapon_Data.py:5` importava (inutilizzato) `Aircraft`, chiudendo il ciclo `Ground_Weapon_Data → Aircraft → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft`, il che rendeva `Vehicle`/`Vehicle_Data`/`Ground_Weapon_Data` **non importabili** in un ambiente pulito (`Ship`/`Ship_Data`/`Ship_Weapon_Data` non erano coinvolti, essendo indipendenti da `Aircraft`). Verificato oggi: **`Ground_Weapon_Data.py` non importa più `Aircraft`** — l'import morto è stato rimosso. Tutta la metà terrestre si importa e testa pulita, sullo stesso piano della metà navale.

### `Vehicle` — normalizzazione `asset_type`/`category` e fix multipli (drift maggiore rispetto all'audit)

- **`get_vehicle_scores` — validazione rotta, era bloccante, ora corretta.** L'audit segnalava che `if scores and scores not in SCORES` (confronto lista-vs-tupla-di-stringhe, sempre vero) faceva fallire **ogni istanziazione di `Vehicle`** con `ValueError`. Oggi (`Vehicle_Data.py:4679-4728`) la firma è `get_vehicle_scores(model, scores: Optional[List] = None)` con validazione per-elemento (`invalid = [s for s in scores if s not in SCORES]`) — identica al pattern già corretto in `Ship_Data.get_ship_scores`. `Vehicle.__init__` chiama questa funzione senza errori.
- **`get_physical_characteristics()` — era sempre `None`, ora funzionante.** L'audit notava che `VEHICLE[model]` (da `get_vehicle_data`) non includeva mai `'physical_characteristics'`. Oggi `VEHICLE[model]['physical_characteristics']` è popolato esplicitamente nel loop di costruzione (`Vehicle_Data.py:4638`, commento: "senza queste due chiavi nessun Vehicle compariva mai in un report (bug B2, Region/Military combat-power redesign 2026-09)") — `Vehicle.get_physical_characteristics()` funziona.
- **`loadAssetDataFromContext()` (ramo Military) riscritto**: bucket per `self.asset_type` (classe generale), match su `self.category` (sotto-classe granulare), usando correttamente `.items()` su `GROUND_MILITARY_VEHICLE_ASSET`/`AIR_DEFENSE_ASSET` — coerente con la convenzione [[asset-type-vs-category]]. Il ramo Logistic resta deliberatamente sul vecchio schema (vocabolario `BLOCK_INFRASTRUCTURE_ASSET` indipendente).
- **`checkParam()` riscritto**: logica sostanzialmente più ricca dell'audit, verifica `asset_type` sia contro `Ground_Military_Vehicle_Asset` sia contro `Air_Defense_Asset` in `BLOCK_ASSET_CATEGORY`, con fallback che cerca `category` in ogni bucket di `asset_type` se il primo controllo diretto fallisce.
- **`set_combat_power()` (nuovo rispetto all'audit)**: per ogni `ACTION_TASKS['ground']`, se `self.asset_type` è in `GROUND_COMBAT_EFFICACY[act]` calcola `combat_power_from_score(category=self.asset_type, score=self._vehicle_scores['combat score']['global_score'], efficacy_table=GROUND_COMBAT_EFFICACY[act], efficiency=self.efficiency)`; altrimenti (SAM/AAA/EWR/veicoli logistici) `combat_power[act] = 0`. Sostituisce il vecchio calcolo ad-hoc documentato nell'audit — allineato al Context helper condiviso `combat_power_from_score` usato anche da `Ship`/`Aircraft`.

### `Ship` — colmato solo in parte il gap con `Vehicle`

- `Ship.set_combat_power()` **esiste ora** (l'audit lo segnalava come assente/non implementato): stesso schema di `Vehicle.set_combat_power` ma su `SEA_COMBAT_EFFICACY`/`ACTION_TASKS['sea']`, chiamato da `Ship.__init__`.
- `Ship.get_physical_characteristics()` funziona: `SHIP[model]['physical_characteristics']` è popolato nello stesso modo di `VEHICLE`.
- `Ship.combatPower` come `@property` non funzionante (segnalato dall'audit) **non esiste più** — sostituita dal meccanismo `combat_power()`/`set_combat_power()` ereditato da `Mobile`, coerente con `Vehicle`/`Aircraft`.
- **`Ship.loadAssetDataFromContext()`/`checkParam()` — bug pre-esistenti, NON corretti**, stessa diagnosi dell'audit: `self.block.isMilitary()`/`isLogistic()` non esistono su `Block` (snake_case `is_military()`/`is_logistic()`, vedi [[asset-base]]) → `AttributeError` certo con un `Block` reale; e — anche a parte questo — `for k, v in asset_data[self.asset_type]:` itera un `dict` flat (`SEA_MILITARY_CRAFT_ASSET`) senza `.items()`. **Nessun test lo esercita** (`Test_Ship.py`, 7 test, copre init/proprietà `is*`/`set_combat_power`/`get_physical_characteristics`, non questi due metodi). Confermato ancora presente da `[[project_vehicle_asset_type_category_conflict]]` (bug segnalato ma esplicitamente lasciato fuori scope).

### Ordinamento destroy_capacity in `Ship_Weapon_Data` (fix confermato ancora applicato)

I template di efficienza (`_EFF_ASM_ANTISHIP_SUBSONIC`, `_EFF_NAVAL_GUN_76/100/127/130MM`, `_EFF_CIWS`, ecc.) rispettano tuttora l'ordine Soft > Armored > ship > Structure > Hard richiesto dal principio `score = accuracy × destroy_capacity` (vedi `[[project_ship_weapon_scoring]]`): verificato spot-check sui valori attuali (es. `_EFF_NAVAL_GUN_76MM`: Armored.dc 0.40-0.65, non più 0.06-0.10 come prima della correzione storica).

### Bug confermati ancora presenti, invariati dall'audit

- **Getter/setter morti in `Vehicle_Data`** (`engine`, `model`, `made`, righe ~101-117): stesso pattern di `Aircraft_Data`, mai richiamabili.
- **`FLAME_TRHOWERS`** (`Ground_Weapon_Data.py:3069`): categoria vuota (`{}`), refuso nel nome mai corretto.
- **Docstring disallineata** in `get_weapon_score_single_target` (`Ground_Weapon_Data.py`): descrive `caliber_factor`/`ammo_factor` che nel codice restano commentati/disattivati.

## Decisioni architetturali rilevanti

- [[asset-type-vs-category]] — implementata pienamente per `Vehicle` (`asset_type` = `Ground_Vehicle_Asset_Type`, `category` = sotto-classe granulare da `GROUND_MILITARY_VEHICLE_ASSET`) e per `Ship` (`asset_type` = `Sea_Asset_Type`; `category` senza vocabolario granulare dedicato, di fatto libero). Il bug residuo `Ship.loadAssetDataFromContext`/`Aircraft.loadAssetDataFromContext` (flat dict + `.items()` mancante) è esplicitamente lasciato fuori scope da questa decisione, non un effetto collaterale della stessa.
- [[combat-power-priority-redesign]] — `Vehicle.set_combat_power`/`Ship.set_combat_power` e il campo `users` (Vehicle: 64 modelli, Ship: 23 modelli, ricerca reale — vedi `[[project_fase2_recon_combat_power_plan]]` Fase 4) sono i pezzi ground/sea di questa redesign; consumati da `Context/Combat_Power_Estimation.py` per la stima fog-of-war (`asset_type` = bucket key, score per-modello = `VEHICLE[m]['combat score']['global_score']`/equivalente `SHIP`).
- [[virtual-session-engine-des]] — `Vehicle`/`Ship` ereditano da `Mobile` (documentata in [[asset-base]]) lo schema `SPEED_SCHEMA` in m/s (con `off_road`, campo specifico Vehicle) e `detection_range()`; la fabbrica `ThreatAA` (v. [[logic-routing]]) consuma i loro dati arma AD via `Vehicle_Data`/`Ship_Data`.

## Note

- **Drift maggiore rispetto all'audit 2026-08-16**: quell'audit descriveva "l'intera metà terrestre del sottosistema" come non testabile/non importabile per il ciclo circolare, con i bug `get_vehicle_scores`/`get_physical_characteristics` verificabili solo per lettura statica (non a runtime). Oggi tutti e tre i problemi sono risolti/verificabili a runtime, e la metà terrestre è testata al pari di quella navale (era già verde nell'audit).
- Gap UML invariato: nessun `Ship.plantuml`/`Ship_Data.plantuml`/`Ship_Weapon_Data.plantuml` in `Analysis/UML/` (esistono solo gli equivalenti `Vehicle*`).
- `Ship` resta strutturalmente meno rifinito di `Vehicle` più che altro sul fronte `loadAssetDataFromContext`/`checkParam` (mai corretti), non più su `set_combat_power`/`get_physical_characteristics` (ormai a parità).
