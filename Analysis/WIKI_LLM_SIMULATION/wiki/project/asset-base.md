---
title: "Asset — Classi Base"
type: project-module
tags: [package-python, warfare-model, dwm, architecture, asset]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Asset/Asset.py, Code/Dynamic_War_Manager/Source/Asset/Mobile.py, Code/Dynamic_War_Manager/Source/Asset/Structure.py]
related_decisions: ["[[asset-type-vs-category]]"]
related: ["[[asset-air]]", "[[asset-ground-naval]]"]
---

## Scopo

`Asset` è la classe radice di ogni unità/oggetto militare, logistico o civile gestito dal Dynamic War Manager (unità DCS → group → country → coalition, oppure edificio/infrastruttura). `Mobile` specializza `Asset` per gli oggetti che si muovono e combattono (ereditato da `Vehicle`, `Ship`, `Aircraft` — vedi [[asset-ground-naval]] e [[asset-air]]). `Structure` dovrebbe specializzare `Asset` per gli oggetti fissi/infrastrutturali (ponti, hangar, depositi...), ma resta non funzionante e non usata da nessuna sottoclasse concreta.

Questa pagina supersede, per lo stato attuale, `Analysis/Modules/03_Asset_Base.md` (audit one-shot del 2026-08-16, ormai superato su più punti — vedi §Note).

## File e classi principali

