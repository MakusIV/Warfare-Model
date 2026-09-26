# Analisi: modello Missione/Sessione. Verifica della regola proposta dall'utente

**Stato**: ANALISI (2026-09-26), in attesa delle decisioni dell'utente (§6). Nessun file di codice
modificato, nessun test scritto. Due script di prova in sola lettura sono stati eseguiti fuori dal
repository (§3).
**Oggetto**: verificare se la regola "una sessione = una missione per asset, non ripetuta" è coerente
con il motore DES di sessioni virtuali (`Logic/Session_Simulator.py` e i moduli che chiama), con il
contratto delle porte (`Command/Session_Types.py`), con il design C2 (wiki
`decisions/c2-hierarchy-design.md`) e con i documenti di riferimento del progetto.
**Convenzione**: **[V]** = VERIFICATO leggendo il codice (con `file:riga`) o eseguendolo;
**[I]** = IPOTESI o conoscenza generale non verificata nel repository.

---

## 0. Sintesi: incongruenze e problemi trovati

La regola, nel suo nucleo, **non contraddice il motore: in parte lo descrive già**. Una rotta per
asset per sessione, il riarmo e il pieno solo all'assegnazione del loadout, e il rifornimento
rimandato al ciclo di campagna dopo ogni sessione sono già così nel codice (§2.4). Adottarla come
vincolo di design però mette in luce sette problemi. I primi tre sono architetturali.

| # | Problema | Gravità | Dove (verificato) |
|---|---|---|---|
| **P1** | **La "Missione" non esiste come entità.** Vive solo come tre argomenti di `run_session` (`routes`/`starts`/`speeds`) e **non attraversa la porta** `SessionOrder`. Un adapter DCS oggi non riceverebbe nessuna missione. La regola non ha un contenitore in cui vivere. | architetturale | `Command/Session_Types.py:20-24, 105-110`; `Logic/Session_Simulator.py:454-465` |
| **P2** | **La fine della missione è solo geometrica** (ultimo waypoint della rotta), mai legata allo stato. Nessuno di questi fatti chiude la missione: carburante al minimo (bingo), munizioni finite (winchester), tempo sulla stazione scaduto, bersaglio assegnato distrutto, danno che obbliga ad abortire. La regola ("concludono in base ai parametri della missione") chiede una fine legata allo stato. Il DES però calcola le finestre di contatto **una sola volta, prima** della risoluzione: una fine anticipata richiederebbe il re-scheduling, che è stato rimandato (R4, seconda parte). | architetturale (il conflitto più profondo) | `Logic/Contact_Scheduler.py:1288-1303`; `Logic/Session_Simulator.py:514-517, 550-552`; `Logic/Engagement_Resolver.py:1370-1376` e docstring `:108-110` |
| **P3** | **Nel motore "terminare l'attività" vuol dire sparire.** Un asset con rotta **non esiste** per lo scheduler prima della partenza e dopo l'arrivo. Dopo non può sparare, ma non può nemmeno essere colpito. Per un aereo atterrato significa che gli aerei parcheggiati non sono colpibili da un attacco alla base. Per un'unità terrestre che ha completato un "posizionamento" significa che scompare proprio sull'obiettivo (esperimento E1). La regola deve distinguere **fine della missione** da **presenza fisica**. | architetturale | `Logic/Contact_Scheduler.py:374-384` (docstring `:377-378`), `:617-631`; E1 in §3 |
| **P4** | **Oggi il carburante non vincola nulla e il rifornimento non esiste in nessuna forma.** Il consumo è contabilizzato **a posteriori** (evento MOVEMENT a fine rotta, dopo tutti gli ingaggi) ed è **basato sulla distanza**, non sul tempo. Un asset a secco continua a muoversi e a combattere (E5). Il punto (b), il rifornimento in volo, richiede quindi cose che mancano: un bisogno calcolato sul **tempo** (la regola dice "durata"), un evento di rifornimento nel contratto di uscita, un `FuelEvent` per tratto e non uno per asset, e il tanker come asset con la propria missione. | alta | `Logic/Session_Simulator.py:126-133, 550-552, 588-598`; `Logic/Fuel_Model.py:17-23, 32`; `Asset/Mobile.py:1103-1139, 1141-1231` |
| **P5** | **Durata di sessione unica e missioni che la superano.** La sessione ha un solo orizzonte scalare. Una rotta più lunga viene **tagliata in silenzio** a fine sessione (E4) e la posizione non persiste fra sessioni. Con la regola (e) una missione non può attraversare due sessioni, e le missioni lunghe sono proprio quelle che richiedono rifornimento in volo. In più il numero di sortite per giorno diventa un **artefatto della durata e della cadenza delle sessioni**, perché i tempi di turnaround non sono modellati e il riarmo avviene dopo ogni sessione. | alta | `Logic/Session_Simulator.py:238-257, 313-330`; manuale cap. 10 §9.1 (`10_Limiti_Estensioni_Divergenze.md:102-105`); wiki c2 `:29-32, 42` |
| **P6** | **L'unità "missione" non coincide con l'unità "forza" del motore.** Disingaggio, `committed` e raggruppamento sono **per forza** (`Military`): un sottoinsieme impegnato per forza, e ogni forza al più una volta per sessione. Due missioni dello stesso blocco nella stessa sessione (es. 2 CAP e 4 Strike dello stesso stormo) condividono l'esito DISENGAGED. La regola non dice se la fine della missione è **per asset** (come la rotta) o **per gruppo** (come il disingaggio). | media | `Logic/Session_Simulator.py:283-284, 303-308`; `Logic/Engagement_Resolver.py:44-48, 1095-1108`; `Command/Session_Types.py:99-101` |
| **P7** | **Gli asset senza missione (SAM, difesa statica) ci sono già, ma la regola non li nomina.** Oggi convivono tre stati impliciti: con rotta (presente solo nella propria finestra), fermo e impegnato (presente per tutta la sessione), non impegnato (assente). La formulazione "tutte le singole missioni definite per ogni asset coinvolto" lascia fuori il secondo stato. | bassa (terminologica) | `Logic/Contact_Scheduler.py:1210-1213, 1303`; `Logic/Session_Simulator.py:536-537`; `Logic/Engagement_Resolver.py:1107-1108` |

