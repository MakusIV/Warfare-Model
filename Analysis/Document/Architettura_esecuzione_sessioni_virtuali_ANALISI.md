# Motore di esecuzione delle sessioni virtuali — analisi delle strategie e architettura proposta

Documento di analisi e progetto, 2026-09-21.

Nasce dalla proposta in [`Architettura_esecuzione_sessioni_virtuali.txt`](Architettura_esecuzione_sessioni_virtuali.txt),
che definisce il modello sessione/missione/operazione e propone due strategie alternative per
simularne l'esecuzione. Questo documento **non sostituisce** quel testo: lo analizza, ne verifica le
assunzioni temporali, lo confronta con lo stato dell'arte e propone un'architettura.

---

## 1. Scopo e legame col vincolo simulator-agnostic

Il vincolo architetturale di progetto è già stato dichiarato in
[`documentazione_dcs/ARCHITETTURA_CORE_AGNOSTICO.md`](documentazione_dcs/ARCHITETTURA_CORE_AGNOSTICO.md):

> Se si cancella l'intero adapter DCS, la campagna deve continuare a girare.

Quel documento (§5) identifica anche il tassello mancante e l'ordine di lavoro che ne consegue:

1. definire `SessionOrder` / `SessionOutcome` in termini puri di dominio;
2. scrivere il `SyntheticResolver`, anche rozzo, che soddisfa il contratto;
3. far girare una campagna intera **senza simulatore**;
4. **solo dopo** scrivere l'adapter DCS, obbligato a produrre lo stesso `SessionOutcome`.

**Il motore di esecuzione delle sessioni virtuali è esattamente il punto 2.** È il pezzo la cui
assenza, in DCE, rende quel progetto strutturalmente incapace di girare senza DCS: DCE non ha alcun
modello di combattimento proprio, la risoluzione degli ingaggi è delegata interamente al simulatore.
Tolto DCS, di DCE resta un generatore di file.

La posta in gioco di questo documento è quindi precisa: se il motore nasce male — troppo costoso per
girare, o modellato sulle strutture del simulatore — l'agnosticismo è perso prima ancora di essere
tentato.

---

## 2. Le due strategie come proposte

Riassunto fedele del testo sorgente, senza commento.

### Modello dati

- **Missione**: azioni di attacco/trasporto/posizionamento, definite da un tipo e numero di asset
  appartenenti a **un solo blocco**. Obiettivo: spostarsi dove è posizionato **un** blocco (per
  attaccarlo, rifornirlo o difenderlo) oppure una specifica zona (posizionamento).
  Ogni missione definisce: asset utilizzati, ruolo assegnato, direttive di missione (ROE, ...),
  e una rotta (`Route`).
- **Operazione**: insieme di missioni eseguite da asset di **blocchi diversi**, finalizzate allo
  stesso scopo.
- **Regola d'ingaggio**: se durante il tragitto asset di blocchi contrapposti si trovano a distanza
  di rilevamento e/o combattimento, agiscono in base alle direttive di missione.

### Strategia 1 — slot temporali su unità atomica

- Si definisce un'**unità atomica temporale** = durata di un ciclo.
- La si dimensiona sull'entità più veloce ipotizzabile: un missile ipersonico a 27 mach (9300 m/s)
  con raggio minimo distruttivo di 10 m → `t_minimo_evento = 1 ms`.
- Si suddivide quel millisecondo in N slot, uno per asset (N ≈ 10.000 = 100 blocchi × 100 asset)
  → `slot_temporale_asset = 0,1 µs`. Ogni asset è elaborato nel proprio slot; l'esecuzione
  sequenziale di tutti gli slot completa un ciclo.
- Non serve rispettare il tempo reale: lo slot serve come **riferimento per contare quanti cicli**
  richiede un evento o un'azione.
- Il comportamento dell'asset è decomposto in quattro classi con latenze proprie:
  **RIV** (rilevazione, dipende dai sensori), **VAL** (valutazione e decisione: ~100 ms per una
  macchina, ~10 s per un umano), **COM** (traduzione in comandi agli attuatori: 1 s per un pilota di
  carro WW2, 1 ms per un autopilota), **ATT** (attuazione: 0,1 s per la rotazione minima di una
  torretta, 0,5 s per lo sgancio di un missile).
- Esempio: aereo acquisito da radar nemico →
  `t_azione = 10 ms + 100 ms + 4 s + 0,1 s = 4,21 s`, `numero_cicli = 4,21 / 0,1 = 43`.
- La strategia si applica **solo** agli asset principali (Vehicle, Ship, Aircraft). Gli effetti
  degli armamenti (missili A2A/A2G/G2A/A2S/S2A, cannoni, mitragliatrici, bombe) sono risolti con
  **calcolo probabilistico** basato su capacità dell'arma, caratteristiche, posizione e assetto di
  asset e bersaglio, e tipologia dell'ambiente.

### Strategia 2 — risoluzione probabilistica

Valutare mediante calcolo probabilistico quali saranno tutti gli eventi della sessione che
determineranno lo stato e le azioni degli asset — primi fra tutti quelli di combattimento fra le
fazioni — determinare e valutare le azioni conseguenti, aggiornando lo stato dello scenario.

---

## 3. Verifica delle assunzioni temporali

