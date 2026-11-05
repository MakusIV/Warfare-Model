# Proposta: radar EWR di siti fissi nei registri (D-4b, blocco C)

**Stato**: DECISIONI PRESE dall'utente il 2026-11-05 (C-0..C-4 tutte come raccomandato). Il piano di §4 e'
scritto su quelle e si esegue senza altre decisioni. Analisi del 2026-11-05. Nessun file di codice o di test
modificato. Le sonde di §1.7 sono script di sola lettura nella scratchpad di sessione: registrano i siti
**in memoria** e rieseguono codice e test esistenti, senza toccare il repository.
**Origine**: `Proposta_Dati_Sensori_EWR_Visivo.md` §4 "Blocco C" e decisione 14 (siti fissi rimandati);
blocchi A (`37816355`) e B (`cbc75634`) fatti. **Fonte dei dati**: `Ricerca_EWR_2026_10_29.md` §3 e §4, riletta
per intero (confidenza di ogni valore riportata in §4.C.3 e §5.1).
**Esecutore**: `des-developer` (Claude Sonnet, sforzo alto). Alternativa: `oc-developer`.
**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`) o eseguendolo; **[S]** = stima o scelta di
progetto, mai dato tarato; **F/D/S** = Fonte / Dedotto / Stima, come nella ricerca. Percorsi di codice relativi a
`Code/Dynamic_War_Manager/Source/`.

> **Decisione presa (C-0, utente, 2026-11-05)**: l'**AN/FPS-20 e' ESCLUSO** dai siti fissi per la contraddizione
> di fonte 322/407 km, entrambe non qualificate, confidenza bassa (`Ricerca_EWR_2026_10_29.md:349`, `:408`).
> L'esecutore non lo aggiunge.

---

## 0. Sintesi

**Decisioni gia' prese dall'utente (2026-11-05, non si riaprono)**:
1. modello **A**: `Vehicle` immobile con un **marcatore esplicito** nel record, cosi' una futura migrazione a
   `Structure` (opzione B) resta meccanica. Niente `Structure` con sensore, niente registro `Structure_Data`;
2. siti: **AN/FPS-117** (riferimento di migliore fonte), **Chain Home**, **AMES Type 7**, **AMES Type 80**,
   **Wassermann**, **Mammut**, **P-14**. AN/FPS-20 escluso (decisione C-0, v. nota sopra).

| Tema | Scelta del piano | Fotografia |
|---|---|---|
| Marcatore | argomento nuovo `fixed_site: bool = False` di `Vehicle_Data`, `True` solo nei 7 record nuovi | — |
| Velocita' | **0** nei tre regimi (dato vero); un test esistente va adattato, v. §1.2 | — |
| Autonomia (`range`) | **1 km**, SEGNAPOSTO di schema dichiarato, non autonomia | — |
| Campi non-sensore | terzo ramo `'fixed'` di `_ewr_support_fields`, tutto [S] | — |
| Portate | tabella §4.C.3, regola (a) del blocco B; valori deboli marcati | — |
| Combat score | invariato per costruzione (G2 gia' in vigore: categoria EWR fuori dalla popolazione globale) | — |
| Interruttore | **non serve**: dati nuovi e un marcatore che il motore non legge; nessuna regola nuova | — |
| Esito | suite `Ran 4757` (4742 + 15), OK, skipped 7; confronto **1009 identiche, 0 cambiate, 0 nuove** | invariata |

**Dimensione stimata**: ~25 righe di codice (costruttore, ramo di `_ewr_support_fields`, commento
nel pianificatore), ~220 righe di dati, ~1 riga cambiata in un test esistente, ~200 righe di test nuovi.

---

## 1. Problema e comportamento attuale

### 1.1 Come sono costruiti gli 8 EWR del blocco B [V]

- `GLOBAL_COMBAT_SCORE_EXCLUDED_CATEGORIES = frozenset({EWR})` (`Asset/Vehicle_Data.py:64`), usata dal solo
  `get_normalized_combat_score` nel caso globale, con saturazione in [0, 1] (`:959-981`).
- `Vehicle_Data.__init__` (`:71`): ultimo argomento `visual: Optional[Dict] = None` (blocco A). Valida solo
  `physical_characteristics` (interi positivi, `:72-83`), poi registra il record (`:108`).
- `_ewr_support_fields(mobility)` (`:4579-4623`): campi non-sensore [S] per `'mobile'` e `'semi_mobile'`;
  `ValueError` per ogni altro valore (`:4590-4591`). Restituisce dizionari nuovi a ogni chiamata.
- Record da `SCR270_data` (`:4633`) ad `AN_TPS43_data` (`:4802-4823`), con commento di testa `:4626-4631`;
  registrazione in coda dopo `S300PS_data`, con l'intestazione `# Nuovi EWR (D-4b)` (`:4907-4915`).
- La tabella `VEHICLE` e' ricalcolata su tutto il registro a fine modulo (`:4933-4953`).

### 1.2 Velocita' 0: cosa si rompe e cosa no [V, sonda S-1 e S-3]

**Si rompe un solo test**: `TestSpeedEval.test_all_vehicles_speed_eval_positive`
(`Test/Test_Vehicle_Data.py:713-717`) chiede `_speed_eval() > 0` per ogni record. Con velocita' 0 nei tre regimi
`_speed_eval` (`Asset/Vehicle_Data.py:279-312`) vale 0,0 e il test fallisce con 7 sotto-test (uno per sito). La suite
completa con i 7 siti in memoria non rompe nient'altro (sonda S-3, §1.7).

**Non si rompe**:
- `Mobile._regime_speed` (`Asset/Mobile.py:605-617`) e `_vehicle_speed_profile` (`:619-633`): profilo
  `{'nominal': 0.0, 'max': 0.0, 'off_road': {'nominal': 0.0, 'max': 0.0}}` (sonda S-2). La validazione del profilo
  accetta valori non negativi (`:550-556`);
- `Fuel_Model.cruise_speed` (`Logic/Fuel_Model.py:330-343`) e `Fuel_Model.max_speed` (`:1059-1063`): None per 0. Un
  tratto FERMO di un asset senza crociera nota **non consuma** (`_leg_equivalent`, `:346-358`; docstring `:41-42`);
- `Mission_Adapter._max_speed` (`Logic/Mission_Adapter.py:1141-1149`): None per 0, quindi `check_mission_speed`
  **esclude** il sito dalla regola A con un warning (`:1188-1194`). V. il limite in §5.2 punto 1;
- `Military._speed_regime` (`Block/Military.py:471-487`): 0,0; gli EWR non sono comunque asset d'attacco
  (`_is_attack_asset`, `:458-469`). Le divisioni per velocita' del core sono tutte protette (`Block/Military.py:401-402`,
  `Logic/Session_Simulator.py:1471`, `:1565`);
- **asset senza missione = fermo in posizione** (`Logic/Session_Simulator.py:2191`, `:2356`): un sito che non e' in
  nessuna missione non ha tratti, non consuma e non si muove. Nella sonda S-2 il sito in sessione non produce
  `FuelEvent`.