Problemi minori, emersi verificando P2-P3 (§2.7):

- l'intercettazione di salva è per forza e non controlla la presenza dell'intercettore nel tempo;
- un asset distrutto consuma il carburante dell'intera rotta;
- chi combatte consuma a regime `max` per tutta la rotta;
- una rotta non schedulabile trasforma in silenzio l'asset in un asset fermo per tutta la sessione;
- nessuna rotta di scenario include il rientro alla base (RTB).

**Coerenze confermate** (§2.4, §4): una rotta per asset (nessuna ripetizione possibile per
costruzione); `Aircraft.assigned_loadout` = preparazione della missione (riarmo più pieno); il riarmo
post-sessione del `Theater_Session_Manager`; lo slot `mission_id` già previsto in `Session_Rng` e
nel piano di migrazione di `Campaign_State`; il documento originale dell'utente (sessione = insieme di
missioni); il modello DCE (una sortita per file-missione, `roster.ready`).

---

## 1. La regola, scomposta

| Punto | Enunciato | Tipo |
|---|---|---|
| (a) | Una missione ha una fine definita dai suoi parametri | criterio di fine missione |
| (b) | Il rifornimento **in volo** durante la missione è ammesso e ne fa parte | evento dentro la missione |
| (c) | Il rientro a terra per rifornire è la **fine** della missione corrente, non un'interruzione | criterio di fine missione |
| (d) | Un nuovo rifornimento a terra implica una missione **nuova** per lo stesso asset | confine fra missioni |
| (e) | Una sessione contiene, per ogni asset coinvolto, **una sola** missione, non ripetuta, dentro la finestra della sessione | vincolo di cardinalità e di tempo |

(c) e (d) sono due facce dello stesso confine. (e) è il vincolo che interessa il motore. (a) e (b)
sono quelli che il motore oggi **non** sa esprimere.

---

## 2. Verifiche nel codice (domande 1-7)

### 2.1 Esiste una "Missione" di prima classe? **No** [V]

- `SessionOrder` ha solo `session_id`, `t_start`, `t_end`, `force_ids`, `committed` e
  `salvo_window` (`Command/Session_Types.py:105-110`). Il docstring lo dichiara:
  *"Nessun campo per concetti che il codice non ha ancora: niente missioni strutturate
  aria/terra/mare, rotte assegnate o obiettivi dentro `SessionOrder`"* (`:20-24`).
- Le rotte arrivano come argomenti di `run_session` (`routes`, `starts`, `speeds`,
  `Logic/Session_Simulator.py:454-465`), **fuori** dalla porta. Il contratto "agnostico dal
  simulatore" quindi oggi **non trasporta** la missione. È il primo punto da sistemare se la regola
  diventa vincolo (P1).
- L'RNG ha già lo slot: `SessionOrder.rng(mission_id=None, ...)` (`Command/Session_Types.py:162-164`).
  L'orchestratore lo chiama con `mission_id=None` (`Logic/Session_Simulator.py:566`), con il commento
  *"Quando nascerà `Theater_Session_Manager` con le missioni, qui entrerà l'id di missione"*
  (`:75-77`).
