# Guida concettuale al motore DES — scaletta ragionata (fase A1)

> **Stato**: scaletta da approvare, **non** la guida. Scritta il 2026-11-19 sul manuale al commit di documentazione
> `31f81967` (branch `analysis/dce-dcs-persistence`); il codice descritto dal manuale è quello di `a99bb3d4` per il motore e
> `ff84e2a4` per test e scenari (nota in testa a `Manuale_Motore_DES.md:8-10`). Nessun file del manuale, del codice o della
> memoria è stato modificato.
>
> **A chi serve questa scaletta**: all'utente, per decidere struttura, livello di dettaglio e punti aperti prima della
> stesura (fase B); all'agente che prepara la bibliografia, per sapere quali argomenti hanno bisogno di una fonte.
>
> **Aggiornamento 2026-11-20 (inizio della fase B).** Le domande Q1-Q11 hanno una risposta (§0.4 e sezione (i)); la struttura
> definitiva della guida è in §0.4 (sezione nuova sui pianificatori, sezione 12 spostata in un documento di stato separato,
> riassunto iniziale). Il corpo delle sezioni qui sotto conserva la **numerazione della scaletta del 2026-11-19**: per passare
> alla numerazione della guida si usi la tabella di §0.4. La §1.1 del capitolo 1 è stata ripristinata nel manuale (`03555c81`):
> le note «ASSENTE» delle sezioni 2 e 14 sono superate.

## 0. Impostazione generale

### 0.1 Lettore e obiettivo

Lettore: un **responsabile di progetto** che non programma. Deve uscire dalla lettura sapendo: (1) che cosa il motore
risponde e che cosa no; (2) come è fatto, a grandi blocchi; (3) perché è fatto così; (4) **quanto fidarsi** dei suoi
risultati e dove stanno le stime non tarate; (5) quali decisioni restano a lui; (6) dove cercare il dettaglio nel manuale.

### 0.2 Regole di scrittura della guida (da applicare in fase B)

- **Nessun riferimento al codice**: niente nomi di file, funzioni, classi, campi, interruttori, righe. I nomi di progetto
  delle regole (D-5, BI, VA, FP, fasi F0-F9, passi G1-G5) compaiono **solo** in una tabella di corrispondenza in appendice
  (sezione 14), perché il manuale li usa come titoli e il lettore deve poterli ritrovare (v. domanda aperta Q3).
- **Etichette di affidabilità**, riprese dal manuale e usate in modo uniforme in tutta la guida:
  - **[V]** verificato sul codice nel manuale (con la data della verifica dove conta);
  - **[S]** stima o scelta di progetto non tarata («STIMA DICHIARATA», `Manuale_Motore_DES.md:276-279`);
  - **[D]** decisione dell'utente (non è una stima: è una scelta, ma non è nemmeno un dato misurato);
  - **[NV]** non verificato, oppure numero dichiarato da un rapporto e non rieseguito, oppure numero da sonda temporanea non
    rieseguibile dalla suite.
- **Letteratura contro scelta di progetto**: ogni sezione separa in modo visibile «idea presa dalla letteratura» e «scelta
  del progetto». Nessuna citazione inventata: i punti dove serve una fonte sono marcati qui come `[FONTE: argomento]` e
  saranno riempiti con la bibliografia verificata (file separato, altro agente).
- **Stato datato**: la guida dichiara in testa la data e il commit del manuale su cui è scritta, perché il motore cambia
  spesso (dal 2026-11-04 al 2026-11-19 i file del manuale sono stati toccati da 10 commit, `git log --since=2026-11-04`).
- **Diagrammi**: Mermaid, piccoli (al più 10-12 nodi), **concettuali** (nessun nome di codice). Ogni diagramma della guida
  indica in didascalia il diagramma tecnico del manuale da cui deriva (D-numero), per chi vuole scendere di livello.
  Nessun renderer in questo ambiente: la sintassi va controllata in Obsidian.

### 0.3 Struttura proposta e differenze rispetto a quella suggerita

| # | Sezione della guida | Corrisponde a (traccia suggerita) | Motivo della modifica |
|---|---|---|---|
| 1 | A che cosa serve e a che cosa NON serve | a | — |
| 2 | L'idea di base: simulare per eventi, non per passi di tempo | b | — |
| 3 | Come è fatto: i quattro strati e il percorso di una sessione | c | — |
| 4 | Che cosa entra: missioni, operazioni, regole d'ingaggio | (in f) | **Separata**: la missione è l'«ordine» che il motore esegue; senza di essa le sezioni 5-7 non si capiscono |
| 5 | Incontrarsi e vedersi: contatti e rilevamento | d | — |
| 6 | Lo scontro: reazione, scelta dell'arma, salva, difese, danno, rottura | e | Aggiunto il «fuoco su posizione» come caso a parte |
| 7 | Tempo, carburante, munizioni e stato delle unità in una sessione | f | — |
| 8 | Dalla sessione alla campagna | g | — |
| 9 | Casualità e riproducibilità | h | — |
| 10 | Come si verifica il motore e che cosa significa | i | — |
| 11 | Quanto fidarsi dei risultati: limiti, stime, punti non verificati | j | Rafforzata: è la sezione di maggior valore per un responsabile |
| 12 | **Decisioni aperte e tarature da fare** | (nuova) | Richiesta dalla traccia («cosa decidere/ricalibrare»): raccoglie in un posto solo ciò che spetta all'utente |
| 13 | **Da dove vengono le idee: letteratura e scelte di progetto** | (nuova, riassuntiva) | Una tabella sola che evita di disperdere il confronto con la letteratura; serve anche a dire che cosa il motore **non** è (non Lanchester) |
| 14 | Come leggere il manuale | k | Con la tabella di corrispondenza dei nomi di progetto |
| 15 | Glossario | l | — |
| 16 | Bibliografia | m | Arriva da un altro agente |

### 0.4 Decisioni dell'utente (Q1-Q11) e struttura definitiva (2026-11-20)

Decisioni che vincolano la stesura (dettaglio nella sezione (i)):

- **Q1** — file finale `Guida_Concettuale_DES.md` in questa cartella; in testa la data e il commit del manuale su cui è scritta.
- **Q2** — le formule restano e sono **parte centrale** del testo (legge di Pd, saturazione, permanenza, CPA, potatura...),
  spiegate a parole e con esempi numerici marcati **ILLUSTRATIVI**; nessun riquadro facoltativo.
- **Q3** — nel testo solo descrizioni piane; le sigle di progetto (D-5, BI, VA, FP, F0-F9, G1-G5, ...) solo nella tabella di
  corrispondenza della sezione 14.
- **Q4** — §1.1 ripristinata nel manuale; il «micro-passo» non esiste nel codice e non va ripreso.
- **Q5** — fotografia da **1219 esecuzioni INSTALLATA** (2026-11-19; prima 1103); sostituita il 2026-11-20 da una nuova da 1219
  (`a910dc15`, Pd al bordo a 0,2: 716 cambiate, 503 identiche rispetto alla precedente).
- **Q6** — fonti primarie; le secondarie solo come indicazioni di lettura. Le pagine del wiki su Hughes e Lanchester derivano da
  conversazioni con assistenti AI: **non si citano**. Il motore **non** è un modello alla Lanchester.
- **Q7** — i pianificatori di rotta e d'attacco (manuale cap. 7 §7.8-§7.9) hanno una **sezione propria** (sezione 9 della guida,
  scaletta in «Sezione 8-bis» più sotto).
- **Q8** — la guida dichiara che oggi il motore serve a **confronti relativi con repliche** e che **non c'è validazione** su dati
  reali o storici.
- **Q9** — la sezione 12 (decisioni aperte e tarature) **non fa parte della guida**: va in un documento di stato separato, scritto
  da altri. La guida rimanda a quel documento senza riportarne il contenuto.
- **Q10** — **confermata dall'utente il 2026-11-20**. Formulazione usata nella stesura: «il contratto di
  ingresso/uscita è lo stesso sia per una sessione sintetica sia per una giocata in DCS; il DES risolve solo le sintetiche; oggi
  non esiste un adattatore DCS né un chiamante di produzione del ciclo di campagna».
- **Q11** — lunghezza completa (circa 58-67 pagine), decisa dalla chiarezza, con un **riassunto iniziale** di 1-2 pagine.

Struttura definitiva della guida (la colonna «scaletta» dà il numero usato nel corpo di questo file):

| # guida | Sezione | # scaletta |
|---|---|---|
| — | Intestazione, come leggere la guida, etichette | 0 |
| — | **Riassunto iniziale** (1-2 pagine, copre tutta la guida) | nuovo |
| 1 | A che cosa serve e a che cosa NON serve | 1 |
| 2 | Simulare per eventi, non per passi di tempo | 2 |
| 3 | I quattro strati e il percorso di una sessione | 3 |
| 4 | Missioni, operazioni, regole d'ingaggio | 4 |
| 5 | Contatti e rilevamento | 5 |
| 6 | Lo scontro | 6 |
| 7 | Tempo, carburante, munizioni, stato delle unità | 7 |
| 8 | Dalla sessione alla campagna | 8 |
| 9 | **Attorno al motore: i pianificatori di rotta e d'attacco** (nuova, Q7) | 8-bis |
| 10 | Casualità e riproducibilità | 9 |
| 11 | Come si verifica il motore | 10 |
| 12 | Quanto fidarsi dei risultati | 11 |
| — | ~~Decisioni aperte e tarature~~ → documento di stato separato (Q9) | 12 |
| 13 | Da dove vengono le idee | 13 |
| 14 | Come leggere il manuale (con la tabella delle sigle) | 14 |
| 15 | Glossario | 15 |
| 16 | Bibliografia (dal file verificato) | 16 |

Stesura a parti: **parte A** = intestazione, riassunto, sezioni 1-4 (`Guida_Concettuale_DES_ParteA.md`, 2026-11-20).

---

## Sezione 1 — A che cosa serve e a che cosa NON serve il motore

**Scopo.** Collocare il motore nel progetto prima di qualunque dettaglio.
**Messaggio chiave.** Il motore DES calcola **come va a finire un turno di campagna giocato senza giocatore DCS** (una
«sessione virtuale»), unità per unità, in un tempo di calcolo breve; non pianifica la campagna, non decide le missioni, non
sostituisce DCS e non è (ancora) collegato a un chiamante di produzione.

**Concetti da spiegare.**
- Campagna, turno, sessione; sessione giocata in DCS contro sessione sintetica (virtuale).
- Il motore riceve un **ordine di sessione** (chi, dove, con quali missioni, per quanto tempo) e restituisce un **esito di
  sessione** (danni, consumi, perdite, esiti di missione, posizioni finali).
- **Indifferenza al simulatore**: il nucleo non conosce DCS; «cancellando l'adattatore DCS la campagna deve girare con sole
  sessioni sintetiche». Oggi un adattatore DCS **non esiste** nel codice Python: è un'intenzione di progetto.
- Che cosa il motore NON fa (elenco esplicito): non sceglie le missioni né quando lanciarle (livello C2, non costruito); non
  gestisce logistica di base; non legge mappe né terreno; non fa movimento al di fuori delle rotte assegnate; non ha giocatori.
- Chi lo usa oggi: **solo test e scenari** (nessun chiamante di produzione).