**Alternativa valutata e scartata**: velocita' minima (1 km/h) [S]. Non rompe il test, ma e' un numero inventato con
effetti collaterali: la crociera diventa 0,28 m/s, quindi le soste di una missione consumerebbero carburante
(`Fuel_Model.py:353-358`), e la regola A limiterebbe a 0,28 m/s ogni missione col sito. Il marcatore esiste proprio
per dichiarare l'eccezione: con velocita' 0 il test si adatta escludendo i record marcati (§4.C.5), e un test nuovo
asserisce lo 0.

### 1.3 Autonomia segnaposto [V]

- `test_range_is_positive_number` (`Test/Test_Vehicle_Data.py:320-324`; il compito citava `:318-322`) chiede
  `range > 0` per ogni record.
- `Mobile.fuel_autonomy` (`Asset/Mobile.py:1260-1320`) restituisce None, cioe' carburante non modellato, per
  `range <= 0` (`:1311-1315`).
- **Scelta: `range = 1`** (km), il minimo intero positivo, dichiarato **SEGNAPOSTO di schema**. Non rompe nulla. Nella
  sonda S-2: carburante 1,0, `fuel_autonomy()` 1000 m, nessun consumo in sessione (fermo e senza crociera). Non e'
  consumato da nessuna regola del motore per un asset fermo. Effetto collaterale dichiarato: se una missione
  muovesse il sito (uso improprio, §5.2 punto 1), il carburante finirebbe dopo 1 km e la F6-A troncherebbe i tratti.
  Non e' un meccanismo voluto.
- Scartato `range = 0`: romperebbe `test_range_is_positive_number` e renderebbe il carburante non modellato. Sarebbe
  semanticamente onesto, ma senza nessun vantaggio pratico rispetto al segnaposto, e la ricerca di tutti gli usi non
  trova consumatori che distinguano i due casi per un asset fermo.

### 1.4 Effetti sugli altri moduli [V, sonda S-2]

| Modulo | Effetto con i 7 siti |
|---|---|
| `Vehicle_Data` combat score globale | **nessun record esistente cambia** (G2): verificato su tutti i 72 record nella sonda S-2. Il globale dei siti satura a 0,0 |
| `Vehicle_Data` combat score di **categoria** | cambia per gli 8 EWR mobili (la popolazione EWR passa da 8 a 15). **Nessun consumatore**: `category_score` non e' letto fuori dai moduli dati e dai test (ricerca di tutti gli usi); `Vehicle.set_combat_power` legge il globale (`Asset/Vehicle.py:355`) |
| Altri score globali (speed, range, radar, reliability, availability) | si spostano (minimo speed ora 0; FPS-117 nuovo massimo di mtbf decisione C-2). **Nessun consumatore** (ricerca di `mtbf`/`mttr`/`speed score`/`range score` fuori dai moduli dati: nessun risultato), come gia' dichiarato al §5.2 punto 8 della Proposta A/B |
| `Vehicle.isEWR` (`Asset/Vehicle.py:298-299`) | True; combat power di terra 0 in ogni azione |
| `Mobile.detection_range`, `DETECTION_SENSORS` (`Asset/Mobile.py:83`) | nessuna modifica: i siti hanno solo il `radar`; portata aria = `acquisition_range` in metri |
| `Military.air_detection_threats` (`Block/Military.py:584-612`) | include i siti; `air_defense_threats()` vuota, `build_threat_aa` None |
| `Air_Route_Manager.build_detection_threat` (`Logic/Air_Route_Manager.py:731-786`) e `sensor_antenna_height` (`:704-728`) | raggio = min(portata, orizzonte); l'altezza d'antenna viene da `antenna_height` se presente, altrimenti da `SENSOR_HEIGHT_EWR_M` = 20 m [S] (`:660`). Sonda a 500 m: 110,6 km con 20 m, 127,4 km con 73 m (Chain Home), 106,1 km con 11,4 m (Type 80), 117,2 km con 37 m (Wassermann) |
| `Fire_Control.target_class` (`Logic/Fire_Control.py:593-614`) | `air_defence` (via `isEWR`); `target_key` = `(('Soft',), 'big', False)` con le dimensioni di §4.C.2 |
| `Air_Defense_Efficacy` | `emits_radar` True, `sam_category` None, `air_defense_profile` None; **fuori** da `default_rwr_catalogue` (limite 5.2.7 della Proposta A/B: gli RWR non vedono gli EWR) |
| `Context` inventari | `ag.EWR.value: {}` resta vuoto (`Context/Initial_Context.py:469-470`, `Context/Actual_Context.py:391-392`; decisione 17) |
| DES | il sito rileva e alimenta la percezione del dominio, **non spara mai**, non consuma; e' un bersaglio (nella sonda S-2 l'A-10C lo colpisce). Nessun cueing (D-7 fuori perimetro) |
| Adapter DCS | nessuno: il nome DCS "FPS-117" resta un commento informativo, non una chiave |

### 1.5 Altezza d'antenna dei siti fissi [V + fonte]

Oggi `antenna_height` e' letta da `sensor_antenna_height` (`Logic/Air_Route_Manager.py:713-717`) e la dichiara il
solo SCR-270. Il commento di `:649-658` elenca i record che usano i 20 m. Dati della ricerca:

| Sito | Dato di fonte (`Ricerca_EWR_2026_10_29.md`) | Proposta |
|---|---|---|
| Chain Home | torri trasmittenti 4x110 m, torri riceventi 4x73 m (`:128`, conf. alta) | **73** [D]: altezza delle torri riceventi, limite superiore delle antenne (stanno lungo la torre) |
| Wassermann | traliccio di ~40 m (L) o palo di 60 m (S); "altezza mast 37-57 m" (`:166`, conf. media) | **37** [D]: minimo dell'intervallo; limite superiore per la variante piu' bassa |
| AMES Type 80 | riflettore 75x25 ft (22,9x7,6 m) su torre piramidale di 25 ft (`:338`, conf. media) | **11,4** [D]: 7,6 m di torre + meta' riflettore (3,8 m) |
| AMES Type 7 | "sito fisso con pozzo radar" (`:217`): l'antenna e' a terra, altezza non data | default 20 m [S] |
| Mammut, P-14, AN/FPS-117 | dimensioni delle schiere, non l'altezza del supporto | default 20 m [S] |

Nota: l'orizzonte esiste solo nel pianificatore. Il DES non ha orizzonte radar (limite gia' dichiarato, Proposta A/B
§5.2 punto 1), quindi l'altezza d'antenna non cambia nessuna sessione.

### 1.6 Interruttore