- `Command/Command_Types.py` contiene solo `RegionInfoReport` (`:35-55`). `C2_Manager`,
  `Theater_Session_Manager`, `Session_Mission_Planner` e `Session` **non esistono** (`:4-7`; wiki
  c2 `:72`).
- Nel resto del codice "missione" compare solo in senso di pianificazione:
  `Air_Resources_Assigner` sceglie modello/loadout per un task e conta le sortite
  (`Logic/Air_Resources_Assigner.py:760-790`) ma non muta mai un `Aircraft` e non produce una
  missione eseguibile (commento `Asset/Aircraft.py:161-166`).

**Risposta**: il motore tratta ogni asset come una rotta (o una posizione fissa) più una forza di
appartenenza. Nessun oggetto dice "missione X: asset, compito, bersaglio, parametri di fine".

### 2.2 Durata per asset o durata di sessione globale? **Globale, con una finestra per asset implicita** [V]

- La durata della sessione è **un solo scalare**: `horizon = t_end - t_start`
  (`_session_horizon`, `Logic/Session_Simulator.py:238-257`), passato a
  `schedule_contacts(..., horizon, ...)` (`:515-516`). Gli scenari usano `duration=3_600.0`
  (`Test/Scenario_Fixtures.py:751`, e S2 `Test/Test_Session_Scenarios.py:182, 197`).
- **Esiste però già una finestra per asset, implicita**: per un asset con rotta i tratti coprono
  `[starts[id], starts[id] + durata della rotta] ∩ [t0, t0 + horizon]`
  (`Logic/Contact_Scheduler.py:1288-1298`, `clamp_legs :348-371`). Lo `legs_span` di quell'intervallo
  è *"l'intervallo fuori dal quale l'asset **non esiste** per lo scheduler: non c'è prima di
  partire e non c'è dopo essere arrivato"* (`:374-384`). Ogni contatto è ritagliato alla
  sovrapposizione degli span (`_overlap :617-631`, usata da `range_intervals :772-777`).
- Quindi **sì**, un asset può "finire" prima della sessione: basta che la sua rotta finisca prima.
  Questa fine però è decisa **solo dalla geometria della rotta pianificata**, non dai parametri della
  missione (P2), e la conseguenza è la **scomparsa** dell'asset (P3).

**Risposta**: per la sola parte temporale la regola non richiede un cambio di architettura: la
finestra per asset c'è già. Lo richiede per due ragioni, che sono il vero cambiamento:
1. la finestra dovrebbe essere portata da una `Mission` dentro `SessionOrder` (P1);
2. la fine dovrebbe dipendere dallo **stato** (carburante, munizioni, danni, obiettivo) e non solo
   dalla geometria (P2). Con finestre di contatto calcolate prima della risoluzione
   (`Logic/Session_Simulator.py:514-517`, poi coda eventi `:540-598`), questo è possibile solo in
   due modi. (i) Criteri di fine calcolabili **prima** della sessione: tempo sulla stazione e bingo
   carburante si possono calcolare a priori sulla rotta, e basta accorciarla. (ii) Il
   re-scheduling rimandato (R4, seconda parte, `Logic/Engagement_Resolver.py:108-110`), necessario
   per winchester, bersaglio distrutto o abort per danni, che dipendono dall'esito della sessione
   stessa.

### 2.3 Rifornimento in volo o rientro a base? **Nessuno dei due è modellato** [V]

- `Fuel_Model`: *"Non rifornisce: il rifornimento è materia del ciclo di campagna"*
  (`Logic/Fuel_Model.py:32`). `consume_fuel` rifiuta quantità negative (*"no refuelling here"*,
  `Asset/Mobile.py:1118-1119`), e il setter `fuel` *"non è un canale di rifornimento"* (`:1079-1096`).
  L'unico "rifornimento" esistente è implicito: `Aircraft.assigned_loadout` rimette il pieno quando
  si (ri)assegna un loadout (`Asset/Aircraft.py:208-211`; commento `Asset/Mobile.py:219-221`).
- Il carburante è un **vincolo a posteriori, non di esecuzione**. È consumato da **un** `FuelEvent`
  per asset, all'istante di fine movimento (`Logic/Session_Simulator.py:550-552`), estratto **dopo**
  tutti gli ingaggi che coinvolgono l'asset (docstring `:32-35`). Se si esaurisce a metà, *"l'asset
  NON viene fermato sulla rotta e i contatti già calcolati non vengono ricalcolati"* (`:126-130`,
  codice `:595-598`, solo un log). Esperimento E5: un carro rimasto a secco dopo 852 m di 7000
  viene comunque ingaggiato 3 km più avanti.
