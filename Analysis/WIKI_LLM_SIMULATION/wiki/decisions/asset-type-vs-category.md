---
title: "asset_type vs category negli asset Mobile (Vehicle/Ship/Aircraft)"
type: decision
tags: [architecture, dwm, asset, vehicle, ship, aircraft, taxonomy]
created: 2026-09-18
updated: 2026-09-18
status: accepted
affects: ["[[asset-air]]", "[[asset-ground-naval]]", "[[asset-base]]"]
related: []
---

## Contesto

`Vehicle`, `Ship` e `Aircraft` (le tre classi `Mobile` con equipaggiamento) usavano in modo incoerente i due campi `asset_type` e `category` ereditati da `Asset`. Il resto della pipeline di classificazione dei bersagli (`Block.ASSET_TYPE`, `Context.classify_asset_dimension`, `Context.get_target_classification`) si aspettava già che `asset_type` contenesse la classe generale (`Ground_Vehicle_Asset_Type`/`Sea_Asset_Type`/`Air_Asset_Type`), ma il codice delle tre classi non era allineato a questa aspettativa in modo uniforme — alcuni metodi leggevano `category` dove avrebbero dovuto leggere `asset_type`, e viceversa.

## Decisione

Convenzione unica, ora applicata a tutte e tre le classi Mobile:

- **`asset_type`**: classe generale — `Ground_Vehicle_Asset_Type` per Vehicle (Tank/Armored/Motorized/Artillery_Fixed/Artillery_Semovent/SAM_Big/SAM_Medium/SAM_Small/EWR/AAA), `Sea_Asset_Type` per Ship, `Air_Asset_Type` per Aircraft.
- **`category`**: sotto-classe granulare, **esiste realmente solo per Vehicle** (le chiavi interne di `GROUND_MILITARY_VEHICLE_ASSET[asset_type]`, es. `Main_Battle_Tank`, `Infantry_Fighting_Vehicle`, `Howitzer_Big`). `SEA_MILITARY_CRAFT_ASSET`/`AIR_MILITARY_CRAFT_ASSET` sono dizionari piatti a un solo livello indicizzati direttamente dalla classe generale — per Ship e Aircraft non esiste una sotto-vocabolario granulare in `Context.py`, quindi `category` è semplicemente libero/inutilizzato per loro (nulla è stato inventato per riempirlo).

Modifiche applicate:
- `Asset.py`: il setter di `asset_type` converte ora un `Enum` al proprio `.value` (mirror del setter di `category`); la stessa conversione è stata aggiunta anche dentro `Asset.__init__` (la sola modifica al setter non bastava, perché `_validate_all_params` legge dalle variabili locali del costruttore, non attraverso i setter delle property).
- `Vehicle.py`: tutti i predicati (`isTank`, `isArmor`, `isSAM_*`, ecc. — non `isCommandControl`, che resta su `category`) letti da `asset_type`; `set_combat_power` e `loadAssetDataFromContext`/`checkParam` (solo ramo Military) ribucketizzati su `asset_type` con match su `category`. Il ramo Logistic è stato lasciato intatto — indicizza `BLOCK_INFRASTRUCTURE_ASSET` con un vocabolario indipendente e non correlato.
- `Ship.py`/`Aircraft.py`: normalizzazione completa analoga — tutti i predicati (`isDestroyer`/.../`isSubmarine` per Ship; `isFighter`/.../`isHelicopter` per Aircraft) e `set_combat_power`/`air_combat_power` letti da `asset_type`; `loadAssetDataFromContext` (ramo Military) ribucketizzato allo stesso modo di Vehicle. `checkParam` non ha richiesto modifiche in nessuna delle due classi, perché già validava `asset_type` contro le rispettive chiavi piatte per accidente di implementazione preesistente.
- `Military.py:348` (`_get_artillery_stats`): sia la parte Vehicle sia la parte Ship aggiornate da `asset.category` a `asset.asset_type`.
- `Context.classify_asset_dimension`: **il ramo Aircraft** (non solo commenti) è stato corretto — leggeva `getattr(asset, 'category', None)` per il bucket dimensionale small/med/big basato sul ruolo, ora legge `asset_type` (variabile separata da `asset_category`, che il ramo Structure continua legittimamente a usare per `structure_type`).

