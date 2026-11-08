# Ricerca dati — Passata 2, lotto D4: tempo di scoperta visiva e sensori ottici

> Bozza di ricerca (`oc-researcher`). **Non e' una decisione di progetto**: riporta i valori trovati, la fonte,
> l'estratto letterale e la confidenza. Le scelte di valore spettano all'utente. Il file e' aggiornato man mano.
> Complemento di `Analysis/Document/Ricerca_Dwell_Sensori_2026_11_06.md` (prima ricerca) e di
> `Ricerca_Sensore_Visivo_ZSU57_M163_2026_10_29.md`.

## 0. Definizioni, scala, convenzioni

- **Oggetto**: per gli osservatori umani (registro `visual` o mirini ottici/TVD) il DES vuole usare un
  `dwell_time_s` come *approssimazione* del tempo di scoperta/aggiornamento. Non e' un periodo di rotazione:
  l'occhio non scandisce con un giro meccanico costante.
- **Tipo di dato (T)**: **F** = valore di fonte; **D** = dedotto con calcolo mostrato; **S** = stima mia
  dichiarata. "non trovato" = cercato e non reperito (esito valido).
- **Confidenza**: **A** = fonte tecnica primaria (rapporto tecnico ufficiale) o due fonti secondarie
  indipendenti concordi; **M** = una fonte secondaria seria; **B** = stima, forum, gioco, mirror, frammento di
  ricerca non verificato.