- Il consumo è **basato sulla distanza**: `fuel_for_distance = distance / fuel_autonomy`
  (`Asset/Mobile.py:1203-1231`), con l'autonomia dell'aereo = 2 × raggio d'azione del loadout
  (`Asset/Aircraft.py:39-45, 284-320`). Non c'è consumo nel tempo. Un asset **senza rotta** non
  produce `FuelEvent` (`Logic/Session_Simulator.py:133`), quindi una CAP modellata come posizione
  fissa non consuma mai. Una rotta non può contenere soste o attese: il tempo di un arco è solo
  `lunghezza / velocità` (`DataType/Edge.py:192-199`) e `Waypoint` non ha campi di tempo
  (`DataType/Waypoint.py:12-18`). Un'orbita di attesa si può rappresentare solo come circuito
  geometrico.
- Dati per il rifornimento in volo: **parziali**.
  - Lato fornitore sì: i loadout tanker esistono (`Asset/Aircraft_Loadouts.py:2227-2252, 2497-2514`),
    e il terzo campo dei pod `boom_refueling`/`buddy_refueling_pod`/`hose_drogue_pod` è il
    *"carburante CEDIBILE ad altri velivoli"*, oggi escluso dall'autonomia
    (`Asset/Aircraft.py:48-55, 364-368`).
  - Lato ricevente no: nessun flag "può ricevere rifornimento in volo" e nessun supporto tanker fra
    i `mandatory_support` dei loadout, che sono solo `Escort`, `SEAD`, `Escort_Jammer`,
    `Flare_Illumination`, `Laser_Illumination` (conteggio su tutto `Aircraft_Loadouts.py`, es.
    `:66-69`).

**Risposta**: nessuna distinzione, perché nessuna delle due azioni esiste. Per il punto (c), la
fine per rientro, basterebbe accorciare la rotta in pianificazione (§2.2, modo i). Il punto (b) è
un'**estensione vera** del modello, non una regola da dichiarare:
- un evento `RefuelEvent` nel `SessionOutcome` (cambio di contratto);
- `FuelEvent` spezzato in tratti fra un rifornimento e l'altro (oggi uno solo per asset, già
  "limitato al disponibile", `Logic/Fuel_Model.py:20-23`: con un rifornimento a metà segnerebbe
  un falso esaurimento);
- il tanker come asset con la propria missione, abbattibile. Se muore, il rifornimento fallisce e
  la missione ricevente deve finire prima: caso non coperto dalla regola;
- un bisogno di rifornimento espresso nel tempo, mentre il modello attuale è in distanza.

### 2.4 Munizioni e "missione unica": la parte già coerente e la parte che manca [V]

**Già coerente con la regola:**
- `assigned_loadout.setter`: *"Assegnare un loadout equivale ad armare il velivolo per la
  missione ... un'operazione del ciclo di campagna/assemblaggio missione, non un canale di
  rifornimento durante l'ingaggio (il risolutore non la chiama mai)"* (`Asset/Aircraft.py:177-181`),
  e rimette anche il pieno (`:208-211`). È esattamente il punto (d): **preparazione a terra = nuova
  missione**.
- **Nessuna ripetizione possibile per costruzione**: `routes` è una mappa `{asset_id: Route}`
  (`Logic/Session_Simulator.py:457, 319`; `Logic/Contact_Scheduler.py:1291`), quindi una sola rotta
  per asset per sessione. Una forza compare al più una volta (`Logic/Session_Simulator.py:283-284`).
  Le componenti di ingaggio sono disgiunte e ognuna è risolta una sola volta (`counter=0`, `:82-84`,
  `:561-573`). Una seconda sortita "con sosta a terra" non è nemmeno rappresentabile in una `Route`,
  perché mancano i tempi di sosta (§2.3).
- Il `Theater_Session_Manager` progettato **riarma dopo ogni sessione** (wiki c2 `:42`), cioè fra
  una sessione e l'altra, non dentro: coerente con (c) e (d).

**Manca: il criterio di fine missione.** L'asset continua a partecipare finché valgono tutte e tre
queste condizioni:
1. la sua rotta è in corso (span dei tratti);
2. è operativo e la sua forza non ha rotto il contatto;
3. ha munizioni.

