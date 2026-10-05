# Capitolo 7 — Moduli di supporto trasversali

## 7.1 `Utility/Session_Rng.py` — l'unica sorgente di casualità

Disciplina trasversale a tutto il motore (`Utility/Session_Rng.py:1-9`): "RNG di sessione
seedato da (session_id, mission_id, event_id, contatore). Ogni estrazione stocastica passa da
lì. L'ordine di risoluzione degli eventi fa parte del contratto — salvare solo il seed non
basta, perché un PRNG riproduce la stessa sequenza solo a parità di ordine delle chiamate."

### Contratto (`:14-30`)

1. **Seed = funzione pura della chiave** `(session_id, mission_id, event_id, counter)`, tutti
   valori di dominio (mai un id del simulatore).
2. **Stabile fra processi, macchine e versioni di Python**: niente `hash()` (randomizzato per
   processo via `PYTHONHASHSEED`, non garantito fra versioni). Si usa **SHA-256** su una codifica
   canonica JSON (con i tipi preservati: `"1"` e `1` sono chiavi diverse, `None` è distinto da
   `"None"`), troncato a `SEED_BITS = 64` bit (`session_seed`, `:70-102`). `random.Random(int)` è
   a sua volta stabile: il seeding da intero e il Mersenne Twister di `random()` non dipendono da
   hash di processo.
3. **Una chiave, uno stream**: ogni valore di `counter` apre uno stream diverso — un evento che
   deve fare più estrazioni indipendenti da un altro evento usa un `counter` diverso. Dentro uno
   stream, l'ordine delle estrazioni resta parte del contratto (es. quello di
   `Engagement_Resolver`, capitolo 4 §4.11).
4. **Mai `random` di modulo**: ogni funzione restituisce un'istanza esplicita.

`SEED_SCHEME = 'warfare-model/session-rng/v1'` (`:48-51`) entra nell'hash: un cambio futuro della
codifica canonica produce seed diversi **in modo dichiarato**, invece di riprodurre in silenzio
sequenze diverse sotto la stessa etichetta.

`session_rng(session_id, mission_id=None, event_id=None, counter=0) -> random.Random`
(`:105-113`) è la funzione consumata direttamente da `SessionOrder.rng(...)` (capitolo 2, §2.2) e
da `Session_Simulator.run_session` (capitolo 6, §6.4). Ogni chiamata restituisce un'istanza
**nuova** posizionata all'inizio dello stream.

## 7.2 `Context/Doctrine.py` — soglie di disingaggio (P1 + R2), soglia di rottura stocastica, dottrina di tiro

`Context/Doctrine.py` (397 righe a `533cd1f5`, 271 modificate dal 2026-09-29) custodisce la **dottrina di
lato**: parametri di bilanciamento, non una costante del risolutore, non un parametro di sessione, non una
proprietà del singolo asset, valutati **per forza intera** (`Context/Doctrine.py:60-68`). Due blocchi,
oltre ai pesi di priorità di targeting (`:13-57`, usati da `Tactical_Evaluation`, fuori dal motore).

### Soglie di disingaggio: erosion e shock (`:60-85`)

- `'erosion'` — frazione **cumulata** dell'organico impegnato non più operativo: la forza si logora
  lentamente;
- `'shock'` — frazione persa in **un singolo impulso** (una sola salva risolta): la forza si rompe per un
  colpo improvviso anche se le perdite cumulate sono ancora sotto `erosion`.

Entrambe sono frazioni dell'**organico impegnato all'inizio dell'ingaggio** (non della forza superstite):
con lo stesso denominatore la perdita di una salva non può mai superare la perdita cumulata, quindi
`shock <= erosion` è un vincolo di coerenza verificato (`validate_disengagement_thresholds`,
`:231-278`) — altrimenti la soglia di shock non scatterebbe mai per prima e sarebbe un parametro morto.

**Dal 2026-09-29 queste due chiavi non sono più soglie fisse ma la mediana** della soglia di rottura
stocastica B(t) (decisioni D1-D9, `Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md`; uso nel
risolutore: capitolo 4 §4.7 e §4.21). I parametri aggiuntivi (`:87-131`, **tutti facoltativi**;
`DISENGAGEMENT_OPTIONAL_KEYS`, `:158`):

| Chiave | Default di lato (`_DEFAULT_SIDE_DOCTRINE`, `:160-172`) | Valore neutro (`DISENGAGEMENT_NEUTRAL`, `:147-157`) | Vincolo (`_validate_optional`, `:197-228`) |
|---|---|---|---|
| `erosion` (mediana) | 0.30 | — (obbligatoria) | (0, 1]; 1 = ad oltranza |
| `shock` | 0.20 | — (obbligatoria) | (0, 1], `shock <= erosion` |
| `dispersion` (σ logit-normale) | 0.5 | 0.0 | ≥ 0 |
| `morale_weight` | 0.3 | 0.0 | [0, 1) |
| `force_ratio_exponent` | 0.5 | 0.0 | ≥ 0 |
| `force_ratio_bounds` | (0.6, 1.5) | (0.6, 1.5) | 0 < low ≤ 1 ≤ high |
| `air_force_ratio_scale` | 2.0 | 2.0 | > 0 |
| `unanswered_fire_weight` | 0.3 | 0.0 | [0, 1) |
| `defensive_posture_factor` | 1.2 | 1.0 | > 0 |
| `shock_min_losses` | 2 | 1 | intero ≥ 1 |
| `median_bounds` | (0.05, 0.95) | (0.05, 0.95) | 0 < low ≤ high < 1 |

Una tabella con le **sole** `erosion`/`shock` si comporta esattamente come le soglie fisse precedenti al
2026-09-29 (modalità deterministica: test e scenari "ad oltranza", `:110-113`); la tabella di default
(`DEFAULT_DISENGAGEMENT_THRESHOLDS`, `:174-178`) dichiara tutti i parametri, con **gli stessi valori per i
tre lati** — l'asimmetria dottrinale, se voluta, va dichiarata esplicitamente dal chiamante (v. wiki
`decisions/c2-hierarchy-design`), mai introdotta di nascosto da un default (`:128-131`).

### Valori di default — **STIMA DI PARTENZA DICHIARATA, non dati validati** (`:115-127`)

- `erosion = 0.30` — regola empirica diffusa nella letteratura militare per cui un'unità scesa sotto
  ~70% dell'organico non è più pienamente efficace in combattimento: un ordine di grandezza, non una
  misura;
- `shock = 0.20` — nessuna fonte: scelto solo per essere strettamente minore di `erosion`;
- `dispersion = 0.5` — deviazione standard ~0.10 attorno a 0.30, 90% delle soglie fra 0.16 e 0.49: le
  soglie di rottura storiche sono una distribuzione, non un valore (`:123-124`);
- gli altri sono stime dichiarate della proposta, senza fonte.

