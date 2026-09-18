# Core simulator-agnostic — implicazioni dell'analisi DCE/DCS

Nota architetturale, 2026-09-18. Nasce da un vincolo di progetto dichiarato:

> Un core Python che modella **tutti** gli aspetti del modello, integrato al simulatore
> tramite moduli di interfaccia. Il simulatore può essere diverso da DCS. L'architettura del
> core deve essere **indifferente** rispetto al simulatore, e deve consentire in linea
> teorica di gestire una campagna **esclusivamente con sessioni sintetiche**.

Questo vincolo **cambia il taglio** di `ANALISI_DCE.md` e `COMPRENSIONE_PERSISTENZA_DCS.md`,
che sono scritti dal punto di vista di DCS. Restano validi come analisi, ma vanno letti
diversamente: **tutto ciò che descrivono appartiene all'adapter, non al core.** Questo
documento dice dove passa la linea.

---

## 1. La lezione negativa di DCE

DCE **non ha un core**. Ha un generatore di missioni con dello stato accanto. La prova sta
nella struttura dei dati, non nelle intenzioni:

| Evidenza | Significato |
|---|---|
| `oob_ground` replica **esattamente** `mission.coalition[].country[].<cat>.group[].units[]` del `.miz`, inclusi `route.points[].task`, `payload.pylons`, `callsign`, `livery_id` | Il modello di dominio **è** il formato del simulatore |
| `targetlist[].x`/`.y` sono coordinate mappa DCS | Nessun sistema di riferimento proprio |
| `DC_Weather.lua` scrive direttamente `mission.weather` e sceglie `Preset17` | Il modello meteo **produce** parametri DCS, non stato di dominio |
| `ATO_FlightPlan.lua` genera waypoint nel formato waypoint DCS | Il pianificatore parla la lingua del simulatore |
| DCE **non ha alcun modello di combattimento** | DCS *è* il risolutore. Senza DCS, DCE non produce nulla |

Quest'ultimo punto è decisivo. **DCE non potrebbe mai girare in sessioni sintetiche**, non
per una scelta implementativa ma perché la risoluzione degli ingaggi non esiste nel suo
codice: è delegata interamente al simulatore. Tolto DCS, resta un generatore di file.

Warfare-Model parte da una posizione migliore: `Combat_Power_Estimation`,
`Tactical_Evaluation`, `Tactical_Analysis`, `Strategical_Evaluation` sono l'embrione di un
risolutore proprio. **Quello è il core**; DCE non ne ha l'equivalente.

## 2. Il test di agnosticismo

Un criterio operativo, non filosofico:

> **Se si cancella l'intero adapter DCS, la campagna deve continuare a girare.**
> Se qualcosa si rompe, quel qualcosa era nel posto sbagliato.

Corollari pratici, in ordine di severità:

1. **Nessun import di `lupa`, `zipfile`, `minizip` nel core.** Oggi
   `Code/Persistence/Source/DCS_Data_Management.py` importa `lupa` — è già fuori dal core
   per posizione (`Persistence/`), ma va sancito che `Dynamic_War_Manager/` non lo importi
   mai. *(Nota: `lupa` è in `requirements.txt` ma non installato nel venv — v.
   `ANALISI_DCE.md` §7.1.)*
2. **Nessun identificatore del simulatore nel dominio.** Niente `unitId`, `groupId`,
   `type = "Bf-109K-4"`, `DictKey_*`, `airdromeId`. Il core ha i propri ID; l'adapter tiene
   una tabella di corrispondenza bidirezionale.
3. **Nessuna stringa di tipo del simulatore.** `"MiG-21Bis"` è un identificatore DCS.
   Il core conosce un asset con caratteristiche fisiche; l'adapter lo mappa.
4. **Nessuna unità di misura del simulatore.** Il core fissa le proprie (metri, secondi,
   m/s, kg) e l'adapter converte. La SAM guide è in nmi e ft, DCS in metri: entrambe
   conversioni dell'adapter.
5. **Nessun concetto temporale del simulatore.** `timer.getTime()` è model time DCS. Il core
   ha il proprio tempo di campagna.

## 3. Dove passa la linea, concretamente