Le tre condizioni di stop del tiratore sono `Logic/Engagement_Resolver.py:1372-1376` (forza rotta,
non operativo, munizioni ≤ 0), più la fine della finestra (`:1400-1402`, `:1514-1520`). Con munizioni
a zero l'asset *"non spara più ma resta un bersaglio valido"* (`Asset/Mobile.py:98`) **e continua la
rotta**: il winchester non lo fa rientrare. Non esiste nemmeno un **bersaglio assegnato**:
`fire_control` è **una sola** callable per l'intera sessione (`Logic/Session_Simulator.py:101-107`) e
ogni nemico rilevato in finestra è un candidato. Uno Strike attacca qualunque bersaglio che le sue
armi possano colpire, non solo il proprio, e "missione conclusa perché il bersaglio è distrutto" non
è esprimibile. Per una **CAP** ha senso, perché il suo bersaglio è "chiunque entri"; per uno
**Strike** no.

**Risposta**: il motore **non** ha un criterio di fine missione. L'asset resta nello scheduler fino
alla fine della sua rotta, o della sessione se è fermo, qualunque cosa avrebbe fatto la sua missione.
L'unica "fine anticipata" esistente è il **DISENGAGED** per forza, che non ferma la rotta (nessun
re-scheduling, manuale cap. 10 §D1).

### 2.5 Asset statici e difensivi [V]

- Un asset senza rotta è **fermo per tutta la sessione** (`static_legs`,
  `Logic/Contact_Scheduler.py:324-345, 1303`; stesso trattamento nell'orchestratore,
  `Logic/Session_Simulator.py:536-537`). Il docstring lo motiva: *"il caso più comune in campagna
  — un sito SAM, un deposito, una base"* (`Logic/Contact_Scheduler.py:1210-1213`).
- La convivenza fra asset con una fine (rotta) e asset continui (fermi) **esiste già** ed è lo
  scenario standard: S1 ha forze Blue in movimento contro una linea Red ferma
  (`Test/Scenario_Fixtures.py:708-751`).
- C'è anche un terzo stato: gli asset **non impegnati** (`committed`) di una forza sono esclusi dallo
  stato ombra (`Logic/Engagement_Resolver.py:1095-1108`). Non sparano e non sono bersagli, anche
  se lo scheduler ha calcolato le loro finestre (`_operative_assets` ignora `committed`,
  `Logic/Contact_Scheduler.py:1277-1285`).

**Risposta**: la regola ha senso solo per gli asset **con un compito e una rotta**: aerei, e anche
mezzi terrestri e navi in movimento. Per un SAM in difesa statica serve una **postura continua**, che
il motore ha già (fermo per tutta la sessione). Non è un cambiamento: va scritto nella regola (P7).
Da decidere se una postura difensiva abbia a sua volta una "fine", per esempio un SAM che esaurisce i
missili. Oggi resta bersaglio fino a fine sessione, coerentemente con `Asset/Mobile.py:98`.

### 2.6 Compatibilità col design C2 e con l'orizzonte delle sessioni [V + I]

Cosa dice il design (wiki `decisions/c2-hierarchy-design.md`) [V]:
- cadenza di 6 sessioni virtuali fra due sessioni DCS (`:29`) e scarto di 1-2 ore fra sessioni DCS
  e virtuali (`:30`);
- stato aggiornato dopo **ogni** sessione, con perdite, consumi e riarmo, prima di pianificare la
  successiva (`:32, 42`);
- `mission_id` riusato **sotto** `session_id` (`:46`);
- dalla memoria di progetto: al termine della sessione DCS la campagna *"chiede se terminare
  anticipatamente altre missioni previste per quel game-day"* (`project_c2_hierarchy_design.md:46`).

**La durata di una sessione non è mai stata fissata** [V]. "1-2 h" è lo **scarto** fra sessioni, non
la durata. L'unico numero di durata è l'ipotesi di dimensionamento "Sessione di 2 h"
(`Architettura_esecuzione_sessioni_virtuali_ANALISI.md:111`) e i 3600 s delle fixture.

Conseguenze della regola:
1. **Una sortita per asset per sessione** [V, per costruzione]: un aereo non può fare due sortite
   nella stessa sessione anche se il tempo lo permetterebbe. Deve aspettare la sessione successiva,
   che è **anche** l'unico punto in cui oggi avviene il riarmo (TSM, wiki c2 `:42`). Non è un
   conflitto: è coerente con il riarmo post-sessione già deciso.