Da ricalibrare con il processo **ATCAL interno** (risolutore fine fatto girare offline), mai con numeri
da fonti non validate — in particolare **nessun coefficiente dei documenti Lanchester ingeriti**
(coerente con l'avvertimento metodologico permanente della wiki `decisions/virtual-session-engine-des`).

`get_disengagement_thresholds(side, thresholds=None) -> Optional[Dict]` (`:281-301`) restituisce una
**copia** della voce del lato (le chiavi facoltative assenti restano assenti), o `None` se il lato non ne
dichiara — è `Engagement_Resolver` a decidere la propria politica su `None` (combatte fino
all'annientamento, con un warning — tranne per i blocchi non-Military, v. capitolo 4 §4.7);
`disengagement_parameter(entry, key)` (`:304-312`) restituisce il valore dichiarato o quello neutro.

### Dottrina di tiro: saturazione e "due missili, poi guarda" (`:315-397`, 2026-09-29)

`DEFAULT_FIRE_DOCTRINE` (`:341-345`): per lato `kill_probability_threshold = 0.9` (decisione O3 dell'utente)
e `max_rounds_in_flight = 2` (la dottrina reale dei SAM *shoot-shoot-look*, decisione dell'utente); uso nel
risolutore: capitolo 4 §4.25. Un lato assente dalla tabella, o una chiave `None`, non ha la regola;
`validate_fire_doctrine` (`:348-383`) ammette soglia in (0, 1] e tetto intero ≥ 1; `get_fire_doctrine`
(`:386-397`) restituisce una copia con entrambe le chiavi (un lato sconosciuto dà `{chiave: None}`: dato
mancante, non errore).

## 7.3 `Context/Reaction_Profile.py` — RIV/VAL/COM/ATT

Salva la decomposizione a quattro fasi della "Strategia 1" bocciata come motore a tick
(capitolo 1, §1.1), qui come **parametri per tipo di sistema** che il risolutore usa per
schedulare eventi futuri, non per contare iterazioni
(`Context/Reaction_Profile.py:1-16`).

### Statuto dei numeri (`:18-37`) — leggere prima di usarli

**Sono documentati solo i totali** rilevazione → lancio (tabella §4.2 del documento di
architettura, con fonti in bibliografia): 9K33 Osa ~26 s, S-300P ~28 s, Tor da fermo 5-8 s,
Tor-M2 "short stop" 2-3 s, pilota umano 1-2 s, equipaggio carro ~31 s per bersaglio, IADS:
valutazione minaccia ~1 s, assegnazione arma-bersaglio poche centinaia di ms. Dove la fonte dà un
intervallo si usa il punto medio.

**La scomposizione nelle quattro fasi è una STIMA DICHIARATA**: VAL, COM e ATT prendono gli
ordini di grandezza citati nel testo della Strategia 1 (100 ms di valutazione macchina, 10 s per
un umano; 1 ms di comando automatico, 1 s per un equipaggio manuale; 0,1 s di brandeggio, 0,5 s
di sgancio missile), e **RIV è il residuo** fino al totale documentato. Il totale resta quindi
esattamente quello della fonte; la ripartizione no. Serve comunque, perché le degradazioni future
colpiscono una fase sola (meteo/notte/disturbo sulla RIV, addestramento sulla VAL).

Il risolutore consuma solo due grandezze derivate (`ReactionProfile`, `:81-140`):

- `total` = `detection + evaluation + command + actuation` — latenza del primo ingaggio;
- `refire_interval` = `evaluation + command + actuation` — fra una salva e la successiva contro
  un bersaglio già in traccia (la RIV non si ripete: la traccia è già stabilita).

Un `evaluation + command + actuation` non positivo è rifiutato (`__post_init__`, `:108-112`): un
intervallo di tiro nullo farebbe sparare un asset infinite volte nello stesso istante, e il
risolutore a eventi non terminerebbe.

### Tabella dei profili documentati (`REACTION_PROFILES`, `:165-199`)

| Chiave | Totale documentato | VAL | COM | ATT |
|---|---|---|---|---|
| `9A33-Osa` | 26.0 s | macchina (0.1s) | automatico (0.001s) | sgancio missile (0.5s) |
| `9K331-Tor` | 6.5 s (punto medio di 5-8 s) | macchina | automatico | sgancio missile |
| `9K331-Tor/short_stop` | 2.5 s (punto medio di 2-3 s) | macchina | automatico | sgancio missile |
| `S-300PS` | 28.0 s | IADS (1.0+0.3s) | automatico | sgancio missile |
| `pilot` | — (reazione umana 1-2s, punto medio 1.5s; RIV esclusa) | residuo | automatico | sgancio missile |
| `tank_crew` | 31.0 s (M1 gunnery, DTIC ADA217416) | umana (10s) | manuale (1s) | brandeggio (0.1s) |
| `default` (ripiego) | 31.0 s (il **più lento** dei totali documentati) | umana | manuale | brandeggio |

Il ripiego `default` è deliberatamente il più lento: "la mancanza di un dato non deve regalare
l'iniziativa" (`:193-196`, stessa logica della memoria
`feedback_no_visibility_low_priority` applicata alla latenza).

### `profile_for_asset(asset, skill=None) -> ReactionProfile` (`:260-306`)

Precedenza: (1) modello con profilo documentato (`REACTION_PROFILES[asset._model]`); (2)
`Aircraft` → `pilot`; (3) `Vehicle` SAM/AAA → fabbrica `_air_defense_profile` (riusa
`Air_Route_Manager.threat_reaction_times`, la stessa stima usata dalla pianificazione di rotta
per la stessa minaccia — evita due verità diverse sulla reattività dello stesso sito, `:238-257`);
(4) `Vehicle` con equipaggio (carri, corazzati, motorizzati, artiglieria) → `tank_crew`; (5) tutto
il resto (navi, EWR, classi non riconosciute) → `default`, con un log: nessuna fonte del progetto
documenta latenze navali.

`SKILL` (i livelli DCS Average/Good/High/Excellent) è previsto dalla roadmap come modulatore, ma
`SKILL_LATENCY_FACTOR` è **tutto a 1.0**: nessuna fonte del progetto dà un fattore per livello
(`:39-44`, `:201-203`).

## 7.4 Degradazione ambientale della Pd (meteo/notte)

Vive in `Logic/Engagement_Resolver.py` (non in `Reaction_Profile`), perché è un parametro della
legge di Pd (`Logic/Engagement_Resolver.py:289-301`, `:716-763`):

```
factor = (NIGHT_DETECTION_FACTOR se notte) * (ADVERSE_WEATHER_DETECTION_FACTOR se avverso)
```

`NIGHT_DETECTION_FACTOR = 0.7`, `ADVERSE_WEATHER_DETECTION_FACTOR = 0.8` (notte + meteo avverso =
0.56). **STIMA DICHIARATA**, nessuna fonte del progetto la fornisce; da ricalibrare via ATCAL
interno.

`weather_detection_factor(conditions)` legge `conditions` nella forma di
`Meteo_Analysis.get_meteo_conditions` (`{'day', 'night', 'adverse_weather'}`).
`weather_detection_factor_fn(conditions)` (`:766-780`) produce la callable `(observer, target) -> float`
richiesta da `resolve_engagement(detection_factor=...)`. `meteo_detection_factor(region_name,
date, time)` (`:783-792`) collega le due funzioni a `Logic/Meteo_Analysis.get_meteo_conditions` (oggi un
placeholder deterministico: nessuna casualità entra da qui).

**Limite noto, dichiarato** (`Logic/Engagement_Resolver.py:291-298`): il fattore è **unico per ogni sensore**. La finestra di
contatto porta solo la portata migliore fra radar e TVD (`Mobile.detection_range`, default =
massimo dei due), e il risolutore non sa quale dei due l'ha prodotta: non può quindi risparmiare
al radar la degradazione notturna che fisicamente non subisce. Il valore notturno è un
compromesso fra i due sensori.

## 7.5 Le dimensioni militari di `Block/Military.py`

### `air_defense_power() -> float` (`Block/Military.py:613-650`)

È la dimensione che manca alla combat power: SAM, AAA e EWR valgono 0 nelle tabelle di efficacia
(`Context.GROUND_COMBAT_EFFICACY`) **per definizione**, perché quella misura fuoco e manovra
terra-terra, che loro non hanno — decisione Q3 della wiki
`decisions/virtual-session-engine-des`, confermata intenzionale. La loro potenza esiste, è di
natura diversa: `1 - Π(1 - danger_level_i)` sui `ThreatAA` costruiti dai volumi di difesa aerea
degli asset operativi ("almeno una delle difese è efficace"), saturante in [0,1], monotona nel
numero di siti. **Non è una combat power** e non è confrontabile con quella.

### `salvo_interceptors() -> List[Tuple[asset, canali]]` (`:652-715`)

Elenco degli asset del blocco che possono intercettare colpi in arrivo, ciascuno con i propri canali
(`engagement_channels('air')`, o `DEFAULT_INTERCEPTION_CHANNELS` se non dichiarato). È la base consumata dal
risolutore d'ingaggio (capitolo 4, §4.5) per popolare `_ForceState.interceptors`.

**Dal 2026-09-28 (regole D e F della proposta SAM, capitolo 4 §4.24)**:

- **Selezione**: `Vehicle` o `Ship` operativi con almeno un'arma **intercettrice** — il registro dichiara il
  task `Anti_Missile` (`Mobile.interceptor_capability()`, `Asset/Mobile.py:1119-1131`). Uno Strela-10 o uno
  Shilka pesano nella difesa aerea (`air_defense_power`, fuoco contro aerei) ma **non** intercettano
  munizioni. Per un asset senza dato di registro (modello ignoto, stub, `capability() is None`) vale la
  regola precedente: ogni asset per cui esiste una `ThreatAA`. Prima, "chi pesa nella difesa aerea" e "chi
  intercetta" erano per costruzione lo stesso insieme; oggi il secondo è un sottoinsieme del primo.
- **Ordine**: per `(rango F, id)`: prima gli intercettori a **soli cannoni** (scorta dedicata, si consuma per
  prima), poi quelli con missili (`Weapon_Stores.interceptor_rank`, `Asset/Weapon_Stores.py:242-249`). L'ordine
  di consumo delle scorte fa parte del contratto di riproducibilità.

### `salvo_interception_capacity() -> int` (`:717-771`)

```
capacita = Σ_i min(canali_i, scorta_i)
```

sugli asset di `salvo_interceptors()`. **STIMA DI PARTENZA DICHIARATA**: ogni canale intercetta
**un** colpo per salva (Pk dell'intercettore = 1 per canale — ipotesi ottimistica per la difesa,
primo candidato alla ricalibrazione). La formula non è cambiata dal 2026-09-26: cambia solo
**cosa** legge `scorta_i` (`asset.interceptor_stock`), ora una vista sulla scorta per arma per
chi la ha modellata (v. §7.6 e capitolo 4 §4.19). **Dal 2026-09-28 è un TETTO**, non il numero di colpi
fermabili: il risolutore esclude, salva per salva, gli intercettori dentro il cui volume è partito il
lancio (regola L1) e quelli senza traccia o tempo di reagire (R-INT), capitolo 4 §4.5. Nota: il
risolutore d'ingaggio **non chiama direttamente** questo metodo per calcolare la capacità durante la run
(ricalcola con `_capacity`, capitolo 4, §4.5, che replica la stessa formula sullo stato **ombra**, non
sull'asset reale) — questo metodo resta la funzione di lettura pubblica per chi consulta lo stato reale
fuori da un ingaggio in corso.

## 7.6 Munizioni e carburante su `Asset/Mobile.py` e `Asset/Aircraft.py`

### Munizioni offensive vs intercettori — scorta per modello d'arma (decisione A1/A3, 2026-09-26)

**Aggiornamento rispetto alla stesura iniziale**: fino al 2026-09-26 la scorta era **un
contatore scalare aggregato per asset** (`Mobile.ammunition`, decisione R3 del 2026-09-23), che
sommava armi eterogenee — la fire control sceglieva un'arma per nome, ma il risolutore scalava
sempre lo stesso scalare, indipendentemente da quale arma avesse davvero sparato (un A-10 con 4
Maverick a bordo ne lanciava 642, pagati dai colpi del cannone, v. capitolo 4 §4.19 per il
dettaglio del difetto e della correzione).

Lo stato primario è ora `Mobile._stores: Optional[Dict[str, int]]` = `{modello_arma: quantità}`
(`Asset/Mobile.py:346`, valore iniziale dal registro del modello, `stores_from_registry`,
`:859-903`); `ammunition`/`interceptor_stock` sono **viste calcolate** su di esso, con le regole
di contabilità in un modulo a parte, `Asset/Weapon_Stores.py` (funzioni pure, senza stato: v.
capitolo 4 §4.19 per il dettaglio delle "quattro forme della scorta" e della vista sugli
intercettori), condiviso con lo stato ombra del risolutore (`_Shadow`, capitolo 4 §4.10) perché
le due contabilità non possano divergere.

Due contatori **distinti per scopo** dal 2026-09-23: `Mobile.ammunition` (munizioni offensive,
proprietà a `:750-757`, setter `:759-783` che imposta un pool anonimo per chi forza la scorta a
mano) e `Mobile.interceptor_stock` (intercettazioni ancora possibili, proprietà a `:961-970`, setter `:972-987`).
Per i cannoni AA, `ROUNDS_PER_GUN_INTERCEPT = 100` (**STIMA DICHIARATA**, da ricalibrare,
definita in `Weapon_Stores.py` e re-esportata da `Mobile.py:182`) converte colpi fisici in
intercettazioni (uno Shilka da 2000 colpi → 20 intercettazioni, non 2000). Dal 2026-09-26, per
qualunque asset con armi AD modellate per arma, `interceptor_stock` è una **vista sulle voci AD**
di `stores`: un missile antiaereo lanciato offensivamente e lo stesso missile usato per
intercettare scalano la stessa voce del dizionario, per costruzione. **La vecchia regola del "SAM
puro" (`Mobile.interceptor_shares_ammunition`, che condivideva un intero pool solo per gli asset
a solo missile) è stata eliminata**: non serve più, perché la condivisione per arma copre già
ogni caso (M6-Linebacker, Arleigh Burke, ecc. — v. capitolo 4 §4.19). Senza vista attiva (pool
anonimo, o scorta impostata a mano col setter `interceptor_stock`, `:972-987`) resta il pool
anonimo di intercettori, distinto dalle munizioni come prima del 2026-09-26.

`Mobile.consume_ammunition(rounds, weapon=None)` (`:789-814`) e
`Mobile.consume_interceptor_stock(amount, weapon=None)` (`:1012-1045`) sono i due punti di
applicazione consumati da `apply_engagement_result` (capitolo 4, §4.12): con `weapon` presente in
`stores` scalano quella voce e solo quella; senza arma, o con un nome estraneo, l'aggregato
(v. `drain_order`, capitolo 4 §4.19). Deterministico in entrambi i casi: nessuna estrazione
casuale, mai sotto zero.

**Regola D e CIWS navali (2026-09-28, commit `37ca477e`)**. Le armi "intercettrici" di un asset
(`Mobile.interceptor_weapons_from_registry`, `Asset/Mobile.py:1047-1117`) sono ora quelle AD di
`air_defense_volume` che dichiarano il task `Mobile.INTERCEPTOR_TASK = 'Anti_Missile'` (`:196`), e
`Mobile.interceptor_capability()` (`:1119-1131`) dice se un asset ne ha almeno una (`True`/`False`, o
`None` se il registro non descrive armi del modello). I **CIWS navali** (Phalanx, AK-630, Type-730) sono
inclusi come cannoni AD (`INTERCEPTOR_WEAPON_TYPES_SHIP = ('MISSILES_SAM', 'CIWS')`,
`INTERCEPTOR_GUN_WEAPON_TYPES = ('AA_CANNONS', 'CIWS')`, `:187-189`) e, se l'arma dichiara
`rounds_per_mount`, la loro scorta è `impianti × colpi per impianto` (`_mount_rounds`, `:204-216`;
`stores_from_registry`, `:859-903`) invece di restare "non modellati" contati a unità: Phalanx 1550, AK-630
2000, Type-730 1280 colpi per impianto (`Asset/Ship_Weapon_Data.py`). Un CIWS senza `rounds_per_mount`
resta fra le armi non modellate (`unmodelled_weapons_from_registry`, `:905-921`).

### Carburante (`Asset/Mobile.py:218-257`)

**Unità: frazione del carico pieno, [0,1] (`FUEL_FULL = 1.0`), per tutti gli asset** — scelta
motivata dai dati, non di comodo:

1. `Vehicle_Data`/`Ship_Data` non dichiarano una capacità di serbatoio, ma dichiarano
   l'**autonomia** (`range`: km per i veicoli, miglia nautiche per le navi) — il consumo per
   metro è `1/autonomia`, senza costanti inventate.
2. Per gli aerei i raggi dei loadout (`cruise/attack.range['fuel_100%']`) valgono per il carico
   **completo** (interno più serbatoi esterni se imbarcati), mentre `fuel_internal_max` è il solo
   carburante interno: un contatore in kg inizializzato a `fuel_internal_max` sovrastimerebbe
   l'autonomia di chi porta serbatoi esterni. La frazione del carico pieno è coerente con il dato
   di autonomia per costruzione.
3. Una sola unità per tutti gli asset rende sommabili/confrontabili i `FuelEvent` del
   `SessionOutcome`.

Regimi: `'nominal'`/`'max'` (`Mobile.FUEL_REGIMES`). Per gli aerei `'nominal'` legge il profilo
`cruise` del loadout e `'max'` il profilo `attack`; per veicoli e navi il registro ha un'unica
autonomia, usata per entrambi (limite dichiarato: sottostima il consumo al regime massimo — è il
dato a non distinguere, non una semplificazione introdotta dal motore). `None` = carburante **non
modellato**: nessun vincolo di movimento (stessa semantica delle munizioni) — casi: modello
ignoto, autonomia mancante, aereo senza loadout assegnato, propulsione nucleare
(`NUCLEAR_ENGINE_TYPES`, l'autonomia dichiarata "convenzionalmente 20.000 nm" dal registro è
trattata come segnaposto, non come dato, `:266-272`).

### `Aircraft.assigned_loadout` (`Asset/Aircraft.py:170-214`)

La scorta di un aereo si ricava dal **loadout assegnato**, non dal modello (`Aircraft_Data` non
ha un campo `weapons`): prima di questa proprietà non esisteva alcuno stato "loadout di questo
volo" su un'istanza. Assegnare un loadout (`assigned_loadout = 'Strike'`) equivale ad armare il
velivolo per la missione: **riarma** l'aereo (ricalcola la scorta per arma via
`load_stores_from_registry()`, che chiama l'override di `stores_from_registry()` sotto, e il
carburante via `load_fuel_from_registry()`, sovrascrivendo l'eventuale consumo precedente) — è
quindi un'operazione del ciclo di campagna/assemblaggio missione, **non** un canale di
rifornimento durante l'ingaggio (il risolutore non la chiama mai).

`Aircraft.stores_from_registry()` (`:216-279`, override di `Mobile.stores_from_registry`, v.
capitolo 4 §4.19) costruisce `{modello_arma: quantità}` dal loadout assegnato
(`AIRCRAFT_LOADOUTS[model][loadout]['stores']['pylons']`): per ogni pilone la quantità, **solo**
se il nome è un'arma reale di `AIR_WEAPONS` (`get_weapon(...)` non `None`) — serbatoi esterni e
pod di rifornimento stanno anch'essi nei piloni e vanno esclusi; piloni con la stessa arma si
sommano. **Dal 2026-09-26 (decisione A2, commit `8bd69727`, v. capitolo 4 §4.16bis)** il **cannone
di bordo** ottiene la propria voce di scorta, `{modello_cannone: colpi}` da
`get_aircraft_gun_rounds(model, stores['gun_rounds'])` (`Asset/Aircraft_Data.py:3745-3773`), MAI
sommata a quella di un'arma dei piloni diversa: fino a questa data i colpi del cannone
(`stores['gun_rounds']`) non entravano affatto nella scorta per arma e finivano nel contatore
scalare aggregato (v. capitolo 4 §4.19), pagando i missili dello stesso asset — è il difetto
descritto in dettaglio al capitolo 4, §4.16bis. Il cannone è candidato della fire control
(`Logic/Fire_Control._candidate_weapons`, capitolo 4 §4.16bis) esattamente come le armi dei
piloni. Senza loadout assegnato, delega a `Mobile.stores_from_registry()`, che per un aereo
restituisce `None` (non modellata).

## 7.7 I punti di iniezione del motore

Sono parametri **iniettati** in `resolve_engagement`/`run_session`, mai implementati dal motore stesso —
il punto di estensione esplicito verso ciò che il motore non fa (v. capitolo 9):

- `fire_control: (shooter, target) -> ShotSpec | Sequence[ShotSpec] | None` — interrogata al
  momento dello scheduling del lancio (capitolo 4, §4.4). Dal 2026-09-26 può restituire una
  **sequenza** ordinata di opzioni, e il risolutore spara con la prima che ha ancora scorta per
  quel modello d'arma (capitolo 4, §4.19); una `ShotSpec` singola resta un valore valido.
  `Session_Simulator.run_session` ne passa **una sola** a ogni ingaggio della sessione, non una
  per lato: la callable riceve gli asset reali e può distinguere lato/blocco/modello da sé
  (`Logic/Session_Simulator.py:129-135`, capitolo 6). Una fabbrica che seleziona davvero l'arma
  dai registri, invece di una tabella di ruoli, esiste in
  `Logic/Fire_Control.make_registry_fire_control` (capitolo 4, §4.16).
- `detection_factor: (observer, target) -> float in [0,1]` — degradazione della Pd (§7.4);
  default nessuna degradazione (`factor=1.0`). Oltre al meteo (`weather_detection_factor_fn`/
  `meteo_detection_factor`, §7.4), esistono fabbriche dello stesso fattore per la nebbia di guerra
  da ricognizione (`region_recon_detection_factor`, capitolo 4, §4.18) e per comporre più
  degradazioni insieme (`combine_detection_factors`).
- **Dal 2026-09-29/30**, quattro punti di iniezione della soglia di rottura e della percezione:
  `morale_for(force) -> [0, 1] | None` (morale della forza, default `None` = neutro),
  `enemy_estimate_for(force) -> float ≥ 0 | None` (stima a priori della forza nemica nella stessa misura del
  rapporto percepito), `fire_doctrine` (tabella al posto di `Doctrine.DEFAULT_FIRE_DOCTRINE`, `{}` = nessuna
  regola) e `rwr_catalogue` (emettitori per il peso di classe della RWR); più il flusso `breakpoint_rng`
  della tempra. Dettaglio in capitolo 4 §4.12, §4.21, §4.23, §4.25; `run_session` inoltra i primi tre,
  `fire_doctrine` e costruisce `breakpoint_rng` (capitolo 6 §6.1, §6.4), ma **non** inoltra
  `rwr_catalogue`. A `533cd1f5` nessun chiamante di produzione fornisce `morale_for` né
  `enemy_estimate_for` (capitolo 9 §9.1).

## 7.8 Il pianificatore di rotta aerea: volumi di rilevamento e intercettazione distinti (`Logic/Air_Route_Manager.py`, decisioni D-1..D-7, 2026-09-26, commit `815dc35f`)

**Fuori dal motore DES in senso stretto** (non è uno dei quattro strati dei capitoli 2-6): è il
pianificatore di rotta che precede una missione, consumato più a monte. Entra in questo manuale
perché condivide con il motore la stessa legge di rilevamento (`Engagement_Resolver.
detection_probability`, v. §4.2) e perché `Block/Military.py` lo espone come una delle dimensioni
militari del capitolo 7. Documento di riferimento:
`Analysis/Document/Proposta_Volumi_Rilevamento_Intercettazione.md`.

### Il problema che ha motivato l'estensione

`Mobile.air_defense_volume()` costruisce da sempre un solo `Cylinder` per asset di difesa aerea:
il volume di **intercettazione**, cioè la portata dell'arma. I registri dichiarano però anche una
portata di **scoperta** del sensore, quasi sempre maggiore (un SA-6/2K12-Kub scopre a 75 km e
intercetta a 24 km), mai letta dal pianificatore prima di questa data: un aereo che aggirava
"la minaccia" aggirava in realtà solo la sua arma, non il suo sensore.

### Due tipi, una base comune (`AirThreat`, `:77-131`)

`AirThreat` è la base comune (`danger_level`, `volume`/`cylinder` — alias finché l'unica forma è
il cilindro —, `min_altitude`/`max_altitude` dal cilindro, `source_id`, `edgeIntersect`/
`innerPoint` usati dalla ricerca di percorso): due specializzazioni con parametri disgiunti.

- **`ThreatAA(AirThreat)`** (`:134-277`) — la classe storica del pianificatore, ora sottoclasse:
  stesso costruttore posizionale `(danger_level, interception_speed, min_fire_time,
  acquisition_time, cylinder)`, quindi compatibile con ogni chiamata preesistente.
  `acquisition_time` (**rinominato** da `min_detection_time`, decisione D-6: `min_detection_time`
  resta accettato come parola chiave e come attributo alias) è la **latenza di acquisizione** —
  dal contatto a una traccia utile al tiro, lo stesso RIV del profilo di reazione del DES
  (capitolo 7, §7.3) — non un volume né un tempo di rilevamento: il nome precedente confondeva le
  due nozioni. `calcMaxLenghtCrossSegmentInterception` (rinominata da
  `calcMaxLenghtCrossSegment`, alias mantenuto) modella **solo** il volume d'intercettazione:
  moto radiale dell'aereo a velocità `v_a`, sito pronto a lanciare dopo `ready_delay_s` (0 nel
  pianificatore odierno) + `min_fire_time`, intercettore a velocità `v_i` — equazione di secondo
  grado nella distanza percorsa dall'intercettore, `float('inf')` se non esiste soluzione positiva
  (nessun intercettore può raggiungere l'aereo: qualunque corda è sicura).
- **`DetectionThreat(AirThreat)`** (`:280-329`, nuova) — il volume di **rilevamento**:
  `danger_level` è sempre `0.0` per costruzione (decisione D-3), così `total_danger` dei percorsi
  e `Military.air_defense_power()` (capitolo 7, §7.5) restano misure della sola potenza di fuoco.
  Il cilindro è costruito **alla quota di rotta** `route_altitude` (un vero volume di rilevamento
  è un solido il cui raggio cresce con la quota; il cilindro ne è la sola sezione a quella quota,
  per cui il pianificatore non ammette cambi di quota per aggirarlo, v. sotto), con raggio
  `min(acquisition_range, orizzonte_radar)`.

### Orizzonte radar (`radar_horizon_range`, `:665-677`)

```
d = sqrt(2*k*R_terra*h_antenna) + sqrt(2*k*R_terra*h_bersaglio)      k = 4/3 (radar standard)
```

`build_detection_threat(asset, route_altitude)` (`:726-779`) prova i sensori `'radar'` e `'TVD'`
dell'asset (`Mobile.detection_range('air', sensor=...)`), tiene quello col raggio **effettivo**
maggiore, e restituisce `None` senza sollevare se l'asset non ha posizione o nessun
`acquisition_range` aria utilizzabile (es. ZSU-57-2, M163-VADS: nessun sensore nei registri,
decisione D-4 sospesa, dati da ricercare). Un sensore puro (EWR) produce la sua `DetectionThreat`
senza bisogno di armi. `build_air_defense_threats(asset, route_altitude)` (`:782-802`) restituisce
la coppia `(DetectionThreat, ThreatAA)` dello stesso sito, con lo **stesso `source_id`**: è il
legame che il pianificatore d'attacco userà per sapere quando un sito ha già acquisito l'aereo
(v. §7.9). **Limite noto**: il raggio d'intercettazione resta la sola portata dell'arma, senza il
minimo con l'`engagement_range` della guida — verificato che con i dati attuali la guida è sempre
≥ la portata dell'arma (nessuna differenza pratica oggi).

### `ThreatMode`: tre modalità di trattamento (`:37-74`)

`resolve_threat_mode(mode=None, intersecate_threat=False)` decide la modalità effettiva: `mode`
prevale, altrimenti l'alias storico `intersecate_threat` (`False` → `AVOID`, `True` →
`CROSS_UNINTERCEPTED`) — nessuna chiamata preesistente cambia comportamento.

| Modalità | Comportamento |
|---|---|
| `AVOID` | Aggira i volumi d'**intercettazione** (comportamento storico, `intersecate_threat=False`). |
| `CROSS_UNINTERCEPTED` | Attraversa i volumi d'intercettazione con la corda di sicurezza (`intersecate_threat=True`). |
| `AVOID_DETECTION` | Aggira i volumi di **rilevamento** e attraversa con la stessa corda limitata ogni volume d'intercettazione toccato comunque. |

In `AVOID_DETECTION` (`calcRoute`, `:1395-1419`) il motore di ricerca dell'aggiramento (invariato)
lavora sui volumi di rilevamento (`detections`); i volumi d'intercettazione (`threats`) diventano
`cross_threats`, attraversati a corda limitata da `_cross_interception_while_avoiding`
(`:1792-1899`) quando un arco già scelto per evitare il rilevamento li tocca comunque — **mai per
costruzione**: ogni intersezione è verificata sui volumi dichiarati (intersezione completa
richiesta, corda massima da `calcMaxLenghtCrossSegmentInterception`, come in
`CROSS_UNINTERCEPTED`), non assunta nulla dal solo fatto che il rilevamento sia stato evitato — per
i SAM tipici (sensore e arma co-locati) i due volumi sono annidati, ma a bassa quota l'orizzonte
radar può rendere il volume di rilevamento **più piccolo** di quello d'intercettazione. Nessun
cambio di quota è ammesso per un volume di rilevamento (`_handle_threat_avoidance`, `:2326-2332`):
è costruito a una sola quota, e cambiarla richiederebbe ricostruirlo, non ancora fatto
(proposta §3.6, Attività D, fuori scope di questo commit).

### Metriche di rilevamento del percorso (decisione D-3/D-5, `Path.compute_detection_metrics`, `:1073-1142`)

Separate da `total_danger` (che resta la sola intercettazione): `detection_exposure_s` (somma
delle durate nei volumi di rilevamento, volumi sovrapposti contati ciascuno), `first_detection_
time_s` (primo ingresso, `None` se mai), `warning_time_s` (arrivo − primo rilevamento),
`max_detection_probability` (replica **esatta** la legge di Pd del DES,
`Engagement_Resolver.detection_probability`, come metrica di pianificazione — nessuna modifica al
risolutore). `PathCollection.best_path_key(mode)` (`:1231-1242`) cambia il criterio di scelta del
percorso migliore solo in `AVOID_DETECTION`: prima il minimo tempo sotto sensore, poi il pericolo
residuo d'intercettazione, poi la lunghezza (altre modalità: la chiave storica pericolo→lunghezza).

### `Block/Military.py`: le due liste per blocco

`Military.air_defense_threats()` (`Block/Military.py:552-582`, preesistente, ora con
`source_id` impostato — v. §7.9) e la nuova `Military.air_detection_threats(route_altitude)`
(`:584-611`) restituiscono rispettivamente i `ThreatAA` e le `DetectionThreat` di tutti gli asset
Vehicle/Ship operativi del blocco con dati utilizzabili — la stessa selezione di asset, due volumi
per sito. Nessuna delle due entra in `air_defense_power()` per la parte di rilevamento
(`DetectionThreat.danger_level == 0.0` per costruzione).

### Fuori perimetro, dichiarato

Reti di sensori/cueing EWR→SAM (D-7); dati EWR e sensore visivo per ZSU-57-2/M163 (D-4b/c,
ricerca dati separata); attraversamento a corda limitata del **solo** rilevamento (D-5, opzione 2:
richiederebbe un dato di tempo di permanenza del sensore e un cambio della legge del risolutore
DES); la firma a due liste minacce di `plan_attack_profile` (D-8) — implementata insieme al
pianificatore d'attacco, v. §7.9.

### Diagramma D14 — tipi e modalità

```mermaid
classDiagram
    class AirThreat {
        +float danger_level
        +Cylinder volume
        +float min_altitude
        +float max_altitude
        +str source_id
        +edgeIntersect(edge) tuple
        +innerPoint(point) bool
    }

    class ThreatAA {
        +float interception_speed
        +float min_fire_time
        +float acquisition_time
        +calcMaxLenghtCrossSegmentInterception(speed, altitude, t_inv) float
    }

    class DetectionThreat {
        +str sensor
        +float acquisition_range
        +float reference_altitude
    }

    class ThreatMode {
        <<enumeration>>
        AVOID
        CROSS_UNINTERCEPTED
        AVOID_DETECTION
    }

    AirThreat <|-- ThreatAA
    AirThreat <|-- DetectionThreat
```

## 7.9 Il pianificatore d'attacco: quota di sgancio e profilo (`Logic/Weapon_Delivery.py`, `Command/Attack_Types.py`, decisioni B1-B6, 2026-09-27, commit `6754bf1c`)

**Anche questo fuori dal motore DES in senso stretto**: è il pianificatore che, prima di una
missione, decide da che quota, velocità, profilo e direzione un aereo sgancia una bomba — ma è
**l'input** che il capitolo 4 consuma (§4.20, decisione B6): "una fisica, un pianificatore, due
esecutori" (`Logic/Weapon_Delivery.py:1-14`, decisione B2). Documento di riferimento:
`Analysis/Document/Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md` (Proposta B).

Due livelli, entrambi stateless, senza RNG:

### Livello 1 — fisica pura (`release_windows`, `fall_time`, `release_solution`, `bomb_engagement_estimate`)

Moto parabolico nel vuoto con velocità iniziale `v` inclinata di `pitch` (negativo in picchiata,
positivo in cabrata a `LOFT_PITCH_DEG = 30°`, zero livellato), da quota `h` **AGL sopra il
bersaglio** (`fall_time`, `:254-259`):

```
v_z = v * sin(pitch);   t_vuoto = (v_z + sqrt(v_z^2 + 2*g*h)) / g;   R_vuoto = v * cos(pitch) * t_vuoto
```

poi i fattori di resistenza per classe `drag` — **STIME DICHIARATE**, non tarate
(`DRAG_FACTORS`, `:123-126`): bassa resistenza (`low`) −10% di gittata/+5% di caduta rispetto al
vuoto, frenata (`high`, Snakeye/ballute/paracadute) circa −50% di gittata/+30% di caduta.
Due casi sostituiscono la balistica (`_solve`, `:262-285`): `glide_ratio` (bombe plananti guidate,
es. GBU-24: `R = max(balistica, glide_ratio * h)`, planata a velocità costante se vince) e
`standoff_range_km` (dispenser plananti BK-90: `R` interpolata linearmente nella finestra di quota
del registro fra `(min, max)` — fisicamente non è planata, è la distanza di sgancio dichiarata).

`release_windows(weapon)` (`:227-251`) legge il campo `release` del registro (v. capitolo 9, §9.1,
per le 29/32 bombe che lo hanno) e lo normalizza in una o due `ReleaseWindow` (`low_drag`/
`high_drag` per il drag selezionabile, Mk-82AIR/M-71/SAMP-250HD); `select_window` (`:333-340`)
sceglie la finestra `low_drag` se la quota ci sta, altrimenti `high_drag` (decisione utente).
`bomb_engagement_estimate(weapon, altitude_agl, speed_kmh)` (`:343-382`, v. capitolo 4, §4.20) è
l'ingresso usato dal DES: rilascio **livellato** (picchiata a metà fascia se il livellato non è
ammesso), quota e velocità **portate al valore ammesso più vicino** se fuori finestra — lo stesso
comportamento dichiarato dell'IA di DCS. Restituisce `None` solo se l'arma non ha dati di rilascio.

### Livello 2 — pianificazione (`plan_attack_profile`, `:657-813`)

Euristica deterministica (nessun RNG), a ricerca su griglia:

1. **Fascia ammessa** = inviluppo `attack` del loadout ∩ finestra `release` dell'arma (quota AGL,
   velocità); vuota → `feasible=False` con il motivo (evita che DCS corregga la quota in silenzio,
   `Controller.md:157`, citato nel modulo).