```
┌──────────────────────── CORE (puro, testabile senza simulatore) ────────────────────────┐
│                                                                                         │
│  Dominio          Region, Block, Military, Asset, Route, Limes, Threat, Payload          │
│  Stato            CampaignState, Target_Status_History, Actual/Initial_Context           │
│  Catalogo asset   parametri fisici reali (inviluppi, velocità, autonomia, carichi)       │
│  Analisi          Tactical_Analysis, Combat_Power_Estimation, Meteo (modello sinottico)  │
│  Valutazione      Tactical_Evaluation, Strategical_Evaluation                            │
│  Pianificazione   Air_Resources_Assigner, Air/Ground_Route_Manager, C2 a due livelli      │
│  ▶ RISOLUZIONE    SyntheticResolver — risolve una sessione SENZA simulatore              │
│                                                                                         │
│                        ▲                                    │                           │
│                        │  SessionOutcome                    │  SessionOrder             │
└────────────────────────┼────────────────────────────────────┼───────────────────────────┘
                         │          PORTE (contratto)         ▼
        ┌────────────────┴────────────────┬─────────────────────────────────┐
        │  Adapter DCS                    │  Adapter "sintetico"            │
        │  .miz r/w, debrief.log,         │  passa l'ordine al              │
        │  EventsTracker, Hooks,          │  SyntheticResolver del core     │
        │  Warehouse API, mapping ID/tipi │  e ne restituisce l'esito       │
        └─────────────────────────────────┴─────────────────────────────────┘
```

Il punto non ovvio: **l'adapter sintetico è quasi vuoto.** Se il risolutore sta nel core,
l'adapter sintetico è un passacarte. È il segno che la linea è nel posto giusto — e spiega
perché va costruito **per primo**.

## 4. Il contratto delle due porte

È il vero artefatto di progetto. Va definito in termini di dominio, e la disciplina sta nel
**non** farci passare nulla che sappia di DCS.

### 4.1 `SessionOrder` (core → sessione)

Cosa il core chiede di eseguire:

| Elemento | Contenuto | Nota |
|---|---|---|
| Finestra temporale | istante d'inizio, durata | tempo di campagna, non model time |
| Condizioni ambientali | meteo, luce, stato del terreno | dal modello sinottico del core |
| Ordine di battaglia | asset presenti, posizione, stato, dotazione | ID di dominio |
| Compiti assegnati | per ciascun gruppo: missione, rotta, bersaglio, tempistica | in termini di dominio |
| Regole d'ingaggio | dottrina attiva per lato | dal C2 |
| Livello di dettaglio richiesto | quanto deve essere granulare l'esito | v. §4.3 |

### 4.2 `SessionOutcome` (sessione → core)

Cosa la sessione restituisce. **Qui l'analisi del `debrief.log` diventa preziosa**, perché
dice cosa un simulatore reale è in grado di dare — e quindi qual è il tetto massimo utile:

| Elemento | DCS lo fornisce? | Sintetico può produrlo? |
|---|---|---|
| Stato finale di ogni asset (vivo/morto) | **sì**, `world_state.dead` | sì |
| **Danno parziale** | **sì**, `world_state.life` | sì |
| Posizione finale | **sì**, `world_state.x/y/alt/heading` | sì |
| **Carburante e munizioni residue** | **sì**, `world_state.payload` | sì |
| Consumo munizioni per ingaggio | **sì**, `ammo_consumption` | sì |
| Attribuzione degli abbattimenti | **sì**, eventi `kill` + `linked_event_id` | sì |
| Cronologia causale degli ingaggi | **sì**, `shot→hit→kill→score` | **parzialmente** — il sintetico può produrre esiti aggregati, non una cronologia al decimo di secondo |
| Rilevamenti / intelligence acquisita | parzialmente (`Controller.getDetectedTargets` in-mission) | sì |
| Esito dei compiti | parzialmente (`result`, `triggers_state`) | sì |
| Guasti, abbandoni missione IA | **sì**, `failure`, `ai abort mission` | sì, se modellati |

**Principio di progetto che ne ricavo**: il contratto va dimensionato sull'**unione** di ciò
che le due sorgenti sanno produrre, con i campi non universali **opzionali** ed esplicitamente
dichiarati. Un contratto tarato solo sul sintetico butterebbe via metà di quel che DCS
regala; uno tarato solo su DCS renderebbe il percorso sintetico impossibile da soddisfare.