### 3.1 La catena di derivazione è aritmeticamente corretta

| passaggio | valore |
|---|---|
| 27 mach | 9.288 m/s |
| 10 m a 27 mach | **1,077 ms** |
| slot = t_min / 10.000 | **1,077·10⁻⁷ s** |

Entrambi i valori confermano quelli del testo (1 ms, 0,1 µs).

### 3.2 C'è un'incongruenza nel conteggio dei cicli

Il testo calcola `t_azione = 4,21 s` e poi `numero_cicli = 4,21 / 0,1 = 43`.
Il divisore `0,1` non è né lo slot per asset né il ciclo:

| se si divide per | cicli |
|---|---|
| slot asset (1,08·10⁻⁷ s) | 39.102.480 |
| ciclo (1,08·10⁻³ s) | 3.910 |
| 0,1 s — il valore usato nel testo | 42 (il testo riporta 43) |

Va deciso esplicitamente quale sia l'unità di conteggio. Nell'architettura proposta al §6 la domanda
decade: il tempo si misura in **secondi assoluti**, non in cicli.

### 3.3 Il costo del tick da 1 ms non è sostenibile

Sessione di 2 h, 10.000 asset, tick da 1,077 ms → 6.687.360 tick × 10.000 =
**6,687·10¹⁰ aggiornamenti-asset**.

| ipotesi di costo per aggiornamento | tempo di calcolo |
|---|---|
| 0,17 µs — pavimento assoluto di CPython, loop **vuoto** (arXiv 1306.6047) | 11.369 s = **3,2 h** |
| 95,7 µs — Mesa, benchmark SIR reale (logica applicativa vera) | 6.399.804 s = **74 giorni** |

La prima riga è già più lenta del tempo reale **con zero lavoro utile svolto**. La seconda è la
stima onesta per un motore in Python puro con logica vera: un rapporto reale/simulato di ~1:890.

E questo prima di considerare il rilevamento. Se ogni asset deve controllare gli altri per vedere
chi rileva chi — che è precisamente il caso d'uso di RIV — il costo per tick diventa O(N²):
10.000² × 6.687.360 ≈ **6,687·10¹⁴ operazioni**, cioè **3,6 anni** al pavimento assoluto di CPython
e **~21 anni** a 1 µs per controllo di distanza.

### 3.4 Il costo in funzione del passo

Stesse ipotesi (2 h, 10.000 asset), 10 µs per aggiornamento:

| dt | tick | aggiornamenti | tempo di calcolo |
|---|---|---|---|
| 1 ms | 7.200.000 | 7,2·10¹⁰ | 200 h |
| 0,1 s | 72.000 | 7,2·10⁸ | 2 h |
| 1 s | 7.200 | 7,2·10⁷ | 12 min |
| 5 s | 1.440 | 1,44·10⁷ | 2,4 min |
| 10 s | 720 | 7,2·10⁶ | 1,2 min |
| 60 s | 120 | 1,2·10⁶ | 12 s |

La transizione da impossibile a banale avviene fra 0,1 s e 1 s.

### 3.5 Il passo è dimensionato sull'entità sbagliata