**Glossario.** Sessione virtuale (turno di campagna risolto dal motore senza DCS); ordine di sessione (descrizione completa
dell'ingresso di una sessione); esito di sessione (resoconto completo dell'uscita); core (insieme dei moduli del motore e del
ciclo di campagna, indipendente dal simulatore); adattatore DCS (componente previsto che tradurrebbe ordine ed esito da e
verso DCS; non esiste).

**Mappa verso il manuale.**
- Capitolo 1 §1.2-§1.4 (`02_Scopo_e_Motivazioni.md`) — [V] righe riportate a `a389cadb` il 2026-11-13.
- Capitolo 10 §10.3 (L0, contesto del core, `11_Atlante_Diagrammi.md:229-288`) — [V] a `f009eb43`, con note successive
  che dicono che il core non è cambiato nei punti di contesto.
- Capitolo 9 §9.1 «Limiti della campagna (F8)» per «nessun chiamante di produzione» — [V].
- Capitolo 8 §8.3 (agnosticismo come test di contratto) — [V] (numeri di suite dichiarati, non rieseguiti).

**Diagrammi proposti.**
- *G1 — Il motore nel suo contesto* (flowchart LR, 6-8 nodi): pianificazione della campagna (futura) → ordine di sessione →
  motore DES **oppure** DCS (tratteggiato: adattatore previsto) → esito → stato della campagna. Deriva da **D57** (L0) e da
  **D1** per il blocco «ciclo di campagna».

**Letteratura.**
- `[FONTE: livelli dei modelli di difesa — ingaggio, missione, campagna, teatro]` per collocare il motore (che sta fra
  «ingaggio» e «missione», dentro un ciclo di campagna). Già nel wiki: `Analysis/WIKI_LLM_SIMULATION/wiki/concepts/campaign-model.md`
  (dalla fonte RAND di Hillestad e Moore, `sources/source-theater-level-campaign-model.md`).
- `[FONTE: scopi della simulazione militare — analisi, addestramento, wargame]`; nel wiki
  `concepts/wargaming.md` e `sources/source-simulation-techniques-past-conflicts.md` (Sabin).

**Limiti e incertezze da dichiarare.**
- Nessun chiamante di produzione del ciclo di campagna [V]; nessun adattatore DCS [V].
- Il bilancio di calcolo «fino a minuti per sessione» è un **vincolo dichiarato dall'utente**, **non misurato** nel manuale
  [NV] (capitolo 1 §1.3 punto 4); lo scenario di scala S8 verifica solo «completa entro un limite di tempo» su 40 blocchi e
  240 asset, non 10.000.
- 10.000 asset è un **limite teorico superiore**, non un caso provato [D].

**Rischi di fraintendimento.**
- «Motore» non significa «simulatore 3D» né «sostituto di DCS»: spiegare che produce numeri ed eventi, non immagini.
- La frase d'apertura del manuale («e, per costruzione, anche quelli con un giocatore», `Manuale_Motore_DES.md:5-6`) può far
  credere che il DES risolva anche le sessioni giocate in DCS: la guida deve dire che il **contratto** è lo stesso, non che
  il DES le esegue (v. Q10, confermata il 2026-11-20).
- «Indifferente al simulatore» non vuol dire «già integrato con DCS».

---

## Sezione 2 — L'idea di base: simulare per eventi, non per passi di tempo

**Scopo.** Spiegare la scelta architetturale centrale senza formule.
**Messaggio chiave.** Il motore non fa avanzare un orologio a scatti fissi: **salta da un fatto rilevante al successivo**
(un contatto, un lancio, un impatto, la fine di un movimento), e i momenti in cui due unità si incontrano sono **calcolati
con la geometria**, non scoperti controllando la situazione a ogni istante. È questo che rende possibili ore di combattimento
in minuti di calcolo.

**Concetti da spiegare.**
- Simulazione a passi di tempo (tick) contro simulazione a eventi discreti (DES): analogia dell'agenda contro il cronometro.
- Perché il tick a 1 ms proposto all'inizio è stato scartato: ordine di grandezza del costo (decine di miliardi di
  aggiornamenti per 2 ore e 10.000 asset). I numeri esatti stanno nella §1.1 **oggi assente dal capitolo 1** (v. sotto).
- Che cosa è stato **conservato** della proposta a tick: la scomposizione della reazione in rilevazione, valutazione,
  comando, attuazione (ciclo OODA), trasformata in **ritardi** che programmano eventi futuri («questo asset lancerà fra 26 s»).
- Perché la sola risoluzione probabilistica non bastava: non dice **se e quando** due forze si incontrano.
- Coda degli eventi; ordine fisso degli eventi simultanei come parte del contratto (anticipo della sezione 9).
- Contatti **analitici**: l'istante d'incontro si ricava da un'equazione del moto (punto di massimo avvicinamento), non
  da un campionamento.

**Glossario.** Evento discreto (fatto puntuale che cambia lo stato: lancio, impatto, fine movimento); coda degli eventi
(agenda ordinata per tempo dei fatti futuri); tick (passo fisso di tempo); OODA / RIV-VAL-COM-ATT (le quattro fasi della
reazione: rilevare, valutare, comandare, attuare); CPA/TCPA (punto e istante di massimo avvicinamento fra due mobili).

**Mappa verso il manuale.**
- Capitolo 1 **§1.1 «Il problema: simulare ore di combattimento in minuti di calcolo»** — **ASSENTE dal file attuale**:
  il capitolo 1 inizia con §1.2 (`02_Scopo_e_Motivazioni.md:31`), ma il testo lo cita ancora (`02_Scopo_e_Motivazioni.md:25`:
  «§1.1, §1.3, §1.5») e lo cita il capitolo 7 §7.3 (`08_Supporto_Trasversale.md:157-158`: «capitolo 1, §1.1»). La sezione esisteva
  fino al commit `355b1017` ed è sparita con `234071d3` (2026-10-18, aggiornamento a `a784a9e7`); il contenuto è recuperabile
  da `git show 355b1017:Analysis/Document/Manuale_Motore_DES/02_Scopo_e_Motivazioni.md` e dalla decisione del wiki
  `Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md` (sezione «Decisione»). [NV] per lo stato attuale:
  non riverificato da nessun aggiornamento successivo, perché mancante.
- Capitolo 1 §1.5 (le due decisioni che attraversano gli strati) — [V].
- Capitolo 3 §3.1-§3.2 (meccanismi A, B, C dello scheduler) — [V] riverifica 2026-11-13.
- Capitolo 6 §6.2 (coda eventi di sessione, tre tipi di evento) — [V] con `:riga` a `fa5fbf1e` + regola di conversione.
- Capitolo 7 §7.3 (latenze come parametri, non cicli) — [V].

**Diagrammi proposti.**
- *G2 — Tick contro eventi* (flowchart LR o gantt semplice, due righe): a sinistra un asse con scatti regolari e molte
  «verifiche a vuoto», a destra un asse con salti fra eventi. Nessun D tecnico corrispondente; spunto dal disegno ASCII del
  wiki `concepts/event-driven-simulation.md`. *Nota: evitare il tipo Mermaid `timeline`, non sempre supportato; un `gantt`
  o due catene di nodi bastano.*
- *G3 — Dal ritardo di reazione all'evento futuro* (flowchart LR, 4-5 nodi): rilevamento → (ritardo di reazione) → lancio →
  (tempo di volo) → impatto. Deriva da **D5** (sequenza della coda eventi dentro un ingaggio).

**Letteratura.**
- `[FONTE: testo di riferimento sulla simulazione a eventi discreti — avanzamento al prossimo evento, lista degli eventi]`
  (tipo: manuale universitario di simulazione). Wiki: `concepts/event-driven-simulation.md` (deriva dalla fonte RAND TLC).
