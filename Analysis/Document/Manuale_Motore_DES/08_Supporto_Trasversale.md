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

## 7.2 `Context/Doctrine.py` — soglie di disingaggio (P1 + R2)

Le soglie sono **dottrina di lato**, non una costante del risolutore, non un parametro di
sessione, non una proprietà del singolo asset, valutata **per forza intera**
(`Context/Doctrine.py:60-68`). Le due soglie, stessa grandezza, stesso denominatore (`:70-85`):

- `'erosion'` — frazione **cumulata** dell'organico impegnato non più operativo: la forza si
  logora lentamente;
- `'shock'` — frazione persa in **un singolo impulso** (una sola salva risolta): la forza si
  rompe per un colpo improvviso anche se le perdite cumulate sono ancora sotto `erosion`.

Entrambe sono frazioni dell'**organico impegnato all'inizio dell'ingaggio** (non della forza
superstite): con lo stesso denominatore la perdita di una salva non può mai superare la perdita
cumulata, quindi `shock <= erosion` è un vincolo di coerenza verificato
(`validate_disengagement_thresholds`, `:112-155`) — altrimenti la soglia di shock non
scatterebbe mai per prima e sarebbe un parametro morto.

### Valori di default — **STIMA DI PARTENZA DICHIARATA, non dati validati** (`:87-100`)

```python
DEFAULT_DISENGAGEMENT_THRESHOLDS = {
    "Blue":    {"erosion": 0.30, "shock": 0.20},
    "Red":     {"erosion": 0.30, "shock": 0.20},
    "Neutral": {"erosion": 0.30, "shock": 0.20},
}
```

- `erosion = 0.30` — regola empirica diffusa nella letteratura militare per cui un'unità scesa
  sotto ~70% dell'organico non è più pienamente efficace in combattimento: un ordine di
  grandezza, non una misura.
- `shock = 0.20` — nessuna fonte: scelto solo per essere strettamente minore di `erosion` e
  abbastanza alto da non rompere una forza per la perdita di un singolo mezzo in un gruppo
  piccolo (1 su 6 = 0.17 non basta).
- I due lati hanno **di default** gli stessi valori: l'asimmetria dottrinale, se voluta, va
  dichiarata esplicitamente dal chiamante (v. wiki `decisions/c2-hierarchy-design`), mai
  introdotta di nascosto da un default.

Da ricalibrare con il processo **ATCAL interno** (risolutore fine fatto girare offline), mai con
numeri da fonti non validate — in particolare **nessun coefficiente dei documenti Lanchester
ingeriti** (`:87-89`, coerente con l'avvertimento metodologico permanente della wiki
`decisions/virtual-session-engine-des`).