2. **Il numero di sortite diventa un artefatto della cadenza** [I]. Nessun tempo di turnaround o di
   manutenzione è modellato. Se il riarmo post-sessione rende l'aereo di nuovo "pronto" alla
   sessione successiva, il massimo di sortite per game-day è uguale al numero di sessioni nel
   game-day, qualunque sia la durata reale delle missioni. Con sessioni frequenti è ottimistico (un
   caccia fa realisticamente 1-3 sortite al giorno [I]); con sessioni lunghe e missioni brevi è
   pessimistico (aereo fermo per il resto della sessione). Il DCE risolve con un pool
   `roster.ready/damaged/lost` per squadrone (`documentazione_dcs/ANALISI_DCE.md:597-607`), non
   con la sola cadenza.
3. **Missioni più lunghe della sessione** [V]. Oggi sono tagliate a fine sessione (E4: rotta di
   200 km, consumo contabilizzato solo per 36 km) e la posizione non persiste
   (`10_Limiti_Estensioni_Divergenze.md:102-105`, `Test/Test_Session_Validation.py:257-261`). La
   regola (e), "dentro il periodo della sessione", impone quindi **una durata di sessione ≥ la
   missione più lunga pianificata**, oppure missioni che attraversano più sessioni, cosa che la
   regola esclude. Il rifornimento in volo (b) serve proprio alle missioni lunghe: è il caso più
   esposto.
4. **Sovrapposizione temporale fra sessioni** [I]. Se una sessione DCS e la virtuale successiva sono
   sfalsate di 1-2 h ma durano di più, i loro "periodi di interesse" si sovrappongono sull'orologio
   di campagna. Un asset in missione nella prima dovrebbe essere escluso dalla seconda. Il design
   non dice se le sessioni siano finestre disgiunte dell'orologio di campagna: la regola ha bisogno
   di questa risposta.

### 2.7 Problemi minori trovati durante la verifica [V]

- **Intercettazione senza presenza**: la capacità di intercettazione di salva è della **forza**
  (`Logic/Engagement_Resolver.py:1182-1200, 1559-1570`). Nessun controllo che l'intercettore (un
  `Vehicle`/`Ship` AD, `Block/Military.py:618-648`) sia dentro il proprio span di rotta al momento
  dell'impatto. Un SAM mobile che ha "concluso" la sua rotta protegge ancora la forza.
- **Relitti che consumano**: un asset distrutto consuma il carburante dell'intera rotta
  (`Logic/Session_Simulator.py:131-132`). Con la regola la sua missione è finita all'abbattimento.
- **Regime pessimistico**: chi ha combattuto consuma a regime `max` per **tutta** la rotta
  (`Logic/Session_Simulator.py:116-124, 588`).
- **Fallback silenzioso**: una rotta non schedulabile (velocità indefinita) trasforma l'asset in
  **fermo per tutta la sessione** (`Logic/Contact_Scheduler.py:1300-1303`). Per un aereo significa
  restare "sospeso" alla quota di partenza, senza consumo e senza fine missione.
- **Nessun rientro alla base (RTB) negli scenari**: le rotte degli scenari finiscono sull'obiettivo
  o oltre. Esempio: la CAS di S1 va da -60 km a +10 km e lì la rotta termina
  (`Test/Scenario_Fixtures.py:747`). La tratta di rientro, che secondo la regola è parte della
  missione fino all'atterraggio, oggi non è né volata né consumata.

---

## 3. Esperimenti di sola lettura

Due script nella scratchpad di sessione, fuori dal repository, con le fixture di
`Test/Scenario_Fixtures.py`. M1A2 Blue contro BMP-2 Red fermo in (0, 0), sensori 'ground' da 5 km,
sessione di 3600 s.

| # | Configurazione | Risultato | Cosa dimostra |
|---|---|---|---|
| E1 | Blue si muove da -6 km a -4 km (200 s) e **si ferma a 4 km** da Red | finestra di contatto `[100, 200]` | a fine rotta l'asset **sparisce**, pur restando fisicamente a 4 km dal nemico per altri 3400 s (P3) |
| E2 | Stesso Blue **fermo** a -4 km, senza rotta | finestra `[0, 3600]` | un asset senza rotta è presente per tutta la sessione (P7) |
| E3 | E1 con `starts=1000` | finestra `[1100, 1200]` | prima della partenza l'asset non esiste |
| E4 | Rotta di 200 km (fine a 20000 s) in una sessione di 3600 s | un `FuelEvent` a t=3600 per 36 km | taglio silenzioso della missione a fine sessione (P5) |
| E5 | Carro con `fuel=0.002` (≈ 852 m di autonomia) su rotta di 7 km | `FuelEvent` con `exhausted=True` e `distance_covered=852`. Red spara a t=370 s e distrugge Blue, che secondo il carburante sarebbe fermo a ~7,1 km, **fuori** dal raggio di 5 km | il carburante non vincola il movimento né i contatti (P4) |

---

## 4. Coerenza della regola con i documenti di riferimento