Il testo esclude esplicitamente i missili dalla simulazione a tick ("per la simulazione degli effetti
degli armamenti si utilizzerà il calcolo probabilistico"). **Il passo è quindi dimensionato su un
oggetto che non verrà simulato a tick.** L'entità più veloce effettivamente simulata è un aereo
(~600 m/s), e la granularità spaziale che conta non è il raggio letale di 10 m, ma l'**ingresso in un
inviluppo di rilevamento o ingaggio**, che si misura in chilometri.

Passo massimo per non "saltare" un inviluppo (`dt_max = 2R/v`, il vincolo classico di *tunneling*):

| inviluppo | vs caccia 600 m/s | vs trasporto 250 m/s | vs colonna 15 m/s |
|---|---|---|---|
| AAA/MANPADS 2 km | 6,7 s | 16,0 s | 266,7 s |
| SHORAD 5 km | 16,7 s | 40,0 s | 666,7 s |
| SA-6 35,6 km | 118,7 s | 284,8 s | 4.746,7 s |
| LORAD 100 km | 333,3 s | 800,0 s | 13.333,3 s |

Il vincolo reale è **3-4 ordini di grandezza** più lasco di 1 ms.

E comunque il tunneling **non si risolve rimpicciolendo il passo globale**: le tecniche standard sono
il *continuous collision detection* per volume spazzato, il *conservative advancement*, e soprattutto
il calcolo analitico del **punto di massimo avvicinamento (CPA)** — cioè si calcola l'istante di
intersezione invece di iterarlo.

---

## 4. Confronto con lo stato dell'arte

### 4.1 Nessun simulatore entity-level reale usa un tick fine

| sistema | livello | avanzamento del tempo | capacità | note |
|---|---|---|---|---|
| **JTLS** | aggregato (btg/brigata) | **time-stepped**, griglia esagonale | teatro intero | usa Lanchester via "Lanchester Development Tool"; aria/mare invece a entità |
| **JCATS** (LLNL) | entità | **event-stepped** | ~100.000 entità | C/C++, **single-threaded**; Pk per singolo colpo |
| **BRAWLER** | entità (velivoli) | event-driven, stocastico | ~20 velivoli | riferimento storico per il combattimento aereo |
| **AFSIM** (AFRL) | entità/piattaforma | coda eventi | — | framework usato per IADS/difesa aerea |
| **ESAMS / Suppressor** | ingaggio (engineering) | sequenza di fasi | 1 ingaggio, alta fedeltà | riferimento diretto per RIV/VAL/COM/ATT |
| **EADSIM** | mission, many-on-many | non dichiarato | — | usato da ~390 agenzie |
| **VR-Forces**, **MASA SWORD** | aggregato + entità | multi-risoluzione dichiarata | — | il livello di dettaglio è una scelta esplicita |

Il pattern è netto: **dove il time-stepping esiste davvero (JTLS) è confinato al livello aggregato**;
dove si simula la singola piattaforma o il singolo colpo, il meccanismo è **a eventi**. E JCATS, che
è l'unico a reggere ~100.000 entità, è codice nativo ottimizzato da decenni e gira su un solo core.

La letteratura DES è esplicita sul perché: con scale temporali eterogenee un delta globale porta a
*"tremendous waste of processor resources"*. La Strategia 1 è esattamente quello scenario — un carro
(ATT ~0,1 s), un pilota umano (COM ~1-4 s) e un missile ipersonico (1 ms) nella stessa griglia.

### 4.2 Le latenze RIV/VAL/COM/ATT sono giuste — ma sono tutte ≫ 1 ms

La decomposizione proposta è sostanzialmente il ciclo OODA applicato all'entità, ed è la parte
migliore della Strategia 1. I valori reali documentati:

| sistema | latenza rilevazione → lancio |
|---|---|
| 9K33 Osa | ~26 s |
| S-300P | ~28 s |
| Tor (da fermo) | 5-8 s |
| Tor-M2, "short stop" | 2-3 s |
| pilota umano (reazione) | 1-2 s |
| equipaggio carro, per bersaglio | ~31 s |
| IADS: valutazione della minaccia | entro un aggiornamento radar (~1 s) |
| IADS: assegnazione arma-bersaglio | poche centinaia di ms |
| kill chain F2T2EA (obiettivo dottrinale) | ≤ 10 min |

Tutto è **1-2 ordini di grandezza sopra il millisecondo**. L'unico evento che richiederebbe davvero
il millisecondo è l'endgame del missile ipersonico — che il testo stesso propone di risolvere
probabilisticamente.

**Conclusione**: queste latenze vanno conservate come **parametri di reazione per tipo di asset**,
schedulate come eventi futuri ("questo asset reagirà fra 4,21 s"), non contate come 3.910 iterazioni.

### 4.3 Il principio mancante: modellazione multi-risoluzione

Paul K. Davis (RAND) ha fondato il filone della *variable-resolution / multiresolution modeling*
proprio per rispondere al problema che la Strategia 1 ignora: **come evitare di simulare tutto alla
risoluzione più fine**.

L'applicazione reale è la federazione **JTLS-JCATS**: le unità viaggiano aggregate a passo grosso
finché non entrano in un'area di interesse tattico, dove vengono **disaggregate** in entità e passate
al motore a eventi a grana fine.

La Strategia 1 non prevede nulla di simile: tratta allo stesso modo il 99% del tempo di sessione
(marcia, attesa, transito) e i pochi minuti di ingaggio attivo in cui la grana fine serve davvero.

### 4.4 Ordine di esecuzione: un artefatto da mitigare in ogni caso

Processare 10.000 slot in sequenza dentro lo stesso ciclo introduce un bias documentato: l'asset
elaborato per primo vede lo stato prima che gli altri agiscano, l'ultimo li vede già tutti aggiornati.
È il classico *order-of-execution bias* della letteratura agent-based. Mesa lo formalizza con due
regimi alternativi: `RandomActivation` (ordine casuale a ogni passo) e `SimultaneousActivation`
(tutti calcolano il prossimo stato, poi tutti avanzano) — quest'ultima *"prevents early-acting agents
from influencing later ones within the same step"*.

La mitigazione va adottata **a prescindere dal motore scelto**, perché lo stesso problema si ripresenta
in una coda di eventi con eventi simultanei.

### 4.5 Avvertimento sulla Strategia 2: i modelli a puro rapporto di forze falliscono

Questo punto riguarda direttamente il codice già esistente nel progetto.

- **Lanchester** è stato testato almeno **nove volte** su dati storici reali (database Ardenne, Kursk)
  e **non si valida**. Willard trova addirittura esponenti negativi. Lucas & Turkes (2004) trovano
  che legge quadratica, lineare e logaritmica si adattano *tutte ugualmente male* — cioè la scelta
  della legge diventa arbitraria. L'unica validazione forte (Engel su Iwo Jima, R² = 0,9937) è un
  caso isolato.
- **La regola 3:1 nella versione RAND** usata da JICM con Situational Force Scoring: su 98 ingaggi
  divisionali storici con rapporto di forze 2,5-3,5:1, solo il **19%** rientra nel range predetto —
  **peggio di una previsione casuale**. Il Dupuy Institute raccomanda esplicitamente di non usare
  JICM con SFS finché l'errore non è corretto.

La diagnosi è che un rapporto di forze aggregato **non cattura né la sequenza degli eventi né
l'iniziativa** — chi spara per primo, chi ha sorpresa, terreno, addestramento — fattori che nella
realtà dominano l'esito più del conteggio.

**Ricaduta diretta sul progetto**: `Logic/Tactical_Evaluation.py:251 calcFightResult` è esattamente
un modello a rapporto di forze con coefficienti `k` tabellati a mano, ed è annotato *"for ground
virtual mission simulation"*. Va mantenuto come **fallback aggregato**, non promosso a risolutore
primario.

### 4.6 Strumenti formali già pronti da adottare

| strumento | formula | uso previsto |
|---|---|---|
| **Catena di uccisione** | `Pk = Pd × Pid × Pe(ROE) × Ph × Pk\|h` | risoluzione del singolo ingaggio |
| **Modello a salva (Hughes)** | `ΔA = −(βB − yA)·u`, `ΔB = −(αA − zB)·v` | scambi molti-contro-molti senza N×M duelli |
| **CPA / TCPA** | `t* = −(Δr · Δv) / \|Δv\|²` | istante di contatto fra due traiettorie, analitico |
| **Sopravvivenza di rotta** | `P(sopravv.) = Π_i P(sopravv. segmento_i)` — prodotto, non somma | esposizione di una rotta a più minacce |
| **Equazione radar** | `SNR = (Pt·Gt·Ar·σ·τ) / ((4π)²·R⁴·k·Ts·L)` | Pd in funzione della distanza (dipendenza R⁴) |
| **ATCAL** | stima ai minimi quadrati dei coefficienti aggregati dall'output di un modello fine | calibrare un eventuale livello aggregato futuro |

Nel modello a salva: α, β = potere offensivo (missili lanciati con precisione per salva, per unità);
y, z = potere difensivo (missili intercettati per salva); w, x = *staying power* (colpi necessari a
neutralizzare un'unità), con u = 1/w, v = 1/x. È chiuso, sta in poche righe, ed è nato proprio per
essere risolto **senza** time-stepping. Si generalizza bene a ogni scambio "a impulsi" — un pacchetto
d'attacco contro una batteria SAM, una scarica di artiglieria — meno al fuoco continuo terrestre.

Su **ATCAL** una nota di metodo importante: è il ponte canonico alta→bassa risoluzione, introdotto
nel 1983 nel modello CEM dell'esercito USA. Se in futuro servirà un livello aggregato per gli scontri
di massa, i coefficienti **non vanno inventati a mano**: vanno stimati facendo girare offline il
risolutore fine su scenari rappresentativi.

---

## 5. Verdetto: due strati, non due alternative

Le due strategie non sono in concorrenza. Descrivono due cose diverse, ed entrambe servono:

- la **Strategia 1** fornisce la *semantica del comportamento dell'asset* — RIV/VAL/COM/ATT, chi
  reagisce e quando, e quindi **chi spara per primo**. È l'unica delle due che affronta l'iniziativa,
  cioè precisamente ciò la cui assenza fa fallire empiricamente i modelli a rapporto di forze (§4.5);
- la **Strategia 2** fornisce la *semantica dell'esito* — probabilità, perdite, danni, consumi.

Ciò che manca a entrambe è il **meccanismo di avanzamento del tempo**:

- la Strategia 1 ne propone uno (il tick) che non regge né l'aritmetica (§3.3) né il confronto con la
  pratica reale (§4.1);
- la Strategia 2 non ne propone nessuno, e quindi non dice **quando e se** due forze opposte si
  incontrano. Senza quello, "valutare probabilisticamente quali eventi determineranno lo stato degli
  asset" non ha input geometrici da cui partire. **È il buco più grave delle due proposte**, ed è il
  pezzo che l'architettura sotto va a colmare.

La risposta — confermata sia dalla letteratura DES sia da ogni simulatore entity-level reale — è una
**coda di eventi con i contatti calcolati analiticamente**.

---

## 6. Architettura proposta: DES con scheduling analitico dei contatti

Quattro strati. Il tempo di sessione è in **secondi assoluti** dall'inizio sessione. Non esiste
nessun tick globale.

### Strato 0 — Contratto di dominio

`SessionOrder` / `SessionOutcome` in termini puri di dominio: nessun identificatore, unità o concetto
del simulatore. È il passo 1 di `ARCHITETTURA_CORE_AGNOSTICO.md` §5 e resta il primo da fare, perché
è ciò a cui l'adapter DCS dovrà poi conformarsi.

### Strato 1 — Scheduler dei contatti

Il pezzo mancante. Da rotte, volumi di minaccia e traiettorie produce una **lista ordinata nel tempo
di finestre di contatto**, per via analitica:

- **mobile vs minaccia statica**: intersezione rotta↔cilindro → segmenti di esposizione →
  intervalli temporali, convertiti con `Route.travelTimeToEdge`;
- **mobile vs mobile**: CPA/TCPA fra le due funzioni posizione(t);
- **potatura gerarchica**: prima a livello di Block (posizione del blocco + raggio massimo fra
  rilevamento e ingaggio), poi solo le coppie di asset dentro i blocchi candidati. È questa potatura
  che evita l'O(N²) che affonda la Strategia 1.

Output: `ContactWindow(t_inizio, t_fine, t_cpa, d_min, asset_A, asset_B)`.

### Strato 2 — Risolutore d'ingaggio

Su ogni finestra, e **solo** su quella:

1. **Pd** in funzione della distanza al CPA e del raggio di acquisizione del sensore, degradata da
   meteo e notte (`Meteo_Analysis` restituisce già `day` / `night` / `adverse_weather`);
2. **latenza di reazione** RIV+VAL+COM+ATT, per tipo di asset e `SKILL` dell'equipaggio → decide
   **chi spara per primo**. Qui vive la parte salvata della Strategia 1;
3. **ROE / dottrina** decide: ingaggia, evita, prosegue;
4. **selezione arma e Pk** dai database esistenti (`accuracy × destroy_capacity` per
   `(target_type, dimensione)`), modulata dalla posizione dentro l'inviluppo;
5. **scambi molti-contro-molti** risolti col modello a salva, non con N×M duelli.

### Strato 3 — Applicazione dello stato

Danno per singolo asset, consumo munizioni e carburante, assemblaggio del `SessionOutcome`, scrittura
in `Campaign_State` in un'unica passata — è la responsabilità già assegnata a
`Theater_Session_Manager` nel design della gerarchia C2.

### Disciplina trasversale, non negoziabile

- **RNG di sessione seedato** da `(session_id, mission_id, event_id, contatore)`. Ogni estrazione
  stocastica passa da lì. Attenzione: **l'ordine di risoluzione degli eventi fa parte del contratto**
  — salvare solo il seed non basta a garantire il replay, perché un PRNG riproduce la stessa sequenza
  solo a parità di *ordine delle chiamate*.
- **Risoluzione simultanea**: si calcola dallo stato a `t`, si applica insieme (§4.4). Tie-break
  deterministico su `(t, tipo_evento, id)`.
- **Geometria numerica** (float/numpy) dentro il risolutore. `sympy` è simbolico ed esatto, quindi
  lento: va bene per costruire gli scenari, non per milioni di valutazioni.
- **Una sola estrazione per evento** nella campagna vera. Le repliche multiple e il valore atteso
  servono solo in fase di analisi e taratura del modello, mai per produrre la storia canonica.

### Micro-passo opzionale

Se un ingaggio prolungato richiede granularità, si ammette un passo fine (1-5 s) **solo dentro la
finestra attiva e solo sugli asset coinvolti**. È l'aggregazione/disaggregazione della federazione
JTLS-JCATS (§4.3), non un tick globale.

Col budget di calcolo concesso (minuti), il margine è ampio: 10.000 asset a passo 5 s per 2 h costano
~2,4 minuti anche nell'ipotesi pessimistica di aggiornare *tutti* gli asset a ogni passo (§3.4) — e
nella realtà solo una frazione è in contatto.

---

## 7. Precondizioni bloccanti già presenti nel codice

Il motore non è scrivibile finché queste non sono risolte. Ogni riga è stata verificata sul codice.

| # | Problema | Dove | Gravità |
|---|---|---|---|
| 1 | **La velocità degli asset non esiste a runtime.** `checkParam` è definita senza `self`; il setter `speed` la chiama come `self.checkParam(speed=param)` → `TypeError` garantito. Inoltre il default è un dizionario mutabile `{"nominal": None, "max": None}` condiviso fra istanze, e **nessuna riga popola `_speed` dai registry** | `Asset/Mobile.py:345`, `:97-100`, `:50`, `:59` | **bloccante** — senza velocità non c'è posizione(t), quindi nessun contatto calcolabile |
| 2 | Di conseguenza `_get_nominal_speed`/`_get_max_speed` restituiscono 0 (Vehicle) o `None` (Aircraft/Ship), e `time_to_direct_line_attack` divide per zero | `Block/Military.py:455-467`, `:363` | bloccante |
| 3 | **Nessuna API di raggio di rilevamento.** I dati esistono e sono ricchi (`radar.capabilities[air\|ground\|sea]` con `acquisition_range`, `tracking_range`, `engagement_range`, `multi_target_capacity`, in km; più `TVD` ottico/termico), ma nessuna classe li espone | `Asset/Vehicle_Data.py`, `Aircraft_Data.py`, `Ship_Data.py` | bloccante |
| 4 | **`ThreatAA` non è mai costruito da dati reali.** La classe funziona ed è testata, `Mobile.air_defense_volume()` produce il `Cylinder`, ma nessuno collega i due: `ThreatAA` è istanziato solo nei test e nel visualizer con valori hard-coded | `Logic/Air_Route_Manager.py:32`, `Asset/Mobile.py:208` | bloccante, ma è il ponte più economico da costruire |
| 5 | **Nessuna API per applicare danno.** Non esiste `apply_damage`/`take_damage`; l'unica via è `asset.health = int`. E un asset è già "Destroyed" a `health ≤ 15`, non a 0 | `Asset/Asset.py:207-210`, `DataType/State.py:178-198` | bloccante per l'esito per-asset richiesto |
| 6 | **`random` non controllato**, usato a livello di modulo in più punti del dominio | `Logic/Tactical_Evaluation.py:360-361`, `Asset/Structure.py:128`, `Utility/Utility.py:320`, DB armi | bloccante per la riproducibilità richiesta |
| 7 | **Tre modelli Route/Edge/Waypoint mutuamente incompatibili**: `DataType/`, `Air_Route_Manager` e `Ground_Route_Manager` definiscono classi omonime e diverse. L'unico consumato dall'ecosistema è `DataType.Route`, che però **nessun generatore produce** | `DataType/Route.py`, `Logic/Air_Route_Manager.py:218`, `Logic/Ground_Route_Manager.py` | da decidere prima dello Strato 1 |
| 8 | `DataType/Event.py` è rotto: `isPush`/`isPop`/`isHit`/`isAssimilate`/`isMove` leggono `self._type`, mai assegnato (`__init__` scrive `_event_type`). Importato da 8 moduli, nessun `Test_Event.py` | `DataType/Event.py:81-95` | da sostituire con la nuova coda eventi, o riparare |
| 9 | `evaluateGroundRouteDangerLevel` è rotta su tre punti: `danger = {"air_attack": list}` assegna il *tipo* invece di `[]`; `route.travelTime` è usata senza parentesi (è un metodo); `is_airbase`/`is_groundbase` non esistono su `Military` | `Logic/Tactical_Evaluation.py:532-579` | il concetto (esposizione temporale della rotta) è giusto, il codice va riscritto |
| 10 | **SAM/AAA/EWR hanno combat power ≡ 0 per costruzione**: `GROUND_COMBAT_EFFICACY` contiene solo Tank, Armored, Motorized, Artillery_Semovent, Artillery_Fixed | `Context/Context.py:502-507` | buco grave per un motore d'ingaggio |
| 11 | `DataType/Threat.py` (`NameError` su `General` e `obj`) e `DataType/Volume.py` (`inside()` ritorna sempre `False`) sono codice morto | — | da non usare come base |

### Le fondamenta buone, però, ci sono

- **`DataType/Cylinder.py`** (924 righe, 404 di test): `innerPoint()` è il test punto-volume,
  `getIntersection(Segment3D, tolerance)` è il test segmento-volume, incluse le superfici orizzontali.
  È esattamente la geometria che serve allo Strato 1.
- **I database d'arma** hanno già `accuracy` × `destroy_capacity` per `(target_type, dimensione)` con
  variabilità stocastica dichiarata (`perc_efficiency_variability`). `Aircraft_Weapon_Data` ha persino
  `reliability`, `accuracy`, `manouvrability` e `seeker` al livello superiore.
- **`Route.travelTimeToEdge(edge)`** è già il gancio per posizionare un asset su una rotta a un `t`
  dato: la rotta conosce le durate relative, le manca solo l'istante assoluto.
- **`Combat_Power_Estimation`** e **`Tactical_Analysis`** sono completi e testati.
- **`Military.time2attack`**, `combat_range()`, `air_defense_volume()`, `artillery_in_range()`,
  `combat_state()` sono implementati e testati.

---

## 8. Roadmap

Implementazione soggetta ad approvazione separata.

| Fase | Contenuto | Nuovi file |
|---|---|---|
| **0** | Contratto `SessionOrder`/`SessionOutcome` + RNG di sessione seedato | `Command/Session_Types.py`, `Utility/Session_Rng.py` |
| **1** | Cinematica utilizzabile: fix di `Mobile.checkParam`, ponte registry→`asset.speed` con tutto normalizzato in **m/s** nel core (km/h, nodi e mph sono conversioni dell'adapter), `posizione(t)` su `DataType.Route` | correzioni |
| **2** | Percezione: `Mobile.detection_range(mode)` sulla falsariga di `combat_range()`; fabbrica `ThreatAA` da `air_defense_volume()` + dati arma | correzioni |
| **3** | Scheduler dei contatti: intersezione rotta↔cilindro → intervalli, CPA/TCPA, potatura a livello Block | `Logic/Contact_Scheduler.py` |
| **4** | Risolutore d'ingaggio: Pd → latenza di reazione → ROE → Pk; salva di Hughes per molti-contro-molti; profili RIV/VAL/COM/ATT per tipo asset e `SKILL` | `Logic/Engagement_Resolver.py`, `Context/Reaction_Profile.py` |
| **5** | Applicazione danno per-asset, consumi, assemblaggio `SessionOutcome` | API su `Asset`/`Block` |
| **6** | Orchestratore a coda eventi (heapq, clock in secondi), risoluzione simultanea | `Logic/Session_Simulator.py` |
| **7** | Validazione: scenari di plausibilità, test di determinismo (stesso seed → stesso outcome), **test di agnosticismo** (campagna intera senza simulatore) | `Test/Test_Session_Simulator.py` ecc. |

Le fasi 1 e 2 sono correzioni a codice esistente e sbloccano tutto il resto: senza velocità e senza
raggio di rilevamento, lo Strato 1 non è scrivibile.

---

## 9. Decisioni prese e questioni aperte

### Decise

1. **Scala**: i 10.000 asset sono un **limite superiore teorico**. Si progetta sul caso tipico e si
   verifica la degradazione verso il limite.
2. **Riproducibilità**: una sessione deve essere **riproducibile da seed**. Ne discende l'obbligo di
   incapsulare ogni estrazione stocastica e di fissare l'ordine di risoluzione degli eventi.
3. **Granularità dell'esito**: perdite e danni **per singolo asset**. Ne discende la necessità di
   un'API di applicazione del danno (precondizione 5).
4. **Budget di calcolo**: fino a **minuti** per sessione. Questo rende sostenibile il micro-passo
   opzionale e toglie ogni pressione sull'ottimizzazione prematura.

### Erano aperte — CHIUSE il 2026-09-22 (le tre bloccanti per la Fase 3)

- **✅ Quale modello di Route vince → `DataType.Route/Edge/Waypoint`, confermato.** I modelli
  interni a `Ground_Route_Manager` e `Air_Route_Manager` restano, ma come **stato di lavoro privato
  dell'algoritmo di ricerca**, mai esposto; la conversione avviene in un solo punto, l'uscita
  pubblica del path-finding (`Logic/Route_Adapter.py`, `RoutePlanner.calcCanonicalRoute`,
  `NavigationGraph.find_canonical_route`). Fatto decisivo: **nessun consumatore di produzione** usa
  oggi i due generatori, mentre tutto l'ecosistema consuma solo il tipo canonico. Rimosso il blocco
  tecnico: `DataType.Edge` non era costruibile per una salita verticale pura (sympy rifiuta due
  punti coincidenti in `Line2D`). Piano a 5 fasi, Fase 1 fatta.
- **✅ Semantica della perdita per-asset → contratto fissato in `Logic/Damage_Model.py`.**
  `accuracy` = P(colpo a segno), `destroy_capacity` = P(distruzione | colpo a segno): scomposizione
  in Ph e Pk|h della Pk `accuracy × destroy_capacity` già usata nei registri d'arma, **senza
  introdurre costanti di taratura nuove**. Tre esiti per colpo (KILL → salute 0; DAMAGE →
  `−round(100 × dc)`, minimo 1; MISS), un colpo **può** uccidere direttamente, l'accumulo è
  emergente (~1/dc colpi non letali). Nessuna estrazione casuale nel modulo: `resolve_hit` riceve il
  `draw` dall'RNG di sessione, e l'ordine delle soglie fa parte del contratto. `DamageEvent` (frozen,
  con `provenance`) è l'atomo del futuro `SessionOutcome`. La soglia `Destroyed ≤ 15` **non** viene
  rivista: il residuo è il relitto, e la messa fuori combattimento avviene comunque già prima
  (`isOperative()` è falso sotto il 50%, e `combat_power` somma solo gli operativi — "mission kill" e
  "distruzione" sono quindi già entrambi nel modello). Scritta `Asset.apply_damage`.
- **✅ Combat power di SAM/AAA/EWR → restano fuori, ed è la definizione, non un bug.** Le tabelle di
  efficacia misurano fuoco e manovra terra-terra: includerli gonfierebbe la forza di superficie del
  blocco che li possiede. Documentato come intenzionale in `Context/Context.py`. **Ma il problema
  pratico esiste**: in `Tactical_Evaluation._calculate_priority` un bersaglio a combat power nulla
  satura a `combat_power_ratio = 0.1`, cioè priorità minima — l'opposto della dottrina SEAD. La
  soluzione è una **dimensione separata**, non una voce in più nella stessa tabella: nuova
  `Military.air_defense_power()` in [0, 1], aggregazione `1 − Π(1 − danger_level_i)` sui `ThreatAA`
  del blocco. Farla leggere alla priorità di targeting per un attaccante aereo è lavoro della Fase 4
  e **richiede conferma dell'utente**, perché cambia numeri di campagna.

### Ancora aperte (non bloccanti per la Fase 3)

- **Sistema di riferimento.** Resta aperta la questione già sollevata in
  `ARCHITETTURA_CORE_AGNOSTICO.md` §8: piano cartesiano locale per teatro (con la proiezione
  nell'adapter) o coordinate geodetiche nel core.
- **Penetrazione contro corazza.** `Vehicle_Data.protections.armor` ha gli spessori per tipo di
  munizione, ma **nei record d'arma non esiste alcun campo `penetration`**: oggi il confronto non è
  calcolabile. Va deciso se introdurlo o se restare al livello `accuracy × destroy_capacity`.

---

## 10. Bibliografia

### Meccanismi di avanzamento del tempo e simulazione a eventi
- [Discrete-event simulation — Wikipedia](https://en.wikipedia.org/wiki/Discrete-event_simulation)
- [Introduction to discrete-time simulation — Software Solutions Studio](https://softwaresim.com/blog/introduction-to-discrete-time-simulation/)
- [Parallel Discrete Event Simulation: The Making of a Field — WSC 2017](https://www.informs-sim.org/wsc17papers/includes/files/019.pdf)
- [The effects of time advance mechanism on simple agent behaviors in combat simulations](https://www.researchgate.net/publication/254050543_The_effects_of_time_advance_mechanism_on_simple_agent_behaviors_in_combat_simulations)

### Simulatori militari reali
- [JCATS — Lawrence Livermore National Laboratory](https://computing.llnl.gov/projects/jcats)
- [JCATS v16 Hardware and NET Requirements](https://csl.llnl.gov/sites/csl/files/2021-04/JCATS-v16-Hardware-NET-Requirements_0.pdf)
- [Multi-Resolution Modeling in the JTLS-JCATS Federation — MITRE](https://www.mitre.org/sites/default/files/pdf/bowers_modeling.pdf)
- [Joint Theater Level Simulation — Wikipedia](https://en.wikipedia.org/wiki/Joint_Theater_Level_Simulation)
- [BRAWLER Tactical Air Combat Simulation — DSIAC](https://dsiac.dtic.mil/wp-content/uploads/2019/04/BRAWLER.pdf)
- [AFSIM — Stellar Science](https://www.stellarscience.com/project/afsim/)
- [ESAMS Engagement-Level Model Overview — JASP](https://jasp-online.org/model-simulations/esams)
- [EADSIM — TBE](https://www.tbe.com/missionsystems/eadsim)
- [VR-Forces Capabilities — MAK Technologies](https://www.mak.com/vr-forces/capabilities)

### Modellazione multi-risoluzione
- [An Introduction to Variable-Resolution Modeling — RAND R-4252 (Davis)](https://www.rand.org/pubs/reports/R4252.html)
- [Experiments in Multiresolution Modeling — RAND MR1004](https://www.rand.org/pubs/monograph_reports/MR1004.html)

### Attrito, Lanchester e validazione
- [Lanchester's laws — Wikipedia](https://en.wikipedia.org/wiki/Lanchester%27s_laws)
- [Lanchester equations have been weighed — The Dupuy Institute](https://dupuyinstitute.org/2016/02/29/lanchester-equations-have-been-weighed/)
- [Fitting Lanchester equations to the battles of Kursk and Ardennes — Lucas & Turkes (2004)](https://onlinelibrary.wiley.com/doi/10.1002/nav.10101)
- [Comparing the RAND Version of the 3:1 Rule to Real-World Data — The Dupuy Institute](https://dupuyinstitute.org/2018/03/05/comparing-the-rand-version-of-the-31-rule-to-real-world-data/)
- [Ground Combat in the JICM — RAND MR422](https://www.rand.org/pubs/monograph_reports/MR422.html)
- [Situational Force Scoring — RAND N3423](https://www.rand.org/pubs/notes/N3423.html)
- [Attrition Calibration (ATCAL) Evaluation Phase II — DTIC](https://apps.dtic.mil/sti/pdfs/ADA302795.pdf)
- [Attrition rates and maneuver in agent-based simulation models — Ormrod & Turnbull (2017)](https://journals.sagepub.com/doi/abs/10.1177/1548512917692693)

### Ingaggio probabilistico
- [Probability of kill — Wikipedia](https://en.wikipedia.org/wiki/Probability_of_kill)
- [Salvo combat model — Wikipedia](https://en.wikipedia.org/wiki/Salvo_combat_model)
- [A salvo model of warships in missile combat — Hughes (1995)](https://onlinelibrary.wiley.com/doi/abs/10.1002/1520-6750(199503)42:2%3C267::AID-NAV3220420209%3E3.0.CO;2-Y)
- [Radar Range Equation — MathWorks](https://www.mathworks.com/help/radar/ug/radar-equation.html)
- [Modeling Radar Detectability Factors (Swerling) — MathWorks](https://www.mathworks.com/help/radar/ug/modeling-radar-detectability-factors.html)
- [Kill chain (military) — Wikipedia](https://en.wikipedia.org/wiki/Kill_chain_(military))
- [Integrated Air Defence Systems — The Aeronautical Society](https://www.aerosociety.com/media/7514/3-limnaios-integrated-air-defence-systems-countering-lo-airborne-threats.pdf)

### Latenze reali
- [9K33 Osa — Wikipedia](https://en.wikipedia.org/wiki/9K33_Osa)
- [Tor missile system — Wikipedia](https://en.wikipedia.org/wiki/Tor_missile_system)
- [M1 Tank Gunnery: A Detailed Analysis — DTIC ADA217416](https://apps.dtic.mil/sti/pdfs/ADA217416.pdf)

### Geometria e ordine di esecuzione
- [Fast-CPA: rapid closest point of approach calculations — IEEE](https://ieeexplore.ieee.org/document/8232338/)
- [C2A — Controlled Conservative Advancement](https://graphics.ewha.ac.kr/projects/details/C2A/C2A.pdf)
- [Continuous Collision Detection — DigitalRune](https://digitalrune.github.io/DigitalRune-Documentation/html/138fc8fe-c536-40e0-af6b-0fb7e8eb9623.htm)
- [Agent Activation — Mesa documentation](https://mesa.readthedocs.io/latest/tutorials/2_agent_activation.html)

### Prestazioni in Python
- [How fast can we make interpreted Python? — arXiv 1306.6047](https://arxiv.org/pdf/1306.6047)
- [AMBER: A Columnar Architecture for High-Performance ABM in Python — arXiv 2601.16292](https://arxiv.org/pdf/2601.16292)

### Teoria del wargame
- [Combat results table — Wikipedia](https://en.wikipedia.org/wiki/Combat_results_table)
- [Simulating War: Studying Conflict Through Simulation Games — Philip Sabin](https://www.researchgate.net/publication/273947290_Simulating_War_Studying_Conflict_Through_Simulation_Games)
- [Variance reduction — Wikipedia](https://en.wikipedia.org/wiki/Variance_reduction)