2. **Velocità**: quella `attack` del loadout, ridotta al massimo della finestra se la supera (un
   aereo rallenta, non accelera oltre il proprio inviluppo).
3. **Quote candidate** (`_candidate_altitudes`, `:526-548`): griglia di `ALTITUDE_GRID_STEPS = 6`
   quote sulla fascia, più i bordi di ogni volume d'**intercettazione** (con gli stessi margini
   ±5% di `Air_Route_Manager`) che cadono nella fascia — gli stessi punti "critici" che il
   pianificatore di rotta userebbe. Profili candidati: quelli ammessi dalla finestra; angoli di
   picchiata `DIVE_ANGLES_DEG = (15°, 30°, 45°, 60°)` dentro `dive_angle`; cabrata a
   `LOFT_PITCH_DEG`.
4. **Azimut**: `AZIMUTH_COUNT = 12` direzioni equispaziate (o quelle imposte dal chiamante).
5. **Esposizione per candidato** (`_evaluate_exposure`, `:433-493`): per il tratto IP → sgancio →
   uscita a quota/velocità costanti, le finestre di permanenza in **ogni** volume (intercettazione
   e rilevamento) via l'intervallo analitico `_segment_cylinder_interval` (lo stesso di
   `Air_Route_Manager`, non `Contact_Scheduler.route_threat_windows`: quest'ultimo usa geometria
   sympy, troppo lenta per le centinaia di candidati valutati — sui segmenti rettilinei dà lo
   stesso intervallo, quindi nessuna perdita di correttezza, solo di generalità geometrica).
   L'esposizione **effettiva** a un volume d'intercettazione segue la regola B3/D-8:

   ```
   t_lancio  = max(t_ingresso_V_I, t_contatto_V_R + acquisition_time) + min_fire_time
   effettivo = max(0, t_uscita_V_I - t_lancio)
   ```

   dove `V_R` è il volume di **rilevamento** con lo **stesso `source_id`** del volume
   d'intercettazione `V_I` (il legame impostato da `build_air_defense_threats`/
   `Military.air_defense_threats`, v. §7.8). Senza `V_R` associato: `t_contatto = -inf` (sito
   già in traccia, ipotesi conservativa); con `V_R` associato ma mai toccato: il sito non vede
   l'aereo, esposizione effettiva 0; IP già dentro `V_R`: rilevato prima dell'IP.