Non serve, ed e' giusto dirlo: il blocco aggiunge **dati** a un registro e un **marcatore** che nessuna regola del
motore legge (ne' DES ne' pianificatore). La validazione del tipo del marcatore nel costruttore e' un controllo di
schema dei dati, non una regola di simulazione. Lo stesso criterio e' gia' stato applicato al blocco B (nessun
interruttore, decisione 9). Se in futuro il marcatore diventasse una regola (immobilita' imposta, §3 C-4), quella
regola avra' il suo interruttore.

### 1.7 Sonde eseguite (sola lettura, scratchpad di sessione)

| # | Cosa | Risultato |
|---|---|---|
| S-1 | 7 siti in memoria (velocita' 0, `range` 1, portate e antenne di §4.C.3), tabella `VEHICLE` ricalcolata; 7 moduli di test pertinenti (`Test_Vehicle_Data`, `Test_EWR_Data`, `Test_Combat_Power_Estimation`, `Test_Vehicle`, `Test_Threat_AA_Factory`, `Test_Air_Defense_Efficacy`, `Test_Mobile`) | `Ran 529`, 7 fallimenti, **tutti** sotto-test di `test_all_vehicles_speed_eval_positive` (uno per sito); combat score globale di nessun record esistente cambiato; score di categoria cambiato per gli 8 EWR mobili |
| S-2 | Siti come `Vehicle` reali in un `Military`, pianificatore, ADE, Fire_Control, sessione DES con un A-10C (come il test 15 del blocco B) | profilo di velocita' tutto 0,0; carburante 1,0, autonomia 1000 m, crociera None, velocita' massima None; `build_threat_aa` None; raggi di §1.4; `air_defence`; fuori dal catalogo RWR; in sessione 0 `AmmunitionEvent` e 0 `FuelEvent` del sito |
| S-3 | Suite completa con i 7 siti in memoria | `Ran 4742`, 7 fallimenti, tutti di `test_all_vehicles_speed_eval_positive` (§1.7.1) |
| S-4 | Stessa sonda con velocita' 1 km/h | nessun fallimento di `_speed_eval`; crociera e massima 0,28 m/s (gli effetti collaterali di §1.2) |
| S-5 | Confronto con la fotografia (`Scenario_Baseline --compare`, senza installare nulla) con i 7 siti in memoria | 1009 IDENTICHE (§1.7.1) |

#### 1.7.1 Esito delle sonde S-3 e S-5 (definitivo)

Suite completa (`unittest discover` come `verifica.sh`, interprete `python3` della VM osboxes), con i 7 siti
registrati in memoria e la tabella `VEHICLE` ricalcolata: **`Ran 4742`, `FAILED (failures=7, skipped=7)`**. I 7
fallimenti sono **tutti** sotto-test di `TestSpeedEval.test_all_vehicles_speed_eval_positive`, uno per sito
(`0.0 not greater than 0.0`). Nessun altro test esistente e' sensibile ai siti, compresi `Test_EWR_Data` (blocco B),
`Test_Combat_Power_Estimation` e `test_range_is_positive_number`. Il conteggio e' quello attuale, perche' la sonda
non aggiunge test: con i 15 di C.6 diventa 4757.

Confronto con la fotografia nella stessa condizione (sonda S-5): `Scenario_Baseline --compare` sulla fotografia
attuale, nulla installato. Esito **`compared 1009 runs: IDENTICAL`** (1090 s). Con i dati del piano l'unico test
esistente da adattare e' quello di §4.C.5, e la fotografia non cambia.

---

## 2. Alternative e raccomandazione

### 2.1 Forma del marcatore

| | **M1: `fixed_site: bool = False`** (raccomandata) | M2: `mobility: str` per tutti i record | M3: ruolo `'Fixed_Site'` in `roles` | M4: insieme di modelli a livello di modulo |
|---|---|---|---|---|
| Dove sta | argomento e attributo del record | argomento e attributo del record | lista `roles` | fuori dal record |
| Record esistenti | invariati (default False) | serve un default per 72 record: 'mobile' sarebbe falso per gli EWR semimobili, quindi vanno toccati anche gli 8 record B | invariati | invariati |
| Migrazione a `Structure` | `[r for r in registry.values() if r.fixed_site]` | idem con `== 'fixed'` | ambigua: `roles` e' letto da `sam_category` (`Context/Air_Defense_Efficacy.py:545-552`) | la lista va tenuta allineata a mano |
| Rischio | nessuno | piu' esteso del necessario | mescola mobilita' e ruolo operativo | dato separato dal record |

**Raccomandazione: M1.** Il nome evita `fixed`, che nel progetto ha gia' un altro senso: la categoria
`Artillery_Fixed` (`Context/Context.py:746`) e "riparato". `site` dice che l'asset e' un'installazione.

### 2.2 Velocita' e autonomia
Decise in §1.2 e §1.3: velocita' 0 (dato vero), con un test esistente adattato; `range` 1 km segnaposto. La
velocita' minima e' scartata (§1.2).

### 2.3 Campi non-sensore
Un terzo ramo `'fixed'` di `_ewr_support_fields` (raccomandato): un solo punto di stima, come per il blocco B. In
alternativa, campi scritti in ogni record: piu' righe e la stessa stima ripetuta 7 volte.

---

## 3. Decisioni dell'utente (2026-11-05)

Tutte DECISE dall'utente il 2026-11-05 come raccomandato. Il piano di §4 e' scritto su queste scelte; le
alternative scartate restano qui solo come traccia.

- **C-0 DECISA: AN/FPS-20 escluso.** Alternativa scartata: un ottavo record con 322 o 407 km dichiarato STIMA.
- **C-1 DECISA: velocita' 0 nei tre regimi, con il test esistente adattato** (§4.C.5). Alternativa scartata:
  velocita' minima 1 km/h [S] senza toccare il test. Aveva effetti collaterali: consumo nelle soste e limite di
  0,28 m/s alla regola A (§1.2).
- **C-2 DECISA: `reliability` dell'AN/FPS-117 da fonte** `{'mtbf': 2000, 'mttr': 0.75}`. E' l'unico EWR con MTBF e
  MTTR **entrambi** di fonte (Lockheed, conf. media-alta): 2000 e' un limite inferiore (">2000 h"), 0,75 h un limite
  superiore ("<45 min", conversione D). Gli altri 6 siti hanno la STIMA generica 45/4 (decisione 12). Alternativa
  scartata: 45/4 anche per l'FPS-117.
- **C-3 DECISA: `antenna_height` Chain Home 73 m, Wassermann 37 m, AMES Type 80 11,4 m, tutti [D] (limiti
  superiori)**; gli altri 4 siti al default EWR 20 m [S]. Alternativa scartata: tutti i siti al default 20 m.
- **C-4 DECISA: nessuna regola di immobilita' nel motore**, limite dichiarato (§5.2 punto 1). Una missione che
  muove un sito fisso non e' rifiutata: la regola A lo esclude con un warning (`Logic/Mission_Adapter.py:1191-1194`).
  Nessuno scenario ne' inventario di campagna assegna missioni agli EWR (decisione 17). Alternativa scartata (per ora):
  una violazione nuova di `Session_Validator` dietro un interruttore. Sarebbe una regola nuova, da Proposta
  separata.

---

## 4. Piano di intervento (opzioni raccomandate)

**Prerequisito**: blocchi A e B fatti (suite 4742, fotografia 1009). Lavorare sul branch indicato dalla sessione
principale. **Ordine**: C.1 → C.2 → C.3 → C.4 → C.5 → C.6 → verifiche C.7.

### C.1 `Asset/Vehicle_Data.py`: costruttore

- Firma (`:71`): aggiungere **in coda**, dopo `visual`, l'argomento keyword `fixed_site: bool = False`.
- Subito dopo la validazione di `physical_characteristics` (dopo `:83`, **prima** della registrazione a `:108`, cosi'
  un record invalido non entra nel registro):
  ```python
          if not isinstance(fixed_site, bool):
              raise ValueError(f"fixed_site must be a bool, got: {fixed_site!r}")
  ```
- Accanto a `self.visual` (`:100-102`):
  ```python
          # Marcatore dei SITI FISSI (D-4b blocco C, Proposta_Dati_Sensori_EWR_Siti_Fissi.md): True = installazione
          # fissa modellata come Vehicle immobile (velocita' 0 nei tre regimi, `range` segnaposto). Nessuna regola del
          # motore lo legge: serve a dichiarare l'eccezione nei dati e a rendere meccanica una futura migrazione a
          # Structure. False per tutti gli altri record (default).
          self.fixed_site = fixed_site
  ```
- Nessuna modifica a `_speed_eval`, `_range_eval`, `_combat_eval`, ai `get_normalized_*` e a
  `GLOBAL_COMBAT_SCORE_EXCLUDED_CATEGORIES`.

### C.2 `Asset/Vehicle_Data.py`: `_ewr_support_fields`

Sostituire il corpo di `_ewr_support_fields` (`:4579-4623`) con il seguente. I rami `'mobile'` e `'semi_mobile'`
devono restare **identici nei valori** (gli 8 record B non cambiano):
```python
def _ewr_support_fields(mobility: str) -> Dict:
    """Campi NON sensore dei record EWR (D-4b): TUTTI STIME DI SCHEMA DICHIARATE, nessuna fonte.

    Servono a soddisfare lo schema di Vehicle_Data (dimensioni intere positive, costo e autonomia > 0, velocita').
    `mobility`: 'mobile' (radar su autocarro) | 'semi_mobile' (rimorchi, messa in opera di ore) |
    'fixed' (sito fisso, blocco C: Proposta_Dati_Sensori_EWR_Siti_Fissi.md).
    Restituisce dizionari NUOVI a ogni chiamata (nessuna struttura condivisa fra record).

    Il `communication` porta una `reliability` {'mtbf': 45, 'mttr': 3} [S], come i "generic comm model"
    del registro. Con la decisione 12 il radar ha una `reliability` propria 45/4, quindi questa non
    serve piu' a evitare la lista vuota di `_reliability_eval`: resta per coerenza di schema.

    Ramo 'fixed': aggiunge `fixed_site: True`; velocita' 0 nei tre regimi (dato vero: il sito non si muove) e
    `range` 1 km, SEGNAPOSTO di schema (non un'autonomia: il primo intero positivo, richiesto dallo schema; un
    sito fermo non consuma, v. Fuel_Model.cruise_speed). L'asset e' l'installazione d'antenna con il suo supporto.
    """
    if mobility not in ('mobile', 'semi_mobile', 'fixed'):
        raise ValueError(f"mobility must be 'mobile', 'semi_mobile' or 'fixed', got {mobility!r}.")

    consumes = (0.4, 0.55, 0.7)

    if mobility == 'mobile':
        physical = {'length': 9, 'width': 3, 'height': 4, 'weight': 14}
        cost = 2.0
        range_km = 500
        speeds = {'sustained': 50, 'max': 70, 'off_road': 30}
    elif mobility == 'semi_mobile':
        physical = {'length': 12, 'width': 3, 'height': 6, 'weight': 25}
        cost = 4.0
        range_km = 300
        speeds = {'sustained': 30, 'max': 40, 'off_road': 15}
    else:
        # [S] ordine di grandezza di un'antenna fissa con il suo supporto (classe 'big' di
        # Context.VEHICLE_SIZE_CATEGORY); le torri del Chain Home (73-110 m) NON sono rappresentate.
        physical = {'length': 30, 'width': 10, 'height': 20, 'weight': 50}
        cost = 10.0           # M$ [S], non consumato dal motore
        range_km = 1          # SEGNAPOSTO di schema, NON autonomia (v. docstring)
        speeds = {'sustained': 0, 'max': 0, 'off_road': 0}
        consumes = (0, 0, 0)  # nessun consumo dichiarato: il sito non si muove

    fields = {
        'physical_characteristics': physical,
        'cost': cost,          # M$ [S], non consumato dal motore (il costo dell'asset viene dal Context)
        'range': range_km,     # km di autonomia [S] (segnaposto per 'fixed')
        'engine': None,        # il motore non e' il soggetto del record; l'autonomia si legge da `range`
        'weapons': {},         # nessun armamento
        'TVD': False,
        'communication': {
            'model': 'generic comm model',
            'capabilities': {'navigation_accuracy': 0.3, 'communication_range': 100},
            'reliability': {'mtbf': 45, 'mttr': 3},
        },
        'protections': {'active': None, 'armor': {}, 'reactive': {}},  # nessuna corazza (mezzo non protetto)
        'hydraulic': False,    # non modellato
        'speed_data': {
            'sustained': {'metric': 'metric', 'speed': speeds['sustained'], 'consume': consumes[0]},
            'max': {'metric': 'metric', 'speed': speeds['max'], 'consume': consumes[1]},
            'off_road': {'metric': 'metric', 'speed': speeds['off_road'], 'consume': consumes[2]},
        },
    }

    if mobility == 'fixed':
        fields['fixed_site'] = True

    return fields
```
`consume` dei veicoli non e' letto da nessun modulo (il carburante dei veicoli usa `range`; l'unico `'consume'` letto
e' quello degli aerei, `Logic/Fuel_Model.py:1025`) [V].

### C.3 `Asset/Vehicle_Data.py`: record dei siti fissi (chiavi stabili)

Posizione: subito dopo `AN_TPS43_data` (`:4823`), prima di `# SETUP DICTIONARY VALUE`, con l'intestazione:
```python
# Siti EWR FISSI (D-4b, blocco C; Proposta_Dati_Sensori_EWR_Siti_Fissi.md, decisioni dell'utente del 2026-11-05):
# Vehicle IMMOBILI con il marcatore `fixed_site` (da `_ewr_support_fields('fixed')`). Stessa forma del radar del
# nucleo mobile: sola scoperta aria, tracking/engagement 0, multi_target 0 = "non trovato". AN/FPS-117 = riferimento di
# migliore fonte. AN/FPS-20 ESCLUSO (contraddizione di fonte 322/407 km, conf. bassa).
```
Forma di ogni record (come il blocco B):
```python
<Variabile> = {
    **_ewr_support_fields('fixed'),
    'constructor': <constructor>,
    'model': <chiave>,
    'made': <made>,
    'users': <users>,
    'start_service': <anno>,
    'end_service': <anno o None>,
    'category': 'EWR',
    'roles': ['EWR'],
    'radar': {
        'model': <nome radar>,
        'capabilities': {
            'air': (True, {'tracking_range': 0, 'acquisition_range': <km>, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
            'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        },
        'reliability': <reliability>,
        # <commento obbligatorio della tabella C.3-b>
        # 'antenna_height' e 'acquisition_profile' solo dove indicati nella tabella C.3-b.
    },
}
```
`roles` non deve contenere `AAA`/`SHORAD`/`MERAD`/`LORAD` (letti da `sam_category`).

**Tabella C.3-a, anagrafica** (ordine = ordine di definizione e di registrazione):

| Variabile | `model` (chiave) | `constructor` | `made` | `start_service` | `end_service` | `users` | `radar['model']` |
|---|---|---|---|---|---|---|---|
| `AN_FPS117_data` | `'AN-FPS-117'` | `'Lockheed'` | `'USA'` | 1983 | None | `['USA']` | `'AN/FPS-117 (Seek Igloo)'` |
| `Chain_Home_data` | `'Chain-Home'` | `'non trovato'` | `'UK'` | 1938 | 1955 | `['UK']` | `'Chain Home (AMES Type 1)'` |
| `AMES_Type7_data` | `'AMES-Type-7'` | `'non trovato'` | `'UK'` | 1941 | None | `['UK']` | `'AMES Type 7 (GCI)'` |
| `AMES_Type80_data` | `'AMES-Type-80'` | `'non trovato'` | `'UK'` | 1955 | 1993 | `['UK', 'Canada', 'Sweden']` | `'AMES Type 80 (Green Garlic)'` |
| `Wassermann_data` | `'Wassermann'` | `'non trovato'` | `'Germany'` | 1942 | 1945 | `['Germany']` | `'Wassermann (FuMG 41 L / 42 S)'` |
| `Mammut_data` | `'Mammut'` | `'non trovato'` | `'Germany'` | 1944 | 1945 | `['Germany']` | `'Mammut'` |
| `P14_Lena_data` | `'P-14-Lena'` | `'non trovato'` | `'USSR'` | 1959 | 2003 | `['USSR', 'Bulgaria', 'China', 'Egypt', 'Iraq', 'Serbia', 'Vietnam']` | `'P-14 Lena (Tall King)'` |

Note all'anagrafica (da riportare come commento breve nel record, accanto al campo):
- FPS-117: `start_service` 1983 = accettazione Seek Igloo; produzione dal 1980. `users`: la fonte parla di >15
  operatori senza elencarli nella ricerca; si scrive il solo `'USA'`. Il costruttore e' la fonte stessa (scheda
  Lockheed). Il tipo d'unita' DCS "FPS-117" (Proposta A/B §5.3) resta un commento, non una chiave;
- Type 7: `end_service` None = "fine non precisa (anni '60, sostituito da Linesman/Mediator)";
- Type 80: servizio operativo dal 1955 (installazione 1953); Canada = 1 sito a Metz; Svezia = PS-08 1957-79;
- Wassermann e Mammut: date dubbie nella fonte ("1942?", "1944?"; radartutorial 1940 per il Wassermann). Mammut:
  designazioni FuMG confuse fra le fonti, quindi la chiave non porta il numero FuMG;
- P-14: il record e' la versione statica 1RL113; la mobile 5N84A (6 rimorchi, oltre 24 h di montaggio) non e'
  modellata a parte. Costruiti 731 o ~2000 (contraddizione).

**Tabella C.3-b, sensore** (`acquisition_range` in km, regola (a) del blocco B: portata contro un caccia alla quota
di crociera se la fonte la da', altrimenti il miglior valore disponibile, marcato):

| Modello | `acquisition_range` | `reliability` | `antenna_height` | `acquisition_profile` | Commento obbligatorio nel codice |
|---|---|---|---|---|---|
| AN-FPS-117 | 330 | `{'mtbf': 2000, 'mttr': 0.75}` | — | — | "330: FONTE (scheda Lockheed via riassunto di ricerca), Pd 80 % contro 1 m2, quota del bersaglio non specificata, conf. media-alta; portata strumentale 10-470 km NON usata. reliability: FONTE (Lockheed, EverythingRF), MTBF critico >2000 h (limite inferiore), MTTR <45 min = 0.75 h (conversione D, limite superiore), conf. media-alta; l'unico EWR con entrambi di fonte (decisione C-2). Riferimento di migliore fonte dei siti fissi" |
| Chain-Home | 160 | `{'mtbf': 45, 'mttr': 4}` | 73.0 | — | "160: FONTE (infobox Wikipedia), bombardieri ad alta quota, conf. media; CONTRADDIZIONE 160/190 km (testo 'tipicamente 120 mi'). Copertura scarsa sotto 2 gradi di elevazione (fonte): il pianificatore la sovrastima a bassa quota. antenna_height 73: DEDOTTO, torri riceventi da 73 m (trasmittenti 110 m), limite superiore. reliability: STIMA [S] generica del registro (decisione 12), non dato di fonte" |
| AMES-Type-7 | 140 | `{'mtbf': 45, 'mttr': 4}` | — | `((150, 16), (6100, 140))` | "140: FONTE (Wikipedia, 'in pratica'; 410 km teorici NON usati) contro un bombardiere a 6100 m (non 10 000), conf. media; a quota piu' alta la portata reale e' probabilmente maggiore. Profilo: FONTE, bombardiere. Antenna in pozzo a terra, altezza non data: default EWR 20 m [S]. reliability: STIMA [S] generica (decisione 12)" |
| AMES-Type-80 | 390 | `{'mtbf': 45, 'mttr': 4}` | 11.4 | — | "390: FONTE (Wikipedia, testo) caccia grande o bombardiere piccolo 'rilevato affidabilmente oltre 210 nmi', quota alta, conf. media; infobox 'migliore di 240 nmi (440 km)' NON usato. antenna_height 11.4: DEDOTTO, torre piramidale 25 ft (7.6 m) + meta' riflettore alto 25 ft (3.8 m). reliability: STIMA [S] generica (decisione 12)" |
| Wassermann | 190 | `{'mtbf': 45, 'mttr': 4}` | 37.0 | `((50, 35), (6000, 190))` | "190: FONTE (sezione tecnica Wikipedia) a 6000 m di quota (non 10 000), conf. media; 300 km = portata massima/strumentale, NON usata; probabile sottostima a quota di crociera. Profilo: FONTE. antenna_height 37: DEDOTTO, minimo dell'intervallo 37-57 m del traliccio (L ~40 m, S 60 m), limite superiore. Banda e designazione contraddittorie fra le fonti. reliability: STIMA [S] generica (decisione 12)" |
| Mammut | 300 | `{'mtbf': 45, 'mttr': 4}` | — | — | "300: FONTE DEBOLE trattata come STIMA (infobox e testo Wikipedia; tabella tecnica 325), bersaglio NON qualificato, conf. media-bassa; potenza contraddittoria (20/200 kW). Fascio su un arco di 100 gradi: il modello lo tratta come omnidirezionale (limite). reliability: STIMA [S] generica (decisione 12)" |
| P-14-Lena | 400 | `{'mtbf': 45, 'mttr': 4}` | — | — | "400: FONTE DEBOLE trattata come STIMA (infobox Wikipedia en), NON qualificato, conf. bassa-media; altre fonti 40-540 km e 593 km strumentali. Portata contro caccia/quota: non trovata. reliability: STIMA [S] generica (decisione 12)" |

Ordine della disuguaglianza `acquisition >= tracking >= engagement` rispettato (x >= 0 >= 0). Le chiavi
`antenna_height` e `acquisition_profile` stanno dentro il dizionario `radar`, come nello SCR-270 (`:4655-4656`).

**Registrazione**, subito dopo `Vehicle_Data(**AN_TPS43_data)` (`:4915`), nello stesso ordine della tabella:
```python

# Siti EWR fissi (D-4b, blocco C)
Vehicle_Data(**AN_FPS117_data)
Vehicle_Data(**Chain_Home_data)
Vehicle_Data(**AMES_Type7_data)
Vehicle_Data(**AMES_Type80_data)
Vehicle_Data(**Wassermann_data)
Vehicle_Data(**Mammut_data)
Vehicle_Data(**P14_Lena_data)
```
Le altre registrazioni non si spostano.

### C.4 `Logic/Air_Route_Manager.py`: solo testo

Commento sopra le costanti d'antenna (`:649-658`): sostituire le righe da "Oggi la dichiara solo il record SCR-270"
fino a "che ha il dato di registro);" con:
```python
# `radar`/`TVD`/`visual`. La dichiarano gli EWR SCR-270 (16,8 m, DEDOTTO: antenna alzata a 55 ft) e tre siti fissi
# (blocco C): Chain-Home 73 m, Wassermann 37 m, AMES-Type-80 11,4 m, tutti DEDOTTI (limiti superiori, v. i record);
# tutti gli altri record usano le stime per classe qui sotto.
#   veicolo  ~5 m: radar su scafo/torretta di un mezzo semovente (SA-6, SA-8, Tunguska, ...);
#   EWR      ~20 m: radar di scoperta su palo o sito predisposto; STIMA per gli 11 record EWR senza
#            `antenna_height` (Freya, P-12, P-18, P-37, 1L13, 55Zh6, AN/TPS-43, AN-FPS-117, AMES-Type-7,
#            Mammut, P-14-Lena; gli EWR sono 15: 8 mobili/semimobili e 7 siti fissi);
```
La riga del "nave ~30 m" resta. Nessuna modifica al codice del modulo.

### C.5 `Test/Test_Vehicle_Data.py`: adattare un test esistente

`TestSpeedEval.test_all_vehicles_speed_eval_positive` (`:713-717`), nuovo corpo:
```python
    def test_all_vehicles_speed_eval_positive(self):
        # I siti fissi (marcatore `fixed_site`, D-4b blocco C) hanno velocita' 0 per dato: li verifica Test_EWR_Data.
        for model, obj in Vehicle_Data._registry.items():
            if getattr(obj, 'fixed_site', False):
                continue
            with self.subTest(model=model):
                score = obj._speed_eval()
                self.assertGreater(score, 0.0)
```
Nessun'altra modifica ai test esistenti. In particolare **non** si tocca `test_range_is_positive_number`: il
segnaposto 1 lo soddisfa.

### C.6 `Test/Test_EWR_Data.py`: test nuovi (15)

Aggiornare il docstring di modulo con un punto: "i 7 siti fissi del blocco C (marcatore `fixed_site`, velocita' 0,
autonomia segnaposto; Proposta_Dati_Sensori_EWR_Siti_Fissi.md)". Import da aggiungere:
```python
from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data, P18_Terek_data, MTLB_data
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control, target_class
from Code.Dynamic_War_Manager.Source.Context import Context
```
(`MTLB_data` esiste, `Asset/Vehicle_Data.py:2731`; `Context.TARGET_CLASS_AIR_DEFENCE` e' la costante usata da
`target_class`.) Costanti di modulo:
```python
# modello -> acquisition_range [km] dei siti fissi (tabella C.3-b).
FIXED_SITE_MODELS = {
    'AN-FPS-117': 330,
    'Chain-Home': 160,
    'AMES-Type-7': 140,
    'AMES-Type-80': 390,
    'Wassermann': 190,
    'Mammut': 300,
    'P-14-Lena': 400,
}
FIXED_SITE_RELIABILITY = {'AN-FPS-117': {'mtbf': 2000, 'mttr': 0.75}}   # gli altri: 45/4 (decisione 12)
FIXED_SITE_PROFILES = {
    'AMES-Type-7': ((150, 16), (6100, 140)),
    'Wassermann': ((50, 35), (6000, 190)),
}
FIXED_SITE_REFERENCE_QUOTAS = {'AMES-Type-7': 6100, 'Wassermann': 6000}
FIXED_SITE_ANTENNA = {'Chain-Home': 73.0, 'AMES-Type-80': 11.4, 'Wassermann': 37.0}
```

**`TestEWRFixedSiteRecords(unittest.TestCase)`**, con setUp e tearDown del logger come `TestEWRRecords`:
1. `test_fixed_sites_are_registered`: per ogni chiave di `FIXED_SITE_MODELS`, `category == 'EWR'`,
   `roles == ['EWR']`, `fixed_site is True`.
2. `test_only_the_fixed_sites_carry_the_marker`: per ogni record del registro, `isinstance(record.fixed_site, bool)`
   e `record.fixed_site == (model in FIXED_SITE_MODELS)`. Copre gli 8 EWR mobili e i 64 record precedenti
   (default False).
3. `test_fixed_sites_declare_zero_speed`: per ogni record con `fixed_site` True, i tre regimi di `speed_data`
   hanno `speed == 0` e `metric == 'metric'`, `_speed_eval() == 0.0` e `range == 1` (segnaposto).
4. `test_fixed_site_radar_is_an_air_only_search_sensor`: `air[0]` True, `ground[0]`/`sea[0]` False; `tracking_range`,
   `engagement_range` e `multi_target_capacity` aria = 0; `weapons == {}`, `TVD is False`, `visual is None`.
5. `test_fixed_site_acquisition_ranges_match_the_plan`: `acquisition_range` aria == `FIXED_SITE_MODELS[model]`.
6. `test_fixed_site_reliability`: `radar['reliability'] == FIXED_SITE_RELIABILITY.get(model, {'mtbf': 45, 'mttr': 4})`.
7. `test_fixed_site_acquisition_profiles_are_consistent`: come `test_acquisition_profiles_are_consistent` del blocco
   B, sui profili di `FIXED_SITE_PROFILES` e sulle quote di `FIXED_SITE_REFERENCE_QUOTAS`; gli altri siti non hanno
   la chiave `acquisition_profile`.
8. `test_fixed_site_antenna_heights`: per i tre di `FIXED_SITE_ANTENNA` il valore e' quello; gli altri quattro siti
   non hanno la chiave `antenna_height`.
9. `test_constructor_defaults_fixed_site_to_false`: `copy.deepcopy(MTLB_data)` con `model='test-fixed-default'`, si
   costruisce e si verifica `fixed_site is False`; `Vehicle_Data._registry.pop('test-fixed-default', None)` in `finally`.
10. `test_constructor_rejects_a_non_bool_marker`: `copy.deepcopy(MTLB_data)` con `model='test-fixed-invalid'` e
    `fixed_site='yes'`, `assertRaises(ValueError)`. Poi `'test-fixed-invalid' not in Vehicle_Data._registry`, e
    comunque `pop` in `finally`.

**`TestEWRFixedSitesKeepTheCombatScores(unittest.TestCase)`**, con il logger mockato:
11. `test_fixed_site_global_combat_scores_in_unit_interval`: per i 7 siti,
    `0.0 <= get_normalized_combat_score() <= 1.0`. L'invarianza dei record esistenti e' gia' coperta dal test
    `test_global_combat_scores_of_existing_models_ignore_ewr`, che esclude per categoria e quindi copre anche i siti.

**`TestEWRFixedSitesAsAssets(F.LoggerSilencer, unittest.TestCase)`**. `setUpClass`: forza `F.make_force('EWR-Fixed', 'Red')`
con `F.make_vehicle` per `'AN-FPS-117'` in `(0.0, 0.0, 0.0)` (id `'EWR-Fixed/fps117'`), `'Chain-Home'` in
`(100.0, 0.0, 0.0)` (`'EWR-Fixed/ch'`), `'AMES-Type-80'` in `(200.0, 0.0, 0.0)` (`'EWR-Fixed/t80'`), poi `F.add_assets`.
12. `test_fixed_site_vehicle_does_not_move_or_burn_fuel` (FPS-117):
    - `speed['nominal'] == 0.0`, `speed['max'] == 0.0`, `speed['off_road']['nominal'] == 0.0`,
      `speed['off_road']['max'] == 0.0`;
    - `FM.cruise_speed(asset) is None` e `FM.max_speed(asset) is None`;
    - `fuel_autonomy() == 1000.0`, `fuel == 1.0`;
    - `isEWR` True, tutti i valori di `combat_power(force='ground')` (dopo `set_combat_power()`) sono 0.
13. `test_fixed_site_gives_detection_without_interception`:
    - `air_defense_threats() == []`;
    - `air_detection_threats(10000.0)`: FPS-117 raggio `330000.0`, `sensor == 'radar'`;
    - `air_detection_threats(500.0)`: FPS-117 == `radar_horizon_range(SENSOR_HEIGHT_EWR_M, 500.0)`, Chain-Home ==
      `radar_horizon_range(73.0, 500.0)`, Type 80 == `radar_horizon_range(11.4, 500.0)`.
14. `test_fixed_site_is_an_air_defence_emitter_outside_the_rwr_catalogue` (FPS-117):
    - `ADE.emits_radar` True, `ADE.sam_category` None, `ADE.air_defense_profile` None;
    - `target_class(asset) == Context.TARGET_CLASS_AIR_DEFENCE`;
    - nessuna chiave di `FIXED_SITE_MODELS` fra i `_model` di `ADE.default_rwr_catalogue()`.
15. `test_fixed_site_in_a_session_detects_and_never_fires`: come `test_ewr_in_a_session_detects_and_never_fires`, con
    `F.Unit('vehicle', 'AN-FPS-117', 1, origin=(0.0, 0.0), prefix='ewr')` nella forza `'Red-EWR-Fixed'`, la stessa
    forza CAS, missione e `BOTH_HOLD`, sessione `'EWR-fixed-session'`. Asserzioni:
    - nessun `AmmunitionEvent` con `asset_id == 'Red-EWR-Fixed/ewr0'`;
    - nessun evento in `outcome.fuel_events` con quell'`asset_id`.

Nessuna unita' nuova nella fotografia e nessuna modifica a `Test/Scenario_Baseline.py`.

### C.7 Vincoli e verifiche

- **RNG**: nessuna estrazione nuova, nessun ordine cambiato; nessuno scenario esistente istanzia un EWR. Nessun uso
  del modulo `random`.
- **Core indifferente al simulatore**: nessun riferimento a DCS; "FPS-117" solo in commento.
- **Nomi stabili**: le 7 chiavi di C.3-a; le chiavi degli 8 EWR B e dei 64 record precedenti invariate.
- **Costanti**: tutte quelle di C.2 sono [S] o SEGNAPOSTO, dichiarate nel codice; i valori di C.3-b portano il commento
  obbligatorio. Riportarle nel rapporto.
- **Interruttore**: nessuno (§1.6).
- **Verifiche** con `tools/ai/verifica.sh` (suite, poi confronto, mai in parallelo). Un solo file:
  `<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_EWR_Data`.

### C.8 Esito atteso

- **Suite**: `Ran 4757` (4742 + 15 test nuovi di C.6; il test adattato in C.5 non cambia il conteggio), `OK`,
  `skipped=7`. Se il conteggio differisce, elencare la differenza. Se fallisce un test diverso da quelli nuovi,
  **fermarsi e riferire**: la sonda S-3 (§1.7.1) dice quali test esistenti sono sensibili ai siti.
- **Confronto con la fotografia**: **1009 IDENTICHE, 0 CAMBIATE, 0 NUOVE**. Motivi:
  - nessuno scenario istanzia un EWR;
  - il combat score globale dei record esistenti non cambia (G2);
  - catalogo RWR e pesi di classe invariati;
  - il DES non legge gli score del registro e nessuna regola legge `fixed_site`.

  Una sola esecuzione cambiata o nuova e' un'anomalia: fermarsi e riferire.
- **Non installare** nessuna fotografia.

---

## 5. Rischi e limiti

### 5.1 Valori deboli che entrano nel codice

| Valore | Tipo | Confidenza | Nota |
|---|---|---|---|
| AN/FPS-117 330 km | F | media-alta | 1 m2 Pd 80 %; quota non specificata; dato letto via riassunto (PDF non estraibile) |
| AN/FPS-117 mtbf 2000 / mttr 0,75 | F / D | media-alta | limiti (">2000 h", "<45 min"), quindi prudenti (C-2) |
| Chain Home 160 | F | media | contraddizione 160/190; bombardieri, non caccia |
| AMES Type 7 140 | F | media | bombardiere a 6100 m; profilo 16/140 di fonte |
| AMES Type 80 390 | F | media | caccia grande/bombardiere piccolo; 440 alternativo |
| Wassermann 190 | F | media | **a 6000 m**, non 10 000; 300 = strumentale; date dubbie |
| **Mammut 300** | F debole → **STIMA** | **media-bassa** | non qualificato; tabella 325; potenza contraddittoria |
| **P-14 400** | F debole → **STIMA** | **bassa-media** | non qualificato; 40-540 / 593 km in altre fonti |
| Antenne 73 / 37 / 11,4 m | D | media | limiti superiori (C-3); gli altri 4 siti 20 m [S] |
| Velocita' 0 | dato | — | vero per definizione di sito fisso |
| `range` 1 km | SEGNAPOSTO | — | non un'autonomia |
| Dimensioni 30x10x20 m, 50 t; costo 10 M$ | S | — | un solo punto (`_ewr_support_fields('fixed')`); classe 'big' |
| `multi_target_capacity` 0, `tracking_range` 0 | — | — | "non trovato" (decisioni 10-11 del blocco B) |
| `reliability` 45/4 dei 6 siti non FPS-117 | S | — | decisione 12 |

### 5.2 Limiti di modello (da dichiarare nel manuale)

1. **Immobilita' non imposta dal motore** (C-4). La velocita' 0 esclude il sito dalla regola A
   (`Logic/Mission_Adapter.py:1191-1194`), non lo blocca. Una missione che lo muovesse lo farebbe muovere alla
   velocita' pianificata, fino all'esaurimento dell'autonomia segnaposto di 1 km (troncamento F6-A). Oggi nessuna
   missione lo fa: nessuno scenario, inventari EWR vuoti.
2. **Il DES non ha orizzonte radar** (limite gia' dichiarato). Le portate da 300-400 km dei siti si applicano nel DES
   anche ai bersagli radenti. Con un raggio cosi' grande lo scheduler apre finestre di contatto con aerei molto
   lontani; il costo di calcolo non e' misurato, perche' nessuno scenario ha un sito.
3. **Copertura angolare**: Mammut (arco di 100 gradi) e Chain Home (150 gradi) sono modellati come omnidirezionali; il
   core non ha settori di scoperta.
4. **Torri non rappresentate**: le dimensioni del sito sono una stima generica, quindi il bersaglio e' 'big' ma non
   alto 110 m (Chain Home). La vulnerabilita' all'attacco non e' tarata.
5. **Siti WWII a lettura manuale** (Chain Home, Type 7, Wassermann, Mammut): nessuna latenza di plotting, come gia'
   per Freya e SCR-270.
6. **RWR**: i siti emettono ma restano fuori dal catalogo RWR (`sam_category` None), come gli EWR mobili.
7. **Nessun cueing** EWR→SAM (D-7 fuori perimetro).
8. **Score di categoria EWR spostati** per gli 8 EWR mobili: oggi nessun consumatore. Un consumatore futuro dovra'
   tenerne conto.
9. **Migrazione a `Structure`** (opzione B, futura): il marcatore la rende meccanica nel registro. Pero' `Structure`
   oggi non ha `detection_range` ne' i metodi di `Mobile` (velocita', carburante, sensori). La migrazione richiedera'
   codice, non solo dati.

### 5.3 Rischi di esecuzione

- **Rami di `_ewr_support_fields`**: un ritocco involontario dei valori `'mobile'`/`'semi_mobile'` cambierebbe gli 8
  record B. I test B esistenti (portate, reliability, antenna) non controllano dimensioni e velocita'. L'esecutore
  deve confrontare il diff delle righe di quei due rami: atteso nessun cambiamento di valore.
- **Ordine di validazione nel costruttore**: il controllo di `fixed_site` va **prima** di
  `Vehicle_Data._registry[self.model] = self`, altrimenti il test 10 trova il record invalido nel registro.
- **Conteggio dei test**: 15 nuovi. Se l'esecutore unisce o separa dei test, il `Ran` cambia: va riferito.

---

## Documenti da aggiornare dopo (non scritti qui)

- `Analysis/Document/Manuale_Motore_DES/`:
  - cap. 3 (`04_Strato1_Scheduler_Contatti.md` §3.5): nota che i siti fissi rilevano con le portate del registro anche
    senza orizzonte nel DES (§5.2 punto 2);
  - cap. 7 (`08_Supporto_Trasversale.md`): §7.8, testo dell'altezza d'antenna (`:515`, `:519`: ora 15 EWR, tre siti con
    `antenna_height`); §7.12, voce nuova "Siti EWR fissi (D-4b blocco C)" con il marcatore `fixed_site`, il ramo
    `'fixed'`, le 7 chiavi e la riga `:574` (blocco C fatto);
  - cap. 8 (`09_Validazione.md` §8.13): i 15 test nuovi e il test adattato `test_all_vehicles_speed_eval_positive`;
  - cap. 9 (`10_Limiti_Estensioni_Divergenze.md`): `:616` da "non fatti" a "fatti" (AN/FPS-20 escluso), limiti di
    §5.2 (immobilita' non imposta, copertura angolare, torri), §9.4 riepilogo;
  - cap. 10 (atlante, `11_Atlante_Diagrammi.md`, `11a`-`11c`): solo una nota come quelle del 2026-11-04
    (`11a_Atlante_Risolutore.md:1446`, `11c_Atlante_Porte_Campagna.md:1209`). Il blocco C tocca `Asset/Vehicle_Data.py`,
    il commento di `Logic/Air_Route_Manager.py` e i test, ma nessun modulo del core descritto nell'atlante. I `:riga`
    di `Air_Route_Manager` dopo `:649` vanno ricontrollati, perche' il commento cambia lunghezza: +1 riga se il testo
    di C.4 e' quello indicato.
- `Analysis/Document/F4_Differenze_Scenari.md`, sezione "D-4c e D-4b" (`:2628`): riga del blocco C nella tabella e
  `:2683` aggiornata (nessuna differenza, 1009 identiche).
- `Analysis/Document/Piano_Implementazione_Missione.md`, riga D-4b/D-4c (`:310`) e intestazione (`:3`): siti fissi
  fatti.
- `Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md` §4 "Blocco C": rimando a questo documento (gia' aggiunto).
- `Analysis/Document/Ricerca_EWR_2026_10_29.md`: nessuna modifica (fonte).
- Memoria `project_detection_interception_volumes` e `project_sensori_d4b_d4c` (solo la sessione principale): blocco
  C fatto, con il commit; aperti curva portata-quota (opzione (c)), immobilita' imposta (C-4), D-7.

## Scelte minori lasciate all'esecutore (da elencare nel rapporto)

- Testo dei docstring e dei commenti brevi dell'anagrafica (C.3-a), nello stile del file, purche' i commenti
  obbligatori di C.3-b ci siano e dicano FONTE/DEDOTTO/STIMA e la confidenza.
- Nomi delle variabili locali e delle funzioni d'appoggio nei test; struttura interna di `setUpClass`, purche' gli id
  degli asset siano quelli di C.6 e i test siano 15.
- Messaggio esatto della `ValueError` di `fixed_site`, purche' contenga il valore ricevuto.