- **Categorie di applicabilita'** (riprese dalla prima ricerca): **A** rotazione meccanica 360°; **B** settore
  o fascio elettronico; **C** inseguimento continuo (dwell non applicabile); **D** ottico/occhio nudo (dwell non
  applicabile come periodo di rivisita; la domanda e' il *tempo di scoperta*).
- **Unita'**: ogni valore e' marcato come **TEMPO (s)**, **FREQUENZA (glimpse/s)** o **PROBABILITA'**.
- **Nota sulle citazioni OCR**: le pagine DTIC sono OCR grezzo con spazi multipli; nelle citazioni qui sotto
  gli spazi multipli sono ridotti a uno, **le parole sono quelle del testo** (nessun'altra normalizzazione).
- **Varianti cercate nel registro** (`Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py`): `ZSU-57-2`
  (riga 3703, 1957, URSS), `M163-VADS` (3825, 1969, USA), `Strela-1-9P31` (4007, 1968, URSS),
  `MIM-72G-Chaparral` (4065, 1969/1998, USA), `9K35-Strela-10` (4181, 1976, URSS), `M6-Linebacker`
  (4355, 1997, USA). I primi due hanno solo `visual`; gli altri quattro hanno `TVD`.

## 1. Tabella riassuntiva

| Voce | Sensore / variante cercata | Tipo di scansione | rpm / periodo (estremi) | Regime normale? | Applicabilita' | Rispetto alla prima ricerca | Conf. |
|---|---|---|---|---|---|---|---|
| **Osservatori a terra, settore 30°/60°/120°** (Poe 1974, test AMTOC-1) | occhio nudo, scansione sistematica a passate | passate orizzontali "avanti e indietro" nel settore | **passata completa 2,72 s (30°), 2,99 s (60°), 3,94 s (120°)**; intervallo per passata 1,75-6,00 s (F) | n/a | **D** (non e' rotazione) | **aggiunge** (rapporto DTIC letto per la prima volta) | **A** |
| **"Glimpse" dell'osservatore** (Poe 1974) | occhio nudo | colpi d'occhio indipendenti | **~3 al secondo** (FREQUENZA); **durata media ~0,28 s** (TEMPO); 0,04-0,79 s secondo gli studi (TEMPO) | n/a | **D** | **conferma e aggiunge** numeri alla prima ricerca (che aveva solo snippet Koopman) | **A** |
| **Osservatori contro elicotteri, 1-5 km** (ADA025823) | occhio nudo, settore, posizione di tiro | osservazione continua di un settore | **mediana del tempo alla prima scoperta ~65 s**, con tempi censurati a **60±5 s** (TEMPO) | n/a (esposizione ~60±5 s) | **D** | **aggiunge** | **A** (valore) |
| **Osservatori contro jet, settore 180°, terreno collinoso** (ADA020657) | occhio nudo | 16 osservatori per prova, settore 180° | tempi di scoperta registrati; **valore medio/mediano non estratto**; il rapporto dice che le analisi "yielded little in the way of positive results" | n/a | **D** | **aggiunge** (metodo; valore non trovato) | **A** (metodo) / valore non trovato |
| **Koopman: modello a glimpse** | occhio nudo | glimpse indipendenti, legge cumulativa | **glimpse standardizzato a 1/3-1 s** (TEMPO) per la soglia di contrasto; nessun rpm | n/a | **D** | **conferma** (forma esponenziale/cumulativa) | **B-M** |
| **ZSU-57-2** (`visual`, equipaggio) | occhio nudo + mirino a riflessione | n/a | **non applicabile come rpm**; tempo di scoperta **non trovato** | - | **D** | **conferma** | - |
| **M163-VADS** (`visual` + AN/VPS-2 solo distanza) | occhio nudo del puntatore | n/a | **non applicabile come rpm**; tempo di scoperta **non trovato** | - | **D** | **conferma** | - |
| **Strela-1-9P31** (`TVD` mirino ottico) | mirino ottico | n/a | tempo di acquisizione **non trovato** | - | **D** | **conferma** | - |
| **MIM-72G-Chaparral** (`TVD` FLIR) | FLIR | n/a | tempo di acquisizione **non trovato** | - | **D** | **conferma** | - |
| **9K35-Strela-10** (`TVD` ottico-IR) | mirino ottico/IR + telemetro | n/a | tempo di acquisizione **non trovato**; "receiving target designations 3-5 s" e' un'altra grandezza (**B**) | - | **D** | **aggiunge** (chiarimento su cosa NON e' acquisizione) | **B** |
| **M6-Linebacker** (`TVD` FLIR + cueing radar) | FLIR, cueing AN/MPQ-64 | n/a | tempo di acquisizione **non trovato**; lo slew-to-cue "reducing target acquisition time" e' solo qualitativo (**B**) | - | **D** | **conferma** | **B** |

## 2. Valori, fonti, estratti

### 2.1 Poe (1974), ADA017599 — modello di scoperta visiva di aerei da osservatori a terra

Rapporto tecnico primario dell'esercito USA, **letto in parte** (prime ~20 pagine del testo OCR) e
**interrogato con la ricerca full-text** tramite la copia su Internet Archive (la prima ricerca lo dava
403/non letto). Riferimento: `Technical Report RD-75-30`, ottobre 1974.

- **Frequenza dei colpi d'occhio (glimpse)**: **~3 al secondo**. Tipo: **FREQUENZA**.
  URL: `https://archive.org/stream/DTIC_ADA017599/DTIC_ADA017599_djvu.txt`
  Estratto: *"Average glimpse rate is in the neighborhood of 3/sec."* — conf. **A** (T=F).
  E' una frequenza, **non** un periodo di aggiornamento: il suo inverso (~0,33 s) e' l'intervallo medio fra
  due colpi d'occhio, non il tempo per riscoprire lo stesso punto del settore.
- **Durata media del colpo d'occhio**: **~0,28 s** (e ~85% del tempo di ricerca e' passato a "glimpse").
  Tipo: **TEMPO**.
  Stesso URL. Estratto: *"Perhaps 85% of the search time is spent actually glimpsing, the rest in jumps
  between fixations. Actual average glimpse times are on the order of 0.28 sec."* — conf. **A** (T=F).
- **Durata delle fissazioni secondo gli studi citati** (dati di letteratura riportati dal rapporto):
  - Cobb e Moss: *"a range of 0.071 to 0.25 sec and a mean of 0.15 sec"*.
  - Leibowitz e Bourne: *"a mode of 0.30 sec and a mean of 0.48 sec"*.
  - Ford, White e Lichtenstein: *"The mean fixation duration was 0.23 sec (with a range of 0.04 to 0.60 sec)."*
  - White e Ford (PPI radar): *"mean 0.37 sec, median 0.36 sec, and range 0.11 to 0.79 sec"*.
  - Sugarman, Hammill e Deutschman: *"the observer shifted his gaze 171 times in 57 seconds, giving an
    effective average glimpse time of 0.33 sec."*
  Tutte **TEMPO**, conf. **A** (riportate da rapporto primario, che a sua volta cita gli studi).
- **Durata di una passata completa del settore** (Tabella 2, "OCULAR ACTIVITY DURING SEARCH OF THE SKY"):
  settore **30°**: media **2,72 s**, intervallo **1,75-4,50 s**, 8,16 glimpse per passata;
  settore **60°**: media **2,99 s**, intervallo **2,00-4,75 s**, 8,97 glimpse;
  settore **120°**: media **3,94 s**, intervallo **2,50-6,00 s**, 11,82 glimpse.
  Tipo: **TEMPO** per passata. Stesso URL (Tabella 2). Estratto: *"Average Duration 2.72 sec 2.99 sec
  3.94 sec"* (riga di tabella). — conf. **A** (T=F).
  **Questo e' il valore piu' vicino a un "periodo di aggiornamento" dell'osservatore**: il tempo per
  ripassare tutto il settore assegnato (non un punto).
- **Legge cumulativa di scoperta** (forma del modello): la probabilita' cumulata si aggiorna a ogni glimpse
  con la ricorrenza `P_cum,t = P_cum,t-1 + (1 - P_cum,t-1) * Pg` (**D**, ricostruita dalla frase sotto),
  con passo di simulazione **1/3 s**.
  Tipo: **PROBABILITA'** (non tempo). Stesso URL. Estratto: *"Every 1/3 sec the model calculates a glimpse
  probability, Pg, for each observer."* — conf. **A** (T=F). Estratto (OCR): *"This glimpse probability is
  cumulated for each observer according to the formula"*.
- **Esempio numerico di probabilita' cumulata**: dopo **30 glimpse (10 s)** con rapporto di contrasto
  costante 0,2, la probabilita' cumulata va da **0,13 a 0,94** secondo la deviazione standard assunta.
  Tipo: **PROBABILITA'**. Stesso URL (ricerca full-text, `...&q=cumulative%20detection`).
  Estratto: *"After 30 glimpses (10 sec.)"* e *"cumulative probability has risen to 0.13 in the first case
  and 0.94 in the second case"* — conf. **A** (T=F). Mostra che a parita' di tempo la probabilita' dipende
  dal contrasto: non c'e' un tempo di scoperta unico.
  Estratto sulla definizione: *"the probability that a man selected randomly from the group has detected
  the target by that time"*.
- **Dimensione del settore modellato**: *"sectors of extent 10° in elevation and between 20° and 180°
  azimuth"*; *"The simulation frame time is 1/3 sec."* — conf. **A**.

**Conseguenza per il DES**: il tempo di scoperta non e' costante; e' una probabilita' cumulata che cresce a
ogni glimpse (~3/s). La "passata completa del settore" (2,7-3,9 s) e' il tempo di *rivisita dello stesso
settore*, non di un punto.

### 2.2 ADA025823 — scoperta di elicotteri da osservatori a terra (FE 43.8, Phase IIA)

Rapporto DTIC del 1976 (Pabon, Davison, Parks; US Army Combined Arms Combat Developments Activity).
**Letto** tramite Internet Archive (metadati + ricerca full-text).

- **Disegno**: *"Phase IIA was a one-sided experiment using AH-1G and OH-58 helicopters for detection at
  ranges from 1 to 5 kilometers by ground observers with unaided vision."* (abstract) — conf. **A**.
  URL: `https://archive.org/details/DTIC_ADA025823` (metadati).
- **Cosa misura**: *"data on the time required for a ground observer to detect an observation helicopter,
  an attack helicopter (AH), or an attack helicopter team (AHT) and the frequency of detection"* (abstract) —
  conf. **A**.
- **Tempo mediano di scoperta**: **~65 s**, con tempi **censurati a 60±5 s** (tempo di esposizione
  massimo per prova). Tipo: **TEMPO**.
  URL (ricerca full-text): `https://ia803105.us.archive.org/fulltext/inside.php?item_id=DTIC_ADA025823&doc=DTIC_ADA025823&path=/33/items/DTIC_ADA025823&q=median`
  Estratto: *"A large percentage of the times to detect were censored at 1 minute (t 5 seconds), the
  constrained exposure time for each trial."*
  Estratto: *"Because the percentage of censored times was so large (greater than 50 percent in most cases),
  the calculated median times were close to 65 seconds."* — conf. **A** (T=F).
  **Avvertenza**: e' una mediana *censurata* a un'esposizione di ~60 s; non e' il tempo medio reale (che
  sarebbe maggiore, non osservabile oltre i 60 s). E' un TEMPO, non un periodo di aggiornamento.
- **Definizione della misura**: *"(1) Median time to first detection (measured from start of line of sight)."*
  — conf. **A**.

### 2.3 ADA020657 — osservatori contro jet su terreno collinoso (1968)

Rapporto DTIC (Baldwin, Frederickson, Kubala, McCluskey, Wright; HumRRO). **Metadati letti**; il testo
full-text e' stato interrogato ma il valore numerico non e' stato estratto.

- **Disegno**: *"Sixteen observers searched a 180 deg sector for each trial, with early warning of an aircraft
  approach being provided for some trials."* (abstract) — conf. **A**.
  URL: `https://archive.org/details/DTIC_ADA020657`.
- **Cosa registra**: *"Three real time events--time at detection, time when the aircraft was at the estimated
  inbound range, and time when aircraft was at the estimated outbound range--were recorded for each observer
  for each trial."* (abstract) — conf. **A**. E' quindi un **TEMPO** (tempo alla scoperta) e una stima di
  portata, non una frequenza.
- **Statistiche descrittive previste**: *"Also computed for each variable were the mean, median, standard
  deviation and maximum and minimum values used."* — conf. **A**. Quindi il rapporto *ha* medie e mediane,
  ma sono in tabelle/grafici non estratti in modo affidabile (vedi sotto).
  URL (ricerca full-text): `https://ia801005.us.archive.org/fulltext/inside.php?item_id=DTIC_ADA020657&doc=DTIC_ADA020657&path=/27/items/DTIC_ADA020657&q=maximum`
- **Esito dichiarato**: *"In summary, the extensive analyses performed on the detection data yielded little in
  the way of positive results."* e *"Any analysis more sophisticated than descriptive statistics was not
  effective due to the imbalance and confounding present."* — conf. **A**.
  URL (ricerca full-text): `https://ia801005.us.archive.org/fulltext/inside.php?item_id=DTIC_ADA020657&doc=DTIC_ADA020657&path=/27/items/DTIC_ADA020657&q=summary`
- **Valore numerico di tempo medio/mediano di scoperta**: **non trovato** (le tabelle non sono state
  estratte in modo affidabile; l'OCR ha confidenza di pagina molto bassa, 17%).

### 2.4 Koopman — modello a glimpse e durata del glimpse

- **Modello**: la ricerca visiva e' una serie di glimpse **indipendenti**; la probabilita' cumulata
  cresce nel tempo con una legge di sopravvivenza (forma esponenziale).
  URL: `https://sarbayes.org/search-theory/brief-intro-to-sar-theory-1-of-4/`
  Estratto: *"Koopman modeled visual search as a series glimpses. Detection can happen on any glimpse, and
  importantly, the glimpses are assumed independent"* — conf. **M** (fonte secondaria divulgativa, letta).
  Nessun valore di durata in questa pagina.
- **Koopman 1956, "The Theory of Search. I. Kinematic Bases"**, *Operations Research* 4(3):324-346.
  URL: `https://ideas.repec.org/a/inm/oropre/v4y1956i3p324-346.html`
  Estratto (abstract): *"The second paper, entitled Target Detection, will deal with the second feature. It
  is based on the methods of survival probabilities familiar in actuarial studies, and is, it must be
  emphasized, confined to the case of independent trials."* — conf. **A** (abstract primario).
  **Correzione alla prima ricerca**: il link `v4y1956i3p324-346` e' il paper **I. Kinematic Bases**, non
  "Target Detection"; il seguito (II) e' un altro articolo.
- **Durata standardizzata del glimpse**: **1/3 - 1 s**. Tipo: **TEMPO** (convenzione, non misura di un
  osservatore antiaereo).
  URL (frammento di ricerca, pagina non letta): `https://www.jstor.org/stable/170928`
  Estratto: *"the probability of detection during a glimpse (usually standardized, as to 1/3 or to 1 second
  duration)"* — conf. **B** (snippet).
  URL (frammento di ricerca): `https://www.semanticscholar.org/paper/An-Empirical-Formula-for-Visual-Search-Koopman/2272e2a852dcbd9f591b380fd47d2d381ae6a7bb`
  Estratto: *"detection probability 1/2 on a single glimpse of about 1/3 to 1 second in duration"* — conf.
  **B** (snippet, probabile mirror dello stesso abstract).

### 2.5 Sensori ottici/TVD dei mezzi del registro

- **ZSU-57-2** (riga 3703; `visual`: "Crew visual observation + analog reflex sight"): nessun radar di
  scoperta; la scoperta e' a vista. **Dwell come rpm: non applicabile**; **tempo di scoperta di fonte:
  non trovato**. Il valore `acquisition_range: 6` del registro e' una STIMA dichiarata nel codice, non un
  dato (vedi commento nel registro).
- **M163-VADS** (riga 3825; `visual`, AN/VPS-2 solo distanza): idem. **Tempo di scoperta: non trovato**.
- **Strela-1-9P31** (riga 4007; `TVD` "Optical sight"): mirino ottico, dwell non applicabile.
  **Tempo di acquisizione: non trovato**.
- **MIM-72G-Chaparral** (riga 4065; `TVD` "Forward Looking Infrared"): FLIR, dwell non applicabile.
  **Tempo di acquisizione: non trovato**.
- **9K35-Strela-10** (riga 4181; `TVD` "Optical-IR tracker"): la scoperta e' a vista (o cueing esterno).
  Dato trovato ma **di altra grandezza**: *"The readiness of the projectile to launch varies from 5 to 10
  seconds... Receiving target designations takes 3-5 s."*
  URL: `https://en.delachieve.com/sam-strela-10-characteristics/` — conf. **B** (sito divulgativo tradotto).
  **Non e' un tempo di acquisizione visiva**: e' prontezza al lancio / ricezione designazione. Da non usare
  come tempo di scoperta.
  **Nota**: la tabella "Reaction time [s]" di [APA-Strela10] (6,5 / 8,5 / 6,5 / 7,0 s per le varianti) **non
  e' usata**: la fonte non definisce che cosa misuri (gia' rilevato nella prima ricerca). Non e' un tempo
  di acquisizione.
- **M6-Linebacker** (riga 4355; `TVD` "FLIR and targeting system"): scoperta demandata a cueing radar
  (AN/MPQ-64 Sentinel) e FLIR. **Tempo di acquisizione: non trovato**. Il FLIR e' "staring": dwell non
  applicabile. Dato qualitativo da **snippet** (nessun numero): *"A digital compass and gyro-stabilised
  turret allow automatic slew-to-target acquisition on the move. This auto-slew function accurately
  positions the launcher on a designated target reducing target acquisition time."*
  URL: `https://www.army-technology.com/projects/linebacker/` — conf. **B** (snippet di pagina non letta).
  Non ne segue un valore numerico.
- **MANPADS in generale (Stinger, Igla, Mistral)**: i dati trovati sono **tempi di reazione del sistema**,
  non di acquisizione/riconoscimento visivo del bersaglio da parte del servente. Esempi (tutti **B**, e
  **non** usabili come tempo di scoperta):
  - FM 44-18-1 (Stinger): *"If the gunner allows the gyro to fully spin up (3-5 seconds), tracks the target
    smoothly (steady IR tone), and uncages after IR acquisition, he should be scored go."*
    URL: `https://www.globalsecurity.org/military/library/policy/army/fm//44-18-1/ch152.htm` — **B**
    (snippet del manuale, pagina non letta; descrive la procedura di lancio, non il tempo di scoperta).
  - Mistral (Wikipedia): *"On the launcher, the missile runs up the gyro in 2 seconds, and total reaction
    time is 5 seconds."* URL: `https://en.wikipedia.org/wiki/Mistral_(missile)` — **B** (enciclopedico, e
    il Mistral non e' nel registro).

### 2.6 Natura delle grandezze (tempo, frequenza, probabilita')

| Grandezza | Valore | Tipo | Ha senso come "periodo di aggiornamento"? |
|---|---|---|---|
| Frequenza dei glimpse | ~3/s | **FREQUENZA** | No: e' il numero di colpi d'occhio al secondo; il suo inverso (~0,33 s) e' l'intervallo tra due glimpse |
| Durata media del glimpse | ~0,28 s (0,04-0,79 s) | **TEMPO** | Parzialmente: e' il tempo di una singola "occhiata", non il tempo per riscoprire un punto |
| Passata completa del settore | 2,72 / 2,99 / 3,94 s (30/60/120°) | **TEMPO** | **Si'**, e' il tempo per ripercorrere tutto il settore: l'analogo piu' vicino a un periodo di rivisita |
| Probabilita' cumulata di scoperta | cresce a ogni glimpse (passo 1/3 s) | **PROBABILITA'** | No: e' una legge cumulativa, non un periodo |
| Mediana (censurata) di scoperta elicotteri | ~65 s (censura 60±5 s) | **TEMPO** | No: e' il tempo alla prima scoperta in una prova, non un aggiornamento |
| Tempo di reazione/prontezza Strela-10 | 5-10 s (prontezza); 3-5 s (designazione) | **TEMPO** | No: e' un'altra grandezza (lancio/designazione) |
| Reazione totale Mistral | 5 s | **TEMPO** | No: reazione del sistema, non scoperta visiva |

## 3. Discordanze fra fonti

1. **"Glimpse" 0,28-0,33 s (Poe 1974, misure) contro "glimpse standardizzato 1/3-1 s" (Koopman, convenzione).**
   Non e' una contraddizione: Koopman *standardizza* la durata per definire la soglia di contrasto; Poe
   misura la durata effettiva delle fissazioni/glimpse. Per il DES il dato misurato e' 0,28-0,33 s.
2. **ADA025823: mediana ~65 s** contro **modello ADA017599 a glimpse ~3/s**. Non e' una contraddizione:
   ADA025823 e' una prova di campo con esposizione limitata a 60±5 s e dati censurati (mediana ~65 s e' un
   limite inferiore, non un tempo medio); ADA017599 e' un modello con settori piccoli (10° di elevazione)
   e condizioni diverse. I due valori non sono confrontabili direttamente.