6. **Scelta**: minimo di `Σ(effettivo × danger_level)` (esposizione pesata; 0 = nessuna possibilità
   di lancio nemico nel tratto), poi quota più bassa (precisione di sgancio), poi azimut più vicino
   alla direzione della base se data, poi azimut/profilo/angolo/drag per determinismo. **Le
   minacce non rendono mai il profilo non fattibile** (decisione utente): una minaccia non
   evitabile vicino al bersaglio si accetta, decide solo quale profilo scegliere fra quelli
   fattibili.
7. **Transito opzionale** (`home_point` dato): rotte base→IP e uscita→base con
   `RoutePlanner.calcCanonicalRoute`, concatenate nella `full_route`.

`detection_threats_factory(assets)` (`:816-829`) costruisce, per un elenco di asset, la funzione
`quota_assoluta -> DetectionThreat` che `plan_attack_profile` usa per ricalcolare il volume di
rilevamento a **ogni** quota candidata (il raggio dipende dall'orizzonte radar, v. §7.8): senza
questa fabbrica, un `Sequence` fisso di `DetectionThreat` costruito a una sola quota sottostimerebbe
o sovrastimerebbe il raggio alle altre quote valutate.

### `Command/Attack_Types.py`: `AttackProfile` e `ThreatExposure`

Tipi immutabili (`@dataclass(frozen=True)`), senza logica di calcolo, senza dipendenze da `Logic/`
(evita cicli con `Weapon_Delivery`): `AttackProfile` è ciò che **due esecutori** consumano allo
stesso modo (vincolo simulator-agnostic, v. capitolo 1) — il motore DES legge `release_slant_range_m`
(→ `ShotSpec.max_range`, capitolo 4 §4.20) e `fall_time_s` (→ `ShotSpec.time_of_flight`); un
futuro adapter DCS leggerebbe `release_altitude_m` (`altitude`), `run_in_azimuth_deg`
(`direction`), `weapon` (`weaponType`) e `quantity`/`passes` (`expend`/`attackQty`) dei task DCS
`AttackGroup`/`Bombing` — il punto di sgancio esatto lo calcola comunque l'IA di DCS, il core le
fornisce solo il profilo, validato contro la finestra di rilascio dell'arma. `ThreatExposure`
porta, per ogni minaccia d'intercettazione toccata, `seconds`/`effective_seconds`/`danger_level` e
i tempi di rilevamento/preavviso (`detected_at_s`/`warning_time_s`/`detected`) descritti sopra.
Con `feasible=False` il profilo porta solo arma, bersaglio e motivo: nessun campo geometrico.

### Limiti dichiarati (dal docstring del modulo, `Logic/Weapon_Delivery.py:76-84`)

- La geometria della picchiata/cabrata **non è nel tratto**: IP → sgancio è a quota costante, il
  profilo entra solo nella balistica (gittata e caduta) — non nella traiettoria valutata per
  l'esposizione alle minacce.
- Il cilindro d'intercettazione è l'unione degli inviluppi dell'asset: nessuna zona morta interna;
  il vantaggio del volo basso viene dall'orizzonte radar del volume di **rilevamento**, quando è
  fornito.
- Terreno non modellato: AGL = quota assoluta − quota del bersaglio.
- Solo armi a caduta (`AIR_WEAPONS['BOMBS']`); i missili aria-superficie sono fuori scope.
- Nessun componente LLM, nessun uso del modulo `random`.
- `route_threat_windows` di `Contact_Scheduler` (capitolo 3) resta **senza consumatori di
  produzione**: sia il pianificatore di rotta (§7.8) sia questo pianificatore d'attacco usano
  l'intervallo analitico `_segment_cylinder_interval`, più veloce sui segmenti rettilinei — la
  funzione sympy resta disponibile ma non è la via effettivamente percorsa oggi.

### Diagramma D15 — dal pianificatore all'`AttackProfile`, verso DES e DCS

```mermaid
flowchart TD
    A["plan_attack_profile(aircraft, loadout, weapon, target,<br/>threats: ThreatAA[], detection_threats: DetectionThreat[]/factory)"] --> B["griglia quota x velocita' x profilo x azimut"]
    B --> C["release_solution: balistica (livello 1)"]
    C --> D["_evaluate_exposure: finestre nei volumi V_I/V_R,<br/>regola B3/D-8"]
    D --> E["scelta: min esposizione pesata,<br/>poi quota, poi azimut verso base"]
    E --> F["AttackProfile (Command/Attack_Types.py)"]
    F --> G["DES: Logic/Fire_Control.shot_spec_for (B6, cap.4 §4.20)<br/>max_range/time_of_flight dalla balistica"]
    F --> H["futuro adapter DCS: altitude/direction/weaponType/expend<br/>dei task AttackGroup/Bombing"]
```

## 7.10 `Asset/Aircraft_Rwr_Data.py` — che cosa riconosce l'RWR di ogni aereo, e quando (2026-09-29, commit `4d225ffb`, `d261062c`)

Dato di registro nuovo (191 righe), richiesto dall'utente per valutare il "fuoco senza risposta" di una forza
aerea con l'RWR di ogni aereo illuminato (`Proposta_Soglia_Rottura_Stocastica.md` §5). Il registro
`Aircraft_Data` nomina l'RWR solo per alcuni aerei (campo `avionics`); qui il dato è **completo**:
`AIRCRAFT_RWR` (`Asset/Aircraft_Rwr_Data.py:90-162`) ha una voce per **ciascuno dei 65 modelli** del
registro (verificato: l'insieme dei modelli coincide con `Aircraft_Data._registry`). Fonti: campo
`avionics` del registro, decisioni dell'utente del 2026-09-29 e la ricerca
`Analysis/Document/Ricerca_RWR_2026_09_29.md` (`:1-8`).

### Schema di una voce (`:9-21`)

| Campo | Significato |
|---|---|
| `rwr` | nome del sistema (`None` = nessun RWR) |
| `classes` | le **classi** di minaccia SAM che il sistema distingue, ciascuna un insieme di categorie (`VSHORAD`, `SHORAD`, `MRSAM`, `LRSAM`); una classe con più categorie = il sistema non le separa; l'unione delle classi è l'insieme di categorie riconosciute come minaccia SAM; vuota = nessun riconoscimento |
| `modes` | modalità del radar nemico che il sistema rileva: `search` (ricerca/acquisizione), `track` (tracciamento), `guidance` (guida del missile): decide **quando** la minaccia è percepita (capitolo 4 §4.23) |
| `sectors` | settori di direzione (4, 8), `None` = direzione precisa |
| `ewr` | se riconosce i radar di scoperta come classe a parte |
| `confidence` | `alta` / `media` / `bassa` |

### Le famiglie (decisioni dell'utente, 2026-09-29; costruttori `:54-81`)

- **Sistemi digitali** (`_digital`: AN/ALR-46/56/67/69, ALQ-161, SERVAL/SPIRALE, L-150 Pastel/SPO-32, BKO-1
  Baykal, ESM di bordo): ogni categoria separata, tutte le modalità, direzione precisa.
- **SPO-15 Beryoza** (`_spo15`, anche L, LE, LM): direzione su 8 settori; **tre** classi SAM
  (VSHORAD-SHORAD insieme, MRSAM, LRSAM); distingue ricerca, tracciamento e guida; rileva il radar dello Shilka
  (verificato dall'utente in DCS con il Su-25).
- **SPO-10 Sirena-3** (`_spo10`): direzione su 4 quadranti; **una sola** classe ("SAM" generico: riconoscimento a
  due soli livelli, SAM o EWR); rileva solo il tracciamento.
- **AN/ALR-45** (`_alr45`, F-14A, A-4E): riconosce la classe AAA ma non distingue i SAM fra loro: due classi,
  VSHORAD e "SAM" generico.
- **Solo allarme** (`_warning_only`: Sirena-2, radarvarnare del Viggen) e **nessun RWR** (`_none`):
  nessun riconoscimento.

Funzioni di lettura: `rwr_entry` (`:165-167`; un modello assente dalla tabella è trattato come senza RWR),
`rwr_categories` (`:170-177`, unione delle classi), `rwr_modes` (`:180-184`), `rwr_classes` (`:187-191`).
Uso: solo `Context/Air_Defense_Efficacy` (§7.11) e, per suo tramite, il risolutore (capitolo 4 §4.23).
**Settori, `ewr` e `confidence` non sono consumati da nessun codice di produzione** (decisione dell'utente,
2026-09-30: rimandati al modulo rotte/evasione e a un futuro SEAD, `Proposta_Uso_Classi_Settori_RWR.md` §3).
Il campo `avionics` di Tu-95MS in `Aircraft_Data` è stato allineato a L-150 Pastel (commit `1c087a37`: il registro
indicava SPO-15 Beryoza, in contrasto con la tabella RWR); cambia solo il nome del modello.

## 7.11 `Context/Air_Defense_Efficacy.py` — struttura del modulo

Descritto nel suo uso al capitolo 4 §4.22 (E(N)) e §4.23 (categorie SAM, RWR, regola R-CLS). Qui la mappa
dei tipi e delle funzioni, per chi dovrà estenderlo:

| Gruppo | Contenuto | Riga |
|---|---|---|
| Stime dichiarate | classe di riferimento `Aircraft_Attacker`/`med`, velocità 200 m/s, velocità di ripiego del proiettile 1000 m/s, `EFFICACY_CORRECTIONS` (vuota), `AD_TASKS`, tipi d'arma AD per veicoli e navi | `:64-90` |
| Profilo statico | `ADWeaponProfile` (`weapon`, `p`, `director`, `channels`, `cycles`, `rounds_per_engagement`, `full_stock`), `ADProfile`, cache `_PROFILE_CACHE`, `clear_cache` | `:93-139` |
| Costruzione | `_is_ad_weapon`, `_single_shot_p`, `_cycles`, `_channels`, `_director`, `_build_profile`, `air_defense_profile` | `:164-353` |
| E(N) | `expected_kills`, `air_defense_efficacy` | `:356-413` |
| Pesi di minaccia | `surface_threat_weight`, `air_threat_weight` | `:445-476` |
| RWR e categorie | `SAM_WEAPON_CATEGORY`, `sam_category`, `emits_radar`, `rwr_identifies`, `rwr_perception` (`PERCEIVED_AT_DETECTION`/`PERCEIVED_AT_LAUNCH`) | `:479-619` |
| Classe RWR (R-CLS) | `emitter_domain`, `rwr_class_of`, `default_rwr_catalogue`, `class_threat_weight` | `:622-725` |

**Mai eccezioni per dato mancante**: modello ignoto o senza armi AD → `None` o peso di ripiego, con un log di
debug (docstring `:48-50`). Gli import dei registri e dei moduli `Logic` sono locali alle funzioni; il dato RWR
è importato a livello di modulo, a metà file (`:491-492`).

*Diagramma D28 — `Air_Defense_Efficacy`: profili, dati RWR e funzioni pubbliche.*

```mermaid
classDiagram
    class ADWeaponProfile {
        +str weapon
        +float p
        +str director
        +int channels
        +int cycles
        +int rounds_per_engagement
        +int full_stock
        +time_limited_engagements() int
    }
    class ADProfile {
        +str model
        +tuple weapons
    }
    class AircraftRwrEntry {
        <<dato di registro>>
        +str rwr
        +tuple classes
        +frozenset modes
        +int sectors
        +bool ewr
        +str confidence
    }
    class Air_Defense_Efficacy {
        <<modulo>>
        +air_defense_efficacy(asset, n) float
        +air_threat_weight(asset, n) float
        +surface_threat_weight(asset) float
        +rwr_perception(aircraft, emitter) str
        +class_threat_weight(classe, dominio, n) float
    }

    ADProfile "1" *-- "1..*" ADWeaponProfile
    Air_Defense_Efficacy ..> ADProfile : air_defense_profile
    Air_Defense_Efficacy ..> AircraftRwrEntry : rwr_categories, rwr_modes, rwr_classes
```

## 7.12 Dati di registro aggiunti dopo `6754bf1c`

Modifiche ai registri d'arma e d'aereo, senza codice consumatore nuovo ma con effetti sul motore:

- **Armi DCS mancanti** (`0df5ddf9`, 2026-09-28): 4 AAM, 12 ASM e 23 bombe aggiunte a `AIR_WEAPONS`
  (`Asset/Aircraft_Weapon_Data.py`), dall'elenco `Analysis/Document/bombe_missili_russi.pdf` (schermate del menu
  armi DCS) con una ricerca a tre gruppi (fonte e confidenza per campo, in
  `Analysis/Document/Ricerca_Armi_DCS_2026_09_28/`) poi **revisionata**: Kh-22 e Kh-58U non inseriti (alias di
  Kh-22N e Kh-58), Kh-41 con testata 320 kg, KD-20 ricostruito (stima), classi `efficiency` mancanti
  ereditate dalla voce del modello, LS-6 planante (standoff 10-60 km), Mk-84 AIR con drag selezionabile; le
  varianti RBK sono voci separate (decisione dell'utente). A `533cd1f5` il registro conta 42 AAM, 44 ASM,
  **54 bombe, tutte con il campo `release`**, 12 razzi, 15 cannoni, 2 mitragliatrici (verificato). Le 54
  bombe con finestra di rilascio superano le 29 su 32 dell'aggiornamento precedente (capitolo 4 §4.20).
- **KMGU-2** (`89f1aa34`, decisione D4, 2026-09-28): le tre voci KGBU-* si sono rivelate un dispenser mal
  identificato; ora `KMGU-2AO` e `KMGU-2PTAB` (nomi DCS KMG-2F/2B; 525 kg; `'dispenser': True`: il dispenser
  **resta sul pilone** ed espelle i blocchi BKF; rilascio solo livellato a 30-1000 m, 500-1100 km/h, drag
  `high`, `Aircraft_Weapon_Data.py:7762-7771`, `:7830-7839`); la voce duplicata KGBU-96r è stata eliminata.
  La decisione D4, sospesa il 2026-09-27, è chiusa: oggi **nessuna** bomba è senza dati di rilascio.
- **Task `Anti_Missile`** su 6 armi terrestri e `rounds_per_mount` sui 3 CIWS navali (`37ca477e`, §7.6).
- **Rename `Retrait` → `Retreat`** (`1d5dc863`) e nuovi task aerei di supporto (`4e18d7d8`): capitolo 2 §2.7.
- **Tu-95MS**: campo `avionics` allineato a L-150 Pastel (`1c087a37`, §7.10).