### 4.3 Il campo che rende il contratto praticabile: la fedeltà

Un `SessionOutcome` da sessione sintetica e uno da DCS **non hanno la stessa granularità**, e
fingere il contrario porta a due errori opposti: o il core assume una precisione che non ha,
o spreca quella che ha.

La via pulita è dichiararla: ogni campo dell'esito porta con sé la sua provenienza —
`measured` (il simulatore l'ha osservato), `derived` (calcolato dal risolutore),
`estimated` (stimato con incertezza nota). Il core può così decidere quanto fidarsi.

Warfare-Model ha già un precedente coerente: il lavoro fog-of-war di Fase 2 distingue tra
dato osservato e dato stimato. È lo stesso concetto applicato all'esito di sessione.

## 5. Il risolutore sintetico è il pezzo mancante

Il vincolo "campagna gestibile solo con sessioni sintetiche" si riduce a una domanda:

> Dato un `SessionOrder`, il core sa dire cosa sarebbe successo?

Componenti necessari, quasi tutti già abbozzati:

| Componente | Stato in Warfare-Model |
|---|---|
| Potenza di combattimento per azione | `Combat_Power_Estimation` — **c'è**, con `use_recon` |
| Inviluppi di minaccia e rilevamento | `DataType/Threat`, `Volume`, `air_defense_volume` — **c'è** |
| Rotte e loro esposizione | `Air_Route_Manager` (13 test su threat), `Ground_Route_Manager` — **parziale** |
| Attrito e logistica | `Logistic_Lines`, `Resource_Manager` — **parziale** |
| Meteo come vincolo | `Meteo_Analysis` — **placeholder** |
| **Risoluzione dell'ingaggio** | **assente** |
| **Consumo munizioni/carburante** | **assente** |

Il tassello mancante è la funzione che, dati attaccante, difensore, condizioni e dottrina,
produce perdite, danni e consumi. Non serve che sia sofisticata all'inizio: serve che **esista
e che sia l'unica strada**, così che l'adapter DCS debba conformarsi al suo formato d'uscita
invece che il contrario.

**Ordine di lavoro che ne consegue** — ed è controintuitivo rispetto all'istinto di partire
dall'integrazione:

1. Definire `SessionOrder` / `SessionOutcome` in termini puri di dominio.
2. Scrivere il `SyntheticResolver`, anche rozzo, che soddisfa il contratto.
3. Far girare una campagna intera **senza simulatore**. È il test di agnosticismo di §2.
4. **Solo dopo** scrivere l'adapter DCS, con l'obbligo di produrre lo stesso `SessionOutcome`.

Se si inverte l'ordine — adapter DCS prima — il contratto nascerà modellato su DCS e
l'agnosticismo sarà perso prima ancora di essere tentato. È esattamente ciò che è successo a
DCE.

## 6. Conseguenze sui dati di riferimento appena ingeriti

I documenti in `estratti/` vanno divisi lungo la stessa linea:

| Dato | Natura | Dove va |
|---|---|---|
| Inviluppi SAM (R/H min/max), `acquire_time`, tipo contromisura | **fisica reale** | **core** — catalogo asset |
| `site_layout`, `sead_priority` | **dottrina** | **core** — è conoscenza militare, non del simulatore |
| Anno di servizio, tassonomie (MERAD/SHORAD/LORAD/MANPADS, ruoli) | **reale** | **core** |
| Schede Encyclopedia (pesi, velocità, autonomia, ceiling) | **reale** | **core** |
| `rwr_symbol`, `track_harm`, `search_harm`, `hdsm`, `launch_warning` | **DCS-specifico** | **adapter** |
| Nomi di tipo (`"MiG-21Bis"`), ICAO, frequenze, canali TACAN, beacon | **DCS/teatro-specifico** | **adapter** |
| Cloud preset `Preset1..RainyPreset3` | **DCS-specifico** | **adapter** |

Il caso della SAM guide illustra bene la distinzione: un SA-6 **ha realmente** un inviluppo
0.9–35.6 km e un tempo di acquisizione di 21 s — questo è il core. Che in DCS il suo radar
Straight Flush risponda al codice HARM 108 e compaia come simbolo `6` sull'RWR — questo è
l'adapter.

Nota sulla tassonomia: sia la SAM guide sia il foglio `AAA-SAM` trattano i **radar come asset
distinti**, con anno di servizio e codice propri. Il core dovrebbe fare lo stesso: **un sito
SAM è un gruppo di asset eterogenei** (lanciatori, track radar, search radar, C2), non un
asset singolo. È anche ciò che rende sensato `sead_priority`, e ciò che DCE già fa di fatto
con `targetlist[].elements[]`.

## 7. Nota sulle warehouse

Da chiarimento dell'utente: **DCE non usa le warehouse DCS**. Coerente con l'analisi — DCE si
è costruito `supply_tab` / `airbase_tab` per conto proprio, con la propagazione
`plant → linea → base` e la formula verificata `efficiency = supply × integrity`.

Nell'ottica simulator-agnostic questa **è la scelta giusta**, e per una ragione più forte di
quella storica (nel 2020 l'API non esisteva): **il magazzino è un concetto di dominio.** Una
campagna gestita solo con sessioni sintetiche deve avere una logistica, e non può dipendere
da una struttura dati del simulatore.

Le warehouse DCS (accessibili da scripting dal 2.8.8 — v. `ANALISI_DCE.md` §A.4) diventano
quindi **una proiezione**: l'adapter le scrive in uscita, per rendere visibile al giocatore
dentro DCS lo stato logistico che il core ha calcolato, e le legge in ingresso solo se si
vuole che i consumi avvenuti in sessione retroagiscano sul modello. In nessun caso il core
deve rappresentare la propria logistica come una tabella `warehouses`.

Se e quanto sfruttarle è quindi una decisione di **fedeltà dell'adapter**, non di
architettura. Il core non se ne accorge.

## 8. Punti di attenzione già visibili nel codice

Rilevati passando, non verificati a fondo:

- **Sistema di riferimento**: il core usa `sympy Point2D/Point3D` in un piano cartesiano
  astratto, senza nozione geodetica. Va bene per l'agnosticismo, ma non compone fra teatri e
  ignora la sfericità. Va deciso esplicitamente se resta un piano locale per teatro (allora
  l'adapter possiede la proiezione) o se il core passa a coordinate geodetiche.
- **`Persistence/Source/`** contiene `Coalition.py`, `Country.py`, `Group.py`, `Route.py`,
  `RoutePoint.py`, `Task.py`, `DCS_Mission_Dictionary.py`: sono nomi del **modello DCS**.
  Se è l'adapter, la posizione è giusta ma il nome `Persistence` è fuorviante — sono due
  responsabilità diverse (persistenza dello stato di dominio ≠ traduzione verso DCS), e
  conviene separarle prima che si mescolino.
- **`Context/Coalition.py` e `Persistence/Source/Coalition.py`** coesistono: due `Coalition`
  in due strati. Va chiarito quale è il dominio e quale la rappresentazione DCS.

## 9. Cosa resta valido dei documenti precedenti

| Documento | Come leggerlo ora |
|---|---|
| `ANALISI_DCE.md` §2 (persistenza), §4 (`.miz`), Appendice A | **specifica dell'adapter DCS** |
| `ANALISI_DCE.md` §5.1 (modello meteo sinottico) | **core** — il modello a 5 zone è fisica, non DCS. Solo la traduzione in `clouds.preset` è adapter |
| `ANALISI_DCE.md` §5.2 (`camp_triggers`) | **core** — eventi di campagna |
| `ANALISI_DCE.md` §5.3 (`commander()`, `airDirective`) | **core** — è il livello C2 |
| `ANALISI_DCE.md` §3 (modello dati DCE) | utile come **catalogo di ciò che va rappresentato**, non come schema da imitare |
| `ANALISI_DCE.md` §7.2 (tabella di corrispondenze) | ⚠️ da rileggere con la linea di §3 in mente: diverse corrispondenze che avevo dato sono con strutture DCS, non di dominio |
| `COMPRENSIONE_PERSISTENZA_DCS.md` | interamente **adapter** — ma la §2.3 su `Controller.getDetectedTargets` tocca un concetto di dominio (conoscenza parziale), da portare nel core in forma astratta |