3. **Tempo di scoperta come grandezza unica**: le fonti mostrano che non esiste *un* tempo di scoperta, ma
   una **distribuzione cumulata** (probabilita' che cresca col tempo). Un singolo `dwell_time_s` e' quindi
   un'approssimazione, non un dato equivalente.
4. **Prima ricerca**: dava Koopman come "glimpse ~1/3-1 s" da snippet. Ora: **confermato** lo snippet e
   **aggiunti** i valori misurati (0,28 s; 3/s) dal rapporto DTIC primario.

## 4. Analoghi candidati [S] (non sono dati; scelta dell'utente)

- **Ipotesi utente: 2 s come "colpo d'occhio"** [S]. Rispetto ai dati: e' **6-7 volte** la durata misurata di
  un glimpse (0,28-0,33 s) e circa la meta' di una passata completa di settore (2,7-3,9 s). Se il DES vuole
  modellare il *tempo di aggiornamento dello stesso punto*, 1/3 s (glimpse) e' il candidato piu' vicino al
  dato; se vuole modellare il *tempo per ripassare il settore*, 2,7-3,9 s e' il candidato. **2 s non ha una
  fonte**: e' una stima [S] e va marcata come tale.
- **Candidato "passata completa del settore" = 2,72 s (30°), 2,99 s (60°), 3,94 s (120°)** [S come scelta di
  quale usare; i valori sono F]. E' l'analogo piu' difendibile di un "periodo di rivisita" per un osservatore
  che cerca in un settore ampio: il settore viene ripercorso ogni ~3 s, ma ogni punto riceve un glimpse solo
  quando la passata lo attraversa.
- **Candidato "glimpse" = 0,28-0,33 s** [S come scelta; valori F]. E' l'intervallo fra due colpi d'occhio,
  non il tempo di riscoperta di un punto gia' visto.
- **Per gli osservatori contro elicotteri a 1-5 km**: la mediana censurata ~65 s [F] suggerisce che la
  scoperta di un bersaglio in avvicinamento e' un processo lento e cumulativo, non un aggiornamento di 2 s.

## 5. Cosa non ho trovato / non ho potuto verificare

- **ADA020657**: il valore numerico di tempo medio/mediano di scoperta **non e' stato estratto** (tabelle
  OCR a bassa confidenza; il rapporto stesso dice che le analisi hanno dato "little in the way of positive
  results"). Metodo e abstract sono verificati.
- **Tempo di acquisizione/riconoscimento** per **Strela-10, Strela-1, Chaparral, M6 Linebacker** e per
  **MANPADS** (servente): **non trovato**. I valori trovati sono tempi di reazione/prontezza al lancio o
  ricezione designazione, non tempi di scoperta visiva.
- **Koopman "Target Detection" (parte II)**: non letto; il link RePEc citato dalla prima ricerca e' la parte I.
  La durata del glimpse di Koopman e' solo da frammenti di ricerca (B).
- **Manuali tecnici primari** (TM/TO) di ZSU-57-2, M163, Strela-10, Chaparral, M6: non reperiti.
- **ResearchGate e Google Scholar**: non consultati/raggiunti (Semantic Scholar restituiva pagina vuota;
  il percorso che ha funzionato e' stato il mirror Internet Archive dei PDF DTIC).
- **Koopman 1946, "A theoretical basis for methods of search and screening"**: il libro e' su Internet
  Archive (194 pagine, OCR buono), ma la ricerca full-text ha restituito `IncompleteRead` per la dimensione
  della risposta: **non e' stato possibile estrarre la pagina sui glimpse** da questa copia.
- **Probabilita' cumulata di scoperta in funzione del tempo**: non c'e' una **tabella numerica** tempo-
  probabilita' (solo l'esempio 0,13/0,94 dopo 30 glimpse in ADA017599 e figure); per ADA020657 la
  tabella numerica non e' stata estratta.
- **Regime "normale"**: per la vista non esiste un regime di rotazione; i valori sono per prova/settore.

## 6. Metodo

- **Strumenti**: `webfetch`. `websearch` non disponibile. Scoperta URL via DuckDuckGo HTML e via la
  funzione "search inside" di Internet Archive (`.../fulltext/inside.php?item_id=...&doc=...&path=...&q=...`).
  Il testo delle pagine e' stato trattato come DATO, mai come istruzione.
- **Pagine/i cui contenuto e' stato letto e usato** (13):
  1. `https://archive.org/details/DTIC_ADA017599` (descrizione e metadati)
  2. `https://archive.org/stream/DTIC_ADA017599/DTIC_ADA017599_djvu.txt` (testo OCR, prime ~20 pagine;
     il resto del file e' stato troncato dallo strumento)
  3. `https://archive.org/metadata/DTIC_ADA017599` (file e pagine)
  4. `https://archive.org/metadata/DTIC_ADA020657`
  5. `https://archive.org/metadata/DTIC_ADA025823`
  6. `https://ia600101.us.archive.org/fulltext/inside.php?...&q=cumulative%20detection` (ADA017599)
  7. `https://.../fulltext/inside.php?...&q=median` (ADA020657: metodi statistici)
  8. `https://.../fulltext/inside.php?...&q=summary` (ADA020657: conclusioni)
  9. `https://.../fulltext/inside.php?...&q=maximum` (ADA020657: statistiche descrittive)
  10. `https://.../fulltext/inside.php?...&q=median` (ADA025823: tabelle e censura a 60 s)
  11. `https://sarbayes.org/search-theory/brief-intro-to-sar-theory-1-of-4/` (Koopman: modello a glimpse)
  12. `https://archive.org/details/theoreticalbasis02koop` (Koopman 1946, metadati)
  13. `https://ideas.repec.org/a/inm/oropre/v4y1956i3p324-346.html` (Koopman 1956, abstract)
- **Pagine di risultati di ricerca consultate solo per gli URL** (9): DuckDuckGo per "ADA017599 Poe",
  "Koopman glimpse duration", "MANPADS gunner reaction time", "Strela-10 reaction time", "air defense
  gunner target acquisition", "Stinger target acquisition time", "Chaparral reaction time", "9P31
  Strela-1", "M6 Linebacker FLIR". **Da qui vengono solo gli snippet** (JSTOR, Semantic Scholar,
  Delachieve, FM 44-18-1, Mistral, Army Technology): non sono state lette le pagine.
- **Pagine tentate e non leggibili / inutili**:
  - `https://apps.dtic.mil/sti/citations/ADA017599`, `.../ADA020657`, `.../ADA025823`: errore di trasporto.
  - `https://web.archive.org/web/2023/https://apps.dtic.mil/sti/citations/ADA017599`: HTTP 429.
  - `https://www.faa.gov/.../201409.pdf`: PDF non interpretabile dallo strumento (solo byte grezzi).
  - `https://archive.org/.../theoreticalbasis02koop...&q=glimpse`: errore `IncompleteRead` (risposta troppo
    grande); il libro di Koopman del 1946 **non e' stato interrogato utilmente**.
  - `https://www.semanticscholar.org/...`: pagina vuota.
  - `...&q=mean AND detection`: errore `IncompleteRead`.
  - Ricerche con frase quotata (`"mean detection time"`, `"time at detection"`, `"time required to detect"`):
    zero risultati; la ricerca full-text di Internet Archive non tratta bene le frasi.
- **Passi usati**: 72 (di 80). **Chiamate `webfetch`**: 40.

Nota: i valori ADA017599 sono citati da una copia OCR (Internet Archive) del PDF DTIC; dove l'OCR e'
illeggibile (formule, tabelle) l'ho dichiarato. Non ho potuto leggere il PDF originale per intero.

## 7. Sintesi (provvisoria)

1. **Il dato primario esiste e ora e' accessibile**: ADA017599 (Poe 1974), letto in parte e con ricerca
   full-text, da' glimpse **~3/s**, durata media **~0,28 s**, passata completa di settore **2,72-3,94 s**
   e la legge cumulata con passo **1/3 s**.
2. **ADA025823** da' una **mediana censurata ~65 s** per la scoperta di elicotteri a 1-5 km: processo lento e
   cumulativo.
3. **ADA020657** e' leggibile come metodo (16 osservatori, settore 180°) e sappiamo che calcolo' media,
   mediana, deviazione standard, massimo e minimo per ogni variabile; il **valore numerico** non e' stato
   estratto (tabelle OCR) e il rapporto stesso ridimensiona i risultati. Valore: **non trovato**.
4. **Koopman**: modello a glimpse indipendenti confermato (RePEc, abstract primario); durata standardizzata
   **1/3-1 s** (snippet, B). La prima ricerca citava come "Koopman 1956" il paper **I. Kinematic Bases**,
   non "Target Detection": correzione di etichetta.
5. **Per i mezzi del registro** (ZSU-57-2, M163, Strela-1, Chaparral, Strela-10, M6): **nessun tempo di
   acquisizione di fonte**. I valori esistenti sono reazione/prontezza al lancio (Strela-10: prontezza 5-10 s,
   ricezione designazione 3-5 s, **B**; Mistral: reazione totale 5 s, **B**) oppure una nota qualitativa
   (M6: lo slew-to-cue "reducing target acquisition time", **M**, senza numero). **Non sono tempi di
   scoperta visiva** e non vanno usati come tali.
6. **Conclusione**: un `dwell_time_s` unico per l'osservatore e' un'approssimazione. I candidati con fonte
   sono **~0,3 s** (glimpse) o **~3 s** (passata di settore); **2 s** resta una stima [S] senza fonte.
   La forma corretta sarebbe cumulativa (probabilita'), non `min(1, permanenza/dwell)`.

---

**Chiusura**: passi usati **72** (di 80); **40** chiamate `webfetch`; pagine/i lette e usate **13**; pagine
di risultati di ricerca consultate solo per gli URL **9**. Cosa non trovato: valore numerico di ADA020657;
tempo di acquisizione/riconoscimento di Strela-10/Strela-1/Chaparral/M6/MANPADS; parte II di Koopman;
manuali tecnici primari.