`get_disengagement_thresholds(side, thresholds=None) -> Optional[Dict[str, float]]`
(`:158-178`) restituisce una **copia** delle soglie del lato, o `None` se il lato non ne
dichiara — è `Engagement_Resolver` a decidere la propria politica su `None` (combatte fino
all'annientamento, con un warning — tranne per i blocchi non-Military, v. capitolo 4, §4.7).

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
legge di Pd (`Logic/Engagement_Resolver.py:172-184`, `:524-600`):

```
factor = (NIGHT_DETECTION_FACTOR se notte) * (ADVERSE_WEATHER_DETECTION_FACTOR se avverso)
```

`NIGHT_DETECTION_FACTOR = 0.7`, `ADVERSE_WEATHER_DETECTION_FACTOR = 0.8` (notte + meteo avverso =
0.56). **STIMA DICHIARATA**, nessuna fonte del progetto la fornisce; da ricalibrare via ATCAL
interno.

`weather_detection_factor(conditions)` legge `conditions` nella forma di
`Meteo_Analysis.get_meteo_conditions` (`{'day', 'night', 'adverse_weather'}`).
`weather_detection_factor_fn(conditions)` produce la callable `(observer, target) -> float`
richiesta da `resolve_engagement(detection_factor=...)`. `meteo_detection_factor(region_name,
date, time)` collega le due funzioni a `Logic/Meteo_Analysis.get_meteo_conditions` (oggi un
placeholder deterministico: nessuna casualità entra da qui).

**Limite noto, dichiarato** (`:536-541`): il fattore è **unico per ogni sensore**. La finestra di
contatto porta solo la portata migliore fra radar e TVD (`Mobile.detection_range`, default =
massimo dei due), e il risolutore non sa quale dei due l'ha prodotta: non può quindi risparmiare
al radar la degradazione notturna che fisicamente non subisce. Il valore notturno è un
compromesso fra i due sensori.

## 7.5 Le dimensioni militari di `Block/Military.py`

### `air_defense_power() -> float` (`Block/Military.py:579-616`)

È la dimensione che manca alla combat power: SAM, AAA e EWR valgono 0 nelle tabelle di efficacia
(`Context.GROUND_COMBAT_EFFICACY`) **per definizione**, perché quella misura fuoco e manovra
terra-terra, che loro non hanno — decisione Q3 della wiki
`decisions/virtual-session-engine-des`, confermata intenzionale. La loro potenza esiste, è di
natura diversa: `1 - Π(1 - danger_level_i)` sui `ThreatAA` costruiti dai volumi di difesa aerea
degli asset operativi ("almeno una delle difese è efficace"), saturante in [0,1], monotona nel
numero di siti. **Non è una combat power** e non è confrontabile con quella.

### `salvo_interceptors() -> List[Tuple[asset, canali]]` (`:618-663`)

Elenco degli asset del blocco che possono intercettare colpi in arrivo (Vehicle/Ship operativi
per cui esiste una `ThreatAA`), ciascuno con i propri canali (`engagement_channels('air')`, o
`DEFAULT_INTERCEPTION_CHANNELS` se non dichiarato). Ordinato per id dell'asset — l'ordine di
consumo delle scorte fa parte del contratto di riproducibilità. È la base consumata dal
risolutore d'ingaggio (capitolo 4, §4.5) per popolare `_ForceState.interceptors`.

### `salvo_interception_capacity() -> int` (`:665-717`)

```
capacita = Σ_i min(canali_i, scorta_i)
```

sugli asset di `salvo_interceptors()`. **STIMA DI PARTENZA DICHIARATA**: ogni canale intercetta
**un** colpo per salva (Pk dell'intercettore = 1 per canale — ipotesi ottimistica per la difesa,
primo candidato alla ricalibrazione). Nota: il risolutore d'ingaggio **non chiama direttamente**
questo metodo per calcolare la capacità durante la run (ricalcola con `_capacity`, capitolo 4,
§4.5, che replica la stessa formula sullo stato **ombra**, non sull'asset reale) — questo metodo
resta la funzione di lettura pubblica per chi consulta lo stato reale fuori da un ingaggio in
corso.

## 7.6 Munizioni e carburante su `Asset/Mobile.py` e `Asset/Aircraft.py`

### Munizioni offensive vs intercettori (`Asset/Mobile.py:132-201`)

Due contatori **distinti** dal 2026-09-23 (ricalibrazione, v. capitolo 4, §4.5):
`Mobile.ammunition` (munizioni offensive) e `Mobile.interceptor_stock` (intercettazioni ancora
possibili). Per i cannoni AA, `ROUNDS_PER_GUN_INTERCEPT = 100` (**STIMA DICHIARATA**, da
ricalibrare) converte colpi fisici in intercettazioni (uno Shilka da 2000 colpi → 20
intercettazioni, non 2000). Per un SAM **puro** (solo missile, nessun cannone: Buk, S-300, Osa,
Tor, Strela-10 — `interceptor_shares_ammunition = True`), `interceptor_stock` è una **vista** di
`ammunition`: stesso pool fisico, perché un missile lanciato offensivamente e un missile usato
per intercettare sono lo stesso oggetto fisico (`:184-201`, `Mobile.py:830-872`, proprietà
`interceptor_stock` con getter/setter che ridirige su `ammunition` quando condiviso).

`Mobile.consume_ammunition(rounds)` (`:717` e seguenti) e `Mobile.consume_interceptor_stock
(amount)` (`:882-913`) sono i due punti di applicazione consumati da
`apply_engagement_result` (capitolo 4, §4.12).

### Carburante (`Asset/Mobile.py:220-262`)

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
trattata come segnaposto, non come dato, `:258-262`).

### `Aircraft.assigned_loadout` (`Asset/Aircraft.py:160-234`)

La scorta di un aereo si ricava dal **loadout assegnato**, non dal modello (`Aircraft_Data` non
ha un campo `weapons`): prima di questa proprietà non esisteva alcuno stato "loadout di questo
volo" su un'istanza. Assegnare un loadout (`assigned_loadout = 'Strike'`) equivale ad armare il
velivolo per la missione: **riarma** l'aereo (ricalcola munizioni via
`load_ammunition_from_registry()` e carburante via `load_fuel_from_registry()`, sovrascrivendo
l'eventuale consumo precedente) — è quindi un'operazione del ciclo di campagna/assemblaggio
missione, **non** un canale di rifornimento durante l'ingaggio (il risolutore non la chiama mai).
`ammunition_from_registry()` (`:213-233`) somma, dal loadout, la quantità di ogni pylon che è
un'arma reale di `AIR_WEAPONS` (esclusi serbatoi e pod) più `gun_rounds`.

## 7.7 I punti di iniezione `fire_control` e `detection_factor`

Entrambi sono parametri **iniettati** in `resolve_engagement`/`run_session`, mai implementati dal
motore stesso — è il punto di estensione esplicito verso ciò che il motore non fa (v. capitolo
10):

- `fire_control: (shooter, target) -> ShotSpec | None` — interrogata al momento dello scheduling
  del lancio (capitolo 4, §4.4). `Session_Simulator.run_session` ne passa **una sola** a ogni
  ingaggio della sessione, non una per lato: la callable riceve gli asset reali e può distinguere
  lato/blocco/modello da sé (`Logic/Session_Simulator.py:101-107`, capitolo 6).
- `detection_factor: (observer, target) -> float in [0,1]` — degradazione della Pd (§7.4);
  default nessuna degradazione (`factor=1.0`).