| File | Righe | Contenuto |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Asset.py` | 550 | `AssetParams` (dataclass inerte, mai istanziata fuori da questo file), `class Asset` |
| `Code/Dynamic_War_Manager/Source/Asset/Mobile.py` | 406 | `class Mobile(Asset)` |
| `Code/Dynamic_War_Manager/Source/Asset/Structure.py` | 193 | `class Structure(Asset)` |

Test: `Test_Asset.py` (41 test), `Test_Mobile.py` (54 test) — entrambi **verdi** (verificato con esecuzione reale, `unittest discover`, 2026-09-18). **Non esiste** `Test_Structure.py` — zero copertura, `Structure` non è mai istanziata con successo in nessun test del repo.

## Stato attuale

### Cosa funziona (verificato con esecuzione reale dei test, non solo lettura)

- `Asset.__init__`, le property (getter/setter con validazione `isinstance` rigorosa via `_validate_param`/`_validate_all_params`), gli eventi (`add_event`/`get_event`/`remove_event`), i `Payload` (`consume`/`_consume`/`get_production`/`produce`), gli stati (`is_operative`/`is_damaged`/`is_destroyed`/`is_healtful`/`is_critical`, tutti deleganti a `State`), la gestione `dcs_unit_data`. `is_critical()` chiama correttamente `self._state.isCritical()` (il typo storico `isCrytical` non è mai stato nel codice attuale).
- `Mobile.air_defense_volume()` e `Mobile.combat_range()` (introdotti prima del 2026-08-16): risolvono i dati arma da `Vehicle_Data`/`Ship_Data`/`Ground_Weapon_Data`/`Ship_Weapon_Data` con **import locale a runtime** (dentro il metodo, non a livello di modulo) — pattern deliberato, ancora oggi l'unico modo con cui `Mobile.py` accede ai dati arma senza reintrodurre dipendenze pesanti a livello di modulo. `air_defense_volume` filtra le armi AD per presenza di `min_altitude`/`max_altitude` **e** per il tag `task` che deve contenere `GROUND_WEAPON_TASK['Anti_Air']` quando presente; `combat_range` esclude simmetricamente le stesse armi AD dal computo del range offensivo.
- `Mobile.combat_power()`/`set_combat_power_value()`: accessor polimorfico validato (force/action) usato da `Vehicle`/`Ship`/`Aircraft` per esporre `_combat_power`.
- `Asset.model` (property, sola lettura su `self._model`, `None` se assente): **aggiunta rispetto all'audit 2026-08-16** — accessor di base usato da `Block.get_recognition_report` per leggere il modello di un asset senza dover distinguere `Vehicle`/`Ship`/`Aircraft`.

### Bug confermati ancora presenti (letti nel codice HEAD, 2026-09-18)

1. **`Asset.is_military()`/`is_logistic()`/`is_civilian()` — chiamano attributi che `Block` non ha.** `Asset.py:463-470`: `return self.block.isMilitary` / `.isLogistic` / `.isCivilian` (accesso ad attributo, senza parentesi). `Block` espone invece solo i metodi `is_military()`/`is_logistic()`/`is_civilian()` (snake_case, `Block.py:452-460`) — nessun attributo `isMilitary`/`isLogistic`/`isCivilian` esiste sulla classe reale. Con un `Block` vero, queste tre chiamate solleverebbero `AttributeError`. **Bug mascherato dal test**: `Test_Asset.py:16-18` usa `MagicMock(spec=Block)` ma poi assegna manualmente `self.mock_block.isMilitary = True` (un attributo che il vero `Block` non ha) — `spec=` blocca solo le *letture* di attributi inesistenti, non le assegnazioni, quindi il mock si allontana silenziosamente dalla vera API e il test passa nonostante il bug di produzione. Non risulta nessun chiamante reale di `Asset.is_military()`/`is_logistic()`/`is_civilian()` nel codice di produzione (solo il test le esercita) — probabile motivo per cui il bug non è mai emerso. **Non presente nell'audit 2026-08-16** (i tre metodi non vi comparivano): drift/aggiunta successiva.
2. **`Mobile.checkParam`/`checkParamDCS` — `self` mancante.** `Mobile.py:345,360`: entrambi definiti senza `self` esplicito e non `@staticmethod`; `speed.setter` (riga 100) chiama `self.checkParam(speed=param)`, che lega implicitamente `self` al parametro posizionale `speed` e va in conflitto con la keyword `speed=param` → `TypeError`. **Bug invariato dall'audit**, ma oggi esplicitamente aggirato: `Vehicle`/`Ship`/`Aircraft` non riassegnano mai `self.speed` dopo la costruzione — usano il placeholder `{"nominal": None, "max": None}` impostato direttamente da `Mobile.__init__` (bypassando la property) — con un commento esplicito in `Ship.py`/`Aircraft.py` che documenta la scelta ("Riassegnarlo qui passerebbe per Mobile.speed.setter... solleverebbe TypeError"). Il bug quindi non si manifesta più in pratica, ma resta non corretto.
3. **`Structure` resta totalmente non istanziabile**, stessa diagnosi dell'audit 2026-08-16, nessun fix nel frattempo:
   - `Structure.__init__` (riga 46) chiama `super().__init__(...)` con argomenti posizionali non allineati alla firma di `Asset.__init__` (manca lo slot `production`) — ogni parametro da `position` in poi finisce nello slot sbagliato.
   - Riga 55: `if not super.checkParam(...)` usa la classe built-in `super` invece del proxy `super()`.
   - Riga 49: `physical_characteristics = physical_characteristics if physical_characteristics else self.get_physical_characteristics()`, ma `get_physical_characteristics()` fa `return self.physical_characteristics` — attributo non ancora assegnato al primo utilizzo.
   - `getBlockInfo` (riga 101) referenzia `STRUCTURE_ASSET_CATEGORY`, mai importato nel file.
   - `loadAssetDataFromContext` (riga 60) itera `asset_data[...][...]` (un `dict`) senza `.items()`.
   Nessuna di queste righe è mai raggiungibile a runtime nel repository attuale (nessun caller istanzia `Structure`), quindi il bug è "dormiente" ma bloccante se qualcuno tentasse di riattivare la classe.

### Bug storici confermati risolti (nessuna azione necessaria)

- Import path (`Code.Dynamic_War_Manager.Source....` ovunque, nessun residuo `from Dynamic_War_Manager...`).
- La property `fire_range` è confermata assente da `Mobile` — sopravvive solo il nome del parametro nella firma orfana di `checkParam`.

## Decisioni architetturali rilevanti

- [[asset-type-vs-category]] — la convenzione `asset_type` = classe generale / `category` = sotto-classe granulare (solo Vehicle ne ha una) è applicata coerentemente a tutte le sottoclassi di `Mobile`; `Asset`/`Mobile` restano agnostici rispetto a questa distinzione (gestita nei setter di `Asset.category`/`Asset.asset_type`, che convertono un `Enum` passato in `.value`).

## Note

- **Drift più significativo rispetto all'audit `Analysis/Modules/03_Asset_Base.md` (2026-08-16)**: quell'audit descriveva `Ship`/`Vehicle`/`Aircraft` come **non istanziabili in nessuna configurazione** a causa del bug `Mobile.checkParam` (self mancante) combinato con l'import circolare `Aircraft ↔ Aircraft_Data ↔ Aircraft_Loadouts ↔ Aircraft_Weapon_Data ↔ Aircraft`. Ad oggi (2026-09-18) **entrambi i problemi sono superati**: l'import circolare è stato rotto (vedi [[asset-air]] §Note) e il bug `checkParam` è stato reso innocuo evitando di richiamare il setter `speed` nei costruttori delle tre sottoclassi. Risultato: `Vehicle`/`Ship`/`Aircraft` si istanziano regolarmente e l'intera suite di test del sottosistema Asset (oltre 2000 test cumulati tra Aircraft/Vehicle/Ship/Ground_Weapon/Ship_Weapon) è verde.
- `Structure` non risulta menzionata in nessuna memoria di progetto recente: verosimilmente non è nella roadmap attiva; nessuna evidenza che qualcuno stia pianificando di ripararla.
- `Mobile._weapon` (riga 61, dict vuoto) resta non popolato/non letto da nessuna sottoclasse — probabile dead code residuo, invariato dall'audit.
