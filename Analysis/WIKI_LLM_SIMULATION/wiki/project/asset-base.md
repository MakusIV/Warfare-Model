---
title: "Asset — Classi Base"
type: project-module
tags: [package-python, warfare-model, dwm, architecture, asset]
created: 2026-09-18
updated: 2026-09-22
code_paths: [Code/Dynamic_War_Manager/Source/Asset/Asset.py, Code/Dynamic_War_Manager/Source/Asset/Mobile.py, Code/Dynamic_War_Manager/Source/Asset/Structure.py]
related_decisions: ["[[asset-type-vs-category]]", "[[virtual-session-engine-des]]"]
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
- **`Mobile.speed` — schema canonico in m/s (Fase 1 motore sessioni virtuali, 2026-09-21, v. [[virtual-session-engine-des]])**: `SPEED_SCHEMA` in testa al file fissa la forma `{"nominal", "max", "off_road": {...} (solo Vehicle), "reference_altitude" (solo Aircraft)}`, tutto in m/s. Chiave canonica `nominal` (non `cruise`, mai usata con successo prima). Il default mutabile condiviso fra istanze nella firma di `__init__` è stato sostituito da `None` + `default_speed_profile()` (nuovo oggetto ad ogni chiamata). Ponte registry→istanza: `Mobile.speed_profile_from_registry()` + `load_speed_from_registry()`, chiamati dai costruttori di `Vehicle`/`Ship`/`Aircraft` dopo `_model`, con dispatch **sul registry che risponde** (non `isinstance`). Conversioni km/h, mph, nodi, IAS→TAS verso m/s in nuove utility su `Utility.py`.
- **`Mobile.detection_range(mode, sensor=None, range_type='acquisition_range')` — Fase 2 motore sessioni virtuali (2026-09-22, v. [[virtual-session-engine-des]])**: raggio di rilevamento in metri contro bersagli `mode∈{ground,air,sea}`, dai dati `radar`/`TVD` già presenti nei registry (`self.radar['capabilities'][mode] → (bool, {tracking_range, acquisition_range, engagement_range, multi_target_capacity})`, km). Compone radar+TVD col **massimo** (non la somma: guardano lo stesso bersaglio), isolabile con `sensor='radar'|'TVD'`. Stesso pattern no-eccezioni/import-locale di `combat_range`/`air_defense_volume`; helper `_sensor_range_km` (staticmethod). È il ponte che permette il confronto rotta↔raggio-di-rilevamento che il futuro `Contact_Scheduler` userà per decidere quando un osservatore vede un bersaglio.
- **`Asset.apply_damage(health_delta)` — nuovo 2026-09-22 (Q2 delle "3 questioni aperte", v. [[virtual-session-engine-des]])**: unico punto in cui la salute cala per effetto del combattimento (il setter `health` resta per inizializzazione/persistenza). Satura a 0 (mai negativo), `ValueError` se `health_delta` è positivo (la riparazione non passa di qui). Nessuna nozione d'arma né estrazione casuale: quanto danno faccia un colpo lo decide il nuovo `Logic/Damage_Model.py` (`resolve_hit`/`health_delta_for_outcome`/`build_damage_event`), che riceve l'esito casuale (`draw`) dal chiamante invece di generarlo — coerente con la convenzione di progetto "mai `random` a livello di modulo" e con il vincolo di riproducibilità da seed del motore DES.

### Bug confermati ancora presenti (letti nel codice HEAD, 2026-09-18)

1. **`Asset.is_military()`/`is_logistic()`/`is_civilian()` — chiamano attributi che `Block` non ha.** `Asset.py:463-470`: `return self.block.isMilitary` / `.isLogistic` / `.isCivilian` (accesso ad attributo, senza parentesi). `Block` espone invece solo i metodi `is_military()`/`is_logistic()`/`is_civilian()` (snake_case, `Block.py:452-460`) — nessun attributo `isMilitary`/`isLogistic`/`isCivilian` esiste sulla classe reale. Con un `Block` vero, queste tre chiamate solleverebbero `AttributeError`. **Bug mascherato dal test**: `Test_Asset.py:16-18` usa `MagicMock(spec=Block)` ma poi assegna manualmente `self.mock_block.isMilitary = True` (un attributo che il vero `Block` non ha) — `spec=` blocca solo le *letture* di attributi inesistenti, non le assegnazioni, quindi il mock si allontana silenziosamente dalla vera API e il test passa nonostante il bug di produzione. Non risulta nessun chiamante reale di `Asset.is_military()`/`is_logistic()`/`is_civilian()` nel codice di produzione (solo il test le esercita) — probabile motivo per cui il bug non è mai emerso. **Non presente nell'audit 2026-08-16** (i tre metodi non vi comparivano): drift/aggiunta successiva.
2. ~~**`Mobile.checkParam`/`checkParamDCS` — `self` mancante.**~~ **RISOLTO 2026-09-21 (Fase 1 motore sessioni virtuali, v. [[virtual-session-engine-des]]).** `checkParam` è ora `@staticmethod` e valida lo schema canonico `SPEED_SCHEMA`; il setter `speed` non passa più da `checkParam` ma da `Mobile._validate_speed`. Il placeholder/bypass descritto sotto (mai riassegnare `self.speed` dopo la costruzione) è stato sostituito dal ponte reale `load_speed_from_registry()` — v. sezione "Cosa funziona" sopra.
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
- [[virtual-session-engine-des]] — Fase 1 (cinematica: `SPEED_SCHEMA`, `speed_profile_from_registry`, fix `checkParam`) e Fase 2 (percezione: `detection_range`) del motore DES per le sessioni virtuali sono costruite qui, in `Mobile.py`.

## Note

- **Drift più significativo rispetto all'audit `Analysis/Modules/03_Asset_Base.md` (2026-08-16)**: quell'audit descriveva `Ship`/`Vehicle`/`Aircraft` come **non istanziabili in nessuna configurazione** a causa del bug `Mobile.checkParam` (self mancante) combinato con l'import circolare `Aircraft ↔ Aircraft_Data ↔ Aircraft_Loadouts ↔ Aircraft_Weapon_Data ↔ Aircraft`. Ad oggi (2026-09-18) **entrambi i problemi sono superati**: l'import circolare è stato rotto (vedi [[asset-air]] §Note) e il bug `checkParam` è stato reso innocuo evitando di richiamare il setter `speed` nei costruttori delle tre sottoclassi. Risultato: `Vehicle`/`Ship`/`Aircraft` si istanziano regolarmente e l'intera suite di test del sottosistema Asset (oltre 2000 test cumulati tra Aircraft/Vehicle/Ship/Ground_Weapon/Ship_Weapon) è verde.
- `Structure` non risulta menzionata in nessuna memoria di progetto recente: verosimilmente non è nella roadmap attiva; nessuna evidenza che qualcuno stia pianificando di ripararla.
- `Mobile._weapon` (riga 61, dict vuoto) resta non popolato/non letto da nessuna sottoclasse — probabile dead code residuo, invariato dall'audit.