## Motivazione

Il criterio guida è stato verificare, non assumere: `GROUND_COMBAT_EFFICACY` (confermato indicizzato dalla classe generale), la forma del ciclo di generazione di `GROUND_MILITARY_VEHICLE_ASSET`/`BLOCK_ASSET_CATEGORY` (esterno = classe generale, interno = granulare — confermato dai commenti dello stesso ciclo, ora corretti), e il gate `valid_asset_types` di `Block.ASSET_TYPE`/`classify_asset_dimension` (confermato che `asset_type` deve essere un membro di `Ground_Vehicle_Asset_Type`) erano tutti già allineati sulla convenzione "asset_type = classe generale". Allineare le tre classi Mobile a questa convenzione esistente, invece di introdurne una nuova, ha richiesto zero cambi allo schema dati di `Context.py`.

La correzione al ramo Aircraft di `classify_asset_dimension` era più di un dettaglio cosmetico: se non fosse stata fatta, `Block.get_recognition_report`/`Region._target_profile_from_block` (si veda [[air-priority-target-specific-loadout]]) avrebbero smesso silenziosamente di classificare la dimensione di ogni Aircraft nel momento in cui il campo `category` di `Aircraft` avesse smesso di essere popolato con la classe generale — un bug latente disinnescato preventivamente.

## Conseguenze

- Normalizzazione completa e verificata per tutte e tre le classi Mobile: suite completa **2465 test OK / 5 skipped**, nessuna regressione rispetto alla baseline pre-modifica.
- **Non risolto da questa decisione, esplicitamente fuori scope**: nessuna factory di produzione costruisce ancora un `Vehicle`/`Ship`/`Aircraft` reale a partire dai dati registro (`Vehicle_Data.py`/`Ship_Data.py`/`Aircraft_Data.py`) collegando il loro campo `'category'` per-modello (es. `VEHICLE['T-90M']['category'] == 'Tank'`) all'`asset_type` dell'istanza a tempo di costruzione. Vehicle ha già un vocabolario granulare reale da cui un futuro `category` potrebbe essere popolato; Ship/Aircraft non ne hanno alcuno.
- **Bug pre-esistente trovato ma esplicitamente NON corretto**, verificato ancora presente a HEAD (2026-09-18): `Ship.loadAssetDataFromContext`/`Aircraft.loadAssetDataFromContext` (ramo Military) iterano `asset_data[self.asset_type]` senza `.items()` — es. `Ship.py:65`, `for k, v in asset_data[self.asset_type]:` — ma `SEA_MILITARY_CRAFT_ASSET`/`AIR_MILITARY_CRAFT_ASSET` sono dizionari **piatti** (a differenza della struttura annidata di Vehicle), quindi `asset_data[self.asset_type]` è già il dict foglia (`{'cost':..., 'value':...}`) e iterarlo senza `.items()` produce solo le sue chiavi stringa — un `for k, v in <dict>:` su quelle stringhe solleverebbe `ValueError: too many values to unpack` non appena questo ramo venisse eseguito con un risultato non vuoto. Non si è mai manifestato perché nessuna factory di produzione chiama questo metodo con dati reali (solo test che mockano `asset_data.__getitem__` per intero). Solo la scelta del campo (`asset_type` vs `category`) è stata allineata alla nuova convenzione; il bug strutturale piatto-vs-annidato/`.items()` mancante resta un difetto pre-esistente aperto.

## Fonti

- [[project_vehicle_asset_type_category_conflict]] (memoria di origine)
- [[project_priority_calc_combat_power_redesign]] / [[project_air_priority_target_specific_loadout]] (thread precedenti da cui questa decisione origina)