- **Documento originale dell'utente** (`Architettura_esecuzione_sessioni_virtuali.txt:3-11`) [V]:
  *"Una sessione virtuale è costituita dall'esecuzione di diverse missioni singole e/o
  operazioni"*. La missione usa asset di **un** blocco e segue una `Route`, e l'operazione
  raggruppa missioni di blocchi diversi. La regola è coerente, ma **non nomina le operazioni**: la
  "fine" di un'operazione (insieme di missioni) resta da definire.
- **DCE** [V]: una sortita per volo per file-missione, disponibilità tenuta dal pool
  `roster.ready` (`documentazione_dcs/ANALISI_DCE.md:597-607`). Le tracce tanker sono bersagli
  "virtuali" di un task separato (`:751-756`): il rifornimento in volo è **una missione del tanker**,
  a cui quella ricevente si appoggia. È un argomento a favore del modellare il tanker come
  dipendenza (§2.3).
- **DCS** [I, conoscenza generale non verificata nel repository]: un gruppo AI ha un solo piano di
  volo; dopo RTB e atterraggio resta fermo, salvo script di respawn. La regola coincide quindi con la
  semantica nativa dell'esecutore DCS. È un buon motivo per farne parte del **contratto della
  porta**, a cui devono conformarsi entrambi gli esecutori (vincolo simulator-agnostic).
- **Persistenza** [V]: rinomina `mission_id` → `session_id` con `mission_id` un livello sotto
  (wiki c2 `:46`). La regola ne fornisce la semantica.

---

## 5. Ambiguità della regola e casi limite (domanda 7)

Per ciascun caso: cosa fa **oggi** il motore [V] e cosa la regola dovrebbe dire.

| Caso | Oggi nel motore | Cosa la regola non dice |
|---|---|---|
| **Abbattuto a metà missione** | Non operativo: smette di sparare e non è più bersaglio (`Engagement_Resolver.py:1375, 1389-1393`). Consuma comunque tutta la rotta (`Session_Simulator.py:131-132`) | La missione è "conclusa" o "fallita"? Serve un esito di missione distinto (COMPLETATA / ABORTITA / PERSA) per le statistiche C2 e per `success_ratio` (`DataType/State.py:54-56`) |
| **Abort per danni, senza bisogno di carburante** | "Mission kill" (salute < 50%, non operativo): smette di combattere ma **segue la rotta originale**, senza rientro | Rientra "a fine missione" per la via più breve (nuova rotta = re-scheduling) o prosegue? L'abort è per asset o trascina il gruppo? |
| **Winchester** (munizioni finite) | Continua la rotta, resta bersaglio (`Mobile.py:98`) | Lo scarico delle munizioni è un parametro di fine missione? Per la CAP sì, per lo Strike dipende dal bersaglio |
| **Bersagli di una CAP eliminati in tempi diversi** | Nessun bersaglio assegnato; ogni asset ha la propria rotta e quindi la **propria** fine | La fine è per asset (il primo a finire torna da solo) o per gruppo (tutti tornano insieme, all'ultimo)? In volo la dottrina tiene la coppia insieme [I] |
| **Disingaggio di una forza con due missioni** | DISENGAGED per **forza**: vale per entrambe (`Engagement_Resolver.py:44-48`) | La rottura del contatto è della missione o del blocco? (P6) |
| **Missione più lunga della sessione** | Tagliata in silenzio (E4) | Vietata (validazione in pianificazione) o spezzata su più sessioni (contro la regola (e))? |
| **Atterraggio su una base diversa** (divert, FARP avanzata) | La posizione non persiste fra sessioni: nella sessione successiva l'asset riparte dalla posizione iniziale | La missione successiva parte dalla base d'arrivo: serve la persistenza della posizione |
| **Tanker abbattuto prima del rifornimento** | Non modellato | Il ricevente deve concludere prima (rientro): è un abort, non una fine per parametri |
| **Mezzi terrestri e navi** | Nessun rifornimento | Il "rifornimento a terra" di un reparto avviene sul campo, da colonne logistiche, non "alla base"; per le navi è il RAS in navigazione. Sono l'analogo terrestre/navale del rifornimento in volo (dentro la missione) o del rientro a base (fine)? La regola è scritta per gli aerei |
| **Asset impegnato ma senza rotta** (difesa) | Presente e attivo per tutta la sessione | Va dichiarato come "postura continua", non missione (P7) |
| **Asset a fine missione (atterrato, arrivato)** | **Sparisce** (E1) | "Terminare l'attività" ≠ sparire: l'asset resta un bersaglio e può difendersi (P3) |
| **Missione conclusa prima dell'inizio dell'ingaggio che l'avrebbe coinvolta** | Coerente: fuori dallo span nessuna finestra | Nessuna ambiguità |

---

## 6. Proposta di riformulazione e decisioni richieste all'utente

Riformulazione suggerita (da confermare):

> Una **Sessione** è una finestra `[t_start, t_end]` dell'orologio di campagna. Contiene, per ogni
> asset coinvolto, **al più una** Missione, oppure una **postura continua** (difesa statica, sito,
> deposito) valida per tutta la finestra. Una Missione ha un inizio (decollo/partenza) e una fine
> (atterraggio/arrivo, oppure abort o perdita) entrambi **dentro** la finestra. Il rifornimento in
> volo (o in movimento, per mezzi terrestri e navali) è un evento **interno** alla missione, che
> dipende dalla missione del rifornitore. Il rientro alla base per rifornire, riarmare o riparare è
> la **fine** della missione. Una nuova preparazione a terra (loadout, pieno) apre una missione
> nuova, **mai nella stessa sessione**. A fine missione l'asset **smette di agire ma resta presente**
> nella sua posizione finale (bersaglio valido fino alla fine della sessione).

Decisioni richieste, in ordine di blocco:

1. **Presenza a fine missione (P3)**: a fine missione l'asset resta presente come bersaglio fermo
   (atterrato, parcheggiato, attestato) oppure sparisce come oggi? È una modifica di
   `Contact_Scheduler._asset_legs`: il tratto fermo dopo l'ultimo waypoint fino a fine sessione, e
   forse anche prima della partenza.
2. **Criteri di fine missione (P2)**: quali sono ammessi? Quelli calcolabili **prima** della sessione
   (tempo sulla stazione, bingo carburante sulla rotta pianificata, orario di rientro) non
   richiedono re-scheduling. Quelli legati all'esito (winchester, bersaglio distrutto, abort per
   danni) richiedono la R4 seconda parte, oggi rimandata.