- `[FONTE: effetto del meccanismo di avanzamento del tempo sulle simulazioni di combattimento]` (tipo: articolo; il
  documento di analisi `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §10 ne elenca uno, da
  verificare).
- `[FONTE: simulatori militari a livello di entità basati su eventi — es. i sistemi citati nel documento di analisi —
  e simulatori aggregati a passo fisso]` (tipo: documentazione tecnica ufficiale). Il manuale (vecchia §1.1) e il wiki
  affermano che i primi sono event-driven e i secondi aggregati: **affermazione del progetto, da sostenere con fonti
  primarie** (il §10 del documento di analisi cita per lo più pagine divulgative o di fornitori).
- `[FONTE: ciclo OODA / kill chain e tempi di reazione dei sistemi d'arma]` (tipo: dottrina, studi tecnici).
- `[FONTE: calcolo del punto di massimo avvicinamento fra mobili]` (tipo: cinematica / anticollisione).

**Limiti e incertezze.**
- Il costo di calcolo reale **non è misurato** sul caso grande [NV]; i numeri di §1.1 sono stime d'ordine di grandezza del
  documento di analisi (non misure sul motore).
- Il moto è **rettilineo uniforme a tratti** (spezzata di punti): ogni manovra fuori dalla rotta assegnata non esiste [V].

**Rischi di fraintendimento.**
- **DES non è «tick»**: il lettore potrebbe pensare a un orologio fine «ma ottimizzato». Sottolineare che fra due eventi
  non si calcola nulla.
- La vecchia §1.1 parlava di «micro-passo fine ammesso solo dentro una finestra di ingaggio»: **non risulta** dal manuale
  attuale che il motore lo usi (nessuna occorrenza di «micro-passo» nei file del manuale). La guida non deve riprenderlo
  senza una verifica (v. Q4).
- «Analitico» non significa «esatto nella realtà»: è esatto **rispetto al modello di moto** (tratti rettilinei a velocità
  costante).

---

## Sezione 3 — Come è fatto: i quattro strati e il percorso di una sessione

**Scopo.** Dare la mappa mentale dell'architettura e seguire una sessione dall'ingresso all'esito.
**Messaggio chiave.** Quattro strati con domande diverse — **il contratto** (che cosa entra ed esce), **quando** (contatti),
**come finisce** (scontro), **applicazione** (danni e consumi sulle unità) — coordinati da un **orchestratore** che non fa
calcoli propri; attorno, ma fuori dalla sessione, un **ciclo di campagna** che concatena le sessioni.

**Concetti da spiegare.**
- Strato 0: contratto di ingresso/uscita, solo «tipi di dominio» (identificativi, secondi, frazioni), più la sorgente di
  casualità di sessione.
- Strato 1: pianificatore dei contatti — deterministico, sola geometria.
- Strato 2: risolutore dello scontro — l'unico punto stocastico.
- Strato 3: applicazione dello stato **per singola unità** (mai «la forza ha perso il 20%»).
- Orchestratore: mette in fila i pezzi; ricava dalle missioni rotta, partenza e velocità; raggruppa i contatti in
  **episodi**; dopo ogni episodio può ri-pianificare gli aerei; fa la contabilità del carburante alla fine.
- Tre tipi di evento di sessione: ingaggio, fuoco su posizione, fine di un movimento (ordine fisso a parità d'istante).
- Il ciclo di campagna **non è un quinto strato** e il motore non lo conosce.
- Vincoli non negoziabili (dell'utente): limite teorico 10.000 asset con potatura per blocchi; riproducibilità da seme con
  ordine degli eventi nel contratto; perdite per singolo asset; bilancio di calcolo fino a minuti.
- Il modello aggregato preesistente a rapporto di forze resta solo come **ripiego**, mai risolutore primario.

**Glossario.** Strato (livello dell'architettura con una sola domanda); orchestratore (il coordinatore della sessione);
finestra di contatto (intervallo di tempo in cui due unità possono interagire); episodio d'ingaggio (gruppo di contatti
risolti insieme perché vicini nel tempo e nelle forze); stato ombra (copia di lavoro dello stato delle unità usata durante
lo scontro, applicata alla fine); esito di sessione.

**Mappa verso il manuale.**
- Capitolo 1 §1.2-§1.5 — [V].
- Capitolo 2 §2.1-§2.4 (porte) — [V] riverifica 2026-11-13 («le porte non cambiano»).
- Capitolo 6 §6.1-§6.3, §6.8-§6.9 (fila di `run_session`, coda, componenti ed episodi) — [V] con `:riga` a `fa5fbf1e` e
  regola di conversione; §6.20 per gli episodi.
- Capitolo 10 §10.4 (architettura L1, import reali), §10.6 (sequenze L3 di una sessione) — [V] a `a389cadb` per le righe,
  «controllo a campione» per i 97 riferimenti spostati delle sequenze.
- Capitolo 10C §10C.9 (mappa dei dati D127-D129, `11c_Atlante_Porte_Campagna.md`) — `:riga` ricalcolati, **riletti per i
  riferimenti, non affermazione per affermazione** (`Manuale_Motore_DES.md:19`) [NV parziale].

**Diagrammi proposti.**
- *G4 — I quattro strati* (flowchart TD, 7-8 nodi, senza nomi di file): Contratto → Quando → Come finisce → Applicazione,
  con l'orchestratore a lato e il ciclo di campagna fuori. Deriva da **D1** (L1, che mescola frecce di dati e di import: la
  guida usa **solo frecce di dati**, come dice la nota di D1) e **D127**.
- *G5 — Il percorso di una sessione* (sequenceDiagram concettuale, 5 partecipanti: Ordine, Contatti, Scontro, Applicazione,
  Esito; 8-10 messaggi). Deriva da **D8**, **D9**, **D64-D66**.
- *G6 — Episodi* (disegno a barre orizzontali su un asse dei tempi, gantt): tre contatti, due raggruppati in un episodio e uno
  separato, con la ri-pianificazione fra i due. Deriva da **D40**.

**Letteratura.**
- `[FONTE: architetture a strati / separazione fra pianificazione dei contatti e risoluzione dell'ingaggio nei simulatori
  militari]` (tipo: documentazione di simulatori a livello di entità).
- `[FONTE: risoluzione variabile e multi-risoluzione — perché si separano i livelli di dettaglio]`; wiki
  `concepts/variable-resolution-modeling.md`, `concepts/cross-resolution-modeling.md` (dalla fonte RAND TLC); il documento di
  analisi cita Davis (RAND R-4252), da verificare.

**Limiti e incertezze.**
- La potatura per blocchi è **conservativa** (meglio esaminare troppe coppie che perderne una) [V]; il suo guadagno su
  scala grande non è misurato [NV].
- Fra un episodio e l'altro si ri-pianificano **solo gli aerei**; forze terrestri e navali che si ritirano restano passive
  sulla rotta [V] (capitolo 9 §9.1 «Re-scheduling»).
- La decisione di ri-pianificare si prende **alla fine** dell'episodio, non durante [V].

**Rischi di fraintendimento.**
- «Orchestratore» non è un comandante: non prende decisioni tattiche, applica regole.
- «Episodio» non è «battaglia»: è un raggruppamento tecnico di contatti.
- Lo «stato ombra» non è una seconda verità: è la bozza di lavoro che diventa reale alla fine dell'episodio.

---

## Sezione 4 — Che cosa entra: missioni, operazioni, regole d'ingaggio

**Scopo.** Spiegare l'«ordine» che il motore esegue e che cosa il motore ne legge davvero.
**Messaggio chiave.** Ogni unità agisce **dentro una missione** (rotta, orari, attese, bersaglio, regole di fuoco, armi
consentite, criteri di fine); la missione è anche **l'unità dello scontro**. Il motore legge solo una parte della missione:
quello che non legge non ha effetto, anche se è scritto nell'ordine.

**Concetti da spiegare.**
- Operazione ⊃ missione ⊃ unità; tipo di missione e postura tattica come **due assi distinti**.
- Dalla missione il motore ricava rotta, partenza, velocità (la missione va alla velocità del mezzo più lento), attese,
  orario sul bersaglio, presenza prima del decollo e dopo l'atterraggio.
- La missione come **forza dello scontro**: ogni missione ha la propria tenuta e il proprio disimpegno; più missioni dello
  stesso blocco o della stessa operazione condividono fuoco, percezione e difesa (dominio di coordinamento).
- Regole d'ingaggio di missione: bersaglio designato, regole di fuoco (ROE), armi designate, politica d'armi per tipo di
  missione (solo missioni aeree).
- Postura continua delle unità senza missione (aerei a terra, unità di superficie in difesa).
- Esito di missione con una regola unica di precedenza (distrutta > completata > abortita > in corso > fallita).
- Che cosa **non** è letto: ruoli degli asset (salvo formazione), regole diverse dalla ROE (allerta, EMCON, reazione alla
  minaccia, formazione), alcuni criteri di fine; condizioni «su evento» solo dichiarabili.

**Glossario.** Missione; operazione (raggruppamento di scopo di più missioni, valido per una sessione); postura (atteggiamento
tattico: attacco, difesa, ritirata, ...); dominio di coordinamento (insieme di missioni che condividono fuoco, percezione e
difesa); ROE (regole di fuoco: libero, solo in risposta, divieto); politica d'armi (tabella che dice quali armi un tipo di
missione può usare contro quale bersaglio); TOT (orario sul bersaglio); criteri di fine (condizioni che fanno terminare
l'attività: munizioni finite, danno, bersaglio distrutto, durata, carburante).

**Mappa verso il manuale.**
- Capitolo 2 §2.6-§2.8 (tipi della missione, tassonomia, attraversamento della porta) — [V] riverifica 2026-11-13.
- Capitolo 4 §4.27-§4.33 (missione come forza, dominio, aerei a terra, fine di attività, regole di bersaglio, politica
  d'armi) — sezioni rimaste identiche dal 2026-10-20; `:riga` rimappati automaticamente il 2026-11-13 [V per contenuto a
  `dcedc541`; righe in parte NV].
- Capitolo 6 §6.10-§6.16, §6.18, §6.22 — [V] a `fa5fbf1e`.
- Capitolo 9 §9.1 «Limiti della Missione», «Limiti introdotti dalla fase F4», «Regole d'ingaggio di missione (F7a)».

**Diagrammi proposti.**
- *G7 — Operazione, missione, unità* (flowchart TD, 6 nodi). Deriva da **D16** (tipi della missione).
- *G8 — I due assi: postura e tipo di missione* (flowchart LR). Deriva da **D18**, già concettuale.
- *G9 — Che cosa il motore legge di una missione* (tabella a due colonne «letto / non letto»): nessun D; dal capitolo 9 §9.1
  «Limiti della Missione».
- *G10 — Regola dell'esito di missione* (flowchart TD a cascata, 5 nodi). Deriva da **D19**.

**Letteratura.**
- `[FONTE: struttura degli ordini e delle missioni aeree e terrestri — tipi di missione, ROE, TOT]` (tipo: dottrina NATO/USA
  pubblica). Nel wiki non c'è una fonte pertinente.
- La politica d'armi è una **scelta di progetto [D]**, non tratta dalla letteratura: dirlo.

**Limiti e incertezze.**
- Politica d'armi per tipo di missione: scelta di progetto confermata dall'utente riga per riga [D], solo per missioni
  aeree; terra e mare senza vincoli d'arma [V].
- Nessun «cueing»: un tiratore spara solo a ciò che ha rilevato lui; la designazione non dà rilevamento [V].
- Condivisione nel dominio **istantanea e senza perdite** [V, approssimazione dichiarata].
- Missione di un solo aereo «distrutta» alla prima perdita [V].
- Raggio efficace di un bersaglio «punto» 500 m [S]; altre costanti di formazione [S].
- Una missione deve stare dentro la sessione (validatore); chi chiama il motore direttamente può violarlo [V].

**Rischi di fraintendimento.**
- Scrivere una regola nella missione non garantisce che il motore la applichi (es. EMCON).
- «Operazione» qui non è un'operazione militare su più giorni: vale **per una sessione** [V].
- Il dominio di coordinamento non è una catena di comando (C2 non modellato).

---

## Sezione 5 — Incontrarsi e vedersi: contatti e rilevamento

**Scopo.** Spiegare come il motore decide **se** e **quando** due unità possono interagire e **se** una vede l'altra.
**Messaggio chiave.** Prima la **geometria** decide le finestre in cui due unità sono abbastanza vicine (nessun caso);
poi, per ogni **passaggio** del bersaglio nel volume di scoperta dell'osservatore, **un'estrazione casuale** decide se e a
che distanza avviene il rilevamento; la probabilità cala con la distanza e, se il passaggio è più breve del giro del radar,
anche con la permanenza. **Vedere non è poter colpire.**

**Concetti da spiegare.**
- Volume di minaccia e volume di scoperta; finestra di contatto; perché la geometria è deterministica.
- Punto di massimo avvicinamento e intervalli «a portata».
- Potatura per blocchi: si scartano prima le coppie di gruppi lontani.
- Legge di probabilità di scoperta (Pd): 1 a distanza zero, costante al bordo della portata (0,5 fino al 2026-11-19, 0,2 dal
  2026-11-20), calo «alla quarta potenza» (idea
  dall'equazione radar), moltiplicata per meteo/notte e ricognizione.
- **Un'estrazione decide sia se sia quando**: niente campionamento continuo.
- **Rilevamento per passaggio**: ogni ingresso nel proprio volume è un'occasione nuova; dopo l'uscita l'osservatore con la
  portata minore non lancia salve nuove.
- **Permanenza nel volume**: se il bersaglio resta nel volume meno del periodo di rivisita del sensore, la Pd si riduce in
  proporzione (legge probabilistica, non una soglia).
- Sensori: radar, ottico/infrarosso, vista; EWR; tre sensori composti per unità; quale portata vince.
- Rilevamento ≠ intercettazione.
- Nebbia di guerra (ricognizione) come fattore della Pd.

**Glossario.** Pd (probabilità di scoperta); portata di acquisizione; volume di scoperta; passaggio (intervallo continuo in cui
il bersaglio sta nel volume dell'osservatore); permanenza; periodo di rivisita (dwell, tempo fra due passate del fascio sullo
stesso punto); EWR (radar di scoperta a lungo raggio); orizzonte radar (limite di visibilità dovuto alla curvatura terrestre);
nebbia di guerra.

**Mappa verso il manuale.**
- Capitolo 3 §3.1-§3.8 — [V] riverifica 2026-11-13.
- Capitolo 4 §4.2 (legge di Pd) — [V] a `a389cadb`, riga della costante corretta il 2026-11-19.
- Capitolo 4 §4.18 (nebbia di guerra) — righe rimappate [V per contenuto, righe NV in parte].
- Capitolo 4 §4.35 (per passaggio) — [V] a `a389cadb`; §4.36 (permanenza) — [V] a `a99bb3d4`.
- Capitolo 7 §7.4 (degradazione ambientale), §7.8 (pianificatore di rotta: volumi, orizzonte), §7.12 (dati dei sensori) —
  [V] ricalcolo 2026-11-13.
- Capitolo 8 §8.13-§8.14 (scenari S31-S36) — [V] numeri di suite dichiarati [NV].
- Capitolo 9 §9.1 «La Pd non distingue radar da ottico», «Limiti dei sensori EWR e visivo», «FP», «D-5» — [V]/[NV] come
  indicato voce per voce.

**Diagrammi proposti.**
- *G11 — Rotta e volume* (disegno: flowchart o schema testuale; nessun Mermaid adatto a un disegno geometrico). Proposta: uno
  **schema ASCII** in blocco di testo (cerchio del volume, rotta che entra ed esce, punto di massimo avvicinamento), più
  leggibile di un Mermaid forzato. Deriva da **D3**/**D70** (tecnici).
- *G12 — Dal contatto al rilevamento* (flowchart TD, 7-8 nodi): finestra → passaggi nel volume proprio → per ogni passaggio
  Pd (distanza × ambiente × permanenza) → estrazione → rilevato a distanza r / non rilevato. Deriva da **D131** e **D133**
  (e **D12** per il fattore di ricognizione).
- *G13 — Curva della Pd* (tabella di 5 punti distanza/Pd, oppure grafico `xychart-beta` se supportato in Obsidian: da
  verificare). Nessun D.
- *G14 — Permanenza breve* (gantt a due righe: passata del fascio ogni T secondi; bersaglio nel volume per t < T).

**Letteratura.**
- `[FONTE: equazione radar e dipendenza del segnale da R^4]`, `[FONTE: curve di probabilità di scoperta di Swerling]`
  (tipo: manuale di ingegneria radar). Il manuale cita Swerling e R⁴ (capitolo 4 §4.2) senza riferimento bibliografico.
- `[FONTE: convenzioni sulla portata dichiarata di un radar — Pd 0,5 o 0,9]` (tipo: manuale radar / documentazione tecnica).
- `[FONTE: teoria della ricerca — legge di scoperta per «sguardi» successivi, Koopman]` (tipo: testo classico di ricerca
  operativa); citata nel manuale come riferimento qualitativo (capitolo 9 §9.1 D-5).
- `[FONTE: scoperta visiva da terra di aerei — tempi di scansione dell'osservatore]` (il manuale cita «Poe 1974» per la banda
  1,75-6 s: **da verificare alla fonte**).
- `[FONTE: orizzonte radar e raggio terrestre equivalente 4/3]` (tipo: manuale radar).
- Nessuna fonte del wiki è pertinente a questa sezione.

**Limiti e incertezze (dal manuale, con etichetta).**
- **Nessun orizzonte radar nel motore**: un EWR vede a piena portata anche un aereo radente [V]; il pianificatore di rotta
  invece lo taglia (incoerenza dichiarata) [V].
- Pd al bordo della portata: era 0,5, **stima giudicata alta dall'utente**; ricalibrata a **0,2 dal 2026-11-20** (stima senza
  fonte, scelta dell'utente) [S] (capitolo 9 §9.1 «Pd sul bordo della portata»).
- Forma della legge di Pd: semplificazione monotona [S].
- Meteo e notte con **un solo fattore** per ogni sensore: il visivo di notte è sovrastimato [V].
- Periodo di rivisita: valore **fisso** per sensore; 53 modelli con valore, **24 stime [S]**; vista e ottico 3,2 s
  approssimazione [S]; dipendenza da distanza/modo/carico **rinviata** [D].
- Permanenza: ipotesi di fase di scansione casuale e uniforme **non verificata su dati** [NV].
- Sessione che si chiude con il bersaglio nel volume: la Pd dipende dalla durata della sessione; un passaggio a cavallo di due
  sessioni dà due estrazioni indipendenti; **il rilevamento non passa da una sessione all'altra** — verificato con sonde
  temporanee non rieseguibili [NV per i numeri, V per la lettura del codice].
- Nessun settore di copertura (radar omnidirezionali), nessuna latenza di tracciamento manuale per i radar storici [V].
- Gli aerei senza radar di allarme non percepiscono i SAM; i sensori «terrestri» mancano nei registri per carri e navi (due
  forze terrestri non si vedono senza un'iniezione) [V].
- La nebbia di guerra è «debole» e c'è un difetto noto, non corretto, nel filtro dei blocchi militari [V].

**Rischi di fraintendimento.**
- «Rilevato» non significa «ingaggiato»: servono arma in portata, regole e tempo di reazione.
- «Con permanenza breve non si vede mai» è **falso**: si vede con probabilità ridotta.
- «Pd 0,5 al bordo» (e anche 0,2) non è un dato del radar: è una convenzione stimata.
- «Portata» qui è una sfera senza terreno: niente valli né rilievi.

---

## Sezione 6 — Lo scontro: reazione, scelta dell'arma, salva, difese, danno, rottura

**Scopo.** Spiegare come il motore risolve uno scontro molti-contro-molti.
**Messaggio chiave.** Lo scontro è una **catena**: chi ha rilevato reagisce dopo un ritardo tipico del suo sistema; sceglie
l'arma dai dati di registro secondo regole e scorte; i colpi che arrivano **insieme** su una forza sono prima confrontati
con la capacità delle difese (saturazione, alla Hughes); ogni colpo superstite è risolto **uno per uno** sull'unità colpita;
dopo ogni salva la forza colpita confronta le perdite con una **soglia di rottura** e può disimpegnarsi.

**Concetti da spiegare.**
- Ritardo di reazione e intervallo fra salve; iniziativa («chi spara per primo»).
- Scelta dell'arma dai registri (efficacia e costo), scorta **per modello d'arma**, cannone di bordo, gittata delle bombe.
- Regole di ripartizione del fuoco (a turno, locale, non ottima); precedenza ai lanciatori di missili contro la propria forza;
  dottrina contro lo spreco («due missili, poi guarda»; bersaglio già condannato).
- Il «carico congelato»: una salva partita arriva comunque, anche se il tiratore muore.
- **Salva e saturazione**: capacità di intercettazione per evento; il surplus passa intero.
- Difesa dai missili: chi può intercettare (armi antimissile), ordine di consumo, colpi lanciati da dentro il volume del
  difensore non intercettabili, servono traccia e tempo di reazione; (regola opzionale, spenta) quali colpi una difesa
  considera bersagli.
- Danno per singolo colpo: tre esiti (distrutto, danneggiato, mancato); fuori combattimento sotto metà salute, relitto sotto
  il 15%; accumulo emergente.
- Soglia di rottura stocastica: mediana di dottrina, modulata da morale, rapporto di forze percepito, fuoco senza risposta,
  postura, e da una «tempra» estratta; erosione cumulata **oppure** shock di una salva; disimpegno della **forza intera**.
- Scontri a più forze nello stesso episodio.
- **Fuoco su posizione** (caso a parte): artiglieria o navi sparano su una posizione stimata senza rilevamento; nessuna
  intercettazione, nessun effetto sul morale.
- Quota nel volume d'ingaggio (regola opzionale, spenta).

**Glossario.** Ph (probabilità di colpire); Pk|h (probabilità di distruggere dato il colpo); Pk; salva; evento-salva (colpi
che arrivano nello stesso istante su una forza); saturazione; intercettore; scorta per arma; soglia di rottura; erosione;
shock; tempra (resistenza propria di una forza, estratta a caso); disimpegno (ritirata della forza); overkill (spreco di
colpi su bersagli già condannati); fuoco su posizione; relitto.

**Mappa verso il manuale.**
- Capitolo 4 §4.1 (la catena) — **riferimenti di riga sfasati** (sezione parzialmente riscritta), contenuto aggiornato al
  2026-11-13 [V per contenuto].
- Capitolo 4 §4.3-§4.10 (latenze, fire control, salva, danno, disingaggio, N forze, payload congelato, stato ombra) — sezioni
  identiche dal 2026-10-20, righe rimappate [V contenuto a `dcedc541`].
- Capitolo 4 §4.16-§4.17, §4.19-§4.20 (arma dai registri, portata, scorta, bombe) — §4.17 [V] a `a389cadb`; §4.16 righe in
  parte sfasate.
- Capitolo 4 §4.21-§4.26 (rottura, E(N), RWR, difesa dai missili con BI, dottrina di tiro, R-INT) — BI e §4.26 [V] a
  `a389cadb`; il resto rimappato.
- Capitolo 4 §4.34, §4.37; capitolo 6 §6.23 (fuoco su posizione).
- Capitolo 5 §5.1, §5.3, §5.4 (danno, applicazione, stati di salute) — [V] a `fa5fbf1e`.
- Capitolo 7 §7.2-§7.3, §7.5, §7.10-§7.11 (dottrina, profili di reazione, capacità di difesa, RWR, efficacia antiaerea).
- Capitolo 9 §9.1 «Altri limiti», «Limiti introdotti dalle estensioni 2026-09-28/30», «BI», «VA», «Fuoco su posizione».

**Diagrammi proposti.**
- *G15 — La catena dello scontro* (flowchart LR, 7 nodi: rilevamento → reazione → scelta arma → salva in volo → difese →
  danno per colpo → soglia di rottura). Deriva da **§4.1** e **D5**.
- *G16 — Saturazione* (flowchart TD o tabella-esempio con numeri **fittizi dichiarati come tali**: 8 colpi, capacità 5, 3
  passano). Deriva da **D24**/**D33**. *Attenzione*: i numeri dell'esempio devono essere marcati come illustrativi.
- *G17 — Stati di una forza nello scontro* (stateDiagram, 4-5 stati: in combattimento, disimpegnata, distrutta, ...).
  Deriva da **D6**.
- *G18 — Da che cosa dipende la soglia di rottura* (flowchart TD, 6-7 nodi). Deriva da **D22**.
- *G19 — Stati di salute di un'unità* (stateDiagram: integra → danneggiata → fuori combattimento (≤50) → relitto (≤15)).
  Deriva da **D7**.

**Letteratura.**
- `[FONTE: modello a salva di Hughes — articolo originale e libro sulla tattica navale]` (tipo: articolo su rivista di
  ricerca operativa e monografia). Wiki: `concepts/salvo-combat-model.md` e `analyses/hughes-salvo-vs-engagement-resolver.md`;
  **attenzione**: la fonte ingerita (`sources/source-hughes-salvo-event-driven.md`) è **una conversazione con un assistente
  AI** (confidenza media), non letteratura primaria. Il documento di analisi cita l'articolo del 1995: da verificare.
- `[FONTE: Ph, Pk e scomposizione della probabilità di uccisione]` (tipo: manuale di efficacia delle armi).
- `[FONTE: soglie storiche di rottura/disimpegno delle unità — la regola del ~30% di perdite]`: il manuale dice «regola
  empirica diffusa nella letteratura militare» per l'erosione 0,30 (`08_Supporto_Trasversale.md:128-129`) **senza citarla**:
  serve una fonte (tipo: studi storici quantitativi sul combattimento).
- `[FONTE: dottrina di tiro «shoot-look-shoot» e prevenzione dell'overkill nella difesa aerea]` (tipo: dottrina/studi).
- `[FONTE: assegnazione arma-bersaglio (WTA)]` (tipo: ricerca operativa) — per spiegare che cosa il motore **non** fa.
- `[FONTE: tempi di reazione dei sistemi SAM e degli equipaggi]`: il manuale cita i totali documentati (Osa, S-300, Tor,
  equipaggio carro da un rapporto DTIC) presi dalla bibliografia del documento di analisi: da verificare.

**Limiti e incertezze.**
- Coefficienti della soglia di rottura (erosione 0,30, shock 0,20, dispersione e pesi): **stime di partenza, non tarate** [S],
  uguali per i tre lati; da ricalibrare con un processo interno di calibrazione (ATCAL) che **non risulta fatto** [NV].
- Morale e stima del nemico: **nessun chiamante li fornisce**, quindi il morale è sempre neutro [V].
- Scomposizione del ritardo di reazione nelle quattro fasi: stima [S]; i totali sono documentati; navi e classi senza dato
  usano il profilo più lento [V]; modulatore di abilità tutto a 1 [V].
- Pk indipendente dalla posizione nell'inviluppo [V]; arma scelta per scorta **prima** del controllo di portata [V];
  esponente costo/efficacia 0,5 [S].
- Ripartizione del fuoco greedy, non ottima [V]; finestra di raggruppamento delle salve 0 s (solo impatti simultanei) [S].
- Disimpegno solo per forza intera, nessun contagio fra forze [V].
- Difesa dai missili: nessun legame C2 fra batterie; tempo di volo dell'intercettore e sezione radar del colpo ignorati
  (ottimistico per la difesa) [V]; classificazione delle armi per la regola opzionale BI: 52 voci **stimate [S]**.
- Regole opzionali **spente** e non usate da nessun codice di produzione: bersagli intercettabili (BI), quota nel volume
  d'ingaggio (VA) [V].
- Fuoco su posizione: dispersione 50 m, raggio letale 0,25 m/mm di calibro, ripiego 25 m — **stime [S]**; niente aerei,
  niente missili, niente fuoco amico [V].
- Nessuna penetrazione di corazza (assente nei registri) [V].

**Rischi di fraintendimento.**
- **Non è un modello alla Lanchester**: niente equazioni di logoramento di forze aggregate; i colpi sono singoli e le perdite
  per unità. Il manuale dichiara che non usa coefficienti dei documenti Lanchester ingeriti (capitolo 4 §4.21,
  `05_Strato2_Risolutore_Ingaggio.md:1490`; capitolo 7 §7.2). Gli scenari S1-S5 riprendono dai documenti Lanchester **solo la
  composizione delle forze, senza i numeri** (capitolo 8 §8.4).
- «Alla Hughes» indica il **meccanismo** di saturazione per salva, non le equazioni aggregate di Hughes.
- Una «soglia stocastica» non è un difetto di riproducibilità (v. sezione 9).
- Il «morale» compare nel modello ma oggi non ha effetto.

---

## Sezione 7 — Tempo, carburante, munizioni e stato delle unità in una sessione

**Scopo.** Spiegare che cosa accade alle unità nel corso della sessione, al di là degli scontri.
**Messaggio chiave.** Il carburante **vincola il movimento** (un aereo a secco plana o si perde, un mezzo di terra si
ferma); gli aerei decidono il rientro al **bingo** con un albero di regole; danni e munizioni sono applicati **subito dopo
ogni episodio**, il carburante in un **conto finale** sui tratti definitivi; l'esito di ogni missione segue una regola unica.

**Concetti da spiegare.**
- Presenza nel tempo: a terra prima del decollo, attese, orario sul bersaglio.
- Consumo per tratto e nel tempo; esaurimento calcolato in anticipo; planata.
- Bingo: riserva di disimpegno (5 min alla massima spinta militare), soglia, albero di decisione (trasferimento /
  combattimento, basi alternative), rientro a ritroso, uscita di scena per aerei comparsi in volo senza basi.
- Consumo in ingaggio «a scatto».
- Fine di attività per criteri di missione (munizioni finite, danno, bersaglio distrutto, durata).
- Munizioni: scorta per arma, condivisa fra attacco e intercettazione.
- Nessun rifornimento dentro la sessione.
- Esito di missione e postura finale di ogni unità.

**Glossario.** Bingo (livello di carburante al quale si deve rientrare); riserva di disimpegno; planata; uscita di scena;
consumo in ingaggio; winchester (munizioni esaurite); postura finale.

**Mappa verso il manuale.**
- Capitolo 5 §5.2 (carburante, bingo) — [V] a `fa5fbf1e` (il modulo ha poi solo modifiche di commento, segnalate dall'atlante
  §10 nota 2026-11-13, non riportate nel capitolo 5) [V/NV minore].
- Capitolo 6 §6.5, §6.15-§6.20 — [V] a `fa5fbf1e`.
- Capitolo 4 §4.31 (fine di attività).
- Capitolo 10B (atlante del carburante, `11b_Atlante_Missione_Carburante.md`) — righe ricalcolate, riletto «per i
  riferimenti» [NV parziale].
- Capitolo 9 §9.1 «Limiti introdotti dalle fasi F5, F6 e G1-G5».

**Diagrammi proposti.**
- *G20 — Vita di un aereo in una sessione* (stateDiagram, 6-7 stati: a terra, in volo, in attesa, in combattimento, in rientro,
  atterrato / uscito di scena / perso). Deriva da **D41**.
- *G21 — Decisione al bingo, semplificata* (flowchart TD, 6-8 nodi). Deriva da **D38**.
- *G22 — Quando si applicano danni e carburante* (gantt o flowchart LR: episodi con applicazione immediata, conto finale del
  carburante alla fine). Deriva da **D9**/**D40**.

**Letteratura.**
- `[FONTE: pianificazione del carburante e riserve minime / bingo nelle operazioni aeree]` (tipo: manuali operativi pubblici).
- Albero di decisione, riserva e uscita di scena sono **scelte di progetto [D]**.

**Limiti e incertezze.**
- Dati di consumo «di emergenza» dei registri **non tarati**: unità dedotta, sottostima circa 1/6 a postbruciatore pieno [S].
- Costanti stimate: 300 s di disimpegno, 3000 m per le basi alternative e per l'area di una base, rapporto di planata 10 [S/D].
- Regola per gli aerei storici con emergenza < 5 min **non implementata** [V].
- Nessuna salva offensiva dopo il bingo; nessun rientro per danno; terra e mare senza bingo [V].
- Orbita senza circuito (aereo fermo nel punto); consumo delle soste pari alla crociera (sovrastima) [V].
- Formazione che si può dividere; forza «occupata» per episodio intero [V].

**Rischi di fraintendimento.**
- Il carburante **non** influenza lo scontro mentre avviene (lo scontro non legge il carburante): influenza ciò che succede
  dopo.
- «Uscita di scena» non è una perdita.
- Il conto finale del carburante non cambia l'ordine degli eventi già risolti.

---

## Sezione 8 — Dalla sessione alla campagna

**Scopo.** Spiegare che cosa accade fra una sessione e la successiva e che cosa sopravvive.
**Messaggio chiave.** Un **conduttore di campagna**, esterno al motore, esegue una sessione alla volta: prima applica i
processi fra sessioni (riarmo, rifornimento, riparazione a fine turnaround), poi **valida** l'ordine, esegue il motore, applica
le posizioni finali e registra l'esito. Danni, munizioni, carburante e posizione passano da una sessione all'altra; **il
rilevamento no**.

**Concetti da spiegare.**
- Registro di campagna (chi è pronto quando).
- Validatore di sessione: rifiuta ordini non validi (sessione aperta o > 4 h, missione oltre la fine, asset non pronto o
  distrutto, carburante insufficiente).
- Prontezza: turnaround e riparazione per classe; riarmo e rifornimento «gratuiti» alla fine.
- Posizione persistente (solo attraverso il conduttore).
- Esito di un'operazione, valido per una sessione.
- Che cosa passa e che cosa non passa fra sessioni.

**Glossario.** Conduttore di campagna; registro di campagna; validatore; turnaround (tempo per tornare pronto dopo una sessione);
prontezza; posizione persistente.

**Mappa verso il manuale.**
- Capitolo 2 §2.10 (tipi della campagna) — [V].
- Capitolo 6 §6.24-§6.27 — [V] (riverificati nel commit `e824cde9`).
- Capitolo 7 §7.13 (tempi di turnaround e riparazione) — [V] per la lettura dei valori; [NV] per le fonti (v. sotto).
- Capitolo 8 §8.12 (S30) — [V], numeri dichiarati [NV].
- Capitolo 9 §9.1 «Limiti della campagna (F8)» e «Taglio di sessione e sessioni concatenate» — [V]/[NV] come indicato.
- Capitolo 10C (`11c_Atlante_Porte_Campagna.md`) — righe ricalcolate, riletto per i riferimenti [NV parziale].

**Diagrammi proposti.**
- *G23 — Un passo del ciclo di campagna* (sequenceDiagram, 4 partecipanti: Conduttore, Prontezza, Validatore, Motore; 6-7
  messaggi). Deriva da **D54** e **D128**.
- *G24 — Che cosa passa fra due sessioni* (tabella «passa / non passa»: danni, munizioni, carburante, posizione / rilevamento,
  stima del nemico [NV]). Nessun D; dal capitolo 9 §9.1.
- *G25 — Esempio di sequenza di sessioni* (flowchart LR). Deriva da **D55** (fuori scala, scenario S30) — facoltativo.

**Letteratura.**
- `[FONTE: tempi di turnaround e riparazione di aerei, navi e reparti terrestri]` (tipo: rapporti tecnici, fonti ufficiali);
  il manuale dice che **una sola fonte è stata verificata sulla pagina originale** (turnaround dell'F-35, ~3 h).
- `[FONTE: modelli di campagna e gestione del tempo fra turni]`; wiki `concepts/campaign-model.md`.

**Limiti e incertezze.**
- Il ciclo di campagna **non ha chiamanti di produzione** [V].
- Tempi di turnaround e riparazione: ordini di grandezza; turnaround navale 48 h **stima senza fonte numerica** [S]; un tempo
  per classe, indipendente dall'impiego [V].
- Nessuna logistica: riarmo, rifornimento e riparazione non consumano risorse della base (attività F8d non fatta per decisione
  dell'utente) [D].
- Processi applicati all'inizio della sessione successiva, non all'istante in cui l'asset è pronto [V].
- Riparazione a gradino (salute a 100 solo alla fine) [V].
- Durata predefinita 2 h e massima 4 h sono **decisioni dell'utente**, non stime [D].
- Il rilevamento non passa fra sessioni; **non verificato** se la stima del nemico o la ricognizione si alimentino dai
  rilevamenti della sessione precedente [NV].
- Artefatto di cadenza: con osservatore e bersaglio fermi c'è una sola estrazione per sessione, quindi la probabilità di
  scoperta nel tempo dipende dalla durata e dalla cadenza delle sessioni [V].

**Rischi di fraintendimento.**
- «Campagna» qui è solo il ciclo meccanico fra sessioni, non la pianificazione strategica.
- Il validatore non è parte del motore: chi chiama il motore direttamente può far girare ordini non validi.
- «Pronto» non significa che la base abbia le risorse.

---

## Sezione 8-bis (nella guida: sezione 9) — Attorno al motore: i pianificatori di rotta e d'attacco (nuova, Q7)

**Scopo.** Descrivere i due pianificatori che stanno **fuori** dai quattro strati ma alimentano il motore o ne condividono le
regole, perché un responsabile sappia che cosa decidono, con quali criteri e con quali limiti.
**Messaggio chiave.** Il pianificatore di **rotta** aerea sceglie un percorso che aggira (o attraversa con una «corda» limitata)
i volumi di intercettazione e, se richiesto, quelli di **scoperta**, che sono distinti; il pianificatore d'**attacco** sceglie da
che quota, velocità, profilo e direzione sganciare una bomba minimizzando l'esposizione pesata alle minacce, e produce un
**profilo d'attacco** che il motore legge (gittata e tempo di caduta) e che un futuro adattatore DCS leggerebbe in altro modo
(«una fisica, un pianificatore, due esecutori»). Sono euristiche deterministiche, non ottimizzatori garantiti.

**Concetti da spiegare.**
- Volume di intercettazione (portata dell'arma) contro volume di scoperta (portata del sensore): perché aggirare l'arma non è
  aggirare il sensore (esempio del manuale: un sistema che scopre a 75 km e intercetta a 24 km).
- Tre modi di trattare una minaccia: aggirarla, attraversarla con la corda di sicurezza, aggirare la scoperta.
- Orizzonte radar nel pianificatore (raggio terrestre equivalente 4/3 per il radar; 1 per ottico e vista, stima) e la sua
  **assenza nel motore** (incoerenza dichiarata).
- Metriche di scoperta del percorso: tempo sotto sensore, primo rilevamento, preavviso, Pd massima (stessa legge del motore, con
  la permanenza); non sono la probabilità di essere rilevati almeno una volta.
- Pianificatore d'attacco a due livelli: fisica del rilascio (moto parabolico nel vuoto più fattori di resistenza **stimati**,
  bombe plananti, distanza di sgancio dichiarata) e ricerca su griglia (quote, profili, angoli, 12 direzioni), con la regola
  dell'esposizione **effettiva** (il sito lancia solo dopo averti visto e dopo il suo tempo di reazione) e la scelta per
  esposizione pesata, poi quota, poi direzione.
- Le minacce non rendono mai un profilo «non fattibile» (decisione dell'utente): scelgono fra i profili fattibili.

**Mappa verso il manuale.** Capitolo 7 §7.8 (pianificatore di rotta, D14), §7.9 (pianificatore d'attacco, D15); capitolo 4 §4.20
(il profilo letto dal motore); capitolo 9 §9.1 «Limiti del pianificatore di rotta e del pianificatore d'attacco» e «D-5».

**Diagrammi proposti.** *Volumi di scoperta e di intercettazione* (flowchart, 6-8 nodi; da D14); *Dal pianificatore d'attacco ai
due esecutori* (flowchart LR, 6-7 nodi; da D15); *Esposizione effettiva* (flowchart TD, 5-6 nodi, con un esempio numerico
ILLUSTRATIVO della formula «lancio = max(ingresso nel volume d'arma, contatto + acquisizione) + tempo minimo di tiro»).

**Letteratura.** `[FONTE: pianificazione di rotte in presenza di minacce / route planning militare]` (non coperta dalla
bibliografia); orizzonte radar: Skolnik [B 5.4] e Mahafza [B 5.5] come testi radar (contenuto specifico non verificato);
balistica delle bombe e profili di sgancio: `[FONTE: ...]` (non coperta). Le scelte (griglia, criteri di scelta, fattori di
resistenza) sono **scelte di progetto [D]/[S]**.

**Limiti e incertezze.**
- Chiamanti: `plan_attack_profile` ha solo chiamanti di test; il pianificatore di rotta è chiamato dal pianificatore d'attacco
  (transito) e da uno strumento di visualizzazione [V, ricerca testuale del 2026-11-20]: **nessuna catena di produzione** li usa.
- Fattori di resistenza delle bombe: stime dichiarate [S]; volo IP → sgancio a quota costante (la picchiata non è nella
  traiettoria di esposizione) [V]; terreno non modellato [V]; solo armi a caduta [V].
- Volume di scoperta costruito a una sola quota: niente cambi di quota per aggirarlo [V]; nessuna rete di sensori (EWR→SAM) [V];
  «attraversamento a corda limitata» del solo rilevamento non fatto [V].
- La sfera di portata non ha distanza minima; quota e velocità fuori finestra portate al bordo ammesso più vicino (come l'IA di
  DCS) [V].

**Rischi di fraintendimento.** «Pianificatore» non è il C2 (non decide missioni né assegna asset); «esposizione minima» non è
«sicurezza»; le metriche di scoperta del pianificatore e il rilevamento del motore usano la stessa legge ma non la stessa
geometria (cilindro a una quota contro sfera; orizzonte sì contro orizzonte no).

---

## Sezione 9 — Casualità e riproducibilità

**Scopo.** Spiegare come un modello stocastico possa dare risultati ripetibili e perché questo conta.
**Messaggio chiave.** Tutte le estrazioni casuali vengono da **una sola sorgente di sessione**, il cui seme è calcolato da una
chiave di dominio (sessione, missione, evento, contatore) in modo identico su qualunque macchina; a parità di ordine e di dati
il motore produce **la stessa storia, bit per bit**. Riproducibile non significa prevedibile né «giusto»: per conoscere la
variabilità servono molte repliche con semi diversi.

**Concetti da spiegare.**
- Generatore pseudo-casuale, seme, flusso (stream).
- Perché salvare solo il seme non basta: conta anche l'**ordine** delle estrazioni (contratto).
- Flussi separati per evento: ingaggio, tempra, passaggi di rilevamento, fuoco su posizione — aggiungere un'estrazione in un
  flusso non sposta gli altri.
- Precondizione: identificativi stabili delle forze.
- Determinismo contro variabilità: replicare con semi diversi (gli scenari usano repliche, es. 20 per S3).
- Perché un modello stocastico e non deterministico «alla media».

**Glossario.** Seme; flusso (stream) di numeri casuali; riproducibilità; replica; determinismo.

**Mappa verso il manuale.**
- Capitolo 1 §1.3 punto 2, §1.5 — [V].
- Capitolo 7 §7.1 — [V] (modulo invariato da `a784a9e7`).
- Capitolo 6 §6.4 — [V] riscritta a `a389cadb`.
- Capitolo 4 §4.11 (ordine delle estrazioni) — [V] a `a389cadb`.
- Capitolo 8 §8.2 (determinismo) — [V].
- Capitolo 10C §10C.8 (D125-D126) — righe ricalcolate [NV parziale].

**Diagrammi proposti.**
- *G26 — Dalla chiave al flusso* (flowchart LR, 5 nodi: chiave di dominio → impronta crittografica → seme → flusso →
  estrazioni in ordine). Deriva da **D125**.
- *G27 — Quattro flussi indipendenti* (flowchart LR, 6 nodi). Deriva da **D126**.

**Letteratura.**
- `[FONTE: generatori pseudo-casuali e riproducibilità degli esperimenti di simulazione]` (tipo: manuale di simulazione).
- `[FONTE: numeri casuali comuni e flussi separati come tecnica di riduzione della varianza]` (tipo: manuale di simulazione;
  il documento di analisi cita una pagina divulgativa sulla riduzione della varianza, da sostituire).
- `[FONTE: perché la simulazione stocastica differisce da quella «al valore medio»]`; wiki
  `concepts/stochastic-simulation.md` (fonte RAND TLC, con la citazione sulla «mean value equivalence»).

**Limiti e incertezze.**
- La riproducibilità vale **a parità di codice**: ogni cambio di regola cambia legittimamente le storie (lo controlla la
  fotografia, sezione 10) [V].
- Il numero di repliche necessario per una stima affidabile **non è discusso** nel manuale per l'uso di campagna [NV].

**Rischi di fraintendimento.**
- «Deterministico» non vuol dire «senza caso».
- Una singola esecuzione non è «il risultato»: è un campione.
- Un esito diverso dopo una modifica non è un errore di riproducibilità.

---

## Sezione 10 — Come si verifica il motore e che cosa significa

**Scopo.** Spiegare gli strumenti di verifica e che cosa provano (e non provano).
**Messaggio chiave.** Ci sono tre livelli: **test unitari** delle regole, **scenari** (S1-S36) che controllano comportamenti
attesi, e una **fotografia di non regressione** che registra in forma esatta l'esito di oltre mille esecuzioni e dice se una
modifica le cambia. Questo è **verifica** (il motore fa ciò che il progetto dice), non **validazione** contro dati reali o
storici: quest'ultima non è stata fatta.

**Concetti da spiegare.**
- Test unitari; suite completa (numero di test, «saltati»).
- Scenari: S1-S5 (composizioni prese dai documenti Lanchester senza i numeri), S6-S18 (domini e meccanismi mancanti), S19-S36
  (fasi successive); repliche; controprove a regola spenta.
- Fotografia di non regressione: che cosa registra, che cosa significa «identiche», «cambiate», «nuove»; chi decide di
  installarne una nuova (**solo l'utente**).
- Interruttori: ogni regola nuova sta dietro un interruttore il cui spegnimento riporta il comportamento precedente, per
  attribuire ogni differenza a una causa sola.
- Test di contratto dell'indipendenza dal simulatore.
- Verifica contro validazione: differenza in una frase.
- Stato attuale: fotografia **installata da 1219** esecuzioni (1103 + 116 della serie S36 dal 2026-11-19, commit `fdb78b86`,
  su richiesta dell'utente; fino al 2026-11-18 era di 1103; sostituita il 2026-11-20 da quella con la Pd al bordo a 0,2,
  `a910dc15`: 716 cambiate e 503 identiche rispetto alla precedente, contate sui due file).

**Glossario.** Test unitario; scenario; replica; fotografia di non regressione; esecuzione identica / cambiata / nuova;
interruttore; controprova; verifica; validazione; taratura (calibrazione).

**Mappa verso il manuale.**
- Capitolo 8 §8.1-§8.4, §8.7, §8.14 — [V] nel commit `e824cde9`; **numeri di suite e confronto sempre dichiarati, non
  rieseguiti** dal manuale [NV] (es. `Ran 4961`, dichiarato da `F4_Differenze_Scenari.md`).
- Capitolo 6 §6.21 (interruttori e default) — [V] a `fa5fbf1e` per la tabella; gli interruttori del risolutore a §6.21 e
  capitolo 4 (tabella iniziale) [V] a `a99bb3d4`.
- Capitolo 9 §9.1 D-5 «Limite della fotografia» — [V].

**Diagrammi proposti.**
- *G28 — I tre livelli di verifica* (flowchart TD, 5-6 nodi: test unitari → scenari → fotografia → decisione dell'utente).
  Nessun D (lo strumento non ha un diagramma nel manuale).
- *G29 — Il processo di non regressione* (flowchart LR, 6 nodi: modifica → cattura → confronto → identiche / cambiate / nuove →
  lettura delle cambiate → installazione da parte dell'utente). Dal capitolo 8 §8.7, nessun D.

**Letteratura.**
- `[FONTE: verifica, validazione e accreditamento (VV&A) dei modelli di simulazione]` (tipo: linee guida ufficiali del
  Dipartimento della Difesa USA o articoli di riferimento sulla validazione dei modelli di simulazione).
- `[FONTE: test di regressione «golden master» / approval testing]` (tipo: letteratura di ingegneria del software).
- `[FONTE: validazione dei modelli di combattimento su dati storici]`; wiki `concepts/historical-conflict-simulation.md`,
  `concepts/lanchester-models.md` (sezione sullo stato di validazione) — utile per spiegare **perché è difficile**.

**Limiti e incertezze.**
- **Nessuna validazione contro dati reali o storici** è dichiarata nel manuale [V per l'assenza; da confermare con l'utente,
  Q8].
- Le 1103 esecuzioni preesistenti **non mettono alla prova la permanenza con i dwell reali**; la serie S36 sì, ed è nella fotografia da 1219 installata [V].
- Le 1103 esecuzioni preesistenti **non registrano i rilevamenti** (li registrano solo le 116 di S36): un cambio della legge di scoperta che non tocca il tiro vi resta
  invisibile [V].
- Molti sensori reali (Shilka, Gepard, Osa, ...) sono provati solo da test di dati, non in sessione [V].
- Nessun EWR in nessuno scenario della fotografia [V].
- Esiti di missione «in corso», posizioni finali ed esiti d'operazione non sono nella fotografia (li verificano i test) [V].
- Lo scenario di scala S8 non misura il caso da 10.000 asset [V].
- Interruttore della D-5 acceso di default: il default non riproduce più il comportamento precedente «in assoluto», solo sulle
  esecuzioni fotografate [V] (capitolo 9 §9.1).

**Rischi di fraintendimento.**
- «Tutti i test passano» ≠ «il modello è realistico».
- «1219 identiche» dopo una modifica ≠ «la modifica è giusta»: significa solo che non tocca quelle esecuzioni.
- La fotografia **non** è un insieme di risultati attesi «veri»: è la storia prodotta dal codice a una data.

---

## Sezione 11 — Quanto fidarsi dei risultati: limiti, stime, punti non verificati

**Scopo.** Dare al responsabile una visione unica e onesta dell'affidabilità.
**Messaggio chiave.** La **struttura** del motore (eventi, geometria, catena dello scontro, riproducibilità) è verificata; i
**numeri** che lo alimentano sono in buona parte **stime dichiarate** o dati di registro di confidenza variabile, e **nessuna
taratura** su dati reali è stata fatta. Il motore oggi è adatto a confronti **relativi** fra scelte (con repliche), non a
previsioni assolute — affermazione della scaletta, da confermare con l'utente (Q8).

**Concetti da spiegare.**
- Tre famiglie di incertezza: (a) **forma del modello** (che cosa non è rappresentato: terreno, orizzonte radar, C2, cueing,
  logistica, manovra); (b) **parametri stimati** [S]; (c) **dati di registro** di qualità mista (portate di sensori con fonti
  contraddittorie, classificazioni stimate).
- Come leggere un'etichetta [V]/[S]/[D]/[NV].
- Dove stanno le stime: tabella riassuntiva per tema.
- Regole opzionali spente (BI, VA) e loro significato.
- Incoerenze dichiarate fra motore e pianificatore di rotta (orizzonte, volumi cilindro/sfera, metrica di scoperta).

**Mappa verso il manuale.**
- Capitolo 9 §9.1 (tutte le sottosezioni), §9.3, §9.4 — [V] nel commit `e824cde9` e aggiornamenti del 2026-11-18/19.
- Capitolo 9 §9.2 (divergenze con il wiki: una sola, sul ritiro dopo il disimpegno) — [V].
- Capitolo 9 §9.6 (incoerenze documenti/codice) — **attenzione**: le voci 30-33 risultano «APERTE» nel manuale
  (`10_Limiti_Estensioni_Divergenze.md`, §9.6), ma almeno le voci 30 e 32 sono state corrette nel codice dal commit `dad7c66f`
  («Commenti stantii nel codice (solo testo)»: la data segnaposto «2026-11-xx» e la frase «ancora letto dal motore» non
  compaiono più nei sorgenti, verificato con `grep` il 2026-11-19). Il manuale non è stato aggiornato su questo punto. La guida
  non deve riportarle (sono commenti, non comportamento).
- Capitolo 10 §10.7 e sezioni «Limiti e domande» degli atlanti 10A-10C — **non lette** per questa scaletta.

**Diagrammi proposti.**
- *G30 — Mappa delle stime* (tabella: tema, grandezza stimata, effetto, stato: stima/da ricalibrare/decisione). Nessun D.
  Contenuto minimo: Pd al bordo (0,2 dal 2026-11-20, prima 0,5); legge di Pd; soglia di rottura (erosione, shock, dispersione, pesi); scomposizione dei
  ritardi; esponente costo/efficacia; finestra della salva 0 s; dwell (24 stime, vista 3,2 s); portate e affidabilità EWR;
  classificazione BI (52 voci); fuoco su posizione (3 costanti); consumi di emergenza; costanti del bingo; turnaround e
  riparazione; raggio di un bersaglio «punto».
- *G31 — Che cosa il modello non rappresenta* (elenco o flowchart a ventaglio, 8-10 foglie). Nessun D.

**Letteratura.**
- `[FONTE: affidabilità e limiti dei modelli di combattimento — «tutti i modelli sono sbagliati, alcuni utili»; uso
  esplorativo contro predittivo]` (tipo: letteratura di analisi della difesa; wiki `concepts/wargaming.md` per l'argomento
  di Sabin).

**Limiti e incertezze.** È la sezione stessa: riprendere da §9.1 **senza trasformare nessun limite in proprietà** (es. non
scrivere «il motore è prudente» dove il manuale dice «stima ottimistica per la difesa»).

**Rischi di fraintendimento.**
- Un numero con molte cifre decimali nell'esito non è preciso: la fotografia arrotonda a 6 decimali per confronto, non per
  precisione fisica.
- «Stima dichiarata» non significa «inventata a caso»: ha una provenienza scritta, ma non è tarata.
- «Spenta» per una regola non vuol dire «rotta»: vuol dire non attiva di default.

---

## Sezione 12 — Decisioni aperte e tarature da fare (nuova) — SPOSTATA FUORI DALLA GUIDA (Q9, 2026-11-20)

> Per decisione dell'utente questa sezione **non fa parte della guida**: il contenuto qui sotto è il materiale di partenza per un
> **documento di stato separato** (non scritto da chi stende la guida). La guida vi rimanda soltanto. Nota: la Pd al bordo della
> portata è stata ricalibrata a 0,2 e l'interruttore è acceso dal 2026-11-20 (stima senza fonte, decisione dell'utente): la
> guida descrive lo stato attuale (0,2).

**Scopo.** Raccogliere in un solo posto ciò che spetta all'utente/responsabile.
**Messaggio chiave.** L'affidabilità del motore cresce soprattutto con **decisioni di taratura e di perimetro**, non con altro
codice.

**Contenuti (tutti dal manuale, capitolo 9 §9.3 e §9.1; stato al 2026-11-19).**
- (Chiusa il 2026-11-19: la fotografia da 1219 è installata, `fdb78b86`.)
- Ricalibrazione ulteriore della Pd al bordo della portata (a 0,2 dal 2026-11-20; tre ipotesi emerse: costante unica rivista, costante per sensore, sezione radar del
  bersaglio — riferite dal manuale come non scritte in documenti del repo).
- Accendere o no le regole BI e VA (ognuna cambierebbe la fotografia).
- Rivedere la regola sui colpi lanciati da dentro il volume del difensore (L1): da essa dipendono S35 e S19AD.
- Logistica (F8d) e dipendenza di riarmo/riparazione dalle risorse della base.
- Orizzonte radar nel motore e curva portata-quota (attività separate).
- Taratura della soglia di rottura (processo interno ATCAL) e dei dati di consumo d'emergenza.
- Fonti per le 24 stime di periodo di rivisita (registro dedicato).
- Chiamante di produzione del ciclo di campagna (pianificatore / C2).

**Mappa.** Capitolo 9 §9.3 (tabella dei punti di estensione), §9.1. **Diagrammi**: una tabella «decisione / effetto /
prerequisito / dove nel manuale». **Letteratura**: nessuna. **Rischio**: la sezione invecchia in fretta; va datata e
dichiarata come istantanea (v. Q9).

---

## Sezione 13 — Da dove vengono le idee: letteratura e scelte di progetto (nuova)

**Scopo.** Tabella unica «idea → origine» per separare letteratura e scelte del progetto.
**Messaggio chiave.** Il motore prende dalla letteratura **meccanismi e forme** (eventi discreti, saturazione per salva,
dipendenza R⁴, ritardi di reazione documentati), **mai coefficienti di logoramento aggregato**; molte regole sono scelte di
progetto dichiarate.

**Righe previste della tabella** (colonna «origine»: letteratura / documento di analisi del progetto / decisione
dell'utente / stima):
- DES con contatti analitici — letteratura sulla simulazione + documento di analisi.
- Ritardi di reazione RIV-VAL-COM-ATT — totali da fonti tecniche, scomposizione stimata.
- Legge di Pd — forma ispirata all'equazione radar, valore al bordo stimato.
- Permanenza (dwell) — giustificazione geometrica, scelta di progetto; Koopman come riferimento qualitativo.
- Saturazione per salva — Hughes (meccanismo).
- Danno per colpo Ph × Pk|h — lettura dei campi di registro.
- Soglia di rottura — idea dalle soglie storiche; valori stimati.
- Dottrina anti-overkill — scelta di progetto (0,9 scelto dall'utente).
- Bingo, uscita di scena, politica d'armi — decisioni dell'utente.
- Tempi di turnaround — ricerca web, una fonte verificata.
- **Lanchester** — **non usato** come modello; i documenti ingeriti sono serviti solo per composizioni di scenario e come
  bersaglio futuro di un eventuale modello aggregato di ripiego (wiki `analyses/lanchester-vs-motore-des.md`).

**Letteratura.** `[FONTE: equazioni di Lanchester e loro validazione empirica — per spiegare perché non sono il modello]`;
wiki `concepts/lanchester-models.md`; **attenzione**: `sources/source-lanchester-scenari-ai.md` è una **conversazione con un
assistente AI a bassa confidenza**, non letteratura. **Diagramma**: tabella. **Rischio**: dare l'impressione che tutto venga
dalla letteratura; la colonna «origine» deve essere esplicita riga per riga.

---

## Sezione 14 — Come leggere il manuale

**Scopo.** Ponte verso il manuale tecnico.
**Contenuti.**
- La numerazione: «capitolo N» = file con prefisso N+1 (capitolo 1 = `02_...`; atlante = capitolo 10 = `11_...`, con le parti
  10A, 10B, 10C nei file `11a`, `11b`, `11c`).
- La scala dei livelli dei diagrammi L0-L4 (`11_Atlante_Diagrammi.md:7-19`): contesto, architettura, moduli, interazione,
  algoritmo; la guida sta «sopra» L0-L1.
- Le note datate in testa ai capitoli: come capire che cosa è verificato e a quale data.
- Tabella **argomento → capitoli e §** (una riga per sezione 1-13 della guida).
- **Tabella di corrispondenza dei nomi di progetto** (D-5, BI, VA, FP, F0-F9, G1-G5, S1-S36, R-INT, L1/L2/L3, R-CLS, E(N)) con
  una riga di spiegazione ciascuno e la sezione della guida.
- Avvertenza: §1.1 del capitolo 1 manca nel file attuale (v. sezione 2).

**Diagrammi.** *G32 — Scala dei livelli* (flowchart TD, 5 nodi + «guida concettuale» sopra). Deriva da §10.1.
**Mappa.** `Manuale_Motore_DES.md:265-359` (convenzioni e indice), capitolo 10 §10.1-§10.2 — [V].

---

## Sezione 15 — Glossario

Raccolta alfabetica dei termini definiti nelle sezioni 1-14 (circa 70-80 voci), ciascuno con definizione in una riga, il rimando
alla sezione della guida e al capitolo del manuale. Termini già elencati sopra; in più: blocco (gruppo di unità del progetto),
lato/schieramento, asset (singola unità: aereo, mezzo, nave, sito), registro (archivio dei dati di armi, mezzi, sensori),
ricognizione, RWR (ricevitore di allarme radar), SAM (missile superficie-aria), AAA (artiglieria antiaerea), CAS/SEAD/CAP (tipi
di missione), C2 (comando e controllo).

## Sezione 16 — Bibliografia

Arriverà da un file separato preparato da un altro agente. Requisiti per l'integrazione: (1) ogni `[FONTE: ...]` delle sezioni
1-13 trova una voce o resta esplicitamente «senza fonte»; (2) le fonti del wiki derivate da conversazioni con assistenti AI
(Hughes, Lanchester) **non** sono citate come letteratura; (3) distinguere fonti primarie da pagine divulgative o di
fornitori; (4) nessuna voce non verificata.

---

## (i) Domande aperte per l'utente

> **Risposte (2026-11-20)**, in sintesi (testo completo in §0.4): Q1 sì (`Guida_Concettuale_DES.md`, data e commit in testa);
> Q2 formule nel testo, parte centrale, con esempi ILLUSTRATIVI; Q3 sigle solo nella tabella della sezione 14; Q4 §1.1
> ripristinata, «micro-passo» tolto; Q5 fotografia da 1219 installata; Q6 fonti primarie, secondarie come indicazioni, wiki su
> Hughes e Lanchester non citate; Q7 sezione propria (sezione 9 della guida); Q8 sì, confronti relativi con repliche e nessuna
> validazione; Q9 sezione 12 in un documento separato; **Q10 confermata il 2026-11-20** (formulazione in §0.4);
> Q11 lunghezza completa con riassunto iniziale. Le domande originali restano qui sotto per memoria.

- **Q1 — Titolo, collocazione e data.** Il file finale si chiamerà `Guida_Concettuale_DES.md` in questa cartella? Va
  dichiarato in testa il commit del manuale su cui è scritta (proposta: sì) e chi la aggiorna quando il manuale cambia?
- **Q2 — Matematica.** Includere le poche formule (legge di Pd, saturazione, regola di permanenza) in riquadri «per chi
  vuole approfondire», oppure nessuna formula?
- **Q3 — Nomi di progetto.** Usare nel testo solo descrizioni piane («regola della permanenza nel volume») e confinare le
  sigle (D-5, BI, VA, FP, F4, G2, ...) alla tabella di corrispondenza della sezione 14, oppure citarle anche nel testo tra
  parentesi?
- **Q4 — §1.1 mancante.** La §1.1 del capitolo 1 è sparita dal file con `234071d3` (2026-10-18) ma è ancora citata. Prima
  della fase B: va ripristinata nel manuale (lavoro separato, con verifica), oppure la guida la ricostruisce dalla versione in
  git e dal wiki? E la frase sul «micro-passo fine dentro una finestra d'ingaggio» va verificata nel codice prima di essere
  ripresa o tolta?
- **Q5 — Fotografia. RISOLTA (2026-11-19).** La fotografia da 1219 è stata installata (`fdb78b86`): la guida descrive la
  1219. (Domanda originale: stato «1103 installata, 1219 in attesa» oppure attesa della decisione.)
- **Q6 — Bibliografia.** Lingua delle fonti, stile di citazione; sono accettabili pagine Wikipedia e di fornitori come fonti
  secondarie, o solo fonti primarie?
- **Q7 — Perimetro dei pianificatori satellite.** I pianificatori di rotta e d'attacco (fuori dal motore, ma lo alimentano e
  condividono i volumi) vanno descritti in una sezione propria o solo citati dove servono (proposta: citati in sezione 5 e 11)?
- **Q8 — Messaggio sull'uso dei risultati.** Confermi che la guida può dire che il motore oggi serve per **confronti relativi
  con repliche** e che **nessuna validazione contro dati reali o storici** è stata fatta? È un giudizio che la scaletta non
  può prendere da sola.
- **Q9 — Sezione 12 (decisioni aperte).** Tenerla nella guida (con data) o spostarla in un documento di stato separato,
  dato che invecchia in pochi giorni?
- **Q10 — Sessioni con giocatore.** Come formulare il rapporto fra motore e sessioni giocate in DCS, data la frase d'apertura
  del manuale «e, per costruzione, anche quelli con un giocatore»?
- **Q11 — Lunghezza.** La stima sotto (~55-65 pagine) è accettabile, o preferisci una guida più breve (~30 pagine) con il
  dettaglio dei limiti rimandato al capitolo 9?

## (ii) Stima della lunghezza

Pagina = circa 450-500 parole o un diagramma con didascalia e mezza pagina di testo.

| Sezione | Pagine stimate |
|---|---|
| 0. Premessa e come leggere la guida | 1-2 |
| 1. A che cosa serve e non serve | 3 |
| 2. Eventi discreti contro passi di tempo | 4 |
| 3. Quattro strati e percorso di una sessione | 5 |
| 4. Missioni, operazioni, regole d'ingaggio | 4-5 |
| 5. Contatti e rilevamento | 6-7 |
| 6. Lo scontro | 7-8 |
| 7. Tempo, carburante, munizioni, stato | 4 |
| 8. Dalla sessione alla campagna | 4 |
| 9. Casualità e riproducibilità | 3 |
| 10. Verifica | 4 |
| 11. Quanto fidarsi | 5-6 |
| 12. Decisioni aperte | 2 |
| 13. Letteratura e scelte di progetto | 2 |
| 14. Come leggere il manuale | 2-3 |
| 15. Glossario | 4 |
| 16. Bibliografia | 2-3 (dipende dall'altro agente) |
| **Totale** | **circa 58-67 pagine** (32 diagrammi o tabelle) |

*Aggiornamento 2026-11-20*: con le decisioni di §0.4 si aggiungono il riassunto iniziale (1-2 pagine) e la sezione sui
pianificatori (3-4 pagine) e si toglie la sezione 12 (2 pagine): il totale resta nell'ordine di 60-70 pagine, deciso dalla
chiarezza (Q11).

## (iii) Parti del manuale NON lette a fondo, e perché

Budget di lettura: il manuale ha 16.105 righe; per una scaletta servivano struttura, stato di verifica e limiti, non il
dettaglio delle regole.

- **Letti per intero o quasi**: `Manuale_Motore_DES.md`; `02_Scopo_e_Motivazioni.md`; `10_Limiti_Estensioni_Divergenze.md`
  §9.1-§9.5 (righe 1-1030) e i titoli delle voci di §9.6.
- **Letti in parte**: `11_Atlante_Diagrammi.md` §10.1-§10.3 (righe 1-290; non letti §10.4-§10.7, cioè import reali, moduli,
  sequenze e «Limiti del pilota»); `04` §3.1-§3.2 e la nota iniziale; `05` nota iniziale, tabella delle quattro regole, §4.1-§4.6
  e inizio di §4.7 (non lette §4.7-§4.37 nel corpo: il contenuto delle regole è stato preso dai riassunti di §4.1 e dai limiti
  del capitolo 9); `06` note iniziali e §5.1; `07` note iniziali, §6.1-§6.7, tabella di §6.21; `08` §7.1, §7.2 (valori di
  default), §7.3; `09` note iniziali, §8.2-§8.4 (prime righe della tabella), inizio di §8.7.
- **Non letti**: `03_Strato0_Contratto_Porte.md` oltre la nota iniziale (porte, tipi della missione, tassonomia: necessari in
  fase B per la sezione 4); `11a_Atlante_Risolutore.md`, `11b_Atlante_Missione_Carburante.md`, `11c_Atlante_Porte_Campagna.md`
  (diagrammi tecnici L2-L3: servono in fase B solo per controllare che i diagrammi concettuali non contraddicano quelli
  tecnici); le sezioni «Limiti e domande» degli atlanti.
- **Wiki**: lette le intestazioni e le definizioni di `concepts/event-driven-simulation.md`, `salvo-combat-model.md`,
  `lanchester-models.md`, `stochastic-simulation.md`, `variable-resolution-modeling.md`, `cross-resolution-modeling.md`,
  `campaign-model.md`, `wargaming.md`; le intestazioni delle quattro pagine `sources/`; l'inizio di
  `analyses/lanchester-vs-motore-des.md` e `analyses/hughes-salvo-vs-engagement-resolver.md`; la sezione «Decisione» di
  `decisions/virtual-session-engine-des.md`. Letto anche il §10 (bibliografia) di
  `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`.

## (iv) Rischi per la fase B

1. **Il manuale cambia di continuo**: 10 commit sui suoi file in quindici giorni; la guida rischia di invecchiare prima di essere
   finita. Mitigazione: data e commit in testa, sezione 12 separabile (Q9).
2. **Stati di verifica disomogenei**: alcune sezioni del capitolo 4 hanno riferimenti di riga sfasati e il loro contenuto è
   verificato a una data più vecchia; i numeri di suite e fotografia sono sempre «dichiarati, non rieseguiti». La guida non usa
   righe di codice, ma deve riportare le etichette senza promuovere [NV] a [V].
3. ~~**§1.1 mancante** nel capitolo 1 (Q4): la sezione 2 della guida poggia su un testo che oggi non c'è nel manuale.~~
   Superato il 2026-11-19: §1.1 ripristinata e riverificata (`03555c81`).
4. **Incoerenze manuale/codice già note** (voci 30 e 32 di §9.6 risolte nel codice ma «APERTE» nel manuale): la guida deve
   evitare di riprenderle; segnalarle a chi mantiene il manuale.
5. **Fonti del wiki non primarie**: le pagine su Hughes e Lanchester derivano da conversazioni con assistenti AI; c'è il
   rischio di citarle come letteratura.
6. **Trasformare limiti in pregi** o stime in dati nel passaggio a un linguaggio semplice (es. «prudente», «realistico»):
   serve una rilettura mirata dopo la stesura, voce per voce contro §9.1.
7. **Numeri illustrativi** negli esempi (saturazione, Pd) potrebbero essere letti come dati: vanno marcati come illustrativi.
8. **Diagrammi non resi**: nessun renderer Mermaid qui; i tipi `timeline`, `xychart-beta`, `quadrantChart` vanno evitati o
   provati in Obsidian.
9. **Gergo del manuale** (stato ombra, dominio, episodio, payload congelato): rischio di lasciarlo non spiegato; il glossario
   va scritto prima del testo.
10. **Dipendenza dalla bibliografia esterna**: la fase B può procedere con i segnaposto `[FONTE: ...]`, ma la versione finale
    richiede l'allineamento con il file della bibliografia.