3. **Unità della missione (P6)**: la fine e l'abort sono per asset o per gruppo? Una missione è un
   sottoinsieme di una forza (e allora `committed` deve diventare "per missione" e il disingaggio
   "per missione"), oppure una forza è sempre una sola missione?
4. **Durata e sovrapposizione delle sessioni (P5)**: le sessioni sono finestre disgiunte
   dell'orologio di campagna? Qual è la durata di riferimento di una sessione virtuale? Una missione
   pianificata più lunga della sessione va rifiutata in pianificazione?
5. **Rifornimento in volo (P4)**: va modellato ora, cioè con evento di rifornimento, tanker come
   dipendenza e consumo nel tempo, oppure si accetta la regola solo come vincolo di pianificazione
   (missioni che non ne hanno bisogno) rimandandolo?
6. **Turnaround e numero di sortite (§2.6 punto 2)**: la disponibilità fra sessioni è decisa dalla
   sola cadenza delle sessioni o da un pool di prontezza con tempi di turnaround, come
   `roster.ready` del DCE?

---

## 7. Impatto se la regola viene adottata (mappa, non implementazione)

| Componente | Cambiamento implicato |
|---|---|
| `Command/Session_Types.py` | Nuovo tipo `Mission` (id, asset, compito, rotta, partenza, parametri di fine, dipendenze come il tanker) dentro `SessionOrder`, al posto di `routes`/`starts`/`speeds` fuori porta; esito di missione nel `SessionOutcome`; eventuale `RefuelEvent` |
| `Logic/Session_Simulator.py` | `mission_id` reale nell'RNG (`:566`); fine missione anticipata calcolata prima della sessione; `FuelEvent` per tratto |
| `Logic/Contact_Scheduler.py` | Presenza dopo l'arrivo e prima della partenza (decisione 1) |
| `Logic/Engagement_Resolver.py` | Disingaggio e `committed` per missione (decisione 3); re-scheduling (decisione 2, R4 seconda parte) |
| `Logic/Fuel_Model.py`, `Asset/Mobile.py` | Consumo nel tempo (attesa/orbita), rifornimento come evento (oggi vietato da `consume_fuel` e dal setter) |
| `Asset/Aircraft_Loadouts.py` / `Aircraft_Data.py` | Capacità di ricevere rifornimento in volo; `mandatory_support` con il tanker |
| Futuri `Theater_Session_Manager` / `Session_Mission_Planner` | Validazione "una missione per asset per sessione" e "missione dentro la finestra", pool di prontezza |
| `Context/Campaign_State.py` | Migrazione `mission_id` → `session_id` con `mission_id` sotto (già decisa, wiki c2 `:46`) |
